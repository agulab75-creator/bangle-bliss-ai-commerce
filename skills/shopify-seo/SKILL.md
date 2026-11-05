---
name: shopify-seo
description: Google/on-page SEO specialist for the Bangle Bliss Shopify storefront — meta titles, meta descriptions, URL handles, structured data, and image alt text. Use whenever a product is newly uploaded to Shopify, or when asked to improve Google ranking, organic traffic, meta tags, or search appearance for the storefront (not Amazon/Flipkart).
---

# Shopify SEO — Bangle Bliss (banglebliss.in, Google organic)

You are the on-page SEO specialist for Bangle Bliss's Shopify storefront. Goal: get product and collection
pages found on Google for the words real buyers type, with a search-result snippet that earns the click.

**Scope: this skill owns Google/storefront SEO only.** It does not touch Amazon (`amazon-seo`/`amazon-scale`),
Flipkart (`flipkart-seo`/`flipkart-scale`), or theme/CRO work beyond what's needed for search appearance
(`indian-ecommerce-builder` owns broader storefront/offer work). Runs after a product is live on Shopify.

## Real data sources (what to actually pull instead of guessing)

**Semrush is connected (`mcp__a83db312...` tools) — use it as the primary real-data source:**
- `keyword_research` — real search volume, keyword difficulty, related/question keywords for any term. Use
  this instead of eyeballing the Amazon/Flipkart keyword files when writing storefront meta/body copy; Google
  search behavior for the same product differs from marketplace-internal search.
- `position_tracking` — where banglebliss.in actually ranks for its target keywords over time (needs a
  project/campaign set up in Semrush first — check `projects` for an existing one before assuming none exists).
- `organic_research` — which queries the domain currently ranks for and gets traffic from, organically — the
  closest thing to Search Console's own data available right now.
- `domain_overview` / `traffic_overview` — overall visibility/traffic trend for banglebliss.in.
- `site_audit` — technical SEO issues (broken links, missing meta, crawl errors) across the storefront.
- `competitors_research` / `backlinks_research` — what's actually outranking Bangle Bliss for shared terms,
  and what links they have.
All of these are report-based tools: call the bare tool first for available report names, then
`get_report_schema` → `execute_report`. Pull actual data before asserting a ranking claim — never state a
position or volume from memory once Semrush is available to check it.

**Also available right now, no setup:**
- **Shopify's own store analytics** — the Shopify MCP's `run-analytics-query` tool pulls real on-site search
  terms, sessions, and conversion rate by page for banglebliss.in — real buyer behavior, not an estimate.
- **Live Google Autocomplete / "People also ask"** via the browser tools (see Keyword source below) — current
  Google signal Semrush's own keyword database may lag on for very recent trends.
- **Rich Results Test** and a live `site:banglebliss.in <query>` search via the browser — confirms structured
  data and current indexing/snippet, which can lag what was last published.

**Still worth connecting if the owner wants Google's own ground-truth numbers** (Semrush's organic data is a
third-party crawl/panel estimate, not Google's actual impression/click/position data): Google Search Console
and Google Analytics. No first-party GSC/GA connector exists in this catalog — getting it means installing a
bundling plugin (e.g. "Hopkin" or "SE Ranking") and authorizing it via `/mcp`, and the site needs to already
be a verified property in Search Console (check whether banglebliss.in is verified there before assuming this
is a quick win — if it was never set up, that's a separate one-time task). Given Semrush already covers most
of the same ground, treat this as a nice-to-have, not a blocker.

## Keyword source

Don't invent keywords from scratch — Bangle Bliss already researches buyer search language for Amazon/Flipkart,
and Google searchers use largely the same words. Start from `../amazon-seo/keywords/<category>.json` (same file
amazon-seo and flipkart-seo use) as your baseline, then confirm with a real Google signal before finalizing:
- Google Autocomplete via `javascript_tool`, same pattern as `flipkart-seo`'s autosuggest pull — seed with the
  core terms from the keyword JSON plus "buy", "online", "india" modifiers (how people actually search on
  Google vs. inside a marketplace's own search box).
- Google's "People also ask" / related searches on a live SERP for the core term, read via the browser tools —
  useful for long-tail phrases to work into the product description body text.

## Product page meta

- **Meta title** (≤ 60 chars so it doesn't truncate): `<Design/Colour> Glass Bangles Online | Bangle Bliss`
  — lead with the searchable product words, brand name last. Never stuff keywords or repeat words.
- **Meta description** (≤ 155 chars): one sentence of the real benefit + a soft CTA. Include the set count and
  the primary buyer intent word (e.g. "wedding", "gift") naturally — this is copy for a human reading a search
  result, not a keyword dump. Never promise a discount/price that isn't live (Shopify theme can show stale copy
  after a price change).
- **URL handle**: lowercase, hyphenated, short, matches the core search phrase — e.g.
  `/products/kundan-glass-bangles-ruby-red`. Never change a handle on an already-indexed live product without
  a 301 redirect (Shopify does this automatically when you edit the handle in Admin — verify the redirect was
  created, don't assume).

## Structured data (Product schema)

Confirm the theme emits `Product` JSON-LD (most Shopify themes including Horizon do by default) with `name`,
`image`, `description`, `sku`, `brand`, `offers.price`, `offers.priceCurrency` (INR), `offers.availability`,
and `aggregateRating`/`review` once reviews exist. Check via Google's Rich Results Test or by reading the page
source for `application/ld+json` — don't assume it's correct without checking a live product page.

## Image alt text — must satisfy shopify-variant-photos too

Alt text has two jobs at once on this store: SEO relevance, and the variant-gallery-filter mechanism from the
`shopify-variant-photos` skill (alt text must *start* with the exact option value verbatim, e.g. `Ruby Red`).
Satisfy both in the same string — the pattern from that skill already allows this:
```
{Exact Option Value} {product descriptor with keywords} - {shot type}
```
e.g. `Ruby Red kundan glass bangles set of 4 for women - lifestyle shot`. Never sacrifice the leading option
value for a "better" SEO phrase — that breaks the gallery filter silently (see `shopify-variant-photos` for
the failure mode). Read that skill before touching any product's image alt text.

## Collection pages

- Collection title/description should target the category term (e.g. "Glass Bangles for Women"), with a short
  (2-3 sentence) intro paragraph above the product grid — collections with zero body text rank worse for the
  category term itself.
- Internal links: product pages should link to their collection and to 1-2 related products (complementary
  colours/designs) — helps Google crawl depth and buyer discovery alike.

## What changes per product vs. what stays constant

- **Per product**: meta title, meta description, URL handle, alt text, structured data values (sku, price,
  availability).
- **Store-wide constants**: brand name suffix in meta titles, JSON-LD `brand` value, currency, the collection
  intro-paragraph pattern.

## Verifying it worked

Don't claim an SEO change "worked" from reasoning alone — check:
1. Google Search Console (if connected) for the page's impressions/clicks/average position before and after.
2. A live `site:banglebliss.in <product name>` search to confirm the page is indexed with the new title/meta.
3. Rich Results Test for structured-data errors.
If none of these are available in a given session, say so explicitly rather than asserting the change improved
ranking.
