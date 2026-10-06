#!/usr/bin/env python3
"""The core roster, tier 1 (docs/BACKLOG.md issue #121, proposal B7 of
docs/VISUAL_PROPOSALS.md): the three stock Red Alert sprites on screen in every
match of either faction, replaced with Sungrid art on the conventions this
file locks for every unit that follows.

  MCV   mcv.png       32 facings (+ mcvicon.png, mcvhusk.png 32 facings)
  HARV  harv.png      idle 32 + harvest 8 facings x 8 + dock 8 + dock-loop 7
        harvhalf.png / harvempty.png  the same 111-frame layout per fullness
        hhusk.png / hhusk2.png  laden / empty wreck, 32 facings each
        harvicon.png
  E1    e1.png        the stock e1.shp layout, 378 frames (+ e1icon.png)

Every sheet mirrors the stock .shp's frame order and count exactly, so the
sequence YAML changes by Filename only - the same rule the Hauler Drone's
sheets follow against harv.shp, and the Disruptor Trooper's against e4.shp.

Conventions (also in CLAUDE.md):

  Vehicles are `Mesh` solids rendered at 32 genuine yaws through
  gen_concept_art's `_mesh_render`, frame 0 facing north (+y in model
  space, the direction sgtur_mesh's gun points) and the yaw advancing
  counter-clockwise by 360/32 per frame - the engine's own facing sense
  (WVec.Yaw: 0 north, 256 west). The model's ground origin lands on the
  frame centre plus a few rows, so the hull mass sits centred; the cast
  shadow is the mesh's own `draw_shadow` through `render_shadow_mask` and
  goes in as the ShadowIndex stencil via `indexed_strip`, exactly like the
  two defence pedestals. No readability outline - a solid wearing one is a
  sticker (art rule 19). Team colour is `accent=True` faces, re-stamped by
  `_mesh_render` onto the remap ramp. Sub-animations are facing-major
  (`Facings` x `Length`), and a single-facing animation (the Harvester's
  dock) is drawn at the facing the engine will show it at - the Refinery's
  `DockAngle: 256`, west.

  Infantry is authored at native resolution in palette indices on the `PC`
  canvas, the Disruptor Trooper's way (art rule 7 and issue #64): 20x26 frame,
  boots on the centre row, eight genuine viewpoints, body on the remap ramp.
  The rifleman reuses the trooper's legs, torso and shadow so the two read
  as one army, and differs in what a rifleman differs in: a plain helmet, no
  discharge cell, a rifle with a muzzle flash.

Usage:
    pip install pillow
    python3 gen_core_units.py
Writes the sheets next to this file (mods/sungrid/bits/).
"""
import math
import os

from PIL import Image

from gen_concept_art import (
    SS, SD, PC, Mesh,
    GREEN_PRIMARY, GREEN_ACCENT, PANEL_BLUEBLACK, SUN_GOLD,
    LEGACY_GRAY, LEGACY_GRAY_DARK, RUST, DAMAGE_SCORCH, POLE_DARK, CONCRETE,
    PALE_STEEL, STEEL, AMBER, LAMP_OFF,
    lit, dim, mix,
    _mesh_render, render_shadow_mask, indexed_strip, sheet_of_indexed,
    save_pngsheet, make_icon, make_icon_from_motif, indexed_to_rgba,
    ICON_W, ICON_H,
    DISR_W, DISR_H, DISR_CX, DISR_GROUND, DISR_TORSO_TOP, DISR_TORSO_BOT, DISR_HEAD_TOP, DISR_HIP,
    DISR_AIM, DISR_ROD_READY, DISR_ROD_REST,
    _disr_shadow, _disr_legs, _disr_torso,
    A_LIT, A_MID, A_SHD, A_DRK, A_DEEP, H_LIT, H_MID, H_SHD, RIM, BOOT, GOLD, GOLD_LIT, GOLD_DRK,
    SHADOW_IDX,
)

HERE = os.path.dirname(os.path.abspath(__file__))

