"""Design 4 — varied lifestyle/creative shots per colour, drawn randomly from a 13-prompt pool so the
14 colours don't look templated. Modeled on thread_creative.py.

2026-10-19 owner feedback: never generate "bangle-stand" again (the pole makes the bangles look like
they're floating / not real) - retired from the pool entirely. Macro must crop in tight on the stones,
not show the whole bangle. Pool widened to 13 shot types; each colour gets a random 4-5 of them instead
of the same fixed set, so colours stop looking like copies of each other with only the colour swapped.

Usage: python design4_creative.py <slug> [<slug> ...]   (or "all")
       python design4_creative.py --redo <slug>:<shot> [<slug>:<shot> ...]   (regenerate specific flagged shots,
       picking a fresh random shot type per item, never repeating a type that colour already has)
Output: jobs/rg-d4c-<slug>-<shot>/generated/<shot>.png
"""
import json, random, shutil, sys
from pathlib import Path
import design4_setup as ds

ROOT = ds.ROOT
SLUGS = list(ds.COLOURS.keys())

# complementary outfit/surface/prop per colour (not matching the bangle colour)
STYLE = {
    "rose-pink":      dict(surf="deep teal silk",      outfit="an ivory and gold silk sleeve",            prop="a few white jasmine flowers"),
    "rani-pink":      dict(surf="mustard-yellow silk",  outfit="an ivory and gold Banarasi sleeve",        prop="a few marigold petals"),
    "emerald-green":  dict(surf="cream raw silk",       outfit="a deep red and gold Banarasi sleeve",      prop="a few red rose petals"),
    "amber-gold":     dict(surf="deep green velvet",    outfit="a deep green silk saree sleeve with gold border", prop="a small brass diya and marigolds"),
    "plum-black":     dict(surf="ivory linen",          outfit="an ivory and silver zari sleeve",          prop="a string of pearls"),
    "olive-green":    dict(surf="deep maroon velvet",   outfit="a mustard-yellow and white bandhani sleeve", prop="a few dried rose petals"),
    "dusty-pink":     dict(surf="white linen",          outfit="an ivory chikankari sleeve",                prop="a string of pearls and jasmine"),
    "teal-blue":      dict(surf="soft peach silk",      outfit="a peach and gold lehenga sleeve",           prop="pearl strings"),
    "champagne-gold": dict(surf="deep red velvet",      outfit="a deep red and gold brocade sleeve",        prop="a small brass diya"),
    "red-maroon":     dict(surf="gold zari silk",       outfit="a cream and gold Banarasi sleeve",          prop="a few marigold petals and a lit diya"),
    "crystal-white":  dict(surf="blush-pink silk",      outfit="a blush-pink and silver sleeve with pearls", prop="a string of pearls"),
    "mauve-pink":     dict(surf="cream raw silk",       outfit="a cream and gold silk sleeve",              prop="a few blush rose petals"),
    "baby-pink":      dict(surf="dusty-blue silk",      outfit="a dusty-blue and silver sleeve",            prop="white jasmine flowers"),
    "gunmetal-black": dict(surf="silver-grey satin",    outfit="an ivory and silver zari sleeve",           prop="a string of pearls"),
}

# Shot pool. No bangle-stand (owner: looks fake/floating). No hooks/door-handles (shot-guide rule 6: only
# allowed holders are a stand -- now retired too -- a velvet roll, a plate/tray, or the wrist).
# 2026-10-19 owner feedback round 2: "scatter-flatlay"/"scatter-geometric" (camera straight down) are
# retired too - a bangle seen edge-on from directly overhead doesn't show its stone design. "macro" is no
# longer an AI-generated shot at all (it kept drawing the wrong stone pattern) - see make_macro() below,
# which crops straight into the verified white-studio hero instead, so the design is always correct.
POOL = [
    "scatter-close", "tray-stack", "tray-scatter", "velvet-roll",
    "worn-relaxed", "worn-prop", "worn-dupatta", "worn-diya", "worn-teacup", "worn-mehendi-close",
]

# Added to every shot that shows multiple loose/overlapping bangles, after the owner flagged a scatter
# shot that read as "one thick bangle with three lines of stones" instead of distinct bangles touching.
DISTINCT = (" Every bangle must read as a clearly separate, individual ring - each with its own visible "
            "outer edge and its own single row (or rows) of stones, with a visible thin gap, edge-line or "
            "shadow between any two bangles that touch or overlap. NEVER let two or more bangles merge, "
            "fuse or blend into what looks like one thicker band or one bangle with multiple stone rows; "
            "if they overlap, one bangle clearly rests ON TOP of the other as two distinct rigid rings.")


