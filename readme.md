# AI agent sandbox benchmark and field guide

An evidence-first comparison of **code-execution integrations**, their tested configurations, and the broader customization their providers document.

The benchmark runs real code with independent correctness checks. It retains failures, prerequisites, repeated samples, timestamps, workload/evaluator/adapter fingerprints, SDK versions, requested settings and guest runtime inventories. Default integrations are the baseline; custom images, GPU configurations and advanced deployment strategies are documented separately.

## Start here: choose your depth

| Depth | What you get | Start here |
|---|---|---|
| **1 · Five-minute overview** | Practical jobs, provider categories and a workflow shortlist | [Executive infographic briefing](reports/executive/index.html) · [Nine-page decision PDF](reports/simplified/agent-sandbox-decisions.pdf) |
| **2 · Interactive exploration** | Exact attempts, visual plots, or hard-requirement filtering | [Raw evidence explorer](reports/index.html) · [Chart studio](reports/ui/index.html) · [Architecture decision filter](reports/variant/index.html) |
| **3 · Technical reference** | Methods, product contracts, pricing units and six-surface residency audit | [Technical report](reports/docs/detailed-report.md) · [EU residency](reports/docs/eu-data-residency.md) · [Evaluation framework](reports/docs/evaluation-framework.md) · [Provider specs](providers/README.md) |

**13 October 2026 retained snapshot:** 975 attempts across different tasks/configurations,
12 provider specifications plus a local control. Five-trial cohorts are pilots;
5/5 is not a production SLA. API success and independently verified task completion
are separate outcomes. Pricing is documented list usage, not invoiced campaign cost.

### What passed the practical fixtures?

| Tested integration | Exact stdout (128 KiB) | Binary round trip (26.9 KB) | CSV pipeline (10k rows) | Offline wheel | Files across calls / recovery |
|---|---|---|---|---|---|
| E2B | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 on each |
| Modal | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 on each |
| Google default code | 5/5 | 5/5 | 5/5 | 5/5¹ | Not exercised by one-shot adapter |
| AWS AgentCore | 0/5: final newline omitted | Inspect exact cohorts | Inspect exact cohorts | Inspect exact cohorts | Inspect exact cohorts |
| Blaxel | 0/5: process logs truncated | Adapter path needs retesting | Inspect exact cohorts | Inspect exact cohorts | Inspect exact cohorts |

¹ One uploaded pure-Python wheel installed in a private target; broader custom-library
support is restricted in the default-code documentation. These are specific adapter
cohorts, not provider-wide ceilings. [Exact cohorts and checks](reports/docs/findings.md).
Untested coverage is not a failure; stdout fidelity does not describe a native binary API.

### Deeper reading

- **[Short decision guide and nine-page PDF](reports/simplified/README.md)** — workload scope, persistence, image/hardware choices, data geography, cancellation and cost per verified completion. [Report map](reports/README.md) provides the deeper reading paths.
- **[Consolidated technical report](reports/docs/detailed-report.md)** — configurations, measured findings, documented trade-offs and remaining gaps in one narrative.
- **[Interactive evidence dashboard](reports/index.html)** — start with measured defects and workflow candidates, then follow each finding to exact attempts, checks and logs. Includes task comparisons, setup options, price sheets and presentation mode.
- **[Measured findings](reports/docs/findings.md)** — what to reproduce before choosing, operations with positive evidence, lifecycle versus calculation time, and provenance gaps. Conclusions are generated from the retained data.
- **[Methodology and experiment recipes](reports/docs/evaluation-framework.md)** — reliability, performance, feature coverage and pricing/value protocol.
- **[Provider specifications](providers/README.md)** — common capability schema and per-provider tested configurations.
- **[Readiness workload leaderboard](reports/docs/leaderboard.md)** — measured dimensions only; no fabricated security/feature scores.
- **[Common data export](reports/data/derived/specifications.json)** — provider → configuration → attempt → runtime observation relationships.

HTML files run locally in a browser. Serve the repository to preserve relative links:

```bash
python3 -m http.server 8000
# Visit http://localhost:8000/reports/index.html
```

The shared portal navigation connects the tools. The [Pages workflow](.github/workflows/pages.yml)
stages the report app with its linked provider/source folders; [index.html](index.html)
opens the dashboard. Enable Pages via Actions in the destination repository.

## Run and extend

The runtime requires Python ≥3.10. The full development/test setup below requires Python ≥3.11 because the Kubernetes SDK has that minimum. Install the SDK/CLI for the chosen provider and configure its credentials separately. Current adapters use Modal, E2B, Blaxel, boto3, Databricks SDK, Google GenAI, Daytona SDK and the installed GCP `agent-sandbox` CLI. The local subprocess is a control, **not an isolation boundary for untrusted code**.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e '.[dev]'

# Bounded local workflow pilot; preserves all attempts
python3 -m src.cli run --backend local --suite realistic --repeats 5

# Default remote integration plus runtime inventory
python3 -m src.cli run --backend modal --suite realistic,runtime_inventory --repeats 5

# Conservative campaign admission guard (not an invoice cap)
python3 -m src.cli run --backend e2b --suite realistic --repeats 5 --budget-cap-usd 1

# Independent worker concurrency (distinct from threads inside one runtime)
python3 -m src.cli run --backend e2b --suite cpu_stress --repeats 12 --concurrency 3 --output reports/data/attempts/e2b_burst_evaluation.json

