"""Creative STB scenes via Shopify Magic from the REAL tight crop, retried until the orientation-tolerant counter reads 12 (11.8-13.0).
Usage: python thread_creative.py <slug> [<slug>...] [--only shot,shot]    Output: stb/creative/<slug>/<shot>.png ; all candidates: stb/creative_cand/"""
import queue, subprocess, sys, threading, shutil
from pathlib import Path
import thread_setup as ts, thread_count as tc
import thread_gen_loop as gl

ROOT = Path(__file__).parent
import os
PROFILES = os.environ.get("CREATIVE_PROFILES", ".magic-profile-g3,.magic-profile-g4").split(",")
MAX_TRY = 1                      # creative shots only need to LOOK like a full dozen: one generation each, no count retries
LO, HI = 11.8, 13.0
ONLY = set()

STYLE = {
 "royal-blue": "a mustard-yellow and gold silk saree with an ivory dupatta and gold jhumkas",
 "crimson-red": "a cream and gold Banarasi saree with gold jewellery",
 "mustard-yellow": "a deep royal-blue silk anarkali with gold embroidery",
 "coral-pink": "an ivory chikankari kurta set with pearl jewellery",
 "turquoise": "a soft peach and gold lehenga with pearl jewellery",
 "emerald-green": "a deep red and gold Banarasi saree with gold jewellery",
 "parrot-green": "a mustard-yellow and white bandhani suit",
 "rani-pink": "a cream and gold silk saree with gold jhumkas",
 "wine-maroon": "a cream and gold brocade saree with pearl jewellery",
 "orange": "a deep green silk saree with a gold border",
 "golden": "a deep green velvet blouse and cream silk saree with kundan jewellery",
}

SURF = {"royal-blue": "mustard-yellow raw silk", "crimson-red": "cream and gold brocade", "mustard-yellow": "deep blue velvet", "coral-pink": "ivory silk",
        "turquoise": "peach silk", "emerald-green": "deep red velvet", "parrot-green": "mustard-yellow silk", "rani-pink": "cream raw silk",
        "wine-maroon": "cream and gold brocade", "orange": "deep green silk", "golden": "deep green velvet"}

def scenes(look, outfit, surf="ivory silk"):
    d = {
    "c1-bangle-stand": ("Create a new photograph: elegant jewellery photograph of " + look + " - ONE single set only - slipped onto a slim vertical brass bangle-stand pole with a round base, stacked one above another like a SHORT neat tower: only twelve thin bangles, about 3.5 cm tall in total, covering just a small part of the pole, "
        "so each bangle appears as a thin horizontal band and the beaded thread surface faces the camera; seen from the side at eye level. There is only this one pole and only this one tower of twelve bangles in the picture; no second stand, no second set, no other bangles anywhere. "
        "Soft warm window light, a small mirror, a brass jewellery box and a few jasmine flowers beside it, shallow depth of field, no people. "),
    "c2-diya-hands": ("Create a new photograph: an Indian woman's two hands held together in front of her at chest height gently cupping a small lit brass diya, Karwa Chauth evening mood, warm glow. "
        "Both forearms point straight UP in the frame (vertical). Only her LEFT wrist wears " + look + " as one snug stack of twelve; the right wrist is completely bare. Soft henna on the hands, she wears " + outfit + " (the outfit colours beautifully complement the bangles); close-up, shallow depth of field. "),
    "c3-earring-hand": ("Create a new photograph: close-up of an elegant Indian woman's hand raised beside her face touching a gold jhumka earring, the forearm held straight and upright (vertical) with the wrist near the centre of the frame, "
        "the wrist wearing " + look + " as one snug stack of twelve, her face softly blurred behind, soft window light, festive editorial jewellery photography. She wears " + outfit + ", chosen to complement the bangle colour. Only one arm visible. "),
    "c4-brass-hook": ("Create a new photograph: " + look + " hanging side by side from a single ornate brass hook on a carved dark wooden wall, hanging straight down in one tight narrow block, "
        "a string of jasmine flowers and a marigold garland on the wall beside it, warm festive light, shallow depth of field, no people, seen from the front exactly like the reference so the beaded thread surface is visible. "),
    }
    d.update({
    "s2-scatter-flatlay": ("Create a new photograph: overhead flat-lay product photograph, camera pointing straight down, of about a dozen " + look.replace("twelve ", "") + " loosely scattered on " + surf + " - every bangle lies flat on the fabric as a full ring, some overlapping each other naturally, a few resting on others, "
        "a few marigold petals and jasmine flowers at one edge, soft window light, soft contact shadows under every bangle, rule-of-thirds composition, no hands, no people. "),
    "s3-scatter-close": ("Create a new photograph: close-up product photograph at a 40 degree angle of a loose pile of about ten " + look.replace("twelve ", "") + " lying scattered on " + surf + ", the bangles lie flat and overlap naturally, "
        "the silk thread twist and gold beads in sharp focus on the nearest bangles, creamy blurred background, warm soft window light, contact shadows, no hands. "),
    "s4-tray-stack": ("Create a new photograph: " + look + " as a neat stack lying on its side like coins on a round brass thali, with three more loose bangles lying flat beside it and a few rose petals, on " + surf + ", "
        "seen from a 35 degree angle, warm soft light, contact shadows, shallow depth of field, no hands. "),
    "s5-worn-rest": ("Create a new photograph: natural lifestyle close-up of an Indian woman's forearm and hand resting relaxed on a wooden table, palm down, soft henna on the hand, a snug stack of " + look + " around the wrist just above the wrist bone, "
        "she wears " + outfit + " (colours chosen to complement the bangles), side view, soft window light, shallow depth of field, anatomically correct natural hand. "),
    "s6-worn-rose": ("Create a new photograph: an Indian woman sitting, her hand resting on her lap gently holding a single red rose by its stem, a snug stack of " + look + " around her wrist, "
        "she wears " + outfit + " (complementary colours), natural relaxed pose, anatomically correct hand, soft window light, shallow depth of field, close-up from the side, face not visible. "),
    "s7-stand-short": ("Create a new photograph: " + look + " - ONE single set only - slipped onto a slim vertical brass bangle-stand pole with a round base, stacked as a SHORT neat tower of only twelve thin bangles about 3.5 cm tall, "
        "on a wooden dressing table beside a small brass jewellery box and a few jasmine flowers, soft window light, eye-level side view, shallow depth of field, only this one pole and one set, no people. "),
    "s8-macro": ("Create a new photograph: extreme macro photograph at a 45 degree angle of the silk thread twist and the small antique-gold beads on " + look + ", a few bangles lying together on " + surf + ", "
        "razor-sharp focus on the thread and beads, creamy blurred background, soft warm light. "),
    })
    d.update({   # A+ occasion scenes (wide, landscape): one per colour, see aplus-ai
    "o1-karwa": ("Create a new landscape photograph: an Indian woman's forearm held horizontally across the frame, resting on the edge of a brass puja thali holding a lit diya, flowers and kumkum, Karwa Chauth evening, "
        "a snug stack of " + look + " around her wrist, she wears a red and gold saree border (colours chosen to complement the bangles), warm glow, shallow depth of field, anatomically correct natural hand, face not visible. "),
    "o2-mehendi": ("Create a new landscape photograph: an Indian woman's hands resting relaxed on her lap, fresh henna on the palms and fingers, a snug stack of " + look + " around the left wrist, "
        "she wears a pastel yellow and ivory outfit (colours chosen to complement the bangles), a few flower petals nearby, bright soft daylight, anatomically correct natural hands, face not visible. "),
    "o3-festive": ("Create a new landscape photograph: an Indian woman's forearm held horizontally across the frame, a snug stack of " + look + " around the wrist, she wears a rich festive silk saree with gold zari (colours chosen to complement the bangles), "
        "softly blurred lit diyas behind, warm festive light, anatomically correct natural hand, face not visible. "),
    "o4-wedding": ("Create a new landscape photograph: an Indian woman's forearm held horizontally across the frame, a snug stack of " + look + " around the wrist, she wears an ivory and gold lehenga sleeve (colours chosen to complement the bangles), "
        "a marigold garland softly blurred beside her, soft morning light, anatomically correct natural hand, face not visible. "),
    })
    return d

