## player.yaml
options-tech-level =
    .infantry-only = Infantry Only
    .low = Low
    .medium = Medium
    .no-superweapons = No Superweapons
    .unrestricted = Unrestricted

checkbox-kill-bounties =
    .label = Kill Bounties
    .description = Players receive cash bonuses for killing enemy units

checkbox-redeployable-mcvs =
    .label = Redeployable MCVs
    .description = Allows Construction Yards to be undeployed

checkbox-reusable-engineers =
    .label = Reusable Engineers
    .description = Engineers stay on the battlefield after capturing a structure

checkbox-gridreserve =
    .label = Grid Reserve
    .description = Adds an economic victory: bank Credits into Vaults and hold
    Grid Lockdown once the Reserve target is reached to win

notification-insufficient-funds = Insufficient funds.
notification-new-construction-options = New construction options.
notification-cannot-deploy-here = Cannot deploy here.
notification-low-power = Low power.
notification-base-under-attack = Base under attack.
notification-grid-lockdown-started = { $player } has reached their Grid Reserve target - Grid Lockdown initiated.
notification-grid-lockdown-cancelled = { $player }'s Grid Lockdown was cancelled.
notification-ally-under-attack = Our ally is under attack.
notification-silos-needed = Battery banks needed.

## world.yaml
notification-game-saved = Game saved.

options-starting-units =
    .mcv-only = MCV Only
    .light-support = Light Support
    .heavy-support = Heavy Support

resource-minerals = Valuable Minerals
resource-scrap = Reclaimed Scrap

map-generator-classic = Map Generator
map-generator-clear = Clear Terrain

## Faction
faction-allies =
    .name = The Consortium

faction-england =
    .name = Greece
    .description = Greece: Counterintelligence
     Special Unit: Auditor
     Special Unit: Mobile Gap Generator

faction-france =
    .name = USA
    .description = USA: Deception
     Special Ability: Can build fake structures
     Special Unit: Phase Transport

faction-germany =
    .name = Germany
    .description = Germany: Chronoshift Technology
     Special Ability: Advanced Chronoshift
     Special Unit: Chrono Tank

faction-soviet =
    .name = The Assembly

faction-russia =
    .name = China
    .description = China: Tesla Weapons
     Special Unit: Tesla Tank
     Special Unit: Shock Trooper

faction-ukraine =
    .name = Iran
    .description = Iran: Demolitions
     Special Ability: Parabombs
     Special Unit: Demolition Truck

faction-random =
    .name = Any
    .description = Random Country
     A random country is chosen when the game starts

faction-randomallies =
    .name = The Consortium
    .description = Random Consortium Country
     A random Consortium country is chosen when the game starts

faction-randomsoviet =
    .name = The Assembly
    .description = Random Assembly Country
     A random Assembly country is chosen when the game starts

## aircraft.yaml
actor-badr-name = Badger

actor-mig =
    .name = MiG Attack Plane
    .description =
    Fast Ground-Attack Plane.
      Strong vs Buildings and Vehicles
      Weak vs Infantry and Aircraft

actor-yak =
    .name = Yak Attack Plane
    .description =
    Attack Plane with dual machine guns.
      Strong vs Infantry and Light armor
      Weak vs Tanks and Aircraft

actor-tran =
    .name = Chinook
    .description =
    Fast infantry transport helicopter.
      Unarmed

actor-heli =
    .name = Longbow
    .description =
    Helicopter gunship with multi-purpose missiles.
      Strong vs Buildings, Vehicles and Aircraft
      Weak vs Infantry

actor-hind =
    .name = Wasp Gunship
    .description =
    Assembly rotary gunship with dual chain guns.
      Strong vs Infantry and Light armor
      Weak vs Tanks and Aircraft

actor-u2-name = Recon Plane

actor-mh60 =
    .name = Black Hawk
    .description =
    Helicopter gunship with dual chain guns.
      Strong vs Infantry and Light armor
      Weak vs Tanks and Aircraft

## civilian.yaml
actor-c10-name = Scientist
actor-tecn-name = Technician
actor-tecn2-name = Technician
actor-v01-name = Church
actor-v19-name = Oil Pump
actor-v19-husk-name = Husk (Oil Pump)
actor-barl-name = Explosive Barrel
actor-brl3-name = Explosive Barrel
actor-v25-name = Church
actor-lhus-name = Lighthouse
actor-windmill-name = Windmill

