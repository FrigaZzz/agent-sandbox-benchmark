# Databricks SQL MCP — tested configurations

Generated from real attempt records. [Documented capabilities](SPEC.md) describe broader options; the tested integration is narrower.

Requested settings, client versions, observation timestamps and raw evidence are retained in [tested-configurations.json](tested-configurations.json). No GPU-enabled or custom-image configuration was tested in these default campaigns.

## Configuration `f6b3c3845d9a` / adapter `ff6ebfad7dbf` / concurrency 1

Runtime classification: **remote_runtime**. Request recording complete: **True**.

```json
{
  "label": "live-rerun",
  "requested": {
    "product": "SQL system.ai.python_exec",
    "image": "provider-default",
    "cpu": null,
    "memory": null,
    "gpu": null
  }
}
```

Client execution stack: `{"python": "3.13.13", "sdk": "databricks-sdk", "version": "0.151.0"}`.

Suites: `artifact_roundtrip`, `cold_start`, `cpu_stress`, `data_pipeline`, `dependency_install`, `error_recovery`, `output_fidelity`, `repository_task`, `session_state`, `sqlite_analytics`, `timeout_handling`

Raw reports: [data/attempts/databricks_evaluation.json](../../reports/data/attempts/databricks_evaluation.json)

No successful runtime inventory for this exact recorded configuration/adapter/stack. See raw checks and prerequisite failures.

Recorded requests and guest-visible observations are distinct; guest observations are not reserved-resource, image, GPU-eligibility or isolation attestation. Early attempts without requested settings remain incomplete.

## Configuration `629df7809d28` / adapter `ff6ebfad7dbf` / concurrency 1

Runtime classification: **remote_runtime**. Request recording complete: **True**.

```json
{
  "label": "adapter-defaults",
  "requested": {
    "product": "SQL system.ai.python_exec",
    "image": "provider-default",
    "cpu": null,
    "memory": null,
    "gpu": null
  }
}
```

Client execution stack: `{"python": "3.13.13", "sdk": "databricks-sdk", "version": "0.151.0"}`.

Suites: `cold_start`, `cpu_stress`, `runtime_inventory`

Raw reports: [data/attempts/databricks_evaluation.json](../../reports/data/attempts/databricks_evaluation.json)

### Observation `bench-ffe6099a8853` — 2026-10-13T07:41:59.384571+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "aarch64", "implementation": "CPython", "kernel": "4.4.0", "os": "Linux", "python": "3.12.3"}` |
| CPU | `{"affinity_count": 8, "model": null, "visible_logical_cpus": 8}` |
| Memory | `{"sysconf_physical_bytes": 314572800}` |
| cgroup limits | `{"cpu_max": null, "cpu_period_v1": "100000", "cpu_quota_v1": "-1", "cpuset_effective": null, "memory_limit_v1": "9223372036854775807", "memory_max": null}` |
| GPU probe | `{"devices": [], "probe": "nvidia-smi_unavailable"}` |

### Observation `bench-a969f85e1357` — 2026-10-13T07:42:32.569712+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "aarch64", "implementation": "CPython", "kernel": "4.4.0", "os": "Linux", "python": "3.12.3"}` |
| CPU | `{"affinity_count": 8, "model": null, "visible_logical_cpus": 8}` |
| Memory | `{"sysconf_physical_bytes": 314572800}` |
| cgroup limits | `{"cpu_max": null, "cpu_period_v1": "100000", "cpu_quota_v1": "-1", "cpuset_effective": null, "memory_limit_v1": "9223372036854775807", "memory_max": null}` |
| GPU probe | `{"devices": [], "probe": "nvidia-smi_unavailable"}` |

### Observation `bench-9dba248fcfbd` — 2026-10-13T07:42:38.961081+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "aarch64", "implementation": "CPython", "kernel": "4.4.0", "os": "Linux", "python": "3.12.3"}` |
| CPU | `{"affinity_count": 8, "model": null, "visible_logical_cpus": 8}` |
| Memory | `{"sysconf_physical_bytes": 314572800}` |
| cgroup limits | `{"cpu_max": null, "cpu_period_v1": "100000", "cpu_quota_v1": "-1", "cpuset_effective": null, "memory_limit_v1": "9223372036854775807", "memory_max": null}` |
| GPU probe | `{"devices": [], "probe": "nvidia-smi_unavailable"}` |

### Observation `bench-5576fa8be000` — 2026-10-13T07:42:42.113897+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "aarch64", "implementation": "CPython", "kernel": "4.4.0", "os": "Linux", "python": "3.12.3"}` |
| CPU | `{"affinity_count": 8, "model": null, "visible_logical_cpus": 8}` |
| Memory | `{"sysconf_physical_bytes": 314572800}` |
| cgroup limits | `{"cpu_max": null, "cpu_period_v1": "100000", "cpu_quota_v1": "-1", "cpuset_effective": null, "memory_limit_v1": "9223372036854775807", "memory_max": null}` |
| GPU probe | `{"devices": [], "probe": "nvidia-smi_unavailable"}` |

### Observation `bench-5e9a40ff4f31` — 2026-10-13T07:42:54.426096+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "aarch64", "implementation": "CPython", "kernel": "4.4.0", "os": "Linux", "python": "3.12.3"}` |
| CPU | `{"affinity_count": 8, "model": null, "visible_logical_cpus": 8}` |
| Memory | `{"sysconf_physical_bytes": 314572800}` |
| cgroup limits | `{"cpu_max": null, "cpu_period_v1": "100000", "cpu_quota_v1": "-1", "cpuset_effective": null, "memory_limit_v1": "9223372036854775807", "memory_max": null}` |
| GPU probe | `{"devices": [], "probe": "nvidia-smi_unavailable"}` |


Recorded requests and guest-visible observations are distinct; guest observations are not reserved-resource, image, GPU-eligibility or isolation attestation. Early attempts without requested settings remain incomplete.

## Configuration `39ed10c5d0c2` / adapter `ff6ebfad7dbf` / concurrency 1

Runtime classification: **remote_runtime**. Request recording complete: **False**.

```json
{
  "label": "adapter-defaults"
}
```

Client execution stack: `null`.

Suites: `cold_start`, `runtime_inventory`

Raw reports: [data/attempts/databricks_evaluation.json](../../reports/data/attempts/databricks_evaluation.json)

No successful runtime inventory for this exact recorded configuration/adapter/stack. See raw checks and prerequisite failures.

Recorded requests and guest-visible observations are distinct; guest observations are not reserved-resource, image, GPU-eligibility or isolation attestation. Early attempts without requested settings remain incomplete.
