"""Export and verify the executive briefing in disposable headless Chrome."""
import asyncio
import base64
import functools
import http.server
import json
import subprocess
import sys
import tempfile
import threading
import urllib.request
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.verify_dashboard import chrome_path
import websockets
import pymupdf
from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent


async def export():
    checks, errors = {}, []
    images = OUT / "checks"
    images.mkdir(exist_ok=True)
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with tempfile.TemporaryDirectory(prefix="executive-chrome-") as profile:
            browser = subprocess.Popen([chrome_path(), '--headless', '--disable-gpu', '--no-first-run',
                '--no-default-browser-check', '--remote-debugging-port=0', f'--user-data-dir={profile}', 'about:blank'],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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
                            message = json.loads(await ws.recv())
                            if message.get('method') == 'Runtime.exceptionThrown':
                                errors.append(message['params']['exceptionDetails'])
                            if message.get('id') == counter:
                                if 'error' in message:
                                    raise RuntimeError(message['error'])
                                return message.get('result', {})
                    async def evaluate(expression):
                        result = await call('Runtime.evaluate', dict(expression=expression, returnByValue=True))
                        if result.get('exceptionDetails'):
                            raise RuntimeError(result['exceptionDetails'])
                        return result['result'].get('value')
                    async def navigate(path):
                        await call('Page.navigate', {'url': f'http://127.0.0.1:{server.server_port}/{path}'})
                        for _ in range(100):
                            if await evaluate('document.readyState==="complete"'):
                                break
                            await asyncio.sleep(.1)
                        await asyncio.sleep(.15)
                    await call('Runtime.enable')
                    await call('Page.enable')
                    await call('Emulation.setDeviceMetricsOverride', {'width': 1248, 'height': 1080, 'deviceScaleFactor': 1, 'mobile': False})
                    await navigate('reports/executive/index.html')
                    for _ in range(100):
                        if await evaluate('document.images.length===6&&[...document.images].every(i=>i.complete&&i.naturalWidth>0)'):
                            break
                        await asyncio.sleep(.1)
                    checks['ten_slides'] = await evaluate('document.querySelectorAll(".slide").length===10')
                    checks['images_loaded'] = await evaluate('[...document.images].every(i=>i.complete&&i.naturalWidth>0)')
                    checks['portal_five_links'] = await evaluate('document.querySelectorAll(".benchmark-nav a").length===5')
                    checks['local_links_resolve'] = all((ROOT / unquote(urlsplit(url).path.lstrip('/'))).exists()
                        for url in await evaluate('[...document.querySelectorAll("a[href]")].map(a=>a.href)')
                        if urlsplit(url).hostname == '127.0.0.1')
                    await call('Input.dispatchKeyEvent', {'type': 'keyDown', 'key': 'ArrowRight', 'code': 'ArrowRight', 'windowsVirtualKeyCode': 39})
                    await call('Input.dispatchKeyEvent', {'type': 'keyUp', 'key': 'ArrowRight', 'code': 'ArrowRight', 'windowsVirtualKeyCode': 39})
                    checks['keyboard_navigation'] = await evaluate('document.querySelector(".slide.active").id==="slide-2"')
                    for i in range(10):
                        # First-party fixture UI only; no external or credential actions.
                        await evaluate(f'show({i})')
                        checks[f'slide_{i+1}_fits'] = await evaluate('(()=>{const s=document.querySelector(".slide.active");return s.scrollHeight<=900&&document.documentElement.scrollWidth<=window.innerWidth})()')
                        rect = await evaluate('(()=>{const r=document.querySelector(".slide.active").getBoundingClientRect();return {x:r.x+scrollX,y:r.y+scrollY,width:r.width,height:900,scale:1}})()')
                        shot = await call('Page.captureScreenshot', {'format': 'png', 'captureBeyondViewport': True, 'clip': rect})
                        (images / f'slide-{i+1}.png').write_bytes(base64.b64decode(shot['data']))
                    for width in (320, 768, 1024, 1440):
                        await call('Emulation.setDeviceMetricsOverride', {'width': width, 'height': 1000, 'deviceScaleFactor': 1, 'mobile': width == 320})
                        for i in range(10):
                            await evaluate(f'show({i})')
                            checks[f'viewport_{width}_slide_{i+1}'] = await evaluate('document.documentElement.scrollWidth<=window.innerWidth')
                    await call('Emulation.setDeviceMetricsOverride', {'width': 1248, 'height': 1080, 'deviceScaleFactor': 1, 'mobile': False})
                    # Relative companion links are not useful in an uploaded PDF; official web links remain.
                    await evaluate('[...document.querySelectorAll("a[href]")].filter(a=>!/^https?:/.test(a.getAttribute("href"))).forEach(a=>a.removeAttribute("href"))')
                    await call('Emulation.setEmulatedMedia', {'media': 'print'})
                    pdf = await call('Page.printToPDF', {'printBackground': True, 'preferCSSPageSize': True, 'displayHeaderFooter': False,
                        'marginTop': 0, 'marginBottom': 0, 'marginLeft': 0, 'marginRight': 0})
                    (OUT / 'agent-sandbox-executive.pdf').write_bytes(base64.b64decode(pdf['data']))
                    with pymupdf.open(OUT / 'agent-sandbox-executive.pdf') as doc:
                        checks['pdf_ten_pages'] = len(doc) == 10
                        checks['pdf_searchable'] = all(len(p.get_text().strip()) > 100 for p in doc)
                        checks['pdf_no_localhost_links'] = all('127.0.0.1' not in l.get('uri', '') for p in doc for l in p.get_links())
                    await call('Emulation.setEmulatedMedia', {'media': 'screen'})
                    await call('Emulation.setDeviceMetricsOverride', {'width': 1200, 'height': 650, 'deviceScaleFactor': 1, 'mobile': False})
                    for figure in ('output', 'latency', 'cost', 'residency', 'categories', 'state'):
                        await navigate(f'reports/executive/{figure}.svg')
                        shot = await call('Page.captureScreenshot', {'format': 'png'})
                        (OUT / f'{figure}.png').write_bytes(base64.b64decode(shot['data']))
                checks['no_browser_exceptions'] = not errors
            finally:
                browser.terminate()
                browser.wait(timeout=10)
    finally:
        server.shutdown()
        server.server_close()
    sheet = Image.new('RGB', (1200, 600), '#e9e7e2')
    draw = ImageDraw.Draw(sheet)
    for i in range(10):
        image = Image.open(images / f'slide-{i+1}.png').convert('RGB')
        image.thumbnail((236, 260))
        x, y = (i % 5)*240, (i // 5)*300
        sheet.paste(image, (x, y+24))
        draw.text((x+8, y+4), f'{i+1:02d}', fill='#17272e')
    sheet.save(images / 'contact-sheet.png')
    result = {"status": "pass" if all(checks.values()) else "fail", "checks": checks, "errors": errors}
    (images / 'verification.json').write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    if result['status'] != 'pass':
        raise SystemExit(1)


if __name__ == '__main__':
    asyncio.run(export())
