"""
apply_review_decisions.py
Applies decisions exported from ghunghroo_review_gallery.html (format:
{"decisions": {"<job_id>_<shot_id>": {"decision": "approved|regen|deleted", "note": "..."}}})

- approved: leave generated file in place (also copied to approved/)
- deleted:  move generated file to rejected/, mark queue item status "deleted"
- regen:    move generated file to rejected/, reset queue item status to "pending" so
            execution_agent.py regenerates it on next run

Usage: python apply_review_decisions.py review_decisions_latest.json
"""
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
JOBS_DIR = ROOT / "jobs"


def main():
    decisions_path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "review_decisions_latest.json"
    if not decisions_path.exists():
        print(f"Error: {decisions_path} not found.")
        return

    data = json.loads(decisions_path.read_text(encoding="utf-8"))
    decisions = data.get("decisions", {})

    by_job = {}
    for key, info in decisions.items():
        job_id, shot_id = key.split("_", 1)
        by_job.setdefault(job_id, {})[shot_id] = info

    counts = {"approved": 0, "regen": 0, "deleted": 0, "skipped": 0}

    for job_id, shots in by_job.items():
        job_dir = JOBS_DIR / job_id
        q_file = job_dir / "image_queue.json"
        if not q_file.exists():
            print(f"[SKIP] {job_id}: no image_queue.json")
            counts["skipped"] += len(shots)
            continue

        queue = json.loads(q_file.read_text(encoding="utf-8"))
        generated_dir = job_dir / "generated"
        approved_dir = job_dir / "approved"
        rejected_dir = job_dir / "rejected"
        approved_dir.mkdir(exist_ok=True)
        rejected_dir.mkdir(exist_ok=True)

        changed = False
        for item in queue:
            shot_id = item.get("id")
            if shot_id not in shots:
                continue
            decision = shots[shot_id].get("decision")
            note = shots[shot_id].get("note", "")
            out_file = item.get("output_file")
            src = generated_dir / out_file if out_file else None

            if decision == "approved":
                if src and src.exists():
                    shutil.copy2(src, approved_dir / out_file)
                counts["approved"] += 1

            elif decision == "deleted":
                if src and src.exists():
                    shutil.move(str(src), str(rejected_dir / out_file))
                item["status"] = "deleted"
                item["review_note"] = note
                changed = True
                counts["deleted"] += 1

            elif decision == "regen":
                if src and src.exists():
                    shutil.move(str(src), str(rejected_dir / f"regen_{out_file}"))
                item["status"] = "pending"
                item["retries"] = 0
                item["review_note"] = note
                changed = True
                counts["regen"] += 1
            else:
                counts["skipped"] += 1

            print(f"  [{job_id}] {shot_id}: {decision}" + (f" ({note})" if note else ""))

        if changed:
            q_file.write_text(json.dumps(queue, indent=2), encoding="utf-8")
            # job needs to be picked up again by the generator for the regenerated shots
            status_file = job_dir / "status.json"
            if status_file.exists():
                st = json.loads(status_file.read_text(encoding="utf-8"))
                st["phase"] = "generation_pending"
                st["images_generated"] = False
                status_file.write_text(json.dumps(st, indent=4), encoding="utf-8")

    print("\n=== Summary ===")
    for k, v in counts.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
