"""One evidence/aggregation implementation shared by Markdown and HTML."""
from __future__ import annotations

import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path

from .validation import parse_metrics


PROVIDERS = {
    "gcp_vertex": "GCP Agent Sandbox", "modal": "Modal", "blaxel": "Blaxel", "e2b": "E2B",
    "daytona": "Daytona", "aws": "AWS AgentCore", "databricks": "Databricks SQL MCP",
    "databricks_sandbox": "Databricks Dedicated Sandbox", "gemini_tool": "Gemini Tool",
    "openai_tool": "OpenAI Tool", "alibaba": "Alibaba OpenSandbox / AgentRun",
    "k8s_agent_sandbox": "Kubernetes adapter (deployment unattested)", "local_baseline": "Local control",
}


def percentile(values, quantile):
    """Linear interpolation, explicitly descriptive (small-n tails are unstable)."""
    if not values:
        return None
    ordered = sorted(values)
    index = (len(ordered) - 1) * quantile
    low = int(index)
    return ordered[low] + (ordered[min(low + 1, len(ordered)-1)] - ordered[low]) * (index-low)


def distribution(values):
    values = [v for v in values if isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and v > 0]
    return {"n": len(values), "p50": percentile(values, .5), "p95": percentile(values, .95),
            "min": min(values) if values else None, "max": max(values) if values else None,
            "mean": statistics.mean(values) if values else None,
            "stdev": statistics.stdev(values) if len(values) > 1 else None}


def wilson(passed, n):
    if not n:
        return None
    z = 1.959963984540054
    p = passed / n
    center = (p + z*z/(2*n)) / (1 + z*z/n)
    half = z * math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / (1+z*z/n)
    return [max(0, center-half), min(1, center+half)]


def load_evidence(reports_dir=Path("reports")):
    attempts, issues, seen = [], [], set()
    root = Path(reports_dir)
    # Explicit input directories prevent derived JSON and UI fixtures from being
    # ingested as new attempts. Flat custom report directories remain supported.
    paths = list(root.glob("*.json"))
    paths += list((root / "data/attempts").rglob("*.json"))
    paths += list((root / "data/legacy").glob("*.json"))
    for path in sorted(paths):
        try:
            content = json.loads(path.read_text())
        except (ValueError, OSError) as exc:
            issues.append(f"{path.name}: unreadable report ({type(exc).__name__})")
            continue
        if not isinstance(content, list):
            continue
        for index, item in enumerate(content):
            if not isinstance(item, dict) or not item.get("provider"):
                issues.append(f"{path.name}[{index}]: missing provider or invalid attempt")
                continue
            run = dict(item)
            identity = (run["provider"], run.get("run_id", f"{path.name}:{index}"))
            if identity in seen:
                issues.append(f"{path.name}[{index}]: duplicate run_id excluded")
                continue
            seen.add(identity)
            run["report_path"] = path.relative_to(root).as_posix()
            run["report_index"] = index
            run["suite"] = run.get("suite") or "unnamed_legacy"
            run["metrics"] = run.get("metrics") or parse_metrics(run.get("stdout", ""))
            provenance = run.get("provenance", {})
            versioned = run.get("schema_version") == 2 and bool(run.get("workload_sha256")) and bool(run.get("started_at"))
            if not versioned:
                run["evaluation"] = "unknown"
                run["evidence_label"] = "legacy_unvalidated"
            else:
                run["evidence_label"] = "validated_attempt"
                if run.get("evaluation") == "pass" and (
                    not run.get("checks") or any(v is not True for v in run["checks"].values())
                    or run.get("cleanup") != "success" or run.get("teardown") != "success"
                ):
                    run["evaluation"] = "fail"
                    issues.append(f"{path.name}[{index}]: inconsistent pass evidence")
            kind = provenance.get("runtime_kind")
            if not kind:
                kind = "local_control" if run["provider"] in {"local", "local_baseline"} else "unattested_legacy"
                if run["provider"] in {"gemini_tool", "openai_tool"}:
                    kind = "model_mediated"
                if run["provider"] == "k8s_agent_sandbox":
                    kind = "unattested_endpoint"
            run["runtime_kind"] = kind
            attempts.append(run)
    return attempts, issues


