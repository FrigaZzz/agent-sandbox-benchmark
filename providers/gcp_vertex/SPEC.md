<!-- COMMON CONTRACT START -->
# Provider contract: GCP Agent Sandbox (`gcp_vertex`)

**Sources reviewed:** 2026-10-13 · **Deployment:** `managed_runtime`

## 1. Executive summary and product boundary

Agent Engine default code sandbox via agent-sandbox CLI; not the model-native Gemini tool, Shell/Computer Use, BYOC, GKE or Compute Engine.

Tested integration: agent-sandbox run with the default Google-managed Python code sandbox under an Agent Engine/Agent Runtime parent. No CPU, RAM, image, GPU or network settings are sent by the adapter. Current official BYOC templates offer image, CPU/memory requests and limits, ports and internet_access, but that separate managed-container path was not tested. GKE Agent Sandbox and Compute Engine GPU VMs are infrastructure alternatives, not capabilities measured for this adapter.

Working adapter: [source](../../src/core/providers/gcp_vertex.py). Historical adapter hashes refer to measured revisions, not necessarily current source.

The preserved dossier describes the dated inspected configuration. New budget/lifecycle guardrails change current adapter defaults without changing historical cohort evidence; see [operations](../../CONTRIBUTING.md).

## 2. Documented contract vs measured adapter

Support describes the platform. Measured describes only a bounded oracle on a recorded setup. Documented-only and unverified entries remain coverage gaps.

