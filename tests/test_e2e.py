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

    def test_filter_prints_denoise_before_lut(self):
        r = self.cli("filter", self.src, "--lut", "x.cube", "--mode", "measure")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertLess(r.stdout.index("hqdn3d"), r.stdout.index("lut3d"))

    def test_run_lowers_measured_noise(self):
        out = str(Path(self.dir.name) / "clean.mov")
        r = self.cli("run", self.src, "-o", out, "--preset", "strong")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertLess(measure.noise_sigma(out, samples=2), measure.noise_sigma(self.src, samples=2))

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
