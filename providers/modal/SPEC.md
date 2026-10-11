<!-- COMMON CONTRACT START -->
# Provider contract: Modal (`modal`)

**Sources reviewed:** 2026-10-13 · **Deployment:** `managed_runtime`

## 1. Executive summary and product boundary

Sandbox exec/filesystem API; Function and model-hosting performance are separate.

Managed Sandbox API with custom built/registry images, fractional physical CPU requests and limits, memory requests and limits in MiB, optional GPUs on gVisor, network controls, volumes and snapshots. The inspected adapter requests debian_slim, 2 physical cores and 2048 MiB, not a hard 2-vCPU/4-GB machine; observed reports do not inventory the allocation.

Working adapter: [source](../../src/core/providers/modal.py). Historical adapter hashes refer to measured revisions, not necessarily current source.

The preserved dossier describes the dated inspected configuration. New budget/lifecycle guardrails change current adapter defaults without changing historical cohort evidence; see [operations](../../CONTRIBUTING.md).

## 2. Documented contract vs measured adapter

Support describes the platform. Measured describes only a bounded oracle on a recorded setup. Documented-only and unverified entries remain coverage gaps.

| Capability | Platform support | Evidence state | Documented contract / scope | Measured adapter behavior | Sources |
|---|---|---|---|---|---|
| `custom_image` | supported | Documented | Sandbox.create accepts modal.Image; method-chained, external registry and published named images are documented. Cached external tags are treated as immutable after pull; pin versions for reproducibility. Adapter uses Image.debian_slim without a pinned Python version or image digest. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [sandbox](#source-sandbox), [api](#source-api), [adapter](#source-adapter) |
| `runtime_packages` | supported | Measured (bounded fixture) | Arbitrary exec supports runtime package installation subject to permissions and egress. Existing dependency_install evaluations pass an uploaded offline wheel installed with --no-index/--no-deps into a private target; this does not measure PyPI availability or system-package installation. | [dependency_install: 5/5](../../reports/index.html#raw?provider=modal&run_id=bench-166f80bc19da), setup `c6eceedf16a1` | [sandbox](#source-sandbox), [evaluation](#source-evaluation), [fixtures](#source-fixtures) |
| `cpu_sizing` | supported | Documented | cpu is fractional physical cores (1 physical core = 2 vCPU equivalent); a scalar is a request, (request, limit) adds throttling. Default request is 0.125 physical cores. Current docs enforce a scheduling maximum without publishing its number on the cited pages. Adapter cpu=2 is a request for 2 physical cores, not 2 vCPUs; allocation/burst usage is not measured. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [resources](#source-resources), [sandbox-resources](#source-sandbox-resources), [api](#source-api), [adapter](#source-adapter) |
| `memory_sizing` | supported | Documented | memory uses MiB; a scalar is a guaranteed request, (request, limit) adds a hard OOM ceiling. Default is 128 MiB. Adapter memory=2048 requests 2 GiB and supplies no hard limit. Report cost.details.ram_gb=4 is an unverified estimator input, not measured RAM. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [resources](#source-resources), [sandbox-resources](#source-sandbox-resources), [adapter](#source-adapter), [evaluation](#source-evaluation) |
| `gpu` | conditional | Documented | Explicit Sandbox GPU reservation exists; GPU sandboxes require runtime=gvisor and are subject to preemption. GPU Function/model-hosting support is not the evidence used here. Adapter requests no GPU; GPU access and availability were not benchmarked. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [sandbox](#source-sandbox), [sandbox-resources](#source-sandbox-resources), [api](#source-api), [adapter](#source-adapter) |
| `network_policy` | supported | Documented | Public outbound IP access by default; block_network, outbound CIDR allowlists, beta domain allowlists and inbound CIDR allowlists are available. Domain filtering uses TLS SNI on 443, does not inspect Host/path, permits unrestricted DNS unless fully blocked, and has domain-fronting limitations. Dynamic updates are experimental and require allowlist types at creation. Adapter sets none of these controls. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [network](#source-network), [api](#source-api), [adapter](#source-adapter) |
| `persistent_storage` | supported | Documented | Mount named Volumes/NetworkFileSystems or snapshot filesystem/directory state for later Sandboxes. Root filesystem persistence during an active sandbox is distinct from storage surviving termination. Adapter mounts no durable storage and terminates on cleanup. Sandbox disk cannot be enlarged; VM root disk is fixed at 512 GiB. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [sandbox](#source-sandbox), [api](#source-api), [sandbox-resources](#source-sandbox-resources), [adapter](#source-adapter) |
| `session_reuse` | supported | Measured (bounded fixture) | from_id/from_name can reconnect to running sandboxes. Current adapter retains its handle across calls; existing session_state evaluations pass three filesystem-state API calls. Each exec starts a new process, so Python globals are not the measured continuity. Documented lifetime defaults to 300 seconds, maximum 24 hours; adapter uses 180 seconds and terminates at cleanup. | [session_state: 5/5](../../reports/index.html#raw?provider=modal&run_id=bench-317552374240), setup `c6eceedf16a1` | [sandbox](#source-sandbox), [api](#source-api), [adapter](#source-adapter), [evaluation](#source-evaluation), [fixtures](#source-fixtures) |
| `shell` | supported | Documented | Sandbox.exec supports arbitrary command argv and PTYs. Adapter selects python -c for Python and bash -c otherwise. Existing evaluated workloads primarily exercise Python and its subprocesses, not a separately evaluated shell-language request. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [api](#source-api), [adapter](#source-adapter), [evaluation](#source-evaluation) |
| `file_transfer` | supported | Measured (bounded fixture) | Native filesystem write_bytes/read_bytes and local copy APIs are documented. Adapter stages input bytes and lists output directory entries; existing artifact_roundtrip reports pass byte/hash validation for a 26900-byte artifact. Nested-directory export and large-file API limits are not established by that result. | [artifact_roundtrip: 5/5](../../reports/index.html#raw?provider=modal&run_id=bench-f47b98a1e3eb), setup `c6eceedf16a1`; [data_pipeline: 5/5](../../reports/index.html#raw?provider=modal&run_id=bench-fb8274ea4362), setup `c6eceedf16a1` | [api](#source-api), [adapter](#source-adapter), [evaluation](#source-evaluation) |
| `ports_preview` | supported | Documented | Authenticated HTTP/WebSocket connect tokens and explicit TLS/plain TCP or HTTP/2 tunnels exist. Default sandbox has no public inbound listener. Tunnel custom domains require Team/Enterprise and manual onboarding. Adapter does not expose ports or generate previews. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [network](#source-network), [api](#source-api), [adapter](#source-adapter) |
| `self_hosting` | unknown | Unverified | Inspected official Sandbox/security docs describe Modal-operated compute. No full customer-operated Sandbox control/data-plane distribution was verified. An open-source client, runtime=vm or underlying cloud selection does not establish self-hosting. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [sandbox](#source-sandbox), [security](#source-security) |
| `cmek` | unknown | Unverified | Provider-managed encryption at rest is documented. Alpha customer-supplied encryption keys (CSEK) are explicitly supported for directory snapshots only; customer passes raw key material on create/mount and Modal does not persist it. This is not verified KMS-backed CMEK for the whole sandbox, volumes, images or logs. Adapter configures neither CSEK nor CMEK. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [security](#source-security), [csek](#source-csek), [adapter](#source-adapter) |

## 3. Six residency surfaces

Source: [dated residency audit and original vendor citations](../../reports/docs/eu-data-residency.md). These are documented boundaries/gaps, not measured EU residency or GDPR certification.

| Surface | Documented boundary / verification gap |
|---|---|
| Compute | Strict EEA compute pinning available; baseline unpinned |
| Files / volumes / snapshots / backups | Managed volumes, images and saved snapshots: US; regional bucket mounts separate |
| Stdout / stderr / traces | Sandbox stdout/stderr: US |
| Control plane / metadata | Lifecycle calls: US-east |
| Support access / subprocessors | Exact support/subprocessor access boundary needs verification |
| External model / API calls | Selected model/API endpoint has a separate contract |

Benchmark location/request provenance is recorded separately in [tested configurations](tested-configurations.md).

## 4. Dated pricing and billing units

Sandbox/Notebook-specific per-second CPU and memory usage, charged at max(request, actual); GPU rates use standard GPU schedule; storage/egress and plan fees separate.

| SKU / resource | Original billing unit | USD list amount | Sources |
|---|---|---:|---|
| Sandbox CPU | physical-core-second (2 vCPU equivalent) | 0.00003942 | [pricing](#source-pricing) |
| Sandbox memory | GiB-second | 0.00000667 | [pricing](#source-pricing) |
| NVIDIA B300 | GPU-second | 0.001972 | [pricing](#source-pricing) |
| NVIDIA B200 | GPU-second | 0.001736 | [pricing](#source-pricing) |
| NVIDIA H200 SXM | GPU-second | 0.001261 | [pricing](#source-pricing) |
| NVIDIA H100 SXM5 | GPU-second | 0.001097 | [pricing](#source-pricing) |
| NVIDIA RTX PRO 6000 | GPU-second | 0.000842 | [pricing](#source-pricing) |
| NVIDIA A100 80 GB | GPU-second | 0.000694 | [pricing](#source-pricing) |
| NVIDIA A100 40 GB | GPU-second | 0.000583 | [pricing](#source-pricing) |
| NVIDIA L40S | GPU-second | 0.000542 | [pricing](#source-pricing) |
| NVIDIA A10 | GPU-second | 0.000306 | [pricing](#source-pricing) |
| NVIDIA L4 | GPU-second | 0.000222 | [pricing](#source-pricing) |
| NVIDIA T4 | GPU-second | 0.000164 | [pricing](#source-pricing) |
| Volumes | GiB-month | 0.09 | [pricing](#source-pricing) |
| Network egress | GiB | 0.04 | [pricing](#source-pricing) |
| Starter plan base fee | workspace-month, plus usage | 0 | [pricing](#source-pricing) |
| Team plan base fee | workspace-month, plus usage | 250 | [pricing](#source-pricing) |
| Enterprise plan | contract | Unknown | [pricing](#source-pricing) |

Public list rates retrieved 2026-10-13, not invoice verification. Sandbox CPU/RAM rates must not be replaced with lower Function rates. Minimum request 0.125 physical cores/128 MiB; bursting can increase billing. Pricing lists region premiums 1.15-1.75x and non-preemptible execution 3x, subject to applicable product/configuration. Starter includes $30/month compute, Team $100/month; Volumes include 1 TiB/month free and egress allowances are plan-dependent (1/10/100 TiB). GPU prices are listed rates, not confirmed capacity for every type. Report costs explicitly use unverified rates/client wall time and inconsistent resource assumptions. No historical price-change conclusion is supported by this retrieval.

## 5. Recorded configuration and guest inventory

[All settings, client stacks, attempt IDs and observations](tested-configurations.md) · [Machine-readable export](tested-configurations.json)

- Setup `e8ca7ef579ec` · adapter `71538074cc69` · stack `761a2e0e7f7e` · concurrency 1 · last measured 2026-10-13T16:27:54.905648+00:00.
- Setup `c6eceedf16a1` · adapter `71538074cc69` · stack `761a2e0e7f7e` · concurrency 3 · last measured 2026-10-13T07:46:06.033036+00:00.
- Setup `c6eceedf16a1` · adapter `71538074cc69` · stack `761a2e0e7f7e` · concurrency 1 · last measured 2026-10-13T07:44:38.238088+00:00.

Guest-visible CPU/RAM and device probes do not attest reserved hardware or isolation. No GPU configuration was benchmarked in this snapshot.

## 6. Dated source register

- <a id="source-sandbox"></a> [sandbox: Modal Sandboxes guide](https://modal.com/docs/guide/sandboxes) — accessed 2026-10-13.
- <a id="source-api"></a> [api: modal.Sandbox Python reference](https://modal.com/docs/sdk/py/latest/Sandbox) — accessed 2026-10-13.
- <a id="source-resources"></a> [resources: Configuring CPU, memory, and disk](https://modal.com/docs/guide/resources) — accessed 2026-10-13.
- <a id="source-sandbox-resources"></a> [sandbox-resources: Sandbox resources and pricing](https://modal.com/docs/guide/sandbox-resources) — accessed 2026-10-13.
- <a id="source-network"></a> [network: Sandbox networking and security](https://modal.com/docs/guide/sandbox-networking) — accessed 2026-10-13.
- <a id="source-pricing"></a> [pricing: Modal pricing, including Sandbox + Notebooks section](https://modal.com/pricing) — accessed 2026-10-13.
- <a id="source-security"></a> [security: Security and privacy at Modal](https://modal.com/docs/guide/security) — accessed 2026-10-13.
- <a id="source-csek"></a> [csek: Customer Supplied Encryption Keys (alpha)](https://modal.com/docs/guide/customer-supplied-encryption-keys) — accessed 2026-10-13.
- <a id="source-adapter"></a> [adapter: Inspected working-tree Modal adapter](../../src/core/providers/modal.py) — accessed 2026-10-13.
- <a id="source-evaluation"></a> [evaluation: Existing Modal evaluations (schema version 2)](../../reports/data/attempts/modal_evaluation.json) — accessed 2026-10-13.
- <a id="source-fixtures"></a> [fixtures: Offline dependency and cross-call filesystem fixtures](../../src/bench/suites/workflows.py) — accessed 2026-10-13.

<!-- COMMON CONTRACT END -->

## Detailed provider dossier
# Modal Sandbox — evidence-first specification

Reviewed and official pages accessed **2026-10-13**. Host UTC retrieval date agrees with the environment date. Machine-readable companion: [spec.json](spec.json), using [spec.schema.json](../spec.schema.json). Scope is the managed **Sandbox** product and the inspected working-tree adapter. Official capabilities, adapter requests, and report observations are separate evidence layers.

## Product and customization

**Deployment:** `managed_runtime`. **Customization:** `custom_image_and_resources`.

Modal exposes a direct Sandbox API for untrusted code, separate from its Function/inference interface. Images, resource requests, network policies, mounts and entrypoint commands are configurable in the managed service. Sandboxes can use gVisor or a full-kernel VM; leaving `runtime` unset lets Modal choose. GPU sandboxes specifically require **gVisor**. Current guest inventory reports a `4.19.0-gvisor` kernel string, but is not independent isolation attestation. **No GPU-enabled configuration was tested.** [sandbox] [api] [sandbox-resources] [evaluation]

## Capability matrix

`measured` refers only to the bounded report/fixture described; `unknown` means no affirmative or explicit negative contract was verified.

| Feature ID | Support / evidence | Contract and boundary |
| --- | --- | --- |
| `custom_image` | Supported / documented | Method-chained, registry and published named `modal.Image` values. External tags are cached as immutable; pin versions. [sandbox] |
| `runtime_packages` | Supported / measured | Arbitrary commands; uploaded offline-wheel install passes. That result establishes neither public registry access nor apt installation. [api] [evaluation] [fixtures] |
| `cpu_sizing` | Supported / documented | Fractional **physical cores**, request or `(request, limit)`; minimum default request 0.125. No numeric maximum verified on inspected pages. [resources] [api] |
| `memory_sizing` | Supported / documented | **MiB**, request or `(request, hard limit)`; minimum default 128 MiB. Scalar request permits bursting. [resources] |
| `gpu` | Conditional / documented | Explicit Sandbox `gpu` reservation, gVisor-only, preemptible; no GPU requested/tested here. [api] [sandbox-resources] |
| `network_policy` | Supported / documented | Full outbound block, CIDR allowlist, beta TLS-domain allowlist, inbound CIDR restriction. Domain/SNI rules are not a full HTTP destination policy. [network] |
| `persistent_storage` | Supported / documented | Volumes/NFS mounts and filesystem/directory snapshots; local state alone does not survive termination. Sandbox disk cannot be enlarged; VM root disk is 512 GiB. [sandbox] [api] [sandbox-resources] |
| `session_reuse` | Supported / measured | Attach by ID/name while running; three separate calls preserve filesystem state in the report. Not a persistent Python process. [sandbox] [evaluation] [fixtures] |
| `shell` | Supported / documented | Arbitrary `exec` argv and PTY; adapter has a `bash -c` route. [api] [adapter] |
| `file_transfer` | Supported / measured | Native byte APIs; existing 26,900-byte roundtrip passes host bytes/hash checks. Not a large/nested export guarantee. [api] [evaluation] |
| `ports_preview` | Supported / documented | HTTP/WebSocket connect tokens, TLS/plain TCP/H2 tunnels; Team/Enterprise custom-domain onboarding. [network] |
| `self_hosting` | Unknown / unverified | No full customer-operated runtime/control-plane distribution verified in inspected official docs. Client source and VM selection are insufficient. [sandbox] [security] |
| `cmek` | Unknown / unverified | At-rest encryption is documented; **alpha CSEK for directory snapshots** is narrower than KMS-backed CMEK for all sandbox data. [security] [csek] |

### Configuration limits that affect comparisons

- CPU requests are physical cores: **`cpu=2` corresponds to 2 physical cores / 4 vCPU equivalent**, not 2 vCPUs. Memory is MiB: **`memory=2048` requests 2 GiB**. Both are requests rather than caps when scalar values are used. Billing is `max(request, actual)` for each resource. [resources] [sandbox-resources]
- Default maximum lifetime is 300 seconds; documented configurable maximum is 24 hours. Reuse requires a still-running sandbox; snapshots are the documented route for carrying filesystem state beyond its lifetime. [sandbox]
- Default outbound access is to public IPs. CIDR and domain allowances combine additively. Domain filtering permits TLS/SNI on 443, leaves DNS unrestricted except under full block, and does not prevent all domain-fronting cases. Experimental dynamic policy updates require relevant allowlist types to have been set on creation. [network]
- CSEK passes customer-held raw key material when snapshotting/mounting a directory. It is alpha, supports directory snapshots only, and does not establish a general cloud-KMS key binding or full-runtime encryption coverage. [csek]

## Tested integration and configuration

Sources: [current adapter](../../src/core/providers/modal.py) [adapter], [evaluated runs](../../reports/data/attempts/modal_evaluation.json) [evaluation], [burst runs](../../reports/data/attempts/modal_burst_evaluation.json) [burst], [workload fixtures](../../src/bench/suites/workflows.py) [fixtures]. Configuration/attempt navigation: [tested-configurations.md](tested-configurations.md) and [tested-configurations.json](tested-configurations.json), **main-generated export pending at this refresh**. No new cloud execution or web research was performed for this refresh; official pricing/capability evidence retains its original 2026-10-13 retrieval date.

| Item | Requested / implemented in inspected adapter | Observed in existing reports / limitation |
| --- | --- | --- |
| SDK path | Async `modal.App.lookup.aio` and `modal.Sandbox.create.aio`; app name defaults to `sandbox-benchmarks` | Client provenance reports Modal **1.6.1**, Python **3.13.13**, Darwin/arm64; these are client versions. |
| Image/runtime options | Adapter supports registry `image`, Debian `python_version`, `runtime` and `region`; defaults remain Debian slim, unpinned Python and unset runtime/region | Latest `configuration.requested` records defaults; no custom image/runtime/region campaign established. Python **3.13.3**, kernel **4.19.0-gvisor** observed; immutable image identity unknown. |
| CPU/RAM options | Configurable CPU/memory scalars or request/limit lists (converted to tuples); latest request `cpu=2`, `memory=2048`, no limits | Guest sees 18 logical CPUs; this is not 18 reserved cores. Report cost `vcpu=2`, `ram_gb=4` remains an unverified estimator input inconsistent with request units. |
| Lifetime | Sandbox timeout **180 seconds**, per-process request timeout plus client wait bound | Does not establish maximum provider lifetime or successful cancellation semantics. |
| Session | One retained handle across separate executions; cleanup/teardown terminate it | `session_state` tests a file value 40 → 42 across three calls, not pause/resume, Python globals or persistence after deletion. |
| Input/output | `filesystem.write_bytes`, `list_files`, `read_bytes`; `INPUT_DIR`/`ARTIFACT_DIR` and workdir set | Roundtrip validates 26,900 bytes. Collector enumerates one directory level and does not explicitly recurse/filter directories. |
| GPU/network/volumes/ports | Adapter accepts `gpu` and `block_network`; latest defaults are `gpu=null`, `block_network=false`; no durable mount or preview route | Options supported by code are not tested configurations. No GPU, custom network policy, volume or preview test established. |

The main evaluation file contains **127 records** at refresh. Preserve the following campaign boundaries rather than pooling adapter versions. [evaluation]

| Campaign / UTC window on 2026-10-13 | Records | Bounded result |
| --- | ---: | --- |
| `campaign-af905b6eb639`, 06:36 | 2 | Initial artifact/ready checks pass. |
| `campaign-bc8647b4771d`, 06:42–06:45 | 55 | 50 pass; **five earlier timeout failures**, returned `exit_code=-1` but labeled `failed`. |
| `campaign-abe1cf5663e4`, 07:13–07:14 | 10 | Five runtime inventories and **five later timeout passes**. |
| `campaign-86fa37bcdf74`, 07:41–07:44 | 60 | Five repeats across 12 suites, **60 pass**, including timeout, binary/SHA-256 transfer, ETL artifact, separate-call session/error recovery and output fidelity. |

Modal SDK 1.6 `ContainerProcess.wait` returns **`-1` as its execution-deadline sentinel**. Current adapter recognizes it, explicitly terminates its sandbox and reports `timed_out`; it also retains the client `asyncio.TimeoutError` route. Earlier failed rows remain valid evidence of the old mapping, not evidence that Modal lacks deadlines. Later timeout rows pass the evaluator's status and response-budget checks. Neither a timeout response nor a cleanup success alone independently proves remote process termination. [adapter] [evaluation] [validation]

Representative evidence:

| Run ID | Result asserted by report |
| --- | --- |
| `bench-2860afb106f9` | Artifact bytes/hash pass; 26,900 bytes saved. |
| `bench-02f56e5b809e` | Ready marker and Python 3.13.3; total client wall time 2,736.304 ms, with creation included in `prepare_ms`. |
| `bench-6ee61ae13df7` | Three-call filesystem session continuity passes. |
| `bench-a4e78e98faec` | Offline dependency install passes; computed fixture value 43. |
| `bench-c0e77e2ceb2b` | Timeout evaluation fails; bounded return/cleanup pass. |
| `bench-7d1c5831eeb8` | Latest timeout passes with `timed_out`, `exit_code=-1`; sentinel mapping and termination route applied. |
| `bench-f47b98a1e3eb` | Latest binary roundtrip passes exact bytes and SHA-256, 26,900 bytes. |
| `bench-fb8274ea4362` | Latest 10k-row ETL and exact `summary.json` bytes/hash pass. |
| `bench-a5258d4a469e` | Latest schema-1 runtime inventory passes; guest observation only. |

### Guest runtime inventory and versioned provenance

Latest five schema-1 inventories report **18 visible logical CPUs / affinity 18**, cgroup-v1 quota/period **18,000,000 / 1,000,000**, Python **3.13.3**, Linux/x86_64, UID **0**, and `nvidia-smi` unavailable with an empty device list. `bash`, `gcc`, `pip` are found; `git`/`node` are not. Memory/sysconf and cgroup-v1 memory values vary from **218,142,515,200 to 486,238,371,840 bytes**; filesystem total is a near-int64-max **9,223,372,036,854,771,712 bytes**. These shared/virtualized values **must not be recast as reserved RAM, usable disk capacity or purchasable CPU allocation**. Missing NVIDIA tools is not a provider GPU-eligibility test. [evaluation] [inventory]

Latest serial configuration ID is **`c6eceedf16a1`**; `provenance.configuration.requested` records defaults and 180-second TTL. Adapter hash prefix **`71538074cc69`**, stack hash prefix **`761a2e0e7f7e`**, client stack Modal **1.6.1** / Python **3.13.13**. Per-suite `evaluation_contract_sha256` values are retained in raw rows; grouping must preserve workload/contract, adapter, stack, configuration and concurrency. Earlier label-only configurations remain incomplete. [evaluation] [validation]

The separate burst report has **12/12 CPU-stress passes at concurrency 3**, `campaign-b0412f75238a` (07:45–07:46), default requests and no GPU. This is a small observed campaign, not a throughput SLA. `cold_start_ms=0` remains an unused phase field; wall time includes client preparation/collection/cleanup, cache state is uncontrolled, and guest inventory does not attest image digest, cloud placement, tier, reserved hardware or metered uptime. [burst] [inventory]

## Current official pricing (USD)

Exact displayed units/rates from [pricing](https://modal.com/pricing) [pricing], accessed 2026-10-13. The **Sandbox + Notebooks** section is the applicable CPU/RAM schedule; the lower Function CPU/RAM rates elsewhere on the page are not interchangeable.

| Resource | Published amount | Unit |
| --- | ---: | --- |
| Sandbox CPU | $0.00003942 | physical-core-second (2 vCPU equivalent) |
| Sandbox RAM | $0.00000667 | GiB-second |
| Volumes | $0.09 | GiB-month; includes 1 TiB/month free |
| Network egress | $0.04 | GiB; plan allowance applies |
| Starter / Team base | $0 / $250 | workspace-month, plus usage |
| Enterprise | Unknown | Negotiated contract |

| GPU list schedule | USD/GPU-second |
| --- | ---: |
| B300 / B200 | 0.001972 / 0.001736 |
| H200 SXM / H100 SXM5 | 0.001261 / 0.001097 |
| RTX PRO 6000 | 0.000842 |
| A100 80 GB / A100 40 GB | 0.000694 / 0.000583 |
| L40S / A10 | 0.000542 / 0.000306 |
| L4 / T4 | 0.000222 / 0.000164 |

CPU/RAM are billed at the greater of request or actual use, with 0.125-core/128-MiB minimum requests. Starter includes $30/month compute and 1 TiB/month egress; Team includes $100/month compute and 10 TiB/month egress; Enterprise lists 100 TiB/month egress. Region selection lists 1.15–1.75× premiums and non-preemptible execution 3×, subject to applicable configuration/product. GPU rates do not establish current capacity for each GPU. [pricing] [sandbox-resources]

**Illustrative request-only rate:** `2 × 0.00003942 + 2 × 0.00000667 = $0.00009218/second` for this adapter's CPU/RAM request, before bursting, premiums, credits and other charges. This is a calculation from list prices, not a measured bill. Existing report costs are explicitly `estimate_unverified_rates`, use client wall time rather than metered uptime, and must not be treated as invoices. No dated comparable official historical price set was gathered; **no price-increase claim is made**. [pricing] [evaluation]

## Sources

All official sources accessed **2026-10-13**; repository paths denote the inspected working tree, not immutable upstream releases.

- [sandbox]: https://modal.com/docs/guide/sandboxes
- [api]: https://modal.com/docs/sdk/py/latest/Sandbox
- [resources]: https://modal.com/docs/guide/resources
- [sandbox-resources]: https://modal.com/docs/guide/sandbox-resources
- [network]: https://modal.com/docs/guide/sandbox-networking
- [pricing]: https://modal.com/pricing
- [security]: https://modal.com/docs/guide/security
- [csek]: https://modal.com/docs/guide/customer-supplied-encryption-keys
- [adapter]: [src/core/providers/modal.py](../../src/core/providers/modal.py)
- [evaluation]: [reports/data/attempts/modal_evaluation.json](../../reports/data/attempts/modal_evaluation.json)
- [fixtures]: [src/bench/suites/workflows.py](../../src/bench/suites/workflows.py)
- [burst]: [reports/data/attempts/modal_burst_evaluation.json](../../reports/data/attempts/modal_burst_evaluation.json)
- [inventory]: [scripts/runtime_inventory.py](../../scripts/runtime_inventory.py)
- [validation]: [src/bench/validation.py](../../src/bench/validation.py)
- Tested-configuration navigation (main export pending): [Markdown](tested-configurations.md), [JSON](tested-configurations.json).