FACINGS = 32
_TRACK = mix(LEGACY_GRAY_DARK, PANEL_BLUEBLACK, 0.4)
_HULL = mix(LEGACY_GRAY, PANEL_BLUEBLACK, 0.3)
_ORE = mix(RUST, LEGACY_GRAY, 0.45)           # the Harvester's load: a rust-brown heap,
_ORE_LIT = mix(AMBER, _ORE, 0.5)               # far from the gold ramp on purpose
_CHAR = mix(_HULL, DAMAGE_SCORCH, 0.5)


def _scorched(col, damaged, f=0.45):
    return mix(col, DAMAGE_SCORCH, f) if damaged else col


# ---------------------------------------------------------------------------
# Vehicle frame machinery
# ---------------------------------------------------------------------------

def vehicle_frame(mesh, w, h, oy_shift, deg, decals=None):
    """One facing of a vehicle: the shaded solid plus its own cast-shadow
    stencil, at the frame centre (ground origin `oy_shift` rows below it)."""
    ox, oy = w // 2, h // 2 + oy_shift
    body = _mesh_render(mesh, w, h, ox, oy, deg, decals=decals)
    shadow = render_shadow_mask(lambda sd, w_, h_: mesh.draw_shadow(sd, ox, oy, deg), w, h)
    return body, shadow


def facing_frames(mesh_fn, w, h, oy_shift, n=FACINGS, decals=None, **kw):
    """n genuine viewpoints, frame 0 north, counter-clockwise."""
    bodies, shadows = [], []
    for i in range(n):
        b, s = vehicle_frame(mesh_fn(**kw), w, h, oy_shift, i * 360.0 / n, decals=decals)
        bodies.append(b)
        shadows.append(s)
    return bodies, shadows


def pods(m, x_in, x_out, y0, y1, z, col, axles=(), hub=None):
    """Track/wheel pods down both flanks, with a hub plate per axle on the
    outer face so the side view reads as wheels rather than a skirt."""
    for side in (-1, 1):
        xa, xb = sorted((side * x_in, side * x_out))
        m.box(xa, y0, 0, xb, y1, z, col, top=lit(col, 0.12))
        for ay in axles:
            hx = side * x_out
            m.box(min(hx, hx + side * 0.35), ay - 1.4, 0.7, max(hx, hx + side * 0.35), ay + 1.4, z - 0.7,
                  hub or lit(col, 0.3), order=1, shadow=False)


def flank_band(m, x, y0, y1, z, live=True):
    """The team-colour conduit band along both flanks - the roster's 'grid
    connection' tell, carried by every Sungrid vehicle."""
    col = SUN_GOLD if live else dim(SUN_GOLD, 0.4)
    for side in (-1, 1):
        xa, xb = sorted((side * x, side * (x + 0.35)))
        m.box(xa, y0, z, xb, y1, z + 0.9, col, top=lit(col, 0.25), order=1, shadow=False, accent=True)


# ---------------------------------------------------------------------------
# MCV: a six-wheel flatbed carrying the folded Construction Yard - crane mast
# lying along the bed, folded array crates, a cab up front. It deploys into
# sgfact (the Sungrid Construction Yard), whose mast and beacon it borrows.
# ---------------------------------------------------------------------------

MCV_W, MCV_H = 48, 40
MCV_OY = 4


