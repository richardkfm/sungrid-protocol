# Sungrid Protocol

A solarpunk reinterpretation of the classic Red Alert RTS formula — renewable power, smart grids, drone logistics, and resilient settlements, built on the [OpenRA](https://www.openra.net) engine. Still a real RTS: base building, unit counters, scouting, raiding, and map control are all intact. The first big design departure is an optional **economic victory mode** ("Grid Reserve") that makes saving money a real alternative win path, alongside the classic destruction victory.

This repository follows the [OpenRAModSDK](https://github.com/OpenRA/OpenRAModSDK) pattern — the OpenRA engine is a pinned, fetched build dependency (see [Technical Architecture](docs/ARCHITECTURE.md) for why, and the trade-offs of that choice). Sungrid Protocol content lives in `mods/sungrid` (currently the SDK's placeholder example template, renamed) — as of this writing it doesn't hold real gameplay yet; that's Phase 1 (see [Roadmap](docs/ROADMAP.md)).

<img width="848" height="1264" alt="ra-sungrid-protocol-draftq" src="https://github.com/user-attachments/assets/77dac1b2-9888-41ba-a7b7-cbb0018c5ab5" />

## Start here

* [`docs/BLUEPRINT.md`](docs/BLUEPRINT.md) — the full project blueprint: vision, technical strategy, phased roadmap, MVP definition, economic victory mode spec, building plan, and GitHub workflow, all in one place.
* [`docs/VISION.md`](docs/VISION.md) — design pillars and what differentiates Sungrid Protocol from vanilla Red Alert-style play.
* [`docs/ROADMAP.md`](docs/ROADMAP.md) — phase-by-phase deliverables, exit criteria, and explicit non-goals.
* [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — how this is structured as an OpenRA mod, and what's data-driven vs. engine-level.
* [`docs/GAME_MODES.md`](docs/GAME_MODES.md) — full spec for the Grid Reserve economic victory mode.
* [`docs/BUILDINGS.md`](docs/BUILDINGS.md) — the initial building roster.
* [`docs/ART_DIRECTION.md`](docs/ART_DIRECTION.md) — tone and visual direction. Non-canonical concept art: <a href="https://raw.githack.com/richardkfm/sungrid-protocol/main/docs/concept-art/phase5-pixel-mockups.html">via githack</a> 
* [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md) — branch strategy, labels, RFC process, PR checklist, release strategy (Sungrid-specific — for engine-level C# style, see the root [`CONTRIBUTING.md`](CONTRIBUTING.md)).
* [`docs/LICENSE_NOTES.md`](docs/LICENSE_NOTES.md) — license inheritance and EA non-affiliation.
* [`docs/BACKLOG.md`](docs/BACKLOG.md) — first 10 engineering issues, held here because GitHub Issues is currently disabled on this repo; import as real issues once it's enabled.
* [`CLAUDE.md`](CLAUDE.md) — navigation map for AI-assisted development sessions in this repo.

## Play

Not yet playable with real gameplay content — `mods/sungrid` is still the SDK's placeholder example template as of this writing (see the roadmap). Once Phase 1 lands, Sungrid Protocol will launch as its own entry in the OpenRA mod chooser with content forked from Red Alert.

EA has not endorsed and does not support this product. See [`docs/LICENSE_NOTES.md`](docs/LICENSE_NOTES.md) for the full non-affiliation and licensing notes.

<img width="1024" height="1280" alt="ra-sungrid_visual" src="https://github.com/user-attachments/assets/31a89549-de39-42be-add0-bf962f9ca148" />

## Building

This repo uses the OpenRA Mod SDK build flow — the engine is not vendored, it's fetched on demand:

* **Linux/macOS:** run `make` (this calls `fetch-engine.sh` automatically, then builds). Launch with `./launch-game.sh`.
* **Windows:** run `make.cmd`. Launch with `launch-game.cmd`.

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for how the engine pinning (`mod.config`'s `ENGINE_VERSION`) works.

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
