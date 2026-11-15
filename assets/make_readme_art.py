#!/usr/bin/env python3
"""Generate the README illustrations in assets/readme/*.svg. Pure stdlib, deterministic.

Visual system matches assets/logo.svg: purple accent, film-grain dots, light/dark via prefers-color-scheme,
CSS-only animation that GitHub plays inside <img>, and a static state under prefers-reduced-motion.
Every number drawn here comes from README.md / CHANGELOG.md / core.py; nothing is invented.

Run: python3 assets/make_readme_art.py
"""
import random
from html import escape
from pathlib import Path

OUT = Path(__file__).parent / "readme"
OUT.mkdir(exist_ok=True)
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"

CSS = f"""
:root{{--bg:#0F0B1A;--panel:#17122A;--line:#3A3258;--fg:#FFFFFF;--dim:#A39EBB;--accent:#B880F2;--ok:#7BE0A4;--warn:#F2C46B;--grain:#8A84A0}}
@media (prefers-color-scheme: light){{:root{{--bg:#FBF9FF;--panel:#F1ECFB;--line:#CFC5EA;--fg:#15111F;--dim:#5E5878;--accent:#7A3FCB;--ok:#1E8A55;--warn:#A56A00;--grain:#6F6885}}}}
text{{font-family:{MONO};fill:var(--fg)}}
.dim{{fill:var(--dim)}}.acc{{fill:var(--accent)}}.ok{{fill:var(--ok)}}.warn{{fill:var(--warn)}}
.b{{font-weight:700}}
.panel{{fill:var(--panel);stroke:var(--line)}}
.hot{{fill:var(--panel);stroke:var(--accent);stroke-width:1.6}}
.flow{{stroke:var(--accent);stroke-width:2;fill:none;stroke-dasharray:6 8;animation:flow 1.4s linear infinite}}
@keyframes flow{{to{{stroke-dashoffset:-28}}}}
.fade{{animation:fade 7s ease-in-out infinite}}
@keyframes fade{{0%,8%{{opacity:.75}}38%{{opacity:.1}}52%,92%{{opacity:0}}100%{{opacity:.75}}}}
.sweep{{animation:sweep 7s ease-in-out infinite}}
@keyframes sweep{{0%,6%{{transform:translateX(0)}}50%,100%{{transform:translateX(var(--w))}}}}
.pulse{{animation:pulse 2s ease-in-out infinite}}
@keyframes pulse{{50%{{opacity:.35}}}}
@media (prefers-reduced-motion: reduce){{*{{animation:none!important}}.fade{{opacity:0}}}}
"""


def t(x, y, s, size=14, cls="", anchor="start", extra=""):
    c = f' class="{cls}"' if cls else ""
    return f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}"{c} {extra}>{escape(str(s))}</text>'


def svg(name, w, h, title, desc, body, css=""):
    s = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-labelledby="t d">
