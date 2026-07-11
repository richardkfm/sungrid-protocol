# Sungrid Protocol — World & UI Visual Identity (Phase 6)

This document specifies Phase 6: **World & UI Visual Identity Overhaul**. It supersedes the diplomacy/shared-resource phase that previously held the "Phase 6" slot in `docs/ROADMAP.md` — that work still exists, still gated the same way, and has moved to **Phase 8+** (with a new Phase 7, sound/music, inserted between the two — see the note at the bottom of this doc). This redefinition happened before Phase 8's gate was met, so it does not pull anything forward; it's a renumbering, not a shortcut.

## Why this phase, why now

Phase 5's exit criteria (`docs/ROADMAP.md`) called for "a distinct visual identity," but the actual Phase 5 delivery (`docs/BACKLOG.md` issue #11, `docs/BUILDINGS.md`'s art note) shipped all 7 remaining buildings on **reused stock sprites** and explicitly deferred "real custom art, a faction-cohesive palette pass, and a sound/music pass" as separate, not-yet-started work. Checking the current mod content confirms the gap is broader than just buildings: `mods/sungrid/tilesets/*.yaml`, `chrome.yaml`, `mod.chrome.yaml`, and `cursors.yaml` are still the stock content ported wholesale in Phase 1 — nothing in the world (terrain) or the UI chrome reads as Sungrid Protocol yet, only the fluent strings and the Phase 3/4 Grid Reserve HUD additions do.

`docs/ART_DIRECTION.md` also left its "Phase 5 planning note" unresolved: before more than one contributor touches art, it calls for locking sprite resolution/frame conventions, a shared palette file, and a naming convention — that lock never happened. Phase 6 is where it finally does, scoped tightly to **world and UI** art (terrain, chrome, cursors, menus) rather than unit/building sprites, which stay out of scope here (see Non-goals).

## Scope

**In scope:**
1. **Terrain** — reskin of the tileset(s) actually used by shipped maps, so the world reads as lush eco-solarpunk per `docs/ART_DIRECTION.md`'s tone/guardrails, not stock Red Alert terrain.
2. **Chrome** — main menu, mod chooser, loading screen, and in-game panel frame/button skinning (`chrome.yaml`, `mod.chrome.yaml`, `chrome/*.yaml`).
3. **Cursors** — a Sungrid Protocol cursor set (`cursors.yaml`), reskinned but functionally identical to stock (same states: select, move, attack, deploy-invalid, etc.).
4. **Menus/shellmap** — the main-menu shellmap background (`maps/desert-shellmap/`) re-themed to a solarpunk vista consistent with the reskinned terrain, since it's the first thing anyone sees.
5. **Asset pipeline lock** — finally resolving `docs/ART_DIRECTION.md`'s deferred Phase 5 planning note: a shared palette reference, sprite resolution/frame conventions, and a naming convention, written down before any of 1–4 starts, so this pass and any future art pass compose instead of drifting.

**Explicit non-goals (deferred, not part of this phase):**
- Unit and building sprite replacement — Phase 5's placeholder/reused sprites stay as-is; this is a separate, later art pass once the pipeline locked here has been validated on a smaller (world/UI) surface first.
- A second faction's visual identity — still blocked on there being a second faction at all (see `docs/ART_DIRECTION.md`).
- Any new gameplay mechanic, trait, or rule change — this phase is visual-only.
- Diplomacy/shared-resource systems — unchanged, still gated, now tracked as Phase 8+ (see bottom of this doc).
- Sound/music pass — named alongside art in Phase 5's original deferred list, but audio is a distinct pipeline (voice/SFX/music direction, not sprites/palettes) and is left for its own future phase (Phase 7) rather than folded in here to keep this phase's scope singular.

## Why terrain/chrome/cursors/menus and not unit/building art

