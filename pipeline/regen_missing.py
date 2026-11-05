"""Regenerate shots whose file was moved to generated/_misplaced. Wrapper around run_drive_generation:
resets state for missing files, serialises uploads with the save lock, rejects duplicate downloads, runs 2 workers."""
import hashlib, sys
from pathlib import Path
import run_drive_generation as r
import drive_shopify_generator as dsg
import execution_agent as ea

NW = 5
r.WORKER_CONFIGS.append({"id": 5, "name": "Worker-05", "profile": ".magic-profile-g5", "pos": "1460,20", "size": "700,500"})
r.WORKER_CONFIGS[:] = r.WORKER_CONFIGS[:NW]

# 1) state: missing/tiny file => pending; stale white-bg ref => cleared
st = dsg.load_state()
for v in st["variants"].values():
    d = Path(v["target_dir"])
    for spec in dsg.SHOT_SPECS:
        f = d / spec["filename"]
        if not (f.exists() and f.stat().st_size > 20000):
            v["shots"][spec["id"]]["status"] = "pending"
            v["shots"][spec["id"]]["generated_fid"] = None
            if spec["num"] == 1:
                v.pop("whitebg_fid", None)
dsg.save_state(st)

# 2) uploads create "newest file" too: take the save lock so a save never picks up another worker's upload
_up = ea.upload_file_to_shopify
def upload_locked(p):
    with r.SAVE_SERIAL_LOCK:
        return _up(p)
ea.upload_file_to_shopify = upload_locked

# 3) reject a download identical to any existing image
_dl = ea.download_url
def md5(p): return hashlib.md5(Path(p).read_bytes()).hexdigest()
def dl_checked(url, out):
    _dl(url, out)
    h = md5(out)
    for f in dsg.GENERATED_BASE.glob("*/*/*"):
        if f.suffix in (".png", ".jpg") and f != Path(out) and f.stat().st_size == Path(out).stat().st_size and md5(f) == h:
            Path(out).unlink()
            raise RuntimeError(f"duplicate of {f} (wrong file saved)")
ea.download_url = dl_checked

r.main()
