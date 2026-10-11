"""Databricks Serverless Sandboxes (Dedicated MicroVM) execution backend adapter."""
from __future__ import annotations

import asyncio
import base64
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


class DatabricksServerlessSandboxBackend(ExecutionBackend):
    """Adapter for Databricks Serverless Sandboxes (Dedicated MicroVM: 4 vCPU / 8 GB RAM).

    Documented in: https://docs.databricks.com/aws/en/compute/serverless/sandbox
    Requires 'Databricks Sandboxes' preview toggle enabled in Workspace Settings -> Previews.
    """

    name = "databricks_sandbox"
    capabilities = BackendCapabilities(
        native_input_files=True,
        native_output_files=True,
        persistent_filesystem=True,
        shell_execution=True,
        supports_multiple_files=True,
        supports_direct_binary_transfer=True,
        has_internet_access=True,
        has_custom_packages=True,
        model_managed=False,
        cmek_supported=False,
    )

    def __init__(self, profile: str | None = None, sandbox_prefix: str = "agent-bench") -> None:
        self.profile = profile or os.environ.get("DATABRICKS_CONFIG_PROFILE")
        self.sandbox_prefix = sandbox_prefix
        self._client = None
        self._sandbox_name = None

    async def initialize(self) -> None:
        try:
            from databricks.sdk import WorkspaceClient

            self._client = WorkspaceClient(profile=self.profile) if self.profile else WorkspaceClient()
        except Exception as exc:
            logger.warning("Could not initialize Databricks WorkspaceClient: %s", exc)

    async def prepare(self, prepared: PreparedExecution) -> None:
        for d in (prepared.input_dir, prepared.work_dir, prepared.output_dir):
            os.makedirs(d, exist_ok=True)

        for inp in prepared.inputs:
            target = Path(prepared.input_dir) / inp.relative_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(inp.data)

        script_path = Path(prepared.work_dir) / "main.py"
        script_path.write_text(prepared.request.code)

    async def execute(self, prepared: PreparedExecution) -> RawExecutionResult:
        try:
            from databricks.sdk.service.sandbox import Sandbox, Duration

            if self._client is None:
                await self.initialize()

            loop = asyncio.get_event_loop()

            # 1. Provision microVM sandbox
            sandbox_id = f"{self.sandbox_prefix}-{prepared.run_id}"

            def _create_sb():
                return self._client.sandbox.create_sandbox(
                    sandbox=Sandbox(),
                    sandbox_id=sandbox_id,
                )

            created = await loop.run_in_executor(None, _create_sb)
            self._sandbox_name = created.name

            # 2. Base64 encode script payload for shell safe execution
            encoded_code = base64.b64encode(prepared.request.code.encode("utf-8")).decode("utf-8")

            # 3. Stage input files if present
            stage_cmd = "mkdir -p /tmp/input && "
            for inp in prepared.inputs:
                inp_b64 = base64.b64encode(inp.data).decode("utf-8")
                stage_cmd += f"echo '{inp_b64}' | base64 --decode > /tmp/input/{inp.relative_path} && "

            full_script = (
                f"{stage_cmd}echo '{encoded_code}' | base64 --decode > /tmp/task.py && python3 /tmp/task.py"
            )

            # 4. Execute command in sandbox microVM
            def _exec_command():
                return self._client.sandbox.execute_command_sync(
                    name=self._sandbox_name,
                    cmd="/bin/bash",
                    args=["-c", full_script],
                    execution_timeout=Duration(seconds=prepared.request.timeout_seconds),
                )

            response = await loop.run_in_executor(None, _exec_command)

            stdout = response.stdout or ""
            stderr = response.stderr or ""
            exit_code = getattr(response, "exit_code", 0)

            return RawExecutionResult(
                stdout=stdout,
                stderr=stderr,
                exit_code=exit_code,
                status="success" if exit_code == 0 else "failed",
            )

        except Exception as exc:
            err_msg = str(exc)
            logger.warning("Databricks Serverless Sandbox error: %s", exc)
            return RawExecutionResult(
                status="failed",
                stderr=err_msg,
                warnings=[
                    f"databricks_sandbox_error: {type(exc).__name__}",
                    "Note: Ensure 'Databricks Sandboxes' preview is enabled in Workspace Settings -> Previews.",
                ],
            )

    async def collect_artifacts(
        self, prepared: PreparedExecution, result: RawExecutionResult
    ) -> list[RetrievedArtifact]:
        return []

    async def cleanup(self, prepared: PreparedExecution) -> None:
        shutil.rmtree(prepared.root, ignore_errors=True)
        if self._sandbox_name and self._client:
            try:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    None, lambda: self._client.sandbox.delete_sandbox(name=self._sandbox_name)
                )
            except Exception:
                raise
            self._sandbox_name = None

    async def teardown(self) -> None:
        if self._sandbox_name and self._client:
            await asyncio.to_thread(self._client.sandbox.delete_sandbox, name=self._sandbox_name)
            self._sandbox_name = None
