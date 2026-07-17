#!/usr/bin/env python3
"""Photographic build-menu cameos cut from the concept-art source scenes in
docs/concept-art/cameo-sources/ (see that folder's README and
docs/LICENSE_NOTES.md for provenance).

This is the "real-style" cameo pass the player asked for: instead of the
flat programmatic motif gen_concept_art.py draws, each actor's cameo is a
cropped region of a rendered scene, cover-fitted to the 64x48 cameo frame,
then given the *same* 1px border and baked uppercase name label the
programmatic cameos use (draw_icon_label / the border recipe are imported
from gen_concept_art so the two styles stay visually consistent where they
meet in the sidebar).

Only the `*icon.png` cameos are touched -- the in-world building/unit sprite
sheets stay exactly as gen_concept_art.py emits them (indexed, team-colored).
Cameos render on the fixed `chrome` palette and are not team-colored, so they
can be truecolor, matching the ported stock RA cameos.

Usage:
    pip install pillow
    python3 gen_photo_cameos.py
Writes the cameo PNGs directly into this directory (mods/sungrid/bits/).
"""
import os
from PIL import Image, ImageDraw

# Reuse the cameo frame size, colors, label baker, border recipe, and PNG
# writer from the programmatic generator so both cameo styles match.
from gen_concept_art import (
    ICON_W, ICON_H, ICON_LABELS,
    LEGACY_GRAY, LEGACY_GRAY_DARK,
    lit, dim, draw_icon_label, save_pngsheet,
)

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "..", "..", "docs", "concept-art", "cameo-sources")

# actor-icon basename -> (source filename, crop box in source pixels).
# Boxes were tuned against the committed source renders via a crop-check
# contact sheet; re-tune here if the sources are ever replaced.
CROPS = {
    # --- desert-base.png (the spec-sheet scene: covers most of the roster) ---
    "sgpwr":  ("desert-base.png", (20, 220, 300, 335)),    # solar panels
    "sgapwr": ("desert-base.png", (330, 195, 485, 320)),   # concentrator dish + panels
    "sgcry":  ("desert-base.png", (0, 300, 300, 485)),     # server racks
    "sgdai":  ("desert-base.png", (575, 235, 735, 330)),   # stacked compute modules
    "sgdro":  ("desert-base.png", (875, 465, 1065, 575)),  # airborne recon quadcopter
    "sgdrn":  ("desert-base.png", (785, 545, 1105, 755)),  # octagonal landing bay
    # --- desert_base2.png (wider, higher-quality re-render of the same base) ---
    "sghyd":  ("desert_base2.png", (95, 85, 235, 320)),     # H2 tanks
    "sgshl":  ("desert_base2.png", (5, 455, 330, 628)),     # SUNGRID PROTOCOL bunker
    "sgwnd":  ("desert_base2.png", (975, 90, 1190, 215)),   # wind turbines
    "sgsns":  ("desert_base2.png", (693, 348, 802, 485)),   # lattice antenna tower + dish
    "sgdrs":  ("desert_base2.png", (928, 396, 1072, 480)),  # armed strike quadcopter
    "sgtur":  ("desert_base2.png", (1073, 298, 1207, 396)), # gatling defense turret
    "sgdra":  ("desert_base2.png", (418, 193, 828, 326)),   # solar-frame fabrication hangar
    "arct":   ("desert_base2.png", (438, 488, 582, 606)),   # purple arc-discharge turret
    "sgrel":  ("desert_base2.png", (683, 450, 807, 525)),   # power-routing / relay gear
    "sghau":  ("desert_base2.png", (812, 528, 1044, 704)),  # 6-wheel unmanned scrap rover
    "rcyd":   ("desert-base.png",  (250, 556, 398, 668)),   # bin of reclaimed scrap metal
    # --- grid-scene.png (the NOVAYA ZARYA hero scene) ---
    "disr":   ("grid-scene.png", (470, 880, 640, 1080)),   # the two engineers
}

# Shorter baked cameo labels where the full in-game name (ICON_LABELS, mirroring
# rules.ftl) is too long to read cleanly at 64px. Cameo-only cosmetic text; the
# hover tooltip still shows the full name.
LABEL_OVERRIDES = {
    "sgdai": "AI Datacenter",
    "sgdra": "Aerial Fab",
    "sgapwr": "Adv Solar Array",
    "sghyd": "Hydrogen Plt",
    "sgshl": "Res Shelter",
    "sgwnd": "Wind Turbine",
    "disr": "Disruptor",
    "sgtur": "Grid Turret",
    "sgrel": "Grid Relay",
    "rcyd": "Recycling Dpt",
}


def cover_fit(img, w, h):
    """Scale to fill w x h preserving aspect, then center-crop the overflow --
    the crop already frames the subject, so the subject stays centered."""
    scale = max(w / img.width, h / img.height)
    rw, rh = max(w, round(img.width * scale)), max(h, round(img.height * scale))
    img = img.resize((rw, rh), Image.LANCZOS)
    left, top = (rw - w) // 2, (rh - h) // 2
    return img.crop((left, top, left + w, top + h))


def vignette(icon):
    """Subtle edge darkening so the full-bleed photo reads as a framed cameo
    rather than a raw rectangle, consistent with the programmatic panels."""
    d = ImageDraw.Draw(icon, "RGBA")
    for i, a in enumerate((70, 45, 22)):  # 3-ring inset darkening
        d.rectangle([i, i, ICON_W - 1 - i, ICON_H - 1 - i], outline=(0, 0, 0, a))


def make_photo_icon(source, box, label):
    crop = Image.open(os.path.join(SRC, source)).convert("RGBA")
    icon = cover_fit(crop.crop(box), ICON_W, ICON_H)
    vignette(icon)
    d = ImageDraw.Draw(icon, "RGBA")
    if label:
        draw_icon_label(icon, label)
    # Border: dark outer frame with a lit top edge (same as make_icon).
    d.rectangle([0, 0, ICON_W - 1, ICON_H - 1], outline=dim(LEGACY_GRAY_DARK, 0.3))
    d.line([(1, 1), (ICON_W - 2, 1)], fill=lit(LEGACY_GRAY, 0.05))
    return icon


def main():
    for name, (source, box) in CROPS.items():
        label = LABEL_OVERRIDES.get(name, ICON_LABELS.get(name))
        icon = make_photo_icon(source, box, label)
        save_pngsheet(icon, f"{name}icon.png", ICON_W, ICON_H, 1)
    print("done")


if __name__ == "__main__":
    main()
