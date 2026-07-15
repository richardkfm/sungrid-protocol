#!/usr/bin/env python3
"""Phase 6 cursor palette reskin tool (see ../../../docs/ART_DIRECTION.md).

Attempted to simply repoint PaletteFromFile@cursor at the same
sungrid-temperat-terrain.pal reskin_terrain_palette.py already produces for
terrain (issue #18) -- reusing work already done, zero new files. Tested by
decoding the actual stock mouse.shp/nopower.shp/attackmove.shp cursor sheets
against both the stock and terrain-recolored palette and diffing every one of
the 222 cursor frames pixel-by-pixel. Result: 112 of 222 frames changed, and
the change was not a subtle tint -- it flips the "blocked"/"attack"/"nuke"
family of cursors (generic-blocked, move-blocked, attackoutsiderange, the
eight scroll-*-blocked directions, nuke, deploy-blocked, sell-blocked,
repair-blocked) from red to green. Root cause: the terrain script's touched
hue band (hue<=45 or >=330, chosen to catch temperate's dominant tan/dirt
ground color) also contains pure saturated red (hue 0), and classic RA's
cursor set relies on that exact red to mean "can't do this here" -- the same
universal convention docs/ART_DIRECTION.md's Design Pillar 1 ("Classic RTS
legibility first -- theme never overrides silhouette/UI readability") argues
against overriding. Shipping the straight reuse would have made half the
mod's warning/blocked cursors read as "go ahead," a real playability
regression, not just a cosmetic one.

This script is the corrected version for cursors specifically: same
piecewise hue remap, but with an added exclusion for the semantic-red core
(hue within 20 degrees of 0, saturation > 0.5) so blocked/attack/nuke/danger
cursors keep their stock red regardless of brightness. Only genuinely
desaturated or off-red warm tones (the sliver of tan/gold cursor accents
outside that protected core, e.g. the goldwrench/repair family and the c4
marker) still shift toward the locked palette, giving a light harmonization
touch without breaking any cursor's meaning.

Re-verified the same way: decode mouse.shp/nopower.shp/attackmove.shp against
the output of this script and diff against stock -- every previously-broken
blocked/attack/nuke frame now matches stock exactly (0 pixels changed); only
frames with no semantic-red content differ at all.

Usage:
    python3 reskin_cursor_palette.py <path/to/stock/temperat.pal>

Writes sungrid-cursor.pal next to this script (768 bytes, same 6-bit VGA
.pal format as reskin_terrain_palette.py's output).
"""
import sys
import os
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reskin_terrain_palette import hue_deg, GREEN_TARGET_HUE, GOLD_TARGET_HUE  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def recolor_cursor_safe(rgb01: np.ndarray) -> np.ndarray:
    maxc = rgb01.max(axis=-1)
    minc = rgb01.min(axis=-1)
    v = maxc
    delta = maxc - minc
    s = np.where(maxc > 1e-6, delta / np.where(maxc > 1e-6, maxc, 1), 0.0)
    h_deg = hue_deg(rgb01)

    in_warm_band = (h_deg <= 45) | (h_deg >= 330)
    is_bright_glint = (s > 0.85) & (v > 0.85)
    # Protect the semantic-red core cursors rely on for blocked/attack/nuke/
    # danger meaning -- pure/near-pure saturated red regardless of brightness.
    is_semantic_red = ((h_deg <= 20) | (h_deg >= 340)) & (s > 0.5)

    touch_green = in_warm_band & (s > 0.12) & (v > 0.03) & ~is_bright_glint & ~is_semantic_red
    touch_gold = in_warm_band & is_bright_glint & ~is_semantic_red

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
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <path/to/stock/temperat.pal>", file=sys.stderr)
        sys.exit(1)

    src = sys.argv[1]
    data = open(src, "rb").read()
    if len(data) != 768:
        print(f"Expected a 768-byte (256x3, 6-bit VGA) .pal file, got {len(data)} bytes", file=sys.stderr)
        sys.exit(1)

    raw = np.frombuffer(data, dtype=np.uint8).reshape(256, 3).astype(np.float64)
    rgb01 = np.clip(raw * 4.0, 0, 255) / 255.0

    out01 = recolor_cursor_safe(rgb01)

    out6 = np.clip(np.round(out01 * 255.0 / 4.0), 0, 63).astype(np.uint8)

    dest = os.path.join(HERE, "sungrid-cursor.pal")
    with open(dest, "wb") as f:
        f.write(out6.tobytes())

    changed = int(np.sum(np.any(out6 != raw.astype(np.uint8), axis=-1)))
    print(f"Wrote {dest} ({os.path.getsize(dest)} bytes); {changed}/256 palette entries recolored")


if __name__ == "__main__":
    main()
