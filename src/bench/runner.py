"""Orchestrates benchmark execution runs across backends and test suites."""
from __future__ import annotations

import asyncio
import logging
import hashlib
import json
import time
import uuid
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

from ..core.interface import ExecutionBackend
from ..core.models import (
    BenchmarkExecutionResult,
    GeneratedArtifact,
    PreparedExecution,
    ResolvedInputFile,
)
from .cost import calculate_cost
from .suites import ALL_BENCHMARKS
from .telemetry import BenchmarkProfiler
from .validation import validate


def resolved_inputs(request):
    return [ResolvedInputFile(artifact_name=i.artifact_name,
                             relative_path=i.target_name or i.artifact_name,
                             data=i.data if i.data is not None else (i.text or "").encode())
            for i in request.input_files]


def request_fingerprint(request):
    return dict(code=request.code, language=request.language, timeout=request.timeout_seconds,
                inputs=[(i.relative_path, hashlib.sha256(i.data).hexdigest()) for i in resolved_inputs(request)])

logger = logging.getLogger(__name__)


class BenchmarkRunner:
    """Executes standardized test suites against an ExecutionBackend."""

    def __init__(self, backend: ExecutionBackend) -> None:
        self.backend = backend

    async def run_benchmark(self, benchmark_cls: type) -> BenchmarkExecutionResult:
        run_id = f"bench-{uuid.uuid4().hex[:12]}"
        request = benchmark_cls.get_request()
        requests = getattr(benchmark_cls, "get_requests", lambda: [request])()
        workload = request_fingerprint(request)
        if len(requests) > 1:
            workload["steps"] = [request_fingerprint(r) for r in requests]
        contract = {"validator_sha256": hashlib.sha256(Path(__file__).with_name("validation.py").read_bytes()).hexdigest(),
                    "expected_metrics": getattr(benchmark_cls, "expected_metrics", {}),
                    "expected_artifacts": {p: hashlib.sha256(b).hexdigest() for p, b in getattr(benchmark_cls, "expected_artifacts", {}).items()},
                    "expected_status": getattr(benchmark_cls, "expected_status", None),
                    "step_statuses": getattr(benchmark_cls, "step_statuses", None)}
        profiler = BenchmarkProfiler()
        profiler.start()

        result = BenchmarkExecutionResult(
            run_id=run_id,
            suite=benchmark_cls.name,
            provider=self.backend.name,
            status="failed",
            started_at=datetime.now(timezone.utc).isoformat(),
            workload_sha256=hashlib.sha256(json.dumps(workload, sort_keys=True).encode()).hexdigest(),
            evaluation_contract_sha256=hashlib.sha256(json.dumps(contract, sort_keys=True).encode()).hexdigest(),
        )
        artifacts = []
        raw = None
        cancelled = False
        if getattr(benchmark_cls, "requires_session", False) and not getattr(self.backend, "supports_session_calls", False):
            result.evaluation = "skipped"
            result.warnings.append("Adapter lacks an explicit reusable session contract; vendor support remains unverified.")
            return result


        prepared = PreparedExecution(
            run_id=run_id,
            nonce=uuid.uuid4().hex,
            root=f"/tmp/bench-{self.backend.name}-{run_id}",
            request=request,
            inputs=resolved_inputs(request),
        )

        try:
            with profiler.measure("initialize"):
                await self.backend.initialize()
            # 1. Preparation phase
            with profiler.measure("prepare"):
                await self.backend.prepare(prepared)
                result.preparation = "success"

            # 2. Execution phase
            with profiler.measure("execute"):
                outputs = []
                for step_idx, step_request in enumerate(requests):
                    prepared.request = step_request
                    prepared.inputs = resolved_inputs(step_request)
                    if step_idx:
                        await self.backend.prepare(prepared)
                    t0 = time.perf_counter()
                    raw = await self.backend.execute(prepared)
                    result.steps.append({"index": step_idx, "status": raw.status,
                                         "stdout": raw.stdout, "stderr": raw.stderr,
                                         "wall_ms": round((time.perf_counter() - t0) * 1000, 3)})
                    outputs.append(raw.stdout)
                    expected_statuses = getattr(benchmark_cls, "step_statuses", ["success"] * len(requests))
                    if raw.status != expected_statuses[step_idx]:
                        break
                result.execution = raw.status
                result.status = raw.status
                result.stdout = "\n".join(outputs)
                result.stderr = raw.stderr
                result.exit_code = raw.exit_code
                result.warnings.extend(raw.warnings)

            # 3. Collection phase (if requested)
            if request.include_generated_artifacts:
                with profiler.measure("collect"):
                    artifacts = await self.backend.collect_artifacts(prepared, raw)
                    result.collection = "success" if artifacts else "empty"
                    result.artifacts = [
                        GeneratedArtifact(
                            artifact_id=f"{run_id}-{idx}",
                            filename=art.relative_path.split("/")[-1],
                            relative_path=art.relative_path,
                            size_bytes=art.size_bytes,
                            sha256=art.sha256,
                            status="saved" if art.data is not None else "failed",
                            error=art.error,
                        )
                        for idx, art in enumerate(artifacts)
                    ]

        except asyncio.CancelledError:
            cancelled = True
            result.status = "failed"
            result.execution = "failed"
            result.error = "Campaign interrupted; remote cancellation is not attested"
            result.checks["campaign_not_interrupted"] = False
        except asyncio.TimeoutError:
            result.status = "timed_out"
            result.execution = "timed_out"
            result.warnings.append("Execution exceeded timeout threshold.")
        except Exception as exc:
            result.status = "failed"
            result.error = f"{type(exc).__name__}: {exc}"
            logger.exception("Benchmark %s failed on provider %s", benchmark_cls.name, self.backend.name)
        finally:
            with profiler.measure("cleanup"):
                try:
                    await asyncio.wait_for(self.backend.cleanup(prepared), 30)
                    result.cleanup = "success"
                except Exception as err:
                    result.cleanup = "failed"
                    result.warnings.append(f"cleanup_failed: {err}")

        # Finish timings & calculate cost attribution
        result.timings = profiler.finish()
        result.cost = calculate_cost(self.backend.name, result.timings)
        result.cost.details.update({"evidence": "estimate_unverified_rates", "billing_verified": False,
                                   "limitations": "Client wall time is not billable uptime; token counts and billing minima not verified."})
        validate(benchmark_cls, result, artifacts, request)
        if cancelled:
            result.evaluation = "fail"
        if self.backend.capabilities.model_managed and result.evaluation != "unknown":
            trace = raw.manifest if raw else None
            traced = bool(trace and trace.get("exact_code_executed") and trace.get("tool_outcome_ok"))
            result.checks["exact_tool_execution_trace"] = traced
            result.provenance["tool_trace"] = trace
            if not traced:
                result.evaluation = "fail"
                result.warnings.append("Model response is not proof that the exact benchmark code executed.")

        return result

    async def run_all(self) -> list[BenchmarkExecutionResult]:
        results: list[BenchmarkExecutionResult] = []
        for bench_cls in ALL_BENCHMARKS:
            logger.info("Running %s against %s...", bench_cls.name, self.backend.name)
            res = await self.run_benchmark(bench_cls)
            results.append(res)
        return results

    async def run_concurrent_burst(
        self, benchmark_cls: type, concurrency: int = 3
    ) -> list[BenchmarkExecutionResult]:
        """Fire concurrent executions simultaneously to stress provider concurrency."""
        if concurrency > 1:
            raise ValueError("Shared backend concurrency is unsafe; use the campaign's independent workers.")
        tasks = [self.run_benchmark(benchmark_cls) for _ in range(concurrency)]
        return await asyncio.gather(*tasks)
