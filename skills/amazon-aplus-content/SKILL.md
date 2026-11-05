---
name: amazon-aplus-content
description: Build and upload Amazon A+ Content modules for Bangle Bliss listings — module selection, copy, and image specs, learned from reference examples of what converts. Use after a product is already live on Amazon (A+ applies to an existing ASIN/parent, it does not create a listing). Runs after amazon-seo/amazon-scale have built and uploaded the base listing.
---

# Amazon A+ Content — Bangle Bliss

Builds the enhanced-content modules Amazon shows below the fold on a product page (not the title/bullets/
backend keywords — that's `amazon-seo`/`amazon-scale`; this skill starts only once a listing already exists).

## Status: scaffold, awaiting reference training

This skill is a placeholder structure. The owner is going to provide 20–25 reference A+ content examples
(competitors' or category leaders') for this skill to learn from — what module choices, copy patterns, and
visual treatments actually convert vs. ones that don't. **Until that reference set is added, do not invent
"best practice" A+ content from general knowledge** — fall back to the verified findings below (from actual
research done 2026-10-17/18, see project history) rather than guessing, and flag to the owner that the deeper
reference-trained guidance isn't in yet.

When the owner provides references, this file should grow two sections:
- **Brand-constant rules** — what should look/read the same across every Bangle Bliss product's A+ content
  (voice, colour-neutral policy, module order, typography treatment, logo/brand-strip placement).
- **Per-product-varying guidance** — what legitimately changes by product (hero scene, which benefit icons
  apply, size-chart numbers, comparison-table contents) and how to decide it from the reference set's patterns
  rather than copying one reference's specific choices onto an unrelated product.

## What's already known (verified research, not guesswork)

- Only ~40% of top amazon.in kundan-bangle listings have real A+ content at all — there's real headroom.
- ZAYA (4.8★) is the category benchmark: 970×600 banners, icon-based benefit callouts, a trust strip, and a
  comparison table.
- **One A+ document per design** (not per colour) applied to the whole parent — a colour-specific doc only
  shows on that one colour's children, and if reused across colours it reads wrong. Keep hero imagery and copy
  colour-neutral when the doc covers the whole product family.
- **No price, no offers, no guarantees, no superlative claims** ("best", "#1") in A+ copy — these are compliance
  risks, not stylistic choices.
- **Big type for mobile** — most Amazon India traffic is mobile; a size-panel or benefit-icon module with small
  text fails there even if it looks fine in the desktop preview.
- **Size chart numbers must come from the brand's real chart file**, never invented or estimated — a previous
  version shipped wrong cm values and had to be corrected and resubmitted. Always read the actual chart image
  before writing any number into an A+ module.
- New images for A+ modules should be purpose-generated (Shopify Magic via the Playwright pipeline — see
  `feedback-use-playwright-magic-pipeline` memory), not the existing gallery shots reused — gallery shots read
  as generic/low-effort versus a dedicated 970×600 banner treatment.

## Workflow (mechanics — already built, see project history)

1. **Compose module images**: `My Bangle Bliss/aplus/compose.py <PRODUCT> <Colour>` (or the `_global` variant
   for a colour-neutral family doc) renders module images to `aplus/out/`.
2. **Plan/spec**: `aplus/PLAN.md` and `aplus/RESEARCH.md` hold the product-specific module plan and the
   category research findings above, in full.
3. **Upload**: `aplus/upload_aplus.py` drives Seller Central's A+ Manager via Playwright — `--login` once,
   then build with `--spec`, stage with `--apply` (applies to ASINs, draft only), and only `--submit` after
   explicit owner go-ahead. **Never run `--submit` without the owner saying so in that session** — draft and
   apply are safe to do proactively, submit is not.
4. Basic tier = 5 modules, Premium = 7 (Bangle Bliss has Premium access via Brand Registry).

## Hard rules (carried over from project history — do not relearn these the hard way again)

- Never invent size-chart numbers — read the real chart file every time.
- Never reuse a colour-specific A+ doc across the whole parent family without making it colour-neutral first.
- Never submit without the owner's explicit go-ahead in that session, even if a draft looks finished.
- Keep alt text under ~95 characters as a safety margin against Amazon's ~100-char cap.
