"""CPU stress benchmark: compute-intensive workload to test processor throttling."""
from __future__ import annotations

from ...core.models import ExecuteCodeRequest


class CpuStressBenchmark:
    name = "cpu_stress"
    description = "Tests compute speed and CPU throttling via prime sieve & matrix multiplications."

    @staticmethod
    def get_request() -> ExecuteCodeRequest:
        code = (
            "import time\n"
            "t0 = time.perf_counter()\n"
            "def count_primes(n):\n"
            "    sieve = [True] * n\n"
            "    for i in range(2, int(n**0.5) + 1):\n"
            "        if sieve[i]:\n"
            "            for j in range(i*i, n, i):\n"
            "                sieve[j] = False\n"
            "    return sum(sieve[2:])\n"
            "total = count_primes(2_000_000)\n"
            "elapsed = time.perf_counter() - t0\n"
            "print(f'PRIMES_FOUND:{total}')\n"
            "print(f'COMPUTE_TIME_SEC:{elapsed:.4f}')\n"
        )
        return ExecuteCodeRequest(code=code, timeout_seconds=120)
