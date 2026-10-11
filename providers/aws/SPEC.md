<!-- COMMON CONTRACT START -->
# Provider contract: AWS AgentCore (`aws`)

**Sources reviewed:** 2026-10-13 · **Deployment:** `managed_tool`

## 1. Executive summary and product boundary

AgentCore Code Interpreter via boto3; not AgentCore Runtime BYOC or classic Bedrock model-mediated execution.

Amazon Bedrock AgentCore Code Interpreter, directly invoked using boto3; not classic Bedrock model-mediated code interpretation, AgentCore Runtime BYOC, or a self-managed EC2/Firecracker VM. The adapter selects a pre-existing tool and region and requests only a session name and timeout. Package customization remains unverified; file operations are documented but this adapter is text-only and collects one hard-coded output.

Working adapter: [source](../../src/core/providers/aws_agentcore.py). Historical adapter hashes refer to measured revisions, not necessarily current source.

The preserved dossier describes the dated inspected configuration. New budget/lifecycle guardrails change current adapter defaults without changing historical cohort evidence; see [operations](../../CONTRIBUTING.md).

## 2. Documented contract vs measured adapter

Support describes the platform. Measured describes only a bounded oracle on a recorded setup. Documented-only and unverified entries remain coverage gaps.

| Capability | Platform support | Evidence state | Documented contract / scope | Measured adapter behavior | Sources |
|---|---|---|---|---|---|
| `custom_image` | unsupported | Documented | Reviewed CreateCodeInterpreter and StartCodeInterpreterSession APIs expose no custom image input. A custom interpreter means network/role/certificate/filesystem configuration, not BYOC. AgentCore Runtime container deployment is a different product path. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [aws_create](#source-aws_create), [aws_start](#source-aws_start), [aws_pricing](#source-aws_pricing) |
| `runtime_packages` | unknown | Unverified | Prebuilt runtimes and terminal commands are documented; current readiness/CPU/SQLite/repository/output/inventory trials do not install a package or prove arbitrary dependencies. Acquisition depends on networking and permissions. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [aws_overview](#source-aws_overview), [aws_tools](#source-aws_tools), [aws_network](#source-aws_network), [report](#source-report) |
| `cpu_sizing` | unsupported | Documented | No CPU sizing field in reviewed create/start APIs. Guest inventory shows two visible/affinity CPUs; this is not a configurable reservation or consumed CPU billing measurement. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [aws_create](#source-aws_create), [aws_start](#source-aws_start), [aws_pricing](#source-aws_pricing), [adapter](#source-adapter), [report](#source-report) |
| `memory_sizing` | unsupported | Documented | No RAM sizing field in reviewed create/start APIs. Guest inventory reports about 7.83 GiB physical memory; consumed/billable memory and reservation remain unattested. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [aws_create](#source-aws_create), [aws_start](#source-aws_start), [aws_pricing](#source-aws_pricing), [report](#source-report) |
| `gpu` | unknown | Unverified | No accelerator selection in reviewed Code Interpreter APIs. New guest inventory has no nvidia-smi device output, which cannot establish platform-wide GPU eligibility. Runtime Instances/EC2 GPU pricing is a separate product. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [aws_create](#source-aws_create), [aws_start](#source-aws_start), [aws_pricing](#source-aws_pricing), [report](#source-report) |
| `network_policy` | supported | Documented | Custom interpreters support PUBLIC, SANDBOX and VPC; VPC specifies subnets/security groups. SANDBOX allows limited AWS-service access such as S3, not general public egress. The adapter comment declares SANDBOX but does not fetch tool configuration or set network mode; effective tested mode remains unattested. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [aws_network](#source-aws_network), [aws_resources](#source-aws_resources), [aws_create](#source-aws_create), [adapter](#source-adapter), [report](#source-report) |
| `persistent_storage` | conditional | Documented | Default files persist within a session, not a durable cross-session filesystem. Current docs support customer-owned S3 Files/EFS mounts with VPC, IAM, mount targets and security groups, but no managed Code Interpreter session-storage option. Adapter supplies no mounts; persistence untested. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [aws_sessions](#source-aws_sessions), [aws_filesystems](#source-aws_filesystems), [adapter](#source-adapter), [report](#source-report) |
| `session_reuse` | supported | Documented | Multiple invocations may share sessionId/state until stop or timeout. Default timeout 900s, maximum 28800s. Adapter starts a fresh session on every execute with max(request.timeout_seconds,60), then stops in cleanup; cross-invocation reuse untested. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [aws_sessions](#source-aws_sessions), [aws_start](#source-aws_start), [adapter](#source-adapter), [report](#source-report) |
| `shell` | supported | Documented | Official executeCommand/startCommandExecution terminal APIs exist. Adapter currently calls executeCode with Python; the selected readiness evaluation does not exercise a shell. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [aws_tools](#source-aws_tools), [adapter](#source-adapter), [report](#source-report) |
| `file_transfer` | conditional | Documented | Service documents file upload/download and 100MB inline support. Adapter decodes inputs as UTF-8 with errors=ignore and collects only transformed_output.txt as text, so its binary-transfer capability declaration is not implemented byte-faithfully. Selected evaluation contains no artifact check. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [aws_overview](#source-aws_overview), [aws_tools](#source-aws_tools), [adapter](#source-adapter), [report](#source-report) |
| `ports_preview` | unknown | Unverified | Reviewed interpreter APIs/docs and adapter do not establish arbitrary inbound ports or public preview URLs. Public outbound network mode is not inbound port exposure. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [aws_create](#source-aws_create), [aws_network](#source-aws_network), [adapter](#source-adapter) |
| `self_hosting` | unsupported | Documented | Fully managed Code Interpreter tool; direct API use without an LLM does not make the runtime self-hosted. Self-managed EC2/container/Firecracker and AgentCore Runtime are separate paths. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [aws_overview](#source-aws_overview), [aws_resources](#source-aws_resources) |
| `cmek` | unknown | Unverified | Adapter declares cmek_supported=true, but reviewed create/start schemas expose no customer-managed KMS key input for the interpreter runtime. General AgentCore encryption docs enumerate Memory/Gateway support, not an interpreter guarantee. Customer-owned storage encryption is a separate surface; no key attestation in report. | No independently mapped passing fixture here; inspect dossier/configuration limits. | [adapter](#source-adapter), [aws_create](#source-aws_create), [aws_start](#source-aws_start), [aws_encryption](#source-aws_encryption), [aws_filesystems](#source-aws_filesystems), [report](#source-report) |

## 3. Six residency surfaces

Source: [dated residency audit and original vendor citations](../../reports/docs/eu-data-residency.md). These are documented boundaries/gaps, not measured EU residency or GDPR certification.

| Surface | Documented boundary / verification gap |
|---|---|
| Compute | Regional tool/client; Stockholm requested; check feature matrix |
| Files / volumes / snapshots / backups | Customer S3/EFS separately configured; session guide lists 30-day retention |
| Stdout / stderr / traces | Log placement/replication must be assessed separately |
| Control plane / metadata | Customer-content commitments exclude various account/management data |
| Support access / subprocessors | Confirm service/legal exceptions and support access |
| External model / API calls | Model inference and external calls separate |

Benchmark location/request provenance is recorded separately in [tested configurations](tested-configurations.md).

## 4. Dated pricing and billing units

Code Interpreter actual CPU consumption and peak memory consumed up to each second over session lifetime, including system overhead; per-second increments, 1-second minimum and 128MB minimum memory billing.

| SKU / resource | Original billing unit | USD list amount | Sources |
|---|---|---:|---|
| Code Interpreter CPU | vCPU-hour consumed | 0.0895 | [aws_pricing](#source-aws_pricing) |
| Code Interpreter memory | GB-hour (peak consumed up to each second) | 0.00945 | [aws_pricing](#source-aws_pricing) |
| Network and customer-owned persistent storage | applicable EC2/S3 Files/EFS SKU | Unknown | [aws_pricing](#source-aws_pricing), [aws_filesystems](#source-aws_filesystems) |

Official Code Interpreter rates reviewed 2026-10-13; these are not Runtime v2 or GPU instance rates. AWS pricing labels memory GB, not GiB. CPU can be uncharged during zero-CPU I/O wait, but memory is independently billed under the peak-consumption rule. Report's flat $0.00003/second times client wall time is estimate_unverified_rates with billing_verified=false, not resource-metered cost or a bill. Deployment region defaults to eu-north-1 but the saved adapter-defaults configuration does not attest the resolved tool/region or an account-specific price. No historical price increase claimed.

## 5. Recorded configuration and guest inventory

[All settings, client stacks, attempt IDs and observations](tested-configurations.md) · [Machine-readable export](tested-configurations.json)

- Setup `05a56c471d15` · adapter `beb5698440d9` · stack `be9cea6def64` · concurrency 1 · last measured 2026-10-13T16:46:54.112917+00:00.
- Setup `a017dc2faa1b` · adapter `beb5698440d9` · stack `be9cea6def64` · concurrency 1 · last measured 2026-10-13T07:37:14.126397+00:00.
- Setup `39ed10c5d0c2` · adapter `c4828f950bf6` · stack `unrecorded` · concurrency 1 · last measured 2026-10-13T07:15:46.603819+00:00.

Guest-visible CPU/RAM and device probes do not attest reserved hardware or isolation. No GPU configuration was benchmarked in this snapshot.

## 6. Dated source register

- <a id="source-adapter"></a> [adapter: Repository AWSAgentCoreBackend](../../src/core/providers/aws_agentcore.py) — accessed 2026-10-13.
- <a id="source-report"></a> [report: Repeated AWS readiness/CPU/SQLite/repository/output/inventory evaluations](../../reports/data/attempts/aws_evaluation.json) — accessed 2026-10-13.
- <a id="source-aws_overview"></a> [aws_overview: AWS: Code Interpreter overview](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/code-interpreter-tool.html) — accessed 2026-10-13.
- <a id="source-aws_create"></a> [aws_create: AWS: CreateCodeInterpreter API](https://docs.aws.amazon.com/bedrock-agentcore-control/latest/APIReference/API_CreateCodeInterpreter.html) — accessed 2026-10-13.
- <a id="source-aws_start"></a> [aws_start: AWS: StartCodeInterpreterSession API](https://docs.aws.amazon.com/bedrock-agentcore/latest/APIReference/API_StartCodeInterpreterSession.html) — accessed 2026-10-13.
- <a id="source-aws_network"></a> [aws_network: AWS: PUBLIC/SANDBOX/VPC network configuration](https://docs.aws.amazon.com/bedrock-agentcore-control/latest/APIReference/API_CodeInterpreterNetworkConfiguration.html) — accessed 2026-10-13.
- <a id="source-aws_resources"></a> [aws_resources: AWS: Code Interpreter resources and network semantics](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/code-interpreter-resource-management.html) — accessed 2026-10-13.
- <a id="source-aws_sessions"></a> [aws_sessions: AWS: Session isolation, lifetime and state](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/code-interpreter-session-characteristics.html) — accessed 2026-10-13.
- <a id="source-aws_tools"></a> [aws_tools: AWS: Code, terminal and file API examples](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/code-interpreter-api-reference-examples.html) — accessed 2026-10-13.
- <a id="source-aws_filesystems"></a> [aws_filesystems: AWS: Customer-owned S3 Files/EFS mounts](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/code-interpreter-filesystem-configurations.html) — accessed 2026-10-13.
- <a id="source-aws_encryption"></a> [aws_encryption: AWS: AgentCore data encryption and resource-specific KMS support](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/data-encryption.html) — accessed 2026-10-13.
- <a id="source-aws_pricing"></a> [aws_pricing: AWS: AgentCore pricing, Code Interpreter section/table](https://aws.amazon.com/bedrock/agentcore/pricing/) — accessed 2026-10-13.

<!-- COMMON CONTRACT END -->

## Detailed provider dossier
# aws — Amazon Bedrock AgentCore Code Interpreter

Reviewed **2026-10-13**. Machine-readable companion: [spec.json](spec.json).

## Identity and tested integration

The adapter calls **AgentCore Code Interpreter directly through boto3**, using `start_code_interpreter_session`, `invoke_code_interpreter(name="executeCode", language="python")`, and `stop_code_interpreter_session`. No model inference is required for this path. It is distinct from classic Bedrock model-mediated interpretation, AgentCore Runtime container/instance hosting, and self-managed Firecracker/EC2 infrastructure. Official session docs describe dedicated microVM isolation, but this repository did not measure isolation strength. [adapter, aws_overview, aws_sessions]

| Dimension | Requested by tested integration | Actual evidence |
|---|---|---|
| CPU / RAM | No sizing fields | Guest inventory: two visible/affinity CPUs and about 7.83 GiB reported physical memory. Reserved allocation and billable consumption are not attested. |
| Network | Pre-existing tool selected; no mode set at session start | Adapter declares SANDBOX in a comment. Tool configuration not fetched or saved, so effective mode unknown. |
| Image / runtime | No image; `language="python"` | Python **3.12.13** observed. Image digest unknown. |
| Region / tool | Arguments, then environment, then adapter defaults; region default `eu-north-1` | New request records capture resolved region; tool network/configuration not independently attested. |
| Lifetime | Session timeout `max(request.timeout_seconds, 60)` | Service API default 900s; maximum 28,800s. Adapter starts a new session every execute and stops during cleanup. |

Sources: [adapter, report, aws_start]. The [current evaluated report](../../reports/data/attempts/aws_evaluation.json) now includes five complete-contract trials for readiness, CPU, SQLite, repository edit/test, stdout fidelity and runtime inventory. All except stdout fidelity passed 5/5. The expected 131,072-byte output returned 131,071 bytes despite removal of adapter `.strip()`; the end-to-end integration still loses one trailing byte. This is not a vendor-wide file-size limit. See [exact tested configurations](tested-configurations.md). Client wall time includes SDK/session work; `cold_start_ms: 0` is not zero remote boot latency.

## Capabilities: all 13 feature IDs

| Feature ID | Support / evidence | Scope and limitation | Sources |
|---|---|---|---|
| `custom_image` | unsupported / documented | No image input in reviewed create/start interpreter APIs. “Custom interpreter” configures networking/role/filesystems/certificates, not BYOC. | aws_create, aws_start, aws_pricing |
| `runtime_packages` | unknown / unverified | Prebuilt runtimes and terminal execution documented; arbitrary package installation not established by selected evaluation. | aws_overview, aws_tools, aws_network, report |
| `cpu_sizing` | unsupported / documented | No caller CPU sizing in reviewed interpreter APIs; no upfront resource selection. | aws_create, aws_start, aws_pricing, adapter, report |
| `memory_sizing` | unsupported / documented | No caller RAM sizing; billed memory consumption is not hardware inventory. | aws_create, aws_start, aws_pricing, report |
| `gpu` | unknown / unverified | No requested/inventoried accelerator. Runtime Instances GPU offerings cannot be attributed to Code Interpreter. | aws_create, aws_start, aws_pricing, report |
| `network_policy` | supported / documented | PUBLIC, SANDBOX and VPC configuration at tool creation. Effective selected mode unattested. | aws_network, aws_resources, aws_create, adapter, report |
| `persistent_storage` | conditional / documented | Live-session files; customer-owned S3 Files/EFS mounts require VPC/IAM/security groups. Adapter supplies no mounts. | aws_sessions, aws_filesystems, adapter, report |
| `session_reuse` | supported / documented | State reused with session ID until stop/timeout. Adapter does not reuse across execute calls. | aws_sessions, aws_start, adapter, report |
| `shell` | supported / documented | `executeCommand` and asynchronous terminal tools exist. Adapter readiness test uses only Python. | aws_tools, adapter, report |
| `file_transfer` | conditional / documented | Service supports file tools; adapter uploads/collects text with lossy binary conversion and one output name. | aws_overview, aws_tools, adapter, report |
| `ports_preview` | unknown / unverified | No arbitrary inbound port or preview URL capability established. Public egress is not inbound exposure. | aws_create, aws_network, adapter |
| `self_hosting` | unsupported / documented | AWS-managed interpreter tool, independent of where client/agent runs. | aws_overview, aws_resources |
| `cmek` | unknown / unverified | Adapter declaration lacks interpreter-specific key configuration or runtime encryption attestation. | adapter, aws_create, aws_start, aws_encryption, aws_filesystems, report |

### Integration caveats

- **File fidelity:** input bytes are decoded with `utf-8, errors="ignore"`; returned text is re-encoded. Collection requests only `transformed_output.txt`. Thus `supports_direct_binary_transfer=true` and generic multiple-output declarations overstate this implementation. The selected evaluation does not verify file round trips. Official inline support is up to 100 MB, with larger S3 workflows documented separately. [adapter, aws_overview, aws_tools, report]
- **Network:** SANDBOX is not necessarily “all network disabled”: AWS documents limited AWS-service access, including S3. PUBLIC permits general internet access; VPC permits private-resource connectivity with configured subnets/security groups and routing. The adapter's comment does not attest any of those effective settings. [aws_network, aws_resources, adapter]
- **Storage:** default files are available for session lifetime. Current interpreter filesystem docs support bring-your-own S3 Files and EFS access points, shared across sessions, but explicitly do **not** offer Runtime's managed session-storage option. These require account/VPC/IAM/mount-target setup and were not configured here. [aws_sessions, aws_filesystems, adapter]
- **CMEK:** `cmek_supported=true` is not sufficient evidence. Reviewed interpreter create/start APIs have no customer-managed runtime key field; general AgentCore encryption docs enumerate resource-specific key support rather than promising it for all services. Encryption on customer-owned storage is a different surface from interpreter runtime encryption. Mark the latter unknown pending a specific official contract and deployment readback. [adapter, aws_create, aws_start, aws_encryption, aws_filesystems]

## Pricing

Official **Code Interpreter** pricing reviewed October 13:

| Resource | Published USD unit/rate |
|---|---|
| CPU | **$0.0895 / vCPU-hour** consumed |
| Memory | **$0.00945 / GB-hour**, peak consumed up to each billed second |

Billing uses per-second increments, a **one-second minimum**, and **128 MB minimum memory billing**, spans microVM boot through session termination, and includes system overhead. CPU may have no charge during zero-CPU I/O waits; memory is independently charged under its peak-consumption rule. Preserve AWS's **GB** label rather than silently converting it to GiB. Network transfer uses applicable EC2 rates; customer-owned persistent storage has separate charges. [aws_pricing, aws_filesystems]

`aws_evaluation.json` multiplies client wall time by a flat `$0.00003/second` and explicitly marks `estimate_unverified_rates` / `billing_verified=false`. It is not a resource-metered bill. Do not substitute the pricing page's **Runtime v2** rates or **Runtime Instances GPU/EC2 management fees** for Code Interpreter rates. No historical interpreter price increase is established. [report, aws_pricing]

## Deployment overhead

The managed tool avoids provisioning a caller-owned VM. Integration still needs AWS credentials, IAM permissions, an available tool in the selected region, session lifecycle and streamed-result handling. Custom networking and customer-owned storage additionally require execution-role, VPC, security-group and mount-target configuration. AgentCore Runtime BYOC or EC2/container isolation would be separate deployments with a different API, lifecycle, customization and cost model; they are not tested alternatives within this adapter. [adapter, aws_resources, aws_create, aws_filesystems, aws_pricing]

## Source references

All accessed 2026-10-13. Local sources describe this integration; official sources describe the service.

- **adapter** — [AWS adapter](../../src/core/providers/aws_agentcore.py)
- **report** — [Saved readiness evaluation](../../reports/data/attempts/aws_evaluation.json)
- **aws_overview** — [Code Interpreter overview](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/code-interpreter-tool.html)
- **aws_create** — [CreateCodeInterpreter](https://docs.aws.amazon.com/bedrock-agentcore-control/latest/APIReference/API_CreateCodeInterpreter.html)
- **aws_start** — [StartCodeInterpreterSession](https://docs.aws.amazon.com/bedrock-agentcore/latest/APIReference/API_StartCodeInterpreterSession.html)
- **aws_network** — [Network configuration](https://docs.aws.amazon.com/bedrock-agentcore-control/latest/APIReference/API_CodeInterpreterNetworkConfiguration.html)
- **aws_resources** — [Resources and network semantics](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/code-interpreter-resource-management.html)
- **aws_sessions** — [Session lifetime and isolation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/code-interpreter-session-characteristics.html)
- **aws_tools** — [Terminal/file/code API examples](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/code-interpreter-api-reference-examples.html)
- **aws_filesystems** — [Customer-owned filesystem configuration](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/code-interpreter-filesystem-configurations.html)
- **aws_encryption** — [Data encryption](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/data-encryption.html)
- **aws_pricing** — [AgentCore pricing, Code Interpreter section](https://aws.amazon.com/bedrock/agentcore/pricing/)
