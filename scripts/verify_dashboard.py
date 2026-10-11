"""Verify the dashboard/deck, retain screenshots and export its 23-page PDF.

Uses a disposable headless Chrome profile and localhost. PDF/contact-sheet checks
also use Pillow and PyMuPDF, available in the presentation authoring environment.
"""
import asyncio
import base64
import functools
import http.server
import json
import os
import shutil
import subprocess
import tempfile
import threading
import time
import urllib.request
from urllib.parse import unquote, urlsplit
import zipfile
from pathlib import Path

import websockets
import pymupdf
from PIL import Image, ImageDraw


def chrome_path():
    explicit = os.environ.get('CHROME_PATH')
    if explicit:
        return explicit
    for name in ['google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser']:
        if path := shutil.which(name):
            return path
    mac_path = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    if Path(mac_path).is_file():
        return mac_path
    raise RuntimeError('Chrome/Chromium not found; set CHROME_PATH to its executable.')


async def verify():
    root = Path(__file__).resolve().parents[1]
    output = root / "reports/checks/dashboard"
    output.mkdir(exist_ok=True)
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(root)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    errors = []
    with tempfile.TemporaryDirectory(prefix='bench-chrome-') as profile:
        browser = subprocess.Popen([chrome_path(), '--headless',
            '--disable-gpu', '--no-first-run', '--no-default-browser-check', '--remote-debugging-port=0',
            f'--user-data-dir={profile}', 'about:blank'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            portfile = Path(profile) / 'DevToolsActivePort'
            for _ in range(100):
                if portfile.exists():
                    break
                await asyncio.sleep(.1)
            port = int(portfile.read_text().splitlines()[0])
            pages = json.loads(urllib.request.urlopen(f'http://127.0.0.1:{port}/json').read())
            page = next(p for p in pages if p['type'] == 'page')
            async with websockets.connect(page['webSocketDebuggerUrl'], max_size=64*1024*1024) as ws:
                counter = 0
                async def call(method, params=None):
                    nonlocal counter
                    counter += 1
                    await ws.send(json.dumps(dict(id=counter, method=method, params=params or {})))
                    while True:
                        msg = json.loads(await ws.recv())
                        if msg.get('method') == 'Runtime.exceptionThrown':
                            errors.append(msg['params']['exceptionDetails'])
                        if msg.get('id') == counter:
                            if 'error' in msg:
                                raise RuntimeError(msg['error'])
                            return msg.get('result', {})
                async def evaluate(expression):
                    result = await call('Runtime.evaluate', {'expression': expression, 'returnByValue': True})
                    if result.get('exceptionDetails'):
                        raise RuntimeError(result['exceptionDetails'])
                    return result['result'].get('value')
                await call('Runtime.enable')
                await call('Page.enable')
                await call('Page.navigate', {'url': f'http://127.0.0.1:{server.server_port}/reports/index.html'})
                for _ in range(100):
                    if await evaluate('document.querySelectorAll("#comparison tr").length > 0'):
                        break
                    await asyncio.sleep(.1)
                checks = {}
                checks['comparison_populated'] = await evaluate('document.querySelectorAll("#comparison tr").length >= 6')
                checks['specifications_populated'] = await evaluate('document.querySelectorAll("#customization-body tr").length === 12')
                checks['price_sheet_populated'] = await evaluate('document.querySelectorAll("#pricing-body tr").length > 0')
                local_urls = set(await evaluate('[...document.querySelectorAll("a[href]")].map(a=>a.href)'))
                for provider in await evaluate('[...document.getElementById("price-provider").options].map(o=>o.value)'):
                    await evaluate(f'document.getElementById("price-provider").value={json.dumps(provider)};renderPricing()')
                    local_urls.update(await evaluate('[...document.querySelectorAll("a[href]")].map(a=>a.href)'))
                checks['dashboard_all_local_links_resolve'] = all(
                    (root / unquote(urlsplit(url).path.lstrip('/'))).exists()
                    for url in local_urls if urlsplit(url).hostname == '127.0.0.1'
                )
                checks['raw_text_safe'] = await evaluate('document.querySelectorAll("#attempt-details pre").length >= 8')
                checks['light_theme'] = await evaluate('getComputedStyle(document.body).backgroundColor === "rgb(245, 245, 247)"')
                checks['measured_findings_populated'] = await evaluate('document.querySelectorAll("#takeaway-body article").length === Math.min(3, data.insights.filter(i=>i.category==="failure").length)')
                evidence_files = await evaluate('[...new Set(data.attempts.map(r=>r.report_path))]')
                # Navigate an evidence permalink and verify the exact attempt, not just transport success.
                first_ref = await evaluate('data.insights.find(i=>i.category==="failure").evidence[0]')
                await call('Page.navigate', {'url': f'http://127.0.0.1:{server.server_port}/reports/index.html#raw?provider={first_ref["provider"]}&run_id={first_ref["run_id"]}'})
                for _ in range(50):
                    if first_ref['run_id'] in (await evaluate('document.getElementById("attempt-details").textContent')):
                        break
                    await asyncio.sleep(.1)
                checks['exact_attempt_navigation'] = first_ref['run_id'] in await evaluate('document.getElementById("attempt-details").textContent')
                checks['exact_attempt_isolation'] = await evaluate('document.getElementById("attempt").options.length === 1')
                checks['failed_checks_visible'] = 'Checks not passed:' in await evaluate('document.getElementById("attempt-details").textContent')
                await call('Page.navigate', {'url': f'http://127.0.0.1:{server.server_port}/reports/index.html#takeaways'})
                await call('Page.reload')
                for _ in range(100):
                    if await evaluate('document.querySelectorAll("#comparison tr").length >= 6'):
                        break
                    await asyncio.sleep(.1)
                # Explicit fixture-only UI interaction; no credentials or external requests.
                await evaluate('document.querySelector(".requirements input[value=session_state]").click()')
                text = await evaluate('document.getElementById("recommendations").textContent')
                checks['hard_requirements_filter'] = 'E2B' in text and 'Modal' in text and 'GCP Agent Sandbox' not in text
                await evaluate('document.getElementById("presentation").click()')
                checks['presentation'] = await evaluate('document.querySelectorAll(".slide-active").length===1 && document.body.classList.contains("presentation")')
                previous_slide = await evaluate('slide')
                dashboard_slides = await evaluate('slides.length')
                await evaluate('document.getElementById("next").click()')
                checks['slide_next'] = await evaluate('slide') == (previous_slide + 1) % dashboard_slides
                await evaluate('document.getElementById("presentation").click()')
                for width in [320, 768, 1440]:
                    await call('Emulation.setDeviceMetricsOverride', {'width': width, 'height': 1000, 'deviceScaleFactor': 1, 'mobile': width == 320})
                    checks[f'viewport_{width}_no_body_overflow'] = await evaluate('document.documentElement.scrollWidth<=window.innerWidth')
                    screenshot = await call('Page.captureScreenshot', {'format': 'png', 'captureBeyondViewport': False})
                    (output / f'dashboard-{width}.png').write_bytes(base64.b64decode(screenshot['data']))
                await call('Page.navigate', {'url': f'http://127.0.0.1:{server.server_port}/reports/slides.html'})
                for _ in range(100):
                    if await evaluate('document.querySelectorAll("#compute-chart .chart-row").length === 6'):
                        break
                    await asyncio.sleep(.1)
                await call('Emulation.setDeviceMetricsOverride', {'width': 1248, 'height': 1050, 'deviceScaleFactor': 1, 'mobile': False})
                slide_count = await evaluate('document.querySelectorAll("main>section").length')
                checks['deck_populated'] = slide_count == 23
                checks['deck_all_local_links_resolve'] = all(
                    (root / unquote(urlsplit(url).path.lstrip('/'))).exists()
                    for url in await evaluate('[...document.querySelectorAll("a[href]")].map(a=>a.href)')
                    if urlsplit(url).hostname == '127.0.0.1'
                )
                checks['story_workflow_evidence'] = await evaluate('document.querySelectorAll("#workflow-matrix .matrix-value").length === 9 && [...document.querySelectorAll("#workflow-matrix .matrix-value")].every(e=>e.textContent.startsWith("5/5"))')
                checks['story_provider_profiles'] = await evaluate('document.querySelectorAll(".profile").length === 7 && document.querySelectorAll(".profile[data-layout=tradeoff]").length === 5 && document.querySelectorAll("#databricks .execution-lanes .panel").length === 3 && document.querySelector("#gcp").textContent.includes("API machine configurations")')
                checks['story_residency_comparison'] = await evaluate('document.querySelectorAll("#region-options tr").length === 7 && [...document.querySelectorAll(".profile")].every(s=>s.querySelector(".residency-strip"))')
                checks['story_legal_scope'] = await evaluate('document.querySelector("#eu-gate h2").textContent.includes("not a blanket") && document.querySelector("#region-evidence h2").textContent.includes("not an")')
                checks['story_notes'] = await evaluate('document.querySelectorAll(".notes").length === 23 && document.querySelectorAll("#jump option").length === 23')
                checks['story_output_bytes'] = await evaluate('[...document.querySelectorAll("#output-chart .chart-value")].map(e=>e.firstChild.textContent).join("|") === "131,071|65,602|131,072|131,072|131,072"')
                checks['story_compute_counts'] = await evaluate('document.querySelectorAll("#compute-chart .chart-row").length === 6 && document.getElementById("compute-chart").textContent.includes("4/5")')
                checks['story_deadline_ranges'] = await evaluate('document.getElementById("deadline-chart").textContent.includes("4.21–4.22") && document.getElementById("deadline-chart").textContent.includes("8.78–10.88")')
                deck_heights = {}
                layout_issues = {}
                # Check text/chart containment, not only document horizontal overflow.
                containment = '''(()=>{const s=document.querySelector("section.active"),issues=[];
                    if(s.scrollHeight>s.clientHeight+2)issues.push("slide vertical overflow");
                    for(const c of s.querySelectorAll(".content")){
                        const box=c.getBoundingClientRect();
                        for(const e of c.querySelectorAll("*")){
                            if(!e.getClientRects().length)continue;
                            const r=e.getBoundingClientRect();
                            if(r.bottom>box.bottom+3)issues.push(e.tagName+" "+e.className+" exceeds content by "+Math.round(r.bottom-box.bottom)+"px");
                        }
                    }return [...new Set(issues)];})()'''
                for index in range(slide_count):
                    checks[f'deck_slide_{index+1}_no_overflow'] = await evaluate('document.documentElement.scrollWidth<=window.innerWidth')
                    deck_heights[str(index+1)] = await evaluate('Math.ceil(document.querySelector("section.active").getBoundingClientRect().height)')
                    issues = await evaluate(containment)
                    layout_issues[str(index+1)] = issues
                    checks[f'deck_slide_{index+1}_content_fits'] = not issues
                    clip = await evaluate('(()=>{const r=document.querySelector("section.active").getBoundingClientRect();return {x:r.x+scrollX,y:r.y+scrollY,width:1200,height:900,scale:1}})()')
                    screenshot = await call('Page.captureScreenshot', {'format': 'png', 'captureBeyondViewport': True, 'clip': clip})
                    (output / f'slide-{index+1}.png').write_bytes(base64.b64decode(screenshot['data']))
                    await evaluate('document.getElementById("next").click()')
                # Exact 4:3 pages, with original external source links and no ephemeral localhost links.
                await evaluate('''window.pdfLinks=[...document.querySelectorAll("a[href]")].filter(a=>!/^https?:/.test(a.getAttribute("href"))).map(a=>[a,a.getAttribute("href")]);window.pdfLinks.forEach(([a])=>a.removeAttribute("href"));''')
                await call('Emulation.setEmulatedMedia', {'media': 'print'})
                for number in range(1, slide_count+1):
                    issues = await evaluate(containment.replace('section.active', f'main>section:nth-of-type({number})'))
                    layout_issues[f'print-{number}'] = issues
                    checks[f'pdf_slide_{number}_content_fits'] = not issues
                pdf = await call('Page.printToPDF', {'printBackground': True, 'preferCSSPageSize': True,
                    'displayHeaderFooter': False, 'marginTop': 0, 'marginBottom': 0, 'marginLeft': 0, 'marginRight': 0})
                pdf_path = root / 'reports/downloads/sandbox-field-guide.pdf'
                pdf_path.parent.mkdir(parents=True, exist_ok=True)
                pdf_path.write_bytes(base64.b64decode(pdf['data']))
                await call('Emulation.setEmulatedMedia', {'media': 'screen'})
                await evaluate('window.pdfLinks.forEach(([a,href])=>a.setAttribute("href",href));delete window.pdfLinks;')
                with pymupdf.open(pdf_path) as doc:
                    checks['pdf_23_pages'] = len(doc) == 23
                    checks['pdf_uniform_4_by_3'] = all(abs(p.rect.width - 900) < 1 and abs(p.rect.height - 675) < 1 for p in doc)
                    checks['pdf_no_localhost_links'] = all('127.0.0.1' not in link.get('uri', '') for p in doc for link in p.get_links())
                    checks['pdf_text_is_searchable'] = all(len(p.get_text().strip()) > 150 for p in doc)
                    checks['pdf_source_links'] = sum(bool(link.get('uri', '').startswith('https://')) for p in doc for link in p.get_links()) >= 15
                    # Rasterise every PDF page to independently inspect print output.
                    for i, page in enumerate(doc):
                        page.get_pixmap(matrix=pymupdf.Matrix(4/3, 4/3)).save(output / f'pdf-slide-{i+1}.png')
                # Compact visual audit sheets retain every slide, with readable full-size files alongside.
                for batch, start in enumerate(range(1, slide_count+1, 8), 1):
                    sheet = Image.new('RGB', (1200, 510), '#e9e7e2')
                    draw = ImageDraw.Draw(sheet)
                    for cell, number in enumerate(range(start, min(start+8, slide_count+1))):
                        # Four columns give a two-row board for each eight-page batch.
                        x, y = (cell % 4)*300, (cell // 4)*250+8
                        image = Image.open(output / f'pdf-slide-{number}.png').convert('RGB')
                        image.thumbnail((292, 219))
                        sheet.paste(image, (x+4, y+22))
                        draw.text((x+8, y), f'Slide {number}', fill='#17272e')
                    sheet.save(output / f'contact-sheet-{batch}.png')
                # The standalone PDF keeps official web sources. Exact attempts and local
                # source guides travel in an explicit offline companion rather than dead links.
                bundle_files = {
                    'reports/downloads/sandbox-field-guide.pdf', 'reports/slides.html', 'reports/index.html',
                    'reports/docs/findings.md', 'reports/docs/eu-data-residency.md', 'reports/docs/evaluation-framework.md',
                    'reports/data/derived/evaluation-summary.json', 'reports/data/derived/specifications.json',
                    'reports/docs/field-guide-readme.md', 'reports/docs/data-notes.md', 'providers/README.md',
                    *(f'reports/checks/dashboard/contact-sheet-{i}.png' for i in range(1, 4)),
                }
                # Evidence ingestion stores report basenames; dashboard links resolve
                # them relative to reports/, rather than the repository root.
                bundle_files.update('reports/' + filename for filename in evidence_files)
                bundle_files.update(str(p.relative_to(root)) for p in (root / 'providers').rglob('*.md'))
                bundle_files.update(str(p.relative_to(root)) for p in (root / 'providers').rglob('*.json'))
                bundle_files.update(str(p.relative_to(root)) for p in (root / 'reports/data/campaigns').glob('*.json'))
                bundle_files.add('reports/portal.css')
                # Shared navigation also works inside the offline companion.
                for directory in ('reports/ui', 'reports/variant', 'reports/executive', 'reports/simplified', 'reports/docs',
                                  'src', 'scripts', 'tests', 'examples', 'deploy', '.github'):
                    bundle_files.update(p.relative_to(root).as_posix() for p in (root / directory).rglob('*')
                        if p.is_file() and p.suffix in {'.html', '.md', '.py', '.js', '.mjs', '.css', '.json', '.svg', '.png', '.pdf', '.yml', '.yaml'}
                        and '__pycache__' not in p.parts)
                bundle_files.update(['readme.md', 'CONTRIBUTING.md', 'index.html', 'BENCHMARK_LOCATIONS.md',
                                     'pyproject.toml', 'Dockerfile.runner', 'compose.yaml', '.pre-commit-config.yaml'])
                bundle_path = root / 'reports/downloads/sandbox-field-guide-bundle.zip'
                missing_files = []
                with zipfile.ZipFile(bundle_path, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
                    for relative in sorted(bundle_files):
                        path = (root / relative).resolve()
                        if not path.is_relative_to(root) or not path.is_file():
                            missing_files.append(relative)
                            continue
                        archive.write(path, str(path.relative_to(root)))
                checks['companion_evidence_files_present'] = not missing_files
                checks['companion_package_exists'] = bundle_path.stat().st_size > 0
                await evaluate('document.getElementById("notes-toggle").click()')
                checks['presenter_notes_toggle'] = await evaluate('[...document.querySelectorAll(".notes")].every(d=>d.open)')
                await evaluate('document.getElementById("notes-toggle").click()')
                for width in [320, 768, 1024, 1440]:
                    await call('Emulation.setDeviceMetricsOverride', {'width': width, 'height': 1000, 'deviceScaleFactor': 1, 'mobile': width == 320})
                    for index in range(slide_count):
                        checks[f'deck_{width}_slide_{index+1}_no_overflow'] = await evaluate('document.documentElement.scrollWidth<=window.innerWidth')
                        if index in [0, 4, 5, 8, 17, 20]:
                            screenshot = await call('Page.captureScreenshot', {'format': 'png', 'captureBeyondViewport': True})
                            (output / f'deck-{width}-slide-{index+1}.png').write_bytes(base64.b64decode(screenshot['data']))
                        await evaluate('document.getElementById("next").click()')
                checks['no_runtime_errors'] = not errors
                result = {'checks': checks, 'errors': errors, 'deck_section_heights_at_master': deck_heights,
                    'layout_issues': layout_issues, 'pdf_path': str(pdf_path.relative_to(root)),
                    'companion_path': str(bundle_path.relative_to(root)), 'missing_companion_files': missing_files,
                    'status': 'pass' if all(checks.values()) else 'fail'}
                (output / 'verification.json').write_text(json.dumps(result, indent=2))
                print(json.dumps(result, indent=2))
                if result['status'] != 'pass':
                    raise SystemExit(1)
        finally:
            browser.terminate()
            browser.wait(timeout=10)
            server.shutdown()


if __name__ == '__main__':
    asyncio.run(verify())
