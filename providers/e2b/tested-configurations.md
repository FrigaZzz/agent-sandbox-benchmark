# E2B — tested configurations

Generated from real attempt records. [Documented capabilities](SPEC.md) describe broader options; the tested integration is narrower.

Requested settings, client versions, observation timestamps and raw evidence are retained in [tested-configurations.json](tested-configurations.json). No GPU-enabled or custom-image configuration was tested in these default campaigns.

## Configuration `1c8788fe1d12` / adapter `44055e4ac080` / concurrency 1

Runtime classification: **remote_runtime**. Request recording complete: **True**.

```json
{
  "label": "live-rerun",
  "requested": {
    "template": null,
    "allow_internet_access": true,
    "session_ttl_seconds": 180,
    "cpu": null,
    "memory": null,
    "gpu": null
  }
}
```

Client execution stack: `{"python": "3.13.13", "sdk": "e2b-code-interpreter", "version": "2.10.5"}`.

Suites: `artifact_roundtrip`, `cold_start`, `cpu_stress`, `data_pipeline`, `dependency_install`, `error_recovery`, `output_fidelity`, `repository_task`, `session_state`, `sqlite_analytics`, `timeout_handling`

Raw reports: [data/attempts/e2b_evaluation.json](../../reports/data/attempts/e2b_evaluation.json)

No successful runtime inventory for this exact recorded configuration/adapter/stack. See raw checks and prerequisite failures.

Recorded requests and guest-visible observations are distinct; guest observations are not reserved-resource, image, GPU-eligibility or isolation attestation. Early attempts without requested settings remain incomplete.

## Configuration `b8b64fa8b3ea` / adapter `44055e4ac080` / concurrency 3

Runtime classification: **remote_runtime**. Request recording complete: **True**.

```json
{
  "label": "adapter-defaults",
  "requested": {
    "template": null,
    "allow_internet_access": true,
    "session_ttl_seconds": 180,
    "cpu": null,
    "memory": null,
    "gpu": null
  }
}
```

Client execution stack: `{"python": "3.13.13", "sdk": "e2b-code-interpreter", "version": "2.10.5"}`.

Suites: `cpu_stress`

Raw reports: [data/attempts/e2b_burst_evaluation.json](../../reports/data/attempts/e2b_burst_evaluation.json)

No successful runtime inventory for this exact recorded configuration/adapter/stack. See raw checks and prerequisite failures.

Recorded requests and guest-visible observations are distinct; guest observations are not reserved-resource, image, GPU-eligibility or isolation attestation. Early attempts without requested settings remain incomplete.

## Configuration `b8b64fa8b3ea` / adapter `44055e4ac080` / concurrency 1

Runtime classification: **remote_runtime**. Request recording complete: **True**.

```json
{
  "label": "adapter-defaults",
  "requested": {
    "template": null,
    "allow_internet_access": true,
    "session_ttl_seconds": 180,
    "cpu": null,
    "memory": null,
    "gpu": null
  }
}
```

Client execution stack: `{"python": "3.13.13", "sdk": "e2b-code-interpreter", "version": "2.10.5"}`.

Suites: `artifact_roundtrip`, `cold_start`, `cpu_stress`, `data_pipeline`, `dependency_install`, `error_recovery`, `output_fidelity`, `repository_task`, `runtime_inventory`, `session_state`, `sqlite_analytics`, `timeout_handling`

Raw reports: [data/attempts/e2b_evaluation.json](../../reports/data/attempts/e2b_evaluation.json)

### Observation `bench-700e8fa525e4` — 2026-10-13T07:42:10.468416+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "x86_64", "implementation": "CPython", "kernel": "6.1.158+", "os": "Linux", "python": "3.13.16"}` |
| CPU | `{"affinity_count": 2, "model": "Intel(R) Xeon(R) Processor @ 2.60GHz", "visible_logical_cpus": 2}` |
| Memory | `{"sysconf_physical_bytes": 2079141888}` |
| cgroup limits | `{"cpu_max": null, "cpu_period_v1": null, "cpu_quota_v1": null, "cpuset_effective": "0-1", "memory_limit_v1": null, "memory_max": null}` |
| GPU probe | `{"devices": [], "probe": "nvidia-smi_unavailable"}` |

### Observation `bench-92738672b3bf` — 2026-10-13T07:42:14.481971+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "x86_64", "implementation": "CPython", "kernel": "6.1.158+", "os": "Linux", "python": "3.13.16"}` |
| CPU | `{"affinity_count": 2, "model": "Intel(R) Xeon(R) Processor @ 2.60GHz", "visible_logical_cpus": 2}` |
| Memory | `{"sysconf_physical_bytes": 2079141888}` |
| cgroup limits | `{"cpu_max": null, "cpu_period_v1": null, "cpu_quota_v1": null, "cpuset_effective": "0-1", "memory_limit_v1": null, "memory_max": null}` |
| GPU probe | `{"devices": [], "probe": "nvidia-smi_unavailable"}` |

