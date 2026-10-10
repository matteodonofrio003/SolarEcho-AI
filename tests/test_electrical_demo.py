"""Test matematici con segnali SINTETICI, non prove fisiche sul pannello."""
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app" / "python"))
from electrical_demo import ElectricalDemo, DEFAULT_SETTINGS


class ElectricalDemoTests(unittest.TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        clock_patch = patch("electrical_demo.time.monotonic", return_value=100.0)
        self.clock = clock_patch.start()
        self.addCleanup(clock_patch.stop)
        history = SimpleNamespace(started_at=0.0, session_id="20261010_120000_abcd1234",
                                  path=Path("power_synthetic.csv"))
        self.demo = ElectricalDemo(self.directory.name, history)

    def point(self, second, power_w):
        self.clock.return_value = float(second)
        row = ("synthetic", "2026-10-10T12:00:00+00:00", float(second), int(second * 1000),
               int(second * 1000), 0, 4.0, 4.0, 0.0, power_w / 4 * 1000, power_w)
        self.demo.observe_row(row)

    def reference(self):
        self.demo.start_reference()
        for second in range(101, 111):
            self.point(second, 2.0)
        self.assertEqual(self.demo.status()["phase"], "REFERENCE_READY")
        self.clock.return_value = 111.0
        self.demo.start_comparison()

    def test_known_energy_deficit_and_household_scenario(self):
        self.reference()
        self.point(112, 1.0)
        self.point(113, 1.0)
        result = self.demo.status()
        trial = result["comparison"]
        self.assertAlmostEqual(trial["measured_wh"], 1 / 3600)
        self.assertAlmostEqual(trial["reference_wh"], 2 / 3600)
        self.assertAlmostEqual(trial["period_reduction_pct"], 50.0)
        self.assertAlmostEqual(result["scenario"]["lost_kwh"], 180.0)
        self.assertAlmostEqual(result["scenario"]["total_eur"], 34.2)

    def test_gap_and_reverse_flow_do_not_invent_energy(self):
        self.reference()
        for second, power in [(112, 1), (113, 1), (117, 1), (118, -1), (119, 1), (120, 1)]:
            self.point(second, power)
        trial = self.demo.status()["comparison"]
        self.assertAlmostEqual(trial["covered_s"], 2.0)
        self.assertAlmostEqual(trial["measured_wh"], 2 / 3600)
        self.assertEqual(trial["reverse_power_samples"], 1)

    def test_manual_scenario_can_run_without_claiming_measurement(self):
        settings = dict(DEFAULT_SETTINGS, reduction_mode="manual", daily_kwh=10,
                        days=10, self_consumption_pct=100, buy_eur_kwh=0.30,
                        assumed_reduction_pct=20)
        result = self.demo.update_settings(settings)
        self.assertEqual(result["phase"], "NO_REFERENCE")
        self.assertTrue(result["scenario"]["hypothetical"])
        self.assertAlmostEqual(result["scenario"]["total_eur"], 6.0)
        reloaded = ElectricalDemo(self.directory.name, self.demo.history)
        self.assertEqual(reloaded.settings["daily_kwh"], 10)
        self.assertIsNone(reloaded.baseline)

    def test_increase_does_not_become_a_negative_loss(self):
        self.reference()
        self.point(112, 3)
        self.point(113, 3)
        result = self.demo.status()
        self.assertLess(result["comparison"]["period_reduction_pct"], 0)
        self.assertEqual(result["comparison"]["net_deficit_wh"], 0)
        self.assertEqual(result["scenario"]["total_eur"], 0)
        self.demo.finish_comparison()
        self.assertFalse(self.demo.report()["comparison"]["running"])
        self.assertTrue(list(Path(self.directory.name).glob("demo_*.json")))

    def test_nonfinite_and_out_of_range_parameters_are_rejected(self):
        for key, value in [("buy_eur_kwh", float("nan")), ("self_consumption_pct", 101), ("days", 1.5)]:
            with self.subTest(key=key):
                with self.assertRaises(ValueError):
                    self.demo.update_settings(dict(DEFAULT_SETTINGS, **{key: value}))


if __name__ == "__main__":
    unittest.main()
