# Sungrid Protocol — Development Blueprint

This is the master planning document for Sungrid Protocol. It's written for a solo technical founder executing with Claude Code assistance, optimized for the fastest realistic route to a playable prototype on the OpenRA engine. Companion docs go deeper on individual topics and are linked throughout; this document is the one to read start-to-finish.

---

## 1. Project summary

Sungrid Protocol is a solarpunk reinterpretation of the classic Red Alert RTS formula, built on OpenRA. It combines readable classic RTS gameplay with renewable-energy and eco-infrastructure themes, real strategic/military tension, and a new economic victory mode that changes spending incentives.

**Design pillars** (full detail in [`VISION.md`](VISION.md)):

1. Classic RTS legibility first — theme never overrides silhouette/UI readability.
2. Solarpunk as a lens, not a coat of paint — it changes what players *do* (power management, recycling, grid defense), not just what things are named.
3. Spend vs. save is a first-class strategic decision, contested the same way territory is.
4. Pressure never disappears — scouting, harassment, raiding, and map control stay relevant in every mode, including the economic one.
5. Data-driven before engine-driven — YAML/Lua first, new C# only when provably necessary.
6. Small, reversible phases — every phase ships something playable and can be rolled back cleanly.
7. Destruction victory stays intact — the economic mode is additive and optional, never a replacement.
8. 3+ players is the design target for new modes — diplomacy and betrayal only get interesting with three or more seats.

**What makes it different from vanilla Red Alert-style play:** vanilla RA-style games have exactly one win condition (elimination) and a single spendable resource with no strategic "hold" option. Sungrid Protocol adds a second, legitimate path to victory built around *not* spending — while making the act of hoarding itself a raid target, so turtling remains exposed rather than becoming a passive-win strategy. See the full comparison table in [`VISION.md`](VISION.md).

---

## 2. Technical strategy for OpenRA

Full detail in [`ARCHITECTURE.md`](ARCHITECTURE.md). Summary:

**Repo structure.** This repo (`richardkfm/sungrid-protocol`) is currently a direct fork of the full OpenRA engine (branch `bleed`), not the lightweight OpenRAModSDK template. **Decision: keep it that way, and build Sungrid Protocol as a new `mods/sungrid` directory forked from the existing `mods/ra` reference mod**, rather than migrating to a separate SDK-based repo. This avoids burning Phase 0 time on infrastructure migration with zero gameplay payoff, and `mods/ra` is a ready-made, working starting point sitting right next to where the new mod will live. Trade-off: this repo is heavier than a typical mod repo and pulling upstream engine updates later means merging against a full engine tree — acceptable given the priority on speed to prototype.

**Data-driven vs. engine-level.** Buildings, units, weapons, costs, and tech tree are YAML in `mods/sungrid/rules/*.yaml`, composing existing OpenRA traits (`Power`, `Cargo`, `Reservable`, `AttackBase`, `Health`, etc.) — this covers nearly the entire building roster. New C# trait work is reserved for the one thing YAML genuinely can't express: the Grid Reserve vault/deposit/hold-to-win mechanic (Phase 3). Core engine changes (`OpenRA.Game`, netcode, renderer) are avoided entirely unless a named friction point forces it.

**Fastest path to a playable prototype:** (1) fork `mods/ra` → `mods/sungrid`, verify it boots and plays identically under the new mod id — no rule changes yet; (2) layer in reflavored buildings via YAML only, still no new traits; (3) only then start the Grid Reserve trait work, since it's the one piece that can't be done in pure YAML. This means a genuinely playable build exists after step 1, before any new C# code is written.

**Biggest technical unknowns:**
1. The Grid Reserve win-condition hook — needs to plug into OpenRA's elimination-oriented `MissionObjectives` framework with a hold-a-threshold-with-countdown condition that stays deterministic/lockstep-safe in multiplayer. Highest-risk item in the roadmap; merits a small 1v1 design spike before Phase 3 is considered "in progress."
2. New HUD/scoreboard elements via OpenRA's `ChromeLayout`/widget system — feasible but more verbose than it looks; budget real time.
3. Keeping the new Vault/Reserve state deterministic and replay-safe like existing `PlayerResources`/`Silo`-style traits.
4. Locking an art/sprite pipeline before more than one contributor touches assets (Phase 5).
5. OpenRA's stock AI (Lua-scripted) has no native awareness of custom win conditions — "AI understands Grid Reserve" is intentionally bounded to "doesn't ignore it," not "plays it well" (Phase 4).