Reskinning the world and the UI chrome touches zero gameplay-critical silhouettes — Design Pillar 1 ("classic RTS legibility first") is about unit/building readability specifically, and that art is untouched here. This makes Phase 6 the lowest-risk place to validate a real asset pipeline: mistakes are visually obvious and easy to iterate on, but a botched terrain tile or cursor state doesn't create the kind of "can't tell what I'm looking at mid-fight" failure that botched unit art would. It's also the largest remaining "still visibly stock RA" surface — terrain and menu chrome are what a player sees for 100% of a match and 100% of the pre-match experience, respectively, more screen-time than any single building.

## Deliverables

### 1. Asset pipeline lock (prerequisite for everything else below)

- **Palette file:** one shared reference (`docs/ART_DIRECTION.md`'s palette direction — greens, solar blues/blacks, sun-gold "powered" accents, desaturated grays/rust for legacy tech, stock red/amber reserved for alert states) turned into concrete hex/index values usable across tilesets, chrome, and cursors.
- **Sprite conventions:** resolution and frame count/timing conventions matching OpenRA's existing pixel-art pipeline (so new tiles/cursors drop into the engine's existing tooling with no loader changes) — confirm against `mods/ra`'s existing tileset/cursor sequence definitions rather than inventing new ones.
- **Naming convention:** tile/cursor/chrome asset names consistent with the existing `mods/sungrid` sequence/YAML key conventions.
- This lock is itself a `type:design` deliverable (an RFC-style doc addition, not art production) — see backlog issue #12 below.

### 2. Terrain

- Start with exactly **one** tileset, not all four (`desert`, `temperat`, `snow`, `interior`) at once. Actual per-map usage today: `SNOW` (`a-nuclear-winter`, `code-19`, `shattered-mountain`, `snow-town` — 4 of 8 shipped maps), `TEMPERAT` (`chernobyl`, `shuriken-island` — 2 of 8), `DESERT` (`desert-rats`, and `desert-shellmap` — the main-menu shellmap itself). `SNOW` covers the most shipped maps; `DESERT` doubles as deliverable 5's shellmap tileset. Recommend `DESERT` first specifically because of that overlap — one reskinned tileset then covers both a played map (`desert-rats`) and the menu shellmap, giving the most visible payoff for a single tileset's worth of work — but this is a call for whoever picks up the issue to confirm, not a hard requirement.
- Approach: palette-shift plus selective re-texture of key tiles (grass/dirt reads as reclaimed green space, ore/gem fields read as recycling/salvage zones) rather than from-scratch tile art for every tile in a ~4,000+ line tileset — full redraws of all four tilesets is exactly the kind of open-ended scope this doc's risk section flags.
- Remaining tilesets stay stock until this one is validated (see Exit criteria) — this is a deliberate single-tileset-first cap, not an oversight.

### 3. Chrome

- Main menu background/theme, mod-chooser tile art, loading screen art, in-game panel frame/button skin.
- Per `docs/ART_DIRECTION.md`: keep existing OpenRA UI conventions (layout, health/status bar behavior, selection indicators) — this phase reskins color/texture/framing, not layout topology. Deviating from stock chrome layout is out of scope; it wasn't tested and isn't needed to read as Sungrid Protocol.
- Must not visually conflict with the already-implemented Grid Reserve HUD elements (`GridReserveHudLogic`, `GridReserveStandingsLogic` in `ingame-player.yaml`/`ingame-observer.yaml`) — those were positioned against stock chrome art; verify they still read cleanly against the new skin.

### 4. Cursors

- Reskin `cursors.yaml`'s existing cursor set to the new palette/style.
- Every existing cursor **state** (select, move, move-blocked, attack, attack-outside-range, deploy/invalid, guard, enter, etc.) must remain present and functionally distinguishable — this is a straight reskin of an existing, already-legible set, not a redesign of what states exist or what they mean.

### 5. Menu shellmap

- Re-theme `maps/desert-shellmap/` (or replace it with a purpose-built shellmap) so the main menu's background reads as a lush solarpunk vista consistent with the reskinned terrain from deliverable 2.

## Code scope

None expected. Everything above is sequences, palette/tileset YAML, `ChromeLayout` YAML, and cursor YAML — all data/content per `docs/ARCHITECTURE.md`'s data-driven-first default. If reskinning surfaces something that genuinely can't be expressed as data (e.g. a chrome layout limitation), that's a stop-and-flag moment for a future RFC, not something to route around with a new trait mid-phase.