# Explicit customization; example is not a previously tested configuration
python3 -m src.cli run --backend modal --suite realistic,runtime_inventory --repeats 30 --backend-options examples/modal-options.json --config-label pinned-python-1core-2gib

python3 -m src.cli specs
python3 -m src.cli leaderboard --suite cold_start --weights latency=0.5,reliability=0.5 --output reports/docs/leaderboard.md
python3 -m src.cli dashboard
python3 -m unittest discover -s tests -v
```

`--suite realistic` covers readiness, deterministic compute, binary artifacts, 10k-row ETL, 20k-row SQLite, a repository edit/test loop, exact Unicode stdout, cross-call state, error recovery, offline dependency installation and deadline response. `runtime_inventory` adds CPU/cgroup/memory/packages/tools/GPU observations. `all` also includes legacy stress/network/environment probes. `--warmups` runs an excluded wave before measurement; `--concurrency` creates independent backend instances. POSIX locking protects repeated report appends.

## Provider scope

| Operational category | Example job | Integrations / documented options |
| :--- | :--- | :--- |
| Model-native tools | A chart/calculation inside a model turn | Gemini and OpenAI; exact tool traces required, separate latency cohort |
| Database / SQL execution | Transform data through a warehouse query | Databricks `system.ai.python_exec`; distinct from newer workspace APIs |
| Programmable workspace APIs | Edit files, run tests, return to a session | Modal, E2B, Blaxel, Daytona; dedicated Databricks workspace is a separate product |
| Enterprise cloud interpreters | Bounded file/data jobs with cloud identity | Google default code, AWS AgentCore Code Interpreter; not their BYOC runtime products |
| Self-operated infrastructure | Run an owned fleet with deployment control | Kubernetes-SIGs/GKE, OpenSandbox; VMs documented separately, deployment not attested here |

Alibaba has a registered OpenSandbox/AgentRun adapter and retained endpoint attempts. Both the Alibaba and Kubernetes adapters can auto-spawn a **host HTTP subprocess executor**; that is not a verified remote cloud, Kubernetes, gVisor or microVM deployment. Dedicated Databricks access, Daytona/OpenAI credentials and other prerequisites can prevent a fresh run; the reports expose those gaps.

## Interpretation

- A successful API call is not correctness. Required outputs and collected artifact bytes must match host oracles.
- Five successes are a pilot, not a 100% reliability claim. Sample counts/Wilson intervals remain visible.
- Current “cold start” is client lifecycle latency, including cleanup—not pure provider provisioning.
- Guest-visible CPU/memory are observations, not guaranteed allocation. No GPU deployment was benchmarked.
- Current official prices retain exact units and conditions. Saved cost estimates are not bills; no unsupported historical price-increase claim is made.
- Provider features, documented capabilities, adapter implementation and verified workload coverage remain separate.

## Structure

```text
providers/                 SPEC.md, spec.json, generated tested-configurations
src/core/                  backend protocol, models and provider adapters
src/bench/suites/           deterministic workload fixtures
src/bench/                 runner, campaigns, validation, shared statistics/reporting
reports/                   dashboards, docs/, data/, downloads/ and checks/
scripts/runtime_inventory.py   shared guest probe (no secrets/environment dump)
examples/                  non-credential customization option files
tests/                     oracle, evidence, lifecycle and integration regressions
sandbox-results/           retained synthetic workload output files
BENCHMARK_LOCATIONS.md     portable map of adapters, suites and results
```

The Google ADK bridge remains available in `src/core/adk_bridge.py`; use `get_backend(...)` and `create_adk_tool(...)` for the existing integration surface. Verify adapter support for the capabilities your agent needs.

## Rebuild and validate

```bash
python3 -m src.cli specs
python3 -m src.cli dashboard
python3 reports/variant/build_variant.py
python3 reports/ui/build_ui.py
python3 reports/executive/build_deck.py
python3 scripts/validate_evidence.py
python3 scripts/check_publication.py
```

Install only the provider extras you need, for example `python3 -m pip install -e '.[modal]'`.
AWS, Daytona and the optional self-hosted HTTP executors have extras named `aws`, `daytona` and `servers`.
Configure credentials through provider environment variables or SDK credential stores. AWS requires
`AWS_BEDROCK_AGENTCORE_TOOL_ID`; Gemini requires `GEMINI_API_KEY` or `GOOGLE_CLOUD_PROJECT`.
The GCP adapter additionally needs the external `agent-sandbox` CLI; its versioned contract and
setup notes are in [client-reference.md](providers/gcp_vertex/client-reference.md).
The [publication/data notes](reports/docs/data-notes.md) describe the retained datasets and privacy redactions.

## Contribute and operate bounded campaigns

See [CONTRIBUTING.md](CONTRIBUTING.md) for cohort provenance, estimated budgets,
server TTLs, dry-run orphan reconciliation, protected live CI, containerized clients,
pre-commit hooks and immutable content-hashed publication bundles. New default
attempt outputs use `reports/data/attempts/YYYY-MM/`; historical paths remain stable.
`Dockerfile.runner` and `compose.yaml` standardize the client Python/OS family while
retaining SDK versions and network/platform differences in provenance.

[Recommendation coverage and operational handoff](reports/docs/recommendation-coverage.md)
records the implemented guide suggestions and the remaining destination/SDK constraints.
