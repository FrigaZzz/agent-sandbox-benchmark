"""Google ADK Bridge: exposes any ExecutionBackend as a Google ADK FunctionTool."""
from __future__ import annotations

import logging
import uuid
from typing import Any, Callable

from .interface import ExecutionBackend
from .models import (
    ExecuteCodeRequest,
    ExecutionTiming,
    InputFileRef,
    PreparedExecution,
    ResolvedInputFile,
)

logger = logging.getLogger(__name__)


def create_adk_tool(backend: ExecutionBackend) -> Any:
    """Wrap any ExecutionBackend as a Google ADK FunctionTool."""
    try:
        from google.adk.tools import FunctionTool, ToolContext
    except ImportError:
        logger.warning("google-adk is not installed. Returning standard async function callable.")

        async def fallback_execute_code(
            code: str,
            input_files: list[dict] | None = None,
            include_generated_artifacts: bool = False,
            timeout_seconds: int = 120,
        ) -> dict:
            request = ExecuteCodeRequest(
                code=code,
                input_files=[InputFileRef(**f) for f in (input_files or [])],
                include_generated_artifacts=include_generated_artifacts,
                timeout_seconds=timeout_seconds,
            )
            run_id = uuid.uuid4().hex
            prepared = PreparedExecution(
                run_id=run_id,
                nonce=uuid.uuid4().hex,
                root=f"/tmp/bench-run-{run_id}",
                request=request,
                inputs=[],
            )
            await backend.prepare(prepared)
            res = await backend.execute(prepared)
            await backend.cleanup(prepared)
            return {
                "run_id": run_id,
                "provider": backend.name,
                "status": res.status,
                "stdout": res.stdout,
                "stderr": res.stderr,
                "exit_code": res.exit_code,
                "warnings": res.warnings,
            }

        return fallback_execute_code

    async def execute_code(
        code: str,
        tool_context: ToolContext,
        input_files: list[InputFileRef] | None = None,
        include_generated_artifacts: bool = False,
        timeout_seconds: int = 120,
    ) -> dict:
        """Execute code in the selected remote sandbox backend.

        Staged files appear in INPUT_DIR. Deliverables written to ARTIFACT_DIR
        are automatically extracted and preserved.

        Args:
            code: Python or shell script source code.
            tool_context: ADK execution context injected automatically.
            input_files: ADK session artifact references to stage.
            include_generated_artifacts: Whether to extract ARTIFACT_DIR files.
            timeout_seconds: Hard timeout in seconds.
        """
        request = ExecuteCodeRequest(
            code=code,
            input_files=input_files or [],
            include_generated_artifacts=include_generated_artifacts,
            timeout_seconds=timeout_seconds,
        )

        resolved_inputs: list[ResolvedInputFile] = []
        for ref in request.input_files:
            try:
                # Fetch artifact bytes from ADK session context
                artifact = await tool_context.load_artifact(ref.artifact_name)
                data = artifact.data if hasattr(artifact, "data") else b""
                target = ref.target_name or ref.artifact_name
                resolved_inputs.append(
                    ResolvedInputFile(
                        artifact_name=ref.artifact_name,
                        relative_path=target,
                        data=data,
                    )
                )
            except Exception as exc:
                logger.warning("Could not resolve input artifact %s: %s", ref.artifact_name, exc)

        run_id = uuid.uuid4().hex
        prepared = PreparedExecution(
            run_id=run_id,
            nonce=uuid.uuid4().hex,
            root=f"/tmp/adk-bench-{run_id}",
            request=request,
            inputs=resolved_inputs,
        )

        await backend.prepare(prepared)
        raw_result = await backend.execute(prepared)

        saved_artifacts = []
        if include_generated_artifacts:
            collected = await backend.collect_artifacts(prepared, raw_result)
            for item in collected:
                if item.data is not None:
                    try:
                        await tool_context.save_artifact(
                            name=f"{run_id}-{item.relative_path}",
                            data=item.data,
                        )
                        saved_artifacts.append({
                            "relative_path": item.relative_path,
                            "size_bytes": item.size_bytes,
                            "sha256": item.sha256,
                            "status": "saved",
                        })
                    except Exception as err:
                        saved_artifacts.append({
                            "relative_path": item.relative_path,
                            "size_bytes": item.size_bytes,
                            "status": "failed",
                            "error": str(err),
                        })

        await backend.cleanup(prepared)

        return {
            "run_id": run_id,
            "provider": backend.name,
            "status": raw_result.status,
            "stdout": raw_result.stdout,
            "stderr": raw_result.stderr,
            "exit_code": raw_result.exit_code,
            "artifacts": saved_artifacts,
            "warnings": raw_result.warnings,
        }

    return FunctionTool(execute_code)
