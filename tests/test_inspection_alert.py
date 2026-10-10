"""Regole LED su dati SINTETICI: nessuna prova sul pannello o inferenza reale."""
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app" / "python"))
from inspection_alert import InspectionAlert


class InspectionAlertTests(unittest.TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.monitor = InspectionAlert(self.directory.name)
        self.reference = {"reference_id": "reference_synthetic_1", "reference_w": 1.0}
        self.point(1000, 0, 1.0)

    def point(self, stamp, events, power, *, reference=None, power_ok=1):
        self.monitor.telemetry({"events": events, "t_ms": stamp + 10,
                                "power_t_ms": stamp, "power_ok": power_ok,
                                "power_error": 1 if power_ok else 2})
        if power_ok:
            row = ("synthetic_session", "2026-10-10T10:00:00Z", stamp / 1000,
                   stamp, stamp + 10, 10, 1.0, 1.0, 0.0, power * 1000, power)
            self.monitor.observe_row(row, reference or self.reference)

    def test_both_impact_count_and_sustained_loss_are_required(self):
        for stamp in range(2000, 8000, 1000):
            self.point(stamp, 2, 0.5)
        self.assertFalse(self.monitor.status()["active"])
        for stamp in range(8000, 14000, 1000):
            self.point(stamp, 3, 1.0)
        self.assertFalse(self.monitor.status()["active"])
        for stamp in range(14000, 18000, 1000):
            self.point(stamp, 3, 0.5)
        self.assertFalse(self.monitor.status()["active"])
        self.point(18000, 3, 0.5)
        self.assertEqual(self.monitor.status()["alert"]["reason"], "ELECTRICAL_DECLINE")

    def test_gap_error_and_reverse_flow_interrupt_the_streak(self):
        for stamp in range(2000, 6000, 1000):
            self.point(stamp, 3, 0.5)
        self.point(10000, 3, 0.5)  # Pausa lunga: riparte da 1.
        self.assertEqual(self.monitor.status()["consecutive_low_samples"], 1)
        self.point(11000, 3, 0.0, power_ok=0)
        self.assertEqual(self.monitor.status()["consecutive_low_samples"], 0)
        self.point(12000, 3, 0.5)
        self.point(13000, 3, -0.1)
        self.assertEqual(self.monitor.status()["consecutive_low_samples"], 0)
        self.assertFalse(self.monitor.status()["active"])

    def test_exact_threshold_is_included(self):
        for stamp in range(2000, 7000, 1000):
            self.point(stamp, 3, 0.8)  # Esattamente il 20% rispetto a 1 W.
        self.assertTrue(self.monitor.status()["active"])

    def test_latch_survives_recovery_restart_and_requires_reset(self):
        for stamp in range(2000, 7000, 1000):
            self.point(stamp, 3, 0.5)
        self.point(7000, 3, 1.0)
        self.assertEqual(self.monitor.desired_led(), 1)
        reloaded = InspectionAlert(self.directory.name)
        self.assertEqual(reloaded.desired_led(), 1)
        self.assertFalse(reloaded.status()["reference_available"])
        reloaded.reset()
        self.assertEqual(reloaded.desired_led(), 0)
        self.assertEqual(InspectionAlert(self.directory.name).desired_led(), 0)

    def test_mcu_restart_requires_a_new_reference(self):
        self.point(2000, 3, 1.0)
        for stamp in range(100, 7100, 1000):
            self.point(stamp, 3, 0.5)
        self.assertFalse(self.monitor.status()["reference_available"])
        self.assertFalse(self.monitor.status()["active"])
        self.reference = {"reference_id": "reference_synthetic_2", "reference_w": 1.0}
        self.point(8100, 3, 1.0)
        for stamp in range(9100, 14100, 1000):
            self.point(stamp, 6, 0.5)
        self.assertTrue(self.monitor.status()["active"])

    def test_ai_hook_requires_a_comparable_finite_result(self):
        # Valori convenzionali per verificare il confronto, non output di un modello.
        self.monitor.on_ai_result(0.9, 0.5, "synthetic_event", comparable=False)
        self.monitor.on_ai_result(0.4, 0.5, "synthetic_event", comparable=True)
        self.assertEqual(self.monitor.desired_led(), 0)
        with self.assertRaises(ValueError):
            self.monitor.on_ai_result(float("nan"), 0.5, "synthetic_event", comparable=True)
        self.monitor.on_ai_result(0.9, 0.5, "synthetic_event", comparable=True)
        self.assertEqual(self.monitor.status()["alert"]["reason"], "AI_ANOMALY")


if __name__ == "__main__":
    unittest.main()
