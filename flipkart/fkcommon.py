import sys
sys.path.insert(0, r"<project-dir>")
from playwright.async_api import async_playwright
from cdp_wake import wake
OUT = r"<project-dir>\fk-single"

async def connect(p, match="addListings/single"):
    try:
        wake(9223, "seller.flipkart.com")
    except Exception:
        pass
    b = await p.chromium.connect_over_cdp("http://127.0.0.1:9223")
    pages = [pg for pg in b.contexts[0].pages if "seller.flipkart.com" in pg.url and "dashboard" in pg.url]
    for pg in pages:
        if match in pg.url:
            return pg
    return pages[0]

async def dismiss_popups(page):
    for t in ("View the new page", "Got it", "Close"):
        loc = page.locator(".ReactModal__Overlay").get_by_text(t, exact=True)
        if await loc.count():
            try: await loc.first.click(timeout=3000)
            except Exception: pass
    await page.wait_for_timeout(1500)

import re
async def open_tab(page, name):
    await page.get_by_text(name).first.evaluate("e=>e.click()")
    await page.wait_for_timeout(1500)

def F(page, label):
    """wrapper of one attribute row, found by its label text"""
    lab = page.locator("[class*='AttributeItemLabelName']").filter(has_text=re.compile(rf"^\s*{re.escape(label)}\s*\*?\s*$")).first
    return lab.locator("xpath=ancestor::div[contains(@class,'EditAttributeItemWrapper') or contains(@class,'styles__AttributeWrapper')][1]")

async def set_text(page, label, val):
    inp = F(page, label).locator("input:not([type=radio]):not([type=checkbox]), textarea").first
    await inp.scroll_into_view_if_needed()
    await inp.click()
    await page.keyboard.press("Control+a")
    await page.keyboard.type(str(val), delay=15)
    await page.keyboard.press("Tab")

async def open_select(page, label):
    w = F(page, label)
    await w.evaluate("e=>e.scrollIntoView({block:'start'})")
    await page.wait_for_timeout(300)
    await w.locator("[class*='control'], [class*='Control'], [class*='select'], [class*='Select'], input").first.click()
    await page.wait_for_timeout(500)

async def _click_option(page, val):
    rx = re.compile(r"^\s*(Check(Box(OutlineBlank)?)?)?\s*" + re.escape(val) + r"\s*$")
    # filter the popup list with its search box so the match is on screen
    search = page.locator("div[class*='FilterWrapper'] input[type=text], div[class*='FilterWrapper'] input:not([type])").filter(visible=True)
    if await search.count():
        await search.first.fill(val)
        await page.wait_for_timeout(600)
    for sel in ("ul[class*='NodeList'] li", "div[class*='CheckMarkOptionWrapper']", "[role=option]"):
        opts = page.locator(sel).filter(has_text=rx).filter(visible=True)
        if await opts.count():
            o = opts.first
            inp = o.locator("input")
            if await inp.count():
                await inp.first.evaluate("e=>e.click()")
            else:
                await o.click()
            return True
    return False

async def pick(page, label, val):
    await open_select(page, label)
    if not await _click_option(page, val):
        raise RuntimeError(f"option {val!r} not found for {label}")
    await page.wait_for_timeout(400)
    await close_dropdown(page)

async def close_dropdown(page):
    await page.keyboard.press("Escape")
    await page.mouse.click(1250, 406)
    await page.wait_for_timeout(400)

async def pick_multi(page, label, vals):
    await open_select(page, label)
    for v in vals:
        if not await _click_option(page, v):
            raise RuntimeError(f"option {v!r} not found for {label}")
        await page.wait_for_timeout(300)
    await close_dropdown(page)

async def set_multi_text(page, label, values):
    inp = F(page, label).locator("input:not([type=radio]):not([type=checkbox]), textarea").first
    await inp.evaluate("e=>e.scrollIntoView({block:'center'})")
    await inp.click()
    for v in values:
        await page.keyboard.type(v, delay=8)
        await page.keyboard.press("Enter")
    await page.keyboard.press("Tab")

async def set_area(page, label, val):
    """fast fill for long text (React-safe: fill then type a char to trigger onChange)"""
    inp = F(page, label).locator("textarea, input:not([type=radio]):not([type=checkbox])").first
    await inp.evaluate("e=>e.scrollIntoView({block:'center'})")
    await inp.fill(val[:-1])
    await inp.click()
    await page.keyboard.press("Control+End")
    await page.keyboard.type(val[-1])
    await page.keyboard.press("Tab")

async def reset_multi(page, container, values):
    box = container.locator(".rti--container").first
    await box.evaluate("e=>e.scrollIntoView({block:'center'})")
    n = await container.locator("[class*='SmallPillContainer']").count()
    await box.click(position={"x": 5, "y": 5})
    for _ in range(n + 2):
        await page.keyboard.press("Backspace")
    for v in values:
        await page.keyboard.type(v, delay=5)
        await page.keyboard.press("Enter")
    await page.keyboard.press("Tab")
