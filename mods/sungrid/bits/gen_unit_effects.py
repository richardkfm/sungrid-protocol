#!/usr/bin/env python3
"""Unit-side effects, wrecks and cameos for the scoped Phase 7 start
(docs/BACKLOG.md issue #120, sections B2-B6 and B8 of docs/VISUAL_PROPOSALS.md).

Everything here is drawn with gen_concept_art.py's own vocabulary (the SD
scaled-draw wrapper, the PC palette-index canvas, the Mesh solid renderer,
rotated_frames for image-plane facings) and saved through its save_pngsheet,
so the same pipeline rules apply: indexed sheets have 1-bit alpha (draw
opaque or dither), frame sizes and counts are fixed by the sequence YAML,
and re-running this script must leave every other sheet byte-identical.

What it writes, by proposal:

  (B3's bolt, bloom and impact for the Grid Defense Turret were withdrawn
   in issue #123: the owner preferred it as a heavy gun, so GridPulseCannon
   is back on ^Cannon's 120mm shell, fireball and the turret1.aud report.)
  B4  sgmissile.png   drone rocket: 32 facings, 12x12 (replaces DRAGON).
      sgexhaust.png   its exhaust puff, 3 frames, 8x8 (Missile TrailImage).
  B5  sgpips.png      drone uplink status pips: uplink / degraded / offline,
                      7x7 truecolor (WithDecoration on the chrome palette).
  B6  sgdrohusk.png   shot-down Recon Drone, 32 facings x 1, 32x30.
      sgdrshusk.png   shot-down Strike Drone, 32 facings x 1, 36x32.
      sgdronecrash.png the ground impact, 8 frames, 28x28: dust and a spark
                      burst, no fire (`drone_crash` in `explosion`).
      sghausmoke.png  the Hauler husk's smoke plume, 8 frames, 34x28
                      (WithIdleOverlay, replaces ^Husk's `fire`).
  B8  sgdischarge.png the discharge death every infantryman plays when an
                      arc weapon kills him, 14 frames, 20x26 (replaces the
                      Tesla-blue electro.tem skeleton in `die6`).
  (B2's cameos for the renamed stock actors were withdrawn in issue #123:
   a cameo changes only when its actor's in-world art does, so those seven
   are back on their stock .shp cameos.)

Palette notes. Projectiles, muzzle flashes and explosions render on the
`effect` palette; it is the same temperat.pal file as `player` but is not
remapped, so the 80-95 ramp is plain khaki there and nothing below touches
it (fx_index() searches the fixed entries only, like gen_concept_art's
_BODY_IDX). Index 4 is ShadowIndex on both and is never used as a colour.
The husks and the smoke overlay render on `player`, so their team-colour
marks go through to_indexed()'s remap routing like any unit sheet.

Usage:
    pip install pillow
    python3 gen_unit_effects.py
Writes the sheets next to this file (mods/sungrid/bits/).
"""
import math
import os

from PIL import Image

from gen_concept_art import (
    SS, SD, PC, PLAYER_PAL, _BODY_IDX, _d2, TRANSPARENT_IDX, SHADOW_IDX,
    GREEN_PRIMARY, GREEN_ACCENT, PANEL_BLUEBLACK, SUN_GOLD,
    LEGACY_GRAY, LEGACY_GRAY_DARK, RUST, DAMAGE_SCORCH, POLE_DARK, CONCRETE,
    PALE_STEEL, STEEL, AMBER,
    lit, dim, mix, sphere,
    rotated_frames, sheet_of, sheet_of_indexed, indexed_strip,
    silhouette_shadow, save_pngsheet, canvas,
    _drone_boom, DRONE_SPIN_FRAMES,
    DISR_W, DISR_H, DISR_CX, DISR_GROUND,
)

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# Effect-palette indices (temperat.pal, fixed entries only)
# ---------------------------------------------------------------------------

FX_WHITE = 15          # (252,252,252)
FX_BLUEWHITE = 160     # (224,228,244) -- the exhaust's cold core
FX_ARC = 144           # (196,228,132) pale green, the arczap halo tone
FX_GREEN = 145         # (176,208,124)
FX_GREEN_MID = 147     # (136,172,108)
FX_GREEN_DEEP = 150    # (88,116,76)
FX_GOLD_LIT = 210      # (244,196,112)
FX_GOLD = 212          # (232,160,64)
FX_GOLD_DRK = 213      # (228,144,40)
FX_AMBER = 159         # (252,136,0)
FX_GREY_LT = 227       # (196,196,196)
FX_GREY = 133          # (160,160,160)
FX_GREY_MID = 69       # (148,148,132) warm smoke
FX_GREY_DK = 49        # (120,116,116)
FX_GREY_DEEP = 139     # (92,92,92)
FX_SOOT = 24           # (44,52,52)
FX_BLACK = 143         # (20,20,20)

