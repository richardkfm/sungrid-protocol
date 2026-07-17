#!/usr/bin/env python3
"""First-pass custom cursor art (docs/BACKLOG.md issue #13/#33 follow-up;
see docs/ART_DIRECTION.md), replacing the stock RA mouse.shp/nopower.shp/
attackmove.shp sprite sheets outright. Issue #33 only palette-tinted the
stock cursor pixels (with a hue exclusion so blocked/attack/danger cursors
kept their semantic red) -- every pixel in those three files was still
derived from stock RA art. This generates genuinely new pointer shapes in
the locked "grid-glass" visual language gen_chrome.py established for the
rest of Phase 6's UI chrome (green/gold geometric glyphs, no stock pixels),
one shape per cursor semantic (scroll arrow, targeting reticle, wrench,
deploy chevron, dollar token, etc.), with the same "programmatic first pass
now, real artist pass later" caveat every other art pass in this backlog
carries.

Ground rules:
  - PngSheet format, truecolor RGBA (mod.yaml already lists PngSheet in
    SpriteFormats). Cursors don't need palette indexing/team-color remap --
    OpenRA.Game/Graphics/CursorManager.cs only resolves a cursor's `Palette`
    when the source frame type is Indexed8; a truecolor Bgra32 frame is used
    directly. So these ship as plain RGBA PngSheets with no Palette needed,
    same technique as the building sprites but without the indexed-on-
    temperat.pal step issue #43 added there.
  - Frame metadata is written as PNG tEXt chunks (FrameSize/FrameAmount),
    the same convention gen_concept_art.py/gen_chrome.py already use.
  - PngSheetLoader.TryParseSprite sniffs file content (PNG magic bytes), not
    the filename extension, so a PNG can be written directly to a file
    literally named mouse.shp/nopower.shp/attackmove.shp -- cursors.yaml's
    `mouse.shp: cursor` references need no changes, and no engine-build SHP
    round-trip is required (unlike issue #17/#33's terrain/cursor-palette
    work, which predates this and had no choice but to go through the real
    Westwood .shp format since it was only ever recoloring, not replacing).
  - Every cursor name's exact (Start, Length) from mods/sungrid/cursors.yaml
    is preserved -- this script draws one PNG per source file with the same
    total frame count (222 / 4 / 20) in the same order, so cursors.yaml
    itself needs zero changes.
  - Frame canvas sizes match the stock sheets exactly (mouse.shp/
    attackmove.shp 30x24, nopower.shp 24x24), decoded via
    `Mod=sungrid ./utility.sh --png mouse.shp temperat.pal` against the real
    engine and confirmed with PIL.

Usage:
    pip install pillow
    python3 gen_cursor_art.py
Writes mouse.shp, nopower.shp, attackmove.shp directly into this directory
(mods/sungrid/bits/), overwriting the stock Westwood-format binaries.
"""
import math
import os
from PIL import Image, ImageDraw, ImageChops, ImageFilter, PngImagePlugin

HERE = os.path.dirname(os.path.abspath(__file__))

# Locked palette (docs/ART_DIRECTION.md), matching gen_chrome.py/gen_concept_art.py.
GREEN_PRIMARY = (0x2E, 0x7D, 0x46)
GREEN_ACCENT = (0x8B, 0xC3, 0x4A)
GREEN_DIM = (0x1B, 0x4A, 0x2A)
PANEL_BLUEBLACK = (0x16, 0x23, 0x2E)
SUN_GOLD = (0xE8, 0xA9, 0x3D)
GOLD_DIM = (0xA8, 0x79, 0x2C)
RED_DANGER = (0xC7, 0x3B, 0x2E)
WHITE = (0xF2, 0xF4, 0xE8)
OUTLINE_DARK = (0x0A, 0x0D, 0x0A)

SS = 4  # supersample factor


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def lit(c, f=0.35):
    return tuple(min(255, int(v + (255 - v) * f)) for v in c[:3])


