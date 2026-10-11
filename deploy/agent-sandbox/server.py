"""Official kubernetes-sigs/agent-sandbox Python runtime server implementation.

Adheres strictly to the specification in:
https://github.com/kubernetes-sigs/agent-sandbox/tree/main/examples/python-runtime-sandbox
"""
import asyncio
import logging
import math
import os
import shutil
import subprocess
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

# GNU coreutils timeout exit code convention
TIMEOUT_EXIT_CODE = 124


class ExecuteRequest(BaseModel):
    command: str
    timeout_seconds: float | None = Field(default=None, gt=0)


class ExecuteResponse(BaseModel):
    stdout: str
    stderr: str
    exit_code: int
    timed_out: bool = False


def get_base_dir() -> str:
    """Base directory where commands execute and files are confined."""
    base = os.environ.get("SANDBOX_BASE_DIR", "").strip() or "/tmp/agent-sandbox-data"
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
    title="Kubernetes-SIGs Agent Sandbox Runtime",
    description="Official API server for executing agent commands and managing files in a secure sandbox.",
    version="1.0.0",
)


@app.get("/", summary="Health Check")
async def health_check():
    return {"status": "ok", "message": "Sandbox Runtime is active.", "runtime": "kubernetes-sigs/agent-sandbox"}


@app.post("/execute", summary="Execute a shell command", response_model=ExecuteResponse)
async def execute_command(req: ExecuteRequest):
    base_dir = get_base_dir()
    timeout = req.timeout_seconds or 300.0

    try:
        proc = await asyncio.create_subprocess_shell(
            req.command,
            cwd=base_dir,
            stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                proc.communicate(), timeout=timeout
            )
            return ExecuteResponse(
                stdout=stdout_bytes.decode(errors="replace"),
                stderr=stderr_bytes.decode(errors="replace"),
                exit_code=proc.returncode if proc.returncode is not None else 0,
                timed_out=False,
            )
        except asyncio.TimeoutError:
            try:
                proc.kill()
                await proc.wait()
            except Exception:
                pass
            return ExecuteResponse(
                stdout="",
                stderr=f"Command exceeded timeout limit of {timeout}s",
                exit_code=TIMEOUT_EXIT_CODE,
                timed_out=True,
            )
    except Exception as exc:
        return ExecuteResponse(
            stdout="",
            stderr=f"Execution error: {type(exc).__name__}: {exc}",
            exit_code=1,
            timed_out=False,
        )


@app.post("/upload", summary="Upload a file to the sandbox")
async def upload_file(file: UploadFile = File(...)):
    try:
        full_path = get_safe_path(file.filename)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        return {"status": "ok", "filename": file.filename, "size": os.path.getsize(full_path)}
    except ValueError:
        return JSONResponse(status_code=403, content={"message": "Access denied"})
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/download/{file_path:path}", summary="Download a file from the sandbox")
async def download_file(file_path: str):
    try:
        full_path = get_safe_path(file_path)
    except ValueError:
        return JSONResponse(status_code=403, content={"message": "Access denied"})

    if not os.path.isfile(full_path):
        return JSONResponse(status_code=404, content={"message": "File not found"})

    return FileResponse(full_path, filename=os.path.basename(full_path))


@app.get("/list/{file_path:path}", summary="List files in a directory")
async def list_files(file_path: str = ""):
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


@app.get("/exists/{file_path:path}", summary="Check if path exists")
async def exists(file_path: str):
    try:
        full_path = get_safe_path(file_path)
    except ValueError:
        return JSONResponse(status_code=403, content={"message": "Access denied"})
    return {"exists": os.path.exists(full_path)}


@app.delete("/delete/{file_path:path}", summary="Delete file or directory")
async def delete_file(file_path: str):
    try:
        full_path = get_safe_path(file_path)
    except ValueError:
        return JSONResponse(status_code=403, content={"message": "Access denied"})

    if not os.path.exists(full_path):
        return JSONResponse(status_code=404, content={"message": "Not found"})

    if os.path.isdir(full_path):
        shutil.rmtree(full_path)
    else:
        os.remove(full_path)
    return {"status": "ok", "deleted": file_path}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8888"))
    uvicorn.run("deploy.agent-sandbox.server:app", host="0.0.0.0", port=port, log_level="info")
