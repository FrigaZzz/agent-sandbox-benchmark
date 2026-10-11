# Agent sandbox comparison: technical report

Evidence and source snapshot. It consolidates the measured findings, requested configurations, documented capabilities and deployment questions into one reference.

## Executive summary

E2B, Modal and Google's default code integration each passed five trials for binary transfer, a 10k-row data pipeline with a returned summary, and an offline pure-Python package installation. E2B and Modal also passed cross-call filesystem state and recovery fixtures.

The exact stdout fixture found two defects in the exercised paths: AWS omitted a final newline in all five trials; Blaxel returned truncated process-log output in all five. One Blaxel prime attempt failed with a connection error. One E2B deadline response exceeded the response budget.

Results apply to specific adapters, requested setups and workload/evaluator identities. The configurations do not match hardware or geography. The pilot does not establish a production-reliability ranking, cross-tenant isolation, EU-only processing, sustained capacity or invoice-backed cost per task.

The practical next step is to shortlist by required operations and deployment eligibility, then test the exact configuration intended for use.

## 1. Product and evidence boundaries

| Product family | Application responsibility | Important comparison boundary |
| :--- | :--- | :--- |
| Model-owned code tools | Model interaction, files, tool traces and token/session usage | Gemini / OpenAI model latency and product capabilities remain separate from direct workspace APIs. |
| Managed workspace APIs | Execution orchestration, resource selection where supported, file/state lifecycle | Modal, E2B, Blaxel and Daytona differ in template, image, class, storage and placement contracts. |
| Managed cloud interpreters | Identity, exact API/tool product, network/storage configuration | AWS Code Interpreter is not Runtime BYOC; Google default code is not BYOC/GKE/VM execution. |
| Databricks execution surfaces | Select SQL, dedicated Sandbox or sandbox MCP | The evaluated SQL function cannot validate dedicated-Sandbox or MCP capabilities. |
| Self-operated infrastructure | Fleet capacity, isolation, images, routing, policies, storage and cleanup | Local HTTP subprocess results do not establish a Kubernetes or OpenSandbox deployment. |

Capability support (`supported`, `conditional`, `unsupported`, `unknown`) and evidence state (`documented`, `measured`, `unverified`) are separate fields. Unknown is not zero. A documented feature is not a successful tested deployment.

The evidence inventory retains 975 attempts, including 121 legacy/unvalidated observations. Of these, 555 carry evaluator-contract hashes, including 469 remote/model-mediated attempts. A hash records a version boundary; it does not establish complete provenance or success. Different task coverage prevents pooled vendor reliability comparisons. These inventory totals do not change the individual cohort identities in the tables below.

## 2. Published pilot configurations

The following setup identities are the cohorts cited by this report and the deck. Complete fingerprints and observation timestamps are retained in each configuration sheet. No GPU/custom-image deployment was exercised by these baseline campaigns.

| Integration | Setup / adapter prefix | Requested configuration | Client SDK | Region evidence |
| :--- | :--- | :--- | :--- | :--- |
| [Modal](../../providers/modal/tested-configurations.md) | `c6eceedf16a1` / `71538074cc69` | 2 physical-core request; 2,048 MiB request; `debian_slim`; 180s session TTL; no GPU | modal 1.6.1 | Region null; unpinned. |
| [E2B](../../providers/e2b/tested-configurations.md) | `b8b64fa8b3ea` / `44055e4ac080` | Default template; internet allowed; 180s TTL; no requested CPU/RAM/GPU | e2b-code-interpreter 2.10.5 | Cluster/region not retained. |
| [Blaxel](../../providers/blaxel/tested-configurations.md) | `ed833ceba657` / `f1238f8bfe20` | `blaxel/py-app:latest`; memory 4,096 in MB API field; memory-coupled CPU; 1h TTL | blaxel 0.4.13 | Oregon `us-pdx-1` requested. |
| [Google code](../../providers/gcp_vertex/tested-configurations.md) | `5a61c94c9323` / `c640a283b17a` | Provider-default code environment; no machine configuration; one-shot CLI lifecycle | CLI/SDK version unrecorded | Refers to an unretained preflight. |
| [AWS interpreter](../../providers/aws/tested-configurations.md) | `a017dc2faa1b` / `beb5698440d9` | Provider-default interpreter; fresh session; no requested CPU/RAM/image sizing | boto3 1.43.112 | Stockholm `eu-north-1` requested. |
| [Databricks SQL](../../providers/databricks/tested-configurations.md) | `629df7809d28` / `ff6ebfad7dbf` | `system.ai.python_exec` through an existing warehouse; no resource sizing | databricks-sdk 0.151.0 | Warehouse region/type not retained. |

