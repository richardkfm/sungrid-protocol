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
using System.Collections.Generic;
using System.Linq;
using OpenRA.Mods.Common.Traits;
using OpenRA.Traits;

namespace OpenRA.Mods.Sungrid.SunCycle
{
	[Flags]
	public enum SunPhase
	{
		None = 0,
		Day = 1,
		Dusk = 2,
		Night = 4,
		Dawn = 8,
	}

	public interface INotifySunPhaseChanged { void SunPhaseChanged(Actor self, SunPhase phase); }

	[TraitLocation(SystemActors.World)]
	[Desc("Implements the Sun Cycle: a global day/night clock that GrantConditionOnSunPhase turns into actor",
		"conditions (solar output, battery behaviour) and the lobby checkbox that switches it on.",
		"The phase is a pure function of World.WorldTick, so it is lockstep-, replay- and save-safe and holds no",
		"synced state of its own. Every timing field is per-map overridable, so a map (e.g. the main-menu",
		"shellmap) can run a faster showcase cycle. See docs/GAME_MODES.md.")]
	public class SunCycleControllerInfo : TraitInfo, ILobbyOptions, IRulesetLoaded
	{
		[FluentReference]
		[Desc("Descriptive label for the Sun Cycle checkbox in the lobby.")]
		public readonly string CheckboxLabel = "checkbox-suncycle.label";

		[FluentReference]
		[Desc("Tooltip description for the Sun Cycle checkbox in the lobby.")]
		public readonly string CheckboxDescription = "checkbox-suncycle.description";

		[Desc("Default value of the Sun Cycle checkbox in the lobby. Off until it has been playtested.")]
		public readonly bool CheckboxEnabled = false;

		[Desc("Prevent the Sun Cycle state from being changed in the lobby.")]
		public readonly bool CheckboxLocked = false;

		[Desc("Whether to display the Sun Cycle checkbox in the lobby.")]
		public readonly bool CheckboxVisible = true;

		[Desc("Display order for the Sun Cycle checkbox in the lobby.")]
		public readonly int CheckboxDisplayOrder = 0;

		[Desc("World tick at which the first Dusk begins. Everything before it is the opening Day,",
			"which keeps the opening build order out of the first night.")]
		public readonly int FirstDuskTick = 7500;

		[Desc("Length of the Day phase, in ticks.")]
		public readonly int DayTicks = 5250;

		[Desc("Length of the Dusk phase, in ticks. May be 0 for an instant sunset.")]
		public readonly int DuskTicks = 750;

		[Desc("Length of the Night phase, in ticks.")]
		public readonly int NightTicks = 2250;

		[Desc("Length of the Dawn phase, in ticks. May be 0 for an instant sunrise.")]
		public readonly int DawnTicks = 750;

		[Desc("Solar output at night, as a percentage. Read by the HUD and by SunCycleBotModule's planning; the",
			"output itself comes from the PowerMultiplier@NIGHT the solar actors carry (^SolarPower in",
			"mods/sungrid/rules/defaults.yaml), which must use the same number.")]
		public readonly int NightSolarPercent = 30;

		[Desc("Solar output at dusk and dawn, as a percentage. Same caveat as " + nameof(NightSolarPercent) + ".")]
		public readonly int TwilightSolarPercent = 65;

		[Desc("Stop the PowerManager's repeating low-power advice during Dusk and Night. The dusk announcement",
			"already told every player the grid is about to dip, and the stock nag repeats every 10 seconds,",
			"which would fire about a dozen times every night.")]
		public readonly bool MuteLowPowerAdviceAtNight = true;

		[NotificationReference("Speech")]
		public readonly string DayNotification = null;

		[FluentReference(optional: true)]
		public readonly string DayTextNotification = null;

		[NotificationReference("Speech")]
		public readonly string DuskNotification = null;

		[FluentReference(optional: true)]
		public readonly string DuskTextNotification = null;

		[NotificationReference("Speech")]
		public readonly string NightNotification = null;

		[FluentReference(optional: true)]
		public readonly string NightTextNotification = null;

		[NotificationReference("Speech")]
		public readonly string DawnNotification = null;

		[FluentReference(optional: true)]
		public readonly string DawnTextNotification = null;

		public int CycleTicks => DayTicks + DuskTicks + NightTicks + DawnTicks;

		IEnumerable<LobbyOption> ILobbyOptions.LobbyOptions(MapPreview map)
		{
			yield return new LobbyBooleanOption(map, "suncycle",
				CheckboxLabel, CheckboxDescription, CheckboxVisible, CheckboxDisplayOrder, CheckboxEnabled, CheckboxLocked);
		}

		void IRulesetLoaded<ActorInfo>.RulesetLoaded(Ruleset rules, ActorInfo info)
		{
			if (FirstDuskTick < 0 || DuskTicks < 0 || DawnTicks < 0)
				throw new YamlException($"{nameof(SunCycleController)}: {nameof(FirstDuskTick)}, {nameof(DuskTicks)} and {nameof(DawnTicks)} must not be negative.");

			if (DayTicks <= 0 || NightTicks <= 0)
				throw new YamlException($"{nameof(SunCycleController)}: {nameof(DayTicks)} and {nameof(NightTicks)} must be positive.");
		}

