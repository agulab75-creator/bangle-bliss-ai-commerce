---
name: seo
description: Top-level SEO dispatcher for Bangle Bliss across every sales channel (Shopify/Google, Amazon, Flipkart). Use whenever the user asks for "SEO" broadly, or for a product launch/update that should be optimized everywhere at once, without naming one channel specifically.
---

# SEO — Bangle Bliss cross-channel dispatcher

This skill does not own SEO content itself — it decides which channel-specific skill(s) to invoke and in what
order, then lets each one do its own job. Never write title/keyword/meta copy directly from this skill; always
go through the owning sub-skill below so channel-specific rules (byte limits, closed-list attributes, variant
filtering) aren't silently violated.

## Sub-skills

| Channel | Skill | Owns |
|---|---|---|
| Google / storefront | `shopify-seo` | meta title/description, URL handles, structured data, image alt text (SEO half) |
| Amazon.in | `amazon-seo` (+ `amazon-scale` for sheet mechanics, `amazon-seo-specialist` agent for a full audit) | title/bullets/backend keywords, image/listing diagnosis |
| Flipkart | `flipkart-seo` (+ `flipkart-scale` for sheet mechanics) | Product Title/Search Keywords/Key Features, live-listing updates |

## How to dispatch

1. **Figure out scope first.** If the user names a channel ("fix my Amazon title"), invoke only that channel's
   skill — don't touch the other two uninvited. If they ask for "SEO" on a product/launch with no channel named,
   or explicitly say "everywhere"/"all platforms", run all three.
2. **Order for a new product launch**: `shopify-seo` first (the product needs to exist on Shopify with its
   handle/images before Amazon/Flipkart sheets reference those assets or copy decisions), then `amazon-seo` and
   `flipkart-seo` in parallel (they're independent of each other — safe to fan out as separate subagents via the
   `Agent` tool if the task is large, since neither reads the other's output).
3. **For an existing-listing refresh** (keyword drift, ranking drop), invoke only the channel(s) affected —
   these run independently and on different schedules (Amazon's keyword refresh is weekly, see `amazon-seo`).
4. **Never duplicate a sub-skill's rules here.** If you notice this file drifting toward restating title
   patterns or byte limits, that content belongs in the sub-skill, not here — move it.

## Shared keyword source

All three channels read buyer search language from the same keyword files
(`amazon-seo/keywords/<category>.json`), refreshed by the `amazon-seo` skill's weekly cadence. `flipkart-seo`
and `shopify-seo` use that file as their baseline, then confirm with their own channel's real search signal
(Flipkart autosuggest, Google autocomplete) before finalizing copy — a word that ranks on Amazon isn't
guaranteed to be the term a Flipkart or Google searcher types.

## What this skill does NOT do

- Doesn't build or upload sheets (that's `amazon-scale`/`flipkart-scale`).
- Doesn't do A+ Content (separate skill — see `amazon-aplus-content` — runs after a listing already exists).
- Doesn't generate product images or run the Shopify product-creation pipeline.
- Doesn't decide pricing, stock, or variant structure — those are business inputs the relevant sub-skill asks
  the owner for when needed, not something SEO infers.
