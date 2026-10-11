#!/usr/bin/env python3
"""Place stock villages and towns on a map (docs/BACKLOG.md issue #131).

A map package (a directory or an .oramap) is read for its terrain, resources,
bounds, spawns and existing actors; two or three hamlets are then laid out on
open ground, away from the spawns, the ore and any village the map already
has, and written into map.yaml as Vil* actors owned by Neutral. Everything is
deterministic: every choice goes through crc32 of the map name and a few
integers, so re-running the script on a clean map gives the same village, and
running it on a map that already carries Vil* actors does nothing.

Each hamlet is a short lane: houses on both sides of a two-cell street with a
one-cell gap between neighbours (so the lane and the gaps stay walkable), a
wooden fence run along one house group, a utility pole or two, and on the
temperate and snow tilesets a small block of crop fields beside it. The kit
is the stock Red Alert civilian set - the Sungrid scenery pieces are left out
on purpose until they have been seen live (the owner's call).

Usage:
    place_villages.py [--dry-run] [--replace] [--render DIR] [--hamlets N] MAP [MAP ...]

--replace strips the Vil* actors a map already carries and places afresh;
--render writes a schematic PNG per map (terrain, resources, the new actors
highlighted) into DIR for review.

After placing, re-save each map with
    ./utility.sh --refresh-map-previews /abs/path/to/map
so map.yaml is normalised and map.png follows (the utility cds into engine/,
so paths must be absolute).
"""

import io
import os
import re
import struct
import sys
import zipfile
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
RULES_DIR = os.path.join(MOD, "rules")
TILESETS_DIR = os.path.join(MOD, "tilesets")

# ---------------------------------------------------------------- helpers


def h(*parts):
    """A stable integer hash of the parts (crc32, so it survives Python's
    per-process string hashing)."""
    return zlib.crc32("|".join(str(p) for p in parts).encode("utf-8")) & 0xFFFFFFFF


def pick(seq, *parts):
    return seq[h(*parts) % len(seq)]


# ---------------------------------------------------------------- rules


def load_footprints():
    """Return {actor_id_lower: [(dx, dy), ...]} of occupied cells for every
    actor that declares a Building footprint, following Inherits chains.
    Actors without a footprint occupy their own cell."""
    nodes = {}
    for name in sorted(os.listdir(RULES_DIR)):
        if not name.endswith(".yaml"):
            continue
        text = open(os.path.join(RULES_DIR, name), encoding="utf-8").read()
        for block in re.split(r"^(?=\S)", text, flags=re.M):
            m = re.match(r"^([^\s:]+):", block)
            if not m:
                continue
            key = m.group(1)
            inherits = re.findall(r"^\tInherits(?:@\w+)?: (\S+)", block, re.M)
            fp = re.search(r"^\t\tFootprint: (.*)$", block, re.M)
            dims = re.search(r"^\t\tDimensions: (\d+),(\d+)", block, re.M)
            occupies = re.search(r"^\t\tOccupiesSpace: false", block, re.M)
            nodes[key] = dict(
                inherits=inherits,
                footprint=fp.group(1).strip() if fp else None,
                dims=(int(dims.group(1)), int(dims.group(2))) if dims else None,
                ghost=bool(occupies))

    def resolve(key, seen=()):
        node = nodes.get(key)
        if node is None or key in seen:
            return None, None, False
        fp, dims, ghost = node["footprint"], node["dims"], node["ghost"]
        for parent in node["inherits"]:
            pfp, pdims, pghost = resolve(parent, seen + (key,))
            fp = fp or pfp
            dims = dims or pdims
            ghost = ghost or pghost
        return fp, dims, ghost

    out = {}
    for key in nodes:
        if key.startswith("^"):
            continue
        fp, dims, ghost = resolve(key)
        if ghost:
            out[key.lower()] = []
            continue
        cells = []
        if fp and dims:
            rows = fp.split()
            for y, row in enumerate(rows):
                for x, ch in enumerate(row):
                    if ch != "_":
                        cells.append((x, y))
        elif dims:
            cells = [(x, y) for y in range(dims[1]) for x in range(dims[0])]
        else:
            cells = [(0, 0)]
        out[key.lower()] = cells
    return out


# ---------------------------------------------------------------- tileset


def load_tileset(tileset_id):
    """Return {template_id: {tile_index: terrain_type}}."""
    path = os.path.join(TILESETS_DIR, tileset_id.lower() + ".yaml")
    text = open(path, encoding="utf-8").read()
    templates = {}
    for block in re.split(r"^(?=\tTemplate@)", text, flags=re.M):
        m = re.match(r"^\tTemplate@(\d+):", block)
        if not m:
            continue
        tid = int(re.search(r"^\t\tId: (\d+)", block, re.M).group(1))
        tiles = {int(i): t for i, t in re.findall(r"^\t\t\t(\d+): (\w+)$", block, re.M)}
        templates[tid] = tiles
    return templates


