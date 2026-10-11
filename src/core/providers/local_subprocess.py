"""Baseline control backend: runs in an isolated local subprocess for benchmark normalization."""
from __future__ import annotations

import asyncio
import os
import shutil
import signal
import sys
import subprocess
from pathlib import Path

from ..interface import ExecutionBackend
from ..models import (
    BackendCapabilities,
    PreparedExecution,
    RawExecutionResult,
    RetrievedArtifact,
)


class LocalSubprocessBackend(ExecutionBackend):
    """Local baseline executor to normalize cross-provider metrics against host hardware."""

    name = "local_baseline"
    supports_session_calls = True
    capabilities = BackendCapabilities(
        native_input_files=True,
        native_output_files=True,
        persistent_filesystem=False,
        shell_execution=True,
        supports_multiple_files=True,
        supports_direct_binary_transfer=True,
        has_internet_access=True,
        has_custom_packages=True,
        model_managed=False,
        cmek_supported=False,
    )

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
        script_path = Path(prepared.work_dir) / "main.py"
        env = os.environ.copy()
        env["INPUT_DIR"] = prepared.input_dir
        env["ARTIFACT_DIR"] = prepared.output_dir

        cmd = [sys.executable, str(script_path)] if prepared.request.language == "python" else ["bash", str(script_path)]

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=prepared.work_dir,
            env=env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            start_new_session=True,
        )

        try:
            stdout_b, stderr_b = await asyncio.wait_for(
                proc.communicate(), timeout=prepared.request.timeout_seconds
            )
            stdout = stdout_b.decode(errors="replace")
            stderr = stderr_b.decode(errors="replace")
            status = "success" if proc.returncode == 0 else "failed"
            return RawExecutionResult(
                stdout=stdout,
                stderr=stderr,
                exit_code=proc.returncode,
                status=status,
            )
        except (asyncio.TimeoutError, asyncio.CancelledError) as exc:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            await proc.wait()
            if isinstance(exc, asyncio.CancelledError):
                raise
            return RawExecutionResult(
                status="timed_out",
                warnings=["Process exceeded timeout limit"],
            )

    async def collect_artifacts(
        self, prepared: PreparedExecution, result: RawExecutionResult
    ) -> list[RetrievedArtifact]:
        out_dir = Path(prepared.output_dir)
        artifacts: list[RetrievedArtifact] = []
        if not out_dir.exists():
            return artifacts

        for f in out_dir.rglob("*"):
            if f.is_file():
                rel = str(f.relative_to(out_dir))
                data = f.read_bytes()
                import hashlib
                artifacts.append(
                    RetrievedArtifact(
                        relative_path=rel,
                        size_bytes=len(data),
                        sha256=hashlib.sha256(data).hexdigest(),
                        data=data,
                    )
                )
        return artifacts

    async def cleanup(self, prepared: PreparedExecution) -> None:
        shutil.rmtree(prepared.root, ignore_errors=True)

    async def teardown(self) -> None:
        pass
