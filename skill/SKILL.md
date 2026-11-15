---
name: quietframe
description: Denoise noisy Log camera footage (e.g. Canon EOS R6 V in Canon Log 2 or 3) after the Log to Rec.709 LUT, with strength measured from each clip. Use when a user says clips look noisy or grainy, shot at high ISO, or asks to denoise video before grading, stock export or Rec.709 conversion.
---

# quietframe

Noise in Log footage is amplified by the Log to Rec.709 LUT. Denoise **after** the LUT (the default; at equal noise it kept
the same or more detail than denoising Log frames first, on three real clips). Strength comes from the noise measured in
each clip (ISO alone predicts it poorly) and is calibrated per Log profile.

## Steps

1. **Never modify originals.** quietframe only reads the source and writes a new file; it refuses to overwrite its input.
2. **Find the Log profile from the `.CPF` sidecar next to the clip**, never from memory or the trip name: the same camera
   shoots Canon Log 2 on one trip and Canon Log 3 on another. `--log-profile auto` does this; without a sidecar the
   profile is unknown and the tool says so.
3. Get the filter chain: `python -m quietframe filter <clip> [--lut <file.cube>]` (LUT first, then denoise; `--stage before` reverses it).
4. Render a short test and compare a 100% crop against the undenoised version before a batch.
5. Report any `[untested tier]` warning to the user. It means that ISO, noise level or profile was not validated; do not
   present those settings as proven.
6. To calibrate another camera: `python -m quietframe calibrate @clips.txt -o noise.csv`. Never publish the `path` column.

Requires `ffmpeg`; `numpy` enables measurement (otherwise an ISO table is used); `exiftool` reads ISO.
Never ship footage or camera-maker LUTs in a repo.
