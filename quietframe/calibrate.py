"""Batch noise survey: measure many clips and write a CSV (path, model, iso, sigma, seconds). Read-only on the inputs.

Use it to calibrate quietframe for your own camera: run it on a spread of clips (different ISO, scenes, dates),
then compare sigma against ISO. Needs numpy, ffmpeg, and exiftool (for model/ISO).
"""
from __future__ import annotations

import csv
import json
import shutil
import subprocess
import time
from concurrent.futures import ProcessPoolExecutor

from . import measure


def _meta(path: str):
    if not shutil.which("exiftool"):
        return None, None
    r = subprocess.run(["exiftool", "-j", "-n", "-Model", "-ISO", path], capture_output=True, text=True)
    try:
        d = json.loads(r.stdout)[0]
        return d.get("Model"), d.get("ISO")
    except (ValueError, IndexError):
        return None, None


def survey_one(path: str) -> dict:
    t = time.time()
    model, iso = _meta(path)
    try:
        sigma = measure.noise_sigma(path)
    except Exception as error:  # one bad file must not stop a long survey
        sigma = None
        model = f"{model} (error: {type(error).__name__})"
    return {"path": path, "model": model, "iso": iso, "sigma": sigma, "seconds": round(time.time() - t, 1)}


def survey(paths: list[str], out_csv: str, jobs: int = 4, progress=print) -> int:
    done = 0
    with open(out_csv, "w", newline="") as f, ProcessPoolExecutor(max_workers=jobs) as pool:
        w = csv.DictWriter(f, fieldnames=["path", "model", "iso", "sigma", "seconds"])
        w.writeheader()
        for row in pool.map(survey_one, paths):
            w.writerow(row)
            f.flush()
            done += 1
            if done % 10 == 0:
                progress(f"{done}/{len(paths)}")
    return done
