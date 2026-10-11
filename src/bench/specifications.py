"""Normalized provider -> configuration -> attempt -> runtime observation relationships."""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from .evidence import PROVIDERS, load_evidence, summarize
from .provider_overview import render_overview, update_spec_page


def specification_bundle(reports_dir=Path("reports"), providers_dir=Path("providers")):
    specifications = {}
    for path in sorted(Path(providers_dir).glob("*/spec.json")):
        spec = json.loads(path.read_text())
        specifications[spec["provider"]] = spec
    attempts, _ = load_evidence(reports_dir)
    configurations = defaultdict(list)
    for run in attempts:
        p = run.get("provenance", {})
        if run.get("schema_version") != 2:
            continue
        key = (run["provider"], p.get("config_id", "unrecorded"), p.get("adapter_sha256", "unrecorded"),
               p.get("concurrency", 1), p.get("stack_sha256", "unrecorded"))
        configurations[key].append(run)
    tested = []
    for key, runs in sorted(configurations.items()):
        provider, config_id, adapter_sha, concurrency, stack_sha = key
        inventories = [r for r in runs if r["suite"] == "runtime_inventory" and r["evaluation"] == "pass"]
        tested.append({"schema_version": 1, "provider": provider, "config_id": config_id,
            "adapter_sha256": adapter_sha, "stack_sha256": stack_sha, "concurrency": concurrency,
            "requested": runs[-1].get("provenance", {}).get("configuration", {}),
            "request_recording_complete": "requested" in runs[-1].get("provenance", {}).get("configuration", {}),
            "client": {k: runs[-1].get("provenance", {}).get(k) for k in ["client_python", "client_os", "client_arch", "sdk_versions", "execution_stack"]},
            "runtime_kind": runs[-1]["runtime_kind"],
            "attempt_ids": [r["run_id"] for r in runs],
            "suites": sorted({r["suite"] for r in runs}),
            "observations": [{"run_id": r["run_id"], "observed_at": r["started_at"], "report_path": r["report_path"],
                              "metrics": r["metrics"]} for r in inventories],
            "reports": sorted({r["report_path"] for r in runs}),
            "last_measured_at": max(r.get("started_at") or "unknown" for r in runs),
            "limitations": "Recorded requests and guest-visible observations are distinct; guest observations are not reserved-resource, image, GPU-eligibility or isolation attestation. Early attempts without requested settings remain incomplete."})
    return {"schema_version": 1, "specifications": specifications, "tested_configurations": tested}


def export_specifications(reports_dir=Path("reports"), providers_dir=Path("providers")):
    bundle = specification_bundle(reports_dir, providers_dir)
    summaries = summarize(load_evidence(reports_dir)[0])
    for provider in bundle["specifications"]:
        configs = sorted((c for c in bundle["tested_configurations"] if c["provider"] == provider),
                         key=lambda c: (c["request_recording_complete"], c["last_measured_at"]), reverse=True)
        directory = Path(providers_dir) / provider
        (directory / "tested-configurations.json").write_text(json.dumps({"schema_version": 1, "provider": provider, "configurations": configs}, indent=2))
        lines = [f"# {PROVIDERS.get(provider, provider)} — tested configurations", "",
            "Generated from real attempt records. [Documented capabilities](SPEC.md) describe broader options; the tested integration is narrower.", "",
            "Requested settings, client versions, observation timestamps and raw evidence are retained in [tested-configurations.json](tested-configurations.json). No GPU-enabled or custom-image configuration was tested in these default campaigns.", ""]
        if not configs:
            lines.append("No versioned campaign configuration was recorded. Historical reports are not configuration attestation.")
        for c in configs:
            lines.extend([f"## Configuration `{c['config_id']}` / adapter `{c['adapter_sha256'][:12]}` / concurrency {c['concurrency']}", "",
                          f"Runtime classification: **{c['runtime_kind']}**. Request recording complete: **{c['request_recording_complete']}**.", "",
                          "```json", json.dumps(c["requested"], indent=2), "```", "",
                          "Client execution stack: `" + json.dumps(c["client"].get("execution_stack"), sort_keys=True) + "`.", "",
                          "Suites: " + ", ".join(f"`{s}`" for s in c["suites"]), "",
                          "Raw reports: " + ", ".join(f"[{p}](../../reports/{p})" for p in c["reports"]), ""])
            for observation in c["observations"]:
                m = observation["metrics"]
                lines.extend([f"### Observation `{observation['run_id']}` — {observation['observed_at']}", "",
                    "| Field | Guest-visible observation |", "| :--- | :--- |",
                    f"| Runtime | `{json.dumps(m.get('runtime', {}), sort_keys=True)}` |",
                    f"| CPU | `{json.dumps(m.get('cpu', {}), sort_keys=True)}` |",
                    f"| Memory | `{json.dumps(m.get('memory', {}), sort_keys=True)}` |",
                    f"| cgroup limits | `{json.dumps(m.get('cgroup', {}), sort_keys=True)}` |",
                    f"| GPU probe | `{json.dumps(m.get('gpu', {}), sort_keys=True)}` |", ""])
            if not c["observations"]:
                lines.append("No successful runtime inventory for this exact recorded configuration/adapter/stack. See raw checks and prerequisite failures.")
            lines.extend(["", c["limitations"], ""])
        (directory / "tested-configurations.md").write_text("\n".join(lines))
        update_spec_page(directory / "SPEC.md", render_overview(bundle["specifications"][provider], configs,
                         summaries, PROVIDERS.get(provider, provider)))
    output = Path(reports_dir) / "data/derived/specifications.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(bundle, indent=2))
    return output
