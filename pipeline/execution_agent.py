"""
execution_agent.py
Parallel Shopify Magic image generation.

Architecture:
  - Reads image_queue.json produced by creative_director.py
  - Spawns up to MAX_CONCURRENCY Playwright browser workers
  - Workers pull jobs from a shared asyncio.Queue
  - Each worker drives Shopify Magic independently
  - Results are saved to generated/ immediately
  - State is persisted to image_queue.json after every completion
  - Failed jobs are retried up to MAX_RETRIES times
  - Persistent browser profile (.magic-profile) avoids repeated logins

Usage:
    python execution_agent.py "jobs/bangle 1"
    python execution_agent.py "jobs/bangle 1" --workers 2

Requirements:
    pip install playwright
    playwright install chromium
"""

import asyncio
import json
import logging
import time
import re
import os
import urllib.request
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime
import argparse
import pyperclip

from playwright.async_api import async_playwright, BrowserContext, Page, TimeoutError as PWTimeout

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
BASE_DIR        = Path(__file__).resolve().parent
STORE_URL       = "https://admin.shopify.com/store/your-store"
STORE_DOMAIN    = "your-store.myshopify.com"
PROFILE_DIR     = BASE_DIR / ".magic-profile"   # persistent Chromium profile (login survives)
MAX_CONCURRENCY = 4                              # configurable via --workers
MAX_RETRIES     = 3
EXECUTABLE_PATH = None                           # override via --executable (e.g. Comet's comet.exe)
MINIMIZED       = False                          # launch the window minimized (--minimized)
WINDOW_POS      = None                           # e.g. '0,0'
WINDOW_SIZE     = None                           # e.g. '700,500'
TMP             = Path(tempfile.mkdtemp())

# --------------------------------------------------------------------------- #
# Logging
# --------------------------------------------------------------------------- #
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("execution_agent")


# --------------------------------------------------------------------------- #
# Shopify GraphQL helpers (via CLI subprocess — same pattern as upload_images.py)
# --------------------------------------------------------------------------- #
def gql(query: str, variables: dict = None, retries: int = 4) -> dict:
    import uuid
    uid = uuid.uuid4().hex[:8]
    q_file = TMP / f"q_{uid}.graphql"
    v_file = TMP / f"v_{uid}.json"
    o_file = TMP / f"o_{uid}.json"

    q_file.write_text(query, encoding="utf-8")
    cmd = (
        f'shopify store execute --store {STORE_DOMAIN} '
        f'--query-file "{q_file}" --output-file "{o_file}"'
    )
    if variables:
        v_file.write_text(json.dumps(variables), encoding="utf-8")
        cmd += f' --variable-file "{v_file}"'
    if query.lstrip().startswith("mutation"):
        cmd += " --allow-mutations"

    if o_file.exists():
        o_file.unlink()

    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=90)
    except subprocess.TimeoutExpired:
        if retries > 0:
            log.warning("GraphQL subprocess timed out. Retrying...")
            time.sleep(3)
            return gql(query, variables, retries - 1)
        raise RuntimeError("GraphQL call timed out repeatedly.")

    if not o_file.exists():
        if retries > 0:
            time.sleep(3)
            return gql(query, variables, retries - 1)
        raise RuntimeError(f"GraphQL call failed:\n{r.stdout[-400:]}\n{r.stderr[-200:]}")

    data = json.loads(o_file.read_text(encoding="utf-8"))
    return data.get("data", data)


