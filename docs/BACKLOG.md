# Sungrid Protocol — Phase 0/1/2/3 Issue Backlog

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

- **Engine build, from this repo's own history, no external download needed.** `mod.config`'s `ENGINE_VERSION` (`bf4102a0...`) is pinned to the exact commit this repo's own `bleed` branch sits at — so `./engine` can be populated directly from `git worktree add`/checkout of `origin/bleed` (or a shallow clone of that SHA) instead of fighting `fetch-engine.sh`'s zip download, which a scoped GitHub token/proxy may block. Confirmed the pinned commit hits the documented `CS0121` `CryptoUtil.SHA1Hash([])` ambiguity under SDK `8.0.128` (installed via `sudo apt-get install -y dotnet-sdk-8.0`); applying the one-line local-only fix (`Array.Empty<byte>()`) in the gitignored `engine/` let `make` complete with **0 warnings, 0 errors** for both the engine and `OpenRA.Mods.Sungrid` — the first time Phase 3's Grid Reserve traits and Phase 5's building roster have been confirmed to compile by anyone/anything other than a manual one-off (see below on CI).
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

### 18. Phase 6 temperate terrain reskin — FIRST PASS DONE, snow/desert + live-client verification still open

**Status:** Recolored the temperate tileset toward `docs/ART_DIRECTION.md`'s locked palette via a **palette-only** edit, not by touching individual tile sprites. `mods/sungrid/bits/reskin_terrain_palette.py` reads the stock `temperat.pal` (extracted via `utility.sh --extract`, per issue #17's now-working recipe) and applies a piecewise hue remap — the dominant tan/dirt/rust band (hue 0-45°) shifts toward the locked green, a small set of near-pure bright highlights (ore/gem glint accents) shift toward the locked sun-gold hex instead so they stay visually distinct from the green ground, and blues (water)/grays (rock, roads) are left untouched. Output is a new file, `mods/sungrid/bits/sungrid-temperat-terrain.pal`, and `rules/palettes.yaml`'s `PaletteFromFile@terrain-temperat` now points at it instead of stock `temperat.pal`.

**Why palette-only, and why it's safe:** `rules/palettes.yaml` already declares terrain (`Name: terrain`) and units/buildings (`Name: player`) as separate `PaletteFromFile` entries, even though both loaded from the same stock file before this change. Repointing only `terrain`'s `Filename` recolors terrain tiles and neutral scenery (trees/rocks, which render via the same `terrain` palette) without touching unit, building, or weapon-effect colors — those traits still load the unmodified stock `temperat.pal`. It also means zero risk to tile geometry/boundaries (the actual `.tem` sprite data is never touched, only the color each index maps to), sidestepping the exact risk `docs/ROADMAP.md`'s Phase 6 section calls out about individual tile-sprite edits.

**First iteration was too subtle to matter:** a straight port of the chrome pass's hue band (±25° from red) only touched 12% of the tileset atlas's pixels at low magnitude — barely perceptible once composited. Widened to a 45° band (verified against the actual stock palette dump, not guessed) to catch the dominant tan "clear ground" tone; this touches ~22% of pixels with a visually obvious result, confirmed via `utility.sh --dump-sheets` (the same composited sprite-sheet-plus-palette code path the live game renders through) diffed against a stock-palette render of the same tileset.

**Labels:** `phase:6`, `type:art`, `area:world`

**Phase:** 6 — World & UI Visual Identity Overhaul (see `docs/ROADMAP.md`, `docs/ART_DIRECTION.md`)

**Purpose:** `docs/ROADMAP.md`'s Phase 6 deliverables call for a reskinned temperate tileset with a "living, reclaimed industrial" look. This is a first pass toward that — same "programmatic first pass now, real artist pass later" approach issues #12/#13 used, adapted for terrain's palette-based rendering instead of per-sprite art.

**Scope:**
- Recolor the temperate tileset's terrain-only palette per the locked palette in `docs/ART_DIRECTION.md`, leaving tile geometry, water, and unit/building/effect colors untouched.
- Verify via the actual composited sprite-sheet render (`--dump-sheets`), not just the raw palette swatch, since what matters is how it looks once tiles are drawn.
- Out of scope: snow/desert tilesets (explicitly sequenced as a same-phase follow-up or Phase 7 per `docs/ROADMAP.md`), individual tile sprite/decoration art, cliffs/scenery actor sprites themselves (only their palette), live-client rendered verification with a real camera view (attempted in this pass but not completed — see below), the main-menu shellmap's own terrain (uses the `DESERT` tileset, not `TEMPERAT`, so this pass doesn't touch it).

**Dependencies:** Builds directly on issue #17's engine-build/content-access recipe.

**Definition of done for this pass:** The temperate tileset visibly reads as recolored toward the locked palette when composited (verified via `--dump-sheets` diff against stock), with tile geometry, water, and non-terrain sprite colors unaffected. **Met for the composited-sheet verification.** Not yet met: an actual live-client screenshot with a real camera view over a temperate map — attempted in this pass (Xvfb + a quick-loaded skirmish) but the viewport rendered black, most likely shroud/camera-position in the no-bots `Launch.Map` quick-load path rather than a rendering defect (sidebar/minimap chrome rendered correctly in the same screenshot), not conclusively resolved. Whoever picks this up next should confirm with a real bot-filled skirmish (see `docs/PLAYTESTING.md`'s `Launch.SkirmishBots` recipe) before treating this as fully closed, and then extend to snow/desert if the direction holds up.
