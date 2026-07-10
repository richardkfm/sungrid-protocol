# Sungrid Protocol — Building Plan

Ten buildings, staged across the roadmap in `docs/ROADMAP.md`. Treat every fantasy/name here as a strong starting point, not a locked final design — expect iteration once these hit a playtest.

## Category map

| Category | Buildings |
|---|---|
| Energy | Solar Array, Battery Bank (Vault), Smart Grid Relay |
| Economy | Recycling Depot, Cryptominer, Datacenter for AI |
| Defense | Grid Defense Turret, Resilience Shelter |
| Intelligence | Sensor Array, Datacenter for AI (dual-category) |
| Logistics | Drone Bay |

## Building details

### 1. Solar Array
- **Category:** Energy
- **Fantasy:** A field of tracking solar panels feeding the base grid — the visual signature of the faction's power economy.
- **Gameplay purpose:** Direct replacement for the classic power plant; primary power-generation building.
- **Prerequisites:** Construction Yard.
- **Likely counters:** Airstrikes/artillery targeting exposed power infrastructure (same counterplay as classic RA power plants — low armor, high strategic value).
- **Implementation complexity:** Low — existing `Power` trait, reflavored art/sequence.
- **Staging:** MVP (Phase 2).

### 2. Battery Bank (Vault)
- **Category:** Energy / Economy
- **Fantasy:** Grid-scale battery storage that can be permanently committed to the settlement's long-term reserve rather than drawn back down.
- **Gameplay purpose:** The deposit structure for the Grid Reserve economic victory mode (see `docs/GAME_MODES.md`) — converts spendable Credits into locked, irreversible Reserve.
- **Prerequisites:** Solar Array (requires an established power economy first), Refinery-equivalent economy building.
- **Likely counters:** Direct assault/raiding once Reserve inside is worth stealing-by-destruction; artillery and air harassment are effective since Vaults have no inherent defensive synergy.
- **Implementation complexity:** High — this is the one building that needs new C# trait work (deposit tracking, capacity, destruction-drain, Lockdown countdown hook).
- **Staging:** MVP (Phase 3) — required for the economic victory mode to exist at all.

