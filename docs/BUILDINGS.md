# Sungrid Protocol — Building Plan

Ten buildings, staged across the roadmap in `docs/ROADMAP.md`, plus a follow-up energy-identity/scarcity pass (see `docs/ENERGY_BALANCE.md`) that added three more: Wind Turbine Array, Hydrogen Plant, and Aerial Fabrication Bay. Treat every fantasy/name here as a strong starting point, not a locked final design — expect iteration once these hit a playtest.

## Category map

| Category | Buildings |
|---|---|
| Energy | Solar Array, Battery Bank (Vault), Smart Grid Relay, Wind Turbine Array (Assembly), Hydrogen Plant (Consortium) |
| Economy | Recycling Depot, Cryptominer, Datacenter for AI |
| Defense | Grid Defense Turret, Resilience Shelter |
| Intelligence | Sensor Array, Datacenter for AI (dual-category) |
| Logistics | Drone Bay (Assembly), Aerial Fabrication Bay (Consortium) |

**Art note (Phase 5, superseded by docs/BACKLOG.md issue #34):** buildings 4-13 below originally shipped with placeholder art — each reused an existing structure's sprite (`RenderSprites.Image` override) chosen for rough thematic fit, not a dedicated sprite. Issue #34 replaced that reuse with dedicated first-pass programmatic art (`mods/sungrid/bits/gen_concept_art.py`) for all of them except Wind Turbine Array and Hydrogen Plant, which were instead drawn as palette/motif variants of Solar Array's own dedicated art (issue #12) since they're mechanically just other power buildings — see each building's entry below for specifics. `docs/concept-art/phase5-building-dossier.html` and `docs/concept-art/phase5-pixel-mockups.html` remain non-canonical discussion sketches, not what actually shipped.


<img width="1280" height="800" alt="desert_base2" src="https://github.com/user-attachments/assets/d8cfc5fa-e1b4-4606-9b41-13f814aba409" />

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
- **Prerequisites:** Materials Refinery (`proc`) — as implemented; the refinery itself requires a power source, so the "established power economy first" intent from the original sketch holds transitively rather than as an explicit Solar Array prerequisite.
- **Likely counters:** Direct assault/raiding once Reserve inside is worth stealing-by-destruction; artillery and air harassment are effective since Vaults have no inherent defensive synergy.
- **Implementation complexity:** High — this is the one building that needs new C# trait work (deposit tracking, capacity, destruction-drain, Lockdown countdown hook).
- **Staging:** Implemented (Phase 3) — **on the RA Ore Silo actor, `SILO`**, display-renamed "Battery Bank", rather than as a new actor: it carries the `GridReserveVault` trait alongside its stock 3000-credit `StoresPlayerResources` role (cost 150, 30000 HP, Wood armor, −10 power, Defense build queue). The vault's own numbers live as C# defaults in `OpenRA.Mods.Sungrid/GridReserve/GridReserveVault.cs`, not in YAML: **capacity 8000 Reserve, deposit rate 30/tick, and on destruction 50% of its share of the owner's Reserve drains, half of which (50%) is paid to the attacker.** Note `SILO` also retains RA's `InfiltrateForCash`: a Thief infiltration steals 50% of *stored spendable credits* — deposited Reserve is held player-side by `GridReserveManager`, so it is **not** stealable by Thief, only by destruction.

### 3. Recycling Depot
- **Category:** Economy
- **Fantasy:** A circular-economy facility that refines Scrap — reclaimed litter and industrial waste scattered across the map — back into usable Credits, delivered by a small dedicated Hauler Drone.
- **Gameplay purpose:** Refinery-adjacent economy building; gives a second, map-control-rewarding income stream alongside its unconditional baseline trickle, distinct from Ore/Gems field control.
- **Prerequisites:** Construction Yard, Solar Array.
- **Likely counters:** Denying the player map access to Scrap patches, harassing the fragile, unarmed Hauler Drone while it's out collecting, direct destruction like any economy building.
- **Implementation complexity:** Low, in practice — reuses the existing Ore/Gems `ResourceType`/`ResourceLayer`/`Harvester`/`Refinery`/`DockHost` machinery almost verbatim for a new `Scrap` resource, plus a dedicated `SGHAU` "Hauler Drone" unit (small `StoresResources` capacity, ground-mobile — `Harvester` requires the `Mobile` trait, so it can't be a flying unit like `SGDRO`/`SGDRS` without new C#). No new C#. Originally estimated Medium/assumed death-triggered wreck-salvage; revised to a map-placed-resource design once implemented.
- **Staging:** Implemented as `RCYD` (Refinery/DockHost/StoresPlayerResources, `FreeActor: SGHAU`) + `SGHAU`. The original Phase 2 `CashTrickler`-only baseline is retained unconditionally (existing shipped maps have no `Scrap` patches painted yet — see `docs/BACKLOG.md` issue #5 resolution for the map-content follow-up), with the Hauler Drone loop as an additive bonus stream on maps that have Scrap painted. **Art (issue #34):** `SGHAU` now has a dedicated sprite — a small hex-chassis cargo sled with a rear cargo canister whose fill level shows current Scrap load, replacing the reused `HARV` (Ore Truck) sprite it previously shared verbatim. That reuse was originally scoped as "easy to adapt, not a new concept" (same call as `DISR`/`ARCT`, which got the identical reversal in `docs/BACKLOG.md` issue #36), but it turned out to be a real gameplay-clarity bug, not just missing flavor: an identical-looking Hauler Drone reads as an idle/broken Ore Truck, since it never appears to collect Ore.

### 4. Cryptominer
- **Category:** Economy
- **Fantasy:** Repurposed compute infrastructure grinding through proof-of-work for a legacy financial network — a deliberately morally ambiguous building in an eco-solarpunk setting (cheap power in, real money out, but it's not "clean" the way Solar Array is).
- **Gameplay purpose:** A high power-draw, high-Credit-output economy building — trades grid stability (drains power hard) for economic upside, creating a real tension with the Solar Array/power budget.
- **Prerequisites:** Solar Array (needs power headroom to be worth building), Tech Center-equivalent.
- **Likely counters:** Power denial (destroy Solar Arrays and the Cryptominer goes offline or throttles), it's a high-value/low-defense target for raids given its output.
- **Implementation complexity:** Low, in practice — stock `GrantConditionOnPowerState` (per-player Normal/Low/Critical tiers) plus two `CashTrickler` instances gated on those conditions gives power-scaled income with no new C#. Originally estimated Medium (assumed a custom trait was needed); revised down once implemented.
- **Staging:** Implemented (Phase 5) as `SGCRY`. **Revised (energy rebalance pass, see `docs/ENERGY_BALANCE.md`):** power draw raised from -120 to -150 (one of the two heaviest single drains in the game, alongside the Datacenter for AI), and the Critical-power tier of its `GrantConditionOnPowerState@STRAINED` now includes `Critical` (previously `Low` only), so income degrades to the reduced rate instead of silently dropping to zero at Critical power. **Art (issue #34):** dedicated sprite -- worn/legacy server-rack blocks in desaturated gray with rust accents and blinking amber status lights, replacing the reused `atek` (Consortium Tech Center) sprite.

### 4a. Note on power-scaled buildings (Cryptominer, Grid Defense Turret)

Both buildings originally assumed they'd need a small custom trait for power-scaled behavior. Implementation found stock `GrantConditionOnPowerState` already covers this (grants a condition based on the owner's aggregate power state), so tiered `CashTrickler`/`FirepowerMultiplier`/`ReloadDelayMultiplier` instances gated on those conditions do the job in pure YAML. Updated `docs/ARCHITECTURE.md` isn't needed since its data-driven-first framing already anticipated this as the default expectation.

### 5. Datacenter for AI
- **Category:** Economy / Intelligence
- **Fantasy:** Racks of compute serving the faction's logistics AI and battlefield analytics — the "brains" behind smart-grid coordination.
- **Gameplay purpose:** Dual-purpose building — modest passive Credit/tech bonus plus an intelligence effect (e.g. periodic radar pulse or unit-vision bonus), tying economic investment to information advantage rather than pure output.
- **Prerequisites:** Tech Center-equivalent, Solar Array.
- **Likely counters:** High-value raid target once its intelligence bonus is felt on the battlefield; power denial reduces its effect the same way as Cryptominer.
- **Implementation complexity:** Low, in practice — composes stock `CashTrickler`, `RevealsShroud`, and `DetectCloaked` (confirmed as the safer, already-verified-in-repo choice over the support-power-style periodic pulse originally described).
- **Staging:** Implemented (Phase 5) as `SGDAI`. **Revised (issue #22):** the original implementation had the `sgdai` prerequisite id auto-provided but never consumed anywhere, so it didn't actually function as a tech gate despite the "brains behind smart-grid coordination" fantasy. It now genuinely gates content: `PDOX`/`IRON`/`MSLO` (the three superweapons) require `sgdai` in addition to their existing tech-center gates, and it's a required prerequisite (alongside `sgdrn`/`sgdra`) for both drone units — see buildings #6 and #11 below. **Revised again (energy rebalance pass, see `docs/ENERGY_BALANCE.md`):** power draw raised from -60 to -140 (matching `SGCRY`'s order of magnitude — this building was previously the weakest link in the power story despite gating both factions' drones). It now also carries the same `GrantConditionOnPowerState` NORMAL/STRAINED pattern as `SGCRY`/`SGTUR`: its `CashTrickler` degrades under strain (20→8/tick) and its `DetectCloaked` cuts out entirely below Normal power — the "AI" genuinely stops working, it doesn't just get cheaper to run. **Art (issue #34):** dedicated sprite -- a dense, neatly aligned blue-black server grid with gold trim and a thin green "data line" accent, deliberately the tidy/orderly foil to Cryptominer's worn look, replacing the reused `dome` (Radar Dome) sprite.

### 6. Drone Bay
- **Category:** Logistics
- **Fantasy:** Autonomous delivery drones ferrying resources and reinforcements across contested terrain, reducing dependence on vulnerable ground supply lines.
- **Gameplay purpose:** Logistics building enabling faster resource transport and/or rapid unit repositioning between owned structures — a mobility/economy hybrid that rewards map-spanning infrastructure over turtled play.
- **Prerequisites:** Construction Yard, Recycling Depot or equivalent economy building.
- **Likely counters:** Anti-air, since drone traffic is the obvious vulnerability; destroying the Drone Bay itself halts the logistics network.
- **Implementation complexity:** Low, in practice — scoped down deliberately per this doc's own friction-point flag. Rather than genuinely novel routing/logistics logic, implemented as a `ProximityExternalCondition` aura granting nearby friendly vehicles a `SpeedMultiplier` bonus ("drone-assisted logistics network"). No new unit, no new C#, no novel routing behavior.
- **Staging:** Implemented (Phase 5) as `SGDRN`. **Revised (issue #22):** the "no new unit" descope above meant the building had no actual drone identity — the speed aura is retained, but `SGDRN` now also has `Production`/`Exit`/`RallyPoint` (originally mirroring `WEAP`'s Vehicle-producer pattern) and builds a new unit, `SGDRO` ("Recon Drone") — a fast, unarmed, wide-vision scout. `SGDRO` requires both `sgdrn` and `sgdai`, so the AI Data Center is what unlocks it. **Revised again (issue #23):** a "drone" that drove on wheels didn't fit — `SGDRO` moved from `mods/sungrid/rules/vehicles.yaml` to `mods/sungrid/rules/aircraft.yaml` as an actual flying unit (`Inherits: ^Helicopter`, reusing `TRAN`'s Chinook sprite/rotor animation rather than `JEEP`'s), and `SGDRN` now mirrors `HPAD`'s aircraft-production block (`Produces: Aircraft, Helicopter`, `Reservable`, `ProductionBar`) instead of `WEAP`'s vehicle one. Still no new C#, no new art. **Revised again (issue #24):** `SGDRN` is now Assembly-exclusive (`~structures.soviet` added to its prerequisites, matching `AGUN`/`SAM`'s idiom), and `SGDRO` is a cheap (350), fragile (`HP: 3000`), lightly-armed (`DroneRocket`, 2×700 damage) harasser rather than an unarmed scout. The Consortium gets its own counterpart, `SGDRS` ("Strike Drone") — pricier (600), slightly harder-hitting (`DroneRocket.Strike`, 2×950 damage), similarly fragile (`HP: 3500`), gated on the same `sgdai` AI Data Center prerequisite. Both stay `Light`-armored, so the existing neutral `E3` Rocket Soldier (100% damage versus Light) remains a strong counter to either side's drone — no new dedicated counter unit was added. **Revised again (energy rebalance pass, see `docs/ENERGY_BALANCE.md`):** `SGDRS` no longer builds from `HPAD` — the Consortium now has its own dedicated mirror building, `SGDRA` ("Aerial Fabrication Bay", building #11 below), for true Drone Bay parity between factions. Both `SGDRO` and `SGDRS` now also carry `GrantConditionOnPowerState` gating their own `Armament` (`RequiresCondition: drone-uplink || drone-uplink-degraded`) — drones fleet-wide lose their weapons outright once their owner's grid drops to Critical power, regardless of proximity to any building. **Art (issue #34):** `SGDRN` now has a dedicated sprite -- an asymmetric, improvised open scaffold/gantry with a small parked drone, replacing the reused `hpad` (Helipad) sprite. `SGDRO`/`SGDRS` also got dedicated 32-facing rotating drone-body sprites (green quadcopter silhouette for `SGDRO`, larger blue-black-and-gold body with visible weapon-pod accents for `SGDRS`), replacing their reused `TRAN`/`MH60` manned-helicopter bodies -- the "no new art" note above is superseded.

**Note on `SGHAU` (Hauler Drone):** this building's own "autonomous delivery drones ferrying resources" fantasy line item above is still descoped — the `ProximityExternalCondition` speed aura is the entire implementation, no literal transport. The Recycling Depot's `SGHAU` unit (see building #3) is unrelated: it's a ground-mobile Scrap collector gated on `RCYD`, not on `SGDRN`/`SGDRA`, and doesn't interact with this building's tech tree despite both sharing "drone" in the name.

### 7. Grid Defense Turret
- **Category:** Defense
- **Fantasy:** A point-defense structure drawing directly off the local grid — hits harder when the grid is healthy, weaker when power is strained.
- **Gameplay purpose:** Standard defensive structure, but with its damage/rate-of-fire tied to the base's current power surplus — creates a direct tactical link between the energy economy and combat strength.
- **Prerequisites:** Solar Array.
- **Likely counters:** Power denial (destroy power plants to weaken the turret before assaulting), standard artillery/air counters to static defense.
- **Implementation complexity:** Low, in practice — see the Cryptominer note above; `GrantConditionOnPowerState` gating `FirepowerMultiplier`/`ReloadDelayMultiplier` covers it with no new trait. Deliberately does **not** inherit `DisableOnLowPowerOrPowerDown` — the design calls for "weaker when strained," not "offline," so it stays combat-capable at low power rather than being paused like most power-consuming defenses.
- **Staging:** Implemented (Phase 5) as `SGTUR`. **Revised (roster survey gap G5):** originally fired the same `TurretGun` weapon as the Consortium-only `GUN`, making `GUN` close to dead content — now fires its own weapon, `GridPulseCannon` (identical damage/reload/range, so the cost/prereq tradeoff is unchanged), reflavored as an energy weapon that's strong vs Light armor and weak vs Heavy, the inverse of `TurretGun`'s profile. `SGTUR` is the shared, power-scaled anti-harassment turret; `GUN` keeps its niche as the Consortium's harder-hitting anti-armor gun. **Art (issue #34):** dedicated sprite -- a genuinely rotating 32-facing turret (green barrel, gold-rimmed blue-black base), replacing the reused `SAM` Site sprite it previously shared with both the real `SAM` and `SGWND` (a three-way silhouette collision, not just missing flavor).

### 8. Smart Grid Relay
- **Category:** Energy / Logistics
- **Fantasy:** A grid-balancing relay station that lets power flow between distant parts of a sprawling, decentralized base.
- **Gameplay purpose:** Extends effective power range/pooling between disconnected base clusters, enabling more spread-out, harder-to-snipe-in-one-strike base layouts.
- **Prerequisites:** Solar Array.
- **Likely counters:** Destroying the Relay can fragment a spread base's power pool, so it becomes a high-value target in decentralized layouts.
- **Implementation complexity:** Low, but scoped down from the original fantasy. OpenRA's stock power system already pools per-player globally (not range-limited), so there's no missing mechanic to extend — building genuine range-limited pooling would mean replacing a core engine system, which is exactly the kind of wide-blast-radius engine change `docs/ARCHITECTURE.md` says to avoid. Implemented instead as a modest flat secondary power source (same `Power` trait as Solar Array; smaller 1×1 footprint and Heavy armor, at a per-power premium — cost retuned 600 → 400 after the roster survey's gap G4), framed narratively as grid-balancing infrastructure. The literal "extends pooling range between disconnected clusters" idea stays deferred until base-spread playstyles are actually observed in a playtest and justify the bigger engine investment.
- **Staging:** Implemented (Phase 5, scoped-down version) as `SGREL`. Pulled forward from this doc's earlier "post-Phase 5" note to match `docs/ROADMAP.md`'s Phase 5 deliverable list, which named all 7 remaining buildings — this doc's per-building staging notes hadn't been updated to match when that roadmap entry was written. **Art (issue #34):** dedicated sprite -- a small gold-lit relay pylon with radiating power lines, replacing the reused `GAP` (Gap Generator) sprite.

### 9. Resilience Shelter
- **Category:** Defense
- **Fantasy:** A hardened civil-defense structure that keeps a settlement's core functions running under sustained attack — the "don't lose everything at once" building.
- **Gameplay purpose:** Damage-mitigation/comeback structure — e.g. reduces splash damage to nearby structures or grants a brief repair pulse when the base takes heavy losses, softening total wipeouts without preventing them.
- **Prerequisites:** Construction Yard, Tech Center-equivalent.
- **Likely counters:** Alpha-strike/overwhelm tactics that outpace its mitigation window; it blunts damage, it doesn't prevent loss.
- **Implementation complexity:** Low, in practice — stock `ProximityExternalCondition` (grants a condition to nearby friendly actors) plus `DamageMultiplier` (gated on that condition, added to the shared `^Building` fragment so any structure can benefit) covers the damage-mitigation aura with no new trait. The "brief repair pulse on heavy losses" alternative from the original fantasy wasn't implemented — the aura alone satisfies the design intent.
- **Staging:** Implemented (Phase 5) as `SGSHL`. Pulled forward from "post-Phase 5" for the same reason as Smart Grid Relay above. **Art (issue #34):** dedicated sprite -- a hardened green dome with a sandbag row along the front edge (per `docs/ART_DIRECTION.md`'s "not utopian" guardrail), replacing the reused `IRON` (Iron Curtain) sprite.

### 10. Sensor Array
- **Category:** Intelligence
- **Fantasy:** A distributed sensor mesh reading grid load, drone traffic, and terrain across the map — battlefield awareness as smart-grid telemetry.
- **Gameplay purpose:** Wide-radius vision/detection building (including stealth/cloak detection if the roster ever needs it), rewarding investment in map awareness over blind aggression.
- **Prerequisites:** Tech Center-equivalent.
- **Likely counters:** High-value raid/airstrike target once its intelligence value is evident; doesn't defend itself.
- **Implementation complexity:** Low — composes stock `RevealsShroud`, `DetectCloaked`, and `RenderDetectionCircle`, as expected.
- **Staging:** Implemented (Phase 5) as `SGSNS`. Pulled forward from "post-Phase 5" for the same reason as Smart Grid Relay above. **Art (issue #34):** dedicated sprite -- a tripod-mounted radar dish with a concentric-ring motif, replacing the reused `KENN` (Kennel) sprite.

### 11. Wind Turbine Array (Assembly)
- **Category:** Energy
- **Fantasy:** Cheap, mass-producible turbines suited to the Assembly's decentralized, improvisational infrastructure philosophy (`docs/ART_DIRECTION.md`).
- **Gameplay purpose:** An early, cheap, individually fragile alternative/supplement to Solar Array — rewards spreading power generation out across a base rather than concentrating it, so raiding and map pressure stay relevant on the power layer.
- **Prerequisites:** Any existing power source, `~techlevel.low` (a tier earlier than Advanced Solar Array).
- **Likely counters:** Individually low HP (30000, the lowest of any power building) makes each turbine an easy kill; the tradeoff is there are cheaply many of them.
- **Implementation complexity:** Low — same `Power`/`ScalePowerWithHealth` composition as Solar Array, just retuned numbers and an earlier/faction-gated prerequisite. No new traits.
- **Staging:** Implemented as `SGWND`, part of the energy rebalance pass — see `docs/ENERGY_BALANCE.md`. **Art (issue #34):** treated as an "easy adapt" of Solar Array's own dedicated art rather than a wholly new motif -- two sparse turbine-and-rotor poles on the same ground-strip/gold-conduit visual language `sgpwr.png` established, replacing the reused `SAM` Site sprite it previously shared with both the real `SAM` and `SGTUR`.

### 12. Hydrogen Plant (Consortium)
- **Category:** Energy
- **Fantasy:** A hardened, centralized power-generation facility matching the Consortium's capital-technocratic infrastructure philosophy.
- **Gameplay purpose:** An expensive, late-game power consolidation building — the highest single power output in the game, at the cost of being one large, very high-value raid target instead of many small ones.
- **Prerequisites:** Radar Dome, Consortium Tech Center, `~techlevel.high`.
- **Likely counters:** Its concentration of power output into one hardened building is itself the weakness — losing it is a much bigger swing than losing any one Solar Array.
- **Implementation complexity:** Low — same composition as Solar Array/Wind Turbine Array, just retuned numbers, higher armor, and a late tech gate. No new traits.
- **Staging:** Implemented as `SGHYD`, part of the energy rebalance pass — see `docs/ENERGY_BALANCE.md`. **Art (issue #34):** also an "easy adapt" of Solar Array's visual language rather than a new motif -- two large gold-banded tanks in place of solar panels, bigger/heavier to match the 3x3 footprint and Heavy armor, replacing the reused `PROC` (Materials Refinery) sprite.

### 13. Aerial Fabrication Bay (Consortium)
- **Category:** Logistics
- **Fantasy:** The Consortium's dedicated counterpart to the Assembly's Drone Bay.
- **Gameplay purpose:** Gives the Consortium a proper, symmetric drone-production structure instead of bolting Strike Drone production onto the Helipad — closes a faction-parity gap.
- **Prerequisites:** Materials Refinery, Recycling Depot, `~structures.allies`, `~techlevel.medium` — an exact mirror of Drone Bay's Assembly prerequisites.
- **Likely counters:** Same as Drone Bay — anti-air against drone traffic, direct destruction of the building halts Strike Drone production.
- **Implementation complexity:** Low — a direct mechanical mirror of `SGDRN` (same `ProximityExternalCondition` speed aura, `Production`/`Exit`/`RallyPoint`), just faction-flipped prerequisites and a different placeholder sprite.
- **Staging:** Implemented as `SGDRA`, part of the energy rebalance pass — see `docs/ENERGY_BALANCE.md`. **Art (issue #34):** dedicated sprite -- an enclosed, symmetric hangar box with gold trim (the hardened Consortium mirror of `SGDRN`'s open scaffold), replacing the reused `AFLD` (Airfield) sprite.

## Roster stat survey — all buildings and units (July 2026)

Values below are read straight out of `mods/sungrid/rules/*.yaml` with `Inherits` chains resolved (so inherited HP/armor/etc. are included). Numbers are engine-internal units: HP is 100× the displayed value, Speed is the `Mobile`/`Aircraft` speed integer, Vision is `RevealsShroud.Range` in cells. Power: positive = generates, negative = drains. Faction names: Consortium = `allies`-gated, Assembly = `soviet`-gated. Tech = the `~techlevel.*` lobby gate (`inf` = available even at infantry-only, `unr` = unrestricted-only). Prereqs omit the techlevel gate.

### Buildings — production, economy, tech (Building queue)

| ID | Name | Faction | Tech | Cost | HP | Armor | Power | Prereqs | Notes |
|---|---|---|---|---|---|---|---|---|---|
| FACT | Construction Yard | Both | — | 2000 | 150000 | Wood | 0 | (MCV deploy only) | |
| POWR | Solar Array | Both | inf | 300 | 40000 | Wood | +100 | — | Best cr/power ratio in game (3.0) |
| APWR | Advanced Solar Array | Both | med | 1000 | 70000 | Wood | +200 | dome | 5.0 cr/power |
| SGWND | Wind Turbine Array | Assembly | low | 250 | 30000 | Wood | +70 | anypower | 3.6 cr/power; cheapest power building in the game (was 400 — see gap G3, since retuned) |
| SGHYD | Hydrogen Plant | Consortium | high | 1200 | 90000 | Heavy | +350 | dome, atek | 3.4 cr/power; only Heavy-armored power source |
| SGREL | Smart Grid Relay | Both | med | 400 | 50000 | Heavy | +60 | anypower | 6.7 cr/power; 1×1 footprint, Heavy, vision 7 (was 600 — see gap G4, since retuned) |
| PROC | Materials Refinery | Both | inf | 1400 | 90000 | Wood | −30 | anypower | Comes with free HARV |
| RCYD | Recycling Depot | Both | inf | 600 | 40000 | Wood | −20 | anypower | Free SGHAU; baseline trickle 25 cr/125 ticks |
| BARR | Assembly Barracks | Assembly | inf | 500 | 60000 | Wood | −20 | anypower | |
| TENT | Consortium Barracks | Consortium | inf | 500 | 60000 | Wood | −20 | anypower | |
| KENN | Kennel | Assembly | inf | 200 | 30000 | Wood | −10 | anypower | |
| WEAP | War Factory | Both | low | 2000 | 150000 | Wood | −30 | proc | |
| DOME | Radar Dome | Both | med | 1500 | 100000 | Wood | −40 | proc | Vision 10 |
| HPAD | Helipad | Consortium | med | 500 | 80000 | Wood | −10 | dome | |
| AFLD | Airfield | Assembly | med | 500 | 100000 | Wood | −20 | dome | Iran variant available to all |
| SPEN | Sub Pen | Assembly | low | 800 | 100000 | Wood | −20 | anypower | |
| SYRD | Naval Yard | Consortium | low | 1000 | 100000 | Wood | −20 | anypower | |
| FIX | Service Depot | Both | med | 1200 | 80000 | Wood | −30 | weap | |
| ATEK | Consortium Tech Center | Consortium | high | 1500 | 60000 | Wood | −200 | weap, dome | |
| STEK | Assembly Tech Center | Assembly | high | 1500 | 80000 | Wood | −100 | weap, dome | Note asymmetry vs ATEK: +20000 HP, half the power drain |
| SGCRY | Cryptominer | Both | high | 1800 | 80000 | Wood | −150 | dome | Income 45 cr/50 ticks Normal, 15 Strained — see gap G8 |
| SGDAI | Datacenter for AI | Both | high | 1600 | 80000 | Wood | −140 | dome | 20 cr/100 ticks Normal, 8 Strained; DetectCloaked off below Normal; gates superweapons + drones |
| SGDRN | Drone Bay | Assembly | med | 900 | 70000 | Wood | −20 | proc, rcyd | Vehicle speed aura + builds SGDRO |
| SGDRA | Aerial Fabrication Bay | Consortium | med | 900 | 70000 | Wood | −20 | proc, rcyd | Exact SGDRN mirror; builds SGDRS |
| SGSHL | Resilience Shelter | Both | high | 1200 | 90000 | Wood | −50 | fact, dome | Damage-mitigation aura to nearby structures |
| SGSNS | Sensor Array | Both | high | 800 | 40000 | Wood | −30 | dome | Vision 10 + DetectCloaked |

### Buildings — defense, storage, walls, superweapons (Defense queue)

| ID | Name | Faction | Tech | Cost | HP | Armor | Power | Weapon | Prereqs | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| SILO | Battery Bank | Both | inf | 150 | 30000 | Wood | −10 | — | proc | **The Grid Reserve Vault** (`GridReserveVault`: capacity 8000, deposit 30/tick, 50% drain / 50% attacker reward on destruction) — see gap G2 |
| PBOX | Pillbox | Consortium | low | 600 | 40000 | Heavy | −20 | (garrisoned E1, included) | tent | |
| HBOX | Camo Pillbox | Consortium | med | 750 | 40000 | Heavy | −20 | (garrisoned E1, cloaked) | tent | |
| GUN | Turret | Consortium | med | 800 | 40000 | Heavy | −40 | TurretGun | tent | Higher flat damage, better vs Heavy — see gap G5, since fixed |
| ARCT | Arc Turret | Assembly | low | 600 | 40000 | Heavy | −20 | ArcDischarge | barr | Also prereq for DISR |
| TSLA | Tesla Coil | Assembly | med | 1200 | 40000 | Heavy | −80 | TeslaZap | weap | |
| SGTUR | Grid Defense Turret | Both | med | 900 | 40000 | Heavy | −40 | GridPulseCannon | anypower | 125% firepower at Normal power; 70% + 130% reload when strained; own weapon now — strong vs Light, weak vs Heavy (was TurretGun, identical to GUN — see gap G5, since fixed) |
| AGUN | AA Gun | Consortium | med | 800 | 40000 | Heavy | −50 | ZSU-23 | dome | |
| SAM | SAM Site | Assembly | med | 700 | 40000 | Heavy | −40 | Nike | dome | |
| GAP | Gap Generator | Consortium | high | 800 | 50000 | Heavy | −60 | — | atek | |
| SBAG | Sandbag Wall | Consortium | low | 30 | 15000 | Wood | — | — | fact | |
| FENC | Wire Fence | Assembly | low | 30 | 15000 | Wood | — | — | fact | |
| BRIK | Concrete Wall | Both | med | 200 | 40000 | Concrete | — | — | fact | |
| MSLO | Missile Silo | Both | unr | 2500 | 100000 | Wood | −150 | — | techcenter, sgdai | sgdai gate confirmed in YAML (issue #22) |
| IRON | Iron Curtain | Assembly | unr | 2000 | 100000 | Wood | −200 | — | stek, sgdai | sgdai gate confirmed |
| PDOX | Chronosphere | Consortium | unr | 1500 | 100000 | Wood | −200 | — | atek, sgdai | sgdai gate confirmed |

### Infantry

| ID | Name | Faction | Tech | Cost | HP | Speed | Weapon(s) | Prereqs | Notes |
|---|---|---|---|---|---|---|---|---|---|
| E1 | Rifle Infantry | Both | inf | 100 | 5000 | 54 | M1Carbine | barracks | |
| E2 | Grenadier | Assembly | inf | 150 | 5000 | 68 | Grenade | barr | |
| E3 | Rocket Soldier | Both | inf | 300 | 4500 | 54 | Dragon, RedEye | barracks | Designated anti-drone counter (100% vs Light) |
| DISR | Disruptor Trooper | Assembly | low | 300 | 4000 | 54 | Disruptor | barr, arct | No Consortium counterpart — see gap G10 |
| DOG | Attack Dog | Assembly | inf | 200 | 1800 | 100 | DogJaw | kenn | |
| E6 | Engineer | Both | inf | 400 | 2500 | 54 | — | barracks | |
| MEDI | Medic | Consortium | inf | 200 | 6000 | 49 | Heal | tent | |
| MECH | Mechanic | Consortium | med | 500 | 8000 | 49 | Repair | tent, fix | |
| SPY | Spy | Consortium | med | 500 | 2500 | 54 | SilencedPPK | tent, dome | The Greek variant costs 250 |
| THF | Thief | Assembly | med | 500 | 8000 | 72 | — | barr, dome | Steals 50% of stored credits — incl. from SILO, see gap G2 |
| SHOK | Shock Trooper | Assembly (China) | high | 350 | 5000 | 54 | PortaTesla | barr, stek, tsla | |
| E7 | Tanya | Consortium | high | 1800 | 10000 | 68 | Colt45 | tent, atek | |

### Vehicles

| ID | Name | Faction | Tech | Cost | HP | Armor | Speed | Weapon(s) | Prereqs | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| HARV | Ore Truck | Both | inf | 1100 | 60000 | Heavy | 72 | — | proc | |
| SGHAU | Hauler Drone | Both | inf | 500 | 22000 | Light | 72 | — | rcyd | Speed was unset (=1, effectively immobile) when first surveyed — see gap G1, since fixed |
| MCV | Mobile Construction Vehicle | Both | med | 2000 | 60000 | Light | 60 | — | fix | |
| TRUK | Supply Truck | Both | low | 500 | 11000 | Light | 113 | — | — | |
| JEEP | Ranger | Consortium | low | 500 | 15000 | Light | 164 | M60mg | — | |
| APC | Armored Personnel Carrier | Assembly | low | 850 | 35000 | Heavy | 128 | M60mg | — | |
| FTRK | Mobile Flak | Assembly | low | 600 | 15000 | Light | 113 | FLAK-23 AA/AG | — | |
| 1TNK | Light Tank | Consortium | low | 700 | 23000 | Heavy | 113 | 25mm | — | |
| 2TNK | Medium Tank | Consortium | med | 850 | 46000 | Heavy | 72 | 90mm | fix | |
| 3TNK | Heavy Tank | Assembly | med | 1150 | 60000 | Heavy | 64 | 105mm | fix | |
| 4TNK | Mammoth Tank | Assembly | high | 2000 | 90000 | Heavy | 43 | 120mm, MammothTusk | fix, stek | |
| ARTY | Artillery | Consortium | med | 850 | 10000 | Light | 72 | 155mm | dome | |
| V2RL | Surge Rocket Launcher | Assembly | med | 900 | 20000 | Light | 72 | SCUD | dome | |
| MNLY | Minelayer | Both | med | 800 | 30000 | Heavy | 113 | — | fix | |
| MGG | Mobile Gap Generator | Consortium (Greece) | high | 1000 | 22000 | Heavy | 72 | — | atek | |
| MRJ | Mobile Radar Jammer | Consortium | high | 1000 | 22000 | Heavy | 68 | — | atek | |
| TTNK | Tesla Tank | Assembly (China) | high | 1350 | 40000 | Light | 92 | TTankZap | tsla, stek | |
| CTNK | Chrono Tank | Consortium (The Epoch) | high | 1350 | 40000 | Light | 86 | APTusk | atek | |
| STNK | Phase Transport | Consortium (USA) | high | 1000 | 35000 | Light | 128 | APTusk.stnk | atek | |
| QTNK | Tremor Tank | Assembly | high | 2000 | 90000 | Heavy | 46 | (quake) | fix, stek | |
| DTRK | Demolition Truck | Assembly (Iran) | high | 2500 | 2800 | Light | 67 | DemoTruck | stek | |

### Aircraft

| ID | Name | Faction | Tech | Cost | HP | Speed | Weapon(s) | Prereqs | Notes |
|---|---|---|---|---|---|---|---|---|---|
| YAK | Yak Attack Plane | Assembly | med | 1350 | 6000 | 178 | ChainGun.Yak | afld | |
| MIG | MiG Attack Plane | Assembly | high | 2000 | 8000 | 223 | Maverick | afld, stek | |
| TRAN | Chinook | Consortium | med | 900 | 14000 | 128 | — | hpad | |
| MH60 | Black Hawk | Consortium | med | 1500 | 10000 | 112 | ChainGun | hpad | |
| HELI | Longbow | Consortium | high | 2000 | 12000 | 149 | Hellfire AA/AG | hpad, atek | |
| HIND | Wasp Gunship | Assembly | med | 1500 | 10000 | 112 | ChainGun | afld | Rebranded as the Assembly's rotary counterpart to Consortium's HPAD helicopters (was disabled dead content — see gap G6, since fixed) |
| SGDRO | Recon Drone | Assembly | high | 350 | 3000 | 170 | DroneRocket (2×700) | sgdrn, sgdai | Weapon disabled at Critical power |
| SGDRS | Strike Drone | Consortium | high | 600 | 3500 | 150 | DroneRocket.Strike (2×950) | sgdra, sgdai | Weapon disabled at Critical power — see gap G7 (tracked, issue #31) |

### Ships

| ID | Name | Faction | Tech | Cost | HP | Armor | Speed | Weapon(s) | Prereqs | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| SS | Submarine | Assembly | low | 950 | 25000 | Light | 78 | TorpTube | spen | Stock RA identity — see gap G9 |
| MSUB | Missile Submarine | Assembly | high | 2000 | 40000 | Light | 44 | SubMissile (+AA) | spen, stek | |
| PT | Gunboat | Consortium | low | 500 | 20000 | Heavy | 142 | 2Inch, DepthCharge | syrd | |
| DD | Destroyer | Consortium | med | 1000 | 40000 | Heavy | 92 | Stinger (+AA), DepthCharge | syrd, dome | |
| CA | Cruiser | Consortium | high | 2400 | 80000 | Heavy | 44 | 8Inch | syrd, atek | |
| LST | Transport | Both | low | 500 | 40000 | Heavy | 115 | — | — | |

Campaign-only / non-skirmish actors, listed for completeness: `Zombie` (Blighted), `Ant` (Swarmling) — `~bio`-gated; `FireAnt`/`ScoutAnt`/`WarriorAnt` (Cinderling/Scoutling/Bulwarkling) — `~disabled`; `AFLD.Ukraine`, `SPY.England` — subfaction variants of actors above.

### Gaps found

- **G1 — `SGHAU` had no `Mobile.Speed` (bug, since fixed).** It inherits `^Vehicle`, whose `Mobile` sets only `Locomotor`/`TurnSpeed`, and never set `Speed` itself. The engine default (`MobileInfo.Speed`, verified in the pinned `ENGINE_VERSION` commit) is **1** — the Hauler Drone moved at 1/72nd of an Ore Truck's speed, i.e. was effectively immobile. Undetected because no shipped map has Scrap painted (see building #3), so the free Hauler never had anywhere to drive. **Fixed: `Mobile: Speed: 72` (matching HARV) in the follow-up to the survey PR.**
- **G2 — Battery Bank doc/rules drift (since fixed).** The Grid Reserve Vault is implemented on `SILO` (display name already "Battery Bank"), but entry #2 above originally never said so, and its listed prerequisites ("Solar Array, Refinery-equivalent") didn't match the YAML (`proc` only, cost 150). The vault's actual numbers live in C# defaults, invisible to YAML readers: capacity 8000, deposit 30/tick, 50% reserve drain + 50% attacker reward on destruction (`OpenRA.Mods.Sungrid/GridReserve/GridReserveVault.cs`). `SILO` also retains RA's `InfiltrateForCash` (Thief steals 50% of **stored spendable** credits) — deposited Reserve is held by `GridReserveManager` so it isn't stealable. **Fixed: entry #2's prerequisites and staging notes now record all of this.**
- **G3 — Wind Turbine Array was strictly dominated by Solar Array (since retuned).** Same 2×3 footprint, but SGWND cost more (400 vs 300), generates less (+70 vs +100), has less HP (30000 vs 40000), is faction-gated, and needs an existing power source — no situation where building one was correct. **Fixed: cost dropped 400 → 250**, making it the cheapest power building in the game (3.6 cr/power vs POWR's 3.0) — it now wins on absolute price and increment size, matching its "cheaply many of them" identity, while POWR keeps the better ratio and HP.
- **G4 — Smart Grid Relay was the worst power-per-credit in the game (since retuned)** (10.0 cr/power vs POWR's 3.0). Its real differentiators — 1×1 footprint, Heavy armor, vision 7 — didn't carry a 2× premium per power point. **Fixed: cost dropped 600 → 400** (6.7 cr/power): still a premium over POWR, but one plausibly worth paying for the smallest-footprint, hardest-to-kill power increment.
- **G5 — `SGTUR` and `GUN` share the same `TurretGun` weapon (since fixed).** SGTUR cost 100 more but was available to both factions, needed only `anypower` (no barracks), and fired at 125% under Normal power — for the Consortium, GUN was close to dead content. **Fixed: `SGTUR` now fires a new weapon, `GridPulseCannon` (`mods/sungrid/weapons/ballistics.yaml`) — same damage/reload/range as `TurretGun` so its cost/prereq tradeoff is unchanged, but reflavored as an energy weapon (`ElectricityDeath`) with a flipped armor profile: 100% vs Light (drones, scouts, light vehicles) but only 55% vs Heavy, versus `TurretGun`'s 75%/100%. SGTUR is now the power-scaled anti-harassment specialist available to both factions; GUN stays the Consortium's harder-hitting anti-armor gun.**
- **G6 — `HIND` was `~disabled` dead content (since fixed)**, and with `MH60`/`TRAN`/`HELI` all on the Consortium's Helipad, the Assembly had no helicopter at all (fixed-wing only). **Fixed: `HIND` is enabled and re-gated to the Assembly's own `AFLD`** (`Prerequisites: ~afld, ~techlevel.medium`, dropping `~disabled` and the Consortium-side `~hpad` gate) — `AFLD`'s `Production.Produces` gained `Helicopter` alongside its existing `Aircraft, Plane` to allow it. Also renamed via fluent (`actor-hind`) from "Hind" — a real-world Mi-24 NATO reporting name, the same category of Cold War designation already retired for `V2RL`/`QTNK`/`U2` — to **"Wasp Gunship"**, matching the Assembly's decentralized/drone-based identity (`docs/ART_DIRECTION.md`). No mechanical changes beyond the prereq/production gating; stats and weapon (`ChainGun`) untouched.
- **G7 — Drone cost/performance skew (tracked, not fixed).** Strike Drone pays +71% cost over Recon Drone (600 vs 350) for +17% HP, +36% damage, and −12% speed. Reasonable as faction flavor, but the Assembly likely gets more per credit. No rules change here — a numeric retune without match data would just be a different guess. **Tracked as `docs/BACKLOG.md` issue #31**, to be resolved from real 3+ player Grid Reserve/skirmish playtest data (`docs/PLAYTESTING.md`) rather than blind.
- **G8 — Cryptominer payback is short and raid-proof (tracked, not fixed).** 45 cr/50 ticks ≈ 1,350 cr/min at normal speed: the 1800 build cost (plus ~600 of power infrastructure for its −150 drain) pays back in roughly 2 minutes, after which it's income that — unlike a Harvester — never leaves the base. Same reasoning as G7: needs opportunity-cost data (vs a second Harvester + refinery) before touching numbers. **Tracked as `docs/BACKLOG.md` issue #31.**
- **G9 — No Sungrid identity pass on naval or several stock names.** Ships plus Chinook/MiG/Yak/Black Hawk/Tesla-branded content are untouched stock RA tone (cf. the Phase 6/7 identity work in `docs/ROADMAP.md`).
- **G10 — Disruptor Trooper has no Consortium counterpart** — all Consortium-unique infantry are stock RA (Medic/Mechanic/Spy/Tanya). Minor, and consistent with RA's own asymmetry, but worth a line in the faction-identity pass.

### Suggestions

1. ~~**Fix G1 now** — one line: `Mobile: Speed: 72` on `SGHAU`~~ **Done** (matching HARV). The Scrap-map follow-up from `docs/BACKLOG.md` issue #5 is still open, and is what would actually exercise the Hauler in a real game.
2. ~~**Close the G2 doc gap** — update entry #2 above to name `SILO` as the implementation, state the C# defaults, and note the Thief/Reserve interaction explicitly.~~ **Done.**
3. ~~**G3:** either drop SGWND to ~250 cr, raise it to +90–100 power, or shrink its footprint below POWR's — it needs at least one column it wins.~~ **Done** — cost dropped to 250.
4. ~~**G4:** price SGREL at ~350–400, or keep 600 and give it a small utility effect.~~ **Done** — cost dropped to 400; the utility-aura idea stays available if playtests want more.
5. ~~**G5:** give SGTUR a distinct energy-flavored weapon (the power-scaling identity invites it) or move GUN's niche elsewhere; alternatively raise SGTUR's prereq above bare `anypower`.~~ **Done** — new `GridPulseCannon` weapon, strong vs Light/weak vs Heavy.
6. ~~**G6:** delete the HIND block or rebrand it as an Assembly drone-carrier/gunship if the Assembly should get rotary air.~~ **Done** — rebranded and enabled as the Assembly's `AFLD`-built "Wasp Gunship."
7. **G7/G8:** no rules change yet — flagged for the next playtest (`docs/PLAYTESTING.md`) via `docs/BACKLOG.md` issue #31: drone cost-efficiency by faction, and Cryptominer opportunity-cost vs a second Harvester + refinery.
8. **G9/G10:** fold into the existing Phase 6/7 visual/audio identity scope rather than one-off renames now.