class SD:
    """ImageDraw wrapper scaling native-pixel coordinates by SS."""

    def __init__(self, img):
        self.d = ImageDraw.Draw(img, "RGBA")

    @staticmethod
    def _xy(xy):
        out = []
        for p in xy:
            if isinstance(p, (tuple, list)):
                out.append((p[0] * SS, p[1] * SS))
            else:
                out.append(p * SS)
        return out

    def rect(self, xy, fill=None, outline=None, width=1):
        self.d.rectangle(self._xy(xy), fill=fill, outline=outline, width=max(1, round(width * SS)))

    def ellipse(self, xy, fill=None, outline=None, width=1):
        self.d.ellipse(self._xy(xy), fill=fill, outline=outline, width=max(1, round(width * SS)))

    def line(self, xy, fill=None, width=1):
        self.d.line(self._xy(xy), fill=fill, width=max(1, round(width * SS)))

    def poly(self, xy, fill=None, outline=None):
        self.d.polygon(self._xy(xy), fill=fill, outline=outline)

    def arc(self, xy, start, end, fill=None, width=1):
        self.d.arc(self._xy(xy), start, end, fill=fill, width=max(1, round(width * SS)))


def canvas(w, h):
    return Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))


def render(draw_fn, w, h, *args, **kwargs):
    img = canvas(w, h)
    draw_fn(SD(img), w, h, *args, **kwargs)
    return img.resize((w, h), Image.LANCZOS)


def outline_sprite(img, color=OUTLINE_DARK):
    """1px dark readability outline -- essential for cursors, which render
    over every possible terrain colour (green/tan/snow/water)."""
    a = img.getchannel("A")
    solid = a.point(lambda v: 255 if v > 40 else 0)
    grown = solid.filter(ImageFilter.MaxFilter(3))
    edge = ImageChops.subtract(grown, solid)
    edge = edge.point(lambda v: min(v, 220))
    ol = Image.new("RGBA", img.size, color + (0,))
    ol.putalpha(edge)
    return Image.alpha_composite(ol, img)


def rotate(img, w, h, angle, resample=Image.BICUBIC):
    big = img.resize((w * SS, h * SS), Image.LANCZOS)
    big = big.rotate(angle, resample=resample, center=(w * SS / 2, h * SS / 2))
    return big.resize((w, h), Image.LANCZOS)


# ---------------------------------------------------------------------------
# Shared glyph primitives
# ---------------------------------------------------------------------------

def _chevron(sd, cx, cy, size, color, width=2.2):
    """An upward chevron (^), the base shape for scroll/move/attackmove arrows."""
    sd.line([(cx - size, cy + size * 0.5), (cx, cy - size * 0.6), (cx + size, cy + size * 0.5)],
            fill=color, width=width)


def draw_pointer(sd, w, h, small=False):
    cx, cy = (w / 2, h / 2) if small else (w / 2 - 3, h / 2 - 4)
    s = 6 if small else 9
    tip = (cx - s * 0.35, cy - s * 0.75)
    tail_l = (cx - s * 0.35, cy + s * 0.55)
    tail_r = (cx + s * 0.15, cy + s * 0.15)
    barb = (cx + s * 0.45, cy + s * 0.35)
    sd.poly([tip, tail_l, tail_r, barb], fill=GREEN_ACCENT, outline=None)
    sd.line([tip, tail_l], fill=lit(GREEN_ACCENT), width=1)
    sd.ellipse([cx - 1, cy - s * 0.75 - 1, cx + 1, cy - s * 0.75 + 1], fill=SUN_GOLD)


def draw_blocked_badge(sd, w, h, small=False):
    cx, cy = w / 2, h / 2
    r = (h / 2 - 3) if not small else (h / 2 - 5)
    sd.ellipse([cx - r, cy - r, cx + r, cy + r], outline=RED_DANGER, width=2.2)
    d = r * 0.72
    sd.line([(cx - d, cy - d), (cx + d, cy + d)], fill=RED_DANGER, width=2.2)


def _blocked_overlay(img, w, h):
    """Composite a small red slash badge onto an existing frame (used for the
    per-direction *-blocked cursors, which reuse their unblocked shape)."""
    ov = render(draw_blocked_badge, w, h, small=True)
    return Image.alpha_composite(img, ov)


