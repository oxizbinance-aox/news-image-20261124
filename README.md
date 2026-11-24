# Tuesday 24 November 2026 in one page — 39 stories, 9 regions

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/oxizbinance-aox/news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/oxizbinance-aox/news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

Sum up Tuesday 24 November 2026's world news in one image — **39 stories,
9 regions**: 3 lead stories with hand-drawn pictograms, 8 illustrated mid
panels, a world map with 10 numbered hotspots, 2 charts, a big data strip,
and a numbered list of the remaining 28 stories. Every story is dated
24 November 2026.

- Bounty: https://make.fun/bounty/news-image-20261124
- Entry image: `entry.png` — 1024×1024, 171,857 bytes
- sha256: `1312845031e763df3f7c1f78c49398c4bb703d822f16b61bbda256abdecfec93`
- Deterministic: two runs of `draw_news24.py` and two runs of `main.ts`
  write byte-identical `entry.png` (sha256 above).
- **v2 rebuild note:** this entry was rebuilt fresh in a session that
  started after the competition opened (00:00 UTC 24 Nov 2026). The
  earlier v1 build started 4 minutes before opening and cannot be
  entered (`thinking_in_window`); no v1 source was read or copied —
  `main.ts` and `draw_news24.py` here were written fresh from this
  design in the new session.

## How it runs

```
python3 draw_news24.py   # renders entry.png (PIL, deterministic, no network)
MAKEFUN_OUTPUT_DIR=out node main.ts   # copies entry.png to out/entry.png
```

`main.ts` (Node 22, stdlib only) resolves `entry.png` relative to itself
via `import.meta.url` and verifies the copy byte-for-byte (SHA-256, PNG
magic bytes, and 1024×1024 IHDR dimensions). No network at run time.

## QC gates (all logged in the repo)

- **Density counter** (`density_check.py`, tesseract OCR on the rendered
  image): 39/39 headline keywords found, 9/9 regions, 2 charts, map
  present, data-strip numbers present, 576 OCR words, ink coverage 0.128.
- **Layout validator** (built into `draw_news24.py`, PIL text bounding
  boxes): 167 text boxes, 0 out-of-bounds, 0 overlaps.
- **Zoom QC:** viewed at full size and at 300 px wide — header, data
  strip, lead headlines, map hotspots and chart titles stay legible;
  no garbled text anywhere.
- **Determinism**: draw script 2× identical sha256; `main.ts` 2× identical.

## The 39 stories (all dated 24 November 2026)

### Leads
1. **NORTH AMERICA · MARKETS — Huang is back, Nvidia soars 36.6%.**
   Board reinstates Huang as chief executive; Wall Street rebounds
   as the AI rout reverses. (Go Herald Now, 24 Nov)
2. **EUROPE · UKRAINE — Odesa dark and cold after Russian strikes.**
   Strikes knock out power, heat and water across the Black Sea port city.
   (m.autoys.eu, 24 Nov)
3. **ASIA-PACIFIC · TAIWAN — 12 Chinese warships circle Taiwan.**
   Drones and helicopters enter the island's air-defence zone as Taipei
   tracks the flotilla. (Geopolitiki live, 24 Nov)

### Illustrated mid panels (04–11)
4. Delta outage grounds 3,000+ US flights — system failure hits key US hubs.
   (m.autoys.eu)
5. Ukraine drones set two Russian refineries ablaze — fires at Perm and
   Rostov plants. (Geopolitiki live)
6. Houthis say they hit Saudi Arabia's Rabigh refinery — Houthi claim;
   Riyadh silent so far. (Geopolitiki live) — tagged CLAIM.
7. Seoul names new foreign minister and spy chief — reshuffle amid US
   alliance worries. (m.autoys.eu)
8. 24 dead as boat capsizes on way to a Nigeria funeral. (m.autoys.eu)
9. Beaver Supermoon rises tonight, first of four — first of four supermoons
   to February 2027. (Sky at Night)
10. 16 cartel suspects killed in 'El Chapo Isidro' arrest — Mexico reports
    16 killed in raid. (m.autoys.eu)
11. Hobart stadium bill jumps to $1.23 billion — Macquarie Point cost hits
    $1.23bn. (Go Herald Now)

