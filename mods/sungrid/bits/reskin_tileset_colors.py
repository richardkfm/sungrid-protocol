#!/usr/bin/env python3
"""Recolour the tilesets' terrain-type `Color:` entries the way
reskin_terrain_palette.py recoloured the terrain palettes (issue #119).

A map's map.png preview and the in-game radar minimap are not drawn from the
terrain *palette* at all: Map.SavePreview / Map.GetTerrainColorPair take each
cell's colour from the tileset yaml's `Terrain: TerrainType@*: Color:` entries
(a tile without its own MinColor/MaxColor falls back to its terrain type's
colour - engine/OpenRA.Mods.Common/Terrain/DefaultTerrain.cs). So after the
Phase 6 palette reskin the world drew green while every preview thumbnail and
the radar still showed stock Red Alert's tan. This applies the same hue remap
(recolor_red_to_green, imported from the palette script so the two cannot
drift) to those entries, with the same per-tileset setting: full strength on
temperate and snow, the desert's bright-sand cutoff (--max-value 0.5) on
desert. Idempotent - a green entry is outside the warm band and is left alone.

Usage:
    python3 reskin_tileset_colors.py          # rewrites ../tilesets/*.yaml in place
Then regenerate the previews:
    ./utility.sh --refresh-map-previews <map> [<map> ...]
"""
import os
import re
import numpy as np

from reskin_terrain_palette import recolor_red_to_green

HERE = os.path.dirname(os.path.abspath(__file__))
TILESETS = os.path.join(HERE, "..", "tilesets")
# Same cutoffs as the palette pass (docs/ART_DIRECTION.md, Phase 6 terrain).
MAX_VALUE = {"desert.yaml": 0.5, "temperat.yaml": None, "snow.yaml": None}


def recolor_hex(hex_rgb, max_value):
    rgb = np.array([[int(hex_rgb[i:i + 2], 16) for i in (0, 2, 4)]], dtype=np.float64) / 255.0
    out = recolor_red_to_green(rgb, max_recolor_value=max_value)[0]
    return "".join(f"{int(round(c * 255)):02X}" for c in out)


def main():
    for name, max_value in MAX_VALUE.items():
        path = os.path.join(TILESETS, name)
        text = open(path).read()
        head, sep, rest = text.partition("\nTemplates:")
        changed = 0

        def repl(m):
            nonlocal changed
            new = recolor_hex(m.group(2), max_value)
            if new != m.group(2):
                changed += 1
            return m.group(1) + new

        head2 = re.sub(r"(\n\t\tColor: )([0-9A-Fa-f]{6})", repl, head)
        open(path, "w").write(head2 + sep + rest)
        print(f"{name}: {changed} terrain-type colours recoloured")


if __name__ == "__main__":
    main()