def mcv_mesh(damaged=False):
    m = Mesh()
    hull = _scorched(_HULL, damaged)
    pods(m, 3.8, 6.2, -10.0, 10.0, 3.2, _scorched(_TRACK, damaged, 0.3), axles=(-7.0, 0.0, 7.0))
    # Flatbed.
    m.box(-4.0, -11.0, 2.8, 4.0, 9.0, 5.2, hull, top=lit(hull, 0.18))
    flank_band(m, 4.0, -9.5, 3.5, 3.9, live=not damaged)
    # Cab: pale steel, dark windscreen band, a roof beacon.
    cab = _scorched(PALE_STEEL, damaged, 0.5)
    cab_top = 10.4 if not damaged else 8.6
    m.box(-4.0, 5.0, 5.2, 4.0, 10.6, cab_top, cab, top=lit(cab, 0.15))
    m.box(-3.4, 10.3, 7.2, 3.4, 10.7, cab_top - 1.0, PANEL_BLUEBLACK, order=1, shadow=False)
    m.box(-4.1, 7.4, 7.2, 4.1, 9.2, cab_top - 1.0, PANEL_BLUEBLACK, order=1, shadow=False)
    if not damaged:
        m.box(-0.8, 6.0, cab_top, 0.8, 7.4, cab_top + 1.0, AMBER, order=1, shadow=False)
    # Folded crane mast along the bed, on two cradles; the hook block aft.
    mast = _scorched(STEEL, damaged, 0.4)
    if not damaged:
        for y in (-8.0, 1.5):
            m.box(-2.6, y - 0.6, 5.2, -0.4, y + 0.6, 6.4, dim(hull, 0.15), shadow=False)
        m.strut((-1.5, -10.0, 6.9), (-1.5, 4.2, 6.9), 0.85, mast, cap=dim(mast, 0.3))
        m.box(-2.4, -10.6, 5.2, -0.6, -9.0, 8.2, dim(mast, 0.2), top=lit(mast, 0.1), shadow=False)
    else:
        # Mast thrown off the bed and lying beside it, cradles empty.
        m.strut((-6.0, -9.0, 0.6), (-8.5, 5.0, 0.6), 0.85, mast, cap=dim(mast, 0.3))
    # Folded array crates (panel-blue tops) and a stores locker.
    if not damaged:
        crate = PANEL_BLUEBLACK
        m.box(0.6, -9.2, 5.2, 3.8, -3.0, 8.2, dim(crate, 0.1), top=lit(crate, 0.35))
        m.box(0.6, -2.2, 5.2, 3.8, 3.6, 7.4, dim(crate, 0.1), top=lit(crate, 0.35))
        m.box(0.6, -9.2, 8.2, 3.8, -3.0, 8.5, GREEN_PRIMARY, top=GREEN_PRIMARY, order=1, shadow=False)
    else:
        m.box(0.6, -9.2, 5.2, 3.8, -5.0, 6.4, _CHAR, top=dim(_CHAR, 0.1))
    # Rear bumper and tail lamps.
    m.box(-4.4, -11.4, 2.6, 4.4, -10.8, 3.6, dim(hull, 0.35), shadow=False)
    if not damaged:
        for x in (-3.6, 3.0):
            m.box(x, -11.5, 3.8, x + 0.6, -11.2, 4.4, AMBER, order=1, shadow=False)
    return m


def _mcv_decals(sd, w, h):
    ox, oy = w // 2, h // 2 + MCV_OY
    sd.ellipse([ox - 2.0, oy - 9.0, ox + 2.6, oy - 6.6], fill=DAMAGE_SCORCH + (235,))
    sd.ellipse([ox + 1.0, oy - 3.5, ox + 4.0, oy - 2.0], fill=(0, 0, 0, 225))
    sd.rect([ox - 4.6, oy - 1.0, ox - 3.9, oy + 2.5], fill=RUST + (220,))


def mcv_icon_draw(sd, w, h):
    m = mcv_mesh()
    m.draw_shadow(sd, w / 2, h * 0.66, 30.0, color=(0, 0, 0, 70))
    m.draw(sd, w / 2, h * 0.66, 30.0)


# ---------------------------------------------------------------------------
# HARV: the Ore Truck - a tracked collector with a front intake drum, a
# covered conveyor and an open rear hopper whose heap is the fullness.
# ---------------------------------------------------------------------------

HARV_W, HARV_H = 44, 36
HARV_OY = 3
HARV_HARVEST_FRAMES = 8
HARV_DOCK_FRAMES = 8
HARV_DOCK_LOOP_FRAMES = 7
HARV_DOCK_YAW = 90.0        # the Refinery's DockAngle 256 = west