## decoration.yaml
actor-ice01-name = Ice Floe
actor-ice02-name = Ice Floe
actor-ice03-name = Ice Floe
actor-ice04-name = Ice Floe
actor-ice05-name = Ice Floe
actor-utilpol1-name = Utility Pole
actor-utilpol2-name = Utility Pole
actor-tanktrap1-name = Tank Trap
actor-tanktrap2-name = Tank Trap

## defaults.yaml
notification-unit-lost = Unit lost.
notification-airborne-unit-lost = Airborne Unit lost.
notification-naval-unit-lost = Naval Unit lost.
notification-unit-promoted = Unit promoted.
notification-primary-building-selected = Primary building selected.
notification-structure-captured = Structure captured.
notification-unit-stolen = Unit stolen.

meta-vehicle-generic-name = Vehicle
meta-infantry-generic-name = Soldier
meta-civinfantry-name = Civilian
meta-ship-generic-name = Ship
meta-neutralplane-generic-name = Plane
meta-helicopter-generic-name = Helicopter
meta-basicbuilding-generic-name = Structure
meta-techbuilding-name = Civilian Building
meta-ammobox-name = Ammo Box
meta-civfield-name = Field

meta-civhaystackorigloo =
    .winter-name = Igloo
    .summer-name = Haystack

meta-tree-name = Tree
meta-treehusk-name = Tree (Burnt)
meta-box-name = Boxes
meta-husk-generic-name = Destroyed Vehicle
meta-planehusk-generic-name = Destroyed Plane
meta-helicopterhusk-generic-name = Destroyed Helicopter
meta-bridge-name = Bridge
meta-rock-name = Rock

meta-crate =
    .name = Crate
    .generic-name = Crate

meta-mine =
    .name = Mine
    .generic-name = Mine

## fakes.yaml
actor-fpwr =
    .name = Fake Solar Array
    .generic-name = Solar Array
    .description = Looks like a Solar Array.

actor-tenf =
    .name = Fake Consortium Barracks
    .generic-name = Consortium Barracks
    .description = Looks like a Consortium Barracks.

actor-syrf =
    .name = Fake Naval Yard
    .generic-name = Naval Yard
    .description = Looks like a Naval Yard.

actor-spef =
    .name = Fake Sub Pen
    .generic-name = Sub Pen
    .description = Looks like a Sub Pen.

actor-weaf =
    .name = Fake War Factory
    .generic-name = War Factory
    .description = Looks like a War Factory.

actor-domf =
    .name = Fake Radar Dome
    .generic-name = Radar Dome
    .description = Looks like a Radar Dome.

actor-fixf =
    .name = Fake Service Depot
    .generic-name = Service Depot
    .description = Looks like a Service Depot.

actor-fapw =
    .name = Fake Advanced Solar Array
    .generic-name = Advanced Solar Array
    .description = Looks like an Advanced Solar Array.

actor-atef =
    .name = Fake Consortium Tech Center
    .generic-name = Consortium Tech Center
    .description = Looks like a Consortium Tech Center.

actor-pdof =
    .name = Fake Chronosphere
    .generic-name = Chronosphere
    .description =
    Looks like a Chronosphere.
    Maximum of one can be built.

actor-mslf =
    .name = Fake Missile Silo
    .generic-name = Missile Silo
    .description =
    Looks like a Missile Silo.
    Maximum of one can be built.

actor-facf =
    .name = Fake Construction Yard
    .generic-name = Construction Yard
    .description = Looks like a Construction Yard.

## husks.yaml
actor-2tnk-husk-name = Husk (Medium Tank)
actor-3tnk-husk-name = Husk (Heavy Tank)
actor-4tnk-husk-name = Husk (Mammoth Tank)
actor-harv-fullhusk-name = Husk (Ore Truck)
actor-harv-emptyhusk-name = Husk (Ore Truck)
actor-mcv-husk-name = Husk (Mobile Construction Vehicle)
actor-mgg-husk-name = Husk (Mobile Gap Generator)
actor-tran-husk-name = Chinook
actor-tran-husk1-name = Husk (Chinook)
actor-tran-husk2-name = Husk (Chinook)
actor-badr-husk-name = Badger
actor-mig-husk-name = MiG Attack Plane
actor-yak-husk-name = Yak Attack Plane
actor-heli-husk-name = Longbow
actor-hind-husk-name = Wasp Gunship
actor-u2-husk-name = Husk (Recon Plane)
actor-mh60-husk-name = Black Hawk

## infantry.yaml
notification-building-infiltrated = Building infiltrated.

actor-dog =
    .name = Attack Dog
    .generic-name = Dog
    .description =
    Anti-infantry unit.
    Can detect spies.
      Strong vs Infantry
      Weak vs Vehicles and Aircraft

