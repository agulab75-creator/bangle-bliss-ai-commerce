"""Silk Thread Bangles (STB): colour table, auto-crop of the raw photos and Shopify-Magic jobs (jobs/rg-stb-<slug>, 4 shots each).
Source photos: raw/Thread bangles/*.jpeg (11 colours, a dozen bangles in each photo).
Run: python thread_setup.py   then   python thread_run.py"""
import json, glob
from pathlib import Path
import numpy as np, cv2
from PIL import Image, ImageOps
import regen_setup as rs

ROOT = rs.ROOT
RAW = sorted(glob.glob(str(ROOT / "raw" / "Thread bangles" / "*")))

# slug: (raw index, Shopify colour name, SKU code, thread look, scene, outfit, macro background)
COLOURS = {
    "mustard-yellow": (0, "Mustard Yellow", "MYL", "deep mustard-yellow", "deep maroon velvet with orange marigold petals and a small lit brass diya", "a maroon and gold silk sleeve", "warm gold and deep red"),
    "coral-pink": (1, "Coral Pink", "CRP", "soft coral-pink (salmon pink)", "ivory silk with white jasmine flowers and a string of pearls, soft morning light", "an ivory and gold silk sleeve", "blush pink and cream"),
    "turquoise": (2, "Turquoise", "TRQ", "bright turquoise-teal", "white linen with white jasmine flowers and pearls, soft diffused window light", "a cream and peach anarkali sleeve", "pale aqua and pearl white"),
    "royal-blue": (3, "Royal Blue", "RBL", "deep royal-blue (cobalt)", "ivory and gold brocade with a lit brass diya and a few marigold petals, warm festive light", "an ivory and gold silk sleeve", "warm gold and deep blue"),
    "crimson-red": (4, "Crimson Red", "RED", "rich crimson-red", "gold zari silk with lit brass diyas and a few red rose petals, warm Karwa Chauth glow", "a cream and gold bridal sleeve, dark rich henna on the hand", "warm gold with soft diya lights"),
    "parrot-green": (5, "Parrot Green", "PGR", "bright parrot-green (lime-leaf green)", "cream raw silk with yellow marigold petals and green leaves, bright fresh morning light", "a cream and gold chikankari sleeve", "pale green and cream"),
    "emerald-green": (6, "Emerald Green", "EMR", "deep emerald-green", "deep red velvet with gold ornaments and a few rose petals, warm festive glow", "a red and gold Banarasi sleeve", "warm gold and soft red"),
    "rani-pink": (7, "Rani Pink", "RNP", "vivid rani-pink (hot magenta pink)", "cream raw silk with blush pink roses and gold zari, soft light", "a cream and gold silk sleeve", "soft cream and gold"),
    "wine-maroon": (8, "Wine Maroon", "WMR", "deep wine-maroon (burgundy plum)", "cream and gold brocade with a small brass lamp and dried rose petals, warm light", "a cream and gold sleeve", "warm gold and burgundy"),
    "orange": (9, "Orange", "ORG", "bright saffron-orange", "deep green silk with a yellow marigold garland and a small brass diya", "a green silk saree sleeve with gold border", "warm gold and deep green"),
    "golden": (10, "Golden", "GLD", "pale champagne-gold (metallic gold thread)", "deep green velvet with a few red rose petals and a small brass diya, warm light", "a deep green silk sleeve with gold border", "warm gold and deep green"),
}

STRICT = (" STRICT RULES: there are EXACTLY 12 bangles in the picture, a full dozen - count them, it must be 12, never 8, never 10, never 14; "
          "all 12 are identical in design and size and sit snugly side by side. Copy the bangle design from the reference photo EXACTLY: "
          "each bangle is a slim round band tightly wrapped in glossy silk thread of ONE solid colour with the fine diagonal thread twist clearly visible, "
          "and small round antique-gold metal beads stitched onto the thread at scattered, irregular intervals. Do not change the thread colour, "
          "do not add or remove beads, do not turn the beads into stones, pearls or crystals, do not add glass, painted motifs, tassels or any other decoration. "
          "It is REAL SILK THREAD texture: never plain glass, never plastic, never smooth metal. No text, no watermark, no logo, no extra jewellery, no extra bangles on the wrist.")
