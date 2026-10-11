# Daytona — tested configurations

Generated from real attempt records. [Documented capabilities](SPEC.md) describe broader options; the tested integration is narrower.

Requested settings, client versions, observation timestamps and raw evidence are retained in [tested-configurations.json](tested-configurations.json). No GPU-enabled or custom-image configuration was tested in these default campaigns.

## Configuration `5bd019963a19` / adapter `3973cef255b4` / concurrency 1

Runtime classification: **remote_runtime**. Request recording complete: **True**.

```json
{
  "label": "live-rerun",
  "requested": {
    "product": "Daytona",
    "image": "client.create defaults",
    "cpu": null,
    "memory": null,
    "gpu": null
  }
}
```

Client execution stack: `{"python": "3.13.13", "sdk": "daytona-sdk", "version": "0.224.0"}`.

Suites: `artifact_roundtrip`, `cold_start`, `cpu_stress`, `data_pipeline`, `dependency_install`, `error_recovery`, `output_fidelity`, `repository_task`, `runtime_inventory`, `session_state`, `sqlite_analytics`, `timeout_handling`

Raw reports: [data/attempts/daytona_evaluation.json](../../reports/data/attempts/daytona_evaluation.json)

### Observation `bench-955a555db315` — 2026-10-13T16:46:55.833210+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "x86_64", "implementation": "CPython", "kernel": "6.17.0-1011-oracle", "os": "Linux", "python": "3.14.4"}` |
| CPU | `{"affinity_count": 48, "model": "AMD EPYC 9J45 128-Core Processor", "visible_logical_cpus": 48}` |
| Memory | `{"sysconf_physical_bytes": 202591866880}` |
| cgroup limits | `{"cpu_max": "100000 100000", "cpu_period_v1": null, "cpu_quota_v1": null, "cpuset_effective": "0-47", "memory_limit_v1": null, "memory_max": "1073741824"}` |
| GPU probe | `{"devices": [], "probe": "nvidia-smi_unavailable"}` |


Recorded requests and guest-visible observations are distinct; guest observations are not reserved-resource, image, GPU-eligibility or isolation attestation. Early attempts without requested settings remain incomplete.

## Configuration `39ed10c5d0c2` / adapter `fd48ea4b8575` / concurrency 1

Runtime classification: **remote_runtime**. Request recording complete: **False**.

```json
{
  "label": "adapter-defaults"
}
```

Client execution stack: `null`.

Suites: `runtime_inventory`

Raw reports: [data/attempts/daytona_evaluation.json](../../reports/data/attempts/daytona_evaluation.json)

No successful runtime inventory for this exact recorded configuration/adapter/stack. See raw checks and prerequisite failures.

Recorded requests and guest-visible observations are distinct; guest observations are not reserved-resource, image, GPU-eligibility or isolation attestation. Early attempts without requested settings remain incomplete.
