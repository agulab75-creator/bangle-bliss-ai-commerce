"""Create Shopify Magic jobs for the global KSG A+ scenes, then run them one by one.

python aplus/make_jobs.py            # create jobs + upload sources
python aplus/make_jobs.py --run      # also run execution_agent on each (slow, uses Shopify Magic)
Each job edits ONE source photo (execution_agent limitation), so one job dir per scene.
"""
import sys, json, shutil, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import execution_agent as ea

RULES = (" STRICT RULES: there are EXACTLY 4 bangles in the picture - count them, it must be 4, never 3, never 5; "
         "all 4 are identical in design and size. Copy the bangle design from the reference photo EXACTLY: same glass "
         "colour, same stone arrangement, same gold details. Do not invent, add, remove, enlarge or rearrange any stone "
         "or motif. The bangles are REAL TRANSLUCENT GLASS: glossy, smooth, see-through with soft refractions and specular "
         "highlights - never plastic, resin or opaque. Each bangle is a slim narrow band. No text, no watermark, no logo, "
         "no extra jewellery, no extra bangles.")
DESIGN = (" Design: plain faceted glass bangles with round clear kundan stones in thin gold rings, evenly spaced in a "
          "single line along each bangle.")

SCENES = {
  "aplus-ksg-hero-flatlay": ("Emerald-Green", "white-studio",
    "Create a new photograph: these four translucent emerald-green glass bangles resting on cream raw-silk fabric with "
    "scattered rose petals, a small brass bowl and a string of jasmine, soft warm window light from the left, wide "
    "landscape composition with the bangles on the right third and empty soft space on the left, luxury jewellery "
    "editorial, no people, real photograph."),
  "aplus-ksg-diya-hand": ("Magenta", "worn-on-hand",
    "Create a new photograph: close-up of an Indian woman's hand with fine mehendi, wearing these four translucent magenta "
    "glass bangles as a snug set on her wrist, gently holding a lit brass diya, pink and gold silk saree edge, warm glow, "
    "soft bokeh lights behind, festive Diwali evening, real photograph."),
  "aplus-ksg-velvet-tray": ("Sky-Aqua", "white-studio",
    "Create a new photograph: these four translucent sky-aqua glass bangles stacked neatly on a deep maroon velvet jewellery "
    "tray, with a small antique mirror and a few gold-toned beads beside them, soft studio light, shallow depth of field, "
    "premium jewellery boutique feel, no people, real photograph."),
  "aplus-ksg-lehenga-wrist": ("Orchid-Pink", "worn-on-hand",
    "Create a new photograph: close-up of a bride's wrist wearing these four translucent orchid-pink glass bangles, pastel "
    "pink and gold embroidered lehenga sleeve and dupatta edge, soft natural daylight, elegant wedding mood, shallow depth "
    "of field, real photograph."),
  "aplus-ksg-haldi-flatlay": ("Lemon-Yellow", "white-studio",
    "Create a new photograph: these four translucent lemon-yellow glass bangles resting on a rustic brass thali with fresh "
    "orange marigold petals and a few green leaves, bright cheerful haldi-ceremony mood, soft natural daylight, shallow "
    "depth of field, no people, real photograph."),
}

def main(run):
    for slug, (colour, shot, prompt) in SCENES.items():
        jd = ROOT / "jobs" / slug
        if (jd / "generated").exists() and any((jd / "generated").iterdir()):
            print("skip (already generated)", slug); continue
        (jd / "original").mkdir(parents=True, exist_ok=True); (jd / "generated").mkdir(exist_ok=True); (jd / "logs").mkdir(exist_ok=True)
        src = next((ROOT / "amazon-latest-images" / "KSG" / colour).glob(f"*{shot}*.jpg"))
        dst = jd / "original" / src.name; shutil.copy(src, dst)
        st = jd / "status.json"
        if st.exists() and json.load(open(st)).get("original_file_id"):
            fid = json.load(open(st))["original_file_id"]
        else:
            fid = ea.upload_file_to_shopify(dst)
        json.dump({"phase": "ready", "original_file_id": fid, "purpose": "KSG global A+"}, open(st, "w"), indent=2)
        json.dump([{"id": "scene", "prompt": prompt + DESIGN + RULES, "status": "pending", "retries": 0}],
                  open(jd / "image_queue.json", "w"), indent=4)
        print("job ready", slug, fid)
        if run:
            subprocess.run([sys.executable, str(ROOT / "execution_agent.py"), str(jd), "--workers", "1",
                            "--profile", str(ROOT / ".magic-profile")], cwd=ROOT)

if __name__ == "__main__":
    main("--run" in sys.argv)
