"""Test software con campioni sintetici: nessun risultato sperimentale hardware."""
import contextlib
import csv
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app" / "python"))
from event_logger import EventLogger


class EventLoggerTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.calls = []
        self.saved = []
        self.errors = []
        self.now = 100.0
        self.output = io.StringIO()
        self.redirect = contextlib.redirect_stdout(self.output)
        self.redirect.__enter__()
        self.addCleanup(self.redirect.__exit__, None, None, None)
        self.logger = EventLogger(
            self.directory.name, "20261017_120000_abcd1234",
            lambda event_id: self.bridge_call("solarecho_ack", event_id),
            on_saved=self.saved.append, on_error=self.errors.append,
            clock=lambda: self.now,
        )

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
        self.logger.process()
        json_path = next(self.logger.output_dir.glob(f"*_event_{event_id:04d}.json"))
        return json.loads(json_path.read_text(encoding="utf-8"))

    def test_two_events_saved_with_signed_timestamps_and_ack(self):
        for event_id in (1, 2):
            metadata = self.feed_event(event_id)
            self.assertTrue(metadata["capture_complete"])
            self.assertEqual(metadata["mean_sample_rate_hz"], 100.0)
            path = next(self.logger.output_dir.glob(f"*_event_{event_id:04d}.csv"))
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
        self.logger.process()
        self.assertEqual(len(list(self.logger.output_dir.glob("*.csv"))), 1)
        self.assertEqual(self.calls, [("solarecho_ack", 1)])

    def test_timeout_saves_partial_diagnostic(self):
        self.logger.on_begin(1, 220, 20, 200_000, 2_000_000, 6000, 1)
        self.logger.process()
        self.now += 11
        self.logger.process()
        path = next(self.logger.output_dir.glob("*.json"))
        metadata = json.loads(path.read_text(encoding="utf-8"))
        self.assertTrue(metadata["timed_out"])
        self.assertFalse(metadata["capture_complete"])
        self.assertEqual(metadata["received_samples"], 0)

    def test_write_failure_never_acknowledges(self):
        self.logger.on_begin(1, 0, 0, 200_000, 2_000_000, 6000, 1)
        self.logger.on_end(1, 0, False, 0)
        with patch.object(self.logger, "save_capture", side_effect=OSError("disk full")):
            self.logger.process()
        self.assertTrue(self.logger.halted)
        self.assertEqual(self.calls, [])
        self.assertEqual(self.saved, [])
        self.assertTrue(self.errors)

    def test_ack_runs_only_after_csv_json_and_saved_callback(self):
        def acknowledge(event_id):
            self.assertEqual(event_id, 1)
            self.assertEqual(len(self.saved), 1)
            path = self.saved[0]
            self.assertTrue(path.is_file())
            metadata = json.loads(path.with_suffix(".json").read_text(encoding="utf-8"))
            self.assertTrue(metadata["capture_complete"])
            self.calls.append(("solarecho_ack", event_id))
            return 1

        self.logger.acknowledge = acknowledge
        self.feed_event(1)
        self.assertEqual(self.calls, [("solarecho_ack", 1)])
        self.assertFalse(self.logger.halted)

    def test_ack_failure_halts_and_keeps_saved_capture(self):
        self.logger.acknowledge = lambda event_id: 0
        self.feed_event(1)
        self.assertTrue(self.logger.halted)
        self.assertTrue(self.errors)
        self.assertTrue(self.saved[0].is_file())
        self.assertTrue(self.saved[0].with_suffix(".json").is_file())


if __name__ == "__main__":
    unittest.main()
