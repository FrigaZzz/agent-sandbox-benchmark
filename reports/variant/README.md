# Sandbox decision guide

Open **[index.html](index.html)** directly in a browser. It is self-contained,
works offline and makes no requests for scripts, fonts or benchmark data.

## Start with the job

1. **Job and requirements:** select concrete operations, optional must-have
   features, interface family, cohort worker count and EU-only data surfaces.
   Workload cards explain the test fixtures and implied requirements. Serving
   and specialised image/GPU work remain explicitly unmeasured.
2. **Candidates:** complete task evidence and documented requirement support
   produce a measured candidate. Conditional/unknown support, failed checks,
   absent cohorts or unresolved residency produce a validation route with a
   next experiment. Unsupported requirements and known residency conflicts
   are set aside. Local/unattested routes require an explicit investigation
   opt-in and never become measured vendor recommendations.
   **Endpoint rerun observations remain visible by default** in a separate
   unranked evidence section, even if the main eligible summary omits them.
   Alibaba's retained earlier and `live-rerun` setups have individual pass/unknown
   counts, timings, sample intervals and attempt links. Showing that evidence
   does not attest a cloud deployment or promote it into the measured ranking.
3. **Compare:** select up to three systems. Inspect their task-specific counts,
   success intervals, timing, failures, assumptions and setup fingerprints.
   The full ledger preserves baseline and burst observations separately.
4. **Cost scenarios:** model job volume, duration, retries, fresh/reused sessions,
   setup/idle time, resource reference, plan fee, retained storage, token usage,
   other quoted charges and credits. Original rate sheets and source links are
   retained. Low/base/high are assumptions, not statistical uncertainty bounds.
5. **Features and residency:** inspect support and evidence separately, including
   qualifications. Residency covers compute, copies, logs, control plane,
   support and downstream calls; no provider is certified EU-only.
6. **Decision summary:** download Markdown containing the selection, scenario,
   sources, setup identities, gaps and proposed validation experiments. Relative
   report links resolve when the file is saved beside this dashboard.

## How ordering works

There is **no composite 0–100 match, capability or evidence-confidence score**.
Missing evidence is never compensated by redistributing weights.

Complete candidates are grouped by the **same set of required task comparison
identities**: suite, workload hash, evaluator-contract hash, runtime kind,
concurrency and client OS/architecture. Provider-specific config, adapter and
stack fingerprints remain visible. Hardware, geography and caches are not
normalised; comparisons are descriptive observations of these integrations.

Within each group, readers can choose:

- **Correctness first:** order by the weakest individual task's 95% Wilson
  lower success bound. Intervals are shown per cohort, never pooled. Ties are
  alphabetical, not evidence of superiority.
- **Task latency first:** order by the geometric mean of relative successful
  p50 ratios for the same required tasks, each anchored to that task's fastest
  candidate in the group. This is an ordering index, not a cross-task average
  in milliseconds. Raw p50/p95 values remain task-specific.
- **Scenario cost first:** order only candidates with a priced scenario and no
  known shape/session eligibility gap. This is a published-rate scenario, not
  an invoice-backed ranking or a cost per verified benchmark completion.

Sensitivity views show alternative orderings inside these groups. Incomplete
systems stay in the validation section. Multiple retained cohorts for one
operation/configuration context are marked ambiguous rather than averaged or
silently selected as latest.

## Cost interpretation

Base planned attempts = `ceil(jobs × attempts per intended job)`.
Session count is that value for fresh sessions, or its ceiling divided by jobs
per session for reuse. Resource-hours include active seconds plus per-session
idle/setup. Low/high vary active duration by the explicit multipliers.

- Modal physical-core rates are converted using the published 2-vCPU
  equivalent; this is not a hardware-performance guarantee.
- AWS and Blaxel decimal-GB memory rates use an explicit GiB → GB conversion.
  AWS consumption fractions are user assumptions. Metering overhead remains
  unverified; exact consumption/minimum rules need a billing trial.
- E2B adds the selected monthly plan; session-runtime limits and shared-EU
  plan eligibility are surfaced.
- OpenAI uses listed 20-minute container blocks, with the final partial reused
  session handled separately, plus the listed gpt-4o token example. This current
  product differs from the failed legacy benchmark integration.
- Gemini uses the listed gemini-2.5-flash token example; runtime resources are
  not caller-sized. Iterative/thinking usage belongs in the token assumptions.
- Dedicated Databricks shows its current no-charge Beta, not a long-term price;
  its fixed shape is not implied to match the reference.
- Retained storage is priced only where an applicable published line is
  available. Otherwise the full total stays unknown and a known subtotal may
  be displayed. GPU, egress and operator costs require separate quoted inputs.

All estimates are scoped partial models. Existing harness cost estimates are
not promoted into measured bills. Published rates are dated at the evidence
snapshot and can become stale.

## Files and regeneration

| File | Purpose |
|---|---|
| `index.html` | Generated standalone dashboard |
| `data.json` | Derived, inspectable dataset with intact cohort identities |
| `build_variant.py` | Reads sibling reports and generates the dataset/page |
| `template.html` | Layout, controls and embedded-data placeholders |
| `app.js` | Readable UI, recommendation, scenario and export logic (inlined at build) |
| `verify.mjs` | Behavioural regression checks using an external jsdom installation |
| `browser_verify.mjs` | Isolated real-Chrome responsive, interaction and download checks |
| `../checks/decision-guide/` | Screenshots, test export and machine-readable browser verification |

```bash
python reports/variant/build_variant.py
# Point to a jsdom entry supplied by your local tooling; no project dependency required.
JSDOM_MODULE=/absolute/path/to/jsdom/lib/api.js node reports/variant/verify.mjs
# Optional: existing Chrome, externally installed Playwright (no project package change).
PLAYWRIGHT_MODULE=/absolute/path/to/playwright node reports/variant/browser_verify.mjs
```

Sources: `../data/derived/evaluation-summary.json`, `../data/derived/specifications.json`, raw evaluation
reports under `../data/attempts/`, provider specifications and `../docs/eu-data-residency.md`. Six-surface
residency notes are conservative curated projections of that guide, not a
new independent attestation.
