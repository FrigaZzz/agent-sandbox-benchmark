"""Build a business-facing briefing from the retained evidence snapshot."""
from __future__ import annotations

import html
import json
import sys
from pathlib import Path
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from src.bench.evidence import load_evidence, summarize
from src.bench.portal import portal_html

OUT = Path(__file__).resolve().parent
SNAPSHOT = "2026-10-13"
NAMES = {"e2b": "E2B", "modal": "Modal", "gcp_vertex": "Google default code",
         "aws": "AWS AgentCore", "blaxel": "Blaxel", "databricks": "Databricks SQL"}


def svg(title, subtitle, rows, *, maximum=None, suffix="", dual=False):
    """Accessible, standalone infographic; exact values remain alongside bars."""
    maximum = maximum or max((r[1] for r in rows), default=1)
    body = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 650" role="img" aria-labelledby="title desc">',
            f'<title id="title">{html.escape(title)}</title><desc id="desc">{html.escape(subtitle)}</desc>',
            '<rect width="1200" height="650" fill="#faf7f0"/>',
            '<g font-family="system-ui,sans-serif" fill="#17272e">',
            f'<text x="40" y="60" font-size="36" font-weight="700">{html.escape(title)}</text>',
            f'<text x="40" y="105" font-size="22" fill="#59636a">{html.escape(subtitle)}</text>']
    for i, (label, value, note, inner) in enumerate(rows):
        y = 155 + i * 68
        body += [f'<text x="40" y="{y+22}" font-size="24">{html.escape(label)}</text>',
                 f'<rect x="305" y="{y}" width="{560*value/maximum:.2f}" height="26" fill="#006c67"/>']
        if dual:
            body += [f'<rect x="305" y="{y+28}" width="{560*inner/maximum:.2f}" height="8" fill="#b9472f"/>']
        body += [f'<text x="900" y="{y+21}" font-size="24" font-weight="650">{value:,.1f}{suffix}</text>',
                 f'<text x="900" y="{y+44}" font-size="17" fill="#59636a">{html.escape(note)}</text>']
    body += ['<text x="40" y="625" font-size="19" fill="#59636a">Specific setups / pilot cohorts · See linked raw evidence</text>', '</g></svg>']
    return "".join(body)


def diagram(title, rows):
    height = max(420, 130 + len(rows) * 77)
    body = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 {height}" role="img" aria-label="{html.escape(title, quote=True)}">',
            f'<rect width="1200" height="{height}" fill="#faf7f0"/><g font-family="system-ui,sans-serif" fill="#17272e">',
            f'<text x="40" y="65" font-size="36" font-weight="700">{html.escape(title)}</text>']
    for i, (label, text) in enumerate(rows):
        y = 130 + i * 77
        body += [f'<text x="40" y="{y}" font-size="28" fill="#006c67">{i+1:02d} / {html.escape(label)}</text>',
                 f'<text x="40" y="{y+31}" font-size="23">{html.escape(text)}</text>']
    return "".join(body + ['</g></svg>'])


