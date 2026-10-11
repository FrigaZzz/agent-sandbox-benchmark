# GCP client contract and historical reference notes

Reviewed 2026-10-13. This is a portable summary of the client contract and earlier
probe notes used in the [provider specification](SPEC.md). The raw October 13
[campaign attempts](../../reports/data/attempts/gcp_vertex_evaluation.json) and
[inventories](tested-configurations.md) remain the primary comparison evidence.
Earlier probe notes are not an attestation of the later campaign's placement,
allocation, encryption or successful cloud cleanup.

## CLI contract

The benchmark expects the external [`agent-sandbox` CLI](https://github.com/FrigaZzz/gcp-agent-sandbox).
It is a separate installation, not included in this benchmark's Python package.
The client checked after the campaign reported version **0.2.0**; its reference
SDK was `google-cloud-aiplatform[agent_engines]==2.3.0`, API `v1beta1` (Preview).
Install the CLI using its upstream instructions and verify `agent-sandbox --version`.

The adapter invokes:

```bash
agent-sandbox run --file workload.py --format json --ttl 900 --max-output-chars 0 --out results
# Add repeatable --upload local-file:input/remote-name for inputs.
```

`run` owns create, upload, execute, output retrieval and deletion. `start`, `exec`,
`bash`, `upload`, `download`, `status` and `stop` support longer-lived sessions.
The client reference defaults to a 900-second TTL and caps it at 3,600 seconds;
the benchmark adapter caps its request at 900 seconds. These are client limits,
distinct from the current service documentation's lifetime options.

JSON results contain `ok`, `exit_status`, `stdout`, `stderr`, returned `files`,
and lifecycle information such as `sandbox_deleted`. CLI exit codes distinguish
success (0), tooling/cloud errors (1), usage errors (2), remote execution failure
(3) and interruption (130). The benchmark adapter does not retain every lifecycle
field, so its local cleanup outcome does not prove provider-side deletion.

Configure your own `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`,
`AGENT_RUNTIME_NAME` and, for parent creation, `KMS_KEY_NAME`. The client supports
an explicit `AGENT_SANDBOX_ENV`, project `.agent-sandbox.env` and user configuration.
Check the installed version's `config show` and `doctor` before running; retain
sanitized requested/resolved placement evidence separately from credentials.

## Historical environment probe

The earlier notes describe one **2026-10-01** code-sandbox probe in
`europe-west8` (Milan). Its original per-call logs are not part of the October 13
campaign dataset. Treat this summary as historical context requiring reproduction.

| Observation in the earlier notes | Scope |
|---|---|
| Python 3.12.5, Debian 12, x86_64, kernel `4.19.0-gvisor` | Guest strings, not independent isolation attestation |
| Eight visible CPUs, approximately 2× parallel/serial speedup | Does not establish eight reserved vCPUs |
| 2 GiB reported memory | Guest observation, not a current allocation guarantee |
| DNS/IP requests failed | Evidence about that probe, not effective policy for all deployments |
| No usable GPU observed | Does not establish platform-wide GPU eligibility |
| Python variables, files and a background process survived calls within one live sandbox | Does not establish persistence across deletion or the one-shot adapter |

The managed working directory in those notes was `/home/bard`; this is a guest
path. Current package/tool observations are published in the benchmark's generated
inventories. The later uploaded offline-wheel fixture independently verifies a narrow
dependency-installation workflow; it does not verify online or arbitrary native installs.

## SDK contracts

The versioned reference used `agentplatform.Client(project=..., location=...,
http_options={"api_version": "v1beta1"})`, parent runtime creation, sandbox
create/get/list/delete and `execute_code` with code plus named input bytes.
Execution returns output chunks: JSON results carry `exit_status_int`, `msg_out`
and `msg_err`; file chunks have a `file_name` metadata attribute and raw byte data.
A file chunk is not stdout, and raw bytes must not be base64-decoded a second time.

Earlier observations reported newly created visible files under the guest working
directory being returned, with uploaded files retained but not echoed. Exceptions
could be returned as a nonzero result rather than a raised SDK exception. These
version-specific details require rechecking when changing the CLI/SDK.
See the [official code execution guide](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/sandbox/code-execution-overview).

## Shell and container scope

The default code sandbox can execute subprocesses. A separately provisioned shell
or custom-container sandbox is a different deployment path. The earlier reference
did not verify default shell containers with CMEK end to end in its preview region;
it recorded possible `INTERNAL` failures. Do not interpret those notes as a current
service-wide limitation or a successfully tested BYOC configuration.
See the [official custom-container guide](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/sandbox/custom-containers).

## CMEK setup

Use a symmetric regional CryptoKey matching the parent runtime's region. Reference
setup notes attach the key when creating the parent and distinguish at-rest content
from resource metadata. The preview client setup required key-level
`roles/cloudkms.cryptoKeyEncrypterDecrypter` for both the Agent Runtime and core
Vertex service agents, identified using the workload project's number. This is
version-specific setup evidence; follow current provider instructions and verify
parent/key readback and KMS audit logs for your deployment.

Configure SDK Application Default Credentials separately from CLI authentication.
Do not infer CMEK attachment from a successful workload. See the
[official CMEK guide](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/sandbox/configure-cmek).

## Billing and cleanup

The reference treats creation-to-deletion/expiry as billable lifetime, uses bounded
TTLs and records CLI-owned sessions for cleanup. Interrupt handlers can attempt
deletion but cannot run after a hard kill or machine failure. List the exact parent
runtime after runs and retain dated status/deletion evidence. A local ledger or
harness cleanup result alone is insufficient. Parent runtimes and KMS resources
have separate lifecycles.

The benchmark's saved cost multiplier is explicitly unverified and is not an invoice.
See [official lifecycle documentation](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/sandbox/manage-sandboxes)
and [provider pricing](https://cloud.google.com/vertex-ai/pricing).
