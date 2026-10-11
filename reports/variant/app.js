/* Embedded by build_variant.py: no network dependencies; source values are untrusted text. */
"use strict";
const D = JSON.parse(document.getElementById("evidence-data").textContent);
const $ = s => document.querySelector(s);
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const fmt = n => n == null ? "—" : Number(n).toLocaleString(undefined, {maximumFractionDigits: 1});
const money = n => n == null ? "Unknown" : "$" + Number(n).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2});
const percent = n => n == null ? "—" : (100 * n).toFixed(1) + "%";
const label = s => s.replace(/_/g, " ");
const badge = (text, cls = "") => `<span class="badge ${esc(cls)}">${esc(text)}</span>`;
const defaults = {
  jobs: 10000, duration: 60, reuse: 20, idle: 30, attempts: 1.05,
  vcpu: 2, memory: 4, low: 0.8, high: 1.5, "cpu-use": 100, "mem-use": 100,
  storage: 0, plan: 0, "input-tokens": 1000, "output-tokens": 500, extras: 0, credits: 0,
};
const state = {
  workloads: new Set(["code_exec"]), requirements: new Set(), surfaces: new Set(),
  family: "remote_runtime", workers: 1, priority: "correctness", controls: false,
  scenario: {...defaults, "session-mode": "fresh"}, compare: new Set(["e2b", "modal", "gcp_vertex"]),
  matrixCandidates: true, sort: "bucket", sortAsc: true,
};
let results = [];

function profile() {
  const tasks = new Map(), required = new Set(state.requirements);
  for (const job of D.workloads.filter(w => state.workloads.has(w.id))) {
    for (const f of job.features || []) required.add(f);
    for (const suite of job.suites) {
      const workers = job.concurrency || state.workers;
      tasks.set(suite + "@" + workers, {suite, workers});
    }
  }
  return {tasks: [...tasks.values()], required: [...required]};
}

function cohortFor(p, task) {
  const rows = (p.measured.suites[task.suite] || []).filter(c => c.eligible && c.concurrency === task.workers &&
    (state.family === "all" || c.runtime_kind === state.family));
  // More than one configuration/version is a decision to make, not a mean to calculate.
  return {row: rows.length === 1 ? rows[0] : null, ambiguous: rows.length > 1, rows};
}

function rate(p, text) {
  return p.cost_model.rates.find(r => r.resource.toLowerCase().includes(text.toLowerCase()));
}