### Numbered list (12–39)
12. Armenia drops Karabakh claim in draft constitution (m.autoys.eu)
13. Cyprus expels two Russian diplomats over spying claims (m.autoys.eu)
14. Estonia answers Russia's airspace allegation firmly (m.autoys.eu)
15. Bomb threats close schools in Germany and Denmark (m.autoys.eu)
16. Merz: keeping Ukraine out of NATO in 2008 was wrong (m.autoys.eu)
17. UK starts world's largest AI breast-screening trial (m.autoys.eu)
18. NATO offers Poland 'significant backing' after incursion (m.autoys.eu)
19. Russian casualties outpace monthly recruiting, US says (m.autoys.eu)
20. Two killed as helicopter crashes near Napa wineries (m.autoys.eu)
21. US states sue SpaceX over Grok's sexual images (m.autoys.eu)
22. Army invokes emergency powers for Iowa munitions blast (m.autoys.eu)
23. US to host the 2031 Women's World Cup, FIFA says (m.autoys.eu)
24. Schumer warns of security risks in Huang's return (m.autoys.eu)
25. Panama and First Quantum resume Cobre mine talks (m.autoys.eu)
26. Storm forces thousands to flee in Brazil (m.autoys.eu)
27. Gaza's soil and water poisoned by war, report finds (Disclosure News —
    Oxfam / Conflict and Environment Observatory report, released 24 Nov)
28. France condemns settler attacks on Palestinians (m.autoys.eu)
29. Lebanon condemns Israeli officer's school visit (m.autoys.eu)
30. Trump faces pivotal decision on Iran deal (m.autoys.eu)
31. Eastern Libya appeals to UN over Russian warship (Geopolitiki live)
32. Fighting traps Ebola responders in Ituri (Geopolitiki live / WHO)
33. Seoul denies navy unit is bound for Iran war (Geopolitiki live)
34. Taiwan eases margin rules from today after rout (The Ledger Asia —
    threshold cut to 120% effective 24 Nov)
35. South Korea tracks North Korean ship off its coast (m.autoys.eu)
36. Taliban erases women's names from Balkh documents (Disclosure News)
37. Australia budget update as rents hit 14-year low (Go Herald Now)
38. UN chief urges global AI safety rules within a year (m.autoys.eu)
39. China's nuclear build-up 'turning world dangerous', expert warns
    (m.autoys.eu)

## Charts (real numbers, labelled with their dates)

- **Friday's falls, 20 Nov** (The Sun Report): Taiwan −6.7%, S. Korea −5.2%,
  Nikkei −5.0%, Shanghai −2.1%, ASX −1.6% — the rout Huang's return reverses.
- **Tremors in the last 24 hours, magnitude** (Liveuamap): Vanuatu 6.5,
  Timor-Leste 5.4, Urumqi 5.1, Kuqa 4.9, Palau 4.8, Bitung 4.7.

## Data strip

+36.6% Nvidia surges as Huang returns · 6.5 Vanuatu quake, no tsunami ·
3,000+ Delta flights hit by outage · 12 Chinese warships off Taiwan.

## Excluded (considered, rejected — wrong date)

- COP31 ends without a climate pact — 22 Nov (PANA).
- Russian warship Merkury sunk off Benghazi — first reported 22 Nov
  (Naval News); only the 24 Nov follow-ups (Albania's denial, eastern
  Libya's UN appeal) are used, as story 31.
- Dymer strike, toll 11 — the strike was 23 Nov; the 24 Nov toll update
  was not counted as a separate story.
- Brazil Supreme Court summons Flávio Bolsonaro — 23 Nov.
- Zanzibar hotel fire — 21 Nov. Indonesia candy-factory fire — 23 Nov.
- US sanctions on Iran 'shadow banking' networks — 23 Nov.
- Miley Cyrus wedding; Spain general election set for 29 Nov; Athens
  Acropolis Museum reopens; EU adds Rinaldo Nazzaro to terror list;
  Democrats reach 258 House seats — all first reported 23 Nov.
- Taiwan TAIEX rebounds 2.16% — 23 Nov close.

## Verification tags

REPORTED = one outlet · CLAIM = one side's account (story 06, the Houthi
claim) · OFFICIAL = on the record. Tags appear on the 3 leads and the
8 mid panels; the full source per story is listed above.
