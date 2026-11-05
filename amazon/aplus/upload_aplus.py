"""Playwright automation for Amazon Seller Central > A+ Content Manager (amazon.in, Basic A+).

One-time login (you type the password / 2FA yourself, the script never sees it):
    python aplus/upload_aplus.py --login
Build the draft only (safe: saves a draft, does not apply or submit):
    python aplus/upload_aplus.py --spec aplus/ksg_global_spec.json
Build + apply to the ASIN family:
    python aplus/upload_aplus.py --spec aplus/ksg_global_spec.json --apply
Build + apply + submit for review (outward-facing, needs the flag):
    python aplus/upload_aplus.py --spec aplus/ksg_global_spec.json --apply --submit

Default engine is your REAL installed Chrome: the script starts chrome.exe with --remote-debugging-port=9333 and its
own profile folder (%LOCALAPPDATA%/BangleBliss-Chrome), then attaches Playwright over CDP. No automation flags are
injected, so it looks like a normal browser. Your everyday Chrome profile cannot be driven (Chrome 136+ blocks the
debug port on the default profile, and its cookies are bound to it), so log in once in this one window.
Use --engine playwright for the old bundled-Chromium mode.

The locators come from walking this UI by hand (2026-10-17). If Amazon changes the page a step fails with a
screenshot in aplus/out/shots/; re-run with --slow 300 to watch it.
"""
import argparse, asyncio, json, os, re, subprocess, time, urllib.request
from pathlib import Path
from playwright.async_api import async_playwright, Page, expect

