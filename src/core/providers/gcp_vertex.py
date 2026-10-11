"""GCP Agent Platform Sandbox backend adapter (CMEK-protected Vertex AI Agent Engine)."""
from __future__ import annotations

import asyncio
import json
import logging
import os
import shutil
import tempfile
from pathlib import Path

from ..interface import ExecutionBackend
from ..models import (
    BackendCapabilities,
    PreparedExecution,
    RawExecutionResult,
    RetrievedArtifact,
)

logger = logging.getLogger(__name__)


class GcpVertexBackend(ExecutionBackend):
    """Adapter for Google Cloud Agent Platform Sandboxes (CMEK)."""

    name = "gcp_vertex"
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
        cmek_supported=True,
    )

    def __init__(self, cli_bin: str = "agent-sandbox") -> None:
        self.cli_bin = cli_bin
        self.sandbox_id: str | None = None

    async def initialize(self) -> None:
        """Verify gcloud and agent-sandbox CLI availability."""
        proc = await asyncio.create_subprocess_exec(
            self.cli_bin, "--version",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await proc.communicate()

    async def prepare(self, prepared: PreparedExecution) -> None:
        # 1. Write the code into a local temp file
        for d in (prepared.input_dir, prepared.work_dir, prepared.output_dir):
            os.makedirs(d, exist_ok=True)

        for inp in prepared.inputs:
            target = Path(prepared.input_dir) / inp.relative_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(inp.data)

        script_path = Path(prepared.work_dir) / "main.py"
        script_path.write_text(
            "import os, pathlib\n"
            "pathlib.Path('input').mkdir(exist_ok=True)\n"
            "pathlib.Path('output').mkdir(exist_ok=True)\n"
            "os.environ['INPUT_DIR'] = str(pathlib.Path('input').resolve())\n"
            "os.environ['ARTIFACT_DIR'] = str(pathlib.Path('output').resolve())\n"
            + prepared.request.code
        )

    async def execute(self, prepared: PreparedExecution) -> RawExecutionResult:
        script_path = Path(prepared.work_dir) / "main.py"

        # Using agent-sandbox run --file ... --output-dir ...
        cmd = [
            self.cli_bin,
            "run",
            "--file", str(script_path),
            "--format", "json",
            "--ttl", str(min(prepared.request.timeout_seconds + 30, 900)),
            "--max-output-chars", "0",
            "--out", prepared.output_dir,
        ]

        # Stage input files if any
        for inp in prepared.inputs:
            inp_local = Path(prepared.input_dir) / inp.relative_path
            cmd.extend(["--upload", f"{inp_local}:input/{inp.relative_path}"])

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            try:
                stdout_b, stderr_b = await asyncio.wait_for(
                    proc.communicate(), timeout=prepared.request.timeout_seconds + 60
                )
            except (asyncio.TimeoutError, asyncio.CancelledError):
                proc.terminate()  # CLI SIGTERM handler deletes its owned sandbox.
                await proc.communicate()
                raise

            stdout_str = stdout_b.decode(errors="replace")
            stderr_str = stderr_b.decode(errors="replace")

            # Try parsing JSON result from agent-sandbox
            try:
                data = json.loads(stdout_str)
                exit_code = data.get("exit_status", data.get("exit_code", proc.returncode))
                is_ok = data.get("ok", exit_code == 0)
                return RawExecutionResult(
                    stdout=data.get("stdout", stdout_str),
                    stderr=data.get("stderr", stderr_str),
                    exit_code=exit_code,
                    status="success" if (is_ok and exit_code == 0) else "failed",
                )
            except Exception:
                return RawExecutionResult(
                    stdout=stdout_str,
                    stderr=stderr_str,
                    exit_code=proc.returncode,
                    status="success" if proc.returncode == 0 else "failed",
                )

        except asyncio.TimeoutError:
            return RawExecutionResult(
                status="timed_out",
                warnings=["GCP Sandbox execution timed out."],
            )

    async def collect_artifacts(
        self, prepared: PreparedExecution, result: RawExecutionResult
    ) -> list[RetrievedArtifact]:
        out_dir = Path(prepared.output_dir) / "output"
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
