---
name: amazon-scale
description: Build or update Amazon bulk-listing spreadsheets for Bangle Bliss products from the fixed master template. Use this whenever the user asks to make, create, generate, update, or fix an Amazon sheet/listing/spreadsheet for a product, asks about Amazon keywords or search terms for a product, or asks to add a new color/variant to an existing Amazon listing — even if they don't say "template" or name this skill directly.
---

# Amazon Scale — Bangle Bliss Amazon listing sheets

This skill builds Amazon bulk-listing spreadsheets (the "flat file" format Seller Central accepts
on the Add Products via Upload page) for Bangle Bliss products. It exists because rebuilding an
Amazon listing sheet from scratch each time is slow and error-prone — almost everything about a
new color/variant is identical to an existing one, and the only things that genuinely change are
the SKU, title, color, and search keywords.

## The master template

`amazon from claude/Amazon Tamplate for claude.xlsm` is the master. Its "Template" sheet has labels
in row 4, and data starts at row 8 — row 8 is always the Parent SKU row, rows 9+ are Child variant
rows (one per color × size combination).

**Rule: one file per product, always.** Never add a second product's rows into an existing
product's workbook. When starting a new product's listing, copy the master template to a brand-new
file first, then work in that copy.

**Rule: exactly one Parent row per product — never one parent per size.** A product has ONE parent
SKU (just the product code, e.g. `KMS`, no size suffix). Every color × size combination is a Child
of that single parent. Do not create a separate "KMS-24" / "KMS-26" / "KMS-28" parent per size —
that was a mistake made once (2026-10-11) and corrected; it only happens if you copy the per-size
parent-row pattern from an older sheet (KSG) without checking it against the Variation Theme rule
below.

**When adding new variant rows to an existing product's sheet** (e.g. a new color was added to an
existing product): clone every column's value from a known-correct existing child row — there are
roughly 418 columns, and hand-filling them is how mistakes creep in — then override only: SKU,
Item Name, the `Color` attribute, `Set Name` (size — see below), and the keyword tail (below). A
short Python/openpyxl script that reads one template row and writes N new rows with those fields
overridden is the reliable way to do this; don't retype columns by hand.

## Variation Theme Name: `COLOR/SET_NAME` — and why `Set Name` must vary by size

Confirmed against the master template's own `Valid Values` sheet (row 6, the enum list scoped
`Variation Theme Name - [ BRACELET ]`): Amazon has **no** `COLOR/SIZE` theme for the BRACELET
product type. The only valid two-axis theme that includes `COLOR` and something size-shaped is
`COLOR/SET_NAME`. The `Data Definitions` sheet spells out the mechanism: "The theme's attributes
must be populated for all items in the grouping" (example given: `Size/Color`) — i.e. **both**
attributes named in the theme must actually differ across child rows, or the grouping doesn't work.

That means `Set Name` is **not** a constant — it's the size axis:
- `Color` (col 64) varies by color, same value across all 3 sizes of that color.
- `Set Name` (col 240) varies by size, same value across all colors of that size — e.g.
  `"Kundan Multi Stone Glass Bangle Set — Size 2.4"` / `"— Size 2.6"` / `"— Size 2.8"`.
- Together, (Color, Set Name) uniquely identifies every child under the one parent.