_FX_CACHE = {}


def fx_index(rgb):
    """Nearest fixed palette entry -- no remap routing, no shadow index."""
    hit = _FX_CACHE.get(rgb)
    if hit is None:
        hit = min(_BODY_IDX, key=lambda i: _d2(rgb, PLAYER_PAL[i]))
        _FX_CACHE[rgb] = hit
    return hit


def fx_strip(frames, w, h):
    """RGBA frames -> one indexed strip on the fixed palette entries. 1-bit
    alpha at 128, same threshold as to_indexed()."""
    sheet = Image.new("P", (w * len(frames), h), TRANSPARENT_IDX)
    flat = []
    for c in PLAYER_PAL:
        flat += list(c)
    sheet.putpalette(flat)
    dst = sheet.load()
    for i, f in enumerate(frames):
        src = f.convert("RGBA").load()
        for y in range(h):
            for x in range(w):
                r, g, b, a = src[x, y]
                if a >= 128:
                    dst[i * w + x, y] = fx_index((r, g, b))
    return sheet


def fx_save(sheet, name, w, h, n):
    """save_pngsheet with the sheet already indexed: it passes P-mode images
    through untouched, which is what keeps the fixed-entry choice above."""
    save_pngsheet(sheet, name, w, h, n, indexed=True)


# RGB stand-ins for the SD (supersampled, RGBA) drawings; fx_strip snaps each
# to the entries above after the downscale.
C_WHITE = PLAYER_PAL[FX_WHITE]
C_BLUEWHITE = PLAYER_PAL[FX_BLUEWHITE]
C_ARC = PLAYER_PAL[FX_ARC]
C_GREEN = PLAYER_PAL[FX_GREEN]
C_GREEN_MID = PLAYER_PAL[FX_GREEN_MID]
C_GOLD_LIT = PLAYER_PAL[FX_GOLD_LIT]
C_GOLD = PLAYER_PAL[FX_GOLD]
C_GOLD_DRK = PLAYER_PAL[FX_GOLD_DRK]
C_GREY_LT = PLAYER_PAL[FX_GREY_LT]
C_GREY = PLAYER_PAL[FX_GREY]
C_GREY_MID = PLAYER_PAL[FX_GREY_MID]
C_GREY_DK = PLAYER_PAL[FX_GREY_DK]
C_SOOT = PLAYER_PAL[FX_SOOT]


# ---------------------------------------------------------------------------
# Shared scatter hash (deterministic, so regeneration is byte-identical).
# ---------------------------------------------------------------------------

def _hash(x, y, salt=0):
    return ((x * 73856093) ^ (y * 19349663) ^ (salt * 83492791)) & 0xFFFF


# ---------------------------------------------------------------------------
# B4. Drone rocket and exhaust
# ---------------------------------------------------------------------------

MISSILE_W, MISSILE_H = 12, 12
MISSILE_FACINGS = 32


def missile_draw(sd, w, h):
    """A slim white rocket, nose up: pale body, dark nose cone, a green fin
    band at the tail, four stub fins. 2px wide so it stays a rocket rather
    than a line at 1x, and no readability outline (projectiles in this mod
    are drawn without one, like the stock DRAGON)."""
    cx, cy = w / 2, h / 2
    sd.rect([cx - 1.0, cy - 2.6, cx + 1.0, cy + 3.4], fill=PALE_STEEL)
    sd.line([(cx - 1.0, cy - 2.6), (cx - 1.0, cy + 3.4)], fill=lit(PALE_STEEL, 0.3), width=0.5)
    sd.poly([(cx, cy - 4.6), (cx + 1.0, cy - 2.4), (cx - 1.0, cy - 2.4)], fill=LEGACY_GRAY_DARK)
    sd.rect([cx - 1.0, cy + 1.4, cx + 1.0, cy + 2.4], fill=GREEN_ACCENT)
    for dx in (-1.9, 1.9):
        sd.poly([(cx + dx * 0.5, cy + 2.4), (cx + dx, cy + 4.0), (cx + dx * 0.5, cy + 4.0)],
                fill=LEGACY_GRAY_DARK)
    sd.rect([cx - 0.6, cy + 3.4, cx + 0.6, cy + 4.2], fill=LEGACY_GRAY_DARK)


