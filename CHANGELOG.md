# Changelog

All notable changes to Sungrid Protocol are logged here, one entry per merged PR, grouped by phase. Written in plain language for playtesters, not raw commit messages.

## Phase 1 — Baseline playable shell

- Replaced the OpenRA Mod SDK's placeholder example content in `mods/sungrid` with real gameplay forked from `mods/ra` (pinned engine commit `bf4102a`): the full Red Alert ruleset (structures, vehicles, infantry, aircraft, ships, weapons, AI), classic sprite/audio formats, and 75 real maps (a main-menu shellmap plus 74 multiplayer/skirmish maps).
- The mod still identifies itself as "Sungrid Protocol" in the title bar and OpenRA mod chooser; only the gameplay data underneath is (for now) unmodified Red Alert content, running under the `sungrid` mod id instead of `ra`.
- No new buildings, mechanics, or art — this phase is plumbing, not content. Solarpunk reskinning starts in Phase 2.

## Ongoing — tone/content fixes

- Removed Flame Infantry (`E4`) and the Flame Tower (`FTUR`), along with their dedicated `Flamer`/`FireballLauncher` weapons, per a tone call that immolation weapons don't fit the project — see `docs/BACKLOG.md` issue #14. AI build orders, defense/protection lists, and a shellmap paratrooper drop table updated to match; no other unit depended on the removed weapons (the Giant Ant's fireball attack was re-based directly on the shared `^FireWeapon` template it and `FireballLauncher` both descended from, rather than losing its base).