		public override object Create(ActorInitializer init) { return new SunCycleController(this); }
	}

	public class SunCycleController : ITick, INotifyCreated
	{
		public readonly SunCycleControllerInfo Info;

		readonly Dictionary<Player, bool> lowPowerAdviceDefaults = [];

		// Resolved once from the "suncycle" lobby checkbox. Everything else (conditions, storage, bots,
		// HUD, tint) reads this rather than the lobby option, so one place owns the toggle (the lesson of
		// Grid Reserve's issue #37, where only one of the mode's pieces read it).
		public bool Enabled { get; private set; }

		// Updated at the start of every world tick. Actors created during a tick read the same value the
		// rest of that tick sees, so nothing depends on actor creation order.
		public SunPhase CurrentPhase { get; private set; } = SunPhase.Day;

		public SunCycleController(SunCycleControllerInfo info)
		{
			Info = info;
		}

		void INotifyCreated.Created(Actor self)
		{
			Enabled = self.World.LobbyInfo.GlobalSettings.OptionOrDefault("suncycle", Info.CheckboxEnabled);
			CurrentPhase = PhaseAt(self.World.WorldTick);
		}

		public SunPhase PhaseAt(int tick) => PhaseAt(tick, out _, out _);

		public int SolarPercent(SunPhase phase) => phase switch
		{
			SunPhase.Night => Info.NightSolarPercent,
			SunPhase.Dusk or SunPhase.Dawn => Info.TwilightSolarPercent,
			_ => 100,
		};

		// Ticks left in the phase running at the given tick, and that phase's full length. Before the first
		// dusk the opening Day counts as one long phase.
		public SunPhase PhaseAt(int tick, out int remaining, out int length)
		{
			if (!Enabled || tick < Info.FirstDuskTick)
			{
				remaining = Enabled ? Info.FirstDuskTick - tick : 0;
				length = Info.FirstDuskTick;
				return SunPhase.Day;
			}

			var t = (tick - Info.FirstDuskTick) % Info.CycleTicks;
			if (t < Info.DuskTicks)
			{
				remaining = Info.DuskTicks - t;
				length = Info.DuskTicks;
				return SunPhase.Dusk;
			}

			t -= Info.DuskTicks;
			if (t < Info.NightTicks)
			{
				remaining = Info.NightTicks - t;
				length = Info.NightTicks;
				return SunPhase.Night;
			}

			t -= Info.NightTicks;
			if (t < Info.DawnTicks)
			{
				remaining = Info.DawnTicks - t;
				length = Info.DawnTicks;
				return SunPhase.Dawn;
			}

			t -= Info.DawnTicks;
			remaining = Info.DayTicks - t;
			length = Info.DayTicks;
			return SunPhase.Day;
		}

		void ITick.Tick(Actor self)
		{
			if (!Enabled)
				return;

			var world = self.World;
			var phase = PhaseAt(world.WorldTick);
			if (phase == CurrentPhase)
				return;

			CurrentPhase = phase;

			// ToArray: a granted condition can enable traits that re-total power and notify other actors,
			// so don't hold an enumerator over the trait dictionary while that happens.
			foreach (var p in world.ActorsWithTrait<INotifySunPhaseChanged>().ToArray())
				if (!p.Actor.IsDead)
					p.Trait.SunPhaseChanged(p.Actor, phase);

			if (Info.MuteLowPowerAdviceAtNight)
				UpdateLowPowerAdvice(world, phase == SunPhase.Dusk || phase == SunPhase.Night);

			// The fast-forward of a loaded save replays every phase change; only the live one is announced.
			if (!world.IsLoadingGameSave)
				Announce(world, phase);
		}

		void UpdateLowPowerAdvice(World world, bool mute)
		{
			foreach (var player in world.Players)
			{
				var power = player.PlayerActor.TraitOrDefault<PowerManager>();
				if (power == null)
					continue;

				// Remember what the advice was set to before the first night (a mission script may have
				// turned it off) and restore exactly that at dawn, rather than forcing it back on.
				if (!lowPowerAdviceDefaults.TryGetValue(player, out var original))
					lowPowerAdviceDefaults[player] = original = power.PlayLowPowerNotification;

				power.PlayLowPowerNotification = !mute && original;
			}
		}

		void Announce(World world, SunPhase phase)
		{
			string speech, text;
			switch (phase)
			{
				case SunPhase.Dusk: speech = Info.DuskNotification; text = Info.DuskTextNotification; break;
				case SunPhase.Night: speech = Info.NightNotification; text = Info.NightTextNotification; break;
				case SunPhase.Dawn: speech = Info.DawnNotification; text = Info.DawnTextNotification; break;
				default: speech = Info.DayNotification; text = Info.DayTextNotification; break;
			}

			if (text != null)
				TextNotificationsManager.AddSystemLine(text);

			var local = world.LocalPlayer ?? world.RenderPlayer;
			if (speech != null)
				Game.Sound.PlayNotification(world.Map.Rules, local, "Speech", speech, local?.Faction.InternalName);
		}
	}
}
