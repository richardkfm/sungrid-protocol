# Sungrid Protocol — Energy Economy Rebalance & Faction Power Identity

A follow-up pass to `docs/BUILDINGS.md`'s Phase 5 roster and the faction roster dossier
(`docs/concept-art/faction-roster-dossier.html`). Goal: make energy genuinely scarce and worth fighting over
for the whole match, give The Consortium and The Assembly distinct power-generation identities instead of a
single universal Solar Array/Advanced Solar Array, and drop the leftover 90s "It Came from Red Alert"
Giant Ant/Zombie easter-egg content in favor of something that fits the grid-contamination tone. All of it is
data-driven — pure YAML/fluent changes, no new C#, per `docs/ARCHITECTURE.md`'s data-driven-first principle.

## Why energy needed tightening

Before this pass, the full power ledger (pulled directly from `mods/sungrid/rules/structures.yaml`) showed two
real gaps in the "energy is scarce and hard-won" design pillar (`docs/VISION.md` #4):

- `APWR` (Advanced Solar Array) was a strictly *better* power-per-credit investment than `POWR` (Solar Array)
  once `dome` was unlocked (0.4 power/credit vs 0.33), so there was no real tension in scaling power — just an
  obvious one-time upgrade.
- `SGDAI` (Datacenter for AI) drained only -60 power and had **zero** power-state interaction, despite being a
  hard prerequisite for both factions' drone units. The building framed as the "brains behind smart-grid
  coordination" didn't actually care whether the grid was healthy.

## Changes

| Actor | Before | After | Why |
|---|---|---|---|
| `APWR` Advanced Solar Array | Cost 500, Power +200 | **Cost 1000**, Power +200 | Flips APWR from a strict upgrade (0.4 power/credit) into a real tradeoff (0.2 power/credit — worse per-credit than just building more `POWR`). Scaling power now always costs real, increasing investment. |
| `SGCRY` Cryptominer | Power -120 | **Power -150** | Reinforces "enormous" power demand alongside the Datacenter. |
| `SGCRY` Cryptominer | `STRAINED` condition only at `Low` power (Critical power silently dropped income to 0) | `STRAINED` now covers `Low, Critical` | Closes a gap — income now degrades on a real curve (45→15/tick) instead of a silent cliff to zero. |
| `SGDAI` Datacenter for AI | Power -60, no power-state interaction | **Power -140**, full `GrantConditionOnPowerState` gating | Was the weakest link — a hard prerequisite for both drone units that didn't care about grid health. Now matches `SGCRY`'s order of magnitude and genuinely degrades: `CashTrickler` drops 20→8/tick under strain. (This row also credited a power-gated `DetectCloaked` at the time; issue #77 later moved detection to `SGSNS`, so income is the only thing this building's power state changes.) |
| `SGDRO`/`SGDRS` (Recon/Strike Drone) | No power interaction on the unit itself | `GrantConditionOnPowerState` gates each drone's own `Armament` | Drones lose their weapons fleet-wide — not just those near a Drone Bay — once their owner's grid drops to Critical power. Verified feasible via this repo's own pre-SDK-migration git history: `GrantConditionOnPowerState` only depends on `Owner.PlayerActor.Trait<PowerManager>()`, no Building requirement, so it works on aircraft the same as on structures. |

## New faction power buildings

Both are **additive** alternatives to `POWR`/`APWR` (which stay available to both sides as the safe baseline)
— not replacements — so no side loses power access, and each is a real tradeoff rather than a strict upgrade,
keeping power a constant spend-vs-save decision (`docs/VISION.md` #3) rather than a one-time solved problem.

### Wind Turbine Array (`SGWND`) — Assembly

Cheap (250 — retuned from the original 400 after the `docs/BUILDINGS.md` roster survey found it strictly dominated by Solar Array at that price), early (`~techlevel.low`, a tier before Advanced Solar Array), individually fragile (30000 HP —
the lowest of any power building), and **one cell** (issue #100 — it was 2×2 until then, i.e. it cost a Solar
Array's worth of base space for less power, which is exactly the "too close to Solar Array" complaint the
price cut alone never fixed). Space, not price, is what now makes a turbine a different building rather than
a cheaper one: 70 power per cell against Solar Array's 25, paid for in HP, armour and blackout exposure.
Rewards spreading turbines out across a base rather than turtling one big
plant, keeping raiding and map pressure relevant on the power layer (`docs/VISION.md` #4 "pressure never
disappears"). Fits the Assembly's already-declared "decentralized/scarcity-adapted/improvisational"
infrastructure identity (`docs/ART_DIRECTION.md`), which was previously only expressed through the Drone Bay.

### Hydrogen Plant (`SGHYD`) — Consortium

Expensive (1200), late (`dome, atek, ~techlevel.high`), hardened (90000 HP, Heavy armor), and by far the
single largest power output in the game (+350). One big building instead of many small ones — a strong single
point of failure that doesn't trivialize scarcity, it just relocates the risk. Fits the Consortium's
"centralized/hardened grid/capital-technocratic" identity from the same doc.

### How this evens the factions out

This isn't just flavor — it's backed by the existing power ledger's own asymmetries. Consortium's late-game
footprint already carries heavier power drains than Assembly's direct counterparts at matching cost tiers:

- `ATEK` (Consortium Tech Center) drains -200 vs `STEK` (Assembly Tech Center) -100, at the same 1500 cost.
- `GAP` (Consortium Gap Generator) drains -60/800 vs Assembly's closest analog, `AGUN` (-50/800) — updated from `SAM` when issue #84 swapped which side builds `AGUN`/`SAM`.

Giving Consortium the large, late Hydrogen Plant helps offset that existing heavier late-tech-tree drain
burden with a correspondingly large supply option. Assembly's cheaper, earlier Wind Turbine Array suits its
already-lighter, faster-tempo drain profile without over-supplying it. Neither building is a strict power
upgrade over the other — they're differently-shaped answers to each faction's differently-shaped power demand.

## Drone Bay parity (`SGDRA`)

Previously only the Assembly had a dedicated Drone Bay (`SGDRN`); the Consortium's Strike Drone (`SGDRS`) was
bolted onto the Helipad instead of getting its own structure. Added `SGDRA` ("Aerial Fabrication Bay"),
Consortium-only, an exact mechanical mirror of `SGDRN` (same cost, power drain, speed-aura, production
pattern) with faction-flipped prerequisites. `SGDRS`'s prerequisites moved from `~hpad, sgdai` to
`sgdra, sgdai`; the Helipad keeps producing its existing helicopter roster untouched. The existing
recon-vs-strike differentiation (`SGDRO` 350cost/light-recon, `SGDRS` 600cost/heavier-strike) remains the real
flavor axis between the two drones — both factions now just have a properly symmetric building for it.

**Correction (issue #78).** "Bolted onto the Helipad" and "moved from `~hpad`" describe a prerequisite
change, and only a prerequisite change — the paragraph above overstated what it accomplished. Both bays
still declared `Produces: Aircraft, Helicopter`, the same production type `HPAD` and `AFLD` declare, and
`ClassicProductionQueue.BuildUnit` dispatches to *any* owned producer carrying the requested type. So
Strike Drones kept rolling out of the Helipad and Recon Drones out of the Airfield; the bays were
prerequisite tokens with a rally point, destructible without interrupting a single drone. The bays now
produce a dedicated `Drone` type nothing else in the mod declares, and both drones set
`BuildAtProductionType: Drone`, which is what this section always meant. Both drones also dropped to
`~techlevel.medium` to match their bay's tier and are gated on the bay alone (`~sgdrn`/`~sgdra`);
`sgdai` keeps gating the three superweapons. See `docs/BACKLOG.md` issues #77 (survey) and #78 (fix).

## Smart Grid Relay (`SGREL`): what the 400 Credits actually buy

This building was missing from this document entirely until issue #79, which is a problem, because
its numbers look bad and the reason to build one is invisible. At 400 Credits for `+60 Power` it is
**by far the worst credits-per-power in the game** — more than double a Solar Array:

| | Cost | Power | cr/power | HP | Cells | power/cell | HP/cell | Power scales with damage | Disabled by outage |
|---|---|---|---|---|---|---|---|---|---|
| `POWR` Solar Array | 300 | +100 | **3.00** | 40000 | 4 | 25 | 10000 | yes | yes |
| `SGWND` Wind Turbine Array | 250 | +70 | 3.57 | 30000 | **1** | **70** | 30000 | yes | yes |
| `SGHYD` Hydrogen Plant | 1200 | +350 | 3.43 | 90000 | 6 | 58 | 15000 | yes | yes |
| `APWR` Advanced Solar Array | 1000 | +200 | 5.00 | 70000 | 6 | 33 | 11667 | yes | yes |
| `SGREL` Smart Grid Relay | 400 | +60 | **6.67** | 50000 | **1** | 60 | **50000** | **no** | **no** |

(The Wind Turbine's `Cells` and `power/cell` are issue #100's; it occupied 4 cells at 17.5 power/cell
until then, which is what made it read as a slightly worse Solar Array.)

The premium buys four properties no other power building has, none of which is stated anywhere the
player can see them:

1. **A 1×1 footprint**, against 4 or 6 occupied cells. It fits gaps, packs behind walls, and can't be
   splashed in bulk. Since issue #100 the Wind Turbine is 1×1 as well, so this is no longer unique —
   but the two are opposite ends of the same cell: the Turbine is the cheap, fragile, health-scaled,
   blackout-able one and the Relay is the expensive, hardened, always-on one. See "Is the Relay
   redundant now?" below.
2. **50000 HP in that single cell** — 3.3× the HP density of the next-toughest power building
   (`SGHYD` at 15000/cell) and 5× a Solar Array's. It is not the densest building in the mod
   (`FIX` is 80000/cell; `MSLO`, `IRON` and `GAP` also reach 50000), but among power sources it is
   in a class of its own. Heavy armour, shared only with `SGHYD`.
3. **No `ScalePowerWithHealth`.** Every other power building bleeds output as it takes damage — a
   Solar Array at 25% health supplies roughly +25. A Relay at 5% health still supplies the full +60.
4. **Not affected by power outage.** Exactly four buildings inherit `^DisabledByPowerOutage`
   (`POWR`, `APWR`, `SGWND`, `SGHYD`), which carries both `InfiltrateForPowerOutage` and
   `AffectedByPowerOutage`. A Spy infiltrating any one of them blacks out *all* of them across the
   owner's base. Relays run straight through it.

Since issue #78 it also provides `anypower`, so a base surviving on Relays alone can still rebuild.

**The coherent reading** is that Solar Arrays are bulk supply and Relays are the floor under it: in a
mod where the Cryptominer's income, the Datacenter's output and the Grid Defense Turret's firepower
all degrade with grid state, paying a premium for power that cannot be raided down or blacked out is
a real trade, and design pillar #4 ("pressure never disappears") is the argument for wanting one.

**What is not established** is whether any of this was designed. `docs/BUILDINGS.md` records the
Relay's original cluster-pooling fantasy as deliberately descoped to "a modest flat secondary power
source"; it says nothing about outage immunity or health-independence, and neither did this document
before now. The two missing `Inherits` lines are equally consistent with a deliberate survivability
niche and with an oversight from when the building was scoped down. **Treat the properties as real
but the intent as unrecorded** — see `docs/BACKLOG.md` issue #79 for the open decision.

### Is the Relay redundant now? (issue #100 follow-up)

Fair question once the Wind Turbine is also 1×1, and the honest answer is *for one faction, nearly*.

The Relay is **not** redundant for the Consortium. `SGWND` is `~structures.soviet`; the Consortium
cannot build a turbine at all, so the Relay stays its only compact power source and its only power
that a Spy blackout can't switch off. Nothing about issue #100 touches that side of the roster.

For the Assembly it is a much narrower building than it was. At the same one cell, a turbine is
150 Credits cheaper, supplies 10 more power, and arrives a tech tier earlier (`~techlevel.low`
against `~techlevel.medium`). What the extra 150 Credits still buy, and they are not nothing:

- **50000 HP behind Heavy armour** against 30000 behind Wood. The nominal gap is 1.67×; the real one
  is larger, since Heavy soaks the small-arms and light-cannon fire most raids arrive with.
- **Full output at any health.** A turbine at 25% health is supplying roughly +18 of its +70; a Relay
  at 5% health is still supplying +60. Under sustained harassment the Relay's *effective* power/cell
  is the one that holds.
- **Immunity to the infiltration blackout** that switches every turbine, Solar Array, Advanced Solar
  Array and Hydrogen Plant dark at once.

So the two 1×1 power buildings now read as the cheap fragile one and the expensive durable one — a
real choice on the same footprint, and arguably a *better* pairing than "the small one is the only
small one". The risk worth watching in playtest is that an Assembly player simply never has a reason
to reach for the Relay, because turbines are cheap enough to replace faster than they die.

**Two options if that is what playtest shows, neither taken here.** Gate the Relay to
`~structures.allies`, mirroring the turbine's Assembly gate, so each faction owns exactly one 1×1
power building expressing its own identity (decentralised-and-fragile against hardened-and-central) —
this is the tidier design and costs the Assembly an option it may not be using. Or leave both open
and let the Relay be the Assembly's answer to *being raided*, which is what it already is. Deleting
the Relay is the one option not worth taking: it is the Consortium's only compact power and the mod's
only power source that a blackout cannot reach, and both of those roles would have to be rebuilt
somewhere else.

## Ant / Zombie replacement

The neutral, capturable "Bio-Research Lab" (`bio` prerequisite, used by the `chernobyl` map's Creeps player)
previously unlocked literal `Zombie` and `Ant` units — classic "It Came from Red Alert" B-movie easter-egg
content that reads as generic 90s filler rather than fitting the solarpunk/grid-contamination tone. Reflavored
in place (actor ids and the `bio` prerequisite token left unchanged, since `desert-shellmap/rules.yaml`
overrides `Ant`'s prerequisites directly and the `chernobyl` map references the neutral actor by id — only
Tooltip names/descriptions changed) — same "reskin the fluff, keep the chassis" pattern already used for Flame
Infantry → Disruptor Trooper (issue #14):

- `Zombie` → **Blighted** — a grid-contaminated scavenger, not literal undead.
- `Ant`/`FireAnt`/`ScoutAnt`/`WarriorAnt` → **Swarmling / Cinderling / Scoutling / Bulwarkling** — the
  existing "irradiated insect" flavor already fit the tone; only the naming was tightened away from generic
  "giant ant" framing.
- The neutral building itself → **Containment Ruins** — a leaking/abandoned containment site rather than a
  generic "Biological Lab."

No new art — same stock sprites, matching the fact that Phase 7 (unit/vehicle sprite work, per
`docs/ROADMAP.md`) hasn't started yet.

## Phase 7 reskin candidates

The broader "which 90s-style units need a full identity pass" question is out of scope for the energy
rebalance above — `docs/ROADMAP.md` explicitly flags Phase 7 (core unit/vehicle sprite and identity work) as
not yet started and as having "no natural stopping point" if scope isn't capped. The infantry/vehicle roster
(`mods/sungrid/rules/infantry.yaml`, `vehicles.yaml`) is almost entirely unmodified stock Red Alert content.
A follow-up pass split the candidates below into what's actually executable now (pure fluent renames, zero
art/mechanics/sub-faction risk) versus what's genuinely blocked pending bigger decisions:

**Done — data-only fluent renames, no mechanical or art changes:**

- **`V2RL`** "V2 Rocket Launcher" (a literal WWII rocket designation) → **"Surge Rocket Launcher"**.
- **`QTNK`** "MAD Tank" (Cold War nuclear-doctrine acronym) → **"Tremor Tank"**, matching its existing seismic
  mechanic.
- **`U2`** "Spy Plane" (a real Cold War reconnaissance aircraft) → **"Recon Plane"**, matching the mod's
  existing recon vocabulary (Sensor Array, Recon Drone).

All three were confirmed faction-general (no `~vehicles.<sub-faction>` gate) before touching them, and the
entire change was confined to `mods/sungrid/fluent/rules.ftl`/`chrome.ftl` — no actor id, weapon, or sprite
changed.

**Resolved — all five real-world-coded sub-factions renamed (see `docs/BACKLOG.md` issues #54/#55):**

The category this section originally deferred ("touches sub-faction identity, needs its own decision first")
is now closed. `DTRK`'s Ukraine sub-faction was renamed to the real country Iran on direct request (issue
#54); the four remaining real-world-coded sub-factions (England, France, Germany, Russia) were then renamed
on direct request (issue #55) — England, France, and Germany to fictional in-universe identities matching the
same "drop real-world national coding" direction the Allies→Consortium/Soviet→Assembly rename already
established for the two umbrella sides, Russia to another real country instead: England → **The Ledger** (since renamed again to **Greece** on direct request, keeping the stock Greek flag art)
(counterintelligence), France → **The Mirage** (deception; since renamed again to **USA** on direct request), Germany → **The Epoch** (chronoshift; since renamed back to **Germany** on direct request, keeping the stock flag it always flew), Russia →
**China** (Tesla weapons). `TTNK`/`CTNK`/`STNK`/`MGG`/`SPY.England`
all keep their existing chassis/weapon/mechanic unchanged — country-label swaps and fictional renames only,
not new unit designs. Internal ids (`~vehicles.england`, `Faction@russia`'s `InternalName: russia`, etc.) are
untouched everywhere, same pattern as every prior faction-identity rename in this project.

**Blocked — needs a real art/audio pipeline, not just YAML/fluent edits:**

- **`E1`/`E2`/`E3` core infantry** and **`1TNK`–`4TNK` generic tank line** — the biggest-volume, highest-
  visibility content, and genuinely need new sprite art or faction-differentiated silhouettes, not name swaps.
  `docs/ART_DIRECTION.md`'s asset-pipeline note requires sprite resolution/frame conventions/a shared palette
  file to be locked before art work starts; nothing equivalent exists yet for units (only building art has had
  even a first pass, and that's flagged as needing a real artist too). No image-generation tooling is
  available in this environment that could produce game-ready indexed-palette sprite sheets matching OpenRA's
  frame/facing conventions, so this genuinely can't be done as a text-editing pass — it needs a `type:design`
  RFC (per `docs/CONTRIBUTING.md`) to settle the pipeline question first.
- The announcer voice set and in-game ambient music pass from Phase 7's roadmap deliverables — same blocker,
  needs real audio assets.

These are proposals for scoping a future phase, not commitments — expect this list to change once Phase 6's
visual identity work (terrain, chrome, cursors) is fully wrapped and Phase 7 actually starts.
