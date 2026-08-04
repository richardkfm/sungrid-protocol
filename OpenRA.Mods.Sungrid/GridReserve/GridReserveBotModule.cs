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
using System.Collections.Frozen;
using System.Linq;
using OpenRA.Mods.Common;
using OpenRA.Mods.Common.Traits;
using OpenRA.Traits;

namespace OpenRA.Mods.Sungrid.GridReserve
{
	[TraitLocation(SystemActors.Player)]
	[Desc("Lets a bot play the Grid Reserve economic victory mode: it builds enough Vaults to actually reach",
		"the map's Reserve target, and reacts when an opponent gets close to winning on Reserve.",
		"Does nothing at all while the gridreserve lobby option is off, so destruction-victory games are unaffected.",
		"Requires GridReserveManager on the same player actor. See docs/GAME_MODES.md.")]
	public class GridReserveBotModuleInfo : ConditionalTraitInfo
	{
		[Desc("Actor types carrying the GridReserveVault trait that this bot should build to bank Reserve.")]
		public readonly FrozenSet<string> VaultTypes = FrozenSet<string>.Empty;

		[Desc("Percentage of the Reserve target the bot wants to have Vault capacity for.",
			"Above 100 so that losing a Vault to a raid doesn't immediately put the target out of reach.")]
		public readonly int CoveragePercent = 125;

		[Desc("Percentage used instead of " + nameof(CoveragePercent) + " once an opponent is visibly banking",
			"(at or past the minimap-reveal threshold). Losing the economic race is answered by banking harder.")]
		public readonly int ContestedCoveragePercent = 150;

		[Desc("Never build more than this many Vaults, whatever the Reserve target works out to.")]
		public readonly int MaximumVaults = 8;

		[Desc("Only queue another Vault while the bot holds at least this much spendable cash.",
			"Vaults siphon Credits once built, so a bot that overbuilds them starves its own army.")]
		public readonly int MinimumCash = 1500;

		[Desc("Ticks between Vault build decisions.")]
		public readonly int BuildIntervalTicks = 250;

		[Desc("Stop queueing new Vaults while an opponent is holding Grid Lockdown.",
			"The economic race is already lost on the clock at that point, so the remaining income",
			"is better spent on the army that can still break the Lockdown by killing their Vaults.")]
		public readonly bool AbandonBankingOnEnemyLockdown = true;

		[GrantedConditionReference]
		[Desc("Optional condition granted on the player actor while an opponent is at or past the minimap-reveal",
			"threshold. Provided as a hook for RequiresCondition on other bot modules; unset by default.")]
		public readonly string EnemyBankingCondition = null;

		[GrantedConditionReference]
		[Desc("Optional condition granted on the player actor while an opponent is holding Grid Lockdown.",
			"Provided as a hook for RequiresCondition on other bot modules; unset by default.")]
		public readonly string EnemyLockdownCondition = null;

		public override object Create(ActorInitializer init) { return new GridReserveBotModule(init.Self, this); }
	}

	public class GridReserveBotModule : ConditionalTrait<GridReserveBotModuleInfo>, IBotTick
	{
		readonly World world;
		readonly Player player;

		GridReserveManager manager;
		PlayerResources playerResources;
		Player[] enemies;

		int vaultCapacity;
		int ticks;

		int bankingToken = Actor.InvalidConditionToken;
		int lockdownToken = Actor.InvalidConditionToken;

		public GridReserveBotModule(Actor self, GridReserveBotModuleInfo info)
			: base(info)
		{
			world = self.World;
			player = self.Owner;
		}

		protected override void Created(Actor self)
		{
			base.Created(self);

			manager = self.Trait<GridReserveManager>();
			playerResources = self.Trait<PlayerResources>();

			// Vault capacity is a rules constant, so the largest one only needs resolving once.
			foreach (var type in Info.VaultTypes)
			{
				if (!world.Map.Rules.Actors.TryGetValue(type, out var actorInfo))
					continue;

				var vaultInfo = actorInfo.TraitInfoOrDefault<GridReserveVaultInfo>();
				if (vaultInfo != null && vaultInfo.Capacity > vaultCapacity)
					vaultCapacity = vaultInfo.Capacity;
			}
		}

