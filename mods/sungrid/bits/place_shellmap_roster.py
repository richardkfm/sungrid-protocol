#!/usr/bin/env python3
"""Put the Sungrid roster on the main-menu battle (docs/BACKLOG.md issue #137).

The desert shellmap (mods/sungrid/maps/desert-shellmap) is the one map every
player sees, and until this pass it showed only part of the roster: no Arc
Pylon, no War Factory or Materials Refinery (both Sungrid art since issues
#126/#130), no anti-air at all (so the menu's drones could never be shot down
and piled up), and the drone buildings, Relays and Wind Turbines on the wrong
side of the faction line (issues #84, #101: the Drone Bay and the Wind Turbine
are the Assembly's, the Aerial Fabrication Bay, the Smart Grid Relay and the
Hydrogen Plant the Consortium's).

This script does two things, both deterministic:

1. RETYPE: actors already on the map whose type belongs to the other faction
   are swapped for their own side's same-footprint counterpart, keeping their
   cell (and the names desert-shellmap.lua refers to).
2. ADD: each entry in ADDITIONS is placed at the nearest valid cell to its
   anchor, searched in a fixed ring order. Valid means every footprint cell is
   free, Clear and resource-free inside the bounds, and the one-cell ring
   around the footprint is passable ground clear of every other actor (the
   rule from issue #131: nothing closes a path, nothing touches a neighbour).

Usage:
    place_shellmap_roster.py [--dry-run] [--replace] [--render PNG] [MAP]

MAP defaults to the desert shellmap. --replace strips the actors this script
added (the names in ADDITIONS) before placing again; without it a map that
already carries them is left alone. --render writes a schematic: terrain,
resources, existing actors dimmed, the additions and retypes highlighted, the
camera's oval path and the area a 1920x1080 menu sees around it.

Afterwards re-save the map with
    ./utility.sh --refresh-map-previews /abs/path/to/desert-shellmap
(absolute: the utility cds into engine/), so map.yaml is normalised and
map.png follows.
"""

import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import place_villages as pv  # noqa: E402

DEFAULT_MAP = os.path.join(pv.MOD, "maps", "desert-shellmap")

# (owner, old type, new type, {old name: new name}) - same footprint each way.
RETYPES = [
    ("Allies", "sgdrn", "sgdra", {}),
    ("Allies", "sgwnd", "sgrel", {}),
    ("Allies", "sgdro", "sgdrs", {"AlliedRecon1": "AlliedStrike1"}),
    ("Soviets", "sgdra", "sgdrn", {}),
    ("Soviets", "sgrel", "sgwnd", {}),
    ("Soviets", "sghyd", "apwr", {"SovietHydrogenPlant": "SovietSolarArray"}),
    ("Soviets", "sgdrs", "sgdro", {"SovietStrike1": "SovietRecon1", "SovietStrike2": "SovietRecon2"}),
]

# (name, type, owner, anchor x, anchor y). Names the Lua uses are spelled out;
# the rest are numbered. Anchors are where the piece reads best on the menu:
# the Assembly's new defences and banks face the valley the camera circles,
# the Consortium's anti-air covers its Battery Banks (the drone raids' target).
ADDITIONS = [
    # The Consortium (Allies), south-east.
    ("AlliedWarFactory", "weap", "Allies", 80, 63),
    ("AlliedAerialFab", "sgdra", "Allies", 57, 73),
    ("AlliedRefinery", "proc", "Allies", 102, 73),
    ("AlliedRelay2", "sgrel", "Allies", 88, 79),
    ("AlliedRelay3", "sgrel", "Allies", 60, 82),
    ("AlliedSAM1", "sam", "Allies", 66, 68),
    ("AlliedSAM2", "sam", "Allies", 81, 94),
    ("AlliedSAM3", "sam", "Allies", 79, 79),
    ("AlliedSAM4", "sam", "Allies", 54, 69),
    # The Assembly (Soviets), north-east plateau and north-west ridge.
    ("SovietRefinery", "proc", "Soviets", 86, 36),
    ("SovietPylon1", "tsla", "Soviets", 98, 44),
    ("SovietPylon2", "tsla", "Soviets", 101, 52),
    ("SovietPylon3", "tsla", "Soviets", 52, 34),
    ("SovietPylon4", "tsla", "Soviets", 88, 40),
    ("SovietFlak1", "agun", "Soviets", 102, 38),
    ("SovietFlak2", "agun", "Soviets", 44, 33),
    ("SovietFlak3", "agun", "Soviets", 108, 56),
    ("SovietBank1", "silo", "Soviets", 99, 40),
    ("SovietBank2", "silo", "Soviets", 101, 40),
    ("SovietBank3", "silo", "Soviets", 99, 42),
    ("SovietBank4", "silo", "Soviets", 55, 30),
    ("SovietBank5", "silo", "Soviets", 57, 30),
    ("SovietTurbine1", "sgwnd", "Soviets", 104, 36),
    ("SovietTurbine2", "sgwnd", "Soviets", 106, 37),
    ("SovietTurbine3", "sgwnd", "Soviets", 102, 44),
    ("SovietTurbine4", "sgwnd", "Soviets", 100, 46),
    ("SovietTurbine5", "sgwnd", "Soviets", 58, 34),
    ("SovietTurbine6", "sgwnd", "Soviets", 60, 32),
]

