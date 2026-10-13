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
using OpenRA.Mods.Common.Widgets;
using OpenRA.Mods.Sungrid.GridReserve;
using OpenRA.Primitives;
using OpenRA.Widgets;

namespace OpenRA.Mods.Sungrid.SunCycle
{
	[Desc("Attach to a Container in ingame-player.yaml to show the time of day, the time to the next phase and the",
		"local player's stored Battery Bank charge. Hides itself when the suncycle lobby option is off, so it is",
		"safe to include in the default HUD unconditionally. Sits under the Grid Reserve bar, and moves up into",
		"its slot when Grid Reserve is off.")]
	public class SunCycleHudLogic : ChromeLogic
	{
		[FluentReference]
		const string Day = "label-sun-cycle-phase.day";

		[FluentReference]
		const string Dusk = "label-sun-cycle-phase.dusk";

		[FluentReference]
		const string Night = "label-sun-cycle-phase.night";

		[FluentReference]
		const string Dawn = "label-sun-cycle-phase.dawn";

		[FluentReference("phase", "next", "time", "percent")]
		const string Text = "label-sun-cycle-hud.text";

		[FluentReference("solar", "banks", "stored", "capacity", "flow", "reserve")]
		const string Tooltip = "label-sun-cycle-hud.tooltip";

		[FluentReference("rate")]
		const string Charging = "label-sun-cycle-hud-flow.charging";

		[FluentReference("rate")]
		const string Discharging = "label-sun-cycle-hud-flow.discharging";

		[FluentReference]
		const string Idle = "label-sun-cycle-hud-flow.idle";

		[ObjectCreator.UseCtor]
		public SunCycleHudLogic(Widget widget, World world)
		{
			var player = world.LocalPlayer;
			var controller = world.WorldActor.TraitOrDefault<SunCycleController>();
			var storage = player?.PlayerActor.TraitOrDefault<PowerStorageManager>();
			if (player == null || controller == null || storage == null || !controller.Enabled)
			{
				widget.IsVisible = () => false;
				return;
			}

			// Grid Reserve off: its bar is hidden, so take its slot instead of leaving a gap above this one.
			var gridReserve = world.WorldActor.TraitOrDefault<GridReserveController>();
			if (gridReserve == null || !gridReserve.Enabled)
				widget.Bounds.Y = widget.Bounds.Y - widget.Bounds.Height - 4;

			var textColor = ChromeMetrics.Get<Color>("SunCycleDayColor");
			var twilightColor = ChromeMetrics.Get<Color>("SunCycleTwilightColor");
			var nightColor = ChromeMetrics.Get<Color>("SunCycleNightColor");

			var label = widget.Get<LabelWithTooltipWidget>("SUN_CYCLE_LABEL");
			var bar = widget.Get<ProgressBarWidget>("SUN_CYCLE_BAR");

			// Percent of the charge the banks can hold *now*: space Grid Reserve credits already fill is not
			// room for charge, and a bar that could never reach 100% would read as a fault.
			int ChargePercent()
			{
				var max = storage.TotalMaxCharge;
				return max > 0 ? Math.Clamp((int)((long)storage.TotalCharge * 100 / max), 0, 100) : 0;
			}

			bar.GetPercentage = ChargePercent;

			string PhaseName(SunPhase phase) => FluentProvider.GetMessage(phase switch
			{
				SunPhase.Dusk => Dusk,
				SunPhase.Night => Night,
				SunPhase.Dawn => Dawn,
				_ => Day,
			});

			static SunPhase Next(SunPhase phase) => phase switch
			{
				SunPhase.Day => SunPhase.Dusk,
				SunPhase.Dusk => SunPhase.Night,
				SunPhase.Night => SunPhase.Dawn,
				_ => SunPhase.Day,
			};

			label.GetText = () =>
			{
				var phase = controller.PhaseAt(world.WorldTick, out var remaining, out _);
				return FluentProvider.GetMessage(Text,
					"phase", PhaseName(phase),
					"next", PhaseName(Next(phase)).ToLower(CultureInfo.CurrentCulture),
					"time", WidgetUtils.FormatTime(remaining, false, world.Timestep),
					"percent", ChargePercent().ToString(CultureInfo.CurrentCulture));
			};

			label.GetColor = () => controller.CurrentPhase switch
			{
				SunPhase.Night => nightColor,
				SunPhase.Dusk or SunPhase.Dawn => twilightColor,
				_ => textColor,
			};

			label.GetTooltipText = () =>
			{
				var solar = controller.SolarPercent(controller.CurrentPhase);

				var flow = storage.Flow;
				var flowText = flow > 0
					? FluentProvider.GetMessage(Charging, "rate", flow.ToString(CultureInfo.CurrentCulture))
					: flow < 0
						? FluentProvider.GetMessage(Discharging, "rate", (-flow).ToString(CultureInfo.CurrentCulture))
						: FluentProvider.GetMessage(Idle);

				return FluentProvider.GetMessage(Tooltip,
					"solar", solar.ToString(CultureInfo.CurrentCulture),
					"banks", storage.BankCount.ToString(CultureInfo.CurrentCulture),
					"stored", storage.TotalCharge.ToString("N0", CultureInfo.CurrentCulture),
					"capacity", storage.TotalMaxCharge.ToString("N0", CultureInfo.CurrentCulture),
					"flow", flowText,
					"reserve", (storage.TotalFullCharge - storage.TotalMaxCharge).ToString("N0", CultureInfo.CurrentCulture));
			};
		}
	}
}
