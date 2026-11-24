#!/usr/bin/env python3
"""Draw entry.png for news-image-20261124 — 'The World in One Page'.

Fresh render for 24 Nov 2026: 39 dated stories, 9 regions, 3 lead panels with
hand-drawn pictograms, world map with hotspots, 2 charts, big data strip.
Deterministic: fixed fonts, fixed layout, no randomness, no network, no time.
Run: python3 draw_news24.py  ->  writes entry.png (1024x1024) next to this file.
"""
import hashlib
import json
import textwrap

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = "entry.png"

# ---------- palette ----------
PAPER = (246, 241, 231)
INK = (22, 32, 48)
NAVY = (22, 35, 58)
NAVY2 = (30, 48, 78)
GOLD = (198, 148, 44)
RED = (178, 44, 36)
TEAL = (18, 110, 105)
WHITE = (255, 255, 255)
CARD = (255, 255, 255)
LINE = (180, 172, 155)
MUTED = (96, 100, 110)
LIGHT = (232, 226, 212)

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"


def font(name, size):
    return ImageFont.truetype(FONT_DIR + name, size)


F_SERIF = lambda s: font("DejaVuSerif-Bold.ttf", s)
F_SANS = lambda s: font("DejaVuSans.ttf", s)
F_BOLD = lambda s: font("DejaVuSans-Bold.ttf", s)

# ---------- story data ----------
# 3 leads + 36 grid = 39 stories, 9 regions. Every story dated 24 Nov 2026
# (source date in the README). Headlines kept <= 64 chars, decks <= 110 chars.
LEADS = [
    {
        "num": "01", "region": "NORTH AMERICA · MARKETS", "color": RED,
        "headline": "Huang is back — Nvidia soars 36.6%",
        "deck": "Board reinstates Huang as chief executive; Wall Street "
                "rebounds as the AI rout reverses.",
        "source": "Go Herald Now · 24 Nov", "tag": "REPORTED",
        "icon": "chip",
    },
    {
        "num": "02", "region": "EUROPE · UKRAINE", "color": NAVY2,
        "headline": "Odesa dark and cold after Russian strikes",
        "deck": "Strikes knock out power, heat and water across the "
                "Black Sea port city.",
        "source": "m.autoys.eu · 24 Nov", "tag": "REPORTED",
        "icon": "city",
    },
    {
        "num": "03", "region": "ASIA-PACIFIC · TAIWAN", "color": TEAL,
        "headline": "12 Chinese warships circle Taiwan",
        "deck": "Drones and helicopters enter the island's air-defence "
                "zone as Taipei tracks the flotilla.",
        "source": "Geopolitiki live · 24 Nov", "tag": "REPORTED",
        "icon": "ship",
    },
]

# Mid tier: 8 illustrated panels (numbered 04-11), each with a small
# hand-drawn icon, a one-line deck and a verification tag.
MIDS = [
    ("04", "NORTH AMERICA", RED, "Delta outage grounds 3,000+ US flights",
     "System failure hits key US hubs", "m.autoys.eu", "REPORTED", "plane"),
    ("05", "EUROPE", NAVY2, "Ukraine drones set two Russian refineries ablaze",
     "Fires at Perm and Rostov plants", "Geopolitiki live", "REPORTED", "flame"),
    ("06", "MIDDLE EAST", (120, 60, 110), "Houthis say they hit Saudi Rabigh refinery",
     "Houthi claim; Riyadh silent so far", "Geopolitiki live", "CLAIM", "factory"),
    ("07", "ASIA-PACIFIC", TEAL, "Seoul names new foreign minister, spy chief",
     "Reshuffle amid US alliance worries", "m.autoys.eu", "REPORTED", "flag"),
    ("08", "AFRICA", (90, 120, 40), "24 dead as boat capsizes to Nigeria funeral",
     "Boat was bound for a funeral", "m.autoys.eu", "REPORTED", "boat"),
    ("09", "GLOBAL", GOLD, "Beaver Supermoon rises tonight, first of four",
     "First of four supermoons to Feb 2027", "Sky at Night", "REPORTED", "moon"),
    ("10", "LATIN AMERICA", (150, 90, 20), "16 cartel suspects killed in 'El Chapo' arrest",
     "Mexico reports 16 killed in raid", "m.autoys.eu", "REPORTED", "shield"),
    ("11", "OCEANIA", (40, 110, 160), "Hobart stadium bill jumps to $1.23 billion",
     "Macquarie Point cost hits $1.23bn", "Go Herald Now", "REPORTED", "coins"),
]

