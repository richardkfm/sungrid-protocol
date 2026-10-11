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
using System.IO;
using System.Linq;
using OpenRA.FileSystem;
using OpenRA.Mods.Common.MapGenerator;
using OpenRA.Mods.Common.Traits;
using OpenRA.Primitives;

namespace OpenRA.Mods.Sungrid.UtilityCommands
{
	// Runs one of the mod's map generators (rules/map-generators.yaml, the engine's classic
	// generator by default) headlessly and saves the result as a map package, so a batch of
	// seeds can be generated and compared from a script instead of one at a time in the editor.
	// The generated map is a starting point: titles, villages, Scrap and the rest are applied
	// afterwards. See docs/BACKLOG.md issue #133.
	sealed class GenerateMapCommand : IUtilityCommand
	{
		string IUtilityCommand.Name => "--generate-map";

		bool IUtilityCommand.ValidateArguments(string[] args)
		{
			return args.Length >= 2;
		}

		[Desc("OUT [Generator=classic] [Tileset=TEMPERAT] [Size=128,128] [Title=..] [Author=..] [Option=Value ...]",
			"Generate a map headlessly and save it to OUT (a directory, or an .oramap). " +
			"Option=Value sets any option of the generator's settings panel by its id (Seed, Players, " +
			"TerrainType, Shape, Symmetry, Resources, Buildings, Density, CivilianDensity, ...).")]
		void IUtilityCommand.Run(Utility utility, string[] args)
		{
			var modData = Game.ModData = utility.ModData;
			var outPath = args[1];
			var options = new Dictionary<string, string>();
			foreach (var arg in args.Skip(2))
			{
				var split = arg.Split('=', 2);
				if (split.Length != 2)
					throw new ArgumentException($"Expected Option=Value, got '{arg}'");
				options[split[0]] = split[1];
			}

			var generatorType = options.TryGetValue("Generator", out var g) ? g : "classic";
			var tileset = options.TryGetValue("Tileset", out var t) ? t : "TEMPERAT";
			var size = options.TryGetValue("Size", out var s) ? FieldLoader.GetValue<Size>("Size", s) : new Size(128, 128);

			var generator = modData.DefaultRules.Actors[SystemActors.EditorWorld]
				.TraitInfos<IEditorMapGeneratorInfo>()
				.FirstOrDefault(i => i.Type == generatorType)
				?? throw new ArgumentException($"No map generator of type '{generatorType}'");

			if (!generator.Tilesets.Contains(tileset))
				throw new ArgumentException($"Generator '{generatorType}' does not support tileset '{tileset}'");

			var settings = generator.GetSettings();
			foreach (var option in settings.Options)
			{
				if (!options.TryGetValue(option.Id, out var value))
					continue;

				switch (option)
				{
					case MapGeneratorBooleanOption bo: bo.Value = FieldLoader.GetValue<bool>(option.Id, value); break;
					case MapGeneratorIntegerOption io: io.Value = FieldLoader.GetValue<int>(option.Id, value); break;
					case MapGeneratorMultiIntegerChoiceOption mio: mio.Value = FieldLoader.GetValue<int>(option.Id, value); break;
					case MapGeneratorMultiChoiceOption mo: mo.Value = value; break;
				}
			}

			var terrainInfo = modData.DefaultTerrainInfo[tileset];
			var generationArgs = settings.Compile(terrainInfo, size);
			if (options.TryGetValue("Title", out var title))
				generationArgs.Title = title;
			if (options.TryGetValue("Author", out var author))
				generationArgs.Author = author;

			var map = generator.Generate(modData, generationArgs);
			map.Title = generationArgs.Title;
			map.Author = generationArgs.Author;

			IReadWritePackage package;
			if (outPath.EndsWith(".oramap", StringComparison.OrdinalIgnoreCase))
			{
				if (File.Exists(outPath))
					File.Delete(outPath);
				package = ZipFileLoader.Create(outPath);
			}
			else
			{
				Directory.CreateDirectory(outPath);
				package = new Folder(outPath);
			}

			using (package)
			{
				map.Save(package);
				Console.WriteLine($"{outPath}: {map.Title} ({tileset} {size.Width}x{size.Height}, {settings.PlayerCount} players) uid {map.Uid}");
			}
		}
	}
}
