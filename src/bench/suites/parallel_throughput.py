"""Concurrency and parallel execution throughput benchmark."""
from __future__ import annotations

from ...core.models import ExecuteCodeRequest


class ParallelThroughputBenchmark:
    name = "parallel_throughput"
    description = (
        "Measures multi-worker thread execution scaling and task throughput across 200 concurrent compute jobs."
    )

    @staticmethod
    def get_request() -> ExecuteCodeRequest:
        code = (
            "import time, hashlib, math\n"
            "from concurrent.futures import ThreadPoolExecutor\n"
            "\n"
            "def worker_job(item_id: int) -> str:\n"
            "    # Mix of CPU crypto hashing and math ops\n"
            "    h = hashlib.sha256(f'worker-seed-{item_id}'.encode())\n"
            "    for _ in range(1500):\n"
            "        h.update(h.digest())\n"
            "    # Small mathematical calculation\n"
            "    val = sum(math.sqrt(x) for x in range(1, 200))\n"
            "    return f'{h.hexdigest()[:8]}_{int(val)}'\n"
            "\n"
            "NUM_TASKS = 200\n"
            "NUM_WORKERS = 8\n"
            "\n"
            "# 1. Serial execution baseline (sample 20 tasks to project serial time)\n"
            "t0 = time.perf_counter()\n"
            "for i in range(20):\n"
            "    worker_job(i)\n"
            "projected_serial_sec = (time.perf_counter() - t0) * 10.0\n"
            "\n"
            "# 2. Concurrent Parallel execution with 8 workers\n"
            "t1 = time.perf_counter()\n"
            "with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:\n"
            "    results = list(executor.map(worker_job, range(NUM_TASKS)))\n"
            "parallel_sec = time.perf_counter() - t1\n"
            "\n"
            "speedup = (projected_serial_sec / parallel_sec) if parallel_sec > 0 else 1.0\n"
            "throughput = NUM_TASKS / parallel_sec if parallel_sec > 0 else 0.0\n"
            "\n"
            "print(f'PARALLEL_WORKERS:{NUM_WORKERS}')\n"
            "print(f'BATCH_TASKS:{NUM_TASKS}')\n"
            "print(f'SERIAL_PROJECTED_SEC:{projected_serial_sec:.4f}')\n"
            "print(f'PARALLEL_WALL_SEC:{parallel_sec:.4f}')\n"
            "print(f'SPEEDUP_RATIO:{speedup:.2f}')\n"
            "print(f'THROUGHPUT_TASKS_PER_SEC:{throughput:.1f}')\n"
            "print(f'CONCURRENCY_TEST_PASSED:{len(results) == NUM_TASKS}')\n"
        )
        return ExecuteCodeRequest(code=code, timeout_seconds=90)
