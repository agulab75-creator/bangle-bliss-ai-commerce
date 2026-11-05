"""
Fill the Amazon BRACELET template with the Kundan Stone glass bangles (10 colours x 3 sizes),
using photo links from your Shopify store.

    python fill_amazon.py
Output: amazon-kundan-stone-glass.xlsm  (the original template is not touched)

Layout: 3 variation families (one per size 2.4 / 2.6 / 2.8). Each family = 1 Parent row + 10 Child rows (colours).
Amazon's BRACELET template has no COLOR/SIZE variation theme, so size is a separate family and
colour is the variation (theme COLOR).
Edit the CONFIG block below to change price, MRP, quantity, etc., then run again.
"""
import json, os, subprocess, tempfile, re
from pathlib import Path
import openpyxl
import listing_copy as LC

ROOT = Path(__file__).parent
TEMPLATE = r"~\Downloads\BRACELET (6).xlsm"
OUT = ROOT / "amazon-kundan-stone-glass-v3.xlsm"
STORE = "your-store.myshopify.com"
PRODUCT = "gid://shopify/Product/<id>"

# ---------------- CONFIG (placeholders: please confirm) ----------------
PRICE = LC.PRICE      # Your Price INR
MRP = LC.MRP          # Maximum Retail Price
QUANTITY = LC.STOCK    # stock per child
HANDLING_DAYS = 2
FULFILMENT = "DEFAULT"   # DEFAULT = you ship it; AMAZON_IN = Fulfilled by Amazon
ADDRESS = ("BANGLE BLISS, Shop No-327, Ground floor, Urban Polyclinic Lal Gali, Sitaram Bazar Road, "
           "Delhi Gate, Daryaganj, New Delhi 110002, India")
EMAIL = "<seller-email>"
BROWSE_NODE = "Jewellery > Women > Bangles & Bracelets > Bangles (<id>)"
# ------------------------------------------------------------------------

SIZES = [("2.4", "6.0"), ("2.6", "6.4"), ("2.8", "6.9")]   # size, approx inner diameter in cm
# name, sku code, bullet about this colour
COLOURS = [
 ("Sky Aqua", "AQU", "TRANSLUCENT SKY-AQUA GLASS: Faceted-cut see-through glass in a soft pastel aqua that pairs with whites, pastels and gold or silver outfits."),
 ("Parrot Green", "PGR", "GLOSSY PARROT GREEN: Bright translucent faceted glass in a vivid parrot green, lovely with reds, yellows and festive wear."),
 ("Coral Peach", "COR", "TRANSLUCENT CORAL PEACH: Faceted glass in a warm coral-peach shade that suits cream, peach and pastel outfits."),
 ("Orchid Pink", "ORC", "TRANSLUCENT ORCHID PINK: Faceted glass in a violet-tinted orchid pink, pretty with pink, white and ivory outfits."),
 ("Mint Green", "MNT", "MILKY MINT GREEN: Soft opaque pastel mint-green glass (not see-through) that pairs well with white, ivory and pastel outfits."),
 ("Magenta", "MAG", "DEEP MAGENTA: Rich translucent faceted glass in bold magenta-purple, striking with silk sarees and festive wear."),
 ("Ruby Red", "RED", "GLOSSY RUBY RED: Deep translucent red faceted glass, a classic choice for bridal, Karwa Chauth and festive looks."),
 ("Plum Wine", "PLM", "PLUM WINE SWIRL: Dark plum-wine translucent glass with marbled magenta-pink swirls for a rich, unique look."),
 ("Emerald Green", "EMR", "EMERALD TEAL GREEN: Translucent faceted glass in deep emerald-teal green, beautiful with red, gold and cream outfits."),
 ("Maroon", "MRN", "DEEP MAROON: Deep translucent maroon faceted glass, elegant with gold, cream and festive silks."),
]

# ---------- photos from Shopify (product gallery) ----------
def gql(q, v=None):
    d = Path(tempfile.mkdtemp()); qf, vf, of = d/"q.graphql", d/"v.json", d/"o.json"
    qf.write_text(q, encoding="utf-8")
    cmd = f'shopify store execute --store {STORE} --query-file "{qf}" --output-file "{of}"'
    if v is not None:
        vf.write_text(json.dumps(v)); cmd += f' --variable-file "{vf}"'
    subprocess.run(cmd, shell=True, capture_output=True, text=True)
    j = json.loads(of.read_text(encoding="utf-8")); return j.get("data", j)

def photos():
    items = []
    cursor = None
    while True:
        r = gql('query($id:ID!,$a:String){product(id:$id){media(first:100,after:$a){nodes{... on MediaImage{alt image{url}}} pageInfo{hasNextPage endCursor}}}}',
                {"id": PRODUCT, "a": cursor})["product"]["media"]
        for n in r["nodes"]:
            if n.get("image"):
                items.append(((n.get("alt") or ""), n["image"]["url"].split("?")[0]))
        if not r["pageInfo"]["hasNextPage"]: break
        cursor = r["pageInfo"]["endCursor"]
    return items

def pick(items, colour):
    """AI photos only: main = white studio shot, then lifestyle, worn on hand, close-up. Raw photos are ignored."""
    mine = [(a, u) for a, u in items if colour.lower() in a.lower() and "kundan stone - view" not in a.lower()]
    def first(word):
        return next((u for a, u in mine if word in a.lower()), None)
    seq = [first("white studio") or first("white"), first("lifestyle"), first("worn"), first("close-up")]
    seq = [u for u in seq if u]
    return (seq[0] if seq else None), seq[1:]

