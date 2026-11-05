"""Run the round-10 flat-lay jobs one after another (single Magic profile; parallel profiles cross-contaminate)."""
import json, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).parent
for name in json.loads((ROOT / "jobs" / "rg10_jobs.json").read_text()):
    d = ROOT / "jobs" / name
    if (d / "generated" / "5-flatlay.png").exists():
        continue
    for attempt in range(2):
        r = subprocess.run([sys.executable, "-u", "execution_agent.py", f"jobs/{name}", "--workers", "1", "--profile", ".magic-profile"],
                           cwd=ROOT, stdout=open(d / "run.log", "a"), stderr=subprocess.STDOUT)
        ok = (d / "generated" / "5-flatlay.png").exists()
        print(name, "OK" if ok else f"FAILED (exit {r.returncode})", flush=True)
        if ok:
            break
