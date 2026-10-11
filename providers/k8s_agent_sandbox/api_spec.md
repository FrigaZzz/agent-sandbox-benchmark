# Kubernetes-SIGs Agent-Sandbox: API Specification & Wire Protocol

The Kubernetes Agent Sandbox exposes an HTTP REST daemon protocol (default port `8888`) implemented inside the sandbox pod / container.

---

## 1. Health & Identity Check

### `GET /`
Verifies that the sandbox runtime is active and reports the underlying runtime identity.

#### Response (`200 OK`)
```json
{
  "status": "ok",
  "message": "Sandbox Runtime is active.",
  "runtime": "kubernetes-sigs/agent-sandbox"
}
```

---

## 2. Command Execution

### `POST /execute`
Executes an arbitrary shell command in the sandbox's working directory (`/tmp/agent-sandbox-data/`).

#### Request Body
```json
{
  "command": "python3 -c \"print('Hello from Agent Sandbox')\"",
  "timeout_seconds": 30.0
}
```

#### Response (`200 OK`)
```json
{
  "stdout": "Hello from Agent Sandbox\n",
  "stderr": "",
  "exit_code": 0,
  "timed_out": false
}
```

#### Timeout Handling
If the command exceeds `timeout_seconds`, the process tree is killed via `SIGKILL` and returns GNU exit code `124`:
```json
{
  "stdout": "",
  "stderr": "Command exceeded timeout limit of 30.0s",
  "exit_code": 124,
  "timed_out": true
}
```

---

## 3. Bidirectional File Management

### `POST /upload`
Uploads a file to the sandbox working directory using `multipart/form-data`.

#### Request
- **Header**: `Content-Type: multipart/form-data`
- **Field**: `file` (binary payload, preserving relative path in filename)

#### Response (`200 OK`)
```json
{
  "status": "ok",
  "filename": "data/sales_q3.csv",
  "size": 40960
}
```

---

### `GET /download/{file_path}`
Downloads a file from the sandbox working directory.

#### Path Parameter
- `file_path`: Relative path to the target file inside `/tmp/agent-sandbox-data/`.

#### Response
- Status: `200 OK`
- Body: Raw file binary stream (`application/octet-stream`).
- Status: `404 Not Found` if file does not exist.
- Status: `403 Forbidden` if path attempts path traversal (`../`).

---

### `GET /list/{dir_path}`
Lists files and directories inside a relative path within the sandbox.

#### Response (`200 OK`)
```json
{
  "path": "data",
  "files": [
    {"name": "sales_q3.csv", "is_dir": false, "size": 40960},
    {"name": "reports", "is_dir": true, "size": 4096}
  ]
}
```

---

### `GET /exists/{file_path}`
Checks whether a file or directory exists.

#### Response (`200 OK`)
```json
{
  "path": "reports/summary.md",
  "exists": true,
  "is_file": true
}
```

---

### `DELETE /delete/{file_path}`
Deletes a file or directory from the sandbox.

#### Response (`200 OK`)
```json
{
  "status": "ok",
  "deleted": "data/sales_q3.csv"
}
```

---

## 4. Python SDK Integration (`k8s_agent_sandbox`)

The official SDK supports both **in-cluster discovery** via kubeconfig and **direct connection** for sidecar or standalone container setups:

```python
from k8s_agent_sandbox.sandbox import Sandbox
from k8s_agent_sandbox.models import SandboxDirectConnectionConfig

# Connect directly to a running sandbox container or sidecar
config = SandboxDirectConnectionConfig(
    api_url="http://localhost:8888",
    auth_token=None,
)
sandbox = Sandbox(sandbox_id="agent-run-101", direct_config=config)

# Execute command
res = sandbox.execute_command("python3 -c \"import sys; print(sys.version)\"")
print(res.stdout)

# Upload and process file
sandbox.upload_file("input.txt", b"Hello, World!")
sandbox.execute_command("cat input.txt > output.txt")

# Download result
content = sandbox.download_file("output.txt")
print(content.decode())
```
