# Sandbox evaluation framework

## What this evaluation answers

**How well does a particular integration, configuration and workload perform?** The repository tests default/basic integrations, not the maximum potential of a provider. Custom images, GPUs, regional placement, persistent volumes, warm pools, snapshots, networking and autoscaling can materially change results. Each has a separate capability record and a configuration-specific evidence trail.

Use the [interactive dashboard](../index.html), [provider specs](../../providers/README.md), [normalized specifications dataset](../data/derived/specifications.json), and [measured findings](findings.md). Historical `*_live.json` files remain available but lack the current correctness/provenance contract. They are never silently promoted to verified data.

**Reading the evidence:** a recorded evaluator/adapter hash establishes a version boundary, not complete provenance or recency. The eligible-group threshold is at least five evaluated attempts with no unknown/skipped trials and recorded evaluator/adapter hashes. Multiple earlier revisions can qualify; the report does not silently pick a latest baseline. Some contract-hashed GCP attempts omit the execution CLI version and refer to an unretained region preflight. Inspect those gaps before reproducing a setup.

## Common data model and joins

| Entity | Key / relationship | Purpose |
| :--- | :--- | :--- |
| Provider specification | `provider`; `providers/<id>/spec.json` | Deployment, customization level, 13 named feature hypotheses, pricing units and dated sources |
| Requested configuration | `(provider, config_id)`; `provenance.configuration.requested` | Non-credential image/template/resources/network/lifecycle options actually sent by the adapter |
| Integration version | `adapter_sha256`, `stack_sha256` | Separate source changes and client Python/relevant SDK versions |
| Workload | `suite`, `workload_sha256` | Exact code, language, timeout and input-content hashes; all steps included |
| Evaluation contract | `evaluation_contract_sha256` | Validator-source hash, expected metrics/artifacts/statuses; oracle changes cannot pool old decisions |
| Attempt | `run_id`, `campaign_id`, UTC `started_at` | Execution status, host checks, evaluation, phase timings, steps, cleanup/teardown, raw output and warnings |
| Runtime observation | `run_id` → `metrics`; [inventory schema](../../providers/runtime-inventory.schema.json) | Guest-visible CPU, cgroups, memory, disk, packages, architecture, Python, GPU/tool observations |
| Campaign | `reports/data/campaigns/<id>.json` → attempt `campaign_id` | Request concurrency, total wall time and verified completion throughput |
| Summary | Provider + workload + contract + config + adapter + stack + concurrency + client platform | Sample counts, success intervals, latency distributions and evidence links |

[Provider schema](../../providers/spec.schema.json) is stable and feature-oriented. `supported`, `conditional`, `unsupported`, and `unknown` are distinct from `documented`, `measured`, and `unverified`. Unknown prices are `null`, never zero. Vendor features and adapter implementation coverage are different relationships.

Runtime inventory uses the same [script](../../scripts/runtime_inventory.py) in every environment. It does not dump environment variables, credentials, hostnames or network endpoints. Visible CPU counts, `sysconf` memory and cgroups may describe shared host capacity, not the guaranteed allocation. Absence of `nvidia-smi` does not establish that a platform cannot offer GPUs. Image digests, reservations, network policies, encryption and isolation require control-plane evidence.

## Bounded real-work suite

| Suite | Real usage simulated | Independent correctness/evidence check |
| :--- | :--- | :--- |
| `cold_start` | First client call into a fresh adapter | Exact ready marker and runtime version output; lifecycle wall time, not pure provisioning |
| `cpu_stress` | Deterministic prime sieve | 148,933 primes below 2,000,000; workload timing separate from API/lifecycle time |
| `artifact_roundtrip` | Stage arbitrary binary bytes and return transformed output | Exact 26,900-byte input/output and host SHA-256/byte equality; no fallback input |
| `data_pipeline` | Parse 10k CSV transactions, deduplicate, reject invalid record, aggregate integer cents | Host-computed totals/region breakdown plus exact collected `summary.json` bytes |
| `sqlite_analytics` | 20k-row ingestion, index, aggregate query and transaction rollback | Exact row count/query sum and rollback-preserved state |
| `repository_task` | Reproduce a CSV bug, edit source and rerun four tests in subprocesses | Red test must fail; corrected tests must pass; fixture is SWE-style, not full SWE-bench |
| `output_fidelity` | Chatty execution with ordered Unicode output | Exact 131,072 stdout bytes; detects truncation, line loss and whitespace normalization |
| `session_state` | Three separate execution calls sharing files | State changes 40 → 42 across calls; adapters must explicitly expose reusable sessions |
| `error_recovery` | Intentional exception followed by another call | Sentinel written before failure must survive; next call reads it and produces 42 |
| `dependency_install` | Install and use a user dependency | Uploaded deterministic wheel, private `--target`, `--no-index --no-deps`, import and execute; not PyPI/network test |
| `timeout_handling` | Long sleep with 4-second request deadline | Execution-specific timeout response, no completion marker, ≤9s execute-phase response budget; not independent remote-process-death proof |
| `runtime_inventory` | Discover actual runtime characteristics | Versioned structured probe, source/attempt link; observations are not allocations or security attestations |

