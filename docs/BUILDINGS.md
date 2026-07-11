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

**Art note (Phase 5):** buildings 4-10 below ship with placeholder art — each reuses an existing structure's sprite (`RenderSprites.Image` override) chosen for rough thematic fit, not a dedicated sprite. This mirrors Phase 2's "recolored/retextured existing art is acceptable" approach, extended to full sprite reuse since no unused building art exists in the current asset set. See `docs/ART_DIRECTION.md`'s Phase 5 asset pipeline note — a real distinct-art pass is still a separate, tracked follow-up, not done in this pass. `docs/concept-art/phase5-building-dossier.html` has non-canonical silhouette/palette sketches for these 7 as a discussion starting point ahead of that pass, and `docs/concept-art/phase5-pixel-mockups.html` follows up with a blocky faux-pixel-art pass at the same roster.

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
- **Implementation complexity:** Low, in practice — stock `GrantConditionOnPowerState` (per-player Normal/Low/Critical tiers) plus two `CashTrickler` instances gated on those conditions gives power-scaled income with no new C#. Originally estimated Medium (assumed a custom trait was needed); revised down once implemented.
- **Staging:** Implemented (Phase 5) as `SGCRY`.

### 4a. Note on power-scaled buildings (Cryptominer, Grid Defense Turret)

Both buildings originally assumed they'd need a small custom trait for power-scaled behavior. Implementation found stock `GrantConditionOnPowerState` already covers this (grants a condition based on the owner's aggregate power state), so tiered `CashTrickler`/`FirepowerMultiplier`/`ReloadDelayMultiplier` instances gated on those conditions do the job in pure YAML. Updated `docs/ARCHITECTURE.md` isn't needed since its data-driven-first framing already anticipated this as the default expectation.

### 5. Datacenter for AI
- **Category:** Economy / Intelligence
- **Fantasy:** Racks of compute serving the faction's logistics AI and battlefield analytics — the "brains" behind smart-grid coordination.
- **Gameplay purpose:** Dual-purpose building — modest passive Credit/tech bonus plus an intelligence effect (e.g. periodic radar pulse or unit-vision bonus), tying economic investment to information advantage rather than pure output.
- **Prerequisites:** Tech Center-equivalent, Solar Array.
- **Likely counters:** High-value raid target once its intelligence bonus is felt on the battlefield; power denial reduces its effect the same way as Cryptominer.
- **Implementation complexity:** Low, in practice — composes stock `CashTrickler`, `RevealsShroud`, and `DetectCloaked` (confirmed as the safer, already-verified-in-repo choice over the support-power-style periodic pulse originally described).
- **Staging:** Implemented (Phase 5) as `SGDAI`.

### 6. Drone Bay
- **Category:** Logistics
- **Fantasy:** Autonomous delivery drones ferrying resources and reinforcements across contested terrain, reducing dependence on vulnerable ground supply lines.
- **Gameplay purpose:** Logistics building enabling faster resource transport and/or rapid unit repositioning between owned structures — a mobility/economy hybrid that rewards map-spanning infrastructure over turtled play.
- **Prerequisites:** Construction Yard, Recycling Depot or equivalent economy building.
- **Likely counters:** Anti-air, since drone traffic is the obvious vulnerability; destroying the Drone Bay itself halts the logistics network.
- **Implementation complexity:** Low, in practice — scoped down deliberately per this doc's own friction-point flag. Rather than genuinely novel routing/logistics logic, implemented as a `ProximityExternalCondition` aura granting nearby friendly vehicles a `SpeedMultiplier` bonus ("drone-assisted logistics network"). No new unit, no new C#, no novel routing behavior.
- **Staging:** Implemented (Phase 5) as `SGDRN`.

