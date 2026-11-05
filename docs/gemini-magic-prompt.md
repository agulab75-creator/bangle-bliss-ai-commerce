# Prompt for Gemini in Chrome — generate Bangle Bliss photos with Shopify Magic

Open Chrome, make sure you are logged in to Shopify admin for the store `your-store`, open the Gemini side panel, and paste everything between "PASTE FROM HERE" and "END OF PROMPT".

---

## PASTE FROM HERE

You are my careful photo assistant. Work in my logged-in Shopify admin (store: your-store, https://admin.shopify.com/store/your-store). Your ONLY job is to create product photos with Shopify's built-in image editor (Magic) in Files. Work continuously until all 44 images are finished. Do not stop to ask me questions unless a rule at the bottom says to stop.

### The job
For each of the 11 source photos below, create exactly 4 new images, one of each shot type = 44 images.

Source photos (find them by file name in Files: https://admin.shopify.com/store/your-store/content/files, use the search box):

1. Sky Aqua: bb-glass-image-2
2. Parrot Green: bb-glass-image-4
3. Coral Peach: bb-glass-image-6
4. Orchid Pink: bb-glass-image-8
5. Mint Green: bb-glass-image-9
6. Magenta: bb-glass-image-10
7. Ruby Red: bb-glass-image-11
8. Plum Wine: bb-glass-image-12
9. Emerald Green: bb-glass-image-13
10. Maroon: bb-glass-image-14
11. Royal Blue: bb-glass-image-7 (this one is a different design: royal blue glass with gold leaf motifs; the other ten are glass bangles with small kundan stones set in gold rings)

### First, for EACH source photo: LOOK and decide
Open the file and look at the picture carefully. Write 2 lines in your reply before you start editing it:
- Analysis: the exact colour, glass finish (see-through / milky / glossy), number of bangles, stone or motif style.
- Plan: the colour palette and setting that will make THIS colour look best (see shot 2) — never reuse the same scene for two different colours. Choose per product.

### The 4 shots (all four are required for every colour)

**Shot 1 — Plain white background (product on pure white)**
Use the "Color background" tool in the editor's right panel (not Generate). Choose white (#FFFFFF) and apply. Check that the bangles are intact, with no halo and no missing parts. If the stand or roller stays visible, that is fine if the bangles stay clean; if edges look damaged, discard and retry once.

**Shot 2 — Lifestyle photo that matches the product**
Use "Generate". Write a prompt of your own, based on your analysis. Rules for the scene you choose:
- The setting must flatter the colour: pick complementary or harmonious colours, not clashing ones. Examples for inspiration only: pale aqua or mint -> white jasmine flowers, pearls, soft ivory linen, morning light; vivid green or emerald -> marigold flowers on red silk; coral or peach -> rose gold and cream silk with blush flowers; pink or magenta -> rose petals on ivory brocade; red, ruby or maroon -> gold zari silk with brass diyas; plum -> deep gold and ivory velvet; royal blue with gold leaf -> ivory and gold brocade with a brass diya.
- Indian festive or bridal feeling, premium jewellery photography, soft warm natural light, no text, no people.
- End the prompt with: "Keep the bangles exactly as they are, same colour, same stones, same shape and same number."

**Shot 3 — Close shot of the product worn on a hand (must FIT naturally)**
Use "Generate". Prompt based on your analysis, for example: "A close-up of an elegant woman's hand and wrist wearing these exact bangles, hand resting gently, soft henna on the hand, natural skin, soft window light, premium jewellery photography. Keep the bangles exactly as they are, same colour, same stones, same shape."
It is GOOD only if: the bangles sit around the wrist naturally like worn bangles (not floating, not stuck on a stick), the hand looks natural (five fingers, no distortion), and the bangle colour is unchanged. If it is not good, discard and retry once with a different wording. If it fails twice, write NOT-FIT in your log and move on (do not save a bad one).

**Shot 4 — Premium close-up (macro) of the design detail**
First click "Crop and transform" and crop tightly to the most beautiful detail (a few stones or the motif and the glass edge), about the middle 50% of the picture; apply the crop. Then use "Generate" with a prompt such as: "Extreme macro close-up photograph of this bangle detail, shallow depth of field, soft creamy blurred background in a colour that complements the bangle, luxury jewellery photography, sharp focus on the stones." Keep the bangle unchanged. If the crop or result looks blurry or distorted, discard and retry once.

### Steps for each image
1. Open the source file (Files, click the file, editor opens).
2. Do the shot as described. In the right-hand panel scroll down if needed to find "Color background", "Generate" and "Crop and transform".
3. After typing a Generate prompt, press Enter. It shows "Generating…" for 20 to 40 seconds. Wait until the result appears and the "Save" and "Discard" buttons show at the top right. Do not click anything meanwhile.
4. Judge the result against the rules for that shot.
5. If GOOD: click the small arrow next to "Save" at the top right and choose "Save as new". NEVER click the main "Save" button: that overwrites my original photo. Wait until the page switches to the new file.
6. If BAD: click "Discard", reopen the SOURCE file (bb-glass-image-N, not a new file) and retry once. After two bad results, skip it and log FAILED.
7. Always start every new shot from the original SOURCE file, never from a saved new file.
8. Order: colour 1 shots 1 to 4, then colour 2 shots 1 to 4, and so on.

### Keep a log
After every saved image write one line: `COLOUR | Shot N | SAVED` (or `FAILED` / `NOT-FIT`). Include your scene choice in the Shot 2 line. At the very end print the full table and the counts.

### Hard rules (never break these)
- Only use the Files editor tools (Color background, Generate, Crop and transform). Do not open any other Shopify page. Never edit products, orders, settings, themes, apps, payments or customers.
- Never click "Save" (overwrite). Only "Save as new". Never delete or rename any file.
- Never publish anything. Never enter passwords or payment details. Never accept a popup asking for money, a plan change or app permissions.
- If Shopify asks you to log in, shows a CAPTCHA, shows an error about plan limits or "usage limit reached", or the page stays frozen for more than 2 minutes, STOP and tell me exactly which colour and shot you stopped at. Otherwise do NOT stop. Keep going until all 44 are done.
- If the tab freezes, wait 20 seconds, refresh once, and continue from the last unfinished shot.

When all 44 are done, reply "ALL DONE" with the table.

## END OF PROMPT

---

## After Gemini finishes

Come back and say "Gemini is done" (and paste its log if some shots are FAILED or NOT-FIT). Claude will find the new files in the order they were created, attach the four images to each colour's variants in the Kundan Stone product, and retry any failed shots itself.

## Known limits (honest)
- Shopify Magic changes backgrounds and lighting well. Shot 3 (hands) and Shot 4 (macro) are the hardest: the editor may keep the bangles on the stand or return soft or distorted results. Expect some NOT-FIT or FAILED lines. Claude can retry those.
- Magic output is about 1024 px wide, so the macro shot may look slightly soft.
