"""Cut the real 12-bangle stack out of each raw photo (full resolution) -> stb/cutouts/<slug>.png (RGBA, tight crop).
Mask = colour mask (kills the grey rod/wall) AND rembg alpha (clean edges), holes filled."""
import glob, numpy as np, cv2
from pathlib import Path
from PIL import Image, ImageOps
from rembg import remove, new_session
from thread_setup import COLOURS, RAW, find_box
ROOT = Path(__file__).parent
S = new_session("u2net")

def cutout(path):
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    W, H = im.size
    b = find_box(path, pad=0.10)
    x0, y0, x1, y1 = int(W * b[0]), int(H * b[1]), int(W * b[2]), int(H * b[3])
    c = im.crop((x0, y0, x1, y1))
    a = np.asarray(c)
    hsv = cv2.cvtColor(a, cv2.COLOR_RGB2HSV)
    col = ((hsv[:, :, 1] > 70) & (hsv[:, :, 2] > 35)).astype(np.uint8)
    col = cv2.morphologyEx(col, cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(col)
    k = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA])); col = (lab == k).astype(np.uint8)
    # fill holes
    cnts, _ = cv2.findContours(col, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    filled = np.zeros_like(col); cv2.drawContours(filled, cnts, -1, 1, -1)
    rem = np.asarray(remove(c, session=S, alpha_matting=False))[:, :, 3]
    allow = cv2.dilate(filled, np.ones((9, 9), np.uint8))
    alpha = np.where(allow > 0, np.maximum(rem, (filled * 255).astype(np.uint8)), 0).astype(np.uint8)
    # inside the filled body keep fully opaque, soften only the rim
    inner = cv2.erode(filled, np.ones((7, 7), np.uint8))
    alpha = np.where(inner > 0, 255, alpha).astype(np.uint8)
    alpha = cv2.GaussianBlur(alpha, (0, 0), 1.0)
    ys, xs = np.where(alpha > 20)
    box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    out = np.dstack([a, alpha])
    return Image.fromarray(out).crop(box)

if __name__ == "__main__":
    for slug, (idx, *_r) in COLOURS.items():
        im = cutout(RAW[idx]); im.save(ROOT / "stb" / "cutouts" / f"{slug}.png")
        print(slug, im.size)
