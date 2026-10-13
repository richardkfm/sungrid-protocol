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

namespace OpenRA.Mods.Sungrid.SunCycle
{
	[TraitLocation(SystemActors.Player)]
	[Desc("Lets a bot get through the Sun Cycle's nights. By day it projects the night-time power deficit of its",
		"solar plants and builds storage banks and night-proof power plants ahead of dusk. At dusk and night it",
		"claims the idle Building queue for a night-proof plant whenever the grid is short, before the base",
		"builder's low-power override can pick a Solar Array, which picks plants by nominal output and would buy",
		"a 30%-output Solar Array over a full-output turbine. Does nothing while the suncycle option is off.")]
	public class SunCycleBotModuleInfo : ConditionalTraitInfo
	{
		[ActorReference(typeof(PowerStorageInfo))]
		[Desc("Actor types with PowerStorage this bot builds to carry power through the night.")]
		public readonly FrozenSet<string> StorageTypes = FrozenSet<string>.Empty;

		[ActorReference]
		[Desc("Power plants whose output falls at night. Must match the actors carrying the night PowerMultipliers.")]
		public readonly FrozenSet<string> SolarTypes = FrozenSet<string>.Empty;

		[ActorReference]
		[Desc("Power plants that hold their output at night. The best buildable one (by output) is chosen.")]
		public readonly FrozenSet<string> NightPowerTypes = FrozenSet<string>.Empty;

		[Desc("Don't plan for the night before this world tick. The default is a minute before the first dusk.")]
		public readonly int StartTick = 6000;

		[Desc("Never build more than this many banks for storage (Grid Reserve banking adds its own on top).")]
		public readonly int MaximumStorageBanks = 3;

		[Desc("Never own more than this many night-proof power plants through this module.")]
		public readonly int MaximumNightPowerPlants = 6;

		[Desc("Only queue anything while the bot holds at least this much spendable cash.")]
		public readonly int MinimumCash = 1000;

		[Desc("Ticks between daytime planning decisions.")]
		public readonly int BuildIntervalTicks = 250;

		[Desc("Ticks between checks at dusk and at night, when the base builder is the competition for the queue.")]
		public readonly int NightIntervalTicks = 25;

		[Desc("Ticks to wait after queueing anything, so an order still in flight isn't queued twice.")]
		public readonly int QueueCooldownTicks = 100;

		public override object Create(ActorInitializer init) { return new SunCycleBotModule(init.Self, this); }
	}

	public class SunCycleBotModule : ConditionalTrait<SunCycleBotModuleInfo>, IBotTick
	{
		readonly World world;
		readonly Player player;

		SunCycleController controller;
		PowerManager power;
		PowerStorageManager storage;
		PlayerResources playerResources;

		int bankDischargeRate;
		int ticks;
		int lastQueuedTick = -1;

		// How many of the bot's banks it wants for storage. GridReserveBotModule adds this to its own Vault
		// count, since the two jobs share one building and one capacity.
		public int StorageBanksWanted { get; private set; }

		public SunCycleBotModule(Actor self, SunCycleBotModuleInfo info)
			: base(info)
		{
			world = self.World;
			player = self.Owner;
		}

		protected override void Created(Actor self)
		{
			base.Created(self);

			controller = world.WorldActor.TraitOrDefault<SunCycleController>();
			power = self.Trait<PowerManager>();
			storage = self.Trait<PowerStorageManager>();
			playerResources = self.Trait<PlayerResources>();

			// A rules constant: the planning rate before any bank exists (faction multipliers come later from
			// the banks actually standing).
			foreach (var type in Info.StorageTypes)
			{
				if (!world.Map.Rules.Actors.TryGetValue(type, out var actorInfo))
					continue;

				var storageInfo = actorInfo.TraitInfoOrDefault<PowerStorageInfo>();
				if (storageInfo != null)
					bankDischargeRate = Math.Max(bankDischargeRate, storageInfo.DischargeRate);
			}
		}

		protected override void TraitDisabled(Actor self)
		{
			StorageBanksWanted = 0;
		}

