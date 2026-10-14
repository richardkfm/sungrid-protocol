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

namespace OpenRA.Mods.Sungrid.GridReserve
{
	[TraitLocation(SystemActors.Player)]
	[Desc("Raises the spendable Credits this player's Vaults never bank below (GridReserveVault.MinimumOperatingBalance)",
		"while enabled. For bots: their base builders only add production and expansions above a cash threshold",
		"(NewProductionCashThreshold, BuildAdditionalMCVCashAmount), and a Vault holding cash at the 3000 floor kept",
		"them below it for the rest of the match. Drive it with a condition every client agrees on, such as",
		"GrantConditionOnBotOwner's - Vaults are synced, so a bot module's condition (host only) would desync.",
		"See docs/BACKLOG.md issue #141.")]
	public class GridReserveOperatingBalanceInfo : ConditionalTraitInfo
	{
		[Desc("Spendable Credits the player's Vaults never draw below while this trait is enabled.")]
		public readonly int MinimumOperatingBalance = 3000;

		public override object Create(ActorInitializer init) { return new GridReserveOperatingBalance(this); }
	}

	public class GridReserveOperatingBalance : ConditionalTrait<GridReserveOperatingBalanceInfo>
	{
		public GridReserveOperatingBalance(GridReserveOperatingBalanceInfo info)
			: base(info) { }
	}
}
