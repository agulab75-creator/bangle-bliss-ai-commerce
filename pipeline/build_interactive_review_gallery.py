"""
build_interactive_review_gallery.py
Generates an interactive HTML review gallery with full-resolution zoom, flag/delete toggle,
and export controls for all 56 images across the 8 Ghunghroo RN P1 color variants.
Outputs to:
1. <project-dir>/ghunghroo_review_gallery.html
2. ~/.gemini/antigravity-ide/brain/82cce8b8-82da-455e-82a0-87ceb15a0d45/ghunghroo_review_gallery.html
"""

import json
import base64
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ARTIFACT_DIR = Path(r"~\.gemini\antigravity-ide\brain\82cce8b8-82da-455e-82a0-87ceb15a0d45")

COLOR_GROUPS = [
    {"id": "gh-rn-p1-wine-maroon", "name": "Wine Maroon", "hex": "#581136"},
    {"id": "gh-rn-p1-deep-maroon", "name": "Deep Maroon", "hex": "#660b1e"},
    {"id": "gh-rn-p1-emerald-green", "name": "Emerald Green", "hex": "#0e6b38"},
    {"id": "gh-rn-p1-turquoise-blue", "name": "Turquoise Blue", "hex": "#2d9da6"},
    {"id": "gh-rn-p1-mustard-yellow", "name": "Mustard Yellow", "hex": "#d4a017"},
    {"id": "gh-rn-p1-crimson-red", "name": "Crimson Red", "hex": "#b31b27"},
    {"id": "gh-rn-p1-rani-pink", "name": "Rani Pink", "hex": "#e0127d"},
    {"id": "gh-rn-p1-multi-color", "name": "Multi Color", "hex": "#d14280"},
]

SHOT_LABELS = {
    "1-white-studio": "1. White Studio (Pure White 255)",
    "2-lifestyle-flatlay": "2. Festive Silk Flat-Lay",
    "3-macro-detail": "3. Macro Mirror & Ghungroo",
    "4-tray-arrangement": "4. Antique Brass Thali Tray",
    "5-model-relaxed-wrist": "5. Model: Henna Wrist",
    "6-model-action-prop": "6. Model: Rose in Motion",
    "7-model-editorial-bridal": "7. Model: Bridal Veil Editorial"
}

items = []
for c in COLOR_GROUPS:
    jid = c["id"]
    job_dir = ROOT / "jobs" / jid
    q_file = job_dir / "image_queue.json"
    if not q_file.exists():
        continue
    q_data = json.loads(q_file.read_text(encoding="utf-8"))
    for s in q_data:
        sid = s["id"]
        out_name = s.get("output_file", f"{sid}.png")
        img_file = job_dir / "generated" / out_name
        rel_path = f"jobs/{jid}/generated/{out_name}"
        abs_path = str(img_file).replace("\\", "/")
        items.append({
            "color": c["name"],
            "color_hex": c["hex"],
            "job_id": jid,
            "shot_id": sid,
            "label": SHOT_LABELS.get(sid, sid),
            "rel_path": rel_path,
            "abs_path": abs_path,
            "alt": s.get("alt_text", "")
        })

html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Bridal Kundan Jhumka Bangle Set — Image Review Gallery (56 Images)</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Playfair+Display:ital,wght@0,600;1,600&display=swap" rel="stylesheet">
<style>
:root {{
  --bg: #0d1117;
  --panel: #161b22;
  --card: #1c2128;
  --card-border: #30363d;
  --accent: #d4af37;
  --accent-soft: rgba(212, 175, 55, 0.15);
  --danger: #f85149;
  --danger-soft: rgba(248, 81, 73, 0.15);
  --success: #3fb950;
  --text: #f0f6fc;
  --muted: #8b949e;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
  background: var(--bg);
  color: var(--text);
  font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
  padding: 24px 32px 140px;
  line-height: 1.5;
}}
header {{
  max-width: 1400px;
  margin: 0 auto 32px;
  border-bottom: 1px solid var(--card-border);
  padding-bottom: 24px;
}}
h1 {{
  font-family: 'Playfair Display', Georgia, serif;
  font-size: 32px;
  color: #fff;
  margin-bottom: 8px;
}}
.subtitle {{
  color: var(--muted);
  font-size: 15px;
}}
.stats-bar {{
  display: flex;
  gap: 16px;
  margin-top: 16px;
  flex-wrap: wrap;
}}
.stat-chip {{
  background: var(--panel);
  border: 1px solid var(--card-border);
  padding: 6px 14px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 500;
}}
.stat-chip b {{ color: var(--accent); }}

/* Filters */
.filter-tabs {{
  max-width: 1400px;
  margin: 0 auto 28px;
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding-bottom: 8px;
}}
.tab {{
  background: var(--panel);
  border: 1px solid var(--card-border);
  color: var(--text);
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: all .15s;
}}
.tab:hover, .tab.active {{
  background: var(--accent-soft);
  border-color: var(--accent);
  color: var(--accent);
}}

