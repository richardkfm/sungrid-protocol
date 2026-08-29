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
	[Desc("Attach to the world actor. Owns the two timers SpawnsResourceOnDeath needs: one that holds a dropped",
		"resource back for a while before it appears, so a Harvester-type unit can't be lured into the fight",
		"that created it (docs/BACKLOG.md issue #97), and one that shrinks the drop back down if it isn't",
		"collected in time, so battlefield wreckage stays a temporary pickup rather than becoming a permanent,",
		"farmable resource patch at a contested chokepoint (issue #87).")]
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

		readonly struct PendingSpawn(CPos origin, string resourceType, byte amount, int maxRange,
			int decayDelay, int spawnsAtTick)
		{
			public readonly CPos Origin = origin;
			public readonly string ResourceType = resourceType;
			public readonly byte Amount = amount;
			public readonly int MaxRange = maxRange;
			public readonly int DecayDelay = decayDelay;
			public readonly int SpawnsAtTick = spawnsAtTick;
		}

		readonly List<PendingDecay> pendingDecays = [];
		readonly List<PendingSpawn> pendingSpawns = [];

		public void ScheduleDecay(World world, CPos cell, string resourceType, byte amount, int delayTicks)
		{
			if (delayTicks <= 0)
				return;

			pendingDecays.Add(new PendingDecay(cell, resourceType, amount, world.WorldTick + delayTicks));
		}

		public void ScheduleSpawn(World world, CPos origin, string resourceType, byte amount, int maxRange,
			int decayDelay, int delayTicks)
		{
			if (delayTicks <= 0)
				return;

			pendingSpawns.Add(new PendingSpawn(origin, resourceType, amount, maxRange, decayDelay,
				world.WorldTick + delayTicks));
		}

		void ITick.Tick(Actor self)
		{
			if (pendingDecays.Count == 0 && pendingSpawns.Count == 0)
				return;

			var world = self.World;
			var tick = world.WorldTick;
			var resourceLayer = world.WorldActor.TraitOrDefault<IResourceLayer>();

			// Decays are walked before spawns so a drop appearing this tick doesn't get its own freshly
			// scheduled decay re-examined in the same pass.
			for (var i = pendingDecays.Count - 1; i >= 0; i--)
			{
				var entry = pendingDecays[i];
				if (entry.ExpiresAtTick > tick)
					continue;

				pendingDecays.RemoveAt(i);

				// Only removes up to this drop's own share -- another kill may since have topped the same cell
				// back up, and RemoveResource already clamps at zero, so this never removes more than is left.
				resourceLayer?.RemoveResource(entry.ResourceType, entry.Cell, entry.Amount);
			}

			for (var i = pendingSpawns.Count - 1; i >= 0; i--)
			{
				var entry = pendingSpawns[i];
				if (entry.SpawnsAtTick > tick)
					continue;

				pendingSpawns.RemoveAt(i);

				if (resourceLayer == null)
					continue;

				// Picked now rather than back at the actor's death: a cell that could take the drop then may
				// since have filled up or been given a different resource type.
				var cell = SpawnsResourceOnDeath.ChooseCell(world, resourceLayer, entry.ResourceType,
					entry.Origin, entry.MaxRange);

				if (cell == null)
					continue;

				resourceLayer.AddResource(entry.ResourceType, cell.Value, entry.Amount);

				// The decay clock starts here, when the drop actually appears, so holding it back doesn't come
				// out of the window a Hauler has to collect it in.
				ScheduleDecay(world, cell.Value, entry.ResourceType, entry.Amount, entry.DecayDelay);
			}
		}
	}
}
