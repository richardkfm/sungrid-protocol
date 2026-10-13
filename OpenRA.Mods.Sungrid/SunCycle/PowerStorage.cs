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
using OpenRA.Mods.Sungrid.GridReserve;
using OpenRA.Primitives;
using OpenRA.Traits;

namespace OpenRA.Mods.Sungrid.SunCycle
{
	[Desc("Lets a building store surplus power and give it back when the grid runs short (the Sun Cycle's",
		"Battery Bank). Charge is held in power-seconds and moved once a second by PowerStorageManager on the",
		"owner's player actor. If the actor also has a GridReserveVault, the two share that Vault's Capacity at",
		"ChargeExchangePercent, energy first: ProtectedChargePercent of the space is kept for charge and Reserve can",
		"never bank into it, and a bank that is absorbing surplus power banks no Reserve until it stops. Banked",
		"Reserve is never displaced to make room for charge. With Grid Reserve off the whole Capacity holds charge.",
		"Does nothing at all while the suncycle lobby option is off, and then the Vault keeps its whole Capacity.",
		"Wiring: the actor's always-on Power drain must carry `RequiresCondition: !<DischargingCondition>`, and a",
		"second `Power@DISCHARGE` with `Amount: 1` and `RequiresCondition: <DischargingCondition>` carries the output.",
		"This trait is the IPowerModifier that scales that 1 up to the bank's output, which is why no other Power",
		"trait on the actor may be enabled while it discharges.")]
	public class PowerStorageInfo : TraitInfo, Requires<PowerInfo>
	{
		[Desc("Space in credit-equivalents when the actor has no GridReserveVault. With a Vault, the Vault's",
			"Capacity is used instead so there is one number to tune.")]
		public readonly int Capacity = 8000;

		[Desc("Power-seconds of charge one hundred credits of space holds. 100 is the shipped 1:1 exchange rate.")]
		public readonly int ChargeExchangePercent = 100;

		[Desc("Percentage of the bank's space kept for charge while Grid Reserve is on: Reserve credits can never",
			"occupy it, so a bank always has room for at least this share of its energy, however much Reserve the",
			"owner has banked. 33 leaves a plain 8000 bank 5360 of Reserve. Applies to the space, so a",
			"PowerStorageMultiplier capacity bonus scales the energy that fits in it. Ignored with the cycle off.")]
		public readonly int ProtectedChargePercent = 33;

		[Desc("Most surplus power the bank absorbs, per second.")]
		public readonly int ChargeRate = 40;

		[Desc("Most power the bank supplies to the grid, per second, while it discharges.")]
		public readonly int DischargeRate = 60;

		[FieldLoader.Require]
		[GrantedConditionReference]
		[Desc("Condition granted while the bank discharges. Switches the upkeep Power off and Power@DISCHARGE on.")]
		public readonly string DischargingCondition = null;

		[Desc("Colour of the charge bar shown under a selected bank.")]
		public readonly Color SelectionBarColor = Color.FromArgb(0x5A, 0xB4, 0xE6);

		// Space (credit-equivalents) of a bank with `space` that Reserve can never occupy while the cycle is on.
		// One formula for the trait and for the bots, which size their Vault count before any bank exists.
		public int ProtectedSpace(int space) => (int)((long)space * Math.Clamp(ProtectedChargePercent, 0, 100) / 100);

		public override object Create(ActorInitializer init) { return new PowerStorage(init.Self, this); }
	}

