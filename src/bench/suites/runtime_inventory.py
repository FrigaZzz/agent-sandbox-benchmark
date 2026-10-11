"""A common, credential-free runtime inventory across every adapter."""
from pathlib import Path
from ...core.models import ExecuteCodeRequest


class RuntimeInventoryBenchmark:
    name = "runtime_inventory"
    description = "Inventory CPU/cgroup/memory/runtime/packages/tools/GPU observations without credentials."
    expected_metrics = {"inventory_schema_version": 1}

    @staticmethod
    def get_request():
        code = Path(__file__).with_name("runtime_probe.py").read_text()
        return ExecuteCodeRequest(code=code, timeout_seconds=45)
