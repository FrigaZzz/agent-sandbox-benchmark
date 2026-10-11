// Behavioural checks for the actual generated page, not a second implementation.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
const require = createRequire(import.meta.url);
if (!process.env.JSDOM_MODULE) throw new Error('Set JSDOM_MODULE to an installed jsdom entry.');
const {JSDOM} = require(process.env.JSDOM_MODULE);
const root = new URL('./', import.meta.url);
const errors = [];
const dom = new JSDOM(fs.readFileSync(new URL('index.html', root), 'utf8'), {
  runScripts: 'dangerously', url: new URL('index.html', root).href,
  beforeParse(w) {w.addEventListener('error', e => errors.push(e.message));},
});
const w = dom.window, d = w.document;
const inspect = expression => JSON.parse(w.eval(`JSON.stringify(${expression})`));
const fire = (el, type = 'change') => el.dispatchEvent(new w.Event(type, {bubbles: true}));
const set = (selector, value, type = 'change') => {
  const el = d.querySelector(selector); assert.ok(el, selector);
  if (el.type === 'checkbox') el.checked = value; else el.value = value;
  fire(el, type);
};
const chooseOnly = id => {
  d.querySelectorAll('[data-workload]').forEach(el => {el.checked = el.dataset.workload === id; fire(el);});
};

assert.equal(d.querySelectorAll('#summary-table tbody tr').length, 13);
// A refreshed endpoint run must be visible without opting into a cloud ranking.
const alibaba = d.querySelector('[data-unranked-provider="alibaba"]');
assert.ok(alibaba, 'Alibaba rerun evidence is visible by default');
assert.match(alibaba.textContent, /Unranked rerun evidence/);
assert.match(alibaba.textContent, /live-rerun/);
assert.ok(inspect('D.providers.alibaba.unranked_cohorts.length') > 0);
assert.equal(inspect('results.find(e=>e.p.id==="alibaba").bucket'), 'conflict');
assert.ok(!inspect('groupsFor(results).flat().map(e=>e.p.id)').includes('alibaba'));
const cohorts = inspect('Object.values(D.providers).flatMap(p=>Object.values(p.measured.suites).flat())');
assert.equal(d.querySelectorAll('#cohort-table tbody tr').length, cohorts.length);
// Samples can grow as new runs arrive. Baseline and burst must remain distinct.
const cpuCohorts = inspect('D.providers.e2b.measured.suites.cpu_stress');
const baseline = cpuCohorts.find(c => c.concurrency === 1);
const burst = cpuCohorts.find(c => c.concurrency === 3);
assert.ok(baseline && burst && baseline !== burst);
assert.ok(baseline.n >= 5 && burst.n >= 5);
assert.notEqual(baseline.comparison_key, burst.comparison_key);
assert.equal(inspect('D.providers.gcp_vertex.eu.surfaces.logs.state'), 'unknown');
assert.equal(inspect('D.providers.modal.eu.surfaces.logs.state'), 'conflict');

chooseOnly('cpu_compute');
assert.equal(inspect('results.find(e=>e.p.id==="e2b").present[0].row.n'), baseline.n);
set('#workers', '3');
assert.equal(inspect('results.find(e=>e.p.id==="e2b").present[0].row.n'), burst.n);
set('#workers', '1');
chooseOnly('output_fidelity');
assert.equal(inspect('results.find(e=>e.p.id==="aws").bucket'), 'validate');
assert.match(d.querySelector('[data-provider="aws"]').textContent, /stdout loses fidelity/);
const output = inspect('results.find(e=>e.p.id==="aws").present[0].row');
assert.equal(output.outcomes.fail, output.n);

