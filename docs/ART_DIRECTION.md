# Sungrid Protocol — Art Direction

## Tone

Lush eco-solarpunk. Renewable power, smart grids, drone logistics, and resilient settlements — hopeful and strategic, not utopian or goofy. This is still a real RTS: the world should look like people building something worth defending, under genuine pressure, not a post-scarcity diorama with no stakes.

## Guardrails

- **Not utopian.** Bases should show wear, improvisation, and defense — sandbags next to solar panels, drone bays bolted onto salvaged structure, not pristine architecture-magazine renders.
- **Not goofy.** No cartoon mascots, no winking irony. The Cryptominer building (morally ambiguous legacy tech repurposed under solar power) is the tone reference: interesting, slightly uneasy, not a joke.
- **Still a Cold-War-adjacent conflict, re-skinned.** Military tension, scouting, raiding, and destruction are real and visible — weapons and defensive structures should read as dangerous, not decorative.

## Readability rules (non-negotiable, ties to Design Pillar 1)

- Every unit and building must have a distinct, readable silhouette at standard RTS zoom — theme never overrides legibility.
- Faction/player color must remain the dominant, unambiguous ownership signal (team-color accents on structures/units), consistent with classic RA-style UI conventions.
- Health/status bars, selection indicators, and UI chrome keep OpenRA's existing conventions until there's a specific, tested reason to deviate — familiarity is a feature for genre-literate players.

## Palette direction

- **Base palette:** greens (living systems, recycling, foliage reclaiming industrial space), warm solar-panel blues/blacks, sun-gold accents for "active/powered" states.
- **Military/industrial counterpoint:** desaturated grays and rust for legacy infrastructure (Cryptominer, salvaged structures) to visually separate "old world tech" from "new grid tech" without needing a second faction yet.
- **Danger/alert states:** reserve existing RTS conventions (red/amber) for low power, under-attack, and Grid Reserve Lockdown countdown states — don't reinvent alert color language.

## Faction visual differentiation (Phase 5+)

Until a second faction is scoped, "faction flavor" means making the single Sungrid Protocol roster visually cohesive and distinct from vanilla RA/Allies/Soviets — not inventing a second full art set. Notes for whenever a second faction is justified: differentiate through material and infrastructure philosophy (e.g. decentralized/drone-based vs. centralized/hardened grid) rather than through tone shifts — both factions should still read as "this world," not swap into a different genre.

## Asset pipeline (locked in Phase 6)

This was deferred through Phase 5 (which shipped on reused/recolored placeholder sprites instead) and is finally locked here as Phase 6's prerequisite deliverable (backlog issue #12), scoped to world/UI art first (terrain, chrome, cursors, menus) rather than unit/building sprites — see `docs/WORLD_UI_IDENTITY.md` for the full spec, deliverables, and exit criteria.

**Palette file** (hex, sRGB — derived from the palette direction above):

| Role | Color | Hex |
|---|---|---|
| Living green (primary) | mid green | `#2E7D46` |
| Living green (shade) | deep green | `#163C28` |
| Living green (accent) | bright leaf | `#8BC34A` |
| Solar panel blue-black | panel base | `#16232E` |
| Sun-gold (active/powered) | accent | `#E8A93D` |
| Legacy/industrial rust | desaturated rust | `#8C5A3C` |
| Legacy/industrial gray | aged gray | `#6E6259` |
| Alert red / amber | **unchanged from stock** — reuse OpenRA's existing low-power/under-attack/Lockdown-countdown colors as-is, per the guardrail above |

**Sprite resolution / frame conventions:**
- Chrome PNGs (`mods/sungrid/uibits/*.png`): canvas dimensions and `Image`/`Image2x`/`Image3x` scale ratios must match the current stock files exactly — `chrome.yaml`'s `Regions`/`PanelRegion` rects are pixel-exact and any resize breaks them.
- Terrain tiles (`mods/sungrid/tilesets/*.yaml`, backed by `.shp`/`.tem`/`.des`/`.sno`/`.int` sprite sheets): match each tileset's existing per-tile pixel dimensions and template geometry; a reskin re-textures, it doesn't reshape tiles or renumber templates.
- Cursors (`mouse.shp`, `attackmove.shp`, `nopower.shp`, referenced by `cursors.yaml`): every existing `Start` frame index and hotspot (`X`/`Y`) must be preserved exactly — a reskin replaces frame art, not frame layout.

**Naming convention:** keep existing lowercase filenames as-is (`dialog.png`, `sidebar.png`, `mouse.shp`, etc.) — `chrome.yaml`/`cursors.yaml`/`mod.yaml` reference these by exact path, so reskins overwrite in place rather than rename.

**Known blocker for this session:** terrain tilesets and cursors are Westwood `.shp`-format sprite sheets, which require OpenRA's own `utility` tool (built from the fetched `engine/`) to decode/encode — there's no standalone SHP codec available outside the built engine. Chrome PNGs (`uibits/*.png`) have no such dependency and can be edited directly. See `docs/WORLD_UI_IDENTITY.md`'s issue-by-issue status for what's actually been executed under this lock versus what's blocked pending a build-capable environment.
