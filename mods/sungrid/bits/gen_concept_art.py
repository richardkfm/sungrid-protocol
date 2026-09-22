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



def scorch(sd, blotches):
    """Damage decals: soft scorch blotches with a couple of rust streaks."""
    for (x, y, r) in blotches:
        sd.ellipse([x - r, y - r * 0.8, x + r, y + r * 0.8], fill=DAMAGE_SCORCH + (215,))
        sd.ellipse([x - r * 0.5, y - r * 0.45, x + r * 0.5, y + r * 0.4], fill=(0, 0, 0, 235))
    for (x, y, r) in blotches[:2]:
        sd.rect([x + r * 0.4, y, x + r * 0.4 + 0.8, y + r + 1.5], fill=RUST + (200,))


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

    def poly(self, verts, color, order=0, accent=False):
        """`accent=True` marks a face as team-coloured: it is drawn like any
        other, and additionally re-stamped at native resolution by
        mesh_frame() so it lands on the player-remap ramp (see there)."""
        self.faces.append((list(verts), color, order, accent))
        return self

    def quad(self, a, b, c, d, color, order=0, accent=False):
        return self.poly((a, b, c, d), color, order, accent)

    def box(self, x0, y0, z0, x1, y1, z1, color, top=None, order=0, shadow=True,
            top_face=True, accent=False):
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
            self.quad((x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1), top, order, accent)  # +z
        self.quad((x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1), color, order, accent)    # -y front
        self.quad((x1, y1, z0), (x0, y1, z0), (x0, y1, z1), (x1, y1, z1), color, order, accent)    # +y back
        self.quad((x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1), color, order, accent)    # +x
        self.quad((x0, y1, z0), (x0, y0, z0), (x0, y0, z1), (x0, y1, z1), color, order, accent)    # -x
        return self

    def prism(self, cx, cy, z0, z1, r, color, sides=10, top=None, phase=0.0, order=0,
              accent=False, shadow=True):
        """Upright n-gon column standing in for a cylinder (the barrel sleeve,
        the mount collar). Its top cap is emitted so it reads as solid."""
        top = color if top is None else top
        ring = [(cx + r * math.cos(phase + i * 2 * math.pi / sides),
                 cy + r * math.sin(phase + i * 2 * math.pi / sides)) for i in range(sides)]
        if shadow:
            self.solids.append([(px, py, z) for px, py in ring for z in (z0, z1)])
        for i in range(sides):
            (ax, ay), (bx, by) = ring[i], ring[(i + 1) % sides]
            self.quad((ax, ay, z0), (bx, by, z0), (bx, by, z1), (ax, ay, z1), color, order, accent)
        self.poly([(px, py, z1) for px, py in ring], top, order, accent)
        return self

    def strut(self, a, b, r, color, cap=None, order=0, shadow=True, accent=False):
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
            self.quad(a0, a1, b1, b0, color, order, accent)
        self.poly([c[1] for c in corners], cap or lit(color, 0.25), order, accent)
        return self

    def _oriented(self, deg):
        rad = math.radians(deg)
        c, s = math.cos(rad), math.sin(rad)
        return [([_rotz(p, c, s) for p in verts], color, order, accent)
                for verts, color, order, accent in self.faces]

    def draw(self, sd, ox, oy, deg=0.0, mode=None):
        """mode=None paints the shaded model. mode="mask" paints accent faces
        white and everything else black (an occlusion-correct coverage mask
        for the accent re-stamp); mode="accent" paints only the accent faces,
        in their shaded colours, ignoring occlusion (the colour source for the
        same re-stamp -- see mesh_frame())."""
        out = []
        for verts, color, order, accent in self._oriented(deg):
            if mode == "accent" and not accent:
                continue
            n = _face_normal(verts)
            if _v_dot(n, MESH_VIEW) <= 0.015:      # back face
                continue
            depth = sum(_v_dot(p, MESH_VIEW) for p in verts) / len(verts)
            shade = MESH_AMBIENT + (1 - MESH_AMBIENT) * max(0.0, _v_dot(n, MESH_LIGHT))
            if mode == "mask":
                col = (255, 255, 255, 255) if accent else (0, 0, 0, 255)
            else:
                col = _shaded(color, shade)
            out.append(((order, depth), [_project(p, ox, oy) for p in verts], col))
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


_REL_TANK = mix(LEGACY_GRAY, PANEL_BLUEBLACK, 0.22)   # transformer tank
_REL_BUSHING_X = (16, 21, 26)                         # bushing stack centres
_REL_BAND_X0, _REL_BAND_X1 = 8, 31                    # conduit band span
_REL_BAND_Y0, _REL_BAND_Y1 = 25, 27
_REL_TERM_Y = 5                                       # bushing terminal centre row


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


# The Arc Turret's head is a rotating sprite of its own (issue #66), so the
# body sheet keeps only the pedestal. `Turreted: Offset: 0,0,112` draws the
# turret sprite 112 world units up, which at RA's 24px/1024-unit scale is
# 2.625px, so the head has to be drawn that much lower inside its own frame
# for its underside to land back on the pedestal.
ARCT_AZIMUTH = 208.0                 # three-quarter view, used for the cameo
ARCT_TUR_LIFT = 112 * 24 / 1024
ARCT_GROUND_DY = 11.5                # pedestal ground contact, below the body frame centre
ARCT_RACE_TOP = 5.0                  # mount-race top, world units above that contact
ARCT_PEDESTAL_DY = ARCT_GROUND_DY - ARCT_RACE_TOP   # pedestal top, below the body frame centre
ARCT_TUR_OY = SG1x1_H / 2 + ARCT_PEDESTAL_DY + ARCT_TUR_LIFT
ARCT_RING_R = 13.6                   # grass ring radius around the hardstand
ARCT_ARC_PHASES = 6                  # idle arc-flicker frames per facing (issue #113); `turret:` Length
ARCT_LAMP_FRAMES = 8                 # pedestal status lamp: on 5, off 3; `idle:` Length


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
    # Turntable collar the head sits in, so the join to the pedestal's race
    # reads as a bearing rather than a box resting on a disc (issue #111).
    m.prism(0, 0, 0.0, 1.5, 8.2, dim(body, 0.3), sides=12, top=lit(body, 0.05), phase=math.pi / 12)
    # Emitter head: main mass, then a shallower brow plate above it.
    m.box(-7.5, -5.5, 1.5, 7.5, 5.5, 10.0, body, top=lit(body, 0.14))
    m.box(-6.2, -4.6, 10.0, 6.2, 4.6, 11.4, cap, top=lit(cap, 0.2))
    # Heat-sink fins on both flanks (the head turns through every facing, so
    # the detail has to be symmetric), proud of the hull by one unit.
    fin = dim(body, 0.2)
    for sx in (-1, 1):
        for y0 in (-3.6, -0.8, 2.0):
            m.box(min(sx * 7.5, sx * 8.6), y0, 4.6, max(sx * 7.5, sx * 8.6), y0 + 1.2, 9.4,
                  fin, top=lit(fin, 0.2), order=1, shadow=False)
    # Cooling stack behind the head, with a lit vent cap.
    m.box(-2.2, -7.0, 5.0, 2.2, -5.4, 14.2, dim(body, 0.35), top=dim(body, 0.2))
    m.box(-2.6, -7.4, 14.2, 2.6, -5.0, 14.9, dim(body, 0.15), top=lit(body, 0.3), order=1, shadow=False)
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
        foot = (sx * 3.6, -0.5, 10.6)
        m.strut(foot, tip, 1.7,
                mix(LEGACY_GRAY_DARK, LEGACY_GRAY, 0.35), cap=lit(LEGACY_GRAY, 0.1),
                order=2, shadow=False)
        # Insulator discs along the rod, pale so they read against the dark
        # shaft: the one mark that says "high voltage" at this size.
        for t in ((0.42, 0.72) if live else (0.55,)):
            cx, cy, cz = (foot[i] + (tip[i] - foot[i]) * t for i in range(3))
            m.prism(cx, cy, cz - 0.45, cz + 0.45, 2.3, PALE_STEEL, sides=8,
                    top=lit(PALE_STEEL, 0.2), order=2, shadow=False)
        if live:
            m.strut(tip, (tip[0] * 1.05, tip[1] + 0.4, tip[2] + 1.8), 1.8,
                    accent, cap=lit(accent, 0.35), order=2, shadow=False)
    return m


def _arct_rod_tip(sx, live=True):
    return (sx * 5.5, 1.5 if live else 0.5, 19.5 if live else 13.5)


def _ring_front(ang, width=0.6):
    """True for angles within `width` radians of the camera-facing (-y) side."""
    d = (ang + math.pi / 2) % (2 * math.pi)
    return min(d, 2 * math.pi - d) < width


def grass_ring(m, r, n, salt, skip=_ring_front, z=0.0):
    """Feather-grass tufts and low groundcover clumps around a circular or
    polygonal footprint at radius `r` (issue #111): the greenery the two
    defence pads get instead of the roster buildings' planted beds -- a
    narrow reclaimed fringe that leaves the pad's own silhouette alone. Every
    position comes from _scatter(), so regeneration stays byte-identical.
    `skip(angle)` keeps the front sector clear of the cable trench."""
    for i in range(n):
        a, b, c = _scatter(i, salt, 1), _scatter(i, salt, 2), _scatter(i, salt, 3)
        ang = 2 * math.pi * (i + 0.5 * a) / n
        if skip is not None and skip(ang):
            continue
        rr = r + (b - 0.5) * 1.8
        x, y = rr * math.cos(ang), rr * math.sin(ang)
        if c < 0.3:
            _clump(m, x, y, z, 1.6 + b * 0.8, LEAF_DARK, LEAF_SAGE, 0.8)
        else:
            tuft(m, x, y, z, cap=2.0 + b * 1.2)


def arct_pedestal_mesh(damaged=False, lamp=True):
    """The fixed pedestal as a solid (issue #111): a gravel hardstand, the
    concrete drum with a chamfered upper step, the dark mount race the head
    turns in, a ring of anchor bolts, the team-coloured feed lug and its
    cable trench on the camera side, an access hatch on the lit flank, vent
    slots on the shaded one, and a fringe of grass around the hardstand. The
    footprint stays round and centred, so the head sits on it at every facing
    exactly as before; only the elevation gained volume."""
    con = CONCRETE if not damaged else mix(CONCRETE, DAMAGE_SCORCH, 0.3)
    base = LEGACY_GRAY_DARK if not damaged else mix(LEGACY_GRAY_DARK, DAMAGE_SCORCH, 0.5)
    accent = SUN_GOLD if not damaged else RUST
    ph = math.pi / 16
    m = Mesh()
    m.prism(0, 0, 0.0, 1.0, 12.5, dim(con, 0.28), sides=16, top=dim(con, 0.08), phase=ph)
    m.prism(0, 0, 1.0, 3.4, 10.2, con, sides=16, top=lit(con, 0.28), phase=ph)
    m.prism(0, 0, 3.4, 4.1, 8.8, dim(con, 0.08), sides=16, top=lit(con, 0.14), phase=ph)
    m.prism(0, 0, 4.1, ARCT_RACE_TOP, 7.8, base, sides=16, top=lit(base, 0.22), phase=ph)
    for i in range(8):
        if damaged and i in (2, 5):
            continue                                       # sheared bolts
        ang = i * math.pi / 4 + math.pi / 8
        m.prism(9.5 * math.cos(ang), 9.5 * math.sin(ang), 3.4, 4.1, 0.65, lit(base, 0.35),
                sides=6, top=lit(base, 0.6), shadow=False)
    # Feed lug and cable trench, on the remap ramp like every conduit.
    m.box(-1.6, -12.2, 1.0, 1.6, -9.6, 3.0, accent, top=lit(accent, 0.25),
          order=1, shadow=False, accent=True)
    m.box(-0.9, -14.2, 1.0, 0.9, -12.2, 1.7, accent, top=lit(accent, 0.2),
          order=1, shadow=False, accent=True)
    # Access hatch on the lit (-x) flank, vent slots on the shaded (+x) one,
    # and a status lamp above the hatch that blinks while the pedestal is
    # intact (issue #113): a fixed-palette green when lit, plain dark grey
    # when not -- never a dark green/amber, which _index_for would route
    # onto the remap ramp (issue #109's lamp lesson).
    m.box(-10.9, -1.8, 1.6, -10.0, 1.8, 3.4, dim(con, 0.45), order=1, shadow=False, top_face=False)
    lamp_col = (lit(GREEN_ACCENT, 0.2) if (lamp and not damaged) else dim(con, 0.5))
    m.box(-11.1, -0.7, 3.7, -10.0, 0.7, 4.6, lamp_col, top=lamp_col, order=2, shadow=False)
    for y0 in (-2.6, 0.4):
        m.box(10.0, y0, 1.8, 10.9, y0 + 1.7, 3.2, dim(con, 0.5), order=1, shadow=False, top_face=False)
    if damaged:
        # A cracked-off wedge of the drum's top edge on the shaded side.
        m.box(4.5, 3.5, 2.6, 9.5, 8.5, 3.5, dim(con, 0.55), top=DAMAGE_SCORCH, order=1, shadow=False)
    grass_ring(m, ARCT_RING_R, 11, salt=66)
    return m


def arct_draw(sd, w=SG1x1_W, h=SG1x1_H, damaged=False, lamp=True):
    """Body sheet: the fixed pedestal only (plain shaded model, for the
    build-up strip and the cameo fallback -- the shipped idle frames go
    through arct_body_frame so the feed lug lands on the remap ramp). The
    emitter head rides above this as a separate 32-facing turret sprite."""
    ox, oy = w // 2, h / 2 + ARCT_GROUND_DY
    arct_pedestal_mesh(damaged, lamp).draw(sd, ox, oy, 0.0)
    if damaged:
        _arct_damage_decals(sd, w, h)


def _arct_damage_decals(sd, w, h):
    ox, oy = w // 2, h / 2 + ARCT_GROUND_DY
    scorch(sd, [(ox + 6, oy - 6, 2.6), (ox - 6, oy - 3.5, 2.2)])


def arct_body_frame(damaged=False, lamp=True):
    """One shipped pedestal frame: the model with its accent faces re-stamped
    natively (see _mesh_render), then the scorch decals."""
    ox, oy = SG1x1_W // 2, SG1x1_H / 2 + ARCT_GROUND_DY
    return _mesh_render(arct_pedestal_mesh(damaged, lamp), SG1x1_W, SG1x1_H, ox, oy, 0.0,
                        decals=_arct_damage_decals if damaged else None)


