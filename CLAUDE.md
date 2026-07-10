# CLAUDE.md — Navigation map for Sungrid Protocol

This repo is large (a full game engine fork) and most of it is upstream OpenRA, not Sungrid Protocol content. Read this first before exploring the tree.

## What this repo is

`richardkfm/sungrid-protocol` is a **direct fork of the OpenRA engine repository** (default branch `bleed`) — not the lightweight [OpenRAModSDK](https://github.com/OpenRA/OpenRAModSDK) template. Sungrid Protocol, a solarpunk reinterpretation of the classic Red Alert RTS formula, is being built as a new mod (`mods/sungrid`) inside this engine tree, forked from the stock `mods/ra` mod. See `docs/ARCHITECTURE.md` for the full rationale on why this structure was chosen over migrating to the Mod SDK pattern.

## Directory map

**Upstream engine — do not modify casually.** Treat any change here as requiring explicit justification against a named friction point in `docs/ARCHITECTURE.md`:
- `OpenRA.Game/`, `OpenRA.Mods.Common/`, `OpenRA.Mods.Cnc/`, `OpenRA.Mods.D2k/`, `OpenRA.Platforms.Default/`, `OpenRA.Server/`, `OpenRA.Test/`, `OpenRA.Utility/`, `OpenRA.Launcher/`, `OpenRA.WindowsLauncher/`

**Mod/content territory — where Sungrid Protocol work actually happens:**
- `mods/ra` — stock upstream Red Alert mod, kept unmodified as a reference template. Do not edit; fork from it instead.
- `mods/cnc`, `mods/d2k`, `mods/ts` — other stock upstream mods, not otherwise relevant to Sungrid Protocol work.
- `mods/sungrid` — **the Sungrid Protocol mod.** Does not exist yet as of this writing (repo is at Phase 0, docs-only). Will be created in Phase 1 by forking `mods/ra`. This is where nearly all future rules/YAML, sequences, maps, and mod-specific C# traits will live.

**Design docs:**
- `docs/BLUEPRINT.md` — master document, full project blueprint in one place.
- `docs/VISION.md` — design pillars, tone, what differentiates Sungrid Protocol from vanilla RA.
- `docs/ROADMAP.md` — phase-by-phase plan (0 through 6+) with deliverables, exit criteria, explicit non-goals.
- `docs/ARCHITECTURE.md` — OpenRA technical strategy, data-driven vs. engine-level split, known friction points.
- `docs/GAME_MODES.md` — full spec for the Grid Reserve economic victory mode.
- `docs/BUILDINGS.md` — the 10-building initial roster, categorized and staged.
- `docs/ART_DIRECTION.md` — solarpunk tone/visual guardrails.
- `docs/CONTRIBUTING.md` — Sungrid-specific workflow (branches, labels, RFCs, PR checklist). Root `CONTRIBUTING.md` is upstream OpenRA's C# style guide and still applies to engine-level changes.
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

- Fork `mods/ra` → `mods/sungrid` inside this engine repo, instead of migrating to a separate OpenRAModSDK-based repo (see `docs/ARCHITECTURE.md` for the trade-off).
- Data-driven-first: buildings/units/rules go through YAML composing existing OpenRA traits wherever possible; new C# traits are reserved for things YAML genuinely can't express (currently: only the Grid Reserve vault/win-condition mechanic).
- Destruction victory is the permanent default; Grid Reserve is a toggleable lobby option.
- "Grid Reserve" is the recommended/working name for the economic victory mode (see `docs/GAME_MODES.md` for the other 4 candidates that were considered).
- Diplomacy, alliance mechanics, and shared/pooled resources are explicitly out of scope until Phase 3-5 playtests justify them (see Phase 6+ in `docs/ROADMAP.md`).

## Current status

This PR (branch `claude/sungrid-protocol-roadmap-83d92w`) is a **docs-only Phase 0 bootstrap** — it adds the design doc set, this navigation file, and a reframed `README.md`. No `mods/sungrid` content exists yet. Next work is tracked in the first 10 GitHub issues opened alongside this PR, covering Phase 0 GitHub setup and Phase 1-3 engineering work (mod scaffolding, CI, baseline content, Grid Reserve implementation).

## Working conventions

- Don't touch upstream `OpenRA.*` engine directories unless a friction point in `docs/ARCHITECTURE.md` says it's required.
- Prefer YAML/Lua trait composition in `mods/sungrid` over new C# traits; if a new trait seems necessary, check it against the "New C# traits" row in `docs/ARCHITECTURE.md` first.
- Keep commits/PRs scoped to one phase/issue at a time — see `docs/CONTRIBUTING.md` for the full PR checklist and label taxonomy.
- Never push directly to `bleed`; always branch + PR.