### 3. Recycling Depot
- **Category:** Economy
- **Fantasy:** A circular-economy facility that reclaims scrap from destroyed units/buildings (yours and the battlefield's) and converts it back into usable Credits.
- **Gameplay purpose:** Refinery-adjacent economy building; gives a second, salvage-based income stream that rewards map control and post-battle cleanup over pure resource-field control.
- **Prerequisites:** Construction Yard, Solar Array.
- **Likely counters:** Denying the player battlefield access (so there's nothing to salvage), direct destruction like any economy building.
- **Implementation complexity:** Medium — likely reuses/extends existing salvage-adjacent traits (there is prior art in OpenRA mods for wreck-harvesting mechanics) rather than needing wholly new systems.
- **Staging:** MVP (Phase 2).

### 4. Cryptominer
- **Category:** Economy
- **Fantasy:** Repurposed compute infrastructure grinding through proof-of-work for a legacy financial network — a deliberately morally ambiguous building in an eco-solarpunk setting (cheap power in, real money out, but it's not "clean" the way Solar Array is).
- **Gameplay purpose:** A high power-draw, high-Credit-output economy building — trades grid stability (drains power hard) for economic upside, creating a real tension with the Solar Array/power budget.
- **Prerequisites:** Solar Array (needs power headroom to be worth building), Tech Center-equivalent.
- **Likely counters:** Power denial (destroy Solar Arrays and the Cryptominer goes offline or throttles), it's a high-value/low-defense target for raids given its output.
- **Implementation complexity:** Medium — power-draw-scaled income likely needs a small custom trait (existing `Power`/economy traits don't natively support "income that scales with available power headroom"), but no win-condition-level complexity.
- **Staging:** Mid-term (Phase 5).

### 5. Datacenter for AI
- **Category:** Economy / Intelligence
- **Fantasy:** Racks of compute serving the faction's logistics AI and battlefield analytics — the "brains" behind smart-grid coordination.
- **Gameplay purpose:** Dual-purpose building — modest passive Credit/tech bonus plus an intelligence effect (e.g. periodic radar pulse or unit-vision bonus), tying economic investment to information advantage rather than pure output.
- **Prerequisites:** Tech Center-equivalent, Solar Array.
- **Likely counters:** High-value raid target once its intelligence bonus is felt on the battlefield; power denial reduces its effect the same way as Cryptominer.
- **Implementation complexity:** Medium — likely composes existing intelligence/reveal traits with a standard economy trait rather than needing new systems.
- **Staging:** Mid-term (Phase 5).

### 6. Drone Bay
- **Category:** Logistics
- **Fantasy:** Autonomous delivery drones ferrying resources and reinforcements across contested terrain, reducing dependence on vulnerable ground supply lines.
- **Gameplay purpose:** Logistics building enabling faster resource transport and/or rapid unit repositioning between owned structures — a mobility/economy hybrid that rewards map-spanning infrastructure over turtled play.
- **Prerequisites:** Construction Yard, Recycling Depot or equivalent economy building.
- **Likely counters:** Anti-air, since drone traffic is the obvious vulnerability; destroying the Drone Bay itself halts the logistics network.
- **Implementation complexity:** Medium-High — likely composes existing `Cargo`/`Reservable`/transport traits, but genuinely novel routing behavior could push into new-trait territory; flagged as a Phase 5 friction point to scope carefully before committing.
- **Staging:** Mid-term (Phase 5).

### 7. Grid Defense Turret
- **Category:** Defense
- **Fantasy:** A point-defense structure drawing directly off the local grid — hits harder when the grid is healthy, weaker when power is strained.
- **Gameplay purpose:** Standard defensive structure, but with its damage/rate-of-fire tied to the base's current power surplus — creates a direct tactical link between the energy economy and combat strength.
- **Prerequisites:** Solar Array.
- **Likely counters:** Power denial (destroy power plants to weaken the turret before assaulting), standard artillery/air counters to static defense.
- **Implementation complexity:** Medium — power-scaled combat stats likely need a small custom trait extension over the stock `AttackBase`/turret traits.
- **Staging:** Mid-term (Phase 5).

### 8. Smart Grid Relay
- **Category:** Energy / Logistics
- **Fantasy:** A grid-balancing relay station that lets power flow between distant parts of a sprawling, decentralized base.
- **Gameplay purpose:** Extends effective power range/pooling between disconnected base clusters, enabling more spread-out, harder-to-snipe-in-one-strike base layouts.
- **Prerequisites:** Solar Array.
- **Likely counters:** Destroying the Relay can fragment a spread base's power pool, so it becomes a high-value target in decentralized layouts.
- **Implementation complexity:** Medium — depends on how OpenRA's stock power-pooling model can be extended; may require a small trait if power pooling isn't naturally range-limited today.
- **Staging:** Later (post-Phase 5, revisit once base-spread playstyles are observed in playtests).

### 9. Resilience Shelter
- **Category:** Defense
- **Fantasy:** A hardened civil-defense structure that keeps a settlement's core functions running under sustained attack — the "don't lose everything at once" building.
- **Gameplay purpose:** Damage-mitigation/comeback structure — e.g. reduces splash damage to nearby structures or grants a brief repair pulse when the base takes heavy losses, softening total wipeouts without preventing them.
- **Prerequisites:** Construction Yard, Tech Center-equivalent.
- **Likely counters:** Alpha-strike/overwhelm tactics that outpace its mitigation window; it blunts damage, it doesn't prevent loss.
- **Implementation complexity:** Medium — likely a conditional damage-modifier trait applied to nearby structures, similar in shape to existing aura/support-power traits.
- **Staging:** Later (post-Phase 5).

### 10. Sensor Array
- **Category:** Intelligence
- **Fantasy:** A distributed sensor mesh reading grid load, drone traffic, and terrain across the map — battlefield awareness as smart-grid telemetry.
- **Gameplay purpose:** Wide-radius vision/detection building (including stealth/cloak detection if the roster ever needs it), rewarding investment in map awareness over blind aggression.
- **Prerequisites:** Tech Center-equivalent.
- **Likely counters:** High-value raid/airstrike target once its intelligence value is evident; doesn't defend itself.
- **Implementation complexity:** Low — largely composes existing reveal/detector traits already in OpenRA's common mod.
- **Staging:** Later (post-Phase 5).
