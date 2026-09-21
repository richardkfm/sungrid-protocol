# DRAFT, non-canonical (see docs/ART_DIRECTION.md 'Concept drafts'). Renders review sheets only; writes nothing into mods/sungrid/bits.
# Issue #108's planting drafts: the A/B array-plot comparison the owner chose A from. The 'before' column shows the
# generator as it was when the draft was made; the shipped planting lives in gen_concept_art.py and diverged from this.
"""Greenery drafts: planted beds, shrubs, tufts, trees, vines and green roofs
on four of the volumetric buildings, rendered through the shipped generator's
own Mesh + indexed pipeline. Writes review PNGs only."""
import sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'mods', 'sungrid', 'bits'))
import gen_concept_art as G
from gen_concept_art import (Mesh, lit, dim, mix, plinth, pv_panel, SUN_GOLD, STEEL, SLAB, PAD_TOP,
                             PALE_STEEL, PANEL_BLUEBLACK, LEGACY_GRAY, LEGACY_GRAY_DARK, RUST,
                             GREEN_ACCENT, GREEN_PRIMARY, GRASS, DIRT, POLE_DARK, DAMAGE_SCORCH)
from PIL import Image, ImageDraw

# Palette-exact foliage ramp (temperat.pal 145..152): sage / olive greens, the
# drought-tolerant look that is plausible on sand, grass and snow alike.
PALE = (176, 208, 124)
SAGE = (136, 172, 108)
MID = (104, 136, 92)
DARK = (76, 100, 60)
DEEP = (60, 84, 48)
SOIL = (100, 80, 56)          # idx 32
BARK = (72, 56, 40)


def _h(x, y, salt=0):
    """Deterministic 0..1 hash of a grid position (draft only)."""
    n = int(x * 73856093) ^ int(y * 19349663) ^ int(salt * 83492791)
    n = (n * 2654435761) & 0xFFFFFFFF
    return ((n >> 8) & 0xFFFF) / 65536.0


def clump(m, x, y, z, r, col, top=None, h=None, sides=7):
    h = r * 0.5 if h is None else h
    m.prism(x, y, z, z + h, r, col, sides=sides, top=top or lit(col, 0.15), shadow=False)


def bed(m, x0, y0, x1, y1, z, h=0.6, step=4.0, lowcap=1.0, salt=0, keep=None):
    """A planted ground bed: a low soil-sided box with a green mat on top and
    scattered groundcover clumps. `keep(x, y)` returns False for positions to
    leave clear (under equipment). `lowcap` caps clump height (under panels)."""
    m.box(x0, y0, z - 0.2, x1, y1, z + h, SOIL, top=MID, shadow=False)
    zt = z + h
    y = y0 + 1.6
    row = 0
    while y < y1 - 1.2:
        x = x0 + 1.6 + (step / 2 if row % 2 else 0)
        while x < x1 - 1.2:
            a, b, c = _h(x, y, salt), _h(x, y, salt + 1), _h(x, y, salt + 2)
            px, py = x + (a - 0.5) * 1.6, y + (b - 0.5) * 1.6
            if keep is None or keep(px, py):
                if c < 0.14:
                    clump(m, px, py, zt, 1.4 + a * 0.8, SOIL, top=lit(SOIL, 0.12), h=0.15)   # bare patch
                elif c < 0.50:
                    clump(m, px, py, zt, 1.6 + a * 1.2, DEEP, top=DARK, h=min(lowcap, 0.6 + b * 0.6))
                elif c < 0.84:
                    clump(m, px, py, zt, 1.5 + a * 1.1, DARK, top=SAGE, h=min(lowcap, 0.7 + b * 0.6))
                else:
                    tuft(m, px, py, zt, cap=lowcap)
            x += step
        y += step * 0.85
        row += 1