function costScenario(p) {
  const cm = p.cost_model, s = state.scenario;
  const attempts = Math.ceil(s.jobs * s.attempts);
  const batch = s["session-mode"] === "reuse" ? s.reuse : 1;
  const sessions = Math.ceil(attempts / batch);
  const missing = [], notes = [], feasibility = [];
  const allocated = cm.billing !== "consumed";
  const gb = s.memory * 2 ** 30 / 1e9;
  const billingMemory = cm.memory_unit === "GB" ? gb : s.memory;
  const cpuFraction = allocated ? 1 : s["cpu-use"] / 100;
  const memoryFraction = allocated ? 1 : s["mem-use"] / 100;
  const monthlyPlan = p.id === "e2b" ? s.plan : 0;
  if (s["session-mode"] === "reuse" && p.features.session_reuse?.support !== "supported") {
    feasibility.push("Reused-session eligibility is not established for this route.");
  }
  if (cm.per_vcpu_hour != null && p.features.cpu_sizing?.support !== "supported") {
    feasibility.push("CPU reference is illustrative: caller-selectable sizing is conditional or unavailable.");
  }
  if (cm.per_gib_hour != null && p.features.memory_sizing?.support !== "supported") {
    feasibility.push("Memory reference is illustrative: requested allocation needs validation.");
  }
  if (p.id === "blaxel") feasibility.push("CPU follows the memory tier; an independent vCPU request is not established.");
  if (p.id === "modal") notes.push(`${fmt(s.vcpu / 2)} physical-core equivalent; this is a pricing conversion, not a hardware guarantee.`);
  if (cm.memory_unit === "GB") notes.push(`${fmt(s.memory)} GiB is ${fmt(gb)} decimal GB for the memory-rate calculation.`);
  if (p.id === "aws") notes.push(`Consumed CPU ${s["cpu-use"]}%; peak memory ${s["mem-use"]}%, with listed 128 MB memory / 1-second session minima. Actual metering and system overhead remain unknown.`);
  const runtimeLimit = p.id === "e2b" ? (s.plan === 0 ? 3600 : 86400) : null;
  if (runtimeLimit && (s.duration * batch + s.idle) * s.high > runtimeLimit) {
    feasibility.push("Reference session exceeds this E2B plan's documented continuous-runtime cap.");
  }
  if (p.id === "e2b" && state.surfaces.has("compute") && s.plan < 150) {
    feasibility.push("The shared EU route needs Pro or above plus support activation; Hobby does not cover that route.");
  }

  let storageCost = 0;
  if (s.storage > 0) {
    if (p.id === "blaxel") {
      storageCost = s.storage * 2 ** 30 / 1e9 * rate(p, "Persistent Volume provisioned").amount;
      notes.push("Storage uses the published provisioned-volume SKU; snapshots and images are separate.");
    } else if (p.id === "daytona") {
      storageCost = Math.max(0, s.storage - 5) * 730 * rate(p, "Storage").amount;
      notes.push("Storage assumes a 730-hour month and the listed first-5-GiB allowance for one storage allocation; confirm its scope.");
    } else {
      missing.push("Retained-storage price / applicable allocation not established; full total is unknown.");
    }
  }
  const computed = [];
  let components = null;
  for (const multiplier of [s.low, 1, s.high]) {
    const seconds = attempts * s.duration * multiplier + sessions * s.idle;
    let compute = null, tokens = 0;
    if (cm.per_vcpu_hour != null || cm.per_gib_hour != null) {
      // AWS consumption fractions apply to the assumed metered reference only.
      const meteredMemory = allocated ? billingMemory : Math.max(0.128, billingMemory * memoryFraction);
      const billedSeconds = allocated ? seconds : Math.max(seconds, sessions);
      compute = billedSeconds / 3600 * ((cm.per_vcpu_hour || 0) * s.vcpu * cpuFraction +
        (cm.per_gib_hour || 0) * meteredMemory);
    } else if (cm.special?.kind === "beta_zero") {
      compute = 0;
      notes.push("Current no-charge Beta only; future Sandbox rates are unresolved.");
      feasibility.push("Dedicated Sandbox is fixed at documented 4 vCPU / 8 GB; the entered shape is not configurable.");
    } else if (cm.special?.kind === "session_fee") {
      // Each batch is billed in 20-minute blocks; charge the final partial batch separately.
      const tier = cm.special.sessions.find(t => parseFloat(t.container) >= gb);
      if (tier) {
        const full = Math.floor(attempts / batch), remainder = attempts % batch;
        const blocks = (n) => Math.max(1, Math.ceil((n * s.duration * multiplier + s.idle) / 1200));
        compute = (full * blocks(batch) + (remainder ? blocks(remainder) : 0)) * tier.usd_per_20min;
        const input = rate(p, "gpt-4o Standard input"), output = rate(p, "gpt-4o Standard output");
        tokens = attempts * (s["input-tokens"] * input.amount + s["output-tokens"] * output.amount) / 1e6;
        notes.push(`Uses ${tier.container} container blocks + gpt-4o Standard token example; current product is separate from the failed legacy adapter.`);
        feasibility.push("Container session shape differs from a caller-sized sandbox. Confirm endpoint and model eligibility.");
      } else missing.push("Memory exceeds the largest listed container tier.");
    } else if (cm.special?.kind === "token_only") {
      compute = 0;
      tokens = attempts * (s["input-tokens"] * cm.special.example.usd_per_1m_input +
        s["output-tokens"] * cm.special.example.usd_per_1m_output) / 1e6;
      notes.push(`Uses ${cm.special.example.model} token example; iterative context and thinking must be included in your token assumption.`);
      feasibility.push("Model tool is fixed-runtime; entered vCPU and memory do not select its allocation.");
    }
    if (compute == null) {
      computed.push(null);
      missing.push(cm.special?.reason || "No applicable compute rate established.");
    } else {
      computed.push(compute + tokens + storageCost + monthlyPlan + s.extras);
      if (multiplier === 1) components = {compute, tokens, storage: storageCost, plan: monthlyPlan, extras: s.extras};
    }
  }
  notes.push("GPU/egress/ancillary services are excluded unless entered as other known charges. No invoice-backed task cost is available.");
  const partial = missing.length > 0;
  return {
    low: partial ? null : computed[0], base: partial ? null : computed[1], high: partial ? null : computed[2],
    knownBase: computed[1], components, cash: !partial && computed[1] != null ? Math.max(0, computed[1] - s.credits) : null,
    missing: [...new Set(missing)], notes: [...new Set(notes)], feasibility: [...new Set(feasibility)],
    sessions, attempts, comparable: !partial && computed[1] != null && feasibility.length === 0,
  };
}

function assess(p) {
  const pr = profile(), conflicts = [], unresolved = [], supported = [];
  for (const id of pr.required) {
    const f = p.features[id];
    const name = D.feature_labels[id];
    if (f?.support === "unsupported") conflicts.push(`${name}: documented unsupported.`);
    else if (f?.support === "supported") supported.push(name);
    else unresolved.push(`${name}: ${f?.support || "unknown"} — validate the intended configuration.`);
  }
  if (p.unattested && !state.controls) conflicts.push("Control / deployment-unattested route: enable investigation to include it.");
  if (state.family !== "all" && p.deployment === "model_mediated" && state.family !== "model_mediated") {
    conflicts.push("Model-mediated interface differs from the chosen direct-execution family.");
  }
  if (state.family === "model_mediated" && p.deployment !== "model_mediated") conflicts.push("Different interface family.");
  for (const id of state.surfaces) {
    const s = p.eu.surfaces[id];
    if (s.state === "conflict") conflicts.push(`${D.residency_surfaces[id]}: ${s.note}`);
    else unresolved.push(`EU-only ${D.residency_surfaces[id]}: ${s.note}`);
  }
  if (state.requirements.has("gpu") && state.surfaces.has("compute") && p.id === "daytona") {
    conflicts.push("Shared GPU placement uses earth and ignores geographic preference; a dedicated/custom region needs separate evidence.");
  }
  const taskRows = pr.tasks.map(t => ({...t, ...cohortFor(p, t)}));
  const present = taskRows.filter(t => t.row), missing = taskRows.filter(t => !t.row);
  for (const t of missing) unresolved.push(`${label(t.suite)} (${t.workers} worker): ${t.ambiguous ? "multiple configuration/version cohorts; select and reproduce one" : "no eligible cohort in this context"}.`);
  const failures = present.filter(t => (t.row.outcomes.fail || 0) > 0);
  const issues = D.insights.filter(i => i.provider === p.id && i.category === "failure" &&
    present.some(t => t.suite === i.suite && t.row.config_id === i.config_id && t.row.concurrency === i.concurrency));
  if (failures.length) unresolved.push("Reproduce the failed task path before deployment.");
  if (p.prerequisite_failure) unresolved.push("Working baseline unavailable: " + p.prerequisite_failure);
  if (!pr.tasks.length) unresolved.push("Choose a job to establish task-specific evidence.");
  if (p.unattested && state.controls) unresolved.push("Deployment attestation is missing; controls are investigation routes only.");
  const cost = costScenario(p);
  if (state.priority === "cost" && !cost.comparable) {
    unresolved.push("Cost priority cannot be resolved: scenario pricing or shape eligibility remains incomplete.");
  }
  if (state.priority === "speed" && present.some(t => t.row.latency_ms.p50 == null)) {
    unresolved.push("Successful-task latency is unavailable for a required cohort.");
  }
  const bucket = conflicts.length ? "conflict" : unresolved.length ? "validate" : "measured";
  const signature = present.length === pr.tasks.length && present.length ? present.map(t => t.row.comparison_key).sort().join(";") : null;
  const smallestSample = present.length ? Math.min(...present.map(t => t.row.n)) : null;
  const weakestLower = present.length ? Math.min(...present.map(t => t.row.success_ci95[0])) : null;
  return {p, bucket, conflicts, unresolved, supported, taskRows, present, missing, issues, failures, cost,
    signature, smallestSample, weakestLower, coverage: present.length, taskCount: pr.tasks.length};
}

