# E2B Code Interpreter & Sandboxes

## Overview & Architecture
E2B (Execute to Build) is an open-source and cloud infrastructure platform purpose-built for AI agents. It uses **Firecracker microVMs** running on bare-metal servers to provide hardware-isolated Linux environments with sub-second provisioning.

### Core Primitives
- **`Sandbox`**: Lightweight microVM instance providing isolated execution.
- **Code Interpreter SDK (`e2b_code_interpreter`)**: Dedicated wrapper containing a persistent Jupyter kernel, enabling incremental Python state (variables and imported modules survive across consecutive calls).
- **Filesystem API (`sandbox.files`)**: Direct methods `write(path, data)`, `read(path)`, `list(path)`, `make_dir(path)`.
- **Command API (`sandbox.commands`)**: Direct shell execution `run("bash command")` with stdout/stderr streaming.
- **Rich Artifacts**: Native extraction of charts, SVG, PNG, and HTML displays produced by matplotlib, plotly, etc.

### Lifecycle & Billing
- **Billing Model**: Per-second billing for microVM uptime (default tier ~2 vCPU, 512MB RAM; customizable via custom templates).
- **Auto-Kill Timeout**: MicroVMs auto-pause or terminate after a configured idle timeout (e.g. 5–60 minutes).
- **Custom Templates**: Build custom environments using Dockerfiles via `e2b template build`.

### API & CLI Capabilities
| Feature | Supported | Details |
| :--- | :--- | :--- |
| **Python Execution** | Yes | Jupyter-style stateful execution via `sandbox.run_code()` |
| **Shell Access** | Yes | `sandbox.commands.run("...")` with background support |
| **Bidirectional File Transfer** | Yes | Fast file upload and download via API |
| **Rich Visualization Outputs** | Yes | Extracts matplotlib/seaborn figures automatically |
| **Network Egress** | Configurable | Can enable/disable internet access per template |
| **Google ADK Integration** | Yes | Direct integration available via E2B toolset |
| **CLI** | Yes | `e2b` CLI installed at `~/.local/bin/e2b` |

### Key Benchmark Metrics
- **Cold-Start Latency**: ~300ms–800ms to spin up a Firecracker microVM.
- **Warm Cell Latency**: ~100ms–200ms for consecutive Python executions.
- **Memory Overhead**: Lightweight base footprint (~150MB baseline).
