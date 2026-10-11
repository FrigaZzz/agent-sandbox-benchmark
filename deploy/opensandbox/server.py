"""Alibaba OpenSandbox & AgentRun runtime server implementation.

Adheres to OpenSandbox lifecycle and execd specifications:
https://github.com/opensandbox-group/OpenSandbox
"""
import asyncio
import io
import json
import logging
import os
import shutil
import time
import uuid
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, File, UploadFile, HTTPException, Query, Request
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

logger = logging.getLogger("opensandbox_server")

TIMEOUT_EXIT_CODE = 124


class RunCommandBody(BaseModel):
    command: str | None = None
    argv: list[str] | None = None
    cwd: str | None = None
    background: bool = False
    timeout: float | None = None  # in seconds or ms
    envs: dict[str, str] | None = None


class CreateSandboxBody(BaseModel):
    image: dict | str | None = None
    entrypoint: list[str] | None = None
    env: dict[str, str] | None = None
    metadata: dict[str, str] | None = None
    timeout: int | None = None
    resource: dict[str, str] | None = None


def get_base_dir() -> str:
    """Base directory where commands execute and files are stored."""
    base = os.environ.get("OPENSANDBOX_BASE_DIR", "").strip() or "/tmp/opensandbox-data"
    os.makedirs(base, exist_ok=True)
    return os.path.realpath(base)


def get_safe_path(file_path: str) -> str:
    """Guarantees relative file paths stay within the sandbox base directory."""
    base_dir = get_base_dir()
    clean_path = file_path.lstrip("/")
    full_path = os.path.realpath(os.path.join(base_dir, clean_path))
    if os.path.commonpath([base_dir, full_path]) != base_dir:
        raise ValueError("Access denied: Path must be within sandbox base directory")
    return full_path


app = FastAPI(
    title="Alibaba OpenSandbox / AgentRun Server",
    description="Server implementing OpenSandbox lifecycle and execution APIs.",
    version="1.1.1",
)

# Active sandboxes registry
ACTIVE_SANDBOXES: dict[str, dict] = {}


@app.get("/", summary="Health Check")
@app.get("/health", summary="Health Check")
async def health_check():
    return {
        "status": "ok",
        "message": "OpenSandbox runtime active.",
        "runtime": "alibaba/opensandbox",
        "sandboxes_count": len(ACTIVE_SANDBOXES),
    }


# Lifecycle APIs
@app.post("/sandboxes", summary="Create sandbox")
async def create_sandbox(req: CreateSandboxBody | None = None):
    sandbox_id = f"sb-{uuid.uuid4().hex[:12]}"
    created_at = time.time()
    ACTIVE_SANDBOXES[sandbox_id] = {
        "id": sandbox_id,
        "status": "Running",
        "created_at": created_at,
        "expires_at": created_at + 600,
    }
    return {
        "id": sandbox_id,
        "status": "Running",
        "created_at": created_at,
        "expires_at": created_at + 600,
    }


@app.get("/sandboxes/{sandbox_id}", summary="Get sandbox details")
async def get_sandbox(sandbox_id: str):
    sb = ACTIVE_SANDBOXES.get(sandbox_id)
    if not sb:
        return {"id": sandbox_id, "status": "Running"}
    return sb


@app.delete("/sandboxes/{sandbox_id}", summary="Delete sandbox")
async def delete_sandbox(sandbox_id: str):
    if sandbox_id in ACTIVE_SANDBOXES:
        del ACTIVE_SANDBOXES[sandbox_id]
    return {"id": sandbox_id, "status": "Terminated"}


@app.get("/sandboxes/{sandbox_id}/endpoints/{port}", summary="Get sandbox endpoint")
async def get_sandbox_endpoint(sandbox_id: str, port: int, request: Request):
    host = request.headers.get("host", f"127.0.0.1:{port}")
    return {
        "endpoint": host,
        "port": port,
        "protocol": "http",
    }


