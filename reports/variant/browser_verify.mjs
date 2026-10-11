// Runs isolated installed Chrome with externally supplied Playwright tooling.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
const require = createRequire(import.meta.url);
if (!process.env.PLAYWRIGHT_MODULE) throw new Error('Set PLAYWRIGHT_MODULE to a Playwright installation.');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE);
const root = new URL('./', import.meta.url);
const out = fileURLToPath(new URL('../checks/decision-guide/', root));
fs.mkdirSync(out, {recursive: true});
const browser = await chromium.launch({
  ...(process.env.CHROME_PATH ? {executablePath: process.env.CHROME_PATH} : {channel: 'chrome'}),
  headless: true,
});
const errors = [], warnings = [], externalRequests = [];
const checks = [];
try {
  const context = await browser.newContext({acceptDownloads: true});
  const page = await context.newPage();
  page.on('pageerror', e => errors.push(e.message));
  page.on('console', m => {if (['error','warning'].includes(m.type())) warnings.push(m.text());});
  page.on('request', r => {if (/^https?:/.test(r.url())) externalRequests.push(r.url());});
  for (const width of [320,768,1024,1440]) {
    await page.setViewportSize({width, height: 1000});
    await page.goto(new URL('index.html', root).href);
    await page.locator('#result-status').waitFor();
    const geometry = await page.evaluate(() => ({viewport: innerWidth, document: document.documentElement.scrollWidth}));
    assert.ok(geometry.document <= width + 1, `Page overflow at ${width}: ${JSON.stringify(geometry)}`);
    assert.equal(await page.locator('#summary-table tbody tr').count(), 13);
    assert.equal(await page.locator('[data-unranked-provider="alibaba"]').count(), 1);
    await page.screenshot({path: `${out}/profile-${width}.png`});
    checks.push({width, documentWidth: geometry.document, rows: 13});
  }
  await page.setViewportSize({width: 1440, height: 1000});
  await page.locator('[data-unranked-provider="alibaba"]').screenshot({path: `${out}/alibaba-rerun.png`});
  await page.locator('[data-workload="code_exec"]').uncheck();
  await page.locator('[data-workload="output_fidelity"]').check();
  await page.locator('#shortlist').scrollIntoViewIfNeeded();
  assert.match(await page.locator('[data-provider="aws"]').innerText(), /stdout loses fidelity/);
  await page.locator('#shortlist').screenshot({path: `${out}/failure-evidence.png`});
  await page.locator('[data-workload="output_fidelity"]').uncheck();
  await page.locator('[data-workload="code_exec"]').check();
  await page.locator('[data-surface="logs"]').check();
  assert.match(await page.locator('[data-provider="gcp_vertex"]').innerText(), /Needs validation/);
  assert.equal(await page.locator('[data-provider="modal"]').count(), 0);
  await page.locator('[data-surface="logs"]').uncheck();
  await page.locator('#priority').selectOption('cost');
  assert.match(await page.locator('[data-provider="aws"]').innerText(), /Needs validation/);
  await page.locator('#priority').selectOption('correctness');
  await page.locator('#plan').selectOption('150');
  assert.match(await page.locator('#cost-table tbody').innerText(), /plan: \$150\.00/);
  await page.locator('#cost').screenshot({path: `${out}/cost-scenarios.png`});
  await page.locator('#session-mode').selectOption('reuse');
  await page.locator('#jobs').fill('100');
  await page.locator('#side-by-side').scrollIntoViewIfNeeded();
  assert.equal(await page.locator('#side-by-side thead th').count(), 4);
  await page.getByRole('button', {name: 'Task coverage'}).click();
  assert.equal(await page.locator('[data-sort="coverage"]').locator('..').getAttribute('aria-sort'), 'ascending');
  const downloadReady = page.waitForEvent('download');
  await page.getByRole('button', {name: 'Download decision summary (.md)', exact: true}).click();
  const download = await downloadReady;
  await download.saveAs(`${out}/decision-export.md`);
  const md = fs.readFileSync(`${out}/decision-export.md`, 'utf8');
  assert.match(md, /jobs: 100/);
  assert.match(md, /session-mode: reuse/);
  assert.match(md, /plan: 150/);
  assert.match(md, /Next experiment:/);
  // Genuine keyboard input: focus a sort button and dispatch its native Enter action.
  await page.locator('[data-sort="name"]').focus();
  await page.keyboard.press('Enter');
  assert.equal(await page.locator('[data-sort="name"]').locator('..').getAttribute('aria-sort'), 'ascending');
  assert.deepEqual(errors, []);
  assert.deepEqual(warnings, []);
  assert.deepEqual(externalRequests, []);
  const evidence = {status: 'pass', viewports: checks, interactions: ['Alibaba rerun visible by default','failed-path details','residency gaps','missing-cost validation','plan fees','reuse','sorting','keyboard','Markdown download'], consoleErrors: errors, consoleWarnings: warnings, externalRequests};
  fs.writeFileSync(`${out}/validation.json`, JSON.stringify(evidence, null, 2));
  console.log(JSON.stringify(evidence, null, 2));
} finally {await browser.close();}
