"""Round 10: one NEW photo per colour for Flipkart image slot 5 (38 jobs, from the RAW product photos).
Flipkart rejects a row that repeats a photo ("Duplicate images found") and bans size charts / multi-set collages,
so slot 5 needs a genuinely different single-set shot: the 4 bangles lying flat on soft ivory silk, seen at ~45 degrees.
Run: python regen_setup10.py  then  python regen_run10.py  (sequential, one Magic profile)"""
import json
from pathlib import Path
import regen_setup as rs

ROOT = rs.ROOT
SC, RAW3, REF, J = ROOT / "source-crops", ROOT / "jobs" / "_raw3", ROOT / "jobs" / "_ref", ROOT / "jobs"
RAWNOTE = (" The reference image is the REAL product photo: copy its glass colour, bangle thickness, stones and gold details exactly. "
           "Ignore its stand, hand and background.")


def first(p):
    return sorted(Path(p).glob("*"))[0]


# SKU base -> (reference photo, crop box, design, look)
G, K, S = rs.GVK_DESIGN, rs.KMS_DESIGN, rs.KSG_DESIGN
SRC = {
    "GVK-AMB": (SC / "src-gold-vine-kundan-amber.jpg", G, "four translucent light honey-amber peach-gold glass bangles"),
    "GVK-CHR": (SC / "src-gold-vine-kundan-cherry.jpg", G, "four translucent cherry-red glass bangles"),
    "GVK-CRY": (SC / "src-gold-vine-kundan-crystal.jpg", G, "four clear colourless crystal glass bangles (completely transparent glass)"),
    "GVK-EMR": (SC / "src-gold-vine-kundan-emerald.jpg", G, "four translucent emerald-green glass bangles"),
    "GVK-FOR": (SC / "src-gold-vine-kundan-forest.jpg", G, "four translucent forest-green glass bangles"),
    "GVK-IVC": (SC / "src-gold-vine-kundan-ivory.jpg", G, "four translucent ivory-cream glass bangles"),
    "GVK-LAV": (SC / "src-gold-vine-kundan-lavender.jpg", G, "four translucent lavender glass bangles"),
    "GVK-LIM": (SC / "src-gold-vine-kundan-lime.jpg", G, "four translucent bright lime-green glass bangles"),
    "GVK-MOS": (SC / "src-gold-vine-kundan-moss.jpg", G, "four translucent moss-green (olive green) glass bangles"),
    "GVK-MUL": (SC / "src-gold-vine-kundan-multicolour.jpg", G,
                "four glass bangles, each with its OWN ombre colour gradient like the reference: 1 magenta-pink into purple and golden amber; "
                "2 deep ruby-magenta into golden amber; 3 purple-blue into teal blue; 4 green-teal into golden amber"),
    "GVK-PUR": (SC / "src-gold-vine-kundan-purple.jpg", G, "four translucent deep purple glass bangles"),
    "GVK-RBL": (RAW3 / "gvk-royal-blue.jpg", G + " The painted motif is copper-gold.", "four translucent royal-blue (deep cobalt) glass bangles"),
    "GVK-SEA": (SC / "src-gold-vine-kundan-sea-green.jpg", G, "four translucent pale sea-green aqua glass bangles"),
    "GVK-YEL": (SC / "src-gold-vine-kundan-yellow.jpg", G, "four translucent lemon-yellow glass bangles"),
    "KMS-APG": (first(J / "kms-apple-green" / "original"), K, "four translucent bright apple-green glass bangles"),
    "KMS-BTG": (first(J / "kms-bottle-green" / "original"), K, "four translucent deep bottle-green glass bangles"),
    "KMS-DPM": (first(J / "kms-dusty-pink" / "original"), K, "four translucent bright rose-pink glass bangles"),
    "KMS-IVM": (first(J / "kms-ivory-multi" / "original"), K, "four milky ivory-white glass bangles with a soft translucent glow"),
    "KMS-LVP": (RAW3 / "kms-lavender-purple.jpg", K, "four translucent lilac-lavender glass bangles"),
    "KMS-MTM": (first(J / "kms-mint-multi" / "original"), K, "four translucent pale mint-pistachio green glass bangles"),
    "KMS-MUS": (first(J / "kms-mustard-gold" / "original"), K, "four translucent golden mustard-yellow glass bangles"),
    "KMS-RNP": (first(J / "kms-rani-pink" / "original"), K, "four translucent deep rani-pink glass bangles"),
    "KMS-RYP": (RAW3 / "kms-royal-purple.jpg", K, "four translucent vivid royal purple-violet glass bangles"),
    "KMS-TRQ": (RAW3 / "kms-turquoise.jpg", K, "four translucent light turquoise-aqua glass bangles"),
    "KMS-WMM": (first(J / "kms-wine-maroon" / "original"), K, "four translucent deep wine-maroon glass bangles"),
    "KSG-AQU": (RAW3 / "ksg-sky-aqua.jpg", S, "four very pale transparent sky-aqua blue glass bangles"),
    "KSG-COR": (REF / "ksg-coral-peach.jpg", S, "four translucent coral-peach glass bangles"),
    "KSG-EMR": (RAW3 / "ksg-emerald-green.jpg", S, "four translucent emerald-green glass bangles"),
    "KSG-LIM": (first(J / "ksg-lime-green" / "original"), S, "four translucent lime-green glass bangles"),
    "KSG-LMY": (RAW3 / "ksg-lemon-yellow.jpg", S, "four translucent golden lemon-yellow glass bangles"),
    "KSG-MAG": (RAW3 / "ksg-magenta.jpg", S, "four translucent magenta-purple (fuchsia) glass bangles"),
    "KSG-MNT": (ROOT / "raw" / "Design !" / "image 9.jpeg", S, "four translucent pale mint-green glass bangles"),
    "KSG-MRN": (RAW3 / "ksg-maroon.jpg", S, "four translucent deep maroon-red glass bangles"),
    "KSG-ORC": (RAW3 / "ksg-orchid-pink.jpg", S, "four translucent orchid-pink glass bangles"),
    "KSG-PGR": (RAW3 / "ksg-parrot-green.jpg", S, "four translucent vivid yellow-green parrot-green glass bangles"),
    "KSG-PLM": (RAW3 / "ksg-plum-wine.jpg", S, "four translucent deep plum-wine burgundy glass bangles"),
    "KSG-RED": (RAW3 / "ksg-ruby-red.jpg", S, "four translucent ruby-red glass bangles"),
    "KSG-RST": (first(J / "ksg-rust-orange" / "original"), S, "four translucent rust-orange glass bangles"),
}
BOX = {"KSG-MNT": (0.33, 0.40, 0.60, 0.70)}


def flatlay(look, design):
    return ("Create a new photograph: premium e-commerce flat-lay of " + look + " lying FLAT on soft plain ivory silk fabric, "
            "photographed from a 45-degree angle above so the stones on the outer face of every bangle are visible. "
            "The four bangles lie in a neat 2 x 2 square arrangement, close together but NOT overlapping and NOT stacked, "
            "each bangle a complete full ring fully inside the frame. Soft even daylight, gentle shadows, sharp focus, nothing else in "
            "the frame: no hand, no flowers, no props, no box, no text. " + design + RAWNOTE + rs.STRICT)


def main():
    made = []
    for sku, (ref, design, look) in SRC.items():
        assert ref.exists(), ref
        made.append(rs.make_job("r10-" + sku.lower(), ref, BOX.get(sku, (0, 0, 1, 1)), [("5-flatlay", flatlay(look, design))]))
    (ROOT / "jobs" / "rg10_jobs.json").write_text(json.dumps([n for n, _ in made]))
    print(len(made), "jobs")


if __name__ == "__main__":
    main()
