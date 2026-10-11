# Contributing evidence

Start with the [cohort issue template](.github/ISSUE_TEMPLATE/submit_benchmark_cohort.md).
Keep the exact product, configuration, versions and requested/resolved placement
with every campaign. Retain failed attempts and unknown/skipped outcomes. A cohort
needs at least five evaluated attempts to enter the pilot comparison; that is not
a production reliability claim.

## Local verification

```sh
python3 -m pip install -e '.[dev]'
python3 -m unittest discover -s tests -v
python3 scripts/validate_evidence.py
python3 scripts/check_publication.py
```

Optional hooks: install `pre-commit`, then `pre-commit install`. The local hooks
run the same schema/link and publication checks. Checks detect common problems;
they do not prove that all possible secrets or confidential data have been removed.

Fixtures are generated deterministically by the suite code, including the binary
round trip and pure-Python wheel. Keep large private datasets outside Git. New raw
outputs are sharded under `reports/data/attempts/YYYY-MM/`; old paths stay stable.

## Bounded live work

```sh
python3 -m src.cli run --backend e2b --suite realistic,runtime_inventory \
  --repeats 5 --config-label my-explicit-setup --budget-cap-usd 1
# Dry-run: only benchmark-labelled E2B resources older than 15 minutes
python3 scripts/reap_zombies.py --provider e2b
```

The budget reserves a conservative estimated full attempt before initialization,
counts warmups/failures, and never refunds a reservation. Modal scalar resource
requests, custom E2B templates and unpriceable integrations require an explicit
`--budget-attempt-estimate-usd` allowance. Storage, model usage, retries and uncertain
remote lifetimes must fit that allowance. This is not a provider invoice cap.
Independent campaigns have independent ledgers. Cap exhaustion is recorded in the
campaign summary; it does not turn unlaunched jobs into benchmark failures.

Supported remote workspace adapters set bounded lifetimes: Modal/E2B default 180s
(configurable 1–900s), Blaxel default 180s (max 900s), Daytona 15-minute TTL with
5-minute idle stop and deletion on stop, AWS sessions 60–900s, and GCP's existing CLI
TTL at most 900s. Databricks Dedicated's installed `SandboxSpec` exposes no maximum
lifetime: explicit deletion and independent status reconciliation remain required.
Model-owned tools and operator-managed endpoints have separate lifecycle contracts.

The reaper supports E2B/Modal/Blaxel and refuses missing ownership/age evidence.
`--execute` requests termination after rechecking candidates. Modal uses the creation
tag because its list API does not expose creation time. Old unlabelled resources
require manual reconciliation; a successful termination response is not independent
deletion attestation. An operator can schedule the dry-run/execute command with
least-privilege credentials; no account-wide automatic cleanup is configured.

## Automation and containers

PR CI uses unit/mocked tests and a bounded host-control fixture with no cloud secrets.
Live CI is maintainer dispatch on `main`; configure the `benchmark` environment with
required reviewers and a branch restriction, and use dedicated low-limit accounts.
It uploads scanned candidate results for review rather than auto-committing them.
Set branch protection to require the offline job. Pages needs GitHub Pages configured
for Actions and the `github-pages` environment enabled. Its staging keeps `reports/`
alongside linked provider/source folders; the root entry opens the evidence explorer.

```sh
docker compose build
docker compose run --rm bench
BENCH_EXTRAS=dev,e2b docker compose build
docker compose run --rm bench run --backend e2b --suite cold_start --budget-cap-usd 1
```

Compose optionally reads ignored `.env` credentials at runtime; they never enter the
image. It mounts all `reports/data` so campaign records survive too. The image fixes
the Python/OS family, not network location or exact package resolution. Capture SDK
versions in provenance; pin the base digest/dependency set for release-grade repeats.
External CLIs such as GCP `agent-sandbox` need separate installation/configuration.

## Frozen publication snapshots

```sh
python3 scripts/freeze_snapshot.py --output snapshots/2026-10-field-guide.zip
python3 scripts/freeze_snapshot.py --verify snapshots/2026-10-field-guide.zip
```

The bundle records source revision, dirty-worktree status, file membership and byte
hashes, preserves raw cohorts, uses deterministic ZIP metadata, scans text inputs,
and refuses overwriting an existing snapshot. Publish a reviewed bundle/release and
link the article to that immutable destination. Creating Git tags, releases or public
links is a separate explicit operation. A manifest hash proves byte integrity, not
that documented vendor capabilities or benchmark conclusions are correct.