# ---------------------------------------------------------------- map package


class MapPackage:
    def __init__(self, path):
        self.path = path
        self.is_dir = os.path.isdir(path)
        self.files = {}
        if self.is_dir:
            for name in os.listdir(path):
                with open(os.path.join(path, name), "rb") as f:
                    self.files[name] = f.read()
        else:
            with zipfile.ZipFile(path) as z:
                for name in z.namelist():
                    self.files[name] = z.read(name)
        self.yaml = self.files["map.yaml"].decode("utf-8")
        self.name = os.path.basename(path.rstrip("/\\"))
        self.title = re.search(r"^Title: (.*)$", self.yaml, re.M).group(1)
        self.tileset = re.search(r"^Tileset: (\w+)", self.yaml, re.M).group(1)
        self.width, self.height = map(int, re.search(r"^MapSize: (\d+),(\d+)", self.yaml, re.M).groups())
        bx, by, bw, bh = map(int, re.search(r"^Bounds: (\d+),(\d+),(\d+),(\d+)", self.yaml, re.M).groups())
        self.bounds = (bx, by, bx + bw, by + bh)  # half-open
        self.actors = []  # (name, type, x, y)
        actors_block = re.search(r"^Actors:\n((?:\t.*\n?)*)", self.yaml, re.M)
        if actors_block:
            for m in re.finditer(r"^\t(\w+): (\S+)\n((?:\t\t.*\n?)*)", actors_block.group(1), re.M):
                loc = re.search(r"^\t\tLocation: (-?\d+),(-?\d+)", m.group(3), re.M)
                if loc:
                    self.actors.append((m.group(1), m.group(2).lower(), int(loc.group(1)), int(loc.group(2))))
        self._parse_bin()

    def _parse_bin(self):
        b = self.files["map.bin"]
        fmt, w, h = struct.unpack_from("<BHH", b, 0)
        assert fmt == 2 and w == self.width and h == self.height, (fmt, w, h)
        self.tiles = [[None] * h for _ in range(w)]
        self.resources = [[0] * h for _ in range(w)]
        off = 5
        for i in range(w):
            for j in range(h):
                t, idx = struct.unpack_from("<HB", b, off)
                self.tiles[i][j] = (t, idx)
                off += 3
        for i in range(w):
            for j in range(h):
                self.resources[i][j] = b[off]
                off += 2

    def write(self, out_path=None):
        out_path = out_path or self.path
        self.files["map.yaml"] = self.yaml.encode("utf-8")
        if self.is_dir:
            with open(os.path.join(out_path, "map.yaml"), "wb") as f:
                f.write(self.files["map.yaml"])
        else:
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
                for name, data in self.files.items():
                    z.writestr(name, data)
            with open(out_path, "wb") as f:
                f.write(buf.getvalue())


# ---------------------------------------------------------------- the world grid


class Grid:
    """Terrain, occupancy and keep-out masks for one map."""

    def __init__(self, pkg, footprints, templates):
        self.pkg = pkg
        w, h = pkg.width, pkg.height
        self.w, self.h = w, h
        self.terrain = [[None] * h for _ in range(w)]
        for i in range(w):
            for j in range(h):
                t, idx = pkg.tiles[i][j]
                self.terrain[i][j] = templates.get(t, {}).get(idx)
        self.occupied = set()
        self.spawns = []
        self.houses = []
        for name, kind, x, y in pkg.actors:
            if kind == "mpspawn":
                self.spawns.append((x, y))
                continue
            if re.fullmatch(r"v\d\d", kind):
                self.houses.append((x, y))
            for dx, dy in footprints.get(kind, [(0, 0)]):
                self.occupied.add((x + dx, y + dy))
        self.resource = {(i, j) for i in range(w) for j in range(h) if pkg.resources[i][j]}

    def inside(self, x, y, margin=0):
        bx0, by0, bx1, by1 = self.pkg.bounds
        return bx0 + margin <= x < bx1 - margin and by0 + margin <= y < by1 - margin

    def clear(self, x, y):
        return self.inside(x, y) and self.terrain[x][y] == "Clear"

    def free(self, x, y):
        return self.clear(x, y) and (x, y) not in self.occupied and (x, y) not in self.resource

    def box_free(self, x0, y0, x1, y1):
        return all(self.free(x, y) for x in range(x0, x1) for y in range(y0, y1))

    def clear_fraction(self, cx, cy, r):
        n = ok = 0
        for x in range(cx - r, cx + r + 1):
            for y in range(cy - r, cy + r + 1):
                n += 1
                if self.free(x, y):
                    ok += 1
        return ok / n


