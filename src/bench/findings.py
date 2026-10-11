"""Reader-first findings generated from retained attempts, not fixed claims."""
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.parse import urlencode

from .evidence import evidence_bundle
from .insights import TASKS, measured_insights, provenance_gaps
from .specifications import specification_bundle


def report_bundle(reports_dir=Path("reports")):
    evidence = evidence_bundle(reports_dir)
    specs = specification_bundle(reports_dir)
    hashed = [r for r in evidence["attempts"] if r.get("evaluation_contract_sha256")]
    return {"schema_version": 1, "generated_at": datetime.now(timezone.utc).isoformat(),
        "providers": evidence["providers"], "specifications": specs["specifications"],
        "summaries": [r for r in evidence["summaries"] if r["eligible"]], "campaigns": evidence["campaigns"],
        "insights": measured_insights(evidence),
        "provenance_gaps": [{"provider": r["provider"], "run_id": r.get("run_id"), "gaps": provenance_gaps(r)}
                            for r in hashed if provenance_gaps(r)],
        "counts": {"all_attempts": len(evidence["attempts"]),
            "legacy": sum(r.get("evidence_label") == "legacy_unvalidated" for r in evidence["attempts"]),
            "contract_hashed_attempts": len(hashed),
            "remote_model_contract_hashed_attempts": sum(r["runtime_kind"] != "local_control" for r in hashed),
            "contract_hashed_outcomes": dict(Counter(r["evaluation"] for r in hashed))},
        "limitations": evidence["methodology"]}


def attempt_link(ref):
    selector = {"provider": ref["provider"], "run_id": ref["run_id"]} if ref.get("run_id") else {
        "provider": ref["provider"], "report_path": ref["report_path"], "report_index": ref["report_index"]}
    label = ref.get("run_id") or f"{ref['report_path']}[{ref['report_index']}]"
    return f"[{label}](../index.html#raw?{urlencode(selector)})"


def proof(row):
    fields = ("provider", "suite", "config_id", "workload_sha256", "evaluation_contract_sha256",
              "adapter_sha256", "stack_sha256", "concurrency", "client_os", "client_arch", "runtime_kind")
    selector = {key: row[key] for key in fields}
    return f"[All {len(row['run_refs'])} attempts](../index.html#raw?{urlencode(selector)}) · " + attempt_link(row["run_refs"][0])


def ms(value):
    return "—" if value is None else f"{value:,.1f}"


