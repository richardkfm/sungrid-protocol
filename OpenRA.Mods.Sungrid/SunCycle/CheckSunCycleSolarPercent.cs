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
using System.Linq;
using OpenRA.Mods.Common.Lint;
using OpenRA.Mods.Common.Traits;
using OpenRA.Server;

namespace OpenRA.Mods.Sungrid.SunCycle
{
	// The night output of a Solar Array lives in two places: the PowerMultiplier that actually applies it
	// (YAML, ^SolarPower) and SunCycleController's NightSolarPercent / TwilightSolarPercent, which the HUD
	// shows and the bots plan with. A retune that touches only one of them would leave bots planning for a
	// night that isn't the one being played, silently. This makes --check-yaml catch it.
	sealed class CheckSunCycleSolarPercent : ILintRulesPass, ILintServerMapPass
	{
		void ILintRulesPass.Run(Action<string> emitError, Action<string> emitWarning, ModData modData, Ruleset rules)
		{
			Run(emitError, rules);
		}

		void ILintServerMapPass.Run(Action<string> emitError, Action<string> emitWarning, ModData modData, MapPreview map, Ruleset mapRules)
		{
			Run(emitError, mapRules);
		}

		static void Run(Action<string> emitError, Ruleset rules)
		{
			if (!rules.Actors.TryGetValue("world", out var world))
				return;

			var controller = world.TraitInfoOrDefault<SunCycleControllerInfo>();
			if (controller == null)
				return;

			foreach (var actor in rules.Actors.Values)
			{
				var grants = actor.TraitInfos<GrantConditionOnSunPhaseInfo>().ToArray();
				if (grants.Length == 0)
					continue;

				foreach (var multiplier in actor.TraitInfos<PowerMultiplierInfo>())
				{
					if (multiplier.RequiresCondition == null)
						continue;

					foreach (var grant in grants)
					{
						if (!multiplier.RequiresCondition.Variables.Contains(grant.Condition))
							continue;

						int expected;
						if (grant.Phases == SunPhase.Night)
							expected = controller.NightSolarPercent;
						else if (grant.Phases == (SunPhase.Dusk | SunPhase.Dawn))
							expected = controller.TwilightSolarPercent;
						else
							continue;

						if (multiplier.Modifier != expected)
							emitError($"Actor `{actor.Name}`: a PowerMultiplier gated on Sun Cycle condition `{grant.Condition}` " +
								$"uses Modifier {multiplier.Modifier}, but SunCycleController says {grant.Phases} solar output is {expected}%. " +
								"The HUD and the bots read the controller's number; keep the two in step.");
					}
				}
			}
		}
	}
}