The client stack records Python 3.13.13 for these cohorts. Guest Python, architecture and visible resources differ. Requested resources, guest observations and independently attested placement/allocation are different evidence categories. Image tags such as `latest` are not immutable image digests.

Successful current remote baselines were not established for Daytona, dedicated Databricks Sandbox or OpenAI in the retained prerequisite attempts. Missing credentials and unavailable APIs are access/integration gaps, not vendor uptime measurements. Gemini is model-mediated and retained separately. Infrastructure-owned deployment evidence remains incomplete.

## 3. Workloads and independent oracles

| Fixture | Work performed | Required evidence |
| :--- | :--- | :--- |
| Readiness | Print exact ready marker and runtime version | Expected output; client lifecycle time. |
| Prime calculation | Count primes below 2,000,000 | Exactly 148,933; guest timing separate from lifecycle. |
| Binary artifact | Upload and transform 26,900 bytes | Host byte equality / SHA-256 checks. |
| CSV pipeline | Deduplicate/validate 10k transactions; aggregate integer cents | Independent expected totals and returned summary artifact. |
| SQLite | Insert 20k rows; index/query; rollback | Expected row/query result and preserved rollback state. |
| Synthetic edit/test task | Reproduce CSV-parser failure, edit two-file fixture, rerun four assertions | Initial failure and corrected passing assertions; no repository clone or full build. |
| Stdout fidelity | Print 131,072 ordered Unicode bytes | Exact bytes, order and final newline. |
| Cross-call state | Read/write files across three API calls | Expected state change from 40 to 42. |
| Error recovery | Write sentinel, raise error, reconnect/call again | Same files survive; follow-up returns 42. |
| Dependency install | Upload wheel, install privately, import/use | `--no-index --no-deps --target`; expected execution. |
| Deadline handling | Sleep beyond a 4s request deadline | Execution timeout; no completion marker; execute response within 9s. |
| Inventory | Versioned guest probe | CPU/cgroup/memory/packages/runtime/tool observations with attempt reference. |

Execution success and evaluation outcome are separate. A missing artifact or wrong bytes fails even if the API returns successfully. Expected negative behavior can pass. Cleanup/teardown outcomes remain in the record, but API success is not independent proof of cloud absence.

The dependency fixture covers one offline pure-Python wheel, not online/native installation. State fixtures cover files between calls, not Python globals, durable stopped disk or checkpointed memory. Artifact bytes passed live host checks but are not retained for independent offline rehashing.

## 4. Measured findings

### Output integrity

| Integration | Observed stdout bytes | Exact-output passed / evaluated | Diagnosis for exercised path |
| :--- | ---: | :--- | :--- |
| AWS Code Interpreter | 131,071 | 0/5 | Final newline absent in every response. |
| Blaxel | 65,602 | 0/5 | Process-log truncation banner in every response. |
| E2B | 131,072 | 5/5 | Byte-exact fixture passed. |
| Google code | 131,072 | 5/5 | Byte-exact fixture passed. |
| Modal | 131,072 | 5/5 | Byte-exact fixture passed. |

Expected: 131,072 bytes. These observations do not establish general file API limits. The adapters' output collection and lossy binary-staging paths require separate investigation. [Exact checks and attempts](findings.md#all-deadlineoutput-observations-and-exact-attempts).

### Workflow candidates

| Integration | Binary transfer | Pipeline + summary | Offline wheel | Shared files / recovery |
| :--- | :--- | :--- | :--- | :--- |
| E2B | 5/5 | 5/5 | 5/5 | Each 5/5 |
| Modal | 5/5 | 5/5 | 5/5 | Each 5/5 |
| Google code | 5/5 | 5/5 | 5/5 | Not established through this one-shot adapter. |

