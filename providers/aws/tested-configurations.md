# AWS AgentCore — tested configurations

Generated from real attempt records. [Documented capabilities](SPEC.md) describe broader options; the tested integration is narrower.

Requested settings, client versions, observation timestamps and raw evidence are retained in [tested-configurations.json](tested-configurations.json). No GPU-enabled or custom-image configuration was tested in these default campaigns.

## Configuration `05a56c471d15` / adapter `beb5698440d9` / concurrency 1

Runtime classification: **remote_runtime**. Request recording complete: **True**.

```json
{
  "label": "live-rerun",
  "requested": {
    "product": "AgentCore Code Interpreter",
    "region": "eu-north-1",
    "image": "provider-default",
    "cpu": null,
    "memory": null,
    "gpu": null,
    "network_policy": "tool configuration not attested by adapter",
    "session_mode": "fresh session"
  }
}
```

Client execution stack: `{"python": "3.13.13", "sdk": "boto3", "version": "1.43.112"}`.

Suites: `artifact_roundtrip`, `cold_start`, `cpu_stress`, `data_pipeline`, `dependency_install`, `error_recovery`, `output_fidelity`, `repository_task`, `runtime_inventory`, `session_state`, `sqlite_analytics`, `timeout_handling`

Raw reports: [data/attempts/aws_evaluation.json](../../reports/data/attempts/aws_evaluation.json)

### Observation `bench-343356c07e13` — 2026-10-13T16:46:54.112917+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "aarch64", "implementation": "CPython", "kernel": "6.1.161-18.298.amzn2023.aarch64", "os": "Linux", "python": "3.12.13"}` |
| CPU | `{"affinity_count": 2, "model": null, "visible_logical_cpus": 2}` |
| Memory | `{"sysconf_physical_bytes": 8406753280}` |
| cgroup limits | `{"cpu_max": null, "cpu_period_v1": null, "cpu_quota_v1": null, "cpuset_effective": "0-1", "memory_limit_v1": null, "memory_max": null}` |
| GPU probe | `{"devices": [], "probe": "nvidia-smi_unavailable"}` |


Recorded requests and guest-visible observations are distinct; guest observations are not reserved-resource, image, GPU-eligibility or isolation attestation. Early attempts without requested settings remain incomplete.

## Configuration `a017dc2faa1b` / adapter `beb5698440d9` / concurrency 1

Runtime classification: **remote_runtime**. Request recording complete: **True**.

```json
{
  "label": "adapter-defaults",
  "requested": {
    "product": "AgentCore Code Interpreter",
    "region": "eu-north-1",
    "image": "provider-default",
    "cpu": null,
    "memory": null,
    "gpu": null,
    "network_policy": "tool configuration not attested by adapter",
    "session_mode": "fresh session"
  }
}
```

Client execution stack: `{"python": "3.13.13", "sdk": "boto3", "version": "1.43.112"}`.

Suites: `cold_start`, `cpu_stress`, `output_fidelity`, `repository_task`, `runtime_inventory`, `sqlite_analytics`

Raw reports: [data/attempts/aws_evaluation.json](../../reports/data/attempts/aws_evaluation.json)

### Observation `bench-d7af96c2c6f7` — 2026-10-13T07:36:43.260548+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "aarch64", "implementation": "CPython", "kernel": "6.1.161-18.298.amzn2023.aarch64", "os": "Linux", "python": "3.12.13"}` |
| CPU | `{"affinity_count": 2, "model": null, "visible_logical_cpus": 2}` |
| Memory | `{"sysconf_physical_bytes": 8406753280}` |
| cgroup limits | `{"cpu_max": null, "cpu_period_v1": null, "cpu_quota_v1": null, "cpuset_effective": "0-1", "memory_limit_v1": null, "memory_max": null}` |
| GPU probe | `{"devices": [], "probe": "nvidia-smi_unavailable"}` |

