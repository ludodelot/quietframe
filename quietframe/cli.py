from __future__ import annotations

import argparse
import shutil
import subprocess
import sys

from . import __version__
from . import measure
from .core import PRESETS, build_filter, plan_for_iso, plan_for_sigma, read_iso


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="quietframe", description="ISO-adaptive denoise for Log footage.")
    ap.add_argument("--version", action="version", version=__version__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, hlp in (("filter", "print the ffmpeg -vf chain"), ("run", "render a denoised clip")):
        s = sub.add_parser(name, help=hlp)
        s.add_argument("input")
        s.add_argument("--iso", type=int, help="override ISO (default: read via exiftool)")
        s.add_argument("--mode", choices=["auto", "measure", "iso"], default="auto",
                       help="measure = noise measured from the clip (needs numpy); iso = ISO table; "
                            "auto = measure if numpy is available, else ISO")
        s.add_argument("--preset", choices=sorted(PRESETS), default="normal")
        s.add_argument("--lut", help="optional .cube applied right after the denoise")
        s.add_argument("--range", choices=["full", "auto"], default="full",
                       help="full = treat source as full range (Canon Log R6 V); auto = leave flags alone")
        if name == "run":
            s.add_argument("-o", "--output", required=True)
    c = sub.add_parser("calibrate", help="measure noise of many clips into a CSV (read-only)")
    c.add_argument("inputs", nargs="+", help="clip files, or a text file with one path per line (prefix with @)")
    c.add_argument("-o", "--output", required=True)
    c.add_argument("--jobs", type=int, default=4)
    a = ap.parse_args(argv)
    if a.cmd == "calibrate":
        if not measure.available():
            sys.exit("calibrate needs numpy (pip install numpy)")
        from .calibrate import survey
        paths = []
        for item in a.inputs:
            paths += [l.strip() for l in open(item[1:]) if l.strip()] if item.startswith("@") else [item]
        print(f"surveyed {survey(paths, a.output, a.jobs, lambda m: print(m, file=sys.stderr, flush=True))} clips -> {a.output}")
        return 0

    sigma = None
    if a.iso is None and a.mode in ("auto", "measure"):
        if a.mode == "measure" and not measure.available():
            sys.exit("--mode measure needs numpy (pip install numpy)")
        sigma = measure.noise_sigma(a.input)
    if sigma is not None:
        plan = plan_for_sigma(sigma, a.preset)
        note = f"measured noise sigma={sigma:.5f}"
    else:
        iso = a.iso if a.iso is not None else read_iso(a.input)
        plan = plan_for_iso(iso, a.preset)
        note = f"ISO {iso}" if iso else "ISO unknown (mid-strength fallback)"
    vf = build_filter(plan, a.lut, a.range == "full")
    print(f"# {note} -> {plan.hqdn3d}" + ("" if plan.tested else "  [untested tier]"), file=sys.stderr)
    if a.cmd == "filter":
        print(vf)
        return 0
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg not found")
    cmd = ["ffmpeg", "-y", "-i", a.input, "-vf", vf, "-c:v", "prores_ks", "-profile:v", "3",
           "-pix_fmt", "yuv422p10le", "-c:a", "copy", a.output]
    return subprocess.run(cmd).returncode


if __name__ == "__main__":
    raise SystemExit(main())