def tuft(m, x, y, z, cap=3.0):
    """Ornamental grass (feather grass / miscanthus): dark base, pale top."""
    m.prism(x, y, z, z + min(cap, 1.2), 1.4, DEEP, sides=6, top=DARK, shadow=False)
    if cap > 1.4:
        m.prism(x, y, z + 1.2, z + min(cap, 3.2), 0.95, SAGE, sides=6, top=PALE, shadow=False)


def shrub(m, x, y, z, r=2.8, tone=MID):
    """A rounded drought-tolerant shrub (lavender / rosemary / sage mound)."""
    m.prism(x, y, z, z + r * 0.55, r, DEEP, sides=8, top=DARK)
    m.prism(x, y, z + r * 0.55, z + r * 1.05, r * 0.66, tone, sides=8, top=SAGE, shadow=False)


def tree(m, x, y, z, h=8.0, r=5.5, tone=MID):
    """A small olive / acacia-type tree: short trunk, wide flat-ish canopy."""
    m.strut((x, y, z), (x, y, z + h * 0.62), 0.7, BARK, cap=BARK)
    base = z + h * 0.5
    m.prism(x, y, base, base + h * 0.26, r, DEEP, sides=9, top=DARK)
    m.prism(x + 0.4, y - 0.4, base + h * 0.26, base + h * 0.46, r * 0.74, dim(tone, 0.1), sides=9, top=tone, shadow=False)
    m.prism(x - 0.3, y + 0.3, base + h * 0.46, base + h * 0.6, r * 0.42, tone, sides=7, top=SAGE, shadow=False)


def vines_x(m, x, y0, y1, z0, z1, salt=0, dark=False):
    """Climbing greenery pressed on a -x (lit, screen-left) wall: broad leaf
    panels of uneven height with clumps standing proud at their tops."""
    n = max(2, int((y1 - y0) / 4.5))
    lo, hi = (DEEP, DARK) if dark else (DARK, MID)
    for i in range(n):
        a, b = _h(i, salt, 3), _h(i, salt, 4)
        ya = y0 + (y1 - y0) * i / n + 0.4
        yb = ya + (y1 - y0) / n * (0.6 + 0.35 * a)
        zt = z0 + (z1 - z0) * (0.5 + 0.5 * b)
        m.quad((x - 0.3, ya, z0), (x - 0.3, yb, z0), (x - 0.3, yb, zt), (x - 0.3, ya, zt), lo if a < 0.5 else hi, order=1)
        m.box(x - 1.3, ya + 0.3, zt - 1.8, x - 0.2, yb - 0.3, zt + 0.3, hi, top=SAGE if not dark else MID, order=2, shadow=False)


def green_roof(m, x0, y0, x1, y1, z, keep=None, salt=5):
    """Sedum mat on a flat roof with a gravel service strip on the near edge."""
    bed(m, x0, y0, x1, y1, z, h=0.5, step=2.8, lowcap=0.6, salt=salt, keep=keep)
    m.box(x0, y0, z + 0.5, x1, y0 + 1.6, z + 0.6, PAD_TOP, top=PAD_TOP, order=1, shadow=False)


def planter(m, x0, y0, x1, y1, z, salt=9):
    """A concrete trough with a planted top and a couple of shrubs."""
    m.box(x0, y0, z, x1, y1, z + 1.4, dim(SLAB, 0.15), top=SLAB, shadow=False)
    bed(m, x0 + 0.4, y0 + 0.4, x1 - 0.4, y1 - 0.4, z + 1.4, h=0.4, step=2.6, lowcap=1.6, salt=salt)


