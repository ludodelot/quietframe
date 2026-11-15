# quietframe

ISO-adaptive denoising for Log camera footage, applied **before** the Log → Rec.709 transform.

Log footage shot at high ISO gets its shadow noise amplified by the display transform. Denoising in the Log
domain, before the LUT, removes more noise for the same loss of detail than denoising afterwards.

## Status

v0.1, classical (ffmpeg `hqdn3d`), stdlib-only Python. Strength is chosen from the clip's ISO.

Measured on a Canon EOS R6 V (Canon Log 3, 4K 10-bit 4:2:2), flat-region noise estimate on one clip per ISO:

| ISO 6400 variant | residual noise | detail kept |
|---|---|---|
| LUT only | 100% | 100% |
| `hqdn3d=3:3:6:6` before LUT | 33% | 93% |
| `hqdn3d` after LUT | 50% | 96% |

Only the ISO 800 and ISO 6400 tiers are measured. Other tiers are provisional and flagged `[untested tier]`.
Very high ISO (above 8000) and fast motion are not validated yet.

## Use

Requires `ffmpeg`; `exiftool` is optional (reads ISO automatically).

```bash
python -m quietframe filter clip.mp4                 # prints the -vf chain
python -m quietframe filter clip.mp4 --lut my.cube   # denoise, then your LUT
python -m quietframe run clip.mp4 -o clean.mov --iso 6400 --preset strong
```

`--range full` (default) tags the source full range, correct for Canon Log from the R6 V. Use `--range auto` otherwise.

## Roadmap

- v0.2: calibrated noise-vs-ISO curve per camera, replacing the provisional table.
- v0.3: optional learned denoiser, fine-tuned from a pretrained video model.

Your footage and vendor LUTs are not part of this repo.

## Tests

`python -m unittest discover -s tests`
