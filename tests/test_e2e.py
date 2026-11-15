"""End-to-end on a synthetic noisy clip: no personal footage needed. Skipped without ffmpeg or numpy."""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from quietframe import measure

ROOT = Path(__file__).resolve().parents[1]
READY = shutil.which("ffmpeg") and measure.available()


@unittest.skipUnless(READY, "needs ffmpeg and numpy")
class EndToEnd(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir = tempfile.TemporaryDirectory()
        cls.src = str(Path(cls.dir.name) / "noisy.mkv")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc2=size=640x360:rate=24:duration=2",
                        "-vf", "noise=alls=25:allf=t+u,format=yuv422p10le", "-c:v", "ffv1", cls.src], check=True)

    @classmethod
    def tearDownClass(cls):
        cls.dir.cleanup()

    def cli(self, *args):
        return subprocess.run([sys.executable, "-m", "quietframe", *args], cwd=ROOT, capture_output=True, text=True)

    def test_filter_defaults_to_denoise_after_lut_and_can_be_flipped(self):
        r = self.cli("filter", self.src, "--lut", "x.cube", "--mode", "measure")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertLess(r.stdout.index("lut3d"), r.stdout.index("hqdn3d"))
        r = self.cli("filter", self.src, "--lut", "x.cube", "--mode", "measure", "--stage", "before")
        self.assertLess(r.stdout.index("hqdn3d"), r.stdout.index("lut3d"))

    def test_run_lowers_measured_noise(self):
        out = str(Path(self.dir.name) / "clean.mov")
        r = self.cli("run", self.src, "-o", out, "--preset", "strong")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertLess(measure.noise_sigma(out, samples=2), measure.noise_sigma(self.src, samples=2))

    def test_rotated_phone_style_clip_is_still_measured(self):
        rotated = str(Path(self.dir.name) / "rotated.mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", self.src, "-c:v", "libx264", "-crf", "12", "-pix_fmt", "yuv420p",
                        "-metadata:s:v", "rotate=90", rotated], check=True)
        self.assertIsNotNone(measure.noise_sigma(rotated, samples=2))

    def test_plain_video_keeps_its_range_flags_but_known_log_forces_full(self):
        r = self.cli("filter", self.src, "--mode", "iso", "--iso", "800")
        self.assertNotIn("setrange", r.stdout)           # unknown profile: flags left alone
        r = self.cli("filter", self.src, "--mode", "iso", "--iso", "800", "--log-profile", "canon-log2")
        self.assertTrue(r.stdout.startswith("setrange=full"))
        r = self.cli("filter", self.src, "--mode", "iso", "--iso", "800", "--range", "full")
        self.assertTrue(r.stdout.startswith("setrange=full"))

    def test_flat_clip_without_noise_does_not_crash(self):
        flat = str(Path(self.dir.name) / "flat.mkv")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=gray:size=320x180:rate=24:duration=1",
                        "-vf", "format=yuv422p10le", "-c:v", "ffv1", flat], check=True)
        self.assertIsNone(measure.noise_sigma(flat, samples=2))
        r = self.cli("filter", flat)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("hqdn3d", r.stdout)

    def test_never_overwrites_input_or_existing_output(self):
        r = self.cli("run", self.src, "-o", self.src)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("originals are never modified", r.stderr)
        existing = Path(self.dir.name) / "exists.mov"
        existing.write_bytes(b"keep")
        r = self.cli("run", self.src, "-o", str(existing))
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(existing.read_bytes(), b"keep")


if __name__ == "__main__":
    unittest.main()