def scenes(body, style, extra):
    look = f"twelve bangles, each with {body}"
    surf, outfit, prop = style["surf"], style["outfit"], style["prop"]
    return {
        "scatter-close": (
            "Create a new photograph: close-up product photograph at a 40 degree angle (NOT from directly overhead - "
            "angled so the side profile and stone design of each bangle is clearly visible) of a loose pile of 5 to 6 "
            "bangles with " + body + " lying scattered on " + surf + ", the bangles lie flat and overlap naturally, "
            "the studded stone surface in sharp focus on the nearest bangles, creamy blurred background, warm soft "
            "window light, contact shadows, no hands." + DISTINCT),
        "tray-stack": (
            "Create a new photograph: " + look + " as a neat stack lying on its side like coins on a round brass "
            "thali - the stack is ONLY twelve bangles tall, the same short height as the twelve bangles in the "
            "reference photo, never taller, never add extra bangles to the stack - with three more loose bangles "
            "lying flat beside it and " + prop + ", on " + surf + ", seen from a 35 degree angle, warm soft light, "
            "contact shadows, shallow depth of field, no hands."),
        "tray-scatter": (
            "Create a new photograph: 5 to 6 bangles with " + body + " scattered loosely inside a round silver or "
            "brass serving tray, shot at an angle (NOT from directly overhead) so the side profile and stone design of "
            "each bangle is clearly visible, some lying flat overlapping each other, " + prop + " tucked among them, "
            "the tray resting on " + surf + ", shot from a 45 degree angle, soft window light, crisp contact shadows, "
            "shallow depth of field, no hands." + DISTINCT),
        "velvet-roll": (
            "Create a new photograph: " + look + " laid inside an open velvet jewellery roll (a soft fabric case that "
            "unrolls flat with slots), each bangle resting in its own slot so all twelve are visible side by side, the "
            "roll open on " + surf + ", soft warm light, shallow depth of field, no hands, no people."),
        "worn-relaxed": (
            "Create a new photograph: natural lifestyle close-up of an Indian woman's forearm and hand resting relaxed "
            "on a wooden table, palm down, soft henna on the hand, a snug stack of twelve bangles with " + body +
            " around the wrist just above the wrist bone, she wears " + outfit + " (colours chosen to complement the "
            "bangles), side view, soft window light, shallow depth of field, anatomically correct natural hand."),
        "worn-prop": (
            "Create a new photograph: an Indian woman sitting, her hand resting on her lap gently holding " + extra +
            " by the stem, a snug stack of twelve bangles with " + body + " around her wrist, she wears " + outfit +
            " (complementary colours), natural relaxed pose, anatomically correct hand, soft window light, shallow "
            "depth of field, close-up from the side, face not visible."),
        "worn-dupatta": (
            "Create a new photograph: close-up of an Indian woman's hand gently pinching the embroidered edge of a "
            "dupatta near her shoulder, forearm angled across the frame, a snug stack of twelve bangles with " + body +
            " around her wrist, she wears " + outfit + " (complementary colours), soft window light, shallow depth of "
            "field, anatomically correct hand, face not visible."),
        "worn-diya": (
            "Create a new photograph: an Indian woman's two hands held together at chest height gently cupping a small "
            "lit brass diya resting in her palms, warm evening glow, only her LEFT wrist wearing a snug stack of twelve "
            "bangles with " + body + ", the right wrist bare, she wears " + outfit + " (complementary colours), soft "
            "henna on the hands, close-up, shallow depth of field, anatomically correct hands."),
        "worn-teacup": (
            "Create a new photograph: close-up of an Indian woman's hand holding a small ceramic teacup by its handle, "
            "forearm resting on a wooden table edge, a snug stack of twelve bangles with " + body + " around her wrist, "
            "she wears " + outfit + " (complementary colours), soft morning window light, shallow depth of field, "
            "anatomically correct hand, face not visible."),
        "worn-mehendi-close": (
            "Create a new photograph: tight close-up of an Indian woman's hand resting palm-down in her lap, fresh "
            "henna covering the back of the hand and fingers, a snug stack of twelve bangles with " + body + " around "
            "the wrist, she wears " + outfit + " (complementary colours), bright soft daylight, shallow depth of field, "
            "anatomically correct natural hand, face not visible."),
    }


LOOK12 = " The bangles form a full, dense stack that looks like a dozen (twelve) thin bangles side by side."
EXTRA_PROP = {
    0: "a single red rose", 1: "a single white jasmine sprig", 2: "a single pink rose",
    3: "a marigold flower", 4: "a single peach rose",
}