def scroll_arrow(direction_deg, blocked=False):
    def _draw(sd, w, h):
        cx, cy = w / 2, h / 2
        _chevron(sd, cx, cy, 6, GREEN_ACCENT if not blocked else RED_DANGER, width=2.6)
        sd.line([(cx, cy - 3.5), (cx, cy + 2)], fill=SUN_GOLD if not blocked else RED_DANGER, width=1.4)
    base = render(_draw, 30, 24)
    base = rotate(base, 30, 24, -direction_deg)
    return outline_sprite(base)


def blocked_icon(small=False):
    return outline_sprite(render(draw_blocked_badge, 30, 24, small=small))


def select_frames(n=6):
    frames = []
    for i in range(n):
        t = i / max(1, n - 1)
        inset = 2 + t * 3

        def _draw(sd, w, h, inset=inset):
            cx, cy = w / 2, h / 2
            half = 8 - inset * 0.3
            arm = 3.5
            corners = [(cx - half, cy - half), (cx + half, cy - half),
                       (cx + half, cy + half), (cx - half, cy + half)]
            for (x, y) in corners:
                dx = arm if x < cx else -arm
                dy = arm if y < cy else -arm
                sd.line([(x, y), (x + dx, y)], fill=GREEN_ACCENT, width=2)
                sd.line([(x, y), (x, y + dy)], fill=GREEN_ACCENT, width=2)
        frames.append(outline_sprite(render(_draw, 30, 24)))
    return frames


def move_reticle_frames(n=4, small=False):
    frames = []
    for i in range(n):
        t = i / max(1, n - 1)
        r = (5 if not small else 3.5) + t * (2.5 if not small else 1.5)

        def _draw(sd, w, h, r=r):
            cx, cy = w / 2, h / 2
            sd.ellipse([cx - r, cy - r, cx + r, cy + r], outline=GREEN_ACCENT, width=1.6)
            for ang in (0, 90, 180, 270):
                rad = math.radians(ang)
                x, y = cx + math.cos(rad) * r, cy + math.sin(rad) * r
                sd.ellipse([x - 1, y - 1, x + 1, y + 1], fill=SUN_GOLD)
        frames.append(outline_sprite(render(_draw, 30, 24)))
    return frames


def target_reticle_frames(n=8, small=False):
    frames = []
    base_r = 6 if not small else 4
    for i in range(n):
        t = i / n
        pulse = 0.85 + 0.3 * abs(math.sin(t * math.pi))
        r = base_r * pulse

        def _draw(sd, w, h, r=r):
            cx, cy = w / 2, h / 2
            sd.ellipse([cx - r, cy - r, cx + r, cy + r], outline=RED_DANGER, width=1.8)
            sd.line([(cx - r - 2, cy), (cx - r + 2, cy)], fill=SUN_GOLD, width=1.4)
            sd.line([(cx + r - 2, cy), (cx + r + 2, cy)], fill=SUN_GOLD, width=1.4)
            sd.line([(cx, cy - r - 2), (cx, cy - r + 2)], fill=SUN_GOLD, width=1.4)
            sd.line([(cx, cy + r - 2), (cx, cy + r + 2)], fill=SUN_GOLD, width=1.4)
            sd.ellipse([cx - 1, cy - 1, cx + 1, cy + 1], fill=WHITE)
        frames.append(outline_sprite(render(_draw, 30, 24)))
    return frames


def enter_frames(n=3):
    frames = []
    for i in range(n):
        t = i / max(1, n - 1)

        def _draw(sd, w, h, t=t):
            cx, cy = w / 2, h / 2
            sd.poly([(cx - 6, cy - 5), (cx - 6, cy + 5), (cx - 2, cy)],
                    outline=GREEN_ACCENT, fill=None)
            ax = cx - 4 + t * 5
            sd.line([(ax - 3, cy), (ax + 3, cy)], fill=SUN_GOLD, width=1.8)
            sd.line([(ax + 1, cy - 2), (ax + 3, cy), (ax + 1, cy + 2)], fill=SUN_GOLD, width=1.6)
        frames.append(outline_sprite(render(_draw, 30, 24)))
    return frames


