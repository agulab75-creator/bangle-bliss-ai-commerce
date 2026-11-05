# Prompt for Claude Haiku 4.5 in the Claude in Chrome extension

How to use: in Chrome, open the Claude side panel, pick **Haiku 4.5**, stay logged in to Shopify admin, and paste the block below. Run it **one colour per chat** (start a new chat for each colour, change the line `MY COLOUR`). That keeps each run short and cheap. 11 colours = 11 chats = 44 images.

---

## PASTE FROM HERE

You are doing a repetitive photo job in my Shopify admin using Shopify's built-in image editor (Magic). Work slowly and carefully. Take a screenshot after every click so you know what is on screen.

**MY COLOUR: Sky Aqua**  (change this line for each chat; use the file ID from the table)

| Colour | File ID |
|---|---|
| Sky Aqua | <id> |
| Parrot Green | <id> |
| Coral Peach | <id> |
| Orchid Pink | <id> |
| Mint Green | <id> |
| Magenta | <id> |
| Ruby Red | <id> |
| Plum Wine | <id> |
| Emerald Green | <id> |
| Maroon | <id> |
| Royal Blue | <id> |

The source photo URL is: `https://admin.shopify.com/store/your-store/content/files/FILE_ID` (replace FILE_ID). Every shot starts by opening THIS URL again, so you always edit the original, never a saved copy.

### Make exactly 4 new images from that one source photo

**Shot 1: clean white studio product photo (made with Generate)**
1. Open the source URL. In the right panel scroll down if needed and click **Generate**.
2. Click the prompt box, type: `Professional e-commerce studio product photo of these exact bangles floating on a clean pure white seamless background, soft even studio lighting, subtle natural shadow, no stand or roller, sharp focus. Keep the bangles exactly as they are, same colour, same stones, same shape and same number.` Press Enter.
3. Wait 20 to 40 seconds until "Save" and "Discard" show at the top right.
4. Check: the bangles look the same colour and shape, the background is clean white, no stand. If not, **Discard**, reopen the source URL and retry once. After two failures write FAILED and move on.
5. Save (see "How to save" below).

**Shot 2: lifestyle photo that matches the colour**
1. Open the source URL. In the right panel scroll down if needed and click **Generate**.
2. Click the prompt box and type a prompt of your own for THIS colour. First look at the photo and decide a setting that flatters the colour (complementary or harmonious, never clashing). Ideas: pale aqua or mint = white jasmine, pearls, ivory linen; green or emerald = marigolds on red silk; coral or peach = cream silk with blush flowers; pink or magenta = rose petals on ivory brocade; red, ruby or maroon = gold zari silk with brass diyas; plum = ivory and gold velvet; royal blue = ivory and gold brocade with a brass diya.
3. End the prompt with exactly: `Keep the bangles exactly as they are, same colour, same stones, same shape and same number.` Press Enter.
4. Wait 20 to 40 seconds until "Save" and "Discard" show at the top right. Do not click anything while it says "Generating".
5. Check: the bangles look the same colour and shape, the background changed. If not, **Discard**, reopen the source URL and retry once. After two failures, write FAILED and move on.
6. Save.

**Shot 3: close-up of the bangles worn on a hand**
1. Open the source URL, click **Generate**, and type: `A close-up of an elegant woman's hand and wrist wearing these exact bangles, hand resting gently, soft henna on the hand, natural skin, soft window light, premium jewellery photography. Keep the bangles exactly as they are, same colour, same stones, same shape.` Press Enter and wait.
2. Check: bangles sit around the wrist like worn bangles (not floating), the hand looks natural, the colour is unchanged. If not, Discard and retry once with slightly different words. If it fails twice, write NOT-FIT and move on without saving.
3. Save.

**Shot 4: premium macro close-up of the design**
1. Open the source URL and click **Generate**. Type: `Extreme macro close-up photograph of this bangle design, filling the frame with the kundan stones and glass detail, shallow depth of field, soft creamy blurred background in a colour that complements the bangle, luxury jewellery photography, sharp focus on the stones. Keep the bangle design exactly as it is.` Press Enter and wait.
2. Check it looks sharp and undistorted. If not, Discard and retry once. After two failures write FAILED.
3. Save.

### How to save (important)
At the top right there is a **Save** button with a small **arrow** next to it. Click the small arrow and choose **Save as new**. NEVER click the main Save button, it overwrites my original. After saving, the page switches to a new file.

### Tips for this website
- If the right-hand panel is long, scroll it down to find **Generate**.
- If a screenshot fails or the page looks frozen, wait 20 seconds and try again. If it stays frozen for 2 minutes, refresh once and continue the unfinished shot.
- Magic output is about 1024 px. That is fine.

### Hard rules
- Use ONLY the **Generate** tool. Do NOT use Color background, remove background or Crop and transform: those look bad. Do not open any other Shopify page or change products, settings, themes, orders or payments.
- Never overwrite, delete or rename any file. Never publish anything. Never enter passwords or payment details.
- If Shopify asks you to log in, shows a CAPTCHA, or says a usage limit is reached, STOP and tell me where you stopped.

### Report
After each shot write one line: `COLOUR | Shot N | SAVED` (or FAILED / NOT-FIT), with the scene you picked for Shot 2. When all 4 shots are done, write "COLOUR DONE" and the four lines.

## END OF PROMPT

---

After all colours are done, tell Claude in Claude Code "images are done". It will find the new files (they are named after the source photo) in the order they were created and attach four to each colour on the product.
