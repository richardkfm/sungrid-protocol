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

## Asset pipeline (Phase 5 planning note)

Before more than one contributor (human or AI-assisted) produces art, lock: sprite resolution and frame conventions matching OpenRA's existing pixel-art pipeline, a shared base palette file, and a naming/sequence convention consistent with `mods/ra`'s existing structure so new sequences drop into the engine's existing tooling without custom loader work. This is a data/content-pipeline decision, not a code decision — see `docs/ARCHITECTURE.md` friction point #4.

**Priority: Solar Array first.** Solar Array (`POWR`/`APWR`) is the building the mod is named after, so it was the first to get dedicated art rather than the reused vanilla RA power plant sprite — see `docs/BACKLOG.md` issue #12. That first pass shipped as a `PngSheet`-format sprite rather than a hand-authored indexed `.shp`, so it does **not** yet establish the final sprite pipeline baseline this section calls for; it proves the palette/tone direction (solar-panel blues, gold power-conduit accent, green reclaiming the base) but still needs a real artist pass, at which point the indexed-palette/`.shp` pipeline baseline should get set properly. Every other Phase 2/5 building still ships with placeholder/reused stock art.

## Beyond building art: full visual identity (Phase 6/7)

Everything above governs building art specifically. Terrain tilesets, UI chrome (sidebar/build palette/radar frame), cursors, the main menu shell, unit/vehicle/infantry sprites, and audio (announcer voice lines, music) are all still unmodified stock OpenRA/RA assets as of Phase 5 — the single biggest reason the game still visually reads as "reskinned RA" rather than its own project, independent of how distinct the building roster becomes. `docs/ROADMAP.md`'s Phase 6 (world/UI reskin: terrain, chrome, cursors, main menu) and Phase 7 (unit sprites + audio) scope the work to close that gap; the guardrails, palette direction, and readability rules in this document apply equally to that work, not just buildings.

## Phase 6 chrome: first-pass reskin + locked palette (see `docs/BACKLOG.md` issue #13)

A first pass at the Phase 6 chrome deliverable is done: `mods/sungrid/uibits/dialog.png`, `sidebar.png`, and `loadscreen.png`(+`-2x`/`-3x`) are recolored from stock RA's beige/maroon toward this document's palette direction, using the concrete hex values below rather than the palette direction's prose alone. This is a scripted recolor (piecewise hue remap preserving exact canvas dimensions and `chrome.yaml`'s pixel-exact `Regions`/`PanelRegion` rects), not a real artist pass — see `mods/sungrid/uibits/PLACEHOLDER_ART.md` for exactly what's still placeholder and how to replace it. It also does **not** touch cursors or terrain tilesets, which remain out of scope for this pass (see that same file for why).

**Locked palette (hex, sRGB):**

| Role | Hex |
|---|---|
| Living green (primary) | `#2E7D46` |
| Living green (accent) | `#8BC34A` |
| Solar panel blue-black | `#16232E` |
| Sun-gold (active/powered) | `#E8A93D` |
| Alert red/amber | unchanged from stock, per the guardrail above |

**A real finding from doing this pass:** `sidebar.png`'s "no radar built yet" placeholder art and `loadscreen.png` turned out to contain the literal stock Allied chevron and Soviet hammer-and-sickle logos baked into pixel art, not just an unstyled color scheme. Both were replaced with a procedural placeholder emblem rather than left shipping unrelated faction IP while the rest of Phase 6 is still pending — see `PLACEHOLDER_ART.md` for the exact pixel locations if you're doing the real design pass.

## Concept drafts (non-canonical)

`docs/concept-art/phase5-building-dossier.html` is a schematic/silhouette sketch for the 7 Phase 5 buildings — palette and material intent only, not sprite art and not a substitute for the real pixel-art pass this section calls for. Open it directly in a browser. Treat it as a discussion starting point for a human (or dedicated art-pipeline) pass, not as an asset to ship.

`docs/concept-art/phase5-pixel-mockups.html` is a companion pass at the same 7 buildings redrawn as blocky, limited-palette faux pixel art (hard-edged vector cells standing in for pixels). Closer to how the buildings could read at a glance than the schematic dossier, but still not real indexed-palette `.shp` sprites — no animation frames, not exported through OpenRA's actual sprite pipeline. Same non-canonical status applies.
