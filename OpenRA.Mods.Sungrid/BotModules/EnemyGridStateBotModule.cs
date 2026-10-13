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
using OpenRA.Mods.Common;
using OpenRA.Mods.Common.Traits;
using OpenRA.Traits;

namespace OpenRA.Mods.Sungrid.BotModules
{
	[TraitLocation(SystemActors.Player)]
	[Desc("Grants a condition on the bot's player actor while an opponent's power grid is down: in low or critical power,",
		"or in a power outage, optionally only after a number of blackouts. A hook for RequiresCondition on other bot",
		"modules, so a personality can hold its main force back until enemy grids have failed and only then push.",
		"Works with or without the Grid Reserve option.",
		"See docs/BACKLOG.md issue #135.")]
	public class EnemyGridStateBotModuleInfo : ConditionalTraitInfo
	{
		[FieldLoader.Require]
		[GrantedConditionReference]
		[Desc("Condition granted on the player actor while an opponent's grid is down.",
			"Bots only run on the host, so only other bot modules may consume it - never a synced trait.")]
		public readonly string EnemyGridDownCondition = null;

		[Desc("Ignore opponents' grids before this tick. An opening base routinely dips into low power for a",
			"moment (a building placed before the plant that feeds it), which is not a collapse worth pushing into.")]
		public readonly int StartDelayTicks = 6000;

		[Desc("Keep the condition for this many ticks after the last check that saw a grid down. A player who",
			"rebuilds one Solar Array a second after a blackout should not call the push straight back off.")]
		public readonly int HoldTicks = 1500;

		[Desc("Ticks between checks of the opponents' power state.")]
		public readonly int CheckIntervalTicks = 50;

		[Desc("Only grant the condition once this many power outages (blackouts, e.g. from an infiltrated power plant)",
			"have been seen across all opponents. Counted from StartDelayTicks, one per outage that begins. Low power",
			"alone is not counted. Zero grants it on the first grid seen down.")]
		public readonly int MinimumOutages = 0;

		public override object Create(ActorInitializer init) { return new EnemyGridStateBotModule(init.Self, this); }
	}

	public class EnemyGridStateBotModule : ConditionalTrait<EnemyGridStateBotModuleInfo>, IBotTick
	{
		readonly World world;
		readonly Player player;

		Player[] enemies;
		bool[] enemyInOutage;
		int outagesSeen;
		int lastSeenDownTick = int.MinValue;
		int token = Actor.InvalidConditionToken;

		public EnemyGridStateBotModule(Actor self, EnemyGridStateBotModuleInfo info)
			: base(info)
		{
			world = self.World;
			player = self.Owner;
		}

		void IBotTick.BotTick(IBot bot)
		{
			var tick = world.WorldTick;
			if (tick < Info.StartDelayTicks || tick % Math.Max(1, Info.CheckIntervalTicks) != 0)
				return;

			// Playable players are fixed once the game starts, so this can be cached lazily.
			enemies ??= world.Players
				.Where(p => !p.NonCombatant && p.Playable && player.RelationshipWith(p) == PlayerRelationship.Enemy)
				.ToArray();

			enemyInOutage ??= new bool[enemies.Length];

			for (var i = 0; i < enemies.Length; i++)
			{
				var enemy = enemies[i];
				if (enemy.WinState != WinState.Undefined)
					continue;

				var power = enemy.PlayerActor.TraitOrDefault<PowerManager>();
				if (power == null)
					continue;

				// An outage lasts far longer than CheckIntervalTicks, so polling sees every one begin.
				var inOutage = power.PowerOutageRemainingTicks > 0;
				if (inOutage && !enemyInOutage[i])
					outagesSeen++;

				enemyInOutage[i] = inOutage;

				if (inOutage || power.PowerState != PowerState.Normal)
					lastSeenDownTick = tick;
			}

			var active = outagesSeen >= Info.MinimumOutages
				&& lastSeenDownTick != int.MinValue && tick - lastSeenDownTick <= Info.HoldTicks;
			if (active && token == Actor.InvalidConditionToken)
			{
				AIUtils.BotDebug("{0} sees an enemy grid down: pushing", player);
				token = player.PlayerActor.GrantCondition(Info.EnemyGridDownCondition);
			}
			else if (!active && token != Actor.InvalidConditionToken)
				token = player.PlayerActor.RevokeCondition(token);
		}

		protected override void TraitDisabled(Actor self)
		{
			if (token != Actor.InvalidConditionToken)
				token = self.RevokeCondition(token);
		}
	}
}
