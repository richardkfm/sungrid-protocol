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

using OpenRA.Graphics;
using OpenRA.Mods.Common.Traits;
using OpenRA.Traits;

namespace OpenRA.Mods.Sungrid.SunCycle
{
	[TraitLocation(SystemActors.World)]
	[Desc("Tints the battlefield through the Sun Cycle: warm at dusk and dawn, cool and dim at night.",
		"A separate post-process pass from the map's own TintPostProcessEffect, so the two multiply and a map",
		"that sets its own tint (snow, desert, nuclear winter) keeps its character at night.",
		"Inactive whenever the suncycle lobby option is off. Requires SunCycleController.")]
	public class SunCycleTintInfo : TraitInfo, Requires<SunCycleControllerInfo>
	{
		[Desc("Red, green, blue multipliers at the middle of Dusk and Dawn.")]
		public readonly float3 TwilightTint = new(1.06f, 0.95f, 0.84f);

		[Desc("Overall brightness at the middle of Dusk and Dawn.")]
		public readonly float TwilightAmbient = 0.92f;

		[Desc("Red, green, blue multipliers at Night.")]
		public readonly float3 NightTint = new(0.84f, 0.9f, 1.12f);

		[Desc("Overall brightness at Night. Keep at or above 0.7: team colours and silhouettes must stay",
			"readable in the dark (design pillar 1, docs/VISION.md).")]
		public readonly float NightAmbient = 0.74f;

		public override object Create(ActorInitializer init) { return new SunCycleTint(init.Self, this); }
	}

	public class SunCycleTint : RenderPostProcessPassBase
	{
		readonly SunCycleTintInfo info;
		readonly SunCycleController controller;
		readonly World world;

		public SunCycleTint(Actor self, SunCycleTintInfo info)
			: base("tint", PostProcessPassType.AfterActors)
		{
			this.info = info;
			world = self.World;
			controller = self.Trait<SunCycleController>();
		}

		// Night lasts long enough that a pass running every frame for the whole match is worth it only
		// while the cycle is on; off, the pass is skipped entirely and the frame is untouched.
		protected override bool Enabled => controller.Enabled && world.WorldTick >= controller.Info.FirstDuskTick;

		protected override void PrepareRender(WorldRenderer wr, IShader shader)
		{
			var tint = Current(out var ambient);
			shader.SetVec("Tint", ambient * tint.X, ambient * tint.Y, ambient * tint.Z);
		}

		// Render-only: floats never feed back into the simulation. Dusk fades day -> twilight -> night across
		// its length and Dawn the reverse, so the light never jumps at a phase boundary.
		float3 Current(out float ambient)
		{
			var phase = controller.PhaseAt(world.WorldTick, out var remaining, out var length);
			var day = new float3(1f, 1f, 1f);
			switch (phase)
			{
				case SunPhase.Night:
					ambient = info.NightAmbient;
					return info.NightTint;

				case SunPhase.Dusk:
					return Fade(day, 1f, info.NightTint, info.NightAmbient, Progress(remaining, length), out ambient);

				case SunPhase.Dawn:
					return Fade(info.NightTint, info.NightAmbient, day, 1f, Progress(remaining, length), out ambient);

				default:
					ambient = 1f;
					return day;
			}
		}

		static float Progress(int remaining, int length) => length > 0 ? 1f - (float)remaining / length : 1f;

		float3 Fade(float3 from, float fromAmbient, float3 to, float toAmbient, float t, out float ambient)
		{
			// Two legs through the twilight colour, which sits at the middle of the phase.
			if (t < 0.5f)
			{
				var k = t * 2f;
				ambient = Lerp(fromAmbient, info.TwilightAmbient, k);
				return Lerp(from, info.TwilightTint, k);
			}
			else
			{
				var k = (t - 0.5f) * 2f;
				ambient = Lerp(info.TwilightAmbient, toAmbient, k);
				return Lerp(info.TwilightTint, to, k);
			}
		}

		static float Lerp(float a, float b, float t) => a + (b - a) * t;
		static float3 Lerp(float3 a, float3 b, float t) => new(Lerp(a.X, b.X, t), Lerp(a.Y, b.Y, t), Lerp(a.Z, b.Z, t));
	}
}