actor-e1 =
    .name = Rifle Infantry
    .description =
    General-purpose infantry.
      Strong vs Infantry
      Weak vs Vehicles and Aircraft

actor-e2 =
    .name = Grenadier
    .description =
    Infantry with grenades.
      Strong vs Buildings and Infantry
      Weak vs Vehicles and Aircraft

actor-e3 =
    .name = Rocket Soldier
    .description =
    Anti-tank/Anti-aircraft infantry.
      Strong vs Vehicles and Aircraft
      Weak vs Infantry

actor-disr =
    .name = Disruptor Trooper
    .description =
    Advanced anti-structure unit, wielding a
    short-range grid-current disruptor.
      Strong vs Infantry and Buildings
      Weak vs Vehicles and Aircraft

actor-e6 =
    .name = Engineer
    .description =
    Infiltrates and captures
    enemy structures.
      Unarmed

actor-spy =
    .disguisetooltip-name = Spy
    .disguisetooltip-generic-name = Soldier
    .description =
    Infiltrates enemy structures for intel or
    sabotage. Exact effect depends on the
    building infiltrated.
    Loses disguise when attacking.
    Can detect spies.
      Strong vs Infantry
      Weak vs Vehicles and Aircraft
      Special Ability: Disguised

actor-spy-england-disguisetooltip-name = Auditor

actor-e7 =
    .name = Tanya
    .description =
    Elite commando infantry, with dual pistols
    and C4.
    Maximum of one can be built.
      Strong vs Infantry and Buildings
      Weak vs Vehicles and Aircraft
      Special Ability: Destroys buildings with C4

actor-medi =
    .name = Medic
    .description =
    Heals nearby infantry.
      Unarmed

actor-mech =
    .name = Mechanic
    .description =
    Repairs nearby vehicles and restores husks to
    working condition by capturing them.
      Unarmed

actor-einstein-name = Prof. Einstein
actor-delphi-name = Agent Delphi
actor-chan-name = Scientist
actor-gnrl-name = General

actor-thf =
    .name = Thief
    .description =
    Steals enemy credits.
    Hijacks enemy vehicles.
      Unarmed

actor-shok =
    .name = Shock Trooper
    .description =
    Elite infantry with portable Tesla coils.
      Strong vs Infantry and Vehicles
      Weak vs Aircraft

actor-zombie =
    .name = Blighted
    .description =
    Scavenger consumed by grid contamination, drawn to close combat.

actor-ant =
    .name = Swarmling
    .generic-name = Swarmling
    .description =
    Insect fauna mutated to an abnormal size by leaking grid energy.

actor-fireant-name = Cinderling
actor-scoutant-name = Scoutling
actor-warriorant-name = Bulwarkling

## misc.yaml
notification-sonar-pulse-ready = Sonar pulse ready.

actor-moneycrate-name = Money Crate
actor-healcrate-name = Heal Crate
actor-wcrate-name = Wooden Crate
actor-scrate-name = Steel Crate
actor-camera-name = (reveals area to owner)
actor-camera-paradrop-name = (support power proxy camera)
actor-camera-spyplane-name = (support power proxy camera)
actor-sonar-name = (support power proxy camera)
actor-flare-name = Flare
actor-mine-name = Ore Mine
actor-gmine-name = Gem Mine
actor-railmine-name = Abandoned Mine
actor-quee-name = Queen Ant
actor-lar1-name = Ant Larva
actor-lar2-name = Ant Larvae
actor-mpspawn-name = (multiplayer starting point)
actor-waypoint-name = (waypoint for scripted behavior)
actor-ctflag-name = Flag

## ships.yaml
actor-ss =
    .name = Submarine
    .description =
    Submerged anti-ship unit with torpedoes.
    Can detect other submarines.
      Strong vs Naval units
      Weak vs Ground units and Aircraft
      Special Ability: Submerge

actor-msub =
    .name = Missile Submarine
    .description =
    Submerged anti-ground siege unit with anti-air
    capabilities.
    Can detect other submarines.
      Strong vs Buildings, Ground units and Aircraft
      Weak vs Naval units
      Special Ability: Submerge

actor-dd =
    .name = Destroyer
    .description =
    Fast multi-role ship.
    Can detect submarines.
      Strong vs Naval units, Vehicles and Aircraft
      Weak vs Infantry

actor-ca =
    .name = Cruiser
    .description =
    Very slow long-range ship.
      Strong vs Buildings and Ground units
      Weak vs Naval units and Aircraft

