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

using OpenRA.Widgets;

namespace OpenRA.Mods.Sungrid.GridReserve
{
	[Desc("Attach to the Grid Reserve rules popup in ingame-player.yaml. Shows once when the match",
		"starts with the gridreserve lobby option on, and hides itself entirely when it is off.")]
	public class GridReserveBriefingLogic : ChromeLogic
	{
		[ObjectCreator.UseCtor]
		public GridReserveBriefingLogic(Widget widget, World world)
		{
			var controller = world.WorldActor.TraitOrDefault<GridReserveController>();
			if (controller == null || !controller.Enabled)
			{
				widget.IsVisible = () => false;
				return;
			}

			var dismissed = false;
			widget.IsVisible = () => !dismissed;

			var closeButton = widget.Get<ButtonWidget>("CLOSE_BUTTON");
			closeButton.OnClick = () => dismissed = true;
		}
	}
}