def arct_shadow_draw(sd, w=SG1x1_W, h=SG1x1_H, damaged=False):
    arct_pedestal_mesh(damaged).draw_shadow(sd, w // 2, h / 2 + ARCT_GROUND_DY, 0.0)


# Idle arc flicker (issue #113): per phase, the zigzag's two knees (as
# fractions along the tip-to-tip line, and their perpendicular throw), whether
# a white core pixel sits on the first knee, and whether a short side branch
# forks off it. Six phases at Tick 120 is a 0.72 s cycle, the same jitter
# grammar as the Smart Grid Relay's arc.
ARCT_ARC_FLICKER = (
    ((0.42, -1.8), (0.58, 1.4), True, False),
    ((0.35, -1.2), (0.62, 1.9), False, True),
    ((0.48, -2.2), (0.55, 0.9), True, False),
    ((0.30, -0.9), (0.68, 1.5), False, False),
    ((0.45, -1.6), (0.52, 2.0), True, True),
    ((0.38, -2.0), (0.60, 1.1), False, False),
)


def arct_turret_draw(sd, w=SG1x1_W, h=SG1x1_H, damaged=False, facing=0.0, phase=0):
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
    (ka, ta), (kb, tb), core, branch = ARCT_ARC_FLICKER[phase % len(ARCT_ARC_FLICKER)]
    dx, dy = rx - lx, ry - ly
    span = max(1.0, math.hypot(dx, dy))
    nx, ny = -dy / span, dx / span                         # perpendicular, screen space
    knee_a = (lx + dx * ka + nx * ta, ly + dy * ka + ny * ta)
    knee_b = (lx + dx * kb + nx * tb, ly + dy * kb + ny * tb)
    sd.line([(lx, ly), knee_a, knee_b, (rx, ry)], fill=lit(GREEN_ACCENT, 0.5), width=1.0)
    if branch:
        sd.line([knee_a, (knee_a[0] + nx * ta * 0.9 + 0.6, knee_a[1] + ny * ta * 0.9 - 1.2)],
                fill=lit(GREEN_ACCENT, 0.5), width=0.8)
    if core:
        sd.px(round(knee_a[0]), round(knee_a[1]), (0xFC, 0xFC, 0xFC))
    for (px_, py_) in ((lx, ly), (rx, ry)):
        sd.px(round(px_), round(py_), lit(GREEN_ACCENT, 0.75))


def arct_turret_shadow_draw(sd, w=SG1x1_W, h=SG1x1_H, damaged=False, facing=0.0):
    arct_mesh(damaged).draw_shadow(sd, w // 2, ARCT_TUR_OY, facing)


def arct_turret_frames(damaged=False, n=32, phases=1):
    """Facing-major: for each of the n facings, `phases` arc-flicker frames
    (the engine indexes facing * Length + frame, issue #35's lesson). The
    damaged head has no arc, so it gets one frame per facing."""
    bodies, shadows = [], []
    for i in range(n):
        deg = i * (360.0 / n)
        shadow = render_shadow_mask(arct_turret_shadow_draw, SG1x1_W, SG1x1_H,
                                    damaged=damaged, facing=deg)
        for ph in range(phases):
            bodies.append(render(arct_turret_draw, SG1x1_W, SG1x1_H, damaged=damaged,
                                 facing=deg, phase=ph))
            shadows.append(shadow)
    return bodies, shadows


def arct_icon_draw(sd, w=SG1x1_W, h=SG1x1_H, damaged=False):
    """Body and head together, for the programmatic cameo fallback (the
    shipped cameo is issue #45's photographic one)."""
    arct_draw(sd, w, h, damaged)
    arct_mesh(damaged).draw(sd, w // 2, h / 2 + ARCT_PEDESTAL_DY, ARCT_AZIMUTH)


# ---------------------------------------------------------------------------
# Volumetric buildings (docs/BACKLOG.md issue #106).
#
# Decoding fact.shp / weap3.shp shows what "the 3D feel" of stock RA building
# art actually is: the building is a solid rotated 45 degrees on the ground,
# so its footprint is a 2:1 diamond, its roof plane is visible, and two walls
# meet at the corner nearest the camera -- the lit one on the left, the shaded
# one on the right. Every building here used to be a *front elevation* on a
# flat horizontal pad, which is a cutout standing on a shelf next to that.
# So every building is now a Mesh (the same renderer the turrets use) viewed
# at BUILDING_YAW, on a diamond plinth that fits its footprint like stock does.
# ---------------------------------------------------------------------------

BUILDING_YAW = 45.0
PALE_STEEL = (0xB2, 0xB6, 0xBC)     # concept-render steel/hangar white; cool, so lit() never drifts onto the gold ramp
STEEL = mix(LEGACY_GRAY, PANEL_BLUEBLACK, 0.25)
SLAB = lit(CONCRETE, 0.18)
PAD_TOP = lit(CONCRETE, 0.42)
AMBER = (0xFF, 0x80, 0x10)          # fixed-palette status amber (far enough from SUN_GOLD to stay off the remap ramp)

# Plinth half-size (world units) and screen origin per frame family. The
# diamond's screen width is 2*half*sqrt(2); its bottom corner sits 2px above
# the frame edge, where the old flat pads' bottom row was, so placement on the
# footprint is unchanged.
def _oy(h, half):
    return h - 2 - round(half * math.sqrt(2) / 2)

FAM = {
    "3x3": (FAM33_W, FAM33_H, 27),
    "2x3": (FAM23_W, FAM23_H, 20),
    "2x2": (SGSHL_W, SGSHL_H, 18),
    "1x1": (SG1x1_W, SG1x1_H, 13),
    "fact": (72, 72, 25),
}


def plinth(m, half, z=2.2, band=True, live=True):
    """Concrete plinth (a diamond on screen) with the team-colour conduit band
    wrapped along its two near edges -- the same 'grid connection' tell the
    flat sprites carried as a horizontal bar, now on a solid. Accent faces get
    re-stamped natively (mesh_frame) so they stay on the remap ramp. Planting
    is per building (below), not a plinth feature: the two green corner
    blocks this used to add sat behind the building mass and read as noise."""
    m.box(-half, -half, 0, half, half, z, dim(SLAB, 0.15), top=SLAB, shadow=False)
    if band:
        col = SUN_GOLD if live else dim(SUN_GOLD, 0.4)
        m.box(-half + 1, -half + 1, z, half - 1, -half + 3.2, z + 1.0, col, top=lit(col, 0.25),
              order=1, shadow=False, accent=True)
        m.box(-half + 1, -half + 1, z, -half + 3.2, half - 1, z + 1.0, col, top=lit(col, 0.25),
              order=1, shadow=False, accent=True)


# Greenery (issue #108). Palette-exact foliage on temperat.pal's own tree ramp
# (indices 145-152): grey-green, drought-tolerant plants -- olive/acacia-type
# trees, lavender and rosemary mounds, feather-grass tufts, sedum roofs -- so
# one sprite is plausible on sand, grass and snow alike. The `player` palette
# is the same file on every tileset, so these tones never shift with terrain.
# Every planting position comes from _scatter(), a pure integer hash, because
# regeneration has to be byte-identical.
LEAF_PALE = (176, 208, 124)
LEAF_SAGE = (136, 172, 108)
LEAF_MID = (104, 136, 92)
LEAF_DARK = (76, 100, 60)
LEAF_DEEP = (60, 84, 48)
SOIL = (100, 80, 56)                # palette 32
BARK = (72, 56, 40)


def _scatter(x, y, salt=0):
    """Deterministic 0..1 hash of a planting position."""
    n = int(x * 73856093) ^ int(y * 19349663) ^ int(salt * 83492791)
    n = (n * 2654435761) & 0xFFFFFFFF
    return ((n >> 8) & 0xFFFF) / 65536.0


def _clump(m, x, y, z, r, col, top, h, sides=7):
    m.prism(x, y, z, z + h, r, col, sides=sides, top=top, shadow=False)


def tuft(m, x, y, z, cap=3.0):
    """Feather grass: a dark base and a pale, narrower plume."""
    m.prism(x, y, z, z + min(cap, 1.2), 1.4, LEAF_DEEP, sides=6, top=LEAF_DARK, shadow=False)
    if cap > 1.4:
        m.prism(x, y, z + 1.2, z + min(cap, 3.2), 0.95, LEAF_SAGE, sides=6, top=LEAF_PALE, shadow=False)


def shrub(m, x, y, z, r=2.8):
    """A rounded drought-tolerant mound (lavender, rosemary, sage)."""
    m.prism(x, y, z, z + r * 0.55, r, LEAF_DEEP, sides=8, top=LEAF_DARK)
    m.prism(x, y, z + r * 0.55, z + r * 1.05, r * 0.66, LEAF_MID, sides=8, top=LEAF_SAGE, shadow=False)


def tree(m, x, y, z, h=8.0, r=5.0):
    """A small olive/acacia-type tree: short trunk, wide flat-topped canopy in
    three stacked tiers. Halls get one at the near-right corner of the plot;
    the solar arrays get none, because a tree next to a panel shades it."""
    m.strut((x, y, z), (x, y, z + h * 0.62), 0.7, BARK, cap=BARK)
    base = z + h * 0.5
    m.prism(x, y, base, base + h * 0.26, r, LEAF_DEEP, sides=9, top=LEAF_DARK)
    m.prism(x + 0.4, y - 0.4, base + h * 0.26, base + h * 0.46, r * 0.74, dim(LEAF_MID, 0.1), sides=9, top=LEAF_MID, shadow=False)
    m.prism(x - 0.3, y + 0.3, base + h * 0.46, base + h * 0.6, r * 0.42, LEAF_MID, sides=7, top=LEAF_SAGE, shadow=False)


def bed(m, x0, y0, x1, y1, z, h=0.6, step=4.0, lowcap=1.0, salt=0, keep=None):
    """A planted bed: a soil-sided box with a green mat on top and scattered
    groundcover clumps, bare patches and the odd grass tuft. `keep(x, y)` is
    False where nothing may grow (equipment footings); `lowcap` caps the
    clump height (under panels). The marks are deliberately few and large:
    at 4x supersampling, clumps under ~1.5 units dissolve into speckle."""
    m.box(x0, y0, z - 0.2, x1, y1, z + h, SOIL, top=LEAF_MID, shadow=False)
    zt = z + h
    y, row = y0 + 1.6, 0
    while y < y1 - 1.2:
        x = x0 + 1.6 + (step / 2 if row % 2 else 0)
        while x < x1 - 1.2:
            a, b, c = _scatter(x, y, salt), _scatter(x, y, salt + 1), _scatter(x, y, salt + 2)
            px, py = x + (a - 0.5) * 1.6, y + (b - 0.5) * 1.6
            if keep is None or keep(px, py):
                if c < 0.14:
                    _clump(m, px, py, zt, 1.4 + a * 0.8, SOIL, lit(SOIL, 0.12), 0.15)
                elif c < 0.50:
                    _clump(m, px, py, zt, 1.6 + a * 1.2, LEAF_DEEP, LEAF_DARK, min(lowcap, 0.6 + b * 0.6))
                elif c < 0.84:
                    _clump(m, px, py, zt, 1.5 + a * 1.1, LEAF_DARK, LEAF_SAGE, min(lowcap, 0.7 + b * 0.6))
                else:
                    tuft(m, px, py, zt, cap=lowcap)
            x += step
        y += step * 0.85
        row += 1


def vines(m, x, y0, y1, z0, z1, salt=0, dark=False):
    """Climbing greenery on a -x (lit, screen-left) wall: leaf panels of
    uneven height pressed on the face, with clumps standing proud of their
    tops. `dark=True` on pale walls, so the leaves keep their contrast."""
    n = max(2, int((y1 - y0) / 4.5))
    lo, hi = (LEAF_DEEP, LEAF_DARK) if dark else (LEAF_DARK, LEAF_MID)
    for i in range(n):
        a, b = _scatter(i, salt, 3), _scatter(i, salt, 4)
        ya = y0 + (y1 - y0) * i / n + 0.4
        yb = ya + (y1 - y0) / n * (0.6 + 0.35 * a)
        zt = z0 + (z1 - z0) * (0.5 + 0.5 * b)
        m.quad((x - 0.3, ya, z0), (x - 0.3, yb, z0), (x - 0.3, yb, zt), (x - 0.3, ya, zt), lo if a < 0.5 else hi, order=1)
        m.box(x - 1.3, ya + 0.3, zt - 1.8, x - 0.2, yb - 0.3, zt + 0.3, hi, top=LEAF_SAGE if not dark else LEAF_MID, order=2, shadow=False)


def green_roof(m, x0, y0, x1, y1, z, keep=None, salt=5, path=True):
    """Sedum mat on a flat roof, with a gravel service strip on the near edge."""
    bed(m, x0, y0, x1, y1, z, h=0.5, step=2.8, lowcap=0.6, salt=salt, keep=keep)
    if path:
        m.box(x0, y0, z + 0.5, x1, y0 + 1.6, z + 0.6, PAD_TOP, top=PAD_TOP, order=1, shadow=False)


def dome(m, cx, cy, z, r, col, steps=5, height=None):
    """Stacked shrinking prisms standing in for a crown or dome."""
    height = r * 0.55 if height is None else height
    for i in range(steps):
        t = i / steps
        rr = r * math.cos(t * math.pi / 2 * 0.92)
        hh = height / steps
        m.prism(cx, cy, z + i * hh, z + (i + 1) * hh, rr, lit(col, 0.05 * i), sides=12,
                top=lit(col, 0.10 + 0.07 * i), shadow=(i == 0))


def pv_panel(m, x0, y, w, d, z, rise=6.5, face=None, order=2, damaged=False, frame=None):
    """A collector panel tilted back-and-up (low edge at the front), on two
    posts, with cell mullions and a lit aluminium frame on its top and left."""
    face = lit(PANEL_BLUEBLACK, 0.1) if face is None else face
    frame = lit(LEGACY_GRAY, 0.45) if frame is None else frame
    x1, lo, hi = x0 + w, z + 3, z + 3 + rise
    m.strut((x0 + 3, y + d / 2, z), (x0 + 3, y + d / 2, lo + rise * 0.4), 0.7, STEEL)
    m.strut((x1 - 3, y + d / 2, z), (x1 - 3, y + d / 2, lo + rise * 0.4), 0.7, STEEL)
    m.quad((x0, y, lo), (x1, y, lo), (x1, y + d, hi), (x0, y + d, hi), face, order=order)
    for k in range(1, 4):
        yy, zz = y + d * k / 4, lo + rise * k / 4
        m.quad((x0, yy - 0.25, zz - 0.15), (x1, yy - 0.25, zz - 0.15), (x1, yy + 0.25, zz + 0.15),
               (x0, yy + 0.25, zz + 0.15), dim(PANEL_BLUEBLACK, 0.55), order=order + 1)
    xm = x0 + w / 2
    m.quad((xm - 0.2, y, lo), (xm + 0.2, y, lo), (xm + 0.2, y + d, hi), (xm - 0.2, y + d, hi),
           dim(PANEL_BLUEBLACK, 0.55), order=order + 1)
    m.quad((x0, y + d - 0.6, hi - 0.4), (x1, y + d - 0.6, hi - 0.4), (x1, y + d, hi), (x0, y + d, hi), frame, order=order + 2)
    m.quad((x0, y, lo), (x0 + 0.6, y, lo), (x0 + 0.6, y + d, hi), (x0, y + d, hi), frame, order=order + 2)
    if damaged:
        m.quad((x0 + 2, y + 2, lo + rise * 0.2), (x0 + w * 0.7, y + 2, lo + rise * 0.2),
               (x0 + w * 0.5, y + d - 2, lo + rise * 0.8), (x0 + w * 0.3, y + d - 2, lo + rise * 0.8),
               DAMAGE_SCORCH, order=order + 3)


def tilted_disc(m, cx, cy, cz, r, normal, col, inner=None, sides=12, order=2, back=None):
    """A dish/disc facing `normal`: a flat n-gon in the plane perpendicular to it.
    `back` gives it a rear face too (the renderer culls by winding, so a dish
    that sweeps away from the camera would otherwise vanish for half a turn)."""
    n = _v_norm(normal)
    up = (0.0, 0.0, 1.0) if abs(n[2]) < 0.9 else (1.0, 0.0, 0.0)
    u = _v_norm((n[1] * up[2] - n[2] * up[1], n[2] * up[0] - n[0] * up[2], n[0] * up[1] - n[1] * up[0]))
    v = (n[1] * u[2] - n[2] * u[1], n[2] * u[0] - n[0] * u[2], n[0] * u[1] - n[1] * u[0])
    def ring(rr, lift):
        return [(cx + rr * (u[0] * math.cos(a) + v[0] * math.sin(a)) + n[0] * lift,
                 cy + rr * (u[1] * math.cos(a) + v[1] * math.sin(a)) + n[1] * lift,
                 cz + rr * (u[2] * math.cos(a) + v[2] * math.sin(a)) + n[2] * lift)
                for a in [i * 2 * math.pi / sides for i in range(sides)]]
    m.poly(ring(r, 0.0), col, order=order)
    if inner is not None:
        m.poly(ring(r * 0.72, 0.2), inner, order=order + 1)
    if back is not None:
        m.poly(list(reversed(ring(r, -0.2))), back, order=order)


def _rot_about(cx, cy, x, y, deg):
    """(x, y) turned `deg` degrees about (cx, cy) in the ground plane."""
    a = math.radians(deg)
    dx, dy = x - cx, y - cy
    return (cx + dx * math.cos(a) - dy * math.sin(a), cy + dx * math.sin(a) + dy * math.cos(a))


def drone_model(m, cx, cy, z, col=GREEN_PRIMARY, r=7.5, damaged=False):
    """A parked quadcopter, the same span the flyable drones have (~15px)."""
    m.box(cx - 3.0, cy - 3.0, z + 1.5, cx + 3.0, cy + 3.0, z + 4.2, col, top=lit(col, 0.3))
    m.box(cx - 1.4, cy - 4.2, z + 2.2, cx + 1.4, cy - 3.0, z + 3.6, PANEL_BLUEBLACK, top=PANEL_BLUEBLACK, order=1, shadow=False)
    for k, (sx, sy) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
        if damaged and k == 1:
            continue
        m.strut((cx + sx * 2.5, cy + sy * 2.5, z + 3.0), (cx + sx * r, cy + sy * r, z + 3.2), 0.6, LEGACY_GRAY_DARK)
        m.prism(cx + sx * r, cy + sy * r, z + 3.2, z + 3.8, 3.4, dim(PALE_STEEL, 0.25), sides=10,
                top=lit(PALE_STEEL, 0.15), order=2)
        m.prism(cx + sx * r, cy + sy * r, z + 3.8, z + 4.4, 1.2, LEGACY_GRAY_DARK, sides=6, top=LEGACY_GRAY_DARK, order=3)
    if not damaged:
        m.box(cx - 1.0, cy - 1.0, z + 4.2, cx + 1.0, cy + 1.0, z + 5.2, SUN_GOLD, top=lit(SUN_GOLD, 0.3), order=3, shadow=False, accent=True)


def gauge(m, x, y0, z0, n_lit, total=8, pitch=1.0, width=4.0, live=True, side="-x"):
    """Vertical charge/fill readout on a cabinet face: `total` rows, the
    lowest `n_lit` of them team-coloured (accent), the rest dark."""
    on = SUN_GOLD if live else dim(SUN_GOLD, 0.4)
    off = dim(LEGACY_GRAY_DARK, 0.15)
    for i in range(total):
        z = z0 + i * pitch
        col = on if i < n_lit else off
        if side == "-x":
            m.box(x - 0.5, y0, z, x + 0.1, y0 + width, z + pitch * 0.85, col, top=col, order=3, shadow=False, accent=(i < n_lit))
        else:
            m.box(y0, x - 0.5, z, y0 + width, x + 0.1, z + pitch * 0.85, col, top=col, order=3, shadow=False, accent=(i < n_lit))


# --------------------------------------------------------------------- roster

def sgpwr_mesh(damaged=False):
    """Solar Array: four large collectors in two rows, filling the plot, with
    the inverter cabinet at the near-left corner in front of them (a cabinet
    behind the back row would vanish behind the panels' raised rear edge)."""
    m = Mesh()
    plinth(m, 20, live=not damaged)
    # Planted bed inside the concrete rim, the collectors standing in it
    # (issue #108): groundcover under the panels, shrubs and grasses on the
    # front strip. No tree -- it would shade the panels.
    bed(m, -16.3, -16.3, 19.5, 19.5, 2.2, lowcap=0.9, salt=1,
        keep=lambda x, y: not (-17 < x < -8 and -17.5 < y < -10))
    for row, y in enumerate((-10, 6)):
        for col, x in enumerate((-16, 3)):
            pv_panel(m, x, y, 17.5, 14, 2.8, rise=9.5, damaged=damaged and row == 1 and col == 1)
    m.box(-16, -16.5, 2.2, -9, -11, 8, STEEL, top=lit(STEEL, 0.2))
    m.box(-16.5, -15.5, 4.5, -15.9, -12, 5.7, SUN_GOLD if not damaged else dim(SUN_GOLD, 0.4), top=SUN_GOLD, order=1, shadow=False, accent=True)
    for x in (-4, 5, 14):
        shrub(m, x, -14.3, 2.8, r=2.3 + 0.7 * _scatter(x, 1))
    for x in (0.5, 9.5, 18):
        tuft(m, x, -14.8, 2.8)
    return m


def sgapwr_mesh(damaged=False):
    """Advanced Solar Array: a full field of nine large collectors in three
    rows, with the storage/switchgear cabinet at the near-right corner in
    front of them. (It shipped first with a concentrator dish taking a third
    of the plot; the owner's read was that the dish looked like a radar and
    the building should carry many more panels instead.)"""
    m = Mesh()
    plinth(m, 27, live=not damaged)
    bed(m, -23.5, -23.3, 26.5, 26.5, 2.2, lowcap=0.9, salt=2,
        keep=lambda x, y: not (11 < x < 27 and -25 < y < -16))
    for row, y in enumerate((-15, -1, 13)):
        for col, x in enumerate((-23.5, -6.1, 11.3)):
            pv_panel(m, x, y, 16, 12.5, 2.8, rise=8.5, damaged=damaged and (row, col) in ((1, 1), (0, 2)))
    m.box(12, -23.5, 2.2, 26, -17, 10, STEEL, top=lit(STEEL, 0.2))
    for i in range(3):
        m.box(13 + i * 4.2, -24, 4, 16 + i * 4.2, -23.5, 8.5, dim(STEEL, 0.4), top=dim(STEEL, 0.4), order=1, shadow=False)
    m.box(11.5, -22.5, 7.5, 12.1, -18, 8.7, SUN_GOLD if not damaged else dim(SUN_GOLD, 0.4), top=SUN_GOLD, order=1, shadow=False, accent=True)
    for x in (-12, -3, 6):
        shrub(m, x, -20.0, 2.8, r=2.4 + 0.9 * _scatter(x, 2))
    for x in (-8, 1.5, 9.5):
        tuft(m, x, -21.2, 2.8)
    if damaged:
        m.box(12.5, -24.1, 5, 19, -23.6, 9.5, DAMAGE_SCORCH, top=DAMAGE_SCORCH, order=2, shadow=False)
    return m


def sgcry_mesh(damaged=False, flicker=None):
    """Cryptominer: worn, scavenged server-rack blocks under a lean-to PV
    canopy -- the untidy legacy-tech foil to the Datacenter. `flicker` (0-7)
    picks which amber status pips are lit that frame (issue #109)."""
    m = Mesh()
    plinth(m, 20, live=not damaged)
    racks = [((-17, -12, -5, 1), 12, LEGACY_GRAY), ((-3, -15, 10, -3), 9, mix(LEGACY_GRAY, RUST, 0.35)),
             ((-14, 4, -1, 17), 15, dim(LEGACY_GRAY, 0.12)), ((3, 1, 16, 15), 11, mix(LEGACY_GRAY, RUST, 0.2))]
    for k, ((x0, y0, x1, y1), hgt, col) in enumerate(racks):
        if damaged and k == 1:
            # Toppled rack: lying on its side, scorched.
            m.box(x0 - 2, y0 - 3, 2.2, x0 + hgt - 2, y0 + 4, 2.2 + (x1 - x0), mix(col, DAMAGE_SCORCH, 0.5), top=dim(col, 0.3))
            continue
        m.box(x0, y0, 2.2, x1, y1, 2.2 + hgt, col, top=lit(col, 0.1))
        # Vent slots down the lit face, amber status pips near the top.
        for zz in range(4, hgt - 1, 3):
            m.box(x0 - 0.4, y0 + 1.5, 2.2 + zz, x0 + 0.1, y1 - 1.5, 2.2 + zz + 1.0, dim(col, 0.45), top=dim(col, 0.45), order=1, shadow=False)
        pip = AMBER if not damaged else dim(AMBER, 0.6)
        if flicker is not None and not damaged and _scatter(k, flicker, 21) < 0.3:
            pip = dim(AMBER, 0.55)
        m.box(x0 - 0.5, y0 + 1.5, 2.2 + hgt - 2.2, x0 + 0.1, y0 + 3.5, 2.2 + hgt - 1.2, pip, top=pip, order=2, shadow=False)
    # Lean-to canopy of salvaged panels over the front racks, on two poles.
    m.strut((-19, -19, 2.2), (-19, -19, 15), 0.7, POLE_DARK)
    m.strut((12, -19, 2.2), (12, -19, 13), 0.7, POLE_DARK)
    m.quad((-20, -20, 15), (13, -20, 13), (13, -8, 16.5), (-20, -8, 18.5), lit(PANEL_BLUEBLACK, 0.12), order=4)
    m.quad((-20, -14, 16.7), (13, -14, 14.7), (13, -13.6, 14.85), (-20, -13.6, 16.85), dim(PANEL_BLUEBLACK, 0.5), order=5)
    # Cable tray slung between the racks.
    m.strut((-8, -5, 12), (6, -1, 13), 0.6, POLE_DARK)
    # Overgrowth (issue #108): moss on the tallest rack, ivy up its lit face,
    # weeds in the front strip and a tree at the near-right corner.
    bed(m, -13.5, 4.5, -1.5, 16.5, 17.2, h=0.4, step=2.8, lowcap=0.5, salt=4)
    vines(m, -14, 5, 16, 2.2, 7.5, salt=4, dark=True)
    shrub(m, -12, -15, 2.2, r=2.2)
    tuft(m, -7, -14.6, 2.2)
    tuft(m, 17, -9, 2.2)
    tree(m, 16.5, -16.5, 2.2, h=7.5, r=4.5)
    return m


def sgdai_mesh(damaged=False, beacon=True):
    """Datacenter for AI: a sealed machine hall with a rooftop chiller bank --
    tidy, capital-intensive, the foil to the Cryptominer. `beacon=False` is
    the mast light's off frame (issue #109)."""
    m = Mesh()
    plinth(m, 20, live=not damaged)
    hall = mix(PANEL_BLUEBLACK, LEGACY_GRAY, 0.35)
    m.box(-18, -15, 2.2, 18, 16, 15, hall, top=lit(hall, 0.12))
    # Window band on the lit face, green data line along the front.
    m.box(-18.5, -12, 7, -17.9, 13, 9.5, lit(PANEL_BLUEBLACK, 0.55), top=lit(PANEL_BLUEBLACK, 0.55), order=1, shadow=False)
    m.box(-16, -15.5, 3.2, 16, -14.9, 4.0, GREEN_ACCENT if not damaged else dim(GREEN_ACCENT, 0.5), top=GREEN_ACCENT, order=1, shadow=False)
    # Sedum roof around the chiller bank (2 x 3 units with dark fan tops),
    # ivy on the lit face below the window band, grasses and two shrubs on
    # the front strip clear of the data line, a tree at the near-right corner
    # (issue #108).
    green_roof(m, -17.5, -14.5, 17.5, 15.5, 15, salt=5,
               keep=lambda x, y: not any(x0 - 0.8 < x < x0 + 7.8 and y0 - 0.8 < y < y0 + 8.8
                                         for x0 in (-13, -3, 7) for y0 in (-8, 4)))
    for i in range(3):
        for j in range(2):
            if damaged and (i, j) == (2, 0):
                continue
            x, y = -13 + i * 10, -8 + j * 12
            m.box(x, y, 15, x + 7, y + 8, 19, PALE_STEEL, top=lit(PALE_STEEL, 0.1), shadow=False, order=1)
            m.prism(x + 3.5, y + 4, 19, 19.6, 2.6, LEGACY_GRAY_DARK, sides=8, top=dim(LEGACY_GRAY, 0.3), shadow=False, order=1)
    vines(m, -18.0, -14, -1, 2.2, 6.6, salt=1)
    vines(m, -18.0, 3, 15, 2.2, 6.6, salt=2)
    shrub(m, -13, -17.4, 2.2, r=2.0)
    shrub(m, 9, -17.4, 2.2, r=2.0)
    for x in (-7, -1.5, 4):
        tuft(m, x, -17.4, 2.2)
    tree(m, 15.5, -17.3, 2.2, h=8.5, r=5.0)
    # Beacon mast on the near corner of the roof.
    m.strut((15, -12, 15), (15, -12, 22 if not damaged else 17), 0.6, STEEL, cap=RUST if damaged else None)
    if not damaged and beacon:
        m.box(14.3, -12.7, 22, 15.7, -11.3, 23.2, SUN_GOLD, top=lit(SUN_GOLD, 0.3), order=4, shadow=False, accent=True)
    elif not damaged:
        m.box(14.3, -12.7, 22, 15.7, -11.3, 23.2, dim(PALE_STEEL, 0.45), top=dim(PALE_STEEL, 0.3), order=4, shadow=False)
    if damaged:
        m.box(4, -16, 8, 12, -14.5, 15, DAMAGE_SCORCH, top=DAMAGE_SCORCH, order=2, shadow=False)
    return m


def sgdrn_mesh(damaged=False, chase=None):
    """Drone Bay: an octagonal landing pad with a team-colour ring, control
    cabin, charging mast, and a Recon Drone parked on the pad. `chase` (0-7)
    lights one opposite pair of the eight pad markers for the idle animation
    (issue #109); None is the even, unanimated ring."""
    m = Mesh()
    plinth(m, 20, live=not damaged)
    m.prism(1, -3, 2.2, 4.0, 15.5, dim(CONCRETE, 0.05), sides=8, top=PAD_TOP, phase=math.pi / 8)
    ring = SUN_GOLD if not damaged else dim(SUN_GOLD, 0.4)
    m.prism(1, -3, 4.0, 4.7, 15.5, ring, sides=8, top=lit(ring, 0.25), phase=math.pi / 8, order=1, accent=True, shadow=False)
    m.prism(1, -3, 4.0, 4.8, 12.5, PAD_TOP, sides=8, top=lit(PAD_TOP, 0.05), phase=math.pi / 8, order=2, shadow=False)
    for i in range(8):
        a = i * math.pi / 4 + math.pi / 8
        px, py = 1 + 15.5 * math.cos(a), -3 + 15.5 * math.sin(a)
        if damaged:
            marker = RUST
        elif chase is None:
            marker = GREEN_ACCENT
        else:
            marker = lit(GREEN_ACCENT, 0.55) if i in (chase, (chase + 4) % 8) else dim(GREEN_ACCENT, 0.45)
        m.box(px - 0.7, py - 0.7, 4.7, px + 0.7, py + 0.7, 6.0, LEGACY_GRAY_DARK, top=marker, order=3, shadow=False)
    m.box(-19, 8, 2.2, -6, 19, 11, STEEL, top=lit(STEEL, 0.2))
    m.box(-18, 9, 11, -7, 18, 11.8, PANEL_BLUEBLACK, top=lit(PANEL_BLUEBLACK, 0.35), shadow=False)
    m.box(-17.5, 7.5, 5, -7.5, 8.2, 8.5, PANEL_BLUEBLACK, top=PANEL_BLUEBLACK, order=1, shadow=False)
    vines(m, -19, 9.5, 18.5, 2.2, 7.5, salt=6)
    m.strut((8, 16, 2.2), (8, 16, 22 if not damaged else 12), 1.0, STEEL, cap=lit(STEEL, 0.3))
    if not damaged:
        m.strut((8, 16, 21), (2, 4, 21), 0.7, STEEL)
        m.box(0.5, 2.5, 19.5, 3.5, 5.5, 21, SUN_GOLD, top=lit(SUN_GOLD, 0.3), order=2, accent=True)
        drone_model(m, 1, -3, 4.8)
    else:
        m.box(-3, -6, 4.8, 4, 0, 6.5, dim(LEGACY_GRAY, 0.4), top=DAMAGE_SCORCH)
    # Planting in the plot corners outside the pad octagon (issue #108).
    tree(m, 16.5, -16, 2.2, h=7.5, r=4.5)
    shrub(m, -15.5, -15.3, 2.2, r=2.2)
    tuft(m, -12, -16.5, 2.2)
    tuft(m, 18, -11, 2.2)
    return m


def sgdra_mesh(damaged=False):
    """Aerial Fabrication Bay: a pale space-frame hangar, open on every side,
    carrying a collector field on its roof, with a Strike Drone underneath."""
    m = Mesh()
    plinth(m, 20, live=not damaged)
    cols = [(x, y) for x in (-18, 0, 18) for y in (-16, 16)]
    for k, (x, y) in enumerate(cols):
        if damaged and k == 5:
            continue
        m.strut((x, y, 2.2), (x, y, 13.5), 0.8, PALE_STEEL, cap=lit(PALE_STEEL, 0.2))
    # Roof slab with the panel field; in the damaged state the right half has dropped.
    if not damaged:
        m.box(-20, -18, 13.5, 20, 18, 14.8, PALE_STEEL, top=lit(PALE_STEEL, 0.15), shadow=False)
        m.box(-18, -16, 14.8, 18, 16, 15.6, PANEL_BLUEBLACK, top=lit(PANEL_BLUEBLACK, 0.3), shadow=False)
        for i in range(1, 4):
            m.box(-18 + i * 9 - 0.3, -16, 15.6, -18 + i * 9 + 0.3, 16, 15.9, dim(PANEL_BLUEBLACK, 0.5), top=dim(PANEL_BLUEBLACK, 0.5), shadow=False)
    else:
        m.box(-20, -18, 13.5, 2, 18, 14.8, PALE_STEEL, top=lit(PALE_STEEL, 0.15), shadow=False)
        m.box(-18, -16, 14.8, 0, 16, 15.6, PANEL_BLUEBLACK, top=lit(PANEL_BLUEBLACK, 0.3), shadow=False)
        m.quad((2, -18, 13.5), (20, -18, 6), (20, 18, 6), (2, 18, 13.5), mix(PALE_STEEL, DAMAGE_SCORCH, 0.3), order=1)
    # Zigzag truss band along the two near eaves: filled triangles, not lines.
    tri = lit(PALE_STEEL, 0.1)
    for edge in ("front", "left"):
        for i in range(6):
            t0, t1 = -20 + i * 6.6, -20 + (i + 1) * 6.6
            if damaged and edge == "front" and t0 > 2:
                continue
            if edge == "front":
                m.poly([(t0, -18.6, 10.5), (t1, -18.6, 10.5), ((t0 + t1) / 2, -18.6, 13.5)], tri, order=2)
            else:
                m.poly([(-18.6, t0, 10.5), (-18.6, t1, 10.5), (-18.6, (t0 + t1) / 2, 13.5)], tri, order=2)
    drone_model(m, 1, -2, 2.2, col=mix(GREEN_PRIMARY, PANEL_BLUEBLACK, 0.4), r=7.5, damaged=damaged)
    # An open hangar has no wall for vines and no room for a tree under its
    # eaves, so the greenery is ivy on the near-left column and shrubs and
    # grasses along the open sides (issue #108).
    m.box(-19.1, -17.1, 2.2, -16.9, -14.9, 6.5, LEAF_DARK, top=LEAF_MID, shadow=False)
    m.box(-19.6, -16.9, 5.0, -17.4, -15.1, 7.2, LEAF_MID, top=LEAF_SAGE, order=1, shadow=False)
    bed(m, -17.6, -12, -14.4, 13, 2.2, lowcap=1.2, salt=14, step=3.0)
    shrub(m, -9, -16.6, 2.2, r=2.5)
    shrub(m, 9, -16.6, 2.2, r=2.5)
    shrub(m, 15.2, -15.4, 2.2, r=2.0)
    tuft(m, 0, -17.2, 2.2)
    tuft(m, -16, 15.5, 2.2)
    return m


def sgshl_mesh(damaged=False, beacon=True):
    """Resilience Shelter: a hardened dome banked into an earth berm, with a
    sandbagged entry throat facing the front. `beacon=False` is the crown
    light's off frame (issue #109)."""
    m = Mesh()
    plinth(m, 18, live=not damaged)
    m.prism(0, 1, 2.2, 5.5, 16.5, DIRT, sides=12, top=LEAF_MID)
    # Planted berm ring between the shell and the berm edge, clear of the
    # entry throat and its sandbags (issue #108).
    for i in range(28):
        a = i * 2 * math.pi / 28 + 0.1
        rr = 13.6 + 2.0 * _scatter(i, 7, 1)
        px, py = rr * math.cos(a), 1 + rr * math.sin(a)
        if -9 < px < 9 and py < -7:
            continue
        c = _scatter(i, 7, 2)
        if c < 0.45:
            _clump(m, px, py, 5.5, 1.5 + c, LEAF_DEEP, LEAF_DARK, 0.8)
        elif c < 0.8:
            _clump(m, px, py, 5.5, 1.4 + c * 0.6, LEAF_DARK, LEAF_SAGE, 0.9)
        else:
            tuft(m, px, py, 5.5, cap=2.2)
    shell = mix(PALE_STEEL, GREEN_PRIMARY, 0.25)
    m.prism(0, 1, 5.5, 8.0, 12.5, shell, sides=12, top=shell)
    dome(m, 0, 1, 8.0, 12.5, shell, steps=6, height=9.5)
    if damaged:
        m.box(-3, -6, 14, 5, 2, 16.5, DAMAGE_SCORCH, top=DAMAGE_SCORCH, order=3, shadow=False)
    # Entry throat, cut through the berm to the front edge.
    m.box(-4, -17, 2.2, 4, -6, 7.5, dim(shell, 0.1), top=lit(shell, 0.05))
    m.box(-2.5, -17.4, 2.2, 2.5, -16.9, 6.5, DAMAGE_SCORCH, top=DAMAGE_SCORCH, order=1, shadow=False)
    for x in (-6.5, 6.5):
        for i in range(3):
            m.box(x - 1.5, -17 + i * 3, 2.2, x + 1.5, -14.5 + i * 3, 4.0, lit(DIRT, 0.25), top=lit(DIRT, 0.4), shadow=False)
    # Vent stack and the live beacon on the crown.
    m.strut((-8, 6, 12), (-8, 6, 17), 0.9, STEEL, cap=lit(STEEL, 0.3))
    if damaged:
        m.box(-1, 0, 17.5, 1, 2, 19, RUST, top=SUN_GOLD, order=4, shadow=False)
    elif beacon:
        m.box(-1, 0, 17.5, 1, 2, 19, SUN_GOLD, top=SUN_GOLD, order=4, shadow=False, accent=True)
    else:
        m.box(-1, 0, 17.5, 1, 2, 19, dim(PALE_STEEL, 0.45), top=dim(PALE_STEEL, 0.3), order=4, shadow=False)
    tree(m, 14, -14, 2.2, h=7.5, r=4.5)
    shrub(m, -14, -13.5, 2.2, r=2.2)
    return m


def sgsns_mesh(damaged=False, sweep=0.0):
    """Sensor Array: a parabolic dish on a mast over its equipment cabinet.
    `sweep` turns the dish assembly about the mast (degrees) for the idle
    animation (issue #109); the fallen damaged dish does not turn."""
    m = Mesh()
    plinth(m, 13, live=not damaged)
    m.box(-11, 1, 2.2, -2, 10, 8, STEEL, top=lit(STEEL, 0.2))
    m.box(-11.5, 2, 4, -10.9, 9, 5, GREEN_ACCENT if not damaged else dim(GREEN_ACCENT, 0.5), top=GREEN_ACCENT, order=1, shadow=False)
    # Sedum on the cabinet roof, a shrub and grasses on the front strip (issue #108).
    green_roof(m, -10.5, 1.5, -2.5, 9.5, 8, salt=8, path=False)
    shrub(m, 8, -8.5, 2.2, r=2.0)
    tuft(m, -6, -8.2, 2.2)
    tuft(m, 10, -3, 2.2)
    m.prism(4, -3, 2.2, 4.0, 3.5, dim(CONCRETE, 0.1), sides=8, top=lit(CONCRETE, 0.1))
    m.prism(4, -3, 4.0, 15.0, 1.4, STEEL, sides=8, top=lit(STEEL, 0.2))
    if not damaged:
        R = lambda x, y: _rot_about(4, -3, x, y, sweep)
        nx, ny = _rot_about(0, 0, -0.45, -0.5, sweep)
        m.strut((4, -3, 15), R(3, -4) + (17,), 0.8, STEEL)
        dx, dy = R(2.5, -4.5)
        tilted_disc(m, dx, dy, 19, 7.5, (nx, ny, 0.74), lit(PALE_STEEL, 0.2), inner=lit(PANEL_BLUEBLACK, 0.3), sides=10,
                    back=dim(PALE_STEEL, 0.3))
        fx, fy = R(0.5, -6.8)
        m.strut((dx, dy, 19), (fx, fy, 22.5), 0.4, STEEL)
        m.box(fx - 0.6, fy - 0.6, 22.3, fx + 0.6, fy + 0.6, 23.4, SUN_GOLD, top=lit(SUN_GOLD, 0.3), order=4, shadow=False, accent=True)
    else:
        tilted_disc(m, 6.5, -1.0, 6.5, 7.5, (0.3, 0.1, 0.95), dim(PALE_STEEL, 0.35), inner=dim(PANEL_BLUEBLACK, 0.3), sides=10)
    return m


def sgrel_mesh(damaged=False, arc=None):
    """Smart Grid Relay: a pad-mounted step-down transformer -- tank, radiator
    fins, three bushings with live terminals. `arc` (0-5) flickers the
    discharge between the terminals for the idle animation (issue #109)."""
    m = Mesh()
    plinth(m, 13, live=not damaged)
    tank = mix(LEGACY_GRAY, PANEL_BLUEBLACK, 0.22)
    m.box(-8, -6, 2.2, 5, 6, 11, tank, top=lit(tank, 0.12))
    for i in range(4):
        m.box(5, -5 + i * 3, 3.5, 8.5, -4 + i * 3, 10, dim(tank, 0.2), top=lit(tank, 0.05), shadow=False)
    # Ivy on the tank's lit face, a shrub at the near-right corner, grasses on the front strip (issue #108).
    vines(m, -8, -4, 4, 2.2, 6.0, salt=9)
    shrub(m, 9, -9, 2.2, r=2.0)
    tuft(m, -2, -8.5, 2.2)
    tuft(m, -9, -8, 2.2)
    for k, x in enumerate((-5.5, -1.5, 2.5)):
        snapped = damaged and k == 1
        top = 15.5 if not snapped else 12.5
        m.prism(x, 0, 11, top, 1.1, lit(PALE_STEEL, 0.1), sides=8, top=lit(PALE_STEEL, 0.25), shadow=False)
        if not snapped:
            m.box(x - 1.2, -1.2, top, x + 1.2, 1.2, top + 1.2, SUN_GOLD if not damaged else dim(SUN_GOLD, 0.4),
                  top=lit(SUN_GOLD, 0.3), order=2, shadow=False, accent=True)
    if arc is None or damaged:
        m.strut((-5.5, 0, 16.4), (2.5, 0, 16.4), 0.35, SUN_GOLD if not damaged else dim(SUN_GOLD, 0.4), order=3, shadow=False, accent=True)
    elif arc not in (2, 5):
        # Live arc: alternately thin and bright, thick and full, with a spark
        # jumping off one terminal on the bright frames.
        bright = arc % 2 == 1
        m.strut((-5.5, 0, 16.4), (2.5, 0, 16.4), 0.5 if bright else 0.35, lit(SUN_GOLD, 0.4) if bright else SUN_GOLD,
                order=3, shadow=False, accent=True)
        if bright:
            sx = (-5.5, 2.5, -1.5)[arc // 2]
            m.box(sx - 0.5, -0.5, 16.7, sx + 0.5, 0.5, 17.9, lit(SUN_GOLD, 0.5), top=lit(SUN_GOLD, 0.5), order=4, shadow=False, accent=True)
    if damaged:
        m.box(-8.5, -5, 4, -7.9, 0, 9, DAMAGE_SCORCH, top=DAMAGE_SCORCH, order=1, shadow=False)
    return m


def sgwnd_mesh(damaged=False, spin=0.0):
    """Wind Turbine Array: one slim mast on a single-cell footing. `spin` turns
    the rotor (degrees) for the idle animation (issue #109)."""
    m = Mesh()
    plinth(m, 13, live=not damaged)
    # Planted bed inside the rim, the mast footing standing in it (issue #108).
    bed(m, -9.5, -9.5, 11.5, 11.5, 2.2, lowcap=1.2, salt=3, step=3.2,
        keep=lambda x, y: x * x + y * y > 30)
    shrub(m, 8, -8, 2.8, r=2.2)
    tuft(m, -7.5, 7.5, 2.8)
    tuft(m, 3, -9, 2.8)
    m.prism(0, 0, 2.8, 3.8, 4.0, dim(CONCRETE, 0.1), sides=8, top=lit(CONCRETE, 0.1))
    m.prism(0, 0, 3.6, 17.0, 1.3, PALE_STEEL, sides=8, top=lit(PALE_STEEL, 0.2))
    m.box(-1.6, -3.2, 16.5, 1.6, 1.8, 19.5, PALE_STEEL, top=lit(PALE_STEEL, 0.2), shadow=False)
    hub = (0.0, -3.6, 18.0)
    m.prism(0, -3.6, 17.2, 18.8, 1.0, dim(PALE_STEEL, 0.3), sides=6, top=dim(PALE_STEEL, 0.2), shadow=False)
    for k, a in enumerate((30, 150, 270)):
        if damaged and k == 2:
            continue
        r = 7.5 if not damaged else 6.0
        a += spin
        tip = (hub[0] + r * math.cos(math.radians(a)), hub[1], hub[2] + r * math.sin(math.radians(a)))
        m.strut(hub, tip, 0.45, lit(PALE_STEEL, 0.15), cap=lit(PALE_STEEL, 0.3), shadow=False)
    m.box(-0.6, -0.6, 19.5, 0.6, 0.6, 20.5, SUN_GOLD if not damaged else RUST, top=SUN_GOLD, order=3, shadow=False, accent=not damaged)
    if damaged:
        m.box(-3, 2, 3.6, 3, 5, 5, DAMAGE_SCORCH, top=DAMAGE_SCORCH, order=1, shadow=False)
    return m


def sghyd_mesh(damaged=False):
    """Hydrogen Plant: two hardened storage cylinders side by side, an
    electrolyser skid at the near corner, and a PV canopy at the back."""
    m = Mesh()
    plinth(m, 27, live=not damaged)
    tank = PALE_STEEL if not damaged else mix(PALE_STEEL, DAMAGE_SCORCH, 0.25)
    pipe = SUN_GOLD if not damaged else RUST
    for k, (cx, cy) in enumerate(((-11, 11), (11, -11))):
        r = 9
        m.prism(cx, cy, 2.2, 4.6, r + 1.4, dim(CONCRETE, 0.1), sides=12, top=lit(CONCRETE, 0.1))
        m.prism(cx, cy, 4.6, 24.0, r, tank, sides=12, top=lit(tank, 0.1))
        m.prism(cx, cy, 10.0, 12.6, r + 0.4, PANEL_BLUEBLACK, sides=12, top=PANEL_BLUEBLACK, shadow=False)
        m.prism(cx, cy, 18.8, 19.9, r + 0.4, pipe, sides=12, top=lit(pipe, 0.2), shadow=False, accent=not damaged)
        if not (damaged and k == 1):
            dome(m, cx, cy, 24.0, r, tank, steps=5)
        else:
            m.prism(cx, cy, 24.0, 25.2, r * 0.8, dim(tank, 0.45), sides=12, top=DAMAGE_SCORCH, shadow=False)
    m.strut((-15, 15, 22), (-15, 15, 33), 0.9, STEEL, cap=lit(STEEL, 0.3))
    m.box(-9, -9, 2.2, 9, 9, 3.4, dim(CONCRETE, 0.05), top=lit(CONCRETE, 0.12), shadow=False)
    m.box(-7, -7, 3.4, 7, 7, 10.5, STEEL, top=lit(STEEL, 0.2))
    for i in range(3):
        m.box(-5.5 + i * 4, -5, 10.5, -3 + i * 4, 5, 13.5, PANEL_BLUEBLACK, top=lit(PANEL_BLUEBLACK, 0.3))
    m.box(-6.8, -7.4, 5.5, 6.8, -6.9, 7.5, pipe, top=pipe, order=1, shadow=False, accent=not damaged)
    m.strut((-11, 11, 16), (0, 0, 16), 0.9, pipe, accent=not damaged)
    m.strut((11, -11, 16), (0, 0, 16), 0.9, pipe, accent=not damaged)
    m.strut((0, 0, 13.5), (0, 0, 16.5), 0.9, pipe, cap=lit(pipe, 0.3), accent=not damaged)
    m.strut((12, 12, 2.2), (12, 12, 8), 0.6, PALE_STEEL)
    m.strut((22, 22, 2.2), (22, 22, 8), 0.6, PALE_STEEL)
    m.quad((8, 16, 8), (18, 26, 8), (26, 18, 10.5), (16, 8, 10.5), lit(PANEL_BLUEBLACK, 0.3), order=2)
    # Planted strip along the near-left of the plot, ivy on the electrolyser
    # skid, a tree at the near-right corner (issue #108).
    bed(m, -23.5, -23.5, -11.5, -10.5, 2.2, lowcap=1.3, salt=12)
    shrub(m, -19, -19, 2.8, r=2.8)
    tuft(m, -14, -21, 2.8)
    tuft(m, -21, -13, 2.8)
    vines(m, -7, -5, 5, 3.4, 8.0, salt=13)
    tree(m, 22, -22, 2.2, h=8.0, r=4.5)
    shrub(m, 14, -22, 2.2, r=2.0)
    return m


def sgvlt_mesh(damaged=False, charge=SGVLT_STAGES - 1):
    """Battery Bank at charge level `charge` (0..SGVLT_STAGES-1): two
    containerised battery cabinets, the stored level read off a vertical
    gauge on the lit face of the front one."""
    m = Mesh()
    plinth(m, 13, live=not damaged)
    skid = _VLT_SKID if not damaged else mix(_VLT_SKID, DAMAGE_SCORCH, 0.3)
    m.box(0, 1, 2.2, 11, 12, 11, skid, top=lit(skid, 0.12))
    m.box(-11, -10, 2.2, 1, 2, 12.5, skid, top=lit(skid, 0.12))
    # Corrugation lines on the shaded faces, louvres on the lit one.
    for i in range(3):
        m.box(-9 + i * 3, -10.5, 4, -8.4 + i * 3, -9.9, 10.5, dim(skid, 0.3), top=dim(skid, 0.3), order=1, shadow=False)
        m.box(2 + i * 3, 0.5, 4, 2.6 + i * 3, 1.1, 9.5, dim(skid, 0.3), top=dim(skid, 0.3), order=1, shadow=False)
    gauge(m, -11, -8.5, 3.2, charge, total=SGVLT_STAGES - 1, pitch=1.05, width=5.0, live=not damaged)
    # Sedum on the front cabinet's roof (clear of its cooling unit), a shrub
    # and grasses in the yard beside it (issue #108).
    green_roof(m, -10.5, -9.5, 0.5, 1.5, 12.5, salt=10, path=False,
               keep=lambda x, y: (x + 6) ** 2 + (y + 4) ** 2 > 12)
    shrub(m, 6.5, -6, 2.2, r=2.3)
    tuft(m, 10, -2.5, 2.2)
    tuft(m, 2.5, -8.5, 2.2)
    # Cooling units on the roofs.
    for (x, y) in ((-6, -4), (5.5, 6.5)):
        m.prism(x, y, 12.5 if x < 0 else 11, (12.5 if x < 0 else 11) + 1.2, 2.4, PALE_STEEL, sides=8, top=dim(LEGACY_GRAY, 0.3), shadow=False)
    if damaged:
        m.box(2, 0.6, 5, 9, 1.2, 10, DAMAGE_SCORCH, top=DAMAGE_SCORCH, order=2, shadow=False)
    return m


def _scrap_tone(k):
    """Deterministic scrap tone for the Depot's heap layers: mixed plate,
    rust and bright cut edges."""
    return (RUST, dim(LEGACY_GRAY, 0.15), lit(LEGACY_GRAY, 0.28), lit(LEGACY_GRAY, 0.08), mix(RUST, LEGACY_GRAY, 0.5))[k % 5]


def _rcyd_scrap_col(x, y):
    """Per-pixel scrap tone, shared with the Hauler Drone's load so a laden
    rover and the Depot heap read as the same material."""
    k = (x * 5 + y * 3) % 7
    if k in (0, 3):
        return RUST
    if k == 1:
        return dim(LEGACY_GRAY, 0.15)
    if k in (5, 6):
        return lit(LEGACY_GRAY, 0.28)
    return lit(LEGACY_GRAY, 0.08)


def rcyd_mesh(damaged=False, charge=RCYD_STAGES - 1):
    """Recycling Depot holding `charge` of scrap (0..RCYD_STAGES-1): an open
    canopy bay with the heap growing under it, shredder cabinet and stack at
    the back, and a fill gauge on the cabinet."""
    m = Mesh()
    plinth(m, 13, live=not damaged)
    shell = _RCY_HALL if not damaged else mix(_RCY_HALL, DAMAGE_SCORCH, 0.3)
    for (x, y) in ((-10, -9), (10, -9), (-10, 9), (10, 9)):
        m.strut((x, y, 2.2), (x, y, 12.5), 0.7, shell, cap=lit(shell, 0.2))
    m.box(4, 3, 2.2, 11, 11, 9, shell, top=lit(shell, 0.15))
    m.prism(9, 9, 9, 15, 1.0, STEEL, sides=6, top=lit(STEEL, 0.3), shadow=False)
    gauge(m, 4, 4.5, 3.0, charge, total=RCYD_STAGES - 1, pitch=0.7, width=4.0, live=not damaged)
    # The heap: a stack of scrap plates, footprint and height following the fill level.
    if charge > 0:
        layers = (charge + 1) // 2
        for k in range(layers):
            r = 2.5 + charge * 0.75 - k * 1.5
            if r <= 1.2:
                break
            m.prism(-4, -3, 2.2 + k * 1.6, 2.2 + (k + 1) * 1.6, r, _scrap_tone(k + charge), sides=7,
                    top=_scrap_tone(k + charge + 2), phase=k * 0.4, shadow=(k == 0))
    # Sedum on the canopy roof (clear of the stack), weeds outside the posts (issue #108).
    if not damaged:
        m.box(-12, -11, 12.5, 12, 11, 13.8, shell, top=lit(shell, 0.25), shadow=False)
        green_roof(m, -11.5, -10.5, 11.5, 10.5, 13.8, salt=11,
                   keep=lambda x, y: (x - 9) ** 2 + (y - 9) ** 2 > 6)
    else:
        m.box(-12, -11, 12.5, 3, 11, 13.8, shell, top=lit(shell, 0.25), shadow=False)
        m.quad((3, -11, 12.5), (12, -11, 5), (12, 11, 5), (3, 11, 12.5), dim(shell, 0.3), order=1)
        green_roof(m, -11.5, -10.5, 2.5, 10.5, 13.8, salt=11)
    shrub(m, 11.5, -11.2, 2.2, r=1.8)
    tuft(m, -11.8, 3, 2.2)
    tuft(m, 11.8, -4, 2.2)
    return m


def sgfact_mesh(damaged=False, build=None, beacon=True):
    """Construction Yard: a vaulted space-frame fabrication hall with a PV
    field on its sunward flank, a team-colour door frame, and an open assembly
    yard under a gantry crane. `build` (0..1) moves the crane trolley along
    the beam for the 25-frame placed-building animation; `beacon=False` is
    the mast light's off frame in the idle animation (issue #109)."""
    m = Mesh()
    plinth(m, 25, z=2.0, live=not damaged)
    hall = PALE_STEEL if not damaged else mix(PALE_STEEL, DAMAGE_SCORCH, 0.15)
    m.box(-24, 0, 2, 24, 24, 17, hall, top=lit(hall, 0.1))
    n = 6
    for i in range(n):
        a0, a1 = math.pi * i / n, math.pi * (i + 1) / n
        x0, x1 = -24 * math.cos(a0), -24 * math.cos(a1)
        z0, z1 = 17 + 8 * math.sin(a0), 17 + 8 * math.sin(a1)
        m.quad((x0, 0, z0), (x1, 0, z1), (x1, 24, z1), (x0, 24, z0), lit(hall, 0.05), order=1)
        if 1 <= i <= 3 and not (damaged and i == 2):
            m.quad((x0 + 1, 3, z0 + 0.4), (x1 - 1, 3, z1 + 0.4), (x1 - 1, 21, z1 + 0.4), (x0 + 1, 21, z0 + 0.4), PANEL_BLUEBLACK, order=2)
        elif damaged and i == 2:
            m.quad((x0 + 1, 3, z0 + 0.4), (x1 - 1, 3, z1 + 0.4), (x1 - 1, 21, z1 + 0.4), (x0 + 1, 21, z0 + 0.4), DAMAGE_SCORCH, order=2)
    m.poly([(-24 * math.cos(math.pi * i / n), 0, 17 + 8 * math.sin(math.pi * i / n)) for i in range(n + 1)], hall, order=1)
    door = SUN_GOLD if not damaged else dim(SUN_GOLD, 0.4)
    m.box(-9, -0.6, 2, 9, 0.6, 16, dim(PANEL_BLUEBLACK, 0.3), top=dim(PANEL_BLUEBLACK, 0.3), order=1, shadow=False)
    m.box(-11, -1.2, 2, -9, 0.4, 18, door, top=lit(door, 0.2), order=2, shadow=False, accent=True)
    m.box(9, -1.2, 2, 11, 0.4, 18, door, top=lit(door, 0.2), order=2, shadow=False, accent=True)
    m.box(-11, -1.2, 16, 11, 0.4, 18, door, top=lit(door, 0.2), order=2, shadow=False, accent=True)
    m.box(-24.6, 6, 9, -23.8, 20, 12, PANEL_BLUEBLACK, top=PANEL_BLUEBLACK, order=1, shadow=False)
    vines(m, -24, 1, 23, 2.0, 8.5, salt=4, dark=True)
    for y in (-6, -18):
        m.strut((-20, y, 2), (-20, y, 17), 1.2, STEEL, cap=lit(STEEL, 0.3))
        m.strut((20, y, 2), (20, y, 17), 1.2, STEEL, cap=lit(STEEL, 0.3))
        m.strut((-20, y, 16.5), (20, y, 16.5), 1.2, STEEL if not damaged else dim(STEEL, 0.3))
    m.strut((-20, -6, 17), (-20, -18, 17), 0.8, STEEL)
    m.strut((20, -6, 17), (20, -18, 17), 0.8, STEEL)
    # Crane trolley: parked right of centre when idle, traversing during the build animation.
    t = 0.62 if build is None else build
    tx = -14 + 28 * t
    trolley = SUN_GOLD if not damaged else dim(SUN_GOLD, 0.4)
    m.box(tx - 3.5, -14, 16.2, tx + 3.5, -10, 19.5, trolley, top=lit(trolley, 0.3), order=2, accent=True)
    if build is not None:
        # Hook line and the load, lowered onto the chassis mid-traverse.
        drop = 4 + 6 * math.sin(math.pi * build)
        m.strut((tx, -12, 16.2), (tx, -12, 16.2 - drop), 0.3, POLE_DARK, shadow=False)
    m.box(-6, -15, 2, 6, -8, 6, dim(GREEN_PRIMARY, 0.1), top=lit(GREEN_PRIMARY, 0.2))
    # Planted near-left corner of the yard, shrubs and grasses along its front
    # edge, a tree at the near-right corner (issue #108).
    bed(m, -22.5, -22.5, -12, -19.0, 2.0, lowcap=1.4, salt=7, step=3.0)
    shrub(m, -19, -21.0, 2.6, r=2.6)
    tuft(m, -14.5, -21.5, 2.6)
    tree(m, 22.0, -21.5, 2.0, h=8.5, r=4.8)
    shrub(m, 12, -22.0, 2.0, r=2.4)
    tuft(m, 16.5, -22.5, 2.0)
    m.strut((21, 21, 20), (21, 21, 32 if not damaged else 24), 0.8, STEEL, cap=RUST if damaged else None)
    if not damaged and beacon:
        m.box(20.2, 20.2, 32, 21.8, 21.8, 33.4, SUN_GOLD, top=lit(SUN_GOLD, 0.3), order=4, shadow=False, accent=True)
    elif not damaged:
        m.box(20.2, 20.2, 32, 21.8, 21.8, 33.4, dim(PALE_STEEL, 0.45), top=dim(PALE_STEEL, 0.3), order=4, shadow=False)
    if damaged:
        m.box(-22, -0.5, 4, -14, 0.2, 12, DAMAGE_SCORCH, top=DAMAGE_SCORCH, order=2, shadow=False)
        m.box(6, -20, 2, 14, -13, 4, mix(STEEL, DAMAGE_SCORCH, 0.5), top=DAMAGE_SCORCH)
    return m


# Idle overlays (issue #109): sheets WithIdleOverlay draws *over* the body, at
# the body's own frame size and origin so no offset is needed. Two reasons a
# moving part is an overlay rather than body frames: the Depot's body is a
# WithResourceLevelSpriteBody stage strip (the frame is picked by fill level,
# so it cannot animate), and the grid-strained lamps only exist while a
# condition holds, which is exactly what RequiresCondition on an overlay is.
STRAIN_ORANGE = (252, 92, 0)        # palette 229: the 'strained' warning tone. Redder than AMBER on purpose:
                                    # a mesh face is *shaded*, and shaded amber (~(150,85,10)) lies inside
                                    # _index_for's gold radius and goes onto the remap ramp; shaded red-orange
                                    # stays next to the palette's own (180,72,0) instead.
FAULT_RED = (204, 0, 0)             # palette 233
LAMP_OFF = dim(LEGACY_GRAY, 0.2)    # an unlit lamp: plain dark grey, nowhere near the gold ramp


def rcyd_smoke_mesh(phase=0):
    """Recycling Depot stack puffs: three puffs at staggered ages rising from
    the shredder stack and drifting downwind. Opaque greys shrinking to
    nothing rather than a fade -- indexed alpha is 1-bit."""
    m = Mesh()
    for j in range(3):
        age = (phase + j * 8 / 3) % 8
        if age > 6.5:
            continue
        z = 15.3 + age * 1.1
        r = 0.8 + age * 0.22 if age < 4.5 else 1.8 - (age - 4.5) * 0.45
        col = (196, 196, 196) if age < 2.5 else ((160, 160, 160) if age < 4.5 else (124, 124, 124))
        m.prism(9 + age * 0.3, 9 + age * 0.15, z, z + r * 0.9, r, col, sides=6, top=lit(col, 0.15), shadow=False)
    return m


def sgdai_strained_mesh(phase=0, damaged=False):
    """grid-strained overlay for the Datacenter: the green data line goes
    amber and the mast beacon blinks amber over the body's own team-colour
    one (the damaged body has no beacon, so its variant is the line alone)."""
    # Fixed-palette tones only, and none that shade into the gold radius: a
    # dark amber for the off lamp and a shaded amber line both landed on the
    # remap ramp on the first renders (see STRAIN_ORANGE). An overlay sheet
    # must carry zero remap-ramp pixels.
    m = Mesh()
    m.box(-16, -15.5, 3.2, 16, -14.9, 4.0, STRAIN_ORANGE, top=STRAIN_ORANGE, order=1, shadow=False)
    if not damaged:
        on = phase != 3
        m.box(14.3, -12.7, 22, 15.7, -11.3, 23.2, STRAIN_ORANGE if on else LAMP_OFF, top=AMBER if on else LAMP_OFF,
              order=4, shadow=False)
    return m


def sgcry_strained_mesh(phase=0, damaged=False):
    """grid-strained overlay for the Cryptominer: every status pip dark, with
    a red fault blink on the back-left rack, over the body's amber flicker."""
    m = Mesh()
    racks = [((-17, -12, -5, 1), 12), ((-3, -15, 10, -3), 9), ((-14, 4, -1, 17), 15), ((3, 1, 16, 15), 11)]
    for k, ((x0, y0, x1, y1), hgt) in enumerate(racks):
        if damaged and k == 1:
            continue
        pip = FAULT_RED if (k == 0 and phase in (0, 1)) else LAMP_OFF
        m.box(x0 - 0.5, y0 + 1.5, 2.2 + hgt - 2.2, x0 + 0.1, y0 + 3.5, 2.2 + hgt - 1.2, pip, top=pip, order=2, shadow=False)
    return m


# ------------------------------------------------------------------ pipeline

MESHES = {
    "sgpwr": ("2x3", sgpwr_mesh), "sgapwr": ("3x3", sgapwr_mesh), "sgcry": ("2x3", sgcry_mesh),
    "sgdai": ("2x3", sgdai_mesh), "sgdrn": ("2x3", sgdrn_mesh), "sgdra": ("2x3", sgdra_mesh),
    "sgshl": ("2x2", sgshl_mesh), "sgsns": ("1x1", sgsns_mesh), "sgrel": ("1x1", sgrel_mesh),
    "sgwnd": ("1x1", sgwnd_mesh), "sghyd": ("3x3", sghyd_mesh), "sgvlt": ("1x1", sgvlt_mesh),
    "rcyd": ("1x1", rcyd_mesh), "sgfact": ("fact", sgfact_mesh),
}


def mesh_draw_fn(name):
    """A draw_fn(sd, w, h, **kw) for make_icon / make_frames: the plain shaded
    model at the frame's own origin."""
    fam, fn = MESHES[name]
    w, h, half = FAM[fam]
    ox, oy = w // 2, _oy(h, half)
    def draw(sd, w_, h_, **kw):
        fn(**kw).draw(sd, ox, oy, BUILDING_YAW)
    return draw


ACCENT_COVERAGE = 90   # of 255: a native pixel at least ~35% covered by accent faces is re-stamped


def mesh_frame(name, **kw):
    """One finished frame of a roster building (see _mesh_frame)."""
    fam, fn = MESHES[name]
    return _mesh_frame(fam, fn, **kw)


def _mesh_frame(fam, fn, **kw):
    """One finished frame: the shaded model, with every accent face re-stamped
    at native resolution so it lands on the player-remap ramp.

    The stamp is needed for the same reason the old _vlt_accents/_sgrel_accents
    tables were: the 4x LANCZOS downscale blends a 1-2px gold strip with the
    concrete beside it and the result quantises to a *fixed* yellow. Measured
    on the drafts, about half the band's pixels came back that way. Two extra
    render passes fix it generally: an occlusion-correct coverage mask (accent
    faces white, everything else black, drawn in painter's order) says *which*
    native pixels the band owns, and an accent-only colour pass on a solid gold
    background says what shade each one should be, without ever blending with
    a non-gold neighbour."""
    w, h, half = FAM[fam]
    return _mesh_render(fn(**kw), w, h, w // 2, _oy(h, half), BUILDING_YAW)


def _mesh_render(mesh, w, h, ox, oy, yaw, decals=None):
    """The shaded model at (ox, oy, yaw) with its accent faces re-stamped --
    the frame path shared by the roster buildings (via _mesh_frame), the two
    defence pedestals and the Grid Defense Turret's station, which sit at
    their own origins. `decals(sd, w, h)` paints 2D damage marks over the
    finished frame."""
    body = render(lambda sd, w_, h_: mesh.draw(sd, ox, oy, yaw), w, h)
    mask_big = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
    mesh.draw(SD(mask_big), ox, oy, yaw, mode="mask")
    cov = mask_big.getchannel("R").resize((w, h), Image.LANCZOS).load()
    col_big = Image.new("RGBA", (w * SS, h * SS), SUN_GOLD + (255,))
    mesh.draw(SD(col_big), ox, oy, yaw, mode="accent")
    col = col_big.resize((w, h), Image.LANCZOS).load()
    px = body.load()
    for y in range(h):
        for x in range(w):
            if cov[x, y] >= ACCENT_COVERAGE:
                # Snap to the nearest gold reference shade: those are, by
                # construction, the colours _index_for routes onto the ramp.
                px[x, y] = min(_GOLD_REFS, key=lambda ref: _d2(ref, col[x, y][:3])) + (255,)
    if decals is not None:
        body = Image.alpha_composite(body, render(decals, w, h))
    return body


# Idle animation (issue #109): the frames each animated building's body sheet
# carries, as kwargs for its *_mesh() -- idle frames first, then damaged.
# `idle:` Length, `damaged-idle:` Start/Length and the Tick per state live in
# sequences/structures.yaml and must agree with these counts; the engine's
# --check-missing-sprites reports a sheet that is short. Buildings not listed
# keep the two-frame idle/damaged sheet.
ANIM = {
    # Three blades, so a 120-degree turn is one visual cycle: 24 x 5 degrees
    # at Tick 100 is 2.4 s per cycle, a stately 7 s per revolution. Damaged
    # (two blades) the cycle is a full turn: 24 x 15 degrees at Tick 400,
    # a quarter slower.
    "sgwnd": ([dict(spin=5.0 * i) for i in range(24)], [dict(damaged=True, spin=15.0 * i) for i in range(24)]),
    # The dish sweeps a full circle in 16 steps at Tick 250 (4 s); the fallen dish is still.
    "sgsns": ([dict(sweep=22.5 * i) for i in range(16)], [dict(damaged=True)]),
    # Beacons: on five frames, off three, Tick 200 (1.6 s). Damaged masts carry no beacon.
    "sgdai": ([dict(beacon=i < 5) for i in range(8)], [dict(damaged=True)]),
    "sgshl": ([dict(beacon=i < 5) for i in range(8)], [dict(damaged=True)]),
    # Pad-ring chase lights, Tick 150; the damaged ring is dead.
    "sgdrn": ([dict(chase=i) for i in range(8)], [dict(damaged=True)]),
    # Amber status pips flicker, Tick 150.
    "sgcry": ([dict(flicker=i) for i in range(8)], [dict(damaged=True)]),
    # The arc between the terminals flickers, Tick 120.
    "sgrel": ([dict(arc=i) for i in range(6)], [dict(damaged=True)]),
}


def building_sheet(name):
    """Every body-sheet frame of a roster building (idle states, then damaged)
    as one indexed strip, plus the frames themselves."""
    idle_kws, dmg_kws = ANIM.get(name, ([{}], [dict(damaged=True)]))
    frames = [mesh_frame(name, **kw) for kw in idle_kws + dmg_kws]
    fam, _ = MESHES[name]
    w, h, _ = FAM[fam]
    return indexed_strip(frames, [silhouette_shadow(f, 2, 2) for f in frames], w, h), frames



# --- Death rubble for the volumetric buildings ------------------------------
#
# The wreck fills the building's *diamond* footprint, not a horizontal strip:
# a pile the shape of the old flat pad would sit at the wrong angle under a
# building that stood on a 45-degree plinth a moment earlier.

def _diamond_pt(ox, oy, half, ang, scale=1.0):
    """A point on the plinth diamond's outline at angle `ang` (radians from
    screen-right), pulled toward the centre by `scale`."""
    hx, hy = half * math.sqrt(2) * scale, half * math.sqrt(2) / 2 * scale
    c, s = math.cos(ang), math.sin(ang)
    r = 1.0 / (abs(c) / hx + abs(s) / hy)   # diamond (L1 ball) radius in that direction
    return (ox + r * c, oy + r * s)


def _rubble_diamond(sd, ox, oy, half, seed):
    """Collapsed mass over the footprint: a jagged diamond of broken material
    with lit edges on the key-light side and charred pockets, the same
    grammar the strip version used (stock powrdead.shp: chaotic mid-tone mass,
    not one dark polygon)."""
    pts = []
    n = 28
    for i in range(n):
        j = ((i * 37 + seed * 53) % 17) / 16.0
        pts.append(_diamond_pt(ox, oy, half, i * 2 * math.pi / n, 0.72 + 0.26 * j))
    sd.poly(pts, fill=dim(CONCRETE, 0.12))
    tones = (LEGACY_GRAY_DARK, lit(CONCRETE, 0.12), DAMAGE_SCORCH, dim(CONCRETE, 0.42), lit(CONCRETE, 0.3))
    for k in range(half * 2):
        ang = ((k * 47 + seed * 11) % 360) * math.pi / 180
        sc = 0.15 + ((k * 29 + seed * 7) % 60) / 100.0
        bx, by = _diamond_pt(ox, oy, half, ang, sc)
        bw = 2 + (k + seed) % 3
        sd.rect([bx, by, bx + bw, by + 1], fill=tones[(k + seed) % 5])
    # Lit crest along the upper-left edges, where the key light catches broken slab.
    for i in range(n // 4, n // 2 + n // 4, 2):
        x, y = pts[i]
        sd.px(x, y - 0.5, lit(CONCRETE, 0.3))
    for k in range(2):
        cx_, cy_ = _diamond_pt(ox, oy, half, (0.9 + 2.2 * k), 0.3)
        sd.ellipse([cx_ - 4, cy_ - 1.5, cx_ + 4, cy_ + 1.5], fill=DAMAGE_SCORCH)


def _dead_origin(fam):
    w, h, half = FAM[fam]
    return w // 2, _oy(h, half), half


def sgpwr_dead_draw(sd, w=FAM23_W, h=FAM23_H):
    """Solar Array rubble: collectors down, one still leaning on its strut."""
    ox, oy, half = _dead_origin("2x3")
    _rubble_diamond(sd, ox, oy, half, seed=11)
    _slab(sd, ox - 9, oy + 1, 20, 5, mix(PANEL_BLUEBLACK, LEGACY_GRAY, 0.35), lean=0.8)
    _slab(sd, ox + 9, oy - 5, 16, 5, dim(PANEL_BLUEBLACK, 0.2), lean=-3.0)
    sd.line([(ox + 4, oy - 3), (ox + 7, oy + 2)], fill=POLE_DARK, width=1.1)
    _conduit_stub(sd, ox - 20, ox - 6, oy + 6)
    _embers(sd, [(ox - 12, oy + 2), (ox + 2, oy + 4), (ox + 14, oy - 1), (ox - 3, oy - 4)])


def sgapwr_dead_draw(sd, w=FAM33_W, h=FAM33_H):
    """Advanced Solar Array rubble: a wider spill of collapsed collectors."""
    ox, oy, half = _dead_origin("3x3")
    _rubble_diamond(sd, ox, oy, half, seed=12)
    _slab(sd, ox - 16, oy + 2, 22, 5, mix(PANEL_BLUEBLACK, LEGACY_GRAY, 0.35), lean=1.0)
    _slab(sd, ox + 16, oy - 4, 20, 5, dim(PANEL_BLUEBLACK, 0.2), lean=-2.4)
    _slab(sd, ox + 2, oy - 9, 18, 5, dim(PANEL_BLUEBLACK, 0.1), lean=1.8)
    sd.line([(ox - 6, oy - 7), (ox - 3, oy - 1)], fill=POLE_DARK, width=1.1)
    _conduit_stub(sd, ox - 28, ox - 14, oy + 4)
    _conduit_stub(sd, ox + 10, ox + 24, oy + 6)
    _embers(sd, [(ox - 20, oy + 3), (ox, oy + 6), (ox + 18, oy + 1), (ox - 8, oy - 3), (ox + 26, oy - 2)])


def sghyd_dead_draw(sd, w=FAM33_W, h=FAM33_H):
    """Hydrogen Plant rubble: both cylinders split and toppled, hoops sprung."""
    ox, oy, half = _dead_origin("3x3")
    _rubble_diamond(sd, ox, oy, half, seed=9)
    sd.ellipse([ox - 30, oy - 8, ox - 8, oy + 1], fill=dim(PALE_STEEL, 0.4))
    sd.ellipse([ox - 27, oy - 6.5, ox - 11, oy - 1], fill=dim(PANEL_BLUEBLACK, 0.15))
    sd.arc([ox - 30, oy - 8, ox - 8, oy + 1], 190, 350, fill=lit(PALE_STEEL, 0.1), width=0.7)
    _slab(sd, ox + 16, oy - 2, 28, 8, dim(PALE_STEEL, 0.3), lean=1.6)
    sd.line([(ox + 2, oy - 5), (ox + 30, oy - 3)], fill=dim(PALE_STEEL, 0.5), width=0.8)
    sd.arc([ox - 4, oy - 6, ox + 14, oy + 3], 200, 20, fill=dim(SUN_GOLD, 0.35), width=1.1)
    _conduit_stub(sd, ox - 10, ox + 4, oy + 5)
    _embers(sd, [(ox - 18, oy - 1), (ox + 6, oy + 2), (ox + 22, oy + 1), (ox - 4, oy + 6), (ox + 14, oy - 6)])


def sgfact_dead_draw(sd, w=72, h=72):
    """Construction Yard rubble: the vault collapsed into the yard, a crane leg
    still standing, the door frame's gold on the ground."""
    ox, oy, half = _dead_origin("fact")
    _rubble_diamond(sd, ox, oy, half, seed=5)
    _slab(sd, ox - 6, oy - 8, 30, 7, dim(PALE_STEEL, 0.3), lean=1.2)
    _slab(sd, ox + 12, oy - 2, 18, 5, PANEL_BLUEBLACK, lean=-2.0)
    _slab(sd, ox - 16, oy + 2, 14, 5, dim(PALE_STEEL, 0.45), lean=2.4)
    sd.line([(ox + 16, oy + 8), (ox + 16, oy - 6)], fill=STEEL, width=1.2)
    sd.line([(ox + 16, oy - 6), (ox + 26, oy - 3)], fill=dim(STEEL, 0.3), width=1.0)
    _conduit_stub(sd, ox - 8, ox + 6, oy + 4)
    _conduit_stub(sd, ox - 26, ox - 16, oy - 1)
    _embers(sd, [(ox - 10, oy - 2), (ox + 4, oy + 6), (ox + 20, oy + 2), (ox - 20, oy + 5), (ox + 2, oy - 10)])


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


SGTUR_SEAT_TOP = 3.8    # turntable seat top above the pad's ground contact (see sgtur_pad_mesh)


def sgtur_mesh(damaged=False):
    """The rotating station in world units (x east, y north, z up), zeroed on
    the pivot at the turntable seat's top and pointing north at facing 0.

    Rebuilt for issue #112 on the photographic cameo's read: a pale armoured
    block (PALE_STEEL, so lit and shaded faces have room for real value
    steps -- the old blue-black hull had none, which is most of why it read
    flat), bevelled between a wide lower hull and a narrower upper hull, a
    dark recessed weapon port on the front-right, and a short, thick gun
    with a recoil sleeve and muzzle ring instead of the old thin bar. The
    turntable is a 32-gon collar: 32 facings x 11.25 degrees map it onto
    itself, so it is pixel-identical under every facing (sam2.shp's
    fixed-mount rule) without needing to be drawn as an ellipse."""
    hull = PALE_STEEL if not damaged else mix(PALE_STEEL, DAMAGE_SCORCH, 0.3)
    dark = mix(PANEL_BLUEBLACK, LEGACY_GRAY, 0.35)
    barrel = _TUR_BARREL if not damaged else mix(_TUR_BARREL, DAMAGE_SCORCH, 0.5)
    accent = SUN_GOLD if not damaged else RUST
    collar = dim(LEGACY_GRAY, 0.2)
    m = Mesh()
    # Turntable collar the hull turns on.
    m.prism(0, 0, 0.0, 1.4, 8.6, collar, sides=32, top=lit(collar, 0.12))
    # Lower hull, the bevel ring, then the upper hull.
    lx0, ly0, lx1, ly1, lz = -8.0, -7.0, 8.0, 5.0, 5.4
    ux0, uy0, ux1, uy1, uz = -6.4, -5.6, 6.4, 3.6, 7.0
    m.box(lx0, ly0, 1.4, lx1, ly1, lz, hull, top=lit(hull, 0.08), top_face=False)
    m.quad((lx0, ly0, lz), (lx1, ly0, lz), (ux1, uy0, uz), (ux0, uy0, uz), hull)          # front glacis (-y)
    m.quad((lx1, ly1, lz), (lx0, ly1, lz), (ux0, uy1, uz), (ux1, uy1, uz), hull)          # rear
    m.quad((lx1, ly0, lz), (lx1, ly1, lz), (ux1, uy1, uz), (ux1, uy0, uz), hull)          # +x
    m.quad((lx0, ly1, lz), (lx0, ly0, lz), (ux0, uy0, uz), (ux0, uy1, uz), hull)          # -x
    m.box(ux0, uy0, uz, ux1, uy1, 10.6, hull, top=lit(hull, 0.14), shadow=False)
    m.solids.append([(x, y, z) for x in (ux0, ux1) for y in (uy0, uy1) for z in (uz, 10.6)])
    # Conduit band wrapping the lower hull, proud so it shades on every face.
    m.box(lx0 - 0.4, ly0 - 0.4, 3.0, lx1 + 0.4, ly1 + 0.4, 4.2, accent, top=lit(accent, 0.25),
          order=1, shadow=False, top_face=False, accent=True)
    # Weapon port: a dark recess in the upper hull's front face, to the right
    # of centre, that the gun comes out of.
    m.box(0.2, uy1 - 0.2, 7.5, 5.8, uy1 + 0.5, 10.1, dark, top=dim(dark, 0.3), order=1, shadow=False)
    # Gun: recoil sleeve, barrel, muzzle ring -- square-section struts along +y.
    tip = 16.6 if not damaged else 12.8
    gx, gz = 3.0, 8.8
    m.strut((gx, uy1 + 0.2, gz), (gx, uy1 + 4.6, gz), 2.2, dark, cap=dark, order=2, shadow=False)
    m.strut((gx, uy1 + 4.4, gz), (gx, tip, gz), 1.55, barrel, cap=dim(barrel, 0.4), order=2)
    if not damaged:
        m.strut((gx, tip - 2.4, gz), (gx, tip + 0.4, gz), 2.0, lit(barrel, 0.15), cap=DAMAGE_SCORCH,
                order=3, shadow=False)
        m.strut((gx, tip - 0.6, gz - 2.3), (gx, tip + 0.2, gz - 2.3), 0.5, accent, cap=accent,
                order=3, shadow=False, accent=True)
    # Sensor block on the rear-left of the roof with its status pip, and a
    # thin mast (snapped when damaged).
    m.box(-5.6, -5.2, 10.6, -2.6, -2.2, 12.8, dim(hull, 0.25),
          top=(GREEN_ACCENT if not damaged else dim(GREEN_ACCENT, 0.55)), shadow=False)
    m.strut((-4.1, -3.7, 12.8), (-4.1, -3.7, 17.2 if not damaged else 14.0), 0.4, PALE_STEEL,
            cap=(accent if not damaged else DAMAGE_SCORCH), shadow=False)
    # Roof hatch, right of centre.
    m.prism(2.6, -2.6, 10.6, 11.3, 2.1, dim(hull, 0.12), sides=8, top=lit(hull, 0.05), shadow=False)
    # Capacitor drums on the lit flank -- the grid-fed part of the turret --
    # lying along the hull with a team-coloured end cap each.
    for z in (3.2, 6.3):
        m.strut((-9.6, -6.0, z), (-9.6, 1.0, z), 1.25, dim(LEGACY_GRAY, 0.15), cap=accent,
                order=1, shadow=False, accent=False)
        m.box(-10.6, 1.0, z - 1.0, -8.6, 1.5, z + 1.0, accent, top=lit(accent, 0.2),
              order=2, shadow=False, accent=True)
    return m


def _sgtur_station_origin(w, h):
    """Screen origin of the station: the pad's turntable seat top."""
    return w // 2, h // 2 + SGTUR_PIVOT_DY + SGTUR_PAD_H - SGTUR_SEAT_TOP


def sgtur_turret_draw(sd, w, h, damaged=False, facing=0.0):
    ox, oy = _sgtur_station_origin(w, h)
    sgtur_mesh(damaged).draw(sd, ox, oy, facing)
    if damaged:
        _sgtur_damage_decals(sd, w, h)


def _sgtur_damage_decals(sd, w, h):
    """Blown roof panel and a rust streak down the hull, on the fixed
    top-left the key light comes from (so they never spin with the gun the
    way the old rotated-image damage decal did)."""
    ox, oy = _sgtur_station_origin(w, h)
    sd.ellipse([ox - 5.0, oy - 12.0, ox - 1.0, oy - 9.2], fill=DAMAGE_SCORCH + (235,))
    sd.ellipse([ox - 4.2, oy - 11.4, ox - 2.0, oy - 10.0], fill=(0, 0, 0, 235))
    sd.rect([ox + 5.2, oy - 6.5, ox + 6.0, oy - 2.5], fill=RUST + (220,))


def sgtur_shadow_draw(sd, w, h, damaged=False, facing=0.0):
    ox, oy = _sgtur_station_origin(w, h)
    sgtur_mesh(damaged).draw_shadow(sd, ox, oy, facing)


SGTUR_SWEEP_FRAMES = 16     # idle scan frames per facing (issue #113); `turret:` Length
SGTUR_SWEEP_DEG = 15.0      # scan amplitude either side of the facing, degrees
SGTUR_LAMP_FRAMES = 8       # pad status lamp: on 5, off 3; `idle:` Length


def sgtur_frames(damaged=False, n=32, sweep=False):
    """One genuine viewpoint per facing: frame 0 = north, winding
    counter-clockwise (the convention heli.shp's 32-facing sheet confirms).

    With `sweep`, each facing carries SGTUR_SWEEP_FRAMES frames in which the
    station scans SGTUR_SWEEP_DEG either side of that facing on a sine, so an
    idle turret looks around a little (issue #113). The engine indexes
    facing * Length + frame, so the strip is facing-major. The rules switch
    to the static `aim:` frames while the turret is actually aiming, which is
    what keeps the gun on its target."""
    bodies, shadows = [], []
    phases = range(SGTUR_SWEEP_FRAMES) if sweep else (0,)
    for i in range(n):
        for ph in phases:
            deg = i * (360.0 / n)
            if sweep:
                deg += SGTUR_SWEEP_DEG * math.sin(2 * math.pi * ph / SGTUR_SWEEP_FRAMES)
            bodies.append(_mesh_render(sgtur_mesh(damaged), SGTUR_W, SGTUR_H,
                                       *_sgtur_station_origin(SGTUR_W, SGTUR_H), deg,
                                       decals=_sgtur_damage_decals if damaged else None))
            shadows.append(render_shadow_mask(sgtur_shadow_draw, SGTUR_W, SGTUR_H,
                                              damaged=damaged, facing=deg))
    return bodies, shadows


def sgtur_base_draw(sd, w, h, damaged=False):
    """Three-quarter view for the programmatic cameo fallback."""
    sgtur_turret_draw(sd, w, h, damaged=damaged, facing=28.0)


SGTUR_PAD_H = 2.4       # hardstand slab height, world units
SGTUR_PAD_R = 15.0      # octagon circumradius; its top face centre is the station's pivot


def sgtur_pad_mesh(lamp=True):
    """The fixed emplacement pad as a solid (issue #111): an octagonal
    concrete slab with a raised turntable seat, anchor bolts on the corner
    flats, the team-coloured cable trench feeding the mount from the camera
    side, and a fringe of grass around the slab. The top face's centre is the
    pivot the station's turntable sits on (SGTUR_PIVOT_DY), and the seat's
    radius matches the turntable ring drawn in the turret sheet."""
    con = CONCRETE
    m = Mesh()
    ph = math.pi / 8
    base = LEGACY_GRAY_DARK
    m.prism(0, 0, 0.0, SGTUR_PAD_H, SGTUR_PAD_R, con, sides=8, top=lit(con, 0.22), phase=ph)
    # Turntable seat: a dark race ring with a lighter bearing plate inside it
    # (its top is SGTUR_SEAT_TOP, where the station's collar sits). 32-gons,
    # the same count as the station's collar.
    m.prism(0, 0, SGTUR_PAD_H, SGTUR_PAD_H + 1.0, 11.0, base, sides=32, top=lit(base, 0.3), shadow=False)
    m.prism(0, 0, SGTUR_PAD_H + 1.0, SGTUR_SEAT_TOP, 9.4, dim(con, 0.05), sides=32,
            top=lit(con, 0.16), shadow=False)
    for i in range(4):
        ang = ph + i * math.pi / 2 + math.pi / 4
        m.prism(12.6 * math.cos(ang), 12.6 * math.sin(ang), SGTUR_PAD_H, SGTUR_PAD_H + 0.7, 0.7,
                lit(LEGACY_GRAY_DARK, 0.35), sides=6, top=lit(LEGACY_GRAY_DARK, 0.6), shadow=False)
    m.box(-2.4, -15.4, SGTUR_PAD_H, 2.4, -11.2, SGTUR_PAD_H + 0.7, SUN_GOLD, top=lit(SUN_GOLD, 0.2),
          order=1, shadow=False, accent=True)
    # Status lamp on the near-right rim, mirroring the grid-strained fault
    # lamp's spot on the near-left (issue #109's overlay), blinking green
    # while the pad is powered (issue #113). Off is plain dark grey.
    lamp_col = lit(GREEN_ACCENT, 0.2) if lamp else dim(con, 0.5)
    m.box(8.4, -10.6, SGTUR_PAD_H, 10.0, -9.4, SGTUR_PAD_H + 1.2, dim(con, 0.3), top=dim(con, 0.2),
          order=1, shadow=False)
    m.box(8.6, -10.4, SGTUR_PAD_H + 1.2, 9.8, -9.6, SGTUR_PAD_H + 1.9, lamp_col, top=lamp_col,
          order=2, shadow=False)
    # Expansion-joint groove across the slab, so the top face is not one flat tone.
    m.box(-13.0, -0.5, SGTUR_PAD_H, -11.4, 0.5, SGTUR_PAD_H + 0.15, dim(con, 0.35), order=1, shadow=False)
    m.box(11.4, -0.5, SGTUR_PAD_H, 13.0, 0.5, SGTUR_PAD_H + 0.15, dim(con, 0.35), order=1, shadow=False)
    grass_ring(m, SGTUR_PAD_R + 2.2, 13, salt=77)
    return m


def _sgtur_pad_origin(w, h):
    return w // 2, h // 2 + SGTUR_PIVOT_DY + SGTUR_PAD_H


def sgtur_pad_draw(sd, w, h, damaged=False):
    """The fixed emplacement pad the rotating station stands on (plain model,
    for the build-up strip; the shipped frame is sgtur_pad_frame).

    Previously stock gunmake.shp (the Turret's own concrete pad), which also
    meant the build-up was a different building's -- see issue #74. Drawn to
    the same contact point the station's turntable sits on (SGTUR_PIVOT_DY),
    so the two line up."""
    ox, oy = _sgtur_pad_origin(w, h)
    sgtur_pad_mesh().draw(sd, ox, oy, 0.0)


def sgtur_pad_frame(lamp=True):
    ox, oy = _sgtur_pad_origin(SGTUR_W, SGTUR_H)
    return _mesh_render(sgtur_pad_mesh(lamp), SGTUR_W, SGTUR_H, ox, oy, 0.0)


def sgtur_strained_draw(sd, w, h, phase=0):
    """grid-strained overlay for the turret pad (issue #109): an amber fault
    lamp blinking on the pad's near-left rim, clear of the station on top."""
    cy = h // 2 + SGTUR_PIVOT_DY
    cx = w // 2
    x, y = cx - 15.0 * 0.62, cy + 8.0 * 0.62
    sd.rect([x - 1.0, y - 1.0, x + 1.0, y + 0.6], fill=dim(CONCRETE, 0.3))
    if phase != 3:
        sd.rect([x - 0.8, y - 2.6, x + 0.8, y - 1.0], fill=AMBER)


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
ARC, ARC_LIT = 144, 15                          # pale green / white -- the same
                                                # pair the arczap projectile uses

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


def _disr_spark_level(p):
    """Bolt intensity per shoot phase: brief windup, bright arc for most of
    the burst, short decay, one hold frame. The Disruptor fires a 15-shot
    burst one tick apart, and WithInfantryBody restarts the shoot sequence on
    every PreparingAttack, so the animation only really plays from the last
    shot's call onward -- the weapon's FireDelay is tuned so the arczap
    projectiles land inside phases 2-14 (docs/BACKLOG.md issue #110)."""
    if p < 2:
        return 0
    if p < 10:
        return 2
    if p < 15:
        return 1
    return 0


def _disr_shoot(facing, p):
    """16-phase discharge: brief windup, bright arc, decay, then hold."""
    spark = _disr_spark_level(p)
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
        level = _disr_spark_level(shoot)
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
# Arc discharge projectile (issue #110): the sheet behind the `arczap` image
# both ArcDischarge and Disruptor draw with `Projectile: TeslaZap`.
#
# The engine's TeslaZapRenderable walks from muzzle to target in 8px screen
# steps and stamps one sprite per step, centred on the step's midpoint, picking
# the frame by the step's direction: 0 = "\\" diagonal, 1 = horizontal,
# 2 = vertical, 3 = "/" diagonal (see Steps[] in TeslaZapRenderable.cs). Two
# `dim` paths wander first, one `bright` path is laid over them. So each frame
# is an 8px segment through the frame centre, and consecutive stamps butt up
# end to end -- the jaggedness comes from the renderer's wandering, not from
# the segment art. Stock `litning.shp` is the same four-frame pair in blue;
# this is the Sungrid one in the trooper's own pale-green/white (ARC/ARC_LIT),
# so the bolt reads as the same discharge that leaves the electrode in the
# disr.png shoot frames, and stays distinct from the Tesla Coil's blue.
#
# Drawn on the `effect` palette (temperat.pal, ShadowIndex 4): index 4 is the
# shadow stencil there, so the bright green at index 4 is off limits; every
# index used here is a plain colour entry.
# ---------------------------------------------------------------------------

ZAP_W, ZAP_H = 12, 12
ZAP_CORE_BRIGHT, ZAP_HALO_BRIGHT = ARC_LIT, ARC           # white core, pale green edge
ZAP_CORE_DIM, ZAP_HALO_DIM = 145, 147                     # green core, deeper green kinks
# Perpendicular wobble per pixel along the 8px segment, in {-1, 0, 1}. Both
# ends sit on the centre line so consecutive stamps still join; the two
# tables differ so the dim paths never line up with the bright one. A
# straight core with a dotted halo read as a dashed rail in the first draft.
ZAP_WOBBLE_BRIGHT = (0, -1, -1, 0, 1, 1, 0, 0)
ZAP_WOBBLE_DIM = (0, 0, 1, 1, 0, -1, -1, 0)


def _zap_segment(c, direction, core, halo, wobble, thick):
    """One 8px segment through the 12x12 frame centre (which sits between
    pixels 5 and 6 on both axes). Axis-aligned segments zigzag by the wobble
    table; diagonals cannot shift a pixel sideways and stay 8-connected, so
    they bulge into a staircase at the same phases instead. `thick` adds a
    continuous second pixel of `halo` along one side, which is what makes the
    bright path read as a 2px bolt at 1x rather than a hairline."""
    if direction == 1:                                     # horizontal, row 5
        pts = [(2 + i, 5 + wobble[i]) for i in range(8)]
        side = (0, 1)
    elif direction == 2:                                   # vertical, column 5
        pts = [(5 + wobble[i], 2 + i) for i in range(8)]
        side = (1, 0)
    elif direction == 0:                                   # "\\": (2,2) -> (9,9)
        pts = [(2 + i, 2 + i) for i in range(8)]
        side = (1, 0)
    else:                                                  # "/": (2,9) -> (9,2)
        pts = [(2 + i, 9 - i) for i in range(8)]
        side = (1, 0)
    if thick:
        for (x, y) in pts:
            c.set(x + side[0], y + side[1], halo)
    for i, (x, y) in enumerate(pts):
        c.set(x, y, core)
        if direction in (0, 3) and wobble[i]:
            # Staircase bulge on a diagonal: a core pixel beside the line.
            if wobble[i] > 0:
                c.set(x + 1, y, core)
            else:
                c.set(x, y + (1 if direction == 0 else -1), core)
        elif direction in (1, 2) and not thick and i in (1, 6):
            # Dim path: a single darker pixel at the kinks, no halo.
            c.set(x - side[0], y - side[1], halo)


def arczap_frames():
    frames = []
    for core, halo, wobble, thick in ((ZAP_CORE_BRIGHT, ZAP_HALO_BRIGHT, ZAP_WOBBLE_BRIGHT, True),
                                      (ZAP_CORE_DIM, ZAP_HALO_DIM, ZAP_WOBBLE_DIM, False)):
        for direction in range(4):
            c = PC(ZAP_W, ZAP_H)
            _zap_segment(c, direction, core, halo, wobble, thick)
            frames.append(c)
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


# Buildings whose team-coloured pixels have to be re-stamped at native
# resolution after the supersampled downscale (see _sgrel_accents).


# ---------------------------------------------------------------------------
# Scrap resource pile (issue #91): the terrain resource tile the Recycling
# Depot/Hauler Drone economy actually collects. Its four density tiers
# (scrap01..scrap04, matching gold01..gold04's low-to-high progression) never
# had real art -- mods/sungrid/sequences/misc.yaml literally pointed
# scrap01..04 at gold01..04.tem, so every Scrap pile rendered as ordinary Ore
# nuggets. This went unnoticed because no map ever had Scrap painted on it
# until issue #86's SpawnsResourceOnDeath became the first thing to ever
# place Scrap on a live map -- at which point a player reported "a destroyed
# enemy tank turns into ore", which is exactly what was happening. Native
# 24x24 to match the classic RA resource-tile footprint: a flat, top-down
# heap of salvaged plate metal, a pipe, and a gear, escalating in size/density
# across the four tiers. Deliberately no gold/amber tones (RUST reads clearly
# distinct from SUN_GOLD in to_indexed()'s remap-ramp distance check -- see
# CLAUDE.md's art-pipeline rule about in-world sprites being indexed on the
# player palette), so a Scrap pile never accidentally colour-matches Ore's
# own remapped highlight.
SCRAP_W, SCRAP_H = 24, 24


def _scrap_plate(sd, x, y, pw, ph, tone):
    """A single bent sheet-metal fragment: flat top-down rectangle with a lit
    top edge and a dim underside crease -- no rotation, since a rectangle
    already reads as a plate lying flat from directly above."""
    sd.rect([x, y, x + pw, y + ph], fill=tone)
    sd.line([(x, y), (x + pw, y)], fill=lit(tone, 0.3), width=0.6)
    sd.line([(x, y + ph), (x + pw, y + ph)], fill=dim(tone, 0.35), width=0.5)


def scrap_pile_draw(sd, w, h, stage):
    cx, cy = w / 2, h / 2

    # Stage 1 (sparsest): a single plate and a bolt -- just enough to read as
    # "something metal", not yet a pile.
    _scrap_plate(sd, cx - 3, cy - 1.5, 5, 3, LEGACY_GRAY)
    sd.ellipse([cx + 2.5, cy + 0.5, cx + 4, cy + 2], fill=LEGACY_GRAY_DARK)

    if stage >= 2:
        # A second plate at an offset (still flat/top-down) and a pipe stub.
        _scrap_plate(sd, cx - 6, cy + 1, 4.5, 2.5, mix(LEGACY_GRAY, RUST, 0.35))
        sd.rect([cx + 1, cy - 4, cx + 6, cy - 2.3], fill=LEGACY_GRAY_DARK)
        sd.line([(cx + 1, cy - 4), (cx + 6, cy - 4)], fill=lit(LEGACY_GRAY_DARK, 0.35), width=0.5)

    if stage >= 3:
        # A gear (a distinct silhouette element, not just more plates) and a
        # rust-streaked plate.
        gx, gy, gr = cx - 1, cy + 4, 3
        sd.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=LEGACY_GRAY_DARK)
        sd.ellipse([gx - gr * 0.45, gy - gr * 0.45, gx + gr * 0.45, gy + gr * 0.45], fill=PANEL_BLUEBLACK)
        for a in range(0, 360, 60):
            rad = math.radians(a)
            tx, ty = gx + math.cos(rad) * gr * 1.15, gy + math.sin(rad) * gr * 1.15
            sd.rect([tx - 0.6, ty - 0.6, tx + 0.6, ty + 0.6], fill=LEGACY_GRAY_DARK)
        _scrap_plate(sd, cx + 3, cy - 6, 5, 2.5, mix(LEGACY_GRAY, RUST, 0.5))
        sd.px(cx + 5, cy - 5, lit(RUST, 0.3))

    if stage >= 4:
        # The pile crests: a bright rust plate on top (most recently added
        # piece) plus a coil of wire for texture and a busier silhouette.
        _scrap_plate(sd, cx - 2, cy - 3, 6, 3.5, lit(RUST, 0.15))
        sd.line([(cx - 2, cy - 3), (cx + 4, cy - 3)], fill=lit(RUST, 0.45), width=0.6)
        for i in range(3):
            r = 2.2 - i * 0.6
            sd.ellipse([cx - 7 - r, cy - 6 - r, cx - 7 + r, cy - 6 + r],
                       outline=dim(LEGACY_GRAY, 0.2), width=0.5)


def main():
    # Arc Turret pedestal (a solid since issue #111, at its own origin rather
    # than the roster's diamond plinth): eight idle frames with the status
    # lamp on five and off three (issue #113), then the damaged frame. The
    # baked ground shadow goes through indexed_strip so SHADOW_IDX survives.
    arct_kws = [dict(lamp=i < 5) for i in range(ARCT_LAMP_FRAMES)] + [dict(damaged=True)]
    arct_bodies = [arct_body_frame(**kw) for kw in arct_kws]
    arct_shadows = [render_shadow_mask(arct_shadow_draw, SG1x1_W, SG1x1_H,
                                       damaged=kw.get("damaged", False)) for kw in arct_kws]
    save_pngsheet(indexed_strip(arct_bodies, arct_shadows, SG1x1_W, SG1x1_H), "arct.png",
                  SG1x1_W, SG1x1_H, len(arct_bodies), indexed=True)
    save_pngsheet(make_icon(arct_icon_draw, SG1x1_W, SG1x1_H, label=ICON_LABELS["arct"]),
                  "arcticon.png", ICON_W, ICON_H, 1)
    # Build-up (issue #74): the structure rising out of the ground, ending on
    # this sheet's own first idle frame so completion never pops.
    arct_mk = make_frames(arct_draw, SG1x1_W, SG1x1_H, final=arct_bodies[0])
    save_pngsheet(indexed_strip(arct_mk, [None] * (len(arct_mk) - 1) + [arct_shadows[0]],
                                SG1x1_W, SG1x1_H),
                  "arctmake.png", SG1x1_W, SG1x1_H, len(arct_mk), indexed=True)

    # Volumetric roster (issue #106): idle + damaged, cameo fallback, build-up.
    # Every frame carries the stock-style silhouette shadow rim, the build-up's
    # final frame included, so completion never pops.
    for name, (fam, _) in MESHES.items():
        if name in ("sgvlt", "rcyd", "sgfact"):
            continue          # multi-state sheets, assembled below
        w, h, _half = FAM[fam]
        sheet, frames = building_sheet(name)
        save_pngsheet(sheet, f"{name}.png", w, h, len(frames), indexed=True)
        save_pngsheet(make_icon(mesh_draw_fn(name), w, h, label=ICON_LABELS.get(name)),
                      f"{name}icon.png", ICON_W, ICON_H, 1)
        idle = frames[0]
        mk = make_frames(mesh_draw_fn(name), w, h, final=idle)
        save_pngsheet(indexed_strip(mk, [None] * (len(mk) - 1) + [silhouette_shadow(idle, 2, 2)], w, h),
                      f"{name}make.png", w, h, len(mk), indexed=True)

    # Battery Bank (the Grid Reserve Vault): one strip of 9 charge stages
    # followed by 9 damaged charge stages, which is what `stages:` /
    # `damaged-stages:` index into. Build-up ends on charge stage 0 -- a
    # Battery Bank comes online empty.
    vlt = [mesh_frame("sgvlt", damaged=dmg, charge=stage)
           for dmg in (False, True) for stage in range(SGVLT_STAGES)]
    save_pngsheet(indexed_strip(vlt, [silhouette_shadow(f, 2, 2) for f in vlt], SG1x1_W, SG1x1_H),
                  "sgvlt.png", SG1x1_W, SG1x1_H, len(vlt), indexed=True)
    save_pngsheet(make_icon(mesh_draw_fn("sgvlt"), SG1x1_W, SG1x1_H, label=ICON_LABELS["sgvlt"]),
                  "sgvlticon.png", ICON_W, ICON_H, 1)
    vlt_mk = make_frames(mesh_draw_fn("sgvlt"), SG1x1_W, SG1x1_H, final=vlt[0], charge=0)
    save_pngsheet(indexed_strip(vlt_mk, [None] * (len(vlt_mk) - 1) + [silhouette_shadow(vlt[0], 2, 2)],
                                SG1x1_W, SG1x1_H),
                  "sgvltmake.png", SG1x1_W, SG1x1_H, len(vlt_mk), indexed=True)

    # Recycling Depot: same layout as the Battery Bank -- 9 fill stages then 9
    # damaged fill stages. The cameo written here is the programmatic
    # fallback; gen_photo_cameos.py overwrites it with the photographic one
    # (issue #47), same as every other actor.
    rcy = [mesh_frame("rcyd", damaged=dmg, charge=stage)
           for dmg in (False, True) for stage in range(RCYD_STAGES)]
    save_pngsheet(indexed_strip(rcy, [silhouette_shadow(f, 2, 2) for f in rcy], SG1x1_W, SG1x1_H),
                  "rcyd.png", SG1x1_W, SG1x1_H, len(rcy), indexed=True)
    save_pngsheet(make_icon(mesh_draw_fn("rcyd"), SG1x1_W, SG1x1_H, label=ICON_LABELS["rcyd"]),
                  "rcydicon.png", ICON_W, ICON_H, 1)
    rcy_mk = make_frames(mesh_draw_fn("rcyd"), SG1x1_W, SG1x1_H, final=rcy[0], charge=0)
    save_pngsheet(indexed_strip(rcy_mk, [None] * (len(rcy_mk) - 1) + [silhouette_shadow(rcy[0], 2, 2)],
                                SG1x1_W, SG1x1_H),
                  "rcydmake.png", SG1x1_W, SG1x1_H, len(rcy_mk), indexed=True)

    # Construction Yard (issue #106): the mod's own FACT art, on stock
    # fact.shp's layout -- idle, 25 `build` frames (the crane trolley
    # traversing, played by WithBuildingPlacedAnimation), damaged idle, 25
    # damaged build frames -- except that the idle is now eight frames (the
    # mast beacon blinking, issue #109), so the layout is idle 0-7, build
    # 8-32, damaged-idle 33, damaged-build 34-58 and sgfact: in
    # sequences/structures.yaml carries those starts.
    fw, fh, _half = FAM["fact"]
    fact_frames = [mesh_frame("sgfact", beacon=i < 5) for i in range(8)]
    fact_frames += [mesh_frame("sgfact", build=i / 24) for i in range(25)]
    fact_frames.append(mesh_frame("sgfact", damaged=True))
    fact_frames += [mesh_frame("sgfact", damaged=True, build=i / 24) for i in range(25)]
    assert len(fact_frames) == 59
    save_pngsheet(indexed_strip(fact_frames, [silhouette_shadow(f, 2, 2) for f in fact_frames], fw, fh),
                  "sgfact.png", fw, fh, len(fact_frames), indexed=True)
    # No cameo of its own: FACT keeps stock facticon.shp (the owner's call,
    # docs/BACKLOG.md issue #107) -- the sgfact: sequence node points there.
    fact_mk = make_frames(mesh_draw_fn("sgfact"), fw, fh, final=fact_frames[0])
    save_pngsheet(indexed_strip(fact_mk, [None] * (len(fact_mk) - 1) + [silhouette_shadow(fact_frames[0], 2, 2)], fw, fh),
                  "sgfactmake.png", fw, fh, len(fact_mk), indexed=True)

    # Idle overlays (issue #109), drawn over the body by WithIdleOverlay:
    # the Depot's stack puffs, and the grid-strained lamps on the three
    # buildings that consume that condition. `strained` frames first, then
    # the `damaged-strained` variant where the damaged body differs.
    smoke = [_mesh_frame("1x1", rcyd_smoke_mesh, phase=i) for i in range(8)]
    save_pngsheet(indexed_strip(smoke, None, SG1x1_W, SG1x1_H), "rcydsmoke.png", SG1x1_W, SG1x1_H, len(smoke), indexed=True)
    for name, fn, dmg_frames in (("sgdai", sgdai_strained_mesh, 1), ("sgcry", sgcry_strained_mesh, 4)):
        fam = MESHES[name][0]
        w, h, _half = FAM[fam]
        fr = [_mesh_frame(fam, fn, phase=i) for i in range(4)]
        fr += [_mesh_frame(fam, fn, phase=i, damaged=True) for i in range(dmg_frames)]
        save_pngsheet(indexed_strip(fr, None, w, h), f"{name}strained.png", w, h, len(fr), indexed=True)
    lamp = [render(sgtur_strained_draw, SGTUR_W, SGTUR_H, phase=i) for i in range(4)]
    save_pngsheet(indexed_strip(lamp, None, SGTUR_W, SGTUR_H), "sgturstrained.png", SGTUR_W, SGTUR_H, len(lamp), indexed=True)

    # Arc Turret: the head is its own 32-facing turret sprite (issue #66), so
    # arct.png above is the pedestal alone and this is what rotates on top.
    # Layout: 32 facings x ARCT_ARC_PHASES flicker frames, then 32 damaged
    # facings (no arc, one frame each) -- `turret:` / `damaged-turret:` Start
    # in sequences/structures.yaml must agree (issue #113).
    arct_idle, arct_idle_sh = arct_turret_frames(damaged=False, phases=ARCT_ARC_PHASES)
    arct_dmg, arct_dmg_sh = arct_turret_frames(damaged=True)
    save_pngsheet(indexed_strip(arct_idle + arct_dmg, arct_idle_sh + arct_dmg_sh,
                                SG1x1_W, SG1x1_H),
                  "arctturret.png", SG1x1_W, SG1x1_H, len(arct_idle) + len(arct_dmg), indexed=True)

    # Turret: 32 idle-facing frames + 32 damaged-facing frames, single strip.
    # Each facing is a separate view of the 3D assembly (issue #65), and the
    # baked ground shadow is injected as SHADOW_IDX rather than painted.
    # Layout (issue #113): 32 facings x SGTUR_SWEEP_FRAMES idle-scan frames,
    # 32 damaged (static), 32 `aim` (static), 32 `damaged-aim` (static) --
    # the Start values in sequences/structures.yaml must agree.
    idle_bodies, idle_shadows = sgtur_frames(damaged=False, sweep=True)
    dmg_bodies, dmg_shadows = sgtur_frames(damaged=True)
    aim_bodies, aim_shadows = sgtur_frames(damaged=False)
    idle_bodies += dmg_bodies + aim_bodies
    idle_shadows += dmg_shadows + aim_shadows
    save_pngsheet(indexed_strip(idle_bodies + dmg_bodies, idle_shadows + dmg_shadows,
                                SGTUR_W, SGTUR_H),
                  "sgturturret.png", SGTUR_W, SGTUR_H, len(idle_bodies) + len(dmg_bodies), indexed=True)
    save_pngsheet(make_icon(sgtur_base_draw, SGTUR_W, SGTUR_H, label=ICON_LABELS["sgtur"]),
                  "sgturicon.png", ICON_W, ICON_H, 1)

    # Emplacement pad: the fixed body under the rotating station, replacing the
    # stock gunmake.shp placeholder it borrowed for both its idle frame and its
    # build-up (issue #74). The station itself is gated on !build-incomplete,
    # so the build-up shows the pad alone and the turret pops in on completion
    # -- exactly how SAM/GUN/AGUN behave.
    # Eight idle frames, the status lamp on five and off three (issue #113).
    pads = [sgtur_pad_frame(lamp=i < 5) for i in range(SGTUR_LAMP_FRAMES)]
    pad, pad_shadow = pads[0], silhouette_shadow(pads[0], 2, 2)
    save_pngsheet(indexed_strip(pads, [silhouette_shadow(f, 2, 2) for f in pads], SGTUR_W, SGTUR_H),
                  "sgturpad.png", SGTUR_W, SGTUR_H, len(pads), indexed=True)
    pad_mk = make_frames(sgtur_pad_draw, SGTUR_W, SGTUR_H, final=pad)
    save_pngsheet(indexed_strip(pad_mk, [None] * (len(pad_mk) - 1) + [pad_shadow],
                                SGTUR_W, SGTUR_H),
                  "sgturmake.png", SGTUR_W, SGTUR_H, len(pad_mk), indexed=True)

    # Death rubble (issue #74), replacing stock powrdead.shp/apwrdead.shp/
    # factdead.shp. One frame each, matching the stock rubble's own layout,
    # with a real SHADOW_IDX rim -- a collapsed building, unlike a standing
    # one, leaves terrain visible around itself.
    for name, dead_fn, w, h in (
        ("sgpwrdead", sgpwr_dead_draw, FAM23_W, FAM23_H),
        ("sgapwrdead", sgapwr_dead_draw, FAM33_W, FAM33_H),
        ("sghyddead", sghyd_dead_draw, FAM33_W, FAM33_H),
        ("sgfactdead", sgfact_dead_draw, 72, 72),
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
    # This procedural icon is a fallback only -- "sghau" is in gen_photo_cameos.py's
    # CROPS, whose photographic cameo is what actually ships. Re-run that script
    # after this one any time sghau_draw() changes, or the shipped cameo reverts
    # to this flatter placeholder (happened once already -- issue #86 follow-up).
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
    # Arc discharge projectile: 4 bright + 4 dim segment frames (issue #110).
    zap = arczap_frames()
    save_pngsheet(sheet_of_indexed(zap, ZAP_W, ZAP_H), "arczap.png",
                  ZAP_W, ZAP_H, len(zap), indexed=True)

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

    # Scrap resource pile (issue #91): four density tiers, one frame each,
    # replacing the gold01..04.tem placeholder scrap01..04 previously aliased.
    for stage, filename in ((1, "scrap01.png"), (2, "scrap02.png"), (3, "scrap03.png"), (4, "scrap04.png")):
        save_pngsheet(render(scrap_pile_draw, SCRAP_W, SCRAP_H, stage), filename,
                      SCRAP_W, SCRAP_H, 1, indexed=True)

    print("done")


if __name__ == "__main__":
    main()
