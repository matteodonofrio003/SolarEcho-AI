"""Solo segnali sintetici: verifiche del formato, non prestazioni hardware/AI."""
import contextlib
import csv
import importlib.util
import io
import json
import math
from pathlib import Path
import tempfile
from unittest.mock import patch
import unittest


MODULE_PATH = Path(__file__).resolve().parents[1] / "tools/export_edge_impulse.py"
SPEC = importlib.util.spec_from_file_location("edge_impulse_export", MODULE_PATH)
exporter = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(exporter)
from vibration_ai import prepare_capture


class EdgeImpulseExportTest(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.source = self.root / "raw"
        self.source.mkdir()
        self.output = self.root / "export"

    def capture(self, name="event", step_us=9600, **changes):
        # Circa 104 Hz, assi lineari nel tempo e offset noto.
        times = list(range(-200_000, 2_000_000, step_us))
        path = self.source / f"{name}.csv"
        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(("session_id", "event_id", "sample_index", "timestamp_us",
                             "ax_g", "ay_g", "az_g", "trigger_source", "capture_complete"))
            for index, stamp in enumerate(times):
                writer.writerow(("synthetic_session", 1, index, stamp, stamp / 1e6,
                                 2 * stamp / 1e6, 1.0, "piezo_analog", True))
        metadata = dict(session_id="synthetic_session", event_id=1, capture_complete=True,
                        transport_complete=True, overflow=False, timed_out=False,
                        additional_events=0, received_samples=len(times),
                        expected_samples=len(times), declared_samples=len(times),
                        pretrigger_us=200_000, posttrigger_us=2_000_000,
                        pretrigger_samples=sum(stamp < 0 for stamp in times))
        metadata.update(changes)
        path.with_suffix(".json").write_text(json.dumps(metadata), encoding="utf-8")
        return path

    def export(self, **kwargs):
        with contextlib.redirect_stdout(io.StringIO()):
            return exporter.export_batch(self.source, self.output, "normal", "training", **kwargs)

    def test_interpolation_uniform_time_label_and_preserved_originals(self):
        path = self.capture()
        original_csv = path.read_bytes()
        original_json = path.with_suffix(".json").read_bytes()
        report = self.export()
        self.assertEqual(report["exported"], 1)
        self.assertEqual(report["units"], "g")
        self.assertEqual(report["trigger_at_export_ms"], 150)
        exported = self.output / report["events"][0]["output_csv"]
        self.assertTrue(exported.name.startswith("normal."))
        with exported.open(newline="", encoding="utf-8") as stream:
            reader = csv.DictReader(stream)
            self.assertEqual(reader.fieldnames, ["timestamp", "accX", "accY", "accZ"])
            rows = list(reader)
        self.assertEqual(len(rows), 200)
        self.assertEqual([float(row["timestamp"]) for row in rows], list(range(0, 2000, 10)))
        for index, row in enumerate(rows):
            relative_s = -0.15 + index / 100
            self.assertAlmostEqual(float(row["accX"]), relative_s)
            self.assertAlmostEqual(float(row["accY"]), 2 * relative_s)
            self.assertEqual(float(row["accZ"]), 1.0)  # Nessuna rimozione implicita di gravita.
        self.assertEqual(path.read_bytes(), original_csv)
        self.assertEqual(path.with_suffix(".json").read_bytes(), original_json)

    def test_default_export_matches_model_input_exactly(self):
        path = self.capture(step_us=9611)
        # Assi non lineari e valori con molte cifre: verifica anche precisione e ordine XYZ.
        with path.open(newline="", encoding="utf-8") as stream:
            reader = csv.DictReader(stream)
            fields, rows = reader.fieldnames, list(reader)
        for row in rows:
            second = int(row["timestamp_us"]) / 1e6
            for axis, frequency in zip(("ax_g", "ay_g", "az_g"), (7.3, 13.1, 19.7)):
                row[axis] = repr(math.sin(second * frequency) + 0.123456789123)
        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        original_csv = path.read_bytes()
        original_json = path.with_suffix(".json").read_bytes()
        report = self.export()
        exported = self.output / report["events"][0]["output_csv"]
        with exported.open(newline="", encoding="utf-8") as stream:
            edge_rows = list(csv.DictReader(stream))
        model_rows, _ = prepare_capture(path)  # Preprocessing soltanto: non avvia il runner.
        self.assertEqual(len(model_rows), 200)
        self.assertEqual(report["window_duration_ms"], 2000)
        self.assertEqual(report["end_relative_trigger_ms_exclusive"], 1850)
        self.assertEqual([row[0] for row in model_rows], list(range(-150, 1850, 10)))
        edge_features = [float(row[axis]) for row in edge_rows for axis in ("accX", "accY", "accZ")]
        model_features = [value for row in model_rows for value in row[1:]]
        self.assertEqual(len(model_features), 600)
        self.assertEqual(model_features, edge_features)
        self.assertEqual([float(row["timestamp"]) - 150 for row in edge_rows],
                         [row[0] for row in model_rows])
        self.assertEqual(path.read_bytes(), original_csv)
        self.assertEqual(path.with_suffix(".json").read_bytes(), original_json)

    def test_cli_defaults_match_current_model(self):
        argv = [str(MODULE_PATH), "--input", "unused_raw", "--output", "unused_export",
                "--label", "normal", "--split", "training"]
        with patch.object(exporter.sys, "argv", argv):
            with patch.object(exporter, "export_batch", return_value={"excluded": 0}) as export:
                self.assertEqual(exporter.main(), 0)
        self.assertEqual(export.call_args.args[5:8], (100, -150, 1850))

    def test_historical_window_requires_explicit_override(self):
        path = self.capture()
        report = self.export(end_ms=1950)
        self.assertEqual(report["events"][0]["exported_samples"], 210)
        self.assertEqual(report["end_relative_trigger_ms_exclusive"], 1950)
        model_rows, _ = prepare_capture(path)
        self.assertEqual(len(model_rows), 200)

    def test_incomplete_and_multiple_impacts_excluded(self):
        self.capture("incomplete", capture_complete=False)
        self.capture("extra_impact", additional_events=1)
        report = self.export()
        self.assertEqual(report["excluded"], 2)
        self.assertEqual(report["exported"], 0)
        self.assertFalse(list((self.output / "training").glob("*.csv")))
        self.assertTrue((self.output / "export_report.json").is_file())
        for path in self.source.glob("*.csv"):
            with self.assertRaises(ValueError):
                prepare_capture(path)

    def test_missing_json_is_not_silently_accepted(self):
        path = self.capture()
        path.with_suffix(".json").unlink()
        self.assertEqual(self.export()["excluded"], 1)

    def test_corrupt_csv_is_rejected_even_when_metadata_says_complete(self):
        path = self.capture()
        original = path.read_text(encoding="utf-8")
        for replacement in ("nan", "inf", ""):
            with self.subTest(value=replacement):
                lines = original.splitlines()
                fields = lines[5].split(",")
                fields[4] = replacement
                lines[5] = ",".join(fields)
                path.write_text("\n".join(lines) + "\n", encoding="utf-8")
                with self.assertRaises(ValueError):
                    exporter.read_capture(path)
        lines = original.splitlines()
        fields = lines[5].split(",")
        fields[3] = "-200000"  # Tempo duplicato/non crescente.
        lines[5] = ",".join(fields)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            exporter.read_capture(path)

    def test_no_upsampling_or_extrapolation(self):
        path = self.capture()
        times, values, _, _ = exporter.read_capture(path)
        with self.assertRaises(ValueError):
            exporter.resample(times, values, rate_hz=200)
        with self.assertRaises(ValueError):
            exporter.resample(times, values, start_ms=-210)
        with self.assertRaises(ValueError):
            exporter.resample(times, values, end_ms=2020)

    def test_duplicate_event_and_output_overwrite_prevented(self):
        self.capture("copy_a")
        self.capture("copy_b")
        report = self.export()
        self.assertEqual(report["exported"], 1)
        self.assertEqual(report["excluded"], 1)
        with self.assertRaises(ValueError):
            self.export()

    def test_modified_cannot_enter_anomaly_training(self):
        self.capture()
        with self.assertRaises(ValueError):
            exporter.export_batch(self.source, self.output, "modified", "training")
        self.assertFalse(self.output.exists())

    def test_restored_is_normal_but_condition_is_retained(self):
        self.capture()
        with contextlib.redirect_stdout(io.StringIO()):
            report = exporter.export_batch(self.source, self.output, "normal", "test", "restored")
        self.assertEqual(report["condition"], "restored")
        self.assertEqual(report["label"], "normal")
        self.assertEqual(report["exported"], 1)
        with self.assertRaises(ValueError):
            exporter.export_batch(self.source, self.root / "other", "normal", "calibration", "restored")


if __name__ == "__main__":
    unittest.main()
