"""Memory stress benchmark: tests memory allocation ceilings and OOM behavior."""
from __future__ import annotations

from ...core.models import ExecuteCodeRequest


class MemoryStressBenchmark:
    name = "mem_stress"
    description = "Allocates memory in increments to find sandbox RAM ceilings and observe OOM handling."

    @staticmethod
    def get_request() -> ExecuteCodeRequest:
        code = (
            "import os, sys, time\n"
            "chunks = []\n"
            "target_mb = [50, 100, 250, 500, 1000, 2000]\n"
            "allocated_mb = 0\n"
            "try:\n"
            "    for mb in target_mb:\n"
            "        delta = mb - allocated_mb\n"
            "        chunks.append(b'X' * (delta * 1024 * 1024))\n"
            "        allocated_mb = mb\n"
            "        print(f'ALLOCATED_MB:{allocated_mb}')\n"
            "    print('MAX_ALLOCATION_REACHED:2000MB')\n"
            "except MemoryError:\n"
            "    print(f'OOM_AT_MB:{allocated_mb}')\n"
            "except Exception as e:\n"
            "    print(f'MEM_ERROR:{type(e).__name__}:{e}')\n"
        )
        return ExecuteCodeRequest(code=code, timeout_seconds=60)