def harv_mesh(fullness="full", damaged=False, harvest=None, gate=0.0, stream=None):
    """`harvest` is the intake phase (0..1) or None; `gate` the tailgate
    opening (0..1); `stream` the unload-stream phase (0..1) or None."""
    m = Mesh()
    hull = _scorched(_HULL, damaged)
    steel = _scorched(STEEL, damaged, 0.4)
    pods(m, 3.6, 6.0, -9.0, 9.0, 3.4, _scorched(_TRACK, damaged, 0.3), axles=(-6.0, 0.0, 6.0),
         hub=dim(_TRACK, 0.2))
    m.box(-3.8, -9.0, 3.0, 3.8, 8.0, 6.0, hull, top=lit(hull, 0.18))
    flank_band(m, 3.8, -7.5, 3.0, 4.2, live=not damaged)
    # Sensor cab, front left: no crew, one dark eye strip.
    cab = _scorched(PALE_STEEL, damaged, 0.5)
    m.box(-3.6, 3.5, 6.0, 0.6, 8.0, 9.2, cab, top=lit(cab, 0.15))
    m.box(-3.0, 7.9, 7.3, 0.0, 8.2, 8.5, PANEL_BLUEBLACK, order=1, shadow=False)
    if not damaged:
        m.box(-2.2, 4.5, 9.2, -1.2, 5.5, 10.0, AMBER, order=1, shadow=False)
    # Intake drum across the front, with teeth that cycle on the harvest phase.
    m.box(-3.4, 8.2, 0.6, 3.4, 10.4, 3.4, steel, top=lit(steel, 0.2))
    if harvest is not None and not damaged:
        for k in range(3):
            ph = (harvest + k / 3.0) % 1.0
            tz = 0.8 + 2.2 * ph
            m.box(-2.8 + k * 2.0, 10.3, tz, -1.8 + k * 2.0, 10.7, tz + 0.5, dim(steel, 0.3), order=1, shadow=False)
        # Loose material thrown up into the conveyor mouth.
        for k in range(2):
            ph = (harvest * 2 + k * 0.5) % 1.0
            m.box(-0.6 + k * 0.8, 9.6 - 2.0 * ph, 3.6 + 3.0 * ph, 0.0 + k * 0.8, 9.0 - 2.0 * ph, 4.1 + 3.0 * ph,
                  _ORE_LIT if k else _ORE, shadow=False)
    # Covered conveyor from the intake up into the hopper.
    if not damaged:
        m.strut((1.6, 9.4, 3.2), (1.6, 1.0, 9.6), 1.1, steel, cap=dim(steel, 0.3))
    else:
        m.strut((1.6, 9.4, 3.2), (3.2, 4.0, 5.8), 1.1, steel, cap=dim(steel, 0.3))
    # Hopper: four walls, open top; the heap inside is the fullness.
    hz0, hz1 = 6.0, 9.4
    wall = _scorched(mix(STEEL, PALE_STEEL, 0.4), damaged, 0.45)
    m.box(-3.6, -8.5, hz0, -2.9, 2.0, hz1, wall, top=lit(wall, 0.15))
    m.box(2.9, -8.5, hz0, 3.6, 2.0, hz1, wall, top=lit(wall, 0.15))
    m.box(-3.6, 1.3, hz0, 3.6, 2.0, hz1, wall, top=lit(wall, 0.15))
    # Tailgate: closed, or swung open about its bottom hinge by `gate`.
    ang = math.radians(gate * 75.0)
    gy0, gy1 = -8.5, -8.5 - 3.4 * math.sin(ang)
    gz1 = hz0 + 3.4 * math.cos(ang)
    m.quad((-3.6, gy0, hz0), (3.6, gy0, hz0), (3.6, gy1, gz1), (-3.6, gy1, gz1), wall, order=1)
    m.quad((-3.6, gy1, gz1), (3.6, gy1, gz1), (3.6, gy0, hz0), (-3.6, gy0, hz0), dim(wall, 0.2), order=1)
    m.box(-2.9, -8.5, hz0, 2.9, 1.3, hz0 + 0.3, dim(hull, 0.45), shadow=False)
    heap = {"empty": 0.0, "half": 1.3, "full": 3.0}[fullness]
    if heap > 0:
        m.box(-2.9, -8.3, hz0, 2.9, 1.2, hz0 + heap, _ORE, top=lit(_ORE, 0.1), shadow=False)
        m.box(-1.9, -6.5, hz0 + heap, 1.6, -0.5, hz0 + heap + 1.2, _ORE, top=_ORE_LIT, shadow=False)
        if heap > 2:
            m.box(-0.9, -5.5, hz0 + heap + 1.2, 0.8, -1.8, hz0 + heap + 2.0, _ORE_LIT, top=lit(_ORE_LIT, 0.2),
                  shadow=False)
    # Unload stream out of the open gate, falling behind the truck.
    if stream is not None and heap > 0:
        for k in range(4):
            ph = (stream + k / 4.0) % 1.0
            y = -9.5 - 3.5 * ph
            z = hz0 + 1.5 - 5.0 * ph * ph
            if z < 0.2:
                continue
            m.box(-1.2 + k * 0.7, y - 0.5, z, -0.4 + k * 0.7, y + 0.3, z + 0.7, _ORE_LIT if k % 2 else _ORE,
                  shadow=False)
    return m


