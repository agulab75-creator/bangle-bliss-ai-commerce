"""Estimate how many bangles an upright side-by-side stack shows: width of the stack / dominant band period (FFT of the column gradient profile)."""
import numpy as np, cv2
from PIL import Image

def stack_box(rgb, h0=None):
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    if h0 is None:
        m = (hsv[:, :, 1] > 90) & (hsv[:, :, 2] > 40)
        if m.sum() < 1000: return None
        h0 = np.bincount(hsv[:, :, 0][m], minlength=180).argmax()
    d = np.minimum(np.abs(hsv[:, :, 0].astype(int) - h0), 180 - np.abs(hsv[:, :, 0].astype(int) - h0))
    mask = ((d < 9) & (hsv[:, :, 1] > 90) & (hsv[:, :, 2] > 40)).astype(np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(mask)
    k = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    x, y, w, h, _ = st[k]
    return x, y, w, h

def count(path_or_img, hue=None):
    im = Image.open(path_or_img).convert("RGB") if not isinstance(path_or_img, Image.Image) else path_or_img.convert("RGB")
    rgb = np.asarray(im)
    b = stack_box(rgb, hue)
    if b is None: return None
    x, y, w, h = b
    reg = rgb[y + int(h * 0.25): y + int(h * 0.75), x: x + w]
    g = cv2.cvtColor(reg, cv2.COLOR_RGB2GRAY).astype(np.float32)
    g = cv2.GaussianBlur(g, (0, 0), 1.2)
    gx = np.abs(cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3))
    prof = np.median(gx, axis=0)
    prof = prof - prof.mean()
    prof = prof * np.hanning(len(prof))
    N = 1 << 14
    F = np.abs(np.fft.rfft(prof, N))
    freqs = np.fft.rfftfreq(N)            # cycles per pixel
    cyc = freqs * w                        # cycles across the stack width = bangle count
    sel = (cyc > 6) & (cyc < 20)
    c = cyc[sel][np.argmax(F[sel])]
    return float(c), (x, y, w, h)

if __name__ == "__main__":
    import sys
    for p in sys.argv[1:]:
        r = count(p); print(p, None if r is None else round(r[0], 1))


def hue_of(cutout_path):
    im = Image.open(cutout_path).convert("RGBA"); b = Image.new("RGB", im.size, (255, 255, 255)); b.paste(im, mask=im.split()[3])
    hsv = cv2.cvtColor(np.asarray(b), cv2.COLOR_RGB2HSV); m = (hsv[:, :, 1] > 90) & (hsv[:, :, 2] > 40)
    return int(np.bincount(hsv[:, :, 0][m], minlength=180).argmax())