---

## 3. Phased roadmap

Full detail — objective, why, deliverables, code scope, data/content scope, testing scope, milestone, exit criteria, biggest risk, explicit non-goals — for every phase lives in [`ROADMAP.md`](ROADMAP.md). Summary table:

| Phase | Objective | Milestone | Exit criteria (short) |
|---|---|---|---|
| 0 | Repository bootstrap and architecture setup | `P0: Bootstrap` | Docs, labels, milestones, first issues all in place |
| 1 | Baseline playable shell on OpenRA | `P1: Baseline Shell` | `mods/sungrid` (forked from `mods/ra`) launches and plays a full skirmish |
| 2 | First solarpunk content layer | `P2: First Content Pass` | 3+ new/reflavored buildings playable without regressions |
| 3 | Economic victory mode MVP | `P3: Grid Reserve MVP` | 3+ player match winnable via Grid Reserve, toggle works, a raid demonstrably disrupts a leader |
| 4 | UI, balance, AI, multiplayer iteration | `P4: Playtest Hardening` | External testers complete a full multiplayer match with no desyncs/crashes |
| 5 | Expanded buildings / faction flavor / polish | `P5: Faction Flavor` | Full 10-building roster balanced, distinct visual identity — this is the MVP release point |
| 6+ | Diplomacy / shared-resource systems (conditional) | `P6: Diplomacy (conditional)` | Only starts if Phase 3-5 playtests show sustained demand |

---

## 4. MVP definition

**Essential features for the smallest external-playtestable MVP:**
- A launchable `mods/sungrid` mod, distinct from stock `mods/ra`, with its own identity in the OpenRA mod chooser.
- The full 10-building roster from [`BUILDINGS.md`](BUILDINGS.md), balanced enough for a complete match.
- Classic destruction victory, fully working, as the default mode.
- Grid Reserve economic victory mode, toggleable, balanced against real playtests (see [`GAME_MODES.md`](GAME_MODES.md)).
- A functional (not necessarily strong) skirmish AI that doesn't actively ignore Grid Reserve.
- Stable multiplayer (dedicated server or lobby-hosted) for 2-6 players without desyncs.
- A distinct, coherent visual identity — not necessarily fully custom art, but not a recolored RA reskin either.

**Intentionally excluded from MVP:** a second faction, campaign/story missions, diplomacy or alliance mechanics, shared/pooled Reserve, spectator tooling beyond the basic scoreboard, competitive-strength AI.

**What players should be able to experience:** a complete, replayable RTS match — scout, expand, build an economy and a base, fight or raid opponents, and win either by elimination or by banking and defending enough Grid Reserve to trigger and hold a Lockdown countdown — in a setting that visibly reads as lush eco-solarpunk rather than a Red Alert reskin.

**"Ready for first public testers" means:** Phase 5's exit criteria are met (full roster, balanced, visually distinct), Phase 4's multiplayer stability bar is cleared, and at least one internal/closed playtest of 3+ players has completed a Grid Reserve win without anyone describing the winning strategy as "just hide and wait."

---

## 5. Economic victory mode: Grid Reserve

Full spec in [`GAME_MODES.md`](GAME_MODES.md). Summary:

**Recommended name:** **Grid Reserve** (candidates considered: Energy Surplus, Sunbank Protocol, Reserve Threshold, Solvency Protocol).

**Mechanic:** A new **Vault** building converts spendable Credits into a locked, non-spendable **Reserve** pool. Deposits are irreversible and rate-capped per tick. Each Vault has a capacity cap, forcing multiple exposed Vaults to reach a real target. Destroying an enemy Vault drains ~50% of its Reserve and rewards the attacker — this is what keeps harassment and raiding relevant under this mode.

