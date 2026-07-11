# Placeholder art in this folder — read before touching these files

Everything below is **scripted placeholder art**, not final design work. It exists so the
mod stops shipping stock Red Alert branding while a human designer does the real Phase 6
art pass (`docs/WORLD_UI_IDENTITY.md`). Treat every file listed here as "good enough to not
be embarrassing, not good enough to ship."

## Quick answer: what should I replace first?

**`sidebar.png`** and **`loadscreen.png`/`loadscreen-2x.png`/`loadscreen-3x.png`** — specifically
the gold hexagon/sun icon in each. That icon is a stand-in for the **literal stock Allied chevron
and Soviet hammer-and-sickle logos** that used to be baked into this art (see "Why this exists"
below). It's programmer art (drawn with basic shape primitives, not a designer), and it's the
single most visible placeholder in the mod — it's on the sidebar every match and on the loading
screen every launch.

## File-by-file

| File | What changed | Where to look |
|---|---|---|
| `dialog.png` | Recolored maroon panel + swatch grid to the locked green palette | Whole image; no logo/emblem here |
| `sidebar.png` | Recolored red/navy bars; **placeholder emblem drawn over both radar-placeholder regions** | Emblem is at pixel rects `(290,67)-(512,289)` and `(290,290)-(512,512)` in the 512×512 image — these are `chrome.yaml`'s `sidebar-allies`/`sidebar-soviet` `radar:` regions (the "no radar built yet" minimap placeholder) |
| `loadscreen.png` | Recolored panel border; **placeholder emblem drawn over the left half** | Emblem occupies roughly the left 50% width, full height, of the 512×256 image |
| `loadscreen-2x.png` | Same as `loadscreen.png`, scaled 2x (1024×512) | Same relative position, 2x coordinates |
| `loadscreen-3x.png` | Same as `loadscreen.png`, scaled 4x — note the "3x" filename is inherited from stock and is actually a 4x-scale image (2048×1024); don't be surprised by the ratio, it predates this pass | Same relative position, 4x coordinates |
| `glyphs.png` / `glyphs-2x.png` / `glyphs-3x.png` | **Untouched** — this is the bitmap font atlas, not thematic art | N/A |

## Why this exists

While doing the Phase 6 chrome reskin, the stock `sidebar.png` radar-placeholder art and
`loadscreen.png` turned out to contain the actual Allied chevron and Soviet hammer-and-sickle
logos as pixel art — not just an unstyled color scheme, but literal faction IP shipped inside
this mod's own committed assets. That felt like a bigger gap than "needs a palette pass," so it
got replaced immediately with a placeholder rather than left in place until a full art pass.
Full context: `docs/BACKLOG.md` issue #13.

## How to replace the placeholder emblem (or any of this) with real art

1. Open the file in an image editor and paint over it directly. The only hard constraint:
   **keep every file's exact current canvas size** (`dialog.png` 1024×512, `sidebar.png` 512×512,
   `loadscreen.png` 512×256, `-2x` 1024×512, `-3x` 2048×1024). `mods/sungrid/chrome.yaml`'s
   `Regions:`/`PanelRegion:` entries reference pixel coordinates directly, so resizing the canvas
   or shifting content within it will misalign those regions.
2. For the emblem specifically, the exact regions to paint into are listed in the table above —
   you can ignore everything outside them if you only want to replace the logo.
3. If you'd rather tweak parameters and regenerate than hand-paint: edit the constants at the top
   of `reskin_chrome.py` (palette hex values) or the `draw_sungrid_emblem` function (the actual
   shape), then run `pip install pillow numpy && python3 reskin_chrome.py` from this directory.
   Re-running is safe — it's idempotent against its own prior output.
4. Once real art lands, delete `reskin_chrome.py` and this file, and update
   `docs/BACKLOG.md` issue #13 to mark the chrome deliverable done.

## What this doesn't cover

Cursors (`cursors.yaml`) and terrain tilesets (`mods/sungrid/tilesets/*.yaml`) are still
completely stock — they're Westwood `.shp` sprite sheets that need OpenRA's built `utility` tool
to touch, which wasn't available when this placeholder pass was done. See `docs/BACKLOG.md`
issues #13/#14/#16.