actor-lst =
    .name = Transport
    .description =
    General-purpose naval transport.
    Carries infantry and tanks
      Unarmed

actor-pt =
    .name = Gunboat
    .description =
    Light scout and support ship.
    Can detect submarines.
      Strong vs Naval units
      Weak vs Ground units and Aircraft

## structures.yaml
notification-construction-complete = Construction complete.
notification-unit-ready = Unit ready.
notification-unable-to-build-more = Unable to build more.
notification-unable-to-comply-building-in-progress = Unable to comply. Building in progress.
notification-repairing = Repairing.
notification-unit-repaired = Unit repaired.
notification-select-target = Select target.
notification-insufficient-power = Insufficient power.
notification-reinforcements-have-arrived = Reinforcements have arrived.
notification-abomb-prepping = A-bomb prepping.
notification-abomb-ready = A-bomb ready.
notification-abomb-launch-detected = A-bomb launch detected.
notification-iron-curtain-charging = Iron curtain charging.
notification-iron-curtain-ready = Iron curtain ready.
notification-chronosphere-charging = Chronosphere charging.
notification-chronosphere-ready = Chronosphere ready.
notification-satellite-launched = Satellite launched.
notification-credits-stolen = Credits stolen.
notification-spy-plane-ready = Spy plane ready.

actor-mslo =
    .name = Missile Silo
    .description =
    Provides an atomic bomb.
    Requires power to operate.
    Maximum of one can be built.
      Special Ability: Atom Bomb
    .nukepower-name = Atom Bomb
    .nukepower-description = Launches a devastating atomic bomb
    at the target location.

actor-gap =
    .name = Gap Generator
    .description =
    Obscures the enemy's view with shroud.
    Requires power to operate.

actor-spen =
    .name = Sub Pen
    .description =
    Produces and repairs submarines
    and transports.

actor-syrd =
    .name = Naval Yard
    .description =
    Produces and repairs ships and
    transports.

actor-iron =
    .name = Iron Curtain
    .description =
    Grants a group of units temporary
    invulnerability.
    Requires power to operate.
    Maximum of one can be built.
      Special Ability: Invulnerability
    .grantexternalconditionpower-ironcurtain-name = Invulnerability
    .grantexternalconditionpower-ironcurtain-description = Grants invulnerability to a group of units
    for 20 seconds.

actor-pdox =
    .name = Chronosphere
    .description =
    Teleports a group of units across
    the map for a short time.
    Requires power to operate.
    Maximum of one can be built.
      Special Ability: Chronoshift
    .chronoshiftpower-chronoshift-name = Chronoshift
    .chronoshiftpower-chronoshift-description = Teleports a group of units across
    the map for 20 seconds.
    .chronoshiftpower-advancedchronoshift-name = Advanced Chronoshift
    .chronoshiftpower-advancedchronoshift-description = Teleports a large group of units across
    the map for 20 seconds.

actor-tsla =
    .name = Tesla Coil
    .description =
    Advanced base defense.
    Requires power to operate.
    Can detect cloaked units.
      Strong vs Vehicles and Infantry
      Weak vs Aircraft

actor-agun =
    .name = AA Gun
    .description =
    Anti-Air base defense.
    Requires power to operate.
      Strong vs Aircraft
      Weak vs Ground units

actor-dome =
    .name = Radar Dome
    .description =
    Provides an overview of
    the battlefield.
    Requires power to operate.

actor-pbox =
    .name = Pillbox
    .description =
    Static defense with a fireport for
    a garrisoned soldier.
    Can detect cloaked units.
      Strong vs Infantry and Light armor
      Weak vs Tanks and Aircraft

actor-hbox =
    .name = Camo Pillbox
    .description =
    Camouflaged static defense with a fireport
    for a garrisoned soldier.
    Can detect cloaked units.
      Strong vs Infantry and Light armor
      Weak vs Tanks and Aircraft

actor-gun =
    .name = Turret
    .description =
    Anti-Armor base defense.
    Can detect cloaked units.
      Strong vs Vehicles
      Weak vs Infantry and Aircraft

actor-arct =
    .name = Arc Turret
    .description =
    Anti-Infantry base defense drawing a
    direct discharge off the local grid.
    Can detect cloaked units.
      Strong vs Infantry and Light armor
      Weak vs Tanks and Aircraft

actor-sam =
    .name = SAM Site
    .description =
    Anti-Air base defense.
    Requires power to operate.
      Strong vs Aircraft
      Weak vs Ground units

