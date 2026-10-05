#!/usr/bin/env python3
"""Phase 6 chrome redesign (docs/BACKLOG.md issue #41).

Generates ALL thematic UI chrome from scratch — dialog.png, sidebar.png,
loadscreen.png(+2x/3x), the mod icons (../icon*.png) and the packaging
artwork (../../../packaging/artwork: the installer/desktop app icons and the
macOS disk-image background; docs/BACKLOG.md issue #114). Unlike the retired
first-pass reskin_chrome.py (which hue-shifted the stock RA art in place),
nothing here derives from stock pixels: every surface, bevel, button state
and the emblem are drawn programmatically in the locked palette
(docs/ART_DIRECTION.md), so the chrome no longer visually reads as
recolored OpenRA/RA.

Visual language ("grid-glass"): solar-panel blue-black surfaces carrying a
faint photovoltaic cell grid, living-green structural frames with a
top-left lit edge (same key-light convention as the issue #40 sprite
pass), and sun-gold reserved for highlighted/active states, filaments and
the emblem. Faction accents follow the established identities: The
Consortium (allies chrome ids) = gold, The Assembly (soviet ids) = green.

Geometry contract: canvas sizes and every pixel rect in
mods/sungrid/chrome.yaml (Regions/PanelRegion) are hard-coded below and
must never move — chrome.yaml addresses them by absolute coordinates.

Usage:
    pip install pillow
    python3 gen_chrome.py

Idempotent by construction: output depends only on this script, never on
the previous file contents.
"""
import itertools
import math
import os
from PIL import Image, ImageDraw, ImageFont

UIBITS = os.path.dirname(os.path.abspath(__file__))

# Locked palette (docs/ART_DIRECTION.md)
GREEN_MID = (0x2E, 0x7D, 0x46)
GREEN_ACCENT = (0x8B, 0xC3, 0x4A)
PANEL = (0x16, 0x23, 0x2E)          # solar panel blue-black
SUN_GOLD = (0xE8, 0xA9, 0x3D)

def mix(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))

def lift(c, d):
    return tuple(max(0, min(255, v + d)) for v in c)

BLACKLINE = lift(PANEL, -14)         # panel seam lines
PANEL_DEEP = lift(PANEL, -8)         # recessed surfaces
SLATE = mix(PANEL, GREEN_MID, 0.22)  # interactive surface (buttons)
GRAY = (0x2B, 0x31, 0x35)            # disabled
OBS = (0x24, 0x2E, 0x36)             # observer/neutral surface
GOLD_DIM = mix(SUN_GOLD, PANEL, 0.45)
GREEN_DIM = mix(GREEN_MID, PANEL, 0.35)


# --------------------------------------------------------------------------
# primitives

