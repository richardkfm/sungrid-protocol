# Sungrid Protocol — Technical Architecture

## Repo structure decision

`richardkfm/sungrid-protocol` started as a **direct fork of the OpenRA engine repository itself** (default branch `bleed`), containing the full engine source tree plus the stock mods (`mods/ra`, `mods/cnc`, `mods/d2k`, `mods/ts`), unmodified from upstream. That was superseded before any mod content existed: this repo now follows the [OpenRAModSDK](https://github.com/OpenRA/OpenRAModSDK) pattern instead, where the engine is a **pinned, fetched build dependency** rather than vendored source.

**Decision: the engine lives under `engine/` (gitignored, downloaded by `fetch-engine.sh`/`make`), pinned via `mod.config`'s `ENGINE_VERSION`. Mod content lives in `mods/sungrid/` (started as a renamed copy of the SDK's `OpenRA.Mods.Example`/`mods/example` starter template, replaced with real content in Phase 1) plus the `OpenRA.Mods.Sungrid/` C# project for mod-specific traits.**

Why this superseded the original full-fork decision: the original rationale ("zero migration risk" from not restructuring) undervalued that the migration cost is close to zero *only* before any mod content exists — and by Phase 0 docs-only, it still didn't. Every phase that passes makes switching later more expensive, so this was the cheapest point the project would ever be at to make the change, and it's also the structure OpenRA's own docs recommend for new mods.

Rationale for the SDK pattern:
- Matches the standard, documented path for new OpenRA mods — not a nonstandard structure future contributors (human or AI) have to re-learn.
- Much smaller, faster repo and CI — no engine source to check out, diff, or build alongside mod content.
- Upstream OpenRA engine updates become a version bump (`mod.config`'s `ENGINE_VERSION`) instead of a merge against a full vendored tree.
- `ENGINE_VERSION` was originally pinned to `bf4102a029f132824d682069fce1105d56fc5e96` — the exact commit this repo forked from — so the SDK migration itself introduced zero behavioral drift. It has been bumped **once**, to `461c7c73c6565f1e2ba557701ad58766d734a428`: a single cherry-picked compile fix on top of that same commit, not an engine upgrade (`docs/BACKLOG.md` issue #20). Any future bump is a deliberate, separate decision (see `docs/CONTRIBUTING.md`'s RFC process).
- If a genuine engine-level change is ever needed, the SDK pattern still accommodates it by pinning `ENGINE_VERSION`/`AUTOMATIC_ENGINE_SOURCE` at a patched commit instead of upstream's — lighter-weight than vendoring the full engine tree permanently. In practice that patched commit lives on an `engine-patch/*` branch **in this repo** (its own pre-Phase-0 history still contains the full engine tree), not in a separate personal fork; this is exactly how issue #20's fix shipped. **Read `CLAUDE.md`'s "Engine version pinning" section before touching any of this** — those branches must never be merged into `main` or deleted, and that mistake has already been made twice.

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

1. **Win-condition hook for Grid Reserve — RESOLVED.** Shipped in Phase 3 as `GridReserveController`, hooking the stock `MissionObjectives` framework; see `docs/GAME_MODES.md` for the implementation and its one deliberate coupling (a ruleset enabling the mode must also have a required objective configured). The original concern, kept for context: OpenRA's `MissionObjectives`/conquest-victory framework is built around elimination-style conditions. A hold-a-threshold-with-a-countdown win condition needs a new trait that plugs into that framework cleanly, is deterministic (OpenRA is lockstep-networked — any new state must replicate identically across all clients), and doesn't desync in multiplayer. This is the single highest-risk technical item in the whole roadmap and should get a design spike (small prototype, 1v1 only) before Phase 3 is considered "in progress" for real.
2. **HUD/scoreboard additions.** New UI elements (Reserve bars, Lockdown countdown, minimap reveal) go through OpenRA's `ChromeLayout` YAML + widget system. Feasible, but budget real time for it — UI work in OpenRA's widget system is more verbose than it looks.
3. **Deterministic economy state.** The Vault's deposit/decay/reveal logic must be replayable and lockstep-safe like all other OpenRA game state (no floating point drift, no client-only randomness). Model it the same way existing `PlayerResources`/`Silo`-style traits already do.
4. **Asset pipeline for new art — RESOLVED in practice, still first-pass.** The pipeline settled on committed Python generators writing indexed PngSheets against the stock RA player palette; its hard-won rules (1-bit alpha, shadow stencils vs. painted contact shadows, downscale bleed on team-color accents, facings as genuine viewpoints) are collected in `CLAUDE.md`'s "Art pipeline" section. A human-designer pass over the output is still open.
5. **AI script depth — PARTIALLY RESOLVED.** Bots now play Grid Reserve via a mod-side `GridReserveBotModule` (C#, not Lua) rather than script hints; what's still open is bots preferentially raiding enemy Vaults, which needs engine-level squad target-selection changes (`docs/BACKLOG.md` issue #67). The original concern: OpenRA's built-in AI is script-driven (Lua) and not naturally aware of custom win conditions. Phase 4's "AI understands Grid Reserve" deliverable is bounded on purpose (see Phase 4 risk note in `docs/ROADMAP.md`) because teaching the stock AI genuinely good judgment about a brand-new mechanic is open-ended.

## What this repo looks like

```
mod.config                  # MOD_ID, ENGINE_VERSION pin, packaging metadata
fetch-engine.sh / .cmd      # downloads/builds the pinned engine into engine/ (gitignored)
Makefile, make.cmd/.ps1     # build entry points (call fetch-engine automatically)
launch-game.sh/.cmd, launch-dedicated.sh/.cmd, utility.sh/.cmd
Sungrid.sln                 # references OpenRA.Mods.Sungrid + engine/OpenRA.Game, engine/OpenRA.Mods.Common
OpenRA.Mods.Sungrid/         # mod-specific C# — GridReserve/ (the economic victory mode), Rendering/ (two SDK example traits)
mods/sungrid/                # mod content: rules/, sequences/, maps/, chrome/, fluent/, bits/, uibits/, etc.
mods/sungrid-content/        # content-installer mod (the player's own Red Alert asset files)
packaging/                   # SDK-style installer scripts, mod-scale (not the full engine's multi-mod packaging)
engine/                      # gitignored — fetched by fetch-engine.sh, not committed
```

There is no vendored `OpenRA.Game/`, `OpenRA.Mods.Common/`, or stock `mods/ra`/`mods/cnc`/`mods/d2k`/`mods/ts` in this repo anymore — they're part of the fetched `engine/` dependency. If a future phase needs a genuine engine-level change, pin `ENGINE_VERSION` at a patched commit on an `engine-patch/*` branch rather than reintroducing a vendored tree (see the rationale above and `CLAUDE.md`'s "Engine version pinning" section).
