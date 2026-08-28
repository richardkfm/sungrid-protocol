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
	[Desc("Attach to a Container in ingame-player.yaml to show the local player's own Grid Reserve",
		"progress (current / target) as a bar and label, and to warn when any opponent is holding",
		"Grid Lockdown. Hides itself when the Grid Reserve lobby option is off, so it is safe to",
		"include in the default HUD unconditionally.")]
	public class GridReserveHudLogic : ChromeLogic
	{
		[FluentReference("current", "target")]
		const string Tooltip = "label-grid-reserve-hud.tooltip";

		[FluentReference("seconds")]
		const string LockdownText = "label-grid-reserve-hud-lockdown.text";

		[FluentReference("seconds")]
		const string LockdownTooltip = "label-grid-reserve-hud-lockdown.tooltip";

		[FluentReference("seconds")]
		const string EnemyLockdownText = "label-grid-reserve-hud-enemy-lockdown.text";

		[FluentReference("player", "seconds")]
		const string EnemyLockdownTooltip = "label-grid-reserve-hud-enemy-lockdown.tooltip";

		[ObjectCreator.UseCtor]
		public GridReserveHudLogic(Widget widget, World world)
		{
			var player = world.LocalPlayer;
			var controller = world.WorldActor.TraitOrDefault<GridReserveController>();
			if (player == null || controller == null)
			{
				widget.IsVisible = () => false;
				return;
			}

			widget.IsVisible = () => controller.Enabled;

			var manager = player.PlayerActor.Trait<GridReserveManager>();
			var opponents = world.Players.Where(p => p != player && !p.NonCombatant && p.Playable).ToArray();
			var bar = widget.Get<ProgressBarWidget>("GRID_RESERVE_BAR");
			var label = widget.Get<LabelWithTooltipWidget>("GRID_RESERVE_LABEL");

			bar.GetPercentage = () => manager.Target > 0 ? Math.Min(100, manager.TotalReserve * 100 / manager.Target) : 0;

			// The soonest-to-complete opponent Lockdown, or null. The one-time start broadcast (see
			// GridReserveController.Broadcast) already reaches every player regardless of visibility, so
			// surfacing the same countdown persistently here leaks nothing new - it just replaces an
			// easy-to-miss text line with something a player actively fighting can actually keep an eye on.
			Player EnemyInLockdown()
			{
				Player soonest = null;
				var soonestRemaining = int.MaxValue;
				foreach (var opponent in opponents)
				{
					var remaining = controller.LockdownTicksRemaining(opponent);
					if (remaining >= 0 && remaining < soonestRemaining)
					{
						soonest = opponent;
						soonestRemaining = remaining;
					}
				}

				return soonest;
			}

			// Once Lockdown is counting down the current/target numbers stop changing (Reserve is held at
			// target while it holds), so swap the label to a countdown instead - otherwise the only sign a
			// countdown is even running is the one-time start broadcast, easy to miss mid-match. If it's an
			// opponent holding Lockdown rather than the local player, warn about that instead: without this,
			// a player who is actively fighting rather than watching the observer scoreboard (GridReserveStandingsLogic)
			// or spectating has no way to see an opponent's countdown running at all (issue #95).
			label.GetText = () =>
			{
				var remaining = controller.LockdownTicksRemaining(player);
				if (remaining >= 0)
					return FluentProvider.GetMessage(LockdownText, "seconds", SecondsRemaining(remaining, world).ToString(CultureInfo.CurrentCulture));

				var enemy = EnemyInLockdown();
				if (enemy != null)
					return FluentProvider.GetMessage(EnemyLockdownText, "seconds", SecondsRemaining(controller.LockdownTicksRemaining(enemy), world).ToString(CultureInfo.CurrentCulture));

				return string.Format(CultureInfo.CurrentCulture, "{0:N0} / {1:N0}", manager.TotalReserve, manager.Target);
			};
			label.GetColor = () =>
			{
				if (manager.LockdownEligible)
					return Color.LimeGreen;
				if (EnemyInLockdown() != null)
					return Color.OrangeRed;
				return Color.White;
			};
			label.GetTooltipText = () =>
			{
				var remaining = controller.LockdownTicksRemaining(player);
				if (remaining >= 0)
					return FluentProvider.GetMessage(LockdownTooltip, "seconds", SecondsRemaining(remaining, world).ToString(CultureInfo.CurrentCulture));

				var enemy = EnemyInLockdown();
				if (enemy != null)
					return FluentProvider.GetMessage(EnemyLockdownTooltip,
						"player", enemy.ResolvedPlayerName,
						"seconds", SecondsRemaining(controller.LockdownTicksRemaining(enemy), world).ToString(CultureInfo.CurrentCulture));

				return FluentProvider.GetMessage(Tooltip,
					"current", manager.TotalReserve.ToString(CultureInfo.CurrentCulture),
					"target", manager.Target.ToString(CultureInfo.CurrentCulture));
			};
		}

		// Rounded up so the last partial tick still reads as "1s" rather than "0s" before Lockdown completes.
		static int SecondsRemaining(int ticksRemaining, World world) => (ticksRemaining * world.Timestep + 999) / 1000;
	}
}