actor-atek =
    .name = Consortium Tech Center
    .description =
    Provides advanced Consortium technology.
      Special Ability: GPS Satellite
    .gpspower-name = GPS Satellite
    .gpspower-description =
    Reveals map terrain and provides tactical information.
    Requires power and active radar.

actor-weap =
    .name = War Factory
    .description =
    Produces vehicles.

actor-fact =
    .name = Construction Yard
    .description =
    Produces structures.

actor-proc =
    .name = Materials Refinery
    .description =
    Converts harvested Ore and Gems into
    credits.

actor-silo =
    .name = Battery Bank
    .description =
    Stores surplus grid capacity, preventing
    resources from overflowing. Also banks spendable
    credits into permanent Grid Reserve for the
    economic victory mode, when enabled.

actor-rcyd =
    .name = Recycling Depot
    .description =
    Reclaims scrap from the battlefield and
    recycles it into a steady trickle of credits.
    Draws a modest amount of power.

actor-hpad =
    .name = Helipad
    .description =
    Produces and reloads helicopters.

actor-afld =
    .name = Airfield
    .description =
    Produces and reloads aircraft.
      Special Ability: Recon Plane
      Special Ability: Paratroopers
    .airstrikepower-spyplane-name = Recon Plane
    .airstrikepower-spyplane-description = Reveals an area of the map.
    .paratrooperspower-paratroopers-name = Paratroopers
    .paratrooperspower-paratroopers-description = A Badger drops a squad of infantry
    at the selected location.
    .airstrikepower-parabombs-name = Parabombs
    .airstrikepower-parabombs-description = A Badger drops parachuted bombs
    at the selected location.

actor-afld-ukraine-description =
    Produces and reloads aircraft.
      Special Ability: Recon Plane
      Special Ability: Paratroopers
      Special Ability: Parabombs

actor-powr =
    .name = Solar Array
    .description =
    A field of grid-tied solar panels.
    Provides power for other
    structures.

actor-apwr =
    .name = Advanced Solar Array
    .description =
    Provides double the power of a standard
    Solar Array, at a steeper cost per watt.

actor-sgwnd =
    .name = Wind Turbine Array
    .description =
    Assembly power infrastructure. Cheap, early and
    individually fragile turbines - scale power by spreading
    them out rather than turtling a single plant.

actor-sghyd =
    .name = Hydrogen Plant
    .description =
    Consortium power infrastructure. An expensive, hardened,
    late-tech consolidation of grid supply into a single
    high-output plant - and a single very high-value target.

actor-stek =
    .name = Assembly Tech Center
    .description =
    Provides advanced Assembly technology.

actor-barr =
    .name = Assembly Barracks
    .description =
    Trains infantry units.

actor-kenn =
    .name = Kennel
    .description =
    Trains Attack Dogs.

actor-tent =
    .name = Consortium Barracks
    .description =
    Trains infantry.

actor-fix =
    .name = Service Depot
    .description =
    Repairs vehicles for credits.

actor-sbag =
    .name = Sandbag Wall
    .description =
    Stops infantry and light vehicles.
       Can be crushed by tanks.

actor-fenc =
    .name = Wire Fence
    .description =
    Stops infantry and light vehicles.
       Can be crushed by tanks.

actor-brik =
    .name = Concrete Wall
    .description =
    Stops units and blocks enemy fire.

actor-cycl-name = Chain-Link Barrier
actor-barb-name = Barbed-Wire Fence
actor-wood-name = Wooden Fence
actor-barracks-name = Infantry Production
actor-techcenter-name = Tech Center
actor-anypower-name = Any Power Generation

## vehicles.yaml
actor-v2rl =
    .name = Surge Rocket Launcher
    .description =
    Long-range rocket artillery.
      Strong vs Infantry and Buildings
      Weak vs Vehicles and Aircraft

actor-1tnk =
    .name = Light Tank
    .generic-name = Tank
    .description =
    Fast tank; good for scouting.
      Strong vs Light armor
      Weak vs Infantry, Tanks and Aircraft

actor-2tnk =
    .name = Medium Tank
    .generic-name = Tank
    .description =
    Consortium Main Battle Tank.
      Strong vs Vehicles
      Weak vs Infantry and Aircraft

actor-3tnk =
    .name = Heavy Tank
    .generic-name = Tank
    .description =
    Assembly Main Battle Tank with dual cannons.
      Strong vs Vehicles
      Weak vs Infantry and Aircraft

actor-4tnk =
    .name = Mammoth Tank
    .generic-name = Tank
    .description =
    Large, slow tank with anti-air capabilities.
    Can crush concrete walls.
      Strong vs Vehicles, Infantry and Aircraft
      Weak vs Nothing

