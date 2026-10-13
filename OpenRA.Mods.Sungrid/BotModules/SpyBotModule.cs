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
using System.Collections.Generic;
using System.Linq;
using OpenRA.Mods.Common;
using OpenRA.Mods.Common.Traits;
using OpenRA.Traits;

namespace OpenRA.Mods.Sungrid.BotModules
{
	[TraitLocation(SystemActors.Player)]
	[Desc("Sends the bot's Spies (or any other infiltrating unit) into enemy buildings. No engine bot module ever orders an",
		"infiltration, so without this a bot Spy only walks into the enemy base with an assault squad.",
		"Runs are paced, disguised where the unit can disguise, aimed away from enemy defences and from where the bot's",
		"diversion is expected to strike, and optionally preceded by a condition that enables a diversion squad manager.",
		"Keep the infiltrators out of every SquadManagerBotModule (ExcludeFromSquadsTypes). See docs/BACKLOG.md issue #135.")]
	public class SpyBotModuleInfo : ConditionalTraitInfo
	{
		[FieldLoader.Require]
		[ActorReference]
		[Desc("Own actor types this module sends to infiltrate. Each only goes for targets its own infiltrate order",
			"accepts, so one list can hold a Spy and a Thief.")]
		public readonly FrozenSet<string> InfiltratorTypes = FrozenSet<string>.Empty;

		[FieldLoader.Require]
		[ActorReference(dictionaryReference: LintDictionaryReference.Keys)]
		[Desc("Enemy actor types to infiltrate, each with a priority measured in cells: how much further an",
			"infiltrator will walk for this target than for one with priority 0. A dictionary of [actor id]: [cells].")]
		public readonly FrozenDictionary<string, int> TargetPriorities = FrozenDictionary<string, int>.Empty;

		[ActorReference]
		[Desc("Enemy actor types that make a target more dangerous to reach (defences, and units that see through",
			"a disguise).")]
		public readonly FrozenSet<string> DefenceTypes = FrozenSet<string>.Empty;

		[Desc("Radius in cells around a target in which DefenceTypes are counted.")]
		public readonly int DefenceScanRadius = 6;

		[Desc("Each DefenceTypes actor near a target counts as this many cells of extra walk.")]
		public readonly int DefenceCost = 8;

		[ActorReference]
		[Desc("Enemy actor types the diversion is expected to strike: the closest one to an infiltrator stands in for",
			"where the diversion lands. Keep in step with the diversion squad manager's PreferredTargetTypes.")]
		public readonly FrozenSet<string> DiversionTargetTypes = FrozenSet<string>.Empty;

		[Desc("A target up to this many cells away from the expected diversion point is credited one cell of walk per",
			"cell of separation, so infiltrators go for the other side of the base from the noise.")]
		public readonly int DiversionSeparation = 12;

		[Desc("Order string of the infiltrate order, as the infiltrating trait issues it.")]
		public readonly string InfiltrateOrder = "Infiltrate";

		[Desc("Order string of the disguise order. An infiltrator that offers it disguises as an enemy unit of the",
			"target's owner before setting off. Empty to never disguise.")]
		public readonly string DisguiseOrder = "Disguise";

		[Desc("Skip power producers of a player already in a power outage: one infiltration blacks out the whole grid,",
			"and another while it lasts only restarts the timer.")]
		public readonly bool IgnoreBlackedOutGrids = true;

		[Desc("Don't start a run before this tick.")]
		public readonly int StartDelayTicks = 0;

		[Desc("Minimum ticks between the start of one run and the next.")]
		public readonly int RunIntervalTicks = 2250;

		[Desc("Most idle infiltrators sent in one run.")]
		public readonly int MaximumInfiltratorsPerRun = 2;

		[GrantedConditionReference]
		[Desc("Condition granted on the player actor for DiversionDurationTicks from the start of each run. A hook for",
			"RequiresCondition on a diversion squad manager. Bots only run on the host, so only other bot modules may",
			"consume it - never a synced trait.")]
		public readonly string DiversionCondition = null;

		[Desc("Ticks between granting DiversionCondition and sending the infiltrators, so the diversion is moving first.")]
		public readonly int DiversionLeadTicks = 250;

		[Desc("Ticks DiversionCondition is held from the start of a run.")]
		public readonly int DiversionDurationTicks = 1500;

		[Desc("Ticks between checks for idle infiltrators and finished missions.")]
		public readonly int CheckIntervalTicks = 50;

		public override void RulesetLoaded(Ruleset rules, ActorInfo ai)
		{
			base.RulesetLoaded(rules, ai);

			if (MaximumInfiltratorsPerRun < 1)
				throw new YamlException("MaximumInfiltratorsPerRun must be at least 1.");

			if (DiversionLeadTicks < 0 || DiversionDurationTicks < 0 || RunIntervalTicks < 0)
				throw new YamlException("DiversionLeadTicks, DiversionDurationTicks and RunIntervalTicks must not be negative.");
		}

