---
name: flipkart-scale
description: Build or update Flipkart bulk-listing spreadsheets for Bangle Bliss products from the category template, mirroring the amazon-scale skill's approach. Use this whenever the user asks to make, create, generate, update, or fix a Flipkart sheet/listing for a product, asks about Flipkart Color/attribute values or search keywords for a product, or asks to add a new color/variant to an existing Flipkart listing — even if they don't say "template" or name this skill directly.
---

# Flipkart Scale — Bangle Bliss Flipkart listing sheets

Flipkart category templates are large legacy `.xls` files (not `.xlsx`) with dropdown data
validation baked in across many sheets, and often a **password-protected VBA macro project**
("Fast Validate", Ctrl+Shift+S — check for a `_VBA_PROJECT_CUR` stream with `olefile` before
assuming there isn't one). Read with `xlrd` (`pip install xlrd` if missing — `openpyxl` cannot open
legacy `.xls`). **Prefer Excel COM automation** (`scripts/fill_flipkart.ps1`) for writing — it edits
cell values in place without touching validation, macros, or formatting.

**Known limitation found 2026-10-08:** some columns live inside a collapsed/grouped "optional
attributes" column block (`Columns.Item(n).OutlineLevel > 0`) that Excel ties to sheet protection.
Writes to cells in that group succeed in the live COM session and even read back correctly
*before* `.Close()`, but silently fail to persist to disk — confirmed with a completely fresh Excel
process re-opening the saved file. Mandatory (non-grouped) columns are unaffected. If you hit this,
check `Columns.Item(n).OutlineLevel` and `Worksheet.ProtectContents` before assuming your write
script has a bug — it may be this. Don't try to guess or brute-force the protection password.

**If the user explicitly accepts the tradeoff** (confirmed this way on 2026-10-08, after being
warned first), the only working fallback is `xlutils.copy` (`xlrd` read with
`formatting_info=True` → `xlwt` write) — but **this strips the entire VBA project**, since `xlwt`
cannot write a `vbaProject` stream, and likely drops in-Excel dropdown validation UI too (the
underlying *data* in `Index`/`DropDownValuesForColumnNN` sheets survives as plain values; only the
pickable-dropdown mechanism is at risk). Always: back up the working COM-filled file first, run the
bypass on the real file only after that backup exists, then verify with `olefile` that you know
what you lost and with `xlrd` that the target cells and everything else (SKUs, titles, colors,
reference sheets) actually survived.

## Two different Flipkart files look similar — check which one you have

Before assuming a `.xls` in a Flipkart folder is a new-listing template, open it and check its
sheet names:
- If it has only `Summary Sheet`, `Sample`, `Template (Fill Here)` with just **Main FSN / Variant
  FSN** columns — this is the **Variant Grouping** tool. It links products that are *already
  live* on Flipkart (each with an assigned FSN) so they appear as color/size options on one page.
  It cannot be used to create new listings and has no title/color/price/image columns at all.
- If it has a sheet named after the category (e.g. `bangle_bracelet_armlet`) with ~100+ columns,
  plus `Index`, `DropDownValuesForColumnNN`, `MatchingAttributes`, `VariantAttributes`,
  `Listing FAQ Sheet`, `Image GuideLines` — this is the real **new-listing category template**,
  Flipkart's equivalent of Amazon's flat file. This is the one to fill in.

Found both of these for Bangle Bliss on 2026-10-08 — the grouping file was the one initially
provided in `flipkart from claude/`, the real category template came after. If asked to "fill up"
a Flipkart sheet and only the grouping file is present, say so rather than guessing or forcing
data into the wrong file.

## Reading the category template's structure

The main data sheet has 4 header rows, then data starts at row 5 (1-indexed in Excel/COM terms):
1. Row 1: attribute name (the header to match on)
2. Row 2: data type (Text / Number / Decimal / Yes-No / Multivalue, etc.)
3. Row 3: example value
4. Row 4: definition/explanation

**Multivalue fields use `::` as the separator** (e.g. `Red::Black`), not Amazon's space-separated
or comma-separated conventions — don't mix these up between the two skills.

The `VariantAttributes` sheet lists which attributes are allowed to differ between rows in the same
product family (for bangles: `Pack of`, `Bangle Brand Size`, `Color`). The `MatchingAttributes`
sheet lists everything that must stay **identical** across every row in that family — this is the
Flipkart equivalent of Amazon's "template defaults," and for a new product you should pull these
values from the `Index` sheet's allowed-values columns (see below) rather than inventing them.

