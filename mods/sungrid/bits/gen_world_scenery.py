#!/usr/bin/env python3
"""Terrain and world pass (docs/BACKLOG.md issue #122): the six neutral
scenery actors, the two civilian tech buildings rebuilt as solids, and the
Legacy Derrick's palette.

Everything here is drawn with gen_concept_art.py's vocabulary -- the `Mesh`
axonometric renderer at BUILDING_YAW, the greenery (`bed`, `shrub`, `tuft`,
`tree`, `vines`, `green_roof`), `_mesh_render`'s accent re-stamp, the stock-
style silhouette shadow -- so a planter beside a Sensor Array is lit by the
same key light and quantised to the same palette.

Scenery renders through the `player` palette like `^Box` does (not the
reskinned `terrain` palette a stock tree uses): `player` is the same stock
temperat.pal on every tileset, so a rust plate stays rust on snow instead of
being hue-shifted toward green with the ground. None of these carries team
colour -- there is no gold on a neutral actor -- so nothing lands on the
remap ramp and the choice of palette changes nothing but tileset stability.

Scenery sheets are the 1x1 roster frame (40x36) at the 1x1 ground origin,
two frames each (idle, damaged); the pieces sit on the bare cell with no
concrete plinth and no conduit band, because they are not grid-connected.
HOSP mirrors stock hosp.shp's layout (idle 0-3, damaged-idle 4-7, dead 8) and
BIO mirrors bio.shp's (idle 0, damaged-idle 1, dead 2), so their sequence
nodes change by Filename only. Both are 2x2 and use the roster's 2x2 family.

Outputs (all into this directory):
  sgpan.png sgslv.png sgpyl.png sgtnk.png sgrak.png sgpln.png   scenery
  hosp.png hospmake.png bio.png biomake.png                     civilian tech
  sungrid-legacy.pal                                            Legacy Derrick

Re-running is byte-identical: every scatter position is a pure integer hash.
"""
import os

from PIL import Image

from gen_concept_art import (
    BARK, BUILDING_YAW, CONCRETE, DAMAGE_SCORCH, DIRT, FAM, GREEN_ACCENT, GREEN_PRIMARY, HERE,
    LAMP_OFF, LEAF_DARK, LEAF_DEEP, LEAF_MID, LEAF_PALE, LEGACY_GRAY, LEGACY_GRAY_DARK, Mesh,
    PAD_TOP, PALE_STEEL, PANEL_BLUEBLACK, POLE_DARK, RUST, SG1x1_H, SG1x1_W, STEEL, _dead_origin,
    _embers, _mesh_render, _oy, _rubble_diamond, _scatter, _scrap_tone, _slab, bed, dim, dome,
    green_roof, indexed_strip, lit, make_frames, mix, plinth, pv_panel, render, save_pngsheet,
    shrub, silhouette_shadow, tilted_disc, tree, tuft, vines,
)

# ---------------------------------------------------------------------------
# Scenery: six 1x1 neutral actors on the bare cell. `damaged=True` is the
# WithSpriteBody damaged state (a Crushable or shot-at pile); there is no
# death frame -- like a stock tree, the actor just goes, and the salvage pile
# leaves its Scrap behind through SpawnsResourceOnDeath.
# ---------------------------------------------------------------------------

SCN_HALF = FAM["1x1"][2]          # the 1x1 cell diamond's half-width, for the ground marks


def _gravel(m, half, col=None, top=None):
    """A service strip barely proud of the ground, filling the cell."""
    m.box(-half, -half, 0, half, half, 0.5, col or dim(CONCRETE, 0.25), top=top or mix(CONCRETE, DIRT, 0.4),
          shadow=False)


