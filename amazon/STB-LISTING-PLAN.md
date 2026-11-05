# Silk Thread Bangles (STB) - everything prepared, NOTHING LIVE yet (2026-10-19)

Product: Silk Thread Bangles with Gold Beads for Women, Set of 12 (11 colours). Sizes 2.4 / 2.6 / 2.8. MRP 1000, price 499. Parent SKU `STB`, child `STB-<COLOUR>-<24|26|28>` (33 SKUs).
Colours: Royal Blue RBL, Crimson Red RED, Mustard Yellow MYL, Coral Pink CRP, Turquoise TRQ, Parrot Green PGR, Emerald Green EMR, Rani Pink RNP, Wine Maroon WMR, Orange ORG, Golden GLD.

## Images
66 approved photos (6 per colour) in `stb/final/<colour>/`, marketplace versions (JPEG, pure-white hero) in `stb/market/<colour>/` + brand size chart as 7th. Hero = exactly 12 bangles (verified by `thread_count.py` + eye). Other shots look like a full dozen (not exact). Guide: `BANGLE-SHOT-GUIDE.md`.

## Shopify - DRAFT created
https://admin.shopify.com/store/your-store/products/<id>  (status DRAFT, not on any sales channel). 33 variants, price 499 / compare-at 1000, stock 10 each, each variant's featured photo = its colour's hero, 66 photos + size chart, alt text starts with the colour name (theme filters the gallery by colour). State: `stb/shopify.json`.
To go live: set Active, tick Online Store. Optional: collection "Silk Thread Bangles" (tag rule `thread bangles` - tag is already on the product).

## Amazon - sheet ready, NOT uploaded
`stb/amazon-silk-thread-bangles.xlsm`: 1 parent + 33 children, theme COLOR/SET_NAME, unique (Color, Set Name), titles `Bangle Bliss Silk Thread Bangles Set for Women, Pack of 12, <Colour>, Chudi for Wedding & Party`, Number of Items 12, Material Silk, price 499 / MRP 1000, qty 10, 7 images per child (hero, flat lay, worn x2, size chart, close-up, macro; all plain CDN links, all return 200), backend keywords <= 249 bytes. To publish: Seller Central > Add Products via Upload > upload > Validate > Submit.

## Amazon A+ - images + spec ready, NOT uploaded
`aplus/out/STB-global/` (5 modules 970x600), overview `aplus/out/STB-global-all.jpg`, spec `aplus/stb_global_spec.json` (asin = placeholder). Needs the parent ASIN, which exists only after the listing is live. Then: `python aplus/upload_aplus.py --spec aplus/stb_global_spec.json --resume --apply --submit` (ask first; submit is outward-facing).

## Flipkart - file filled and accepted by the uploader, NOT sent to QC
`stb/fk/<flipkart-catalog-file>.xls` (name must stay exactly as issued). 33 rows, Group ID STB, Flipkart-hosted images (5 per SKU incl. size chart), 11 unique Color values (Blue, Red, Yellow, Pink, Turquoise, Lime, Green, Magenta, Maroon, Orange, Gold), MRP 1000, price 499, pack of 12, 5 search phrases from live Flipkart autosuggest. UPDATE: the 9223 Chrome window closed after this was prepared, so the parked Seller Hub tab (and its green-tick state) is gone. The images are already hosted by Flipkart (URLs are in the file). To finish: Listings > Add Listings in Bulk > Bangles > Bangle Bliss > Create new listing > Upload filled template (the .xls above, name unchanged) > Send to QC.

## Please check (I did not invent these; they are copies or estimates)
1. **Stock** 10 per variant everywhere (copied from KSG). Tell me real quantities.
2. **Weights/dimensions**: Amazon item 250 g, package 10x10x10 cm 400 g; Flipkart 0.4 kg, 10x10x10 cm. Copied from glass-bangle rows, not measured on thread bangles.
3. **Item thickness** 0.12 in (about 3 mm) is an estimate. Item width 0.3 cm.
4. **HSN / tax**: confirmed by owner 2026-10-19 as HSN 7117, GST 3%. Amazon sheet already has HSN 7117; Flipkart file now has HSN 7117 and Tax Code GST_3.
5. **Amazon keywords**: Brand Analytics could not be reached (Chrome extension unresponsive) and Amazon autosuggest returned nothing, so Amazon backend keywords use the existing glass-bangle keyword file plus thread words. Flipkart phrases are real autosuggest.
6. **Shopify description** says delivery about 5 days, COD, 7-day returns (same text as KSG).
7. Flipkart MRP/price are 1000/499 as you said; Amazon sale price field left empty.
8. Closing the Flipkart tab loses the uploaded-file state; the images stay in Flipkart's host and the .xls can be re-uploaded.