def c4_frames(n=3, small=False):
    frames = []
    s = 5 if not small else 3.5
    for i in range(n):
        t = i / max(1, n - 1)
        glow = 0.4 + 0.6 * t

        def _draw(sd, w, h, glow=glow):
            cx, cy = w / 2, h / 2
            pts = []
            for k in range(6):
                a = math.radians(60 * k - 90)
                pts.append((cx + math.cos(a) * s, cy + math.sin(a) * s))
            sd.poly(pts, fill=PANEL_BLUEBLACK, outline=SUN_GOLD)
            sd.ellipse([cx - 1.5 * glow, cy - 1.5 * glow, cx + 1.5 * glow, cy + 1.5 * glow],
                       fill=mix(RED_DANGER, SUN_GOLD, 0.5))
        frames.append(outline_sprite(render(_draw, 30, 24)))
    return frames


def shield_icon(small=False):
    def _draw(sd, w, h):
        cx, cy = w / 2, h / 2
        s = 6 if not small else 4
        sd.poly([(cx, cy - s), (cx + s * 0.8, cy - s * 0.4), (cx + s * 0.8, cy + s * 0.3),
                  (cx, cy + s), (cx - s * 0.8, cy + s * 0.3), (cx - s * 0.8, cy - s * 0.4)],
                fill=GREEN_DIM, outline=GREEN_ACCENT)
        sd.line([(cx, cy - s * 0.5), (cx, cy + s * 0.5)], fill=SUN_GOLD, width=1.4)
    return outline_sprite(render(_draw, 30, 24))


def capture_frames(n=3, small=False):
    frames = []
    s = 6 if not small else 4
    for i in range(n):
        t = i / max(1, n - 1)

        def _draw(sd, w, h, t=t):
            cx, cy = w / 2, h / 2
            sd.line([(cx - s * 0.5, cy + s), (cx - s * 0.5, cy - s)], fill=GREEN_ACCENT, width=1.4)
            lean = t * 2
            sd.poly([(cx - s * 0.5, cy - s), (cx + s * 0.6 + lean, cy - s * 0.6),
                      (cx - s * 0.5, cy - s * 0.2)], fill=SUN_GOLD)
        frames.append(outline_sprite(render(_draw, 30, 24)))
    return frames


def heal_frames(n=4, small=False):
    frames = []
    s = 5 if not small else 3.5
    for i in range(n):
        t = i / max(1, n - 1)
        arm = s * (0.7 + 0.3 * abs(math.sin(t * math.pi)))

        def _draw(sd, w, h, arm=arm):
            cx, cy = w / 2, h / 2
            sd.line([(cx - arm, cy), (cx + arm, cy)], fill=GREEN_ACCENT, width=2.4)
            sd.line([(cx, cy - arm), (cx, cy + arm)], fill=GREEN_ACCENT, width=2.4)
            sd.ellipse([cx - 1.2, cy - 1.2, cx + 1.2, cy + 1.2], fill=SUN_GOLD)
        frames.append(outline_sprite(render(_draw, 30, 24)))
    return frames


def ability_frames(n=8, small=False):
    frames = []
    s = 6 if not small else 4
    for i in range(n):
        ang = i * (360.0 / n)

        def _draw(sd, w, h, ang=ang):
            cx, cy = w / 2, h / 2
            for k in range(3):
                a = math.radians(ang + k * 120)
                x1, y1 = cx + math.cos(a) * s * 0.3, cy + math.sin(a) * s * 0.3
                x2, y2 = cx + math.cos(a) * s, cy + math.sin(a) * s
                sd.line([(x1, y1), (x2, y2)], fill=SUN_GOLD, width=1.8)
            sd.ellipse([cx - 1.4, cy - 1.4, cx + 1.4, cy + 1.4], fill=GREEN_ACCENT)
        frames.append(outline_sprite(render(_draw, 30, 24)))
    return frames


