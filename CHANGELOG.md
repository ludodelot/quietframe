# Changelog

## Unreleased (towards 1.0.0)
- Calibration anchors are now per Log profile (`canon-log2`, `canon-log3`); the profile is read from the `.CPF` next to the clip (`--log-profile auto`) and never guessed. Unknown profile => flagged `[untested tier]`.
- `calibrate` writes a `profile` column.
- `run` refuses to overwrite its input or an existing output (`--force`).
- Tests: profile detection, anchors, synthetic end-to-end (no personal footage).

## 0.2.0
- Strength from noise measured in the clip (truncated-RMS of the Haar diagonal band), ISO table as fallback.
- `calibrate` command. Spatial strength capped at 4.0.

## 0.1.0
- ISO-adaptive `hqdn3d` before the LUT.