actor-arty =
    .name = Artillery
    .description =
    Long-range artillery.
      Strong vs Infantry and Buildings
      Weak vs Vehicles and Aircraft

actor-harv =
    .name = Ore Truck
    .generic-name = Harvester
    .description =
    Collects Ore and Gems for
    processing.
      Unarmed

actor-sghau =
    .name = Hauler Drone
    .generic-name = Hauler
    .description =
    Collects small amounts of Scrap
    for recycling at a Recycling Depot.
      Unarmed

actor-mcv =
    .name = Mobile Construction Vehicle
    .description =
    Deploys into a Construction Yard.
      Unarmed

actor-jeep =
    .name = Ranger
    .description =
    Fast scout and anti-infantry vehicle.
    Can carry just one infantry unit.
      Strong vs Infantry
      Weak vs Vehicles and Aircraft

actor-apc =
    .name = Armored Personnel Carrier
    .description =
    Tough infantry transport.
      Strong vs Infantry and Light armor
      Weak vs Tanks and Aircraft

actor-mnly =
    .name = Minelayer
    .description =
    Lays mines to destroy
    unwary enemy units.
    Can detect mines.
      Unarmed

actor-truk =
    .name = Supply Truck
    .description =
    Transports cash to other players.
      Unarmed

actor-mgg =
    .name = Mobile Gap Generator
    .description =
    Regenerates shroud to obscure nearby areas.
      Unarmed

actor-mrj =
    .name = Mobile Radar Jammer
    .description =
    Jams nearby enemy Radar Domes
    and deflects incoming missiles.
      Unarmed

actor-ttnk =
    .name = Tesla Tank
    .generic-name = Tank
    .description =
    Tank with mounted Tesla coil.
      Strong vs Infantry, Vehicles and Buildings
      Weak vs Aircraft

actor-ftrk =
    .name = Mobile Flak
    .description =
    Mobile unit with a Flak cannon.
      Strong vs Infantry, Light armor and Aircraft
      Weak vs Tanks

actor-dtrk =
    .name = Demolition Truck
    .description =
    Truck carrying armed nuclear explosives,
    with very weak armor.

actor-ctnk =
    .name = Chrono Tank
    .generic-name = Tank
    .description =
    Armed with anti-ground missiles.
    Teleports to any area within range.
      Strong vs Vehicles and Buildings
      Weak vs Infantry and Aircraft
      Special ability: Can teleport

actor-qtnk =
    .name = Tremor Tank
    .generic-name = Tank
    .description =
    Deals seismic damage to nearby vehicles
    and structures.
      Strong vs Vehicles and Buildings
      Weak vs Infantry and Aircraft

actor-stnk =
    .name = Phase Transport
    .description =
    Light armored infantry transport which can
    cloak. Armed with anti-ground missiles.
      Strong vs Light armor
      Weak vs Infantry, Tanks and Aircraft

## Civilian Tech
actor-hosp =
    .name = Hospital
    .captured-desc = Provides infantry with self-healing.
    .capturable-desc = Capture to enable self-healing for infantry.

actor-fcom =
    .name = Forward Command
    .captured-desc = Provides buildable area.
    .capturable-desc = Capture to give buildable area.

actor-miss =
    .name = Communications Center
    .captured-desc = Provides range of vision.
    .capturable-desc = Capture to give visual range.

actor-bio =
    .name = Containment Ruins
    .captured-desc = A leaking containment site. Provides prerequisite for grid-mutated fauna.
    .capturable-desc = Capture to produce grid-mutated fauna.

actor-oilb =
    .name = Oil Derrick
    .captured-desc = Provides additional funds.
    .capturable-desc =  Capture to receive additional funds.

## misc.yaml
actor-powerproxy-parabombs =
    .name = Parabombs (Single Use)
    .description =
    A Badger drops parachuted bombs
    over a selected location.

actor-powerproxy-sonarpulse =
    .name = Sonar Pulse
    .description =
    Reveals all submarines in the vicinity for a
    short time.

actor-powerproxy-paratroopers =
    .name = Paratroopers
    .description =
    A Badger drops a squad of infantry
    anywhere on the map.

## ai.yaml
bot-rush-ai =
    .name = Rush AI

bot-normal-ai =
    .name = Normal AI

bot-turtle-ai =
    .name = Turtle AI

bot-naval-ai =
    .name = Naval AI

## map-generators.yaml
label-random-map = Random Map
label-clear-map-generator-option-tile = Tile
label-clear-map-generator-choice-tile-clear =
   .label = Clear
