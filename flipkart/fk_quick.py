"""Quick Flipkart fix (18 Oct): slot 5 = white-studio photo (replaces the live size chart), and the two colour changes
that do not clash inside their variant group (KMS-RYP and KSG-EMR -> Multicolor). Runs in ONE temporary tab of the
9223 Chrome over raw DevTools (other tabs untouched).  Usage: python fk_quick.py [build|download|upload|all]"""
import asyncio, json, subprocess, sys, time
from pathlib import Path
import openpyxl
from fk_cdp_tab import Tab, allow_downloads

ROOT = Path(__file__).parent
WORK = ROOT / "flipkart from claude" / "catalog-update-v4"
IN, OUT = WORK / "in", WORK / "out"
for d in (IN, OUT):
    d.mkdir(parents=True, exist_ok=True)
DATA = ROOT / "flipkart from claude" / "flipkart-update-data.xlsx"
DATA_Q = ROOT / "flipkart from claude" / "flipkart-update-data-quick.xlsx"
LINKS = json.loads((ROOT / "flipkart-images" / "drive-urls-v6.json").read_text())
SLOTS = [("Main Image URL", "__1.jpg"), ("Other Image URL 1", "__2.jpg"), ("Other Image URL 2", "__3.jpg"),
         ("Other Image URL 3", "__4w.jpg"), ("Other Image URL 4", "__3.jpg")]
COLOUR = {"KMS-RYP": "Multicolor", "KSG-EMR": "Multicolor"}
LIST = ("https://seller.flipkart.com/index.html#dashboard/listings-management?listingState=ACTIVE"
        "&filters=%7B%22vertical%22%3A%5B%22bangle_bracelet_armlet%22%5D%7D")


def build():
    wb = openpyxl.load_workbook(DATA); ws = wb.active
    hdr = [c.value for c in ws[1]]
    if "Color" not in hdr:
        ws.cell(1, len(hdr) + 1).value = "Color"; hdr.append("Color")
    ix = {h: i + 1 for i, h in enumerate(hdr)}
    for r in range(2, ws.max_row + 1):
        sku = ws.cell(r, 1).value
        if not sku:
            continue
        base = sku.rsplit("-", 1)[0]
        for col, suf in SLOTS:
            ws.cell(r, ix[col]).value = LINKS[f"{base}-24{suf}"]
        ws.cell(r, ix["Color"]).value = COLOUR.get(base)
    wb.save(DATA_Q); print("quick data written", flush=True)


async def download():
    await allow_downloads(IN)
    before = set(IN.glob("E_*.xls"))
    async with Tab() as t:
        await t.go(LIST, 15)
        await t.js("document.querySelector('thead input[type=checkbox]').click()"); await asyncio.sleep(2)
        await t.click_text("All Pages")
        print("dl menu", await t.click_text("Downloads"), "catalog", await t.click_text("Download Catalog File", 8), flush=True)
        if "Downloads History" not in await t.text():
            await t.click_text("Downloads"); print("recent", await t.click_text("View Recent Downloads", 6), flush=True)
        clicked = False; dl = Path.home() / "Downloads"; t0 = time.time()
        for i in range(30):
            r = await t.js("""(() => { const el = [...document.querySelectorAll('*')].find(e => e.children.length === 0 && /^E_bangle-bracelet-armlet_/.test((e.textContent||'').trim()));
              if (!el) return null; const y0 = el.getBoundingClientRect().top + el.getBoundingClientRect().height / 2;
              // right-most visible element on the same row (the download arrow)
              const cands = [...document.querySelectorAll('svg,button,img,a,[role=button]')].map(e => [e, e.getBoundingClientRect()])
                 .filter(([e, b]) => b.width > 0 && Math.abs(b.top + b.height / 2 - y0) < 20);
              if (!cands.length) return null; cands.sort((a, b) => b[1].right - a[1].right); const b = cands[0][1];
              return {x: b.left + b.width / 2, y: b.top + b.height / 2, name: el.textContent.trim()}; })()""")
            if i in (0, 3):
                await t.shot(str(WORK / f"dbg-download-{i}.jpg"))
            if r and not clicked:
                await t.mouse_click(r["x"], r["y"]); clicked = True
            await asyncio.sleep(10)
            new = [p for p in IN.glob("E_*.xls") if p not in before] + [p for p in dl.glob("E_bangle*.xls") if p.stat().st_mtime > t0 and " (" not in p.name]
            if new and new[0].parent == dl:
                import shutil; shutil.copy(new[0], IN / new[0].name); new = [IN / new[0].name]
            if new:
                print("downloaded", new[0].name, flush=True); return new[0]
            print("  waiting for catalog file...", r, flush=True)
    raise SystemExit("catalog file not downloaded")


def fill(src):
    dst = OUT / src.name
    subprocess.run([sys.executable, str(ROOT / "fk_fill_by_sku.py"), str(src), str(dst), str(DATA_Q)], check=True)
    bak = dst.with_suffix(".backup.xls")
    if bak.exists():
        bak.replace(IN / bak.name)
    return dst


async def upload(f):
    async with Tab() as t:
        await t.go(LIST, 15)
        await t.click_text("Uploads"); await t.click_text("Upload Catalog File", 3)
        doc = await t.call("DOM.getDocument", {"depth": -1, "pierce": True})
        q = await t.call("DOM.querySelector", {"nodeId": doc["result"]["root"]["nodeId"], "selector": 'input[type=file][accept*="ms-excel"]'})
        await t.call("DOM.setFileInputFiles", {"files": [str(f.resolve())], "nodeId": q["result"]["nodeId"]})
        await asyncio.sleep(4)
        await t.click_text("Upload", 10)
        txt = await t.text()
        print("UPLOAD", "OK" if "successfully uploaded" in txt else "NOT CONFIRMED", flush=True)


async def main(step):
    if step in ("build", "all"):
        build()
    if step in ("download", "all"):
        src = await download()
    else:
        src = max((p for p in IN.glob("E_*.xls") if not p.name.endswith("backup.xls")), key=lambda p: p.stat().st_mtime, default=None)
    if step in ("upload", "all"):
        dst = fill(src)
        await upload(dst)

if __name__ == "__main__":
    asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else "all"))
