"""Poll a Flipkart bulk-edit request until QC finishes, WITHOUT Playwright (no tab-waking): opens ONE new tab in the
9223 Chrome via the DevTools HTTP API, reads the QC counts over that tab's own websocket, closes the tab.
Usage: python fk_qc_poll.py <request-id> [minutes_between_checks=45] [max_hours=30]
Prints one line per check; exits when 'QC Progress' reaches 0."""
import asyncio, json, re, sys, time, urllib.request
import websockets

RID = sys.argv[1]
EVERY = float(sys.argv[2]) if len(sys.argv) > 2 else 45
MAX_H = float(sys.argv[3]) if len(sys.argv) > 3 else 30
import os
BASE = f"http://127.0.0.1:{os.environ.get('FK_CDP_PORT', '9224')}"
URL = ("https://seller.flipkart.com/index.html#dashboard/addListings/bulk?vertical=bangle_bracelet_armlet"
       f"&requestId={RID}&initialIndex=0&context=BULK_EDIT")
PAT = re.compile(r"(\d+)\s*Listings Submitted\s*(\d+)\s*QC (?:In )?Progress\s*(\d+)\s*QC Passed\s*(\d+)\s*QC Failed", re.I)


async def check():
    req = urllib.request.Request(f"{BASE}/json/new?about:blank", method="PUT")
    tab = json.load(urllib.request.urlopen(req))
    try:
        async with websockets.connect(tab["webSocketDebuggerUrl"], max_size=None, open_timeout=20) as ws:
            n = 0

            async def call(method, params=None):
                nonlocal n
                n += 1; my = n
                await ws.send(json.dumps({"id": my, "method": method, "params": params or {}}))
                while True:
                    m = json.loads(await asyncio.wait_for(ws.recv(), 60))
                    if m.get("id") == my:
                        return m

            async def js(expr):
                r = await call("Runtime.evaluate", {"expression": expr, "returnByValue": True, "awaitPromise": True})
                return r.get("result", {}).get("result", {}).get("value")

            await call("Page.navigate", {"url": URL})
            await asyncio.sleep(14)
            await js("[...document.querySelectorAll('button')].filter(b=>/View QC Status/.test(b.innerText)).pop()?.click()")
            await asyncio.sleep(8)
            text = await js("document.body.innerText") or ""
            if "BANGLEBLIS" not in text:
                return "NOT SIGNED IN"
            m = PAT.search(text)
            return m.groups() if m else "counts not found"
    finally:
        urllib.request.urlopen(f"{BASE}/json/close/{tab['id']}")


async def main():
    end = time.time() + MAX_H * 3600
    while time.time() < end:
        try:
            res = await check()
        except Exception as e:
            res = f"check error {type(e).__name__}: {str(e)[:80]}"
        print(time.strftime("%d %b %H:%M"), RID, "submitted/progress/passed/failed =", res, flush=True)
        if isinstance(res, tuple) and res[0] != "0" and res[1] == "0":
            print("QC FINISHED", flush=True); return
        await asyncio.sleep(EVERY * 60)
    print("gave up waiting", flush=True)

asyncio.run(main())
