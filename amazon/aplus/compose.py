"""Compose Amazon Basic A+ module images (exact pixel sizes) from Magic-generated shots.

Usage: python aplus/compose.py KSG Ruby-Red
Reads  amazon-latest-images/<PRODUCT>/<Colour>/*.jpg  (white-studio, lifestyle, worn-on-hand, macro-detail)
Writes aplus/out/<PRODUCT>/<Colour>/NN-<module>.jpg   (RGB JPEG, <2 MB)

Module sizes are the Basic A+ reference sizes from third-party guides; confirm each slot in
Seller Central > A+ Content Manager before first upload (see aplus/PLAN.md).
No prices, guarantees, returns, superlatives or health claims in any copy (Amazon rejects them).
"""
import sys, json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent.parent
MAROON, GOLD, CREAM, INK = (91, 16, 32), (201, 162, 75), (251, 243, 228), (40, 24, 28)
FONTS = Path("C:/Windows/Fonts")
def font(name, size): return ImageFont.truetype(str(FONTS / name), size)
SERIF, SERIF_B, SANS, SANS_B = "georgia.ttf", "georgiab.ttf", "segoeui.ttf", "segoeuib.ttf"

def find(folder, key):
    hits = sorted(folder.glob(f"*{key}*.jpg"))
    if not hits: raise SystemExit(f"missing shot '{key}' in {folder}")
    return Image.open(hits[0]).convert("RGB")

def cover(img, w, h, fx=0.5, fy=0.5):
    s = max(w / img.width, h / img.height)
    im = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    x = round((im.width - w) * fx); y = round((im.height - h) * fy)
    return im.crop((x, y, x + w, y + h))

def wrap(d, text, f, maxw):
    lines, cur = [], ""
    for word in text.split():
        t = (cur + " " + word).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: lines.append(cur); cur = word
    return lines + [cur]

def text_block(d, xy, text, f, fill, maxw, gap=1.25):
    x, y = xy
    for ln in wrap(d, text, f, maxw):
        d.text((x, y), ln, font=f, fill=fill); y += int(f.size * gap)
    return y

def save(img, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    q = 92
    while True:
        img.save(path, "JPEG", quality=q, optimize=True)
        if path.stat().st_size < 1_900_000 or q < 60: break
        q -= 6

def hero(shot, colour, out):           # STANDARD_HEADER_IMAGE_TEXT / IMAGE_TEXT_OVERLAY, 970x600
    im = cover(shot, 970, 600, fy=0.45)
    # left-to-right maroon fade so large type stays legible on phones
    fade = Image.new("L", im.size); px = fade.load()
    for x in range(im.width):
        a = max(0, int(235 * (1 - x / 560)))
        for y in range(im.height): px[x, y] = a
    im.paste(Image.new("RGB", im.size, MAROON), mask=fade)
    d = ImageDraw.Draw(im)
    d.text((48, 150), "BANGLE BLISS", font=font(SANS_B, 22), fill=GOLD)
    d.rectangle((48, 188, 108, 191), fill=GOLD)
    y = text_block(d, (48, 214), f"{colour.replace('-', ' ')} Kundan Glass Bangles", font(SERIF_B, 54), CREAM, 480, 1.1)
    text_block(d, (48, y + 14), "Set of 4 \u00b7 Faceted glass, kundan stones", font(SANS, 26), CREAM, 480)
    save(im, out)

def four_up(shots, out_dir):           # STANDARD_FOUR_IMAGE_TEXT, 4 x 220x220
    for i, (k, s) in enumerate(shots.items()):
        save(cover(s, 220, 220), out_dir / f"02-four-image-{i+1}-{k}.jpg")

def detail(shot, out):                 # STANDARD_SINGLE_SIDE_IMAGE, 300x300
    save(cover(shot, 300, 300), out)

def size_panel(wrist, colour, out):    # infographic banner 970x600, large type only
    im = Image.new("RGB", (970, 600), CREAM); d = ImageDraw.Draw(im)
    d.text((48, 40), "FIND YOUR FIT", font=font(SANS_B, 22), fill=GOLD)
    d.text((48, 76), "Three sizes, one set of 4", font=font(SERIF_B, 40), fill=MAROON)
    photo = cover(wrist, 360, 400, fy=0.5)
    im.paste(photo, (562, 140)); d.rectangle((562, 140, 922, 540), outline=GOLD, width=3)
    rows = [("2.4", "Slim wrists"), ("2.6", "Average wrists"), ("2.8", "Broader wrists")]
    y = 150
    for size, label in rows:
        d.rounded_rectangle((48, y, 520, y + 100), 14, fill=MAROON)
        d.text((74, y + 14), size, font=font(SERIF_B, 56), fill=GOLD)
        d.text((190, y + 24), label, font=font(SANS_B, 30), fill=CREAM)
        d.text((190, y + 62), "inner diameter, inches", font=font(SANS, 20), fill=CREAM)
        y += 124
    d.text((48, 558), "Check the size chart image in the gallery before ordering.", font=font(SANS, 22), fill=INK)
    save(im, out)

def range_strip(collage, out):         # banner 970x300 colour-range strip
    im = cover(collage, 970, 300, fy=0.5)
    ov = Image.new("RGB", im.size, MAROON); mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rectangle((0, 100, 970, 200), fill=215); im.paste(ov, mask=mask)
    d = ImageDraw.Draw(im); f = font(SERIF_B, 40); t = "Available in 13 colours"
    d.text(((970 - d.textlength(t, font=f)) / 2, 122), t, font=f, fill=CREAM)
    save(im, out)

if __name__ == "__main__":
    product, colour = sys.argv[1], sys.argv[2]
    src = ROOT / "amazon-latest-images" / product / colour
    out = Path(__file__).parent / "out" / product / colour
    life, wrist, macro, studio = (find(src, k) for k in ("lifestyle", "worn-on-hand", "macro-detail", "white-studio"))
    hero(life, colour, out / "01-hero-970x600.jpg")
    four_up({"studio": studio, "wrist": wrist, "macro": macro, "lifestyle": life}, out)
    detail(macro, out / "03-detail-300x300.jpg")
    size_panel(wrist, colour, out / "04-size-970x600.jpg")
    collage = ROOT / "amazon-latest-images" / product / f"00-colour-collage-{product}.jpg"
    if collage.exists(): range_strip(Image.open(collage).convert("RGB"), out / "05-range-970x300.jpg")
    print("wrote", sorted(p.name for p in out.glob("*.jpg")))
