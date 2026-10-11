# Modal — tested configurations

Generated from real attempt records. [Documented capabilities](SPEC.md) describe broader options; the tested integration is narrower.

Requested settings, client versions, observation timestamps and raw evidence are retained in [tested-configurations.json](tested-configurations.json). No GPU-enabled or custom-image configuration was tested in these default campaigns.

## Configuration `e8ca7ef579ec` / adapter `71538074cc69` / concurrency 1

Runtime classification: **remote_runtime**. Request recording complete: **True**.

```json
{
  "label": "live-rerun",
  "requested": {
    "cpu": 2,
    "cpu_unit": "physical-core request",
    "memory": 2048,
    "memory_unit": "MiB request",
    "image": "debian_slim",
    "python_version": null,
    "gpu": null,
    "runtime": null,
    "region": null,
    "block_network": false,
    "session_ttl_seconds": 180
  }
}
```

Client execution stack: `{"python": "3.13.13", "sdk": "modal", "version": "1.6.1"}`.

Suites: `artifact_roundtrip`, `cold_start`, `cpu_stress`, `data_pipeline`, `dependency_install`, `error_recovery`, `output_fidelity`, `repository_task`, `session_state`, `sqlite_analytics`, `timeout_handling`

Raw reports: [data/attempts/modal_evaluation.json](../../reports/data/attempts/modal_evaluation.json)

No successful runtime inventory for this exact recorded configuration/adapter/stack. See raw checks and prerequisite failures.

Recorded requests and guest-visible observations are distinct; guest observations are not reserved-resource, image, GPU-eligibility or isolation attestation. Early attempts without requested settings remain incomplete.

## Configuration `c6eceedf16a1` / adapter `71538074cc69` / concurrency 3

Runtime classification: **remote_runtime**. Request recording complete: **True**.

```json
{
  "label": "adapter-defaults",
  "requested": {
    "cpu": 2,
    "cpu_unit": "physical-core request",
    "memory": 2048,
    "memory_unit": "MiB request",
    "image": "debian_slim",
    "python_version": null,
    "gpu": null,
    "runtime": null,
    "region": null,
    "block_network": false,
    "session_ttl_seconds": 180
  }
}
```

Client execution stack: `{"python": "3.13.13", "sdk": "modal", "version": "1.6.1"}`.

Suites: `cpu_stress`

Raw reports: [data/attempts/modal_burst_evaluation.json](../../reports/data/attempts/modal_burst_evaluation.json)

No successful runtime inventory for this exact recorded configuration/adapter/stack. See raw checks and prerequisite failures.

Recorded requests and guest-visible observations are distinct; guest observations are not reserved-resource, image, GPU-eligibility or isolation attestation. Early attempts without requested settings remain incomplete.

## Configuration `c6eceedf16a1` / adapter `71538074cc69` / concurrency 1

Runtime classification: **remote_runtime**. Request recording complete: **True**.

```json
{
  "label": "adapter-defaults",
  "requested": {
    "cpu": 2,
    "cpu_unit": "physical-core request",
    "memory": 2048,
    "memory_unit": "MiB request",
    "image": "debian_slim",
    "python_version": null,
    "gpu": null,
    "runtime": null,
    "region": null,
    "block_network": false,
    "session_ttl_seconds": 180
  }
}
```

Client execution stack: `{"python": "3.13.13", "sdk": "modal", "version": "1.6.1"}`.

Suites: `artifact_roundtrip`, `cold_start`, `cpu_stress`, `data_pipeline`, `dependency_install`, `error_recovery`, `output_fidelity`, `repository_task`, `runtime_inventory`, `session_state`, `sqlite_analytics`, `timeout_handling`

Raw reports: [data/attempts/modal_evaluation.json](../../reports/data/attempts/modal_evaluation.json)

### Observation `bench-a5258d4a469e` — 2026-10-13T07:42:06.839662+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "x86_64", "implementation": "CPython", "kernel": "4.19.0-gvisor", "os": "Linux", "python": "3.13.3"}` |
| CPU | `{"affinity_count": 18, "model": "unknown", "visible_logical_cpus": 18}` |
| Memory | `{"sysconf_physical_bytes": 352928985088}` |
| cgroup limits | `{"cpu_max": null, "cpu_period_v1": "1000000", "cpu_quota_v1": "18000000", "cpuset_effective": null, "memory_limit_v1": "352928985088", "memory_max": null}` |
| GPU probe | `{"devices": [], "probe": "nvidia-smi_unavailable"}` |

