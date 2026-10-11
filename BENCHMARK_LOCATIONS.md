# Benchmark code and data map

All paths below are relative to this repository. Provider specifications distinguish
documented service capabilities from the integration and configuration actually tested.

## Providers

| Backend key | Adapter | Specification and configuration | Retained attempts |
|---|---|---|---|
| `local` | [LocalSubprocessBackend](src/core/providers/local_subprocess.py) | Host subprocess control; no isolation boundary | [Evaluation](reports/data/attempts/local_evaluation.json) · [Historical baseline](reports/data/legacy/local_baseline.json) |
| `alibaba` | [AlibabaBackend](src/core/providers/alibaba.py) | [Specification](providers/alibaba/SPEC.md) · [Configurations](providers/alibaba/tested-configurations.md) | [Evaluation](reports/data/attempts/alibaba_evaluation.json) |
| `k8s_agent_sandbox` | [KubernetesAgentSandboxBackend](src/core/providers/k8s_agent_sandbox.py) | [Specification](providers/k8s_agent_sandbox/SPEC.md) · [Configurations](providers/k8s_agent_sandbox/tested-configurations.md) | [Evaluation](reports/data/attempts/k8s_agent_sandbox_evaluation.json) · [Historical](reports/data/legacy/k8s_agent_sandbox_live.json) |
| `modal` | [ModalBackend](src/core/providers/modal.py) | [Specification](providers/modal/SPEC.md) · [Configurations](providers/modal/tested-configurations.md) | [Evaluation](reports/data/attempts/modal_evaluation.json) · [Burst](reports/data/attempts/modal_burst_evaluation.json) · [Historical](reports/data/legacy/modal_live.json) |
| `e2b` | [E2BBackend](src/core/providers/e2b.py) | [Specification](providers/e2b/SPEC.md) · [Configurations](providers/e2b/tested-configurations.md) | [Evaluation](reports/data/attempts/e2b_evaluation.json) · [Burst](reports/data/attempts/e2b_burst_evaluation.json) · [Historical](reports/data/legacy/e2b_live.json) |
| `blaxel` | [BlaxelBackend](src/core/providers/blaxel.py) | [Specification](providers/blaxel/SPEC.md) · [Configurations](providers/blaxel/tested-configurations.md) | [Evaluation](reports/data/attempts/blaxel_evaluation.json) · [Historical](reports/data/legacy/blaxel_live.json) |
| `gcp_vertex` | [GcpVertexBackend](src/core/providers/gcp_vertex.py) | [Specification](providers/gcp_vertex/SPEC.md) · [Configurations](providers/gcp_vertex/tested-configurations.md) · [CLI contract](providers/gcp_vertex/client-reference.md) | [Evaluation](reports/data/attempts/gcp_vertex_evaluation.json) · [Historical](reports/data/legacy/gcp_vertex_live.json) |
| `databricks` | [DatabricksBackend](src/core/providers/databricks.py) | [Specification](providers/databricks/SPEC.md) · [Configurations](providers/databricks/tested-configurations.md) | [Evaluation](reports/data/attempts/databricks_evaluation.json) · [Historical](reports/data/legacy/databricks_live.json) |
| `databricks_sandbox` | [DatabricksServerlessSandboxBackend](src/core/providers/databricks_sandbox.py) | [Specification](providers/databricks_sandbox/SPEC.md) · [Configurations](providers/databricks_sandbox/tested-configurations.md) | [Evaluation](reports/data/attempts/databricks_sandbox_evaluation.json) · [Historical](reports/data/legacy/databricks_sandbox_live.json) |
| `daytona` | [DaytonaBackend](src/core/providers/daytona.py) | [Specification](providers/daytona/SPEC.md) · [Configurations](providers/daytona/tested-configurations.md) | [Evaluation](reports/data/attempts/daytona_evaluation.json) · [Historical](reports/data/legacy/daytona_live.json) |
| `aws` | [AWSAgentCoreBackend](src/core/providers/aws_agentcore.py) | [Specification](providers/aws/SPEC.md) · [Configurations](providers/aws/tested-configurations.md) | [Evaluation](reports/data/attempts/aws_evaluation.json) · [Historical](reports/data/legacy/aws_live.json) |
| `gemini_tool` | [GeminiToolBackend](src/core/providers/gemini_tool.py) | [Specification](providers/gemini_tool/SPEC.md) · [Configurations](providers/gemini_tool/tested-configurations.md) | [Evaluation](reports/data/attempts/gemini_tool_evaluation.json) · [Historical](reports/data/legacy/gemini_tool_live.json) |
| `openai_tool` | [OpenAIToolBackend](src/core/providers/openai_tool.py) | [Specification](providers/openai_tool/SPEC.md) · [Configurations](providers/openai_tool/tested-configurations.md) | [Evaluation](reports/data/attempts/openai_tool_evaluation.json) |

Each provider directory also includes `spec.json` and generated `tested-configurations.json`.
Raw reports retain failed and prerequisite attempts as well as successful samples.
Endpoint success alone does not establish a remote cloud deployment.

## Workloads and execution

| Component | Location |
|---|---|
| CLI and backend registry | [CLI](src/cli.py) · [Registry](src/core/providers/__init__.py) |
| Backend protocol and result models | [Interface](src/core/interface.py) · [Models](src/core/models.py) |
| All 19 suites and the 11-suite realistic subset | [Suite registry](src/bench/suites/__init__.py) |
| Deterministic data, SQLite, repository, stdout, state, recovery and dependency fixtures | [Workflows](src/bench/suites/workflows.py) |
| Per-attempt execution and correctness checks | [Runner](src/bench/runner.py) · [Validation](src/bench/validation.py) |
| Repeated/concurrent campaigns and provenance | [Campaign harness](src/bench/campaign.py) · [Campaign outputs](reports/data/campaigns/) |
| Guest runtime inventory | [Suite](src/bench/suites/runtime_inventory.py) · [Probe](scripts/runtime_inventory.py) |
| HTTP executors, Docker and Kubernetes examples | [Kubernetes path](deploy/agent-sandbox/) · [OpenSandbox path](deploy/opensandbox/) |
| Non-credential customization examples | [Options](examples/) |
| Regression tests | [Tests](tests/) |
| Retained synthetic output files | [Artifacts](sandbox-results/) |

## Reports and regeneration

| Output | Source / validation |
|---|---|
| [Evidence dashboard](reports/index.html) | [Generator](src/bench/dashboard.py) · [Template](src/bench/dashboard.html) |
| [Preference-driven decision guide](reports/variant/index.html) | [Builder](reports/variant/build_variant.py) · [Guide](reports/variant/README.md) |
| [Findings](reports/docs/findings.md) | [Generator](src/bench/findings.py) · [Insights](src/bench/insights.py) |
| [Leaderboard](reports/docs/leaderboard.md) | [Statistics and renderer](src/bench/leaderboard.py) |
| [Specifications](reports/data/derived/specifications.json) and [summary](reports/data/derived/evaluation-summary.json) | [Specifications generator](src/bench/specifications.py) · [Evidence processor](src/bench/evidence.py) |
| [Methodology](reports/docs/evaluation-framework.md) and [detailed report](reports/docs/detailed-report.md) | [Data notes](reports/docs/data-notes.md) |
| [Schema/link validation](reports/checks/schema-links.json) | [Validator](scripts/validate_evidence.py) |

See [readme.md](readme.md#rebuild-and-validate) for install, rebuild and verification commands.
