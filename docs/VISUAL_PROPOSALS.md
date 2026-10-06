# Visual fixes and improvements — proposals

A prioritized list of visual work that is *not yet scheduled*: user interface and menus, units,
terrain and world, buildings and defences. It was written after a full survey of the shipped art
at alpha39 / beta01 (issue #118 in `docs/BACKLOG.md`, which also shipped the four cheapest items
below). Each proposal is a candidate; when one is picked up it gets a `docs/BACKLOG.md` issue number
and this file's entry is marked with it, the same way `docs/BUILDINGS.md` tracks its roster.

How to read an entry:

- **Now** — what ships today and why it reads wrong, with the file that proves it.
- **Proposal** — the concrete change, in this repo's own vocabulary (`gen_concept_art.py` meshes,
  `gen_chrome.py`, sequence YAML), so it can be started without re-deriving the survey.
- **Cost** — S (an hour or two, one generator or YAML pass), M (a session), L (several sessions,
  no natural stopping point: cap the scope before starting).
- **Kind** — *generator* (committed Python + YAML, byte-reproducible, the default and the only kind
  this repo ships unaided), *C#* (`OpenRA.Mods.Sungrid`), *map*, *artist* (needs a human designer
  or composer; listed so they can be briefed), *engine* (needs an `engine-patch/*` branch — see
  `CLAUDE.md`'s pinning section before starting one).
- **Verify** — what proves it without a live client (`./utility.sh --check-yaml`,
  `--check-missing-sprites`, composited sheet renders in `docs/concept-art/`), and what still needs
  a desktop client.

Priorities follow the owner's call for this pass: **first impression and beta polish first**, then a
**scoped start on units (Phase 7)**, then **terrain and world**; buildings and defences are listed last
because the roster has had eight consecutive passes (issues #106–#113) and is in the best shape of the
four areas. Everything here is subordinate to `docs/ART_DIRECTION.md`'s guardrails and the art-pipeline
rules in `CLAUDE.md` — nothing below asks for translucency in an indexed sheet, a rotated-in-plane
facing, or a sprite that describes a mechanic the actor doesn't have.

---

## Shipped with this survey (issue #118) and the first-impression pass (issue #119)

Issue #119 took A1, A2, A3, A5, A6, A7, A8 and A9 from section A below (each is marked
`[shipped, issue #119]`; the full engineering detail is in `docs/BACKLOG.md`). A4 (the glyph
atlas) shipped as issue #124, so section A is closed. Issue #120 took B2, B3, B4, B5, B6 and B8 from
section B (marked `[shipped, issue #120]`); B7 is capped at its first tier (MCV, HARV, E1), the
owner's call, and that tier shipped as issue #121 - the later tiers (the tanks, then the raiders)
stay open. Issue #122 took section C: C2, C3 and C4 are marked `[shipped, issue #122]`, C5 is
marked `[checked, issue #122]` with the half that needs game content still noted, and C6 was A7. Issue #125
took section D short of the stock buildings: D2 (narrowed to the defences), D3, D4 and D6; issue #126 took the
first building of D5, the Materials Refinery - the War Factory, the barracks and the Tesla Coil are still open.

- **U1 — The game's name on the load screen and main menu.** The `logo` slot (256×256, drawn centred
  on the load screen and top-right of the main menu) held the bare emblem; neither screen said
  "Sungrid Protocol" anywhere except a 14px Bold label inside the menu panel. `wordmark_badge()` in
  `gen_chrome.py` now stacks SUNGRID / PROTOCOL in the mod's own Title face under the emblem.
- **B1 — Fake Solar Arrays rendered stock RA power plants.** `FPWR`/`FAPW` drew `powr.shp`/`apwr.shp`,
  the only place those sprites still appeared, which both looked wrong and told a scout exactly which
  array was the decoy. They now render `sgpwr`/`sgapwr` with FAKE-stamped photographic cameos.
- **W1 — A laden Hauler Drone's wreck spilled Ore.** `SGHAU` inherited `HARV`'s `OreExplosion`; it only
  ever carries Scrap. `ScrapExplosion` now spills Scrap.
