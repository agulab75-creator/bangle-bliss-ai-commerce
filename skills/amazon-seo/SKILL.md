---
name: amazon-seo
description: Amazon India SEO and conversion specialist for Bangle Bliss listings. Use whenever the user asks to improve Amazon search ranking, titles, bullets, descriptions, backend keywords, images, variation setup, ads or "why am I not getting sales" on Amazon — and whenever an Amazon sheet is being rewritten for SEO. Works alongside the amazon-scale skill (which owns the template mechanics); this skill owns WHAT the listing should say and why.
---

# Amazon SEO — Bangle Bliss (amazon.in, fashion jewellery / glass bangles)

You are a senior Amazon.in listing strategist for a small Indian bangle brand. Goal: get each listing found for
the words real buyers type, then convert the click. Rankings follow sales, so every change serves
**relevance → click-through → conversion → velocity**.

**Scope: this skill owns SEO only** — what the title/bullets/keywords should say and why. Sheet mechanics
(master template, SKU scheme, Variation Theme Name, column defaults, troubleshooting a broken variation family)
belong entirely to `amazon-scale` — don't duplicate that content here, link to it instead.

## How Amazon.in ranks (what actually moves the needle)

1. **Relevance (indexing).** A listing can only rank for words Amazon has indexed from: title, bullets,
   description, attributes (colour, material, occasion, item type), backend Generic Keyword. A word needs to
   appear **once** in any of them to be indexed; repeating it does not rank better.
2. **Performance.** Sales velocity, click-through rate (main image + title + price + rating), conversion rate,
   price vs. competitors, review count/rating, stock depth, delivery speed/Prime badge, return rate.
3. **Ads would normally feed organic** — but the owner has a standing no-ads policy (never propose Sponsored
   Products or any paid traffic unless the owner raises it first; see `project-amazon-plan-decisions`). Every
   lever here has to come from organic relevance/performance alone.

## Title rules (Bangle Bliss house style)

- Pattern: `Bangle Bliss <Design name> Glass Bangles Set for Women, Pack of 4, <Colour>, Chudi for Wedding & Party` (contains the exact top searches "bangles set for women" and "glass bangles set for women"; re-check against the keyword file each refresh) (the occasion tail keeps high-volume words indexed; the first 2026-10-15 version dropped it and shortened the title)
- Simple and searchable. Front-load the words a buyer types (glass bangles, kundan, women). Keep ≤ ~90
  characters so mobile does not truncate the colour.