STRICT_SOFT = (" Copy the bangle design from the reference photo: each bangle is a slim round band tightly wrapped in glossy silk thread of ONE solid colour with the fine diagonal thread twist visible, "
               "and small round antique-gold metal beads stitched onto the thread at scattered, irregular intervals. Keep the exact thread colour. Do not turn the beads into stones or pearls, no glass, no painted motifs, no tassels. "
               "Real silk thread texture. No text, no watermark, no logo.")
BLOCK = ("The twelve bangles stand upright on their edge, side by side in ONE tight compact row forming a neat narrow block, "
         "seen from the front exactly like the reference so the beaded thread surface of every bangle is visible.")


def shots(look, scene, outfit, macro_bg):
    s1 = ("Create a new photograph: professional e-commerce studio product photograph of " + look + " on a clean pure white seamless background, "
          "soft even studio light, a faint soft contact shadow, sharp focus, no rod, no stand, no roller, no hand, no props, no text. " + BLOCK + STRICT)
    s2 = ("Create a new photograph: premium jewellery lifestyle product photograph of " + look + " resting on " + scene +
          ", Indian festive elegance, shallow depth of field, no people, no hand, no text, no plain white or grey background. "
          "The twelve bangles stand upright on their edge side by side in one tight row in the centre of the frame, large and clearly visible. " + STRICT)
    s3 = ("Create a new photograph: close-up of an elegant Indian woman's hand and wrist, soft henna on the hand, natural skin, wearing " + look +
          " as one full snug stack on a single wrist, " + outfit + ", soft window light, premium jewellery photography. All twelve slim bangles sit side by side "
          "touching each other on the wrist forming one neat full stack, the beaded thread surface facing the camera. Only ONE arm and ONE hand in the frame, natural relaxed fingers. " + STRICT)
    s4 = ("Create a new photograph: extreme macro close-up of " + look + ", the twelve bangles filling the frame side by side as vertical bands, showing the silk thread twist "
          "and the antique-gold beads sharply, shallow depth of field, soft creamy blurred background in " + macro_bg + ", luxury jewellery photography. " + STRICT)
    return [("1-white-studio", s1), ("2-lifestyle", s2), ("3-wrist-shot", s3), ("4-closeup", s4)]


def find_box(path, pad=0.14):
    """Bounding box (fractions) of the coloured bangle block: saturated, non-grey pixels."""
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    small = im.resize((im.width // 6, im.height // 6))
    hsv = cv2.cvtColor(np.asarray(small), cv2.COLOR_RGB2HSV)
    m = ((hsv[:, :, 1] > 90) & (hsv[:, :, 2] > 40)).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    k = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    x, y, w, h, _ = st[k]
    W, H = small.size
    return (max(0, x / W - pad * w / W), max(0, y / H - pad * h / H), min(1, (x + w) / W + pad * w / W), min(1, (y + h) / H + pad * h / H))


def make_job(name, src, shot_list):
    d = rs.JOBS / f"rg-{name}"
    for sub in ("original", "generated", "approved", "rejected", "logs"):
        (d / sub).mkdir(parents=True, exist_ok=True)
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    box = find_box(src)
    W, H = im.size
    c = im.crop((int(W * box[0]), int(H * box[1]), int(W * box[2]), int(H * box[3])))
    c.save(d / "original" / "ref-crop.jpg", quality=95)
    (d / "status.json").write_text(json.dumps({"phase": "queued", "images_generated": False}, indent=4))
    q = [{"id": i, "prompt": p, "status": "pending", "retries": 0, "output_file": i + ".png"} for i, p in shot_list]
    (d / "image_queue.json").write_text(json.dumps(q, indent=4))
    return d.name, c.size, box


if __name__ == "__main__":
    names = []
    for slug, (idx, cname, code, thread, scene, outfit, macro) in COLOURS.items():
        look = f"twelve {thread} silk-thread bangles with gold beads"
        n, size, box = make_job(f"stb-{slug}", RAW[idx], shots(look, scene, outfit, macro))
        names.append(n)
        print(n, size, [round(v, 2) for v in box])
    (ROOT / "jobs" / "stb_jobs.json").write_text(json.dumps(names))
