"""Host-side oracles. Provider 'success' is not workload correctness."""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any


def parse_metrics(stdout: str) -> dict[str, Any]:
    metrics = {}
    for line in stdout.splitlines():
        if line.startswith("BENCH_RESULT:"):
            try:
                value = json.loads(line.split(":", 1)[1])
                if isinstance(value, dict):
                    metrics.update(value)
            except ValueError:
                continue
        elif re.match(r"^[A-Z][A-Z_0-9]+:", line):
            key, value = line.split(":", 1)
            try:
                metrics[key] = json.loads(value)
            except ValueError:
                metrics[key] = value
    return metrics


def validate(benchmark, result, artifacts, request) -> None:
    result.metrics = parse_metrics(result.stdout)
    checks = {}
    if hasattr(benchmark, "expected_metrics"):
        checks.update({key: result.metrics.get(key) == value
                       for key, value in benchmark.expected_metrics.items()})
    elif benchmark.name == "cold_start":
        checks["ready"] = "SANDBOX_READY" in result.stdout.splitlines()
    elif benchmark.name == "cpu_stress":
        checks["prime_count"] = result.metrics.get("PRIMES_FOUND") == 148933
    elif benchmark.name == "disk_io":
        checks["disk_integrity"] = result.metrics.get("INTEGRITY_MATCH") == "True"
    elif benchmark.name == "timeout_handling":
        checks["timeout_observed"] = result.status == "timed_out" and bool(
            result.steps and result.steps[-1]["status"] == "timed_out")
        checks["did_not_finish"] = "SLEEP_FINISHED_UNEXPECTEDLY" not in result.stdout
        checks["bounded_response"] = result.timings.execute_ms <= (request.timeout_seconds + 5) * 1000
        result.warnings.append("Timeout response does not independently prove remote process termination.")
    elif benchmark.name == "parallel_throughput":
        checks["batch_completed"] = result.metrics.get("CONCURRENCY_TEST_PASSED") == "True"
    elif benchmark.name == "agent_multiturn":
        checks["single_call_pipeline"] = result.metrics.get("STATE_CONTINUITY_SUCCESS") == "True"
        result.warnings.append("Legacy pipeline runs in one call; not evidence of cross-call persistence.")
    elif benchmark.name == "output_fidelity":
        checks["stdout_exact"] = result.stdout == benchmark.payload
        result.metrics.update({"stdout_bytes": len(result.stdout.encode()),
                               "stdout_sha256": hashlib.sha256(result.stdout.encode()).hexdigest()})

    if hasattr(benchmark, "get_requests"):
        expected_steps = getattr(benchmark, "step_statuses", ["success"] * len(benchmark.get_requests()))
        checks["all_steps"] = [s["status"] for s in result.steps] == expected_steps
        if benchmark.name == "error_recovery":
            checks["expected_error"] = bool(result.steps and "EXPECTED_BENCH_ERROR" in result.steps[0]["stderr"])

    expected_artifacts = getattr(benchmark, "expected_artifacts", {})
    for path, expected in expected_artifacts.items():
        art = next((a for a in artifacts if a.relative_path == path), None)
        checks[f"artifact_bytes:{path}"] = art is not None and art.data == expected
        checks[f"artifact_hash:{path}"] = (
            art is not None and art.data is not None
            and hashlib.sha256(art.data).hexdigest() == hashlib.sha256(expected).hexdigest()
        )
    result.checks = checks
    if not checks:
        result.evaluation = "unknown"  # Environmental observations are not universal pass criteria.
    else:
        expected_status = getattr(benchmark, "expected_status", "success")
        if benchmark.name == "timeout_handling":
            expected_status = "timed_out"
        checks["execution_status"] = result.status == expected_status
        checks["cleanup"] = result.cleanup == "success"
        result.evaluation = "pass" if all(checks.values()) else "fail"
