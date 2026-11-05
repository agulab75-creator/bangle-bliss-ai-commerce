"""Tiny raw-DevTools helper: run steps in ONE temporary tab of the 9223 Chrome without touching other tabs.
from fk_cdp_tab import Tab;  async with Tab() as t: await t.go(url); await t.click_text("Downloads"); ..."""
import asyncio, json, urllib.request
import websockets

import os
BASE = f"http://127.0.0.1:{os.environ.get('FK_CDP_PORT', '9224')}"


async def allow_downloads(path):
    """Browser-level: save downloads of every tab into `path` (Page.setDownloadBehavior alone is ignored)."""
    v = json.load(urllib.request.urlopen(f"{BASE}/json/version"))
    async with websockets.connect(v["webSocketDebuggerUrl"], max_size=None) as b:
        await b.send(json.dumps({"id": 1, "method": "Browser.setDownloadBehavior",
                                 "params": {"behavior": "allow", "downloadPath": str(path), "eventsEnabled": True}}))
        await asyncio.wait_for(b.recv(), 20)


class Tab:
    async def __aenter__(self):
        self.info = json.load(urllib.request.urlopen(urllib.request.Request(f"{BASE}/json/new?about:blank", method="PUT")))
        self.ws = await websockets.connect(self.info["webSocketDebuggerUrl"], max_size=None, open_timeout=20)
        self.n = 0
        await self.call("Page.bringToFront")                      # background tabs get frozen and stop answering
        await self.call("Emulation.setFocusEmulationEnabled", {"enabled": True})
        await self.call("Emulation.setDeviceMetricsOverride", {"width": 1920, "height": 1000, "deviceScaleFactor": 1, "mobile": False})
        return self

    async def __aexit__(self, *a):
        await self.ws.close()
        urllib.request.urlopen(f"{BASE}/json/close/{self.info['id']}")

    async def call(self, method, params=None):
        self.n += 1; my = self.n
        await self.ws.send(json.dumps({"id": my, "method": method, "params": params or {}}))
        while True:
            m = json.loads(await asyncio.wait_for(self.ws.recv(), 90))
            if m.get("id") == my:
                return m

    async def js(self, expr):
        r = await self.call("Runtime.evaluate", {"expression": expr, "returnByValue": True, "awaitPromise": True})
        return r.get("result", {}).get("result", {}).get("value")

    async def go(self, url, wait=12):
        await self.call("Page.navigate", {"url": url}); await asyncio.sleep(wait)

    async def click_text(self, text, wait=2, last=True):
        """Click the innermost visible element whose own text equals `text`."""
        ok = await self.js("""(() => { const t = %s;
          const els = [...document.querySelectorAll('*')].filter(e => (e.innerText || '').trim() === t && e.getClientRects().length);
          const inner = els.filter(e => ![...e.children].some(c => (c.innerText || '').trim() === t));
          const el = inner[%s]; if (!el) return false; el.scrollIntoView({block:'center'}); el.click(); return true; })()""" % (json.dumps(text), "inner.length-1" if last else "0"))
        await asyncio.sleep(wait)
        return ok

    async def mouse_click(self, x, y):
        """Trusted click (pages ignore synthetic JS clicks for downloads)."""
        for t in ("mousePressed", "mouseReleased"):
            await self.call("Input.dispatchMouseEvent", {"type": t, "x": x, "y": y, "button": "left", "clickCount": 1})

    async def shot(self, path):
        import base64
        r = await self.call("Page.captureScreenshot", {"format": "jpeg", "quality": 60})
        open(path, "wb").write(base64.b64decode(r["result"]["data"]))

    async def text(self):
        return await self.js("document.body.innerText") or ""
