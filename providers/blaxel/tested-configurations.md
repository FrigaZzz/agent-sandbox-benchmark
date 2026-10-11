# Blaxel — tested configurations

Generated from real attempt records. [Documented capabilities](SPEC.md) describe broader options; the tested integration is narrower.

Requested settings, client versions, observation timestamps and raw evidence are retained in [tested-configurations.json](tested-configurations.json). No GPU-enabled or custom-image configuration was tested in these default campaigns.

## Configuration `98d5f84fa22b` / adapter `f1238f8bfe20` / concurrency 1

Runtime classification: **remote_runtime**. Request recording complete: **True**.

```json
{
  "label": "live-rerun",
  "requested": {
    "image": "blaxel/py-app:latest",
    "memory": 4096,
    "memory_unit": "MB API field",
    "cpu": "memory-coupled",
    "region": "us-pdx-1",
    "ttl": "1h",
    "gpu": null,
    "network_policy": "default; no restriction requested"
  }
}
```

Client execution stack: `{"python": "3.13.13", "sdk": "blaxel", "version": "0.4.13"}`.

Suites: `artifact_roundtrip`, `cold_start`, `cpu_stress`, `data_pipeline`, `dependency_install`, `error_recovery`, `output_fidelity`, `repository_task`, `session_state`, `sqlite_analytics`, `timeout_handling`

Raw reports: [data/attempts/blaxel_evaluation.json](../../reports/data/attempts/blaxel_evaluation.json)

No successful runtime inventory for this exact recorded configuration/adapter/stack. See raw checks and prerequisite failures.

Recorded requests and guest-visible observations are distinct; guest observations are not reserved-resource, image, GPU-eligibility or isolation attestation. Early attempts without requested settings remain incomplete.

## Configuration `ed833ceba657` / adapter `f1238f8bfe20` / concurrency 1

Runtime classification: **remote_runtime**. Request recording complete: **True**.

```json
{
  "label": "adapter-defaults",
  "requested": {
    "image": "blaxel/py-app:latest",
    "memory": 4096,
    "memory_unit": "MB API field",
    "cpu": "memory-coupled",
    "region": "us-pdx-1",
    "ttl": "1h",
    "gpu": null,
    "network_policy": "default; no restriction requested"
  }
}
```

Client execution stack: `{"python": "3.13.13", "sdk": "blaxel", "version": "0.4.13"}`.

Suites: `cold_start`, `cpu_stress`, `output_fidelity`, `repository_task`, `runtime_inventory`, `sqlite_analytics`

Raw reports: [data/attempts/blaxel_evaluation.json](../../reports/data/attempts/blaxel_evaluation.json)

### Observation `bench-de95f5fad206` — 2026-10-13T07:36:47.014453+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "x86_64", "implementation": "CPython", "kernel": "6.12.75+", "os": "Linux", "python": "3.12.15"}` |
| CPU | `{"affinity_count": 2, "model": "Intel(R) Xeon(R) Processor @ 2.90GHz", "visible_logical_cpus": 2}` |
| Memory | `{"sysconf_physical_bytes": 4123979776}` |
| cgroup limits | `{"cpu_max": null, "cpu_period_v1": null, "cpu_quota_v1": null, "cpuset_effective": null, "memory_limit_v1": null, "memory_max": null}` |
| GPU probe | `{"devices": [], "probe": "nvidia-smi_unavailable"}` |

### Observation `bench-d3ac667557ac` — 2026-10-13T07:36:53.262734+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "x86_64", "implementation": "CPython", "kernel": "6.12.75+", "os": "Linux", "python": "3.12.15"}` |
| CPU | `{"affinity_count": 2, "model": "Intel(R) Xeon(R) Processor @ 2.90GHz", "visible_logical_cpus": 2}` |
| Memory | `{"sysconf_physical_bytes": 4123979776}` |
| cgroup limits | `{"cpu_max": null, "cpu_period_v1": null, "cpu_quota_v1": null, "cpuset_effective": null, "memory_limit_v1": null, "memory_max": null}` |
| GPU probe | `{"devices": [], "probe": "nvidia-smi_unavailable"}` |

