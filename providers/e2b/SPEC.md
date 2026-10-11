<!-- COMMON CONTRACT START -->
# Provider contract: E2B (`e2b`)

**Sources reviewed:** 2026-10-13 · **Deployment:** `managed_runtime`

## 1. Executive summary and product boundary

Code Interpreter sandbox API; shared cloud, BYOC and self-operated Embed are distinct deployments.

Managed CPU-only Firecracker sandbox with custom image-derived templates and CPU/RAM sizing at template build time, network rules, pause/resume and private-beta volumes. Inspected integration uses e2b_code_interpreter.Sandbox.create(timeout=180) with no explicit template or resource sizing. Official default RAM descriptions conflict; tested allocation is unknown. BYOC is E2B-operated and distinct from self-hosted Embed.

Working adapter: [source](../../src/core/providers/e2b.py). Historical adapter hashes refer to measured revisions, not necessarily current source.

The preserved dossier describes the dated inspected configuration. New budget/lifecycle guardrails change current adapter defaults without changing historical cohort evidence; see [operations](../../CONTRIBUTING.md).

## 2. Documented contract vs measured adapter

Support describes the platform. Measured describes only a bounded oracle on a recorded setup. Documented-only and unverified entries remain coverage gaps.

| Capability | Platform support | Evidence state | Documented contract / scope | Measured adapter behavior | Sources |
|---|---|---|---|---|---|
| `custom_image` | supported | Documented | Managed templates can derive from Docker registry images, existing templates or parsed Dockerfiles. Distribution/package requirements apply; scratch/distroless and multistage Dockerfile conversion are unsupported. Adapter does not select/build a custom template, and the Code Interpreter SDK default must not be confused with generic Sandbox base. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [base-image](#source-base-image), [build](#source-build), [adapter](#source-adapter) |
| `runtime_packages` | supported | Measured (bounded fixture) | Existing dependency_install evaluations pass installation/import of an uploaded offline wheel in a private directory using --no-index/--no-deps. This tests runtime Python package installation, not internet package registry connectivity or apt/sudo privileges. | [dependency_install: 5/5](../../reports/index.html#raw?provider=e2b&run_id=bench-8fb2e58cc949), setup `b8b64fa8b3ea` | [evaluation](#source-evaluation), [fixtures](#source-fixtures) |
| `cpu_sizing` | supported | Documented | cpu_count/cpuCount is configured in Template.build, not a cpu keyword in this adapter's create call. Pricing lists 1-8 vCPUs; billing docs list 8 Hobby, 8+ Pro by support request, custom Enterprise. Adapter does not request CPU and reports do not inventory allocation. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [build](#source-build), [billing](#source-billing), [pricing](#source-pricing), [adapter](#source-adapter) |
| `memory_sizing` | supported | Documented | memory_mb/memoryMB at template build; pricing bills GiB-seconds and lists 1-8 GiB, with support-approved higher Pro/Enterprise limits in billing docs. Pricing says default 4 GiB, generic base-image docs say 512 MiB, and billing FAQ repeats 512 MiB. Do not infer default Code Interpreter or tested RAM from these descriptions; adapter leaves sizing unset. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [build](#source-build), [billing](#source-billing), [pricing](#source-pricing), [base-image](#source-base-image), [adapter](#source-adapter) |
| `gpu` | unsupported | Documented | Official GPU FAQ explicitly states sandboxes are CPU-only with no GPU SDK/CLI/API/template option; BYOC does not change this. Calling remote inference, installing CUDA libraries, or running an agent that orchestrates GPU training elsewhere is not local sandbox GPU access. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [gpu](#source-gpu), [pricing](#source-pricing) |
| `network_policy` | supported | Documented | Default public egress; allow_internet_access switch, IP/CIDR allow/deny rules, HTTP 80 Host and TLS 443 SNI domain allowlisting. Allow rules override denies; domain mode requires deny-all and allows default DNS server. Domain filtering does not cover QUIC/other ports and shared endpoints have limitations. Runtime update_network replaces rules. Adapter uses defaults and tests no custom policy. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [network](#source-network), [adapter](#source-adapter) |
| `persistent_storage` | supported | Documented | Pause/resume preserves filesystem and memory; paused retention is indefinite until explicit kill. Persistent volumes independent of sandbox lifetime are in private beta with locking/ownership limitations. Adapter kills at cleanup and mounts no volume; measured session state is not persistence after kill. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [persistence](#source-persistence), [volumes](#source-volumes), [adapter](#source-adapter), [evaluation](#source-evaluation) |
| `session_reuse` | supported | Measured (bounded fixture) | Connect to a running/paused sandbox; adapter retains one Code Interpreter sandbox across calls and session_state evaluation passes three separate filesystem calls. The fixture does not prove Python-variable continuity or pause/resume. Continuous runtime caps are 1h Hobby/24h Pro, reset after pause/resume; adapter timeout is 180s. | [session_state: 5/5](../../reports/index.html#raw?provider=e2b&run_id=bench-6421dab0ac23), setup `b8b64fa8b3ea` | [persistence](#source-persistence), [billing](#source-billing), [adapter](#source-adapter), [evaluation](#source-evaluation), [fixtures](#source-fixtures) |
| `shell` | supported | Documented | Provider commands.run supports foreground/background shell commands. Adapter instead submits all code to run_code with no language selector, so generic shell capability is not a native shell-request route in this integration. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [public-url](#source-public-url), [adapter](#source-adapter) |
| `file_transfer` | supported | Measured (bounded fixture) | files.write/read APIs; adapter transfers input bytes, reads output with format=bytes and hashes it. Existing artifact_roundtrip validates 26900 bytes; offline-wheel install also exercises binary input staging. One-level output listing does not establish recursive directory or maximum-size transfer support. | [artifact_roundtrip: 5/5](../../reports/index.html#raw?provider=e2b&run_id=bench-54a769a78ca5), setup `b8b64fa8b3ea`; [data_pipeline: 5/5](../../reports/index.html#raw?provider=e2b&run_id=bench-a3f6ae2c4c4f), setup `b8b64fa8b3ea` | [files](#source-files), [adapter](#source-adapter), [evaluation](#source-evaluation), [fixtures](#source-fixtures) |
| `ports_preview` | supported | Documented | get_host(port) generates a public HTTPS proxy URL for sandbox services, with optional public-access restrictions. URLs are public by default; proxy terminates TLS and can re-encrypt to configured HTTPS ports, not TLS passthrough. Adapter configures no service/preview or public-access restriction. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [public-url](#source-public-url), [adapter](#source-adapter) |
| `self_hosting` | conditional | Documented | Official open-source runtime/control plane is Apache-2.0. BYOC docs distinguish self-operated single-machine Embed on Linux/KVM from E2B-operated Enterprise clusters in customer AWS/GCP/Azure accounts. This adapter and its evaluations use managed Code Interpreter; no self-hosted parity or deployment was tested. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [open-source](#source-open-source), [byoc](#source-byoc), [adapter](#source-adapter) |
| `cmek` | unknown | Unverified | No provider-native customer KMS key binding/rotation/revocation contract was verified in inspected pricing, API-facing and BYOC documentation. Customer-account storage locality in BYOC does not itself establish CMEK coverage for all sandbox data. Adapter declares false but does not test key management. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [byoc](#source-byoc), [adapter](#source-adapter) |

## 3. Six residency surfaces

Source: [dated residency audit and original vendor citations](../../reports/docs/eu-data-residency.md). These are documented boundaries/gaps, not measured EU residency or GDPR certification.

| Surface | Documented boundary / verification gap |
|---|---|
| Compute | Default us-west1; Belgium Pro+ through support |
| Files / volumes / snapshots / backups | Shared-cluster scope unestablished; Enterprise BYOC templates/snapshots in customer VPC |
| Stdout / stderr / traces | Shared scope unestablished; BYOC runtime logs in customer VPC |
| Control plane / metadata | E2B management/metrics flows remain; confirm scope |
| Support access / subprocessors | Provider operates BYOC; confirm support access |
| External model / API calls | Selected model/API endpoint has a separate contract |

Benchmark location/request provenance is recorded separately in [tested configurations](tested-configurations.md).

## 4. Dated pricing and billing units

Monthly plan fee plus provisioned vCPU/RAM per running sandbox-second; paused/killed compute not billed; included sandbox storage.

| SKU / resource | Original billing unit | USD list amount | Sources |
|---|---|---:|---|
| Sandbox CPU | vCPU-second | 0.000014 | [pricing](#source-pricing) |
| Sandbox RAM | GiB-second | 0.0000045 | [pricing](#source-pricing) |
| Included sandbox storage | included plan allocation, no extra charge | 0 | [pricing](#source-pricing) |
| Hobby plan | project-month, plus usage | 0 | [pricing](#source-pricing), [billing](#source-billing) |
| Pro plan (100 concurrent sandboxes) | project-month, plus usage | 150 | [pricing](#source-pricing) |
| Pro+ (600 concurrent sandboxes) | project-month including plan/add-on, plus usage | 650 | [pricing](#source-pricing) |
| Pro++ (1100 concurrent sandboxes) | project-month including plan/add-ons, plus usage | 1150 | [pricing](#source-pricing) |
| Enterprise minimum usage commitment | month, minimum not a unit compute rate | 3000 | [pricing](#source-pricing) |
| Enterprise/BYOC contracted rate | contract | Unknown | [pricing](#source-pricing), [byoc](#source-byoc) |
| Independent private-beta Volume storage rate | not published in inspected sources | Unknown | [volumes](#source-volumes), [pricing](#source-pricing) |
| Standalone network egress rate | not published in inspected pricing | Unknown | [pricing](#source-pricing) |

Exact public rates retrieved 2026-10-13; no invoice or historical price comparison verified. Hobby has one-time $100 credits, 20 concurrency/1h continuous runtime/10 GiB storage; Pro 100 concurrency/24h/20 GiB storage and no additional credits. Pricing default is 2 vCPU/4 GiB while generic base/billing FAQ say 2 vCPU/512 MiB; Code Interpreter allocation and tier are unverified. 'Storage free' is scoped to included sandbox storage, not an independently priced beta-volume contract. Report fixed $0.00004/sec is estimate_unverified_rates and client wall time is not metered runtime.

## 5. Recorded configuration and guest inventory

[All settings, client stacks, attempt IDs and observations](tested-configurations.md) · [Machine-readable export](tested-configurations.json)

- Setup `1c8788fe1d12` · adapter `44055e4ac080` · stack `7e13445a554e` · concurrency 1 · last measured 2026-10-13T16:28:30.167215+00:00.
- Setup `b8b64fa8b3ea` · adapter `44055e4ac080` · stack `7e13445a554e` · concurrency 3 · last measured 2026-10-13T07:46:06.220267+00:00.
- Setup `b8b64fa8b3ea` · adapter `44055e4ac080` · stack `7e13445a554e` · concurrency 1 · last measured 2026-10-13T07:44:30.898398+00:00.

Guest-visible CPU/RAM and device probes do not attest reserved hardware or isolation. No GPU configuration was benchmarked in this snapshot.

## 6. Dated source register

- <a id="source-pricing"></a> [pricing: E2B Pricing](https://e2b.dev/pricing.md) — accessed 2026-10-13.
- <a id="source-billing"></a> [billing: Billing & limits](https://docs.e2b.dev/billing.md) — accessed 2026-10-13.
- <a id="source-base-image"></a> [base-image: Template base image and default resources](https://docs.e2b.dev/template/base-image.md) — accessed 2026-10-13.
- <a id="source-build"></a> [build: Template build resources and minimum free disk](https://docs.e2b.dev/template/build.md) — accessed 2026-10-13.
- <a id="source-gpu"></a> [gpu: Does E2B support GPUs?](https://docs.e2b.dev/faq/gpu-support.md) — accessed 2026-10-13.
- <a id="source-network"></a> [network: Internet access and fine-grained network controls](https://docs.e2b.dev/network/internet-access.md) — accessed 2026-10-13.
- <a id="source-public-url"></a> [public-url: Sandbox public URL](https://docs.e2b.dev/network/public-url.md) — accessed 2026-10-13.
- <a id="source-files"></a> [files: Read & write files](https://docs.e2b.dev/filesystem/read-write.md) — accessed 2026-10-13.
- <a id="source-persistence"></a> [persistence: Sandbox persistence](https://docs.e2b.dev/sandbox/persistence.md) — accessed 2026-10-13.
- <a id="source-volumes"></a> [volumes: Volumes overview (private beta)](https://docs.e2b.dev/volumes.md) — accessed 2026-10-13.
- <a id="source-open-source"></a> [open-source: E2B Open Source](https://e2b.dev/open-source.md) — accessed 2026-10-13.
- <a id="source-byoc"></a> [byoc: BYOC versus self-hosted Embed](https://docs.e2b.dev/byoc.md) — accessed 2026-10-13.
- <a id="source-adapter"></a> [adapter: Inspected working-tree E2B adapter](../../src/core/providers/e2b.py) — accessed 2026-10-13.
- <a id="source-evaluation"></a> [evaluation: Existing E2B evaluations (schema version 2)](../../reports/data/attempts/e2b_evaluation.json) — accessed 2026-10-13.
- <a id="source-fixtures"></a> [fixtures: Offline dependency and cross-call filesystem fixtures](../../src/bench/suites/workflows.py) — accessed 2026-10-13.

<!-- COMMON CONTRACT END -->

## Detailed provider dossier
# E2B — evidence-first specification

Reviewed and official sources accessed **2026-10-13**, matching host UTC and environment dates. Companion: [spec.json](spec.json), conforming to [spec.schema.json](../spec.schema.json). This specification covers managed E2B sandboxes and the repository's **Code Interpreter SDK** integration, not external model inference or GPU training infrastructure.

## Product and customization

**Deployment:** `managed_runtime`. **Customization:** `custom_image_and_resources`.

E2B provides CPU-only Firecracker microVMs, customizable via managed image-derived templates. CPU and memory are template-build options; they are not supplied by this adapter's sandbox creation call. E2B also documents Enterprise **BYOC** on AWS/GCP/Azure, operated by E2B, and a distinct self-operated **Embed** runtime on a single Linux/KVM machine. These deployment options were not tested by this integration. [base-image] [build] [gpu] [byoc] [open-source]

## Capability matrix

| Feature ID | Support / evidence | Contract and boundary |
| --- | --- | --- |
| `custom_image` | Supported / documented | Docker-image/existing-template bases and Dockerfile conversion. Distribution/package requirements; no scratch/distroless or multistage conversion. [base-image] |
| `runtime_packages` | Supported / measured | Offline wheel install/import passes in current evaluations; no external package registry test implied. [evaluation] [fixtures] |
| `cpu_sizing` | Supported / documented | Template `cpu_count`/`cpuCount`; pricing range 1–8 vCPU, higher support-approved/Enterprise limits documented separately. [build] [billing] [pricing] |
| `memory_sizing` | Supported / documented | Template `memory_mb`/`memoryMB`; GiB-second billing. **Official default-memory descriptions disagree.** [base-image] [billing] [pricing] |
| `gpu` | **Unsupported / documented** | Official FAQ says CPU-only, including BYOC, with no GPU parameter in SDK/CLI/API/templates. [gpu] |
| `network_policy` | Supported / documented | Default egress, internet switch, IP/CIDR rules and domain allowlists with protocol limitations; runtime rule replacement. [network] |
| `persistent_storage` | Supported / documented | Pause/resume filesystem+memory; private-beta independent volumes with limitations. Kill is terminal. [persistence] [volumes] |
| `session_reuse` | Supported / measured | Retained sandbox handle; report verifies three filesystem-state calls, not memory pause/resume or Python globals. [adapter] [evaluation] [fixtures] |
| `shell` | Supported / documented | `commands.run`, including background server examples; adapter uses Python `run_code` instead. [public-url] [adapter] |
| `file_transfer` | Supported / measured | Native `files` APIs; 26,900-byte artifact bytes/hash validation and uploaded binary-wheel installation. [files] [evaluation] |
| `ports_preview` | Supported / documented | `get_host(port)` public HTTPS service URL; authentication restrictions are optional. No preview tested here. [public-url] |
| `self_hosting` | Conditional / documented | Apache-2.0 runtime/Embed; operator supplies Linux/KVM host. Managed Enterprise BYOC is a different arrangement. [open-source] [byoc] |
| `cmek` | Unknown / unverified | No customer-KMS binding/rotation/revocation contract verified; customer-account residency alone is insufficient. [byoc] |

### Sizing, network and persistence details

- `Template.build` takes CPU/RAM settings; documented pricing lists 1–8 vCPUs/1–8 GiB. Billing docs list Hobby maxima of 8/8, Pro 8+ by support request, and custom Enterprise limits. The pricing page associates custom resources with Pro, while the build/billing pages show configurable resource fields; exact account entitlement requires verification. [build] [billing] [pricing]
- **Default ambiguity:** pricing calls the default sandbox **2 vCPU / 4 GiB**; generic base-template docs and the billing optimization FAQ state **2 vCPU / 512 MiB**. The adapter imports `e2b_code_interpreter.Sandbox`, not generic `e2b.Sandbox`, and selects no template. None of these descriptions proves its actual allocated RAM. [pricing] [base-image] [billing] [adapter]
- `min_free_disk_mb` is a **post-build free-space target**, not total disk size and not a `Sandbox.create` disk parameter. Plan storage allocations are 10 GiB Hobby and 20+ GiB Pro in billing docs. [build] [billing]
- Egress allow rules take precedence over denies. Domain allowlisting requires deny-all, matches HTTP Host on port 80/TLS SNI on 443, and permits the default DNS server. It does not cover UDP/QUIC or arbitrary ports; shared CDN endpoints can weaken hostname isolation. A successful TCP connection alone is not proof of permitted application traffic. `update_network` replaces rather than merges rules. [network]
- Paused sandboxes retain filesystem+memory indefinitely; running continuous limits are 1 hour Hobby/24 hours Pro and reset after pause/resume. Default timeout lifecycle action is kill unless pause is configured. Network clients disconnect during pause. Volumes independent of sandboxes are **private beta**, with locking/ownership/performance limitations. [persistence] [billing] [volumes]
- Calling remote inference from sandbox code, or coordinating training on a separate GPU host, does not change the explicit **no local sandbox GPU** contract. [gpu]

## Tested integration and configuration

Read [adapter](../../src/core/providers/e2b.py) [adapter], [evaluations](../../reports/data/attempts/e2b_evaluation.json) [evaluation], [burst report](../../reports/data/attempts/e2b_burst_evaluation.json) [burst] and [workload fixtures](../../src/bench/suites/workflows.py) [fixtures]. See [tested-configurations.md](tested-configurations.md) and [tested-configurations.json](tested-configurations.json), **main-generated export pending at refresh**. No new cloud execution or web research was performed; official source retrieval remains 2026-10-13.

| Item | Requested / implemented | Observed / unverified |
| --- | --- | --- |
| SDK path | Synchronous `e2b_code_interpreter.Sandbox` operations offloaded with `asyncio.to_thread` | Provenance reports `e2b-code-interpreter` **2.10.5**, client Python **3.13.13**, Darwin/arm64. |
| Template/resources options | Adapter now accepts `template`; CPU/RAM still derive from selected template rather than create-time sizing. Latest recorded request `template=null`, `cpu=null`, `memory=null` | Remote Python **3.13.16** and two guest-visible logical CPUs; template identity and reserved allocation still unverified. No custom-template configuration tested. |
| Lifecycle | `Sandbox.create(..., timeout=180)` once per adapter; retained across calls; kill during cleanup/teardown | No pause, snapshot, volume mount or durable state beyond kill exercised. |
| Execution | `run_code`, prepended `os.chdir`, input/output env vars and request timeout | No language selector forwarded; generic provider shell support is broader than adapter shell-request support. |
| Files | Input bytes written under prepared input dir; output list/read `format="bytes"`, SHA-256 | Tested artifact and binary-wheel input succeed; recursive collection not established. |
| Network/GPU options | Adapter accepts `allow_internet_access`; latest request **true**, GPU **null** | No custom restriction, preview/privacy or GPU-enabled test; broader fine-grained network APIs are provider capabilities, not exposed adapter fields. |
| Configuration/provenance | Latest `configuration.requested`, config ID **`b8b64fa8b3ea`**, adapter/stack and per-suite evaluator contract hashes | Request recording and guest inventory are separate; account tier, reserved resources and immutable image identity unknown. Earlier label-only config ID `39ed10c5d0c2` remains incomplete. |

At refresh the main report has **120 records**, separated by campaign below. [evaluation]

| Campaign / UTC window on 2026-10-13 | Records | Bounded result |
| --- | ---: | --- |
| `campaign-7135acd6f4eb`, 06:36 | 2 | Initial artifact/ready checks pass. |
| `campaign-cf173bdae961`, 06:42–06:45 | 55 | All pass, including five timeout response-budget checks. |
| `campaign-c40bf51ceb15`, 07:13 | 3 | Schema-1 guest inventories pass. |
| `campaign-2c725e417820`, 07:41–07:44 | 60 | **59 pass / 1 fail**; five repeats per 12 suites. Session calls, sentinel-based error recovery, binary/SHA-256 transfer, ETL artifact, dependency install, SQLite and exact 128-KiB output pass. |

Latest timeout status is `timed_out` in **all five** trials; **four** pass the client response-budget check and **one** fails only `bounded_response`. Run `bench-33d31916a325` takes **10,876.174 ms** in `execute_ms`, exceeding `(request timeout + 5 s)` = **10,000 ms**; timeout-observed, did-not-finish, execution-status and cleanup checks are true. This is one observed client/SDK response-budget failure, **not an SLA measurement or platform-reliability conclusion**. Timeout responses do not independently prove the remote process was killed. Earlier all-pass rows remain separate evidence. Costs remain unverified estimates. [evaluation] [validation]

| Representative run | Evidence |
| --- | --- |
| `bench-3daade047bcb` | 26,900-byte output saved with host bytes/hash checks. |
| `bench-c6673f8738a3` | Remote Python 3.13.16 and ready marker; client total 2,201.847 ms, creation inside `execute_ms`. |
| `bench-c581d0f48798` | Three distinct filesystem calls preserve value 42. |
| `bench-fd6a2be1e6f6` | Uploaded offline wheel installed/imported; fixture value 43. |
| `bench-d9b697f3c1a3` | Timeout observed and bounded response/cleanup pass. |
| `bench-54a769a78ca5` | Latest binary roundtrip exact bytes/SHA-256 pass, 26,900 bytes. |
| `bench-a3f6ae2c4c4f` | Latest 10k-row ETL metrics and exact `summary.json` bytes/hash pass. |
| `bench-6421dab0ac23` | Latest three distinct API calls preserve filesystem state. |
| `bench-33d31916a325` | Latest timeout status observed, client response-budget check fails. |
| `bench-700e8fa525e4` | Latest schema-1 inventory passes. |

### Guest runtime inventory and versioned provenance

Latest five inventories report **2 visible logical CPUs / affinity 2**, cpuset **`0-1`**, sysconf physical memory **2,079,141,888 bytes**, filesystem total/free **1,039,572,992 bytes**, Python **3.13.16**, kernel **6.1.158+**, Linux/x86_64 and UID **0**. CPU quota/memory-limit cgroup fields are null. `bash`, `gcc`, `git`, `node`, `pip` are present; `nvidia-smi` is absent, device list empty. These are guest-visible observations, not reserved CPU/RAM/storage attestation or a GPU provisioning test. They neither resolve the official default-memory conflict nor establish a new memory ceiling. [evaluation] [inventory]

Latest adapter hash prefix **`44055e4ac080`**, stack hash prefix **`7e13445a554e`**, client SDK **2.10.5** / Python **3.13.13**. `evaluation_contract_sha256` is per suite; retain it with workload hash, adapter, stack, config and concurrency when comparing results. The recovery fixture now writes a filesystem sentinel before the expected exception and reads it in the next API call; three-call session continuity is still filesystem-based, not a Python-global or pause/resume oracle. The dependency fixture uses an uploaded offline wheel with `--no-index --no-deps --target`, so success does not establish internet registry access. [evaluation] [fixtures] [validation]

Separate burst campaign `campaign-d22f19df9fe1` has **12/12 CPU-stress passes at concurrency 3** (07:45–07:46), default template/network requests and no GPU. This small sample does not establish a capacity or latency SLA. `cold_start_ms=0` is not zero startup time; client wall time and guest-visible inventory do not establish image identity, reserved allocation, geographic placement or metered lifetime. [burst] [inventory]

## Current official pricing (USD)

Exact values from [pricing](https://e2b.dev/pricing.md) [pricing], accessed 2026-10-13; [billing] supplies lifecycle and quota details.

| Resource / plan | Amount | Exact unit / scope |
| --- | ---: | --- |
| CPU | $0.000014 | vCPU-second while running |
| RAM | $0.0000045 | GiB-second while running |
| Sandbox storage | $0 | Included plan allocation; not unlimited storage |
| Hobby | $0 | Monthly plan fee + usage; one-time $100 credits |
| Pro | $150 | Monthly plan fee + usage; 100 concurrency |
| Pro+ / Pro++ | $650 / $1,150 | Total monthly plan/add-on fees + usage; 600 / 1,100 concurrency |
| Enterprise minimum | $3,000 | Monthly usage minimum, not a per-resource rate |
| Negotiated Enterprise/BYOC rates | Unknown | Contract required |
| Independent private-beta Volume rate | Unknown | No explicit rate verified in inspected sources |
| Standalone network egress rate | Unknown | Not itemized in inspected pricing |

Paused/killed sandbox compute is not billed. Pro grants no additional credits. Storage is 10 GiB Hobby / 20 GiB Pro on the pricing page, with larger support-approved storage described in billing docs. The statement that sandbox storage is included does not by itself establish an independent-volume price. [pricing] [billing] [volumes]

**Illustrative rates, not tested allocations:** 2 vCPU + 4 GiB yields `2×0.000014 + 4×0.0000045 = $0.000046/second`; 2 vCPU + 0.5 GiB yields `$0.00003025/second`. Both calculations are shown because the official default descriptions differ, not as competing measured bills. Report `rate_per_sec=0.00004` is a fixed unverified estimate and client wall time is not metered runtime. No comparable dated official historical prices were collected; **no price-increase claim is supported**. [pricing] [evaluation]

## Sources

All accessed **2026-10-13**; relative repository paths denote inspected working-tree evidence.

- [pricing]: https://e2b.dev/pricing.md
- [billing]: https://docs.e2b.dev/billing.md
- [base-image]: https://docs.e2b.dev/template/base-image.md
- [build]: https://docs.e2b.dev/template/build.md
- [gpu]: https://docs.e2b.dev/faq/gpu-support.md
- [network]: https://docs.e2b.dev/network/internet-access.md
- [public-url]: https://docs.e2b.dev/network/public-url.md
- [files]: https://docs.e2b.dev/filesystem/read-write.md
- [persistence]: https://docs.e2b.dev/sandbox/persistence.md
- [volumes]: https://docs.e2b.dev/volumes.md
- [open-source]: https://e2b.dev/open-source.md
- [byoc]: https://docs.e2b.dev/byoc.md
- [adapter]: [src/core/providers/e2b.py](../../src/core/providers/e2b.py)
- [evaluation]: [reports/data/attempts/e2b_evaluation.json](../../reports/data/attempts/e2b_evaluation.json)
- [fixtures]: [src/bench/suites/workflows.py](../../src/bench/suites/workflows.py)
- [burst]: [reports/data/attempts/e2b_burst_evaluation.json](../../reports/data/attempts/e2b_burst_evaluation.json)
- [inventory]: [scripts/runtime_inventory.py](../../scripts/runtime_inventory.py)
- [validation]: [src/bench/validation.py](../../src/bench/validation.py)
- Tested-configuration navigation (main export pending): [Markdown](tested-configurations.md), [JSON](tested-configurations.json).
