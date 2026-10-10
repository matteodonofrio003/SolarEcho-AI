"""Test software con campioni sintetici: nessun risultato sperimentale hardware."""
import contextlib
import csv
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch


class EventLoggerTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.calls = []
        utils = types.ModuleType("arduino.app_utils")
        utils.App = types.SimpleNamespace(run=lambda **kwargs: None)
        utils.Bridge = types.SimpleNamespace(provide=lambda *args: None, call=self.bridge_call)
        self.output = io.StringIO()
        self.redirect = contextlib.redirect_stdout(self.output)
        self.redirect.__enter__()
        self.addCleanup(self.redirect.__exit__, None, None, None)
        with patch.dict(sys.modules, {"arduino": types.ModuleType("arduino"), "arduino.app_utils": utils}):
            path = Path(__file__).resolve().parents[1] / "app/python/main.py"
            spec = importlib.util.spec_from_file_location("event_logger_under_test", path)
            self.logger = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(self.logger)
        self.logger.OUTPUT_DIR = Path(self.directory.name)
        self.logger.armed = True

    def bridge_call(self, name, *args):
        self.calls.append((name, *args))
        return 1

    def feed_event(self, event_id, additional_events=0, missing_index=None, gap=False):
        # 100 Hz sintetici, -200 ms .. +1990 ms. Non rappresentano la firma del pannello.
        stamps = list(range(-200_000, 2_000_000, 10_000))
        self.logger.on_begin(event_id, len(stamps), 20, 200_000, 2_000_000, 6000, event_id)
        for index, stamp in enumerate(stamps):
            if index == missing_index:
                continue
            if gap and index == 80:
                stamp += 40_000
            self.logger.on_sample(event_id, index, stamp, 0.0, 0.0, 1.0,
                                  0, event_id, event_id, 25, 25, stamp - 200, 1000)
        self.logger.on_end(event_id, len(stamps), False, additional_events)
        with patch.object(self.logger.time, "sleep"):
            self.logger.loop()
        json_path = next(self.logger.OUTPUT_DIR.glob(f"*_event_{event_id:04d}.json"))
        return json.loads(json_path.read_text(encoding="utf-8"))

    def test_two_events_saved_with_signed_timestamps_and_ack(self):
        for event_id in (1, 2):
            metadata = self.feed_event(event_id)
            self.assertTrue(metadata["capture_complete"])
            self.assertEqual(metadata["mean_sample_rate_hz"], 100.0)
            path = next(self.logger.OUTPUT_DIR.glob(f"*_event_{event_id:04d}.csv"))
            with path.open(newline="", encoding="utf-8") as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(len(rows), 220)
            self.assertEqual(rows[0]["timestamp_us"], "-200000")
            self.assertEqual(rows[-1]["timestamp_us"], "1990000")
            self.assertEqual(rows[0]["event_id"], str(event_id))
            self.assertEqual(rows[0]["trigger_source"], "piezo_analog")
            self.assertEqual(rows[0]["capture_complete"], "True")
            self.assertFalse(any(None in row for row in rows))
        self.assertEqual(self.calls, [("solarecho_ack", 1), ("solarecho_ack", 2)])
        self.assertIsNone(self.logger.pending)

    def test_extra_impacts_excluded_from_baseline(self):
        metadata = self.feed_event(1, additional_events=1)
        self.assertTrue(metadata["transport_complete"])
        self.assertFalse(metadata["capture_complete"])
        self.assertIn("altri eventi piezo nella stessa finestra", metadata["unusable_reasons"])

    def test_missing_sample_excluded(self):
        metadata = self.feed_event(1, missing_index=30)
        self.assertFalse(metadata["transport_complete"])
        self.assertFalse(metadata["capture_complete"])

    def test_bad_timestamps_excluded(self):
        metadata = self.feed_event(1, gap=True)
        self.assertFalse(metadata["capture_complete"])
        self.assertIn("interruzione nel campionamento IMU", metadata["unusable_reasons"])

    def test_duplicate_end_does_not_overwrite(self):
        self.feed_event(1)
        self.logger.on_end(1, 220, False, 0)
        with patch.object(self.logger.time, "sleep"):
            self.logger.loop()
        self.assertEqual(len(list(self.logger.OUTPUT_DIR.glob("*.csv"))), 1)
        self.assertEqual(self.calls, [("solarecho_ack", 1)])

    def test_timeout_saves_partial_diagnostic(self):
        self.logger.on_begin(1, 220, 20, 200_000, 2_000_000, 6000, 1)
        with patch.object(self.logger.time, "sleep"):
            self.logger.loop()
            self.logger.pending["received_at"] -= 11
            self.logger.loop()
        path = next(self.logger.OUTPUT_DIR.glob("*.json"))
        metadata = json.loads(path.read_text(encoding="utf-8"))
        self.assertTrue(metadata["timed_out"])
        self.assertFalse(metadata["capture_complete"])
        self.assertEqual(metadata["received_samples"], 0)

    def test_write_failure_never_acknowledges(self):
        self.logger.on_begin(1, 0, 0, 200_000, 2_000_000, 6000, 1)
        self.logger.on_end(1, 0, False, 0)
        with patch.object(self.logger, "save_capture", side_effect=OSError("disk full")):
            with patch.object(self.logger.time, "sleep"):
                self.logger.loop()
        self.assertTrue(self.logger.halted)
        self.assertEqual(self.calls, [])


if __name__ == "__main__":
    unittest.main()
