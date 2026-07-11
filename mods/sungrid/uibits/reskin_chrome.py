#!/usr/bin/env python3
"""Phase 6 chrome reskin tool (see ../../../docs/WORLD_UI_IDENTITY.md).

Recolors dialog.png/sidebar.png/loadscreen.png(+2x/3x) toward the locked
Sungrid Protocol palette (docs/ART_DIRECTION.md) and draws a procedural
placeholder emblem over the two spots that used to hold the literal stock
Allied chevron and Soviet hammer-and-sickle logos.

THIS IS PLACEHOLDER ART. See PLACEHOLDER_ART.md in this directory for
exactly what's placeholder, where to find it in each file, and how to
replace it with real designer art.

Geometry-preserving only: canvas sizes and chrome.yaml's pixel-exact
Regions/PanelRegion rects are never touched, only pixel color/content.

Usage:
    pip install pillow numpy
    python3 reskin_chrome.py

Re-running is safe/idempotent: the hue remap only touches the original
stock reddish band, and green pixels from a prior run aren't in that band,
so running twice doesn't double-shift anything. The emblem draw always
paints the same fixed regions, so re-running just redraws the same emblem.
"""
import math
import os
import colorsys
import numpy as np
from PIL import Image, ImageDraw

UIBITS = os.path.dirname(os.path.abspath(__file__))

# Locked palette (docs/ART_DIRECTION.md) -- edit here to change the target
# colors, then re-run.
GREEN_MID = (0x2E, 0x7D, 0x46)
GREEN_ACCENT = (0x8B, 0xC3, 0x4A)
PANEL_BLUEBLACK = (0x16, 0x23, 0x2E)
SUN_GOLD = (0xE8, 0xA9, 0x3D)

GREEN_TARGET_HUE = colorsys.rgb_to_hsv(*[c / 255 for c in GREEN_MID])[0]  # ~0.35


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


def recolor_red_to_green(im: Image.Image) -> Image.Image:
    """Piecewise hue remap: only the reddish stock-RA hue band shifts to the
    green target hue; blues/grays/neutrals are left alone so a blind global
    rotation doesn't wreck unrelated tones (e.g. the soviet navy bar)."""
    had_alpha = "A" in im.getbands()
    rgba = im.convert("RGBA")
    arr = np.asarray(rgba).astype(np.float32) / 255.0
    rgb = arr[..., :3]
    a = arr[..., 3]

    maxc = rgb.max(axis=-1)
    minc = rgb.min(axis=-1)
    v = maxc
    delta = maxc - minc
    s = np.where(maxc > 1e-6, delta / np.where(maxc > 1e-6, maxc, 1), 0.0)
    h_deg = hue_deg(rgb)

    in_red_band = (h_deg <= 25) | (h_deg >= 330)
    touch = in_red_band & (s > 0.12) & (v > 0.03)

    target_h = GREEN_TARGET_HUE * 360.0
    new_h_deg = np.where(touch, target_h, h_deg)
    new_s = np.where(touch, np.clip(s * 1.05, 0, 1), s)
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
    out_rgb = np.stack([r_out, g_out, b_out], axis=-1)
    out = np.concatenate([out_rgb, a[..., None]], axis=-1)
    out = np.clip(out * 255.0, 0, 255).astype(np.uint8)
    result = Image.fromarray(out, mode="RGBA")
    return result if had_alpha else result.convert(im.mode)


def draw_sungrid_emblem(canvas: Image.Image, cx, cy, r, bg=PANEL_BLUEBLACK):
    """PLACEHOLDER emblem: gold hexagon ring + sun core + green leaf band.
    Replaces the literal Allied/Soviet logos found baked into stock chrome.
    A human designer should replace the pixels this draws, not iterate on
    this function -- see PLACEHOLDER_ART.md."""
    draw = ImageDraw.Draw(canvas, "RGBA")
    draw.rectangle((cx - r, cy - r, cx + r, cy + r), fill=bg + (255,))

    hexpts = [(cx + r * 0.82 * math.cos(math.pi / 6 + k * math.pi / 3),
               cy + r * 0.82 * math.sin(math.pi / 6 + k * math.pi / 3)) for k in range(6)]
    draw.polygon(hexpts, outline=SUN_GOLD + (255,), width=int(max(2, r // 40)))

    core_r = r * 0.42
    draw.ellipse((cx - core_r, cy - core_r, cx + core_r, cy + core_r), fill=SUN_GOLD + (255,))

    for k in range(8):
        ang = k * math.pi / 4
        x0, y0 = cx + core_r * 1.15 * math.cos(ang), cy + core_r * 1.15 * math.sin(ang)
        x1, y1 = cx + r * 0.72 * math.cos(ang), cy + r * 0.72 * math.sin(ang)
        draw.line((x0, y0, x1, y1), fill=SUN_GOLD + (255,), width=int(max(2, r // 45)))

    band_top, band_bottom = cy + r * 0.35, cy + r * 0.62
    draw.rectangle((cx - r * 0.7, band_top, cx + r * 0.7, band_bottom), fill=GREEN_MID + (230,))
    draw.line((cx - r * 0.7, (band_top + band_bottom) / 2, cx + r * 0.7, (band_top + band_bottom) / 2),
              fill=GREEN_ACCENT + (255,), width=int(max(1, r // 80)))


def process_dialog():
    p = f"{UIBITS}/dialog.png"
    out = recolor_red_to_green(Image.open(p))
    out.save(p)
    print("dialog.png recolored", out.size, out.mode)


def process_sidebar():
    p = f"{UIBITS}/sidebar.png"
    out = recolor_red_to_green(Image.open(p).convert("RGBA"))
    # radar placeholder regions from mods/sungrid/chrome.yaml (pixel-exact, do not move)
    draw_sungrid_emblem(out, 290 + 111, 67 + 111, 105)   # sidebar-allies radar: 290,67,222,222
    draw_sungrid_emblem(out, 290 + 111, 290 + 111, 105)  # sidebar-soviet radar: 290,290,222,222
    out.save(p)
    print("sidebar.png recolored + emblem placed", out.size, out.mode)


def process_loadscreen():
    for name in ("loadscreen.png", "loadscreen-2x.png", "loadscreen-3x.png"):
        p = f"{UIBITS}/{name}"
        out = recolor_red_to_green(Image.open(p).convert("RGBA"))
        w, h = out.size
        # left half held the stock Soviet star/hammer-sickle logo; right half is the panel
        draw_sungrid_emblem(out, w * 0.25, h * 0.5, h * 0.46)
        out.save(p)
        print(f"{name} recolored + emblem placed", out.size, out.mode)


if __name__ == "__main__":
    process_dialog()
    process_sidebar()
    process_loadscreen()
