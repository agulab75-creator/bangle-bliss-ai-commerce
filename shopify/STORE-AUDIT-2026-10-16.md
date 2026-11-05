# Bangle Bliss store audit — 16 Oct 2026

Done with the `indian-ecommerce-builder` skill scorecard, on banglebliss.in at 375px mobile and desktop,
plus the live Horizon theme (#<id>) and Admin API data. Karwa Chauth is Thu 29 Oct: 13 days left.

## What already works
- Clear festive hero ("KARWA CHAUTH EDIT — Bangles that celebrate you") with one CTA.
- Trust strip: Cash on Delivery · Delivery in ~5 days · 7-day returns · Secure checkout.
- COD + delivery in the announcement bar. Floating WhatsApp button with a per-product prefilled message.
- Product pages for the 3 glass ranges are strong: 13–15 colours with per-colour photos, size guide in cm,
  colour-pairing copy, FAQ, MRP ₹1,200 → ₹599, keyword-rich titles.
- Fonts (Playfair + Lato) and the cream/maroon palette already read premium.

## What's not working (ranked: impact × effort)

| # | Problem | Evidence | Impact | Fix |
|---|---|---|---|---|
| 1 | **Your 3 main ranges (KSG, GVK, KMS: 810 units of stock) are in no curated collection** | Collections match tags `glass`, `festive`, `bridal`, `bestseller`; these products use `glass bangles`, `festive bangles`, `bridal bangles` | H | Make collection rules match both tag spellings; add Kundan + Kadas + New Arrivals collections |
| 2 | Homepage "Featured pieces" shows the 4 old temple/ghungroo pieces, not the glass range | `bestsellers` collection = tag `bestseller` | H | Feature the glass ranges; tag/rule fix above |
| 3 | No welcome offer / first-order discount, no email or WhatsApp capture besides the footer field | 0 discounts in Admin | H | 10% first-order popup + code |
| 4 | Karwa Chauth is only words: no deal, no date, no "order by" cut-off | Hero + bar text only | H | Festive offer banner with real countdown to 29 Oct and delivery cut-off |
| 5 | Product cards show "Sale" instead of "50% OFF"; prices read "Rs. 599.00" | card badge + shop money format | M | % OFF badge (theme); money format `₹{{amount_no_decimals}}` (Settings → General → Store currency → Change formatting) |
| 6 | No hover feedback on cards (theme setting `card_hover_effect: none`), no second image on hover | settings_data.json | M | Lift + image swap + soft zoom (CSS, reduced-motion safe) |
| 7 | No Instagram on the site (only a footer icon) — your audience lives on @bangle_blissofficial | Homepage | M | Instagram section: live feed via a token-holding proxy, manual posts as fallback |
| 8 | Category tiles are big rectangles; no shop by colour/occasion/price | Homepage | M | Circular category row + shop-by-colour swatches |
| 9 | No reviews anywhere | — | H | Install Judge.me (free plan), ask first buyers for photo reviews |
| 10 | PDP gallery shows 58 dots on mobile for one product | KSG page | M | The unpublished "variant media fix" theme fixes the gallery filter; it's merged into the new theme |
| 11 | No free-shipping threshold or cart progress bar | Cart | M | Decide threshold (₹499 is the Indian norm; your AOV is ~₹599) |
| 12 | Compliance gaps: grievance officer, GST no., seller address not on site | Footer / policies | M | Fill `docs/policies-draft.md` items, add to footer |
| 13 | 4 old products track no stock (inventory 0 but sellable) | Admin | L | Confirm they're in stock or set tracking |
| 14 | Size chart differs from common charts (2.4 = 6.0 cm here vs 5.7 cm elsewhere) | PDP | L | Fine if measured from your stock; keep one chart everywhere |

## Built in this pass

**Theme** "Bangle Bliss - Festive 2026 (preview)" (#<id>, unpublished), local copy `theme-festive/`.
Preview: https://banglebliss.in/?preview_theme_id=<id> · Editor: admin → Online Store → Themes.
Based on the "variant media fix" theme (live theme + the 14 Oct gallery fix).

| File | What |
|---|---|
| `sections/bb-festive-offer.liquid` | Karwa Chauth banner: code KARWA15 tap-to-copy, live countdown to 29 Oct 6 pm IST, "order by Sat 24 Oct" cut-off, auto-hides after 30 Oct |
| `sections/bb-category-circles.liquid` | Circular shop-by-category row, gold ring draws on hover, swipe row on phones |
| `sections/bb-shop-by-colour.liquid` | 12 glass-bead colour swatches → store search |
| `sections/bb-instagram.liquid` | Instagram grid: live feed via proxy, fallback to posts/collection photos, hover captions |
| `blocks/bb-offer-callout.liquid` | Product page: "Buy any 2, get 15% off · 2 for ₹1,018" + WELCOME10 box |
| `snippets/bb-welcome-popup.liquid` | 10% first-order popup (12 s / exit intent, once a week), email → reveals WELCOME10, side tab to reopen |
| `snippets/bb-discount-badge.liquid` | "50% OFF" instead of "Sale" on cards |
| `assets/bb-festive.css` | Card lift + soft zoom, headings, reduced-motion support |
| `instagram-proxy/` | Cloudflare Worker + setup README for the live Instagram feed |

Also: homepage reordered (hero → trust → circles → Karwa banner → Karwa favourites → colours →
bestsellers → story → Instagram), announcement bar, mobile quick add on, PDP tick icons fixed
(the live site shows "¹3�a0" before each trust line).

**Store data (live now)**
- Discounts: KARWA15 (15% off, 2+ items, 16 Oct 2:30 pm → 29 Oct 11:59 pm IST, all customers);
  WELCOME10 (10% off, one use per customer, no end). They don't combine.
- Collections: Glass Bangles, Bridal Edit, Karwa Chauth Edit, Featured Pieces now also match the glass
  ranges' tags. New: Kundan Glass Bangles, Kadas, New Arrivals.

## Still open (your call / your hands)
1. Publish the preview theme (Online Store → Themes → Publish) after a look on your phone.
2. Money format → `₹{{amount_no_decimals}}` (Settings → General → Store currency → Change formatting).
3. Kundan Multi Stone: 12 raw "original photo" shots sit before the studio shots, so cards show a grey photo;
   it also has no compare-at price, unlike the other two ranges.
4. Main menu: add Kundan, Kadas, New Arrivals (Online Store → Navigation).
5. Install Judge.me (reviews) and enable Colour/Size filters in Search & Discovery.
6. Instagram live feed: follow `instagram-proxy/README.md`, paste the Worker URL in the section.
7. Grievance officer, GST no., seller address in the footer (see `docs/policies-draft.md`).

## Update 16 Oct, afternoon (theme is now LIVE)
- You published the festive theme (#<id>, renamed "Bangle Bliss - Festive 2026"); later changes were tested on
  "Bangle Bliss - Animated hero (test)" (#<id>), then pushed live.
- Karwa Chauth Edit = only the 3 glass ranges (tag `karwa chauth bangles`). KARWA15 now applies only to that collection
  (2+ items, 15% off). The product-page Karwa offer shows only on those products.
- New animated hero `sections/bb-bangle-hero.liquid`: canvas-drawn kundan glass bangle stack (spin, sparkles, light sweep,
  7 colour swatches), whole stage links to the Karwa edit; ~60 fps, pauses off-screen, still frame for reduced motion.
  The old photo hero is disabled in index.json, not deleted.
- Kundan Multi Stone: 11 grey raw photos detached (still in Files); Crystal Multi Stone raw kept, moved last.
- Main menu: Karwa Chauth Edit, Glass Bangles (Kundan / All), Kadas, Ghungroo Chuda Sets, Bridal Edit, New Arrivals, Shop All, Contact.
- Storefront prices show ₹599 (theme). Checkout still shows "Rs." until the admin money format is changed.
- Instagram: no Meta account connected here is linked to @bangle_blissofficial, so the live feed still needs the README steps.

## Update 16 Oct, evening
- The animated canvas hero was removed (`bb-bangle-hero.liquid` deleted) at the owner's request. It was replaced by
  `sections/bb-hero-slider.liquid`: 4 photo slides, each linked to a product colour (variant URL, size 2.6), with price
  and "Shop now", auto-advancing every 5 s, swipeable.
- Slide images: the original `bb-hero-festive.jpg` plus 3 new Karwa Chauth scenes generated with the Shopify Magic
  pipeline (`jobs/kc-hero-*`, `jobs/apply_kc_hero.py` rebuilds the slider): KSG Ruby Red hand + thali,
  GVK Cherry Red thali under the moon, KMS Wine Maroon shringar flat-lay.
- Judge.me installed (free plan): app embed on, review widget on product pages above recommendations. No reviews yet;
  real ones go in via `reviews-import/`.
