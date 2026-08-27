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

using System;
using System.Globalization;
using System.Linq;
using OpenRA.Mods.Common.Widgets;
using OpenRA.Primitives;
using OpenRA.Widgets;

namespace OpenRA.Mods.Sungrid.GridReserve
{
	[Desc("Attach to a Container in ingame-observer.yaml to list every active player's Grid Reserve",
		"total against the match target. Observers (including players who have finished the match",
		"and dropped to spectating, per MissionObjectives' EarlyGameOver) can use this as the",
		"end-of-match Reserve scoreboard regardless of which victory condition ended the game.",
		"Expects MaxRows Container children named ROW_0.. each with NAME/AMOUNT labels and a BAR.",
		"Hides itself when the Grid Reserve lobby option is off.")]
	public class GridReserveStandingsLogic : ChromeLogic
	{
		[FluentReference("seconds")]
		const string LockdownText = "label-grid-reserve-hud-lockdown.text";

		const int MaxRows = 8;

		[ObjectCreator.UseCtor]
		public GridReserveStandingsLogic(Widget widget, World world)
		{
			var controller = world.WorldActor.TraitOrDefault<GridReserveController>();
			if (controller == null)
			{
				widget.IsVisible = () => false;
				return;
			}

			widget.IsVisible = () => controller.Enabled;

			var players = world.Players.Where(p => !p.NonCombatant && p.Playable).ToArray();

			for (var i = 0; i < MaxRows; i++)
			{
				var row = widget.GetOrNull<ContainerWidget>("ROW_" + i.ToString(CultureInfo.InvariantCulture));
				if (row == null)
					continue;

				if (i >= players.Length)
				{
					row.IsVisible = () => false;
					continue;
				}

				var player = players[i];
				var manager = player.PlayerActor.Trait<GridReserveManager>();

				var name = row.Get<LabelWidget>("NAME");
				name.GetText = () => player.ResolvedPlayerName;
				name.GetColor = () => player.Color;

				var amount = row.Get<LabelWidget>("AMOUNT");

				// Mirrors GridReserveHudLogic: once this player is holding Grid Lockdown the current/target
				// numbers stop changing (Reserve is held at target), so swap to the countdown instead - an
				// observer watching the standings otherwise has no way to see how much longer the hold lasts.
				amount.GetText = () =>
				{
					var remaining = controller.LockdownTicksRemaining(player);
					if (remaining >= 0)
						return FluentProvider.GetMessage(LockdownText, "seconds", SecondsRemaining(remaining, world).ToString(CultureInfo.CurrentCulture));

					return string.Format(CultureInfo.CurrentCulture, "{0:N0} / {1:N0}", manager.TotalReserve, manager.Target);
				};
				amount.GetColor = () => manager.LockdownEligible ? Color.LimeGreen : player.Color;

				var bar = row.Get<ProgressBarWidget>("BAR");
				bar.GetPercentage = () => manager.Target > 0 ? Math.Min(100, manager.TotalReserve * 100 / manager.Target) : 0;
			}
		}

		// Rounded up so the last partial tick still reads as "1s" rather than "0s" before Lockdown completes.
		static int SecondsRemaining(int ticksRemaining, World world) => (ticksRemaining * world.Timestep + 999) / 1000;
	}
}