Environmental probes (`env_security`, `net_isolation`, memory stress and package inventory) are retained as observations. Root UID is not a cross-tenant isolation score. DNS/TLS/HTTP errors are not proof of enforcement. Reaching 2 GiB allocation is a lower-bound observation, not a measured maximum. The old `agent_multiturn` suite is a single-process pipeline; the old `parallel_throughput` is an in-sandbox threaded microbenchmark, not API scale-out.

## Reliability protocol

1. Keep raw execution status separate from evaluation: `pass`, `fail`, `unknown`, `skipped`. An expected exception/timeout can pass; successful transport with wrong/missing output fails.
2. Retain every attempt. Append under a POSIX cross-process lock, with atomic replacement; never merge samples by suite name. Separate adapter/evaluator/stack versions instead of deleting inconvenient runs.
3. Every worker owns its backend. Mutable shared sessions are not used for concurrent requests. Cleanup and teardown are attempted and their failures invalidate passes. Some older adapters swallow lifecycle errors; their cleanup success is not cloud deletion attestation.
4. Model-mediated tools require exact requested code plus successful execution-tool trace; assistant prose alone is not proof. Gemini traces are captured; the current OpenAI adapter still lacks sufficient trace extraction.
5. Report failure categories and prerequisites. Missing credentials or an unavailable workspace API are integration/access failures, not evidence of vendor outage rates.
6. Report Wilson 95% intervals, numerator and denominator. Five successes give a lower bound around **56.6%**, not “100% reliable.” Shared infrastructure/time windows can correlate attempts, so this interval remains exploratory.

For a production availability claim: run at least hundreds/thousands of attempts, multiple times of day/regions/accounts, include retries/rate limits/service faults, and record correlated incident periods. Zero failures in 299 independent trials gives a one-sided 95% upper failure bound of roughly 1%; a five-trial pilot cannot do that.

## Performance protocol

- Controlled repeats, shuffled suite order and a warmup barrier. Warmups use fresh adapters and warm provider caches; they do not establish a reused session. `--warmups` completes before measured attempts.
- Record fresh provision, cached-image launch, reused session and snapshot resume as different configurations. Current `cold_start` includes SDK/client initialization, staging, execution and cleanup; image cache state is uncontrolled.
- Separate end-to-end latency from inner workload CPU/ETL timing. Client location and SDK implementation matter; synchronous adapters can limit achievable client concurrency.
- Show median/min/max/standard deviation and descriptive p95. Use ≥100 measured attempts for useful tail studies; five-sample p95 is exploratory.
- Compare exact workload and evaluator contract within runtime cohorts. Model-generation latency is not compared as raw VM provisioning speed. Hardware/image/network differences remain explicit; current results are basic-integration comparisons, not CPU-normalized platform benchmarks.
- Scale experiments use independent workers and successful client completions divided by campaign wall time. Sweep concurrency 1/3/10/30/100 only after checking quotas; include queueing, throttling, cleanup, error rate and service response metadata. The current 12-request, 3-worker burst is not a capacity ceiling.

## Feature richness without invented scores

Do not add arbitrary “98/100 features” or “99/100 security” ratings. Show the capability matrix with sources and test coverage. Apply hard requirements (e.g. binary artifacts, cross-call disk state, offline dependency installation). A documented GPU feature without a tested GPU configuration remains **documented / untested**. A provider with many features may still be the wrong choice for a constrained task.

The dashboard shortlist requires ≥5 verified trials and all observed passes for each selected workflow, on the same configuration/adapter/stack/concurrency. A shortlist is an exploratory fit signal, not a guarantee. Weighted Markdown scores use only measured median latency and the lower success bound, disclose the formula/weights, and require at least two comparable providers; cost/security/full capability scores are unavailable.

## Pricing and value protocol

Provider price sheets use current official sources retrieved on **2026-10-13**, original units and conditions. Sandbox rates can differ from function/model/agent-hosting rates. Physical cores, vCPUs, GB and GiB are not interchangeable; GPU classes and preemptible/on-demand pricing differ. Databricks Dedicated Sandbox currently documents no-charge Beta; future rates are unverified. Model tools require actual model token and container/session usage.

