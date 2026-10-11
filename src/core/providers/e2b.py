"""E2B Code Interpreter backend adapter."""
from __future__ import annotations

import asyncio
import logging
import os
import shutil
import hashlib
from .lifecycle import bounded_ttl, ownership
from pathlib import Path

from ..interface import ExecutionBackend
from ..models import (
    BackendCapabilities,
    PreparedExecution,
    RawExecutionResult,
    RetrievedArtifact,
)

logger = logging.getLogger(__name__)


class E2BBackend(ExecutionBackend):
    """Adapter for E2B Firecracker microVM sandboxes."""

    name = "e2b"
    supports_session_calls = True
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

    def __init__(self, api_key: str | None = None, *, template=None, allow_internet_access=True,
                 session_ttl_seconds=180) -> None:
        key = api_key or os.environ.get("E2B_API_KEY")
        if not key:
            cfg = Path.home() / ".e2b" / "config.json"
            if cfg.exists():
                try:
                    import json
                    data = json.loads(cfg.read_text())
                    key = data.get("projectApiKey")
                except Exception:
                    pass
        self.api_key = key
        self._sandbox = None
        self.benchmark_configuration = {"template": template, "allow_internet_access": allow_internet_access,
                                       "session_ttl_seconds": bounded_ttl(session_ttl_seconds), "cpu": None, "memory": None, "gpu": None}

    async def initialize(self) -> None:
        pass

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
            from e2b_code_interpreter import Sandbox
            from e2b.exceptions import TimeoutException

            if self._sandbox is None:
                self._sandbox = await asyncio.to_thread(Sandbox.create, api_key=self.api_key,
                    timeout=self.benchmark_configuration["session_ttl_seconds"], metadata=ownership(prepared.run_id),
                    template=self.benchmark_configuration["template"],
                    allow_internet_access=self.benchmark_configuration["allow_internet_access"])
            sb = self._sandbox
            for directory in (prepared.input_dir, prepared.work_dir, prepared.output_dir):
                await asyncio.to_thread(sb.files.make_dir, directory)

            # Stage inputs
            for inp in prepared.inputs:
                await asyncio.to_thread(sb.files.write, f"{prepared.input_dir}/{inp.relative_path}", inp.data)

            try:
                code = f"import os\nos.chdir({prepared.work_dir!r})\n" + prepared.request.code
                execution = await asyncio.to_thread(sb.run_code,
                    code,
                    envs={"INPUT_DIR": prepared.input_dir, "ARTIFACT_DIR": prepared.output_dir},
                    timeout=prepared.request.timeout_seconds,
                )
                stdout = "".join(execution.logs.stdout)
                stderr = "\n".join(execution.logs.stderr)
                exit_code = 0 if not execution.error else 1

                return RawExecutionResult(
                    stdout=stdout,
                    stderr=stderr or (execution.error.value if execution.error else ""),
                    exit_code=exit_code,
                    status="success" if exit_code == 0 else "failed",
                )
            except TimeoutException as te:
                return RawExecutionResult(
                    status="timed_out",
                    stderr=str(te),
                    warnings=["e2b_timeout"],
                )
        except Exception as exc:
            logger.warning("E2B execution failed or unauthenticated: %s", exc)
            return RawExecutionResult(
                status="failed",
                stderr=str(exc),
                warnings=[f"e2b_error: {type(exc).__name__}"],
            )

    async def collect_artifacts(
        self, prepared: PreparedExecution, result: RawExecutionResult
    ) -> list[RetrievedArtifact]:
        if self._sandbox is None:
            return []
        artifacts = []
        for entry in await asyncio.to_thread(self._sandbox.files.list, prepared.output_dir):
            content_bytes = bytes(await asyncio.to_thread(self._sandbox.files.read, entry.path, format="bytes"))
            artifacts.append(
                RetrievedArtifact(
                    relative_path=entry.name,
                    data=content_bytes,
                    size_bytes=len(content_bytes),
                    sha256=hashlib.sha256(content_bytes).hexdigest(),
                )
            )
        return artifacts

    async def cleanup(self, prepared: PreparedExecution) -> None:
        shutil.rmtree(prepared.root, ignore_errors=True)
        if self._sandbox is not None:
            await asyncio.to_thread(self._sandbox.kill)
            self._sandbox = None

    async def teardown(self) -> None:
        if self._sandbox is not None:
            await asyncio.to_thread(self._sandbox.kill)
            self._sandbox = None
