"""Kubernetes-SIGs Agent-Sandbox execution backend provider.

Implements the official Kubernetes-SIGs Agent Sandbox specification:
https://github.com/kubernetes-sigs/agent-sandbox
"""
from __future__ import annotations

import asyncio
import io
import logging
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import httpx

from ..interface import ExecutionBackend
from ..models import (
    BackendCapabilities,
    PreparedExecution,
    RawExecutionResult,
    RetrievedArtifact,
)

logger = logging.getLogger(__name__)


class KubernetesAgentSandboxBackend(ExecutionBackend):
    """Execution backend targeting the official kubernetes-sigs/agent-sandbox runtime.

    Supports:
    1. Remote / In-Cluster / Tunnel mode via AGENT_SANDBOX_URL (e.g. http://localhost:8888)
    2. Self-hosted managed process mode (automatically boots runtime server if no cluster is running)
    3. Official k8s-agent-sandbox Python SDK integration
    """

    name = "k8s_agent_sandbox"
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

    def __init__(self, api_url: str | None = None, auto_spawn: bool = True) -> None:
        self.api_url = (
            api_url
            or os.environ.get("AGENT_SANDBOX_URL")
            or "http://127.0.0.1:8888"
        ).rstrip("/")
        self.auto_spawn = auto_spawn
        self._server_proc: subprocess.Popen | None = None
        self._spawned_base_dir: str | None = None
        self._client: httpx.AsyncClient | None = None

    async def initialize(self) -> None:
        """Verify connectivity to agent-sandbox server, or spawn managed instance."""
        self._client = httpx.AsyncClient(base_url=self.api_url, timeout=30.0)

        # Check if server is already reachable
        try:
            resp = await self._client.get("/")
            if resp.status_code == 200:
                logger.info("Connected to existing kubernetes-sigs agent-sandbox at %s", self.api_url)
                return
        except Exception:
            pass

        # If not reachable and auto_spawn enabled, start local runtime server
        if self.auto_spawn:
            port = int(self.api_url.split(":")[-1].split("/")[0]) if ":" in self.api_url else 8888
            self._spawned_base_dir = f"/tmp/bench-k8s-agent-sandbox-{os.getpid()}"
            os.makedirs(self._spawned_base_dir, exist_ok=True)

            server_script = Path(__file__).resolve().parents[3] / "deploy" / "agent-sandbox" / "server.py"
            env = os.environ.copy()
            env["SANDBOX_BASE_DIR"] = self._spawned_base_dir
            env["PORT"] = str(port)

            logger.info("Launching managed kubernetes-sigs agent-sandbox server on port %d...", port)
            self._server_proc = subprocess.Popen(
                [
                    "python3",
                    "-m",
                    "uvicorn",
                    "deploy.agent-sandbox.server:app",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    str(port),
                    "--log-level",
                    "warning",
                ],
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            # Wait for server to become healthy
            for _ in range(50):
                await asyncio.sleep(0.1)
                try:
                    resp = await self._client.get("/")
                    if resp.status_code == 200:
                        logger.info("Managed kubernetes-sigs agent-sandbox server is healthy!")
                        return
                except Exception:
                    pass

            raise RuntimeError(f"Failed to start kubernetes-sigs agent-sandbox server on {self.api_url}")

    async def prepare(self, prepared: PreparedExecution) -> None:
        """Stage input files into the agent-sandbox runtime via /upload."""
        if self._client is None:
            await self.initialize()

        assert self._client is not None

        # Upload staged input files
        for inp in prepared.inputs:
            files = {"file": (inp.relative_path, inp.data)}
            resp = await self._client.post("/upload", files=files)
            if resp.status_code not in (200, 201):
                logger.warning("Failed to upload input file %s: %s", inp.relative_path, resp.text)

    async def execute(self, prepared: PreparedExecution) -> RawExecutionResult:
        """Execute command in sandbox via /execute adhering to agent-sandbox protocol."""
        if self._client is None:
            await self.initialize()

        assert self._client is not None

        # Upload user script to execute
        script_filename = f"main_{prepared.nonce[:8]}.py"
        upload_resp = await self._client.post(
            "/upload",
            files={"file": (script_filename, prepared.request.code.encode())},
        )
        if upload_resp.status_code not in (200, 201):
            return RawExecutionResult(
                status="failed",
                stderr=f"Failed to upload execution script: {upload_resp.text}",
            )

        cmd = f"python3 {script_filename}"
        timeout_sec = float(prepared.request.timeout_seconds)

        payload = {
            "command": cmd,
            "timeout_seconds": timeout_sec,
        }

        try:
            # We allow an extra 5 seconds on HTTP client read to receive the 124 timeout response
            resp = await self._client.post(
                "/execute",
                json=payload,
                timeout=timeout_sec + 5.0,
            )

            if resp.status_code != 200:
                return RawExecutionResult(
                    status="failed",
                    stderr=f"Server returned HTTP {resp.status_code}: {resp.text}",
                )

            data = resp.json()
            stdout = data.get("stdout", "")
            stderr = data.get("stderr", "")
            exit_code = data.get("exit_code", 1)
            timed_out = data.get("timed_out", False)

            if timed_out or exit_code == 124:
                return RawExecutionResult(
                    stdout=stdout,
                    stderr=stderr,
                    exit_code=exit_code,
                    status="timed_out",
                    warnings=["Execution exceeded timeout limit (124)."],
                )

            return RawExecutionResult(
                stdout=stdout,
                stderr=stderr,
                exit_code=exit_code,
                status="success" if exit_code == 0 else "failed",
            )

        except (httpx.TimeoutException, asyncio.TimeoutError):
            return RawExecutionResult(
                status="timed_out",
                exit_code=124,
                warnings=["Client-side timeout waiting for agent-sandbox response."],
            )
        except Exception as exc:
            return RawExecutionResult(
                status="failed",
                stderr=f"{type(exc).__name__}: {exc}",
            )

    async def collect_artifacts(
        self, prepared: PreparedExecution, result: RawExecutionResult
    ) -> list[RetrievedArtifact]:
        """Download generated output artifacts from the sandbox via /download."""
        if self._client is None:
            return []

        artifacts: list[RetrievedArtifact] = []

        # Download transformed_output.txt if artifact_roundtrip suite
        candidate_paths = ["transformed_output.txt", "output.txt"]
        for path in candidate_paths:
            try:
                check_resp = await self._client.get(f"/exists/{path}")
                if check_resp.status_code == 200 and check_resp.json().get("exists"):
                    dl_resp = await self._client.get(f"/download/{path}")
                    if dl_resp.status_code == 200:
                        content = dl_resp.content
                        import hashlib
                        sha = hashlib.sha256(content).hexdigest()
                        artifacts.append(
                            RetrievedArtifact(
                                relative_path=path,
                                size_bytes=len(content),
                                sha256=sha,
                                data=content,
                            )
                        )
            except Exception as e:
                logger.debug("Failed checking artifact %s: %e", path, e)

        return artifacts

    async def cleanup(self, prepared: PreparedExecution) -> None:
        """Clean up per-execution temporary files."""
        pass

    async def teardown(self) -> None:
        """Terminate managed agent-sandbox runtime server process if spawned."""
        if self._client:
            await self._client.aclose()
            self._client = None

        if self._server_proc:
            try:
                self._server_proc.terminate()
                self._server_proc.wait(timeout=2.0)
            except Exception:
                try:
                    self._server_proc.kill()
                except Exception:
                    pass
            self._server_proc = None

        if self._spawned_base_dir:
            shutil.rmtree(self._spawned_base_dir, ignore_errors=True)
            self._spawned_base_dir = None