def meadow_plinth(m, half, z=2.2, live=True, keep=None, salt=0, lowcap=1.2):
    """Variant B: the plot is a raised planted bed behind a low concrete kerb
    -- no concrete top at all. The conduit band still runs along the two near
    edges, now laid across the bed."""
    m.box(-half, -half, 0, half, half, z - 0.5, dim(SLAB, 0.15), top=SLAB, shadow=False)
    m.box(-half + 0.9, -half + 0.9, z - 0.5, half - 0.9, half - 0.9, z + 0.3, SOIL, top=MID, shadow=False)
    col = SUN_GOLD if live else dim(SUN_GOLD, 0.4)
    m.box(-half + 1, -half + 1, z + 0.3, half - 1, -half + 3.2, z + 1.2, col, top=lit(col, 0.25), order=1, shadow=False, accent=True)
    m.box(-half + 1, -half + 1, z + 0.3, -half + 3.2, half - 1, z + 1.2, col, top=lit(col, 0.25), order=1, shadow=False, accent=True)
    band = lambda x, y: x > -half + 4.2 and y > -half + 4.2 and (keep is None or keep(x, y))
    bed(m, -half + 1.2, -half + 1.2, half - 1.0, half - 1.0, z - 0.3, h=0.6, lowcap=lowcap, salt=salt, keep=band)


# ----------------------------------------------------------------- buildings
def sgpwr_meadow(damaged=False):
    m = Mesh()
    cab = lambda x, y: not (-17 < x < -8 and -17.5 < y < -10)
    meadow_plinth(m, 20, live=not damaged, keep=cab, salt=11)
    for row, y in enumerate((-10, 6)):
        for col, x in enumerate((-16, 3)):
            pv_panel(m, x, y, 17.5, 14, 2.8, rise=9.5, damaged=damaged and row == 1 and col == 1)
    m.box(-16, -16.5, 2.2, -9, -11, 8, STEEL, top=lit(STEEL, 0.2))
    m.box(-16.5, -15.5, 4.5, -15.9, -12, 5.7, SUN_GOLD if not damaged else dim(SUN_GOLD, 0.4), top=SUN_GOLD, order=1, shadow=False, accent=True)
    for x in (-4, 5, 14):
        shrub(m, x, -14.0, 2.8, r=2.4 + 0.7 * _h(x, 1))
    for x in (0.5, 9.5, 18):
        tuft(m, x, -14.8, 2.8)
    for y in (-2, 10, 17):
        tuft(m, -17.8, y, 2.8)
    return m


def sgapwr_meadow(damaged=False):
    m = Mesh()
    cab = lambda x, y: not (11 < x < 27 and -25 < y < -16)
    meadow_plinth(m, 27, live=not damaged, keep=cab, salt=12)
    for row, y in enumerate((-15, -1, 13)):
        for col, x in enumerate((-23.5, -6.1, 11.3)):
            pv_panel(m, x, y, 16, 12.5, 2.8, rise=8.5, damaged=damaged and (row, col) in ((1, 1), (0, 2)))
    m.box(12, -23.5, 2.2, 26, -17, 10, STEEL, top=lit(STEEL, 0.2))
    for i in range(3):
        m.box(13 + i * 4.2, -24, 4, 16 + i * 4.2, -23.5, 8.5, dim(STEEL, 0.4), top=dim(STEEL, 0.4), order=1, shadow=False)
    m.box(11.5, -22.5, 7.5, 12.1, -18, 8.7, SUN_GOLD if not damaged else dim(SUN_GOLD, 0.4), top=SUN_GOLD, order=1, shadow=False, accent=True)
    for x in (-19, -10, -1, 7):
        shrub(m, x, -20.0, 2.8, r=2.4 + 0.9 * _h(x, 2))
    for x in (-15, -5.5, 3.5):
        tuft(m, x, -21.2, 2.8)
    for y in (-6, 4, 14, 22):
        tuft(m, -24.8, y, 2.8)
    if damaged:
        m.box(12.5, -24.1, 5, 19, -23.6, 9.5, DAMAGE_SCORCH, top=DAMAGE_SCORCH, order=2, shadow=False)
    return m


