"""High-resolution telemetry profiler for sandbox execution benchmarking."""
from __future__ import annotations

import time
from contextlib import contextmanager
from typing import Generator
from ..core.models import ExecutionTiming


class BenchmarkProfiler:
    """Tracks latency breakdowns across lifecycle stages."""

    def __init__(self) -> None:
        self.timings = ExecutionTiming()
        self._start_total: float = 0.0

    def start(self) -> None:
        self._start_total = time.perf_counter()

    def finish(self) -> ExecutionTiming:
        if self._start_total > 0:
            self.timings.total_wall_clock_ms = round((time.perf_counter() - self._start_total) * 1000.0, 3)
        return self.timings

    @contextmanager
    def measure(self, phase: str) -> Generator[None, None, None]:
        t0 = time.perf_counter()
        try:
            yield
        finally:
            elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 3)
            if hasattr(self.timings, f"{phase}_ms"):
                setattr(self.timings, f"{phase}_ms", elapsed_ms)
