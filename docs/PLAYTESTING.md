# Sungrid Protocol — Building & Playtesting Guide

Step-by-step instructions to build, launch, and play a local Sungrid Protocol skirmish. This is the practical companion to [`docs/ARCHITECTURE.md`](ARCHITECTURE.md) (how the SDK/engine pinning works) — this doc is just "how do I get a match running on my machine."

The mod is playable today: `mods/sungrid` holds real Red Alert-derived gameplay (not the SDK's placeholder example content), including the full Phase 2/5 building roster and the Grid Reserve economic victory mode. See `CLAUDE.md`'s "Current status" for where the project stands.

## Prerequisites

- **.NET SDK** matching the engine's target (currently `net8.0`). If your distro only ships a newer major version (common on rolling-release distros like Arch/CachyOS, which track only the latest .NET), see the roll-forward workaround below rather than assuming you need to downgrade.
- **git**, and on Linux a working OpenGL/SDL2 stack (already present on most desktop installs).
- No manual engine download needed — `make`/`make.cmd` calls `fetch-engine.sh`/`.cmd` automatically, which fetches and pins the exact engine commit named in `mod.config`'s `ENGINE_VERSION`.

## Build

- **Linux/macOS:** `make`
- **Windows:** `make.cmd`

This fetches the pinned engine into `engine/` (gitignored — never commit or hand-edit it) and compiles `OpenRA.Mods.Sungrid.dll` plus the engine assemblies. Re-run `make` after pulling changes that touch `OpenRA.Mods.Sungrid/` or `mod.config`'s `ENGINE_VERSION`.

## Launch

- **Linux/macOS:** `./launch-game.sh`
- **Windows:** `launch-game.cmd`

This should bring up the OpenRA main menu with "Sungrid Protocol" as the mod (not "Red Alert"). From there: **Skirmish** → add AI/human slots → **Start Game**.

### `.NET` runtime mismatch ("You must install or update .NET to run this application")

If the error names a version you don't have installed (e.g. asks for `8.0.0` but `dotnet --list-runtimes` shows something newer, like `10.0.9`), you almost never need to install an older runtime side-by-side — let the newer major runtime roll forward instead:

```sh
DOTNET_ROLL_FORWARD=LatestMajor ./launch-game.sh
```

This works because the app targets `net8.0` but is compatible with newer majors; it's the standard fix on distros that only package the latest .NET. Only fall back to installing a matching runtime (`sudo pacman -S dotnet-runtime-8.0` / `paru -S dotnet-runtime-8.0-bin` on Arch-based distros, or the equivalent for your package manager) if the roll-forward flag doesn't resolve it.

## Debugging a crash

If the game crashes on startup, on entering a map, or mid-match, the full exception and stack trace print to **the terminal you launched from** — not to the log files under `~/.config/openra/Logs/<mod>/` (or the platform equivalent). Those logs (`install.log`, `lua.log`, `nat.log`, `perf.log`, `server.log`, `sound.log`) cover other subsystems and usually won't contain a rules-loading or widget-rendering crash.

To capture a crash for a bug report, redirect and tee stdout/stderr instead of relying on the log directory:

```sh
DOTNET_ROLL_FORWARD=LatestMajor ./launch-game.sh 2>&1 | tee /tmp/sungrid-crash.txt
```

Then search the captured file, e.g. `grep -i exception /tmp/sungrid-crash.txt`.

## Known-good local playtest

A full skirmish (build queue, Recycling Depot, Grid Reserve HUD bar, Phase 5 buildings including Smart Grid Relay) has been confirmed working end-to-end on CachyOS as of `main`'s current tip. If you hit a crash that isn't covered above, it's likely a new regression, not a known/expected gap — check `docs/BACKLOG.md` for open issues before assuming it's environment-specific, and capture the terminal output per the section above when reporting it.

## Playing a skirmish

- **Grid Reserve** (the economic victory mode) is a per-lobby toggle in the Skirmish setup screen — destruction victory (eliminate all opponents) remains the default and is always available regardless of the toggle. See [`docs/GAME_MODES.md`](GAME_MODES.md) for the full mechanic.
- The Grid Reserve HUD bar (top of screen, `current / target`) only appears when the mode is enabled for that match.
- 3+ player matches are the design target for Grid Reserve balance — see `docs/BACKLOG.md` issue #9 for the open structured-playtest task if you're testing multiplayer dynamics specifically, not just solo build-order checks.

## Multiplayer / dedicated server

Use `launch-dedicated.sh` (`.cmd` on Windows) to host a headless dedicated server instead of a local skirmish. Not yet covered by a structured external-playtest package (see `docs/BACKLOG.md` issue #10) — treat this as LAN/direct-connect only for now.