# Execd Command Execution API
@app.post("/command", summary="Execute shell command")
@app.post("/execute", summary="Execute command alias")
async def run_command_endpoint(req: RunCommandBody, request: Request):
    base_dir = get_base_dir()
    cmd = req.command or (" ".join(req.argv) if req.argv else "true")
    cwd = req.cwd or base_dir
    if not os.path.isabs(cwd):
        cwd = os.path.join(base_dir, cwd)
    os.makedirs(cwd, exist_ok=True)

    # Calculate timeout in seconds
    timeout_sec = 300.0
    if req.timeout is not None:
        timeout_sec = req.timeout / 1000.0 if req.timeout > 1000 else req.timeout

    env = os.environ.copy()
    if req.envs:
        env.update(req.envs)

    accept = request.headers.get("accept", "")
    is_sse = "text/event-stream" in accept

    async def execute_process():
        try:
            proc = await asyncio.create_subprocess_shell(
                cmd,
                cwd=cwd,
                stdin=asyncio.subprocess.DEVNULL,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
            )
            try:
                stdout_bytes, stderr_bytes = await asyncio.wait_for(
                    proc.communicate(), timeout=timeout_sec
                )
                return (
                    stdout_bytes.decode(errors="replace"),
                    stderr_bytes.decode(errors="replace"),
                    proc.returncode if proc.returncode is not None else 0,
                    False,
                )
            except asyncio.TimeoutError:
                try:
                    proc.kill()
                    await proc.wait()
                except Exception:
                    pass
                return (
                    "",
                    f"Command exceeded timeout limit of {timeout_sec}s",
                    TIMEOUT_EXIT_CODE,
                    True,
                )
        except Exception as exc:
            return "", f"Execution error: {type(exc).__name__}: {exc}", 1, False

    if is_sse:
        async def event_generator():
            yield f'data: {json.dumps({"type": "init", "timestamp": int(time.time()*1000)})}\n\n'
            stdout, stderr, exit_code, timed_out = await execute_process()
            if stdout:
                yield f'data: {json.dumps({"type": "stdout", "text": stdout, "timestamp": int(time.time()*1000)})}\n\n'
            if stderr:
                yield f'data: {json.dumps({"type": "stderr", "text": stderr, "timestamp": int(time.time()*1000)})}\n\n'
            yield f'data: {json.dumps({"type": "execution_complete", "exit_code": exit_code, "timed_out": timed_out, "timestamp": int(time.time()*1000)})}\n\n'

        return StreamingResponse(event_generator(), media_type="text/event-stream")

    # Regular JSON response
    stdout, stderr, exit_code, timed_out = await execute_process()
    return {
        "stdout": stdout,
        "stderr": stderr,
        "exit_code": exit_code,
        "timed_out": timed_out,
        "complete": True,
    }


# Execd Filesystem APIs
@app.post("/files/upload", summary="Upload file")
@app.post("/upload", summary="Upload file alias")
async def upload_file(
    file: UploadFile = File(...),
    path: str | None = Query(None),
):
    target_rel = path or file.filename or "uploaded_file"
    try:
        full_path = get_safe_path(target_rel)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        return {"status": "ok", "path": target_rel, "size": os.path.getsize(full_path)}
    except ValueError:
        return JSONResponse(status_code=403, content={"message": "Access denied"})
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/files/download", summary="Download file via query path")
async def download_file_query(path: str = Query(...)):
    try:
        full_path = get_safe_path(path)
    except ValueError:
        return JSONResponse(status_code=403, content={"message": "Access denied"})

    if not os.path.isfile(full_path):
        return JSONResponse(status_code=404, content={"message": "File not found"})

    return FileResponse(full_path, filename=os.path.basename(full_path))


@app.get("/download/{file_path:path}", summary="Download file via URL path")
async def download_file_path(file_path: str):
    return await download_file_query(path=file_path)


@app.get("/files/info", summary="File info")
@app.get("/exists/{file_path:path}", summary="Check if path exists")
async def check_exists(file_path: str | None = None, path: str | None = Query(None)):
    target = path or file_path or ""
    try:
        full_path = get_safe_path(target)
    except ValueError:
        return JSONResponse(status_code=403, content={"message": "Access denied"})
    exists = os.path.exists(full_path)
    size = os.path.getsize(full_path) if os.path.isfile(full_path) else 0
    return {"exists": exists, "path": target, "size": size}


@app.get("/list/{file_path:path}", summary="List directory contents")
async def list_dir_endpoint(file_path: str = ""):
    try:
        full_path = get_safe_path(file_path)
    except ValueError:
        return JSONResponse(status_code=403, content={"message": "Access denied"})

    if not os.path.isdir(full_path):
        return JSONResponse(status_code=404, content={"message": "Directory not found"})

    items = []
    for entry in os.scandir(full_path):
        items.append({
            "name": entry.name,
            "is_dir": entry.is_dir(),
            "size": entry.stat().st_size if entry.is_file() else 0,
        })
    return {"items": items}


@app.delete("/files/delete", summary="Delete file")
@app.delete("/delete/{file_path:path}", summary="Delete file alias")
async def delete_file_endpoint(file_path: str | None = None, path: str | None = Query(None)):
    target = path or file_path or ""
    try:
        full_path = get_safe_path(target)
    except ValueError:
        return JSONResponse(status_code=403, content={"message": "Access denied"})

    if not os.path.exists(full_path):
        return JSONResponse(status_code=404, content={"message": "Not found"})

    if os.path.isdir(full_path):
        shutil.rmtree(full_path)
    else:
        os.remove(full_path)
    return {"status": "ok", "deleted": target}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8889"))
    uvicorn.run("deploy.opensandbox.server:app", host="0.0.0.0", port=port, log_level="info")