# (number, region tag, region colour, headline) — numbered list 12-39
GRID = [
    ("12", "EU", NAVY2, "Armenia drops Karabakh claim in draft constitution"),
    ("13", "EU", NAVY2, "Cyprus expels two Russian diplomats over spying claims"),
    ("14", "EU", NAVY2, "Estonia answers Russia's airspace allegation firmly"),
    ("15", "EU", NAVY2, "Bomb threats close schools in Germany and Denmark"),
    ("16", "EU", NAVY2, "Merz: keeping Ukraine out of NATO in 2008 was wrong"),
    ("17", "EU", NAVY2, "UK starts world's largest AI breast-screening trial"),
    ("18", "EU", NAVY2, "NATO offers Poland 'significant backing' after incursion"),
    ("19", "EU", NAVY2, "Russian casualties outpace monthly recruiting, US says"),
    ("20", "NA", RED, "Two killed as helicopter crashes near Napa wineries"),
    ("21", "NA", RED, "US states sue SpaceX over Grok's sexual images"),
    ("22", "NA", RED, "Army invokes emergency powers for Iowa munitions blast"),
    ("23", "NA", RED, "US to host the 2031 Women's World Cup, FIFA says"),
    ("24", "NA", RED, "Schumer warns of security risks in Huang's return"),
    ("25", "LATAM", (150, 90, 20), "Panama and First Quantum resume Cobre mine talks"),
    ("26", "LATAM", (150, 90, 20), "Storm forces thousands to flee in Brazil"),
    ("27", "ME", (120, 60, 110), "Gaza's soil and water poisoned by war, report finds"),
    ("28", "ME", (120, 60, 110), "France condemns settler attacks on Palestinians"),
    ("29", "ME", (120, 60, 110), "Lebanon condemns Israeli officer's school visit"),
    ("30", "ME", (120, 60, 110), "Trump faces pivotal decision on Iran deal"),
    ("31", "AFRICA", (90, 120, 40), "Eastern Libya appeals to UN over Russian warship"),
    ("32", "AFRICA", (90, 120, 40), "Fighting traps Ebola responders in Ituri"),
    ("33", "APAC", TEAL, "Seoul denies navy unit is bound for Iran war"),
    ("34", "APAC", TEAL, "Taiwan eases margin rules from today after rout"),
    ("35", "APAC", TEAL, "South Korea tracks North Korean ship off its coast"),
    ("36", "S. ASIA", (160, 60, 90), "Taliban erases women's names from Balkh documents"),
    ("37", "OCEANIA", (40, 110, 160), "Australia budget update as rents hit 14-year low"),
    ("38", "GLOBAL", GOLD, "UN chief urges global AI safety rules within a year"),
    ("39", "GLOBAL", GOLD, "China's nuclear build-up 'turning world dangerous'"),
]

REGIONS = ["Europe", "North America", "Latin America", "Middle East",
           "Africa", "Asia-Pacific", "South Asia", "Oceania", "Global"]

DATA_STRIP = [
    ("+36.6%", "NVIDIA SURGES AS HUANG RETURNS"),
    ("6.5", "VANUATU QUAKE — NO TSUNAMI"),
    ("3,000+", "DELTA FLIGHTS HIT BY OUTAGE"),
    ("12", "CHINESE WARSHIPS OFF TAIWAN"),
]

# Friday's falls, 20 Nov 2026 (The Sun Report) — labelled with the date.
CHART_FALLS = [("Taiwan", -6.7), ("S. Korea", -5.2), ("Nikkei", -5.0),
               ("Shanghai", -2.1), ("ASX", -1.6)]
# Tremors in the last 24 hours, magnitude (Liveuamap).
CHART_QUAKES = [("Vanuatu", 6.5), ("Timor-Leste", 5.4), ("Ürümqi", 5.1),
                ("Kuqa", 4.9), ("Palau", 4.8), ("Bitung", 4.7)]

# ---------- text helpers (with bounding-box recording for the validator) ----------
boxes = []  # (x0, y0, x1, y1, label)


def draw_text(d, xy, text, fnt, fill, anchor="la", label=""):
    d.text(xy, text, font=fnt, fill=fill, anchor=anchor)
    # real ink bounding box (anchor-aware) — the validator's source of truth
    bb = d.textbbox(xy, text, font=fnt, anchor=anchor)
    boxes.append((bb[0], bb[1], bb[2], bb[3], label or text[:28]))
    return bb