def deploy_frames(n=9):
    frames = []
    for i in range(n):
        t = i / max(1, n - 1)
        r = 2 + t * 6

        def _draw(sd, w, h, r=r, t=t):
            cx, cy = w / 2, h / 2
            sd.line([(cx, cy - 7), (cx, cy - 1)], fill=GREEN_ACCENT, width=2)
            sd.line([(cx - 2.5, cy - 3.5), (cx, cy - 1), (cx + 2.5, cy - 3.5)], fill=GREEN_ACCENT, width=1.8)
            sd.ellipse([cx - r, cy + 2 - r * 0.3, cx + r, cy + 2 + r * 0.3],
                       outline=mix(SUN_GOLD, GREEN_ACCENT, t), width=1.4)
        frames.append(outline_sprite(render(_draw, 30, 24)))
    return frames


def wrench_frames(n=24, color=SUN_GOLD):
    def _draw(sd, w, h):
        cx, cy = w / 2, h / 2
        # Thick shaft.
        sd.line([(cx - 5, cy + 5), (cx + 3, cy - 3)], fill=color, width=3.4)
        # Open-jaw ring at the top end (a horseshoe with a visible gap facing
        # away from the shaft) -- reads as a wrench head, not a lollipop.
        hx, hy = cx + 4, cy - 4
        sd.arc([hx - 3.6, hy - 3.6, hx + 3.6, hy + 3.6], 25, 335, fill=color, width=3.2)
        # Hex bolt-head at the other end.
        tx, ty = cx - 5, cy + 5
        r = 2.8
        pts = [(tx + r * math.cos(math.radians(a)), ty + r * math.sin(math.radians(a))) for a in range(0, 360, 60)]
        sd.poly(pts, fill=color)
    base = render(_draw, 30, 24)
    frames = []
    for i in range(n):
        angle = i * (360.0 / n)
        frames.append(outline_sprite(rotate(base, 30, 24, angle)))
    return frames


def nuke_frames(n=7):
    frames = []
    for i in range(n):
        t = i / max(1, n - 1)
        r = 3 + t * 5

        def _draw(sd, w, h, r=r, t=t):
            cx, cy = w / 2, h / 2
            col = mix(SUN_GOLD, RED_DANGER, t)
            tri = [(cx, cy - 7), (cx - 6, cy + 5), (cx + 6, cy + 5)]
            sd.line([tri[0], tri[1]], fill=col, width=2)
            sd.line([tri[1], tri[2]], fill=col, width=2)
            sd.line([tri[2], tri[0]], fill=col, width=2)
            sd.ellipse([cx - r * 0.3, cy - 1, cx + r * 0.3, cy + 1], fill=RED_DANGER)
            sd.ellipse([cx - r, cy - 3 - r * 0.2, cx + r, cy - 3 + r * 0.2], outline=RED_DANGER, width=1.2)
        frames.append(outline_sprite(render(_draw, 30, 24)))
    return frames


def chrono_frames(n=8, variant=0):
    frames = []
    for i in range(n):
        ang = i * (360.0 / n) * (1 if variant == 0 else -1)

        def _draw(sd, w, h, ang=ang):
            cx, cy = w / 2, h / 2
            sd.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], outline=GREEN_ACCENT, width=1.4)
            a = math.radians(ang - 90)
            sd.line([(cx, cy), (cx + math.cos(a) * 5, cy + math.sin(a) * 5)], fill=SUN_GOLD, width=1.6)
            a2 = math.radians(ang * 1.6 - 90)
            sd.line([(cx, cy), (cx + math.cos(a2) * 3, cy + math.sin(a2) * 3)], fill=SUN_GOLD, width=1.6)
        frames.append(outline_sprite(render(_draw, 30, 24)))
    return frames


