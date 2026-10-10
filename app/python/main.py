"""Cattura per impatto: pretrigger IMU, CSV e controllo della qualita' locale."""
"""prova ciao"""
from arduino.app_utils import App, Bridge

import csv
import json
from datetime import datetime
from pathlib import Path
from queue import Empty, Queue
import statistics
import time
from uuid import uuid4


# App Lab conserva i dati persistenti nella cartella data/ della App.
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
TRANSFER_TIMEOUT_S = 10.0
MAX_IMU_GAP_US = 30_000  # Gate conservativo iniziale, da verificare sui CSV reali.
messages = Queue()
pending = None
closed_ids = set()
armed = False
halted = False
next_arm_at = time.monotonic() + 1.0
session_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:8]}"


def on_ready(previous_capture_id):
    messages.put(("ready", previous_capture_id))


def on_begin(capture_id, count, pre_count, pre_us, post_us, trigger_adc, event_count):
    messages.put(("begin", capture_id, count, pre_count, pre_us, post_us,
                  trigger_adc, event_count))


def on_sample(capture_id, index, timestamp_us, ax_g, ay_g, az_g,
              piezo_state, piezo_threshold_crossings, piezo_event_count,
              piezo_adc, piezo_peak_adc, piezo_timestamp_us, piezo_max_gap_us):
    messages.put(("sample", capture_id, index, timestamp_us, ax_g, ay_g, az_g,
                  piezo_state, piezo_threshold_crossings, piezo_event_count,
                  piezo_adc, piezo_peak_adc, piezo_timestamp_us, piezo_max_gap_us))


def on_end(capture_id, count, overflow, additional_events):
    messages.put(("end", capture_id, count, overflow, additional_events))