def sgpan_mesh(damaged=False):
    """Ground Array: three collector panels in a row on a gravel strip, low
    edge to the front, a cable trench and a junction box along the near edge.
    Damaged: the middle panel is face down on the gravel, the right one scorched."""
    m = Mesh()
    _gravel(m, 12)
    m.box(-11, -10.5, 0.5, 9, -9.5, 0.9, POLE_DARK, top=dim(LEGACY_GRAY, 0.3), order=1, shadow=False)
    m.box(-12, -11.5, 0.5, -8.5, -8.5, 3.2, PANEL_BLUEBLACK, top=lit(PANEL_BLUEBLACK, 0.3))
    for i, x0 in enumerate((-11.5, -3.5, 4.5)):
        if damaged and i == 1:
            m.box(x0, -6, 0.5, x0 + 7, 4, 1.6, dim(PANEL_BLUEBLACK, 0.3), top=dim(LEGACY_GRAY, 0.2))
            m.strut((x0 + 3, -1, 0.5), (x0 + 5.5, 2, 3.5), 0.6, STEEL)
        else:
            pv_panel(m, x0, -6, 7, 10, 0.5, rise=5.0, damaged=damaged and i == 2)
    tuft(m, 10, 9, 0.5, cap=2.2)
    tuft(m, -10, 10, 0.5, cap=1.8)
    return m


def sgslv_mesh(damaged=False):
    """Salvage Pile: a heap of plate stacked on an oil-stained patch, a pipe
    across the front, a wheel leaning on the side, and a severed green cable --
    the one tell that this is grid salvage. Crushing it flattens the heap."""
    m = Mesh()
    k = 0.55 if damaged else 1.0
    m.box(-10, -9, 0, 10, 9, 0.3, dim(DIRT, 0.3), top=mix(DIRT, RUST, 0.25), shadow=False)
    z = 0.3
    for i, (cx, cy, r, h) in enumerate(((0, 0, 8.5, 3.2), (-3, 2, 6.0, 2.6), (3.5, -2.5, 5.0, 2.4), (-1, -1, 3.8, 2.2))):
        if damaged and i == 3:
            break
        m.prism(cx, cy, z, z + h * k, r, _scrap_tone(i + 1), sides=6 + i, top=_scrap_tone(i + 3), phase=i * 0.5)
        z += h * k * 0.8
    m.strut((-9, -7, 0.9), (6, -5, 1.4), 0.8, dim(LEGACY_GRAY, 0.2), cap=LEGACY_GRAY_DARK)
    if not damaged:
        tilted_disc(m, 8.5, -3, 3.0, 3.0, (0.9, -0.3, 0.3), dim(LEGACY_GRAY, 0.25), inner=POLE_DARK, sides=10,
                    back=dim(LEGACY_GRAY, 0.4))
    else:
        tilted_disc(m, 8.5, -3, 0.5, 3.0, (0.1, -0.1, 1.0), dim(LEGACY_GRAY, 0.25), inner=POLE_DARK, sides=10)
    m.strut((-6, 6, 0.4), (-11, 2, 0.3), 0.45, GREEN_ACCENT, cap=GREEN_ACCENT)
    m.box(-4.5, 1.5, z, -1.5, 2.1, z + 0.4, lit(LEGACY_GRAY, 0.5), top=lit(LEGACY_GRAY, 0.6), order=2, shadow=False)
    tuft(m, 10, 8, 0.3, cap=1.6)
    return m


