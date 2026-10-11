"""Unified data models for requests, capabilities, telemetry, timings, and cost attribution."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field


class InputFileRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    artifact_name: str = Field(min_length=1, max_length=512, description="Artifact or file reference name.")
    target_name: str | None = Field(default=None, description="Relative destination path inside sandbox.")
    data: bytes | None = Field(default=None, description="Direct binary data if supplied inline.")
    text: str | None = Field(default=None, description="Text data if supplied inline.")


class ExecuteCodeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    code: str = Field(min_length=1, description="Python or bash code to execute.")
    input_files: list[InputFileRef] = Field(default_factory=list)
    include_generated_artifacts: bool = Field(default=False)
    timeout_seconds: int = Field(default=120, ge=1, le=600)
    language: Literal["python", "bash"] = "python"


@dataclass(frozen=True)
class BackendCapabilities:
    native_input_files: bool = True
    native_output_files: bool = True
    persistent_filesystem: bool = True
    shell_execution: bool = True
    supports_multiple_files: bool = True
    supports_direct_binary_transfer: bool = True
    has_internet_access: bool = True
    has_custom_packages: bool = True
    model_managed: bool = False
    cmek_supported: bool = False


@dataclass(frozen=True)
class ResolvedInputFile:
    artifact_name: str
    relative_path: str
    data: bytes
    mime_type: str = "application/octet-stream"


@dataclass
class RetrievedArtifact:
    relative_path: str
    size_bytes: int
    sha256: str | None = None
    data: bytes | None = None
    error: str | None = None


@dataclass
class PreparedExecution:
    run_id: str
    nonce: str
    root: str
    request: ExecuteCodeRequest
    inputs: list[ResolvedInputFile]
    script: str = ""

    @property
    def input_dir(self) -> str:
        return f"{self.root}/input"

    @property
    def work_dir(self) -> str:
        return f"{self.root}/work"

    @property
    def output_dir(self) -> str:
        return f"{self.root}/output"


@dataclass
class RawExecutionResult:
    stdout: str = ""
    stderr: str = ""
    exit_code: int | None = None
    status: Literal["success", "failed", "timed_out", "oom", "unknown"] = "failed"
    artifacts: list[RetrievedArtifact] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    manifest: dict[str, Any] | None = None


class ExecutionTiming(BaseModel):
    initialize_ms: float = 0.0
    cold_start_ms: float = 0.0
    prepare_ms: float = 0.0
    execute_ms: float = 0.0
    collect_ms: float = 0.0
    cleanup_ms: float = 0.0
    total_wall_clock_ms: float = 0.0


class ResourceUsage(BaseModel):
    cpu_time_user_s: float | None = None
    cpu_time_system_s: float | None = None
    max_memory_mb: float | None = None
    disk_written_bytes: int | None = None


class CostEstimate(BaseModel):
    compute_cost_usd: float = 0.0
    token_cost_usd: float = 0.0
    session_fee_usd: float = 0.0
    total_cost_usd: float = 0.0
    billing_unit: str = "per-second"
    details: dict[str, Any] = Field(default_factory=dict)


class GeneratedArtifact(BaseModel):
    artifact_id: str
    filename: str
    relative_path: str
    mime_type: str = "application/octet-stream"
    size_bytes: int
    sha256: str | None = None
    status: Literal["saved", "omitted", "failed"] = "omitted"
    error: str | None = None


class BenchmarkExecutionResult(BaseModel):
    run_id: str
    suite: str = ""
    provider: str
    status: Literal["success", "failed", "timed_out", "oom", "unknown"] = "failed"
    preparation: str = "pending"
    execution: str = "pending"
    collection: str = "not_requested"
    persistence: str = "not_requested"
    cleanup: str = "pending"
    stdout: str = ""
    stderr: str = ""
    exit_code: int | None = None
    artifacts: list[GeneratedArtifact] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    error: str | None = None
    timings: ExecutionTiming = Field(default_factory=ExecutionTiming)
    resources: ResourceUsage = Field(default_factory=ResourceUsage)
    cost: CostEstimate = Field(default_factory=CostEstimate)
    schema_version: int = 2
    started_at: str | None = None
    workload_sha256: str = ""
    evaluation_contract_sha256: str = ""
    evaluation: Literal["pass", "fail", "unknown", "skipped"] = "unknown"
    checks: dict[str, bool] = Field(default_factory=dict)
    metrics: dict[str, Any] = Field(default_factory=dict)
    provenance: dict[str, Any] = Field(default_factory=dict)
    steps: list[dict[str, Any]] = Field(default_factory=list)
    teardown: str = "pending"