<title id="t">{escape(title)}</title>
<desc id="d">{escape(desc)}</desc>
<style>{CSS}{css}</style>
<defs>
<marker id="ar" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10z" fill="var(--accent)"/></marker>
<pattern id="dots" width="14" height="14" patternUnits="userSpaceOnUse"><circle cx="7" cy="7" r="1" fill="var(--grain)" opacity=".16"/></pattern>
</defs>
<rect width="{w}" height="{h}" rx="14" fill="var(--bg)"/>
<rect width="{w}" height="{h}" rx="14" fill="url(#dots)"/>
{body}
<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="14" fill="none" stroke="var(--line)"/>
</svg>
'''
    (OUT / name).write_text(s)
    print("wrote", name, f"{len(s) / 1024:.1f} KB")


def heading(kicker, title, sub):
    return (t(48, 58, kicker, 13, "acc") + t(48, 98, title, 32, "b") + t(48, 126, sub, 14, "dim"))


def arrow(x1, y1, x2, y2, dashed=True):
    cls = "flow" if dashed else ""
    return f'<line class="{cls}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="var(--accent)" stroke-width="2" marker-end="url(#ar)"/>'


# ───────────────────────── 1. HERO ─────────────────────────
def hero():
    W, H = 1600, 520
    rnd = random.Random(7)
    fx, fy, fw, fh = 1000, 90, 540, 320
    dots = []
    for _ in range(620):
        x = fx + 8 + rnd.random() * (fw - 16)
        y = fy + 8 + rnd.random() * (fh - 16)
        r = 1 + rnd.random() * 1.6
        d = (x - fx) / fw * 3.2
        dots.append(f'<circle class="fade" cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="var(--grain)" style="animation-delay:{d:.2f}s"/>')
    # a calm "scene": horizon, hills, sun, so the frame reads as an image
    scene = (
        f'<rect x="{fx}" y="{fy}" width="{fw}" height="{fh}" fill="var(--panel)"/>'
        f'<circle cx="{fx + 400}" cy="{fy + 90}" r="34" fill="var(--accent)" opacity=".85"/>'
        f'<path d="M{fx} {fy + 230} Q{fx + 120} {fy + 150} {fx + 240} {fy + 215} T{fx + 470} {fy + 200} T{fx + fw} {fy + 225} V{fy + fh} H{fx}z" fill="var(--accent)" opacity=".28"/>'
        f'<path d="M{fx} {fy + 262} Q{fx + 160} {fy + 210} {fx + 320} {fy + 258} T{fx + fw} {fy + 250} V{fy + fh} H{fx}z" fill="var(--accent)" opacity=".5"/>'
    )
    chips = ""
    labels = [("LOG", False), ("DENOISE", True), ("LUT", False), ("REC.709", False)]
    cx = 48
    for i, (lab, hot) in enumerate(labels):
        w = len(lab) * 11 + 36
        chips += f'<rect x="{cx}" y="318" width="{w}" height="40" rx="6" class="{"hot" if hot else "panel"}"/>'
        chips += t(cx + w / 2, 344, lab, 15, "b acc" if hot else "b", "middle")
        if i < len(labels) - 1:
            chips += arrow(cx + w + 4, 338, cx + w + 30, 338)
        cx += w + 36
    badges = ""
    bx = 48
    for lab in ["MIT", "ffmpeg hqdn3d", "python 3.9+", "stdlib only", "Claude Code skill"]:
        w = len(lab) * 8 + 24
        badges += f'<rect x="{bx}" y="440" width="{w}" height="28" rx="14" class="panel"/>' + t(bx + w / 2, 459, lab, 12, "dim", "middle")
        bx += w + 12
    body = (
        t(48, 62, "● v0.2  ·  CLASSICAL  ·  OPEN SOURCE", 13, "acc pulse")
        + t(48, 168, "quietframe", 84, "b", extra='letter-spacing="-3"')
        + '<rect x="48" y="184" width="300" height="5" rx="2" fill="var(--accent)"/>'
        + t(48, 232, "ISO-adaptive denoising for Log camera footage.", 24)
        + t(48, 264, "Denoise before the Log → Rec.709 transform. Strength measured per clip.", 16, "dim")
        + t(48, 292, "Canon Log 2 · Canon Log 3 · ffmpeg · Python · Claude Code skill", 14, "acc")
        + chips + badges
        + scene + "".join(dots)
        + f'<g style="--w:{fw}px"><g class="sweep"><rect x="{fx}" y="{fy}" width="2" height="{fh}" fill="var(--accent)"/></g></g>'
        + f'<rect x="{fx}" y="{fy}" width="{fw}" height="{fh}" fill="none" stroke="var(--line)"/>'
        + t(fx, fy + fh + 30, "ISO 6400 · Canon Log 3 · 4K 10-bit 4:2:2", 13, "dim")
        + t(fx + fw, fy + fh + 30, "noise 100% → 33%", 13, "ok b", "end")
        + t(fx + fw, fy + fh + 52, "detail kept 93%", 13, "dim", "end")
    )
    svg("hero.svg", W, H, "quietframe: ISO-adaptive denoising for Log camera footage",
        "Animated frame whose film grain fades away as a scan line sweeps across it, above the pipeline Log, denoise, LUT, Rec.709. Measured on a Canon EOS R6 V at ISO 6400: residual noise 33 percent, detail kept 93 percent.",
        body)


# ───────────────────────── 2. WHY BEFORE THE LUT ─────────────────────────
def why():
    W, H = 1600, 560
    rows = [
        ("LUT only", "no denoise", 100, 100, False),
        ("hqdn3d AFTER the LUT", "denoise in Rec.709", 50, 96, False),
        ("hqdn3d BEFORE the LUT", "hqdn3d=3:3:6:6 in Log", 33, 93, True),
    ]
    bx, bw = 560, 420
    body = heading("WHY THE ORDER MATTERS", "Denoise in Log, before the LUT",
                   "The display transform amplifies shadow noise. Remove it first, at the same cost in detail.")
    body += t(bx, 168, "RESIDUAL NOISE  (lower is better)", 12, "dim") + t(bx + bw + 160, 168, "DETAIL KEPT  (higher is better)", 12, "dim")
    for i, (a, b, noise, detail, hot) in enumerate(rows):
        y = 196 + i * 92
        body += f'<rect x="48" y="{y}" width="1504" height="76" rx="8" class="{"hot" if hot else "panel"}"/>'
        body += t(72, y + 34, a, 18, "b acc" if hot else "b") + t(72, y + 58, b, 13, "dim")
        body += f'<rect x="{bx}" y="{y + 26}" width="{bw}" height="24" rx="4" fill="var(--line)" opacity=".5"/>'
        body += f'<rect x="{bx}" y="{y + 26}" width="{bw * noise / 100:.0f}" height="24" rx="4" fill="{"var(--ok)" if hot else "var(--dim)"}"/>'
        body += t(bx + bw + 14, y + 45, f"{noise}%", 18, "b ok" if hot else "b")
        dx = bx + bw + 160
        body += f'<rect x="{dx}" y="{y + 26}" width="{bw * 0.6:.0f}" height="24" rx="4" fill="var(--line)" opacity=".5"/>'
        body += f'<rect x="{dx}" y="{y + 26}" width="{bw * 0.6 * detail / 100:.0f}" height="24" rx="4" fill="var(--accent)" opacity="{1 if hot else .55}"/>'
        body += t(dx + bw * 0.6 + 14, y + 45, f"{detail}%", 18, "b")
    body += t(48, 500, "Canon EOS R6 V · Canon Log 3 · 4K 10-bit 4:2:2 · ISO 6400 · flat-region noise estimate on one clip per ISO.", 13, "dim")
    body += t(48, 526, "Same detail, about a third of the noise left. That is the whole idea.", 14, "acc")
    svg("why-before-lut.svg", W, H, "Why denoise before the LUT: 33% residual noise versus 50% after",
        "Bar chart for ISO 6400 on a Canon EOS R6 V: LUT only keeps 100 percent noise, hqdn3d after the LUT leaves 50 percent noise and keeps 96 percent detail, hqdn3d before the LUT leaves 33 percent noise and keeps 93 percent detail.",
        body)


# ───────────────────────── 3. HOW IT WORKS ─────────────────────────
def how():
    W, H = 1600, 640
    steps = [
        ("01", "READ", "clip + .CPF", "Log profile from the sidecar,\nnever guessed"),
        ("02", "MEASURE", "5 full frames", "median of truncated-RMS\nHaar diagonal band → σ"),
        ("03", "STRENGTH", "σ → hqdn3d", "per-profile anchors,\nspatial clamped to 4.0"),
        ("04", "FILTER", "before the LUT", "hqdn3d chain, optional\n--lut my.cube"),
        ("05", "RENDER", "new file", "never overwrites input;\n--force to replace output"),
    ]
    cw, gap, x0, y = 276, 31, 48, 160
    body = heading("HOW IT WORKS", "Measure the clip, then choose the strength",
                   "ISO alone predicts noise poorly, so the strength comes from the noise measured in each clip.")
    for i, (n, name, art, sub) in enumerate(steps):
        x = x0 + i * (cw + gap)
        hot = i == 2
        body += f'<rect x="{x}" y="{y}" width="{cw}" height="210" rx="8" class="{"hot" if hot else "panel"}"/>'
        body += t(x + cw - 14, y + 70, n, 52, "dim", "end", 'opacity=".18" font-weight="700"')
        body += t(x + 18, y + 36, name, 19, "b acc" if hot else "b")
        body += f'<rect x="{x + 18}" y="{y + 90}" width="{cw - 36}" height="30" rx="5" fill="var(--bg)" stroke="var(--line)"/>'
        body += t(x + 30, y + 110, art, 13, "acc")
        for k, line in enumerate(sub.split("\n")):
            body += t(x + 18, y + 156 + k * 20, line, 12.5, "dim")
        if i < len(steps) - 1:
            body += arrow(x + cw + 3, y + 105, x + cw + gap - 3, y + 105)
    # fallback lane
    fx = x0 + 1 * (cw + gap)
    body += f'<path d="M{x0 + cw // 2} {y + 210} V{y + 262} H{fx + cw + gap + cw // 2} V{y + 216}" fill="none" stroke="var(--warn)" stroke-width="1.6" stroke-dasharray="4 6" marker-end="url(#ar)"/>'
    body += t(x0 + cw // 2 + 14, y + 284, "no numpy? fall back to the ISO table  (--mode iso, ISO from exiftool, never guessed)", 13, "warn")
    # outputs
    body += f'<rect x="48" y="480" width="1504" height="112" rx="8" class="panel"/>'
    body += t(72, 512, "COMMANDS", 12, "dim")
    cmds = [
        "python -m quietframe filter clip.mp4                 # measure noise, print the -vf chain",
        "python -m quietframe filter clip.mp4 --lut my.cube   # denoise, then your LUT",
        "python -m quietframe run clip.mp4 -o clean.mov --preset strong",
    ]
    for k, c in enumerate(cmds):
        body += t(72, 538 + k * 20, c, 13, "acc" if k == 2 else "")
    svg("how-it-works.svg", W, H, "How quietframe works: read, measure, strength, filter, render",
        "Five-step flow: read the Log profile from the .CPF sidecar, measure noise on five frames, map the noise to an hqdn3d strength clamped to 4.0, filter before the LUT, render to a new file. Without numpy an ISO table is used instead.",
        body)


# ───────────────────────── 4. NOISE VS ISO ─────────────────────────
def noise():
    W, H = 1600, 560
    # typical sigma by ISO (README): ~0.0008 up to ISO 2000, 0.0014 at 3200-6400, 0.002 at 51200
    pts = [(800, 0.0008), (2000, 0.0008), (3200, 0.0014), (6400, 0.0014), (51200, 0.002)]
    px, py, pw, ph = 130, 170, 860, 300
    import math
    lo, hi = math.log(800), math.log(51200)
    X = lambda iso: px + (math.log(iso) - lo) / (hi - lo) * pw
    Y = lambda s: py + ph - (s / 0.0024) * ph
    body = heading("MEASURE, DON'T TRUST ISO", "Noise rises with ISO, but varies per scene",
                   "21 clips, ISO 800 to 51200, Log domain. Two ISO 800 clips measured 0.0005 and 0.0011.")
    for s in (0.0005, 0.001, 0.0015, 0.002):
        body += f'<line x1="{px}" y1="{Y(s):.0f}" x2="{px + pw}" y2="{Y(s):.0f}" stroke="var(--line)" stroke-dasharray="3 6"/>' + t(px - 12, Y(s) + 4, f"{s:.4f}", 11, "dim", "end")
    body += t(px - 12, py - 14, "σ  (Log domain)", 11, "dim", "end")
    # ±30% band
    up = " ".join(f"{X(i):.0f},{Y(s * 1.3):.0f}" for i, s in pts)
    dn = " ".join(f"{X(i):.0f},{Y(s * 0.7):.0f}" for i, s in reversed(pts))
    body += f'<polygon points="{up} {dn}" fill="var(--accent)" opacity=".16"/>'
    line = " ".join(f"{X(i):.0f},{Y(s):.0f}" for i, s in pts)
    body += f'<polyline points="{line}" fill="none" stroke="var(--accent)" stroke-width="3"/>'
    for i, s in pts:
        body += f'<circle cx="{X(i):.0f}" cy="{Y(s):.0f}" r="5" fill="var(--bg)" stroke="var(--accent)" stroke-width="2.5"/>'
    for iso in (800, 1600, 3200, 6400, 12800, 25600, 51200):
        body += t(X(iso), py + ph + 26, iso, 12, "dim", "middle")
    body += t(px + pw / 2, py + ph + 52, "ISO", 12, "dim", "middle")
    # the two ISO 800 clips
    body += f'<circle cx="{X(800):.0f}" cy="{Y(0.0005):.0f}" r="6" fill="var(--warn)"/><circle cx="{X(800):.0f}" cy="{Y(0.0011):.0f}" r="6" fill="var(--warn)"/>'
    body += f'<line x1="{X(800):.0f}" y1="{Y(0.0005):.0f}" x2="{X(800):.0f}" y2="{Y(0.0011):.0f}" stroke="var(--warn)" stroke-width="1.5"/>'
    body += t(X(800) + 16, Y(0.0011) - 10, "two clips, same ISO 800", 12, "warn")
    body += t(X(800) + 16, Y(0.0011) + 6, "σ 0.0005 vs 0.0011", 12, "warn")
    # side facts
    fx = 1060
    facts = [("±30%", "treat any estimate as this accurate"), ("5 frames", "median of full frames per clip"),
             ("~20%", "per-frame spread"), ("~25%", "per-region spread")]
    for k, (big, small) in enumerate(facts):
        yy = 170 + k * 80
        body += f'<rect x="{fx}" y="{yy}" width="492" height="66" rx="8" class="panel"/>'
        body += t(fx + 20, yy + 42, big, 28, "b acc") + t(fx + 190, yy + 40, small, 13, "dim")
    body += t(48, 528, "Estimator: truncated-RMS of the Haar diagonal band (README, CHANGELOG 0.2.0). Spatial strength clamped to 4.0: at 4.5, ISO 51200 kept only 92% detail.", 12, "dim")
    svg("noise-vs-iso.svg", W, H, "Noise versus ISO for Log footage: why quietframe measures each clip",
        "Line chart of typical Log-domain noise sigma by ISO from 800 to 51200 with a plus or minus 30 percent band, and two ISO 800 clips measuring 0.0005 and 0.0011.",
        body)


# ───────────────────────── 5. CLAUDE SKILL ─────────────────────────
def skill():
    W, H = 1600, 520
    rules = [
        ("1", "Originals are never modified", "reads the source, writes a new file, refuses to overwrite its input"),
        ("2", "Profile from the .CPF sidecar", "same camera shoots Canon Log 2 one trip and Log 3 the next, never guessed"),
        ("3", "Get the filter chain", "python -m quietframe filter <clip> [--lut file.cube]"),
        ("4", "Test before a batch", "render a short test, compare a 100% crop to the undenoised clip"),
        ("5", "Report [untested tier]", "an ISO, noise level or profile that was not validated is never called proven"),
        ("6", "Calibrate another camera", "python -m quietframe calibrate @clips.txt -o noise.csv  (never publish the path column)"),
    ]
    body = heading("CLAUDE CODE SKILL", "Ask Claude to denoise your Log footage",
                   "Copy skill/SKILL.md into your skills folder. Claude follows these rules every time.")
    for i, (n, a, b) in enumerate(rules):
        col, row = i % 2, i // 2
        x, y = 48 + col * 760, 160 + row * 92
        warn = i == 4
        body += f'<rect x="{x}" y="{y}" width="744" height="76" rx="8" class="{"hot" if warn else "panel"}"/>'
        body += t(x + 22, y + 48, n, 34, "b acc" if warn else "b dim", extra='opacity=".9"')
        body += t(x + 62, y + 32, a, 17, "b")
        body += t(x + 62, y + 56, b, 12, "dim")
    body += f'<rect x="48" y="450" width="1504" height="44" rx="8" class="panel"/>'
    body += t(72, 478, "“My clips look grainy, denoise them before I grade.”", 15, "acc") + t(1528, 478, "triggers the skill", 13, "dim", "end")
    svg("claude-skill.svg", W, H, "quietframe as a Claude Code skill: six rules for safe denoising",
        "Six rules the skill enforces: never modify originals, read the Log profile from the CPF sidecar, get the filter chain, test before a batch, report untested tiers, and calibrate other cameras.",
        body)


if __name__ == "__main__":
    hero(); why(); how(); noise(); skill()