## Testing scope

- Manual visual review: mod chooser, main menu, loading screen, the one reskinned tileset in-game, cursor states exercised in a skirmish (select/move/attack/deploy/guard/enter).
- Regression check: Grid Reserve HUD (Phase 3/4) and existing unit/building sprites still render correctly and legibly against the new chrome/terrain palette — this phase must not regress Design Pillar 1 legibility even though it doesn't touch unit/building art directly (a terrain palette shift can still wash out unit silhouettes if contrast isn't checked).
- No automated testing applies here beyond the existing CI build/YAML-parse check — this is a visual/content phase.

## Exit criteria

- The asset pipeline (palette, sprite conventions, naming convention) is written down and referenced from `docs/ART_DIRECTION.md`.
- Main menu, mod chooser, and loading screen visually read as Sungrid Protocol, not stock Red Alert.
- At least one tileset is fully re-paletted/re-textured per the locked pipeline and confirmed playable/legible in a full skirmish.
- The cursor set is fully replaced with no missing/misread states.
- The shellmap reads as a solarpunk vista.
- No legibility regression reported in the manual playtest above.

## Biggest risk

Same shape as Phase 5's original risk note: art/UI work has no natural stopping point. The single-tileset-first cap and the explicit non-goals list above exist specifically to prevent this phase from quietly expanding into a full four-tileset redraw or unit/building art before the pipeline and the first surface are validated. If scope creep starts here, stop and ship what's validated rather than extending the phase.

## Do NOT attempt yet

- Unit or building sprite replacement.
- A second faction's visual identity.
- Sound/music production.
- Any of the remaining three tilesets, before the first one clears the exit criteria above.
- Diplomacy/shared-resource systems (Phase 8+, unchanged gate — see below).

## Relationship to the former "Phase 6: Diplomacy" slot

Diplomacy and shared-resource systems (alliances, betrayal, resource sharing on top of Grid Reserve) are unaffected by this redefinition — same scope, same conditional framing, same exit gate (Phase 3-5 playtests showing sustained 3+ player engagement with Grid Reserve and explicit tester demand for social mechanics), just renumbered to **Phase 8+** to make room for this phase and the new Phase 7 (sound/music pass). That gate has not been met as of this writing — no recorded playtests exist yet for Phases 3-5 (see `docs/BACKLOG.md`'s implementation status notes) — so Phase 8 remains exactly as un-started and un-scoped as "Phase 6" was before this document.

## Implementation status

See `docs/BACKLOG.md` issues #12-17 for the current per-deliverable status. Summary as of this writing:

- **Asset pipeline lock (#12): done.** Palette hex values, sprite/frame conventions, and naming convention are in `docs/ART_DIRECTION.md`.
- **Chrome (#15): partially done.** `dialog.png` and `sidebar.png`/`loadscreen.png`(+2x/3x) are recolored to the locked palette. A real finding surfaced doing this work: `sidebar.png`'s "no radar yet" placeholder art and `loadscreen.png` contained the literal stock **Allied chevron and Soviet hammer-and-sickle logos** baked into this mod's committed art — both were replaced with a procedural Sungrid placeholder emblem rather than left shipping unrelated faction IP. **This emblem is itself a placeholder, not final art** — see `mods/sungrid/uibits/PLACEHOLDER_ART.md` for exactly which pixels to replace and how (it lives next to the art it documents, specifically so a designer doesn't have to go hunting for it). Mod-chooser chrome and rendered-client verification remain open.
- **Cursors (#13) and terrain (#14, #16): blocked.** Both are Westwood `.shp`-format sprite sheets and need OpenRA's `utility` tool (built from the fetched `engine/`) to decode/encode. This session's environment has no fetched/built engine and no standalone SHP codec, so this work needs an environment where `make`/`fetch-engine.sh` can actually run.
- **Visual regression pass (#17): not started** — depends on #13/#14 and on having a rendered client to check against, neither available here.
