---
name: Submit verified benchmark cohort
about: Submit raw attempts, exact configuration and independent checks.
title: "[Cohort] <provider> — <configuration> (<date>)"
labels: benchmark-evidence
---

## Provenance
- Provider and exact product/API:
- Configuration label and requested region/endpoint:
- Resolved placement evidence (or explicitly unrecorded):
- Client OS / architecture / Python; SDK/CLI versions:
- Image digest, CPU/RAM limits, network policy, storage mounts:
- Workload, evaluator-contract and adapter identities:

## Command and cohort
```sh
python3 -m src.cli run --backend <provider> --suite realistic,runtime_inventory --repeats 5 --config-label <label> --budget-cap-usd <cap> --budget-attempt-estimate-usd <conservative-allowance>
```

- [ ] Retained all failures, connection errors, timeouts and warmups.
- [ ] At least five evaluated attempts per comparison group, or marked exploratory.
- [ ] Ran `python3 scripts/validate_evidence.py` and `python3 scripts/check_publication.py`.
- [ ] Removed credentials, personal paths and confidential payloads; original hashes are not silently altered.
- [ ] Verified remote cleanup through provider status and attached the evidence.
- [ ] Distinguished estimated costs, actual bills, credits and discounts.

## Observations
What returned incorrectly? Did stdout truncate, binary transport change bytes,
or cancellation leave late side effects? Separate adapter behavior from vendor
capability. Include raw JSON, campaign summary and configuration evidence.