- **N1 — The Disruptor Trooper died in a napalm fireball.** Inherited from the flamethrower he replaced
  (issue #14): `FireWarheadsOnDeath: VisualExplode`, 50% chance. Removed — it was the last fire effect
  in the roster.

---

## A. First impression and beta polish

What a tester sees in the first five minutes, in the order they see it.

**A1. [shipped, issue #119] The content installer is the first screen on a clean machine, and it is stock OpenRA.**
Now: `mods/sungrid-content/mod.yaml` points `Chrome`, `Cursors`, `ChromeLayout` and `LoadScreen` at
`^EngineDir|mods/common-content` — stock grey chrome, stock cursor, the stock "OpenRA" load image — so
beta gate B6 (first-run install on a clean machine) opens on a screen that isn't ours.
Proposal: point the installer's `LoadScreen` images at `sungrid|uibits/loadscreen*.png` and its
`Chrome` at a copy of `sungrid|chrome.yaml`'s `dialog`/button regions (the layout file
`content.yaml` can stay stock — only the art references change), plus the Sungrid cursor sheets.
Cost: S. Kind: YAML. Verify: `--check-yaml` on the content mod; the installer dialog is the one screen
`docs/BACKLOG.md` issue #117 did capture under Xvfb, so the recipe for a screenshot exists.

**A2. [shipped, issue #119] Main menu layout is the stock 200×320 panel; the Title face is never used in-game.**
Now: `chrome/mainmenu.yaml` is stock RA's layout minus the news panel; the menu title label inside the
panel duplicates the wordmark now in the logo slot; `Font: Title` (ZoodRangmah) is defined in
`mod.chrome.yaml` but no Sungrid layout uses it.
Proposal: drop the duplicated `MAINMENU_LABEL_TITLE` text (or make it the section name, e.g. "MAIN
MENU" in `Title` at a small size), use `Title` for the lobby title, the map-chooser title and the Grid
Reserve briefing title, and move the tagline directly under the logo slot so logo, name and tagline
read as one block. Cost: S. Kind: YAML + fluent. Verify: `--check-yaml`; an Xvfb screenshot (recipe in
`docs/PLAYTESTING.md`) for the layout.

**A3. [shipped, issue #119] The shellmap behind the menu is a stock Red Alert battle.**
Now: `maps/desert-shellmap/` is Scott_NZ's RA desert shellmap; its Lua spawns 3TNK/4TNK/V2RL/MiGs and
the base is Tesla Coils, oil derricks and refineries. Apart from the three ported buildings, nothing on
the menu's moving background is Sungrid.
Proposal: a Sungrid shellmap on the same terrain: both factions' roster (arrays, turbines, Hydrogen
Plant, Battery Banks, Drone Bays), Haulers running Scrap to a Depot, drones on patrol, an Arc Turret
line being probed by Disruptor Troopers, the `CameraOvalMover` path over it. Keep the stock units out
of frame until B-series below replaces them. Cost: M. Kind: map + Lua. Verify: `--check-yaml` loads
the map; `--check-scripts`; a screenshot under Xvfb (the shellmap renders there, issue #33).

**A4. [shipped, issue #124] The glyph atlas is still stock RA pixel art.**
Now: `uibits/glyphs*.png` is the stock sheet except the two faction-flag plaques `gen_flags()` patches
in: production/order/stance icons in stock grey with stock-yellow highlights, red cash/power/clock
tooltip icons, the three Random "?" flags on stock blue/red/grey.
Proposal: extend `gen_flags()` into `gen_glyphs()`: remap the stock-yellow highlight rows to sun-gold
and the red alert icons to the locked amber, redraw the Random "?" plaques on the Consortium gold /
Assembly green plaque style the faction slots already use. Pixel rects unchanged. Cost: S. Kind:
generator. Verify: `chrome.yaml` regions untouched; diff the atlas (only the intended rows change).
Shipped: `gen_glyphs()` recolours the stock yellow to sun gold (alert row, selected stance, admin crowns) and
redraws the three Random plaques; the red cash / power / clock icons stay stock red, because
`docs/ART_DIRECTION.md` keeps the alert colour language unchanged from stock - the guardrail wins over this
proposal. Not seen live.

**A5. [shipped, issue #119] The Grid Reserve HUD and standings are plain black boxes with hard-coded colours.**
Now: `GRID_RESERVE_HUD` and `GRID_RESERVE_STANDINGS` sit on `ColorBlock 00000090`;
`GridReserveHudLogic.cs` colours text `Color.LimeGreen` / `OrangeRed` / `White`;
`GridReserveStandingsLogic.cs` likewise. This is the one piece of UI that is *ours* and it is the
least designed.
Proposal: give both a chrome panel (a new 3-slice `grid-reserve-panel` region in `dialog.png`: panel
blue-black, green frame, gold filament on the lit edge), a 16px Battery Bank glyph before the amount,
a progress bar whose fill is sun-gold and turns the locked-down state pulsing gold-on-black, and move
the colours to `metrics.yaml` constants (`GridReserveBankingColor`, `GridReserveLockdownColor`,
`GridReserveEnemyLockdownColor`) read via `ChromeMetrics.Get`. Cost: S–M. Kind: generator + YAML +
C#. Verify: `dotnet build -c Debug -warnaserror` on `OpenRA.Mods.Sungrid`; `--check-yaml`; the widget
is only seen live.

**A6. [shipped, issue #119] Loading tips and tooltips still tell Red Alert jokes.**
Now: `fluent/mod.ftl`'s `loadscreen-loading` keeps "Reticulating Splines", "Aging Empires",
"Constructing Pylons", "Splitting Atoms"; `fluent/chrome.ftl`'s command-bar tooltips name Chrono Tanks,
Demolition Trucks and MCVs; the observer headers say "Harvesters" and "Oil Derricks".
Proposal: a Sungrid tip list ("Balancing the Grid…", "Composting Scrap…", "Charging the Reserve…",
"Routing Surplus…", "Reclaiming Pavement…", "Calibrating Arrays…"), tooltips rewritten for the roster,
observer headers "Collectors" / "Depots". Cost: S. Kind: fluent. Verify: `--check-yaml` (it validates
`FluentReference`s).

**A7. [shipped, issue #119] Map chooser: 75 stock Red Alert titles and stock preview thumbnails.**
Now: map titles like "A Nuclear Winter" and "Chernobyl"; each `map.png` preview was rendered on the
stock tan palette, so the chooser shows the old world even though the game draws the green one.
Proposal: regenerate every preview from the reskinned terrain palettes — `Map.Save()` rewrites
`map.png` from `SavePreview()` unless the map sets `LockPreview`, and `./utility.sh --update-map` is the
path that saves a map without the editor (confirmed on the shellmap: its shipped preview is ~70% tan,
0% green) — and retitle the handful of maps whose
names are explicitly Cold-War (a fluent-only rename, keeping the map ids). Cost: S for previews, S for
titles. Kind: utility + fluent. Verify: `--check-yaml` across all 75 maps; diff the preview PNGs.

**A8. [shipped, issue #119] Lobby, settings and dialogs are stock layouts on Sungrid art.**
Now: every `chrome/*.yaml` except five is `common|chrome/*`; they already draw on the grid-glass
sheets, so they *look* consistent, but the lobby has no Sungrid header, the faction dropdown shows
real-world flags next to the two plaques, and `TextfieldColorHighlight` in `metrics.yaml` is the stock
maroon. Proposal: override `lobby.yaml` only to add a header strip (emblem + map name) and the Grid
Reserve checkbox's own icon; set the text-field highlight to living green. Cost: S. Kind: YAML. Low
priority — these screens already read as ours.

**A9. [shipped, issue #119] The emblem and wordmark are first-pass programmatic marks.**
`uibits/PLACEHOLDER_ART.md` says so. Proposal: a designer brief — the emblem's concept (sun over a
living horizon inside a grid cell) and the locked palette are settled; what a designer adds is
proportion, a drawn rather than stroked sun, and a wordmark cut for the ZoodRangmah face rather than
set in it. Cost: artist. Kind: artist. Everything in `gen_chrome.py` consumes the emblem through
`emblem()`, so a supplied PNG can be dropped in at one call site.

## B. Units — a scoped start on Phase 7

Phase 7 is the largest item in the roadmap and has no natural stopping point (`docs/ROADMAP.md`). These
are ordered by **screen time**: how many seconds of every match a tester spends looking at the thing.

**B2. [shipped, issue #120; withdrawn, issue #123] Build-menu cameos of renamed stock units still say the old name.**
Now: stock RA cameos bake the actor name into the pixels (issue #44). `V2RL` is "Surge Rocket
Launcher" but its cameo (`v2rlicon.shp`) reads V2 ROCKET; `QTNK` "Tremor Tank" reads MAD TANK; `PROC`
"Materials Refinery" reads ORE REFINERY; `TENT`/`BARR` "Consortium/Assembly Barracks", `ATEK`/`STEK`
"Consortium/Assembly Tech Center" read the Allied/Soviet names. The build menu is where a tester first
meets the renames, and the cameo contradicts the tooltip on every one of them.
Proposal: photographic cameos for the renamed actors via `gen_photo_cameos.py`'s existing recipe (crop
+ cover-fit + baked label), either from new crops of the three committed source scenes or from a fourth
source render the owner supplies; programmatic fallback (`make_icon_from_motif`) where no photo fits.
Cost: S per actor, ~7 actors. Kind: generator. Verify: `--check-missing-sprites`; the issue #107
contact-sheet script.
Shipped: `TENT`/`BARR`/`ATEK`/`STEK` are photo crops of the hero scene's crew modules and the Novaya
Zarya tower, labelled BARRACKS / TECH CENTER like the stock cameos (a player only sees their own
faction's); `V2RL`/`QTNK`/`PROC` are programmatic `Mesh` solids in `gen_unit_effects.py`, **tagged for
a designer or a fourth source render** - the scenes hold no rocket launcher, seismic tank or refinery.
Withdrawn (issue #123): the owner's rule is that a cameo changes only when its actor's in-world art does,
so all seven are back on their stock `.shp` cameos, old names included. This entry reopens with the
actor: when a renamed stock unit or building gets Sungrid art, its cameo comes with it.

**B3. [shipped, issue #120; withdrawn, issue #123] The Grid Defense Turret fires a 120mm tank shell with a tank's report.**
Now: `GridPulseCannon` inherits `^Cannon` (`120MM` shell sprite, `small_explosion`, `turret1.aud`);
its muzzle flash is stock `samfire.shp`. The station was rebuilt twice (issues #112/#113) and still
sounds and shoots like a Soviet turret.
Proposal: a `Bullet` with its own 3-frame `sgpulse.png` (a short gold-white bolt with a green core,
`effect` palette, opaque per art rule 2), a 2-frame muzzle bloom on the station (`sgturfire.png`,
replacing `samfire`), an electrical-scorch impact effect instead of `small_explosion`, and a report
synthesized by `gen_arc_sounds.py`'s method (issue #110's two reports are the reference). Cost: S–M.
Kind: generator + YAML. Verify: `--check-missing-sprites`; the sheet layout rule for effects is in
`CLAUDE.md` art rule 17.
Shipped as proposed, with a three-frame bloom rather than two and a short green contrail on the bolt;
`sgpulse.wav` / `sgpulsehit.wav` from `gen_arc_sounds.py`, the impact leaves a Scorch smudge.
Withdrawn (issue #123): the owner found the turret read better as a heavy anti-tank gun with the shell, the
fireball and the cannon report, so all of it is back to stock; the numbers never changed either way. The art
(`issue120-unit-effects.png`) stays in the review render for the record.

**B4. [shipped, issue #120] Drone rockets are the stock `DRAGON` missile with a stock smoke trail.**
Now: `DroneRocket`/`.Strike` in `weapons/missiles.yaml` use the stock missile sprite, `smokey` trail,
`med_explosion`, `missile6.aud`. Proposal: a slimmer `sgmissile.png` (8 facings, white body, green
fin band), a short blue-white exhaust via `TrailImage` on a 2-frame sheet, keep `med_explosion`.
Cost: S. Kind: generator + YAML. Shipped with 32 facings rather than 8 (the stock DRAGON's count;
`rotated_frames` makes the extra facings free).

**B5. [shipped, issue #120] `drone-uplink` / `drone-uplink-degraded` change the drones' output with no visual cue.**
Now: the conditions switch `Armament`s in `aircraft.yaml`; nothing on screen changes. The body sheets
are `rotated_frames()` output, so an overlay would drift across facings (`CLAUDE.md` art rule 13).
Proposal: a `WithDecoration` status pip (selection-independent, 5×5, green = uplinked, amber =
degraded) anchored `Top`, drawn from a new `sgpips.png`; decorations are screen-space and don't go
through `BodyOrientation`, so rule 13 doesn't bite. Cost: S. Kind: generator + YAML. Verify:
`--check-yaml`'s condition-wiring report (negative control: name an ungranted condition).
Shipped with a third, red `offline` pip for the state neither condition covers (power Critical, the
armament disabled) - that is the one a player most needs to see.

**B6. [shipped, issue #120] Shot-down drones fall as their intact sprite and burn.**
Now: `SGDRO.Husk`/`SGDRS.Husk` render the live sheets; `UnitExplodeHeli` is a napalm effect; `SGHAU`'s
husks carry `^Husk`'s `fire` overlay. Proposal: a 4-frame tumbling husk per drone (rotors stopped,
one arm bent — `rotated_frames` of a single damaged drawing is correct here because a falling airframe
*does* rotate in the image plane), a smoke-only fall effect, and a decision recorded in
`docs/ART_DIRECTION.md` on whether *wreckage* may burn in a mod with no fire weapons (the Hauler husk
and `BuildingExplode`'s `building_napalm` are the same question). Cost: S–M. Kind: generator + YAML +
a one-line design decision.
Shipped: the decision (owner's call) is **electrical wrecks don't burn, buildings may** - see
`docs/ART_DIRECTION.md`. The husks are 32-facing sheets of one damaged drawing rather than a 4-frame
tumble: `FallsToEarth` spins the facing on the way down, which is the tumble. The Hauler husk's `fire`
overlay is its own smoke plume now; `BuildingExplode` is untouched.

**B7. [tier 1 shipped, issue #121, rifleman withdrawn in #123; tiers 2–3 open] The core roster is still stock Red Alert sprites — the Phase 7 unit pass, scoped.**
Now: every buildable infantry, vehicle, aircraft and ship except the drones, the Hauler and the
Disruptor Trooper is a stock `.shp`. Proposal: do not start with "all units"; start with the three
actors on screen in every match of either faction, then the tanks, then stop and playtest:

1. **MCV, HARV, E1** — the MCV deploys into the Sungrid Construction Yard and is seen at minute zero
   of every game; HARV sits beside the Hauler and is the only stock-looking thing in a Sungrid
   economy; E1 is most of every army. Vehicles go through the `Mesh` renderer at 32 genuine yaws (the
   renderer already handles 32-facing turret heads, issue #113), on the diamond-plinth-free
   `_mesh_render` path the pedestals use; infantry uses the per-facing `PC` track from issue #64.
2. **1TNK–4TNK** — four hulls on one chassis vocabulary (wheel/track pod, hull, turret), varying size
   and turret only, so the set stays a family.
3. **JEEP, APC, ARTY/V2RL** — the harassment and siege units Pillar 4 depends on.

Each unit needs: 32 facings × (idle, optional move frames), a `WithSpriteTurret` sheet where the stock
one has a turret, a husk, and a cameo. Lock the sheet conventions on MCV first (decode `mcv.shp` for
frame order the way `heli.shp` was decoded for the drones) and write them into `CLAUDE.md` before
drawing the second unit. Cost: L (S–M per unit). Kind: generator, with an artist pass as the
alternative for the infantry. Verify: `--check-missing-sprites` with the negative control, composited
sheets, and the first live match with the new MCV.
Shipped (tier 1): `gen_core_units.py` renders the MCV and the Ore Truck as `Mesh` solids at 32 genuine
yaws (plus the Truck's harvest/dock/dock-loop frames and all three fullness images, and both units'
husks and cameos) and draws the rifleman on the Disruptor Trooper's native-pixel figure, on the stock
sheets' exact frame layouts so only Filenames changed. The conventions are in `CLAUDE.md` art rule 24.
Not seen live. Tier 2 (1TNK–4TNK) and tier 3 (JEEP, APC, ARTY/V2RL) are the next picks.
Issue #123: the rifleman went back to stock `e1.shp` at the owner's call after a live look (the drawing
stays in git history at the #121 commit); the MCV and the Ore Truck stay, and their cameos are now scene
renders (`scene_cameo`: sky, horizon, ground plane, cast shadow) instead of the flat panel.

**B8. [shipped, issue #120] Infantry death and crush effects.**
Now: `DISR` (and every stock soldier) use `electro.tem` for the electric death, `corpse1.tem` when
crushed, stock parachute. Fine for now; a Sungrid "discharge" death for units killed by arc weapons
(a 6-frame white-green flicker rather than the Tesla-blue skeleton) is the one worth doing once B3 and
B7 exist. Cost: S. Kind: generator.
Shipped: `sgdischarge.png`, 6 flicker frames played twice and 8 collapse-and-dissolve frames, in every
infantryman's `die6` (19 sequence blocks, the Disruptor Trooper's included); `die-crushed` stays stock.

## C. Terrain and world

**C2. [shipped, issue #122] Scrap has never been seen on a map by a player — check it reads as Scrap, not Ore.**
Now: `scrap01–04.png` ship (issue #91) and only the Hauler's death drop (issues #86/#97, and W1 above)
puts them on the ground. Proposal: a composited render of the four Scrap sequences on all three
reskinned terrain palettes next to the Ore and Gem sprites, and if the grey-rust piles vanish against
the green ground, a brighter lit edge and a green-accent cable on each pile. Also place a hand-painted
Scrap field on one map (issue #5 asked for this) so the resource exists before the first wreck. Cost: S.
Kind: generator + map. Verify: the composite; `--check-yaml` on the edited map.
Shipped: the composite (`docs/concept-art/issue122-terrain-and-world.png`) showed tiers 1-2 as one grey plate that
vanished on the temperate ground and tiers 3-4 as a near-black gear; the four tiers are now a growing scatter of
lit-edged plates over the whole tile with a green cable on every tier, and the shellmap carries a 34-cell Scrap field
beside its eastern Recycling Depot, so the Haulers on the menu background have something to collect before the
first wreck.

**C3. [shipped, issue #122] Terrain scenery — the Phase 6 remainder.**
Now: the three tilesets are palette-reskinned (issue #18) and nothing else in the world is Sungrid:
trees, rocks and the civilian villages are stock. Proposal: six neutral decoration actors drawn with
the roster's `Mesh` vocabulary on the terrain palette — a ground-mounted panel row, a salvage pile
(crushable, with `SpawnsResourceOnDeath` dropping Scrap: scenery that feeds the economy), a vine-grown
pylon stump, a rain tank, a bus-shelter bike rack, a rewilded planter — registered in
`rules/civilian.yaml`, then placed by hand on the three maps testers will actually play (the shellmap,
and two 3–4-player maps), not scripted across all 75. Cost: M. Kind: generator + map. Verify:
`--check-yaml` on the three maps; a composite on each tileset.
Shipped: `SGPAN` Ground Array, `SGSLV` Salvage Pile (crushable, drops Scrap), `SGPYL` Pylon Stump, `SGTNK` Rain
Tank, `SGRAK` Bike Shelter, `SGPLN` Planter, all 1x1 in `rules/decoration.yaml` on `^Box`'s template, drawn by
`bits/gen_world_scenery.py`; 14 on the shellmap, 18 on Crossfire, 12 on Doubles. Only the pile feeds the economy
(the owner's call).

**C4. [shipped, issue #122] Civilian and tech structures are stock and still read as Cold War.**
Now: `OILB` oil derricks (eight on the shellmap), `HOSP`, `BIO` ("Containment Ruins"), `MISS`, the
`V01–V37` village houses. Proposal: treat the derricks as deliberate "old world tech" under
`docs/ART_DIRECTION.md`'s rust guardrail (rename "Legacy Derrick", rust palette shift only), and
rebuild only the two tech buildings that grant something — `HOSP` as a Field Clinic, `BIO` as a
Seed Vault — as `Mesh` solids. Cost: M. Kind: generator + fluent.
Shipped: the Legacy Derrick keeps `oilb.shp` and renders through `PlayerColorPalette@LEGACY`, a rust-shifted copy
of the player palette (`bits/sungrid-legacy.pal`); the Field Clinic and the Seed Vault are solids on the stock
frame layouts, so their sequences changed by Filename only. The village houses stay stock.
Issue #123 dropped the derrick's palette again: in a live temperate match it read as the desert derrick, not
as old iron. The Legacy Derrick keeps its name on the stock colours.

**C5. [checked, issue #122] Ore and Gem fields against green ground.**
Now: Ore kept its gold glint in the palette reskin (issue #18) and reads well; Gems were not checked.
Proposal: one composited readability check of Ore/Gem density stages on all three palettes, filed with
the issue #40 terrain-readability sheet. Cost: S. Kind: check only.
Checked as far as the build environment allows: both resources render through the `player` palette
(`ResourceRenderer ... Palette: player`), which is the stock `temperat.pal` on every tileset, so the palette reskin
never touched them and Ore's glint is the stock one over green ground. The Gem composite itself needs
`gem01-04.tem` from the game content, which the cloud environment cannot download - one desktop-session look at a
Gem field on Crossfire closes it.

**C6. Map previews** — see A7; it is a world item too.

## D. Buildings and defences

The roster is in good shape; these are the gaps the survey found, smallest first.

**D2. [shipped narrowed, issue #125] Small buildings carry very little team colour.**
Now: issue #108's roster sheet labels count remap pixels per sprite: `sgsns` 203, `sgwnd` 204, `sgrel`
249, `sgpwr` 332, against `sgfact` 20268. At zoomed-out magnification the owner of a Sensor Array or
Wind Turbine is a guess. Proposal: a generator-side check — each building's idle frame must put at
least ~6% of its opaque pixels on indices 80–95 — and for the three that fail, a team-coloured mast
band / roof panel / cabinet door flagged `accent=True` so the re-stamp keeps it on the ramp. Cost: S–M.
Kind: generator. Verify: the count is printed by the sheet render; a composite at 50% zoom.
Shipped (narrowed): the premise was off - as a *share* of the sprite the small buildings are at 13-20%, and
issue #108's plinth band carries every roster building's owner at half zoom. The two real gaps were the
defence pedestals (no plinth, ~5%), which now carry a full team ring each. Nothing else was changed.

**D3. [shipped, issue #125] Rubble exists for four buildings; the other eleven vanish after the explosion.**
Now: `dead:` sequences only on `sgpwr`, `sgapwr`, `sghyd`, `sgfact`. Stock RA is the same for most
buildings, but the halls (`sgdra`, `sgshl`, `sgcry`, `sgdai`) popping out of existence reads cheap at
their size. Proposal: derive rubble the way build-ups are derived (`make_frames()`): flatten the mesh to
~20% height, grey-rust tint, scatter a few slab fragments with `_scatter()`, `Tick: 800` like the
existing four. One function, eleven sheets. Cost: S–M. Kind: generator.
Shipped: twelve (the count was ten roster buildings plus both defence pedestals), all derived from each
building's own damaged mesh by `wreck_mesh()`. Not seen live.

**D4. [shipped, issue #125] The concrete aprons under every building are stock RA bibs.**
Now: `bib2.tem`/`bib3.tem`/`mb*` under every Sungrid building — tan Red Alert concrete under solarpunk
buildings, on every tileset. Proposal: `sgbib2.png`/`sgbib3.png` on the terrain palette: permeable
pavers with grass joints, drawn once per size with `_scatter()` for the joints, referenced from each
building's `bib:` sequence (`TilesetFilenames` can stay a single sheet since the terrain palettes are
all reskinned toward the same green). Cost: S–M. Kind: generator + sequence YAML.
Shipped, with one correction to the proposal: the desert terrain palette is a different palette, not a hue
shift, so a single sheet came out red there - each apron is indexed per tileset and the sequences carry
`-snow` / `-desert` variants like the stock bibs. Four sheets cover every Sungrid footprint. Not seen live.

**D5. [Refinery shipped, issue #126; WEAP, the barracks and TSLA open] Stock buildings still in the tree, ordered by screen time.**
Now: `PROC`, `WEAP`, `BARR`/`TENT`, `DOME`, `FIX`, `HPAD`, `AFLD`, `ATEK`/`STEK`, `SPEN`/`SYRD`, the stock
defences (`PBOX`, `HBOX`, `GUN`, `AGUN`, `SAM`, `TSLA`, `GAP`), the superweapons. Proposal: `PROC`
first (in every base, already renamed Materials Refinery, and the Depot beside it is a Sungrid solid),
then `WEAP` and the two barracks, then `TSLA` (the strongest remaining Red Alert signature — make it an
Arc Pylon in the Arc Turret's vocabulary), then stop. Cost: M each. Kind: generator (one `*_mesh()`
each, with build-up and rubble derived). Verify: as for every roster pass since issue #106.
Shipped (first of four): the Materials Refinery, `sgproc_mesh()` on a new 90x72 frame family, conveyor
animated in the body (the stock `proctop` overlay goes), wreck and build-up derived, apron from D4, scene cameo.
Not seen live; the War Factory, the two barracks and the Tesla Coil wait on that look.

**D6. [shipped, issue #125] Production and docking have no animation on the Sungrid producers.**
Now: `SGDRN`/`SGDRA` have no `WithProductionOverlay`; `RCYD` has no dock overlay (stock `PROC` has
`proctop`). Proposal: a pad-light chase on the Drone Bay while producing (its idle chase already exists
— gate a brighter variant on the production condition), and a Depot conveyor overlay while a Hauler is
docked. Cost: S each. Kind: generator + YAML. Verify: condition wiring via `--check-yaml`.
Shipped: `WithProductionOverlay` on both Drone Bays (a fast marker chase on the Drone Bay, work lights under
the Aerial Fab's eave) and `WithDockedOverlay` on the Depot (scrap plates arcing into the heap). Not seen live.

**D7. Cameo drift** (issue #107): the Advanced Solar Array's photo still shows the concentrator dish
the sprite lost. Owner's decision is to keep the photographic set; a re-crop is recorded there, not
here.

## E. Items that need an engine patch

Listed so they are scoped as engine work rather than attempted in YAML.

**E1. `WithTurretAimAnimation` loses the damage prefix** (found in issue #113). A one-line engine fix
would let `SGTUR`, and any future turret, use the stock trait instead of two `WithSpriteTurret`s
flipped by a condition. Kind: engine. Verify: compile first (`CLAUDE.md`, "Do this from now on").

**E2. `WithResourceLevelSpriteBody` cannot animate**, which is why the Battery Bank's charging and the
Depot's stack are overlays. A `Length`-aware variant that cycles frames within the fill stage would let
both bodies carry their motion. Kind: engine. Cost: S once the build environment is up.

**E3. The headless black battlefield** (issue #49): the render player's `Shroud` reports nothing
explored under the `Launch.SkirmishBots` patch. Not player-facing, but it is the single blocker to
screenshotting any in-world item on this list without a desktop. Kind: engine investigation.

## F. Artist and composer briefs

Not blockers (`docs/ROADMAP.md`, Beta gate); recorded so a brief can be handed over without a survey.

- **Emblem and wordmark** — see A9.
- **Infantry** — the per-facing `PC` track works but a 15px soldier is where a pixel artist beats a
  generator fastest; B7's E1 is the brief.
- **A second pass over the `Mesh` roster** — materials and value structure only; silhouettes, footprints
  and the diamond plinth are settled.
- **Menu sting** — `gen_intro_music.py`'s 42-second loop is a placeholder for a composer.
