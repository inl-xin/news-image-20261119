#!/usr/bin/env python3
"""Draw the make.fun news-image-20261119 entry (1024x1024) with PIL.

Style: GTA-game-poster flat painting -- high-saturation neon pink /
orange / cyan, thick black outlines, blocky pixel-art figures,
buildings and vehicles, layered shadows and highlights. Original
artwork only: no GTA official art, characters, logos or screenshots.
Text stays crisp vector type (never pixelated).
Content: only verified 19 Nov 2026 stories from NEWS_BRIEF_2026-11-19.md.
Deterministic: fixed fonts, fixed geometry, no randomness, no network.
Run:  python3 draw.py [output_path]   (default: entry.png next to this file)
main.py (stdlib-only) just copies entry.png to the output dir.
"""
import math
import os
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
DJ = "/usr/share/fonts/truetype/dejavu/"
SERIF_B = DJ + "DejaVuSerif-Bold.ttf"
SANS_B = DJ + "DejaVuSans-Bold.ttf"
SANS = DJ + "DejaVuSans.ttf"

PAPER = "#FFF8E7"
INK = "#111111"
NAVY = "#14264E"
NAVY2 = "#1E3A6E"
RED = "#E63946"
RED2 = "#D62828"
YELLOW = "#FFD23F"
ORANGE = "#F77F00"
TEAL = "#2A9D8F"
SKY = "#8ECAE6"
BLUE = "#4361EE"
# GTA neon palette
NEON_PINK = "#FF2E88"
NEON_ORANGE = "#FF6B1A"
NEON_CYAN = "#00E5FF"
NEON_YELLOW = "#FFE600"
NEON_PURPLE = "#7B2FF7"
NEON_GREEN = "#39FF6A"
HOT_PINK = "#FF7BAC"
SUNSET = "#FF9E7D"


def F(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, font, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, xy, lines, font, fill, leading=None):
    x, y = xy
    leading = leading or int(font.size * 1.18)
    for ln in lines:
        draw.text((x, y), ln, font=font, fill=fill)
        y += leading
    return y


def pix(d, x, y, s, col, outline=None):
    """One pixel-art block: a filled square, optionally outlined."""
    d.rectangle([x, y, x + s, y + s], fill=col,
                outline=outline, width=1 if outline else 0)


def pix_rect(d, x, y, w, h, col, outline=INK, width=2):
    d.rectangle([x, y, x + w, y + h], fill=col, outline=outline, width=width)