### Observation `bench-399189f1c914` — 2026-10-13T07:37:02.716113+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "x86_64", "implementation": "CPython", "kernel": "6.12.75+", "os": "Linux", "python": "3.12.15"}` |
| CPU | `{"affinity_count": 2, "model": "Intel(R) Xeon(R) Processor @ 2.90GHz", "visible_logical_cpus": 2}` |
| Memory | `{"sysconf_physical_bytes": 4123979776}` |
| cgroup limits | `{"cpu_max": null, "cpu_period_v1": null, "cpu_quota_v1": null, "cpuset_effective": null, "memory_limit_v1": null, "memory_max": null}` |
| GPU probe | `{"devices": [], "probe": "nvidia-smi_unavailable"}` |

### Observation `bench-ce7d71d07a22` — 2026-10-13T07:37:17.241142+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "x86_64", "implementation": "CPython", "kernel": "6.12.75+", "os": "Linux", "python": "3.12.15"}` |
| CPU | `{"affinity_count": 2, "model": "Intel(R) Xeon(R) Processor @ 2.90GHz", "visible_logical_cpus": 2}` |
| Memory | `{"sysconf_physical_bytes": 4123979776}` |
| cgroup limits | `{"cpu_max": null, "cpu_period_v1": null, "cpu_quota_v1": null, "cpuset_effective": null, "memory_limit_v1": null, "memory_max": null}` |
| GPU probe | `{"devices": [], "probe": "nvidia-smi_unavailable"}` |

### Observation `bench-565167211b04` — 2026-10-13T07:37:28.842412+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "x86_64", "implementation": "CPython", "kernel": "6.12.75+", "os": "Linux", "python": "3.12.15"}` |
| CPU | `{"affinity_count": 2, "model": "Intel(R) Xeon(R) Processor @ 2.90GHz", "visible_logical_cpus": 2}` |
| Memory | `{"sysconf_physical_bytes": 4123979776}` |
| cgroup limits | `{"cpu_max": null, "cpu_period_v1": null, "cpu_quota_v1": null, "cpuset_effective": null, "memory_limit_v1": null, "memory_max": null}` |
| GPU probe | `{"devices": [], "probe": "nvidia-smi_unavailable"}` |


Recorded requests and guest-visible observations are distinct; guest observations are not reserved-resource, image, GPU-eligibility or isolation attestation. Early attempts without requested settings remain incomplete.

## Configuration `39ed10c5d0c2` / adapter `39db71c37648` / concurrency 1

Runtime classification: **remote_runtime**. Request recording complete: **False**.

```json
{
  "label": "adapter-defaults"
}
```

Client execution stack: `null`.

Suites: `cold_start`, `cpu_stress`, `output_fidelity`, `repository_task`, `runtime_inventory`, `sqlite_analytics`

Raw reports: [data/attempts/blaxel_evaluation.json](../../reports/data/attempts/blaxel_evaluation.json)

### Observation `bench-6f8c3ee8ee03` — 2026-10-13T07:13:22.552337+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "x86_64", "implementation": "CPython", "kernel": "6.12.75+", "os": "Linux", "python": "3.12.15"}` |
| CPU | `{"affinity_count": 2, "model": "Intel(R) Xeon(R) Processor @ 2.90GHz", "visible_logical_cpus": 2}` |
| Memory | `{"sysconf_physical_bytes": 4123979776}` |
| cgroup limits | `{"cpu_max": null, "cpu_period_v1": null, "cpu_quota_v1": null, "cpuset_effective": null, "memory_limit_v1": null, "memory_max": null}` |
| GPU probe | `{"devices": [], "probe": "nvidia-smi_unavailable"}` |


Recorded requests and guest-visible observations are distinct; guest observations are not reserved-resource, image, GPU-eligibility or isolation attestation. Early attempts without requested settings remain incomplete.
