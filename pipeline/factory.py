"""
factory.py  —  Bangle Bliss Product Factory (Phase 0 + Phase 2 Orchestrator)

This script is the DETERMINISTIC half of the pipeline.
The AI (Creative Director) work is done by Antigravity directly:
  - Antigravity agent looks at the image and writes image_queue.json
  - This script does everything else: prep, execution, state tracking

Usage:
    python factory.py                    # run generation on all jobs with image_queue.json
    python factory.py --workers 2        # use 2 parallel browsers (default: 4)
    python factory.py --prep-only        # only run source image prep (Phase 0)
"""

import asyncio
import argparse
import json
from pathlib import Path

import cropper
from execution_agent import run_execution_agent

BASE_DIR  = Path("~/Desktop/My Bangle Bliss")
INPUT_DIR = BASE_DIR / "input"
JOBS_DIR  = BASE_DIR / "jobs"

INPUT_DIR.mkdir(parents=True, exist_ok=True)
JOBS_DIR.mkdir(parents=True, exist_ok=True)


def scan_and_prep_input():
    """
    Phase 0 — deterministic (no AI):
    Deduplicate + crop every image in input/
    Save crops to input/cropped/, then create job folders.
    """
    valid = {".jpg", ".jpeg", ".png", ".webp"}
    raw_images = [p for p in INPUT_DIR.iterdir()
                  if p.is_file() and p.suffix.lower() in valid]

    if not raw_images:
        print("input/ is empty — nothing to prep.")
        return

    cropped_dir = INPUT_DIR / "cropped"
    cropped_dir.mkdir(exist_ok=True)
    cropper.process_raw_images(INPUT_DIR, cropped_dir)

    import shutil
    for crop in sorted(cropped_dir.glob("*.jpg")):
        product_id = crop.stem
        job_dir = JOBS_DIR / product_id
        if job_dir.exists():
            print(f"Job '{product_id}' already exists — skipping.")
            continue

        for folder in ["original", "generated", "approved", "rejected", "logs"]:
            (job_dir / folder).mkdir(parents=True, exist_ok=True)

        shutil.copy2(crop, job_dir / "original" / crop.name)
        crop.unlink()

        status = {
            "product_id": product_id,
            "original_image": crop.name,
            "phase": "awaiting_creative_director",
            "images_generated": False,
            "qc_complete": False,
            "published": False,
        }
        with open(job_dir / "status.json", "w") as f:
            json.dump(status, f, indent=4)

        print(f"Created job folder: {product_id}")
        print(f"  → Now ask Antigravity to analyze this product and write image_queue.json")


async def run(max_workers: int):
    job_dirs = sorted(d for d in JOBS_DIR.iterdir()
                      if d.is_dir() and (d / "status.json").exists())

    if not job_dirs:
        print("No jobs found in jobs/")
        return

    for job_dir in job_dirs:
        with open(job_dir / "status.json") as f:
            status = json.load(f)

        product_id = status["product_id"]
        queue_file = job_dir / "image_queue.json"

        if not queue_file.exists():
            print(f"\n[{product_id}] Waiting for Antigravity — image_queue.json not yet written.")
            print(f"  Tell Antigravity: analyze jobs/{product_id} and write image_queue.json")
            continue

        if status.get("images_generated"):
            print(f"\n[{product_id}] Already generated. Skipping.")
            continue

        print(f"\n{'='*55}")
        print(f"Processing: {product_id}")
        print(f"{'='*55}")
        await run_execution_agent(job_dir, max_workers)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bangle Bliss Product Factory")
    parser.add_argument("--workers",   type=int, default=4,
                        help="Max parallel browsers (default: 4)")
    parser.add_argument("--prep-only", action="store_true",
                        help="Only run Phase 0 image prep, skip generation")
    args = parser.parse_args()

    if args.prep_only:
        scan_and_prep_input()
    else:
        scan_and_prep_input()
        asyncio.run(run(args.workers))
