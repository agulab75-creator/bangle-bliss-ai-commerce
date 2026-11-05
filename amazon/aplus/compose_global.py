"""Global (all-colour) A+ module images for KSG: Magic scenes + deterministic Pillow layouts.

python aplus/compose_global.py            -> aplus/out/KSG-global/
Colour wall / range strip use the REAL studio shots (colour accuracy matters), never Magic output.
Facts used: set of 4, sizes 2.4/2.6/2.8 inches, 13 colours. No prices, offers, guarantees or superlatives.
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw
sys.path.insert(0, str(Path(__file__).parent))
from compose import ROOT, MAROON, GOLD, CREAM, INK, font, SERIF, SERIF_B, SANS, SANS_B, cover, text_block, save

OUT = Path(__file__).parent / "out" / "KSG-global"
LAT = ROOT / "amazon-latest-images"

def scene(slug):
    gen = sorted((ROOT / "jobs" / slug / "generated").glob("*.*"))
    if not gen: raise SystemExit(f"no Magic output yet for {slug}")
    return Image.open(gen[0]).convert("RGB")

def studio(product, colour):
    return Image.open(next((LAT / product / colour).glob("*white-studio*.jpg"))).convert("RGB")

def hero():
    im = cover(scene("aplus-ksg-hero-flatlay"), 970, 600, fx=0.5, fy=0.5)
    fade = Image.new("L", im.size); px = fade.load()
    for x in range(im.width):
        a = max(0, int(225 * (1 - x / 520)))
        for y in range(im.height): px[x, y] = a
    im.paste(Image.new("RGB", im.size, MAROON), mask=fade)
    d = ImageDraw.Draw(im)
    d.text((48, 120), "BANGLE BLISS", font=font(SANS_B, 24), fill=GOLD)
    d.rectangle((48, 160, 118, 163), fill=GOLD)
    y = text_block(d, (48, 186), "Kundan Stone Glass Bangles", font(SERIF_B, 54), CREAM, 430, 1.1)
    text_block(d, (48, y + 16), "Set of 4  \u00b7  13 colours", font(SANS, 30), CREAM, 430)
    bar = Image.new("RGB", (970, 84), MAROON); im.paste(bar, (0, 516))
    d = ImageDraw.Draw(im)
    for i, t in enumerate(["Faceted glass", "Kundan stones", "13 colours", "Sizes 2.4 \u00b7 2.6 \u00b7 2.8"]):
        f = font(SANS_B, 25); w = d.textlength(t, font=f)
        d.text((48 + i * 232 + (200 - w) / 2, 543), t, font=f, fill=CREAM)
    save(im, OUT / "01-hero-970x600.jpg")

def four_up():
    for i, (slug, key) in enumerate([("aplus-ksg-diya-hand", "diya"), ("aplus-ksg-velvet-tray", "tray"),
                                     ("aplus-ksg-lehenga-wrist", "lehenga"), ("aplus-ksg-haldi-flatlay", "haldi")]):
        save(cover(scene(slug), 220, 220), OUT / f"02-four-image-{i+1}-{key}.jpg")

def colour_wall():
    colours = ["Sky-Aqua", "Mint-Green", "Parrot-Green", "Lime-Green", "Emerald-Green", "Lemon-Yellow", "Coral-Peach",
               "Rust-Orange", "Ruby-Red", "Maroon", "Magenta", "Orchid-Pink", "Plum-Wine"]
    im = Image.new("RGB", (970, 600), CREAM); d = ImageDraw.Draw(im)
    cw, ch = 194, 200
    cells = colours + ["__badge", "__sizes"]
    for i, c in enumerate(cells):
        x, y = (i % 5) * cw, (i // 5) * ch
        if c.startswith("__"):
            d.rectangle((x, y, x + cw, y + ch), fill=MAROON)
            lines = ["13", "COLOURS"] if c == "__badge" else ["SIZES", "2.4 2.6 2.8"]
            f1, f2 = font(SERIF_B, 64 if c == "__badge" else 34), font(SANS_B, 26)
            w1 = d.textlength(lines[0], font=f1); w2 = d.textlength(lines[1], font=f2)
            d.text((x + (cw - w1) / 2, y + 60), lines[0], font=f1, fill=GOLD)
            d.text((x + (cw - w2) / 2, y + 140), lines[1], font=f2, fill=CREAM)
            continue
        s = studio("KSG", c); m = int(s.width * 0.14)
        tile = cover(s.crop((m, m, s.width - m, s.height - m)), cw, ch - 42, fy=0.5)
        im.paste(tile, (x, y))
        label = c.replace("-", " ")
        f = font(SANS_B, 25)
        d.rectangle((x, y + ch - 42, x + cw, y + ch), fill=(255, 255, 255))
        d.text((x + (cw - d.textlength(label, font=f)) / 2, y + ch - 36), label, font=f, fill=MAROON)
        d.rectangle((x, y, x + cw, y + ch), outline=CREAM, width=3)
    save(im, OUT / "03-colour-wall-970x600.jpg")

def size_guide():
    im = Image.new("RGB", (970, 600), CREAM); d = ImageDraw.Draw(im)
    d.text((48, 36), "FIND YOUR FIT", font=font(SANS_B, 24), fill=GOLD)
    d.text((48, 72), "Sizes 2.4, 2.6 and 2.8", font=font(SERIF_B, 46), fill=MAROON)
    steps = ["Bring your thumb and little finger together.",
             "The bangle should just slide over the widest part of your hand.",
             "Between two sizes? Choose the larger one."]
    y = 150
    for n, t in enumerate(steps, 1):
        d.ellipse((48, y, 48 + 56, y + 56), fill=MAROON)
        d.text((48 + 28 - 9, y + 8), str(n), font=font(SERIF_B, 34), fill=GOLD)
        yy = text_block(d, (126, y + 4), t, font(SANS_B, 28), INK, 430, 1.2)
        y = max(y + 100, yy + 24)
    rows = [("2.4", "6.1 cm"), ("2.6", "6.6 cm"), ("2.8", "7.1 cm")]
    x0 = 600
    d.rounded_rectangle((x0, 150, 922, 540), 18, fill=MAROON)
    d.text((x0 + 28, 168), "INNER DIAMETER", font=font(SANS_B, 24), fill=GOLD)
    for i, (inch, cm) in enumerate(rows):
        yy = 232 + i * 98
        d.text((x0 + 28, yy), inch + '"', font=font(SERIF_B, 54), fill=CREAM)
        d.text((x0 + 180, yy + 14), cm, font=font(SANS_B, 36), fill=GOLD)
        if i < 2: d.line((x0 + 28, yy + 84, 922 - 28, yy + 84), fill=GOLD, width=1)
    save(im, OUT / "04-size-guide-970x600.jpg")

def range_strip():
    items = [("KSG", "Ruby-Red", "Kundan Stone Glass"), ("KMS", "Rani-Pink", "Kundan Multi Stone Glass"),
             ("GVK", "Emerald-Green", "Gold Vine Kundan Glass")]
    im = Image.new("RGB", (970, 300), CREAM); d = ImageDraw.Draw(im)
    for i, (p, c, name) in enumerate(items):
        x = 10 + i * 320
        s = studio(p, c); m = int(s.width * 0.14)
        im.paste(cover(s.crop((m, m, s.width - m, s.height - m)), 300, 240), (x, 10))
        d.rectangle((x, 250, x + 300, 290), fill=MAROON)
        f = font(SANS_B, 25); d.text((x + (300 - d.textlength(name, font=f)) / 2, 257), name, font=f, fill=CREAM)
    save(im, OUT / "05-range-970x300.jpg")

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    colour_wall(); size_guide(); range_strip()          # no Magic needed
    if all(any((ROOT / "jobs" / s / "generated").glob("*.*")) for s in
           ["aplus-ksg-hero-flatlay", "aplus-ksg-diya-hand", "aplus-ksg-velvet-tray", "aplus-ksg-lehenga-wrist", "aplus-ksg-haldi-flatlay"]
           if (ROOT / "jobs" / s / "generated").exists()):
        hero(); four_up()
    print(sorted(p.name for p in OUT.glob("*.jpg")))


# ---------------------------------------------------------------- v2: text-on-image, premium look ----
OUT2 = Path(__file__).parent / "out" / "KSG-global-v2"
SERIF_I = "georgiai.ttf"


def gradient_left(im, width, alpha=235, color=MAROON, plateau=0):
    fade = Image.new("L", im.size); px = fade.load()
    for x in range(im.width):
        a = alpha if x < plateau else max(0, int(alpha * (1 - (x - plateau) / max(1, width - plateau))))
        for y in range(im.height): px[x, y] = a
    im.paste(Image.new("RGB", im.size, color), mask=fade)


def gold_frame(im, inset=14, w=2):
    ImageDraw.Draw(im).rectangle((inset, inset, im.width - inset, im.height - inset), outline=GOLD, width=w)


def hero2():
    im = cover(scene("aplus-ksg-hero-flatlay"), 970, 600, fx=0.5, fy=0.5)
    gradient_left(im, 600, alpha=238, plateau=360)
    d = ImageDraw.Draw(im)
    d.text((56, 92), "BANGLE BLISS", font=font(SANS_B, 24), fill=GOLD)
    d.rectangle((56, 130, 126, 133), fill=GOLD)
    y = text_block(d, (56, 152), "Kundan Stone Glass Bangles", font(SERIF_B, 54), CREAM, 420, 1.08)
    y = text_block(d, (56, y + 10), "Where every facet catches the light.", font(SERIF_I, 30), (232, 196, 120), 400, 1.25)
    text_block(d, (56, y + 14), "Set of 4  \u00b7  13 colours", font(SANS_B, 28), CREAM, 420)
    d.rectangle((0, 516, 970, 600), fill=MAROON)
    for i, t in enumerate(["Faceted glass", "Kundan stones", "13 colours", "Sizes 2.4 \u00b7 2.6 \u00b7 2.8"]):
        f = font(SANS_B, 25); w = d.textlength(t, font=f)
        d.text((48 + i * 232 + (200 - w) / 2, 543), t, font=f, fill=CREAM)
    gold_frame(im)
    save(im, OUT2 / "01-hero-970x600.jpg")


def icon(d, kind, cx, cy, r=27):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=GOLD, width=3)
    if kind == "facet":      # cut gem
        d.polygon([(cx - 13, cy - 4), (cx - 7, cy - 12), (cx + 7, cy - 12), (cx + 13, cy - 4), (cx, cy + 14)], outline=GOLD, width=3)
    elif kind == "stone":    # stone in a ring
        d.ellipse((cx - 13, cy - 13, cx + 13, cy + 13), outline=GOLD, width=3); d.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), fill=GOLD)
    elif kind == "colour":   # three overlapping dots
        for dx in (-9, 9, 0):
            d.ellipse((cx + dx - 9, cy + (8 if dx == 0 else -4) - 9, cx + dx + 9, cy + (8 if dx == 0 else -4) + 9), outline=GOLD, width=3)
    else:                    # set of four bars
        for i in range(4): d.rounded_rectangle((cx - 15 + i * 10, cy - 12, cx - 10 + i * 10, cy + 12), 2, fill=GOLD)


def features2():
    im = Image.new("RGB", (970, 600), MAROON)
    im.paste(cover(scene("aplus-ksg-velvet-tray"), 470, 600, fx=0.5, fy=0.5), (500, 0))   # scene on the right, text left
    gradient_strip = Image.new("L", (60, 600)); gp = gradient_strip.load()
    for x in range(60):
        for y in range(600): gp[x, y] = int(255 * (1 - x / 60))
    im.paste(Image.new("RGB", (60, 600), MAROON), (500, 0), gradient_strip)             # soft seam
    d = ImageDraw.Draw(im)
    d.text((56, 44), "THE DETAILS", font=font(SANS_B, 24), fill=GOLD)
    d.text((56, 78), "Made to be noticed", font=font(SERIF_B, 50), fill=CREAM)
    rows = [("facet", "Faceted glass", "Cut surfaces that catch the light"),
            ("stone", "Kundan stones", "Set in thin gold-coloured rings"),
            ("colour", "13 colours", "From Sky Aqua to Plum Wine"),
            ("set", "Set of 4", "Sizes 2.4, 2.6 and 2.8")]
    for i, (k, t, s) in enumerate(rows):
        y = 170 + i * 98
        icon(d, k, 84, y + 36)
        d.text((136, y + 2), t, font=font(SANS_B, 32), fill=CREAM)
        d.text((136, y + 42), s, font=font(SANS, 25), fill=(235, 220, 200))
        if i < 3: d.line((56, y + 86, 470, y + 86), fill=(150, 80, 90), width=1)
    gold_frame(im)
    save(im, OUT2 / "02-features-970x600.jpg")


def occasions2():
    tiles = [("aplus-ksg-diya-hand", "Diwali nights"), ("aplus-ksg-velvet-tray", "Festive dressing"),
             ("aplus-ksg-lehenga-wrist", "Wedding mornings"), ("aplus-ksg-haldi-flatlay", "Haldi days")]
    im = Image.new("RGB", (970, 600), CREAM)
    for i, (slug, cap) in enumerate(tiles):
        x, y = (i % 2) * 485, (i // 2) * 300
        t = cover(scene(slug), 481, 296, fy=0.45)
        shade = Image.new("L", t.size); px = shade.load()
        for yy in range(t.height):
            a = max(0, int(215 * (yy - 150) / 146)) if yy > 150 else 0
            for xx in range(t.width): px[xx, yy] = a
        t.paste(Image.new("RGB", t.size, (40, 8, 18)), mask=shade)
        d = ImageDraw.Draw(t)
        d.rectangle((24, 232, 62, 235), fill=GOLD)
        d.text((24, 244), cap, font=font(SERIF_B, 38), fill=CREAM)
        im.paste(t, (x + 2, y + 2))
    save(im, OUT2 / "04-occasions-970x600.jpg")


def size_brand():
    """Brand's own size chart (amazon-assets/bangle-bliss-size-chart.jpg) + its table values in big, phone-readable type."""
    chart = Image.open(ROOT / "amazon-assets" / "bangle-bliss-size-chart.jpg").convert("RGB").resize((600, 600), Image.LANCZOS)
    im = Image.new("RGB", (970, 600), CREAM); im.paste(chart, (0, 0)); d = ImageDraw.Draw(im)
    x0 = 624
    d.text((x0, 34), "FIND YOUR FIT", font=font(SANS_B, 24), fill=GOLD)
    d.text((x0, 66), "Your size", font=font(SERIF_B, 46), fill=MAROON)
    d.rounded_rectangle((x0, 140, 946, 520), 16, fill=MAROON)
    d.text((x0 + 22, 154), "SIZE", font=font(SANS_B, 22), fill=GOLD)
    d.text((x0 + 150, 154), "CM (APPROX.)", font=font(SANS_B, 22), fill=GOLD)
    rows = [("2.2", "5.3 cm", False), ("2.4", "5.7 cm", True), ("2.6", "5.9 cm", True), ("2.8", "6.3 cm", True), ("2.10", "6.6 cm", False)]
    for i, (size, cm, ours) in enumerate(rows):
        y = 190 + i * 66
        if ours: d.rounded_rectangle((x0 + 10, y - 2, 936, y + 56), 10, fill=(120, 30, 48))
        d.text((x0 + 22, y + 2), size, font=font(SERIF_B, 40), fill=CREAM if ours else (200, 170, 170))
        d.text((x0 + 150, y + 6), cm, font=font(SANS_B, 34), fill=GOLD if ours else (200, 170, 170))
    d.text((x0, 540), "Sets come in 2.4, 2.6 and 2.8", font=font(SANS_B, 25), fill=MAROON)
    save(im, OUT2 / "05-size-guide-970x600.jpg")


def main2():
    OUT2.mkdir(parents=True, exist_ok=True)
    hero2(); features2(); occasions2(); size_brand()
    import shutil
    shutil.copy(OUT / "03-colour-wall-970x600.jpg", OUT2 / "03-colour-wall-970x600.jpg")
    print(sorted(p.name for p in OUT2.glob("*.jpg")))
