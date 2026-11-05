import asyncio
import json
import os
import re
import time
import subprocess
import tempfile
import urllib.request
from pathlib import Path
from playwright.async_api import async_playwright
import pydantic
from google.antigravity import Agent, LocalAgentConfig
from google.antigravity.types import Image

# --- CONFIGURATION ---
BASE_DIR = Path("~/Desktop/My Bangle Bliss")
JOBS_DIR = BASE_DIR / "jobs"
STORE = "your-store.myshopify.com"
STORE_URL = f"https://admin.shopify.com/store/{STORE.split('.')[0]}"
STATE_FILE = BASE_DIR / ".magic-profile" # Playwright will use persistent context here
TMP = Path(tempfile.mkdtemp())

# --- SHOPIFY GRAPHQL HELPERS ---
def gql(query, variables=None, _retries=4):
    q, v, o = TMP / "q.graphql", TMP / "v.json", TMP / "o.json"
    q.write_text(query, encoding="utf-8")
    cmd = f'shopify store execute --store {STORE} --query-file "{q}" --output-file "{o}"'
    if variables is not None:
        v.write_text(json.dumps(variables), encoding="utf-8")
        cmd += f' --variable-file "{v}"'
    if query.lstrip().startswith("mutation"):
        cmd += " --allow-mutations"
    if o.exists():
        o.unlink()
        
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if not o.exists():
        if _retries > 0:
            time.sleep(3)
            return gql(query, variables, _retries - 1)
        raise RuntimeError(r.stdout[-600:] + r.stderr[-300:])
    d = json.loads(o.read_text(encoding="utf-8"))
    return d.get("data", d)

def upload_original_to_files(img_path: Path):
    print(f"Uploading {img_path.name} to Shopify Files...")
    # 1. Create Staged Target
    t = gql("mutation($i:[StagedUploadInput!]!){stagedUploadsCreate(input:$i){stagedTargets{url resourceUrl parameters{name value}}userErrors{message}}}",
            {"i": [{"filename": img_path.name, "mimeType": "image/jpeg", "httpMethod": "POST", "resource": "FILE"}]})
    tg = t["stagedUploadsCreate"]["stagedTargets"][0]
    
    # 2. Upload bytes
    cmd = ["curl", "-s", "-o", os.devnull, "-w", "%{http_code}", "-X", "POST", tg["url"]]
    for p in tg["parameters"]:
        cmd += ["-F", f"{p['name']}={p['value']}"]
    cmd += ["-F", f"file=@{img_path}"]
    code = subprocess.run(cmd, capture_output=True, text=True).stdout
    if code != "201":
        raise RuntimeError(f"upload failed {code}")
        
    # 3. Create File in Shopify
    fc = gql("mutation($f:[FileCreateInput!]!){fileCreate(files:$f){files{id}userErrors{message}}}",
             {"f": [{"originalSource": tg["resourceUrl"], "contentType": "IMAGE", "alt": f"Original {img_path.name}"}]})
    fid_gid = fc["fileCreate"]["files"][0]["id"]
    
    # Wait for readiness
    for _ in range(30):
        st = gql('query($id:ID!){node(id:$id){... on MediaImage{fileStatus} ... on GenericFile{fileStatus}}}', {"id": fid_gid})["node"]["fileStatus"]
        if st == "READY":
            break
        time.sleep(3)
        
    print(f"Upload complete. File GID: {fid_gid}")
    return fid_gid.split("/")[-1] # return numeric ID

def download_file_by_id(numeric_id: str, dest_path: Path):
    print(f"Resolving URL for new file ID {numeric_id}...")
    gid = f"gid://shopify/MediaImage/{numeric_id}"
    res = gql('query($id:ID!){node(id:$id){... on MediaImage{image{url}}}}', {"id": gid})
    
    # Sometimes it takes a moment for the node to be queryable as a MediaImage
    if not res or not res.get("node"):
        # try as GenericFile
        gid = f"gid://shopify/GenericFile/{numeric_id}"
        res = gql('query($id:ID!){node(id:$id){... on GenericFile{url}}}', {"id": gid})
        url = res["node"]["url"]
    else:
        url = res["node"]["image"]["url"]
        
    print(f"Downloading generated image from {url} to {dest_path.name}...")
    urllib.request.urlretrieve(url, str(dest_path))

