# quietframe

ISO-adaptive denoising for Log camera footage, applied **before** the Log → Rec.709 transform.

Log footage shot at high ISO gets its shadow noise amplified by the display transform. Denoising in the Log
domain, before the LUT, removes more noise for the same loss of detail than denoising afterwards.

## Status

v0.2, classical (ffmpeg `hqdn3d`). Strength comes from the noise measured in the clip (needs numpy); without numpy it falls back to an ISO table.

Measured on a Canon EOS R6 V (Canon Log 3, 4K 10-bit 4:2:2), flat-region noise estimate on one clip per ISO:

| ISO 6400 variant | residual noise | detail kept |
|---|---|---|
| LUT only | 100% | 100% |
| `hqdn3d=3:3:6:6` before LUT | 33% | 93% |
| `hqdn3d` after LUT | 50% | 96% |

### Why measure the clip instead of trusting the ISO

Noise in the Log domain (21 clips, ISO 800 to 51200) rises with ISO but varies a lot per scene:
two ISO 800 clips measured 0.0005 and 0.0011. Typical sigma: about 0.0008 up to ISO 2000, 0.0014 at ISO 3200 to 6400,
0.002 at ISO 51200. Per-frame spread is about 20% and per-region about 25%, so the estimator uses 5 full frames
and takes the median. Treat the estimate as ±30%.

Strength is clamped to a spatial value of 4.0 (checked on 8 further clips: at 4.5 an ISO 51200 clip kept only 92% of detail).

Validated: ISO 6400 at `hqdn3d=3:3:6:6`. At ISO 51200 the automatic setting (about `3.9:3.9:7.8:7.8`) looks cleaner with
no ghosting on a moving chain in one clip, but it is only checked by eye and is flagged `[untested tier]`.
Fast pans and subjects are not validated yet.

## Use

Requires `ffmpeg`. Optional: `numpy` (measure noise), `exiftool` (read ISO for the fallback).

```bash
python -m quietframe filter clip.mp4                 # measures noise, prints the -vf chain
python -m quietframe filter clip.mp4 --mode iso      # ISO table only (no numpy needed)
python -m quietframe filter clip.mp4 --lut my.cube   # denoise, then your LUT
python -m quietframe run clip.mp4 -o clean.mov --iso 6400 --preset strong
```

`--range full` (default) tags the source full range, correct for Canon Log from the R6 V. Use `--range auto` otherwise.

## Roadmap

- v0.2 (done): noise measured per clip, calibrated on one camera. Next: more cameras and scenes.
- v0.3: optional learned denoiser, fine-tuned from a pretrained video model.

Your footage and vendor LUTs are not part of this repo.

## Tests

`python -m unittest discover -s tests`
