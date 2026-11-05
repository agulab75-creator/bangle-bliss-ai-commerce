# Image ↔ Product Map — Bangle Bliss

**Read this first in any new session before touching `raw/`, image generation, or the glass-bangle
Shopify products.** It documents how the reorganized `raw/` photos map to live Shopify products,
what's missing, and what's already been decided. The machine-readable twin is
`IMAGE_PRODUCT_MAP.json` (same facts, structured for scripts).

Store: `your-store.myshopify.com` ("Bangle Bliss"). Shopify CLI (`shopify store execute`) is
authenticated on this machine — no login needed for GraphQL calls.

## The three bangle designs

`raw/` is organized into 3 folders by **physical design**, confirmed by visually inspecting
sample photos from each (not just by number):

| raw/ folder | Visual design | Shopify product | Handle | SKU prefix |
|---|---|---|---|---|
| `Design !` (really "Design 1" — Shift-stuck typo) | Plain faceted glass, one round kundan stone per facet, evenly spaced | **Kundan Stone Glass Bangles for Women, Set of 4** | `kundan-stone-glass-bangles-set-of-4` | `KSG-` |
| `Design #` (really "Design 3") | Mixed stone shapes/colours per bangle — round + teardrop, red/green accent stones | **Kundan Multi Stone Glass Bangles for Women, Set of 4** | `kundan-multi-stone-glass-bangles-for-women-set-of-4-12-colours` | `KMS-` |
| `painted` | Hand-painted gold vine/leaf motif + single kundan stone | **Gold Vine Kundan Glass Bangles for Women, Set of 4** | `gold-vine-kundan-glass-bangles-set-of-4` | `GVK-` |

Product GIDs:
- KSG: `gid://shopify/Product/<id>`
- KMS: `gid://shopify/Product/<id>`
- GVK: `gid://shopify/Product/<id>`
- Royal Blue Gold Leaf (being merged into GVK as its 15th colour — see below): `gid://shopify/Product/<id>`

Each colour has 3 size variants (2.4 / 2.6 / 2.8) and normally 4 product shots: white studio,
lifestyle, worn-on-hand, macro close-up. Generation pipeline: raw photo → Shopify Magic AI editor
(browser-automated via `execution_agent.py` / `e2e_pipeline.py`, NOT the local `gen_images.py`
Gemini script — there is no `GEMINI_API_KEY` in `.env`, only `HF_TOKEN`) → 4 styled shots →
uploaded + attached to the colour's variants.

## raw/Design ! → KSG (Kundan Stone Glass) — number map

| image # | colour | KSG SKU | image status |
|---|---|---|---|
| bangle 1 | (test/original, not a colour) | — | n/a |
| 2 | Sky Aqua | KSG-AQU | ✅ complete (4 shots) |
| 4 | Parrot Green | KSG-PGR | ✅ complete |
| 6 | Coral Peach | KSG-COR | ✅ complete |
| 8 | Orchid Pink | KSG-ORC | ✅ complete |
| 9 | Mint Green | KSG-MNT | ✅ complete |
| 10 | Magenta | KSG-MAG | ✅ complete |
| 11 | Ruby Red | KSG-RED | ✅ complete |
| 12 | Plum Wine | KSG-PLM | ✅ complete |
| 13 | Emerald Green | KSG-EMR | ✅ complete |
| 14 | Maroon | KSG-MRN | ✅ complete |
| 40 | Rust Orange | KSG-RST | ✅ complete — 4 shots generated, uploaded, attached |
| 46 | Lemon Yellow | KSG-LMY | ✅ complete — 4 shots generated, uploaded, attached (wrist shot regenerated once after a duplicate-image QC failure) |
| 5 | Lime Green *(new)* | KSG-LIM | ✅ complete — variant created, 4 shots generated, uploaded, attached |
| 15, 16 | *(duplicate of Mint Green, image 9)* | KSG-MNT | ℹ️ Correction: visually identical to the existing Mint Green — these are extra/duplicate shots, not a new colour. No action needed. |
| 7 | Royal Blue | *(was its own product; now merging into GVK, not KSG)* | see Royal Blue section below |

