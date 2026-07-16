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

1. **Depositing.** Vaults convert spendable Credits into Reserve at a fixed rate, at a capped deposit rate per tick (prevents "dump the whole treasury in one safe moment"). Deposits are **irreversible** — Reserve cannot be withdrawn back into spendable Credits. This is the actual spend-vs-save decision: money in a Vault can never again buy units or defenses.
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

(Baseline: ~15,000 Reserve per player on a medium map, roughly a 5% per-additional-player discount past the second player. These are starting points for Phase 3 playtesting, not final balance — expect them to move.)

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

## Deferred to later revisions

- Diplomacy-gated Vault protection (e.g. non-aggression pacts that exempt Vaults from raids).
- Shared or pooled Reserve between allied players.
- Alliance-split victory (co-op win when allied players' combined Reserve hits target).
- Per-faction Reserve mechanics or bonuses.
- Any UI/spectator tooling beyond the basic scoreboard above.

## Technical design (resolved RFC — backlog issue #6)

This section records the concrete trait design implemented for Phase 3, superseding the open questions in `docs/ARCHITECTURE.md`'s "New C# traits" friction point for this specific mechanic.

**The Vault is the existing Battery Bank (`SILO` in `mods/sungrid/rules/structures.yaml`), not a new actor.** `docs/BUILDINGS.md` already scoped "Battery Bank (Vault)" as one evolving building — Phase 2 shipped its storage-capacity role, Phase 3 adds the Grid Reserve deposit role on the same actor/art. No new art or actor id was introduced.

Three traits, `OpenRA.Mods.Sungrid/GridReserve/`:

- **`GridReserveVault`** (on the Battery Bank actor). `ITick` deposits `min(DepositRate, remaining Capacity, player's Cash+Resources)` from `PlayerResources` into a per-Vault `CurrentReserve` counter every tick — the per-tick cap is what makes deposits "a sustained commitment, not a last-second reflex." `INotifyKilled` drains `DestructionDrainPercent` (default 50%) of `CurrentReserve` from the owner's total, of which `DestructionRewardPercent` (default 50%, so 25% of the Vault's holdings by default) is paid to the attacker as Credits; the undrained remainder is not refunded anywhere, it is simply lost with the building. `INotifyRemovedFromWorld` covers every other removal path (selling, etc.) as a full, reward-free loss — consistent with deposits being irreversible, this closes off "sell the Vault to launder Reserve back" as an escape hatch.
- **`GridReserveManager`** (per-`Player` actor). Pure bookkeeping: sums `TotalReserve` across the player's registered Vaults, computes the Reserve `Target` once at `WorldLoaded` from active player count, and exposes `BeaconActive`/`LockdownEligible` as threshold checks. All arithmetic is integer-only (cross-multiplication instead of division for percentage comparisons) to avoid any float non-determinism in lockstep. It also resolves its own `Enabled` flag from the `gridreserve` lobby checkbox at `WorldLoaded`, mirroring `GridReserveController` — `BeaconActive` and `LockdownEligible` both short-circuit false when disabled, and `GridReserveVault.Tick` (below) checks `manager.Enabled` before doing anything at all. This was a real bug (see `docs/BACKLOG.md` issue #37): before this gate existed, every Vault deposited Credits into Reserve unconditionally, including in ordinary destruction-victory matches with the checkbox off.
- **`GridReserveController`** (world actor, one instance). Owns the `gridreserve` lobby checkbox (`ILobbyOptions`, on by default as of the Phase 3 rollout — see the Toggle rule above), the Grid Lockdown countdown state machine per player, Grid Decay, and the win hook.

**Target formula.** `Target = BaseTargetPerPlayer * activePlayers * (1000 - discountPerMille) / 1000`, where the discount is `min(1000, 75 * max(0, activePlayers - 2))` per-mille — i.e. roughly 7.5% cheaper per player past the second. With the default `BaseTargetPerPlayer = 15000` this approximates (not exactly matches) the example target table above; both constants are map/mod YAML-overridable and are expected to move after issue #9's playtests.