**Grouping new listings** (no FSN needed yet): give every row in the same product family the same
free-text **Group ID** (e.g. `KSG`) and leave **Parent Variant FSN** blank — that field is only for
linking new rows to an FSN that already exists from a prior listing. Flipkart assigns the FSN after
upload; there is nothing to fill in there for a brand-new product.

**Critical: every row's combination of `VariantAttributes` values must be unique within a Group ID,
not just the SKU.** Found the hard way 2026-10-08: submitted a 36-row KSG group where 5 of the 12
colors (Parrot Green, Mint Green, Emerald Green → all mapped to Flipkart `Color: Green`; Coral
Peach, Rust Orange → both mapped to `Color: Orange`) shared a Color value at the same Bangle Brand
Size. Flipkart's QC rejected the **entire group** — not just those rows — with "Grouping Failed.
This product has matching variant attributes with SKU(s): ..." listing the colliding SKUs, which
then cascaded into every other row in the group failing too ("cannot be created in group, as the
following skus ... failed quality checks"). The precise original shade name living safely in the
free-text `Brand Color` field does **not** help here — Flipkart's grouping logic only looks at the
actual `VariantAttributes` columns (`Color`, `Bangle Brand Size`, `Pack of` for bangles), so two
rows that are obviously different products to a human (Mint Green vs. Parrot Green) are
indistinguishable duplicates to Flipkart if they share the same `Color` dropdown value and size.

**Before submitting, check `Color` (or whatever the category's variant-defining dropdown attribute
is) is unique per distinct product within a Group ID — if two shades would naturally map to the
same popular-color word, pick a second word from the same allowed-values list rather than reusing
it**, even if it's a slightly less perfect semantic fit (e.g. Rust Orange → `Bronze` once `Orange`
is already taken by Coral Peach; Emerald Green → `Turquoise` once `Green` is taken by Parrot Green).
Cross-check the full `Color` + `Bangle Brand Size` combination for every row before upload — a
simple `collections.Counter` over `(color, size)` tuples catches this instantly.

**Flipkart will regenerate and return your file with data pre-populated plus QC status/reasons**
when you upload one built against an outdated schema, or just to report QC results — don't assume
the returned file is the same shape as what you submitted. On 2026-10-08 the schema grew from 148
to 255 columns between versions; header *names* stayed stable so a name-matching fill script still
works, but positions shifted substantially. Always re-locate columns by header name against
whatever file you're actually editing, never assume a column index carries over from a prior
session's file.

## Allowed values live in the `Index` sheet, not just the `DropDownValuesForColumnNN` sheets

Columns whose row-4 definition says "Click Here to get Allowed Values" are controlled dropdowns.
Some have a dedicated `DropDownValuesForColumnNN` sheet; most don't — their valid values are
instead one column each in the `Index` sheet (attribute name in its row 2, values below). Check
both before guessing a value, and don't write a value that isn't in the list — Flipkart will fail
QC on it.

**Flipkart's `Color` field is a closed, short list** (around two dozen common words: Beige, Black,
Blue, Bronze, Brown, Copper, Gold, Green, Grey, Lavender, Lime, Magenta, Maroon, Multicolor,
Orange, Pink, Platinum, Purple, Red, Rose, Silver, Turquoise, White, Yellow — confirm against the
actual file's `Index` sheet since category/version can vary) — unlike Amazon, where the structured
Color field can be the literal marketing shade name. This means the "map the niche shade to a
popular search color" logic from `amazon-scale` isn't just an SEO nicety here, it's mandatory: every
row's `Color` must be one of the allowed values. Put the precise original shade name (e.g. "Sky
Aqua") in **Brand Color** instead, which is free text — that preserves both at once.

**Don't just copy Amazon's shade → word mapping over unmodified** — Amazon's free-text keyword
field tolerates duplicate words fine (multiple shades can all add "green" to their keywords with no
issue), but Flipkart's `Color` is a `VariantAttributes` field and **must be unique per product
within a Group ID** (see the critical note above) or the whole group's upload fails. Start from
Amazon's mapping for the semantic starting point, then de-duplicate: if two or more shades would
land on the same word, spread them across different allowed values instead. Worked example for
KSG's 12 colors (final, collision-free mapping used 2026-10-08): Sky Aqua→Blue, Parrot Green→Green,
Coral Peach→Orange, Orchid Pink→Pink, Mint Green→Lime, Magenta→Magenta, Ruby Red→Red, Plum
Wine→Purple, Emerald Green→Turquoise, Maroon→Maroon, Rust Orange→Bronze, Lemon Yellow→Yellow.