		void IBotTick.BotTick(IBot bot)
		{
			// Grid Reserve off: the Vault is just an ordinary storage building, and the base builder's own
			// build-a-silo-when-storage-is-full logic already covers that. Nothing here should touch production.
			if (!manager.Enabled || Info.VaultTypes.Count == 0 || vaultCapacity <= 0)
				return;

			if (++ticks % Math.Max(1, Info.BuildIntervalTicks) != 0)
				return;

			// Playable players are fixed once the game starts, so this can be cached lazily.
			enemies ??= world.Players
				.Where(p => !p.NonCombatant && p.Playable && player.RelationshipWith(p) == PlayerRelationship.Enemy)
				.ToArray();

			var enemyBanking = false;
			var enemyLockdown = false;
			foreach (var enemy in enemies)
			{
				if (enemy.WinState != WinState.Undefined)
					continue;

				var enemyManager = enemy.PlayerActor.TraitOrDefault<GridReserveManager>();
				if (enemyManager == null)
					continue;

				if (enemyManager.BeaconActive)
					enemyBanking = true;

				if (enemyManager.LockdownEligible)
					enemyLockdown = true;
			}

			UpdateCondition(player.PlayerActor, Info.EnemyBankingCondition, enemyBanking, ref bankingToken);
			UpdateCondition(player.PlayerActor, Info.EnemyLockdownCondition, enemyLockdown, ref lockdownToken);

			if (enemyLockdown && Info.AbandonBankingOnEnemyLockdown)
				return;

			if (playerResources.GetCashAndResources() < Info.MinimumCash)
				return;

			var wanted = WantedVaultCount(enemyBanking);
			if (wanted <= 0)
				return;

			var owned = world.ActorsHavingTrait<GridReserveVault>().Count(a => a.Owner == player && !a.IsDead);
			if (owned >= wanted)
				return;

			var queuesByCategory = AIUtils.FindQueuesByCategory(player);
			if (owned + CountQueuedVaults(queuesByCategory) >= wanted)
				return;

			QueueVault(bot, queuesByCategory);
		}

		int WantedVaultCount(bool contested)
		{
			if (manager.Target <= 0)
				return 0;

			var coverage = contested ? Info.ContestedCoveragePercent : Info.CoveragePercent;

			// Round up: covering the whole target always needs the partially-filled Vault as well.
			var needed = (int)(((long)manager.Target * coverage / 100 + vaultCapacity - 1) / vaultCapacity);
			return Math.Clamp(needed, 0, Info.MaximumVaults);
		}

		int CountQueuedVaults(ILookup<string, ProductionQueue> queuesByCategory)
		{
			var queued = 0;
			foreach (var category in queuesByCategory)
				foreach (var queue in category)
					foreach (var item in queue.AllQueued())
						if (Info.VaultTypes.Contains(item.Item))
							queued++;

			return queued;
		}

		void QueueVault(IBot bot, ILookup<string, ProductionQueue> queuesByCategory)
		{
			foreach (var type in Info.VaultTypes)
			{
				if (!world.Map.Rules.Actors.TryGetValue(type, out var actorInfo))
					continue;

				var buildable = actorInfo.TraitInfoOrDefault<BuildableInfo>();
				if (buildable == null)
					continue;

				foreach (var category in buildable.Queue)
				{
					// Only an idle queue is usable: BaseBuilderQueueManager places whatever finishes at the front
					// of the queue, so slotting a Vault in behind the base builder's own pick would strand it.
					var queue = queuesByCategory[category]
						.FirstOrDefault(q => !q.AllQueued().Any() && q.BuildableItems().Any(a => a.Name == type));

					if (queue == null)
						continue;

					AIUtils.BotDebug("{0} decided to build {1}: Grid Reserve banking", player, type);
					bot.QueueOrder(Order.StartProduction(queue.Actor, type, 1));
					return;
				}
			}
		}

		protected override void TraitDisabled(Actor self)
		{
			UpdateCondition(self, Info.EnemyBankingCondition, false, ref bankingToken);
			UpdateCondition(self, Info.EnemyLockdownCondition, false, ref lockdownToken);
		}

		static void UpdateCondition(Actor self, string condition, bool active, ref int token)
		{
			if (string.IsNullOrEmpty(condition))
				return;

			if (active && token == Actor.InvalidConditionToken)
				token = self.GrantCondition(condition);
			else if (!active && token != Actor.InvalidConditionToken)
				token = self.RevokeCondition(token);
		}
	}
}