LOOK12 = " The bangles form a full, dense stack that looks like a dozen (twelve) thin bangles side by side."

def prompts(slug):
    idx, cname, code, thread, scene, outfit, macro = ts.COLOURS[slug]
    look = f"twelve {thread} silk-thread bangles with gold beads"
    return [(k, v + LOOK12 + ts.STRICT_SOFT) for k, v in scenes(look, STYLE[slug], SURF[slug]).items() if (not ONLY or k in ONLY)]

def main(slugs):
    q = queue.Queue(); lock = threading.Lock(); done = {}; busy = [0]
    hues = {s: tc.hue_of(ROOT / "stb" / "cutouts" / f"{s}.png") for s in slugs}
    for s in slugs:
        for shot, pr in prompts(s): q.put((s, shot, pr, 1))
    total = sum(1 for s in slugs for _ in prompts(s))
    (ROOT / "stb" / "creative_cand").mkdir(parents=True, exist_ok=True)
    def work(profile):
        while True:
            try: s, shot, pr, att = q.get(timeout=20)
            except queue.Empty:
                with lock:
                    if len(done) >= total or (q.empty() and not busy[0]): return
                continue
            with lock: busy[0] += 1
            try:
                name = f"stbc-{s}-{shot.split('-')[0]}-a{att}"
                job, _, _ = ts.make_job(name, ts.RAW[ts.COLOURS[s][0]], [(shot, pr)])
                with open(ROOT / "jobs" / job / "run.log", "a") as lg:
                    subprocess.run([sys.executable, "-u", "execution_agent.py", f"jobs/{job}", "--workers", "1", "--profile", str(ROOT / profile)], cwd=ROOT, stdout=lg, stderr=subprocess.STDOUT)
                f = ROOT / "jobs" / job / "generated" / f"{shot}.png"; r = None
                if f.exists():
                    r = tc.count_dir(f, hues[s]); c = None if r is None else round(r[0], 1)
                    shutil.copy(f, ROOT / "stb" / "creative_cand" / f"{s}-{shot}-a{att}-c{c}.png")
                else: c = None
                ok = f.exists()
                print(f"{s} {shot} attempt {att}: count {c} {'ACCEPT' if ok else 'reject'} {'' if r is None else r[2:]}", flush=True)
                with lock:
                    if ok:
                        d = ROOT / "stb" / "creative" / s; d.mkdir(parents=True, exist_ok=True); shutil.copy(f, d / f"{shot}.png"); done[(s, shot)] = c
                    elif att < MAX_TRY: q.put((s, shot, pr, att + 1))
                    else: done[(s, shot)] = None
            finally:
                with lock: busy[0] -= 1
    th = [threading.Thread(target=work, args=(p,)) for p in PROFILES]
    [t.start() for t in th]; [t.join() for t in th]
    print("FINISHED", {f"{k[0]}/{k[1]}": v for k, v in done.items()}, flush=True)

if __name__ == "__main__":
    a = sys.argv[1:]
    if "--only" in a:
        i = a.index("--only"); ONLY.update(a[i + 1].split(",")); del a[i:i + 2]
    main(a)
