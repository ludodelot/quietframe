"""Synthetic camera-like noise for benchmarking: spatially correlated Gaussian, luma sigma + weaker chroma.

Fitted on a Canon EOS R6 V (Canon Log 3, 4K 10-bit 4:2:2): noise is NOT white. The ratio of robust std of
x[i+k]-x[i] for k=2 and k=4 relative to k=1 was about 1.7 and 2.5 at ISO 6400 (white noise gives 1.0 and 1.0).
Chroma sigma is about 0.09 of luma sigma in Log code values.
"""
import numpy as np
from scipy.ndimage import gaussian_filter

CHROMA_RATIO = 0.09


def _rob(d):
    x = np.abs(d).ravel(); c = np.quantile(x, 0.8)
    return float(np.sqrt(np.mean(x[x <= c] ** 2)) / 0.6616)


def lag_ratios(plane):
    d1, d2, d4 = (_rob(plane[:, k:] - plane[:, :-k]) for k in (1, 2, 4))
    return d2 / d1, d4 / d1


def fit_kernel(target=(1.71, 2.45)):
    """Gaussian smoothing sigma (px) whose white-noise output matches the measured lag ratios."""
    rng = np.random.default_rng(1)
    base = rng.normal(size=(512, 512))
    best = min(((k, np.hypot(*(np.array(lag_ratios(gaussian_filter(base, k))) - target))) for k in np.arange(0.4, 3.01, 0.1)),
               key=lambda t: t[1])
    return round(float(best[0]), 1)


def make_noise(shape, sigma_hf, kernel, rng):
    """One plane of noise whose Haar-HH robust sigma (quietframe.measure.sigma_frame) equals sigma_hf."""
    from quietframe.measure import sigma_frame
    n = gaussian_filter(rng.normal(size=shape), kernel)
    return n * (sigma_hf / sigma_frame(n))
