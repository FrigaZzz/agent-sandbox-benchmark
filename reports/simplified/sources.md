# Source register for the short decision guide

Reviewed. Historical announcement dates below remain historical; live-page retrieval dates are not tariff effective dates. Measured findings describe retained cohorts, not newly run experiments.

## Why revisit the architecture now?

The publication story starts with Google and Databricks sandbox news prompting the author's side-project architecture review, principally around cost. The personal motivation is supplied by the author. News and market evidence explain the context; the benchmark does not independently measure those announcements or market trends.

| Source | Date / evidence | Supported use |
| :--- | :--- | :--- |
| [Google Agent Platform release notes](https://docs.cloud.google.com/gemini-enterprise-agent-platform/release-notes#September_09_2026) | 9 September 2026: Shell and Computer Use sandboxes GA, plus private-network controls, CMEK and pause/resume | New execution choices and a reason to investigate idle-resource management. Pause preserves filesystem state and connection identity while descheduling compute. This is not a memory-resume finding or a result from the measured default-code adapter. BYOC/template/snapshot preview was announced 26 May, not made GA by this release. |
| [Databricks Agent Bricks announcement](https://www.databricks.com/blog/agent-bricks-dais-2026) | 16 June 2026: Sandbox introduced within Agent Bricks | A newer execution option alongside the data platform. [Current dedicated documentation](https://docs.databricks.com/aws/en/compute/serverless/sandbox) describes Beta, currently no-charge with future pricing unresolved. Measured SQL `python_exec` is a separate surface. |
| [Stanford 2025 AI Index](https://hai.stanford.edu/ai-index/2025-ai-index-report) | Historical period: November 2022 to October 2024 | Reports a greater-than-280-fold inference-cost drop for GPT-3.5-level performance. Supports a bounded cost-of-capability trend, not lower prices for every frontier model or complete job. Its reported long-run hardware cost/efficiency improvements concern different periods/metrics from the 2026 price pressures below. |
| [Theo - t3.gg: "I thought AI was gonna get cheaper?"](https://www.youtube.com/watch?v=vRS2leJLAI0) | Uploaded 12 October 2026; metadata and English automatic captions retrieved | At 04:12 to 04:50, separates token/task/capability prices; at 08:18 considers cost at a given capability; [13:05 to 14:10](https://www.youtube.com/watch?v=vRS2leJLAI0&t=785s) discusses expanded end-to-end work. Attribute the argument that cheaper capability can coexist with growing spending. The video does not establish memory shortages or that sandbox execution always costs more than inference. |
| [TrendForce memory-market report](https://www.trendforce.com/presscenter/news/20260930-13258.html) | 30 September 2026: forecasts conventional DRAM contract prices rising 10 to 15% quarter-on-quarter in Q4 2026 | Reports tight server-memory supply, including demand for general servers supporting agentic AI. This is a procurement-market forecast, not realized price increases across managed sandbox services. |
| [Hetzner price adjustment](https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/#cloud-servers) | Effective 15 June 2026 for new orders/rescales, with legacy exceptions | Actual supplier-price increases. Germany/Finland monthly CAX11: €4.49 to €5.99, about 33.4%; CX23: €3.99 to €5.49, about 37.6%; excluding VAT/IPv4. [Official explanation](https://www.hetzner.com/pressroom/standardization-and-price-adjustment-of-our-server-products/) attributes the change to procurement-cost pressure. Does not prove rate rises at each benchmark provider. |

The defensible connection is: cheaper access to capable models allows more ambitious work; larger jobs consume more machine resources; memory supply and some infrastructure prices face upward pressure. For a particular job, execution can exceed inference cost, as the hypothetical example below illustrates. Supplier rates, workload resource consumption and completed-task costs are separate quantities.

## Claims and their boundaries

| Slide / claim | Evidence | What the evidence establishes |
| :--- | :--- | :--- |
| 2 / Sandbox news prompted the author's review | Official Google/Databricks announcements and supplied personal motivation, above | New options are documented context, not measured results from the default-code/SQL benchmark paths. |
| Guide / Different workloads need different controls | [Fixture inventory](../docs/detailed-report.md#3-workloads-and-independent-oracles), [methods](../docs/evaluation-framework.md) | CPU file/data, edit/test and cross-call work were exercised. GPU, advanced image and stop/resume paths were not. The smallest adequate setup is a design recommendation. |
| 3 / Files, stopped disk and memory are separate contracts | [Recorded state checks](../docs/findings.md#operations-with-useful-positive-evidence), [fixture limits](../docs/detailed-report.md#3-workloads-and-independent-oracles) | E2B/Modal file state and exception recovery passed in the cited cohorts. This is not memory or stop/resume evidence. |
| 3 / E2B default pause preserves files and memory | [E2B persistence](https://docs.e2b.dev/sandbox/persistence.md) | The documentation describes filesystem and memory on default pause. Filesystem-only modes and failure/auto-pause behaviour have qualifications; the required path needs testing. |
| 4 / Templates do not allocate a GPU | [E2B GPU FAQ](https://docs.e2b.dev/faq/gpu-support.md), [Modal resources](https://modal.com/docs/guide/sandbox-resources) | E2B documents CPU-only sandboxes including BYOC. Modal GPU Sandboxes require an explicit GPU request, gVisor and preemption handling. |
| 4 / Daytona shared GPU ignores region preference | [Daytona regions](https://www.daytona.io/docs/en/regions.md) | Shared GPU sandboxes/snapshots use logical `earth` placement; dedicated/custom region contracts differ. |
| 5 / Compute placement is only part of residency | [Modal data residency](https://modal.com/docs/guide/data-residency), [region selection](https://modal.com/docs/guide/region-selection), [full source guide](../docs/eu-data-residency.md) | Modal documents strict compute pinning, EEA scope for `eu`, US logs, explicitly created snapshots and managed durable storage. Lifecycle calls use the US-east control plane. Customer-regional bucket mounts are a different option. |
| 5 / Model calls, backups and access paths need their own map | [Full data-surface guide](../docs/eu-data-residency.md), [EDPB transfer guidance](https://www.edpb.europa.eu/sme-data-protection-guide/international-data-transfers_en) | A recommendation to inspect every surface, not a claim that all providers put them abroad. GDPR does not impose blanket EU-only hosting. |
| 6 / Cheaper capability and infrastructure price pressure concern different markets | Stanford AI Index, TrendForce and Hetzner sources above | Historical fixed-performance inference-cost decline, current memory procurement forecast and actual supplier-price adjustments have different units and time periods. None establishes every sandbox's price trend. |
| Deep dive / Output can be wrong despite API success | [Exact output observations](../docs/findings.md#all-deadlineoutput-observations-and-exact-attempts) | In cited cohorts, expected stdout was 131,072 bytes. AWS returned 131,071 (missing final newline); Blaxel returned 65,602 with a truncation banner. Each exact-output check failed 5/5 times. This is not a general file-transfer limit. |
| 8 + guide / Timeout response does not prove remote cancellation | [Deadline evidence](../docs/findings.md#deadline-responses), [oracle implementation](../../src/bench/validation.py), [fixture](../../src/bench/suites/timeout_handling.py) | Checks concern timeout status, absent completion marker and bounded response time. Process death and late side effects were not independently verified. |
| 7 / Execution or inference can dominate the bill | Official prices and hypothetical arithmetic below | Explicit illustrative quantities only; no measured bills or equal-performance claims. |
| 8 / Gross cost per verified completion; credits separate | [Cost interpretation](../docs/detailed-report.md#7-pricing-credits-and-value) | A recommended accounting framework. The dataset has no invoice-backed cost winner. |
| 9 / E2B, Modal and Google default code give file/data candidates | [Positive workflow evidence](../docs/findings.md#operations-with-useful-positive-evidence) | Checked binary and pipeline results in the cited setups. Does not validate new Google shell/computer-use features, GPU work, resume or production reliability. |

## Inference price changes: a bounded historical comparison

Two official announcements provide a concrete example of cheaper small-model inference:

| Announcement | Input / million tokens | Output / million tokens |
| :--- | ---: | ---: |
| [OpenAI, 25 January 2024: GPT-3.5 Turbo-0125, announced for the following week](https://openai.com/index/new-embedding-models-and-api-updates/) | $0.50 | $1.50 |
| [OpenAI, 18 July 2024: GPT-4o mini](https://openai.com/index/gpt-4o-mini-advancing-cost-efficient-intelligence/) | $0.15 | $0.60 |

The announced GPT-4o mini rate was **70% lower for input and 60% lower for output**. This compares two model offerings, not the same SKU over time. It does not establish equal quality for every workload or a universal monotonic price trend. The OpenAI GPT-4o mini model page still lists $0.15/$0.60 on the retrieval date used here.

Use the narrative claim "small-model inference has become much cheaper" with this bounded example. Avoid claiming all models are now cheap or that tokens always cost less than execution. This comparison does not show that compute prices increased.

## Model-agnostic scenario used in slide 7

Observed from official pages:

| Item | USD list rate | Source / qualification |
| :--- | ---: | :--- |
| Aggregate model budget | $0.003 per job | Hypothetical assumption, not a model list price; substitute actual token/cache/tool usage |
| E2B provisioned CPU | $0.000014 / vCPU-second | [Official pricing](https://e2b.dev/pricing) |
| E2B provisioned RAM | $0.0000045 / GiB-second | Same page; default sandbox is 2 vCPU and 4 GiB |
| E2B sandbox storage | Included | Same page; external services are separate |

No sandbox or model request was made for these examples. The model budget is an
**aggregate scenario assumption across the entire hypothetical job**, not a per-call
allowance or a claim about contemporary model rates. Sandbox seconds mean total
billed running time, including waiting while the sandbox remains running.

```text
assumed model budget = $0.00300

sandbox / second = 2 × $0.000014 + 4 × $0.0000045 = $0.000046
```

| Billed sandbox lifetime | Model | Sandbox | Combined marginal usage |
| :--- | ---: | ---: | ---: |
| 10 seconds | $0.00300 | $0.00046 | $0.00346 |
| 300 seconds / 5 minutes | $0.00300 | $0.01380 | $0.01680 |

At these assumed quantities, the crossover is about **65.2 billed seconds**.
The five-minute machine portion is **4.6 times** the model portion; for the ten-second
job, the model portion is about 6.52 times the machine portion. The historical model
comparison above remains source context, not the current slide's price assumption.

Assumptions: E2B Hobby marginal list usage, before credits/discounts; sandbox storage included. Excludes taxes, paid plan allocation, retries, network or third-party service charges, and additional storage services. These omissions make the example unsuitable as an invoice prediction or provider ranking. Count them in a real campaign. Physical cores, vCPUs, GB and GiB need explicit labels when comparing other providers.

## Design references

- [Assertion-evidence principles](https://www.assertion-evidence.com/principles.html): technical message headlines with supporting visual evidence. Adapted to self-contained asynchronous reading.
- [NN/g visual hierarchy](https://www.nngroup.com/articles/visual-hierarchy-ux-definition/): scale, contrast and grouping.
- [W3C contrast guidance](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html): informative text needs adequate contrast at its rendered size.

Nine pages and portrait 4:5 are editorial/layout choices. The PDF uses a restrained dark-ink/cream/lime palette, repeated section labels, direct facts and vector text. Essential scope statements sit with the claims; full source context lives here. The previews are rendered at 360 px page width for review.