def wrap(d, text, fnt, max_w):
    """Greedy word wrap to max_w pixels; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if d.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(d, xy, text, fnt, fill, max_w, leading, max_lines=None,
                 label=""):
    x, y = xy
    lines = wrap(d, text, fnt, max_w)
    if max_lines:
        lines = lines[:max_lines]
    for ln in lines:
        draw_text(d, (x, y), ln, fnt, fill, label=label)
        y += leading
    return y

# ---------- hand-drawn pictograms (one per lead story) ----------
def draw_chip(d, cx, cy, s, color):
    """Microchip with pins + upward arrow (Nvidia / Huang returns)."""
    w = int(s * 0.62)
    d.rounded_rectangle([cx - w // 2, cy - w // 2, cx + w // 2, cy + w // 2],
                        radius=8, fill=color, outline=INK, width=2)
    d.rounded_rectangle([cx - w // 4, cy - w // 4, cx + w // 4, cy + w // 4],
                        radius=4, outline=WHITE, width=2)
    for i in (-1, 0, 1):
        off = i * w // 3
        d.line([cx + off, cy - w // 2 - 10, cx + off, cy - w // 2], fill=INK, width=3)
        d.line([cx + off, cy + w // 2, cx + off, cy + w // 2 + 10], fill=INK, width=3)
        d.line([cx - w // 2 - 10, cy + off, cx - w // 2, cy + off], fill=INK, width=3)
        d.line([cx + w // 2, cy + off, cx + w // 2 + 10, cy + off], fill=INK, width=3)
    # green up arrow rising out of the chip
    ax = cx + w // 2 + 26
    d.line([ax, cy + 26, ax, cy - 26], fill=(30, 140, 60), width=5)
    d.polygon([(ax - 10, cy - 14), (ax + 10, cy - 14), (ax, cy - 30)],
              fill=(30, 140, 60))


def draw_city(d, cx, cy, s, color):
    """City skyline under a broken power line / lightning (Odesa blackout)."""
    base = cy + s // 2
    heights = [0.55, 0.85, 0.45, 0.95, 0.65, 0.75]
    bw = s // 6
    for i, hh in enumerate(heights):
        x0 = cx - s // 2 + i * bw + 2
        x1 = x0 + bw - 4
        y0 = base - int(s * hh)
        d.rectangle([x0, y0, x1, base], fill=color, outline=INK, width=1)
        # lit / dark windows: only a few lit (blackout)
        for wy in range(y0 + 8, base - 6, 12):
            for wx in range(x0 + 4, x1 - 4, 9):
                if (wx + wy) % 37 < 8:
                    d.rectangle([wx, wy, wx + 3, wy + 4], fill=GOLD)
    # lightning bolt low over the skyline (kept clear of the region line
    # above the pictogram box) + a few lit windows: mostly a blackout
    d.polygon([(cx + 22, cy - 12), (cx + 12, cy + 8), (cx + 20, cy + 8),
               (cx + 14, cy + 26), (cx + 28, cy + 2), (cx + 20, cy + 2)],
              fill=GOLD, outline=INK)


def draw_ship(d, cx, cy, s, color):
    """Warship silhouette + radar arcs (Taiwan flotilla). Compact: every
    stroke stays inside the pictogram box so it cannot touch the headline."""
    base = cy + s // 4
    # hull
    d.polygon([(cx - s // 2, base - 12), (cx + s // 2, base - 12),
               (cx + s // 2 - 10, base + 6), (cx - s // 2 + 14, base + 6)],
              fill=color, outline=INK, width=2)
    # superstructure + mast
    d.rectangle([cx - 10, base - 30, cx + 18, base - 12], fill=color,
                outline=INK, width=2)
    d.line([cx + 3, base - 30, cx + 3, base - 42], fill=INK, width=3)
    d.ellipse([cx - 2, base - 47, cx + 8, base - 37], fill=RED, outline=INK)
    # radar arcs — small, close to the mast
    for r in (13, 20, 27):
        d.arc([cx + 3 - r, base - 42 - r, cx + 3 + r, base - 42 + r],
              start=300, end=60, fill=TEAL, width=3)
    # waves
    for yy in (base + 12, base + 20):
        for xx in range(cx - s // 2, cx + s // 2, 20):
            d.arc([xx, yy, xx + 14, yy + 8], start=180, end=360,
                  fill=NAVY2, width=2)


ICONS = {"chip": draw_chip, "city": draw_city, "ship": draw_ship}


# ---------- small icons for the mid tier (drawn in a ~44px box) ----------
def draw_plane(d, cx, cy, s, color):
    d.polygon([(cx - s // 2, cy + 4), (cx + s // 2 - 6, cy - 8),
               (cx + s // 2, cy - 4), (cx - s // 2 + 8, cy + 10)],
              fill=color, outline=INK, width=2)
    d.polygon([(cx - 6, cy - 2), (cx + 8, cy - 16), (cx + 12, cy - 10),
               (cx + 2, cy + 2)], fill=color, outline=INK, width=1)
    d.polygon([(cx - 10, cy + 8), (cx + 2, cy - 2), (cx + 6, cy + 2),
               (cx - 6, cy + 12)], fill=color, outline=INK, width=1)
    d.line([cx - s // 2 - 6, cy + 16, cx + s // 2, cy + 16], fill=MUTED, width=2)


def draw_flame(d, cx, cy, s, color):
    d.polygon([(cx, cy - s // 2), (cx + s // 3, cy - 2), (cx + s // 4, cy + s // 3),
               (cx - s // 4, cy + s // 3), (cx - s // 3, cy - 2)],
              fill=color, outline=INK, width=2)
    d.polygon([(cx, cy - 2), (cx + s // 6, cy + s // 5), (cx - s // 6, cy + s // 5)],
              fill=GOLD, outline=INK, width=1)


def draw_factory(d, cx, cy, s, color):
    d.rectangle([cx - s // 2, cy - 2, cx + s // 2, cy + s // 3], fill=color,
                outline=INK, width=2)
    d.polygon([(cx - s // 2, cy - 2), (cx - s // 4, cy - s // 3),
               (cx, cy - 2)], fill=color, outline=INK, width=1)
    d.polygon([(cx, cy - 2), (cx + s // 4, cy - s // 3), (cx + s // 2, cy - 2)],
              fill=color, outline=INK, width=1)
    d.rectangle([cx + s // 4, cy - s // 2, cx + s // 3, cy - 2], fill=color,
                outline=INK, width=2)
    d.ellipse([cx - s // 4, cy + 2, cx - s // 8, cy + 10], fill=GOLD)
    d.ellipse([cx + s // 8, cy + 2, cx + s // 4, cy + 10], fill=GOLD)


def draw_flag(d, cx, cy, s, color):
    d.line([cx - s // 4, cy - s // 2, cx - s // 4, cy + s // 2], fill=INK, width=3)
    d.polygon([(cx - s // 4, cy - s // 2), (cx + s // 2, cy - s // 3),
               (cx - s // 4, cy - s // 6)], fill=color, outline=INK, width=2)
    d.line([cx - s // 2, cy + s // 2, cx + s // 2, cy + s // 2], fill=INK, width=3)


def draw_boat(d, cx, cy, s, color):
    d.polygon([(cx - s // 2, cy), (cx + s // 2, cy), (cx + s // 3, cy + s // 4),
               (cx - s // 3, cy + s // 4)], fill=color, outline=INK, width=2)
    d.line([cx, cy, cx, cy - s // 2], fill=INK, width=2)
    d.polygon([(cx, cy - s // 2), (cx, cy - 4), (cx + s // 3, cy - 4)],
              fill=WHITE, outline=INK, width=1)
    d.arc([cx - s // 2, cy + s // 3, cx - s // 4, cy + s // 2], start=180,
          end=360, fill=NAVY2, width=2)
    d.arc([cx + s // 4, cy + s // 3, cx + s // 2, cy + s // 2], start=180,
          end=360, fill=NAVY2, width=2)


def draw_moon(d, cx, cy, s, color):
    d.ellipse([cx - s // 3, cy - s // 3, cx + s // 3, cy + s // 3],
              fill=GOLD, outline=INK, width=2)
    d.ellipse([cx - s // 6, cy - s // 8, cx, cy + s // 8], fill=(210, 165, 70))
    d.ellipse([cx + s // 12, cy + s // 12, cx + s // 5, cy + s // 4],
              fill=(210, 165, 70))
    for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        d.line([cx + dx * s // 2, cy + dy * s // 2 - 3, cx + dx * s // 2,
                cy + dy * s // 2 + 3], fill=GOLD, width=2)
        d.line([cx + dx * s // 2 - 3, cy + dy * s // 2, cx + dx * s // 2 + 3,
                cy + dy * s // 2], fill=GOLD, width=2)


def draw_shield(d, cx, cy, s, color):
    d.polygon([(cx - s // 3, cy - s // 3), (cx + s // 3, cy - s // 3),
               (cx + s // 3, cy + 2), (cx, cy + s // 2),
               (cx - s // 3, cy + 2)], fill=color, outline=INK, width=2)
    d.text((cx, cy - 8), "★", font=F_BOLD(16), fill=WHITE, anchor="ma")


def draw_coins(d, cx, cy, s, color):
    for i, yy in enumerate((cy + s // 4, cy, cy - s // 4)):
        d.ellipse([cx - s // 3, yy - 7, cx + s // 3, yy + 7], fill=GOLD,
                  outline=INK, width=2)
        d.text((cx, yy - 7), "$", font=F_BOLD(11), fill=INK, anchor="ma")


MID_ICONS = {"plane": draw_plane, "flame": draw_flame,
             "factory": draw_factory, "flag": draw_flag,
             "boat": draw_boat, "moon": draw_moon,
             "shield": draw_shield, "coins": draw_coins}

# ---------- world map (schematic, hand-coded lon/lat outlines) ----------
# Equirectangular projection into the map box.
MAP_BOX = (16, 408, 556, 612)  # x0, y0, x1, y1 (title strip above inside panel)


def project(lon, lat, box):
    x0, y0, x1, y1 = box
    x = x0 + (lon + 180.0) / 360.0 * (x1 - x0)
    y = y0 + (90.0 - lat) / 180.0 * (y1 - y0)
    return (x, y)


CONTINENTS = [
    # North America
    [(-168, 66), (-150, 70), (-130, 71), (-110, 73), (-95, 80), (-80, 80),
     (-72, 71), (-65, 60), (-55, 52), (-60, 46), (-70, 42), (-76, 35),
     (-81, 26), (-86, 21), (-91, 15), (-97, 16), (-102, 19), (-106, 23),
     (-111, 26), (-116, 30), (-122, 37), (-125, 43), (-125, 49),
     (-131, 56), (-141, 60), (-152, 58), (-162, 58), (-168, 66)],
    # Greenland
    [(-58, 64), (-48, 60), (-40, 68), (-50, 76), (-62, 76), (-68, 70)],
    # South America
    [(-79, 9), (-74, 4), (-68, -1), (-58, -4), (-48, -4), (-40, -9),
     (-35, -14), (-39, -20), (-47, -24), (-54, -30), (-60, -36),
     (-66, -41), (-70, -50), (-71, -54), (-74, -46), (-73, -36),
     (-72, -26), (-77, -16), (-80, -6), (-81, 1)],
    # Africa
    [(-17, 15), (-12, 7), (-4, 5), (3, 6), (9, 3), (10, -3), (13, -9),
     (18, -14), (23, -19), (28, -25), (33, -28), (37, -22), (40, -16),
     (46, -11), (51, -2), (51, 9), (46, 11), (43, 15), (39, 21), (35, 27),
     (30, 31), (22, 33), (12, 35), (2, 36), (-6, 34), (-10, 30), (-16, 21)],
    # Eurasia (Europe + Asia as one landmass)
    [(-10, 36), (-9, 43), (-2, 44), (3, 43), (8, 44), (12, 45), (18, 45),
     (23, 40), (27, 41), (30, 36), (33, 36), (36, 36), (40, 38), (44, 39),
     (48, 42), (50, 46), (52, 50), (55, 54), (58, 58), (62, 62), (68, 66),
     (75, 70), (85, 73), (95, 75), (105, 76), (115, 73), (125, 71),
     (135, 71), (145, 71), (155, 69), (165, 66), (175, 65), (178, 64),
     (170, 60), (162, 56), (156, 51), (148, 45), (142, 40), (137, 36),
     (131, 33), (127, 31), (122, 28), (118, 24), (112, 21), (108, 16),
     (105, 9), (101, 6), (98, 10), (94, 16), (91, 21), (88, 21), (84, 19),
     (80, 14), (77, 8), (74, 14), (71, 21), (67, 25), (63, 25), (58, 26),
     (55, 27), (52, 28), (49, 30), (46, 30), (42, 32), (38, 36), (33, 36),
     (27, 37), (22, 37), (18, 40), (12, 44), (8, 44), (3, 42), (0, 39),
     (-3, 37), (-9, 37)],
    # Australia
    [(113, -22), (114, -30), (115, -35), (120, -34), (125, -32), (130, -32),
     (135, -35), (140, -38), (145, -38), (150, -37), (153, -32), (150, -25),
     (146, -20), (142, -15), (140, -10), (136, -12), (132, -11), (129, -13),
     (126, -14), (122, -17), (118, -20), (114, -22)],
    # United Kingdom
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51)],
    # Japan
    [(130, 31), (132, 33), (135, 34), (138, 35), (140, 38), (142, 42),
     (145, 44), (142, 40), (140, 36), (137, 34), (133, 33)],
    # New Zealand
    [(167, -45), (170, -42), (174, -39), (177, -38), (175, -41), (172, -43),
     (168, -46)],
]

HOTSPOTS = [
    # (label incl. story number, lon, lat, label dy)
    ("02 Odesa", 30.7, 46.5, -13), ("31 Benghazi", 20.1, 32.1, -13),
    ("03 Taipei", 121.6, 25.0, -13), ("6.5 Vanuatu", 167.0, -16.0, -13),
    ("06 Rabigh", 39.0, 22.8, 8), ("10 Mexico C.", -99.1, 19.4, -13),
    ("25 Panama C.", -79.5, 9.0, 8), ("11 Hobart", 147.3, -42.9, -13),
    ("12 Yerevan", 44.5, 40.2, 8), ("07 Seoul", 127.0, 37.5, -24),
]


def draw_map(d, panel):
    """Draw the schematic world map inside panel (x0,y0,x1,y1)."""
    x0, y0, x1, y1 = panel
    # ocean
    d.rectangle(panel, fill=(214, 230, 238))
    # graticule
    for lon in range(-150, 181, 30):
        x = x0 + (lon + 180.0) / 360.0 * (x1 - x0)
        d.line([x, y0, x, y1], fill=(190, 208, 220), width=1)
    for lat in (-60, -30, 0, 30, 60):
        y = y0 + (90.0 - lat) / 180.0 * (y1 - y0)
        d.line([x0, y, x1, y], fill=(190, 208, 220), width=1)
    # land
    for poly in CONTINENTS:
        pts = [project(lon, lat, panel) for lon, lat in poly]
        d.polygon(pts, fill=(226, 214, 182), outline=(120, 105, 75))
    # hotspots
    f_small = F_BOLD(9)
    for name, lon, lat, dy in HOTSPOTS:
        x, y = project(lon, lat, panel)
        d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=RED, outline=WHITE, width=2)
        # label: keep inside the panel
        lx = min(max(x + 8, x0 + 2), x1 - d.textlength(name, font=f_small) - 2)
        ly = min(max(y + dy, y0 + 2), y1 - 12)
        d.text((lx, ly), name, font=f_small, fill=INK)
        boxes.append((lx, ly, lx + d.textlength(name, font=f_small), ly + 11,
                      "map:" + name))

# ---------- charts ----------
def draw_hbar_chart(d, panel, title, subtitle, data, value_fmt, color, max_abs):
    x0, y0, x1, y1 = panel
    d.rectangle(panel, fill=CARD, outline=LINE, width=1)
    draw_text(d, (x0 + 10, y0 + 6), title, F_BOLD(13), INK, label="chart-title")
    draw_text(d, (x1 - 10, y0 + 7), subtitle, F_SANS(10), MUTED, anchor="ra",
              label="chart-sub")
    top = y0 + 28
    row_h = (y1 - top - 6) / len(data)
    label_w = 78
    for i, (name, val) in enumerate(data):
        ry = top + i * row_h
        cy = ry + row_h / 2
        draw_text(d, (x0 + 10, cy - 6), name, F_SANS(11), INK, label="chart-lab")
        bx0 = x0 + 10 + label_w
        bx1 = x1 - 46
        w = (bx1 - bx0) * abs(val) / max_abs
        d.rectangle([bx0, cy - 7, bx0 + w, cy + 7], fill=color)
        d.rectangle([bx0, cy - 7, bx0 + w, cy + 7], outline=INK, width=1)
        draw_text(d, (bx0 + w + 5, cy - 6), value_fmt(val), F_BOLD(11), INK,
                  label="chart-val")


# ---------- render ----------
def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    boxes.clear()

    # ===== HEADER =====
    d.rectangle([0, 0, W, 92], fill=PAPER)
    draw_text(d, (W // 2, 8), "THE WORLD IN ONE PAGE", F_SERIF(40), INK,
              anchor="ma", label="masthead")
    d.line([16, 58, W - 16, 58], fill=INK, width=2)
    draw_text(d, (16, 66), "TUESDAY 24 NOVEMBER 2026", F_BOLD(21), INK,
              label="date")
    # count badge
    badge = "39 STORIES  ·  9 REGIONS"
    bw = d.textlength(badge, font=F_BOLD(17)) + 28
    bx1, by0, by1 = W - 16, 64, 90
    d.rounded_rectangle([bx1 - bw, by0, bx1, by1], radius=13, fill=RED)
    draw_text(d, (bx1 - bw / 2, by0 + 5), badge, F_BOLD(17), WHITE,
              anchor="ma", label="badge")

    # ===== DATA STRIP =====
    sy0, sy1 = 98, 150
    d.rectangle([16, sy0, W - 16, sy1], fill=NAVY)
    cw = (W - 32) / 4
    for i, (num, lab) in enumerate(DATA_STRIP):
        cx = 16 + cw * i + cw / 2
        if i:
            d.line([16 + cw * i, sy0 + 8, 16 + cw * i, sy1 - 8],
                   fill=(70, 90, 120), width=1)
        draw_text(d, (cx, sy0 + 6), num, F_BOLD(27), GOLD, anchor="ma",
                  label="strip-num")
        draw_text(d, (cx, sy0 + 36), lab, F_BOLD(10), WHITE, anchor="ma",
                  label="strip-lab")

    # ===== LEAD PANELS =====
    ly0, ly1 = 156, 348
    lw, gap = 322, 8
    for i, lead in enumerate(LEADS):
        x0 = 16 + i * (lw + gap)
        x1 = x0 + lw
        d.rectangle([x0, ly0, x1, ly1], fill=CARD, outline=LINE, width=1)
        d.rectangle([x0, ly0, x1, ly0 + 6], fill=lead["color"])
        draw_text(d, (x0 + 10, ly0 + 12), lead["num"], F_SERIF(22),
                  lead["color"], label="lead-num")
        draw_text(d, (x0 + 44, ly0 + 18), lead["region"], F_BOLD(11),
                  lead["color"], label="lead-region")
        # pictogram
        ICONS[lead["icon"]](d, x0 + lw // 2, ly0 + 58, 76, lead["color"])
        # headline + deck
        hy = ly0 + 102
        hy = draw_wrapped(d, (x0 + 10, hy), lead["headline"], F_BOLD(19),
                          INK, lw - 20, 21, max_lines=2, label="lead-head")
        hy = draw_wrapped(d, (x0 + 10, hy + 4), lead["deck"], F_SANS(12),
                          (60, 64, 74), lw - 20, 14, max_lines=2,
                          label="lead-deck")
        draw_text(d, (x0 + 10, ly1 - 16), lead["source"], F_SANS(10), MUTED,
                  label="lead-src")
        draw_text(d, (x1 - 10, ly1 - 16), lead["tag"], F_BOLD(10),
                  lead["color"], anchor="ra", label="lead-tag")

    # ===== MID PANELS (illustrated, numbered 04-11) =====
    my0 = 354
    mw, mh, mgap = 245, 88, 4
    for i, (num, region, color, head, deck, src, tag, icon) in enumerate(MIDS):
        col, row = i % 4, i // 4
        x0 = 16 + col * (mw + mgap)
        y0 = my0 + row * (mh + 4)
        x1 = x0 + mw
        y1 = y0 + mh
        d.rectangle([x0, y0, x1, y1], fill=CARD, outline=LINE, width=1)
        d.rectangle([x0, y0, x1, y0 + 4], fill=color)
        draw_text(d, (x0 + 8, y0 + 8), num, F_BOLD(12), color, label="mid-num")
        draw_text(d, (x0 + 34, y0 + 9), region, F_BOLD(9), color,
                  label="mid-region")
        draw_text(d, (x1 - 8, y0 + 9), tag, F_BOLD(9),
                  RED if tag == "CLAIM" else MUTED, anchor="ra",
                  label="mid-tag")
        # tinted chip behind the icon (visual richness, region colour)
        tint = tuple(255 - (255 - c) // 5 for c in color)
        d.rounded_rectangle([x0 + 6, y0 + 22, x0 + 50, y0 + 66], radius=8,
                            fill=tint)
        MID_ICONS[icon](d, x0 + 28, y0 + 44, 40, color)
        draw_wrapped(d, (x0 + 54, y0 + 26), head, F_BOLD(13), INK,
                     mw - 62, 15, max_lines=2, label="mid-head")
        draw_text(d, (x0 + 8, y0 + 64), deck, F_SANS(11), (60, 64, 74),
                  label="mid-deck")
        draw_text(d, (x0 + 8, y0 + 77), src, F_SANS(9), MUTED, label="mid-src")

    # ===== MIDDLE ROW: MAP + CHARTS SIDE BY SIDE =====
    my0, my1 = 540, 716
    # map panel
    d.rectangle([16, my0, 452, my1], fill=CARD, outline=LINE, width=1)
    draw_text(d, (26, my0 + 8), "WHERE THE DAY HAPPENED", F_BOLD(13), INK,
              label="map-title")
    draw_text(d, (442, my0 + 9), "10 HOTSPOTS", F_SANS(10), MUTED,
              anchor="ra", label="map-sub")
    draw_map(d, (22, my0 + 30, 446, my1 - 8))
    # charts side by side
    draw_hbar_chart(d, (460, my0, 730, my1),
                    "FRIDAY'S FALLS — %", "20 NOV",
                    CHART_FALLS, lambda v: f"{v:.1f}%", RED, 7.0)
    draw_hbar_chart(d, (738, my0, 1008, my1),
                    "TREMORS — LAST 24H", "MAGNITUDE",
                    CHART_QUAKES, lambda v: f"{v:.1f}", TEAL, 7.0)

    # ===== GRID =====
    gy0 = 722
    draw_text(d, (16, gy0), "28 MORE STORIES — NUMBERED 12–39", F_BOLD(14),
              INK, label="grid-title")
    draw_text(d, (W - 16, gy0 + 1), "TAGS: EU · NA · LATAM · ME · AFRICA · APAC · S. ASIA · OCEANIA · GLOBAL",
              F_SANS(10), MUTED, anchor="ra", label="grid-legend")
    cols, rows = 3, 10
    gx0, gx1 = 16, W - 16
    col_w = (gx1 - gx0) / cols
    grid_top = gy0 + 22
    grid_bot = 986
    row_h = (grid_bot - grid_top) / rows
    for idx, (num, tag, color, head) in enumerate(GRID):
        col, row = idx % cols, idx // cols
        x0 = gx0 + col * col_w
        y0 = grid_top + row * row_h
        # colour chip + number
        d.rectangle([x0, y0 + 2, x0 + 5, y0 + 2 + row_h - 6], fill=color)
        draw_text(d, (x0 + 9, y0), num, F_BOLD(11), color, label="grid-num")
        tx = x0 + 36
        draw_text(d, (tx, y0), tag + " —", F_BOLD(10), color, label="grid-tag")
        tw = d.textlength(tag + " — ", font=F_BOLD(10))
        lines = wrap(d, head, F_SANS(11), col_w - 40 - tw - 2)
        # first line shares the tag row; overflow lines go below
        ly = y0
        first = True
        for ln in lines[:2]:
            if first:
                draw_text(d, (tx + tw, ly), ln, F_SANS(11), INK,
                          label="grid-head")
                first = False
            else:
                ly += 12
                draw_text(d, (tx, ly), ln, F_SANS(11), INK, label="grid-head")
        if len(lines) > 2:
            # third line would overflow: shrink marker (should not happen;
            # headlines are capped at 64 chars)
            draw_text(d, (tx, ly + 12), "…", F_SANS(11), RED, label="OVERFLOW")

    # ===== FOOTER =====
    d.line([16, 992, W - 16, 992], fill=LINE, width=1)
    draw_text(d, (W // 2, 995),
              "Sources: Go Herald Now · m.autoys.eu · Geopolitiki · Liveuamap · The Ledger Asia · Disclosure News · Sky at Night · CLSTR",
              F_SANS(9), MUTED, anchor="ma", label="footer-src")
    draw_text(d, (W // 2, 1005),
              "DATE CHECK — LEFT OUT AS OLDER NEWS: COP31 ends without a pact (22 Nov) · Merkury warship sunk (22 Nov) · Dymer strike (23 Nov) · Zanzibar hotel fire (21 Nov)",
              F_SANS(9), MUTED, anchor="ma", label="footer-datecheck")
    draw_text(d, (W // 2, 1014),
              "Every story dated 24 November 2026 · 39 stories · 9 regions · REPORTED one outlet · CLAIM one side's account · OFFICIAL on the record",
              F_SANS(9), MUTED, anchor="ma", label="footer-note")

    img.save(OUT, optimize=True)
    return img


# ---------- validators ----------
def validate_layout():
    """No text box may run past the canvas or overlap another text box."""
    bad = []
    for (x0, y0, x1, y1, lab) in boxes:
        if x0 < 0 or y0 < 0 or x1 > W + 1 or y1 > H + 1:
            bad.append(f"OUT-OF-BOUNDS {lab}: ({x0:.0f},{y0:.0f})-({x1:.0f},{y1:.0f})")
    # overlap: only flag substantial overlaps (>2px on both axes) between
    # boxes on the same visual row band (different rows may share x ranges
    # only if y ranges truly intersect).
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i], boxes[j]
            ox = min(a[2], b[2]) - max(a[0], b[0])
            oy = min(a[3], b[3]) - max(a[1], b[1])
            if ox > 2 and oy > 2:
                bad.append(f"OVERLAP {a[4]!r} x {b[4]!r} ({ox:.0f}x{oy:.0f})")
    return bad


def main():
    render()
    problems = validate_layout()
    overflow = [b for b in boxes if b[4] == "OVERFLOW"]
    report = {
        "stories": len(LEADS) + len(MIDS) + len(GRID),
        "regions": len(REGIONS),
        "charts": 2,
        "map": True,
        "data_strip_items": len(DATA_STRIP),
        "text_boxes": len(boxes),
        "layout_problems": problems,
        "headline_overflow_markers": len(overflow),
    }
    with open("layout_report.json", "w") as f:
        json.dump(report, f, indent=1)
    h = hashlib.sha256(open(OUT, "rb").read()).hexdigest()
    print(f"entry.png sha256: {h}")
    print(json.dumps(report, indent=1))
    if problems or overflow:
        print("LAYOUT GATE: FAIL")
        raise SystemExit(1)
    print("LAYOUT GATE: PASS")


if __name__ == "__main__":
    main()