| Capability | Platform support | Evidence state | Documented contract / scope | Measured adapter behavior | Sources |
|---|---|---|---|---|---|
| `custom_image` | conditional | Documented | Official BYOC uses an Artifact Registry image and a custom-container sandbox template. The tested default code sandbox has no image selector; local shell/CMEK references explicitly lack end-to-end verification. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [gcp_byoc](#source-gcp_byoc), [adapter](#source-adapter), [local_shell](#source-local_shell) |
| `runtime_packages` | conditional | Measured (bounded fixture) | The report verifies installing one uploaded pure-Python fixture wheel via pip --no-index --no-deps --target, then importing it. This is not online package installation or arbitrary native dependencies. Official code-sandbox docs say own libraries cannot be installed; retain this narrow observed exception rather than generalizing it. BYOC is the documented dependency-customization path. | [dependency_install: 5/5](../../reports/index.html#raw?provider=gcp_vertex&run_id=bench-ca9a72120334), setup `5a61c94c9323` | [report](#source-report), [offline_workload](#source-offline_workload), [gcp_code](#source-gcp_code), [gcp_byoc](#source-gcp_byoc) |
| `cpu_sizing` | conditional | Documented | BYOC templates document CPU requests/limits. The tested adapter requests none; its cost estimate assumes 2 vCPU, not an allocation attestation. A separate 2026-10-01 local probe saw 8 visible CPUs and roughly 2x CPU parallel speedup, neither a contractual allocation nor current-run inventory. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [gcp_byoc](#source-gcp_byoc), [adapter](#source-adapter), [report](#source-report), [local_environment](#source-local_environment) |
| `memory_sizing` | conditional | Documented | BYOC templates document memory requests/limits. The tested adapter requests none; 4 GB in report cost metadata is an estimate. The separate 2026-10-01 reference measured 2 GiB, illustrating why actual current allocation remains unknown. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [gcp_byoc](#source-gcp_byoc), [adapter](#source-adapter), [report](#source-report), [local_environment](#source-local_environment) |
| `gpu` | unknown | Unverified | No GPU requested/tested. Current guest inventory reports nvidia-smi unavailable, which does not establish platform-wide GPU eligibility. Reviewed BYOC example does not establish accelerator support. Compute Engine and compatible GKE GPU deployments are separate choices. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [adapter](#source-adapter), [report](#source-report), [local_environment](#source-local_environment), [gcp_byoc](#source-gcp_byoc), [compute_gpu](#source-compute_gpu), [gke_runtime](#source-gke_runtime) |
| `network_policy` | conditional | Documented | The official code sandbox has no network access; the local probe concurs, contradicting has_internet_access=true in the adapter. BYOC documents egress_control_config.internet_access. The tested adapter sends no network policy and the evaluation campaign does not attest effective policy. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [gcp_code](#source-gcp_code), [gcp_byoc](#source-gcp_byoc), [local_environment](#source-local_environment), [adapter](#source-adapter), [report](#source-report) |
| `persistent_storage` | conditional | Documented | Files/state survive calls within a live sandbox, not deletion. Current lifecycle docs describe filesystem-preserving pause/resume, but code-sandbox snapshots are explicitly unsupported and the adapter uses one-shot deletion. Durable cross-deletion storage and pause/resume were not tested. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [gcp_code](#source-gcp_code), [gcp_lifecycle](#source-gcp_lifecycle), [local_sdk](#source-local_sdk), [local_cli](#source-local_cli), [adapter](#source-adapter) |
| `session_reuse` | supported | Documented | Code execution can reuse state by sandbox ID. Local start/exec supports this, but this adapter calls run for every execution and does not retain a remote session. Current docs advertise up to 14 days; the bundled CLI caps TTL at 3600s and the adapter caps its requested TTL at 900s. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [gcp_code](#source-gcp_code), [local_cli](#source-local_cli), [adapter](#source-adapter) |
| `shell` | supported | Documented | The offline-wheel workload executes a pip subprocess inside the code sandbox. Local tooling also documents bash via the code sandbox. This does not attest a separately provisioned shell-container sandbox under CMEK. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [report](#source-report), [offline_workload](#source-offline_workload), [local_environment](#source-local_environment), [local_shell](#source-local_shell) |
| `file_transfer` | supported | Measured (bounded fixture) | The evaluation verifies a 26900-byte artifact round trip by expected size and SHA-256 and verifies summary.json. The adapter passes --upload and reads output files. Official request/response limit is 100 MB in aggregate; unlimited stdout rendering is not unlimited API payload size. | [artifact_roundtrip: 5/5](../../reports/index.html#raw?provider=gcp_vertex&run_id=bench-508887bd1358), setup `5a61c94c9323`; [data_pipeline: 5/5](../../reports/index.html#raw?provider=gcp_vertex&run_id=bench-c66657311c60), setup `5a61c94c9323` | [report](#source-report), [adapter](#source-adapter), [gcp_code](#source-gcp_code) |
| `ports_preview` | conditional | Documented | BYOC templates document ports. That is not evidence of an automatically public preview URL. The tested code adapter has no port exposure or preview integration. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [gcp_byoc](#source-gcp_byoc), [adapter](#source-adapter) |
| `self_hosting` | unsupported | Documented | This service is Google-managed. A locally running client does not self-host its sandbox. Kubernetes-SIGs/GKE Agent Sandbox and Compute Engine VMs are separate infrastructure deployments. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [gcp_code](#source-gcp_code), [gke_agent](#source-gke_agent), [compute_custom](#source-compute_custom) |
| `cmek` | supported | Documented | CMEK is configured at parent runtime creation and inherited by sandboxes/templates/snapshots for at-rest content, not resource metadata. Local setup observed a need for both Vertex service agents. The saved evaluation lacks parent/key readback and KMS audit evidence, so encryption is not measured by that report. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [gcp_cmek](#source-gcp_cmek), [local_cmek](#source-local_cmek), [report](#source-report) |

## 3. Six residency surfaces

Source: [dated residency audit and original vendor citations](../../reports/docs/eu-data-residency.md). These are documented boundaries/gaps, not measured EU residency or GDPR certification.

| Surface | Documented boundary / verification gap |
|---|---|
| Compute | Five named EU regions plus eu code endpoint; campaign preflight unretained |
| Files / volumes / snapshots / backups | Selected-location at-rest commitments; CMEK scope/parent region constraints apply |
| Stdout / stderr / traces | Blanket operational-log EU-only boundary not established |
| Control plane / metadata | Covered at-rest metadata differs from excluded CMEK metadata |
| Support access / subprocessors | Blanket support-flow EU-only boundary not established |
| External model / API calls | Foundation model endpoint/location configured separately |

Benchmark location/request provenance is recorded separately in [tested configurations](tested-configurations.md).

## 4. Dated pricing and billing units

Allocated Agent Compute vCPU-hours plus Agent Memory GiB-hours; official usage rounded to the nearest second. Separate KMS and other resource costs may apply.

| SKU / resource | Original billing unit | USD list amount | Sources |
|---|---|---:|---|
| Agent Compute, default paid tier | vCPU-hour | 0.085 | [gcp_pricing](#source-gcp_pricing) |
| Agent Memory, default paid tier | GiB-hour | 0.009 | [gcp_pricing](#source-gcp_pricing) |
| Cloud KMS and ancillary resources | applicable resource SKU | Unknown | [gcp_cmek](#source-gcp_cmek), [local_billing](#source-local_billing) |

Reviewed 2026-10-13. Official pricing includes monthly free usage per account of 50 compute hours and 100 GiB-hours of RAM and eligible savings-plan tiers. The report's 2-vCPU/4-GB and $0.000114/second inputs are explicitly estimate_unverified_rates; client wall time is not billable resource time and billing_verified=false. Do not use them as a bill or observed hardware inventory. Runtime-only idle-time wording must not be assumed to apply to sandbox idle time; lifecycle docs say sandboxes are billed while they exist. No historical price increase is asserted without comparable dated evidence. GKE/Compute Engine alternatives have their own pricing, not these rates.

## 5. Recorded configuration and guest inventory

[All settings, client stacks, attempt IDs and observations](tested-configurations.md) · [Machine-readable export](tested-configurations.json)

- Setup `1d300bb22b3d` · adapter `c640a283b17a` · stack `0a074557c3d6` · concurrency 1 · last measured 2026-10-13T16:30:17.206879+00:00.
- Setup `5a61c94c9323` · adapter `c640a283b17a` · stack `0a074557c3d6` · concurrency 1 · last measured 2026-10-13T07:40:59.061824+00:00.
- Setup `39ed10c5d0c2` · adapter `c640a283b17a` · stack `unrecorded` · concurrency 1 · last measured 2026-10-13T07:13:36.220476+00:00.

Guest-visible CPU/RAM and device probes do not attest reserved hardware or isolation. No GPU configuration was benchmarked in this snapshot.

## 6. Dated source register

- <a id="source-adapter"></a> [adapter: Repository adapter: GcpVertexBackend](../../src/core/providers/gcp_vertex.py) — accessed 2026-10-13.
- <a id="source-report"></a> [report: Saved GCP evaluation; measured workload outcomes, unverified billing](../../reports/data/attempts/gcp_vertex_evaluation.json) — accessed 2026-10-13.
- <a id="source-offline_workload"></a> [offline_workload: DependencyInstallBenchmark: uploaded offline wheel](../../src/bench/suites/workflows.py) — accessed 2026-10-13.
- <a id="source-local_environment"></a> [local_environment: Historical code-sandbox probe summary, 2026-10-01; original logs not in campaign dataset](../../providers/gcp_vertex/client-reference.md#historical-environment-probe) — accessed 2026-10-13.
- <a id="source-local_sdk"></a> [local_sdk: Versioned SDK contract summary and observed state/file semantics](../../providers/gcp_vertex/client-reference.md#sdk-contracts) — accessed 2026-10-13.
- <a id="source-local_cli"></a> [local_cli: External CLI lifecycle and TTL contract](../../providers/gcp_vertex/client-reference.md#cli-contract) — accessed 2026-10-13.
- <a id="source-local_shell"></a> [local_shell: Shell/container path: CMEK end-to-end unverified](../../providers/gcp_vertex/client-reference.md#shell-and-container-scope) — accessed 2026-10-13.
- <a id="source-local_cmek"></a> [local_cmek: Versioned CMEK parent runtime and dual-service-agent setup notes](../../providers/gcp_vertex/client-reference.md#cmek-setup) — accessed 2026-10-13.
- <a id="source-local_billing"></a> [local_billing: Billed lifecycle and deletion/TTL scope](../../providers/gcp_vertex/client-reference.md#billing-and-cleanup) — accessed 2026-10-13.
- <a id="source-gcp_code"></a> [gcp_code: Google: Code Execution overview](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/sandbox/code-execution-overview) — accessed 2026-10-13.
- <a id="source-gcp_byoc"></a> [gcp_byoc: Google: Custom container sandbox overview (BYOC)](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/sandbox/custom-containers) — accessed 2026-10-13.
- <a id="source-gcp_lifecycle"></a> [gcp_lifecycle: Google: Manage sandboxes, pause/resume and billing lifetime](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/sandbox/manage-sandboxes) — accessed 2026-10-13.
- <a id="source-gcp_cmek"></a> [gcp_cmek: Google: Configure CMEK for sandboxes](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/sandbox/configure-cmek) — accessed 2026-10-13.
- <a id="source-gcp_pricing"></a> [gcp_pricing: Google pricing: Agents / Agent Compute section](https://cloud.google.com/vertex-ai/pricing) — accessed 2026-10-13.
- <a id="source-gke_agent"></a> [gke_agent: Google: Isolate AI code execution with GKE Agent Sandbox](https://docs.cloud.google.com/kubernetes-engine/docs/how-to/agent-sandbox) — accessed 2026-10-13.
- <a id="source-gke_runtime"></a> [gke_runtime: Google: GKE Sandbox runtimes and GPU restrictions](https://docs.cloud.google.com/kubernetes-engine/docs/concepts/sandbox-pods) — accessed 2026-10-13.
- <a id="source-gke_pricing"></a> [gke_pricing: Google: GKE pricing](https://cloud.google.com/kubernetes-engine/pricing) — accessed 2026-10-13.
- <a id="source-compute_custom"></a> [compute_custom: Google: Compute Engine custom CPU/memory machine types](https://docs.cloud.google.com/compute/docs/instances/creating-instance-with-custom-machine-type) — accessed 2026-10-13.
- <a id="source-compute_image"></a> [compute_image: Google: Create custom Compute Engine images](https://docs.cloud.google.com/compute/docs/images/create-custom) — accessed 2026-10-13.
- <a id="source-compute_gpu"></a> [compute_gpu: Google: Create a general-purpose VM with attached GPUs](https://docs.cloud.google.com/compute/docs/gpus/create-gpu-vm-general-purpose) — accessed 2026-10-13.
- <a id="source-compute_pricing"></a> [compute_pricing: Google: VM instance pricing and billing units](https://cloud.google.com/compute/all-pricing) — accessed 2026-10-13.
- <a id="source-compute_gpu_pricing"></a> [compute_gpu_pricing: Google: Accelerator-optimized VM pricing](https://cloud.google.com/products/compute/pricing/accelerator-optimized) — accessed 2026-10-13.

<!-- COMMON CONTRACT END -->

## Detailed provider dossier
# gcp_vertex — managed Agent Engine / Agent Platform code sandbox

Reviewed **2026-10-13**. Machine-readable companion: [spec.json](spec.json).

Post-run client check: installed `agent-sandbox --version` reported **0.2.0**. The early campaign execution-stack metadata did not record the CLI-managed SDK version; do not equate the host Python package inventory with that isolated CLI environment.

## Identity and tested integration

`GcpVertexBackend` invokes the separately installed `agent-sandbox run --file … --format json --ttl … --max-output-chars 0 --out …`, with repeatable `--upload`. This is the default **Google-managed Python code sandbox** under a parent Agent Engine, now called Agent Runtime in current Agent Platform documentation. It is not Gemini's model-native code-execution tool, a GKE cluster administered by this benchmark, or a Compute Engine VM. The adapter uses a one-shot lifecycle and does not expose BYOC template selection. [adapter, local_cli, gcp_code]

| Dimension | Requested by tested integration | Actual evidence |
|---|---|---|
| CPU | No sizing setting | Current campaign allocation unknown. Report cost metadata assumes 2 vCPU; separate October 1 probe saw 8 visible CPUs and roughly 2x parallel speedup. Neither establishes an allocation guarantee. |
| RAM | No sizing setting | Current campaign allocation unknown. Report assumes 4 GB for costing; October 1 probe measured 2 GiB. |
| Network | No policy setting | Current code-sandbox docs specify no network; October 1 probe could not use DNS/IP. Adapter `has_internet_access=true` is a declaration contradicted by that evidence. |
| Image | Default code environment, no custom image requested | Python 3.12.5 observed in the evaluation; actual image digest unknown. |
| Lifetime | `min(request.timeout_seconds + 30, 900)` seconds | CLI `run` owns create/delete. Saved cleanup success is a harness outcome, not cloud deletion/key attestation. |

Sources: [adapter, report, local_environment, local_cli]. Current [tested configurations and guest inventories](tested-configurations.md) supplement the older probe: Python 3.12.5, x86_64, eight visible/affinity CPUs, 2 GiB physical memory reported, kernel string `4.19.0-gvisor`; cgroup reservation limits were unavailable. These are guest observations, not resource reservations or control-plane isolation attestation. No GPU requested/tested; absence of `nvidia-smi` cannot establish the broader platform's GPU eligibility.

The saved evaluation verifies artifact byte/hash checks, including the 26,900-byte round trip and `summary.json`; Python 3.12.5; repository/SQLite/data workloads; and installation/import of an **uploaded offline pure-Python wheel** into a private target. The workload calls `pip --no-index --no-deps --target`, not PyPI. This narrow observed behavior differs from the official statement that own libraries cannot be installed in the code environment. Do not generalize it into unrestricted package installation. [report, offline_workload, gcp_code]

## Capabilities: all 13 feature IDs

Support describes the stated scope; evidence distinguishes documented service features from measured workloads. Conditional broader-service support does not mean the tested adapter implements it.

| Feature ID | Support / evidence | Scope and limitation | Sources |
|---|---|---|---|
| `custom_image` | conditional / documented | BYOC image in Artifact Registry plus a custom-container template; not this default-code run. Local shell/CMEK path is end-to-end unverified. | gcp_byoc, adapter, local_shell |
| `runtime_packages` | conditional / measured | One uploaded pure-Python wheel installed offline; arbitrary/native/online installs unproven. BYOC supplies custom dependencies. | report, offline_workload, gcp_code, gcp_byoc |
| `cpu_sizing` | conditional / documented | CPU requests/limits in BYOC; no sizing requested by this adapter. | gcp_byoc, adapter, report, local_environment |
| `memory_sizing` | conditional / documented | RAM requests/limits in BYOC; report's 4 GB is a costing assumption. | gcp_byoc, adapter, report, local_environment |
| `gpu` | unknown / unverified | No campaign inventory/request; prior code probe found none. BYOC GPU availability not established. | adapter, report, local_environment, gcp_byoc, compute_gpu, gke_runtime |
| `network_policy` | conditional / documented | Default code has no network; BYOC has `internet_access`. Effective current deployment policy unrecorded. | gcp_code, gcp_byoc, local_environment, adapter, report |
| `persistent_storage` | conditional / documented | Live-sandbox files/state; broader lifecycle pause/resume documented, not tested. No durable storage across deletion; code snapshots unsupported. | gcp_code, gcp_lifecycle, local_sdk, local_cli, adapter |
| `session_reuse` | supported / documented | Same sandbox ID can retain state. Adapter creates/deletes on every execution. | gcp_code, local_cli, adapter |
| `shell` | supported / measured | Subprocess execution verified by offline pip workload; local code sandbox also supports bash. Separate shell-container deployment untested. | report, offline_workload, local_environment, local_shell |
| `file_transfer` | supported / measured | Uploaded input and generated artifacts validated by bytes/hash. Official aggregate request/response limit: 100 MB. | report, adapter, gcp_code |
| `ports_preview` | conditional / documented | BYOC ports documented; no automatic public preview URL attested or adapter support. | gcp_byoc, adapter |
| `self_hosting` | unsupported / documented | Managed service; local client location does not change runtime ownership. | gcp_code, gke_agent, compute_custom |
| `cmek` | supported / documented | Parent-runtime key inheritance; saved report does not verify key attachment or KMS use. | gcp_cmek, local_cmek, report |

Current Code Execution docs advertise state retention up to **14 days**. The bundled CLI reference caps its requested TTL at **3,600 seconds**; the adapter caps at **900 seconds**. These are distinct service/documentation/tool constraints, not evidence that the tested CLI supports 14-day sessions. [gcp_code, local_cli, adapter]

CMEK covers sandbox at-rest content and eligible snapshots via the parent, not names, labels, state metadata or environment variables. Custom image encryption requires the Artifact Registry repository's own encryption configuration. The local setup records a need to grant both Vertex service agents; current Google sandbox instructions describe the Agent Runtime service agent. Preserve this as version-specific setup evidence, not an encryption claim inferred from benchmark success. [gcp_cmek, local_cmek]

## Customization alternatives and deployment overhead

1. **Managed Agent Platform BYOC**: current official docs show an Artifact Registry image, compatible entry point, image-read IAM grant, sandbox template, CPU/RAM requests and limits, ports, and `egress_control_config.internet_access`. This is a broader service path, not a tested feature of `GcpVertexBackend`. It requires image build/publish, permissions, template lifecycle, and integration with the container data plane. Local references warn that default shell containers under CMEK in the tested preview region were not verified end to end. [gcp_byoc, local_shell]
2. **GKE Agent Sandbox / Kubernetes-SIGs**: a distinct Kubernetes deployment using `Sandbox`, `SandboxTemplate`, `SandboxClaim`, a router, and optional warm pools. Google's GKE add-on manages the controller; operators still configure the cluster, images, resources, routing, identities, storage, and policies. The official guide requires gVisor and admission constraints; developer router tunneling is not production access control. This alternative is described further in [../k8s_agent_sandbox/SPEC.md](../k8s_agent_sandbox/SPEC.md). GPU use depends on compatible sandbox runtime, GKE version, models and drivers; it is not implied by choosing GKE. [gke_agent, gke_runtime]
3. **Compute Engine CPU/GPU VMs**: select supported custom CPU/RAM machine types, custom VM images, and supported GPU configurations. General-purpose N1 VMs can attach supported GPUs; newer accelerator-heavy work uses A/G-series machines. This is infrastructure control, requiring VM/image lifecycle, drivers/CUDA, quota and zonal capacity, disk/IAM/network setup, a command/file access layer, isolation choices, and cleanup. No such VM was tested by `gcp_vertex`. [compute_custom, compute_image, compute_gpu]

## Pricing and interpretation

Official **Agents / Agent Compute** pricing reviewed on October 13 lists default paid-tier rates of **$0.085 per vCPU-hour** and **$0.009 per GiB-hour**, with usage rounded to the nearest second. The page explicitly includes Sandbox environments, Code Execution and Computer Use. It lists monthly per-account free tiers of 50 compute hours and 100 GiB-hours of memory, plus eligible savings-plan tiers. The statement about unbilled between-turn idle time is explicitly for Runtime; do not extend it to sandbox idle time. Sandbox lifecycle docs state that sandboxes are billed while they exist. [gcp_pricing, gcp_lifecycle]

The saved report's `$0.000114/second`, 2 vCPU and 4 GB values are marked `estimate_unverified_rates`, `billing_verified=false`. Client wall time is not resource billing time. No report total is an observed cloud bill, and no historical increase is established by these mismatched estimates. CMEK/KMS and ancillary resource charges need separate SKU/account verification. [report, local_billing]

For alternatives, GKE Agent Sandbox has **no additional feature fee**, but GKE pricing applies: $0.10 per cluster-hour before eligible credits, plus Standard node or Autopilot resource charges, storage, networking and warm capacity. Compute Engine CPU/GPU/memory billing has a **one-minute minimum**, then second increments; rates depend on region, hardware, discounts and commitment. Accelerator-optimized VM prices are separate from Agent Compute rates. A useful cost comparison must include image provisioning, startup/idle time and deployment overhead. [gke_agent, gke_pricing, compute_pricing, compute_gpu_pricing]

## Source references

Repository notes are versioned historical context, not official product promises. The earlier probe's original per-call logs are not part of this campaign dataset. All sources reviewed 2026-10-13.

- **adapter** — [GCP adapter](../../src/core/providers/gcp_vertex.py)
- **report** — [Saved evaluation](../../reports/data/attempts/gcp_vertex_evaluation.json)
- **offline_workload** — [DependencyInstallBenchmark](../../src/bench/suites/workflows.py)
- **local_environment** — [October 1 probe summary](client-reference.md#historical-environment-probe)
- **local_sdk** — [SDK contract summary](client-reference.md#sdk-contracts)
- **local_cli** — [Versioned CLI contract](client-reference.md#cli-contract)
- **local_shell** — [Shell/CMEK scope](client-reference.md#shell-and-container-scope)
- **local_cmek** — [Versioned CMEK setup notes](client-reference.md#cmek-setup)
- **local_billing** — [Lifecycle billing and cleanup](client-reference.md#billing-and-cleanup)
- **gcp_code** — [Google Code Execution overview](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/sandbox/code-execution-overview)
- **gcp_byoc** — [Google custom-container sandboxes](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/sandbox/custom-containers)
- **gcp_lifecycle** — [Google sandbox lifecycle](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/sandbox/manage-sandboxes)
- **gcp_cmek** — [Google sandbox CMEK](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/sandbox/configure-cmek)
- **gcp_pricing** — [Google pricing, Agents section](https://cloud.google.com/vertex-ai/pricing)
- **gke_agent** — [Google GKE Agent Sandbox deployment guide](https://docs.cloud.google.com/kubernetes-engine/docs/how-to/agent-sandbox)
- **gke_runtime** — [Google GKE Sandbox and GPU limitations](https://docs.cloud.google.com/kubernetes-engine/docs/concepts/sandbox-pods)
- **gke_pricing** — [GKE pricing](https://cloud.google.com/kubernetes-engine/pricing)
- **compute_custom** — [Compute Engine custom machine types](https://docs.cloud.google.com/compute/docs/instances/creating-instance-with-custom-machine-type)
- **compute_image** — [Compute Engine custom images](https://docs.cloud.google.com/compute/docs/images/create-custom)
- **compute_gpu** — [Compute Engine GPU VM configuration](https://docs.cloud.google.com/compute/docs/gpus/create-gpu-vm-general-purpose)
- **compute_pricing** — [Compute Engine billing/pricing](https://cloud.google.com/compute/all-pricing)
- **compute_gpu_pricing** — [Accelerator-optimized VM pricing](https://cloud.google.com/products/compute/pricing/accelerator-optimized)
