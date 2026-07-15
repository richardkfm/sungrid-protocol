#!/usr/bin/env python3
"""First-pass custom art for Sungrid-original buildings/units (docs/BACKLOG.md
issue #34; see docs/ART_DIRECTION.md). Extends the "programmatic first pass
now, real artist pass later" approach docs/BACKLOG.md issue #12 established
for Solar Array (mods/sungrid/bits/sgpwr.png/sgapwr.png) to the rest of the
roster that has no real-world/mods/ra equivalent and, until now, silently
reused an unrelated existing building's or unit's sprite wholesale -- a real
readability bug under docs/ART_DIRECTION.md's "every actor must have a
distinct silhouette" rule, not just missing flavor (e.g. SGTUR, SGWND, and
the stock SAM Site all rendered the *same* sprite before this pass).

SGHAU (Hauler Drone) also gets dedicated art here, reversing an earlier scoping
call to leave it on HARV's (Ore Truck) chassis: the two rendered identically,
which caused real gameplay confusion (a Hauler Drone reads as an idle/broken
Ore Truck since it never appears to collect Ore -- it collects Scrap). It
needs three parallel image variants (empty/half/full cargo, matching
WithHarvesterSpriteBody.ImageByFullness) with identical idle/harvest/dock/
dock-loop frame layouts across all three -- see sghau_frames()/SGHAU_* below.

Stock-RA-derived units (tanks, infantry, aircraft, ships) are out of scope --
see docs/ART_DIRECTION.md's Phase 7 section for that larger, separately
tracked effort.

Ground rules carried over from issue #12:
  - PngSheet format (mod.yaml already lists PngSheet in SpriteFormats), not
    hand-authored indexed .shp -- no engine/dedicated pixel-art tool available
    in this environment.
  - Frame metadata is written directly as PNG tEXt chunks (FrameSize,
    FrameAmount), matching the exact keys/format already verified working in
    sgpwr.png/sgapwr.png (loaded and rendered correctly in a live headless
    skirmish per issue #12) -- reverse-engineered from those files since no
    engine `utility --png-sheet-import` is available here to generate it.
  - Buildings keep the *same* footprint/Dimensions and reuse the bib/minibib
    decal + dead-animation assets already wired for whichever building they
    used to borrow art from (bib decals are already shared across unrelated
    buildings throughout this ruleset's stock content, e.g. KENN borrows
    mbSILO -- this is normal, not a new corner cut).
  - This is a first pass, not final production art: flat/geometric shapes in
    the locked palette below, not hand-painted detail. A real artist pass is
    still open follow-up work, same status as Solar Array's.

Usage:
    pip install pillow
    python3 gen_concept_art.py
Writes all PNGs directly into this directory (mods/sungrid/bits/).
"""
import os
import math
from PIL import Image, ImageDraw, PngImagePlugin

HERE = os.path.dirname(os.path.abspath(__file__))

# Locked palette (docs/ART_DIRECTION.md).
GREEN_PRIMARY = (0x2E, 0x7D, 0x46)
GREEN_ACCENT = (0x8B, 0xC3, 0x4A)
PANEL_BLUEBLACK = (0x16, 0x23, 0x2E)
SUN_GOLD = (0xE8, 0xA9, 0x3D)

# Military/industrial counterpoint (legacy tech, per ART_DIRECTION.md) and a
# couple of neutral/structural tones needed for the ground strip all buildings
# share, matching sgpwr.png's established visual grammar.
LEGACY_GRAY = (0x5A, 0x55, 0x4C)
LEGACY_GRAY_DARK = (0x30, 0x2C, 0x28)
RUST = (0x8B, 0x3F, 0x2A)
CONCRETE = (0x4A, 0x47, 0x42)
DIRT = (0x6E, 0x58, 0x33)
GRASS = (0x3B, 0x63, 0x38)
POLE_DARK = (0x1C, 0x1C, 0x1A)
DAMAGE_SCORCH = (0x12, 0x10, 0x0E)


def save_pngsheet(img, name, frame_w, frame_h, frame_amount):
    meta = PngImagePlugin.PngInfo()
    meta.add_text("FrameSize", f"{frame_w},{frame_h}")
    meta.add_text("FrameAmount", str(frame_amount))
    path = os.path.join(HERE, name)
    img.save(path, pnginfo=meta)
    print(f"wrote {name}  {img.size}  frame={frame_w}x{frame_h} x{frame_amount}")


def canvas(w, h):
    return Image.new("RGBA", (w, h), (0, 0, 0, 0))


# ---------------------------------------------------------------------------
# Shared "ground strip" grammar, matching sgpwr.png/sgapwr.png: a concrete
# base band with grass tufts at the outer corners and dirt speckle, optional
# gold conduit band above it signaling grid connection.
# ---------------------------------------------------------------------------

