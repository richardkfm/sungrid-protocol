# Sungrid Protocol — Issue Backlog

GitHub Issues are currently **disabled** on this repository, so these could not be opened as actual GitHub issues (attempted via the API, got `410 Issues has been disabled in this repository`). This file holds the exact content, ready to paste in as-is once Issues is enabled (repo Settings → Features → Issues), or to import via `gh issue create` / the GitHub UI.

Once Issues is enabled, these can be created in order and this file can be trimmed down to just a pointer, or deleted.

---

### 1. Port mods/ra's gameplay into mods/sungrid

**Labels:** `phase:1`, `type:content`, `good-first-issue`

**Phase:** 1 — Baseline playable shell (see `docs/ROADMAP.md`)

**Purpose:** Replace the placeholder SDK example-mod content in `mods/sungrid` (already renamed to Sungrid branding as part of the Mod SDK migration) with real gameplay forked from `mods/ra`. No new rules/mechanics yet — this is a content port, not a design pass.

**Scope:**
- Pull `mods/ra`'s rules/sequences/maps from the fetched engine's bundled copy (`engine/mods/ra` after `fetch-engine.sh` runs) or the public OpenRA/OpenRA repo, since `mods/ra` is no longer vendored in this repo.
- Replace `mods/sungrid`'s current placeholder content (rules, sequences, maps, chrome, fluent strings) with the ported RA content.
- Keep `mod.yaml`/`mod.config` metadata as already set by the Mod SDK migration (mod id `sungrid`, etc.) — no changes needed there.
- No new units/buildings/rules design in this issue — straight port only.

**Dependencies:** Depends on the Phase 0 docs + Mod SDK migration PR being merged, since it defines this exact approach and already did the renaming/scaffolding.