label-clear-map-generator-choice-tile-water =
   .label = Water
label-clear-map-generator-choice-tile-empty =
   .label = Empty space

label-ra-map-generator-option-seed = Seed

label-ra-map-generator-option-terrain-type = Terrain Type
label-ra-map-generator-choice-terrain-type-lakes =
   .label = Lakes
   .description = Open spaces with moderately sized lakes
label-ra-map-generator-choice-terrain-type-puddles =
   .label = Puddles
   .description = Open spaces with small ponds
label-ra-map-generator-choice-terrain-type-gardens =
   .label = Gardens
   .description = Densely-packed terrain with ponds, cliffs, and forests
label-ra-map-generator-choice-terrain-type-plots =
   .label = Plots
   .description = Loosely-packed terrain with ponds, cliffs, and forests
label-ra-map-generator-choice-terrain-type-plains =
   .label = Plains
   .description = Open spaces with sparse trees and cliffs
label-ra-map-generator-choice-terrain-type-parks =
   .label = Parks
   .description = Open spaces with light forestry and occasional cliffs
label-ra-map-generator-choice-terrain-type-woodlands =
   .label = Woodlands
   .description = Moderate forestry with occasional cliffs
label-ra-map-generator-choice-terrain-type-overgrown =
   .label = Overgrown
   .description = Narrow passages, dense forestry and moderate cliffs
label-ra-map-generator-choice-terrain-type-rocky =
   .label = Rocky
   .description = Moderate cliffs with light forestry
label-ra-map-generator-choice-terrain-type-mountains =
   .label = Mountains
   .description = Many long cliffs
label-ra-map-generator-choice-terrain-type-mountain-lakes =
   .label = Mountain Lakes
   .description = Lakes and many long cliffs
label-ra-map-generator-choice-terrain-type-oceanic =
   .label = Oceanic
   .description = Small islands separated by an ocean
label-ra-map-generator-choice-terrain-type-large-islands =
   .label = Large Islands
   .description = Large islands separated by an ocean
label-ra-map-generator-choice-terrain-type-continents =
   .label = Continents
   .description = Large bodies of land and water
label-ra-map-generator-choice-terrain-type-wetlands =
   .label = Wetlands
   .description = Loose mixtures of land and water
label-ra-map-generator-choice-terrain-type-narrow-wetlands =
   .label = Narrow Wetlands
   .description = Tight mixtures of land and water

label-ra-map-generator-option-symmetry = Symmetry
label-ra-map-generator-choice-mirror-none =
   .label = None
label-ra-map-generator-choice-symmetry-mirror-horizontal =
   .label = Mirror Horizontal
label-ra-map-generator-choice-symmetry-mirror-vertical =
   .label = Mirror Vertical
label-ra-map-generator-choice-symmetry-mirror-diagonal-tl =
   .label = Mirror Diagonal (Top-Left)
label-ra-map-generator-choice-symmetry-mirror-diagonal-tr =
   .label = Mirror Diagonal (Top-Right)
label-ra-map-generator-choice-symmetry-mirror-2-rotations =
   .label = 2 Rotations
label-ra-map-generator-choice-symmetry-mirror-3-rotations =
   .label = 3 Rotations
label-ra-map-generator-choice-symmetry-mirror-4-rotations =
   .label = 4 Rotations
label-ra-map-generator-choice-symmetry-mirror-5-rotations =
   .label = 5 Rotations
label-ra-map-generator-choice-symmetry-mirror-6-rotations =
   .label = 6 Rotations
label-ra-map-generator-choice-symmetry-mirror-7-rotations =
   .label = 7 Rotations
label-ra-map-generator-choice-symmetry-mirror-8-rotations =
   .label = 8 Rotations

label-ra-map-generator-option-shape = Boundary Shape
label-ra-map-generator-choice-shape-square =
   .label = Rectangle
   .description = Playable area is the full map
label-ra-map-generator-choice-shape-circle-mountain =
   .label = Circle in mountains
   .description = Playable area is contained within a circular mountain range
label-ra-map-generator-choice-shape-circle-water =
   .label = Circle in water
   .description = Playable area is a circular island

label-ra-map-generator-option-players = Players

label-ra-map-generator-option-resources = Resources
label-ra-map-generator-choice-resources-none =
   .label = None
label-ra-map-generator-choice-resources-low =
   .label = Low
label-ra-map-generator-choice-resources-medium =
   .label = Medium
label-ra-map-generator-choice-resources-high =
   .label = High
