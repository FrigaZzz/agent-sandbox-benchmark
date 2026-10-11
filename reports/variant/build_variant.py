"""Build the preference-driven decision dashboard in reports/variant/.

Reads the same evidence the rest of the report tree uses:
  - reports/data/derived/evaluation-summary.json  (eligible measured cohorts)
  - reports/data/derived/specifications.json      (documented features + published pricing)
  - reports/data/attempts/*_evaluation.json        (per-attempt cost estimates, prerequisites)
  - reports/docs/eu-data-residency.md              (curated EU notes below cite this file)

Writes:
  - reports/variant/data.json        (inspectable intermediate)
  - reports/variant/index.html       (self-contained dashboard, data inlined)

Nothing here invents measurements. Pricing is published list rate, never an
invoice. Documented-only providers stay visible and flagged; local control is
never ranked as a cloud winner.
"""
from __future__ import annotations

import json
import os
import hashlib
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlencode
from urllib.parse import urlsplit

REPORTS = Path(__file__).resolve().parents[1]
OUT = REPORTS / "variant"
sys.dont_write_bytecode = True
sys.path.insert(0, str(REPORTS.parent))
from src.bench.evidence import load_evidence, summarize
from src.bench.portal import portal_html

DISPLAY_NAMES = {
    "gcp_vertex": "GCP Agent Sandbox",
    "modal": "Modal",
    "blaxel": "Blaxel",
    "e2b": "E2B",
    "daytona": "Daytona",
    "aws": "AWS AgentCore",
    "databricks": "Databricks SQL MCP",
    "databricks_sandbox": "Databricks Dedicated Sandbox",
    "gemini_tool": "Gemini Tool",
    "openai_tool": "OpenAI Tool",
    "alibaba": "Alibaba OpenSandbox / AgentRun",
    "k8s_agent_sandbox": "Kubernetes adapter",
    "local_baseline": "Local control",
}

ROLES = {
    "gcp_vertex": "Managed cloud interpreter",
    "modal": "Managed workspace API",
    "blaxel": "Managed workspace API",
    "e2b": "Managed workspace API",
    "daytona": "Managed workspace API",
    "aws": "Managed cloud interpreter",
    "databricks": "Databricks execution surface",
    "databricks_sandbox": "Databricks execution surface",
    "gemini_tool": "Model-owned code tool",
    "openai_tool": "Model-owned code tool",
    "alibaba": "Hybrid: self-hosted + managed",
    "k8s_agent_sandbox": "Self-operated infrastructure",
    "local_baseline": "Local control (not a secure runtime)",
}

# Curated one-line residency notes. Source: reports/docs/eu-data-residency.md
# (reviewed 2026-10-13). status: documented | partial | not_established | operator
EU_NOTES = {
    "modal": ("partial", "EEA compute pinning documented (region=eu is EEA, not strict EU). "
                         "Stdout/stderr logs, snapshots and managed durable storage are US-resident; "
                         "lifecycle control plane is US-east."),
    "e2b": ("partial", "Default cluster us-west1. Shared EU route: Belgium europe-west1, Pro and above, "
                       "via support. Templates/snapshots/logs residency beyond sandbox availability "
                       "not established by the reviewed sources. Enterprise BYOC keeps templates, "
                       "snapshots and runtime logs in the customer VPC."),
    "blaxel": ("partial", "Frankfurt eu-fra-1 (London eu-lon-1 is UK, not EU). Volumes are same-region. "
                          "Location scope of images, standby snapshots, logs, telemetry and control "
                          "plane not established."),
    "gcp_vertex": ("documented", "Five named EU regions (Belgium, Frankfurt, Netherlands, Milan, Madrid) "
                                 "plus an eu Code Execution endpoint. Model processing is configured "
                                 "separately. CMEK single-region keys must match the parent instance; "
                                 "multi-regional eu path does not support CMEK."),
    "aws": ("partial", "EU Built-in Tools regions include Frankfurt, Ireland, Paris, Milan, Spain, "
                       "Stockholm (London is not EU). Session data retention policy is 30 days; "
                       "stop success is not deletion attestation. General endpoint reference lists "
                       "fewer regions than the feature matrix — confirm the exact endpoint."),
    "databricks": ("partial", "Supported EU cloud/workspace regions. AI Europe Geo includes the UK and "
                              "Switzerland. Serverless SQL region does not establish function-specific "
                              "residency for the evaluated SQL surface."),
    "databricks_sandbox": ("partial", "Dedicated Sandbox EU availability: AWS Frankfurt/Ireland/Paris; "
                                      "Azure France Central, Germany West Central, North Europe, Sweden "
                                      "Central. Azure West Europe supports serverless SQL but is not "
                                      "marked for dedicated Sandbox."),
    "daytona": ("partial", "Shared eu target documented but countries/zones unnamed. GPU sandboxes and "
                           "snapshots use logical 'earth' placement that ignores geographic preference. "
                           "BYOC compute still uses Daytona's managed control plane."),
    "gemini_tool": ("not_established", "Availability in an EU country is not processing residency. "
                                        "No EU-only boundary established for the Developer API route. "
                                        "Google Cloud route has model/endpoint-specific commitments."),
    "openai_tool": ("partial", "Europe (EEA + Switzerland, not strict EU) storage/processing eligible "
                               "via eu.api.openai.com, subject to endpoint/model eligibility, abuse-"
                               "monitoring approval and retention amendment. System/account/billing "
                               "data excluded from customer-content commitments."),
    "alibaba": ("operator", "Self-hosted OpenSandbox: geography is operator-controlled. Managed "
                            "AgentRun residency not verified by this benchmark."),
    "k8s_agent_sandbox": ("operator", "Operator-selected compute/storage offers geographic control; "
                                      "does not automatically localise observability, backups, support, "
                                      "package registries or model calls."),
    "local_baseline": ("operator", "Runs where you run it; no remote residency question."),
}

