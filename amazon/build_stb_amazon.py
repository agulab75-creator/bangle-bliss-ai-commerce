"""Amazon flat file for Silk Thread Bangles (STB): 1 parent + 33 children (11 colours x sizes 2.4/2.6/2.8). Rows are CLONED from the known-good GVK2 rows in
the combined v4 sheet (amazon-scale rule); only product fields are overridden. Needs stb/shopify.json (photo URLs). Output: stb/amazon-silk-thread-bangles.xlsm"""
import json, re
from copy import copy
from pathlib import Path
import openpyxl
import build_combined_amazon as b
from thread_setup import COLOURS

ROOT = Path(__file__).parent
BASE = ROOT / "amazon from claude" / "amazon-all-3-products-combined-v4.xlsm"
OUT = ROOT / "stb" / "amazon-silk-thread-bangles.xlsm"
ST = json.loads((ROOT / "stb" / "shopify.json").read_text())
SIZES = ["2.4", "2.6", "2.8"]
ORDER = "royal-blue crimson-red mustard-yellow coral-pink turquoise parrot-green emerald-green rani-pink wine-maroon orange golden".split()
PARENT = "STB"
PRICE, MRP, QTY = 279, 1000, 10
SIZE_CHART = b.SIZE_CHART
# plain search colour words per shade (Amazon free-text keywords only)
KW_COL = {"royal-blue": "blue navy", "crimson-red": "red", "mustard-yellow": "yellow golden", "coral-pink": "pink peach orange", "turquoise": "blue aqua teal",
          "parrot-green": "green lime", "emerald-green": "green dark", "rani-pink": "pink hot magenta", "wine-maroon": "maroon purple red", "orange": "orange saffron", "golden": "gold champagne beige"}
PAIR = {"royal-blue": "gold, ivory, mustard and pastel outfits", "crimson-red": "cream, gold and bridal outfits", "mustard-yellow": "royal blue, green, maroon and white outfits",
        "coral-pink": "ivory, cream and pastel outfits", "turquoise": "peach, white and pastel outfits", "parrot-green": "yellow, red and white festive outfits",
        "emerald-green": "red, gold and cream sarees and lehengas", "rani-pink": "cream, gold and white outfits", "wine-maroon": "gold, cream and ivory outfits",
        "orange": "green, white and festive earthy outfits", "golden": "green, maroon, white and ivory outfits"}
BASE_WORDS = ("churi chudi chudiyan choodi kangan bangdi chooda bridal bridesmaid ladies wedding sangeet mehendi haldi karwa chauth karva diwali navratri garba teej "
              "saree lehenga ethnic traditional indian jewellery gift handmade stackable lightweight")


def kw(title, colour_slug):
    tw = set(re.findall(r"[a-z0-9\-]+", title.lower()))
    out, seen, size = [], set(), 0
    for w in (KW_COL.get(colour_slug, "") + " " + BASE_WORDS).split():
        if w in tw or w in seen: continue
        add = len(w.encode()) + (1 if out else 0)
        if size + add > 249: continue
        seen.add(w); out.append(w); size += add
    return " ".join(out)


