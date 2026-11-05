"""Write flipkart-update-data.xlsx values into a Flipkart category template / returned file by header name,
matching rows on Seller SKU ID. Usage: python fk_fill_by_sku.py <template.xls> <out.xls>
Needs xlrd + xlutils. NOTE: xlutils/xlwt drops any VBA project and may drop dropdown UI (see flipkart-scale skill);
prefer Excel COM (scripts/fill_flipkart.ps1) when the template has macros. Keeps a backup copy automatically."""
import sys, shutil, xlrd, openpyxl
from xlutils.copy import copy as xl_copy
from pathlib import Path
src, dst = sys.argv[1], sys.argv[2]
shutil.copy(src, str(Path(dst).with_suffix(".backup.xls")))
data_path = sys.argv[3] if len(sys.argv) > 3 else Path(__file__).parent / "flipkart from claude" / "flipkart-update-data.xlsx"
data = openpyxl.load_workbook(data_path).active
hdr = [c.value for c in data[1]]
vals = {r[0]: dict(zip(hdr, r)) for r in data.iter_rows(min_row=2, values_only=True)}
rb = xlrd.open_workbook(src, formatting_info=True)
sheet_name = [n for n in rb.sheet_names() if n not in ("Summary Sheet", "Index") and rb.sheet_by_name(n).ncols > 50][0]
rs = rb.sheet_by_name(sheet_name)
h = [str(rs.cell_value(0, c)).strip() for c in range(rs.ncols)]
col = {n: i for i, n in enumerate(h) if n}
wb = xl_copy(rb); ws = wb.get_sheet(rb.sheet_names().index(sheet_name))
fields = ["Product Title", "Search Keywords", "Key Features", "Brand Color", "Color", "Type", "Pack of (pieces)", "Items Included", "Main Image URL", "Other Image URL 1", "Other Image URL 2", "Other Image URL 3", "Other Image URL 4"]
hit = 0; unknown = []
for r in range(4, rs.nrows):
    sku = str(rs.cell_value(r, col["Seller SKU ID"])).strip()
    if not sku: continue
    if sku not in vals:
        unknown.append(sku); continue
    for f in fields:
        if f in col and vals[sku].get(f):
            ws.write(r, col[f], vals[sku][f])
    hit += 1
wb.save(dst)
print("filled rows:", hit, "| SKUs in template not in data (e.g. removed variants):", sorted(set(unknown))[:10])
missing = [f for f in fields if f not in col]
print("fields not found in template (check header names):", missing)