### 7. Grid Defense Turret
- **Category:** Defense
- **Fantasy:** A point-defense structure drawing directly off the local grid — hits harder when the grid is healthy, weaker when power is strained.
- **Gameplay purpose:** Standard defensive structure, but with its damage/rate-of-fire tied to the base's current power surplus — creates a direct tactical link between the energy economy and combat strength.
- **Prerequisites:** Solar Array.
- **Likely counters:** Power denial (destroy power plants to weaken the turret before assaulting), standard artillery/air counters to static defense.
- **Implementation complexity:** Low, in practice — see the Cryptominer note above; `GrantConditionOnPowerState` gating `FirepowerMultiplier`/`ReloadDelayMultiplier` covers it with no new trait. Deliberately does **not** inherit `DisableOnLowPowerOrPowerDown` — the design calls for "weaker when strained," not "offline," so it stays combat-capable at low power rather than being paused like most power-consuming defenses.
- **Staging:** Implemented (Phase 5) as `SGTUR`.

### 8. Smart Grid Relay
- **Category:** Energy / Logistics
- **Fantasy:** A grid-balancing relay station that lets power flow between distant parts of a sprawling, decentralized base.
- **Gameplay purpose:** Extends effective power range/pooling between disconnected base clusters, enabling more spread-out, harder-to-snipe-in-one-strike base layouts.
- **Prerequisites:** Solar Array.
- **Likely counters:** Destroying the Relay can fragment a spread base's power pool, so it becomes a high-value target in decentralized layouts.
- **Implementation complexity:** Low, but scoped down from the original fantasy. OpenRA's stock power system already pools per-player globally (not range-limited), so there's no missing mechanic to extend — building genuine range-limited pooling would mean replacing a core engine system, which is exactly the kind of wide-blast-radius engine change `docs/ARCHITECTURE.md` says to avoid. Implemented instead as a modest flat secondary power source (same `Power` trait as Solar Array, cheaper, smaller footprint), framed narratively as grid-balancing infrastructure. The literal "extends pooling range between disconnected clusters" idea stays deferred until base-spread playstyles are actually observed in a playtest and justify the bigger engine investment.
- **Staging:** Implemented (Phase 5, scoped-down version) as `SGREL`. Pulled forward from this doc's earlier "post-Phase 5" note to match `docs/ROADMAP.md`'s Phase 5 deliverable list, which named all 7 remaining buildings — this doc's per-building staging notes hadn't been updated to match when that roadmap entry was written.

### 9. Resilience Shelter
- **Category:** Defense
- **Fantasy:** A hardened civil-defense structure that keeps a settlement's core functions running under sustained attack — the "don't lose everything at once" building.
- **Gameplay purpose:** Damage-mitigation/comeback structure — e.g. reduces splash damage to nearby structures or grants a brief repair pulse when the base takes heavy losses, softening total wipeouts without preventing them.
- **Prerequisites:** Construction Yard, Tech Center-equivalent.
- **Likely counters:** Alpha-strike/overwhelm tactics that outpace its mitigation window; it blunts damage, it doesn't prevent loss.
- **Implementation complexity:** Low, in practice — stock `ProximityExternalCondition` (grants a condition to nearby friendly actors) plus `DamageMultiplier` (gated on that condition, added to the shared `^Building` fragment so any structure can benefit) covers the damage-mitigation aura with no new trait. The "brief repair pulse on heavy losses" alternative from the original fantasy wasn't implemented — the aura alone satisfies the design intent.
- **Staging:** Implemented (Phase 5) as `SGSHL`. Pulled forward from "post-Phase 5" for the same reason as Smart Grid Relay above.

### 10. Sensor Array
- **Category:** Intelligence
- **Fantasy:** A distributed sensor mesh reading grid load, drone traffic, and terrain across the map — battlefield awareness as smart-grid telemetry.
- **Gameplay purpose:** Wide-radius vision/detection building (including stealth/cloak detection if the roster ever needs it), rewarding investment in map awareness over blind aggression.
- **Prerequisites:** Tech Center-equivalent.
- **Likely counters:** High-value raid/airstrike target once its intelligence value is evident; doesn't defend itself.
- **Implementation complexity:** Low — composes stock `RevealsShroud`, `DetectCloaked`, and `RenderDetectionCircle`, as expected.
- **Staging:** Implemented (Phase 5) as `SGSNS`. Pulled forward from "post-Phase 5" for the same reason as Smart Grid Relay above.
