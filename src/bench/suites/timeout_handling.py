"""Timeout and cancellation responsiveness benchmark."""
from __future__ import annotations

from ...core.models import ExecuteCodeRequest


class TimeoutHandlingBenchmark:
    name = "timeout_handling"
    description = "Tests hard cancellation by executing an intentional sleep longer than the requested timeout."

    @staticmethod
    def get_request() -> ExecuteCodeRequest:
        code = (
            "import time\n"
            "print('SLEEP_STARTING')\n"
            "time.sleep(30)\n"
            "print('SLEEP_FINISHED_UNEXPECTEDLY')\n"
        )
        # Bounded to a fast 4s timeout to verify provider cancellation responsiveness
        return ExecuteCodeRequest(code=code, timeout_seconds=4)
