# CLAUDE.md — Navigation map for Sungrid Protocol

This repo follows the [OpenRAModSDK](https://github.com/OpenRA/OpenRAModSDK) pattern: the OpenRA engine is a pinned, fetched build dependency (`engine/`, gitignored, not committed), not vendored source. Read this first before exploring the tree.

## What this repo is

`richardkfm/sungrid-protocol` is a Mod SDK-style repo for Sungrid Protocol, a solarpunk reinterpretation of the classic Red Alert RTS formula, built on the OpenRA engine. It started as a direct fork of the full OpenRA engine repository, but that was superseded in Phase 0 (before any mod content existed) in favor of the standard SDK pattern — see `docs/ARCHITECTURE.md` for the full rationale.

## Directory map

**Fetched engine dependency — never commit, never edit directly:**
- `engine/` — downloaded/built by `fetch-engine.sh` (or `make`), pinned via `mod.config`'s `ENGINE_VERSION`. Contains `OpenRA.Game`, `OpenRA.Mods.Common`, stock mods (`mods/ra`, `mods/cnc`, `mods/d2k`, `mods/ts`), etc. Gitignored — if a friction point genuinely needs an engine-level change, it usually does **not** need a separate personal fork repo: this repo's own pre-Phase-0 history already contains the full engine tree, so a fix can be pinned via an `engine-patch/*` branch built on the currently-pinned commit — see "Engine version pinning" below before touching `ENGINE_VERSION` or any `engine-patch/*` branch. Only reach for an actual personal fork of `OpenRA/OpenRA` if the needed base commit genuinely isn't already reachable in this repo's own history (see `docs/ARCHITECTURE.md`).

**Mod/content territory — where Sungrid Protocol work actually happens:**
- `mods/sungrid/` — **the Sungrid Protocol mod content**: real Red Alert-derived gameplay (rules/YAML, sequences, 75 maps, chrome layouts, fluent strings) plus all Sungrid-original content on top of it. Art generators live beside their output: `bits/gen_concept_art.py` (in-world sprites, build-ups, rubble, husks, programmatic cameos), `bits/gen_photo_cameos.py` (the shipped photographic cameos), `bits/gen_cursor_art.py`, `bits/gen_intro_music.py`, `bits/reskin_terrain_palette.py`, `uibits/gen_chrome.py` (dialog/sidebar/loadscreens/mod icons/faction flags). Regenerating is always safe — output depends only on the script.
- `mods/sungrid-content/` — the content-installer mod. Sungrid Protocol reads Red Alert asset `.mix` files from `<SupportDir>/Content/ra/v2/`; this is the first-launch flow that fetches the official freeware package or extracts from a disc/Steam/Origin copy.
- `OpenRA.Mods.Sungrid/` — mod-specific C# project. `GridReserve/` holds the whole economic-victory mode (`GridReserveVault`, `GridReserveManager`, `GridReserveController`, `GridReserveBotModule`, and the HUD/briefing/standings logic); `Rendering/` still holds the SDK's two renamed example traits (`ColorPickerColorShift`, `PlayerColorShift`); `Economy/` holds `SpawnsResourceOnDeath` (issue #86 — drops a small amount of a resource at an actor's death cell for a Harvester-type unit to auto-collect) and `ResourceDecayManager` (issue #87 — a World-actor `ITick` trait that expires an uncollected drop after a delay, so battlefield wreckage stays temporary); both unverified, no engine build available in this environment to compile against.
- `mod.config`, `fetch-engine.sh`/`.cmd`, `Makefile`/`make.cmd`/`make.ps1`, `launch-game.*`, `launch-dedicated.*`, `utility.*`, `Sungrid.sln`, `packaging/` — SDK scaffolding, all mod-scale (not the engine's own build/packaging tooling).

**Design docs:**
- `docs/BLUEPRINT.md` — the Phase 0 planning snapshot: vision, technical strategy, roadmap, MVP definition, all in one place. Historical by now — the sibling docs below are the maintained versions.
- `docs/VISION.md` — design pillars, tone, what differentiates Sungrid Protocol from vanilla RA.
- `docs/ROADMAP.md` — phase-by-phase plan (0 through 8+) with deliverables, exit criteria, explicit non-goals, and per-phase status.
- `docs/ARCHITECTURE.md` — OpenRA technical strategy, data-driven vs. engine-level split, known friction points.
- `docs/GAME_MODES.md` — full spec for the Grid Reserve economic victory mode, including the shipped tuning constants and why each one is what it is. **Read this before touching anything in `OpenRA.Mods.Sungrid/GridReserve/`.**
- `docs/BUILDINGS.md` — the building roster (the original ten, plus the three from the energy pass), categorized and staged.
- `docs/ENERGY_BALANCE.md` — the energy-scarcity rebalance and faction power-identity pass, plus the sub-faction rename history.
- `docs/ART_DIRECTION.md` — solarpunk tone/visual guardrails and the locked palette. `docs/concept-art/` holds non-canonical HTML sketches (the Phase 5 building dossier, its faux-pixel-art follow-up, the faction-roster dossier) — discussion drafts, not shippable assets — plus per-issue PNG review renders of actual generator output referenced inline from `docs/ART_DIRECTION.md`, and `cameo-sources/` (author-supplied concept renders the photographic cameos are cropped from).
- `docs/PLAYTESTING.md` — build/launch/troubleshooting steps for actually running a local match, including the RA content install and the known headless-environment blockers.
- `docs/CONTRIBUTING.md` — Sungrid-specific workflow (branches, labels, RFCs, PR checklist). Root `CONTRIBUTING.md` is the Mod SDK's own contributing guidelines (still points to OpenRA's coding-standard wiki for engine-level style).
- `docs/LICENSE_NOTES.md` — GPLv3 inheritance, EA non-affiliation, original-asset licensing notes.
- `docs/BACKLOG.md` — **the issue tracker** (GitHub Issues is disabled on this repo). Full engineering detail per issue; everything below cites issue numbers from it. `CHANGELOG.md` is the playtester-facing summary of the same work.

## Project goals and principles (condensed from `docs/VISION.md`)

1. Classic RTS legibility first — theme never overrides silhouette/UI readability.
2. Solarpunk as a lens that changes gameplay (power management, recycling, grid defense), not just reskinned names.
3. Spend vs. save is a first-class strategic decision (this is what Grid Reserve is for).
4. Pressure never disappears — scouting, harassment, raiding, and map control stay relevant in every mode, including the economic one.
5. Data-driven before engine-driven — YAML/Lua first, new C# only when provably necessary.
6. Small, reversible phases — every phase ships something playable and can be rolled back cleanly.
7. Destruction victory stays intact — Grid Reserve is additive and optional, never a replacement.
8. 3+ players is the target for new social/economic mechanics — diplomacy and shared-resource systems are deliberately deferred until this is validated.

## Key architecture decisions already made

- **Mod SDK pattern, not a vendored engine fork** — the engine is fetched/pinned via `mod.config` + `fetch-engine.sh`, not committed to this repo. Superseded the original "full engine fork" decision before any mod content existed (see `docs/ARCHITECTURE.md` for the full reasoning).
- Data-driven-first: buildings/units/rules go through YAML composing existing OpenRA traits wherever possible; new C# traits (in `OpenRA.Mods.Sungrid/`) are reserved for things YAML genuinely can't express (currently: only the Grid Reserve vault/win-condition mechanic).
- Destruction victory is permanent and always available; Grid Reserve is an additive lobby option, **on by default** since issue #39 (the trait's own C# default is off — `mods/sungrid/rules/world.yaml` turns it on).
- "Grid Reserve" is the recommended/working name for the economic victory mode (see `docs/GAME_MODES.md` for the other 4 candidates that were considered).
- Diplomacy, alliance mechanics, and shared/pooled resources are explicitly out of scope until Phase 3-5 playtests justify them (see Phase 8+ in `docs/ROADMAP.md`).

## Current status

`docs/BACKLOG.md` is the issue tracker and holds the full detail for every issue number cited below;
`CHANGELOG.md` is the plain-language summary of the same work. This section is the orientation layer:
what is true now, and the hard-won rules that are expensive to rediscover.

### Phase status

| Phase | State |
|---|---|
| 0 Bootstrap, 1 Baseline shell, 2 First content layer, 3 Grid Reserve MVP, 5 Expanded roster | Complete, playable |
| 4 Balance / AI / CI / packaging | Substantially done (AI plays Grid Reserve, CI green, all three platforms package). Not done: structured external multiplayer playtests |
| 6 World & UI identity | Complete except terrain **scenery** (palette reskins done for all three tilesets; solar-farm fixtures / salvage piles / reclaiming greenery deliberately deferred) |
| 7 Unit & audio identity | Barely started — three unit renames only (issue #27). Core inherited unit sprites, voices, announcer, and in-game music are all still stock |
| 8+ Diplomacy / shared resources | Deferred by design |

Releases: `alpha1` … `alpha25`. `alpha17` was the first run in the repo's history where all three
platform jobs (Linux AppImage, Windows installer, macOS DMG) succeeded together — Windows was fixed
twice (issues #21, #23) and macOS twice (issues #29, #30).

### Grid Reserve (the mode this project exists for)

All of it lives in `OpenRA.Mods.Sungrid/GridReserve/`, wired from `rules/world.yaml` (controller +
lobby checkbox), `rules/player.yaml` (manager), `rules/structures.yaml` (`SILO` = the Battery Bank /
Vault), `rules/ai.yaml` (bot module) and `chrome/ingame-player.yaml` (HUD + briefing popup).
**`docs/GAME_MODES.md` is the spec and documents every constant with its reasoning — read it first.**

Shipped tuning: `Capacity` 8000/Vault, `DepositRate` 3 Credits/tick (~75/sec),
`MinimumOperatingBalance` 3000, `MaximumTargetPercent` 100, `BaseTargetPerPlayer` 15000,
`LockdownDurationTicks` 2250 (90s). On by default.

Four bugs worth remembering, because each one came from the same blind spot — the mode's pieces read
each other's state and it is easy to leave one of them out:

- **#37** — only the controller read the lobby toggle, so Vaults drained Credits in *every* match.
- **#68** — Vaults banked with no spendable floor, and every engine bot production path gates on
  spendable cash (`ProductionMinCashRequirement` 500, `NewProductionCashThreshold` 7000-8000), so
  bots were pinned at zero cash and built nothing all match. A human with Vaults filling was equally
  locked out; the AI just made it visible. Hence `MinimumOperatingBalance`.
- **#69** — nothing capped banking at the *target*, so surplus Vault capacity (meant as raid
  redundancy) became a banked buffer and a Lockdown could not be broken. Hence `MaximumTargetPercent`,
  re-read every tick rather than latched.
- **#75/#76** — banking was fast enough that the raid window Core Rule 4 depends on wasn't real
  (hence `DepositRate` 3), and the Lockdown countdown was broadcast once and then invisible for the
  whole 90-second hold (hence `GridReserveController.LockdownTicksRemaining`).

**Bots (issue #67).** `GridReserveBotModule` sizes Vault count off the real Target and queues them one
at a time so stock `BaseBuilderQueueManager` still does the placing. Six lobby personalities: the four
stock ones plus **Grid Broker AI** and **Easy Grid Broker AI**. Deliberately deferred: bots don't
preferentially raid enemy Vaults and Turtle AI doesn't drop turtling against an imminent economic win
— both need engine-level squad target-selection changes, so the module grants
`EnemyBankingCondition`/`EnemyLockdownCondition` as the mod-side hook for trying that later.
Gotcha for any future personality: `McvExpansionManagerBotModule` is what deploys the starting MCV, so
a personality with no instance of it never builds anything at all.

**Easy Grid Broker AI never opens a second base** — `MinimumConstructionYardCount: 1` /
`AdditionalConstructionYardCount: 0` is deliberate (issue #69). A player who reports it "expanding" is
seeing its pace, not a second Construction Yard: issue #82 found its War Factory was undelayed (so it
reached production parity with a human on the bot's usual no-hesitation clock) and its 25-unit attack
force was most of its ~43-unit army cap in one wave. Both eased (War Factory now delayed like its other
buildings; attack force 25→16 with a longer rebuilding gap; army cap ~43→~30) — ground-war tuning only,
separate from issue #75's banking-speed retune of the same personality. Both delays pushed out further
still by issue #85 (weap `BuildingDelays` 3000→5000; `GridReserveBotModule@easygridbroker`'s
`StartDelayTicks` 15000→18000) after feedback that the War Factory and first Battery Bank still arrived
too soon.

**Only `AGUN`/`SAM` can hit an airborne target — `ARCT`/`SGTUR` never can.** Both anti-air structures are
`^AutoTargetAir`; the other two defenses every personality builds are `^AutoTargetGround` and will not
engage a drone or aircraft regardless of tuning. Every `SquadManagerBotModule` already treats `sgdro`/
`sgdrs` as air units (`AirUnitsTypes`, `AircraftTargetType: AirborneActor`), so bots do actively hunt
drones — but only if they have an anti-air answer standing. Issue #83 found Easy Grid Broker's
`DefenseTypes` had `sam` but not `agun` (at the time, `sam` was Assembly-only and `agun` Consortium-only),
leaving one faction's Easy Grid Broker with zero anti-air structures — fixed by adding `agun` alongside
`sam`, same pattern every other personality already used. Easy Grid Broker still doesn't build the Drone
Bay or either drone itself (deliberate, per issue #78 — it stays ground-only to teach the mode).

**`AGUN` is Assembly's, `SAM` is Consortium's** — reversed from stock RA's original Allied-AAGun/
Soviet-SAM pairing (issue #84): the heavier industrial flak cannon (`ZSU-23`) reads as Assembly, the
guided missile (`Nike`) reads as Consortium. Only the `Prerequisites` faction flag on each actor changed
(`~structures.soviet`/`~structures.allies` in `mods/sungrid/rules/structures.yaml`) — everything else
(cost, HP, weapon, art) stays attached to the same actor id. `ai.yaml` needed no changes: every
personality's `DefenseTypes`/`BuildingFractions` already lists both `agun` and `sam`, since a bot only
ever builds the one its own faction's prerequisites allow.

**The roster the bots play on (issue #78).** Until this pass `ai.yaml` contained zero occurrences of any
Sungrid-original building, so #67 taught the AI the *mode* but not the *content*: every bot match
silently exercised the stock RA tech tree, and — because issue #22 gave all three superweapons an `sgdai`
prerequisite no bot could satisfy — no bot could finish a superweapon either. All five
`BaseBuilderBotModule` instances now carry the roster, with `sgwnd`/`sghyd`/`sgrel` in `PowerTypes`,
`sgtur` in `DefenseTypes`, the roster in `EnemyBaseBuildingTypes`/`ProtectionTypes`, and drones in
`AirUnitsTypes`/`UnitsToBuild`. Two rules that cost thought and are easy to get wrong again: `rcyd`
stays **out** of `RefineryTypes` (that list drives the ore-economy adequacy check and refinery-near-ore
placement — a Depot refines Scrap), and Easy Grid Broker deliberately gets only the low-tech subset,
which stays self-consistent because it never builds `atek`/`stek` and the tech buildings now need
`techcenter`. Same caveat as the Grid Reserve constants: the fractions are reasoned, not measured.

Not verified: that the tuning constants are *right*. They're reasoned from the engine's own cash gates
and config, not measured against observed income.

### Art pipeline — rules that cost real debugging to learn

Everything Sungrid-original is generated by committed Python scripts (see the directory map). Two
invariants hold across all of them: **frame sizes/counts/layouts never change**, so no sequence YAML
gets touched; and **re-running a generator must leave every other sprite byte-identical** — that diff
is the regression check.

1. **In-world sprites are indexed, on the stock RA player palette** (`mods/sungrid/bits/temperat.pal`,
   committed for the generators). OpenRA renders indexed PngSheets through the actor's `player`
   palette, so pixels on the remap ramp (indices 80-95) take the owner's team color; truecolor sprites
   ignore ownership entirely (issue #43). **Build-menu cameos are the deliberate exception** — they
   stay truecolor 64×48, because nothing about a cameo needs team color and the photographic ones
   (issue #45) would not survive palettization.
2. **Indexed alpha is 1-bit — translucency is silently deleted.** This has bitten repeatedly: swept
   rotor discs vanished leaving a body ringed by holes, discharge arcs and motion streaks disappeared,
   an alpha death-fade did nothing. Draw it opaque, or dither it.
3. **`contact_shadow()` must paint opaque.** At alpha 70 it didn't merely fail to draw — it *erased*
   the ground pad under it, punching a transparent lens through the sprite (issues #72, #73).
4. **`ShadowIndex` 4 is a stencil, and `indexed_strip()` only writes it where the body frame is
   transparent.** So a shadow projected onto the building's own pad is discarded. Rule: a sprite that
   fills its frame (buildings) gets a *painted* contact shadow; a sprite that doesn't (turret
   pedestals, husks, rubble) gets a real stencil shadow via `silhouette_shadow()`. Stock agrees —
   `fact.shp` bakes no cast shadow, `powrdead.shp` and `hhusk2.shp` do.
5. **The 4× LANCZOS downscale bleeds across pixel blocks**, so thin team-color accents land off the
   remap ramp. Accents are re-stamped at native resolution afterwards (`ACCENT_FRAMES`,
   `_vlt_accents`). Symptom to recognize: a gauge whose segments alternate team-colored and fixed gold.
6. **Facings must be genuine viewpoints, not one drawing rotated in the image plane.** This shipped
   twice — the Disruptor Trooper appeared lying on his side in seven of eight directions (issue #64),
   and the Grid Defense Turret's whole drum and shading orbited with the barrel (issue #65). Rotating
   a top-down drone body is fine; rotating anything with a fixed relationship to the ground is not.
   Turrets are now built on the `Mesh` axonometric renderer with the key light fixed in world space.
7. **Decode the stock art before drawing the replacement.** This is the established method and it has
   worked every time: `e6.shp` for infantry proportions (~15px tall, feet on the frame centre row),
   `heli.shp` for the frame-0-is-north / counter-clockwise facing convention, `sam2.shp` for what a
   32-facing turret keeps identical across facings, `silo2.shp` for fill-stage layout, `fcommake.shp`
   for build-ups, `powrdead.shp`/`hhusk.shp` for rubble and husks.
8. **Build-ups are derived, not hand-drawn** — RA's own are a squat version of the finished building
   growing to full height at constant footprint width, so `make_frames()` is a bottom-anchored
   vertical scale plus a grey construction tint. That keeps 15 build-ups in step with their draw
   functions instead of needing 15 more of them (issue #74).
9. **Two distinct failure modes, don't conflate them.** *Silhouette collision* — two actors rendering
   alike (issues #34, #36, #58, #64, #65). *Wrong mechanic* — perfectly legible art describing
   something the actor doesn't do: the Vault as an ore silo, the Recycling Depot as an oil pumpjack,
   the Smart Grid Relay depicting a descoped pooling mechanic (issues #70, #71). Both are real bugs.
   Issue #80 adds two more: *wrong scale* — a correct drawing at the wrong size (the drones read as
   gunships next to a 14px trooper) — and *wrong subject* — a well-drawn building that isn't this
   building (the Aerial Fab as a masonry vault). Neither is fixable by shading.
10. **Changing a sprite's size means re-choosing its marks, not scaling its coordinates.** Below about
    1px of stroke, detail either disappears into the 1-bit alpha or welds to its neighbour under the
    readability outline. `rotor_blur()`'s dashes-and-streak recipe reads at a 3-4px disc and turns into
    a direction-changing spike at 2px, which is why the shrunk drones use `_small_rotor()`'s opaque
    ring instead (issue #80). Same rule the other way for fine structure: the Aerial Fab's truss web is
    *filled triangles*, because 0.9px diagonals come back from the 4× downscale as a chain of loops.
11. **An actor with bespoke art shouldn't also wear a generic overlay for a part its own sprite draws.**
    Both drones baked four rotors *and* mounted stock RA helicopter rotor discs on top (issue #80);
    scale changes made it obvious, but it was wrong at any size. Check `WithIdleOverlay` against what
    the sheet already contains before regenerating a body.
12. **Decorative copies of a unit have to track that unit's size.** `SGDRN`/`SGDRA` park an airframe on
    their pad; when the flyable drones shrank, a bigger parked model would have read as a different,
    larger aircraft (issue #80).
13. **If the facings were made by image-plane rotation, moving parts belong in the body sheet, not in a
    `WithIdleOverlay`.** An overlay is placed by a `WVec` run through `BodyOrientation.LocalToWorld`,
    which with the default `UseClassicPerspectiveFudge` shears y by sin(40°) — an ellipse where
    `rotated_frames()` made a circle, so a part pinned to a boom tip at north drifts ~2px off it by west
    on a 15px sprite. Baked-in animation is exact at every facing, and `WithShadow` clones the body
    renderable so it turns in the ground shadow for free (issue #81, `rotated_anim_frames()`).
14. **`Facings` x `Length` is the frame count, facing-major, and the engine will tell you.**
    `DefaultSpriteSequence` indexes `facingIndex * Length + frame % Length`, so the drones' 32 x 4 sheets
    hold 128 frames. `./utility.sh --check-missing-sprites` runs `SpriteCache.LoadReservations` and
    reports the out-of-range frames — the same error that crashed the shellmap in issue #35 — so an
    animated sheet's math is checkable here rather than by inspection. Verify with a negative control
    (bump `Length` by one, see it fail) before trusting a silent pass.

### What can and can't be verified in this environment

Verifiable with a real engine build (`make`, then `./utility.sh`): `--check-yaml` (exits 0 across all
maps), `--check-missing-sprites`, `--png-sheet-export` (proves the engine's own PNG reader parses a
sheet at its intended frame layout), `--resolved-rules`, `--resolved-sequences`. Use these — they have
caught real bugs that reading YAML did not.

**Not verifiable here: anything requiring a live client.** No RA game content is installed by default
(see `docs/PLAYTESTING.md` for the freeware install), and even with content plus the
`Launch.SkirmishBots` engine patch, a 4-player bot match runs to completion but the battlefield
renders fully black — `World.RenderPlayer` resolves correctly, but that player's `Shroud` reports
nothing explored. Root cause not found; scoped as an open blocker rather than a fifth open-ended
debugging pass. Every sprite pass since is verified via the utility commands above plus composited
sheet renders, and marked "not verified in a live client" — keep doing that rather than overclaiming.

CI is real and it catches things: a docs PR that happened to touch non-markdown files triggered the
first run in the repo's history and immediately found 4 analyzer errors and 45 rules/map validation
errors (issue #19). Local playtests catch a different class again — a crash on shellmap load from a
sequence that combined `Length` and `Facings` (issue #35), an actor-id collision, an invalid
`FluentReference`.

### Naming and tone conventions

The two sides are **The Consortium** (was Allies) and **The Assembly** (was Soviet). Sub-factions are
Greece, USA, Germany, China, Iran. Every rename in this project has been **fluent-text (and flag) only
— internal ids, prerequisites, AI weights and palette keys are never touched**; keep it that way. No
fire/immolation weapons (issue #14 replaced both, and four separate later passes caught leftover `e4`
references in a paratrooper table, an APC drop, a shellmap Lua script, and AI build orders — grep
widely, including `.lua`, when removing an actor).

### Known-open, deliberately not done

- **Animated sprite states, "batch 5"** (from issue #74's audit): no Sungrid-original building has an
  idle animation (`WithIdleOverlay` appears exactly once in `rules/structures.yaml`, on the ported
  stock `PROC`), so the Wind Turbine's blades don't turn and the Sensor Array's dish doesn't sweep;
  the `grid-normal`/`grid-strained` power-tier conditions on `SGCRY`/`SGDAI`/`SGTUR` and
  `drone-uplink`/`drone-uplink-degraded` on both drones change output with no visual cue; `ARCT` has
  no `WithMuzzleOverlay`, so the Arc Turret fires with no flash. Three items came off this list: in
  issue #80, the drones' doubled rotors (the stock overlays are gone) and `SGHAU`'s hex-sled fullness
  sheets (redrawn as the six-wheel scrap rover, cargo shown as the load itself); in issue #81, the
  drones' flight animation — both drone sheets are now `Facings: 32` x `Length: 4` and their rotors
  turn, which is also the worked example for how to animate anything else here. Still open on the
  drones: no separate slow-rotor state while landed (deliberate — a second 128-frame sheet and a pair
  of conditional sprite bodies for a state a 15px drone barely occupies).
- **Terrain scenery** — the Phase 6 item that isn't palette work.
- **Phase 7 proper** — unit sprites, voices, announcer, in-game music.
- **Issue #60** — consolidating European sub-factions into an EU faction (and Iran et al. into a
  fictional Federation of the Middle East) is recorded as a design question, not implemented: unlike
  every rename so far it is many-to-one, shrinking the lobby list and forcing a call on which special
  units survive.
- **Issue #31** — drone cost skew and Cryptominer payback, flagged for playtest, no numbers changed.
- A human-designer pass over all the programmatic art, and a composer pass over the menu sting.

## Working conventions

- Never edit or commit anything under `engine/` — it's fetched by `fetch-engine.sh` and gitignored. If a friction point genuinely needs an engine-level change, see "Engine version pinning" below (usually an `engine-patch/*` branch, not a personal fork).
- Prefer YAML/Lua trait composition in `mods/sungrid` over new C# traits in `OpenRA.Mods.Sungrid`; if a new trait seems necessary, check it against the "New C# traits" row in `docs/ARCHITECTURE.md` first.
- Keep commits/PRs scoped to one phase/issue at a time — see `docs/CONTRIBUTING.md` for the full PR checklist and label taxonomy.
- `main` is now the default/integration branch (previously `bleed`, inherited from the original OpenRA engine fork; `bleed` has since been deleted from the remote — its history lives on as `main`'s own ancestry, since `main` was built on top of it rather than starting fresh). Never push directly to `main`; always branch + PR.

## Engine version pinning: how `ENGINE_VERSION` actually works (read before touching `engine-patch/*` branches)

`mod.config`'s `ENGINE_VERSION` + `AUTOMATIC_ENGINE_SOURCE` do **not** point at a separate personal engine fork repo. They point at a specific commit SHA inside `richardkfm/sungrid-protocol`'s **own git history** — an ancestor of `main` predating the Phase 0 SDK migration (`e96d2ae`), from back when this repo still had the full vendored engine tree. `fetch-engine.sh` downloads that exact commit as a GitHub archive-by-SHA zip (`https://github.com/richardkfm/sungrid-protocol/archive/${ENGINE_VERSION}.zip`). See `docs/BACKLOG.md` issue #20 for the full history of why this exists (a `CS0121`/`CryptoUtil.SHA1Hash` overload ambiguity under some .NET 8 SDK patch versions, fixed with a one-line disambiguation plus a follow-up `IDE0301` suppression).

**`engine-patch/*` branches (e.g. `engine-patch/bf4102a-cryptoutil-fix`) exist only to keep one specific pinned engine commit reachable for that archive-by-SHA fetch. They are not mod-content branches.**

- **Never merge one into `main`.** Doing so would try to re-add the entire pre-SDK-migration vendored engine tree (`OpenRA.Game/`, `OpenRA.Mods.Common/`, etc.) that Phase 0 deliberately removed. GitHub will correctly report this as a conflicting/`dirty` merge — **that's expected, not a bug to fix or a conflict to resolve.**
- **Never delete one.** Deleting the branch risks GitHub garbage-collecting the commit it points at (no longer reachable from any ref), silently breaking `fetch-engine.sh`/CI for every future build pinned to that SHA.
- **This exact mistake has already happened twice**: once during issue #20's original implementation, and again as PR #33 ("Engine patch/bf4102a cryptoutil fix"), opened a second time against `main` and correctly showing `mergeable_state: dirty`. Investigation confirmed the fix it carried was already the pinned `ENGINE_VERSION` commit and already verified working — the PR was redundant, not a real conflict to resolve. **If you see a PR like this again: close it without merging, comment pointing at this section, and do not delete its source branch.**

**To ship a *new* engine-level fix in the future:** branch from the currently-pinned `ENGINE_VERSION` commit, add the fix, and push it as a new `engine-patch/<description>` branch — never opened as a PR against `main`. Then open a normal mod-content PR that only updates `mod.config`'s `ENGINE_VERSION`/`AUTOMATIC_ENGINE_SOURCE` to the new SHA; that `mod.config` change is the only part of this process that goes through normal review and merges into `main`.

**First fix shipped this way since issue #20 itself:** `engine-patch/461c7c7-flyattack-dead-target-pursuit` (issue #90) — `OpenRA.Mods.Common/Activities/Air/FlyAttack.cs`'s Hover-attack-type path didn't stop a drone from chasing/hovering over a killed target's last position, which read as the drone still firing on the wreck. Built on top of the `bf4102a-cryptoutil-fix` commit (so it carries that fix too), pinned via `ENGINE_VERSION`.
