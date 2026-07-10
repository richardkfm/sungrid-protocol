# Sungrid Protocol — Phased Roadmap

Scope control is the whole game here. Each phase must ship something playable or reviewable, and each phase must be revertible without breaking the one before it. See `docs/BLUEPRINT.md` for the full narrative version of this table and `docs/ARCHITECTURE.md` for the technical reasoning behind the code/data split.

## Phase overview

| Phase | Objective | GitHub milestone |
|---|---|---|
| 0 | Repository bootstrap and architecture setup | `P0: Bootstrap` |
| 1 | Baseline playable shell on OpenRA | `P1: Baseline Shell` |
| 2 | First solarpunk content layer | `P2: First Content Pass` |
| 3 | Economic victory mode MVP | `P3: Grid Reserve MVP` |
| 4 | UI, balance, AI, multiplayer iteration | `P4: Playtest Hardening` |
| 5 | Expanded buildings / faction flavor / polish | `P5: Faction Flavor` |
| 6+ | Diplomacy / shared-resource systems (conditional) | `P6: Diplomacy (conditional)` |

## Phase 0 — Repository bootstrap and architecture setup

- **Why:** Nothing downstream is trustworthy if the repo structure, docs, and contribution model aren't settled first. This is also where the "full engine fork vs. Mod SDK" question got answered (Mod SDK — see `docs/ARCHITECTURE.md`) once, in writing, so it never gets re-litigated per-PR.
- **Deliverables:** `docs/` design doc set (this file and its siblings), `CLAUDE.md` navigation map, root `README.md` reframed for Sungrid Protocol, label taxonomy and milestones created in GitHub, first 10 issues opened; **the repo restructured onto the OpenRAModSDK pattern** — `mod.config`, `fetch-engine.sh`, and `mods/sungrid`/`OpenRA.Mods.Sungrid` (renamed from the SDK's example template) in place, engine fetch verified working.
- **Code scope:** None beyond the SDK's own example-mod stub, renamed to Sungrid branding.
- **Data/content scope:** None beyond the SDK's placeholder example content, renamed. No real gameplay rules yet.
- **Testing scope:** Docs review (links resolve, tables render, no contradictions) plus a build check: `fetch-engine.sh`/`make` successfully fetches the pinned engine and the stub mod builds/launches to the main menu.
- **Exit criteria:** All docs merged to `bleed`; milestones and labels exist; contributors (even a future solo-plus-Claude workflow) can onboard from `README.md` alone; `make` + `launch-game.sh Game.Mod=sungrid` reaches the main menu on a clean checkout.
- **Biggest risk:** Scope creep into writing real gameplay content in `mods/sungrid` before Phase 1 properly starts — this phase proves the scaffold works, it doesn't populate it with Red Alert-derived rules yet.
- **Do NOT attempt yet:** Any C# traits beyond the SDK's stub, any real gameplay YAML, any art asset pipeline decisions.

## Phase 1 — Baseline playable shell on OpenRA

- **Why:** Prove the SDK scaffold can carry real gameplay content, not just the placeholder example mod, before any new mechanic is added. This is the fastest way to a genuinely "playable" milestone.
- **Deliverables:** `mods/sungrid`'s placeholder example rules/sequences/maps replaced with real content forked from `mods/ra`'s gameplay (pulled from the fetched `engine/mods/ra` reference or the public OpenRA/OpenRA repo, since `mods/ra` is no longer vendored locally), mod metadata (title, icon placeholder) finalized, mod appears in the OpenRA mod chooser and launches to a working skirmish against the AI.
- **Code scope:** None beyond what `mods/ra` already has. No new traits in `OpenRA.Mods.Sungrid` yet beyond the SDK's stub.
- **Data/content scope:** Real rules/sequences/maps replacing the SDK's `example` placeholder content. Unit and building YAML is untouched from `mods/ra` at this point (still literally Red Alert content, just running under the Sungrid Protocol mod id).
- **Testing scope:** Manual: launch the mod, start a skirmish vs. AI, confirm win/lose on destruction victory, confirm no crashes, confirm assets load.
- **Exit criteria:** A build of the Sungrid Protocol mod can be launched, played start-to-finish against the AI, and produces a normal win/loss result.
- **Biggest risk:** Treating this phase as "done" content-wise — it isn't, it's plumbing. It's tempting to start reskinning immediately; resist until Phase 1 is merged and stable.
- **Do NOT attempt yet:** Any new buildings, new economy mechanics, or art replacement. This phase is a port-and-verify pass, not a content pass.

## Phase 2 — First solarpunk content layer

- **Why:** This is the first phase where Sungrid Protocol starts to look and feel different from vanilla RA, entirely through data-driven YAML changes (renamed/reflavored existing structures, new low-complexity buildings).
- **Deliverables:** Solar Array (power plant reflavor), Battery Bank (silo-style storage reflavor), Recycling Depot (refinery-adjacent reflavor), first-pass renames of core econ buildings to fit the solarpunk fiction, placeholder or lightly-modified art (existing OpenRA art recolored/retextured is acceptable here — full asset production is a later-phase concern).
- **Code scope:** None expected; if a genuinely new mechanic turns out to need C#, it gets flagged and deferred to Phase 3+ rather than rushed here.
- **Data/content scope:** New/edited `rules/*.yaml` entries in `mods/sungrid`, new building icons/sequences (can be placeholder), updated tech tree ordering.
- **Testing scope:** Manual skirmish playtest confirming new buildings are buildable, produce expected effects (power, storage), and don't break the existing economy loop or AI build orders.
- **Exit criteria:** A skirmish match is playable start-to-finish using at least 3 new/reflavored solarpunk buildings without regressions to Phase 1's baseline.
- **Biggest risk:** Scope-creeping into full custom art production before the mechanics are validated — expensive art on unvalidated mechanics is wasted work.
- **Do NOT attempt yet:** Cryptominer, Datacenter for AI, Drone Bay, or anything that implies new mechanics (those wait for Phase 3+ where they can justify custom traits).

## Phase 3 — Economic victory mode MVP

- **Why:** This is the project's first real design innovation and the reason the project exists in its current form. See `docs/GAME_MODES.md` for the full spec.
- **Deliverables:** New "Vault" building (Grid Reserve deposit structure), a new win-condition/`MissionObjectives`-style trait implementing hold-to-win Reserve logic, HUD/scoreboard elements showing per-player Reserve progress, minimap reveal-at-threshold behavior, lobby option to enable/disable the mode (destruction victory remains the default).
- **Code scope:** This phase is where the first real C# work happens — a new trait (or small set of traits) for tracking Reserve, handling deposits, handling the Lockdown countdown, and hooking into the existing win-condition framework. Kept as small and additive as possible; does not touch unrelated engine systems.
- **Data/content scope:** Vault building YAML, per-map-size Reserve target config, HUD layout changes (Lua/`ChromeLayout` YAML where possible).
- **Testing scope:** Automated where feasible (unit-test the Reserve threshold/countdown logic if it's isolated enough), plus manual 1v1 and 3-4 player matches specifically testing: reaching target, holding through Lockdown, losing Lockdown progress via vault destruction, decay/anti-stalemate behavior over a long game.
- **Exit criteria:** A 3+ player skirmish match can be won via Grid Reserve without destroying all opponents, the mode can be toggled off to fall back to pure destruction victory, and at least one playtest match demonstrates a vault raid meaningfully disrupting a leader's countdown.
- **Biggest risk:** Under-scoping the anti-turtle mechanics and shipping a mode where the "optimal" strategy is to hide in a corner and never fight — this is the single most damaging outcome for the project's core thesis, so it gets explicit playtesting attention, not just code review.
- **Do NOT attempt yet:** Diplomacy-gated protection, alliance/shared-reserve mechanics, per-faction Reserve bonuses.

## Phase 4 — UI, balance, AI, and multiplayer iteration

- **Why:** A mode that only works when a human designer is watching isn't done. This phase is about making Grid Reserve (and the Phase 2 content) survive contact with real players and the game's AI.
- **Deliverables:** AI skirmish scripts updated to understand Grid Reserve (build vaults, raid enemy vaults, respond to Lockdown countdowns at a basic level), balance pass on Reserve targets/decay/deposit caps from Phase 3 playtests, HUD polish, netcode/lobby-sync validation for the new traits under real multiplayer conditions (not just LAN/local).
- **Code scope:** AI script updates (Lua), trait bugfixes/tuning found via playtests, no new major systems.
- **Data/content scope:** Balance tuning (numbers only) across Phase 2 and Phase 3 content.
- **Testing scope:** Structured playtests with 3-6 external testers, dedicated-server multiplayer test session, AI-vs-AI stress test for desync/crash issues.
- **Exit criteria:** External testers can complete a full multiplayer match (destruction or Grid Reserve) without desyncs, crashes, or "obviously broken" balance complaints; AI provides a credible skirmish opponent.
- **Biggest risk:** AI work is a classic time sink in OpenRA-style engines — cap the AI ambition at "doesn't actively ignore the new mechanic," not "plays Grid Reserve optimally."
- **Do NOT attempt yet:** New buildings beyond balance tuning of existing ones, new victory modes, diplomacy.

## Phase 5 — Expanded buildings / faction flavor / polish

- **Why:** With the core loop (destruction + Grid Reserve) validated by real playtests, this phase spends effort on breadth and production values rather than new systems.
- **Deliverables:** Remaining buildings from `docs/BUILDINGS.md` (Cryptominer, Datacenter for AI, Drone Bay, Grid Defense Turret, Smart Grid Relay, Resilience Shelter, Sensor Array), first custom art pass replacing recolored placeholders, at least one visually-distinct faction identity, sound/music pass.
- **Code scope:** Only as required by new building mechanics (e.g. Drone Bay logistics behavior) — still preferentially data-driven via existing OpenRA traits (`Reservable`, `Cargo`, `AttackBase`, etc.) before new C#.
- **Data/content scope:** The bulk of this phase — new building YAML, art, audio, tech tree balancing across a fuller roster.
- **Testing scope:** Full playtest campaign across the expanded roster, regression testing that Phase 3's Grid Reserve balance still holds with more economy options available.
- **Exit criteria:** The building roster from `docs/BUILDINGS.md` is complete and balanced, the mod has a distinct visual identity, and this is the version considered ready for wider public testing (see MVP definition in `docs/BLUEPRINT.md`).
- **Biggest risk:** Faction flavor work has no natural stopping point — set a fixed roster (the 10 buildings already listed) and resist adding more before shipping.
- **Do NOT attempt yet:** Second faction, campaign/story missions, diplomacy.

## Phase 6+ — Diplomacy and shared-resource systems (conditional)

- **Why:** Only pursued if Grid Reserve playtests show that the spend/save tension is solid and players are asking for deeper multiplayer social dynamics (alliances, betrayal, resource sharing) on top of it.
- **Deliverables:** Not scoped yet — deliberately. This phase does not get planned in detail until Phase 3-5 data justifies it.
- **Exit criteria for even starting this phase:** Phase 3-5 playtests show sustained 3+ player engagement with Grid Reserve and explicit tester demand for social/diplomatic mechanics.
- **Do NOT attempt yet:** Everything. This is the phase most likely to blow up the schedule if pulled forward — see Scope Trap #1 in `docs/BLUEPRINT.md`.
