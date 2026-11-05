# Amazon keyword research files (amazon.in)

One JSON per product category (`glass-kundan-bangles.json` is the first). The sheet builder reads the file and fills the
249-byte Generic Keyword field with the most-searched words (rank order), skipping words already in the title.

## Data source (real, not guessed)
Seller Central (owner's logged-in Chrome, via the Claude-in-Chrome tools) > Brand Analytics > Search Analytics >
**Top Search Terms**, weekly. It returns **Search Frequency Rank** (1 = most searched). Amazon gives no absolute counts.
If Brand Analytics says "Access Required" or "No data", tell the owner; never invent ranks.

## How to pull terms (fast method, no clicking)
1. `tabs_context_mcp {createIfEmpty:true}`, then navigate to
   `https://sellercentral.amazon.in/brand-analytics/dashboard/top-search-terms?view-id=top-search-terms-default-view&reporting-range=weekly&weekly-week=<YYYY-MM-DD of the Saturday ending the latest week>&search-term-freeform=<keyword>&country-id=in`
   (the page's own default week is in its URL after the first load; use it).
2. Run this in the page with javascript_tool (rows come back sorted by rank, 25 per page):
```js
for(let i=0;i<40;i++){if(document.querySelectorAll('[role="row"]').length>2)break;await new Promise(r=>setTimeout(r,500));}
await new Promise(r=>setTimeout(r,1200));
JSON.stringify([...document.querySelectorAll('[role="row"]')].slice(2).map(r=>r.children[0].innerText.trim()+'='+r.children[1].innerText.trim()))
```
   Batch many keywords with `browser_batch` (navigate + javascript_tool pairs). Close the tab when done.
3. Keep only terms that truly describe the product (judge relevance; drop other materials/brands). Put them in `terms`.
   Put real-but-irrelevant ones (e.g. kangan, kashmiri, raindrop) in `searched_but_not_our_product`.
4. `python rebuild_priority.py <file>.json` to recompute the ranked word list.
5. Update `week`/`pulled`, then rebuild sheets (`build_combined_amazon.py` reads this file).

## Seed keywords per research round (substring filters)
Core: bangles, glass bangles, bangles set, bangles for women, chudi, churi, chudiyan, kundan, stone bangles.
Colours: red/pink/green/blue/purple/yellow/orange/white/maroon/multicolor + "bangles".
Occasions: bridal, wedding, karwa chauth, navratri, diwali, party wear, daily wear.
Modifiers: stylish, fancy, trendy, designer, latest, combo, girls, ladies, traditional.
For a NEW category (e.g. metal bangles, oxidised bangles, kada) copy this list swapping the material words, pull, and
save a new `<category>.json` in this folder BEFORE writing any title or keywords.

## Refresh cadence
Every 2 weeks (scheduled task "amazon-keyword-refresh"): re-pull every category file, diff against the saved ranks,
update the files, and report to the owner: terms that rose/fell by >30%, brand-new relevant terms, words to add or drop.

## Flipkart files
`flipkart-<category>.json` holds Flipkart autosuggest phrases (see `.claude/skills/flipkart-seo/SKILL.md` for the method). Flipkart gives no
numeric volume; the order of suggestions is the signal. The 2-week refresh task covers both marketplaces.
