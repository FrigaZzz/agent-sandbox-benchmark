"""Modal session adapter with native binary staging and collection."""
from __future__ import annotations

import asyncio
import hashlib
from .lifecycle import bounded_ttl, ownership

from ..models import BackendCapabilities, PreparedExecution, RawExecutionResult, RetrievedArtifact


class ModalBackend:
    name = "modal"
    supports_session_calls = True
    capabilities = BackendCapabilities(persistent_filesystem=True)

    def __init__(self, app_name: str = "sandbox-benchmarks", *, cpu=2, memory=2048,
                 image=None, python_version=None, gpu=None, runtime=None, region=None, block_network=False,
                 session_ttl_seconds=180) -> None:
        self.app_name = app_name
        self._sandbox = None
        self.benchmark_configuration = {"cpu": cpu, "cpu_unit": "physical-core request", "memory": memory,
            "memory_unit": "MiB request", "image": image or "debian_slim", "python_version": python_version,
            "gpu": gpu, "runtime": runtime, "region": region, "block_network": block_network,
             "session_ttl_seconds": bounded_ttl(session_ttl_seconds)}

    async def initialize(self) -> None:
        import modal  # noqa: F401

    async def prepare(self, prepared: PreparedExecution) -> None:
        import modal
        if self._sandbox is None:
            app = await modal.App.lookup.aio(self.app_name, create_if_missing=True)
            c = self.benchmark_configuration
            image = modal.Image.from_registry(c["image"]) if c["image"] != "debian_slim" else modal.Image.debian_slim(python_version=c["python_version"])
            self._sandbox = await modal.Sandbox.create.aio(
                "sleep", "infinity", app=app, image=image,
                cpu=tuple(c["cpu"]) if isinstance(c["cpu"], list) else c["cpu"],
                memory=tuple(c["memory"]) if isinstance(c["memory"], list) else c["memory"],
                timeout=c["session_ttl_seconds"], tags=ownership(prepared.run_id),
                gpu=c["gpu"], runtime=c["runtime"], region=c["region"], block_network=c["block_network"],
            )
        fs = self._sandbox.filesystem
        for directory in (prepared.input_dir, prepared.work_dir, prepared.output_dir):
            await fs.make_directory.aio(directory)
        for inp in prepared.inputs:
            await fs.write_bytes.aio(inp.data, f"{prepared.input_dir}/{inp.relative_path}")

    async def execute(self, prepared: PreparedExecution) -> RawExecutionResult:
        args = ["python", "-c", prepared.request.code] if prepared.request.language == "python" else ["bash", "-c", prepared.request.code]
        proc = await self._sandbox.exec.aio(
            *args, workdir=prepared.work_dir,
            env={"INPUT_DIR": prepared.input_dir, "ARTIFACT_DIR": prepared.output_dir},
            timeout=prepared.request.timeout_seconds,
        )
        try:
            await asyncio.wait_for(proc.wait.aio(), prepared.request.timeout_seconds + 2)
            # modal 1.6 ContainerProcess.wait converts ExecTimeoutError to -1.
            # Unexpected status raises instead; returned -1 is the deadline sentinel.
            if proc.returncode == -1:
                await self._sandbox.terminate.aio()
                self._sandbox = None
                return RawExecutionResult(status="timed_out", exit_code=-1,
                    warnings=["Modal SDK wait returned its execution-deadline sentinel (-1); sandbox terminated."])
            stdout, stderr = await asyncio.gather(proc.stdout.read.aio(), proc.stderr.read.aio())
            return RawExecutionResult(stdout=stdout, stderr=stderr, exit_code=proc.returncode,
                                      status="success" if proc.returncode == 0 else "failed")
        except asyncio.TimeoutError:
            await self._sandbox.terminate.aio()
            self._sandbox = None
            return RawExecutionResult(status="timed_out")

    async def collect_artifacts(self, prepared, result):
        artifacts = []
        if self._sandbox is None:
            return artifacts
        fs = self._sandbox.filesystem
        for entry in await fs.list_files.aio(prepared.output_dir):
            data = await fs.read_bytes.aio(f"{prepared.output_dir}/{entry.name}")
            artifacts.append(RetrievedArtifact(relative_path=entry.name, size_bytes=len(data),
                           sha256=hashlib.sha256(data).hexdigest(), data=data))
        return artifacts

    async def cleanup(self, prepared) -> None:
        await self.teardown()

    async def teardown(self) -> None:
        if self._sandbox is not None:
            await self._sandbox.terminate.aio()
            self._sandbox = None
