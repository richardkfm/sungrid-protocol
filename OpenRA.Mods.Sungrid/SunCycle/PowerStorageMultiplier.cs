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

using OpenRA.Mods.Common.Traits;
using OpenRA.Traits;

namespace OpenRA.Mods.Sungrid.SunCycle
{
	[Desc("Modifies a PowerStorage bank's charge capacity and charge/discharge rates while enabled.",
		"Meant for faction identity (e.g. RequiresCondition on a GrantConditionOnFaction condition).",
		"Affects stored charge only, never the Grid Reserve credits the same building may hold.")]
	public class PowerStorageMultiplierInfo : ConditionalTraitInfo, Requires<PowerStorageInfo>
	{
		[Desc("Percentage applied to how much charge one credit of bank space holds (the charge capacity).")]
		public readonly int CapacityModifier = 100;

		[Desc("Percentage applied to the bank's maximum charge rate.")]
		public readonly int ChargeRateModifier = 100;

		[Desc("Percentage applied to the bank's maximum discharge rate.")]
		public readonly int DischargeRateModifier = 100;

		public override object Create(ActorInitializer init) { return new PowerStorageMultiplier(this); }
	}

	public class PowerStorageMultiplier : ConditionalTrait<PowerStorageMultiplierInfo>
	{
		public PowerStorageMultiplier(PowerStorageMultiplierInfo info)
			: base(info) { }
	}
}
