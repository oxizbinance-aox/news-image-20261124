#!/usr/bin/env python3
"""NI24 density gate — OCR the rendered entry.png and count the design.

Fails (exit 1, prints DENSITY GATE: FAIL) when the image is short on
stories, regions, charts, map, or data-strip numbers. Run after EVERY
render of entry.png. Writes density_report.json + density_log.txt.
"""
import json
import os
import re
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PNG = os.path.join(HERE, "entry.png")

# One distinctive keyword per story (01-39). A story counts when ANY of
# its keywords appears in the OCR text — some glyphs confuse tesseract
# at small sizes (e.g. "Iowa" reads as "lowa"), so a story may carry an
# alternative keyword that is equally distinctive to it.
KEYWORDS = [
    ["Nvidia"], ["Odesa"], ["Taiwan"], ["Delta"], ["refineries"],
    ["Rabigh"], ["Seoul"], ["Nigeria"], ["Supermoon"], ["Chapo"],
    ["Hobart"], ["Karabakh"], ["Cyprus"], ["Estonia"], ["Germany"],
    ["Merz"], ["breast"], ["Poland"], ["casualties"], ["Napa"],
    ["SpaceX"], ["Iowa", "munitions"], ["2031"], ["Schumer"], ["Panama"],
    ["Brazil"], ["Gaza"], ["France"], ["Lebanon"], ["Iran"], ["Libya"],
    ["Ebola"], ["navy"], ["margin"], ["Korean"], ["Taliban"],
    ["Australia"], ["safety"], ["nuclear"],
]

REGIONS = ["North America", "Europe", "Asia-Pacific", "Latin America",
           "Middle East", "Africa", "South Asia", "Oceania", "Global"]

CHART_WORDS = ["FALLS", "TREMORS"]
MAP_WORDS = ["HOTSPOTS"]
STRIP_WORDS = ["36.6", "6.5"]


def ocr_text(path):
    out = subprocess.run(
        ["tesseract", path, "stdout", "--psm", "6"],
        capture_output=True, text=True, check=True)
    return out.stdout


def main():
    text = ocr_text(PNG)
    flat = re.sub(r"\s+", " ", text)
    words = text.split()
    found = [alts[0] for alts in KEYWORDS
             if any(a.lower() in flat.lower() for a in alts)]
    missing = [alts[0] for alts in KEYWORDS
               if not any(a.lower() in flat.lower() for a in alts)]
    regions = [r for r in REGIONS if r.lower() in flat.lower()]
    charts = [c for c in CHART_WORDS if c.lower() in flat.lower()]
    map_ok = any(m.lower() in flat.lower() for m in MAP_WORDS)
    squashed = flat.replace(",", "").replace(" ", "")
    strip = [w for w in STRIP_WORDS if w in flat] + \
        (["3,000+"] if "3000" in squashed else [])
    img = Image.open(PNG).convert("L")
    px = list(img.getdata())
    ink = sum(1 for p in px if p < 200) / len(px)
    report = {
        "stories_found": len(found),
        "stories_missing": missing,
        "regions_found": len(regions),
        "regions_missing": [r for r in REGIONS if r not in regions],
        "charts_found": len(charts),
        "map_present": map_ok,
        "data_strip_numbers": strip,
        "ocr_words": len(words),
        "ink_coverage": round(ink, 3),
    }
    with open(os.path.join(HERE, "density_report.json"), "w") as f:
        json.dump(report, f, indent=2)
    with open(os.path.join(HERE, "density_log.txt"), "w") as f:
        f.write(json.dumps(report, indent=2) + "\n")
        f.write("---- OCR (first 4000 chars) ----\n" + text[:4000] + "\n")
    print(f"stories: {len(found)}/39  missing: {missing}")
    print(f"regions: {len(regions)}/9  missing: {report['regions_missing']}")
    print(f"charts: {len(charts)}/2  map: {map_ok}  strip: {strip}")
    print(f"OCR words: {len(words)}  ink coverage: {ink:.3f}")
    ok = (len(found) >= 30 and len(regions) >= 6 and len(charts) >= 2
          and map_ok and len(strip) >= 3 and 0.05 <= ink <= 0.30)
    print("DENSITY GATE: " + ("PASS" if ok else "FAIL"))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
