# Bangle Bliss — working notes for Claude

## Shopify product/image mapping
See [IMAGE_PRODUCT_MAP.md](IMAGE_PRODUCT_MAP.md) (+ `.json` twin) before touching `raw/` photos,
image generation, or the glass-bangle Shopify products (KSG, KMS, GVK). It's the source of truth
for which raw photo belongs to which product/color/variant, generation pipeline usage, and what's
already been fixed vs. still open.

## Amazon listing sheets

Covered by the `amazon-scale` skill (`.claude/skills/amazon-scale/SKILL.md`) — it should
auto-trigger whenever asked to make, update, or fix an Amazon sheet/listing for a product, but
invoke it explicitly if it doesn't. Master template location, field defaults, the keyword-color
mapping, and the "Festive Wear" prohibited-phrase fix all live there — don't duplicate that detail
here.

## Flipkart listing sheets

Covered by the `flipkart-scale` skill (`.claude/skills/flipkart-scale/SKILL.md`) — same idea as
Amazon's, but Flipkart's legacy `.xls` templates need `xlrd` to read and Excel COM automation
(`scripts/fill_flipkart.ps1`) to write safely, since they have embedded dropdown validation that a
raw rewrite could break. Also documents how to tell Flipkart's two different file types apart (new
listing template vs. variant-grouping tool) and which fields are still open placeholders
(MRP/pricing, HSN/tax, legal business details, fulfilment settings, JPEG image requirement).

## Storefront theme
Store audit, what was built and what's still open: [STORE-AUDIT-2026-10-16.md](STORE-AUDIT-2026-10-16.md).
Theme work goes in `theme-festive/`, the local copy of the LIVE theme #<id>: test on unpublished #<id> first, then push with --allow-live.
Use the `indian-ecommerce-builder` skill for any store/theme/offer work.