	public class PowerStorage : IPowerModifier, ISync, ISelectionBar, INotifyCreated, INotifyAddedToWorld,
		INotifyRemovedFromWorld, INotifyOwnerChanged
	{
		public readonly PowerStorageInfo Info;

		// What the bank costs the grid while idle (its upkeep), as a positive number. While it discharges that
		// upkeep is switched off and paid from the charge instead, so "gross" below is output plus upkeep.
		public readonly int IdleDraw;

		PowerManager power;
		PowerStorageManager manager;
		GridReserveVault vault;
		SunCycleController controller;
		PowerStorageMultiplier[] multipliers = [];

		int token = Actor.InvalidConditionToken;

		[VerifySync]
		public int Charge { get; private set; }

		[VerifySync]
		public int Output { get; private set; }

		public bool IsDischarging { get; private set; }

		// Absorbed surplus in the manager's last update. Energy first: while this is set the bank banks no Reserve,
		// so Reserve only ever takes space surplus power is not flowing into right now.
		[VerifySync]
		public bool IsCharging { get; private set; }

		// World tick at which this bank last gave power (or was placed). See IdleCharge.
		[VerifySync]
		int lastUsedTick;

		World world;

		public PowerStorage(Actor self, PowerStorageInfo info)
		{
			Info = info;
			IdleDraw = -self.Info.TraitInfos<PowerInfo>().Where(p => p.EnabledByDefault).Sum(p => p.Amount);
			power = self.Owner.PlayerActor.Trait<PowerManager>();
			manager = self.Owner.PlayerActor.Trait<PowerStorageManager>();
		}

		void INotifyCreated.Created(Actor self)
		{
			world = self.World;
			vault = self.TraitOrDefault<GridReserveVault>();
			controller = self.World.WorldActor.TraitOrDefault<SunCycleController>();
			multipliers = self.TraitsImplementing<PowerStorageMultiplier>().ToArray();
		}

		public bool Enabled => controller != null && controller.Enabled;

		// The power this bank is currently adding to its owner's grid relative to standing idle.
		public int Gross => IsDischarging ? Output + IdleDraw : 0;

		public int SpaceCapacity => vault?.Capacity ?? Info.Capacity;

		public int ReserveHeld => vault?.CurrentReserve ?? 0;

		int Modified(int value, Func<PowerStorageMultiplierInfo, int> modifier)
		{
			return Util.ApplyPercentageModifiers(value, multipliers.Where(m => !m.IsTraitDisabled).Select(m => modifier(m.Info)));
		}

		public int ChargeExchange => Math.Max(1, Modified(Info.ChargeExchangePercent, m => m.CapacityModifier));

		public int ChargeRate => Math.Max(0, Modified(Info.ChargeRate, m => m.ChargeRateModifier));

		public int DischargeRate => Math.Max(0, Modified(Info.DischargeRate, m => m.DischargeRateModifier));

		// Charge the bank could hold if it held no Reserve at all.
		public int FullCharge => (int)((long)SpaceCapacity * ChargeExchange / 100);

		// Charge the bank can hold right now: the space Reserve has not already taken.
		public int MaxCharge => Math.Max(0, (int)((long)(SpaceCapacity - ReserveHeld) * ChargeExchange / 100));

		// Credit-equivalents of space the stored charge occupies. Rounded up, so charge and Reserve together
		// can never exceed the bank's Capacity: Charge <= floor(free * exchange / 100) implies this <= free.
		public int OccupiedSpace => Charge <= 0 ? 0 : (int)(((long)Charge * 100 + ChargeExchange - 1) / ChargeExchange);

		// Space Reserve can never occupy: the protected share, kept for energy. Zero with the cycle off, so the
		// Vault keeps its whole Capacity for Reserve exactly as before.
		public int ProtectedSpace => Enabled ? Info.ProtectedSpace(SpaceCapacity) : 0;

		// The most Reserve this bank can ever hold.
		public int ReserveCapacity => SpaceCapacity - ProtectedSpace;

		// Charge that fits in the protected share alone: the energy this bank can always store.
		public int ProtectedCharge => (int)((long)ProtectedSpace * ChargeExchange / 100);

		// Credit-equivalents of stored charge sitting outside the protected share, i.e. in space Reserve could
		// otherwise use.
		public int UnprotectedOccupiedSpace => Math.Max(0, OccupiedSpace - ProtectedSpace);

		// Charge that has not been drawn on for a whole sun cycle - a bank whose owner never runs short, so it
		// fills by day and never empties. Energy comes first, so without an exit that charge would hold the whole
		// bank for the rest of the match and Grid Reserve could never bank into it: a player who built enough
		// night-proof power (the Assembly's whole night identity) would have locked themselves out of the economic
		// victory. Idle charge outside the protected share gives way to Reserve deposits; the protected share
		// stays energy whatever happens.
		public bool IdleCharge => Enabled && Charge > 0 && world.WorldTick - lastUsedTick >= controller.Info.CycleTicks;

		// Space a Reserve deposit may take from stored charge.
		public int YieldableSpace => IdleCharge ? UnprotectedOccupiedSpace : 0;

		// Credits of Reserve that may be banked into this bank right now (GridReserveVault reads this; only while
		// the cycle is on). Energy first: nothing while the bank is absorbing surplus, never into the protected
		// share, and never into space stored charge occupies unless that charge is idle.
		public int ReserveRoom
		{
			get
			{
				if (IsCharging)
					return 0;

				var held = ReserveHeld;
				var free = SpaceCapacity - held - OccupiedSpace + YieldableSpace;
				return Math.Max(0, Math.Min(ReserveCapacity - held, free));
			}
		}

		// After a deposit into yieldable space: drop whatever charge no longer fits beside the Reserve.
		public void YieldToReserve()
		{
			ClampToSpace();
		}

		internal void SetCharging(bool charging)
		{
			IsCharging = charging;
		}

		internal void AddCharge(int amount)
		{
			Charge = Math.Clamp(Charge + amount, 0, Math.Max(Charge, MaxCharge));
		}

		// Called by the manager before it plans each second, and after a deposit into idle charge's space. A
		// capacity multiplier switching off can also shrink the room under existing charge. Either way the
		// charge that no longer fits is lost; Reserve is never pushed out.
		internal void ClampToSpace()
		{
			var max = MaxCharge;
			if (Charge > max)
				Charge = max;
		}

		// Supplies `output` power (>= 0) to the grid for the coming second; negative stops discharging.
		internal void SetOutput(Actor self, int output)
		{
			if (output < 0)
			{
				if (!IsDischarging && token == Actor.InvalidConditionToken)
					return;

				// Order matters: the modifier goes back to 100 before the upkeep Power is re-enabled, so the grid
				// never sees the upkeep scaled by the old output, even for the length of one condition update.
				IsDischarging = false;
				Output = 0;
				if (token != Actor.InvalidConditionToken)
					token = self.RevokeCondition(token);

				power.UpdateActor(self);
				return;
			}

			// And the reverse here: the condition goes on while the modifier still reads 100, which switches the
			// upkeep off and the 1-power discharge trait on, then the output is set and re-totalled.
			if (token == Actor.InvalidConditionToken)
				token = self.GrantCondition(Info.DischargingCondition);

			lastUsedTick = self.World.WorldTick;
			if (IsDischarging && Output == output)
				return;

			IsDischarging = true;
			Output = output;
			power.UpdateActor(self);
		}

		// A Spy's infiltration (InfiltrateForChargeDrain). Reserve credits in the same building are untouched.
		public void Drain(Actor self, int percent)
		{
			if (Charge <= 0 || percent <= 0)
				return;

			Charge -= (int)((long)Charge * Math.Min(percent, 100) / 100);
			if (Charge <= 0)
				SetOutput(self, -1);
		}

		int IPowerModifier.GetPowerModifier() { return IsDischarging ? Output * 100 : 100; }

		void INotifyAddedToWorld.AddedToWorld(Actor self)
		{
			lastUsedTick = self.World.WorldTick;
			manager.Register(self, this);
		}

		void INotifyRemovedFromWorld.RemovedFromWorld(Actor self)
		{
			// Killed, sold or otherwise gone: the stored energy goes with it. No reward to anyone, so a battery
			// kill is never a second payout on top of the Vault's raid reward.
			manager.Unregister(this);
			Charge = 0;
			Output = 0;
			IsDischarging = false;
			IsCharging = false;
		}

		void INotifyOwnerChanged.OnOwnerChanged(Actor self, Player oldOwner, Player newOwner)
		{
			// Captured: stop discharging and move to the new owner's manager; the charge is the captor's now.
			// No explicit PowerManager re-total here - the Power traits follow the owner change themselves, and
			// depending on trait order calling the old manager could re-add this actor to the old owner's grid.
			IsDischarging = false;
			IsCharging = false;
			Output = 0;
			if (token != Actor.InvalidConditionToken)
				token = self.RevokeCondition(token);

			manager.Unregister(this);
			power = newOwner.PlayerActor.Trait<PowerManager>();
			manager = newOwner.PlayerActor.Trait<PowerStorageManager>();
			lastUsedTick = self.World.WorldTick;
			if (self.IsInWorld)
				manager.Register(self, this);
		}

		float ISelectionBar.GetValue()
		{
			if (!Enabled)
				return 0;

			var full = FullCharge;
			return full > 0 ? (float)Charge / full : 0;
		}

		Color ISelectionBar.GetColor() { return Info.SelectionBarColor; }

		bool ISelectionBar.DisplayWhenEmpty => Enabled;
	}
}
