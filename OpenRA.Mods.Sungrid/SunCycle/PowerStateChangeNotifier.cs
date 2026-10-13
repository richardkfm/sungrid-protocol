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

using System.Linq;
using OpenRA.Mods.Common.Traits;
using OpenRA.Traits;

namespace OpenRA.Mods.Sungrid.SunCycle
{
	[TraitLocation(SystemActors.Player)]
	[Desc("Works around an engine gap: PowerManager only notifies INotifyPowerLevelChanged actors when excess power",
		"changes sign (Normal <-> Low), never on Low <-> Critical, so a GrantConditionOnPowerState with",
		"`ValidPowerStates: Critical` goes stale - the drones' weapons stayed armed at Critical power. Every night",
		"of the Sun Cycle walks a solar-heavy grid down through exactly that transition, so this watches the",
		"PowerState itself and sends the missing notification. Harmless alongside the engine's own: every",
		"listener re-reads the state, so a duplicate call changes nothing.")]
	public class PowerStateChangeNotifierInfo : TraitInfo, Requires<PowerManagerInfo>
	{
		public override object Create(ActorInitializer init) { return new PowerStateChangeNotifier(init.Self); }
	}

	public class PowerStateChangeNotifier : ITick
	{
		readonly PowerManager power;
		PowerState last = PowerState.Normal;

		public PowerStateChangeNotifier(Actor self)
		{
			power = self.Trait<PowerManager>();
		}

		void ITick.Tick(Actor self)
		{
			var state = power.PowerState;
			if (state == last)
				return;

			// The engine has already notified any change that crossed into or out of Normal, but several
			// power changes can land in one tick (Normal -> Low -> Critical as two plants die together), and the
			// engine's notification then reported the intermediate state. Re-notify on every change instead of
			// trying to work out which ones it missed; a duplicate is a no-op for every listener.
			last = state;

			foreach (var p in self.World.ActorsWithTrait<INotifyPowerLevelChanged>().ToArray())
				if (!p.Actor.IsDead && p.Actor.IsInWorld && p.Actor.Owner == self.Owner)
					p.Trait.PowerLevelChanged(p.Actor);
		}
	}
}