## Filling in a new product (workflow)

1. Copy the category template to its own new file first (same one-file-per-product rule as
   `amazon-scale` — never add a second product's rows into an existing product's workbook).
2. Confirm product category still matches the template (`bangle_bracelet_armlet` covers bangles,
   bracelets and armlets — a genuinely different product type needs Flipkart's template for that
   category instead).
3. Write a small Python script (see `flipkart_ksg_data.py` in the project root as a worked example)
   that builds one dict per row — one per color × size combination — covering every column you have
   real data for, and dump it to JSON.
4. Run `scripts/fill_flipkart.ps1 -FilePath <file> -DataPath <json> -SheetName <category sheet
   name>` to write it in. The script matches JSON keys to column headers by name (not by hardcoded
   index), so it's safe even if a template's column order differs from a previous one.
5. Re-open the saved file with `xlrd` and spot-check a few rows before calling it done.

## What's a template default vs. what needs real business input

Reuse the box dimensions/weight, stone/gemstone boilerplate, and brand/material/style attributes
established for Amazon (see `amazon-scale`) wherever the same physical product is involved — they
don't change by sales channel. But several Flipkart-specific operational and legal fields have
**no established value yet** and must not be guessed:
- **MRP vs. selling price** — no markup convention exists across any channel yet; filled equal
  (599 = 599) as a placeholder on 2026-10-08, flagged for the user to set a real MRP.
- **HSN code, Tax Code, Luxury Cess** — tax/compliance fields, left blank, need the user's actual
  registration details.
- **Manufacturer/Packer/Importer Details** — legal business name + address + pincode, left blank.
- **Fulfilment by, Procurement type/SLA, Shipping provider, handling fees** — operational choices
  that affect real order handling; filled with reasonable-looking placeholders (Seller / 2 days) on
  2026-10-08 but flagged, since getting these wrong risks SLA violations, not just a cosmetic
  listing error. **`Procurement type` is a closed enum, not free text** — guessed "Instock" first
  and Flipkart rejected it; the actual allowed values are `QUICK, REGULAR, EXPRESS, DOMESTIC,
  MADE_TO_ORDER, INTERNATIONAL`. `REGULAR` is the safe default for ordinary ready-to-ship stock.

## Attributes that are "optional" by category but mandatory-by-default per product

Found 2026-10-08, second submission attempt: fields that are genuinely not applicable to glass
bangles (Silver Purity, Diamond Cut/Clarity/Shape/Weight/Color Grade, Pearl Type, Silver Weight,
Certification) still came back as hard QC failures when left blank — *"Mandatory Attribute [x] is
missing"* — even though nothing in the template's own color-coding flagged them as required for
this category. Worse, a subset of these (**Model Number**, **Diameter (inch)**, confirmed by the
`Used For: ID, Variant` note in their row-2 type text) additionally failed with *"Attribute data
not present ... but it is an idAttribute of group DEFAULT and id Attributes are mandatory by
default"* — Flipkart uses a cluster of ID-tagged attributes to identify the product regardless of
whether they're semantically relevant, and will not accept them blank.

**Fix**: for genuinely-not-applicable dropdown attributes, write `NA` if `NA` is in that attribute's
allowed-values list (check the `Index` sheet — it was, for every one of these). For ID-tagged
free-text fields, a blank is never acceptable even if the attribute seems irrelevant:
- **Model Number** — give it a real (if generic) value; used the product/material name
  ("Bangle Bliss Kundan Stone Glass") constant across all rows, since a physical design's model
  number doesn't usually vary by color.
- **Diameter (inch)** — for bangles this one actually *is* meaningful: reused the same value as
  `Bangle Brand Size` (2.4/2.6/2.8), since Flipkart's own example value ("2.5") confirms it's the
  same kind of measurement, just under a different attribute name.

This looks the same in spirit as the Color-uniqueness bug but is a different failure mode (blank
vs. duplicate) — expect this kind of back-and-forth with Flipkart's live QC on a new category:
submit, read every distinct error line (not just the first), fix, resubmit. Don't assume a
category's full mandatory-field set is knowable in advance from the template's own color-coding —
treat Flipkart's QC response as the authoritative source and iterate.
- **Images must be `.JPEG`** — Flipkart rejects other formats outright. The Shopify-hosted product
  photos reused as placeholders are `.png`; they need converting and re-hosting before a real
  upload, not just linking as-is.

Always call out which of the above are still placeholders in your summary to the user — don't let
a fully-populated-looking spreadsheet imply these are settled when they aren't.
