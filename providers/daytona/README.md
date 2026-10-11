# Daytona Development Workspaces & Sandboxes

## Overview & Architecture
Daytona is an open-source development environment orchestrator and workspace manager. While originally created to automate self-hosted developer workspaces, it provides a comprehensive infrastructure for agentic execution where agents require a full repository checkout, language server (LSP), and long-lived development environment.

### Core Primitives
- **Workspace**: A containerized Linux environment backed by Docker, Podman, or Kubernetes.
- **Provider System**: Can target local machine Docker, remote SSH servers, AWS, GCP, Azure, or DigitalOcean.
- **Git Integration**: Natively clones repositories, configures branch checkouts, and sets up project dependencies.
- **LSP / Language Server Support**: Exposes Language Server Protocol endpoints so agents can perform semantic code navigation (go-to-definition, find-references, autocompletion).

### Lifecycle & Billing
- **Self-Hosted / Open-Source**: Free and self-managed on your own infrastructure (Docker/K8s).
- **Daytona Cloud**: Managed offering billed by workspace compute hours.
- **Statefulness**: Workspaces are completely stateful; can be stopped, resumed, snapshotted, and destroyed.

### API & CLI Capabilities
| Feature | Supported | Details |
| :--- | :--- | :--- |
| **Shell Access** | Yes | Full bash / zsh execution via `daytona ssh` or SDK exec |
| **Filesystem Persistence** | Yes | Persistent disk volumes across workspace stop/start |
| **Git & Repo Tooling** | Exceptional | Built-in git credentials and workspace scaffolding |
| **Bidirectional File I/O** | Yes | Fast file upload/download via Daytona agent daemon |
| **Network Egress** | Yes | Unrestricted outbound access (or governed by host Docker network) |
| **CLI** | Yes | `daytona` CLI installed at `~/.local/bin/daytona` |

### Key Benchmark Metrics
- **Cold-Start Latency**: ~3s–10s (dependent on container image pull and repo clone).
- **Warm Shell Latency**: ~50ms–150ms.
- **Persistence**: 100% persistent across workspace reboots.