def _harv_decals(sd, w, h):
    ox, oy = w // 2, h // 2 + HARV_OY
    sd.ellipse([ox - 3.0, oy - 8.5, ox + 1.0, oy - 6.2], fill=DAMAGE_SCORCH + (235,))
    sd.ellipse([ox + 0.5, oy - 2.0, ox + 3.5, oy - 0.6], fill=(0, 0, 0, 225))
    sd.rect([ox - 4.4, oy - 3.0, ox - 3.7, oy + 1.5], fill=RUST + (220,))


def harv_sheet(fullness):
    """idle(32) + harvest(8 facings x 8, facing-major) + dock(8) + dock-loop(7)
    = 111 frames, the stock harv.shp layout, so the Start offsets in
    sequences/vehicles.yaml are unchanged."""
    bodies, shadows = facing_frames(harv_mesh, HARV_W, HARV_H, HARV_OY, fullness=fullness)
    for f in range(8):
        for p in range(HARV_HARVEST_FRAMES):
            b, s = vehicle_frame(harv_mesh(fullness=fullness, harvest=p / HARV_HARVEST_FRAMES),
                                 HARV_W, HARV_H, HARV_OY, f * 45.0)
            bodies.append(b)
            shadows.append(s)
    for k in range(HARV_DOCK_FRAMES):
        b, s = vehicle_frame(harv_mesh(fullness=fullness, gate=k / (HARV_DOCK_FRAMES - 1)),
                             HARV_W, HARV_H, HARV_OY, HARV_DOCK_YAW)
        bodies.append(b)
        shadows.append(s)
    for k in range(HARV_DOCK_LOOP_FRAMES):
        b, s = vehicle_frame(harv_mesh(fullness=fullness, gate=1.0, stream=k / HARV_DOCK_LOOP_FRAMES),
                             HARV_W, HARV_H, HARV_OY, HARV_DOCK_YAW)
        bodies.append(b)
        shadows.append(s)
    assert len(bodies) == 32 + 64 + 8 + 7
    return bodies, shadows


def harv_icon_draw(sd, w, h):
    m = harv_mesh("full")
    m.draw_shadow(sd, w / 2, h * 0.66, 35.0, color=(0, 0, 0, 70))
    m.draw(sd, w / 2, h * 0.66, 35.0)


# ---------------------------------------------------------------------------
# E1: the rifleman, on the Disruptor Trooper's figure.
# ---------------------------------------------------------------------------

