# Sungrid Protocol — Building & Playtesting Guide

Step-by-step instructions to build, launch, and play a local Sungrid Protocol skirmish. This is the practical companion to [`docs/ARCHITECTURE.md`](ARCHITECTURE.md) (how the SDK/engine pinning works) — this doc is just "how do I get a match running on my machine."

The mod is playable today: `mods/sungrid` holds real Red Alert-derived gameplay (not the SDK's placeholder example content), including the full Phase 2/5 building roster and the Grid Reserve economic victory mode. See `CLAUDE.md`'s "Current status" for where the project stands.

This guide is for building from source. If you just want to play, download the pre-built package for your platform from the [Releases](https://github.com/richardkfm/sungrid-protocol/releases) page instead — no build step required.

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

## Headless / automated testing

For running a real build+launch smoke test in a container/CI-like environment with no pre-existing OpenRA install, no display, and possibly a network proxy that blocks `codeload.github.com`/GitHub release-asset downloads (used once for `docs/BACKLOG.md` issues #9/#10/#12's mechanical verification):

- **Engine fetch when `fetch-engine.sh`'s zip download is blocked:** shallow-clone the exact pinned commit instead: `git init && git remote add origin https://github.com/OpenRA/OpenRA.git && git fetch --depth 1 origin <ENGINE_VERSION-sha> && git checkout FETCH_HEAD` into `./engine`, then `rm -rf engine/.git` and write the version marker `fetch-engine.sh` checks for: `echo "<sha>" > engine/VERSION`. `make` will then see the version already matches and skip its own download.
- **`.NET` SDK missing entirely:** `sudo apt-get install -y dotnet-sdk-8.0` works on Ubuntu/Debian-based containers without extra package feeds.
- **`CS0121: ambiguous call between CryptoUtil.SHA1Hash(byte[]) and CryptoUtil.SHA1Hash(string)` at `Map.cs`'s `CryptoUtil.SHA1Hash([])` call — RESOLVED, no longer needs a manual patch.** This was a Roslyn overload-resolution quirk with newer `.NET 8` SDK patch versions (reproduced under SDK `8.0.128`, not present under `8.0.422`, the version upstream CI happens to use). Per `docs/BACKLOG.md` issue #20's RFC, `mod.config`'s `ENGINE_VERSION`/`AUTOMATIC_ENGINE_SOURCE` now point at a commit with this one line already fixed, so a normal `fetch-engine.sh`/`make` picks up the fix automatically — no local workaround needed anymore. Left here for context in case a *different* SDK-patch-dependent compile issue ever surfaces the same way.
- **No game content assets (`.mix` files):** the mod's `RequiredContentFiles`/`ContentPackages` need real Red Alert assets under `<SupportDir>/Content/ra/v2/`. OpenRA's official freeware `ra-quickinstall` package (~13MB, SHA1 `44241f68e69db9511db82cf83c174737ccda300b`, listed in the engine's `mods/ra-content/installer/downloads.yaml`) covers exactly what `mod.yaml` requires — download one of its mirrors (`https://www.openra.net/packages/ra-quickinstall-mirrors.txt` lists them; not every mirror is reachable through every proxy, try a few), verify the SHA1, and extract its `.mix`/`.aud` files into `<SupportDir>/Content/ra/v2/` (and `expand/`, `cnc/` subfolders) matching the paths in `mod.yaml`'s `ContentPackages`. **`<SupportDir>` on a Linux container running as root, confirmed by actually reading `Platform.cs`'s `InitializeSupportDir` and using it (not previously written down here): `$XDG_CONFIG_HOME/openra` if set, else `~/.config/openra`** — i.e. `~/.config/openra/Content/ra/v2/` in the common case. `OpenRA.Utility.dll`'s `--extract` command also resolves filenames through the mod's own virtual filesystem (`utility.ModData.DefaultFileSystem`), not a literal path, so `Mod=sungrid ./utility.sh --extract mouse.shp temperat.pal` (bare filenames, no `Content/ra/v2/` prefix) is the correct invocation once the above is in place — and note `utility.sh`/`launch-game.sh` both `cd` into `${ENGINE_DIRECTORY}` before running, so extracted files land in `engine/`, not the repo root or wherever the script was invoked from.
- **No display:** run under `Xvfb :99 -screen 0 1280x800x24 &` and `DISPLAY=:99` — OpenRA's SDL/OpenGL path works fine against Xvfb's software (llvmpipe) renderer. Capture a screenshot with `DISPLAY=:99 import -window root out.png` (ImageMagick). **Confirmed working end-to-end** (`docs/BACKLOG.md` issue #33): the actual client (`launch-game.sh`, not just `utility.sh`) launches, renders the main menu and the desert-tileset shellmap correctly under Xvfb's llvmpipe software renderer, and both are capturable with `import`. Two things worth knowing before repeating this:
  - The first-run "Establishing Battlefield Control" setup dialogs need clicking through once (no config file yet) — `xdotool mousemove <x> <y> click 1` against the same `DISPLAY` works fine for this since Xvfb has no real window manager to fight with. Screenshot first to find button coordinates (they match the captured image's pixel coordinates 1:1 when `Graphics.WindowedSize` matches the Xvfb screen size).
  - `import -window root` does **not** capture OpenRA's normal (SDL hardware) cursor — it's composited by the X server outside the captured framebuffer content. Launch with `Graphics.DisableHardwareCursors=true` to force the cursor to render as part of the game's own drawn scene if a screenshot needs to show it.
  - Loading straight into a temperate map via `Launch.Map=<uid>` (no bots) still reproduces the exact black-viewport limitation described below — sidebar/build palette render fine, but there's no shroud-clearing without a real skirmish, confirming this is inherent to the no-bots quick-load path, not an environment or rendering problem.
- **Headlessly starting a bot-filled skirmish (no UI automation) — patch built and actually run to completion for the first time (docs/BACKLOG.md issue #49):** OpenRA has no built-in CLI flag for this — `Launch.Map=<uid>` only loads a map with the single connecting client, no bots (`ServerType.Local`, not `Skirmish`), and the real `isSkirmish: true` path is only reachable from `MainMenuLogic.StartSkirmishGame`'s UI button. A temporary, **local-only, never-committed** patch to the gitignored `engine/` adds a `Launch.SkirmishBots=<comma-separated bot types>` flag that creates a real Skirmish-type server and starts the match — see `Game.LoadSkirmishWithBots` (new method, mirrors the existing `Game.LoadMap`), `LaunchArguments.SkirmishBots` (new field), and `BlankLoadScreen.StartGame` (new branch before the existing `Launch.Map` handling) if this needs reapplying. Bot type ids come from `mods/sungrid/rules/ai.yaml`'s `ModularBot@*` entries (`rush`, `normal`, `turtle`, `naval`). Example: `Launch.Map=<uid> Launch.SkirmishBots=normal,normal,turtle`.
  - **Wait for the join handshake before issuing `state Ready`.** The first cut of this patch fired `slot_bot`/`state Ready` on the very first `Game.LobbyInfoChanged` event, which can race the server's own connection-accept slot assignment (`Server.cs`: `client.Slot = LobbyInfo.FirstEmptySlot()`) and start the match with the human client itself unplaced — no start position, no vision, no build queue, and the match auto-starts almost immediately since `EnableSingleplayer` is true for any non-dedicated server. Guard on `botController.Slot != null && lobbyInfo.Slots.Count > 0` before acting.
  - **`SkirmishLogic`'s own `IClientJoined` handler restores a previous session's bot roster automatically**, or falls back to auto-filling one slot with the ruleset's first-registered bot type (`rush`, alphabetically/registration-order first in `mods/sungrid/rules/ai.yaml`) if no `SkirmishSettings` exist yet — this happens server-side before the client-side patch's own `slot_bot` calls run, so don't assume every empty slot the patch sees is actually yours to fill with your requested types; log `lobbyInfo.Clients`/`Slots` before assuming.
  - **Confirmed this now genuinely works, not just compiles:** a real 4-player match (1 human + 3 bots) ran to conclusion — `Tab` in-game shows a real objectives/score panel with distinct bot scores, confirming actual gameplay (economy, combat) happened, not just a lobby handshake.
  - **Still open, and still the real blocker for a live camera screenshot:** even with the human client correctly slotted, `SpawnStartingUnitsInfo.SpawnUnitsForPlayer` genuinely placing a base actor at the correct non-zero `HomeLocation` (confirmed via an added `Console.WriteLine` — `Playable=True`, `HomeLocation=<real cell>`), and the viewport explicitly re-centered on that location (`wr.Viewport.Center(world.Map.CenterOfCell(world.LocalPlayer.HomeLocation))`, called from `SpawnStartingUnits.WorldLoaded` since it's the first hook with both a loaded world and a `WorldRenderer`), the battlefield still renders fully black. `World.RenderPlayer` does correctly resolve to the local player (via `World.SetLocalPlayer` setting the backing field directly, which `ShroudRenderer.WorldLoaded`'s own `WorldOnRenderPlayerChanged(world.RenderPlayer)` call picks up) — so the renderer is asking the right player's `Shroud` for visibility, but that `Shroud` reports nothing explored/visible despite the player owning a real actor there. Root cause not found — plausibly some vision/shroud-tick catch-up that the interactive lobby's own connect/start sequence triggers and this headless path skips, but that's a guess, not a diagnosis. Correctly scoped as its own follow-up (third time this exact blocker has been deferred, after issues #18 and #33) rather than another open-ended debugging pass in the same session.
  - This patch's usefulness doesn't depend on solving the above: it's sufficient to drive a real bot-vs-bot(-vs-human) match to a real conclusion for mechanical verification (rules loading, AI, win conditions), which is what issues #9/#33's own headless verification already relied on. The remaining gap is specifically "screenshot what a temperate/desert battlefield looks like from the human player's camera."
- **Getting a map UID:** `./utility.sh --map-hash <path/to/map-dir-or-.oramap>` (run from the repo root; use a path relative to `engine/` if invoked directly via `dotnet engine/bin/OpenRA.Utility.dll`).
- This whole workflow is disposable: `engine/` is gitignored and rebuilt from the pinned commit every time, so none of the above (including the `Launch.SkirmishBots` patch) persists or needs cleanup beyond deleting the directory.
