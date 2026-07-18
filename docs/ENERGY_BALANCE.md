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
| `SGDAI` Datacenter for AI | Power -60, no power-state interaction | **Power -140**, full `GrantConditionOnPowerState` gating | Was the weakest link — a hard prerequisite for both drone units that didn't care about grid health. Now matches `SGCRY`'s order of magnitude and genuinely degrades: `CashTrickler` drops 20→8/tick under strain, `DetectCloaked` cuts out entirely below Normal power. |
| `SGDRO`/`SGDRS` (Recon/Strike Drone) | No power interaction on the unit itself | `GrantConditionOnPowerState` gates each drone's own `Armament` | Drones lose their weapons fleet-wide — not just those near a Drone Bay — once their owner's grid drops to Critical power. Verified feasible via this repo's own pre-SDK-migration git history: `GrantConditionOnPowerState` only depends on `Owner.PlayerActor.Trait<PowerManager>()`, no Building requirement, so it works on aircraft the same as on structures. |

## New faction power buildings

Both are **additive** alternatives to `POWR`/`APWR` (which stay available to both sides as the safe baseline)
— not replacements — so no side loses power access, and each is a real tradeoff rather than a strict upgrade,
keeping power a constant spend-vs-save decision (`docs/VISION.md` #3) rather than a one-time solved problem.

### Wind Turbine Array (`SGWND`) — Assembly

Cheap (250 — retuned from the original 400 after the `docs/BUILDINGS.md` roster survey found it strictly dominated by Solar Array at that price), early (`~techlevel.low`, a tier before Advanced Solar Array), individually fragile (30000 HP —
the lowest of any power building). Rewards spreading turbines out across a base rather than turtling one big
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
- `GAP` (Consortium Gap Generator) drains -60/800 vs Assembly's closest analog, `SAM` (-40/700).

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
