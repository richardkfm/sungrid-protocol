#!/usr/bin/env python3
"""First-pass custom art for Sungrid-original buildings/units (docs/BACKLOG.md
issue #34; see docs/ART_DIRECTION.md), plus Solar Array/Advanced Solar Array
(issue #12, folded in here during the quality pass below so the whole set is
regenerable from one script -- issue #12's original generator was never
committed). Extends the "programmatic first pass now, real artist pass later"
approach issue #12 established to the rest of the roster that has no
real-world/mods/ra equivalent and previously reused an unrelated existing
building's or unit's sprite wholesale -- a real readability bug under
docs/ART_DIRECTION.md's "every actor must have a distinct silhouette" rule,
not just missing flavor (e.g. SGTUR, SGWND, and the stock SAM Site all
rendered the *same* sprite before this pass).

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

Quality-pass rendering rules (second pass over the same set; frame sizes,
counts, and layout order are byte-compatible with the first pass so no
sequence YAML changes are needed):
  - Everything is drawn 4x supersampled and LANCZOS-downscaled, so curves,
    diagonals, and rotated facings resolve cleanly instead of stair-stepping.
  - Consistent top-left key light: every major mass gets a lit top/left edge
    and a shaded bottom/right edge (box3d/dome/cylinder helpers below).
  - Units get a 1px dark readability outline (docs/ART_DIRECTION.md's
    silhouette rule) applied per-frame after downscale.
  - Damaged frames are genuinely distinct now: each building redraws itself
    with status lights off, scorch blotches, and rust streaks. (The first
    pass had a bug where the damage blotches were computed after the sheet
    was already assembled, so damaged-idle rendered identical to idle.)
  - Icons are proper sidebar cameos: the motif is cropped and fitted onto a
    shaded panel background with a border, instead of a transparent
    whole-frame downscale that left the motif tiny and muddy.

Ground rules carried over from issue #12:
  - PngSheet format (mod.yaml already lists PngSheet in SpriteFormats), not
    hand-authored indexed .shp -- no engine/dedicated pixel-art tool available
    in this environment.
  - Frame metadata is written directly as PNG tEXt chunks (FrameSize,
    FrameAmount), matching the exact keys/format already verified working in
    sgpwr.png/sgapwr.png (loaded and rendered correctly in a live headless
    skirmish per issue #12).
  - Buildings keep the *same* footprint/Dimensions and reuse the bib/minibib
    decal + dead-animation assets already wired for whichever building they
    used to borrow art from (bib decals are already shared across unrelated
    buildings throughout this ruleset's stock content, e.g. KENN borrows
    mbSILO -- this is normal, not a new corner cut).
  - This is still a first pass, not final production art: geometric shapes in
    the locked palette below, not hand-painted detail. A real artist pass is
    still open follow-up work.

Usage:
    pip install pillow
    python3 gen_concept_art.py
Writes all PNGs directly into this directory (mods/sungrid/bits/).
"""
import os
import math
from PIL import Image, ImageDraw, ImageChops, ImageFilter, ImageFont, PngImagePlugin

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
OUTLINE_DARK = (0x0C, 0x0E, 0x0C)

SS = 4  # supersample factor: draw at 4x, downscale with LANCZOS


def lit(c, f=0.35):
    return tuple(min(255, int(v + (255 - v) * f)) for v in c[:3]) + tuple(c[3:])


def dim(c, f=0.35):
    return tuple(int(v * (1 - f)) for v in c[:3]) + tuple(c[3:])


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


class SD:
    """ImageDraw wrapper that scales all coordinates/widths by SS, so the
    draw functions keep thinking in native sprite pixels. Blend mode is RGBA
    so translucent fills (glows, shadows, rotor discs) composite instead of
    overwriting."""

    def __init__(self, img):
        self.d = ImageDraw.Draw(img, "RGBA")

    @staticmethod
    def _xy(xy):
        out = []
        for p in xy:
            if isinstance(p, (tuple, list)):
                out.append((p[0] * SS, p[1] * SS))
            else:
                out.append(p * SS)
        return out

    def rect(self, xy, fill=None, outline=None, width=1):
        self.d.rectangle(self._xy(xy), fill=fill, outline=outline, width=max(1, round(width * SS)))

    def rrect(self, xy, radius, fill=None, outline=None, width=1):
        self.d.rounded_rectangle(self._xy(xy), radius=radius * SS, fill=fill, outline=outline, width=max(1, round(width * SS)))

    def ellipse(self, xy, fill=None, outline=None, width=1):
        self.d.ellipse(self._xy(xy), fill=fill, outline=outline, width=max(1, round(width * SS)))

    def line(self, xy, fill=None, width=1):
        self.d.line(self._xy(xy), fill=fill, width=max(1, round(width * SS)))

    def poly(self, xy, fill=None, outline=None):
        self.d.polygon(self._xy(xy), fill=fill, outline=outline)

    def arc(self, xy, start, end, fill=None, width=1):
        self.d.arc(self._xy(xy), start, end, fill=fill, width=max(1, round(width * SS)))

    def px(self, x, y, fill):
        """One native pixel (an SS x SS block)."""
        self.d.rectangle([x * SS, y * SS, (x + 1) * SS - 1, (y + 1) * SS - 1], fill=fill)


def render(draw_fn, w, h, *args, **kwargs):
    """Draw at SS scale, downscale to native."""
    img = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
    draw_fn(SD(img), w, h, *args, **kwargs)
    return img.resize((w, h), Image.LANCZOS)


def outline_sprite(img, color=OUTLINE_DARK):
    """1px dark readability outline behind a unit frame."""
    a = img.getchannel("A")
    solid = a.point(lambda v: 255 if v > 40 else 0)
    grown = solid.filter(ImageFilter.MaxFilter(3))
    edge = ImageChops.subtract(grown, solid)
    edge = edge.point(lambda v: min(v, 200))
    ol = Image.new("RGBA", img.size, color + (0,))
    ol.putalpha(edge)
    return Image.alpha_composite(ol, img)


# ---------------------------------------------------------------------------
# Team-color indexing (docs/BACKLOG.md issue #43).
#
# The Sungrid-original roster used to ship as truecolor PngSheets with a fixed
# sun-gold accent. Truecolor sprites don't participate in OpenRA's player-color
# remap, so those buildings/units ignored ownership entirely -- a fixed gold
# touch next to every stock building's team-colored (default red) touch. Fix:
# emit *indexed* sprites on the stock RA player palette (temperat.pal). OpenRA
# loads an indexed PNG as an Indexed8 sprite and renders it through the trait's
# palette (the default `player` palette here), so PlayerColorPalette's remap of
# indices 80-95 now applies. We map the gold "grid-live" accent onto that remap
# ramp (so it becomes the owner's colour) and everything else onto its nearest
# fixed palette entry. No rules/sequence changes are needed -- the bodies
# already render on `player`. temperat.pal is the stock RA player palette (a
# byte copy committed alongside this script for reproducibility; its 80-95
# ramp matches the canonical RA player-remap ramp).
_PAL_RAW = open(os.path.join(HERE, "temperat.pal"), "rb").read()
PLAYER_PAL = [(_PAL_RAW[i * 3] << 2, _PAL_RAW[i * 3 + 1] << 2, _PAL_RAW[i * 3 + 2] << 2)
              for i in range(256)]
REMAP_LO, REMAP_HI = 80, 95          # PlayerColorPalette remap ramp (palettes.yaml)
TRANSPARENT_IDX, SHADOW_IDX = 0, 4   # player palette: index 0 transparent, ShadowIndex 4
_BODY_IDX = [i for i in range(1, 256)
             if not (REMAP_LO <= i <= REMAP_HI) and i != SHADOW_IDX]
# Reference ramp for the gold accent (its own dim..lit shades), used to tell
# "gold accent" pixels apart from incidental warm body tones (dirt/rust) by
# nearest-reference rather than a brittle hue gate.
_GOLD_REFS = ([dim(SUN_GOLD, f) for f in (0.6, 0.4, 0.2)] + [SUN_GOLD]
              + [lit(SUN_GOLD, f) for f in (0.2, 0.4, 0.5)])


def _d2(a, b):
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2


_IDX_CACHE = {}


def _index_for(rgb):
    hit = _IDX_CACHE.get(rgb)
    if hit is not None:
        return hit
    nb = min(_BODY_IDX, key=lambda i: _d2(rgb, PLAYER_PAL[i]))
    db = _d2(rgb, PLAYER_PAL[nb])
    dg = min(_d2(rgb, g) for g in _GOLD_REFS)
    if dg < db and dg < 2500:            # closer to the gold ramp than to any body tone
        lum = 0.3 * rgb[0] + 0.59 * rgb[1] + 0.11 * rgb[2]
        idx = REMAP_LO + round((1 - lum / 255) * (REMAP_HI - REMAP_LO))
    else:
        idx = nb
    _IDX_CACHE[rgb] = idx
    return idx


def to_indexed(img):
    """RGBA sprite -> indexed 'P' image on the player palette (gold -> remap
    ramp 80-95, transparent -> 0, else nearest fixed entry). 1-bit alpha, as
    indexed sprites require."""
    img = img.convert("RGBA")
    w, h = img.size
    out = Image.new("P", (w, h), TRANSPARENT_IDX)
    flat = []
    for c in PLAYER_PAL:
        flat += list(c)
    out.putpalette(flat)
    src, dst = img.load(), out.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = src[x, y]
            dst[x, y] = TRANSPARENT_IDX if a < 128 else _index_for((r, g, b))
    return out


def save_pngsheet(img, name, frame_w, frame_h, frame_amount, indexed=False):
    meta = PngImagePlugin.PngInfo()
    meta.add_text("FrameSize", f"{frame_w},{frame_h}")
    meta.add_text("FrameAmount", str(frame_amount))
    path = os.path.join(HERE, name)
    if indexed:
        to_indexed(img).save(path, pnginfo=meta, transparency=TRANSPARENT_IDX)
    else:
        img.save(path, pnginfo=meta)
    print(f"wrote {name}  {img.size}  frame={frame_w}x{frame_h} x{frame_amount}"
          f"{'  [indexed/team-color]' if indexed else ''}")


def canvas(w, h):
    return Image.new("RGBA", (w, h), (0, 0, 0, 0))