def sgpwr_green(damaged=False):
    m = Mesh()
    plinth(m, 20, live=not damaged)
    # Planted bed inside the concrete rim: the whole plot except the band
    # strips on the two near edges and the inverter's own footing.
    cab = lambda x, y: not (-17 < x < -8 and -17.5 < y < -10)
    bed(m, -16.5, -17.0, 19.5, 19.5, 2.2, lowcap=0.9, salt=1, keep=cab)
    for row, y in enumerate((-10, 6)):
        for col, x in enumerate((-16, 3)):
            pv_panel(m, x, y, 17.5, 14, 2.8, rise=9.5, damaged=damaged and row == 1 and col == 1)
    m.box(-16, -16.5, 2.2, -9, -11, 8, STEEL, top=lit(STEEL, 0.2))
    m.box(-16.5, -15.5, 4.5, -15.9, -12, 5.7, SUN_GOLD if not damaged else dim(SUN_GOLD, 0.4), top=SUN_GOLD, order=1, shadow=False, accent=True)
    # Shrubs and grasses on the near strip in front of the panels.
    for x in (-4, 5, 14):
        shrub(m, x, -14.3, 2.8, r=2.3 + 0.7 * _h(x, 1))
    for x in (0.5, 9.5, 18):
        tuft(m, x, -14.8, 2.8)
    return m


def sgapwr_green(damaged=False):
    m = Mesh()
    plinth(m, 27, live=not damaged)
    cab = lambda x, y: not (11 < x < 27 and -25 < y < -16)
    bed(m, -23.5, -23.0, 26.5, 26.5, 2.2, lowcap=0.9, salt=2, keep=cab)
    for row, y in enumerate((-15, -1, 13)):
        for col, x in enumerate((-23.5, -6.1, 11.3)):
            pv_panel(m, x, y, 16, 12.5, 2.8, rise=8.5, damaged=damaged and (row, col) in ((1, 1), (0, 2)))
    m.box(12, -23.5, 2.2, 26, -17, 10, STEEL, top=lit(STEEL, 0.2))
    for i in range(3):
        m.box(13 + i * 4.2, -24, 4, 16 + i * 4.2, -23.5, 8.5, dim(STEEL, 0.4), top=dim(STEEL, 0.4), order=1, shadow=False)
    m.box(11.5, -22.5, 7.5, 12.1, -18, 8.7, SUN_GOLD if not damaged else dim(SUN_GOLD, 0.4), top=SUN_GOLD, order=1, shadow=False, accent=True)
    for x in (-12, -3, 6):
        shrub(m, x, -20.0, 2.8, r=2.4 + 0.9 * _h(x, 2))
    for x in (-8, 1.5, 9.5):
        tuft(m, x, -21.0, 2.8)
    tree(m, -19.5, -19.0, 2.8, h=8.0, r=5.0)
    if damaged:
        m.box(12.5, -24.1, 5, 19, -23.6, 9.5, DAMAGE_SCORCH, top=DAMAGE_SCORCH, order=2, shadow=False)
    return m


