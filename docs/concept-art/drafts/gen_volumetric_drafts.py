# DRAFT, non-canonical (see docs/ART_DIRECTION.md 'Concept drafts'). Renders review sheets only; writes nothing into mods/sungrid/bits.
"""Draft renders: buildings as true 3D solids at RA's 45-degree yaw, through the
shipped generator's own Mesh renderer + indexed pipeline. Nothing here writes
into the repo."""
import sys, math
HERE = __import__('os').path.dirname(__import__('os').path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, __import__('os').path.join(HERE, '..', '..', '..', 'mods', 'sungrid', 'bits'))
import gen_concept_art as G
from gen_concept_art import (Mesh, lit, dim, mix, render, render_shadow_mask, indexed_strip,
                             CONCRETE, SUN_GOLD, PANEL_BLUEBLACK, LEGACY_GRAY, LEGACY_GRAY_DARK,
                             GREEN_PRIMARY, GREEN_ACCENT, RUST, GRASS, DIRT, SHADOW_IDX, PLAYER_PAL)
from PIL import Image, ImageDraw
from shp import read_shp, load_pal, frame_rgba

YAW = 45.0
PALE_STEEL = (0xB2, 0xB6, 0xBC)              # concept-render tank/hangar white, cool so it never lands on the gold ramp
STEEL = mix(LEGACY_GRAY, PANEL_BLUEBLACK, 0.25)
SLAB = lit(CONCRETE, 0.18)
PAD_TOP = lit(CONCRETE, 0.42)

def slab(m, hx, hy, z=2.2, col=SLAB, band=True):
    """Concrete plinth (diamond on screen) with the team-colour conduit band
    running along its two near edges -- the same 'grid connection' tell the
    flat sprites carried, now wrapped round a solid."""
    m.box(-hx, -hy, 0, hx, hy, z, dim(col, 0.15), top=col, shadow=False)
    if band:
        # Band sits on the slab top, inset from the edge, along both near edges.
        m.box(-hx + 1.0, -hy + 1.0, z, hx - 1.0, -hy + 2.6, z + 0.9, SUN_GOLD,
              top=lit(SUN_GOLD, 0.25), order=1, shadow=False)
        m.box(-hx + 1.0, -hy + 1.0, z, -hx + 2.6, hy - 1.0, z + 0.9, SUN_GOLD,
              top=lit(SUN_GOLD, 0.25), order=1, shadow=False)

def dome(m, cx, cy, z, r, col, steps=4):
    """Stacked shrinking prisms standing in for a tank crown."""
    for i in range(steps):
        t = i / steps
        rr = r * math.cos(t * math.pi / 2 * 0.92)
        h = r * 0.55 / steps
        m.prism(cx, cy, z + i * h, z + (i + 1) * h, rr, lit(col, 0.06 * i),
                sides=12, top=lit(col, 0.12 + 0.08 * i))

