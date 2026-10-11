# Databricks AI Sandbox Runtimes

Databricks provides two distinct code execution and sandboxing paradigms for AI agents and data engineers:

1. **Databricks Serverless Sandboxes (Dedicated MicroVM)**: Dedicated Linux microVMs with 4 vCPUs, 8 GB RAM, `/bin/bash` shell access, and outbound network access, managed under Databricks Apps.
2. **Databricks Unity Catalog MCP Python Execution (`system.ai.python_exec`)**: A stateless Python function executed over serverless SQL warehouses and MCP JSON-RPC, governed by strict lakehouse data boundaries.

---

## Architecture 1: Databricks Serverless Sandboxes (Dedicated MicroVM)

### Overview
Documented in the [official Sandbox guide](https://docs.databricks.com/aws/en/compute/serverless/sandbox), Databricks Serverless Sandboxes are isolated execution environments for dynamic code and agent workflows. See the [dedicated integration specification](../databricks_sandbox/SPEC.md) for current scope and retained evidence.

### Specifications & Hardware
- **Compute Sizing**: 4 vCPUs, 8 GB RAM per microVM instance.
- **Operating Environment**: Full Linux container runtime with pre-installed developer tooling (Python, Node.js, Rust, Databricks CLI).
- **Network Egress**: Outbound network allowed (can download external APIs and datasets such as USGS earthquake feeds, PyPI packages, etc.).
- **Filesystem**: Persistent workspace disk scoped to the sandbox session.
- **Observability**: Integrated into the **Databricks Apps** section in the workspace UI, enabling compute auditing, logs inspection, and resource tracking.

### CLI Workflows
```bash
# Register SSH key with workspace
databricks sandbox register

# Provision a new sandbox (becomes default)
databricks sandbox create --name agent-sandbox

# SSH directly into the sandbox
databricks sandbox ssh agent-sandbox

# Inspect active sandboxes
databricks sandbox list

# Teardown sandbox
databricks sandbox delete agent-sandbox
```

### Python SDK Integration (`w.sandbox`)
```python
import base64
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sandbox import Sandbox

w = WorkspaceClient()

# 1. Provision sandbox
created = w.sandbox.create_sandbox(
    sandbox=Sandbox(),
    sandbox_id="agent-sandbox",
)
sandbox_name = created.name

# 2. Stage code and execute via bash shell
code_to_run = """
import urllib.request, json
url = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson'
data = json.loads(urllib.request.urlopen(url).read().decode('utf-8'))
print(f"Features loaded: {len(data['features'])}")
"""

encoded = base64.b64encode(code_to_run.encode('utf-8')).decode('utf-8')

response = w.sandbox.execute_command_sync(
    name=sandbox_name,
    cmd="/bin/bash",
    args=["-c", f"echo '{encoded}' | base64 --decode > task.py && python3 task.py"]
)

print(response.stdout)
```

### Activation Note
The Serverless Sandbox feature is currently in preview. To activate on a workspace:
1. Navigate to **Workspace Settings** -> **Previews** in your own Databricks workspace.
2. Enable the **"Databricks Sandboxes"** toggle.

---

## Architecture 2: Unity Catalog MCP Python Execution (`system.ai.python_exec`)

### Overview
A managed, stateless Python execution tool exposed natively via Unity Catalog functions and the Model Context Protocol (MCP) endpoint (`/api/2.0/mcp/functions/system/ai/python_exec`).

### Core Characteristics
- **Transport**: Invoked via SQL statement (`SELECT system.ai.python_exec(:code)`) on Databricks Serverless SQL Warehouses or over Anthropic MCP tool envelopes.
- **Stateless Filesystem**: No persistent disk. File write operations are restricted or discarded at invocation end.
- **Zero Outbound Internet**: Outbound egress is strictly disabled to prevent exfiltration outside the Unity Catalog perimeter.
- **Security**: Sandboxed Python AST execution preventing arbitrary system calls.
- **Availability**: depends on workspace previews, permissions and the execution surface; retained prerequisite failures are reported separately.

### Empirical Benchmarks (`system.ai.python_exec`)
From our live runs (`reports/data/legacy/databricks_live.json`):
- **Cold Start**: 4.15s (Serverless SQL Warehouse statement compilation + execution)
- **CPU Math Compute**: 1.22s (148k prime sieve calculation)
- **Memory Ceiling**: Bounded within UDF container constraints
- **Disk I/O**: Forbidden (stateless execution throws error on file I/O)
- **Network Isolation**: Strict zero-egress verified (outbound requests blocked)
- **Cost**: ~$0.000025 per second compute billing