label-ra-map-generator-choice-resources-very-high =
   .label = Very High
label-ra-map-generator-choice-resources-full =
   .label = Oreful

label-ra-map-generator-option-buildings = Tech Structures
label-ra-map-generator-choice-buildings-none =
   .label = None
   .description = No tech structures
label-ra-map-generator-choice-buildings-standard =
   .label = Standard
   .description = Oil Derricks, Hospitals, and Communication Centers
label-ra-map-generator-choice-buildings-extra =
   .label = Extra
   .description = Oil Derricks, Hospitals, Communication Centers, Forward Command Posts
label-ra-map-generator-choice-buildings-oil-only =
   .label = Oil Only
   .description = Oil Derricks only
label-ra-map-generator-choice-buildings-oil-rush =
   .label = Oil Rush
   .description = Lots of Oil Derricks

label-ra-map-generator-option-density = Expansion Opportunities
label-ra-map-generator-choice-density-players =
   .label = Scale with players
label-ra-map-generator-choice-density-area-and-players =
   .label = Scale with size and players
label-ra-map-generator-choice-density-area-very-low =
   .label = Very Low
label-ra-map-generator-choice-density-area-low =
   .label = Low
label-ra-map-generator-choice-density-area-medium =
   .label = Medium
label-ra-map-generator-choice-density-area-high =
   .label = High
label-ra-map-generator-choice-density-area-very-high =
   .label = Very High

label-ra-map-generator-option-roads = Roads
label-ra-map-generator-option-deny-walled-areas = Obstruct walled areas

label-ra-map-generator-option-civilian-density = Civilian Density
label-ra-map-generator-choice-civilian-density-default =
   .label = Default
label-ra-map-generator-choice-civilian-density-none =
   .label = None
label-ra-map-generator-choice-civilian-density-low =
   .label = Low
label-ra-map-generator-choice-civilian-density-medium =
   .label = Medium
label-ra-map-generator-choice-civilian-density-high =
   .label = High
label-ra-map-generator-choice-civilian-density-very-high =
   .label = Very High
label-ra-map-generator-choice-civilian-density-max =
   .label = Maximum

actor-sgcry =
    .name = Cryptominer
    .description =
    Repurposed compute infrastructure grinding through
    legacy proof-of-work for a steady, high income.
    Draws heavy power; throttles when the grid is strained.

actor-sgdai =
    .name = Datacenter for AI
    .description =
    Racks of compute serving grid logistics and battlefield
    analytics. Enormous, constant power draw. Income and
    cloak detection both fall away once the grid is strained,
    and stop outright under critical power. Its coordination
    is required to build the most advanced structures and
    drone units.

actor-sgdrn =
    .name = Drone Bay
    .description =
    Assembly infrastructure. Autonomous delivery drones speed
    up nearby friendly vehicles, easing logistics across a
    spread-out base. Produces Recon Drones once a Datacenter
    for AI is built. Drones lose their weapons fleet-wide
    once the grid drops to critical power.

actor-sgdro =
    .name = Recon Drone
    .description =
    A cheap, fast Assembly scout drone armed with small
    rockets. Wide sensor range, very light armour. Requires
    a Drone Bay and a Datacenter for AI. Weapons cut out if
    the Assembly's grid falls to critical power.

actor-sgdrs =
    .name = Strike Drone
    .description =
    A pricier, harder-hitting Consortium counterpart to the
    Assembly's Recon Drone. Still very light armour. Requires
    an Aerial Fabrication Bay and a Datacenter for AI. Weapons
    cut out if the Consortium's grid falls to critical power.

actor-sgdra =
    .name = Aerial Fabrication Bay
    .description =
    Consortium infrastructure. The Consortium's dedicated
    counterpart to the Assembly's Drone Bay: autonomous
    delivery drones speed up nearby friendly vehicles.
    Produces Strike Drones once a Datacenter for AI is built.

actor-sgtur =
    .name = Grid Defense Turret
    .description =
    A point-defense turret drawing directly off the local
    grid. Hits harder when the grid is healthy, weaker when
    power is strained.

actor-sgrel =
    .name = Smart Grid Relay
    .description =
    A grid-balancing relay station providing a modest
    secondary supply of power.

actor-sgshl =
    .name = Resilience Shelter
    .description =
    A hardened civil-defense structure. Nearby structures
    take reduced damage while it has power.

actor-sgsns =
    .name = Sensor Array
    .description =
    A distributed sensor mesh reading grid load, drone
    traffic, and terrain. Wide vision radius; detects
    cloaked units.