def draw_ground_strip(d, x0, x1, y0, y1, seed=0):
    d.rectangle([x0, y0, x1, y1], fill=CONCRETE)
    tuft = max(3, (x1 - x0) // 8)
    d.rectangle([x0, y0, x0 + tuft, y1], fill=GRASS)
    d.rectangle([x1 - tuft, y0, x1, y1], fill=GRASS)
    # Deterministic dirt speckle (no RNG import needed for a handful of dots).
    for i in range((x1 - x0) // 6):
        px = x0 + tuft + 2 + (i * 7 + seed * 3) % max(1, (x1 - x0) - 2 * tuft - 4)
        py = y0 + 1 + (i * 5 + seed) % max(1, (y1 - y0) - 2)
        d.point((px, py), fill=DIRT)


def draw_gold_band(d, x0, x1, y0, y1):
    d.rectangle([x0, y0, x1, y1], fill=SUN_GOLD)


def add_damage(img, blotches):
    """blotches: list of (x, y, r) small scorch marks + a couple rust flecks."""
    d = ImageDraw.Draw(img)
    for (x, y, r) in blotches:
        d.ellipse([x - r, y - r, x + r, y + r], fill=DAMAGE_SCORCH)
    for (x, y) in blotches[:2]:
        d.point((x[0] if isinstance(x, tuple) else x, y), fill=RUST)
    return img


def two_frame_sheet(draw_fn, frame_w, frame_h, damage_blotches):
    sheet = canvas(frame_w * 2, frame_h)
    idle = canvas(frame_w, frame_h)
    draw_fn(ImageDraw.Draw(idle))
    sheet.paste(idle, (0, 0), idle)
    damaged = idle.copy()
    dd = ImageDraw.Draw(damaged)
    for (x, y, r) in damage_blotches:
        dd.ellipse([x - r, y - r, x + r, y + r], fill=DAMAGE_SCORCH)
    if damage_blotches:
        rx, ry, _ = damage_blotches[0]
        dd.rectangle([rx - 1, ry, rx + 1, ry + 2], fill=RUST)
    sheet.paste(damaged, (frame_w, 0), damaged)
    return sheet


def make_icon(draw_fn, frame_w, frame_h, icon_w=32, icon_h=24):
    frame = canvas(frame_w, frame_h)
    draw_fn(ImageDraw.Draw(frame), frame_w, frame_h)
    return frame.resize((icon_w, icon_h), Image.LANCZOS)


# ---------------------------------------------------------------------------
# Per-building motifs. Each draw_fn renders one undamaged frame into a
# frame_w x frame_h transparent canvas.
# ---------------------------------------------------------------------------

FAM23_W, FAM23_H = 66, 54   # 2x3 footprint family (matches sgpwr.png)
FAM33_W, FAM33_H = 90, 60   # 3x3 footprint family (matches sgapwr.png)
SGSHL_W, SGSHL_H = 72, 50   # 2x2 footprint
SG1x1_W, SG1x1_H = 40, 36   # 1x1 footprint


def sgcry_draw(d, w=FAM23_W, h=FAM23_H):
    ground_y0, ground_y1 = h - 12, h
    gold_y0, gold_y1 = ground_y0 - 8, ground_y0
    draw_ground_strip(d, 2, w - 2, ground_y0, ground_y1, seed=1)
    draw_gold_band(d, 6, w - 6, gold_y0, gold_y1)
    # Two rows x three columns of scavenged server-rack blocks.
    cols, rows = 3, 2
    block_w, block_h = 14, 12
    gap = 3
    total_w = cols * block_w + (cols - 1) * gap
    x0 = (w - total_w) // 2
    for r in range(rows):
        for c in range(cols):
            bx = x0 + c * (block_w + gap)
            by = gold_y0 - (r + 1) * (block_h + 2)
            d.rectangle([bx, by, bx + block_w, by + block_h], fill=LEGACY_GRAY, outline=LEGACY_GRAY_DARK)
            # Blinking status light, and a rust fleck on the outer racks for wear.
            d.point((bx + 3, by + 3), fill=SUN_GOLD)
            if c in (0, cols - 1) and r == 0:
                d.rectangle([bx + block_w - 4, by + block_h - 4, bx + block_w - 1, by + block_h - 1], fill=RUST)
            d.line([bx, by + block_h // 2, bx, by], fill=POLE_DARK)
    return {"blotches": [(x0 + total_w // 2, gold_y0 - 6, 3), (x0 + 4, gold_y0 + 2, 2)]}


def sgdai_draw(d, w=FAM23_W, h=FAM23_H):
    ground_y0, ground_y1 = h - 12, h
    gold_y0, gold_y1 = ground_y0 - 8, ground_y0
    draw_ground_strip(d, 2, w - 2, ground_y0, ground_y1, seed=2)
    draw_gold_band(d, 6, w - 6, gold_y0, gold_y1)
    cols, rows = 4, 3
    block_w, block_h = 10, 8
    gap = 1
    total_w = cols * block_w + (cols - 1) * gap
    x0 = (w - total_w) // 2
    top = gold_y0 - rows * (block_h + gap)
    for r in range(rows):
        for c in range(cols):
            bx = x0 + c * (block_w + gap)
            by = top + r * (block_h + gap)
            d.rectangle([bx, by, bx + block_w, by + block_h], fill=PANEL_BLUEBLACK, outline=SUN_GOLD)
    # Data line linking the rack tops -- the "AI" identity signal.
    d.line([x0, top - 2, x0 + total_w, top - 2], fill=GREEN_ACCENT)
    return {"blotches": [(x0 + total_w // 2, top + 4, 2)]}


def sgdrn_draw(d, w=FAM23_W, h=FAM23_H):
    ground_y0, ground_y1 = h - 12, h
    gold_y0, gold_y1 = ground_y0 - 8, ground_y0
    draw_ground_strip(d, 2, w - 2, ground_y0, ground_y1, seed=3)
    draw_gold_band(d, 6, w - 6, gold_y0, gold_y1)
    # Improvised, asymmetric open scaffold/gantry rather than an enclosed hangar.
    d.line([(10, gold_y0), (24, gold_y0 - 22), (24, gold_y0)], fill=GREEN_PRIMARY, width=2)
    d.line([(w - 12, gold_y0), (w - 26, gold_y0 - 18), (w - 26, gold_y0)], fill=GREEN_PRIMARY, width=2)
    d.line([(24, gold_y0 - 20), (w - 26, gold_y0 - 16)], fill=GREEN_PRIMARY, width=1)
    # Parked drone on a small raised pad in the middle.
    pad_x0, pad_x1 = w // 2 - 10, w // 2 + 10
    d.rectangle([pad_x0, gold_y0 - 6, pad_x1, gold_y0], fill=LEGACY_GRAY)
    cx, cy = w // 2, gold_y0 - 10
    d.polygon([(cx, cy - 5), (cx + 5, cy), (cx, cy + 5), (cx - 5, cy)], fill=GREEN_ACCENT)
    return {"blotches": [(cx, cy, 2)]}


def sgdra_draw(d, w=FAM23_W, h=FAM23_H):
    ground_y0, ground_y1 = h - 12, h
    gold_y0, gold_y1 = ground_y0 - 8, ground_y0
    draw_ground_strip(d, 2, w - 2, ground_y0, ground_y1, seed=4)
    draw_gold_band(d, 6, w - 6, gold_y0, gold_y1)
    # Enclosed, symmetric hangar box -- the hardened Consortium mirror of SGDRN.
    hx0, hx1 = 8, w - 8
    hy0, hy1 = gold_y0 - 26, gold_y0
    d.rectangle([hx0, hy0, hx1, hy1], fill=PANEL_BLUEBLACK, outline=SUN_GOLD)
    mid = (hx0 + hx1) // 2
    d.line([(mid, hy0), (mid, hy1)], fill=SUN_GOLD)
    d.line([(hx0 + 3, hy0), (hx0 + 3, hy1)], fill=SUN_GOLD)
    d.line([(hx1 - 3, hy0), (hx1 - 3, hy1)], fill=SUN_GOLD)
    return {"blotches": [(mid, (hy0 + hy1) // 2, 3)]}


def sgshl_draw(d, w=SGSHL_W, h=SGSHL_H):
    ground_y0, ground_y1 = h - 10, h
    draw_ground_strip(d, 2, w - 2, ground_y0, ground_y1, seed=5)
    # Sandbag row along the front edge, per ART_DIRECTION.md's "not utopian" guardrail.
    bag_w = 6
    for bx in range(4, w - 4, bag_w + 1):
        d.ellipse([bx, ground_y0 - 3, bx + bag_w, ground_y0 + 2], fill=DIRT, outline=LEGACY_GRAY_DARK)
    # Hardened dome/mound roof.
    dome_y0 = 8
    d.ellipse([6, dome_y0, w - 6, ground_y0 + 6], fill=GREEN_PRIMARY, outline=LEGACY_GRAY_DARK)
    d.ellipse([w // 2 - 3, dome_y0 + 2, w // 2 + 3, dome_y0 + 8], fill=SUN_GOLD)
    return {"blotches": [(w // 2, dome_y0 + 16, 4)]}


def sgsns_draw(d, w=SG1x1_W, h=SG1x1_H):
    ground_y0, ground_y1 = h - 8, h
    draw_ground_strip(d, 2, w - 2, ground_y0, ground_y1, seed=6)
    cx = w // 2
    mast_top = 10
    d.line([(cx - 6, ground_y0), (cx, mast_top)], fill=LEGACY_GRAY_DARK)
    d.line([(cx + 6, ground_y0), (cx, mast_top)], fill=LEGACY_GRAY_DARK)
    d.line([(cx, ground_y0), (cx, mast_top)], fill=LEGACY_GRAY_DARK)
    d.ellipse([cx - 10, mast_top - 8, cx + 10, mast_top + 6], fill=PANEL_BLUEBLACK, outline=SUN_GOLD)
    d.arc([cx - 7, mast_top - 5, cx + 7, mast_top + 3], 200, 340, fill=GREEN_ACCENT)
    d.arc([cx - 4, mast_top - 3, cx + 4, mast_top + 1], 200, 340, fill=GREEN_ACCENT)
    return {"blotches": [(cx, mast_top, 2)]}


def sgrel_draw(d, w=SG1x1_W, h=SG1x1_H):
    ground_y0, ground_y1 = h - 8, h
    draw_ground_strip(d, 2, w - 2, ground_y0, ground_y1, seed=7)
    cx = w // 2
    pylon_top = 6
    d.polygon([(cx - 6, ground_y0), (cx + 6, ground_y0), (cx + 2, pylon_top), (cx - 2, pylon_top)], fill=PANEL_BLUEBLACK, outline=LEGACY_GRAY_DARK)
    node_y = pylon_top - 2
    d.ellipse([cx - 4, node_y - 4, cx + 4, node_y + 4], fill=SUN_GOLD)
    for ang in (200, 270, 340):
        rad = math.radians(ang)
        ex, ey = cx + 14 * math.cos(rad), node_y + 14 * math.sin(rad)
        d.line([(cx, node_y), (ex, ey)], fill=SUN_GOLD)
    return {"blotches": [(cx, node_y + 8, 2)]}


def arct_draw(d, w=SG1x1_W, h=SG1x1_H):
    """Arc Turret: a squat discharge base with a forked electrode, deliberately
    NOT a nozzle/fuel-tank silhouette so it reads as "electric discharge"
    rather than "flamethrower" -- see docs/BACKLOG.md issue #36 (reverses the
    FTUR chassis reuse issue #14 left in place)."""
    ground_y0, ground_y1 = h - 8, h
    draw_ground_strip(d, 2, w - 2, ground_y0, ground_y1, seed=10)
    cx = w // 2
    base_top = ground_y0 - 10
    d.rounded_rectangle([cx - 9, base_top, cx + 9, ground_y0], radius=4, fill=PANEL_BLUEBLACK, outline=GREEN_ACCENT)
    rod_top = base_top - 12
    d.line([(cx, base_top), (cx, rod_top)], fill=LEGACY_GRAY_DARK, width=2)
    # Forked electrode + a small arc bridging the two prongs -- a discharge
    # gap, not a flame nozzle.
    d.line([(cx, rod_top), (cx - 5, rod_top - 6)], fill=SUN_GOLD, width=2)
    d.line([(cx, rod_top), (cx + 5, rod_top - 6)], fill=SUN_GOLD, width=2)
    d.line([(cx - 3, rod_top - 3), (cx + 3, rod_top - 4)], fill=GREEN_ACCENT)
    return {"blotches": [(cx, base_top + 2, 2)]}


def sgtur_base_draw(d, w, h):
    """Non-rotating reference frame, used only to derive the icon."""
    cx, cy = w // 2, h // 2 + 4
    d.ellipse([cx - 16, cy - 12, cx + 16, cy + 12], fill=PANEL_BLUEBLACK, outline=SUN_GOLD)
    d.rectangle([cx - 3, cy - 20, cx + 3, cy], fill=GREEN_PRIMARY, outline=GREEN_ACCENT)
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=SUN_GOLD)


def sgwnd_draw(d, w=FAM23_W, h=FAM23_H):
    ground_y0, ground_y1 = h - 12, h
    gold_y0, gold_y1 = ground_y0 - 8, ground_y0
    draw_ground_strip(d, 2, w - 2, ground_y0, ground_y1, seed=8)
    draw_gold_band(d, 6, w - 6, gold_y0, gold_y1)
    # Two slim turbine poles/rotors -- deliberately sparser than Solar Array's
    # dense panel frames, matching Wind Turbine's "cheap, mass-producible" fantasy.
    for cx in (w // 3, 2 * w // 3):
        hub_y = gold_y0 - 26
        d.line([(cx, gold_y0), (cx, hub_y)], fill=LEGACY_GRAY_DARK, width=2)
        d.ellipse([cx - 2, hub_y - 2, cx + 2, hub_y + 2], fill=SUN_GOLD)
        for ang in (90, 210, 330):
            rad = math.radians(ang)
            ex, ey = cx + 13 * math.cos(rad), hub_y - 13 * math.sin(rad)
            d.line([(cx, hub_y), (ex, ey)], fill=GREEN_ACCENT, width=2)
    return {"blotches": [(w // 3, gold_y0 - 10, 2)]}


def sghyd_draw(d, w=FAM33_W, h=FAM33_H):
    ground_y0, ground_y1 = h - 13, h
    gold_y0, gold_y1 = ground_y0 - 9, ground_y0
    draw_ground_strip(d, 2, w - 2, ground_y0, ground_y1, seed=9)
    draw_gold_band(d, 5, w - 5, gold_y0, gold_y1)
    # Two large hardened tanks -- a bigger, heavier industrial-cluster read
    # matching Hydrogen Plant's expensive/late-game/Heavy-armor identity.
    tank_w, tank_h = 26, 30
    tank_top = gold_y0 - tank_h
    for cx in (w // 2 - 20, w // 2 + 20):
        tx0, tx1 = cx - tank_w // 2, cx + tank_w // 2
        d.rounded_rectangle([tx0, tank_top, tx1, gold_y0], radius=6, fill=PANEL_BLUEBLACK, outline=LEGACY_GRAY_DARK)
        for by in (tank_top + 8, tank_top + 18):
            d.line([(tx0 + 1, by), (tx1 - 1, by)], fill=SUN_GOLD)
    d.line([(w // 2 - 20 + tank_w // 2, tank_top + 13), (w // 2 + 20 - tank_w // 2, tank_top + 13)], fill=SUN_GOLD, width=2)
    return {"blotches": [(w // 2, tank_top + 15, 3), (w // 2 - 20, tank_top + 8, 2)]}


# ---------------------------------------------------------------------------
# Rotating sprites: turret (32 facings x2 for damaged) and the two drone
# bodies (32 facings, no damaged variant -- matching tran/mh60/heli, which
# don't define one either).
# ---------------------------------------------------------------------------

def rotated_frames(draw_fn, frame_w, frame_h, n=32, extra_frames=None):
    """draw_fn renders one north-facing (up) frame; classic facing convention
    is frame 0 = up, winding clockwise in equal steps."""
    base = canvas(frame_w, frame_h)
    draw_fn(ImageDraw.Draw(base), frame_w, frame_h)
    frames = []
    for i in range(n):
        angle = i * (360.0 / n)
        frames.append(base.rotate(angle, resample=Image.BICUBIC, center=(frame_w / 2, frame_h / 2)))
    if extra_frames:
        frames.extend(extra_frames)
    sheet = canvas(frame_w * len(frames), frame_h)
    for i, f in enumerate(frames):
        sheet.paste(f, (i * frame_w, 0), f)
    return sheet


def sgtur_turret_draw(d, w, h):
    cx, cy = w // 2, h // 2 + 6
    d.rectangle([cx - 3, cy - h // 2 + 4, cx + 3, cy], fill=GREEN_PRIMARY, outline=GREEN_ACCENT)
    d.ellipse([cx - 8, cy - 6, cx + 8, cy + 6], fill=PANEL_BLUEBLACK, outline=SUN_GOLD)
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=SUN_GOLD)


def sgtur_turret_damaged_draw(d, w, h):
    cx, cy = w // 2, h // 2 + 6
    d.rectangle([cx - 3, cy - h // 2 + 4, cx + 3, cy], fill=LEGACY_GRAY, outline=LEGACY_GRAY_DARK)
    d.ellipse([cx - 8, cy - 6, cx + 8, cy + 6], fill=PANEL_BLUEBLACK, outline=RUST)
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=RUST)
    d.point((cx - 5, cy - 8), fill=DAMAGE_SCORCH)


def sgdro_body_draw(d, w, h):
    cx, cy = w // 2, h // 2
    d.polygon([(cx, cy - 8), (cx + 6, cy), (cx, cy + 8), (cx - 6, cy)], fill=GREEN_PRIMARY, outline=GREEN_ACCENT)
    for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        ex, ey = cx + dx * 10, cy + dy * 7
        d.line([(cx, cy), (ex, ey)], fill=LEGACY_GRAY_DARK)
        d.ellipse([ex - 2, ey - 2, ex + 2, ey + 2], fill=(0xB0, 0xB0, 0xA8, 160))
    d.point((cx, cy - 6), fill=SUN_GOLD)


def sgdrs_body_draw(d, w, h):
    cx, cy = w // 2, h // 2
    d.polygon([(cx, cy - 9), (cx + 7, cy), (cx, cy + 9), (cx - 7, cy)], fill=PANEL_BLUEBLACK, outline=SUN_GOLD)
    for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        ex, ey = cx + dx * 11, cy + dy * 8
        d.line([(cx, cy), (ex, ey)], fill=LEGACY_GRAY_DARK)
        d.ellipse([ex - 2, ey - 2, ex + 2, ey + 2], fill=(0xB0, 0xB0, 0xA8, 160))
        if dy == 1:
            d.rectangle([ex - 2, ey - 1, ex + 2, ey + 3], fill=RUST)
    d.point((cx, cy - 7), fill=SUN_GOLD)


# ---------------------------------------------------------------------------
# Hauler Drone (SGHAU): a small hex-chassis cargo sled, deliberately NOT a
# truck silhouette so it can never again be mistaken for HARV (Ore Truck) --
# see docs/BACKLOG.md issue #34's SGHAU follow-up. Needs three parallel
# fullness-state images (empty/half/full) with an identical idle(32)/
# harvest(8)/dock(8)/dock-loop(7) frame layout across all three, matching
# WithHarvesterSpriteBody.ImageByFullness: harvempty, harvhalf, harv's
# convention -- the fullness itself is which image is active, not an
# animation baked into any one image's frames.
# ---------------------------------------------------------------------------

SGHAU_W, SGHAU_H = 34, 28
SGHAU_FULLNESS_FRAC = {"empty": 0.0, "half": 0.5, "full": 1.0}


def sghau_draw(d, w, h, fullness="full", pose="idle", light_on=True):
    cx, cy = w // 2, h // 2
    # Low hex chassis on a sled base -- reads as a cargo sled, not a truck bed.
    d.polygon(
        [(cx, cy - 10), (cx + 9, cy - 4), (cx + 9, cy + 6), (cx, cy + 11), (cx - 9, cy + 6), (cx - 9, cy - 4)],
        fill=LEGACY_GRAY, outline=LEGACY_GRAY_DARK,
    )
    # Front magnetic scoop, lowered during the harvest pose.
    scoop_cy = cy - 8 if pose == "idle" else cy - 4
    d.arc([cx - 7, scoop_cy - 4, cx + 7, scoop_cy + 4], 200, 340, fill=GREEN_ACCENT, width=2)
    # Rear cargo canister -- fill level reads the fullness state directly, the
    # same "show the cargo" grammar HARV's own bed uses.
    can_x0, can_x1 = cx - 5, cx + 5
    can_y0, can_y1 = cy + 1, cy + 9
    d.rectangle([can_x0, can_y0, can_x1, can_y1], fill=PANEL_BLUEBLACK, outline=SUN_GOLD)
    frac = SGHAU_FULLNESS_FRAC[fullness]
    if frac > 0:
        fill_y0 = can_y1 - round((can_y1 - can_y0) * frac)
        d.rectangle([can_x0 + 1, fill_y0, can_x1 - 1, can_y1 - 1], fill=GREEN_ACCENT)
    if light_on:
        d.point((cx, cy - 10), fill=SUN_GOLD)


def _frame_list_rotated(draw_fn, w, h, n):
    base = canvas(w, h)
    draw_fn(ImageDraw.Draw(base), w, h)
    return [base.rotate(i * (360.0 / n), resample=Image.BICUBIC, center=(w / 2, h / 2)) for i in range(n)]


def sghau_frames(fullness):
    """One fullness variant's full frame list: idle(32) + harvest(8) +
    dock(8) + dock-loop(7) = 55 frames, in that order (matching the Start
    offsets wired in sequences/vehicles.yaml)."""
    idle = _frame_list_rotated(lambda d, w, h: sghau_draw(d, w, h, fullness, "idle"), SGHAU_W, SGHAU_H, 32)
    harvest = _frame_list_rotated(lambda d, w, h: sghau_draw(d, w, h, fullness, "scoop"), SGHAU_W, SGHAU_H, 8)
    dock = []
    for i in range(8):
        pose = "idle" if i % 2 == 0 else "scoop"
        f = canvas(SGHAU_W, SGHAU_H)
        sghau_draw(ImageDraw.Draw(f), SGHAU_W, SGHAU_H, fullness, pose)
        dock.append(f)
    dock_loop = []
    for i in range(7):
        f = canvas(SGHAU_W, SGHAU_H)
        sghau_draw(ImageDraw.Draw(f), SGHAU_W, SGHAU_H, fullness, "idle", light_on=(i % 2 == 0))
        dock_loop.append(f)
    return idle + harvest + dock + dock_loop


# ---------------------------------------------------------------------------
# Disruptor Trooper (DISR): dedicated infantry art, reversing the "leave it
# on E4's (Flame Infantry) chassis" call issue #14 made -- same rationale as
# SGHAU's reversal above (see docs/BACKLOG.md issue #36): the sprite still
# visually read as a flamethrower trooper after the name/weapon swap to an
# Arc Turret-style electric discharge, which is exactly the kind of
# silhouette/identity mismatch docs/ART_DIRECTION.md rules out.
#
# Self-contained new sheet covering every sequence disr: actually needs:
# stand/stand2/run/shoot/prone-run/prone-shoot (all facing-dependent, laid
# out facing-major -- Start + facing*Length + pose, see docs/BACKLOG.md
# issue #35 for why) plus idle1/idle2/die1-5/parachute (single-direction, no
# Facings key). prone-stand/prone-stand2 reuse prone-run's own frames via
# Stride in the sequence YAML, matching e1/e4's own convention, so they need
# no separate art here. die6 (electro zap) and die-crushed (corpse) stay on
# the shared generic FX assets, unchanged -- same "shared generic FX asset"
# convention rotor blur and bib decals already use elsewhere in this file.
# ---------------------------------------------------------------------------

DISR_W, DISR_H = 20, 26


def disr_pose(d, w, h, stance="stand", phase=0.0):
    cx, cy = w // 2, h // 2 + 2
    leg_swing = 0
    arm_forward = False
    spark = False
    crouch = 0
    if stance == "walk":
        leg_swing = round(3 * math.sin(phase * 2 * math.pi))
    elif stance in ("shoot", "prone-shoot"):
        arm_forward = True
        spark = phase < 0.5
    elif stance == "stand2":
        arm_forward = True
    elif stance == "prone-walk":
        leg_swing = round(2 * math.sin(phase * 2 * math.pi))

    if stance in ("prone-walk", "prone-shoot"):
        crouch = 8

    hip_y = cy + 6 - crouch
    leg_len = 8 - crouch // 2
    d.line([(cx - 2 - leg_swing, hip_y), (cx - 2 - leg_swing, hip_y + leg_len)], fill=LEGACY_GRAY_DARK, width=2)
    d.line([(cx + 2 + leg_swing, hip_y), (cx + 2 + leg_swing, hip_y + leg_len)], fill=LEGACY_GRAY_DARK, width=2)
    # Torso.
    torso_top = hip_y - 10
    d.rectangle([cx - 4, torso_top, cx + 4, hip_y], fill=LEGACY_GRAY, outline=GREEN_ACCENT)
    # Backpack discharge cell -- the "Disruptor" identity signal, replacing
    # E4's fuel tank.
    d.rectangle([cx - 3, torso_top - 2, cx + 3, torso_top + 4], fill=PANEL_BLUEBLACK, outline=SUN_GOLD)
    d.point((cx, torso_top), fill=SUN_GOLD)
    # Head.
    head_y = torso_top - 4
    d.ellipse([cx - 3, head_y - 3, cx + 3, head_y + 3], fill=LEGACY_GRAY)
    # Weapon rod, forward when aiming.
    if arm_forward:
        wx0, wy0 = cx + 4, torso_top + 3
        wx1, wy1 = cx + 10, torso_top + 1
    else:
        wx0, wy0 = cx + 3, torso_top + 4
        wx1, wy1 = cx + 6, torso_top + 8
    d.line([(wx0, wy0), (wx1, wy1)], fill=GREEN_ACCENT, width=2)
    if spark:
        d.point((wx1 + 1, wy1 - 1), fill=SUN_GOLD)
        d.point((wx1 + 2, wy1), fill=SUN_GOLD)


def _facing_major_frames(pose_fn, w, h, n_facings, n_poses):
    """Facing-major layout: n_poses consecutive frames per facing, matching
    how a sequence with both Length and Facings consumes Length x Facings
    frames (see docs/BACKLOG.md issue #35)."""
    poses = []
    for p in range(n_poses):
        base = canvas(w, h)
        pose_fn(ImageDraw.Draw(base), w, h, p / max(1, n_poses))
        poses.append(base)
    frames = []
    for facing in range(n_facings):
        angle = facing * (360.0 / n_facings)
        for base in poses:
            frames.append(base.rotate(angle, resample=Image.BICUBIC, center=(w / 2, h / 2)))
    return frames


def disr_die_frame(w, h, angle_deg, fade=1.0):
    base = canvas(w, h)
    disr_pose(ImageDraw.Draw(base), w, h, "stand")
    frame = base.rotate(angle_deg, resample=Image.BICUBIC, center=(w / 2, h / 2 + 2))
    if fade < 1.0:
        alpha = frame.split()[3].point(lambda a: int(a * fade))
        frame.putalpha(alpha)
    return frame


def disr_die_frames(n, max_angle, fade_from=None):
    out = []
    for i in range(n):
        t = i / max(1, n - 1)
        angle = max_angle * t
        fade = 1.0
        if fade_from is not None and t > fade_from:
            fade = max(0.0, 1.0 - (t - fade_from) / (1.0 - fade_from))
        out.append(disr_die_frame(DISR_W, DISR_H, angle, fade))
    return out


def disr_parachute_frame(w, h):
    f = canvas(w, h)
    dd = ImageDraw.Draw(f)
    disr_pose(dd, w, h, "stand")
    dd.arc([w // 2 - 9, 0, w // 2 + 9, 14], 200, 340, fill=SUN_GOLD, width=2)
    dd.line([(w // 2 - 8, 8), (w // 2 - 2, 14)], fill=SUN_GOLD)
    dd.line([(w // 2 + 8, 8), (w // 2 + 2, 14)], fill=SUN_GOLD)
    return f


def disr_frames():
    w, h = DISR_W, DISR_H
    frames = []

    def single(stance, phase=0.0):
        f = canvas(w, h)
        disr_pose(ImageDraw.Draw(f), w, h, stance, phase)
        return f

    # stand / stand2: 1 pose x 8 facings each.
    frames += _facing_major_frames(lambda d, w, h, ph: disr_pose(d, w, h, "stand"), w, h, 8, 1)
    frames += _facing_major_frames(lambda d, w, h, ph: disr_pose(d, w, h, "stand2"), w, h, 8, 1)
    # run: 6 walk-cycle poses x 8 facings.
    frames += _facing_major_frames(lambda d, w, h, ph: disr_pose(d, w, h, "walk", ph), w, h, 8, 6)
    # shoot: 16 poses x 8 facings.
    frames += _facing_major_frames(lambda d, w, h, ph: disr_pose(d, w, h, "shoot", ph), w, h, 8, 16)
    # prone-run: 4 poses x 8 facings (prone-stand/prone-stand2 reuse these via Stride).
    frames += _facing_major_frames(lambda d, w, h, ph: disr_pose(d, w, h, "prone-walk", ph), w, h, 8, 4)
    # prone-shoot: 16 poses x 8 facings.
    frames += _facing_major_frames(lambda d, w, h, ph: disr_pose(d, w, h, "prone-shoot", ph), w, h, 8, 16)
    # idle1/idle2: single-direction breathing loops, no facings.
    for i in range(14):
        frames.append(single("stand", i / 14))
    for i in range(16):
        frames.append(single("stand2", i / 16))
    # die1-5: a simple topple-and-fade, single direction. Lengths match the
    # sequence's own Length values; die4/die5 fall further and fade out more.
    frames += disr_die_frames(8, 70)
    frames += disr_die_frames(8, -70)
    frames += disr_die_frames(8, 90, fade_from=0.6)
    frames += disr_die_frames(12, 100, fade_from=0.5)
    frames += disr_die_frames(18, 110, fade_from=0.35)
    # parachute: single static frame.
    frames.append(disr_parachute_frame(w, h))

    return frames


def main():
    flat_buildings = [
        ("sgcry", sgcry_draw, FAM23_W, FAM23_H),
        ("sgdai", sgdai_draw, FAM23_W, FAM23_H),
        ("sgdrn", sgdrn_draw, FAM23_W, FAM23_H),
        ("sgdra", sgdra_draw, FAM23_W, FAM23_H),
        ("sgshl", sgshl_draw, SGSHL_W, SGSHL_H),
        ("sgsns", sgsns_draw, SG1x1_W, SG1x1_H),
        ("sgrel", sgrel_draw, SG1x1_W, SG1x1_H),
        ("sgwnd", sgwnd_draw, FAM23_W, FAM23_H),
        ("sghyd", sghyd_draw, FAM33_W, FAM33_H),
        ("arct", arct_draw, SG1x1_W, SG1x1_H),
    ]

    for name, draw_fn, w, h in flat_buildings:
        info = {}

        def wrapped(dd, _fn=draw_fn, _info=info):
            _info.update(_fn(dd) or {})

        sheet = two_frame_sheet(wrapped, w, h, info.get("blotches", []))
        save_pngsheet(sheet, f"{name}.png", w, h, 2)
        icon = make_icon(draw_fn, w, h)
        save_pngsheet(icon, f"{name}icon.png", 32, 24, 1)

    # Turret: 32 idle-facing frames + 32 damaged-facing frames, single strip.
    idle_frames_img = canvas(48, 44)
    sgtur_turret_draw(ImageDraw.Draw(idle_frames_img), 48, 44)
    damaged_frames_img = canvas(48, 44)
    sgtur_turret_damaged_draw(ImageDraw.Draw(damaged_frames_img), 48, 44)

    def _rot(img, n=32):
        return [img.rotate(i * (360.0 / n), resample=Image.BICUBIC, center=(24, 22)) for i in range(n)]

    idle_rot = _rot(idle_frames_img)
    damaged_rot = _rot(damaged_frames_img)
    all_frames = idle_rot + damaged_rot
    turret_sheet = canvas(48 * len(all_frames), 44)
    for i, f in enumerate(all_frames):
        turret_sheet.paste(f, (i * 48, 0), f)
    save_pngsheet(turret_sheet, "sgturturret.png", 48, 44, len(all_frames))
    save_pngsheet(make_icon(sgtur_turret_draw, 48, 44), "sgturicon.png", 32, 24, 1)

    # Drones: 32-facing body only (no damaged state, matching tran/mh60/heli).
    for name, draw_fn, fw, fh in (
        ("sgdro", sgdro_body_draw, 32, 30),
        ("sgdrs", sgdrs_body_draw, 36, 32),
    ):
        sheet = rotated_frames(draw_fn, fw, fh, n=32)
        save_pngsheet(sheet, f"{name}.png", fw, fh, 32)
        save_pngsheet(make_icon(draw_fn, fw, fh), f"{name}icon.png", 32, 24, 1)

    # Hauler Drone (SGHAU): three parallel fullness-state images, identical
    # 55-frame layout (idle 32 + harvest 8 + dock 8 + dock-loop 7), plus one
    # shared icon (fullness has no icon variant, matching harv/harvempty/
    # harvhalf's own Inherits: harv icon reuse).
    for fullness, filename in (("full", "sghau.png"), ("half", "sghauhalf.png"), ("empty", "sghauempty.png")):
        frames = sghau_frames(fullness)
        sheet = canvas(SGHAU_W * len(frames), SGHAU_H)
        for i, f in enumerate(frames):
            sheet.paste(f, (i * SGHAU_W, 0), f)
        save_pngsheet(sheet, filename, SGHAU_W, SGHAU_H, len(frames))
    save_pngsheet(
        make_icon(lambda d, w, h: sghau_draw(d, w, h, "full", "idle"), SGHAU_W, SGHAU_H),
        "sghauicon.png", 32, 24, 1,
    )

    # Disruptor Trooper (DISR): one self-contained 437-frame sheet, plus icon.
    disr_all = disr_frames()
    disr_sheet = canvas(DISR_W * len(disr_all), DISR_H)
    for i, f in enumerate(disr_all):
        disr_sheet.paste(f, (i * DISR_W, 0), f)
    save_pngsheet(disr_sheet, "disr.png", DISR_W, DISR_H, len(disr_all))
    save_pngsheet(
        make_icon(lambda d, w, h: disr_pose(d, w, h, "stand"), DISR_W, DISR_H),
        "disricon.png", 32, 24, 1,
    )

    print("done")


if __name__ == "__main__":
    main()
