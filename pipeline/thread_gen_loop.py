"""Generate STB shots with Shopify Magic from the REAL tight crop, retrying until the bangle counter says 12.
Usage: python thread_gen_loop.py <slug> [<slug> ...]      Output: stb/gen/<slug>/<n>-<name>.png (only count-verified), all candidates in stb/gen_cand/
Candidate acceptance window 11.8-13.0 (real photos measure 12.0-12.8); every accepted image is still checked by eye."""
import json, queue, subprocess, sys, threading, shutil
from pathlib import Path
import thread_setup as ts, thread_count as tc

ROOT = Path(__file__).parent
import os
PROFILES = os.environ.get("HERO_PROFILES", ".magic-profile-c2v3").split(",")
MAX_TRY = 8
LO, HI = 11.8, 13.0
ONLY = set()
NARROW = (" The stack of twelve is a NARROW block: its width is only about half of its height, because every bangle is very thin (about 3 mm), "
          "so twelve of them side by side are only about 3.5 cm wide.")

WRIST_ORI = (" COMPOSITION (important): the forearm lies perfectly HORIZONTAL across the frame from left to right, seen from the side, with the wrist in the centre and the hand on the right, "
             "so the twelve bangles on the wrist appear as twelve separate UPRIGHT VERTICAL bands standing side by side, each band running from the top edge of the wrist to its bottom edge, "
             "exactly like the reference photo. The stack covers only a short part of the forearm, about 3.5 cm.")

def prompts(slug):
    idx, cname, code, thread, scene, outfit, macro = ts.COLOURS[slug]
    look = f"twelve {thread} silk-thread bangles with gold beads"
    sh = ts.shots(look, scene, outfit, macro)
    return [(i, p + NARROW + (WRIST_ORI if i == "3-wrist-shot" else "")) for i, p in sh if (not ONLY or i in ONLY)]

def make(slug, shot, prompt, attempt):
    name = f"rg-stbg-{slug}-{shot.split('-')[0]}-a{attempt}"
    src = ts.RAW[ts.COLOURS[slug][0]]
    n, _, _ = ts.make_job(name[3:], src, [(shot, prompt)])
    return n

def main(slugs):
    q = queue.Queue(); lock = threading.Lock(); done = {}; log = []
    hues = {s: tc.hue_of(ROOT / "stb" / "cutouts" / f"{s}.png") for s in slugs}
    for s in slugs:
        for shot, pr in prompts(s): q.put((s, shot, pr, 1))
    (ROOT / "stb" / "gen_cand").mkdir(parents=True, exist_ok=True)
    def work(profile):
        while True:
            try: s, shot, pr, att = q.get(timeout=20)
            except queue.Empty:
                with lock:
                    if len(done) >= len(slugs) * (len(ONLY) or 4) or q.empty() and not busy[0]: return
                continue
            with lock: busy[0] += 1
            try:
                job = make(s, shot, pr, att)
                with open(ROOT / "jobs" / job / "run.log", "a") as lg:
                    subprocess.run([sys.executable, "-u", "execution_agent.py", f"jobs/{job}", "--workers", "1", "--profile", str(ROOT / profile)], cwd=ROOT, stdout=lg, stderr=subprocess.STDOUT)
                f = ROOT / "jobs" / job / "generated" / f"{shot}.png"
                c = None
                if f.exists():
                    try: r = tc.count(f, hues[s])
                    except Exception: r = None
                    c = None if r is None else round(r[0], 1)
                    cand = ROOT / "stb" / "gen_cand" / f"{s}-{shot}-a{att}-c{c}.png"; shutil.copy(f, cand)
                ok = c is not None and LO <= c <= HI
                if ok and shot == "3-wrist-shot":
                    x_, y_, w_, h_ = r[1]; ok = h_ >= 1.25 * w_ and w_ > 80          # stack must stand upright so the count is measurable
                print(f"{s} {shot} attempt {att}: count {c} {'ACCEPT' if ok else 'reject'}", flush=True)
                with lock:
                    if ok:
                        d = ROOT / "stb" / "gen" / s; d.mkdir(parents=True, exist_ok=True); shutil.copy(f, d / f"{shot}.png"); done[(s, shot)] = c
                    elif att < MAX_TRY: q.put((s, shot, pr, att + 1))
                    else: done[(s, shot)] = None
            finally:
                with lock: busy[0] -= 1
    busy = [0]
    th = [threading.Thread(target=work, args=(p,)) for p in PROFILES]
    [t.start() for t in th]; [t.join() for t in th]
    print("FINISHED", {f"{k[0]}/{k[1]}": v for k, v in done.items()}, flush=True)

if __name__ == "__main__":
    args = sys.argv[1:]
    if "--only" in args:
        i = args.index("--only"); ONLY.update(args[i + 1].split(",")); del args[i:i + 2]
    main(args)
