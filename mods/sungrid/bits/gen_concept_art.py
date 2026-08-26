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
        # Already-indexed sheets (the infantry art below draws straight in
        # palette indices) pass through untouched -- to_indexed()'s nearest-RGB
        # match would only be able to reproduce them approximately.
        if img.mode != "P":
            img = to_indexed(img)
        img.save(path, pnginfo=meta, transparency=TRANSPARENT_IDX)
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
# Native-resolution palette-index canvas.
#
# The supersample + LANCZOS + to_indexed() path above is right for the
# building/vehicle art (curves and 32 rotated facings resolve cleanly), but
# wrong at infantry scale: a 14px-tall figure downscaled from 4x comes out as
# an anti-aliased blur that the 1-bit-alpha indexed conversion then has to
# hard-threshold, so edges go ragged and the interior turns to dither noise.
# Every stock RA infantry sheet is instead authored one pixel at a time in
# palette indices, with hard edges and a small deliberate value ramp (decoding
# e6.shp shows a single stand frame using ~10 distinct indices in ~95 pixels).
# PC draws that way: no scaling, no blending, indices only.
# ---------------------------------------------------------------------------

class PC:
    """A frame-sized grid of palette indices (0 = transparent)."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.px = [[0] * w for _ in range(h)]

    def set(self, x, y, idx):
        x, y = int(round(x)), int(round(y))
        if idx and 0 <= x < self.w and 0 <= y < self.h:
            self.px[y][x] = idx

    def get(self, x, y):
        x, y = int(round(x)), int(round(y))
        if 0 <= x < self.w and 0 <= y < self.h:
            return self.px[y][x]
        return 0

    def hline(self, x0, x1, y, idx):
        for x in range(int(round(x0)), int(round(x1)) + 1):
            self.set(x, y, idx)

    def vline(self, x, y0, y1, idx):
        for y in range(int(round(y0)), int(round(y1)) + 1):
            self.set(x, y, idx)

    def box(self, x0, y0, x1, y1, idx):
        for y in range(int(round(y0)), int(round(y1)) + 1):
            self.hline(x0, x1, y, idx)

    def blob(self, cx, cy, rx, ry, idx):
        """Small filled ellipse, rounded at native resolution."""
        cx, cy = float(cx), float(cy)
        for y in range(int(math.floor(cy - ry)), int(math.ceil(cy + ry)) + 1):
            for x in range(int(math.floor(cx - rx)), int(math.ceil(cx + rx)) + 1):
                dx = (x - cx) / max(0.4, rx)
                dy = (y - cy) / max(0.4, ry)
                if dx * dx + dy * dy <= 1.15:
                    self.set(x, y, idx)

    def ray(self, x0, y0, x1, y1, idx):
        """Bresenham-ish 1px line (no anti-aliasing)."""
        steps = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 1
        for i in range(steps + 1):
            t = i / steps
            self.set(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, idx)

    def stamp(self, x, y, rows, cmap):
        """Paint an ASCII template; '.' / ' ' leave the pixel untouched."""
        for dy, row in enumerate(rows):
            for dx, ch in enumerate(row):
                if ch in cmap:
                    self.set(x + dx, y + dy, cmap[ch])

    def dissolve(self, keep):
        """Drop pixels on an ordered 4x4 pattern (keep in 0..1). Indexed
        sprites have 1-bit alpha, so a fade-out has to be a dither, not an
        alpha ramp -- the first pass's alpha fade was silently thresholded
        back to fully opaque/absent by to_indexed()."""
        order = (0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5)
        cut = keep * 16
        for y in range(self.h):
            for x in range(self.w):
                if self.px[y][x] and order[(y % 4) * 4 + (x % 4)] >= cut:
                    self.px[y][x] = 0


def _palette_flat():
    flat = []
    for c in PLAYER_PAL:
        flat += list(c)
    return flat


def sheet_of_indexed(frames, frame_w, frame_h):
    """Assemble PC frames into one P-mode strip on the player palette."""
    sheet = Image.new("P", (frame_w * len(frames), frame_h), TRANSPARENT_IDX)
    sheet.putpalette(_palette_flat())
    dst = sheet.load()
    for i, f in enumerate(frames):
        for y in range(frame_h):
            row = f.px[y]
            for x in range(frame_w):
                if row[x]:
                    dst[i * frame_w + x, y] = row[x]
    return sheet


# Cameo/preview rendering of an indexed frame. The player-remap ramp (80-95)
# renders as the owner's colour in game; for a standalone cameo there is no
# owner, so substitute the mod's own green ramp so the preview reads the way a
# Sungrid-coloured player's trooper does rather than palette-file khaki.
_PREVIEW_REMAP = {
    80: lit(GREEN_ACCENT, 0.35), 81: lit(GREEN_ACCENT, 0.2), 82: GREEN_ACCENT,
    83: mix(GREEN_ACCENT, GREEN_PRIMARY, 0.4), 84: mix(GREEN_ACCENT, GREEN_PRIMARY, 0.6),
    85: lit(GREEN_PRIMARY, 0.15), 86: GREEN_PRIMARY, 87: GREEN_PRIMARY,
    88: dim(GREEN_PRIMARY, 0.15), 89: dim(GREEN_PRIMARY, 0.3),
    90: dim(GREEN_PRIMARY, 0.4), 91: dim(GREEN_PRIMARY, 0.5),
    92: dim(GREEN_PRIMARY, 0.6), 93: dim(GREEN_PRIMARY, 0.7),
    94: dim(GREEN_PRIMARY, 0.8), 95: dim(GREEN_PRIMARY, 0.85),
}


def indexed_to_rgba(frame, drop_shadow=True):
    img = Image.new("RGBA", (frame.w, frame.h), (0, 0, 0, 0))
    dst = img.load()
    for y in range(frame.h):
        for x in range(frame.w):
            idx = frame.px[y][x]
            if not idx or (drop_shadow and idx == SHADOW_IDX):
                continue
            dst[x, y] = _PREVIEW_REMAP.get(idx, PLAYER_PAL[idx]) + (255,)
    return img


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


def sphere(sd, x0, y0, x1, y1, fill, steps=10, lit_f=0.30, dim_f=0.38):
    """Rounded mass shaded as a real sphere: nested ellipses shrinking toward a
    highlight up-and-left of centre, so the ramp runs dark rim -> body ->
    small highlight instead of dome3d's three hand-placed blobs. The lit half
    of the ramp is deliberately gamma-curved: a linear one puts a pale wash
    over most of the dome and reads as gloss, not curvature."""
    cxm, cym = (x0 + x1) / 2, (y0 + y1) / 2
    hx, hy = cxm - (x1 - x0) * 0.15, cym - (y1 - y0) * 0.19
    for i in range(steps):
        t = i / (steps - 1)
        a = 1 - t * 0.93
        col = (dim(fill, dim_f * (1 - t / 0.5)) if t < 0.5
               else lit(fill, lit_f * ((t - 0.5) / 0.5) ** 1.8))
        sd.ellipse([hx + (x0 - hx) * a, hy + (y0 - hy) * a,
                    hx + (x1 - hx) * a, hy + (y1 - hy) * a], fill=col)


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


def contact_shadow(sd, cx, cy, rx, ry, f=0.45, base=CONCRETE):
    """Opaque ambient-occlusion pool where a mass meets the pad it stands on.

    Deliberately opaque (docs/BACKLOG.md issue #72). This used to draw
    (0, 0, 0, alpha=70), which the indexed pipeline does not merely fail to
    darken: to_indexed maps anything under a=128 to TRANSPARENT_IDX, so every
    pixel the ellipse covered was *erased*, punching a lens-shaped hole through
    the building's own ground pad that terrain showed through. Painting the
    shadow as a solid dim() of whatever it lands on is the same fix sgvlt_draw
    already used, and it is also what the stock art does -- decoding fact.shp
    (Construction Yard) against temperat.pal shows RA buildings bake no long
    cast shadow at all, just a 1-3px ShadowIndex rim hugging the lower edge of
    a silhouette that already fills its own frame. So the shadow a building
    here needs is this: a painted pool on its own pad, not a projection."""
    sd.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=dim(base, f))



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
# Axonometric mesh renderer (docs/BACKLOG.md issue #65).
#
# Everything above draws a *single* front-above elevation and, for rotating
# actors, spins that one picture with rotated_frames(). That is fine for the
# drones (genuinely top-down, radially symmetric) but wrong for a turret: the
# real thing keeps its housing still and swings a barrel, whereas rotating the
# picture swings the housing, the base, and the key light along with it.
# Decoding the stock rotating turret in this directory (sam2.shp, 48x24, 32
# idle facings + 32 damaged) shows how the legacy art solves it: 227 of its
# pixels are byte-identical across all 32 facings -- the mount never moves --
# and only the superstructure is redrawn per facing, as a genuine viewpoint of
# a solid, with the light staying put in world space.
#
# This is the same fault (and the same fix) as the Disruptor Trooper rebuild in
# issue #64, so it gets the same treatment: build the object once in 3D and
# draw each facing as a real view of it. Projection is orthographic with the
# ground plane foreshortened 2:1 and height 1:1, measured off the stock
# 32-facing art (heli.shp: north-facing height 22px and west-facing width 37px
# over a 13px beam give a ground factor of (22-9)/(37-13) = 0.54).
# ---------------------------------------------------------------------------

MESH_KY = 0.5          # ground-plane depth foreshortening (2:1)
MESH_AMBIENT = 0.34    # fraction of full brightness a fully-unlit face keeps


def _v_norm(v):
    m = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2]) or 1.0
    return (v[0] / m, v[1] / m, v[2] / m)


def _v_dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


# Key light from the front-above-left, matching the "one top-left key light"
# convention every other sprite here is drawn to. The cast shadow below is
# deliberately NOT derived from it: stock RA throws building shadows down and
# to the right (light from behind-left), and matching that convention matters
# more for sitting next to the ported art than being physically consistent
# with the face shading -- the same split the infantry sheet already uses.
MESH_LIGHT = _v_norm((-0.5, -0.35, 0.8))
MESH_VIEW = _v_norm((0.0, -1.0, MESH_KY))   # scene -> camera (south and above)
MESH_SHADOW_SLANT = (0.55, -0.30)           # per unit of height: +x, -y


def _rotz(p, c, s):
    return (p[0] * c - p[1] * s, p[0] * s + p[1] * c, p[2])


def _project(p, ox, oy):
    """World (x east, y north, z up) -> screen pixels."""
    return (ox + p[0], oy - (p[1] * MESH_KY + p[2]))


def _face_normal(v):
    ax, ay, az = (v[1][i] - v[0][i] for i in range(3))
    bx, by, bz = (v[2][i] - v[0][i] for i in range(3))
    return _v_norm((ay * bz - az * by, az * bx - ax * bz, ax * by - ay * bx))


# Illumination is snapped to this many steps before it becomes a colour, so a
# material's faces land on a handful of flat tones rather than a continuous
# ramp -- the small per-material ramp the stock art is built from (a sam2.shp
# facing uses ~30 palette indices in total). Note this only flattens face
# interiors: most of the residual index spread in the finished sheet comes
# from the 4x -> 1x downscale blending along face edges, which is inherent to
# this pipeline and would need native-index authoring (as the infantry sheet
# uses) to remove entirely.
MESH_SHADE_STEPS = 6


def _shaded(color, s):
    """Map a 0..1 illumination onto the colour's dim..lit range."""
    s = round(s * MESH_SHADE_STEPS) / MESH_SHADE_STEPS
    return lit(color, (s - 0.62) * 1.25) if s >= 0.62 else dim(color, (0.62 - s) * 0.95)


def mesh_screen(p, ox, oy, deg=0.0):
    """Where a model-space point lands on screen -- for placing effect
    overlays (muzzle glow, discharge arc) on top of a rendered mesh."""
    rad = math.radians(deg)
    return _project(_rotz(p, math.cos(rad), math.sin(rad)), ox, oy)


# Shared hull/plating materials for the two defence structures, so the Grid
# Defense Turret and the Arc Turret read as the same manufacturer.
_TUR_HULL = mix(PANEL_BLUEBLACK, LEGACY_GRAY, 0.30)
_TUR_CAP = mix(LEGACY_GRAY, PANEL_BLUEBLACK, 0.25)
_TUR_BARREL = mix(LEGACY_GRAY_DARK, LEGACY_GRAY, 0.40)


def _convex_hull(points):
    """Monotone-chain hull of a small 2D point set."""
    pts = sorted(set((round(x, 3), round(y, 3)) for x, y in points))
    if len(pts) < 3:
        return pts

    def half(seq):
        out = []
        for p in seq:
            while len(out) >= 2:
                (ax, ay), (bx, by) = out[-2], out[-1]
                if (bx - ax) * (p[1] - ay) - (by - ay) * (p[0] - ax) > 0:
                    break
                out.pop()
            out.append(p)
        return out[:-1]

    return half(pts) + half(pts[::-1])


class Mesh:
    """A handful of convex quads, drawn back-to-front with per-face flat
    shading. Deliberately tiny: no clipping, no z-buffer, no textures -- at
    24-odd pixels across, painter's order over a dozen faces is all a turret
    needs, and flat faces are what keeps the indexed conversion clean."""

    def __init__(self):
        self.faces = []
        self.solids = []   # vertex groups, one per solid, for the cast shadow

    def poly(self, verts, color, order=0):
        self.faces.append((list(verts), color, order))
        return self

    def quad(self, a, b, c, d, color, order=0):
        return self.poly((a, b, c, d), color, order)

    def box(self, x0, y0, z0, x1, y1, z1, color, top=None, order=0, shadow=True,
            top_face=True):
        """Axis-aligned box. Only the four sides and the top are emitted --
        the underside is never visible from this camera. `order` overrides
        painter's depth for detail that sits proud of a parent solid: this
        projection makes higher geometry sort as nearer, so a thin band
        wrapped around a tall hull loses the depth test against the hull's own
        front face however the key is computed. Ordering it explicitly is
        correct here because back faces are culled anyway."""
        top = color if top is None else top
        if shadow:
            self.solids.append([(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)])
        if top_face:
            self.quad((x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1), top, order)  # +z
        self.quad((x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1), color, order)    # -y front
        self.quad((x1, y1, z0), (x0, y1, z0), (x0, y1, z1), (x1, y1, z1), color, order)    # +y back
        self.quad((x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1), color, order)    # +x
        self.quad((x0, y1, z0), (x0, y0, z0), (x0, y0, z1), (x0, y1, z1), color, order)    # -x
        return self

    def prism(self, cx, cy, z0, z1, r, color, sides=10, top=None, phase=0.0, order=0):
        """Upright n-gon column standing in for a cylinder (the barrel sleeve,
        the mount collar). Its top cap is emitted so it reads as solid."""
        top = color if top is None else top
        ring = [(cx + r * math.cos(phase + i * 2 * math.pi / sides),
                 cy + r * math.sin(phase + i * 2 * math.pi / sides)) for i in range(sides)]
        self.solids.append([(px, py, z) for px, py in ring for z in (z0, z1)])
        for i in range(sides):
            (ax, ay), (bx, by) = ring[i], ring[(i + 1) % sides]
            self.quad((ax, ay, z0), (bx, by, z0), (bx, by, z1), (ax, ay, z1), color, order)
        self.poly([(px, py, z1) for px, py in ring], top, order)
        return self

    def strut(self, a, b, r, color, cap=None, order=0, shadow=True):
        """Square-section beam between two arbitrary points (electrode rods,
        braces) -- the one shape here that is not axis-aligned."""
        ax = _v_norm(tuple(b[i] - a[i] for i in range(3)))
        up = (0.0, 0.0, 1.0) if abs(ax[2]) < 0.9 else (1.0, 0.0, 0.0)
        u = _v_norm((ax[1] * up[2] - ax[2] * up[1], ax[2] * up[0] - ax[0] * up[2],
                     ax[0] * up[1] - ax[1] * up[0]))
        v = (ax[1] * u[2] - ax[2] * u[1], ax[2] * u[0] - ax[0] * u[2], ax[0] * u[1] - ax[1] * u[0])
        corners = []
        for su, sv in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            off = tuple(r * (su * u[i] + sv * v[i]) for i in range(3))
            corners.append((tuple(a[i] + off[i] for i in range(3)),
                            tuple(b[i] + off[i] for i in range(3))))
        if shadow:
            self.solids.append([p for pair in corners for p in pair])
        for i in range(4):
            (a0, b0), (a1, b1) = corners[i], corners[(i + 1) % 4]
            self.quad(a0, a1, b1, b0, color, order)
        self.poly([c[1] for c in corners], cap or lit(color, 0.25), order)
        return self

    def _oriented(self, deg):
        rad = math.radians(deg)
        c, s = math.cos(rad), math.sin(rad)
        return [([_rotz(p, c, s) for p in verts], color, order) for verts, color, order in self.faces]

    def draw(self, sd, ox, oy, deg=0.0):
        out = []
        for verts, color, order in self._oriented(deg):
            n = _face_normal(verts)
            if _v_dot(n, MESH_VIEW) <= 0.015:      # back face
                continue
            depth = sum(_v_dot(p, MESH_VIEW) for p in verts) / len(verts)
            shade = MESH_AMBIENT + (1 - MESH_AMBIENT) * max(0.0, _v_dot(n, MESH_LIGHT))
            out.append(((order, depth), [_project(p, ox, oy) for p in verts], _shaded(color, shade)))
        out.sort(key=lambda t: t[0])
        for _, pts, col in out:
            sd.poly(pts, fill=col, outline=col)

    def draw_shadow(self, sd, ox, oy, deg=0.0, color=(0, 0, 0, 255)):
        """Flatten each solid onto the ground plane along the shadow slant and
        fill its 2D hull. Per-solid hulls rather than per-face polygons: a face
        on edge flattens to a sliver, which showed up as detached streaks
        instead of one shadow."""
        rad = math.radians(deg)
        c, s = math.cos(rad), math.sin(rad)
        sx, sy = MESH_SHADOW_SLANT
        for solid in self.solids:
            pts = []
            for p in solid:
                q = _rotz(p, c, s)
                pts.append(_project((q[0] + sx * q[2], q[1] + sy * q[2], 0.0), ox, oy))
            hull = _convex_hull(pts)
            if len(hull) >= 3:
                sd.poly(hull, fill=color, outline=color)


def indexed_strip(bodies, shadows, frame_w, frame_h):
    """Assemble RGBA frames (+ optional native-resolution shadow masks) into a
    single indexed strip. Shadows have to be injected here rather than drawn
    into the RGBA frame: SHADOW_IDX is excluded from the nearest-colour search
    in _index_for (it is a stencil index, not a colour), so a black blob drawn
    into the frame would come back as ordinary near-black paint."""
    sheet = Image.new("P", (frame_w * len(bodies), frame_h), TRANSPARENT_IDX)
    sheet.putpalette(_palette_flat())
    dst = sheet.load()
    for i, body in enumerate(bodies):
        src = body.convert("RGBA").load()
        shd = shadows[i].load() if shadows and shadows[i] is not None else None
        for y in range(frame_h):
            for x in range(frame_w):
                r, g, b, a = src[x, y]
                if a >= 128:
                    dst[i * frame_w + x, y] = _index_for((r, g, b))
                elif shd is not None and shd[x, y] >= 110:
                    dst[i * frame_w + x, y] = SHADOW_IDX
    return sheet


def render_shadow_mask(draw_fn, w, h, *args, **kwargs):
    """Native-resolution 'L' coverage mask of a shadow-only draw pass."""
    img = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
    draw_fn(SD(img), w, h, *args, **kwargs)
    return img.getchannel("A").resize((w, h), Image.LANCZOS)


# ---------------------------------------------------------------------------
# Per-building motifs. Each draw_fn renders one frame into a frame_w x
# frame_h (native-pixel) canvas via the SD scaled-draw wrapper; damaged=True
# redraws the same building with status lights off + scorch/rust decals.
# ---------------------------------------------------------------------------

FAM23_W, FAM23_H = 66, 54   # 2x3 footprint family (matches sgpwr.png)
FAM33_W, FAM33_H = 90, 60   # 3x3 footprint family (matches sgapwr.png)
SGSHL_W, SGSHL_H = 72, 50   # 2x2 footprint
SG1x1_W, SG1x1_H = 40, 36   # 1x1 footprint


def capped_box(sd, x0, y0, x1, y1, fill, depth=3.0, edge=0.34):
    """A box seen from the game's front-above angle: lit top face receding
    up-and-right, a shaded right side face, then the front face on top --
    gives ground-level equipment (battery cells, rack blocks) real volume
    instead of a flat front elevation."""
    dx, dy = depth, depth * 0.6
    sd.poly([(x0, y0), (x1, y0), (x1 + dx, y0 - dy), (x0 + dx, y0 - dy)], fill=lit(fill, edge))
    sd.line([(x0 + dx, y0 - dy), (x1 + dx, y0 - dy)], fill=lit(fill, edge + 0.2), width=0.5)
    sd.poly([(x1, y0), (x1, y1), (x1 + dx, y1 - dy), (x1 + dx, y0 - dy)], fill=dim(fill, edge))
    sd.rect([x0, y0, x1, y1], fill=fill)
    sd.line([(x0, y0), (x1, y0)], fill=lit(fill, edge * 0.5))
    sd.line([(x0, y0), (x0, y1)], fill=lit(fill, edge * 0.3))
    sd.line([(x0, y1), (x1, y1)], fill=dim(fill, edge))


class Roof:
    """The receding top plane of a building mass, plus the mapping needed to
    put things *on* it.

    capped_box gives ground-level equipment volume by drawing a lit top face
    receding up-and-right; a building needs the same top face, but big enough
    that rooftop plant (chiller banks, vents, a beacon mast) has to sit on it in
    the right perspective rather than floating over the eaves. `at(u, v)` maps
    roof-space -- u across the eaves 0..1, v from eaves (0) to ridge (1) -- onto
    screen pixels, so a rooftop unit can be drawn as a capped_box at at(u, v)
    with its own small depth and still line up with the plane under it."""

    def __init__(self, x0, y_eaves, x1, depth):
        self.x0, self.x1, self.y = x0, x1, y_eaves
        self.dx, self.dy = depth, depth * 0.6

    def at(self, u, v):
        return (self.x0 + (self.x1 - self.x0) * u + self.dx * v, self.y - self.dy * v)

    def quad(self):
        return [self.at(0, 0), self.at(1, 0), self.at(1, 1), self.at(0, 1)]

    def draw(self, sd, fill, edge=0.34, seams=0):
        sd.poly(self.quad(), fill=lit(fill, edge))
        sd.line([self.at(0, 1), self.at(1, 1)], fill=lit(fill, edge + 0.22), width=0.6)
        sd.line([self.at(0, 0), self.at(0, 1)], fill=lit(fill, edge + 0.1), width=0.4)
        sd.line([self.at(1, 0), self.at(1, 1)], fill=dim(fill, 0.18), width=0.4)
        for i in range(1, seams):
            u = i / seams
            sd.line([self.at(u, 0.04), self.at(u, 0.96)], fill=dim(fill, 0.12), width=0.4)
        return self


def tilted_collector(sd, x0, y0, x1, y1, depth=6.0, damaged_crack=False):
    """A solar collector seen from front-above: the cell surface is a shallow
    parallelogram tilted back-and-up so it reads as an angled panel catching
    the sky, with a bright top sky-gleam fading toward the bottom, cell
    mullions following the shear, and a lit aluminium frame."""
    dx = depth * 0.45
    top_y = y0 - depth
    n = 9
    for i in range(n):
        t0, t1 = i / n, (i + 1) / n
        yA = top_y + (y1 - top_y) * t0
        yB = top_y + (y1 - top_y) * t1
        xa, xb = dx * (1 - t0), dx * (1 - t1)
        b = 0.55 * (1 - t0) ** 1.3
        sd.poly([(x0 + xb, yB), (x1 + xb, yB), (x1 + xa, yA), (x0 + xa, yA)], fill=lit(PANEL_BLUEBLACK, b))
    # Cell mullions, following the shear.
    cols = max(3, round((x1 - x0) / 6))
    for c in range(1, cols):
        f = c / cols
        gx = x0 + (x1 - x0) * f
        sd.line([(gx + dx, top_y), (gx, y1)], fill=dim(PANEL_BLUEBLACK, 0.55), width=0.4)
    midy = (top_y + y1) / 2
    sd.line([(x0 + dx * 0.5, midy - depth * 0.25), (x1 + dx * 0.5, midy - depth * 0.25)],
            fill=dim(PANEL_BLUEBLACK, 0.5), width=0.4)
    # Aluminium frame, top edge lit.
    fbl, fbr = (x0, y1), (x1, y1)
    btl, btr = (x0 + dx, top_y), (x1 + dx, top_y)
    sd.line([btl, btr], fill=lit(LEGACY_GRAY, 0.45), width=0.6)
    sd.line([fbl, btl], fill=lit(LEGACY_GRAY, 0.2), width=0.5)
    sd.line([fbr, btr], fill=dim(LEGACY_GRAY, 0.1), width=0.5)
    sd.line([fbl, fbr], fill=dim(LEGACY_GRAY, 0.25), width=0.5)
    # Soft sky glint near the top-left of the surface.
    sd.line([(x0 + dx * 0.7, top_y + depth * 0.2), (x0 + (x1 - x0) * 0.4 + dx * 0.4, midy)],
            fill=lit(PANEL_BLUEBLACK, 0.7) + (150,), width=0.5)
    if damaged_crack:
        cxm = (x0 + x1) / 2
        sd.line([(cxm - 3 + dx * 0.6, top_y + 2), (cxm + dx * 0.3, midy), (cxm + 2, y1 - 1)],
                fill=lit(PANEL_BLUEBLACK, 0.85), width=0.5)


def sgpwr_draw(sd, w=FAM23_W, h=FAM23_H, damaged=False):
    """Solar Array: two collector panels over the shared conduit band --
    issue #12's motif, redrawn with volumetric (tilted, top-lit) panels."""
    ground_y0, ground_y1 = h - 12, h
    gold_y0, gold_y1 = ground_y0 - 8, ground_y0
    draw_ground_strip(sd, 2, w - 2, ground_y0, ground_y1, seed=11)
    draw_gold_band(sd, 6, w - 6, gold_y0, gold_y1)
    panel_y0, panel_y1 = 10, gold_y0 - 7
    for i, (px0, px1) in enumerate(((6, 30), (35, 59))):
        contact_shadow(sd, (px0 + px1) / 2 + 1, gold_y0 + 0.7, (px1 - px0) / 2, 1.7, base=SUN_GOLD)
        # Support struts down to the conduit.
        for px in (px0 + 5, px1 - 3):
            sd.line([(px, panel_y1 - 1), (px + 2, gold_y0)], fill=POLE_DARK, width=1.1)
            sd.line([(px - 0.4, panel_y1 - 1), (px + 1.6, gold_y0)], fill=lit(POLE_DARK, 0.35), width=0.4)
        tilted_collector(sd, px0, panel_y0, px1, panel_y1, depth=6, damaged_crack=(damaged and i == 0))
        if not damaged:
            sd.px(px0 + 2, panel_y0 - 5, lit(GREEN_ACCENT, 0.3))
    if damaged:
        scorch(sd, [(20, panel_y1 - 3, 3.5), (w - 18, gold_y0 + 3, 2.5)])


def sgapwr_draw(sd, w=FAM33_W, h=FAM33_H, damaged=False):
    """Advanced Solar Array: three collectors + a storage cell, on the 3x3
    footprint -- redrawn with volumetric panels and a capped storage box."""
    ground_y0, ground_y1 = h - 13, h
    gold_y0, gold_y1 = ground_y0 - 9, ground_y0
    draw_ground_strip(sd, 2, w - 2, ground_y0, ground_y1, seed=12)
    draw_gold_band(sd, 5, w - 5, gold_y0, gold_y1)
    panel_y0, panel_y1 = 9, gold_y0 - 8
    for i, (px0, px1) in enumerate(((5, 27), (33, 55), (61, 83))):
        contact_shadow(sd, (px0 + px1) / 2 + 1, gold_y0 + 0.7, (px1 - px0) / 2, 1.7, base=SUN_GOLD)
        for px in (px0 + 5, px1 - 3):
            sd.line([(px, panel_y1 - 1), (px + 2, gold_y0)], fill=POLE_DARK, width=1.1)
            sd.line([(px - 0.4, panel_y1 - 1), (px + 1.6, gold_y0)], fill=lit(POLE_DARK, 0.35), width=0.4)
        tilted_collector(sd, px0, panel_y0, px1, panel_y1, depth=6, damaged_crack=(damaged and i == 1))
        if not damaged:
            sd.px(px0 + 2, panel_y0 - 5, lit(GREEN_ACCENT, 0.3))
    # Ground-level storage cell between the middle poles, now a capped box.
    bx0, bx1 = 37, 53
    capped_box(sd, bx0, gold_y0 - 8, bx1, gold_y0 - 1, PANEL_BLUEBLACK, depth=2.5, edge=0.4)
    for i in range(3):
        sd.px(bx0 + 3 + i * 4, gold_y0 - 4, (SUN_GOLD if not damaged else dim(SUN_GOLD, 0.6)))
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
    block_w, block_h = 13, 12
    gap = 3
    total_w = cols * block_w + (cols - 1) * gap
    x0 = (w - total_w) // 2
    contact_shadow(sd, w / 2 + 2, gold_y0 + 0.7, total_w / 2, 1.7, base=SUN_GOLD)
    # Back row first, then front row, so the volumetric racks overlap correctly.
    for r in (rows - 1, 0):
        for c in range(cols):
            bx = x0 + c * (block_w + gap)
            by = gold_y0 - (r + 1) * (block_h + 2)
            # Slightly mismatched rack heights: scavenged, not uniform.
            jitter = (c * 2 + r) % 3 - 1
            capped_box(sd, bx, by + jitter, bx + block_w, by + block_h, LEGACY_GRAY, depth=2.5, edge=0.3)
            # Vent slits.
            for vy in range(3):
                sd.line([(bx + 2, by + jitter + 3 + vy * 3), (bx + block_w - 2, by + jitter + 3 + vy * 3)],
                        fill=dim(LEGACY_GRAY, 0.4), width=0.5)
            # Status light: amber, off when damaged.
            sd.px(bx + 2, by + jitter + 1, SUN_GOLD if not damaged and (c + r) % 3 != 2 else dim(LEGACY_GRAY, 0.3))
            # Rust streaks on the outer racks.
            if c in (0, cols - 1):
                sd.rect([bx + block_w - 3, by + jitter + block_h - 4, bx + block_w - 2, by + jitter + block_h], fill=RUST)
    # Tangle of power cabling down to the conduit.
    sd.line([(x0 + 8, gold_y0 - 2), (x0 + 12, gold_y0 + 2)], fill=POLE_DARK, width=0.7)
    sd.line([(x0 + total_w - 8, gold_y0 - 2), (x0 + total_w - 14, gold_y0 + 2)], fill=POLE_DARK, width=0.7)
    if damaged:
        scorch(sd, [(x0 + total_w // 2, gold_y0 - 6, 3.5), (x0 + 4, gold_y0 + 2, 2)])


def sgdai_draw(sd, w=FAM23_W, h=FAM23_H, damaged=False):
    """Datacenter for AI: a sealed machine hall under a regular rooftop chiller
    bank -- the tidy, capital-intensive foil to sgcry's open rack of scavenged
    boxes.

    Volumetric pass (issue #48 batch 3): the flat 4x3 grid of front-elevation
    tiles became one enclosed mass with a real receding roof plane (Roof)
    carrying plant, so it reads as a building rather than a tiled wall, and the
    server identity moved onto lit window bands in the front face."""
    ground_y0, ground_y1 = h - 12, h
    gold_y0, gold_y1 = ground_y0 - 8, ground_y0
    draw_ground_strip(sd, 2, w - 2, ground_y0, ground_y1, seed=2)
    draw_gold_band(sd, 6, w - 6, gold_y0, gold_y1)
    hx0, hx1, eaves, depth = 7, 53, 18, 8.0
    wall = mix(PANEL_BLUEBLACK, LEGACY_GRAY, 0.14)
    contact_shadow(sd, (hx0 + hx1) / 2 + 2, gold_y0 + 0.7, (hx1 - hx0) / 2, 1.7, base=SUN_GOLD)
    roof = Roof(hx0, eaves, hx1, depth)
    roof.draw(sd, wall, edge=0.34, seams=4)
    # Rooftop chiller bank: identical units on a regular pitch, which is where
    # the "industrial-scale, bought not scavenged" read comes from.
    for i, u in enumerate((0.17, 0.5, 0.83)):
        bx, by = roof.at(u, 0.6)
        sag = 1.6 if (damaged and i == 1) else 0.0
        capped_box(sd, bx - 5, by - 4 + sag, bx + 5, by + sag,
                   mix(LEGACY_GRAY, PANEL_BLUEBLACK, 0.35), depth=2.0, edge=0.34)
        for k in range(3):
            sd.line([(bx - 3.4 + k * 3, by - 3.2 + sag), (bx - 3.4 + k * 3, by - 0.8 + sag)],
                    fill=dim(LEGACY_GRAY, 0.45), width=0.5)
        sd.px(bx + 3.6, by - 4.6 + sag, GREEN_ACCENT if not damaged else dim(LEGACY_GRAY, 0.35))
    # Ridge mast: the one asymmetric silhouette cue at this distance.
    mx, my = roof.at(0.5, 0.99)
    sd.line([(mx, my), (mx, my - 7)], fill=LEGACY_GRAY_DARK, width=0.8)
    sd.line([(mx - 0.4, my), (mx - 0.4, my - 7)], fill=lit(LEGACY_GRAY_DARK, 0.4), width=0.3)
    sd.px(mx, my - 8, SUN_GOLD if not damaged else dim(LEGACY_GRAY, 0.3))
    # Front wall: eaves shadow at the top, slight left-to-right falloff.
    for i in range(5):
        t0, t1 = i / 5, (i + 1) / 5
        sd.rect([hx0 + (hx1 - hx0) * t0, eaves, hx0 + (hx1 - hx0) * t1, gold_y0],
                fill=lit(wall, 0.12 * (1 - t0)))
    sd.line([(hx0, eaves), (hx1, eaves)], fill=dim(wall, 0.4), width=0.8)
    sd.line([(hx0, gold_y0 - 0.4), (hx1, gold_y0 - 0.4)], fill=dim(wall, 0.35), width=0.5)
    sd.line([(hx0, eaves + 1.6), (hx1, eaves + 1.6)], fill=lit(wall, 0.28), width=0.4)
    # Server window bands: two perfectly regular rows of lit apertures.
    for r, wy in enumerate((eaves + 4, eaves + 9.5)):
        for c in range(6):
            wx = hx0 + 3 + c * 6
            sd.rect([wx, wy, wx + 4.2, wy + 3.2], fill=dim(wall, 0.62))
            sd.line([(wx, wy), (wx + 4.2, wy)], fill=dim(wall, 0.8), width=0.4)
            broke = damaged and (c, r) in ((1, 0), (4, 1))
            if not damaged:
                glow = GREEN_ACCENT if (c + r) % 4 else lit(GREEN_ACCENT, 0.4)
                sd.rect([wx + 0.7, wy + 0.8, wx + 3.6, wy + 2.4], fill=glow)
                sd.line([(wx + 0.7, wy + 0.8), (wx + 3.6, wy + 0.8)], fill=lit(GREEN_ACCENT, 0.55), width=0.4)
            elif not broke:
                sd.rect([wx + 0.7, wy + 0.8, wx + 3.6, wy + 2.4], fill=dim(GREEN_ACCENT, 0.72))
    # Service door with a recessed jamb and a gold threshold strip.
    dx0, dx1 = hx1 - 8, hx1 - 2
    sd.rect([dx0, eaves + 8, dx1, gold_y0], fill=dim(wall, 0.5))
    sd.rect([dx0 + 0.8, eaves + 9, dx1 - 0.8, gold_y0], fill=dim(wall, 0.72))
    sd.line([(dx0, eaves + 8), (dx1, eaves + 8)], fill=lit(wall, 0.3), width=0.5)
    sd.rect([dx0 + 0.8, gold_y0 - 1.2, dx1 - 0.8, gold_y0 - 0.6],
            fill=SUN_GOLD if not damaged else dim(SUN_GOLD, 0.6))
    if damaged:
        scorch(sd, [(hx0 + 13, eaves + 6, 3), (hx1 - 14, gold_y0 - 4, 2.5)])


def rotor_blur(sd, cx, cy, r, ry=None, tint=(0xA8, 0xA8, 0x9C), dashes=3, phase=0.0,
               stopped=False):
    """A spinning rotor, drawn opaque.

    The indexed pipeline's 1-bit alpha throws away anything translucent (see
    to_indexed), so the swept disc the first pass drew at alpha 70 was simply
    deleted -- and, worse, deleted the pixels under it (issue #72). The read
    has to be built from opaque marks instead: a thin dark swept ring with a
    few bright trailing dashes riding on it, which is the same solution the
    Wind Turbine Array's blades needed in issue #58."""
    ry = r if ry is None else ry
    n = 2 if stopped else dashes
    for i in range(n):
        a = math.radians(phase + i * 360 / n)
        ex, ey = cx + r * math.cos(a), cy - ry * math.sin(a)
        sd.line([(cx, cy), (ex, ey)], fill=dim(tint, 0.35) if stopped else tint, width=1.3)
        if stopped:
            sd.line([(cx, cy), (cx - r * math.cos(a), cy + ry * math.sin(a))],
                    fill=dim(tint, 0.35), width=1.3)
    if not stopped:
        # One trailing streak off the leading blade: the cue that says this is
        # turning rather than parked, and the only one that survives the 1-bit
        # alpha (a swept disc does not -- issue #72). One, not three, because
        # at four rotors per frame three each turns the sprite into lace.
        sd.arc([cx - r, cy - ry, cx + r, cy + ry], -phase - 46, -phase - 12,
               fill=dim(tint, 0.45), width=0.9)
    sd.ellipse([cx - 1.3, cy - 1.3, cx + 1.3, cy + 1.3], fill=LEGACY_GRAY_DARK)
    sd.px(cx - 0.5, cy - 0.5, lit(LEGACY_GRAY, 0.35))


def sgdrn_draw(sd, w=FAM23_W, h=FAM23_H, damaged=False):
    """Drone Bay: an open gantry over a landing apron with a drone parked on
    it -- Assembly's field-workshop answer to sgdra's hardened hangar.

    Volumetric pass (issue #48 batch 3): the near-invisible 1px A-frame line
    trusses became box-section masts and a cross beam with real thickness, and
    the apron became a raised slab whose *top* plane (Roof) is what the drone
    stands on, so the parked drone sits in the scene instead of floating in
    front of it."""
    ground_y0, ground_y1 = h - 12, h
    gold_y0, gold_y1 = ground_y0 - 8, ground_y0
    draw_ground_strip(sd, 2, w - 2, ground_y0, ground_y1, seed=3)
    draw_gold_band(sd, 6, w - 6, gold_y0, gold_y1)
    ax0, ax1, apron = 14, 52, 30
    steel = mix(LEGACY_GRAY, PANEL_BLUEBLACK, 0.18)
    contact_shadow(sd, (ax0 + ax1) / 2 + 2, gold_y0 + 0.7, (ax1 - ax0) / 2, 1.7, base=SUN_GOLD)
    # Gantry: two box-section masts and the beam they carry. Drawn before the
    # apron so the apron slab reads as standing in front of the legs.
    for mx in (10, 56):
        capped_box(sd, mx - 2, 12, mx + 2, gold_y0, steel, depth=2.2, edge=0.34)
        for ry in range(16, int(gold_y0) - 3, 6):
            sd.line([(mx - 1.6, ry), (mx + 1.6, ry)], fill=dim(steel, 0.4), width=0.4)
    if not damaged:
        capped_box(sd, 7, 9, 59, 13, steel, depth=2.2, edge=0.36)
        sd.line([(9, 10.6), (57, 10.6)], fill=lit(steel, 0.34), width=0.5)
    else:
        # Beam sheared through: the gantry is what fails first on a raid.
        capped_box(sd, 7, 9, 30, 13, steel, depth=2.2, edge=0.36)
        capped_box(sd, 37, 11, 59, 15, steel, depth=2.2, edge=0.36)
        sd.line([(30, 9.5), (35, 13)], fill=dim(steel, 0.5), width=0.7)
    # Knee braces from the masts down to the apron.
    for mx, bx in ((12, 21), (54, 45)):
        sd.line([(mx, 17), (bx, apron - 1)], fill=dim(steel, 0.2), width=1.0)
        sd.line([(mx - 0.3, 17), (bx - 0.3, apron - 1)], fill=lit(steel, 0.3), width=0.35)
    # Work lamp: the gold "powered" tell.
    lamp = SUN_GOLD if not damaged else dim(LEGACY_GRAY, 0.35)
    capped_box(sd, 21, 13, 25, 15, dim(steel, 0.25), depth=1.2, edge=0.3)
    sd.rect([21.5, 15, 24.5, 15.8], fill=lamp)
    # Landing apron: front edge, then the top plane the drone stands on.
    plane = Roof(ax0, apron, ax1, 6.0)
    plane.draw(sd, CONCRETE, edge=0.30)
    px_, py_ = plane.at(0.5, 0.5)
    sd.rect([ax0, apron, ax1, gold_y0], fill=dim(CONCRETE, 0.3))
    sd.line([(ax0, apron), (ax1, apron)], fill=lit(CONCRETE, 0.15), width=0.5)
    sd.line([(ax0, gold_y0 - 0.4), (ax1, gold_y0 - 0.4)], fill=dim(CONCRETE, 0.5), width=0.5)
    for i in range(1, 5):
        sd.line([(ax0 + (ax1 - ax0) * i / 5, apron + 0.6), (ax0 + (ax1 - ax0) * i / 5, gold_y0 - 1)],
                fill=dim(CONCRETE, 0.42), width=0.4)
    # Hazard striping along the apron lip -- the pad's "live" marking, and the
    # team-coloured element on an otherwise grey structure.
    stripe = SUN_GOLD if not damaged else dim(SUN_GOLD, 0.5)
    for i in range(6):
        sx = ax0 + 2 + i * 6
        sd.rect([sx, apron + 1.2, sx + 3, apron + 2.2], fill=stripe)
    # Parked drone, standing on the apron plane. Rotors are drawn *stopped* --
    # a parked airframe on a service pad isn't spinning, and at this scale two
    # clean blades read where a swept ring turns to noise.
    # Drawn to the same span the flyable drones now have (~15px): a service
    # pad whose parked airframe is bigger than the drone that lands on it
    # reads as a different, larger aircraft.
    dcx, dcy = px_, py_ - 1.6
    contact_shadow(sd, dcx + 1, dcy + 3.0, 7, 1.9, f=0.28)
    for k, (ox, oy) in enumerate(((-5.6, -2.1), (5.6, -2.1), (-5.6, 2.1), (5.6, 2.1))):
        sd.line([(dcx, dcy), (dcx + ox, dcy + oy)], fill=LEGACY_GRAY_DARK, width=1.0)
        sd.line([(dcx - 0.3, dcy - 0.3), (dcx + ox - 0.3, dcy + oy - 0.3)],
                fill=lit(LEGACY_GRAY_DARK, 0.35), width=0.4)
        if not (damaged and k == 1):
            rotor_blur(sd, dcx + ox, dcy + oy, 2.9, ry=1.5, phase=25 + 35 * k, stopped=True)
    sd.poly([(dcx, dcy - 3.6), (dcx + 4.2, dcy), (dcx, dcy + 3.6), (dcx - 4.2, dcy)],
            fill=GREEN_PRIMARY, outline=dim(GREEN_PRIMARY, 0.45))
    sd.poly([(dcx, dcy - 2.6), (dcx + 2.6, dcy - 0.4), (dcx - 2.6, dcy - 0.4)],
            fill=lit(GREEN_PRIMARY, 0.35))
    sd.ellipse([dcx - 1.1, dcy + 0.2, dcx + 1.1, dcy + 2.2], fill=PANEL_BLUEBLACK)
    sd.px(dcx, dcy - 3.0, lamp)
    if damaged:
        scorch(sd, [(45, apron + 3.5, 2.8), (19, apron + 2.5, 2.2)])


def _arch(cx, rx, ry, sy, n=20):
    """Points along a semicircular arch, left springing to right springing."""
    return [(cx - rx * math.cos(math.pi * i / n), sy - ry * math.sin(math.pi * i / n))
            for i in range(n + 1)]


def sgdra_draw(sd, w=FAM23_W, h=FAM23_H, damaged=False):
    """Aerial Fabrication Bay: a solar-roofed space-frame hangar standing over
    an open apron -- the Consortium's built, permanent answer to sgdrn's bare
    field gantry.

    History: this shipped first as a closed barrel vault with an arched door.
    The vault was legible but it was the wrong building -- a windowless masonry
    tunnel with a black mouth reads as a bunker or a kiln, and nothing about it
    said either *aircraft* or *solarpunk*; it was also the darkest mass in the
    roster sitting next to the second darkest (sgdai). Redrawn from the concept
    render (docs/concept-art/cameo-sources/desert_base2.png, the same subject
    its photographic cameo is cut from): a pale steel space frame carrying a
    field of collector panels, open on every side, with the airframes it builds
    parked underneath in plain sight.

    The read is carried by three things, in this order: the zigzag truss band
    along the front eave (nothing else in the roster has one, and it is what
    says lightweight space frame rather than wall), the row of slim columns
    with daylight between them, and the panel field on the roof plane tying it
    to the Solar Array family. Against sgdrn -- two heavy masts and a beam --
    the difference is a roof: this one is a building, that one is a rig."""
    ground_y0, ground_y1 = h - 12, h
    gold_y0, gold_y1 = ground_y0 - 8, ground_y0
    draw_ground_strip(sd, 2, w - 2, ground_y0, ground_y1, seed=4)
    draw_gold_band(sd, 6, w - 6, gold_y0, gold_y1)

    steel = mix(LEGACY_GRAY, (0xFF, 0xFF, 0xFF), 0.34)   # pale space-frame steel
    if damaged:
        steel = mix(steel, DAMAGE_SCORCH, 0.22)
    apron_y = 32.0
    eave_y, chord_h = 17.0, 5.0                          # truss band, front elevation
    rx0, rx1 = 4.0, 62.0
    contact_shadow(sd, w / 2 + 2, gold_y0 + 0.7, (rx1 - rx0) / 2 - 2, 1.7, base=SUN_GOLD)

    # --- apron ---------------------------------------------------------------
    # Drawn first: everything under the canopy stands on this plane.
    plane = Roof(7, apron_y, 59, 6.0)
    plane.draw(sd, CONCRETE, edge=0.28)
    sd.rect([7, apron_y, 59, gold_y0], fill=dim(CONCRETE, 0.3))
    sd.line([(7, apron_y), (59, apron_y)], fill=lit(CONCRETE, 0.15), width=0.5)
    sd.line([(7, gold_y0 - 0.4), (59, gold_y0 - 0.4)], fill=dim(CONCRETE, 0.5), width=0.5)
    stripe = SUN_GOLD if not damaged else dim(SUN_GOLD, 0.5)
    for i in range(7):
        sx = 10 + i * 7
        sd.rect([sx, apron_y + 1.2, sx + 3, apron_y + 2.2], fill=stripe)

    # --- rear workshop module -------------------------------------------------
    # The one solid volume, tucked under the back-left corner of the canopy, so
    # the fabrication bay has a workshop without the canopy becoming a wall.
    capped_box(sd, 10, 22, 27, apron_y - 0.5, mix(GREEN_PRIMARY, LEGACY_GRAY_DARK, 0.55),
               depth=2.6, edge=0.3)
    sd.rect([13, 25, 18, apron_y - 1], fill=dim(PANEL_BLUEBLACK, 0.25))     # roller door
    for dy_ in (26.4, 28.0, 29.6):
        sd.line([(13.2, dy_), (17.8, dy_)], fill=dim(LEGACY_GRAY, 0.5), width=0.4)
    sd.rect([20, 25.5, 25, 27.5], fill=dim(PANEL_BLUEBLACK, 0.1))           # lit window band
    sd.px(21, 26.4, lit(GREEN_ACCENT, 0.25) if not damaged else dim(LEGACY_GRAY, 0.35))

    # --- airframe on the apron ------------------------------------------------
    # Half-built: one boom still on the assembly trestle, which is the thing
    # that makes this a *fabrication* bay rather than a landing pad.
    dcx, dcy = plane.at(0.72, 0.45)
    dcy -= 1.5
    contact_shadow(sd, dcx + 1, dcy + 3.4, 7.5, 2.0, f=0.26)
    for k, (ox, oy) in enumerate(((-6.0, -2.4), (6.0, -2.4), (-6.0, 2.4), (6.0, 2.4))):
        if damaged and k == 1:
            continue
        sd.line([(dcx, dcy), (dcx + ox, dcy + oy)], fill=LEGACY_GRAY_DARK, width=1.1)
        rotor_blur(sd, dcx + ox, dcy + oy, 3.0, ry=1.7, phase=25 + 35 * k, stopped=True)
    sd.poly([(dcx, dcy - 3.6), (dcx + 4.2, dcy), (dcx, dcy + 3.6), (dcx - 4.2, dcy)],
            fill=GREEN_PRIMARY, outline=dim(GREEN_PRIMARY, 0.45))
    sd.poly([(dcx, dcy - 2.6), (dcx + 2.6, dcy - 0.4), (dcx - 2.6, dcy - 0.4)],
            fill=lit(GREEN_PRIMARY, 0.35))
    sd.px(dcx, dcy - 3.0, stripe)
    # Assembly trestle under the near boom, and the arm working on it.
    sd.rect([dcx - 7.4, dcy + 3.2, dcx - 4.2, dcy + 4.0], fill=dim(LEGACY_GRAY, 0.25))
    sd.line([(dcx - 7.0, dcy + 4.0), (dcx - 7.0, dcy + 6.4)], fill=LEGACY_GRAY_DARK, width=0.7)
    sd.line([(dcx - 4.6, dcy + 4.0), (dcx - 4.6, dcy + 6.4)], fill=LEGACY_GRAY_DARK, width=0.7)

    # --- columns --------------------------------------------------------------
    # Slim, and evenly spaced with real daylight between them: the gaps are what
    # make the canopy read as standing over the apron rather than enclosing it.
    for i in range(6):
        cxp = 7.0 + i * 10.0
        bent = damaged and i == 4
        top_x = cxp + (1.6 if bent else 0)
        sd.line([(top_x, eave_y + chord_h), (cxp, apron_y + 1.5)], fill=dim(steel, 0.32), width=1.3)
        sd.line([(top_x - 0.5, eave_y + chord_h), (cxp - 0.5, apron_y + 1.5)],
                fill=lit(steel, 0.25), width=0.5)
        sd.rect([cxp - 1.6, apron_y + 1.0, cxp + 1.6, apron_y + 2.0], fill=dim(steel, 0.42))

    # --- roof: panel field on the receding plane ------------------------------
    roof = Roof(rx0, eave_y, rx1, 9.0)
    sd.poly(roof.quad(), fill=dim(steel, 0.5))
    for i in range(5):
        u0, u1 = 0.02 + i * 0.196, 0.02 + i * 0.196 + 0.176
        for v0, v1 in ((0.08, 0.48), (0.52, 0.92)):
            if damaged and i == 3 and v0 > 0.5:
                continue                                  # panel blown off the frame
            quad = [roof.at(u0, v0), roof.at(u1, v0), roof.at(u1, v1), roof.at(u0, v1)]
            sd.poly(quad, fill=lit(PANEL_BLUEBLACK, 0.04 + 0.24 * v0))
            sd.line([quad[3], quad[2]], fill=lit(PANEL_BLUEBLACK, 0.55), width=0.5)
            sd.line([quad[0], quad[3]], fill=dim(PANEL_BLUEBLACK, 0.3), width=0.4)
    # Ridge purlin along the back of the plane, and the rafters under the panels.
    sd.line([roof.at(0, 1), roof.at(1, 1)], fill=lit(steel, 0.3), width=0.8)
    for i in range(1, 5):
        u = i / 5
        sd.line([roof.at(u, 0.0), roof.at(u, 1.0)], fill=dim(steel, 0.25), width=0.5)

    # --- front truss band -----------------------------------------------------
    # Top and bottom chords with a zigzag web between them. This is the shape
    # doing the identifying work, so it is drawn last and lit hardest.
    sd.line([(rx0, eave_y), (rx1, eave_y)], fill=lit(steel, 0.35), width=1.2)
    sd.line([(rx0, eave_y + chord_h), (rx1, eave_y + chord_h)], fill=dim(steel, 0.3), width=1.2)
    bays = 8
    for i in range(bays):
        x0_ = rx0 + (rx1 - rx0) * i / bays
        x1_ = rx0 + (rx1 - rx0) * (i + 1) / bays
        if damaged and i == 5:
            continue                                      # web snapped over the hit column
        # Filled sawtooth rather than drawn diagonals: a 5px-deep band of 0.9px
        # lines comes back from the 4x downscale as a chain of soft loops, where
        # solid triangles keep hard edges and leave the inverted triangles
        # between them as real holes -- which is what a truss looks like.
        top, bot = (eave_y + 0.9, eave_y + chord_h - 0.6)
        sd.poly([(x0_ + 0.4, bot), ((x0_ + x1_) / 2, top), (x1_ - 0.4, bot)],
                fill=steel if i % 2 == 0 else dim(steel, 0.16))
    # Approach beacon on the eave, over the open end.
    sd.line([(rx1 - 3, eave_y), (rx1 - 3, eave_y - 4)], fill=dim(steel, 0.35), width=0.7)
    sd.px(rx1 - 3, eave_y - 5, GREEN_ACCENT if not damaged else dim(LEGACY_GRAY, 0.3))

    if damaged:
        # The hit bay: torn frame over the bent column, and the panel it dropped.
        sd.line([(rx0 + 40, eave_y + 1), (rx0 + 44, eave_y + chord_h + 2)], fill=RUST, width=0.6)
        sd.poly([(45, apron_y + 3), (52, apron_y + 1.5), (52.5, apron_y + 3.5), (45.5, apron_y + 5)],
                fill=dim(PANEL_BLUEBLACK, 0.25))
        scorch(sd, [(48, apron_y + 4, 3.0), (30, eave_y + chord_h + 3, 2.2)])


def sgshl_draw(sd, w=SGSHL_W, h=SGSHL_H, damaged=False):
    """Resilience Shelter: a hardened dome banked into an earth berm, with a
    sandbagged entry throat -- ART_DIRECTION.md's "not utopian" guardrail.

    Volumetric pass (issue #48 batch 3): dome3d's three stacked blobs are
    replaced by a real sphere ramp (sphere()) with projected meridian ribs, and
    the dome now meets the ground through a berm and a stepped entry throat
    rather than sitting on the pad like a dropped bead."""
    ground_y0, ground_y1 = h - 10, h
    draw_ground_strip(sd, 2, w - 2, ground_y0, ground_y1, seed=5)
    cx = w / 2
    dx0, dx1 = 7, w - 7
    dy0, dy1 = 5, ground_y0 + 5
    contact_shadow(sd, cx + 3, ground_y0 + 1.5, (dx1 - dx0) / 2 + 1, 2.6)
    sphere(sd, dx0, dy0, dx1, dy1, GREEN_PRIMARY)
    # Meridian ribs: a sphere's meridians project to ellipses sharing its
    # vertical extent, so each is just a narrower top-half arc.
    for k in (0.58, 0.92):
        rw = (dx1 - dx0) / 2 * k
        sd.arc([cx - rw, dy0, cx + rw, dy1], 190, 350, fill=dim(GREEN_PRIMARY, 0.15), width=0.5)
    # Latitude seam.
    sd.arc([dx0 + 3, dy0 + 5, dx1 - 3, dy1 - 3], 190, 350, fill=dim(GREEN_PRIMARY, 0.15), width=0.5)
    if damaged:
        # Split panel: the rib cage under the skin shows through.
        sd.poly([(cx + 9, dy0 + 7), (cx + 17, dy0 + 10), (cx + 15, dy0 + 18), (cx + 8, dy0 + 15)],
                fill=dim(GREEN_PRIMARY, 0.72))
        for i in range(3):
            sd.line([(cx + 10 + i * 2.4, dy0 + 8.5), (cx + 9.4 + i * 2.4, dy0 + 16)],
                    fill=dim(LEGACY_GRAY, 0.3), width=0.4)
    # Earth berm banked against the base, with grass catching the top edge.
    sd.arc([dx0 - 1, ground_y0 - 11, dx1 + 1, ground_y0 + 7], 192, 348, fill=DIRT, width=3.2)
    sd.arc([dx0 - 1, ground_y0 - 11.8, dx1 + 1, ground_y0 + 6.2], 196, 344,
           fill=lit(GRASS, 0.1), width=0.8)
    # Entry throat: a stepped concrete box projecting from the dome, with a
    # recessed airlock door and a lit lintel.
    tx0, tx1 = cx - 7, cx + 7
    capped_box(sd, tx0, ground_y0 - 11, tx1, ground_y0 + 1, CONCRETE, depth=2.4, edge=0.3)
    sd.rect([tx0 + 2, ground_y0 - 8, tx1 - 2, ground_y0 + 1], fill=dim(PANEL_BLUEBLACK, 0.15))
    sd.rect([tx0 + 3, ground_y0 - 7, tx1 - 3, ground_y0 + 1], fill=dim(PANEL_BLUEBLACK, 0.45))
    sd.line([(tx0 + 2, ground_y0 - 8.4), (tx1 - 2, ground_y0 - 8.4)], fill=lit(CONCRETE, 0.35), width=0.6)
    sd.rect([tx0 + 3.4, ground_y0 - 6.6, tx1 - 3.4, ground_y0 - 6],
            fill=SUN_GOLD if not damaged else dim(SUN_GOLD, 0.55))
    # Filtration/vent stack rising beside the dome, planted on the berm.
    vx, vy = dx1 - 3, ground_y0 - 17
    vcyl(sd, vx - 2.4, vy, vx + 2.4, ground_y0 - 1, mix(LEGACY_GRAY, GREEN_PRIMARY, 0.25), bands=5)
    sd.ellipse([vx - 2.4, vy - 1.8, vx + 2.4, vy + 1.8], fill=lit(LEGACY_GRAY, 0.18))
    sd.ellipse([vx - 1.4, vy - 1.1, vx + 0.7, vy + 0.6], fill=dim(PANEL_BLUEBLACK, 0.1))
    sd.line([(vx - 2.4, vy + 6), (vx + 2.4, vy + 6)], fill=dim(LEGACY_GRAY, 0.4), width=0.5)
    # Apex beacon.
    sd.ellipse([cx - 2.6, dy0 + 0.4, cx + 2.6, dy0 + 5],
               fill=SUN_GOLD if not damaged else dim(SUN_GOLD, 0.5))
    sd.ellipse([cx - 1.6, dy0 + 1.2, cx + 0.4, dy0 + 3],
               fill=lit(SUN_GOLD, 0.45) if not damaged else dim(SUN_GOLD, 0.35))
    # Sandbag revetment flanking the throat: two-tone bags with lit tops.
    bag_w = 6
    for i, bx in enumerate(list(range(5, int(tx0) - bag_w, bag_w + 1))
                           + list(range(int(tx1) + 2, w - 6 - bag_w, bag_w + 1))):
        if damaged and i == 1:
            continue
        by = ground_y0 - 3 + (i % 2)
        sd.ellipse([bx, by, bx + bag_w, by + 5], fill=DIRT)
        sd.arc([bx, by, bx + bag_w, by + 5], 180, 320, fill=lit(DIRT, 0.3), width=0.7)
        sd.arc([bx, by, bx + bag_w, by + 5], 20, 160, fill=dim(DIRT, 0.35), width=0.6)
    if damaged:
        scorch(sd, [(cx + 12, dy0 + 20, 3.2), (cx - 21, ground_y0 - 8, 2.5)])


def sgsns_draw(sd, w=SG1x1_W, h=SG1x1_H, damaged=False):
    """Sensor Array: a parabolic dish on a mast, over its equipment cabinet.

    Volumetric pass (issue #48 batch 3): the three 1px tripod lines become a
    tapering cylindrical mast on a plinth with a yoke, and the dish becomes a
    genuine concave bowl -- lit on the *lower-right* of its inner surface,
    which is what a dish facing up-and-left does under this key light, and the
    cue that tells a bowl apart from a disc at 20px across. This is also the
    sprite issue #72 was reproduced on: its pad used to have a lens-shaped hole
    punched through it by the old translucent contact_shadow."""
    ground_y0, ground_y1 = h - 8, h
    draw_ground_strip(sd, 2, w - 2, ground_y0, ground_y1, seed=6)
    cx = w // 2
    steel = mix(LEGACY_GRAY, PANEL_BLUEBLACK, 0.2)
    contact_shadow(sd, cx + 2, ground_y0 + 0.5, 11, 2.2)
    # Equipment cabinet beside the mast, with a status light.
    capped_box(sd, 5, ground_y0 - 6, 13, ground_y0, steel, depth=1.8, edge=0.32)
    for i in range(3):
        sd.line([(6.4, ground_y0 - 4.6 + i * 1.4), (11.6, ground_y0 - 4.6 + i * 1.4)],
                fill=dim(steel, 0.42), width=0.4)
    sd.px(11.4, ground_y0 - 5.4, GREEN_ACCENT if not damaged else dim(GREEN_ACCENT, 0.5))
    # Concrete plinth and tapering mast.
    capped_box(sd, cx - 5, ground_y0 - 3, cx + 5, ground_y0, CONCRETE, depth=1.6, edge=0.28)
    mast_top = 13
    bands = 5
    for i in range(bands):
        t0, t1 = i / bands, (i + 1) / bands
        c = (t0 + t1) / 2
        b = 1.0 - abs(c - 0.35) * 2.0
        col = lit(steel, 0.3 * max(0.0, b)) if b > 0 else dim(steel, 0.3 * min(1.0, -b + 0.3))
        sd.poly([(cx - 2.4 + 4.8 * t0, ground_y0 - 2), (cx - 2.4 + 4.8 * t1, ground_y0 - 2),
                 (cx - 1.5 + 3.0 * t1, mast_top), (cx - 1.5 + 3.0 * t0, mast_top)], fill=col)
    sd.line([(cx - 2.1, ground_y0 - 11), (cx + 2.1, ground_y0 - 11)], fill=dim(steel, 0.4), width=0.4)
    # Conduit collar: the "grid-live" tell, and the mast's team-coloured band.
    collar = SUN_GOLD if not damaged else dim(SUN_GOLD, 0.55)
    sd.rect([cx - 2.3, ground_y0 - 7, cx + 2.3, ground_y0 - 5.4], fill=collar)
    sd.line([(cx - 2.3, ground_y0 - 7), (cx + 2.3, ground_y0 - 7)], fill=lit(SUN_GOLD, 0.4), width=0.4)
    sd.rect([5.8, ground_y0 - 1.6, 12.2, ground_y0 - 0.8], fill=collar)
    # Yoke carrying the dish off the mast head.
    sd.line([(cx - 1, mast_top + 1), (cx - 5, mast_top - 3)], fill=steel, width=1.0)
    sd.line([(cx + 1, mast_top + 1), (cx + 5, mast_top - 3)], fill=dim(steel, 0.2), width=1.0)
    # Dish. Outer rim, then the bowl as nested ellipses brightening toward the
    # lower-right inner face (concave = the highlight sits opposite the light).
    dcx, dcy, drx, dry = cx, 10.0, 10.5, 7.5
    sd.ellipse([dcx - drx, dcy - dry, dcx + drx, dcy + dry], fill=dim(steel, 0.45))
    steps = 7
    for i in range(steps):
        t = i / (steps - 1)
        a = 1 - t * 0.9
        fx, fy = dcx + drx * 0.24, dcy + dry * 0.26
        col = dim(PANEL_BLUEBLACK, 0.35 * (1 - t)) if t < 0.45 else lit(PANEL_BLUEBLACK, 0.34 * (t - 0.45) / 0.55)
        sd.ellipse([fx + (dcx - drx + 1.2 - fx) * a, fy + (dcy - dry + 1.0 - fy) * a,
                    fx + (dcx + drx - 1.2 - fx) * a, fy + (dcy + dry - 1.0 - fy) * a], fill=col)
    # Rim lip, brightest where it faces the light.
    sd.arc([dcx - drx, dcy - dry, dcx + drx, dcy + dry], 170, 320, fill=lit(steel, 0.4), width=0.7)
    sd.arc([dcx - drx, dcy - dry, dcx + drx, dcy + dry], 20, 150, fill=dim(steel, 0.3), width=0.6)
    ring = GREEN_ACCENT if not damaged else dim(GREEN_ACCENT, 0.5)
    sd.arc([dcx - 6.4, dcy - 4.6, dcx + 6.4, dcy + 4.6], 200, 340, fill=ring, width=0.6)
    sd.arc([dcx - 3.4, dcy - 2.4, dcx + 3.4, dcy + 2.4], 200, 340, fill=ring, width=0.5)
    if damaged:
        # A bite out of the rim: the state reads from the outline, not decals.
        sd.poly([(dcx + 3, dcy - dry - 0.5), (dcx + 9, dcy - dry + 2.5),
                 (dcx + 7, dcy - 1), (dcx + 2.5, dcy - 3)], fill=dim(steel, 0.62))
    # Feed boom and horn, on the remap ramp.
    sd.line([(dcx, dcy), (dcx - 4.5, dcy - 5.5)], fill=lit(steel, 0.25), width=0.6)
    sd.ellipse([dcx - 6, dcy - 7.2, dcx - 3.4, dcy - 4.6],
               fill=SUN_GOLD if not damaged else dim(SUN_GOLD, 0.5))
    if damaged:
        scorch(sd, [(cx + 9, ground_y0 + 2.5, 2.2), (7, ground_y0 + 3, 1.6)])


_REL_TANK = mix(LEGACY_GRAY, PANEL_BLUEBLACK, 0.22)   # transformer tank
_REL_BUSHING_X = (16, 21, 26)                         # bushing stack centres
_REL_BAND_X0, _REL_BAND_X1 = 8, 31                    # conduit band span
_REL_BAND_Y0, _REL_BAND_Y1 = 25, 27
_REL_TERM_Y = 5                                       # bushing terminal centre row


def _sgrel_accents(damaged):
    """The energized parts as (x, y, colour) *native* pixels.

    Same re-stamp the Battery Bank needs (see _vlt_accents), and for the same
    reason -- but it bites harder here. draw_gold_band works untouched on the
    2x3 buildings because their band is 8px tall, so its interior rows survive
    the 4x LANCZOS downscale as pure SUN_GOLD and land on the 80-95 player-remap
    ramp. On this 1x1 plinth the band is only 3px tall, so every row is an edge
    row, every row gets blended with the concrete above and below it, and the
    whole band came back on *fixed* palette entries -- a relay whose grid
    conduit ignored its owner's colour.
    """
    live = not damaged
    core = SUN_GOLD if live else dim(SUN_GOLD, 0.4)
    hi = lit(SUN_GOLD, 0.35) if live else dim(SUN_GOLD, 0.25)
    out = []
    for x in range(_REL_BAND_X0, _REL_BAND_X1 + 1):
        out.append((x, _REL_BAND_Y0, hi))
        for y in range(_REL_BAND_Y0 + 1, _REL_BAND_Y1 + 1):
            out.append((x, y, core))
    for i, bx in enumerate(_REL_BUSHING_X):
        if damaged and i == 1:      # snapped bushing carries no terminal
            continue
        for dx in (-1, 0, 1):
            out.append((bx + dx, _REL_TERM_Y, core))
            out.append((bx + dx, _REL_TERM_Y - 1, hi if dx < 1 else core))
    return out


def sgrel_frame(damaged=False):
    """One Smart Grid Relay frame with its energized pixels re-stamped at
    native resolution on top of the supersampled render."""
    img = render(sgrel_draw, SG1x1_W, SG1x1_H, damaged=damaged)
    px = img.load()
    for x, y, col in _sgrel_accents(damaged):
        px[x, y] = tuple(col[:3]) + (255,)
    return img


def sgrel_draw(sd, w=SG1x1_W, h=SG1x1_H, damaged=False):
    """Smart Grid Relay: a pad-mounted step-down transformer.

    Redrawn for the issue #70 wrong-mechanic check. The sprite this replaces
    was a relay pylon with radiating distribution lines -- it depicted the
    cluster-pooling fantasy that docs/BUILDINGS.md records as *explicitly
    descoped*, while the trait set (mods/sungrid/rules/structures.yaml) is a
    flat +60 Power source and nothing else. A pad transformer is what a small
    local supply actually looks like, and it is the object the concept renders
    in docs/concept-art/cameo-sources/ put on exactly this footprint (the
    bushing-topped tank on a concrete pad in desert-base.png).
    """
    live = not damaged
    ground_y0, ground_y1 = h - 8, h
    draw_ground_strip(sd, 2, w - 2, ground_y0, ground_y1, seed=7)

    tank = _REL_TANK if live else mix(_REL_TANK, DAMAGE_SCORCH, 0.32)
    accent = SUN_GOLD if live else dim(SUN_GOLD, 0.4)
    # Painted (opaque) contact shadow, not contact_shadow(): that helper draws
    # at alpha 70, which the indexed pipeline's 1-bit alpha drops entirely --
    # so it not only never shows a shadow (issue #65) but punches a transparent
    # lens through whatever it covers. See docs/BACKLOG.md for the roster-wide
    # case; here it would have holed the pad this building stands on.
    sd.ellipse([w // 2 - 13, ground_y0 - 1, w // 2 + 13, ground_y0 + 3], fill=dim(CONCRETE, 0.25))

    # Concrete plinth with the shared gold conduit band signalling grid tie-in.
    sd.rect([6, 23, 33, ground_y0], fill=CONCRETE)
    sd.line([(6, 23), (33, 23)], fill=lit(CONCRETE, 0.22), width=0.5)
    draw_gold_band(sd, 8, 31, 25, 27)

    # Radiator fin bank jutting out to the left -- the transformer's signature
    # profile, and what keeps this silhouette clear of the Battery Bank's
    # canister rank on the same 1x1 footprint.
    sd.rect([5, 14, 13, 24], fill=dim(tank, 0.5))
    for i in range(4):
        fx = 5.4 + i * 1.9
        sd.rect([fx, 15, fx + 1.1, 23.4], fill=lit(tank, 0.18))
        sd.line([(fx, 15), (fx, 23.4)], fill=lit(tank, 0.42), width=0.4)
    # Header rails top and bottom tie the fins together as one radiator bank.
    sd.line([(5, 14.4), (13, 14.4)], fill=lit(tank, 0.34), width=0.7)
    sd.line([(5, 24), (13, 24)], fill=dim(tank, 0.3), width=0.6)

    # Main tank.
    capped_box(sd, 12, 13, 30, 24, tank, depth=3.0, edge=0.32)
    sd.rect([24, 16, 28, 20], fill=dim(tank, 0.4))          # rating plate
    sd.line([(24, 16), (28, 16)], fill=lit(tank, 0.25), width=0.4)
    sd.px(14, 15, lit(GREEN_ACCENT, 0.3) if live else dim(LEGACY_GRAY, 0.35))

    # Bushings: stacked insulator sheds with an energized terminal on top. The
    # terminals are drawn in SUN_GOLD so they land on the player-remap ramp.
    for i, bx in enumerate(_REL_BUSHING_X):
        snapped = damaged and i == 1
        top = 9 if snapped else 5
        sd.line([(bx, 13), (bx, top)], fill=dim(LEGACY_GRAY_DARK, 0.05), width=1.0)
        sheds = 2 if snapped else 3
        for k in range(sheds):
            sy = 12 - k * 2.4
            sd.ellipse([bx - 2.2, sy - 1, bx + 2.2, sy + 1], fill=RUST if live else dim(RUST, 0.3))
            sd.line([(bx - 2.2, sy - 0.6), (bx + 2.2, sy - 0.6)], fill=lit(RUST, 0.25), width=0.4)
        if snapped:
            # Sheared stub, so the damage reads from the outline alone.
            sd.line([(bx - 1.5, top), (bx + 1.5, top - 1)], fill=LEGACY_GRAY_DARK, width=0.6)
        else:
            sd.ellipse([bx - 1.6, top - 1.6, bx + 1.6, top + 1.6], fill=accent)
            sd.ellipse([bx - 1, top - 1, bx + 0.3, top + 0.3],
                       fill=lit(SUN_GOLD, 0.45) if live else dim(SUN_GOLD, 0.2))
    # HV jumper looping between the two outer terminals, clear of the middle one.
    if not damaged:
        sd.arc([_REL_BUSHING_X[0] - 1, 1, _REL_BUSHING_X[2] + 1, 9], 200, 340, fill=dim(SUN_GOLD, 0.2), width=0.5)

    if damaged:
        # Oil weeping from the split tank down onto the pad.
        sd.line([(20, 20), (20, 24)], fill=dim(DAMAGE_SCORCH, 0.0), width=0.8)
        sd.ellipse([17, 23.5, 24, 25.5], fill=DAMAGE_SCORCH + (200,))
        scorch(sd, [(15, 17, 1.9), (27, 21, 1.5)])


# ---------------------------------------------------------------------------
# Battery Bank (SILO / the Grid Reserve Vault).
#
# The mode's signature building had never been drawn: it still rendered stock
# RA's silo2.shp, a rusty open-topped ore bin, which reads as "ore storage"
# in a mode whose whole point is that the Vault banks *Credits* as grid
# capacity (docs/GAME_MODES.md). Decoding silo2.shp here (24x24, 9 fill stages
# + 9 damaged, a baked ShadowIndex-4 blob, and a fill drawn in indices 83-91 --
# i.e. inside the 80-95 player-remap ramp, so stock's fill level is already
# team-coloured) gives the constraints this has to hit:
#
#   - WithResourceLevelSpriteBody picks a frame from `stages` by fill fraction,
#     so all 9 charge levels must be individually legible, and so must all 9
#     *damaged* ones -- a damaged Vault still holds Reserve, and hiding the
#     level while it is under attack would hide exactly the information Core
#     Rule 4's "Lockdown breaks when Reserve drops below target" turns on.
#     (This is also the trap issue #40 fell into: 9 identical damaged frames.)
#   - The charge accent is drawn in SUN_GOLD, which _index_for maps onto the
#     remap ramp, so charge reads in the owner's colour the way stock's does.
#
# Form is the containerised battery energy storage system from the concept
# renders in docs/concept-art/cameo-sources/: an olive switchgear/inverter
# cabinet with roof louvres behind a front rank of silver cell canisters. The
# level is double-coded -- a discrete 8-segment charge readout on the cabinet
# (one segment per stage, so the exact stage is countable) plus a continuous
# bottom-up fill in each canister's sight window (readable at RTS zoom, where
# 2px LEDs are not).
# ---------------------------------------------------------------------------

SGVLT_STAGES = 9                     # matches `stages:` Length in sequences
SGVLT_SEGMENTS = SGVLT_STAGES - 1    # stage n lights n of them (0 = empty)
_VLT_SKID = mix(GREEN_PRIMARY, LEGACY_GRAY_DARK, 0.55)  # cabinet shell
_VLT_CAN = lit(LEGACY_GRAY, 0.30)                       # cell canister
_VLT_CANS = ((8, 14), (16, 22), (24, 30))               # x spans, integer pixels
_VLT_CAN_TOP, _VLT_CAN_BOT = 14, 27


_VLT_BAR_X0, _VLT_BAR_Y0, _VLT_BAR_Y1 = 8, 9, 11   # gauge origin, 3px segment pitch


def _vlt_charge_px(sd, x0, x1, y0, y1, col):
    """Fill whole native pixels only (sd.px draws an exact SS x SS block)."""
    for y in range(int(y0), int(y1) + 1):
        for x in range(int(x0), int(x1) + 1):
            sd.px(x, y, col)


def _vlt_accents(damaged, charge):
    """The charge readout as (x, y, colour) *native* pixels.

    SUN_GOLD is what _index_for routes onto the 80-95 player-remap ramp, so
    these pixels are what make the stored level render in the owner's colour.
    They have to be re-stamped after the 4x LANCZOS downscale: the kernel
    reaches past a pixel's own block, so even a pixel-aligned gold segment
    picks up enough of the dark bezel beside it to land back on a *fixed*
    palette entry -- which showed up as a gauge whose segments alternated
    team-coloured and off-palette gold along its length.
    """
    live = not damaged
    on = SUN_GOLD if live else dim(SUN_GOLD, 0.4)
    off = dim(LEGACY_GRAY_DARK, 0.15)
    out = []
    for i in range(SGVLT_SEGMENTS):
        col = on if i < charge else off
        for x in (_VLT_BAR_X0 + i * 3, _VLT_BAR_X0 + i * 3 + 1):
            for y in range(_VLT_BAR_Y0, _VLT_BAR_Y1 + 1):
                out.append((x, y, col))
    wy1 = _VLT_CAN_BOT - 2
    for cx0, _ in _VLT_CANS:
        for k in range(charge):
            col = lit(SUN_GOLD, 0.4) if (live and k == charge - 1) else on
            for x in range(cx0 + 2, cx0 + 5):
                out.append((x, wy1 - k, col))
    return out


def sgvlt_frame(damaged=False, charge=SGVLT_STAGES - 1):
    """One Battery Bank frame, with the charge readout re-stamped at native
    resolution on top of the supersampled render (see _vlt_accents)."""
    img = render(sgvlt_draw, SG1x1_W, SG1x1_H, damaged=damaged, charge=charge)
    px = img.load()
    for x, y, col in _vlt_accents(damaged, charge):
        px[x, y] = tuple(col[:3]) + (255,)
    return img


def sgvlt_draw(sd, w=SG1x1_W, h=SG1x1_H, damaged=False, charge=SGVLT_STAGES - 1):
    """Battery Bank at charge level `charge` (0..SGVLT_STAGES-1)."""
    live = not damaged
    ground_y0, ground_y1 = h - 8, h
    draw_ground_strip(sd, 2, w - 2, ground_y0, ground_y1, seed=9)

    # --- switchgear cabinet (rear mass) --------------------------------------
    cab_x0, cab_x1, cab_y0, cab_y1 = 7, 31, 6, 20
    depth = 3.0
    skid = _VLT_SKID if live else mix(_VLT_SKID, DAMAGE_SCORCH, 0.3)
    capped_box(sd, cab_x0, cab_y0, cab_x1, cab_y1, skid, depth=depth, edge=0.36)
    # Roof louvres, following the receding top face.
    for t in (0.28, 0.5, 0.72, 0.94):
        ly = cab_y0 - depth * 0.6 * t
        sd.line([(cab_x0 + depth * t + 2, ly), (cab_x1 + depth * t - 3, ly)],
                fill=dim(skid, 0.42), width=0.4)
    # Access door seam and a rating plate on the front face.
    sd.line([(cab_x1 - 4, cab_y0 + 2), (cab_x1 - 4, cab_y1 - 1)], fill=dim(skid, 0.45), width=0.5)
    # Standby pip: stays lit at zero charge so an empty bank still reads as
    # powered rather than destroyed.
    sd.px(cab_x0 + 2, cab_y0 + 2, lit(GREEN_ACCENT, 0.3) if live else dim(LEGACY_GRAY, 0.35))
    # Busbar trunk down to the pad, the shared grid-connection grammar.
    sd.line([(cab_x1 - 2, cab_y1 - 2), (34, ground_y0 + 1)], fill=POLE_DARK, width=1.0)

    # --- charge readout: one segment per stage --------------------------------
    # Dimmed rather than dark when damaged: the readout survives, so all nine
    # damaged frames stay distinguishable from each other.
    on_col = SUN_GOLD if live else dim(SUN_GOLD, 0.4)
    off_col = dim(LEGACY_GRAY_DARK, 0.15)
    bar_x0, bar_y0, bar_y1 = _VLT_BAR_X0, _VLT_BAR_Y0, _VLT_BAR_Y1
    sd.rect([bar_x0 - 2, bar_y0 - 1, bar_x0 + SGVLT_SEGMENTS * 3, bar_y1 + 1],
            fill=mix(PANEL_BLUEBLACK, skid, 0.25))
    sd.line([(bar_x0 - 2, bar_y0 - 1), (bar_x0 + SGVLT_SEGMENTS * 3, bar_y0 - 1)],
            fill=lit(skid, 0.3), width=0.5)
    for i in range(SGVLT_SEGMENTS):
        sx = bar_x0 + i * 3
        _vlt_charge_px(sd, sx, sx + 1, bar_y0, bar_y1, on_col if i < charge else off_col)

    # --- cell canisters (front rank) ------------------------------------------
    # Painted contact shadow rather than a SHADOW_IDX one: the pad the whole
    # roster stands on is opaque, so a real cast shadow would only ever show
    # through the gaps *between* the cans, which reads as holes in the sprite.
    can_top, can_bot = _VLT_CAN_TOP, _VLT_CAN_BOT
    sd.ellipse([6, can_bot - 0.5, 34, can_bot + 3], fill=dim(CONCRETE, 0.25))
    can = _VLT_CAN if live else mix(_VLT_CAN, DAMAGE_SCORCH, 0.22)
    for i, (cx0, cx1) in enumerate(_VLT_CANS):
        # Anchor foot, then the can body, then a domed terminal cap.
        sd.rect([cx0 - 1, can_bot - 1, cx1 + 1, can_bot + 1], fill=dim(CONCRETE, 0.05))
        vcyl(sd, cx0, can_top, cx1, can_bot, can, bands=7)
        sd.ellipse([cx0, can_top - 2.5, cx1, can_top + 2.5], fill=lit(can, 0.16))
        sd.ellipse([cx0 + 1, can_top - 2, cx1 - 2.4, can_top + 0.4], fill=lit(can, 0.3))
        # Retaining straps break up the white cylinder mass.
        for sy in (can_top + 2, can_top + 9):
            sd.line([(cx0, sy), (cx1, sy)], fill=dim(can, 0.4), width=0.5)
        # Terminal post and its lead back into the cabinet.
        sd.px(cx0 + 2, can_top - 3, POLE_DARK)
        sd.line([(cx0 + 2.5, can_top - 3), (cx0 + 2.5, can_top - 5)], fill=POLE_DARK, width=0.6)
        # Sight window: dark slot filled bottom-up with the stored charge, on
        # whole pixels so every stage moves the fill by exactly one row.
        wx0, wx1 = cx0 + 2, cx0 + 4
        wy0, wy1 = can_top + 4, can_bot - 2      # 8 rows: one per lit stage
        _vlt_charge_px(sd, wx0 - 1, wx1 + 1, wy0 - 1, wy1 + 1, mix(PANEL_BLUEBLACK, can, 0.18))
        if charge:
            _vlt_charge_px(sd, wx0, wx1, wy1 - charge + 1, wy1, on_col)
            _vlt_charge_px(sd, wx0, wx1, wy1 - charge + 1, wy1 - charge + 1,
                           lit(SUN_GOLD, 0.45) if live else SUN_GOLD)

    if damaged:
        # Split can seam, rust, and scorch across the cabinet face.
        sd.line([(24, can_top + 2), (26, can_bot - 2)], fill=RUST, width=0.6)
        scorch(sd, [(13, cab_y0 + 7, 3.5), (30, can_bot - 6, 2.5)])


# ---------------------------------------------------------------------------
# Recycling Depot (RCYD).
#
# Second building found by the issue #70 check ("does this sprite describe what
# the building actually *does*?", docs/ART_DIRECTION.md). RCYD still rendered
# stock RA's oilb.shp -- an oil derrick, which says "pumps crude out of the
# ground" -- for a building whose rules (mods/sungrid/rules/structures.yaml)
# make it a *Scrap refinery*: Refinery + DockHost:Unload + StoresPlayerResources
# + FreeActor: SGHAU + a baseline CashTrickler. Issue #47 gave it a dedicated
# photographic cameo but deliberately left the world sprite on the derrick, so
# this is the last Sungrid-original-role building on borrowed art.
#
# Like the Vault, its stored level is real state the sprite has to carry, so it
# gets WithResourceLevelSpriteBody and the same double-coded readout: a discrete
# segment gauge (countable, exact) plus a continuous scrap heap in the tipping
# bay (what actually reads at RTS zoom). Damaged stages keep the readout dimmed
# rather than dark, so all nine stay distinguishable from each other -- issue
# #40's identical-damaged-frames trap.
#
# Silhouette (revised): an open-sided *bay*, not a cabinet. The first pass put
# the tipping bay in the lower third of a tall closed hall with a segment gauge
# across its face, which is the Battery Bank's own composition -- a box with a
# lit readout on it -- and the player read it as another battery. What separates
# a recycling bay from any other block in the roster is that you can see
# *through* it: a wide flat canopy standing on slim posts, open at the front and
# both ends, with daylight between the roof and the pile underneath. The mass
# that is left (shredder, chute, stack) is pushed to one end so the canopy stays
# an outline of air and posts rather than a wall. Damage lands in that
# silhouette (the near canopy corner shears off its post and sags) rather than
# only in decals, per issue #65.
# ---------------------------------------------------------------------------

RCYD_STAGES = 9                      # matches `stages:` Length in sequences
RCYD_SEGMENTS = RCYD_STAGES - 1      # stage n lights n of them (0 = empty)
_RCY_HALL = mix(LEGACY_GRAY, PANEL_BLUEBLACK, 0.30)     # canopy/shredder shell
_RCY_BAR_X0, _RCY_BAR_Y0, _RCY_BAR_Y1 = 5, 9, 11        # gauge origin, 3px pitch
_RCY_BAY_X0, _RCY_BAY_X1 = 5, 27                        # heap interior columns
_RCY_BAY_FLOOR = 27                                     # heap bottom row
_RCY_ROOF_Y = 5                                         # canopy front-lip row
_RCY_POSTS = (5.0, 15.0, 25.0)                          # canopy post centres


def _rcyd_col_height(x, charge):
    """Rows of scrap standing in bay column `x` at fill level `charge`.

    A centre-peaked mound with deterministic per-column roughness, so the heap
    reads as tipped scrap rather than a level liquid, and every stage still
    raises the profile somewhere visible."""
    if charge <= 0:
        return 0
    span = _RCY_BAY_X1 - _RCY_BAY_X0
    t = (x - _RCY_BAY_X0) / span
    mound = 1.0 - abs(t - 0.5) * 1.35
    jag = ((x * 7 + 3) % 5) / 12.0
    return max(0, min(charge, int(round(charge * max(0.0, mound) - jag * charge * 0.35))))


def _rcyd_scrap_col(x, y):
    """Deterministic scrap tone: mixed plate, rust and bright cut edges. Kept
    well above the bay's shadowed interior so the heap reads as a mass of
    material rather than a dark void in the middle of the sprite."""
    k = (x * 5 + y * 3) % 7
    if k in (0, 3):
        return RUST
    if k == 1:
        return dim(LEGACY_GRAY, 0.15)
    if k in (5, 6):
        return lit(LEGACY_GRAY, 0.28)
    return lit(LEGACY_GRAY, 0.08)


def _rcyd_accents(damaged, charge):
    """The fill readout as (x, y, colour) *native* pixels.

    Same reason as _vlt_accents: SUN_GOLD is what _index_for routes onto the
    80-95 player-remap ramp, and the 4x LANCZOS kernel reaches past a pixel's
    own block, so gold drawn in the supersampled pass blends with the dark
    bezel/scrap beside it and lands back on a fixed palette entry. Re-stamping
    these after the downscale is what keeps the level team-coloured."""
    live = not damaged
    on = SUN_GOLD if live else dim(SUN_GOLD, 0.4)
    off = dim(LEGACY_GRAY_DARK, 0.15)
    out = []
    for i in range(RCYD_SEGMENTS):
        col = on if i < charge else off
        for x in (_RCY_BAR_X0 + i * 3, _RCY_BAR_X0 + i * 3 + 1):
            for y in range(_RCY_BAR_Y0, _RCY_BAR_Y1 + 1):
                out.append((x, y, col))
    # Sorter light along the crest of the heap: marks the current level on the
    # continuous readout the way the Vault's lit top row does.
    rim = lit(SUN_GOLD, 0.4) if live else dim(SUN_GOLD, 0.35)
    for x in range(_RCY_BAY_X0, _RCY_BAY_X1 + 1):
        n = _rcyd_col_height(x, charge)
        if n:
            out.append((x, _RCY_BAY_FLOOR - n + 1, rim))
    return out


def rcyd_frame(damaged=False, charge=RCYD_STAGES - 1):
    """One Recycling Depot frame, with the fill readout re-stamped at native
    resolution on top of the supersampled render (see _rcyd_accents)."""
    img = render(rcyd_draw, SG1x1_W, SG1x1_H, damaged=damaged, charge=charge)
    px = img.load()
    for x, y, col in _rcyd_accents(damaged, charge):
        px[x, y] = tuple(col[:3]) + (255,)
    return img


def rcyd_draw(sd, w=SG1x1_W, h=SG1x1_H, damaged=False, charge=RCYD_STAGES - 1):
    """Recycling Depot holding `charge` of scrap (0..RCYD_STAGES-1)."""
    live = not damaged
    ground_y0, ground_y1 = h - 8, h
    draw_ground_strip(sd, 2, w - 2, ground_y0, ground_y1, seed=13)

    shell = _RCY_HALL if live else mix(_RCY_HALL, DAMAGE_SCORCH, 0.3)
    floor_y = _RCY_BAY_FLOOR + 1
    wall_top = 19.0                       # low back wall: air above it, under the roof
    roof_x0, roof_x1 = 2.0, 33.0
    fascia_y0, fascia_y1 = _RCY_ROOF_Y, _RCY_ROOF_Y + 4

    # Painted contact shadow rather than a SHADOW_IDX one, same reasoning as the
    # Battery Bank: the pad is opaque, so a cast shadow would only show through
    # the gaps and read as holes in the sprite.
    sd.ellipse([3, floor_y - 0.5, 37, floor_y + 3], fill=dim(CONCRETE, 0.25))
    # Apron the bay is poured on, with the tipping lip along its front edge.
    sd.rect([3, wall_top, 35, floor_y], fill=dim(CONCRETE, 0.12))
    sd.line([(3, floor_y), (35, floor_y)], fill=dim(CONCRETE, 0.5), width=0.7)
    sd.line([(3, wall_top), (35, wall_top)], fill=dim(CONCRETE, 0.35), width=0.4)

    # --- back wall and rear post, both behind the heap ------------------------
    # Kept low so the gap between its top and the canopy stays open: that strip
    # of daylight is the whole difference between a bay and a shed.
    sd.rect([4, wall_top, 30, floor_y], fill=dim(CONCRETE, 0.3))
    sd.line([(4, wall_top), (30, wall_top)], fill=lit(CONCRETE, 0.2), width=0.5)
    for gx in range(7, 30, 5):
        sd.line([(gx, wall_top + 1), (gx, floor_y - 1)], fill=dim(CONCRETE, 0.45), width=0.4)
    sd.rect([_RCY_POSTS[1] - 0.7, fascia_y1, _RCY_POSTS[1] + 0.7, wall_top + 1],
            fill=dim(shell, 0.12))
    sd.line([(_RCY_POSTS[1] - 0.7, fascia_y1), (_RCY_POSTS[1] - 0.7, wall_top)],
            fill=lit(shell, 0.25), width=0.4)

    # --- shredder end ---------------------------------------------------------
    # All the machinery is pushed to one end: the jaw box that eats what the
    # bay holds, its feed chute, and the stack. Keeping it off to the side is
    # what leaves the rest of the outline as posts and air.
    capped_box(sd, 30, 12, 37, floor_y, lit(shell, 0.12), depth=2.4, edge=0.34)
    # Jaw mouth: a dark slot with the shredder's teeth showing in it, the one
    # detail that says this end of the bay is a machine and not a shed wall.
    sd.rect([30.8, 13.6, 36.2, 17.4], fill=dim(PANEL_BLUEBLACK, 0.15))
    for jx in (31.6, 33.0, 34.4, 35.6):
        sd.line([(jx, 13.8), (jx, 17.2)], fill=lit(shell, 0.45), width=0.5)
    sd.line([(30.8, 15.5), (36.2, 15.5)], fill=dim(PANEL_BLUEBLACK, 0.45), width=0.5)
    # Feed chute, running down out of the jaw into the bay.
    sd.poly([(30.4, 18.4), (23, 21.4), (23, 23.4), (30.4, 20.6)], fill=dim(shell, 0.05))
    sd.line([(30.4, 18.4), (23, 21.4)], fill=lit(shell, 0.4), width=0.6)
    sd.line([(30.4, 20.6), (23, 23.4)], fill=dim(shell, 0.45), width=0.5)
    sd.rect([33.4, 2, 35.4, 12], fill=dim(shell, 0.25))                           # stack
    sd.line([(33.4, 2), (33.4, 12)], fill=lit(shell, 0.35), width=0.5)
    sd.ellipse([32.9, 1.2, 35.9, 3], fill=dim(LEGACY_GRAY_DARK, 0.1))
    # Running light: stays lit at zero fill so an empty bay still reads as
    # powered rather than destroyed.
    sd.px(31, 19, lit(GREEN_ACCENT, 0.3) if live else dim(LEGACY_GRAY, 0.35))

    # --- the heap the bay exists to hold -------------------------------------
    # Drawn on whole pixels so every stage moves the profile by exact rows.
    for x in range(_RCY_BAY_X0, _RCY_BAY_X1 + 1):
        n = _rcyd_col_height(x, charge)
        for k in range(n):
            y = _RCY_BAY_FLOOR - k
            sd.px(x, y, _rcyd_scrap_col(x, y) if live else mix(_rcyd_scrap_col(x, y), DAMAGE_SCORCH, 0.25))

    # --- canopy: front posts, then the roof they carry ------------------------
    for i, px_ in enumerate(_RCY_POSTS):
        if i == 1:
            continue                                   # rear post, drawn above
        lean = 1.4 if (damaged and i == 0) else 0.0    # near post kicked out
        sd.poly([(px_ - 1.0 - lean, floor_y), (px_ + 1.0 - lean, floor_y),
                 (px_ + 1.0, fascia_y1), (px_ - 1.0, fascia_y1)], fill=shell)
        sd.line([(px_ - 1.0 - lean * 0.5, floor_y - 1), (px_ - 1.0, fascia_y1)],
                fill=lit(shell, 0.3), width=0.4)
        # Foot plate, so the posts stand on the apron instead of floating.
        sd.rect([px_ - 1.8 - lean, floor_y - 0.8, px_ + 1.8 - lean, floor_y], fill=dim(shell, 0.45))
    sag = 2.2 if damaged else 0.0                      # near corner drops with its post
    roof = Roof(roof_x0, fascia_y0, roof_x1, 5.0)
    quad = roof.quad()
    sd.poly([(quad[0][0], quad[0][1] + sag), quad[1], quad[2], quad[3]], fill=lit(shell, 0.34))
    sd.line([roof.at(0, 1), roof.at(1, 1)], fill=lit(shell, 0.5), width=0.6)
    for i in range(1, 5):
        u = i / 5
        sd.line([roof.at(u, 0.06), roof.at(u, 0.94)], fill=dim(shell, 0.14), width=0.4)
    # Fascia: the roof's front face, and the strip the fill gauge is read off.
    sd.poly([(roof_x0, fascia_y0 + sag), (roof_x1, fascia_y0), (roof_x1, fascia_y1),
             (roof_x0, fascia_y1 + sag)], fill=shell)
    sd.line([(roof_x0, fascia_y1 + sag), (roof_x1, fascia_y1)], fill=dim(shell, 0.4), width=0.5)

    # --- fill gauge on the fascia --------------------------------------------
    on_col = SUN_GOLD if live else dim(SUN_GOLD, 0.4)
    off_col = dim(LEGACY_GRAY_DARK, 0.15)
    sd.rect([_RCY_BAR_X0 - 1.5, _RCY_BAR_Y0 - 1, _RCY_BAR_X0 + RCYD_SEGMENTS * 3, _RCY_BAR_Y1 + 1],
            fill=mix(PANEL_BLUEBLACK, shell, 0.25))
    for i in range(RCYD_SEGMENTS):
        sx = _RCY_BAR_X0 + i * 3
        _vlt_charge_px(sd, sx, sx + 1, _RCY_BAR_Y0, _RCY_BAR_Y1, on_col if i < charge else off_col)

    if damaged:
        # The near corner has come off its post: torn fascia, buckled roof edge.
        sd.line([(roof_x0, fascia_y0 + sag), (roof_x0 + 7, fascia_y0 + sag * 0.4)],
                fill=RUST, width=0.5)
        sd.line([(35.4, 4), (34.2, 8)], fill=RUST, width=0.5)
        scorch(sd, [(6, fascia_y1 + 2, 2.0), (32, 20, 1.8)])


# The Arc Turret's head is a rotating sprite of its own (issue #66), so the
# body sheet keeps only the pedestal. `Turreted: Offset: 0,0,112` draws the
# turret sprite 112 world units up, which at RA's 24px/1024-unit scale is
# 2.625px, so the head has to be drawn that much lower inside its own frame
# for its underside to land back on the pedestal.
ARCT_AZIMUTH = 208.0                 # three-quarter view, used for the cameo
ARCT_TUR_LIFT = 112 * 24 / 1024
ARCT_PEDESTAL_DY = 9                 # pedestal top, below the body frame centre
ARCT_TUR_OY = SG1x1_H / 2 + ARCT_PEDESTAL_DY + ARCT_TUR_LIFT


def arct_mesh(damaged=False):
    """Arc Turret as a solid: a ring-mounted emitter head carrying twin
    discharge rods, deliberately NOT a nozzle/fuel-tank silhouette so it reads
    as "electric discharge" rather than "flamethrower" (docs/BACKLOG.md issue
    #36). Rebuilt in 3D for issue #65 -- the flat blob it replaced had no
    volume at all next to the ported stock defences it shares a sidebar with."""
    body = mix(_TUR_HULL, LEGACY_GRAY, 0.22)
    body = body if not damaged else mix(body, DAMAGE_SCORCH, 0.4)
    cap = _TUR_CAP if not damaged else mix(_TUR_CAP, DAMAGE_SCORCH, 0.4)
    accent = SUN_GOLD if not damaged else RUST
    m = Mesh()
    # Emitter head: main mass, then a shallower brow plate above it.
    m.box(-7.5, -5.5, 1.5, 7.5, 5.5, 10.0, body, top=lit(body, 0.14))
    m.box(-6.2, -4.6, 10.0, 6.2, 4.6, 11.4, cap, top=lit(cap, 0.2))
    # Cooling stack behind the head.
    m.box(-2.2, -7.0, 5.0, 2.2, -5.4, 14.2, dim(body, 0.35), top=dim(body, 0.2))
    # Capacitor band -- the team-coloured element, same grammar as the turret
    # -- and the recessed emitter port above it. Both are proud of the head so
    # they are drawn after it, and both drop their top face: a wrap-around
    # band is a strip of side faces, not a slab sitting on the roof.
    m.box(-7.9, -5.9, 3.0, 7.9, 5.9, 4.4, accent, order=1, shadow=False, top_face=False)
    m.box(-4.2, -6.0, 5.4, 4.2, 6.0, 8.4, dim(body, 0.5), order=1, shadow=False,
          top_face=False)
    # Twin discharge rods standing off the brow, splayed just enough to leave
    # a gap for the arc. The right rod snaps short when damaged, so the
    # silhouette itself carries the damage state.
    for sx, live in ((-1, True), (1, not damaged)):
        tip = _arct_rod_tip(sx, live)
        # The rods are excluded from the cast shadow: at this camera a 10px
        # mast throws a shadow longer than the whole footprint, which reads as
        # a smear rather than as contact. Only the head's own mass casts.
        m.strut((sx * 3.6, -0.5, 10.6), tip, 1.7,
                mix(LEGACY_GRAY_DARK, LEGACY_GRAY, 0.35), cap=lit(LEGACY_GRAY, 0.1),
                order=2, shadow=False)
        if live:
            m.strut(tip, (tip[0] * 1.05, tip[1] + 0.4, tip[2] + 1.8), 1.8,
                    accent, cap=lit(accent, 0.35), order=2, shadow=False)
    return m


def _arct_rod_tip(sx, live=True):
    return (sx * 5.5, 1.5 if live else 0.5, 20.5 if live else 14.0)


def arct_draw(sd, w=SG1x1_W, h=SG1x1_H, damaged=False):
    """Body sheet: the fixed pedestal and mount race only. The emitter head
    rides above this as a separate 32-facing turret sprite."""
    ground_y0, ground_y1 = h - 8, h
    draw_ground_strip(sd, 2, w - 2, ground_y0, ground_y1, seed=10)
    ox, oy = w // 2, h - ARCT_PEDESTAL_DY
    base = LEGACY_GRAY_DARK if not damaged else mix(LEGACY_GRAY_DARK, DAMAGE_SCORCH, 0.5)
    # Concrete pedestal and the mount race the head sits in -- ellipses, so
    # the footprint stays a clean oval, and so the race is pixel-identical
    # under every facing of the head (sam2.shp's fixed-mount rule).
    sd.ellipse([ox - 11, oy - 1.5, ox + 11, oy + 6.5], fill=dim(CONCRETE, 0.35))
    sd.ellipse([ox - 11, oy - 4, ox + 11, oy + 4], fill=CONCRETE)
    sd.ellipse([ox - 11, oy - 4, ox + 11, oy + 4], outline=lit(CONCRETE, 0.25), width=0.6)
    sd.ellipse([ox - 8, oy - 4.6, ox + 8, oy + 1.4], fill=base)
    sd.ellipse([ox - 8, oy - 5.4, ox + 8, oy + 0.6], fill=lit(base, 0.18))
    # Anchor bolts around the race, and a team-coloured feed lug at the front.
    for i in range(8):
        a = i * math.pi / 4 + math.pi / 8
        sd.px(round(ox + 9.4 * math.cos(a)), round(oy - 2 + 4.4 * math.sin(a)), lit(base, 0.4))
    sd.rect([ox - 2, oy + 1.6, ox + 2, oy + 3.2], fill=(SUN_GOLD if not damaged else RUST))
    if damaged:
        scorch(sd, [(ox + 6, oy - 2, 3), (ox - 7, oy + 2, 2.5)])


def arct_shadow_draw(sd, w=SG1x1_W, h=SG1x1_H, damaged=False):
    ox, oy = w // 2, h - ARCT_PEDESTAL_DY
    sd.ellipse([ox - 5, oy - 0.5, ox + 17, oy + 7], fill=(0, 0, 0, 255))


def arct_turret_draw(sd, w=SG1x1_W, h=SG1x1_H, damaged=False, facing=0.0):
    """Rotating emitter head: the mesh plus its live discharge arc."""
    ox, oy = w // 2, ARCT_TUR_OY
    arct_mesh(damaged).draw(sd, ox, oy, facing)
    if damaged:
        return
    # The living arc bridging the rod tips, anchored to the projected
    # electrode heads so it tracks the head through every facing. Opaque, not
    # a translucent bloom: indexed sprites have 1-bit alpha, so anything drawn
    # at low opacity is simply thresholded away (issue #64's fade lesson).
    tips = sorted(mesh_screen((t[0], t[1], t[2] + 1.7), ox, oy, facing)
                  for t in (_arct_rod_tip(-1), _arct_rod_tip(1)))
    (lx, ly), (rx, ry) = tips
    mid = ((lx + rx) / 2, (ly + ry) / 2)
    sd.line([(lx, ly), (mid[0] - 1.2, mid[1] - 1.8), (mid[0] + 1.2, mid[1] + 1.4), (rx, ry)],
            fill=lit(GREEN_ACCENT, 0.5), width=1.0)
    for (px_, py_) in ((lx, ly), (rx, ry)):
        sd.px(round(px_), round(py_), lit(GREEN_ACCENT, 0.75))


def arct_turret_shadow_draw(sd, w=SG1x1_W, h=SG1x1_H, damaged=False, facing=0.0):
    arct_mesh(damaged).draw_shadow(sd, w // 2, ARCT_TUR_OY, facing)


def arct_turret_frames(damaged=False, n=32):
    bodies, shadows = [], []
    for i in range(n):
        deg = i * (360.0 / n)
        bodies.append(render(arct_turret_draw, SG1x1_W, SG1x1_H, damaged=damaged, facing=deg))
        shadows.append(render_shadow_mask(arct_turret_shadow_draw, SG1x1_W, SG1x1_H,
                                          damaged=damaged, facing=deg))
    return bodies, shadows


def arct_icon_draw(sd, w=SG1x1_W, h=SG1x1_H, damaged=False):
    """Body and head together, for the programmatic cameo fallback (the
    shipped cameo is issue #45's photographic one)."""
    arct_draw(sd, w, h, damaged)
    arct_mesh(damaged).draw(sd, w // 2, h - ARCT_PEDESTAL_DY, ARCT_AZIMUTH)


def sgwnd_draw(sd, w=FAM23_W, h=FAM23_H, damaged=False):
    """Wind Turbine Array: two slim turbine poles/rotors -- deliberately
    sparser than Solar Array's dense panel frames, matching Wind Turbine's
    "cheap, mass-producible" fantasy.

    Volumetric second pass (issue #48's technique, batch 2): the flat
    tapered-polygon towers become cylindrical masts (horizontal lighting
    ramp on a tapering silhouette, same key light as vcyl) planted on a
    concrete footing with real depth (capped_box); the nacelle becomes a
    shaded pod with a sphere-read hub; and the rotor gains a foreshortened
    translucent swept disc behind tapered volume blades, so it reads as a
    spinning mass at the game's front-above angle instead of three stick
    lines."""
    ground_y0, ground_y1 = h - 12, h
    gold_y0, gold_y1 = ground_y0 - 8, ground_y0
    draw_ground_strip(sd, 2, w - 2, ground_y0, ground_y1, seed=8)
    draw_gold_band(sd, 6, w - 6, gold_y0, gold_y1)
    for k, cx in enumerate((w // 3, 2 * w // 3)):
        hub_y = gold_y0 - 26
        stopped = damaged and k == 0
        contact_shadow(sd, cx + 1, gold_y0 + 0.7, 5, 1.5, base=SUN_GOLD)
        # Concrete footing block with volume.
        capped_box(sd, cx - 3, gold_y0 - 3, cx + 3, gold_y0 - 0.5, CONCRETE, depth=1.4, edge=0.3)
        # Tapered cylindrical mast: brightness peaks left of center, darkest
        # at both silhouette edges (vcyl's ramp on a tapering outline).
        base_hw, top_hw = 2.0, 0.9
        bands = 5
        for i in range(bands):
            t0, t1 = i / bands, (i + 1) / bands
            c = (t0 + t1) / 2
            b = 1.0 - abs(c - 0.35) * 2.0
            col = (lit(LEGACY_GRAY, 0.32 * max(0.0, b)) if b > 0
                   else dim(LEGACY_GRAY, 0.3 * min(1.0, -b + 0.3)))
            sd.poly([
                (cx - base_hw + 2 * base_hw * t0, gold_y0 - 2),
                (cx - base_hw + 2 * base_hw * t1, gold_y0 - 2),
                (cx - top_hw + 2 * top_hw * t1, hub_y),
                (cx - top_hw + 2 * top_hw * t0, hub_y),
            ], fill=col)
        # Service door at the mast base.
        sd.rect([cx - 0.8, gold_y0 - 6.5, cx + 0.8, gold_y0 - 2.5], fill=dim(LEGACY_GRAY, 0.45))
        # Nacelle pod: shaded body behind a sphere-read hub cone.
        sd.ellipse([cx - 2.6, hub_y - 2.2, cx + 2.6, hub_y + 2.2], fill=dim(LEGACY_GRAY, 0.2))
        sd.ellipse([cx - 2.6, hub_y - 2.2, cx + 1.6, hub_y + 1.4], fill=LEGACY_GRAY)
        sd.arc([cx - 2.6, hub_y - 2.2, cx + 2.6, hub_y + 2.2], 150, 300,
               fill=lit(LEGACY_GRAY, 0.4), width=0.5)
        hub_c = SUN_GOLD if not stopped else dim(SUN_GOLD, 0.5)
        # Rotor sweep: foreshortened (rx > ry) spinning-volume read. NB the
        # indexed pipeline's 1-bit alpha (to_indexed) drops sub-threshold
        # translucency over transparent background, so the sweep can't be a
        # soft disc -- it's full-opacity trailing streak arcs behind each
        # blade tip (plus a faint disc that only survives where it overlaps
        # opaque geometry). Skipped when stopped.
        rx, ry = 13, 10.5
        if not stopped:
            sd.ellipse([cx - rx, hub_y - ry, cx + rx, hub_y + ry], fill=GREEN_ACCENT + (13,))
        # Three tapered volume blades on the foreshortened path, phase-offset
        # per turbine so the pair doesn't read as a copy-paste.
        phase = 15 + k * 40
        for b in range(3):
            ang = phase + b * 120
            rad = math.radians(ang)
            blade = dim(GREEN_ACCENT, 0.45) if stopped else GREEN_ACCENT
            blen = 1.0 if not (stopped and b == 1) else 0.55  # snapped blade
            ex = cx + rx * blen * math.cos(rad)
            ey = hub_y - ry * blen * math.sin(rad)
            prad = rad + math.pi / 2
            r0x, r0y = cx + 1.4 * math.cos(prad), hub_y - 1.4 * math.sin(prad)
            r1x, r1y = cx - 1.4 * math.cos(prad), hub_y + 1.4 * math.sin(prad)
            sd.poly([(r0x, r0y), (r1x, r1y), (ex, ey)], fill=blade)
            sd.line([(r0x, r0y), (ex, ey)], fill=lit(blade, 0.4), width=0.6)
            if not stopped:
                # Trailing motion streak on the foreshortened tip path
                # (PIL arc angles run clockwise with y down: math angle a
                # maps to -a).
                sd.arc([cx - rx, hub_y - ry, cx + rx, hub_y + ry],
                       -ang - 52, -ang - 14, fill=dim(GREEN_ACCENT, 0.25), width=1.1)
        # Hub sphere over the blade roots: dark rim, body, offset highlight.
        sd.ellipse([cx - 1.9, hub_y - 1.9, cx + 1.9, hub_y + 1.9], fill=dim(hub_c, 0.35))
        sd.ellipse([cx - 1.7, hub_y - 1.7, cx + 1.5, hub_y + 1.5], fill=hub_c)
        sd.ellipse([cx - 1.2, hub_y - 1.2, cx - 0.1, hub_y - 0.1], fill=lit(hub_c, 0.45))
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
    steel = mix(LEGACY_GRAY, PANEL_BLUEBLACK, 0.25)
    for k, cx in enumerate((w // 2 - 20, w // 2 + 20)):
        tx0, tx1 = cx - tank_w // 2, cx + tank_w // 2
        contact_shadow(sd, cx + 2, gold_y0 + 0.7, tank_w / 2, 1.7, base=SUN_GOLD)
        # Concrete skirt the tank stands on.
        capped_box(sd, tx0 - 1, gold_y0 - 3.5, tx1 + 1, gold_y0, CONCRETE, depth=1.8, edge=0.3)
        # Cylinder body with a horizontal lighting ramp, capped by a real dome
        # (nested ellipses converging on an up-left highlight) instead of one
        # flat ellipse with a bright patch stuck on it.
        vcyl(sd, tx0, tank_top + 5, tx1, gold_y0 - 3, PANEL_BLUEBLACK)
        sphere(sd, tx0, tank_top, tx1, tank_top + 11, PANEL_BLUEBLACK, steps=7,
               lit_f=0.30, dim_f=0.3)
        sd.arc([tx0, tank_top + 1, tx1, tank_top + 12], 12, 168,
               fill=dim(PANEL_BLUEBLACK, 0.45), width=0.6)
        # Gold hoop bands, following the cylinder shading.
        for by in (tank_top + 13, tank_top + 22):
            broke = damaged and k == 1 and by > tank_top + 20
            sd.line([(tx0 + 0.6, by), (tx1 - (9 if broke else 0.6), by)], fill=SUN_GOLD, width=1.2)
            sd.line([(tx0 + 0.6, by + 0.8), (tx1 - (9 if broke else 0.6), by + 0.8)],
                    fill=dim(SUN_GOLD, 0.4), width=0.4)
        if k == 0:
            # Relief stack rising off the far tank's crown.
            sd.line([(tx0 + 6, tank_top + 3), (tx0 + 6, tank_top - 7)], fill=steel, width=1.4)
            sd.line([(tx0 + 5.4, tank_top + 3), (tx0 + 5.4, tank_top - 7)], fill=lit(steel, 0.35), width=0.4)
            sd.ellipse([tx0 + 4.2, tank_top - 9, tx0 + 7.8, tank_top - 6.4], fill=lit(steel, 0.15))
        else:
            # Caged access ladder up the near tank -- the "you could walk on
            # this" scale cue the flat cylinders were missing.
            lx = tx1 - 7
            sd.line([(lx - 1.6, gold_y0 - 4), (lx - 1.6, tank_top + 7)], fill=dim(steel, 0.15), width=0.5)
            sd.line([(lx + 1.6, gold_y0 - 4), (lx + 1.6, tank_top + 7)], fill=dim(steel, 0.15), width=0.5)
            for ry in range(int(tank_top) + 9, int(gold_y0) - 4, 4):
                if damaged and ry > gold_y0 - 12:
                    continue
                sd.line([(lx - 1.6, ry), (lx + 1.6, ry)], fill=lit(steel, 0.2), width=0.4)
    # Compressor skid between the tanks, with the transfer pipe arching over it.
    sx0, sx1 = w // 2 - 8, w // 2 + 8
    capped_box(sd, sx0, gold_y0 - 9, sx1, gold_y0, steel, depth=2.2, edge=0.34)
    for i in range(3):
        sd.line([(sx0 + 2, gold_y0 - 7 + i * 2), (sx1 - 2, gold_y0 - 7 + i * 2)],
                fill=dim(steel, 0.4), width=0.4)
    sd.px(sx1 - 2.5, gold_y0 - 8.4, GREEN_ACCENT if not damaged else dim(GREEN_ACCENT, 0.45))
    pipe_y = tank_top + 17
    for x0_, x1_ in ((w // 2 - 20 + tank_w // 2, sx0 + 3), (sx1 - 3, w // 2 + 20 - tank_w // 2)):
        sd.line([(x0_, pipe_y), (x1_, pipe_y)], fill=SUN_GOLD, width=1.6)
        sd.line([(x0_, pipe_y - 0.9), (x1_, pipe_y - 0.9)], fill=lit(SUN_GOLD, 0.4), width=0.4)
    sd.line([(sx0 + 3, pipe_y), (sx0 + 3, gold_y0 - 9)], fill=SUN_GOLD, width=1.4)
    sd.line([(sx1 - 3, pipe_y), (sx1 - 3, gold_y0 - 9)], fill=dim(SUN_GOLD, 0.25), width=1.4)
    sd.ellipse([w / 2 - 2.6, pipe_y - 2.6, w / 2 + 2.6, pipe_y + 2.6], fill=dim(SUN_GOLD, 0.25))
    sd.ellipse([w / 2 - 1.4, pipe_y - 1.4, w / 2 + 1.4, pipe_y + 1.4], fill=lit(SUN_GOLD, 0.3))
    if damaged:
        # Crumpled crown on the near tank: the outline carries the state.
        cxd = w // 2 + 20
        sd.poly([(cxd + 1, tank_top + 1), (cxd + 11, tank_top + 3.5), (cxd + 10, tank_top + 8),
                 (cxd + 1, tank_top + 6)], fill=dim(PANEL_BLUEBLACK, 0.5))
        scorch(sd, [(w / 2, pipe_y + 5, 3.5), (w / 2 - 26, tank_top + 12, 3),
                    (w / 2 + 15, gold_y0 + 3, 2.5)])


# ---------------------------------------------------------------------------
# Image-plane rotation, for genuinely top-down radially symmetric hardware
# only: the two drone bodies and the Hauler Drone (32 facings, no damaged
# variant -- matching tran/mh60/heli, which don't define one either). Rotation
# happens at SS resolution before the downscale, so facings stay crisp.
# Anything with a distinguishable top, front and side -- the defence turrets --
# goes through Mesh instead; see issue #65 for why this is not a matter of
# taste.
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


def rotated_anim_frames(draw_fn, frame_w, frame_h, n=32, length=4, outlined=True, **kwargs):
    """Same as rotated_frames, but each facing carries `length` animation frames
    and the strip is laid out **facing-major** -- facing 0's whole animation,
    then facing 1's, and so on.

    That is the layout `Facings: n` + `Length: length` resolves to: the engine
    indexes a sequence as `facingIndex * Length + frame % Length`
    (DefaultSpriteSequence.GetSprite), so the sheet has to hold n * length
    frames. Getting this wrong is what crashed the shellmap in issue #35, so
    the frame count is asserted against the sequence math at the call site.

    `draw_fn` is called once per animation step with `spin=` set to that step's
    phase in degrees, and the result is rotated into the facing the same way a
    static body is -- so a moving part stays registered with the airframe it is
    bolted to at every facing, which is the whole reason the animation lives in
    the body sheet rather than in a WithIdleOverlay (see docs/BACKLOG.md #81)."""
    bases = []
    for k in range(length):
        base = Image.new("RGBA", (frame_w * SS, frame_h * SS), (0, 0, 0, 0))
        draw_fn(SD(base), frame_w, frame_h, spin=k * (360.0 / length), **kwargs)
        bases.append(base)
    frames = []
    for i in range(n):
        angle = i * (360.0 / n)
        for base in bases:
            f = base.rotate(angle, resample=Image.BICUBIC, center=(frame_w * SS / 2, frame_h * SS / 2))
            f = f.resize((frame_w, frame_h), Image.LANCZOS)
            if outlined:
                f = outline_sprite(f)
            frames.append(f)
    return frames


# ---------------------------------------------------------------------------
# Grid Defense Turret (SGTUR) rotating assembly -- 32 facings x 2 damage
# states, drawn as 32 genuine viewpoints of one 3D weapon station (issue #65).
#
# Construction copied from the stock rotating turret next to it (sam2.shp):
# the mount never moves and never re-lights, the superstructure is a solid
# redrawn per facing, and the barrel is offset from the pivot so the direction
# it points is legible at a glance. The sheet holds only the rotating
# assembly -- sequences/structures.yaml draws the fixed pad underneath from
# stock gunmake.shp, the same split sam: uses.
# ---------------------------------------------------------------------------

SGTUR_W, SGTUR_H = 48, 44
SGTUR_PIVOT_DY = 3      # pad contact point, just below the frame centre


def sgtur_mesh(damaged=False):
    """The rotating assembly in world units (x east, y north, z up), zeroed on
    the pivot at pad level and pointing north at facing 0."""
    hull = _TUR_HULL if not damaged else mix(_TUR_HULL, DAMAGE_SCORCH, 0.38)
    cap = _TUR_CAP if not damaged else mix(_TUR_CAP, DAMAGE_SCORCH, 0.42)
    barrel = _TUR_BARREL if not damaged else mix(_TUR_BARREL, DAMAGE_SCORCH, 0.5)
    accent = SUN_GOLD if not damaged else RUST
    m = Mesh()
    # Hull, then the recessed cap plate above it.
    m.box(-7.5, -6.5, 2.0, 7.5, 4.5, 9.0, hull, top=lit(hull, 0.12))
    m.box(-6.2, -5.5, 9.0, 6.2, 3.5, 10.3, cap, top=lit(cap, 0.18))
    # Conduit band wrapping the hull: the one team-coloured element, sitting
    # slightly proud so it catches its own shading on every face.
    m.box(-7.9, -6.9, 4.4, 7.9, 4.9, 5.9, accent, top=lit(accent, 0.25))
    # Front apron below the barrel line.
    m.box(-5.5, 4.5, 2.0, 5.5, 6.2, 6.6, dim(hull, 0.12))
    # Sensor block on the rear left of the cap, with a live status pip.
    m.box(-5.4, -4.8, 10.3, -3.2, -2.2, 12.6, dim(cap, 0.15),
          top=(GREEN_ACCENT if not damaged else dim(GREEN_ACCENT, 0.55)))
    # Mantlet + barrel, carried on top of the hull rather than through its
    # front face, so the gun is still visible over the roofline when it points
    # away from the camera -- the read stock turret art keeps at every facing.
    # Both sit right of the pivot (as in the concept art), so a facing is
    # legible from the offset alone, not just the barrel angle.
    tip = 16.4 if not damaged else 13.2
    m.prism(3.2, 1.2, 9.0, 12.9, 2.5, dim(hull, 0.18), sides=8, top=lit(hull, 0.22))
    m.box(1.9, 4.0, 10.2, 4.5, tip, 12.5, barrel, top=lit(barrel, 0.3))
    if not damaged:
        m.box(1.3, tip - 1.5, 9.8, 5.1, tip + 0.9, 12.9, accent, top=lit(accent, 0.3))
    return m


def _sgtur_mount(sd, ox, oy, damaged=False):
    """Turntable under the assembly. Drawn with ellipses rather than as mesh
    faces so it is pixel-identical in all 32 facings (sam2.shp keeps 227
    pixels byte-identical across its facings for exactly this reason)."""
    ring = dim(SUN_GOLD, 0.35) if not damaged else dim(RUST, 0.2)
    base = LEGACY_GRAY_DARK if not damaged else mix(LEGACY_GRAY_DARK, DAMAGE_SCORCH, 0.5)
    sd.ellipse([ox - 11, oy - 5.5, ox + 11, oy + 5.5], fill=dim(base, 0.35))
    sd.ellipse([ox - 11, oy - 6.8, ox + 11, oy + 4.2], fill=base)
    sd.ellipse([ox - 11, oy - 6.8, ox + 11, oy + 4.2], outline=lit(base, 0.3), width=0.6)
    sd.ellipse([ox - 8.6, oy - 5.4, ox + 8.6, oy + 3.2], fill=dim(base, 0.25))
    # Bolt ring: eight studs around the race, one team-coloured feed lug.
    for i in range(8):
        a = i * math.pi / 4 + math.pi / 8
        sd.px(round(ox + 9.7 * math.cos(a)), round(oy - 1.3 + 4.8 * math.sin(a)), lit(base, 0.45))
    sd.rect([ox - 2, oy + 2.4, ox + 2, oy + 4.2], fill=ring)


def sgtur_turret_draw(sd, w, h, damaged=False, facing=0.0):
    ox, oy = w // 2, h // 2 + SGTUR_PIVOT_DY
    _sgtur_mount(sd, ox, oy, damaged)
    sgtur_mesh(damaged).draw(sd, ox, oy, facing)
    if damaged:
        # Blown cap panel and a rust streak down the hull, on the fixed
        # top-left the key light comes from (so it never spins with the
        # barrel the way the old rotated-image damage decal did).
        sd.ellipse([ox - 5.5, oy - 11.5, ox - 1.5, oy - 8.5], fill=DAMAGE_SCORCH + (235,))
        sd.ellipse([ox - 4.6, oy - 10.8, ox - 2.6, oy - 9.6], fill=(0, 0, 0, 255))
        sd.px(ox + 5, oy - 4, RUST)
        sd.px(ox + 5, oy - 3, dim(RUST, 0.3))


def sgtur_shadow_draw(sd, w, h, damaged=False, facing=0.0):
    ox, oy = w // 2, h // 2 + SGTUR_PIVOT_DY
    sd.ellipse([ox - 10, oy - 4.5, ox + 12, oy + 5], fill=(0, 0, 0, 255))
    sgtur_mesh(damaged).draw_shadow(sd, ox, oy, facing)


def sgtur_frames(damaged=False, n=32):
    """One genuine viewpoint per facing: frame 0 = north, winding
    counter-clockwise (the convention heli.shp's 32-facing sheet confirms)."""
    bodies, shadows = [], []
    for i in range(n):
        deg = i * (360.0 / n)
        bodies.append(outline_sprite(render(sgtur_turret_draw, SGTUR_W, SGTUR_H,
                                            damaged=damaged, facing=deg)))
        shadows.append(render_shadow_mask(sgtur_shadow_draw, SGTUR_W, SGTUR_H,
                                          damaged=damaged, facing=deg))
    return bodies, shadows


def sgtur_base_draw(sd, w, h, damaged=False):
    """Three-quarter view for the programmatic cameo fallback."""
    sgtur_turret_draw(sd, w, h, damaged=damaged, facing=28.0)


def sgtur_pad_draw(sd, w, h, damaged=False):
    """The fixed emplacement pad the rotating station stands on.

    Previously stock gunmake.shp (the Turret's own concrete pad), which also
    meant the build-up was a different building's -- see issue #74. Drawn to
    the same contact point the station's turntable sits on (SGTUR_PIVOT_DY),
    so the two line up."""
    cy = h // 2 + SGTUR_PIVOT_DY
    cx = w // 2
    rx, ry = 15.0, 8.0
    # Octagonal hardstand: lit top face, shaded lower rim, anchor bolts.
    oct_pts = [(cx + rx * dx, cy + ry * dy) for dx, dy in
               ((-1, -0.42), (-0.42, -1), (0.42, -1), (1, -0.42),
                (1, 0.42), (0.42, 1), (-0.42, 1), (-1, 0.42))]
    sd.poly([(x, y + 1.6) for x, y in oct_pts], fill=dim(CONCRETE, 0.45))
    sd.poly(oct_pts, fill=CONCRETE)
    sd.line([oct_pts[7], oct_pts[0], oct_pts[1], oct_pts[2]], fill=lit(CONCRETE, 0.22), width=0.6)
    sd.line([oct_pts[3], oct_pts[4], oct_pts[5], oct_pts[6]], fill=dim(CONCRETE, 0.3), width=0.6)
    for dx, dy in ((-0.66, -0.5), (0.66, -0.5), (-0.66, 0.5), (0.66, 0.5)):
        sd.px(cx + rx * dx, cy + ry * dy, dim(CONCRETE, 0.4))
    # Cable trench feeding the mount, on the remap ramp like every other
    # building's conduit.
    sd.rect([cx - 3, cy + ry * 0.4, cx + 3, cy + ry * 0.4 + 1.6], fill=dim(SUN_GOLD, 0.25))


def _drone_boom(sd, cx, cy, ex, ey, col, wide=1.5):
    """Tapered rotor boom with a lit upper edge, so the arms read as tubes."""
    sd.line([(cx, cy), (ex, ey)], fill=col, width=wide)
    sd.line([(cx - 0.35, cy - 0.35), (ex - 0.35, ey - 0.35)], fill=lit(col, 0.4), width=0.45)


# Rotor-spin frames per facing on both drone sheets. Must match `Length:` on
# sgdro/sgdrs's `idle:` sequence in mods/sungrid/sequences/aircraft.yaml --
# the engine reads Facings x Length frames out of the sheet (issue #35).
DRONE_SPIN_FRAMES = 4


def _small_rotor(sd, cx, cy, r, phase=0.0, tint=(0xA8, 0xA8, 0x9C)):
    """A turning rotor at the shrunk drones' scale: a swept *ring*, not blades.

    rotor_blur's dashes-plus-trailing-streak recipe is drawn for a 3-4px disc.
    At the ~2px radius the smaller airframes carry, two dashes and a streak
    land on the same handful of pixels, and the 1px readability outline then
    welds them into a spike -- the drone reads as a caltrop rather than a
    quadcopter, and the spike direction changes frame to frame through the 32
    image-plane rotations. An opaque ring with one brighter leading quadrant
    keeps its shape at every facing and still says 'this is turning'."""
    sd.ellipse([cx - r, cy - r, cx + r, cy + r], outline=dim(tint, 0.22), width=0.8)
    # Blade inside the ring, plus a brighter tip on its leading edge. The blade
    # is what actually moves frame to frame; the ring holds the silhouette (and
    # therefore the ground shadow) steady while it does, which is what keeps a
    # rotating radial mark from reading as the caltrop spike a bare blade does
    # at this radius.
    a = math.radians(phase)
    sd.line([(cx, cy), (cx + r * 0.95 * math.cos(a), cy - r * 0.95 * math.sin(a))],
            fill=dim(tint, 0.28), width=0.7)
    sd.arc([cx - r, cy - r, cx + r, cy + r], -phase - 34, -phase + 12,
           fill=lit(tint, 0.4), width=0.9)
    sd.px(cx - 0.5, cy - 0.5, LEGACY_GRAY_DARK)


def sgdro_body_draw(sd, w, h, spin=0.0):
    """Recon Drone: a light, slim quadcopter with a gimbal camera slung under
    the nose.

    Volumetric pass (issue #48 batch 3): the four rotors used to be translucent
    discs, which the 1-bit indexed alpha deleted outright (issue #72), leaving
    the drone reading as a diamond ringed by four empty circles. They are now
    opaque swept rings with trailing dashes (rotor_blur), and the flat diamond
    body has become a faceted airframe with a raised spine.

    Scale pass: the airframe used to span ~26x20 of its 32x30 frame, which put
    a *hand-launched scout* on screen at roughly the footprint of a Longbow --
    both drones now sit near half that (~15x12), so an in-flight drone reads as
    the small, cheap thing its cost and 3000hp say it is next to the vehicles
    it flies over. Detail is redrawn rather than scaled: single-pixel booms,
    two-dash rotors, and one flat lit facet instead of a three-facet ramp, so
    nothing is left below the resolution the 1-bit indexed alpha can keep."""
    cx, cy = w // 2, h // 2
    arms = ((-1, -1), (1, -1), (-1, 1), (1, 1))
    for dx, dy in arms:
        _drone_boom(sd, cx, cy, cx + dx * 5.6, cy + dy * 4.0, LEGACY_GRAY_DARK, 1.0)
    for k, (dx, dy) in enumerate(arms):
        _small_rotor(sd, cx + dx * 5.6, cy + dy * 4.0, 2.2, phase=35 + 90 * k + spin)
    # Faceted airframe: dark underside chine, lit upper-left facet, spine.
    sd.poly([(cx, cy - 5.4), (cx + 2.8, cy - 2.0), (cx + 2.6, cy + 3.0), (cx, cy + 5.2),
             (cx - 2.6, cy + 3.0), (cx - 2.8, cy - 2.0)], fill=dim(GREEN_PRIMARY, 0.32))
    sd.poly([(cx, cy - 4.4), (cx + 2.0, cy - 1.6), (cx + 1.6, cy + 2.0), (cx, cy + 3.4),
             (cx - 1.9, cy + 2.0), (cx - 2.2, cy - 1.6)], fill=GREEN_PRIMARY)
    sd.poly([(cx - 0.2, cy - 3.6), (cx + 1.0, cy - 1.6), (cx - 0.4, cy + 1.4), (cx - 1.7, cy - 1.4)],
            fill=lit(GREEN_PRIMARY, 0.3))
    # Gimbal camera ball under the nose.
    sphere(sd, cx - 1.4, cy - 2.2, cx + 1.4, cy + 0.6,
           mix(LEGACY_GRAY, PANEL_BLUEBLACK, 0.55), steps=4, lit_f=0.45)
    sd.px(cx - 0.4, cy - 1.6, lit(LEGACY_GRAY, 0.5))
    # Nav strip on the remap ramp: which drone this is, and whose.
    sd.rect([cx - 0.8, cy + 3.0, cx + 0.8, cy + 4.4], fill=SUN_GOLD)
    sd.px(cx, cy - 5.0, SUN_GOLD)


def sgdrs_body_draw(sd, w, h, spin=0.0):
    """Strike Drone: a heavier armoured airframe with rail-mounted munitions.

    Same volumetric pass as sgdro (issue #48 batch 3): opaque rotor blur, a
    stepped armoured hull with a raised sensor turret rather than a flat
    diamond, and munition rails that read as objects hung under the booms.

    Same scale pass as sgdro, and it stays the visibly bigger of the two: a
    wider rotor square, a longer hull and the munition rails still hanging off
    the forward booms, so the size cue that separates the two drones survives
    at the smaller size."""
    cx, cy = w // 2, h // 2
    arms = ((-1, -1), (1, -1), (-1, 1), (1, 1))
    for dx, dy in arms:
        _drone_boom(sd, cx, cy, cx + dx * 6.6, cy + dy * 4.8, LEGACY_GRAY_DARK, 1.2)
        if dy == -1:
            # Munition rail slung under the forward booms.
            mx, my = cx + dx * 4.2, cy + dy * 3.0
            sd.poly([(mx - 1.0, my - 1.4), (mx + 1.0, my - 1.4), (mx + 1.0, my + 1.6),
                     (mx, my + 2.5), (mx - 1.0, my + 1.6)], fill=dim(PANEL_BLUEBLACK, 0.18))
            sd.px(mx - 0.5, my - 1.0, SUN_GOLD)
    for k, (dx, dy) in enumerate(arms):
        _small_rotor(sd, cx + dx * 6.6, cy + dy * 4.8, 2.5, phase=20 + 90 * k + spin)
    # Armoured hull: dark chine, plated deck, chamfered nose.
    sd.poly([(cx, cy - 6.0), (cx + 3.4, cy - 2.6), (cx + 3.2, cy + 3.6), (cx, cy + 5.8),
             (cx - 3.2, cy + 3.6), (cx - 3.4, cy - 2.6)], fill=dim(PANEL_BLUEBLACK, 0.35))
    sd.poly([(cx, cy - 5.0), (cx + 2.5, cy - 2.2), (cx + 2.1, cy + 2.6), (cx, cy + 4.0),
             (cx - 2.2, cy + 2.6), (cx - 2.6, cy - 2.2)], fill=PANEL_BLUEBLACK)
    sd.poly([(cx - 0.2, cy - 4.2), (cx + 1.3, cy - 2.2), (cx - 0.4, cy + 1.2), (cx - 1.9, cy - 1.8)],
            fill=lit(PANEL_BLUEBLACK, 0.42))
    # Raised sensor/targeting turret amidships.
    sphere(sd, cx - 1.6, cy - 0.6, cx + 1.6, cy + 2.6, mix(LEGACY_GRAY, PANEL_BLUEBLACK, 0.45),
           steps=4, lit_f=0.42)
    sd.px(cx - 0.5, cy + 0.2, lit(LEGACY_GRAY, 0.45))
    # Tail flash + nose light on the remap ramp.
    sd.poly([(cx - 1.1, cy + 3.8), (cx + 1.1, cy + 3.8), (cx, cy + 5.4)], fill=SUN_GOLD)
    sd.px(cx, cy - 5.6, SUN_GOLD)


# ---------------------------------------------------------------------------
# Hauler Drone (SGHAU): the six-wheel unmanned scrap rover from the concept
# render (docs/concept-art/cameo-sources/desert_base2.png, the same subject its
# photographic cameo is cut from) -- a plated hull on three wheel pairs, a
# ploughed prow, and an open bed heaped with salvage.
#
# History: issue #34's follow-up moved SGHAU off HARV's Ore Truck sprite, and
# deliberately went *away* from a truck silhouette -- a hex sled on skids --
# so the two could never be confused again. That over-corrected: the sled read
# as a domed appliance with a green panel on it (a robot vacuum, in the
# player's words) rather than as the mod's harvester, and the cargo state was
# an abstract level bar rather than the load itself. This pass keeps the "not
# HARV" requirement but satisfies it the way the 3D concept does -- a wheeled
# rover, unmistakably a hauler, whose cargo is visible *scrap* rather than a
# gauge, and whose plan view (long, narrow, six wheels proud of the hull, open
# bed) is nothing like HARV's short boxy tracked body.
#
# Needs three parallel fullness-state images (empty/half/full) with an
# identical idle(32)/harvest(8)/dock(8)/dock-loop(7) frame layout across all
# three, matching WithHarvesterSpriteBody.ImageByFullness: harvempty, harvhalf,
# harv's convention -- the fullness itself is which image is active, not an
# animation baked into any one image's frames.
# ---------------------------------------------------------------------------

SGHAU_W, SGHAU_H = 34, 28
SGHAU_FULLNESS_FRAC = {"empty": 0.0, "half": 0.5, "full": 1.0}
_HAU_HULL = mix(LEGACY_GRAY, PANEL_BLUEBLACK, 0.42)   # plated chassis
_HAU_BED_X0, _HAU_BED_X1 = -3.2, 3.2                  # bed interior, from cx
_HAU_BED_Y0, _HAU_BED_Y1 = -2.0, 7.6                  # bed interior, from cy
_HAU_WHEEL_Y = (-6.4, 0.0, 6.4)                       # bogie centres, from cy


def _sghau_wheel(sd, cx, cy, side):
    """One road wheel seen from above: a dark tyre standing clear of the hull
    with a lit outer shoulder and two tread notches.

    Three a side, with real gaps between them, is what carries the rover read
    at 24px: the gaps are transparent, so the readability outline wraps each
    tyre separately and the six-wheel plan survives every facing. A tyre that
    only just clears the hull side is swallowed by that same outline."""
    x0, x1 = cx + side * 4.0, cx + side * 8.0
    sd.rect([min(x0, x1), cy - 2.0, max(x0, x1), cy + 2.0], fill=POLE_DARK)
    sd.line([(cx + side * 7.8, cy - 1.7), (cx + side * 7.8, cy + 1.7)],
            fill=lit(LEGACY_GRAY_DARK, 0.5), width=0.7)
    sd.px(cx + side * 6.0, cy, lit(LEGACY_GRAY, 0.2))
    for ty in (-1.0, 1.0):
        sd.line([(cx + side * 4.6, cy + ty), (cx + side * 7.4, cy + ty)],
                fill=lit(LEGACY_GRAY_DARK, 0.22), width=0.5)


def _sghau_scrap_col(x, y):
    """Scrap tone for a rover load: the Recycling Depot's own material palette
    (_rcyd_scrap_col, so a load and the pile it is tipped onto are made of the
    same stuff), broken up by a second hash. The depot's heap is 20px wide and
    its 7-step cycle reads as texture there; across a 7px bed the same cycle
    lines up into stripes, so a third of the pixels are re-rolled darker or
    left as shadow between the pieces."""
    k = (x * 13 + y * 29 + ((x * y) % 5)) % 11
    if k in (0, 7):
        return dim(LEGACY_GRAY_DARK, 0.1)
    if k == 4:
        return dim(RUST, 0.25)
    if k in (2, 9):
        return lit(LEGACY_GRAY, 0.42)
    return mix(_rcyd_scrap_col(x + (y % 3), y), LEGACY_GRAY, 0.45)


def _sghau_load(sd, cx, cy, frac):
    """The salvage in the bed, drawn as material rather than as a level bar.

    Filled from the tailgate forward. A full load overtops the bed rim and
    grows loose pipe and plate ends that break the hull outline -- the
    silhouette itself says laden, which is what has to read while the rover is
    driving away from you."""
    if frac <= 0:
        return
    x0, x1 = cx + _HAU_BED_X0, cx + _HAU_BED_X1
    y0, y1 = cy + _HAU_BED_Y0, cy + _HAU_BED_Y1
    over = 1.4 if frac >= 1.0 else 0.0      # heap overtopping the rim
    front = y1 - (y1 - y0 + over) * frac    # ragged leading edge of the load
    for x in range(int(math.floor(x0)), int(math.ceil(x1)) + 1):
        jag = ((x * 7 + 5) % 4) * 0.5       # broken, not a straight line
        for y in range(int(math.floor(front + jag)), int(math.ceil(y1)) + 1):
            sd.px(x, y, _sghau_scrap_col(x, y))
    # Long stock -- pipe, angle iron, a torn plate -- lying across the load.
    if frac >= 0.5:
        sd.line([(x0 - 0.5, y1 - 1.0), (x1 + 0.5, y1 - 3.0)], fill=lit(LEGACY_GRAY, 0.35), width=0.5)
    if frac >= 1.0:
        sd.line([(x0 - 1.8, y0 + 0.6), (x1 + 1.4, y0 - 1.0)], fill=lit(LEGACY_GRAY, 0.45), width=0.5)
        sd.line([(x0 + 0.6, y0 - 1.8), (x1 - 0.4, y0 + 2.2)], fill=dim(LEGACY_GRAY, 0.05), width=0.5)
        sd.poly([(x1 - 1.6, y0 - 1.6), (x1 + 2.0, y0 - 0.6), (x1 + 0.8, y0 + 1.4)], fill=RUST)


def sghau_draw(sd, w, h, fullness="full", pose="idle", light_on=True):
    cx, cy = w // 2, h // 2
    frac = SGHAU_FULLNESS_FRAC[fullness]
    # Six road wheels, drawn first so the hull plating overlaps their inner
    # shoulders and they read as running under it.
    for side in (-1, 1):
        for wy in _HAU_WHEEL_Y:
            _sghau_wheel(sd, cx, cy + wy, side)
    # Hull: a long plated chassis with a ploughed prow, lit along the port side
    # from the same top-left key light every other sprite here uses.
    hull = [(cx, cy - 11.0), (cx + 2.6, cy - 8.6), (cx + 4.2, cy - 6.2), (cx + 4.2, cy + 9.2),
            (cx - 4.2, cy + 9.2), (cx - 4.2, cy - 6.2), (cx - 2.6, cy - 8.6)]
    sd.poly(hull, fill=_HAU_HULL, outline=dim(_HAU_HULL, 0.45))
    sd.line([(cx - 3.8, cy - 6.0), (cx - 3.8, cy + 8.8)], fill=lit(_HAU_HULL, 0.45), width=0.7)
    sd.line([(cx - 3.0, cy - 8.0), (cx - 0.4, cy - 10.2)], fill=lit(_HAU_HULL, 0.38), width=0.6)
    sd.line([(cx + 3.7, cy - 5.6), (cx + 3.7, cy + 8.8)], fill=dim(_HAU_HULL, 0.35), width=0.6)
    # Prow plough: the blunt blade the rover shoves debris with, and the front
    # of the silhouette that says which way it is pointing.
    dy = -0.6 if pose == "idle" else 0.8
    sd.poly([(cx, cy - 12.0 - dy), (cx + 5.2, cy - 8.6 - dy), (cx + 4.4, cy - 7.2 - dy),
             (cx, cy - 9.8 - dy), (cx - 4.4, cy - 7.2 - dy), (cx - 5.2, cy - 8.6 - dy)],
            fill=dim(PANEL_BLUEBLACK, 0.1))
    sd.line([(cx - 5.2, cy - 8.6 - dy), (cx, cy - 12.0 - dy), (cx + 5.2, cy - 8.6 - dy)],
            fill=lit(PANEL_BLUEBLACK, 0.5), width=0.5)
    # Sensor/uplink block on the forward deck, ahead of the bed.
    box3d(sd, cx - 1.8, cy - 5.8, cx + 1.8, cy - 3.8, dim(PANEL_BLUEBLACK, 0.15), edge=0.28)
    sd.px(cx - 0.8, cy - 5.2, lit(LEGACY_GRAY, 0.25))
    # Open cargo bed: dark floor with cross ribs, so an *empty* rover still
    # reads as a load-carrier rather than a slab.
    bx0, bx1 = cx + _HAU_BED_X0, cx + _HAU_BED_X1
    by0, by1 = cy + _HAU_BED_Y0, cy + _HAU_BED_Y1
    sd.rect([bx0, by0, bx1, by1], fill=dim(PANEL_BLUEBLACK, 0.35))
    for ry in (1.2, 3.6, 6.0):
        sd.line([(bx0 + 0.5, by0 + ry), (bx1 - 0.5, by0 + ry)], fill=dim(_HAU_HULL, 0.5), width=0.4)
    _sghau_load(sd, cx, cy, frac)
    # Bed rim rails on the player-remap ramp: the team-coloured element. Full
    # flank-length strips rather than corner nubs (issue #86), so ownership
    # still reads at a glance under a full, overtopping load that could
    # otherwise swallow corner-only caps.
    for rx in (bx0 - 0.9, bx1 + 0.1):
        sd.rect([rx, by0 - 0.6, rx + 0.8, by1 - 0.4], fill=SUN_GOLD)
    # Working gear: the grapple arm swings out over the prow on the harvest and
    # dock poses. Opaque marks only -- a translucent field glow is deleted
    # outright by the 1-bit indexed alpha (issue #72).
    if pose != "idle":
        arm_y = cy - 10.4
        sd.line([(cx - 2.8, cy - 4.6), (cx - 1.8, arm_y)], fill=LEGACY_GRAY_DARK, width=0.8)
        sd.line([(cx + 2.8, cy - 4.6), (cx + 1.8, arm_y)], fill=LEGACY_GRAY_DARK, width=0.8)
        sd.line([(cx - 2.4, arm_y), (cx + 2.4, arm_y)], fill=GREEN_ACCENT, width=0.9)
        for gx in (-1.8, 0.0, 1.8):
            sd.px(cx + gx, arm_y - 1.4, lit(GREEN_ACCENT, 0.35))
    if light_on:
        sd.px(cx, cy - 9.2, SUN_GOLD)


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
# Disruptor Trooper (DISR): dedicated infantry art.
#
# History: issue #14 swapped Flame Infantry's name/weapon but kept e4.shp's
# chassis; issue #36 called that the same silhouette-identity mistake SGHAU had
# already been reversed for and generated a self-contained sheet here. That
# first sheet was built the way the vehicle/turret art in this file is -- draw
# ONE side-view figure 4x supersampled, then rotate it in the image plane for
# each of the 8 facings. Correct for a top-down drone or turret; badly wrong
# for infantry: issue #58's volumetric pass reshaded that figure without
# revisiting how the facings were produced, and a player rejected the result
# outright ("does not work out at all ... too bad to be taken seriously").
# Reviewing the shipped sheet against the stock art (docs/BACKLOG.md issue #64)
# found four separate faults, all of them structural:
#   * facings 1-7 were a side-view man ROTATED, so the trooper rendered lying
#     on his side or upside down in seven of eight directions,
#   * the figure was ~23px tall where every stock RA infantryman is ~15, and
#     its feet sat ~15px BELOW the frame centre -- so it drew roughly half a
#     cell south of where the actor actually stood, with the boots clipped off
#     the bottom edge of the frame entirely,
#   * 4x LANCZOS downscale + a full 1px outline + 1-bit indexed alpha turned
#     the interior into dither noise and the edges into a ragged blob,
#   * no shadow at all, so it floated over the terrain.
#
# This pass models it the way the stock sheets actually are, studied by
# decoding e6.shp against temperat.pal (a stand frame is ~95 pixels using ~10
# palette indices, ~9px wide and ~15px tall, no anti-aliasing anywhere):
#   * drawn at NATIVE resolution straight in palette indices (PC, above):
#     hard pixel edges, form carried by a small deliberate value ramp plus
#     selective near-black rim pixels, no all-round outline,
#   * ~14px tall with the boots ON the frame centre row -- stock infantry put
#     the feet at the canvas centre and leave the rest as slack (e6: body rows
#     5-19 of a 39px frame),
#   * a baked ShadowIndex-4 blob at the feet offset to the lower right, which
#     every stock infantry frame has (palettes.yaml: player palette
#     ShadowIndex: 4),
#   * the body mass on the 80-95 player-remap ramp, exactly as stock infantry
#     uniforms are, so ownership reads at a glance -- with the Disruptor's own
#     identity carried by FIXED bright accents the remap can't touch (gold
#     visor slit, backpack charge pips, forked electrode tips, electric-white
#     discharge). Issue #43 put only the gold accent on the remap ramp; on a
#     14px figure that left almost nothing team-coloured.
#   * all 8 facings drawn as actual viewpoints -- back, three-quarter, profile,
#     front -- upright in every one, with pack coverage, visor, shoulder width,
#     stride axis and weapon anchor all swapped per facing, and the draw order
#     flipped so the prod sits behind the body in the away-facing frames.
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
# Frame size (20x26) and the 437-frame layout are unchanged from the first
# pass, so mods/sungrid/sequences/infantry.yaml needs no edits.
# ---------------------------------------------------------------------------

DISR_W, DISR_H = 20, 26
DISR_CX = 9                  # figure centre column
DISR_GROUND = DISR_H // 2    # boots land on the frame centre row

# Vertical anatomy, measured off a decoded stock e6.shp stand frame: helmet 3
# rows, torso 7, legs 3, boots 1 -- 14 rows all in, ~6px wide. The first pass
# drew a 23-row figure, which towered over every other infantryman in the game.
DISR_HEAD_TOP = 0
DISR_TORSO_TOP = 3
DISR_TORSO_BOT = 9
DISR_HIP = 10

# Palette indices (temperat.pal), picked the way the stock infantry sheets pick
# theirs: body mass on the player-remap ramp, greys for hardware, one near
# black for rim/occlusion, fixed brights for the energy accents.
A_LIT, A_MID, A_SHD, A_DRK, A_DEEP = 82, 85, 89, 92, 94   # PlayerColorPalette remap
H_LIT, H_MID, H_SHD = 14, 13, 143               # helmet/hardware greys
RIM = 143                                       # (20,20,20) selective rim pixel
BOOT = 12                                       # pure black boot
PACK_LIT, PACK, PACK_DRK = 183, 17, 16          # discharge cell blue-blacks
GOLD, GOLD_LIT, GOLD_DRK = 212, 210, 213        # fixed gold accents
ARC, ARC_LIT = 192, 15                          # electric blue / white

# Frame 0 is north and frame indices advance counter-clockwise -- verified by
# decoding heli.shp, whose 32-facing sheet has frames 0/8/16/24 pointing
# N/W/S/E -- so the 8 facings run N, NW, W, SW, S, SE, E, NE. The y component
# is foreshortened: the camera looks down at the battlefield, so a step "south"
# covers less screen height than a step "west" covers width.
DISR_AIM = ((0.0, -1.0), (-0.8, -0.5), (-1.0, 0.0), (-0.8, 0.5),
            (0.0, 1.0), (0.8, 0.5), (1.0, 0.0), (0.8, -0.5))

# Torso extent per facing as (left, right) from the centre column: 5px across
# the shoulders front-on (stock e6 is 6 including its sleeves), one column
# narrower in profile where the far arm is hidden behind the near one.
DISR_TORSO_EXT = ((2, 2), (2, 2), (1, 2), (2, 2), (2, 2), (2, 2), (2, 1), (2, 2))

# How much of the discharge cell shows, as a box relative to (cx, torso top):
# across the upper back facing away, a bump behind the shoulder in profile, a
# one-column sliver on the three-quarter fronts, nothing head-on. Deliberately
# smaller than the first pass's, which covered the whole torso and turned the
# trooper into a black box with green legs.
# The box starts one row BELOW the shoulder line so the lit shoulder pixels
# always separate the (near-black) cell from the helmet -- with the cell flush
# to the shoulders the head read as sitting on a black brick.
DISR_PACK_BOX = {
    0: (-1, 1, 1, 3),
    1: (0, 2, 1, 3),
    7: (-2, 0, 1, 3),
    2: (1, 2, 1, 3),
    6: (-2, -1, 1, 3),
    3: (2, 2, 2, 3),
    5: (-2, -2, 2, 3),
    4: None,
}

# Prod geometry per facing, (x0, y0, x1, y1) relative to (cx, torso top): a
# 3-4px rod, the length a rifle gets on a stock RA infantry frame. Raised/
# aiming runs along the facing direction, foreshortened to a stub for the two
# head-on facings (0 aims away from the camera, 4 toward it) the way a real
# sprite sheet fakes depth.
# The grip x is kept inside the torso extent for that facing, so the weapon
# never floats a pixel clear of the body it is supposed to be held against.
DISR_ROD_READY = {
    0: (2, 1, 3, -1),
    1: (-2, 1, -4, -1),
    2: (-1, 2, -4, 1),
    3: (-2, 2, -4, 4),
    4: (2, 2, 3, 5),
    5: (2, 2, 4, 4),
    6: (1, 2, 4, 1),
    7: (2, 1, 4, -1),
}

# Lowered/at rest: same hand, tip swung down.
DISR_ROD_REST = {
    0: (2, 2, 3, 4),
    1: (-2, 2, -3, 5),
    2: (-1, 2, -3, 5),
    3: (-2, 3, -3, 5),
    4: (2, 3, 3, 5),
    5: (2, 3, 3, 5),
    6: (1, 2, 3, 5),
    7: (2, 2, 3, 4),
}


def _disr_shadow(c, cx=DISR_CX, ground=DISR_GROUND, wide=0, flat=False):
    """Baked ShadowIndex-4 blob at the feet, thrown to the lower right like
    every stock RA infantry frame's."""
    if flat:
        c.hline(cx - 4 - wide, cx + 4 + wide, ground, SHADOW_IDX)
        c.hline(cx - 3 - wide, cx + 5 + wide, ground + 1, SHADOW_IDX)
        return
    c.hline(cx - 2, cx + 2 + wide, ground, SHADOW_IDX)
    c.hline(cx - 1, cx + 3 + wide, ground + 1, SHADOW_IDX)
    c.hline(cx + 1, cx + 3 + wide, ground + 2, SHADOW_IDX)


def _disr_leg(c, x, top, bot, near=True):
    """One 2px leg: lit outer column, shaded inner, black boot. Legs sit a
    step or two down the ramp from the torso -- stock infantry are lighter up
    top and darker below, which is what gives them a waist at 5px wide."""
    c.vline(x, top, bot, A_SHD if near else A_DRK)
    c.vline(x + 1, top, bot, A_DRK if near else A_DEEP)
    c.hline(x, x + 1, bot + 1, BOOT)


def _disr_legs(c, facing, phase=None, cx=DISR_CX, ground=DISR_GROUND):
    """Two 2px legs meeting at the centre (stock legs are 4px wide with no gap),
    striding along the facing axis when phase is given."""
    hip = DISR_HIP
    bot = ground - 1
    ax, ay = DISR_AIM[facing]
    swing = 0.0 if phase is None else math.sin(phase * 2 * math.pi)
    dx = 1.6 * ax * swing            # lateral stride: full in profile
    dy = 1.0 * ay * swing            # walking toward/away: near leg reads longer
    lx, rx = -2 + dx, 0 - dx
    lbot = bot + (1 if dy > 0.4 else 0)
    rbot = bot + (1 if dy < -0.4 else 0)
    if swing == 0.0:
        order = ((rx, rbot, False), (lx, lbot, True))
    elif dx >= 0:
        order = ((lx, lbot, False), (rx, rbot, True))
    else:
        order = ((rx, rbot, False), (lx, lbot, True))
    for x, b, near in order:         # trailing leg first, leading one overlaps
        _disr_leg(c, cx + x, hip, min(bot, b), near=near)


def _disr_torso(c, facing, cx=DISR_CX, top=DISR_TORSO_TOP, bot=DISR_TORSO_BOT,
                pulse=0, arm_swing=0):
    """Armour torso: a 3px core with an arm column down each side, on the
    player-remap ramp so the mass of the unit carries the owner's colour the
    way stock infantry uniforms do."""
    left, right = DISR_TORSO_EXT[facing]
    for y in range(top, bot + 1):
        c.hline(cx - 1, cx + 1, y, A_MID)
        c.set(cx - 1, y, A_LIT)                            # top-left key light
        c.set(cx + 1, y, A_SHD)
    c.hline(cx - left, cx + right, top, A_LIT)             # lit shoulder line
    c.set(cx + right, top, A_MID)
    # Arms: grey armoured sleeves, not more of the body ramp. This is the trick
    # that makes a 5px-wide stock infantryman's shoulders read at all (e6 puts
    # light grey 0x0E down both sides of its khaki torso) -- with the arms on
    # neighbouring steps of the same ramp the whole figure was one flat lump.
    for side, ext in ((-1, left), (1, right)):
        if ext < 2:
            continue
        ax = cx + side * 2
        ay0 = top + 1 + (1 if side * arm_swing > 0 else 0)
        c.vline(ax, ay0, bot - 1, H_LIT if side < 0 else H_MID)
        c.set(ax, bot - 1, H_SHD)                          # glove, in shadow
    c.hline(cx - 1, cx + 1, bot, RIM)                      # belt: hard division
    if facing in (2, 3, 4, 5, 6):
        # Front-ish views: a spare charge cartridge on the hip, doing the job
        # e6's red toolbox does -- one small saturated non-remap mass so the
        # figure isn't a single flat colour from the front, plus the harness
        # pip that brightens on the animation pulse.
        hip_x = cx - 2 if facing in (5, 6) else cx + 2
        c.vline(hip_x, bot - 2, bot - 1, PACK)
        c.set(hip_x, bot - 2, GOLD if pulse % 4 < 2 else GOLD_DRK)
        c.set(cx, top + 2, GOLD_LIT if pulse % 4 < 2 else GOLD_DRK)


def _disr_pack(c, facing, cx=DISR_CX, top=DISR_TORSO_TOP, pulse=0):
    box = DISR_PACK_BOX[facing]
    if box is None:
        # Head-on: only the cell's top corners clear the shoulders.
        c.set(cx - 2, top, PACK_LIT)
        c.set(cx + 2, top, PACK)
        return
    x0, x1, y0, y1 = box
    # Filled on the lighter of the two cell tones: at 3px wide inside a 5px
    # torso, the near-black fill read as a hole punched through the trooper.
    c.box(cx + x0, top + y0, cx + x1, top + y1, PACK_LIT)
    c.hline(cx + x0, cx + x1, top + y0, H_SHD)             # lit top facet
    c.vline(cx + x1, top + y0, top + y1, PACK_DRK)         # shaded right edge
    # One charge pip, pulsing, so the cell reads as live hardware. (Two pips
    # plus a visor plus a nape coil just read as scattered orange pixels.)
    c.set(cx + x0, top + y0 + 1, GOLD_LIT if pulse % 4 < 2 else GOLD)


def _disr_head(c, facing, cx=DISR_CX, top=DISR_HEAD_TOP, turn=0.0):
    """3x3 helmet -- stock infantry heads are 3px wide; the first pass's 5px
    one gave the trooper a bobble head."""
    hx = cx + turn
    # A bright cap: stock infantry all carry their strongest value up here (e6's
    # yellow hard hat), which is what lets a 14px figure read at a glance.
    c.hline(hx - 1, hx + 1, top, H_LIT)                    # crown
    c.set(hx - 1, top, ARC_LIT)                            # key-light glint
    c.set(hx + 1, top, H_MID)
    c.hline(hx - 1, hx + 1, top + 1, H_MID)
    c.set(hx + 1, top + 1, H_SHD)
    c.hline(hx - 1, hx + 1, top + 2, H_SHD)                # jaw / neck shadow
    c.set(hx, top + 2, H_MID)
    if facing in (3, 4, 5):                                # visor toward us
        c.hline(hx - 1, hx, top + 1, GOLD)
        c.set(hx - 1, top + 1, GOLD_LIT)
    elif facing == 2:
        c.set(hx - 1, top + 1, GOLD)
    elif facing == 6:
        c.set(hx + 1, top + 1, GOLD)
    else:                                                  # back of the helmet
        c.set(hx, top + 1, H_LIT)
        c.set(hx + 1, top + 1, GOLD_DRK)                   # nape coil


def _disr_arc(c, x, y, level, seed=0, ax=1.0, ay=0.0):
    """Electric discharge off the electrodes: a short zigzag bolt along the
    aim direction plus a white core, rather than a symmetrical star."""
    if level <= 0:
        return
    c.set(x, y, ARC_LIT)
    px, py = x, y
    for i in range(2 + level):
        px += ax
        py += ay
        jitter = 1 if (seed + i) % 2 else -1
        if abs(ax) > abs(ay):
            py += jitter * (0.5 if i % 2 else -0.5)
        else:
            px += jitter * (0.5 if i % 2 else -0.5)
        c.set(px, py, ARC_LIT if i == 0 else ARC)
    if level > 1:
        c.set(x - ay, y + ax, ARC)
        c.set(x + ay, y - ax, ARC)


def _disr_rod(c, facing, pose, cx, torso_top, spark=0, seed=0):
    x0, y0, x1, y1 = (DISR_ROD_READY if pose in ("ready", "fire") else DISR_ROD_REST)[facing]
    gx, gy = cx + x0, torso_top + y0
    bx, by = cx + x1, torso_top + y1
    c.ray(gx, gy, bx, by, H_LIT)                           # light grey reads
    c.set(gx, gy, H_MID)                                   # grip, in shadow
    c.set(bx, by, GOLD_LIT if spark else GOLD)             # electrode
    if spark:
        ang = math.atan2(by - gy, bx - gx)
        _disr_arc(c, bx + round(math.cos(ang)), by + round(math.sin(ang)),
                  spark, seed, math.cos(ang), math.sin(ang))


def disr_upright(facing, pose="rest", phase=None, spark=0, turn=0.0, dy=0,
                 pulse=0, ground=DISR_GROUND, shadow=True, seed=0):
    """One upright trooper frame, drawn as an actual viewpoint for `facing`."""
    c = PC(DISR_W, DISR_H)
    cx = DISR_CX
    if shadow:
        _disr_shadow(c, cx, ground)
    torso_top = DISR_TORSO_TOP + dy
    torso_bot = DISR_TORSO_BOT + dy
    head_top = DISR_HEAD_TOP + dy
    away = facing in (0, 1, 7)
    arm_swing = 0 if phase is None else (1 if math.sin(phase * 2 * math.pi) > 0 else -1)
    if away:                                               # weapon behind body
        _disr_rod(c, facing, pose, cx, torso_top, spark, seed)
    _disr_legs(c, facing, phase, cx, ground)
    _disr_torso(c, facing, cx, torso_top, torso_bot, pulse, arm_swing)
    _disr_pack(c, facing, cx, torso_top, pulse)
    _disr_head(c, facing, cx, head_top, turn)
    if not away:
        _disr_rod(c, facing, pose, cx, torso_top, spark, seed)
    return c


def _disr_shoot(facing, p):
    """16-phase discharge: brief windup, bright arc, decay, then hold."""
    if p < 2:
        spark = 0
    elif p < 6:
        spark = 2
    elif p < 9:
        spark = 1
    else:
        spark = 0
    kick = -1 if 2 <= p < 4 else 0                         # recoil
    return disr_upright(facing, "fire", spark=spark, dy=kick, pulse=p, seed=p)


def disr_prone(facing, phase=None, shoot=None):
    """Prone/crawling trooper: the figure strung out along the facing axis,
    vertically foreshortened for the overhead camera."""
    c = PC(DISR_W, DISR_H)
    cx, ground = DISR_CX, DISR_GROUND
    _disr_shadow(c, cx, ground + 1, flat=True)
    ax, ay = DISR_AIM[facing]
    ox, oy = cx, ground - 1
    crawl = 0.0 if phase is None else math.sin(phase * 2 * math.pi)

    def at(t, lateral=0.0):
        return (ox + ax * t - ay * lateral * 1.2,
                oy + ay * t * 0.55 + ax * lateral * 0.6)

    # Legs trail behind, alternating on the crawl cycle.
    for s in (-1, 1):
        lx, ly = at(-3.4 - 0.6 * s * crawl, 0.8 * s)
        c.blob(lx, ly, 1.1, 1.0, A_SHD if s < 0 else A_DRK)
        c.set(lx, ly + 1, BOOT)
    for t, r, idx in ((-1.9, 1.4, A_SHD), (-0.2, 1.8, A_MID), (1.5, 1.5, A_LIT)):
        bx, by = at(t)
        c.blob(bx, by, r, r * 0.85, idx)
    # Discharge cell rides on the back, visible whenever the back is toward us.
    if facing in (0, 1, 7):
        px, py = at(0.2)
        c.blob(px, py, 1.2, 1.0, PACK)
        c.set(px, py - 1, PACK_LIT)
        c.set(px, py, GOLD if (shoot or 0) % 4 < 2 else GOLD_DRK)
    # Helmet at the leading end.
    hx, hy = at(3.2)
    c.blob(hx, hy, 1.5, 1.3, H_MID)
    c.set(hx - 1, hy - 1, H_LIT)
    c.set(hx + 1, hy + 1, H_SHD)
    if facing in (2, 3, 4, 5, 6):
        c.set(hx + (1 if ax > 0 else -1 if ax < 0 else 0), hy, GOLD)
    # Prod pushed forward past the head; arms are implied at this scale.
    gx, gy = at(2.0, 1.0)
    tx, ty = at(5.2, 0.8)
    c.ray(gx, gy, tx, ty, H_MID)
    c.set(tx, ty, GOLD)
    if shoot is not None:
        if shoot < 2:
            level = 0
        elif shoot < 6:
            level = 2
        elif shoot < 9:
            level = 1
        else:
            level = 0
        if level:
            sx, sy = at(6.4, 0.7)
            _disr_arc(c, round(sx), round(sy), level, shoot)
    return c


def _disr_dying(t, dir_sign, zap=False, keep=1.0):
    """Articulated collapse: the body chain rotates from upright to flat about
    the hips while the legs fold, instead of the first pass's whole-sprite
    image rotation (which just tipped a standing man over sideways)."""
    c = PC(DISR_W, DISR_H)
    cx, ground = DISR_CX, DISR_GROUND
    ease = t * t * (3 - 2 * t)
    # The shadow spreads as the body goes flat, then draws back in as the
    # corpse dissolves rather than dithering into loose speckle.
    _disr_shadow(c, cx, ground, wide=round(3 * ease * max(0.0, keep * 2 - 1)),
                 flat=ease > 0.65 and keep > 0.5)
    theta = math.radians(90 * (1 - ease))
    hip_x = cx + dir_sign * 2.6 * ease
    hip_y = ground - 3.0 * (1 - ease) - 0.5
    dx, dy = dir_sign * math.cos(theta), -math.sin(theta)
    # Legs fold under the hips.
    for s in (-1, 1):
        lx = hip_x - dir_sign * 2.0 * ease + s * 1.1
        ly = min(ground - 0.5, hip_y + 2.6 * (1 - ease) + 1.2 * ease)
        c.blob(lx, ly, 1.1, 1.0, A_SHD)
        c.set(lx, min(ground, ly + 1.2), BOOT)
    for d, r, idx in ((2.0, 1.6, A_MID), (4.0, 1.5, A_MID), (5.6, 1.3, A_LIT)):
        c.blob(hip_x + dx * d, hip_y + dy * d, r, r * 0.85, idx)
    hx, hy = hip_x + dx * 7.3, hip_y + dy * 7.3
    c.blob(hx, hy, 1.5, 1.3, H_MID)
    c.set(hx - 1, hy - 1, H_LIT)
    c.set(hx + 1, hy + 1, H_SHD)
    c.set(hx, hy + 1, GOLD_DRK)
    # The prod slips from the hands and lands beside the body.
    if ease < 0.5:
        c.ray(hip_x + dx * 4, hip_y + dy * 4 + 1, hip_x + dir_sign * 5, ground - 1, H_MID)
    else:
        c.hline(hip_x + dir_sign * 3, hip_x + dir_sign * 6, ground - 1, H_MID)
        c.set(hip_x + dir_sign * 6, ground - 1, GOLD_DRK)
    if zap:
        # Electrocution flicker: the discharge earths itself through the body.
        step = round(t * 12)
        for i, (ox, oy) in enumerate(((-2, -4), (2, -6), (0, -2), (3, -3), (-3, -1))):
            if (step + i) % 2 == 0:
                c.set(cx + ox, ground - 1 + oy, ARC_LIT if i % 2 else ARC)
    if keep < 1.0:
        c.dissolve(keep)
    return c


def _disr_die_frames(n, dir_sign, zap=False, dissolve_from=None):
    out = []
    for i in range(n):
        t = i / max(1, n - 1)
        keep = 1.0
        if dissolve_from is not None and t > dissolve_from:
            keep = 1.0 - (t - dissolve_from) / (1.0 - dissolve_from)
        out.append(_disr_dying(t, dir_sign, zap=zap, keep=keep))
    return out


def disr_parachute():
    """Airborne drop frame: canopy up top, trooper slung below it."""
    ground = 21
    c = disr_upright(4, "rest", dy=8, ground=ground, shadow=False)
    cx = DISR_CX
    c.hline(cx - 3, cx + 3, 1, GOLD_LIT)                   # canopy crown
    c.hline(cx - 5, cx + 5, 2, GOLD)
    c.hline(cx - 6, cx + 6, 3, GOLD_DRK)
    c.set(cx - 5, 2, GOLD_LIT)
    c.set(cx + 5, 2, GOLD_DRK)
    c.set(cx - 6, 4, GOLD_DRK)                             # skirt corners
    c.set(cx + 6, 4, GOLD_DRK)
    c.ray(cx - 5, 4, cx - 1, 8, H_MID)                     # shrouds
    c.ray(cx + 5, 4, cx + 1, 8, H_MID)
    return c


def _disr_idle1(i):
    """Sentry scan: the trooper checks left and right, cell pips pulsing."""
    turn = (0, 0, -1, -1, -1, 0, 0, 0, 1, 1, 1, 1, 0, 0)[i % 14]
    facing = 3 if turn < 0 else 5 if turn > 0 else 4
    return disr_upright(facing, "rest", turn=turn * 0.0, pulse=i)


def _disr_idle2(i):
    """Prod check: weapon comes up, an arc runs across the electrodes, down."""
    if i < 3 or i >= 13:
        return disr_upright(4, "rest", pulse=i)
    spark = 2 if 6 <= i <= 8 else 1 if 5 <= i <= 10 else 0
    return disr_upright(4, "fire" if spark else "ready", spark=spark, pulse=i, seed=i)


def disr_frames():
    frames = []
    # stand / stand2: one frame per facing, weapon lowered then ready.
    for pose in ("rest", "ready"):
        frames += [disr_upright(f, pose) for f in range(8)]
    # run: 6 walk-cycle poses per facing, with a 1px body bob.
    for f in range(8):
        for p in range(6):
            frames.append(disr_upright(f, "ready", phase=p / 6,
                                       dy=-1 if p % 3 == 1 else 0))
    # shoot: 16 poses per facing.
    for f in range(8):
        frames += [_disr_shoot(f, p) for p in range(16)]
    # prone-run: 4 crawl poses per facing (prone-stand/-stand2 reuse these
    # via Stride in the sequence YAML).
    for f in range(8):
        frames += [disr_prone(f, phase=p / 4) for p in range(4)]
    # prone-shoot: 16 poses per facing.
    for f in range(8):
        frames += [disr_prone(f, shoot=p) for p in range(16)]
    # idle1/idle2: single-direction loops, drawn front-on since the sequence
    # has no Facings key and plays whatever way the unit is turned.
    frames += [_disr_idle1(i) for i in range(14)]
    frames += [_disr_idle2(i) for i in range(16)]
    # die1-5: collapse forward, backward, then three electrocution variants
    # that dissolve out over their longer runs.
    frames += _disr_die_frames(8, 1)
    frames += _disr_die_frames(8, -1)
    frames += _disr_die_frames(8, 1, zap=True)
    frames += _disr_die_frames(12, -1, zap=True, dissolve_from=0.6)
    frames += _disr_die_frames(18, 1, zap=True, dissolve_from=0.45)
    frames.append(disr_parachute())
    return frames


# ---------------------------------------------------------------------------
# Sheet assembly: cameo-style sidebar icons. (The two-frame idle+damaged
# building sheet is assembled inline in main() now, since issue #74's build-up
# strip needs the idle frame itself, not just the finished sheet.)
# ---------------------------------------------------------------------------

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
    "sgvlt": "Battery Bank",
    "rcyd": "Recycling Depot",
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


_LABEL_BAND_PAD = 2
_LABEL_BAND_CEILING_SIZE = 8

# The in-game production palette (ProductionPaletteWidget, IconSize 62x46)
# draws these 64x48 cameos centered in a cell 2px smaller than the sprite in
# both dimensions, so a few rows at the very bottom edge are cropped off in
# the live sidebar even though they're fully visible in the standalone
# generator output (see docs/BACKLOG.md issue #61 -- reported as "Barracks/
# War Factory subtitle not visible, others slightly moved up"). Reserve a
# real safety margin, not just the 1px the widget math implies, since the
# exact clip boundary isn't worth re-deriving pixel-by-pixel here.
_LABEL_BOTTOM_CLEARANCE = 4

# Band geometry (height, and thus how far down the darkening strip starts) is
# fixed to the ceiling font size's metrics, independent of which size a given
# label ends up using -- otherwise a long name that has to drop to a smaller
# size to fit on one line (e.g. "Adv Solar Array") gets a shorter band than
# its neighbors, which reads as that cameo's motif being vertically shifted
# relative to the rest of the row.
_LABEL_BAND_H = (
    _load_label_font(_LABEL_BAND_CEILING_SIZE).getbbox("AGY")[3]
    - _load_label_font(_LABEL_BAND_CEILING_SIZE).getbbox("AGY")[1]
) + _LABEL_BAND_PAD * 2


def draw_icon_label(icon, text):
    """Bake an uppercase name as a single white line across the bottom of a
    cameo, matching the ported stock RA cameos (BARRACKS / ORE REFINERY / ...):
    one line, white text, over a thin dark strip. Picks the largest FreeSansBold
    size (8px down to 5px) whose single-line width fits, so even long names stay
    on one line the way the stock cameos do, and draws a 1px shadow under the
    text so it reads over any motif or photo. The strip itself is always
    _LABEL_BAND_H tall and sits 1px clear of the very bottom edge (see
    _LABEL_BAND_H's docstring) regardless of which size wins, so every cameo's
    band -- and the motif crop above it -- lines up row to row.
    """
    text = text.upper()
    d = ImageDraw.Draw(icon, "RGBA")
    max_w = ICON_W - 3
    # Largest size that fits on ONE line; keep the smallest as a last resort.
    # Ceiling matches the ported stock cameos (BARRACKS / ORE REFINERY) so the
    # short Sungrid names don't tower over their neighbors in the sidebar.
    font = _load_label_font(5)
    for size in (8, 7, 6, 5):
        f = _load_label_font(size)
        if d.textlength(text, font=f) <= max_w:
            font = f
            break
        font = f
    bbox = d.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    band_h = _LABEL_BAND_H
    band_top = ICON_H - band_h - _LABEL_BOTTOM_CLEARANCE
    # Thin dark strip behind the single line for legibility over any motif.
    strip = Image.new("RGBA", (ICON_W, band_h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(strip, "RGBA")
    for i in range(band_h):
        a = int(150 * (i / max(1, band_h - 1)) + 50)
        sd.line([(0, i), (ICON_W, i)], fill=PANEL_BLUEBLACK + (min(215, a),))
    icon.alpha_composite(strip, (0, band_top))
    x = (ICON_W - tw) / 2 - bbox[0]
    y = band_top + (band_h - th) / 2 - bbox[1]
    d.text((x + 1, y + 1), text, font=font, fill=(0, 0, 0, 220))  # shadow
    d.text((x, y), text, font=font, fill=(255, 255, 255, 255))
    return icon


def make_icon(draw_fn, frame_w, frame_h, *args, label=None, **kwargs):
    """Sidebar cameo: the motif cropped tight and fitted onto a shaded panel
    with a border, instead of a transparent whole-frame downscale."""
    # Render the motif at SS resolution and crop to content for a crisp fit.
    big = Image.new("RGBA", (frame_w * SS, frame_h * SS), (0, 0, 0, 0))
    draw_fn(SD(big), frame_w, frame_h, *args, **kwargs)
    return make_icon_from_motif(big, label=label)


def make_icon_from_motif(big, label=None):
    """Panel/border/label half of make_icon, for motifs that are already
    rendered (the infantry art is authored at native resolution in palette
    indices, so it is upscaled with NEAREST rather than drawn at SS scale)."""
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


# ---------------------------------------------------------------------------
# Sprite *states*: build-up, death rubble, vehicle husk (issue #74).
#
# Every pass up to here drew a better *picture*. This one draws the states the
# engine already asks each actor for and which were still being answered with
# another actor's art (or with nothing at all):
#
#   - `make:`  every Sungrid building held a single frame, so it popped in
#              fully formed while every ported stock building next to it rose
#              out of the ground over ~9 frames.
#   - `dead:`  the three buildings that have one pointed at stock RA rubble
#              (powrdead.shp / apwrdead.shp).
#   - husks    the Hauler Drone left an Ore Truck wreck -- the exact sprite
#              issue #34's follow-up gave it dedicated art to stop colliding
#              with -- and the two drones left a Chinook and a Black Hawk.
#
# Shadows here are derived from the frame's own silhouette rather than drawn:
# indexed_strip only writes SHADOW_IDX where the body is transparent, so an
# offset copy of the silhouette leaves exactly the 1-3px down-right rim that
# decoding fact.shp showed stock buildings use (issue #73). Unlike a finished
# building, a wreck genuinely leaves terrain visible around itself, so it gets
# one -- and the stock art agrees: powrdead.shp is 789 opaque pixels with 77
# of them ShadowIndex, hhusk2.shp bakes one per facing.
# ---------------------------------------------------------------------------

MAKE_FRAMES = 9   # matches stock fcommake.shp's 9; gapmake.shp runs 13


def silhouette_shadow(frame, dx=2, dy=2):
    """Ground-shadow stencil for indexed_strip: the frame's own 1-bit
    silhouette, offset down-right."""
    solid = frame.getchannel("A").point(lambda v: 255 if v >= 128 else 0)
    mask = Image.new("L", frame.size, 0)
    mask.paste(solid, (dx, dy))
    return mask


def construction_tint(img):
    """Bare, unpowered structure: RA's *make.shp frames are monochrome until
    the last one, so a building only takes its colours -- and, here, its
    owner's, since the gold accents live on the player-remap ramp -- at the
    moment it finishes. Greys are far from the gold reference ramp, so
    _index_for lands them on fixed palette entries and nothing in a
    half-built structure is team-coloured."""
    px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = px[x, y]
            if a < 8:
                continue
            lum = 0.30 * r + 0.59 * g + 0.11 * b
            v = min(255, int(lum * 0.80) + 12)
            px[x, y] = (v, v, v, a)
    return img


def make_frames(draw_fn, w, h, final=None, n=MAKE_FRAMES, **kwargs):
    """Build-up strip: the finished mass rising out of the ground, anchored on
    the sprite's own contact row, monochrome until the final frame.

    Deliberately a bottom-anchored vertical scale of the finished sprite
    rather than a hand-drawn scaffold sequence -- that is what stock RA's own
    build-up reads as (decoding fcommake.shp shows frame 1 is a squat version
    of the whole building, base included, growing to full height with a
    constant footprint width), and it keeps the 15 build-ups here in step with
    their draw functions automatically instead of needing 15 more of them.

    `final` overrides the last frame for actors whose shipped idle frame is not
    a plain render() of draw_fn (sgrel re-stamps its accents at native
    resolution; arct carries a baked shadow), so construction completing never
    shows a one-frame pop."""
    big = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
    draw_fn(SD(big), w, h, **kwargs)
    bbox = big.getbbox()
    base_y = bbox[3] if bbox else big.height
    mass = big.crop((0, 0, big.width, base_y))
    frames = []
    for i in range(n - 1):
        t = (i + 1) / n
        mh = max(SS, round(mass.height * t))
        f = Image.new("RGBA", big.size, (0, 0, 0, 0))
        f.paste(mass.resize((mass.width, mh), Image.LANCZOS), (0, base_y - mh))
        frames.append(construction_tint(f.resize((w, h), Image.LANCZOS)))
    frames.append(final if final is not None else render(draw_fn, w, h, **kwargs))
    return frames


# --- Death rubble ----------------------------------------------------------
#
# Stock building rubble (powrdead.shp/apwrdead.shp, decoded here) is a single
# frame -- no concrete pad, because WithBuildingBib keeps drawing the bib
# underneath -- of collapsed mass with a few remap-ramp pixels still in it, so
# the wreck reads as still having been someone's. Same grammar below, with two
# or three recognisable pieces of the original building left in the pile so
# you can tell what you just killed.

def _rubble_bed(sd, x0, x1, y0, y1, seed):
    """Mound of collapsed structure, built column by column so the crest is
    jagged and the ends taper into shoulders.

    Drawn as broken *material* rather than one dark polygon: a solid silhouette
    the size of a building footprint reads as a black box at RTS zoom, whereas
    stock rubble (powrdead.shp decoded) is a chaotic mid-tone mass with lit
    edges catching all through it."""
    span = max(1, int(x1 - x0))
    # One solid mass under a wandering crest line, then tonal variation laid
    # *across* it as short broken blocks. Varying the tone per full-height
    # column instead reads as a picket fence, and a jagged silhouette also
    # lets the SHADOW_IDX rim show through the gaps.
    crest = []
    for i in range(span + 1):
        n = ((i * 37 + seed * 53) % 17) / 16.0
        m = ((i * 11 + seed * 29) % 7) / 6.0
        rise = (y1 - y0) * (0.70 + 0.30 * (0.55 * n + 0.45 * m))
        shoulder = min(1.0, min(i, span - i) / max(1.0, span * 0.10))
        crest.append((x0 + i, y1 - rise * shoulder))
    sd.poly([(x0, y1)] + crest + [(x1, y1)], fill=dim(CONCRETE, 0.12))
    tones = (LEGACY_GRAY_DARK, lit(CONCRETE, 0.12), DAMAGE_SCORCH, dim(CONCRETE, 0.42))
    for k in range(span // 2):
        bx = x0 + (k * 13 + seed * 7) % max(1, span - 4)
        by = crest[min(len(crest) - 1, int(bx - x0))][1]
        by += 1 + (k * 5 + seed) % max(1, int(y1 - by) - 1)
        bw = 2 + (k + seed) % 3
        sd.rect([bx, by, bx + bw, by + 1], fill=tones[(k + seed) % 4])
    # Lit crest, so the top edge catches the key light like broken slab does.
    for i in range(0, span, 2):
        sd.px(crest[i][0], crest[i][1], lit(CONCRETE, 0.3))
    # Charred pockets where the fire burned through, kept shallow: deep round
    # blobs on the lower edge read as holes in the sprite, not as soot.
    for k in range(2):
        cxp = x0 + span * (0.34 + 0.3 * k)
        sd.ellipse([cxp - 4, y1 - 3.5, cxp + 4, y1 - 1.5], fill=DAMAGE_SCORCH)


def _slab(sd, cx, cy, wid, hgt, col, lean=0.0):
    """One canted slab of debris, lit along its upper edge."""
    pts = [(cx - wid / 2, cy + hgt / 2 + lean), (cx - wid / 2 + 1.5, cy - hgt / 2),
           (cx + wid / 2, cy - hgt / 2 - lean), (cx + wid / 2 - 1.5, cy + hgt / 2)]
    sd.poly(pts, fill=col)
    sd.line([pts[1], pts[2]], fill=lit(col, 0.32), width=0.6)


def _embers(sd, spots):
    for i, (x, y) in enumerate(spots):
        sd.px(x, y, RUST if i % 2 else lit(RUST, 0.35))


def _conduit_stub(sd, x0, x1, y):
    """Severed length of the gold conduit band -- the remap-ramp pixels that
    keep the wreck legible as the owner's, matching stock rubble."""
    sd.rect([x0, y, x1, y + 1.6], fill=dim(SUN_GOLD, 0.4))
    sd.line([(x0, y), (x1, y)], fill=dim(SUN_GOLD, 0.15))


def sgpwr_dead_draw(sd, w=FAM23_W, h=FAM23_H):
    """Solar Array rubble: both collector surfaces down, one still leaning on
    its snapped strut."""
    gy = h - 12
    _rubble_bed(sd, 8, w - 8, gy - 2, gy + 7, seed=11)
    # Collapsed collectors: one flat in the ash, one canted on a bent strut.
    _slab(sd, 22, gy - 4, 22, 5, mix(PANEL_BLUEBLACK, LEGACY_GRAY, 0.35), lean=0.8)
    _slab(sd, 44, gy - 8, 18, 5, dim(PANEL_BLUEBLACK, 0.2), lean=-3.2)
    sd.line([(38, gy - 6), (41, gy - 1)], fill=POLE_DARK, width=1.1)
    sd.line([(52, gy - 5), (49, gy - 1)], fill=POLE_DARK, width=1.0)
    _conduit_stub(sd, 12, 26, gy - 2)
    _embers(sd, [(20, gy - 3), (33, gy - 2), (48, gy - 3), (27, gy - 5)])


def sgapwr_dead_draw(sd, w=FAM33_W, h=FAM33_H):
    """Advanced Solar Array rubble: a wider spill, with the storage cell burst
    open in the middle of it."""
    gy = h - 13
    _rubble_bed(sd, 6, w - 6, gy - 2, gy + 8, seed=12)
    _slab(sd, 22, gy - 4, 24, 5, mix(PANEL_BLUEBLACK, LEGACY_GRAY, 0.35), lean=1.0)
    _slab(sd, 66, gy - 5, 22, 5, dim(PANEL_BLUEBLACK, 0.2), lean=-2.4)
    _slab(sd, 45, gy - 9, 14, 6, dim(LEGACY_GRAY, 0.25), lean=-1.2)
    for x in (34, 58):
        sd.line([(x, gy - 7), (x + 3, gy - 1)], fill=POLE_DARK, width=1.1)
    _conduit_stub(sd, 10, 30, gy - 2)
    _conduit_stub(sd, 60, 74, gy - 3)
    _embers(sd, [(24, gy - 3), (45, gy - 6), (63, gy - 3), (37, gy - 2), (71, gy - 4)])


def sghyd_dead_draw(sd, w=FAM33_W, h=FAM33_H):
    """Hydrogen Plant rubble: both cylinders split and toppled, hoops sprung
    clear of the shells -- the outline says 'tank', not 'generic pile'."""
    gy = h - 13
    _rubble_bed(sd, 6, w - 6, gy - 2, gy + 8, seed=9)
    steel = mix(LEGACY_GRAY, PANEL_BLUEBLACK, 0.25)
    # Toppled cylinders, seen end-on and flank-on.
    sd.ellipse([12, gy - 11, 34, gy - 2], fill=dim(steel, 0.3))
    sd.ellipse([15, gy - 9.5, 31, gy - 4], fill=dim(PANEL_BLUEBLACK, 0.15))
    sd.arc([12, gy - 11, 34, gy - 2], 190, 350, fill=lit(steel, 0.2), width=0.7)
    _slab(sd, 62, gy - 6, 30, 8, dim(steel, 0.15), lean=1.6)
    sd.line([(48, gy - 9), (76, gy - 7)], fill=dim(steel, 0.45), width=0.8)
    # Sprung hoops, still gold.
    sd.arc([44, gy - 10, 62, gy - 1], 200, 20, fill=dim(SUN_GOLD, 0.35), width=1.1)
    _conduit_stub(sd, 30, 44, gy - 2)
    _embers(sd, [(23, gy - 6), (52, gy - 4), (68, gy - 5), (38, gy - 2), (60, gy - 8)])


# --- Hauler Drone husk -----------------------------------------------------

def sghau_husk_draw(sd, w, h, laden=False):
    """Wrecked Hauler Drone: the rover burnt out and sitting on its rims, the
    prow plough torn off at the mounts, one bogie sprung out of line and the
    bed split open.

    Its own silhouette rather than HARV's (hhusk2.shp): a Hauler Drone that
    dies into an Ore Truck wreck undoes exactly the identity issue #34's
    follow-up pass was for. Redrawn with the intact rover (see sghau_draw) so
    the wreck is recognisably the same vehicle -- a burnt hex sled left behind
    by a six-wheeled rover reads as a different unit's husk."""
    cx, cy = w // 2, h // 2
    # Burnt metal, not black: a 14px wreck under a 1px dark outline has no
    # room to lose contrast, and stock hhusk2.shp is a mid-tone scorched olive
    # rather than a silhouette.
    char = mix(dim(LEGACY_GRAY, 0.22), RUST, 0.22)
    # Wheels: the middle pair blown clear on one side, the rest sitting flat.
    for side in (-1, 1):
        for k, wy in enumerate(_HAU_WHEEL_Y):
            if side < 0 and k == 1:
                continue
            x0, x1 = cx + side * 4.0, cx + side * (7.4 if k != 2 else 6.8)
            sd.rect([min(x0, x1), cy + wy - 1.7, max(x0, x1), cy + wy + 1.7],
                    fill=dim(POLE_DARK, 0.1))
    # The sprung wheel, off the hull and canted.
    sd.poly([(cx - 10.4, cy - 1.6), (cx - 7.2, cy - 0.4), (cx - 7.8, cy + 2.6),
             (cx - 11.0, cy + 1.4)], fill=POLE_DARK)
    # Hull, canted: the near-side plating collapses, so the chassis reads bent.
    sd.poly([(cx + 0.6, cy - 10.2), (cx + 3.0, cy - 8.0), (cx + 4.2, cy - 5.6),
             (cx + 3.6, cy + 9.0), (cx - 4.4, cy + 8.6), (cx - 4.0, cy - 6.0),
             (cx - 2.0, cy - 8.4)], fill=char)
    sd.line([(cx - 3.6, cy - 5.6), (cx - 3.2, cy + 8.0)], fill=lit(char, 0.26), width=0.6)
    # Buckled deck plate peeled up out of the forward hull.
    sd.poly([(cx - 1.6, cy - 7.0), (cx + 2.6, cy - 5.6), (cx + 1.8, cy - 3.0),
             (cx - 2.2, cy - 4.4)], fill=dim(char, 0.3))
    sd.line([(cx - 1.6, cy - 7.0), (cx + 2.6, cy - 5.6)], fill=lit(char, 0.4), width=0.5)
    # Torn plough mounts: two bent stubs where the blade used to sit.
    sd.line([(cx - 3.4, cy - 8.6), (cx - 5.2, cy - 10.6)], fill=lit(char, 0.15), width=0.9)
    sd.line([(cx + 2.6, cy - 9.0), (cx + 4.0, cy - 11.2)], fill=lit(char, 0.15), width=0.9)
    # Cargo bed, split down the near side: the breach is the dark, the hull
    # around it stays readable.
    sd.rect([cx - 3.4, cy - 2.0, cx + 3.0, cy + 7.6], fill=dim(char, 0.42))
    sd.poly([(cx - 1.8, cy - 1.0), (cx + 2.2, cy - 0.2), (cx + 1.6, cy + 6.6), (cx - 2.2, cy + 6.0)],
            fill=DAMAGE_SCORCH)
    if laden:
        # The load it was carrying, part burnt in the bed and part thrown out
        # over the tailgate -- the laden/empty split has to read from the
        # wreck the same way it read from the rover.
        for x in range(int(cx - 2), int(cx + 3)):
            for y in range(int(cy + 1), int(cy + 7)):
                if (x * 5 + y * 3) % 3:
                    sd.px(x, y, mix(_sghau_scrap_col(x, y), DAMAGE_SCORCH, 0.35))
        for i, (dx, dy) in enumerate(((6.0, 8.0), (-6.0, 9.0), (2.5, 10.5), (-2.0, 9.5))):
            sd.rect([cx + dx, cy + dy, cx + dx + 1.2, cy + dy + 0.8],
                    fill=RUST if i % 2 else dim(LEGACY_GRAY, 0.2))
    # A little scattered wreckage, kept tight to the hull: isolated single
    # pixels each pick up their own shadow rim and read as speckle.
    for i, (dx, dy) in enumerate(((-9.5, -6.5), (9.0, 6.5), (-1.0, -11.5))):
        sd.rect([cx + dx, cy + dy, cx + dx + 1, cy + dy + 0.6],
                fill=LEGACY_GRAY_DARK if i % 2 else dim(char, 0.4))
    _embers(sd, [(cx - 2, cy - 4), (cx + 3, cy + 4)])


def sghau_husk_frames(laden):
    """32 facings, matching the intact sled's layout and hhusk2.shp's own."""
    bodies = rotated_frames(sghau_husk_draw, SGHAU_W, SGHAU_H, 32, laden=laden)
    return bodies, [silhouette_shadow(b, 1, 1) for b in bodies]


# Buildings that bake a cast shadow into their sprite the way the stock art
# does. The rest of the roster still has none -- a deliberate follow-up, not
# an oversight (docs/BACKLOG.md issue #65).
SHADOW_DRAWS = {"arct": lambda sd, w, h, damaged=False: arct_shadow_draw(sd, w, h, damaged)}

# Cameos whose motif is not simply the body sheet's draw function (the Arc
# Turret's body is only its pedestal now that the head rotates separately).
ICON_DRAWS = {"arct": arct_icon_draw}

# Buildings whose team-coloured pixels have to be re-stamped at native
# resolution after the supersampled downscale (see _sgrel_accents).
ACCENT_FRAMES = {"sgrel": sgrel_frame}


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
        idle_shadow = None
        if name in ACCENT_FRAMES:
            frames = [ACCENT_FRAMES[name](damaged=d) for d in (False, True)]
            sheet = sheet_of(frames, w, h)
            idle = frames[0]
        elif name in SHADOW_DRAWS:
            # Buildings whose sprite carries a baked ground shadow have to go
            # through indexed_strip so SHADOW_IDX survives (see its docstring).
            bodies = [render(draw_fn, w, h, damaged=d) for d in (False, True)]
            shadows = [render_shadow_mask(SHADOW_DRAWS[name], w, h, damaged=d) for d in (False, True)]
            sheet = indexed_strip(bodies, shadows, w, h)
            idle, idle_shadow = bodies[0], shadows[0]
        else:
            idle = render(draw_fn, w, h, damaged=False)
            sheet = sheet_of([idle, render(draw_fn, w, h, damaged=True)], w, h)
        save_pngsheet(sheet, f"{name}.png", w, h, 2, indexed=True)
        icon = make_icon(ICON_DRAWS.get(name, draw_fn), w, h, label=ICON_LABELS.get(name))
        save_pngsheet(icon, f"{name}icon.png", ICON_W, ICON_H, 1)

        # Build-up (issue #74): the structure rising out of the ground, ending
        # on this sheet's own idle frame so completion never pops.
        mk = make_frames(draw_fn, w, h, final=idle)
        mk_shadows = [None] * (len(mk) - 1) + [idle_shadow]
        save_pngsheet(indexed_strip(mk, mk_shadows, w, h), f"{name}make.png",
                      w, h, len(mk), indexed=True)

    # Battery Bank (the Grid Reserve Vault): one strip of 9 charge stages
    # followed by 9 damaged charge stages, which is what `stages:` /
    # `damaged-stages:` index into.
    vlt = [sgvlt_frame(damaged=dmg, charge=stage)
           for dmg in (False, True) for stage in range(SGVLT_STAGES)]
    save_pngsheet(sheet_of(vlt, SG1x1_W, SG1x1_H), "sgvlt.png",
                  SG1x1_W, SG1x1_H, len(vlt), indexed=True)
    save_pngsheet(make_icon(sgvlt_draw, SG1x1_W, SG1x1_H, label=ICON_LABELS["sgvlt"]),
                  "sgvlticon.png", ICON_W, ICON_H, 1)
    # Build-up ends on charge stage 0 -- a Battery Bank comes online empty,
    # which is also the frame the `make:` sequence used to hold on its own.
    vlt_mk = make_frames(sgvlt_draw, SG1x1_W, SG1x1_H, final=sgvlt_frame(charge=0), charge=0)
    save_pngsheet(sheet_of(vlt_mk, SG1x1_W, SG1x1_H), "sgvltmake.png",
                  SG1x1_W, SG1x1_H, len(vlt_mk), indexed=True)

    # Recycling Depot: same layout as the Battery Bank -- 9 fill stages then 9
    # damaged fill stages, indexed by `stages:` / `damaged-stages:`. The cameo
    # written here is the programmatic fallback; gen_photo_cameos.py overwrites
    # it with the photographic one (issue #47), same as every other actor.
    rcy = [rcyd_frame(damaged=dmg, charge=stage)
           for dmg in (False, True) for stage in range(RCYD_STAGES)]
    save_pngsheet(sheet_of(rcy, SG1x1_W, SG1x1_H), "rcyd.png",
                  SG1x1_W, SG1x1_H, len(rcy), indexed=True)
    save_pngsheet(make_icon(rcyd_draw, SG1x1_W, SG1x1_H, label=ICON_LABELS["rcyd"]),
                  "rcydicon.png", ICON_W, ICON_H, 1)
    rcy_mk = make_frames(rcyd_draw, SG1x1_W, SG1x1_H, final=rcyd_frame(charge=0), charge=0)
    save_pngsheet(sheet_of(rcy_mk, SG1x1_W, SG1x1_H), "rcydmake.png",
                  SG1x1_W, SG1x1_H, len(rcy_mk), indexed=True)

    # Arc Turret: the head is its own 32-facing turret sprite (issue #66), so
    # arct.png above is the pedestal alone and this is what rotates on top.
    arct_idle, arct_idle_sh = arct_turret_frames(damaged=False)
    arct_dmg, arct_dmg_sh = arct_turret_frames(damaged=True)
    save_pngsheet(indexed_strip(arct_idle + arct_dmg, arct_idle_sh + arct_dmg_sh,
                                SG1x1_W, SG1x1_H),
                  "arctturret.png", SG1x1_W, SG1x1_H, 64, indexed=True)

    # Turret: 32 idle-facing frames + 32 damaged-facing frames, single strip.
    # Each facing is a separate view of the 3D assembly (issue #65), and the
    # baked ground shadow is injected as SHADOW_IDX rather than painted.
    idle_bodies, idle_shadows = sgtur_frames(damaged=False)
    dmg_bodies, dmg_shadows = sgtur_frames(damaged=True)
    save_pngsheet(indexed_strip(idle_bodies + dmg_bodies, idle_shadows + dmg_shadows,
                                SGTUR_W, SGTUR_H),
                  "sgturturret.png", SGTUR_W, SGTUR_H, 64, indexed=True)
    save_pngsheet(make_icon(sgtur_base_draw, SGTUR_W, SGTUR_H, label=ICON_LABELS["sgtur"]),
                  "sgturicon.png", ICON_W, ICON_H, 1)

    # Emplacement pad: the fixed body under the rotating station, replacing the
    # stock gunmake.shp placeholder it borrowed for both its idle frame and its
    # build-up (issue #74). The station itself is gated on !build-incomplete,
    # so the build-up shows the pad alone and the turret pops in on completion
    # -- exactly how SAM/GUN/AGUN behave.
    pad = render(sgtur_pad_draw, SGTUR_W, SGTUR_H)
    pad_shadow = silhouette_shadow(pad, 2, 2)
    save_pngsheet(indexed_strip([pad], [pad_shadow], SGTUR_W, SGTUR_H),
                  "sgturpad.png", SGTUR_W, SGTUR_H, 1, indexed=True)
    pad_mk = make_frames(sgtur_pad_draw, SGTUR_W, SGTUR_H, final=pad)
    save_pngsheet(indexed_strip(pad_mk, [None] * (len(pad_mk) - 1) + [pad_shadow],
                                SGTUR_W, SGTUR_H),
                  "sgturmake.png", SGTUR_W, SGTUR_H, len(pad_mk), indexed=True)

    # Death rubble (issue #74), replacing stock powrdead.shp/apwrdead.shp. One
    # frame each, matching the stock rubble's own layout, with a real
    # SHADOW_IDX rim -- a collapsed building, unlike a standing one, leaves
    # terrain visible around itself.
    for name, dead_fn, w, h in (
        ("sgpwrdead", sgpwr_dead_draw, FAM23_W, FAM23_H),
        ("sgapwrdead", sgapwr_dead_draw, FAM33_W, FAM33_H),
        ("sghyddead", sghyd_dead_draw, FAM33_W, FAM33_H),
    ):
        wreck = render(dead_fn, w, h)
        save_pngsheet(indexed_strip([wreck], [silhouette_shadow(wreck, 2, 2)], w, h),
                      f"{name}.png", w, h, 1, indexed=True)

    # Drones: 32 facings x DRONE_SPIN_FRAMES rotor-spin frames, facing-major, no
    # damaged state (matching tran/mh60/heli). The spin lives in the body sheet
    # rather than in a WithIdleOverlay rotor disc for three reasons (issue #81):
    # the rotors stay registered with the booms at every facing because they are
    # rotated with the airframe rather than positioned by a WVec the engine's
    # classic perspective fudge shears differently than the image-plane rotation
    # that made the facings; WithShadow clones the body renderable, so the
    # ground shadow gets the turning rotors for free; and it keeps the rule that
    # an actor with bespoke art doesn't wear a generic overlay for a part its
    # own sprite draws.
    for name, draw_fn, fw, fh in (
        ("sgdro", sgdro_body_draw, 32, 30),
        ("sgdrs", sgdrs_body_draw, 36, 32),
    ):
        frames = rotated_anim_frames(draw_fn, fw, fh, n=32, length=DRONE_SPIN_FRAMES)
        assert len(frames) == 32 * DRONE_SPIN_FRAMES, "Facings x Length must equal the sheet"
        save_pngsheet(sheet_of(frames, fw, fh), f"{name}.png", fw, fh, len(frames), indexed=True)
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

    # Hauler Drone wrecks (issue #74): laden and empty, 32 facings each,
    # matching hhusk.shp/hhusk2.shp's split. Until now SGHAU died into those
    # two stock Ore Truck husks, which put back the exact sprite collision the
    # Hauler Drone was given its own art to end.
    for laden, filename in ((True, "sghauhuskfull.png"), (False, "sghauhusk.png")):
        bodies, shadows = sghau_husk_frames(laden)
        save_pngsheet(indexed_strip(bodies, shadows, SGHAU_W, SGHAU_H), filename,
                      SGHAU_W, SGHAU_H, len(bodies), indexed=True)

    # Disruptor Trooper (DISR): one self-contained 437-frame sheet, plus icon.
    # Authored natively in palette indices (see PC/disr_upright), so the sheet
    # is assembled as an indexed strip directly rather than converted from RGBA.
    disr_all = disr_frames()
    save_pngsheet(sheet_of_indexed(disr_all, DISR_W, DISR_H), "disr.png",
                  DISR_W, DISR_H, len(disr_all), indexed=True)
    # Cameo motif: the three-quarter front facing, mid-discharge, upscaled with
    # NEAREST so the cameo shows the same hard pixels the in-world sprite has.
    # (gen_photo_cameos.py overwrites this with the photographic cameo when it
    # runs -- see docs/BACKLOG.md issue #45 -- this keeps the programmatic
    # fallback in step with the sprite.)
    motif = indexed_to_rgba(disr_upright(5, "fire", spark=2))
    motif = motif.crop(motif.getbbox())
    motif = motif.resize((motif.width * SS, motif.height * SS), Image.NEAREST)
    save_pngsheet(make_icon_from_motif(motif, label=ICON_LABELS["disr"]),
                  "disricon.png", ICON_W, ICON_H, 1)

    print("done")


if __name__ == "__main__":
    main()