# ---------------------------------------------------------------- kits

# Houses by footprint size, per tileset family. The temperate and snow
# tilesets share the V01-V19 set (desert excluded); desert has V20-V36.
KITS = {
    "TEMPERAT": dict(
        big=["v01", "v02", "v03", "v04"], long=["v05", "v06", "v07"],
        small=["v08", "v09", "v10", "v11"], fields=["v14", "v15", "v16", "v17", "v18"],
        stacks=["v12", "v13"], fence="wood", poles=["utilpol1", "utilpol2"]),
    "DESERT": dict(
        big=["v20", "v21", "v24", "v25"], long=["v22", "v26", "v30", "v31", "v32", "v33"],
        small=["v23", "v27", "v28", "v29", "v34", "v35", "v36"], fields=[],
        stacks=[], fence="fenc", poles=["utilpol1", "utilpol2"]),
}
KITS["SNOW"] = KITS["TEMPERAT"]

SIZES = {"big": (2, 2), "long": (2, 1), "small": (1, 1)}

MIN_HOUSE_DIST = 14     # cells from any village the map already has

# Site tiers, strictest first: (spawn distance, hamlet spacing, open-ground
# radius, fraction of that ground that must be free Clear). A busy map (trees
# and ore everywhere, or a small one with four spawns) falls through to the
# looser tiers rather than getting no village at all.
SITE_TIERS = [
    (16, 36, 8, 0.82),
    (14, 30, 6, 0.72),
    (12, 24, 5, 0.62),
]


def site_ok(grid, cx, cy, spawn_dist, radius, clear):
    if not grid.inside(cx, cy, margin=radius + 2):
        return False
    if any((cx - x) ** 2 + (cy - y) ** 2 < spawn_dist ** 2 for x, y in grid.spawns):
        return False
    if any((cx - x) ** 2 + (cy - y) ** 2 < MIN_HOUSE_DIST ** 2 for x, y in grid.houses):
        return False
    return grid.clear_fraction(cx, cy, radius) >= clear


def find_sites(grid, want):
    """Candidate centres on a 3-cell lattice, visited in hash order so the
    choice is stable, keeping the ones far enough from each other. Tiers are
    tried in turn until enough sites are found; sites found by a stricter
    tier are kept."""
    bx0, by0, bx1, by1 = grid.pkg.bounds
    cands = [(x, y) for x in range(bx0, bx1, 3) for y in range(by0, by1, 3)]
    cands.sort(key=lambda c: h(grid.pkg.name, "site", c[0], c[1]))
    sites = []
    for spawn_dist, spacing, radius, clear in SITE_TIERS:
        for cx, cy in cands:
            if len(sites) >= want:
                return sites
            if not site_ok(grid, cx, cy, spawn_dist, radius, clear):
                continue
            if any((cx - x) ** 2 + (cy - y) ** 2 < spacing ** 2 for x, y in sites):
                continue
            sites.append((cx, cy))
    return sites


