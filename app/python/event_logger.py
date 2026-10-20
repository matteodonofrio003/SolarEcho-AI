"""Logger e protocollo delle catture, indipendenti dal runtime Arduino.

I callback sono iniettati dall'app; i test usano un ACK fittizio e file temporanei.
"""
import csv
import json
from pathlib import Path
from queue import Empty, Queue
import statistics
import time

from signal_processing import MAX_GAP_US


class EventLogger:
    def __init__(self, output_dir, session_id, acknowledge, *, on_saved=None,
                 on_error=None, clock=None, transfer_timeout_s=10.0):
        self.output_dir = Path(output_dir)
        self.session_id = session_id
        self.acknowledge = acknowledge
        self.on_saved = on_saved or (lambda path: None)
        self.on_error = on_error or (lambda message: None)
        self.clock = clock or time.monotonic
        self.transfer_timeout_s = transfer_timeout_s
        self.messages = Queue()
        self.pending = None
        self.closed_ids = set()
        self.halted = False

    def on_ready(self, previous_capture_id):
        self.messages.put(("ready", previous_capture_id))

    def on_begin(self, capture_id, count, pre_count, pre_us, post_us, trigger_adc, event_count):
        self.messages.put(("begin", capture_id, count, pre_count, pre_us, post_us,
                           trigger_adc, event_count))

    def on_sample(self, capture_id, *sample):
        self.messages.put(("sample", capture_id, *sample))

    def on_end(self, capture_id, count, overflow, additional_events):
        self.messages.put(("end", capture_id, count, overflow, additional_events))

    def save_capture(self, capture, declared_count, overflow, additional_events, timed_out=False):
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
        if intervals_us and max(intervals_us) > MAX_GAP_US:
            reasons.append("interruzione nel campionamento IMU")
        actual_pre = sum(stamp < 0 for stamp in times)
        if (actual_pre != capture["pretrigger_samples"] or not times
                or times[0] > -capture["pretrigger_us"] + MAX_GAP_US):
            reasons.append("pretrigger insufficiente")
        if not times or times[-1] < capture["posttrigger_us"] - MAX_GAP_US:
            reasons.append("risposta dopo il trigger incompleta")
        if any(not -capture["pretrigger_us"] <= stamp < capture["posttrigger_us"] for stamp in times):
            reasons.append("timestamp fuori finestra")
        if additional_events:
            reasons.append("altri eventi piezo nella stessa finestra")
        capture_complete = not reasons

        self.output_dir.mkdir(parents=True, exist_ok=True)
        stem = f"{self.session_id}_event_{capture['event_id']:04d}"
        destination = self.output_dir / f"{stem}.csv"
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
                writer.writerow((self.session_id, capture["event_id"], index, timestamp_us,
                                 ax_g, ay_g, az_g, "piezo_analog", piezo_state,
                                 piezo_threshold_crossings, piezo_event_count,
                                 piezo_adc, piezo_peak_adc, piezo_timestamp_us, piezo_max_gap_us,
                                 capture_complete))

        frequency_hz = None
        if intervals_us and all(delta > 0 for delta in intervals_us):
            frequency_hz = 1_000_000 / statistics.mean(intervals_us)
        metadata = {key: value for key, value in capture.items()
                    if key not in ("samples", "received_at")}
        metadata.update(session_id=self.session_id, transport_complete=transport_complete,
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

    def finish_capture(self, count, overflow, additional_events, timed_out=False):
        capture_id = self.pending["event_id"]
        try:
            destination = self.save_capture(self.pending, count, overflow, additional_events, timed_out)
            self.on_saved(destination)
        except OSError as error:
            self.halted = True
            self.on_error(f"Salvataggio fallito: {error}. Acquisizione sospesa.")
            print(f"ERRORE salvataggio: {error}. Acquisizione sospesa; correggere e riavviare la App.")
        else:
            try:
                result = self.acknowledge(capture_id)
                if result != 1:
                    self.halted = True
                    self.on_error("Conferma CSV rifiutata dal firmware. Riavviare la App.")
                    print("ERRORE conferma CSV: firmware non in attesa. Riavviare la App.")
            except Exception as error:
                self.halted = True
                self.on_error(f"Errore Bridge durante conferma CSV: {error}")
                print(f"ERRORE Bridge durante conferma CSV: {error}. Riavviare la App.")
        self.closed_ids.add(capture_id)
        self.pending = None

    def process(self):
        try:
            while True:
                message = self.messages.get_nowait()
                kind, capture_id, *payload = message
                if kind == "ready":
                    if not self.halted:
                        print("READY: far cadere una pallina; poi attendere il prossimo READY.")
                    continue
                if capture_id in self.closed_ids:
                    continue
                if kind == "begin":
                    if self.pending is not None:
                        print("ERRORE protocollo: inizio evento durante un trasferimento; riavviare la App.")
                        self.halted = True
                        self.on_error("Inizio evento durante un trasferimento. Riavviare la App.")
                        continue
                    count, pre_count, pre_us, post_us, trigger_adc, event_count = payload
                    self.pending = dict(event_id=capture_id, expected_samples=count,
                                        pretrigger_samples=pre_count, pretrigger_us=pre_us,
                                        posttrigger_us=post_us, trigger_adc=trigger_adc,
                                        trigger_event_count=event_count, samples=[], received_at=self.clock())
                    print(f"Evento {capture_id}: trasferimento di {count} campioni...")
                elif self.pending is not None and capture_id == self.pending["event_id"]:
                    self.pending["received_at"] = self.clock()
                    if kind == "sample":
                        self.pending["samples"].append(tuple(payload))
                    elif kind == "end":
                        self.finish_capture(*payload)
        except Empty:
            pass

        if self.pending is not None and self.clock() - self.pending["received_at"] > self.transfer_timeout_s:
            print("Timeout del trasferimento Bridge: controllare il log e la connessione.")
            self.finish_capture(self.pending["expected_samples"], True, 0, timed_out=True)