def summarize(attempts):
    groups = defaultdict(list)
    for run in attempts:
        if run.get("provenance", {}).get("warmup"):
            continue
        p = run.get("provenance", {})
        key = (run["provider"], run["suite"], run.get("workload_sha256", "legacy"),
               p.get("config_id", "unknown"), p.get("concurrency", 1), run["runtime_kind"],
               p.get("client_os", "unknown"), p.get("client_arch", "unknown"), p.get("adapter_sha256", "unrecorded"),
               run.get("evaluation_contract_sha256", "unrecorded"),
               p.get("stack_sha256") or json.dumps({"python": p.get("client_python"), "sdks": p.get("sdk_versions")}, sort_keys=True))
        groups[key].append(run)
    rows = []
    for key, runs in sorted(groups.items()):
        provider, suite, workload, config_id, concurrency, kind, client_os, client_arch, adapter_sha, contract_sha, stack_sha = key
        outcomes = Counter(r.get("evaluation", "unknown") for r in runs)
        n = outcomes["pass"] + outcomes["fail"]
        valid = [r for r in runs if r.get("evaluation") == "pass"]
        verified = [r for r in runs if r.get("evaluation") in {"pass", "fail"}]
        rows.append({"provider": provider, "suite": suite, "workload_sha256": workload,
            "config_id": config_id, "configuration": runs[-1].get("provenance", {}).get("configuration", {}),
            "concurrency": concurrency, "runtime_kind": kind, "client_os": client_os, "client_arch": client_arch,
            "adapter_sha256": adapter_sha,
            "evaluation_contract_sha256": contract_sha, "stack_sha256": stack_sha,
            "attempts": len(runs), "outcomes": dict(outcomes), "n": n,
            "pass_rate": outcomes["pass"] / n if n else None,
            "success_ci95": wilson(outcomes["pass"], n),
            "latency_ms": distribution([r.get("timings", {}).get("total_wall_clock_ms") for r in valid]),
            "attempt_latency_ms": distribution([r.get("timings", {}).get("total_wall_clock_ms") for r in verified]),
            "phases_ms": {phase: distribution([r.get("timings", {}).get(phase) for r in valid])
                          for phase in ["initialize_ms", "prepare_ms", "execute_ms", "collect_ms", "cleanup_ms"]},
            "workload_ms": distribution([r.get("metrics", {}).get("workload_ms") or
                                         (r.get("metrics", {}).get("COMPUTE_TIME_SEC", 0) * 1000) for r in valid]),
            "eligible": n >= 5 and not outcomes["unknown"] and not outcomes["skipped"]
                        and kind in {"remote_runtime", "model_mediated"}
                        and contract_sha != "unrecorded" and adapter_sha != "unrecorded",
            "reports": sorted({r["report_path"] for r in runs}),
            "run_refs": [{"provider": r["provider"], "run_id": r.get("run_id"),
                          "report_path": r["report_path"], "report_index": r["report_index"]} for r in runs],
            "last_measured_at": max((r.get("started_at") or "unknown" for r in runs)),
        })
    return rows


def evidence_bundle(reports_dir=Path("reports")):
    attempts, issues = load_evidence(reports_dir)
    root = Path(reports_dir)
    paths = list((root / "campaigns").glob("*.json")) + list((root / "data/campaigns").glob("*.json"))
    campaigns = []
    for path in sorted(paths):
        campaign = dict(json.loads(path.read_text()), evidence_path=path.relative_to(root).as_posix())
        # Old campaign records store basenames. Resolve presentation links without
        # rewriting their original provenance; new records are data-root-relative.
        report = campaign["report_path"]
        if path.parent == root / "data/campaigns":
            campaign["report_path"] = "data/" + (report if "/" in report else "attempts/" + report)
        campaigns.append(campaign)
    return {"attempts": attempts, "summaries": summarize(attempts), "issues": issues,
            "campaigns": campaigns,
            "providers": PROVIDERS,
            "methodology": "Correctness-validated samples only. p95 is descriptive; use >=100 for tails. Wilson intervals assume independent attempts; shared infrastructure may correlate failures. Client wall time includes cleanup and is not pure cold provisioning. Pricing is unverified and unranked."}