FEATURE_LABELS = {
    "custom_image": "Custom image",
    "runtime_packages": "Runtime package install",
    "cpu_sizing": "CPU sizing",
    "memory_sizing": "Memory sizing",
    "gpu": "GPU",
    "network_policy": "Network policy",
    "persistent_storage": "Persistent storage",
    "session_reuse": "Session reuse",
    "shell": "Shell",
    "file_transfer": "File transfer",
    "ports_preview": "Ports / preview URLs",
    "self_hosting": "Self-hosting / BYOC",
    "cmek": "CMEK / customer keys",
}

# Workload profile -> measured suites that back it. Only suites present in the
# eligible summary cohorts appear in the evidence grid.
WORKLOADS = [
    {"id": "code_exec", "label": "Quick code execution",
     "blurb": "Agent tool calls: start a sandbox, run a snippet, read stdout.",
     "suites": ["cold_start"], "features": []},
    {"id": "data_pipeline", "label": "Data cleaning / analytics",
     "blurb": "CSV-style ETL, aggregations, SQL over files.",
     "suites": ["data_pipeline", "sqlite_analytics"], "features": ["file_transfer"]},
    {"id": "repo_task", "label": "Repository edits + tests",
     "blurb": "Clone/upload a repo, patch source, run a test suite.",
     "suites": ["repository_task"], "features": ["shell"]},
    {"id": "file_transfer", "label": "Binary file round trip",
     "blurb": "Upload and download artifacts with byte integrity.",
     "suites": ["artifact_roundtrip"], "features": ["file_transfer"]},
    {"id": "package_install", "label": "Dependency install",
     "blurb": "Install packages at runtime (offline wheel in this pilot).",
     "suites": ["dependency_install"], "features": ["runtime_packages", "file_transfer"]},
    {"id": "stateful_agent", "label": "Stateful multi-step agent",
     "blurb": "Disk state across calls, error recovery, deadline behaviour.",
     "suites": ["session_state", "error_recovery", "timeout_handling"], "features": ["session_reuse"]},
    {"id": "output_fidelity", "label": "Byte-exact stdout",
     "blurb": "Consumers that hash or diff returned stdout.",
     "suites": ["output_fidelity"], "features": []},
    {"id": "cpu_compute", "label": "CPU-heavy compute",
     "blurb": "Prime-style batch math inside the sandbox.",
     "suites": ["cpu_stress"], "features": []},
    {"id": "throughput", "label": "Parallel worker bursts",
     "blurb": "Several sandboxes completing tasks at once.",
     "suites": ["cpu_stress"], "features": [], "concurrency": 3},
    {"id": "serve_app", "label": "Serve an application",
     "blurb": "Background process, authenticated preview and lifecycle. No serving fixture was measured.",
     "suites": ["application_serving"], "features": ["shell", "ports_preview"]},
    {"id": "special_compute", "label": "Custom image / GPU workload",
     "blurb": "Specialised environments and accelerator workloads. No GPU/custom-image campaign was measured.",
     "suites": ["specialised_compute"], "features": ["custom_image", "gpu", "cpu_sizing", "memory_sizing"]},
]