def generate_findings(reports_dir=Path("reports")):
    bundle = report_bundle(reports_dir)
    evidence = evidence_bundle(reports_dir)
    counts = bundle["counts"]
    remote = [r for r in bundle["summaries"] if r["runtime_kind"] == "remote_runtime"]
    names = bundle["providers"]
    lines = ["# Sandbox benchmark: what the evidence helps you decide", "",
        f"Generated **{bundle['generated_at'][:10]}** from retained attempts. [Dashboard](../index.html#takeaways) · [Methods](evaluation-framework.md).", "",
        "## Read this first", "",
        "**Choose by the operation your agent needs, then inspect the failed attempts.** A fast readiness call does not establish that file transfer, state reuse or output fidelity works. Results below apply to recorded integrations and setups.", "",
        "### Problems worth reproducing before choosing", ""]
    failures = [i for i in bundle["insights"] if i["category"] == "failure"]
    if not failures:
        lines.append("No failures appear in the eligible direct-remote setup groups. Missing coverage is still unknown.")
    for insight in failures:
        row = insight["group"]
        lines.extend([f"**{insight['title']}.** {insight['finding']} {insight['implication']}", "",
            f"- What this proves: {insight['boundary']}",
            f"- Next check: {insight['action']}",
            f"- Setup `{row['config_id']}`, adapter `{row['adapter_sha256'][:8]}`. Exact attempts: {proof(row)}.", ""])
    lines.extend(["### Operations with useful positive evidence", "",
        "These are candidates for a larger trial, not an overall vendor ranking. Each cell is a separate setup/task group; absent operations were not established by this pilot.", "",
        "| Integration / setup | Operation | Passed / evaluated | Exact proof |",
        "| :--- | :--- | :--- | :--- |"])
    for insight in bundle["insights"]:
        if insight["category"] == "workflow":
            r = insight["group"]
            lines.append(f"| {names.get(r['provider'], r['provider'])} / `{r['config_id']}` | {TASKS[r['suite']]} | {r['outcomes'].get('pass', 0)} / {r['n']} | {proof(r)} |")
    lines.extend(["", "Binary/ETL passes mean the recorded host byte/hash and aggregation checks passed. Returned artifact bytes are not retained in these JSON reports, so an independent offline rehash of those bytes is unavailable. State/recovery checks exercise files across calls. Installation covers one offline pure-Python wheel, not native builds or public package downloads.", "",
        "## How long does the full integration take?", "",
        "Fresh adapter per attempt; new sessions/sandboxes where that adapter provisions them. Databricks SQL is a warehouse execution path. Successful lifecycle timing includes initialization, staging, execution, collection and cleanup; final teardown is separate. Different hardware requests, regions and uncontrolled caches make these descriptive observations, not an equal-hardware race.", "",
        "| Integration / setup | Passed / evaluated | Successful median ms (timing n) | All-evaluated median ms | Exact proof |",
        "| :--- | :--- | :--- | :--- | :--- |"])
    for r in remote:
        if r["suite"] == "cold_start" and r["concurrency"] == 1:
            lines.append(f"| {names.get(r['provider'], r['provider'])} / `{r['config_id']}` | {r['outcomes'].get('pass', 0)} / {r['n']} | {ms(r['latency_ms']['p50'])} ({r['latency_ms']['n']}) | {ms(r['attempt_latency_ms']['p50'])} | {proof(r)} |")
    lines.extend(["", "### Fast calculation is not the same as fast completion", "",
        "The same prime fixture exposes two different timings. Guest calculation excludes most orchestration; the client lifecycle is what a caller waits for. Do not divide by guest-visible CPUs to infer per-core performance: visible host resources may differ from reserved resources.", "",
        "| Integration / setup | Passed / evaluated | Guest median ms | Successful lifecycle median ms | Exact proof |",
        "| :--- | :--- | :--- | :--- | :--- |"])
    for r in remote:
        if r["suite"] == "cpu_stress" and r["concurrency"] == 1:
            lines.append(f"| {names.get(r['provider'], r['provider'])} / `{r['config_id']}` | {r['outcomes'].get('pass', 0)} / {r['n']} | {ms(r['workload_ms']['p50'])} | {ms(r['latency_ms']['p50'])} | {proof(r)} |")
    lines.extend(["", "### Deadline responses", ""])
    for insight in bundle["insights"]:
        if insight["group"]["suite"] == "timeout_handling":
            lines.extend([f"- **{insight['title']}:** {insight['finding']} {insight['boundary']} [Exact attempts below](#evidence-scope-and-reproduction)."])
    lines.extend(["", "## What happens with more workers?", "",
        "| Campaign / raw proof | Workers | Verified / attempted | Wall seconds | Verified completions/s |",
        "| :--- | :--- | :--- | :--- | :--- |"])
    for c in bundle["campaigns"]:
        if c["concurrency"] > 1:
            lines.append(f"| [{c['report_path']}](../{c['evidence_path']}) | {c['concurrency']} | {c['passes']} / {c['attempts']} | {c['wall_seconds_including_warmups']:.2f} | {c['verified_completions_per_second_including_warmup_time']:.2f} |")
    lines.extend(["", "Campaign rates include warmup time if present. Check campaign workload hashes and attempt outcomes; short bursts do not establish sustained capacity. Repeat a concurrency sweep before interpreting small rate differences.", "",
        "## Evidence scope and reproduction", "",
        f"The repository retains **{counts['all_attempts']} attempts**, including **{counts['legacy']} legacy/unvalidated observations**. **{counts['contract_hashed_attempts']} attempts carry an evaluator-contract hash**, including **{counts['remote_model_contract_hashed_attempts']} remote/model-mediated attempts**. A recorded contract hash is not proof of complete provenance or a successful remote execution.", "",
        "Comparison groups require at least five evaluated trials and recorded evaluator/adapter hashes. They are kept separate by workload, evaluator, configuration, adapter, stack, client platform and concurrency. **Eligible does not mean latest:** multiple earlier versions can qualify; none is silently selected as the current baseline. Warmups are excluded. Model-mediated tools and local controls are separate interfaces.", "",
        "| Integration | Passed | Failed | Setup/task groups |",
        "| :--- | :--- | :--- | :--- |"])
    for provider in sorted({r["provider"] for r in remote}):
        rows = [r for r in remote if r["provider"] == provider]
        lines.append(f"| {names.get(provider, provider)} | {sum(r['outcomes'].get('pass', 0) for r in rows)} | {sum(r['outcomes'].get('fail', 0) for r in rows)} | {len(rows)} |")
    lines.extend(["", "These totals describe coverage, not pooled provider reliability: providers faced different tasks and counts. Five passes out of five have a 95% Wilson lower success bound of roughly 56.6%; shared infrastructure may correlate attempts. Five-sample p95 is exploratory.", "",
        "### Provenance gaps and failed prerequisites", ""])
    gaps = Counter((r["provider"], gap) for r in bundle["provenance_gaps"] for gap in r["gaps"])
    for (provider, gap), n in sorted(gaps.items()):
        lines.append(f"- **{names.get(provider, provider)}:** {gap} in {n} contract-hashed attempts. Inspect its [tested settings](../../providers/{provider}/tested-configurations.md).")
    for provider in ("databricks_sandbox", "daytona", "openai_tool"):
        runs = [r for r in evidence["attempts"] if r["provider"] == provider and r["evaluation"] == "fail"]
        if runs:
            r = max(runs, key=lambda r: r.get("started_at") or "")
            detail = r.get("stderr") or r.get("error") or "; ".join(r.get("warnings", [])) or "No originating error retained"
            # Quote the recorded diagnosis; do not infer credentials from generic client failures.
            lines.append(f"- **{names.get(provider, provider)}:** latest retained failed attempt says {json.dumps(detail[:350])}. {attempt_link(r)}. This is an access/integration gap, not a vendor uptime score.")
    lines.extend(["", "**Cleanup evidence:** adapter cleanup/teardown success records a lifecycle response, not independently verified remote absence. No scoped post-run GCP status artifact is retained with these campaigns; the earlier zero-remaining-sandboxes claim is therefore not independently auditable. Timeout responses also do not attest remote termination.", "",
        "## Decisions the pilot cannot settle", "",
        "- **Cheapest successful task:** official list rates are documented, but invoice-backed campaign cost—including retries, failures, idle time and storage—has not been measured. [Price sheets](../index.html#economics).",
        "- **Custom images, GPUs and resource guarantees:** documented options need configuration-specific experiments. Guest-visible CPUs/memory are observations. [Setup options and sources](../index.html#customization).",
        "- **Production reliability, sustained scale and isolation:** this pilot does not establish an SLA, quota ceiling, controlled network policy or cross-tenant isolation. Historical Kubernetes observations are deployment-unattested.", "",
        "**Next useful experiment:** take the shortlist for your required operations, pin the setup and payload, reproduce the known failure checks, then collect larger repeated samples, deletion-status artifacts and gross cost per verified completion. [Methods and recipes](evaluation-framework.md).", "",
        "### All deadline/output observations and exact attempts", ""])
    for insight in bundle["insights"]:
        if insight["group"]["suite"] in {"output_fidelity", "timeout_handling"}:
            lines.extend([f"- **{insight['title']}:** {insight['finding']} {proof(insight['group'])}"])
    root = Path(reports_dir)
    (root / "docs").mkdir(parents=True, exist_ok=True)
    (root / "data/derived").mkdir(parents=True, exist_ok=True)
    (root / "docs/findings.md").write_text("\n".join(lines) + "\n")
    (root / "data/derived/evaluation-summary.json").write_text(json.dumps(bundle, indent=2))


if __name__ == "__main__":
    generate_findings()
