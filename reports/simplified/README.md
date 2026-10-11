# Cheaper AI. What about the machines?

Google's and Databricks' sandbox announcements prompted a fresh look at the author's side-project architecture, mainly around cost. More affordable AI capability can make larger jobs practical, while machine lifetime and infrastructure price pressures affect the bill. The comparison covers cost, privacy, features and customization.

Define the job's output, resources, duration, concurrency, network access and data boundary. Then ask what the execution environment promises at each stage of its life.

Snapshot.

## The short package

- [Nine-page PDF carousel](agent-sandbox-decisions.pdf): the reader-facing summary, portrait 4:5, searchable text and clickable official references.
- [Readable slide transcript](slides.md): the same slide text without the visual layout.
- [Source register and cost arithmetic](sources.md): claim-by-claim evidence, historical pricing context, live rates and exclusions.

The PDF covers nine topics: the cost question, sandbox news, persistence, software/hardware choices, data geography, capability versus infrastructure economics, a worked cost example, the five-question checklist and benchmark takeaways. News, Theo's discussion and market sources are linked in the [source register](sources.md).

## Five questions worth asking before you pick

### 1. What survives between calls, after a stop, and on resume?

Files inside a running session, disk retained after a stop, and restored memory are separate contracts. State what you need: input files, installed dependencies, variables, running processes or durable outputs. Check retention and deletion as well as resume behaviour.

The recorded E2B and Modal fixtures verified files across calls and recovery after an exception. They did not test stop/resume or restored memory. E2B documents filesystem and memory preservation on its default pause path; filesystem-only options have a different contract.

### 2. Does a custom image also reserve a GPU?

It doesn't. An image supplies software. The runtime separately allocates hardware. E2B has templates but documents CPU-only sandboxes. Modal documents explicit GPU allocation with gVisor and preemption. Daytona's shared GPU placement ignores geographic preference.

Pin the actual product/API, image, resource request, runtime class, network rules and placement. GPU, advanced custom-image and resume configurations were not exercised by this pilot.

### 3. Where do logs, backups and model calls live?

An EU compute region does not establish the location of the whole data flow. Map input/output storage, snapshots and backups, logs, control-plane data, support access and external/model calls separately. EU, EEA and wider Europe describe different geographic boundaries.

Modal provides a concrete documented example: compute can be pinned to the EEA, while stdout/stderr logs, explicitly created sandbox snapshots and managed durable storage reside in the US. Model processing follows the separately chosen model endpoint. This is a data-flow question; it does not establish a blanket legal conclusion or describe every provider.

### 4. What happens when a request times out?

Distinguish the caller's deadline, the remote process lifetime and the session's lifetime. Poll for process termination, look for late writes or other side effects, and try useful work in the same session. Decide whether retrying the job can duplicate effects.

This pilot checked timeout responses, not independent process death. It also found output-path defects: the AWS Code Interpreter stdout path omitted the final newline and the Blaxel process-log path truncated output. Each observation repeated five times in the cited cohort. They are integration-path findings, not general file API limits.

### 5. What's the cost per verified completion, with credits kept apart?

```text
gross campaign cost = all model + execution + billed setup/idle usage
                    + storage + network + plan/fleet costs attributable to the job
                    (including failed attempts and retries)

cost per verified completion = gross campaign cost / verified completed tasks
```

Keep gross usage value, discounts, applied credits and cash paid in separate fields. A zero-completion campaign has no finite cost-per-completion value. Operator effort is an additional consideration when running your own fleet.

The denominator needs an output check: exact files or hashes, valid totals, passing tests or the job's own acceptance condition. An API success alone is insufficient. No invoice-backed cheapest-provider conclusion is established here.

## Scope changes the shortlist

| Workload | What to specify before choosing | Evidence in this repository |
| :--- | :--- | :--- |
| File/data processing | Input/output size, CPU/RAM, data location, verified artifact | Binary round trip, 10k-row CSV pipeline, 20k-row SQLite fixture |
| Code edit/test | Shell, dependencies, egress, toolchain, bounded test run | Synthetic two-file CSV-parser fix with four assertions; one offline pure-Python wheel |
| Iterative workspace | Repeated calls, file state, failures, disk/memory lifetime | Cross-call files and exception recovery; stop/resume remains untested |
| GPU/heavy computation | Explicit device, resource limits, capacity, region, interruption handling | Documented options only; no GPU campaign measured |

E2B, Modal and Google's default code integration passed the checked binary, data-pipeline and offline-wheel fixtures in their cited setups. That is useful CPU-workflow evidence. It does not establish production reliability, internet package access, native builds, equivalent hardware or a universal winner.

## Go deeper

- [Technical report](../docs/detailed-report.md): configuration-specific findings and limits.
- [Measured findings](../docs/findings.md): exact attempt references and output/deadline observations.
- [Evidence dashboard](../index.html): raw checks, setup comparisons and retained attempts.
- [EU data-surface guide](../docs/eu-data-residency.md): geographic scope, retention and provider/legal sources.
- [Methods](../docs/evaluation-framework.md): fixtures, verification and next experiments.
- [Decision explorer](../variant/index.html): requirement filtering and hypothetical scenario estimates.
- [Provider specifications](../../providers/README.md): product contracts and tested settings.

The repository and article resource cards in the PDF use supplied public URLs when available. Until then, the PDF directs readers to the accompanying post. No deployment URL is inferred.

## Rebuild

With the repository's presentation dependencies installed:

```sh
python reports/simplified/build_carousel.py
python reports/simplified/verify_carousel.py
```

Once public destinations exist:

```sh
python reports/simplified/build_carousel.py \
  --github-url "https://github.com/OWNER/REPOSITORY" \
  --medium-url "https://medium.com/@AUTHOR/ARTICLE"
```

The source is [build_carousel.py](build_carousel.py). It generates the PDF, transcript, nine page previews, contact sheet and bounded export checks. Text is vector-based and selectable; the export checks reject text overflow and off-page text. Visual review remains necessary.

The verifier checks PDF links, text placement and cost arithmetic.
