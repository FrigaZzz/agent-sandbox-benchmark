"""Safe runtime fingerprint: no credentials, environment dump, hostname or network calls."""
import importlib.metadata
import json
import os
import pathlib
import platform
import shutil
import subprocess
import sys


def read_limit(path):
    try:
        return pathlib.Path(path).read_text().strip()
    except (OSError, ValueError):
        return None


def inventory():
    cgroup = {key: read_limit(path) for key, path in {
        'cpu_max': '/sys/fs/cgroup/cpu.max',
        'memory_max': '/sys/fs/cgroup/memory.max',
        'cpuset_effective': '/sys/fs/cgroup/cpuset.cpus.effective',
        'memory_limit_v1': '/sys/fs/cgroup/memory/memory.limit_in_bytes',
        'cpu_quota_v1': '/sys/fs/cgroup/cpu/cpu.cfs_quota_us',
        'cpu_period_v1': '/sys/fs/cgroup/cpu/cpu.cfs_period_us',
    }.items()}
    memory_bytes = None
    try:
        memory_bytes = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')
    except (ValueError, OSError, AttributeError):
        pass
    cpu_model = None
    cpuinfo = read_limit('/proc/cpuinfo')
    if cpuinfo:
        cpu_model = next((line.split(':', 1)[1].strip() for line in cpuinfo.splitlines()
                          if line.startswith('model name') and ':' in line), None)
    versions = {}
    for package in ['pip', 'numpy', 'pandas', 'scipy', 'matplotlib', 'torch', 'requests']:
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = None
    gpu = {'probe': 'nvidia-smi_unavailable', 'devices': []}
    if shutil.which('nvidia-smi'):
        try:
            p = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total', '--format=csv,noheader'],
                               capture_output=True, text=True, timeout=5)
            gpu = {'probe': 'nvidia-smi', 'exit_code': p.returncode, 'devices': p.stdout.splitlines()[:16]}
        except Exception as exc:
            gpu = {'probe': 'error', 'type': type(exc).__name__, 'devices': []}
    usage = shutil.disk_usage('.')
    return {
        'inventory_schema_version': 1,
        'runtime': {'python': platform.python_version(), 'implementation': platform.python_implementation(),
                    'os': platform.system(), 'kernel': platform.release(), 'architecture': platform.machine()},
        'cpu': {'visible_logical_cpus': os.cpu_count(), 'model': cpu_model,
                'affinity_count': len(os.sched_getaffinity(0)) if hasattr(os, 'sched_getaffinity') else None},
        'memory': {'sysconf_physical_bytes': memory_bytes},
        'cgroup': cgroup,
        'disk': {'filesystem_total_bytes': usage.total, 'filesystem_free_bytes': usage.free},
        'gpu': gpu,
        'packages': versions,
        'tools': {tool: shutil.which(tool) is not None for tool in ['bash', 'git', 'node', 'gcc', 'pip', 'nvidia-smi']},
        'identity': {'uid': os.getuid() if hasattr(os, 'getuid') else None},
        'limitations': 'Visible CPUs, physical memory and filesystem capacity can be shared host values. cgroup files can be hidden or report shared limits. This probe cannot attest reserved resources, image digest, cloud network policy, GPU eligibility, or isolation technology.',
    }


print('BENCH_RESULT:' + json.dumps(inventory(), sort_keys=True))