def save_capture(capture, declared_count, overflow, additional_events, timed_out=False):
    """Salva anche catture inutilizzabili; il JSON ne esplicita le ragioni."""
    samples = capture["samples"]
    times = [row[1] for row in samples]
    intervals_us = [b - a for a, b in zip(times, times[1:])]
    indices = [row[0] for row in samples]
    reasons = []
    transport_complete = (
        bool(samples) and len(samples) == declared_count == capture["expected_samples"]
        and indices == list(range(len(samples))) and not overflow and not timed_out
    )
    if not transport_complete:
        reasons.append("trasferimento incompleto, indici non validi o overflow")
    if len(samples) < 10 or not intervals_us or any(delta <= 0 for delta in intervals_us):
        reasons.append("campioni insufficienti o timestamp non crescenti")
    if intervals_us and max(intervals_us) > MAX_IMU_GAP_US:
        reasons.append("interruzione nel campionamento IMU")
    actual_pre = sum(stamp < 0 for stamp in times)
    if (actual_pre != capture["pretrigger_samples"] or not times
            or times[0] > -capture["pretrigger_us"] + MAX_IMU_GAP_US):
        reasons.append("pretrigger insufficiente")
    if not times or times[-1] < capture["posttrigger_us"] - MAX_IMU_GAP_US:
        reasons.append("risposta dopo il trigger incompleta")
    if any(not -capture["pretrigger_us"] <= stamp < capture["posttrigger_us"] for stamp in times):
        reasons.append("timestamp fuori finestra")
    if additional_events:
        reasons.append("altri eventi piezo nella stessa finestra")
    capture_complete = not reasons

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    stem = f"{session_id}_event_{capture['event_id']:04d}"
    destination = OUTPUT_DIR / f"{stem}.csv"
    with destination.open("x", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(("session_id", "event_id", "sample_index", "timestamp_us",
                         "ax_g", "ay_g", "az_g", "trigger_source", "trigger_state",
                         "piezo_threshold_crossings", "piezo_event_count",
                         "piezo_adc", "piezo_peak_adc", "piezo_timestamp_us", "piezo_max_gap_us",
                         "capture_complete"))
        for (index, timestamp_us, ax_g, ay_g, az_g,
             piezo_state, piezo_threshold_crossings, piezo_event_count,
             piezo_adc, piezo_peak_adc, piezo_timestamp_us, piezo_max_gap_us) in samples:
            writer.writerow((session_id, capture["event_id"], index, timestamp_us,
                             ax_g, ay_g, az_g, "piezo_analog", piezo_state,
                             piezo_threshold_crossings, piezo_event_count,
                             piezo_adc, piezo_peak_adc, piezo_timestamp_us, piezo_max_gap_us,
                             capture_complete))

    frequency_hz = None
    if intervals_us and all(delta > 0 for delta in intervals_us):
        frequency_hz = 1_000_000 / statistics.mean(intervals_us)
    metadata = {key: value for key, value in capture.items()
                if key not in ("samples", "received_at")}
    metadata.update(session_id=session_id, transport_complete=transport_complete,
                    capture_complete=capture_complete, unusable_reasons=reasons,
                    received_samples=len(samples), declared_samples=declared_count,
                    overflow=bool(overflow), timed_out=timed_out,
                    additional_events=additional_events, mean_sample_rate_hz=frequency_hz,
                    max_imu_gap_us=max(intervals_us) if intervals_us else None)
    with destination.with_suffix(".json").open("x", encoding="utf-8") as stream:
        json.dump(metadata, stream, indent=2, ensure_ascii=False)

    print(f"CSV: {destination}")
    print(f"Campioni: {len(samples)}; dichiarati dal firmware: {declared_count}; "
          f"cattura completa: {capture_complete}")
    if frequency_hz is not None:
        print(f"Frequenza effettiva media: {frequency_hz:.1f} Hz; "
              f"intervallo min/max: {min(intervals_us)} / {max(intervals_us)} us")
    if reasons:
        print("Non usare come baseline: " + "; ".join(reasons))
    return destination


Bridge.provide("solarecho_begin", on_begin)
Bridge.provide("solarecho_sample", on_sample)
Bridge.provide("solarecho_end", on_end)
Bridge.provide("solarecho_ready", on_ready)
print("Acquisizione automatica: attendere READY prima di ogni impatto.")


def finish_capture(count, overflow, additional_events, timed_out=False):
    global pending, halted
    capture_id = pending["event_id"]
    try:
        save_capture(pending, count, overflow, additional_events, timed_out)
    except OSError as error:
        halted = True
        print(f"ERRORE salvataggio: {error}. Acquisizione sospesa; correggere e riavviare la App.")
    else:
        try:
            result = Bridge.call("solarecho_ack", capture_id)
            if result != 1:
                halted = True
                print("ERRORE conferma CSV: firmware non in attesa. Riavviare la App.")
        except Exception as error:
            halted = True
            print(f"ERRORE Bridge durante conferma CSV: {error}. Riavviare la App.")
    closed_ids.add(capture_id)
    pending = None


def loop():
    global pending, armed, halted, next_arm_at

    if not armed and not halted and time.monotonic() >= next_arm_at:
        next_arm_at = time.monotonic() + 1.0
        try:
            result = Bridge.call("solarecho_arm")
            if result == 1:
                armed = True
            elif result == -1:
                halted = True
                print("SENSOR ERROR: Modulino non inizializzato. Controllare Qwiic e riavviare.")
        except Exception as error:
            print(f"Attesa firmware Bridge: {error}")

    try:
        while True:
            message = messages.get_nowait()
            kind, capture_id, *payload = message
            if kind == "ready":
                if not halted:
                    print("READY: far cadere una pallina; poi attendere il prossimo READY.")
                continue
            if capture_id in closed_ids:
                continue
            if kind == "begin":
                if pending is not None:
                    print("ERRORE protocollo: inizio evento durante un trasferimento; riavviare la App.")
                    halted = True
                    continue
                count, pre_count, pre_us, post_us, trigger_adc, event_count = payload
                pending = dict(event_id=capture_id, expected_samples=count,
                               pretrigger_samples=pre_count, pretrigger_us=pre_us,
                               posttrigger_us=post_us, trigger_adc=trigger_adc,
                               trigger_event_count=event_count, samples=[], received_at=time.monotonic())
                print(f"Evento {capture_id}: trasferimento di {count} campioni...")
            elif pending is not None and capture_id == pending["event_id"]:
                pending["received_at"] = time.monotonic()
                if kind == "sample":
                    pending["samples"].append(tuple(payload))
                elif kind == "end":
                    finish_capture(*payload)
    except Empty:
        pass

    if pending is not None and time.monotonic() - pending["received_at"] > TRANSFER_TIMEOUT_S:
        print("Timeout del trasferimento Bridge: controllare il log e la connessione.")
        finish_capture(pending["expected_samples"], True, 0, timed_out=True)

    time.sleep(0.05)


App.run(user_loop=loop)
