## Change and evidence
Describe the exact execution surface, configuration and recommendation addressed.
Link the raw cohort and report sources; retain failed attempts.

## Verification
- [ ] Offline tests and evidence/schema/link checks passed.
- [ ] Publication scan passed; no credentials or confidential logs included.
- [ ] Documented capabilities and measured behavior are separate.
- [ ] Any live run used an explicit budget, bounded lifetime and verified cleanup.
- [ ] New comparisons keep workload/contract/adapter/stack/configuration identities separate.

For new measurements, provide the provenance fields in the benchmark cohort issue
template. CI on this PR does not run authenticated cloud workloads.
