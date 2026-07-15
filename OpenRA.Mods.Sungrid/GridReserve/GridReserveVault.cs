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
using OpenRA.Mods.Common.Traits;
using OpenRA.Traits;

namespace OpenRA.Mods.Sungrid.GridReserve
{
	[Desc("Converts spendable Credits into the owner's Grid Reserve pool at a capped per-tick rate.",
		"Deposits are irreversible. Requires GridReserveManager on the owner's player actor.")]
	public class GridReserveVaultInfo : TraitInfo
	{
		[Desc("Maximum Reserve this single Vault can hold. Reaching a high Reserve target requires multiple Vaults.")]
		public readonly int Capacity = 8000;

		[Desc("Maximum Credits converted into Reserve per tick. Prevents dumping an entire treasury into Reserve in one move.")]
		public readonly int DepositRate = 30;

		[Desc("Percentage (0-100) of this Vault's held Reserve that is drained from the owner's total Reserve when the Vault is destroyed.")]
		public readonly int DestructionDrainPercent = 50;

		[Desc("Percentage (0-100) of the drained amount awarded to the attacker as Credits when this Vault is destroyed.")]
		public readonly int DestructionRewardPercent = 50;

		[GrantedConditionReference]
		[Desc("Condition granted on this actor while the owner's Reserve is at or above the manager's minimap reveal threshold.",
			"Intended to be referenced by a RevealsShroud (ValidRelationships: Enemy) instance on the same actor.")]
		public readonly string BeaconCondition = "gridreserve-beacon";

		public override object Create(ActorInitializer init) { return new GridReserveVault(init.Self, this); }
	}

	public class GridReserveVault : ITick, INotifyKilled, INotifyRemovedFromWorld, ISync
	{
		readonly GridReserveVaultInfo info;
		readonly PlayerResources playerResources;
		readonly GridReserveManager manager;

		int beaconToken = Actor.InvalidConditionToken;
		bool removed;

		[VerifySync]
		public int CurrentReserve { get; private set; }

		public GridReserveVault(Actor self, GridReserveVaultInfo info)
		{
			this.info = info;
			playerResources = self.Owner.PlayerActor.Trait<PlayerResources>();
			manager = self.Owner.PlayerActor.Trait<GridReserveManager>();
			manager.RegisterVault(this);
		}

		void ITick.Tick(Actor self)
		{
			if (!manager.Enabled)
				return;

			if (CurrentReserve < info.Capacity)
			{
				var room = info.Capacity - CurrentReserve;
				var wanted = Math.Min(info.DepositRate, room);
				var available = playerResources.GetCashAndResources();
				var amount = Math.Min(wanted, available);

				if (amount > 0 && playerResources.TakeCash(amount))
				{
					CurrentReserve += amount;
					manager.AddReserve(amount);
				}
			}

			var beaconActive = manager.BeaconActive;
			if (beaconActive && beaconToken == Actor.InvalidConditionToken)
				beaconToken = self.GrantCondition(info.BeaconCondition);
			else if (!beaconActive && beaconToken != Actor.InvalidConditionToken)
				beaconToken = self.RevokeCondition(beaconToken);
		}

		void INotifyKilled.Killed(Actor self, AttackInfo e)
		{
			if (removed)
				return;
			removed = true;
			manager.UnregisterVault(this);

			if (CurrentReserve <= 0)
				return;

			// Destroying a Vault drains its Reserve from the owner's total. Only a share of the
			// drained amount is recovered by the attacker as a raid reward; the rest is simply lost.
			var drained = CurrentReserve * info.DestructionDrainPercent / 100;
			CurrentReserve = 0;
			manager.AddReserve(-drained);

			if (drained <= 0)
				return;

			var attacker = e.Attacker;
			if (attacker == null || attacker.Owner == null || attacker.Owner.NonCombatant || attacker.Owner == self.Owner)
				return;

			var reward = drained * info.DestructionRewardPercent / 100;
			if (reward > 0)
				attacker.Owner.PlayerActor.Trait<PlayerResources>().GiveCash(reward);
		}

		void INotifyRemovedFromWorld.RemovedFromWorld(Actor self)
		{
			if (removed)
				return;
			removed = true;
			manager.UnregisterVault(this);

			// Covers sales and any other non-combat removal: Reserve deposits are irreversible,
			// so a Vault that leaves play by any means other than being killed in combat forfeits
			// its held Reserve outright rather than refunding it.
			if (CurrentReserve > 0)
			{
				manager.AddReserve(-CurrentReserve);
				CurrentReserve = 0;
			}
		}

		public int ApplyDecay(int percent)
		{
			if (CurrentReserve <= 0 || percent <= 0)
				return 0;

			var amount = CurrentReserve * percent / 100;
			if (amount <= 0)
				return 0;

			CurrentReserve -= amount;
			return amount;
		}
	}
}