def sgdai_green(damaged=False):
    m = Mesh()
    plinth(m, 20, live=not damaged)
    hall = mix(PANEL_BLUEBLACK, LEGACY_GRAY, 0.35)
    m.box(-18, -15, 2.2, 18, 16, 15, hall, top=lit(hall, 0.12))
    m.box(-18.5, -12, 7, -17.9, 13, 9.5, lit(PANEL_BLUEBLACK, 0.55), top=lit(PANEL_BLUEBLACK, 0.55), order=1, shadow=False)
    m.box(-16, -15.5, 3.2, 16, -14.9, 4.0, GREEN_ACCENT if not damaged else dim(GREEN_ACCENT, 0.5), top=GREEN_ACCENT, order=1, shadow=False)
    # Sedum roof, chillers standing in it.
    chill = lambda x, y: not any(x0 - 0.8 < x < x0 + 7.8 and y0 - 0.8 < y < y0 + 8.8
                                 for x0 in (-13, -3, 7) for y0 in (-8, 4))
    green_roof(m, -17.5, -14.5, 17.5, 15.5, 15, keep=chill)
    for i in range(3):
        for j in range(2):
            if damaged and (i, j) == (2, 0):
                continue
            x, y = -13 + i * 10, -8 + j * 12
            m.box(x, y, 15, x + 7, y + 8, 19, PALE_STEEL, top=lit(PALE_STEEL, 0.1), shadow=False, order=1)
            m.prism(x + 3.5, y + 4, 19, 19.6, 2.6, LEGACY_GRAY_DARK, sides=8, top=dim(LEGACY_GRAY, 0.3), shadow=False, order=1)
    vines_x(m, -18.0, -14, -1, 2.2, 7.0, salt=1)
    vines_x(m, -18.0, 3, 15, 2.2, 6.8, salt=2)
    # Near strip: tree at the screen-right corner, shrubs along the front.
    tree(m, 15.5, -17.3, 2.2, h=8.5, r=5.0)
    for x in (-12, -3, 6):
        shrub(m, x, -17.0, 2.2, r=2.0 + 0.6 * _h(x, 3))
    tuft(m, -7.5, -17.4, 2.2)
    tuft(m, 1.5, -17.4, 2.2)
    m.strut((15, -12, 15), (15, -12, 22 if not damaged else 17), 0.6, STEEL, cap=RUST if damaged else None)
    if not damaged:
        m.box(14.3, -12.7, 22, 15.7, -11.3, 23.2, SUN_GOLD, top=lit(SUN_GOLD, 0.3), order=4, shadow=False, accent=True)
    if damaged:
        m.box(4, -16, 8, 12, -14.5, 15, DAMAGE_SCORCH, top=DAMAGE_SCORCH, order=2, shadow=False)
    return m


def sgfact_green(damaged=False, build=None):
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
    vines_x(m, -24.0, 1, 23, 2.0, 8.5, salt=4, dark=True)
    for y in (-6, -18):
        m.strut((-20, y, 2), (-20, y, 17), 1.2, STEEL, cap=lit(STEEL, 0.3))
        m.strut((20, y, 2), (20, y, 17), 1.2, STEEL, cap=lit(STEEL, 0.3))
        m.strut((-20, y, 16.5), (20, y, 16.5), 1.2, STEEL if not damaged else dim(STEEL, 0.3))
    m.strut((-20, -6, 17), (-20, -18, 17), 0.8, STEEL)
    m.strut((20, -6, 17), (20, -18, 17), 0.8, STEEL)
    t = 0.62 if build is None else build
    tx = -14 + 28 * t
    trolley = SUN_GOLD if not damaged else dim(SUN_GOLD, 0.4)
    m.box(tx - 3.5, -14, 16.2, tx + 3.5, -10, 19.5, trolley, top=lit(trolley, 0.3), order=2, accent=True)
    if build is not None:
        drop = 4 + 6 * math.sin(math.pi * build)
        m.strut((tx, -12, 16.2), (tx, -12, 16.2 - drop), 0.3, POLE_DARK, shadow=False)
    m.box(-6, -15, 2, 6, -8, 6, dim(GREEN_PRIMARY, 0.1), top=lit(GREEN_PRIMARY, 0.2))
    # Planted near-left corner (was a flat grass patch) and a tree at the near-right corner.
    bed(m, -22.5, -22.5, -12, -19.0, 2.0, lowcap=1.4, salt=7, step=3.0)
    shrub(m, -19, -21.0, 2.6, r=2.6)
    tuft(m, -14.5, -21.5, 2.6)
    tree(m, 22.0, -21.5, 2.0, h=8.5, r=4.8)
    shrub(m, 12, -22.0, 2.0, r=2.4)
    tuft(m, 16.5, -22.5, 2.0)
    m.strut((21, 21, 20), (21, 21, 32 if not damaged else 24), 0.8, STEEL, cap=RUST if damaged else None)
    if not damaged:
        m.box(20.2, 20.2, 32, 21.8, 21.8, 33.4, SUN_GOLD, top=lit(SUN_GOLD, 0.3), order=4, shadow=False, accent=True)
    if damaged:
        m.box(-22, -0.5, 4, -14, 0.2, 12, DAMAGE_SCORCH, top=DAMAGE_SCORCH, order=2, shadow=False)
        m.box(6, -20, 2, 14, -13, 4, mix(STEEL, DAMAGE_SCORCH, 0.5), top=DAMAGE_SCORCH)
    return m


