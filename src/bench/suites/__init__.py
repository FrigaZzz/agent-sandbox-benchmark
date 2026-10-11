"""Standardized benchmark test suites for sandbox systems."""
from .cold_start import ColdStartBenchmark
from .cpu_stress import CpuStressBenchmark
from .mem_stress import MemoryStressBenchmark
from .disk_io import DiskIoBenchmark
from .net_isolation import NetworkIsolationBenchmark
from .env_security import EnvSecurityBenchmark
from .timeout_handling import TimeoutHandlingBenchmark
from .artifact_roundtrip import ArtifactRoundtripBenchmark
from .agent_multiturn import AgentMultiturnBenchmark
from .parallel_throughput import ParallelThroughputBenchmark
from .package_ecosystem import PackageEcosystemBenchmark
from .workflows import (DataPipelineBenchmark, SQLiteAnalyticsBenchmark, RepositoryTaskBenchmark,
                        OutputFidelityBenchmark, CrossCallStateBenchmark, ErrorRecoveryBenchmark,
                        DependencyInstallBenchmark)
from .runtime_inventory import RuntimeInventoryBenchmark

ALL_BENCHMARKS = [
    ColdStartBenchmark,
    CpuStressBenchmark,
    MemoryStressBenchmark,
    DiskIoBenchmark,
    NetworkIsolationBenchmark,
    EnvSecurityBenchmark,
    TimeoutHandlingBenchmark,
    ArtifactRoundtripBenchmark,
    AgentMultiturnBenchmark,
    ParallelThroughputBenchmark,
    PackageEcosystemBenchmark,
    DataPipelineBenchmark,
    SQLiteAnalyticsBenchmark,
    RepositoryTaskBenchmark,
    OutputFidelityBenchmark,
    CrossCallStateBenchmark,
    ErrorRecoveryBenchmark,
    DependencyInstallBenchmark,
    RuntimeInventoryBenchmark,
]

REALISTIC_BENCHMARKS = [ColdStartBenchmark, CpuStressBenchmark, ArtifactRoundtripBenchmark,
                      DataPipelineBenchmark, SQLiteAnalyticsBenchmark, RepositoryTaskBenchmark,
                      OutputFidelityBenchmark, CrossCallStateBenchmark, ErrorRecoveryBenchmark,
                      DependencyInstallBenchmark, TimeoutHandlingBenchmark]