def main():
    attempts, issues = load_evidence(ROOT / "reports")
    # Future campaigns never silently change this publication snapshot.
    attempts = [r for r in attempts if (r.get("started_at") or "")[:10] <= SNAPSHOT]
    summaries = summarize(attempts)
    selected = {}
    for provider in NAMES:
        for suite in ("cpu_stress", "output_fidelity", "artifact_roundtrip", "data_pipeline", "dependency_install", "session_state", "error_recovery"):
            rows = [r for r in summaries if r["provider"] == provider and r["suite"] == suite
                    and r["eligible"] and r["concurrency"] == 1 and r["runtime_kind"] == "remote_runtime"]
            if rows:
                selected[provider, suite] = max(rows, key=lambda r: r["last_measured_at"])
    def proof(provider, suite):
        row = selected.get((provider, suite))
        if not row:
            return "Not established"
        ref = row["run_refs"][0]
        url = "../index.html#raw?" + urlencode({"provider": provider, "run_id": ref["run_id"]})
        return f'<a href="{url}">{row["outcomes"].get("pass", 0)}/{row["n"]}</a>'
    output_rows = []
    for provider in ("e2b", "modal", "gcp_vertex", "aws", "blaxel"):
        row = selected.get((provider, "output_fidelity"))
        if row:
            runs = [r for r in attempts if r["run_id"] in {ref["run_id"] for ref in row["run_refs"]}]
            sizes = sorted({len(r.get("stdout", "").encode()) for r in runs})
            if len(sizes) != 1:
                raise ValueError("Output cohort sizes vary; update infographic labels rather than hide the range")
            output_rows.append((NAMES[provider], sizes[0], f'{row["outcomes"].get("pass", 0)}/{row["n"]} exact-output passes', 0))
    latency_rows = []
    for provider in sorted(NAMES, key=lambda p: selected.get((p, "cpu_stress"), {}).get("latency_ms", {}).get("p50") or float("inf")):
        row = selected.get((provider, "cpu_stress"))
        if row and row["latency_ms"]["p50"] is not None and row["workload_ms"]["p50"] is not None:
            latency_rows.append((NAMES[provider], row["latency_ms"]["p50"],
                f'guest {row["workload_ms"]["p50"]:.1f} ms; {row["outcomes"].get("pass", 0)}/{row["n"]} pass', row["workload_ms"]["p50"]))
    (OUT / "output.svg").write_text(svg("Did the agent receive the complete output?", "Expected: 131,072 UTF-8 bytes, including the final newline", output_rows, maximum=131072, suffix=" B"))
    (OUT / "latency.svg").write_text(svg("Same calculation. Different user-visible wait.", "Long bar: client lifecycle. Thin coral bar: guest calculation. Successful medians.", latency_rows, suffix=" ms", dual=True))
    cost_rows = [(f"{s} billed seconds", s * .000046, f"Model budget assumed: $0.003", 0) for s in (10, 180, 300)]
    # Dollars need five decimals, not the generic millisecond/byte formatter.
    cost = svg("The machine bill grows while the model budget stays fixed", "Scenario: E2B published default 2 vCPU / 4 GiB; $0.000046 per billed second", cost_rows)
    for _, value, _, _ in cost_rows:
        cost = cost.replace(f'>{value:,.1f}</text>', f'>${value:.5f}</text>', 1)
    cost = cost.replace("Specific setups / pilot cohorts · See linked raw evidence", "Hypothetical usage, not invoices · Excludes plan fees, storage, egress, retries and tax")
    (OUT / "cost.svg").write_text(cost)
    residency = [("Compute", "Where code runs and data is processed"), ("Stored copies", "Files, volumes, images, snapshots and backups"),
                 ("Logs / traces", "What stdout, stderr and telemetry retain"), ("Control plane", "Account data and lifecycle metadata"),
                 ("Support / subprocessors", "Who can access data, and from where"), ("Model / API calls", "Where the next service processes the payload")]
    (OUT / "residency.svg").write_text(diagram("One region selector. Six data surfaces.", residency))
    categories = [("Model-native", "Gemini / OpenAI: execute inside a model turn"), ("SQL execution", "Databricks python_exec: warehouse request and result"),
                  ("Workspace APIs", "E2B / Modal / Blaxel / Daytona: file and process control"), ("Enterprise cloud tools", "Google / AWS: cloud session, identity and policy"),
                  ("Self-operated fleets", "Kubernetes / OpenSandbox: own deployment and operations")]
    (OUT / "categories.svg").write_text(diagram("Five categories, chosen by operational control", categories))
    state = [("Across calls", "Write data.csv now; read it in the next live session call"), ("After stop/start", "Shut down compute; recover files from durable storage"),
             ("Memory resume", "Restore variables and processes, not just files")]
    (OUT / "state.svg").write_text(diagram("Files, disk and memory are different promises", state))
    suites = ["artifact_roundtrip", "data_pipeline", "dependency_install", "session_state", "error_recovery"]
    matrix = '<div class="table-wrap"><table><thead><tr><th>Tested path</th><th>Binary return</th><th>CSV pipeline</th><th>Offline wheel</th><th>Files across calls</th><th>Error recovery</th></tr></thead><tbody>'
    for p in ("e2b", "modal", "gcp_vertex"):
        matrix += f'<tr><th>{NAMES[p]}</th>' + ''.join(f'<td>{proof(p, s)}</td>' for s in suites) + '</tr>'
    matrix += '</tbody></table></div>'
    slides = [
        ("The complete job is what you buy", '<h1>Agent sandboxes:<br>choose for the job,<br>then count the bill.</h1><p class="lead">For PMs, engineering leads and architects choosing where an agent cleans data, edits files or runs tests.</p><div class="flow"><b>Model instructions</b><span>→</span><b>Machine work</b><span>→</span><b>Verified result</b></div>',
         'Snapshot: 975 retained attempts across different workloads; 12 provider specifications plus a local control. Pilot evidence, not an overall winner.'),
        ("Five categories, different jobs", '<img src="categories.svg" alt="Five operational categories with provider examples"><p>Dedicated Databricks is a workspace product, separate from SQL. Google/AWS runtime BYOC is separate from the interpreters measured here.</p>', 'Categories are operational ownership models, not a ranking of isolation strength.'),
        ("Which job are you building?", '<div class="jobs"><article><h3>Fix a repository</h3><p>Keep files across calls, run tests, recover after mistakes.</p><b>Trial candidates: E2B / Modal</b></article><article><h3>Clean a data export</h3><p>Upload bytes, compute checked totals, return an artifact.</p><b>E2B / Modal / Google default code</b></article><article><h3>Run a GPU workload</h3><p>Reserve a device, choose image, test interruptions and placement.</p><b>Documented options: Modal / Daytona</b></article><article><h3>Operate your own fleet</h3><p>Own routing, isolation, capacity, storage and cleanup.</p><b>Documented routes: K8s / OpenSandbox</b></article></div>', 'GPU and attested remote self-hosted configurations were not benchmarked. Model-native tools may fit a calculation inside a model turn; SQL tools may fit a warehouse query.'),
        ("Who completed the file workflows?", '<h2>A workflow shortlist,<br>with the checks beside it.</h2>' + matrix + '<p>E2B and Modal have positive evidence across these five operations. Google passed the first three through the tested one-shot path.</p>', 'Each linked cell is a separate recorded setup/cohort. Five passes are a pilot signal (Wilson 95% lower bound ≈56.6%), not an SLA. Google offline install: one uploaded pure-Python wheel into a private target.'),
        ("API success can return incomplete output", '<img src="output.svg" alt="E2B, Modal and Google exact output; AWS one byte missing; Blaxel logs truncated"><p><b>Why a PM should care:</b> clipped structured results can be unusable; byte-exact consumers can reject a missing newline. Check what reaches the caller.</p>', 'Known ordered Unicode output fixture. These findings describe stdout/log paths, not native file-size limits. No Git-patch failure was measured.'),
        ("What is the user waiting for?", '<img src="latency.svg" alt="Guest prime-calculation time compared with full client lifecycle"><p>The job finds 148,933 primes below two million. The caller also waits for initialization, staging, transport, collection and cleanup.</p>', 'AWS had the smallest observed full lifecycle median; Modal had the smallest guest median. Different hardware, regions and clients: not an equal-hardware race. Separate final teardown is excluded.'),
        ("Duration changes the cost mix", '<img src="cost.svg" alt="Compute costs $0.00046 at 10 seconds, $0.00828 at 180 seconds and $0.01380 at 300 seconds"><p>At 300 seconds the machine is <b>4.6×</b> the assumed $0.003 model budget. Substitute your actual model bill. Count idle wait, failed attempts and retained storage.</p>', 'Model-agnostic scenario using list rates, not measured invoices. Gross cost per verified completion = full campaign cost / completed tasks. Zero completions means no finite ratio.'),
        ("EU compute is one part of the map", '<img src="residency.svg" alt="Six residency surfaces: compute, stored copies, logs, control plane, support and model calls"><p><b>Example:</b> Modal documents EEA compute pinning with US logs/snapshots/managed durable storage. Daytona shared GPUs ignore geographic preference.</p>', 'GDPR does not impose blanket EU-only hosting. Contractual requirements may be stricter. EEA, EU-27, UK and Switzerland are distinct boundaries; other surfaces may remain unverified.'),
        ("What survives when compute stops?", '<img src="state.svg" alt="Live session files, durable disk and memory resume are separate contracts"><p>The pilot verified files across calls on E2B and Modal. Durable disk after stop and memory checkpoint/resume need their own trials.</p><p>Daytona GPU sandboxes are deleted on stop; external persistence needs an explicit plan.</p>', 'Choose the lifecycle contract before using pause/delete to save compute. A timeout response does not independently prove remote process termination.'),
        ("Inspect the evidence. Try your own job.", '<h2>Take the shortlist<br>to your own workload.</h2><p class="lead">Exact attempts, provider contracts and reproduction commands are in the repository companion.</p><div class="links"><a href="../index.html">Open raw evidence →</a><a href="../../readme.md">Repository guide →</a><a href="../../CONTRIBUTING.md">Run / contribute a cohort →</a><a href="../docs/eu-data-residency.md">Residency sources →</a></div><p>A public repository destination is not configured in this checkout. Add its reviewed release URL when publishing the article or attachment.</p>', 'No global vendor winner or invoice-backed cheapest-provider claim. Start with one real job, preserve failures and verify cleanup/cancellation.')]
    body = []
    for i, (title, content, note) in enumerate(slides):
        body.append(f'<section class="slide{ " active" if i == 0 else ""}" id="slide-{i+1}" aria-label="{html.escape(title, quote=True)}"><p class="eyebrow">{i+1:02d} / Executive field guide</p>'
                    + (f'<h2>{html.escape(title)}</h2>' if i not in (0, 3, 9) else '') + content
                    + f'<footer><p>{html.escape(note)}</p><a href="../docs/findings.md">Evidence / methods</a> · <a href="../docs/eu-data-residency.md">Residency sources</a> · <a href="https://e2b.dev/pricing">E2B rate source</a></footer></section>')
    template = (OUT / "template.html").read_text()
    (OUT / "index.html").write_text(portal_html(template.replace("__SLIDES__", "\n".join(body)), "../", "executive/index.html"))
    (OUT / "cohorts.json").write_text(json.dumps({"snapshot": SNAPSHOT, "issues": issues,
        "selected_cohorts": list(selected.values()), "model_budget_assumption_usd": .003,
        "compute_scenario_rate_usd_per_second": .000046}, indent=2))
    print(f"Built {len(slides)} executive slides, 6 SVG figures and inspectable cohort references")


if __name__ == "__main__":
    main()
