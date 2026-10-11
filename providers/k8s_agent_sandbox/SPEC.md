<!-- COMMON CONTRACT START -->
# Provider contract: Kubernetes adapter (deployment unattested) (`k8s_agent_sandbox`)

**Sources reviewed:** 2026-10-13 · **Deployment:** `self_hosted`

## 1. Executive summary and product boundary

HTTP endpoint adapter; host auto-spawn does not establish deployment to Kubernetes/GKE or an isolation runtime.

Deployment unattested. Adapter talks HTTP to an existing AGENT_SANDBOX_URL or, by default, auto-spawns the repository FastAPI/uvicorn server as a host subprocess. That fallback is not Kubernetes-SIGs controller/CRD provisioning or managed GKE isolation. Official Kubernetes deployments allow image/resource/storage/network configuration; GKE offers a managed controller add-on on an operator-configured cluster. Saved results must not be assigned a security ranking.

Working adapter: [source](../../src/core/providers/k8s_agent_sandbox.py). Historical adapter hashes refer to measured revisions, not necessarily current source.

The preserved dossier describes the dated inspected configuration. New budget/lifecycle guardrails change current adapter defaults without changing historical cohort evidence; see [operations](../../CONTRIBUTING.md).

## 2. Documented contract vs measured adapter

Support describes the platform. Measured describes only a bounded oracle on a recorded setup. Documented-only and unverified entries remain coverage gaps.

