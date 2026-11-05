# Amazon A+ Content — research + plan (Bangle Bliss, amazon.in)

Researched 2026-10-17. Mostly third-party blogs plus Amazon's SP-API docs; sizes below are UNVERIFIED until
checked against the slot hints in Seller Central > Advertising > A+ Content Manager.

## Rules (what Amazon rejects)
- No prices/promos, guarantees, return/refund policy, shipping info, QR codes, contact details, external links.
- No unsubstantiated superlatives ("#1", "best", "guaranteed", "clinically proven"), no competitor names.
  Applies to text baked into images too.
- Max 4 quotes/endorsements, only from well-known publications/public figures.
- Review takes ~24-72 h. Rejected = fix and resubmit. Violations can pull the ASIN.

## What works / doesn't
Works (directional, agency data; Amazon cites roughly up to 8% lift for Basic, higher for Premium): big-type benefit
panels, size/fit guide, colour-range strip, varied module layouts, mobile-first (check at 375 px).
Doesn't: small baked-in text, dense desktop infographics, repeating one layout, unsubstantiated claims.
Premium A+ (video, hotspots, carousels) needs eligibility; Basic = up to 7 modules per document for sellers.

## Image pipeline (this folder)
1. Magic (Shopify) produces the scene shots via `execution_agent.py` (existing flow). Magic edits a source
   photo; it cannot hit exact pixel sizes or render reliable text.
2. `compose.py <PRODUCT> <Colour>` (Pillow) crops/lays out exact module sizes and draws all text itself:
   01 hero 970x600, 02 four-up 4x220x220, 03 detail 300x300, 04 size panel 970x600, 05 range strip 970x300.
   Output: `aplus/out/<PRODUCT>/<Colour>/`. JPEG RGB, under 2 MB.
3. Pilot done: KSG Ruby-Red. Copy deck is in compose.py; facts used: set of 4, sizes 2.4/2.6/2.8, 13 colours.

## Upload options
| Route | Verdict |
|---|---|
| SP-API A+ Content v2020-11-01 (createUploadDestinationForResource -> POST image -> validateContentDocumentAsinRelations -> createContentDocument -> postContentDocumentAsinRelations -> postContentDocumentApprovalSubmission) | Supported, scalable, but needs a developer profile + Product Listing role + self-authorized app, and a JSON module builder. Best for many colours. |
| Playwright on A+ Content Manager | Feasible for a pilot with a persistent profile where YOU log in (incl. 2FA) once; I never enter the password. Slower and brittle (UI changes), possible ToS grey area, so keep low-volume, human-paced. |
| Manual in A+ Content Manager | Fine for the first document; ~10 min. |

Recommendation: do KSG Ruby-Red manually once to learn the real slot sizes and approval behaviour; then reuse one
document across all colours of a product (A+ is per-ASIN/parent, so one document per design KSG/KMS/GVK is
enough, not per colour). Go SP-API if you will update often; Playwright only as a fallback.

## Open items
- Confirm slot sizes in the Manager; adjust constants in compose.py.
- Pick Playwright vs SP-API (needs your OK + a login/registration step that only you can do).
- KMS and GVK need their own copy and shots.
