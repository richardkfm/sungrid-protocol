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

using OpenRA.Traits;

namespace OpenRA.Mods.Sungrid.SunCycle
{
	[Desc("Grants a condition while the Sun Cycle is in one of the listed phases. Works on any actor, including",
		"the Player actor. Never grants anything while the suncycle lobby option is off - not even for",
		"`Phases: Day` - so a match without the cycle behaves exactly as if this trait were absent.",
		"Requires SunCycleController on the world actor.")]
	public class GrantConditionOnSunPhaseInfo : TraitInfo
	{
		[FieldLoader.Require]
		[GrantedConditionReference]
		[Desc("Condition to grant.")]
		public readonly string Condition = null;

		[FieldLoader.Require]
		[Desc("Phases during which the condition is granted. Options are Day, Dusk, Night and Dawn.")]
		public readonly SunPhase Phases = SunPhase.None;

		public override object Create(ActorInitializer init) { return new GrantConditionOnSunPhase(this); }
	}

	public class GrantConditionOnSunPhase : INotifyCreated, INotifySunPhaseChanged
	{
		readonly GrantConditionOnSunPhaseInfo info;
		SunCycleController controller;
		int token = Actor.InvalidConditionToken;

		public GrantConditionOnSunPhase(GrantConditionOnSunPhaseInfo info)
		{
			this.info = info;
		}

		void INotifyCreated.Created(Actor self)
		{
			// Actors created mid-night (a Solar Array finished after dusk, a map-placed actor) pick up the
			// current phase here; the controller's broadcast only reaches actors that already exist.
			controller = self.World.WorldActor.TraitOrDefault<SunCycleController>();
			if (controller != null)
				Update(self, controller.CurrentPhase);
		}

		void INotifySunPhaseChanged.SunPhaseChanged(Actor self, SunPhase phase)
		{
			Update(self, phase);
		}

		void Update(Actor self, SunPhase phase)
		{
			var active = controller.Enabled && (info.Phases & phase) != 0;
			if (active && token == Actor.InvalidConditionToken)
				token = self.GrantCondition(info.Condition);
			else if (!active && token != Actor.InvalidConditionToken)
				token = self.RevokeCondition(token);
		}
	}
}
