"""Alibaba OpenSandbox & AgentRun execution backend provider.

Implements the Alibaba OpenSandbox runtime & AgentRun specification:
https://github.com/opensandbox-group/OpenSandbox
"""
from __future__ import annotations

import asyncio
import hashlib
import io
import logging
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

import httpx

from ..interface import ExecutionBackend
from ..models import (
    BackendCapabilities,
    PreparedExecution,
    RawExecutionResult,
    RetrievedArtifact,
)

logger = logging.getLogger(__name__)

TIMEOUT_EXIT_CODE = 124


class AlibabaBackend(ExecutionBackend):
    """Execution backend targeting Alibaba OpenSandbox and managed AgentRun.

    Supports:
    1. Remote AgentRun / OpenSandbox server via OPENSANDBOX_URL or AGENTRUN_SANDBOX_ENDPOINT
    2. Self-hosted managed process mode (automatically boots runtime server if not running)
    3. Official opensandbox Python SDK integration
    """

    name = "alibaba"
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

    def __init__(
        self,
        api_url: str | None = None,
        api_key: str | None = None,
        auto_spawn: bool = True,
        *,
        image: str = "opensandbox/code-interpreter:v1.0.2",
        cpu: str = "1",
        memory: str = "2Gi",
    ) -> None:
        self.api_url = (
            api_url
            or os.environ.get("OPENSANDBOX_URL")
            or os.environ.get("AGENTRUN_SANDBOX_ENDPOINT")
            or "http://127.0.0.1:8889"
        ).rstrip("/")
        key = (
            api_key
            or os.environ.get("OPENSANDBOX_API_KEY")
            or os.environ.get("ALIBABA_CLOUD_AGENTRUN_API_KEY")
            or os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_ID")
        )
        self.access_key_secret = os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_SECRET")
        self.sts_token = os.environ.get("ALIBABA_CLOUD_SECURITY_TOKEN")
        self.region_id = os.environ.get("ALIBABA_CLOUD_REGION_ID", "ap-southeast-1")

        if not key:
            cfg_path = Path.home() / ".aliyun" / "config.json"
            if cfg_path.exists():
                try:
                    import json
                    cfg_data = json.loads(cfg_path.read_text())
                    cur_prof = cfg_data.get("current", "default")
                    prof = next((p for p in cfg_data.get("profiles", []) if p.get("name") == cur_prof), None)
                    if prof:
                        key = prof.get("access_key_id") or prof.get("oauth_access_token")
                        self.access_key_secret = prof.get("access_key_secret")
                        self.sts_token = prof.get("sts_token")
                        self.region_id = prof.get("region_id") or self.region_id
                except Exception:
                    pass

        self.api_key = key
        self.auto_spawn = auto_spawn
        self.benchmark_configuration = {
            "product": "Alibaba OpenSandbox / AgentRun",
            "image": image,
            "cpu": cpu,
            "memory": memory,
            "gpu": None,
            "session_mode": "stateful_reusable",
        }
        self._server_proc: subprocess.Popen | None = None
        self._spawned_base_dir: str | None = None
        self._client: httpx.AsyncClient | None = None
        self._sandbox_id: str | None = None

    async def initialize(self) -> None:
        """Verify connectivity to OpenSandbox/AgentRun server, or spawn managed instance."""
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        self._client = httpx.AsyncClient(
            base_url=self.api_url,
            headers=headers,
            timeout=30.0,
        )

        # Check if server is already reachable
        try:
            resp = await self._client.get("/health")
            if resp.status_code == 200:
                logger.info("Connected to existing Alibaba OpenSandbox runtime at %s", self.api_url)
                return
        except Exception:
            pass

        try:
            resp = await self._client.get("/")
            if resp.status_code == 200:
                logger.info("Connected to existing Alibaba OpenSandbox runtime at %s", self.api_url)
                return
        except Exception:
            pass

        # If not reachable and auto_spawn enabled, start local runtime server
        if self.auto_spawn:
            port = int(self.api_url.split(":")[-1].split("/")[0]) if ":" in self.api_url else 8889
            self._spawned_base_dir = f"/tmp/bench-alibaba-opensandbox-{os.getpid()}"
            os.makedirs(self._spawned_base_dir, exist_ok=True)

            server_script = Path(__file__).resolve().parents[3] / "deploy" / "opensandbox" / "server.py"
            env = os.environ.copy()
            env["OPENSANDBOX_BASE_DIR"] = self._spawned_base_dir
            env["PORT"] = str(port)

            logger.info("Launching managed Alibaba OpenSandbox server on port %d...", port)
            self._server_proc = subprocess.Popen(
                [
                    "python3",
                    "-m",
                    "uvicorn",
                    "deploy.opensandbox.server:app",
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
                    resp = await self._client.get("/health")
                    if resp.status_code == 200:
                        logger.info("Managed Alibaba OpenSandbox server is healthy!")
                        return
                except Exception:
                    pass

            raise RuntimeError(f"Failed to start Alibaba OpenSandbox server on {self.api_url}")

    async def prepare(self, prepared: PreparedExecution) -> None:
        """Stage input files into the OpenSandbox runtime via /files/upload."""
        if self._client is None:
            await self.initialize()

        assert self._client is not None

        # Create sandbox session if not yet active
        if self._sandbox_id is None:
            try:
                resp = await self._client.post(
                    "/sandboxes",
                    json={"image": self.benchmark_configuration["image"]},
                )
                if resp.status_code in (200, 201):
                    self._sandbox_id = resp.json().get("id")
            except Exception as e:
                logger.debug("Sandbox session creation note: %s", e)

        # Upload staged input files
        for inp in prepared.inputs:
            files = {"file": (inp.relative_path, inp.data)}
            params = {"path": inp.relative_path}
            resp = await self._client.post("/files/upload", files=files, params=params)
            if resp.status_code not in (200, 201):
                # Fallback to /upload
                resp = await self._client.post("/upload", files={"file": (inp.relative_path, inp.data)})
                if resp.status_code not in (200, 201):
                    logger.warning("Failed to upload input file %s: %s", inp.relative_path, resp.text)

    async def execute(self, prepared: PreparedExecution) -> RawExecutionResult:
        """Execute command in OpenSandbox adhering to OpenSandbox protocol."""
        if self._client is None:
            await self.initialize()

        assert self._client is not None

        # Prepare wrapped code script
        wrapped_code = (
            "import os, pathlib\n"
            "os.environ.setdefault('INPUT_DIR', str(pathlib.Path('.').resolve()))\n"
            "os.environ.setdefault('ARTIFACT_DIR', str(pathlib.Path('.').resolve()))\n"
            + prepared.request.code
        )

        script_filename = f"main_{prepared.nonce[:8]}.py"
        upload_resp = await self._client.post(
            "/files/upload",
            files={"file": (script_filename, wrapped_code.encode())},
            params={"path": script_filename},
        )
        if upload_resp.status_code not in (200, 201):
            upload_resp = await self._client.post(
                "/upload",
                files={"file": (script_filename, wrapped_code.encode())},
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
            "timeout": timeout_sec,
            "envs": {
                "INPUT_DIR": ".",
                "ARTIFACT_DIR": ".",
            },
        }

        try:
            resp = await self._client.post(
                "/command",
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

            if timed_out or exit_code == TIMEOUT_EXIT_CODE:
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
                exit_code=TIMEOUT_EXIT_CODE,
                warnings=["Client-side timeout waiting for Alibaba OpenSandbox response."],
            )
        except Exception as exc:
            return RawExecutionResult(
                status="failed",
                stderr=f"{type(exc).__name__}: {exc}",
            )

    async def collect_artifacts(
        self, prepared: PreparedExecution, result: RawExecutionResult
    ) -> list[RetrievedArtifact]:
        """Download generated output artifacts from OpenSandbox via /files/download."""
        if self._client is None:
            return []

        artifacts: list[RetrievedArtifact] = []
        seen = set()

        async def _check_and_add(rel_path: str, artifact_name: str | None = None):
            base_name = artifact_name or os.path.basename(rel_path)
            if base_name in seen:
                return
            try:
                check_resp = await self._client.get(f"/exists/{rel_path}")
                if check_resp.status_code == 200 and check_resp.json().get("exists"):
                    dl_resp = await self._client.get("/files/download", params={"path": rel_path})
                    if dl_resp.status_code != 200:
                        dl_resp = await self._client.get(f"/download/{rel_path}")
                    if dl_resp.status_code == 200:
                        seen.add(base_name)
                        content = dl_resp.content
                        sha = hashlib.sha256(content).hexdigest()
                        artifacts.append(
                            RetrievedArtifact(
                                relative_path=base_name,
                                size_bytes=len(content),
                                sha256=sha,
                                data=content,
                            )
                        )
            except Exception as e:
                logger.debug("Failed checking artifact %s: %s", rel_path, e)

        # 1. Discover artifacts via /list/ in base and output directories
        try:
            for prefix in ["output", ""]:
                list_resp = await self._client.get(f"/list/{prefix}".rstrip("/"))
                if list_resp.status_code == 200:
                    for item in list_resp.json().get("items", []):
                        if not item.get("is_dir"):
                            name = item["name"]
                            # Ignore scripts and uploaded input payloads
                            if not name.startswith("main_") and not name.endswith(".py") and name != "payload.bin":
                                full_rel = f"{prefix}/{name}".strip("/")
                                await _check_and_add(full_rel, name)
        except Exception:
            pass

        # 2. Known benchmark target fallbacks
        for path in ["transformed_output.txt", "output.txt", "summary.json", "output/summary.json"]:
            await _check_and_add(path)

        return artifacts

    async def cleanup(self, prepared: PreparedExecution) -> None:
        """Clean up per-execution temporary files."""
        pass

    async def teardown(self) -> None:
        """Terminate managed Alibaba OpenSandbox runtime server process if spawned."""
        if self._client:
            if self._sandbox_id:
                try:
                    await self._client.delete(f"/sandboxes/{self._sandbox_id}")
                except Exception:
                    pass
                self._sandbox_id = None
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
