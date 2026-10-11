"""Measured observations shared by the narrative, dashboard and briefing.

Eligibility is a sample-size rule, not a latest-version or provenance guarantee.
Every observation retains its setup row and the exact underlying attempt refs.
"""
import hashlib
import json

from .evidence import PROVIDERS, distribution
from .runner import request_fingerprint
from .suites.timeout_handling import TimeoutHandlingBenchmark
from .suites.workflows import OutputFidelityBenchmark


TASKS = {
    "cold_start": "first-call readiness", "cpu_stress": "prime calculation",
    "artifact_roundtrip": "binary file round trip", "data_pipeline": "data cleaning and returned summary",
    "sqlite_analytics": "SQLite queries and rollback", "repository_task": "code edit and test loop",
    "output_fidelity": "byte-exact stdout", "session_state": "disk state across calls",
    "error_recovery": "recovery after an exception", "dependency_install": "offline Python package install",
    "timeout_handling": "deadline response", "runtime_inventory": "guest environment inventory",
}
WORKFLOWS = {"artifact_roundtrip", "data_pipeline", "dependency_install", "session_state", "error_recovery"}


def matching_runs(row, attempts):
    identities = {(r["report_path"], r["report_index"]) for r in row["run_refs"]}
    return [r for r in attempts if (r["report_path"], r["report_index"]) in identities]


def provenance_gaps(run):
    p = run.get("provenance", {})
    gaps = []
    for field in ("config_id", "adapter_sha256", "stack_sha256", "client_os", "client_arch"):
        if not p.get(field) or p[field] in {"unknown", "unrecorded"}:
            gaps.append(field + " not recorded")
    if not p.get("configuration", {}).get("requested"):
        gaps.append("requested settings not recorded")
    stack = p.get("execution_stack", {})
    if run["runtime_kind"] != "local_control" and (
        not stack.get("version") or "unrecorded" in str(stack["version"]).lower()
    ):
        gaps.append("execution CLI/SDK version not recorded")
    region = p.get("configuration", {}).get("requested", {}).get("region", "")
    if "see preflight" in str(region).lower():
        gaps.append("region refers to an unretained preflight")
    return gaps


def measured_insights(evidence):
    insights = []
    fixtures = {b.name: (b, hashlib.sha256(json.dumps(request_fingerprint(b.get_request()), sort_keys=True).encode()).hexdigest())
                for b in (OutputFidelityBenchmark, TimeoutHandlingBenchmark)}
    for row in evidence["summaries"]:
        if not row["eligible"] or row["runtime_kind"] != "remote_runtime" or row["concurrency"] != 1:
            continue
        runs = matching_runs(row, evidence["attempts"])
        provider = PROVIDERS.get(row["provider"], row["provider"])
        suite = row["suite"]
        failed = row["outcomes"].get("fail", 0)
        observation = None
        if suite == "output_fidelity":
            sizes = sorted({len(r.get("stdout", "").encode()) for r in runs})
            exact = sum(r.get("checks", {}).get("stdout_exact") is True for r in runs)
            mismatched = sum(r.get("checks", {}).get("stdout_exact") is False for r in runs)
            observation = dict(
                returned_stdout_bytes=sizes,
                title=f"{provider}: {'stdout loses fidelity' if mismatched else 'stdout fixture returned intact' if exact == row['n'] else 'stdout check incomplete'}",
                finding=f"{exact}/{row['n']} passed the exact-output check. Returned UTF-8 sizes: "
                        + ", ".join(f"{v:,}" for v in sizes) + " bytes.",
                implication="Byte-exact output consumers should reproduce the failed path before using it." if failed
                            else "This setup preserved the exercised Unicode, line order and final newline.",
                boundary="This is an output-path test, not a provider-wide file-size limit.",
                action="Compare stdout_exact, stdout_bytes and the raw output against the fixture.")
            fixture, fingerprint = fixtures[suite]
            if row["workload_sha256"] == fingerprint:
                expected = len(fixture.payload.encode())
                observation["expected_stdout_bytes"] = expected
                observation["finding"] += f" Expected fixture: {expected:,} bytes."
                if runs and all(r.get("stdout") == fixture.payload[:-1] for r in runs) and fixture.payload.endswith("\n"):
                    observation["finding"] += " Every response is missing exactly the final newline."
            # Describe truncation only when the retained output actually contains the banner.
            if runs and all("[... truncated, see the process log file for the full output ...]" in r.get("stdout", "") for r in runs):
                observation["finding"] += " Every response contains a process-log truncation banner."
        elif suite == "timeout_handling":
            times = distribution([r.get("timings", {}).get("execute_ms") for r in runs])
            if times["n"]:
                observation = dict(
                    execute_response_ms=times,
                    title=f"{provider}: {failed}/{row['n']} deadline responses failed" if failed
                          else f"{provider}: {row['n']}/{row['n']} deadline responses passed",
                    finding=f"Execute-phase responses ranged from {times['min']/1000:.2f} to {times['max']/1000:.2f} seconds; "
                            f"{row['outcomes'].get('pass', 0)}/{row['n']} passed the recorded timeout oracle.",
                    implication="Budget for the observed response time, including work performed inside this adapter's execute phase.",
                    boundary="Timeout status and an absent completion marker do not independently prove remote process termination.",
                    action="Read bounded_response, step status and execute_ms; verify cancellation separately.")
                fixture, fingerprint = fixtures[suite]
                if row["workload_sha256"] == fingerprint:
                    deadline = fixture.get_request().timeout_seconds
                    observation["finding"] += f" Requested deadline: {deadline:g}s; response budget: {deadline+5:g}s."
        elif suite in WORKFLOWS:
            observation = dict(
                title=f"{provider}: {TASKS[suite]}",
                finding=f"{row['outcomes'].get('pass', 0)}/{row['n']} passed; {failed} failed on this recorded setup.",
                implication="Candidate for this operation in a larger workload-specific trial." if not failed
                            else "Resolve the failing check before depending on this operation.",
                boundary="Disk state means filesystem reuse, not interpreter or snapshot persistence; installation covers one offline pure-Python wheel.",
                action="Repeat with your own file sizes, packages and multi-call workflow.")
        elif failed:
            warnings = sorted({w for r in runs if r["evaluation"] == "fail" for w in r.get("warnings", [])})
            checks = sorted({k for r in runs if r["evaluation"] == "fail" for k, v in r.get("checks", {}).items() if v is not True})
            observation = dict(
                title=f"{provider}: {failed}/{row['n']} {TASKS.get(suite, suite)} attempts failed",
                finding="Checks not passed: " + (", ".join(checks) or "no failed check retained")
                        + (". Warnings: " + "; ".join(warnings) if warnings else "") + ".",
                implication="A failed connection or lifecycle call differs from a wrong computed answer.",
                boundary="Inspect the failed checks and execution status before attributing this to the computation.",
                action="Reproduce the connection/lifecycle failure with the same setup.")
        if observation:
            observation.update(category="failure" if failed else "workflow" if suite in WORKFLOWS else "observation",
                               group=row, evidence=row["run_refs"])
            insights.append(observation)
    return sorted(insights, key=lambda x: (x["category"] != "failure",
        -x["group"]["outcomes"].get("fail", 0) / x["group"]["n"], x["group"]["suite"], x["group"]["provider"]))
