#!/usr/bin/env python3
"""NI24 — Tuesday 24 November 2026 in one page. Fresh render, PIL only.

Draws entry.png (1024x1024, deterministic) from scratch: a header naming
the day and the story count, a big data strip, 3 lead panels with
hand-drawn pictograms, 8 illustrated mid panels, a world map with 10
numbered hotspots, 2 charts built from the day's real numbers, a numbered
list of the remaining 28 stories, and a footer with region coverage and
a date check. No network, no random values, no timestamps in the output —
two runs of this script write byte-identical PNGs.

Layout (1024x1024, 16px side margins):
  header 8-56 | data strip 62-100 | leads 108-290 | mids 298-506
  map + charts 514-706 | list title 712-732 | list 736-988 | footer 992-1018
"""
import hashlib
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

PAPER = (247, 243, 234)
CARD = (255, 255, 255)
INK = (24, 24, 24)
MUTED = (92, 88, 80)
LINE = (198, 190, 174)
RED = (178, 34, 34)
BLUE = (31, 78, 121)
GOLD = (176, 124, 24)
GREEN = (34, 120, 70)
ORANGE = (204, 102, 0)
MAP_BG = (232, 238, 242)
MAP_LAND = (198, 206, 192)
MAP_LINE = (118, 128, 118)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(size, bold=False, serif=False):
    if serif:
        path = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf" if bold else "DejaVuSerif.ttf")
    else:
        path = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf")
    return ImageFont.truetype(path, size)


# --- layout bookkeeping: every text box is recorded, then validated ---
BOXES = []  # (x0, y0, x1, y1, label)


def text(d, xy, s, f, fill=INK, anchor="la"):
    bb = d.textbbox(xy, s, font=f, anchor=anchor)
    BOXES.append((bb[0], bb[1], bb[2], bb[3], s[:28]))
    d.text(xy, s, font=f, fill=fill, anchor=anchor)
    return bb


def wrap(s, f, max_w):
    lines, cur = [], ""
    for w in s.split():
        t = (cur + " " + w).strip()
        if f.getlength(t) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def para(d, x, y, s, f, max_w, fill=INK, lh=None):
    if lh is None:
        lh = int(f.size * 1.3)
    yy = y
    for ln in wrap(s, f, max_w):
        text(d, (x, yy), ln, f, fill=fill)
        yy += lh
    return yy


def panel(d, x, y, w, h, top=None):
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=LINE, width=1)
    if top is not None:
        d.rectangle([x, y, x + w, y + 4], fill=top)


