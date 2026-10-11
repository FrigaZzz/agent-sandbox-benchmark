"""Consistent front matter generated above preserved expert provider dossiers."""
from urllib.parse import urlencode

START = "<!-- COMMON CONTRACT START -->"
END = "<!-- COMMON CONTRACT END -->"
ADAPTERS = {"aws": "aws_agentcore", "local_baseline": "local_subprocess"}
BOUNDARIES = {
    "modal": "Sandbox exec/filesystem API; Function and model-hosting performance are separate.",
    "e2b": "Code Interpreter sandbox API; shared cloud, BYOC and self-operated Embed are distinct deployments.",
    "blaxel": "Managed Sandbox process/file API; agent deployments and inference hosting are separate.",
    "daytona": "Sandbox workspace API; standard, VM and GPU classes have different state/placement contracts.",
    "gcp_vertex": "Agent Engine default code sandbox via agent-sandbox CLI; not the model-native Gemini tool, Shell/Computer Use, BYOC, GKE or Compute Engine.",
    "aws": "AgentCore Code Interpreter via boto3; not AgentCore Runtime BYOC or classic Bedrock model-mediated execution.",
    "databricks": "SQL system.ai.python_exec via an existing warehouse; not Dedicated Sandbox Beta or system.ai.sandbox MCP.",
    "databricks_sandbox": "Dedicated Sandbox Beta workspace; not the measured SQL warehouse or newer MCP tool.",
    "gemini_tool": "Model-mediated code_execution; not application-controlled Agent Platform sandboxes.",
    "openai_tool": "Legacy Assistants Code Interpreter adapter; newer Hosted Shell/Responses products need separate measurements.",
    "alibaba": "OpenSandbox/AgentRun endpoint adapter; self-hosted and managed endpoints are distinct. Host auto-spawn is not attested remote isolation.",
    "k8s_agent_sandbox": "HTTP endpoint adapter; host auto-spawn does not establish deployment to Kubernetes/GKE or an isolation runtime.",
}
RESIDENCY = {
    "modal": ["Strict EEA compute pinning available; baseline unpinned", "Managed volumes, images and saved snapshots: US; regional bucket mounts separate", "Sandbox stdout/stderr: US", "Lifecycle calls: US-east", "Exact support/subprocessor access boundary needs verification", "Selected model/API endpoint has a separate contract"],
    "e2b": ["Default us-west1; Belgium Pro+ through support", "Shared-cluster scope unestablished; Enterprise BYOC templates/snapshots in customer VPC", "Shared scope unestablished; BYOC runtime logs in customer VPC", "E2B management/metrics flows remain; confirm scope", "Provider operates BYOC; confirm support access", "Selected model/API endpoint has a separate contract"],
    "blaxel": ["Frankfurt Mark 3 listed; baseline requested Oregon", "Volumes in-region; other images/snapshots/backups unknown", "Complete residency scope unknown", "Complete residency scope unknown", "Access/subprocessor boundary unknown", "External endpoint contract separate"],
    "gcp_vertex": ["Five named EU regions plus eu code endpoint; campaign preflight unretained", "Selected-location at-rest commitments; CMEK scope/parent region constraints apply", "Blanket operational-log EU-only boundary not established", "Covered at-rest metadata differs from excluded CMEK metadata", "Blanket support-flow EU-only boundary not established", "Foundation model endpoint/location configured separately"],
    "aws": ["Regional tool/client; Stockholm requested; check feature matrix", "Customer S3/EFS separately configured; session guide lists 30-day retention", "Log placement/replication must be assessed separately", "Customer-content commitments exclude various account/management data", "Confirm service/legal exceptions and support access", "Model inference and external calls separate"],
    "daytona": ["Shared eu target; shared GPUs use earth and ignore preference", "All shared volume/snapshot/backup placement not established", "Complete shared telemetry/log boundary unknown", "BYOC still uses managed control plane", "Dedicated regions are provider-managed; support boundary unknown", "External endpoint contract separate"],
    "databricks": ["SQL workspace/warehouse region unrecorded", "Function-specific storage/retention commitment unestablished", "Every SQL-tool log/backup location not established", "Regional processing statements do not settle every management flow", "Exact support/account flows unknown", "Designated AI Europe Geo includes EEA, UK and Switzerland; settings matter"],
    "databricks_sandbox": ["Dedicated EU availability depends on cloud/workspace; access failed here", "Home storage survives stop/start until deletion; placement/backup scope needs confirmation", "Every Sandbox log location not established", "Confirm regional management/account scope", "Exact support/account flows unknown", "Model endpoint and designated AI Geo settings separate"],
    "gemini_tool": ["Developer API EU-only processing not established; Cloud route differs", "Tool/file/cache retention and geography need route-specific verification", "Developer API terms permit transient logging across facilities", "No blanket EU-only management boundary established", "Google/agent facilities and access need contract review", "Execution is inside model turn; exact model/endpoint eligibility matters"],
    "openai_tool": ["Eligible European tool processing: EEA + Switzerland, not EU-27; legacy adapter unvalidated", "Regional content eligibility and temporary container/file retention separate", "Abuse-monitoring/retention eligibility conditions apply", "System/account/billing data excluded from content commitments", "System/support data excluded from content commitments", "Exact endpoint/model eligibility required"],
}
SURFACES = ["Compute", "Files / volumes / snapshots / backups", "Stdout / stderr / traces", "Control plane / metadata", "Support access / subprocessors", "External model / API calls"]
MEASURED_SUITES = {"file_transfer": ["artifact_roundtrip", "data_pipeline"],
                   "runtime_packages": ["dependency_install"], "session_reuse": ["session_state"]}


