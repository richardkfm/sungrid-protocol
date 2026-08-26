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
using OpenRA.Mods.Common.Traits;
using OpenRA.Traits;

namespace OpenRA.Mods.Sungrid.Economy
{
	[TraitLocation(SystemActors.World)]
	[Desc("Attach to the world actor. Lets other traits (SpawnsResourceOnDeath) schedule a dropped resource to",
		"shrink back down if it isn't collected in time, so battlefield wreckage stays a temporary pickup rather",
		"than becoming a permanent, farmable resource patch at a contested chokepoint.")]
	public class ResourceDecayManagerInfo : TraitInfo
	{
		public override object Create(ActorInitializer init) { return new ResourceDecayManager(); }
	}

	public class ResourceDecayManager : ITick
	{
		readonly struct PendingDecay(CPos cell, string resourceType, byte amount, int expiresAtTick)
		{
			public readonly CPos Cell = cell;
			public readonly string ResourceType = resourceType;
			public readonly byte Amount = amount;
			public readonly int ExpiresAtTick = expiresAtTick;
		}

		readonly List<PendingDecay> pending = [];

		public void ScheduleDecay(World world, CPos cell, string resourceType, byte amount, int delayTicks)
		{
			if (delayTicks <= 0)
				return;

			pending.Add(new PendingDecay(cell, resourceType, amount, world.WorldTick + delayTicks));
		}

		void ITick.Tick(Actor self)
		{
			if (pending.Count == 0)
				return;

			var tick = self.World.WorldTick;
			var resourceLayer = self.World.WorldActor.TraitOrDefault<IResourceLayer>();

			for (var i = pending.Count - 1; i >= 0; i--)
			{
				var entry = pending[i];
				if (entry.ExpiresAtTick > tick)
					continue;

				pending.RemoveAt(i);

				// Only removes up to this drop's own share -- another kill may since have topped the same cell
				// back up, and RemoveResource already clamps at zero, so this never removes more than is left.
				resourceLayer?.RemoveResource(entry.ResourceType, entry.Cell, entry.Amount);
			}
		}
	}
}
