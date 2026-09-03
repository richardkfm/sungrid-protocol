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
2. **Capacity.** Each Vault has a maximum Reserve capacity. Reaching a high Reserve target requires building and defending **multiple Vaults**, which is what keeps the mode from collapsing into "build one Vault in a corner and wait."
3. **Vulnerability.** Vaults are ordinary destructible structures. Destroying an enemy Vault drains a percentage (recommended: 50%) of the Reserve it held and grants the attacker a Credits reward proportional to the drained amount. This is the mechanism that keeps harassment and raiding relevant under this mode — a Vault is a juicier raid target than almost anything else on the map once it's carrying real Reserve.
4. **Win condition — Grid Lockdown.** When a player's total Reserve across all their Vaults first reaches the map's Reserve target, a **Grid Lockdown countdown** (60–120 seconds, map-configurable) begins and is broadcast to all players. If the player's Reserve stays at or above the target for the full countdown, they win. If Reserve drops below target at any point during the countdown (typically because a Vault was destroyed), the countdown cancels and must be re-triggered from scratch once the target is met again.
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
- **Bots read the race.** A bot that sees an opponent past the 50% minimap-reveal threshold banks *harder* (it raises its own coverage target); a bot that sees an opponent actually holding Lockdown stops buying Vaults, because the race is already lost on the clock and that income is worth more as the army that can still break the Lockdown by killing their Vaults.
- **Bots pace their capacity against what they've actually banked.** A bot adds the next Vault only once the ones already standing are ~80% full, and doesn't start banking at all for the first few minutes. Vaults all draw from one treasury, so several filling at once multiply the drain — and every bot production path in the engine is gated on spendable cash (`ProductionMinCashRequirement`), so a bot that banks too early or too wide stops building anything at all. See backlog issue #68.
- **Grid Broker AI** is a fifth lobby personality for players who want an opponent that treats the economic win as its primary plan. It builds the Normal AI's base and differs in two things: its Reserve economy (over-builds *capacity* past the target as raid redundancy, and never abandons banking when an opponent reaches Lockdown — it races them for it), and a smaller attack force threshold, because banking is income that could have been army and an unpressured opponent simply out-banks it. It no longer starts banking *earlier* than the stock personalities: doing so ran its economic clock before an opponent had an army to contest it with (backlog issue #69).
- **Easy Grid Broker AI** is a sixth personality, and the one to learn the mode against. The point it exists to make is that a Grid Reserve bot which plays the *economy* well is still a full-strength Normal AI in the *ground war*, and it is usually the ground war that beats a new player — so unlike the Grid Broker it deliberately does **not** reuse the Normal AI's base. It carries its own smaller base builder (1 barracks / 1 tent / 1 war factory against 7/7/4, no superweapons or advanced tech, and its War Factory itself is delayed, delayed further still by issue #85, and pushed out again by issue #96, so it doesn't reach production parity before a player finishing their own opening build), its own unit builder with hard `UnitLimits` on every line rather than the four the Normal AI caps (so its army cannot grow past a small, fixed ceiling — which for a banking bot's economy alone would otherwise never happen), a flat non-random 16-unit attack force with a guaranteed rebuilding gap between pushes, half the opening harvesters, and no support powers at all. It permits one additional base past its starting Construction Yard as of issue #94, gated behind a spare-cash threshold raised again by issue #96 after it was still expanding too quickly, so a new player still faces a single-base opponent through most of the match. Its Reserve economy banks late, one Vault at a time, starting even later still after issue #85, and concedes an opponent's Lockdown instead of racing it. See backlog issues #69, #82, #85, #94, and #96.

Deliberately *not* done yet: bots do not preferentially target enemy Vaults when choosing what to attack, and do not switch out of turtling when an opponent is about to win economically. Both need changes inside the engine's squad target selection rather than mod-side configuration; see `docs/BACKLOG.md` issue #67.

Bots read every player's Reserve total directly rather than inferring it from the minimap reveal. This is the usual OpenRA bot convention (stock modules read enemy positions and unit counts the same way), and the reveal threshold means a human is seeing most of the same information anyway.

## Deferred to later revisions

- Diplomacy-gated Vault protection (e.g. non-aggression pacts that exempt Vaults from raids).
- Shared or pooled Reserve between allied players.
- Alliance-split victory (co-op win when allied players' combined Reserve hits target).
- Per-faction Reserve mechanics or bonuses.
- Any UI/spectator tooling beyond the basic scoreboard above.

## Technical design (resolved RFC — backlog issue #6)

This section records the concrete trait design implemented for Phase 3, superseding the open questions in `docs/ARCHITECTURE.md`'s "New C# traits" friction point for this specific mechanic.

**The Vault is the existing Battery Bank (`SILO` in `mods/sungrid/rules/structures.yaml`), not a new actor.** `docs/BUILDINGS.md` already scoped "Battery Bank (Vault)" as one evolving building — Phase 2 shipped its storage-capacity role, Phase 3 adds the Grid Reserve deposit role on the same actor. No new actor id was introduced. It initially kept stock RA's silo art too; that was replaced in `docs/BACKLOG.md` issue #70 with dedicated Battery Bank art (`mods/sungrid/bits/sgvlt.png`, wired via `RenderSprites: Image: sgvlt`), since an ore bin filling with ore is the wrong read for a building that banks Credits as grid capacity. The nine `stages` frames now show battery charge, which is the same fill-fraction the trait already drove.

**Naming convention: "Vault" is internal, "Battery Bank" is what the player sees.** These docs, the trait names (`GridReserveVault`), and the C# `[Desc]` modder documentation all say *Vault*, because that is what the thing is in design terms. Every string a player actually reads says *Battery Bank* — the actor's display name, the in-match briefing popup (`label-grid-reserve-briefing-line1`…`line5`), and the baked cameo label. Keep new player-facing text on that side of the split: a player never sees a building called a Vault, so using the word in the lobby or HUD sends them looking for something that does not exist. (This was a real leak in the lobby checkbox description until issue #70's follow-up.)

Three traits, `OpenRA.Mods.Sungrid/GridReserve/`:

- **`GridReserveVault`** (on the Battery Bank actor). `ITick` deposits `min(DepositRate, remaining Capacity, MaximumTargetPercent ceiling on the owner's total Reserve, player's Cash+Resources - MinimumOperatingBalance)` from `PlayerResources` into a per-Vault `CurrentReserve` counter every tick — the per-tick cap is what makes deposits "a sustained commitment, not a last-second reflex," and the operating-balance floor is what keeps the owner able to *play* while banking. Vaults tick in sequence and each re-reads the current balance, so the floor holds across all of a player's Vaults rather than per-Vault. Without that floor (the shipped behaviour up to backlog issue #68) a Vault absorbed every Credit the instant it arrived, so any player with a Vault still filling could not spend at all — "save only," not spend-vs-save. The `MaximumTargetPercent` ceiling is checked against `GridReserveManager.TotalReserve`, not this Vault's own holdings, and is re-read every tick rather than latched: spare Vault capacity is meant to be *raid redundancy* (somewhere to re-bank after losing one), and without the ceiling a player whose capacity exceeded the target simply banked all of it, so every Vault killed during their Lockdown came off a surplus buffer instead of off the target and the countdown never cancelled — the exact counterplay rule 4 above describes (see backlog issue #69). Because it is re-read each tick, a raid that drops the total below target re-opens banking and the owner must earn the Lockdown back. `INotifyKilled` drains `DestructionDrainPercent` (default 50%) of `CurrentReserve` from the owner's total, of which `DestructionRewardPercent` (default 50%, so 25% of the Vault's holdings by default) is paid to the attacker as Credits; the undrained remainder is not refunded anywhere, it is simply lost with the building. `INotifyRemovedFromWorld` covers every other removal path (selling, etc.) as a full, reward-free loss — consistent with deposits being irreversible, this closes off "sell the Vault to launder Reserve back" as an escape hatch.
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
| `GridReserveVaultInfo` | `DestructionDrainPercent` | 50% | — |
| `GridReserveVaultInfo` | `DestructionRewardPercent` | 50% (of the drained amount, so 25% of the Vault's holdings) | — |
| `GridReserveManagerInfo` | `BaseTargetPerPlayer` | 20000 (raised from 15000 by issue #93) | — |
| `GridReserveManagerInfo` | `TargetDiscountPerMillePerExtraPlayer` | 75 per-mille | — |
| `GridReserveManagerInfo` | `MinimapRevealPercent` | 50% of Target | — |
| `GridReserveControllerInfo` | `CheckboxEnabled` | `false` | — |
| `GridReserveControllerInfo` | `LockdownDurationTicks` | 2250 ticks | 90 seconds |
| `GridReserveControllerInfo` | `DecayGraceTicks` | 45000 ticks | 30 minutes |
| `GridReserveControllerInfo` | `DecayIntervalTicks` | 1500 ticks | 60 seconds |
| `GridReserveControllerInfo` | `DecayPercent` | 1% of each Vault's Reserve per interval | — |

At these defaults, a single Vault (8000 capacity) can never reach even the cheapest 2-player Target (~40000, after issue #93's `BaseTargetPerPlayer` increase): reaching Target always requires multiple Vaults, which is the intended anti-turtle property, not an incidental side effect of the numbers.

**`DepositRate` was retuned from 10 to 3 Credits/tick (see `docs/BACKLOG.md` issue #75).** A report of a Grid Reserve win in ~15 minutes with zero attacks traced back to the old rate: a single Vault capped in ~32 real-time seconds, and several Vaults deposit in parallel, so the window between the 50%-Target beacon reveal and Lockdown completion was too short for raiding a Vault to be a realistic counterplay — even though winning without ever fighting is fully intended by design, the vulnerability that's supposed to come with committing to that path wasn't real. The new rate stretches a single Vault's fill time to ~107 seconds, giving an attentive opponent several real-time minutes between the reveal and Lockdown to scout, redirect an army, and break the countdown per Core Rule 4.

**Minimap reveal reuses the stock `RevealsShroud` trait**, not new rendering code: the Vault has `RevealsShroud@GridReserveBeacon` with `ValidRelationships: Enemy` and `RequiresCondition: gridreserve-beacon`. `GridReserveVault` grants/revokes that condition each tick based on `GridReserveManager.BeaconActive` (Reserve ≥ 50% of target). This is the same condition-gated trait pattern already used throughout the engine (e.g. `GrantConditionOnDamageState`), so the reveal itself carries no bespoke visibility/rendering risk.

**Winning rides the existing `MissionObjectives` required-objective gate instead of touching `Player.WinState` directly.** Every player already has a `Required` objective from `ConquestVictoryConditions`. When a Lockdown countdown completes, `GridReserveController` force-completes *all* of that player's still-incomplete objectives (its own optional Grid Reserve objective and the Conquest one), which satisfies `MissionObjectives`' "all required objectives complete" check and triggers the normal `OnPlayerWon` path. `MissionObjectives.EarlyGameOver` is turned on for the `Player` template so that win immediately force-defeats the winner's enemies too — otherwise, opponents who are still alive would stay `WinState.Undefined` forever, since Grid Reserve's win path doesn't fit the "keep playing until you're eliminated" trigger natural to Conquest. This is a no-op for pure destruction games: by the time Conquest can complete, every opponent is already `Lost` through elimination.

Deliberate coupling worth flagging for reviewers: `GridReserveController` assumes every ruleset that enables the `gridreserve` checkbox also has a `Required` `MissionObjectives` objective configured (true for the default Sungrid Protocol `Player` template via `ConquestVictoryConditions`). A ruleset with Grid Reserve enabled and no other required objective would never resolve a Lockdown win. Team play is intentionally out of scope here too: a Lockdown win only resolves the triggering player, not their allies — consistent with alliance-split victory being explicitly deferred above.

**Issue #8's UI scope is now fully shipped.** In addition to the Lockdown start/cancel broadcast (system text line + `Speech` cue, unconditionally visible/audible to every player, not just the affected one) and the minimap reveal above, a persistent per-player Reserve bar (`GridReserveHudLogic`, `Container@GRID_RESERVE_HUD` in `ingame-player.yaml`) and a Reserve-totals scoreboard for observers (`GridReserveStandingsLogic`, `Container@GRID_RESERVE_STANDINGS` in `ingame-observer.yaml`) have since landed — both hide themselves via `controller.Enabled`/`IsVisible` when the mode is off, the same pattern used throughout this trait family.

**The Reserve bar shows a live Lockdown countdown, not just the one-time broadcast (see `docs/BACKLOG.md` issue #76).** Once Reserve reaches target, `GridReserveController.LockdownTicksRemaining(player)` exposes the ticks left to hold it, and `GridReserveHudLogic` swaps the bar's current/target label for a "GRID LOCKDOWN — Ns" countdown for the rest of the hold, reverting automatically the moment the countdown ends or cancels. Before this, the only signal a countdown was even running was the start/cancel broadcast text line, easy to miss mid-match with nothing on-screen to check afterward.

**The observer scoreboard shows the same countdown (see `docs/BACKLOG.md` issue #92).** Issue #76 only wired `LockdownTicksRemaining` into `GridReserveHudLogic`; `GridReserveStandingsLogic`'s per-row `AMOUNT` label kept showing the static current/target numbers even while that player was actively holding Lockdown, so an observer - including a player who dropped to spectating via `EarlyGameOver` - had no on-screen way to see the one countdown that decides the match. `GridReserveStandingsLogic` now swaps to the same "GRID LOCKDOWN — Ns" text (and a `LimeGreen` color) per row, mirroring `GridReserveHudLogic` exactly.

**An actively-playing local player also gets a warning when an opponent is holding Lockdown (see `docs/BACKLOG.md` issue #95).** Issues #76 and #92 covered the affected player's own HUD and the observer scoreboard, but a player who is fighting rather than spectating and who never opens the standings screen had no persistent on-screen sign that *someone else's* countdown was running - only the one-time start/cancel broadcast (system line + `Speech` cue), which issue #76 itself already called "easy to miss mid-match." `GridReserveHudLogic` now also checks every opponent's `LockdownTicksRemaining` (when the local player isn't themselves eligible) and swaps its label to an "ENEMY LOCKDOWN — Ns" warning in `Color.OrangeRed`, naming the opponent in the tooltip, for whichever opponent is soonest to complete. This surfaces nothing the initial broadcast didn't already tell every player (see Core Rule 4 and the "unconditionally visible... not just the affected one" note above) - it just makes that state checkable at a glance instead of a missable one-time line.

**In-match rules briefing.** `GridReserveBriefingLogic` (`Container@GRID_RESERVE_BRIEFING` in `ingame-player.yaml`) shows a small, non-blocking popup once at match start summarizing the Core Rules above (deposits, irreversibility, multi-Vault requirement, destruction/sale forfeiture, minimap reveal at 50%) with a dismiss button, and hides itself entirely when the `gridreserve` checkbox is off. Added alongside the on-by-default change above so players who have never played a Grid Reserve match aren't dropped into it with no in-game explanation.

**Bot participation (`GridReserveBotModule`).** A per-`Player` `ConditionalTrait`/`IBotTick` module in `OpenRA.Mods.Sungrid/GridReserve/GridReserveBotModule.cs`, wired up in `mods/sungrid/rules/ai.yaml`. It resolves the number of Vaults the bot wants from `GridReserveManager.Target` and `GridReserveVaultInfo.Capacity` (`ceil(Target * CoveragePercent / 100 / Capacity)`, clamped to `MaximumVaults`), and queues one at a time through the Vault's own declared production queue whenever that queue is idle — `BaseBuilderQueueManager` then places whatever finishes at the front of a queue, so placement, base-radius and power checks are all the stock ones and no bespoke placement logic is involved. It reads `GridReserveManager.BeaconActive`/`LockdownEligible` off each enemy player to switch between `CoveragePercent` and `ContestedCoveragePercent` and to honour `AbandonBankingOnEnemyLockdown`. Two optional granted conditions (`EnemyBankingCondition`, `EnemyLockdownCondition`, both unset by default) expose that same race state to `RequiresCondition` on other bot modules, so a future aggression swap needs no further C#.

**Bot Vault raiding (issue #105).** Bots build Vaults from the module above, but until this pass they never *attacked* one on purpose. Squad target selection in the engine is purely distance-based (`FindClosestEnemy` → `ClosestToIgnoringPath`), and its only configurable steering, `IgnoredEnemyTargetTypes`, is an exclusion list — so there was no way to say "hit the Vault first". A squad walked to whichever enemy structure happened to be nearest and stopped there, which meant the raid pressure Core Rule 4 depends on existed only when a human applied it, and a bot could never break an opponent's Lockdown except by accident.

This is fixed with a pinned engine patch (`engine-patch/a15f080-squad-preferred-targets`) adding three opt-in fields to `SquadManagerBotModuleInfo` — `PreferredTargetTypes`, `PreferredTargetScanRadius` and `PreferredTargetCondition` — plus wiring in `ai.yaml`:

| Setting | Value | Why |
|---|---|---|
| `PreferredTargetTypes` | `silo` | The Vault is the win-condition structure; everything else is ordinary economy. |
| `PreferredTargetScanRadius` | `30` cells | Covers an enemy base and its approaches. Beyond it, targeting falls back to plain distance, so squads don't abandon a fight to cross the map. **Reasoned, not measured** — the first number to tune if raids feel too eager or too rare. |
| `PreferredTargetCondition` | `enemy-banking` | Granted by `GridReserveBotModule.EnemyBankingCondition`. The preference applies **only while an opponent is actually banking toward the Reserve target**, so it is dormant in destruction-only matches and in the early game. |

Applied to the Rush, Normal, Turtle, Naval and Grid Broker squad managers. **Deliberately not applied to Easy Grid Broker**, which is the learn-the-mode opponent: per this document's own framing its Reserve win should be a clock a new player can beat by pressuring the base, not an opponent that also cracks their Vaults.

Note what this does and does not change. It changes which enemy a *squad* walks toward. It does not change individual-unit auto-targeting: `^AutoTargetGround`'s default `AutoTargetPriority` omits `Structure`, so units still never open fire on a building of their own accord — a squad ordered onto a Vault attacks it, but units idling beside one do nothing, for bots and humans alike. That is stock Red Alert behaviour and is left intact.

The whole module short-circuits on `GridReserveManager.Enabled`, the same lobby-toggle gate `GridReserveVault` and `GridReserveController` use — with the checkbox off it never touches production, and the base builder's ordinary "build a silo when ore storage is nearly full" behaviour is all that remains. `BuildingLimits: silo` was also added to all four stock personalities (previously unlimited) so that overflow path can't fight the module for build slots.
