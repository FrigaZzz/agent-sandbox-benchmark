# Recommendation coverage and operational handoff

The October 2026 benchmark-guide recommendations have been reconciled with the
repository's retained evidence. Later audience corrections take precedence over
the earlier sample copy. The repository has **12 provider specs**, plus a local
control in the evidence; the supplied sample's “13 provider specs” was inaccurate.

| Recommendation | Implementation / evidence | Status |
|---|---|---|
| Clear three-tier repository funnel and summary matrix | [Root guide](../../readme.md), [report map](../README.md) | Implemented |
| Five operational categories and concrete jobs | [Executive briefing](../executive/index.html), root category table | Implemented |
| Cost/reliability-led plain-language publication copy | Local author drafts revised; 2,536-character social copy, model-agnostic cost scenario, technical appendix | Prepared locally; public destinations pending |
| Consolidated scope and honest workload shortlists | Executive overview and article callout; cohort-specific proof links instead of universal winners | Implemented |
| Explain output completeness and the actual latency workload | [Output figure](../executive/output.svg), [prime/lifecycle figure](../executive/latency.svg) | Implemented |
| Executive infographic attachments | [Ten-page PDF](../executive/agent-sandbox-executive.pdf), six SVG/PNG figures, reviewed contact sheet | Built and browser-verified |
| Update the old model-centered cost illustration | [Nine-page guide](../simplified/agent-sandbox-decisions.pdf) now uses an explicit $0.003 model-budget assumption | Rebuilt and verified |
| Standard provider contract vs tested reality | All twelve `SPEC.md` pages have generated common summaries above preserved dossiers; [generator](../../src/bench/provider_overview.py) | Implemented |
| Six residency surfaces and dated original sources | Per-provider tables, [residency audit](eu-data-residency.md); unresolved surfaces remain explicit | Implemented; no EU/GDPR certification implied |
| Community cohort issue/PR templates | [Cohort issue](../../.github/ISSUE_TEMPLATE/submit_benchmark_cohort.md), [contribution guide](../../CONTRIBUTING.md) | Implemented |
| Campaign budget cap | `--budget-cap-usd`, full-attempt concurrent reservations, warmups/failures included, unknown-price refusal | Tested with controlled backends; not an invoice cap |
| Interruption retention and cleanup | Interrupted attempts and campaign status persisted; bounded cleanup and teardown | Regression-tested; remote cancellation/absence not attested |
| Server-side lifetime controls | Existing GCP/AWS bounds; E2B/Modal 180s defaults; Blaxel reduced to 180s; Daytona TTL + idle stop/delete | Implemented; Dedicated Databricks SDK has no TTL field |
| Orphan reconciliation | [Dry-run reaper](../../scripts/reap_zombies.py), ownership/age checks, recheck before explicit deletion | Mock-tested; old unlabelled resources need manual reconciliation |
| Offline fork CI / protected live dispatch | [Offline CI](../../.github/workflows/ci.yml), [main-only live workflow](../../.github/workflows/live-benchmark.yml) | Configured; environment approvals/branch protection must be enabled on destination |
| Unified GitHub Pages app | Shared five-link portal nav; [Pages staging](../../scripts/stage_pages.py) preserves source/provider links | Configured; hosting not deployed |
| Remove unsupported comparative scores in chart studio | Canonical normalization, cohort-specific charts, no fabricated radar/burst/price winners; escaped raw logs and mobile layout fixes | All tabs and four viewport widths browser-verified |
| Standardized container client | [Runner Dockerfile](../../Dockerfile.runner), [Compose](../../compose.yaml), credential-free build context | Compose config validated; image build not run because local daemon is unavailable |
| Date-sharded evidence without breaking old citations | New default `data/attempts/YYYY-MM/`; recursive ingestion; shared campaign root | Regression-tested; historical records unchanged |
| Keep fixture binaries out of ordinary Git history | Existing deterministic binary/wheel generators retained | Already satisfied; Git LFS unnecessary for these generated fixtures |
| Frozen publication bundles | [Snapshot tool](../../scripts/freeze_snapshot.py): deterministic archive metadata, file hashes, membership/tamper check, no overwrite | Implemented and tested |
| Immutable Git-tag/release destinations | Documented snapshot/release procedure | Actual tag/release awaits explicit Git/publication request |
| Pre-commit publication/evidence checks | [Hook configuration](../../.pre-commit-config.yaml); expanded attempt schema/hash checks | Configured; install hooks locally when desired |

## Claims deliberately corrected

- A missing stdout newline does not establish a binary-file API failure or a measured
  Git-patch/build failure. Truncated process logs are a different observed defect.
- Google's measured one-shot adapter is not proof the product is stateless.
- Modal had the smallest guest prime median; AWS had the smallest recorded full
  lifecycle median. These unequal-hardware pilots do not establish a speed winner.
- The cost scenario does not claim that all 2026 models cost pennies or that every
  agent's machine bill is 5–10 times its model bill. With a $0.003 assumption, the
  300-second example is **4.6 times**; the 180-second example is **2.76 times**.
- “EU region,” BYOC and encryption do not locate all data or establish GDPR compliance.
- Base64 is a reversible binary encoding. Lossy UTF-8 decoding is the problem; the
  guide's blanket prohibition on base64 was not adopted.
- An arbitrary universal 60–120-second TTL is unsuitable for many workloads. Bounded,
  explicitly configured lifetimes and separate cancellation verification are used.
- Live workflows upload reviewed candidate artifacts, including failed attempts,
  rather than automatically committing account-funded results.

## Verification record

- Final unit/integration suite: **44 tests passed**, including regressions
  for concurrent budget reservations, interrupted evidence, zero-admission reports,
  reaper refusal/rechecks, snapshot tampering and provider-dossier preservation.
- Schema/link validation: 12 provider specs, 56 inventories, 555 contract-hashed
  attempts, 1,176 local links, no issues.
- Headless browser checks passed for the executive deck, detailed deck, decision
  filter and all chart-studio tabs. Four viewport widths and malicious stdout
  rendered as text were checked; no page exceptions or external requests in portal
  tests. PDF exports have 10, 23 and 9 pages respectively.
- Automation YAML and Compose configuration parse. Python wheel build and Pages
  staging succeeded. Docker image execution requires an available Docker daemon.
- Publication scans passed; public article/repository destination slots remain
  unresolved. Recheck draft length after replacing URLs.