def upload_file_to_shopify(img_path: Path) -> str:
    """Upload a local image to Shopify Files. Returns the numeric file ID."""
    log.info(f"Uploading {img_path.name} to Shopify Files...")

    # Stage
    t = gql(
        "mutation($i:[StagedUploadInput!]!){stagedUploadsCreate(input:$i){"
        "stagedTargets{url resourceUrl parameters{name value}}userErrors{message}}}",
        {"i": [{"filename": img_path.name, "mimeType": "image/jpeg",
                "httpMethod": "POST", "resource": "FILE"}]},
    )
    tg = t["stagedUploadsCreate"]["stagedTargets"][0]

    # Upload bytes via curl
    cmd = ["curl", "-s", "-o", os.devnull, "-w", "%{http_code}", "-X", "POST", tg["url"]]
    for p in tg["parameters"]:
        cmd += ["-F", f"{p['name']}={p['value']}"]
    cmd += ["-F", f"file=@{img_path}"]
    code = subprocess.run(cmd, capture_output=True, text=True).stdout
    if code != "201":
        raise RuntimeError(f"File upload failed (HTTP {code})")

    # Create in Shopify
    fc = gql(
        "mutation($f:[FileCreateInput!]!){fileCreate(files:$f){"
        "files{id}userErrors{message}}}",
        {"f": [{"originalSource": tg["resourceUrl"],
                "contentType": "IMAGE",
                "alt": f"Source: {img_path.stem}"}]},
    )
    fid_gid = fc["fileCreate"]["files"][0]["id"]

    # Wait for READY
    for _ in range(30):
        st = gql(
            'query($id:ID!){node(id:$id){... on MediaImage{fileStatus}}}',
            {"id": fid_gid},
        )["node"]["fileStatus"]
        if st == "READY":
            break
        time.sleep(3)

    numeric_id = fid_gid.split("/")[-1]
    log.info(f"Uploaded. File ID: {numeric_id}")
    return numeric_id


def download_url(url: str, dest: Path):
    import urllib.request
    import shutil
    with urllib.request.urlopen(url, timeout=15) as response, open(dest, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)


# --------------------------------------------------------------------------- #
# Playwright helpers — one worker drives one browser
# --------------------------------------------------------------------------- #
async def wait_for_generate_button(page: Page, timeout: int = 60_000):
    """Wait for the Generate button on the Shopify Files editor page."""
    gen = page.get_by_role("button", name="Generate", exact=True).first
    await gen.wait_for(timeout=timeout)
    return gen



SAVE_LOCK = Path(__file__).parent / ".magic-save.lock"