		void IBotTick.BotTick(IBot bot)
		{
			if (controller == null || !controller.Enabled || world.WorldTick < Info.StartTick)
				return;

			var phase = controller.CurrentPhase;
			var dark = phase == SunPhase.Dusk || phase == SunPhase.Night;
			if (++ticks % Math.Max(1, dark ? Info.NightIntervalTicks : Info.BuildIntervalTicks) != 0)
				return;

			var deficit = ProjectedNightDeficit(phase);
			var rate = storage.BankCount > 0 ? storage.TotalDischargeRate / storage.BankCount : bankDischargeRate;
			StorageBanksWanted = rate > 0 ? Math.Clamp((deficit + rate - 1) / rate, 0, Info.MaximumStorageBanks) : 0;

			if (lastQueuedTick >= 0 && world.WorldTick - lastQueuedTick < Info.QueueCooldownTicks)
				return;

			if (playerResources.GetCashAndResources() < Info.MinimumCash)
				return;

			var queues = AIUtils.FindQueuesByCategory(player);

			if (dark)
			{
				// The grid is under the base builder's own power margin right now, after whatever the banks are
				// already giving. Left alone, its "first priority is to get out of low power" override would buy
				// the highest-output plant it can, which by nominal output is a Solar Array running at a third of
				// that. Getting to the idle queue first and buying a night-proof plant answers the same need.
				if (power.ExcessPower < BaseBuilderExcessPowerTarget() && CountOwned(Info.NightPowerTypes) < Info.MaximumNightPowerPlants)
					QueueBest(bot, queues, Info.NightPowerTypes, "night-time power deficit");

				return;
			}

			if (deficit <= 0)
				return;

			// Storage first: banks are cheap and cover the dusk dip as well as the night.
			var banks = CountOwned(Info.StorageTypes);
			if (banks + CountQueued(queues, Info.StorageTypes) < StorageBanksWanted)
			{
				QueueBest(bot, queues, Info.StorageTypes, "storage for the night");
				return;
			}

			// Whatever the banks wanted cannot discharge fast enough to cover is bought as night-proof supply.
			var covered = Math.Min(banks, StorageBanksWanted) * rate;
			if (deficit > covered && CountOwned(Info.NightPowerTypes) < Info.MaximumNightPowerPlants)
				QueueBest(bot, queues, Info.NightPowerTypes, "projected night-time deficit");
		}

		// The power the bot would be short by at full night, with its banks idle and its solar plants at the
		// night percentage. Read from the plants' current output, so damage and outages are included.
		int ProjectedNightDeficit(SunPhase phase)
		{
			var excess = power.ExcessPower - storage.TotalGross;

			var phasePercent = controller.SolarPercent(phase);

			if (phasePercent <= 0)
				return Math.Max(0, -excess);

			var solarNow = 0;
			foreach (var p in world.ActorsWithTrait<Power>())
				if (p.Actor.Owner == player && !p.Trait.IsTraitDisabled && Info.SolarTypes.Contains(p.Actor.Info.Name))
					solarNow += Math.Max(0, p.Trait.GetEnabledPower());

			var solarFull = (long)solarNow * 100 / phasePercent;
			var solarNight = solarFull * controller.Info.NightSolarPercent / 100;
			var nightExcess = excess - (solarNow - solarNight);
			return (int)Math.Max(0, -nightExcess);
		}

		// The power margin BaseBuilderQueueManager is currently defending: its MinimumExcessPower plus an
		// increment per ExcessPowerIncreaseThreshold buildings, clamped to MaximumExcessPower. Mirrors the engine's
		// own computation (BaseBuilderQueueManager.ProductionTick) because the result is not exposed.
		int BaseBuilderExcessPowerTarget()
		{
			var builder = player.PlayerActor.TraitsImplementing<BaseBuilderBotModule>().FirstOrDefault(m => !m.IsTraitDisabled);
			if (builder == null)
				return 0;

			var info = builder.Info;
			var buildings = world.ActorsHavingTrait<Building>().Count(a => a.Owner == player);
			var bonus = info.ExcessPowerIncrement * (buildings / Math.Max(1, info.ExcessPowerIncreaseThreshold));
			return Math.Clamp(info.MinimumExcessPower + bonus, info.MinimumExcessPower, Math.Max(info.MinimumExcessPower, info.MaximumExcessPower));
		}

		int CountOwned(FrozenSet<string> types)
		{
			return world.Actors.Count(a => a.Owner == player && !a.IsDead && a.IsInWorld && types.Contains(a.Info.Name));
		}

		static int CountQueued(ILookup<string, ProductionQueue> queues, FrozenSet<string> types)
		{
			var queued = 0;
			foreach (var category in queues)
				foreach (var queue in category)
					foreach (var item in queue.AllQueued())
						if (types.Contains(item.Item))
							queued++;

			return queued;
		}

		void QueueBest(IBot bot, ILookup<string, ProductionQueue> queues, FrozenSet<string> types, string reason)
		{
			// Only an idle queue is usable: BaseBuilderQueueManager places whatever finishes at the front of a
			// queue, so slotting in behind the base builder's own pick would strand it (the same rule as
			// GridReserveBotModule). Among the buildable candidates, the one supplying the most power wins.
			foreach (var category in queues)
			{
				foreach (var queue in category)
				{
					if (queue.AllQueued().Any())
						continue;

					var best = queue.BuildableItems()
						.Where(a => types.Contains(a.Name))
						.MaxByOrDefault(a => a.TraitInfos<PowerInfo>().Where(i => i.EnabledByDefault).Sum(i => i.Amount));

					if (best == null)
						continue;

					AIUtils.BotDebug("{0} decided to build {1}: Sun Cycle ({2})", player, best.Name, reason);
					bot.QueueOrder(Order.StartProduction(queue.Actor, best.Name, 1));
					lastQueuedTick = world.WorldTick;
					return;
				}
			}
		}
	}
}