**Status: ✅ DONE (2026-10-07).** KSG now has 13 live, fully-imaged colours: the original 10 plus
Rust Orange, Lemon Yellow, and the new Lime Green. Title updated to "(13 Colours)", description's
colour list and count copy corrected (also removed 8 colour names that were copy-pasted from KMS
and never actually existed as KSG variants: Bottle Green, Ivory Multi Stone, Lavender Purple, Mint
Multi Stone, Mustard Gold, Rani Pink, Royal Purple, Turquoise), tags cleaned up to match (removed
those 8 + "multicolor", added "lime green").

**Still outstanding — needs manual cleanup in Shopify admin:** KSG's media gallery still has ~10
orphaned raw/unstyled uploads at the end (`bb-glass-image-2.jpg`, `bb-glass-image-5.jpg`,
`bb-glass-bangle-1.jpg`, `bb-glass-image-6/8/9/10/15/16.jpg`, media GIDs <id>,
<id>, <id>, <id>, <id>, <id>, <id>,
<id>, <id>, <id>) — leftover from earlier attempts, not attached to
any variant, safe to delete. An attempt to delete them via the Admin API in this session was
blocked by a permission guardrail (destructive external write); detach/delete them manually from
Settings → Files or the product's media gallery in Shopify admin.

## raw/Design # → KMS (Kundan Multi Stone) — number map

KMS has exactly 12 live colours (matches its title). Verified against `ksg_more_map.json` /
`magic_sources_ksg.json` (historical mapping files — accurate for 11 of these; 2 entries in those
files, `rust-orange`/`image 40` and `lemon-yellow`/`image 46`, turned out on visual inspection to
actually be the *plain single-stone* KSG design, not multi-stone, and were correctly **not** used
on KMS — see KSG section above).

| image # | colour | KMS SKU |
|---|---|---|
| 31 | Ivory Multi Stone | KMS-IVM |
| 32 | Turquoise | KMS-TRQ |
| 33 | Rani Pink | KMS-RNP |
| 34 | Mustard Gold | KMS-MUS |
| 36 | Mint Multi Stone | KMS-MTM |
| 38 | Lavender Purple | KMS-LVP |
| 41 | Bottle Green | KMS-BTG |
| 44 | Royal Purple | KMS-RYP |
| 47 | Wine Maroon Multi Stone | KMS-WMM |
| 49 | Dusty Pink Multi Stone | KMS-DPM |
| 50 | Apple Green Multi Stone | KMS-APG |
| *(unclear)* | Crystal Multi Stone | KMS-CRM |

**Open issue, not yet fixed:** KMS's "Crystal Multi Stone" variant (`KMS-CRM`) product-gallery
image is `src-gold-vine-kundan-crystal-multi.jpg` — that's the **GVK (painted)** product's Crystal
Multi Stone photo, reused by name coincidence, not a real KMS multi-stone-pattern photo. The
correct raw source is still unidentified among the unmapped `Design #` numbers: `19, 35, 37, 39,
42, 43, 45, 48`. Checked so far: 19 = pale pink/blush multi-stone, 35 = rainbow multicolour set,
37 = teal multi-stone, 42 = amber/orange multi-stone, 48 = rani-pink-adjacent — none are a clear
crystal/transparent multi-stone bangle. Still unresolved; needs either a closer look at the
remaining numbers (39, 43, 45) or a user decision on what "Crystal Multi Stone" should actually
show.

KMS inventory is intentionally 0 across all variants (user confirmed — not live/stocked yet).

**Status: ✅ DONE (2026-10-08) for the other 11 colours' photography.** Ivory Multi Stone,
Turquoise, Rani Pink, Mustard Gold, Mint Multi Stone, Lavender Purple, Bottle Green, Royal Purple,
Wine Maroon Multi Stone, Dusty Pink Multi Stone, Apple Green Multi Stone each now have a full
4-shot set (44 images total) generated via `jobs/kms-<slug>/` and attached to KMS's media gallery.
Generation ran across **4 parallel browser profiles** (`.magic-profile` + cloned
`.magic-profile-g2/g3/g4`, caches stripped so each clone is ~10MB instead of ~400MB) to speed things
up — `execution_agent.py` gained a `--profile` flag for this. A separate `qc_agent.py` script
(pre-existing in the project, not written this session) ran an independent AI quality pass on every
generated image and genuinely caught bad generations (e.g. Bottle Green's first attempt came out
cream-coloured with hallucinated stones) — those got regenerated and the fixed versions are what's
live now, verified by direct visual inspection of the live Shopify CDN URLs on 2026-10-08.

