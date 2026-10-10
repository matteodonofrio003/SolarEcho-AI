"""Prima acquisizione reale per Arduino App Lab (Linux su UNO Q)."""
"""prova ciao"""
from arduino.app_utils import App, Bridge

import csv
from datetime import datetime
from pathlib import Path
from queue import Empty, Queue
import statistics
import time
from uuid import uuid4


CAPTURE_ID = 1
# App Lab conserva i dati persistenti nella cartella data/ della App.
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
messages = Queue()
samples = []
expected_samples = None
capture_started = False
capture_finished = False
capture_started_at = None
start_at = time.monotonic() + 5.0
session_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:8]}"


def on_begin(capture_id, count):
    messages.put(("begin", capture_id, count))


def on_sample(capture_id, index, timestamp_us, ax_g, ay_g, az_g,
              piezo_state, piezo_threshold_crossings, piezo_event_count,
              piezo_adc, piezo_peak_adc, piezo_timestamp_us, piezo_max_gap_us):
    messages.put(("sample", capture_id, index, timestamp_us, ax_g, ay_g, az_g,
                  piezo_state, piezo_threshold_crossings, piezo_event_count,
                  piezo_adc, piezo_peak_adc, piezo_timestamp_us, piezo_max_gap_us))


def on_end(capture_id, count, overflow):
    messages.put(("end", capture_id, count, overflow))


def save_capture(declared_count, overflow):
    if not samples:
        print("SENSOR ERROR: nessun campione ricevuto.")
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    destination = OUTPUT_DIR / f"{session_id}.csv"
    with destination.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(("session_id", "event_id", "sample_index", "timestamp_us",
                         "ax_g", "ay_g", "az_g", "trigger_source", "trigger_state",
                         "piezo_threshold_crossings", "piezo_event_count",
                         "piezo_adc", "piezo_peak_adc", "piezo_timestamp_us", "piezo_max_gap_us"))
        for (index, timestamp_us, ax_g, ay_g, az_g,
             piezo_state, piezo_threshold_crossings, piezo_event_count,
             piezo_adc, piezo_peak_adc, piezo_timestamp_us, piezo_max_gap_us) in samples:
            writer.writerow((session_id, 0, index, timestamp_us,
                             ax_g, ay_g, az_g, "manual_window", piezo_state,
                             piezo_threshold_crossings, piezo_event_count,
                             piezo_adc, piezo_peak_adc, piezo_timestamp_us, piezo_max_gap_us))

    times = [row[1] for row in samples]
    intervals_us = [b - a for a, b in zip(times, times[1:])]
    indices = [row[0] for row in samples]
    complete = (len(samples) == declared_count == expected_samples
                and indices == list(range(len(samples)))
                and all(delta > 0 for delta in intervals_us)
                and not overflow)
    print(f"CSV: {destination}")
    print(f"Campioni: {len(samples)}; dichiarati dal firmware: {declared_count}; "
          f"cattura completa: {complete}")
    if intervals_us:
        print(f"Frequenza effettiva media: {1_000_000 / statistics.mean(intervals_us):.1f} Hz; "
              f"intervallo min/max: {min(intervals_us)} / {max(intervals_us)} us")
    if not complete:
        print("ATTENZIONE: cattura incompleta, non usarla come baseline.")


Bridge.provide("solarecho_begin", on_begin)
Bridge.provide("solarecho_sample", on_sample)
Bridge.provide("solarecho_end", on_end)
print("Acquisizione fra 5 secondi; poi 6 secondi per far cadere la pallina.")


def loop():
    global capture_started, capture_finished, capture_started_at, expected_samples

    if not capture_started and time.monotonic() >= start_at:
        result = Bridge.call("solarecho_start_capture", CAPTURE_ID)
        capture_started = True
        capture_started_at = time.monotonic()
        if result != 1:
            capture_finished = True
            print(f"Impossibile avviare la cattura: codice {result} (-1 = sensore, 0 = occupato).")
        else:
            print("Cattura avviata: far cadere la pallina ora.")

    try:
        while True:
            message = messages.get_nowait()
            kind, capture_id, *payload = message
            if capture_id != CAPTURE_ID:
                continue
            if kind == "begin":
                expected_samples = payload[0]
                print(f"Trasferimento di {expected_samples} campioni...")
            elif kind == "sample":
                samples.append(tuple(payload))
            elif kind == "end":
                if not capture_finished:
                    save_capture(payload[0], payload[1])
                    capture_finished = True
    except Empty:
        pass

    if (capture_started and not capture_finished and capture_started_at is not None
            and time.monotonic() - capture_started_at > 30):
        print("Timeout del trasferimento Bridge: controllare il log e la connessione.")
        save_capture(expected_samples or 0, overflow=True)
        capture_finished = True

    time.sleep(0.05)


App.run(user_loop=loop)