def pv_grid(img, x, y, w, h, base=PANEL, cell=16, line=-7, alt=2):
    """Photovoltaic cell-grid texture: base fill, darker gridlines, faint
    checker variation. Deterministic and tileable at `cell` period."""
    d = ImageDraw.Draw(img)
    d.rectangle((x, y, x + w - 1, y + h - 1), fill=base)
    for j in range(h):
        for_row = (y + j) % cell == 0
        for i in range(w):
            if for_row or (x + i) % cell == 0:
                img.putpixel((x + i, y + j), lift(base, line))
            elif alt and (((x + i) // cell + (y + j) // cell) % 2 == 0):
                img.putpixel((x + i, y + j), lift(base, alt))

def bevel(img, x, y, w, h, fill, border=2, light=None, dark=None, flat=False):
    """Filled rect with a lit top/left + shaded bottom/right edge."""
    d = ImageDraw.Draw(img)
    light = light or mix(fill, GREEN_ACCENT, 0.35)
    dark = dark or lift(fill, -18)
    d.rectangle((x, y, x + w - 1, y + h - 1), fill=fill)
    if flat:
        light = dark = lift(fill, -8)
    for b in range(border):
        d.line((x + b, y + b, x + w - 1 - b, y + b), fill=light)          # top
        d.line((x + b, y + b, x + b, y + h - 1 - b), fill=light)          # left
        d.line((x + b, y + h - 1 - b, x + w - 1 - b, y + h - 1 - b), fill=dark)  # bottom
        d.line((x + w - 1 - b, y + b, x + w - 1 - b, y + h - 1 - b), fill=dark)  # right

def inset(img, x, y, w, h, fill=PANEL_DEEP, frame=GREEN_DIM, radius=3):
    """Recessed slot: dark fill, soft low-contrast rounded frame, faint inner
    shadow at top. Rounded + blended toward `fill` (docs/BACKLOG.md issue #51
    follow-up: differently-sized hard-edged boxes across the sidebar read as a
    visible "step" between panels; a lower-contrast, rounded frame keeps the
    recessed-slot cue without each region reading as its own stark box)."""
    d = ImageDraw.Draw(img)
    soft_frame = mix(frame, fill, 0.35)
    r = min(radius, (h - 1) // 2)
    d.rounded_rectangle((x, y, x + w - 1, y + h - 1), radius=r, fill=fill)
    d.rounded_rectangle((x, y, x + w - 1, y + h - 1), radius=r, outline=soft_frame, width=1)
    d.line((x + 1 + r, y + 1, x + w - 2 - r, y + 1), fill=lift(fill, -10))


# --------------------------------------------------------------------------
# emblem — the Sungrid mark: sun rising over a living-green horizon inside a
# hexagonal grid cell, filaments feeding an outer ring ("the sun feeds the
# grid"). Drawn supersampled, returned RGBA with transparent background.

SS = 4

def emblem(size, accent=SUN_GOLD, simple=False):
    """`accent` drives the whole ring/hex/sun/rays so each faction's
    placeholder badge is genuinely its own mark (Consortium gold, Assembly
    green — docs/ART_DIRECTION.md), not a recolor-in-name-only.

    `simple` is the small-size cut (app icons below 48px, issue #114): no
    ring, filaments or vertex nodes — at 16-32px they are sub-pixel and only
    smear the silhouette — and a heavier hexagon so the mark still reads.
    Every existing caller keeps the full mark, so their output is unchanged."""
    s = size * SS
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx = cy = s / 2
    r = s * 0.46
    lw = max(SS, round(s * 0.014))
    # the hexagon's own stroke: heavier in the small-size cut, while rays and
    # the baseline keep `lw` so they don't weld to it
    hw = max(SS * 2, round(s * 0.035)) if simple else max(lw, round(s * 0.018))

    # outer ring
    if not simple:
        d.ellipse((cx - r, cy - r, cx + r, cy + r),
                  outline=accent + (110,), width=max(SS // 2, lw // 2))

    # hexagon (pointy-top) + vertex nodes + filaments to the ring
    hr = r * (0.92 if simple else 0.82)
    pts = [(cx + hr * math.sin(k * math.pi / 3),
            cy - hr * math.cos(k * math.pi / 3)) for k in range(6)]
    if not simple:
        for k in range(6):
            px, py = pts[k]
            ox = cx + r * math.sin(k * math.pi / 3)
            oy = cy - r * math.cos(k * math.pi / 3)
            d.line((px, py, ox, oy), fill=accent + (150,), width=max(SS // 2, lw // 2))
    # Issue #119 refinement (a designer pass is still pending - see
    # PLACEHOLDER_ART.md): the hexagon is filled panel-dark so the mark holds
    # on any background and its stroke is a touch heavier; the sun is *drawn*
    # (a limb-darkened disc with the highlight drifting up-left) rather than a
    # flat disc with a lighter disc on it; the rays are five tapered wedges;
    # and three small panel cells sit on the horizon - the grid the sun feeds.
    d.polygon(pts, fill=PANEL + (235,))
    d.polygon(pts, outline=accent + (255,), width=hw)
    if not simple:
        nr = s * 0.016
        for px, py in pts:
            d.ellipse((px - nr, py - nr, px + nr, py + nr), fill=accent + (255,))

    # sun disc, centered so the horizon band overlaps its lower third
    sr = hr * 0.44
    sy = cy - hr * 0.02
    rings = 14
    for i in range(rings):
        t = i / (rings - 1)  # 0 = outer limb, 1 = core
        rr = sr * (1 - 0.72 * t)
        ox, oy = -sr * 0.10 * t, -sr * 0.12 * t
        col = mix(lift(accent, -14), mix(accent, (255, 255, 255), 0.32), t)
        d.ellipse((cx + ox - rr, sy + oy - rr, cx + ox + rr, sy + oy + rr), fill=col + (255,))
    if not simple:
        d.ellipse((cx - sr * 1.10, sy - sr * 1.10, cx + sr * 1.10, sy + sr * 1.10),
                  outline=accent + (70,), width=max(SS, lw))

    # five tapered rays above the sun, the middle one longest
    rays = ((-0.9, 1.42), (-0.45, 1.55), (0.0, 1.70), (0.45, 1.55), (0.9, 1.42))
    for off, length in rays:
        ang = -math.pi / 2 + off
        x0 = cx + (sr * 1.20) * math.cos(ang)
        y0 = sy + (sr * 1.20) * math.sin(ang)
        x1 = cx + (sr * length) * math.cos(ang)
        y1 = sy + (sr * length) * math.sin(ang)
        nx, ny = -math.sin(ang) * lw * 0.9, math.cos(ang) * lw * 0.9
        d.polygon([(x0 + nx, y0 + ny), (x0 - nx, y0 - ny), (x1, y1)], fill=accent + (235,))

    # horizon band (two-tone living green), clipped to the hexagon width
    bw = hr * 0.80
    t0 = sy + sr * 0.28
    t1 = sy + sr * 1.05  # past the disc's lower limb so no gold pokes out below
    d.rectangle((cx - bw, t0, cx + bw, (t0 + t1) / 2), fill=GREEN_MID + (255,))
    d.rectangle((cx - bw, (t0 + t1) / 2, cx + bw, t1), fill=lift(GREEN_MID, -16) + (255,))
    d.line((cx - bw, t0, cx + bw, t0), fill=GREEN_ACCENT + (255,), width=max(SS // 2, lw // 2))
    if not simple:
        # three panel cells on the horizon (sub-pixel below 48px, so the
        # simple cut leaves them out, like the ring and filaments)
        cw, gap = bw * 0.18, bw * 0.10
        ya = (t0 + t1) / 2 + (t1 - t0) * 0.08
        yb = t1 - (t1 - t0) * 0.10
        for j in (-1, 0, 1):
            xa = cx + j * (cw + gap) - cw / 2
            d.rectangle((xa, ya, xa + cw, yb), fill=lift(GREEN_MID, -30) + (255,),
                        outline=GREEN_ACCENT + (255,), width=max(1, SS // 2))
    # faction accent baseline under the horizon
    d.line((cx - bw, t1 + lw * 1.5, cx + bw, t1 + lw * 1.5), fill=accent + (255,), width=lw)

    return im.resize((size, size), Image.LANCZOS)

def emblem_consortium(size, accent=SUN_GOLD):
    """Consortium mark — "Citadel Seal" (second pass): hardened and
    centralized, not a recolor of the shared sun mark. docs/BUILDINGS.md: a
    Consortium facility "matching the Consortium's capital-technocratic
    infrastructure philosophy" (hardened, centralized) vs. the Assembly's
    decentralized, improvisational one. A thick solid fortress-wall hex
    over a translucent keep wash, spokes converging inward (capital
    concentrating to one point, not radiating out), square rivet nodes
    (industrial, not organic), and a cut-gem vault core rather than a sun.

    Redone bolder than the first pass (docs/BACKLOG.md issue #52): the
    original thin-line wall + 16-tick metering ring turned to mush below
    ~32px, and this mark now also has to read at lobby-flag scale (15px
    tall, see gen_flags below). Line weights are proportional with much
    higher floors, the wall is a solid filled band, and fine detail
    (metering ticks, the inner vault wall) only draws at sizes with the
    pixels to resolve it."""
    s = size * SS
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx = cy = s / 2
    r = s * 0.46
    fine = size >= 40   # detail tier: below this, ticks/inner wall just blur

    # metering ring (fine tier only): gauge/ledger precision ticks
    if fine:
        for i in range(16):
            ang = 2 * math.pi * i / 16
            x0, y0 = cx + r * 0.99 * math.cos(ang), cy + r * 0.99 * math.sin(ang)
            x1, y1 = cx + r * 0.88 * math.cos(ang), cy + r * 0.88 * math.sin(ang)
            d.line((x0, y0, x1, y1), fill=accent + (150,), width=max(SS // 2, round(s * 0.012)))

    def hexpts(rad):
        return [(cx + rad * math.sin(k * math.pi / 3),
                 cy - rad * math.cos(k * math.pi / 3)) for k in range(6)]

    # fortress wall: a solid filled band (outer hex minus inner hex), far
    # bolder than an outline stroke. ImageDraw fills replace pixels (no
    # compositing), so punching the yard with a faint wash both carves the
    # wall band and leaves a translucent keep fill in one step.
    hr = r * (0.80 if fine else 0.88)
    wall = hr * 0.20
    d.polygon(hexpts(hr), fill=accent + (255,))
    d.polygon(hexpts(hr - wall), fill=accent + (45,))                # punch the yard

    # inner vault wall (fine tier only)
    if fine:
        d.polygon(hexpts(hr * 0.55), outline=mix(accent, PANEL, 0.15) + (255,),
                  width=max(SS, round(s * 0.014)))

    # spokes converging inward — centralization, the mirror image of the
    # neutral mark's filaments feeding outward to a ring
    for px, py in hexpts(hr - wall):
        d.line((px, py, cx, cy), fill=accent + (120,), width=max(SS // 2, round(s * 0.014)))

    # square rivet nodes at the outer vertices — precision hardware
    nr = s * (0.024 if fine else 0.034)
    for px, py in hexpts(hr):
        d.rectangle((px - nr, py - nr, px + nr, py + nr), fill=accent + (255,))

    # central core: a cut-gem diamond (vault asset / capital), not a sun disc
    cr = hr * 0.34
    d.polygon([(cx, cy - cr), (cx + cr, cy), (cx, cy + cr), (cx - cr, cy)],
              fill=accent + (255,))
    icr = cr * 0.52
    d.polygon([(cx, cy - icr), (cx + icr, cy), (cx, cy + icr), (cx - icr, cy)],
              fill=mix(accent, (255, 255, 255), 0.45) + (255,))

    return im.resize((size, size), Image.LANCZOS)


def emblem_assembly(size, accent=GREEN_ACCENT):
    """Assembly mark — "Swarm Rig" (second pass): decentralized and
    improvisational, not a recolor of the shared sun mark.
    docs/BUILDINGS.md/docs/ART_DIRECTION.md: "cheap, mass-producible...
    decentralized, improvisational infrastructure philosophy" and the
    "decentralized/drone-based" faction axis. Three unevenly sized nodes in
    a peer mesh (no single hub, unlike the Consortium's converging spokes),
    kinked strut cabling, and a drone rotor standing in for a sun.

    Redone bolder than the first pass (docs/BACKLOG.md issue #52): thin
    struts and dim node fills disappeared below ~32px, and this mark now
    also has to read at lobby-flag scale (15px tall, see gen_flags below).
    Node fills are brighter, outlines/struts much heavier, and the weld
    rivet dots only draw at sizes that can resolve them."""
    s = size * SS
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx = cy = s / 2
    r = s * 0.46
    fine = size >= 40

    # three asymmetric nodes: unequal size, offset — a peer mesh, not a hub
    nodes = [
        (cx - r * 0.36, cy - r * 0.28, r * (0.44 if fine else 0.50)),
        (cx + r * 0.46, cy - r * 0.10, r * (0.31 if fine else 0.36)),
        (cx + r * 0.02, cy + r * 0.50, r * (0.26 if fine else 0.30)),
    ]

    # mesh struts between every pair, each with a slight kink — hand-run cabling
    strut_w = max(SS, round(s * 0.030))
    for (x0, y0, _), (x1, y1, _) in itertools.combinations(nodes, 2):
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        dx, dy = x1 - x0, y1 - y0
        nlen = math.hypot(dx, dy) or 1
        jx, jy = -dy / nlen, dx / nlen
        j = s * 0.014
        d.line([(x0, y0), (mx + jx * j, my + jy * j), (x1, y1)],
               fill=accent + (220,), width=strut_w, joint="curve")
        if fine:
            for t in (0.3, 0.7):
                rx, ry = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
                d.ellipse((rx - SS, ry - SS, rx + SS, ry + SS),
                          fill=mix(accent, PANEL, 0.2) + (255,))

    # irregular hex node bodies — bright fill + heavy outline so each node
    # holds together as a solid chip even at flag scale
    for nx, ny, nr in nodes:
        pts = [(nx + nr * math.sin(k * math.pi / 3), ny - nr * math.cos(k * math.pi / 3)) for k in range(6)]
        d.polygon(pts, fill=mix(accent, PANEL, 0.40) + (255,),
                  outline=accent + (255,), width=max(SS, round(s * 0.022)))

    # drone rotor on the largest node — drone-based identity, not a sun
    hx, hy, hr = nodes[0]
    blade_len = hr * 0.92
    for k in range(3):
        ang = k * (2 * math.pi / 3) - math.pi / 2
        x1 = hx + blade_len * math.cos(ang)
        y1 = hy + blade_len * math.sin(ang)
        perp = ang + math.pi / 2
        w = hr * 0.22
        p0 = (hx + w * math.cos(perp), hy + w * math.sin(perp))
        p1 = (hx - w * math.cos(perp), hy - w * math.sin(perp))
        d.polygon([p0, p1, (x1, y1)], fill=accent + (255,))
    d.ellipse((hx - hr * 0.18, hy - hr * 0.18, hx + hr * 0.18, hy + hr * 0.18),
              fill=mix(accent, (255, 255, 255), 0.35) + (255,))

    return im.resize((size, size), Image.LANCZOS)


def emblem_panel(size, accent=SUN_GOLD, kind="neutral"):
    """Opaque framed panel with the emblem centered — radar placeholder /
    loadscreen badge. `kind` picks the mark: 'neutral' (shared brand, used
    by the main menu logo and mod icon — unchanged), 'consortium', or
    'assembly' (the two faction-distinct marks above).

    Frame softened (docs/BACKLOG.md issue #51 follow-up): the original
    3-ring, full-contrast outline made this panel read as its own hard box
    next to the sidebar's other (differently sized) bordered regions. Down
    to a single low-contrast rounded outline — still a frame, not stock's
    borderless texture, but no longer a competing hard edge."""
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    pv_grid(im, 0, 0, size, size, base=PANEL, cell=max(8, size // 14), line=-6, alt=2)
    d = ImageDraw.Draw(im)
    r = max(2, size // 30)
    d.rounded_rectangle((0, 0, size - 1, size - 1), radius=r,
                        outline=mix(GREEN_MID, PANEL, 0.30), width=2)
    mark_fn = {"consortium": emblem_consortium, "assembly": emblem_assembly}.get(kind, emblem)
    e = mark_fn(round(size * 0.86), accent)
    im.alpha_composite(e, ((size - e.width) // 2, (size - e.height) // 2))
    return im


# --------------------------------------------------------------------------
# wordmark badge — the 256x256 `logo` region of loadscreen.png, which is both
# what LogoStripeLoadScreen centres on the load screen and what
# chrome/mainmenu.yaml's Image@LOGO shows top-right of the main menu
# (chrome.yaml `logos: logo: 0,0,256,256`). Until issue #118 this slot held
# the bare emblem_panel: the emblem alone, so neither the load screen nor the
# main menu ever said the game's name — the title only appeared as a Bold
# label inside the 200px menu panel. The badge now carries the name in the
# mod's own Title face (ZoodRangmah, the same face as the DMG background and
# stock RA's own menu logo), stacked on two lines so it fills the 256px slot
# at a cap height that still reads at 1x.

def wordmark_badge(size, scale=1):
    """Grid-glass tile (same recipe as emblem_panel) with the neutral emblem
    on top and SUNGRID / PROTOCOL beneath, sun-gold, over a living-green
    rule. `scale` only widens the outline and rule so the -2x/-3x sheets
    stay a true upscale of the 1x layout."""
    font_path = os.path.join(os.path.dirname(UIBITS), "ZoodRangmah.ttf")
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    pv_grid(im, 0, 0, size, size, base=PANEL, cell=max(8, size // 14), line=-6, alt=2)
    d = ImageDraw.Draw(im)
    r = max(2, size // 30)
    d.rounded_rectangle((0, 0, size - 1, size - 1), radius=r,
                        outline=mix(GREEN_MID, PANEL, 0.30), width=2 * scale)
    e = emblem(round(size * 0.54), SUN_GOLD)
    im.alpha_composite(e, ((size - e.width) // 2, round(size * 0.05)))
    f = ImageFont.truetype(font_path, round(size * 0.215))
    y = round(size * 0.615)
    sp = round(size * 0.008)  # letter-spacing: ZoodRangmah sets tight (issue #119)
    for t in ("SUNGRID", "PROTOCOL"):
        tw = sum(f.getlength(ch) for ch in t) + sp * (len(t) - 1)
        x = size / 2 - tw / 2
        for ch in t:
            # 1px-per-scale shadow so the gold holds its edge over the cell grid
            d.text((x + scale, y + scale), ch, font=f, fill=BLACKLINE, anchor="lt")
            d.text((x, y), ch, font=f, fill=SUN_GOLD, anchor="lt")
            x += f.getlength(ch) + sp
        y = d.textbbox((0, y), t, font=f, anchor="lt")[3] + round(size * 0.025)
    ry = size - round(size * 0.055)
    d.line((round(size * 0.2), ry, size - round(size * 0.2), ry),
           fill=GREEN_MID, width=max(1, scale))
    return im


# --------------------------------------------------------------------------
# glyphs.png faction-flag patch: the lobby/observer `flags` collection
# (chrome.yaml) still ships the stock RA sheet, so The Consortium's logo slot
# carried the stock Allied eagle and The Assembly's the Soviet
# hammer-and-sickle — literal Cold War heraldry contradicting both factions'
# documented identities (docs/BUILDINGS.md's infrastructure-philosophy axis,
# docs/ART_DIRECTION.md). Replaced with plaques carrying the two faction
# marks above (Citadel Seal / Swarm Rig), so the logo a player picks a side
# by matches the badge their sidebar then shows.
#
# Unlike everything else in this file, this PATCHES the existing glyphs
# sheets in place rather than regenerating them: glyphs.png is otherwise
# still stock content (cash/power icons, checkboxes, sub-faction flags...)
# that is NOT being replaced here. Idempotent for the two regions it owns —
# their pixels depend only on this script. Sub-faction slots are handled
# below (FLAG_BORDER_SOVIET notes): western nation flags stay stock by
# direct request, and the three slots whose displayed sub-faction no longer
# matches the stock art (Greece / China / Iran) get corrected art.

FLAG_W, FLAG_H = 30, 15
FLAG_REGIONS = {          # chrome.yaml `flags:` region origins, 1x units
    "allies": (226, 177, "consortium", SUN_GOLD),
    "soviet": (226, 193, "assembly", GREEN_ACCENT),
}

# Sub-faction flag corrections. The western nation flags stay exactly as
# stock (direct request), but three slots no longer match the sub-faction
# they display for:
#  - russia's slot showed the USSR flag while the faction now displays
#    "China" (docs/BACKLOG.md issue #55) -> a PRC flag.
#  - ukraine's slot showed the UkSSR flag while the faction now displays
#    "Iran" (issue #54) -> an Iranian flag.
#  - england's slot shows the Union Jack while the faction now displays
#    "Greece" (direct request: Greece as a Consortium nation, replacing
#    England) -> stock already ships a Greek flag in its own (unused)
#    `greece` slot, so that art is copied verbatim into the england region.
#  - france's slot showed the French tricolore; on direct request the
#    faction is now the USA -> a US flag.
# Border convention sampled from the stock sheet: Consortium-side flags use
# a 1px light-blue frame (89,144,255), Assembly-side a red one (191,0,0).
FLAG_BORDER_SOVIET = (191, 0, 0)
FLAG_BORDER_ALLIED = (89, 144, 255)
GREECE_SRC, ENGLAND_DST = (226, 129), (226, 49)   # copy greece -> england


def _star(d, cx, cy, r, fill):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=fill)


def _framed_flag(scale, draw_fn, border):
    """Draw a 30x15 flag supersampled, downscale, then apply the stock-style
    1px (per scale) border frame."""
    s = 4
    w, h = FLAG_W * scale * s, FLAG_H * scale * s
    im = Image.new("RGBA", (w, h))
    draw_fn(ImageDraw.Draw(im), w, h)
    im = im.resize((FLAG_W * scale, FLAG_H * scale), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    for b in range(scale):
        d.rectangle((b, b, FLAG_W * scale - 1 - b, FLAG_H * scale - 1 - b), outline=border)
    return im


def china_flag(scale):
    def draw(d, w, h):
        d.rectangle((0, 0, w, h), fill=(0xDE, 0x29, 0x10))
        gold = (0xFF, 0xDE, 0x00)
        u = h / 15.0
        _star(d, 5.5 * u, 5 * u, 3.2 * u, gold)
        for sx, sy in ((10.5, 1.6), (12.2, 3.6), (12.2, 6.2), (10.5, 8.2)):
            _star(d, sx * u, sy * u, 1.1 * u, gold)
    return _framed_flag(scale, draw, FLAG_BORDER_SOVIET)


def iran_flag(scale):
    def draw(d, w, h):
        green, white, red = (0x23, 0x9F, 0x40), (0xF0, 0xF0, 0xF0), (0xDA, 0x00, 0x00)
        d.rectangle((0, 0, w, h / 3), fill=green)
        d.rectangle((0, h / 3, w, 2 * h / 3), fill=white)
        d.rectangle((0, 2 * h / 3, w, h), fill=red)
        # Simplified central emblem (the tulip monogram): a center blade
        # between two mirrored crescent strokes -- legible at 15px, no
        # attempt at the full calligraphy.
        cx, cy = w / 2, h / 2
        u = h / 15.0
        lw = max(1, round(0.5 * u))
        d.line((cx, cy - 1.9 * u, cx, cy + 1.9 * u), fill=red, width=lw)
        d.arc((cx - 2.1 * u, cy - 1.7 * u, cx - 0.2 * u, cy + 1.9 * u), 110, 320, fill=red, width=lw)
        d.arc((cx + 0.2 * u, cy - 1.7 * u, cx + 2.1 * u, cy + 1.9 * u), 220, 70, fill=red, width=lw)
    return _framed_flag(scale, draw, FLAG_BORDER_SOVIET)


def usa_flag(scale):
    def draw(d, w, h):
        red, white, blue = (0xB2, 0x22, 0x34), (0xF0, 0xF0, 0xF0), (0x3C, 0x3B, 0x6E)
        u = h / 15.0
        # 13 stripes, red outermost.
        for i in range(13):
            y0 = h * i / 13
            y1 = h * (i + 1) / 13
            d.rectangle((0, y0, w, y1), fill=red if i % 2 == 0 else white)
        # Canton over the top 7 stripes with a dot-grid of stars (50 don't
        # resolve at 15px; a legible grid stands in).
        cw, ch = 12 * u * 2, h * 7 / 13
        d.rectangle((0, 0, cw, ch), fill=blue)
        r = 0.55 * u
        for row in range(3):
            for col in range(4):
                sx = cw * (col + 0.5 + (row % 2) * 0.28) / 4.6
                sy = ch * (row + 0.6) / 3.4
                d.ellipse((sx - r, sy - r, sx + r, sy + r), fill=white)
    return _framed_flag(scale, draw, FLAG_BORDER_ALLIED)


def flag_plaque(scale, kind, accent):
    """One faction-logo plaque at FLAG_W x FLAG_H times `scale`: panel
    surface, soft accent frame, the faction mark centered."""
    w, h = FLAG_W * scale, FLAG_H * scale
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # panel surface with a slight vertical ramp (too small for pv_grid texture)
    for y in range(h):
        d.line((0, y, w - 1, y), fill=mix(lift(PANEL, 6), lift(PANEL, -6), y / (h - 1)))
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=2 * scale,
                        outline=mix(accent, PANEL, 0.35), width=scale)
    mark_fn = {"consortium": emblem_consortium, "assembly": emblem_assembly}[kind]
    m = mark_fn((FLAG_H - 2) * scale, accent)
    im.alpha_composite(m, ((w - m.width) // 2, (h - m.height) // 2))
    return im


def gen_flags():
    # NB: glyphs-3x.png is a genuine 3x layout on an oversized 1024px canvas
    # (content occupies the 768px top-left; the rest is padding) — verified
    # against the stock sheet's own flag positions, so patch at scale 3.
    for name, scale in (("glyphs.png", 1), ("glyphs-2x.png", 2), ("glyphs-3x.png", 3)):
        path = f"{UIBITS}/{name}"
        sheet = Image.open(path).convert("RGBA")
        for x, y, kind, accent in FLAG_REGIONS.values():
            plaque = flag_plaque(scale, kind, accent)
            sheet.paste(plaque, (x * scale, y * scale))
        # Sub-faction corrections (see the notes above FLAG_BORDER_SOVIET):
        # greece's stock art -> england's slot (the faction displays Greece),
        # then PRC/Iran flags into russia's/ukraine's slots (they display
        # China/Iran). The greece source region is never written to, so the
        # copy stays idempotent across re-runs.
        gsx, gsy = GREECE_SRC
        edx, edy = ENGLAND_DST
        greece = sheet.crop((gsx * scale, gsy * scale,
                             (gsx + FLAG_W) * scale, (gsy + FLAG_H) * scale))
        sheet.paste(greece, (edx * scale, edy * scale))
        sheet.paste(china_flag(scale), (226 * scale, 161 * scale))   # russia slot
        sheet.paste(iran_flag(scale), (226 * scale, 145 * scale))    # ukraine slot
        sheet.paste(usa_flag(scale), (226 * scale, 81 * scale))      # france slot
        sheet.save(path)
        print(name, "flags patched", sheet.size)


# --------------------------------------------------------------------------
# dialog.png (1024x512)

def button_block(img, x, y, size, fill, accent=None, pressed=False,
                 disabled=False, border=2):
    """One PanelRegion button block. `accent` draws a colored outer ring
    (highlighted states)."""
    if disabled:
        bevel(img, x, y, size, size, GRAY, border, flat=True)
        return
    light = mix(fill, GREEN_ACCENT, 0.40)
    dark = lift(fill, -20)
    if pressed:
        light, dark = dark, lift(fill, 6)
        fill = lift(fill, -12)
    bevel(img, x, y, size, size, fill, border, light=light, dark=dark)
    if accent:
        ImageDraw.Draw(img).rectangle((x, y, x + size - 1, y + size - 1),
                                      outline=accent, width=max(1, border - 1))

def gen_dialog():
    W, H = 1024, 512
    im = Image.new("RGBA", (W, H), BLACKLINE + (255,))

    # dialog background (1,1,480,480) — grid-glass surface
    pv_grid(im, 1, 1, 480, 480, base=PANEL, cell=16, line=-7, alt=2)

    # border strips: 9px cross-section, uniform along the tiling axis
    profile = [BLACKLINE, GREEN_MID, GREEN_MID, GREEN_ACCENT,
               mix(PANEL, GREEN_MID, 0.10), PANEL, PANEL, PANEL, BLACKLINE]
    d = ImageDraw.Draw(im)
    for i, c in enumerate(profile):                      # border-l (483,1,9,190)
        d.line((483 + i, 1, 483 + i, 190), fill=c)
    for i, c in enumerate(reversed(profile)):            # border-r (492,1,9,190)
        d.line((492 + i, 1, 492 + i, 190), fill=c)
    for i, c in enumerate(profile):                      # border-t (1,483,189,9)
        d.line((1, 483 + i, 189, 483 + i), fill=c)
    for i, c in enumerate(reversed(profile)):            # border-b (1,492,189,9)
        d.line((1, 492 + i, 189, 492 + i), fill=c)
    # corners 9x9: L-bend of the same profile
    for j in range(9):
        for i in range(9):
            im.putpixel((192 + i, 483 + j), profile[min(i, j)])          # tl
            im.putpixel((201 + i, 483 + j), profile[min(8 - i, j)])      # tr
            im.putpixel((192 + i, 492 + j), profile[min(i, 8 - j)])      # bl
            im.putpixel((201 + i, 492 + j), profile[min(8 - i, 8 - j)])  # br

    B = 126  # dialog button blocks (PanelRegion 2,2,122,122,2,2)
    button_block(im, 513, 1, B, SLATE)                                   # button
    button_block(im, 641, 1, B, SLATE, pressed=True)                     # button-pressed
    button_block(im, 769, 1, B, SLATE, accent=GREEN_ACCENT)              # newsbutton-highlighted
    button_block(im, 897, 1, B, SLATE, accent=SUN_GOLD)                  # checkbox-highlighted
    button_block(im, 513, 129, B, lift(SLATE, 12))                       # button-hover
    button_block(im, 641, 129, B, lift(SLATE, 12))                       # checkbox-hover
    button_block(im, 769, 129, B, SLATE, accent=SUN_GOLD)                # button-highlighted
    button_block(im, 897, 129, B, SLATE, accent=GOLD_DIM, pressed=True)  # button-highlighted-pressed
    button_block(im, 513, 257, B, GRAY, disabled=True)                   # button-disabled
    button_block(im, 641, 257, B, GRAY, disabled=True)                   # checkbox-disabled
    button_block(im, 769, 257, B, OBS)                                   # observer-scrollpanel-button
    button_block(im, 897, 257, B, OBS, pressed=True)                     # observer-scrollpanel-button-pressed
    button_block(im, 769, 385, B, GRAY, disabled=True)                   # observer-scrollpanel-button-disabled

    # dialog4 tooltip panel (512,387,6,6,52,52,6,6 -> 64x64)
    d.rectangle((512, 387, 512 + 63, 387 + 63), fill=lift(PANEL, -4))
    d.rectangle((512, 387, 512 + 63, 387 + 63), outline=BLACKLINE, width=1)
    d.rectangle((513, 388, 512 + 62, 387 + 62), outline=GREEN_MID, width=2)
    d.rectangle((515, 390, 512 + 60, 387 + 60), outline=lift(PANEL, -8), width=1)

    # dialog5 pure-black tile (580,388,62x62)
    d.rectangle((580, 388, 580 + 61, 388 + 61), fill=(0, 0, 0))

    # mainmenu-border (650,389,39,39,38,38,39,39 -> 116x116), edges only:
    # heavy structural frame with a gold filament inset
    mm = 116
    x0, y0 = 650, 389
    d.rectangle((x0, y0, x0 + mm - 1, y0 + mm - 1), fill=PANEL)
    d.rectangle((x0 + 2, y0 + 2, x0 + mm - 3, y0 + mm - 3), outline=BLACKLINE, width=2)
    d.rectangle((x0 + 4, y0 + 4, x0 + mm - 5, y0 + mm - 5), outline=GREEN_MID, width=3)
    d.rectangle((x0 + 7, y0 + 7, x0 + mm - 8, y0 + mm - 8), outline=GREEN_ACCENT, width=1)
    d.rectangle((x0 + 12, y0 + 12, x0 + mm - 13, y0 + mm - 13), outline=GOLD_DIM, width=1)
    d.rectangle((x0 + 14, y0 + 14, x0 + mm - 15, y0 + mm - 15), outline=BLACKLINE, width=1)

    # Issue #119: the free 126x126 block at (897,385) holds the Grid Reserve HUD
    # chrome, the small emblems the lobby header and the HUD use, and the content
    # installer's disc icon. chrome.yaml names each rect; keep them in step.
    grid_reserve_chrome(im, 897, 385)

    im.convert("RGB").save(f"{UIBITS}/dialog.png")
    print("dialog.png", im.size)


def grid_reserve_chrome(im, x0, y0):
    """Grid Reserve HUD panel, bars, battery glyph, small emblems, disc icon.

    grid-reserve-panel  (x0,     y0,     64x64)  PanelRegion 6/52/6: panel blue-black,
                                                 living-green frame, gold filament on
                                                 the lit (top/left) edge
    grid-reserve-icon   (x0+66,  y0,     16x16)  a Battery Bank cell, gold on panel
    emblem-24           (x0+66,  y0+18,  24x24)  neutral mark, lobby header / HUD
    emblem-32           (x0+92,  y0,     32x32)  neutral mark, larger
    cd-icon             (x0+92,  y0+34,  20x20)  the content installer's disc
    grid-reserve-bar-bg      (x0, y0+67, 64x12)  PanelRegion 3/58/3, recessed slot
    grid-reserve-bar-thumb   (x0, y0+80, 64x12)  banking: living-green fill
    grid-reserve-bar-lockdown(x0, y0+93, 64x12)  own Lockdown hold: sun-gold fill
    grid-reserve-bar-enemy   (x0, y0+106,64x12)  an opponent's hold: amber-red fill
    """
    d = ImageDraw.Draw(im)
    # panel
    d.rectangle((x0, y0, x0 + 63, y0 + 63), fill=PANEL)
    pv_grid(im, x0 + 1, y0 + 1, 62, 62, base=PANEL, cell=8, line=-6, alt=2)
    d.rectangle((x0, y0, x0 + 63, y0 + 63), outline=BLACKLINE, width=1)
    d.rectangle((x0 + 1, y0 + 1, x0 + 62, y0 + 62), outline=GREEN_MID, width=2)
    d.line((x0 + 3, y0 + 3, x0 + 60, y0 + 3), fill=GOLD_DIM)
    d.line((x0 + 3, y0 + 3, x0 + 3, y0 + 60), fill=GOLD_DIM)
    d.rectangle((x0 + 4, y0 + 4, x0 + 59, y0 + 59), outline=lift(PANEL, -6), width=1)

    # battery glyph 16x16: a cell with a terminal nub, three gold charge bars
    bx, by = x0 + 66, y0
    d.rectangle((bx, by, bx + 15, by + 15), fill=PANEL)
    d.rectangle((bx + 1, by + 3, bx + 12, by + 12), outline=GREEN_ACCENT, width=1)
    d.rectangle((bx + 13, by + 6, bx + 14, by + 9), fill=GREEN_ACCENT)
    for i in range(3):
        d.rectangle((bx + 3 + i * 3, by + 5, bx + 4 + i * 3, by + 10), fill=SUN_GOLD)

    # small emblems on transparency-free panel tiles
    for size, (ex, ey) in ((24, (x0 + 66, y0 + 18)), (32, (x0 + 92, y0))):
        d.rectangle((ex, ey, ex + size - 1, ey + size - 1), fill=PANEL)
        e = emblem(size, SUN_GOLD, simple=size < 48)
        im.alpha_composite(e, (ex, ey))

    # disc icon 20x20 (content installer: "install from disc")
    cx, cy = x0 + 92, y0 + 34
    d.rectangle((cx, cy, cx + 19, cy + 19), fill=PANEL)
    d.ellipse((cx + 2, cy + 2, cx + 17, cy + 17), fill=mix(PANEL, (255, 255, 255), 0.55), outline=BLACKLINE)
    d.ellipse((cx + 5, cy + 5, cx + 14, cy + 14), outline=GOLD_DIM, width=1)
    d.ellipse((cx + 8, cy + 8, cx + 11, cy + 11), fill=PANEL)

    # bars: 64x12, 3px frame + 58x6 body
    def bar(y, fill):
        d.rectangle((x0, y, x0 + 63, y + 11), fill=PANEL_DEEP)
        d.rectangle((x0, y, x0 + 63, y + 11), outline=BLACKLINE, width=1)
        d.rectangle((x0 + 1, y + 1, x0 + 62, y + 10), outline=lift(PANEL, -4), width=1)
        if fill is not None:
            d.rectangle((x0 + 2, y + 2, x0 + 61, y + 9), fill=fill)
            d.line((x0 + 2, y + 2, x0 + 61, y + 2), fill=mix(fill, (255, 255, 255), 0.25))
            d.line((x0 + 2, y + 9, x0 + 61, y + 9), fill=lift(fill, -18))
    bar(y0 + 67, None)
    bar(y0 + 80, GREEN_MID)
    bar(y0 + 93, SUN_GOLD)
    bar(y0 + 106, (0xC7, 0x3B, 0x2E))


# --------------------------------------------------------------------------
# sidebar.png (512x512)

def gen_sidebar():
    W = H = 512
    im = Image.new("RGBA", (W, H), PANEL + (255,))
    d = ImageDraw.Draw(im)

    # commandbar background (0,0,434,44)
    pv_grid(im, 0, 0, 434, 44, base=lift(PANEL, 3), cell=11, line=-6, alt=2)
    d.line((0, 0, 433, 0), fill=GREEN_ACCENT)
    d.line((0, 1, 433, 1), fill=GREEN_MID)
    d.rectangle((0, 41, 433, 43), fill=GREEN_MID)
    d.line((0, 43, 433, 43), fill=BLACKLINE)

    # moneybin strips: soviet/Assembly (0,54) green accent, allies/Consortium
    # (0,85) gold accent — recessed credit readouts.
    # NB: the real cash/power icons (glyphs.png, cash-icons/power-icons in
    # chrome.yaml) and the game-timer label are drawn by the engine ON TOP
    # of this background at runtime (see Image@CASH_ICON/@POWER_ICON in
    # chrome/ingame-player.yaml) — leave that band clear of decoration so a
    # baked shape doesn't collide with the live cash icon and read as a
    # stray glitch next to the money counter (docs/BACKLOG.md issue #50).
    for y, accent in ((54, GREEN_ACCENT), (85, SUN_GOLD)):
        inset(im, 0, y, 238, 28, fill=PANEL_DEEP, frame=GREEN_DIM)
        d.line((2, y + 25, 235, y + 25), fill=mix(accent, PANEL, 0.35))

    # background-iconrow (0,116,238,47): this is the PALETTE_FOREGROUND overlay
    # drawn ON TOP of the production icons (its widget is listed after
    # ProductionPalette in ingame-player.yaml), tiled once per icon row. It MUST
    # stay transparent over the icon cells — a solid fill here hides every
    # buildable and empties the build menu. Draw only thin cell frames; leave
    # the cell interiors fully transparent so the icons underneath show through.
    ir_y, ir_h = 116, 47
    im.paste((0, 0, 0, 0), (0, ir_y, 238, ir_y + ir_h))
    # icon columns align with ProductionPalette (X:42 in the widget, 62px cells,
    # 1px margin -> column origins 42, 105, 168). Softened (docs/BACKLOG.md
    # issue #51 follow-up): a full per-column box outline read as a fenced
    # grid boxing in the icons, sharper than the panels around it — down to
    # just a faint lit top edge per column, no side/bottom lines, so the row
    # reads as a shelf rather than a set of cells.
    for cx in (42, 105, 168):
        d.line((cx - 1, ir_y, cx + 62, ir_y), fill=mix(GREEN_ACCENT, PANEL, 0.25))

    # thin trims: background-bottom (0,166,238,8), observer-bottom (0,176,238,8)
    for y in (166, 176):
        d.rectangle((0, y, 237, y + 7), fill=PANEL)
        d.line((0, y + 2, 237, y + 2), fill=GREEN_MID)
        d.line((0, y + 3, 237, y + 3), fill=GREEN_MID)
        d.line((0, y + 4, 237, y + 4), fill=lift(GREEN_MID, -18))

    # sidebar body (0,185,238,287 incl. observer variant to y=472)
    pv_grid(im, 0, 185, 238, 287, base=PANEL, cell=14, line=-6, alt=2)
    d.line((0, 185, 237, 185), fill=lift(PANEL, 8))
    d.line((2, 185, 2, 471), fill=GREEN_DIM)          # structural filament, left
    d.line((235, 185, 235, 471), fill=GREEN_DIM)      # structural filament, right

    # icon-slot recesses inside the body: allies (12,227,190,47) gold,
    # soviet (12,275,190,47) green
    inset(im, 12, 227, 190, 47, fill=PANEL_DEEP, frame=GOLD_DIM)
    inset(im, 12, 275, 190, 47, fill=PANEL_DEEP, frame=GREEN_DIM)
    # support-power slots: allies (12,324,64,48), soviet (77,324,64,48)
    inset(im, 12, 324, 64, 48, fill=PANEL_DEEP, frame=GOLD_DIM)
    inset(im, 77, 324, 64, 48, fill=PANEL_DEEP, frame=GREEN_DIM)

    # replay-bottom (0,472,238,40)
    pv_grid(im, 0, 472, 238, 40, base=lift(PANEL, 2), cell=10, line=-6, alt=2)
    d.line((0, 472, 237, 472), fill=GREEN_MID)
    d.line((0, 511, 237, 511), fill=BLACKLINE)

    # 28x28 sidebar button states at x=260 (PanelRegion 5,5,18,18,5,5).
    # soviet/Assembly rows use green accents, allies/Consortium gold,
    # observer neutral.
    S = 28
    states = [
        (136, lift(SLATE, 12), None, False),          # soviet-hover
        (165, SLATE, None, False),                    # soviet
        (194, lift(SLATE, 12), GREEN_ACCENT, False),  # soviet-highlighted-hover
        (223, SLATE, GREEN_ACCENT, False),            # soviet-highlighted
        (252, lift(SLATE, 12), None, False),          # allies-hover
        (281, SLATE, None, False),                    # allies
        (310, lift(SLATE, 12), SUN_GOLD, False),      # allies-highlighted-hover
        (339, SLATE, SUN_GOLD, False),                # allies-highlighted
        (368, lift(OBS, 12), None, False),            # observer-hover
        (397, OBS, None, False),                      # observer
        (426, lift(OBS, 12), GREEN_ACCENT, False),    # observer-highlighted-hover
        (455, OBS, GREEN_ACCENT, False),              # observer-highlighted
        (484, GRAY, None, True),                      # disabled (shared)
    ]
    for y, fill, accent, disabled in states:
        button_block(im, 260, y, S, fill, accent=accent, disabled=disabled, border=2)

    # radar placeholder emblems: allies/Consortium (290,67) "Citadel Seal",
    # soviet/Assembly (290,290) "Swarm Rig" — distinct marks per faction
    # infrastructure philosophy (docs/BUILDINGS.md), not a recolor of one
    # shared shape
    im.paste(emblem_panel(222, SUN_GOLD, kind="consortium"), (290, 67))
    im.paste(emblem_panel(222, GREEN_ACCENT, kind="assembly"), (290, 290))

    im.save(f"{UIBITS}/sidebar.png")
    print("sidebar.png", im.size)


# --------------------------------------------------------------------------
# loadscreen.png (512x256) + -2x (1024x512) + -3x (2048x1024; 4x scale,
# filename inherited from stock)

def gen_loadscreen():
    for name, scale in (("loadscreen.png", 1), ("loadscreen-2x.png", 2),
                        ("loadscreen-3x.png", 4)):
        W, H = 512 * scale, 256 * scale
        im = Image.new("RGBA", (W, H), PANEL + (255,))
        # stripe (258,0,253,256 at 1x): tileable grid-glass band.
        # 253 = 11*23, so a 23px vertical period tiles seamlessly.
        pv_grid(im, 258 * scale, 0, 253 * scale, 256 * scale,
                base=PANEL, cell=23 * scale if scale > 1 else 23, line=-6, alt=2)
        d = ImageDraw.Draw(im)
        d.line((258 * scale, 4 * scale, W - 1, 4 * scale), fill=GREEN_MID, width=scale)
        d.line((258 * scale, H - 1 - 4 * scale, W - 1, H - 1 - 4 * scale),
               fill=GREEN_MID, width=scale)
        # logo badge (0,0,256,256 at 1x): emblem + wordmark (issue #118)
        im.paste(wordmark_badge(256 * scale, scale), (0, 0))
        im.save(f"{UIBITS}/{name}")
        print(name, im.size)


# --------------------------------------------------------------------------
# content-bg.png (1024x512, of which the top 1024x480 is used): the content
# installer's full-screen tile (issue #119). ModContentLoadScreen tiles the
# (0,0,1024,480) rect of its Image across the window and the
# MODCONTENT_BACKGROUND widget draws the same rect as a centre-tiled panel, so
# this is a seamless grid-glass texture with no mark on it - the installer's
# own dialog (sungrid `dialog`) sits on top. 1024 and 480 are both multiples
# of the 16px cell, so the tile repeats without a seam. The canvas itself is
# 1024x512 because every sheet the engine uploads as a texture must be
# power-of-two in both dimensions (Texture.SetData throws "Non-power-of-two
# array" otherwise - a 1024x480 first draft crashed the installer under Xvfb);
# the stock chrome.png is 1024x1024 for the same reason.

def gen_content_background():
    W, H = 1024, 512
    im = Image.new("RGBA", (W, H), PANEL + (255,))
    pv_grid(im, 0, 0, W, H, base=PANEL, cell=16, line=-6, alt=2)
    im.convert("RGB").save(f"{UIBITS}/content-bg.png")
    print("content-bg.png", im.size)


# --------------------------------------------------------------------------
# mod icons (../icon.png 32, icon-2x.png 64, icon-3x.png 96) — transparent
# background, emblem only

def gen_icons():
    icon_dir = os.path.dirname(UIBITS)
    for name, size in (("icon.png", 32), ("icon-2x.png", 64), ("icon-3x.png", 96)):
        im = emblem(size, SUN_GOLD)
        im.save(f"{icon_dir}/{name}")
        print(name, im.size)


# --------------------------------------------------------------------------
# packaging/artwork (docs/BACKLOG.md issue #114) — the icons the three
# platform packages ship as the *application* icon (Windows launcher .exe /
# installer, macOS .app / .icns, Linux AppImage / .desktop) and the macOS
# disk-image background. Until this pass all of them were still the Mod SDK's
# example-mod placeholders: a black "Ex" glyph, and a DMG background titled
# "OpenRA Example Mod". packaging/*/buildpackage.sh consume these files by
# fixed name and size, so the set below is exactly what those scripts list.
#
# Unlike the in-game icon (emblem on transparency, drawn over the mod
# chooser's own panel) an app icon sits on an arbitrary desktop or Finder
# background, so it carries its own rounded grid-glass tile. Below 48px the
# full mark's ring and filaments would be sub-pixel, so `emblem(simple=True)`
# drops them and thickens the hexagon — the same "draw less, not smaller"
# rule as the sprite pipeline (CLAUDE.md, art rule 10).

ARTWORK = os.path.normpath(os.path.join(UIBITS, "..", "..", "..", "packaging", "artwork"))
APP_ICON_SIZES = (16, 24, 32, 48, 64, 128, 256, 512, 1024)

def app_icon(size):
    s = size * SS
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    tile = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    pv_grid(tile, 0, 0, s, s, base=PANEL, cell=max(8, s // 7), line=-6, alt=2)
    mask = Image.new("L", (s, s), 0)
    r = round(s * 0.18)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, s - 1, s - 1), radius=r, fill=255)
    im.paste(tile, (0, 0), mask)
    d = ImageDraw.Draw(im)
    # frame: one living-green line, lit toward the top-left like every other
    # panel in this file
    lw = max(SS, round(s * 0.012))
    d.rounded_rectangle((lw // 2, lw // 2, s - 1 - lw // 2, s - 1 - lw // 2), radius=r,
                        outline=mix(GREEN_MID, PANEL, 0.25), width=lw)
    d.arc((lw // 2, lw // 2, 2 * r, 2 * r), 180, 270, fill=GREEN_ACCENT, width=lw)
    im = im.resize((size, size), Image.LANCZOS)
    e = emblem(round(size * 0.80), SUN_GOLD, simple=size < 48)
    im.alpha_composite(e, ((size - e.width) // 2, (size - e.height) // 2))
    return im

def gen_app_icons():
    os.makedirs(ARTWORK, exist_ok=True)
    for size in APP_ICON_SIZES:
        im = app_icon(size)
        name = f"icon_{size}x{size}.png"
        im.save(f"{ARTWORK}/{name}")
        print(name, im.size)

def gen_macos_background():
    """600x450 (+2x) Finder window background for the DMG. The two icon
    positions and the 72px icon size are mod.config's
    PACKAGING_OSX_DMG_*_ICON_POSITION / packaging/macos/buildpackage.sh:
    the app at (190,210), the Applications alias at (410,210); Finder
    draws the icons and their names, so the background only carries the
    title, the arrow between the two slots and a hint line."""
    font_path = os.path.join(os.path.dirname(UIBITS), "ZoodRangmah.ttf")
    for name, scale in (("macos-background.png", 1), ("macos-background-2x.png", 2)):
        W, H = 600 * scale, 450 * scale
        im = Image.new("RGBA", (W, H), PANEL + (255,))
        pv_grid(im, 0, 0, W, H, base=PANEL, cell=25 * scale, line=-6, alt=2)
        d = ImageDraw.Draw(im)
        # top/bottom rules, as on the loadscreen stripe
        d.line((0, 6 * scale, W - 1, 6 * scale), fill=GREEN_MID, width=scale)
        d.line((0, H - 1 - 6 * scale, W - 1, H - 1 - 6 * scale), fill=GREEN_MID, width=scale)

        badge = emblem(56 * scale, SUN_GOLD)
        title = ImageFont.truetype(font_path, 40 * scale)
        tw = round(d.textlength("Sungrid Protocol", font=title))
        gap = 14 * scale
        x0 = (W - (badge.width + gap + tw)) // 2
        ty = 70 * scale
        im.alpha_composite(badge, (x0, ty - badge.height // 2))
        d.text((x0 + badge.width + gap, ty), "Sungrid Protocol", font=title,
               fill=SUN_GOLD, anchor="lm")

        # arrow from the app slot to the Applications slot (72px icons,
        # centres 220px apart) — a sun-gold filament, nodes at both ends
        ax0, ax1, ay = 240 * scale, 360 * scale, 210 * scale
        lw = 3 * scale
        d.line((ax0, ay, ax1, ay), fill=GOLD_DIM, width=lw)
        d.polygon([(ax1 + 10 * scale, ay), (ax1 - 8 * scale, ay - 11 * scale),
                   (ax1 - 8 * scale, ay + 11 * scale)], fill=SUN_GOLD)
        nr = 4 * scale
        d.ellipse((ax0 - nr, ay - nr, ax0 + nr, ay + nr), fill=SUN_GOLD)

        hint = ImageFont.truetype(font_path, 20 * scale)
        d.text((W // 2, 330 * scale), "Drag Sungrid Protocol into Applications to install",
               font=hint, fill=GREEN_ACCENT, anchor="mm")
        im.save(f"{ARTWORK}/{name}")
        print(name, im.size)


if __name__ == "__main__":
    gen_dialog()
    gen_sidebar()
    gen_loadscreen()
    gen_content_background()
    gen_icons()
    gen_flags()
    gen_app_icons()
    gen_macos_background()
