"""Disk I/O throughput benchmark: tests local filesystem write and read speeds."""
from __future__ import annotations

from ...core.models import ExecuteCodeRequest


class DiskIoBenchmark:
    name = "disk_io"
    description = "Tests filesystem throughput: 100 small files and 1 large 25MB file with SHA-256 verification."

    @staticmethod
    def get_request() -> ExecuteCodeRequest:
        code = (
            "import os, time, hashlib\n"
            "work_dir = '.' if os.access('.', os.W_OK) else '/tmp'\n"
            "t0 = time.perf_counter()\n"
            "for i in range(100):\n"
            "    with open(os.path.join(work_dir, f'test_small_{i}.txt'), 'w') as f:\n"
            "        f.write(f'file content {i}\\n' * 50)\n"
            "t_small_write = time.perf_counter() - t0\n"
            "\n"
            "large_data = b'ABCDEF0123456789' * (1024 * 1024 * 2)  # 32 MB\n"
            "h_orig = hashlib.sha256(large_data).hexdigest()\n"
            "large_path = os.path.join(work_dir, 'test_large.bin')\n"
            "t1 = time.perf_counter()\n"
            "with open(large_path, 'wb') as f:\n"
            "    f.write(large_data)\n"
            "t_large_write = time.perf_counter() - t1\n"
            "\n"
            "t2 = time.perf_counter()\n"
            "with open(large_path, 'rb') as f:\n"
            "    read_back = f.read()\n"
            "t_large_read = time.perf_counter() - t2\n"
            "h_read = hashlib.sha256(read_back).hexdigest()\n"
            "\n"
            "print(f'SMALL_FILES_WRITE_SEC:{t_small_write:.4f}')\n"
            "print(f'LARGE_FILE_WRITE_SEC:{t_large_write:.4f}')\n"
            "print(f'LARGE_FILE_READ_SEC:{t_large_read:.4f}')\n"
            "print(f'INTEGRITY_MATCH:{h_orig == h_read}')\n"
        )
        return ExecuteCodeRequest(code=code, timeout_seconds=90)
