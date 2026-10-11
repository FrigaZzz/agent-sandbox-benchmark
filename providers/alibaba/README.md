# Alibaba Cloud AgentRun & OpenSandbox

## Overview & Architecture
Alibaba Cloud's **AgentRun** platform provides serverless infrastructure for enterprise Agentic AI. At its core is **OpenSandbox** (an open-source project created and maintained by Alibaba under `opensandbox-group/OpenSandbox`), designed to offer standardized containerized runtime environments for agents.

### Core Primitives
- **Code Interpreter Sandbox**: An isolated runtime for executing untrusted model-generated code (Python, Node.js, Go) without endangering host systems.
- **Browser Sandbox**: A headless browser runtime (Playwright/Chrome) for web interaction and DOM automation.
- **All-In-One (AIO) Sandbox**: A combined environment providing both headless browser navigation and code interpretation in a unified session.
- **Dynamic Skill Mounting**: Capability to mount modular agent skills (`SKILL.md`) stored in Alibaba Cloud OSS directly into the sandbox runtime upon provisioning.

### Runtimes & Dual Architecture
- **Docker**: For local development, testing, and isolated single-node runners.
- **Kubernetes (K8s)**: For production clustering, multi-tenant isolation, and high concurrency.

### Lifecycle & Billing
- **Billing Model**: Serverless compute-seconds in Alibaba Cloud AgentRun; completely free and self-hosted via OpenSandbox.
- **Session Reusability**: Sandboxes can be kept alive and reused across multi-turn agent threads.

### API & CLI Capabilities
| Feature | Supported | Details |
| :--- | :--- | :--- |
| **Multi-Language Runtimes** | Yes | Python, Node.js, Java, Go |
| **Shell Access** | Yes | Full container bash execution |
| **Bidirectional File I/O** | Yes | File upload and download via OpenSandbox REST API / SDK |
| **Browser Integration** | Yes | Integrated Chromium / Playwright in AIO mode |
| **Network Egress** | Configurable | Configurable security group rules |

### Key Benchmark Metrics
- **Cold-Start Latency**: ~1.5s–3s (Kubernetes pod scheduling) / ~500ms (pre-warmed pools).
- **Execution Overhead**: Direct container runtime speed.
