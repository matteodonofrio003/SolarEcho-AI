"""Export locale SolarEcho -> Edge Impulse. Solo libreria standard Python.

Non carica dati online, non modifica i grezzi e non assegna classi dal segnale.
"""
import argparse
import bisect
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys


MAX_GAP_US = 30_000  # Stesso gate iniziale del logger, non soglia di anomalia.
AXES = ("ax_g", "ay_g", "az_g")


def read_capture(path):
    """Ricontrolla CSV e JSON: il solo flag capture_complete non basta."""
    metadata_path = path.with_suffix(".json")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8-sig"))
    if not isinstance(metadata, dict):
        raise ValueError("il JSON deve contenere un oggetto")
    for field in ("capture_complete", "transport_complete"):
        if metadata.get(field) is not True:
            raise ValueError(f"{field} non True: {metadata.get('unusable_reasons', [])}")
    if metadata.get("overflow") is not False or metadata.get("timed_out") is not False:
        raise ValueError("overflow/timeout presente o non documentato")
    if metadata.get("additional_events") != 0:
        raise ValueError("ulteriori impatti nella finestra o dato non documentato")

    with path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        required = {"session_id", "event_id", "sample_index", "timestamp_us",
                    "capture_complete", "trigger_source", *AXES}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("colonne del logger mancanti")
        rows = list(reader)
    if len(rows) < 10:
        raise ValueError("meno di 10 campioni")
    for field in ("received_samples", "declared_samples", "expected_samples"):
        if metadata.get(field) != len(rows):
            raise ValueError(f"conteggio {field} incoerente")

    times, acceleration = [], []
    for index, row in enumerate(rows):
        if None in row or any(value is None for value in row.values()):
            raise ValueError("riga CSV incompleta o con colonne aggiuntive")
        if int(row["sample_index"]) != index:
            raise ValueError("indici campioni mancanti, duplicati o non ordinati")
        if (row["session_id"] != metadata.get("session_id")
                or int(row["event_id"]) != metadata.get("event_id")):
            raise ValueError("sessione/evento incoerente fra CSV e JSON")
        if row["capture_complete"].lower() != "true":
            raise ValueError("CSV marcato come cattura incompleta")
        if row["trigger_source"] != "piezo_analog":
            raise ValueError("sorgente trigger non supportata da questo export")
        times.append(int(row["timestamp_us"]))
        values = tuple(float(row[axis]) for axis in AXES)
        if not all(math.isfinite(value) for value in values):
            raise ValueError("accelerazione NaN o infinita")
        acceleration.append(values)

    intervals = [b - a for a, b in zip(times, times[1:])]
    if min(intervals) <= 0:
        raise ValueError("timestamp non strettamente crescenti")
    if max(intervals) > MAX_GAP_US:
        raise ValueError("buco IMU superiore a 30 ms")
    pre_us, post_us = metadata["pretrigger_us"], metadata["posttrigger_us"]
    if not isinstance(pre_us, int) or not isinstance(post_us, int) or min(pre_us, post_us) <= 0:
        raise ValueError("durata pre/post trigger non valida")
    if (times[0] < -pre_us or times[0] > -pre_us + MAX_GAP_US
            or times[-1] >= post_us or times[-1] < post_us - MAX_GAP_US):
        raise ValueError("copertura della cattura grezza insufficiente")
    if sum(stamp < 0 for stamp in times) != metadata.get("pretrigger_samples"):
        raise ValueError("conteggio pretrigger incoerente")
    stats = {
        "raw_samples": len(times),
        "mean_sample_rate_hz": 1_000_000 / statistics.mean(intervals),
        "median_sample_rate_hz": 1_000_000 / statistics.median(intervals),
        "max_imu_gap_us": max(intervals),
        "raw_first_timestamp_us": times[0],
        "raw_last_timestamp_us": times[-1],
    }
    return times, acceleration, metadata, stats


def resample(times, acceleration, rate_hz=100, start_ms=-150, end_ms=1950):
    """Griglia [start, end), interpolazione lineare, nessuna estrapolazione.

    Non e' un filtro antialias e non recupera frequenze/campioni non acquisiti.
    """
    if rate_hz <= 0 or end_ms <= start_ms:
        raise ValueError("frequenza/durata non valida")
    count, remainder = divmod((end_ms - start_ms) * rate_hz, 1000)
    if remainder or count < 2:
        raise ValueError("durata * frequenza deve dare un numero intero di campioni >= 2")
    intervals = [b - a for a, b in zip(times, times[1:])]
    mean_rate = 1_000_000 / statistics.mean(intervals)
    median_rate = 1_000_000 / statistics.median(intervals)
    if rate_hz > min(mean_rate, median_rate) * 1.01:
        raise ValueError("frequenza di export superiore alla frequenza acquisita (tolleranza 1%)")
    first = start_ms * 1000
    last = first + (count - 1) * 1_000_000 / rate_hz
    if first < times[0] or last > times[-1]:
        raise ValueError("il segnale non copre la griglia richiesta; niente estrapolazione")
    result = []
    for index in range(count):
        target = first + index * 1_000_000 / rate_hz
        right = bisect.bisect_left(times, target)
        if times[right] == target:
            values = acceleration[right]
        else:
            left = right - 1
            weight = (target - times[left]) / (times[right] - times[left])
            values = tuple(a + weight * (b - a)
                           for a, b in zip(acceleration[left], acceleration[right]))
        # Edge Impulse riceve millisecondi da zero, non timestamp relativi al trigger.
        result.append((index * 1000 / rate_hz, *values))
    return result


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def export_batch(source, output, label, split, condition=None, rate_hz=100,
                 start_ms=-150, end_ms=1950, notes=""):
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
    parser.add_argument("--rate-hz", type=int, default=100)
    parser.add_argument("--start-ms", type=int, default=-150)
    parser.add_argument("--end-ms", type=int, default=1950)
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
