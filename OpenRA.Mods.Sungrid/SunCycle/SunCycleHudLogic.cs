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
using OpenRA.Mods.Common.Traits;
using OpenRA.Mods.Common.Widgets;
using OpenRA.Mods.Sungrid.GridReserve;
using OpenRA.Primitives;
using OpenRA.Widgets;

namespace OpenRA.Mods.Sungrid.SunCycle
{
	[Desc("Attach to a Container in ingame-player.yaml to show the time of day, the time to the next phase and the",
		"local player's stored Battery Bank energy in absolute numbers, with a sun or moon icon that follows the phase.",
		"Hides itself when the suncycle lobby option is off, so it is safe to include in the default HUD",
		"unconditionally. Sits under the Grid Reserve bar, and moves up into its slot when Grid Reserve is off.")]
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

		[FluentReference("phase", "next", "time", "stored", "capacity", "state")]
		const string Text = "label-sun-cycle-hud.text";

		[FluentReference("solar", "banks", "stored", "capacity", "flow", "charge", "discharge")]
		const string Tooltip = "label-sun-cycle-hud.tooltip";

		[FluentReference("solar", "banks", "stored", "capacity", "flow", "charge", "discharge", "percent", "protected", "reserve")]
		const string TooltipReserve = "label-sun-cycle-hud.tooltip-reserve";

		[FluentReference]
		const string StateCharging = "label-sun-cycle-hud-state.charging";

		[FluentReference]
		const string StateDraining = "label-sun-cycle-hud-state.draining";

		[FluentReference]
		const string StateFull = "label-sun-cycle-hud-state.full";

		[FluentReference]
		const string StateEmpty = "label-sun-cycle-hud-state.empty";

		[FluentReference]
		const string StateNoSurplus = "label-sun-cycle-hud-state.no-surplus";

		[FluentReference]
		const string StateBlackout = "label-sun-cycle-hud-state.blackout";

		[FluentReference]
		const string StateNoBanks = "label-sun-cycle-hud-state.no-banks";

		[FluentReference("rate")]
		const string Charging = "label-sun-cycle-hud-flow.charging";

		[FluentReference("rate")]
		const string Discharging = "label-sun-cycle-hud-flow.discharging";

		[FluentReference]
		const string Idle = "label-sun-cycle-hud-flow.idle";

		// Region names in chrome.yaml's sungrid-marks collection (drawn by uibits/gen_chrome.py). A missing name
		// is not caught by any lint and throws on the first draw, so keep these in step with chrome.yaml.
		const string SunIcon = "sun";
		const string TwilightIcon = "sun-low";
		const string MoonIcon = "moon";