```
gross task cost = active/reserved compute + initialization/idle billed time
                + storage/snapshots/images + egress + model tokens/session
                + control-plane overhead + retries/failed tasks
cost per verified completion = campaign gross cost / verified completions
cash cost = gross usage value - eligible credits/discounts
```

Saved per-attempt `cost` estimates are **not invoices**. Legacy assumed rates/resources and token guesses are not used in rankings; new model-tool costs stay unknown when actual usage is absent. For self-hosting, include cluster/VM idle capacity, warm pools, drivers/images, maintenance and operator time. Current list-rate snapshots do not prove that prices increased. A historical trend needs comparable dated SKU, region, resource, commitment and unit evidence. Keep credit value separate so hackathon/promotional balances do not disguise unit economics.

## Reproduce and extend

```bash
# Known, bounded local control (not a secure runtime for untrusted code)
python3 -m src.cli run --backend local --suite realistic --repeats 5

# Default managed baseline + guest inventory
python3 -m src.cli run --backend modal --suite realistic,runtime_inventory --repeats 5
python3 -m src.cli run --backend e2b --suite realistic,runtime_inventory --repeats 5

# Small independent-worker burst
python3 -m src.cli run --backend modal --suite cpu_stress --repeats 12 --concurrency 3 --output reports/data/attempts/modal_burst_evaluation.json

# Alternate configuration; options contain no credentials
python3 -m src.cli run --backend modal --suite realistic,runtime_inventory --repeats 30 --backend-options examples/modal-options.json --config-label pinned-python-1core-2gib

# Generate all relationships/report views from the same evidence
python3 -m src.cli specs
python3 -m src.cli leaderboard --suite cold_start --weights latency=0.5,reliability=0.5 --output reports/docs/leaderboard.md
python3 -m src.cli dashboard
python3 -m unittest discover -s tests -v
```

Supported option files: Modal `cpu`, `memory` (scalar request or `[request, limit]`), registry `image`, `python_version`, `gpu`, `runtime`, `region`, `block_network`; E2B `template`, `allow_internet_access`; Blaxel `image`, `memory`, `region`, `ttl`. Configuration changes use a new `config_id`. Public credentials remain outside reports/options. GPU/custom-image options are implemented for future experiments but **not exercised by this published baseline**.

GCP configuration remains the installed CLI's project/runtime/CMEK settings. Use [the versioned client guidance](../../providers/gcp_vertex/client-reference.md#cli-contract), preflight `config show`/`doctor`, and verify `status` after runs. Retain the successful status response, scope and timestamp with the campaign. No such post-run status artifact is retained for this pilot, so the earlier zero-remaining-sandboxes assertion is not independently auditable. Adapter cleanup can mean local cleanup or a no-op; it is not remote deletion attestation.

## Next experiments, explicitly unmeasured

| Experiment | Design / oracle | Required configuration |
| :--- | :--- | :--- |
| GPU compute and economics | Same model/data/precision/seed; device inventory, output tolerance, load/kernel/runtime timing and actual billing | Modal/Daytona documented GPU selection; Blaxel managed GPU eligibility unresolved |
| Image strategy | Cold/cached image build, setup, first response, second call; identical dependency lockfiles | Pinned digest/image/template per provider |
| Snapshot/standby/resume | Persist file and process state, idle, resume, validate after reconnection; bill idle/storage separately | E2B/Blaxel/Modal/Daytona supported lifecycle APIs |
| Real repository build | Pinned small public repo/commit and dependency lockfiles; clean build/test oracle | Network policy or offline source/dependency bundle |
| Large artifact throughput | 1/10/100 MB binary/random fixture; staged/collected host hash, nested paths and measured transfer phases | Native binary transport, payload limits |
| Process cancellation/recovery | Timeout then poll process/sentinel and perform next call; prove no late side effects | Explicit cancel/kill/status endpoint, reusable session |
| Isolation and policy | Controlled allow/deny endpoints, redirects/DNS, cross-session nonce leakage tests | Attested deployment and network policy; authorized probes only |
| GKE/Compute Engine | Same workloads on declared RuntimeClass/node/VM/image, scheduler/claim/pool timings and controller costs | Real cluster/VM provisioning and control-plane evidence; local HTTP server excluded |
| Historical pricing | Archive dated official comparable SKUs and discounts | Same resource/unit/region; no promotional credit equivalence |

The repository makes these experiments extensible; it does not present them as completed work.