# ----------------------------------------------------------------- review sheet
GROUNDS = {"temperate": (52, 108, 48), "desert": (198, 176, 128), "snow": (222, 226, 232)}


def indexed_rgba(frame):
    p = G.to_indexed(frame)
    src = p.load()
    w, h = p.size
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    dst = out.load()
    for y in range(h):
        for x in range(w):
            i = src[x, y]
            if i == 0:
                continue
            if i == G.SHADOW_IDX:
                dst[x, y] = (0, 0, 0, 120)
            else:
                dst[x, y] = G.PLAYER_PAL[i] + (255,)
    return out


def frame_with(name, fn, **kw):
    fam, orig = G.MESHES[name]
    G.MESHES[name] = (fam, fn)
    try:
        return indexed_rgba(G.mesh_frame(name, **kw))
    finally:
        G.MESHES[name] = (fam, orig)


def main():
    scale = 3
    T, D, S = GROUNDS["temperate"], GROUNDS["desert"], GROUNDS["snow"]
    rows = []
    for name, a_fn, b_fn in (("sgpwr", sgpwr_green, sgpwr_meadow), ("sgapwr", sgapwr_green, sgapwr_meadow)):
        before = indexed_rgba(G.mesh_frame(name))
        a, b = frame_with(name, a_fn), frame_with(name, b_fn)
        rows.append((name, [("before", before, T), ("A: bed in concrete rim", a, T), ("B: meadow plot", b, T),
                            ("B desert", b, D), ("B snow", b, S), ("B damaged", frame_with(name, b_fn, damaged=True), T)]))
    for name, fn in (("sgdai", sgdai_green), ("sgfact", sgfact_green)):
        before = indexed_rgba(G.mesh_frame(name))
        a = frame_with(name, fn)
        rows.append((name, [("before", before, T), ("green roof / vines / tree", a, T), ("desert", a, D),
                            ("snow", a, S), ("damaged", frame_with(name, fn, damaged=True), T)]))
    cw, ch = 96 * scale, 66 * scale
    pad = 8
    ncol = max(len(c) for _, c in rows)
    W = pad + ncol * (cw + pad)
    H = pad + sum(ch + 18 + pad for _ in rows) + 66 + 30
    sheet = Image.new("RGB", (W, H), (24, 24, 24))
    d = ImageDraw.Draw(sheet)
    y = pad
    for name, cells in rows:
        d.text((pad, y), name, fill=(220, 220, 220))
        y += 14
        x = pad
        for label, img, ground in cells:
            cell = Image.new("RGBA", (96, 66), ground + (255,))
            cell.alpha_composite(img, ((96 - img.width) // 2, (66 - img.height) // 2))
            cell = cell.resize((cw, ch), Image.NEAREST)
            sheet.paste(cell, (x, y))
            d.text((x + 2, y + ch - 12), label, fill=(240, 240, 240))
            x += cw + pad
        y += ch + pad + 4
    # Native 1x strip: the same frames at in-game size, on all three grounds.
    d.text((pad, y), "native 1x: before / A / B (arrays), before / green (halls) on temperate, desert, snow", fill=(220, 220, 220))
    y += 14
    x = pad
    for name, cells in rows:
        for label, img, _ in cells[:3]:
            for ground in (T, D, S):
                cell = Image.new("RGBA", (96, 66), ground + (255,))
                cell.alpha_composite(img, ((96 - img.width) // 2, (66 - img.height) // 2))
                sheet.paste(cell, (x, y))
                x += 96 + 2
            x += 6
    out = os.path.join(HERE, "greenery-review.png")
    sheet.save(out)
    print("wrote", out, sheet.size)


if __name__ == "__main__":
    main()
