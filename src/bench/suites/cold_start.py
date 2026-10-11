"""Cold start benchmark: measures provisioning and initial execution latency."""
from __future__ import annotations

from ...core.models import ExecuteCodeRequest


class ColdStartBenchmark:
    name = "cold_start"
    description = "Measures sandbox initialization and first execution latency."

    @staticmethod
    def get_request() -> ExecuteCodeRequest:
        code = (
            "import sys, time\n"
            "print('SANDBOX_READY')\n"
            "print(f'PYTHON_VERSION:{sys.version.split()[0]}')\n"
        )
        return ExecuteCodeRequest(code=code, timeout_seconds=60)
