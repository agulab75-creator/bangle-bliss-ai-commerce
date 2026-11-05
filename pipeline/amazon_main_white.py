"""Amazon needs a PURE WHITE (255,255,255) main-image background. Take each live main image in the combined sheet,
flood-fill the outside background to pure white, save as a square JPEG, upload to Shopify Files (not attached to a
product) and write the new plain URL into Main Image URL (col 31). Result map: amazon-main-white/map.json.
Usage: python amazon_main_white.py [sheet-in] [sheet-out]"""
import json, io, sys
from pathlib import Path
import numpy as np, requests, openpyxl
from PIL import Image
from scipy import ndimage
import execution_agent as e

ROOT = Path(__file__).parent
OUT = ROOT / "amazon-main-white"
MAP = OUT / "map.json"
SRC = ROOT / "amazon from claude" / "amazon-all-3-products-combined-v3.xlsm"
DST = ROOT / "amazon from claude" / "amazon-all-3-products-combined-v4.xlsm"
PARENT_FALLBACK = {"KMS2": "kundan-stone-glass-ivory-multi-white-studio-v3.png"}


def whiten(im):
    a = np.asarray(im.convert("RGB")).astype(np.int16)
    light = a.min(axis=2) >= 205
    lab, n = ndimage.label(light)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(edge))
    bg = ndimage.binary_closing(bg, iterations=1) | bg
    a[bg] = 255
    out = Image.fromarray(a.astype(np.uint8))
    s = max(out.size)
    if s < 1200:
        out = out.resize((1200, 1200 * out.height // out.width), Image.LANCZOS)
    if np.asarray(out).min(axis=2)[[0, -1], :].min() < 255 or np.asarray(out).min(axis=2)[:, [0, -1]].min() < 255:
        pad = Image.new("RGB", (round(out.width * 1.16), round(out.height * 1.16)), (255, 255, 255))
        pad.paste(out, ((pad.width - out.width) // 2, (pad.height - out.height) // 2))
        out = pad
    sq = Image.new("RGB", (max(out.size),) * 2, (255, 255, 255))
    sq.paste(out, ((sq.width - out.width) // 2, (sq.height - out.height) // 2))
    return sq


def fetch(u):
    for i in range(5):
        try:
            return requests.get(u, timeout=60).content
        except requests.exceptions.RequestException:
            import time; time.sleep(2 * (i + 1))
    raise RuntimeError("fetch failed " + u)


def main():
    OUT.mkdir(exist_ok=True)
    m = json.loads(MAP.read_text()) if MAP.exists() else {}
    wb = openpyxl.load_workbook(SRC, keep_vba=True)
    ws = wb["Template"]
    for r in range(8, ws.max_row + 1):
        sku = ws.cell(r, 1).value
        if not sku:
            continue
        u = (ws.cell(r, 31).value or "").split("?")[0]
        if not u:
            continue
        if ws.cell(r, 4).value == "Parent" and sku.startswith("KMS2"):
            u = u.rsplit("/", 1)[0] + "/" + PARENT_FALLBACK["KMS2"]
        key = u.rsplit("/", 1)[1]
        if key not in m:
            im = Image.open(io.BytesIO(fetch(u)))
            w = whiten(im)
            name = "amz-main-" + key.rsplit(".", 1)[0] + ".jpg"
            p = OUT / name
            w.save(p, "JPEG", quality=95)
            fid = e.upload_file_to_shopify(p)
            gid = f"gid://shopify/MediaImage/{fid}"
            url = e.gql('query($id:ID!){node(id:$id){... on MediaImage{image{url}}}}', {"id": gid})["node"]["image"]["url"].split("?")[0]
            m[key] = {"id": gid, "url": url}
            MAP.write_text(json.dumps(m, indent=1))
            print("done", key)
        ws.cell(r, 31).value = m[key]["url"]
    wb.save(DST)
    print("saved", DST)


if __name__ == "__main__":
    main()
