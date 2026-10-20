"""Contratto del segnale condiviso da export PC e inferenza locale.

Solo libreria standard: importare questo modulo non avvia Arduino o servizi.
I timestamp restituiti da resample partono da zero (formato Edge Impulse).
"""
import bisect
import csv
import json
import math
from pathlib import Path
import statistics

RATE_HZ = 100
START_MS = -150
END_MS = 1850  # Estremo escluso; ultimo campione relativo al trigger: +1840 ms.
SAMPLE_COUNT = (END_MS - START_MS) * RATE_HZ // 1000
MAX_GAP_US = 30_000  # Gate di qualita, non soglia di anomalia.
AXES = ("ax_g", "ay_g", "az_g")


def read_capture(path):
    """Ricontrolla CSV e JSON: il solo flag capture_complete non basta."""
    path = Path(path)
    metadata_path = path.with_suffix(".json")
    if metadata_path.resolve().parent != path.resolve().parent:
        raise ValueError("metadati fuori dalla cartella di acquisizione")
    if path.stat().st_size > 4_000_000 or metadata_path.stat().st_size > 64_000:
        raise ValueError("acquisizione troppo grande")
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
    if not 10 <= len(rows) <= 512:
        raise ValueError("servono da 10 a 512 campioni")
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
    if any(not -pre_us <= stamp < post_us for stamp in times):
        raise ValueError("timestamp fuori dalla cattura")
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


def resample(times, acceleration, rate_hz=RATE_HZ, start_ms=START_MS, end_ms=END_MS):
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
        # Stessa precisione serializzata nel CSV di training e nell'input AI.
        values = tuple(float(f"{value:.10g}") for value in values)
        result.append((index * 1000 / rate_hz, *values))
    return result


