# Sandbox Providers & Runtimes: Deep-Dive Evaluation Matrix

## Evidence-first specification index

Use the current specification sheets below rather than assigning old architectural estimates to tested runs. Every provider uses the same [13-feature JSON schema](spec.schema.json); guest inventories use [runtime-inventory.schema.json](runtime-inventory.schema.json). The generated configuration sheets retain requested settings, adapter/SDK identities, raw attempt links and observations. Advanced options are documented, not presumed exercised. For an exhaustive file-by-file mapping across adapters, runners, evaluation reports, tests, and CLIs, see [Benchmark Locations Map](../BENCHMARK_LOCATIONS.md).

| Provider | Current capability/price sheet | Tested configurations |
| :--- | :--- | :--- |
| Modal | [SPEC.md](modal/SPEC.md) · [JSON](modal/spec.json) | [Configuration evidence](modal/tested-configurations.md) |
| Blaxel | [SPEC.md](blaxel/SPEC.md) · [JSON](blaxel/spec.json) | [Configuration evidence](blaxel/tested-configurations.md) |
| E2B | [SPEC.md](e2b/SPEC.md) · [JSON](e2b/spec.json) | [Configuration evidence](e2b/tested-configurations.md) |
| Daytona | [SPEC.md](daytona/SPEC.md) · [JSON](daytona/spec.json) | [Configuration evidence](daytona/tested-configurations.md) |
| GCP Agent Engine | [SPEC.md](gcp_vertex/SPEC.md) · [JSON](gcp_vertex/spec.json) | [Configuration evidence](gcp_vertex/tested-configurations.md) |
| AWS AgentCore | [SPEC.md](aws/SPEC.md) · [JSON](aws/spec.json) | [Configuration evidence](aws/tested-configurations.md) |
| Databricks SQL MCP | [SPEC.md](databricks/SPEC.md) · [JSON](databricks/spec.json) | [Configuration evidence](databricks/tested-configurations.md) |
| Databricks Dedicated Sandbox | [SPEC.md](databricks_sandbox/SPEC.md) · [JSON](databricks_sandbox/spec.json) | [Configuration evidence](databricks_sandbox/tested-configurations.md) |
| Gemini Tool | [SPEC.md](gemini_tool/SPEC.md) · [JSON](gemini_tool/spec.json) | [Configuration evidence](gemini_tool/tested-configurations.md) |
| OpenAI Tool | [SPEC.md](openai_tool/SPEC.md) · [JSON](openai_tool/spec.json) | [Configuration evidence](openai_tool/tested-configurations.md) |
| Alibaba OpenSandbox/AgentRun | [SPEC.md](alibaba/SPEC.md) · [JSON](alibaba/spec.json) | [Configuration evidence](alibaba/tested-configurations.md) |
| Kubernetes/GKE | [SPEC.md](k8s_agent_sandbox/SPEC.md) · [JSON](k8s_agent_sandbox/spec.json) | [Deployment evidence](k8s_agent_sandbox/tested-configurations.md) |

Customization levels distinguish fixed runtime, packages/files, custom image/resources, and infrastructure control. A custom image does not reserve a GPU. GCP default code sandbox, BYOC templates, GKE Agent Sandbox and Compute Engine GPU VMs are separate paths with different setup/billing responsibilities. See [methodology](../reports/docs/evaluation-framework.md).

## Historical overview (not tested configuration attestation)

This directory contains in-depth architectural analyses, API contracts, CLI usage guides, and native runner harnesses for all major sandbox systems evaluated in this benchmark suite.

---

## Evaluated Providers

| Provider | Type | Sandboxing Tech | Shell Access | Filesystem | Network Outbound | Billing Model | CLI / SDK Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Kubernetes-SIGs Agent-Sandbox** | Cloud-Native K8s CRD / Pod | gVisor / Warm-Pooled Singleton Pods | Yes (`bash`) | Persistent per session | Configurable (NetworkPolicy) | Self-hosted compute | `k8s-agent-sandbox` SDK / REST API |
| **GCP Agent Sandbox** | Full Container Sandbox | Vertex AI Agent Engine (CMEK) | Yes (`bash`) | Stateful / Persistent per TTL | Yes (Configurable) | Per-second billed | `agent-sandbox` CLI / `google-cloud-aiplatform` |
| **Modal Sandbox** | Serverless Container | gVisor / Custom Container MicroVM | Yes (`exec`) | Ephemeral / Volume mounts | Yes (Configurable) | Per vCPU/RAM-second | `modal` CLI / `modal` Python SDK |
| **Blaxel Sandbox** | Agentic MicroVM Container | Linux Sandbox Instance | Yes (`exec`) | Persistent per session | Yes | Per-second / Hourly | `bl` CLI / `blaxel` Python SDK |
| **Databricks Serverless SQL MCP** | Managed MCP Python Exec | Unity Catalog Serverless REPL | No | Stateless (Read-only CWD) | Restricted (Zero-Egress) | DBUs (Databricks Units) | `databricks` CLI / Unity Catalog MCP |
| **Databricks Dedicated Sandbox** | Dedicated MicroVM Sandbox | Firecracker MicroVM (4 vCPU / 8 GB) | Yes (`bash`) | Stateful / Persistent (`/tmp`) | Yes (Configurable) | Serverless MicroVM DBUs | Databricks Sandboxes Preview (`w.sandbox`) |
| **E2B Code Interpreter** | Agentic MicroVM | Firecracker MicroVMs | Yes (`commands.run`) | Stateful per session | Yes (Toggleable) | Per-second billed | `e2b` CLI / `e2b_code_interpreter` SDK |
| **Daytona** | Dev Environment Sandbox | Docker / K8s / Linux Containers | Yes (`exec`) | Full Git / Workspace Disk | Yes | Per-workspace instance | `daytona` CLI / `daytona` SDK |
| **AWS Bedrock / Firecracker**| Managed Action / MicroVM | Bedrock Code Interpreter / Firecracker | Bedrock: No (REPL only) | Ephemeral session storage | No (Bedrock) / Yes (EC2/ECS) | Per tool call / Bedrock tokens | `aws` CLI / `boto3` SDK |
| **Alibaba AgentRun** | Serverless AI Sandbox | OpenSandbox (K8s/Docker) | Yes | Stateful per session | Yes | Per compute-second | `aliyun` CLI / OpenSandbox SDK |
| **Gemini Code Execution** | Model-Managed Native Tool | Google Cloud Sandboxed Kernel | No (Python REPL only) | Ephemeral per turn | Disabled | Included in Token Costs | `google-genai` / Vertex AI SDK |
| **OpenAI Code Interpreter** | Model-Managed Native Tool | Isolated Docker Container | No (Python REPL only) | Session-scoped container | Disabled | Session Fee ($0.03) + Tokens | `openai` SDK |

---

## Directory Structure per Provider

Each subfolder contains:
1. `README.md`: Architectural profile, security boundary, network posture, limits, and cost structure.
2. `api_spec.md`: Concrete API endpoints, SDK schemas, payload constraints, and CLI commands.
3. `runner.py`: A native, standalone Python runner exercising the provider's native API directly (independent of abstraction layers).