def missile_frames():
    return rotated_frames(missile_draw, MISSILE_W, MISSILE_H, n=MISSILE_FACINGS, outlined=False)


EXHAUST_W, EXHAUST_H = 8, 8
EXHAUST_FRAMES = 3


def exhaust_draw(sd, w, h, k=0):
    """Exhaust puff: a blue-white core that opens into a pale grey ring and
    then a few motes. Spawned every two ticks behind the rocket, so three
    40ms frames is the whole life of one puff."""
    cx, cy = w / 2, h / 2
    if k == 0:
        sd.ellipse([cx - 1.6, cy - 1.6, cx + 1.6, cy + 1.6], fill=C_BLUEWHITE)
        sd.px(cx - 0.5, cy - 0.5, C_WHITE)
    elif k == 1:
        sd.ellipse([cx - 2.4, cy - 2.4, cx + 2.4, cy + 2.4], outline=C_GREY_LT, width=1.0)
        sd.px(cx - 0.5, cy - 0.5, C_BLUEWHITE)
    else:
        for dx, dy in ((-2, -2), (2, -1), (-1, 2), (2, 2)):
            sd.px(cx + dx - 0.5, cy + dy - 0.5, C_GREY)


def exhaust_frames():
    out = []
    for k in range(EXHAUST_FRAMES):
        img = Image.new("RGBA", (EXHAUST_W * SS, EXHAUST_H * SS), (0, 0, 0, 0))
        exhaust_draw(SD(img), EXHAUST_W, EXHAUST_H, k=k)
        out.append(img.resize((EXHAUST_W, EXHAUST_H), Image.LANCZOS))
    return out


# ---------------------------------------------------------------------------
# B5. Drone uplink pips (truecolor, chrome palette)
# ---------------------------------------------------------------------------

PIP_W, PIP_H = 7, 7
PIP_STATES = (
    ("uplink", GREEN_ACCENT),            # drone-uplink: full output
    ("degraded", AMBER),                 # drone-uplink-degraded: grid strained
    ("offline", (0xC7, 0x3B, 0x2E)),     # neither: no power, armament disabled
)


def pip_image(col):
    """A 7x7 lamp: dark rim, filled disc, one lit pixel. Decorations are
    screen-space sprites on the chrome palette, so this is plain RGBA."""
    img = Image.new("RGBA", (PIP_W * SS, PIP_H * SS), (0, 0, 0, 0))
    sd = SD(img)
    sd.ellipse([0.5, 0.5, PIP_W - 0.5, PIP_H - 0.5], fill=PANEL_BLUEBLACK)
    sd.ellipse([1.5, 1.5, PIP_W - 1.5, PIP_H - 1.5], fill=col)
    sd.px(2, 2, lit(col, 0.5))
    return img.resize((PIP_W, PIP_H), Image.LANCZOS)


# ---------------------------------------------------------------------------
# B6. Shot-down drones, the crash, the Hauler husk's smoke
# ---------------------------------------------------------------------------

def _dead_rotor(sd, cx, cy, r, ang, tint=(0xA8, 0xA8, 0x9C)):
    """A stopped two-blade rotor: no ring, no leading-edge highlight, just the
    blade at a fixed angle -- the swept ring is what said 'turning'."""
    a = math.radians(ang)
    dx, dy = r * 0.95 * math.cos(a), -r * 0.95 * math.sin(a)
    sd.line([(cx - dx, cy - dy), (cx + dx, cy + dy)], fill=dim(tint, 0.3), width=0.8)
    sd.px(cx - 0.5, cy - 0.5, LEGACY_GRAY_DARK)


def _soot(sd, spots):
    for x, y in spots:
        sd.px(x, y, DAMAGE_SCORCH)


