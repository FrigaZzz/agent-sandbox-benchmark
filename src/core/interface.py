"""Agnostic sandbox execution backend interface protocol."""
from __future__ import annotations

from typing import Protocol, runtime_checkable
from .models import (
    BackendCapabilities,
    PreparedExecution,
    RawExecutionResult,
    RetrievedArtifact,
)


@runtime_checkable
class ExecutionBackend(Protocol):
    """Protocol for pluggable sandbox execution providers."""

    name: str
    capabilities: BackendCapabilities

    async def initialize(self) -> None:
        """Initialize provider client and verify credentials/prerequisites."""
        ...

    async def prepare(self, prepared: PreparedExecution) -> None:
        """Stage input files, generate wrapper scripts, and ensure runtime is active."""
        ...

    async def execute(self, prepared: PreparedExecution) -> RawExecutionResult:
        """Execute user code inside the isolated sandbox."""
        ...

    async def collect_artifacts(
        self, prepared: PreparedExecution, result: RawExecutionResult
    ) -> list[RetrievedArtifact]:
        """Retrieve output files created in the sandbox's ARTIFACT_DIR."""
        ...

    async def cleanup(self, prepared: PreparedExecution) -> None:
        """Clean up per-execution files or temporary directories."""
        ...

    async def teardown(self) -> None:
        """Terminate the underlying sandbox container/instance to stop billing."""
        ...
