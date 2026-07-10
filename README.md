# Sungrid Protocol

A solarpunk reinterpretation of the classic Red Alert RTS formula — renewable power, smart grids, drone logistics, and resilient settlements, built on the [OpenRA](https://www.openra.net) engine. Still a real RTS: base building, unit counters, scouting, raiding, and map control are all intact. The first big design departure is an optional **economic victory mode** ("Grid Reserve") that makes saving money a real alternative win path, alongside the classic destruction victory.

This repository is a fork of the OpenRA engine (see [Technical Architecture](docs/ARCHITECTURE.md) for why, and the trade-offs of that choice). Sungrid Protocol content lives in `mods/sungrid` once Phase 1 scaffolding lands (see [Roadmap](docs/ROADMAP.md)) — as of this writing, that directory does not exist yet; this repo is at the Phase 0 documentation-bootstrap stage.

## Start here

* [`docs/BLUEPRINT.md`](docs/BLUEPRINT.md) — the full project blueprint: vision, technical strategy, phased roadmap, MVP definition, economic victory mode spec, building plan, and GitHub workflow, all in one place.
* [`docs/VISION.md`](docs/VISION.md) — design pillars and what differentiates Sungrid Protocol from vanilla Red Alert-style play.
* [`docs/ROADMAP.md`](docs/ROADMAP.md) — phase-by-phase deliverables, exit criteria, and explicit non-goals.
* [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — how this is structured as an OpenRA mod, and what's data-driven vs. engine-level.
* [`docs/GAME_MODES.md`](docs/GAME_MODES.md) — full spec for the Grid Reserve economic victory mode.
* [`docs/BUILDINGS.md`](docs/BUILDINGS.md) — the initial building roster.
* [`docs/ART_DIRECTION.md`](docs/ART_DIRECTION.md) — tone and visual direction.
* [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md) — branch strategy, labels, RFC process, PR checklist, release strategy (Sungrid-specific — for engine-level C# style, see the root [`CONTRIBUTING.md`](CONTRIBUTING.md)).
* [`docs/LICENSE_NOTES.md`](docs/LICENSE_NOTES.md) — license inheritance and EA non-affiliation.
* [`CLAUDE.md`](CLAUDE.md) — navigation map for AI-assisted development sessions in this repo.

## Play

Not yet playable as a distinct mod — see the roadmap. Once Phase 1 lands, Sungrid Protocol will launch as its own entry in the OpenRA mod chooser alongside the stock mods included in this fork (Red Alert, Tiberian Dawn, Dune 2000), which remain present as unmodified reference/upstream content.

EA has not endorsed and does not support this product. See [`docs/LICENSE_NOTES.md`](docs/LICENSE_NOTES.md) for the full non-affiliation and licensing notes.

## Building the engine

This repo is a full OpenRA engine checkout. See [`INSTALL.md`](INSTALL.md) for environment setup and the [OpenRA Compiling guide](https://github.com/OpenRA/OpenRA/wiki/Compiling) for engine build instructions — these are unchanged from upstream OpenRA.

## Contribute

* Read [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md) first for Sungrid Protocol's workflow (branches, labels, RFCs, PR checklist).
* Read and follow the [Code of Conduct](CODE_OF_CONDUCT.md).
* Engine-level C# contributions still follow the upstream [`CONTRIBUTING.md`](CONTRIBUTING.md) style guide.

## Upstream OpenRA

Sungrid Protocol builds on the OpenRA engine and community tooling. If you're looking for the original OpenRA project (Red Alert, Tiberian Dawn, and Dune 2000 mods): [https://github.com/OpenRA/OpenRA](https://github.com/OpenRA/OpenRA), [https://www.openra.net](https://www.openra.net), [Discord](https://discord.openra.net).

## License

Copyright (c) OpenRA Developers and Contributors, and Sungrid Protocol Contributors.
This project is free software, available under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of
the License, or (at your option) any later version. For more
information, see [COPYING](COPYING) and [`docs/LICENSE_NOTES.md`](docs/LICENSE_NOTES.md).
