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
using System.Collections.Generic;
using OpenRA.Mods.Common.Traits;
using OpenRA.Traits;

namespace OpenRA.Mods.Sungrid.SunCycle
{
	[TraitLocation(SystemActors.Player)]
	[Desc("Moves energy in and out of the player's PowerStorage banks once a second while the Sun Cycle is on.",
		"Surplus power charges the banks; a deficit is covered from them, up to each bank's discharge rate.",
		"Charging draws nothing from the grid - it only ever takes surplus - so it can never push a player",
		"into low power. Banks do not discharge during a power outage (a Spy on a power plant).")]
	public class PowerStorageManagerInfo : TraitInfo, Requires<PowerManagerInfo>
	{
		public override object Create(ActorInitializer init) { return new PowerStorageManager(init.Self); }
	}

	public class PowerStorageManager : ITick, INotifyCreated
	{
		// Rates are per second, and one second is 25 ticks (Normal speed), the same convention as the Grid
		// Reserve documentation. Updating once a second keeps every quantity a whole number of power-seconds:
		// no fractions, no floating point, nothing that could drift between clients.
		const int UpdateInterval = 25;

		readonly PowerManager power;

		// Kept sorted by ActorID so the allocation below visits banks in the same order on every client.
		readonly List<(Actor Actor, PowerStorage Storage)> banks = [];

		SunCycleController controller;

		// Net energy moved in the last update, per second: positive while charging, negative while discharging.
		public int Flow { get; private set; }

		public PowerStorageManager(Actor self)
		{
			power = self.Trait<PowerManager>();
		}

		void INotifyCreated.Created(Actor self)
		{
			// Player actors are created after the world actor, so the controller's own Created (which resolves
			// the lobby option) has already run.
			controller = self.World.WorldActor.TraitOrDefault<SunCycleController>();
		}

		public int BankCount => banks.Count;

		public int TotalCharge
		{
			get
			{
				var total = 0;
				foreach (var b in banks)
					total += b.Storage.Charge;
				return total;
			}
		}

		// Charge the banks could hold right now, given the space Grid Reserve credits already occupy.
		public int TotalMaxCharge
		{
			get
			{
				var total = 0;
				foreach (var b in banks)
					total += b.Storage.MaxCharge;
				return total;
			}
		}

		// Charge the banks could hold if no Reserve were banked in them.
		public int TotalFullCharge
		{
			get
			{
				var total = 0;
				foreach (var b in banks)
					total += b.Storage.FullCharge;
				return total;
			}
		}

		// Credit-equivalents of bank space stored charge occupies (Reserve's competitor for the same space).
		public int TotalOccupiedSpace
		{
			get
			{
				var total = 0;
				foreach (var b in banks)
					total += b.Storage.OccupiedSpace;
				return total;
			}
		}

		// Power the banks are adding to the grid right now, relative to standing idle.
		public int TotalGross
		{
			get
			{
				var total = 0;
				foreach (var b in banks)
					total += b.Storage.Gross;
				return total;
			}
		}

		public int TotalDischargeRate
		{
			get
			{
				var total = 0;
				foreach (var b in banks)
					total += b.Storage.DischargeRate;
				return total;
			}
		}

		internal void Register(Actor actor, PowerStorage storage)
		{
			if (banks.Exists(b => b.Storage == storage))
				return;

			banks.Add((actor, storage));
			banks.Sort((a, b) => a.Actor.ActorID.CompareTo(b.Actor.ActorID));
		}

		internal void Unregister(PowerStorage storage)
		{
			banks.RemoveAll(b => b.Storage == storage);
		}

		void ITick.Tick(Actor self)
		{
			if (controller == null || !controller.Enabled || self.World.WorldTick % UpdateInterval != 0)
				return;

			// The grid as it would stand with every bank idle: what the banks are adding right now comes off.
			var baseExcess = power.ExcessPower;
			foreach (var b in banks)
			{
				b.Storage.ClampToSpace();
				baseExcess -= b.Storage.Gross;
			}

			var flow = 0;
			if (baseExcess < 0 && power.PowerOutageRemainingTicks <= 0)
			{
				// Cover the deficit, earliest-built bank first. Each discharging bank switches its own upkeep
				// off and pays it from the charge, so a bank's improvement to the grid ("gross") is its output
				// plus that upkeep, and gross is also what it spends. Paid up front for the coming interval.
				var need = -baseExcess;
				foreach (var (actor, storage) in banks)
				{
					var perSecond = 0;
					if (need > 0)
					{
						var max = Math.Min(storage.DischargeRate + storage.IdleDraw, storage.Charge);
						var min = Math.Max(storage.IdleDraw, 1);
						if (max >= min)
							perSecond = Math.Clamp(need, min, max);
					}

					if (perSecond <= 0)
					{
						storage.SetOutput(actor, -1);
						continue;
					}

					storage.SetOutput(actor, perSecond - storage.IdleDraw);
					storage.AddCharge(-perSecond);
					need -= perSecond;
					flow -= perSecond;
				}
			}
			else
			{
				// Outage or surplus: nothing discharges. A blackout leaves the charge where it is.
				foreach (var (actor, storage) in banks)
					storage.SetOutput(actor, -1);

				var surplus = baseExcess;
				foreach (var (_, storage) in banks)
				{
					if (surplus <= 0)
						break;

					var room = storage.MaxCharge - storage.Charge;
					var perSecond = Math.Min(surplus, Math.Min(storage.ChargeRate, room));
					if (perSecond <= 0)
						continue;

					storage.AddCharge(perSecond);
					surplus -= perSecond;
					flow += perSecond;
				}
			}

			Flow = flow;
		}
	}
}
