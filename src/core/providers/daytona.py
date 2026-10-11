"""Daytona Sandbox backend adapter."""
from __future__ import annotations

import asyncio
import hashlib
import logging
import os
import shutil
from pathlib import Path
from .lifecycle import ownership

from ..interface import ExecutionBackend
from ..models import (
    BackendCapabilities,
    PreparedExecution,
    RawExecutionResult,
    RetrievedArtifact,
)

logger = logging.getLogger(__name__)

DEFAULT_API_URL = "https://app.daytona.io/api"


class DaytonaBackend(ExecutionBackend):
    """Adapter for Daytona Sandboxes cloud environment."""

    name = "daytona"
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
        api_key: str | None = None,
        api_url: str | None = None,
        jwt_token: str | None = None,
        organization_id: str | None = None,
    ) -> None:
        self.api_key = api_key or os.environ.get("DAYTONA_API_KEY")
        self.jwt_token = jwt_token or os.environ.get("DAYTONA_JWT_TOKEN")
        self.organization_id = organization_id or os.environ.get("DAYTONA_ORGANIZATION_ID")
        self.api_url = api_url or os.environ.get("DAYTONA_API_URL") or DEFAULT_API_URL
        self._client = None
        self._sandbox = None

        if not self.api_key and not (self.jwt_token and self.organization_id):
            self._load_cli_credentials()

    def _load_cli_credentials(self) -> None:
        candidate_paths = [
            Path.home() / "Library/Application Support/daytona/config.json",
            Path.home() / ".config/daytona/config.json",
        ]
        for p in candidate_paths:
            if p.exists():
                try:
                    import json
                    data = json.loads(p.read_text())
                    active_name = data.get("activeProfile", "initial")
                    profiles = data.get("profiles", [])
                    prof = next((pr for pr in profiles if pr.get("name") == active_name), None)
                    if not prof and profiles:
                        prof = profiles[0]
                    if prof:
                        api_info = prof.get("api", {})
                        self.api_key = self.api_key or api_info.get("key") or None
                        tok = api_info.get("token")
                        if isinstance(tok, dict):
                            self.jwt_token = self.jwt_token or tok.get("accessToken")
                        elif isinstance(tok, str):
                            self.jwt_token = self.jwt_token or tok
                        self.organization_id = self.organization_id or prof.get("activeOrganizationId")
                        if api_info.get("url"):
                            self.api_url = api_info.get("url")
                        break
                except Exception as e:
                    logger.debug("Failed loading daytona CLI config from %s: %s", p, e)

    async def initialize(self) -> None:
        try:
            from daytona_sdk import Daytona, DaytonaConfig

            cfg_kwargs: dict[str, str | None] = {"api_url": self.api_url}
            if self.api_key:
                cfg_kwargs["api_key"] = self.api_key
            if self.jwt_token:
                cfg_kwargs["jwt_token"] = self.jwt_token
            if self.organization_id:
                cfg_kwargs["organization_id"] = self.organization_id

            cfg = DaytonaConfig(**cfg_kwargs)
            self._client = Daytona(cfg)
        except Exception as exc:
            logger.warning("Could not initialize Daytona client: %s", exc)

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
            from daytona_sdk.common.errors import DaytonaProcessExecutionTimeoutError

            if self._client is None:
                await self.initialize()

            # API request timeout is distinct from server-side maximum lifetime.
            from daytona_sdk import CreateSandboxFromSnapshotParams
            sb = await asyncio.to_thread(self._client.create,
                CreateSandboxFromSnapshotParams(ttl_minutes=15, auto_stop_interval=5,
                    auto_delete_interval=0, labels=ownership(prepared.run_id)), timeout=60)
            self._sandbox = sb

            # Stage input files into sandbox
            for inp in prepared.inputs:
                try:
                    sb.fs.upload_file(inp.data, f"/tmp/{inp.relative_path}")
                except Exception as fe:
                    logger.warning("Could not upload input file %s: %s", inp.relative_path, fe)

            # Upload main python script
            script_remote = f"/tmp/bench_{prepared.run_id}.py"
            sb.fs.upload_file(prepared.request.code.encode("utf-8"), script_remote)

            timeout_s = max(prepared.request.timeout_seconds, 1)

            try:
                res = sb.process.exec(
                    f"python {script_remote}",
                    cwd="/tmp",
                    timeout=timeout_s,
                )
                stdout = res.result or (res.artifacts.stdout if res.artifacts else "") or ""
                return RawExecutionResult(
                    stdout=stdout,
                    exit_code=res.exit_code,
                    status="success" if res.exit_code == 0 else "failed",
                )
            except DaytonaProcessExecutionTimeoutError as te:
                return RawExecutionResult(
                    status="timed_out",
                    stderr=str(te),
                    warnings=["daytona_timeout"],
                )

        except Exception as exc:
            logger.warning("Daytona execution error: %s", exc)
            return RawExecutionResult(
                status="failed",
                stderr=str(exc),
                warnings=[f"daytona_error: {type(exc).__name__}"],
            )

    async def collect_artifacts(
        self, prepared: PreparedExecution, result: RawExecutionResult
    ) -> list[RetrievedArtifact]:
        if self._sandbox is None:
            return []
        artifacts = []
        target_file = "/tmp/transformed_output.txt"
        try:
            data = self._sandbox.fs.download_file(target_file)
            if data:
                artifacts.append(
                    RetrievedArtifact(
                        relative_path="transformed_output.txt",
                        data=data,
                        size_bytes=len(data),
                        sha256=hashlib.sha256(data).hexdigest(),
                    )
                )
        except Exception:
            pass
        return artifacts

    async def cleanup(self, prepared: PreparedExecution) -> None:
        shutil.rmtree(prepared.root, ignore_errors=True)
        if self._sandbox is not None:
            await asyncio.to_thread(self._sandbox.delete)
            self._sandbox = None

    async def teardown(self) -> None:
        if self._sandbox is not None:
            await asyncio.to_thread(self._sandbox.delete)
            self._sandbox = None
