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
using OpenRA.Mods.Sungrid.SunCycle;
using OpenRA.Traits;

namespace OpenRA.Mods.Sungrid.GridReserve
{
	[TraitLocation(SystemActors.Player)]
	[Desc("Caps how many Vaults a player may own while Grid Reserve is on: as many as the Reserve target needs, plus",
		"SpareBanks. Provides Prerequisite while the player is under the cap, so list it in the Vault's Buildable",
		"Prerequisites; at the cap the build button greys out and anything still queued is refunded by the queue.",
		"A captured Vault still counts, and may take a player past the cap. Off-mode matches are never capped.",
		"See docs/BACKLOG.md issue #147.")]
	public class GridReserveBankLimitInfo : TraitInfo, ITechTreePrerequisiteInfo, Requires<GridReserveManagerInfo>, Requires<TechTreeInfo>
	{
		[ActorReference]
		[FieldLoader.Require]
		[Desc("Vault actor types. The cap is sized off the Reserve the largest of them can hold.")]
		public readonly HashSet<string> BankTypes = [];

		[FieldLoader.Require]
		[Desc("Prerequisite provided while the player owns fewer Vaults than the cap.")]
		public readonly string Prerequisite = null;

		[Desc("Vaults allowed on top of the number that can hold the Reserve target: raid redundancy and,",
			"with the Sun Cycle on, room for banks bought for energy storage.")]
		public readonly int SpareBanks = 4;

		IEnumerable<string> ITechTreePrerequisiteInfo.Prerequisites(ActorInfo info) { yield return Prerequisite; }

		public override object Create(ActorInitializer init) { return new GridReserveBankLimit(init.Self, this); }

		// The Reserve one Vault of these types can hold, fixed for the match (rules plus lobby options): with the
		// Sun Cycle on, a Vault that is also a Battery Bank keeps a protected share for energy
		// (PowerStorage.ReserveRoom). The world actor, and so the controller's lobby option, is created before any
		// player actor, so this is safe from a player trait's Created.
		public static int ReserveCapacityPerBank(World world, IEnumerable<string> bankTypes)
		{
			var sunCycle = world.WorldActor.TraitOrDefault<SunCycleController>();
			var cycleOn = sunCycle != null && sunCycle.Enabled;
			var capacity = 0;
			foreach (var type in bankTypes)
			{
				if (!world.Map.Rules.Actors.TryGetValue(type, out var actorInfo))
					continue;

				var vaultInfo = actorInfo.TraitInfoOrDefault<GridReserveVaultInfo>();
				if (vaultInfo == null)
					continue;

				var reserveCapacity = vaultInfo.Capacity;
				var storageInfo = actorInfo.TraitInfoOrDefault<PowerStorageInfo>();
				if (cycleOn && storageInfo != null)
					reserveCapacity -= storageInfo.ProtectedSpace(vaultInfo.Capacity);

				if (reserveCapacity > capacity)
					capacity = reserveCapacity;
			}

			return capacity;
		}
	}

	public class GridReserveBankLimit : ITechTreePrerequisite, INotifyCreated, ITick
	{
		readonly GridReserveBankLimitInfo info;
		readonly IEnumerable<string> prerequisite;
		GridReserveManager manager;
		TechTree techTree;
		int bankCapacity;
		bool provided = true;

		public GridReserveBankLimit(Actor self, GridReserveBankLimitInfo info)
		{
			this.info = info;
			prerequisite = [info.Prerequisite];
		}

		void INotifyCreated.Created(Actor self)
		{
			manager = self.Trait<GridReserveManager>();
			techTree = self.Trait<TechTree>();
			bankCapacity = GridReserveBankLimitInfo.ReserveCapacityPerBank(self.World, info.BankTypes);
		}

		// The most Vaults this player may own, or 0 for no cap (Grid Reserve off, no target, no Vault type).
		// Read off the manager every time rather than cached: its target resolves at WorldLoaded.
		public int Limit => manager.Enabled && manager.Target > 0 && bankCapacity > 0
			? (manager.Target + bankCapacity - 1) / bankCapacity + info.SpareBanks
			: 0;

		public bool HasRoom => Limit == 0 || manager.VaultCount < Limit;

		IEnumerable<string> ITechTreePrerequisite.ProvidesPrerequisites => HasRoom ? prerequisite : [];

		void ITick.Tick(Actor self)
		{
			// Vaults are not tech-tree actors, so nothing re-evaluates the tree when one is placed, destroyed,
			// sold or captured. Do it here, once, whenever the answer changes.
			var room = HasRoom;
			if (room == provided)
				return;

			provided = room;
			techTree.Update();
		}
	}
}
