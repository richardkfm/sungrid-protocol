# Changelog

All notable changes to Sungrid Protocol are logged here, grouped by phase and theme rather than by
commit. Written in plain language for playtesters, not raw commit messages. Issue numbers in
parentheses refer to `docs/BACKLOG.md`, which holds the full engineering detail for each item
(GitHub Issues is disabled on this repo, so the backlog file is the issue tracker).

Pre-built packages for each tagged version are on the
[Releases](https://github.com/richardkfm/sungrid-protocol/releases) page. Latest release: **alpha26**.

## Where the project stands

Playable end-to-end: real Red Alert-derived gameplay, the full solarpunk building roster, the Grid
Reserve economic victory mode (on by default), original UI chrome, cursors, menu music, faction
badges, reskinned terrain palettes, and original in-world art for every Sungrid-specific building
and unit. Still stock: the core inherited RA unit/vehicle sprites, all voice and sound effects, and
in-game music beyond the menu sting — that's Phase 7, not started. See `docs/ROADMAP.md` for the
phase plan and `CLAUDE.md` for detailed current status.

## Phase 1 — Baseline playable shell

- Replaced the OpenRA Mod SDK's placeholder example content in `mods/sungrid` with real gameplay forked from `mods/ra` (pinned engine commit `bf4102a`): the full Red Alert ruleset (structures, vehicles, infantry, aircraft, ships, weapons, AI), classic sprite/audio formats, and 75 real maps (a main-menu shellmap plus 74 multiplayer/skirmish maps).
- The mod still identifies itself as "Sungrid Protocol" in the title bar and OpenRA mod chooser; only the gameplay data underneath is (for now) unmodified Red Alert content, running under the `sungrid` mod id instead of `ra`.
- No new buildings, mechanics, or art — this phase is plumbing, not content. Solarpunk reskinning starts in Phase 2.

## Phase 2 — First solarpunk content layer

- Added the first solarpunk economy buildings: **Solar Array** and **Advanced Solar Array** (power), and the **Battery Bank** (storage), plus first-pass renames of the core economy buildings to fit the fiction (issue #4).
- Added the **Recycling Depot** (issue #5). It shipped here as a reflavored cash-trickler; its real salvage mechanic — a separate `Scrap` resource, the **Hauler Drone** (`SGHAU`) that collects it, and the Depot's refinery/dock rework — landed later as a dedicated design pass.

## Phase 3 — Grid Reserve economic victory mode

- Implemented the **Grid Reserve** mode: Vaults (Battery Banks) bank Credits into a per-player Reserve, reaching the map's Reserve target starts a 90-second **Grid Lockdown**, and holding it wins the match without destroying anyone (issues #6, #7). Destruction victory is untouched and always available.
- Added the HUD side of the mode: per-player Reserve bars, the Lockdown state, and a minimap beacon that reveals a player once they pass 50% of target (issue #8).
- Deposits are irreversible: destroying a Vault drains half its holdings from the owner's Reserve and pays a quarter of them to the attacker; selling a Vault forfeits its holdings entirely, so you can't launder Reserve back into cash.
- **Fixed:** Vaults drained Credits into Reserve in every match, whether or not the lobby checkbox was on — only the HUD/win-condition side actually read the toggle (issue #37).
- **Grid Reserve is now on by default** in the lobby, with destruction victory fully intact regardless (issue #39). A one-time, non-blocking in-match popup explains the core rules at match start so nobody is dropped into the mode with no explanation.
- **Fixed:** the Lockdown countdown was announced once and then invisible for the rest of the 90-second hold. The Reserve bar now shows a live `GRID LOCKDOWN — Ns` countdown for the duration, reverting on win or cancel (issue #76).

### Grid Reserve balance

- **Vaults no longer bankrupt their owner.** Deposits used to take every Credit the instant it arrived, so anyone with a Vault still filling literally could not spend — "save only," not spend-vs-save. Vaults now bank only the surplus above a 3000-Credit spendable floor (`MinimumOperatingBalance`), and the deposit rate was cut from 30 Credits/tick (~750/sec per Vault) to 10 (issue #68).
- **Vaults no longer bank past the target.** Spare Vault capacity is meant to be raid redundancy, not a buffer — banking past target made a Lockdown effectively unbreakable, since kills came off the surplus instead of off the target. A new ceiling caps the owner's *total* Reserve at 100% of target, re-checked every tick, so a successful raid re-opens banking and the leader has to earn the Lockdown back (issue #69).
- **Banking slowed further so raiding is real counterplay** (issue #75). At the previous rate a single Vault capped in ~32 seconds and several fill in parallel, so a Grid Reserve win could land ~15 minutes in with no fighting at all. The rate is now 3 Credits/tick (~75/sec per Vault, ~107 seconds to fill one), which leaves an attentive opponent several real-time minutes between the beacon reveal and Lockdown to scout, redirect, and break the countdown.

### AI opponents

- **Bots can play Grid Reserve at all** (issue #67). Nothing in the bot stack knew the mode existed, so bots only ever built one or two Vaults by accident and every AI match quietly collapsed back to destruction victory. A new bot module sizes the Vault count off the actual Reserve target, banks harder when an opponent passes the reveal threshold, and stops buying Vaults when an opponent is already holding Lockdown. All four stock personalities get it; bots are unchanged when the mode is off.
- Added a fifth lobby personality, **Grid Broker AI** — the same Normal AI in the ground war, but it over-builds Vault capacity and never concedes an opponent's Lockdown.
- Added a sixth, **Easy Grid Broker AI**, as a genuine beginner opponent (issue #69): its own smaller base builder, hard unit caps, a flat 25-unit attack force with a rebuilding gap, half the opening harvesters, no expansion, no support powers, and a Reserve economy that banks late.
- **Easy Grid Broker AI's ground war eased further** (issue #82). Its single-base design was never the problem — it doesn't expand, as intended — but its first attack wave arrived at full strength before a new player had even finished their first War Factory. Its own War Factory is now delayed like its other buildings, its attack force shrank from a flat 25 units to 16 with a longer rebuilding gap between pushes, and its total army cap dropped from ~43 to ~30 units so a single push is no longer most of its standing force.
- **Fixed:** a Consortium-side Easy Grid Broker AI had no anti-air structure at all — its `DefenseTypes` list had `sam` (the Assembly-only anti-air site) but not `agun` (its Consortium equivalent), so it could never build any defense against enemy aircraft or drones. Every other personality already listed both (issue #83).
- **Swapped which side builds `AA Gun` vs `SAM Site`** (issue #84): `AA Gun` (`AGUN`) now requires the Assembly tech tree and `SAM Site` (`SAM`) now requires Consortium's, reversed from stock RA's original pairing — the heavier flak cannon reads as Assembly, the guided missile as Consortium. Cost, HP, and weapon are unchanged on both; only which faction can build which moved.
- **Easy Grid Broker AI eased further still** (issue #85): its War Factory delay grew (3000→5000 ticks) and its first Battery Bank now starts banking Credits even later (`StartDelayTicks` 15000→18000), on top of issue #82's earlier ground-war ease.
- **Fixed:** Grid Reserve bots banked themselves into paralysis — pinned at zero cash, they built no defenses and no army for the whole match (issue #68). Bots now build a base and an army before banking at all, and add the next Vault only when the standing ones are ~80% full.
- **Fixed:** the Grid Lockdown countdown never showed on the observer scoreboard, only on the local player's own HUD bar (issue #92) — an observer, or a player who dropped to spectating, had no on-screen way to see the one timer that decides the match. Both widgets now show the same "GRID LOCKDOWN — Ns" countdown.
- **Grid Reserve targets raised — AI opponents were reaching Lockdown too soon** (issue #93): `BaseTargetPerPlayer` raised from 15000 to 20000 (+33%), the single constant every player's and bot's Reserve target is computed from.
- **Easy Grid Broker AI can now expand, just later than everyone else** (issue #94): it was permanently single-base since issue #69; it can now build one additional Construction Yard, but only once it is sitting on real spare cash (`BuildAdditionalMCVCashAmount` 12000, well above the engine default every other personality uses), so the second base still lands well after its already-delayed opening build.
- **Fixed:** an actively-playing local player had no on-screen sign that an *opponent* was holding Grid Lockdown, only their own countdown or the observer scoreboard (issue #95) — the one-time start broadcast was the only signal, easy to miss mid-fight. The HUD now warns "ENEMY LOCKDOWN — Ns" when someone else is in the hold.
- **Easy Grid Broker AI eased again — its second base and War Factory were still too fast** (issue #96): War Factory delay raised 5000→7000 ticks, and the second-base cash threshold from issue #94 raised 12000→25000.

## Phase 4 — Balance, CI, and release packaging

- **Energy economy rebalance and faction power identity** (issue #26): the Advanced Solar Array is a real tradeoff rather than a strict upgrade, the Cryptominer and Datacenter for AI now genuinely interact with power state (reduced output when the grid is strained instead of silently zeroing), and each side got its own power line — **Wind Turbine Array** and **Hydrogen Plant**. The neutral Bio-Research Lab's `Zombie`/`Ant` B-movie units were replaced with tone-appropriate content.
- Gave the Datacenter for AI and Drone Bay real tech-tree and logistics identity instead of being cosmetic (issue #22), made the Recon Drone an actual flying unit rather than a wheeled vehicle (issue #23), and armed both drones with faction-specific, balanced loadouts (issue #24).
- **Fixed:** the Grid Defense Turret shared the standard Turret's weapon, and the Hind was disabled dead content (issue #32).
- **CI turned out never to have run.** A docs PR that happened to touch non-markdown files triggered the first real CI run in the repo's history and immediately found 4 latent analyzer errors in the Grid Reserve code plus 45 rules/map validation errors — dangling references to the removed Flame Infantry and wrong prerequisites on two Phase 5 buildings — all fixed in the same pass (issue #19).
- **Re-pinned the engine** to a commit fixing a compile-time ambiguity that broke builds under some .NET 8 SDK patch versions, verified on real CI runs on Linux and Windows (issue #20).
- **Windows installers fixed** — twice. First a missing multiarch dependency broke version-stamping (issue #21), then the real underlying cause turned out to be the version string itself (issue #23), confirmed on a real release tag.
- **macOS builds fixed** — also twice. Every release through alpha8 shipped without a macOS package because the job was pinned to a runner image GitHub retired, so it queued forever and was auto-cancelled after 24h (issue #29). Once it could actually run, it failed on packaging steps referencing engine files the pinned engine doesn't have (issue #30).
- **alpha17 is the first release in the repo's history where all three platform jobs — Linux AppImages, Windows installers, and the macOS disk image — succeeded in the same run.**

## Phase 5 — Expanded roster

- Added the remaining building roster: **Cryptominer, Datacenter for AI, Drone Bay, Grid Defense Turret, Smart Grid Relay, Resilience Shelter, Sensor Array** (issue #11).
- First custom art pass on the Solar Array — the mod's namesake building, until then still the unmodified stock RA power plant (issue #12).
- **Fixed by the first real local playtest** (things CI could never catch): an invalid attribute, an actor-id collision that broke rules loading, a nonexistent server-trait class, and a missing sprite icon sequence.
- **Fixed:** the Hauler Drone's harvest sequence crashed the game on load (issue #35).

## Phase 6 — World & UI visual identity

- **Original UI chrome** (issue #41, superseding the earlier recolor pass in #13): the dialog frame, sidebar, loading screens, and mod icons are generated from scratch in the locked palette with zero stock-derived pixels, around a redesigned sun-over-horizon-in-hex emblem, with Consortium-gold and Assembly-green faction accents. Existing widget geometry is unchanged.
- **Terrain reskin for all three tilesets** (issue #18) — temperate, snow, and desert now use mod-owned palettes shifting the dominant tan/dirt band toward the project's green while preserving ore glints, water, and rock/road grays. Desert needed a brightness cutoff so bright dune sand stays sand.
- **Original cursors** (issue #49), replacing the earlier palette-tint-only pass.
- **Main menu cleanup** (issue #49): the mod now owns its menu layout, dropping the stock "Battlefield News" feed (which pulls upstream OpenRA release announcements) and the OpenRA forum-account prompt.
- **Original main-menu music** (issue #49) — a synthesized ambient loop replacing stock RA's intro track.
- **Faction badges and logos.** The radar placeholder rendered the same gold badge for both sides despite per-faction plumbing already existing (issue #51); then each faction got a genuinely distinct mark rather than a recolor — the Consortium's **Citadel Seal** (fortress hex, spokes converging on a vault core) and the Assembly's **Swarm Rig** (three uneven nodes in a peer mesh, no hub), grounded in the centralized-vs-decentralized axis in the design docs (issue #52). Those marks then replaced the stock Allied eagle and Soviet hammer-and-sickle still showing in the lobby faction picker (issue #56).
- **Sidebar polish:** removed a decorative rectangle baked into the money-bin art that rendered as a stray gold box next to the live cash readout (issue #50), and softened the hard-edged panel borders that made existing stock RA panel-width differences read as a glitch (issues #51, #53).
- **Build-menu cameos.** Sungrid-original cameos got baked-in name labels to match the ported stock ones (issue #44), were replaced with photographic "real-style" crops from concept renders (issue #45), had their labels harmonized to single-line white to match the stock cameos beside them (issue #46), and picked up the Recycling Depot cameo the pass had missed (issue #47).
- **Fixed:** the chrome redesign initially emptied the build menu — an opaque overlay hid every production icon (issue #42) — and cameos were variously hidden, crowded, or shifted up by leftover fixes and a world-sprite offset leaking into the icon sequence (issues #61, #62, #63).

## Phase 7 — Unit & audio identity (first wave only)

- Renamed three faction-general units away from 90s C&C vocabulary: V2 Rocket Launcher → **Surge Rocket Launcher**, MAD Tank → **Tremor Tank**, Spy Plane → **Recon Plane** (issue #27). Deliberately capped as a first wave; sub-faction special units were left alone as a larger creative decision.
- The rest of Phase 7 — core unit/vehicle sprites, voices, announcer, in-game music — is **not started**.

## Art passes over the Sungrid-original roster

- **First dedicated art** for every Sungrid-original building and unit that had been reusing an unrelated actor's sprite (issue #34), fixing a real silhouette collision where two buildings rendered identically to the SAM Site. The Hauler Drone initially kept the Ore Truck chassis and then got its own, once it was clear an unarmed drone indistinguishable from an idle Ore Truck reads as a bug.
- **Quality pass over the whole programmatic set** (issue #40): supersampled rendering, consistent key lighting, readability outlines, and genuinely distinct damaged frames (the first pass had every building's damaged frame pixel-identical to its idle one).
- **Team colors** (issue #43): the roster switched from truecolor to indexed sprites on the stock RA player palette, so the gold "grid-live" accent now recolors to each player's team color like the ported stock buildings, instead of a fixed gold that ignored ownership.
- **Arc Turret and Disruptor Trooper** stopped looking like the Flame Tower and Flame Infantry they replaced (issue #36) — the earlier rename kept the original chassis art on a call that turned out to be the same identity mistake.
- **Volumetric in-world sprites**, three batches, covering the whole roster (issues #48, #58, #73): flat front-elevation shapes replaced with genuine volume at the game's overhead camera angle.
- **Rebuilt as real pixel art, not rotated drawings** (issues #64, #65, #66): the Disruptor Trooper's eight facings had been one side-view image spun around, so the trooper appeared lying on his side in seven of eight directions, and he stood half again as tall as every stock infantryman with his boots clipped off the frame. The Grid Defense Turret had the same construction bug — the whole drum and its shading rotated with the barrel, so the mount visibly orbited while tracking. Both were rebuilt as genuine per-facing views with real ground shadows. The Arc Turret's emitter head was then split into its own rotating turret sprite, so the Arc Turret visibly points at what it is shooting (issue #66).
- **Sprites that described the wrong mechanic** (issues #70, #71): the Grid Reserve Vault still rendered stock RA's rusty ore silo filling with ore — for the building whose entire job is banking Credits as grid capacity — and is now a containerized battery energy storage system with a readable charge level. The Recycling Depot still rendered an oil pumpjack, and the Smart Grid Relay depicted a cluster-pooling mechanic that was explicitly descoped and never shipped; both were redrawn.
- **Build-ups, rubble, and husks** (issue #74): almost no Sungrid building had a construction animation (they popped in fully formed) or its own death rubble, and the Hauler Drone died into the Ore Truck wreck — undoing the point of giving it a chassis of its own. 21 new sprite sheets fixed all three.
- **Fixed:** a shadow helper was punching a transparent hole through the sprite it was drawn on, on every affected sheet (issue #72).
- **Scale and subject pass** (issue #80), from four playtest reads:
  - **Both drones are much smaller.** A Recon or Strike Drone used to be drawn bigger than the Hauler Drone and nearly twice the height of an infantryman — on screen it read as a gunship, not a scout you buy for 350 credits. Both are now about the size of a trooper, redrawn at that scale rather than shrunk.
  - **Drones no longer fly wearing two sets of rotors.** Each drone's sprite bakes its own four rotors *and* mounted a stock Red Alert helicopter rotor disc on top — by the end wider than the whole drone. The stock discs are gone; the cost is that drones no longer have a spinning-rotor animation in flight.
  - **The Hauler Drone is a scrap rover again.** It had drifted into a smooth grey pod with a green panel on the back (the "vacuum cleaner" read) and is redrawn as the six-wheeled salvage rover from the project's own concept render: ploughed prow, open bed, and a bed you can actually see the scrap piled in — full, half and empty now read from the load itself rather than from a level bar. Its wreck was redrawn to match.
  - **The Recycling Depot is an open bay, not a box.** It shared the Battery Bank's shape — a closed cabinet with a lit gauge on the front — so the two read as the same building. It is now a canopy on posts with the scrap heap piled underneath in the open and the shredder off to one end.
  - **The Aerial Fabrication Bay is a hangar, not a bunker.** The dark barrel vault with a black arched mouth read as a kiln; it is now a light steel space frame under a field of solar panels, open on all sides, with an airframe being built on the apron underneath.
- **Drone rotors turn again** (issue #81), and this time they are the drone's own rotors rather than a stock helicopter disc bolted on top: each drone sheet now carries four rotor-spin frames per facing, so the blades sweep while the airframe flies — and because the spin is part of the body sprite, it shows in the drone's ground shadow too. Drones have always had that shadow, inherited from the same trait every other aircraft uses; what shrank it was the size fix, not a missing shadow.

## Ongoing — tone, naming, and content fixes

- Replaced Flame Infantry (`E4`) and the Flame Tower (`FTUR`) with the **Disruptor Trooper** (`DISR`) and the **Arc Turret** (`ARCT`) — a tone call that immolation weapons don't fit the project (issue #14). Same cost, stats, and tech-tier slot; only the weapon changed, from fire to a grid-current disruptor with equivalent damage. Three later passes caught references the first sweep missed: a shellmap paratrooper table, an APC drop (issue #25), and a shellmap Lua script (issue #28).
- Renamed the two playable sides: **Allies → The Consortium**, **Soviet → The Assembly** (issue #15).
- Renamed the real-world-coded sub-factions and corrected their flags: Ukraine → **Iran** (issue #54); England, France, Germany, and Russia renamed (issue #55), then corrected on request to **Greece** (England's slot), **USA** (France's slot), and **China** (Russia's slot), each flying its real flag instead of inherited stock art (issue #57); Germany reverted to plain Germany (issue #59). "British Spy" became "Auditor." All of these are display-text and flag changes only — no rules, AI, or actor-id changes.
- First-boot menu/intro pass (issue #16): fixed a regression where the main-menu shellmap still placed the removed Flame Tower in six spots, replaced the window/taskbar/mod-chooser icon (a literal stock Soviet star and hammer-and-sickle) with the project emblem, and reworded two off-theme loading-screen tips.

## Building system — tech-tree and bot-support fix pass

An audit of the whole building roster (issue #77) started from one question: *why would I build a Drone
Bay if I can only build drones after building the AI Data Center?* The answer was that you wouldn't —
and the audit found eleven more problems of the same shape. Issue #78 fixes all of them.

- **Drone Bays are now where drones are built.** Both bays used to share the Helipad's production type,
  so Strike Drones actually rolled out of the Helipad and Recon Drones out of the Airfield — you could
  destroy a bay without interrupting a single drone. The bays now have their own production type and are
  the only structures that can build drones.
- **Drones no longer need the Datacenter for AI.** Bay and drone now sit at the same tech tier, gated on
  the bay alone: build a Drone Bay, get drones. Previously the bay unlocked a whole tier early, so in a
  Medium-tech lobby it could produce literally nothing while still opening an empty Aircraft tab. The
  Datacenter still gates the three superweapons, which is what it was given that job for.
- **Cryptominer, Datacenter for AI and Resilience Shelter now need a Tech Center**, as their descriptions
  have said since Phase 5. In particular the Cryptominer's ~1,350 credits/minute was reachable two cheap
  buildings from a Construction Yard with no military structure built at all.
- **The Sensor Array is now the detection building.** It used to cost 800 credits for +2 detection range
  over the Datacenter, which the same tech path already required. The Datacenter loses cloak detection,
  the Sensor Array becomes the only structure that spots cloaked units away from a base defense, and it
  drops to radar tier so it arrives when scouting actually matters.
- **The Smart Grid Relay counts as a power source.** It was the only power building that didn't, so a base
  kept alive entirely on Relays couldn't rebuild a Refinery, Barracks, Naval Yard, Depot — or another Relay.
- **The Smart Grid Relay's tooltip now says what it's for** (issue #79). At 400 credits for +60 power it
  reads as the worst deal in the roster with nothing to explain why — it's actually the one power source
  that survives a Spy blackout and doesn't lose output as it takes damage, and the description now says so.
- **Ore Trucks can no longer unload at a Recycling Depot.** A 600-credit Depot was a working substitute for
  the 1400-credit Refinery. Haulers deliver Scrap to Depots, Ore Trucks deliver Ore to Refineries.
- **Build menus read correctly.** The Grid Defense Turret moved out of the tail of the Defense tab (it sat
  *after* all three superweapons) into the turret block, and the Consortium's Aerial Fabrication Bay now
  occupies the same slot as the Assembly's Drone Bay, so the two faction tabs are exact mirrors.
- **The AI plays the Sungrid roster.** Until now no bot ever built a Wind Turbine Array, Hydrogen Plant,
  Smart Grid Relay, Recycling Depot, Cryptominer, Datacenter, Sensor Array, Resilience Shelter, Grid
  Defense Turret or either Drone Bay — every bot match silently played the stock Red Alert tech tree, and
  bot squads didn't even recognise a Grid Defense Turret as enemy defense. All five personalities now
  build, defend and target the roster, and build drones. **Side effect worth knowing:** because all three
  superweapons were given a Datacenter prerequisite and no bot built one, *no bot has been able to finish
  a superweapon* since that change. They can again. One knock-on caught and fixed in the same pass:
  bots that build Recycling Depots get the free Hauler Drone that comes with one, and the squad
  manager would have sent that unarmed hauler along on attacks — it's now excluded from attack
  squads the same way Ore Trucks are.

Not verified in a live client, per the standing blocker below. Two things specifically want a playtest:
whether medium-tier drones are priced right against the 1500-credit helicopters they now share a tier
with, and whether the new bot build fractions produce a sensible opening.

## Hauler Drone follow-up: art, wreck salvage, speed (issue #86)

Direct player feedback on the Hauler Drone, three separate fixes:

- **Sharper art.** The bed-rim team-color trim was two short corner nubs that a full load of scrap
  could visually swallow — now full-length rails down each flank, so ownership reads at a glance
  regardless of load state. Wheels and hull highlights got a touch more contrast against the busy
  scrap texture.
- **Destroyed units now leave collectible Scrap.** This is the "death-triggered wreck salvage" idea
  from the Recycling Depot's original design (issue #5), revisited now that it's a direct request —
  it needed genuinely new engine-level code, which is why it didn't ship the first time. Any ground
  unit (both factions, not just Sungrid-original ones) now drops a small amount of Scrap where it
  dies, which an idle Hauler Drone collects the same way it collects map-painted Scrap. A dropped
  pile decays after 150 seconds if nobody collects it, so a contested chokepoint can't slowly turn
  into a permanent farmable resource node — battlefield debris is a temporary bonus, not new economy.
- **Faster, so it survives harassment better.** Speed 72 → 100 — it was matched to the Ore Truck's
  speed despite having under half its HP and lighter armor. Still slower than dedicated raiders, so
  it's still a legitimate harassment target, just no longer an automatic loss the moment anything
  catches it.
- **Fixed a real crash (issue #87):** the very first time a unit died in an actual match, the game
  crashed with `Tileset 'TEMPERAT' lacks terrain type 'Scrap'`. The Scrap resource had referenced a
  terrain type that was never actually defined in any tileset — a gap that existed since Scrap was
  first added (issue #5) and stayed invisible only because no map ever had Scrap painted on it until
  now. All four tilesets now define it, matching how Ore and Gems have always worked.
- **Restored the Hauler Drone's build-menu cameo (issue #88).** The art regen above accidentally
  overwrote the nicer photographic cameo with the flatter placeholder icon the art generator falls
  back to — the photo cameo pass just needed to be re-run afterward. Back to the version players
  already knew, confirmed byte-identical to what shipped before this whole follow-up started.
- **Fixed dropped Scrap not getting collected (issue #89).** The Hauler Drone's automatic resource
  search was inherited from the Ore Truck's tuning, which searches close to the Recycling Depot —
  reasonable for Ore, which sits near a Refinery on purpose, but wrong for Scrap, which drops
  wherever a unit dies in combat, usually well away from base. Its search radius is now wide enough
  to reach a typical battlefield instead of just the Depot's doorstep. A second report from the same
  feedback — units continuing to fire on Scrap piles — is still being investigated; the resource
  itself and the wreck sitting on it were both checked and neither should be attackable, so this
  needs more detail from a live match before it can be fixed.
- **Found and fixed the drones-still-firing-on-wrecks bug (issue #90) — engine-level, not a rules
  change.** Turned out to be specifically the drones (Hover-type attackers): once they kill something,
  they kept closing in on and hovering over the empty spot where it died instead of disengaging,
  because the fallback position they fall back to when a target dies is always treated as "still
  there" by the engine's own target-validity check. That let them linger right on top of a fresh kill
  and keep finding other things to shoot at nearby, which is what looked like continued fire on the
  wreck itself. Fixed in the pinned engine build (`ENGINE_VERSION` bumped) — this is the mod's first
  engine-level patch since the original build-compatibility fix from issue #20.
- **Gave Scrap its own art (issue #91).** Player feedback: "a destroyed enemy tank turns into ore" —
  and it genuinely did, visually. Scrap's four resource-pile stages had been aliased straight to Ore's
  own sprite files since Scrap was first added, which had zero effect until Scrap started actually
  appearing on the battlefield. Scrap now renders as its own thing: a heap of salvaged plate metal,
  a pipe, and a gear, distinct from Ore's gold nuggets and Gems' purple crystals.

## Open / recorded but not implemented

- Consolidating the European sub-factions into a single EU faction, with a fictional Federation of the Middle East as the Assembly's counterpart, is recorded as a design question (issue #60) rather than implemented — unlike every rename so far, it would shrink the lobby's sub-faction list and force a decision about which special units each merged identity keeps.
- Drone cost skew and Cryptominer payback time are flagged for playtest with no numbers changed yet (issue #31).
- A live-client view of a running battlefield in a headless environment is still blocked (issues #18, #33, #49): a bot match runs to completion, but the battlefield renders black because the local player's shroud reports nothing explored. Root cause not found; the sprite and terrain work above is verified through the engine's own asset-validation tooling and composited renders instead.