SURFACES = {
    "compute": "Compute / in-memory processing",
    "storage": "Files, images, snapshots and backups",
    "logs": "Logs and traces",
    "control": "Control plane / account metadata",
    "support": "Support access / subprocessors",
    "model": "Model calls / external APIs / downloads",
}


def residency(pid):
    """Bounded source-guide projections, never a residency certification."""
    surfaces = {key: {"state": "unknown", "note": "Full EU-only scope not established by the reviewed sources."}
                for key in SURFACES}
    if pid in {"modal", "e2b", "blaxel", "gcp_vertex", "aws", "databricks", "databricks_sandbox", "daytona", "openai_tool"}:
        surfaces["compute"] = {"state": "conditional", "note": EU_NOTES[pid][1]}
    if pid == "modal":
        for key, note in {
            "storage": "Managed images, volumes and snapshots are US-resident; external storage is a different route.",
            "logs": "Sandbox stdout/stderr logs are US-resident in the reviewed managed route.",
            "control": "Lifecycle control plane is US-east.",
        }.items():
            surfaces[key] = {"state": "conflict", "note": note}
    if pid in {"gcp_vertex", "blaxel", "databricks_sandbox", "e2b", "aws", "openai_tool"}:
        surfaces["storage"] = {"state": "conditional", "note": "Some regional or customer-owned storage is documented. Confirm the exact route and every retained copy; full scope is unverified."}
    if pid in {"alibaba", "k8s_agent_sandbox", "local_baseline"}:
        for key in ("compute", "storage", "logs", "control"):
            surfaces[key] = {"state": "conditional", "note": "Operator-selected infrastructure requires deployment attestation; no attested EU deployment was established here."}
    return {"note": EU_NOTES[pid][1], "surfaces": surfaces, "source": "../docs/eu-data-residency.md"}

HARD_REQUIREMENTS = [
    {"id": "custom_image", "label": "Custom image"},
    {"id": "runtime_packages", "label": "Runtime package install"},
    {"id": "gpu", "label": "GPU"},
    {"id": "network_policy", "label": "Network policy control"},
    {"id": "persistent_storage", "label": "Persistent storage"},
    {"id": "session_reuse", "label": "Session reuse"},
    {"id": "shell", "label": "Shell access"},
    {"id": "file_transfer", "label": "File transfer"},
    {"id": "ports_preview", "label": "Ports / preview URLs"},
    {"id": "self_hosting", "label": "Self-hosting / BYOC"},
    {"id": "cmek", "label": "CMEK / customer-managed keys"},
    {"id": "cpu_sizing", "label": "CPU sizing"},
    {"id": "memory_sizing", "label": "Memory sizing"},
]


def rate_by(substrings, rates):
    for r in rates:
        blob = (r.get("resource", "") + " " + r.get("unit", "")).lower()
        if all(s.lower() in blob for s in substrings):
            try:
                return float(r["amount"])
            except (TypeError, ValueError):
                return None
    return None