def sell_frames(n=12, accent=SUN_GOLD):
    frames = []
    for i in range(n):
        t = i / n
        squash = abs(math.cos(t * math.pi))

        def _draw(sd, w, h, squash=squash):
            cx, cy = w / 2, h / 2
            rx = 6 * max(0.25, squash)
            sd.ellipse([cx - rx, cy - 6, cx + rx, cy + 6], fill=PANEL_BLUEBLACK, outline=accent, width=1.6)
            if squash > 0.3:
                sd.line([(cx, cy - 3.5), (cx, cy + 3.5)], fill=accent, width=1.6)
                sd.line([(cx - 2, cy - 2), (cx + 2, cy - 2)], fill=accent, width=1.2)
                sd.line([(cx - 2, cy + 2), (cx + 2, cy + 2)], fill=accent, width=1.2)
        frames.append(outline_sprite(render(_draw, 30, 24)))
    return frames


def lightning_icon(w, h, blocked=False, pulse=0.5):
    def _draw(sd, w, h):
        cx, cy = w / 2, h / 2
        color = RED_DANGER if blocked else mix(GREEN_ACCENT, SUN_GOLD, pulse)
        sd.poly([(cx + 1, cy - 7), (cx - 3, cy + 1), (cx, cy + 1),
                  (cx - 1, cy + 7), (cx + 4, cy - 1), (cx + 1, cy - 1)], fill=color)
    frame = render(_draw, w, h)
    if blocked:
        frame = _blocked_overlay(frame, w, h)
    return outline_sprite(frame)


def attackmove_icon(blocked=False, pulse=0.5, assault=False):
    def _draw(sd, w, h):
        cx, cy = w / 2, h / 2
        color = RED_DANGER if blocked else GREEN_ACCENT
        r = 4 + pulse * 2
        sd.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=1.6)
        if assault:
            _chevron(sd, cx, cy - 8, 3, SUN_GOLD if not blocked else RED_DANGER, width=1.8)
            _chevron(sd, cx, cy - 5, 3, SUN_GOLD if not blocked else RED_DANGER, width=1.8)
        else:
            sd.line([(cx - r - 2, cy), (cx + r + 2, cy)], fill=SUN_GOLD if not blocked else RED_DANGER, width=1.2)
            sd.line([(cx, cy - r - 2), (cx, cy + r + 2)], fill=SUN_GOLD if not blocked else RED_DANGER, width=1.2)
    frame = render(_draw, 30, 24)
    if blocked:
        frame = _blocked_overlay(frame, 30, 24)
    return outline_sprite(frame)


# ---------------------------------------------------------------------------
# Sheet assembly. Every (Start, Length) below is copied verbatim from
# mods/sungrid/cursors.yaml so this stays byte-compatible with it; frames
# not covered by any block are filled with a faint neutral dot (never
# referenced by name, but the sheet must stay contiguous).
# ---------------------------------------------------------------------------

