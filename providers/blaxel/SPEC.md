<!-- COMMON CONTRACT START -->
# Provider contract: Blaxel (`blaxel`)

**Sources reviewed:** 2026-10-13 · **Deployment:** `managed_runtime`

## 1. Executive summary and product boundary

Managed Sandbox process/file API; agent deployments and inference hosting are separate.

Managed sandbox microVMs with custom images containing sandbox-api, memory-sized CPU, network/proxy options, volumes and previews. CPU is coupled to RAM. Current adapter requests a unique per-attempt name, py-app:latest, 4096 MB, us-pdx-1 and ttl=1h; options allow alternate image/memory/region/TTL. Exact requested settings and guest observations are recorded in tested-configurations.json. No GPU deployment tested.

Working adapter: [source](../../src/core/providers/blaxel.py). Historical adapter hashes refer to measured revisions, not necessarily current source.

The preserved dossier describes the dated inspected configuration. New budget/lifecycle guardrails change current adapter defaults without changing historical cohort evidence; see [operations](../../CONTRIBUTING.md).

## 2. Documented contract vs measured adapter

Support describes the platform. Measured describes only a bounded oracle on a recorded setup. Documented-only and unverified entries remain coverage gaps.

| Capability | Platform support | Evidence state | Documented contract / scope | Measured adapter behavior | Sources |
|---|---|---|---|---|---|
| `custom_image` | supported | Documented | Dockerfile/custom registry images must include sandbox-api; SDK ImageInstance injects the binary/default entrypoint. Generic unmodified Docker Hub images cannot directly act as sandbox images. Default slimming removes build-time compilers/caches; opt out where runtime builds need them. Adapter requests a mutable prebuilt py-app:latest tag. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [templates](#source-templates), [deployment](#source-deployment), [adapter](#source-adapter) |
| `runtime_packages` | supported | Documented | Official sandbox use cases describe autonomous package installation and process execution. Availability depends on image tools, writable RAM-backed filesystem and egress policy. Legacy package_ecosystem report establishes pip availability, not a verified package installation; no new evaluated installation report was available. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [sandbox](#source-sandbox), [process](#source-process), [legacy-report](#source-legacy-report) |
| `cpu_sizing` | conditional | Documented | CPU follows selected memory, not an independent CPU field in inspected SandboxRuntime. API description says memory MB/2048 (4096 MB=2 CPUs), while overview examples say 8 GB=4 cores and 16 GB=6 cores. Do not extrapolate a universal linear mapping or assign physical/vCPU equivalence without inventory. Adapter requests 4096 MB; actual existing-instance CPU is unknown. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [sandbox](#source-sandbox), [api](#source-api), [adapter](#source-adapter) |
| `memory_sizing` | supported | Documented | memory is documented in MB; limits depend on account tier, custom pricing advertises up to 256 GB. Image base is read-only EROFS with writable tmpfs layer sharing RAM, approximately 50% reserved when possible. memory=4096 is a requested creation value, not measured process-available RAM; create_if_not_exists does not reconfigure existing instances. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [sandbox](#source-sandbox), [api](#source-api), [quotas](#source-quotas), [pricing](#source-pricing), [adapter](#source-adapter) |
| `gpu` | unknown | Unverified | No GPU reservation field in the inspected sandbox API/runtime configuration or explicit managed Sandbox GPU offering verified. Agent Hosting, model integrations, CUDA_VISIBLE_DEVICES image examples, NVIDIA-branded tools and custom hardware marketing do not prove sandbox GPU access. No GPU requested or tested. Absence of documentation is not an explicit unsupported contract. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [api](#source-api), [deployment](#source-deployment), [agents](#source-agents), [templates](#source-templates), [pricing](#source-pricing), [adapter](#source-adapter) |
| `network_policy` | conditional | Documented | Public-preview proxy domain/method/path filters; environment-variable routing alone can be bypassed. Explicit firewall rulesets=[proxy] at creation enforces proxy egress, documented for Mark 3.0 not Carbon/3.1. API relocates allow/deny fields under network.proxy and has conflicting rule-precedence wording versus guide; verify exact version semantics before relying on overlap. Adapter configures no network restriction. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [domains](#source-domains), [api](#source-api), [adapter](#source-adapter) |
| `persistent_storage` | supported | Documented | Standby snapshots retain state; attached Volumes survive deletion. Current guide limits one volume per sandbox, same region, create-time attach. Adapter mounts no durable storage and deletes its owned sandbox during cleanup/teardown with errors propagated. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [sandbox](#source-sandbox), [volumes](#source-volumes), [api](#source-api), [adapter](#source-adapter) |
| `session_reuse` | supported | Documented | Named lookup/reuse and standby restore are documented. Adapter now uses a unique per-attempt sandbox and does not declare reusable session calls. Legacy single-script multi-turn is not separate-call or standby/resume evidence. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [sandbox](#source-sandbox), [adapter](#source-adapter), [legacy-report](#source-legacy-report), [legacy-fixture](#source-legacy-fixture) |
| `shell` | supported | Documented | process.exec accepts arbitrary shell command strings; named process wait/kill supported. Adapter always runs an uploaded Python script and combines logs. Without keepAlive, documented timeout bounds waiting and does not auto-kill process; adapter reports timed_out on wait timeout but does not call process.kill. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [process](#source-process), [adapter](#source-adapter) |
| `file_transfer` | supported | Documented | Provider supports native binary read/write and multipart transfer (direct HTTP request cap 5 MB, SDK chunks larger writes). Current adapter instead UTF-8-decodes inputs with errors=ignore, text-writes, and text-reads only /tmp/transformed_output.txt. Legacy 6000-byte text roundtrip does not validate arbitrary binary or multi-file fidelity. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [files](#source-files), [adapter](#source-adapter), [legacy-report](#source-legacy-report) |
| `ports_preview` | supported | Documented | Creation-time API ports and dynamic public/private token previews; preview URLs can use custom domains. API reserves 80/443/8080; preview guide explicitly forbids port 80. Bind to injected HOST; active WebSocket connections have timeout/reconnect constraints. Adapter exposes no ports/previews. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [sandbox](#source-sandbox), [preview](#source-preview), [api](#source-api), [adapter](#source-adapter) |
| `self_hosting` | conditional | Documented | Pricing describes bring-your-own-metal: customer bare metal in own VPC connected privately to Blaxel control plane, with quote/custom hardware. This is partial infrastructure control, not a verified wholly self-operated control plane/runtime distribution. Evaluated path remains managed cloud. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [pricing](#source-pricing) |
| `cmek` | unknown | Unverified | No provider-native customer KMS encryption-key binding/rotation/revocation contract for sandbox snapshots, volumes, images or logs verified in inspected sources. BYOM, encrypted secrets or ZDR assertions do not establish CMEK. Adapter declares cmek_supported=False without an encryption test. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [api](#source-api), [pricing](#source-pricing), [adapter](#source-adapter) |

## 3. Six residency surfaces

Source: [dated residency audit and original vendor citations](../../reports/docs/eu-data-residency.md). These are documented boundaries/gaps, not measured EU residency or GDPR certification.

| Surface | Documented boundary / verification gap |
|---|---|
| Compute | Frankfurt Mark 3 listed; baseline requested Oregon |
| Files / volumes / snapshots / backups | Volumes in-region; other images/snapshots/backups unknown |
| Stdout / stderr / traces | Complete residency scope unknown |
| Control plane / metadata | Complete residency scope unknown |
| Support access / subprocessors | Access/subprocessor boundary unknown |
| External model / API calls | External endpoint contract separate |

Benchmark location/request provenance is recorded separately in [tested configurations](tested-configurations.md).

## 4. Dated pricing and billing units

Active Sandbox compute billed by allocated GB RAM-second with CPU included; separate snapshot/image/volume storage while retained; standby has no compute charge.

| SKU / resource | Original billing unit | USD list amount | Sources |
|---|---|---:|---|
| Sandbox active compute including CPU | GB RAM-second | 0.0000115 | [pricing](#source-pricing) |
| Sandbox snapshot storage | GB-month | 0.2 | [pricing](#source-pricing) |
| Sandbox image storage | GB-month | 0.045 | [pricing](#source-pricing) |
| Persistent Volume provisioned capacity | GB-month, provisioned not used | 0.12 | [pricing](#source-pricing) |
| Wildcard custom domain | domain-month | 20 | [pricing](#source-pricing) |
| Agent Drive data storage/operations | free during beta; future rate unknown | 0 | [pricing](#source-pricing) |
| Dedicated egress IP/gateway runtime | free during beta; future rate unknown | 0 | [pricing](#source-pricing) |
| Proxy data processed | free during beta; future rate unknown | 0 | [pricing](#source-pricing) |
| Internal/internet egress traffic | included, no separate displayed charge | 0 | [pricing](#source-pricing) |
| Fully-qualified non-wildcard custom domain | coming soon; no published rate | Unknown | [pricing](#source-pricing) |
| Custom/BYOM deployment | contract | Unknown | [pricing](#source-pricing) |
| Sandbox GPU rate | not published; GPU availability unverified | Unknown | [pricing](#source-pricing), [api](#source-api) |

Official public rates retrieved 2026-10-13; GB labels are retained and not silently converted to GiB. Memory API uses MB; exact MB-to-billable-GB convention not established. Snapshot/image/volume charges can continue while idle. Quota top-ups are wallet prepayment, not flat plan fees; eligibility is rolling 30-day real-money top-ups, promo credits do not count. Up to $200 credits advertised, account entitlement unverified. Agent/MCP/Batch Jobs pricing is a different product and is excluded from Sandbox compute rate. Legacy report fixed rates/resources have no billing verification or dated rate provenance. No price-change conclusion supported.

## 5. Recorded configuration and guest inventory

[All settings, client stacks, attempt IDs and observations](tested-configurations.md) · [Machine-readable export](tested-configurations.json)

- Setup `98d5f84fa22b` · adapter `f1238f8bfe20` · stack `1d71f3be8c2a` · concurrency 1 · last measured 2026-10-13T16:28:58.560153+00:00.
- Setup `ed833ceba657` · adapter `f1238f8bfe20` · stack `1d71f3be8c2a` · concurrency 1 · last measured 2026-10-13T07:37:33.846829+00:00.
- Setup `39ed10c5d0c2` · adapter `39db71c37648` · stack `unrecorded` · concurrency 1 · last measured 2026-10-13T07:16:02.248650+00:00.

Guest-visible CPU/RAM and device probes do not attest reserved hardware or isolation. No GPU configuration was benchmarked in this snapshot.

## 6. Dated source register

- <a id="source-sandbox"></a> [sandbox: Sandboxes overview and lifecycle](https://docs.blaxel.ai/Sandboxes/Overview.md) — accessed 2026-10-13.
- <a id="source-api"></a> [api: Create sandbox OpenAPI reference](https://docs.blaxel.ai/api-reference/compute/create-sandbox.md) — accessed 2026-10-13.
- <a id="source-templates"></a> [templates: Build reusable sandbox images with Dockerfiles](https://docs.blaxel.ai/Sandboxes/Templates.md) — accessed 2026-10-13.
- <a id="source-deployment"></a> [deployment: blaxel.toml deployment configuration](https://docs.blaxel.ai/deployment-reference.md) — accessed 2026-10-13.
- <a id="source-domains"></a> [domains: Domain filtering (public preview)](https://docs.blaxel.ai/Sandboxes/Proxy-domains.md) — accessed 2026-10-13.
- <a id="source-volumes"></a> [volumes: Volumes for sandboxes](https://docs.blaxel.ai/Sandboxes/Volumes.md) — accessed 2026-10-13.
- <a id="source-process"></a> [process: Process execution and timeout semantics](https://docs.blaxel.ai/Sandboxes/Processes.md) — accessed 2026-10-13.
- <a id="source-files"></a> [files: Sandbox file system and binary/multipart operations](https://docs.blaxel.ai/Sandboxes/Filesystem.md) — accessed 2026-10-13.
- <a id="source-preview"></a> [preview: Real-time previews](https://docs.blaxel.ai/Sandboxes/Preview-url.md) — accessed 2026-10-13.
- <a id="source-quotas"></a> [quotas: Usage and quotas](https://docs.blaxel.ai/Security/Quotas.md) — accessed 2026-10-13.
- <a id="source-pricing"></a> [pricing: Blaxel pricing and deployment options](https://blaxel.ai/pricing) — accessed 2026-10-13.
- <a id="source-agents"></a> [agents: Agents Hosting (distinct product)](https://docs.blaxel.ai/Agents/Overview.md) — accessed 2026-10-13.
- <a id="source-adapter"></a> [adapter: Inspected working-tree Blaxel adapter](../../src/core/providers/blaxel.py) — accessed 2026-10-13.
- <a id="source-legacy-report"></a> [legacy-report: Legacy Blaxel live report without evaluated provenance](../../reports/data/legacy/blaxel_live.json) — accessed 2026-10-13.
- <a id="source-legacy-fixture"></a> [legacy-fixture: Single-script multi-turn fixture](../../src/bench/suites/agent_multiturn.py) — accessed 2026-10-13.

<!-- COMMON CONTRACT END -->

## Detailed provider dossier
# Blaxel Sandbox — evidence-first specification

Reviewed and official sources accessed **2026-10-13**, matching host UTC/environment dates. Companion [spec.json](spec.json) follows [spec.schema.json](../spec.schema.json). Scope is **managed Sandboxes**, distinct from Agents Hosting, MCP Hosting, Batch Jobs and the model gateway.

## Product and customization

**Deployment:** `managed_runtime`. **Customization:** `custom_image_and_resources`.

Named sandbox microVMs have a managed active/standby lifecycle, filesystem/process APIs and previews. Custom images run inside the managed service; users choose memory, with CPU allocated accordingly rather than independently. Standby snapshots retain filesystem, RAM and running processes. Durable volumes persist independently of the sandbox. [sandbox] [api] [volumes]

## Capability matrix

| Feature ID | Support / evidence | Contract and boundary |
| --- | --- | --- |
| `custom_image` | Supported / documented | Dockerfile or declarative SDK builder; **sandbox-api required**. Plain registry images are not directly ready sandbox images. [templates] |
| `runtime_packages` | Supported / documented | Shell/runtime installation; writable tmpfs, image tools, privileges and egress matter. Legacy pip-available marker is not an installation test. [sandbox] [process] [legacy-report] |
| `cpu_sizing` | Conditional / documented | CPU follows RAM; no independent CPU field verified. Official mapping examples are inconsistent at larger sizes. [sandbox] [api] |
| `memory_sizing` | Supported / documented | Creation memory in **MB**; tier limits, custom offer up to 256 GB. Filesystem writes share sandbox RAM. [sandbox] [api] [quotas] [pricing] |
| `gpu` | **Unknown / unverified** | No Sandbox GPU reservation contract verified. Agent hosting/model integration/custom hardware are insufficient evidence. [api] [agents] [pricing] |
| `network_policy` | Conditional / documented | Public-preview filters; enforced proxy firewall is opt-in, creation-only and documented for Mark 3.0, not Carbon. [domains] |
| `persistent_storage` | Supported / documented | Standby snapshots; independent persistent volume, one-volume/one-sandbox attachment limit in guide. [sandbox] [volumes] |
| `session_reuse` | Supported / documented | Named lookup/idempotent create and automatic standby resume. Legacy multi-turn script is not separate-call verification. [sandbox] [legacy-fixture] |
| `shell` | Supported / documented | Arbitrary process commands and named wait/kill. Adapter always executes uploaded Python. [process] [adapter] |
| `file_transfer` | Supported / documented | Native binary and multipart provider APIs; adapter's UTF-8 text conversion loses arbitrary binary bytes. [files] [adapter] |
| `ports_preview` | Supported / documented | API-exposed ports plus dynamic public/private preview URLs/custom domains. Adapter does not use them. [sandbox] [preview] |
| `self_hosting` | Conditional / documented | BYOM customer hardware linked to **Blaxel control plane**; not verified full self-operated stack. [pricing] |
| `cmek` | Unknown / unverified | No verified customer KMS key lifecycle contract; encrypted secrets, ZDR and BYOM are different properties. [api] [pricing] |

### Important contract details and source conflicts

1. **Images:** custom images need the `sandbox-api` binary and a correct startup path. The SDK builder injects it automatically. Default image slimming removes caches, headers and compilers; `slim=false` is needed if those tools must remain available at runtime. The adapter's `blaxel/py-app:latest` is not a reproducible digest. [templates] [deployment] [adapter]
2. **RAM/CPU/disk:** a read-only EROFS image is overlaid with RAM-backed tmpfs. Approximately half of RAM is reserved for the writable filesystem when possible. API `memory` is labeled MB and describes CPU = MB/2048; the overview says 8 GB → 4 CPU cores but 16 GB → 6 CPU cores. Treat this as coupled sizing with an unresolved high-size mapping, not a guaranteed universal formula or physical-core/vCPU equivalence. Current account maxima are console/tier-dependent; the custom pricing offer lists up to 256 GB. [sandbox] [api] [quotas] [pricing]
3. **Standby timing:** overview describes approximately **15 seconds** to standby, whereas pricing FAQ says about **5 seconds** of inactivity. Neither is benchmarked here. Memory/process preservation does not preserve external database/HTTP connections on their peers. TTL means maximum age/deletion, not an idle process timeout. [sandbox] [pricing] [api]
4. **Network policy:** proxy environment variables alone can be bypassed. `firewall.rulesets=["proxy"]` at creation enforces proxy routing on documented Mark 3.0 infrastructure. The domain guide says deny wins when rules overlap; the API `ProxyConfig` says allow takes precedence, and migrates fields from `network.allowedDomains` into `network.proxy`. Exact version behavior is unresolved; overlapping rules cannot be presented as a verified policy. [domains] [api]
5. **GPU:** inspected SandboxRuntime and deployment config expose no GPU reservation. The image-builder example setting `CUDA_VISIBLE_DEVICES` does not allocate a device. Agents Hosting is a separate HTTP endpoint service. Custom hardware/BYOM marketing is not a managed GPU sandbox contract. GPU remains **unknown**, not an assumed yes or an unsupported claim from silence. [api] [templates] [deployment] [agents] [pricing]
6. **Ports/storage:** API ports 80/443/8080 are reserved; preview docs explicitly forbid port 80 and use dynamic opening. Servers should bind injected `HOST`; WebSocket reconnection/ping support matters. Volumes attach at creation, same region, one per sandbox and one sandbox per volume; they cannot be detached according to the current guide. [sandbox] [preview] [volumes]

## Integration and existing tested configuration

Read [adapter](../../src/core/providers/blaxel.py), [current evaluated attempts](../../reports/data/attempts/blaxel_evaluation.json), and [exact tested configuration/inventories](tested-configurations.md). The earlier dossier inspection used the legacy report; current repeated cloud runs now supplement it with host oracles and versioned provenance.

| Item | Current adapter request/implementation | Observation / caveat |
| --- | --- | --- |
| SDK | `blaxel.core.SandboxInstance.create_if_not_exists` | Legacy report lacks SDK version, timestamp, revision and evaluated checks. Installed-version listings in another provider's report do not prove a Blaxel run used that version. |
| Identity/config | Unique per-attempt name; default `blaxel/py-app:latest`; **4096 MB**, **us-pdx-1**, **TTL 1h** | Requested settings are recorded; image/memory/region/TTL can be overridden. Mutable tag is not a pinned digest. |
| CPU | No independent CPU request | API 4096 MB example maps to 2 CPUs; actual allocation unverified. Legacy cost `vcpu=2`, `ram_gb=4` is estimator input. |
| Execution | Script text uploaded to `/tmp`; `python <script>`; `/tmp` workdir; process wait; combined logs | Does not honor a separate shell language route; stdout/stderr separation is lost. |
| Files | Input UTF-8 decode with `errors="ignore"`; text write; only `/tmp/transformed_output.txt` read/encoded | Provider binary support exceeds adapter integration. Missing collection file is silently ignored; no recursive/multi-file collection or prepared-directory env forwarding. |
| Lifecycle | `cleanup` deletes the owned remote sandbox; `teardown` retries a remaining handle | Deletion errors propagate. Fresh names prevent shared-session attribution. `timed_out` is wait exhaustion, not verified process death. |
| GPU/network/storage/preview | None configured | No feature-specific managed tests established. |

Legacy report records a 6,000-byte **text** artifact, remote Python **3.12.15**, root UID **0**, successful public HTTPS probe, and a metadata error marker. These are bounded stdout/collection observations from an older schema, with no independently recorded provider response/allocation inventory. They do not establish general isolation, binary fidelity, maximum memory or benchmark-wide comparability. [legacy-report]

| Legacy run | Bounded observation |
| --- | --- |
| `bench-f9329b7266ac` | Ready/Python marker; total client wall time 2,206.961 ms; `cold_start_ms=0` is not launch time. |
| `bench-deffdb0ba77e` | One text artifact collected, 6,000 bytes. |
| `bench-a4ce6b44fed1` | Script printed allocations through 2,000 MB; not provider RAM inventory. |
| `bench-a58998206b0c` | Adapter reported `timed_out`; no process-kill verification. |
| `bench-cdb1d51d2842` | Five logical turns **inside one execution script**; not five API calls or standby-resume test. |

Official process docs clarify that **without `keepAlive`, `timeout` does not auto-kill the process**; it bounds waiting. The adapter sets neither `keep_alive` nor an explicit `process.kill` on wait timeout. This limits the meaning of its timeout marker. Raw runtime inventory, current evaluated artifacts, image identity, active/standby spans and account tier can be added later by the report owner. [process] [adapter]

## Current official pricing (USD)

### Updated measured baseline

Latest complete-contract campaign: five trials per readiness/CPU/SQLite/repository/output/inventory workload. Readiness, SQLite and repository checks passed 5/5; prime-sieve checks passed 4/5 with one integration failure. All five 128-KiB stdout-fidelity checks failed: 65,602 bytes returned instead of 131,072. This identifies a log-output integration limit, not a universal vendor execution-size limit. The guest inventory reported Python 3.12.15, x86_64, two visible/affinity CPUs and about 3.84 GiB physical memory; allocation guarantees and GPU availability are not established. See [configuration evidence](tested-configurations.md) and [raw attempts](../../reports/data/attempts/blaxel_evaluation.json).

Exact displayed units from [pricing](https://blaxel.ai/pricing) [pricing], accessed 2026-10-13. Keep **GB/MB labels as published**; no GiB conversion convention was verified.

| Sandbox-relevant resource | Amount | Published unit / scope |
| --- | ---: | --- |
| Active Sandbox compute (CPU included) | $0.0000115 | GB RAM-second |
| Snapshot storage | $0.20 | GB-month |
| Image storage | $0.045 | GB-month |
| Volume provisioned capacity | $0.12 | GB-month, regardless of bytes used |
| Wildcard custom domain | $20 | domain-month |
| Agent Drive data/operations | $0 currently | Free during beta; future rate unknown |
| Dedicated egress gateway/IP, proxy processing | $0 currently | Free during beta; future rate unknown |
| Internal / internet egress traffic | Included | No separate displayed charge |
| Fully-qualified non-wildcard domain | Unknown | Coming soon |
| Custom/BYOM deployment | Unknown | Quote |
| Sandbox GPU | Unknown | No verified offering/rate |

Standby compute is free but retained snapshots/volumes can still incur charges; image storage is separate. For a billing allocation of exactly **4 published GB**, active compute is `4×0.0000115 = $0.000046/second`; this is conditional arithmetic, **not confirmation that API 4096 MB is metered as 4 GB**. Batch Jobs/MCP/Agent Runtime schedules are distinct and are not used for Sandbox compute. [pricing]

Pricing advertises up to $200 credits and tier-based limits. **Top-ups are wallet prepayments, not monthly subscription fees**: eligibility is based on real-money top-ups in the trailing 30 days; promotional credits do not unlock tiers. Legacy report costs use a different fixed estimated rate without dated official rate provenance or invoice validation. No dated comparable historical prices were established; **no price-increase claim is made**. [quotas] [pricing] [legacy-report]

## Sources

All accessed **2026-10-13**. Local links denote inspected working-tree evidence.

- [sandbox]: https://docs.blaxel.ai/Sandboxes/Overview.md
- [api]: https://docs.blaxel.ai/api-reference/compute/create-sandbox.md
- [templates]: https://docs.blaxel.ai/Sandboxes/Templates.md
- [deployment]: https://docs.blaxel.ai/deployment-reference.md
- [domains]: https://docs.blaxel.ai/Sandboxes/Proxy-domains.md
- [volumes]: https://docs.blaxel.ai/Sandboxes/Volumes.md
- [process]: https://docs.blaxel.ai/Sandboxes/Processes.md
- [files]: https://docs.blaxel.ai/Sandboxes/Filesystem.md
- [preview]: https://docs.blaxel.ai/Sandboxes/Preview-url.md
- [quotas]: https://docs.blaxel.ai/Security/Quotas.md
- [pricing]: https://blaxel.ai/pricing
- [agents]: https://docs.blaxel.ai/Agents/Overview.md
- [adapter]: [src/core/providers/blaxel.py](../../src/core/providers/blaxel.py)
- [legacy-report]: [reports/data/legacy/blaxel_live.json](../../reports/data/legacy/blaxel_live.json)
- [legacy-fixture]: [src/bench/suites/agent_multiturn.py](../../src/bench/suites/agent_multiturn.py)
