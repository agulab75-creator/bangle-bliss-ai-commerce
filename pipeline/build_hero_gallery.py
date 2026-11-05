"""
build_hero_gallery.py
Generates the Approved Products Hero Showcase:
1. approved_heroes_gallery.html (Workspace root)
2. approved_heroes_gallery.html (Artifacts directory)
3. approved_products_heroes.md (Markdown artifact with embedded images)
"""

import json
from pathlib import Path
import raw01_metadata as rm

ROOT = Path(r"<project-dir>")
ARTIFACTS_DIR = Path(r"~\.gemini\antigravity-ide\brain\48ec34a7-c611-4c64-89aa-3638740d1058")
ART_IMG_DIR = ARTIFACTS_DIR / "images"

EXCLUDED_IDS = {
    "raw01-01-broad-kada-silver",
    "raw01-01-broad-kada-gold",
    "raw01-07-dense-ghungroo-kada-bright-gold",
    "raw01-07-dense-ghungroo-kada-antique-brass",
    "raw01-19-pearl-crystal-tassels-gold-white",
    "raw01-21-multicolor-crystal-teardrop-drops",
}

REGEN_7 = {
    "raw01-02-jhumka-latkan-silver",
    "raw01-04-wire-bell-clusters-silver",
    "raw01-06-rhinestone-twisted-silver",
    "raw01-06-rhinestone-twisted-gold",
    "raw01-09-enamel-halo-green-maroon-round",
    "raw01-24-pearl-gold-beaded-wire-stack",
    "raw01-25-thin-wire-floral-bell-charms-gold"
}

def main():
    active_items = [item for item in rm.METADATA if item["id"] not in EXCLUDED_IDS]
    print(f"Generating Hero Showcase for {len(active_items)} approved active products...")

    products_data = []
    for item in active_items:
        jid = item["id"]
        title = item.get("shopify_title", jid.replace("-", " ").title())
        metal = item.get("metal", "Gold Plated")
        count = item.get("count", 4)
        var = item.get("variation", "Gold")
        is_regen = jid in REGEN_7
        
        rel_hero = f"jobs/{jid}/generated/1-white-studio.png"
        art_rel_hero = f"images/hero__{jid}.png"
        art_abs_hero = str(ART_IMG_DIR / f"hero__{jid}.png").replace("\\", "/")
        disk_abs_hero = str(ROOT / "jobs" / jid / "generated" / "1-white-studio.png").replace("\\", "/")

        products_data.append({
            "id": jid,
            "title": title,
            "metal": metal,
            "count": count,
            "variation": var,
            "is_regen": is_regen,
            "category": "Regenerated (Latest Fix)" if is_regen else "Approved Catalog",
            "rel_hero": rel_hero,
            "art_rel_hero": art_rel_hero,
            "art_abs_hero": art_abs_hero,
            "disk_abs_hero": disk_abs_hero
        })

    # 1. HTML for Workspace
    html_workspace = render_html(products_data, is_artifact=False)
    out_ws = ROOT / "approved_heroes_gallery.html"
    out_ws.write_text(html_workspace, encoding="utf-8")
    print(f"Wrote workspace HTML: {out_ws}")

    # 2. HTML for Artifact
    html_artifact = render_html(products_data, is_artifact=True)
    out_art = ARTIFACTS_DIR / "approved_heroes_gallery.html"
    out_art.write_text(html_artifact, encoding="utf-8")
    print(f"Wrote artifact HTML: {out_art}")

    # 3. Markdown Artifact
    md_content = render_markdown(products_data)
    out_md = ARTIFACTS_DIR / "approved_products_heroes.md"
    out_md.write_text(md_content, encoding="utf-8")
    print(f"Wrote markdown artifact: {out_md}")

