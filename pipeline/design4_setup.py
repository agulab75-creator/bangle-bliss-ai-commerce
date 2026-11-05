"""Design 4 — diamante/rhinestone-studded bangle sets (14 colours): auto-crop the raw photos
(removes the grey display rod/background) and build Shopify-Magic jobs (jobs/rg-d4-<slug>).
Source photos: raw/design 4/*.jpg (one or two raw shots per colour).
Run: python design4_setup.py   then   python design4_creative.py <slug> [<slug> ...]
"""
import json
from pathlib import Path
import regen_setup as rs
import thread_setup as ts  # reuse find_box()

ROOT = rs.ROOT
RAW = ROOT / "raw" / "design 4"

# slug: (raw filename, Shopify colour name, SKU code, stone/body colour sentence)
# Identities confirmed visually from design4_contact_sheet.jpg (16 raws -> 14 distinct colourways;
# 134152262/145018166 are the same vivid rose-pink shot twice, 140049346/140415085 the same amber-gold shot twice).
COLOURS = {
    "rose-pink":      ("IMG_20261019_134152262.jpg", "Rose Pink",       "RSP", "a vivid rose-pink lac body"),
    "rani-pink":      ("IMG_20261019_134227982.jpg", "Rani Pink",       "RNP", "a deep rani-pink (magenta-purple) lac body"),
    "emerald-green":  ("IMG_20261019_135905638.jpg", "Emerald Green",   "EMG", "a deep emerald/bottle-green lac body"),
    "amber-gold":     ("IMG_20261019_140049346.jpg", "Amber Gold",      "AMG", "a warm amber-gold metallic body"),
    "plum-black":     ("IMG_20261019_141442836.jpg", "Plum Black",      "PLB", "a deep plum-black lac body"),
    "olive-green":    ("IMG_20261019_141702385.jpg", "Olive Green",     "OLG", "a muted olive/sage-green lac body"),
    "dusty-pink":     ("IMG_20261019_144845852.jpg", "Dusty Pink",      "DSP", "a muted dusty-pink lac body"),
    "teal-blue":      ("IMG_20261019_145215691.jpg", "Teal Blue",       "TLB", "a bright peacock teal-blue lac body"),
    "champagne-gold": ("IMG_20261019_145525254.jpg", "Champagne Gold",  "CHG", "a pale antique champagne-gold metallic body"),
    "red-maroon":     ("IMG_20261019_145732643.jpg", "Red Maroon",      "RDM", "a deep red-crimson lac body"),
    "crystal-white":  ("IMG_20261019_145945879.jpg", "Crystal White",   "CRW", "a clean white lac body"),
    "mauve-pink":     ("IMG_20261019_150132091.jpg", "Mauve Pink",      "MVP", "a dusty mauve-rose lac body"),
    "baby-pink":      ("IMG_20261019_150604494.jpg", "Baby Pink",       "BBP", "a pale baby-pink lac body"),
    "gunmetal-black": ("IMG_20261019_150820923.jpg", "Gunmetal Black",  "GMB", "a deep gunmetal-black lac body"),
}

STRICT = (
    " STRICT RULES: there are EXACTLY 12 bangles in the picture, a full dozen - count them, it must be 12, never 8, "
    "never 10, never 14; all 12 are identical in design and size and sit snugly side by side. Copy the bangle design "
    "from the reference photo EXACTLY: each bangle is a slim rigid round band with " "{body}" " densely studded, edge "
    "to edge, with several tight parallel rows of small round faceted rhinestones running all the way around - most "
    "rows in the body colour, with rows of clear/silver diamante stones mixed in, so the surface sparkles all over. "
    "Do not change the body colour, do not turn it into plain smooth glass, do not turn it into painted enamel, do not "
    "turn it into silk thread, do not add or remove stone rows. It is a RIGID metal/lac bangle densely paved with real "
    "rhinestones: never translucent glass, never matte fabric, never soft or bendable. No text, no watermark, no logo, "
    "no extra jewellery, no extra bangles on the wrist.")

BLOCK = ("The twelve bangles stand upright on their edge, side by side in ONE tight compact row forming a neat narrow "
         "block, seen from the front exactly like the reference so the studded stone surface of every bangle is visible.")


def strict_for(body):
    return STRICT.replace("{body}", body)


# manual fallback crop boxes (fractions) for colours too dark/low-saturation for the auto-detector
MANUAL_BOX = {
    "plum-black": (0.33, 0.30, 0.62, 0.65),
    "crystal-white": (0.36, 0.30, 0.62, 0.65),
}


def make_job(name, src, shot_list, box_override=None):
    d = rs.JOBS / f"rg-{name}"
    for sub in ("original", "generated", "approved", "rejected", "logs"):
        (d / sub).mkdir(parents=True, exist_ok=True)
    box = box_override or ts.find_box(src)
    from PIL import Image, ImageOps
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    W, H = im.size
    c = im.crop((int(W * box[0]), int(H * box[1]), int(W * box[2]), int(H * box[3])))
    c.save(d / "original" / "ref-crop.jpg", quality=95)
    (d / "status.json").write_text(json.dumps({"phase": "queued", "images_generated": False}, indent=4))
    q = [{"id": i, "prompt": p, "status": "pending", "retries": 0, "output_file": i + ".png"} for i, p in shot_list]
    (d / "image_queue.json").write_text(json.dumps(q, indent=4))
    return d.name, c.size, box


def hero_shot(body):
    look = f"twelve bangles, each with {body}"
    return [("1-white-studio",
             "Create a new photograph: professional e-commerce studio product photograph of " + look +
             " on a clean pure white seamless background, soft even studio light, a faint soft contact shadow, "
             "sharp focus, no rod, no stand, no roller, no hand, no props, no text. " + BLOCK + strict_for(body))]


if __name__ == "__main__":
    names = []
    for slug, (fname, cname, code, body) in COLOURS.items():
        src = RAW / fname
        n, size, box = make_job(f"d4-{slug}", src, hero_shot(body), box_override=MANUAL_BOX.get(slug))
        names.append(n)
        print(n, size, [round(v, 2) for v in box])
    (ROOT / "jobs" / "design4_jobs.json").write_text(json.dumps(names))
