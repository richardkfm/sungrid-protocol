#!/usr/bin/env python3
"""The core roster, tier 1 (docs/BACKLOG.md issue #121, proposal B7 of
docs/VISUAL_PROPOSALS.md): the stock Red Alert vehicles on screen in every
match of either faction, replaced with Sungrid art on the conventions this
file locks for every unit that follows.

  MCV   mcv.png       32 facings (+ mcvicon.png, mcvhusk.png 32 facings)
  HARV  harv.png      idle 32 + harvest 8 facings x 8 + dock 8 + dock-loop 7
        harvhalf.png / harvempty.png  the same 111-frame layout per fullness
        hhusk.png / hhusk2.png  laden / empty wreck, 32 facings each
        harvicon.png

The rifleman this file also drew (e1.png on e1.shp's 378-frame layout, on
the Disruptor Trooper's figure) went back to the stock sprite in issue #123
at the owner's call; the drawing is in git history at the #121/#122 commits
if a later tier wants to pick it up again. The two cameos are scene renders
(scene_cameo, issue #123), not the flat panel make_icon() gives a building.

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

from PIL import Image, ImageDraw

from gen_concept_art import (
    SS, SD, Mesh,
    GREEN_PRIMARY, PANEL_BLUEBLACK, SUN_GOLD,
    LEGACY_GRAY, LEGACY_GRAY_DARK, RUST, DAMAGE_SCORCH, CONCRETE, PAD_TOP,
    PALE_STEEL, STEEL, AMBER, lit, dim, mix,
    _mesh_render, render_shadow_mask, indexed_strip,
    save_pngsheet, draw_icon_label, scene_cameo,
    ICON_W, ICON_H,
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


# ---------------------------------------------------------------------------
# Cameos (issue #123): the vehicle at three-quarter view in a scene -- a sky
# ramp over a horizon haze, a ground plane in the terrain green with a lit
# verge and its cast shadow -- instead of on the bare blue-black panel the
# make_icon() fallback gives a building. The owner read that panel as bland
# beside the photographic cameos; this is the same tonal range those have
# (dark sky, lit subject, dark foot) without pretending to be a photograph.
# ---------------------------------------------------------------------------

# scene_cameo() moved to gen_concept_art.py in issue #126 so the Materials
# Refinery's cameo can share it; imported above.


# ---------------------------------------------------------------------------

def main():
    # MCV: 32 facings, husk, cameo.
    bodies, shadows = facing_frames(mcv_mesh, MCV_W, MCV_H, MCV_OY)
    save_pngsheet(indexed_strip(bodies, shadows, MCV_W, MCV_H), "mcv.png", MCV_W, MCV_H, len(bodies), indexed=True)
    bodies, shadows = facing_frames(mcv_mesh, MCV_W, MCV_H, MCV_OY, decals=_mcv_decals, damaged=True)
    save_pngsheet(indexed_strip(bodies, shadows, MCV_W, MCV_H), "mcvhusk.png", MCV_W, MCV_H, len(bodies), indexed=True)
    save_pngsheet(scene_cameo(mcv_mesh(), "MCV", yaw=30.0, lift=1.0), "mcvicon.png", ICON_W, ICON_H, 1)

    # HARV: three fullness images on one layout, two husks, cameo.
    for fullness, filename in (("full", "harv.png"), ("half", "harvhalf.png"), ("empty", "harvempty.png")):
        bodies, shadows = harv_sheet(fullness)
        save_pngsheet(indexed_strip(bodies, shadows, HARV_W, HARV_H), filename, HARV_W, HARV_H, len(bodies), indexed=True)
    for fullness, filename in (("full", "hhusk.png"), ("empty", "hhusk2.png")):
        bodies, shadows = facing_frames(harv_mesh, HARV_W, HARV_H, HARV_OY, decals=_harv_decals,
                                        fullness=fullness, damaged=True)
        save_pngsheet(indexed_strip(bodies, shadows, HARV_W, HARV_H), filename, HARV_W, HARV_H, len(bodies), indexed=True)
    save_pngsheet(scene_cameo(harv_mesh("full"), "Ore Truck", yaw=35.0, lift=2.0), "harvicon.png", ICON_W, ICON_H, 1)

    print("done")


if __name__ == "__main__":
    main()