def sheet_of(frames, frame_w, frame_h):
    sheet = canvas(frame_w * len(frames), frame_h)
    for i, f in enumerate(frames):
        sheet.paste(f, (i * frame_w, 0), f)
    return sheet


# ---------------------------------------------------------------------------
# Shading vocabulary: one top-left key light everywhere.
# ---------------------------------------------------------------------------

def box3d(sd, x0, y0, x1, y1, fill, edge=0.3):
    """Rectangular mass with lit top/left and shaded bottom/right edges."""
    sd.rect([x0, y0, x1, y1], fill=fill)
    sd.line([(x0, y0), (x1, y0)], fill=lit(fill, edge))
    sd.line([(x0, y0), (x0, y1)], fill=lit(fill, edge * 0.7))
    sd.line([(x0, y1), (x1, y1)], fill=dim(fill, edge))
    sd.line([(x1, y0), (x1, y1)], fill=dim(fill, edge * 0.7))


def dome3d(sd, x0, y0, x1, y1, fill):
    """Dome with a radial-ish ramp: dark base ellipse, mid, lit top-left cap."""
    sd.ellipse([x0, y0, x1, y1], fill=dim(fill, 0.3))
    w, h = x1 - x0, y1 - y0
    sd.ellipse([x0 + w * 0.08, y0 + h * 0.06, x1 - w * 0.16, y1 - h * 0.18], fill=fill)
    sd.ellipse([x0 + w * 0.2, y0 + h * 0.12, x1 - w * 0.42, y1 - h * 0.5], fill=lit(fill, 0.22))


def vcyl(sd, x0, y0, x1, y1, fill, bands=7):
    """Vertical cylinder: horizontal lighting ramp, brightest just left of
    center, darkest at both silhouette edges."""
    w = x1 - x0
    for i in range(bands):
        t0, t1 = i / bands, (i + 1) / bands
        center = (t0 + t1) / 2
        # Brightness peaks at ~35% across the width.
        b = 1.0 - abs(center - 0.35) * 1.7
        c = lit(fill, 0.3 * max(0.0, b)) if b > 0 else dim(fill, 0.3 * min(1.0, -b + 0.2))
        sd.rect([x0 + w * t0, y0, x0 + w * t1, y1], fill=c)


def contact_shadow(sd, cx, cy, rx, ry, alpha=70):
    sd.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=(0, 0, 0, alpha))


def scorch(sd, blotches):
    """Damage decals: soft scorch blotches with a couple of rust streaks."""
    for (x, y, r) in blotches:
        sd.ellipse([x - r, y - r * 0.8, x + r, y + r * 0.8], fill=DAMAGE_SCORCH + (215,))
        sd.ellipse([x - r * 0.5, y - r * 0.45, x + r * 0.5, y + r * 0.4], fill=(0, 0, 0, 235))
    for (x, y, r) in blotches[:2]:
        sd.rect([x + r * 0.4, y, x + r * 0.4 + 0.8, y + r + 1.5], fill=RUST + (200,))


# ---------------------------------------------------------------------------
# Shared "ground strip" grammar, matching sgpwr.png/sgapwr.png: a concrete
# base pad with grass fringing the outer corners and dirt speckle, plus a
# gold conduit band above it signaling grid connection.
# ---------------------------------------------------------------------------

