# Programmatic chrome art in this folder — read before touching these files

Everything thematic in this folder (`dialog.png`, `sidebar.png`, `loadscreen*.png`) plus the
mod icons one level up (`../icon.png`, `../icon-2x.png`, `../icon-3x.png`) is **generated from
scratch by `gen_chrome.py`** — original programmatic art in the locked palette
(`docs/ART_DIRECTION.md`), containing zero pixels derived from stock OpenRA/RA chrome.

This replaced the earlier first-pass reskin (`docs/BACKLOG.md` issue #13), which hue-shifted
the stock RA art in place and so still visually read as recolored OpenRA. That pass's script
(`reskin_chrome.py`) is deleted; the full redesign is `docs/BACKLOG.md` issue #41.

Status: **good first-pass identity work, still not a human-designer pass.** It's clean
geometric rendering, not hand-crafted art — a real designer pass over the chrome and the
emblem remains open follow-up, same status as the programmatic sprite set in
`mods/sungrid/bits/gen_concept_art.py`.

## File-by-file

| File | Contents |
|---|---|
| `dialog.png` (1024×512) | Dialog background + border strips/corners, every button/checkbox/scrollpanel state block, tooltip panel, black tile, main-menu border frame |
| `sidebar.png` (512×512) | Command bar, faction moneybin strips, production tab row, sidebar body with icon-slot/support-power recesses, all 13 sidebar button state blocks, both 222×222 radar-placeholder emblem panels |
| `loadscreen.png` / `-2x` / `-3x` (512×256 / 1024×512 / 2048×1024) | Emblem badge (the `logos` region) + tileable stripe. The "3x" file is actually 4x scale — filename inherited from stock, predates this repo |
| `glyphs.png` / `glyphs-2x.png` / `glyphs-3x.png` | **Untouched stock** — bitmap font atlas + small functional glyphs (order/production/stance icons etc.), not thematic art. Redesigning these is open follow-up |
| `../icon*.png` (32/64/96) | Window/taskbar/mod-chooser icon — the emblem on transparency |

## Hard constraints if you touch any of this

1. **Never change a canvas size and never move content within it.** `mods/sungrid/chrome.yaml`
   addresses every band, button block, and emblem panel by absolute pixel rect
   (`Regions:`/`PanelRegion:`). All of those rects are re-derived from `chrome.yaml` and
   hard-coded in `gen_chrome.py` — that script is the authoritative map of what lives where.
2. Panel center regions are tiled/stretched by the engine — keep them flat or tileable
   (the loadscreen stripe's texture period is chosen to divide its 253px width exactly).
3. `dialog5` (the "completely black tile" at 580,388) must stay pure black.

## How to iterate

Edit `gen_chrome.py` (palette constants at the top, `emblem()` for the mark, per-file
`gen_*` functions) and re-run:

    pip install pillow
    python3 gen_chrome.py

Output depends only on the script, so re-running is always safe. A human designer replacing
this outright can instead paint the PNGs directly — respect the constraints above, then
delete `gen_chrome.py` and this file and update `docs/BACKLOG.md` issue #41.

## What this doesn't cover

Cursors (`cursors.yaml`) and the main-menu shellmap are still stock content
(see `docs/BACKLOG.md` issues #17/#33), and `glyphs*.png` is stock as noted above.