def cell(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_overview(spec, configs, summaries, name):
    provider = spec["provider"]
    adapter = ADAPTERS.get(provider, provider)
    lines = [START, f"# Provider contract: {name} (`{provider}`)", "",
             f"**Sources reviewed:** {spec['reviewed_at']} · **Deployment:** `{spec['deployment']}`", "",
             "## 1. Executive summary and product boundary", "",
             BOUNDARIES.get(provider, "Exact product boundary is described in the preserved dossier below."), "",
             cell(spec["customization"]["summary"]), "",
             f"Working adapter: [source](../../src/core/providers/{adapter}.py). Historical adapter hashes refer to measured revisions, not necessarily current source.", "",
             "The preserved dossier describes the dated inspected configuration. New budget/lifecycle guardrails change current adapter defaults without changing historical cohort evidence; see [operations](../../CONTRIBUTING.md).", "",
             "## 2. Documented contract vs measured adapter", "",
             "Support describes the platform. Measured describes only a bounded oracle on a recorded setup. Documented-only and unverified entries remain coverage gaps.", "",
             "| Capability | Platform support | Evidence state | Documented contract / scope | Measured adapter behavior | Sources |",
             "|---|---|---|---|---|---|"]
    for feature in spec["features"]:
        rows = [r for r in summaries if r["provider"] == provider and r["suite"] in MEASURED_SUITES.get(feature["id"], [])
                and r["eligible"] and r["concurrency"] == 1]
        by_suite = {suite: max((r for r in rows if r["suite"] == suite), key=lambda r: r["last_measured_at"], default=None)
                    for suite in MEASURED_SUITES.get(feature["id"], [])}
        observations = []
        for suite, row in by_suite.items():
            if row:
                ref = row["run_refs"][0]
                url = "../../reports/index.html#raw?" + urlencode({"provider": provider, "run_id": ref["run_id"]})
                observations.append(f"[{suite}: {row['outcomes'].get('pass', 0)}/{row['n']}]({url}), setup `{row['config_id']}`")
        measured = any(row for row in by_suite.values())
        state = "Measured (bounded fixture)" if measured else "Documented" if feature["evidence"] != "unverified" else "Unverified"
        sources = ", ".join(f"[{s}](#source-{s})" for s in feature["source_ids"])
        lines.append(f"| `{feature['id']}` | {feature['support']} | {state} | {cell(feature['notes'])} | "
                     + ("; ".join(observations) if observations else "No independently mapped passing fixture here; inspect dossier/configuration limits.") + f" | {sources} |")
    lines += ["", "## 3. Six residency surfaces", "",
              "Source: [dated residency audit and original vendor citations](../../reports/docs/eu-data-residency.md). These are documented boundaries/gaps, not measured EU residency or GDPR certification.", "",
              "| Surface | Documented boundary / verification gap |", "|---|---|"]
    values = RESIDENCY.get(provider, ["Operator-selected; remote deployment not attested",
        "Operator-selected storage/backup configuration", "Operator-selected observability",
        "Operator-selected management/control plane", "Operator/support-access policy required", "External endpoints remain separate"])
    lines.extend(f"| {surface} | {value} |" for surface, value in zip(SURFACES, values))
    lines += ["", "Benchmark location/request provenance is recorded separately in [tested configurations](tested-configurations.md).", "",
              "## 4. Dated pricing and billing units", "", cell(spec["pricing"]["model"]), "",
              "| SKU / resource | Original billing unit | USD list amount | Sources |", "|---|---|---:|---|"]
    for rate in spec["pricing"]["rates"]:
        amount = "Unknown" if rate["amount"] is None else f"{rate['amount']:.8f}".rstrip("0").rstrip(".")
        lines.append(f"| {cell(rate['resource'])} | {cell(rate['unit'])} | {amount} | " + ", ".join(f"[{s}](#source-{s})" for s in rate["source_ids"]) + " |")
    lines += ["", cell(spec["pricing"]["limitations"]), "", "## 5. Recorded configuration and guest inventory", "",
              "[All settings, client stacks, attempt IDs and observations](tested-configurations.md) · [Machine-readable export](tested-configurations.json)", ""]
    for config in configs[:3]:
        lines.append(f"- Setup `{config['config_id']}` · adapter `{config['adapter_sha256'][:12]}` · stack `{config['stack_sha256'][:12]}` · concurrency {config['concurrency']} · last measured {config['last_measured_at']}.")
    if not configs:
        lines.append("No versioned tested configuration; documented support does not establish a working deployment.")
    lines += ["", "Guest-visible CPU/RAM and device probes do not attest reserved hardware or isolation. No GPU configuration was benchmarked in this snapshot.", "",
              "## 6. Dated source register", ""]
    for source in spec["sources"]:
        lines.append(f"- <a id=\"source-{source['id']}\"></a> [{source['id']}: {cell(source['title'])}]({source['url']}) — accessed {source['accessed_at']}.")
    return "\n".join(lines + ["", END, "", "## Detailed provider dossier", ""])


def update_spec_page(path, overview):
    original = path.read_text() if path.exists() else ""
    if START in original and END in original:
        original = original.split(END, 1)[1].lstrip()
        original = original.removeprefix("## Detailed provider dossier").lstrip()
    path.write_text(overview + original)
