"""Flipkart bulk image upload in ONE step with Playwright (no per-image clicking).

How it works
  Flipkart's "Add Listings in Bulk > upload images" step has a hidden <input type=file webkitdirectory>.
  When you hand it a folder laid out as  <root>/<SKU>/<n>.jpg  it creates one row per sub-folder (= SKU) and uploads
  every image in it to Flipkart's own image host (fkmpimages.flixcart.com). Playwright's set_input_files() accepts a
  DIRECTORY for such inputs, so the whole 38 SKUs x 5 images = 190 files go in with a single call.
  Then "Generate Catalog File" -> "Download template" gives an xls whose Main/Other Image URL columns are already
  filled with the Flipkart-hosted URLs; we read them into fixed/flipkart_image_urls.json (SKU -> 5 URLs).

Usage
  python flipkart_bulk_images.py stage                # build fk-stage/<SKU>/1..5.jpg from the flat <SKU>__<n>.jpg files
  python flipkart_bulk_images.py upload               # headed Chrome with a saved profile; log in once by hand
  python flipkart_bulk_images.py selftest             # proves the folder -> rows mechanism on a local page (no login needed)

Login: the profile in .flipkart-profile keeps the session, so you only type the password the first time
(the script never reads or types credentials).
"""
import json, re, shutil, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).parent
SRC = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "fk-final"            # flat <SKU>__<n>.jpg files
STAGE = ROOT / "fk-stage"
PROFILE = ROOT / ".flipkart-profile"
BULK_URL = "https://seller.flipkart.com/index.html#dashboard/addListings/bulk"


def stage():
    shutil.rmtree(STAGE, ignore_errors=True)
    n = 0
    for f in sorted(SRC.glob("*__*.jpg")):
        sku, num = f.stem.split("__")
        d = STAGE / sku
        d.mkdir(parents=True, exist_ok=True)
        shutil.copy(f, d / f"{num}.jpg")
        n += 1
    print(f"staged {n} images in {len(list(STAGE.iterdir()))} SKU folders -> {STAGE}")


def upload():
    if not STAGE.exists():
        stage()
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(str(PROFILE), channel="chrome", headless=False, accept_downloads=True,
                                                   viewport={"width": 1500, "height": 900})
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto("https://seller.flipkart.com/")
        print("If the login page shows, sign in by hand (first run only). Waiting for the dashboard...")
        page.wait_for_url(re.compile(r"seller\.flipkart\.com/index\.html#dashboard"), timeout=600_000)
        # The vertical/brand wizard is UI driven: open Listings > Add Listing > Bulk, pick the category and brand once by hand.
        page.goto(BULK_URL)
        print("Pick the vertical + brand until the 'upload images' step is visible, then press Enter here.")
        input()
        # THE ONE CALL: the whole folder tree goes into the hidden directory input.
        folder_input = page.locator("input[type=file][webkitdirectory]").first
        folder_input.set_input_files(str(STAGE))
        page.wait_for_function("document.querySelectorAll('img[src*=flixcart]').length >= %d" % (len(list(STAGE.iterdir())) * 5 - 5),
                               timeout=900_000)
        print("images uploaded to Flipkart's host")
        page.get_by_role("button", name=re.compile("Generate Catalog File", re.I)).click()
        page.get_by_text(re.compile("Download template", re.I)).wait_for(timeout=300_000)
        with page.expect_download() as dl:
            page.get_by_text(re.compile("Download template", re.I)).click()
        tpl = ROOT / "fixed" / "flipkart_catalog_template.xls"
        dl.value.save_as(str(tpl))
        print("template saved", tpl)
        ctx.close()
    extract_urls(tpl)


def extract_urls(tpl):
    import pandas as pd
    d = pd.read_excel(tpl, sheet_name="bangle_bracelet_armlet", header=None)
    hdr = [str(v) for v in d.iloc[0].tolist()]
    cols = [hdr.index(h) for h in ("Main Image URL", "Other Image URL 1", "Other Image URL 2", "Other Image URL 3", "Other Image URL 4")]
    sku = hdr.index("Seller SKU ID")
    m = {str(d.iloc[r, sku]): [d.iloc[r, c] for c in cols] for r in range(4, d.shape[0]) if str(d.iloc[r, sku]) != "nan"}
    (ROOT / "fixed" / "flipkart_image_urls.json").write_text(json.dumps(m, indent=1))
    print("SKU -> image URLs:", len(m))


def selftest():
    """Local proof that ONE set_input_files(folder) call yields File objects grouped by SKU sub-folder."""
    if not STAGE.exists():
        stage()
    html = ("<input id=f type=file webkitdirectory multiple><script>document.getElementById('f').onchange=e=>{"
            "const g={};for(const f of e.target.files){const [r,s]=f.webkitRelativePath.split('/');(g[s]=g[s]||[]).push(f.name)}"
            "document.title=JSON.stringify(g)}</script>")
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        pg.set_content(html)
        pg.locator("#f").set_input_files(str(STAGE))
        pg.wait_for_function("document.title.startsWith('{')")
        g = json.loads(pg.title())
        b.close()
    print("SKU groups seen by the page:", len(g), "| images per SKU:", sorted({len(v) for v in g.values()}), "| total:", sum(len(v) for v in g.values()))


if __name__ == "__main__":
    {"stage": stage, "upload": upload, "selftest": selftest}[sys.argv[1]]()
