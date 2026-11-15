from __future__ import annotations

import argparse
import shutil
import subprocess
import sys

from . import __version__
from .core import PRESETS, build_filter, plan_for_iso, read_iso


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="quietframe", description="ISO-adaptive denoise for Log footage.")
    ap.add_argument("--version", action="version", version=__version__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, hlp in (("filter", "print the ffmpeg -vf chain"), ("run", "render a denoised clip")):
        s = sub.add_parser(name, help=hlp)
        s.add_argument("input")
        s.add_argument("--iso", type=int, help="override ISO (default: read via exiftool)")
        s.add_argument("--preset", choices=sorted(PRESETS), default="normal")
        s.add_argument("--lut", help="optional .cube applied right after the denoise")
        s.add_argument("--range", choices=["full", "auto"], default="full",
                       help="full = treat source as full range (Canon Log R6 V); auto = leave flags alone")
        if name == "run":
            s.add_argument("-o", "--output", required=True)
    a = ap.parse_args(argv)

    iso = a.iso if a.iso is not None else read_iso(a.input)
    plan = plan_for_iso(iso, a.preset)
    vf = build_filter(plan, a.lut, a.range == "full")
    note = f"ISO {iso}" if iso else "ISO unknown (mid-strength fallback)"
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
