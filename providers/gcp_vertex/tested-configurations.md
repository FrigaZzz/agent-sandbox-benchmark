# GCP Agent Sandbox — tested configurations

Generated from real attempt records. [Documented capabilities](SPEC.md) describe broader options; the tested integration is narrower.

Requested settings, client versions, observation timestamps and raw evidence are retained in [tested-configurations.json](tested-configurations.json). No GPU-enabled or custom-image configuration was tested in these default campaigns.

## Configuration `1d300bb22b3d` / adapter `c640a283b17a` / concurrency 1

Runtime classification: **remote_runtime**. Request recording complete: **True**.

```json
{
  "label": "live-rerun",
  "requested": {
    "product": "Agent Engine default code sandbox",
    "image": "provider-default",
    "cpu": null,
    "memory": null,
    "gpu": null,
    "region": "CLI-configured; see preflight",
    "network_policy": "not requested by adapter",
    "session_mode": "one-shot run"
  }
}
```

Client execution stack: `{"python": "3.13.13", "sdk": "agent-sandbox", "version": "unrecorded CLI/SDK"}`.

Suites: `artifact_roundtrip`, `cold_start`, `cpu_stress`, `data_pipeline`, `dependency_install`, `error_recovery`, `output_fidelity`, `repository_task`, `session_state`, `sqlite_analytics`, `timeout_handling`

Raw reports: [data/attempts/gcp_vertex_evaluation.json](../../reports/data/attempts/gcp_vertex_evaluation.json)

No successful runtime inventory for this exact recorded configuration/adapter/stack. See raw checks and prerequisite failures.

Recorded requests and guest-visible observations are distinct; guest observations are not reserved-resource, image, GPU-eligibility or isolation attestation. Early attempts without requested settings remain incomplete.

## Configuration `5a61c94c9323` / adapter `c640a283b17a` / concurrency 1

Runtime classification: **remote_runtime**. Request recording complete: **True**.

```json
{
  "label": "adapter-defaults",
  "requested": {
    "product": "Agent Engine default code sandbox",
    "image": "provider-default",
    "cpu": null,
    "memory": null,
    "gpu": null,
    "region": "CLI-configured; see preflight",
    "network_policy": "not requested by adapter",
    "session_mode": "one-shot run"
  }
}
```

Client execution stack: `{"python": "3.13.13", "sdk": "agent-sandbox", "version": "unrecorded CLI/SDK"}`.

Suites: `artifact_roundtrip`, `cold_start`, `cpu_stress`, `data_pipeline`, `dependency_install`, `output_fidelity`, `repository_task`, `runtime_inventory`, `sqlite_analytics`

Raw reports: [data/attempts/gcp_vertex_evaluation.json](../../reports/data/attempts/gcp_vertex_evaluation.json)

### Observation `bench-5660d6199e6d` — 2026-10-13T07:37:42.172191+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "x86_64", "implementation": "CPython", "kernel": "4.19.0-gvisor", "os": "Linux", "python": "3.12.5"}` |
| CPU | `{"affinity_count": 8, "model": "unknown", "visible_logical_cpus": 8}` |
| Memory | `{"sysconf_physical_bytes": 2147483648}` |
| cgroup limits | `{"cpu_max": null, "cpu_period_v1": null, "cpu_quota_v1": null, "cpuset_effective": null, "memory_limit_v1": null, "memory_max": null}` |
| GPU probe | `{"devices": [], "probe": "nvidia-smi_unavailable"}` |

### Observation `bench-4e1181bd3117` — 2026-10-13T07:38:09.053041+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "x86_64", "implementation": "CPython", "kernel": "4.19.0-gvisor", "os": "Linux", "python": "3.12.5"}` |
| CPU | `{"affinity_count": 8, "model": "unknown", "visible_logical_cpus": 8}` |
| Memory | `{"sysconf_physical_bytes": 2147483648}` |
| cgroup limits | `{"cpu_max": null, "cpu_period_v1": null, "cpu_quota_v1": null, "cpuset_effective": null, "memory_limit_v1": null, "memory_max": null}` |
| GPU probe | `{"devices": [], "probe": "nvidia-smi_unavailable"}` |

### Observation `bench-43cb53ac8d1a` — 2026-10-13T07:39:39.083616+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "x86_64", "implementation": "CPython", "kernel": "4.19.0-gvisor", "os": "Linux", "python": "3.12.5"}` |
| CPU | `{"affinity_count": 8, "model": "unknown", "visible_logical_cpus": 8}` |
| Memory | `{"sysconf_physical_bytes": 2147483648}` |
| cgroup limits | `{"cpu_max": null, "cpu_period_v1": null, "cpu_quota_v1": null, "cpuset_effective": null, "memory_limit_v1": null, "memory_max": null}` |
| GPU probe | `{"devices": [], "probe": "nvidia-smi_unavailable"}` |