def sgpyl_mesh(damaged=False):
    """Pylon Stump: the torch-cut base of a transmission tower on its footing,
    two brace rings left, ivy up the lit leg, a shrub where the cable drum
    used to sit. Damaged: the near-right leg is sheared and the stump leans."""
    m = Mesh()
    m.box(-7, -7, 0, 7, 7, 1.6, dim(CONCRETE, 0.1), top=lit(CONCRETE, 0.1))
    col = mix(LEGACY_GRAY, RUST, 0.35)
    legs = ((-5, -5), (5, -5), (5, 5), (-5, 5))
    tops = ((-2.8, -2.8), (2.8, -2.8), (2.8, 2.8), (-2.8, 2.8))
    heights = (12.0, 10.5, 12.5, 11.0)
    pts = []
    for i, ((x, y), (tx, ty), h) in enumerate(zip(legs, tops, heights)):
        if damaged and i == 1:
            h = 4.0
            tx, ty = x + 0.8, y - 0.6
        f = h / 12.5
        top = (x + (tx - x) * f, y + (ty - y) * f, 1.6 + h)
        pts.append(top)
        m.strut((x, y, 1.6), top, 0.55, col, cap=RUST)
    for zr, inset in ((5.0, 0.75), (9.2, 0.45)):
        ring = [(x + (tx - x) * (1 - inset), y + (ty - y) * (1 - inset), zr) for (x, y), (tx, ty) in zip(legs, tops)]
        for i in range(4):
            if damaged and zr > 6 and i in (0, 1):
                continue
            m.strut(ring[i], ring[(i + 1) % 4], 0.4, col)
    # Diagonals on the two faces the camera sees.
    m.strut((-5, -5, 1.6), (3.9, -3.9, 9.2), 0.35, dim(col, 0.1))
    m.strut((-5, -5, 1.6), (-3.9, 3.9, 9.2), 0.35, dim(col, 0.1))
    # Ivy climbing the lit leg.
    for i, (z, r) in enumerate(((1.8, 2.2), (4.2, 1.8), (6.6, 1.5))):
        a = _scatter(i, 7, 1)
        m.prism(-5 + a * 0.6, -5 - 0.3, z, z + 2.0, r, LEAF_DEEP if i % 2 else LEAF_DARK, sides=6,
                top=LEAF_MID if not damaged else LEAF_DARK, shadow=False)
    shrub(m, 9.5, -7.5, 0, r=2.4)
    tuft(m, -9, 8, 0, cap=2.2)
    tuft(m, 8, 9.5, 0, cap=1.8)
    return m


def sgtnk_mesh(damaged=False):
    """Rain Tank: a ribbed cistern on a steel stand over a concrete pad, a
    gutter hopper fed by a riser, a tap and trough at the front. Damaged:
    the lid is off, the shell scorched, and the pad is wet under the tap."""
    m = Mesh()
    m.box(-8, -8, 0, 8, 8, 1.2, dim(CONCRETE, 0.12), top=lit(CONCRETE, 0.08))
    for x, y in ((-3.5, -3.5), (3.5, -3.5), (3.5, 3.5), (-3.5, 3.5)):
        m.strut((x, y, 1.2), (x, y, 3.6), 0.6, STEEL)
    tank = PALE_STEEL if not damaged else mix(PALE_STEEL, DAMAGE_SCORCH, 0.3)
    m.prism(0, 0.5, 3.6, 13.0, 6.0, tank, sides=12, top=lit(tank, 0.1))
    for z in (6.0, 10.5):
        m.prism(0, 0.5, z, z + 0.9, 6.2, PANEL_BLUEBLACK, sides=12, top=PANEL_BLUEBLACK, shadow=False)
    if not damaged:
        dome(m, 0, 0.5, 13.0, 6.0, GREEN_PRIMARY, steps=3, height=1.6)
    else:
        m.prism(0, 0.5, 13.0, 13.6, 5.0, dim(tank, 0.4), sides=12, top=DAMAGE_SCORCH, shadow=False)
        m.box(-5, -8.5, 1.2, 3, -6, 1.3, dim(PANEL_BLUEBLACK, 0.2), top=dim(PANEL_BLUEBLACK, 0.1), shadow=False)
    m.box(-9.5, -1.5, 12.5, -6.0, 1.5, 14.5, dim(PALE_STEEL, 0.2), top=lit(PALE_STEEL, 0.1))
    m.strut((-7.8, 0, 1.2), (-7.8, 0, 12.5), 0.5, dim(PALE_STEEL, 0.3))
    m.box(-2, -8.5, 1.2, 2, -6.5, 2.4, dim(STEEL, 0.1), top=lit(STEEL, 0.1))
    m.strut((0, -6.5, 3.6), (0, -6.5, 1.8), 0.4, STEEL)
    shrub(m, 9.5, -8, 0, r=2.0)
    tuft(m, -9, 9, 0, cap=2.0)
    return m


