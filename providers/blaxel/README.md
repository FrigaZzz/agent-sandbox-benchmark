# Blaxel Sandbox

## Overview & Architecture
Blaxel provides high-performance, developer-friendly serverless sandboxes designed specifically for autonomous AI agents. Sandboxes are full Linux environments that can be provisioned instantly and kept alive across conversation turns, with direct REST/gRPC filesystem and process control APIs.

### Core Primitives
- **`SandboxInstance`**: A named, isolated Linux sandbox instance (`SandboxInstance.create_if_not_exists`).
- **Filesystem API (`sandbox.fs`)**: Native binary read, write, directory creation, and deletion without needing base64 wrapper overhead.
- **Process API (`sandbox.process`)**: Asynchronous process execution (`exec`), waiting (`wait`), status querying (`get`), and termination (`kill`).
- **Named Process Identifiers**: Allows starting long-running background tasks and reconnecting to them by name.

### Lifecycle & Billing
- **Billing Model**: Billed per second of active sandbox lifetime, based on configured memory (e.g. 1024 MB to 16 GB) and vCPU.
- **Session Scoping**: Sandboxes can be named deterministically based on agent conversation ID / user ID, enabling natural state persistence across turns.
- **TTL**: Configurable time-to-live (e.g. `blaxel_ttl="24h"` or `"15m"`).

### API & CLI Capabilities
| Feature | Supported | Details |
| :--- | :--- | :--- |
| **Python / Shell Execution** | Yes | Full bash / Python execution via `process.exec` |
| **Bidirectional File Transfer** | Yes | Direct binary transport (`fs.write_binary` and `fs.read_binary`) |
| **Filesystem Persistence** | Yes | Persistent across multiple executions within the same sandbox |
| **Custom Images** | Yes | Configurable container image (default `blaxel/py-app:latest`) |
| **Process Management** | Yes | Non-blocking execution, polling, kill on timeout |
| **Network Egress** | Yes | Full outbound internet access |
| **CLI** | Yes | `bl` CLI installed at `~/.local/bin/bl` |

### Key Benchmark Metrics
- **Cold-Start Latency**: ~1.5s–3s for new instance creation.
- **Warm Process Latency**: ~300ms–800ms.
- **Binary I/O Performance**: High throughput native file streaming.