### Observation `bench-e16ff5f8938a` — 2026-10-13T07:40:24.786306+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "x86_64", "implementation": "CPython", "kernel": "4.19.0-gvisor", "os": "Linux", "python": "3.12.5"}` |
| CPU | `{"affinity_count": 8, "model": "unknown", "visible_logical_cpus": 8}` |
| Memory | `{"sysconf_physical_bytes": 2147483648}` |
| cgroup limits | `{"cpu_max": null, "cpu_period_v1": null, "cpu_quota_v1": null, "cpuset_effective": null, "memory_limit_v1": null, "memory_max": null}` |
| GPU probe | `{"devices": [], "probe": "nvidia-smi_unavailable"}` |

### Observation `bench-00c6e3de3abe` — 2026-10-13T07:40:40.876732+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "x86_64", "implementation": "CPython", "kernel": "4.19.0-gvisor", "os": "Linux", "python": "3.12.5"}` |
| CPU | `{"affinity_count": 8, "model": "unknown", "visible_logical_cpus": 8}` |
| Memory | `{"sysconf_physical_bytes": 2147483648}` |
| cgroup limits | `{"cpu_max": null, "cpu_period_v1": null, "cpu_quota_v1": null, "cpuset_effective": null, "memory_limit_v1": null, "memory_max": null}` |
| GPU probe | `{"devices": [], "probe": "nvidia-smi_unavailable"}` |


Recorded requests and guest-visible observations are distinct; guest observations are not reserved-resource, image, GPU-eligibility or isolation attestation. Early attempts without requested settings remain incomplete.

## Configuration `39ed10c5d0c2` / adapter `c640a283b17a` / concurrency 1

Runtime classification: **remote_runtime**. Request recording complete: **False**.

```json
{
  "label": "adapter-defaults"
}
```

Client execution stack: `null`.

Suites: `runtime_inventory`

Raw reports: [data/attempts/gcp_vertex_evaluation.json](../../reports/data/attempts/gcp_vertex_evaluation.json)

### Observation `bench-155a70502b58` — 2026-10-13T07:13:22.557310+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "x86_64", "implementation": "CPython", "kernel": "4.19.0-gvisor", "os": "Linux", "python": "3.12.5"}` |
| CPU | `{"affinity_count": 8, "model": "unknown", "visible_logical_cpus": 8}` |
| Memory | `{"sysconf_physical_bytes": 2147483648}` |
| cgroup limits | `{"cpu_max": null, "cpu_period_v1": null, "cpu_quota_v1": null, "cpuset_effective": null, "memory_limit_v1": null, "memory_max": null}` |
| GPU probe | `{"devices": [], "probe": "nvidia-smi_unavailable"}` |

### Observation `bench-076822f9fbe9` — 2026-10-13T07:13:30.456143+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "x86_64", "implementation": "CPython", "kernel": "4.19.0-gvisor", "os": "Linux", "python": "3.12.5"}` |
| CPU | `{"affinity_count": 8, "model": "unknown", "visible_logical_cpus": 8}` |
| Memory | `{"sysconf_physical_bytes": 2147483648}` |
| cgroup limits | `{"cpu_max": null, "cpu_period_v1": null, "cpu_quota_v1": null, "cpuset_effective": null, "memory_limit_v1": null, "memory_max": null}` |
| GPU probe | `{"devices": [], "probe": "nvidia-smi_unavailable"}` |

### Observation `bench-7de7edf4bc3a` — 2026-10-13T07:13:36.220476+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "x86_64", "implementation": "CPython", "kernel": "4.19.0-gvisor", "os": "Linux", "python": "3.12.5"}` |
| CPU | `{"affinity_count": 8, "model": "unknown", "visible_logical_cpus": 8}` |
| Memory | `{"sysconf_physical_bytes": 2147483648}` |
| cgroup limits | `{"cpu_max": null, "cpu_period_v1": null, "cpu_quota_v1": null, "cpuset_effective": null, "memory_limit_v1": null, "memory_max": null}` |
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

Suites: `artifact_roundtrip`, `cold_start`, `cpu_stress`, `data_pipeline`, `dependency_install`, `output_fidelity`, `repository_task`, `sqlite_analytics`

Raw reports: [data/attempts/gcp_vertex_evaluation.json](../../reports/data/attempts/gcp_vertex_evaluation.json)

No successful runtime inventory for this exact recorded configuration/adapter/stack. See raw checks and prerequisite failures.

Recorded requests and guest-visible observations are distinct; guest observations are not reserved-resource, image, GPU-eligibility or isolation attestation. Early attempts without requested settings remain incomplete.
