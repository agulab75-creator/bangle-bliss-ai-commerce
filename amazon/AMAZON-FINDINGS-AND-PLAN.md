# Amazon.in: why impressions dropped, what the old winners did, what to do with Silk Thread Bangles

Date: 2026-10-19. Brand `bangle bliss`, Amazon.in. Written for the next agent and for the owner.
Sources: `BusinessReport-19-10-26.csv` (child item, 292 ASINs, date range not recorded); Brand Analytics > Search Query Performance (weekly wk 42/2026, monthly Mar and Apr 2026; May-Sep 2026 returned no data); old sheets in `My Bangle Bliss/bangle bliss/amazon/` (multi, dark multi, RAINDROP CRYSTAL, oxi ghunghro set update, shell ghunghroo); new sheets `amazon from claude/amazon-all-3-products-combined-v5.xlsm` and `My Bangle Bliss/stb/amazon-silk-thread-bangles.xlsm`.
Owner has never run Amazon ads. All traffic below is organic.

## 1. Result in one paragraph

The "Viral Kashmiri Ghungroo" listings carried almost all sales. They rode a trend (peak Mar 2026), then demand halved and the brand's share fell about 6x by Apr 2026, then the account was inactive May-Sep. The 69 new Kundan ASINs (GVK2/KMS2/KSG2, pack of 4, Rs 599) got about 103 sessions and 0 orders. Conversion is not the problem; the new listings are not being shown. The Silk Thread Bangles sheet repeats several choices of the Kundan sheets.

## 2. Numbers

| Family | ASINs | Sessions | Units | Conv. | Sales |
|---|---|---|---|---|---|
| Viral Kashmiri Ghungroo (multi, dark multi) | 68 | 13,534 | 189 | 1.4% | ~Rs 1.37 lakh |
| Raindrop | 37 | 1,225 | 11 | 0.9% | Rs 5.6k |
| New Kundan (GVK2, KMS2, KSG2) | 69 | ~103 | 0 | - | 0 |

Total in export: 16,224 sessions, 212 units, Rs 1.49 lakh. Best ASINs: 700-2,100 sessions, 1.1-3.5% unit-session %. Buy box 85-99%.

Brand Analytics, brand impressions (brand share):
- "kashmiri bangles for women": Mar 148,033 (0.83%) of 17.9M, search volume 664k; Apr 13,596 (0.14%), volume 366k.
- "kashmiri bangles": Mar 52,873 (0.83%); Apr 4,123 (0.16%).
- "viral bangles for women": Mar 11,402 (2.85%); Apr 2,097 (1.91%).
- "bangle bliss" (brand search): 1,077 impressions in Mar. Brand awareness is tiny.

Week 42 (2026-10-11 to 10-17), where the brand is seen: rust bangles set for women 102/5,234; rust orange bangles 55/6,043; dusty pink bangles 17/926; hot pink bangles 14/4,261; kundan glass bangles 15/1,358; karwa chauth bangles set 25/29,977 (0.08%); pink bangles 20/133,734 (0.01%); lavender 12/19,382; coral 21/4,880; mint green 9/4,247. Click rate when shown is 20-70%; purchases about 0. Few impressions is the issue.

## 3. What the old winning sheets did (and the new ones do not)

1. Title = the search phrase: "16pc Multi Color Glass Bangles Set Viral Kashmiri Ghungroo Chuda with Heavy Gold Guchha Charms Traditional Jewelry for Women". No brand prefix. New titles lead with the brand and a generic phrase.
2. Backend keywords were product terms: "viral kashmiri ghungroo heavy latkan kada guchha charm bracelet". New ones are festival/relative filler (rakhi, garba, wife mother sister).
3. One listing per design, variation theme size only (colour fixed). Reviews and sales concentrated. New sheets: colour x size, 33 children (STB) or 69 (Kundan).
4. Bullets sold the trend and the value ("trending on social media", "massive wrist volume without spending thousands on real gold", sound hook). New bullets are neutral.
5. Big set at a sharp price: 16pc, MRP 999 / price 499 (same price point as STB, so price is not the gap).
6. Five images from the Shopify CDN, stock 10 per variant, weight 100 g.

## 4. Diagnosis, ranked

1. Trend ended: demand fell, share fell.
2. New ASINs have no sales, reviews or click history; no ads to seed them; rank is zero.
3. Too many variants split a tiny signal.
4. 4-6 months inactive; old listings decayed.
5. Generic keywords on the Kundan sheets.
6. Rs 599 for pack of 4 is weak value next to Rs 499 for 12 (unverified).
7. Not checked: suppression, review counts, listing quality scores, competitor rank.

## 5. Flags on the Silk Thread Bangles sheet (`stb/amazon-silk-thread-bangles.xlsm`)

Structurally clean: 1 parent + 33 children (11 colours x 2.4/2.6/2.8), no duplicate pairs, Rs 499, stock 10, titles 93-101 chars, 5 bullets, backend keywords ~245 bytes. But:
- All 11 colours at once (repeats the Kundan fragmentation).
- Colour names do not match queries that give impressions (rust, rust orange, dusty pink, lavender, mint, hot pink). STB colours: Royal Blue, Crimson Red, Mustard Yellow, Coral Pink, Turquoise, Parrot Green, Rani Pink, Emerald Green, Golden, Orange, Wine Maroon. Coral, Rani (hot) pink and Orange (rust orange) are the closest. Rename only if the photo colour really fits.
- Title leads with brand + "Silk Thread Bangles", a phrase whose search volume is unverified.
- Backend keywords are generic filler; almost no colour or product phrases.
- No ads, no reviews.
- item_length = 1 cm looks like a thickness value in the wrong field; thickness 0.12 in unconfirmed; MRP column not re-checked in this audit.
- Mustard hero changed after the sheet was built; its image URL needs updating before upload.
- Owner confirmed: stock 10 per variant; weight/box size stay as they are (under 500 g).

## 6. Plan (needs owner OK before editing or spending)

1. Pull market-wide Brand Analytics > Search Terms for: thread bangles, silk thread bangles, silk thread churi, thread bangles set, rust bangles, dusty pink bangles, coral bangles, hot pink bangles. Pick the real lead phrase from volume, not guesses.
2. Rewrite STB titles starting with that phrase (old-winner style, no filler); put colour phrases in per-colour keywords; add a value hook to the bullets (set of 12 at Rs 499) and a trend/benefit angle only if true for this product. Do not copy "viral Kashmiri" - wrong product and demand halved.
3. Launch fewer colours first (3-4: the best match to rust/orange, coral/pink, hot pink, plus one more), or make each colour its own size-only listing like the old winners; add the rest after first sales.
4. Small Sponsored Products campaign (auto + exact on the lead phrases) for the first weeks. Ask the owner for the budget.
5. Refresh the old ghungroo listings (only proven sellers): check reviews, images, stock.
6. Decide whether to merge or retire the 69 Kundan children.
7. Re-check Brand Analytics weekly.

## 7. Working notes

- Owner asked for no screenshots in browser work (token cost): use page text / JS. Seller Central tab group is already logged in.
- Business Reports grid is virtualised; ask the owner to export CSVs.
- Brand Analytics monthly URL pattern: `.../brand-analytics/dashboard/query-performance?view-id=query-performance-brands-view&brand=21080477&reporting-range=monthly&monthly-year=2026&2026-month=2026-04-30&country-id=in`.
- Nothing has been uploaded or changed on Amazon, Shopify or Flipkart in this analysis.
