# Sungrid Protocol — Technical Architecture

## Repo structure decision

`richardkfm/sungrid-protocol` started as a **direct fork of the OpenRA engine repository itself** (default branch `bleed`), containing the full engine source tree plus the stock mods (`mods/ra`, `mods/cnc`, `mods/d2k`, `mods/ts`), unmodified from upstream. That was superseded before any mod content existed: this repo now follows the [OpenRAModSDK](https://github.com/OpenRA/OpenRAModSDK) pattern instead, where the engine is a **pinned, fetched build dependency** rather than vendored source.

**Decision: the engine lives under `engine/` (gitignored, downloaded by `fetch-engine.sh`/`make`), pinned via `mod.config`'s `ENGINE_VERSION`. Mod content lives in `mods/sungrid/` (a renamed copy of the SDK's `OpenRA.Mods.Example`/`mods/example` starter template) plus the `OpenRA.Mods.Sungrid/` C# project for mod-specific traits.**

Why this superseded the original full-fork decision: the original rationale ("zero migration risk" from not restructuring) undervalued that the migration cost is close to zero *only* before any mod content exists — and by Phase 0 docs-only, it still didn't. Every phase that passes makes switching later more expensive, so this was the cheapest point the project would ever be at to make the change, and it's also the structure OpenRA's own docs recommend for new mods.

