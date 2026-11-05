# Bangle Bliss shot guide (thread bangles first, applies to all bangles)

Written 2026-10-18 after the owner rejected the first creative set ("who holds a diya like that", "bangles floating in the air", "hung on a doorknob"). Read this before generating or approving any lifestyle image.

## 1. What the research says

Sources are mostly general jewellery and flat-lay tutorials plus stock-photo listings; nothing bangle-specific and authoritative, so the shot list below combines them with common sense.

- Flat lay = camera straight down (90 degrees), camera parallel to the surface, otherwise round bangles look oval. Use a focal length above ~35 mm. Place the hero off-centre (rule of thirds), a gentle curve or S-shape adds flow. [DIYPhotography](https://www.diyphotography.net/flat-lay-photography-tips/), [Expert Photography](https://expertphotography.com/flat-lay-product-photography), [Orbitvu](https://orbitvu.com/blog/how-shoot-flat-lay-clothing)
- Jewellery shot types: flat lay, close-up detail (1-2 per listing, "details are the most important aspect"), model shot for scale, macro (1:1). Soft light from two sides, foam core to fill shadows, no mixed colour temperatures. [Clipping Magic](https://clippingmagic.com/resources/photographing-your-jewelry)
- Stock libraries show the Indian bangle look: bangles scattered or stacked on silk (orange, teal, red velvet), marigolds and rose petals, a diya in the background, henna hands with a stack on the wrist, bridal hands layering bangles, brushed backdrops with shallow depth of field. [Adobe Stock](https://stock.adobe.com/search?k=indian+bangles), [Adobe Stock video](https://stock.adobe.com/search/video?k=bangles)
- Amazon main image: product only, pure white 255, fills >= 85% of the frame, 1000 px+ on the longest side. Jewellery may be shown worn only in later images. Secondary images: lifestyle, close-up of material and finish, one benefit per infographic. (Secondary sources, verify in Seller Central.) [Amazon image guide summary](https://mpsh.atlassian.net/wiki/spaces/SUC/pages/1335721987/Amazon+Image+Guidelines)

## 2. Physics rules (reject any image that breaks one)

1. Gravity: nothing floats. Every bangle rests on a surface, on a person, or on a real holder (see rule 6).
2. Bangles are rigid rings. They do not bend, melt into each other or pass through each other. Overlapping bangles must overlap believably (one rests on the other).
3. A loose bangle lying on a surface lies FLAT (ring on the surface) or leans against another bangle; it does not stand on its thin edge unsupported, except a short stack on its side that is clearly leaning on something.
4. A stack of bangles sits coaxially (like coins), not randomly tilted.
5. Worn bangles encircle the wrist, sit just above the wrist bone, and the arm passes through them. Hands: five fingers, natural anatomy, relaxed pose, no twisted wrists.
6. Allowed holders: a bangle stand pole with a base, a velvet bangle roll or cylinder, a plate or tray, the wrist. NOT allowed: hooks, door handles, candles, air.
7. Objects are handled the normal way: a diya sits in a brass thali or on a surface; flowers held by the stem; a dupatta edge pinched; a teacup by its handle. Nobody cups a flame in bare palms.
8. Shadows: every object has a contact shadow under it, light direction is the same for all objects.
9. One product set per image unless the shot is a colour-range image. Scale must be believable: a bangle is 6-7 cm across, a hand is about 17 cm long.
10. Thread bangles: matte-silky thread texture with a visible diagonal twist and small antique-gold beads scattered irregularly. Never glossy glass, never stones.

## 3. Count rule (owner decision 2026-10-18)

- White-background hero image: exactly 12 bangles, verified (`thread_count.py` reads 11.8-13.0 and a human glance agrees).
- Every other image: must LOOK like a full dozen (about 10-14 reads naturally), but may differ. In scattered and flat-lay shots count does not matter.
- Never show two sets in one image (the first bangle-stand render showed two towers).

## 4. Shot list per colour (aim for 6-7 images, listing order)

| # | Shot | Camera | Surface and props | Notes |
|---|---|---|---|---|
| 1 | White hero | eye level, front | pure white | exactly 12, Amazon main |
| 2 | Scatter flat lay | overhead 90 degrees | silk or velvet in a contrasting colour, a few marigold petals or jasmine at the edge | 12 bangles loosely scattered and overlapping, some lying flat, some resting on others |
| 3 | Scatter close-up | 30-45 degrees, shallow depth of field | same fabric | tight on 4-6 bangles and beads, creamy blur behind |
| 4 | Stack on its side on a tray | 30-40 degrees | brass thali or velvet tray with petals | stack lies on its side like coins, a few loose bangles beside it |
| 5 | Worn, relaxed hand | side or 3/4, soft window light | forearm resting on a table or lap, saree or kurta sleeve | outfit colour chosen to complement the bangle (table below) |
| 6 | Worn, in action | 3/4 | hand holding a rose by the stem, or a dupatta edge, or a mogra gajra | still natural, no flames, no earrings gestures |
| 7 | Bangle stand | eye level | slim brass pole stand with base, vanity table, one set only | short tower only |
| 8 | Macro of thread and beads | 45 degrees, 1:1 feel | any | shows twist and beads |

Outfit pairing (complementary, not matching): royal blue - mustard or ivory and gold; crimson - cream and gold; mustard - deep blue; coral pink - ivory with pearls; turquoise - peach and gold; emerald - deep red and gold; parrot green - mustard, white bandhani; rani pink - cream and gold; wine - cream and gold brocade; orange - deep green; golden - deep green.

## 5. Pipeline

1. Generate with Shopify Magic from the real tight crop (`thread_setup.make_job`, prompts in `thread_creative.py`). Use profiles `.magic-profile-g3` / `-g4` only; another session uses `.magic-profile` and `-g2`. Never mass-kill browsers.
2. Check every image: automatic count for the hero, then the realism review below.
3. Realism review by Gemini through the Antigravity CLI (`agy`) plus a look by Claude. Brief and results go in `agy-handoff/stb-realism/`.
4. Keep only images that pass; regenerate the rest with the reviewer's note added to the prompt.

## 6. Review checklist (what the reviewer must answer per image)

- Does anything float, hang from nothing, or defy gravity? Yes/No + where.
- Are objects held or placed the way a person would really do it?
- Are the hands and arms anatomically correct?
- Are the bangles rigid rings, stacked or scattered believably, with contact shadows?
- Does the product look like thread bangles with gold beads (not glass, not stones)?
- Approximate number of bangles visible.
- Do the outfit and background complement the bangle colour?
- Verdict PASS / FAIL with one-line reason.

## 7. Status notes
- 2026-10-18: Gemini review via `agy` did not work (model `gemini-3.1-pro-high` no longer exists; `Gemini 3.8 Flash (High)` returned no JSON headless). Claude reviewed images by eye with the checklist instead. Retry agy later with `--model "Gemini 3.8 Flash (High)"`.
- First Royal Blue realistic set (stb/creative/royal-blue/s2..s8): scatter flat lay, scatter close-up, relaxed wrist, wrist with rose, macro pass. Tray stack and stand towers show ~16-20 bangles (generator over-stacks); needs a shorter-stack retry if the owner wants those to read as 12.

## 8. Shot-type rules learned from Design 4 (2026-10-19/20) — applies to every design, not just rhinestone

- **No "bangle-stand" shots.** The pole makes the bangles read as floating/fake to the owner. Drop it from
  the shot pool entirely; do not regenerate it even if asked to redo a different shot of the same colour.
- **No overhead/straight-down flat-lay shots either** ("scatter-flatlay", "scatter-geometric" — camera
  pointing straight down at a bangle lying flat). Seen edge-on from directly above, a bangle doesn't show
  its side/face design. Use an angled scatter (30-45 degrees) instead, never a true top-down.
- **Anti-fusing clause for any shot with multiple loose/overlapping bangles** (scatter-close, tray-scatter):
  without an explicit instruction, Magic can merge 2-3 bangles into what reads as "one thick bangle with
  multiple stone rows" instead of distinct rings. Add a clause requiring every bangle to show its own edge
  and a visible gap/shadow from its neighbours, never fused into one band.
  Example clause: "Every bangle must read as a clearly separate, individual ring - each with its own
  visible outer edge and its own single row (or rows) of stones, with a visible thin gap, edge-line or
  shadow between any two bangles that touch or overlap. NEVER let two or more bangles merge, fuse or blend
  into what looks like one thicker band."
- **Anti-overstack clause for any tray/stack shot**: Magic tends to add extra bangles beyond the real count
  when stacking them on their side. State the exact count explicitly and that it must match the reference,
  never taller.
- **Vary shot selection randomly per colour from a wide pool (10-15 shot types), not a fixed set.** With the
  same 3-4 shot types repeated for every colour, a whole product line looks templated with only the colour
  changed (owner feedback, 2026-10-19). Build a pool of distinct scenes (scatter-close, tray-stack,
  tray-scatter, velvet-roll, worn-relaxed, worn-holding-a-flower/dupatta/diya/teacup, worn-henna-close,
  plus the hero and the cropped macro) and randomly sample ~4-5 per colour, seeded by colour name so a
  re-run is reproducible but different colours get different combinations.

## 9. Multi-angle composite references for structurally complex designs (2026-10-20)

For a design with real 3D structure the camera can't fully show from one angle — hanging bell/ghungroo
clusters on chains, a multi-piece bangle stack where each bangle in the stack has a different pattern,
anything with an underside or a dangling element — a single reference crop is not enough information for
Magic to get right, even with a very detailed text description. Tested head-to-head on two designs
(`raw 01/Round Wire Bangles with Hanging Bell Clusters on Chains/Gold`, `raw 02/01` — a 5-bangle kundan
stack with 3 different patterns):

- **Multi-angle composite (recommended for complex designs):** stack 3-4 of the real reference photos
  (front view, 3/4 angle, macro/detail of the hard part) into ONE labeled image — a black caption band above
  each panel naming what it shows (e.g. "FRONT VIEW", "MACRO - BELL CLUSTER + CHAIN DETAIL") — and use that
  as the single Magic reference, with a prompt line telling Magic to study all panels together before
  generating. Both test designs came back structurally correct: right chain/bell count on the hanging
  design, right bangle count (5) and all three patterns in the right positions on the kundan stack.
- **Single-view reference (what the pipeline used until now):** on the hanging-bells design it was close but
  less realistic (perfectly symmetric "flower" cluster instead of an organic bunch, bangles spaced apart
  instead of nested). On the kundan stack it was worse: wrong bangle count (7 instead of 5) and it invented
  an extra pattern that doesn't exist in the real piece — almost certainly because the one photo given had
  bangles overlapping and running off both edges of frame, so Magic had no way to know the true boundary of
  the design.
- **Don't bother with a composite for a simple repeating surface pattern** (e.g. the Design 4 rhinestone
  bangles, where the stone pattern is identical all the way around) — one crop is already enough.
- **Build the composite with plain PIL**, not a browser: stack panels vertically, same width, a dark caption
  band (~40px) above each with the view name in white text. Keep the whole composite's file size small
  (resize each source photo down first) — see the upload-stall note below.

## 10. Shopify Magic / `execution_agent.py` operational notes (2026-10-19/20)

- **Driving a different browser**: `execution_agent.py` now takes `--executable <path to a Chromium-based
  browser>` and `--minimized` (launches with `--start-minimized` so the window doesn't steal focus). Used
  with Comet (`~\AppData\Local\Perplexity\Comet\Application\comet.exe`) reusing the existing
  `.magic-profile-g3`/`-g4` login — a different binary can drive the same profile directory without a fresh
  login, as long as the profile isn't open elsewhere.
- **Never combine a shell `&` background with the harness's own background-run flag** on the same command —
  it orphans a duplicate driver process that keeps racing the real one for the same browser profile, causing
  `Opening in existing browser session` lock errors and silent generation failures. Background it one way
  only.
- **If a job hangs with no visible progress and no error for several minutes**, before assuming the
  automation is broken, check `status.json` for a cached `original_file_id` — the script re-uses that id on
  every retry instead of re-uploading, so if the *uploaded Shopify file* itself is in a bad state, every
  retry hits the same wall and looks identical. Clear `original_file_id` (and `generation_summary`) from
  `status.json`, reset the job's `image_queue.json` entries to `"status": "pending"`, and re-run so it
  uploads a fresh copy. This fixed a real stuck job (confirmed: new file ID, generation completed normally
  within 2 minutes after a fresh upload, after 3+ timeouts on the old one).
- **Downsize raw reference photos before uploading** — a 50-megapixel phone photo (8160x6120, several MB)
  is needless weight for Magic's editor and was a contributing factor in one stuck job; resize to ~1400px on
  the long side before use, same as the crop pipeline already does for the hero/creative jobs.
- **Stale `.magic-profile-g*/SingletonLock` / `.magic-save.lock` files** are left behind whenever a browser
  or the driver script is force-killed (from an earlier crash, a manual stop, or cleaning up an orphaned
  process). Delete `SingletonLock`, `SingletonSocket`, `SingletonCookie` in the profile dir and
  `.magic-save.lock` in the project root before relaunching after any forced kill.