def render_html(products, is_artifact=False):
    cards_html = []
    for p in products:
        img_src = p["art_rel_hero"] if is_artifact else p["rel_hero"]
        badge_cls = "badge-regen" if p["is_regen"] else "badge-approved"
        badge_text = "✨ Latest Regenerated" if p["is_regen"] else "✓ Approved"
        
        card = f"""
        <div class="hero-card" data-category="{p['category']}" data-metal="{p['metal'].lower()}" data-id="{p['id']}">
            <div class="hero-img-wrapper" onclick="openLightbox('{img_src}', '{p['title']}', '{p['id']} | Set of {p['count']} | {p['metal']}')">
                <img src="{img_src}" alt="{p['title']}" loading="lazy">
                <span class="card-status-badge {badge_cls}">{badge_text}</span>
                <div class="zoom-hint">🔍 Enlarge</div>
            </div>
            <div class="hero-card-body">
                <div class="sku-row">
                    <span class="sku-tag">{p['id']}</span>
                    <span class="count-tag">Set of {p['count']}</span>
                </div>
                <h3 class="hero-title">{p['title']}</h3>
                <div class="meta-row">
                    <span class="meta-tag">{p['metal']}</span>
                    <span class="meta-tag">{p['variation']}</span>
                </div>
                <div class="card-actions">
                    <a href="{p['disk_abs_hero']}" target="_blank" class="btn-action">View Full Master (PNG)</a>
                    <button type="button" class="btn-action btn-copy" onclick="copyId('{p['id']}')">Copy SKU</button>
                </div>
            </div>
        </div>
        """
        cards_html.append(card)

    cards_str = "\n".join(cards_html)
    total_approved = sum(1 for p in products if not p["is_regen"])
    total_regen = sum(1 for p in products if p["is_regen"])
    total_all = len(products)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bangle Bliss — Approved Products Hero Image Catalog</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@500;600&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-base: #06080E;
            --bg-card: rgba(14, 20, 33, 0.94);
            --bg-card-hover: rgba(20, 30, 50, 0.98);
            --gold-primary: #D4AF37;
            --gold-light: #F7E7B4;
            --text-main: #F8FAFC;
            --text-muted: #94A3B8;
            --border-subtle: rgba(212, 175, 55, 0.18);
            --border-gold: rgba(212, 175, 55, 0.45);
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background: var(--bg-base);
            color: var(--text-main);
            font-family: 'Outfit', sans-serif;
            padding-bottom: 5rem;
            min-height: 100vh;
            background-image: radial-gradient(circle at 10% 10%, rgba(212, 175, 55, 0.08) 0%, transparent 40%);
            background-attachment: fixed;
        }}
        header {{
            position: sticky;
            top: 0;
            z-index: 500;
            background: rgba(6, 8, 14, 0.95);
            backdrop-filter: blur(16px);
            border-bottom: 1px solid var(--border-subtle);
            padding: 1.25rem 2.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
        }}
        h1 {{
            font-family: 'Cormorant Garamond', serif;
            font-size: 2.2rem;
            background: linear-gradient(135deg, #FFF8E7, #F7E7B4, #D4AF37);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .filter-bar {{
            display: flex;
            gap: 0.6rem;
            align-items: center;
            flex-wrap: wrap;
        }}
        .filter-btn {{
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.12);
            color: var(--text-muted);
            padding: 0.45rem 0.9rem;
            border-radius: 6px;
            font-size: 0.82rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .filter-btn.active {{
            background: var(--gold-primary);
            color: #06080E;
            border-color: var(--gold-primary);
            font-weight: 700;
        }}
        .container {{
            max-width: 1720px;
            margin: 2rem auto;
            padding: 0 2rem;
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 1.5rem;
        }}
        .hero-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: 14px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            transition: all 0.25s;
            box-shadow: 0 8px 25px rgba(0,0,0,0.4);
        }}
        .hero-card:hover {{
            transform: translateY(-4px);
            border-color: var(--border-gold);
            box-shadow: 0 12px 35px rgba(212, 175, 55, 0.15);
        }}
        .hero-img-wrapper {{
            position: relative;
            width: 100%;
            aspect-ratio: 1;
            background: #FFFFFF;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            padding: 10px;
        }}
        .hero-img-wrapper img {{
            width: 100%;
            height: 100%;
            object-fit: contain;
            transition: transform 0.3s;
        }}
        .hero-img-wrapper:hover img {{
            transform: scale(1.04);
        }}
        .card-status-badge {{
            position: absolute;
            top: 10px;
            left: 10px;
            padding: 0.25rem 0.65rem;
            border-radius: 6px;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.02em;
        }}
        .badge-approved {{
            background: rgba(16, 185, 129, 0.9);
            color: #FFF;
        }}
        .badge-regen {{
            background: rgba(245, 158, 11, 0.95);
            color: #000;
        }}
        .zoom-hint {{
            position: absolute;
            bottom: 10px;
            right: 10px;
            background: rgba(0, 0, 0, 0.7);
            color: #FFF;
            font-size: 0.72rem;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            opacity: 0;
            transition: opacity 0.2s;
        }}
        .hero-img-wrapper:hover .zoom-hint {{
            opacity: 1;
        }}
        .hero-card-body {{
            padding: 1.2rem;
            display: flex;
            flex-direction: column;
            gap: 0.65rem;
            flex-grow: 1;
        }}
        .sku-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .sku-tag {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.78rem;
            color: var(--gold-light);
            background: rgba(212, 175, 55, 0.12);
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            border: 1px solid rgba(212, 175, 55, 0.3);
        }}
        .count-tag {{
            font-size: 0.75rem;
            color: #6EE7B7;
            background: rgba(16, 185, 129, 0.12);
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-weight: 600;
        }}
        .hero-title {{
            font-family: 'Cormorant Garamond', serif;
            font-size: 1.25rem;
            color: #FFF;
            line-height: 1.3;
        }}
        .meta-row {{
            display: flex;
            gap: 0.4rem;
            flex-wrap: wrap;
        }}
        .meta-tag {{
            font-size: 0.75rem;
            color: var(--text-muted);
            background: rgba(255, 255, 255, 0.05);
            padding: 0.15rem 0.45rem;
            border-radius: 4px;
        }}
        .card-actions {{
            display: grid;
            grid-template-columns: 1fr auto;
            gap: 0.5rem;
            margin-top: auto;
            padding-top: 0.6rem;
            border-top: 1px solid rgba(255, 255, 255, 0.08);
        }}
        .btn-action {{
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.12);
            color: var(--text-main);
            padding: 0.45rem 0.7rem;
            border-radius: 6px;
            font-size: 0.78rem;
            text-decoration: none;
            text-align: center;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .btn-action:hover {{
            background: var(--gold-primary);
            color: #06080E;
            border-color: var(--gold-primary);
        }}
        .btn-copy {{
            background: rgba(212, 175, 55, 0.12);
            color: var(--gold-light);
            border-color: rgba(212, 175, 55, 0.3);
        }}
        /* Lightbox */
        .lightbox {{
            position: fixed;
            inset: 0;
            background: rgba(3, 4, 8, 0.94);
            backdrop-filter: blur(15px);
            z-index: 1000;
            display: none;
            align-items: center;
            justify-content: center;
            padding: 2rem;
        }}
        .lightbox.active {{ display: flex; }}
        .lb-box {{
            max-width: 90vw;
            max-height: 90vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 1rem;
            position: relative;
        }}
        .lb-img-wrap {{
            max-height: 75vh;
            max-width: 85vw;
            background: #FFFFFF;
            border-radius: 12px;
            padding: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 2px solid var(--gold-primary);
            box-shadow: 0 0 50px rgba(212, 175, 55, 0.3);
        }}
        .lb-img-wrap img {{
            max-height: 70vh;
            max-width: 80vw;
            object-fit: contain;
        }}
        .lb-caption {{
            text-align: center;
        }}
        .lb-close {{
            position: absolute;
            top: -2.5rem;
            right: 0;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: #FFF;
            font-size: 1.5rem;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
    </style>
</head>
<body>
    <header>
        <div>
            <h1>✨ Approved Products — Hero Images</h1>
            <p style="color:var(--text-muted); font-size:0.88rem; margin-top:0.2rem;">
                Official primary listing photos (White Studio 1-white-studio.png) for all {total_all} approved active catalog products.
            </p>
        </div>
        <div class="filter-bar">
            <button class="filter-btn active" onclick="filterGallery('all')">All Active ({total_all})</button>
            <button class="filter-btn" onclick="filterGallery('Approved Catalog')">Approved ({total_approved})</button>
            <button class="filter-btn" onclick="filterGallery('Regenerated (Latest Fix)')">Latest Fixes ({total_regen})</button>
        </div>
    </header>

    <div class="container" id="galleryGrid">
        {cards_str}
    </div>

    <div class="lightbox" id="lightbox" onclick="closeLightbox(event)">
        <div class="lb-box" onclick="event.stopPropagation()">
            <button class="lb-close" onclick="closeLightbox()">✕</button>
            <div class="lb-img-wrap">
                <img id="lbImg" src="" alt="Enlarged Hero">
            </div>
            <div class="lb-caption">
                <h3 id="lbTitle" style="font-family:'Cormorant Garamond',serif; font-size:1.6rem; color:var(--gold-light);"></h3>
                <p id="lbMeta" style="color:var(--text-muted); font-size:0.85rem; margin-top:0.3rem;"></p>
            </div>
        </div>
    </div>

    <script>
        function filterGallery(cat) {{
            const cards = document.querySelectorAll('.hero-card');
            const btns = document.querySelectorAll('.filter-btn');
            btns.forEach(b => b.classList.remove('active'));
            event.target.classList.add('active');

            cards.forEach(c => {{
                if (cat === 'all' || c.getAttribute('data-category') === cat) {{
                    c.style.display = 'flex';
                }} else {{
                    c.style.display = 'none';
                }}
            }});
        }}

        function openLightbox(src, title, meta) {{
            const lb = document.getElementById('lightbox');
            document.getElementById('lbImg').src = src;
            document.getElementById('lbTitle').textContent = title;
            document.getElementById('lbMeta').textContent = meta;
            lb.classList.add('active');
        }}

        function closeLightbox(e) {{
            document.getElementById('lightbox').classList.remove('active');
        }}

        function copyId(id) {{
            navigator.clipboard.writeText(id).then(() => {{
                alert('Copied SKU: ' + id);
            }});
        }}

        document.addEventListener('keydown', (e) => {{
            if (e.key === 'Escape') closeLightbox();
        }});
    </script>
</body>
</html>
"""

def render_markdown(products):
    lines = [
        "# ✨ Bangle Bliss — Master Hero Images Showcase",
        "",
        "> [!NOTE]",
        "> **Catalog Scope:**",
        "> - Primary listing hero shots (`1-white-studio.png`) on clean pure white backgrounds.",
        "> - Displays all **31 active products** (24 previously approved products + 7 latest defect-fixed products).",
        "> - Discontinued/deleted products (`raw01-01`, `raw01-07`, `raw01-19`, `raw01-21`) are fully excluded.",
        "",
        f"🔗 **Interactive Hero Gallery**: [Open Hero Gallery (HTML)](file:///{str(ROOT / 'approved_heroes_gallery.html').replace('\\', '/')})",
        "",
        "---",
        "",
        "## 1. Previously Approved Products (24 Products)",
        "",
    ]

    approved_prods = [p for p in products if not p["is_regen"]]
    for p in approved_prods:
        lines.extend([
            f"### {p['title']}",
            f"- **SKU**: [`{p['id']}`](file:///{p['disk_abs_hero']})",
            f"- **Specs**: Set of {p['count']} | {p['metal']} ({p['variation']})",
            f"- **Status**: ✓ Approved Master",
            "",
            f"![{p['title']} Hero]({p['art_abs_hero']})",
            f"<sub>[Click to Open Full PNG File](file:///{p['disk_abs_hero']})</sub>",
            "",
            "---",
            ""
        ])

    lines.extend([
        "## 2. Latest Regenerated Defect-Fixed Products (7 Products)",
        "",
    ])

    regen_prods = [p for p in products if p["is_regen"]]
    for p in regen_prods:
        lines.extend([
            f"### {p['title']}",
            f"- **SKU**: [`{p['id']}`](file:///{p['disk_abs_hero']})",
            f"- **Specs**: Set of {p['count']} | {p['metal']} ({p['variation']})",
            f"- **Status**: ✨ Latest Regenerated Defect Fix",
            "",
            f"![{p['title']} Hero]({p['art_abs_hero']})",
            f"<sub>[Click to Open Full PNG File](file:///{p['disk_abs_hero']})</sub>",
            "",
            "---",
            ""
        ])

    return "\n".join(lines)

if __name__ == "__main__":
    main()