**Win condition:** reaching the map's Reserve target triggers a broadcast **Grid Lockdown** countdown (60-120s); holding Reserve at/above target for the full countdown wins; dropping below target (e.g., a Vault is destroyed) cancels the countdown.

**Example targets** (medium map): ~15,000/player baseline, roughly a 5% per-player discount at higher counts — e.g. 30,000 (2p), 40,000 (3p), 48,000 (4p), 63,000 (6p) on a medium map; see the full size × player-count table in `GAME_MODES.md`.

**HUD/scoreboard:** per-player Reserve bar with numeric target, broadcast banner/audio on Lockdown start/cancel, minimap reveal of Vault locations once a player hits 50% of target, end-of-match scoreboard showing final Reserve for all players.

**Anti-stalemate:** "Grid Decay" slowly drains all players' Reserve if nobody triggers a Lockdown within a time window, forcing the race to resolve.

**Anti-turtle:** 50% minimap reveal, per-Vault capacity caps forcing exposure, no combat/defensive synergy granted by Vaults, deposit-rate caps preventing last-second panic-banking.

**Why harassment/map pressure remain relevant:** the mode redirects what's worth attacking (Vaults) rather than removing the incentive to attack — a large undefended Reserve is a bigger prize than a player who spent everything on units.

**Why 3+ players:** in 1v1, hoarding is a pure two-body optimization race identical in shape to destruction play. With 3+, a leading hoarder becomes the shared target of the whole table once revealed — dogpile dynamics, opportunistic raiding, and kingmaking only exist with three or more seats.

**Deferred to later revisions:** diplomacy-gated Vault protection, shared/pooled Reserve between allies, alliance-split victory, per-faction Reserve bonuses, spectator tooling beyond the basic scoreboard.

---

## 6. Building plan

Full detail — fantasy, gameplay purpose, prerequisites, likely counters, implementation complexity, MVP staging — for all 10 buildings lives in [`BUILDINGS.md`](BUILDINGS.md). Categorized summary:

| Building | Category | Staging | Complexity |
|---|---|---|---|
| Solar Array | Energy | MVP (Phase 2) | Low |
| Battery Bank (Vault) | Energy / Economy | MVP (Phase 3) | High |
| Recycling Depot | Economy | MVP (Phase 2) | Medium |
| Cryptominer | Economy | Mid-term (Phase 5) | Medium |
| Datacenter for AI | Economy / Intelligence | Mid-term (Phase 5) | Medium |
| Drone Bay | Logistics | Mid-term (Phase 5) | Medium-High |
| Grid Defense Turret | Defense | Mid-term (Phase 5) | Medium |
| Smart Grid Relay | Energy / Logistics | Later | Medium |
| Resilience Shelter | Defense | Later | Medium |
| Sensor Array | Intelligence | Later | Low |

---

## 7. GitHub execution model

Full detail in [`CONTRIBUTING.md`](CONTRIBUTING.md). Summary:

- **Repo structure:** upstream engine (`OpenRA.*`) untouched by default; `mods/ra` etc. as unmodified references; `mods/sungrid` as the active mod; `docs/` for design docs.
- **Branch strategy:** `bleed` is the protected integration branch; short-lived `feature/*`/`claude/*` branches per issue; no direct pushes to `bleed`.
- **Milestones:** one per roadmap phase (`P0: Bootstrap` through `P6: Diplomacy (conditional)`).
- **Label taxonomy:** `phase:0`-`phase:6`, `type:design`/`content`/`engine`/`docs`/`bug`, `area:economy`/`energy`/`defense`/`intelligence`/`logistics`/`grid-reserve`, `risk:scope-trap`, `good-first-issue`.
- **RFC workflow:** any `type:engine` change, or any change to a rule already documented in `GAME_MODES.md`/`BUILDINGS.md`, gets a `type:design` issue first; docs update in the same PR as (or immediately before) the implementation.
- **PR checklist:** linked issue + milestone; RFC linked if engine-level; docs updated if a documented rule changed; manually playtested; no untouched-directory violations; builds cleanly.
- **Release strategy:** internal builds off `bleed` per phase exit criteria; first public-facing tag at the Phase 5/MVP point.
- **Changelog:** starts at Phase 1 (first playable build), one plain-language entry per merged PR, grouped by phase.
- **Contributor onboarding:** README → VISION → ROADMAP → ARCHITECTURE → pick an issue matching the current milestone.
- **Claude Code usage:** default to `mods/sungrid/` and `docs/`; treat any `OpenRA.*` engine diff as requiring explicit justification; prefer YAML/Lua over new C# traits; never push directly to `bleed`; keep sessions scoped to one issue/phase item.