		public override object Create(ActorInitializer init) { return new SpyBotModule(init.Self, this); }
	}

	public class SpyBotModule : ConditionalTrait<SpyBotModuleInfo>, IBotTick
	{
		// Bot orders reach the order manager a few ticks after they are queued, so an infiltrator that was
		// just sent still reads as idle for a moment. Don't treat it as back from its mission before this.
		const int OrderGraceTicks = 25;

		readonly World world;
		readonly Player player;

		// Infiltrators on a mission, with the tick they were sent.
		readonly Dictionary<Actor, int> missions = [];

		// Infiltrators chosen for the next run and their targets, waiting out DiversionLeadTicks.
		readonly List<(Actor Infiltrator, Actor Target)> pending = [];

		int nextRunTick;
		int launchTick;
		int diversionEndTick;
		int diversionToken = Actor.InvalidConditionToken;

		public SpyBotModule(Actor self, SpyBotModuleInfo info)
			: base(info)
		{
			world = self.World;
			player = self.Owner;
		}

		void IBotTick.BotTick(IBot bot)
		{
			var tick = world.WorldTick;

			if (diversionToken != Actor.InvalidConditionToken && tick >= diversionEndTick)
				diversionToken = player.PlayerActor.RevokeCondition(diversionToken);

			if (pending.Count > 0 && tick >= launchTick)
				Launch(bot, tick);

			if (tick % Math.Max(1, Info.CheckIntervalTicks) != 0)
				return;

			// Dead, disposed (a completed infiltration disposes the unit) or idle again (the target died or
			// could no longer be entered): either way the mission is over.
			var finished = missions
				.Where(m => !IsUsable(m.Key) || (m.Key.IsIdle && tick - m.Value > OrderGraceTicks))
				.Select(m => m.Key)
				.ToList();
			foreach (var a in finished)
				missions.Remove(a);

			if (tick < Info.StartDelayTicks || tick < nextRunTick || pending.Count > 0 || player.WinState != WinState.Undefined)
				return;

			PlanRun(tick);
		}

		bool IsUsable(Actor a)
		{
			return a != null && !a.IsDead && a.IsInWorld && a.Owner == player;
		}

		static bool IsValidTarget(Actor a)
		{
			return a != null && !a.IsDead && a.IsInWorld && a.Owner.WinState == WinState.Undefined;
		}

		void PlanRun(int tick)
		{
			var ready = world.ActorsHavingTrait<IPositionable>()
				.Where(a => a.Owner == player && Info.InfiltratorTypes.Contains(a.Info.Name)
					&& IsUsable(a) && a.IsIdle && !missions.ContainsKey(a))
				.OrderBy(a => a.ActorID)
				.Take(Info.MaximumInfiltratorsPerRun)
				.ToList();

			if (ready.Count == 0)
				return;

			var chosen = new HashSet<Actor>();
			foreach (var infiltrator in ready)
			{
				var target = ChooseTarget(infiltrator, chosen);
				if (target == null)
					continue;

				chosen.Add(target);
				pending.Add((infiltrator, target));
			}

			// Nothing worth entering (or nothing reachable): look again on a later check, not a whole interval later.
			if (pending.Count == 0)
				return;

			nextRunTick = tick + Info.RunIntervalTicks;
			launchTick = tick;

			if (!string.IsNullOrEmpty(Info.DiversionCondition))
			{
				launchTick = tick + Info.DiversionLeadTicks;
				diversionEndTick = tick + Info.DiversionDurationTicks;
				if (diversionToken == Actor.InvalidConditionToken)
					diversionToken = player.PlayerActor.GrantCondition(Info.DiversionCondition);
			}

			AIUtils.BotDebug("{0} plans an infiltration run with {1} unit(s)", player, pending.Count);
		}

		void Launch(IBot bot, int tick)
		{
			var chosen = new HashSet<Actor>(pending.Select(p => p.Target));
			foreach (var (infiltrator, plannedTarget) in pending)
			{
				if (!IsUsable(infiltrator))
					continue;

				// The planned target may have died, or its grid gone dark, during the diversion lead.
				var target = plannedTarget;
				if (!IsValidTarget(target) || !IsWorthEntering(infiltrator, target))
				{
					chosen.Remove(target);
					target = ChooseTarget(infiltrator, chosen);
					if (target == null)
						continue;

					chosen.Add(target);
				}

				if (!string.IsNullOrEmpty(Info.DisguiseOrder) && !(infiltrator.EffectiveOwner?.Disguised ?? false))
				{
					var disguise = ChooseDisguise(infiltrator, target.Owner);
					if (disguise != null)
						bot.QueueOrder(new Order(Info.DisguiseOrder, infiltrator, Target.FromActor(disguise), false));
				}

				// The same order a player gives by clicking the building with the unit selected.
				bot.QueueOrder(new Order(Info.InfiltrateOrder, infiltrator, Target.FromActor(target), false));
				missions[infiltrator] = tick;
				AIUtils.BotDebug("{0} sends {1} to infiltrate {2}", player, infiltrator, target);
			}

			pending.Clear();
		}

