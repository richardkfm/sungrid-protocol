# Sungrid Protocol

A solarpunk reinterpretation of the classic Red Alert RTS formula — renewable power, smart grids, drone logistics, and resilient settlements, built on the [OpenRA](https://www.openra.net) engine. Still a real RTS: base building, unit counters, scouting, raiding, and map control are all intact. The first big design departure is an optional **economic victory mode** ("Grid Reserve") that makes saving money a real alternative win path, alongside the classic destruction victory.

This repository follows the [OpenRAModSDK](https://github.com/OpenRA/OpenRAModSDK) pattern — the OpenRA engine is a pinned, fetched build dependency (see [Technical Architecture](docs/ARCHITECTURE.md) for why, and the trade-offs of that choice). Sungrid Protocol content lives in `mods/sungrid`: real Red Alert-derived gameplay, the full building roster, and the Grid Reserve economic victory mode are implemented and playable, with a first pass of the game's own visual identity (UI chrome, terrain palette) now landing on top of that — see [Roadmap](docs/ROADMAP.md) for exact phase-by-phase status.

<img width="848" height="1264" alt="sungridprotocol_newart_v3" src="https://github.com/user-attachments/assets/208966c6-4a62-411d-bbfd-ba9c69d7d2f3" />

## Start here

* [`docs/BLUEPRINT.md`](docs/BLUEPRINT.md) — the full project blueprint: vision, technical strategy, phased roadmap, MVP definition, economic victory mode spec, building plan, and GitHub workflow, all in one place.
* [`docs/VISION.md`](docs/VISION.md) — design pillars and what differentiates Sungrid Protocol from vanilla Red Alert-style play.
* [`docs/ROADMAP.md`](docs/ROADMAP.md) — phase-by-phase deliverables, exit criteria, and explicit non-goals.
* [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — how this is structured as an OpenRA mod, and what's data-driven vs. engine-level.
* [`docs/GAME_MODES.md`](docs/GAME_MODES.md) — full spec for the Grid Reserve economic victory mode.
* [`docs/BUILDINGS.md`](docs/BUILDINGS.md) — the initial building roster. Full unit/building roster by faction, plus a makeover-vs-new-mechanic breakdown and parity flags: <a href="https://raw.githack.com/richardkfm/sungrid-protocol/main/docs/concept-art/faction-roster-dossier.html">via githack</a>
* [`docs/ENERGY_BALANCE.md`](docs/ENERGY_BALANCE.md) — the energy-scarcity rebalance and faction power-identity pass (Wind Turbine Array, Hydrogen Plant, Drone Bay parity, drone/AI Datacenter power-gating), plus scoped suggestions for a future unit/vehicle reskin pass.
* [`docs/PLAYTESTING.md`](docs/PLAYTESTING.md) — step-by-step build/launch/troubleshooting instructions to actually run a local match.
* [`docs/ART_DIRECTION.md`](docs/ART_DIRECTION.md) — tone and visual direction. Non-canonical concept art: <a href="https://raw.githack.com/richardkfm/sungrid-protocol/main/docs/concept-art/phase5-pixel-mockups.html">via githack</a> 
* [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md) — branch strategy, labels, RFC process, PR checklist, release strategy (Sungrid-specific — for engine-level C# style, see the root [`CONTRIBUTING.md`](CONTRIBUTING.md)).
* [`docs/LICENSE_NOTES.md`](docs/LICENSE_NOTES.md) — license inheritance and EA non-affiliation.
* [`docs/BACKLOG.md`](docs/BACKLOG.md) — first 10 engineering issues, held here because GitHub Issues is currently disabled on this repo; import as real issues once it's enabled.
* [`CLAUDE.md`](CLAUDE.md) — navigation map for AI-assisted development sessions in this repo.

## Play

Playable today: `mods/sungrid` holds real Red Alert-derived gameplay (Phase 1), the full Phase 2/5 building roster, and the Grid Reserve economic victory mode (Phase 3), all confirmed working end-to-end in a local skirmish. Sungrid Protocol launches as its own entry in the OpenRA mod chooser — see [`docs/PLAYTESTING.md`](docs/PLAYTESTING.md) for exact build/launch/troubleshooting steps. Visual identity work is underway (Phase 6): UI chrome and the temperate terrain tileset have a first-pass palette reskin toward `docs/ART_DIRECTION.md`'s locked palette. Cursors, the remaining tilesets, and unit/audio identity (Phase 7) are still stock OpenRA/RA art — see `docs/ROADMAP.md`'s Phase 6/7 for the plan.

EA has not endorsed and does not support this product. See [`docs/LICENSE_NOTES.md`](docs/LICENSE_NOTES.md) for the full non-affiliation and licensing notes.


### Download

You don't need to build from source to try it — pre-built Windows installers, macOS disk images, and Linux AppImages are published on the [Releases](https://github.com/richardkfm/sungrid-protocol/releases) page for each tagged version. Grab the package for your platform and run it; building (below) is only needed if you want the latest `main` or plan to make changes.

## Building

This repo uses the OpenRA Mod SDK build flow — the engine is not vendored, it's fetched on demand:

* **Linux/macOS:** run `make` (this calls `fetch-engine.sh` automatically, then builds). Launch with `./launch-game.sh`.
* **Windows:** run `make.cmd`. Launch with `launch-game.cmd`.

See [`docs/PLAYTESTING.md`](docs/PLAYTESTING.md) for a full walkthrough including common launch errors (`.NET` runtime mismatches, crash log locations), and [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for how the engine pinning (`mod.config`'s `ENGINE_VERSION`) works.

## Contribute

* Read [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md) first for Sungrid Protocol's workflow (branches, labels, RFCs, PR checklist).
* Read and follow the [Code of Conduct](CODE_OF_CONDUCT.md).
* Engine-level C# style still follows the upstream OpenRA coding standard linked from the root [`CONTRIBUTING.md`](CONTRIBUTING.md) (the Mod SDK's own contributing guidelines).

## Upstream OpenRA

Sungrid Protocol builds on the OpenRA engine and community tooling. If you're looking for the original OpenRA project (Red Alert, Tiberian Dawn, and Dune 2000 mods): [https://github.com/OpenRA/OpenRA](https://github.com/OpenRA/OpenRA), [https://www.openra.net](https://www.openra.net), [Discord](https://discord.openra.net).

## License

Copyright (c) OpenRA Developers and Contributors, and Sungrid Protocol Contributors.
This project is free software, available under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of
the License, or (at your option) any later version. For more
information, see [COPYING](COPYING) and [`docs/LICENSE_NOTES.md`](docs/LICENSE_NOTES.md).
