# Sungrid Protocol — License Notes

## Inherited license

Sungrid Protocol is built on the OpenRA engine, which is licensed under the **GNU General Public License v3.0 or later**. The engine is fetched as a pinned build dependency (`engine/`, via `fetch-engine.sh`) rather than vendored into this repo — GPLv3 compliance for the engine itself is satisfied through OpenRA's own upstream distribution, same as any Mod SDK-based mod. This repo's own code (`mods/sungrid/`, `OpenRA.Mods.Sungrid/`) is distributed under GPLv3 as well (see [`COPYING`](../COPYING) at the repo root, copied from upstream OpenRA), since any executable code loaded by the engine must be GPLv3-compatible.

Practical implications:
- Any code contributed to `mods/sungrid/` or `OpenRA.Mods.Sungrid/` is distributed under GPLv3, same as upstream OpenRA.
- Mod **data** files (rules/YAML, art, audio) are not source code, so — per standard OpenRA Mod SDK convention — they can be licensed separately from the GPLv3 code if desired (see "Original asset licensing" below).
- Do not add dependencies with licenses incompatible with GPLv3 without checking compatibility first.

## EA / Command & Conquer non-affiliation

OpenRA's stock mods (`mods/ra`, `mods/cnc`, `mods/d2k`, bundled with the fetched engine) reimplement classic Westwood/EA game rules using original code, and EA has not endorsed and does not support OpenRA (this disclaimer already appears in the upstream `README.md`). Sungrid Protocol carries the same posture: it is a new, original game built on the OpenRA engine, not a Red Alert reskin distributing EA assets. `mods/sungrid` currently still holds the SDK's placeholder example content (Phase 0); Phase 1 replaces it with content ported from `mods/ra`'s gameplay. Any placeholder content still recognizable as Red Alert-specific IP (unit names tied to the C&C universe, EA-owned imagery) should be treated as temporary scaffolding to be replaced by original Sungrid Protocol content no later than Phase 2, not shipped in a public build.

## Original asset licensing (Phase 5+)

Once Phase 5 starts producing original art/audio for Sungrid Protocol:
- New art/audio assets can be licensed separately from the GPLv3 code if desired (OpenRA's own asset conventions distinguish code license from content license in places), but the choice should be made explicitly and documented here once decided — do not leave it implicit.
- Any third-party asset (fonts, sound effects, music) brought in from outside must have a license compatible with public redistribution, with attribution recorded in this file.
- AI-assisted art/audio generation used for prototyping should be treated as placeholder unless the specific tool/model's output terms are confirmed compatible with the project's chosen distribution license.

## Open items

This file will need a decision once Phase 5 art production starts: whether original Sungrid Protocol assets ship under GPLv3 (matching code) or a separate content license (e.g. CC-BY-SA, matching conventions used by some other OpenRA-based projects). Track that decision as a `type:design` RFC issue when Phase 5 begins.