function orderGroup(group, priority) {
  const anchors = new Map();
  for (const e of group) for (const t of e.present) {
    const value = t.row.latency_ms.p50;
    if (value != null && value > 0) anchors.set(t.row.comparison_key, Math.min(value, anchors.get(t.row.comparison_key) ?? Infinity));
  }
  // Relative ratios compare the same set of tasks; no milliseconds are averaged across tasks.
  const speedIndex = e => {
    const ratios = e.present.map(t => t.row.latency_ms.p50 / anchors.get(t.row.comparison_key));
    return ratios.every(Number.isFinite) && ratios.length ? Math.exp(ratios.reduce((sum, r) => sum + Math.log(r), 0) / ratios.length) : Infinity;
  };
  return group.slice().sort((a, b) => {
    let delta;
    if (priority === "speed") delta = speedIndex(a) - speedIndex(b);
    else if (priority === "cost") delta = (a.cost.comparable ? a.cost.base : Infinity) - (b.cost.comparable ? b.cost.base : Infinity);
    else delta = (b.weakestLower ?? -1) - (a.weakestLower ?? -1);
    return (Number.isFinite(delta) ? delta : 0) || a.p.name.localeCompare(b.p.name);
  });
}

function allResults() {
  return D.provider_order.map(id => assess(D.providers[id]));
}
function groupsFor(evals) {
  const groups = new Map();
  for (const e of evals.filter(e => e.bucket === "measured")) {
    if (!groups.has(e.signature)) groups.set(e.signature, []);
    groups.get(e.signature).push(e);
  }
  return [...groups.values()];
}

function nextCheck(e) {
  if (e.conflicts.length) return e.conflicts[0];
  if (e.issues.length) return e.issues[0].implication;
  if (e.missing.length) return `Run ${label(e.missing[0].suite)} with ${e.missing[0].workers} worker(s), retained setup/evaluator hashes and an independent oracle.`;
  if (e.unresolved.length) return e.unresolved[0];
  return "Reproduce the pinned setup with your payload; collect larger repeated samples, provider deletion-status proof and metered gross cost per verified completion.";
}
function cohortLink(c, text = "Exact attempts") {return `<a href="${esc(c.evidence_url)}">${esc(text)}</a>`;}
function requirementList(e) {
  return `<ul class="requirements">${e.supported.map(x => `<li>${badge("Supported", "supported")} ${esc(x)}</li>`).join("")}${e.unresolved.map(x => `<li>${badge("Unresolved", "unknown")} ${esc(x)}</li>`).join("")}${e.conflicts.map(x => `<li>${badge("Conflict", "conflict")} ${esc(x)}</li>`).join("")}</ul>`;
}
function taskTable(e) {
  return `<div class="tablewrap"><table><thead><tr><th>Required operation</th><th>Passed / evaluated</th><th>95% success interval</th><th>Successful lifecycle p50 / p95</th></tr></thead><tbody>${e.taskRows.map(t => {
    const c = t.row;
    return `<tr><td>${esc(label(t.suite))} · ${t.workers} worker(s)</td>${c ? `<td>${c.outcomes.pass || 0}/${c.n}</td><td>${percent(c.success_ci95[0])}–${percent(c.success_ci95[1])}</td><td>${fmt(c.latency_ms.p50)} / ${fmt(c.latency_ms.p95)} ms<br>${cohortLink(c)}</td>` : '<td colspan="3">' + (t.ambiguous ? 'Ambiguous configuration/version' : 'Not measured in selected context') + '</td>'}</tr>`;
  }).join("")}</tbody></table></div>`;
}
function setupDetails(e) {
  return e.present.map(t => {
    const c = t.row;
    return `<details><summary>${esc(label(t.suite))}: setup ${esc(c.config_id)} · ${c.concurrency} worker(s)</summary><p class="mono">${esc(JSON.stringify(c.configuration.requested))}</p><p class="small">Runtime ${esc(c.runtime_kind)}; client ${esc(c.client_os)} / ${esc(c.client_arch)}; n=${c.n}. p95 is descriptive${c.n < 100 ? "; fewer than 100 attempts" : ""}.</p><p class="mono">Workload ${esc(c.workload_sha256)}<br>Evaluator ${esc(c.evaluation_contract_sha256)}<br>Adapter ${esc(c.adapter_sha256)}<br>Stack ${esc(c.stack_sha256)}</p>${cohortLink(c)} ${c.reports.map(r => `<a href="../${esc(r)}">Report JSON</a>`).join(" · ")}</details>`;
  }).join("");
}
function cardHtml(e) {
  const title = {measured: "Measured candidate", validate: "Needs validation", conflict: "Set aside"}[e.bucket];
  const weak = e.smallestSample == null ? "No matching cohort" : `Smallest task sample: n=${e.smallestSample}`;
  return `<article class="card" data-provider="${esc(e.p.id)}"><div class="result-head"><div><h3>${esc(e.p.name)}</h3><div class="small">${esc(e.p.role)}</div></div>${badge(title, e.bucket === "measured" ? "supported" : e.bucket)}</div>
    <p class="small">${e.coverage}/${e.taskCount} required operations measured in this context. ${esc(weak)}. ${e.p.raw_attempts_retained} raw attempts retained across versions.</p>
    <p class="provider-note"><b>Why investigate:</b> ${e.bucket === "measured" ? "All chosen task cohorts passed their recorded checks; required capabilities have documented support." : e.coverage ? "Some required operations have measured evidence; gaps below prevent a complete recommendation." : "Documentation suggests an investigation route, but your selected task has no complete eligible evidence."}</p>
    ${taskTable(e)}
    ${e.issues.map(i => `<div class="notice danger"><b>${esc(i.title)}</b><br>${esc(i.finding)}<br><span class="small">${esc(i.boundary)}</span></div>`).join("")}
    ${requirementList(e)}
    <p class="provider-note"><b>Cost scenario:</b> ${money(e.cost.base)} gross base${e.cost.base == null && e.cost.knownBase != null ? `; ${money(e.cost.knownBase)} known subtotal` : ""}. ${e.cost.feasibility.length ? "Shape/session eligibility needs validation." : "Published-rate assumption only."}</p>
    <p class="provider-note"><b>Next check:</b> ${esc(nextCheck(e))}</p>
    <div class="linkrow"><a href="${esc(e.p.spec_url)}">Product specification</a><a href="${esc(e.p.eu.source)}">Residency scope</a></div>
    <details class="panel-details"><summary>Setup fingerprints, source qualification and pricing</summary>${setupDetails(e)}<p class="small">${esc(e.p.customization_summary)}</p><p class="small">${esc(e.p.pricing_limitations)}</p>${e.cost.notes.concat(e.cost.missing, e.cost.feasibility).map(n => `<p class="small">${esc(n)}</p>`).join("")}</details>
    <label class="check compare-picker"><input type="checkbox" data-compare="${esc(e.p.id)}" ${state.compare.has(e.p.id) ? "checked" : ""}>Compare side by side</label></article>`;
}

