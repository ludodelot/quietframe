# Changelog

## 1.0.0
- **Default stage changed to after the LUT** (`--stage after`; `--stage before` keeps the old order). With the correct LUT for each Log curve, at equal residual noise denoising after the LUT kept the same or more detail on all three test clips (Canon Log 2 ISO 6400 and 51200, Canon Log 3 ISO 8299). Earlier "before the LUT" claims came from a test that used a Log 3 LUT on Log 2 footage and are withdrawn.
- Anchors calibrated per Log profile on 356 Canon EOS R6 V clips (Log 2: 160, Log 3: 196); `assets/calibration_summary.json` has the aggregates.
- Calibration anchors are now per Log profile (`canon-log2`, `canon-log3`); the profile is read from the `.CPF` next to the clip (`--log-profile auto`) and never guessed. Unknown profile => flagged `[untested tier]`.
- `calibrate` writes a `profile` column.
- `run` refuses to overwrite its input or an existing output (`--force`).
- Tests: profile detection, anchors, synthetic end-to-end (no personal footage).

## 0.2.0
- Strength from noise measured in the clip (truncated-RMS of the Haar diagonal band), ISO table as fallback.
- `calibrate` command. Spatial strength capped at 4.0.

## 0.1.0
- ISO-adaptive `hqdn3d` before the LUT.
