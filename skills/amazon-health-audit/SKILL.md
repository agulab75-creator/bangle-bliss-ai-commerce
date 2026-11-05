---
name: amazon-health-audit
description: Weekly read-only health audit of every live Bangle Bliss Amazon listing — finds gaps and leaks (suppression, stock-outs, broken variation families, indexing gaps, image/compliance errors, A+ status, rating/review drops) and reports them. Never fixes or uploads anything itself; never proposes ads. Use when asked to audit, check health of, or find problems with the Amazon catalog, or on the weekly schedule.
---

# Amazon Health Audit — Bangle Bliss

A **read-only diagnostic sweep** across every live Bangle Bliss ASIN/family, run weekly, to catch gaps and
leaks before they cost sales — distinct from `amazon-seo` (which rewrites copy) and `amazon-keyword-refresh`
(which refreshes search-term files). This skill only finds and reports problems; fixing them is a separate,
explicitly-approved step using `amazon-seo`/`amazon-scale`.

**Never propose Sponsored Products or any paid campaign from this audit** — the owner has a standing no-ads
policy (see `project-amazon-plan-decisions` memory). A traffic gap found here gets reported as a gap, not an
ads recommendation.

## Checklist (run all of these every time, not just the ones that seem relevant)

1. **Buyable & visible** — for every parent/child: Active status, no suppression flag, Buy Box owned, and the
   listing is actually findable by searching its own exact title on amazon.in.
2. **Stock depth** — flag any child at 0 stock that *shouldn't* be (cross-check against known intentional
   zero-stock decisions like the STB size 2.8 rule — a 0 that's a deliberate business decision is not a leak,
   don't flag it as one; a 0 that looks accidental is).
3. **Variation family health** — children actually grouped under their parent (not split into orphaned
   single-child "families" — the exact failure mode documented in `amazon-scale`). Check `(Color, Set Name)`
   uniqueness and that Variation Theme Name is identical and typo-free across every row.
4. **Indexing** — spot-check 3-5 core search terms per product category (from the keyword files) with
   `ASIN + keyword` searches; report any that don't surface the listing.
5. **Image compliance** — main image pure white (255,255,255 border, not off-white), all slots present
   (lifestyle, worn-on-hand, macro, size chart, colour-range, infographic), every image URL resolving
   (HEAD 200) and not a stale `cdn.shopify.com?v=` link to a file that may have been deleted.
6. **A+ Content status** — approved / awaiting review / rejected / expired for each product family; flag
   anything rejected or expired for more than a few days with no resubmission.
7. **Reviews & rating** — any family that dropped below 4.0 or lost review count (a removed/flagged review is
   itself worth flagging, not just a number).
8. **Price sanity** — selling price vs. MRP still shows a believable discount band, and hasn't drifted from
   what the owner last set without a reason.
9. **Keyword drift carried over from `amazon-keyword-refresh`** — if that task found a top-3 shift this week
   and the sheet wasn't actually updated yet, call that out as an open gap here too.
10. **Cross-session conflicts** — note anything that looks like a parallel session's upload partially
    overwrote another's work (seen before with STB stock/hero-image updates) — these are easy to miss until
    a listing silently regresses.

## Reporting

One report per run: a short table of **gap / where / how bad / suggested next step** (not a fix — a next
step like "re-run amazon-scale's troubleshooting checklist on KMS2" or "ask owner whether 0 stock on X was
intentional"). Group by severity (buyability/suppression first, cosmetic last). Save to
`bangle bliss/amazon-health-audit/<date>.md` so the owner has a record to compare week over week, and note
anything that's unchanged from the prior week's report vs. genuinely new.

## What this skill explicitly does not do

- Does not edit any sheet, upload anything, or touch Seller Central settings — audit only.
- Does not recommend ads, ever, regardless of what the audit finds.
- Does not duplicate `amazon-seo`'s copy rules or `amazon-scale`'s sheet mechanics — if a gap needs fixing,
  name which of those skills owns the fix and stop there.
