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
    labels = [("LOG", False), ("LUT", False), ("DENOISE", True), ("REC.709", False)]
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
        t(48, 62, "● v1.0  ·  CLASSICAL  ·  OPEN SOURCE", 13, "acc pulse")
        + t(48, 168, "quietframe", 84, "b", extra='letter-spacing="-3"')
        + '<rect x="48" y="184" width="300" height="5" rx="2" fill="var(--accent)"/>'
        + t(48, 232, "Noise-adaptive denoising for Log camera footage.", 24)
        + t(48, 264, "Denoise after the Log → Rec.709 LUT. Strength measured per clip.", 16, "dim")
        + t(48, 292, "Canon Log 2 · Canon Log 3 · ffmpeg · Python · Claude Code skill", 14, "acc")
        + chips + badges
        + scene + "".join(dots)
        + f'<g style="--w:{fw}px"><g class="sweep"><rect x="{fx}" y="{fy}" width="2" height="{fh}" fill="var(--accent)"/></g></g>'
        + f'<rect x="{fx}" y="{fy}" width="{fw}" height="{fh}" fill="none" stroke="var(--line)"/>'
        + t(fx, fy + fh + 30, "ISO 6400 · Canon Log 2 · 4K 10-bit 4:2:2", 13, "dim")
        + t(fx + fw, fy + fh + 30, "noise 100% → 44%", 13, "ok b", "end")
        + t(fx + fw, fy + fh + 52, "detail kept 96%", 13, "dim", "end")
    )
    svg("hero.svg", W, H, "quietframe: noise-adaptive denoising for Log camera footage",
        "Animated frame whose film grain fades away as a scan line sweeps across it, above the pipeline Log, LUT, denoise, Rec.709. Measured on a Canon EOS R6 V in Canon Log 2 at ISO 6400: residual noise 44 percent, detail kept 96 percent.",
        body)


# ───────────────────────── 2. WHERE IN THE CHAIN ─────────────────────────
def why():
    """Detail kept vs noise left for hqdn3d before vs after the LUT, 3 real clips, strengths 1.5 / 2 / 3 / 4.
    Numbers: equal-strength sweep measured with the correct Log 2 / Log 3 LUT (README, 'Where to denoise')."""
    W, H = 1600, 560
    panels = [
        ("Canon Log 2 · ISO 6400", [(63, 97), (54, 96), (46, 94), (43, 92)], [(70, 98), (59, 97), (44, 96), (36, 94)]),
        ("Canon Log 2 · ISO 51200", [(78, 99), (68, 98), (55, 95), (46, 93)], [(87, 99), (79, 99), (65, 98), (55, 96)]),
        ("Canon Log 3 · ISO 8299", [(62, 96), (55, 94), (49, 91), (45, 87)], [(76, 99), (68, 98), (56, 96), (47, 94)]),
    ]
    body = heading("WHERE IN THE CHAIN", "Denoise after the LUT: more detail at the same noise",
                   "Each line is a strength sweep (1.5, 2, 3, 4). Further right = less noise left. Higher = more detail kept.")
    pw, ph, gap, x0, y0 = 440, 250, 72, 80, 190
    X = lambda n, ox: ox + (100 - n) / 70 * pw       # noise left 100% .. 30%
    Y = lambda d: y0 + ph - (d - 85) / 15 * ph        # detail 85 .. 100
    for k, (title, before, after) in enumerate(panels):
        ox = x0 + k * (pw + gap)
        body += t(ox, y0 - 18, title, 15, "b")
        for d in (88, 92, 96, 100):
            body += f'<line x1="{ox}" y1="{Y(d):.0f}" x2="{ox + pw}" y2="{Y(d):.0f}" stroke="var(--line)" stroke-dasharray="3 6"/>'
            if k == 0:
                body += t(ox - 10, Y(d) + 4, f"{d}%", 11, "dim", "end")
        for n in (100, 80, 60, 40):
            body += t(X(n, ox), y0 + ph + 22, f"{n}%", 11, "dim", "middle")
        body += t(ox + pw / 2, y0 + ph + 44, "noise left", 11, "dim", "middle")
        for pts, color, dash in ((before, "var(--dim)", "6 5"), (after, "var(--accent)", "")):
            line = " ".join(f"{X(n, ox):.0f},{Y(d):.0f}" for n, d in pts)
            body += f'<polyline points="{line}" fill="none" stroke="{color}" stroke-width="3"' + (f' stroke-dasharray="{dash}"' if dash else "") + "/>"
            for n, d in pts:
                body += f'<circle cx="{X(n, ox):.0f}" cy="{Y(d):.0f}" r="4.5" fill="var(--bg)" stroke="{color}" stroke-width="2.5"/>'
    lx = 80
    body += f'<line x1="{lx}" y1="500" x2="{lx + 40}" y2="500" stroke="var(--accent)" stroke-width="3"/>' + t(lx + 52, 505, "hqdn3d AFTER the LUT (default)", 13, "b acc")
    body += f'<line x1="{lx + 330}" y1="500" x2="{lx + 370}" y2="500" stroke="var(--dim)" stroke-width="3" stroke-dasharray="6 5"/>' + t(lx + 382, 505, "BEFORE the LUT (--stage before)", 13, "dim")
    body += t(48, 536, "Canon EOS R6 V · 4K 10-bit · measured with the correct LUT for each Log curve · one clip per panel · 4 frames per point.", 12, "dim")
    svg("stage-comparison.svg", W, H, "Denoise after the LUT keeps more detail at the same noise",
        "Three panels, one clip each (Canon Log 2 ISO 6400, Canon Log 2 ISO 51200, Canon Log 3 ISO 8299), plotting detail kept against noise left for hqdn3d before and after the LUT. At the same residual noise, denoising after the LUT keeps the same or more detail in all three, most clearly in Canon Log 3.",
        body)


