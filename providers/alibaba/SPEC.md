<!-- COMMON CONTRACT START -->
# Provider contract: Alibaba OpenSandbox / AgentRun (`alibaba`)

**Sources reviewed:** 2026-10-13 · **Deployment:** `hybrid`

## 1. Executive summary and product boundary

OpenSandbox/AgentRun endpoint adapter; self-hosted and managed endpoints are distinct. Host auto-spawn is not attested remote isolation.

Inventory covers self-hosted Apache-2.0 OpenSandbox Docker/Kubernetes and separate managed AgentRun. OCI images/resources/network/storage depend on backend; managed AgentRun custom images documented but upstream API parity/GPU sandbox availability not verified. No repo adapter or run.

Working adapter: [source](../../src/core/providers/alibaba.py). Historical adapter hashes refer to measured revisions, not necessarily current source.

The preserved dossier describes the dated inspected configuration. New budget/lifecycle guardrails change current adapter defaults without changing historical cohort evidence; see [operations](../../CONTRIBUTING.md).

## 2. Documented contract vs measured adapter

Support describes the platform. Measured describes only a bounded oracle on a recorded setup. Documented-only and unverified entries remain coverage gaps.

| Capability | Platform support | Evidence state | Documented contract / scope | Measured adapter behavior | Sources |
|---|---|---|---|---|---|
| `custom_image` | supported | Documented | OpenSandbox OCI image.uri/auth; managed AgentRun overview explicitly supports custom sandbox images. Managed image constraints not exhaustively verified; not proof of identical API. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [S1](#source-S1), [S2](#source-S2), [M1](#source-M1) |
| `runtime_packages` | conditional | Documented | Dependencies can be baked into custom images; runtime installation depends on permissions and egress. No managed live-pip execution verified. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [S1](#source-S1), [S2](#source-S2), [S3](#source-S3), [M1](#source-M1) |
| `cpu_sizing` | conditional | Documented | OpenSandbox resourceLimits.cpu supports quantities e.g. 500m. Backend quota/template/admission determine capacity. Managed AgentRun sandbox CPU range not verified. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [S2](#source-S2), [S4](#source-S4), [M1](#source-M1) |
| `memory_sizing` | conditional | Documented | OpenSandbox resourceLimits.memory supports 512Mi/1Gi style quantities. Backend limits apply; managed sandbox RAM tiers unverified. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [S2](#source-S2), [S4](#source-S4), [M1](#source-M1) |
| `gpu` | conditional | Documented | Official OpenSandbox ResourceLimits schema describes gpu device counts. Requires compatible backend mapping, GPU nodes/device integration/isolation and image; not universal Docker/Firecracker support. AgentRun model-runtime GPU is not managed sandbox GPU evidence; latter unknown. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [S2](#source-S2), [S3](#source-S3), [S4](#source-S4), [M1](#source-M1) |
| `network_policy` | conditional | Documented | OpenSandbox policy/enforcement deployment-dependent: Docker sidecar requires bridge and config, DNS mode not CIDR enforcement; IPv6 gaps. AgentRun VPC/PrivateLink does not prove upstream per-sandbox egress-schema parity. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [S2](#source-S2), [S3](#source-S3), [M1](#source-M1) |
| `persistent_storage` | conditional | Documented | OpenSandbox host/PVC/OSSFS volumes and backend snapshots; pool-mode storage configured in template. AgentRun OSS/NAS documented. Rootfs/session alone not indefinite durable storage. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [S2](#source-S2), [S3](#source-S3), [S4](#source-S4), [M1](#source-M1) |
| `session_reuse` | supported | Documented | OpenSandbox sandbox ID/lifecycle renew and backend-specific pause/resume; AgentRun file/session management. Rootfs snapshot not generic memory checkpoint; no repo multiturn run. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [S1](#source-S1), [S2](#source-S2), [S4](#source-S4), [M1](#source-M1) |
| `shell` | conditional | Documented | OpenSandbox commands.run shell documented. Managed AgentRun chosen image/tool/API governs shell availability; no blanket upstream interface inheritance. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [S1](#source-S1), [M1](#source-M1) |
| `file_transfer` | supported | Documented | OpenSandbox file SDK/API and managed AgentRun file management documented; exact managed file transport limits unverified. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [S1](#source-S1), [M1](#source-M1) |
| `ports_preview` | conditional | Documented | OpenSandbox port endpoint with configured ingress/proxy. Managed Browser CDP/WebSocket specific to browser; not general public preview guarantee. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [S2](#source-S2), [S3](#source-S3), [M1](#source-M1) |
| `self_hosting` | conditional | Documented | OpenSandbox self-hostable on Docker/Kubernetes, including configured isolation profiles; managed AgentRun backend not thereby self-hostable. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [S1](#source-S1), [S3](#source-S3), [M1](#source-M1) |
| `cmek` | unknown | Unverified | No native sandbox CMEK API or managed AgentRun sandbox key coverage verified. Infrastructure/storage encryption choices are distinct. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [S2](#source-S2), [S3](#source-S3), [M1](#source-M1) |

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

OpenSandbox has no software usage license fee; infrastructure paid separately. Managed AgentRun sandbox tariff unknown. FC standard CU reference rates below are independently sourced underlying-service prices, not verified managed sandbox quote; model inference separate.

| SKU / resource | Original billing unit | USD list amount | Sources |
|---|---|---:|---|
| OpenSandbox Apache-2.0 software usage license fee only | software usage license fee (excludes hosting) | 0 | [S1](#source-S1) |
| OpenSandbox operator-owned CPU/RAM/GPU/storage/network | chosen infrastructure billing unit | Unknown | [S1](#source-S1), [S3](#source-S3) |
| Managed AgentRun sandbox product-specific tariff | managed sandbox tariff not verified | Unknown | [M1](#source-M1) |
| FC reference standard Tier 1, regional monthly (0,100 million] CU | CU | 0.00002 | [P1](#source-P1), [P2](#source-P2) |
| FC reference standard Tier 2, regional monthly (100 million,500 million] CU | CU | 0.000017 | [P1](#source-P1) |
| FC reference standard Tier 3, regional monthly >500 million CU | CU | 0.000014 | [P1](#source-P1) |
| FC reference Tier 1 active CPU derived at 1 CU/vCPU-second | active vCPU-second | 0.00002 | [P1](#source-P1), [P2](#source-P2) |
| FC reference Tier 1 CPU-workload memory derived at 0.15 CU/GB-second | GB-second of CPU-workload memory | 0.000003 | [P1](#source-P1), [P2](#source-P2) |
| FC reference Tier 1 invocation derived at 75 CU/10,000 invocations | 10,000 invocations | 0.0015 | [P1](#source-P1), [P2](#source-P2) |
| FC reference Tier 1 billable disk derived at 0.05 CU/GB-second | billable GB-second of disk | 0.000001 | [P1](#source-P1), [P2](#source-P2) |
| External model inference | selected model/provider token billing unit | Unknown | [M1](#source-M1) |

FC reference rates do not prove AgentRun sandbox tariff. Promotion 2024-08-27 to 2026-08-27 ended before review; standard rates quoted. FC hourly settlement/CU rounding/$0.01 active function-hour minimum, CPU on-demand 1ms vs provisioned 10s and GPU 1s metering documented. FC sources differ on GPU coefficients/disk free quotas, so no managed GPU/storage quote inferred. OSS/NAS/CDT/registry/logging/model costs separate. No measured bills or comparable dated increase claim.

## 5. Recorded configuration and guest inventory

[All settings, client stacks, attempt IDs and observations](tested-configurations.md) · [Machine-readable export](tested-configurations.json)

- Setup `001504324c5f` · adapter `6c4185a41998` · stack `578cdc6d53b4` · concurrency 1 · last measured 2026-10-13T16:26:13.981726+00:00.
- Setup `dd9b844d07e4` · adapter `6c4185a41998` · stack `578cdc6d53b4` · concurrency 1 · last measured 2026-10-13T10:45:22.642506+00:00.

Guest-visible CPU/RAM and device probes do not attest reserved hardware or isolation. No GPU configuration was benchmarked in this snapshot.

## 6. Dated source register

- <a id="source-S1"></a> [S1: Official upstream OpenSandbox features, SDK example and Apache-2.0 license](https://github.com/opensandbox-group/OpenSandbox/blob/main/README.md) — accessed 2026-10-13.
- <a id="source-S2"></a> [S2: Official upstream lifecycle API, image/resource/GPU/volume/port contracts](https://github.com/opensandbox-group/OpenSandbox/blob/main/specs/sandbox-lifecycle.yml) — accessed 2026-10-13.
- <a id="source-S3"></a> [S3: Official server runtime/network/storage configuration](https://github.com/opensandbox-group/OpenSandbox/blob/main/server/configuration.md) — accessed 2026-10-13.
- <a id="source-S4"></a> [S4: Official Kubernetes controller templates, pools and snapshots](https://github.com/opensandbox-group/OpenSandbox/blob/main/docs/architecture/control-plane/operator.md) — accessed 2026-10-13.
- <a id="source-M1"></a> [M1: Official managed AgentRun overview](https://www.alibabacloud.com/help/en/agentrun/what-is-agentrun) — accessed 2026-10-13.
- <a id="source-P1"></a> [P1: Official FC CU tiers, promotional dates and metering](https://www.alibabacloud.com/help/en/functioncompute/pay-as-you-go-billing-methods) — accessed 2026-10-13.
- <a id="source-P2"></a> [P2: Official FC billing overview and CU coefficients](https://www.alibabacloud.com/help/en/functioncompute/billing-overview-of-fc) — accessed 2026-10-13.
- <a id="source-A1"></a> [A1: Inspected backend registry with no Alibaba provider](repo:src/core/providers/__init__.py) — accessed 2026-10-13.
- <a id="source-L1"></a> [L1: Existing Alibaba README, not a measured run](repo:providers/alibaba/README.md) — accessed 2026-10-13.

<!-- COMMON CONTRACT END -->

## Detailed provider dossier
# Alibaba: OpenSandbox and managed AgentRun (`alibaba`)

Reviewed: **2026-10-13**. Deployment: **hybrid** (an inventory entry covering two deployment choices, not a claim a hybrid deployment was tested). Customization: **deployment_dependent**.

## Two execution products, distinct guarantees

### OpenSandbox open-source backend

OpenSandbox is an **Apache-2.0 self-hosted execution service** with SDKs and lifecycle/execution APIs. It runs on operator-owned Docker or Kubernetes infrastructure. Current upstream repository is `opensandbox-group/OpenSandbox`; the former `alibaba/OpenSandbox` source URL resolves to current project content. Its openness does **not** make hosting/GPUs/storage/network free. [S1, S2]

The lifecycle protocol accepts OCI `image.uri` (including image authentication), resource limits, environment, entrypoint, timeout, volumes and network policy. CPU limits use quantities such as `500m`; memory uses `512Mi`/`1Gi`. These are requested constraints, not measured capacity or an invariant cluster quota. Per-deployment templates, available node resources and runtime support determine admission. [S2, S3]

**GPU:** the official `ResourceLimits` schema explicitly describes `gpu` device counts, e.g. `"1"`. This is protocol-level evidence. GPU usability still requires a backend that maps the request, GPU-capable nodes/device integration, compatible isolation runtime and image/libraries. A GPU-aware Kubernetes pod template/infrastructure is a deployment choice, not proof every Docker/Kata/Firecracker/Fast Sandbox deployment supports GPUs. No GPU request or execution was tested here. [S2, S3, S4]

Isolation is deployment-dependent: server configuration documents default OCI/runc or configured gVisor, Kata and Kubernetes-only Firecracker profiles. It is incorrect to call all OpenSandbox deployments microVMs. Current upstream also documents Fast Sandbox; do not generalize one backend's pause/resume or latency to all backends. [S1, S3]

### AgentRun managed service

Alibaba Cloud **AgentRun** is a separate managed, Function Compute-powered platform with an agent runtime, sandbox service, model management and tools. Its official overview documents prebuilt/**custom sandbox images**, Code Interpreter, Browser Use, file/session management and OSS/NAS mounts. It does not establish that the managed service accepts every upstream OpenSandbox field or uses the same backend/version. [M1]

The overview's **elastic GPU delivery is under model runtime**, not a GPU sandbox sizing promise. Managed sandbox GPU availability remains **unknown**. The same overview labels All-in-One/RL/Simulation sandbox types as future support; the repository README's blanket AIO availability is not accepted as current managed-service verification. Browser CDP/WebSocket support is also not a guarantee of arbitrary public preview ports. [M1, L1]

## Capability matrix

`conditional` means deployment-specific support, with both products scoped below. `documented` means source-level evidence, not newly measured runtime acceptance. `unknown` does not mean unavailable. There is no tested `alibaba` adapter in this repository.

| Feature ID | Support | Evidence | OpenSandbox versus AgentRun | Sources |
|---|---|---|---|---|
| `custom_image` | supported | documented | OpenSandbox OCI image URI/auth; AgentRun overview explicitly supports custom sandbox images. Managed image requirements not exhaustively verified. | S1, S2, M1 |
| `runtime_packages` | conditional | documented | Own dependencies can be baked into images; live installation depends on image permissions and configured egress. No managed live-pip guarantee tested. | S1, S2, S3, M1 |
| `cpu_sizing` | conditional | documented | OpenSandbox `resourceLimits.cpu`; admission/backend quotas apply. No current managed AgentRun sandbox CPU range verified. | S2, S4, M1 |
| `memory_sizing` | conditional | documented | OpenSandbox `resourceLimits.memory`; no invariant maximum. Managed sandbox memory tiers unverified. | S2, S4, M1 |
| `gpu` | conditional | documented | OpenSandbox protocol includes GPU, requires compatible backend/infrastructure. AgentRun model GPU is not sandbox GPU evidence; managed sandbox support unknown. | S2, S3, S4, M1 |
| `network_policy` | conditional | documented | OpenSandbox per-sandbox egress requires configured enforcement; Docker sidecar requires bridge, not host mode. AgentRun VPC/PrivateLink support is not proof of identical egress-policy schema. | S2, S3, M1 |
| `persistent_storage` | conditional | documented | OpenSandbox host/PVC/OSSFS volumes and backend-dependent snapshots; AgentRun documents OSS/NAS mounting. Ephemeral rootfs alone is not durable storage. | S2, S3, S4, M1 |
| `session_reuse` | supported | documented | OpenSandbox sandbox ID/lifecycle renewal/reuse; backend-specific pause/resume. AgentRun documents session management. No cross-request benchmark here. | S1, S2, S4, M1 |
| `shell` | conditional | documented | OpenSandbox `commands.run` shell workflow. AgentRun's chosen image/API controls availability; upstream shell API not automatically inherited. | S1, M1 |
| `file_transfer` | supported | documented | OpenSandbox file SDK/API, AgentRun file management; precise managed transport limits not verified. | S1, M1 |
| `ports_preview` | conditional | documented | OpenSandbox port endpoint and configured ingress/proxy. AgentRun Browser CDP is specific, not a general preview endpoint contract. | S2, S3, M1 |
| `self_hosting` | conditional | documented | OpenSandbox self-hostable Docker/Kubernetes; managed AgentRun backend not thereby self-hostable. | S1, S3, M1 |
| `cmek` | unknown | unverified | No native OpenSandbox or AgentRun sandbox-key API/coverage verified; storage/cluster encryption is an independent infrastructure choice. | S2, S3, M1 |

### Backend conditions that matter

- OpenSandbox egress sidecar attaches only when a policy is requested and enforcement is configured. DNS mode does not enforce CIDR/static IP rules; `dns+nft` adds nftables where available. IPv6 coverage has documented gaps. Merely accepting policy intent is not proof of enforcement. [S2, S3]
- Pool-mode pods are configured before allocation: volume/network policy requests cannot simply be injected per allocation; configure those in the pool template. [S4]
- Snapshot/pause behavior depends on backend: Kubernetes rootfs snapshots are not automatically live memory checkpoints, and snapshot metadata deletion does not guarantee deletion of pushed OCI images. Fast Sandbox has its own state-preservation contract. [S1, S2, S4]
- The upstream protocol/server sources were inspected on mutable `main`; pin and reverify a release before treating them as a deployed-version contract. No SDK or infrastructure was installed in this review.

## Inspected / tested configuration

An integrated Alibaba OpenSandbox & AgentRun adapter ([alibaba.py](../../src/core/providers/alibaba.py)) is registered in the core provider registry ([__init__.py](../../src/core/providers/__init__.py)) under `alibaba`, `opensandbox`, and `agentrun`. The integration supports both remote endpoints (`OPENSANDBOX_URL`, `AGENTRUN_SANDBOX_ENDPOINT`, `ALIBABA_CLOUD_AGENTRUN_API_KEY`) and managed local OpenSandbox runtime server execution ([server.py](../../deploy/opensandbox/server.py)).

A standalone native test runner ([runner.py](runner.py)), detailed API specification ([api_spec.md](api_spec.md)), and unit tests ([test_alibaba_provider.py](../../tests/test_alibaba_provider.py)) are implemented and verified. The Alibaba Cloud CLI (`aliyun-cli` 3.5.1) and official OpenSandbox Python SDK (`opensandbox` 1.1.1) are installed on the host. Live cloud authentication via OAuth token profile is verified active in `~/.aliyun/config.json` (`aliyun sts GetCallerIdentity` verified against Account ID `5487091114685721` with AgentRun endpoints in `ap-southeast-1`). [A1, L1]

## Pricing (USD): separate software, hosting, service and model costs

### OpenSandbox

The upstream Apache-2.0 software has **no usage license fee**. There is no single OpenSandbox cloud vCPU/RAM/GPU price: operator infrastructure, storage, ingress/egress, image registry, operations and optional model inference are independently billed. A zero license fee is not zero compute cost. [S1]

### Managed AgentRun

The AgentRun overview establishes Function Compute as underlying runtime. A **product-specific managed sandbox USD tariff** was not verified from the retrieved AgentRun pages; represent it as unknown rather than importing an old per-second estimate or all upstream capabilities. [M1]

For independently priced **Function Compute workloads**, official current references provide the following **standard pay-as-you-go regional monthly CU tiers**. These are useful underlying-service reference prices, **not a verified AgentRun sandbox quote**: [P1, P2]

| FC reference resource | Exact unit / tier | Standard amount |
|---|---|---|
| Tier 1 | USD per CU; monthly regional usage `(0, 100 million]` CU | $0.000020 |
| Tier 2 | USD per CU; `(100 million, 500 million]` CU | $0.000017 |
| Tier 3 | USD per CU; `>500 million` CU | $0.000014 |
| Active CPU usage conversion | CU per vCPU-second | 1.0 CU |
| CPU-workload memory conversion | CU per GB-second, active or idle/light sleep | 0.15 CU |
| Function invocation conversion | CU per 10,000 invocations | 75 CU |
| Disk conversion | CU per billable GB-second | 0.05 CU |

At Tier 1, these imply **$0.000020 per active vCPU-second**, **$0.000003 per GB-second of CPU-workload memory**, **$0.0015 per 10,000 invocations**, and **$0.000001 per billable GB-second of disk**, before other charges/minima. These derived equivalents are not universal sandbox rates. [P1, P2]

Important qualifications:

- Promotion columns on P1 explicitly cover **2024-08-27 through 2026-08-27**, before this review date; use the standard column here, not the expired promotional price. This observation alone is not a historical like-for-like price-increase claim.
- P1 documents CPU on-demand 1 ms metering, provisioned 10-second rounding, GPU 1-second rounding, hourly settlement, CU rounding and a **$0.01 minimum for an active/continuously occupied function-hour**. No sandbox session fee or monthly model-token bundle follows from these units. [P1]
- Official FC pages differ on some GPU coefficients/disk free quotas (P1's active/light-sleep 10 GB quota versus P2's 512 MB-free billing examples). Deep-sleep/snapshot conversion also differs from active memory. Do not choose a managed sandbox storage/GPU price from those inconsistent examples. [P1, P2]
- Model calls have provider/model token rates separate from runtime, and OSS/NAS, registry, observability and outbound Internet/CDT can add charges. Actual deployment, region, state and resource plan determine cost. [M1, P2]

## Sources

Official/upstream sources accessed 2026-10-13:

- **S1:** [OpenSandbox README, features, SDK example, Apache-2.0 license](https://github.com/opensandbox-group/OpenSandbox/blob/main/README.md)
- **S2:** [OpenSandbox lifecycle OpenAPI, including image, GPU resource limits, volumes and ports](https://github.com/opensandbox-group/OpenSandbox/blob/main/specs/sandbox-lifecycle.yml)
- **S3:** [OpenSandbox server configuration: runtimes, network enforcement, storage](https://github.com/opensandbox-group/OpenSandbox/blob/main/server/configuration.md)
- **S4:** [OpenSandbox Kubernetes controller: templates, pools and snapshots](https://github.com/opensandbox-group/OpenSandbox/blob/main/docs/architecture/control-plane/operator.md)
- **M1:** [Alibaba Cloud AgentRun overview: managed service capabilities](https://www.alibabacloud.com/help/en/agentrun/what-is-agentrun)
- **P1:** [Function Compute pay-as-you-go, tiers, promotion dates and metering](https://www.alibabacloud.com/help/en/functioncompute/pay-as-you-go-billing-methods)
- **P2:** [Function Compute billing overview, CU conversion and separate services](https://www.alibabacloud.com/help/en/functioncompute/billing-overview-of-fc)

Repository sources: **A1** [backend registry](../../src/core/providers/__init__.py), **L1** [existing README](README.md). No Alibaba result is presented as measured.