**Current shipped defaults.** The prose above and the example target table describe the design; these are the literal trait field defaults actually shipped in `OpenRA.Mods.Sungrid/GridReserve/` today (all YAML-overridable per map/mod, and — like the Target constants above — provisional pending issue #9's playtests). Tick counts are converted assuming Normal game speed (25 ticks/second); real time will differ at other speeds.

| Trait | Field | Default | ~Real time (Normal speed) |
|---|---|---|---|
| `GridReserveVaultInfo` | `Capacity` | 8000 Reserve per Vault | — |
| `GridReserveVaultInfo` | `DepositRate` | 30 Credits/tick per Vault | 750 Credits/second per Vault |
| `GridReserveVaultInfo` | `DestructionDrainPercent` | 50% | — |
| `GridReserveVaultInfo` | `DestructionRewardPercent` | 50% (of the drained amount, so 25% of the Vault's holdings) | — |
| `GridReserveManagerInfo` | `BaseTargetPerPlayer` | 15000 | — |
| `GridReserveManagerInfo` | `TargetDiscountPerMillePerExtraPlayer` | 75 per-mille | — |
| `GridReserveManagerInfo` | `MinimapRevealPercent` | 50% of Target | — |
| `GridReserveControllerInfo` | `CheckboxEnabled` | `false` | — |
| `GridReserveControllerInfo` | `LockdownDurationTicks` | 2250 ticks | 90 seconds |
| `GridReserveControllerInfo` | `DecayGraceTicks` | 45000 ticks | 30 minutes |
| `GridReserveControllerInfo` | `DecayIntervalTicks` | 1500 ticks | 60 seconds |
| `GridReserveControllerInfo` | `DecayPercent` | 1% of each Vault's Reserve per interval | — |

At these defaults, a single Vault (8000 capacity) can never reach even the cheapest 2-player Target (~30000): reaching Target always requires multiple Vaults, which is the intended anti-turtle property, not an incidental side effect of the numbers.

**Minimap reveal reuses the stock `RevealsShroud` trait**, not new rendering code: the Vault has `RevealsShroud@GridReserveBeacon` with `ValidRelationships: Enemy` and `RequiresCondition: gridreserve-beacon`. `GridReserveVault` grants/revokes that condition each tick based on `GridReserveManager.BeaconActive` (Reserve ≥ 50% of target). This is the same condition-gated trait pattern already used throughout the engine (e.g. `GrantConditionOnDamageState`), so the reveal itself carries no bespoke visibility/rendering risk.

**Winning rides the existing `MissionObjectives` required-objective gate instead of touching `Player.WinState` directly.** Every player already has a `Required` objective from `ConquestVictoryConditions`. When a Lockdown countdown completes, `GridReserveController` force-completes *all* of that player's still-incomplete objectives (its own optional Grid Reserve objective and the Conquest one), which satisfies `MissionObjectives`' "all required objectives complete" check and triggers the normal `OnPlayerWon` path. `MissionObjectives.EarlyGameOver` is turned on for the `Player` template so that win immediately force-defeats the winner's enemies too — otherwise, opponents who are still alive would stay `WinState.Undefined` forever, since Grid Reserve's win path doesn't fit the "keep playing until you're eliminated" trigger natural to Conquest. This is a no-op for pure destruction games: by the time Conquest can complete, every opponent is already `Lost` through elimination.

Deliberate coupling worth flagging for reviewers: `GridReserveController` assumes every ruleset that enables the `gridreserve` checkbox also has a `Required` `MissionObjectives` objective configured (true for the default Sungrid Protocol `Player` template via `ConquestVictoryConditions`). A ruleset with Grid Reserve enabled and no other required objective would never resolve a Lockdown win. Team play is intentionally out of scope here too: a Lockdown win only resolves the triggering player, not their allies — consistent with alliance-split victory being explicitly deferred above.

**Issue #8's UI scope is now fully shipped.** In addition to the Lockdown start/cancel broadcast (system text line + `Speech` cue, unconditionally visible/audible to every player, not just the affected one) and the minimap reveal above, a persistent per-player Reserve bar (`GridReserveHudLogic`, `Container@GRID_RESERVE_HUD` in `ingame-player.yaml`) and a Reserve-totals scoreboard for observers (`GridReserveStandingsLogic`, `Container@GRID_RESERVE_STANDINGS` in `ingame-observer.yaml`) have since landed — both hide themselves via `controller.Enabled`/`IsVisible` when the mode is off, the same pattern used throughout this trait family.

**In-match rules briefing.** `GridReserveBriefingLogic` (`Container@GRID_RESERVE_BRIEFING` in `ingame-player.yaml`) shows a small, non-blocking popup once at match start summarizing the Core Rules above (deposits, irreversibility, multi-Vault requirement, destruction/sale forfeiture, minimap reveal at 50%) with a dismiss button, and hides itself entirely when the `gridreserve` checkbox is off. Added alongside the on-by-default change above so players who have never played a Grid Reserve match aren't dropped into it with no in-game explanation.