def sgdro_husk_draw(sd, w, h):
    """The Recon Drone after the hit: three rotors stopped, the fourth boom
    snapped short with its rotor gone, the airframe scorched, the nav strip
    still the owner's colour so the wreck is still legible as theirs. Same
    frame size and silhouette family as sgdro_body_draw, so the live-to-husk
    swap at the moment of death never pops in size."""
    cx, cy = w // 2, h // 2
    arms = ((-1, -1), (1, -1), (-1, 1), (1, 1))
    char = mix(dim(GREEN_PRIMARY, 0.45), DAMAGE_SCORCH, 0.35)
    for k, (dx, dy) in enumerate(arms):
        if k == 1:
            # Snapped boom: a short stub with a bent tip.
            _drone_boom(sd, cx, cy, cx + dx * 3.0, cy + dy * 2.2, LEGACY_GRAY_DARK, 1.0)
            sd.line([(cx + dx * 3.0, cy + dy * 2.2), (cx + dx * 3.8, cy + dy * 0.9)],
                    fill=dim(LEGACY_GRAY_DARK, 0.2), width=0.9)
        else:
            _drone_boom(sd, cx, cy, cx + dx * 5.6, cy + dy * 4.0, LEGACY_GRAY_DARK, 1.0)
    for k, (dx, dy) in enumerate(arms):
        if k == 1:
            continue
        _dead_rotor(sd, cx + dx * 5.6, cy + dy * 4.0, 2.2, ang=20 + 55 * k)
    sd.poly([(cx, cy - 5.4), (cx + 2.8, cy - 2.0), (cx + 2.6, cy + 3.0), (cx, cy + 5.2),
             (cx - 2.6, cy + 3.0), (cx - 2.8, cy - 2.0)], fill=dim(char, 0.3))
    sd.poly([(cx, cy - 4.4), (cx + 2.0, cy - 1.6), (cx + 1.6, cy + 2.0), (cx, cy + 3.4),
             (cx - 1.9, cy + 2.0), (cx - 2.2, cy - 1.6)], fill=char)
    sd.poly([(cx - 0.2, cy - 3.6), (cx + 1.0, cy - 1.6), (cx - 0.4, cy + 1.4), (cx - 1.7, cy - 1.4)],
            fill=lit(char, 0.18))
    # Gimbal gone dark; a torn panel over it.
    sphere(sd, cx - 1.4, cy - 2.2, cx + 1.4, cy + 0.6, dim(LEGACY_GRAY, 0.4), steps=3, lit_f=0.2)
    _soot(sd, [(cx + 1, cy - 1), (cx - 2, cy + 1), (cx + 2, cy + 2)])
    sd.rect([cx - 0.8, cy + 3.0, cx + 0.8, cy + 4.4], fill=SUN_GOLD)


def sgdrs_husk_draw(sd, w, h):
    """The Strike Drone after the hit: rotors stopped, one rear boom bent
    double, one munition rail empty, hull scorched; tail flash kept on the
    remap ramp. Frame size and family as sgdrs_body_draw."""
    cx, cy = w // 2, h // 2
    arms = ((-1, -1), (1, -1), (-1, 1), (1, 1))
    char = mix(PANEL_BLUEBLACK, DAMAGE_SCORCH, 0.4)
    for k, (dx, dy) in enumerate(arms):
        if k == 2:
            # Bent boom: out, then folded back toward the hull.
            _drone_boom(sd, cx, cy, cx + dx * 4.6, cy + dy * 3.4, LEGACY_GRAY_DARK, 1.2)
            sd.line([(cx + dx * 4.6, cy + dy * 3.4), (cx + dx * 3.2, cy + dy * 5.6)],
                    fill=dim(LEGACY_GRAY_DARK, 0.2), width=1.0)
        else:
            _drone_boom(sd, cx, cy, cx + dx * 6.6, cy + dy * 4.8, LEGACY_GRAY_DARK, 1.2)
        if dy == -1 and dx == -1:
            # The one rail still loaded; the other was fired or torn away.
            mx, my = cx + dx * 4.2, cy + dy * 3.0
            sd.poly([(mx - 1.0, my - 1.4), (mx + 1.0, my - 1.4), (mx + 1.0, my + 1.6),
                     (mx, my + 2.5), (mx - 1.0, my + 1.6)], fill=dim(PANEL_BLUEBLACK, 0.18))
    for k, (dx, dy) in enumerate(arms):
        if k == 2:
            _dead_rotor(sd, cx + dx * 3.2, cy + dy * 5.6, 2.0, ang=70)
        else:
            _dead_rotor(sd, cx + dx * 6.6, cy + dy * 4.8, 2.5, ang=10 + 50 * k)
    sd.poly([(cx, cy - 6.0), (cx + 3.4, cy - 2.6), (cx + 3.2, cy + 3.6), (cx, cy + 5.8),
             (cx - 3.2, cy + 3.6), (cx - 3.4, cy - 2.6)], fill=dim(char, 0.3))
    sd.poly([(cx, cy - 5.0), (cx + 2.5, cy - 2.2), (cx + 2.1, cy + 2.6), (cx, cy + 4.0),
             (cx - 2.2, cy + 2.6), (cx - 2.6, cy - 2.2)], fill=char)
    sd.poly([(cx - 0.2, cy - 4.2), (cx + 1.3, cy - 2.2), (cx - 0.4, cy + 1.2), (cx - 1.9, cy - 1.8)],
            fill=lit(char, 0.22))
    sphere(sd, cx - 1.6, cy - 0.6, cx + 1.6, cy + 2.6, dim(LEGACY_GRAY, 0.45), steps=3, lit_f=0.2)
    _soot(sd, [(cx + 1, cy - 3), (cx - 2, cy), (cx + 2, cy + 1), (cx, cy - 1)])
    sd.poly([(cx - 1.1, cy + 3.8), (cx + 1.1, cy + 3.8), (cx, cy + 5.4)], fill=SUN_GOLD)