Each cell is a separate operation/setup group. Absent evidence does not imply unsupported product features. [Workflow evidence](findings.md#operations-with-useful-positive-evidence).

### Prime calculation and client wait

| Integration | Guest median, ms | Successful lifecycle median, ms | Passed / evaluated |
| :--- | ---: | ---: | :--- |
| AWS Code Interpreter | 139.6 | 1,358.1 | 5/5 |
| Blaxel | 204.2 | 2,313.7 | 4/5 |
| Databricks SQL | 166.3 | 3,107.0 | 5/5 |
| E2B | 165.1 | 1,454.0 | 5/5 |
| Google code | 393.5 | 6,039.6 | 5/5 |
| Modal | 74.8 | 1,821.3 | 5/5 |

Lifecycle includes initialization, staging, execution, collection and cleanup; final teardown is separate. Differences in architecture, resources, region provenance, caches and interface prevent equal-hardware ranking. These are separate medians, so the difference is not measured median overhead. Blaxel's unsuccessful trial records `ConnectError`. [Timing evidence](findings.md#fast-calculation-is-not-the-same-as-fast-completion).

Readiness lifecycle medians, all 5/5 for these groups, were AWS 1,173.5 ms, E2B 1,267.6 ms, Blaxel 1,422.1 ms, Modal 1,892.9 ms, Databricks SQL 3,135.1 ms and Google 5,808.2 ms. They are not pure provisioning measurements. [Readiness definitions and evidence](findings.md#how-long-does-the-full-integration-take).

### Deadline response

| Integration | Execute response range, seconds | Response-oracle passed / evaluated |
| :--- | :--- | :--- |
| Modal | 4.21 to 4.22 | 5/5 |
| E2B | 8.78 to 10.88 | 4/5 |

Request deadline: 4s; response budget: 9s. Adapter work can contribute to the execute phase. Remote process termination was not independently verified. [Deadline evidence](findings.md#deadline-responses).

### Small worker burst

| Integration | Independent workers | Verified / attempted | Campaign seconds | Verified completions / second |
| :--- | ---: | :--- | ---: | ---: |
| Modal | 3 | 12/12 | 8.41 | 1.43 |
| E2B | 3 | 12/12 | 8.76 | 1.37 |

Campaign rates include warmup time when present. Short bursts do not establish sustained capacity or support a strong conclusion from this small rate difference. [Campaign records](findings.md#what-happens-with-more-workers).

### Uncertainty

Groups require at least five evaluated trials and evaluator/adapter fingerprints. Eligibility does not mean latest version or complete provenance. Samples are separated by configuration, workload, evaluator, adapter, stack, concurrency and client platform.

Five successes out of five have a Wilson 95% lower success bound around 56.6%. Shared infrastructure may correlate trials. Five-sample descriptive p95 is exploratory. This baseline cannot establish SLAs, regional production reliability or tail latency.

## 5. Documented feature trade-offs

| Product | Why investigate it | Limit / untested path |
| :--- | :--- | :--- |
| [Modal](../../providers/modal/SPEC.md) | Custom images, CPU/RAM request/limit controls, volumes, authenticated previews, explicit GPU request | GPU requires gVisor and is preemptible. Advanced image/GPU/resume paths untested. Physical-core units matter. |
| [E2B](../../providers/e2b/SPEC.md) | Templates, binary files, network controls, previews, file/memory pause-resume | CPU-only managed offering. Plan-specific continuous-runtime caps; pause/resume untested. |
| [Blaxel](../../providers/blaxel/SPEC.md) | Standby, persistent volumes, processes, public/private previews | CPU follows RAM; custom image requires sandbox-api. This adapter's output/binary handling needs repair. |
| [Google code/BYOC](../../providers/gcp_vertex/SPEC.md) | Default-code data fixtures; documented broader custom-container path and CMEK | Default API also documents machine configurations, not requested here. No network in default code; effective policies, keys and BYOC untested. |
| [AWS interpreter](../../providers/aws/SPEC.md) | Direct sessions, networking modes, customer-owned mounts | No custom image/caller sizing in reviewed interpreter API. Effective tool networking unrecorded. |
| [Databricks dedicated](../../providers/databricks_sandbox/SPEC.md) | Shell/SSH, fixed 4 vCPU/8 GB, home retained across stop/start | Unrestricted non-configurable egress; custom image conflict unresolved; no working evaluated baseline. |
| [Databricks SQL](../../providers/databricks/SPEC.md) | Python execution through existing warehouse | Stateless; no reusable interpreter/native artifact collector. Separate from dedicated/MCP. |
| [Daytona](../../providers/daytona/SPEC.md) | OCI images, resource sizing, previews and distinct classes | GPU deleted on stop; shared GPU placement ignores geographic preference; no evaluated remote baseline. |
| [Model-owned tools](../../providers/README.md) | Code-assisted model answers with less app orchestration | Current Responses features differ from legacy OpenAI adapter; Gemini needs tool traces and route-specific residency. |
| [Self-operated routes](../../providers/k8s_agent_sandbox/SPEC.md) | Deployment/resource policy under operator control | Fleet capacity, isolation, network, image supply and lifecycle become operational work; deployment attestation absent. |

For Google specifically, default code, custom-container/BYOC, GKE Agent Sandbox and Compute Engine are separate deployment choices. The [default code API](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/sandbox/code-execution-quickstart) documents machine configurations; CPU/RAM choice is not exclusively BYOC. Custom image, GPU, network and storage eligibility need product-specific evidence rather than inheritance from another route.

## 6. EU data residency and regulations

The current pilot was not an EU-only comparison. AWS requested Stockholm, Blaxel requested Oregon, Modal was unpinned, E2B's cluster was unrecorded, Google lacked a retained region preflight and Databricks SQL lacked warehouse location. A separate earlier Milan probe is not campaign placement evidence.

| Product | Documented European route | Data-boundary qualification |
| :--- | :--- | :--- |
| Modal | Strict EEA compute pinning | US stdout/stderr logs, snapshots and managed durable storage; US-east lifecycle control plane. |
| E2B | Belgium shared cluster, Pro+ via support | Wider shared-cloud scope requires confirmation. Enterprise BYOC documents customer-VPC templates/snapshots/logs; vendor management remains. |
| Blaxel | Frankfurt, Mark 3 | Volumes same-region; logs/snapshots/images/control-plane scope unverified. London is not EU. |
| Google | Five named EU regions and eu Code Execution endpoint | Model processing separately configured; single-region parent/CMEK setup differs from multi-region Runtime path. |
| AWS | EU Built-in Tools regions | Endpoint references differ; customer storage and session retention have separate scope. Stop is not deletion attestation. |
| Databricks | Supported EU cloud/workspace regions | Dedicated, SQL and MCP differ. AI Europe Geo includes UK/Switzerland; designated-service processing settings matter. |
| Daytona | Ordinary shared eu target | Shared GPU uses earth and ignores preference; dedicated/custom GPU regions differ. |
| OpenAI | Eligible Europe tool storage/processing | EEA + Switzerland, not strict EU; system data excluded; endpoint/retention eligibility applies. |
| Gemini | Cloud model/endpoint-specific commitments | Developer API access countries do not establish EU-only processing. Benchmark route unrecorded. |

The requirement must identify compute, persistent copies, logs, control-plane data, support access and external/model calls. EU members, EEA and wider Europe are different boundaries.

GDPR does not require blanket EU-only hosting. Article 28 addresses processor arrangements, Article 32 appropriate security, and Articles 44 to 46 qualifying international transfers and safeguards. Third-country remote access can matter while disks remain in the EU; foreign ownership alone does not establish a transfer. EU-only may nevertheless be a stricter contractual or sector-specific requirement.

The [full EU source guide](eu-data-residency.md) retains original provider sources, geographic exceptions, retention scope and [GDPR](https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng)/[EDPB](https://www.edpb.europa.eu/sme-data-protection-guide/international-data-transfers_en) references. No independent effective residency, network/key policy or isolation attestation was collected by this pilot.

## 7. Pricing, credits and value

Published USD list rates reviewed, with original units preserved:

| Product | Published CPU / active resource rate | Published memory rate | Important billing condition |
| :--- | :--- | :--- | :--- |
| Modal | $0.00003942 / physical-core-second | $0.00000667 / GiB-second | Requests/actual usage, burst and region premiums; other charges/plan conditions. |
| E2B | $0.000014 / vCPU-second | $0.0000045 / GiB-second | Provisioned resources while running; plan and pause/storage conditions. |
| Blaxel | $0.0000115 / GB RAM-second, CPU included | Included in active-RAM unit | API 4,096 MB is not independently verified as 4 published GB for billing. Storage can remain in standby. |
| Google | $0.085 / vCPU-hour | $0.009 / GiB-hour | Default paid tier; sandboxes billed while they exist, with account free-tier/plan conditions. |
| AWS Code Interpreter | $0.0895 / consumed vCPU-hour | $0.00945 / GB-hour | Per-second rules/minima, overhead and peak consumed memory; mounts/transfer separate. |
| Daytona | $0.0504 / vCPU-hour | $0.0162 / GiB-hour | Reserved resources by lifecycle state; stopped/paused disk and retained snapshots can remain billable. |

Original scoped sources and conditions are in the linked provider specifications and [dashboard price sheet](../index.html#economics). GB and GiB, physical cores and vCPUs are not interchangeable. These rates cannot be multiplied by client lifecycle timing to manufacture metered bills.

Databricks dedicated usage is currently no-charge Beta with future rates unresolved; the measured SQL warehouse bills separately. Gemini incurs model tokens without a separate execution fee. The reviewed OpenAI 1-GB container unit is $0.03 per 20-minute session per container, subject to its current eligibility/billing conditions, plus model usage. These are different products and pricing units.

```text
gross campaign cost = billed active/reserved compute (including setup/idle)
                    + retained disk/snapshots/images + egress
                    + model tokens/session + control-plane/fleet overhead
                    (all terms include failed attempts and retries)
cost per verified completion = gross campaign cost / verified completions
cash paid = gross usage value - applicable credits/discounts
```

No invoice-backed task-cost ranking or comparable historical price trend was measured. Promotional credits reduce cash paid, not resource consumption. Self-operated comparisons must include idle/warm capacity, maintenance and operator effort.

## 8. Reproduction and next experiments

Run only bounded trusted fixtures on the host subprocess control. Install each chosen provider's SDK and configure credentials outside report/options files.

```bash
# Default baseline; not a rerun of every historical adapter revision
python3 -m src.cli run --backend modal --suite realistic,runtime_inventory --repeats 5
python3 -m src.cli run --backend e2b --suite realistic,runtime_inventory --repeats 5

# Independent-worker burst
python3 -m src.cli run --backend modal --suite cpu_stress --repeats 12 --concurrency 3 --output reports/data/attempts/modal_burst_evaluation.json

# Separate explicitly labelled configuration
python3 -m src.cli run --backend modal --suite realistic,runtime_inventory --repeats 30 --backend-options examples/modal-options.json --config-label pinned-python-1core-2gib

# Refresh evidence views and checks
python3 -m src.cli specs
python3 -m src.cli dashboard
python3 scripts/verify_dashboard.py
python3 scripts/validate_evidence.py
python3 -m unittest discover -s tests -v
```

New runs can change SDK/adapter hashes and therefore form new cohorts. Exact reproduction needs the retained stack/configuration fingerprints. Current source hashing is useful provenance, not a substitute for an immutable checkout/container archive. Google's CLI version and campaign region gaps must be repaired before claiming exact reproduction.

Prioritise a real repository build with pinned dependencies, 1/10/100-MB binary artifacts, stop/resume checks, cancellation plus late-side-effect checks, explicit GPU/device placement, larger concurrency sweeps and metered gross cost. For EU deployments, retain requested/resolved regions, storage/log/access commitments, effective controls and scoped deletion-status evidence.

The methods and fixtures are in [evaluation-framework.md](evaluation-framework.md). Generated exact-attempt links are in [findings.md](findings.md), with raw report files in the dashboard. Broader feature/pricing details live in [provider specifications](../../providers/README.md). The [common JSON export](../data/derived/specifications.json) ties provider, configuration, attempt and observation records together.

## 9. Conditional investigation routes

- **Files, dependencies and repeated CPU calls:** E2B / Modal, using the positive fixture evidence as a starting point.
- **Custom images and GPU:** Modal / Daytona, after checking class, region, capacity and preemption.
- **Standby, volumes and previews:** Blaxel, after repairing this adapter's binary/output path.
- **Cloud-native identity/connectivity:** exact Google / AWS execution products and policies.
- **Databricks-native work:** select SQL, dedicated or MCP before comparing resources and networking.
- **Deployment ownership:** Kubernetes/GKE, OpenSandbox or VMs with attested infrastructure and full fleet economics.

Apply required data boundaries before performance/cost optimisation. Select two eligible deployments, pin their actual configurations, run the same workflow and retain correctness, lifecycle, cancellation/deletion and gross billing evidence. Contributions should include failed attempts and exact checks as well as successful results.
