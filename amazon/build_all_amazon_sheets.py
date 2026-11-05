"""
build_all_amazon_sheets.py
Generates official Amazon Flat-File listing spreadsheets (.xlsm) for all Bangle Bliss raw 01 products.
Conforms strictly to:
- amazon-scale rules (COLOR/SET_NAME variation theme, 1 parent, child per size, master template macros/validations preserved)
- amazon-seo rules (front-loaded high-CTR titles, no size in title, no prohibited words like 'Festive Wear', 5 luxury benefit-driven bullets, generic keywords <= 249 bytes UTF-8)
- User explicit directive: (dont put image links) -> Image columns 31-39 left completely empty.
- Outputs BOTH:
  1. amazon-sheets/by-product/ (37 individual product spreadsheets, matching Shopify catalog & review gallery 1-to-1)
  2. amazon-sheets/by-design/ (27 design-family spreadsheets, grouping color variants under 1 parent)
"""

import json
import re
import shutil
from copy import copy
from pathlib import Path
import openpyxl

import raw01_metadata as rm

ROOT = Path(__file__).resolve().parent
BASE_TEMPLATE = ROOT / "amazon from claude" / "amazon-all-3-products-combined-v4.xlsm"

OUT_DIR = ROOT / "amazon-sheets"
OUT_BY_PRODUCT = OUT_DIR / "by-product"
OUT_BY_DESIGN = OUT_DIR / "by-design"

OUT_BY_PRODUCT.mkdir(parents=True, exist_ok=True)
OUT_BY_DESIGN.mkdir(parents=True, exist_ok=True)

SIZES = ["2.4", "2.6", "2.8"]

# Column indices in 'Template' sheet (1-based)
C_SKU = 1
C_TYPE = 4          # Parent / Child
C_PARENT_SKU = 5    # None for parent
C_THEME = 6         # COLOR/SET_NAME
C_NAME = 7          # Item Name (Title)
C_BRAND = 9         # Brand Name
C_MFG = 27          # Manufacturer
C_MAIN = 31         # Main Image URL (EMPTY)
# Cols 32-39: Other Image URLs (EMPTY)
C_DESC = 41         # Product Description
C_B1 = 42           # Bullet 1
C_B2 = 43           # Bullet 2
C_B3 = 44           # Bullet 3
C_B4 = 45           # Bullet 4
C_B5 = 46           # Bullet 5
C_KEY = 47          # Generic Keywords
C_MAT = 53          # Material
C_COUNT = 61        # Number of Items
C_COLOR = 64        # Color
C_SIZE = 65         # Size
C_SETTING = 91      # Setting Type
C_PART = 158        # Part Number (SKU)
C_COLL = 159        # Collection Name
C_INSIDE = 201      # Inside Diameter Decimal Value
C_THICK = 213       # Item Thickness Decimal Value
C_THICK_UNIT = 215  # Item Thickness Unit
C_SETNAME = 240     # Set Name ('Size 2.4', etc.)
C_QTY = 281         # Quantity
C_PRICE = 285       # Your Price INR
C_MRP = 286         # Maximum Retail Price INR

BASE_KEYWORDS = (
    "churi chudi chudiyan choodi kangan kada bangdi chooda bridal bridesmaid ladies wedding sangeet mehendi "
    "haldi karwa chauth karva diwali navratri garba teej rakhi party saree lehenga ethnic traditional "
    "indian jewellery gift wife mother sister bhabhi return"
)

def build_keywords(title: str, color_text: str, extra_terms: str = "") -> str:
    title_words = set(re.findall(r"[a-z0-9\-]+", title.lower()))
    candidate_tokens = []
    
    # Color-specific tokens
    if color_text:
        col_clean = re.sub(r"[^a-zA-Z\s]", " ", color_text).lower()
        for w in col_clean.split():
            candidate_tokens.append(w)
            
    # Extra terms (pearl, kundan, etc.)
    if extra_terms:
        for w in extra_terms.lower().split():
            candidate_tokens.append(w)
            
    # Base tokens
    for w in BASE_KEYWORDS.split():
        candidate_tokens.append(w)
        
    out = []
    seen = set()
    size = 0
    for w in candidate_tokens:
        if not w or w in title_words or w in seen:
            continue
        add = len(w.encode("utf-8")) + (1 if out else 0)
        if size + add > 249:
            continue
        seen.add(w)
        out.append(w)
        size += add
    return " ".join(out)

