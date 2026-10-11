# Kubernetes adapter (deployment unattested) — tested configurations

Generated from real attempt records. [Documented capabilities](SPEC.md) describe broader options; the tested integration is narrower.

Requested settings, client versions, observation timestamps and raw evidence are retained in [tested-configurations.json](tested-configurations.json). No GPU-enabled or custom-image configuration was tested in these default campaigns.

## Configuration `5ec993b27fcf` / adapter `b8704b7e87ef` / concurrency 1

Runtime classification: **unattested_endpoint**. Request recording complete: **True**.

```json
{
  "label": "live-rerun",
  "requested": {
    "product": "HTTP endpoint adapter",
    "auto_spawn": true,
    "deployment_attested": false
  }
}
```

Client execution stack: `{"python": "3.13.13", "sdk": null, "version": "unrecorded CLI/SDK"}`.

Suites: `agent_multiturn`, `artifact_roundtrip`, `cold_start`, `cpu_stress`, `data_pipeline`, `dependency_install`, `disk_io`, `env_security`, `error_recovery`, `mem_stress`, `net_isolation`, `output_fidelity`, `package_ecosystem`, `parallel_throughput`, `repository_task`, `runtime_inventory`, `session_state`, `sqlite_analytics`, `timeout_handling`

Raw reports: [data/attempts/k8s_agent_sandbox_evaluation.json](../../reports/data/attempts/k8s_agent_sandbox_evaluation.json)

### Observation `bench-f3568cb0173d` — 2026-10-13T16:21:34.861964+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "aarch64", "implementation": "CPython", "kernel": "6.12.54-linuxkit", "os": "Linux", "python": "3.12.15"}` |
| CPU | `{"affinity_count": 10, "model": null, "visible_logical_cpus": 10}` |
| Memory | `{"sysconf_physical_bytes": 8217448448}` |
| cgroup limits | `{"cpu_max": "max 100000", "cpu_period_v1": null, "cpu_quota_v1": null, "cpuset_effective": "0-9", "memory_limit_v1": null, "memory_max": "max"}` |
| GPU probe | `{"devices": [], "probe": "nvidia-smi_unavailable"}` |

### Observation `bench-317c0ae3a626` — 2026-10-13T16:26:44.244892+00:00

| Field | Guest-visible observation |
| :--- | :--- |
| Runtime | `{"architecture": "aarch64", "implementation": "CPython", "kernel": "6.12.54-linuxkit", "os": "Linux", "python": "3.12.15"}` |
| CPU | `{"affinity_count": 10, "model": null, "visible_logical_cpus": 10}` |
| Memory | `{"sysconf_physical_bytes": 8217448448}` |
| cgroup limits | `{"cpu_max": "max 100000", "cpu_period_v1": null, "cpu_quota_v1": null, "cpuset_effective": "0-9", "memory_limit_v1": null, "memory_max": "max"}` |
| GPU probe | `{"devices": [], "probe": "nvidia-smi_unavailable"}` |


Recorded requests and guest-visible observations are distinct; guest observations are not reserved-resource, image, GPU-eligibility or isolation attestation. Early attempts without requested settings remain incomplete.
