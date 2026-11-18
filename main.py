#!/usr/bin/env python3
"""Draw a 1024x1024 newspaper front page summing up the world news of
Wednesday 18 November 2026, and write it as entry.png.

Pure Python 3.13 standard library. No network, no files read, no time or
randomness: two runs write identical bytes.
"""
import binascii
import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (247, 243, 232)
INK = (20, 20, 20)
RED = (178, 34, 34)
BLUE = (31, 78, 121)
TEAL = (14, 110, 110)
GOLD = (176, 124, 18)
SLATE = (84, 84, 84)
RULE = (180, 172, 152)
PANEL_BG = (255, 252, 244)
WHITE = (255, 255, 255)

# ---------------------------------------------------------------- font
# 5x7 bitmap glyphs, rows top to bottom, '#' = on, '.' = off.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
}


def char_width(scale):
    return 6 * scale


def text_width(text, scale):
    return len(text) * char_width(scale) - scale


def wrap_text(text, scale, max_width):
    """Greedy word wrap. Returns a list of lines that fit max_width."""
    words = text.split(" ")
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if text_width(trial, scale) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def set_pixel(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = color[0]
            self.px[i + 1] = color[1]
            self.px[i + 2] = color[2]

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i] = color[0]
                self.px[i + 1] = color[1]
                self.px[i + 2] = color[2]

    def hline(self, x, y, w, color, thick=1):
        self.fill_rect(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.fill_rect(x, y, thick, h, color)

    def line(self, x0, y0, x1, y1, color):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set_pixel(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def fill_circle(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy) <= r * r:
                    self.set_pixel(xx, yy, color)

    def ring(self, cx, cy, r, color, thick=3):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy)
                if (r - thick) * (r - thick) <= d <= r * r:
                    self.set_pixel(xx, yy, color)

    def fill_triangle(self, x0, y0, x1, y1, x2, y2, color):
        min_y = min(y0, y1, y2)
        max_y = max(y0, y1, y2)
        for yy in range(min_y, max_y + 1):
            xs = []
            for ax, ay, bx, by in ((x0, y0, x1, y1), (x1, y1, x2, y2), (x2, y2, x0, y0)):
                if ay == by:
                    continue
                if min(ay, by) <= yy < max(ay, by):
                    t = (yy - ay) / (by - ay)
                    xs.append(ax + t * (bx - ax))
            if len(xs) >= 2:
                xa = int(min(xs))
                xb = int(max(xs))
                self.fill_rect(xa, yy, xb - xa + 1, 1, color)

    def draw_char(self, ch, x, y, scale, color):
        glyph = FONT.get(ch, FONT["?"])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "1":
                    self.fill_rect(x + col * scale, y + row * scale,
                                   scale, scale, color)

    def draw_text(self, text, x, y, scale, color):
        cx = x
        for ch in text:
            self.draw_char(ch, cx, y, scale, color)
            cx += char_width(scale)
        return cx

    def draw_text_centered(self, text, cx, y, scale, color):
        x = cx - text_width(text, scale) // 2
        self.draw_text(text, x, y, scale, color)
        return x


# ---------------------------------------------------------------- icons
def icon_burst(c, cx, cy, color):
    c.fill_circle(cx, cy, 12, color)
    for k in range(8):
        ang = k * 3.14159 / 4.0
        x1 = cx + int(16 * _cos(ang))
        y1 = cy + int(16 * _sin(ang))
        x2 = cx + int(28 * _cos(ang))
        y2 = cy + int(28 * _sin(ang))
        c.line(x1, y1, x2, y2, color)
        c.line(x1 + 1, y1, x2 + 1, y2, color)


def _cos(a):
    # cosine by Taylor around 0..2pi via the standard series on reduced angle
    while a > 3.14159:
        a -= 6.28318
    while a < -3.14159:
        a += 6.28318
    return 1 - a * a / 2 + a ** 4 / 24 - a ** 6 / 720


def _sin(a):
    while a > 3.14159:
        a -= 6.28318
    while a < -3.14159:
        a += 6.28318
    return a - a ** 3 / 6 + a ** 5 / 120 - a ** 7 / 5040


def icon_rocket(c, cx, cy, color):
    c.fill_triangle(cx, cy - 26, cx - 12, cy + 6, cx + 12, cy + 6, color)
    c.fill_rect(cx - 12, cy + 4, 24, 18, color)
    c.fill_triangle(cx - 12, cy + 8, cx - 24, cy + 24, cx - 12, cy + 22, color)
    c.fill_triangle(cx + 12, cy + 8, cx + 24, cy + 24, cx + 12, cy + 22, color)
    c.fill_triangle(cx - 5, cy + 22, cx + 5, cy + 22, cx, cy + 34, GOLD)


def icon_cross(c, cx, cy, color):
    c.ring(cx, cy, 28, color, 4)
    c.fill_rect(cx - 5, cy - 16, 10, 32, color)
    c.fill_rect(cx - 16, cy - 5, 32, 10, color)


def icon_ballot(c, cx, cy, color):
    c.fill_rect(cx - 22, cy - 8, 44, 34, color)
    c.fill_rect(cx - 26, cy - 16, 52, 10, INK)
    c.fill_rect(cx - 8, cy - 13, 16, 4, PAPER)
    c.line(cx - 14, cy - 30, cx - 4, cy - 20, RED)
    c.line(cx - 4, cy - 20, cx + 16, cy - 40, RED)
    c.line(cx - 14, cy - 29, cx - 4, cy - 19, RED)
    c.line(cx - 4, cy - 19, cx + 16, cy - 39, RED)


def icon_virus(c, cx, cy, color):
    c.fill_circle(cx, cy, 14, color)
    for k in range(8):
        ang = k * 3.14159 / 4.0
        x1 = cx + int(15 * _cos(ang))
        y1 = cy + int(15 * _sin(ang))
        x2 = cx + int(26 * _cos(ang))
        y2 = cy + int(26 * _sin(ang))
        c.line(x1, y1, x2, y2, color)
        c.fill_circle(x2, y2, 3, color)


def icon_plane(c, cx, cy, color):
    c.fill_rect(cx - 28, cy - 4, 56, 8, color)
    c.fill_triangle(cx - 4, cy - 4, cx + 8, cy - 20, cx + 14, cy - 4, color)
    c.fill_triangle(cx - 10, cy + 4, cx - 2, cy + 18, cx + 4, cy + 4, color)
    c.fill_triangle(cx + 20, cy - 4, cx + 30, cy - 14, cx + 30, cy - 4, color)
    c.fill_triangle(cx + 20, cy + 4, cx + 30, cy + 14, cx + 30, cy + 4, color)


ICONS = (icon_burst, icon_rocket, icon_cross, icon_ballot, icon_virus, icon_plane)

# ---------------------------------------------------------------- content
PANELS = (
    ("MIDDLE EAST", RED, "IRAN STRIKES KUWAIT AND BAHRAIN",
     "US BASES HIT AFTER THE US STRUCK AN IRGC MISSILE SITE ON QESHM ISLAND ON 17 NOV."),
    ("SPACE", BLUE, "VOYAGER 1 REACHES ONE LIGHT-DAY",
     "FIRST HUMAN-MADE OBJECT TO DO SO, 16 BILLION MILES OUT, AT 5:16 AM ET."),
    ("HEALTH - USA", TEAL, "US LOSES MEASLES-FREE STATUS",
     "5,412 CASES IN 2026, 10 DEATHS, THE HIGHEST ANNUAL TOTAL SINCE 1991, AFTER 26 YEARS."),
    ("US POLITICS", BLUE, "PELTOLA WINS ALASKA SENATE RACE",
     "DEMOCRATS TAKE A 56-44 MAJORITY IN THE SENATE."),
    ("HEALTH - AFRICA", TEAL, "EBOLA IN CONGO PASSES 11,000 CASES",
     "SECOND-LARGEST OUTBREAK ON RECORD, CHILDREN HIT HARDEST."),
    ("RUSSIA", RED, "RUSSIAN MILITARY PLANE CRASHES",
     "19 DEAD IN SIBERIA, IN THE KEMEROVO REGION."),
)

FOOTER = (
    "KNESSET ELECTS MATAN KAHANA SPEAKER, A SETBACK FOR NETANYAHU",
    "XI RECEIVES PUTIN IN SHENZHEN AT APEC",
    "6.0-MAGNITUDE QUAKE HITS PAPUA NEW GUINEA",
    "146,000 PROTEST ACROSS FRANCE OVER LIVING COSTS",
    "NVIDIA REPORTS RECORD QUARTERLY REVENUE",
)


def draw_panel(c, x, y, w, h, number, kicker, accent, headline, sub):
    c.fill_rect(x, y, w, h, PANEL_BG)
    c.hline(x, y, w, accent, 6)
    # number badge
    c.fill_circle(x + 34, y + 36, 20, accent)
    c.draw_text_centered(str(number), x + 34, y + 27, 2, WHITE)
    # kicker
    c.draw_text(kicker, x + 64, y + 28, 2, accent)
    # icon at right of headline zone
    ICONS[number - 1](c, x + w - 46, y + 62, accent)
    # headline, wrapped, leaving room for the icon
    lines = wrap_text(headline, 3, w - 64 - 96)
    ly = y + 62
    for line in lines:
        c.draw_text(line, x + 24, ly, 3, INK)
        ly += 28
    c.hline(x + 24, ly + 4, w - 48, RULE, 2)
    # sub text
    sub_lines = wrap_text(sub, 2, w - 48)
    sy = ly + 16
    for line in sub_lines:
        c.draw_text(line, x + 24, sy, 2, SLATE)
        sy += 18


def draw_page():
    c = Canvas(W, H, PAPER)
    # ---- header
    c.fill_rect(0, 0, W, 118, INK)
    c.draw_text_centered("WEDNESDAY 18 NOVEMBER 2026", W // 2, 22, 4, WHITE)
    c.hline(72, 62, W - 144, RED, 3)
    c.draw_text_centered("THE WORLD IN ONE DAY", W // 2, 76, 3, (232, 196, 120))
    # ---- panels: 2 columns x 3 rows
    margin = 24
    gap = 16
    pw = (W - margin * 2 - gap) // 2
    ph = 240
    top = 134
    for i, (kicker, accent, headline, sub) in enumerate(PANELS):
        px = margin + (i % 2) * (pw + gap)
        py = top + (i // 2) * (ph + 12)
        draw_panel(c, px, py, pw, ph, i + 1, kicker, accent, headline, sub)
    # ---- footer
    fy = 892
    c.fill_rect(0, fy, W, H - fy, INK)
    c.draw_text("ALSO TODAY", 24, fy + 18, 2, (232, 196, 120))
    c.hline(24, fy + 40, W - 48, RED, 2)
    yy = fy + 50
    for item in FOOTER:
        c.fill_rect(24, yy + 4, 8, 8, RED)
        c.draw_text(item, 44, yy, 2, WHITE)
        yy += 16
    return c


# ---------------------------------------------------------------- png
def chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", binascii.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png(c):
    raw = bytearray()
    stride = W * 3
    for y in range(H):
        raw.append(0)
        raw += c.px[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    return png


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    png = encode_png(draw_page())
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(png)


if __name__ == "__main__":
    main()
