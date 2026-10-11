"""Gemini Built-In Code Execution Tool adapter."""
from __future__ import annotations

import logging
import os

from ..interface import ExecutionBackend
from ..models import (
    BackendCapabilities,
    PreparedExecution,
    RawExecutionResult,
    RetrievedArtifact,
)

logger = logging.getLogger(__name__)


class GeminiToolBackend(ExecutionBackend):
    """Adapter for Google Gemini model-managed code execution."""

    name = "gemini_tool"
    capabilities = BackendCapabilities(
        native_input_files=False,
        native_output_files=False,
        persistent_filesystem=False,
        shell_execution=False,
        supports_multiple_files=False,
        supports_direct_binary_transfer=False,
        has_internet_access=False,
        has_custom_packages=False,
        model_managed=True,
        cmek_supported=False,
    )

    def __init__(self, model_name: str = "gemini-2.5-flash") -> None:
        self.model_name = model_name

    async def initialize(self) -> None:
        pass

    async def prepare(self, prepared: PreparedExecution) -> None:
        pass

    async def execute(self, prepared: PreparedExecution) -> RawExecutionResult:
        try:
            from google import genai
            from google.genai import types

            if os.environ.get("GEMINI_API_KEY"):
                client = genai.Client()
            else:
                project = os.environ.get("GOOGLE_CLOUD_PROJECT")
                if not project:
                    raise ValueError("Set GEMINI_API_KEY or GOOGLE_CLOUD_PROJECT for your Gemini integration.")
                location = os.environ.get("GOOGLE_CLOUD_LOCATION", "europe-west8")
                client = genai.Client(vertexai=True, project=project, location=location)

            prompt = (
                f"Please execute the following Python code directly using your code execution tool and return the output:\n\n"
                f"```python\n{prepared.request.code}\n```"
            )
            resp = await client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(code_execution=types.ToolCodeExecution())]
                ),
            )

            raw_stdout = ""
            codes = []
            outcomes = []
            if resp.candidates and resp.candidates[0].content and resp.candidates[0].content.parts:
                for part in resp.candidates[0].content.parts:
                    if getattr(part, "executable_code", None):
                        codes.append(part.executable_code.code.strip())
                    if hasattr(part, "code_execution_result") and part.code_execution_result:
                        raw_stdout += getattr(part.code_execution_result, "output", "") or ""
                        outcomes.append(str(part.code_execution_result.outcome))

            if not raw_stdout:
                return RawExecutionResult(status="failed", stderr="No code execution tool output returned.")

            return RawExecutionResult(
                status="success" if outcomes and all(o.endswith("OUTCOME_OK") for o in outcomes) else "failed",
                stdout=raw_stdout,
                exit_code=0,
                manifest={"exact_code_executed": codes == [prepared.request.code.strip()],
                          "tool_outcome_ok": bool(outcomes) and all(o.endswith("OUTCOME_OK") for o in outcomes),
                          "tool_blocks": len(codes), "outcomes": outcomes},
            )
        except Exception as exc:
            logger.warning("Gemini tool execution: %s", exc)
            return RawExecutionResult(
                status="failed",
                stderr=str(exc),
                warnings=[f"gemini_tool_error: {type(exc).__name__}"],
            )

    async def collect_artifacts(
        self, prepared: PreparedExecution, result: RawExecutionResult
    ) -> list[RetrievedArtifact]:
        return []

    async def cleanup(self, prepared: PreparedExecution) -> None:
        pass

    async def teardown(self) -> None:
        pass
