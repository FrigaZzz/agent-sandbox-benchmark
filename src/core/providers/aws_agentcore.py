"""Amazon Bedrock AgentCore Code Interpreter Sandbox adapter."""
from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import shutil
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

DEFAULT_REGION = "eu-north-1"


class AWSAgentCoreBackend(ExecutionBackend):
    """Adapter for Amazon Bedrock AgentCore Code Interpreter Sandboxes."""

    name = "aws"
    capabilities = BackendCapabilities(
        native_input_files=True,
        native_output_files=True,
        persistent_filesystem=True,
        shell_execution=True,
        supports_multiple_files=True,
        supports_direct_binary_transfer=True,
        has_internet_access=False,  # SANDBOX networkMode
        has_custom_packages=True,
        model_managed=False,
        cmek_supported=True,
    )

    def __init__(
        self,
        tool_id: str | None = None,
        region: str | None = None,
    ) -> None:
        self.tool_id = tool_id or os.environ.get("AWS_BEDROCK_AGENTCORE_TOOL_ID")
        self.region = region or os.environ.get("AWS_REGION") or DEFAULT_REGION
        self._client = None
        self._session_id = None

    async def initialize(self) -> None:
        if not self.tool_id:
            raise ValueError("Set AWS_BEDROCK_AGENTCORE_TOOL_ID or pass tool_id for your code interpreter.")
        try:
            import boto3

            self._client = boto3.client("bedrock-agentcore", region_name=self.region)
        except Exception as exc:
            logger.warning("Could not initialize bedrock-agentcore boto3 client: %s", exc)

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
            if self._client is None:
                await self.initialize()

            loop = asyncio.get_event_loop()

            # 1. Start sandbox session
            timeout_sec = min(max(prepared.request.timeout_seconds, 60), 900)

            def _start_session():
                return self._client.start_code_interpreter_session(
                    codeInterpreterIdentifier=self.tool_id,
                    name=f"bench-{prepared.run_id[:16]}",
                    sessionTimeoutSeconds=timeout_sec,
                )

            session = await loop.run_in_executor(None, _start_session)
            self._session_id = session.get("sessionId")

            # 2. Stage input files if provided
            if prepared.inputs:
                content_payload = []
                for inp in prepared.inputs:
                    try:
                        content_payload.append({
                            "path": inp.relative_path,
                            "text": inp.data.decode("utf-8", errors="ignore"),
                        })
                    except Exception as fe:
                        logger.warning("Could not stage file %s: %s", inp.relative_path, fe)

                if content_payload:
                    def _write_files():
                        return self._client.invoke_code_interpreter(
                            codeInterpreterIdentifier=self.tool_id,
                            sessionId=self._session_id,
                            name="writeFiles",
                            arguments={"content": content_payload},
                        )

                    await loop.run_in_executor(None, _write_files)

            # 3. Execute python code
            def _execute_code():
                return self._client.invoke_code_interpreter(
                    codeInterpreterIdentifier=self.tool_id,
                    sessionId=self._session_id,
                    name="executeCode",
                    arguments={
                        "code": prepared.request.code,
                        "language": "python",
                    },
                )

            response = await loop.run_in_executor(None, _execute_code)

            # Parse response payload
            stdout_parts = []
            stderr_parts = []
            exit_code = 0

            if "stream" in response:
                for event in response["stream"]:
                    res = event.get("result", {})
                    if isinstance(res, dict):
                        # Structured content from Bedrock AgentCore
                        sc = res.get("structuredContent", {})
                        if sc:
                            if sc.get("stdout"):
                                stdout_parts.append(str(sc["stdout"]))
                            if sc.get("stderr"):
                                stderr_parts.append(str(sc["stderr"]))
                            if "exitCode" in sc:
                                exit_code = sc["exitCode"]
                        else:
                            for c in res.get("content", []):
                                if c.get("text"):
                                    stdout_parts.append(c["text"])
                        if res.get("isError"):
                            exit_code = 1
            elif "response" in response:
                body = response["response"].read()
                data = json.loads(body.decode("utf-8"))
                if isinstance(data, dict):
                    stdout_parts.append(str(data.get("stdout", "")))
                    stderr_parts.append(str(data.get("stderr", "")))
                    if data.get("error"):
                        stderr_parts.append(str(data["error"]))
                        exit_code = 1

            full_stdout = "".join(stdout_parts)
            full_stderr = "\n".join(stderr_parts).strip()

            return RawExecutionResult(
                stdout=full_stdout,
                stderr=full_stderr,
                exit_code=exit_code,
                status="success" if exit_code == 0 else "failed",
            )

        except Exception as exc:
            err_msg = str(exc)
            logger.warning("AWS Bedrock AgentCore execution error: %s", exc)
            return RawExecutionResult(
                status="failed",
                stderr=err_msg,
                warnings=[f"aws_agentcore_error: {type(exc).__name__}"],
            )

    async def collect_artifacts(
        self, prepared: PreparedExecution, result: RawExecutionResult
    ) -> list[RetrievedArtifact]:
        if not self._client or not self._session_id:
            return []

        artifacts = []
        target_file = "transformed_output.txt"
        loop = asyncio.get_event_loop()

        try:
            def _read_file():
                return self._client.invoke_code_interpreter(
                    codeInterpreterIdentifier=self.tool_id,
                    sessionId=self._session_id,
                    name="readFiles",
                    arguments={"paths": [target_file]},
                )

            res = await loop.run_in_executor(None, _read_file)
            content_str = None
            if "stream" in res:
                for event in res["stream"]:
                    r = event.get("result", {})
                    for item in r.get("content", []):
                        if item.get("type") == "resource" and "resource" in item:
                            content_str = item["resource"].get("text")
                            break
                        elif item.get("text"):
                            content_str = item["text"]
            elif "response" in res:
                body = res["response"].read()
                data = json.loads(body.decode("utf-8"))
                if isinstance(data, dict) and target_file in data:
                    content_str = data[target_file]

            if content_str is not None:
                content_bytes = content_str.encode("utf-8")
                artifacts.append(
                    RetrievedArtifact(
                        relative_path=target_file,
                        data=content_bytes,
                        size_bytes=len(content_bytes),
                        sha256=hashlib.sha256(content_bytes).hexdigest(),
                    )
                )
        except Exception as exc:
            logger.warning("Could not retrieve artifact from AWS AgentCore: %s", exc)

        return artifacts

    async def cleanup(self, prepared: PreparedExecution) -> None:
        shutil.rmtree(prepared.root, ignore_errors=True)
        if self._client and self._session_id:
            try:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    None,
                    lambda: self._client.stop_code_interpreter_session(
                        codeInterpreterIdentifier=self.tool_id,
                        sessionId=self._session_id,
                    ),
                )
            except Exception:
                raise
            self._session_id = None

    async def teardown(self) -> None:
        if self._client and self._session_id:
            await asyncio.to_thread(self._client.stop_code_interpreter_session,
                codeInterpreterIdentifier=self.tool_id, sessionId=self._session_id)
            self._session_id = None
