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

namespace OpenRA.Mods.Sungrid.Economy
{
	[Desc("Drops a small amount of a resource into the ground at this actor's death cell, or the nearest cell",
		"nearby that can hold it, so an idle Harvester-type unit collects it automatically through its own",
		"resource search. Written for the Recycling Depot/Hauler Drone economy so battlefield wreckage becomes",
		"collectible Scrap -- see docs/BACKLOG.md issue #5, which shelved this exact idea ('death-triggered",
		"wreck salvage') for a map-placed-resource design because nothing in the ruleset could add a resource",
		"to a cell. IResourceLayer.AddResource (added to the engine since that decision) is that missing piece.")]
	public class SpawnsResourceOnDeathInfo : ConditionalTraitInfo
	{
		[FieldLoader.Require]
		[Desc("Resource type to drop, matching a ResourceLayer.ResourceTypes key (e.g. 'Scrap').")]
		public readonly string ResourceType = null;

		[Desc("Amount of resource dropped at the chosen cell.")]
		public readonly byte Amount = 1;

		[Desc("How many random steps outward from the death cell to search for a cell that can hold the resource.",
			"Wrong terrain, a full cell, or a cell already holding a different resource are all skipped.")]
		public readonly int MaxRange = 8;

		public override object Create(ActorInitializer init) { return new SpawnsResourceOnDeath(this); }
	}

	public class SpawnsResourceOnDeath : ConditionalTrait<SpawnsResourceOnDeathInfo>, INotifyKilled
	{
		public SpawnsResourceOnDeath(SpawnsResourceOnDeathInfo info)
			: base(info) { }

		void INotifyKilled.Killed(Actor self, AttackInfo e)
		{
			if (IsTraitDisabled)
				return;

			var resourceLayer = self.World.WorldActor.TraitOrDefault<IResourceLayer>();
			if (resourceLayer == null)
				return;

			var cell = Util.RandomWalk(self.Location, self.World.SharedRandom)
				.Take(Info.MaxRange)
				.SkipWhile(p => !resourceLayer.CanAddResource(Info.ResourceType, p))
				.Cast<CPos?>()
				.FirstOrDefault();

			if (cell != null)
				resourceLayer.AddResource(Info.ResourceType, cell.Value, Info.Amount);
		}
	}
}
