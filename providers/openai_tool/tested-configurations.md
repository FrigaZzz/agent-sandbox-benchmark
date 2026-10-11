# OpenAI Tool — tested configurations

Generated from real attempt records. [Documented capabilities](SPEC.md) describe broader options; the tested integration is narrower.

Requested settings, client versions, observation timestamps and raw evidence are retained in [tested-configurations.json](tested-configurations.json). No GPU-enabled or custom-image configuration was tested in these default campaigns.

## Configuration `dac26c6c470b` / adapter `ea1dd2cdcb0a` / concurrency 1

Runtime classification: **model_mediated**. Request recording complete: **True**.

```json
{
  "label": "adapter-defaults",
  "requested": {
    "product": "OpenAI Assistants Code Interpreter",
    "model": "gpt-4o"
  }
}
```

Client execution stack: `{"python": "3.13.13", "sdk": "openai", "version": "3.29.0"}`.

Suites: `runtime_inventory`

Raw reports: [data/attempts/openai_tool_evaluation.json](../../reports/data/attempts/openai_tool_evaluation.json)

No successful runtime inventory for this exact recorded configuration/adapter/stack. See raw checks and prerequisite failures.

Recorded requests and guest-visible observations are distinct; guest observations are not reserved-resource, image, GPU-eligibility or isolation attestation. Early attempts without requested settings remain incomplete.