def draw_ground_strip(sd, x0, x1, y0, y1, seed=0):
    sd.rect([x0, y0, x1, y1], fill=CONCRETE)
    sd.line([(x0, y0), (x1, y0)], fill=lit(CONCRETE, 0.22))
    sd.line([(x0, y1), (x1, y1)], fill=dim(CONCRETE, 0.35))
    # Expansion seams.
    for i in range(1, 4):
        gx = x0 + (x1 - x0) * i // 4
        sd.line([(gx, y0 + 1), (gx, y1 - 1)], fill=dim(CONCRETE, 0.2))
    # Deterministic dirt/wear speckle (no RNG needed for a handful of dots).
    for i in range((x1 - x0) // 4):
        px = x0 + 2 + (i * 7 + seed * 3) % max(1, (x1 - x0) - 4)
        py = y0 + 1 + (i * 5 + seed) % max(1, (y1 - y0) - 2)
        sd.px(px, py, DIRT if i % 3 else dim(CONCRETE, 0.25))
    # Grass tufts reclaiming the pad's outer corners: irregular clusters, not
    # solid bars.
    tuft = max(3, (x1 - x0) // 9)
    for k, base in ((0, x0), (1, x1 - tuft)):
        for i in range(tuft * 2):
            gx = base + (i * 3 + seed + k) % tuft
            gy = y0 + (i * 2 + seed * 2 + k) % max(1, (y1 - y0))
            sd.px(gx, gy, GRASS if i % 2 else lit(GRASS, 0.2))


def draw_gold_band(sd, x0, x1, y0, y1):
    sd.rect([x0, y0, x1, y1], fill=SUN_GOLD)
    sd.line([(x0, y0), (x1, y0)], fill=lit(SUN_GOLD, 0.4))
    sd.line([(x0, y1), (x1, y1)], fill=dim(SUN_GOLD, 0.4))
    # Segment joints along the conduit.
    for i in range(1, 6):
        jx = x0 + (x1 - x0) * i // 6
        sd.line([(jx, y0 + 1), (jx, y1 - 1)], fill=dim(SUN_GOLD, 0.3))


# ---------------------------------------------------------------------------
# Per-building motifs. Each draw_fn renders one frame into a frame_w x
# frame_h (native-pixel) canvas via the SD scaled-draw wrapper; damaged=True
# redraws the same building with status lights off + scorch/rust decals.
# ---------------------------------------------------------------------------

FAM23_W, FAM23_H = 66, 54   # 2x3 footprint family (matches sgpwr.png)
FAM33_W, FAM33_H = 90, 60   # 3x3 footprint family (matches sgapwr.png)
SGSHL_W, SGSHL_H = 72, 50   # 2x2 footprint
SG1x1_W, SG1x1_H = 40, 36   # 1x1 footprint


def _solar_panel(sd, x0, y0, x1, y1, damaged_crack=False):
    """One tilted-read solar collector: dark cell field with a sky-gleam ramp,
    thin lit frame, cell grid."""
    sd.rect([x0, y0, x1, y1], fill=PANEL_BLUEBLACK)
    # Sky reflection: brighter toward the top of the panel.
    sd.rect([x0, y0, x1, y0 + (y1 - y0) * 0.3], fill=lit(PANEL_BLUEBLACK, 0.35))
    sd.rect([x0, y0 + (y1 - y0) * 0.3, x1, y0 + (y1 - y0) * 0.6], fill=lit(PANEL_BLUEBLACK, 0.15))
    # Cell grid.
    cols = max(2, round((x1 - x0) / 6))
    rows = max(2, round((y1 - y0) / 7))
    for c in range(1, cols):
        gx = x0 + (x1 - x0) * c / cols
        sd.line([(gx, y0), (gx, y1)], fill=dim(PANEL_BLUEBLACK, 0.5))
    for r in range(1, rows):
        gy = y0 + (y1 - y0) * r / rows
        sd.line([(x0, gy), (x1, gy)], fill=dim(PANEL_BLUEBLACK, 0.5))
    # Diagonal gleam.
    sd.line([(x0 + 2, y1 - 2), (x1 - 2, y0 + 2)], fill=lit(PANEL_BLUEBLACK, 0.6), width=0.5)
    # Lit aluminum frame.
    sd.rect([x0, y0, x1, y1], outline=lit(LEGACY_GRAY, 0.35), width=0.5)
    if damaged_crack:
        sd.line([(x0 + (x1 - x0) * 0.3, y0), ((x0 + x1) / 2, (y0 + y1) / 2), (x0 + (x1 - x0) * 0.4, y1)],
                fill=lit(PANEL_BLUEBLACK, 0.8), width=0.5)


def sgpwr_draw(sd, w=FAM23_W, h=FAM23_H, damaged=False):
    """Solar Array: two collector panels over the shared conduit band --
    issue #12's motif, redrawn with the quality-pass shading."""
    ground_y0, ground_y1 = h - 12, h
    gold_y0, gold_y1 = ground_y0 - 8, ground_y0
    draw_ground_strip(sd, 2, w - 2, ground_y0, ground_y1, seed=11)
    draw_gold_band(sd, 6, w - 6, gold_y0, gold_y1)
    panel_y0, panel_y1 = 8, gold_y0 - 8
    for i, (px0, px1) in enumerate(((7, 31), (35, 59))):
        contact_shadow(sd, (px0 + px1) / 2, gold_y0 - 1.5, (px1 - px0) / 2, 2)
        # Support poles.
        for px in (px0 + 4, px1 - 4):
            sd.line([(px, panel_y1), (px, gold_y0)], fill=POLE_DARK, width=1)
            sd.line([(px - 0.5, panel_y1), (px - 0.5, gold_y0)], fill=lit(POLE_DARK, 0.3), width=0.3)
        _solar_panel(sd, px0, panel_y0, px1, panel_y1, damaged_crack=(damaged and i == 0))
    # Status light on the conduit.
    if not damaged:
        sd.px(w // 2, gold_y0 + 2, lit(GREEN_ACCENT, 0.3))
    if damaged:
        scorch(sd, [(20, panel_y1 - 4, 3.5), (w - 18, gold_y0 + 3, 2.5)])


def sgapwr_draw(sd, w=FAM33_W, h=FAM33_H, damaged=False):
    """Advanced Solar Array: three collectors + a storage cell, on the 3x3
    footprint."""
    ground_y0, ground_y1 = h - 13, h
    gold_y0, gold_y1 = ground_y0 - 9, ground_y0
    draw_ground_strip(sd, 2, w - 2, ground_y0, ground_y1, seed=12)
    draw_gold_band(sd, 5, w - 5, gold_y0, gold_y1)
    panel_y0, panel_y1 = 7, gold_y0 - 9
    for i, (px0, px1) in enumerate(((6, 30), (33, 57), (60, 84))):
        contact_shadow(sd, (px0 + px1) / 2, gold_y0 - 1.5, (px1 - px0) / 2, 2)
        for px in (px0 + 4, px1 - 4):
            sd.line([(px, panel_y1), (px, gold_y0)], fill=POLE_DARK, width=1)
            sd.line([(px - 0.5, panel_y1), (px - 0.5, gold_y0)], fill=lit(POLE_DARK, 0.3), width=0.3)
        _solar_panel(sd, px0, panel_y0, px1, panel_y1, damaged_crack=(damaged and i == 1))
    # Ground-level storage cell between the middle poles.
    box3d(sd, 38, gold_y0 - 7, 52, gold_y0 - 1, PANEL_BLUEBLACK)
    for i in range(3):
        sd.px(40 + i * 4, gold_y0 - 4, (SUN_GOLD if not damaged else dim(SUN_GOLD, 0.6)))
    if damaged:
        scorch(sd, [(45, gold_y0 - 4, 3), (70, panel_y1 - 3, 3), (16, gold_y0 + 3, 2)])


def sgcry_draw(sd, w=FAM23_W, h=FAM23_H, damaged=False):
    """Cryptominer: worn, scavenged server-rack blocks -- deliberately the
    untidy legacy-tech foil to sgdai's neat grid."""
    ground_y0, ground_y1 = h - 12, h
    gold_y0, gold_y1 = ground_y0 - 8, ground_y0
    draw_ground_strip(sd, 2, w - 2, ground_y0, ground_y1, seed=1)
    draw_gold_band(sd, 6, w - 6, gold_y0, gold_y1)
    cols, rows = 3, 2
    block_w, block_h = 14, 12
    gap = 3
    total_w = cols * block_w + (cols - 1) * gap
    x0 = (w - total_w) // 2
    contact_shadow(sd, w / 2, gold_y0 - 0.5, total_w / 2 + 2, 2.5)
    for r in range(rows):
        for c in range(cols):
            bx = x0 + c * (block_w + gap)
            by = gold_y0 - (r + 1) * (block_h + 2)
            # Slightly mismatched rack heights: scavenged, not uniform.
            jitter = (c * 2 + r) % 3 - 1
            box3d(sd, bx, by + jitter, bx + block_w, by + block_h, LEGACY_GRAY)
            # Vent slits.
            for vy in range(3):
                sd.line([(bx + 2, by + jitter + 3 + vy * 3), (bx + block_w - 2, by + jitter + 3 + vy * 3)],
                        fill=dim(LEGACY_GRAY, 0.35), width=0.5)
            # Status light: amber, off when damaged.
            sd.px(bx + 2, by + jitter + 1, SUN_GOLD if not damaged and (c + r) % 3 != 2 else dim(LEGACY_GRAY, 0.3))
            # Rust streaks on the outer racks.
            if c in (0, cols - 1):
                sd.rect([bx + block_w - 3, by + block_h - 4, bx + block_w - 2, by + block_h], fill=RUST)
    # Tangle of power cabling down to the conduit.
    sd.line([(x0 + 8, gold_y0 - 2), (x0 + 12, gold_y0 + 2)], fill=POLE_DARK, width=0.7)
    sd.line([(x0 + total_w - 8, gold_y0 - 2), (x0 + total_w - 14, gold_y0 + 2)], fill=POLE_DARK, width=0.7)
    if damaged:
        scorch(sd, [(x0 + total_w // 2, gold_y0 - 6, 3.5), (x0 + 4, gold_y0 + 2, 2)])


def sgdai_draw(sd, w=FAM23_W, h=FAM23_H, damaged=False):
    """Datacenter for AI: dense, perfectly aligned blue-black server grid with
    gold trim and a green data line -- the tidy foil to sgcry."""
    ground_y0, ground_y1 = h - 12, h
    gold_y0, gold_y1 = ground_y0 - 8, ground_y0
    draw_ground_strip(sd, 2, w - 2, ground_y0, ground_y1, seed=2)
    draw_gold_band(sd, 6, w - 6, gold_y0, gold_y1)
    cols, rows = 4, 3
    block_w, block_h = 10, 8
    gap = 1
    total_w = cols * block_w + (cols - 1) * gap
    x0 = (w - total_w) // 2
    top = gold_y0 - rows * (block_h + gap)
    contact_shadow(sd, w / 2, gold_y0 - 0.5, total_w / 2 + 2, 2.5)
    for r in range(rows):
        for c in range(cols):
            bx = x0 + c * (block_w + gap)
            by = top + r * (block_h + gap)
            box3d(sd, bx, by, bx + block_w, by + block_h, PANEL_BLUEBLACK, edge=0.45)
            sd.rect([bx, by, bx + block_w, by + block_h], outline=dim(SUN_GOLD, 0.25), width=0.4)
            # Tiny green activity LEDs, dark when damaged.
            if not damaged:
                sd.px(bx + 2, by + block_h - 2, GREEN_ACCENT if (r * cols + c) % 3 else dim(GREEN_ACCENT, 0.4))
    # Data line linking the rack tops -- the "AI" identity signal, with a
    # soft glow. Flickers out when damaged.
    if not damaged:
        sd.line([(x0, top - 2), (x0 + total_w, top - 2)], fill=GREEN_ACCENT + (90,), width=1.6)
        sd.line([(x0, top - 2), (x0 + total_w, top - 2)], fill=lit(GREEN_ACCENT, 0.3), width=0.6)
        for i in range(4):
            sd.px(x0 + 3 + i * (total_w // 4), top - 2, lit(GREEN_ACCENT, 0.6))
    else:
        sd.line([(x0, top - 2), (x0 + total_w * 0.4, top - 2)], fill=dim(GREEN_ACCENT, 0.5), width=0.6)
        scorch(sd, [(x0 + total_w // 2, top + 6, 3), (x0 + total_w - 6, gold_y0 - 3, 2.5)])


def sgdrn_draw(sd, w=FAM23_W, h=FAM23_H, damaged=False):
    """Drone Bay: improvised, asymmetric open scaffold/gantry with a parked
    drone -- Assembly's field-workshop answer to sgdra's hardened hangar."""
    ground_y0, ground_y1 = h - 12, h
    gold_y0, gold_y1 = ground_y0 - 8, ground_y0
    draw_ground_strip(sd, 2, w - 2, ground_y0, ground_y1, seed=3)
    draw_gold_band(sd, 6, w - 6, gold_y0, gold_y1)
    # Truss legs with X-bracing; deliberately unequal heights.
    def truss(bx0, apex_x, apex_y, bx1):
        sd.line([(bx0, gold_y0), (apex_x, apex_y)], fill=GREEN_PRIMARY, width=1.4)
        sd.line([(bx1, gold_y0), (apex_x, apex_y)], fill=GREEN_PRIMARY, width=1.4)
        sd.line([(bx0, gold_y0), (apex_x, apex_y)], fill=lit(GREEN_PRIMARY, 0.3), width=0.4)
        mid_y = (gold_y0 + apex_y) / 2
        sd.line([((bx0 + apex_x) / 2, mid_y), ((bx1 + apex_x) / 2, mid_y)], fill=dim(GREEN_PRIMARY, 0.2), width=0.5)
    truss(9, 17, gold_y0 - 22, 25)
    truss(w - 25, w - 19, gold_y0 - 18, w - 11)
    # Sagging cross-cable between the two masts, with a work lamp.
    sd.line([(17, gold_y0 - 21), (w / 2, gold_y0 - 17), (w - 19, gold_y0 - 17)], fill=dim(LEGACY_GRAY, 0.1), width=0.5)
    sd.px(w // 2, gold_y0 - 16, SUN_GOLD if not damaged else dim(LEGACY_GRAY, 0.3))
    # Raised landing pad with the parked drone.
    pad_x0, pad_x1 = w // 2 - 11, w // 2 + 11
    contact_shadow(sd, w / 2, gold_y0 - 0.5, 13, 2.5)
    box3d(sd, pad_x0, gold_y0 - 6, pad_x1, gold_y0, LEGACY_GRAY)
    sd.rect([pad_x0 + 2, gold_y0 - 5, pad_x1 - 2, gold_y0 - 4.4], fill=dim(SUN_GOLD, 0.25))
    cx, cy = w // 2, gold_y0 - 10
    contact_shadow(sd, cx, gold_y0 - 6.5, 6, 1.2, alpha=90)
    sd.poly([(cx, cy - 5), (cx + 5, cy), (cx, cy + 5), (cx - 5, cy)], fill=GREEN_PRIMARY, outline=GREEN_ACCENT)
    sd.poly([(cx, cy - 3.4), (cx + 2.6, cy - 0.6), (cx, cy - 0.6), (cx - 2.6, cy - 0.6)], fill=lit(GREEN_PRIMARY, 0.3))
    for ddx, ddy in ((-5.5, -3.5), (5.5, -3.5), (-5.5, 3.5), (5.5, 3.5)):
        sd.ellipse([cx + ddx - 1.6, cy + ddy - 1.6, cx + ddx + 1.6, cy + ddy + 1.6], fill=(0xB0, 0xB0, 0xA8, 110))
    if damaged:
        scorch(sd, [(cx, cy, 2.5), (18, gold_y0 - 4, 2.5)])


def sgdra_draw(sd, w=FAM23_W, h=FAM23_H, damaged=False):
    """Aerial Fabrication Bay: enclosed, symmetric hangar -- the hardened
    Consortium mirror of sgdrn's open scaffold."""
    ground_y0, ground_y1 = h - 12, h
    gold_y0, gold_y1 = ground_y0 - 8, ground_y0
    draw_ground_strip(sd, 2, w - 2, ground_y0, ground_y1, seed=4)
    draw_gold_band(sd, 6, w - 6, gold_y0, gold_y1)
    hx0, hx1 = 8, w - 8
    hy0, hy1 = gold_y0 - 26, gold_y0
    contact_shadow(sd, w / 2, gold_y0 - 0.5, (hx1 - hx0) / 2 + 2, 2.5)
    # Main hall with a lit, slightly vaulted roof strip.
    box3d(sd, hx0, hy0 + 3, hx1, hy1, PANEL_BLUEBLACK, edge=0.4)
    sd.rrect([hx0 + 1, hy0, hx1 - 1, hy0 + 5], 2, fill=lit(PANEL_BLUEBLACK, 0.3))
    sd.line([(hx0 + 1, hy0 + 5), (hx1 - 1, hy0 + 5)], fill=dim(PANEL_BLUEBLACK, 0.4), width=0.5)
    # Big front door: vertical slats, gold header rail.
    dx0, dx1 = w // 2 - 12, w // 2 + 12
    sd.rect([dx0, hy0 + 8, dx1, hy1 - 1], fill=dim(PANEL_BLUEBLACK, 0.25))
    for i in range(6):
        slat = dx0 + i * 4
        sd.line([(slat, hy0 + 8), (slat, hy1 - 1)], fill=dim(PANEL_BLUEBLACK, 0.5), width=0.5)
    sd.rect([dx0 - 1, hy0 + 6, dx1 + 1, hy0 + 8], fill=SUN_GOLD)
    sd.line([(dx0 - 1, hy0 + 8), (dx1 + 1, hy0 + 8)], fill=dim(SUN_GOLD, 0.4), width=0.4)
    # Corner service pylons + roof beacon.
    for px in (hx0 + 3, hx1 - 3):
        sd.line([(px, hy0 + 4), (px, hy1)], fill=dim(SUN_GOLD, 0.15), width=0.8)
    sd.px(w // 2, hy0 + 1, GREEN_ACCENT if not damaged else dim(LEGACY_GRAY, 0.3))
    if damaged:
        scorch(sd, [(w // 2, (hy0 + hy1) / 2 + 2, 3.5), (hx1 - 6, hy0 + 6, 2.5)])


def sgshl_draw(sd, w=SGSHL_W, h=SGSHL_H, damaged=False):
    """Resilience Shelter: hardened dome with a sandbag row along the front
    edge, per ART_DIRECTION.md's "not utopian" guardrail."""
    ground_y0, ground_y1 = h - 10, h
    draw_ground_strip(sd, 2, w - 2, ground_y0, ground_y1, seed=5)
    dome_y0 = 8
    contact_shadow(sd, w / 2, ground_y0 + 2, w / 2 - 6, 3)
    dome3d(sd, 6, dome_y0, w - 6, ground_y0 + 6, GREEN_PRIMARY)
    # Panel seams following the dome curve.
    sd.arc([6, dome_y0, w - 6, ground_y0 + 6], 210, 330, fill=dim(GREEN_PRIMARY, 0.25), width=0.6)
    sd.arc([12, dome_y0 + 4, w - 12, ground_y0 + 2], 200, 340, fill=dim(GREEN_PRIMARY, 0.2), width=0.5)
    # Entry airlock front and center.
    door_w = 7
    sd.rrect([w / 2 - door_w / 2, ground_y0 - 9, w / 2 + door_w / 2, ground_y0 + 1], 2, fill=dim(PANEL_BLUEBLACK, 0.1))
    sd.line([(w / 2 - door_w / 2 + 1, ground_y0 - 8), (w / 2 + door_w / 2 - 1, ground_y0 - 8)], fill=lit(PANEL_BLUEBLACK, 0.5), width=0.5)
    # Gold beacon cap.
    sd.ellipse([w / 2 - 3, dome_y0 + 1, w / 2 + 3, dome_y0 + 6], fill=SUN_GOLD if not damaged else dim(SUN_GOLD, 0.55))
    sd.ellipse([w / 2 - 1.8, dome_y0 + 1.8, w / 2 + 0.6, dome_y0 + 3.6], fill=lit(SUN_GOLD, 0.45) if not damaged else dim(SUN_GOLD, 0.4))
    # Sandbag row: two-tone bags with lit tops.
    bag_w = 6
    for i, bx in enumerate(range(4, w - 4 - bag_w, bag_w + 1)):
        by = ground_y0 - 3 + (i % 2)
        sd.ellipse([bx, by, bx + bag_w, by + 5], fill=DIRT)
        sd.arc([bx, by, bx + bag_w, by + 5], 180, 320, fill=lit(DIRT, 0.3), width=0.7)
        sd.arc([bx, by, bx + bag_w, by + 5], 20, 160, fill=dim(DIRT, 0.35), width=0.6)
    if damaged:
        scorch(sd, [(w / 2 + 8, dome_y0 + 14, 4), (w / 2 - 14, ground_y0 - 4, 2.5)])


def sgsns_draw(sd, w=SG1x1_W, h=SG1x1_H, damaged=False):
    """Sensor Array: tripod-mounted dish with a concentric-ring motif."""
    ground_y0, ground_y1 = h - 8, h
    draw_ground_strip(sd, 2, w - 2, ground_y0, ground_y1, seed=6)
    cx = w // 2
    mast_top = 10
    contact_shadow(sd, cx, ground_y0 + 1, 9, 2)
    # Tripod with lit near-edges and a cross-brace.
    for off, wd in ((-6, 1), (6, 1), (0, 1.2)):
        sd.line([(cx + off, ground_y0), (cx, mast_top)], fill=LEGACY_GRAY_DARK, width=wd)
    sd.line([(cx - 6, ground_y0), (cx, mast_top)], fill=lit(LEGACY_GRAY_DARK, 0.35), width=0.4)
    sd.line([(cx - 3.2, ground_y0 - 5), (cx + 3.2, ground_y0 - 5)], fill=dim(LEGACY_GRAY, 0.1), width=0.5)
    # Dish: shaded bowl + concentric scan rings + gold feed point.
    sd.ellipse([cx - 10, mast_top - 8, cx + 10, mast_top + 6], fill=dim(PANEL_BLUEBLACK, 0.15))
    sd.ellipse([cx - 8.4, mast_top - 6.8, cx + 8.4, mast_top + 4.2], fill=PANEL_BLUEBLACK)
    sd.ellipse([cx - 7, mast_top - 6, cx + 3, mast_top + 1], fill=lit(PANEL_BLUEBLACK, 0.22))
    sd.ellipse([cx - 10, mast_top - 8, cx + 10, mast_top + 6], outline=dim(SUN_GOLD, 0.2), width=0.5)
    ring = GREEN_ACCENT if not damaged else dim(GREEN_ACCENT, 0.45)
    sd.arc([cx - 7, mast_top - 5, cx + 7, mast_top + 3], 195, 345, fill=ring, width=0.7)
    sd.arc([cx - 4, mast_top - 3, cx + 4, mast_top + 1], 195, 345, fill=ring, width=0.6)
    sd.line([(cx, mast_top - 1), (cx + 4, mast_top - 6)], fill=lit(LEGACY_GRAY, 0.2), width=0.5)
    sd.ellipse([cx + 3, mast_top - 7, cx + 5.4, mast_top - 4.6], fill=SUN_GOLD if not damaged else dim(SUN_GOLD, 0.5))
    if damaged:
        scorch(sd, [(cx + 2, mast_top + 2, 2.5), (cx - 4, ground_y0 - 2, 2)])


def sgrel_draw(sd, w=SG1x1_W, h=SG1x1_H, damaged=False):
    """Smart Grid Relay: gold-lit relay pylon with radiating power lines."""
    ground_y0, ground_y1 = h - 8, h
    draw_ground_strip(sd, 2, w - 2, ground_y0, ground_y1, seed=7)
    cx = w // 2
    pylon_top = 6
    contact_shadow(sd, cx, ground_y0 + 1, 8, 2)
    # Tapered lattice pylon with a lit left edge and crossarms.
    sd.poly([(cx - 6, ground_y0), (cx + 6, ground_y0), (cx + 2, pylon_top), (cx - 2, pylon_top)],
            fill=PANEL_BLUEBLACK, outline=dim(LEGACY_GRAY, 0.1))
    sd.line([(cx - 5.6, ground_y0), (cx - 1.8, pylon_top)], fill=lit(PANEL_BLUEBLACK, 0.5), width=0.5)
    for t in (0.35, 0.65):
        yy = pylon_top + (ground_y0 - pylon_top) * t
        half = 2 + 4 * t
        sd.line([(cx - half, yy), (cx + half, yy)], fill=dim(LEGACY_GRAY, 0.15), width=0.6)
        # Insulator studs at the crossarm tips.
        sd.px(round(cx - half), round(yy) - 1, dim(SUN_GOLD, 0.25))
        sd.px(round(cx + half) - 1, round(yy) - 1, dim(SUN_GOLD, 0.25))
    node_y = pylon_top - 2
    # Radiating distribution lines with node dots, then the energized head.
    live = not damaged
    for ang in (200, 245, 295, 340):
        rad = math.radians(ang)
        ex, ey = cx + 14 * math.cos(rad), node_y + 12 * math.sin(rad)
        sd.line([(cx, node_y), (ex, ey)], fill=(SUN_GOLD if live else dim(SUN_GOLD, 0.5)), width=0.6)
        sd.ellipse([ex - 1, ey - 1, ex + 1, ey + 1], fill=lit(SUN_GOLD, 0.3) if live else dim(SUN_GOLD, 0.4))
    if live:
        sd.ellipse([cx - 6, node_y - 6, cx + 6, node_y + 6], fill=SUN_GOLD + (60,))
    sd.ellipse([cx - 4, node_y - 4, cx + 4, node_y + 4], fill=SUN_GOLD if live else dim(SUN_GOLD, 0.45))
    sd.ellipse([cx - 2.6, node_y - 2.6, cx + 0.2, node_y + 0.2], fill=lit(SUN_GOLD, 0.5) if live else dim(SUN_GOLD, 0.3))
    if damaged:
        scorch(sd, [(cx, node_y + 8, 2.5), (cx + 4, ground_y0 - 2, 2)])


def arct_draw(sd, w=SG1x1_W, h=SG1x1_H, damaged=False):
    """Arc Turret: a squat discharge base with a forked electrode, deliberately
    NOT a nozzle/fuel-tank silhouette so it reads as "electric discharge"
    rather than "flamethrower" -- see docs/BACKLOG.md issue #36 (reverses the
    FTUR chassis reuse issue #14 left in place)."""
    ground_y0, ground_y1 = h - 8, h
    draw_ground_strip(sd, 2, w - 2, ground_y0, ground_y1, seed=10)
    cx = w // 2
    base_top = ground_y0 - 10
    contact_shadow(sd, cx, ground_y0 + 1, 10, 2)
    # Capacitor housing: shaded, vented, green-trimmed.
    sd.rrect([cx - 9, base_top, cx + 9, ground_y0], 4, fill=PANEL_BLUEBLACK)
    sd.arc([cx - 9, base_top, cx + 9, base_top + 8], 180, 360, fill=lit(PANEL_BLUEBLACK, 0.45), width=0.7)
    sd.rrect([cx - 9, base_top, cx + 9, ground_y0], 4, outline=GREEN_ACCENT if not damaged else dim(GREEN_ACCENT, 0.4), width=0.5)
    for vx in (-5, 0, 5):
        sd.line([(cx + vx, base_top + 4), (cx + vx, ground_y0 - 3)], fill=dim(PANEL_BLUEBLACK, 0.6), width=0.7)
    # Charge indicator pips.
    for i in range(3):
        on = not damaged or i == 0
        sd.px(cx - 4 + i * 4, ground_y0 - 3, SUN_GOLD if on else dim(LEGACY_GRAY, 0.3))
    # Electrode mast with insulator rings.
    rod_top = base_top - 12
    sd.line([(cx, base_top), (cx, rod_top)], fill=LEGACY_GRAY_DARK, width=1.6)
    sd.line([(cx - 0.6, base_top), (cx - 0.6, rod_top)], fill=lit(LEGACY_GRAY_DARK, 0.4), width=0.4)
    for ry in (base_top - 4, base_top - 8):
        sd.line([(cx - 1.8, ry), (cx + 1.8, ry)], fill=lit(LEGACY_GRAY, 0.3), width=0.8)
    # Forked electrode: two gold prongs with ball tips -- a discharge gap,
    # not a flame nozzle.
    for sx in (-1, 1):
        sd.line([(cx, rod_top), (cx + sx * 5, rod_top - 6)], fill=SUN_GOLD, width=1.4)
        sd.ellipse([cx + sx * 5 - 1.4, rod_top - 7.4, cx + sx * 5 + 1.4, rod_top - 4.6], fill=lit(SUN_GOLD, 0.3))
    # The living arc bridging the prongs: jagged bolt + soft glow.
    if not damaged:
        sd.ellipse([cx - 6, rod_top - 9, cx + 6, rod_top - 2], fill=GREEN_ACCENT + (55,))
        sd.line([(cx - 4.6, rod_top - 6), (cx - 1.5, rod_top - 4), (cx + 1.5, rod_top - 7), (cx + 4.6, rod_top - 6)],
                fill=lit(GREEN_ACCENT, 0.35), width=0.7)
    if damaged:
        scorch(sd, [(cx + 3, base_top + 4, 3), (cx - 5, ground_y0 - 2, 2)])


def sgwnd_draw(sd, w=FAM23_W, h=FAM23_H, damaged=False):
    """Wind Turbine Array: two slim turbine poles/rotors -- deliberately
    sparser than Solar Array's dense panel frames, matching Wind Turbine's
    "cheap, mass-producible" fantasy."""
    ground_y0, ground_y1 = h - 12, h
    gold_y0, gold_y1 = ground_y0 - 8, ground_y0
    draw_ground_strip(sd, 2, w - 2, ground_y0, ground_y1, seed=8)
    draw_gold_band(sd, 6, w - 6, gold_y0, gold_y1)
    for k, cx in enumerate((w // 3, 2 * w // 3)):
        hub_y = gold_y0 - 26
        contact_shadow(sd, cx, gold_y0 - 1, 4, 1.5)
        # Tapered tower with a lit edge.
        sd.poly([(cx - 1.8, gold_y0), (cx + 1.8, gold_y0), (cx + 0.8, hub_y), (cx - 0.8, hub_y)], fill=LEGACY_GRAY_DARK)
        sd.line([(cx - 1.4, gold_y0), (cx - 0.6, hub_y)], fill=lit(LEGACY_GRAY_DARK, 0.45), width=0.4)
        # Nacelle + hub.
        sd.rrect([cx - 2.4, hub_y - 2, cx + 2.4, hub_y + 2], 1, fill=LEGACY_GRAY)
        sd.ellipse([cx - 1.6, hub_y - 1.6, cx + 1.6, hub_y + 1.6], fill=SUN_GOLD if not damaged or k == 1 else dim(SUN_GOLD, 0.5))
        # Three blades, phase-offset per turbine so the pair doesn't read as
        # a copy-paste; lit leading edge, dark root.
        phase = 15 + k * 40
        stopped = damaged and k == 0
        for b in range(3):
            ang = phase + b * 120
            rad = math.radians(ang)
            ex, ey = cx + 13 * math.cos(rad), hub_y - 13 * math.sin(rad)
            mx, my = cx + 4 * math.cos(rad), hub_y - 4 * math.sin(rad)
            blade = dim(GREEN_ACCENT, 0.45) if stopped else GREEN_ACCENT
            sd.line([(mx, my), (ex, ey)], fill=blade, width=1.6)
            sd.line([(mx, my), (ex, ey)], fill=lit(blade, 0.3), width=0.5)
            sd.line([(cx, hub_y), (mx, my)], fill=dim(blade, 0.3), width=1.2)
    if damaged:
        scorch(sd, [(w // 3, gold_y0 - 10, 2.5), (2 * w // 3 + 4, gold_y0 + 2, 2)])


def sghyd_draw(sd, w=FAM33_W, h=FAM33_H, damaged=False):
    """Hydrogen Plant: two large hardened storage cylinders -- a bigger,
    heavier industrial-cluster read matching its expensive/late-game/
    Heavy-armor identity."""
    ground_y0, ground_y1 = h - 13, h
    gold_y0, gold_y1 = ground_y0 - 9, ground_y0
    draw_ground_strip(sd, 2, w - 2, ground_y0, ground_y1, seed=9)
    draw_gold_band(sd, 5, w - 5, gold_y0, gold_y1)
    tank_w, tank_h = 26, 30
    tank_top = gold_y0 - tank_h
    for k, cx in enumerate((w // 2 - 20, w // 2 + 20)):
        tx0, tx1 = cx - tank_w // 2, cx + tank_w // 2
        contact_shadow(sd, cx, gold_y0 - 1, tank_w / 2 + 1, 2.5)
        # Cylinder body with a proper horizontal lighting ramp + domed cap.
        vcyl(sd, tx0, tank_top + 4, tx1, gold_y0, PANEL_BLUEBLACK)
        sd.ellipse([tx0, tank_top, tx1, tank_top + 9], fill=PANEL_BLUEBLACK)
        sd.ellipse([tx0 + 3, tank_top + 1, tx1 - 9, tank_top + 5.5], fill=lit(PANEL_BLUEBLACK, 0.3))
        # Gold hoop bands (following the cylinder shading).
        for by in (tank_top + 10, tank_top + 20):
            sd.line([(tx0 + 0.6, by), (tx1 - 0.6, by)], fill=SUN_GOLD, width=1.2)
            sd.line([(tx0 + 0.6, by + 0.8), (tx1 - 0.6, by + 0.8)], fill=dim(SUN_GOLD, 0.4), width=0.4)
        # Vent stack on the far tank / gauge box on the near one.
        if k == 0:
            box3d(sd, tx1 - 6, gold_y0 - 8, tx1 - 1, gold_y0 - 2, LEGACY_GRAY)
            sd.px(tx1 - 4, gold_y0 - 6, GREEN_ACCENT if not damaged else dim(GREEN_ACCENT, 0.4))
        else:
            sd.line([(tx0 + 4, tank_top + 2), (tx0 + 4, tank_top - 4)], fill=LEGACY_GRAY, width=1)
            sd.px(tx0 + 4, tank_top - 5, lit(LEGACY_GRAY, 0.3))
    # Transfer pipe with a valve wheel between the tanks.
    pipe_y = tank_top + 14
    sd.line([(w // 2 - 20 + tank_w // 2, pipe_y), (w // 2 + 20 - tank_w // 2, pipe_y)], fill=SUN_GOLD, width=1.6)
    sd.line([(w // 2 - 20 + tank_w // 2, pipe_y - 0.8), (w // 2 + 20 - tank_w // 2, pipe_y - 0.8)], fill=lit(SUN_GOLD, 0.4), width=0.4)
    sd.ellipse([w / 2 - 2.4, pipe_y - 2.4, w / 2 + 2.4, pipe_y + 2.4], fill=dim(SUN_GOLD, 0.2))
    sd.ellipse([w / 2 - 1.2, pipe_y - 1.2, w / 2 + 1.2, pipe_y + 1.2], fill=lit(SUN_GOLD, 0.3))
    if damaged:
        scorch(sd, [(w / 2, pipe_y + 4, 3.5), (w / 2 - 24, tank_top + 8, 3), (w / 2 + 16, gold_y0 - 4, 2.5)])


# ---------------------------------------------------------------------------
# Rotating sprites: turret (32 facings x2 for damaged) and the two drone
# bodies (32 facings, no damaged variant -- matching tran/mh60/heli, which
# don't define one either). All rotation happens at SS resolution before the
# downscale, so facings stay crisp.
# ---------------------------------------------------------------------------

def rotated_frames(draw_fn, frame_w, frame_h, n=32, outlined=True, **kwargs):
    """draw_fn renders one north-facing (up) frame; classic facing convention
    is frame 0 = up, winding counter-clockwise in equal steps (matching the
    first pass, which shipped and was verified in-game)."""
    base = Image.new("RGBA", (frame_w * SS, frame_h * SS), (0, 0, 0, 0))
    draw_fn(SD(base), frame_w, frame_h, **kwargs)
    frames = []
    for i in range(n):
        angle = i * (360.0 / n)
        f = base.rotate(angle, resample=Image.BICUBIC, center=(frame_w * SS / 2, frame_h * SS / 2))
        f = f.resize((frame_w, frame_h), Image.LANCZOS)
        if outlined:
            f = outline_sprite(f)
        frames.append(f)
    return frames


def sgtur_turret_draw(sd, w, h, damaged=False):
    cx, cy = w // 2, h // 2 + 6
    barrel = GREEN_PRIMARY if not damaged else LEGACY_GRAY
    ring = SUN_GOLD if not damaged else RUST
    # Barrel: two-tone with a lit center stripe and a muzzle collar.
    sd.rect([cx - 3, cy - h // 2 + 4, cx + 3, cy], fill=barrel)
    sd.line([(cx - 2.4, cy - h // 2 + 4), (cx - 2.4, cy)], fill=dim(barrel, 0.3), width=0.6)
    sd.line([(cx - 0.6, cy - h // 2 + 4), (cx - 0.6, cy)], fill=lit(barrel, 0.35), width=1)
    sd.line([(cx + 2.4, cy - h // 2 + 4), (cx + 2.4, cy)], fill=dim(barrel, 0.35), width=0.6)
    sd.rect([cx - 3.4, cy - h // 2 + 4, cx + 3.4, cy - h // 2 + 6.5], fill=ring)
    # Housing: shaded disc with a gold trim ring and center emitter dome.
    sd.ellipse([cx - 8, cy - 6, cx + 8, cy + 6], fill=dim(PANEL_BLUEBLACK, 0.2))
    sd.ellipse([cx - 7, cy - 5.4, cx + 7, cy + 5], fill=PANEL_BLUEBLACK)
    sd.arc([cx - 7, cy - 5.4, cx + 7, cy + 5], 150, 300, fill=lit(PANEL_BLUEBLACK, 0.4), width=0.8)
    sd.ellipse([cx - 8, cy - 6, cx + 8, cy + 6], outline=dim(ring, 0.25), width=0.5)
    sd.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=ring)
    sd.ellipse([cx - 2, cy - 2, cx + 0.4, cy + 0.4], fill=lit(ring, 0.4))
    if damaged:
        sd.ellipse([cx - 6, cy - 9, cx - 2.4, cy - 6], fill=DAMAGE_SCORCH + (220,))
        sd.px(cx + 4, cy + 2, RUST)


def sgtur_base_draw(sd, w, h, damaged=False):
    """Non-rotating reference frame, used only to derive the icon."""
    cx, cy = w // 2, h // 2 + 4
    sd.ellipse([cx - 16, cy - 12, cx + 16, cy + 12], fill=dim(PANEL_BLUEBLACK, 0.2))
    sd.ellipse([cx - 15, cy - 11.2, cx + 15, cy + 11], fill=PANEL_BLUEBLACK)
    sd.arc([cx - 15, cy - 11.2, cx + 15, cy + 11], 150, 300, fill=lit(PANEL_BLUEBLACK, 0.35), width=1)
    sd.ellipse([cx - 16, cy - 12, cx + 16, cy + 12], outline=dim(SUN_GOLD, 0.2), width=0.6)
    sd.rect([cx - 3, cy - 20, cx + 3, cy], fill=GREEN_PRIMARY)
    sd.line([(cx - 0.6, cy - 20), (cx - 0.6, cy)], fill=lit(GREEN_PRIMARY, 0.35), width=1)
    sd.rect([cx - 3.4, cy - 20, cx + 3.4, cy - 17.5], fill=SUN_GOLD)
    sd.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=SUN_GOLD)
    sd.ellipse([cx - 2, cy - 2, cx + 0.4, cy + 0.4], fill=lit(SUN_GOLD, 0.4))


def _rotor_disc(sd, ex, ey, r):
    """Spinning rotor read: translucent disc + brighter rim + hub dot."""
    sd.ellipse([ex - r, ey - r, ex + r, ey + r], fill=(0xB0, 0xB0, 0xA8, 70))
    sd.ellipse([ex - r, ey - r, ex + r, ey + r], outline=(0xC8, 0xC8, 0xC0, 140), width=0.5)
    sd.ellipse([ex - 0.8, ey - 0.8, ex + 0.8, ey + 0.8], fill=LEGACY_GRAY_DARK)


def sgdro_body_draw(sd, w, h):
    """Recon Drone: light green quadcopter."""
    cx, cy = w // 2, h // 2
    # Rotor arms first (under the body), then discs.
    for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        ex, ey = cx + dx * 10, cy + dy * 7
        sd.line([(cx, cy), (ex, ey)], fill=LEGACY_GRAY_DARK, width=1.2)
        sd.line([(cx, cy), (ex, ey)], fill=lit(LEGACY_GRAY_DARK, 0.3), width=0.4)
    for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        _rotor_disc(sd, cx + dx * 10, cy + dy * 7, 3.4)
    # Diamond body with a lit nose facet and camera eye.
    sd.poly([(cx, cy - 8), (cx + 6, cy), (cx, cy + 8), (cx - 6, cy)], fill=GREEN_PRIMARY, outline=GREEN_ACCENT)
    sd.poly([(cx, cy - 6.4), (cx + 3.6, cy - 1), (cx - 3.6, cy - 1)], fill=lit(GREEN_PRIMARY, 0.3))
    sd.ellipse([cx - 1.4, cy - 0.6, cx + 1.4, cy + 2.2], fill=PANEL_BLUEBLACK)
    sd.px(cx, cy - 6, SUN_GOLD)


def sgdrs_body_draw(sd, w, h):
    """Strike Drone: heavier blue-black-and-gold body with weapon pods."""
    cx, cy = w // 2, h // 2
    for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        ex, ey = cx + dx * 11, cy + dy * 8
        sd.line([(cx, cy), (ex, ey)], fill=LEGACY_GRAY_DARK, width=1.4)
        sd.line([(cx, cy), (ex, ey)], fill=lit(LEGACY_GRAY_DARK, 0.3), width=0.4)
        # Underslung weapon pods on the rear arms.
        if dy == 1:
            mx, my = cx + dx * 6.5, cy + dy * 4.5
            sd.rect([mx - 1.4, my - 1, mx + 1.4, my + 3.4], fill=dim(PANEL_BLUEBLACK, 0.2))
            sd.rect([mx - 1.4, my + 2.4, mx + 1.4, my + 3.4], fill=SUN_GOLD)
    for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        _rotor_disc(sd, cx + dx * 11, cy + dy * 8, 3.8)
    sd.poly([(cx, cy - 9), (cx + 7, cy), (cx, cy + 9), (cx - 7, cy)], fill=PANEL_BLUEBLACK, outline=SUN_GOLD)
    sd.poly([(cx, cy - 7.2), (cx + 4.2, cy - 1), (cx - 4.2, cy - 1)], fill=lit(PANEL_BLUEBLACK, 0.35))
    sd.line([(cx, cy - 9), (cx, cy + 9)], fill=dim(SUN_GOLD, 0.35), width=0.4)
    sd.ellipse([cx - 1.6, cy - 0.8, cx + 1.6, cy + 2.4], fill=RUST)
    sd.px(cx, cy - 7, SUN_GOLD)


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


def sghau_draw(sd, w, h, fullness="full", pose="idle", light_on=True):
    cx, cy = w // 2, h // 2
    # Low hex chassis on a sled base -- reads as a cargo sled, not a truck
    # bed. Top facet lit, side facets shaded.
    hexpts = [(cx, cy - 10), (cx + 9, cy - 4), (cx + 9, cy + 6), (cx, cy + 11), (cx - 9, cy + 6), (cx - 9, cy - 4)]
    sd.poly(hexpts, fill=LEGACY_GRAY, outline=LEGACY_GRAY_DARK)
    sd.poly([(cx, cy - 8.6), (cx + 7.6, cy - 3.4), (cx, cy - 1), (cx - 7.6, cy - 3.4)], fill=lit(LEGACY_GRAY, 0.25))
    sd.poly([(cx - 9, cy + 6), (cx, cy + 11), (cx, cy + 8.6), (cx - 7.4, cy + 4.8)], fill=dim(LEGACY_GRAY, 0.3))
    sd.poly([(cx + 9, cy + 6), (cx, cy + 11), (cx, cy + 8.6), (cx + 7.4, cy + 4.8)], fill=dim(LEGACY_GRAY, 0.35))
    # Skid rails.
    sd.line([(cx - 8, cy - 5), (cx - 8, cy + 7)], fill=POLE_DARK, width=0.8)
    sd.line([(cx + 8, cy - 5), (cx + 8, cy + 7)], fill=POLE_DARK, width=0.8)
    # Front magnetic scoop, lowered during the harvest pose, with a faint
    # field glow while working.
    scoop_cy = cy - 8 if pose == "idle" else cy - 4
    if pose != "idle":
        sd.ellipse([cx - 5, scoop_cy - 3, cx + 5, scoop_cy + 3], fill=GREEN_ACCENT + (45,))
    sd.arc([cx - 7, scoop_cy - 4, cx + 7, scoop_cy + 4], 200, 340, fill=GREEN_ACCENT, width=1.4)
    sd.arc([cx - 5.6, scoop_cy - 3, cx + 5.6, scoop_cy + 3], 210, 330, fill=lit(GREEN_ACCENT, 0.35), width=0.5)
    # Rear cargo canister -- fill level reads the fullness state directly, the
    # same "show the cargo" grammar HARV's own bed uses.
    can_x0, can_x1 = cx - 5, cx + 5
    can_y0, can_y1 = cy + 1, cy + 9
    box3d(sd, can_x0, can_y0, can_x1, can_y1, PANEL_BLUEBLACK, edge=0.45)
    sd.rect([can_x0, can_y0, can_x1, can_y1], outline=dim(SUN_GOLD, 0.25), width=0.4)
    frac = SGHAU_FULLNESS_FRAC[fullness]
    if frac > 0:
        fill_y0 = can_y1 - round((can_y1 - can_y0) * frac)
        sd.rect([can_x0 + 1, fill_y0, can_x1 - 1, can_y1 - 1], fill=GREEN_ACCENT)
        sd.line([(can_x0 + 1, fill_y0), (can_x1 - 1, fill_y0)], fill=lit(GREEN_ACCENT, 0.4), width=0.5)
    if light_on:
        sd.px(cx, cy - 10, SUN_GOLD)


def _sghau_frame(fullness, pose, light_on=True):
    f = render(sghau_draw, SGHAU_W, SGHAU_H, fullness, pose, light_on)
    return outline_sprite(f)


def sghau_frames(fullness):
    """One fullness variant's full frame list: idle(32) + harvest(8) +
    dock(8) + dock-loop(7) = 55 frames, in that order (matching the Start
    offsets wired in sequences/vehicles.yaml)."""
    idle = rotated_frames(sghau_draw, SGHAU_W, SGHAU_H, 32, fullness=fullness, pose="idle")
    harvest = rotated_frames(sghau_draw, SGHAU_W, SGHAU_H, 8, fullness=fullness, pose="scoop")
    dock = [_sghau_frame(fullness, "idle" if i % 2 == 0 else "scoop") for i in range(8)]
    dock_loop = [_sghau_frame(fullness, "idle", light_on=(i % 2 == 0)) for i in range(7)]
    return idle + harvest + dock + dock_loop


# ---------------------------------------------------------------------------
# Disruptor Trooper (DISR): dedicated infantry art, reversing the "leave it
# on E4's (Flame Infantry) chassis" call issue #14 made -- same rationale as
# SGHAU's reversal above (see docs/BACKLOG.md issue #36): the sprite still
# visually read as a flamethrower trooper after the name/weapon swap to an
# Arc Turret-style electric discharge, which is exactly the kind of
# silhouette/identity mismatch docs/ART_DIRECTION.md rules out.
#
# Self-contained sheet covering every sequence disr: actually needs:
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

DISR_SUIT = GREEN_PRIMARY
DISR_PANTS = dim(LEGACY_GRAY, 0.15)
DISR_HELMET = lit(LEGACY_GRAY, 0.2)


def disr_pose(sd, w, h, stance="stand", phase=0.0):
    cx, cy = w // 2, h // 2 + 2
    leg_swing = 0.0
    arm_forward = False
    spark = False
    crouch = 0
    bob = 0.0
    if stance == "walk":
        leg_swing = 3 * math.sin(phase * 2 * math.pi)
        bob = 0.6 * abs(math.sin(phase * 2 * math.pi))
    elif stance in ("shoot", "prone-shoot"):
        arm_forward = True
        spark = phase < 0.5
    elif stance == "stand2":
        arm_forward = True
    elif stance == "prone-walk":
        leg_swing = 2 * math.sin(phase * 2 * math.pi)
    if stance == "stand":
        bob = 0.35 * math.sin(phase * 2 * math.pi)  # idle breathing

    if stance in ("prone-walk", "prone-shoot"):
        crouch = 8

    hip_y = cy + 6 - crouch - bob
    leg_len = 8 - crouch // 2
    # Legs: two-tone with boot pixels; prone spreads them wider.
    spread = 2 if crouch == 0 else 3.5
    for side in (-1, 1):
        lx = cx + side * spread + side * leg_swing * (0.4 if side < 0 else -0.4) + leg_swing * (0.6 if side < 0 else -0.6)
        sd.line([(cx + side * 2, hip_y), (lx, hip_y + leg_len)], fill=DISR_PANTS, width=1.7)
        sd.px(round(lx) , round(hip_y + leg_len) - 1, dim(DISR_PANTS, 0.4))
    # Torso: suit jacket with a lit shoulder line and a belt.
    torso_top = hip_y - 10
    sd.rect([cx - 4, torso_top, cx + 4, hip_y], fill=DISR_SUIT)
    sd.line([(cx - 4, torso_top), (cx + 4, torso_top)], fill=lit(DISR_SUIT, 0.4), width=0.7)
    sd.line([(cx - 3.6, torso_top), (cx - 3.6, hip_y)], fill=lit(DISR_SUIT, 0.2), width=0.5)
    sd.line([(cx + 3.6, torso_top), (cx + 3.6, hip_y)], fill=dim(DISR_SUIT, 0.3), width=0.5)
    sd.line([(cx - 4, hip_y - 2), (cx + 4, hip_y - 2)], fill=dim(SUN_GOLD, 0.35), width=0.7)
    # Backpack discharge cell -- the "Disruptor" identity signal, replacing
    # E4's fuel tank: blue-black cell with charge pips.
    sd.rrect([cx - 3, torso_top - 2.4, cx + 3, torso_top + 4], 1, fill=PANEL_BLUEBLACK)
    sd.rrect([cx - 3, torso_top - 2.4, cx + 3, torso_top + 4], 1, outline=dim(SUN_GOLD, 0.25), width=0.4)
    sd.px(cx - 1, torso_top, SUN_GOLD)
    sd.px(cx + 1, torso_top + 1, dim(SUN_GOLD, 0.2))
    # Arms: counter-swing while walking, both toward the weapon when aiming.
    arm_y = torso_top + 3
    if arm_forward:
        sd.line([(cx - 3, arm_y + 1), (cx + 3, arm_y)], fill=dim(DISR_SUIT, 0.15), width=1.4)
        sd.line([(cx + 2, arm_y + 1), (cx + 6, arm_y - 0.5)], fill=dim(DISR_SUIT, 0.15), width=1.4)
    else:
        sw = leg_swing * 0.5
        sd.line([(cx - 3.5, arm_y), (cx - 4 - sw * 0.4, arm_y + 5)], fill=dim(DISR_SUIT, 0.15), width=1.3)
        sd.line([(cx + 3.5, arm_y), (cx + 4 + sw * 0.4, arm_y + 5)], fill=dim(DISR_SUIT, 0.15), width=1.3)
    # Head: pale helmet distinct from the torso, gold visor slit.
    head_y = torso_top - 4.6
    sd.ellipse([cx - 3, head_y - 3, cx + 3, head_y + 3], fill=DISR_HELMET)
    sd.arc([cx - 3, head_y - 3, cx + 3, head_y + 3], 150, 320, fill=lit(DISR_HELMET, 0.4), width=0.6)
    sd.line([(cx - 1.6, head_y + 0.8), (cx + 1.6, head_y + 0.8)], fill=dim(SUN_GOLD, 0.15), width=0.7)
    # Discharge prod: dark rod, twin gold prong tips, spark star when firing.
    if arm_forward:
        wx0, wy0 = cx + 4, torso_top + 3
        wx1, wy1 = cx + 10, torso_top + 0.5
    else:
        wx0, wy0 = cx + 3, torso_top + 4
        wx1, wy1 = cx + 6, torso_top + 8
    sd.line([(wx0, wy0), (wx1, wy1)], fill=LEGACY_GRAY_DARK, width=1.4)
    sd.line([(wx0, wy0), (wx1, wy1)], fill=lit(LEGACY_GRAY_DARK, 0.35), width=0.5)
    ang = math.atan2(wy1 - wy0, wx1 - wx0)
    for da in (-0.5, 0.5):
        tx = wx1 + 1.8 * math.cos(ang + da)
        ty = wy1 + 1.8 * math.sin(ang + da)
        sd.line([(wx1, wy1), (tx, ty)], fill=SUN_GOLD, width=0.8)
    if spark:
        sx, sy = wx1 + 2.6 * math.cos(ang), wy1 + 2.6 * math.sin(ang)
        sd.ellipse([sx - 2.2, sy - 2.2, sx + 2.2, sy + 2.2], fill=GREEN_ACCENT + (70,))
        sd.line([(sx - 1.8, sy), (sx + 1.8, sy)], fill=lit(SUN_GOLD, 0.4), width=0.6)
        sd.line([(sx, sy - 1.8), (sx, sy + 1.8)], fill=lit(SUN_GOLD, 0.4), width=0.6)
        sd.px(round(sx), round(sy), lit(GREEN_ACCENT, 0.5))


def _disr_frame(stance, phase=0.0):
    return outline_sprite(render(disr_pose, DISR_W, DISR_H, stance, phase))


def _facing_major_frames(stance, n_facings, n_poses):
    """Facing-major layout: n_poses consecutive frames per facing, matching
    how a sequence with both Length and Facings consumes Length x Facings
    frames (see docs/BACKLOG.md issue #35). Rotation happens at SS resolution
    before the downscale + outline."""
    w, h = DISR_W, DISR_H
    poses = []
    for p in range(n_poses):
        base = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
        disr_pose(SD(base), w, h, stance, p / max(1, n_poses))
        poses.append(base)
    frames = []
    for facing in range(n_facings):
        angle = facing * (360.0 / n_facings)
        for base in poses:
            f = base.rotate(angle, resample=Image.BICUBIC, center=(w * SS / 2, h * SS / 2))
            frames.append(outline_sprite(f.resize((w, h), Image.LANCZOS)))
    return frames


def disr_die_frame(w, h, angle_deg, fade=1.0):
    base = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
    disr_pose(SD(base), w, h, "stand")
    frame = base.rotate(angle_deg, resample=Image.BICUBIC, center=(w * SS / 2, (h / 2 + 2) * SS))
    frame = outline_sprite(frame.resize((w, h), Image.LANCZOS))
    if fade < 1.0:
        alpha = frame.getchannel("A").point(lambda a: int(a * fade))
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


def disr_parachute_draw(sd, w, h):
    disr_pose(sd, w, h, "stand")
    # Canopy: shaded gold arc + shroud lines.
    sd.arc([w / 2 - 9, 0, w / 2 + 9, 16], 180, 360, fill=SUN_GOLD, width=1.6)
    sd.arc([w / 2 - 7, 2, w / 2 + 7, 14], 200, 270, fill=lit(SUN_GOLD, 0.4), width=0.7)
    sd.line([(w / 2 - 8.4, 7), (w / 2 - 2, 14)], fill=dim(SUN_GOLD, 0.2), width=0.5)
    sd.line([(w / 2 + 8.4, 7), (w / 2 + 2, 14)], fill=dim(SUN_GOLD, 0.2), width=0.5)
    sd.line([(w / 2, 8), (w / 2, 14)], fill=dim(SUN_GOLD, 0.3), width=0.4)


def disr_frames():
    frames = []
    # stand / stand2: 1 pose x 8 facings each.
    frames += _facing_major_frames("stand", 8, 1)
    frames += _facing_major_frames("stand2", 8, 1)
    # run: 6 walk-cycle poses x 8 facings.
    frames += _facing_major_frames("walk", 8, 6)
    # shoot: 16 poses x 8 facings.
    frames += _facing_major_frames("shoot", 8, 16)
    # prone-run: 4 poses x 8 facings (prone-stand/prone-stand2 reuse these via Stride).
    frames += _facing_major_frames("prone-walk", 8, 4)
    # prone-shoot: 16 poses x 8 facings.
    frames += _facing_major_frames("prone-shoot", 8, 16)
    # idle1/idle2: single-direction breathing loops, no facings.
    for i in range(14):
        frames.append(_disr_frame("stand", i / 14))
    for i in range(16):
        frames.append(_disr_frame("stand2", i / 16))
    # die1-5: a simple topple-and-fade, single direction. Lengths match the
    # sequence's own Length values; die4/die5 fall further and fade out more.
    frames += disr_die_frames(8, 70)
    frames += disr_die_frames(8, -70)
    frames += disr_die_frames(8, 90, fade_from=0.6)
    frames += disr_die_frames(12, 100, fade_from=0.5)
    frames += disr_die_frames(18, 110, fade_from=0.35)
    # parachute: single static frame.
    frames.append(outline_sprite(render(disr_parachute_draw, DISR_W, DISR_H)))
    return frames


# ---------------------------------------------------------------------------
# Sheet assembly: two-frame building sheets (idle + genuinely-damaged) and
# cameo-style sidebar icons.
# ---------------------------------------------------------------------------

def two_frame_sheet(draw_fn, frame_w, frame_h):
    idle = render(draw_fn, frame_w, frame_h, damaged=False)
    damaged = render(draw_fn, frame_w, frame_h, damaged=True)
    return sheet_of([idle, damaged], frame_w, frame_h)


ICON_W, ICON_H = 64, 48

# Baked-in cameo name labels, matching the stock RA cameos in the same build
# menu (BARRACKS / SUB PEN / ORE REFINERY etc.), which carry the actor name in
# the sprite itself -- without them the Sungrid-original cameos read as
# inconsistent next to the ported stock ones. Text mirrors the in-game display
# names in mods/sungrid/fluent/rules.ftl (kept in sync by hand; the label is
# cosmetic, not a FluentReference the engine resolves).
ICON_LABELS = {
    "sgpwr": "Solar Array",
    "sgapwr": "Advanced Solar Array",
    "sgcry": "Cryptominer",
    "sgdai": "Datacenter for AI",
    "sgdrn": "Drone Bay",
    "sgdra": "Aerial Fabrication Bay",
    "sgshl": "Resilience Shelter",
    "sgsns": "Sensor Array",
    "sgrel": "Smart Grid Relay",
    "sgwnd": "Wind Turbine Array",
    "sghyd": "Hydrogen Plant",
    "arct": "Arc Turret",
    "sgtur": "Grid Defense Turret",
    "sgdro": "Recon Drone",
    "sgdrs": "Strike Drone",
    "sghau": "Hauler Drone",
    "disr": "Disruptor Trooper",
}

# The build menu draws cameo tooltips/labels in FreeSansBold (see
# mods/sungrid/mod.chrome.yaml Fonts), so bake the cameo name in the same
# family for typographic consistency. Fall back through common system paths,
# then PIL's default bitmap font, so the generator stays runnable anywhere.
_FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]


def _load_label_font(size):
    for path in _FONT_CANDIDATES:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def _wrap_to_width(d, text, font, max_w):
    """Greedy word-wrap; returns (lines, total_w, total_h) for the given font."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if cur and d.textlength(trial, font=font) > max_w:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    if cur:
        lines.append(cur)
    widths = [d.textlength(ln, font=font) for ln in lines]
    asc, desc = font.getmetrics()
    lh = asc + desc
    return lines, (max(widths) if widths else 0), lh * len(lines)


def draw_icon_label(icon, text):
    """Bake an uppercase name across the bottom of a cameo, the way the stock
    RA cameos carry theirs. Picks the largest FreeSansBold size (down to 7px)
    whose word-wrapped lines fit the width and a ~20px bottom band, darkens a
    gradient strip behind the text for legibility over any motif, and draws a
    1px shadow under pale text."""
    text = text.upper()
    d = ImageDraw.Draw(icon, "RGBA")
    max_w = ICON_W - 4
    max_band = 20
    for size in (10, 9, 8, 7):
        font = _load_label_font(size)
        lines, _, total_h = _wrap_to_width(d, text, font, max_w)
        if total_h <= max_band and all(d.textlength(ln, font=font) <= max_w for ln in lines):
            break
    asc, desc = font.getmetrics()
    lh = asc + desc
    band_top = ICON_H - total_h - 2
    # Darken a gradient strip behind the text so it reads over bright motifs.
    strip = Image.new("RGBA", (ICON_W, ICON_H - band_top), (0, 0, 0, 0))
    sd = ImageDraw.Draw(strip, "RGBA")
    for i in range(strip.height):
        a = int(150 * (i / max(1, strip.height - 1)) + 40)
        sd.line([(0, i), (ICON_W, i)], fill=PANEL_BLUEBLACK + (min(210, a),))
    icon.alpha_composite(strip, (0, band_top))
    text_col = mix(GREEN_ACCENT, (255, 255, 255), 0.65) + (255,)
    y = band_top + 1
    for ln in lines:
        w = d.textlength(ln, font=font)
        x = (ICON_W - w) / 2
        d.text((x + 1, y + 1), ln, font=font, fill=(0, 0, 0, 210))  # shadow
        d.text((x, y), ln, font=font, fill=text_col)
        y += lh
    return icon


def make_icon(draw_fn, frame_w, frame_h, *args, label=None, **kwargs):
    """Sidebar cameo: the motif cropped tight and fitted onto a shaded panel
    with a border, instead of a transparent whole-frame downscale."""
    # Render the motif at SS resolution and crop to content for a crisp fit.
    big = Image.new("RGBA", (frame_w * SS, frame_h * SS), (0, 0, 0, 0))
    draw_fn(SD(big), frame_w, frame_h, *args, **kwargs)
    bbox = big.getbbox()
    if bbox:
        big = big.crop(bbox)
    icon = Image.new("RGBA", (ICON_W, ICON_H))
    d = ImageDraw.Draw(icon)
    # Panel background: vertical ramp, darker at the bottom.
    top, bot = lit(PANEL_BLUEBLACK, 0.28), dim(PANEL_BLUEBLACK, 0.35)
    for y in range(ICON_H):
        d.line([(0, y), (ICON_W - 1, y)], fill=mix(top, bot, y / (ICON_H - 1)))
    # Faint ground line anchoring the motif.
    d.line([(2, ICON_H - 4), (ICON_W - 3, ICON_H - 4)], fill=lit(PANEL_BLUEBLACK, 0.12))
    # Fit the motif into the panel with a small margin.
    fit_w, fit_h = ICON_W - 6, ICON_H - 6
    scale = min(fit_w / big.width, fit_h / big.height)
    mw, mh = max(1, round(big.width * scale)), max(1, round(big.height * scale))
    motif = big.resize((mw, mh), Image.LANCZOS)
    icon.paste(motif, ((ICON_W - mw) // 2, (ICON_H - mh + 1) // 2), motif)
    # Border: dark outer frame with a lit top edge.
    d.rectangle([0, 0, ICON_W - 1, ICON_H - 1], outline=dim(LEGACY_GRAY_DARK, 0.3))
    d.line([(1, 1), (ICON_W - 2, 1)], fill=lit(LEGACY_GRAY, 0.05))
    if label:
        draw_icon_label(icon, label)
        # Redraw the border so the label strip doesn't bleed over the frame.
        d.rectangle([0, 0, ICON_W - 1, ICON_H - 1], outline=dim(LEGACY_GRAY_DARK, 0.3))
    return icon


def main():
    flat_buildings = [
        ("sgpwr", sgpwr_draw, FAM23_W, FAM23_H),
        ("sgapwr", sgapwr_draw, FAM33_W, FAM33_H),
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
        sheet = two_frame_sheet(draw_fn, w, h)
        save_pngsheet(sheet, f"{name}.png", w, h, 2, indexed=True)
        icon = make_icon(draw_fn, w, h, label=ICON_LABELS.get(name))
        save_pngsheet(icon, f"{name}icon.png", ICON_W, ICON_H, 1)

    # Turret: 32 idle-facing frames + 32 damaged-facing frames, single strip.
    idle_rot = rotated_frames(sgtur_turret_draw, 48, 44, 32, damaged=False)
    damaged_rot = rotated_frames(sgtur_turret_draw, 48, 44, 32, damaged=True)
    all_frames = idle_rot + damaged_rot
    save_pngsheet(sheet_of(all_frames, 48, 44), "sgturturret.png", 48, 44, len(all_frames), indexed=True)
    save_pngsheet(make_icon(sgtur_base_draw, 48, 44, label=ICON_LABELS["sgtur"]), "sgturicon.png", ICON_W, ICON_H, 1)

    # Drones: 32-facing body only (no damaged state, matching tran/mh60/heli).
    for name, draw_fn, fw, fh in (
        ("sgdro", sgdro_body_draw, 32, 30),
        ("sgdrs", sgdrs_body_draw, 36, 32),
    ):
        frames = rotated_frames(draw_fn, fw, fh, n=32)
        save_pngsheet(sheet_of(frames, fw, fh), f"{name}.png", fw, fh, 32, indexed=True)
        save_pngsheet(make_icon(draw_fn, fw, fh, label=ICON_LABELS.get(name)), f"{name}icon.png", ICON_W, ICON_H, 1)

    # Hauler Drone (SGHAU): three parallel fullness-state images, identical
    # 55-frame layout (idle 32 + harvest 8 + dock 8 + dock-loop 7), plus one
    # shared icon (fullness has no icon variant, matching harv/harvempty/
    # harvhalf's own Inherits: harv icon reuse).
    for fullness, filename in (("full", "sghau.png"), ("half", "sghauhalf.png"), ("empty", "sghauempty.png")):
        frames = sghau_frames(fullness)
        save_pngsheet(sheet_of(frames, SGHAU_W, SGHAU_H), filename, SGHAU_W, SGHAU_H, len(frames), indexed=True)
    save_pngsheet(
        make_icon(sghau_draw, SGHAU_W, SGHAU_H, "full", "idle", label=ICON_LABELS["sghau"]),
        "sghauicon.png", ICON_W, ICON_H, 1,
    )

    # Disruptor Trooper (DISR): one self-contained 437-frame sheet, plus icon.
    disr_all = disr_frames()
    save_pngsheet(sheet_of(disr_all, DISR_W, DISR_H), "disr.png", DISR_W, DISR_H, len(disr_all), indexed=True)
    save_pngsheet(
        make_icon(disr_pose, DISR_W, DISR_H, "stand2", label=ICON_LABELS["disr"]),
        "disricon.png", ICON_W, ICON_H, 1,
    )

    print("done")


if __name__ == "__main__":
    main()