# ---------------------------------------------------------------- Hydrogen Plant
def sghyd_mesh(damaged=False):
    m = Mesh()
    slab(m, 27, 27)
    tank = PALE_STEEL if not damaged else mix(PALE_STEEL, G.DAMAGE_SCORCH, 0.25)
    pipe = SUN_GOLD if not damaged else RUST
    # Tanks on the plot's screen-horizontal diagonal so they stand side by side
    # at equal depth (building (+x,-y) is screen-right at 45 degrees yaw).
    for k, (cx, cy) in enumerate(((-11, 11), (11, -11))):
        r = 9
        m.prism(cx, cy, 2.2, 4.6, r + 1.4, dim(CONCRETE, 0.1), sides=12, top=lit(CONCRETE, 0.1))
        m.prism(cx, cy, 4.6, 24.0, r, tank, sides=12, top=lit(tank, 0.1))
        m.prism(cx, cy, 10.0, 12.6, r + 0.4, PANEL_BLUEBLACK, sides=12, top=PANEL_BLUEBLACK)  # ID band (no order override: a prism's top cap is a full disc and would paint over the crown)
        m.prism(cx, cy, 18.8, 19.9, r + 0.4, pipe, sides=12, top=lit(pipe, 0.2))               # hoop
        if not (damaged and k == 1):
            dome(m, cx, cy, 24.0, r, tank, steps=5)
        else:
            m.prism(cx, cy, 24.0, 25.2, r * 0.8, dim(tank, 0.45), sides=12, top=G.DAMAGE_SCORCH)
    # Relief stack on the far tank
    m.strut((-15, 15, 22), (-15, 15, 33), 0.9, STEEL, cap=lit(STEEL, 0.3))
    # Electrolyser skid at the near corner, on a low deck, with three stack modules
    m.box(-9, -9, 2.2, 9, 9, 3.4, dim(CONCRETE, 0.05), top=lit(CONCRETE, 0.12), shadow=False)
    m.box(-7, -7, 3.4, 7, 7, 10.5, STEEL, top=lit(STEEL, 0.2))
    for i in range(3):
        m.box(-5.5 + i * 4, -5, 10.5, -3 + i * 4, 5, 13.5, PANEL_BLUEBLACK, top=lit(PANEL_BLUEBLACK, 0.3))
    m.box(-6.8, -7.4, 5.5, 6.8, -6.9, 7.5, pipe, top=pipe, order=1, shadow=False)  # status band
    # Transfer manifold: both tanks feed the skid through an elevated gold line
    m.strut((-11, 11, 16), (0, 0, 16), 0.9, pipe)
    m.strut((11, -11, 16), (0, 0, 16), 0.9, pipe)
    m.strut((0, 0, 13.5), (0, 0, 16.5), 0.9, pipe, cap=lit(pipe, 0.3))
    # PV canopy on the back corner: the solarpunk tell on an industrial plant
    m.strut((12, 12, 2.2), (12, 12, 8), 0.6, PALE_STEEL)
    m.strut((22, 22, 2.2), (22, 22, 8), 0.6, PALE_STEEL)
    m.quad((8, 16, 8), (18, 26, 8), (26, 18, 10.5), (16, 8, 10.5), lit(PANEL_BLUEBLACK, 0.3), order=2)
    return m

# ---------------------------------------------------------------- Drone Bay
def drone(m, cx, cy, z, col=GREEN_PRIMARY, r=7.5):
    m.box(cx - 3.0, cy - 3.0, z + 1.5, cx + 3.0, cy + 3.0, z + 4.2, col, top=lit(col, 0.3))
    m.box(cx - 1.4, cy - 4.2, z + 2.2, cx + 1.4, cy - 3.0, z + 3.6, PANEL_BLUEBLACK, top=PANEL_BLUEBLACK, order=1, shadow=False)  # sensor nose
    for sx in (-1, 1):
        for sy in (-1, 1):
            m.strut((cx + sx * 2.5, cy + sy * 2.5, z + 3.0), (cx + sx * r, cy + sy * r, z + 3.2), 0.6, LEGACY_GRAY_DARK)
            m.prism(cx + sx * r, cy + sy * r, z + 3.2, z + 3.8, 3.4, dim(PALE_STEEL, 0.25),
                    sides=10, top=lit(PALE_STEEL, 0.15), order=2)
            m.prism(cx + sx * r, cy + sy * r, z + 3.8, z + 4.4, 1.2, LEGACY_GRAY_DARK, sides=6, top=LEGACY_GRAY_DARK, order=3)
    m.box(cx - 1.0, cy - 1.0, z + 4.2, cx + 1.0, cy + 1.0, z + 5.2, SUN_GOLD, top=lit(SUN_GOLD, 0.3), order=3, shadow=False)
    m.box(cx - 0.8, cy - 0.8, z + 3.4, cx + 0.8, cy + 0.8, z + 4.2, SUN_GOLD, top=lit(SUN_GOLD, 0.3), order=2)

