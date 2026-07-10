# Sungrid Protocol — Technical Architecture

## Repo structure decision

`richardkfm/sungrid-protocol` is currently a **direct fork of the OpenRA engine repository itself** (default branch `bleed`), containing the full engine source tree (`OpenRA.Game/`, `OpenRA.Mods.Common/`, `OpenRA.Mods.Cnc/`, `OpenRA.Mods.D2k/`, `OpenRA.Platforms.Default/`, `OpenRA.Server/`, `OpenRA.Test/`, `OpenRA.Utility/`) plus the stock mods (`mods/ra`, `mods/cnc`, `mods/d2k`, `mods/ts`), all unmodified from upstream. This is **not** the lightweight [OpenRAModSDK](https://github.com/OpenRA/OpenRAModSDK) repo, which normally treats the engine as a downloaded dependency and keeps a mod's repo small.

**Decision: keep this repo as the full engine fork, and build Sungrid Protocol as a new mod directory (`mods/sungrid`) forked from `mods/ra`, rather than migrating to a separate OpenRAModSDK-based repo.**

Rationale:
- Zero migration risk — restructuring into the SDK pattern now would burn Phase 0 time on infrastructure instead of content, with no gameplay payoff.
- `mods/ra` is a complete, working reference implementation sitting right next to where the new mod will live — the fastest possible starting point.
- The full engine tree is already available in-repo if a Phase 3+ friction point genuinely requires an engine-level (not mod-level) change — no separate checkout needed.
- Trade-off accepted: this repo is heavier than a typical mod repo, and pulling upstream OpenRA engine updates later means merging against a full engine tree rather than bumping a dependency version. This is an acceptable cost given the "fastest realistic route to a playable prototype" priority; it can be revisited post-MVP if upstream sync pain becomes real.

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

1. Fork `mods/ra` → `mods/sungrid` (copy, rename mod id/metadata, no rule changes). Verify it launches and plays identically to RA under the new mod id. This is all of Phase 1.
2. Layer in Phase 2's reflavored buildings via YAML only — no new traits, no new art pipeline yet (recolor/retexture existing sprites). Verify nothing regresses.
3. Only then start Phase 3's Grid Reserve trait work, since it's the one piece that can't be done purely in YAML.

This sequencing means there is a genuinely playable (if visually undifferentiated) build after Phase 1, well before any new C# code is written — which de-risks the whole project against "big rewrite that never ships."

## Biggest technical unknowns / friction points

1. **Win-condition hook for Grid Reserve.** OpenRA's `MissionObjectives`/conquest-victory framework is built around elimination-style conditions. A hold-a-threshold-with-a-countdown win condition needs a new trait that plugs into that framework cleanly, is deterministic (OpenRA is lockstep-networked — any new state must replicate identically across all clients), and doesn't desync in multiplayer. This is the single highest-risk technical item in the whole roadmap and should get a design spike (small prototype, 1v1 only) before Phase 3 is considered "in progress" for real.
2. **HUD/scoreboard additions.** New UI elements (Reserve bars, Lockdown countdown, minimap reveal) go through OpenRA's `ChromeLayout` YAML + widget system. Feasible, but budget real time for it — UI work in OpenRA's widget system is more verbose than it looks.
3. **Deterministic economy state.** The Vault's deposit/decay/reveal logic must be replayable and lockstep-safe like all other OpenRA game state (no floating point drift, no client-only randomness). Model it the same way existing `PlayerResources`/`Silo`-style traits already do.
4. **Asset pipeline for new art.** Phase 5's original art pass needs a decided pixel-art/sprite pipeline (palette, resolution, animation frame conventions) consistent with `docs/ART_DIRECTION.md` before more than one artist (human or AI-assisted) touches it, or assets won't compose visually.
5. **AI script depth.** OpenRA's built-in AI is script-driven (Lua) and not naturally aware of custom win conditions. Phase 4's "AI understands Grid Reserve" deliverable is bounded on purpose (see Phase 4 risk note in `docs/ROADMAP.md`) because teaching the stock AI genuinely good judgment about a brand-new mechanic is open-ended.

## What this repo will look like after Phase 1

```
mods/
  ra/            # unmodified upstream reference, kept for diffing
  sungrid/       # new: Sungrid Protocol mod (forked from ra)
    mod.yaml
    rules/
    sequences/
    maps/
    chrome/
    ...
```

Upstream engine directories (`OpenRA.Game/`, `OpenRA.Mods.*/`, etc.) are expected to stay untouched through at least Phase 5. If a future phase needs an engine change, it should be a small, clearly-justified diff reviewed with the same scrutiny as any upstream OpenRA contribution — not a place to accumulate hacks.
