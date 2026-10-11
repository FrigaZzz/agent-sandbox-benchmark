# Alibaba OpenSandbox / AgentRun — tested configurations

Generated from real attempt records. [Documented capabilities](SPEC.md) describe broader options; the tested integration is narrower.

Requested settings, client versions, observation timestamps and raw evidence are retained in [tested-configurations.json](tested-configurations.json). No GPU-enabled or custom-image configuration was tested in these default campaigns.

## Configuration `001504324c5f` / adapter `6c4185a41998` / concurrency 1

Runtime classification: **unattested_endpoint**. Request recording complete: **True**.

```json
{
  "label": "live-rerun",
  "requested": {
    "product": "Alibaba OpenSandbox / AgentRun",
    "image": "opensandbox/code-interpreter:v1.0.2",
    "cpu": "1",
    "memory": "2Gi",
    "gpu": null,
    "session_mode": "stateful_reusable"
  }
}
```

Client execution stack: `{"python": "3.13.13", "sdk": null, "version": "unrecorded CLI/SDK"}`.

Suites: `agent_multiturn`, `artifact_roundtrip`, `cold_start`, `cpu_stress`, `data_pipeline`, `dependency_install`, `disk_io`, `env_security`, `error_recovery`, `mem_stress`, `net_isolation`, `output_fidelity`, `package_ecosystem`, `parallel_throughput`, `repository_task`, `runtime_inventory`, `session_state`, `sqlite_analytics`, `timeout_handling`

Raw reports: [data/attempts/alibaba_evaluation.json](../../reports/data/attempts/alibaba_evaluation.json)

### Observation `bench-7e17f684f468` — 2026-10-13T16:19:59.767439+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "arm64", "implementation": "CPython", "kernel": "27.0.0", "os": "Darwin", "python": "3.13.13"}` |
| CPU | `{"affinity_count": null, "model": null, "visible_logical_cpus": 10}` |
| Memory | `{"sysconf_physical_bytes": 17179869184}` |
| cgroup limits | `{"cpu_max": null, "cpu_period_v1": null, "cpu_quota_v1": null, "cpuset_effective": null, "memory_limit_v1": null, "memory_max": null}` |
| GPU probe | `{"devices": [], "probe": "nvidia-smi_unavailable"}` |

### Observation `bench-2196d4a58a17` — 2026-10-13T16:26:13.768432+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "arm64", "implementation": "CPython", "kernel": "27.0.0", "os": "Darwin", "python": "3.13.13"}` |
| CPU | `{"affinity_count": null, "model": null, "visible_logical_cpus": 10}` |
| Memory | `{"sysconf_physical_bytes": 17179869184}` |
| cgroup limits | `{"cpu_max": null, "cpu_period_v1": null, "cpu_quota_v1": null, "cpuset_effective": null, "memory_limit_v1": null, "memory_max": null}` |
| GPU probe | `{"devices": [], "probe": "nvidia-smi_unavailable"}` |


Recorded requests and guest-visible observations are distinct; guest observations are not reserved-resource, image, GPU-eligibility or isolation attestation. Early attempts without requested settings remain incomplete.

## Configuration `dd9b844d07e4` / adapter `6c4185a41998` / concurrency 1

Runtime classification: **unattested_endpoint**. Request recording complete: **True**.

```json
{
  "label": "adapter-defaults",
  "requested": {
    "product": "Alibaba OpenSandbox / AgentRun",
    "image": "opensandbox/code-interpreter:v1.0.2",
    "cpu": "1",
    "memory": "2Gi",
    "gpu": null,
    "session_mode": "stateful_reusable"
  }
}
```

Client execution stack: `{"python": "3.13.13", "sdk": null, "version": "unrecorded CLI/SDK"}`.

Suites: `agent_multiturn`, `artifact_roundtrip`, `cold_start`, `cpu_stress`, `data_pipeline`, `dependency_install`, `error_recovery`, `output_fidelity`, `parallel_throughput`, `repository_task`, `runtime_inventory`, `session_state`, `sqlite_analytics`, `timeout_handling`

Raw reports: [data/attempts/alibaba_evaluation.json](../../reports/data/attempts/alibaba_evaluation.json)

### Observation `bench-cd7c8bc61076` — 2026-10-13T10:45:17.172408+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "arm64", "implementation": "CPython", "kernel": "27.0.0", "os": "Darwin", "python": "3.13.13"}` |
| CPU | `{"affinity_count": null, "model": null, "visible_logical_cpus": 10}` |
| Memory | `{"sysconf_physical_bytes": 17179869184}` |
| cgroup limits | `{"cpu_max": null, "cpu_period_v1": null, "cpu_quota_v1": null, "cpuset_effective": null, "memory_limit_v1": null, "memory_max": null}` |
| GPU probe | `{"devices": [], "probe": "nvidia-smi_unavailable"}` |


Recorded requests and guest-visible observations are distinct; guest observations are not reserved-resource, image, GPU-eligibility or isolation attestation. Early attempts without requested settings remain incomplete.