PASSABLE = {"Clear", "Road", "Rough", "Beach", "Bridge"}
SEARCH_RADIUS = 6


def owners_of(yaml):
    return {m.group(1): re.search(r"^\t\tOwner: (\w+)", m.group(3), re.M).group(1)
            for m in re.finditer(r"^\t(\w+): (\S+)\n((?:\t\t.*\n?)*)", yaml, re.M)}


def retype(pkg):
    owners = owners_of(pkg.yaml)
    done = []
    for owner, old, new, renames in RETYPES:
        for name, kind, x, y in list(pkg.actors):
            if kind != old or owners.get(name) != owner:
                continue
            new_name = renames.get(name, name)
            pkg.yaml = re.sub(rf"^\t{name}: {old}$", f"\t{new_name}: {new}", pkg.yaml, count=1, flags=re.M)
            done.append((new_name, old, new, x, y))
    return done


def ring_order(radius):
    """Offsets by distance, then angle - a fixed search order, no hashing."""
    cells = [(dx, dy) for dx in range(-radius, radius + 1) for dy in range(-radius, radius + 1)]
    return sorted(cells, key=lambda c: (c[0] * c[0] + c[1] * c[1], math.atan2(c[1], c[0])))


class Site:
    def __init__(self, grid, footprints):
        self.grid = grid
        self.fp = footprints

    def cells(self, kind, x, y):
        return [(x + dx, y + dy) for dx, dy in self.fp.get(kind, [(0, 0)])]

    def ok(self, kind, x, y):
        g = self.grid
        cells = self.cells(kind, x, y)
        for cx, cy in cells:
            if not g.inside(cx, cy, margin=1) or not g.free(cx, cy):
                return False
        footprint = set(cells)
        for cx, cy in cells:
            for rx in (cx - 1, cx, cx + 1):
                for ry in (cy - 1, cy, cy + 1):
                    if (rx, ry) in footprint:
                        continue
                    if (rx, ry) in g.occupied or g.terrain[rx][ry] not in PASSABLE:
                        return False
        return True

    def place(self, kind, ax, ay):
        for dx, dy in ring_order(SEARCH_RADIUS):
            if self.ok(kind, ax + dx, ay + dy):
                x, y = ax + dx, ay + dy
                self.grid.occupied.update(self.cells(kind, x, y))
                return x, y
        return None


def camera_oval(pkg):
    """CameraOvalMover's path: the viewport centre (the map bounds' centre on a
    shellmap) plus OvalRadius 19200 x 20480 world units = 18.75 x 20 cells."""
    bx0, by0, bx1, by1 = pkg.bounds
    return (bx0 + bx1) / 2, (by0 + by1) / 2, 19200 / 1024, 20480 / 1024