### Observation `bench-a65421209f4e` — 2026-10-13T07:42:10.803667+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "x86_64", "implementation": "CPython", "kernel": "4.19.0-gvisor", "os": "Linux", "python": "3.13.3"}` |
| CPU | `{"affinity_count": 18, "model": "unknown", "visible_logical_cpus": 18}` |
| Memory | `{"sysconf_physical_bytes": 218142515200}` |
| cgroup limits | `{"cpu_max": null, "cpu_period_v1": "1000000", "cpu_quota_v1": "18000000", "cpuset_effective": null, "memory_limit_v1": "218142515200", "memory_max": null}` |
| GPU probe | `{"devices": [], "probe": "nvidia-smi_unavailable"}` |

### Observation `bench-abd28c084c36` — 2026-10-13T07:42:59.739133+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "x86_64", "implementation": "CPython", "kernel": "4.19.0-gvisor", "os": "Linux", "python": "3.13.3"}` |
| CPU | `{"affinity_count": 18, "model": "unknown", "visible_logical_cpus": 18}` |
| Memory | `{"sysconf_physical_bytes": 353064042496}` |
| cgroup limits | `{"cpu_max": null, "cpu_period_v1": "1000000", "cpu_quota_v1": "18000000", "cpuset_effective": null, "memory_limit_v1": "353064042496", "memory_max": null}` |
| GPU probe | `{"devices": [], "probe": "nvidia-smi_unavailable"}` |

### Observation `bench-4291daf1978a` — 2026-10-13T07:43:35.875716+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "x86_64", "implementation": "CPython", "kernel": "4.19.0-gvisor", "os": "Linux", "python": "3.13.3"}` |
| CPU | `{"affinity_count": 18, "model": "unknown", "visible_logical_cpus": 18}` |
| Memory | `{"sysconf_physical_bytes": 218142519296}` |
| cgroup limits | `{"cpu_max": null, "cpu_period_v1": "1000000", "cpu_quota_v1": "18000000", "cpuset_effective": null, "memory_limit_v1": "218142519296", "memory_max": null}` |
| GPU probe | `{"devices": [], "probe": "nvidia-smi_unavailable"}` |

### Observation `bench-f8d3923a99a9` — 2026-10-13T07:44:32.360288+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "x86_64", "implementation": "CPython", "kernel": "4.19.0-gvisor", "os": "Linux", "python": "3.13.3"}` |
| CPU | `{"affinity_count": 18, "model": "unknown", "visible_logical_cpus": 18}` |
| Memory | `{"sysconf_physical_bytes": 486238371840}` |
| cgroup limits | `{"cpu_max": null, "cpu_period_v1": "1000000", "cpu_quota_v1": "18000000", "cpuset_effective": null, "memory_limit_v1": "486238371840", "memory_max": null}` |
| GPU probe | `{"devices": [], "probe": "nvidia-smi_unavailable"}` |


Recorded requests and guest-visible observations are distinct; guest observations are not reserved-resource, image, GPU-eligibility or isolation attestation. Early attempts without requested settings remain incomplete.

## Configuration `39ed10c5d0c2` / adapter `05607a7a2ce5` / concurrency 1

Runtime classification: **remote_runtime**. Request recording complete: **False**.

```json
{
  "label": "adapter-defaults"
}
```

Client execution stack: `null`.

Suites: `runtime_inventory`, `timeout_handling`

Raw reports: [data/attempts/modal_evaluation.json](../../reports/data/attempts/modal_evaluation.json)

### Observation `bench-e02663f89706` — 2026-10-13T07:13:22.556860+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "x86_64", "implementation": "CPython", "kernel": "4.19.0-gvisor", "os": "Linux", "python": "3.13.3"}` |
| CPU | `{"affinity_count": 18, "model": "unknown", "visible_logical_cpus": 18}` |
| Memory | `{"sysconf_physical_bytes": 218142531584}` |
| cgroup limits | `{"cpu_max": null, "cpu_period_v1": "1000000", "cpu_quota_v1": "18000000", "cpuset_effective": null, "memory_limit_v1": "218142531584", "memory_max": null}` |
| GPU probe | `{"devices": [], "probe": "nvidia-smi_unavailable"}` |