def sgrak_mesh(damaged=False):
    """Bike Shelter: a PV canopy on two posts over four hoops and a bench, one
    bike parked. Damaged: the left post is gone and the canopy lies on it."""
    m = Mesh()
    m.box(-11, -7, 0, 11, 7, 0.6, PAD_TOP, top=lit(PAD_TOP, 0.05), shadow=False)
    m.strut((9, 4, 0.6), (9, 4, 8.0), 0.6, STEEL)
    if not damaged:
        m.strut((-9, 4, 0.6), (-9, 4, 8.0), 0.6, STEEL)
        roof = ((-11.5, -1, 7.5), (11.5, -1, 7.5), (11.5, 7.5, 9.0), (-11.5, 7.5, 9.0))
    else:
        m.strut((-9, 4, 0.6), (-10.5, 1, 2.5), 0.6, STEEL)
        roof = ((-11.5, -1, 1.2), (11.5, -1, 7.5), (11.5, 7.5, 9.0), (-11.5, 7.5, 2.4))
    m.quad(*roof, lit(PANEL_BLUEBLACK, 0.1), order=3)
    a, b, c, d = roof
    m.quad(a, b, (b[0], b[1], b[2] - 0.6), (a[0], a[1], a[2] - 0.6), lit(LEGACY_GRAY, 0.45), order=3)
    m.quad((a[0], a[1] + 0.3, a[2]), (b[0], b[1] + 0.3, b[2]), (b[0], b[1] + 0.8, b[2] + 0.1), (a[0], a[1] + 0.8, a[2] + 0.1),
           lit(LEGACY_GRAY, 0.45), order=4)
    for x in (-6, -2, 2, 6):
        m.strut((x, 1, 0.6), (x, 1, 3.2), 0.4, STEEL)
        m.strut((x + 1.6, 1, 0.6), (x + 1.6, 1, 3.2), 0.4, STEEL)
        m.strut((x, 1, 3.2), (x + 1.6, 1, 3.2), 0.4, STEEL, cap=STEEL)
    m.box(-8, 4.5, 2.4, 4, 6, 3.0, BARK, top=lit(BARK, 0.2))
    m.strut((-7, 5.2, 0.6), (-7, 5.2, 2.4), 0.4, STEEL)
    m.strut((3, 5.2, 0.6), (3, 5.2, 2.4), 0.4, STEEL)
    if not damaged:
        for wx in (-3.6, -0.4):
            tilted_disc(m, wx, -1.5, 2.3, 1.7, (0, -1, 0), dim(LEGACY_GRAY, 0.3), inner=POLE_DARK, sides=10, order=2,
                        back=dim(LEGACY_GRAY, 0.3))
        m.strut((-3.6, -1.5, 2.3), (-1.2, -1.5, 4.2), 0.3, GREEN_PRIMARY)
        m.strut((-1.2, -1.5, 4.2), (-0.4, -1.5, 2.3), 0.3, GREEN_PRIMARY)
    tuft(m, 10, -8.5, 0, cap=2.0)
    tuft(m, -10.5, 8.5, 0, cap=1.8)
    return m


def sgpln_mesh(damaged=False):
    """Rewilded Planter: a concrete street planter overgrown -- a mat of
    groundcover, a shrub, a sapling, ivy spilling down the lit side. Damaged:
    the near-right corner is broken off and the sapling is a stump."""
    m = Mesh()
    rim = dim(CONCRETE, 0.08)
    top = lit(CONCRETE, 0.15)
    m.box(-7.5, -5.5, 0, 7.5, 5.5, 3.6, rim, top=top)
    if damaged:
        m.box(3.5, -5.6, 0, 7.6, -2.2, 3.7, DAMAGE_SCORCH, top=dim(CONCRETE, 0.35), order=1, shadow=False)
        m.box(7.5, -10, 0, 11, -7, 1.4, dim(CONCRETE, 0.2), top=lit(CONCRETE, 0.05))
    bed(m, -6.5, -4.5, 6.5, 4.5, 3.6, h=0.4, step=3.2, lowcap=1.2, salt=22)
    if not damaged:
        tree(m, 2.5, 1.5, 3.8, h=7.5, r=4.2)
    else:
        m.strut((2.5, 1.5, 3.8), (2.5, 1.5, 6.0), 0.7, BARK, cap=dim(BARK, 0.3))
        m.box(-3, -2, 4.0, 3, 3, 4.2, DAMAGE_SCORCH, top=DAMAGE_SCORCH, order=2, shadow=False)
    shrub(m, -4, -1.5, 4.0, r=2.4)
    vines(m, -7.5, -4, 3, 0.6, 3.6, salt=23)
    tuft(m, 10, -8, 0, cap=2.0)
    tuft(m, -9.5, 8, 0, cap=1.8)
    return m


