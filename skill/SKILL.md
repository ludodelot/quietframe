---
name: quietframe
description: Denoise noisy Log footage (e.g. Canon EOS R6 V at high ISO) before the Log to Rec.709 conversion, choosing strength from the clip's ISO. Use when a user says clips look noisy, grainy, or asks to denoise video before grading or exporting to Rec.709.
---

# quietframe

1. Read the clip's ISO (`exiftool -ISO`). Do not guess it.
2. Run `python -m quietframe filter <clip>` to get the ffmpeg chain; add `--lut <file.cube>` so denoise runs before the LUT.
3. Render and compare a 100% crop against the undenoised version before applying to a batch.
4. Report `[untested tier]` warnings to the user; do not claim those settings were validated.
5. Never ship vendor LUTs or the user's footage.
