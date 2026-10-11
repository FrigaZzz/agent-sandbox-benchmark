# Alibaba OpenSandbox & AgentRun: API Specification & Wire Protocol

Alibaba Cloud's **AgentRun** platform and open-source **OpenSandbox** (`opensandbox-group/OpenSandbox`) provide containerized and microVM execution environments for Agentic AI.

---

## 1. CLI Management & Tools

### Alibaba Cloud CLI (`aliyun`)
Installed version: `3.5.1` (via Homebrew `aliyun-cli`).
Management commands for AgentRun workloads:
```bash
# Configure credentials (AccessKey ID & Secret)
aliyun configure

# List AgentRun resources
aliyun agentrun list-flows
aliyun agentrun get-agent-runtime --RuntimeId <id>
```

### OpenSandbox Python SDK (`opensandbox`)
Installed version: `1.1.1` (via PyPI `opensandbox`).
Official SDK module structure:
- `opensandbox.Sandbox`: Lifecycle management (`create`, `connect`, `kill`, `pause`, `resume`)
- `opensandbox.config.connection.ConnectionConfig`: Endpoint, protocol, auth token, and client options
- `opensandbox.models.WriteEntry`: File write model with permissions and encoding
- `opensandbox.services.command.Commands`: Shell and argv execution with streaming logs
- `opensandbox.services.filesystem.Filesystem`: Directory listing, file read/write/delete

---

## 2. OpenSandbox Wire Protocol

The OpenSandbox execution daemon (`execd`) and lifecycle controller expose standard REST APIs.

### Health Check
`GET /health` or `GET /`
```json
{
  "status": "ok",
  "message": "OpenSandbox runtime active.",
  "runtime": "alibaba/opensandbox"
}
```

### Sandbox Lifecycle
- `POST /sandboxes`: Provision a sandbox instance with image, entrypoint, resources, and timeout.
  ```json
  {
    "image": "opensandbox/code-interpreter:v1.0.2",
    "resource": {"cpu": "1", "memory": "2Gi"},
    "timeout": 600
  }
  ```
  Returns:
  ```json
  {
    "id": "sb-3a7b9c1d2e",
    "status": "Running",
    "created_at": 1728810000.0,
    "expires_at": 1728810600.0
  }
  ```
- `GET /sandboxes/{id}`: Inspect runtime status and expiration.
- `DELETE /sandboxes/{id}`: Terminate sandbox and reclaim resources.
- `GET /sandboxes/{id}/endpoints/{port}`: Query ingress/internal endpoint for target port.

### Command Execution
`POST /command` or `POST /execute`
#### Request:
```json
{
  "command": "python3 -c \"print('Hello from OpenSandbox')\"",
  "cwd": "/workspace",
  "timeout": 30.0
}
```

#### Response (JSON mode):
```json
{
  "stdout": "Hello from OpenSandbox\n",
  "stderr": "",
  "exit_code": 0,
  "timed_out": false,
  "complete": true
}
```

#### Timeout Handling:
Commands exceeding the specified timeout are terminated with GNU exit code `124`:
```json
{
  "stdout": "",
  "stderr": "Command exceeded timeout limit of 30.0s",
  "exit_code": 124,
  "timed_out": true,
  "complete": true
}
```

#### SSE Streaming Mode:
When `Accept: text/event-stream` is requested, the endpoint streams lifecycle events:
```text
data: {"type": "init", "timestamp": 1728810001000}

data: {"type": "stdout", "text": "Hello from OpenSandbox\n", "timestamp": 1728810001050}

data: {"type": "execution_complete", "exit_code": 0, "timed_out": false, "timestamp": 1728810001060}
```

### Filesystem Operations
- `POST /files/upload` (multipart form): Staging input artifacts or scripts into sandbox paths.
- `GET /files/download?path={path}`: Retrieving generated outputs and binary artifacts.
- `GET /files/info?path={path}`: Verifying file existence, mode, and byte size.
- `DELETE /files/delete?path={path}`: Removing temporary or sensitive files.

---

## 3. Benchmark Adapter Architecture

The adapter in `src/core/providers/alibaba.py` implements `ExecutionBackend`:
- **Remote Cloud Mode**: Connects to an existing Alibaba Cloud AgentRun or self-hosted OpenSandbox instance via `OPENSANDBOX_URL`, `OPENSANDBOX_API_KEY`, or `AGENTRUN_SANDBOX_ENDPOINT`.
- **Managed Auto-Spawn Mode**: When running standalone benchmarks or unit tests without an active remote cluster, automatically starts a local OpenSandbox server instance (`deploy/opensandbox/server.py`) with full lifecycle and execution semantics.
