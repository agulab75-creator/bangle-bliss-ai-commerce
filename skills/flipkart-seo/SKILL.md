---
name: flipkart-seo
description: Flipkart SEO and listing-update specialist for Bangle Bliss. Use whenever the user asks to improve Flipkart search visibility, titles, Search Keywords, Key Features, descriptions or images for Flipkart, to update live Flipkart listings, or to research Flipkart search terms. Pairs with flipkart-scale (template mechanics) and amazon-seo (shared keyword files).
---

# Flipkart SEO — Bangle Bliss (flipkart.com, bangle_bracelet_armlet category)

## What is different from Amazon
- **Search Keywords field = max 5 phrases**, `::` separated, full phrases a shopper types (the template's own example is
  `Red Casual Tshirt for Women::Black Mens Tshirt`). There is no 250-byte backend field. Choose the 5 highest-demand phrases
  that are true for the product. Words alone are weak; phrases matter.
- Searchable text lives in: **Product Title (col "Product Title")**, **Search Keywords**, **Key Features**, **Other Features**,
  **Description**, **Brand Color**, **Model Name** and the closed-list attributes (Color, Occasion, Ideal For, Type, Design...).
- `Color` is a closed list and must be unique per Group ID + size (see flipkart-scale). Put the real shade in Brand Color.
- **Images: JPEG only, RGB, >= 1000 px, and hosted where Flipkart's fetcher can reliably download them.**
  NEVER use cdn.shopify.com links (2026-10-16: 111 of 121 edit rows QC-failed "image URL incomplete/invalid ... use image
  uploader" + "Insufficient images count", at random, although every URL worked in a browser). What works, in order:
  1) Flipkart's own image uploader (`fkmpimages.flixcart.com/iu-pre-catalog-images-feed/...`, see section below and
  `flipkart_bulk_images.py`); 2) Google Drive direct links `https://drive.google.com/uc?export=view&id=<id>` with the file
  shared "Anyone with the link" (REQ3HN836JQLH passed 33/33 with these; a "restricted access" error means the share was not
  public). Main + Other Image URL 1-4 (5 images). The template's Image GuideLines sheet says the **primary image must be on a
  white background**, solo product, no props/text. Flipkart copies each image to its own CDN
  (`img1a.flixcart.com/fk-p-images-internalise/...`) on first QC, so **changing an image URL later only works if the listing
  is re-submitted/updated through a template**, not by editing the source file.
- "churi" means *churidar* (clothing) on Flipkart; never use it. "chudi bangle" and "chuda set bridal" are bangle terms.

## Research first (mandatory, same rule as amazon-seo)
Seller Hub has no search-volume report. The real demand signal is Flipkart's own search autosuggest (order = demand).
1. Check `../amazon-seo/keywords/flipkart-<category>.json` (`flipkart-glass-kundan-bangles.json` exists). If `pulled` is older
   than 3 weeks or the category is new, re-pull.
2. Method (Claude-in-Chrome, no login needed): open `https://www.flipkart.com/`, then with `javascript_tool`:
```js
const seeds=["glass bangles","bangles set","kundan bangles"]; const res={};
for(const q of seeds){const r=await fetch('https://1.rome.api.flipkart.com/api/4/discover/autosuggest',{method:'POST',
 headers:{'content-type':'application/json','x-user-agent':navigator.userAgent+' FKUA/website/42/website/Desktop'},
 body:JSON.stringify({query:q,marketPlace:'FLIPKART'})}); const s=JSON.stringify(await r.json());
 res[q]=[...s.matchAll(/"title":"([^"]+)"/g)].map(x=>x[1]); await new Promise(r=>setTimeout(r,250));}
window.__fk=res; JSON.stringify(res)
```
   Output is cut at about 1,000 characters per call, so read `window.__fk` back in slices of 5-6 seeds. Aggregate: a phrase at
   position 1-3 or under several seeds is high demand. Seeds: core terms, colours, occasions (bridal, wedding, karwa chauth,
   navratri), modifiers (stylish, fancy, trendy, combo, girls), plus the product's material (kundan, stone, crystal, glass).
3. Save to `flipkart-<category>.json` (same folder as the Amazon files). Refresh every 2 weeks (scheduled task
   `amazon-keyword-refresh` also refreshes Flipkart).

## Writing a row
- **Product Title**: `Bangle Bliss <Design> Glass Bangles Set for Women (Pack of 4) <Colour>`; first words = what shoppers type.
- **Search Keywords** (5): `<colour phrase>::glass bangles for women::bangles set for women::kundan bangles for women::stone bangles for women`
  where the colour phrase comes from `search_keywords_colour_phrase` in the keyword file (e.g. `green bangles for women`).
