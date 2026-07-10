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
5. **Toggle.** Grid Reserve is a lobby option, off by default at first release, so destruction victory is never at risk of feeling deprecated.

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