def make_shot_job(slug, shot, prompt):
    name = f"d4c-{slug}-{shot}"
    d = ROOT / "jobs" / f"rg-{name}"
    for sub in ("original", "generated", "approved", "rejected", "logs"):
        (d / sub).mkdir(parents=True, exist_ok=True)
    src = ROOT / "jobs" / f"rg-d4-{slug}" / "original" / "ref-crop.jpg"
    shutil.copy(src, d / "original" / "ref-crop.jpg")
    (d / "status.json").write_text(json.dumps({"phase": "queued", "images_generated": False}, indent=4))
    q = [{"id": shot, "prompt": prompt + LOOK12, "status": "pending", "retries": 0, "output_file": shot + ".png"}]
    (d / "image_queue.json").write_text(json.dumps(q, indent=4))
    return d.name


def build_prompt(slug, shot, extra_idx=0):
    _, cname, code, body = ds.COLOURS[slug]
    style = STYLE[slug]
    sc = scenes(body, style, EXTRA_PROP[extra_idx % 5])
    return sc[shot] + ds.strict_for(body)


def build(slug, i, k=None):
    """Pick a random k (4-5) shots for this colour, seeded by slug so re-running is reproducible."""
    rnd = random.Random(slug)
    k = k or rnd.choice([4, 5])
    shots = rnd.sample(POOL, k)
    jobs = []
    for j, shot in enumerate(shots):
        jobs.append(make_shot_job(slug, shot, build_prompt(slug, shot, extra_idx=i + j)))
    return jobs


def make_macro(slug, seed=None):
    """Macro is a deterministic crop/zoom of the verified white-studio hero, not a fresh AI generation -
    the AI kept drawing the wrong stone pattern when asked to imagine a macro shot from scratch."""
    from PIL import Image
    hero = ROOT / "jobs" / f"rg-d4-{slug}" / "generated" / "1-white-studio.png"
    d = ROOT / "jobs" / f"rg-d4c-{slug}-macro" / "generated"
    d.mkdir(parents=True, exist_ok=True)
    im = Image.open(hero).convert("RGB")
    W, H = im.size
    rnd = random.Random(seed or slug)
    cx = 0.50 + rnd.uniform(-0.10, 0.10)
    cy = 0.52 + rnd.uniform(-0.08, 0.08)
    w = 0.16 + rnd.uniform(-0.02, 0.03)
    h = w
    box = (int(W * (cx - w / 2)), int(H * (cy - h / 2)), int(W * (cx + w / 2)), int(H * (cy + h / 2)))
    c = im.crop(box)
    c = c.resize((c.width * 3, c.height * 3), Image.LANCZOS)
    out = d / "macro.png"
    c.save(out)
    return out


def existing_shots(slug):
    return {p.name[len(f"rg-d4c-{slug}-"):] for p in ROOT.glob(f"jobs/rg-d4c-{slug}-*") if p.is_dir()}


def redo(pairs):
    """pairs: list of 'slug:old-shot'. Replaces each with a random NEW shot type that colour doesn't already
    have (or, for 'macro', just re-crops the hero again - macro is never AI-generated)."""
    jobs = []
    for pair in pairs:
        slug, old_shot = pair.split(":", 1)
        rnd = random.Random(slug + ":" + old_shot)
        if old_shot == "macro":
            shutil.rmtree(ROOT / "jobs" / f"rg-d4c-{slug}-macro", ignore_errors=True)
            make_macro(slug, seed=slug + ":redo")
            print(f"{slug}: macro -> macro (re-cropped)")
            continue
        have = existing_shots(slug) - {old_shot}
        choices = [s for s in POOL if s not in have]
        new_shot = rnd.choice(choices)
        old_dir = ROOT / "jobs" / f"rg-d4c-{slug}-{old_shot}"
        if old_dir.exists():
            shutil.rmtree(old_dir)
        jobs.append(make_shot_job(slug, new_shot, build_prompt(slug, new_shot, extra_idx=rnd.randint(0, 4))))
        print(f"{slug}: {old_shot} -> {new_shot}")
    return jobs


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "--macro":
        slugs = args[1:] or SLUGS
        for slug in slugs:
            shutil.rmtree(ROOT / "jobs" / f"rg-d4c-{slug}-macro", ignore_errors=True)
            p = make_macro(slug)
            print(slug, "->", p)
    elif args and args[0] == "--redo":
        all_jobs = redo(args[1:])
        (ROOT / "jobs" / "design4_redo_jobs.json").write_text(json.dumps(all_jobs))
        print(f"\n{len(all_jobs)} redo jobs queued.")
    else:
        slugs = SLUGS if (not args or args == ["all"]) else args
        all_jobs = []
        for i, slug in enumerate(slugs):
            js = build(slug, i)
            all_jobs.extend(js)
            print(slug, js)
        (ROOT / "jobs" / "design4_creative_jobs.json").write_text(json.dumps(all_jobs))
        print(f"\n{len(all_jobs)} creative jobs queued.")
