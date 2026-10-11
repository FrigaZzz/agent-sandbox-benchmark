# Agent sandboxes: EU data-residency source guide

Reviewed. Companion to the [PDF](../downloads/sandbox-field-guide.pdf). This research describes documented product boundaries; the benchmark did not independently attest end-to-end EU residency.

## The decision that matters

Specify whether your requirement is **EU member states**, **EEA**, or a wider **Europe** geography. These are different boundaries. The UK and Switzerland are not EU member states; the EEA also includes Iceland, Liechtenstein and Norway.

Check six data surfaces separately:

1. Execution and in-memory processing.
2. Files, images, snapshots, volumes and backups.
3. Application logs and traces.
4. Control-plane, account and resource-management data.
5. Support access and subprocessors.
6. Downstream model inference, API calls and dependency downloads.

An EU region selector is useful configuration evidence. It does not establish where every associated data surface is processed or stored. **Unknown** means the reviewed sources do not establish a boundary; it does not mean the feature is unsupported.

## Provider comparison

### Modal

- **Compute:** Sandbox `region=` accepts `eu` and European subregions. Broad `eu` is the **EEA**, not strictly EU members. Region pinning is strict; capacity shortages do not trigger out-of-region relocation. Unpinned workloads use the global pool. Region pinning changes capacity and pricing.
- **Data plane:** Sandbox exec I/O and encrypted tunnels go directly to the selected container region. Lifecycle calls such as create/terminate use the **US-east control plane**.
- **Stored data:** Sandbox stdout/stderr logs, explicitly created snapshots, and managed Images, Volumes, Dicts, Queues and Secrets are **US-resident**. Filesystem and memory snapshots can contain customer data. Customer-selected cloud bucket mounts provide a separate durable-storage option.
- **Practical consequence:** EEA compute pinning alone cannot satisfy a strict EU-only requirement covering sensitive stdout, snapshots and managed volumes. Evaluate sanitised logging, external storage and all remaining flows against the actual requirement.

