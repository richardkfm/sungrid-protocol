#region Copyright & License Information
/*
 * Copyright (c) The OpenRA Developers and Contributors
 * This file is part of OpenRA, which is free software. It is made
 * available to you under the terms of the GNU General Public License
 * as published by the Free Software Foundation, either version 3 of
 * the License, or (at your option) any later version. For more
 * information, see COPYING.
 */
#endregion

using System.Collections.Generic;
using System.Linq;
using OpenRA.Mods.Common.Traits;
using OpenRA.Traits;

namespace OpenRA.Mods.Sungrid.GridReserve
{
	[TraitLocation(SystemActors.World)]
	[Desc("Implements the Grid Reserve economic victory mode: the Grid Lockdown hold-to-win countdown,",
		"anti-stalemate Grid Decay, and the lobby toggle. Requires GridReserveManager on every Player actor,",
		"and relies on each player already having a Required MissionObjectives objective (ConquestVictoryConditions",
		"in the default Sungrid Protocol ruleset) to actually resolve the win - see docs/GAME_MODES.md.")]
	public class GridReserveControllerInfo : TraitInfo, ILobbyOptions
	{
		[FluentReference]
		[Desc("Descriptive label for the Grid Reserve checkbox in the lobby.")]
		public readonly string CheckboxLabel = "checkbox-gridreserve.label";

		[FluentReference]
		[Desc("Tooltip description for the Grid Reserve checkbox in the lobby.")]
		public readonly string CheckboxDescription = "checkbox-gridreserve.description";

		[Desc("Default value of the Grid Reserve checkbox in the lobby. Off by default: destruction victory is never at risk of feeling deprecated.")]
		public readonly bool CheckboxEnabled = false;

		[Desc("Prevent the Grid Reserve state from being changed in the lobby.")]
		public readonly bool CheckboxLocked = false;

		[Desc("Whether to display the Grid Reserve checkbox in the lobby.")]
		public readonly bool CheckboxVisible = true;

		[Desc("Display order for the Grid Reserve checkbox in the lobby.")]
		public readonly int CheckboxDisplayOrder = 0;

		[Desc("Description of the Grid Reserve objective, shown in the mission objectives panel.")]
		public readonly string Objective = "Bank enough Grid Reserve across your Vaults and hold Grid Lockdown to win.";

		[Desc("Ticks the Reserve total must stay at or above target to win once Grid Lockdown starts (60-120s at normal speed recommended).")]
		public readonly int LockdownDurationTicks = 2250;

		[Desc("Ticks after the match starts before Grid Decay can begin, if nobody has triggered Grid Lockdown yet.")]
		public readonly int DecayGraceTicks = 45000;

		[Desc("How often (in ticks) Grid Decay reduces Reserve once active.")]
		public readonly int DecayIntervalTicks = 1500;

		[Desc("Percentage (0-100) of each Vault's Reserve removed per Grid Decay interval once active.")]
		public readonly int DecayPercent = 1;

		[NotificationReference("Speech")]
		public readonly string LockdownStartNotification = null;

		[FluentReference(optional: true)]
		public readonly string LockdownStartTextNotification = null;

		[NotificationReference("Speech")]
		public readonly string LockdownCancelledNotification = null;

		[FluentReference(optional: true)]
		public readonly string LockdownCancelledTextNotification = null;

		IEnumerable<LobbyOption> ILobbyOptions.LobbyOptions(MapPreview map)
		{
			yield return new LobbyBooleanOption(map, "gridreserve",
				CheckboxLabel, CheckboxDescription, CheckboxVisible, CheckboxDisplayOrder, CheckboxEnabled, CheckboxLocked);
		}

		public override object Create(ActorInitializer init) { return new GridReserveController(this); }
	}

	public class GridReserveController : ITick, INotifyCreated
	{
		readonly GridReserveControllerInfo info;
		readonly HashSet<Player> objectiveAdded = [];
		readonly Dictionary<Player, int> lockdownRemaining = [];

		bool anyLockdownEverTriggered;
		int elapsedTicks;
		Player[] players;

		// Exposes the resolved lobby toggle for HUD widgets (GridReserveHudLogic, GridReserveStandingsLogic)
		// so they can hide themselves in matches where the mode is off, without re-parsing lobby options.
		public bool Enabled { get; private set; }

		public GridReserveController(GridReserveControllerInfo info)
		{
			this.info = info;
		}

		void INotifyCreated.Created(Actor self)
		{
			Enabled = self.World.LobbyInfo.GlobalSettings.OptionOrDefault("gridreserve", info.CheckboxEnabled);
		}

		void ITick.Tick(Actor self)
		{
			if (!Enabled)
				return;

			// Players and NonCombatants are fixed once the game starts, so this can be cached lazily.
			players ??= self.World.Players.Where(p => !p.NonCombatant && p.Playable).ToArray();
			if (players.Length == 0)
				return;

			elapsedTicks++;

			if (!anyLockdownEverTriggered && elapsedTicks >= info.DecayGraceTicks && elapsedTicks % info.DecayIntervalTicks == 0)
				foreach (var decayPlayer in players)
					decayPlayer.PlayerActor.Trait<GridReserveManager>().ApplyDecay(info.DecayPercent);

			foreach (var player in players)
			{
				if (player.WinState != WinState.Undefined)
					continue;

				var manager = player.PlayerActor.Trait<GridReserveManager>();
				var mo = player.PlayerActor.Trait<MissionObjectives>();

				if (objectiveAdded.Add(player))
					mo.Add(player, info.Objective, "Secondary", required: false, inhibitAnnouncement: true);

				var remaining = lockdownRemaining.TryGetValue(player, out var r) ? r : -1;

				if (manager.LockdownEligible)
				{
					if (remaining < 0)
					{
						lockdownRemaining[player] = info.LockdownDurationTicks;
						anyLockdownEverTriggered = true;
						Broadcast(self.World, player, info.LockdownStartNotification, info.LockdownStartTextNotification);
					}
					else if (remaining <= 1)
					{
						lockdownRemaining.Remove(player);
						CompleteGridReserveVictory(mo, player);
					}
					else
						lockdownRemaining[player] = remaining - 1;
				}
				else if (remaining >= 0)
				{
					lockdownRemaining.Remove(player);
					Broadcast(self.World, player, info.LockdownCancelledNotification, info.LockdownCancelledTextNotification);
				}
			}
		}

		static void CompleteGridReserveVictory(MissionObjectives mo, Player winner)
		{
			// Grid Reserve rides the existing MissionObjectives required-objective gate: force-completing the
			// winner's other pending required objectives (i.e. ConquestVictoryConditions' "destroy all opposition")
			// is what actually resolves player.WinState and ends the match through the engine's normal win path,
			// rather than reaching into WinState/OnPlayerWinStateChanged plumbing directly.
			for (var id = 0; id < mo.Objectives.Count; id++)
				if (mo.Objectives[id].State == ObjectiveState.Incomplete)
					mo.MarkCompleted(winner, id);
		}

		static void Broadcast(World world, Player player, string speechNotification, string textNotification)
		{
			if (textNotification != null)
				TextNotificationsManager.AddSystemLine(textNotification, "player", player.ResolvedPlayerName);

			if (speechNotification != null)
				Game.Sound.PlayNotification(world.Map.Rules, player, "Speech", speechNotification, player.Faction.InternalName);
		}
	}
}
