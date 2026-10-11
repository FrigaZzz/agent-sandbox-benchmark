"""Databricks AI Gateway MCP sandbox (system.ai.sandbox run_code) execution backend."""
from __future__ import annotations

import asyncio
import base64
import json
import logging
import os
import shutil
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any

from ..interface import ExecutionBackend
from ..models import (
    BackendCapabilities,
    PreparedExecution,
    RawExecutionResult,
    RetrievedArtifact,
)

logger = logging.getLogger(__name__)

DEFAULT_SERVICE = "system.ai.sandbox"
RUN_CODE_TOOL = "run_code"


class DatabricksMcpSandboxBackend(ExecutionBackend):
    """Adapter for the Databricks AI Gateway MCP sandbox service.

    Distinct product from the Dedicated Sandbox MicroVM API: this speaks MCP
    JSON-RPC (tools/list, tools/call run_code) to
    ``{host}/ai-gateway/mcp-services/<service>`` using the Databricks CLI
    profile / environment credentials. The service exposes a single tool,
    ``run_code`` (python / sh, optional session_id); there is no native file
    staging API, so workload inputs are inline-staged as base64 literals and
    recorded as such. No remote state is kept: sessions are ephemeral.
    """

    name = "databricks_mcp"
    capabilities = BackendCapabilities(
        native_input_files=False,
        native_output_files=False,
        persistent_filesystem=False,
        shell_execution=True,
        supports_multiple_files=False,
        supports_direct_binary_transfer=False,
        has_internet_access=False,
        has_custom_packages=False,
        model_managed=False,
        cmek_supported=False,
    )

    def __init__(self, profile: str | None = None, service: str = DEFAULT_SERVICE) -> None:
        self.profile = profile or os.environ.get("DATABRICKS_CONFIG_PROFILE")
        self.service = service or DEFAULT_SERVICE
        self._endpoint: str | None = None
        self._auth_headers: dict[str, str] | None = None

    @property
    def benchmark_configuration(self) -> dict[str, Any]:
        return {"product": "AI Gateway MCP system.ai.sandbox run_code", "service": self.service,
                "cpu": None, "memory": None, "gpu": None, "session_mode": "ephemeral per execute"}

    async def initialize(self) -> None:
        try:
            from databricks.sdk import WorkspaceClient

            client = WorkspaceClient(profile=self.profile) if self.profile else WorkspaceClient()
            config = client.config
            self._auth_headers = dict(config.authenticate())
            self._endpoint = config.host.rstrip("/") + f"/ai-gateway/mcp-services/{self.service}"
        except Exception as exc:
            logger.warning("Could not initialize Databricks MCP client: %s", exc)
            self._endpoint = None
            self._auth_headers = None

    def _rpc(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        if self._endpoint is None or self._auth_headers is None:
            raise RuntimeError("Databricks MCP client not initialized (missing host/credentials).")
        payload = {"jsonrpc": "2.0", "method": method, "id": 1}
        if params is not None:
            payload["params"] = params
        request = urllib.request.Request(
            self._endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={**self._auth_headers, "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:500]
            raise RuntimeError(f"MCP HTTP {exc.code}: {detail}") from exc
        if not isinstance(body, dict) or "error" in body:
            raise RuntimeError(f"MCP error: {json.dumps(body)[:500]}")
        result = body.get("result", {})
        return result if isinstance(result, dict) else {"value": result}

    async def prepare(self, prepared: PreparedExecution) -> None:
        for d in (prepared.input_dir, prepared.work_dir, prepared.output_dir):
            os.makedirs(d, exist_ok=True)
        script_path = Path(prepared.work_dir) / "main.py"
        script_path.write_text(prepared.request.code)

    def _wrap_with_inputs(self, code: str, prepared: PreparedExecution) -> tuple[str, list[str]]:
        warnings: list[str] = []
        if not prepared.inputs:
            return code, warnings
        lines = ["import base64 as _b64", "import os as _os"]
        for inp in prepared.inputs:
            blob = base64.b64encode(inp.data).decode("ascii")
            lines.append(f"_open = open({inp.relative_path!r}, 'wb'); _open.write(_b64.b64decode('{blob}')); _open.close()")
        warnings.append(f"databricks_mcp_inline_staged_inputs:{len(prepared.inputs)} (no native file API)")
        return "\n".join(lines) + "\n" + code, warnings

    @staticmethod
    def _result_text(result: dict[str, Any]) -> str:
        texts: list[str] = []
        content = result.get("content", [])
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and isinstance(block.get("text"), str):
                    texts.append(block["text"])
        if texts:
            return "\n".join(texts)
        structured = result.get("structuredContent")
        if structured is not None:
            return json.dumps(structured)[:20000]
        return json.dumps(result)[:20000]

    async def execute(self, prepared: PreparedExecution) -> RawExecutionResult:
        try:
            if self._endpoint is None:
                await self.initialize()

            loop = asyncio.get_event_loop()
            listed = await loop.run_in_executor(None, lambda: self._rpc("tools/list"))
            tools = [t.get("name") for t in listed.get("tools", []) if isinstance(t, dict)]
            warnings = []
            if tools and RUN_CODE_TOOL not in tools:
                warnings.append(f"databricks_mcp_missing_tool:{RUN_CODE_TOOL} (available: {','.join(tools)})")

            language = "sh" if prepared.request.language == "bash" else "python"
            code, staged = self._wrap_with_inputs(prepared.request.code, prepared)
            warnings.extend(staged)
            arguments: dict[str, Any] = {"code": code, "language": language,
                                         "timeout_seconds": prepared.request.timeout_seconds}
            result = await loop.run_in_executor(
                None, lambda: self._rpc("tools/call", {"name": RUN_CODE_TOOL, "arguments": arguments}))

            stdout = self._result_text(result)
            raw_exit = result.get("exit_code")
            exit_code = raw_exit if isinstance(raw_exit, int) and not isinstance(raw_exit, bool) else None
            status = result.get("status", "success")
            if status not in ("success", "failed", "timed_out", "oom", "unknown"):
                status = "success" if (exit_code in (None, 0)) else "failed"
            return RawExecutionResult(
                stdout=stdout,
                stderr=result.get("stderr", "") if isinstance(result.get("stderr"), str) else "",
                exit_code=exit_code,
                status=status,  # type: ignore[arg-type]
                warnings=warnings,
                manifest={"mcp_session": result.get("session_id"), "tools": tools},
            )
        except Exception as exc:
            err_msg = str(exc)
            logger.warning("Databricks MCP sandbox error: %s", exc)
            return RawExecutionResult(
                status="failed",
                stderr=err_msg,
                warnings=[f"databricks_mcp_error: {type(exc).__name__}"],
            )

    async def collect_artifacts(
        self, prepared: PreparedExecution, result: RawExecutionResult
    ) -> list[RetrievedArtifact]:
        return []

    async def cleanup(self, prepared: PreparedExecution) -> None:
        shutil.rmtree(prepared.root, ignore_errors=True)

    async def teardown(self) -> None:
        return None