/* Sections */
.gallery-container {{
  max-width: 1400px;
  margin: 0 auto;
}}
.color-group {{
  margin-bottom: 48px;
}}
.group-title {{
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
}}
.color-dot {{
  width: 14px;
  height: 14px;
  border-radius: 50%;
  display: inline-block;
  border: 2px solid rgba(255,255,255,0.2);
}}
.grid {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 20px;
}}
.card {{
  background: var(--card);
  border: 1px solid var(--card-border);
  border-radius: 12px;
  overflow: hidden;
  position: relative;
  transition: transform .18s, border-color .18s, box-shadow .18s;
  display: flex;
  flex-direction: column;
}}
.card:hover {{
  transform: translateY(-3px);
  border-color: var(--accent);
  box-shadow: 0 8px 24px rgba(0,0,0,0.4);
}}
.card.flagged {{
  border-color: var(--danger);
  box-shadow: 0 0 0 2px var(--danger);
  opacity: 0.65;
}}
.thumb-wrap {{
  position: relative;
  aspect-ratio: 3/4;
  background: #000;
  cursor: pointer;
}}
.thumb-wrap img {{
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}}
.badge-del {{
  position: absolute;
  top: 10px;
  right: 10px;
  background: var(--danger);
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 999px;
  display: none;
  box-shadow: 0 2px 8px rgba(0,0,0,0.5);
}}
.card.flagged .badge-del {{ display: block; }}
.badge-hero {{
  position: absolute;
  top: 10px;
  left: 10px;
  background: rgba(0,0,0,0.75);
  backdrop-filter: blur(4px);
  border: 1px solid rgba(255,255,255,0.2);
  color: #fff;
  font-size: 11px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 6px;
}}
.card-body {{
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
}}
.card-label {{
  font-size: 13px;
  font-weight: 600;
  color: #fff;
}}
.card-alt {{
  font-size: 11px;
  color: var(--muted);
  line-height: 1.4;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}}
.card-actions {{
  display: flex;
  gap: 8px;
  margin-top: auto;
  padding-top: 8px;
}}
.btn {{
  flex: 1;
  font: inherit;
  font-size: 12px;
  font-weight: 600;
  padding: 6px 10px;
  border-radius: 6px;
  cursor: pointer;
  border: 1px solid var(--card-border);
  background: var(--panel);
  color: var(--text);
  transition: all .15s;
}}
.btn:hover {{
  background: var(--accent-soft);
  border-color: var(--accent);
  color: var(--accent);
}}
.btn.flag-btn {{
  border-color: rgba(248,81,73,0.3);
  color: #ff7b72;
}}
.card.flagged .btn.flag-btn {{
  background: var(--danger);
  color: #fff;
  border-color: var(--danger);
}}

/* Sticky Action Bar */
.bottom-bar {{
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(22, 27, 34, 0.95);
  backdrop-filter: blur(12px);
  border-top: 1px solid var(--card-border);
  padding: 16px 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  z-index: 100;
}}
.bar-info {{
  font-size: 14px;
}}
.bar-info b {{ color: var(--accent); font-size: 16px; }}
.bar-actions {{
  display: flex;
  gap: 12px;
}}
.primary-btn {{
  background: var(--accent);
  color: #000;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  font-size: 14px;
}}
.danger-btn {{
  background: var(--danger);
  color: #fff;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  font-size: 14px;
}}

/* Lightbox Modal */
.modal {{
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.92);
  display: none;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 30px;
}}
.modal.open {{ display: flex; }}
.modal img {{
  max-width: 90vw;
  max-height: 85vh;
  object-fit: contain;
  border-radius: 8px;
  box-shadow: 0 12px 48px rgba(0,0,0,0.8);
}}
.modal-close {{
  position: absolute;
  top: 20px;
  right: 28px;
  font-size: 32px;
  color: #fff;
  cursor: pointer;
}}
</style>
</head>
<body>

<header>
  <h1>Bridal Kundan & Diamond-Cut Glass Bangle Set with Hanging Jhumkas</h1>
  <div class="subtitle">Complete Review Gallery • 8 Color Variants • 56 Generated Product & Lifestyle Images</div>
  <div class="stats-bar">
    <div class="stat-chip">Total Images: <b id="total-count">{len(items)}</b></div>
    <div class="stat-chip">Marked for Deletion: <b id="del-count" style="color:var(--danger)">0</b></div>
    <div class="stat-chip">Approved: <b id="app-count" style="color:var(--success)">{len(items)}</b></div>
    <div class="stat-chip">Shopify Product: <a href="https://admin.shopify.com/store/your-store/products/<id>" target="_blank" style="color:var(--accent); text-decoration:none"><b>Open in Admin ↗</b></a></div>
  </div>