Sources: [Region selection](https://modal.com/docs/guide/region-selection) · [Product-specific data residency](https://modal.com/docs/guide/data-residency) · [Security and retention](https://modal.com/docs/guide/security).

### E2B

- **Managed default:** Google Cloud `us-west1` for all plans.
- **Shared EU route:** Google Cloud **Belgium `europe-west1`**, **Pro and above**, enabled through support. Exact placement/ranges can change; the egress guide is not a permanent single-region contract.
- **Shared-cloud scope:** The EU-cluster FAQ establishes sandbox availability, not comprehensive residency for templates, snapshots, logs, secrets or management data.
- **Enterprise BYOC:** Documents templates, snapshots and runtime logs inside the customer VPC, and direct build-source and sandbox traffic to that VPC. E2B still operates the deployment and receives anonymised system metrics. Confirm E2B Cloud account/management data, support and selected-region scope separately. BYOC is distinct from self-operated E2B Embed.

Sources: [EU access and plan](https://docs.e2b.dev/faq/eu-region.md) · [Default and EU cloud regions](https://docs.e2b.dev/faq/egress-ip-ranges.md) · [Security](https://docs.e2b.dev/faq/security-and-compliance.md) · [BYOC architecture](https://docs.e2b.dev/byoc.md).

### Blaxel

- **Mark 3:** `eu-fra-1` is Frankfurt, Germany. `eu-lon-1` is London, **UK**, despite the prefix. Availability may need support enablement.
- **Placement:** Sandboxes and preview URLs are single-region resources with regional endpoints. Omission / `auto` chooses an optimal location; it is not an EU-only constraint. Applicable deployment policies constrain placement.
- **Storage:** Volumes are regional and attach to same-region sandboxes. The reviewed sources do not establish complete location scope for images, standby snapshots, logs, telemetry, backups, secrets or the control plane.
- **Telemetry:** CLI/SDK error tracking, deployed OpenTelemetry and sandbox-runtime reporting have separate controls. Disabling one does not disable all.

Sources: [Mark 3 regions](https://docs.blaxel.ai/Infrastructure/Regions.md) · [Regional volumes](https://docs.blaxel.ai/api-reference/volumes/create-persistent-volume.md) · [Data collection](https://docs.blaxel.ai/Security/Data-collection-and-privacy.md).

### Google Agent Platform Sandbox

This is the direct managed sandbox path, not Gemini's model-native Developer API tool.

- **Named EU regions:** Belgium `europe-west1`, Frankfurt `europe-west3`, Netherlands `europe-west4`, Milan `europe-west8`, Madrid `europe-southwest1`. London and Zurich are separately listed, outside the EU.
- **Multi-region:** Code Execution also supports the `eu` endpoint. Match API version and feature eligibility to the selected path.
- **Default code resource configuration:** The official Code Execution quickstart exposes `machine_config`, including `MACHINE_CONFIG_VCPU4_RAM4GIB`. Resource selection is not exclusively a BYOC capability; the benchmark adapter did not request a machine configuration. Custom containers remain a separate path.
- **Residency scope:** Agent infrastructure documents selected-location **data-at-rest** residency, including agent source, deployment packages, session history, memory entries and metadata. Foundation-model processing follows its separately configured model endpoint/location.
- **CMEK:** Specified sandbox disk/snapshot surfaces are covered; resource metadata and environment variables are excluded. Custom image encryption is separately configured in Artifact Registry. Single-region keys must match the parent instance's region. Runtime multi-regional endpoints do not support CMEK; do not assume the `eu` path and the single-region parent-runtime key setup are interchangeable.
- **Unknown:** The reviewed pages do not establish a blanket EU-only boundary for every operational log, support flow and ancillary service.

Sources: [Sandbox/agent locations](https://docs.cloud.google.com/gemini-enterprise-agent-platform/resources/agent-locations) · [Data residency](https://docs.cloud.google.com/gemini-enterprise-agent-platform/resources/data-residency) · [Explicit code location](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/sandbox/code-execution-quickstart) · [CMEK scope](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/sandbox/configure-cmek).

### AWS AgentCore Code Interpreter

- **Feature-specific matrix:** Built-in Tools includes Frankfurt `eu-central-1`, Ireland `eu-west-1`, Paris `eu-west-3`, Milan `eu-south-1`, Spain `eu-south-2`, Stockholm `eu-north-1`. London is not EU.
- **Documentation discrepancy:** The general endpoint reference lists fewer regions than the feature-specific matrix. Confirm the exact Code Interpreter endpoint, account eligibility and API operation before deployment.
- **Placement:** Regional SDK/client and tool resource configure execution. The repository's Stockholm default is an adapter choice, not an AWS-wide default.
- **Storage and retention:** Customer S3 Files/EFS mounts have independent IAM, network and storage policies; replication and logs require separate assessment. The session guide describes cleanup after termination and separately a **30-day session-data retention policy**. Do not infer independently verified deletion of all retained copies from stop success.
- **Scope:** General customer-content location commitments exclude account information and various management metadata, with service/legal exceptions. Model inference and external calls have separate data flows.

Sources: [AgentCore feature regions](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agentcore-regions.html) · [General endpoints](https://docs.aws.amazon.com/general/latest/gr/bedrock_agentcore.html) · [Code Interpreter](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/code-interpreter-tool.html) · [Customer filesystems](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/code-interpreter-filesystem-configurations.html) · [Session characteristics](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/code-interpreter-session-characteristics.html) · [Content versus account data](https://aws.amazon.com/compliance/data-privacy-faq/).

### Databricks: three separate surfaces

- **Dedicated Sandbox Beta:** AWS EU availability lists Frankfurt, Ireland and Paris. Azure lists France Central, Germany West Central, North Europe and Sweden Central. Azure West Europe is not marked for dedicated Sandbox, although it supports serverless SQL. Requires supported workspace and preview enablement. GCP dedicated availability remains unverified from the reviewed sources.
- **Legacy SQL `system.ai.python_exec`:** This is the benchmarked adapter. Serverless SQL availability does not establish a complete function-specific entitlement/residency contract. The adapter chose an existing warehouse; its location/type were not retained.
- **New `system.ai.sandbox` MCP:** Unity Gateway Beta documents Python, SQL and shell with **no egress**, unlike dedicated Sandbox's unrestricted non-configurable egress. It was not benchmarked.
- **Storage:** Dedicated home storage, up to 100 GB, survives stop/start until deletion; non-home storage does not. Beta-end purge is possible.
- **Processing scope:** Databricks describes regional compute/control planes and regional serverless SQL processing. Designated AI Services use Geos: **Europe includes EEA, Switzerland and UK**. Cross-Geo processing can be enabled by an administrator. Storage commitments and AI processing commitments are distinct.
- **Unknown:** The reviewed evidence does not independently locate every Sandbox backup, log, support/account flow or downstream model request.

Sources: [AWS feature matrix](https://docs.databricks.com/aws/en/resources/feature-region-support) · [Azure matrix](https://learn.microsoft.com/en-us/azure/databricks/resources/feature-region-support) · [GCP matrix](https://docs.databricks.com/gcp/en/resources/feature-region-support) · [Dedicated Sandbox](https://docs.databricks.com/aws/en/compute/serverless/sandbox) · [Execution tools comparison](https://docs.databricks.com/aws/en/agents/custom-agents/code-interpreter-tools) · [Geos](https://docs.databricks.com/aws/en/resources/databricks-geos) · [Designated Services](https://docs.databricks.com/aws/en/resources/designated-services).

### Daytona

- **Ordinary shared placement:** `us` and `eu` targets. The reviewed shared `eu` guide does not name countries, cloud regions or zones. Target precedence is per-call → client/environment configuration → organisation default.
- **Shared GPU exception:** GPU sandboxes and snapshots use logical **`earth`**. Daytona selects placement and **ignores geographic preference**. Dedicated/custom GPU regions retain their targetable real region IDs.
- **Ownership:** Dedicated regions are Daytona-managed. BYOC customer compute still uses Daytona's managed control plane, although region-scoped proxy/SSH/snapshot services can be customer-deployed.
- **Storage:** Managed volumes use an S3-compatible object store and persist independently of sandbox deletion. Geographic placement of all shared snapshots, backups, telemetry, managed volumes and control-plane surfaces is not established by these sources.

Sources: [Regions and Earth exception](https://www.daytona.io/docs/en/regions.md) · [SDK target precedence](https://www.daytona.io/docs/en/python-sdk/sync/daytona.md) · [BYOC](https://www.daytona.io/docs/en/bring-your-own-compute.md) · [Volumes](https://www.daytona.io/docs/en/volumes.md).

## Model tools and self-operated routes

**OpenAI:** Current Code Interpreter supports regional storage/processing in **Europe: EEA + Switzerland**, via `eu.api.openai.com`, subject to endpoint/model eligibility and applicable retention arrangements. Non-US residency requires approval for abuse-monitoring controls and a Modified Retention amendment. System/account/billing/usage/support data is excluded from customer-content residency commitments. Temporary container state, Files and other objects have separate retention. This does not validate the benchmark's legacy Assistants adapter. [Official data controls](https://developers.openai.com/api/docs/guides/your-data).

**Gemini Developer API:** Availability in an EU country is not processing residency. Paid-service terms allow transient logging/caching in countries where Google or its agents maintain facilities. No EU-only boundary is established for that route. The **Google Cloud** route has model-, context-variant- and endpoint-specific commitments; a selected client region alone does not settle tool/model processing. New jurisdictional multi-region endpoints require supported models. [API terms](https://ai.google.dev/gemini-api/terms) · [Cloud residency](https://docs.cloud.google.com/gemini-enterprise-agent-platform/resources/data-residency) · [Supported capability/location framework](https://docs.cloud.google.com/gemini-enterprise-agent-platform/resources/supported-capabilities).

**Kubernetes/GKE, OpenSandbox, VMs:** Operator-selected compute/storage offers geographic control. It does not automatically localise observability, backups, support, package registries or model calls. Managed Alibaba AgentRun and self-operated OpenSandbox are separate offerings. No attested remote infrastructure benchmark was established here. [Kubernetes scope](../../providers/k8s_agent_sandbox/SPEC.md) · [OpenSandbox/AgentRun scope](../../providers/alibaba/SPEC.md).

## What the benchmark actually recorded

| Integration / setup | Retained location evidence | Interpretation |
| :--- | :--- | :--- |
| Modal `c6eceedf16a1` | `region: null` | Unpinned; resolved region unknown. |
| E2B `b8b64fa8b3ea` | No cluster/region retained | EU activation not established. |
| Blaxel `ed833ceba657` | Requested `us-pdx-1` | Oregon request, not EU-targeted. |
| AWS `a017dc2faa1b` | Requested `eu-north-1` | Stockholm request; wider data scope unverified. |
| Google `5a61c94c9323` | “CLI-configured; see preflight” | Campaign region unknown; preflight not retained. |
| Databricks SQL `629df7809d28` | No warehouse region/type retained | Workspace/warehouse region unknown. |
| Dedicated Databricks | API unavailable | No evaluated current placement evidence. |
| Daytona | Failed client prerequisite; incomplete placement record | No evaluated remote baseline. |
| Gemini | `gemini-2.5-flash`, no API branch/location retained | Model/tool route unknown. |
| OpenAI | Missing credentials | No working current region evidence. |

The separate **1 October Google reference probe names Milan**. It cannot establish the location of the separate **comparison campaign**. Requested configuration, returned inventory and independent provider placement attestation are different evidence strengths.

Sources: [Measured provenance gaps](findings.md#provenance-gaps-and-failed-prerequisites), provider `tested-configurations.md` files linked from each [specification](../../providers/README.md), and the [historical Google probe summary](../../providers/gcp_vertex/client-reference.md#historical-environment-probe).

## EU regulations: precise framing

**GDPR does not impose blanket EU-only hosting.** Controllers must use processors offering sufficient guarantees, establish appropriate processing contracts, implement risk-appropriate security and satisfy Chapter V for qualifying international transfers and onward transfers. EU-only can be a stricter customer, contractual or sector-specific requirement.

- **Article 28:** processor guarantees, processing instructions, contracts and subprocessor obligations.
- **Article 32:** confidentiality, integrity, availability and risk-appropriate security, restoration and testing.
- **Articles 44–46:** international-transfer conditions, including qualifying adequacy decisions and safeguards. Article 49 derogations are exceptional.
- **EDPB Guidelines 05/2021:** whether an international transfer occurs depends on disclosure/making data available between the relevant controllers/processors and a third-country/international-organisation importer. Third-country remote support can be a transfer while the disks stay in the EU. Foreign ownership alone does not establish a transfer.
- **EDPB Recommendations 01/2020:** Article 46 transfers may require destination-law/practice assessment and effective supplementary measures. A DPA, encryption option or region selector alone does not resolve that assessment.

Primary sources: [GDPR official text](https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng) · [EDPB Guidelines 05/2021, final v2](https://www.edpb.europa.eu/system/files/2023-02/edpb_guidelines_05-2021_interplay_between_the_application_of_art3-chapter_v_of_the_gdpr_v2_en_0.pdf) · [EDPB Recommendations 01/2020](https://www.edpb.europa.eu/our-work-tools/our-documents/recommendations/recommendations-012020-measures-supplement-transfer_en) · [EDPB international-transfer guide](https://www.edpb.europa.eu/sme-data-protection-guide/international-data-transfers_en).

## Evidence to collect in the next EU deployment trial

Pin the exact execution product, supported region/endpoint, image/class, storage and model route. Retain requested and resolved resource locations, data categories covered by commitments, log/snapshot/backup locations and retention, access/subprocessor terms, effective network controls and deletion evidence. Re-run the same output/workflow fixtures on that configuration. Only then compare timings and metered gross cost under the deployment you intend to use.
