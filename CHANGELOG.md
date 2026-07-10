# Changelog

All notable changes to Sungrid Protocol are logged here, one entry per merged PR, grouped by phase. Written in plain language for playtesters, not raw commit messages.

## Phase 1 — Baseline playable shell

- Replaced the OpenRA Mod SDK's placeholder example content in `mods/sungrid` with real gameplay forked from `mods/ra` (pinned engine commit `bf4102a`): the full Red Alert ruleset (structures, vehicles, infantry, aircraft, ships, weapons, AI), classic sprite/audio formats, and 75 real maps (a main-menu shellmap plus 74 multiplayer/skirmish maps).
- The mod still identifies itself as "Sungrid Protocol" in the title bar and OpenRA mod chooser; only the gameplay data underneath is (for now) unmodified Red Alert content, running under the `sungrid` mod id instead of `ra`.
- No new buildings, mechanics, or art — this phase is plumbing, not content. Solarpunk reskinning starts in Phase 2.
