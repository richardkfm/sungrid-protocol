# Sungrid Protocol — Beta Tester Guide

Thanks for testing. Sungrid Protocol is a solarpunk take on classic Red Alert, built on the OpenRA engine. You
build a base, fight, raid and scout like in any classic RTS, and you can also win by saving: bank enough Credits
in your Battery Banks, then hold them for 90 seconds (the **Grid Reserve** mode).

This page covers everything a tester needs: install, play, and report. It is the page the game's crash dialog
opens when you click "View FAQ".

**Quick links:** [Install](#1-install) · [First launch](#2-first-launch-game-content) ·
[Play together](#3-playing-together) · [Report a bug](#4-reporting-a-problem) ·
[Crashes](#if-the-game-crashes) · [Feedback](#5-giving-feedback) · [Known issues](#6-known-issues--please-dont-report-these)

---

## 1. Install

Download the package for your system from the
[Releases page](https://github.com/richardkfm/sungrid-protocol/releases). Take the **newest** release unless someone
you are playing with tells you otherwise — everyone in a match must run the exact same version (see
[Playing together](#3-playing-together)).

| System | File | Notes |
|---|---|---|
| Windows (most PCs) | `SungridProtocol-<version>-x64.exe` | Installer. `-x64-winportable.zip` is the no-install alternative. |
| Windows (32-bit) | `SungridProtocol-<version>-x86.exe` | Only if your Windows is 32-bit. |
| macOS | `SungridProtocol-<version>.dmg` | Open it and drag **Sungrid Protocol** into Applications. |
| Linux | `SungridProtocol-<version>-x86_64.AppImage` | Make it executable (`chmod +x`, or Properties → Permissions), then run it. |

**Security warnings are expected.** This is a hobby project without the paid developer certificates that silence
them, so your system may warn you that the app comes from an unknown developer:

- **Windows SmartScreen** ("Windows protected your PC"): click **More info → Run anyway**.
- **macOS** ("cannot be opened because the developer cannot be verified", or "is damaged"): open
  **System Settings → Privacy & Security**, scroll down and click **Open Anyway** next to the Sungrid Protocol
  message. If macOS says the app "is damaged", run `xattr -dr com.apple.quarantine "/Applications/Sungrid Protocol.app"`
  in Terminal once, then open it again.

Only download the game from the Releases page linked above.

## 2. First launch: game content

Sungrid Protocol reuses some of the original Red Alert files (sounds, terrain, the classic units). EA released
Red Alert as freeware, but the game can't ship those files itself. On the first launch you get a
**content installer**:

- Choose **Quick Install** / download — it fetches the official freeware package (~13 MB) and sets everything up.
  This is the easiest option and needs no purchase.
- Alternatively, install from an original Red Alert disc, or a Steam/Origin copy of the C&C Ultimate Collection.

It is a one-time step. **Please tell us how it went** — this has never been checked on a fresh computer, which is
exactly what we need from you. A two-line comment in your feedback ("worked first try", or "got stuck at …") is
enough. If it failed, file a [bug report](#4-reporting-a-problem).

## 3. Playing together

- **Everyone must run the same release.** Two different versions can't see each other's games at all — the game
  isn't greyed out, it simply doesn't appear. The version is shown in the main menu.
- **Grid Reserve** is on by default. Destruction victory (eliminate everyone) always works too. A popup explains
  the rules at the start of a match.
- **3 or more players is what we most need to test.** Bots are fine for filling slots; **Easy Grid Broker AI** is
  the beginner opponent, **Grid Broker AI** plays the economic win hard.

### Same network (LAN)

The host clicks **Multiplayer → Create**. The others open **Multiplayer**; the game appears in the list.
If it doesn't, use **Direct IP** with the host's local address (for example `192.168.1.20`) and port `1234`.

Please tell us whether joining over LAN actually worked — so far we have only confirmed that a LAN game *shows up*
on a second machine.

### Over the internet — use a VPN (recommended for this beta)

**Known issue:** hosting a game for friends over the internet via the public server list has not worked yet in
our own tests (the game did not appear in the list, and connecting directly also failed). Until that's solved,
the reliable way to play together from different homes is a free mesh VPN, which makes your computers behave as
if they were on the same network:

1. Everyone installs the same VPN — [Tailscale](https://tailscale.com) or [ZeroTier](https://www.zerotier.com)
   both work — and joins the host's network.
2. The host starts the game and clicks **Multiplayer → Create**.
3. Everyone else clicks **Multiplayer → Direct IP** and enters the **host's VPN address** (Tailscale: the
   `100.x.y.z` address shown in the Tailscale app) and port `1234`. The server list may not show games over a VPN —
   use Direct IP.

**Windows hosts:** the first time you create a server, Windows Firewall asks whether to allow the game. Allow it.
VPN connections often count as a *public* network on Windows, so tick **both** private and public, or players
won't get through.

### Over the internet without a VPN (helps us fix the known issue)

If you want to try the normal way and help us diagnose it:

1. On the host's router, forward **TCP port 1234** to the host computer — or enable
   **Settings → Advanced → Enable UPnP/NAT-PMP Discovery** in the game if your router supports it (restart
   the game afterwards).
2. Allow the game through the host's firewall.
3. Create the server with "Advertise Online" on, and **read the lobby chat right after hosting**. The game checks
   whether it can be reached from outside and says so there — e.g. *"Server port is not accessible from the
   internet."*
4. Report the result with the **Multiplayer / connection problem** form, and attach the host's `server.log`
   (see [where the files are](#where-the-files-are)). The line starting `Master server:` is the one we need.

If your internet provider uses carrier-grade NAT (common on mobile, some cable and fibre plans), port forwarding
can't work from your side at all — that's what the VPN route avoids.

## 4. Reporting a problem

Reports go to [GitHub Issues](https://github.com/richardkfm/sungrid-protocol/issues/new/choose) (a free GitHub
account is needed). Pick the form that fits:

- **Bug report** — something behaves wrong, looks broken, or doesn't match its description.
- **Crash report** — the game closed or showed an error dialog.
- **Multiplayer / connection problem** — can't see, join, or stay in a game; "out of sync".
- **Playtest feedback** — after a match: what was fun, what felt unfair or broken.

Search the existing issues first; if yours is already there, a comment with your details helps more than a new
issue. Always include the **version** (main menu) and your **operating system**.

### If the game crashes

The game writes a crash log automatically. It's named `exception-<date>.log` and lives in the `Logs` folder
([where the files are](#where-the-files-are)). If a crash dialog appears, **View Logs** opens that folder
directly. Attach the newest `exception-*.log` to a **Crash report**.

If the game says **"Out of sync"** during a multiplayer match, *every* player should attach their newest
`syncreport-*.log` from the same folder — we need the files from all sides to compare.

### Replays help a lot

Every match is recorded automatically. If something went wrong mid-match, attach the replay: zip the `.orarep`
file (GitHub won't take it unzipped) and drag the zip into the issue. You can also watch it yourself from
**Main menu → Extras → Replays**.

### Where the files are

| System | Folder |
|---|---|
| Windows | `%APPDATA%\OpenRA\` (paste into the Explorer address bar) |
| macOS | `~/Library/Application Support/OpenRA/` (Finder → Go → Go to Folder…) |
| Linux | `~/.config/openra/` (older setups: `~/.openra/`) |

Inside it:

- `Logs/` — `exception-*.log` (crashes), `syncreport-*.log` (out-of-sync), `server.log` (hosting).
- `Replays/sungrid/<version>/` — your recorded matches.
- `Content/ra/v2/` — the Red Alert files the content installer set up.

## 5. Giving feedback

The single most useful thing you can do is play a full match with **three or more human players** and fill in
the **Playtest feedback** form afterwards. It asks, among other things:

- Did anyone reach **Grid Lockdown** (the 90-second hold)? Did anyone win that way?
- Did someone try to **raid** a Battery Bank to break a Lockdown — and did it work?
- Could a player win by just hiding and saving, without being threatened?
- Did anything feel clearly overpowered or useless (drones, the Cryptominer, a specific defence)?
- Was it clear what each building does, and what the Grid Reserve bar at the top meant?

Bot matches are welcome too, but human-vs-human matches are what we can't produce ourselves.

## 6. Known issues — please don't report these

These are known and planned; reports about them won't change anything yet:

- **Most units still look and sound like classic Red Alert.** Tanks, infantry, ships and aircraft use the
  original art, voices and in-game music. Only Sungrid's own buildings, drones, the Hauler Drone, the Arc Turret
  and the Disruptor Trooper's weapon are new. A unit and audio pass comes after beta.
- **Terrain is recoloured Red Alert terrain.** Solarpunk scenery (solar farms, salvage piles, greenery on the
  map) comes later.
- **Internet play via the server list doesn't work yet** — use a VPN, see
  [Playing together](#over-the-internet--use-a-vpn-recommended-for-this-beta). Diagnostic reports *are* welcome.
- **Security warnings on install** — see [Install](#1-install).
- **Numbers aren't final.** Costs, Grid Reserve targets and AI behaviour are reasoned, not yet measured against
  real matches — telling us what felt off is exactly what feedback is for.

Everything else that looks wrong, please report.
