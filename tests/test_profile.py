import tempfile
import unittest
from pathlib import Path

from quietframe import profile
from quietframe.core import ANCHORS, plan_for_sigma


def fake_cpf(name: str, start: int = 0x60) -> bytes:
    """Bytes shaped like a Canon .CPF name field: (index, value) pairs with incrementing index."""
    out = bytearray(b"\x00\x01\x02\x03")
    for i, ch in enumerate(name):
        out += bytes([(start + i) % 256, ord(ch)])
    return bytes(out) + b"\x00\x00\x00\x00"


class ProfileTests(unittest.TestCase):
    def test_detects_log2_and_log3_from_sidecar(self):
        with tempfile.TemporaryDirectory() as d:
            for name, key in (("Canon Log 2", "canon-log2"), ("Canon Log 3", "canon-log3")):
                video = Path(d) / f"{key}.MP4"
                video.write_bytes(b"x")
                video.with_suffix(".CPF").write_bytes(fake_cpf(name))
                self.assertEqual(profile.detect(str(video)), key)

    def test_no_sidecar_is_none_not_a_guess(self):
        with tempfile.TemporaryDirectory() as d:
            video = Path(d) / "a.MP4"
            video.write_bytes(b"x")
            self.assertIsNone(profile.detect(str(video)))

    def test_unrelated_sidecar_is_none(self):
        with tempfile.TemporaryDirectory() as d:
            video = Path(d) / "a.MP4"
            video.write_bytes(b"x")
            video.with_suffix(".CPF").write_bytes(b"\x00" * 64)
            self.assertIsNone(profile.detect(str(video)))

    def test_canon_name_mapping(self):
        self.assertEqual(profile.from_canon_name("Canon Log 2"), "canon-log2")
        self.assertEqual(profile.from_canon_name("Canon Log 3"), "canon-log3")
        self.assertIsNone(profile.from_canon_name("BT.709"))
        self.assertIsNone(profile.from_canon_name(None))


class AnchorTests(unittest.TestCase):
    def test_every_profile_reaches_validated_strength_at_its_high_anchor(self):
        for key, (lo, hi) in ANCHORS.items():
            self.assertLess(lo, hi, key)
            self.assertEqual(plan_for_sigma(hi, "normal", key).params[0], 3.0, key)
            self.assertEqual(plan_for_sigma(lo, "normal", key).params[0], 1.5, key)

    def test_unknown_profile_is_flagged_untested(self):
        self.assertFalse(plan_for_sigma(0.001, "normal", None).tested)
        self.assertFalse(plan_for_sigma(0.001, "normal", "mystery-log").tested)
        self.assertTrue(plan_for_sigma(0.001, "normal", "canon-log2").tested)


if __name__ == "__main__":
    unittest.main()