function renderCandidates() {
  const groups = groupsFor(results);
  const measured = results.filter(e => e.bucket === "measured"), validation = results.filter(e => e.bucket === "validate"), conflicts = results.filter(e => e.bucket === "conflict");
  const reruns = results.filter(e => e.p.unranked_cohorts.length);
  $("#result-status").textContent = `${measured.length} measured candidate(s), ${validation.length} validation route(s), ${conflicts.length} set aside; ${reruns.length} unranked endpoint route(s) have visible rerun evidence below. ${state.priority === "cost" ? "Cost is a scenario assumption, never a measured cost-per-task result." : "No composite confidence or capability scores."}`;
  let html = "";
  groups.forEach((g, i) => {
    const ordered = orderGroup(g, state.priority);
    html += `<h3 class="group">Measured comparison group ${i + 1} · ${esc(g[0].present[0].row.runtime_kind)}${g.length === 1 ? " · one candidate, no head-to-head ranking" : ""}</h3><p class="hint">Same required task/evaluator identities, worker count and client platform. Ordering: ${esc(state.priority)}. Hardware and regions differ; inspect setup fingerprints.</p><div class="results">${ordered.map(cardHtml).join("")}</div>`;
  });
  if (!measured.length) html += `<div class="empty">No complete measured recommendation for these requirements. Review validation routes and their next experiments below.</div>`;
  if (reruns.length) html += `<h3 class="group">Rerun evidence · unranked endpoint observations</h3><p class="hint">These results are always visible. The runtime is recorded as deployment-unattested, so endpoint timings are not treated as verified cloud-provider performance. Earlier and rerun configurations remain separate.</p><div class="results">${reruns.map(unrankedCard).join("")}</div>`;
  if (validation.length) html += `<h3 class="group">Candidates needing validation</h3><div class="results">${validation.map(cardHtml).join("")}</div>`;
  if (conflicts.length) html += `<details class="panel-details"><summary>Set aside (${conflicts.length}) — inspect reasons</summary><ul>${conflicts.map(e => `<li><b>${esc(e.p.name)}</b>: ${e.conflicts.map(esc).join(" ")}</li>`).join("")}</ul></details>`;
  $("#candidates").innerHTML = html;
  $("#candidates").querySelectorAll("[data-compare]").forEach(el => el.addEventListener("change", () => {
    if (el.checked && state.compare.size >= 3) {el.checked = false; $("#result-status").textContent = "Select up to three systems. Uncheck one first."; return;}
    el.checked ? state.compare.add(el.dataset.compare) : state.compare.delete(el.dataset.compare);
    renderCompare(); renderDecision();
  }));
  const sensitivity = ["correctness", "speed", "cost"].map(priority => {
    const items = groups.map(g => {
      const eligible = priority === "cost" ? g.filter(e => e.cost.comparable) : g.filter(e => e.present.every(t => priority !== "speed" || t.row.latency_ms.p50 != null));
      const tie = priority === "correctness" && eligible.length > 1 && eligible.every(e => e.weakestLower === eligible[0].weakestLower);
      return eligible.length ? orderGroup(eligible, priority).map(e => esc(e.p.name)).join(tie ? " · " : " → ") +
        (tie ? "<br>Equal lower bounds; alphabetical display, no winner inferred." : "") : "No complete input for this group";
    });
    return `<div><h3>${esc(label(priority))} first</h3><p class="small">${items.length ? items.join("<br>") : "No measured comparison group"}</p></div>`;
  });
  $("#sensitivity").innerHTML = sensitivity.join("");
}

