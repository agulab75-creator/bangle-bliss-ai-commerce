# Amazon.in visibility findings (Bangle Bliss) — read before writing any new Amazon listing

Source: Seller Central exports/pages read on 2026-10-19. Brand `bangle bliss`, India.
Data used: `BusinessReport-19-10-26.csv` (Detail Page Sales & Traffic by Child Item, 292 ASINs, date range not recorded),
Brand Analytics > Search Query Performance (weekly wk 42/2026; monthly Mar 2026 and Apr 2026; May–Sep 2026 show "No data found").
**Owner has never run Amazon ads.** Every impression below is organic.

## 1. What worked (old listings)

| Family | ASINs | Sessions | Units | Conv. | Sales |
|---|---|---|---|---|---|
| "Viral Kashmiri Ghungroo" multi-colour / dark multi (16pc) | 68 | 13,534 | 189 | 1.4% | ~Rs 1.37 lakh |
| Raindrop | 37 | 1,225 | 11 | 0.9% | Rs 5.6k |
| New Kundan Multi Stone / Kundan Stone / Gold Vine (GVK2, KMS2, KSG2, pack of 4, Rs 599) | 69 | ~103 | 0 | – | 0 |

- Best ASINs: 700–2,100 sessions each, 1.1–3.5% unit-session %, Featured Offer ~99%.
- Total in export: 16,224 sessions, 212 units, Rs 1.49 lakh. Almost all of it is the ghungroo family.
- Buy box is fine (85–99%). Conversion on sessions that arrive is normal. **The problem is that the new listings get no sessions.**

## 2. Search demand: the peak was a trend

Brand Analytics, brand impressions vs total impressions:

| Query | Mar 2026 brand impressions (share) | Apr 2026 brand impressions (share) |
|---|---|---|
| kashmiri bangles for women | 148,033 (0.83%) of 17.9M | 13,596 (0.14%) of 10.05M |
| kashmiri bangles | 52,873 (0.83%) | 4,123 (0.16%) |
| ghungroo bangles | 10,248 (0.41%) | not in top rows |
| viral bangles for women | 11,402 (2.85%) | 2,097 (1.91%) |
| viral kashmiri bangles | 5,888 (3.06%) | – |

- Mar: query volume 664k for "kashmiri bangles for women"; Apr: 366k. Market demand fell and the brand's share fell about 6x.
- May–Sep 2026: Brand Analytics returns no data, i.e. no meaningful brand activity (owner was inactive 4–6 months).
- Brand-name search "bangle bliss" gave 1,077 impressions (53% share) in Mar: brand awareness is tiny, so branded search can't carry new listings.

## 3. Current state (week 42, 2026-10-11 to 10-17)

Top queries where the brand is seen (brand impressions / total):

- rust bangles set for women 102 / 5,234 (1.95%)
- hot pink bangles 14 / 4,261
- bangles karwa chauth 6 / 2,585
- rust orange bangles 55 / 6,043 (0.91%)
- dusty pink bangles 17 / 926 (1.84%); dusty pink bangles set for women 12 / 715 (1.68%)
- kundan glass bangles for women 3 / 966; kundan glass bangles 15 / 1,358
- karwa chauth bangles set 25 / 29,977 (0.08%)
- pink bangles 20 / 133,734 (0.01%)
- lavender bangles 12 / 19,382; coral bangles 21 / 4,880; mint green bangles 9 / 4,247

Observations:
- Click rate when shown is healthy (20–70%), cart adds 0–16%, purchases ~0. The few impressions are the issue, not the pull.
- **Colour-led queries (rust, rust orange, dusty pink, coral, lavender, mint, hot pink) are where this brand is visible.** Generic "kundan glass bangles" volume is small and crowded.
- Rust / rust orange queries have decent volume (rust orange bangles 217 score-volume rank 5) and brand share around 1–2%: cheapest wins.
- Karwa Chauth terms are huge (30k impressions on one query) but seasonal and the brand has ~0.1% share.

## 4. Diagnosis (ranked)

1. **Trend ended.** The old winners rode "Kashmiri ghungroo / viral bangles". Demand roughly halved Mar→Apr 2026 and the brand's share fell with it.
2. **New ASINs have no history.** No sales, no reviews, no click data → no organic rank. With no ads, nothing seeds them. 69 children and 3 parents spread tiny signal across too many ASINs.
3. **Inactivity.** 4–6 months of no activity decays rank on the old listings too.
4. **Generic keywords on the Kundan sheets** ("stylish navratri studded wedding combo bridesmaid…") vs the actual converting queries, which are colour + product phrases.
5. **Price/offer (unverified):** Rs 599 for pack of 4 is weak value next to Rs 499 for 12 (thread bangles).
6. Not checked: listing suppression, image/title quality scores, review count, competitor rank.

## 5. Rules for the next listing (Silk Thread Bangles, `stb/amazon-silk-thread-bangles.xlsm`)

- Put the **colour + exact search phrase in title and backend keywords** (rust, rust orange, dusty pink, coral, lavender, mint, hot pink). Drop generic festive filler.
- Title pattern: `Bangle Bliss Silk Thread Bangles Set of 12 for Women, <Colour>, with Gold Beads` — keep "Chudi for Wedding & Party" only if under length.
- Launch the 3–4 strongest colours first (rust/orange, dusty pink/coral, hot pink, mint/lavender), not all 11; add more once they have sales.
- Keep Rs 499 / MRP 1000, set of 12 as the value hook.
- Budget a **small Sponsored Products auto/exact campaign for the first weeks**: organic alone did not start ranking for the Kundan family. Ask owner before spending.
- Re-check Brand Analytics weekly; query list is in Search Query Performance (use page text, no screenshots — owner asked to save tokens).
- Confirm from owner: stock 10 per variant; weight/box dims stay as-is (under 500 g).

## 6. Still to do / open

- Pull Brand Analytics Search Terms (market-wide, not brand only) for "thread bangles", "silk thread bangles", "rust bangles", "dusty pink bangles" to validate volume.
- Check review count and listing health on the ghungroo ASINs; consider refreshing them since they are the only proven sellers.
- Decide whether to retire or merge the 69 Kundan children (GVK2/KMS2/KSG2) that have ≤10 sessions each.
