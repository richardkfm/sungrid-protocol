#!/usr/bin/env python3
"""Phase 6 terrain palette reskin tool (see ../../../docs/ART_DIRECTION.md).

Recolors the temperate tileset's *terrain*-only palette toward the locked
Sungrid Protocol palette, using the same piecewise hue remap already proven
for the Phase 6 chrome pass (reskin_chrome.py): only the reddish/rust stock
hue band shifts toward the locked green target hue; blues (water), grays
(roads/cliffs/rock), and already-green pixels (grass/foliage) are left alone.

Critical design point, not shared with the chrome pass: classic Westwood-era
palettes are shared across an entire theater. mods/sungrid/rules/palettes.yaml
has SEPARATE named PaletteFromFile entries that today all point at the same
stock temperat.pal -- `terrain` (Tileset: TEMPERAT, used by terrain tiles and
neutral scenery/decorations), `player` (used by unit/building sprites, with
the player-color remap band), `effect` (explosions/muzzle flashes/etc), and
`chrome`/`cursor`. This script only touches a NEW file that `terrain`'s
Filename gets repointed at -- `player`/`effect`/`chrome`/`cursor` keep
loading the original stock temperat.pal unchanged. This is what makes it
safe: recoloring terrain/scenery here cannot bleed into unit, building, or
weapon-effect colors, even though today they all trace back to one file.

THIS IS A FIRST PASS, not a real artist's terrain palette -- see
docs/ART_DIRECTION.md's Phase 6 section. Geometry/tile shapes are never
touched (only the color lookup table changes), so there is no risk of the
cliff/resource-boundary breakage docs/ROADMAP.md's Phase 6 section warns
about from touching individual tile sprites.

Usage:
    pip install pillow numpy
    python3 reskin_terrain_palette.py <path/to/stock/temperat.pal>

Writes sungrid-temperat-terrain.pal next to this script (768 bytes, same
6-bit-per-channel VGA .pal format OpenRA's PaletteFromFile trait expects --
see engine/OpenRA.Game/Graphics/Palette.cs's `reader.ReadByte() << 2`).

Re-running is safe/idempotent for the same reason reskin_chrome.py's is:
the hue remap only touches the original stock reddish band, and green
pixels from a prior run aren't in that band.
"""
import sys
import os
import colorsys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))

# Locked palette (docs/ART_DIRECTION.md) -- same targets reskin_chrome.py uses.
GREEN_MID = (0x2E, 0x7D, 0x46)
SUN_GOLD = (0xE8, 0xA9, 0x3D)
GREEN_TARGET_HUE = colorsys.rgb_to_hsv(*[c / 255 for c in GREEN_MID])[0]  # ~0.35
GOLD_TARGET_HUE = colorsys.rgb_to_hsv(*[c / 255 for c in SUN_GOLD])[0]  # ~0.106


def hue_deg(rgb_arr):
    """rgb_arr: (...,3) float 0-1 -> hue in degrees 0-360"""
    r, g, b = rgb_arr[..., 0], rgb_arr[..., 1], rgb_arr[..., 2]
    maxc = np.max(rgb_arr, axis=-1)
    delta = maxc - np.min(rgb_arr, axis=-1)
    mask = delta > 1e-6
    rc = np.zeros_like(maxc)
    gc = np.zeros_like(maxc)
    bc = np.zeros_like(maxc)
    np.divide(maxc - r, delta, out=rc, where=mask)
    np.divide(maxc - g, delta, out=gc, where=mask)
    np.divide(maxc - b, delta, out=bc, where=mask)
    is_r = mask & (maxc == r)
    is_g = mask & (maxc == g) & ~is_r
    is_b = mask & ~is_r & ~is_g
    h = np.zeros_like(maxc)
    h = np.where(is_r, bc - gc, h)
    h = np.where(is_g, 2.0 + rc - bc, h)
    h = np.where(is_b, 4.0 + gc - rc, h)
    h = (h / 6.0) % 1.0
    return h * 360.0


