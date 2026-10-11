<!-- COMMON CONTRACT START -->
# Provider contract: Daytona (`daytona`)

**Sources reviewed:** 2026-10-13 · **Deployment:** `managed_runtime`

## 1. Executive summary and product boundary

Sandbox workspace API; standard, VM and GPU classes have different state/placement contracts.

Managed Sandboxes from OCI images, declarative builds or snapshots; configurable vCPU/RAM/disk and network policies. Default Linux containers, separate Linux/Windows VM and explicitly documented ephemeral GPU classes. Inspected adapter uses older daytona_sdk client.create(timeout=60) without selecting image/snapshot/resources/target; actual deployed configuration is not recorded. Customer-operated compute regions attach to Daytona's managed control plane; legacy public core is unmaintained.

Working adapter: [source](../../src/core/providers/daytona.py). Historical adapter hashes refer to measured revisions, not necessarily current source.

The preserved dossier describes the dated inspected configuration. New budget/lifecycle guardrails change current adapter defaults without changing historical cohort evidence; see [operations](../../CONTRIBUTING.md).

## 2. Documented contract vs measured adapter

Support describes the platform. Measured describes only a bounded oracle on a recorded setup. Documented-only and unverified entries remain coverage gaps.

| Capability | Platform support | Evidence state | Documented contract / scope | Measured adapter behavior | Sources |
|---|---|---|---|---|---|
| `custom_image` | supported | Documented | Managed container sandbox creation from public OCI/Docker images with fixed tags/digests, declarative builds and snapshots. Direct image path rejects mutable latest/lts/stable tags. VM class is created from existing VM snapshots, not container declarative builds. Adapter leaves image/snapshot unset. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [sandbox](#source-sandbox), [adapter](#source-adapter) |
| `runtime_packages` | supported | Documented | Official persistence guide demonstrates runtime pip installation retained across stop/start and captured in snapshots. Shell/package permissions and tier network policy apply. Legacy package_ecosystem stdout inventories pip/preinstalled libraries, not a verified new package installation. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [persistence](#source-persistence), [process](#source-process), [network](#source-network), [legacy-report](#source-legacy-report) |
| `cpu_sizing` | supported | Documented | Create resources CPU uses vCPU. Current general sandbox table defaults to 1, minimum 1, organization default maximum 4; GPU limits scale separately up to 16 vCPUs per GPU. Adapter supplies no CPU resource; documented default is not proof of legacy tested allocation. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [sandbox](#source-sandbox), [adapter](#source-adapter), [legacy-report](#source-legacy-report) |
| `memory_sizing` | supported | Documented | General resource table labels GiB, default/minimum 1, maximum 8 by default organization limits; GPU class up to 192 GB per GPU in prose. Adapter supplies no memory; legacy exit 137 does not establish OOM root cause or memory ceiling. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [sandbox](#source-sandbox), [adapter](#source-adapter), [legacy-report](#source-legacy-report) |
| `gpu` | conditional | Documented | Explicit managed GPU Sandbox resources gpu/gpu_type; ephemeral class up to 8 GPUs with NVIDIA H100/H200/B300/RTX PRO 6000/RTX 4090/RTX 5090 and AMD MI355X documented. Shared fleet uses logical Earth placement and ignores requested geographic target; on-demand quota/capacity or immediate spot failure/preemption apply. Not inferred from agent hosting. Adapter requests no GPU and none was tested. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [sandbox](#source-sandbox), [regions](#source-regions), [adapter](#source-adapter) |
| `network_policy` | conditional | Documented | Tier 1/2 organization restrictions cannot be overridden by sandbox settings; Tier 3/4 default full egress and can set mutually exclusive CIDR/domain allowlists or block-all. Custom rules also restrict essential services. Runtime settings updates supported at higher tiers; upstream proxy is create-only. Adapter sets no policy; legacy HTTP block does not prove all egress is blocked. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [network](#source-network), [adapter](#source-adapter), [legacy-report](#source-legacy-report) |
| `persistent_storage` | supported | Documented | Container disk survives stop/start/archive but memory does not; VM pause/resume retains memory and filesystem. Independent S3-backed Volumes and snapshots survive deletion. GPU sandboxes are deleted on stop and need external volumes for results. Adapter deletes sandbox at cleanup and does not test durable persistence. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [persistence](#source-persistence), [sandbox](#source-sandbox), [adapter](#source-adapter) |
| `session_reuse` | supported | Documented | Get existing sandbox, process sessions and persistent Python interpreter contexts supported. Current adapter creates a fresh sandbox on every execute and does not declare supports_session_calls; legacy agent_multiturn is one script, not distinct API calls. No pause/resume or cross-call reuse measured. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [sandbox](#source-sandbox), [process](#source-process), [adapter](#source-adapter), [legacy-fixture](#source-legacy-fixture), [legacy-report](#source-legacy-report) |
| `shell` | supported | Documented | process.exec runs shell commands with cwd/env/timeout and supports persistent sessions/PTY via provider APIs. Adapter always uploads and runs a Python file, so shell-language requests are not implemented as a separate native route. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [process](#source-process), [adapter](#source-adapter) |
| `file_transfer` | supported | Documented | Provider byte upload/download, multiple-file and streaming APIs documented. Adapter uploads bytes but downloads only /tmp/transformed_output.txt, silently ignores failures and skips empty content. Legacy 6000-byte text result does not establish general binary, recursive or multi-file collection fidelity. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [files](#source-files), [adapter](#source-adapter), [legacy-report](#source-legacy-report) |
| `ports_preview` | supported | Documented | HTTP service preview URLs for ports 1-65535. Private standard preview token is sandbox-wide and unrevocable while running; signed URL token is single-port, expiring and revocable. Public sandbox property removes preview authentication. Adapter generates no preview and tests no ports. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [preview](#source-preview), [adapter](#source-adapter) |
| `self_hosting` | conditional | Documented | Current BYOC supports customer-managed runners/custom regions with Daytona control plane and region Helm charts. Public daytonaio/daytona README states core development moved private in June 2026 and repository is unmaintained; legacy code remains usable/forkable as-is. Neither proves current managed GPU/VM feature parity in a fully self-operated deployment. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [byoc](#source-byoc), [regions](#source-regions), [legacy-core](#source-legacy-core) |
| `cmek` | unknown | Unverified | No managed Sandbox customer-KMS key binding/rotation/revocation contract verified in inspected sources. BYOC infrastructure control or independently encrypted object buckets is not a documented platform-wide CMEK guarantee. Adapter declares cmek_supported=False without testing key management. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [byoc](#source-byoc), [adapter](#source-adapter) |

## 3. Six residency surfaces

Source: [dated residency audit and original vendor citations](../../reports/docs/eu-data-residency.md). These are documented boundaries/gaps, not measured EU residency or GDPR certification.

| Surface | Documented boundary / verification gap |
|---|---|
| Compute | Shared eu target; shared GPUs use earth and ignore preference |
| Files / volumes / snapshots / backups | All shared volume/snapshot/backup placement not established |
| Stdout / stderr / traces | Complete shared telemetry/log boundary unknown |
| Control plane / metadata | BYOC still uses managed control plane |
| Support access / subprocessors | Dedicated regions are provider-managed; support boundary unknown |
| External model / API calls | External endpoint contract separate |

Benchmark location/request provenance is recorded separately in [tested configurations](tested-configurations.md).

## 4. Dated pricing and billing units

Reserved vCPU/RAM/disk charges by lifecycle state, calculated per second; public base rates displayed hourly. GPU preemptible rates are a distinct schedule; on-demand amounts unavailable in retrieved page text.

| SKU / resource | Original billing unit | USD list amount | Sources |
|---|---|---:|---|
| CPU | vCPU-hour (billed per second) | 0.0504 | [pricing](#source-pricing) |
| RAM | GiB-hour (billed per second) | 0.0162 | [pricing](#source-pricing) |
| Storage | GiB-hour after first 5 free (billed per second) | 0.000108 | [pricing](#source-pricing) |
| Windows OS displayed rate | vCPU-hour; relationship to base compute not specified in retrieved pricing | 0.0858 | [pricing](#source-pricing) |
| Preemptible NVIDIA B300 | GPU-hour (billed per second) | 4.08 | [pricing](#source-pricing) |
| Preemptible NVIDIA B200 | GPU-hour (billed per second); pricing-only, not confirmed by inspected GPU type list | 3.59 | [pricing](#source-pricing) |
| Preemptible AMD MI355X | GPU-hour (billed per second) | 3.44 | [pricing](#source-pricing) |
| Preemptible NVIDIA H200 | GPU-hour (billed per second) | 2.61 | [pricing](#source-pricing) |
| Preemptible NVIDIA H100 | GPU-hour (billed per second) | 2.27 | [pricing](#source-pricing) |
| Preemptible NVIDIA RTX PRO 6000 | GPU-hour (billed per second) | 1.74 | [pricing](#source-pricing) |
| Preemptible NVIDIA RTX 5090 | GPU-hour (billed per second) | 0.74 | [pricing](#source-pricing) |
| Preemptible NVIDIA RTX 4090 | GPU-hour (billed per second) | 0.57 | [pricing](#source-pricing) |
| On-demand GPU schedule | GPU-hour; amounts not available in retrieved official text | Unknown | [pricing](#source-pricing) |
| Independent Volume/snapshot-specific storage schedule | not explicitly priced in inspected sources | Unknown | [pricing](#source-pricing), [billing](#source-billing), [persistence](#source-persistence) |
| Standalone network egress rate | not itemized in retrieved pricing | Unknown | [pricing](#source-pricing) |
| Enterprise/BYOC contract | contract plus customer infrastructure | Unknown | [pricing](#source-pricing), [byoc](#source-byoc) |

Public page retrieved 2026-10-13 carries publication metadata 2026-10-02; this is not a rate-change effective date. First-5-GiB allowance scope is not specified (do not assume per sandbox). Started and creating/starting/stopping/pausing reserve and bill resources; stopped/paused bill disk only, archived containers not billed, deleted sandbox not billed but retained snapshots can be. GPU free-credit exclusion is explicit in billing docs; advertised $200 free compute is not GPU entitlement. On-demand prices, GPU CPU/RAM additivity and independent volume tariff not verified. Pricing includes B200 but inspected sandbox supported-type list does not. Legacy fixed-rate report is not a metered invoice; no price-increase claim supported.

## 5. Recorded configuration and guest inventory

[All settings, client stacks, attempt IDs and observations](tested-configurations.md) · [Machine-readable export](tested-configurations.json)

- Setup `5bd019963a19` · adapter `3973cef255b4` · stack `9493b75dc1a6` · concurrency 1 · last measured 2026-10-13T16:46:55.833210+00:00.
- Setup `39ed10c5d0c2` · adapter `fd48ea4b8575` · stack `unrecorded` · concurrency 1 · last measured 2026-10-13T07:15:13.906779+00:00.

Guest-visible CPU/RAM and device probes do not attest reserved hardware or isolation. No GPU configuration was benchmarked in this snapshot.

## 6. Dated source register

- <a id="source-sandbox"></a> [sandbox: Sandboxes, resources, VM and GPU classes](https://www.daytona.io/docs/en/sandboxes.md) — accessed 2026-10-13.
- <a id="source-network"></a> [network: Network Limits (Firewall)](https://www.daytona.io/docs/en/network-limits.md) — accessed 2026-10-13.
- <a id="source-persistence"></a> [persistence: Persistence by sandbox class](https://www.daytona.io/docs/en/persistence.md) — accessed 2026-10-13.
- <a id="source-preview"></a> [preview: Standard and signed preview URLs](https://www.daytona.io/docs/en/preview.md) — accessed 2026-10-13.
- <a id="source-process"></a> [process: Process and Code Execution](https://www.daytona.io/docs/en/process-code-execution.md) — accessed 2026-10-13.
- <a id="source-files"></a> [files: File System Operations](https://www.daytona.io/docs/en/file-system-operations.md) — accessed 2026-10-13.
- <a id="source-pricing"></a> [pricing: Daytona pricing (page publication metadata 2026-10-02)](https://www.daytona.io/pricing) — accessed 2026-10-13.
- <a id="source-billing"></a> [billing: Reserved resource billing by lifecycle state](https://www.daytona.io/docs/en/billing.md) — accessed 2026-10-13.
- <a id="source-regions"></a> [regions: Shared, Earth, dedicated and custom regions](https://www.daytona.io/docs/en/regions.md) — accessed 2026-10-13.
- <a id="source-byoc"></a> [byoc: Bring Your Own Compute](https://www.daytona.io/docs/en/bring-your-own-compute.md) — accessed 2026-10-13.
- <a id="source-legacy-core"></a> [legacy-core: Official legacy core README: unmaintained since June 2026](https://raw.githubusercontent.com/daytonaio/daytona/main/README.md) — accessed 2026-10-13.
- <a id="source-adapter"></a> [adapter: Inspected working-tree Daytona adapter](../../src/core/providers/daytona.py) — accessed 2026-10-13.
- <a id="source-legacy-report"></a> [legacy-report: Legacy Daytona live report without evaluated provenance](../../reports/data/legacy/daytona_live.json) — accessed 2026-10-13.
- <a id="source-legacy-fixture"></a> [legacy-fixture: Single-script multi-turn fixture](../../src/bench/suites/agent_multiturn.py) — accessed 2026-10-13.

<!-- COMMON CONTRACT END -->

## Detailed provider dossier
# Daytona Sandbox — evidence-first specification

Reviewed and official sources accessed **2026-10-13**, matching host UTC/environment dates. Companion [spec.json](spec.json) follows [spec.schema.json](../spec.schema.json). Scope is the current **managed Sandbox** product and the inspected repository integration; the historical developer-workspace description is not treated as the current contract.

## Product and customization

**Deployment:** `managed_runtime`. **Customization:** `custom_image_and_resources`.

The managed service supports custom OCI images, declarative builds, snapshots, resource sizing and network controls. Linux **container** sandboxes are default; Linux/Windows **VM** and **GPU** sandbox classes are documented separately with different lifecycle capabilities. Current docs explicitly show `Resources(gpu=1, gpu_type=...)` for managed sandbox creation: GPU support is therefore direct sandbox evidence, not inferred from agent/model hosting. [sandbox]

Current BYOC means customer-managed runner compute attached to **Daytona's control plane**. The official public core README states that development moved private in **June 2026** and the repository is unmaintained, available as-is to use/fork. Legacy public code availability cannot establish parity with the current managed VM/GPU service or a maintained fully self-hosted control plane. [byoc] [legacy-core]

## Capability matrix

| Feature ID | Support / evidence | Contract and boundary |
| --- | --- | --- |
| `custom_image` | Supported / documented | Public image with fixed tag/digest, builds or snapshots; direct image path excludes `latest`/`lts`/`stable`. VM creation requires VM snapshot. [sandbox] |
| `runtime_packages` | Supported / documented | Runtime pip-install and retained package state explicitly demonstrated; egress/permissions apply. [persistence] [network] |
| `cpu_sizing` | Supported / documented | vCPU; general table 1 default/minimum, 4 default max; GPU limits separate. [sandbox] |
| `memory_sizing` | Supported / documented | GiB in general table; 1 default/minimum, 8 default max. Actual adapter allocation unrecorded. [sandbox] [adapter] |
| `gpu` | Conditional / documented | Explicit ephemeral GPU class, quota/capacity/placement limits; up to 8 GPUs. Not benchmarked here. [sandbox] [regions] |
| `network_policy` | Conditional / documented | Lower-tier org restrictions; higher-tier custom CIDR/domain/block-all and runtime changes. [network] |
| `persistent_storage` | Supported / documented | Container/VM disk persistence; VM-only memory pause/resume; independent volumes/snapshots; GPU deleted on stop. [persistence] |
| `session_reuse` | Supported / documented | Existing sandbox, process sessions and interpreter contexts. Adapter creates fresh sandbox per execute. [sandbox] [process] [adapter] |
| `shell` | Supported / documented | Arbitrary command exec, sessions and PTY options; adapter runs Python file only. [process] [adapter] |
| `file_transfer` | Supported / documented | Byte/multi-file/streaming APIs; adapter collector restricted to one hard-coded file. [files] [adapter] |
| `ports_preview` | Supported / documented | HTTP previews by port; private sandbox-wide standard token versus port-scoped revocable signed URL. [preview] |
| `self_hosting` | Conditional / documented | Current customer compute with managed control plane; legacy core as-is/unmaintained. [byoc] [legacy-core] |
| `cmek` | Unknown / unverified | No customer KMS key lifecycle contract verified for managed sandbox data. BYOC is not itself CMEK. [byoc] |

### Resource and runtime boundaries

| General container sizing table | Default | Minimum | Default organization maximum |
| --- | ---: | ---: | ---: |
| CPU (vCPU) | 1 | 1 | 4 |
| Memory (GiB) | 1 | 1 | 8 |
| Disk (GiB) | 3 | 1 | 10 |

These are **current documented defaults**, not the actual configuration of historical runs. Default snapshots also encode sizes (`daytona-small` 1/1/3, `daytona-medium` 2/4/8, `daytona-large` 4/8/10). The adapter names none of them. GPU class limits scale separately: per GPU up to 16 vCPUs, **192 GB RAM** and **512 GB disk**, with up to 8 GPUs. Keep the GPU prose GB units distinct from the general GiB table; no conversion convention was verified. [sandbox] [adapter]

The sandbox guide lists H100, H200, B300, RTX PRO 6000, RTX 4090, RTX 5090 and MI355X. Shared GPU sandboxes use a logical **Earth** region, with geographic target preference ignored; dedicated/custom GPU regions keep their real target. On-demand GPU requests are quota/capacity constrained and may wait; spot requests fail immediately without capacity and may be preempted without warning. The pricing table additionally lists **B200**, but the inspected GPU type contract does not: its listed price is not proof of a selectable type. [sandbox] [regions] [pricing]

### Network, storage and ports

- **Tier 1/2:** organization restrictions prevail and cannot be overridden per sandbox. **Tier 3/4:** full egress by default; custom CIDR/domain allowlist or block-all is mutually exclusive and replaces default access, including essential-service exceptions. CIDRs are IPv4-only, max 10 entries; domains max 100. Runtime policy updates are documented at higher tiers; upstream HTTP(S) proxy is create-only and clients ignoring proxy env vars require additional enforcement. [network]
- Containers retain disk across stop/start and archive but lose memory on stop. VM pause/resume preserves memory; GPU sandboxes are ephemeral/deleted on stop. S3-backed Volumes and snapshots can outlive sandbox deletion. A persistent filesystem flag does not mean every sandbox class has durable RAM or that adapter cleanup preserves data. [persistence]
- HTTP previews cover ports 1–65535. Private **standard** preview tokens are sandbox-wide credentials, including privileged toolbox/terminal ports, and cannot be revoked while the sandbox keeps running; **signed** previews are port-bound, expiring and revocable (1–86,400 seconds, 60-second default). Public sandbox configuration bypasses preview authentication. No actual token-bearing URL is included here. [preview]

## Integration and existing tested configuration

Read [adapter](../../src/core/providers/daytona.py), [historical report](../../reports/data/legacy/daytona_live.json), [current prerequisite attempt](../../reports/data/attempts/daytona_evaluation.json), and [tested configurations](tested-configurations.md). The fresh inventory attempt failed because the environment has no configured Daytona credentials. No guest inventory was obtained; this is an access prerequisite, not a measured vendor outage. The hard-coded default credential was removed from the adapter.

| Item | Current adapter request/implementation | Existing observation / unknown |
| --- | --- | --- |
| SDK/client | Imports older `daytona_sdk.Daytona`/`DaytonaConfig`; default API `https://app.daytona.io/api`, override supported | Current official examples import `daytona`; legacy report records no SDK version/revision/date, so compatibility is not re-tested. |
| Creation | `client.create(timeout=60)` **on every execute** | 60 seconds is client creation timeout, not a chosen sandbox maximum lifetime. |
| Image/resources/region | No explicit snapshot/image, CPU/RAM/disk, class, GPU, target or network policy | Documented defaults cannot be assigned as measured configuration. Actual selected image/region/tier/allocation unrecorded. |
| Execution | Upload Python file to `/tmp`, run `python <file>` with request timeout | No persistent interpreter or separate shell-language route; synchronous SDK operations run inside async methods. |
| Input/output | Byte upload to `/tmp`; only fixed `/tmp/transformed_output.txt` download | No prepared-directory env forwarding, arbitrary output enumeration or recursion; failures swallowed and empty artifacts omitted. |
| Lifecycle | Delete on cleanup/teardown; errors swallowed | No stop/start/pause/volume reuse measured; no `supports_session_calls` declaration. |
| GPU/previews | None requested | Managed GPU and port contracts are official-document evidence only. |

Legacy report observations are narrow:

| Legacy run | Bounded observation |
| --- | --- |
| `bench-a83f0ac4ffbd` | Ready marker and Python **3.14.4**; client total 3,167.215 ms, not native cold-start duration. |
| `bench-afe6922ae55a` | Memory workload exits **137** with empty output; compatible with SIGKILL but no evidence identifying OOM or a RAM ceiling. |
| `bench-be66becd21f0` | DNS marker allowed, one public HTTP probe fails, metadata probe errors; not proof of zero egress or which tier/policy applied. |
| `bench-31a2a2a18ddc` | UID **1001**, non-root, passwordless sudo marker; not a universal security configuration. |
| `bench-53cdbbd4b6e5` | One **6,000-byte text** artifact collected; not arbitrary binary/multi-file validation. |
| `bench-b4fb7c33e683` | Adapter reports `timed_out`; does not establish universal process termination semantics. |
| `bench-54f962f89480` | Five logical turns occur inside **one script execution**, not five API calls or sandbox resume. |

The legacy report has no evaluated host checks, timestamp/config provenance or actual resource inventory. `cold_start_ms=0` is not evidence of zero launch time. Its cost field saying “or self-hosted $0” is an estimator label, not evidence that this run was self-hosted or cost-free. Runtime inventory and evaluated reports may later establish actual configuration; this spec deliberately leaves allocation, image digest, tier/target and metered uptime unknown. [legacy-report] [adapter]

## Current official pricing (USD)

Exact displayed values from [pricing](https://www.daytona.io/pricing) [pricing], accessed **2026-10-13**. Retrieved page metadata says published **2026-10-02**; this is not established as the effective date of a pricing change. Billing is calculated **per second**, while these public rates are displayed per hour.

| Resource | Amount | Published unit |
| --- | ---: | --- |
| CPU | $0.0504 | vCPU-hour |
| RAM | $0.0162 | GiB-hour |
| Storage | $0.000108 | GiB-hour after first 5 free |
| Windows OS displayed rate | $0.0858 | vCPU-hour; base/add-on relationship unspecified in retrieved text |
| On-demand GPU rates | **Unknown** | Tab exists; amounts absent from retrieved official text |
| Independent Volume/snapshot-specific tariff | **Unknown** | No explicitly scoped separate rate verified |
| Standalone egress rate | **Unknown** | Not itemized in retrieved pricing |
| Enterprise/BYOC | **Unknown** | Contract and customer infrastructure costs |

| Preemptible GPU | USD/GPU-hour |
| --- | ---: |
| B300 / B200 | 4.08 / 3.59 |
| MI355X | 3.44 |
| H200 / H100 | 2.61 / 2.27 |
| RTX PRO 6000 | 1.74 |
| RTX 5090 / RTX 4090 | 0.74 / 0.57 |

Do not substitute these preemptible prices for on-demand. GPU CPU/RAM charge additivity is not resolved by the retrieved pricing text. B200 is retained as a **pricing-only entry**, not added to the verified supported-type list. The “first 5 free” storage allowance is not explicitly scoped per sandbox or organization, so a per-sandbox assumption would be unwarranted. [pricing] [sandbox]

Equivalent base list rates are `$0.000014/vCPU-second`, `$0.0000045/GiB-second` and `$0.00000003/GiB-second` storage after allowance. These are arithmetic conversions, not additional tariffs or measured bills. [pricing]

Billing uses **reserved resources by lifecycle state**: started and creating/starting/stopping/pausing bill CPU/RAM/disk; stopped or paused bill disk only; archived containers are not billed; deleted sandbox resources are not billed, but retained snapshots still incur storage. GPU sandboxes do not use free-credit balances, despite the pricing page advertising $200 free compute. No current evaluated invoice/billing telemetry was inspected; legacy fixed `$0.00002/second` client-wall-time estimates are not official metered costs. No dated comparable historical official price set was established; **no price-increase claim is made**. [billing] [pricing] [legacy-report]

## Sources

All accessed **2026-10-13**. Local paths refer to inspected working-tree evidence.

- [sandbox]: https://www.daytona.io/docs/en/sandboxes.md
- [network]: https://www.daytona.io/docs/en/network-limits.md
- [persistence]: https://www.daytona.io/docs/en/persistence.md
- [preview]: https://www.daytona.io/docs/en/preview.md
- [process]: https://www.daytona.io/docs/en/process-code-execution.md
- [files]: https://www.daytona.io/docs/en/file-system-operations.md
- [pricing]: https://www.daytona.io/pricing
- [billing]: https://www.daytona.io/docs/en/billing.md
- [regions]: https://www.daytona.io/docs/en/regions.md
- [byoc]: https://www.daytona.io/docs/en/bring-your-own-compute.md
- [legacy-core]: https://raw.githubusercontent.com/daytonaio/daytona/main/README.md
- [adapter]: [src/core/providers/daytona.py](../../src/core/providers/daytona.py)
- [legacy-report]: [reports/data/legacy/daytona_live.json](../../reports/data/legacy/daytona_live.json)
- [legacy-fixture]: [src/bench/suites/agent_multiturn.py](../../src/bench/suites/agent_multiturn.py)