def sgdrn_mesh(damaged=False):
    m = Mesh()
    slab(m, 20, 20)
    # Octagonal landing pad with a team-colour ring (the concept render's pad)
    m.prism(1, -3, 2.2, 4.0, 15.5, dim(CONCRETE, 0.05), sides=8, top=PAD_TOP, phase=math.pi / 8)
    m.prism(1, -3, 4.0, 4.7, 15.5, SUN_GOLD, sides=8, top=lit(SUN_GOLD, 0.25), phase=math.pi / 8, order=1)
    m.prism(1, -3, 4.0, 4.8, 12.5, PAD_TOP, sides=8, top=lit(PAD_TOP, 0.05), phase=math.pi / 8, order=2)
    # Perimeter lamps
    for i in range(8):
        a = i * math.pi / 4 + math.pi / 8
        m.box(1 + 15.5 * math.cos(a) - 0.7, -3 + 15.5 * math.sin(a) - 0.7, 4.7,
              1 + 15.5 * math.cos(a) + 0.7, -3 + 15.5 * math.sin(a) + 0.7, 6.0,
              LEGACY_GRAY_DARK, top=(GREEN_ACCENT if not damaged else RUST), order=3, shadow=False)
    # Control cabin + charging mast at the back corner
    m.box(-19, 8, 2.2, -6, 19, 11, STEEL, top=lit(STEEL, 0.2))
    m.box(-18, 9, 11, -7, 18, 11.8, PANEL_BLUEBLACK, top=lit(PANEL_BLUEBLACK, 0.35), shadow=False)  # rooftop PV
    m.box(-17.5, 7.5, 5, -7.5, 8.2, 8.5, PANEL_BLUEBLACK, top=PANEL_BLUEBLACK, order=1, shadow=False)  # window strip
    m.strut((8, 16, 2.2), (8, 16, 22 if not damaged else 12), 1.0, STEEL, cap=lit(STEEL, 0.3))
    if not damaged:
        m.strut((8, 16, 21), (2, 4, 21), 0.7, STEEL)           # boom over the pad
        m.box(0.5, 2.5, 19.5, 3.5, 5.5, 21, SUN_GOLD, top=lit(SUN_GOLD, 0.3), order=2)  # work lamp
    # Parked drone
    if not damaged:
        drone(m, 1, -3, 4.8, r=7.5)
    else:
        m.box(-3, -6, 4.8, 4, 0, 6.5, dim(LEGACY_GRAY, 0.4), top=G.DAMAGE_SCORCH)
    return m