### Observation `bench-8d37029291d3` — 2026-10-13T07:43:00.741015+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "x86_64", "implementation": "CPython", "kernel": "6.1.158+", "os": "Linux", "python": "3.13.16"}` |
| CPU | `{"affinity_count": 2, "model": "Intel(R) Xeon(R) Processor @ 2.60GHz", "visible_logical_cpus": 2}` |
| Memory | `{"sysconf_physical_bytes": 2079141888}` |
| cgroup limits | `{"cpu_max": null, "cpu_period_v1": null, "cpu_quota_v1": null, "cpuset_effective": "0-1", "memory_limit_v1": null, "memory_max": null}` |
| GPU probe | `{"devices": [], "probe": "nvidia-smi_unavailable"}` |

### Observation `bench-191e71516a70` — 2026-10-13T07:43:31.308740+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "x86_64", "implementation": "CPython", "kernel": "6.1.158+", "os": "Linux", "python": "3.13.16"}` |
| CPU | `{"affinity_count": 2, "model": "Intel(R) Xeon(R) Processor @ 2.60GHz", "visible_logical_cpus": 2}` |
| Memory | `{"sysconf_physical_bytes": 2079141888}` |
| cgroup limits | `{"cpu_max": null, "cpu_period_v1": null, "cpu_quota_v1": null, "cpuset_effective": "0-1", "memory_limit_v1": null, "memory_max": null}` |
| GPU probe | `{"devices": [], "probe": "nvidia-smi_unavailable"}` |

### Observation `bench-b7ec5b5dcbd3` — 2026-10-13T07:44:26.487097+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "x86_64", "implementation": "CPython", "kernel": "6.1.158+", "os": "Linux", "python": "3.13.16"}` |
| CPU | `{"affinity_count": 2, "model": "Intel(R) Xeon(R) Processor @ 2.60GHz", "visible_logical_cpus": 2}` |
| Memory | `{"sysconf_physical_bytes": 2079141888}` |
| cgroup limits | `{"cpu_max": null, "cpu_period_v1": null, "cpu_quota_v1": null, "cpuset_effective": "0-1", "memory_limit_v1": null, "memory_max": null}` |
| GPU probe | `{"devices": [], "probe": "nvidia-smi_unavailable"}` |


Recorded requests and guest-visible observations are distinct; guest observations are not reserved-resource, image, GPU-eligibility or isolation attestation. Early attempts without requested settings remain incomplete.

## Configuration `39ed10c5d0c2` / adapter `4bb2a61a8dab` / concurrency 1

Runtime classification: **remote_runtime**. Request recording complete: **False**.

```json
{
  "label": "adapter-defaults"
}
```

Client execution stack: `null`.

Suites: `runtime_inventory`

Raw reports: [data/attempts/e2b_evaluation.json](../../reports/data/attempts/e2b_evaluation.json)

### Observation `bench-1650fd65b551` — 2026-10-13T07:13:22.555687+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "x86_64", "implementation": "CPython", "kernel": "6.1.158+", "os": "Linux", "python": "3.13.16"}` |
| CPU | `{"affinity_count": 2, "model": "Intel(R) Xeon(R) Processor @ 2.60GHz", "visible_logical_cpus": 2}` |
| Memory | `{"sysconf_physical_bytes": 2079141888}` |
| cgroup limits | `{"cpu_max": null, "cpu_period_v1": null, "cpu_quota_v1": null, "cpuset_effective": "0-1", "memory_limit_v1": null, "memory_max": null}` |
| GPU probe | `{"devices": [], "probe": "nvidia-smi_unavailable"}` |

### Observation `bench-3e10db933e0a` — 2026-10-13T07:13:25.782001+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "x86_64", "implementation": "CPython", "kernel": "6.1.158+", "os": "Linux", "python": "3.13.16"}` |
| CPU | `{"affinity_count": 2, "model": "Intel(R) Xeon(R) Processor @ 2.60GHz", "visible_logical_cpus": 2}` |
| Memory | `{"sysconf_physical_bytes": 2079141888}` |
| cgroup limits | `{"cpu_max": null, "cpu_period_v1": null, "cpu_quota_v1": null, "cpuset_effective": "0-1", "memory_limit_v1": null, "memory_max": null}` |
| GPU probe | `{"devices": [], "probe": "nvidia-smi_unavailable"}` |

### Observation `bench-43412619a6c1` — 2026-10-13T07:13:27.520010+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "x86_64", "implementation": "CPython", "kernel": "6.1.158+", "os": "Linux", "python": "3.13.16"}` |
| CPU | `{"affinity_count": 2, "model": "Intel(R) Xeon(R) Processor @ 2.60GHz", "visible_logical_cpus": 2}` |
| Memory | `{"sysconf_physical_bytes": 2079141888}` |
| cgroup limits | `{"cpu_max": null, "cpu_period_v1": null, "cpu_quota_v1": null, "cpuset_effective": "0-1", "memory_limit_v1": null, "memory_max": null}` |
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

Raw reports: [data/attempts/e2b_evaluation.json](../../reports/data/attempts/e2b_evaluation.json)

No successful runtime inventory for this exact recorded configuration/adapter/stack. See raw checks and prerequisite failures.

Recorded requests and guest-visible observations are distinct; guest observations are not reserved-resource, image, GPU-eligibility or isolation attestation. Early attempts without requested settings remain incomplete.
