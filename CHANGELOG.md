# Changelog

All notable changes to Sungrid Protocol are logged here, one entry per merged PR, grouped by phase. Written in plain language for playtesters, not raw commit messages.

## Phase 1 — Baseline playable shell

- Replaced the OpenRA Mod SDK's placeholder example content in `mods/sungrid` with real gameplay forked from `mods/ra` (pinned engine commit `bf4102a`): the full Red Alert ruleset (structures, vehicles, infantry, aircraft, ships, weapons, AI), classic sprite/audio formats, and 75 real maps (a main-menu shellmap plus 74 multiplayer/skirmish maps).
- The mod still identifies itself as "Sungrid Protocol" in the title bar and OpenRA mod chooser; only the gameplay data underneath is (for now) unmodified Red Alert content, running under the `sungrid` mod id instead of `ra`.
- No new buildings, mechanics, or art — this phase is plumbing, not content. Solarpunk reskinning starts in Phase 2.

## Ongoing — tone/content fixes

- Replaced Flame Infantry (`E4`) and the Flame Tower (`FTUR`) with the Disruptor Trooper (`DISR`) and the Arc Turret (`ARCT`) — a tone call that immolation weapons don't fit the project, per `docs/BACKLOG.md` issue #14. Same cost, stats, tech-tier slot, and chassis art as the units they replace; only the weapon changed, from fire (`Flamer`/`FireballLauncher`) to a grid-current disruptor (`Disruptor`/`ArcDischarge`) with equivalent damage numbers. AI build orders, defense/protection lists, and a shellmap paratrooper drop table updated to reference the new units; no other unit depended on the old weapons (the Giant Ant's fireball attack was re-based directly on the shared `^FireWeapon` template it and `FireballLauncher` both descended from, rather than losing its base).
- First-boot menu/intro pass, per `docs/BACKLOG.md` issue #15: fixed a regression where the main-menu shellmap still placed the removed Flame Tower (`ftur`) in six spots (would have broken the main menu background entirely); replaced the window/taskbar/mod-chooser icon (a literal, unmodified stock Soviet star and hammer-and-sickle) with the Phase 6 emblem; reworded two off-theme loading-screen tips. Main menu widget layout, cursors, terrain, the shellmap's own terrain, and the main menu's music are still stock — tracked as open follow-up in the same issue, blocked on either a built engine or Phase 7's audio pass.