def build_mouse_sheet():
    w, h = 30, 24
    frames = [None] * 222

    def put(start, fs):
        for i, f in enumerate(fs):
            frames[start + i] = f

    put(0, [outline_sprite(render(draw_pointer, w, h))])          # default / joystick-all
    dirs = {1: 0, 2: 45, 3: 90, 4: 135, 5: 180, 6: 225, 7: 270, 8: 315}
    for start, deg in dirs.items():
        put(start, [scroll_arrow(deg)])
    put(9, [blocked_icon()])                                       # generic-blocked
    put(10, move_reticle_frames(4))                                 # move / move-rough
    put(14, [blocked_icon()])                                       # move-blocked
    put(15, select_frames(6))                                       # select
    put(21, target_reticle_frames(8))                               # attackoutsiderange / harvest
    put(29, move_reticle_frames(4, small=True))                     # move-minimap
    put(33, [blocked_icon(small=True)])                             # *-blocked-minimap (shared)
    put(35, wrench_frames(24, color=GREEN_ACCENT))                  # repair
    put(59, deploy_frames(9))                                       # deploy
    put(68, sell_frames(12, accent=SUN_GOLD))                       # sell
    put(80, [outline_sprite(render(draw_pointer, w, h, small=True))])  # default-minimap
    put(82, ability_frames(8))                                      # ability
    put(90, nuke_frames(7))                                         # nuke
    put(97, chrono_frames(8, variant=0))                            # chrono-select
    put(105, chrono_frames(8, variant=1))                           # chrono-target
    put(113, enter_frames(3))                                       # enter
    put(116, c4_frames(3))                                          # c4
    put(119, [blocked_icon()])                                      # sell-blocked
    put(120, [blocked_icon()])                                      # repair-blocked
    put(121, c4_frames(3, small=True))                              # c4-minimap
    blocked_dirs = {124: 0, 125: 45, 126: 90, 127: 135, 128: 180, 129: 225, 130: 270, 131: 315}
    for start, deg in blocked_dirs.items():
        put(start, [scroll_arrow(deg, blocked=True)])
    put(134, target_reticle_frames(8, small=True))                  # attackoutsiderange/harvest/enter-minimap
    put(146, [shield_icon(small=True)])                             # guard-minimap
    put(147, [shield_icon()])                                       # guard
    put(148, sell_frames(12, accent=GREEN_ACCENT))                  # sell2
    put(160, heal_frames(4))                                        # heal
    put(164, capture_frames(3))                                     # capture
    put(167, capture_frames(3, small=True))                         # capture-minimap
    put(170, wrench_frames(24, color=SUN_GOLD))                     # goldwrench
    put(194, heal_frames(1, small=True))                            # heal-minimap
    put(195, target_reticle_frames(8))                              # attack
    put(203, target_reticle_frames(8, small=True))                  # attack-minimap
    put(211, [blocked_icon()])                                      # deploy-blocked
    put(212, [blocked_icon()])                                      # enter-blocked
    put(213, [blocked_icon()])                                      # goldwrench-blocked
    put(214, ability_frames(8, small=True))                         # ability-minimap

    for i in range(len(frames)):
        if frames[i] is None:
            frames[i] = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    return frames, w, h


def build_nopower_sheet():
    w, h = 24, 24
    return [
        lightning_icon(w, h, blocked=True),
        lightning_icon(w, h, blocked=False, pulse=0.15),
        lightning_icon(w, h, blocked=False, pulse=0.55),
        lightning_icon(w, h, blocked=False, pulse=0.95),
    ], w, h


def build_attackmove_sheet():
    w, h = 30, 24
    frames = [None] * 20

    def put(start, fs):
        for i, f in enumerate(fs):
            frames[start + i] = f

    put(0, [attackmove_icon(pulse=p) for p in (0.1, 0.4, 0.7, 1.0)])
    put(4, [attackmove_icon(pulse=p) for p in (0.1, 0.4, 0.7, 1.0)])
    put(8, [attackmove_icon(pulse=p, assault=True) for p in (0.1, 0.4, 0.7, 1.0)])
    put(12, [attackmove_icon(pulse=p, assault=True) for p in (0.1, 0.4, 0.7, 1.0)])
    put(16, [attackmove_icon(blocked=True)])
    put(17, [attackmove_icon(blocked=True, assault=True)])
    put(18, [attackmove_icon(blocked=True)])
    put(19, [attackmove_icon(blocked=True, assault=True)])

    for i in range(len(frames)):
        if frames[i] is None:
            frames[i] = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    return frames, w, h


def save_pngsheet(frames, w, h, name):
    sheet = Image.new("RGBA", (w * len(frames), h), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        sheet.paste(f, (i * w, 0), f)
    meta = PngImagePlugin.PngInfo()
    meta.add_text("FrameSize", f"{w},{h}")
    meta.add_text("FrameAmount", str(len(frames)))
    path = os.path.join(HERE, name)
    sheet.save(path, format="PNG", pnginfo=meta)
    print(f"wrote {name}  frame={w}x{h} x{len(frames)}")


if __name__ == "__main__":
    frames, w, h = build_mouse_sheet()
    save_pngsheet(frames, w, h, "mouse.shp")

    frames, w, h = build_nopower_sheet()
    save_pngsheet(frames, w, h, "nopower.shp")

    frames, w, h = build_attackmove_sheet()
    save_pngsheet(frames, w, h, "attackmove.shp")
