<!-- COMMON CONTRACT START -->
# Provider contract: Databricks SQL MCP (`databricks`)

**Sources reviewed:** 2026-10-13 · **Deployment:** `managed_tool`

## 1. Executive summary and product boundary

SQL system.ai.python_exec via an existing warehouse; not Dedicated Sandbox Beta or system.ai.sandbox MCP.

Legacy system.ai.python_exec via SQL in the current adapter; not dedicated Sandbox or the new system.ai.sandbox MCP. Warehouse capacity is separately configurable, but built-in-function image/resources/dependencies are not requested.

Working adapter: [source](../../src/core/providers/databricks.py). Historical adapter hashes refer to measured revisions, not necessarily current source.

The preserved dossier describes the dated inspected configuration. New budget/lifecycle guardrails change current adapter defaults without changing historical cohort evidence; see [operations](../../CONTRIBUTING.md).

## 2. Documented contract vs measured adapter

Support describes the platform. Measured describes only a bounded oracle on a recorded setup. Documented-only and unverified entries remain coverage gaps.

| Capability | Platform support | Evidence state | Documented contract / scope | Measured adapter behavior | Sources |
|---|---|---|---|---|---|
| `custom_image` | unsupported | Documented | No image selector in the built-in-function invocation; general cluster image support is outside scope. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [D1](#source-D1), [A1](#source-A1) |
| `runtime_packages` | unknown | Unverified | Historical report lists packages and pip --version, not installation. Custom dependency ENVIRONMENT clauses for separately defined UDFs do not prove python_exec customization. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [D3](#source-D3), [A1](#source-A1), [R1](#source-R1) |
| `cpu_sizing` | conditional | Documented | SQL warehouse cluster size/concurrency configurable externally; no per-function vCPU allocation. Actual warehouse size absent from report. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [D4](#source-D4), [A1](#source-A1) |
| `memory_sizing` | conditional | Documented | Warehouse capacity can be sized; independent interpreter RAM selection unavailable in inspected request. PENDING after 50 seconds is not a measured RAM ceiling. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [D4](#source-D4), [A1](#source-A1), [R1](#source-R1) |
| `gpu` | unsupported | Documented | No selectable GPU in this SQL/function interface; other Databricks GPU services are not this provider. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [D1](#source-D1), [A1](#source-A1) |
| `network_policy` | unknown | Unverified | No adapter policy control. Historical DNS allowed, HTTP/metadata probes blocked. New sandbox MCP explicitly has no egress; general UDF networking exists, so neither establishes a universal legacy configurable policy. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [D1](#source-D1), [D2](#source-D2), [D3](#source-D3), [A1](#source-A1), [R1](#source-R1) |
| `persistent_storage` | unsupported | Documented | No durable disk/mount interface in adapter. Historical scratch disk writes succeeded, contradicting README's all-I/O-forbidden claim, but not proving persistence. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [A1](#source-A1), [R1](#source-R1), [L1](#source-L1) |
| `session_reuse` | unsupported | Documented | Independent statement submissions without interpreter session handle. Historical five-turn workload runs inside a single program. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [A1](#source-A1), [R1](#source-R1) |
| `shell` | unsupported | Documented | Python-code function, no first-class command or SSH interface. New system.ai.sandbox shell capability is outside this adapter. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [D1](#source-D1), [A1](#source-A1) |
| `file_transfer` | unsupported | Documented | Adapter embeds lossy UTF-8 INPUT_FILES and returns no artifacts; it does not implement native file transport. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [A1](#source-A1) |
| `ports_preview` | unsupported | Documented | No preview or port interface in this built-in function invocation. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [D1](#source-D1), [A1](#source-A1) |
| `self_hosting` | unsupported | Documented | Managed Databricks-provided execution; open client libraries do not self-host the service. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [D1](#source-D1), [D2](#source-D2) |
| `cmek` | unknown | Unverified | No function-specific key guarantee verified. Adapter capability false is not a documented platform prohibition. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [A1](#source-A1) |

## 3. Six residency surfaces

Source: [dated residency audit and original vendor citations](../../reports/docs/eu-data-residency.md). These are documented boundaries/gaps, not measured EU residency or GDPR certification.

| Surface | Documented boundary / verification gap |
|---|---|
| Compute | SQL workspace/warehouse region unrecorded |
| Files / volumes / snapshots / backups | Function-specific storage/retention commitment unestablished |
| Stdout / stderr / traces | Every SQL-tool log/backup location not established |
| Control plane / metadata | Regional processing statements do not settle every management flow |
| Support access / subprocessors | Exact support/account flows unknown |
| External model / API calls | Designated AI Europe Geo includes EEA, UK and Switzerland; settings matter |

Benchmark location/request provenance is recorded separately in [tested configurations](tested-configurations.md).

## 4. Dated pricing and billing units

Applicable SQL warehouse/serverless compute SKU billed in DBUs; legacy functions MCP documented as serverless general compute. Model inference separate and absent from adapter.

| SKU / resource | Original billing unit | USD list amount | Sources |
|---|---|---:|---|
| Applicable warehouse/serverless compute SKU | DBU | Unknown | [D2](#source-D2), [D5](#source-D5), [D6](#source-D6) |
| External model inference if separately used | model-specific token billing unit | Unknown | [A1](#source-A1) |

No universal rate extracted: official numeric pricing table rendered Loading; actual SKU/cloud/configuration and effective price period missing. list_prices documents exact usage units and effective dates. Report's $0.000025/second is an assumption, not current official pricing or invoice evidence. No comparable dated price-increase evidence.

## 5. Recorded configuration and guest inventory

[All settings, client stacks, attempt IDs and observations](tested-configurations.md) · [Machine-readable export](tested-configurations.json)

- Setup `f6b3c3845d9a` · adapter `ff6ebfad7dbf` · stack `e8a6874856cd` · concurrency 1 · last measured 2026-10-13T16:31:08.596020+00:00.
- Setup `629df7809d28` · adapter `ff6ebfad7dbf` · stack `e8a6874856cd` · concurrency 1 · last measured 2026-10-13T07:43:03.590806+00:00.
- Setup `39ed10c5d0c2` · adapter `ff6ebfad7dbf` · stack `unrecorded` · concurrency 1 · last measured 2026-10-13T07:15:38.555958+00:00.

Guest-visible CPU/RAM and device probes do not attest reserved hardware or isolation. No GPU configuration was benchmarked in this snapshot.

## 6. Dated source register

- <a id="source-D1"></a> [D1: Let agents run code and legacy python_exec MCP](https://docs.databricks.com/aws/en/agents/custom-agents/code-interpreter-tools) — accessed 2026-10-13.
- <a id="source-D2"></a> [D2: Databricks-provided MCPs and legacy endpoint pricing](https://docs.databricks.com/aws/en/agents/mcp-tools/built-in-mcp-services) — accessed 2026-10-13.
- <a id="source-D3"></a> [D3: Unity Catalog UDF customization and networking scope](https://docs.databricks.com/aws/en/udf/unity-catalog) — accessed 2026-10-13.
- <a id="source-D4"></a> [D4: SQL warehouse sizing and scaling](https://docs.databricks.com/aws/en/compute/sql-warehouse/warehouse-behavior) — accessed 2026-10-13.
- <a id="source-D5"></a> [D5: Serverless general compute pricing (numeric table not retrieved)](https://www.databricks.com/product/pricing/datascience-ml) — accessed 2026-10-13.
- <a id="source-D6"></a> [D6: Pricing system table reference](https://docs.databricks.com/aws/en/admin/system-tables/pricing) — accessed 2026-10-13.
- <a id="source-A1"></a> [A1: Inspected current SQL adapter](repo:src/core/providers/databricks.py) — accessed 2026-10-13.
- <a id="source-R1"></a> [R1: Historical raw report, not rerun](repo:reports/data/legacy/databricks_live.json) — accessed 2026-10-13.
- <a id="source-L1"></a> [L1: Existing README, non-authoritative historical claims](repo:providers/databricks/README.md) — accessed 2026-10-13.

<!-- COMMON CONTRACT END -->

## Detailed provider dossier
# Databricks legacy Python execution (`databricks`)

Reviewed: **2026-10-13**. Deployment: **managed_tool**. Customization: **fixed_runtime** for the built-in function used by this adapter.

## Scope and interface

This provider is the legacy **`system.ai.python_exec` Unity Catalog function**, not the dedicated [Databricks Sandbox](../databricks_sandbox/SPEC.md). The inspected adapter actually calls the SQL Statement Execution SDK with `SELECT system.ai.python_exec(:code)`; it does not send MCP JSON-RPC. The official legacy MCP URL is `/api/2.0/mcp/functions/system/ai/python_exec`. [D1, A1]

Current official documentation recommends the separate **`system.ai.sandbox` MCP**, exposed through `/ai-gateway/mcp-services/system.ai.sandbox` under Unity Gateway Beta. That service runs Python, SQL, and shell code and has no network egress. Its shell support must not be assigned to this legacy adapter. Likewise, the dedicated Sandbox SDK's unrestricted egress and persistent home are different capabilities. [D1, D2]

The legacy MCP requires the **Managed MCP Servers** workspace preview and access to the function. SQL invocation requires access to the selected warehouse and underlying function. General Unity Catalog UDFs can have custom dependencies and networking, but those are properties of separately defined UDFs, not demonstrated customization options for the built-in `python_exec` function. [D1, D3]

## Capability matrix

Support describes this specific execution surface. `unknown` means unresolved, not a negative result. Evidence is `documented` for an inspected API/code contract and `unverified` when historical reports or missing product-specific documentation cannot establish a guarantee. No new execution was performed.

| Feature ID | Support | Evidence | Scope / qualification | Sources |
|---|---|---|---|---|
| `custom_image` | unsupported | documented | No image parameter in this built-in-function invocation; general cluster images do not customize it. | D1, A1 |
| `runtime_packages` | unknown | unverified | Report lists installed libraries and working `pip --version`, not a successful installation. Custom UDF dependency support does not establish built-in-function package installation. | D3, A1, R1 |
| `cpu_sizing` | conditional | documented | Warehouse cluster size/concurrency can be configured outside the adapter; no per-function vCPU allocation is exposed. | D4, A1 |
| `memory_sizing` | conditional | documented | Warehouse sizing affects warehouse capacity; no independent interpreter RAM limit is requested or verified. | D4, A1 |
| `gpu` | unsupported | documented | No selectable GPU in the SQL/function interface inspected here. Other Databricks GPU products are outside scope. | D1, A1 |
| `network_policy` | unknown | unverified | Adapter has no policy parameter. Report shows DNS allowed and one HTTP/metadata probe blocked. Current no-egress documentation is explicit for the newer sandbox MCP, not a configurable legacy policy. | D1, D2, D3, A1, R1 |
| `persistent_storage` | unsupported | documented | No durable sandbox disk/mount contract in this adapter. Scratch writes reported within one call do not establish persistence. | A1, R1 |
| `session_reuse` | unsupported | documented | No interpreter/session handle; each execute submits a SQL statement. Reusing a client or warehouse is not reusing Python state. | A1 |
| `shell` | unsupported | documented | API accepts Python code, with no first-class command/SSH interface. Reported `pip --version` is not a supported shell execution contract. | D1, A1, R1 |
| `file_transfer` | unsupported | documented | Inputs become a lossy UTF-8 `INPUT_FILES` dictionary in code; collector always returns `[]`. No native binary upload/download. | A1 |
| `ports_preview` | unsupported | documented | No service port or preview endpoint in this function interface. | D1, A1 |
| `self_hosting` | unsupported | documented | Databricks-provided function/MCP is managed; the client library is not a self-hostable execution service. | D1, D2 |
| `cmek` | unknown | unverified | Adapter says false but exposes no key setting; no function-specific customer-managed-key guarantee verified. | A1 |

## Inspected / historical tested configuration

- **Requested by current code:** optional `DATABRICKS_CONFIG_PROFILE`, optional `DATABRICKS_WAREHOUSE_ID`, otherwise the first listed warehouse. Warehouse type, size, region, actual CPU/RAM, UDF environment version, and network settings are not recorded by the adapter. Do not label a particular warehouse configuration as tested. [A1]
- **Timeout behavior:** `wait_timeout` is clamped to 5–50 seconds. This is a statement response wait, not necessarily execution completion. Pending/running statements are canceled only when the requested timeout is at most five seconds; longer pending statements are returned as failed without polling. [A1]
- **Historical report:** `reports/data/legacy/databricks_live.json` contains 11 suite rows, without a dated campaign/configuration record. It reports Python 3.12.3, cold-start-suite execute time 7,162.018 ms, CPU-suite execute time 1,247.230 ms, scratch disk integrity success, and DNS resolution with blocked HTTP and metadata probes. Memory stress ends in `StatementState.PENDING` after roughly 50 seconds; that is not a measured RAM ceiling. [R1]
- The README's **file I/O forbidden/read-only CWD** claim conflicts with the report's successful disk I/O. Neither observation establishes durable storage. The report's five-turn state continuity is inside one submitted program, not five independent API sessions. Its costs use an assumed `$0.000025/second`; they are not billing export evidence. [L1, R1]
- This repository's adapter uses SQL, not MCP, and its artifact collector is empty. A different MCP implementation cannot establish capabilities for this adapter. [A1]
- [Current attempts](../../reports/data/attempts/databricks_evaluation.json) and [tested configurations](tested-configurations.md) supplement the historical report; no cloud configuration is inferred from the old README.

## Pricing (USD)

Official documentation routes **legacy Unity Catalog functions MCP** to **serverless general compute pricing**, and SQL warehouse work to Databricks SQL pricing. The actual adapter uses a warehouse; account for its SKU usage rather than assigning one universal code-execution price. DBUs are usage units, not dollars or seconds. [D2, D5]

| Resource | Exact unit | Verified amount |
|---|---|---|
| Applicable warehouse/serverless compute SKU | USD per DBU | **Unknown for this configuration**; requires cloud, SKU, applicable dates, region/tier/contract and usage. |
| External agent/model inference, if used | USD per model token unit | Separate; no model is invoked by this adapter. |

The official pricing page's retrieved content rendered the numeric table as `Loading...`; no reliable universal numeric rate was extracted. `system.billing.list_prices` documents `usage_unit`, `price_start_time`, `price_end_time`, and `pricing.effective_list`; join applicable usage to the matching price period for a defensible estimate. We did not query a workspace. Do not promote the report's wall-time multiplier into current pricing. No price-increase claim is made. [D5, D6]

## Sources

Official pages accessed 2026-10-13:

- **D1:** [Let agents run code; legacy `python_exec` and new sandbox MCP](https://docs.databricks.com/aws/en/agents/custom-agents/code-interpreter-tools)
- **D2:** [Databricks-provided MCPs; preview, limitations, endpoint pricing](https://docs.databricks.com/aws/en/agents/mcp-tools/built-in-mcp-services)
- **D3:** [Unity Catalog Python UDFs; dependency/networking scope](https://docs.databricks.com/aws/en/udf/unity-catalog)
- **D4:** [SQL warehouse sizing, scaling, and queuing](https://docs.databricks.com/aws/en/compute/sql-warehouse/warehouse-behavior)
- **D5:** [Serverless general compute pricing](https://www.databricks.com/product/pricing/datascience-ml)
- **D6:** [Pricing system table reference](https://docs.databricks.com/aws/en/admin/system-tables/pricing)

Repository evidence inspected 2026-10-13:

- **A1:** [Current SQL adapter](../../src/core/providers/databricks.py)
- **R1:** [Historical report](../../reports/data/legacy/databricks_live.json)
- **L1:** [Existing README, including claims qualified above](README.md)
