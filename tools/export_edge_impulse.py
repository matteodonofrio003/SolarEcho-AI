"""Export locale SolarEcho -> Edge Impulse. Solo libreria standard Python.

Non carica dati online, non modifica i grezzi e non assegna classi dal segnale.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys


# Il deploy copia lo stesso modulo in python/ sulla UNO Q.
APP_PYTHON = Path(__file__).resolve().parents[1] / "app" / "python"
if str(APP_PYTHON) not in sys.path:
    sys.path.insert(0, str(APP_PYTHON))
from signal_processing import END_MS, MAX_GAP_US, RATE_HZ, START_MS, read_capture, resample


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def export_batch(source, output, label, split, condition=None, rate_hz=RATE_HZ,
                 start_ms=START_MS, end_ms=END_MS, notes=""):
    """Una cartella di input = una condizione e un gruppo scelti dall'operatore."""
    source, output = Path(source).resolve(), Path(output).resolve()
    condition = condition or label
    if label not in ("normal", "modified") or split not in ("training", "calibration", "test"):
        raise ValueError("etichetta o gruppo non supportato")
    if condition not in ("normal", "modified", "restored"):
        raise ValueError("condizione non supportata")
    if label != ("modified" if condition == "modified" else "normal"):
        raise ValueError("normal/restored richiedono label normal; modified richiede label modified")
    if split != "test" and condition != "normal":
        raise ValueError("per anomaly detection modified/restored restano nel test")
    if rate_hz <= 0 or end_ms <= start_ms:
        raise ValueError("frequenza/durata non valida")
    count, remainder = divmod((end_ms - start_ms) * rate_hz, 1000)
    if remainder or count < 2:
        raise ValueError("durata * frequenza deve dare un numero intero di campioni >= 2")
    if output == source or source in output.parents:
        raise ValueError("l'output deve essere fuori dalla cartella dei grezzi")
    if not source.is_dir():
        raise ValueError(f"cartella di input inesistente: {source}")
    paths = sorted(source.glob("*.csv"))  # Non ricorsivo: evita di mescolare condizioni.
    if not paths:
        raise ValueError("nessun CSV nella cartella di input")
    if output.exists():
        raise ValueError("cartella output gia esistente: sceglierne una nuova, senza sovrascrivere")
    output.mkdir(parents=True)
    upload_dir = output / split
    upload_dir.mkdir()
    records, identities = [], set()
    for path in paths:
        record = dict(source_csv=str(path), label=label, condition=condition,
                      split=split, status="excluded")
        try:
            times, acceleration, metadata, stats = read_capture(path)
            identity = (metadata["session_id"], metadata["event_id"])
            if identity in identities:
                raise ValueError("sessione/evento duplicato in questo lotto")
            samples = resample(times, acceleration, rate_hz, start_ms, end_ms)
            source_hash = sha256(path)
            metadata_hash = sha256(path.with_suffix(".json"))
        except (OSError, UnicodeError, ValueError, TypeError, KeyError, csv.Error) as error:
            record["reason"] = str(error)
            print(f"ESCLUSO {path.name}: {error}")
        else:
            # Hash stabile del grezzo: aiuta a riconoscere copie dello stesso evento.
            destination = upload_dir / f"{label}.{source_hash}.csv"
            with destination.open("x", newline="", encoding="utf-8") as stream:
                writer = csv.writer(stream)
                writer.writerow(("timestamp", "accX", "accY", "accZ"))
                for stamp, x, y, z in samples:
                    writer.writerow((f"{stamp:.9f}".rstrip("0").rstrip("."),
                                     f"{x:.10g}", f"{y:.10g}", f"{z:.10g}"))
            identities.add(identity)
            record.update(status="exported", output_csv=str(destination.relative_to(output)),
                          session_id=identity[0], event_id=identity[1],
                          source_csv_sha256=source_hash, source_json_sha256=metadata_hash,
                          exported_samples=len(samples), **stats)
            print(f"EXPORT {path.name}: {len(samples)} campioni -> {destination.name}")
        records.append(record)
    exported = sum(record["status"] == "exported" for record in records)
    report = dict(format_version=1, axes=["accX", "accY", "accZ"], units="g",
                  rate_hz=rate_hz, start_relative_trigger_ms=start_ms,
                  end_relative_trigger_ms_exclusive=end_ms, trigger_at_export_ms=-start_ms,
                  window_duration_ms=end_ms - start_ms, preprocessing="linear_interpolation_only",
                  offset_removed=False, max_allowed_imu_gap_us=MAX_GAP_US,
                  label=label, condition=condition, split=split, notes=notes,
                  exported=exported, excluded=len(records) - exported, events=records)
    with (output / "export_report.json").open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2, ensure_ascii=False, allow_nan=False)
    print(f"Esportati: {exported}; esclusi: {len(records) - exported}; report: {output / 'export_report.json'}")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Cartella CSV + JSON grezzi, non ricorsiva")
    parser.add_argument("--output", type=Path, required=True, help="Cartella nuova per questo lotto")
    parser.add_argument("--label", choices=("normal", "modified"), required=True)
    parser.add_argument("--condition", choices=("normal", "modified", "restored"))
    parser.add_argument("--split", choices=("training", "calibration", "test"), required=True)
    parser.add_argument("--rate-hz", type=int, default=RATE_HZ)
    parser.add_argument("--start-ms", type=int, default=START_MS)
    parser.add_argument("--end-ms", type=int, default=END_MS)
    parser.add_argument("--notes", default="", help="Protocollo: altezza, pallina, posizione, fissaggio")
    args = parser.parse_args()
    try:
        report = export_batch(args.input, args.output, args.label, args.split,
                              args.condition, args.rate_hz, args.start_ms, args.end_ms, args.notes)
    except (OSError, ValueError) as error:
        parser.exit(2, f"ERRORE: {error}\n")
    # Un lotto parziale ha comunque un report, ma va rivisto prima dell'upload.
    return 1 if report["excluded"] else 0


if __name__ == "__main__":
    sys.exit(main())