function unrankedCard(e) {
  const cohorts = e.p.unranked_cohorts.slice().sort((a, b) => b.last_measured_at.localeCompare(a.last_measured_at));
  const latest = cohorts[0];
  const wanted = new Set(profile().tasks.map(t => t.suite));
  const latestRows = cohorts.filter(c => c.config_id === latest.config_id && c.adapter_sha256 === latest.adapter_sha256 && c.stack_sha256 === latest.stack_sha256)
    .sort((a, b) => Number(wanted.has(b.suite)) - Number(wanted.has(a.suite)) || a.suite.localeCompare(b.suite));
  const passed = latestRows.reduce((sum, c) => sum + (c.outcomes.pass || 0), 0);
  const evaluated = latestRows.reduce((sum, c) => sum + c.n, 0);
  const unknown = latestRows.reduce((sum, c) => sum + (c.outcomes.unknown || 0) + (c.outcomes.skipped || 0), 0);
  const cohortRows = rows => rows.map(c => `<tr><td>${esc(label(c.suite))}<br><span class="small">${c.concurrency} worker(s)</span></td><td>${c.n ? `${c.outcomes.pass || 0}/${c.n}` : "Not evaluated"}${c.outcomes.unknown ? `<br>${c.outcomes.unknown} unvalidated` : ""}</td><td>${c.success_ci95 ? percent(c.success_ci95[0]) + "–" + percent(c.success_ci95[1]) : "—"}</td><td>${fmt(c.latency_ms.p50)} / ${fmt(c.latency_ms.p95)} ms</td></tr>`).join("");
  const table = rows => `<div class="tablewrap"><table><thead><tr><th>Operation</th><th>Passed / evaluated</th><th>Success 95% interval</th><th>Successful lifecycle p50 / p95</th></tr></thead><tbody>${cohortRows(rows)}</tbody></table></div>`;
  return `<article class="card" data-unranked-provider="${esc(e.p.id)}"><div class="result-head"><h3>${esc(e.p.name)}</h3>${badge("Unranked rerun evidence", "validate")}</div>
    <p class="small">${e.p.raw_attempts_retained} retained attempts across configurations. Latest observed setup: <span class="mono">${esc(latest.config_id)}</span> (${esc(latest.configuration.label || "unlabelled")}); ${esc(latest.last_measured_at)}.</p>
    <p class="provider-note"><b>Latest setup coverage:</b> ${passed}/${evaluated} evaluated attempts passed across ${latestRows.filter(c => c.n > 0).length} evaluated operations. ${latestRows.length} operation cohorts retained${unknown ? `; ${unknown} additional unvalidated/skipped observations` : ""}. These totals describe coverage, not pooled reliability.</p>
    <div class="notice warning">Recorded runtime: ${esc(latest.runtime_kind)}. Per-operation samples and setup identities are retained below. Endpoint/deployment attestation and published managed-product pricing remain unresolved.</div>
    ${table(latestRows)}
    <p class="small"><b>Requested setup:</b> <span class="mono">${esc(JSON.stringify(latest.configuration.requested))}</span></p>
    <p class="provider-note"><b>Next check:</b> Establish the exact deployment/backend, retain placement and isolation evidence, then collect at least five evaluated attempts per operation with the same setup and evaluator. Do not infer a managed AgentRun bill from a self-hosted endpoint.</p>
    <details class="panel-details"><summary>All retained endpoint cohorts and exact attempt links</summary>${cohorts.map(c => `<details><summary>${esc(label(c.suite))} · ${esc(c.configuration.label || "unlabelled")} · ${esc(c.config_id)} · n=${c.n}</summary>${table([c])}<p class="mono">Workload ${esc(c.workload_sha256)}<br>Evaluator ${esc(c.evaluation_contract_sha256)}<br>Adapter ${esc(c.adapter_sha256)}<br>Stack ${esc(c.stack_sha256)}</p>${c.run_refs.map(r => `<a href="../index.html#raw?provider=${encodeURIComponent(e.p.id)}&amp;run_id=${encodeURIComponent(r.run_id)}">${esc(r.run_id)}</a>`).join(" · ")}</details>`).join("")}</details>
    <div class="linkrow"><a href="${esc(e.p.spec_url)}">Product specification</a><a href="../../providers/${esc(e.p.id)}/tested-configurations.md">Tested configurations</a></div></article>`;
}

