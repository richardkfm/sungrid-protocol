# Sungrid Protocol — Economic Victory Mode

Destruction victory (eliminate all opponents) remains the default, always-available win condition. This document specifies the first alternative: an optional economic victory mode, toggleable per-lobby.

## Name

| Candidate | Note |
|---|---|
| **Grid Reserve** *(recommended)* | Reads as a bank/reserve concept, fits the smart-grid fiction, short and HUD-friendly ("Grid Reserve: 42,000 / 60,000"). |
| Energy Surplus | Clear but undersells the "banking" mechanic. |
| Sunbank Protocol | On-theme but slightly cute; risks tone drift toward goofy. |
| Reserve Threshold | Descriptive but dry, weak as a lobby-facing mode name. |
| Solvency Protocol | Strong economic framing, less solarpunk-specific. |

## Core rules

Grid Reserve introduces a new building type, the **Vault**, and a new per-player resource pool, **Reserve**, that is separate from ordinary spendable Credits.

1. **Depositing.** Vaults convert spendable Credits into Reserve at a fixed rate, at a capped deposit rate per tick (prevents "dump the whole treasury in one safe moment"), and only ever bank the **surplus above a minimum operating balance** — a Vault will not draw its owner down to nothing. Deposits are **irreversible** — Reserve cannot be withdrawn back into spendable Credits. This is the actual spend-vs-save decision: money in a Vault can never again buy units or defenses.
2. **Capacity.** Each Vault has a maximum Reserve capacity. Reaching a high Reserve target requires building and defending **multiple Vaults**, which is what keeps the mode from collapsing into "build one Vault in a corner and wait." With the Sun Cycle on (the default since issue #136's second revision) a third of every Vault is kept for stored energy, so one holds 5,360 Reserve instead of 8,000 - see "Sun Cycle" below. The number of Vaults is capped too (issue #147, `GridReserveBankLimit`): as many as hold the target, plus four - enough to rebuild after a raid, not enough to out-bank a raid by sheer count.
3. **Vulnerability.** Vaults are ordinary destructible structures. Destroying an enemy Vault drains a percentage (recommended: 50%) of the Reserve it held and grants the attacker a Credits reward proportional to the drained amount. This is the mechanism that keeps harassment and raiding relevant under this mode — a Vault is a juicier raid target than almost anything else on the map once it's carrying real Reserve.
4. **Win condition — Grid Lockdown.** When a player's total Reserve across all their Vaults first reaches the map's Reserve target, a **Grid Lockdown countdown** (60–120 seconds, map-configurable) begins and is broadcast to all players. If the player's Reserve stays at or above the target for the full countdown, they win. If Reserve drops below target at any point during the countdown (typically because a Vault was destroyed), the countdown cancels and must be re-triggered from scratch once the target is met again - and not before a **45-second re-arm** has passed (`LockdownRearmTicks`, issue #143), however fast the owner re-banks. Without it a raid bought about five seconds: cash piles up above the operating floor while Lockdown holds, so the owner's banks refilled the loss almost at once. Banking carries on during the re-arm; both sides see it on the HUD ("LOCKDOWN RE-ARMING" / "ENEMY RE-ARMING"), and the cancel line names the wait. Bots read an opponent at target as "in Lockdown" (`LockdownEligible`), so their Lockdown response keeps attacking through the re-arm window.
5. **Toggle.** Grid Reserve is a lobby option, still toggleable off per-match, but on by default as of Phase 3's playtest rollout — it's the mode that makes Sungrid Protocol's economy distinct, so it's the standard experience rather than an opt-in extra. Destruction victory remains fully intact and available in every match regardless of this toggle (see pillar 7 in `docs/VISION.md`) — turning Grid Reserve off never removes it, and winning by elimination works identically whether Grid Reserve is on or off.

## Example Reserve targets

Targets scale per player, with a modest per-player discount at higher counts so 6-player games don't take disproportionately longer to resolve than 3-player games.

| Map size | 2 players | 3 players | 4 players | 6 players |
|---|---|---|---|---|
| Small | 20,000 | 27,000 | 32,000 | 42,000 |
| Medium | 30,000 | 40,000 | 48,000 | 63,000 |
| Large | 45,000 | 60,000 | 72,000 | 95,000 |

(Baseline: ~15,000 Reserve per player on a medium map, roughly a 5% per-additional-player discount past the second player. These are starting points for Phase 3 playtesting, not final balance — expect them to move. Superseded for the actual shipped baseline by issue #93's `BaseTargetPerPlayer` increase below — this table is kept as the original Phase 3 illustration.)

## HUD / scoreboard requirements

- Per-player Reserve bar in the sidebar/scoreboard, showing current Reserve and the map's target (e.g. `Grid Reserve: 42,000 / 60,000`).
- Broadcast banner + audio cue to **all players** when any player's Grid Lockdown countdown starts, and again if it cancels — this is the moment that should trigger table-wide attention and raids.
- Minimap reveal: once a player's Reserve reaches **50% of target**, their Vault locations are revealed on all opponents' minimaps for the rest of the match (see anti-turtle rules below).
- End-of-match scoreboard shows final Reserve totals for all players regardless of who won, so "who was closest" is visible even in a destruction-victory game.

## Anti-stalemate rules

- **Grid Decay:** if no player has triggered a Grid Lockdown countdown within a map-configured time window (recommended: 75% of the map's expected match length), all players' Reserve begins slowly decaying (recommended: 1%/minute) until someone reaches target. This prevents a mutual-turtle deadlock where nobody pushes for the win because everyone is "safely" below target.
- Grid Decay never reduces Reserve below zero and never affects Credits — it only pressures the Reserve race to actually resolve.

## Anti-turtle rules

- **50% minimap reveal** (above) — you cannot bank in total secrecy once you're meaningfully ahead.
- **Per-Vault capacity cap** — reaching a real target requires multiple exposed Vaults, not one hidden bunker.
- **No defensive synergy** — Vaults grant no combat bonus, no repair aura, nothing that makes them worth defending *other than* the Reserve inside them. They don't anchor a defensive turtle the way a normal base does.
- **Deposit-rate cap** — Credits can't be dumped into Reserve in one panic move when a raid is spotted inbound; hoarding has to be a sustained commitment, not a last-second reflex.

## Why harassment and map pressure remain relevant

Under Grid Reserve, the *thing worth attacking* is different (Vaults instead of, or in addition to, production buildings), but the incentive to scout, harass, and raid is not reduced — it's redirected. A player sitting on a large, undefended Reserve is a bigger prize than a player who spent everything on units, which keeps map control and scouting valuable exactly the way they are in a destruction-victory game.

## Why this mode is strongest with 3+ players

In a 1v1 match, hoarding is a pure two-body optimization race — whoever banks faster wins, and the only counterplay is "attack the other guy," which is identical to destruction-victory play. With 3 or more players, a leading hoarder becomes the shared target of the whole table: minimap reveal at 50% invites opportunistic raids from *any* opponent, not just the "designated rival," which creates dogpile dynamics, kingmaking (a weaker player choosing who to raid can decide who wins), and genuine multi-way tension that doesn't exist in 2-player games. This is also why diplomacy/alliance mechanics are deferred — they only make sense once this 3+-player dynamic is validated.

## AI opponents

Grid Reserve is on by default, so skirmish bots have to be able to play it — otherwise the mode's headline decision ("bank or spend?") is one only the human ever makes, and every AI match silently reduces back to destruction victory. Deposits themselves are automatic for everyone, so the only real agency the mode offers is **how much Vault capacity you build**, **whether you defend it**, and **whether you go kill someone else's**. Bot behaviour is scoped to the first two:

- **Every stock personality (Rush / Normal / Turtle / Naval) banks.** Each one builds Vaults sized to the *map's Reserve target* rather than to its ore-storage needs, which is what makes an economic win reachable for them at all. Without this a bot only ever builds a Vault when its ore storage is nearly full — a trigger that has nothing to do with the Reserve target and tops out long below it.
- **Bots defend their Vaults** — the Vault actor is already in every personality's squad `ProtectionTypes`, so a raid on a bot's Reserve pulls its defending squads the same way a raid on its refineries does.
- **Bots read the race.** A bot that sees an opponent past the 50% minimap-reveal threshold banks *harder* (it raises its own coverage target); a bot that sees an opponent actually holding Lockdown stops buying Vaults, because the race is already lost on the clock and that income is worth more as the army that can still break the Lockdown by killing their Vaults. Since issue #141 they also go and do it: while an opponent holds Lockdown, the Rush, Normal, Turtle, Naval and Grid Broker personalities swap their own squad manager for `SquadManagerBotModule@lockdown-response`, which sends every unit at the Vaults in waves of six from the first tick, map-wide (Turtle included - it otherwise never attacks). Easy Grid Broker still concedes.
- **Bots pace their capacity against what they've actually banked.** A bot adds the next Vault only once the ones already standing are ~80% full, and doesn't start banking at all for the first few minutes. Vaults all draw from one treasury, so several filling at once multiply the drain — and every bot production path in the engine is gated on spendable cash (`ProductionMinCashRequirement`), so a bot that banks too early or too wide stops building anything at all. See backlog issue #68.
- **Grid Broker AI** is a fifth lobby personality for players who want an opponent that treats the economic win as its primary plan. It builds the Normal AI's base and differs in two things: its Reserve economy (over-builds *capacity* past the target as raid redundancy, and never abandons banking when an opponent reaches Lockdown — it races them for it), and a smaller attack force threshold, because banking is income that could have been army and an unpressured opponent simply out-banks it. It no longer starts banking *earlier* than the stock personalities: doing so ran its economic clock before an opponent had an army to contest it with (backlog issue #69).
- **Easy Grid Broker AI** is a sixth personality, and the one to learn the mode against. The point it exists to make is that a Grid Reserve bot which plays the *economy* well is still a full-strength Normal AI in the *ground war*, and it is usually the ground war that beats a new player — so unlike the Grid Broker it deliberately does **not** reuse the Normal AI's base. It carries its own smaller base builder (1 barracks / 1 tent / 1 war factory against 7/7/4, no superweapons or advanced tech, and its War Factory itself is delayed, delayed further still by issue #85, and pushed out again by issue #96, so it doesn't reach production parity before a player finishing their own opening build), its own unit builder with hard `UnitLimits` on every line rather than the four the Normal AI caps (so its army cannot grow past a small, fixed ceiling — which for a banking bot's economy alone would otherwise never happen), a flat non-random 16-unit attack force with a guaranteed rebuilding gap between pushes, half the opening harvesters, and no support powers at all. It permits one additional base past its starting Construction Yard as of issue #94, gated behind a spare-cash threshold raised again by issue #96 after it was still expanding too quickly, so a new player still faces a single-base opponent through most of the match. Its Reserve economy banks late, one Vault at a time, starting even later still after issue #85, and concedes an opponent's Lockdown instead of racing it. See backlog issues #69, #82, #85, #94, and #96.
- **Saboteur AI** is a seventh personality (backlog issue #135, reworked). It plays for the Reserve - it banks with the Grid Broker's settings - behind a defensive base and a small army, and slows its opponents with Spies (Thieves for the Assembly, which cannot build a Spy): every 90 seconds up to two infiltrators make for a power plant (a blackout) or a Refinery (half the owner's cash), covered by a small diversion attack on another part of the base. Its heavy units only move in a finishing push, once three blackouts have been seen and an opponent's grid is down again, or at once if an opponent goes into Lockdown. With Grid Reserve off it plays the same way and that push is how it wins. A Thief cannot cause a blackout, so the Assembly's Saboteur never saw three and never pushed at all until issue #141 gave `EnemyGridStateBotModule` a fallback: 14 minutes without a push (from the start, then from the end of the last one) and it pushes anyway, for two minutes.

Both of the gaps issue #67 left open are closed: bots prefer enemy Vaults as targets (issue #105, an engine patch) and every personality but Easy Grid Broker attacks an opponent holding Lockdown, Turtle included (issue #141, configuration only).

**Bots keep a higher spendable floor (issue #141).** Every bot base builder only adds production above `NewProductionCashThreshold` (7000-8000) and every expansion manager only buys an MCV above `BuildAdditionalMCVCashAmount` (5000), so a bot whose Vaults held its cash at the 3000 floor stopped growing once banking began. `GridReserveOperatingBalance@bots` on the Player (driven by `GrantConditionOnBotOwner`, which every client resolves alike, since Vaults are synced) raises the floor to 8500 for every personality except Easy Grid Broker. A human keeps 3000.

Bots read every player's Reserve total directly rather than inferring it from the minimap reveal. This is the usual OpenRA bot convention (stock modules read enemy positions and unit counts the same way), and the reveal threshold means a human is seeing most of the same information anyway.

## Deferred to later revisions

- Diplomacy-gated Vault protection (e.g. non-aggression pacts that exempt Vaults from raids).
- Shared or pooled Reserve between allied players.
- Alliance-split victory (co-op win when allied players' combined Reserve hits target).
- Per-faction Reserve mechanics or bonuses.
- Any UI/spectator tooling beyond the basic scoreboard above.

## Technical design (resolved RFC — backlog issue #6)

This section records the concrete trait design implemented for Phase 3, superseding the open questions in `docs/ARCHITECTURE.md`'s "New C# traits" friction point for this specific mechanic.

**The Vault is the existing Battery Bank (`SILO` in `mods/sungrid/rules/structures.yaml`), not a new actor.** `docs/BUILDINGS.md` already scoped "Battery Bank (Vault)" as one evolving building — Phase 2 shipped its storage-capacity role, Phase 3 adds the Grid Reserve deposit role on the same actor. No new actor id was introduced. It initially kept stock RA's silo art too; that was replaced in `docs/BACKLOG.md` issue #70 with dedicated Battery Bank art (`mods/sungrid/bits/sgvlt.png`, wired via `RenderSprites: Image: sgvlt`), since an ore bin filling with ore is the wrong read for a building that banks Credits as grid capacity. The nine `stages` frames are drawn as battery charge, but what drives them is **ore-storage fill**: `WithResourceLevelSpriteBody` reads `PlayerResources` (stored ore against storage capacity), not Reserve and - since the Sun Cycle (below) - not stored energy either. (This paragraph said "the same fill-fraction the trait already drove" until issue #136; neither `GridReserveVault` nor `PowerStorage` has ever driven the sprite. Showing charge or Reserve needs a sprite body that reads them, which is open follow-up work.)

**Naming convention: "Vault" is internal, "Battery Bank" is what the player sees.** These docs, the trait names (`GridReserveVault`), and the C# `[Desc]` modder documentation all say *Vault*, because that is what the thing is in design terms. Every string a player actually reads says *Battery Bank* — the actor's display name, the in-match briefing popup (`label-grid-reserve-briefing-line1`…`line5`), and the baked cameo label. Keep new player-facing text on that side of the split: a player never sees a building called a Vault, so using the word in the lobby or HUD sends them looking for something that does not exist. (This was a real leak in the lobby checkbox description until issue #70's follow-up.)

Three traits, `OpenRA.Mods.Sungrid/GridReserve/`:

- **`GridReserveVault`** (on the Battery Bank actor). `ITick` deposits `min(DepositRate, remaining Capacity, MaximumTargetPercent ceiling on the owner's total Reserve, player's Cash+Resources - MinimumOperatingBalance)` from `PlayerResources` into a per-Vault `CurrentReserve` counter every tick — the per-tick cap is what makes deposits "a sustained commitment, not a last-second reflex," and the operating-balance floor is what keeps the owner able to *play* while banking. Vaults tick in sequence and each re-reads the current balance, so the floor holds across all of a player's Vaults rather than per-Vault. Without that floor (the shipped behaviour up to backlog issue #68) a Vault absorbed every Credit the instant it arrived, so any player with a Vault still filling could not spend at all — "save only," not spend-vs-save. The `MaximumTargetPercent` ceiling is checked against `GridReserveManager.TotalReserve`, not this Vault's own holdings, and is re-read every tick rather than latched: spare Vault capacity is meant to be *raid redundancy* (somewhere to re-bank after losing one), and without the ceiling a player whose capacity exceeded the target simply banked all of it, so every Vault killed during their Lockdown came off a surplus buffer instead of off the target and the countdown never cancelled — the exact counterplay rule 4 above describes (see backlog issue #69). Because it is re-read each tick, a raid that drops the total below target re-opens banking and the owner must earn the Lockdown back. `INotifyKilled` takes the Vault's whole `CurrentReserve` off the owner's total, and pays `DestructionRewardPercent` (25%) of it to the attacker as Credits if the attacker is an enemy; the rest is lost with the building. (Until issue #141 only half came off the total and the other half stayed in it with no building holding it, out of reach of raids and Grid Decay.) `INotifyRemovedFromWorld` covers every other removal path (selling, etc.) as a full, reward-free loss — consistent with deposits being irreversible, this closes off "sell the Vault to launder Reserve back" as an escape hatch. A **capture** is a removal followed by a re-add under the new owner (`Actor.ChangeOwnerSync`): the old owner loses everything the bank held, the captor gets the same 25% reward as for destroying it, and the bank registers with the captor and banks for them from then on. The Reserve itself never changes hands. A Vault keys everything off being registered with its owner's manager (`AddedToWorld`/`RemovedFromWorld`), because an actor out of the world still ticks: before issue #141 a captured bank kept moving its *old* owner's Credits into the old owner's Reserve.
- **`GridReserveManager`** (per-`Player` actor). Pure bookkeeping: sums `TotalReserve` across the player's registered Vaults, computes the Reserve `Target` once at `WorldLoaded` from active player count, and exposes `BeaconActive`/`LockdownEligible` as threshold checks. All arithmetic is integer-only (cross-multiplication instead of division for percentage comparisons) to avoid any float non-determinism in lockstep. It also resolves its own `Enabled` flag from the `gridreserve` lobby checkbox at `WorldLoaded`, mirroring `GridReserveController` — `BeaconActive` and `LockdownEligible` both short-circuit false when disabled, and `GridReserveVault.Tick` (below) checks `manager.Enabled` before doing anything at all. This was a real bug (see `docs/BACKLOG.md` issue #37): before this gate existed, every Vault deposited Credits into Reserve unconditionally, including in ordinary destruction-victory matches with the checkbox off.
- **`GridReserveController`** (world actor, one instance). Owns the `gridreserve` lobby checkbox (`ILobbyOptions`, on by default as of the Phase 3 rollout — see the Toggle rule above), the Grid Lockdown countdown state machine per player, Grid Decay, and the win hook.

**Target formula.** `Target = BaseTargetPerPlayer * activePlayers * (1000 - discountPerMille) / 1000`, where the discount is `min(1000, 75 * max(0, activePlayers - 2))` per-mille — i.e. roughly 7.5% cheaper per player past the second. With the shipped `BaseTargetPerPlayer = 20000` (raised from 15000 by issue #93) this runs above the example target table above rather than approximating it; both constants are map/mod YAML-overridable and are expected to move further after issue #9's playtests.

**Current shipped defaults.** The prose above and the example target table describe the design; these are the literal trait field defaults actually shipped in `OpenRA.Mods.Sungrid/GridReserve/` today (all YAML-overridable per map/mod, and — like the Target constants above — provisional pending issue #9's playtests). Tick counts are converted assuming Normal game speed (25 ticks/second); real time will differ at other speeds.

| Trait | Field | Default | ~Real time (Normal speed) |
|---|---|---|---|
| `GridReserveVaultInfo` | `Capacity` | 8000 Reserve per Vault | — |
| `GridReserveVaultInfo` | `DepositRate` | 3 Credits/tick per Vault | 75 Credits/second per Vault |
| `GridReserveVaultInfo` | `MinimumOperatingBalance` | 3000 Credits | spendable floor a Vault never banks below |
| `GridReserveVaultInfo` | `MaximumTargetPercent` | 100% of Target | ceiling on the owner's *total* banked Reserve |
| `GridReserveVaultInfo` | `DestructionRewardPercent` | 25% of the Vault's holdings, to an enemy that destroys or captures it (the owner loses all of it; issue #141) | — |
| `GridReserveOperatingBalanceInfo` | `MinimumOperatingBalance` | 8500 Credits, bots except Easy Grid Broker | raises the Vault floor so bot production and expansion thresholds stay reachable (issue #141) |
| `GridReserveBankLimitInfo` | `SpareBanks` | 4 | banks allowed on top of `ceil(Target / Reserve a bank holds)`; the cap only applies with Grid Reserve on (issue #147) |
| `GridReserveManagerInfo` | `BaseTargetPerPlayer` | 20000 (raised from 15000 by issue #93) | — |
| `GridReserveManagerInfo` | `TargetDiscountPerMillePerExtraPlayer` | 75 per-mille | — |
| `GridReserveManagerInfo` | `MinimapRevealPercent` | 50% of Target | — |
| `GridReserveControllerInfo` | `CheckboxEnabled` | `false` | — |
| `GridReserveControllerInfo` | `LockdownDurationTicks` | 2250 ticks | 90 seconds |
| `GridReserveControllerInfo` | `LockdownRearmTicks` | 1125 ticks | 45 seconds after a cancel before Lockdown may start again; fixed length, not escalating (issue #143) |
| `GridReserveControllerInfo` | `DecayGraceTicks` | 45000 ticks | 30 minutes |
| `GridReserveControllerInfo` | `DecayIntervalTicks` | 1500 ticks | 60 seconds |
| `GridReserveControllerInfo` | `DecayPercent` | 1% of each Vault's Reserve per interval | — |

At these defaults (and more so with the Sun Cycle's protected energy share, 5,360 Reserve a Vault), a single Vault (8000 capacity) can never reach even the cheapest 2-player Target (~40000, after issue #93's `BaseTargetPerPlayer` increase): reaching Target always requires multiple Vaults, which is the intended anti-turtle property, not an incidental side effect of the numbers.

**`DepositRate` was retuned from 10 to 3 Credits/tick (see `docs/BACKLOG.md` issue #75).** A report of a Grid Reserve win in ~15 minutes with zero attacks traced back to the old rate: a single Vault capped in ~32 real-time seconds, and several Vaults deposit in parallel, so the window between the 50%-Target beacon reveal and Lockdown completion was too short for raiding a Vault to be a realistic counterplay — even though winning without ever fighting is fully intended by design, the vulnerability that's supposed to come with committing to that path wasn't real. The new rate stretches a single Vault's fill time to ~107 seconds, giving an attentive opponent several real-time minutes between the reveal and Lockdown to scout, redirect an army, and break the countdown per Core Rule 4.

**Minimap reveal reuses the stock `RevealsShroud` trait**, not new rendering code: the Vault has `RevealsShroud@GridReserveBeacon` with `ValidRelationships: Enemy` and `RequiresCondition: gridreserve-beacon`. `GridReserveVault` grants/revokes that condition each tick based on `GridReserveManager.BeaconActive` (Reserve ≥ 50% of target). This is the same condition-gated trait pattern already used throughout the engine (e.g. `GrantConditionOnDamageState`), so the reveal itself carries no bespoke visibility/rendering risk.

**Winning rides the existing `MissionObjectives` required-objective gate instead of touching `Player.WinState` directly.** Every player already has a `Required` objective from `ConquestVictoryConditions`. When a Lockdown countdown completes, `GridReserveController` force-completes *all* of that player's still-incomplete objectives (its own optional Grid Reserve objective and the Conquest one), which satisfies `MissionObjectives`' "all required objectives complete" check and triggers the normal `OnPlayerWon` path. `GridReserveController` then calls `ForceDefeat` on every non-allied player still undecided — otherwise opponents who are still alive would stay `WinState.Undefined` forever, since Grid Reserve's win path doesn't fit the "keep playing until you're eliminated" trigger natural to Conquest. The winner's allies are left to their own `ConquestVictoryConditions`, which completes once every non-allied player has lost. Until issue #141 this was done with `MissionObjectives.EarlyGameOver: true`, but the engine applies that flag to every *defeat* as well: the first player eliminated in a free-for-all of three or more made every survivor the winner and ended the match. It is off now, so destruction victory ends with the last side standing.

Deliberate coupling worth flagging for reviewers: `GridReserveController` assumes every ruleset that enables the `gridreserve` checkbox also has a `Required` `MissionObjectives` objective configured (true for the default Sungrid Protocol `Player` template via `ConquestVictoryConditions`). A ruleset with Grid Reserve enabled and no other required objective would never resolve a Lockdown win. Team play is intentionally out of scope here too: a Lockdown win only resolves the triggering player, not their allies — consistent with alliance-split victory being explicitly deferred above.

**Issue #8's UI scope is now fully shipped.** In addition to the Lockdown start/cancel broadcast (system text line + `Speech` cue, visible/audible to every player, not just the affected one - the speech only reached the affected player until issue #141; neither replays while a save loads) and the minimap reveal above, a persistent per-player Reserve bar (`GridReserveHudLogic`, `Container@GRID_RESERVE_HUD` in `ingame-player.yaml`) and a Reserve-totals scoreboard for observers (`GridReserveStandingsLogic`, `Container@GRID_RESERVE_STANDINGS` in `ingame-observer.yaml`) have since landed — both hide themselves via `controller.Enabled`/`IsVisible` when the mode is off, the same pattern used throughout this trait family.

**The Reserve bar shows a live Lockdown countdown, not just the one-time broadcast (see `docs/BACKLOG.md` issue #76).** Once Reserve reaches target, `GridReserveController.LockdownTicksRemaining(player)` exposes the ticks left to hold it, and `GridReserveHudLogic` swaps the bar's current/target label for a "GRID LOCKDOWN — Ns" countdown for the rest of the hold, reverting automatically the moment the countdown ends or cancels. Before this, the only signal a countdown was even running was the start/cancel broadcast text line, easy to miss mid-match with nothing on-screen to check afterward.

**The observer scoreboard shows the same countdown (see `docs/BACKLOG.md` issue #92).** Issue #76 only wired `LockdownTicksRemaining` into `GridReserveHudLogic`; `GridReserveStandingsLogic`'s per-row `AMOUNT` label kept showing the static current/target numbers even while that player was actively holding Lockdown, so an observer - including a defeated player who dropped to spectating - had no on-screen way to see the one countdown that decides the match. `GridReserveStandingsLogic` now swaps to the same "GRID LOCKDOWN — Ns" text (and a `LimeGreen` color) per row, mirroring `GridReserveHudLogic` exactly.

**An actively-playing local player also gets a warning when an opponent is holding Lockdown (see `docs/BACKLOG.md` issue #95).** Issues #76 and #92 covered the affected player's own HUD and the observer scoreboard, but a player who is fighting rather than spectating and who never opens the standings screen had no persistent on-screen sign that *someone else's* countdown was running - only the one-time start/cancel broadcast (system line + `Speech` cue), which issue #76 itself already called "easy to miss mid-match." `GridReserveHudLogic` now also checks every opponent's `LockdownTicksRemaining` (when the local player isn't themselves eligible) and swaps its label to an "ENEMY LOCKDOWN — Ns" warning in `Color.OrangeRed`, naming the opponent in the tooltip, for whichever opponent is soonest to complete. This surfaces nothing the initial broadcast didn't already tell every player (see Core Rule 4 and the "unconditionally visible... not just the affected one" note above) - it just makes that state checkable at a glance instead of a missable one-time line.

**In-match rules briefing.** `GridReserveBriefingLogic` (`Container@GRID_RESERVE_BRIEFING` in `ingame-player.yaml`) shows a small, non-blocking popup once at match start summarizing the Core Rules above (deposits, irreversibility, multi-Vault requirement, destruction/sale forfeiture, minimap reveal at 50%) with a dismiss button, and hides itself entirely when the `gridreserve` checkbox is off. Added alongside the on-by-default change above so players who have never played a Grid Reserve match aren't dropped into it with no in-game explanation.

**Bot participation (`GridReserveBotModule`).** A per-`Player` `ConditionalTrait`/`IBotTick` module in `OpenRA.Mods.Sungrid/GridReserve/GridReserveBotModule.cs`, wired up in `mods/sungrid/rules/ai.yaml`. It resolves the number of Vaults the bot wants from `GridReserveManager.Target` and the Reserve one Vault can hold - `GridReserveVaultInfo.Capacity`, less `PowerStorageInfo.ProtectedSpace` while the Sun Cycle is on (`ceil(Target * CoveragePercent / 100 / capacity)`, clamped to `MaximumVaults` - but never below `ceil(Target / capacity)`, the count that can hold the target at all; issue #136's second revision, see "Sun Cycle"), and queues one at a time through the Vault's own declared production queue whenever that queue is idle — `BaseBuilderQueueManager` then places whatever finishes at the front of a queue, so placement, base-radius and power checks are all the stock ones and no bespoke placement logic is involved. It reads `GridReserveManager.BeaconActive`/`LockdownEligible` off each enemy player to switch between `CoveragePercent` and `ContestedCoveragePercent` and to honour `AbandonBankingOnEnemyLockdown`. Two optional granted conditions (`EnemyBankingCondition`, `EnemyLockdownCondition`, both unset by default) expose that same race state to `RequiresCondition` on other bot modules, so a future aggression swap needs no further C#.

**Bot Vault raiding (issue #105).** Bots build Vaults from the module above, but until this pass they never *attacked* one on purpose. Squad target selection in the engine is purely distance-based (`FindClosestEnemy` → `ClosestToIgnoringPath`), and its only configurable steering, `IgnoredEnemyTargetTypes`, is an exclusion list — so there was no way to say "hit the Vault first". A squad walked to whichever enemy structure happened to be nearest and stopped there, which meant the raid pressure Core Rule 4 depends on existed only when a human applied it, and a bot could never break an opponent's Lockdown except by accident.

This is fixed with a pinned engine patch (`engine-patch/a15f080-squad-preferred-targets`) adding three opt-in fields to `SquadManagerBotModuleInfo` — `PreferredTargetTypes`, `PreferredTargetScanRadius` and `PreferredTargetCondition` — plus wiring in `ai.yaml`:

| Setting | Value | Why |
|---|---|---|
| `PreferredTargetTypes` | `silo` | The Vault is the win-condition structure; everything else is ordinary economy. |
| `PreferredTargetScanRadius` | `30` cells | Covers an enemy base and its approaches. Beyond it, targeting falls back to plain distance, so squads don't abandon a fight to cross the map. **Reasoned, not measured** — the first number to tune if raids feel too eager or too rare. |
| `PreferredTargetCondition` | `enemy-banking` | Granted by `GridReserveBotModule.EnemyBankingCondition`. The preference applies **only while an opponent is actually banking toward the Reserve target**, so it is dormant in destruction-only matches and in the early game. |

Applied to the Rush, Normal, Turtle, Naval and Grid Broker squad managers. **Deliberately not applied to Easy Grid Broker**, which is the learn-the-mode opponent: per this document's own framing its Reserve win should be a clock a new player can beat by pressuring the base, not an opponent that also cracks their Vaults. The Saboteur AI (issue #135) does not raid Vaults on `enemy-banking` - it answers an opponent's banking with Spies - and only its finishing push prefers them, among the power buildings and the Construction Yard, with no radius limit.

Note what this does and does not change. It changes which enemy a *squad* walks toward. It does not change individual-unit auto-targeting: `^AutoTargetGround`'s default `AutoTargetPriority` omits `Structure`, so units still never open fire on a building of their own accord — a squad ordered onto a Vault attacks it, but units idling beside one do nothing, for bots and humans alike. That is stock Red Alert behaviour and is left intact.

The whole module short-circuits on `GridReserveManager.Enabled`, the same lobby-toggle gate `GridReserveVault` and `GridReserveController` use — with the checkbox off it never touches production, and the base builder's ordinary "build a silo when ore storage is nearly full" behaviour is all that remains. `BuildingLimits: silo` was also added to all four stock personalities (previously unlimited) so that overflow path can't fight the module for build slots.

## Sun Cycle (day/night, issue #136)

A second, independent lobby option (`suncycle`, **"Day/Night Cycle", on by default** since issue #136's second
revision - the owner's call; it was off until then. `rules/world.yaml` sets `CheckboxEnabled: true` over the trait's
own default of off, the same pattern as Grid Reserve, and the checkbox stays unlocked). It changes no victory condition. One sky for the whole table: every player's night
falls at the same moment, so a dusk is a shared, readable timing window rather than a per-player hidden state.
Every number below is **reasoned, not measured**. Tick counts assume Normal speed (25 ticks/s), as elsewhere in this
document.

### The cycle

| Phase | Ticks | Time | Solar output | Why |
|---|---|---|---|---|
| Opening day | 7500 | 5:00 | 100% | `FirstDuskTick`. Keeps the opening build order out of the first night, and matches `GridReserveBotModule.StartDelayTicks` (7500): the first dusk arrives as banking can start |
| Dusk | 750 | 0:30 | 65% | One visible step down before the drop: the power bar changes in two readable steps (Pillar 1), and the dusk line is the warning |
| Night | 2250 | 1:30 | **30%** | Equal to `LockdownDurationTicks` (2250): a full Grid Lockdown hold fits exactly inside one night |
| Dawn | 750 | 0:30 | 65% | Mirror of Dusk |
| Day | 5250 | 3:30 | 100% | The bulk of the cycle, so solar's average loss stays bounded |
| **Cycle** | **9000** | **6:00** | avg 76.7% | No daytime bonus (the owner's call): `POWR` effectively costs 3.91 Credits/power on average instead of 3.00, `APWR` 6.52 instead of 5.00 |

The phase is a pure function of `World.WorldTick` (`SunCycleController.PhaseAt`): no accumulated state, nothing to
sync, identical on every client, in a replay and after loading a save. Every timing field lives on
`SunCycleController` in `rules/world.yaml` and can be overridden in a map's `rules.yaml`. The main-menu shellmap does exactly that (issue #137): with no lobby the
controller falls back to `CheckboxEnabled`, which the shellmap's rules force on, and it runs a 2750-tick (1:50)
showcase cycle with the first dusk at 0:30. Phase changes are never announced on a shellmap - it has no HUD, and it
keeps running behind the lobby, whose chat would otherwise collect every dusk and dawn line.

**Only solar falls.** `POWR` and `APWR` inherit `^SolarPower` (`rules/defaults.yaml`): two `GrantConditionOnSunPhase`
traits grant `sun-night` / `sun-twilight`, and two stock `PowerMultiplier`s (30 / 65) re-total the owner's power the
moment the condition changes. Health scaling stacks multiplicatively (a Solar Array at 25% health gives about 7 at
night). Wind Turbines, Hydrogen Plants and Smart Grid Relays are unchanged. The conditions are never granted with the
option off, so the multipliers never apply and the rules are exactly as before. `SunCycleController` repeats the two
percentages (`NightSolarPercent`, `TwilightSolarPercent`) because the HUD shows them and the bots plan with them; a
mod lint pass (`CheckSunCycleSolarPercent`) fails `--check-yaml` if the YAML multipliers and the controller disagree.
**Never put `^SolarPower` on an actor `PowerDownBotModule` can switch off** - that module sums every `PowerMultiplier`
on an actor when it estimates a toggle.

### The Battery Bank stores energy too (one building, two jobs)

There is no new building. The Battery Bank (`SILO`, the Grid Reserve Vault) gains a `PowerStorage` trait and stores
charge as well as Reserve. Charge is held in **power-seconds** (one power for one second).

**Shared capacity, energy first.** Each bank has one capacity: the Vault's `Capacity` (8000). Stored charge and banked
Reserve share it at a fixed **exchange rate of 1 power-second per credit of space** (`ChargeExchangePercent: 100`).
Since issue #136's second revision **energy comes first** (the owner's call after the first live look: "priority
should be to save energy, right?" - under the first rules Reserve, which never leaves, took over the banks within a
few cycles). The rules, in priority order:

1. **Banked Reserve is never removed to make room for charge.** Charge only ever enters space Reserve has left free.
   Irreversibility, the `MaximumTargetPercent` ceiling, the drain-on-destruction and Lockdown are untouched, so the
   guarantees from issues #37, #68, #69, #75 and #76 all hold. Energy can only *slow banking down* and lower what one
   bank holds, never undo it.
2. **A protected third.** `ProtectedChargePercent` (33) of every bank's *space* is kept for energy: Reserve can never
   occupy it, so a plain bank holds at most **5,360 Reserve** (8000 - 2640) and always has room for 2,640 energy. The
   share is of the space, so the Consortium's x1.5 capacity applies to it as to the rest of the bank: its protected
   third holds 3,960 energy. A YAML field on `PowerStorage`, not a constant.
3. **Charge first in the rest.** A bank that took surplus power in the last update (`PowerStorage.IsCharging`, set
   once a second by `PowerStorageManager`) banks no Reserve until it stops - because it is full, or the surplus has
   gone. So Reserve only ever takes space surplus power is not flowing into right now, and a bank filling up for the
   night is never raced for its space. (The literal rule the owner offered - "Reserve may not take space the bank's
   charge could still fill this day" - would need a forecast of each bank's surplus share until dusk; this is its
   deterministic, state-free equivalent. Surplus is handed out earliest-built bank first, so the banks surplus does
   not reach go on banking Reserve normally.)
4. **Charge comes only from surplus power.** Charging draws nothing visible from the grid, so it can never push a
   player into low power, and the power bar stays honest.
5. **Charge outside the protected third that has not been drawn on for a whole sun cycle gives way to Reserve**
   (`PowerStorage.IdleCharge`). Kept, but only for the unprotected two thirds: with charge first, a base that never
   runs short at night (lots of Wind Turbines - the Assembly's whole night identity) fills its banks by day and never
   empties them, and without an exit could never bank Reserve at all. A bank that discharges every night is never idle
   (the gap between nights is one Day, 5250 ticks, well under a 9000-tick cycle). The protected third stays energy
   whatever happens.
6. **Grid Reserve off:** no Reserve is ever banked, so the whole 8000 holds charge.
7. **Sun Cycle off:** `PowerStorageManager` never runs, charge stays 0, nothing is protected, and `GridReserveVault`
   uses its original formula (`Capacity - CurrentReserve`): the bank behaves exactly as before, 8000 Reserve each.

**What it does to the target (reasoned, not measured).** With the cycle on, holding a target takes `ceil(Target /
5360)` banks instead of `ceil(Target / 8000)`: two players (40,000) **8** instead of 5, three (55,500) **11** instead
of 7, four (68,000) **13** instead of 9, six (84,000) **16** instead of 11. Every bank built still adds 2,640 energy
of night storage (3,960 for the Consortium), so eight banks for a two-player target carry 21,120 energy - more than the
~13,000 a solar base's night needs (below), which is the point of protecting a share rather than a fixed amount. The
number of banks is capped at what the target needs plus four (issue #147: 12 for two players, 21 for eight), so Lockdown
stays reachable; the target ceiling, the drain-on-destruction (50% of what
the killed bank held - now at most 5,360) and the 50% minimap reveal all work on Reserve totals and are unchanged.
A deterministic model of the rules (issue #136's second revision in `docs/BACKLOG.md`; 200 Credits a second of
income, eight banks standing from 0:00) has a solar base reach 40,000 at 6:24, during its first night as drained
space opens; a turbine base (never short) at 6:58, once its idle charge yields at 6:00; the same solar base with
Consortium banks, whose bigger charge holds more of the space, at 12:02. Banks added one at a time by a bot's pacing
from 6:00 reach it at 13:15 (solar) and 20:23 (turbine), against 11:42 / 13:33 under the old first-come rules - which
left those bots 16,000 energy of 56,000 once Reserve had taken the rest.

**Why 1:1.** The exchange rate decides whether the two jobs genuinely compete. One night of a moderate deficit costs
about one bank of space: a 100-power shortfall across dusk, night and dawn is 100 x 90 + 35 x 60 (twilight runs at
65%, so its shortfall is about a third of the night's) = about 11,000 power-seconds. At 1:1 that is one and a half
banks' worth of space, a fifth to a quarter of a two-player Reserve target (40,000) - big enough to hurt, small
enough that a player can afford both with a few extra banks. At 10:1 storage would be free and there would be no
tension; at 1:10 a single night would need more banks than the target itself.

**Rates.** `ChargeRate` 40 power/s per bank: refills 8000 in 200 s, inside a 210 s day, so a bank that ran flat
overnight is full again by the next dusk. `DischargeRate` 60 power/s per bank (net, to the grid), the output of a
Smart Grid Relay: a full bank lasts 133 s at full draw against 150 s of dusk, night and dawn, so a base that leans
on storage needs more than one bank, and the rate - not the capacity - is usually what limits a single bank.
While a bank discharges, its own -10 upkeep is switched off and paid from its charge instead (an engine constraint:
the output is applied as a power modifier, and a modifier scales every enabled Power trait on the actor), so a
discharging bank spends output + 10 per second. Discharge is allocated once a second, earliest-built bank first, and
only covers the deficit (the bank never overshoots by more than its upkeep).

**What stops a bank.**
- **A power outage** (a Spy in any `^DisabledByPowerOutage` plant): banks do not discharge while it lasts, and keep
  their charge. Without this, storage would be universal blackout insurance and the Spy would lose its hard counter.
- **A Spy in the bank itself** (`InfiltrateForChargeDrain`, new): empties that bank's charge. Reserve credits in it
  are untouched; the Thief's existing 50% cash steal (`InfiltrateForCash`) is unchanged. The `SpyInfiltrate` target
  type is on a separate `Targetable@SPY` that only exists while the cycle is on, so a Spy is never spent on a bank
  that cannot hold charge (issue #103's "advertised capability with nothing behind it").
- **Destruction or sale:** the charge is lost, with **no** reward to anyone - one kill must not pay twice on top of
  the Vault's Reserve reward.

### The spend-vs-save tension it creates

The owner wanted this, so it is spelled out: **every power-second of night charge is a credit of bank space not
banked for victory, and every credit banked is night storage gone for good** (Reserve never leaves).

Worked example, two players, Target 40,000 = eight banks at minimum with the cycle on. A solar base of three Solar
Arrays and about 220 drain runs +80 by day, -25 at dusk and dawn, -130 at night. Riding the night out on storage takes
about 13,000 power-seconds a cycle and, for the rate, three banks (two for the Consortium). Under the energy-first
rules:

- **By day** surplus fills the banks it reaches first (earliest-built first, 40 a second each), and those banks bank
  no Reserve while they charge; the rest bank Reserve as before. A bank surplus has filled is closed to Reserve.
- **By night** the charge drains and Reserve backfills the freed space down to the protected third (deposits are
  automatic), so banking runs *faster* after dark - a player at exactly target capacity tends to reach Lockdown at
  night, and a Lockdown hold is exactly one night long.
- **Over a few cycles** Reserve settles into the unprotected two thirds of every bank and energy keeps the third:
  eight banks keep 21,120 energy for the night, more than this base needs. Under the first rules Reserve took the
  whole of every bank it reached and the nights became brownouts; that is what the protected share fixes.

The tension that remains: every bank's third is energy, so the target simply **costs more banks** with the cycle on
(8 instead of 5 for two players), each 150 Credits, -10 power while idle and one more exposed target once the 50%
minimap reveal turns on; and a base with big surplus keeps more than a third as energy in the banks it fills, which
slows its banking until the night drains them (or, if it never runs short, for one cycle). The alternative to storage
is night-proof power. Either way, night is a cost paid out of the same budget as victory, which is Pillar 3 doing its
job.

### Faction night identity

The Assembly **generates**: Wind Turbines (`SGWND`, `low` tech, 250) hold full output all night, unchanged. The
Consortium **stores**: its Battery Banks hold 50% more charge in the same space (12,000 power-seconds in an empty
bank) and release it 50% faster (90 power/s). Both come from a faction-gated `PowerStorageMultiplier@CONSORTIUM` on
`SILO` behind `GrantConditionOnFaction` (allies, england, france, germany). It affects **charge only**; Reserve
capacity is identical for both sides. The charge rate is deliberately unchanged (the owner's spec named capacity and
discharge only), so a drained Consortium bank refills 8,400 of its 12,000 in one day: the extra capacity is a buffer
across several nights or outages, and the faster discharge is the difference that shows every night. See
`docs/ENERGY_BALANCE.md`, "Night".

### What the player sees

- **HUD** (`SunCycleHudLogic`, `Container@SUN_CYCLE_HUD` in `chrome/ingame-player.yaml`): under the Grid Reserve bar
  (or in its slot when Grid Reserve is off). Since issue #136's second revision, absolute numbers and its own marks:
  a blue lightning bolt on the left, a sun (day), a low sun on the horizon (dusk and dawn) or a moon (night) on the
  right, a blue bar for stored energy over the energy the banks can hold right now, and
  "Day — dusk in 0:53 · Energy 1,200 / 10,900 · charging" - the state is *charging*, *draining*, *full*, *empty*,
  *blackout* (a Spy outage: the banks hold charge but may not give it), *no spare power* or *no Battery Banks*. The
  tooltip gives the solar percentage, the bank count, energy stored / held, the flow per second, each bank's charge
  and discharge rates and, with Grid Reserve on, the protected share (percent and energy) and the Reserve held in
  the rest. The label is white by day, sun gold at dusk and dawn, moonlight blue at night (`metrics.yaml`). The Grid
  Reserve bar above it now carries a gold coin rather than the shared battery, and reads "Reserve 11,528 / 40,000";
  its tooltip adds how many banks the player has and how much Reserve they can hold. Both bars are 380 wide for the
  energy line. Review render: `docs/concept-art/issue136-hud-bars.png`.
- **Charge bar** under a selected Battery Bank (`ISelectionBar`), whenever the cycle is on.
- **Screen tint** (`SunCycleTint`): its own post-process pass, so it multiplies with a map's `TintPostProcessEffect`
  rather than replacing it. Night is cool and dim (R0.84 G0.90 B1.12 at ambient 0.74; the floor is 0.70 so team
  colours and silhouettes stay readable), twilight warm (R1.06 G0.95 B0.84 at 0.92); Dusk fades day -> twilight ->
  night across its 30 seconds and Dawn the reverse. Render-only; not drawn before the first dusk or with the option off.
- **Announcements**: a system text line at dusk, nightfall, dawn and full daylight. No new speech (Phase 7 has no voice
  set yet). The stock low-power nag (every 10 s) is muted during Dusk and Night, since the dusk line already said it,
  and restored at dawn to whatever it was before.

### Bots (`SunCycleBotModule`)

The engine's base builder treats low power as a priority override and buys the plant with the highest **nominal**
output - at night, a Solar Array running at 30%, over and over. `SunCycleBotModule` (every personality) answers
that:

- **By day** (from tick 6000, a minute before the first dusk) it projects the night deficit from its solar plants'
  current output and the controller's night percentage, wants `ceil(deficit / bank discharge rate)` storage banks
  (max 3; Easy Grid Broker 1), and buys night-proof power (`sgwnd`, `sgrel`, `sghyd`, best buildable by output; max 6,
  Easy Grid Broker 2) for whatever the storage cannot discharge fast enough to cover.
- **At dusk and night** it checks every second and claims the idle Building queue for a night-proof plant whenever
  the grid is under the base builder's own power margin (mirrored from `BaseBuilderQueueManager`, which does not
  expose it), getting there before the low-power override can buy a Solar Array. Best effort: the two modules race
  for an idle queue, and if no night-proof plant is buildable, or the cap is reached, the stock override still runs.
- **Banks for both jobs.** `GridReserveBotModule` adds the sun module's `StorageBanksWanted` on top of its Vault count
  (the storage share is extra capacity, never taken out of the target coverage), and its "expand once the standing
  Vaults are 80% full" pacing only counts the Vault share - otherwise storage banks that never fill with Reserve
  would stall it. With the cycle off the storage count is 0 and both modules behave exactly as before. Since issue
  #136's second revision the Vault count is sized against the Reserve one bank can hold with the protected third
  taken out (5,360), and its pacing counts charge outside the protected thirds as taken - otherwise a bot whose newest
  bank surplus has filled with energy waits a whole cycle for it before building the next (the model above: 20:23
  rather than 39:09 to a two-player target for a turbine base). `MaximumVaults` (8) now trims only the redundancy:
  it never drops the count below `ceil(Target / 5360)`. Worked, cycle on: two players, Target 40,000,
  `CoveragePercent` 125 -> 10, trimmed to 8 (the floor is 8), plus up to 3 storage banks = up to 11; three players
  (55,500) -> 11 (+3); four (68,000) -> 13 (+3). The floor also fixes a gap that predates the cycle: with it off, four
  players (68,000) needed 9 Vaults of 8,000 and the cap of 8 left bots 4,000 short of the target for good.
- `silo` stays **out** of every `PowerTypes` list: it is storage, not supply (the same reasoning that keeps `rcyd` out
  of `RefineryTypes`).
- **The Saboteur (issue #135) gets stronger at night without any change**: its `EnemyGridStateBotModule` reads an
  opponent in low or critical power as "grid down", and night puts solar bases there. Tune it with the cycle off
  first, so its strength never depends on an optional mode. Its `SpyBotModule` could add `silo` to
  `TargetPriorities` to drain banks before dusk; it asks the Spy's own targeters, so with the cycle off (no
  `SpyInfiltrate` on the bank) it would simply never pick one. Not done here - that is issue #135's call.

### A pre-existing engine gap the night exposes

`PowerManager` only notifies `INotifyPowerLevelChanged` listeners when excess power changes sign (Normal <-> Low).
Low <-> Critical was never announced, so a `GrantConditionOnPowerState` with `ValidPowerStates: Critical` went stale:
the drones stayed armed at Critical power, and once disarmed could stay disarmed until power was fully back. Every
night walks a solar grid down through exactly that step. Fixed mod-side, without an engine patch:
`PowerStateChangeNotifier` on the Player actor watches `PowerState` every tick and re-notifies on any change
(duplicates are harmless; the only listener re-reads the state). It is active whether or not the cycle is on, since
the gap existed before it.

### Not verified, and open

No live match has been played with the cycle on - nothing here can run a client (see `CLAUDE.md`). Verified only by
compiling, `--check-yaml` across every map, the interface checks and negative controls (issue #136 lists them).
Open: the bank's sprite still shows ore-storage fill, not charge (needs a sprite body that reads `PowerStorage`);
no night art states (lamps on the arrays, dark panels - art rule 16 territory); an
observer-scoreboard column; a "hit the banks before sunset" squad hook for the bots (`GrantConditionOnSunPhase` works
on the Player actor and is ready for a `PreferredTargetCondition`); and every constant above is waiting on a playtest.
Since the cycle went on by default, the Saboteur AI (tuned with it off) meets a night in every default match, and night
makes its `EnemyGridStateBotModule` read more opponents as "grid down" - its push timing is the first thing to watch.
The protected third (33%) and the energy-first rule are the owner's decisions; their numbers above are reasoned and
modelled, not measured.
