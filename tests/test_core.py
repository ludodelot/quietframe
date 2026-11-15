import unittest

from quietframe.core import ANCHORS, build_filter, plan_for_iso, plan_for_sigma
from quietframe import measure


class CoreTests(unittest.TestCase):
    def test_iso6400_matches_measured_setting(self):
        self.assertEqual(plan_for_iso(6400).hqdn3d, "hqdn3d=3:3:6:6")
        self.assertTrue(plan_for_iso(6400).tested)

    def test_low_iso_is_gentler(self):
        self.assertLess(plan_for_iso(800).params[0], plan_for_iso(6400).params[0])

    def test_unknown_iso_falls_back_to_mid(self):
        self.assertEqual(plan_for_iso(None).hqdn3d, "hqdn3d=3:3:6:6")

    def test_presets_scale_and_mark_untested(self):
        self.assertGreater(plan_for_iso(6400, "strong").params[0], 3)
        self.assertFalse(plan_for_iso(6400, "strong").tested)

    def test_bad_inputs(self):
        with self.assertRaises(ValueError):
            plan_for_iso(0)
        with self.assertRaises(ValueError):
            plan_for_iso(800, "nuclear")

    def test_default_stage_denoises_after_the_lut(self):
        vf = build_filter(plan_for_iso(3200), lut="a.cube")
        self.assertLess(vf.index("lut3d"), vf.index("hqdn3d"))
        self.assertTrue(vf.startswith("setrange=full"))

    def test_before_stage_denoises_before_the_lut(self):
        vf = build_filter(plan_for_iso(3200), lut="a.cube", stage="before")
        self.assertLess(vf.index("hqdn3d"), vf.index("lut3d"))

    def test_bad_stage_rejected(self):
        with self.assertRaises(ValueError):
            build_filter(plan_for_iso(3200), stage="sideways")

    def test_unsafe_lut_path_rejected(self):
        with self.assertRaises(ValueError):
            build_filter(plan_for_iso(800), lut="a,b.cube")


class SigmaTests(unittest.TestCase):
    def test_anchors(self):
        lo, hi = ANCHORS["canon-log2"]
        self.assertEqual(plan_for_sigma(hi, "normal", "canon-log2").params[0], 3.0)
        self.assertEqual(plan_for_sigma(lo, "normal", "canon-log2").params[0], 1.5)

    def test_monotonic_and_clamped(self):
        a, b = plan_for_sigma(0.001, "normal", "canon-log2").params[0], plan_for_sigma(0.0015, "normal", "canon-log2").params[0]
        self.assertLess(a, b)
        self.assertEqual(plan_for_sigma(1.0).params[0], 4.0)
        self.assertEqual(plan_for_sigma(1e-9).params[0], 1.0)

    def test_high_sigma_marked_untested(self):
        self.assertFalse(plan_for_sigma(0.003).tested)

    @unittest.skipUnless(measure.available(), "numpy not installed")
    def test_unreadable_file_returns_none(self):
        self.assertIsNone(measure.noise_sigma("/nonexistent/x.mp4"))

    @unittest.skipUnless(measure.available(), "numpy not installed")
    def test_estimator_recovers_gaussian_sigma(self):
        import numpy as np
        rng = np.random.default_rng(0)
        g = rng.normal(0.5, 0.002, (512, 512))
        self.assertAlmostEqual(measure.sigma_frame(g), 0.002, delta=0.0002)


if __name__ == "__main__":
    unittest.main()
