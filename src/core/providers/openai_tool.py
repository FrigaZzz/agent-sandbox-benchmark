"""OpenAI Code Interpreter Tool adapter."""
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


class OpenAIToolBackend(ExecutionBackend):
    """Adapter for OpenAI Assistants Code Interpreter tool."""

    name = "openai_tool"
    capabilities = BackendCapabilities(
        native_input_files=True,
        native_output_files=True,
        persistent_filesystem=False,
        shell_execution=False,
        supports_multiple_files=True,
        supports_direct_binary_transfer=False,
        has_internet_access=False,
        has_custom_packages=False,
        model_managed=True,
        cmek_supported=False,
    )

    def __init__(self, model_name: str = "gpt-4o") -> None:
        self.model_name = model_name

    async def initialize(self) -> None:
        pass

    async def prepare(self, prepared: PreparedExecution) -> None:
        pass

    async def execute(self, prepared: PreparedExecution) -> RawExecutionResult:
        try:
            import openai

            client = openai.AsyncOpenAI()
            assistant = await client.beta.assistants.create(
                name="Sandbox Benchmark Assistant",
                instructions="Execute the requested python code using your code_interpreter tool and return exact stdout.",
                tools=[{"type": "code_interpreter"}],
                model=self.model_name,
            )
            thread = await client.beta.threads.create(
                messages=[{
                    "role": "user",
                    "content": f"Execute this code and output raw stdout:\n```python\n{prepared.request.code}\n```"
                }]
            )
            run = await client.beta.threads.runs.create_and_poll(
                thread_id=thread.id, assistant_id=assistant.id
            )
            messages = await client.beta.threads.messages.list(thread_id=thread.id)
            out_text = ""
            for m in messages.data:
                if m.role == "assistant":
                    for block in m.content:
                        if hasattr(block, "text"):
                            out_text += block.text.value + "\n"

            # Clean up assistant
            await client.beta.assistants.delete(assistant.id)

            return RawExecutionResult(
                status="success" if run.status == "completed" else "failed",
                stdout=out_text,
                exit_code=0 if run.status == "completed" else 1,
            )
        except Exception as exc:
            logger.warning("OpenAI tool execution: %s", exc)
            return RawExecutionResult(
                status="failed",
                stderr=str(exc),
                warnings=[f"openai_tool_error: {type(exc).__name__}"],
            )

    async def collect_artifacts(
        self, prepared: PreparedExecution, result: RawExecutionResult
    ) -> list[RetrievedArtifact]:
        return []

    async def cleanup(self, prepared: PreparedExecution) -> None:
        pass

    async def teardown(self) -> None:
        pass
