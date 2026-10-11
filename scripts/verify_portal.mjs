// Verify the chart studio and shared nav using isolated, installed Chrome.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
const require = createRequire(import.meta.url);
if (!process.env.PLAYWRIGHT_MODULE) throw new Error('Set PLAYWRIGHT_MODULE to an installed Playwright package.');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE);
const root = new URL('../', import.meta.url);
const output = fileURLToPath(new URL('reports/checks/portal/', root));
fs.mkdirSync(output, {recursive: true});
const browser = await chromium.launch({headless: true,
  ...(process.env.CHROME_PATH ? {executablePath: process.env.CHROME_PATH} : {channel: 'chrome'})});
const errors = [], warnings = [], requests = [], checks = [];
try {
  const page = await browser.newPage();
  page.on('pageerror', error => errors.push(error.message));
  page.on('console', message => {if (['warning', 'error'].includes(message.type())) warnings.push(message.text());});
  page.on('request', request => {if (/^https?:/.test(request.url())) requests.push(request.url());});
  await page.addInitScript(() => {
    Object.defineProperty(window, 'BENCHMARK_DATA', {configurable: true, get() {return this.__fixtureData;}, set(data) {
      if (data?.attempts?.length) {
        data.attempts[0].stdout_preview = '<img src="invalid-fixture" onerror="window.logInjectionExecuted=true">& literal text';
      }
      this.__fixtureData = data;
    }});
  });
  for (const width of [320, 768, 1024, 1440]) {
    await page.setViewportSize({width, height: 1000});
    await page.goto(new URL('reports/ui/index.html', root).href);
    await page.locator('#header-kpis strong').first().waitFor({state: 'attached'});
    assert.equal(await page.locator('.benchmark-nav a').count(), 5);
    assert.equal(await page.locator('.benchmark-nav [aria-current=page]').textContent(), 'Chart studio');
    const noOverflow = await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth);
    if (!noOverflow) {
      await page.screenshot({path: `${output}/overflow-${width}.png`});
      const geometry = await page.evaluate(() => ({documentWidth: document.documentElement.scrollWidth,
        offenders: [...document.querySelectorAll('body *')].filter(e => e.getBoundingClientRect().right > innerWidth + 1)
          .slice(0, 20).map(e => ({tag: e.tagName, id: e.id, className: e.className, right: e.getBoundingClientRect().right}))}));
      fs.writeFileSync(`${output}/overflow-${width}.json`, JSON.stringify(geometry, null, 2));
      console.log(JSON.stringify(geometry, null, 2));
    }
    assert.ok(noOverflow, `Chart studio overflows at ${width}`);
    await page.locator('[data-tab=latency]').click();
    assert.equal(await page.locator('[data-tab=latency]').getAttribute('aria-selected'), 'true');
    await page.waitForTimeout(350); // Complete first-party fade-in before visual capture.
    await page.screenshot({path: `${output}/chart-${width}.png`});
    checks.push({width, noOverflow: true, latencyTab: true});
  }
  assert.ok(!await page.locator('#overview-hero-kpis').innerText().then(t => /16 workers|14\.8|HIGHEST RELIABILITY/.test(t)));
  for (const width of [320, 1440]) {
    await page.setViewportSize({width, height: 1000});
    for (const tab of ['phases','reliability','cost','scale','matrix','inventory','simulator','inspector']) {
      await page.locator(`[data-tab=${tab}]`).click();
      assert.equal(await page.locator(`[data-tab=${tab}]`).getAttribute('aria-selected'), 'true');
      assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), `${tab} overflow at ${width}`);
    }
  }
  await page.locator('#inspector-table-tbody tr').first().click();
  assert.ok((await page.locator('#drawer-content .log-viewer').first().innerText()).includes('<img src="invalid-fixture"'));
  assert.equal(await page.locator('#drawer-content .log-viewer img').count(), 0);
  assert.ok(!await page.evaluate(() => window.logInjectionExecuted));
  assert.ok((await page.locator('#raw-report-link').getAttribute('href')).endsWith('.json'));
  await page.locator('#drawer-close-btn').click();
  for (const link of await page.locator('.benchmark-nav a').evaluateAll(links => links.map(a => a.href))) {
    assert.ok(fs.existsSync(fileURLToPath(link)), 'Portal target missing');
  }
  await page.locator('.benchmark-nav a').filter({hasText: 'Decision filter'}).click();
  await page.locator('#result-status').waitFor();
  assert.equal(await page.locator('.benchmark-nav [aria-current=page]').textContent(), 'Decision filter');
  assert.deepEqual(errors, []);
  assert.deepEqual(warnings, []);
  assert.deepEqual(requests, []);
  const result = {status: 'pass', viewports: checks, allTabs: true, escapedRawLogs: true,
    noFabricatedWinners: true, navigation: 'chart studio → decision filter', errors, warnings, externalRequests: requests};
  fs.writeFileSync(`${output}/verification.json`, JSON.stringify(result, null, 2));
  console.log(JSON.stringify(result, null, 2));
} finally {await browser.close();}