**Definition of done:** `mods/sungrid` builds, plays real Red Alert-derived gameplay (not the SDK's placeholder example content), and appears as its own distinct entry (not "Red Alert") in the OpenRA mod chooser.

---

### 2. Verify baseline playable shell (skirmish vs. AI)

**Labels:** `phase:1`, `type:content`

**Phase:** 1 — Baseline playable shell (see `docs/ROADMAP.md`)

**Purpose:** Prove `mods/sungrid` is genuinely playable with real content before any solarpunk content work starts, per the "fastest path to a playable prototype" sequencing in `docs/ARCHITECTURE.md`.

**Scope:**
- Launch `mods/sungrid`.
- Play a full skirmish match against the built-in AI.
- Confirm destruction victory/defeat triggers correctly.
- Confirm no crashes and assets load correctly under the mod id.

**Dependencies:** Blocked by #1 "Port mods/ra's gameplay into mods/sungrid."

**Definition of done:** A complete skirmish match can be played start-to-finish with a normal win/loss result and no crashes.

---

### 3. Confirm CI is green on real mod content

**Labels:** `phase:0`, `type:engine`

**Phase:** 0/1 — Bootstrap / Baseline playable shell

**Purpose:** CI (`ci.yml`) already builds/validates `mods/sungrid` against the fetched engine as part of the Mod SDK migration — but only against the SDK's placeholder example content so far. This issue confirms CI still passes once #1 replaces that placeholder with real `mods/ra`-derived content, per `docs/CONTRIBUTING.md`'s PR checklist ("builds cleanly").

**Scope:**
- Re-run CI (`make check`, `make test`) against #1's ported content and fix anything that breaks.
- Confirm CI still fails on an intentionally broken mod build/rules parse.

**Dependencies:** Blocked by #1.

**Definition of done:** CI is green against real `mods/ra`-derived content; a PR that intentionally breaks `mods/sungrid` still fails CI.

---

### 4. Add Solar Array + Battery Bank building stubs

**Labels:** `phase:2`, `type:content`, `area:energy`

**Phase:** 2 — First solarpunk content layer (see `docs/ROADMAP.md`, `docs/BUILDINGS.md`)

**Purpose:** First visible solarpunk content pass, entirely data-driven.

**Scope:**
- Solar Array: reflavor of the power plant (`Power` trait, new name/sequence, placeholder or recolored art is fine).
- Battery Bank: reflavor of the silo/storage building as **placeholder economy only** — this is not yet the Grid Reserve Vault mechanic (that's issue #6/#7).
- No new C# traits.

**Dependencies:** Blocked by #2.

**Definition of done:** Both buildings are buildable in a skirmish match, function correctly (power generation / storage), and don't regress the Phase 1 baseline.

---

### 5. Add Recycling Depot (salvage-based economy building)

**Labels:** `phase:2`, `type:content`, `area:economy`

**Phase:** 2 — First solarpunk content layer (see `docs/ROADMAP.md`, `docs/BUILDINGS.md`)

**Purpose:** Second economy stream rewarding map control and battlefield cleanup, per the Recycling Depot spec in `docs/BUILDINGS.md`.

**Scope:**
- Refinery-adjacent building that reclaims Credits from destroyed units/buildings (wrecks).
- Data-driven where possible; flag in the PR if wreck-salvage genuinely requires new trait logic (see `docs/ARCHITECTURE.md` friction points).

**Dependencies:** Blocked by #2.

**Definition of done:** Buildable, and produces Credits from battlefield wreckage during a test skirmish match.

**Resolution:** The original "produces Credits from battlefield wreckage" DoD was never actually met — Phase 2 shipped `RCYD` as a YAML-only reflavor with a flat, unconditional `CashTrickler` and no wreck detection or collection mechanic at all. Investigated during a later design pass (recycling/trash-collection design, see `docs/BUILDINGS.md` #3): death-triggered wreck salvage has no existing trait support in this ruleset and would need new custom C# to implement, contradicting the data-driven-first preference in `docs/ARCHITECTURE.md`. Corrected design instead reuses the existing Ore/Gems economy machinery for a new map-placed `Scrap` resource: `RCYD` gained `Refinery`/`DockHost`/`StoresPlayerResources`/`FreeActor` (mirroring `PROC`/`HARV`), and a new dedicated `SGHAU` "Hauler Drone" unit (small, unarmed, ground-mobile — `Harvester` requires `Mobile`, so it can't be a flying unit like `SGDRO`/`SGDRS`) collects Scrap and docks at `RCYD`. The original `CashTrickler` baseline is retained unconditionally since no currently-shipped map has `Scrap` patches painted (that requires the in-game Map Editor against a real local build, and is tracked as a separate follow-up — hand-painting `chernobyl` first as the initial testable instance). Real completion: `world.yaml`/`player.yaml`/`vehicles.yaml`/`structures.yaml`/`sequences/misc.yaml`/`fluent/rules.ftl` changes land the mechanic; the map-painting follow-up and DockHost/DockOffset visual tuning against a real client remain open, same caveat pattern as other Phase 5 content in this repo's history.

---

### 6. RFC: Grid Reserve trait design — RESOLVED

**Resolution:** Design implemented and documented in the "Technical design (resolved RFC)" section of `docs/GAME_MODES.md` alongside issue #7's implementation. Summary: the Vault is the existing Battery Bank (`SILO`) actor gaining a `GridReserveVault` trait rather than a new building; `GridReserveManager` (per-player) tracks totals/target in integer-only arithmetic; `GridReserveController` (world) owns the lobby toggle, Lockdown countdown, and Grid Decay, and resolves the win by force-completing the winner's `MissionObjectives` (riding the existing `ConquestVictoryConditions` required-objective gate rather than touching `Player.WinState` directly). See the doc for the full reasoning and the explicit couplings/assumptions it calls out.

**Labels:** `phase:3`, `type:design`, `area:grid-reserve`, `risk:scope-trap`

**Phase:** 3 — Economic victory mode MVP (see `docs/GAME_MODES.md`, `docs/ARCHITECTURE.md`)

**Purpose:** This is the project's first genuinely new C# system and its highest-risk technical item (deterministic/lockstep-safe custom win condition). Per `docs/CONTRIBUTING.md`'s RFC workflow, design it in an issue before writing implementation code.

**Scope:**
- Concrete trait design for the Vault building: deposit tracking (irreversible, per-tick rate cap), per-Vault capacity cap, destruction-drain behavior (~50% Reserve loss + attacker Credit reward), and the hold-to-win "Grid Lockdown" countdown hook into OpenRA's `MissionObjectives`/win-condition framework.
- Explicit check for multiplayer lockstep determinism (no floating point drift, no client-only randomness).
- Update `docs/GAME_MODES.md` and/or `docs/ARCHITECTURE.md` in this issue/PR if the concrete design diverges from the current spec.

**Dependencies:** Blocked by #2. Should ideally follow #4/#5 so there's a stable content base to build on, but is not strictly blocked by them.

**Definition of done:** RFC issue resolved with a design that's been sanity-checked against OpenRA's existing win-condition/resource trait patterns; docs updated to match; ready to hand to an implementation issue.

---

### 7. Implement Grid Reserve Vault trait + win condition — IMPLEMENTED, needs engine-build verification

**Status:** `GridReserveVault`, `GridReserveManager`, and `GridReserveController` are implemented in `OpenRA.Mods.Sungrid/GridReserve/` and wired into `mods/sungrid/rules/{structures,player,world}.yaml`. This was built against the pinned engine's actual trait source (fetched read-only from `OpenRA/OpenRA` at `ENGINE_VERSION` to confirm exact APIs — `PlayerResources`, `MissionObjectives`, `ConquestVictoryConditions`, `RevealsShroud`, `ILobbyOptions`, condition granting), but **could not be compiled or run in the environment this was implemented in** (no access to build the pinned engine there). CI (`ci.yml`) builds against the real fetched engine and is the first real compile of this code — treat its result as the actual verification, and expect to iterate on any build errors it surfaces. The 1v1 local test match described below still needs a human playtester.

**Labels:** `phase:3`, `type:engine`, `area:grid-reserve`

**Phase:** 3 — Economic victory mode MVP (see `docs/GAME_MODES.md`)

**Purpose:** Implement the resolved RFC — the actual Grid Reserve mechanic that makes the economic victory mode exist.

**Scope:**
- Vault building trait (deposit/capacity/destruction-drain) per the resolved RFC.
- Win-condition trait for the Grid Lockdown countdown (start on reaching target, cancel/reset if Reserve drops below target).
- Lobby toggle for the mode; destruction victory remains available and unaffected when toggled off.

**Dependencies:** Blocked by #6.

**Definition of done:** A 1v1 local test match can be won via Grid Reserve end-to-end (deposit → reach target → hold Lockdown → win), and destruction victory still works normally when the mode is toggled off.

---

### 8. Add Grid Reserve HUD/scoreboard elements — IMPLEMENTED, needs engine-build + visual verification

**Status:** All four HUD elements are now implemented. The two that were previously deferred — the per-player sidebar bar and the all-players scoreboard — were added in Phase 4 as `GridReserveHudLogic` and `GridReserveStandingsLogic` (`OpenRA.Mods.Sungrid/GridReserve/`), wired into `mods/sungrid/chrome/ingame-player.yaml` and `mods/sungrid/chrome/ingame-observer.yaml`. Both were written against the pinned engine's actual widget/logic source (`ProgressBarWidget`, `LabelWidget`, `ChromeLogic`, `ObserverStatsLogic`, etc., fetched read-only from `OpenRA/OpenRA` at `ENGINE_VERSION`), the same approach #7 used — but **could not be compiled or rendered in the environment this was implemented in** (no engine build access there either). CI is the first real compile; layout/positioning (the fixed `X`/`Y` coordinates chosen to avoid the existing sidebar art without overlap) has not been visually confirmed in a running client and should be checked in the first real playtest.

**Labels:** `phase:3`, `phase:4`, `type:engine`, `area:grid-reserve`

**Phase:** 3/4 — Economic victory mode MVP / Playtest Hardening (see `docs/GAME_MODES.md`)

**Purpose:** Make Grid Reserve legible and dramatic to play, not just functional — the countdown broadcast and minimap reveal are core anti-turtle mechanics, not cosmetic.

**Scope:**
- Per-player Reserve bar with numeric current/target. **Done** — `GridReserveHudLogic` drives a `ProgressBar` + label centered at the top of `ingame-player.yaml`'s HUD, reading `GridReserveManager.TotalReserve`/`Target` directly; hides itself via the new `GridReserveController.Enabled` accessor when the lobby option is off.
- Broadcast banner + audio cue to all players when a Lockdown countdown starts or cancels. **Done** (Phase 3) — unchanged.
- Minimap reveal of a player's Vault locations once their Reserve hits 50% of target. **Done** (Phase 3) — unchanged.
- End-of-match scoreboard showing final Reserve totals for all players regardless of win condition used. **Done** — `GridReserveStandingsLogic` lists up to 8 players' current/target Reserve in `ingame-observer.yaml`. Placed there rather than a dedicated post-game screen because `MissionObjectives.EarlyGameOver: true` (set in `rules/player.yaml`) already drops every remaining participant into the observer/spectator widget tree the moment the match resolves (`Player.Spectating` flips true off `WinState`), so this panel is visible to everyone at match end regardless of which victory condition triggered it.

**Dependencies:** Blocked by #7 (implemented; pending CI/build verification — see #7's status note).

**Definition of done:** All four HUD elements are visible, correctly triggered, and verified in a test match. Implementation is complete; remaining work is purely verification — confirm layout/readability in a rendered client and that nothing overlaps existing sidebar art, as part of issue #9's playtest pass.

---

### 9. 3-4 player Grid Reserve playtest + balance pass

**Status:** Mechanical/technical bar cleared, balance question still open. Built the engine from source and ran a headless 4-player (1 real client + 3 AI bots: normal/normal/turtle) Grid-Reserve-enabled skirmish on a temperate 4-player map (Chernobyl) for ~4.5 minutes of simulated time. Confirmed via `perf.log`/`server.log`: `GridReserveManager`, `MissionObjectives`, and `HarvesterBotModule` all initialized correctly per player, the world loaded, the match started, and there were zero exceptions or desyncs across the run. This rules out crash/desync risk under real multi-player load. **It does not answer this issue's actual question** — the AI bots don't meaningfully engage with Grid Reserve strategy (they're not turtling deliberately or contesting vaults), so "can a player win by hiding" and "does a raid disrupt a leader's countdown" are still unverified and need real human players. The automated harness used for this (a temporary, local-only, never-committed CLI flag added to the gitignored `engine/` to headlessly fill a skirmish lobby with bots) is documented in `docs/PLAYTESTING.md`'s "Headless / automated testing" section for reuse.

**Labels:** `phase:3`, `phase:4`, `type:content`, `area:grid-reserve`, `risk:scope-trap`

**Phase:** 3/4 — Grid Reserve MVP / Playtest Hardening (see `docs/GAME_MODES.md`)

**Purpose:** Grid Reserve's entire value proposition depends on turtling being a losing strategy. This issue exists specifically to stress-test that, not just general balance — see "Top 3 scope traps" #2 in `docs/BLUEPRINT.md`.

**Scope:**
- Run structured 3-player and 4-player matches with Grid Reserve enabled.
- Specifically probe: can a player win by hiding and never engaging? Does a Vault raid meaningfully disrupt a leader's Lockdown countdown in practice?
- Tune Reserve targets, decay rate, deposit caps, and minimap reveal threshold from `docs/GAME_MODES.md` based on results; update the doc if numbers change.

**Dependencies:** Blocked by #8.

**Definition of done:** At least one recorded match is won via Grid Reserve with a documented instance of a Vault raid affecting the outcome; no playtest match is won by a strategy reviewers would describe as "just hide and wait."

---

### 10. Set up first external playtest build/packaging

**Status:** Packaging build verified, cross-machine dry-run still open. Ran the actual `packaging/linux/buildpackage.sh` build. It compiles the engine + mod in Release mode, stamps the given version into `mod.yaml`, and assembles a complete AppDir bundle (~103MB: all engine + mod DLLs, launcher wrapper, desktop file, icon) — confirmed it registers and launches correctly via its `AppRun` entrypoint in a headless run. The final step (wrapping the AppDir into a single-file AppImage via the third-party `appimagetool` binary) could not complete in this environment because the session's GitHub access is scoped to `richardkfm/sungrid-protocol` only and the proxy blocks fetching arbitrary third-party release binaries from `github.com` — an environment limitation, not a packaging bug. This issue's actual definition of done (a non-team playtester installing and completing a match unassisted on a different machine) still needs a real external tester.

**Labels:** `phase:4`, `phase:5`, `type:content`

**Phase:** 4/5 prep — Playtest Hardening / Faction Flavor (see MVP definition in `docs/BLUEPRINT.md` section 4)

**Purpose:** Get a build that a non-team playtester can install and run unassisted — this is the concrete "ready for first public testers" gate.

**Scope:**
- Package a distributable build of `mods/sungrid` (installer or archive, per platform as feasible).
- Write minimal install/run instructions for testers.
- Dry-run the install process on a machine that isn't the founder's dev environment.

**Dependencies:** Blocked by #9. Should also follow enough of Phase 5's building roster to be worth external testing (see `docs/ROADMAP.md`), but packaging work itself can start in parallel.

**Definition of done:** A non-team playtester successfully installs the build and completes a full match unassisted.

---

### 11. Add remaining Phase 5 building roster (Cryptominer, Datacenter for AI, Drone Bay, Grid Defense Turret, Smart Grid Relay, Resilience Shelter, Sensor Array) — IMPLEMENTED, needs engine-build verification

**Status:** All 7 buildings are implemented as pure YAML in `mods/sungrid/rules/structures.yaml` (`SGCRY`, `SGDAI`, `SGDRN`, `SGTUR`, `SGREL`, `SGSHL`, `SGSNS`), plus two small additive fragments in `mods/sungrid/rules/defaults.yaml` (`^Building` gains a `ProximityExternalCondition`-gated `DamageMultiplier` for Resilience Shelter's aura; `^Vehicle` gains one for Drone Bay's speed bonus) and fluent strings in `mods/sungrid/fluent/rules.ftl`. No new C# traits were needed — see `docs/BUILDINGS.md`'s per-building notes for what stock traits ended up covering things originally assumed to need custom trait work (`GrantConditionOnPowerState`, `ProximityExternalCondition`, `CashTrickler`/`DetectCloaked`/`RevealsShroud` composition). Built against the pinned engine's actual trait source (`GrantConditionOnPowerState`, `CashTrickler`, `DetectCloaked`, `ProximityExternalCondition`, `PlayerResources`), fetched read-only from `OpenRA/OpenRA` at `ENGINE_VERSION`, the same approach used for Grid Reserve — but **could not be compiled or run in the environment this was implemented in**. CI is the first real compile; a human playtest is still needed.

**Labels:** `phase:5`, `type:content`, `area:energy`, `area:economy`, `area:defense`, `area:intelligence`, `area:logistics`

**Phase:** 5 — Faction Flavor (see `docs/ROADMAP.md`, `docs/BUILDINGS.md`)

**Scope:**
- All 7 buildings, universal (no `~structures.allies`/`~structures.soviet` gating), matching the Phase 2 buildings' pattern.
- Placeholder art only (each reuses an existing structure's sprite) — see `docs/BUILDINGS.md`'s new art note. Real custom art, a faction-cohesive palette pass, and a sound/music pass are separate, not-yet-started Phase 5 deliverables (see `docs/ROADMAP.md`).
- Reconciled a stale discrepancy: `docs/BUILDINGS.md` had staged Smart Grid Relay, Resilience Shelter, and Sensor Array as "post-Phase 5," while `docs/ROADMAP.md`'s Phase 5 deliverables named all 7. Updated `docs/BUILDINGS.md`'s staging notes to match the roadmap rather than leave the docs drifted.

**Dependencies:** None blocking — additive to the existing tech tree, doesn't touch Grid Reserve or the Phase 1-2 economy buildings.

**Definition of done:** All 7 buildings are buildable in a skirmish match, function as described, CI is green, and a human playtest confirms no regressions to the existing build order/economy loop. Remaining Phase 5 scope (real art, palette cohesion pass, sound/music) tracked separately, not part of this issue.

---

### 12. Solar Array custom art pass — FIRST PASS DONE, needs a real artist polish pass

**Status:** `POWR`/`APWR` now render dedicated solar-panel-array art (`sgpwr`/`sgapwr` images, `mods/sungrid/bits/sgpwr.png` + `sgapwr.png` + icons) instead of the stock RA power-plant sprite, via a `RenderSprites: Image:` override and new sequence blocks in `mods/sungrid/sequences/structures.yaml`. Shipped as a `PngSheet`-format sprite (added to `mod.yaml`'s `SpriteFormats`) rather than a hand-authored indexed `.shp`, since that's the tractable path without a dedicated pixel-art tool/artist. Confirmed loading and rendering in a live headless skirmish with no regressions (icon renders in the build palette, damaged-idle state is visually distinct with scorch/crack detail, existing vendored `powrdead.shp`/`apwrdead.shp` death animations and shared bib decals are reused unchanged). **This is explicitly a first pass, not final production art** — it establishes the palette/tone (solar-panel blues, gold power-conduit accent, green reclaiming the base, sandbag wear per `docs/ART_DIRECTION.md`) but is programmatically drawn, not a human/dedicated pixel-art pass, and the `make` (construction) sequence is a single static frame rather than a proper build-up animation. A real artist pass matching the rest of the roster's eventual quality bar is still open work.

**Labels:** `phase:5`, `type:art`, `area:energy`

**Phase:** 5 — Faction Flavor (see `docs/ROADMAP.md`, `docs/ART_DIRECTION.md`)

**Purpose:** The mod is named after this building's fiction and it currently has zero distinct visuals. `POWR`/`APWR` ("Solar Array"/"Advanced Solar Array") are a pure name-and-flavor-text reflavor of the vanilla RA power plant — `mods/sungrid/sequences/structures.yaml` still points them at the stock, unrecolored `powr.shp`/`apwr.shp` sprites (no `RenderSprites.Image` override, no palette change). Every other Phase 2/5 building shares this "placeholder art" debt, but Solar Array is the one whose absence is most visible: it's the title concept, the first building most players place, and the building `docs/ART_DIRECTION.md`'s palette direction ("warm solar-panel blues/blacks, sun-gold accents") was written to describe. Called out ahead of the general Phase 5 art/palette pass (referenced in #11 and `docs/ROADMAP.md`'s Phase 5 deliverables) so it isn't just one line item among ten equally-weighted buildings.

**Scope:**
- New indexed-palette sprite art for `POWR`/`APWR` (idle, damaged-idle, and existing death/build-up animation slots — see current `powr`/`apwr` sequence blocks in `mods/sungrid/sequences/structures.yaml` for the frame contract to match), depicting a grid-tied solar panel array per `docs/ART_DIRECTION.md`'s tone/palette guardrails (not utopian/pristine — panels with visible wear, mounting hardware, maybe sandbags/improvised bracing).
- Lock the sprite resolution/frame/naming conventions this establishes as the de facto Phase 5 asset pipeline baseline (`docs/ART_DIRECTION.md`'s "Asset pipeline" section currently says this needs to happen before more than one contributor produces art — this issue is a reasonable place for that baseline to actually get set, rather than deciding it in the abstract).
- Update `RenderSprites`/sequence references only if the new art requires a different filename/frame layout than the current `powr.shp`/`apwr.shp` slot; otherwise this is asset-only, no rules.yaml logic changes.
- Out of scope: the other 7 Phase 5 buildings' placeholder art (tracked generally under #11's "remaining Phase 5 scope" note), a second faction's art set, sound/music.

**Dependencies:** None blocking — Solar Array's mechanics (`Power` trait) are untouched and already playtested since Phase 2; this is asset-only.

**Definition of done:** `POWR`/`APWR` render with dedicated solar-panel sprite art (not stock RA power-plant art) in a skirmish match, matching `docs/ART_DIRECTION.md`'s palette/tone guardrails, with no regression to power generation behavior. **Met by the first pass above** for the mechanical/visual-distinctness bar; remaining open work is a real artist pass (proper indexed-palette pixel art, an actual construction/build-up animation) to replace the programmatically-drawn placeholder, tracked as a follow-up rather than reopening this issue.

---

### 13. Phase 6 chrome first-pass reskin — FIRST PASS DONE, cursors/terrain still blocked

**Status:** `mods/sungrid/uibits/dialog.png`, `sidebar.png`, and `loadscreen.png`(+`-2x`/`-3x`) recolored from stock RA's beige/maroon to the palette now locked in `docs/ART_DIRECTION.md`, via a scripted piecewise hue remap (only the stock reddish band shifts to green, so untouched hues and every file's exact canvas dimensions/`chrome.yaml` sub-region rects are preserved — verified byte-for-byte identical dimensions before/after). A real finding surfaced doing this: `sidebar.png`'s "no radar built yet" placeholder art (`chrome.yaml`'s `sidebar-allies`/`sidebar-soviet` `radar:` regions) and `loadscreen.png` contained the **literal stock Allied chevron and Soviet hammer-and-sickle logos** baked into this mod's own committed art. Both were replaced with a procedural placeholder emblem (gold hexagon/sun motif, locked palette) rather than ship unrelated faction IP while the rest of Phase 6 is pending. The recolor/emblem script is checked in as `mods/sungrid/uibits/reskin_chrome.py`, with `mods/sungrid/uibits/PLACEHOLDER_ART.md` alongside it — a file-by-file table of exactly which pixels are placeholder, their pixel-rect location, and how a human designer replaces them (hand-paint over the existing canvas, or tweak the script's palette/shape constants and re-run), co-located with the art specifically so it doesn't require re-reading this backlog entry to find.

Cursors (`cursors.yaml`) and terrain tilesets (`mods/sungrid/tilesets/*.yaml`) are **not** touched by this pass and remain fully stock — both are Westwood `.shp`-format sprite sheets that need OpenRA's built `utility` tool (from the fetched `engine/`) to decode/encode, which wasn't available in the environment this pass was done in. Same for the main-menu shellmap (`maps/desert-shellmap/`, distinct from the loading-screen splash `loadscreen.png` above) — its terrain is the same blocked `.shp` format. Mod-chooser chrome and rendered-client verification (including confirming the Phase 3/4 Grid Reserve HUD still reads cleanly against the new skin) also remain open.

**Labels:** `phase:6`, `type:art`, `area:ui`

**Phase:** 6 — World & UI Visual Identity Overhaul (see `docs/ROADMAP.md`, `docs/ART_DIRECTION.md`)

**Purpose:** `docs/ROADMAP.md`'s Phase 6 deliverables call for custom UI chrome "replacing stock RA's beige/gold frame." This is a first pass toward that, using the same "programmatic first pass now, real artist pass later" approach issue #12 used for Solar Array — and, like #12, it surfaced a real content problem (literal faction IP in the mod's own art) worth fixing immediately rather than leaving until a full art pass.

**Scope:**
- Recolor `dialog.png`, `sidebar.png`, `loadscreen.png`(+2x/3x) to the locked palette in `docs/ART_DIRECTION.md`, preserving exact canvas dimensions and `chrome.yaml` region geometry.
- Replace the literal Allied/Soviet logos found in `sidebar.png`/`loadscreen.png` with a placeholder emblem — not final logo art, but not shipping unrelated faction IP either.
- Out of scope: cursors, terrain tilesets, the main-menu shellmap (all blocked on engine-build access), mod-chooser chrome, unit/building sprites, real designer logo art.

**Dependencies:** None blocking for this first pass. Cursors/terrain/shellmap need an environment where `make`/`fetch-engine.sh` can actually build the engine (for `utility`'s SHP encode/decode).

**Definition of done for this issue:** Chrome PNGs read as Sungrid Protocol rather than stock RA, with no literal Allied/Soviet branding remaining, and no regression to `chrome.yaml`'s region geometry. **Met by the first pass above.** Remaining Phase 6 scope (cursors, terrain, shellmap, mod-chooser chrome, rendered-client verification, a real designer pass replacing the placeholder emblem) tracked as follow-up work, not part of this issue.

---

### 14. Replace Flame Infantry and Flame Tower — DONE

**Status:** A tone/content call (immolation weapons don't fit the project), not a balance or design-doc-driven change, so there's no RFC/spec to update. Initially implemented as a straight removal, then revised to a like-for-like **replacement** so the Soviet tech tree doesn't lose a slot: `E4` (Flame Infantry) → **`DISR`, Disruptor Trooper**; `FTUR` (Flame Tower) → **`ARCT`, Arc Turret**. Both replacements keep the original's exact `Buildable`/`Health`/`Armor`/cost/prerequisite/tech-level slot and the same chassis art (`e4.shp`/`ftur.shp`+bib, reused under the new actor ids — the models themselves were never the issue, only the weapon), so the tech tree, AI build orders, and balance are unchanged in shape. Only the weapon changed:
- **`Disruptor`** (replaces `Flamer`) and **`ArcDischarge`** (replaces `FireballLauncher`), `mods/sungrid/weapons/other.yaml` — same damage/spread/versus/burst numbers as the weapons they replace, `DamageTypes` swapped from `FireDeath, Incendiary` to `ElectricityDeath`, and no napalm/scorch effects (`LeaveSmudge` now `SmudgeType: Crater`, no `CreateEffect`).
- Fluent text reframes both as grid-current/disruptor-based rather than fire-based.

Every reference updated to point at the new ids instead of dangling or disappearing:
- `mods/sungrid/rules/ai.yaml`: `arct` added back into `EnemyBaseBuildingTypes`, all four bot tiers' `DefenseTypes`/`BuildingFractions`/`BuildingDelays` (same weights `ftur` had: 3/2000, 10/1500, 13, 2), and all four `ProtectionTypes` lists.
- `mods/sungrid/maps/desert-shellmap/rules.yaml`: paratrooper `DropItems` now drops `DISR` where it used to drop `E4`.
- `DISR`'s `Prerequisites` points at `arct` (was `ftur`) — the coupling itself (trooper requires the tower first) is preserved, just renamed.
- The Giant Ant's `AntFireball` weapon (which inherited from the now-removed `FireballLauncher`) was re-pointed at the shared `^FireWeapon` template both it and `FireballLauncher` originally descended from, with the two fields it needed (`Projectile.TrailImage`/`Image`) copied in explicitly — unaffected by the Flamer/FireballLauncher removal either way.

**Labels:** `type:content`, `type:bug`

**Phase:** Not tied to a specific roadmap phase — a tone/content correction applicable regardless of phase.

**Purpose:** Direct tone call: flamethrower/incendiary-against-infantry weapons don't fit the project. Replacing rather than deleting keeps the Soviet early-game tech tree (an anti-infantry static defense, an anti-structure trooper gated behind it) intact rather than quietly losing two roster slots.

**Scope:**
- Replace `E4`/`FTUR` with `DISR`/`ARCT`, reusing the original chassis art and every `Buildable`/cost/prerequisite/tech-tier value unchanged.
- New `Disruptor`/`ArcDischarge` weapons matching the original `Flamer`/`FireballLauncher` damage numbers, re-themed away from fire.
- Update every AI list/dict, the map drop table, and the actor-to-actor prerequisite to reference the new ids.
- Out of scope: other fire-based weapons (e.g. `Napalm`, used by an airstrike-style support power) — only the two units named were in scope.

**Dependencies:** None.

**Definition of done:** `DISR`/`ARCT` are buildable in the same tech-tree slot `E4`/`FTUR` occupied, with equivalent stats and no fire/incineration mechanic; no dangling reference to the old or new ids anywhere in `mods/sungrid`. **Met.** Still needs the same engine-build verification every other content change in this backlog is pending on (no build access in this environment) — in particular, confirming `ftur.shp`/`e4.shp` (pulled from the RA content pack, not committed in this repo) actually render correctly under the new `arct`/`disr` sequence keys.

---

### 15. Rename the two playable sides away from "Allies"/"Soviet" — PARTIALLY DONE

**Status:** The two umbrella sides are renamed in every player-facing string: **Allies → The Consortium** (capital/technocratic bloc), **Soviet → The Assembly** (scarcity-adapted, improvisational bloc) — a direct fiction request, not derived from a design doc. Updated in `mods/sungrid/fluent/rules.ftl`: the `faction-allies`/`faction-soviet`/`faction-randomallies`/`faction-randomsoviet` fluent entries, and every building/unit name or description that said "Allied"/"Soviet" as an adjective (Tech Center, Barracks, the two fake-structure decoys, Medium/Heavy Tank's flavor text).

**What's deliberately left unrenamed, and why:** the umbrella rename does **not** touch the five individual playable country sub-factions underneath it (`faction-england`/`france`/`germany` under the old Allies side, `faction-russia`/`faction-ukraine` under the old Soviet side, each with real-world-coded special units — British Spy, Tesla Tank, Demolition Truck, etc.) — that's a separate, larger creative decision (new names for five sub-factions, and specifically whether "Russia"/"Ukraine" as opposing in-game factions is something to keep given real-world context) that shouldn't be assumed. Also left alone: every place "Allies"/"Soviet" appears as an **internal identifier** rather than displayed text — `~structures.allies`/`~structures.soviet` prerequisite conditions, `Side: Allies`/`Side: Soviet` in `world.yaml`'s `Faction` definitions, `RandomAllies`/`RandomSoviet` palette-remap keys in `chrome.yaml`, `Allied*`/`Soviet*` notification keys in `audio/notifications.yaml` (the audio files themselves are still stock RA voice lines literally saying "Soviet Empire has fallen" — a Phase 7 audio-pass concern, not a text one), `Soviets:`/`Allies:` palette keys in `campaign-palettes.yaml`, and the ~300 `Owner: Allies`/`Owner: Soviets`/`PlayerReference@Allies`/`PlayerReference@Soviets` entries in the main-menu shellmap (`maps/desert-shellmap/map.yaml`) — none of these are ever displayed as text to a player, so renaming them would be pure internal-plumbing churn with real risk of a typo silently breaking the shellmap or a prerequisite gate.

**Labels:** `type:content`

**Phase:** Not tied to a specific roadmap phase — a tone/fiction correction applicable regardless of phase.

**Purpose:** `docs/BACKLOG.md`'s own earlier audits (and a direct ask) flagged that the two sides were still literally named "Allies"/"Soviet" — the single most player-visible remaining piece of unrenamed Red Alert content, read on every faction-picker screen and in dozens of unit/building tooltips.

**Scope:**
- Rename the two umbrella `Faction` display names and every adjectival "Allied"/"Soviet" use in building/unit fluent text.
- Leave internal ids, palette keys, notification keys, and shellmap ownership data untouched — not player-visible, not in scope.
- Out of scope: the five sub-faction names, their real-world-coded special units, and the RA-original stock voice-line audio.

**Dependencies:** None.

**Definition of done for this pass:** No player-facing string reads "Allies"/"Allied"/"Soviet" anywhere in `mods/sungrid` (confirmed via a full grep of `mods/sungrid/fluent/`). **Met.** Sub-faction naming and the audio pass remain open, tracked separately rather than folded into this issue.

---

### 16. Menu & intro first-boot redesign — FIRST PASS DONE, mainmenu layout/cursors/shellmap terrain still blocked

**Status:** Direct ask: the game should read as distinctly not-Red-Alert from the moment it boots, not just once you're in a match. Three things landed in this pass:

- **Fixed a real regression from issue #14:** `maps/desert-shellmap/map.yaml` (the map that runs as the animated main-menu background) still placed six actors as `ftur` — the Flame Tower removed in #14 and replaced with `arct` (Arc Turret). Since `FTUR` no longer exists as an actor type, the shellmap would have failed to load its background battle entirely — the main menu itself was broken by that earlier change and this went unnoticed because there was no build/render access to catch it. All six (`Actor68`, `112`, `113`, `114`, `187`, `188`) now place `arct` instead.
- **Replaced `mods/sungrid/icon.png`/`icon-2x.png`/`icon-3x.png`** (the window/taskbar icon, and the icon shown for this mod in the OpenRA mod chooser — arguably the single most-seen-at-boot asset there is): the stock file was a literal Soviet red star with a hammer-and-sickle, unmodified since the Phase 1 content port. Replaced outright with the same procedural gold-hexagon/sun/green-band emblem used elsewhere in the Phase 6 chrome pass (`reskin_chrome.py`'s new `process_icons()`), at each file's existing canvas size (32/64/96px).
- **Reworded two loading-screen tip strings** (`loadscreen-loading` in `fluent/mod.ftl`) that referenced other franchises' iconography with no thematic tie to Sungrid ("Activating Skynet...", "Compiling EVA...") to grid/energy-flavored equivalents ("Balancing the Grid...", "Composting Scrap...").

**What's still blocked, and why:** the things that would move the needle most are exactly the items issue #13 already flagged as needing a built engine or new authored assets, unchanged by this pass:
- **Main menu widget layout itself** (button arrangement, title placement) is `common|chrome/mainmenu.yaml` per `mod.chrome.yaml` — engine-owned, not overridden by `mods/sungrid`. The Phase 6 chrome pass already reskins everything that layout draws from (`dialog.png`/`sidebar.png`/`loadscreen.png`'s colors and emblem, the custom `Title` font), so the visual *content* is already Sungrid; a from-scratch widget layout override would need to duplicate the engine's `MainMenuLogic` widget-ID contract with no way to render/verify it in this environment — deferred rather than risk a silent breakage.
- **Cursors and terrain tilesets** (including the shellmap's own terrain, distinct from its actor placement fixed above) are unchanged stock `.shp` assets — same `utility`-tool/build-access blocker as issue #13.
- **Main menu music.** The main menu's background track is `audio/music.yaml`'s `intro` entry (`Hidden: true`, i.e. not in the jukebox list — directly referenced by id) — this is stock Red Alert's own theme audio file, arguably as recognizable as the visuals were. Changing it needs a newly composed/licensed track, which is explicitly Phase 7 (`docs/ROADMAP.md`'s "Unit & Audio Identity Pass") scope, not something this pass can produce.
- **FMV intro / mod-chooser splash video**, if any, is stock content-pack video, same asset-authoring blocker as issue #13.

**Labels:** `phase:6`, `type:art`, `type:bug`, `area:ui`

**Phase:** 6 — World & UI Visual Identity Overhaul (see `docs/ROADMAP.md`, `docs/ART_DIRECTION.md`)

**Purpose:** A player's very first impression is the mod-chooser icon, the boot window icon, and the main menu — if any of those still read as stock Red Alert (or are broken outright), everything else in Phase 6 is undercut before a match even starts.

**Scope:**
- Fix the `ftur` shellmap actor-id regression from issue #14.
- Replace the literal stock Soviet icon set with the locked Phase 6 emblem.
- Polish loading-tip copy for thematic consistency.
- Out of scope (blocked, tracked here for visibility): main menu widget layout, cursors, terrain tilesets (including the shellmap's own terrain), main menu music, any FMV/video intro.

**Dependencies:** None blocking for this pass. The remaining items need either a built engine (`fetch-engine.sh`/`make`, for `utility`'s SHP encode/decode and for actually rendering/verifying a `mainmenu.yaml` override) or new composed audio/video assets (Phase 7).

**Definition of done for this pass:** The shellmap loads without a dangling actor reference, and the icon shown in the taskbar/window chrome/mod chooser is Sungrid's own emblem rather than a stock faction logo. **Met.** Main menu layout, cursors, terrain, and music remain open, explicitly tracked above rather than implied "done" by this issue's title.

---

### 17. Unblock and verify engine-build access for cursors/terrain — RESOLVED, ready to hand to an art/wiring pass

**Status:** Issues #13 and #16 both named the same recurring blocker for the rest of Phase 6: no session doing that work had access to a built engine, so `utility`'s `.shp` encode/decode could never be exercised. `docs/PLAYTESTING.md`'s "Headless / automated testing" section already documented the environment recipe from #9/#10/#12's work (apt-installed `dotnet-sdk-8.0`, the `CryptoUtil.SHA1Hash([])` ambiguity workaround, the `ra-quickinstall` content package), but nobody had actually run it through to the specific commands #13/#16 need. This pass did:

- **Engine build, from this repo's own history, no external download needed.** `mod.config`'s `ENGINE_VERSION` (`bf4102a0...`) was pinned to the exact commit this repo's own `bleed` branch sat at — so `./engine` was populated directly from a `git worktree add`/checkout of `origin/bleed` instead of fighting `fetch-engine.sh`'s zip download, which a scoped GitHub token/proxy may block. **Note for reproducing this: `bleed` has since been deleted from the remote** (see `CLAUDE.md`'s "Working conventions"), but its history is not lost — `main` was built directly on top of it, so `git checkout <ENGINE_VERSION SHA>` (or `git worktree add`/`git show` against that SHA) still works against `origin/main` in any full (non-shallow) clone; a shallow clone may need `git fetch --unshallow` first. Confirmed the pinned commit hits the documented `CS0121` `CryptoUtil.SHA1Hash([])` ambiguity under SDK `8.0.128` (installed via `sudo apt-get install -y dotnet-sdk-8.0`); applying the one-line local-only fix (`Array.Empty<byte>()`) in the gitignored `engine/` let `make` complete with **0 warnings, 0 errors** for both the engine and `OpenRA.Mods.Sungrid` — the first time Phase 3's Grid Reserve traits and Phase 5's building roster have been confirmed to compile by anyone/anything other than a manual one-off (see below on CI).
- **Content assets, legitimately.** Fetched `ra-quickinstall.zip` from a mirror in `ra-quickinstall-mirrors.txt`, verified its SHA1 matches the one already documented in `PLAYTESTING.md`, extracted into `<SupportDir>/Content/ra/v2/`. This is OpenRA's own official freeware redistribution, not a piracy workaround.
- **The actual thing #13/#16 needed proven, not just theorized:** extracted the real `mouse.shp` (the file `cursors.yaml`'s stock cursor definitions point at) via `utility.sh --extract`, decoded it to 222 individual PNG frames via `--png mouse.shp temperat.pal`, and re-encoded those PNGs back into a working `.shp` via `--shp` — a clean round-trip. Repeated the same for a terrain tile (`clear1.tem`, a `temperat.yaml` template) via `--extract`/`--png`/`--shp`.
- **One real technical wrinkle surfaced, worth flagging before someone starts the actual art pass:** `--shp` always writes a generic SHP-TS-style container, not a byte-identical re-encode of the original `.tem` TmpRA format. Reconstructing a tileset template likely means pointing `tilesets/temperat.yaml`'s `Images:` field at the new `.shp` output (the mod's `SpriteFormats` list already includes `ShpTS` alongside `TmpRA`) rather than assuming the round-trip preserves the `.tem` container — this wasn't tested end-to-end in a running client and should be the first thing whoever picks up the actual terrain reskin confirms.

**A second, unrelated finding surfaced doing this:** GitHub Actions shows **zero recorded workflow runs ever** on this repo, despite `ci.yml` being configured to trigger on every push/PR to `main`. Every "implemented, needs engine-build verification" status note across this backlog (issues #7, #8, #11, #14) was written assuming CI would eventually compile it — it apparently never has. This pass's manual `make` is the first real compile confirmation for any of that code. Worth checking whether Actions is disabled at the repo level the same way Issues is (see this file's intro) — if so, that's a bigger gap than any single issue here.

**Labels:** `phase:6`, `type:engine`, `area:ui`

**Phase:** 6 — World & UI Visual Identity Overhaul (see `docs/ROADMAP.md`)

**Purpose:** Every Phase 6 status note since #13 named the same blocker without anyone actually testing whether it still held. It didn't — this closes that gap so the remaining Phase 6 work (real cursor art, terrain retexture, main menu widget layout) is scoped purely as art/design/wiring work, not environment access.

**Scope:**
- Document a working recipe for building the engine and exercising `utility`'s SHP tooling without relying on `fetch-engine.sh`'s network path or a full manual RA install (this issue; `docs/PLAYTESTING.md` already carries the detailed steps).
- Prove the cursor and terrain `.shp`/`.tem` decode→edit→encode loop actually works, not just that the commands exist.
- Flag the `ENGINE_VERSION`-pin compile bug and the CI-never-ran finding for a real decision rather than silently working around them forever.
- Out of scope: doing the actual cursor/terrain art, verifying the round-tripped assets render correctly in a live client (no display was exercised in this pass — `PLAYTESTING.md`'s Xvfb recipe covers that for whoever picks this up next), fixing CI or bumping `ENGINE_VERSION`.

**Dependencies:** None blocking. Builds on the environment recipe `PLAYTESTING.md` already documented from #9/#10/#12.

**Definition of done:** A real `.shp` cursor and a real `.tem` terrain tile both round-tripped through `utility.sh --extract`/`--png`/`--shp` without error, using a legitimately-obtained content package and a from-source engine build. **Met.** Two decisions are now ready for a human call rather than another engineering pass rediscovering the same blocker: (1) `ENGINE_VERSION` is pinned to a commit that doesn't compile under current `.NET 8` SDK patch versions — per `docs/CONTRIBUTING.md`'s RFC process for engine bumps, this needs either a documented required local patch step or a deliberate re-pin, not a silent per-session workaround; (2) CI has never actually run — worth confirming whether Actions is disabled repo-wide before assuming any future green check means anything.

---

### 18. Phase 6 terrain reskin (temperate, snow, desert) — FIRST PASS DONE for all three, live-client verification still open

**Status:** Recolored the temperate tileset toward `docs/ART_DIRECTION.md`'s locked palette via a **palette-only** edit, not by touching individual tile sprites. `mods/sungrid/bits/reskin_terrain_palette.py` reads the stock `temperat.pal` (extracted via `utility.sh --extract`, per issue #17's now-working recipe) and applies a piecewise hue remap — the dominant tan/dirt/rust band (hue 0-45°) shifts toward the locked green, a small set of near-pure bright highlights (ore/gem glint accents) shift toward the locked sun-gold hex instead so they stay visually distinct from the green ground, and blues (water)/grays (rock, roads) are left untouched. Output is a new file, `mods/sungrid/bits/sungrid-temperat-terrain.pal`, and `rules/palettes.yaml`'s `PaletteFromFile@terrain-temperat` now points at it instead of stock `temperat.pal`.

**Why palette-only, and why it's safe:** `rules/palettes.yaml` already declares terrain (`Name: terrain`) and units/buildings (`Name: player`) as separate `PaletteFromFile` entries, even though both loaded from the same stock file before this change. Repointing only `terrain`'s `Filename` recolors terrain tiles and neutral scenery (trees/rocks, which render via the same `terrain` palette) without touching unit, building, or weapon-effect colors — those traits still load the unmodified stock `temperat.pal`. It also means zero risk to tile geometry/boundaries (the actual `.tem` sprite data is never touched, only the color each index maps to), sidestepping the exact risk `docs/ROADMAP.md`'s Phase 6 section calls out about individual tile-sprite edits.

**First iteration was too subtle to matter:** a straight port of the chrome pass's hue band (±25° from red) only touched 12% of the tileset atlas's pixels at low magnitude — barely perceptible once composited. Widened to a 45° band (verified against the actual stock palette dump, not guessed) to catch the dominant tan "clear ground" tone; this touches ~22% of pixels with a visually obvious result, confirmed via `utility.sh --dump-sheets` (the same composited sprite-sheet-plus-palette code path the live game renders through) diffed against a stock-palette render of the same tileset.

**Labels:** `phase:6`, `type:art`, `area:world`

**Phase:** 6 — World & UI Visual Identity Overhaul (see `docs/ROADMAP.md`, `docs/ART_DIRECTION.md`)

**Purpose:** `docs/ROADMAP.md`'s Phase 6 deliverables call for a reskinned temperate tileset with a "living, reclaimed industrial" look. This is a first pass toward that — same "programmatic first pass now, real artist pass later" approach issues #12/#13 used, adapted for terrain's palette-based rendering instead of per-sprite art.

**Scope:**
- Recolor the temperate tileset's terrain-only palette per the locked palette in `docs/ART_DIRECTION.md`, leaving tile geometry, water, and unit/building/effect colors untouched.
- Verify via the actual composited sprite-sheet render (`--dump-sheets`), not just the raw palette swatch, since what matters is how it looks once tiles are drawn.
- Out of scope: individual tile sprite/decoration art, cliffs/scenery actor sprites themselves (only their palette), live-client rendered verification with a real camera view (attempted twice now, still not completed — see below), the main-menu shellmap's own terrain (uses the `DESERT` tileset, but its own actor placements, not this palette-only pass's scope in the sense of a rendered-client check).

**Follow-up pass — snow and desert (same issue, same technique):**
- **Snow:** the temperate pass's exact recolor logic ported directly, no adjustments needed. Snow's dominant "clear ground" color (white/light gray, near-zero saturation) is never matched by the hue-based touch condition, so actual snow stays snow — only the exposed dirt/rock breaking through it shifts toward green. 79/256 palette entries changed, confirmed via `--dump-sheets` diffed against stock: cliff structure, water, and the snow itself all read correctly, with visible green moss/dirt patches where the stock render showed brown/olive.
- **Desert:** the direct port does not work and was caught before shipping, not after. Desert's dominant "clear ground" color sits inside the same warm hue band the recolor targets (unlike temperate/snow, where it's a minority accent) — a straight port turns the whole visible sand surface solid green, erasing the desert identity outright, confirmed visually via `--dump-sheets` (not just inferred from the entry count). A brightness-based taper was tried next and still read as "green field" — so much of what looks like sand spans a wide brightness range, not just the brightest highlight, that a gradual reduction still washed the whole surface. What actually worked: a hard brightness cutoff (`reskin_terrain_palette.py --max-value=0.5`) that recolors only entries at or below that value, leaving bright sunlit dune sand untouched and shifting only darker shadowed crevices/rock toward green. 54/256 entries changed; confirmed visually — desert still reads as desert, with a distinct, deliberate green accent in the low spots, not a wash.
- `reskin_terrain_palette.py` now takes an output filename and an optional `--max-value=N` hard cutoff as arguments, generalizing what was previously temperate-only, hardcoded logic.
- `rules/palettes.yaml`'s `PaletteFromFile@terrain-snow`/`@terrain-desert` now point at `sungrid-snow-terrain.pal`/`sungrid-desert-terrain.pal` respectively, same pattern as temperate's entry.

**Dependencies:** Builds directly on issue #17's engine-build/content-access recipe.

**Definition of done for this pass:** All three tilesets visibly read as recolored toward the locked palette when composited (verified via `--dump-sheets` diff against stock for each), with tile geometry, water, and non-terrain sprite colors unaffected, and each tileset's own biome identity (snow reads as snow, desert reads as desert) intact rather than replaced. **Met for the composited-sheet verification, for all three tilesets.** Not yet met, and attempted twice now without success: an actual live-client screenshot with a real camera view — Xvfb + a quick-loaded skirmish, including a longer stabilization wait on the second attempt to rule out a timing issue. Sidebar/minimap chrome render correctly both times; the world viewport is fully black regardless of wait time, because the no-bots `Launch.Map` quick-load path (`ServerType.Local`, not `Skirmish`) places no starting units anywhere on the map, so there's no vision/shroud-clearing at all — not a rendering defect, and not something more patience fixes. Confirming this needs the documented `Launch.SkirmishBots` engine patch from `docs/PLAYTESTING.md` (a real, if temporary, C# addition to the gitignored `engine/`), which is a large enough undertaking that it's better scoped as its own follow-up than folded into another attempt at this issue.

---

### 19. GitHub Actions turns out not to be disabled — first real CI run found and fixed 4 latent bugs

**Status:** Issue #17 flagged "CI has never actually run — worth confirming whether Actions is disabled repo-wide" as an open question. It wasn't disabled: a docs-only PR (#27) that happened to also touch `mod.config` and `.github/workflows/ci.yml` (outside `ci.yml`'s `paths-ignore: '*.md'` filter) triggered the very first Continuous Integration run in this repo's history, on both the Linux and Windows jobs. It found real problems immediately:

- **4 analyzer errors** in `OpenRA.Mods.Sungrid/GridReserve/` (Phase 3/4 code, never compiled by anything but a manual one-off before — see issue #17): an unused `using OpenRA.Network;` in `GridReserveController.cs`, unused `using OpenRA.Traits;` in both `GridReserveHudLogic.cs` and `GridReserveStandingsLogic.cs` (`IDE0005`), and a manual `bool` field plus expression-bodied getter in `GridReserveController.cs` that should be an auto-property (`IDE0032`). Fixed by removing the dead imports and converting `Enabled` to `public bool Enabled { get; private set; }`.
- **45 rules/map validation errors** (`make test`), all pre-existing content bugs invisible until `--check-yaml`/map-testing actually ran for the first time:
  - `rules/misc.yaml`'s Soviet heavy-squad crate reward and all three `rules/ai.yaml` `UnitBuilderBotModule` tiers still referenced the removed `e4` (Flame Infantry, replaced by `disr`/Disruptor Trooper in issue #14) — that rename's own notes claimed every reference was updated, but crate rewards and AI unit-composition weights were missed. Fixed: `e4` → `disr` in both files.
  - `SGDRN` (Drone Bay)'s `Prerequisites` referenced `oilb` — not a dangling id (a civilian neutral oil-derrick prop actor genuinely named `OILB` still exists on many maps), but the wrong id: it doesn't have a `Buildable` trait, so it can never satisfy a prerequisite. The actual Recycling Depot (renamed `OILB`→`RCYD` specifically to avoid colliding with this civilian prop, per an earlier fix referenced in issue #17) was the evident intended target. Fixed: `oilb` → `rcyd`.
  - `SGTUR` (Grid Defense Turret) and `SGREL` (Smart Grid Relay) both listed `powr` (Solar Array's actor id) as a prerequisite, but `POWR`/`APWR` both carry a `ProvidesPrerequisite: Prerequisite: anypower` trait, which replaces rather than supplements the default auto-provided own-id prerequisite — so `powr` was never actually satisfiable, and every other power-gated building in the ruleset already correctly requires `anypower` instead. Fixed: `powr` → `anypower` in both.
- Confirmed a real, previously undocumented SDK-patch-version divergence beyond issue #17's `CryptoUtil` finding: CI's `actions/setup-dotnet@v5`-installed SDK (`8.0.422`) does not hit that `CryptoUtil.SHA1Hash([])` ambiguity at all (the engine step built clean, 0 warnings/0 errors, no workaround needed) — it's specific to newer patch versions like the apt-installed `8.0.128` used in issue #17's manual verification. The reverse also showed up: a local `dotnet build -c Debug -warnaserror` against the same commit under `8.0.128` reported ~921 `IDE0055` formatting errors across vendored `engine/` source that CI's `8.0.422` never flags at all. Local verification under a different SDK patch version is not a reliable stand-in for CI's actual result in either direction.

**Labels:** `type:bug`, `type:content`, `type:engine`

**Phase:** Not tied to a specific roadmap phase — cross-cutting correctness fixes surfaced by CI running for the first time.

**Purpose:** Resolves issue #17's open "is CI actually disabled" question (no — it just hadn't been triggered by anything since `paths-ignore` skips markdown-only changes and every prior PR happened to stay within that filter), and fixes every defect that first real run surfaced rather than treating a suddenly-working safety net as someone else's problem.

**Scope:**
- Fix the 4 analyzer findings and 45 rules/map validation errors listed above.
- Document that CI actually works and was never disabled.
- Out of scope: auditing for further latent bugs beyond what this one CI run surfaced (a full audit would need deliberately re-running CI against every historical PR, which is disproportionate); the `ENGINE_VERSION`/SDK-patch-version RFC issue #17 already flagged, still open.

**Dependencies:** None blocking.

**Definition of done:** CI green on both Linux and Windows jobs for a real PR. **Met** — confirmed via the actual re-triggered CI run (both jobs completed with conclusion `success` on PR #27), not just the local `utility.sh --check-yaml` verification (also clean) that preceded it. `docs/BACKLOG.md`'s and `CLAUDE.md`'s "CI has never run" language is now stale and updated accordingly.

---

### 20. RFC: Re-pin ENGINE_VERSION to a patched commit fixing the CryptoUtil ambiguity — APPROVED AND IMPLEMENTED

**Problem:** `mod.config`'s `ENGINE_VERSION` is pinned to `bf4102a029f132824d682069fce1105d56fc5e96`. That exact commit fails to compile under some `.NET 8` SDK patch versions with a `CS0121` ambiguous-overload error (`CryptoUtil.SHA1Hash([])` — the empty collection expression matches both the `byte[]` and `string` overloads). Confirmed behavior:
- Fails under `8.0.128` (installable via `sudo apt-get install -y dotnet-sdk-8.0` on Ubuntu/Debian — a completely ordinary, likely-common local setup path).
- Builds clean under `8.0.422` (what `actions/setup-dotnet@v5` currently resolves to on GitHub's hosted runners, hence CI itself has never hit this — see issue #19).

This means the project currently only "works" by accident of which exact SDK patch version happens to be installed, with no visible error message pointing at the cause. Anyone building locally with a newer/different patch than CI's is likely to hit a hard, confusing compile failure on their very first `make`.

**Why this needs an RFC:** Any `ENGINE_VERSION` change is `type:engine` per `docs/CONTRIBUTING.md`'s RFC workflow, gated on a design issue before implementation — this is that issue.

**Proposed solution (validated, not just theorized):** Pin to a single cherry-picked fix on top of the exact same commit, rather than bumping to a newer upstream commit.

- No external fork needed: `richardkfm/sungrid-protocol` started as a direct fork of the OpenRA engine, and `bf4102a...` — the exact pinned commit — is still fully present in this repo's own history (it's an ancestor of `main`, even though the old `bleed` branch pointer that used to name it directly was deleted per issue #17's cleanup).
- A new branch, `engine-patch/bf4102a-cryptoutil-fix`, starts at that exact commit and adds one line on top (commit `83c2b72`): `CryptoUtil.SHA1Hash([])` → `CryptoUtil.SHA1Hash(Array.Empty<byte>())`, unambiguously resolving to the `byte[]` overload with identical behavior.
- Verified end-to-end: the commit's GitHub archive URL (`https://github.com/richardkfm/sungrid-protocol/archive/83c2b72.../zip`) downloads successfully, and the resulting tree builds with **0 warnings, 0 errors** under `8.0.128` — the exact SDK version that fails against the current pin.

**Concrete change, if approved:**
```
mod.config:
  ENGINE_VERSION="83c2b72eec1ec493b9ed6e6b631bbab7f270929a"
  AUTOMATIC_ENGINE_SOURCE="https://github.com/richardkfm/sungrid-protocol/archive/${ENGINE_VERSION}.zip"
```
(`AUTOMATIC_ENGINE_SOURCE` currently hardcodes `OpenRA/OpenRA`'s archive URL — it needs to point at this repo instead, since that's where the patched commit lives.)

**Risk assessment:** Effectively zero behavioral drift. The change is a single disambiguating call rewrite with identical runtime output — not a real engine upgrade, and none of the months of intervening upstream OpenRA history that a genuine version bump would drag in (which could break the Grid Reserve traits and Phase 5 building YAML written against this exact commit's API surface, per `docs/ARCHITECTURE.md`'s original rationale for pinning in the first place).

**Alternatives considered:**
1. **Do nothing.** CI (`8.0.422`) isn't affected, so merges keep working. Rejected as the primary fix: leaves every future local contributor to rediscover this exact failure with no clear error pointing at the cause, indefinitely.
2. **Document the workaround only** (already partly done in `docs/PLAYTESTING.md`, from issue #17's investigation). Zero risk, zero engineering cost, but doesn't fix the underlying fragility — still requires an active memory of "go read that one subsection" the first time someone hits it cold.
3. **Bump `ENGINE_VERSION` to a current upstream commit.** Rejected for now: solves this one bug but reintroduces the exact migration-risk tradeoff `docs/ARCHITECTURE.md` deliberately avoided by pinning — real API drift across months of upstream changes, needing a full re-validation pass across Grid Reserve and the Phase 5 building roster. Disproportionate for a one-line compile fix; could be revisited separately if there's ever a reason to track upstream more closely.
4. **Pin to a personal fork of `OpenRA/OpenRA` itself**, per `docs/ARCHITECTURE.md`'s originally-stated fallback for engine-level friction points. Works, but needs a separate repo to own and maintain — strictly more overhead than option in "Proposed solution" above for the same one-line result, now that it's confirmed this repo's own history already contains everything needed.

**Labels:** `type:engine`, `type:design`, `risk:scope-trap`

**Phase:** Not tied to a specific roadmap phase — cross-cutting build-tooling fix.

**Scope:**
- Decision needed: approve the re-pin above, or direct a different approach (see alternatives).
- If approved: update `mod.config`'s `ENGINE_VERSION`/`AUTOMATIC_ENGINE_SOURCE` in a follow-up PR, confirm `fetch-engine.sh` still resolves/builds correctly against the new source, and remove or update the now-resolved workaround note in `docs/PLAYTESTING.md`.
- Out of scope: any actual upstream engine version bump (alternative 3 above); creating/maintaining a separate personal fork repo (alternative 4).

**Dependencies:** None blocking. Builds on issue #17's verification and the `engine-patch/bf4102a-cryptoutil-fix` branch already pushed.

**Definition of done:** A recorded decision (approve the re-pin, or an explicit alternative) — this RFC issue is about the decision, not the implementation. **Met** — approved. Implemented: `mod.config`'s `ENGINE_VERSION`/`AUTOMATIC_ENGINE_SOURCE` now point at the patched commit per "Concrete change" above. Verified via the real `fetch-engine.sh`/`make` flow (not a manual workaround) under `8.0.128` — the exact SDK version that failed against the old pin — with 0 warnings/0 errors.

**One real wrinkle during implementation, worth recording:** a PR was opened attempting to merge `engine-patch/bf4102a-cryptoutil-fix` directly into `main` (rather than just re-pointing `mod.config` at it). That's not how this is meant to work, and it doesn't merge cleanly: the branch is a snapshot of the *pre-SDK-migration* engine tree (`OpenRA.Game/`, etc. at the repo root, matching commit `bf4102a`'s original layout), while `main`'s own history deleted all of those root-level files as part of the SDK migration (engine content becomes a gitignored fetched dependency, not vendored source). Merging the two produces a modify/delete conflict on `Map.cs`, and force-resolving it in favor of the incoming side would resurrect the entire old engine tree as committed files in `main` — exactly what the Mod SDK pattern exists to avoid. That PR was closed unmerged. `engine-patch/bf4102a-cryptoutil-fix` is not meant to ever merge into `main` — it exists solely as a fetch target, downloaded by commit SHA via its GitHub archive URL, the same way `OpenRA/OpenRA` was downloaded from before.

---

### 21. Windows packaging job fails: missing `wine32`/multiarch breaks `rcedit` version-stamping — FIXED

**Problem:** The user manually pushed the `alpha1` tag to test `packaging.yml`'s release flow. The Linux AppImage job succeeded (and is confirmed the correct downloadable artifact: `SungridProtocol-alpha1-x86_64.AppImage`), but the Windows Installers job failed, and the macOS Disk Image job never started (stuck `queued`, `runner_id: 0` — a GitHub-hosted `macos-13` runner availability/queueing issue, not a repo config problem; no action taken here).

**Root cause (confirmed from the actual job log, not guessed):** `packaging/windows/buildpackage.sh` builds the Windows launcher `.exe` successfully, then shells out to `wine64 rcedit-x64.exe ... --set-product-version ...` to stamp version metadata and the icon onto it. The workflow's `Prepare Environment` step only installed `nsis wine64`. Wine's own first-run output says exactly what's wrong:
```
it looks like wine32 is missing, you should install it.
multiarch needs to be enabled first.  as root, please
execute "dpkg --add-architecture i386 && apt-get update &&
apt-get install wine32"
```
Ubuntu 22.04's distro-packaged `wine64` (6.0.3~repack) still depends on the `wine32`/i386 multiarch component for its own registry/config initialization, even to run a 64-bit-only tool like `rcedit-x64.exe`. Without it, Wine's first-run config bootstrap fails partway through, `rcedit` gets fed a broken/empty environment, and crashes immediately with `Fatal error: Unable to parse version string for ProductVersion` (exit code 1) — a downstream symptom of the missing dependency, not a bug in the version string itself.

**Fix:** `.github/workflows/packaging.yml`'s Windows job now runs `sudo dpkg --add-architecture i386` before `apt-get update`, and installs `wine32 wine64` (not just `wine64`).

**Scope:** This one workflow file, one job. Out of scope: the macOS job's `queued` stall (looks like GitHub-hosted macOS runner capacity, not a repo bug — worth a retry, not a config change); a real second release-tag test to confirm the fix end-to-end (needs another manual tag push from the user, since this session can't push tags/trigger releases itself without being asked).

**Dependencies:** None.

**Definition of done:** `packaging.yml` installs `wine32` alongside `wine64` for the Windows job. **Met.** Full green confirmation (re-running the release workflow against a new tag) is still pending — that's the user's call on when to cut the next test tag.

**Labels:** `type:build`, `type:ci`

**Phase:** Cross-cutting build-tooling fix (release packaging, not tied to a specific content phase).

---

### 22. Datacenter for AI and Drone Bay had no real tech-tree/logistics identity — FIXED

**Problem:** Design review of the two Phase 5 buildings found that despite their names and flavor text, neither did what it implied. `SGDAI` ("Datacenter for AI... battlefield analytics") only trickled a little cash and gave vision/cloak detection — it had the standard auto-provided `sgdai` prerequisite id, but nothing in the ruleset actually required it, so it never functioned as a tech gate the way `dome`/`atek`/`stek` do. `SGDRN` ("Drone Bay... autonomous delivery drones") produced no drones at all — it was purely a `ProximityExternalCondition` vehicle speed aura, a deliberate Phase 5 descope noted in `docs/BUILDINGS.md` at the time.

**Fix:**
- `SGDAI` is now a real tech gate: `PDOX` (Chronosphere), `IRON` (Iron Curtain), and `MSLO` (Missile Silo) all require `sgdai` in addition to their existing `atek`/`stek`/`techcenter` + `~techlevel.unrestricted` gates.
- `SGDRN` gained `Production`/`Exit`/`RallyPoint` traits (Vehicle queue), mirroring `WEAP`'s existing pattern, and now builds a new unit: `SGDRO` ("Recon Drone") in `mods/sungrid/rules/vehicles.yaml` — a fast, unarmed, wide-vision scout, `Inherits: ^Vehicle`, reusing `JEEP`'s sprite (`RenderSprites.Image: jeep`) per the same placeholder-art-reuse precedent as the rest of the Phase 5 roster. `SGDRO` requires both `sgdrn` and `sgdai`, so the AI Data Center is literally what unlocks the Drone Bay's drone production — tying the two buildings' fantasies together.
- The existing `CashTrickler`/`RevealsShroud`/`DetectCloaked` on `SGDAI` and the speed aura on `SGDRN` were kept as-is rather than removed, so the buildings still fill their original economy/logistics role in addition to the new gating role.
- Fluent descriptions for `actor-sgdai` and `actor-sgdrn` updated to mention the new tech-gate/production relationship; `actor-sgdro` added.

**Scope:** `mods/sungrid/rules/structures.yaml` (`SGDAI`, `SGDRN`, `PDOX`, `IRON`, `MSLO`), `mods/sungrid/rules/vehicles.yaml` (new `SGDRO`), `mods/sungrid/fluent/rules.ftl`. No new C# — same stock-trait-composition approach (`Production`, `Exit`, `RallyPoint`) already used by `WEAP`/`HPAD`.

**Verification:** Could not run `make test` (`./utility.sh --check-yaml`) in this environment — no fetched engine/`dotnet` available, the same constraint noted in issue #11. Manually verified: tab-consistent indentation matching surrounding YAML, no actor id collisions (`SGDRO` is unique), and every new `Prerequisites:` reference (`sgdai`, `sgdrn`) resolves to an actual actor definition. **A real engine build/YAML-check and a human playtest are both still needed post-merge** — same outstanding gap as the rest of the Phase 5 roster.

**Labels:** `type:content`, `type:balance`, `area:economy`, `area:logistics`, `area:intelligence`

**Phase:** 5 — Faction Flavor (follow-up correction to the original roster).

---

### 23. Recon Drone (SGDRO) drove on wheels — FIXED, now an actual flying unit

**Problem:** Issue #22's `SGDRO` ("Recon Drone", built from the Drone Bay) was implemented as a ground vehicle (`Inherits: ^Vehicle`, reusing `JEEP`'s sprite) — the fastest way to get "a drone gets built" working, but a drone that drives on wheels doesn't match the fantasy at all.

**Fix:** `SGDRO` moved from `mods/sungrid/rules/vehicles.yaml` to `mods/sungrid/rules/aircraft.yaml` and is now `Inherits: ^Helicopter`. Every existing flying unit in the roster is either an armed combat helicopter (`HELI`/`HIND`/`MH60`), a jet (`MIG`/`YAK`), or `TRAN` (Chinook transport, the only unarmed and fully-buildable helicopter) — no small "scout drone" sprite exists to reuse. `U2` ("Spy Plane") is the closer thematic match but is structurally unsuited: it's a `^NeutralPlane`-based, non-`Buildable` actor spawned only by a support power, with `-Selectable`/`-Voiced` stripped and no VTOL/hover — reusing it would mean undoing most of its overrides. `TRAN` was the better donor: already unarmed, already `^Helicopter`-based, so `SGDRO` reuses its sprite (`RenderSprites.Image: tran`), rotor animation overlays, and husk, but with stats scaled down (`HP: 6000` vs. `TRAN`'s 14000, `Speed: 170` vs. 128, `Cost: 500` vs. 900, no `Cargo`) and `RevealsShroud` widened (`Range: 10c0`) for a recon role. `SGDRN` (Drone Bay) now mirrors `HPAD`'s aircraft-production block (`Exit@1` geometry, `RallyPoint: ForceSetType: Helicopter`, `Production: Produces: Aircraft, Helicopter`, `Reservable`, `ProductionBar`) instead of `WEAP`'s vehicle one, since `SGDRN` already reuses `HPAD`'s sprite/footprint.

**One real wrinkle avoided, worth recording:** issue #22's own follow-up fix (commit `c434a83`) had already broken CI once by referencing a `notmobile` condition nothing granted. Before writing this version, the `^Helicopter`/`^Plane`/`^NeutralPlane` inheritance chain (`mods/sungrid/rules/defaults.yaml:587-687`) was checked to confirm exactly which conditions it grants (`airborne`, `cruising`) — `SGDRO` only references those plus `being-captured` (granted by the base `CaptureManager`), and does not reference `notmobile` anywhere.

**Scope:** `mods/sungrid/rules/aircraft.yaml` (new `SGDRO`), `mods/sungrid/rules/vehicles.yaml` (old `SGDRO` removed), `mods/sungrid/rules/structures.yaml` (`SGDRN`'s production block). No fluent text changes needed — `actor-sgdro`'s existing description never implied ground movement. No new C#, no new art.

**Verification:** Same constraint as issue #22 — no engine/`dotnet` available in this sandbox, so `make test` couldn't run locally; CI on the pushed branch is the first real check. Manually verified: every `RequiresCondition`/`PauseOnCondition` on the new block resolves to a condition actually granted in the inheritance chain, `SGDRN`'s `Production: Produces:` list matches `SGDRO`'s `Buildable: BuildAtProductionType: Helicopter`, `TRAN.Husk` (referenced by `SpawnActorOnDeath`) exists, and `SGDRO` is defined exactly once across the ruleset. **A real engine build/YAML-check and a human playtest are both still needed post-merge.**

**Labels:** `type:content`, `area:logistics`

**Phase:** 5 — Faction Flavor (second follow-up correction to the Drone Bay/AI Data Center pairing).
### 23. Windows packaging still fails after issue #21's fix: `rcedit` version string, not `wine32`, was the real cause — FIXED

**Problem:** The user cut the `alpha2` release tag expecting issue #21's `wine32` fix to have resolved Windows packaging. It didn't: the `Windows Installers` job on the real `alpha2` run failed with the exact same crash as `alpha1` — `Fatal error: Unable to parse version string for ProductVersion` — even though `wine32` was installed correctly this time (confirmed in the job log: `wine32:i386` sets up cleanly, no multiarch complaint). The Linux AppImage job succeeded again, producing `SungridProtocol-alpha2-x86_64.AppImage`; the macOS job stayed stuck `queued` (same pre-existing GitHub-hosted `macos-13` capacity issue as before, unrelated to this repo — still out of scope).

**Root cause (confirmed from the actual `alpha2` job log — issue #21's `wine32` diagnosis was an incorrect guess, made without a second data point):** `packaging/windows/buildpackage.sh` builds a "backwards" version string for `rcedit --set-product-version` because rcedit's version parser (`parse_version_string` in electron/rcedit, confirmed from its source) rejects any string that doesn't start with a digit — it's just `swscanf_s(str, "%hu.%hu...")` chains, no fallback for a letter-led string. The swap logic is:
```sh
TAG_TYPE="${TAG%%-*}"
TAG_VERSION="${TAG#*-}"
BACKWARDS_TAG="${TAG_VERSION}-${TAG_TYPE}"
```
This only produces a digit-led string when `TAG` has a `type-version` shape like `release-20240101` (giving `20240101-release`). This repo's actual release tags are `alpha1`/`alpha2` — no dash — so `${TAG%%-*}` and `${TAG#*-}` both leave `TAG` unchanged, and `BACKWARDS_TAG` becomes `alpha2-alpha2`: still letter-led. rcedit rejects it immediately, before doing anything wine/multiarch-related. Installing `wine32` (issue #21) fixed a real but unrelated warning in the same log region and made no difference to this crash — the `alpha2` run proves it.

**Fix:** `packaging/windows/buildpackage.sh` now detects the no-dash case (`TAG_TYPE == TAG_VERSION` after the swap) and falls back to a synthetic digit-led string (`0-${TAG}`) instead of producing a letter-led one. Tags that do follow the `type-version` shape (`release-*`, `playtest-*`, `devtest-*`) are unaffected and keep the original backwards-swap behavior.

**Scope:** `packaging/windows/buildpackage.sh` only. Out of scope: the macOS `queued` stall (unrelated, pre-existing, GitHub-hosted runner capacity — not a repo config problem); renaming the `alpha1`/`alpha2` tag convention itself (the fix makes the script tolerate the existing convention rather than requiring the tags to change).

**Dependencies:** Builds on / corrects issue #21. `wine32` should stay installed — it's still needed for wine's own bootstrap — this just wasn't the blocking bug.

**Definition of done:** `BACKWARDS_TAG` is guaranteed to start with a digit for both dashed (`release-20240101` → `20240101-release`) and non-dashed (`alpha2` → `0-alpha2`) tags — verified locally by running the substitution logic standalone. **A real release-tag push is still needed to confirm green end-to-end** (this session can't push tags itself); that's the same outstanding verification gap issue #21 also left open, now with the actual bug fixed underneath it.

**Labels:** `type:build`, `type:ci`

**Phase:** Cross-cutting build-tooling fix (release packaging, not tied to a specific content phase).

---

### 24. Drones were unarmed/faction-neutral — gave each faction its own, balanced

**Problem:** Issue #23 made `SGDRO` ("Recon Drone") an actual flying unit, but left it unarmed, faction-neutral, and only moderately fragile (`HP: 6000`, cost 500) — not the cheap, weakly-armed, very-fragile asymmetric harasser the fiction implied, and with no faction identity behind it.

**Fix:**
- `SGDRN` (Drone Bay) is now Assembly-exclusive: `~structures.soviet` added to its `Buildable.Prerequisites`, matching the exact idiom `AGUN`/`SAM` already use. `SGDRO` needed no direct faction tag — it's transitively gated once only the Assembly can build `sgdrn`, the same relationship `TRAN`/`HELI` have to the Consortium-exclusive `HPAD`. Doc research (`docs/BACKLOG.md` issue #15's "scarcity-adapted, improvisational" characterization of The Assembly vs. The Consortium's "capital/technocratic" one, plus `docs/ART_DIRECTION.md`'s unassigned "decentralized/drone-based" faction axis) supports this assignment.
- `SGDRO` tuned down: `Cost: 500 → 350`, `HP: 6000 → 3000`, armed with a new weak weapon `DroneRocket` (`mods/sungrid/weapons/missiles.yaml`, `Inherits: ^AntiGroundMissile`, `Burst: 2` small rockets at `Damage: 700` each, slower `ReloadDelay: 80` than any existing ground missile) via `Armament`/`AttackAircraft`.
- Added a Consortium counterpart, `SGDRS` ("Strike Drone", `mods/sungrid/rules/aircraft.yaml`), built from the existing Consortium-exclusive `HPAD` rather than a new building (`Prerequisites: ~hpad, sgdai, ~techlevel.high`, mirroring `SGDRO`'s `sgdrn, sgdai, ~techlevel.high` structure). Reuses `MH60`'s (Black Hawk) sprite/rotor-overlay/husk rather than `TRAN`'s, so it reads as visually distinct. Pricier (`Cost: 600`) and slightly harder-hitting (new weapon `DroneRocket.Strike`, `Inherits: DroneRocket` with `Damage: 950`) than the Assembly's drone, but kept close rather than a different tier, and still `Armor: Type: Light` / low `HP: 3500` — "still very easy to take down," per the request.
- No new dedicated counter unit was added on either side: both drones stay `Light`-armored, and the existing faction-neutral `E3` Rocket Soldier (300 cost, `RedEye` weapon does 100% damage versus `Light`) already answers either one decisively, as does each side's own `AGUN`/`SAM` AA structure.
- Fluent text updated for `actor-sgdrn`/`actor-sgdro`; `actor-sgdrs` added.

**Scope:** `mods/sungrid/rules/structures.yaml` (`SGDRN`), `mods/sungrid/rules/aircraft.yaml` (`SGDRO` tuned, new `SGDRS`), `mods/sungrid/weapons/missiles.yaml` (new `DroneRocket`/`DroneRocket.Strike`), `mods/sungrid/fluent/rules.ftl`. No new C#, no new building, no new art (both drones reuse existing helicopter sprites).

**Verification:** Same constraint as issues #22/#23 — no engine/`dotnet` available in this sandbox, so `make test` couldn't run locally; CI on the pushed branch is the first real check. Manually verified: `SGDRS`/`DroneRocket`/`DroneRocket.Strike` don't collide with existing ids, `SGDRN`'s new `~structures.soviet` tag doesn't drop its existing `proc`/`rcyd` prerequisites, both `Armament.Weapon` references resolve, `MH60.Husk` (referenced by `SGDRS`'s `SpawnActorOnDeath`) exists, and `SGDRS`'s single-pair `WithIdleOverlay@ROTORAIR`/`@ROTORGROUND` block matches `MH60`'s own pattern (not `TRAN`/`SGDRO`'s dual-rotor one). **A real engine build/YAML-check and a human playtest (balance feel, not just correctness) are both still needed post-merge.**

**Labels:** `type:content`, `type:balance`, `area:logistics`

**Phase:** 5 — Faction Flavor (third follow-up correction to the Drone Bay/AI Data Center pairing).

---

### 25. Shellmap APC still dropped `e4` — third missed reference from issue #14's rename — FIXED

**Problem:** A real-build playtest reported seeing the game's Solar Array buildings (expected) but no new units, and Flame Infantry still present — despite issue #14 replacing it with `DISR` (Disruptor Trooper). `mods/sungrid/maps/desert-shellmap/rules.yaml`'s `APC` override still had `Cargo.InitialUnits: e1, e1, e2, e3, e4` — a third leftover reference to the removed `E4` actor in the very same file, distinct from the two already caught and fixed in the same rename: the `ParatroopersPower.DropItems` line 11 lines below it (fixed in #14 itself) and the six `ftur` map-actor placements in the sibling `map.yaml` (fixed in #16). This `InitialUnits` line sits in the shellmap's own `APC`'s passenger list — the animated main-menu background battle — so it's exactly the kind of thing a player would notice within seconds of launching the game, and exactly the kind of reference `--check-yaml`/`make test` should catch as a dangling actor id.

**Fix:** `e4` → `disr` in that one line, matching the lowercase-id convention the rest of the `InitialUnits` list already uses (`e1, e1, e2, e3`).

**Root cause:** Three independent references to the same removed actor id, spread across two files, all introduced or left behind by the same rename. Each was found and fixed in a separate pass (#14 itself, #16, and now this one) rather than all at once — grepping for a bare `e4`/`E4` token across `mods/sungrid` (not just the specific lines the original commit message called out) would have caught all three at once.

**Labels:** `type:bug`, `type:content`

**Phase:** Not tied to a specific roadmap phase — follow-up correctness fix to issue #14.

**Verification:** Confirmed via a full-repo grep for bare `e4`/`E4`/`ftur`/`FTUR` tokens across `mods/sungrid/**/*.yaml` (excluding compiled `.oramap` binaries and the legitimate `e4.shp`/`ftur.shp` art-filename reuse noted in #14) — no remaining dangling references. No engine/`dotnet` available in this sandbox, so `make test`/a real client launch couldn't be run locally; CI and a human playtest on the pushed branch are the real checks.

---

### 26. Energy economy rebalance, faction power identity, and Ant/Zombie replacement

**Problem:** Power was too easy to solve once — `APWR` (Advanced Solar Array) was a strictly better
power-per-credit investment than `POWR` (Solar Array), and `SGDAI` (Datacenter for AI) drained only -60 power
with zero power-state interaction despite gating both factions' drone units. Both factions also shared a
single universal power building line with no faction-specific identity, and the Consortium's Strike Drone
(`SGDRS`) was bolted onto the Helipad rather than getting its own dedicated Drone Bay like the Assembly's
`SGDRN`. Separately, the neutral capturable "Bio-Research Lab" (`bio` prerequisite, used by the `chernobyl`
map's Creeps player) unlocked literal `Zombie`/`Ant` units — classic "It Came from Red Alert" B-movie
easter-egg content that reads as 90s filler rather than fitting the grid-contamination tone.

**Fix:**
- `APWR.Valued.Cost`: 500 → 1000 (power stays +200) — flips it from a strict upgrade into a real tradeoff.
- `SGCRY` (Cryptominer): `Power.Amount` -120 → -150; `GrantConditionOnPowerState@STRAINED.ValidPowerStates`
  `Low` → `Low, Critical`, closing a gap where income silently dropped to 0 instead of the intended reduced
  rate at Critical power.
- `SGDAI` (Datacenter for AI): `Power.Amount` -60 → -140; added `GrantConditionOnPowerState@NORMAL`/`@STRAINED`
  (matching `SGCRY`'s pattern) gating a new split `CashTrickler@NORMAL`/`@STRAINED` (20→8/tick) and
  `DetectCloaked` (`RequiresCondition: grid-normal` — cloak detection cuts out entirely below Normal power).
- `SGDRO`/`SGDRS`: added `GrantConditionOnPowerState@NORMAL`/`@STRAINED` on each drone itself (confirmed via
  this repo's own pre-SDK-migration git history that the trait only needs `Owner.PlayerActor`, not a
  `Building`, so it works on aircraft) gating their own `Armament.RequiresCondition` — drones lose their
  weapons fleet-wide once their owner's grid drops to Critical power, not just those near a building.
- Two new faction-exclusive power buildings in `structures.yaml`: `SGWND` ("Wind Turbine Array", Assembly —
  cheap/early/fragile: `Cost: 400`, `Power: +70`, `HP: 30000`, `~techlevel.low`) and `SGHYD` ("Hydrogen Plant",
  Consortium — expensive/late/hardened: `Cost: 1200`, `Power: +350`, `HP: 90000`, `Armor: Heavy`,
  `dome, atek, ~techlevel.high`). Both additive alongside `POWR`/`APWR`, not replacements.
- New `SGDRA` ("Aerial Fabrication Bay", Consortium) mirrors `SGDRN` mechanically with faction-flipped
  prerequisites; `SGDRS.Buildable.Prerequisites` moved from `~hpad, sgdai` to `sgdra, sgdai`.
- `Zombie`/`Ant`/`FireAnt`/`ScoutAnt`/`WarriorAnt` and the `bio` neutral building reflavored in place (actor
  ids and the `bio` prerequisite token unchanged — `desert-shellmap/rules.yaml` overrides `Ant`'s
  prerequisites directly and the `chernobyl` map references the neutral actor by id): `Zombie` → "Blighted",
  `Ant` line → "Swarmling"/"Cinderling"/"Scoutling"/"Bulwarkling", `bio` → "Containment Ruins". Same
  "reskin the fluff, keep the chassis" pattern as issue #14's Flame Infantry → Disruptor Trooper.
- Full rationale, exact numbers, and a suggestions-only list of further Phase 7 reskin candidates (not
  implemented in this pass) written up in the new `docs/ENERGY_BALANCE.md`.

**Scope:** `mods/sungrid/rules/structures.yaml` (`APWR`, `SGCRY`, `SGDAI` retuned; new `SGWND`, `SGHYD`,
`SGDRA`), `mods/sungrid/rules/aircraft.yaml` (`SGDRO`/`SGDRS` power gating, `SGDRS` prerequisites),
`mods/sungrid/fluent/rules.ftl` (new/updated fluent for all of the above plus `actor-zombie`/`actor-ant`/
`actor-bio`), `docs/BUILDINGS.md`, `docs/ENERGY_BALANCE.md` (new), `docs/concept-art/faction-roster-dossier.html`.
No new C#, no new art (new buildings reuse existing placeholder sprites per the established Phase 5
convention; Ant/Zombie keep their existing sprites).

**Verification:** No engine/`dotnet` available in this sandbox, so `make test`/a real client launch couldn't
be run locally; CI's rules/map validator (confirmed active per issue #19) is the primary correctness gate on
the pushed branch. Manually grepped for every new/changed actor id and prerequisite token (`SGWND`, `SGHYD`,
`SGDRA`, `sgdra` replacing `hpad` on `SGDRS`) across `mods/sungrid/` to confirm nothing else referenced the
old wiring, and cross-checked every `GrantConditionOnPowerState`/`RequiresCondition` condition-name pair for
exact string matches (a mismatch is a silent no-op, not a CI error). **A human playtest for balance feel is
still needed post-merge — this pass is untested for actual match-length energy pressure and faction parity.**

**Labels:** `type:balance`, `type:content`, `area:economy`

**Phase:** Not tied to a specific roadmap phase — a rebalance/faction-identity pass following up on the
Phase 5 building roster.

---

### 27. Phase 7 first wave: three unit renames, and an honest map of what's still blocked

**Problem:** `docs/ENERGY_BALANCE.md`'s "Phase 7 reskin candidates" section listed several 90s-style unit
names as suggestions only. `docs/ROADMAP.md` flags Phase 7 (core unit/vehicle sprite and audio identity) as
not started and as the roadmap's biggest scope-creep risk ("no natural stopping point... cap scope to the
core skirmish roster before declaring the phase done") — so the goal here was to turn a few of those
suggestions into an actual scoped, capped, low-risk first wave rather than attempt the whole phase at once.

**Fix:**
- Renamed three units via `mods/sungrid/fluent/rules.ftl` (plus one matching update in `chrome.ftl`) —
  `V2RL` "V2 Rocket Launcher" → "Surge Rocket Launcher", `QTNK` "MAD Tank" → "Tremor Tank" (matches its
  existing seismic mechanic), `U2` "Spy Plane" → "Recon Plane" (matches the mod's existing recon vocabulary —
  Sensor Array, Recon Drone). Also updated the `SpyPlane` support power's own display name
  (`.airstrikepower-spyplane-name`) and its two mentions inside `AFLD`'s description text, the `U2` husk name,
  and `chrome.ftl`'s deploy-tooltip line that named "MAD Tanks."
- Confirmed all three are faction-general (no `~vehicles.<sub-faction>` gate) before touching them — this
  was a deliberate filter, not an oversight: `TTNK` (Tesla Tank, Russia-gated) and `DTRK` (Demolition Truck,
  Ukraine-gated) were also strong candidates but are exactly the kind of real-world-coded sub-faction special
  unit issue #15 flagged as "a separate, larger creative decision... shouldn't be assumed." Asked the user
  directly whether to include them; they confirmed **defer**. `CTNK` (Chrono Tank, Germany-gated) was left
  alone for the same reason without needing to ask again, same category.
- None of the three renamed units needed a weapon/warhead change (unlike the `DISR`/`ARCT` precedent from
  issue #14) — their underlying mechanics already fit the setting, only the literal real-world Cold War names
  were the clash. So the entire change is confined to fluent text: no `rules/*.yaml`, no `sequences/*.yaml`,
  no new weapon file, no actor id change.
- Documented what's genuinely blocked rather than pretending it's done: core roster sprite work
  (`E1`/`E2`/`E3`, `1TNK`–`4TNK`) and the announcer voice/ambient music pass need real new art or audio
  assets, or a locked generation pipeline — neither exists yet. `docs/ART_DIRECTION.md`'s asset-pipeline note
  requires sprite resolution/frame conventions/a shared palette file to be locked before art work starts, and
  there's no image-generation tooling in this environment that could produce game-ready indexed-palette
  sprite sheets matching OpenRA's frame/facing conventions. Recommended a `type:design` RFC (per
  `docs/CONTRIBUTING.md`'s workflow) to settle the pipeline question before any of that work starts, rather
  than attempting it blind.

**Scope:** `mods/sungrid/fluent/rules.ftl` (`actor-v2rl`, `actor-qtnk`, `actor-u2-name`, `actor-u2-husk-name`,
`actor-afld`'s two Special Ability mentions and `.airstrikepower-spyplane-name`, `actor-afld-ukraine-description`),
`mods/sungrid/fluent/chrome.ftl` (one deploy-tooltip line), `docs/ENERGY_BALANCE.md` (candidates list updated
to reflect done/deferred/blocked), `docs/BACKLOG.md` (this entry). No `rules/*.yaml`, no `sequences/*.yaml`,
no new C#, no new art.

**Verification:** Grepped the whole `mods/sungrid/` tree for the old display strings ("V2 Rocket Launcher",
"MAD Tank", "Spy Plane") after editing to confirm no other file hardcoded the literal text outside the fluent
keys changed — found and fixed two more mentions inside `AFLD`'s own description block and one in
`chrome.ftl` that a narrower first pass would have missed. Confirmed no duplicate fluent keys introduced. No
engine/`dotnet` available in this sandbox; CI's rules/map validator is the primary correctness gate on the
pushed branch, though there's little for it to catch here since no actor id/weapon/sequence changed.

**Labels:** `type:content`, `area:units`

**Phase:** 7 — Unit & Audio Identity (first wave; the bulk of the phase — core roster sprites, sub-faction
units, audio — remains explicitly unstarted, see `docs/ENERGY_BALANCE.md`).

---

### 28. Shellmap Lua still spawned `e4` — a fourth missed reference from issue #14's rename, in a file type no prior audit checked — FIXED

**Problem:** Reported from an actual Windows alpha7 playtest: Flame Infantry was still visibly present in the
main-menu shellmap battle, despite issue #14 replacing it with `DISR` (Disruptor Trooper) and issues #16/#25
each fixing a leftover `e4`/`ftur` reference in the shellmap's `map.yaml`/`rules.yaml`. Root cause:
`mods/sungrid/maps/desert-shellmap/desert-shellmap.lua` — the script that actually drives the shellmap's
animated background battle — still spawned `"e4"` in four places: `BeachUnitTypes` (the beach-landing wave
sent via `SendSovietUnits(Entry7.Location, BeachUnitTypes, 15)`) and all three Soviet barracks'
`ProducedUnitTypes` lists (`SovietBarracks1`/`2`/`3`, each producing `dog, e1, e2, e3, e4, shok` on a loop via
`ProduceUnits`). This is the actual mechanism that puts units on screen in the shellmap — `map.yaml`'s static
actor placements (fixed in #16) and `rules.yaml`'s APC cargo (fixed in #25) are one-shot; the Lua script's
recurring production/reinforcement loops are what a player watching the main menu for more than a few seconds
actually sees.

**Why this was missed three times over:** Every prior `e4`/`ftur` audit (#14's own fix, #16, #25) explicitly
scoped its verification grep to `mods/sungrid/**/*.yaml` — none of them checked `.lua`. This repo has exactly
two Lua scripts (`mods/sungrid/scripts/campaign.lua`, clean, and this one), so the blind spot was narrow but
exactly where it mattered: the one script that runs every time the game launches.

**Fix:** `e4` → `disr` in all four spots in `desert-shellmap.lua`, matching the established replacement.

**Root cause:** Same as #25's: a rename covered by grepping one file type, re-verified by grepping the same
file type again. Fourth instance of the same missed reference, in a fourth distinct location, across three
separate follow-up passes.

**Labels:** `type:bug`, `type:content`

**Phase:** Not tied to a specific roadmap phase — follow-up correctness fix to issue #14.

**Verification:** Grepped the entire `mods/sungrid/` tree (not just `.yaml`) for bare `e4`/`E4`/`ftur`/`FTUR`
tokens, this time explicitly including `.lua`, `.ftl`, and every other extension — confirmed the only
remaining hits are legitimate art-filename reuse (`e4.shp`/`ftur.shp`/`fturmake.shp`/`fturicon.shp`,
per #14's "same chassis art, different actor id" design) and unrelated hex color codes
(`E4E4E4`, `ABB7E4`) that happen to contain the substring. No engine/`dotnet` available in this sandbox, so
`make test`/a real client launch couldn't be run locally; CI and a human playtest on the pushed branch are the
real checks — this fix should be re-verified against an actual alpha8-equivalent build before considering the
shellmap's `e4`/`ftur` cleanup finished for real.

---

### 29. Every release since alpha1 has shipped without a macOS build — the packaging job never runs — PARTIALLY FIXED, see #30

**Problem:** None of the alpha1–alpha7 GitHub releases have a `.dmg` asset, despite `.github/workflows/packaging.yml`
having a `macos` job and `packaging/macos/buildpackage.sh` being a complete, working OpenRA Mod SDK macOS
packaging script (universal x86_64+arm64 launcher, codesigning/notarization support if secrets are set, disk
image assembly). The macOS job in every one of the seven `Release Packaging` workflow runs to date shows
`conclusion: cancelled`, `runner_id: 0`, and zero steps ever started — it sat queued for exactly 24 hours before
GitHub auto-cancelled it, never once acquiring a runner. The Windows and Linux jobs in the same runs all
succeeded normally.

**Root cause:** The job was pinned to `runs-on: macos-13`. GitHub began deprecating the macOS 13 runner image on
2025-09-22 and fully retired it by 2025-12-08 (see
[github.blog/changelog/2025-09-19-github-actions-macos-13-runner-image-is-closing-down](https://github.blog/changelog/2025-09-19-github-actions-macos-13-runner-image-is-closing-down/)).
By the time of this repo's first tagged release (alpha1, 2026-07-12), `macos-13` was no longer a schedulable
runner label at all, so every job requesting it queued forever instead of failing fast — the eventual 24-hour
auto-cancellation looks like a hang, not a clear error, which is why this went unnoticed across seven releases.

**Fix:** `runs-on: macos-13` → `runs-on: macos-14` in `.github/workflows/packaging.yml`. No changes needed to
`packaging/macos/buildpackage.sh` — it already cross-compiles both the x86_64 and arm64 launcher/mod assemblies
via `dotnet publish -r osx-x64`/`osx-arm64` and `clang -target x86_64-apple-macos.../arm64-apple-macos...`, so it
does not depend on the runner's own host architecture (macos-14 runners are Apple Silicon/arm64).

**Labels:** `type:bug`, `type:engine`

**Phase:** Not tied to a specific roadmap phase — release infrastructure fix.

**Verification:** Confirmed via the GitHub Actions API that the `macOS Disk Image` job in the workflow runs
backing releases alpha1 through alpha7 all show `runner_id: 0` and no job steps, consistent with never being
scheduled. This fix was confirmed to solve the *scheduling* half of the problem: alpha8's `macos` job actually
acquired a `macos-14` runner and ran for the first time ever — but it then failed for an unrelated reason,
tracked separately as issue #30, so alpha8 still shipped without a `.dmg`.

---

### 30. macOS packaging job now runs (issue #29) but fails: `buildpackage.sh` references engine files the pinned engine commit doesn't have — FIXED

**Problem:** With issue #29's runner fix landed, alpha8's `Release Packaging` run gave the `macOS Disk Image` job
a real `macos-14` runner for the first time in this repo's history — engine fetch and compile both succeeded —
but the "Package Disk Image" step then failed after 19 seconds:

```
clang: error: no such file or directory:
'.../packaging/macos/../..//./engine/packaging/macos/apphost-mono.c'
```

**Root cause:** This repo's `packaging/macos/buildpackage.sh` (mod-SDK-level, not engine) compiles a "mono"
fallback launcher variant, expecting `apphost-mono.c` and `checkmono.c` to exist under
`${ENGINE_DIRECTORY}/packaging/macos/` and installing a third `osx-x64`+`mono` assembly set alongside the native
x86_64/arm64 ones. The pinned `ENGINE_VERSION` commit (`461c7c73c6565f1e2ba557701ad58766d734a428`, itself an
ancestor of this repo's own pre-Phase-0 history — see `CLAUDE.md`'s "Engine version pinning" section) predates
that engine-side mono-fallback feature: its `packaging/macos/` directory only has `Info.plist.in`, `apphost.c`,
`buildpackage.sh` (the engine's own, unused old vendored-fork-era script — superseded by this repo's SDK-level
one), `entitlements.plist`, `launcher.m`, and `utility.m` — no `apphost-mono.c`, no `checkmono.c`. Checked
`launcher.m` at that pinned commit directly: it only ever dispatches to `apphost-arm64`/`apphost-x86_64` (grepped
for "mono", zero hits), confirming the mono fallback path is entirely unused/unreachable dead weight for this
engine version, not a required capability that's merely missing a source file.

**Fix:** Simplified `packaging/macos/buildpackage.sh` to match what the pinned engine actually supports and what
its own historical vendored script already did (confirmed by inspecting that commit's own now-unused
`buildpackage.sh`, which also only ever builds+installs x86_64 and arm64 native variants):
- Dropped the `mono` assembly directory, the `apphost-mono.c`/`checkmono.c` clang compile steps, and the
  `mono`-target `install_assemblies`/`install_mod_assemblies` calls.
- Raised `MINIMUM_SYSTEM_VERSION` in `Info.plist` from `10.11` to `10.15` and the `Launcher-x86_64` apphost's
  clang `-target` from `x86_64-apple-macos10.11` to `x86_64-apple-macos10.15`, since `10.15` is the actual floor
  for native (non-mono) .NET on macOS and matches what the engine's own historical script set.

**Labels:** `type:bug`

**Phase:** Not tied to a specific roadmap phase — release infrastructure fix, follow-up to issue #29.

**Verification:** Confirmed via the GitHub Actions API that `apphost-mono.c`/`checkmono.c` are absent from the
pinned engine commit's tree (`git ls-tree` against a direct fetch of that SHA) and that `launcher.m` at the same
commit has no mono-related code path. No macOS host available in this sandbox to run `buildpackage.sh` directly;
this fix should be confirmed by watching the next tag's `Release Packaging` run end-to-end and checking the
resulting release for a `SungridProtocol-<tag>.dmg` asset.

---

### 31. Roster survey gaps G7/G8 (drone cost skew, Cryptominer payback) — flagged for playtest, no rules change yet

**Problem:** `docs/BUILDINGS.md`'s July 2026 roster survey found two possible balance issues that don't have an obvious correct fix without real match data:

- **G7 — Drone cost/performance skew.** The Consortium's Strike Drone (`SGDRS`) pays +71% cost over the Assembly's Recon Drone (`SGDRO`, 600 vs 350) for +17% HP, +36% damage, and −12% speed. Could be reasonable faction flavor (Consortium's centralized/hardened identity vs. Assembly's decentralized/scarcity-adapted one), or could mean the Assembly gets strictly more value per credit.
- **G8 — Cryptominer payback is short and raid-proof.** `SGCRY`'s 45 cr/50 ticks (≈1,350 cr/min at normal speed) pays back its 1800 build cost plus ~600 of supporting power infrastructure in roughly 2 minutes — after which, unlike a Harvester, that income never leaves the base to be raided.

**Why no rules change:** Both gaps are plausibly-fine-as-is per each faction's declared identity (`docs/ART_DIRECTION.md`), and retuning either without seeing how they play out in a real 3+ player match would just be substituting one guess for another — the same reasoning the roster survey itself gave when it flagged these for playtest rather than proposing numbers.

**Action:** Tracked here so it isn't lost as a one-line doc suggestion. Both should be evaluated against a real skirmish/Grid Reserve playtest (`docs/PLAYTESTING.md`, and the existing 3+ player structured-playtest task in issue #9) — specifically: does the Assembly's drone economy noticeably underperform the Consortium's at matching investment, and does a Cryptominer-heavy build order measurably outperform Harvester-based econ once raiding is a real threat.

**Labels:** `type:balance`, `needs:playtest`

**Phase:** 5 — Faction Flavor (follow-up to the roster survey; no phase work blocked on this).

**Verification:** N/A — no code/rules change in this issue by design. Resolved when a playtest either confirms the current numbers are fine or a follow-up issue lands a specific retune backed by observed match data.

---

### 32. Roster survey gaps G5/G6: SGTUR shared GUN's weapon, HIND was disabled dead content — FIXED

**Problem:** Two more findings from the July 2026 roster survey (`docs/BUILDINGS.md`):

- **G5** — `SGTUR` (Grid Defense Turret, buildable by both factions off bare `anypower`) fired the exact same `TurretGun` weapon as `GUN` (Consortium-only Turret, needs `tent`). Since `SGTUR` was cheaper to reach and available to both sides, `GUN` was close to dead content for the Consortium.
- **G6** — `HIND` carried `~disabled` in its `Buildable.Prerequisites` (inherited as-is from stock RA) and was gated to the Consortium's `~hpad`, so it was unreachable dead content — and with `MH60`/`TRAN`/`HELI` all on the Consortium's Helipad, the Assembly had no helicopter at all (fixed-wing only via `AFLD`).

**Fix:**
- Added a new weapon, `GridPulseCannon` (`mods/sungrid/weapons/ballistics.yaml`), identical to `TurretGun` in damage/reload/range so `SGTUR`'s existing cost/prereq tradeoff is unchanged, but reflavored as an energy weapon (`ElectricityDeath` instead of `ExplosionDeath`) with an inverted armor profile: 100% vs Light armor (drones, scouts, light vehicles), only 55% vs Heavy — vs. `TurretGun`'s 75%/100%. `SGTUR.Armament.Weapon` now points at it. `SGTUR` is the shared, power-scaled anti-harassment turret; `GUN` keeps its niche as the Consortium's harder-hitting anti-armor gun.
- `HIND` (`mods/sungrid/rules/aircraft.yaml`): dropped `~disabled` and `~hpad`; re-gated to `~afld, ~techlevel.medium`. `AFLD` (`mods/sungrid/rules/structures.yaml`) gained `Helicopter` in its `Production.Produces` (was `Aircraft, Plane` only) to allow it. No stat or weapon changes — still `Cost: 1500`, `HP: 10000`, `ChainGun`.
- Renamed via fluent (`actor-hind` in `mods/sungrid/fluent/rules.ftl`) from "Hind" — a real-world Mi-24 NATO reporting name — to **"Wasp Gunship"**, matching the Assembly's decentralized/drone-based identity and the same "drop the real-world Cold War designation" pattern already applied to `V2RL`/`QTNK`/`U2` (issue #27). Husk tooltip name updated to match.

**Scope:** `mods/sungrid/weapons/ballistics.yaml` (new `GridPulseCannon`), `mods/sungrid/rules/structures.yaml` (`SGTUR.Armament`, `AFLD.Production`), `mods/sungrid/rules/aircraft.yaml` (`HIND.Buildable.Prerequisites`), `mods/sungrid/fluent/rules.ftl` (`actor-hind`, `actor-hind-husk-name`). No new C#, no new art — `HIND` reuses its existing stock sprite/sequences/husk, already present in `mods/sungrid/sequences/aircraft.yaml` and `mods/sungrid/rules/husks.yaml`.

**Labels:** `type:balance`, `type:content`

**Phase:** 5 — Faction Flavor (roster survey follow-up).

**Verification:** Confirmed `ai.yaml`'s four `ModularBot@*` entries already list `hind` in their generic `AirUnitsTypes` wishlist (dead weight until now, since bots only build what's actually reachable) — no AI-side change needed to make bots use it. Confirmed no other reference to `~disabled`/`~hpad` remained on `HIND`, and that `GridPulseCannon` doesn't collide with an existing weapon id. No engine/`dotnet` available in this sandbox, so `make test`/a real client launch couldn't be run locally — CI and a human playtest on the pushed branch are the real checks.

---

### 33. Phase 6 wrap-up: engine build + real live-client verification achieved for the first time, cursor palette first pass, and a real main-menu title bug caught by it — FIXED

**Status:** Every prior Phase 6 backlog entry (#13, #16, #17, #18) independently hit the same wall: no session doing that work had both a built engine *and* a real content pack at once, so nothing in Phase 6 had ever actually been seen rendered by a running client — only composited sprite-sheet dumps. This pass had genuine network + build access, so it went all the way through, and the payoff was immediate: the very first real screenshot of the mod's own main menu showed its single largest heading reading **"OpenRA"**, not "Sungrid Protocol" — a bug invisible to every previous check because it only exists in the rendered chrome, not in any YAML a linter or `--check-yaml` pass would flag.

**What made the full pipeline possible this time (all done fresh in this session, nothing pre-existing):**
- Unshallowed the local clone (`git fetch --unshallow`) so the pinned `ENGINE_VERSION` commit (`461c7c73c6...`, an ancestor of `main` per `CLAUDE.md`'s "Engine version pinning" section) was actually present locally, then `git worktree add` checked it out and symlinked it in as `./engine` (gitignored, never committed) rather than fighting `fetch-engine.sh`'s zip path.
- `sudo apt-get install -y dotnet-sdk-8.0` (8.0.128) plus `make` built both the engine and `OpenRA.Mods.Sungrid` clean — 0 warnings, 0 errors, matching issue #17's earlier finding that the current pin compiles fine.
- Downloaded the official freeware `ra-quickinstall.zip` from a working mirror, verified its SHA1 (`44241f68e69db9511db82cf83c174737ccda300b`, matches `docs/PLAYTESTING.md`'s documented hash exactly), and extracted it to `~/.config/openra/Content/ra/v2/` (the actual Linux `SupportDir` path per `OpenRA.Game/Platform.cs` — not previously written down anywhere in this repo's docs).
- With both in place, `Mod=sungrid ./utility.sh --check-yaml` ran clean (exit 0) against the full ruleset and every shipped map — the first real confirmation of this since issue #19's CI run, but now reproducible locally on demand.
- Installed `xvfb`, `imagemagick`, and `xdotool`; launched the actual client (`./launch-game.sh Game.Mod=sungrid`) under `Xvfb :99`, drove it through the first-run setup dialogs with `xdotool`, and captured real screenshots with `import -window root` — the first genuine live-client renders in this repo's history, not composited dumps.

**What the live render confirmed working correctly, for real, for the first time:** the Phase 6 chrome recolor (issue #13) and the desert-tileset terrain recolor (issue #18, via the main-menu shellmap) render together cohesively — green-tinted dialog/sidebar chrome, the placeholder gold-hexagon emblem (issue #16), and the recolored ground all read as one consistent world, not a patchwork. The shellmap's battle plays correctly with no crash and no dangling actor reference (confirming issues #16/#25/#28's fixes hold). The default cursor renders crisply in the actual client scene (confirmed by forcing `Graphics.DisableHardwareCursors=true` so the cursor draws into the captured framebuffer rather than as a separate host-composited layer invisible to `import`).

**What it found broken (fixed in this pass):** `label-main-menu-title` — the fluent key `common|chrome/mainmenu.yaml`'s `Label@MAINMENU_LABEL_TITLE` widget reads — was never overridden in `mods/sungrid/fluent/chrome.ftl`, so it fell through to the engine's own stock default (`engine/mods/common/fluent/chrome.ftl`: `label-main-menu-title = OpenRA`). Every other Phase 6 pass touched the art (`dialog.png`, `sidebar.png`, the icon, the emblem) but nobody had actually seen the assembled main menu to notice the literal title text underneath all of it was untouched stock. Audited every other `= OpenRA` string in the engine's stock chrome fluent file before fixing just this one: the rest (`label-openra` on the credits screen's own "Engine" tab, "Requires OpenRA forum account", "Download the latest version of OpenRA from www.openra.net", "OpenRA Resource Center") all correctly refer to the real upstream OpenRA project/forum/services this mod is built on and depends on — those are correct as-is and were left alone.

**Cursor palette — first pass, with a real near-miss caught before shipping:** `docs/ROADMAP.md`'s Phase 6 deliverables call for "a custom cursor set replacing the stock RA cursors." Real custom cursor art (new pointer shapes) needs a dedicated pixel artist and wasn't attempted. What was tractable with the tooling now proven working: reusing the same palette-recolor technique issue #18 already validated for terrain, since `mods/sungrid/rules/palettes.yaml`'s `PaletteFromFile@cursor` was still pointing at plain stock `temperat.pal`. The first attempt — just repointing it at the already-existing `sungrid-temperat-terrain.pal` — was tested properly this time (decoding `mouse.shp`/`nopower.shp`/`attackmove.shp` via `utility.sh --png` against both palettes and diffing all 222 frames pixel-by-pixel) rather than assumed safe, and it wasn't: 112 of 222 frames changed, and the change flipped the entire "blocked"/"attack"/"nuke"/danger cursor family from red to green, because the terrain script's touched hue band (hue≤45° or ≥330°, chosen to catch temperate's dominant tan ground color) also contains pure saturated red — exactly the color classic RA's cursor set uses for "can't do this here." Shipping that straight reuse would have silently broken half the mod's cursor-based player feedback, a real legibility regression `docs/ART_DIRECTION.md`'s own "legibility first" pillar exists to prevent.

Fix: a dedicated `mods/sungrid/bits/reskin_cursor_palette.py` (adapted from `reskin_terrain_palette.py`) adds a protected "semantic-red" exclusion (hue within 20° of pure red, saturation > 0.5) so blocked/attack/nuke/danger cursors keep their exact stock color regardless of brightness, while the non-semantic accents (the sell "$" and repair/goldwrench wrench family) still pick up a subtle green tint consistent with the rest of the recolored world. Output is `mods/sungrid/bits/sungrid-cursor.pal` (54/256 entries changed, vs. the unsafe attempt's much larger and semantically-wrong diff); `PaletteFromFile@cursor`'s `Filename` now points at it. Re-verified the same rigorous way: every previously-broken blocked/attack/nuke frame now diffs at 0 changed pixels against stock; only frames with no semantic-red content differ at all.

**What's still genuinely open, not just re-flagged:** the main menu's own widget *layout* (button placement, panel arrangement) is still stock `common|chrome/mainmenu.yaml` — only its title text and the art it draws from are now Sungrid's own; a full custom layout override remains a larger, separate undertaking. The main menu music sting is still stock RA's `intro` track (real composed/licensed audio, explicitly Phase 7 scope per issue #16). Real custom cursor *shapes* (not just a palette tint) still need a dedicated art pass. A live-client camera view of an actual temperate-tileset skirmish (as opposed to the desert-tileset main-menu shellmap, now confirmed) was attempted again with the now-working full pipeline via `Launch.Map=<uid>` directly into a temperate map (`chernobyl`) — confirmed exactly the same limitation issue #18 already documented: the sidebar/build palette render correctly, but the battlefield viewport is fully black because the no-bots `ServerType.Local` quick-load path places no starting units anywhere on the map, so there's no shroud-clearing at all. This is not a rendering defect and not something this pass's environment access changes — actually seeing the temperate recolor in a live camera view still needs the documented `Launch.SkirmishBots` engine patch, which remains correctly scoped as its own separate follow-up (large enough to not fold into this pass, per issue #17's original assessment).

**Scope:** `mods/sungrid/fluent/chrome.ftl` (`label-main-menu-title`), `mods/sungrid/rules/palettes.yaml` (`PaletteFromFile@cursor.Filename`), `mods/sungrid/bits/reskin_cursor_palette.py` (new), `mods/sungrid/bits/sungrid-cursor.pal` (new). No C#, no changes to `engine/` (gitignored, never committed, exactly as `CLAUDE.md` requires).

**Labels:** `type:bug`, `type:art`, `area:ui`

**Phase:** 6 — World & UI Visual Identity Overhaul.

**Verification:** `Mod=sungrid ./utility.sh --check-yaml` clean (exit 0) against the full ruleset and every shipped map, run locally against a real built engine (not CI) for the first time since issue #19. Real live-client screenshots (attached to the PR discussion, not just described) confirm the main-menu title fix and cursor rendering. Cursor palette change verified via exhaustive per-frame pixel diffing of all 222 cursor frames against stock, both before the fix (confirming the regression) and after (confirming it's gone). This is the first Phase 6 entry in this backlog whose "Verification" section describes things actually observed running, rather than inferred from a composited dump or deferred to "CI and a human playtest."

---

### 34. Custom art for the rest of the Sungrid-original roster (buildings + drones) — FIRST PASS DONE

**Problem:** `docs/BACKLOG.md` issue #12 gave Solar Array (`POWR`/`APWR`) dedicated art, but every other Sungrid-original building added in Phase 5/the energy rebalance pass — Cryptominer (`SGCRY`), Datacenter for AI (`SGDAI`), Drone Bay (`SGDRN`), Aerial Fabrication Bay (`SGDRA`), Grid Defense Turret (`SGTUR`), Smart Grid Relay (`SGREL`), Resilience Shelter (`SGSHL`), Sensor Array (`SGSNS`), Wind Turbine Array (`SGWND`), Hydrogen Plant (`SGHYD`) — was still shipping with a `RenderSprites.Image` override pointing at a completely unrelated *existing* building's sprite (respectively: `atek`, `dome`, `hpad`, `afld`, `sam`, `gap`, `iron`, `kenn`, `sam`, `proc`). This was flagged as generic "placeholder art debt" in `docs/BUILDINGS.md`, but it's worse than that in two concrete cases: `SGTUR` and `SGWND` **both** rendered the exact same sprite as the real `SAM` Site — three unrelated buildings sharing one silhouette, a direct violation of `docs/ART_DIRECTION.md`'s non-negotiable "every unit and building must have a distinct, readable silhouette" rule. The two Recon/Strike Drone units (`SGDRO`/`SGDRS`) had the same problem: both fully reused `TRAN`'s (Chinook) and `MH60`'s (Black Hawk) manned-helicopter bodies respectively, with docs explicitly noting "no new art" as still-open for both.

**Fix:** Extended issue #12's "programmatic first pass now, real artist pass later" approach to this whole list, scoped per the same "don't redraw what's roughly the same or easy to adapt" call issue #14 made for `DISR`/`ARCT` reusing `E4`/`FTUR`'s chassis art:

- **10 buildings got genuinely new art**, generated by a new `mods/sungrid/bits/gen_concept_art.py` (Pillow) and shipped as `PngSheet`-format sprites (idle + damaged-idle frames, matching Solar Array's exact "single static make-frame, not a proper build-up animation" simplification) plus dedicated 32x24 build-palette icons: `SGCRY`/`SGDAI` (server-rack motifs, distinguished by legacy-gray-and-rust vs. neat blue-black-and-gold per `docs/ART_DIRECTION.md`'s "military/industrial counterpoint" guardrail), `SGDRN`/`SGDRA` (open improvised scaffold vs. enclosed hardened hangar, matching the Assembly/Consortium decentralized-vs-centralized philosophy split), `SGSHL` (a bunkered dome with a sandbag row, per the "not utopian" guardrail), `SGSNS` (a mast-mounted radar dish), `SGREL` (a small relay pylon), and `SGTUR` (a genuinely rotating turret — a 64-frame, 32-facing idle + 32-facing damaged `UseClassicFacings` sheet, generated by rotating one drawn frame with Pillow, the same technique now proven for the two drone bodies below).
- **`SGWND`/`SGHYD` were treated as "easy to adapt" rather than fully new motifs**: both are mechanically just other power buildings, so they're drawn as variants of Solar Array's already-established "grid-tied panel array" visual language (ground strip + gold conduit band) rather than inventing unrelated designs — `SGWND` swaps the solar-panel frames for two sparse turbine-and-rotor poles (cheaper/thinner, matching its "cheap, mass-producible" fantasy and 2x3 `POWR`-family footprint), `SGHYD` swaps them for two large gold-banded tanks (bigger/heavier, matching its Heavy-armor, 3x3 `APWR`-family footprint and late-game cost).
- **`SGDRO`/`SGDRS` got dedicated small-drone silhouettes** (32-facing `UseClassicFacings` body sheets, no damaged-idle -- matching `tran`/`mh60`/`heli`, none of which define one either): a green quadcopter-style body for the Assembly's Recon Drone, a larger blue-black-and-gold body with visible weapon-pod accents for the Consortium's Strike Drone. Rotor-blur overlays (`WithIdleOverlay@ROTOR*`) still reuse the shared generic `lrotor.shp`/`rrotor.shp`/`yrotorlg.shp` assets unchanged (a blurred disc isn't part of either drone's distinct identity, the same "shared generic FX asset" convention bib decals already use) -- `SGDRO`'s dual-rotor offsets were retuned down from `TRAN`'s (597,0,213 / -597,0,341 -> 350,0,130 / -350,0,200) to match its much smaller body; `SGDRS`'s single centered rotor needed no change.
- **`SGHAU` (Hauler Drone) was deliberately left alone**, still on `HARV`'s (Ore Truck) chassis -- it's mechanically and thematically just a small wheeled resource hauler, the same "reuse the chassis, only the identity changed" call already made for `DISR`/`ARCT`. Redrawing it would have been scope creep against this issue's own "don't implement new graphics when a concept is roughly the same or easy to adapt" instruction.
- Every new sequence block reuses the bib/minibib decal (and, for `SGHYD`, the death animation) already wired for whichever building it used to borrow art from, rather than inventing new ones -- e.g. `sgtur:` reuses `SAM`'s `mbSAM.*` minibib and `gunmake.shp` base-pad placeholder exactly the way the stock `sam:` sequence block already does, and `sghyd:` reuses `APWR`'s `apwrdead.shp` death animation.

**Scope:** New `mods/sungrid/bits/gen_concept_art.py` plus its 24 generated PNGs (`sgcry`/`sgdai`/`sgdrn`/`sgdra`/`sgshl`/`sgsns`/`sgrel`/`sgwnd`/`sghyd` sheets+icons, `sgturturret.png`+icon, `sgdro`/`sgdrs` sheets+icons). New sequence blocks in `mods/sungrid/sequences/structures.yaml` and `mods/sungrid/sequences/aircraft.yaml`. `RenderSprites.Image` repointed (and `SGDRO`'s rotor `WithIdleOverlay` offsets retuned) in `mods/sungrid/rules/structures.yaml` and `mods/sungrid/rules/aircraft.yaml`. No trait/behavior changes, no C#, no changes to `SGHAU`.

**Labels:** `type:art`, `area:buildings`, `area:units`, `area:ui`

**Phase:** 5/6 follow-up (closes the "placeholder art" gap `docs/BUILDINGS.md` flagged for buildings 4-13, plus the drone half of the Phase 7 roster-art gap `docs/BACKLOG.md` issue #27 documented as blocked).

**Definition of done:** Every building/unit in this list renders a sprite distinct from any other actor's, in the locked `docs/ART_DIRECTION.md` palette, with no regression to any trait's behavior. **Met by this first pass** for the distinctness/readability bar (verified via composited NEAREST-upscaled preview renders of every sheet, every rotation set, and every icon -- no engine/live-client access in this environment, same constraint issue #12's own first pass had). A real artist pass (hand-painted indexed-palette pixel art, proper build-up animations) remains open follow-up work, same status as Solar Array's own remaining gap.