</header>

<div class="filter-tabs">
  <button class="tab active" onclick="filterColor('all')">All Colors (56)</button>
"""

for c in COLOR_GROUPS:
    html += f'  <button class="tab" onclick="filterColor(\'{c["name"]}\')"><span class="color-dot" style="background:{c["hex"]}"></span> {c["name"]}</button>\n'

html += """</div>

<div class="gallery-container">
"""

for c in COLOR_GROUPS:
    c_items = [it for it in items if it["color"] == c["name"]]
    html += f"""
  <div class="color-group" data-color="{c['name']}">
    <div class="group-title">
      <span class="color-dot" style="background:{c['hex']}; width:18px; height:18px;"></span>
      <span>{c['name']}</span>
      <span style="font-size:13px; color:var(--muted); font-weight:normal;">({len(c_items)} images)</span>
    </div>
    <div class="grid">
"""
    for it in c_items:
        card_id = f"{it['job_id']}_{it['shot_id']}"
        is_hero = "1-white-studio" in it["shot_id"]
        hero_tag = '<div class="badge-hero">Hero Shot</div>' if is_hero else ""
        html += f"""
      <div class="card" id="card_{card_id}">
        <div class="thumb-wrap" onclick="openModal('{it['abs_path']}')">
          <img src="{it['abs_path']}" alt="{it['alt']}" loading="lazy">
          {hero_tag}
          <div class="badge-del">MARKED FOR DELETION</div>
        </div>
        <div class="card-body">
          <div class="card-label">{it['label']}</div>
          <div class="card-alt">{it['alt']}</div>
          <div class="card-actions">
            <button class="btn" onclick="openModal('{it['abs_path']}')">Zoom</button>
            <button class="btn flag-btn" onclick="toggleFlag('{card_id}')">Delete</button>
          </div>
        </div>
      </div>
"""
    html += """    </div>
  </div>
"""

html += """</div>

<div class="bottom-bar">
  <div class="bar-info">
    Marked <b id="del-count-bar">0</b> / 56 images for deletion.
  </div>
  <div class="bar-actions">
    <button class="btn" onclick="resetAll()">Reset All</button>
    <button class="primary-btn" onclick="copyDeleteList()">Copy Deletion List</button>
    <button class="danger-btn" onclick="deleteFlagged()">Confirm & Delete Flagged</button>
  </div>
</div>

<div class="modal" id="modal" onclick="closeModal()">
  <span class="modal-close">&times;</span>
  <img id="modal-img" src="" onclick="event.stopPropagation()">
</div>

<script>
const flagged = new Set();

function toggleFlag(id) {
  const card = document.getElementById('card_' + id);
  if (flagged.has(id)) {
    flagged.delete(id);
    card.classList.remove('flagged');
  } else {
    flagged.add(id);
    card.classList.add('flagged');
  }
  updateCounts();
}

function updateCounts() {
  const d = flagged.size;
  const total = 56;
  document.getElementById('del-count').innerText = d;
  document.getElementById('del-count-bar').innerText = d;
  document.getElementById('app-count').innerText = total - d;
}

function resetAll() {
  flagged.clear();
  document.querySelectorAll('.card.flagged').forEach(c => c.classList.remove('flagged'));
  updateCounts();
}

function filterColor(col) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  event.target.closest('.tab').classList.add('active');
  document.querySelectorAll('.color-group').forEach(grp => {
    if (col === 'all' || grp.getAttribute('data-color') === col) {
      grp.style.display = 'block';
    } else {
      grp.style.display = 'none';
    }
  });
}

function openModal(src) {
  document.getElementById('modal-img').src = src;
  document.getElementById('modal').classList.add('open');
}

function closeModal() {
  document.getElementById('modal').classList.remove('open');
}

function copyDeleteList() {
  const list = Array.from(flagged);
  if (list.length === 0) {
    alert("No images are currently flagged for deletion.");
    return;
  }
  const text = JSON.stringify(list, null, 2);
  navigator.clipboard.writeText(text).then(() => {
    alert(`Copied ${list.length} flagged image ID(s) to clipboard!`);
  });
}

function deleteFlagged() {
  const count = flagged.size;
  if (count === 0) {
    alert("No images are marked for deletion.");
    return;
  }
  if (confirm(`Are you sure you want to delete ${count} flagged image(s)?`)) {
    alert("Deletion list ready! Inform the assistant to purge the selected files.");
  }
}

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') closeModal();
});
</script>

</body>
</html>
"""

out1 = ROOT / "ghunghroo_review_gallery.html"
out2 = ARTIFACT_DIR / "ghunghroo_review_gallery.html"

out1.write_text(html, encoding="utf-8")
out2.write_text(html, encoding="utf-8")

print(f"Generated review galleries:")
print(f"  [1] {out1}")
print(f"  [2] {out2}")