def get_mrp(price_str: str) -> int:
    try:
        p = float(price_str)
    except Exception:
        p = 1299.0
    if p <= 999:
        return 1999
    elif p <= 1299:
        return 2499
    elif p <= 1499:
        return 2999
    elif p <= 1699:
        return 3499
    else:
        return int(p * 2)

def derive_material(metal_str: str) -> str:
    m = metal_str.lower()
    if "silver" in m or "rhodium" in m:
        return "Silver Plated"
    elif "brass" in m:
        return "Brass"
    elif "bronze" in m:
        return "Bronze"
    elif "gold" in m:
        return "Gold Plated"
    elif "glass" in m:
        return "Glass"
    return "Brass"

def clean_title(title: str) -> str:
    t = title.replace("—", "-").replace("–", "-")
    t = re.sub(r"\bFestive Wear\b", "Festive Celebrations", t, flags=re.IGNORECASE)
    # Ensure no size pattern like 'Size 2.4' in title
    t = re.sub(r"\bSize\s+[0-9\.]+\b", "", t, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", t).strip()

def build_parent_title(item: dict) -> str:
    dname = item["design_name"]
    itype = item["item_type"]
    return clean_title(f"Bangle Bliss {dname} Bangles for Women, {itype}, Chudi for Wedding & Party")

def build_child_title(item: dict, variant_color: str) -> str:
    dname = item["design_name"]
    itype = item["item_type"]
    return clean_title(f"Bangle Bliss {dname} Bangles for Women, {itype}, {variant_color}, Chudi for Wedding & Party")

def build_description(item: dict, variant_color: str = None) -> str:
    stitle = item["shopify_title"]
    look = item.get("look", "")
    dexact = item.get("design_exact", "")
    color_note = f"in {variant_color}" if variant_color else ""
    desc = (
        f"Bangle Bliss presents {stitle} {color_note}, an exquisite addition to luxury Indian traditional jewellery. "
        f"{look}. {dexact} Meticulously handcrafted for brides, bridesmaids, and festive occasions. "
        f"Wear this set as a standalone statement on one wrist, or stack with traditional kadas for an opulent bridal aesthetic. "
        f"Coordinates beautifully with Kanjivaram silk sarees, Banarasi lehengas, Anarkali suits, and festive fusion ensembles "
        f"for weddings, Diwali, Karwa Chauth, Navratri, Pooja, and sangeet celebrations. "
        f"Makes a cherished luxury gift for wife, mother, sister, or friends. "
        f"Finished with smooth, skin-friendly inner edges for comfortable all-day wear. "
        f"Available in sizes 2.4, 2.6 and 2.8. To preserve finish, keep away from water, perfumes, and sprays."
    )
    return desc.strip()

def build_bullets(item: dict, variant_color: str = None) -> list[str]:
    itype = item["item_type"]
    count = item["count"]
    color_str = f" in {variant_color}" if variant_color else ""
    metal = item.get("metal", "Gold Plated")
    look = item.get("look", "")
    
    b1 = f"{itype.upper()}: Each box contains {count} beautifully crafted bangles{color_str}, designed to be worn together as an opulent matching stack or paired with kadas."
    b2 = f"EXQUISITE HANDCRAFTED DESIGN: {look}. Handcrafted with high-precision detailing in a rich {metal} finish that radiates festive brilliance."
    b3 = f"PREMIUM QUALITY & COMFORT: Handcrafted from high-grade skin-friendly jewellery alloy and brass with smooth, snag-free inner rims ensuring comfortable all-day wear."
    b4 = f"PERFECT FOR WEDDINGS & FESTIVALS: Ideal for brides, bridesmaids, Karwa Chauth, Diwali, Navratri, Teej, mehendi, haldi, and sangeet. A thoughtful gift for wife, mother, or sister."
    b5 = f"AVAILABLE IN SIZES 2.4, 2.6 & 2.8: Refer to the size options to choose your fit (2.4 = Small, 2.6 = Medium, 2.8 = Large). Store in an airtight pouch away from water and perfume."
    return [b1, b2, b3, b4, b5]

EXCLUDED_IDS = {
    "raw01-01-broad-kada-silver",
    "raw01-01-broad-kada-gold",
    "raw01-07-dense-ghungroo-kada-bright-gold",
    "raw01-07-dense-ghungroo-kada-antique-brass",
    "raw01-19-pearl-crystal-tassels-gold-white",
    "raw01-21-multicolor-crystal-teardrop-drops",
}

def main():
    print("=" * 65)
    print("Building Amazon Flat Sheets for All Active Raw 01 Products")
    print("Pricing: Rs. 999 | MRP: Rs. 1999 | Quantity: 10 per SKU")
    print("=" * 65)
    
    # Clean previous sheets so excluded items don't linger
    for old_file in OUT_BY_PRODUCT.glob("*.xlsm"):
        old_file.unlink()
    for old_file in OUT_BY_DESIGN.glob("*.xlsm"):
        old_file.unlink()
        
    # Load base template
    print(f"Loading master base template: {BASE_TEMPLATE.name}...")
    wb_base = openpyxl.load_workbook(BASE_TEMPLATE, keep_vba=True)
    ws_base = wb_base["Template"]
    mc = ws_base.max_column
    
    prow = next(r for r in range(8, ws_base.max_row + 1) if ws_base.cell(r, 1).value == "GVK2")
    crow = next(r for r in range(8, ws_base.max_row + 1) if ws_base.cell(r, 1).value == "GVK2-LIM-24")
    
    pv = [ws_base.cell(prow, c).value for c in range(1, mc + 1)]
    cv = [ws_base.cell(crow, c).value for c in range(1, mc + 1)]
    ps = [copy(ws_base.cell(prow, c)._style) for c in range(1, mc + 1)]
    cs = [copy(ws_base.cell(crow, c)._style) for c in range(1, mc + 1)]
    
    active_items = [(idx, item) for idx, item in enumerate(rm.METADATA, 1) if item["id"] not in EXCLUDED_IDS]
    print(f"Active Products: {len(active_items)} of {len(rm.METADATA)} (6 excluded)")
    
    PRICE = 999
    MRP = 1999
    QTY = 10
    
    # -------------------------------------------------------------
    # 1. BUILD INDIVIDUAL PRODUCT SHEETS (31 active products)
    # -------------------------------------------------------------
    print(f"\nGenerating {len(active_items)} Individual Product Spreadsheets in {OUT_BY_PRODUCT.name}...")
    for idx, item in active_items:
        pid = item["id"]
        var = item["variation"]
        material = derive_material(item.get("metal", "Gold Plated"))
        count = item["count"]
        
        num_str = f"{idx:02d}"
        parent_sku = f"BB-RAW01-{num_str}"
        
        wb = openpyxl.load_workbook(BASE_TEMPLATE, keep_vba=True)
        ws = wb["Template"]
        
        for r in range(8, ws.max_row + 1):
            for c in range(1, mc + 1):
                ws.cell(r, c).value = None
                
        # Row 8: Parent Row
        out_r = 8
        for c in range(1, mc + 1):
            ws.cell(out_r, c).value = pv[c - 1]
            ws.cell(out_r, c)._style = copy(ps[c - 1])
            
        p_title = build_parent_title(item)
        p_desc = build_description(item)
        p_bullets = build_bullets(item)
        p_kw = build_keywords(p_title, var, item.get("look", ""))
        
        ws.cell(out_r, C_SKU).value = parent_sku
        ws.cell(out_r, C_TYPE).value = "Parent"
        ws.cell(out_r, C_PARENT_SKU).value = None
        ws.cell(out_r, C_THEME).value = "COLOR/SET_NAME"
        ws.cell(out_r, C_NAME).value = p_title
        ws.cell(out_r, C_DESC).value = p_desc
        ws.cell(out_r, C_B1).value = p_bullets[0]
        ws.cell(out_r, C_B2).value = p_bullets[1]
        ws.cell(out_r, C_B3).value = p_bullets[2]
        ws.cell(out_r, C_B4).value = p_bullets[3]
        ws.cell(out_r, C_B5).value = p_bullets[4]
        ws.cell(out_r, C_KEY).value = p_kw
        ws.cell(out_r, C_MAT).value = material
        ws.cell(out_r, C_COUNT).value = count
        ws.cell(out_r, C_COLOR).value = None
        ws.cell(out_r, C_SIZE).value = None
        ws.cell(out_r, C_PART).value = parent_sku
        ws.cell(out_r, C_COLL).value = "Bangle Bliss Luxury Indian Jewellery"
        ws.cell(out_r, C_INSIDE).value = None
        ws.cell(out_r, C_SETNAME).value = None
        ws.cell(out_r, C_QTY).value = None
        ws.cell(out_r, C_PRICE).value = None
        ws.cell(out_r, C_MRP).value = None
        for c in range(31, 40):
            ws.cell(out_r, c).value = None
            
        # Rows 9, 10, 11: Child Rows for sizes 2.4, 2.6, 2.8
        for sz in SIZES:
            out_r += 1
            for c in range(1, mc + 1):
                ws.cell(out_r, c).value = cv[c - 1]
                ws.cell(out_r, c)._style = copy(cs[c - 1])
                
            c_sku = f"{parent_sku}-{sz.replace('.', '')}"
            c_title = build_child_title(item, var)
            c_desc = build_description(item, var)
            c_bullets = build_bullets(item, var)
            c_kw = build_keywords(c_title, var, item.get("look", ""))
            
            ws.cell(out_r, C_SKU).value = c_sku
            ws.cell(out_r, C_TYPE).value = "Child"
            ws.cell(out_r, C_PARENT_SKU).value = parent_sku
            ws.cell(out_r, C_THEME).value = "COLOR/SET_NAME"
            ws.cell(out_r, C_NAME).value = c_title
            ws.cell(out_r, C_DESC).value = c_desc
            ws.cell(out_r, C_B1).value = c_bullets[0]
            ws.cell(out_r, C_B2).value = c_bullets[1]
            ws.cell(out_r, C_B3).value = c_bullets[2]
            ws.cell(out_r, C_B4).value = c_bullets[3]
            ws.cell(out_r, C_B5).value = c_bullets[4]
            ws.cell(out_r, C_KEY).value = c_kw
            ws.cell(out_r, C_MAT).value = material
            ws.cell(out_r, C_COUNT).value = count
            ws.cell(out_r, C_COLOR).value = var
            ws.cell(out_r, C_SIZE).value = sz
            ws.cell(out_r, C_PART).value = c_sku
            ws.cell(out_r, C_COLL).value = "Bangle Bliss Luxury Indian Jewellery"
            ws.cell(out_r, C_INSIDE).value = float(sz)
            ws.cell(out_r, C_THICK).value = 0.4
            ws.cell(out_r, C_THICK_UNIT).value = "Inches"
            ws.cell(out_r, C_SETNAME).value = f"Size {sz}"
            ws.cell(out_r, C_QTY).value = QTY
            ws.cell(out_r, C_PRICE).value = PRICE
            ws.cell(out_r, C_MRP).value = MRP
            for c in range(31, 40):
                ws.cell(out_r, c).value = None

        if ws.max_row > out_r:
            ws.delete_rows(out_r + 1, ws.max_row - out_r)

        filename = f"{num_str}_{pid}.xlsm"
        out_file = OUT_BY_PRODUCT / filename
        wb.save(out_file)
        print(f"  [{num_str}] Saved {filename} ({out_r - 7} rows, Price: Rs {PRICE}, Qty: {QTY})")

    # -------------------------------------------------------------
    # 2. BUILD DESIGN-FAMILY SHEETS (Active designs)
    # -------------------------------------------------------------
    print(f"\nGenerating Design-Family Spreadsheets in {OUT_BY_DESIGN.name}...")
    designs = {}
    for idx, item in active_items:
        did = item["design_id"]
        if did not in designs:
            designs[did] = []
        designs[did].append((idx, item))
        
    for did, d_items in sorted(designs.items()):
        first_idx, first_item = d_items[0]
        did_str = f"Design-{did:02d}"
        d_name_slug = re.sub(r"[^a-zA-Z0-9]+", "-", first_item["design_name"]).strip("-").lower()
        parent_sku = f"BB-RAW01-D{did:02d}"
        
        wb = openpyxl.load_workbook(BASE_TEMPLATE, keep_vba=True)
        ws = wb["Template"]
        for r in range(8, ws.max_row + 1):
            for c in range(1, mc + 1):
                ws.cell(r, c).value = None
                
        # Row 8: Parent Row
        out_r = 8
        for c in range(1, mc + 1):
            ws.cell(out_r, c).value = pv[c - 1]
            ws.cell(out_r, c)._style = copy(ps[c - 1])
            
        p_title = build_parent_title(first_item)
        p_desc = build_description(first_item)
        p_bullets = build_bullets(first_item)
        colors_all = ", ".join(item["variation"] for _, item in d_items)
        p_kw = build_keywords(p_title, colors_all, first_item.get("look", ""))
        
        ws.cell(out_r, C_SKU).value = parent_sku
        ws.cell(out_r, C_TYPE).value = "Parent"
        ws.cell(out_r, C_PARENT_SKU).value = None
        ws.cell(out_r, C_THEME).value = "COLOR/SET_NAME"
        ws.cell(out_r, C_NAME).value = p_title
        ws.cell(out_r, C_DESC).value = p_desc
        ws.cell(out_r, C_B1).value = p_bullets[0]
        ws.cell(out_r, C_B2).value = p_bullets[1]
        ws.cell(out_r, C_B3).value = p_bullets[2]
        ws.cell(out_r, C_B4).value = p_bullets[3]
        ws.cell(out_r, C_B5).value = p_bullets[4]
        ws.cell(out_r, C_KEY).value = p_kw
        ws.cell(out_r, C_MAT).value = derive_material(first_item.get("metal", "Gold Plated"))
        ws.cell(out_r, C_COUNT).value = first_item["count"]
        ws.cell(out_r, C_COLOR).value = None
        ws.cell(out_r, C_SIZE).value = None
        ws.cell(out_r, C_PART).value = parent_sku
        ws.cell(out_r, C_COLL).value = "Bangle Bliss Luxury Indian Jewellery"
        ws.cell(out_r, C_INSIDE).value = None
        ws.cell(out_r, C_SETNAME).value = None
        ws.cell(out_r, C_QTY).value = None
        ws.cell(out_r, C_PRICE).value = None
        ws.cell(out_r, C_MRP).value = None
        for c in range(31, 40):
            ws.cell(out_r, c).value = None
            
        # Child Rows: each variant x 3 sizes
        for v_idx, (_, v_item) in enumerate(d_items, 1):
            var = v_item["variation"]
            var_slug = re.sub(r"[^a-zA-Z0-9]+", "", var)[:3].upper()
            material = derive_material(v_item.get("metal", "Gold Plated"))
            count = v_item["count"]
            
            for sz in SIZES:
                out_r += 1
                for c in range(1, mc + 1):
                    ws.cell(out_r, c).value = cv[c - 1]
                    ws.cell(out_r, c)._style = copy(cs[c - 1])
                    
                c_sku = f"{parent_sku}-{var_slug}-{sz.replace('.', '')}"
                c_title = build_child_title(v_item, var)
                c_desc = build_description(v_item, var)
                c_bullets = build_bullets(v_item, var)
                c_kw = build_keywords(c_title, var, v_item.get("look", ""))
                
                ws.cell(out_r, C_SKU).value = c_sku
                ws.cell(out_r, C_TYPE).value = "Child"
                ws.cell(out_r, C_PARENT_SKU).value = parent_sku
                ws.cell(out_r, C_THEME).value = "COLOR/SET_NAME"
                ws.cell(out_r, C_NAME).value = c_title
                ws.cell(out_r, C_DESC).value = c_desc
                ws.cell(out_r, C_B1).value = c_bullets[0]
                ws.cell(out_r, C_B2).value = c_bullets[1]
                ws.cell(out_r, C_B3).value = c_bullets[2]
                ws.cell(out_r, C_B4).value = c_bullets[3]
                ws.cell(out_r, C_B5).value = c_bullets[4]
                ws.cell(out_r, C_KEY).value = c_kw
                ws.cell(out_r, C_MAT).value = material
                ws.cell(out_r, C_COUNT).value = count
                ws.cell(out_r, C_COLOR).value = var
                ws.cell(out_r, C_SIZE).value = sz
                ws.cell(out_r, C_PART).value = c_sku
                ws.cell(out_r, C_COLL).value = "Bangle Bliss Luxury Indian Jewellery"
                ws.cell(out_r, C_INSIDE).value = float(sz)
                ws.cell(out_r, C_THICK).value = 0.4
                ws.cell(out_r, C_THICK_UNIT).value = "Inches"
                ws.cell(out_r, C_SETNAME).value = f"Size {sz}"
                ws.cell(out_r, C_QTY).value = QTY
                ws.cell(out_r, C_PRICE).value = PRICE
                ws.cell(out_r, C_MRP).value = MRP
                for c in range(31, 40):
                    ws.cell(out_r, c).value = None

        if ws.max_row > out_r:
            ws.delete_rows(out_r + 1, ws.max_row - out_r)

        filename = f"{did_str}_{d_name_slug}.xlsm"
        out_file = OUT_BY_DESIGN / filename
        wb.save(out_file)
        print(f"  [Design {did:02d}] Saved {filename} ({out_r - 7} rows, {len(d_items)} variants)")

    # -------------------------------------------------------------
    # 3. BUILD MASTER COMBINED SHEET (All 31 active products)
    # -------------------------------------------------------------
    print(f"\nGenerating Master Combined Workbook for all 31 Active Products...")
    wb_comb = openpyxl.load_workbook(BASE_TEMPLATE, keep_vba=True)
    ws_comb = wb_comb["Template"]
    for r in range(8, ws_comb.max_row + 1):
        for c in range(1, mc + 1):
            ws_comb.cell(r, c).value = None

    cur_row = 7
    for idx, item in active_items:
        pid = item["id"]
        var = item["variation"]
        material = derive_material(item.get("metal", "Gold Plated"))
        count = item["count"]
        num_str = f"{idx:02d}"
        parent_sku = f"BB-RAW01-{num_str}"
        
        # Parent row
        cur_row += 1
        for c in range(1, mc + 1):
            ws_comb.cell(cur_row, c).value = pv[c - 1]
            ws_comb.cell(cur_row, c)._style = copy(ps[c - 1])
            
        p_title = build_parent_title(item)
        p_desc = build_description(item)
        p_bullets = build_bullets(item)
        p_kw = build_keywords(p_title, var, item.get("look", ""))
        
        ws_comb.cell(cur_row, C_SKU).value = parent_sku
        ws_comb.cell(cur_row, C_TYPE).value = "Parent"
        ws_comb.cell(cur_row, C_PARENT_SKU).value = None
        ws_comb.cell(cur_row, C_THEME).value = "COLOR/SET_NAME"
        ws_comb.cell(cur_row, C_NAME).value = p_title
        ws_comb.cell(cur_row, C_DESC).value = p_desc
        ws_comb.cell(cur_row, C_B1).value = p_bullets[0]
        ws_comb.cell(cur_row, C_B2).value = p_bullets[1]
        ws_comb.cell(cur_row, C_B3).value = p_bullets[2]
        ws_comb.cell(cur_row, C_B4).value = p_bullets[3]
        ws_comb.cell(cur_row, C_B5).value = p_bullets[4]
        ws_comb.cell(cur_row, C_KEY).value = p_kw
        ws_comb.cell(cur_row, C_MAT).value = material
        ws_comb.cell(cur_row, C_COUNT).value = count
        ws_comb.cell(cur_row, C_COLOR).value = None
        ws_comb.cell(cur_row, C_SIZE).value = None
        ws_comb.cell(cur_row, C_PART).value = parent_sku
        ws_comb.cell(cur_row, C_COLL).value = "Bangle Bliss Luxury Indian Jewellery"
        ws_comb.cell(cur_row, C_INSIDE).value = None
        ws_comb.cell(cur_row, C_SETNAME).value = None
        ws_comb.cell(cur_row, C_QTY).value = None
        ws_comb.cell(cur_row, C_PRICE).value = None
        ws_comb.cell(cur_row, C_MRP).value = None
        for c in range(31, 40):
            ws_comb.cell(cur_row, c).value = None
            
        # Children rows (2.4, 2.6, 2.8)
        for sz in SIZES:
            cur_row += 1
            for c in range(1, mc + 1):
                ws_comb.cell(cur_row, c).value = cv[c - 1]
                ws_comb.cell(cur_row, c)._style = copy(cs[c - 1])
                
            c_sku = f"{parent_sku}-{sz.replace('.', '')}"
            c_title = build_child_title(item, var)
            c_desc = build_description(item, var)
            c_bullets = build_bullets(item, var)
            c_kw = build_keywords(c_title, var, item.get("look", ""))
            
            ws_comb.cell(cur_row, C_SKU).value = c_sku
            ws_comb.cell(cur_row, C_TYPE).value = "Child"
            ws_comb.cell(cur_row, C_PARENT_SKU).value = parent_sku
            ws_comb.cell(cur_row, C_THEME).value = "COLOR/SET_NAME"
            ws_comb.cell(cur_row, C_NAME).value = c_title
            ws_comb.cell(cur_row, C_DESC).value = c_desc
            ws_comb.cell(cur_row, C_B1).value = c_bullets[0]
            ws_comb.cell(cur_row, C_B2).value = c_bullets[1]
            ws_comb.cell(cur_row, C_B3).value = c_bullets[2]
            ws_comb.cell(cur_row, C_B4).value = c_bullets[3]
            ws_comb.cell(cur_row, C_B5).value = c_bullets[4]
            ws_comb.cell(cur_row, C_KEY).value = c_kw
            ws_comb.cell(cur_row, C_MAT).value = material
            ws_comb.cell(cur_row, C_COUNT).value = count
            ws_comb.cell(cur_row, C_COLOR).value = var
            ws_comb.cell(cur_row, C_SIZE).value = sz
            ws_comb.cell(cur_row, C_PART).value = c_sku
            ws_comb.cell(cur_row, C_COLL).value = "Bangle Bliss Luxury Indian Jewellery"
            ws_comb.cell(cur_row, C_INSIDE).value = float(sz)
            ws_comb.cell(cur_row, C_THICK).value = 0.4
            ws_comb.cell(cur_row, C_THICK_UNIT).value = "Inches"
            ws_comb.cell(cur_row, C_SETNAME).value = f"Size {sz}"
            ws_comb.cell(cur_row, C_QTY).value = QTY
            ws_comb.cell(cur_row, C_PRICE).value = PRICE
            ws_comb.cell(cur_row, C_MRP).value = MRP
            for c in range(31, 40):
                ws_comb.cell(cur_row, c).value = None

    if ws_comb.max_row > cur_row:
        ws_comb.delete_rows(cur_row + 1, ws_comb.max_row - cur_row)

    combined_file = OUT_DIR / "raw01-all-31-products-combined-v6.xlsm"
    wb_comb.save(combined_file)
    print(f"\nSaved Master Combined Workbook: {combined_file.name} ({cur_row - 7} total rows across 31 products)")

    print("\n" + "=" * 65)
    print("All Amazon Flat Sheets Generated Successfully!")
    print(f"  Individual Product Sheets: {len(active_items)} files in {OUT_BY_PRODUCT.relative_to(ROOT)}")
    print(f"  Design Family Sheets:     {len(designs)} files in {OUT_BY_DESIGN.relative_to(ROOT)}")
    print(f"  Master Combined Sheet:    {combined_file.name}")
    print("=" * 65)

if __name__ == "__main__":
    main()