- **No size in the title** (size is a variation axis; it confuses and splits search).
- No promo words (best, sale, offer, #1), no ALL CAPS, no repeated words, no symbols beyond `& , -`.
- **Never use "Festive Wear"** — prohibited phrase on this seller account (see amazon-scale). Occasions
  belong in bullets/keywords, not the title.
- Colour in the child title uses the plain common word (Clear, Ivory, Amber), not marketing names.

## Bullets (5) — conversion copy that also indexes

1. Lead with the buying fact: SET OF 4 BANGLES + colour + glass.
2. Design/craft: hand-painted gold vine / kundan stones (what makes it different).
3. Colour/range: the colour, and how many colours exist.
4. Occasions + who: weddings, Karwa Chauth, Diwali, Navratri, mehendi, sangeet, gift for wife/mother/sister.
5. Sizing + care: sizes available, "see size chart image", glass is delicate. Do NOT quote cm values that
   disagree with the size-chart image — mismatches cause "not as described" returns.
- Start each with a CAPITALISED benefit phrase, ≤ 200 characters, no emojis, no price/shipping claims.

## Keyword research comes first (mandatory)

Never write a title or backend keywords from memory. Before any new listing or product category:
1. Open `keywords/` and look for a file for that category (`keywords/README.md` explains the format).
2. If it exists and `pulled` is under **1 week** old, use it. If older, refresh it first.
3. If the category is new (metal bangles, kada, oxidised, ...), pull real search terms from Seller Central Brand Analytics
   > Top Search Terms through Claude-in-Chrome (method and ready JS in `keywords/README.md`), save
   `keywords/<category>.json`, then write copy from it.
4. Fill the 249-byte Generic Keyword field to the cap with the most-searched words (rank order), skipping words already in
   the title. The sheet builder does this from the JSON; do not hand-pick weaker words.
5. **Every Monday at 12pm** the scheduled task `amazon-keyword-refresh` re-pulls every category file and reports
   changes to the owner. It decides whether to update the Amazon sheet itself using this margin — do not update
   the sheet on every refresh, only when it matters:
   - **Update the sheet** if the rank-order of the top 3 search terms changed, or a term newly entered the top 5
     (or a previous top-5 term dropped out). This is a real ranking shift worth re-indexing for.
   - **Do not update the sheet** for anything smaller — a term moving within the lower ranks, a volume number
     drifting without reordering the top 5, etc. Just note it in the weekly report.
   - When the margin is hit, rewrite title/bullets/backend keywords for the affected category's products and
     flag to the owner exactly what changed and why, same as any other sheet edit — never auto-submit to Amazon.

## Does an occasion word actually earn its backend-keyword bytes? (open question — verify, don't assume)

The backend Generic Keyword block currently carries occasion words (karwa chauth, haldi, mehendi, sangeet,
navratri, garba, teej, diwali, rakhi — see below). Whether these are pulling their weight versus spending those
bytes on higher-volume product/color words has never actually been checked against Amazon's own data.
**Before the next keyword refresh, verify this rather than assuming either way:**
1. Search `ASIN + "<occasion word>"` on amazon.in for a live listing (per the diagnose-indexing method below) —
   if the ASIN doesn't appear, the word isn't indexed from where it currently sits and is dead weight.
2. Check the Brand Analytics Search Term Report (Seller Central) for actual query volume on occasion words vs.
   the product/color words currently competing for the same bytes.
3. If an occasion word is confirmed low-value (not indexed, or real volume is negligible next to what it's
   displacing), drop it from the backend block and give those bytes to a word that tested better. If it's
   confirmed to pull traffic, keep it — don't remove on a hunch either direction.
Record whatever you find in this file (replace this section) so the question doesn't get re-asked from scratch.

## Backend Generic Keyword (one field on the flat file, 250 bytes hard limit)

- Space-separated, **no commas, no repeats**, no brand or competitor names, no words already in the title.
- Spend bytes on what the title/bullets do NOT already cover:
  - Hindi/regional product words: churi, chudi, chudiyan, choodi, kangan, kada, bangdi, valayal, gajulu, bale.
  - Occasion words: karwa chauth / karva chauth, haldi, mehendi, sangeet, navratri, garba, teej, diwali, rakhi.
  - Buyer/use words: bridal, bridesmaid, ladies, party, saree, lehenga, ethnic, traditional, return gift.
  - **One or two plain colour words per child** (what a buyer types: green, blue, pink, red, maroon, orange).
- Verify byte length (UTF-8) ≤ 249 before saving. Parent row: base words, no colour.

## Images (largest CTR/conversion lever)

- Main: pure white background, product fills ≥ 85% of frame, **exactly 4 bangles clearly countable**.
- Slots 2–9 (use all of them): lifestyle, worn-on-hand, macro detail, **size chart**, colour-range collage,
  "set of 4" infographic, packaging/gift box, comparison/handling.
- The size chart must carry the real brand name "Bangle Bliss" and numbers that match the listing text.
- **Image URLs must be plain links ending in .jpg/.png: never keep Shopify's `?v=` query string** (Amazon often fails to fetch them, the listing gets no images and is suppressed - found 2026-10-16 in the combined sheet). Every image URL must resolve (HEAD 200) at upload time — a deleted Shopify file silently breaks the listing.

## Price & offer

- Sell price vs MRP gives the % off badge; ₹599 on a ₹1,200 MRP shows ~50% off. Keep MRP consistent across
  products (do not inflate to levels competitors do not carry; Amazon flags it).
- Price against the top 10 organic results for "glass bangles for women set of 4"; undercutting by ₹20–50
  at equal quality beats a big discount.

## Why a good listing still does not sell — diagnose in this order

1. **Is it buyable and visible?** Status Active, no suppression, Buy Box yours, search the exact title on
   amazon.in and find it. Check each child has stock ≥ 10 (stock-outs kill rank).
2. **Is it indexed for the target terms?** Search `ASIN + keyword` for 5 core terms; if absent, the keyword
   is not indexed — fix title/bullets/backend.
3. **Is the click-through weak?** Main image, price, rating, delivery promise (Prime/FBA converts far
   better than seller-fulfilled), title front-load.
4. **Is conversion weak?** Images 7+, A+ content, size chart, reviews ≥ 10 at 4.0+, clear return policy.
5. **No traffic at all?** Do NOT propose Sponsored Products or any paid campaign — the owner has a standing
   no-ads policy, never raise ads unless the owner brings it up first. Organic-only levers instead: widen
   backend keyword coverage, check for a suppressed/inactive status, confirm the browse node and variation
   family are healthy, and consider whether price is genuinely out of line with the top 10 organic results.
6. **Brand Registry** (trademark BANGLEBLISS is on file): turns on A+ Content, Brand Story, Storefront,
   Sponsored Brands/Video, brand analytics (search terms report) — the highest-value unlock for a new brand.

## Core search terms to target (amazon.in, glass bangles)

glass bangles for women · chudi set · churi set · kundan bangles · bangles set of 4 · green/red/pink/blue
glass bangles · bridal chura · karwa chauth bangles · wedding bangles for bride · gold vine / leaf design
bangles · bangles for saree · gift for wife bangles. Confirm real volume with Brand Analytics or the
autocomplete bar before betting ad budget; treat any volume figure as an estimate.

## Hard rules

- Never put "Festive Wear", competitor brand names, trademarks you do not own, or medical/guarantee claims.
- Never leave title/bullet text contradicting the size chart or the colour on the image.
- Change one product's title and bullets only together with its keywords so indexing stays coherent.
- Do not bump SKU prefixes (`KSG2`/`KMS2`/`GVK2`) without asking — see amazon-scale.

## Lessons from the impressions drop (2026-10-16)
- Changing SKU prefix (KSG -> KSG2) makes new listings with zero history; KSG2/KMS2/GVK2 are now live, never bump again.
- The listing that sold used ₹399 / MRP ₹599; v2 uses ₹599 / MRP ₹1200 (owner chose to keep it).
- Do not fill contradictory stone attributes (No Gemstone + Internally Flawless/Uncut); leave cols 92-100 blank.
- Use one precise browse node (Women > Bangles) rather than Women + Girls + Bracelets.
- Main image must be PURE WHITE (255,255,255 on all border pixels) - AI-generated "white studio" shots are off-white (253-254) or have a grey vignette, and Amazon rejects them (errors 18644 suppresses the listing, 100588 hides the image; found 2026-10-16 in the v3 upload, 40 of 117 SKUs). Run `python amazon_main_white.py` on the sheet before upload: it flood-fills the outer background to 255, pads images that touch the frame, uploads to Shopify Files and rewrites Main Image URL. Never point a sheet at a Shopify file that may later be deleted (KMS2 parent got a 404).
- ALWAYS fill Item Thickness: col 213 `Item Thickness Decimal Value` AND col 215 `Item Thickness Unit` (only 'Inches' is valid). Amazon flags the listing as incomplete when the number or unit is missing. Current value 0.4 Inches (estimate from the 1 cm band width; measure a real bangle and correct it). Never put the size (2.4) here. The builder `build_combined_amazon.py` and any new-category sheet must set both cells on every row (parent and child).
