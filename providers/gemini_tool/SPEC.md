<!-- COMMON CONTRACT START -->
# Provider contract: Gemini Tool (`gemini_tool`)

**Sources reviewed:** 2026-10-13 · **Deployment:** `model_mediated`

## 1. Executive summary and product boundary

Model-mediated code_execution; not application-controlled Agent Platform sandboxes.

Model-mediated Python execution with fixed libraries and 30-second maximum runtime. Model/prompt/thinking/tool combinations and media inputs can vary; no container image/resource customization. Adapter defaults to gemini-2.5-flash text-only GenerateContent.

Working adapter: [source](../../src/core/providers/gemini_tool.py). Historical adapter hashes refer to measured revisions, not necessarily current source.

The preserved dossier describes the dated inspected configuration. New budget/lifecycle guardrails change current adapter defaults without changing historical cohort evidence; see [operations](../../CONTRIBUTING.md).

## 2. Documented contract vs measured adapter

Support describes the platform. Measured describes only a bounded oracle on a recorded setup. Documented-only and unverified entries remain coverage gaps.

| Capability | Platform support | Evidence state | Documented contract / scope | Measured adapter behavior | Sources |
|---|---|---|---|---|---|
| `custom_image` | unsupported | Documented | No hosted container image selector. Gemini 3 Flash image inspection/output refers to media, not OS images; not tested by text-only 2.5 Flash adapter. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [G1](#source-G1), [G2](#source-G2), [A1](#source-A1) |
| `runtime_packages` | unsupported | Documented | Official guides explicitly prohibit own library installation; fixed preinstalled libraries. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [G1](#source-G1), [G2](#source-G2) |
| `cpu_sizing` | unsupported | Documented | Tool contract exposes no vCPU selector; model selection is not resource sizing. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [G1](#source-G1), [A1](#source-A1) |
| `memory_sizing` | unsupported | Documented | No RAM selector. README's approximate 1 GB/50 KB stdout numbers not verified in current official guides or report. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [G1](#source-G1), [G2](#source-G2), [L1](#source-L1), [R1](#source-R1) |
| `gpu` | unsupported | Documented | No selectable sandbox GPU; preinstalled TensorFlow does not establish accelerator access. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [G1](#source-G1), [G2](#source-G2) |
| `network_policy` | unsupported | Unverified | No configurable network control in inspected tool request; historical model-mediated output reports blocked DNS/HTTP/metadata without retained tool trace. Search/custom tools do not grant Python network access. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [G1](#source-G1), [A1](#source-A1), [R1](#source-R1) |
| `persistent_storage` | unsupported | Documented | No durable sandbox storage/mount interface in documented tool. Files API/model context and scratch writes are not persistent interpreter disk. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [G1](#source-G1), [G2](#source-G2), [A1](#source-A1), [R1](#source-R1) |
| `session_reuse` | unknown | Unverified | Current multi-turn conversations/previous_interaction_id documented but persistent Python kernel memory/files not established. Adapter creates independent GenerateContent calls; reported five turns occur inside one program. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [G1](#source-G1), [A1](#source-A1), [R1](#source-R1) |
| `shell` | unsupported | Documented | Python-only first-class tool; no SSH/command/shell endpoint. Subprocess probes do not establish a supported shell service. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [G1](#source-G1), [G2](#source-G2) |
| `file_transfer` | conditional | Documented | Developer API inline/Files API input, inline graph/image output with model-dependent behavior. Vertex guide excludes file URI I/O and documents inline bytes. Adapter does not submit files or retrieve inline artifacts. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [G1](#source-G1), [G2](#source-G2), [A1](#source-A1) |
| `ports_preview` | unsupported | Documented | No port forwarding/service preview contract in built-in tool. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [G1](#source-G1), [A1](#source-A1) |
| `self_hosting` | unsupported | Documented | Google-hosted built-in execution. External function-calling runtimes are separate products/deployments. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [G1](#source-G1), [G2](#source-G2) |
| `cmek` | unknown | Unverified | No tool-runtime CMEK selector or coverage verified. Separate Google Cloud sandbox CMEK must not be inherited. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [G2](#source-G2), [A1](#source-A1) |

## 3. Six residency surfaces

Source: [dated residency audit and original vendor citations](../../reports/docs/eu-data-residency.md). These are documented boundaries/gaps, not measured EU residency or GDPR certification.

| Surface | Documented boundary / verification gap |
|---|---|
| Compute | Developer API EU-only processing not established; Cloud route differs |
| Files / volumes / snapshots / backups | Tool/file/cache retention and geography need route-specific verification |
| Stdout / stderr / traces | Developer API terms permit transient logging across facilities |
| Control plane / metadata | No blanket EU-only management boundary established |
| Support access / subprocessors | Google/agent facilities and access need contract review |
| External model / API calls | Execution is inside model turn; exact model/endpoint eligibility matters |

Benchmark location/request provenance is recorded separately in [tested configurations](tested-configurations.md).

## 4. Dated pricing and billing units

No separate Code Execution runtime/session charge; token billing for selected model, including code/results and iterative context. Quoted rates are Developer API Standard paid gemini-2.5-flash only.

| SKU / resource | Original billing unit | USD list amount | Sources |
|---|---|---:|---|
| gemini-2.5-flash Standard paid text/image/video input | 1,000,000 input tokens | 0.3 | [G3](#source-G3) |
| gemini-2.5-flash Standard paid audio input | 1,000,000 input tokens | 1 | [G3](#source-G3) |
| gemini-2.5-flash Standard paid output including thinking | 1,000,000 output tokens | 2.5 | [G3](#source-G3) |
| Separate Code Execution enablement/runtime/session charge | Code Execution tool enablement/runtime charge | 0 | [G1](#source-G1), [G3](#source-G3) |

Developer rates do not establish a Vertex regional quote, or Batch/Flex/Priority rates. Adapter sends text only. Generated code/results are output when created and can be input in iterative reasoning; actual usage metadata required. Fixed 500/250 report tokens and $0.0001125 costs are estimates. No supported dated price-increase comparison.

## 5. Recorded configuration and guest inventory

[All settings, client stacks, attempt IDs and observations](tested-configurations.md) · [Machine-readable export](tested-configurations.json)

- Setup `ae1077b5e6a4` · adapter `cf31d20528a9` · stack `c26a42c190e7` · concurrency 1 · last measured 2026-10-13T16:33:10.410077+00:00.
- Setup `1cf72ddce422` · adapter `cf31d20528a9` · stack `c26a42c190e7` · concurrency 1 · last measured 2026-10-13T07:43:49.697427+00:00.
- Setup `39ed10c5d0c2` · adapter `cf31d20528a9` · stack `unrecorded` · concurrency 1 · last measured 2026-10-13T07:15:22.493494+00:00.

Guest-visible CPU/RAM and device probes do not attest reserved hardware or isolation. No GPU configuration was benchmarked in this snapshot.

## 6. Dated source register

- <a id="source-G1"></a> [G1: Official Developer Code Execution guide, retrieved through Jina Reader](https://ai.google.dev/gemini-api/docs/code-execution) — accessed 2026-10-13.
- <a id="source-G2"></a> [G2: Official Google Cloud Code Execution guide and inline I/O restrictions](https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/code-execution) — accessed 2026-10-13.
- <a id="source-G3"></a> [G3: Official Gemini Developer pricing, retrieved through Jina Reader](https://ai.google.dev/gemini-api/docs/pricing) — accessed 2026-10-13.
- <a id="source-A1"></a> [A1: Inspected current Gemini adapter](repo:src/core/providers/gemini_tool.py) — accessed 2026-10-13.
- <a id="source-R1"></a> [R1: Historical model-mediated report without raw tool trace](repo:reports/data/legacy/gemini_tool_live.json) — accessed 2026-10-13.
- <a id="source-L1"></a> [L1: Existing README with unverified resource ceilings](repo:providers/gemini_tool/README.md) — accessed 2026-10-13.

<!-- COMMON CONTRACT END -->

## Detailed provider dossier
# Gemini model-mediated Code Execution (`gemini_tool`)

Reviewed: **2026-10-13**. Deployment: **model_mediated**. Customization: **fixed_runtime**.

## Execution and customization boundary

Gemini Code Execution lets the **model generate, run, inspect, and potentially revise Python** within a model request. Enabling the tool and asking for execution does not guarantee that the submitted source is executed verbatim, or that a tool invocation occurred. There is no standalone arbitrary-code execution endpoint in this tool interface. Model generation, execution and answer synthesis contribute to request latency. [G1, G2, A1]

The environment supplies a fixed library list; **users cannot install their own libraries**. Model, prompt, generation/thinking options and compatible tool combinations are model-level configuration, not container image, CPU, RAM, GPU or network configuration. Google Search/function calling can be combined where supported, but those tools do not establish internet access from the Python sandbox. [G1, G2]

Official docs set a **30-second maximum code-environment runtime**, and the Developer API guide describes up to five code regenerations after errors. We did not verify the README's approximate **1 GB RAM** or **50 KB stdout** ceilings from current official documentation. Do not use those numbers as measured or configurable limits. [G1, G2, L1]

### Images and file I/O

“Image support” means **input/output media**, not a custom container image. Current Developer API documentation explicitly supports Gemini 3 Flash image inspection/manipulation using Code Execution and Thinking. The inspected adapter defaults to **`gemini-2.5-flash`** and sends only text; it does not test that newer image workflow. Graphs/images may be inline response data. [G1, A1]

- **Developer API:** inline file input or Files API upload, primarily text/CSV; input size constrained by the model context window; output returned inline. This is not a general bidirectional sandbox filesystem API. [G1]
- **Vertex AI / current Google Cloud guide:** code-execution file URIs are not supported as I/O; inline bytes are supported for the listed MIME types, including CSV and images, with graph output. Developer Files API behavior must not be assumed to apply to this route. [G2]
- Multi-turn conversations/`previous_interaction_id` are documented in current Developer API examples. That is conversational context continuity, not a guarantee of durable files or addressable Python kernel memory. [G1]

## Capability matrix

`documented` refers to an inspected official guide or request/code contract. Historical model-mediated output lacking tool traces remains `unverified`; new trace-validated observations are linked separately below.

| Feature ID | Support | Evidence | Scope / qualification | Sources |
|---|---|---|---|---|
| `custom_image` | unsupported | documented | Fixed hosted Python environment; no container image selector. | G1, G2 |
| `runtime_packages` | unsupported | documented | Preinstalled libraries only; own library installation explicitly prohibited. | G1, G2 |
| `cpu_sizing` | unsupported | documented | No tool-level vCPU selector; model selection is not CPU sizing. | G1, A1 |
| `memory_sizing` | unsupported | documented | No tool-level RAM selector; approximate README ceiling unverified. | G1, G2, L1 |
| `gpu` | unsupported | documented | No selectable sandbox accelerator; included TensorFlow is not GPU evidence. | G1, G2 |
| `network_policy` | unsupported | unverified | No configurable policy in inspected tool request. Historical DNS/HTTP/metadata probes blocked; not an exhaustive official no-egress guarantee. | A1, R1 |
| `persistent_storage` | unsupported | documented | No durable mount/storage interface documented for built-in Code Execution. Scratch disk I/O in one response is not persistence. | G1, G2, A1, R1 |
| `session_reuse` | unknown | unverified | Multi-turn context supported; reusable kernel/filesystem continuity not established. Adapter sends independent `generate_content` requests. | G1, A1, R1 |
| `shell` | unsupported | documented | First-class execution only Python, no shell/SSH API. Python subprocess behavior is not a shell service contract. | G1, G2 |
| `file_transfer` | conditional | documented | Inline/Files API input and inline graph/image output depend on API/model; Vertex excludes file URI I/O. Adapter implements neither file input nor artifact collection. | G1, G2, A1 |
| `ports_preview` | unsupported | documented | No service port/public preview interface. | G1, A1 |
| `self_hosting` | unsupported | documented | Built-in Google-hosted tool; external custom function execution is a different deployment. | G1, G2 |
| `cmek` | unknown | unverified | No Code Execution runtime key selection/coverage verified. Other Google Cloud sandbox CMEK services do not prove this tool's support. | G2, A1 |

## Inspected / historical tested configuration

- **Requested:** `google-genai` `generate_content(model=self.model_name, contents=text_prompt, tools=[Tool(code_execution=ToolCodeExecution())])`; default model `gemini-2.5-flash`. If `GEMINI_API_KEY` is present, Developer API is used; otherwise `vertexai=True`, project from `GOOGLE_CLOUD_PROJECT` (with a hard-coded fallback), location from `GOOGLE_CLOUD_LOCATION` (fallback `europe-west8`). Environment branch, resolved model version and project/location are not captured in the report. [A1]
- No timeout, generation/thinking budget, image, library, resource or network customization is forwarded. Inputs are not staged; artifact collection returns `[]`; no conversation/session handle is retained. [A1]
- The updated adapter uses the async client, retains tool outcome/block metadata, requires exact requested source execution and successful outcomes for validation, and rejects prose-only responses. This fixes the historical success-reporting problem; it does not make model-mediated latency a raw-runtime measure. [A1]
- `reports/data/legacy/gemini_tool_live.json` contains 11 historical rows, reports Python 3.11.8, imports of NumPy/pandas/SciPy/Matplotlib, blocked DNS/HTTP/metadata probes and `pip_error_TypeError`. The memory row says **`ExecuteCode failed`** yet has `status: success`; timeout output says **`Code execution timed out. Forcefully killed.`** yet also has success. No RAM ceiling follows from these records. [R1]
- Artifact row has `collection: empty` and no output files. Five “turns” in `agent_multiturn` are inside one Python program, not cross-request kernel reuse. Constant 500 prompt/250 completion token counts and `$0.0001125` costs across suites are estimates, not captured token usage or invoices. [R1]
- [Current evaluated attempts](../../reports/data/attempts/gemini_tool_evaluation.json) include five complete-contract trials each for readiness, prime sieve, SQLite and inventory, all passing exact-code/tool-outcome and output checks. The guest reports Python 3.11.8, x86_64, eight visible CPUs and 2 GiB physical memory; those are observations, not guaranteed resources. SQLite had substantial request-latency variation; newer image/Interactions workflows remain untested. [Tested configurations](tested-configurations.md) capture model/SDK/source settings.

## Pricing (USD)

**No separate Code Execution enablement, container/session or runtime fee**; model tokens remain billable. Generated code/results and their reuse in iterative reasoning affect token billing. Thinking and summary output can add cost. Use response usage metadata rather than fixed report token guesses. [G1, G3]

Paid **Gemini Developer API Standard `gemini-2.5-flash`**, matching the adapter's default model name: [G3]

| Resource | Exact unit | Amount |
|---|---|---|
| Text/image/video input | 1,000,000 input tokens | $0.30 |
| Audio input | 1,000,000 input tokens | $1.00 |
| Output, including thinking | 1,000,000 output tokens | $2.50 |
| Separate Code Execution charge | Tool enablement / runtime charge | $0 |

These are Standard paid-tier Developer API rates, not Batch/Flex/Priority rates or a verified Vertex regional quote. The adapter sends text only; audio is an optional API modality. Free-tier availability/quotas differ. Files API retention, context-cache storage and other enabled tools are not Python session fees. No price-increase claim is made and no cloud billing was queried. [G3, A1]

## Sources

Official pages accessed 2026-10-13:

- **G1:** [Gemini Developer API Code Execution](https://ai.google.dev/gemini-api/docs/code-execution) (retrieved through Jina Reader after direct transport failure; official content, updated 2026-10-09)
- **G2:** [Google Cloud Code Execution guide](https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/code-execution) (redirects to current Agent Platform model tools documentation; updated 2026-10-12)
- **G3:** [Gemini Developer API pricing, `gemini-2.5-flash` and tool pricing](https://ai.google.dev/gemini-api/docs/pricing) (official content retrieved through Jina Reader)

Local sources: **A1** [current adapter](../../src/core/providers/gemini_tool.py), **R1** [historical report](../../reports/data/legacy/gemini_tool_live.json), **L1** [existing README](README.md). README limits are historical claims, not authoritative verification.