function renderCompare() {
  const selected = [...state.compare].map(id => results.find(e => e.p.id === id)).filter(Boolean);
  if (!selected.length) {$("#side-by-side").innerHTML = '<p class="empty">Select up to three systems on their cards.</p>';}
  else {
    const sameGroup = selected.every(e => e.signature && e.signature === selected[0].signature);
    const rows = [
      ["Decision state", e => badge(e.bucket, e.bucket)],
      ["Required task evidence", e => `${e.coverage}/${e.taskCount} operations; smallest n=${e.smallestSample ?? "—"}`],
      ["Task counts & timing", e => e.present.map(t => `${esc(label(t.suite))}: ${t.row.outcomes.pass || 0}/${t.row.n}; p50 ${fmt(t.row.latency_ms.p50)} ms; CI ${percent(t.row.success_ci95[0])}–${percent(t.row.success_ci95[1])}; ${cohortLink(t.row)}`).join("<br>") || "None"],
      ["Requirement gaps", e => e.unresolved.concat(e.conflicts).map(esc).join("<br>") || "None documented for this selection"],
      ["Failures to reproduce", e => e.issues.map(i => esc(i.finding)).join("<br>") || (e.failures.length ? "Failed checks in a selected cohort" : "No observed failures in matching cohorts; not an SLA")],
      ["Gross cost scenario", e => `${money(e.cost.low)} / ${money(e.cost.base)} / ${money(e.cost.high)}<br>${e.cost.feasibility.map(esc).join("<br>")}`],
      ["Next experiment", e => esc(nextCheck(e))],
    ];
    $("#side-by-side").innerHTML = `<div class="notice ${sameGroup ? "" : "warning"}">${sameGroup ? "Selected systems share the required comparison identities. Hardware/geography are still not equalised." : "These systems do not share a complete comparison context; no cross-system latency or reliability winner is inferred."}</div><div class="tablewrap"><table><thead><tr><th>Decision dimension</th>${selected.map(e => `<th>${esc(e.p.name)}<br><button data-remove="${esc(e.p.id)}" aria-label="Remove ${esc(e.p.name)} from comparison">Remove</button></th>`).join("")}</tr></thead><tbody>${rows.map(([name, value]) => `<tr><th scope="row">${name}</th>${selected.map(e => `<td>${value(e)}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`;
    $("#side-by-side").querySelectorAll('[data-remove]').forEach(button => button.addEventListener('click', () => {
      state.compare.delete(button.dataset.remove);
      renderCandidates(); renderCompare(); renderDecision();
    }));
  }
  const rank = {measured: 0, validate: 1, conflict: 2};
  const sorted = results.slice().sort((a, b) => {
    const key = state.sort;
    const delta = key === "name" ? a.p.name.localeCompare(b.p.name) : key === "coverage" ? a.coverage - b.coverage : rank[a.bucket] - rank[b.bucket];
    return (state.sortAsc ? delta : -delta) || a.p.name.localeCompare(b.p.name);
  });
  $("#summary-table tbody").innerHTML = sorted.map(e => {
    const p50s = e.present.map(t => t.row.latency_ms.p50).filter(n => n != null);
    return `<tr><td>${esc(e.p.name)}</td><td>${badge(e.bucket, e.bucket)}</td><td>${e.coverage}/${e.taskCount}</td><td>${e.supported.length} supported; ${e.unresolved.length} unresolved; ${e.conflicts.length} conflict(s)</td><td>${p50s.length ? `${fmt(Math.min(...p50s))}–${fmt(Math.max(...p50s))} ms across different operations` : "Not measured"}</td><td>${money(e.cost.base)}</td><td>${esc(nextCheck(e))}</td></tr>`;
  }).join("");
  document.querySelectorAll("[data-sort]").forEach(b => b.parentElement.setAttribute("aria-sort", state.sort === b.dataset.sort ? (state.sortAsc ? "ascending" : "descending") : "none"));
}

function renderLedger() {
  const rows = D.provider_order.flatMap(id => Object.values(D.providers[id].measured.suites).flat());
  $("#cohort-table tbody").innerHTML = rows.map(c => `<tr><td>${esc(D.providers[c.provider].name)}<br>${esc(label(c.suite))}</td><td>${esc(c.runtime_kind)}<br>${c.concurrency} workers</td><td>${c.outcomes.pass || 0}/${c.n}</td><td>${percent(c.success_ci95[0])}–${percent(c.success_ci95[1])}</td><td>${fmt(c.latency_ms.p50)} / ${fmt(c.latency_ms.p95)} ms<br><span class="small">Passed attempts; timing n=${c.latency_ms.n}; p95 descriptive</span></td><td>${fmt(c.attempt_latency_ms.p50)} ms</td><td><span class="mono">${esc(c.config_id)}</span><br>${cohortLink(c)}<details><summary>Fingerprint</summary><p class="mono">${esc(JSON.stringify(c.configuration.requested))}<br>workload ${esc(c.workload_sha256)}<br>adapter ${esc(c.adapter_sha256)}<br>stack ${esc(c.stack_sha256)}</p></details></td></tr>`).join("");
  const campaigns = D.campaigns.filter(c => c.workers > 1);
  $("#bursts").innerHTML = `<p class="hint">Short campaigns include warmup time if present. They do not establish sustained capacity or justify a provider-wide speed ranking.</p>${campaigns.map(c => `<p><a href="${esc(c.evidence_url)}">${esc(c.report)}</a>: ${c.workers} workers; ${c.passes}/${c.attempts} verified; ${fmt(c.wall_seconds)} seconds; ${fmt(c.verified_per_sec)} verified completions/s.</p>`).join("")}`;
}

function renderCost() {
  const s = state.scenario, sessions = Math.ceil(Math.ceil(s.jobs * s.attempts) / (s["session-mode"] === "reuse" ? s.reuse : 1));
  $("#cost-explanation").textContent = `${fmt(s.jobs)} intended jobs × ${s.attempts} attempts/job → ${fmt(Math.ceil(s.jobs * s.attempts))} planned attempts, ${fmt(sessions)} sessions. Base active time = attempts × ${s.duration}s; idle/setup = sessions × ${s.idle}s. Runtime range multipliers: ${s.low} / 1 / ${s.high}. Allocated resources accrue while the session exists; consumed AWS resources use your consumption assumptions.`;
  $("#cost-table tbody").innerHTML = results.map(e => {
    const c = e.cost;
    const breakdown = c.components ? Object.entries(c.components).map(([k, v]) => `${k}: ${money(v)}`).join("; ") : "No priced compute model";
    return `<tr><td>${esc(e.p.name)}</td><td>${money(c.low)} / ${money(c.base)} / ${money(c.high)}${c.base == null && c.knownBase != null ? `<br>Known base subtotal: ${money(c.knownBase)}` : ""}</td><td>${money(c.cash)}</td><td>${c.feasibility.length ? c.feasibility.map(esc).join("<br>") : "Documented options; exact SKU/quota/configuration still needs confirmation."}</td><td><p>${esc(breakdown)}</p>${c.missing.concat(c.notes).map(n => `<p class="small">${esc(n)}</p>`).join("")}</td></tr>`;
  }).join("");
}

function renderMatrices() {
  const providers = state.matrixCandidates ? results.filter(e => e.bucket !== "conflict").map(e => e.p) : D.provider_order.map(id => D.providers[id]);
  const heading = `<tr><th>Requirement / surface</th>${providers.map(p => `<th>${esc(p.name)}</th>`).join("")}</tr>`;
  $("#feature-table thead").innerHTML = heading;
  $("#feature-table tbody").innerHTML = Object.entries(D.feature_labels).map(([id, name]) => `<tr><th scope="row">${esc(name)}</th>${providers.map(p => {
    const f = p.features[id] || {support: "unknown", evidence: "no specification", notes: "No provider specification for this control."};
    return `<td>${badge(f.support, f.support)}<div class="small">Evidence: ${esc(f.evidence)}</div><details><summary>Qualification</summary>${esc(f.notes)}<br><a href="${esc(p.spec_url)}">Spec & sources</a></details></td>`;
  }).join("")}</tr>`).join("");
  $("#residency-table thead").innerHTML = heading;
  $("#residency-table tbody").innerHTML = Object.entries(D.residency_surfaces).map(([id, name]) => `<tr><th scope="row">${esc(name)}</th>${providers.map(p => {const s = p.eu.surfaces[id]; return `<td>${badge(s.state, s.state)}<p class="small">${esc(s.note)}</p></td>`;}).join("")}</tr>`).join("");
}

function decisionMarkdown() {
  const pr = profile(), candidates = results.filter(e => e.bucket !== "conflict");
  let md = `# Sandbox decision record\n\nEvidence snapshot: ${D.generated_at}\n\n## Job and requirements\n\nWorkloads: ${[...state.workloads].join(", ") || "None selected"}\nFamily: ${state.family}; priority: ${state.priority}; workers: ${state.workers}\nRequired features: ${pr.required.join(", ") || "None"}\nEU-only surfaces: ${[...state.surfaces].join(", ") || "None"}\n\n## Scenario assumptions\n\n`;
  md += Object.entries(state.scenario).map(([k, v]) => `- ${k}: ${v}`).join("\n");
  md += "\n\n## Candidate decisions\n\n";
  for (const e of candidates) {
    md += `### ${e.p.name} — ${e.bucket}\n\nCoverage: ${e.coverage}/${e.taskCount} required operations; smallest cohort n=${e.smallestSample ?? "unknown"}.\nGross cost low/base/high: ${money(e.cost.low)} / ${money(e.cost.base)} / ${money(e.cost.high)}.\n`;
    md += e.present.map(t => `- ${t.suite}, ${t.workers} worker(s): ${t.row.outcomes.pass || 0}/${t.row.n}; 95% success interval ${percent(t.row.success_ci95[0])}–${percent(t.row.success_ci95[1])}; lifecycle p50 ${fmt(t.row.latency_ms.p50)} ms. Setup ${t.row.config_id}; workload ${t.row.workload_sha256}; evaluator ${t.row.evaluation_contract_sha256}; adapter ${t.row.adapter_sha256}; stack ${t.row.stack_sha256}. Evidence: ${t.row.evidence_url}`).join("\n");
    md += "\n" + e.unresolved.concat(e.cost.missing, e.cost.feasibility, e.issues.map(i => i.finding)).map(x => `- Unresolved / reproduce: ${x}`).join("\n");
    md += `\nNext experiment: ${nextCheck(e)}\nSources: ${e.p.spec_url}; ${e.p.eu.source}\n\n`;
  }
  md += "## Set aside\n\n" + results.filter(e => e.bucket === "conflict").map(e => `- ${e.p.name}: ${e.conflicts.join(" ")}`).join("\n");
  md += "\n\n## Unranked endpoint rerun evidence\n\n";
  for (const e of results.filter(e => e.p.unranked_cohorts.length)) {
    md += `### ${e.p.name}\n\n${e.p.raw_attempts_retained} raw attempts retained; deployment attestation unresolved.\n`;
    md += e.p.unranked_cohorts.map(c => `- ${c.suite}, setup ${c.config_id} (${c.configuration.label}), ${c.concurrency} worker(s): ${c.outcomes.pass || 0}/${c.n}; p50 ${fmt(c.latency_ms.p50)} ms; runtime ${c.runtime_kind}; last observed ${c.last_measured_at}. Report: ../${c.reports[0]}`).join("\n") + "\n";
  }
  md += "\n\n## Interpretation\n\nNo SLA, residency certification, arbitrary confidence score or invoice-backed task-cost ranking is implied. Cohorts are not pooled. Runtime scenario multipliers are assumptions, not statistical intervals. Relative report links resolve from reports/variant/.\n";
  md += "\nSelected side-by-side systems: " + [...state.compare].join(", ") + "\n";
  md += "\n## Input source fingerprints (SHA-256)\n\n" + Object.entries(D.source_hashes).map(([name, hash]) => `- ${name}: ${hash}`).join("\n") + "\n";
  return md;
}
function renderDecision() {
  const selected = [...state.compare].map(id => results.find(e => e.p.id === id)).filter(Boolean);
  $("#decision-preview").innerHTML = `<h3>Selected decision routes</h3>${selected.map(e => `<p><b>${esc(e.p.name)}</b> · ${badge(e.bucket, e.bucket)} · ${e.coverage}/${e.taskCount} operations measured.<br><span class="small">Next: ${esc(nextCheck(e))}</span></p>`).join("") || '<p class="hint">Select systems for a focused summary. The export includes every current candidate.</p>'}<p class="small">Exports preserve every gap and cost assumption. Report-relative links remain usable if the Markdown is saved beside this dashboard.</p>`;
}

function render() {
  results = allResults();
  const pr = profile();
  $("#profile-preview").textContent = `Required fixtures: ${pr.tasks.map(t => `${label(t.suite)} (${t.workers} workers)`).join(", ") || "select a job"}. Required capabilities: ${pr.required.map(f => D.feature_labels[f]).join(", ") || "none additional"}. Serving and specialised-compute fixtures are unmeasured. No tested complexity ceiling is inferred from this pilot.`;
  renderCandidates(); renderCompare(); renderCost(); renderMatrices(); renderDecision();
}

function buildControls() {
  $("#snapshot").textContent = D.snapshot_label;
  $("#generated").textContent = "Corpus generated " + D.generated_at;
  $("#workloads").innerHTML = D.workloads.map(w => `<label class="choice"><input type="checkbox" data-workload="${esc(w.id)}" ${state.workloads.has(w.id) ? "checked" : ""}><span><b>${esc(w.label)}</b><small>${esc(w.blurb)} Tests: ${esc(w.suites.join(", "))}${w.concurrency ? "; 3-worker cohort" : ""}.</small></span></label>`).join("");
  $("#requirements").innerHTML = D.hard_requirements.map(f => `<label class="check"><input type="checkbox" data-requirement="${esc(f.id)}">${esc(f.label)}</label>`).join("");
  $("#residency-checks").innerHTML = Object.entries(D.residency_surfaces).map(([id, name]) => `<label class="check"><input type="checkbox" data-surface="${esc(id)}">${esc(name)}</label>`).join("");
  for (const [attribute, set] of [["workload", state.workloads], ["requirement", state.requirements], ["surface", state.surfaces]]) {
    document.querySelectorAll(`[data-${attribute}]`).forEach(el => el.addEventListener("change", () => {
      el.checked ? set.add(el.dataset[attribute]) : set.delete(el.dataset[attribute]); render();
    }));
  }
  for (const id of ["family", "workers", "priority", "controls"]) {
    $("#" + id).addEventListener("change", event => {
      state[id] = id === "controls" ? event.target.checked : id === "workers" ? +event.target.value : event.target.value; render();
    });
  }
  for (const id of [...Object.keys(defaults), "session-mode"]) {
    $("#" + id).addEventListener("input", event => {
      if (id === "session-mode") state.scenario[id] = event.target.value;
      else {
        const el = event.target;
        const numeric = el.tagName === "SELECT" ? Number(el.value) : el.valueAsNumber;
        if (!Number.isFinite(numeric)) return;
        const value = el.tagName === "SELECT" ? numeric : Math.max(+el.min, Math.min(+el.max, numeric));
        state.scenario[id] = ["jobs", "reuse", "input-tokens", "output-tokens"].includes(id) ? Math.floor(value) : value;
        el.value = state.scenario[id];
      }
      render();
    });
  }
  $("#matrix-candidates").addEventListener("change", event => {state.matrixCandidates = event.target.checked; renderMatrices();});
  document.querySelectorAll("[data-sort]").forEach(el => el.addEventListener("click", () => {
    state.sortAsc = el.dataset.sort === state.sort ? !state.sortAsc : true;
    state.sort = el.dataset.sort; renderCompare();
  }));
  $("#export").addEventListener("click", () => {
    const url = URL.createObjectURL(new Blob([decisionMarkdown()], {type: "text/markdown;charset=utf-8"}));
    const a = document.createElement("a"); a.href = url; a.download = "sandbox-decision-summary.md";
    a.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
  });
  $("#print").addEventListener("click", () => window.print());
  $("#reset").addEventListener("click", () => window.location.reload());
}

function renderStatic() {
  renderLedger();
  const counts = D.counts;
  $("#counts").innerHTML = `<p class="small">Summary snapshot: ${counts.all_attempts} retained attempts; ${counts.legacy} legacy/unvalidated; ${counts.contract_hashed_attempts} with an evaluator-contract hash. A hash is not complete provenance. ${D.campaigns.length} campaigns retained. Raw counts on cards are read separately at build time; reports may be refreshed independently. Input file hashes are retained in data.json and the decision export.</p>`;
  $("#provenance").innerHTML = Object.entries(D.provenance_gaps).map(([id, gaps]) => `<p class="small"><b>${esc(D.providers[id].name)}:</b> ${gaps.map(esc).join("; ")}</p>`).join("");
  $("#insights").innerHTML = D.insights.map(i => `<p>${badge(i.category, i.category)} <b>${esc(i.title)}</b><br>${esc(i.finding)}<br><span class="small">${esc(i.boundary)}</span></p>`).join("");
  $("#rate-sheets").innerHTML = D.provider_order.filter(id => D.providers[id].cost_model.rates.length).map(id => {
    const p = D.providers[id];
    return `<details><summary>${esc(p.name)} · ${esc(p.reviewed_at)}</summary><p class="small">${esc(p.cost_model.model_text)}</p><div class="tablewrap"><table><thead><tr><th>Resource</th><th>Original unit</th><th>USD rate</th></tr></thead><tbody>${p.cost_model.rates.map(r => `<tr><td>${esc(r.resource)}</td><td>${esc(r.unit)}</td><td>${r.amount == null ? "Unknown" : esc(String(r.amount))}</td></tr>`).join("")}</tbody></table></div><div class="linkrow">${p.cost_model.sources.map(s => `<a href="${esc(s.url)}" target="_blank" rel="noopener noreferrer">${esc(s.title)}</a>`).join("")}</div><p class="small">${esc(p.pricing_limitations)}</p></details>`;
  }).join("");
}
buildControls(); renderStatic(); render();