Rationale for the SDK pattern:
- Matches the standard, documented path for new OpenRA mods — not a nonstandard structure future contributors (human or AI) have to re-learn.
- Much smaller, faster repo and CI — no engine source to check out, diff, or build alongside mod content.
- Upstream OpenRA engine updates become a version bump (`mod.config`'s `ENGINE_VERSION`) instead of a merge against a full vendored tree.
- `ENGINE_VERSION` is pinned to `bf4102a029f132824d682069fce1105d56fc5e96` — the exact commit this repo forked from — so the SDK migration itself introduces zero behavioral drift. Bumping to a newer engine version later is a deliberate, separate decision (see `docs/CONTRIBUTING.md`'s RFC process).
- If a genuine engine-level change is ever needed for Grid Reserve (see friction point #1 below), the SDK pattern still accommodates it: pin `ENGINE_VERSION`/`AUTOMATIC_ENGINE_SOURCE` to a personal engine fork's commit instead of upstream's. That remains lighter-weight than vendoring the full engine tree in this repo permanently.

## Data-driven vs. engine-level split

| Layer | Examples | Default assumption |
|---|---|---|
| YAML rules (`mods/sungrid/rules/*.yaml`) | Buildings, units, weapons, tech tree, costs, power values | **Always try this first.** This is how OpenRA mods normally differentiate from each other. |
| Sequences/art config | Sprite sheets, palettes, UI chrome layout | Data-driven; new art is a content/pipeline problem, not a code problem. |
| Lua map/mission scripting | AI hints, scripted triggers, campaign logic | Data-driven; used for Phase 4 AI behavior tuning. |
| Existing C# traits, recombined | `Power`, `Cargo`, `Reservable`, `AttackBase`, `Selectable`, `Health`, etc. applied to new units/buildings via YAML | Data-driven — this covers the large majority of Phase 2 and Phase 5 building work (Solar Array is just `Power` with a new sprite; Drone Bay is largely `Cargo`/`Reservable` composition). |
| New C# traits | Grid Reserve deposit/withdrawal tracking, hold-to-win countdown, HUD reserve bar | **Engine-level, but scoped and additive.** Only Phase 3 is expected to need genuinely new trait code. |
| Core engine changes (`OpenRA.Game`, netcode, renderer) | — | **Avoid entirely if possible.** Nothing in the current roadmap is expected to require this. If a friction point below turns out to force it, that's a stop-and-reassess moment, not a "just do it" moment. |

The rule of thumb: if it can be expressed as YAML composing existing traits, it's data-driven and low-risk. If it needs new *game state that OpenRA's existing traits don't track* (like a locked, non-spendable currency pool with a countdown), it needs a new trait — but that trait should be small, additive, and not modify how existing modes/traits behave.

## Fastest path to a playable prototype

1. **Done in Phase 0:** the SDK scaffold itself — `mod.config`, `fetch-engine.sh`, and `mods/sungrid`/`OpenRA.Mods.Sungrid` renamed from the SDK's example template — fetches the pinned engine and builds/launches to the in-game main menu under the `sungrid` mod id. This proves the scaffold works before any real gameplay content exists.
2. **Phase 1:** replace the example template's placeholder rules/sequences/maps in `mods/sungrid` with real content forked from `mods/ra`'s gameplay (pulled from the fetched `engine/mods/ra` reference or the public OpenRA/OpenRA repo, since `mods/ra` is no longer vendored locally). Verify it launches and plays a full skirmish.
3. Layer in Phase 2's reflavored buildings via YAML only — no new traits, no new art pipeline yet (recolor/retexture existing sprites). Verify nothing regresses.
4. Only then start Phase 3's Grid Reserve trait work in `OpenRA.Mods.Sungrid`, since it's the one piece that can't be done purely in YAML.

This sequencing means there is a genuinely playable (if visually undifferentiated) build after Phase 1, well before any new C# code is written — which de-risks the whole project against "big rewrite that never ships."

## Biggest technical unknowns / friction points

1. **Win-condition hook for Grid Reserve.** OpenRA's `MissionObjectives`/conquest-victory framework is built around elimination-style conditions. A hold-a-threshold-with-a-countdown win condition needs a new trait that plugs into that framework cleanly, is deterministic (OpenRA is lockstep-networked — any new state must replicate identically across all clients), and doesn't desync in multiplayer. This is the single highest-risk technical item in the whole roadmap and should get a design spike (small prototype, 1v1 only) before Phase 3 is considered "in progress" for real.
2. **HUD/scoreboard additions.** New UI elements (Reserve bars, Lockdown countdown, minimap reveal) go through OpenRA's `ChromeLayout` YAML + widget system. Feasible, but budget real time for it — UI work in OpenRA's widget system is more verbose than it looks.
3. **Deterministic economy state.** The Vault's deposit/decay/reveal logic must be replayable and lockstep-safe like all other OpenRA game state (no floating point drift, no client-only randomness). Model it the same way existing `PlayerResources`/`Silo`-style traits already do.
4. **Asset pipeline for new art.** Phase 5's original art pass needs a decided pixel-art/sprite pipeline (palette, resolution, animation frame conventions) consistent with `docs/ART_DIRECTION.md` before more than one artist (human or AI-assisted) touches it, or assets won't compose visually.
5. **AI script depth.** OpenRA's built-in AI is script-driven (Lua) and not naturally aware of custom win conditions. Phase 4's "AI understands Grid Reserve" deliverable is bounded on purpose (see Phase 4 risk note in `docs/ROADMAP.md`) because teaching the stock AI genuinely good judgment about a brand-new mechanic is open-ended.

## What this repo looks like

```
mod.config                  # MOD_ID, ENGINE_VERSION pin, packaging metadata
fetch-engine.sh / .cmd      # downloads/builds the pinned engine into engine/ (gitignored)
Makefile, make.cmd/.ps1     # build entry points (call fetch-engine automatically)
launch-game.sh/.cmd, launch-dedicated.sh/.cmd, utility.sh/.cmd
Sungrid.sln                 # references OpenRA.Mods.Sungrid + engine/OpenRA.Game, engine/OpenRA.Mods.Common
OpenRA.Mods.Sungrid/         # mod-specific C# (Grid Reserve trait lands here in Phase 3)
mods/sungrid/                # mod content: rules/, sequences/, maps/, chrome/, fluent/, etc.
packaging/                   # SDK-style installer scripts, mod-scale (not the full engine's multi-mod packaging)
engine/                      # gitignored — fetched by fetch-engine.sh, not committed
```

There is no vendored `OpenRA.Game/`, `OpenRA.Mods.Common/`, or stock `mods/ra`/`mods/cnc`/`mods/d2k`/`mods/ts` in this repo anymore — they're part of the fetched `engine/` dependency. If a future phase needs a genuine engine-level change, pin `ENGINE_VERSION` to a personal engine fork's commit rather than reintroducing a vendored tree (see the rationale above).
