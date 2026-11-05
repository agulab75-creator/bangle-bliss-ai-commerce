"""Playwright Drive uploader for the FINAL Flipkart images (flipkart-images/v6, <SKU>__<n>.jpg). Waits for the owner to finish Google's 'Verify it's you' in the
opened window, then: create folder, upload (resumable), share 'Anyone with the link', write flipkart-images/drive-urls-v6.json (export=view links)."""
import asyncio, json, re, time
from pathlib import Path
from playwright.async_api import async_playwright
from cdp_wake import wake
import fk_drive_upload as u

ROOT = Path(__file__).parent
SRC = ROOT / "flipkart-images" / "v6"
u.FOLDER = "BB Flipkart v6 final"
u.STATE = ROOT / "flipkart-images" / "drive-folder-v6.json"
import os
u.FILES = sorted(SRC.glob("*.jpg")) + sorted((ROOT / "flipkart-images" / "v7").glob("*__4w.jpg"))
OUT = ROOT / "flipkart-images" / "drive-urls-v6.json"
DBG = ROOT / "flipkart-images"


async def wait_login(page, minutes=30):
    """Open Drive once, then only WATCH the url (never reload) so the owner can finish Google's verification undisturbed."""
    try:
        await page.goto("https://drive.google.com/drive/my-drive", wait_until="domcontentloaded", timeout=60000)
    except Exception:
        pass
    end = time.time() + minutes * 60; last = 0
    while time.time() < end:
        await page.wait_for_timeout(3000)
        url = page.url
        if "accounts.google.com" not in url and "drive.google.com/drive" in url:
            await page.wait_for_timeout(4000); print("LOGGED IN", flush=True); return True
        if time.time() - last > 60:
            print("waiting for owner to verify in the Chrome window...", flush=True); last = time.time()
    return False


async def share_public(page):
    await page.goto("https://drive.google.com/drive/my-drive", wait_until="domcontentloaded", timeout=60000); await page.wait_for_timeout(7000)
    row = page.locator("tr[data-id]").filter(has_text=u.FOLDER).first
    await row.wait_for(timeout=90000); await row.click(); await page.wait_for_timeout(800)
    await page.keyboard.press("Control+Alt+a"); await page.wait_for_timeout(3500)
    await page.screenshot(path=str(DBG / "dbg-v6-share-1.png"))
    # the share dialog lives in an iframe: find the frame that shows "General access"
    fr = None
    for _ in range(20):
        for f in page.frames:
            try:
                if await f.get_by_text("General access").count():
                    fr = f; break
            except Exception:
                pass
        if fr: break
        await page.wait_for_timeout(1000)
    fr = fr or page.main_frame
    if not await fr.locator("text=Restricted").count():
        print("already public", flush=True)
    else:
        # the "Restricted" label is aria-hidden inside the general-access button; a forced click opens the menu
        await fr.locator("text=Restricted").first.click(force=True); await page.wait_for_timeout(2000)
        await page.screenshot(path=str(DBG / "dbg-v6-share-2.png"))
        await fr.get_by_role("menuitemradio", name=re.compile("Anyone with the link")).first.click(); await page.wait_for_timeout(3000)
    await page.screenshot(path=str(DBG / "dbg-v6-share-3.png"))
    done = fr.get_by_role("button", name="Done")
    if await done.count(): await done.first.click(); await page.wait_for_timeout(1500)
    print("shared", flush=True)


async def present_all(page):
    """Drive only renders ~100 rows of a big folder, so read the list A-Z, then Z-A, and merge."""
    a = await u.present(page)
    hdr = page.get_by_role("columnheader", name=re.compile("^Name")).first
    if not await hdr.count():
        hdr = page.get_by_text("Name", exact=True).first
    await hdr.click(); await page.wait_for_timeout(4000)
    b = await u.present(page)
    await hdr.click(); await page.wait_for_timeout(3000)
    a.update(b)
    return a


async def upload_batch(page, batch):
    """Upload one batch and wait for Drive's own panel to say 'N uploads complete' (the row count is unreliable)."""
    for attempt in range(3):
        try:
            close = page.locator('[aria-label="Close"]').filter(has=page.locator("svg")).last
            if await page.get_by_text(re.compile(r"uploads? complete")).count() and await close.count():
                await close.click(); await page.wait_for_timeout(800)
            await page.keyboard.press("Escape"); await page.wait_for_timeout(800)
            await page.get_by_role("button", name="New").first.click()
            async with page.expect_file_chooser(timeout=15000) as fc:
                await page.get_by_role("menuitem", name="File upload").click(timeout=10000)
            await (await fc.value).set_files([str(f) for f in batch])
            break
        except Exception as ex:
            print("  retry", attempt, str(ex)[:80], flush=True)
            await page.goto(page.url, wait_until="domcontentloaded", timeout=60000); await page.wait_for_timeout(6000)
    pat = re.compile(rf"{len(batch)} uploads? complete")
    for _ in range(90):
        await page.wait_for_timeout(2000)
        if pat.search(await page.evaluate("document.body.innerText")):
            print("  batch ok", batch[0].name, "..", batch[-1].name, flush=True); return True
    print("  batch NOT confirmed", batch[0].name, flush=True); return False


async def main():
    async with async_playwright() as pw:
        # Attach to the Chrome started with --remote-debugging-port=9223 --user-data-dir=.shopify_chrome_profile
        # (banglebliss Google account already signed in; Google blocks sign-in inside Playwright-launched browsers).
        wake(int(__import__('os').environ.get('FK_CDP_PORT', '9224')), "drive.google.com")
        browser = await pw.chromium.connect_over_cdp(f"http://127.0.0.1:{__import__('os').environ.get('FK_CDP_PORT', '9224')}", timeout=90000)
        ctx = browser.contexts[0]
        page = await ctx.new_page(); await page.bring_to_front()
        if not await wait_login(page): print("login timeout"); return
        url = await u.open_or_create_folder(page); print("folder", url, flush=True)
        have = await present_all(page); todo = [f for f in u.FILES if f.name not in have]
        print(len(have), "present,", len(todo), "to upload", flush=True)
        for i in range(0, len(todo), 10):
            await upload_batch(page, todo[i:i + 10])
        if todo:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000); await page.wait_for_timeout(8000)
        have = await present_all(page)
        miss = [f.name for f in u.FILES if f.name not in have]; print("final", len(have), "missing", miss, flush=True)
        OUT.write_text(json.dumps({k: f"https://drive.google.com/uc?export=view&id={v}" for k, v in have.items()}, indent=1))
        await share_public(page)
        print("DONE", OUT, flush=True)
        await page.close()

async def share_only():
    async with async_playwright() as pw:
        wake(int(__import__('os').environ.get('FK_CDP_PORT', '9224')), "drive.google.com")
        browser = await pw.chromium.connect_over_cdp(f"http://127.0.0.1:{__import__('os').environ.get('FK_CDP_PORT', '9224')}", timeout=90000)
        page = await browser.contexts[0].new_page(); await page.bring_to_front()
        await share_public(page); print("shared", flush=True); await page.close()

import sys
asyncio.run(share_only() if sys.argv[1:] == ["share"] else main())
