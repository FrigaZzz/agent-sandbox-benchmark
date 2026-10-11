# Modal Sandbox

## Overview & Architecture
Modal provides high-performance serverless containers and sandboxes built on top of customized container virtualization (with gVisor and custom memory snapshotting). It is heavily optimized for sub-second startup times, elastic scale, and hardware acceleration (CPUs, GPUs, TPUs).

### Core Primitives
- **`modal.Sandbox`**: An isolated container created on demand using `modal.Sandbox.create()`.
- **`modal.Image`**: Definition of Debian/Ubuntu images with arbitrary `pip_install`, `apt_install`, and environment variables, built and cached in Modal's content-addressable registry.
- **`modal.Volume` / `modal.NetworkFileSystem`**: Persistent disks that can be mounted into one or more sandboxes simultaneously.
- **Tunnels & Ports**: Expose TCP/HTTP ports directly to public endpoints or secure tunnels.

### Lifecycle & Billing
- **Billing Model**: Per-millisecond active compute pricing based on vCPU, RAM (GB-seconds), and optional GPU tiers (T4, L4, A100, H100).
- **Startup Mechanics**: Uses image caching and container snapshots for sub-second cold starts (~500ms to 1.5s).
- **Auto-Termination**: Sandboxes automatically terminate when the entrypoint process finishes or upon hitting `timeout` (seconds).

### API & CLI Capabilities
| Feature | Supported | Details |
| :--- | :--- | :--- |
| **Python / Shell Execution** | Yes | Entrypoint command or interactive `sandbox.exec("bash", "-c", "...")` |
| **Streaming Output** | Yes | `sandbox.stdout.read()` and `sandbox.stderr.read()` stream in real time |
| **Bidirectional File I/O** | Yes | `sandbox.open("/path", "wb")` and `sandbox.open("/path", "rb")` |
| **Custom Dependencies** | Yes | Defined declaratively on the `modal.Image` object or installed dynamically via apt/pip |
| **Hardware Flexibility** | Exceptional | 0.1 to 64 vCPUs, up to 384 GB RAM, full range of GPUs |
| **Network Egress** | Yes | Unrestricted outbound internet by default; custom proxy/network policies available |
| **CLI** | Yes | `modal` CLI (inspect sandboxes with `modal sandbox list`) |

### Key Benchmark Metrics
- **Cold-Start Latency**: ~800ms–1.5s with cached images.
- **Warm Execution Latency**: Immediate via `exec`.
- **I/O Throughput**: NVMe-backed local storage + network file systems.