		bool IsWorthEntering(Actor infiltrator, Actor target)
		{
			if (!Info.TargetPriorities.ContainsKey(target.Info.Name)
				|| player.RelationshipWith(target.Owner) != PlayerRelationship.Enemy
				|| !CanIssue(infiltrator, Info.InfiltrateOrder, target))
				return false;

			if (Info.IgnoreBlackedOutGrids && target.Info.TraitInfos<PowerInfo>().Any(p => p.Amount > 0))
			{
				var power = target.Owner.PlayerActor.TraitOrDefault<PowerManager>();
				if (power != null && power.PowerOutageRemainingTicks > 0)
					return false;
			}

			return true;
		}

		Actor ChooseTarget(Actor infiltrator, HashSet<Actor> alreadyChosen)
		{
			var candidates = world.Actors
				.Where(a => IsValidTarget(a) && IsWorthEntering(infiltrator, a))
				.ToList();

			if (candidates.Count == 0)
				return null;

			// Where the diversion squad will most likely land: it starts from home, like the infiltrator, and goes
			// for the closest of its preferred types.
			WPos? diversionPoint = null;
			if (Info.DiversionTargetTypes.Count > 0)
			{
				var nearest = world.Actors
					.Where(a => Info.DiversionTargetTypes.Contains(a.Info.Name) && IsValidTarget(a)
						&& player.RelationshipWith(a.Owner) == PlayerRelationship.Enemy)
					.ClosestToIgnoringPath(infiltrator);
				diversionPoint = nearest?.CenterPosition;
			}

			// Lower is better, in cells. Sorted by ActorID first so ties resolve the same way every time.
			var scored = candidates
				.OrderBy(a => a.ActorID)
				.Select(a => (Actor: a, Cost: Cost(infiltrator, a, diversionPoint, alreadyChosen)))
				.OrderBy(x => x.Cost)
				.Select(x => x.Actor);

			// Path checks are the expensive part, so stop at the first reachable one.
			foreach (var target in scored)
				if (new[] { target }.WithPathFrom(infiltrator).Any())
					return target;

			return null;
		}

		int Cost(Actor infiltrator, Actor target, WPos? diversionPoint, HashSet<Actor> alreadyChosen)
		{
			var cost = Cells(infiltrator.CenterPosition, target.CenterPosition) - Info.TargetPriorities[target.Info.Name];

			if (Info.DefenceTypes.Count > 0)
			{
				var defences = world.FindActorsInCircle(target.CenterPosition, WDist.FromCells(Info.DefenceScanRadius))
					.Count(a => Info.DefenceTypes.Contains(a.Info.Name) && !a.IsDead
						&& player.RelationshipWith(a.Owner) == PlayerRelationship.Enemy);
				cost += defences * Info.DefenceCost;
			}

			if (diversionPoint.HasValue)
				cost -= Math.Min(Cells(diversionPoint.Value, target.CenterPosition), Info.DiversionSeparation);

			// Spread a run over different buildings where there is a choice: one defence or one unlucky path
			// should not catch every infiltrator at the same door.
			if (alreadyChosen.Contains(target))
				cost += Info.DefenceCost;

			return cost;
		}

		Actor ChooseDisguise(Actor infiltrator, Player targetOwner)
		{
			return world.Actors
				.Where(a => a.Owner == targetOwner && !a.IsDead && a.IsInWorld && CanIssue(infiltrator, Info.DisguiseOrder, a))
				.ClosestToIgnoringPath(infiltrator);
		}

		// Asks the unit's own order traits whether this order may target this actor, which is how a player's click
		// is resolved. Keeps the module free of any one infiltration or disguise implementation.
		static bool CanIssue(Actor self, string orderID, Actor target)
		{
			var t = Target.FromActor(target);
			foreach (var issuer in self.TraitsImplementing<IIssueOrder>())
			{
				foreach (var targeter in issuer.Orders)
				{
					if (targeter.OrderID != orderID)
						continue;

					var modifiers = TargetModifiers.None;
					string cursor = null;
					if (targeter.CanTarget(self, t, ref modifiers, ref cursor))
						return true;
				}
			}

			return false;
		}

		static int Cells(WPos a, WPos b)
		{
			return (a - b).HorizontalLength / 1024;
		}

		protected override void TraitDisabled(Actor self)
		{
			pending.Clear();
			missions.Clear();
			if (diversionToken != Actor.InvalidConditionToken)
				diversionToken = self.RevokeCondition(diversionToken);
		}
	}
}
