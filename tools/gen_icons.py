#!/usr/bin/env python3
"""Generates the 16x16 shaded pixel-art module icons.

Run:  python3 tools/gen_icons.py            -> writes intermediary-src/client/confis/IconData.java
      python3 tools/gen_icons.py preview.png -> also writes a contact sheet (needs Pillow)

Icons are drawn with a tiny pixel toolkit (shapes + bevel shading + automatic 1px outline) so every
icon shares the same light source (top-left), outline color and palette. Edit the draw_* functions and
re-run to tweak an icon. The Java side only reads the resulting character grids (see Icons.java).
"""
import math
import os
import sys

N = 16

# palette: one character -> 0xRRGGBB. '.' = transparent. Light comes from the top-left.
PAL = {
    'k': 0x141C2B,  # outline
    'w': 0xFFFFFF,
    'S': 0xF2F6FA, 's': 0xC4CDD8, 't': 0x7C8799,  # silver light / mid / dark
    'B': 0x9AD0FF, 'b': 0x3F8EEA, 'd': 0x1F4FA8, 'F': 0x13295C,  # blue light / mid / dark / face
    'R': 0xFF9494, 'r': 0xE2363F, 'D': 0x8E1C2A,
    'G': 0xA6F5B0, 'g': 0x3DC85C, 'h': 0x1E7A3A,
    'Y': 0xFFF08A, 'y': 0xF6C31C, 'z': 0xB57F10,
    'P': 0xD6B0FF, 'p': 0x9552E8, 'q': 0x5A2AA3,
    'C': 0xB4FFFF, 'c': 0x3FD9D9, 'e': 0x1B8D96,
    'N': 0xDDA062, 'n': 0x9C6234, 'm': 0x5E3A1C,
    'O': 0xFFC37A, 'o': 0xF08A26,
    'l': 0xECCF98,
}


