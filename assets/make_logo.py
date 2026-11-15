#!/usr/bin/env python3
"""Generate assets/logo.svg: pixel-art camera on a gimbal, a purple orbit with a comet, and grain that fades out
("quiet frame"). Pure stdlib; every shape sits on a 48x48 pixel grid. Run: python3 assets/make_logo.py"""
import math
import random
from pathlib import Path

G = 48  # grid units; each unit is one "pixel"

def rect_outline(x0, y0, x1, y1):  # 1-unit outline, inclusive corners
    cells = set()
    for x in range(x0, x1 + 1):
        cells |= {(x, y0), (x, y1)}
    for y in range(y0, y1 + 1):
        cells |= {(x0, y), (x1, y)}
    return cells

def hline(x0, x1, y): return {(x, y) for x in range(x0, x1 + 1)}
def vline(x, y0, y1): return {(x, y) for y in range(y0, y1 + 1)}

# --- camera + gimbal (drawn in the foreground colour) ---
body = rect_outline(15, 13, 26, 22) | hline(18, 22, 12)  # body + viewfinder bump
lens = vline(28, 15, 20) | hline(28, 31, 15) | hline(28, 31, 20) | vline(32, 14, 21) | {(27, 17), (27, 18)}
camera = body | lens
arm = vline(12, 16, 23) | hline(11, 13, 16) | hline(12, 19, 24) | {(11, 17)}
pole = hline(20, 23, 21) | rect_outline(19, 23, 24, 25) | rect_outline(20, 26, 23, 34) | {(22, 28), (22, 29)}
gimbal = arm | pole

# --- orbit (purple): ellipse sampled onto the grid, ordered by angle for the comet animation ---
cx, cy, rx, ry, tilt = 24.0, 25.0, 17.0, 5.6, math.radians(-14)
orbit = {}
for i in range(720):
    a = 2 * math.pi * i / 720
    x, y = rx * math.cos(a), ry * math.sin(a)
    px = cx + x * math.cos(tilt) - y * math.sin(tilt)
    py = cy + x * math.sin(tilt) + y * math.cos(tilt)
    front = math.sin(a) > 0  # lower half passes in front of the pole
    cell = (round(px), round(py))
    if (not front) and abs(a - 1.5 * math.pi) < 0.9:  # gap behind the camera: the orbit hides behind it
        continue
    orbit.setdefault(cell, (a, front))
    if front:  # thicker swoosh in front
        orbit.setdefault((round(px), round(py) + 1), (a, front))
cells = sorted(orbit.items(), key=lambda kv: kv[1][0])
# tidy: drop orbit cells that would sit on the camera body outline
blocked = camera | arm
cells = [(c, af) for c, af in cells if c not in blocked]
speed_lines = hline(13, 16, 32) | hline(19, 21, 34) | hline(31, 33, 7)

# --- grain: dim random cells away from the drawing ---
rng = random.Random(7)
occupied = camera | gimbal | {c for c, _ in cells}
grain = []
while len(grain) < 32:
    c = (rng.randrange(3, G - 3), rng.randrange(3, G - 3))
    if c in occupied or any(abs(c[0] - o[0]) < 2 and abs(c[1] - o[1]) < 2 for o in occupied | set(grain)):
        continue
    grain.append(c)

def r(c, cls="", extra=""):
    return f'<rect x="{c[0]}" y="{c[1]}" width="1" height="1"{(" class=%r" % cls).replace(chr(39), chr(34)) if cls else ""}{extra}/>'

allc = camera | gimbal | {c for c, _ in cells}
dx = round(G / 2 - (min(x for x, _ in allc) + max(x for x, _ in allc) + 1) / 2)
dy = round(G / 2 - (min(y for _, y in allc) + max(y for _, y in allc) + 1) / 2)
DUR = 6.0
def orbit_rects(front_only):
    return "".join(
        f'<rect x="{c[0]}" y="{c[1]}" width="1" height="1" style="animation-delay:{-(a / (2 * math.pi)) * DUR * 0.55:.3f}s"/>'
        for c, (a, front) in cells if front == front_only)
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {G} {G}" width="480" height="480" role="img"
     aria-labelledby="t d" shape-rendering="crispEdges">
  <title id="t">quietframe</title>
  <desc id="d">Pixel-art camera on a gimbal inside a purple orbit. Film grain fades away and the camera settles.</desc>
  <style>
    :root {{ --fg:#FFFFFF; --accent:#B880F2; --grain:#8A84A0; }}
    @media (prefers-color-scheme: light) {{ :root {{ --fg:#15111F; --accent:#8A4BD6; --grain:#6F6885; }} }}
    .fg {{ fill:var(--fg) }}
    .orbit rect {{ fill:var(--accent); opacity:.6; animation: comet {DUR}s linear infinite; }}
    .front rect {{ opacity:.95; animation-name: comet-front; }}
    .lines rect {{ fill:var(--accent); opacity:.7 }}
    .grain rect {{ fill:var(--grain); animation: denoise {DUR}s ease-in-out infinite; opacity:0 }}
    .rig {{ animation: settle {DUR}s steps(1,end) infinite; }}
    @keyframes comet {{ 0%{{opacity:1}} 14%{{opacity:.6}} 100%{{opacity:.6}} }}
    @keyframes comet-front {{ 0%{{opacity:1}} 14%{{opacity:.95}} 100%{{opacity:.95}} }}
    @keyframes denoise {{ 0%,6%{{opacity:.5}} 32%{{opacity:.35}} 48%,92%{{opacity:0}} 100%{{opacity:.5}} }}
    @keyframes settle {{ 0%{{transform:translate(0,0)}} 4%{{transform:translate(1px,0)}} 8%{{transform:translate(0,1px)}}
      12%{{transform:translate(-1px,0)}} 16%{{transform:translate(0,-1px)}} 20%{{transform:translate(1px,1px)}}
      24%{{transform:translate(0,0)}} 28%{{transform:translate(-1px,0)}} 32%{{transform:translate(0,0)}} 100%{{transform:translate(0,0)}} }}
    @media (prefers-reduced-motion: reduce) {{ .orbit rect,.grain rect,.rig {{ animation:none }} .grain rect {{ opacity:0 }} .orbit rect {{ opacity:.95 }} }}
  </style>
  <g transform="translate({dx} {dy})">
  <g class="grain">{"".join(r(c, extra=f' style="animation-delay:{(i % 7) * 0.09:.2f}s"') for i, c in enumerate(grain))}</g>
  <g class="orbit">{orbit_rects(False)}</g>
  <g class="rig fg">{"".join(r(c) for c in sorted(gimbal | camera))}</g>
  <g class="orbit front">{orbit_rects(True)}</g>
  <g class="lines">{"".join(r(c) for c in sorted(speed_lines))}</g>
  </g>
</svg>
'''
Path(__file__).with_name("logo.svg").write_text(svg, encoding="utf-8")
print(f"logo.svg: {len(svg) / 1024:.1f} KB, {len(cells)} orbit cells, {len(grain)} grain cells")