def husk_frames(draw_fn, w, h):
    return rotated_frames(draw_fn, w, h, n=32, outlined=True)


CRASH_W, CRASH_H = 28, 28
CRASH_FRAMES = 8


def crash_draw(sd, w, h, k=0):
    """The ground impact of a falling drone: a spark burst at the hit, a dust
    and smoke cloud that rises and thins, no flame. The sparks are the
    electrical cue (a battery pack letting go), the dust is the weight."""
    cx, cy = w / 2, h / 2 + 4
    # Dust and smoke: a few overlapping puffs rising and spreading.
    rise = 1.4 * k
    spread = 1.0 + 0.55 * k
    puffs = ((0.0, 0.0, 3.2), (-2.4, -1.2, 2.4), (2.6, -0.8, 2.6), (-1.0, -2.8, 2.0), (1.6, -2.4, 2.2))
    if k <= 6:
        for i, (px, py, pr) in enumerate(puffs):
            if k < 1 and i > 2:
                continue
            r = pr * (0.55 + 0.1 * k) * (1.0 if k < 6 else 0.7)
            x = cx + px * spread
            y = cy + py * (1.0 + 0.3 * k) - rise
            tone = (C_GREY_MID, C_GREY_DK, C_GREY, C_GREY_DK, C_GREY_MID)[(i + k) % 5]
            if k >= 4:
                tone = C_GREY_DK if i % 2 else C_GREY_MID
            sd.ellipse([x - r, y - r * 0.8, x + r, y + r * 0.8], fill=tone)
            sd.ellipse([x - r * 0.5, y - r * 0.6, x + r * 0.3, y - r * 0.1], fill=lit(tone, 0.1))
    # Thinning tail: loose motes once the cloud has mostly gone.
    if k >= 5:
        for i in range(6 - (k - 5) * 2):
            sd.px(cx - 5 + i * 2.2 + (k % 2), cy - rise - 3 - (i % 3), C_GREY_MID)
    # Scorch where it hit, under everything from frame 1 on.
    if k >= 1:
        sd.ellipse([cx - 4.0, cy + 1.0, cx + 4.0, cy + 3.8], fill=C_SOOT)
    # Spark burst, frames 0-3.
    if k <= 3:
        n = (10, 8, 5, 2)[k]
        for i in range(n):
            ang = math.radians(i * 360 / n + 17 * k)
            d = 2.5 + 2.2 * k + (_hash(i, k, 7) % 3) * 0.6
            sx, sy = cx + d * math.cos(ang), cy + 1 + d * math.sin(ang) * 0.6 - 1.2 * k
            col = (C_ARC, C_WHITE, C_GOLD_LIT, C_GREEN)[_hash(i, k, 3) % 4]
            sd.px(sx - 0.5, sy - 0.5, col)
        if k == 0:
            sd.ellipse([cx - 2.0, cy - 0.4, cx + 2.0, cy + 2.4], fill=C_WHITE)
            sd.ellipse([cx - 3.2, cy - 1.2, cx + 3.2, cy + 3.2], outline=C_ARC, width=0.9)


