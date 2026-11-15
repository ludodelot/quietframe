"""Core logic: ISO -> denoise strength -> ffmpeg filter chain. Stdlib only."""
from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass

# Provisional tiers (v1). Measured on a Canon EOS R6 V, Canon Log 3, 4K 10-bit 4:2:2:
# hqdn3d=3:3:6:6 cut ~67% of residual noise at ISO 6400 while keeping ~93% of detail.
# Lower ISOs use gentler values. v2 replaces this table with a calibrated noise-vs-ISO curve.
# (max_iso, luma_spatial, chroma_spatial, luma_temporal, chroma_temporal, tested)
TIERS = [
    (1000, 1.5, 1.5, 3.0, 3.0, True),
    (2500, 2.0, 2.0, 4.0, 4.0, False),
    (8000, 3.0, 3.0, 6.0, 6.0, True),
    (10**9, 4.0, 4.0, 8.0, 8.0, False),
]
PRESETS = {"light": 0.6, "normal": 1.0, "strong": 1.4}

# Measured-noise anchors per Log profile: (sigma -> spatial 1.5, sigma -> spatial 3.0).
# Noise in code values depends on the Log curve, so each profile has its own pair. Sigma is the Log-domain
# estimate from measure.py. Each pair is the median sigma of the clips shot at base ISO (<=1000) and of those at
# high ISO (>=5500), from a Canon EOS R6 V survey (Log 2: 160 clips; Log 3: 196 clips; see README).
ANCHORS = {
    "canon-log2": (0.00076, 0.00140),
    "canon-log3": (0.00082, 0.00106),
}
DEFAULT_PROFILE = "canon-log2"
SPATIAL_LO, SPATIAL_HI = 1.5, 3.0
SPATIAL_MIN, SPATIAL_MAX = 1.0, 4.0


@dataclass(frozen=True)
class Plan:
    iso: int | None
    params: tuple[float, float, float, float]
    tested: bool

    @property
    def hqdn3d(self) -> str:
        return "hqdn3d=" + ":".join(f"{p:g}" for p in self.params)


def plan_for_iso(iso: int | None, preset: str = "normal") -> Plan:
    """Pick hqdn3d parameters for an ISO. Unknown ISO falls back to the mid tier."""
    if preset not in PRESETS:
        raise ValueError(f"preset must be one of {sorted(PRESETS)}")
    k = PRESETS[preset]
    if iso is None:
        row = TIERS[2]
    else:
        if iso <= 0:
            raise ValueError("iso must be positive")
        row = next(t for t in TIERS if iso <= t[0])
    p = tuple(round(v * k, 2) for v in row[1:5])
    return Plan(iso=iso, params=p, tested=row[5] and preset == "normal")


def plan_for_sigma(sigma: float, preset: str = "normal", profile: str | None = None) -> Plan:
    """Strength from a measured noise sigma (preferred over ISO: noise varies a lot per clip at equal ISO).

    An unknown or missing profile uses the Log 2 anchors but is flagged untested.
    """
    if preset not in PRESETS:
        raise ValueError(f"preset must be one of {sorted(PRESETS)}")
    if not sigma > 0:
        raise ValueError("sigma must be positive")
    known = profile in ANCHORS
    lo, hi = ANCHORS[profile if known else DEFAULT_PROFILE]
    sp = SPATIAL_LO + (sigma - lo) / (hi - lo) * (SPATIAL_HI - SPATIAL_LO)
    sp = min(max(sp, SPATIAL_MIN), SPATIAL_MAX) * PRESETS[preset]
    p = (round(sp, 2), round(sp, 2), round(sp * 2, 2), round(sp * 2, 2))
    return Plan(iso=None, params=p, tested=known and preset == "normal" and sigma <= hi * 1.15)


STAGES = ("after", "before")


def build_filter(plan: Plan, lut: str | None = None, full_range: bool = True, stage: str = "after") -> str:
    """Filter chain around the Log -> Rec.709 LUT.

    stage="after" (default): [setrange] -> lut3d -> denoise. In equal-noise tests on real clips this kept as much or
    more detail than denoising the Log frames first (see README). stage="before": [setrange] -> denoise -> lut3d.
    Without a LUT the denoise is applied to whatever frames are fed in.
    """
    if stage not in STAGES:
        raise ValueError(f"stage must be one of {STAGES}")
    chain = []
    if full_range:
        chain.append("setrange=full")
    lut_filter = None
    if lut:
        if any(c in lut for c in "'\\:,;[]"):
            raise ValueError("LUT path contains characters unsafe for an ffmpeg filter; rename or move it")
        lut_filter = f"lut3d=file={lut}:interp=tetrahedral"
    if stage == "before":
        chain += [plan.hqdn3d] + ([lut_filter] if lut_filter else [])
    else:
        chain += ([lut_filter] if lut_filter else []) + [plan.hqdn3d]
    return ",".join(chain)


def read_iso(path: str) -> int | None:
    """ISO from exiftool, or None when unavailable (never guesses)."""
    if not shutil.which("exiftool"):
        return None
    r = subprocess.run(["exiftool", "-j", "-n", "-ISO", path], capture_output=True, text=True)
    try:
        v = json.loads(r.stdout)[0].get("ISO")
        return int(v) if v else None
    except (ValueError, IndexError, json.JSONDecodeError):
        return None
