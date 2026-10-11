"""Environment security & privileges benchmark: probes UID/GID, sudo, and virtualization environment."""
from __future__ import annotations

from ...core.models import ExecuteCodeRequest


class EnvSecurityBenchmark:
    name = "env_security"
    description = "Probes sandbox isolation: user UID/GID, root privileges, sudo access, container cgroups."

    @staticmethod
    def get_request() -> ExecuteCodeRequest:
        code = (
            "import os, subprocess, platform\n"
            "uid = os.getuid() if hasattr(os, 'getuid') else -1\n"
            "gid = os.getgid() if hasattr(os, 'getgid') else -1\n"
            "print(f'USER_ID:{uid}:{gid}')\n"
            "print(f'IS_ROOT:{uid == 0}')\n"
            "print(f'OS_SYSTEM:{platform.system()}:{platform.machine()}')\n"
            "\n"
            "# Check container / virtualization clues\n"
            "is_container = os.path.exists('/.dockerenv') or os.path.exists('/run/.containerenv')\n"
            "print(f'CONTAINER_FLAG:{is_container}')\n"
            "\n"
            "# Check sudo if available\n"
            "try:\n"
            "    res = subprocess.run(['sudo', '-n', 'true'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=2)\n"
            "    print(f'PASSWORDLESS_SUDO:{res.returncode == 0}')\n"
            "except Exception:\n"
            "    print('PASSWORDLESS_SUDO:FALSE_OR_UNAVAILABLE')\n"
        )
        return ExecuteCodeRequest(code=code, timeout_seconds=30)