# --- PLAYWRIGHT AUTOMATION ---
def file_id_from_url(url):
    m = re.search(r"/files/(\d+)", url)
    return m.group(1) if m else None

async def make_magic_image(page, file_id, prompt_text):
    print(f"Navigating to Magic UI for file {file_id}...")
    await page.goto(f"{STORE_URL}/content/files/{file_id}", wait_until="domcontentloaded")
    
    gen = page.get_by_role("button", name="Generate", exact=True).first
    try:
        await gen.wait_for(timeout=15000)
    except Exception:
        await page.screenshot(path="debug_timeout.png", full_page=True)
        raise
    await gen.scroll_into_view_if_needed()
    await gen.click()
    
    box = page.get_by_label(re.compile("sunny park", re.I))
    await box.wait_for(timeout=20000)
    await box.scroll_into_view_if_needed()
    await box.click()
    await asyncio.sleep(0.5)
    
    await page.keyboard.type(prompt_text, delay=8)
    await asyncio.sleep(1)
    await page.keyboard.press("Enter")
    
    print("   Waiting for generation to finish (up to 5 minutes)...")
    await asyncio.sleep(8)
    
    save_btn = None
    for _ in range(150):
        cands = page.locator("button").filter(has_text=re.compile(r"^\s*Save\s*$"))
        count = await cands.count()
        for i in range(count):
            c = cands.nth(i)
            try:
                if await c.is_visible() and await c.is_enabled():
                    save_btn = c
                    break
            except Exception:
                await run_qc_on_job(job_dir)
        if save_btn is not None:
            break
        await asyncio.sleep(2)
        
    if save_btn is None:
        raise RuntimeError("Magic did not finish (no enabled Save button appeared)")
        
    print("   Image generated! Saving as new...")
    await asyncio.sleep(3)
    
    item = page.locator("button:visible").filter(has_text=re.compile(r"save as new", re.I)).first
    menu_opened = False
    
    for up in ("xpath=..", "xpath=../..", "xpath=../../.."):
        group = save_btn.locator(up)
        btns = group.locator("button:visible")
        count = await btns.count()
        for i in range(count):
            b = btns.nth(i)
            try:
                txt = (await b.inner_text() or "").strip()
                if txt: 
                    continue
                await b.click(timeout=3000)
                await item.wait_for(state="visible", timeout=3000)
                await item.click(timeout=5000)
                menu_opened = True
                break
            except Exception:
                await page.keyboard.press("Escape")
                await asyncio.sleep(0.4)
        if menu_opened:
            break
            
    if not menu_opened:
        raise RuntimeError("Could not open the Save menu")
        
    # Instead of waiting for URL redirect (which Shopify may no longer do),
    # we just wait 5 seconds for the file to be saved in Shopify backend.
    await asyncio.sleep(5)
    
    # Use GraphQL to get the most recently created file ID
    print("   Fetching newest image URL via API...")
    res = gql('query { files(first: 1, sortKey: CREATED_AT, reverse: true) { nodes { id } } }')
    try:
        new_fid_gid = res["files"]["nodes"][0]["id"]
        new_fid = new_fid_gid.split("/")[-1]
        print(f"   Success! New file ID: {new_fid}")
        return new_fid
    except Exception as e:
        print(f"   Failed to fetch new file ID: {e}")
        return "saved-" + time.strftime("%Y%m%d-%H%M%S")

# --- QC AGENT ---
class QCResult(pydantic.BaseModel):
    is_approved: bool
    reason: str
    defects: list[str]