- **Key Features** (`::`): set of 4 glass bangles::kundan stones in gold-tone settings::<design detail>::size 2.4/2.6/2.8 options.
- Never claim what the product is not (not Kashmiri, not oxidised, not metal, not lac).

## Updating listings that are already live (verified 2026-10-16 in Seller Hub)
- Seller Hub > Listings > (filter Category = Bangle Bracelet Armlet) > set **Items / page = 100** > header checkbox > **This Page**
  (not "All Pages", that greys the option out) > **Downloads > Download Catalog File** > Downloads History > download icon.
  Result: an `E_bangle-bracelet-armlet_*.xls` file prefilled with every selected listing's FSN and current data (100 rows per file,
  so 121 listings = 2 files). It contains Product Title, Description, Search Keywords, Key Features, Brand Color and Main/Other
  Image URL 1-4. Image cells hold Flipkart's own `img.fkcdn.com` copies; writing a new public URL makes Flipkart re-fetch it.
- Fill with `fk_fill_by_sku.py <in.xls> <out.xls>` (matches Seller SKU ID; makes a backup). xlutils drops the VBA validation macro.
- Upload: **Listings > Uploads > Upload Catalog File > Select File**, then **Uploads > View Recent Uploads** for the QC report.
- Other menu items: Download/Upload Listing File (price, stock), Variant Grouping File. Seller Hub also needs the owner logged in.

## (older notes) Updating listings that are already live
- Image or text changes on live listings need a template round-trip: Seller Hub > Listings > bulk update / add listings
  (category bangle_bracelet_armlet) > download the template (for live listings prefilled with their FSNs) > fill by header
  name using `fk_fill_by_sku.py` > upload > read Flipkart's QC report (it returns the file with a status and
  "QC Failed Reason" per row). Fix every distinct error line, resubmit.
- The owner must be logged in to Seller Hub; the assistant cannot log in. If the page shows "Become an Online Seller"
  the session is logged out; ask the owner to log in, then continue.
- Remove variants that no longer exist (e.g. GVK-CRM) by deactivating them in Seller Hub (Listings > select > deactivate),
  not by deleting rows from the template.

## Hard rules
- MRP/price: owner decides (Amazon uses 599/1200; Flipkart rows were placeholders).
- Never write a Color that is not in the template's `Index` allowed list; never leave ID attributes blank.

## Lessons from the 2026-10-16 catalog update
- **Keep the downloaded file name EXACTLY as Flipkart issued it** (`E_bangle-bracelet-armlet_<id>_<ts>FK_BLK....xls`). Renamed copies give "Feed upload failed" and create no request.
- **Reading QC failures:** Seller Hub > Listings > Add New Listings > Bulk Listings > Edited > click the failed count > "Correct Errors" > **Request**, wait ~10 s, then **Last Requested File** downloads an .xls with the reason per row in column C ("QC Failed Reason"). The in-page detail view often renders blank; this file always has the text.
- **Result of the first update:** all 121 rows QC-failed ONLY on images: "[Main Image URL] ... incomplete/invalid ... use image uploader", "Insufficient images count". Titles/keywords/features were not the problem. Failures were intermittent per URL (shared size-chart URL failed 92/100, ~30 rows passed each slot) although every cdn.shopify.com URL returns 200 image/jpeg, so Flipkart's fetcher dislikes the host/volume. Flipkart's guideline sheet recommends Dropbox/Google Drive public links or its own image uploader.
- 8 rows returned "Data provided in edit request is same as existing data" (nothing to change).

## Image hosting that works: Flipkart's own image uploader (found 2026-10-16)
Seller Hub > Listings > Add New Listing > Add Bulk Listings > Bangles > brand "Bangle Bliss" > Create new listing shows **"Auto-filled Excel Template"**:
- *Upload from Google Drive* (paste a public Drive folder link) or *Upload from Device > Upload Images*: Flipkart ingests the photos and returns a template whose Main/Other Image URLs are Flipkart-hosted (`fkmpimages.flixcart.com/iu-pre-catalog-images-feed/...`). This avoids the "incomplete/invalid URL" failures seen with cdn.shopify.com links.
- On the Upload Images screen set the SKU ID, use **Re-use Images for Variant** for more sizes, then **Generate Catalog File** and Download. Always review the AI-filled attributes: it wrote diamond cut / "32 diamonds" for glass bangles (replace with NA), and it defaults Group ID to the first SKU.
- *Manual-filling Excel Template*: Download template (blank) / Upload filled template / **Send to QC** (this is the submit step).
- Keep the downloaded file name exactly. A 5th photo (size chart) must be included in the uploader to get a Flipkart-hosted link for Other Image URL 4.
