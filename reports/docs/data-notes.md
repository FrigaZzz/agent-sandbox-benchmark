# Published benchmark data

## Included outputs

- `../data/attempts/*_evaluation.json`: retained per-attempt records, including failed prerequisites,
  checks, stdout/stderr, timings, costs, provenance and available inventories.
- `../data/legacy/`: historical `*_live.json` and `local_baseline.json` observations with the original
  evidence limitations; an old success flag is not an independent correctness check.
- `../data/campaigns/`: retained campaign-level concurrency and throughput records.
- `../data/derived/specifications.json`, `../data/derived/evaluation-summary.json` and provider
  `tested-configurations.*`: derived specification, configuration and observation datasets.
- HTML dashboards, Markdown findings/leaderboard, the presentation PDF and ZIP
  companion, and browser-verification outputs.
- `../../sandbox-results/`: synthetic transaction/state files and binary/text I/O
  artifacts retained from exploratory workloads. These loose files do not by
  themselves identify a provider or prove a benchmark outcome; use the reports'
  run IDs, checks and artifact metadata for comparisons.

## Privacy redactions

Before publication, a personal home-directory prefix in `PIP_STATUS` was replaced
with `<LOCAL_HOME>` in `local_baseline.json`, `local_evaluation.json` and
`alibaba_evaluation.json`. The affected evaluation run IDs are `bench-9c4ff7c3b084`
and `bench-803caecd3a2a`. The replacement appears in stdout, parsed metrics and
the corresponding step stdout. Package and Python versions remain visible.

These are sanitized logs, not byte-identical originals. Attempt counts, run IDs,
timestamps, outcomes, checks, timings, cost estimates and recorded workload,
evaluator, adapter and artifact hashes were preserved. Historical adapter hashes
describe the code at execution time and need not match the cleaned current adapters.
Derived dashboards and the ZIP companion are rebuilt from the sanitized data.

Private cloud configuration notes, external research checkouts, personal publication
drafts, credentials, caches and build directories are excluded through `.gitignore`.
Portable provider/client guidance is included under `providers/`.

## Reproduction

Install and run from the repository root using the commands in [readme.md](../../readme.md).
New runs append observations; use a separate `--output` path when reproducing a
published snapshot. Runtime images, provider APIs and price sheets can change.
The [methodology](evaluation-framework.md) explains comparison identities and
remaining gaps. Run `python3 scripts/check_publication.py` before distributing
new logs; it reports detected locations without printing credential values.