SCENERY = {
    "sgpan": sgpan_mesh, "sgslv": sgslv_mesh, "sgpyl": sgpyl_mesh,
    "sgtnk": sgtnk_mesh, "sgrak": sgrak_mesh, "sgpln": sgpln_mesh,
}

SCN_OX, SCN_OY = SG1x1_W // 2, _oy(SG1x1_H, SCN_HALF)


def scenery_frame(fn, **kw):
    """One finished scenery frame at the 1x1 roster origin."""
    return _mesh_render(fn(**kw), SG1x1_W, SG1x1_H, SCN_OX, SCN_OY, BUILDING_YAW)


def scenery_sheet(name):
    frames = [scenery_frame(SCENERY[name]), scenery_frame(SCENERY[name], damaged=True)]
    return indexed_strip(frames, [silhouette_shadow(f, 2, 2) for f in frames], SG1x1_W, SG1x1_H), frames


# ---------------------------------------------------------------------------
# Civilian tech buildings (proposal C4): the Field Clinic (HOSP) and the Seed
# Vault (BIO) as roster-style solids on the 2x2 plinth, without the conduit
# band -- they are nobody's until captured, and even then they draw no grid.
# ---------------------------------------------------------------------------

CIV_W, CIV_H, CIV_HALF = FAM["2x2"]


def _scorch_decals(spots):
    """2D scorch marks painted over the finished frame (opaque -- indexed
    alpha is 1-bit, a translucent dab would vanish)."""
    def decals(sd, w, h):
        for x, y, rx, ry in spots:
            sd.ellipse([x - rx, y - ry, x + rx, y + ry], fill=DAMAGE_SCORCH)
    return decals


def hosp_mesh(damaged=False, lamp=True):
    """Field Clinic: a long white ward hall under a sedum roof, a glazed
    entrance under a canvas awning, a green plus on the lit wall, a mast lamp
    (the idle animation), a collector and a rain tank in the yard, beds along
    the front. Damaged: awning down on one post, plus dark, shell scorched."""
    m = Mesh()
    plinth(m, CIV_HALF, band=False)
    wall = PALE_STEEL if not damaged else mix(PALE_STEEL, DAMAGE_SCORCH, 0.2)
    m.box(-15, -2, 2.2, 7, 13, 11.0, wall, top=lit(wall, 0.12))
    green_roof(m, -14.5, -1.5, 6.5, 12.5, 11.0, salt=31, path=True)
    m.box(-13, -2.4, 2.2, -8, -2.0, 8.5, PANEL_BLUEBLACK, top=PANEL_BLUEBLACK, order=1, shadow=False)
    for x in (-5, 0, 4):
        m.box(x, -2.3, 5.5, x + 2.6, -2.0, 8.5, lit(PANEL_BLUEBLACK, 0.25), top=lit(PANEL_BLUEBLACK, 0.25), order=1,
              shadow=False)
    plus = GREEN_ACCENT if not damaged else dim(GREEN_ACCENT, 0.45)
    m.box(-15.4, 4.0, 5.0, -15.0, 7.0, 9.5, plus, top=plus, order=1, shadow=False)
    m.box(-15.4, 2.5, 6.5, -15.0, 8.5, 8.0, plus, top=plus, order=2, shadow=False)
    m.strut((-7, -9, 2.2), (-7, -9, 8.5), 0.6, STEEL)
    if not damaged:
        m.strut((-14, -9, 2.2), (-14, -9, 8.5), 0.6, STEEL)
        m.quad((-15, -10, 8.3), (-6, -10, 8.3), (-6, -2, 10.2), (-15, -2, 10.2), LEAF_PALE, order=2)
    else:
        m.quad((-15, -10, 2.6), (-6, -10, 8.3), (-6, -2, 10.2), (-15, -2, 3.4), dim(LEAF_PALE, 0.25), order=2)
    pv_panel(m, 9, 3, 8, 9, 2.2, rise=5.0, damaged=damaged)
    m.prism(13, 13, 2.2, 9.5, 3.2, PALE_STEEL, sides=10, top=GREEN_PRIMARY if not damaged else DAMAGE_SCORCH)
    m.box(8, -15, 2.2, 16.5, -5, 2.5, PAD_TOP, top=lit(PAD_TOP, 0.05), shadow=False)
    m.box(8.5, -14.5, 2.5, 16, -14, 2.6, GREEN_PRIMARY, top=GREEN_PRIMARY, order=1, shadow=False)
    bed(m, -16.5, -16.5, -4, -11.5, 2.2, salt=32, lowcap=1.3)
    shrub(m, 0, -14, 2.2, r=2.2)
    tuft(m, 4, -12, 2.2)
    tuft(m, -1, -8, 2.2)
    m.strut((3, -6, 2.2), (3, -6, 15.5), 0.6, STEEL)
    col = lit(GREEN_ACCENT, 0.45) if lamp else LAMP_OFF
    m.box(2.2, -6.8, 15.5, 3.8, -5.2, 17.0, col, top=lit(col, 0.2), order=3, shadow=False)
    return m