class Canvas:
    def __init__(self):
        self.g = [['.'] * N for _ in range(N)]

    def get(self, x, y):
        return self.g[y][x] if 0 <= x < N and 0 <= y < N else '.'

    def set(self, x, y, c):
        if 0 <= x < N and 0 <= y < N:
            self.g[y][x] = c

    def rect(self, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.set(x, y, c)

    def disc(self, cx, cy, r, c):
        for y in range(N):
            for x in range(N):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                    self.set(x, y, c)

    def ring(self, cx, cy, r0, r1, c):
        for y in range(N):
            for x in range(N):
                d = math.hypot(x - cx, y - cy)
                if r0 <= d <= r1:
                    self.set(x, y, c)

    def line(self, x0, y0, x1, y1, c, thick=1):
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(steps + 1):
            x = round(x0 + (x1 - x0) * i / steps)
            y = round(y0 + (y1 - y0) * i / steps)
            for dx in range(thick):
                for dy in range(thick):
                    self.set(x + dx, y + dy, c)

    def poly(self, pts, c):
        for y in range(N):
            xs = []
            for i in range(len(pts)):
                (ax, ay), (bx, by) = pts[i], pts[(i + 1) % len(pts)]
                if (ay <= y + 0.5 < by) or (by <= y + 0.5 < ay):
                    xs.append(ax + (y + 0.5 - ay) * (bx - ax) / (by - ay))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                for x in range(math.ceil(xs[i] - 0.5), math.floor(xs[i + 1] - 0.5) + 1):
                    self.set(x, y, c)

    def bevel(self, base, light, dark):
        """Pixels of `base` that touch empty/other space on the top-left get `light`, bottom-right get `dark`."""
        out = [row[:] for row in self.g]
        for y in range(N):
            for x in range(N):
                if self.g[y][x] != base:
                    continue
                tl = self.get(x - 1, y) != base or self.get(x, y - 1) != base
                br = self.get(x + 1, y) != base or self.get(x, y + 1) != base
                if tl and not br:
                    out[y][x] = light
                elif br and not tl:
                    out[y][x] = dark
        self.g = out

    def outline(self, c='k'):
        out = [row[:] for row in self.g]
        for y in range(N):
            for x in range(N):
                if self.g[y][x] == '.':
                    if any(self.get(x + dx, y + dy) != '.' for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                        out[y][x] = c
        self.g = out

    def rows(self):
        return [''.join(r) for r in self.g]


# --------------------------------------------------------------------------- icons
def fps():
    c = Canvas()
    c.disc(7.5, 7.5, 6.4, 'b')
    c.bevel('b', 'B', 'd')
    c.disc(7.5, 7.5, 4.6, 'F')
    for (x, y) in ((3, 9), (3, 6), (5, 3), (8, 2), (11, 4), (12, 7)):
        c.set(x, y, 's')
    c.line(7, 8, 11, 4, 'r')
    c.set(7, 8, 'w')
    c.set(8, 8, 'w')
    c.rect(5, 11, 10, 11, 't')
    c.outline()
    return c


def ping():
    c = Canvas()
    for i, hgt in enumerate((4, 7, 10, 13)):
        x0 = 1 + i * 4
        c.rect(x0, 14 - hgt, x0 + 1, 13, 'g')
        c.rect(x0, 14 - hgt, x0 + 1, 14 - hgt, 'G')
        c.rect(x0 + 1, 15 - hgt, x0 + 1, 13, 'h')
        c.set(x0, 14 - hgt + 1, 'G')
    c.outline()
    return c


def tps():
    c = Canvas()
    c.poly([(10, 0.5), (2.5, 9), (7, 9), (4.5, 15.5), (13.5, 6), (9, 6), (12, 0.5)], 'y')
    c.bevel('y', 'Y', 'z')
    c.outline()
    return c


def cps():
    c = Canvas()
    c.rect(4, 3, 11, 14, 's')
    c.rect(5, 2, 10, 2, 's')
    c.set(4, 3, '.')
    c.set(11, 3, '.')
    c.bevel('s', 'S', 't')
    c.rect(8, 3, 10, 6, 'r')   # right button
    c.rect(8, 3, 8, 6, 'R')
    c.rect(5, 3, 7, 6, 'S')    # left button
    c.rect(7, 3, 7, 7, 'k')    # divider
    c.rect(5, 7, 10, 7, 'k')
    c.rect(7, 4, 7, 5, 'w')    # wheel
    c.outline()
    return c


def clock():
    c = Canvas()
    c.disc(7.5, 7.5, 6.5, 'y')
    c.bevel('y', 'Y', 'z')
    c.disc(7.5, 7.5, 4.8, 'b')
    c.ring(7.5, 7.5, 3.9, 4.8, 'd')
    c.rect(7, 4, 7, 7, 'w')
    c.rect(7, 7, 10, 7, 'w')
    c.set(7, 7, 'Y')
    for (x, y) in ((7, 3), (7, 12), (3, 7), (12, 7)):
        c.set(x, y, 'B')
    c.outline()
    return c


def day():
    c = Canvas()
    c.disc(7.5, 7.5, 3.9, 'y')
    c.bevel('y', 'Y', 'o')
    c.set(6, 6, 'w')
    for (x0, y0, x1, y1) in ((7, 0, 8, 1), (7, 14, 8, 15), (0, 7, 1, 8), (14, 7, 15, 8)):
        c.rect(x0, y0, x1, y1, 'Y')
    for (x, y) in ((2, 2), (3, 3), (12, 2), (11, 3), (2, 12), (3, 11), (12, 12), (11, 11)):
        c.set(x, y, 'O')
    c.outline()
    return c


def armor():
    c = Canvas()
    c.rect(3, 4, 12, 14, 'c')
    c.rect(0, 2, 4, 7, 'c')
    c.rect(11, 2, 15, 7, 'c')
    c.rect(5, 2, 10, 3, '.')           # neck
    c.rect(6, 4, 9, 4, '.')
    c.rect(4, 13, 11, 14, 'c')
    c.set(3, 14, '.')
    c.set(12, 14, '.')
    c.bevel('c', 'C', 'e')
    c.rect(7, 5, 8, 13, 'e')           # seam
    c.rect(5, 7, 6, 7, 'C')
    c.rect(9, 7, 10, 7, 'C')
    c.set(1, 3, 'w')
    c.set(5, 5, 'w')
    c.outline()
    return c


KEYS = {
    'W': ("x.x", "x.x", "x.x", ".x."),
    'A': (".x.", "x.x", "xxx", "x.x"),
    'S': (".xx", "x..", "..x", "xx."),
    'D': ("xx.", "x.x", "x.x", "xx."),
}


def keystrokes():
    c = Canvas()

    def key(x0, y0, ch):
        c.rect(x0, y0, x0 + 4, y0 + 5, 'k')
        c.rect(x0 + 1, y0 + 1, x0 + 3, y0 + 4, 'S')
        for j, row in enumerate(KEYS[ch]):
            for i, v in enumerate(row):
                if v == 'x':
                    c.set(x0 + 1 + i, y0 + 1 + j, 'k')
        c.rect(x0 + 1, y0 + 5, x0 + 3, y0 + 5, 't')

    key(5, 1, 'W')
    key(0, 7, 'A')
    key(5, 7, 'S')
    key(10, 7, 'D')
    return c


def waypoints():
    c = Canvas()
    c.poly([(2.5, 6), (7.5, 15.2), (12.5, 6)], 'r')
    c.disc(7.5, 5.5, 5.2, 'r')
    c.bevel('r', 'R', 'D')
    c.disc(7.5, 5.5, 1.9, 'w')
    c.set(7, 5, 'S')
    c.outline()
    return c


def bottle(kind):
    c = Canvas()
    c.rect(6, 1, 9, 4, 'S')            # neck (glass)
    c.disc(7.5, 10, 5.3, 'p')
    c.rect(5, 3, 10, 5, 'p') if kind == 'p' else None
    c.bevel('p', 'P', 'q')
    c.rect(6, 0, 9, 1, 'n')            # cork
    c.rect(6, 0, 6, 0, 'N')
    c.rect(4, 8, 11, 8, 'q')           # liquid line
    c.rect(5, 7, 10, 7, 'S')
    c.set(5, 10, 'w')
    c.set(5, 11, 'P')
    if kind == 'e':
        c.set(9, 11, 'w')              # sparkle
        c.set(8, 12, 'P')
        c.set(10, 12, 'P')
    else:
        c.set(8, 10, 'P')              # bubbles
        c.set(9, 12, 'P')
    c.outline()
    return c


def scoreboard():
    c = Canvas()
    c.rect(0, 1, 15, 14, 'b')
    c.bevel('b', 'B', 'd')
    c.rect(2, 3, 13, 12, 'F')
    c.rect(3, 4, 8, 4, 'w')
    c.rect(3, 7, 7, 7, 'w')
    c.rect(3, 10, 9, 10, 'w')
    c.rect(11, 4, 12, 4, 'y')
    c.rect(11, 7, 12, 7, 'y')
    c.rect(11, 10, 12, 10, 'y')
    c.outline()
    return c


def reach():
    c = Canvas()
    c.rect(0, 5, 15, 10, 'l')
    c.bevel('l', 'S', 'N')
    for x in range(1, 15, 2):
        c.rect(x, 5, x, 7 if x % 4 == 1 else 6, 'k')
    c.rect(1, 9, 14, 9, 'N')
    c.set(0, 5, '.')
    c.set(15, 10, '.')
    c.outline()
    return c


def rng():
    c = Canvas()
    c.ring(7.5, 7.5, 5.2, 6.6, 'c')
    c.bevel('c', 'C', 'e')
    c.rect(7, 0, 8, 4, 'r')
    c.rect(7, 11, 8, 15, 'r')
    c.rect(0, 7, 4, 8, 'r')
    c.rect(11, 7, 15, 8, 'r')
    c.rect(7, 7, 8, 8, 'w')
    c.outline()
    return c


def saturation():
    c = Canvas()
    c.line(8, 8, 13, 13, 'S', 2)       # bone
    c.rect(12, 14, 14, 14, 'S')
    c.rect(14, 12, 14, 14, 'S')
    c.disc(6, 6, 5.2, 'n')
    c.bevel('n', 'N', 'm')
    c.disc(5, 5, 2.2, 'N')
    c.set(4, 4, 'O')
    c.set(5, 4, 'O')
    c.outline()
    return c


def inventory():
    c = Canvas()
    c.rect(0, 0, 15, 15, 'b')
    c.bevel('b', 'B', 'd')
    for j in range(3):
        for i in range(3):
            x0, y0 = 1 + i * 5, 1 + j * 5
            c.rect(x0, y0, x0 + 3, y0 + 3, 'F')
            c.rect(x0, y0, x0 + 3, y0, 'k')
    c.set(7, 7, 'y')
    c.set(8, 8, 'z')
    c.set(2, 2, 'r')
    c.set(12, 12, 'g')
    return c


def totems():
    c = Canvas()
    c.rect(4, 1, 11, 8, 'y')           # head
    c.rect(2, 6, 3, 9, 'y')            # arms
    c.rect(12, 6, 13, 9, 'y')
    c.rect(5, 9, 10, 14, 'g')          # body
    c.bevel('y', 'Y', 'z')
    c.bevel('g', 'G', 'h')
    c.rect(5, 4, 6, 4, 'k')            # eyes
    c.rect(9, 4, 10, 4, 'k')
    c.rect(7, 6, 8, 6, 'z')            # mouth
    c.rect(4, 2, 11, 2, 'g')           # green crown stripe
    c.rect(7, 10, 8, 13, 'h')
    c.outline()
    return c


def zoom():
    c = Canvas()
    c.line(9, 9, 14, 14, 'n', 2)
    c.disc(6.5, 6.5, 5.6, 'b')
    c.bevel('b', 'B', 'd')
    c.disc(6.5, 6.5, 3.7, 'C')
    c.rect(4, 4, 5, 4, 'w')
    c.set(4, 5, 'w')
    c.outline()
    return c


def freecam():
    c = Canvas()
    c.rect(1, 4, 14, 13, 'b')
    c.rect(5, 2, 9, 3, 'b')
    c.bevel('b', 'B', 'd')
    c.disc(7.5, 8.5, 3.6, 'k')
    c.disc(7.5, 8.5, 2.6, 'C')
    c.set(6, 7, 'w')
    c.rect(11, 5, 12, 5, 'y')
    c.outline()
    return c


def fullbright():
    c = Canvas()
    c.disc(7.5, 7.5, 3.0, 'Y')
    c.bevel('Y', 'w', 'y')
    c.rect(7, 6, 8, 7, 'w')
    for (x0, y0, x1, y1) in ((7, 0, 8, 2), (7, 13, 8, 15), (0, 7, 2, 8), (13, 7, 15, 8)):
        c.rect(x0, y0, x1, y1, 'y')
    for (x, y) in ((2, 2), (3, 3), (12, 2), (11, 3), (2, 12), (3, 11), (12, 12), (11, 11)):
        c.set(x, y, 'O')
    for (x, y) in ((4, 1), (11, 1), (1, 4), (14, 4), (4, 14), (11, 14), (1, 11), (14, 11)):
        c.set(x, y, 'Y')
    c.outline()
    return c


def noblind():
    c = Canvas()
    c.poly([(0.5, 8), (4, 4), (8, 3), (12, 4), (15.5, 8), (12, 12), (8, 13), (4, 12)], 'S')
    c.bevel('S', 'w', 's')
    c.disc(7.5, 8, 2.8, 'b')
    c.disc(7.5, 8, 1.2, 'k')
    c.set(6, 7, 'w')
    c.outline()
    c.line(2, 14, 14, 2, 'k', 3)
    c.line(2, 14, 14, 2, 'r', 2)
    c.line(2, 14, 13, 3, 'R', 1)
    return c


def tiers():
    c = Canvas()
    c.rect(4, 1, 11, 5, 'y')
    c.rect(5, 6, 10, 6, 'y')
    c.rect(6, 7, 9, 7, 'y')
    c.ring(3.5, 3.5, 1.4, 2.4, 'z')    # handles
    c.ring(11.5, 3.5, 1.4, 2.4, 'z')
    c.rect(7, 8, 8, 11, 'z')
    c.rect(4, 12, 11, 14, 'z')
    c.bevel('y', 'Y', 'z')
    c.rect(5, 12, 10, 12, 'y')
    c.set(6, 3, 'w')
    c.set(7, 2, 'w')
    c.set(7, 4, 'w')
    c.set(8, 3, 'w')
    c.outline()
    return c


def shulker():
    c = Canvas()
    c.rect(0, 5, 11, 15, 'q')
    c.rect(0, 5, 11, 9, 'p')
    c.bevel('p', 'P', 'q')
    c.rect(0, 9, 11, 9, 'q')
    c.rect(5, 8, 6, 10, 'y')           # latch
    c.outline()
    c.rect(8, 0, 15, 5, 'k')           # tooltip panel
    c.rect(9, 1, 14, 4, 'F')
    c.rect(9, 1, 14, 1, 'P')
    c.rect(10, 3, 12, 3, 'w')
    return c


def crosshair():
    c = Canvas()
    for (x0, y0, dx, dy) in ((0, 0, 1, 1), (15, 0, -1, 1), (0, 15, 1, -1), (15, 15, -1, -1)):
        for i in range(4):
            c.set(x0 + dx * i, y0, 'c')
            c.set(x0, y0 + dy * i, 'c')
        c.set(x0 + dx, y0 + dy, 'C')
    c.rect(7, 4, 8, 6, 'c')
    c.rect(7, 9, 8, 11, 'c')
    c.rect(4, 7, 6, 8, 'c')
    c.rect(9, 7, 11, 8, 'c')
    c.rect(7, 7, 8, 8, 'w')
    c.outline()
    return c


ICONS = {
    'fps': fps, 'ping': ping, 'tps': tps, 'cps': cps, 'clock': clock, 'day': day, 'armor': armor,
    'keystrokes': keystrokes, 'waypoints': waypoints, 'effects': lambda: bottle('e'),
    'scoreboard': scoreboard, 'reach': reach, 'range': rng, 'saturation': saturation,
    'inventory': inventory, 'totems': totems, 'potions': lambda: bottle('p'), 'zoom': zoom,
    'freecam': freecam, 'fullbright': fullbright, 'noblind': noblind, 'tiers': tiers,
    'shulker': shulker, 'crosshair': crosshair,
}


def write_java(path):
    lines = ["package client.confis;", "",
             "/** GENERATED by tools/gen_icons.py - do not edit by hand. 16x16 shaded pixel icons as character grids. */",
             "final class IconData {", "    private IconData() {}", "",
             "    /** character -> 0xRRGGBB */",
             "    static final String PALETTE = \"" + ''.join(f"{k}{v:06X}" for k, v in PAL.items()) + "\";", "",
             "    static final String[] IDS = {" + ", ".join(f'"{k}"' for k in ICONS) + "};", "",
             "    static final String[][] ROWS = {"]
    for k, fn in ICONS.items():
        rows = fn().rows()
        lines.append("        {" + ", ".join(f'"{r}"' for r in rows) + "},  // " + k)
    lines += ["    };", "}", ""]
    with open(path, 'w') as f:
        f.write("\n".join(lines))


def preview(path, scale=10):
    from PIL import Image
    cols = 6
    names = list(ICONS)
    rows = (len(names) + cols - 1) // cols
    cell = N * scale + 16
    for bg_name, bg in (('dark', (24, 60, 110)), ('light', (225, 232, 240))):
        img = Image.new('RGB', (cols * cell, rows * cell), bg)
        for idx, k in enumerate(names):
            cv = ICONS[k]()
            ox, oy = (idx % cols) * cell + 8, (idx // cols) * cell + 8
            for y in range(N):
                for x in range(N):
                    ch = cv.g[y][x]
                    if ch != '.':
                        rgb = PAL[ch]
                        col = ((rgb >> 16) & 255, (rgb >> 8) & 255, rgb & 255)
                        for yy in range(scale):
                            for xx in range(scale):
                                img.putpixel((ox + x * scale + xx, oy + y * scale + yy), col)
        img.save(path.replace('.png', f'_{bg_name}.png'))


if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    write_java(os.path.join(here, '..', 'intermediary-src', 'client', 'confis', 'IconData.java'))
    if len(sys.argv) > 1:
        preview(sys.argv[1])
    print("wrote IconData.java with", len(ICONS), "icons")
