<!-- COMMON CONTRACT START -->
# Provider contract: Databricks Dedicated Sandbox (`databricks_sandbox`)

**Sources reviewed:** 2026-10-13 · **Deployment:** `managed_runtime`

## 1. Executive summary and product boundary

Dedicated Sandbox Beta workspace; not the measured SQL warehouse or newer MCP tool.

Beta dedicated Sandbox: fixed 4 vCPU/8 GB, packages/configuration reusable in persistent home. Official SDK image_uri exists, but product guide prohibits startup customization; image deployability unresolved.

Working adapter: [source](../../src/core/providers/databricks_sandbox.py). Historical adapter hashes refer to measured revisions, not necessarily current source.

The preserved dossier describes the dated inspected configuration. New budget/lifecycle guardrails change current adapter defaults without changing historical cohort evidence; see [operations](../../CONTRIBUTING.md).

## 2. Documented contract vs measured adapter

Support describes the platform. Measured describes only a bounded oracle on a recorded setup. Documented-only and unverified entries remain coverage gaps.

| Capability | Platform support | Evidence state | Documented contract / scope | Measured adapter behavior | Sources |
|---|---|---|---|---|---|
| `custom_image` | unknown | Documented | Official EnvironmentSpec.image_uri accepts a Unity Catalog container artifact in schema; current product guide says startup customization unavailable. Field existence is not verified workspace acceptance or arbitrary registry-image support. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [D1](#source-D1), [D4](#source-D4), [D5](#source-D5) |
| `runtime_packages` | supported | Documented | Product guide explicitly allows packages/configuration stored in home for cross-session reuse; system-image/root customization not promised. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [D1](#source-D1) |
| `cpu_sizing` | unsupported | Documented | Fixed 4 vCPU, not configurable. ComputeSpec exposes inactivity timeout, not vCPU selection. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [D1](#source-D1), [D4](#source-D4) |
| `memory_sizing` | unsupported | Documented | Fixed 8 GB RAM, not configurable. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [D1](#source-D1) |
| `gpu` | unsupported | Documented | No selectable accelerator in current fixed CPU Sandbox offering or inspected SDK compute contract. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [D1](#source-D1), [D4](#source-D4) |
| `network_policy` | unsupported | Documented | Unrestricted outbound egress is explicitly non-configurable; default ingress closed and non-configurable. New system.ai.sandbox MCP has different no-egress posture. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [D1](#source-D1), [D6](#source-D6) |
| `persistent_storage` | supported | Documented | 100 GB /home/sandbox-agent persists across stop/start until delete; up to 10 GB outside home lost on stop, including adapter /tmp staging. Possible Beta-end purge. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [D1](#source-D1), [D2](#source-D2), [A1](#source-A1) |
| `session_reuse` | supported | Documented | Named sandbox reuse and stop/start documented. Not a memory/process checkpoint guarantee; adapter creates per execution and deletes, so reuse untested. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [D1](#source-D1), [D2](#source-D2), [A1](#source-A1) |
| `shell` | supported | Documented | Direct exec via SDK name/cmd; /bin/bash -c plus SSH. Adapter keywords corrected and Duration execution timeout forwarded; configured workspace reports API unavailable, so shell not freshly verified. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [D2](#source-D2), [D3](#source-D3), [D4](#source-D4), [A1](#source-A1) |
| `file_transfer` | conditional | Documented | Command/stdin/stdout or SSH-based transfer; no native file endpoint in inspected SDK. Adapter base64-stages inputs but collector returns []; historical artifact result unresolved. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [D3](#source-D3), [D4](#source-D4), [A1](#source-A1), [R1](#source-R1) |
| `ports_preview` | conditional | Documented | Documented SSH -L local forwarding; not public preview URLs. Public ingress closed/non-configurable. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [D1](#source-D1), [D3](#source-D3) |
| `self_hosting` | unsupported | Documented | Managed serverless execution; SDK/CLI are clients, not self-hosted backend. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [D1](#source-D1) |
| `cmek` | unknown | Unverified | No dedicated Sandbox key configuration or encryption-key coverage verified. Adapter false is not authoritative exclusion. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [D1](#source-D1), [A1](#source-A1) |

## 3. Six residency surfaces

Source: [dated residency audit and original vendor citations](../../reports/docs/eu-data-residency.md). These are documented boundaries/gaps, not measured EU residency or GDPR certification.

| Surface | Documented boundary / verification gap |
|---|---|
| Compute | Dedicated EU availability depends on cloud/workspace; access failed here |
| Files / volumes / snapshots / backups | Home storage survives stop/start until deletion; placement/backup scope needs confirmation |
| Stdout / stderr / traces | Every Sandbox log location not established |
| Control plane / metadata | Confirm regional management/account scope |
| Support access / subprocessors | Exact support/account flows unknown |
| External model / API calls | Model endpoint and designated AI Geo settings separate |

Benchmark location/request provenance is recorded separately in [tested configurations](tested-configurations.md).

## 4. Dated pricing and billing units

Current Beta Sandbox feature usage is not charged. Future compute/storage/data-transfer billing anticipated; external model inference separate.

| SKU / resource | Original billing unit | USD list amount | Sources |
|---|---|---:|---|
| Dedicated Sandbox feature usage during current no-charge Beta | Sandbox feature usage while Beta no-charge policy applies | 0 | [D1](#source-D1), [D2](#source-D2) |
| Anticipated future running Sandbox compute | running-sandbox hour | Unknown | [D1](#source-D1), [D7](#source-D7) |
| Anticipated future persistent home storage | stored home data over resource lifetime; exact price unit not verified | Unknown | [D1](#source-D1), [D7](#source-D7) |
| External model inference and applicable data-transfer services | separate service-specific billing unit | Unknown | [D1](#source-D1) |

No-charge policy is temporary and product-specific, not free model inference. Future numeric rates/DBU conversions not verified; Beta pricing table rendered Loading. Historical report assumes $0.000036/second and is not an invoice. No supported dated price-increase comparison.

## 5. Recorded configuration and guest inventory

[All settings, client stacks, attempt IDs and observations](tested-configurations.md) · [Machine-readable export](tested-configurations.json)

- Setup `39ed10c5d0c2` · adapter `f79f492591b9` · stack `unrecorded` · concurrency 1 · last measured 2026-10-13T07:15:13.911751+00:00.

Guest-visible CPU/RAM and device probes do not attest reserved hardware or isolation. No GPU configuration was benchmarked in this snapshot.

## 6. Dated source register

- <a id="source-D1"></a> [D1: Databricks Sandbox product guide](https://docs.databricks.com/aws/en/compute/serverless/sandbox) — accessed 2026-10-13.
- <a id="source-D2"></a> [D2: Sandbox SDK usage guide](https://docs.databricks.com/aws/en/compute/serverless/sandbox-usage-guide) — accessed 2026-10-13.
- <a id="source-D3"></a> [D3: Sandbox CLI command group](https://docs.databricks.com/aws/en/dev-tools/cli/reference/sandbox-commands) — accessed 2026-10-13.
- <a id="source-D4"></a> [D4: Official Sandbox dataclasses, including EnvironmentSpec](https://databricks-sdk-py.readthedocs.io/en/latest/dbdataclasses/sandbox.html) — accessed 2026-10-13.
- <a id="source-D5"></a> [D5: Official generated SDK REST paths and signatures](https://github.com/databricks/databricks-sdk-py/blob/main/databricks/sdk/service/sandbox.py) — accessed 2026-10-13.
- <a id="source-D6"></a> [D6: Distinct new and legacy MCP execution surfaces](https://docs.databricks.com/aws/en/agents/custom-agents/code-interpreter-tools) — accessed 2026-10-13.
- <a id="source-D7"></a> [D7: Beta products pricing (numeric table not retrieved)](https://www.databricks.com/product/pricing/beta-products) — accessed 2026-10-13.
- <a id="source-D8"></a> [D8: Official Sandbox SDK execution and streaming API](https://databricks-sdk-py.readthedocs.io/en/latest/workspace/sandbox/sandbox.html) — accessed 2026-10-13.
- <a id="source-A1"></a> [A1: Inspected dedicated Sandbox adapter](repo:src/core/providers/databricks_sandbox.py) — accessed 2026-10-13.
- <a id="source-T1"></a> [T1: Inspected mock tests, not live SDK verification](repo:tests/test_databricks_providers.py) — accessed 2026-10-13.
- <a id="source-R1"></a> [R1: Historical report with unresolved adapter contradictions](repo:reports/data/legacy/databricks_sandbox_live.json) — accessed 2026-10-13.
- <a id="source-L1"></a> [L1: Existing shared Databricks README citing third-party article](repo:providers/databricks/README.md) — accessed 2026-10-13.

<!-- COMMON CONTRACT END -->

## Detailed provider dossier
# Databricks dedicated Sandbox (`databricks_sandbox`)

Reviewed: **2026-10-13**. Deployment: **managed_runtime**. Customization: **packages_and_files** under the current product guide; the SDK image field has conflicting availability evidence.

## Current official product contract

Databricks Sandbox is **Beta**, enabled by the **Databricks Sandbox** workspace preview setting, subject to supported regions. It is a microVM-isolated execution/development environment, with direct SDK command execution and SSH. It is distinct from legacy SQL `system.ai.python_exec` and the newer no-egress `system.ai.sandbox` MCP execution surface. [D1, D2, D3, D6]

- **Fixed resources:** 4 vCPU, 8 GB RAM; not configurable. No selectable GPU documented. [D1]
- **Storage:** persistent `/home/sandbox-agent`, maximum 100 GB, retained across stop/start until sandbox deletion. Up to 10 GB outside home is deleted on stop; `/tmp` is not durable across stop/start. Beta-end data purge is possible. [D1]
- **Network:** unrestricted outbound egress, **not configurable**; default ingress closed and cannot be changed. SSH local port forwarding is documented, but that is not a public preview URL service. [D1, D3]
- **Environment:** startup customization is unavailable according to the product guide. Packages/configuration can be kept in home for reuse. [D1]

### Custom-image documentation conflict

The official latest SDK reference and generated SDK source expose `SandboxSpec.environment`, with `EnvironmentSpec.image_uri` described as a **Unity Catalog container artifact**, e.g. `catalog.schema.folder.image:tag`. This is real official API-schema evidence, not merely the third-party article cited by the README. However, the current product guide says **“You cannot customize your environment at startup”**, and the usage guide provides no image deployment walkthrough. [D1, D4, D5]

Accordingly, custom-image availability is **unknown** at the deployable-product level: the field is documented, but acceptance, entitlement, image preparation and workspace/region support were not tested. Do not infer arbitrary Docker registry URI support from this field. CPU/RAM/GPU sizing does not become configurable because the SDK describes a “compute spec”: its actual exposed field is inactivity timeout. [D1, D4, D5]

## API / lifecycle

The inspected official generated SDK implements: [D5]

| Operation | Current SDK / REST shape |
|---|---|
| Create | `w.sandbox.create_sandbox(sandbox=Sandbox(...), sandbox_id=...)`; `POST /api/2.0/sandboxes?sandbox_id=...` |
| Get/list/delete | Resource name `sandboxes/{id}`; `GET/DELETE /api/2.0/{name}` and list `/api/2.0/sandboxes` |
| Execute | `execute_command_sync(name, cmd, args=..., envs=..., execution_timeout=Duration(...))`; `POST /api/2.0/sandbox-exec/{name}/exec-sync` |
| Stop/start | `stop_sandbox(name)` / `start_sandbox(name)`; `POST /api/2.0/{name}/stop` or `/start` |
| Update | Only `display_name` and `spec.compute.inactivity_timeout` are mutable. |

Execution is direct exec; invoke `/bin/bash -c` for shell syntax. The response includes stdout/stderr, terminal status, nullable exit code, command ID, and output truncation flag. SDK also documents streaming execution, attach/replay, stdin streaming and listing commands. Timeout has a server default/upper bound; exact default/cap was not established here. [D2, D4]

## Capability matrix

These are official product/API capabilities, not a claim the benchmark adapter exercised each one. `unknown` is unresolved; `conditional` includes explicit transport/lifecycle conditions. No new execution occurred.

| Feature ID | Support | Evidence | Scope / qualification | Sources |
|---|---|---|---|---|
| `custom_image` | unknown | documented | Official `image_uri` schema conflicts with product guide's no-startup-customization limitation; deployability unverified. | D1, D4, D5 |
| `runtime_packages` | supported | documented | Store packages/configuration in persistent home; no root/system-image customization guarantee. | D1 |
| `cpu_sizing` | unsupported | documented | Fixed 4 vCPU. | D1 |
| `memory_sizing` | unsupported | documented | Fixed 8 GB RAM. | D1 |
| `gpu` | unsupported | documented | Current fixed CPU offering exposes no selectable accelerator. | D1, D4 |
| `network_policy` | unsupported | documented | Outbound egress unrestricted and non-configurable; ingress closed/non-configurable. | D1 |
| `persistent_storage` | supported | documented | Home 100 GB survives stop/start; 10 GB outside home does not. Delete destroys home. | D1, D2 |
| `session_reuse` | supported | documented | Reuse sandbox resource and stop/start it; disk persistence is not RAM/process checkpointing. | D1, D2 |
| `shell` | supported | documented | `/bin/bash -c` SDK example and SSH. | D2, D3 |
| `file_transfer` | conditional | documented | Command/stdin/stdout or SSH-based transport possible; no standalone native file API in inspected SDK. Adapter stages base64 inputs and never collects outputs. | D3, D4, A1 |
| `ports_preview` | conditional | documented | SSH `-L` local forwarding documented; no public ingress/preview URL. | D1, D3 |
| `self_hosting` | unsupported | documented | Managed serverless service; SDK/CLI do not implement its backend. | D1 |
| `cmek` | unknown | unverified | No dedicated-Sandbox key configuration/coverage verified. Adapter flag false does not establish product exclusion. | D1, A1 |

## Inspected / historical tested configuration

- Adapter requests **`Sandbox()` defaults**, optional profile, prefix `agent-bench`, and a fresh sandbox per execute. It requests no image, RAM, CPU, network policy, inactivity policy, or `execution_timeout`. It runs base64-staged input files under `/tmp/input` and code under `/tmp/task.py`. These paths are outside persistent home. [A1]
- Current official SDK takes **`name` and `cmd`**. The adapter has been corrected to those arguments, uses `Duration(seconds=...)` for execution timeout and `name` for delete. Mocks verify integration plumbing but are not live API evidence. [D2, D4, A1, T1]
- `collect_artifacts()` always returns `[]`, and cleanup deletes the sandbox. The adapter does not exercise persistent-home stop/start or cross-request reuse despite positive capability flags. [A1]
- `reports/data/legacy/databricks_sandbox_live.json` has 11 historical rows claiming Python 3.12.3, 4 vCPU/8 GB, HTTP 200, 2,000 MB allocation, a two-second timeout, and an artifact with checksum. It lacks a dated campaign, SDK version, resource response or request trace. **Its collected artifact cannot be produced by the inspected empty collector**, and its timeout is not requested by that adapter. Treat these as historical claims with unresolved provenance, not source-tested confirmation. [R1]
- Report cost entries assume `$0.000036/second`; that is not current official pricing. The README/adapter cite a Medium article for Firecracker specifics; official material verifies microVM isolation, not that exact hypervisor implementation. [L1, A1, R1, D3]
- The current [fresh inventory attempt](../../reports/data/attempts/databricks_sandbox_evaluation.json) failed with **“The requested API is not available”** in the configured workspace. No dedicated Sandbox was inventoried. This is an access/feature prerequisite result, not proof of general service outage. See [tested configurations](tested-configurations.md).

## Pricing (USD)

**Current official position: Databricks does not currently charge for Sandbox usage during Beta.** This is a temporary product-specific statement, not free inference or free unrelated Databricks products. [D1, D2]

| Resource | Exact unit / status | Amount |
|---|---|---|
| Dedicated Sandbox feature usage, current Beta | Usage while no-charge Beta applies | **$0** |
| Future runtime compute | Per running-sandbox hour, anticipated | Not published/verified |
| Future persistent storage | Stored home data until deletion, anticipated | No verified numeric rate or storage time unit |
| Data transfer and external model calls | Separate applicable services | Not a Sandbox compute/session rate |

The guide anticipates hourly compute, persistent storage while the resource exists (even stopped), and data transfer charges. The Beta pricing page's numeric table rendered `Loading...`; no future DBU conversion is asserted. The old report's wall-time estimate is not an invoice. No price-increase claim is made. [D1, D7, R1]

## Sources

Official sources accessed 2026-10-13:

- **D1:** [Databricks Sandbox: Beta, fixed resources, storage, network, costs, limitations](https://docs.databricks.com/aws/en/compute/serverless/sandbox)
- **D2:** [Create and manage sandboxes with the SDK](https://docs.databricks.com/aws/en/compute/serverless/sandbox-usage-guide)
- **D3:** [CLI sandbox commands: microVM, SSH, stop/start, local forwarding](https://docs.databricks.com/aws/en/dev-tools/cli/reference/sandbox-commands)
- **D4:** [Official SDK Sandbox API reference](https://databricks-sdk-py.readthedocs.io/en/latest/workspace/sandbox/sandbox.html) and [dataclasses](https://databricks-sdk-py.readthedocs.io/en/latest/dbdataclasses/sandbox.html)
- **D5:** [Official generated SDK source: REST paths and environment schema](https://github.com/databricks/databricks-sdk-py/blob/main/databricks/sdk/service/sandbox.py)
- **D6:** [Separate legacy/new MCP execution surfaces](https://docs.databricks.com/aws/en/agents/custom-agents/code-interpreter-tools)
- **D7:** [Beta products pricing](https://www.databricks.com/product/pricing/beta-products)

Local evidence: **A1** [adapter](../../src/core/providers/databricks_sandbox.py), **T1** [mock tests](../../tests/test_databricks_providers.py), **R1** [historical report](../../reports/data/legacy/databricks_sandbox_live.json), **L1** [existing shared Databricks README](../databricks/README.md). The README's [Medium article](https://medium.com/@shamen1209/databricks-sandboxes-the-secure-playground-for-ai-agents-5deb5bd9683d) is third-party attribution only and was not used to establish capabilities.