| Capability | Platform support | Evidence state | Documented contract / scope | Measured adapter behavior | Sources |
|---|---|---|---|---|---|
| `custom_image` | conditional | Documented | Official Sandbox/SandboxTemplate podTemplate selects a container image. Adapter sends no image and does not create templates/claims; auto_spawn uses host Python. Repository YAML/image is deployment intent, not evidence that it ran. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [upstream](#source-upstream), [gke_guide](#source-gke_guide), [adapter](#source-adapter), [local_manifest](#source-local_manifest) |
| `runtime_packages` | conditional | Unverified | A chosen image can bundle dependencies and runtime installation depends on permission/egress. Saved report observes preinstalled packages and pip availability, not installing a new package. Auto-spawn inherits the host runtime and network. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [gke_guide](#source-gke_guide), [adapter](#source-adapter), [server](#source-server), [report](#source-report) |
| `cpu_sizing` | conditional | Documented | Official pod templates support requests/limits. Repository manifest requests 500m and limits 2 CPUs; adapter sends neither and auto-spawn sets no CPU constraint. Report's cost assumption of 2 vCPU does not attest effective allocation. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [gke_guide](#source-gke_guide), [local_manifest](#source-local_manifest), [adapter](#source-adapter), [server](#source-server), [report](#source-report) |
| `memory_sizing` | conditional | Documented | Official pod templates support memory requests/limits. Repository manifest requests 1Gi and limits 4Gi; adapter sends neither. Saved allocation workload reaching 2000MB is not a 4Gi limit or allocation measurement. Actual deployment limits unknown. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [gke_guide](#source-gke_guide), [local_manifest](#source-local_manifest), [adapter](#source-adapter), [report](#source-report) |
| `gpu` | conditional | Documented | A real GKE gVisor deployment can use supported GPUs for CUDA under version/model/driver constraints; microVM sandbox runtimes do not support GPUs per reviewed GKE docs. Adapter/manifest request no accelerator and report contains no GPU inventory. No accelerator access is attested here. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [gke_runtime](#source-gke_runtime), [adapter](#source-adapter), [local_manifest](#source-local_manifest), [report](#source-report) |
| `network_policy` | conditional | Documented | Official GKE add-on manages ingress/egress policies and permits template customization. Auto-spawn installs no network policy. Report observed DNS/HTTP allowed and metadata URL failure, which does not prove an enforced isolation policy or identify the deployment. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [gke_guide](#source-gke_guide), [adapter](#source-adapter), [server](#source-server), [report](#source-report) |
| `persistent_storage` | conditional | Documented | Upstream supports persistent storage surviving Pod restarts when configured. Local fallback uses a shared temporary base directory removed in teardown; per-run cleanup is a no-op. No PVC/mount/retention attestation in report or local template. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [upstream](#source-upstream), [adapter](#source-adapter), [server](#source-server), [local_manifest](#source-local_manifest), [report](#source-report) |
| `session_reuse` | conditional | Documented | Upstream provides stable stateful Sandbox identity/lifecycle. This adapter targets one HTTP server/base directory with no claim/session allocation. A five-turn loop inside one execution does not prove independently isolated cross-request sessions. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [upstream](#source-upstream), [adapter](#source-adapter), [server](#source-server), [report](#source-report) |
| `shell` | supported | Documented | Saved Python workloads ran through /execute. Repository server executes arbitrary commands with asyncio.create_subprocess_shell in a working directory; auto-spawn imposes no kernel/container boundary. Measured command execution is not measured sandbox isolation. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [adapter](#source-adapter), [server](#source-server), [report](#source-report) |
| `file_transfer` | conditional | Documented | HTTP upload/download are implemented, but the saved roundtrip stdout says 20 output bytes with SHA 03f8b5a6985317bb443711cf59982832808ed02a2a2b2c2e7c07bd702ac081e9 while collected artifact is 35 bytes with SHA 1093d1f916b518786a39c26266690572a4dfb9b7273ca21cf923acd9e42fa394. This is not a verified byte-faithful roundtrip. Adapter collects only two candidate paths. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [adapter](#source-adapter), [server](#source-server), [report](#source-report) |
| `ports_preview` | conditional | Documented | Official deployments route HTTP through a Sandbox Router and production direct/Gateway connections. Operator configures services, exposure and authentication; no automatic public preview URL. Local port 8888 is an execution API, not proof of application-port preview support. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [gke_guide](#source-gke_guide), [upstream](#source-upstream), [adapter](#source-adapter) |
| `self_hosting` | supported | Documented | Upstream is a Kubernetes CRD/controller installed on an operator cluster; GKE alternatively manages the controller add-on. Adapter can run its local server but does not provision either deployment. The saved deployment remains unattested. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [upstream](#source-upstream), [gke_concepts](#source-gke_concepts), [adapter](#source-adapter), [report](#source-report) |
| `cmek` | conditional | Documented | GKE can use customer-managed keys for node boot disks and attached Persistent Disks/Filestore with explicit KMS/IAM/StorageClass setup. This is infrastructure/storage-specific, not an Agent Sandbox API guarantee; control-plane disks cannot use CMEK. No key configured by adapter or attested in report. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [gke_cmek](#source-gke_cmek), [adapter](#source-adapter), [local_manifest](#source-local_manifest), [report](#source-report) |

## 3. Six residency surfaces

Source: [dated residency audit and original vendor citations](../../reports/docs/eu-data-residency.md). These are documented boundaries/gaps, not measured EU residency or GDPR certification.

| Surface | Documented boundary / verification gap |
|---|---|
| Compute | Operator-selected; remote deployment not attested |
| Files / volumes / snapshots / backups | Operator-selected storage/backup configuration |
| Stdout / stderr / traces | Operator-selected observability |
| Control plane / metadata | Operator-selected management/control plane |
| Support access / subprocessors | Operator/support-access policy required |
| External model / API calls | External endpoints remain separate |

Benchmark location/request provenance is recorded separately in [tested configurations](tested-configurations.md).

## 4. Dated pricing and billing units

No universal Kubernetes-SIGs per-execution tariff; pay for deployed infrastructure, warm pools, router/controller capacity, storage and networking. GKE Agent Sandbox adds no feature fee; normal GKE pricing applies.

| SKU / resource | Original billing unit | USD list amount | Sources |
|---|---|---:|---|
| GKE Agent Sandbox incremental feature fee | feature surcharge | 0 | [gke_guide](#source-gke_guide) |
| GKE cluster management before eligible credits | cluster-hour | 0.1 | [gke_pricing](#source-gke_pricing) |
| Deployment CPU, memory, GPU, storage and network | deployment-specific infrastructure SKU | Unknown | [gke_pricing](#source-gke_pricing), [compute_pricing](#source-compute_pricing) |

Deployment unattested, so no measured cloud cost. Saved $0.000072/second and 2-vCPU/4-GB inputs have no bill/SKU provenance. GKE Standard nodes use Compute Engine per-second billing with one-minute minimum; general-purpose Autopilot uses requested Pod resources in one-second increments with no duration minimum; selected hardware uses node-based billing plus management premium. Warm pool idle capacity and cluster/router/storage costs cannot be omitted. GKE monthly eligible cluster-fee credit is $74.40 per billing account, not free workload compute. No historical increase or security ranking asserted.

## 5. Recorded configuration and guest inventory

[All settings, client stacks, attempt IDs and observations](tested-configurations.md) · [Machine-readable export](tested-configurations.json)

- Setup `5ec993b27fcf` · adapter `b8704b7e87ef` · stack `578cdc6d53b4` · concurrency 1 · last measured 2026-10-13T16:26:44.965515+00:00.

Guest-visible CPU/RAM and device probes do not attest reserved hardware or isolation. No GPU configuration was benchmarked in this snapshot.

## 6. Dated source register

- <a id="source-adapter"></a> [adapter: Repository HTTP adapter and auto_spawn fallback](../../src/core/providers/k8s_agent_sandbox.py) — accessed 2026-10-13.
- <a id="source-server"></a> [server: Repository FastAPI host-subprocess execution server](../../deploy/agent-sandbox/server.py) — accessed 2026-10-13.
- <a id="source-local_manifest"></a> [local_manifest: Unattested repository SandboxTemplate/WarmPool deployment intent](../../deploy/agent-sandbox/k8s-sandbox.yaml) — accessed 2026-10-13.
- <a id="source-report"></a> [report: Saved legacy live report, missing deployment provenance](../../reports/data/legacy/k8s_agent_sandbox_live.json) — accessed 2026-10-13.
- <a id="source-upstream"></a> [upstream: Official Kubernetes-SIGs Agent Sandbox controller and CRDs](https://github.com/kubernetes-sigs/agent-sandbox) — accessed 2026-10-13.
- <a id="source-gke_guide"></a> [gke_guide: Google: Isolate AI code execution with GKE Agent Sandbox](https://docs.cloud.google.com/kubernetes-engine/docs/how-to/agent-sandbox) — accessed 2026-10-13.
- <a id="source-gke_concepts"></a> [gke_concepts: Google: GKE managed Agent Sandbox add-on](https://docs.cloud.google.com/kubernetes-engine/docs/concepts/machine-learning/agent-sandbox) — accessed 2026-10-13.
- <a id="source-gke_runtime"></a> [gke_runtime: Google: GKE Sandbox runtimes, CPU/memory/GPU restrictions](https://docs.cloud.google.com/kubernetes-engine/docs/concepts/sandbox-pods) — accessed 2026-10-13.
- <a id="source-gke_cmek"></a> [gke_cmek: Google: GKE CMEK for boot and attached disks](https://docs.cloud.google.com/kubernetes-engine/docs/how-to/using-cmek) — accessed 2026-10-13.
- <a id="source-gke_pricing"></a> [gke_pricing: Google: GKE cluster, Standard and Autopilot pricing](https://cloud.google.com/kubernetes-engine/pricing) — accessed 2026-10-13.
- <a id="source-compute_pricing"></a> [compute_pricing: Google: Compute Engine infrastructure billing units](https://cloud.google.com/compute/all-pricing) — accessed 2026-10-13.

<!-- COMMON CONTRACT END -->

## Detailed provider dossier
# k8s_agent_sandbox — deployment-dependent HTTP integration

Reviewed **2026-10-13**. Machine-readable companion: [spec.json](spec.json).

**Deployment unattested; no security ranking.** The adapter name and successful commands do not identify the deployment or prove official Kubernetes/GKE isolation. [adapter, server, report]

## Three different deployment paths

1. **Official Kubernetes-SIGs Agent Sandbox** is a Kubernetes `Sandbox` CRD/controller with optional `SandboxTemplate`, `SandboxClaim` and `SandboxWarmPool` extensions. It orchestrates stateful singleton Pods and delegates low-level isolation to a configured runtime such as gVisor or Kata via `RuntimeClass`. Operators install/configure the controller and isolation/runtime infrastructure. [upstream]
2. **Official GKE Agent Sandbox** is a managed GKE controller add-on based on that project. Google manages controller upgrades/patches, while the operator provisions/configures the cluster, templates, images, resources, router, access identities, networking, storage and warm capacity. This is distinct from Agent Engine/Agent Runtime managed sandboxes tested by `gcp_vertex`. [gke_concepts, gke_guide]
3. **This repository's `auto_spawn` fallback** runs `python3 -m uvicorn deploy.agent-sandbox.server:app --host 127.0.0.1 --port …` as a host subprocess. Its FastAPI `/execute` calls `asyncio.create_subprocess_shell(command, cwd=base_dir)`. It creates no Kubernetes resource, claim, controller, container, gVisor or VM boundary. A working directory and file-endpoint path checks are not command execution isolation. Source comments calling it “official”, “managed” or “secure” do not prove those properties. [adapter, server]

The adapter defaults to an existing HTTP endpoint (`AGENT_SANDBOX_URL`, otherwise `127.0.0.1:8888`) and auto-spawns only if its health check fails. It uses `httpx`, not the official client claim lifecycle, and does not establish which infrastructure serves the endpoint. Thus the saved report must not be relabeled as definitely local fallback either: its deployment is **unknown**, even though the fallback path is known from code. [adapter, report]

## Requested settings versus actual evidence

| Dimension | Adapter / repository deployment intent | Actual saved-run evidence |
|---|---|---|
| CPU | No adapter sizing; YAML requests `500m`, limits `2` | Allocation unknown; report's `vcpu: 2` is a cost assumption, not readback. |
| RAM | No adapter sizing; YAML requests `1Gi`, limits `4Gi` | Actual limit unknown. A workload allocating through 2,000 MB does not establish a 4 GiB allocation/limit. |
| Network | No adapter policy; fallback inherits host network | DNS and public HTTP succeeded; metadata URL failed. These outcomes do not attest a policy, CNI or isolation boundary. |
| Image | No adapter image choice; YAML names `k8s-agent-sandbox:latest` | Python 3.12.15 and Linux/aarch64/container flag observed; image digest, runtime class, cluster and Pod unknown. |
| State / storage | Shared server base directory; no session/claim identifier; per-run cleanup is no-op | A single-program five-turn loop reported continuity; separate requests/session isolation and durable storage untested. |

Sources: [adapter, server, local_manifest, report]. The YAML expresses intent only. Its API group `sandbox.k8s.io/v1alpha1` and `templateRef` differ from the current official GKE example's `extensions.agents.x-k8s.io/v1beta1` and `sandboxTemplateRef`. No applied-resource or controller/version evidence establishes compatibility or deployment. [local_manifest, gke_guide]

## Saved-report caveats

- The legacy report has no campaign configuration, start timestamp, cluster/Pod/node identifiers, RuntimeClass, image digest, policy manifest/readback, isolation attestation, or billing verification. Host/process/container observations cannot recover those omissions. [report]
- `artifact_roundtrip` prints **20 output bytes** and SHA-256 `03f8b5a6985317bb443711cf59982832808ed02a2a2b2c2e7c07bd702ac081e9`, but the collected artifact records **35 bytes** and SHA-256 `1093d1f916b518786a39c26266690572a4dfb9b7273ca21cf923acd9e42fa394`. It is not a validated byte-faithful round trip despite `status: success`. Collection only checks `transformed_output.txt` and `output.txt`, and per-run cleanup does nothing; these are relevant implementation limitations, not proof of the mismatch's cause. [report, adapter]
- A failed metadata request labeled `BLOCKED_SECURE` can result from an absent route/service as well as a policy. Non-root UID, a container flag, unavailable sudo, and a client-side timeout do not demonstrate resistance to escapes or cross-session access. The recorded client timeout does not prove the remote workload stopped. **Do not assign a security rank to this report.** [report, adapter, server]
- `cold_start_ms: 0` is not a measured zero-latency Kubernetes claim/Pod startup. Reported timings and cost estimates cannot be compared as official managed-GKE provisioning or billing measurements. [report]

## Capabilities: all 13 feature IDs

Conditional documented entries refer to properly deployed infrastructure, not attested capabilities of this saved run.

| Feature ID | Support / evidence | Scope and limitation | Sources |
|---|---|---|---|
| `custom_image` | conditional / documented | Official Pod templates choose image. Adapter sends none; fallback uses host Python. | upstream, gke_guide, adapter, local_manifest |
| `runtime_packages` | conditional / unverified | Image/permission/egress dependent. Saved report observes pip/packages, not new package installation. | gke_guide, adapter, server, report |
| `cpu_sizing` | conditional / documented | Official requests/limits; local YAML intent only; fallback has no CPU constraint. | gke_guide, local_manifest, adapter, server, report |
| `memory_sizing` | conditional / documented | Official requests/limits; no actual limit readback. | gke_guide, local_manifest, adapter, report |
| `gpu` | conditional / documented | GKE gVisor CUDA support depends on models/drivers/version; microVM runtimes do not support GPU. No GPU tested here. | gke_runtime, adapter, local_manifest, report |
| `network_policy` | conditional / documented | Official managed/template policies; fallback creates none. | gke_guide, adapter, server, report |
| `persistent_storage` | conditional / documented | Upstream configurable persistent storage survives restarts; no PVC in local template or report. Fallback temp directory removed in teardown. | upstream, adapter, server, local_manifest, report |
| `session_reuse` | conditional / documented | Upstream stable Sandbox state/identity; current adapter has one server directory, no claim/session allocation. | upstream, adapter, server, report |
| `shell` | supported / measured | Commands/Python ran via HTTP. Isolation is not thereby measured. | adapter, server, report |
| `file_transfer` | conditional / measured | Upload/download implemented; saved artifact differs from workload output bytes/hash. | adapter, server, report |
| `ports_preview` | conditional / documented | Router/services/Gateway configured by operator; no automatic public application preview. | gke_guide, upstream, adapter |
| `self_hosting` | supported / documented | Upstream installed on an operator cluster; optional managed GKE controller; actual report deployment unknown. | upstream, gke_concepts, adapter, report |
| `cmek` | conditional / documented | GKE disk/storage CMEK needs KMS/IAM/StorageClass configuration, not a universal sandbox encryption switch. | gke_cmek, adapter, local_manifest, report |

## Official GKE path and operational overhead

The official GKE guide uses a gVisor `SandboxTemplate`, non-root operation, disabled service-account-token automount, dropped capabilities, resource limits, and managed admission/network policies. Its secure-by-default networking allows public internet egress while blocking private ranges, cluster DNS and metadata ranges; ingress is restricted to the router. Custom policies are needed for private resources/Workload Identity integration. These are documented controls, not controls attested in the report. [gke_guide]

Production operators must configure authentication/RBAC or workload identity, router reachability through in-cluster direct connections or Gateway, and storage/retention. The guide distinguishes developer `kubectl port-forward` to the router from production access. Warm pools consume capacity while idle. Runtime isolation, GPU compatibility, template/claim/controller versions, and cleanup must be explicitly verified on the chosen deployment. GKE's managed controller reduces operational work but does not make a local HTTP server a managed sandbox. [gke_guide, gke_concepts, upstream, gke_runtime]

GKE disk CMEK can protect node boot disks and eligible attached storage, with explicit key/IAM and storage-class setup. GKE control-plane disks cannot be protected with CMEK. Neither a Pod resource nor this adapter intrinsically provides end-to-end customer-managed encryption. [gke_cmek]

For an infrastructure-controlled GPU VM alternative, see [gcp_vertex/SPEC.md](../gcp_vertex/SPEC.md#customization-alternatives-and-deployment-overhead): Compute Engine GPU/image/resource configuration has its own drivers, quotas, lifecycle, network/IAM and isolation overhead and is not a measured capability of this integration.

## Pricing

There is **no universal Kubernetes-SIGs per-execution tariff**. Google's Agent Sandbox GKE guide says the feature is offered **at no extra charge**, with normal GKE charges applying. GKE's cluster management fee is **$0.10 per cluster-hour**, billed in second increments, before eligible monthly **$74.40 per billing-account credits** for qualifying Autopilot/zonal clusters. Those credits do not make workload compute free. [gke_guide, gke_pricing]

- **Standard:** node VM charges continue until deletion; Compute Engine second increments with one-minute minimum. [gke_pricing, compute_pricing]
- **General-purpose Autopilot:** requested Pod CPU/memory/ephemeral-storage resources billed in second increments with no duration minimum; effective requests may be increased to satisfy constraints. [gke_pricing]
- **Specific-hardware Autopilot:** whole-node Compute Engine charges plus management premium, not simply the small Pod request. [gke_pricing]
- Add warm-pool idle capacity, router/controller capacity, disks, networking, images and operational overhead to any comparison. [gke_guide, gke_pricing]

The saved report's `$0.000072/second`, 2 vCPU and 4 GB are **unattributed estimates**, not a cloud bill, current official GKE tariff, or deployment inventory. With deployment unattested, leave aggregate deployment rates unknown. No historical price increase or security ordering is established. [report]

## Source references

All accessed 2026-10-13.

- **adapter** — [HTTP integration and fallback](../../src/core/providers/k8s_agent_sandbox.py)
- **server** — [FastAPI subprocess server](../../deploy/agent-sandbox/server.py)
- **local_manifest** — [Unattested local YAML](../../deploy/agent-sandbox/k8s-sandbox.yaml)
- **report** — [Legacy saved live report](../../reports/data/legacy/k8s_agent_sandbox_live.json)
- **upstream** — [Official Kubernetes-SIGs Agent Sandbox](https://github.com/kubernetes-sigs/agent-sandbox)
- **gke_guide** — [Official Google GKE Agent Sandbox deployment guide](https://docs.cloud.google.com/kubernetes-engine/docs/how-to/agent-sandbox)
- **gke_concepts** — [Official Google managed add-on overview](https://docs.cloud.google.com/kubernetes-engine/docs/concepts/machine-learning/agent-sandbox)
- **gke_runtime** — [GKE Sandbox runtime/GPU restrictions](https://docs.cloud.google.com/kubernetes-engine/docs/concepts/sandbox-pods)
- **gke_cmek** — [GKE CMEK storage configuration](https://docs.cloud.google.com/kubernetes-engine/docs/how-to/using-cmek)
- **gke_pricing** — [GKE pricing](https://cloud.google.com/kubernetes-engine/pricing)
- **compute_pricing** — [Compute Engine billing units](https://cloud.google.com/compute/all-pricing)
