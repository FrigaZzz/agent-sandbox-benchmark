"""Blaxel Sandbox backend adapter."""
from __future__ import annotations

import asyncio
import logging
import os
import shutil
from pathlib import Path
from .lifecycle import ttl_seconds, ownership

from ..interface import ExecutionBackend
from ..models import (
    BackendCapabilities,
    PreparedExecution,
    RawExecutionResult,
    RetrievedArtifact,
)

logger = logging.getLogger(__name__)


class BlaxelBackend(ExecutionBackend):
    """Adapter for Blaxel Linux container sandboxes."""

    name = "blaxel"
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

    def __init__(self, sandbox_name: str = "adk-bench-sandbox", *, image="blaxel/py-app:latest", memory=4096, region="us-pdx-1", ttl="180s") -> None:
        ttl_seconds(ttl)
        self.sandbox_name = sandbox_name
        self._sandbox = None
        self.benchmark_configuration = {"image": image, "memory": memory, "memory_unit": "MB API field",
            "cpu": "memory-coupled", "region": region, "ttl": ttl, "gpu": None,
            "network_policy": "default; no restriction requested"}

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
            from blaxel.core import SandboxInstance

            sb = await SandboxInstance.create_if_not_exists({
                "name": f"{self.sandbox_name}-{prepared.run_id}",
                "image": self.benchmark_configuration["image"],
                "memory": self.benchmark_configuration["memory"],
                "region": self.benchmark_configuration["region"],
                "ttl": self.benchmark_configuration["ttl"],
                "labels": ownership(prepared.run_id),
            })
            self._sandbox = sb

            # Stage input files into the sandbox filesystem
            for inp in prepared.inputs:
                try:
                    await sb.fs.write(f"/tmp/{inp.relative_path}", inp.data.decode("utf-8", errors="ignore"))
                except Exception as fe:
                    logger.warning("Could not stage input file %s: %s", inp.relative_path, fe)

            exec_name = f"bench-{prepared.run_id}"
            script_remote = f"/tmp/{exec_name}.py"
            await sb.fs.write(script_remote, prepared.request.code)

            timeout_s = max(prepared.request.timeout_seconds, 1)
            await sb.process.exec({
                "name": exec_name,
                "command": f"python {script_remote}",
                "working_dir": "/tmp",
                "wait_for_completion": False,
                "timeout": timeout_s,
            })

            try:
                proc = await sb.process.wait(exec_name, max_wait=timeout_s * 1000)
                output = proc.logs or (proc.stdout + proc.stderr)
                return RawExecutionResult(
                    stdout=output,
                    exit_code=proc.exit_code,
                    status="success" if proc.exit_code == 0 else "failed",
                )
            except TimeoutError as te:
                return RawExecutionResult(
                    status="timed_out",
                    stderr=str(te),
                    warnings=["blaxel_timeout"],
                )
        except Exception as exc:
            logger.warning("Blaxel execution failed or unauthenticated: %s", exc)
            return RawExecutionResult(
                status="failed",
                stderr=str(exc),
                warnings=[f"blaxel_error: {type(exc).__name__}"],
            )

    async def collect_artifacts(
        self, prepared: PreparedExecution, result: RawExecutionResult
    ) -> list[RetrievedArtifact]:
        if self._sandbox is None:
            return []
        import hashlib
        artifacts = []
        target_file = "/tmp/transformed_output.txt"
        try:
            content_str = await self._sandbox.fs.read(target_file)
            content_bytes = content_str.encode("utf-8")
            artifacts.append(
                RetrievedArtifact(
                    relative_path="transformed_output.txt",
                    data=content_bytes,
                    size_bytes=len(content_bytes),
                    sha256=hashlib.sha256(content_bytes).hexdigest(),
                )
            )
        except Exception:
            pass
        return artifacts

    async def cleanup(self, prepared: PreparedExecution) -> None:
        shutil.rmtree(prepared.root, ignore_errors=True)
        await self.teardown()

    async def teardown(self) -> None:
        if self._sandbox is not None:
            await self._sandbox.delete()
        self._sandbox = None
