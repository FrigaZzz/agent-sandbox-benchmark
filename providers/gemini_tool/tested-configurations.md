# Gemini Tool — tested configurations

Generated from real attempt records. [Documented capabilities](SPEC.md) describe broader options; the tested integration is narrower.

Requested settings, client versions, observation timestamps and raw evidence are retained in [tested-configurations.json](tested-configurations.json). No GPU-enabled or custom-image configuration was tested in these default campaigns.

## Configuration `ae1077b5e6a4` / adapter `cf31d20528a9` / concurrency 1

Runtime classification: **model_mediated**. Request recording complete: **True**.

```json
{
  "label": "live-rerun",
  "requested": {
    "product": "Gemini code_execution",
    "model": "gemini-2.5-flash",
    "image": "provider-default",
    "cpu": null,
    "memory": null,
    "gpu": null
  }
}
```

Client execution stack: `{"python": "3.13.13", "sdk": "google-genai", "version": "2.22.0"}`.

Suites: `artifact_roundtrip`, `cold_start`, `cpu_stress`, `data_pipeline`, `dependency_install`, `error_recovery`, `output_fidelity`, `repository_task`, `session_state`, `sqlite_analytics`, `timeout_handling`

Raw reports: [data/attempts/gemini_tool_evaluation.json](../../reports/data/attempts/gemini_tool_evaluation.json)

No successful runtime inventory for this exact recorded configuration/adapter/stack. See raw checks and prerequisite failures.

Recorded requests and guest-visible observations are distinct; guest observations are not reserved-resource, image, GPU-eligibility or isolation attestation. Early attempts without requested settings remain incomplete.

## Configuration `1cf72ddce422` / adapter `cf31d20528a9` / concurrency 1

Runtime classification: **model_mediated**. Request recording complete: **True**.

```json
{
  "label": "adapter-defaults",
  "requested": {
    "product": "Gemini code_execution",
    "model": "gemini-2.5-flash",
    "image": "provider-default",
    "cpu": null,
    "memory": null,
    "gpu": null
  }
}
```

Client execution stack: `{"python": "3.13.13", "sdk": "google-genai", "version": "2.22.0"}`.

Suites: `cold_start`, `cpu_stress`, `runtime_inventory`, `sqlite_analytics`

Raw reports: [data/attempts/gemini_tool_evaluation.json](../../reports/data/attempts/gemini_tool_evaluation.json)

### Observation `bench-e7d2c6931dbf` — 2026-10-13T07:41:59.384572+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "x86_64", "implementation": "CPython", "kernel": "4.19.0-gvisor", "os": "Linux", "python": "3.11.8"}` |
| CPU | `{"affinity_count": 8, "model": "unknown", "visible_logical_cpus": 8}` |
| Memory | `{"sysconf_physical_bytes": 2147483648}` |
| cgroup limits | `{"cpu_max": null, "cpu_period_v1": null, "cpu_quota_v1": null, "cpuset_effective": null, "memory_limit_v1": null, "memory_max": null}` |
| GPU probe | `{"devices": [], "probe": "nvidia-smi_unavailable"}` |

### Observation `bench-2d72cdb9274c` — 2026-10-13T07:42:22.996971+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "x86_64", "implementation": "CPython", "kernel": "4.19.0-gvisor", "os": "Linux", "python": "3.11.8"}` |
| CPU | `{"affinity_count": 8, "model": "unknown", "visible_logical_cpus": 8}` |
| Memory | `{"sysconf_physical_bytes": 2147483648}` |
| cgroup limits | `{"cpu_max": null, "cpu_period_v1": null, "cpu_quota_v1": null, "cpuset_effective": null, "memory_limit_v1": null, "memory_max": null}` |
| GPU probe | `{"devices": [], "probe": "nvidia-smi_unavailable"}` |

### Observation `bench-b8f383a1f326` — 2026-10-13T07:43:17.606632+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "x86_64", "implementation": "CPython", "kernel": "4.19.0-gvisor", "os": "Linux", "python": "3.11.8"}` |
| CPU | `{"affinity_count": 8, "model": "unknown", "visible_logical_cpus": 8}` |
| Memory | `{"sysconf_physical_bytes": 2147483648}` |
| cgroup limits | `{"cpu_max": null, "cpu_period_v1": null, "cpu_quota_v1": null, "cpuset_effective": null, "memory_limit_v1": null, "memory_max": null}` |
| GPU probe | `{"devices": [], "probe": "nvidia-smi_unavailable"}` |

### Observation `bench-9690b50009fa` — 2026-10-13T07:43:36.216659+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "x86_64", "implementation": "CPython", "kernel": "4.19.0-gvisor", "os": "Linux", "python": "3.11.8"}` |
| CPU | `{"affinity_count": 8, "model": "unknown", "visible_logical_cpus": 8}` |
| Memory | `{"sysconf_physical_bytes": 2147483648}` |
| cgroup limits | `{"cpu_max": null, "cpu_period_v1": null, "cpu_quota_v1": null, "cpuset_effective": null, "memory_limit_v1": null, "memory_max": null}` |
| GPU probe | `{"devices": [], "probe": "nvidia-smi_unavailable"}` |

### Observation `bench-a030f41b6789` — 2026-10-13T07:43:49.697427+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "x86_64", "implementation": "CPython", "kernel": "4.19.0-gvisor", "os": "Linux", "python": "3.11.8"}` |
| CPU | `{"affinity_count": 8, "model": "unknown", "visible_logical_cpus": 8}` |
| Memory | `{"sysconf_physical_bytes": 2147483648}` |
| cgroup limits | `{"cpu_max": null, "cpu_period_v1": null, "cpu_quota_v1": null, "cpuset_effective": null, "memory_limit_v1": null, "memory_max": null}` |
| GPU probe | `{"devices": [], "probe": "nvidia-smi_unavailable"}` |


Recorded requests and guest-visible observations are distinct; guest observations are not reserved-resource, image, GPU-eligibility or isolation attestation. Early attempts without requested settings remain incomplete.

## Configuration `39ed10c5d0c2` / adapter `cf31d20528a9` / concurrency 1

Runtime classification: **model_mediated**. Request recording complete: **False**.

```json
{
  "label": "adapter-defaults"
}
```

Client execution stack: `null`.

Suites: `cold_start`, `runtime_inventory`

Raw reports: [data/attempts/gemini_tool_evaluation.json](../../reports/data/attempts/gemini_tool_evaluation.json)

### Observation `bench-d7539e1b2901` — 2026-10-13T07:15:13.907896+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "x86_64", "implementation": "CPython", "kernel": "4.19.0-gvisor", "os": "Linux", "python": "3.11.8"}` |
| CPU | `{"affinity_count": 8, "model": "unknown", "visible_logical_cpus": 8}` |
| Memory | `{"sysconf_physical_bytes": 2147483648}` |
| cgroup limits | `{"cpu_max": null, "cpu_period_v1": null, "cpu_quota_v1": null, "cpuset_effective": null, "memory_limit_v1": null, "memory_max": null}` |
| GPU probe | `{"devices": [], "probe": "nvidia-smi_unavailable"}` |


Recorded requests and guest-visible observations are distinct; guest observations are not reserved-resource, image, GPU-eligibility or isolation attestation. Early attempts without requested settings remain incomplete.