### Observation `bench-197c19f67cb0` — 2026-10-13T07:36:45.773887+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "aarch64", "implementation": "CPython", "kernel": "6.1.161-18.298.amzn2023.aarch64", "os": "Linux", "python": "3.12.13"}` |
| CPU | `{"affinity_count": 2, "model": null, "visible_logical_cpus": 2}` |
| Memory | `{"sysconf_physical_bytes": 8406753280}` |
| cgroup limits | `{"cpu_max": null, "cpu_period_v1": null, "cpu_quota_v1": null, "cpuset_effective": "0-1", "memory_limit_v1": null, "memory_max": null}` |
| GPU probe | `{"devices": [], "probe": "nvidia-smi_unavailable"}` |

### Observation `bench-1f87d9302c2b` — 2026-10-13T07:36:51.053191+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "aarch64", "implementation": "CPython", "kernel": "6.1.161-18.298.amzn2023.aarch64", "os": "Linux", "python": "3.12.13"}` |
| CPU | `{"affinity_count": 2, "model": null, "visible_logical_cpus": 2}` |
| Memory | `{"sysconf_physical_bytes": 8406753280}` |
| cgroup limits | `{"cpu_max": null, "cpu_period_v1": null, "cpu_quota_v1": null, "cpuset_effective": "0-1", "memory_limit_v1": null, "memory_max": null}` |
| GPU probe | `{"devices": [], "probe": "nvidia-smi_unavailable"}` |

### Observation `bench-15498de02f23` — 2026-10-13T07:37:02.208812+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "aarch64", "implementation": "CPython", "kernel": "6.1.161-18.298.amzn2023.aarch64", "os": "Linux", "python": "3.12.13"}` |
| CPU | `{"affinity_count": 2, "model": null, "visible_logical_cpus": 2}` |
| Memory | `{"sysconf_physical_bytes": 8406753280}` |
| cgroup limits | `{"cpu_max": null, "cpu_period_v1": null, "cpu_quota_v1": null, "cpuset_effective": "0-1", "memory_limit_v1": null, "memory_max": null}` |
| GPU probe | `{"devices": [], "probe": "nvidia-smi_unavailable"}` |

### Observation `bench-2f31f117e5ab` — 2026-10-13T07:37:09.909648+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "aarch64", "implementation": "CPython", "kernel": "6.1.161-18.298.amzn2023.aarch64", "os": "Linux", "python": "3.12.13"}` |
| CPU | `{"affinity_count": 2, "model": null, "visible_logical_cpus": 2}` |
| Memory | `{"sysconf_physical_bytes": 8406753280}` |
| cgroup limits | `{"cpu_max": null, "cpu_period_v1": null, "cpu_quota_v1": null, "cpuset_effective": "0-1", "memory_limit_v1": null, "memory_max": null}` |
| GPU probe | `{"devices": [], "probe": "nvidia-smi_unavailable"}` |


Recorded requests and guest-visible observations are distinct; guest observations are not reserved-resource, image, GPU-eligibility or isolation attestation. Early attempts without requested settings remain incomplete.

## Configuration `39ed10c5d0c2` / adapter `c4828f950bf6` / concurrency 1

Runtime classification: **remote_runtime**. Request recording complete: **False**.

```json
{
  "label": "adapter-defaults"
}
```

Client execution stack: `null`.

Suites: `cold_start`, `cpu_stress`, `output_fidelity`, `repository_task`, `runtime_inventory`, `sqlite_analytics`

Raw reports: [data/attempts/aws_evaluation.json](../../reports/data/attempts/aws_evaluation.json)

### Observation `bench-4b2aa14e4e01` — 2026-10-13T07:13:22.552291+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "aarch64", "implementation": "CPython", "kernel": "6.1.161-18.298.amzn2023.aarch64", "os": "Linux", "python": "3.12.13"}` |
| CPU | `{"affinity_count": 2, "model": null, "visible_logical_cpus": 2}` |
| Memory | `{"sysconf_physical_bytes": 8406753280}` |
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

Suites: `cold_start`

Raw reports: [data/attempts/aws_evaluation.json](../../reports/data/attempts/aws_evaluation.json)

No successful runtime inventory for this exact recorded configuration/adapter/stack. See raw checks and prerequisite failures.

Recorded requests and guest-visible observations are distinct; guest observations are not reserved-resource, image, GPU-eligibility or isolation attestation. Early attempts without requested settings remain incomplete.