def render(grid, placed, retyped, path, scale=6):
    from PIL import Image, ImageDraw

    pkg = grid.pkg
    owners = owners_of(pkg.yaml)
    img = Image.new("RGB", (grid.w * scale, grid.h * scale), (0, 0, 0))
    d = ImageDraw.Draw(img)
    for x in range(grid.w):
        for y in range(grid.h):
            c = pv.TERRAIN_COLOURS.get(grid.terrain[x][y], (120, 60, 120))
            r = pkg.resources[x][y]
            if r in pv.RESOURCE_COLOURS:
                c = pv.RESOURCE_COLOURS[r]
            d.rectangle([x * scale, y * scale, x * scale + scale - 1, y * scale + scale - 1], fill=c)
    side = {"Allies": (90, 150, 255), "Soviets": (255, 80, 60)}
    new_names = {n for n, _, _, _, _ in placed} | {n for n, _, _, _, _ in retyped}
    for name, kind, x, y in pkg.actors:
        if kind == "waypoint" or name in new_names:
            continue
        c = side.get(owners.get(name), (170, 170, 170))
        c = tuple(v // 2 for v in c)
        for dx, dy in grid_fp(grid, kind):
            d.rectangle([(x + dx) * scale, (y + dy) * scale, (x + dx + 1) * scale - 1, (y + dy + 1) * scale - 1], fill=c)
    for name, old, kind, x, y in retyped:
        c = side[owners[name]]
        for dx, dy in grid_fp(grid, kind):
            d.rectangle([(x + dx) * scale, (y + dy) * scale, (x + dx + 1) * scale - 1, (y + dy + 1) * scale - 1],
                        outline=(255, 255, 255), fill=tuple(v * 3 // 4 for v in c))
        d.text((x * scale + 2, y * scale - 10), f"{old}>{kind}", fill=(255, 255, 255))
    for name, kind, owner, x, y in placed:
        c = side[owner]
        for dx, dy in grid_fp(grid, kind):
            d.rectangle([(x + dx) * scale, (y + dy) * scale, (x + dx + 1) * scale - 1, (y + dy + 1) * scale - 1], fill=c)
        d.text((x * scale + 2, y * scale - 10), kind, fill=(255, 255, 160))
    cx, cy, rx, ry = camera_oval(pkg)
    d.ellipse([(cx - rx) * scale, (cy - ry) * scale, (cx + rx) * scale, (cy + ry) * scale], outline=(255, 255, 0), width=2)
    # A 1920x1080 window shows 80 x 45 cells at 24px per cell; outline what it covers over a whole orbit.
    hw, hh = 40, 22.5
    box = [(cx - rx - hw) * scale, (cy - ry - hh) * scale, (cx + rx + hw) * scale, (cy + ry + hh) * scale]
    d.rectangle(box, outline=(255, 255, 0))
    legend = ["issue #137: Sungrid roster on the main-menu battle",
              "bright = added (yellow label), white-edged = retyped to its own faction (old>new)",
              "blue = Consortium, red = Assembly, dimmed = unchanged actors",
              "yellow oval = camera centre path, yellow box = what a 1920x1080 menu sees over one orbit",
              "teal = Scrap, gold = ore, purple = gems"]
    for i, line in enumerate(legend):
        d.text((8, (grid.h - 2) * scale - 12 * (len(legend) - i)), line, fill=(255, 255, 255))
    img.save(path)


def grid_fp(grid, kind):
    return grid.footprints.get(kind, [(0, 0)])


def main(argv):
    dry = "--dry-run" in argv
    replace = "--replace" in argv
    render_path = None
    if "--render" in argv:
        render_path = argv[argv.index("--render") + 1]
    paths = [a for i, a in enumerate(argv) if not a.startswith("--") and (i == 0 or argv[i - 1] != "--render")]
    path = paths[0] if paths else DEFAULT_MAP

    pkg = pv.MapPackage(path)
    names = {n for n, _, _, _, _ in ADDITIONS}
    present = [a for a in pkg.actors if a[0] in names]
    if present and not replace:
        print(f"{pkg.name}: already carries the roster additions, skipping (--replace to redo)")
        return 0
    if present:
        for name in names:
            pkg.yaml = re.sub(rf"^\t{name}: \S+\n(?:\t\t.*\n)*", "", pkg.yaml, flags=re.M)

    retyped = retype(pkg)
    pkg = reload(pkg)
    footprints = pv.load_footprints()
    grid = pv.Grid(pkg, footprints, pv.load_tileset(pkg.tileset))
    grid.footprints = footprints
    site = Site(grid, footprints)

    placed = []
    for name, kind, owner, ax, ay in ADDITIONS:
        spot = site.place(kind, ax, ay)
        if spot is None:
            print(f"  {name} ({kind}): no valid cell within {SEARCH_RADIUS} of {ax},{ay}")
            return 1
        placed.append((name, kind, owner, spot[0], spot[1]))

    block = "".join(f"\t{n}: {k}\n\t\tLocation: {x},{y}\n\t\tOwner: {o}\n" for n, k, o, x, y in placed)
    m = re.search(r"^Actors:\n((?:\t.*\n?)*)", pkg.yaml, re.M)
    pkg.yaml = pkg.yaml[:m.end()].rstrip("\n") + "\n" + block + pkg.yaml[m.end():]

    for n, old, new, x, y in retyped:
        print(f"  retype {n} at {x},{y}: {old} -> {new}")
    for n, k, o, x, y in placed:
        print(f"  add {n} ({k}, {o}) at {x},{y}")
    print(f"{pkg.name}: {len(retyped)} retyped, {len(placed)} added")

    if render_path:
        pkg = reload(pkg)
        grid.pkg = pkg
        render(grid, placed, retyped, render_path)
    if not dry:
        pkg.write()
    return 0


def reload(pkg):
    """Re-parse the actor list from the edited map.yaml text."""
    fresh = pv.MapPackage.__new__(pv.MapPackage)
    fresh.__dict__.update(pkg.__dict__)
    fresh.actors = []
    block = re.search(r"^Actors:\n((?:\t.*\n?)*)", fresh.yaml, re.M)
    for m in re.finditer(r"^\t(\w+): (\S+)\n((?:\t\t.*\n?)*)", block.group(1), re.M):
        loc = re.search(r"^\t\tLocation: (-?\d+),(-?\d+)", m.group(3), re.M)
        if loc:
            fresh.actors.append((m.group(1), m.group(2).lower(), int(loc.group(1)), int(loc.group(2))))
    return fresh


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
