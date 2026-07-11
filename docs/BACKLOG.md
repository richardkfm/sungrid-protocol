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

### 12. Solar Array custom art pass — PRIORITY

**Labels:** `phase:5`, `type:art`, `area:energy`, `priority`

**Phase:** 5 — Faction Flavor (see `docs/ROADMAP.md`, `docs/ART_DIRECTION.md`)

**Purpose:** The mod is named after this building's fiction and it currently has zero distinct visuals. `POWR`/`APWR` ("Solar Array"/"Advanced Solar Array") are a pure name-and-flavor-text reflavor of the vanilla RA power plant — `mods/sungrid/sequences/structures.yaml` still points them at the stock, unrecolored `powr.shp`/`apwr.shp` sprites (no `RenderSprites.Image` override, no palette change). Every other Phase 2/5 building shares this "placeholder art" debt, but Solar Array is the one whose absence is most visible: it's the title concept, the first building most players place, and the building `docs/ART_DIRECTION.md`'s palette direction ("warm solar-panel blues/blacks, sun-gold accents") was written to describe. Called out ahead of the general Phase 5 art/palette pass (referenced in #11 and `docs/ROADMAP.md`'s Phase 5 deliverables) so it isn't just one line item among ten equally-weighted buildings.

**Scope:**
- New indexed-palette sprite art for `POWR`/`APWR` (idle, damaged-idle, and existing death/build-up animation slots — see current `powr`/`apwr` sequence blocks in `mods/sungrid/sequences/structures.yaml` for the frame contract to match), depicting a grid-tied solar panel array per `docs/ART_DIRECTION.md`'s tone/palette guardrails (not utopian/pristine — panels with visible wear, mounting hardware, maybe sandbags/improvised bracing).
- Lock the sprite resolution/frame/naming conventions this establishes as the de facto Phase 5 asset pipeline baseline (`docs/ART_DIRECTION.md`'s "Asset pipeline" section currently says this needs to happen before more than one contributor produces art — this issue is a reasonable place for that baseline to actually get set, rather than deciding it in the abstract).
- Update `RenderSprites`/sequence references only if the new art requires a different filename/frame layout than the current `powr.shp`/`apwr.shp` slot; otherwise this is asset-only, no rules.yaml logic changes.
- Out of scope: the other 7 Phase 5 buildings' placeholder art (tracked generally under #11's "remaining Phase 5 scope" note), a second faction's art set, sound/music.

**Dependencies:** None blocking — Solar Array's mechanics (`Power` trait) are untouched and already playtested since Phase 2; this is asset-only.

**Definition of done:** `POWR`/`APWR` render with dedicated solar-panel sprite art (not stock RA power-plant art) in a skirmish match, matching `docs/ART_DIRECTION.md`'s palette/tone guardrails, with no regression to power generation behavior.
