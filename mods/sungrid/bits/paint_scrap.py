#!/usr/bin/env python3
"""Paint Scrap fields onto a map (docs/BACKLOG.md issue #132).

Scrap is the Recycling Depot's resource (ResourceIndex 3, rules/world.yaml);
until now only the shellmap carried a painted field and every real match ran
the Depot and Hauler loop on wreck drops alone. This paints one field per two
players on a map, in the contested middle rather than beside a spawn, so the
Depot has something to work on and the Hauler has somewhere to be raided.

A field is a rounded blob of about 30 to 40 cells on free Clear ground, its
density highest at the centre (index 5 of the shellmap's 2..5 range, MaxDensity
6) and falling off outward, as the shellmap's hand-painted field does. Sites are
chosen in crc32 order, at least 16 cells from any spawn, clear of ore and gems,
inside the central 60% of the playable area where possible, and at least 30
cells apart. Only map.bin's resource layer changes; map.yaml is untouched.

Usage:
    paint_scrap.py [--dry-run] [--replace] [--fields N] MAP [MAP ...]

--replace clears the Scrap a map already carries inside its bounds first.

Re-save afterwards with ./utility.sh --refresh-map-previews /abs/path so the
preview shows the field.
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import place_villages as pv  # noqa: E402

SCRAP = 3
MIN_SPAWN_DIST = 16
MIN_FIELD_DIST = 30
RESOURCE_CLEARANCE = 4


def has_scrap(pkg):
    """Scrap inside the playable bounds; a few stock and generated maps carry
    stray resource bytes in the out-of-bounds border, which do not count."""
    bx0, by0, bx1, by1 = pkg.bounds
    return any(pkg.resources[i][j] == SCRAP for i in range(bx0, bx1) for j in range(by0, by1))


def site_ok(grid, cx, cy, central):
    pkg = grid.pkg
    bx0, by0, bx1, by1 = pkg.bounds
    if central:
        mx, my = (bx0 + bx1) / 2, (by0 + by1) / 2
        if abs(cx - mx) > 0.3 * (bx1 - bx0) or abs(cy - my) > 0.3 * (by1 - by0):
            return False
    if not grid.inside(cx, cy, margin=6):
        return False
    if any((cx - x) ** 2 + (cy - y) ** 2 < MIN_SPAWN_DIST ** 2 for x, y in grid.spawns):
        return False
    for x in range(cx - RESOURCE_CLEARANCE - 3, cx + RESOURCE_CLEARANCE + 4):
        for y in range(cy - RESOURCE_CLEARANCE - 3, cy + RESOURCE_CLEARANCE + 4):
            if (x, y) in grid.resource:
                return False
    return grid.clear_fraction(cx, cy, 4) >= 0.8


def spread_ok(grid, cx, cy, sites, want):
    """Keep the fields roughly fair on a symmetric map: every field at about
    the same distance from the map centre as the first, and the angles
    between them close to an even split of the circle."""
    if not sites:
        return True
    bx0, by0, bx1, by1 = grid.pkg.bounds
    mx, my = (bx0 + bx1) / 2, (by0 + by1) / 2
    d0 = math.dist(sites[0], (mx, my))
    d = math.dist((cx, cy), (mx, my))
    if d0 > 8 and abs(d - d0) > 0.3 * d0:
        return False
    a = math.atan2(cy - my, cx - mx)
    slack = math.radians(30)
    for sx, sy in sites:
        b = math.atan2(sy - my, sx - mx)
        gap = abs((a - b + math.pi) % (2 * math.pi) - math.pi)
        if gap < 2 * math.pi / want - slack:
            return False
    return True


def find_sites(grid, want):
    bx0, by0, bx1, by1 = grid.pkg.bounds
    cands = [(x, y) for x in range(bx0, bx1, 2) for y in range(by0, by1, 2)]
    cands.sort(key=lambda c: pv.h(grid.pkg.name, "scrap", c[0], c[1]))
    sites = []
    for central, spread in ((True, True), (False, True), (False, False)):
        for cx, cy in cands:
            if len(sites) >= want:
                return sites
            if not site_ok(grid, cx, cy, central):
                continue
            if any((cx - x) ** 2 + (cy - y) ** 2 < MIN_FIELD_DIST ** 2 for x, y in sites):
                continue
            if spread and not spread_ok(grid, cx, cy, sites, want):
                continue
            sites.append((cx, cy))
    return sites


def blob(grid, cx, cy, index):
    """Cells of one field with their density index: a jittered disc, densest
    at the centre, on free Clear cells only."""
    cells = {}
    r = 3.4
    for x in range(cx - 4, cx + 5):
        for y in range(cy - 4, cy + 5):
            d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            jitter = (pv.h(grid.pkg.name, "blob", index, x, y) % 100) / 100 * 0.9
            if d + jitter > r:
                continue
            if not grid.free(x, y) or grid.terrain[x][y] != "Clear":
                continue
            density = 5 if d < 1.2 else 4 if d < 2.2 else 3 if d < 3.0 else 2
            cells[(x, y)] = density
    return cells


def write_resources(pkg, cells):
    b = bytearray(pkg.files["map.bin"])
    off = 5 + pkg.width * pkg.height * 3
    for (x, y), density in cells.items():
        o = off + (x * pkg.height + y) * 2
        b[o] = SCRAP
        b[o + 1] = density
        pkg.resources[x][y] = SCRAP
    pkg.files["map.bin"] = bytes(b)


def clear_scrap(pkg):
    b = bytearray(pkg.files["map.bin"])
    off = 5 + pkg.width * pkg.height * 3
    bx0, by0, bx1, by1 = pkg.bounds
    for x in range(bx0, bx1):
        for y in range(by0, by1):
            if pkg.resources[x][y] == SCRAP:
                o = off + (x * pkg.height + y) * 2
                b[o] = b[o + 1] = 0
                pkg.resources[x][y] = 0
    pkg.files["map.bin"] = bytes(b)


def paint(pkg, footprints, fields=None, dry_run=False, replace=False):
    if has_scrap(pkg):
        if not replace:
            print(f"{pkg.name}: already has Scrap, skipping")
            return
        clear_scrap(pkg)
    grid = pv.Grid(pkg, footprints, pv.load_tileset(pkg.tileset))
    want = fields or max(1, len(grid.spawns) // 2)
    sites = find_sites(grid, want)
    painted = {}
    for i, (cx, cy) in enumerate(sites):
        painted.update(blob(grid, cx, cy, i))
    print(f"{pkg.name} ({pkg.tileset}, {len(grid.spawns)} spawns): {len(sites)} Scrap fields, "
          f"{len(painted)} cells at {sites}")
    if painted and not dry_run:
        write_resources(pkg, painted)
        pkg.write()


def main(argv):
    dry = "--dry-run" in argv
    replace = "--replace" in argv
    fields = int(argv[argv.index("--fields") + 1]) if "--fields" in argv else None
    paths = [a for i, a in enumerate(argv) if not a.startswith("--") and (i == 0 or argv[i - 1] != "--fields")]
    if not paths:
        print(__doc__)
        return 2
    footprints = pv.load_footprints()
    for p in paths:
        paint(pv.MapPackage(p), footprints, fields=fields, dry_run=dry, replace=replace)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