# ---------------------------------------------------------------- Construction Yard
def fact_mesh(damaged=False):
    m = Mesh()
    slab(m, 25, 25, z=2.0)
    hall = PALE_STEEL
    # Fabrication hall: back half of the plot
    m.box(-24, 0, 2, 24, 24, 17, hall, top=lit(hall, 0.1))
    # Shallow barrel vault along the hall (the stock yard's arched hall, in a
    # modern space-frame skin), carrying the PV field on its sunward flank.
    n = 6
    for i in range(n):
        a0, a1 = math.pi * i / n, math.pi * (i + 1) / n
        x0, x1 = -24 * math.cos(a0), -24 * math.cos(a1)
        z0, z1 = 17 + 8 * math.sin(a0), 17 + 8 * math.sin(a1)
        m.quad((x0, 0, z0), (x1, 0, z1), (x1, 24, z1), (x0, 24, z0), lit(hall, 0.05), order=1)
        if 1 <= i <= 3:
            m.quad((x0 + 1, 3, z0 + 0.4), (x1 - 1, 3, z1 + 0.4), (x1 - 1, 21, z1 + 0.4), (x0 + 1, 21, z0 + 0.4), PANEL_BLUEBLACK, order=2)
    m.poly([(-24 * math.cos(math.pi * i / n), 0, 17 + 8 * math.sin(math.pi * i / n)) for i in range(n + 1)], hall, order=1)  # front gable
    # Big doorway in the front face, framed by the team-colour band
    m.box(-9, -0.6, 2, 9, 0.6, 16, dim(PANEL_BLUEBLACK, 0.3), top=dim(PANEL_BLUEBLACK, 0.3), order=1, shadow=False)
    m.box(-11, -1.2, 2, -9, 0.4, 18, SUN_GOLD, top=lit(SUN_GOLD, 0.2), order=2, shadow=False)
    m.box(9, -1.2, 2, 11, 0.4, 18, SUN_GOLD, top=lit(SUN_GOLD, 0.2), order=2, shadow=False)
    m.box(-11, -1.2, 16, 11, 0.4, 18, SUN_GOLD, top=lit(SUN_GOLD, 0.2), order=2, shadow=False)
    # Window strip on the lit side wall
    m.box(-24.6, 6, 9, -23.8, 20, 12, PANEL_BLUEBLACK, top=PANEL_BLUEBLACK, order=1, shadow=False)
    # Assembly yard in front: gantry crane on two portal frames
    for y in (-6, -18):
        m.strut((-20, y, 2), (-20, y, 17), 1.2, STEEL, cap=lit(STEEL, 0.3))
        m.strut((20, y, 2), (20, y, 17), 1.2, STEEL, cap=lit(STEEL, 0.3))
        m.strut((-20, y, 16.5), (20, y, 16.5), 1.2, STEEL if not damaged else dim(STEEL, 0.3))
    m.strut((-20, -6, 17), (-20, -18, 17), 0.8, STEEL)
    m.strut((20, -6, 17), (20, -18, 17), 0.8, STEEL)
    m.box(2, -14, 16.2, 9, -10, 19.5, SUN_GOLD, top=lit(SUN_GOLD, 0.3), order=2)  # trolley
    # Part-built chassis on the yard floor
    m.box(-6, -15, 2, 6, -8, 6, dim(GREEN_PRIMARY, 0.1), top=lit(GREEN_PRIMARY, 0.2))
    # Reclaimed-green planter along the left near edge
    m.box(-24, -24, 2, -14, -20, 3.2, dim(GRASS, 0.2), top=GREEN_ACCENT, shadow=False)
    m.box(-22, -23, 3.2, -16, -21, 5.0, GREEN_PRIMARY, top=GREEN_ACCENT, shadow=False)
    # Comms mast on the back corner
    m.strut((21, 21, 20), (21, 21, 32 if not damaged else 24), 0.8, STEEL, cap=SUN_GOLD)
    return m

# ---------------------------------------------------------------- Solar Array (roster test)
def sgpwr_mesh(damaged=False):
    m = Mesh()
    slab(m, 20, 20)
    frame = lit(LEGACY_GRAY, 0.45)
    for row, y in enumerate((-13, 1)):
        for col, x in enumerate((-15, 1)):
            x0, x1, base = x, x + 13, 2.2
            hit = damaged and row == 1 and col == 1
            face = lit(PANEL_BLUEBLACK, 0.1) if not hit else dim(PANEL_BLUEBLACK, 0.5)
            lo, hi = base + 3, base + 9.5
            m.strut((x0 + 3, y + 5, base), (x0 + 3, y + 5, lo + 2.5), 0.7, STEEL)
            m.strut((x1 - 3, y + 5, base), (x1 - 3, y + 5, lo + 2.5), 0.7, STEEL)
            m.quad((x0, y, lo), (x1, y, lo), (x1, y + 10, hi), (x0, y + 10, hi), face, order=2)
            # cell mullions across the tilt
            for k in range(1, 4):
                yy, zz = y + 10 * k / 4, lo + (hi - lo) * k / 4
                m.quad((x0, yy - 0.25, zz - 0.15), (x1, yy - 0.25, zz - 0.15), (x1, yy + 0.25, zz + 0.15), (x0, yy + 0.25, zz + 0.15), dim(PANEL_BLUEBLACK, 0.55), order=3)
            m.quad((x0 + 6.3, y, lo), (x0 + 6.7, y, lo), (x0 + 6.7, y + 10, hi), (x0 + 6.3, y + 10, hi), dim(PANEL_BLUEBLACK, 0.55), order=3)
            # lit aluminium frame on the top and left edges
            m.quad((x0, y + 9.4, hi - 0.4), (x1, y + 9.4, hi - 0.4), (x1, y + 10, hi), (x0, y + 10, hi), frame, order=4)
            m.quad((x0, y, lo), (x0 + 0.6, y, lo), (x0 + 0.6, y + 10, hi), (x0, y + 10, hi), frame, order=4)
            if hit:
                m.quad((x0 + 2, y + 2, lo + 1.3), (x0 + 9, y + 2, lo + 1.3), (x0 + 6, y + 8, lo + 5.2), (x0 + 4, y + 8, lo + 5.2), G.DAMAGE_SCORCH, order=5)
    # Inverter cabinet at the back corner, with the live status band
    m.box(11, 11, 2.2, 19, 19, 9, STEEL, top=lit(STEEL, 0.2))
    m.box(11.5, 10.6, 5, 18.5, 11, 6.2, SUN_GOLD if not damaged else RUST, top=SUN_GOLD, order=1, shadow=False)
    return m

