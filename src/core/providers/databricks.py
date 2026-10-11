"""Databricks Unity Catalog MCP Python execution backend adapter."""
from __future__ import annotations

import asyncio
import json
import logging
import os
import shutil
from pathlib import Path

from ..interface import ExecutionBackend
from ..models import (
    BackendCapabilities,
    PreparedExecution,
    RawExecutionResult,
    RetrievedArtifact,
)

logger = logging.getLogger(__name__)


class DatabricksBackend(ExecutionBackend):
    """Adapter for Databricks Unity Catalog MCP Python execution."""

    name = "databricks"
    capabilities = BackendCapabilities(
        native_input_files=False,
        native_output_files=False,
        persistent_filesystem=False,
        shell_execution=False,
        supports_multiple_files=False,
        supports_direct_binary_transfer=False,
        has_internet_access=False,
        has_custom_packages=False,
        model_managed=False,
        cmek_supported=False,
    )

    def __init__(self, profile: str | None = None, warehouse_id: str | None = None) -> None:
        self.profile = profile or os.environ.get("DATABRICKS_CONFIG_PROFILE")
        self.warehouse_id = warehouse_id or os.environ.get("DATABRICKS_WAREHOUSE_ID")
        self._client = None

    async def initialize(self) -> None:
        try:
            from databricks.sdk import WorkspaceClient

            self._client = WorkspaceClient(profile=self.profile) if self.profile else WorkspaceClient()
            if not self.warehouse_id:
                whs = list(self._client.warehouses.list())
                if whs:
                    self.warehouse_id = whs[0].id
        except Exception as exc:
            logger.warning("Could not initialize Databricks WorkspaceClient: %s", exc)

    async def prepare(self, prepared: PreparedExecution) -> None:
        pass

    async def execute(self, prepared: PreparedExecution) -> RawExecutionResult:
        try:
            from databricks.sdk import WorkspaceClient
            from databricks.sdk.service.sql import StatementParameterListItem, StatementState

            if self._client is None:
                await self.initialize()
            if self._client is None or not self.warehouse_id:
                return RawExecutionResult(
                    status="failed",
                    stderr="Databricks client not initialized or no SQL warehouse found.",
                )

            # Prepend any input files if present as fallback
            code_to_run = prepared.request.code
            if prepared.inputs:
                input_map = {inp.relative_path: inp.data.decode("utf-8", errors="ignore") for inp in prepared.inputs}
                prefix = f"INPUT_FILES = {repr(input_map)}\n"
                code_to_run = prefix + code_to_run

            timeout_s = prepared.request.timeout_seconds
            wait_timeout_str = f"{min(max(timeout_s, 5), 50)}s"

            # Execute statement asynchronously in event loop thread
            def _run_statement():
                return self._client.statement_execution.execute_statement(
                    warehouse_id=self.warehouse_id,
                    statement="SELECT system.ai.python_exec(:code)",
                    parameters=[StatementParameterListItem(name="code", value=code_to_run, type="STRING")],
                    wait_timeout=wait_timeout_str,
                )

            loop = asyncio.get_event_loop()
            res = await loop.run_in_executor(None, _run_statement)

            state = res.status.state
            stmt_id = res.statement_id

            # If still pending / running beyond expected timeout, cancel it
            if state in (StatementState.PENDING, StatementState.RUNNING):
                if timeout_s <= 5:
                    await loop.run_in_executor(None, lambda: self._client.statement_execution.cancel_execution(stmt_id))
                    return RawExecutionResult(
                        status="timed_out",
                        stderr="Databricks execution cancelled after timeout threshold.",
                        warnings=["databricks_timeout"],
                    )

            if state == StatementState.SUCCEEDED:
                stdout = ""
                if res.result and res.result.data_array and res.result.data_array[0]:
                    stdout = res.result.data_array[0][0] or ""
                return RawExecutionResult(
                    status="success",
                    stdout=stdout,
                    exit_code=0,
                )
            elif state in (StatementState.CANCELED, StatementState.CLOSED):
                return RawExecutionResult(
                    status="timed_out",
                    stderr="Databricks statement execution was cancelled.",
                    warnings=["databricks_cancelled"],
                )
            else:
                err_msg = ""
                if hasattr(res.status, "error") and res.status.error:
                    err_msg = res.status.error.message or ""
                return RawExecutionResult(
                    status="failed",
                    stderr=err_msg or f"Statement execution status: {state}",
                    exit_code=1,
                )

        except Exception as exc:
            logger.warning("Databricks execution error: %s", exc)
            return RawExecutionResult(
                status="failed",
                stderr=str(exc),
                warnings=[f"databricks_error: {type(exc).__name__}"],
            )

    async def collect_artifacts(
        self, prepared: PreparedExecution, result: RawExecutionResult
    ) -> list[RetrievedArtifact]:
        return []

    async def cleanup(self, prepared: PreparedExecution) -> None:
        pass

    async def teardown(self) -> None:
        pass