def bio_mesh(damaged=False):
    """Seed Vault: a half-buried concrete vault under a meadow roof with two
    vent stacks, an entrance portal with a steel-rimmed vault door at the
    front, a cold-storage plant at the right, a tree, beds. Damaged: the
    door is blown, a vent is down, the roof is scorched."""
    m = Mesh()
    plinth(m, CIV_HALF, band=False)
    conc = CONCRETE
    m.box(-16, -3, 2.2, 14, 14, 8.5, dim(conc, 0.05), top=lit(conc, 0.1))
    keep = lambda x, y: not (-4 < x < 3.5 and 3 < y < 10.5)
    bed(m, -15.5, -2.5, 13.5, 13.5, 8.5, h=0.8, step=3.4, lowcap=1.4, salt=41, keep=keep)
    if damaged:
        m.box(-12, 5, 9.3, -4, 12, 9.4, DAMAGE_SCORCH, top=DAMAGE_SCORCH, order=2, shadow=False)
    m.prism(-2, 8, 9.3, 12.5, 1.6, PALE_STEEL, sides=8, top=dim(PALE_STEEL, 0.4))
    if not damaged:
        m.prism(1.5, 5, 9.3, 12.5, 1.6, PALE_STEEL, sides=8, top=dim(PALE_STEEL, 0.4))
    else:
        m.strut((1.5, 5, 9.4), (5.5, 2.5, 9.6), 1.4, dim(PALE_STEEL, 0.2), cap=DAMAGE_SCORCH)
    m.box(-8, -13, 2.2, 0, -3, 9.0, conc, top=lit(conc, 0.12))
    door = PANEL_BLUEBLACK if not damaged else DAMAGE_SCORCH
    m.box(-6.8, -13.4, 2.6, -1.2, -13.0, 8.0, door, top=door, order=1, shadow=False)
    rimc = PALE_STEEL if not damaged else dim(PALE_STEEL, 0.3)
    m.box(-7.3, -13.5, 2.4, -0.7, -13.1, 3.0, rimc, top=rimc, order=2, shadow=False)
    m.box(-7.3, -13.5, 7.8, -0.7, -13.1, 8.4, rimc, top=rimc, order=2, shadow=False)
    m.box(-7.3, -13.5, 2.4, -6.7, -13.1, 8.4, rimc, top=rimc, order=2, shadow=False)
    m.box(-1.3, -13.5, 2.4, -0.7, -13.1, 8.4, rimc, top=rimc, order=2, shadow=False)
    if not damaged:
        tilted_disc(m, -4, -13.7, 5.2, 1.5, (0, -1, 0), PALE_STEEL, inner=dim(PALE_STEEL, 0.3), sides=8, order=3)
    m.quad((-8.5, -13, 2.25), (0.5, -13, 2.25), (0.5, -17, 2.25), (-8.5, -17, 2.25), dim(PAD_TOP, 0.1), order=1)
    m.box(5, -14, 2.2, 13, -7, 7.5, PALE_STEEL, top=lit(PALE_STEEL, 0.1))
    for z in (3.4, 4.8, 6.2):
        m.box(5.5, -14.3, z, 12.5, -14.0, z + 0.5, dim(PALE_STEEL, 0.5), top=dim(PALE_STEEL, 0.5), order=1, shadow=False)
    m.strut((12, -7, 7.5), (12, -3, 7.5), 0.5, dim(PALE_STEEL, 0.3))
    if not damaged:
        tree(m, 15, 0, 2.2, h=7.5, r=4.2)
    else:
        m.strut((15, 0, 2.2), (15, 0, 5.5), 0.7, BARK, cap=dim(BARK, 0.3))
    bed(m, -16.5, -16.5, -10, -5, 2.2, salt=42)
    shrub(m, -12, -8, 2.8, r=2.4)
    tuft(m, 3, -16, 2.2)
    tuft(m, 16, -10, 2.2)
    return m