ROOT = Path(__file__).resolve().parent.parent
PROFILE = ROOT / ".aplus-profile"                    # only used by --engine playwright
CHROME_EXE = next((p for p in [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                               r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                               os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")]
                   if os.path.exists(p)), None)
# Real Chrome, started normally (no automation flags), with a debug port. Chrome 136+ refuses a debug port on the
# DEFAULT profile, so it gets its own profile folder: log in once there and it stays logged in.
CHROME_PROFILE = Path(os.path.expandvars(r"%LOCALAPPDATA%\BangleBliss-Chrome"))
CDP_PORT = 9333                                       # 9222 is taken by your everyday Chrome
SHOTS = ROOT / "aplus" / "out" / "shots"
MANAGER = "https://sellercentral.amazon.in/enhanced-content/content-manager"
HEADLINE = "kat-input[placeholder='Enter headline text']"
EMPTY_SLOT = re.compile(r"Click to add image|Add background image")


async def shot(page: Page, name: str):
    SHOTS.mkdir(parents=True, exist_ok=True)
    try:
        await page.screenshot(path=str(SHOTS / f"{int(time.time())}-{name}.png"), timeout=8000)
    except Exception as e:                      # a slow screenshot must never fail the run
        print("screenshot skipped:", name, str(e)[:60])


def cdp_alive() -> bool:
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{CDP_PORT}/json/version", timeout=2)
        return True
    except Exception:
        return False


def ensure_real_chrome():
    """Start installed Chrome with a debug port + its own profile, unless one is already up."""
    if cdp_alive():
        return
    if not CHROME_EXE:
        raise SystemExit("Chrome not found. Install Chrome or use --engine playwright.")
    CHROME_PROFILE.mkdir(parents=True, exist_ok=True)
    subprocess.Popen([CHROME_EXE, f"--remote-debugging-port={CDP_PORT}", f"--user-data-dir={CHROME_PROFILE}",
                      "--no-first-run", "--no-default-browser-check", "--window-size=1440,900", "about:blank"])
    for _ in range(40):
        if cdp_alive():
            return
        time.sleep(0.5)
    raise SystemExit("Chrome started but the debug port never opened. Close any Chrome using that profile and retry.")


async def open_page(pw, engine: str, slow: int = 0):
    """Return (page, close). engine 'chrome' = attach to real Chrome over CDP; 'playwright' = bundled Chromium."""
    if engine == "chrome":
        ensure_real_chrome()
        browser = await pw.chromium.connect_over_cdp(f"http://127.0.0.1:{CDP_PORT}", slow_mo=slow)
        ctx = browser.contexts[0]
        page = await ctx.new_page()
        async def close():                     # leave Chrome open; just drop our tab + connection
            await page.close()
            await browser.close()
        return page, close
    ctx = await pw.chromium.launch_persistent_context(str(PROFILE), headless=False, slow_mo=slow,
                                                      viewport={"width": 1440, "height": 900})
    page = ctx.pages[0] if ctx.pages else await ctx.new_page()
    return page, ctx.close


async def login(pw, engine: str):
    page, close = await open_page(pw, engine)
    await page.goto("https://sellercentral.amazon.in/")
    print("Log in to Seller Central in the opened window (password + 2FA). Waiting up to 10 minutes...")
    await page.wait_for_url(re.compile(r"sellercentral\.amazon\.in/(?!.*(signin|ap/))"), timeout=600_000)
    await page.goto(MANAGER)
    await page.wait_for_load_state("domcontentloaded")
    print("Logged in. Session saved in", CHROME_PROFILE if engine == "chrome" else PROFILE)
    await close()


async def start_document(page: Page, name: str):
    await page.goto(MANAGER)
    await page.wait_for_load_state("domcontentloaded")
    await page.get_by_text("Start creating A+ content").first.click()
    await page.get_by_role("button", name=re.compile(r"Create Basic A\+")).click()
    await page.wait_for_selector("text=Content details")
    # Content name is the first <kat-input> web component (its real <input> lives in a shadow root and the page
    # also has a global search box), so click the component and type.
    await page.locator("kat-input").first.click()
    await page.keyboard.type(name, delay=15)
    await page.keyboard.press("Tab")


async def add_module(page: Page, type_name: str):
    await page.get_by_role("button", name="Add Module").last.click()
    search = page.get_by_placeholder(re.compile("Search", re.I)).last
    await search.click()
    await search.fill(type_name)
    await page.wait_for_timeout(800)
    modal = page.locator("kat-modal[visible='true']")
    await modal.get_by_text(type_name, exact=True).first.click()   # the filtered preview card (inside the picker only)
    await modal.wait_for(state="hidden", timeout=15_000)
    await page.wait_for_timeout(1200)


async def fill_image(page: Page, img_path: Path, alt: str):
    if len(alt) > 95:
        raise SystemExit(f"alt text over 95 chars (Amazon rejects ~100) ({len(alt)}): {alt[:50]}...")
    await page.get_by_text(EMPTY_SLOT).first.click()                          # first still-empty slot, DOM order
    await page.get_by_role("button", name="Add image", exact=True).click()    # opens the Asset Library
    async with page.expect_file_chooser() as fc:
        await page.get_by_role("button", name=re.compile(r"Upload image", re.I)).first.click()
    await (await fc.value).set_files(str(img_path))
    alt_box = page.locator("kat-input[placeholder='Enter image keywords']").locator("visible=true").first
    await alt_box.wait_for(timeout=30_000)                                    # image details page after upload
    lib_add = page.get_by_role("button", name="Add", exact=True).last
    for attempt in range(4):                                                  # Add stays disabled until alt text commits
        await alt_box.click()
        await page.keyboard.press("Control+A")
        await page.keyboard.type(alt, delay=5)
        await page.keyboard.press("Tab")
        try:
            await expect(lib_add).to_be_enabled(timeout=3000)
            break
        except AssertionError:
            continue
    await page.get_by_role("button", name="Add", exact=True).last.click()     # library -> dialog
    await page.wait_for_timeout(800)
    await page.locator("kat-button[data-component-id='image-modal-add-button']").locator("visible=true").last.click()  # dialog -> module
    await page.locator("kat-button[data-component-id='image-modal-add-button']").locator("visible=true").first.wait_for(state="hidden", timeout=30_000)  # dialog gone (big images take a moment)
    await page.wait_for_timeout(600)


async def fill_texts(page: Page, n_head_before: int, n_body_before: int, headlines, bodies):
    heads = page.locator(HEADLINE)
    bods = page.locator("[contenteditable='true']")
    for i, t in enumerate(headlines):
        if t:
            f = heads.nth(n_head_before + i)
            await f.scroll_into_view_if_needed()
            await f.click()
            await page.keyboard.type(t, delay=5)
    for i, t in enumerate(bodies):
        if t:
            f = bods.nth(n_body_before + i)
            await f.scroll_into_view_if_needed()
            await f.click()
            await page.keyboard.type(t, delay=3)


async def build(page: Page, spec: dict):
    await start_document(page, spec["name"])
    img_dir = ROOT / spec["image_dir"]
    for n, m in enumerate(spec["modules"], 1):
        print(f"module {n}: {m['type']}")
        hb = await page.locator(HEADLINE).count()
        bb = await page.locator("[contenteditable='true']").count()
        await add_module(page, m["type"])
        for im in m["images"]:
            p = img_dir / im["file"]
            if not p.exists():
                raise SystemExit(f"missing image {p}")
            await fill_image(page, p, im["alt"])
        await fill_texts(page, hb, bb, m.get("headlines", []), m.get("bodies", []))
        await shot(page, f"module-{n}")
    await page.get_by_text("Save as draft").first.click()
    await page.wait_for_timeout(3000)
    await shot(page, "draft-saved")


async def open_draft(page: Page, name: str):
    """Reopen an existing document from the manager list by its content name (for --resume)."""
    await page.goto(MANAGER)
    await page.wait_for_load_state("domcontentloaded")
    link = page.get_by_role("link", name=name, exact=True).first      # list shows newest first; no search needed
    await link.wait_for(timeout=30_000)
    await link.click()
    await page.wait_for_load_state("domcontentloaded")
    await page.wait_for_selector("text=Content details")
    edit = page.get_by_role("button", name="Edit", exact=True)
    if await edit.count():                                  # detail view -> editor
        await edit.first.click()
    await page.wait_for_selector("text=Next: Apply ASINs")


async def apply_asins(page: Page, spec: dict):
    await page.get_by_text("Next: Apply ASINs").first.click()
    box = page.get_by_placeholder("Search for ASINs").first
    await page.wait_for_timeout(1500)                       # the box ignores keystrokes right after load
    for attempt in range(4):
        await box.click()
        await page.keyboard.press("Control+A")
        await page.keyboard.press("Backspace")
        await page.keyboard.type(spec["asin"], delay=40)
        await page.keyboard.press("Enter")
        try:
            await page.wait_for_selector("text=Apply content", timeout=8_000)
            break
        except Exception:
            continue
    else:
        raise SystemExit("ASIN search returned nothing after 4 tries, see screenshot")
    if spec.get("apply_to", "parent") == "parent":
        await page.get_by_role("checkbox").locator("visible=true").first.check()   # the parent/family row (first result row)
    await page.get_by_text("Apply content").first.click()
    override = page.get_by_role("button", name="Override", exact=True)       # shown when the ASINs already have live A+
    try:
        await override.wait_for(timeout=5_000)
        print("ASINs already have A+ content: confirming Override (replaces it once the new doc is approved)")
        await override.click()
    except Exception:
        pass
    await page.wait_for_timeout(2500)
    await shot(page, "applied")
    txt = await page.locator("body").inner_text()
    m = re.search(r"Applied ASINs \((\d+)\)", txt)
    print("Applied ASINs:", m.group(1) if m else "?")
    if not m or m.group(1) == "0":
        raise SystemExit("Apply failed, see screenshot")


async def submit(page: Page):
    await page.get_by_text("Next: Review and submit").first.click()
    await page.get_by_text("Submit for approval").first.click()
    await page.get_by_role("button", name="Submit for approval").last.click()   # confirm dialog
    await page.wait_for_selector("text=successfully submitted", timeout=60_000)
    await shot(page, "submitted")
    print("Submitted for approval.")


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--login", action="store_true")
    ap.add_argument("--spec")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--resume", action="store_true", help="reopen the existing draft named in the spec instead of building a new one")
    ap.add_argument("--slow", type=int, default=0, help="slow_mo ms to watch it")
    ap.add_argument("--engine", choices=["chrome", "playwright"], default="chrome",
                    help="chrome = your installed Chrome over CDP (default); playwright = bundled Chromium")
    a = ap.parse_args()
    async with async_playwright() as pw:
        if a.login:
            return await login(pw, a.engine)
        if not a.spec:
            ap.error("--spec or --login required")
        spec = json.load(open(a.spec, encoding="utf-8"))
        page, close = await open_page(pw, a.engine, a.slow)
        page.set_default_timeout(20_000)
        try:
            if a.resume:
                await open_draft(page, spec["name"])
            else:
                await build(page, spec)
            if a.apply:
                await apply_asins(page, spec)
            if a.submit:
                if not a.apply:                              # draft already has its ASINs: just step to Review
                    await page.get_by_text("Next: Apply ASINs").first.click()
                    await page.wait_for_selector("text=Applied ASINs", timeout=30_000)
                await submit(page)
        except Exception:
            await shot(page, "FAILED")
            raise
        finally:
            await close()


if __name__ == "__main__":
    asyncio.run(main())
