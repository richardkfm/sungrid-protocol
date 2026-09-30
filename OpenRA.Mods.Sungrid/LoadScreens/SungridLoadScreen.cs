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

using System.Reflection;
using OpenRA.FileSystem;
using OpenRA.Graphics;
using OpenRA.Mods.Common.LoadScreens;

namespace OpenRA.Mods.Sungrid.LoadScreens
{
	/// <summary>
	/// The stock logo-stripe load screen, plus an early window title (docs/BACKLOG.md issue #117).
	/// The engine creates its window titled "OpenRA" and only switches to the mod's WindowTitle at the very
	/// end of Game.InitializeMod, after every map has loaded - so the window and its Windows taskbar button
	/// read "OpenRA" for the whole load. ModData initializes the mod's fluent strings immediately before it
	/// creates the load screen, so Init is the earliest point the translated title exists.
	/// LogoStripeLoadScreen is sealed, so it is wrapped rather than subclassed: its drawing is unchanged.
	/// </summary>
	public sealed class SungridLoadScreen : SheetLoadScreen
	{
		// Renderer.Window is internal to OpenRA.Game; IPlatformWindow and its SetWindowTitle are public.
		// Going through them (rather than calling SDL directly) keeps the engine's own thread-affinity check.
		static readonly PropertyInfo RendererWindow =
			typeof(Renderer).GetProperty("Window", BindingFlags.Instance | BindingFlags.NonPublic);

		readonly LogoStripeLoadScreen stripe = new();

		public override void Init(Manifest manifest, IReadOnlyFileSystem fileSystem)
		{
			base.Init(manifest, fileSystem);
			stripe.Init(manifest, fileSystem);

			var title = manifest.Metadata.WindowTitleTranslated;
			if (Game.Renderer != null && !string.IsNullOrEmpty(title) && RendererWindow?.GetValue(Game.Renderer) is IPlatformWindow window)
				window.SetWindowTitle(title);
		}

		public override void DisplayInner(Renderer r, Sheet s, int density)
		{
			stripe.DisplayInner(r, s, density);
		}

		protected override void Dispose(bool disposing)
		{
			if (disposing)
				stripe.Dispose();

			base.Dispose(disposing);
		}
	}
}