# --- hand-drawn pictograms (all primitives, drawn inside box x,y,s) ---
def icon_chip(d, x, y, s):
    c = BLUE
    step = (s - 20) // 3
    for i in range(4):
        px = x + 10 + i * step
        d.line([px, y + 2, px, y + 10], fill=c, width=2)
        d.line([px, y + s - 10, px, y + s - 2], fill=c, width=2)
        py = y + 10 + i * step
        d.line([x + 2, py, x + 10, py], fill=c, width=2)
        d.line([x + s - 10, py, x + s - 2, py], fill=c, width=2)
    d.rectangle([x + 10, y + 10, x + s - 10, y + s - 10], outline=c, width=3)
    d.rectangle([x + s // 2 - 8, y + s // 2 - 8, x + s // 2 + 8, y + s // 2 + 8], fill=GOLD)
    # rising arrow, bottom-left to top-right
    ax, ay = x + s - 30, y + s - 18
    bx, by = x + s - 12, y + s - 36
    d.line([ax, ay, bx, by], fill=GREEN, width=3)
    d.line([bx, by, bx - 8, by + 1], fill=GREEN, width=3)
    d.line([bx, by, bx + 1, by + 8], fill=GREEN, width=3)


def icon_city_dark(d, x, y, s):
    c = INK
    # three buildings, middle one dark with no lit windows
    d.rectangle([x + 4, y + s - 34, x + 22, y + s - 4], fill=(70, 70, 78))
    d.rectangle([x + 26, y + s - 52, x + 48, y + s - 4], fill=(40, 40, 48))
    d.rectangle([x + 52, y + s - 28, x + 68, y + s - 4], fill=(70, 70, 78))
    for wx in (8, 14):
        for wy in (y + s - 28, y + s - 18):
            d.rectangle([x + wx, wy, x + wx + 3, wy + 3], fill=GOLD)
    for wx in (56, 62):
        d.rectangle([x + wx, y + s - 20, x + wx + 3, y + s - 17], fill=GOLD)
    # snowflake top-right
    cx, cy = x + s - 14, y + 14
    for ang in (0, 60, 120):
        import math
        r = math.radians(ang)
        dx, dy = 9 * math.cos(r), 9 * math.sin(r)
        d.line([cx - dx, cy - dy, cx + dx, cy + dy], fill=BLUE, width=2)


def icon_ships(d, x, y, s):
    # island + three warships circling it (dashed ring)
    d.ellipse([x + s // 2 - 12, y + s // 2 - 6, x + s // 2 + 12, y + s // 2 + 10], fill=GREEN)
    d.ellipse([x + 4, y + 4, x + s - 4, y + s - 4], outline=RED, width=2)
    for (sx, sy, sc) in ((x + 10, y + s - 22, 1), (x + s - 26, y + 12, -1), (x + s // 2 - 4, y + s - 12, 1)):
        d.polygon([(sx, sy + 6), (sx + 16, sy + 6), (sx + 13, sy), (sx + 3, sy)], fill=INK)
        d.line([sx + 8, sy, sx + 8, sy - 7], fill=INK, width=2)


def icon_plane(d, x, y, s):
    c = BLUE
    # side profile: fuselage, wing, tail, grounded (no motion lines)
    d.polygon([(x + 6, y + s // 2), (x + s - 14, y + s // 2 - 8),
               (x + s - 6, y + s // 2 - 4), (x + s - 6, y + s // 2 + 2),
               (x + 10, y + s // 2 + 6)], fill=c)
    d.polygon([(x + s // 2 - 4, y + s // 2 - 2), (x + s // 2 + 10, y + s // 2 + 8),
               (x + s // 2 + 2, y + s // 2 + 8)], fill=c)
    d.polygon([(x + 8, y + s // 2), (x + 16, y + s // 2 - 12),
               (x + 20, y + s // 2 - 12), (x + 16, y + s // 2)], fill=c)
    d.line([x + 6, y + s - 8, x + s - 6, y + s - 8], fill=RED, width=3)


def icon_flame_factory(d, x, y, s):
    # refinery: two chimneys + flame
    d.rectangle([x + 8, y + s - 30, x + 20, y + s - 6], fill=INK)
    d.rectangle([x + 24, y + s - 22, x + 40, y + s - 6], fill=INK)
    d.rectangle([x + 6, y + s - 34, x + 22, y + s - 30], fill=INK)
    d.polygon([(x + 30, y + 6), (x + 38, y + 20), (x + 34, y + 26),
               (x + 26, y + 26), (x + 22, y + 20)], fill=ORANGE)
    d.polygon([(x + 30, y + 14), (x + 34, y + 22), (x + 26, y + 22)], fill=RED)


def icon_derrick(d, x, y, s):
    # oil derrick frame + flame at the top
    d.line([x + 8, y + s - 6, x + s // 2, y + 10], fill=INK, width=3)
    d.line([x + s - 8, y + s - 6, x + s // 2, y + 10], fill=INK, width=3)
    d.line([x + 14, y + s - 16, x + s - 14, y + s - 16], fill=INK, width=2)
    d.line([x + 18, y + s - 26, x + s - 18, y + s - 26], fill=INK, width=2)
    d.polygon([(x + s // 2, y + 2), (x + s // 2 + 5, y + 10),
               (x + s // 2 - 5, y + 10)], fill=ORANGE)


def icon_govt(d, x, y, s):
    # government building with columns + flag
    d.rectangle([x + 6, y + s - 10, x + s - 6, y + s - 6], fill=INK)
    d.polygon([(x + 4, y + s - 26), (x + s // 2, y + s - 40),
               (x + s - 4, y + s - 26)], fill=BLUE)
    for i in range(4):
        cx = x + 12 + i * ((s - 24) // 3)
        d.rectangle([cx, y + s - 26, cx + 3, y + s - 10], fill=INK)
    d.line([x + s // 2, y + s - 40, x + s // 2, y + 8], fill=INK, width=2)
    d.polygon([(x + s // 2, y + 8), (x + s // 2 + 12, y + 12),
               (x + s // 2, y + 16)], fill=RED)


def icon_boat(d, x, y, s):
    # small boat on waves
    d.polygon([(x + 6, y + s // 2), (x + s - 6, y + s // 2),
               (x + s - 12, y + s // 2 + 10), (x + 12, y + s // 2 + 10)], fill=INK)
    d.line([x + s // 2, y + s // 2, x + s // 2, y + 8], fill=INK, width=2)
    d.polygon([(x + s // 2, y + 8), (x + s // 2 + 12, y + s // 2 - 2),
               (x + s // 2, y + s // 2 - 2)], fill=RED)
    for wy in (y + s - 12, y + s - 6):
        for wx in range(6, s - 6, 12):
            d.arc([x + wx, wy, x + wx + 10, wy + 8], 0, 180, fill=BLUE, width=2)


def icon_moon(d, x, y, s):
    d.ellipse([x + 8, y + 8, x + s - 8, y + s - 8], fill=(232, 200, 120), outline=GOLD, width=2)
    d.ellipse([x + 16, y + 16, x + 22, y + 22], fill=(210, 175, 95))
    d.ellipse([x + s - 26, y + s - 24, x + s - 18, y + s - 16], fill=(210, 175, 95))
    for (sx, sy) in ((x + 4, y + 6), (x + s - 8, y + 10), (x + 6, y + s - 10)):
        d.line([sx - 2, sy, sx + 2, sy], fill=GOLD, width=2)
        d.line([sx, sy - 2, sx, sy + 2], fill=GOLD, width=2)


def icon_badge(d, x, y, s):
    # shield badge
    d.polygon([(x + s // 2, y + 4), (x + s - 6, y + 12), (x + s - 6, y + s // 2 + 4),
               (x + s // 2, y + s - 4), (x + 6, y + s // 2 + 4), (x + 6, y + 12)],
              fill=BLUE, outline=INK)
    d.line([x + s // 2 - 8, y + s // 2, x + s // 2 - 2, y + s // 2 + 8], fill=CARD, width=3)
    d.line([x + s // 2 - 2, y + s // 2 + 8, x + s // 2 + 10, y + s // 2 - 8], fill=CARD, width=3)


def icon_stadium(d, x, y, s):
    # stadium bowl + floodlights
    d.arc([x + 4, y + 10, x + s - 4, y + s - 6], 0, 180, fill=INK, width=3)
    d.line([x + 4, y + s // 2 + 4, x + s - 4, y + s // 2 + 4], fill=INK, width=2)
    for fx in (x + 8, x + s - 12):
        d.line([fx, y + 6, fx, y + 16], fill=INK, width=2)
        d.ellipse([fx - 3, y + 2, fx + 3, y + 8], fill=GOLD)
    d.rectangle([x + s // 2 - 10, y + s - 12, x + s // 2 + 10, y + s - 8], fill=GREEN)


# --- world map: simplified continents in (lon, lat) ---
NA = [(-168, 66), (-150, 70), (-135, 69), (-125, 71), (-115, 68), (-105, 68),
      (-95, 69), (-85, 66), (-80, 73), (-70, 68), (-60, 60), (-55, 52),
      (-60, 47), (-65, 44), (-70, 42), (-74, 39), (-76, 35), (-80, 32),
      (-81, 26), (-84, 30), (-85, 20), (-90, 14), (-95, 16), (-97, 16),
      (-105, 20), (-110, 24), (-115, 30), (-120, 34), (-124, 42), (-125, 48),
      (-130, 55), (-140, 60), (-150, 61), (-160, 58), (-165, 60), (-168, 66)]
SA = [(-79, 9), (-77, 4), (-75, 0), (-70, -5), (-60, -8), (-50, -5),
      (-40, -10), (-35, -18), (-38, -25), (-48, -28), (-55, -35), (-65, -41),
      (-68, -50), (-70, -54), (-73, -45), (-73, -35), (-72, -25), (-75, -15),
      (-80, -8), (-81, 0), (-80, 6), (-79, 9)]
EU = [(-9, 37), (-9, 43), (-2, 48), (0, 50), (3, 52), (7, 54), (8, 57),
      (12, 56), (18, 56), (21, 58), (24, 60), (28, 62), (30, 66), (32, 70),
      (38, 68), (44, 67), (48, 62), (44, 55), (40, 50), (38, 46), (34, 45),
      (30, 44), (28, 41), (26, 38), (23, 37), (20, 40), (16, 42), (12, 44),
      (8, 44), (3, 42), (0, 39), (-2, 37), (-6, 36), (-9, 37)]
AF = [(-6, 35), (-10, 31), (-15, 27), (-17, 21), (-16, 15), (-12, 8),
      (-8, 5), (-4, 5), (0, 6), (6, 4), (9, 0), (9, -5), (12, -10),
      (13, -18), (14, -25), (16, -30), (18, -34), (20, -35), (26, -34),
      (31, -29), (33, -26), (36, -22), (39, -18), (40, -12), (42, -5),
      (45, 0), (48, 5), (51, 10), (48, 12), (44, 14), (40, 18), (38, 22),
      (35, 28), (32, 31), (28, 32), (22, 33), (15, 35), (10, 37), (5, 37),
      (0, 36), (-6, 35)]
AS = [(38, 68), (42, 70), (48, 70), (55, 71), (62, 70), (68, 72), (75, 73),
      (82, 73), (90, 75), (98, 76), (105, 77), (112, 76), (120, 73), (128, 71),
      (135, 72), (142, 71), (150, 70), (158, 69), (165, 66), (170, 67),
      (178, 65), (172, 62), (165, 60), (160, 55), (158, 50), (155, 45),
      (150, 42), (145, 40), (142, 38), (138, 35), (134, 33), (130, 31),
      (127, 30), (124, 28), (121, 25), (118, 22), (114, 21), (110, 18),
      (108, 12), (106, 9), (103, 6), (100, 7), (98, 10), (96, 15), (94, 18),
      (92, 21), (90, 22), (88, 24), (86, 20), (83, 17), (80, 13), (78, 8),
      (76, 10), (74, 15), (72, 20), (70, 23), (68, 25), (65, 25), (62, 26),
      (58, 26), (56, 26), (54, 27), (52, 28), (50, 29), (48, 30), (46, 29),
      (44, 28), (42, 25), (40, 22), (39, 21), (38, 24), (37, 28), (36, 32),
      (36, 36), (38, 40), (40, 44), (42, 48), (44, 52), (46, 56), (44, 60),
      (42, 64), (40, 66), (38, 68)]
AU = [(113, -22), (114, -28), (115, -33), (118, -35), (122, -34), (126, -32),
      (129, -32), (132, -32), (135, -35), (138, -35), (140, -38), (144, -39),
      (147, -39), (150, -37), (152, -34), (153, -30), (153, -27), (150, -23),
      (147, -19), (144, -15), (142, -11), (140, -14), (137, -12), (135, -15),
      (132, -12), (129, -14), (126, -14), (123, -17), (120, -20), (117, -20),
      (113, -22)]
JP = [(130, 31), (132, 33), (134, 34), (136, 35), (138, 36), (140, 37),
      (141, 39), (141, 42), (142, 44), (140, 44), (139, 41), (137, 38),
      (135, 34), (132, 32), (130, 31)]
NZ = [(167, -45), (170, -43), (173, -41), (175, -38), (177, -38),
      (175, -40), (172, -43), (169, -46), (167, -45)]
CONTINENTS = [NA, SA, EU, AF, AS, AU, JP, NZ]


def proj(lon, lat, mx, my, mw, mh):
    x = mx + (lon + 170.0) / 360.0 * mw
    y = my + (84.0 - lat) / 142.0 * mh
    return (x, y)


# --- content: all 39 stories dated Tuesday 24 November 2026 ---
LEADS = [
    ("NORTH AMERICA", "MARKETS", "REPORTED",
     "Huang is back, Nvidia soars 36.6%.",
     "Board reinstates Huang as chief executive; Wall Street "
     "rebounds as the AI rout reverses.", icon_chip, RED),
    ("EUROPE", "UKRAINE", "REPORTED",
     "Odesa dark and cold after Russian strikes.",
     "Strikes knock out power, heat and water across the Black Sea "
     "port city.", icon_city_dark, BLUE),
    ("ASIA-PACIFIC", "TAIWAN", "REPORTED",
     "12 Chinese warships circle Taiwan.",
     "Drones and helicopters enter the island's air-defence zone as "
     "Taipei tracks the flotilla.", icon_ships, GOLD),
]

MIDS = [
    ("NORTH AMERICA", "Delta outage grounds 3,000+ US flights",
     "System failure hits key US hubs.", "m.autoys.eu", icon_plane),
    ("EUROPE", "Ukraine drones set two Russian refineries ablaze",
     "Fires at Perm and Rostov plants.", "Geopolitiki live", icon_flame_factory),
    ("MIDDLE EAST", "Houthis say they hit Saudi Arabia's Rabigh refinery",
     "Houthi claim; Riyadh silent so far.", "Geopolitiki live", icon_derrick),
    ("ASIA-PACIFIC", "Seoul names new foreign minister and spy chief",
     "Reshuffle amid US alliance worries.", "m.autoys.eu", icon_govt),
    ("AFRICA", "24 dead as boat capsizes on way to a Nigeria funeral",
     "Boat overturns en route to the ceremony.", "m.autoys.eu", icon_boat),
    ("GLOBAL", "Beaver Supermoon rises tonight, first of four",
     "First of four supermoons to February 2027.", "Sky at Night", icon_moon),
    ("LATIN AMERICA", "16 cartel suspects killed in 'El Chapo Isidro' arrest",
     "Mexico reports 16 killed in the raid.", "m.autoys.eu", icon_badge),
    ("OCEANIA", "Hobart stadium bill jumps to $1.23 billion",
     "Macquarie Point cost hits $1.23bn.", "Go Herald Now", icon_stadium),
]

LIST = [
    "Armenia drops Karabakh claim in draft constitution",
    "Cyprus expels two Russian diplomats over spying claims",
    "Estonia answers Russia's airspace allegation firmly",
    "Bomb threats close schools in Germany and Denmark",
    "Merz: keeping Ukraine out of NATO in 2008 was wrong",
    "UK starts world's largest AI breast-screening trial",
    "NATO offers Poland 'significant backing' after incursion",
    "Russian casualties outpace monthly recruiting, US says",
    "Two killed as helicopter crashes near Napa wineries",
    "US states sue SpaceX over Grok's sexual images",
    "Army invokes emergency powers for Iowa munitions blast",
    "US to host the 2031 Women's World Cup, FIFA says",
    "Schumer warns of security risks in Huang's return",
    "Panama and First Quantum resume Cobre mine talks",
    "Storm forces thousands to flee in Brazil",
    "Gaza's soil and water poisoned by war, report finds",
    "France condemns settler attacks on Palestinians",
    "Lebanon condemns Israeli officer's school visit",
    "Trump faces pivotal decision on Iran deal",
    "Eastern Libya appeals to UN over Russian warship",
    "Fighting traps Ebola responders in Ituri",
    "Seoul denies navy unit is bound for Iran war",
    "Taiwan eases margin rules from today after rout",
    "South Korea tracks North Korean ship off its coast",
    "Taliban erases women's names from Balkh documents",
    "Australia budget update as rents hit 14-year low",
    "UN chief urges global AI safety rules within a year",
    "China's nuclear build-up 'turning world dangerous', expert warns",
]

# (number, lon, lat) — 1 Odesa, 2 Taiwan, 3 Atlanta, 4 Perm, 5 Rabigh,
# 6 Nigeria, 7 Sinaloa, 8 Hobart, 9 Seoul, 10 Vanuatu
HOTSPOTS = [(1, 30.7, 46.5), (2, 121.0, 23.5), (3, -84.4, 33.7),
            (4, 56.3, 58.0), (5, 39.0, 22.8), (6, 8.0, 9.0),
            (7, -107.0, 25.0), (8, 147.3, -42.9), (9, 127.0, 37.5),
            (10, 167.0, -16.0)]

FALLS = [("Taiwan", "-6.7%"), ("S. Korea", "-5.2%"), ("Nikkei", "-5.0%"),
         ("Shanghai", "-2.1%"), ("ASX", "-1.6%")]
FALLS_VAL = [6.7, 5.2, 5.0, 2.1, 1.6]
TREMORS = [("Vanuatu", "6.5"), ("Timor-Leste", "5.4"), ("Urumqi", "5.1"),
           ("Kuqa", "4.9"), ("Palau", "4.8"), ("Bitung", "4.7")]
TREMOR_VAL = [6.5, 5.4, 5.1, 4.9, 4.8, 4.7]

STRIP = [("+36.6%", "NVIDIA SURGES AS HUANG RETURNS"),
         ("6.5", "VANUATU QUAKE — NO TSUNAMI"),
         ("3,000+", "DELTA FLIGHTS HIT BY OUTAGE"),
         ("12", "CHINESE WARSHIPS OFF TAIWAN")]


def draw_header(d):
    text(d, (16, 10), "TUESDAY 24 NOVEMBER 2026", font(30, bold=True, serif=True))
    text(d, (1008, 16), "39 STORIES · 9 REGIONS", font(20, bold=True), fill=RED, anchor="ra")
    d.line([16, 52, 1008, 52], fill=INK, width=2)


def draw_strip(d):
    y0, y1 = 62, 100
    d.rectangle([16, y0, 1008, y1], fill=CARD, outline=LINE, width=1)
    cw = 992 // 4
    for i, (num, lab) in enumerate(STRIP):
        x = 16 + i * cw
        if i:
            d.line([x, y0 + 5, x, y1 - 5], fill=LINE, width=1)
        text(d, (x + 14, y0 + 4), num, font(24, bold=True), fill=RED)
        text(d, (x + 14, y0 + 27), lab, font(9, bold=True), fill=MUTED)


def draw_leads(d):
    y0, h = 108, 182
    pw, gap = 320, 16
    for i, (region, beat, tag, head, deck, icon, accent) in enumerate(LEADS):
        x = 16 + i * (pw + gap)
        panel(d, x, y0, pw, h, top=accent)
        text(d, (x + 12, y0 + 12), region, font(11, bold=True), fill=accent)
        text(d, (x + 12, y0 + 28), beat, font(10, bold=True), fill=MUTED)
        # verification tag, right-aligned in a small box
        tf = font(9, bold=True)
        tw = tf.getlength(tag) + 12
        d.rectangle([x + pw - 12 - tw, y0 + 11, x + pw - 12, y0 + 27], outline=accent, width=1)
        text(d, (x + pw - 12 - tw + 6, y0 + 13), tag, tf, fill=accent)
        icon(d, x + 12, y0 + 52, 84)
        para(d, x + 108, y0 + 52, head, font(18, bold=True), pw - 120, lh=22)
        para(d, x + 12, y0 + 146, deck, font(13), pw - 24, lh=16)


def draw_mids(d):
    y0 = 298
    pw, ph, gap = 242, 100, 8
    for i, (region, head, deck, src, icon) in enumerate(MIDS):
        row, col = divmod(i, 4)
        x = 16 + col * (pw + gap)
        y = y0 + row * (ph + 8)
        panel(d, x, y, pw, ph)
        text(d, (x + 8, y + 6), region, font(9, bold=True), fill=BLUE)
        icon(d, x + 8, y + 26, 46)
        para(d, x + 62, y + 24, head, font(13, bold=True), pw - 70, lh=16)
        text(d, (x + 8, y + ph - 14), src, font(9), fill=MUTED)


def draw_map(d):
    x0, y0, w, h = 16, 514, 544, 192
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=MAP_BG, outline=LINE, width=1)
    text(d, (x0 + 12, y0 + 8), "THE WORLD TODAY — 10 HOTSPOTS", font(13, bold=True))
    mx, my, mw, mh = x0 + 12, y0 + 30, w - 24, 144
    for poly in CONTINENTS:
        pts = [proj(lon, lat, mx, my, mw, mh) for (lon, lat) in poly]
        d.polygon(pts, fill=MAP_LAND, outline=MAP_LINE)
    for (num, lon, lat) in HOTSPOTS:
        cx, cy = proj(lon, lat, mx, my, mw, mh)
        d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=RED, outline=CARD, width=1)
        text(d, (cx, cy - 5), str(num), font(10, bold=True), fill=CARD, anchor="ma")
    legend = "1 Odesa  2 Taiwan  3 Atlanta  4 Perm  5 Rabigh  6 Nigeria  7 Sinaloa  8 Hobart  9 Seoul  10 Vanuatu"
    text(d, (x0 + 12, y0 + h - 16), legend, font(9), fill=MUTED)


def draw_bar_chart(d, x, y, w, title, rows, vals, vmax, color):
    text(d, (x, y), title, font(12, bold=True))
    ly = y + 18
    for (label, vtxt), v in zip(rows, vals):
        text(d, (x, ly), label, font(11))
        bx = x + 86
        bw = int(v / vmax * 190)
        d.rectangle([bx, ly + 1, bx + bw, ly + 11], fill=color)
        text(d, (bx + bw + 6, ly), vtxt, font(11, bold=True), fill=color)
        ly += 15


def draw_charts(d):
    x0, y0, w, h = 576, 514, 432, 192
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=CARD, outline=LINE, width=1)
    draw_bar_chart(d, x0 + 12, y0 + 8, w - 24,
                   "FRIDAY'S FALLS — 20 NOV", FALLS, FALLS_VAL, 6.7, RED)
    d.line([x0 + 12, y0 + 100, x0 + w - 12, y0 + 100], fill=LINE, width=1)
    draw_bar_chart(d, x0 + 12, y0 + 108, w - 24,
                   "TREMORS — LAST 24H, MAGNITUDE", TREMORS, TREMOR_VAL, 6.5, ORANGE)


def draw_list(d):
    text(d, (16, 712), "THE REST OF THE DAY — 28 MORE STORIES", font(14, bold=True))
    d.line([16, 732, 1008, 732], fill=INK, width=1)
    f = font(12, bold=True)
    fb = font(12)
    for col in range(2):
        x = 16 + col * 496
        y = 738
        for r in range(14):
            idx = col * 14 + r
            num = 12 + idx
            text(d, (x, y), f"{num:>2}.", f, fill=RED)
            text(d, (x + 30, y), LIST[idx], fb)
            y += 18


def draw_footer(d):
    text(d, (16, 992),
         "REGIONS COVERED: North America · Europe · Asia-Pacific · Latin America · "
         "Middle East · Africa · South Asia · Oceania · Global",
         font(11, bold=True), fill=BLUE)
    text(d, (16, 1008),
         "DATE CHECK — all 39 stories dated Tue 24 Nov 2026. "
         "Sources: Go Herald Now · m.autoys.eu · Geopolitiki live · Disclosure News · "
         "Sky at Night · The Sun Report · Liveuamap · The Ledger Asia",
         font(9), fill=MUTED)


def validate_layout():
    problems = []
    for (x0, y0, x1, y1, label) in BOXES:
        if x0 < 0 or y0 < 0 or x1 > W or y1 > H:
            problems.append(f"OUT-OF-BOUNDS {label!r}: {(x0, y0, x1, y1)}")
    n = len(BOXES)
    for i in range(n):
        for j in range(i + 1, n):
            a, b = BOXES[i], BOXES[j]
            ox = min(a[2], b[2]) - max(a[0], b[0])
            oy = min(a[3], b[3]) - max(a[1], b[1])
            if ox > 1 and oy > 1:
                problems.append(f"OVERLAP {a[4]!r} vs {b[4]!r}")
    return problems


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_header(d)
    draw_strip(d)
    draw_leads(d)
    draw_mids(d)
    draw_map(d)
    draw_charts(d)
    draw_list(d)
    draw_footer(d)
    problems = validate_layout()
    print(f"LAYOUT: {len(BOXES)} text boxes, {len(problems)} problems")
    for p in problems[:20]:
        print("  " + p)
    if problems:
        print("LAYOUT GATE: FAIL")
        sys.exit(1)
    img.save(OUT, format="PNG")
    raw = open(OUT, "rb").read()
    print(f"WROTE {OUT} {len(raw)} bytes sha256={hashlib.sha256(raw).hexdigest()}")
    print("LAYOUT GATE: PASS")


if __name__ == "__main__":
    main()