def main():
    wb = openpyxl.load_workbook(BASE, keep_vba=True); ws = wb["Template"]; mc = ws.max_column
    prow = next(r for r in range(8, ws.max_row + 1) if ws.cell(r, 1).value == "GVK2")
    crow = next(r for r in range(8, ws.max_row + 1) if ws.cell(r, 1).value == "GVK2-LIM-24")
    pv = [ws.cell(prow, c).value for c in range(1, mc + 1)]; cv = [ws.cell(crow, c).value for c in range(1, mc + 1)]
    ps = [copy(ws.cell(prow, c)._style) for c in range(1, mc + 1)]; cs = [copy(ws.cell(crow, c)._style) for c in range(1, mc + 1)]
    for r in range(8, ws.max_row + 1):
        for c in range(1, mc + 1): ws.cell(r, c).value = None
    parent_title = "Thread Bangles Set for Women, 12 Silk Thread Bangles with Gold Beads"
    colour_names = [COLOURS[s][1] for s in ORDER]
    colour_list = ", ".join(n.lower() for n in colour_names)
    design = "Each bangle is wrapped by hand in soft silk thread and finished with small antique-gold beads, for a rich traditional look."
    desc_tail = ("Wear the full dozen as a matching stack or mix with other colours, kadas and gold bangles. A good choice for weddings, bridal and bridesmaid looks, "
                 "Karwa Chauth, Diwali, Navratri, Teej, mehendi, haldi and sangeet functions, parties and everyday ethnic wear with sarees, lehengas, salwar suits and kurtis. "
                 "It also makes a thoughtful gift for wife, mother, sister, bhabhi or friends. Available in sizes 2.4, 2.6 and 2.8 - check the size chart image to choose your fit. "
                 "Keep away from water and perfume, and store in the box provided.")
    size_txt = ("SIZES 2.4, 2.6 AND 2.8: Choose your size from the size chart image. If you are between sizes, choose the larger one. "
                "Keep the bangles away from water and perfume and store them in the box provided.")
    media = ST["media"]; url = lambda s, k: media[f"{s}/{k}"]["url"]
    rows = [("parent", None, None)] + [("child", s, z) for s in ORDER for z in SIZES]
    out_r = 8
    for kind, slug, size in rows:
        vals = pv if kind == "parent" else cv; sty = ps if kind == "parent" else cs
        for c in range(1, mc + 1):
            ws.cell(out_r, c).value = vals[c - 1]; ws.cell(out_r, c)._style = copy(sty[c - 1])
        sku = PARENT if kind == "parent" else f"{PARENT}-{COLOURS[slug][2]}-{size.replace('.', '')}"
        ws.cell(out_r, b.C_SKU).value = sku
        ws.cell(out_r, b.C_PARENT_SKU).value = None if kind == "parent" else PARENT
        ws.cell(out_r, 158).value = sku                                  # Part Number
        ws.cell(out_r, 159).value = "Silk Thread Bangles"                # Collection Name
        ws.cell(out_r, 53).value = "Silk"                                # Material
        ws.cell(out_r, 61).value = 12                                    # Number of Items
        # stone block (91-100: setting type, stone id/type/creation/treatment/clarity/colour/cut/shape) stays as cloned from the GVK2 base row: Amazon flags it when blank (owner 2026-10-19)
        ws.cell(out_r, 229).value = 0.3                                  # Item Width (cm) = bangle band width
        ws.cell(out_r, b.C_THICK).value = 0.12; ws.cell(out_r, b.C_THICK_UNIT).value = "Inches"
        if kind == "parent":
            title = parent_title + ", Churi Chudi for Wedding & Party"
            ws.cell(out_r, b.C_DESC).value = f"Bangle Bliss Silk Thread Bangles for women and girls in 11 colours, a set of 12 silk thread bangles with gold beads. {design} " + desc_tail
            ws.cell(out_r, b.C_B1).value = "FULL DOZEN, GREAT VALUE: each box has 12 slim silk thread bangles in one colour, a complete matching stack for the price of a single kada."
            ws.cell(out_r, b.C_B3).value = f"11 COLOURS AVAILABLE: {colour_list}."
            ws.cell(out_r, b.C_KEY).value = kw(title, "")
            for col in range(32, 40): ws.cell(out_r, col).value = None
            ws.cell(out_r, 31).value = url(ORDER[0], "1-hero")
        else:
            cname = COLOURS[slug][1]
            title = f"{parent_title}, {cname}, Churi Chudi for Wedding"
            ws.cell(out_r, b.C_DESC).value = f"Bangle Bliss Silk Thread Bangles for women and girls in {cname}, a set of 12 silk thread bangles with gold beads. {design} " + desc_tail
            ws.cell(out_r, b.C_B1).value = f"FULL DOZEN, GREAT VALUE: each box has 12 slim {cname.lower()} silk thread bangles, a complete matching stack for the price of a single kada."
            ws.cell(out_r, b.C_B3).value = f"{cname.upper()}: a rich {cname.lower()} thread bangle set that pairs well with {PAIR[slug]}. 11 colours available."
            ws.cell(out_r, b.C_KEY).value = kw(title, slug)
            ws.cell(out_r, b.C_COLOR).value = cname
            ws.cell(out_r, b.C_SETNAME).value = f"Size {size}"
            ws.cell(out_r, b.C_SIZE).value = size
            ws.cell(out_r, 201).value = float(size)
            for col, key in ((31, "1-hero"), (32, "2-flat"), (33, "4-worn-table"), (34, "5-worn-rose")): ws.cell(out_r, col).value = url(slug, key)
            ws.cell(out_r, 35).value = SIZE_CHART
            ws.cell(out_r, 36).value = url(slug, "3-close"); ws.cell(out_r, 37).value = url(slug, "6-macro"); ws.cell(out_r, 38).value = None; ws.cell(out_r, 39).value = None
            ws.cell(out_r, 285).value = PRICE; ws.cell(out_r, 286).value = MRP; ws.cell(out_r, 281).value = 0 if size == "2.8" else QTY
        ws.cell(out_r, b.C_NAME).value = title
        ws.cell(out_r, b.C_B2).value = "SILK THREAD AND GOLD BEADS: Each bangle is wrapped in soft silk thread and finished with small antique-gold beads for a rich, traditional look."
        ws.cell(out_r, b.C_B4).value = "FOR EVERY OCCASION: wear for weddings, Karwa Chauth, Diwali, Navratri, Teej, mehendi, sangeet and parties. A thoughtful gift for wife, mother, sister or friends."
        ws.cell(out_r, b.C_B5).value = size_txt
        out_r += 1
    last = out_r - 1
    for dv in ws.data_validations.dataValidation:
        new = []
        for rng in str(dv.sqref).split():
            m = re.match(r"([A-Z]+)(\d+):([A-Z]+)(\d+)$", rng)
            if m and 70 <= int(m.group(4)) < last: rng = f"{m.group(1)}{m.group(2)}:{m.group(3)}{last}"
            new.append(rng)
        dv.sqref = openpyxl.worksheet.cell_range.MultiCellRange(" ".join(new))
    OUT.parent.mkdir(exist_ok=True); wb.save(OUT); print("saved", OUT, "rows 8..", last)
    # checks
    pairs = set(); bad = []
    for r in range(9, last + 1):
        pr = (ws.cell(r, b.C_COLOR).value, ws.cell(r, b.C_SETNAME).value)
        if pr in pairs: bad.append(pr)
        pairs.add(pr)
        k = ws.cell(r, b.C_KEY).value or ""
        if len(k.encode()) > 249 or len(ws.cell(r, b.C_NAME).value) > 200: bad.append(("len", r))
    print("children", last - 8, "unique (colour,set) pairs", len(pairs), "problems", bad)
    print(ws.cell(9, b.C_NAME).value, "|", ws.cell(9, b.C_KEY).value, len(ws.cell(9, b.C_KEY).value.encode()))


if __name__ == "__main__":
    main()
