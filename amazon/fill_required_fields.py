"""
Fill the Amazon-required fields that are blank on every row (old and new) but were
filled in the earlier processing-summary snapshot: Stone ID/Type/Creation
Method/Treatment Method/Clarity/Color/Cut/Shape and Item Thickness Unit.
Same placeholder value on every child row, as found in the processing summary.
Also backfills KSG-AQU-24's still-missing Item Width/Height (cols 314-317).

    python fill_required_fields.py
"""
import openpyxl

SRC = "amazon-kundan-stone-glass-v3.xlsm"

CONSTANT_FIELDS = {
    92: 0,                      # Stone ID
    93: "No Gemstone",          # Stone Type
    95: "Unknown",               # Stone Creation Method
    96: "Not Treated",           # Stone Treatment Method
    97: "Internally Flawless",   # Stone Clarity
    98: "Other Color",           # Stone Color
    99: "Uncut",                 # Stone Cut
    100: "Round",                # Stone Shape
    215: "Centimetres",          # Item Thickness Unit
}

AQU24_DIM_FIX = {
    314: 15, 315: "Centimetres", 316: 16, 317: "Centimetres",
}


def main():
    wb = openpyxl.load_workbook(SRC, keep_vba=True)
    ws = wb["Template"]

    filled_count = 0
    for r in range(8, ws.max_row + 1):
        sku = ws.cell(row=r, column=1).value
        if not sku:
            continue
        level = ws.cell(row=r, column=4).value
        if level != "Child":
            continue
        for col, val in CONSTANT_FIELDS.items():
            cell = ws.cell(row=r, column=col)
            if cell.value in (None, ""):
                cell.value = val
                filled_count += 1
        if sku == "KSG-AQU-24":
            for col, val in AQU24_DIM_FIX.items():
                cell = ws.cell(row=r, column=col)
                if cell.value in (None, ""):
                    cell.value = val

    wb.save(SRC)
    print(f"filled {filled_count} cells across all child rows, plus AQU-24 width/height.")


if __name__ == "__main__":
    main()