def civ_frame(fn, decals=None, **kw):
    return _mesh_render(fn(**kw), CIV_W, CIV_H, CIV_W // 2, _oy(CIV_H, CIV_HALF), BUILDING_YAW, decals=decals)


def civ_draw_fn(fn):
    """A draw_fn(sd, w, h, **kw) for make_frames: the plain model at the frame origin."""
    ox, oy = CIV_W // 2, _oy(CIV_H, CIV_HALF)

    def draw(sd, w_, h_, **kw):
        fn(**kw).draw(sd, ox, oy, BUILDING_YAW)
    return draw


HOSP_SCORCH = _scorch_decals([(31, 23, 4, 2), (44, 17, 3, 1.5)])
BIO_SCORCH = _scorch_decals([(26, 29, 4, 2), (46, 20, 3, 1.5)])


def hosp_dead_draw(sd, w=CIV_W, h=CIV_H):
    """Field Clinic rubble: the hall down, the awning frame still up, the green
    plus on the ground beside a pale wall slab."""
    ox, oy, half = _dead_origin("2x2")
    _rubble_diamond(sd, ox, oy, half, seed=21)
    _slab(sd, ox - 8, oy - 3, 20, 6, dim(PALE_STEEL, 0.3), lean=1.2)
    _slab(sd, ox + 10, oy + 1, 12, 4, dim(PALE_STEEL, 0.45), lean=-2.0)
    sd.rect([ox - 14, oy + 3, ox - 10, oy + 4], fill=dim(GREEN_ACCENT, 0.3))
    sd.rect([ox - 12.5, oy + 1.5, ox - 11.5, oy + 5.5], fill=dim(GREEN_ACCENT, 0.3))
    sd.line([(ox + 2, oy + 7), (ox + 2, oy - 2)], fill=STEEL, width=1.0)
    sd.line([(ox + 2, oy - 2), (ox + 8, oy - 4)], fill=dim(STEEL, 0.3), width=0.9)
    sd.ellipse([ox - 3, oy - 7, ox + 3, oy - 4], fill=dim(LEAF_PALE, 0.5))
    _embers(sd, [(ox - 6, oy + 2), (ox + 6, oy + 4), (ox + 12, oy - 2), (ox - 2, oy - 1)])


def bio_dead_draw(sd, w=CIV_W, h=CIV_H):
    """Seed Vault rubble: the vault's concrete mass split open, the door lying
    flat, a vent stack across the pile."""
    ox, oy, half = _dead_origin("2x2")
    _rubble_diamond(sd, ox, oy, half, seed=22)
    _slab(sd, ox - 6, oy - 4, 22, 7, dim(CONCRETE, 0.15), lean=1.0)
    _slab(sd, ox + 9, oy + 2, 14, 5, dim(CONCRETE, 0.3), lean=-1.6)
    sd.ellipse([ox - 15, oy + 2, ox - 7, oy + 6], fill=PANEL_BLUEBLACK, outline=dim(PALE_STEEL, 0.2), width=0.7)
    sd.line([(ox - 2, oy + 6), (ox + 6, oy + 1)], fill=dim(PALE_STEEL, 0.3), width=1.4)
    sd.ellipse([ox + 2, oy - 8, ox + 8, oy - 5], fill=LEAF_DARK)
    _embers(sd, [(ox - 8, oy - 1), (ox + 4, oy + 5), (ox + 14, oy), (ox - 3, oy + 2)])


# ---------------------------------------------------------------------------
# Legacy Derrick: the stock oilb.shp through a rust-shifted copy of the player
# palette. Every entry but transparent (0), the shadow stencil (4) and the
# player-remap ramp (80-95) is pulled toward a rust hue at its own luminance
# and slightly desaturated, so the derrick reads as old-world iron next to the
# Sungrid roster without touching the sprite -- the "rust guardrail" in
# docs/ART_DIRECTION.md. PlayerColorPalette@LEGACY still remaps 80-95, so a
# captured derrick keeps its owner's colour.
# ---------------------------------------------------------------------------

LEGACY_SHIFT = 0.45
LEGACY_HUE = (0x9A, 0x4E, 0x30)
REMAP = range(80, 96)


def legacy_palette(pal):
    out = []
    lum_hue = 0.30 * LEGACY_HUE[0] + 0.59 * LEGACY_HUE[1] + 0.11 * LEGACY_HUE[2]
    for i, c in enumerate(pal):
        if i in (0, 4) or i in REMAP:
            out.append(c)
            continue
        lum = 0.30 * c[0] + 0.59 * c[1] + 0.11 * c[2]
        rust = tuple(min(255, round(ch * lum / lum_hue)) for ch in LEGACY_HUE)
        out.append(tuple(round(c[k] * (1 - LEGACY_SHIFT) + rust[k] * LEGACY_SHIFT) for k in range(3)))
    return out


def write_pal(pal, name):
    with open(os.path.join(HERE, name), "wb") as f:
        for c in pal:
            f.write(bytes(ch >> 2 for ch in c))


def main():
    for name in SCENERY:
        sheet, frames = scenery_sheet(name)
        save_pngsheet(sheet, f"{name}.png", SG1x1_W, SG1x1_H, len(frames), indexed=True)

    # Field Clinic: stock hosp.shp's layout -- idle 0-3 (lamp on three, off
    # one), damaged-idle 4-7 (lamp flickers: one on), dead 8.
    hosp = [civ_frame(hosp_mesh, lamp=i < 3) for i in range(4)]
    hosp += [civ_frame(hosp_mesh, decals=HOSP_SCORCH, damaged=True, lamp=i == 1) for i in range(4)]
    hosp.append(render(hosp_dead_draw, CIV_W, CIV_H))
    assert len(hosp) == 9
    save_pngsheet(indexed_strip(hosp, [silhouette_shadow(f, 2, 2) for f in hosp], CIV_W, CIV_H),
                  "hosp.png", CIV_W, CIV_H, len(hosp), indexed=True)
    mk = make_frames(civ_draw_fn(hosp_mesh), CIV_W, CIV_H, final=hosp[0])
    save_pngsheet(indexed_strip(mk, [None] * (len(mk) - 1) + [silhouette_shadow(hosp[0], 2, 2)], CIV_W, CIV_H),
                  "hospmake.png", CIV_W, CIV_H, len(mk), indexed=True)

    # Seed Vault: stock bio.shp's layout -- idle 0, damaged-idle 1, dead 2.
    bio = [civ_frame(bio_mesh), civ_frame(bio_mesh, decals=BIO_SCORCH, damaged=True), render(bio_dead_draw, CIV_W, CIV_H)]
    save_pngsheet(indexed_strip(bio, [silhouette_shadow(f, 2, 2) for f in bio], CIV_W, CIV_H),
                  "bio.png", CIV_W, CIV_H, len(bio), indexed=True)
    mk = make_frames(civ_draw_fn(bio_mesh), CIV_W, CIV_H, final=bio[0])
    save_pngsheet(indexed_strip(mk, [None] * (len(mk) - 1) + [silhouette_shadow(bio[0], 2, 2)], CIV_W, CIV_H),
                  "biomake.png", CIV_W, CIV_H, len(mk), indexed=True)

    from gen_concept_art import PLAYER_PAL
    write_pal(legacy_palette(PLAYER_PAL), "sungrid-legacy.pal")
    print("done")


if __name__ == "__main__":
    main()