def crash_frames():
    out = []
    for k in range(CRASH_FRAMES):
        img = Image.new("RGBA", (CRASH_W * SS, CRASH_H * SS), (0, 0, 0, 0))
        crash_draw(SD(img), CRASH_W, CRASH_H, k=k)
        out.append(img.resize((CRASH_W, CRASH_H), Image.LANCZOS))
    return out


SMOKE_W, SMOKE_H = 34, 28     # SGHAU's frame size
SMOKE_FRAMES = 8


def smoke_draw(sd, w, h, k=0):
    """Looping smoke plume off a wreck: three puffs on a slow upward drift,
    each born at the hull, rising and thinning, with an ember that flickers
    at the base. Greys only -- the husk no longer burns, it smoulders."""
    cx, cy = w / 2, h / 2
    for i in range(3):
        # Each puff is one third of a cycle behind the last.
        phase = ((k + i * (SMOKE_FRAMES / 3)) % SMOKE_FRAMES) / SMOKE_FRAMES
        y = cy - 1 - 9.0 * phase
        x = cx + 1.0 + 2.4 * math.sin(phase * math.pi * 2 + i)
        r = 1.8 + 2.2 * phase
        if phase > 0.85:
            continue
        tone = (C_GREY_DK, C_GREY_MID, C_GREY)[i]
        sd.ellipse([x - r, y - r * 0.8, x + r, y + r * 0.8], fill=tone)
        sd.ellipse([x - r * 0.5, y - r * 0.6, x + r * 0.2, y - r * 0.1], fill=lit(tone, 0.12))
    if k % 3 != 2:
        sd.px(cx - 1, cy + 1, RUST if k % 2 else lit(RUST, 0.35))


def smoke_frames():
    out = []
    for k in range(SMOKE_FRAMES):
        img = Image.new("RGBA", (SMOKE_W * SS, SMOKE_H * SS), (0, 0, 0, 0))
        smoke_draw(SD(img), SMOKE_W, SMOKE_H, k=k)
        out.append(img.resize((SMOKE_W, SMOKE_H), Image.LANCZOS))
    return out


# ---------------------------------------------------------------------------
# B8. The discharge death (indexed, player palette, authored on the PC grid
# like the infantry art)
# ---------------------------------------------------------------------------

DIS_FLICKER = 6        # the lit-skeleton frames; the sequence plays them twice
DIS_FALL = 8           # then the collapse and dissolve
DIS_FRAMES = DIS_FLICKER + DIS_FALL

D_WHITE, D_ARC, D_GREEN, D_GREEN_MID, D_SOOT, D_BLACK = 15, 144, 145, 147, 24, 143


def _skeleton(c, cx, ground, lean=0.0, scale=1.0, bright=True):
    """A generic lit figure, 14 rows tall like every stock infantryman: skull,
    spine, rib bars, arms thrown out, legs. Nothing unit-specific -- the same
    frames serve a rifleman and a Disruptor Trooper, as electro.tem did."""
    core = D_WHITE if bright else D_ARC
    edge = D_ARC if bright else D_GREEN
    top = ground - 14 * scale
    hx = cx + lean * 3
    # Skull
    c.blob(hx, top + 1.5, 1.6, 1.5, core)
    c.set(hx - 1, top + 2, edge)
    c.set(hx + 1, top + 2, edge)
    # Spine and ribs
    for i in range(4, 11):
        y = top + i * scale
        x = cx + lean * (10 - i) * 0.3
        c.set(x, y, core)
        if i in (5, 6, 7):
            wdt = 2 if i == 6 else 1
            c.set(x - wdt, y, edge)
            c.set(x + wdt, y, edge)
    # Arms thrown out and up
    sh_y = top + 4.5 * scale
    c.ray(cx - 1, sh_y, cx - 5, sh_y - 2.5 + lean, edge)
    c.ray(cx + 1, sh_y, cx + 5, sh_y - 2.5 - lean, edge)
    c.set(cx - 5, sh_y - 3 + lean, core)
    c.set(cx + 5, sh_y - 3 - lean, core)
    # Legs
    hip = top + 10.5 * scale
    c.ray(cx, hip, cx - 2, ground, edge)
    c.ray(cx, hip, cx + 2, ground, edge)
    c.set(cx - 2, ground, core)
    c.set(cx + 2, ground, core)