chooseOnly('serve_app');
assert.equal(inspect('results.filter(e=>e.bucket==="measured").length'), 0);
chooseOnly('code_exec');
set('[data-requirement="gpu"]', true);
assert.equal(inspect('results.find(e=>e.p.id==="e2b").bucket'), 'conflict');
assert.equal(inspect('results.find(e=>e.p.id==="gcp_vertex").bucket'), 'validate');
set('[data-requirement="gpu"]', false);
set('[data-surface="logs"]', true);
assert.equal(inspect('results.find(e=>e.p.id==="modal").bucket'), 'conflict');
assert.equal(inspect('results.find(e=>e.p.id==="gcp_vertex").bucket'), 'validate');
// An excluded system must still be removable from an already selected comparison.
fire(d.querySelector('[data-remove="modal"]'), 'click');
assert.equal(inspect('state.compare.has("modal")'), false);
set('[data-surface="logs"]', false);
set('#family', 'all');
const families = inspect('groupsFor(results).map(g=>g[0].present[0].row.runtime_kind)');
assert.ok(families.includes('remote_runtime') && families.includes('model_mediated'));
set('#family', 'remote_runtime');
set('#priority', 'cost');
assert.equal(inspect('results.find(e=>e.p.id==="databricks").bucket'), 'validate');
assert.equal(inspect('results.find(e=>e.p.id==="aws").bucket'), 'validate');
assert.equal(inspect('results.find(e=>e.p.id==="e2b").bucket'), 'measured');
set('#priority', 'correctness');

const oldCost = inspect('results.find(e=>e.p.id==="e2b").cost.base');
set('#plan', '150', 'input');
assert.equal(inspect('results.find(e=>e.p.id==="e2b").cost.base'), oldCost + 150);
set('#plan', '0', 'input');
set('#session-mode', 'reuse', 'input');
assert.ok(inspect('results.find(e=>e.p.id==="e2b").cost.base') < oldCost);
const range = inspect('results.find(e=>e.p.id==="e2b").cost');
assert.ok(range.low <= range.base && range.base <= range.high);
set('#storage', '10', 'input');
assert.equal(inspect('results.find(e=>e.p.id==="modal").cost.base'), null);
assert.ok(inspect('results.find(e=>e.p.id==="modal").cost.knownBase') > 0);
assert.ok(inspect('results.find(e=>e.p.id==="blaxel").cost.base') > 0);
set('#storage', '0', 'input');
set('#cpu-use', '0', 'input');
set('#mem-use', '0', 'input');
assert.ok(inspect('results.find(e=>e.p.id==="aws").cost.base') > 0, '128 MB minimum still incurs memory cost');
set('#cpu-use', '100', 'input');
set('#mem-use', '100', 'input');
set('#jobs', '0', 'input');
assert.equal(inspect('results.find(e=>e.p.id==="openai_tool").cost.base'), 0);
set('#jobs', '10000', 'input');
// Clamp malformed assumptions; don't turn blanks into artificial free usage.
set('#jobs', '-3', 'input');
assert.equal(inspect('state.scenario.jobs'), 0);
set('#jobs', '10000', 'input');
for (const b of d.querySelectorAll('[data-sort]')) {fire(b, 'click'); fire(b, 'click');}
set('#matrix-candidates', false);
assert.equal(d.querySelectorAll('#feature-table thead th').length, 14);
const markdown = w.eval('decisionMarkdown()');
assert.match(markdown, /Scenario assumptions/);
assert.match(markdown, /workload [a-f0-9]{64}/);
assert.match(markdown, /No SLA, residency certification/);
assert.match(markdown, /Next experiment:/);
assert.equal(d.querySelectorAll('.score').length, 0);
assert.deepEqual(errors, []);

// All rendered local report links must resolve; external sources remain passive links.
for (const a of d.querySelectorAll('a[href]')) {
  const url = new URL(a.href);
  if (url.protocol === 'file:') assert.ok(fs.existsSync(fileURLToPath(new URL(url.pathname, 'file://'))), a.href);
}
console.log('PASS: cohort separation, failed-path evidence, missing-input handling, residency, pricing, sorting, export and local links.');
dom.window.close();
