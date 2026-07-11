# CLAUDE.md — Navigation map for Sungrid Protocol

This repo follows the [OpenRAModSDK](https://github.com/OpenRA/OpenRAModSDK) pattern: the OpenRA engine is a pinned, fetched build dependency (`engine/`, gitignored, not committed), not vendored source. Read this first before exploring the tree.

## What this repo is

`richardkfm/sungrid-protocol` is a Mod SDK-style repo for Sungrid Protocol, a solarpunk reinterpretation of the classic Red Alert RTS formula, built on the OpenRA engine. It started as a direct fork of the full OpenRA engine repository, but that was superseded in Phase 0 (before any mod content existed) in favor of the standard SDK pattern — see `docs/ARCHITECTURE.md` for the full rationale.

## Directory map

**Fetched engine dependency — never commit, never edit directly:**
- `engine/` — downloaded/built by `fetch-engine.sh` (or `make`), pinned via `mod.config`'s `ENGINE_VERSION`. Contains `OpenRA.Game`, `OpenRA.Mods.Common`, stock mods (`mods/ra`, `mods/cnc`, `mods/d2k`, `mods/ts`), etc. Gitignored — if a friction point genuinely needs an engine-level change, pin `ENGINE_VERSION` to a personal engine fork's commit instead of vendoring source into this repo (see `docs/ARCHITECTURE.md`).

**Mod/content territory — where Sungrid Protocol work actually happens:**
- `mods/sungrid/` — **the Sungrid Protocol mod content** (rules/YAML, sequences, maps, chrome, fluent strings). Currently the SDK's example-mod template renamed to Sungrid branding — Phase 1's job is to replace this placeholder content with real gameplay forked from `mods/ra` (pulled from `engine/mods/ra` once fetched, or the public OpenRA/OpenRA repo).
- `OpenRA.Mods.Sungrid/` — mod-specific C# project. Currently the SDK's example stub traits (`ColorPickerColorShift`, `PlayerColorShift`), renamed. This is where the Phase 3 Grid Reserve trait will live.
- `mod.config`, `fetch-engine.sh`/`.cmd`, `Makefile`/`make.cmd`/`make.ps1`, `launch-game.*`, `launch-dedicated.*`, `utility.*`, `Sungrid.sln`, `packaging/` — SDK scaffolding, all mod-scale (not the engine's own build/packaging tooling).

**Design docs:**
- `docs/BLUEPRINT.md` — master document, full project blueprint in one place.
- `docs/VISION.md` — design pillars, tone, what differentiates Sungrid Protocol from vanilla RA.
- `docs/ROADMAP.md` — phase-by-phase plan (0 through 6+) with deliverables, exit criteria, explicit non-goals.
- `docs/ARCHITECTURE.md` — OpenRA technical strategy, data-driven vs. engine-level split, known friction points.
- `docs/GAME_MODES.md` — full spec for the Grid Reserve economic victory mode.
- `docs/BUILDINGS.md` — the 10-building initial roster, categorized and staged.
- `docs/ART_DIRECTION.md` — solarpunk tone/visual guardrails. `docs/concept-art/` holds non-canonical HTML concept sketches (currently the Phase 5 building dossier) — discussion drafts, not shippable assets.
- `docs/CONTRIBUTING.md` — Sungrid-specific workflow (branches, labels, RFCs, PR checklist). Root `CONTRIBUTING.md` is the Mod SDK's own contributing guidelines (still points to OpenRA's coding-standard wiki for engine-level style).
- `docs/LICENSE_NOTES.md` — GPLv3 inheritance, EA non-affiliation, original-asset licensing notes.

## Project goals and principles (condensed from `docs/VISION.md`)

1. Classic RTS legibility first — theme never overrides silhouette/UI readability.
2. Solarpunk as a lens that changes gameplay (power management, recycling, grid defense), not just reskinned names.
3. Spend vs. save is a first-class strategic decision (this is what Grid Reserve is for).
4. Pressure never disappears — scouting, harassment, raiding, and map control stay relevant in every mode, including the economic one.
5. Data-driven before engine-driven — YAML/Lua first, new C# only when provably necessary.
6. Small, reversible phases — every phase ships something playable and can be rolled back cleanly.
7. Destruction victory stays intact — Grid Reserve is additive and optional, never a replacement.
8. 3+ players is the target for new social/economic mechanics — diplomacy and shared-resource systems are deliberately deferred until this is validated.

## Key architecture decisions already made

- **Mod SDK pattern, not a vendored engine fork** — the engine is fetched/pinned via `mod.config` + `fetch-engine.sh`, not committed to this repo. Superseded the original "full engine fork" decision before any mod content existed (see `docs/ARCHITECTURE.md` for the full reasoning).
- Data-driven-first: buildings/units/rules go through YAML composing existing OpenRA traits wherever possible; new C# traits (in `OpenRA.Mods.Sungrid/`) are reserved for things YAML genuinely can't express (currently: only the Grid Reserve vault/win-condition mechanic).
- Destruction victory is the permanent default; Grid Reserve is a toggleable lobby option.
- "Grid Reserve" is the recommended/working name for the economic victory mode (see `docs/GAME_MODES.md` for the other 4 candidates that were considered).
- Diplomacy, alliance mechanics, and shared/pooled resources are explicitly out of scope until Phase 3-5 playtests justify them (see Phase 6+ in `docs/ROADMAP.md`).

## Current status

Phase 0 is complete: the design doc set, this navigation file, a reframed `README.md`, and the Mod SDK scaffold (engine fetched/pinned rather than vendored, `mods/sungrid`/`OpenRA.Mods.Sungrid` renamed from the SDK's example template) are all in place. `mods/sungrid` currently holds the SDK's placeholder example content, not real gameplay yet — that's Phase 1. See `docs/BACKLOG.md` for the first 10 engineering issues (GitHub Issues is disabled on this repo, so they're tracked there instead of as real issues until it's enabled).

## Working conventions

- Never edit or commit anything under `engine/` — it's fetched by `fetch-engine.sh` and gitignored. If a friction point genuinely needs an engine-level change, see `docs/ARCHITECTURE.md`'s guidance on pinning to a personal engine fork instead.
- Prefer YAML/Lua trait composition in `mods/sungrid` over new C# traits in `OpenRA.Mods.Sungrid`; if a new trait seems necessary, check it against the "New C# traits" row in `docs/ARCHITECTURE.md` first.
- Keep commits/PRs scoped to one phase/issue at a time — see `docs/CONTRIBUTING.md` for the full PR checklist and label taxonomy.
- `main` is now the default/integration branch (previously `bleed`, which is kept in sync but is no longer the branch to target). Never push directly to `main`; always branch + PR.