def _arc_sparks(c, cx, ground, k, n=5, spread=6):
    for i in range(n):
        hx = _hash(i, k, 11)
        x = cx + (hx % (spread * 2 + 1)) - spread
        y = ground - 1 - (hx >> 4) % 14
        if (hx >> 8) % 3 == 0:
            continue
        c.set(x, y, D_WHITE if (hx >> 10) % 2 else D_ARC)
        if (hx >> 12) % 2:
            c.set(x + 1, y + ((hx >> 13) % 3 - 1), D_GREEN)


def discharge_frame(k):
    """Frames 0-5: the figure lit from within, white and green alternating,
    arcs crawling over it. Frames 6-13: it folds to the ground and dissolves
    into motes, leaving a small scorch."""
    c = PC(DISR_W, DISR_H)
    cx, ground = DISR_CX, DISR_GROUND
    if k < DIS_FLICKER:
        bright = k % 2 == 0
        lean = (0.0, 0.3, -0.3, 0.5, -0.4, 0.2)[k]
        _skeleton(c, cx, ground, lean=lean, bright=bright)
        _arc_sparks(c, cx, ground, k, n=6 if bright else 4)
        # Ground flash under the boots on the bright frames.
        if bright:
            c.hline(cx - 3, cx + 3, ground + 1, D_GREEN)
        return c
    j = k - DIS_FLICKER                       # 0..7
    t = j / (DIS_FALL - 1)
    # Scorch grows in as the body goes down, then stays.
    sw = 2 + round(3 * min(1.0, t * 1.5))
    c.hline(cx - sw, cx + sw, ground + 1, D_SOOT)
    c.hline(cx - sw + 2, cx + sw - 2, ground, D_BLACK)
    if t <= 0.5:
        # Collapse: the figure shrinks toward the ground and leans over.
        scale = 1.0 - t * 1.2
        _skeleton(c, cx, ground, lean=t * 2.0, scale=max(0.35, scale), bright=False)
        _arc_sparks(c, cx, ground, k, n=3, spread=4)
    else:
        # Dissolve: a heap of motes thinning out.
        keep = 1.0 - (t - 0.5) * 2
        heap = PC(DISR_W, DISR_H)
        for y in range(ground - 3, ground + 1):
            for x in range(cx - 4, cx + 5):
                if _hash(x, y, 5) % 5 < 3:
                    heap.set(x, y, D_GREEN if _hash(x, y, 6) % 3 else D_ARC)
        heap.dissolve(keep)
        for y in range(DISR_H):
            for x in range(DISR_W):
                if heap.px[y][x]:
                    c.set(x, y, heap.px[y][x])
        for i in range(max(0, 3 - j // 2)):
            c.set(cx - 3 + i * 3, ground - 5 - j + i, D_GREEN_MID)
    return c


# ---------------------------------------------------------------------------

def main():
    # B4
    missile = missile_frames()
    fx_save(fx_strip(missile, MISSILE_W, MISSILE_H), "sgmissile.png", MISSILE_W, MISSILE_H, len(missile))
    exhaust = exhaust_frames()
    fx_save(fx_strip(exhaust, EXHAUST_W, EXHAUST_H), "sgexhaust.png", EXHAUST_W, EXHAUST_H, len(exhaust))
    # B5
    pips = [pip_image(col) for _, col in PIP_STATES]
    save_pngsheet(sheet_of(pips, PIP_W, PIP_H), "sgpips.png", PIP_W, PIP_H, len(pips))
    # B6
    for name, fn, w, h in (("sgdrohusk", sgdro_husk_draw, 32, 30), ("sgdrshusk", sgdrs_husk_draw, 36, 32)):
        frames = husk_frames(fn, w, h)
        assert len(frames) == 32
        save_pngsheet(sheet_of(frames, w, h), f"{name}.png", w, h, len(frames), indexed=True)
    crash = crash_frames()
    fx_save(fx_strip(crash, CRASH_W, CRASH_H), "sgdronecrash.png", CRASH_W, CRASH_H, len(crash))
    smoke = smoke_frames()
    save_pngsheet(sheet_of(smoke, SMOKE_W, SMOKE_H), "sghausmoke.png", SMOKE_W, SMOKE_H, len(smoke), indexed=True)
    # B8
    dis = [discharge_frame(k) for k in range(DIS_FRAMES)]
    save_pngsheet(sheet_of_indexed(dis, DISR_W, DISR_H), "sgdischarge.png", DISR_W, DISR_H, len(dis), indexed=True)
    print("done")


if __name__ == "__main__":
    main()
