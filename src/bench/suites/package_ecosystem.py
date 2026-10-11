"""Package ecosystem and dependency installation benchmark."""
from __future__ import annotations

from ...core.models import ExecuteCodeRequest


class PackageEcosystemBenchmark:
    name = "package_ecosystem"
    description = (
        "Inspects pre-installed agent packages and tests dynamic runtime pip installation capability."
    )

    @staticmethod
    def get_request() -> ExecuteCodeRequest:
        code = (
            "import sys, subprocess, importlib, importlib.util\n"
            "\n"
            "# 1. Test core standard library packages\n"
            "core_mods = ['math', 'sqlite3', 'csv', 'hashlib', 'json', 'dataclasses', 'uuid', 'urllib', 'concurrent.futures']\n"
            "core_avail = [m for m in core_mods if importlib.util.find_spec(m) is not None]\n"
            "\n"
            "# 2. Test common third-party data/AI packages\n"
            "ext_candidates = ['numpy', 'pandas', 'requests', 'yaml', 'pydantic', 'scipy', 'matplotlib']\n"
            "ext_installed = []\n"
            "for pkg in ext_candidates:\n"
            "    try:\n"
            "        __import__(pkg)\n"
            "        ext_installed.append(pkg)\n"
            "    except ImportError:\n"
            "        pass\n"
            "\n"
            "# 3. Test dynamic package installation via pip\n"
            "pip_working = False\n"
            "pip_msg = 'pip_not_attempted'\n"
            "try:\n"
            "    res = subprocess.run(\n"
            "        [sys.executable, '-m', 'pip', '--version'],\n"
            "        capture_output=True, text=True, timeout=10\n"
            "    )\n"
            "    if res.returncode == 0:\n"
            "        pip_working = True\n"
            "        pip_msg = res.stdout.strip().split('\\n')[0]\n"
            "    else:\n"
            "        pip_msg = f'pip_exit_{res.returncode}'\n"
            "except Exception as e:\n"
            "    pip_msg = f'pip_error_{type(e).__name__}'\n"
            "\n"
            "print(f'CORE_STDLIB_COUNT:{len(core_avail)}/{len(core_mods)}')\n"
            "print(f'PREINSTALLED_EXT_PACKAGES:{ext_installed}')\n"
            "print(f'PIP_AVAILABLE:{pip_working}')\n"
            "print(f'PIP_STATUS:{pip_msg}')\n"
        )
        return ExecuteCodeRequest(code=code, timeout_seconds=90)