# ---------- template ----------
wb = openpyxl.load_workbook(TEMPLATE, keep_vba=True)
ws = wb["Template"]
label_row, data_row = 4, 8
colmap = {}
for c in range(1, ws.max_column + 1):
    lab = ws.cell(label_row, c).value
    if lab:
        colmap.setdefault(str(lab).strip(), []).append(c)

def col(label, n=0):
    cs = colmap.get(label)
    return cs[n] if cs and len(cs) > n else None

prefill = {c: ws.cell(data_row, c).value for c in range(1, ws.max_column + 1) if ws.cell(data_row, c).value not in (None, "")}

def put(r, label, value, n=0):
    c = col(label, n)
    if c and value not in (None, ""):
        ws.cell(r, c).value = value
    elif not c:
        print("  (no column named)", label)

def base_row(r):
    for c, v in prefill.items():
        ws.cell(r, c).value = v

photo_map = photos()
print("photos found on the product:", len(photo_map))

def common(r, parent, sku, parent_sku, colour, size, cm):
    base_row(r)
    put(r, "SKU", sku)
    put(r, "Product Type", "BRACELET")
    put(r, "Listing Action", "Create or Replace (Full Update)")
    put(r, "Parentage Level", "Parent" if parent else "Child")
    if not parent:
        put(r, "Parent SKU", parent_sku)
    put(r, "Variation Theme Name", "COLOR")
    put(r, "Item Name", LC.amazon_title(colour, size) if not parent else LC.amazon_parent_title(size))
    put(r, "Brand Name", "bangle bliss")
    put(r, "Product Id Type", "GTIN Exempt")
    put(r, "Recommended Browse Nodes", BROWSE_NODE)
    put(r, "Manufacturer", "BANGLE BLISS")
    ctext = colour or "10 colours"
    put(r, "Product Description", LC.amazon_description(colour, size))
    bullets = LC.amazon_bullets(colour, size)
    for i, b in enumerate(bullets):
        put(r, "Bullet Point", b, i)
    put(r, "Generic Keyword", LC.AMAZON_SEARCH_TERMS)
    for i, k in enumerate(LC.AUDIENCE_KEYWORDS):
        put(r, "Target Audience Keyword", k, i)
    for i, k in enumerate(LC.AUDIENCE):
        put(r, "Target Audience", k, i)
    # template prefilled item length 2.4 cm / weight 300 g are wrong for bangles: leave blank until measured
    for lab in ("Item Length End to End", "Item Length Unit", "Item Weight", "Item Weight Unit"):
        for cc in colmap.get(lab, []):
            ws.cell(r, cc).value = None
    put(r, "Style", "Contemporary")
    put(r, "Number of Items", 4)
    put(r, "Item Type Name", "Bangle Bracelets")
    if colour:
        put(r, "Color", colour)
    put(r, "Inside Diameter Decimal Value", float(size))
    put(r, "Inside Diameter Unit", "Inches")
    put(r, "Setting Type", "Bezel")
    for i, o in enumerate(["Wedding", "Diwali", "Engagement", "Anniversary"]):
        put(r, "Occasion", o, i)
    put(r, "Part Number", sku)
    put(r, "Collection Name", "Kundan Stone Glass Bangles")
    put(r, "Item Shape", "Round")
    put(r, "Manufacturer Contact Information", ADDRESS)
    put(r, "Packer Contact Information", ADDRESS)
    put(r, "Bracelet Form", "Bangle")
    put(r, "Number of Packs", 1)
    put(r, "Country of Origin", "India")
    put(r, "Responsible Person's Email or Electronic Address", EMAIL)
    put(r, "Manufacturer’s Email or Electronic Address", EMAIL)
    put(r, "Safety Attestation", "Yes")

def offer(r):
    put(r, "Item Condition", "New")
    put(r, "Fulfillment Channel Code (IN)", FULFILMENT)
    put(r, "Quantity (IN)", QUANTITY)
    put(r, "Handling Time (IN)", HANDLING_DAYS)
    put(r, "Your Price INR (Sell on Amazon, IN)", PRICE)
    put(r, "Maximum Retail Price (Sell on Amazon, IN)", MRP)

# clear old data rows below the header (keep example rows above)
for rr in range(data_row, ws.max_row + 1):
    for c in range(1, ws.max_column + 1):
        ws.cell(rr, c).value = None

r = data_row
for size, cm in SIZES:
    psku = f"KSG-{size.replace('.', '')}"
    common(r, True, psku, None, None, size, cm)
    main, others = pick(photo_map, "Sky Aqua")
    if main:
        put(r, "Main Image URL", main)
    r += 1
    for colour, code, _ in COLOURS:
        sku = f"KSG-{code}-{size.replace('.', '')}"      # same SKU as the Shopify variant
        common(r, False, sku, psku, colour, size, cm)
        offer(r)
        main, others = pick(photo_map, colour)
        if main:
            put(r, "Main Image URL", main)
        for i, u in enumerate(others):
            put(r, "Other Image URL", u, i)
        if not main:
            print("  WARNING: no photo for", colour)
        r += 1

try:
    wb.save(OUT)
except PermissionError:
    OUT = ROOT / "amazon-kundan-stone-glass-v3.xlsm"   # earlier files may be open in Excel
    wb.save(OUT)
print("saved", OUT, "rows:", r - data_row)