def cost_model(provider: str, spec: dict) -> dict:
    """Convert time units; preserve GB versus GiB in memory_unit for scenarios."""
    pricing = (spec or {}).get("pricing") or {}
    rates = pricing.get("rates") or []
    model = {"provider": provider, "currency": pricing.get("currency", "USD"),
             "model_text": pricing.get("model", ""), "limitations": pricing.get("limitations", ""),
             "per_vcpu_hour": None, "per_gib_hour": None, "notes": [], "basis": None,
             "special": None}

    if provider == "modal":
        # Sandbox CPU is billed per physical-core-second; 1 physical core ≈ 2 vCPU.
        cpu = rate_by(["sandbox cpu"], rates)
        mem = rate_by(["sandbox memory"], rates)
        if cpu is not None:
            model["per_vcpu_hour"] = cpu * 3600 / 2
            model["notes"].append(("CPU list rate is per physical-core-second; shown here as "
                                  "per-vCPU-hour assuming 1 physical core ≈ 2 vCPU."))
        if mem is not None:
            model["per_gib_hour"] = mem * 3600
        model["basis"] = "Sandbox-specific per-second CPU and memory, charged at max(request, actual)."
    elif provider == "e2b":
        cpu = rate_by(["sandbox cpu"], rates)
        mem = rate_by(["sandbox ram"], rates)
        if cpu is not None:
            model["per_vcpu_hour"] = cpu * 3600
        if mem is not None:
            model["per_gib_hour"] = mem * 3600
        model["basis"] = "Provisioned vCPU/RAM per running sandbox-second; paused/killed compute not billed."
        model["notes"].append(("Plan fees (Hobby $0, Pro $150/mo, Pro+ $650/mo, Pro++ $1,150/mo) are "
                              "additional to usage."))
    elif provider == "blaxel":
        mem = rate_by(["ram-second"], rates)
        if mem is not None:
            model["per_gib_hour"] = mem * 3600
            model["notes"].append("CPU is included in the active-RAM unit; no separate CPU line.")
        model["basis"] = "Active sandbox compute billed by allocated GB RAM-second; standby has no compute charge."
        model["notes"].append(("Benchmark adapter requested memory 4,096 in an MB API field; whether that "
                              "bills as 4 published GB is not independently verified."))
    elif provider == "gcp_vertex":
        cpu = rate_by(["agent compute"], rates)
        mem = rate_by(["agent memory"], rates)
        if cpu is not None:
            model["per_vcpu_hour"] = cpu
        if mem is not None:
            model["per_gib_hour"] = mem
        model["basis"] = "Allocated Agent Compute vCPU-hours + Agent Memory GiB-hours, rounded to the second."
        model["notes"].append("Sandboxes are billed while they exist, not only while executing.")
    elif provider == "aws":
        cpu = rate_by(["code interpreter cpu"], rates)
        mem = rate_by(["code interpreter memory"], rates)
        if cpu is not None:
            model["per_vcpu_hour"] = cpu
        if mem is not None:
            model["per_gib_hour"] = mem
        model["basis"] = ("Actual CPU consumption and peak memory consumed, per second, with 1-second "
                         "and 128 MB minimums.")
    elif provider == "daytona":
        cpu = rate_by(["cpu"], rates)
        mem = rate_by(["ram"], rates)
        if cpu is not None:
            model["per_vcpu_hour"] = cpu
        if mem is not None:
            model["per_gib_hour"] = mem
        model["basis"] = ("Reserved vCPU/RAM/disk by lifecycle state, calculated per second; public base "
                         "rates displayed hourly.")
        model["notes"].append(("Stopped/paused disk and retained snapshots can remain billable. "
                              "GPU is a separate preemptible schedule."))
    elif provider == "databricks_sandbox":
        model["basis"] = "Dedicated Sandbox usage is currently no-charge Beta; future rates unresolved."
        model["notes"].append(("Beta $0 is a promotional state, not a long-term price. Model inference "
                              "and data transfer bill separately."))
        model["special"] = {"kind": "beta_zero"}
    elif provider == "databricks":
        model["basis"] = ("SQL warehouse/serverless compute billed in DBUs; amount depends on warehouse "
                         "SKU and was not fixed for the evaluated surface.")
        model["special"] = {"kind": "unresolved", "reason": "DBU rate not pinned to the evaluated warehouse"}
    elif provider == "openai_tool":
        model["basis"] = ("Hosted Shell/Code Interpreter container session fees (per 20-minute session) "
                         "plus separately billed model tokens.")
        model["special"] = {"kind": "session_fee", "sessions": [
            {"container": "1 GB", "usd_per_20min": 0.03},
            {"container": "4 GB", "usd_per_20min": 0.12},
            {"container": "16 GB", "usd_per_20min": 0.48},
            {"container": "64 GB", "usd_per_20min": 1.92},
        ]}
    elif provider == "gemini_tool":
        model["basis"] = ("No separate runtime/session charge; selected-model token billing covers code, "
                         "results and iterative context.")
        model["special"] = {"kind": "token_only", "example": {
            "model": "gemini-2.5-flash", "usd_per_1m_input": 0.3, "usd_per_1m_output": 2.5}}
    elif provider == "alibaba":
        model["basis"] = ("OpenSandbox is Apache-2.0 with no usage license fee; hosting is operator-paid. "
                         "Managed AgentRun sandbox tariff not verified.")
        model["special"] = {"kind": "unresolved", "reason": "managed tariff unknown; self-host cost is your infrastructure"}
    elif provider == "k8s_agent_sandbox":
        model["basis"] = ("No universal per-execution tariff; you pay for deployed infrastructure, warm "
                         "pools, routing, storage and networking. GKE Agent Sandbox adds no feature fee.")
        model["special"] = {"kind": "unresolved", "reason": "cost is your cluster economics"}
    for k in ("per_vcpu_hour", "per_gib_hour"):
        if model[k] is not None:
            model[k] = round(model[k], 6)
    model["memory_unit"] = "GB" if provider in {"aws", "blaxel"} else "GiB"
    model["billing"] = "consumed" if provider == "aws" else "allocated"
    model["rates"] = rates
    model["sources"] = [s for s in spec.get("sources", []) if s["id"] in
                        {sid for r in rates for sid in r.get("source_ids", [])}]
    if provider == "openai_tool":
        model["special"]["sessions"] = [
            {"container": r["resource"].split(" Hosted")[0], "usd_per_20min": r["amount"]}
            for r in rates if "20-minute session" in r["unit"]
        ]
    if provider == "gemini_tool":
        model["special"]["example"]["usd_per_1m_input"] = rate_by(["text/image/video input"], rates)
        model["special"]["example"]["usd_per_1m_output"] = rate_by(["output including thinking"], rates)
    return model


