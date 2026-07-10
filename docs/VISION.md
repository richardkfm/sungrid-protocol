# Sungrid Protocol — Vision

## What it is

Sungrid Protocol is a solarpunk reinterpretation of the classic Red Alert RTS formula, built on the OpenRA engine. It keeps the readable, skill-testing bones of 90s RTS design — base building, unit counters, scouting, raiding, map control — and reframes the fiction and the economy around renewable power, smart grids, drone logistics, and resilient settlements. It is hopeful and strategic, not utopian or goofy: factions are still at war, resources are still contested, and losing your base still hurts.

The project's first real design innovation is not the art direction, it's the **economic victory mode**: an optional win condition that makes *saving* money a legitimate alternative to spending it on offense or defense, without turning the game into a passive economy race.

## Design pillars

1. **Classic RTS legibility first.** Every unit, building, and system must read clearly on screen at a glance — silhouette, color, and UI legibility are not sacrificed for theme.
2. **Solarpunk as a lens, not a coat of paint.** Renewable energy, circular economy, and smart-grid logistics should change what players *do* (power management, recycling, grid defense), not just what things are called.
3. **Spend vs. save is a first-class decision.** The economic victory mode exists to make hoarding capital a real strategic axis, contested the same way territory is.
4. **Pressure never disappears.** Scouting, harassment, raiding, and map control stay relevant in every mode, including the economic one — a mode that rewards passive turtling is a failed mode.
5. **Data-driven before engine-driven.** New content ships as OpenRA YAML/Lua/mod rules wherever physically possible; engine-level C# changes are reserved for things that are provably impossible any other way.
6. **Small reversible phases.** Every phase ships something playable and can be rolled back without breaking the previous phase's promises.
7. **Destruction victory stays intact.** The classic "kill everyone" win condition is never removed — the economic mode is additive and optional.
8. **3+ players is the design target for new modes.** Diplomacy, betrayal, and opportunistic raiding only get interesting with three or more seats at the table; new social mechanics are designed for that context first.

## What makes it different from vanilla Red Alert-style play

| Vanilla RA-style play | Sungrid Protocol |
|---|---|
| Ore/Tiberium-style single resource, spend it or lose tempo | Power and capital are legible, gridded systems (solar, batteries, storage) with a real "bank it" option |
| Only win condition is elimination | Elimination **and** an optional economic victory (hold a capital threshold) |
| Turtling is usually just slow, not punished | Turtling under the economic mode is actively exposed (visible reserves, raidable vaults, decay pressure) |
| Tech tree is purely military escalation | Tech tree includes eco-infrastructure (recycling, batteries, drone logistics) that trades off against military tech |
| Aesthetic: Cold War industrial/military | Aesthetic: lush eco-industrial — solar arrays, green retrofits, drone logistics, resilient settlements over ruins |

## What Sungrid Protocol is explicitly not (yet)

- Not a diplomacy or alliance simulator — treaties, reparations, and resource-sharing are later-phase ideas, only pursued if the economic victory mode proves itself first.
- Not a economy-only "builder" game — combat, raiding, and destruction remain core, non-optional systems.
- Not a new engine or a total conversion of OpenRA's renderer/netcode — we build within OpenRA's data-driven trait system as far as it will take us.