class Placer:
    def __init__(self, grid, kit, seed):
        self.grid = grid
        self.kit = kit
        self.seed = seed
        self.placed = []   # (type, x, y)
        self.taken = set()

    def can(self, x, y, w, h_, gap=1):
        """The footprint must be free Clear ground; the gap ring around it
        must be free of other placed actors (terrain may be anything there)."""
        if not self.grid.box_free(x, y, x + w, y + h_):
            return False
        for i in range(x - gap, x + w + gap):
            for j in range(y - gap, y + h_ + gap):
                if (i, j) in self.taken or (i, j) in self.grid.occupied:
                    return False
        return True

    def put(self, kind, x, y, w=1, h_=1):
        self.placed.append((kind, x, y))
        for i in range(x, x + w):
            for j in range(y, y + h_):
                self.taken.add((i, j))

    def town(self, cx, cy, index):
        """Two parallel lanes six cells apart, so a double row of houses
        stands back to back between them: 10 to 16 houses."""
        horizontal = h(self.seed, "axis", index) % 2 == 0
        total = 0
        for k, off in enumerate((-3, 3)):
            lx, ly = (cx, cy + off) if horizontal else (cx + off, cy)
            total += self.hamlet(lx, ly, (index, k), horizontal=horizontal, long=True,
                                 fence_side=-1 if off < 0 else 1)
        return total

    def hamlet(self, cx, cy, index, horizontal=None, long=False, fence_side=None):
        """A lane through (cx, cy): houses on both sides, fence, poles, fields."""
        kit, g = self.kit, self.grid
        if horizontal is None:
            horizontal = h(self.seed, "axis", index) % 2 == 0
        length = 7 + h(self.seed, "len", index) % 4            # 7..10 cells of lane
        want = 4 + h(self.seed, "houses", index) % 5           # 4..8 houses
        if long:
            length += 4
            want += 2
        count = 0
        # Slots along the lane, alternating sides, walking outward from the centre.
        slots = []
        for step in range(length + 1):
            for side in (-1, 1):
                slots.append((step - length // 2, side))
        slots.sort(key=lambda s: (abs(s[0]), s[1]))
        for n, (t, side) in enumerate(slots):
            if count >= want:
                break
            cls = pick(["big", "big", "long", "small", "small"], self.seed, "cls", index, n)
            kind = pick(kit[cls], self.seed, "kind", index, n)
            w, h_ = SIZES[cls]
            # The lane is two cells wide: rows cy-1..cy (horizontal) or
            # columns cx-1..cx (vertical). Houses sit just outside it.
            if horizontal:
                x = cx + t
                y = cy + 1 if side > 0 else cy - 1 - h_
            else:
                y = cy + t
                x = cx + 1 if side > 0 else cx - 1 - w
            if self.can(x, y, w, h_):
                self.put(kind, x, y, w, h_)
                count += 1
        if count == 0:
            return 0
        # Crop fields: a 3x2 (or 2x3) block past one end of the lane, 60% of hamlets.
        if kit["fields"] and h(self.seed, "fields", index) % 5 < 3:
            end = length // 2 + 4
            fx, fy = (cx + end, cy - 1) if horizontal else (cx - 1, cy + end)
            fw, fh = (3, 2) if horizontal else (2, 3)
            if self.can(fx, fy, fw, fh):
                for i in range(fw):
                    for j in range(fh):
                        self.put(pick(kit["fields"], self.seed, "field", index, i, j), fx + i, fy + j)
            elif kit["stacks"] and self.can(fx, fy, 1, 1):
                self.put(pick(kit["stacks"], self.seed, "stack", index), fx, fy)
        # A fence run beside the far end of one side, a few cells long.
        run = 4 + h(self.seed, "fence", index) % 4
        side = fence_side or (1 if h(self.seed, "fside", index) % 2 else -1)
        off = 4 if side > 0 else -4
        for k in range(run):
            if horizontal:
                x, y = cx - run // 2 + k, cy + off
            else:
                x, y = cx + off, cy - run // 2 + k
            if self.can(x, y, 1, 1, gap=0):
                self.put(kit["fence"], x, y)
        # A utility pole at each end of the lane, on opposite edges.
        for k, (t, edge) in enumerate(((-length // 2 - 2, 0), (length // 2 + 2, -1))):
            pole = pick(kit["poles"], self.seed, "pole", index, k)
            x, y = (cx + t, cy + edge) if horizontal else (cx + edge, cy + t)
            if self.can(x, y, 1, 1, gap=0):
                self.put(pole, x, y)
        return count


TERRAIN_COLOURS = {
    "Clear": (72, 108, 60), "Road": (120, 110, 80), "Rough": (90, 96, 70),
    "Water": (48, 84, 140), "River": (60, 100, 150), "Beach": (150, 140, 100),
    "Rock": (70, 70, 64), "Bridge": (110, 100, 90), "Tree": (40, 70, 36), None: (20, 20, 20),
}
RESOURCE_COLOURS = {1: (200, 170, 60), 2: (150, 110, 220), 3: (90, 170, 150)}


def render(grid, placer, sites, kit, path, scale=4):
    """A schematic of the map with the new actors highlighted, for review:
    terrain by type, resources, existing actors dark, spawns white, placed
    houses red, fields yellow, fence pink, poles light blue, sites ringed."""
    from PIL import Image, ImageDraw

    w, h_ = grid.w, grid.h
    img = Image.new("RGB", (w * scale, h_ * scale), (0, 0, 0))
    d = ImageDraw.Draw(img)
    for x in range(w):
        for y in range(h_):
            c = TERRAIN_COLOURS.get(grid.terrain[x][y], (120, 60, 120))
            r = grid.pkg.resources[x][y]
            if r in RESOURCE_COLOURS:
                c = RESOURCE_COLOURS[r]
            if (x, y) in grid.occupied:
                c = tuple(v // 3 for v in c)
            d.rectangle([x * scale, y * scale, x * scale + scale - 1, y * scale + scale - 1], fill=c)
    bx0, by0, bx1, by1 = grid.pkg.bounds
    d.rectangle([bx0 * scale, by0 * scale, bx1 * scale - 1, by1 * scale - 1], outline=(255, 255, 255))
    for x, y in grid.spawns:
        d.ellipse([x * scale - 6, y * scale - 6, x * scale + 6, y * scale + 6], outline=(255, 255, 255), width=2)
    for x, y in grid.houses:
        d.rectangle([x * scale, y * scale, x * scale + 2 * scale - 1, y * scale + 2 * scale - 1], outline=(255, 150, 60))
    for cx, cy in sites:
        d.ellipse([cx * scale - 40, cy * scale - 40, cx * scale + 40, cy * scale + 40], outline=(255, 255, 0))
    for kind, x, y in placer.placed:
        if kind in kit["fields"] + kit["stacks"]:
            c, (fw, fh) = (230, 220, 90), (1, 1)
        elif kind == kit["fence"]:
            c, (fw, fh) = (255, 120, 200), (1, 1)
        elif kind in kit["poles"]:
            c, (fw, fh) = (150, 210, 255), (1, 1)
        else:
            c = (240, 50, 40)
            fw, fh = next(SIZES[s] for s in SIZES if kind in kit[s])
        d.rectangle([x * scale, y * scale, (x + fw) * scale - 1, (y + fh) * scale - 1], fill=c)
    img.save(path)


def place(pkg, footprints, hamlets=None, dry_run=False, render_dir=None, replace=False):
    if any(name.startswith("Vil") for name, _, _, _ in pkg.actors):
        if not replace:
            print(f"{pkg.name}: already has villages, skipping")
            return []
        pkg.yaml = re.sub(r"^\tVil\d+: \S+\n(?:\t\t.*\n)*", "", pkg.yaml, flags=re.M)
        pkg.actors = [a for a in pkg.actors if not a[0].startswith("Vil")]
    templates = load_tileset(pkg.tileset)
    grid = Grid(pkg, footprints, templates)
    kit = KITS[pkg.tileset]
    bx0, by0, bx1, by1 = pkg.bounds
    area = (bx1 - bx0) * (by1 - by0)
    want = hamlets or (3 if area >= 110 * 110 else 2)
    sites = find_sites(grid, want)
    placer = Placer(grid, kit, pkg.name)
    report = []
    # The first site (found by the strictest tier that yielded anything, so the
    # most open ground on the map) becomes the town; the rest are hamlets.
    for i, (cx, cy) in enumerate(sites):
        n = placer.town(cx, cy, i) if i == 0 else placer.hamlet(cx, cy, i)
        report.append((cx, cy, n))
    if render_dir:
        render(grid, placer, sites, kit, os.path.join(render_dir, pkg.name.replace(".oramap", "") + ".png"))
    if not placer.placed:
        print(f"{pkg.name}: no site found")
        return report
    lines = []
    for n, (kind, x, y) in enumerate(placer.placed):
        lines.append(f"\tVil{n:03d}: {kind}\n\t\tOwner: Neutral\n\t\tLocation: {x},{y}\n")
    block = "".join(lines)
    m = re.search(r"^Actors:\n((?:\t.*\n?)*)", pkg.yaml, re.M)
    end = m.end()
    pkg.yaml = pkg.yaml[:end].rstrip("\n") + "\n" + block + pkg.yaml[end:]
    houses = sum(1 for k, _, _ in placer.placed if re.fullmatch(r"v\d\d", k) and k not in kit["fields"] + kit["stacks"])
    print(f"{pkg.name} ({pkg.tileset}, {len(grid.spawns)} spawns): {len(sites)} hamlets, "
          f"{houses} houses, {len(placer.placed)} actors at {[(x, y) for x, y, _ in report]}")
    if not dry_run:
        pkg.write()
    return report


def main(argv):
    dry = "--dry-run" in argv
    replace = "--replace" in argv
    hamlets = render_dir = None
    if "--hamlets" in argv:
        hamlets = int(argv[argv.index("--hamlets") + 1])
    if "--render" in argv:
        render_dir = argv[argv.index("--render") + 1]
    paths = [a for i, a in enumerate(argv)
             if not a.startswith("--") and (i == 0 or argv[i - 1] not in ("--hamlets", "--render"))]
    if not paths:
        print(__doc__)
        return 2
    footprints = load_footprints()
    for p in paths:
        place(MapPackage(p), footprints, hamlets=hamlets, dry_run=dry, render_dir=render_dir, replace=replace)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