# ---------------------------------------------------------------- pipeline
def build(mesh_fn, w, h, oy, damaged=False, outline=False):
    ox = w // 2
    def body(sd, w, h):
        mesh_fn(damaged).draw(sd, ox, oy, YAW)
    def shadow(sd, w, h):
        mesh_fn(damaged).draw_shadow(sd, ox, oy, YAW)
    b = render(body, w, h)
    s = render_shadow_mask(shadow, w, h)
    return indexed_strip([b], [s], w, h)

def preview(strip, w, h, bg):
    """Indexed strip -> RGBA on a terrain colour, shadow as a dark stencil."""
    p = strip.load()
    img = Image.new('RGBA', (w, h), bg + (255,))
    d = img.load()
    for y in range(h):
        for x in range(w):
            v = p[x, y]
            if v == 0: continue
            d[x, y] = (dim(bg, 0.45) + (255,)) if v == SHADOW_IDX else PLAYER_PAL[v] + (255,)
    return img

def current(name, w, h, k=0):
    p = Image.open(HERE + f'/../../../mods/sungrid/bits/{name}.png')
    return p.crop((k * w, 0, (k + 1) * w, h))

if __name__ == '__main__':
    SC = 3
    GREEN, TAN = (0x3B, 0x63, 0x38), (0x9A, 0x86, 0x55)
    rows = []
    B = HERE + '/../../../mods/sungrid/bits'
    fw, fh, ff = read_shp(f'{B}/fact.shp')
    pal = load_pal(f'{B}/temperat.pal')
    def stock_strip(k):
        img = frame_rgba(fw, fh, ff[k], pal)
        return G.to_indexed(img)
    specs = [
        ('Hydrogen Plant  (SGHYD, 3x3, 90x60)', sghyd_mesh, 90, 60, 40, lambda k: current('sghyd', 90, 60, k)),
        ('Drone Bay  (SGDRN, 2x3, 66x54)', sgdrn_mesh, 66, 54, 37, lambda k: current('sgdrn', 66, 54, k)),
        ('Construction Yard  (FACT, 3x3, 72x72)  -- "current" = stock RA fact.shp', fact_mesh, 72, 72, 51, lambda k: stock_strip(0 if k == 0 else 26)),
        ('Solar Array  (SGPWR, 2x3, 66x54)  -- roster test', sgpwr_mesh, 66, 54, 38, lambda k: current('sgpwr', 66, 54, k)),
    ]
    cellw = 100 * SC
    canvas = Image.new('RGBA', (cellw * 6, len(specs) * 80 * SC), (30, 30, 30, 255))
    dr = ImageDraw.Draw(canvas)
    for r, (label, fn, w, h, oy, cur) in enumerate(specs):
        y0 = r * 80 * SC
        dr.text((6, y0 + 4), label, fill=(255, 255, 255, 255))
        dr.text((6, y0 + 16), 'current idle | current damaged | DRAFT idle (temperate) | DRAFT damaged | DRAFT idle (desert) | DRAFT damaged', fill=(200, 200, 200, 255))
        tiles = [preview(cur(0), w, h, GREEN), preview(cur(1), w, h, GREEN),
                 preview(build(fn, w, h, oy, False), w, h, GREEN), preview(build(fn, w, h, oy, True), w, h, GREEN),
                 preview(build(fn, w, h, oy, False), w, h, TAN), preview(build(fn, w, h, oy, True), w, h, TAN)]
        for c, t in enumerate(tiles):
            big = t.resize((w * SC, h * SC), Image.NEAREST)
            canvas.alpha_composite(big, (c * cellw + (cellw - big.width) // 2, y0 + 30 + (80 * SC - 30 - big.height) // 2))
    canvas.save('drafts.png')
    print('ok', canvas.size)

    # ---- in-context scene: drafts beside the ported stock buildings, 2x
    SC2 = 2
    scene = Image.new('RGBA', (560 * SC2, 200 * SC2), GREEN + (255,))
    # faint cell grid so the footprints can be judged
    g = ImageDraw.Draw(scene)
    for x in range(0, 560, 24): g.line([(x * SC2, 0), (x * SC2, 200 * SC2)], fill=dim(GREEN, 0.12) + (255,))
    for y in range(0, 200, 24): g.line([(0, y * SC2), (560 * SC2, y * SC2)], fill=dim(GREEN, 0.12) + (255,))
    def put(strip, w, h, x, y):
        t = preview(strip, w, h, GREEN)
        # transparent where the strip is 0 so the grid shows through
        p = strip.load(); tp = t.load()
        for yy in range(h):
            for xx in range(w):
                if p[xx, yy] == 0: tp[xx, yy] = (0, 0, 0, 0)
        scene.alpha_composite(t.resize((w * SC2, h * SC2), Image.NEAREST), (x * SC2, y * SC2))
    ww, wh, wf = read_shp(f'{B}/weap3.shp')
    put(stock_strip(0), fw, fh, 8, 8)                                  # stock Construction Yard
    put(build(fact_mesh, 72, 72, 51), 72, 72, 90, 8)                   # draft Construction Yard
    put(G.to_indexed(frame_rgba(ww, wh, wf[0], pal)), ww, wh, 176, 20)  # stock War Factory
    put(build(sghyd_mesh, 90, 60, 40), 90, 60, 256, 14)
    put(current('sghyd', 90, 60, 0), 90, 60, 356, 14)                  # current Hydrogen Plant for contrast
    put(build(sgdrn_mesh, 66, 54, 37), 66, 54, 20, 110)
    put(current('sgdrn', 66, 54, 0), 66, 54, 100, 110)
    put(build(sgpwr_mesh, 66, 54, 38), 66, 54, 190, 110)
    put(current('sgpwr', 66, 54, 0), 66, 54, 270, 110)
    put(current('sgvlt', 40, 36, 8), 40, 36, 356, 120)                 # current Battery Bank (untouched)
    put(current('rcyd', 40, 36, 8), 40, 36, 410, 120)                  # current Recycling Depot (untouched)
    g = ImageDraw.Draw(scene)
    for txt, x, y in (('stock FACT', 8, 82), ('DRAFT FACT', 90, 82), ('stock WEAP', 176, 70), ('DRAFT SGHYD', 256, 76), ('current SGHYD', 356, 76),
                      ('DRAFT SGDRN', 20, 166), ('current SGDRN', 100, 166), ('DRAFT SGPWR', 190, 166), ('current SGPWR', 270, 166), ('current SGVLT / RCYD', 356, 158)):
        g.text((x * SC2, y * SC2), txt, fill=(255, 255, 255, 255))
    scene.save('scene.png')
    print('scene ok')
