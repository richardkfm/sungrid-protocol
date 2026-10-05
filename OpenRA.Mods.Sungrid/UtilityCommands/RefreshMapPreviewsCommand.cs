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
using System.IO;
using OpenRA.FileSystem;

namespace OpenRA.Mods.Sungrid.UtilityCommands
{
	// A map's map.png preview is rendered from the tileset's terrain-type colours when the map is
	// saved, and the 75 ported maps were last saved on stock Red Alert's tan palette. This re-saves
	// each map package in place so the preview (and the lobby minimap) follow the reskinned
	// tilesets. Nothing else about the map changes except the normalised map.yaml serialisation
	// Map.Save always produces. See docs/BACKLOG.md issue #119.
	sealed class RefreshMapPreviewsCommand : IUtilityCommand
	{
		string IUtilityCommand.Name => "--refresh-map-previews";

		bool IUtilityCommand.ValidateArguments(string[] args)
		{
			return args.Length >= 2;
		}

		[Desc("MAP [MAP ...]", "Re-save each map package (a directory or an .oramap) so its map.png preview is rendered from the current tileset colours.")]
		void IUtilityCommand.Run(Utility utility, string[] args)
		{
			var modData = Game.ModData = utility.ModData;
			var folder = new Folder(Platform.EngineDir);
			for (var i = 1; i < args.Length; i++)
			{
				if (folder.OpenPackage(args[i], modData.ModFiles) is not IReadWritePackage package)
					throw new FileNotFoundException(args[i]);

				using (package)
				{
					var map = new Map(modData, package);
					map.Save(package);
					Console.WriteLine($"{args[i]}: {map.Title} - preview refreshed");
				}
			}
		}
	}
}