---

## 8. Documentation plan

| File | Purpose | Core sections |
|---|---|---|
| `README.md` | Front door for the repo | Project summary, quick links to all docs, play/build instructions, license |
| `VISION.md` | Why this project exists and what makes it different | Design pillars, tone, vanilla-RA comparison table, explicit non-goals |
| `ROADMAP.md` | Phase-by-phase execution plan | Per-phase objective/deliverables/scope/exit criteria/risk/non-goals table |
| `ARCHITECTURE.md` | Technical strategy | Repo structure decision, data-driven vs. engine-level split, fastest path to prototype, named friction points |
| `GAME_MODES.md` | Economic victory mode spec | Naming, mechanic, win condition, target tables, HUD, anti-stalemate/turtle rules, why 3+ players |
| `BUILDINGS.md` | Content roster | Per-building fantasy/purpose/prereqs/counters/complexity/staging, categorized |
| `ART_DIRECTION.md` | Visual/tone direction | Tone, guardrails, readability rules, palette, asset pipeline notes |
| `CONTRIBUTING.md` (docs/) | Sungrid-specific contributor workflow | Repo structure, branches, milestones, labels, RFC process, PR checklist, release/changelog, Claude Code usage |
| `LICENSE_NOTES.md` | Licensing clarity | GPLv3 inheritance, EA non-affiliation, original-asset licensing, open decisions |
| `CLAUDE.md` (root) | AI-session navigation map | What this repo is, directory map, doc index, principles, current status, working conventions |
| `BLUEPRINT.md` (this file) | Single-read master plan | All of the above, condensed and cross-linked |

---

## 9. First 10 GitHub issues

See the issues opened alongside this PR for the live versions; summarized here for reference:

1. **Scaffold `mods/sungrid` from `mods/ra` template** — Phase 1. Fork the mod directory, update `mod.yaml` metadata (id/title/icon), no rule changes. *Depends on: this docs PR merged.* *DoD: mod appears in the OpenRA mod chooser under its own name.*
2. **Verify baseline playable shell** — Phase 1. Launch `mods/sungrid`, play a full skirmish vs. AI, confirm destruction win/loss works. *Depends on: #1.* *DoD: a complete match can be played start-to-finish with no crashes.*
3. **Set up CI build for the Sungrid mod** — Phase 0/1. Extend existing CI workflow to build/validate `mods/sungrid`. *Depends on: #1.* *DoD: CI fails on a broken mod build.*
4. **Add Solar Array + Battery Bank building stubs** — Phase 2. YAML-only reflavor of the power plant and silo-equivalent; Battery Bank here is placeholder economy only, not yet the Grid Reserve Vault. *Depends on: #2.* *DoD: both buildable and functional in a skirmish.*
5. **Add Recycling Depot** — Phase 2. Refinery-adjacent economy building with a salvage-based income stream. *Depends on: #2.* *DoD: buildable, produces Credits from battlefield wreckage in a test match.*
6. **RFC: Grid Reserve trait design** — Phase 3, `type:design`. Design the Vault deposit/capacity/decay/win-condition trait before writing it. *Depends on: #2.* *DoD: RFC issue resolved, `GAME_MODES.md`/`ARCHITECTURE.md` updated if the design shifts from the current spec.*
7. **Implement Grid Reserve Vault trait + win condition** — Phase 3, `type:engine`. The actual C# implementation per the resolved RFC. *Depends on: #6.* *DoD: a 1v1 match can be won via Grid Reserve in a local test.*
8. **Add Grid Reserve HUD/scoreboard elements** — Phase 3. Reserve bars, Lockdown broadcast, minimap reveal at 50%. *Depends on: #7.* *DoD: all HUD elements visible and correct in a test match.*
9. **3-4 player Grid Reserve playtest + balance pass** — Phase 3/4. Structured playtest specifically probing turtle strategies and raid disruption of Lockdown countdowns. *Depends on: #8.* *DoD: at least one match won via Grid Reserve with a documented Vault raid affecting the outcome.*
10. **Set up first external playtest build/packaging** — Phase 4/5 prep. Package a build testers can install and run, with basic instructions. *Depends on: #9.* *DoD: a non-team playtester successfully installs and completes a match unassisted.*