Earlier drafts of this skill said `Set Name: kundan glass set` was a fixed constant under "What
stays constant" — that was wrong and has been removed below; it would have made every child's
second variation axis identical, collapsing the grouping. Leave the **Parent row's** `Color` and
`Set Name` cells blank (parents don't carry variant-dimension values).

**Confirmed, not just theoretical (2026-10-11):** the KSG listing was uploaded with `Set Name`
held constant across all three sizes of every color, and Amazon Seller Central never grouped its
child ASINs into one variation family — Seller Assistant's own diagnosis named "unique variation
attributes... no duplicate size-color combinations" as the cause. **The master template's own
built-out KSG example rows (row 8 onward in `Amazon Tamplate for claude.xlsm`) still have this
exact bug** — `Set Name` = `"kundan glass set"` on every row regardless of size. Do not copy that
column's value verbatim from the master's demo rows when building a new product; override it with
the size-suffixed version as described above. (The KSG live listing itself still needs this same
fix re-uploaded — flag it to the user rather than assuming it's already fixed.)

### If old SKUs are already registered against a broken listing

Re-uploading a flat file with the same SKUs as an already-live (but broken/ungrouped) listing
just updates that same listing in place — Amazon doesn't treat it as a fresh variation family,
so a COLOR/SET_NAME fix made in the file may not actually take effect on an SKU Amazon already
has on record. If the user reports a product "keeps messing up with the old products" after a
fix, the reliable move is a **new SKU prefix for the whole product** (parent and every child),
not just re-uploading corrected data under the old SKUs. Precedent (2026-10-12): KSG → `KSG2`,
KMS → `KMS2`, GVK → `GVK2` (new files `amazon-<product>-v2.xlsm`), keeping the old sheets
untouched as a record of what was live before. Don't reuse a bumped prefix a second time without
asking — check with the user whether `KSG2` etc. are themselves already registered before
bumping again.

### Troubleshooting checklist if variants still don't group after upload

If the user reports Seller Central isn't showing child ASINs as one variation family, check in
this order (first two are the ones this skill has actually gotten wrong before):
1. **Unique (Color, Set Name) pairs** — query the generated rows for duplicate
   `(col 64, col 240)` tuples across all children. Any duplicate means two children are
   indistinguishable to Amazon's variation engine.
2. **Identical Variation Theme Name on every row** (parent and all children) — col 6 must be
   exactly `COLOR/SET_NAME` everywhere, no typos or stray whitespace.
3. **Non-varying attributes match**: Brand Name (col 9), Product Type (col 2), Manufacturer
   (col 27) must be byte-identical across parent and every child.
4. **Product Id Type** (col 10) consistent (`GTIN Exempt` for all Bangle Bliss listings).
5. **Inventory/Active status** — zero-quantity or inactive children can fail to display even
   with a correct theme; these are operational (post-upload, on Seller Central), not something
   the sheet alone guarantees, so confirm after upload rather than assuming the file fixes it.
6. **Processing time** — Amazon can take 24–48 hours to reflect a new/changed variation family;
   don't conclude the sheet is wrong from an immediate re-check.

## What stays constant across products (the template defaults)

Bangle Bliss's products are almost all in the same size and weight class, so these fields should be
copied from the template, not re-derived per product, unless a specific product genuinely differs:

- **Stone fields**: Stone ID `0`, Stone Type `No Gemstone`, Stone Color `Other Color`, Stone Shape
  `Round`. (Kundan-style glass studs aren't "real" gemstones in Amazon's taxonomy — this is just
  boilerplate, not a per-product judgment call.)
- **Item dimensions**: `8×8×8 cm`, item weight `250 g`.
- **Package dimensions**: `10×10×10 cm`, package weight `400 g`.
- **Variation Theme Name**: `COLOR/SET_NAME` (see above — `Set Name` itself still varies by size).
- **Style**: `Contemporary`.
- **Target Audience Keywords**: `Women, Girls, Brides, Ladies, Bridesmaids`.

## What changes per product/variant

- SKU (Parent SKU is just the product code, no size suffix; Child SKU is
  `<PRODUCT>-<COLOR CODE>-<SIZE>`, e.g. `KMS-IVM-24`)
- Item Name (title) — follows the `amazon-seo` skill's pattern (no size — size is a variation
  axis, not title text): `Bangle Bliss <Design name> Glass Bangles Set for Women, Pack of 4,
  <Colour>, Chudi for Wedding & Party`. Do not reintroduce `Size <X.X>` into the title; this
  skill's own pattern briefly disagreed with `amazon-seo` on this and was corrected 2026-10-21 —
  `amazon-seo` owns title wording, this skill owns the sheet mechanics it gets typed into.
- The `Color` attribute and `Set Name` (size) on each child row
- The generic keyword's color tail (below)

**Never include "Festive Wear" in an Item Name.** Amazon's title-compliance check rejects it
outright as a prohibited phrase for this seller account — found and fixed 2026-10-08 after it was
baked into the master template's titles. Use `Diwali` (already used as the replacement) or another
safe occasion word (Karwa Chauth, Navratri, Teej) instead. If any other phrase gets flagged as
prohibited by Amazon in the future, add it to this list so it isn't reused.

## Generic Keyword field — the color-targeting fix

Amazon's flat file has exactly **one** free-text "Generic Keyword" field per row (it used to be
five separate "Search Terms" columns; it's been consolidated into one — don't go looking for more).

The base keyword block, identical across every child row of a product:
```
churi chudi kangan karwa chauth bridal wedding sangeet mehendi haldi diwali navratri garba teej
rakhi gift for wife mother sister ethnic traditional indian jewellery stone kada
```

This block alone was the original problem: it never mentioned color, so a search for "blue
bangles" would never surface a listing whose actual variant is named "Sky Aqua." Customers search
for common color words, not marketing shade names.

**Append one popular, high-search-volume color word to the end of each child row's keyword block** —
the word a customer would actually type, not the shade's marketing name. Don't limit yourself to a
fixed short list of colors; pick whichever common word is the nearest honest fit for that shade.
Mapping used so far for Kundan Stone Glass (KSG), as a reference point for new products:

| Shade | Keyword word |
|---|---|
| Sky Aqua | blue |
| Parrot Green, Mint Green, Emerald Green | green |
| Coral Peach, Rust Orange | orange |
| Orchid Pink, Magenta | pink |
| Ruby Red | red |
| Plum Wine | purple |
| Maroon | maroon |
| Lemon Yellow | yellow |

Leave the **Parent row's** keyword block as just the base text with no color appended — it isn't
tied to one color.

## Related context

For which raw product photos map to which Shopify product/color (useful when naming Amazon color
variants to match what's actually live on Shopify), see `IMAGE_PRODUCT_MAP.md` in the project root.

## Combined sheet (2026-10-15)

On the user's request, `amazon from claude/amazon-all-3-products-combined.xlsm` holds GVK2, KMS2 and KSG2 in ONE
file (three parent rows, each with its own children) — an exception to "one file per product". Built by
`build_combined_amazon.py` from the three v2 sheets: titles carry no size, `Set Name` is `Size X.X`, size chart
image is Other Image URL 4 on every child, GVK2-CRM removed. Copy/keyword rules live in the `amazon-seo` skill.