### Observation `bench-505f9c3cbdc5` — 2026-10-13T07:13:25.365449+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "x86_64", "implementation": "CPython", "kernel": "4.19.0-gvisor", "os": "Linux", "python": "3.13.3"}` |
| CPU | `{"affinity_count": 18, "model": "unknown", "visible_logical_cpus": 18}` |
| Memory | `{"sysconf_physical_bytes": 353059229696}` |
| cgroup limits | `{"cpu_max": null, "cpu_period_v1": "1000000", "cpu_quota_v1": "18000000", "cpuset_effective": null, "memory_limit_v1": "353059229696", "memory_max": null}` |
| GPU probe | `{"devices": [], "probe": "nvidia-smi_unavailable"}` |

### Observation `bench-a15f15f71a74` — 2026-10-13T07:13:39.494484+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "x86_64", "implementation": "CPython", "kernel": "4.19.0-gvisor", "os": "Linux", "python": "3.13.3"}` |
| CPU | `{"affinity_count": 18, "model": "unknown", "visible_logical_cpus": 18}` |
| Memory | `{"sysconf_physical_bytes": 353064173568}` |
| cgroup limits | `{"cpu_max": null, "cpu_period_v1": "1000000", "cpu_quota_v1": "18000000", "cpuset_effective": null, "memory_limit_v1": "353064173568", "memory_max": null}` |
| GPU probe | `{"devices": [], "probe": "nvidia-smi_unavailable"}` |

### Observation `bench-ff543858ee65` — 2026-10-13T07:13:47.039558+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "x86_64", "implementation": "CPython", "kernel": "4.19.0-gvisor", "os": "Linux", "python": "3.13.3"}` |
| CPU | `{"affinity_count": 18, "model": "unknown", "visible_logical_cpus": 18}` |
| Memory | `{"sysconf_physical_bytes": 218142507008}` |
| cgroup limits | `{"cpu_max": null, "cpu_period_v1": "1000000", "cpu_quota_v1": "18000000", "cpuset_effective": null, "memory_limit_v1": "218142507008", "memory_max": null}` |
| GPU probe | `{"devices": [], "probe": "nvidia-smi_unavailable"}` |

### Observation `bench-4d8107f67915` — 2026-10-13T07:14:00.258881+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "x86_64", "implementation": "CPython", "kernel": "4.19.0-gvisor", "os": "Linux", "python": "3.13.3"}` |
| CPU | `{"affinity_count": 18, "model": "unknown", "visible_logical_cpus": 18}` |
| Memory | `{"sysconf_physical_bytes": 352929026048}` |
| cgroup limits | `{"cpu_max": null, "cpu_period_v1": "1000000", "cpu_quota_v1": "18000000", "cpuset_effective": null, "memory_limit_v1": "352929026048", "memory_max": null}` |
| GPU probe | `{"devices": [], "probe": "nvidia-smi_unavailable"}` |


Recorded requests and guest-visible observations are distinct; guest observations are not reserved-resource, image, GPU-eligibility or isolation attestation. Early attempts without requested settings remain incomplete.

## Configuration `39ed10c5d0c2` / adapter `unrecorded` / concurrency 1

Runtime classification: **remote_runtime**. Request recording complete: **False**.

```json
{
  "label": "adapter-defaults"
}
```

Client execution stack: `null`.

Suites: `artifact_roundtrip`, `cold_start`, `cpu_stress`, `data_pipeline`, `dependency_install`, `error_recovery`, `output_fidelity`, `repository_task`, `session_state`, `sqlite_analytics`, `timeout_handling`

Raw reports: [data/attempts/modal_evaluation.json](../../reports/data/attempts/modal_evaluation.json)

No successful runtime inventory for this exact recorded configuration/adapter/stack. See raw checks and prerequisite failures.

Recorded requests and guest-visible observations are distinct; guest observations are not reserved-resource, image, GPU-eligibility or isolation attestation. Early attempts without requested settings remain incomplete.
