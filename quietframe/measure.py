"""Measure a clip's noise in the Log domain (before any LUT). Needs numpy and ffmpeg/ffprobe.

Estimator: truncated RMS of the Haar diagonal band (HH). Plain MAD saturates on 10-bit data
(it collapses to one code step), so the top 20% of |HH| (edges, texture) is dropped and the
Gaussian truncation bias is corrected (factor 0.6616 at the 80th percentile).
Units: normalised full-range code values (1.0 = 16-bit full scale).
"""
from __future__ import annotations

import json
import subprocess

try:
    import numpy as np
except ImportError:  # numpy is optional; callers fall back to the ISO table
    np = None


def available() -> bool:
    return np is not None


def sigma_frame(g) -> float:
    h, w = (g.shape[0] // 2) * 2, (g.shape[1] // 2) * 2
    g = g[:h, :w]
    d = (g[0::2, 0::2] - g[0::2, 1::2] - g[1::2, 0::2] + g[1::2, 1::2]) / 2.0
    a = np.abs(d).ravel()
    c = np.quantile(a, 0.8)
    return float(np.sqrt(np.mean(a[a <= c] ** 2)) / 0.6616)


def _probe(path: str):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height:format=duration", "-of", "json", path], capture_output=True, text=True)
    j = json.loads(r.stdout)
    s = j["streams"][0]
    return int(s["width"]), int(s["height"]), float(j["format"]["duration"])


def noise_sigma(path: str, samples: int = 5) -> float | None:
    """Median over `samples` full frames spread through the clip. None if nothing could be read.

    Full frames, not a crop: per-region sigma varies by about 25% and per-frame by about 20%,
    so a single centre crop is not a stable estimate.
    """
    if np is None:
        return None
    try:
        W, H, dur = _probe(path)
    except (ValueError, KeyError, IndexError):  # unreadable or missing file
        return None
    W2, H2 = W // 2 * 2, H // 2 * 2
    vals = []
    for i in range(samples):
        t = dur * (i + 1) / (samples + 1)
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", path, "-vf",
                              f"setrange=full,crop={W2}:{H2},format=gray16le",
                              "-frames:v", "1", "-f", "rawvideo", "-"], capture_output=True).stdout
        if len(raw) == W2 * H2 * 2:
            vals.append(sigma_frame(np.frombuffer(raw, "<u2").reshape(H2, W2).astype(np.float64) / 65535))
    return float(np.median(vals)) if vals else None