		[ObjectCreator.UseCtor]
		public SunCycleHudLogic(Widget widget, World world)
		{
			var player = world.LocalPlayer;
			var controller = world.WorldActor.TraitOrDefault<SunCycleController>();
			var storage = player?.PlayerActor.TraitOrDefault<PowerStorageManager>();
			var power = player?.PlayerActor.TraitOrDefault<PowerManager>();
			if (player == null || controller == null || storage == null || power == null || !controller.Enabled)
			{
				widget.IsVisible = () => false;
				return;
			}

			// Grid Reserve off: its bar is hidden, so take its slot instead of leaving a gap above this one.
			var gridReserve = world.WorldActor.TraitOrDefault<GridReserveController>();
			var reserveOn = gridReserve != null && gridReserve.Enabled;
			if (!reserveOn)
				widget.Bounds.Y = widget.Bounds.Y - widget.Bounds.Height - 4;

			var textColor = ChromeMetrics.Get<Color>("SunCycleDayColor");
			var twilightColor = ChromeMetrics.Get<Color>("SunCycleTwilightColor");
			var nightColor = ChromeMetrics.Get<Color>("SunCycleNightColor");

			var label = widget.Get<LabelWithTooltipWidget>("SUN_CYCLE_LABEL");
			var bar = widget.Get<ProgressBarWidget>("SUN_CYCLE_BAR");
			var phaseIcon = widget.Get<ImageWidget>("SUN_CYCLE_PHASE_ICON");

			// Stored energy over the energy the banks can hold right now (their protected shares plus whatever
			// space Grid Reserve has not taken), the same two numbers the label shows.
			bar.GetPercentage = () =>
			{
				var max = storage.TotalMaxCharge;
				return max > 0 ? Math.Clamp((int)((long)storage.TotalCharge * 100 / max), 0, 100) : 0;
			};

			phaseIcon.GetImageName = () => controller.CurrentPhase switch
			{
				SunPhase.Night => MoonIcon,
				SunPhase.Dusk or SunPhase.Dawn => TwilightIcon,
				_ => SunIcon,
			};

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

			// What the banks are doing, in words: the flow of the last update first, then why nothing moves.
			string State()
			{
				if (storage.BankCount == 0)
					return FluentProvider.GetMessage(StateNoBanks);

				if (storage.Flow > 0)
					return FluentProvider.GetMessage(StateCharging);

				if (storage.Flow < 0)
					return FluentProvider.GetMessage(StateDraining);

				var stored = storage.TotalCharge;
				if (power.ExcessPower < 0)
					return FluentProvider.GetMessage(power.PowerOutageRemainingTicks > 0 && stored > 0 ? StateBlackout : StateEmpty);

				var max = storage.TotalMaxCharge;
				if (max > 0 && stored >= max)
					return FluentProvider.GetMessage(StateFull);

				return FluentProvider.GetMessage(StateNoSurplus);
			}

			static string Number(int value) => value.ToString("N0", CultureInfo.CurrentCulture);

			label.GetText = () =>
			{
				var phase = controller.PhaseAt(world.WorldTick, out var remaining, out _);
				return FluentProvider.GetMessage(Text,
					"phase", PhaseName(phase),
					"next", PhaseName(Next(phase)).ToLower(CultureInfo.CurrentCulture),
					"time", WidgetUtils.FormatTime(remaining, false, world.Timestep),
					"stored", Number(storage.TotalCharge),
					"capacity", Number(storage.TotalMaxCharge),
					"state", State());
			};

			label.GetColor = () => controller.CurrentPhase switch
			{
				SunPhase.Night => nightColor,
				SunPhase.Dusk or SunPhase.Dawn => twilightColor,
				_ => textColor,
			};

			// Rates per bank are the same for every bank a player owns (one faction), so the first one's suffice.
			label.GetTooltipText = () =>
			{
				var solar = controller.SolarPercent(controller.CurrentPhase);

				var flow = storage.Flow;
				var flowText = flow > 0
					? FluentProvider.GetMessage(Charging, "rate", Number(flow))
					: flow < 0
						? FluentProvider.GetMessage(Discharging, "rate", Number(-flow))
						: FluentProvider.GetMessage(Idle);

				var banks = storage.BankCount;
				var charge = banks > 0 ? storage.TotalChargeRate / banks : 0;
				var discharge = banks > 0 ? storage.TotalDischargeRate / banks : 0;

				if (!reserveOn)
					return FluentProvider.GetMessage(Tooltip,
						"solar", solar.ToString(CultureInfo.CurrentCulture),
						"banks", banks.ToString(CultureInfo.CurrentCulture),
						"stored", Number(storage.TotalCharge),
						"capacity", Number(storage.TotalMaxCharge),
						"flow", flowText,
						"charge", Number(charge),
						"discharge", Number(discharge));

				return FluentProvider.GetMessage(TooltipReserve,
					"solar", solar.ToString(CultureInfo.CurrentCulture),
					"banks", banks.ToString(CultureInfo.CurrentCulture),
					"stored", Number(storage.TotalCharge),
					"capacity", Number(storage.TotalMaxCharge),
					"flow", flowText,
					"charge", Number(charge),
					"discharge", Number(discharge),
					"percent", storage.ProtectedChargePercent.ToString(CultureInfo.CurrentCulture),
					"protected", Number(storage.TotalProtectedCharge),
					"reserve", Number(storage.TotalReserveHeld));
			};
		}
	}
}
