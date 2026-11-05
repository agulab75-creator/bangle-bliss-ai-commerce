"""Fill the Flipkart template generated from the STB photos (Flipkart-hosted image URLs) for 33 SKUs. Non-image attributes are cloned from a Flipkart-accepted GVK row,
then product fields overridden. File keeps EXACTLY Flipkart's issued name (renamed files are rejected). NOT sent to QC."""
import collections, shutil
from pathlib import Path
import xlrd
from xlutils.copy import copy as xl_copy
from thread_setup import COLOURS

ROOT = Path(__file__).parent; D = ROOT / "stb" / "fk"
AI = D / "<flipkart-catalog-file>.xls"
BASE = Path(r"~\Downloads\<flipkart-catalog-file>.xls")
SH = "bangle_bracelet_armlet"
FKCOL = {"royal-blue": "Blue", "crimson-red": "Red", "mustard-yellow": "Yellow", "coral-pink": "Pink", "turquoise": "Turquoise", "parrot-green": "Lime",
         "emerald-green": "Green", "rani-pink": "Magenta", "wine-maroon": "Maroon", "orange": "Orange", "golden": "Gold"}
PHRASE = {"royal-blue": "blue", "crimson-red": "red", "mustard-yellow": "yellow", "coral-pink": "pink", "turquoise": "turquoise", "parrot-green": "green",
          "emerald-green": "green", "rani-pink": "pink", "wine-maroon": "maroon", "orange": "orange", "golden": "golden"}
CODE2SLUG = {v[2]: k for k, v in COLOURS.items()}

rb = xlrd.open_workbook(AI, formatting_info=True); rs = rb.sheet_by_name(SH); H = [str(x) for x in rs.row_values(0)]; col = {h: i for i, h in enumerate(H)}
bs = xlrd.open_workbook(BASE).sheet_by_name(SH)
brow = next(i for i in range(4, bs.nrows) if str(bs.cell_value(i, 6)).startswith("GVK") and "0 error" in str(bs.cell_value(i, 2)))
base = {H[c]: bs.cell_value(brow, c) for c in range(bs.ncols) if str(bs.cell_value(brow, c)).strip() != ""}
ai = {}
for r in range(4, rs.nrows):
    k = str(rs.cell_value(r, col["Seller SKU ID"])).strip()
    if k: ai[k] = (r, {H[c]: rs.cell_value(r, c) for c in range(rs.ncols) if str(rs.cell_value(r, c)).strip() != ""})

DESC = ("Bangle Bliss Silk Thread Bangles for women and girls, sold as a set of 12 slim bangles in {cn}. Each bangle is wrapped by hand in soft silk thread and finished with small "
        "antique-gold beads. Wear the full dozen as a matching stack or mix with other bangles and kadas. A good choice for weddings, bridal looks, Karwa Chauth, Diwali, Navratri, "
        "mehendi, sangeet and parties, with sarees, lehengas and suits. Available in sizes 2.4, 2.6 and 2.8 - check the size chart image to choose your fit. "
        "Keep away from water and perfume.")
KEEP_AI = ["Main Image URL", "Other Image URL 1", "Other Image URL 2", "Other Image URL 3", "Other Image URL 4", "Design", "Finish"]
OUT = D / AI.name
wb = xl_copy(rb); ws = wb.get_sheet(rb.sheet_names().index(SH))
def put(r, name, v):
    if isinstance(v, float) and v == int(v): v = int(v)
    ws.write(r, col[name], v)
seen = collections.Counter(); n = 0
for sku, (r, aid) in ai.items():
    _, code, z = sku.split("-"); slug = CODE2SLUG[code]; cn = COLOURS[slug][1]; size = f"{z[0]}.{z[1]}"
    row = dict(base)
    row.update({"Group ID": "STB", "MRP (INR)": 1000, "Your selling price (INR)": 279, "Stock": 0 if size == "2.8" else 10,
                "Model Number": "Silk Thread Bangle Set", "Model Name": "Silk Thread Bangles with Gold Beads", "Ideal For": "Women::Girls", "Type": "Bangle Set",
                "Base Material": "Fabric", "Plating": "NA", "Gemstone": "NA", "Ornamentation Type": "Beads::Thread Work", "Style Type": "Sleek Bangle",
                "Items Included": "12 Bangles", "Pack of (pieces)": 12, "Color": FKCOL[slug], "Brand Color": cn, "Bangle Brand Size": size, "Diameter (inch)": size,
                "Seller SKU ID": sku, "HSN": 7117, "Tax Code": "GST_3", "Occasion": "Wedding & Engagement::Party::Everyday",
                "Product Title": f"Bangle Bliss Silk Thread Bangles Set for Women (Pack of 12) {cn}",
                "Search Keywords": "::".join([f"{PHRASE[slug]} silk thread bangles", "silk thread bangles set for women", "thread bangles set of 12", "bridal silk thread bangle sets", "thread bangles for women"]),
                "Key Features": f"set of 12 silk thread bangles::antique gold bead detailing::soft silk thread finish in {cn.lower()}::sizes 2.4, 2.6 and 2.8 (see size chart image)",
                "Other Features": "Handcrafted Finish::Festive & Bridal Wear", "Description": DESC.format(cn=cn),
                "QC Failed Reason (if any)": "", "Catalog QC Status": "", "Product Data Status": ""})
    for k in KEEP_AI:
        if k in aid: row[k] = aid[k]
    for c in range(rs.ncols):
        name = H[c]
        if name in row: put(r, name, row[name])
        elif str(rs.cell_value(r, c)).strip() != "": ws.write(r, c, "")
    seen[(FKCOL[slug], size)] += 1; n += 1
wb.save(str(OUT)); shutil.copy(AI, D / ("AI-GENERATED-ORIGINAL-" + AI.name)) if not (D / ("AI-GENERATED-ORIGINAL-" + AI.name)).exists() else None
chk = xlrd.open_workbook(str(OUT)).sheet_by_name(SH)
print("rows filled", n, "| duplicate (Color,size):", [k for k, v in seen.items() if v > 1])
allowed = {"Beige","Black","Blue","Bronze","Brown","Copper","Gold","Green","Grey","Lavender","Lime","Magenta","Maroon","Multicolor","Orange","Pink","Platinum","Purple","Red","Rose","Silver","Turquoise","White","Yellow"}
print("colours allowed:", all(v in allowed for v in FKCOL.values()))
for r in (4, 5, 36):
    g = lambda nme: chk.cell_value(r, col[nme])
    print(g("Seller SKU ID"), g("Group ID"), g("Color"), g("Bangle Brand Size"), g("MRP (INR)"), g("Your selling price (INR)"), g("Pack of (pieces)"), "|", g("Main Image URL")[:55], "|", g("Other Image URL 4")[:40])
    print("  ", g("Product Title"), "|", g("Search Keywords"))
imgmissing = [chk.cell_value(r, col["Seller SKU ID"]) for r in range(4, chk.nrows) if chk.cell_value(r, col["Seller SKU ID"]) and not all(str(chk.cell_value(r, col[k])).startswith("http") for k in KEEP_AI[:5])]
print("rows missing an image URL:", imgmissing)