def recolor_red_to_green(rgb01: np.ndarray, max_recolor_value: float | None = None) -> np.ndarray:
    """Wider than reskin_chrome.py's recolor_red_to_green (which only caught
    stock RA's saturated reddish-maroon UI chrome): terrain's dominant "clear
    ground" color is a desaturated tan/khaki around hue 10-45, well outside
    that narrow band, so a straight port barely changed anything visible
    (verified: 12% of pixels touched, but low-magnitude, imperceptible in a
    rendered sheet). This widens the band to hue<=45 or >=330 to actually
    catch that dominant tan/dirt/rust range plus the rust-cliff/red ramps,
    while carving out the small set of near-pure bright highlights (the
    existing sun-gold glint accents docs/ART_DIRECTION.md's palette wants to
    KEEP distinct from the green base) and nudging those toward the locked
    sun-gold hex instead of green, so terrain still reads as two distinct
    tones (living green ground, gold highlights) rather than a flat green
    wash.

    max_recolor_value: desert's dominant "clear ground" color itself sits in
    this same warm band across a wide range of brightness (unlike temperate/
    snow, where it's a smaller, mostly-darker accent) - even a gradual
    brightness-based taper still visibly washes the whole surface green and
    erases the desert identity, since so much of what reads as "sand" spans
    that range. A hard cutoff (only recolor entries at or below this value)
    proved the only thing that actually preserved "desert with mossy
    crevices" instead of "green field": verified visually via --dump-sheets,
    not just by the entry count. Leave as None (no cutoff) for temperate/snow,
    where the full-strength shift already reads correctly."""
    maxc = rgb01.max(axis=-1)
    minc = rgb01.min(axis=-1)
    v = maxc
    delta = maxc - minc
    s = np.where(maxc > 1e-6, delta / np.where(maxc > 1e-6, maxc, 1), 0.0)
    h_deg = hue_deg(rgb01)

    in_warm_band = (h_deg <= 45) | (h_deg >= 330)
    is_bright_glint = (s > 0.85) & (v > 0.85)  # preserve existing sun-gold highlight accents
    touch_green = in_warm_band & (s > 0.12) & (v > 0.03) & ~is_bright_glint
    if max_recolor_value is not None:
        touch_green = touch_green & (v < max_recolor_value)
    touch_gold = in_warm_band & is_bright_glint

    target_h = GREEN_TARGET_HUE * 360.0
    gold_h = GOLD_TARGET_HUE * 360.0
    new_h_deg = np.where(touch_green, target_h, np.where(touch_gold, gold_h, h_deg))
    new_s = np.where(touch_green, np.clip(s * 1.05, 0, 1), s)
    new_v = v

    h60 = (new_h_deg / 60.0) % 6
    i = np.floor(h60).astype(np.int32)
    f = h60 - i
    p = new_v * (1 - new_s)
    q = new_v * (1 - new_s * f)
    t = new_v * (1 - new_s * (1 - f))

    r_out = np.select([i == 0, i == 1, i == 2, i == 3, i == 4, i == 5],
                       [new_v, q, p, p, t, new_v], default=new_v)
    g_out = np.select([i == 0, i == 1, i == 2, i == 3, i == 4, i == 5],
                       [t, new_v, new_v, q, p, p], default=new_v)
    b_out = np.select([i == 0, i == 1, i == 2, i == 3, i == 4, i == 5],
                       [p, p, t, new_v, new_v, q], default=new_v)
    return np.clip(np.stack([r_out, g_out, b_out], axis=-1), 0, 1)


def main():
    args = list(sys.argv[1:])
    max_value = None
    for a in list(args):
        if a.startswith("--max-value="):
            max_value = float(a.split("=", 1)[1])
            args.remove(a)
    if len(args) not in (1, 2):
        print(f"Usage: {sys.argv[0]} <path/to/stock/tileset.pal> [output-filename] [--max-value=0.5]", file=sys.stderr)
        sys.exit(1)

    src = args[0]
    out_name = args[1] if len(args) == 2 else "sungrid-temperat-terrain.pal"
    data = open(src, "rb").read()
    if len(data) != 768:
        print(f"Expected a 768-byte (256x3, 6-bit VGA) .pal file, got {len(data)} bytes", file=sys.stderr)
        sys.exit(1)

    # Stored as 6-bit-per-channel (0-63); engine widens via << 2 to 0-255 (see Palette.cs).
    raw = np.frombuffer(data, dtype=np.uint8).reshape(256, 3).astype(np.float64)
    rgb01 = np.clip(raw * 4.0, 0, 255) / 255.0

    out01 = recolor_red_to_green(rgb01, max_recolor_value=max_value)

    # Narrow back to 6-bit by matching the engine's own widening (x << 2 == x * 4),
    # so the round trip is exact for untouched entries.
    out6 = np.clip(np.round(out01 * 255.0 / 4.0), 0, 63).astype(np.uint8)

    dest = os.path.join(HERE, out_name)
    with open(dest, "wb") as f:
        f.write(out6.tobytes())

    changed = int(np.sum(np.any(out6 != raw.astype(np.uint8), axis=-1)))
    print(f"Wrote {dest} ({os.path.getsize(dest)} bytes); {changed}/256 palette entries recolored")


if __name__ == "__main__":
    main()
