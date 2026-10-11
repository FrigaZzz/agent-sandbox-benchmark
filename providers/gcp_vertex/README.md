# GCP Agent Sandbox (Vertex AI Agent Engine)

## Overview & Architecture
Google Cloud Vertex AI Agent Platform provides managed sandboxes designed for enterprise agentic execution. It integrates natively with **Cloud KMS Customer-Managed Encryption Keys (CMEK)**, allowing execution environments and persistent state to be encrypted with organizational keys.

### Core Primitives
- **Parent Runtime**: A `reasoningEngines` resource (`projects/<PROJECT_NUMBER>/locations/<LOCATION>/reasoningEngines/<ENGINE_ID>`) acts as the parent container/lifecycle controller for sandboxes.
- **Sandbox Environment Templates**: Reusable templates specifying base images, resource allocations, and network configurations.
- **Sandbox Instance**: Ephemeral or session-scoped isolated environment with execution endpoints for Python and bash.

### Lifecycle & Billing
- **Billing Model**: Per-second billing while active.
- **Auto-Cleanup / Safety**: Supports short TTLs (default 900s, max 3600s). Local ledger tracks started sandboxes to prevent orphan billing.
- **CMEK Encryption**: Dual service agent setup:
  - `service-<PROJECT_NUMBER>@gcp-sa-aiplatform.iam.gserviceaccount.com`
  - `service-<PROJECT_NUMBER>@gcp-sa-aiplatform-cc.iam.gserviceaccount.com`
  Both require `roles/cloudkms.cryptoKeyEncrypterDecrypter`.

### API & CLI Capabilities
| Feature | Supported | Details |
| :--- | :--- | :--- |
| **Python Execution** | Yes | `agent-sandbox exec --code "..."` or SDK `code_execution` |
| **Shell Access** | Yes | `agent-sandbox bash -c "..."` |
| **Bidirectional File I/O** | Yes | `agent-sandbox upload <local> <remote>` / `agent-sandbox download <remote> <local>` |
| **Directory Download** | Yes | Automatically streams directories as `.tar.gz` |
| **Session Persistence** | Yes | State persists while sandbox instance is alive |
| **Network Egress** | Yes | Configurable via VPC Service Controls / VPC network |
| **CLI** | Yes | `agent-sandbox` launcher in `bin/agent-sandbox` |

### Key Benchmark Metrics
- **Cold-Start Latency**: ~3–5s for existing runtime sandbox spawn; ~2m for parent runtime creation.
- **Warm Execution Latency**: ~200–500ms per snippet.
- **File Transfer Speed**: Native gRPC streaming.
