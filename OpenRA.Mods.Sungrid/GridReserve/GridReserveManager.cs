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
using System.Linq;
using OpenRA.Graphics;
using OpenRA.Traits;

namespace OpenRA.Mods.Sungrid.GridReserve
{
	[TraitLocation(SystemActors.Player)]
	[Desc("Tracks a player's Grid Reserve total across all of their Vaults and the map's Reserve target.",
		"Pair with GridReserveController on the world actor to enable the Grid Reserve economic victory mode.")]
	public class GridReserveManagerInfo : TraitInfo
	{
		[Desc("Baseline Reserve target contributed per active player.")]
		public readonly int BaseTargetPerPlayer = 15000;

		[Desc("Per-mille (of 1000) discount applied to the target for each active player beyond the second.",
			"E.g. 75 = 7.5% cheaper per additional player past two, capped at a 100% discount.",
			"Starting values only; see docs/GAME_MODES.md for the example target table these approximate.")]
		public readonly int TargetDiscountPerMillePerExtraPlayer = 75;

		[Desc("Percentage (0-100) of the Reserve target at which this player's Vaults become permanently visible to opponents.")]
		public readonly int MinimapRevealPercent = 50;

		public override object Create(ActorInitializer init) { return new GridReserveManager(this); }
	}

	public class GridReserveManager : IWorldLoaded, ISync
	{
		readonly GridReserveManagerInfo info;
		readonly List<GridReserveVault> vaults = [];

		[VerifySync]
		public int TotalReserve { get; private set; }

		[VerifySync]
		public int Target { get; private set; }

		// Resolved once from the "gridreserve" lobby checkbox. Vaults must not deposit Credits into
		// Reserve at all when the mode is off, since deposits are irreversible and off-mode games have
		// no UI, win condition, or way to ever get that money back.
		public bool Enabled { get; private set; }

		// Cross-multiplied instead of dividing to keep the comparison exact in integer math.
		public bool BeaconActive => Enabled && Target > 0 && TotalReserve * 100 >= Target * info.MinimapRevealPercent;

		public bool LockdownEligible => Enabled && Target > 0 && TotalReserve >= Target;

		public GridReserveManager(GridReserveManagerInfo info)
		{
			this.info = info;
		}

		void IWorldLoaded.WorldLoaded(World w, WorldRenderer wr)
		{
			Enabled = w.LobbyInfo.GlobalSettings.OptionOrDefault("gridreserve", false);

			var activePlayers = w.Players.Count(p => !p.NonCombatant && p.Playable);
			if (activePlayers <= 0)
			{
				Target = 0;
				return;
			}

			var extra = Math.Max(0, activePlayers - 2);
			var discount = Math.Min(1000, info.TargetDiscountPerMillePerExtraPlayer * extra);
			Target = info.BaseTargetPerPlayer * activePlayers * (1000 - discount) / 1000;
		}

		public void RegisterVault(GridReserveVault vault) { vaults.Add(vault); }

		public void UnregisterVault(GridReserveVault vault) { vaults.Remove(vault); }

		public void AddReserve(int delta)
		{
			TotalReserve = Math.Max(0, TotalReserve + delta);
		}

		public void ApplyDecay(int percent)
		{
			if (percent <= 0)
				return;

			// PERF: Avoid LINQ in a path that runs across every Vault whenever Grid Decay is active.
			foreach (var vault in vaults)
			{
				var removed = vault.ApplyDecay(percent);
				if (removed > 0)
					AddReserve(-removed);
			}
		}
	}
}