**Bug found and fixed 2026-10-08:** all 44 of these images had been uploaded and attached to the
**wrong product** — they were sitting on KSG's media gallery instead of KMS's (KMS had only its 12
raw source photos, no generated shots at all). Root cause not fully diagnosed since it happened in
a compacted part of a prior session, but likely an upload script that hardcoded the wrong product
GID. Fixed by: `fileUpdate(referencesToAdd: [KMS])` on all 44 media IDs, then
`fileUpdate(referencesToRemove: [KSG])` on those same 44 **plus** 8 further images (an earlier,
superseded duplicate generation of KSG's own Rust Orange/Lemon Yellow that had also ended up on
KSG's gallery alongside the correct, already-verified set). KSG's media count went 122 → 70; KMS's
went 12 → 56 (12 originals + 44 generated). The 8 duplicate KSG images were only detached, not
deleted (file deletion needs the user to do it manually in Shopify admin, same as the older
orphaned-raw-images item above) — they're unreferenced but still exist in the file library.
**When writing any future per-product upload script, always double-check the target product GID is
the one you think it is** — this bug would have been caught immediately by a single verification
query after upload, which is now standard practice (see the "always visually inspect" note below).

## raw/painted → GVK (Gold Vine Kundan) — number map

GVK already has all 14 of its colours live, each sourced from named files (not numbered) in
`source-crops/src-gold-vine-kundan-*.jpg`, listed in `magic_sources.json`:

lime, lavender, crystal-multi, sea-green, forest, purple, crystal, multicolour, amber, emerald,
cherry, moss, ivory, yellow.

`raw/painted`'s 14 non-Royal-Blue numbered photos (`3, 17, 18, 20–30`) line up count-for-count with
these 14 existing colours — they're almost certainly the original uncropped sources behind the
already-used `src-gold-vine-kundan-*.jpg` crops, just archived here under their original shoot
numbers. **No new product work needed from these** — treat `raw/painted` as "already fully
represented in Shopify," not a backlog.

Two of GVK's 14 colours were missing 3 of their 4 shots (only had the white-studio shot):
**Ivory Cream** (`GVK-IVC`) and **Lemon Yellow** (`GVK-YEL`).

**Status: ✅ DONE (2026-10-07).** Generated the missing lifestyle/worn-on-hand/macro shots for
both via `jobs/gvk-ivory-cream/` and `jobs/gvk-lemon-yellow-vine/` (used
`source-crops/src-gold-vine-kundan-ivory.jpg` / `-yellow.jpg` as sources, since `raw/painted` has
no per-colour numbering for GVK), uploaded and attached via `upload_gvk_gapfill.py`
(state tracked in `jobs/upload_state_gvk.json`). One shot (Ivory Cream's lifestyle) came back on
the first try as a plain studio-style shot instead of the requested velvet/marigold festive scene —
caught by visual inspection, fixed by rewriting the prompt to be more explicit ("no plain white or
grey background", overhead flat-lay framing) and re-running.

### Royal Blue merge (user-approved)

`raw/painted/image 7.jpeg` = Royal Blue, same gold-vine-leaf design family as GVK, but was built as
its own standalone product ("Royal Blue Gold Leaf Kundan Glass Bangles",
`gid://shopify/Product/<id>`) instead of a GVK colour. **User decided: merge it into GVK
as a 15th colour** (`GVK-RBL`), reusing its existing 4 images, then archive the standalone product.

**Status: ✅ DONE (2026-10-07).** `GVK-RBL-24/26/28` variants created (₹599, inventory 10 at the
Daryaganj location, matching the rest of GVK), the 4 existing Royal Blue shots
(`bb-glass-image-7*.png` — studio/lifestyle/hand/macro, media GIDs <id> /
<id> / <id> / <id>) attached to GVK's media gallery, GVK title
updated to "(15 Colours)", description's "Choose your colour" list and colour-count copy updated,
tags `royal blue` / `royal blue bangles` / `blue bangles` / `gold leaf bangles` added. The
standalone Royal Blue product (`gid://shopify/Product/<id>`) was set to **ARCHIVED**
(not deleted, so order history is preserved) rather than left ACTIVE.

## Decisions already made (2026-10-07)

- Images 5, 15, 16 (KSG) → image 5 became new colour "Lime Green"; 15/16 turned out to be duplicate
  shots of the existing Mint Green, not new colours (corrected after visual inspection).
  **Status: ✅ done.**
- Royal Blue product → merge into GVK as colour #15, then archive the standalone product.
  **Status: ✅ done.**
- "Green Studded Glass Bangle Set (Test)" draft product → **leave alone**, not part of this cleanup.
- KMS inventory (currently 0 on all variants) → **leave at 0**, intentional.

## Image generation pipeline — used successfully (2026-10-07)

Rust Orange, Lemon Yellow, and Lime Green were all generated via the Shopify Magic AI editor,
driven by `execution_agent.py` (Playwright automation against the logged-in `.magic-profile`
browser profile). Ran as `python execution_agent.py "jobs/<name>" --workers 1` per colour,
sequentially, in the background — each colour took roughly 10-15 minutes for 4 shots. One shot
(Lemon Yellow's "worn on hand") initially came back as a duplicate of the lifestyle shot — a
Shopify Magic / download-timing glitch, not a prompt problem — caught by visually inspecting every
generated image before upload, fixed by resetting that one job item to `pending` and re-running.
**Always visually inspect generated images before uploading** — file-size comparison
(`ls -la jobs/*/generated/`) is a fast way to flag likely duplicates (two shots with identical byte
size are almost certainly the same image saved twice).

`gen_images.py` (direct Gemini API) remains unusable — no `GEMINI_API_KEY` in `.env`, only
`HF_TOKEN`.

Upload + attach to Shopify was done with `upload_new_ksg_colors.py` (one-off script modeled on
`upload_images.py`), which uploads `jobs/<name>/generated/*.png`, creates Shopify Files, waits for
`READY`, then attaches via `fileUpdate(referencesToAdd: [KSG product gid])`. Progress is tracked in
`jobs/upload_state.json` (keyed by `<job-dir>/<filename>` → media GID) so it's safe to re-run.

## Local folder map

- `raw/Design !`, `raw/Design #`, `raw/painted` — original full-size photos, organized by design
  (this session's reorg). Treat as read-only source material.
- `source-crops/` — cropped versions of raw photos. Some renamed to final colour slugs
  (`src-gold-vine-kundan-*.jpg`, `src-kundan-stone-glass-*.jpg`), others still numbered
  (`image_N.jpg`, `ksg_NN.jpg`, `new_NN.jpg`) from before the final name was decided.
- `jobs/<job-name>/` — per-colour generation jobs for the Shopify-Magic browser pipeline
  (`original/`, `prompts.json`, `generated/`, `approved/`, `rejected/`, `status.json`,
  `image_queue.json`). Only `jobs/bangle 1` existed before this session (an incomplete test run).
- `final-images/`, `output/` — old/experimental generation attempts (Gemini API script, Modal
  Flux/Hunyuan tests). Not part of the live pipeline; ignore for product work.
- `magic_sources.json` (GVK colour → media GID map), `magic_sources_ksg.json` (KMS colour → media
  GID map, now 1 ahead of the live product — see KMS section), `ksg_more_map.json` (old raw-number
  → KMS-colour map, 2 entries now known wrong), `magic_files.json` (KSG colour-number →
  Shopify-uploaded media GIDs, 4 per colour) — historical mapping files from earlier sessions, now
  superseded by this document for anything they disagree on.

## 2026-10-16: KMS raw photos detached
The 11 "- original photo" images on Kundan Multi Stone (KMS) whose colour has a white-studio shot were detached
from the product with `fileUpdate referencesToRemove` (the files are still in Shopify Files: `src-kundan-stone-glass-*.jpg`).
The Crystal Multi Stone original stays, moved to the last position, because it's the only photo for that
colour and its 3 variants point to it. Featured image is now "Ivory Multi Stone ... - white studio".

## 2026-10-16: Karwa Chauth hero images (homepage only, not attached to products)
Generated with `execution_agent.py` from white-studio sources, jobs `jobs/kc-hero-ksg-ruby`, `kc-hero-gvk-cherry`, `kc-hero-kms-wine`.
Used on the homepage slider: `bb-glass-image-11_9c5df85a-…png` (KSG Ruby Red, hand + thali),
`gold-vine-kundan-cherry-white-studio_f0e2c521-…png` (GVK Cherry Red, moon), `kundan-stone-glass-wine-maroon-white-studio-v3_d4c11cd0-…png`
(KMS Wine Maroon, shringar). Unused extras in Files: `bb-glass-image-11_e3c2423d-…png`, `gold-vine-kundan-cherry-white-studio_09bf9cd3-…png`.