E1_W, E1_H = DISR_W, DISR_H
E1_SHOOT_FRAMES = 8
E1_BLANK = 35               # frames 342-376 of e1.shp are not referenced by any sequence


def _e1_head(c, facing, cx=DISR_CX, top=DISR_HEAD_TOP, turn=0.0):
    """Plain helmet: lit crown, a dark visor strip on the facings that show
    the face, no gold - the trooper's visor is his, not the army's."""
    hx = cx + turn
    c.hline(hx - 1, hx + 1, top, H_LIT)
    c.set(hx + 1, top, H_MID)
    c.hline(hx - 1, hx + 1, top + 1, H_MID)
    c.set(hx + 1, top + 1, H_SHD)
    c.hline(hx - 1, hx + 1, top + 2, H_SHD)
    c.set(hx, top + 2, H_MID)
    if facing in (3, 4, 5):
        c.hline(hx - 1, hx, top + 1, RIM)
    elif facing == 2:
        c.set(hx - 1, top + 1, RIM)
    elif facing == 6:
        c.set(hx + 1, top + 1, RIM)
    else:
        c.set(hx, top + 1, H_LIT)


def _e1_rifle(c, facing, pose, cx, torso_top, flash=0):
    """A carbine on the trooper's per-facing weapon geometry: dark barrel,
    lit top edge at the grip, a white-gold muzzle flash when firing."""
    x0, y0, x1, y1 = (DISR_ROD_READY if pose in ("ready", "fire") else DISR_ROD_REST)[facing]
    gx, gy = cx + x0, torso_top + y0
    bx, by = cx + x1, torso_top + y1
    c.ray(gx, gy, bx, by, H_SHD)
    c.set(gx, gy, H_MID)
    c.set(bx, by, H_LIT)
    if flash:
        ang = math.atan2(by - gy, bx - gx)
        fx, fy = bx + round(math.cos(ang)), by + round(math.sin(ang))
        c.set(fx, fy, 15)
        if flash > 1:
            c.set(fx + round(math.cos(ang)), fy + round(math.sin(ang)), GOLD_LIT)
            c.set(fx - round(math.sin(ang)), fy + round(math.cos(ang)), GOLD)


def e1_upright(facing, pose="rest", phase=None, flash=0, turn=0.0, dy=0, ground=DISR_GROUND, shadow=True):
    c = PC(E1_W, E1_H)
    cx = DISR_CX
    if shadow:
        _disr_shadow(c, cx, ground)
    torso_top, torso_bot, head_top = DISR_TORSO_TOP + dy, DISR_TORSO_BOT + dy, DISR_HEAD_TOP + dy
    away = facing in (0, 1, 7)
    arm_swing = 0 if phase is None else (1 if math.sin(phase * 2 * math.pi) > 0 else -1)
    if away:
        _e1_rifle(c, facing, pose, cx, torso_top, flash)
    _disr_legs(c, facing, phase, cx, ground)
    _disr_torso(c, facing, cx, torso_top, torso_bot, 3, arm_swing)   # pulse 3: pips dark
    _e1_head(c, facing, cx, head_top, turn)
    if not away:
        _e1_rifle(c, facing, pose, cx, torso_top, flash)
    return c