def count_any(path_or_img, hue):
    """Rotation-tolerant count: try angles, pick the one where the band pattern is most periodic; count = stack length along that direction / period."""
    im = Image.open(path_or_img).convert("RGB") if not isinstance(path_or_img, Image.Image) else path_or_img.convert("RGB")
    rgb = np.asarray(im)
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    d = np.minimum(np.abs(hsv[:, :, 0].astype(int) - hue), 180 - np.abs(hsv[:, :, 0].astype(int) - hue))
    mask = ((d < 8) & (hsv[:, :, 1] > 100) & (hsv[:, :, 2] > 40)).astype(np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(mask)
    if n < 2: return None
    k = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA])); m = (lab == k).astype(np.uint8)
    x, y, w, h, _ = st[k]
    pad = int(0.25 * max(w, h))
    X0, Y0 = max(0, x - pad), max(0, y - pad)
    g = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY).astype(np.float32)[Y0:y + h + pad, X0:x + w + pad]
    mm = m[Y0:y + h + pad, X0:x + w + pad]
    best = None
    cx, cy = g.shape[1] / 2, g.shape[0] / 2
    for ang in range(0, 180, 4):
        M = cv2.getRotationMatrix2D((cx, cy), ang, 1.0)
        gr = cv2.warpAffine(g, M, (g.shape[1], g.shape[0]), flags=cv2.INTER_LINEAR)
        mr = cv2.warpAffine(mm, M, (g.shape[1], g.shape[0]), flags=cv2.INTER_NEAREST)
        ys, xs = np.where(mr > 0)
        if len(xs) < 2000: continue
        x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
        L = x1 - x0 + 1
        if L < 60: continue
        r0, r1 = y0 + int((y1 - y0) * 0.3), y0 + int((y1 - y0) * 0.7)
        reg = cv2.GaussianBlur(gr[r0:r1, x0:x1 + 1], (0, 0), 1.2)
        inside = (mr[r0:r1, x0:x1 + 1] > 0).mean(0) > 0.6
        gx = np.abs(cv2.Sobel(reg, cv2.CV_32F, 1, 0, ksize=3))
        prof = np.median(gx, axis=0); prof = (prof - prof.mean()) * np.hanning(len(prof))
        N = 1 << 14; F = np.abs(np.fft.rfft(prof, N)); cyc = np.fft.rfftfreq(N) * L
        sel = (cyc > 6) & (cyc < 22)
        if not sel.any(): continue
        j = np.argmax(F[sel]); score = F[sel][j] / (F[(cyc > 1)].sum() + 1e-6)
        if best is None or score > best[0]: best = (score, float(cyc[sel][j]), ang)
    return None if best is None else (best[1], best[0], best[2])


def _vert_count(rgb, hue, h0=None):
    """Vertical-band count on an RGB array using the thread hue mask; returns (count, score, bbox_w, bbox_h) or None."""
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    d = np.minimum(np.abs(hsv[:, :, 0].astype(int) - hue), 180 - np.abs(hsv[:, :, 0].astype(int) - hue))
    mask = ((d < 9) & (hsv[:, :, 1] > 90) & (hsv[:, :, 2] > 40)).astype(np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(mask)
    if n < 2: return None
    k = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA])); x, y, w, h, _ = st[k]
    if w < 80 or h < 80: return None
    reg = rgb[y + int(h * 0.25): y + int(h * 0.75), x: x + w]
    g = cv2.GaussianBlur(cv2.cvtColor(reg, cv2.COLOR_RGB2GRAY).astype(np.float32), (0, 0), 1.2)
    prof = np.median(np.abs(cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3)), axis=0)
    prof = (prof - prof.mean()) * np.hanning(len(prof))
    N = 1 << 14; F = np.abs(np.fft.rfft(prof, N)); cyc = np.fft.rfftfreq(N) * w
    sel = (cyc > 6) & (cyc < 20)
    j = np.argmax(F[sel]); return float(cyc[sel][j]), float(F[sel][j] / (F[cyc > 1].sum() + 1e-6)), w, h

def count_dir(path_or_img, hue, tilts=(-16, -12, -8, -4, 0, 4, 8, 12, 16)):
    """Count for a stack that may be upright (vertical bands) or lying (horizontal bands), tilted up to ~16 degrees. Returns (count, score, orientation, tilt)."""
    im = Image.open(path_or_img).convert("RGB") if not isinstance(path_or_img, Image.Image) else path_or_img.convert("RGB")
    base = np.asarray(im); best = None
    for trans in (False, True):
        a0 = np.ascontiguousarray(np.rot90(base)) if trans else base
        for t in tilts:
            M = cv2.getRotationMatrix2D((a0.shape[1] / 2, a0.shape[0] / 2), t, 1.0)
            a = cv2.warpAffine(a0, M, (a0.shape[1], a0.shape[0]), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
            r = _vert_count(a, hue)
            if r is None: continue
            c, s, w, h = r
            if w > h * 1.1: continue                        # a stack seen from the side is taller than it is long
            if best is None or s > best[1]: best = (c, s, "horizontal bands" if trans else "vertical bands", t)
    return best
