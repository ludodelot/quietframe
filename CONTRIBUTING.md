# Contributing

The most useful contribution is **calibration data for another camera or Log profile**.

1. Pick 50+ clips that span your ISO range, scenes and dates (read-only; originals are never modified):
   `python -m quietframe calibrate clip1.mp4 clip2.mp4 -o noise.csv` or `calibrate @list.txt -o noise.csv`
2. Strip the `path` column (it contains folder and place names) and open an issue with the rest:
   camera model, Log profile, ISO and sigma per clip.
3. Do not attach footage, LUTs from camera makers, or anything you do not have the right to share.

Code changes: keep it stdlib-only except for the optional numpy measurement, add a test, and run
`python -m unittest discover -s tests` with and without numpy.