async def _acquire_save_lock(timeout: int = 600):
    """Cross-process spin lock (create-exclusive file). Stale locks older than 240 s are broken."""
    t0 = time.time()
    while True:
        try:
            fd = os.open(str(SAVE_LOCK), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            return
        except FileExistsError:
            try:
                if time.time() - SAVE_LOCK.stat().st_mtime > 240:
                    SAVE_LOCK.unlink()
            except OSError:
                pass
            if time.time() - t0 > timeout:
                raise RuntimeError("Timed out waiting for save lock")
            await asyncio.sleep(1.0)


def _release_save_lock():
    try:
        SAVE_LOCK.unlink()
    except OSError:
        pass



CLAIMED = Path(__file__).parent / ".magic-claimed.json"   # file id -> job that owns it (all processes)


def _newest_ids(n: int = 25) -> list[str]:
    nodes = gql("query($n:Int!){files(first:$n,sortKey:CREATED_AT,reverse:true){nodes{id}}}", {"n": n})["files"]["nodes"]
    return [x["id"] for x in nodes]


def _claimed() -> dict:
    try:
        return json.loads(CLAIMED.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _claim(gid: str, owner: str):
    c = _claimed(); c[gid] = owner
    CLAIMED.write_text(json.dumps(c, indent=1), encoding="utf-8")


# Guards the shared OS clipboard: workers run concurrently in one process, so
# copy+paste must be atomic or one worker's prompt can land in another's box.
CLIPBOARD_LOCK = asyncio.Lock()


async def drive_shopify_magic(page: Page, file_id: str, prompt: str, owner: str = "?") -> tuple[str, dict]:
    """
    Navigate to a Shopify Files editor page, trigger Magic, wait for completion,
    click 'Save as new', then resolve the new file ID via GraphQL.

    Returns (new numeric file ID, evidence dict). The new file is identified by being the ONE unclaimed
    file that appeared during our locked save, never just 'the newest file'.
    Raises on failure.
    """
    url = f"{STORE_URL}/content/files/{file_id}"
    log.debug(f"Navigating to {url}")
    await page.goto(url, wait_until="domcontentloaded")

    # --- Click Generate ---
    gen = await wait_for_generate_button(page)
    await gen.scroll_into_view_if_needed()
    await gen.click()

    # --- Fill prompt ---
    # Shopify Magic prompt textarea has placeholder text like "A sunny park..."
    box = page.get_by_label(re.compile(r"sunny park", re.I))
    await box.wait_for(timeout=20_000)
    await box.scroll_into_view_if_needed()
    # Clear any existing text, then paste (much faster than typing char-by-char;
    # lock held only for the copy+paste since the clipboard is process-wide)
    async with CLIPBOARD_LOCK:
        await asyncio.to_thread(pyperclip.copy, prompt)
        await box.click(click_count=3)
        await page.keyboard.press("Backspace")
        await page.keyboard.press("Control+V")
    await asyncio.sleep(0.8)
    await page.keyboard.press("Enter")

    # --- Wait for generation to complete ---
    # Magic is done when a "Save" button (exact label) becomes enabled.
    log.debug("Waiting for Magic to finish...")
    save_btn = None
    deadline = time.time() + 300  # 5 min max
    await asyncio.sleep(8)         # give it time to start

    # Submission can silently no-op on long prompts (Enter lands as a newline, or an
    # autocomplete/suggestion row eats the keypress) - if nothing looks like it started
    # generating yet, re-focus the box and press Enter again before committing to the long poll.
    def _looks_like_generating():
        return page.locator("text=/generating|creating|working on it/i").count()

    if await _looks_like_generating() == 0:
        try:
            await box.click()
            await page.keyboard.press("End")
            await page.keyboard.press("Enter")
            await asyncio.sleep(5)
        except Exception:
            pass

    while time.time() < deadline:
        cands = page.locator("button").filter(has_text=re.compile(r"^\s*Save\s*$"))
        count = await cands.count()
        for i in range(count):
            c = cands.nth(i)
            try:
                if await c.is_visible() and await c.is_enabled():
                    save_btn = c
                    break
            except Exception:
                pass
        if save_btn:
            break
        await asyncio.sleep(2)

    if not save_btn:
        raise RuntimeError("Magic did not finish within 5 minutes")

    await asyncio.sleep(3)  # let the image fully render

    # Serialize the save + 'newest file' lookup across parallel worker processes (race otherwise
    # hands one worker another worker's image).
    await _acquire_save_lock()
    try:
        # --- Click 'Save as new' via the dropdown arrow ---
        save_as_new = page.locator("button:visible").filter(has_text=re.compile(r"save as new", re.I)).first
        _before = set(_newest_ids())
        url_before = page.url
        opened = False
        for up in ("xpath=..", "xpath=../..", "xpath=../../.."):
            group = save_btn.locator(up)
            btns  = group.locator("button:visible")
            count = await btns.count()
            for i in range(count):
                b = btns.nth(i)
                try:
                    txt = (await b.inner_text() or "").strip()
                    if txt:
                        continue  # skip labeled buttons; arrow has empty text
                    await b.click(timeout=3_000)
                    await save_as_new.wait_for(state="visible", timeout=3_000)
                    await save_as_new.click(timeout=5_000)
                    opened = True
                    break
                except Exception:
                    await page.keyboard.press("Escape")
                    await asyncio.sleep(0.4)
            if opened:
                break

        if not opened:
            raise RuntimeError("Could not open Save → Save as new dropdown")

        # --- Resolve the new file ID: exactly one unclaimed file must appear during our locked save ---
        taken = set(_claimed())
        fresh = []
        t_end = time.time() + 120
        while time.time() < t_end:
            await asyncio.sleep(4)
            fresh = [g for g in _newest_ids() if g not in _before and g not in taken]
            if fresh:
                await asyncio.sleep(4)   # let a second file (a foreign save) show up before deciding
                fresh = [g for g in _newest_ids() if g not in _before and g not in taken]
                break
        if len(fresh) != 1:
            raise RuntimeError(f"Save as new: expected 1 new unclaimed file, saw {len(fresh)} {fresh}")
        new_gid = fresh[0]
        m = re.search(r"/content/files/(\d+)", page.url)   # the editor navigates to the saved copy: strongest proof of identity
        if m and m.group(1) != str(file_id):
            if f"gid://shopify/MediaImage/{m.group(1)}" != new_gid:
                raise RuntimeError(f"Save as new: page URL says {m.group(1)} but new file is {new_gid}")
        _claim(new_gid, owner)
        evidence = {"source_fid": file_id, "new_gid": new_gid, "url_before": url_before, "url_after": page.url,
                    "saved_at": datetime.now().isoformat()}
        return new_gid.split("/")[-1], evidence
    finally:
        _release_save_lock()


# --------------------------------------------------------------------------- #
# Queue state helpers
# --------------------------------------------------------------------------- #
def load_queue(queue_file: Path) -> list[dict]:
    with open(queue_file) as f:
        return json.load(f)


def save_queue(queue_file: Path, jobs: list[dict]):
    """Atomic write to avoid corruption if the process dies mid-write."""
    tmp = queue_file.with_suffix(".tmp")
    with open(tmp, "w") as f:
        json.dump(jobs, f, indent=4)
    tmp.replace(queue_file)


def get_pending_jobs(jobs: list[dict]) -> list[dict]:
    return [j for j in jobs if j.get("status") in ("pending", "failed", "needs_human_review")]


def _record_shot(job_dir: Path, shot_id: str, info: dict):
    """Per-colour manifest: which Shopify file became which saved image, so nothing can be confused later."""
    f = job_dir / "manifest.json"
    try:
        m = json.loads(f.read_text(encoding="utf-8"))
    except Exception:
        m = {}
    m.setdefault("shots", {})[shot_id] = info
    f.write_text(json.dumps(m, indent=1), encoding="utf-8")


# --------------------------------------------------------------------------- #
# Worker
# --------------------------------------------------------------------------- #
async def worker(
    worker_id: int,
    job_queue: asyncio.Queue,
    all_jobs: list[dict],
    queue_file: Path,
    generated_dir: Path,
    source_file_id: str,
    queue_lock: asyncio.Lock,
    playwright,
):
    """
    One worker = one persistent browser context.
    Pulls jobs from job_queue, drives Shopify Magic, saves result.
    """
    log.info(f"[W{worker_id}] Starting browser...")

    # For worker 1, we use the root profile to keep your existing Shopify login.
    # For extra workers, they would need a cloned profile, but we'll stick to 1 profile for now.
    profile = PROFILE_DIR if worker_id == 1 else PROFILE_DIR / f"worker-{worker_id}"
    
    # Clean up any stale crash locks before launching
    lock_file = profile / "SingletonLock"
    if lock_file.exists():
        try: lock_file.unlink()
        except Exception: pass
        
    launch_args = ["--start-minimized"] if MINIMIZED else []
    if WINDOW_POS:
        launch_args.append(f"--window-position={WINDOW_POS}")
    if WINDOW_SIZE:
        launch_args.append(f"--window-size={WINDOW_SIZE}")
    ctx: BrowserContext = await playwright.chromium.launch_persistent_context(
        str(profile),
        headless=False,  # must be False to avoid Cloudflare block
        viewport={"width": 1280, "height": 800},
        executable_path=EXECUTABLE_PATH,
        args=launch_args,
    )
    page: Page = ctx.pages[0] if ctx.pages else await ctx.new_page()

    # Check login — navigate to store; if redirected to accounts.shopify.com we need manual login
    await page.goto(f"{STORE_URL}/content/files", wait_until="domcontentloaded")
    for _ in range(120):  # wait up to 4 min for manual login
        u = page.url
        if "admin.shopify.com/store" in u and "accounts.shopify.com" not in u:
            break
        await asyncio.sleep(2)
    log.info(f"[W{worker_id}] Logged in.")

    while True:
        try:
            job_id: str = job_queue.get_nowait()
        except asyncio.QueueEmpty:
            break

        # Find the job dict
        job = next((j for j in all_jobs if j["id"] == job_id), None)
        if job is None:
            job_queue.task_done()
            continue

        retries = job.get("retries", 0)
        log.info(f"[W{worker_id}] Processing job {job['id']} (attempt {retries + 1})")
        is_regen = queue_file.name == "image_queue_regen.json"
        dest_filename = f"{job['id']}_regen.png" if is_regen else f"{job['id']}.png"
        dest = generated_dir / dest_filename
        target_fid = job.get("target_file_id") or source_file_id

        # Skip if already successfully saved
        if dest.exists() and job["status"] == "success":
            log.info(f"[W{worker_id}] Job {job['id']} already done. Skipping.")
            job_queue.task_done()
            continue

        try:
            owner = f"{generated_dir.parent.name}/{job['id']}"
            new_fid, evidence = await drive_shopify_magic(page, target_fid, job["prompt"], owner)

            # Download from Shopify
            res = gql(
                'query($id:ID!){node(id:$id){... on MediaImage{image{url}}}}',
                {"id": f"gid://shopify/MediaImage/{new_fid}"},
            )
            img_url = res["node"]["image"]["url"]
            download_url(img_url, dest)

            if not dest.exists() or dest.stat().st_size < 10_000:
                raise RuntimeError(f"Downloaded file is missing or too small: {dest}")

            # If this is a regen, preserve original as _v1.png for comparison
            orig_dest = generated_dir / f"{job['id']}.png"
            v1_dest = generated_dir / f"{job['id']}_v1.png"
            if is_regen and orig_dest.exists() and not v1_dest.exists():
                try:
                    import shutil
                    shutil.copy2(orig_dest, v1_dest)
                except Exception:
                    pass

            import hashlib
            sha = hashlib.sha1(dest.read_bytes()).hexdigest()
            _record_shot(generated_dir.parent, job["id"], {"file": dest.name, "fid": new_fid, "sha1": sha, "prompt": job["prompt"], **evidence})
            log.info(f"[W{worker_id}] ✓ Job {job['id']} saved to {dest.name}")
            try:
                art_dir = Path(r"~\.gemini\antigravity-ide\brain\82cce8b8-82da-455e-82a0-87ceb15a0d45\ghunghroo_media")
                if art_dir.exists():
                    job_slug = job_dir.name
                    target_art = art_dir / f"{job_slug}_{dest.name}"
                    shutil.copyfile(dest, target_art)
                    os.utime(target_art, None)
            except Exception as _e:
                pass

            async with queue_lock:
                job["status"] = "success"
                job["output_file"] = dest.name
                job["generated_fid"] = new_fid
                save_queue(queue_file, all_jobs)

        except Exception as e:
            job["retries"] = job.get("retries", 0) + 1
            log.warning(f"[W{worker_id}] ✗ Job {job['id']} failed (attempt {job['retries']}): {e}")
            async with queue_lock:
                if job["retries"] >= MAX_RETRIES:
                    job["status"] = "needs_human_review"
                    log.error(f"[W{worker_id}] Job {job['id']} → NEEDS_HUMAN_REVIEW after {MAX_RETRIES} attempts")
                else:
                    job["status"] = "failed"
                    job_queue.put_nowait(job["id"])  # re-queue for retry
                save_queue(queue_file, all_jobs)

            # Take debug screenshot
            try:
                ts = datetime.now().strftime("%H%M%S")
                await page.screenshot(path=str(generated_dir.parent / "logs" / f"debug-{job['id']}-{ts}.png"))
            except Exception:
                pass

        job_queue.task_done()
        await asyncio.sleep(4)  # gentle on Shopify

    await ctx.close()
    log.info(f"[W{worker_id}] Done.")


# --------------------------------------------------------------------------- #
# Orchestrator
# --------------------------------------------------------------------------- #
async def run_execution_agent(job_dir: Path, max_workers: int = MAX_CONCURRENCY, is_regen: bool = False, only: list[str] | None = None):
    queue_file    = job_dir / ("image_queue_regen.json" if is_regen else "image_queue.json")
    generated_dir = job_dir / "generated"
    status_file   = job_dir / "status.json"
    logs_dir      = job_dir / "logs"

    generated_dir.mkdir(exist_ok=True)
    logs_dir.mkdir(exist_ok=True)

    if not queue_file.exists():
        raise FileNotFoundError(
            f"No {'image_queue_regen.json' if is_regen else 'image_queue.json'} in {job_dir}."
        )

    all_jobs = load_queue(queue_file)

    # Load status.json for source file ID
    with open(status_file) as f:
        status = json.load(f)

    source_file_id = status.get("original_file_id")
    if not source_file_id:
        comp_ref = job_dir / "composite_reference.jpg"
        if comp_ref.exists():
            log.info(f"[{job_dir.name}] Uploading composite_reference.jpg to Shopify Files...")
            source_file_id = upload_file_to_shopify(comp_ref)
        else:
            originals = sorted((job_dir / "original").glob("*"))
            originals = [p for p in originals if p.suffix.lower() in {".jpg", ".jpeg", ".png"}]
            if not originals:
                raise FileNotFoundError(f"No original image or composite_reference.jpg in {job_dir}")
            source_file_id = upload_file_to_shopify(originals[0])
        status["original_file_id"] = source_file_id
        with open(status_file, "w") as f:
            json.dump(status, f, indent=4)

    pending = get_pending_jobs(all_jobs)
    if only:
        pending = [j for j in pending if j["id"] in only]
    if not pending:
        log.info(f"[{job_dir.name}] No pending jobs in {'regen queue' if is_regen else 'main queue'}. All done.")
        return

    log.info(f"[{job_dir.name}] {len(pending)} jobs to process with up to {max_workers} workers.")

    # Build the shared asyncio queue
    job_queue: asyncio.Queue = asyncio.Queue()
    for j in pending:
        job_queue.put_nowait(j["id"])

    queue_lock = asyncio.Lock()

    async with async_playwright() as pw:
        workers = [
            asyncio.create_task(
                worker(
                    worker_id=i + 1,
                    job_queue=job_queue,
                    all_jobs=all_jobs,
                    queue_file=queue_file,
                    generated_dir=generated_dir,
                    source_file_id=source_file_id,
                    queue_lock=queue_lock,
                    playwright=pw,
                )
            )
            for i in range(min(max_workers, len(pending)))
        ]
        await asyncio.gather(*workers)

    # Final status update
    success_count = sum(1 for j in all_jobs if j["status"] == "success")
    review_count  = sum(1 for j in all_jobs if j["status"] == "needs_human_review")
    total         = len(all_jobs)

    log.info(f"\n{'='*50}")
    log.info(f"Job {job_dir.name} complete:")
    log.info(f"  Success:           {success_count}/{total}")
    log.info(f"  Needs review:      {review_count}/{total}")
    log.info(f"  Still pending:     {total - success_count - review_count}/{total}")
    log.info(f"{'='*50}")

    if not is_regen:
        status["images_generated"] = success_count > 0
        status["phase"] = "generation_complete"
        status["generation_summary"] = {
            "success": success_count,
            "needs_human_review": review_count,
            "total": total,
            "timestamp": datetime.now().isoformat(),
        }
    else:
        status["regen_summary"] = {
            "success": success_count,
            "needs_human_review": review_count,
            "total": total,
            "timestamp": datetime.now().isoformat(),
        }
    with open(status_file, "w") as f:
        json.dump(status, f, indent=4)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Execution Agent — parallel Shopify Magic generation")
    parser.add_argument("job_dir", help="Path to the job directory (e.g. 'jobs/bangle 1')")
    parser.add_argument("--workers", type=int, default=MAX_CONCURRENCY,
                        help=f"Max parallel browsers (default: {MAX_CONCURRENCY})")
    parser.add_argument("--profile", type=str, default=None,
                        help="Override the persistent browser profile directory (for running multiple parallel group processes, each with its own cloned authenticated profile)")
    parser.add_argument("--executable", type=str, default=None,
                        help="Path to a Chromium-based browser executable to drive instead of Playwright's bundled Chromium (e.g. Comet's comet.exe)")
    parser.add_argument("--minimized", action="store_true",
                        help="Launch the browser window minimized (--start-minimized) so it doesn't take focus")
    parser.add_argument("--window-pos", type=str, default=None,
                        help="Position of browser window (e.g. '0,0')")
    parser.add_argument("--window-size", type=str, default=None,
                        help="Size of browser window (e.g. '700,500')")
    parser.add_argument("--only", nargs="+", default=None, help="Only run these job ids")
    parser.add_argument("--regen", action="store_true",
                        help="Run targeted regenerations using image_queue_regen.json and save as <id>_regen.png")
    args = parser.parse_args()

    if args.profile:
        PROFILE_DIR = Path(args.profile)
    if args.executable:
        EXECUTABLE_PATH = args.executable
    if args.window_pos:
        WINDOW_POS = args.window_pos
    if args.window_size:
        WINDOW_SIZE = args.window_size
    MINIMIZED = args.minimized

    asyncio.run(run_execution_agent(Path(args.job_dir), args.workers, is_regen=args.regen, only=args.only))