def main() -> None:
    source_hashes = {}

    def load_json(path):
        content = path.read_bytes()
        source_hashes[path.name] = hashlib.sha256(content).hexdigest()
        return json.loads(content)

    summary = load_json(REPORTS / "data/derived/evaluation-summary.json")
    specs = load_json(REPORTS / "data/derived/specifications.json")["specifications"]
    for pid, spec in specs.items():
        for source in spec.get("sources", []):
            parsed = urlsplit(source["url"])
            if parsed.scheme == "repo":
                target = REPORTS.parent / parsed.path
            elif not parsed.scheme:
                target = REPORTS.parent / "providers" / pid / parsed.path
            else:
                continue
            source["url"] = os.path.relpath(target.resolve(), OUT) + ("#" + parsed.fragment if parsed.fragment else "")
    source_hashes["docs/eu-data-residency.md"] = hashlib.sha256((REPORTS / "docs/eu-data-residency.md").read_bytes()).hexdigest()
    providers_order = list(summary["providers"].keys())
    # The published comparison summary intentionally omits unattested routes.
    # Preserve their validated observations for inspection without promoting
    # endpoint measurements into cloud comparisons. Reuse the repository's
    # evaluator normalisation and exact cohort aggregation.
    attempts, evidence_issues = load_evidence(REPORTS)
    unranked_cohorts = [c for c in summarize(attempts)
                       if c["runtime_kind"].startswith("unattested")
                       and c["workload_sha256"] != "legacy"
                       and c["evaluation_contract_sha256"] != "unrecorded"]

    # ---- eligible measured cohorts, grouped provider -> suite -> cohort list
    by_provider_suite = defaultdict(lambda: defaultdict(list))
    for s in summary["summaries"]:
        by_provider_suite[s["provider"]][s["suite"]].append(s)

    # ---- per-attempt cost estimates + raw outcome counts from evaluation files
    cost_stats = {}
    prereq_failures = {}
    attempt_counts = {}
    raw_outcomes = {}
    for path in sorted((REPORTS / "data/attempts").glob("*_evaluation.json")):
        filename_provider = path.name.replace("_evaluation.json", "")
        try:
            rows = load_json(path)
        except (json.JSONDecodeError, OSError):
            continue
        if not isinstance(rows, list):
            continue
        provider = rows[0].get("provider", filename_provider) if rows else filename_provider
        attempt_counts[provider] = attempt_counts.get(provider, 0) + len(rows)
        outcomes = {"pass": 0, "fail": 0, "other": 0}
        for r in rows:
            ev = r.get("evaluation")
            if ev == "pass":
                outcomes["pass"] += 1
            elif ev == "fail":
                outcomes["fail"] += 1
            else:
                outcomes["other"] += 1
        raw_outcomes[provider] = {k: raw_outcomes.get(provider, {}).get(k, 0) + v for k, v in outcomes.items()}
        totals, units = [], set()
        any_success = False
        first_failure = None
        for r in rows:
            c = r.get("cost") or {}
            t = c.get("total_cost_usd")
            if isinstance(t, (int, float)):
                totals.append(t)
            if c.get("billing_unit"):
                units.add(c["billing_unit"])
            if r.get("status") == "success":
                any_success = True
            elif r.get("status") == "failed" and first_failure is None:
                # Prefer the concrete stderr; fall back to warnings.
                for field in ("stderr", "error", "warnings"):
                    blob = r.get(field)
                    if not blob:
                        continue
                    blob = str(blob)
                    blob = blob.strip()
                    if blob and blob != "None":
                        first_failure = blob[:220]
                        break
        # A prerequisite failure means the provider never produced a successful
        # remote baseline in the retained corpus — not that one attempt failed.
        if first_failure is not None and not any_success:
            prereq_failures[provider] = first_failure
        if totals:
            cost_stats[provider] = {
                "n": len(totals),
                "mean_usd": statistics.mean(totals),
                "median_usd": statistics.median(totals),
                "max_usd": max(totals),
                "billing_units": sorted(units),
                "note": "estimate_unverified_rates from retained attempts; not an invoice",
            }

    # ---- campaigns / burst throughput
    campaigns = []
    for c in summary.get("campaigns", []):
        campaigns.append({
            "report": c["report_path"],
            "workers": c["concurrency"],
            "attempts": c["attempts"],
            "passes": c["passes"],
            "wall_seconds": c["wall_seconds_including_warmups"],
            "verified_per_sec": c["verified_completions_per_second_including_warmup_time"],
            "campaign_id": c["campaign_id"],
            "evidence_url": "../" + c["evidence_path"],
        })

    providers = {}
    for pid in providers_order:
        spec = specs.get(pid, {})
        features = {f["id"]: {"support": f["support"], "evidence": f["evidence"],
                              "notes": f.get("notes", "")}
                    for f in spec.get("features", [])}
        suites = {}
        total_pass = total_n = 0
        for suite, cohorts in by_provider_suite.get(pid, {}).items():
            # Preserve every identity boundary, including concurrency. Never
            # average medians or merge success intervals across distinct cohorts.
            suites[suite] = []
            for c in cohorts:
                total_pass += c["outcomes"].get("pass", 0)
                total_n += c["n"]
                row = {key: c.get(key) for key in (
                    "provider", "suite", "n", "attempts", "outcomes", "pass_rate", "success_ci95",
                    "latency_ms", "attempt_latency_ms", "workload_ms", "phases_ms", "configuration", "config_id",
                    "runtime_kind", "concurrency", "workload_sha256", "evaluation_contract_sha256",
                    "adapter_sha256", "stack_sha256", "client_os", "client_arch", "eligible",
                    "last_measured_at", "reports", "run_refs",
                )}
                # Cross-provider comparability excludes provider-specific adapter/
                # config hashes, but those identities remain inspectable on every row.
                row["comparison_key"] = "|".join(str(c.get(key, "")) for key in (
                    "suite", "workload_sha256", "evaluation_contract_sha256", "runtime_kind",
                    "concurrency", "client_os", "client_arch",
                ))
                params = {key: str(c.get(key, "")) for key in (
                    "provider", "suite", "config_id", "workload_sha256", "evaluation_contract_sha256",
                    "adapter_sha256", "stack_sha256", "concurrency", "client_os", "client_arch", "runtime_kind",
                )}
                row["evidence_url"] = "../index.html#raw?" + urlencode(params)
                suites[suite].append(row)

        measured = bool(suites)
        endpoint_cohorts = [c for c in unranked_cohorts if c["provider"] == pid]
        runtime_kinds = {c["runtime_kind"] for rows in suites.values() for c in rows}
        runtime_kinds.update(c["runtime_kind"] for c in endpoint_cohorts)
        unattested = (not runtime_kinds.intersection({"remote_runtime", "model_mediated"})
                      and (bool(endpoint_cohorts) or spec.get("deployment") == "self_hosted"
                           or pid == "local_baseline"))
        evidence_state = "measured"
        if pid == "local_baseline":
            evidence_state = "control"
        elif not measured:
            if endpoint_cohorts:
                evidence_state = "unattested_endpoint"
            elif pid in prereq_failures:
                evidence_state = "prerequisite_failed"
            elif attempt_counts.get(pid):
                evidence_state = "attempted_below_threshold"
            else:
                evidence_state = "documented_only"

        providers[pid] = {
            "id": pid,
            "name": DISPLAY_NAMES.get(pid, pid),
            "role": ROLES.get(pid, ""),
            "deployment": spec.get("deployment"),
            "customization_level": (spec.get("customization") or {}).get("level"),
            "customization_summary": (spec.get("customization") or {}).get("summary", ""),
            "reviewed_at": spec.get("reviewed_at"),
            "features": features,
            "cost_model": cost_model(pid, spec),
            "pricing_limitations": (spec.get("pricing") or {}).get("limitations", ""),
            "eu": residency(pid),
            "measured": {
                "attempted": total_n, "passed": total_pass,
                "failed": total_n - total_pass,
                "suites": suites,
            },
            "evidence_state": evidence_state,
            "raw_attempts_retained": attempt_counts.get(pid, 0),
            "raw_outcomes": raw_outcomes.get(pid),
            "cost_estimate": cost_stats.get(pid),
            "prerequisite_failure": prereq_failures.get(pid),
            "source_count": len(spec.get("sources", [])),
            "sources": spec.get("sources", []),
            "spec_url": f"../../providers/{pid}/SPEC.md" if pid in specs else "../docs/evaluation-framework.md",
            "unattested": unattested,
            "unranked_cohorts": endpoint_cohorts,
        }

    # ---- insights: keep only reader-actionable fields, group by provider
    insights = []
    for ins in summary.get("insights", []):
        grp = ins.get("group") or {}
        insights.append({
            "provider": grp.get("provider"),
            "suite": grp.get("suite"),
            "category": ins.get("category"),
            "title": ins.get("title"),
            "finding": ins.get("finding"),
            "implication": ins.get("implication"),
            "boundary": ins.get("boundary"),
            "config_id": grp.get("config_id"),
            "concurrency": grp.get("concurrency"),
        })

    gaps = defaultdict(set)
    for g in summary.get("provenance_gaps", []):
        gaps[g["provider"]].update(g.get("gaps", []))

    data = {
        "generated_at": summary.get("generated_at"),
        "source_hashes": source_hashes,
        "evidence_issues": evidence_issues,
        "snapshot_label": str(summary.get("generated_at", "unknown"))[:10] + " evidence snapshot",
        "counts": summary.get("counts", {}),
        "limitations": summary.get("limitations", ""),
        "workloads": WORKLOADS,
        "hard_requirements": HARD_REQUIREMENTS,
        "feature_labels": FEATURE_LABELS,
        "residency_surfaces": SURFACES,
        "providers": providers,
        "provider_order": providers_order,
        "insights": insights,
        "provenance_gaps": {k: sorted(v) for k, v in gaps.items()},
        "campaigns": campaigns,
        "links": {
            "full_dashboard": "../index.html",
            "findings": "../docs/findings.md",
            "leaderboard": "../docs/leaderboard.md",
            "framework": "../docs/evaluation-framework.md",
            "eu_guide": "../docs/eu-data-residency.md",
            "detailed": "../docs/detailed-report.md",
        },
        "method_notes": [
            "No composite capability or confidence score is used. Unknown requirements stay unresolved.",
            "Eligible cohorts require >=5 correctness-validated attempts; five passes still give a "
            "95% Wilson lower bound of only ~56.6%.",
            "Client wall time includes cleanup and is not pure cold provisioning.",
            "Different providers faced different tasks and counts; totals are coverage, not pooled "
            "vendor reliability.",
            "Pricing is published list rate, reviewed 2026-10-13, never invoice-backed. GB is not GiB; "
            "a physical core is not a vCPU.",
            "Unknown capability is not a no; conditional capability is not a yes. A documented feature "
            "is not a tested deployment.",
            "Local control is a measurement baseline, never a secure runtime for untrusted code.",
        ],
    }

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "data.json").write_text(json.dumps(data, indent=1, sort_keys=False))

    template = (OUT / "template.html").read_text()
    for document in ["findings.md", "detailed-report.md", "evaluation-framework.md", "eu-data-residency.md"]:
        template = template.replace(f'href="../{document}', f'href="../docs/{document}')
    payload = json.dumps(data, separators=(",", ":")).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    html = template.replace("__DATA_JSON__", payload).replace("__APP_JS__", (OUT / "app.js").read_text())
    (OUT / "index.html").write_text(portal_html(html, "../", "variant/index.html"))
    print(f"wrote {OUT / 'data.json'} ({(OUT / 'data.json').stat().st_size} bytes)")
    print(f"wrote {OUT / 'index.html'} ({(OUT / 'index.html').stat().st_size} bytes)")


if __name__ == "__main__":
    main()
