# Contributing to Sungrid Protocol

This document covers Sungrid Protocol's project workflow: branching, issues, RFCs, releases. For C# coding style on engine-level changes, see the root [`CONTRIBUTING.md`](../CONTRIBUTING.md) (the Mod SDK's contributing guidelines, which point to OpenRA's coding-standard wiki).

## Repository structure

```
engine/                              # fetched by fetch-engine.sh, pinned via mod.config — gitignored, never commit or edit
mods/sungrid/                        # Sungrid Protocol mod content — this is where almost all work happens
OpenRA.Mods.Sungrid/                 # mod-specific C# traits (Grid Reserve lands here)
mod.config, fetch-engine.sh, Makefile, launch-*, utility.*, Sungrid.sln, packaging/   # SDK scaffolding
docs/                                # design docs (this file, VISION, ROADMAP, ARCHITECTURE, GAME_MODES, BUILDINGS, ART_DIRECTION, LICENSE_NOTES, BLUEPRINT, BACKLOG)
CLAUDE.md                            # navigation map for AI-assisted sessions
```

## Branch strategy

- `bleed` — default/integration branch, always playable. Nothing merges here that doesn't at least build.
- `claude/*` or `feature/*` — short-lived branches per issue/phase item. Named after the issue where possible (e.g. `feature/grid-reserve-vault`).
- No direct pushes to `bleed` — everything goes through a PR, even for a solo-founder-plus-Claude workflow, so the diff history stays reviewable.
- Tag releases off `bleed` once a phase's exit criteria (per `docs/ROADMAP.md`) are met.

## Milestones

One GitHub milestone per roadmap phase, named to match `docs/ROADMAP.md` exactly:

`P0: Bootstrap`, `P1: Baseline Shell`, `P2: First Content Pass`, `P3: Grid Reserve MVP`, `P4: Playtest Hardening`, `P5: Faction Flavor`, `P6: Diplomacy (conditional)`.

Every issue and PR should be assigned to the milestone of the phase it belongs to; an issue with no clear phase is a signal it's premature (check it against the "do NOT attempt yet" list in that phase's roadmap entry).

## Label taxonomy

| Label | Meaning |
|---|---|
| `phase:0` … `phase:6` | Which roadmap phase this belongs to |
| `type:design` | RFC / design proposal, not yet implementation |
| `type:content` | Data-driven YAML/art/audio work |
| `type:engine` | New or modified C# trait / engine-level change |
| `type:docs` | Documentation only |
| `type:bug` | Regression or broken behavior |
| `area:economy`, `area:energy`, `area:defense`, `area:intelligence`, `area:logistics` | Matches the building categories in `docs/BUILDINGS.md` |
| `area:grid-reserve` | Anything touching the economic victory mode specifically |
| `risk:scope-trap` | Flagged as touching something explicitly deferred in the roadmap — extra scrutiny before merging |
| `good-first-issue` | Self-contained, low-context-required |

## RFC / design proposal workflow

Anything in the `type:engine` category, or anything that changes a rule already documented in `docs/GAME_MODES.md` or `docs/BUILDINGS.md`, gets an RFC first:

1. Open an issue labeled `type:design` describing the problem, the proposed change, and which doc(s) it would update.
2. Resolve open questions in the issue thread (or via a short doc update proposal) before writing implementation code.
3. Once agreed, update the relevant doc (`GAME_MODES.md`, `BUILDINGS.md`, `ARCHITECTURE.md`, etc.) in the same PR as the implementation, or in a docs-only PR immediately before it — the docs should never silently drift from what's actually implemented.

Pure `type:content` changes (a new building's YAML stats, a balance tweak) don't need a full RFC — a normal PR description explaining the change is enough.

## PR checklist

- [ ] Linked to an issue and the correct phase milestone
- [ ] If `type:engine`: matching RFC issue linked, and the change is additive (doesn't alter unrelated existing traits/behavior)
- [ ] If it changes a documented rule: the relevant `docs/*.md` file is updated in the same PR
- [ ] Manually playtested (skirmish match minimum) if it touches buildable content or a game mode
- [ ] No changes to anything under `engine/` (it's fetched, gitignored, and never committed)
- [ ] Builds cleanly (`make` / the repo's standard build command)

## Release strategy

- Internal/dev builds off `bleed` after every merged phase-exit-criteria milestone (see `docs/ROADMAP.md` exit criteria per phase).
- First tagged release intended for external humans is the Phase 5 exit point — see the MVP definition in `docs/BLUEPRINT.md`.
- Pre-MVP, tags are for the founder's/testers' own tracking (`v0.0.x-phaseN`) — not public releases.

## Changelog

Keep a `CHANGELOG.md` at the repo root once Phase 1 ships a playable build (not needed for Phase 0's docs-only bootstrap). One entry per merged PR, grouped by phase, written in plain language a playtester would understand (not raw commit messages).

## Contributor onboarding

1. Read `README.md`, then `docs/VISION.md` and `docs/ROADMAP.md` for the "why" and "what's next."
2. Read `docs/ARCHITECTURE.md` before touching any code — it defines what's data-driven (default) vs. engine-level (exception).
3. Pick an open issue matching the current phase's milestone; if none exist, propose one against the roadmap rather than inventing new scope.
4. Follow the PR checklist above.

## Using Claude Code safely in this repo

- Default Claude Code sessions to `mods/sungrid/`, `OpenRA.Mods.Sungrid/`, and `docs/` — nothing under `engine/` should ever be touched (it's fetched, gitignored). If a friction point genuinely needs an engine-level change, see `docs/ARCHITECTURE.md`'s guidance on pinning to a personal engine fork instead of vendoring source into this repo.
- Prefer data-driven (YAML/Lua) changes; a Claude session proposing a new C# trait should point to which "New C# traits" row in `docs/ARCHITECTURE.md` it satisfies.
- Never push directly to `bleed` from an automated session — always a branch + PR, even for docs.
- Keep sessions scoped to one issue/phase item at a time; a session that starts drifting into unrelated files or future-phase content is a signal to stop and re-scope, not to keep going.