# ───────────────────────── 3. HOW IT WORKS ─────────────────────────
def how():
    W, H = 1600, 640
    steps = [
        ("01", "READ", "clip + .CPF", "Log profile from the sidecar,\nnever guessed"),
        ("02", "MEASURE", "5 full frames", "median of truncated-RMS\nHaar diagonal band → σ"),
        ("03", "STRENGTH", "σ → hqdn3d", "per-profile anchors,\nspatial clamped to 4.0"),
        ("04", "FILTER", "after the LUT", "your LUT first, then the\nhqdn3d chain (--lut my.cube)"),
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
        "python -m quietframe filter clip.mp4 --lut my.cube   # your LUT, then denoise",
        "python -m quietframe run clip.mp4 -o clean.mov --preset strong",
    ]
    for k, c in enumerate(cmds):
        body += t(72, 538 + k * 20, c, 13, "acc" if k == 2 else "")
    svg("how-it-works.svg", W, H, "How quietframe works: read, measure, strength, filter, render",
        "Five-step flow: read the Log profile from the .CPF sidecar, measure noise on five frames, map the noise to an hqdn3d strength clamped to 4.0, apply your LUT and then the filter, render to a new file. Without numpy an ISO table is used instead.",
        body)


# ───────────────────────── 4. NOISE VS ISO ─────────────────────────
def noise():
    """Noise vs ISO from the calibration survey (assets/calibration_summary.json: aggregates, no paths)."""
    import json
    import math
    from pathlib import Path
    data = json.loads((Path(__file__).with_name("calibration_summary.json")).read_text())["profiles"]
    n_clips = sum(p["clips"] for p in data.values())
    W, H = 1600, 560
    px, py, pw, ph = 130, 170, 860, 300
    lo, hi = math.log(800), math.log(51200)
    X = lambda iso: px + (math.log(iso) - lo) / (hi - lo) * pw
    Y = lambda s_: py + ph - (s_ / 0.0024) * ph
    body = heading("MEASURE, DON'T TRUST ISO", "Noise rises with ISO, but varies per clip and per Log curve",
                   f"{n_clips} Canon EOS R6 V clips, ISO 800 to 51200, Log domain. Dots: median. Bars: 10th to 90th percentile.")
    for s_ in (0.0005, 0.001, 0.0015, 0.002):
        body += f'<line x1="{px}" y1="{Y(s_):.0f}" x2="{px + pw}" y2="{Y(s_):.0f}" stroke="var(--line)" stroke-dasharray="3 6"/>' + t(px - 12, Y(s_) + 4, f"{s_:.4f}", 11, "dim", "end")
    body += t(px - 12, py - 14, "σ  (Log domain)", 11, "dim", "end")
    series = (("canon-log2", "Canon Log 2", "var(--accent)", -9), ("canon-log3", "Canon Log 3", "var(--warn)", 9))
    for key, label, color, dx in series:
        rows = data[key]["buckets"]
        line = " ".join(f"{X(r['iso_median']) + dx:.0f},{Y(r['p50']):.0f}" for r in rows)
        body += f'<polyline points="{line}" fill="none" stroke="{color}" stroke-width="3"/>'
        for r in rows:
            x = X(r["iso_median"]) + dx
            body += f'<line x1="{x:.0f}" y1="{Y(r["p10"]):.0f}" x2="{x:.0f}" y2="{Y(r["p90"]):.0f}" stroke="{color}" stroke-width="2" opacity=".55"/>'
            body += f'<circle cx="{x:.0f}" cy="{Y(r["p50"]):.0f}" r="5" fill="var(--bg)" stroke="{color}" stroke-width="2.5"/>'
    for iso in (800, 1600, 3200, 6400, 12800, 25600, 51200):
        body += t(X(iso), py + ph + 26, iso, 12, "dim", "middle")
    body += t(px + pw / 2, py + ph + 46, "ISO", 12, "dim", "middle")
    for k, (key, label, color, _) in enumerate(series):
        body += f'<circle cx="{px + 70 + k * 200}" cy="{py - 18}" r="5" fill="{color}"/>' + t(px + 82 + k * 200, py - 14, f"{label} ({data[key]['clips']} clips)", 12, "dim")
    # side facts
    fx = 1060
    facts = [("±30%", "treat any estimate as this accurate"), ("5 frames", "median of full frames per clip"),
             ("~20%", "per-frame spread"), ("~25%", "per-region spread")]
    for k, (big, small) in enumerate(facts):
        yy = 170 + k * 80
        body += f'<rect x="{fx}" y="{yy}" width="492" height="66" rx="8" class="panel"/>'
        body += t(fx + 20, yy + 42, big, 28, "b acc") + t(fx + 190, yy + 40, small, 13, "dim")
    body += t(48, 544, "Estimator: truncated-RMS of the Haar diagonal band. Spatial strength clamped to 4.0: at 4.5, ISO 51200 kept only 92% detail.", 12, "dim")
    svg("noise-vs-iso.svg", W, H, "Noise versus ISO for Log footage: why quietframe measures each clip",
        f"Median Log-domain noise sigma by ISO bucket for Canon Log 2 and Canon Log 3 on {n_clips} Canon EOS R6 V clips, with 10th to 90th percentile bars. Log 2 rises from about 0.0008 to 0.0014; Log 3 from 0.0008 to 0.0011; at base ISO clips range from 0.0005 to 0.0012.",
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
