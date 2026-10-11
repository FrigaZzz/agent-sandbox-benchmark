<!-- COMMON CONTRACT START -->
# Provider contract: OpenAI Tool (`openai_tool`)

**Sources reviewed:** 2026-10-13 · **Deployment:** `model_mediated`

## 1. Executive summary and product boundary

Legacy Assistants Code Interpreter adapter; newer Hosted Shell/Responses products need separate measurements.

Current Responses containers have files, 1/4/16/64 GB memory, expiry and network policy options; package/shell workflows require separately documented Hosted Shell. Inspected adapter uses fresh text-only Assistants gpt-4o Code Interpreter and requests none of these options.

Working adapter: [source](../../src/core/providers/openai_tool.py). Historical adapter hashes refer to measured revisions, not necessarily current source.

The preserved dossier describes the dated inspected configuration. New budget/lifecycle guardrails change current adapter defaults without changing historical cohort evidence; see [operations](../../CONTRIBUTING.md).

## 2. Documented contract vs measured adapter

Support describes the platform. Measured describes only a bounded oracle on a recorded setup. Documented-only and unverified entries remain coverage gaps.

| Capability | Platform support | Evidence state | Documented contract / scope | Measured adapter behavior | Sources |
|---|---|---|---|---|---|
| `custom_image` | unsupported | Documented | No custom base-image selector in hosted container create contract. Image media processing and skills are not container image customization. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [O1](#source-O1), [O2](#source-O2) |
| `runtime_packages` | conditional | Documented | Official Hosted Shell example pip-installs with org/request network allowlist. Separate Responses tool; no verified package installation in inspected Assistants Code Interpreter adapter or offline-wheel workflow. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [O3](#source-O3), [A1](#source-A1) |
| `cpu_sizing` | unsupported | Documented | Managed container create contract exposes no vCPU selector. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [O2](#source-O2) |
| `memory_sizing` | supported | Documented | Current Responses Code Interpreter containers expose 1g default, 4g, 16g, 64g, fixed over container life. No memory setting requested by legacy adapter. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [O1](#source-O1), [O2](#source-O2), [A1](#source-A1) |
| `gpu` | unsupported | Documented | No selectable GPU in inspected hosted container create contract. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [O2](#source-O2) |
| `network_policy` | conditional | Documented | Shared container create contract exposes disabled or domain allowlist; Hosted Shell documents default-disabled egress plus admin org and request allowlists. Legacy adapter requests no policy; no network execution tested. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [O2](#source-O2), [O3](#source-O3), [A1](#source-A1) |
| `persistent_storage` | conditional | Documented | Files/state persist only in active reused container; expired/deleted data unrecoverable, no durable volume. Code Interpreter guide specifies 20-minute inactivity expiry; create API exposes expires_after without verified arbitrary range. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [O1](#source-O1), [O2](#source-O2), [O3](#source-O3) |
| `session_reuse` | supported | Documented | Responses auto context reuse or explicit container ID supported. Adapter creates new assistant/thread for each execute and does not exercise reuse. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [O1](#source-O1), [A1](#source-A1) |
| `shell` | conditional | Documented | Separate Hosted Shell Responses tool, not first-class execution in inspected Assistants code_interpreter-only call. No interactive TTY/sudo promised by Hosted Shell. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [O1](#source-O1), [O3](#source-O3), [A1](#source-A1) |
| `file_transfer` | supported | Documented | Current container upload/list/download APIs and file/image citations documented. Adapter flags true but uploads nothing and collector returns []. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [O1](#source-O1), [O2](#source-O2), [A1](#source-A1) |
| `ports_preview` | unknown | Unverified | Hosted Shell can run services, but no publicly exposed port/preview URL interface verified in inspected docs. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [O2](#source-O2), [O3](#source-O3) |
| `self_hosting` | unsupported | Documented | Hosted Code Interpreter backend not self-hostable; application-owned local shell executor is a different tool mode. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [O1](#source-O1), [O3](#source-O3) |
| `cmek` | unknown | Unverified | No container-runtime CMEK setting or key coverage verified. Adapter capability false is not an authoritative prohibition. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [O1](#source-O1), [O2](#source-O2), [A1](#source-A1) |

## 3. Six residency surfaces

Source: [dated residency audit and original vendor citations](../../reports/docs/eu-data-residency.md). These are documented boundaries/gaps, not measured EU residency or GDPR certification.

| Surface | Documented boundary / verification gap |
|---|---|
| Compute | Eligible European tool processing: EEA + Switzerland, not EU-27; legacy adapter unvalidated |
| Files / volumes / snapshots / backups | Regional content eligibility and temporary container/file retention separate |
| Stdout / stderr / traces | Abuse-monitoring/retention eligibility conditions apply |
| Control plane / metadata | System/account/billing data excluded from content commitments |
| Support access / subprocessors | System/support data excluded from content commitments |
| External model / API calls | Exact endpoint/model eligibility required |

Benchmark location/request provenance is recorded separately in [tested configurations](tested-configurations.md).

## 4. Dated pricing and billing units

Current listed Hosted Shell/Code Interpreter container session fees plus separately billed selected-model tokens. Quoted gpt-4o token rates Standard; not Azure or a measured Assistants invoice.

| SKU / resource | Original billing unit | USD list amount | Sources |
|---|---|---:|---|
| 1 GB Hosted Shell/Code Interpreter container | 20-minute session per container | 0.03 | [O4](#source-O4) |
| 4 GB Hosted Shell/Code Interpreter container | 20-minute session per container | 0.12 | [O4](#source-O4) |
| 16 GB Hosted Shell/Code Interpreter container | 20-minute session per container | 0.48 | [O4](#source-O4) |
| 64 GB Hosted Shell/Code Interpreter container | 20-minute session per container | 1.92 | [O4](#source-O4) |
| gpt-4o Standard input | 1,000,000 input tokens | 2.5 | [O4](#source-O4) |
| gpt-4o cached input | 1,000,000 cached input tokens | 1.25 | [O4](#source-O4) |
| gpt-4o Standard output | 1,000,000 output tokens | 10 | [O4](#source-O4) |

Pricing page also says eligible sessions billed by minute with five-minute minimum; eligibility unresolved, so listed 20-minute units retained. GB is binary GiB. Inactivity expiry separate from billing unit. Legacy README $0.03/thread/day not authoritative. No old comparable dated billing evidence or price-increase claim; model versions/service tiers differ.

## 5. Recorded configuration and guest inventory

[All settings, client stacks, attempt IDs and observations](tested-configurations.md) · [Machine-readable export](tested-configurations.json)

- Setup `dac26c6c470b` · adapter `ea1dd2cdcb0a` · stack `842289258d8c` · concurrency 1 · last measured 2026-10-13T07:45:59.423625+00:00.

Guest-visible CPU/RAM and device probes do not attest reserved hardware or isolation. No GPU configuration was benchmarked in this snapshot.

## 6. Dated source register

- <a id="source-O1"></a> [O1: Official Code Interpreter guide](https://developers.openai.com/api/docs/guides/tools-code-interpreter) — accessed 2026-10-13.
- <a id="source-O2"></a> [O2: Official create container contract](https://developers.openai.com/api/reference/resources/containers/methods/create) — accessed 2026-10-13.
- <a id="source-O3"></a> [O3: Official Hosted Shell network/package and local-shell scope](https://developers.openai.com/api/docs/guides/tools-shell) — accessed 2026-10-13.
- <a id="source-O4"></a> [O4: Official API container and model pricing](https://developers.openai.com/api/docs/pricing) — accessed 2026-10-13.
- <a id="source-A1"></a> [A1: Inspected Assistants adapter](repo:src/core/providers/openai_tool.py) — accessed 2026-10-13.
- <a id="source-L1"></a> [L1: Existing README with historical unverified claims](repo:providers/openai_tool/README.md) — accessed 2026-10-13.

<!-- COMMON CONTRACT END -->

## Detailed provider dossier
# OpenAI model-mediated Code Interpreter (`openai_tool`)

Reviewed: **2026-10-13**. Deployment: **model_mediated**. Customization: **packages_and_files** for current container workflows, with important tool/API qualifications below.

## Scope: inspected adapter versus current API

The benchmark adapter uses **Assistants API**, creates a fresh assistant and thread per execute, defaults to **`gpt-4o`**, enables only `code_interpreter`, then returns assistant message text. Current official documentation emphasizes **Responses Code Interpreter** with explicit or automatic reusable containers. Current Responses container memory/network controls are not configuration that this adapter requested or tested. [A1, O1, O2]

Code Interpreter is **model-mediated Python execution**. The model generates and may revise code, executes it and synthesizes an answer. A successful model run/assistant message is not proof the supplied benchmark source was executed unchanged. Container creation and file APIs are direct management operations; they do not form an arbitrary-code exec endpoint. [O1, O2]

### Current documented options

- **Containers:** `container={type:"auto", memory_limit:"4g", file_ids:[...]}` or an explicit container ID. Auto mode can reuse an active container represented by earlier `code_interpreter_call` context; explicit mode creates via `POST /v1/containers`. [O1, O2]
- **Memory:** `1g` default, `4g`, `16g`, `64g`, fixed for that container's lifetime. This is genuine runtime customization absent from Gemini's built-in tool. CPU counts/GPU/custom base images are not exposed in the inspected create contract. [O1, O2]
- **Lifecycle:** Code Interpreter guide says expiry after 20 minutes of inactivity; data becomes unrecoverable and cannot be reactivated. Current create API also exposes `expires_after` anchored to `last_active_at`. Do not confuse inactivity expiry with the billing session unit, or assume arbitrary accepted expiry ranges not stated in the reference. [O1, O2]
- **Network:** current container create contract exposes `network_policy` disabled/allowlist. Hosted Shell guide documents outbound access disabled by default, organization-admin domain allowlist plus an explicit request policy, and request domains constrained to the org allowlist. Shared container configuration is documented; no such setting was requested by the Assistants adapter. [O2, O3]
- **Shell/packages:** Hosted Shell is a **separate Responses tool** using hosted containers. Its official network example installs packages with `pip install`. This disproves an OpenAI-wide “no packages/no shell/no network” claim, but does not make those first-class features of the inspected Assistants `code_interpreter` call. Offline uploaded wheels or Python subprocess behavior were not source-tested. [O3, A1]
- **Files/images:** model input files can be placed in containers; APIs support upload/list/download/delete. Generated files have container citations. Cropping/zooming/rotating images and graph/image file output are documented. These are media capabilities, not custom OS/container images. [O1, O2]

## Capability matrix

Support refers to the current managed tool/container family with API qualifiers, not a positive benchmark result. All evidence is source inspection; no new execution or cloud resource creation occurred.

| Feature ID | Support | Evidence | Scope / qualification | Sources |
|---|---|---|---|---|
| `custom_image` | unsupported | documented | No image field in current hosted container creation; skills/files are not base images. | O1, O2 |
| `runtime_packages` | conditional | documented | Package installation documented for separate Hosted Shell with network allowlist; not implemented/tested by Assistants Code Interpreter adapter. | O3, A1 |
| `cpu_sizing` | unsupported | documented | No selectable vCPU count in inspected managed container contract. | O2 |
| `memory_sizing` | supported | documented | Responses containers: 1/4/16/64 GB tiers; adapter sends no memory option. | O1, O2, A1 |
| `gpu` | unsupported | documented | No selectable accelerator in managed container create interface. | O2 |
| `network_policy` | conditional | documented | Current shared container disabled/allowlist setting; org + request allowlists needed for documented Hosted Shell workflow. Legacy adapter has no policy request. | O2, O3, A1 |
| `persistent_storage` | conditional | documented | Files remain in active reused container; expiry/deletion discards them. Not durable volumes or persistence after expiry. | O1, O3 |
| `session_reuse` | supported | documented | Auto context reuse or explicit container ID in Responses; fresh-thread adapter does not exercise it. | O1, A1 |
| `shell` | conditional | documented | Separate Hosted Shell Responses tool; Code Interpreter remains Python-first, adapter enables no shell tool. | O1, O3, A1 |
| `file_transfer` | supported | documented | Official container files APIs and citations; current adapter uploads nothing and collector is empty despite positive flags. | O1, O2, A1 |
| `ports_preview` | unknown | unverified | Shell can run services, but no public port/preview URL contract verified in inspected guides. | O2, O3 |
| `self_hosting` | unsupported | documented | Hosted Code Interpreter backend not self-hostable. Local shell mode is a separate application-owned executor. | O1, O3 |
| `cmek` | unknown | unverified | No runtime CMEK setting/coverage verified in these contracts. Key/account data controls must not be assumed to cover container disks. | O1, O2, A1 |

## Inspected / historical tested configuration

- **Requested:** `AsyncOpenAI`, model `gpt-4o`, assistant instructions asking for exact stdout, `tools=[{"type":"code_interpreter"}]`, a fresh text-only thread, and `runs.create_and_poll`. No explicit tool choice, memory/container/network/image/file/expiry options. [A1]
- Output is **assistant message text**, not Code Interpreter run-step logs. The adapter does not verify tool invocation, code identity, stdout origin or runtime outcome. `run.status == completed` controls success. Model-mediated repair/prose can contaminate benchmark comparisons. [A1]
- Native file capability flags are true, but `prepare()` is empty, no Files API upload occurs, and `collect_artifacts()` returns `[]`. Assistant is deleted on the normal path; thread deletion is not performed, and exception-path cleanup is not guaranteed. [A1]
- No `openai_tool_live.json` or `openai_tool_evaluation.json` found in the inspected reports. Model name is an adapter default, not a verified historical live configuration. No measurements for network, packages, memory or image processing are claimed.
- Existing README conflates Assistants sessions, current Responses containers and Azure OpenAI. Its “$0.03 per thread per day,” fixed file-total limits, and blanket no-network/package claims are not accepted as current OpenAI-wide specifications. Azure billing and capabilities require separate sources. [L1, O1, O2, O3, O4]

## Current pricing (USD)

Official pricing lists **Hosted Shell and Code Interpreter container charges separately from model tokens**: [O4]

| Resource | Exact listed unit | Amount |
|---|---|---|
| 1 GB container | 20-minute session per container | $0.03 |
| 4 GB container | 20-minute session per container | $0.12 |
| 16 GB container | 20-minute session per container | $0.48 |
| 64 GB container | 20-minute session per container | $1.92 |
| `gpt-4o` Standard input | 1,000,000 tokens | $2.50 |
| `gpt-4o` cached input | 1,000,000 tokens | $1.25 |
| `gpt-4o` Standard output | 1,000,000 tokens | $10.00 |

The same pricing page says **eligible container sessions are billed by the minute, with a five-minute minimum**. Eligibility is not fully specified in the retrieved text; preserve that caveat rather than assuming universal per-minute billing or inventing a different tier price. GB on that page means **binary GiB (`2^30` bytes)**. Model snapshots, service tiers and Azure/Bedrock billing can differ. [O4]

These current listed rates are not a measured invoice for the legacy adapter. We have not established a historical comparable billing period, so there is **no price-increase claim**. Expiry after inactivity and billing for a 20-minute session are separate concepts. [O1, O4]

## Sources

Official sources accessed 2026-10-13:

- **O1:** [Code Interpreter guide: model mediation, memory tiers, reuse, expiry, files and images](https://developers.openai.com/api/docs/guides/tools-code-interpreter)
- **O2:** [Create container API: memory, network policy, files, skills, expiry](https://developers.openai.com/api/reference/resources/containers/methods/create)
- **O3:** [Hosted and local Shell guide: packages, network control and lifecycle](https://developers.openai.com/api/docs/guides/tools-shell)
- **O4:** [API pricing: container session units and model token rates](https://developers.openai.com/api/docs/pricing)

Local sources: **A1** [inspected adapter](../../src/core/providers/openai_tool.py), **L1** [existing README](README.md). Historical Assistants guide URLs returned 404 during this review; no unsupported claim about their current session billing was substituted.
