# Flipkart catalog automation (Bangle Bliss)

Everything here runs from `My Bangle Bliss/` with Python + Playwright / raw DevTools. Nobody has to click in Seller Hub.

## One-time setup
1. Start the automation Chrome (its own profile, already signed in to Google Drive and Seller Hub as banglebliss):
   ```
   "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9223 --user-data-dir="<project-dir>\.shopify_chrome_profile"
   ```
   If Seller Hub or Google asks to sign in, do it once in that window. Scripts never type passwords.
   Your everyday Chrome cannot be used: Chrome 155 rejects debugging connections to the default profile.
2. Leave that window open while scripts run. Do not click in it during a run.
3. **Comet works too** (Chromium 154, tested 18 Oct). It keeps automation completely out of Chrome:
   ```
   "%LOCALAPPDATA%\Perplexity\Comet\Application\comet.exe" --remote-debugging-port=9224 --user-data-dir="<project-dir>\.comet-profile"
   ```
   Sign in once to Google (<seller-email>) and Seller Hub in that Comet window, then run any script with
   `set FK_CDP_PORT=9224` (PowerShell: `$env:FK_CDP_PORT="9224"`). Every script reads FK_CDP_PORT; the default is now 9224 = Comet (set 9223 to use the Chrome window instead).

## The pipeline
| Step | Script | What it does |
|---|---|---|
| 1. Photos | `regen_setup10.py` + `regen_run10.py` | Generates missing shots from the RAW product photos with the Shopify Magic pipeline (`execution_agent.py`, one profile, sequential). |
| 2. Host | `fk_drive_v6.py`, `fk_drive_4w.py` | Uploads JPEGs to the public Drive folder "BB Flipkart v6 final" and writes `flipkart-images/drive-urls-v6.json` (direct `uc?export=view` links). |
| 3. Data | `flipkart from claude/flipkart-update-data.xlsx` | One row per Seller SKU: title, keywords, key features, colours, 5 image URLs. |
| 4. Catalog | `fk_quick.py download` | Seller Hub > Listings (category filter) > select all > Download Catalog File > newest file, one trusted click. |
| 5. Fill | `fk_fill_by_sku.py <in> <out> <data.xlsx>` | Writes the data into the catalog file by Seller SKU ID. Keeps Flipkart's exact file name. |
| 6. Upload | `fk_quick.py upload` | Listings > Uploads > Upload Catalog File (file set via DevTools). |
| 7. QC | `fk_qc_poll.py <REQ> 45 30` then `fk_qc_errfile.py <REQ>` | Polls the request until QC finishes, then downloads the error file and groups failure reasons. |

All Seller Hub steps use `fk_cdp_tab.py`: one temporary tab, real (trusted) mouse clicks, 1920 px viewport, closed afterwards.
Other tabs are never touched (the older Playwright `connect_over_cdp` approach had to wake every tab and made the window flicker).

## Flipkart rules learned the hard way (bangle_bracelet_armlet)
1. **Image hosting:** never cdn.shopify.com (random "image URL incomplete/invalid" + "Insufficient images count").
   Use Google Drive direct links (public folder) or Flipkart's own image uploader.
2. **Every image must show exactly one set of 4 bangles.** A "colours available" collage (11-14 sets) fails "Pack of".
3. **No size chart** in the product images ("Size chart images should not be provided as product image").
4. **No repeated photo** in one row: auto-rejected within an hour ("Duplicate images found").
5. **A blank image cell does not delete** the live image; to replace an image, send a different one.
6. **Colour words** must describe the photo (multi-stone sets => Multicolor, apple green => Green).
   **Color is an ID attribute and can NOT be edited on a live listing** (tested 18 Oct, request <request-id>:
   "Edits in the ID attributes for a product are not allowed"). If QC says a live listing's colour is wrong, the only
   fix is a NEW listing (new SKU, correct Color, its own Group ID so colours stay unique) and deactivating the old one.
   Pick Color carefully at creation: it is permanent. Uniqueness of Color + Pack of + Bangle Brand Size inside a
   Group ID is enforced on new listings.
7. **Lifestyle photo as main image is accepted** in this category.
8. File name must stay exactly as downloaded; rows you do not change come back "same as existing data" (harmless).
9. Only one edit per listing can be in QC; QC takes from under 1 hour (automatic checks) to ~12 hours (manual).
10. **Pack of is locked too** (tested 19 Oct, <request-id>). Since ~18 Oct night an automated image reviewer
    rejects image edits with "Pack of must reflect the number of items shown" even when the main image shows exactly
    4 bangles; changing Type to "Bangle" did not help. Escalate via Seller Support (draft: bangle bliss/flipkart-support-ticket.txt).
11. Variant grouping file (`Bulk Variant Groupings`) can only attach FSNs to a main FSN and copies the main FSN's
    attributes onto them; it cannot split a group.

## Official Seller API
Flipkart's Listing API v3 updates price, stock, shipping and similar listing fields, not product images, and needs API
credentials registered to the seller account. Seller Hub catalog files remain the only image route.
