"""Download a bulk-edit request's QC error file with ONE trusted click (temporary tab, other tabs untouched) and summarise.
Usage: python fk_qc_errfile.py REQUEST_ID"""
import asyncio, json, shutil, sys, time
from pathlib import Path
from fk_cdp_tab import Tab
from fk_qc_report import summarise, DEST

RID = sys.argv[1] if len(sys.argv) > 1 else ""
URL = ("https://seller.flipkart.com/index.html#dashboard/addListings/bulk?vertical=bangle_bracelet_armlet"
       f"&requestId={RID}&initialIndex=0&context=BULK_EDIT")
POS = """(() => { const t = %s; const els = [...document.querySelectorAll('button,a,span,div')].filter(e => (e.innerText||'').trim() === t && e.getClientRects().length);
  const e = els[els.length - 1]; if (!e) return null; e.scrollIntoView({block: 'center'}); const b = e.getBoundingClientRect(); return {x: b.left + b.width / 2, y: b.top + b.height / 2}; })()"""


async def tclick(t, text, wait=3):
    p = await t.js(POS % json.dumps(text))
    if p:
        await t.mouse_click(p["x"], p["y"])
    await asyncio.sleep(wait)
    return bool(p)


async def main():
    dl = Path.home() / "Downloads"
    async with Tab() as t:
        await t.go(URL, 15)
        print("qc", await tclick(t, "View QC Status", 6), "errors", await tclick(t, "Correct Errors", 4),
              "request", await tclick(t, "Request", 20), flush=True)
        t0 = time.time()
        print("last", await tclick(t, "Last Requested File", 2), flush=True)
        for _ in range(15):
            new = [p for p in dl.glob("E_bangle*.xls") if p.stat().st_mtime > t0 - 2]
            if new:
                f = DEST / new[0].name; shutil.copy(new[0], f); summarise(f); return
            await asyncio.sleep(4)
    print("error file did not download")

if __name__ == "__main__":
    asyncio.run(main())