async def run_qc_on_job(job_dir: Path):
    status_file = job_dir / "status.json"
    with open(status_file, "r") as f:
        status = json.load(f)

    original_img_path = job_dir / "original" / status["original_image"]
    generated_dir = job_dir / "generated"
    generated_images = [f for f in generated_dir.iterdir() if f.is_file()]
    if not generated_images: return

    print(f"[{status['product_id']}] Starting QC on {len(generated_images)} images...")
    config = LocalAgentConfig(
        system_instructions=(
            "You are a strict Image Quality QC agent for a jewelry brand. "
            "Compare the GENERATED image against the ORIGINAL image. "
            "Check for: 1. Is it the exact same product? 2. Any AI artifacts/distortions? "
            "Reject if it fails ANY check."
        ),
        response_schema=QCResult,
        temperature=0.1
    )

    original_img_obj = Image.from_file(str(original_img_path))
    
    async with Agent(config) as agent:
        for gen_img_path in generated_images:
            gen_img_obj = Image.from_file(str(gen_img_path))
            response = await agent.chat(["Original:", original_img_obj, "Generated:", gen_img_obj, "Evaluate."])
            qc_data = await response.structured_output()
            
            log_path = job_dir / "logs" / f"qc_{gen_img_path.stem}.json"
            with open(log_path, "w") as f:
                json.dump(qc_data, f, indent=4)
                
            if qc_data["is_approved"]:
                print(f"  [APPROVED] {gen_img_path.name}: {qc_data['reason']}")
                import shutil
                shutil.move(str(gen_img_path), str(job_dir / "approved" / gen_img_path.name))
            else:
                print(f"  [REJECTED] {gen_img_path.name}: {qc_data['reason']}")
                import shutil
                shutil.move(str(gen_img_path), str(job_dir / "rejected" / gen_img_path.name))
                
    status["qc_complete"] = True
    with open(status_file, "w") as f:
        json.dump(status, f, indent=4)

# --- MAIN PIPELINE ---
async def process_job(job_dir: Path):
    status_file = job_dir / "status.json"
    with open(status_file, "r") as f:
        status = json.load(f)
        
    product_id = status["product_id"]
    print(f"\n--- PROCESSING JOB: {product_id} ---")
    
    # 1. Upload original if not uploaded
    if "original_file_id" not in status:
        original_img_path = job_dir / "original" / status["original_image"]
        fid = upload_original_to_files(original_img_path)
        status["original_file_id"] = fid
        with open(status_file, "w") as f: json.dump(status, f, indent=4)
    
    base_file_id = status["original_file_id"]
    
    # 2. Run Playwright to generate images for each prompt
    with open(job_dir / "prompts.json", "r") as f:
        prompts = json.load(f)
        
    if not status.get("images_generated"):
        print(f"[{product_id}] Launching Playwright with persistent profile...")
        
        async with async_playwright() as p:
            # We use the existing Claude .magic-profile, so no login is needed!
            ctx = await p.chromium.launch_persistent_context(str(STATE_FILE), headless=False)
            page = ctx.pages[0] if ctx.pages else await ctx.new_page()
            
            
            for prompt_name, prompt_text in prompts.items():
                print(f"\n[{product_id}] Executing prompt: {prompt_name}")
                new_fid = await make_magic_image(page, base_file_id, prompt_text)
                
                # 3. Download the generated image immediately
                if new_fid and not new_fid.startswith("saved-"):
                    dest_path = job_dir / "generated" / f"{prompt_name}.jpg"
                    download_file_by_id(new_fid, dest_path)
            
            await ctx.close()
            
        status["images_generated"] = True
        with open(status_file, "w") as f: json.dump(status, f, indent=4)

    # 4. Run QC
    if not status.get("qc_complete"):
        await run_qc_on_job(job_dir)
        
    print(f"--- JOB {product_id} PIPELINE COMPLETE ---")

if __name__ == "__main__":
    # Process all jobs that have completed phase 1 (prompts ready)
    for job_dir in JOBS_DIR.iterdir():
        if job_dir.is_dir() and (job_dir / "status.json").exists():
            with open(job_dir / "status.json", "r") as f:
                s = json.load(f)
            if s.get("prompts_complete") and not s.get("qc_complete"):
                asyncio.run(process_job(job_dir))