def e1_prone(facing, phase=None, shoot=None):
    c = PC(E1_W, E1_H)
    cx, ground = DISR_CX, DISR_GROUND
    _disr_shadow(c, cx, ground + 1, flat=True)
    ax, ay = DISR_AIM[facing]
    ox, oy = cx, ground - 1
    crawl = 0.0 if phase is None else math.sin(phase * 2 * math.pi)

    def at(t, lateral=0.0):
        return (ox + ax * t - ay * lateral * 1.2, oy + ay * t * 0.55 + ax * lateral * 0.6)

    for s in (-1, 1):
        lx, ly = at(-3.4 - 0.6 * s * crawl, 0.8 * s)
        c.blob(lx, ly, 1.1, 1.0, A_SHD if s < 0 else A_DRK)
        c.set(lx, ly + 1, BOOT)
    for t, r, idx in ((-1.9, 1.4, A_SHD), (-0.2, 1.8, A_MID), (1.5, 1.5, A_LIT)):
        bx, by = at(t)
        c.blob(bx, by, r, r * 0.85, idx)
    hx, hy = at(3.2)
    c.blob(hx, hy, 1.5, 1.3, H_MID)
    c.set(hx - 1, hy - 1, H_LIT)
    c.set(hx + 1, hy + 1, H_SHD)
    gx, gy = at(2.0, 1.0)
    tx, ty = at(5.2, 0.8)
    c.ray(gx, gy, tx, ty, H_SHD)
    c.set(tx, ty, H_LIT)
    if shoot is not None and shoot in (1, 2):
        fx, fy = at(6.3, 0.8)
        c.set(round(fx), round(fy), 15)
        if shoot == 1:
            fx2, fy2 = at(7.2, 0.8)
            c.set(round(fx2), round(fy2), GOLD_LIT)
    return c


def _e1_dying(t, dir_sign, keep=1.0):
    c = PC(E1_W, E1_H)
    cx, ground = DISR_CX, DISR_GROUND
    ease = t * t * (3 - 2 * t)
    _disr_shadow(c, cx, ground, wide=round(3 * ease * max(0.0, keep * 2 - 1)), flat=ease > 0.65 and keep > 0.5)
    theta = math.radians(90 * (1 - ease))
    hip_x = cx + dir_sign * 2.6 * ease
    hip_y = ground - 3.0 * (1 - ease) - 0.5
    dx, dy = dir_sign * math.cos(theta), -math.sin(theta)
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
    if ease < 0.5:
        c.ray(hip_x + dx * 4, hip_y + dy * 4 + 1, hip_x + dir_sign * 5, ground - 1, H_SHD)
    else:
        c.hline(hip_x + dir_sign * 3, hip_x + dir_sign * 6, ground - 1, H_SHD)
    if keep < 1.0:
        c.dissolve(keep)
    return c


def _e1_die_frames(n, dir_sign, dissolve_from=None):
    out = []
    for i in range(n):
        t = i / max(1, n - 1)
        keep = 1.0
        if dissolve_from is not None and t > dissolve_from:
            keep = 1.0 - (t - dissolve_from) / (1.0 - dissolve_from)
        out.append(_e1_dying(t, dir_sign, keep=keep))
    return out


def e1_parachute():
    ground = 21
    c = e1_upright(4, "rest", dy=8, ground=ground, shadow=False)
    cx = DISR_CX
    c.hline(cx - 3, cx + 3, 1, H_LIT)
    c.hline(cx - 5, cx + 5, 2, H_MID)
    c.hline(cx - 6, cx + 6, 3, H_SHD)
    c.set(cx - 5, 2, H_LIT)
    c.set(cx - 6, 4, H_SHD)
    c.set(cx + 6, 4, H_SHD)
    c.ray(cx - 5, 4, cx - 1, 8, H_MID)
    c.ray(cx + 5, 4, cx + 1, 8, H_MID)
    return c


def _e1_shoot(facing, p):
    flash = 2 if p == 1 else 1 if p == 2 else 0
    return e1_upright(facing, "fire", flash=flash, dy=-1 if p == 1 else 0)