def neon_sky(d, x, y, w, h):
    """GTA sunset: hot pink -> orange -> purple horizontal bands,
    with a pale cyan strip at the horizon."""
    bands = [NEON_PINK, "#FF5E3A", NEON_ORANGE, "#FF9E2E", NEON_PURPLE]
    for i, col in enumerate(bands):
        d.rectangle([x, y + i * h // 5, x + w, y + (i + 1) * h // 5],
                    fill=col)
    d.rectangle([x, y + 4 * h // 5, x + w, y + h], fill=NEON_CYAN)


def pix_person(d, cx, base_y, skin, hair, suit, tie, scale=1):
    """Blocky pixel person: square head, hair cap, suit, tie, shoulders.
    base_y is the bottom of the shoulders. All rectangles, no curves."""
    s = scale
    hw = 9 * s
    # shoulders / suit
    pix_rect(d, cx - 13 * s, base_y - 14 * s, 26 * s, 14 * s, suit)
    pix_rect(d, cx - 13 * s, base_y - 14 * s, 26 * s, 3 * s, suit)
    # shirt V + tie
    d.polygon([(cx - 5 * s, base_y - 14 * s), (cx + 5 * s, base_y - 14 * s),
               (cx, base_y - 4 * s)], fill="#FFFFFF", outline=INK, width=1)
    d.polygon([(cx - 2 * s, base_y - 13 * s), (cx + 2 * s, base_y - 13 * s),
               (cx + 3 * s, base_y - 6 * s), (cx, base_y - 3 * s),
               (cx - 3 * s, base_y - 6 * s)], fill=tie, outline=INK, width=1)
    # head
    pix_rect(d, cx - hw, base_y - 30 * s, 2 * hw, 16 * s, skin)
    # hair cap + sideburns
    pix_rect(d, cx - hw, base_y - 32 * s, 2 * hw, 5 * s, hair)
    pix_rect(d, cx - hw, base_y - 28 * s, 3 * s, 8 * s, hair)
    pix_rect(d, cx + hw - 3 * s, base_y - 28 * s, 3 * s, 8 * s, hair)
    # eyes (2px blocks), mouth
    pix(d, cx - 5 * s, base_y - 22 * s, 2 * s, INK)
    pix(d, cx + 3 * s, base_y - 22 * s, 2 * s, INK)
    d.line([cx - 3 * s, base_y - 17 * s, cx + 3 * s, base_y - 17 * s],
           fill=INK, width=1)


def pix_palm(d, x, base_y, h, col="#0E5C2E"):
    """Pixel palm: stepped trunk + 5 blocky fronds."""
    d.line([x, base_y - h, x, base_y], fill=col, width=4)
    for dx, dy, ln in [(-14, -6, 14), (14, -6, 14), (-11, 2, 11),
                       (11, 2, 11), (0, -10, 10)]:
        d.line([x, base_y - h, x + dx, base_y - h + dy], fill=col, width=3)
        d.line([x + dx, base_y - h + dy, x + dx + (4 if dx > 0 else -4),
                base_y - h + dy + 4], fill=col, width=2)


def pix_car(d, x, y, w, h, body, neon=NEON_CYAN):
    """Low pixel sports car: body, cabin, wheels, neon underglow."""
    d.ellipse([x - 4, y + h - 6, x + w + 4, y + h + 2], fill=neon)
    pix_rect(d, x, y + h // 2, w, h // 2, body)
    d.polygon([(x + w // 5, y + h // 2), (x + w // 3, y + 2),
               (x + 2 * w // 3, y + 2), (x + 4 * w // 5, y + h // 2)],
              fill="#0E2A4A", outline=INK, width=2)
    d.line([x + w // 2 - 2, y + 2, x + w // 2 - 2, y + h // 2], fill=INK,
           width=2)
    # window glint
    d.polygon([(x + w // 3 + 2, y + 4), (x + w // 3 + 10, y + 4),
               (x + w // 3 + 6, y + h // 2 - 2)], fill="#BFEFFF")
    for wx in (x + w // 5, x + 4 * w // 5):
        d.ellipse([wx - 8, y + h - 10, wx + 8, y + h + 6], fill=INK,
                  outline=INK, width=2)
        d.ellipse([wx - 4, y + h - 5, wx + 4, y + h + 1], fill="#E8E8E8",
                  outline=INK, width=1)
    d.ellipse([x + w - 6, y + h // 2 + 2, x + w - 1, y + h // 2 + 7],
              fill=NEON_YELLOW, outline=INK, width=1)


def smoke_plume(d, x, y, w, h, base_y, lean=-1):
    """Flat smoke column: layered grey-blue ribbons + puffs, never balls."""
    top_y = y + 4
    pts_out, pts_in = [], []
    steps = 6
    for i in range(steps + 1):
        t = i / steps
        yy = base_y - (base_y - top_y) * t
        cx = x + lean * (10 * t + 4 * math.sin(t * math.pi))
        pts_out.append((cx - 9, yy))
        pts_in.append((cx - 4, yy))
    for i in range(steps, -1, -1):
        t = i / steps
        yy = base_y - (base_y - top_y) * t
        cx = x + lean * (10 * t + 4 * math.sin(t * math.pi))
        pts_out.append((cx + 9, yy))
    for i in range(steps, -1, -1):
        t = i / steps
        yy = base_y - (base_y - top_y) * t
        cx = x + lean * (10 * t + 4 * math.sin(t * math.pi))
        pts_in.append((cx + 4, yy))
    d.polygon(pts_out, fill="#7A8AA0", outline="#4A5A6E", width=1)
    d.polygon(pts_in, fill="#AAB6C4")
    px, py = x + lean * 14, top_y + 6
    d.ellipse([px - 12, py - 8, px + 12, py + 8], fill="#7A8AA0",
              outline="#4A5A6E", width=1)
    d.ellipse([px - 8, py - 11, px + 10, py + 4], fill="#AAB6C4")
    d.ellipse([px - 5, py - 9, px + 5, py + 1], fill="#D3DAE2")
    mx, my = x - lean * 2, base_y - (base_y - top_y) * 0.45
    d.ellipse([mx - 9, my - 6, mx + 9, my + 6], fill="#8F9AA8")
    d.ellipse([mx - 5, my - 8, mx + 6, my + 2], fill="#C2CAD4")


def draw_gavel(d, cx, cy, angle_deg=35):
    """A real gavel: cylindrical head perpendicular to its handle."""
    a = math.radians(angle_deg)
    hx, hy = -math.cos(a), math.sin(a)
    px, py = math.sin(a), math.cos(a)
    x0, y0 = cx + hx * 6, cy + hy * 6
    x1, y1 = cx + hx * 52, cy + hy * 52
    d.line([(x0, y0), (x1, y1)], fill="#8A5A2B", width=8)
    d.line([(x0, y0), (x1, y1)], fill="#B07A3A", width=4)
    hl, hw = 30, 11
    corners = []
    for s1, s2 in [(1, 1), (-1, 1), (-1, -1), (1, -1)]:
        corners.append((cx + px * hl * s1 + hx * hw * s2,
                        cy + py * hl * s1 + hy * hw * s2))
    d.polygon(corners, fill="#B07A3A", outline=INK, width=2)
    for s in (1, -1):
        ex, ey = cx + px * hl * s, cy + py * hl * s
        cap = []
        for s1, s2 in [(1, 1), (-1, 1), (-1, -1), (1, -1)]:
            cap.append((ex + px * 6 * s1 + hx * (hw + 1) * s2,
                        ey + py * 6 * s1 + hy * (hw + 1) * s2))
        d.polygon(cap, fill="#8A5A2B", outline=INK, width=1)
    bx, by = cx + hx * 62, cy + hy * 62
    d.ellipse([bx - 20, by - 7, bx + 20, by + 7], fill="#8A5A2B",
              outline=INK, width=2)
    d.ellipse([bx - 14, by - 4, bx + 14, by + 2], fill="#B07A3A")


def badge(draw, x, y, n, r=13, fill=RED):
    draw.ellipse([x, y, x + 2 * r, y + 2 * r], fill=fill,
                 outline="#FFFFFF", width=2)
    f = F(SANS_B, 14 if r >= 13 else 11)
    t = str(n)
    tw = draw.textlength(t, font=f)
    draw.text((x + r - tw / 2, y + r - (10 if r >= 13 else 8)), t, font=f,
              fill="#FFFFFF")


def panel(d, x, y, pw, ph, n, tg, head, sub, fn, art_h, head_sz,
          sub_sz, max_head=2):
    """One uniform panel: art on top, badge top-right, tag, headline, sub."""
    d.rectangle([x, y, x + pw, y + ph], fill="#FFFFFF", outline=INK,
                width=3)
    fn(d, x + 3, y + 3, pw - 6, art_h)
    badge(d, x + pw - 32, y + 6, n, r=11)
    f = F(SANS_B, 10)
    d.text((x + 10, y + art_h + 8), tg, font=f, fill=RED)
    f = F(SANS_B, head_sz)
    lines = wrap(d, head, f, pw - 20)[:max_head]
    hy = text_block(d, (x + 10, y + art_h + 24), lines, f, INK,
                    leading=int(head_sz * 1.12))
    f = F(SANS, sub_sz)
    lines = wrap(d, sub, f, pw - 20)[:2]
    text_block(d, (x + 10, hy + 2), lines, f, "#333333",
               leading=int(sub_sz * 1.12))


def face(d, cx, cy, r, skin, hair, suit):
    """Kept for compatibility: blocky head + shoulders."""
    pix_person(d, cx, cy + r + 22, skin, hair, suit, RED2, scale=1)


def flag(d, x, y, w, h, kind):
    d.rectangle([x, y, x + w, y + h], outline=INK, width=2)
    if kind == "CN":
        d.rectangle([x, y, x + w, y + h], fill=RED2)
        d.text((x + 3, y - 1), "*", font=F(SANS_B, 12), fill=YELLOW)
    elif kind == "US":
        d.rectangle([x, y, x + w, y + h], fill="#FFFFFF")
        for i in range(3):
            d.rectangle([x, y + i * h // 3, x + w, y + (i + 1) * h // 3],
                        fill=RED2 if i % 2 == 0 else "#FFFFFF")
        d.rectangle([x, y, x + w // 2, y + h // 2], fill=NAVY)
    elif kind == "RU":
        d.rectangle([x, y, x + w, y + h // 3], fill="#FFFFFF")
        d.rectangle([x, y + h // 3, x + w, y + 2 * h // 3], fill=BLUE)
        d.rectangle([x, y + 2 * h // 3, x + w, y + h], fill=RED2)


# ---------------------------------------------------------------- figures
def draw_shenzhen(d, x, y, w, h):
    """GTA Shenzhen: neon sunset, pixel skyline, three suited leaders."""
    neon_sky(d, x, y, w, h)
    # sun with halo
    d.ellipse([x + w - 62, y + 4, x + w - 22, y + 44], fill=NEON_YELLOW,
              outline=NEON_ORANGE, width=3)
    d.ellipse([x + w - 56, y + 10, x + w - 28, y + 38], fill="#FFF7AE")
    # pixel skyline: stepped block towers, neon windows, roof details
    towers = [(0, 44, 34, "#1B2A6B"), (36, 26, 30, "#0E5C2E"),
              (68, 50, 36, "#7B2FF7"), (106, 18, 28, "#14264E"),
              (136, 40, 34, "#D62828"), (172, 30, 30, "#0E7A6E"),
              (204, 52, 34, "#1B2A6B"), (240, 36, 30, "#FF6B1A"),
              (272, 54, 36, "#14264E")]
    for bx, by, bw, col in towers:
        pix_rect(d, x + bx, y + by, bw, h - 44 - by, col)
        pix_rect(d, x + bx, y + by, bw, 5, "#FFFFFF")
        for wy in range(y + by + 10, y + h - 50, 12):
            for wx in range(x + bx + 5, x + bx + bw - 6, 11):
                pix(d, wx, wy, 4,
                    NEON_CYAN if (wx + wy) % 22 == 0 else NEON_YELLOW)
    # lake with neon reflections -- leaders stand in front of it
    pix_rect(d, x, y + h - 44, w, 44, "#0E2A4A")
    for i, col in enumerate([NEON_PINK, NEON_CYAN, NEON_YELLOW, NEON_ORANGE]):
        d.line([x + 20 + i * 70, y + h - 34, x + 60 + i * 70, y + h - 34],
               fill=col, width=3)
    # red carpet
    pix_rect(d, x + w // 2 - 78, y + h - 18, 156, 10, RED2)
    # three pixel leaders, suits + ties, in front of the skyline
    pix_person(d, x + 92, y + h - 8, "#F2C9A0", "#111111", NAVY, RED2)
    pix_person(d, x + w // 2, y + h - 8, "#F2C9A0", "#F2D06B", "#7A1F1F",
               NAVY)
    pix_person(d, x + w - 92, y + h - 8, "#F2C9A0", "#C9C9C9", "#333333",
               BLUE)
    for fx, kind in [(x + 58, "CN"), (x + w // 2 - 12, "US"),
                     (x + w - 122, "RU")]:
        d.line([fx + 12, y + h - 36, fx + 12, y + h - 20], fill=INK, width=2)
        flag(d, fx, y + h - 36, 24, 15, kind)


def draw_icj(d, x, y, w, h):
    """GTA court: warm wood panels, gold scales, big wooden gavel."""
    pix_rect(d, x, y, w, h, "#8A5A2B")
    # wood grain + neon-lit panels
    for wy in range(y + 6, y + h - 6, 14):
        d.line([x + 4, wy, x + w - 4, wy], fill="#6E4423", width=1)
    for bx in (x + 10, x + w // 2 - 14, x + w - 38):
        pix_rect(d, bx, y + 6, 28, h - 12, "#C89B5A")
        pix_rect(d, bx, y + 6, 28, 6, NEON_YELLOW)
    # pediment + gold disc
    d.polygon([(x + 30, y + 4), (x + w // 2, y + 22), (x + w - 30, y + 4)],
              fill=NAVY, outline=INK, width=2)
    d.ellipse([x + w // 2 - 9, y + 8, x + w // 2 + 9, y + 26], fill=YELLOW,
              outline=INK, width=2)
    # columns
    for cx in (x + 44, x + w // 2 - 10, x + w - 64):
        pix_rect(d, cx, y + 28, 20, h - 54, "#FFF3D6")
        pix_rect(d, cx - 4, y + 24, 28, 6, NAVY)
    pix_rect(d, x, y + h - 26, w, 26, NAVY)
    # scales, large and balanced
    scx, scy = x + 108, y + 28
    d.polygon([(scx - 16, y + h - 28), (scx + 16, y + h - 28),
               (scx + 6, y + h - 36), (scx - 6, y + h - 36)],
              fill=NAVY, outline=INK, width=2)
    d.line([scx, y + h - 36, scx, scy], fill=INK, width=3)
    d.ellipse([scx - 4, scy - 4, scx + 4, scy + 4], fill=YELLOW,
              outline=INK, width=2)
    d.line([scx - 42, scy, scx + 42, scy], fill=INK, width=3)
    for s in (-1, 1):
        px = scx + s * 42
        d.line([px, scy, px, scy + 18], fill=INK, width=2)
        d.polygon([(px - 16, scy + 30), (px + 16, scy + 30),
                   (px + 10, scy + 18), (px - 10, scy + 18)],
                  fill=YELLOW, outline=INK, width=2)
        d.line([px - 16, scy + 30, px + 16, scy + 30], fill=ORANGE, width=2)
    draw_gavel(d, x + 248, y + 52, angle_deg=35)


def draw_riyadh(d, x, y, w, h):
    """GTA Riyadh night: glass PIF Tower, neon reflections, smoke."""
    pix_rect(d, x, y, w, h, "#0B1030")
    for sx, sy in [(20, 14), (70, 30), (250, 12), (290, 34), (120, 18),
                   (180, 8), (40, 44)]:
        pix(d, x + sx, y + sy, 3, "#FFFFFF")
        pix(d, x + sx + 6, y + sy + 10, 2, NEON_CYAN)
    # neon city glow at the base
    pix_rect(d, x, y + h - 16, w, 16, NEON_PINK)
    pix_rect(d, x, y + h - 16, w, 4, NEON_CYAN)
    tx = x + w // 2
    # PIF Tower: tapering glass slab, cyan/magenta faces, lit windows
    d.polygon([(tx - 34, y + h), (tx - 22, y + 8), (tx + 22, y + 8),
               (tx + 34, y + h)], fill="#1E3A6E", outline=INK, width=3)
    d.polygon([(tx - 22, y + 8), (tx - 10, y + 8), (tx - 16, y + h),
               (tx - 34, y + h)], fill="#7FD8FF")
    d.polygon([(tx + 12, y + 8), (tx + 22, y + 8), (tx + 34, y + h),
               (tx + 20, y + h)], fill="#FF2E88")
    for wy in range(y + 16, y + h - 8, 12):
        for wx in range(tx - 26, tx + 20, 11):
            pix(d, wx, wy, 4,
                NEON_YELLOW if (wx + wy) % 24 == 0 else NEON_CYAN)
    # crack zigzag
    d.line([(tx - 28, y + 44), (tx - 8, y + 58), (tx + 6, y + 46),
            (tx + 26, y + 62)], fill=RED, width=4)
    d.line([(tx - 20, y + 74), (tx + 2, y + 86), (tx + 22, y + 76)],
           fill=RED, width=3)
    smoke_plume(d, tx + 2, y, w, h, base_y=y + 52, lean=-1)
    # side towers with neon windows
    for bx, bw, bh, col in [(8, 44, 52, "#0E5C2E"), (58, 36, 38, "#7B2FF7"),
                            (w - 96, 38, 44, "#0E5C2E"),
                            (w - 52, 44, 58, "#7B2FF7")]:
        pix_rect(d, x + bx, y + h - bh, bw, bh, col)
        for wy in range(y + h - bh + 6, y + h - 6, 10):
            pix(d, x + bx + 6, wy, 3, NEON_YELLOW)
            pix(d, x + bx + bw - 12, wy, 3, NEON_CYAN)
    d.ellipse([x + 12, y + h - 26, x + 34, y + h - 6], fill=NEON_ORANGE,
              outline=INK, width=2)


def draw_gta(d, x, y, w, h):
    """GTA Vice City: neon sunset, palms, neon VI, low sports car."""
    neon_sky(d, x, y, w, h)
    # sun with glow rings
    sr = min(18, h // 3)
    d.ellipse([x + w // 2 - sr - 6, y - 2, x + w // 2 + sr + 6,
               y + 10 + 2 * sr], outline=NEON_YELLOW, width=2)
    d.ellipse([x + w // 2 - sr, y + 4, x + w // 2 + sr, y + 4 + 2 * sr],
              fill=NEON_YELLOW, outline=NEON_ORANGE, width=2)
    # neon skyline silhouettes
    for bx, bw, bh, col in [(0, 30, 30, "#2A0A4A"), (w - 34, 34, 38,
                                                     "#2A0A4A")]:
        pix_rect(d, x + bx, y + h - bh - 14, bw, bh, col)
        for wy in range(y + h - bh - 8, y + h - 16, 9):
            pix(d, x + bx + 5, wy, 3, NEON_PINK)
    # palms, bigger and blockier
    pix_palm(d, x + 22, y + h - 16, 34)
    pix_palm(d, x + w - 28, y + h - 16, 30)
    # neon VI, top-left, with pink glow block behind it
    pix_rect(d, x + 6, y + 2, 44, 26, NEON_PINK)
    f = F(SANS_B, 22)
    d.text((x + 12, y + 4), "VI", font=f, fill="#FFFFFF",
           stroke_width=2, stroke_fill=INK)
    # road + lane dashes + car
    pix_rect(d, x, y + h - 16, w, 16, "#1A0A2E")
    for lx in range(x + 8, x + w - 8, 26):
        d.line([lx, y + h - 8, lx + 12, y + h - 8], fill=NEON_YELLOW,
               width=2)
    pix_car(d, x + w // 4, y + h - 38, w // 2, 24, RED, neon=NEON_CYAN)

def draw_anthropic(d, x, y, w, h):
    """GTA Nasdaq: neon ticker board, green chart, city lights."""
    pix_rect(d, x, y, w, h, "#0B1030")
    # city lights at the bottom
    for bx, bw, bh in [(0, 18, 12), (26, 14, 18), (w - 44, 16, 14),
                       (w - 22, 12, 10)]:
        pix_rect(d, x + bx, y + h - bh, bw, bh, NEON_PURPLE)
        pix(d, x + bx + 3, y + h - bh + 3, 3, NEON_YELLOW)
    pix_rect(d, x + 8, y + 8, w - 16, 26, "#FFFFFF")
    f = F(SANS_B, 18)
    d.text((x + 14, y + 11), "ANT", font=f, fill=NAVY)
    f = F(SANS_B, 14)
    d.text((x + 70, y + 13), "$83 IPO", font=f, fill="#1F7A3A")
    d.text((x + w - 62, y + 13), "+17%", font=f, fill="#1F7A3A")
    d.polygon([(x + w - 70, y + 16), (x + w - 62, y + 16),
               (x + w - 66, y + 24)], fill="#1F7A3A")
    pts = [(x + 14, y + h - 14), (x + 60, y + h - 20), (x + 100, y + h - 16),
           (x + 140, y + h - 30), (x + 180, y + h - 34), (x + w - 18, y + 40)]
    d.polygon(pts + [(x + w - 18, y + h - 6), (x + 14, y + h - 6)],
              fill="#123A24")
    for gy in (y + 44, y + 54):
        d.line([x + 10, gy, x + w - 10, gy], fill="#2A4A6E", width=1)
    d.line(pts, fill=NEON_GREEN, width=4, joint="curve")
    d.polygon([(pts[-1][0], pts[-1][1]), (pts[-1][0] - 14, pts[-1][1] - 2),
               (pts[-1][0] - 4, pts[-1][1] + 12)], fill=NEON_GREEN)
    # neon dollar coin
    d.ellipse([x + w - 34, y + h - 30, x + w - 12, y + h - 8],
              fill=NEON_YELLOW, outline=INK, width=2)
    d.text((x + w - 30, y + h - 28), "$", font=F(SANS_B, 14), fill=INK)


def draw_greenland(d, x, y, w, h):
    """GTA Arctic: aurora sky, pixel Greenland, iceberg, Danish flag."""
    pix_rect(d, x, y, w, h, "#0E2A4A")
    # aurora bands: neon green / pink ribbons
    for i, col in enumerate([NEON_GREEN, NEON_CYAN, NEON_PINK]):
        d.polygon([(x, y + 6 + i * 7), (x + w // 3, y + 2 + i * 7),
                   (x + 2 * w // 3, y + 10 + i * 7), (x + w, y + 4 + i * 7),
                   (x + w, y + 10 + i * 7), (x + 2 * w // 3, y + 16 + i * 7),
                   (x + w // 3, y + 8 + i * 7), (x, y + 12 + i * 7)],
                  fill=col)
    pix_rect(d, x, y + h - 18, w, 18, "#7FB8D9")
    # Greenland, jagged east coast, pointed south tip
    d.polygon([(x + w // 4 + 6, y + 24), (x + w // 2, y + 20),
               (x + 3 * w // 4, y + 22), (x + w - 16, y + 30),
               (x + w - 10, y + h // 2 - 4), (x + w - 22, y + h // 2 + 6),
               (x + 3 * w // 5 + 8, y + h - 20),
               (x + w // 2 - 6, y + h - 24),
               (x + 2 * w // 5 - 6, y + h - 18),
               (x + w // 4 - 2, y + h // 2)],
              fill="#FFFFFF", outline=INK, width=2)
    d.polygon([(x + 3 * w // 4, y + 22), (x + w - 16, y + 30),
               (x + w - 10, y + h // 2 - 4), (x + w - 22, y + h // 2 + 6),
               (x + 3 * w // 4 - 4, y + h // 2)],
              fill="#D6ECF5")
    d.line([x + w - 18, y + 34, x + w - 30, y + 42], fill="#7FB8D9", width=2)
    d.ellipse([x + w // 2 - 10, y + h // 3, x + w // 2 + 10,
               y + h // 3 + 20], fill=RED, outline=INK, width=2)
    d.ellipse([x + w // 2 - 10, y + h // 3 + 10, x + w // 2 + 10,
               y + h // 3 + 20], fill="#FFFFFF")
    d.polygon([(x + w - 52, y + h - 22), (x + w - 38, y + h - 32),
               (x + w - 24, y + h - 22)], fill="#FFFFFF", outline=INK,
              width=2)
    d.ellipse([x + w - 52, y + h - 24, x + w - 24, y + h - 18],
              fill="#7FB8D9")
    d.rectangle([x + 8, y + 6, x + 30, y + 18], fill=RED2, outline=INK,
                width=2)
    d.line([x + 8, y + 12, x + 30, y + 12], fill="#FFFFFF", width=2)
    d.line([x + 19, y + 6, x + 19, y + 18], fill="#FFFFFF", width=2)


def draw_kerch(d, x, y, w, h):
    """GTA Kerch: dusk bridge, neon blast, pixel waves."""
    # dusk gradient: orange -> purple
    for i, col in enumerate([NEON_ORANGE, "#FF5E3A", NEON_PURPLE, "#2A0A4A"]):
        pix_rect(d, x, y + i * h // 4, w, h // 4 + 1, col)
    pix_rect(d, x, y + h - 18, w, 18, "#0E5C8A")
    for i in range(4):
        wx = x + 10 + i * (w // 4)
        d.arc([wx, y + h - 16, wx + 26, y + h - 6], 180, 360,
              fill=NEON_CYAN, width=2)
    pix_rect(d, x + 18, y + 22, 12, h - 40, "#8A6D3B")
    pix_rect(d, x + w - 30, y + 22, 12, h - 40, "#8A6D3B")
    d.line([x + 6, y + 36, x + w // 2 - 26, y + 36], fill="#FFD23F", width=4)
    d.line([x + w // 2 + 26, y + 36, x + w - 6, y + 36], fill="#FFD23F",
           width=4)
    cx, cy = x + w // 2, y + 34
    for a in range(8):
        ang = math.radians(a * 45)
        d.line([cx, cy, cx + 17 * math.cos(ang), cy + 17 * math.sin(ang)],
               fill=NEON_YELLOW, width=3)
    d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=NEON_ORANGE,
              outline=INK, width=2)
    d.line([cx - 11, cy + 10, cx - 3, cy + 22], fill=RED2, width=2)
    d.line([cx + 11, cy + 10, cx + 3, cy + 22], fill=RED2, width=2)
    smoke_plume(d, cx, y, w, h, base_y=y + 30, lean=1)


def draw_cyclone(d, x, y, w, h):
    """GTA cyclone: dark storm sky, neon spiral, pixel coast."""
    pix_rect(d, x, y, w, h, "#0E2A4A")
    for sx, sy in [(14, 8), (w - 20, 10), (w // 3, 6)]:
        pix(d, x + sx, y + sy, 3, NEON_YELLOW)
    cx, cy = x + w // 2, y + h // 2
    for r, start, col in [(30, 20, "#FFFFFF"), (25, 110, NEON_CYAN),
                          (19, 200, "#FFFFFF"), (13, 290, NEON_CYAN),
                          (7, 40, "#FFFFFF")]:
        d.arc([cx - r, cy - r, cx + r, cy + r], start, start + 280,
              fill=col, width=3)
    d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=RED, outline=INK,
              width=2)
    d.ellipse([cx - 11, cy - 11, cx + 11, cy + 11], outline="#FFFFFF",
              width=2)
    # rain streaks, neon cyan
    for i in range(5):
        lx = x + 10 + i * (w // 5)
        d.line([lx, y + h - 14, lx - 5, y + h - 5], fill=NEON_CYAN, width=2)
        d.line([lx + 8, y + h - 12, lx + 3, y + h - 4], fill="#7FB8D9",
               width=1)
    # pixel coast + houses
    pix_rect(d, x, y + h - 8, w, 8, "#2E7A4E")
    for hx, col in [(x + 18, RED), (x + 60, NEON_YELLOW), (x + 150, TEAL)]:
        pix_rect(d, hx, y + h - 20, 16, 12, col)
        d.polygon([(hx - 2, y + h - 20), (hx + 8, y + h - 28),
                   (hx + 18, y + h - 20)], fill=INK)
    d.ellipse([x + 6, y + 4, x + 22, y + 20], fill=NEON_YELLOW,
              outline=INK, width=2)


def draw_gaza(d, x, y, w, h):
    """GTA Gaza: pixel rubble blocks, layered smoke, ember glow."""
    pix_rect(d, x, y, w, h, "#FF9E7D")
    d.ellipse([x + 8, y + 6, x + 28, y + 26], fill=RED, outline=INK, width=2)
    smoke_plume(d, x + 58, y, w, h, base_y=y + h - 34, lean=-1)
    smoke_plume(d, x + 150, y, w, h, base_y=y + h - 30, lean=1)
    d.ellipse([x + 48, y + h - 40, x + 68, y + h - 30], fill=NEON_ORANGE,
              outline=INK, width=1)
    d.ellipse([x + 140, y + h - 36, x + 160, y + h - 26], fill=NEON_ORANGE,
              outline=INK, width=1)
    # pixel rubble: stepped blocks with window holes
    for bx, bw, bh, col in [(10, 42, 32, "#3A3A3A"), (62, 34, 24, "#5A4630"),
                            (106, 44, 38, "#3A3A3A"), (158, 36, 26, "#5A4630")]:
        pix_rect(d, x + bx, y + h - 16 - bh, bw, bh, col)
        pix(d, x + bx + 6, y + h - 16 - bh + 6, 4, NEON_YELLOW)
        pix(d, x + bx + bw - 12, y + h - 16 - bh + 12, 4, NEON_CYAN)
    pix_rect(d, x, y + h - 16, w, 16, "#C9B48A")


def draw_nk(d, x, y, w, h):
    """GTA Yongbyon: pixel cooling tower, neon warning, fence."""
    pix_rect(d, x, y, w, h, "#0E2A4A")
    for sx in (14, 60, 120, 180):
        pix(d, x + sx, y + 8, 3, NEON_YELLOW)
    # pixel cooling tower with brick courses
    d.polygon([(x + 52, y + 14), (x + 84, y + 14), (x + 76, y + h - 14),
               (x + 60, y + h - 14)], fill="#FFFFFF", outline=INK, width=2)
    for wy in range(y + 24, y + h - 16, 10):
        d.line([x + 54, wy, x + 82, wy], fill="#C9C9C9", width=1)
    d.ellipse([x + 52, y + 10, x + 84, y + 22], fill="#B9CDE0",
              outline=INK, width=2)
    for sx, sy, r in [(x + 60, y + 6, 8), (x + 78, y + 2, 10)]:
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill="#FFFFFF",
                  outline=INK, width=2)
    # warning triangle, neon yellow
    d.polygon([(x + w - 62, y + 16), (x + w - 26, y + 16),
               (x + w - 44, y + 52)], fill=NEON_YELLOW, outline=INK, width=2)
    d.text((x + w - 48, y + 26), "!", font=F(SANS_B, 20), fill=INK)
    # fence + green ground
    for fx in range(x + 8, x + w - 8, 18):
        d.line([fx, y + h - 22, fx, y + h - 14], fill=INK, width=2)
    d.line([x + 8, y + h - 20, x + w - 8, y + h - 20], fill=INK, width=2)
    pix_rect(d, x, y + h - 14, w, 14, "#2E7A4E")


def draw_bangladesh(d, x, y, w, h):
    """GTA street: pixel crowd, placards, flame, neon banner."""
    neon_sky(d, x, y, w, h)
    pix_rect(d, x + 10, y + 4, w - 56, 16, RED)
    f = F(SANS_B, 11)
    d.text((x + 16, y + 7), "SHUTDOWN", font=f, fill="#FFFFFF")
    # flame with layered petals
    d.ellipse([x + w - 44, y + 34, x + w - 14, y + 62], fill=NEON_ORANGE,
              outline=INK, width=2)
    d.ellipse([x + w - 36, y + 42, x + w - 22, y + 62], fill=NEON_YELLOW)
    d.ellipse([x + w - 32, y + 50, x + w - 26, y + 62], fill="#FFFFFF")
    # pixel crowd, 5 people with placards
    for i, (cx, col, hair) in enumerate([(x + 34, NAVY, "#111111"),
                                        (x + 66, TEAL, "#5A3A1A"),
                                        (x + 98, RED2, "#111111"),
                                        (x + 130, NAVY2, "#C9C9C9"),
                                        (x + 162, NEON_ORANGE, "#111111")]):
        pix_person(d, cx, y + h - 8, "#F2C9A0", hair, col, YELLOW)
        # (placards removed: they covered the SHUTDOWN banner text)


def draw_cop(d, x, y, w, h):
    """GTA COP31: neon globe, orbit ring, leaf, hot sun, flags."""
    pix_rect(d, x, y, w, h, "#0E2A4A")
    d.ellipse([x + 8, y + 6, x + 30, y + 28], fill=NEON_ORANGE,
              outline=INK, width=2)
    cx, cy = x + w // 2, y + h // 2
    d.ellipse([cx - 34, cy - 12, cx + 34, cy + 12], outline=NEON_CYAN,
              width=2)
    d.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], fill="#3B82D6",
              outline=INK, width=2)
    d.polygon([(cx + 4, cy - 22), (cx + 22, cy - 22), (cx + 22, cy + 22),
               (cx + 4, cy + 22)], fill="#2A5AAC")
    d.ellipse([cx - 18, cy - 18, cx - 2, cy - 4], fill="#7FC4E8")
    # pixel continents
    d.polygon([(cx - 15, cy - 5), (cx - 2, cy - 12), (cx + 8, cy - 2),
               (cx - 3, cy + 8)], fill=NEON_GREEN, outline=INK, width=1)
    d.polygon([(cx - 5, cy + 7), (cx + 13, cy + 3), (cx + 15, cy + 15),
               (cx + 2, cy + 17)], fill=NEON_GREEN, outline=INK, width=1)
    d.ellipse([cx - 28, cy + 6, cx - 5, cy + 24], fill="#7FC4E8")
    d.ellipse([cx - 24, cy + 20, cx + 24, cy + 28], fill="#A8D8B0")
    d.ellipse([x + 14, y + h - 26, x + 44, y + h - 6], fill="#2E7A4E",
              outline=INK, width=2)
    d.line([x + 18, y + h - 10, x + 40, y + h - 22], fill="#FFFFFF",
           width=2)
    # tiny flags row at the bottom
    for i, col in enumerate([NEON_PINK, NEON_CYAN, NEON_YELLOW, NEON_GREEN]):
        pix_rect(d, x + w - 52 + i * 12, y + h - 14, 10, 8, col)

def draw_venezuela(d, x, y, w, h):
    """GTA Caracas deal: pixel flags, signed document, handshake."""
    pix_rect(d, x, y, w, h, "#0E2A4A")
    # neon skyline strip at the bottom
    for bx, bw, bh in [(0, 22, 10), (30, 16, 16), (w - 40, 20, 12)]:
        pix_rect(d, x + bx, y + h - bh, bw, bh, NEON_PURPLE)
        pix(d, x + bx + 4, y + h - bh + 3, 3, NEON_YELLOW)
    # US flag top left, Venezuela stripes top right (pixel blocks)
    pix_rect(d, x + 8, y + 6, 30, 14, "#FFFFFF")
    pix_rect(d, x + 8, y + 6, 30, 5, RED2)
    pix_rect(d, x + 8, y + 15, 30, 5, RED2)
    pix_rect(d, x + 8, y + 6, 12, 7, NAVY)
    for i, col in enumerate([NEON_YELLOW, BLUE, RED2]):
        pix_rect(d, x + w - 38, y + 6 + i * 5, 30, 5, col)
    # document with seal + pen, handshake below
    pix_rect(d, x + w // 4, y + h // 3, w // 2, h - h // 3 - 8, "#FFFFFF")
    for i in range(3):
        d.line([x + w // 4 + 8, y + h // 3 + 10 + i * 8,
                x + 3 * w // 4 - 8, y + h // 3 + 10 + i * 8],
               fill="#555555", width=2)
    d.ellipse([x + w // 2 - 8, y + h - 22, x + w // 2 + 8, y + h - 6],
              fill=RED, outline=INK, width=2)
    d.line([x + w - 30, y + h - 24, x + w - 12, y + h - 10], fill=INK,
           width=3)
    # two pixel hands meeting over the seal
    pix_rect(d, x + w // 2 - 26, y + h - 30, 20, 8, "#F2C9A0")
    pix_rect(d, x + w // 2 + 6, y + h - 30, 20, 8, "#C9A06B")


def draw_hormuz(d, x, y, w, h):
    """GTA Hormuz: pixel tanker, neon flames, smoke, waves."""
    pix_rect(d, x, y, w, h, "#FF9E7D")
    d.ellipse([x + w - 30, y + 4, x + w - 10, y + 24], fill=NEON_YELLOW,
              outline=INK, width=2)
    pix_rect(d, x, y + 2 * h // 3, w, h // 3, "#0E5C8A")
    for i in range(3):
        wx = x + 12 + i * (w // 3)
        d.arc([wx, y + 2 * h // 3 + 4, wx + 24, y + 2 * h // 3 + 14],
              180, 360, fill=NEON_CYAN, width=2)
    d.polygon([(x + 12, y + h // 2), (x + w - 12, y + h // 2),
               (x + w - 26, y + 2 * h // 3), (x + 26, y + 2 * h // 3)],
              fill="#8A5A2B", outline=INK, width=2)
    for i, col in enumerate([RED2, TEAL, NEON_YELLOW]):
        pix_rect(d, x + 24 + i * 36, y + h // 2 - 16,
                 30, 16, col)
    for fx in (x + w // 3, x + w // 2, x + 2 * w // 3):
        d.ellipse([fx - 8, y + h // 2 - 24, fx + 8, y + h // 2 - 6],
                  fill=NEON_ORANGE, outline=INK, width=2)
        d.ellipse([fx - 4, y + h // 2 - 16, fx + 4, y + h // 2 - 6],
                  fill=NEON_YELLOW)
    smoke_plume(d, x + w // 2, y, w, h, base_y=y + h // 2 - 4, lean=-1)


def draw_senegal(d, x, y, w, h):
    """GTA Senegal: pixel boat, neon sea, lifebuoy, gulls."""
    pix_rect(d, x, y, w, h, "#FF7BAC")
    d.ellipse([x + 8, y + 6, x + 26, y + 24], fill=NEON_YELLOW,
              outline=INK, width=2)
    pix_rect(d, x, y + 2 * h // 3, w, h // 3, "#0E5C8A")
    for i in range(3):
        wx = x + 10 + i * (w // 3)
        d.arc([wx, y + 2 * h // 3 + 4, wx + 28, y + 2 * h // 3 + 16],
              180, 360, fill=NEON_CYAN, width=2)
    d.polygon([(x + w // 4, y + h // 2), (x + 3 * w // 4, y + h // 2 - 8),
               (x + 3 * w // 4 - 10, y + 2 * h // 3),
               (x + w // 4 + 10, y + 2 * h // 3)], fill="#8A5A2B",
              outline=INK, width=2)
    d.line([x + w // 2, y + h // 2 - 6, x + w // 2, y + h // 4],
           fill=INK, width=2)
    d.polygon([(x + w // 2, y + h // 4), (x + w // 2 + 22, y + h // 3),
               (x + w // 2, y + h // 3)], fill=NEON_PINK, outline=INK,
              width=2)
    # pixel passengers: two heads in the boat
    pix_person(d, x + w // 2 - 12, y + h // 2 + 2, "#F2C9A0", "#111111",
               TEAL, YELLOW, scale=1)
    d.ellipse([x + w - 34, y + h - 26, x + w - 12, y + h - 4], fill="#FFFFFF",
              outline=RED, width=4)
    d.ellipse([x + w - 28, y + h - 20, x + w - 18, y + h - 10],
              fill="#2E7AC4", outline=RED, width=2)
    # gulls
    for gx, gy in [(x + 40, y + 12), (x + 90, y + 8)]:
        d.arc([gx, gy, gx + 10, gy + 6], 180, 360, fill=INK, width=2)
        d.arc([gx + 10, gy, gx + 20, gy + 6], 180, 360, fill=INK, width=2)


def draw_crabs(d, x, y, w, h):
    """GTA Christmas Island: pixel red crabs, neon sea, palm."""
    pix_rect(d, x, y, w, h, "#FFE8B8")
    pix_rect(d, x, y, w, h // 4, NEON_CYAN)
    for i in range(3):
        wx = x + 10 + i * (w // 3)
        d.arc([wx, y + 6, wx + 24, y + 16], 180, 360, fill="#FFFFFF",
              width=2)
    pix_palm(d, x + 14, y + h - 10, 26)
    # three crabs: shell pattern, eye stalks, legs, claws
    for cx in (x + w // 4 + 10, x + w // 2, x + 3 * w // 4 - 10):
        cy = y + 2 * h // 3
        for dx in (-16, -10, 10, 16):
            d.line([cx + dx, cy, cx + dx * 3 // 2, cy + 10], fill=RED2,
                   width=2)
        d.ellipse([cx - 16, cy - 9, cx + 16, cy + 9], fill=RED,
                  outline=INK, width=2)
        pix(d, cx - 6, cy - 4, 4, NEON_YELLOW)
        pix(d, cx + 2, cy + 2, 4, "#7A1010")
        d.line([cx - 8, cy - 9, cx - 8, cy - 16], fill=INK, width=2)
        d.line([cx + 8, cy - 9, cx + 8, cy - 16], fill=INK, width=2)
        d.ellipse([cx - 10, cy - 18, cx - 6, cy - 14], fill=INK)
        d.ellipse([cx + 6, cy - 18, cx + 10, cy - 14], fill=INK)
        d.ellipse([cx - 22, cy - 14, cx - 12, cy - 4], fill=RED,
                  outline=INK, width=2)
        d.ellipse([cx + 12, cy - 14, cx + 22, cy - 4], fill=RED,
                  outline=INK, width=2)
    d.ellipse([x + w - 30, y + h - 18, x + w - 14, y + h - 4],
              fill="#2E7A4E", outline=INK, width=2)


def draw_map(d, x, y, w, h):
    """GTA-style world map: neon sea, green continents, red dots."""
    s = min(w / 380.0, h / 150.0)
    ox = x + (w - 380 * s) / 2
    oy = y + (h - 150 * s) / 2

    def P(pts):
        return [(ox + px * s, oy + py * s) for px, py in pts]

    pix_rect(d, x, y, w, h, "#0E5C8A")
    land1, land2 = "#39FF6A", "#2ECC71"
    d.polygon(P([(10, 28), (35, 18), (65, 12), (95, 16), (105, 30),
                 (95, 45), (72, 50), (58, 64), (38, 58), (16, 44)]),
              fill=land1, outline="#0E5C2E", width=2)
    d.polygon(P([(78, 72), (105, 68), (116, 86), (106, 110), (92, 130),
                 (82, 108), (74, 88)]),
              fill=land2, outline="#0E5C2E", width=2)
    d.polygon(P([(190, 20), (215, 10), (236, 16), (241, 30), (226, 40),
                 (206, 38), (190, 30)]),
              fill=land2, outline="#0E5C2E", width=2)
    d.polygon(P([(195, 52), (225, 48), (246, 58), (251, 86), (236, 115),
                 (216, 104), (200, 80)]),
              fill=land1, outline="#0E5C2E", width=2)
    d.polygon(P([(245, 12), (300, 8), (350, 12), (371, 28), (356, 48),
                 (326, 62), (286, 58), (256, 42), (240, 25)]),
              fill=land1, outline="#0E5C2E", width=2)
    d.polygon(P([(214, 6), (232, 4), (238, 10), (224, 14), (212, 12)]),
              fill="#FFFFFF", outline="#0E5C2E", width=1)
    d.ellipse([ox + 325 * s, oy + 102 * s, ox + 372 * s, oy + 128 * s],
              fill=land2, outline="#0E5C2E", width=2)
    dots = {1: (330, 30), 2: (215, 30), 3: (255, 62),
            6: (232, 26), 7: (225, 96), 8: (315, 48), 9: (246, 56)}
    f = F(SANS_B, 11)
    r = max(7, int(9 * s))
    for n, (dx, dy) in dots.items():
        cx, cy = ox + dx * s, oy + dy * s
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED,
                  outline="#FFFFFF", width=2)
        t = str(n)
        d.text((cx - d.textlength(t, font=f) / 2, cy - 7), t, font=f,
               fill="#FFFFFF", stroke_width=1, stroke_fill=INK)


# ---------------------------------------------------------------- page
def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead: GTA poster block -- deep purple-navy, neon strips ----
    d.rectangle([0, 0, W, 132], fill="#1B0A3A")
    d.rectangle([0, 0, W, 6], fill=NEON_PINK)
    d.rectangle([0, 126, W, 132], fill=NEON_CYAN)
    d.rectangle([16, 14, 100, 48], fill=NEON_PINK, outline="#FFFFFF",
                width=2)
    f = F(SANS_B, 16)
    d.text((24, 22), "THE DAY", font=f, fill="#FFFFFF")
    f = F(SANS_B, 13)
    d.text((116, 16), "T H E   D A Y   I N   W O R L D   N E W S", font=f,
           fill=NEON_YELLOW)
    f = F(SERIF_B, 38)
    d.text((114, 36), "Thursday 19 November 2026", font=f, fill="#FFFFFF")
    f = F(SANS_B, 15)
    d.text((116, 90), "22 STORIES  ·  7 REGIONS  ·  16 DRAWN  ·  ONE PAGE",
           font=f, fill="#FFFFFF")
    d.ellipse([W - 64, 84, W - 24, 124], fill=NEON_YELLOW, outline=INK,
              width=2)
    d.text((W - 54, 92), "!", font=F(SANS_B, 22), fill=INK)
    d.rectangle([0, 132, W, 138], fill=NEON_PINK)

    # ---- region bar: flat colour chips, equal widths, centred text ----
    regions = [("ASIA", "7", "#FFD23F"), ("EUROPE", "2", "#8ECAE6"),
               ("MIDDLE EAST", "3", "#F77F00"), ("AMERICAS", "4", "#E63946"),
               ("AFRICA", "3", "#2A9D8F"), ("OCEANIA", "1", "#B388EB"),
               ("GLOBAL", "2", "#C9C9C9")]
    f = F(SANS_B, 13)
    seg_w = (W - 16) // len(regions)
    for i, (name, n, col) in enumerate(regions):
        x = 8 + i * seg_w
        d.rectangle([x, 144, x + seg_w - 4, 168], fill=col, outline=INK,
                    width=2)
        t = f"{name} {n}"
        d.text((x + (seg_w - 4 - d.textlength(t, font=f)) / 2, 149), t,
               font=f, fill=INK)

    # ---- UTC timeline strip ----
    f = F(SANS_B, 12)
    d.text((12, 176), "THE DAY IN UTC", font=f, fill=RED)
    beats = ["GTA VI OUT", "ICJ RULES", "SHENZHEN SUMMIT", "PIF TOWER HIT",
             "ANT DEBUTS"]
    bx = 172
    for i, b in enumerate(beats):
        d.ellipse([bx, 176, bx + 12, 188], fill=NAVY, outline=INK, width=1)
        d.text((bx + 20, 176), b, font=f, fill=INK)
        bx += 32 + d.textlength(b, font=f) + 36
    d.line([8, 196, 1016, 196], fill=INK, width=2)

    heroes = [
        (1, "ASIA · DIPLOMACY", "TRUMP, XI & PUTIN MEET IN SHENZHEN",
         "First-ever trilateral at Kylin Villa — 'peace declaration', "
         "no breakthrough yet.", draw_shenzhen),
        (2, "ASIA · LAW", "ICJ: MYANMAR GUILTY OF GENOCIDE",
         "First-ever state genocide ruling — ~10,000 Rohingya killed "
         "in 2017.", draw_icj),
        (3, "MIDDLE EAST · SECURITY", "HOUTHI MISSILE HITS RIYADH TOWER",
         "PIF Tower, Riyadh's tallest, damaged — no injuries reported.",
         draw_riyadh),
    ]
    for i, (n, tg, head, sub, fn) in enumerate(heroes):
        panel(d, 8 + i * 339, 204, 330, 200, n, tg, head, sub, fn, 108, 16,
              12, max_head=3)

    second = [
        (4, "CULTURE · TECH", "GTA VI IS OUT AFTER 13 YEARS",
         "Vice City returns; 99 Metacritic.", draw_gta),
        (5, "GLOBAL · BUSINESS", "ANTHROPIC DEBUTS ON NASDAQ",
         "$83 IPO, biggest ever; ANT starts trading.", draw_anthropic),
        (6, "EUROPE · ARCTIC", "DENMARK RATIFIES GREENLAND PACT",
         "109-0 vote; two US bases, sovereignty kept.", draw_greenland),
        (7, "EUROPE · WAR", "KERCH BRIDGE HIT AGAIN",
         "Rail disrupted; Odesa strike kills 4.", draw_kerch),
    ]
    for i, (n, tg, head, sub, fn) in enumerate(second):
        panel(d, 8 + i * 254, 412, 246, 150, n, tg, head, sub, fn, 66, 14,
              11)

    third = [
        (8, "ASIA · WEATHER", "CYCLONE AKVAN NEARS INDIA",
         "~50,000 evacuated; landfall due Fri.", draw_cyclone),
        (9, "MIDDLE EAST · WAR", "GAZA: NEW OPERATION",
         "Central Gaza; Arab League condemns.", draw_gaza),
        (10, "ASIA · SECURITY", "N. KOREA EXPANDS ENRICHMENT",
         "IAEA warns on Yongbyon.", draw_nk),
        (11, "ASIA · POLITICS", "BANGLADESH SHUTDOWN",
         "Yunus family home torched in unrest.", draw_bangladesh),
    ]
    for i, (n, tg, head, sub, fn) in enumerate(third):
        panel(d, 8 + i * 254, 570, 246, 140, n, tg, head, sub, fn, 62, 13,
              11)

    fourth = [
        (12, "GLOBAL · CLIMATE", "COP31: FINAL STRETCH",
         "Fossil-fuel wording unresolved; Fiji drought.", draw_cop),
        (13, "AMERICAS · DIPLOMACY", "VENEZUELA DEAL SIGNED WEDNESDAY",
         "US restores military ties; signed 18 Nov.", draw_venezuela),
        (14, "MIDDLE EAST · ENERGY", "HORMUZ: 3 TANKERS REPORTED ON FIRE",
         "Iranian reports only; cause unconfirmed.", draw_hormuz),
        (15, "AFRICA · MIGRATION", "SENEGAL BOAT SINKS; DOZENS MISSING",
         "Boat with ~100 migrants reported sunk.", draw_senegal),
        (16, "OCEANIA · NATURE", "RED CRABS BEGIN ANNUAL MIGRATION",
         "Millions head to the sea, Christmas Is.", draw_crabs),
    ]
    for i, (n, tg, head, sub, fn) in enumerate(fourth):
        panel(d, 8 + i * 203, 718, 195, 140, n, tg, head, sub, fn, 56, 13,
              11)

    # ---- bottom: map + ALSO, same top (866) and bottom (960) ----
    d.rectangle([8, 866, 318, 960], fill="#FFFFFF", outline=INK, width=3)
    f = F(SANS_B, 15)
    d.text((20, 872), "WHERE IT HAPPENED", font=f, fill=INK)
    draw_map(d, 18, 892, 290, 44)
    f = F(SANS, 10)
    d.text((20, 942),
           "1 Shenzhen  2 The Hague  3 Riyadh  6 Greenland  7 Kerch",
           font=f, fill="#333333")

    d.rectangle([326, 866, 1016, 960], fill="#FFFFFF", outline=INK, width=3)
    f = F(SANS_B, 15)
    d.text((338, 872), "ALSO ON THURSDAY 19 NOVEMBER", font=f, fill=INK)
    also_l = [
        "17. Gas Husky: all 19 crew safe",
        "18. Trump on Iran: 'see what happens'",
        "19. Japan Tobacco $8.9bn charge",
    ]
    also_r = [
        "20. Sudan: RSF commander defects",
        "21. DR Congo: Ebola response hampered",
        "22. Haiti pastor convicted in Miami",
    ]
    f = F(SANS, 11)
    y = 896
    for t in also_l:
        d.text((338, y), t, font=f, fill="#222222")
        y += 20
    y = 896
    for t in also_r:
        d.text((676, y), t, font=f, fill="#222222")
        y += 20

    # ---- date check ----
    d.rectangle([8, 966, 1016, 998], outline=RED, width=3, fill="#FDECEC")
    f = F(SANS_B, 12)
    d.text((20, 971), "DATE CHECK — NOT 19 NOV NEWS:", font=f, fill=RED)
    f = F(SANS, 11)
    d.text((20, 982),
           "Van Gogh $190.4m sale was 18 Nov; Cyclone Akvan landfall is "
           "20 Nov; no Shenzhen breakthrough.", font=f, fill="#333333")

    # ---- footer ----
    f = F(SANS, 11)
    d.text((8, 1004),
           "Sources: Reuters · AP · AFP · Al Jazeera · Nikkei · IAEA · IMD "
           "· All stories from Thursday 19 November 2026.",
           font=f, fill="#555555")
    d.text((W - 8 - d.textlength("make.fun / @inl-xin", font=f), 1004),
           "make.fun / @inl-xin", font=f, fill="#555555")

    img.save(out, "PNG", optimize=True)
    print("saved", out, img.size)


if __name__ == "__main__":
    main()