---

## 10. Next 3 Claude Code prompts

After this planning PR merges, these are the next three prompts to run, in order:

1. *"Fork `mods/ra` into a new `mods/sungrid` mod: copy the directory, update `mod.yaml` (id, title, description, icon path) to Sungrid Protocol branding, and make no other rule changes. Verify it builds and appears as a separate entry in the OpenRA mod chooser. This is issue #1/#2 from `docs/BLUEPRINT.md` section 9."*
2. *"In `mods/sungrid`, add Solar Array (power plant reflavor), Battery Bank (silo reflavor, placeholder economy only — not yet the Grid Reserve Vault), and Recycling Depot (refinery-adjacent salvage income) as YAML-only content changes composing existing OpenRA traits. No new C# code. Playtest a skirmish to confirm no regressions to the baseline shell. This is issues #4/#5 from `docs/BLUEPRINT.md` section 9."*
3. *"Write the Grid Reserve RFC (issue #6): a concrete C# trait design for the Vault building — deposit/withdrawal-forbidden state, per-tick deposit rate cap, per-Vault capacity cap, destruction-drain behavior, and the hold-to-win Lockdown countdown hook into OpenRA's win-condition framework — checked specifically for lockstep-determinism in multiplayer. Update `docs/GAME_MODES.md` and `docs/ARCHITECTURE.md` if the concrete design differs from the current spec, before any implementation code is written."*

---

## A. Recommended MVP scope

The full 10-building roster, both victory modes (destruction default, Grid Reserve toggleable), a functional (not strong) AI, stable 2-6 player multiplayer, and a visually distinct (not necessarily fully custom-art) solarpunk identity. See section 4 above for the full breakdown.

## B. Recommended Phase 0 checklist

- [x] Write and merge the full `docs/` design doc set (`VISION`, `ROADMAP`, `ARCHITECTURE`, `GAME_MODES`, `BUILDINGS`, `ART_DIRECTION`, `CONTRIBUTING`, `LICENSE_NOTES`, `BLUEPRINT`) and `CLAUDE.md`.
- [x] Reframe root `README.md` around Sungrid Protocol while preserving OpenRA attribution/license requirements.
- [ ] Create GitHub milestones `P0`-`P6` matching `ROADMAP.md`.
- [ ] Create the label taxonomy from `docs/CONTRIBUTING.md`.
- [ ] Open the first 10 issues (section 9 above).
- [ ] Merge this PR to `bleed`.

## C. Top 3 scope traps to avoid

1. **Pulling Phase 6 (diplomacy/shared-resource systems) forward.** It's the single biggest risk to the schedule — it's genuinely interesting but has no natural stopping point and isn't validated by any playtest data yet. Don't start it until Phase 3-5 explicitly justify it.
2. **Under-scoping Grid Reserve's anti-turtle mechanics.** If the mode ships without real exposure (minimap reveal, capacity caps, no defensive synergy), the "optimal" strategy becomes hiding in a corner — which directly kills the project's core thesis. This gets dedicated playtesting attention, not just code review.
3. **Producing custom art before mechanics are validated.** Phase 2's content pass should ship on recolored/placeholder art; committing to a full asset pipeline (Phase 5) before Grid Reserve and the core building set have survived real playtests risks expensive rework.

## D. Single next action

Merge this docs PR, then run Claude Code prompt #1 from section 10: fork `mods/ra` into `mods/sungrid` and get a genuinely playable (if unstyled) build launching under its own mod identity. Everything else in the roadmap is downstream of that one step existing and working.