def e1_frames():
    """The stock e1.shp layout, frame for frame (378 frames)."""
    frames = []
    for pose in ("rest", "ready"):                                   # 0-15 stand, stand2
        frames += [e1_upright(f, pose) for f in range(8)]
    for f in range(8):                                               # 16-63 run
        for p in range(6):
            frames.append(e1_upright(f, "ready", phase=p / 6, dy=-1 if p % 3 == 1 else 0))
    for f in range(8):                                               # 64-127 shoot
        frames += [_e1_shoot(f, p) for p in range(E1_SHOOT_FRAMES)]
    for f in range(8):                                               # 128-143 liedown
        frames += [e1_upright(f, "ready", dy=2), e1_prone(f)]
    for f in range(8):                                               # 144-175 prone-run
        frames += [e1_prone(f, phase=p / 4) for p in range(4)]
    for f in range(8):                                               # 176-191 standup
        frames += [e1_prone(f), e1_upright(f, "ready", dy=2)]
    for f in range(8):                                               # 192-255 prone-shoot
        frames += [e1_prone(f, shoot=p) for p in range(8)]
    # 256-271 idle1: a look left and right; 272-287 idle2: the rifle checked.
    for i in range(16):
        turn = (0, 0, -1, -1, -1, -1, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0)[i]
        frames.append(e1_upright(3 if turn < 0 else 5 if turn > 0 else 4, "rest"))
    for i in range(16):
        frames.append(e1_upright(4, "ready" if 3 <= i < 13 else "rest"))
    frames += _e1_die_frames(8, 1)                                   # 288 die1
    frames += _e1_die_frames(8, -1)                                  # 296 die2
    frames += _e1_die_frames(8, 1, dissolve_from=0.6)                # 304 die3
    frames += _e1_die_frames(12, -1, dissolve_from=0.5)              # 312 die4
    frames += _e1_die_frames(18, 1, dissolve_from=0.45)              # 324 die5
    frames += [PC(E1_W, E1_H) for _ in range(E1_BLANK)]              # 342-376 unused
    frames.append(e1_parachute())                                    # 377
    assert len(frames) == 378, len(frames)
    return frames


# ---------------------------------------------------------------------------

def main():
    # MCV: 32 facings, husk, cameo.
    bodies, shadows = facing_frames(mcv_mesh, MCV_W, MCV_H, MCV_OY)
    save_pngsheet(indexed_strip(bodies, shadows, MCV_W, MCV_H), "mcv.png", MCV_W, MCV_H, len(bodies), indexed=True)
    bodies, shadows = facing_frames(mcv_mesh, MCV_W, MCV_H, MCV_OY, decals=_mcv_decals, damaged=True)
    save_pngsheet(indexed_strip(bodies, shadows, MCV_W, MCV_H), "mcvhusk.png", MCV_W, MCV_H, len(bodies), indexed=True)
    save_pngsheet(make_icon(mcv_icon_draw, 56, 44, label="MCV"), "mcvicon.png", ICON_W, ICON_H, 1)

    # HARV: three fullness images on one layout, two husks, cameo.
    for fullness, filename in (("full", "harv.png"), ("half", "harvhalf.png"), ("empty", "harvempty.png")):
        bodies, shadows = harv_sheet(fullness)
        save_pngsheet(indexed_strip(bodies, shadows, HARV_W, HARV_H), filename, HARV_W, HARV_H, len(bodies), indexed=True)
    for fullness, filename in (("full", "hhusk.png"), ("empty", "hhusk2.png")):
        bodies, shadows = facing_frames(harv_mesh, HARV_W, HARV_H, HARV_OY, decals=_harv_decals,
                                        fullness=fullness, damaged=True)
        save_pngsheet(indexed_strip(bodies, shadows, HARV_W, HARV_H), filename, HARV_W, HARV_H, len(bodies), indexed=True)
    save_pngsheet(make_icon(harv_icon_draw, 56, 44, label="Ore Truck"), "harvicon.png", ICON_W, ICON_H, 1)

    # E1: one self-contained sheet on the stock layout, cameo from the
    # three-quarter ready frame like the Disruptor's.
    frames = e1_frames()
    save_pngsheet(sheet_of_indexed(frames, E1_W, E1_H), "e1.png", E1_W, E1_H, len(frames), indexed=True)
    motif = indexed_to_rgba(e1_upright(5, "ready"))
    motif = motif.crop(motif.getbbox())
    motif = motif.resize((motif.width * SS, motif.height * SS), Image.NEAREST)
    save_pngsheet(make_icon_from_motif(motif, label="Rifle Infantry"), "e1icon.png", ICON_W, ICON_H, 1)
    print("done")


if __name__ == "__main__":
    main()
