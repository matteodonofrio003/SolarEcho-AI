"""Inferenza locale per impatto, con origine reale/sintetica e dati persistenti."""
import copy
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
from queue import Empty, Queue
import re
import statistics
from threading import Event, RLock, Thread
import time
from uuid import uuid4

from signal_processing import END_MS, RATE_HZ, SAMPLE_COUNT, START_MS, read_capture, resample


MODEL_ID = "ei-model-1136239-1"
PROJECT_ID = 1136239
RESULT_ID = re.compile(r"[0-9a-f]{32}")
# Da configurare con il valore usato in Edge Impulse, non scelto dai sintetici.
DEFAULT_THRESHOLD = None
STRESS = {"name": "stress_sustained", "amplitude_g": 0.35,
          "frequencies_hz": [8.0, 17.0, 29.0], "ramp_time_s": 0.05}


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def prepare_capture(path):
    """Usa gli stessi controlli, griglia e precisione dell'export Edge Impulse."""
    path = Path(path)
    times, axes, _, quality = read_capture(path)
    exported = resample(times, axes)
    # Solo il riferimento temporale cambia: i 600 valori XYZ restano identici.
    samples = [[stamp + START_MS, x, y, z] for stamp, x, y, z in exported]
    return samples, {"raw_samples": quality["raw_samples"],
                     "mean_rate_hz": quality["mean_sample_rate_hz"],
                     "max_gap_us": quality["max_imu_gap_us"],
                     "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def stress_samples(samples):
    """Identico al profilo stress del generatore offline, con tempo dal trigger."""
    result = []
    for stamp, *axes in samples:
        if stamp >= 0:
            elapsed = stamp/1000
            ramp = min(1.0, elapsed/STRESS["ramp_time_s"])
            axes = [v+ramp*STRESS["amplitude_g"]*math.sin(2*math.pi*f*elapsed)
                    for v,f in zip(axes, STRESS["frequencies_hz"])]
        result.append([stamp, *(float(f"{v:.12g}") for v in axes)])
    return result


def diagnostics(samples):
    pre = [row for row in samples if row[0] < 0]
    offset = [statistics.mean(row[k+1] for row in pre) for k in range(3)]
    dynamic = [sum((row[k+1]-offset[k])**2 for k in range(3))
               for row in samples if row[0] >= 0]
    return {"rms_g": math.sqrt(statistics.mean(dynamic)), "peak_g": math.sqrt(max(dynamic))}


def create_detector():
    """SDK inizializzato solo dal worker: mantiene intatta l'identita del brick."""
    from arduino.app_bricks.vibration_anomaly_detection import VibrationAnomalyDetection
    from arduino.app_utils import App
    detector = VibrationAnomalyDetection(anomaly_detection_threshold=0.0)
    # Non usiamo il loop continuo: la finestra arriva gia completa dal piezo.
    App.unregister(detector)
    info = detector.get_model_info()
    if (info is None or getattr(info, "project_id", None) != PROJECT_ID
            or info.frequency != RATE_HZ or info.input_features_count != SAMPLE_COUNT*3
            or getattr(info, "axis_count", None) != 3):
        raise RuntimeError("Modello inatteso: servono progetto 1136239, 100 Hz, 600 valori XYZ")
    return detector, {"id": MODEL_ID, "project_id": info.project_id,
                      "name": info.name, "frequency_hz": info.frequency,
                      "input_features_count": info.input_features_count, "units": "g"}


class VibrationAI:
    def __init__(self, directory, inspection):
        self.directory, self.inspection = Path(directory), inspection
        self.lock, self.stopping = RLock(), Event()
        self.queue = Queue(maxsize=4)
        self.worker, self.detector, self.http = None, None, None
        self.connection, self.error, self.io_error = "STARTING", None, None
        self.model = {"id": MODEL_ID}
        self.settings = {"threshold": DEFAULT_THRESHOLD, "alerts_enabled": True}
        self.active_id, self.jobs = None, []
        self.latest_real, self.latest_synthetic = None, None
        try:
            config = self.directory / "settings.json"
            if config.exists():
                saved = json.loads(config.read_text(encoding="utf-8"))
                if saved.get("model_id") == MODEL_ID:
                    self.settings = self._validate_settings(saved["settings"])
            paths = sorted(self.directory.glob("result_*.json"), key=lambda p: p.stat().st_mtime)[-20:]
            for path in paths:
                if path.is_symlink() or path.stat().st_size > 128_000:
                    continue
                record = json.loads(path.read_text(encoding="utf-8"))
                if (not isinstance(record, dict) or not RESULT_ID.fullmatch(str(record.get("id", "")))
                        or record.get("model_id") != MODEL_ID):
                    continue
                summary = self._summary(record)
                self.jobs.append(summary)
                if record.get("state") == "DONE" and record.get("score") is not None:
                    if record.get("synthetic") is True:
                        self.latest_synthetic = summary
                    else:
                        self.latest_real = summary
        except (OSError, ValueError, KeyError, TypeError) as error:
            self.io_error = f"Archivio AI non caricato: {error}"

    @staticmethod
    def _validate_settings(settings):
        if not isinstance(settings, dict) or set(settings) != {"threshold", "alerts_enabled"}:
            raise ValueError("Servono soglia AI e abilitazione allerta")
        value = settings["threshold"]
        if value is not None and (isinstance(value, bool) or not isinstance(value, (float,int))
                                  or not math.isfinite(value)):
            raise ValueError("Soglia AI non valida")
        if not isinstance(settings["alerts_enabled"], bool):
            raise ValueError("Abilitazione allerta non valida")
        return dict(settings)

    def _write(self, path, data):
        self.directory.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(".tmp")
        with temporary.open("w", encoding="utf-8") as stream:
            json.dump(data, stream, indent=2, ensure_ascii=False, allow_nan=False)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)

    def update_settings(self, settings):
        values = self._validate_settings(settings)
        with self.lock:
            self._write(self.directory / "settings.json", {"model_id": MODEL_ID, "settings": values})
            self.settings = values
        return self.status()

    @staticmethod
    def _summary(record):
        return {k: copy.deepcopy(v) for k,v in record.items()
                if k not in ("samples", "original_samples")}

    def status(self):
        with self.lock:
            return {"connection": self.connection, "error": self.error, "io_error": self.io_error,
                    "ready": self.connection == "READY", "model": dict(self.model),
                    "settings": dict(self.settings), "active_id": self.active_id,
                    "queued": self.queue.qsize(), "history": copy.deepcopy(self.jobs[-20:][::-1]),
                    "latest_real": copy.deepcopy(self.latest_real),
                    "latest_synthetic": copy.deepcopy(self.latest_synthetic)}

    def submit(self, path, *, synthetic=False):
        with self.lock:
            if synthetic and self.connection != "READY":
                raise RuntimeError("Modello AI non pronto")
            if self.queue.full():
                raise RuntimeError("Coda AI piena; attendere il completamento")
            job = {"id": uuid4().hex, "at_utc": utc_now(), "source_event": Path(path).stem,
                   "synthetic": synthetic, "model_id": MODEL_ID, "state": "QUEUED",
                   "threshold": self.settings["threshold"],
                   "alerts_enabled": self.settings["alerts_enabled"]}
            self.queue.put_nowait((Path(path), job))
            self.jobs.append(dict(job))
            self.jobs = self.jobs[-20:]
            return dict(job)

    def result(self, result_id):
        if not isinstance(result_id, str) or not RESULT_ID.fullmatch(result_id):
            raise ValueError("Identificativo inferenza non valido")
        path = self.directory / f"result_{result_id}.json"
        if path.is_symlink() or path.stat().st_size > 128_000:
            raise ValueError("Report AI non valido")
        return json.loads(path.read_text(encoding="utf-8"))

    def start(self):
        with self.lock:
            if self.worker is None:
                self.worker = Thread(target=self._run, name="SolarEcho-AI", daemon=True)
                self.worker.start()

    def stop(self):
        self.stopping.set()
        if self.worker is not None:
            self.worker.join(timeout=1)

    def _infer(self, samples):
        features = [v for row in samples for v in row[1:]]
        if len(features) != SAMPLE_COUNT*3 or not all(math.isfinite(v) for v in features):
            raise ValueError("Input AI non valido")
        started = time.perf_counter()
        # API locale usata dalla facade ufficiale; timeout esplicito per il worker.
        response = self.http.post(f"{self.detector.url}/api/features",
                                  json={"features": features}, timeout=(3, 20))
        response.raise_for_status()
        payload = response.json()
        score = (payload.get("result") or {}).get("anomaly")
        if isinstance(score, bool) or not isinstance(score, (int,float)) or not math.isfinite(score):
            raise RuntimeError("Runner senza score di anomalia numerico")
        return float(score), (time.perf_counter()-started)*1000

    def _process(self, path, job):
        try:
            original, quality = prepare_capture(path)
        except (OSError, ValueError, KeyError, TypeError, csv.Error) as error:
            job.update(state="SKIPPED", error=str(error))
            return
        samples = stress_samples(original) if job["synthetic"] else original
        score, latency = self._infer(samples)
        threshold = job["threshold"]
        decision = "UNCALIBRATED" if threshold is None else "ANOMALY" if score >= threshold else "NORMAL"
        job.update(state="DONE", score=score, decision=decision, inference_ms=latency,
                   quality=quality, diagnostics=diagnostics(samples), samples=samples,
                   frequency_hz=RATE_HZ, units="g", window_start_ms=START_MS,
                   window_end_ms_exclusive=END_MS, transform=dict(STRESS) if job["synthetic"] else None)
        if job["synthetic"]:
            job["original_samples"] = original
            # Confronto misurato sulla stessa cattura e sullo stesso runner.
            base_score, base_latency = self._infer(original)
            job.update(original_score=base_score, original_inference_ms=base_latency,
                       original_diagnostics=diagnostics(original))
        if threshold is not None and job["alerts_enabled"] and not self.stopping.is_set():
            self.inspection.on_ai_result(score, threshold, path.stem, comparable=True,
                                         synthetic=job["synthetic"], model_id=MODEL_ID,
                                         inference_id=job["id"])
        print(f"AI_RESULT origin={'SYNTHETIC_TEST' if job['synthetic'] else 'REAL'} "
              f"event={path.stem} score={score:.6f} threshold={threshold} "
              f"decision={decision} inference_ms={latency:.1f}", flush=True)

    def _finish(self, job):
        job["completed_at_utc"] = utc_now()
        try:
            self._write(self.directory / f"result_{job['id']}.json", job)
            path = self.directory / "inferences.csv"
            has_header = path.exists() and path.stat().st_size > 0
            with path.open("a", newline="", encoding="utf-8") as stream:
                fields = ("id", "at_utc", "model_id", "source_event", "synthetic", "state",
                          "score", "threshold", "decision", "inference_ms", "original_score", "error")
                writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
                if not has_header:
                    writer.writeheader()
                writer.writerow(job)
            with self.lock:
                self.io_error = None
        except OSError as error:
            with self.lock:
                self.io_error = f"Risultato AI non completamente salvato: {error}"
        summary = self._summary(job)
        with self.lock:
            self.jobs = [summary if item["id"] == job["id"] else item for item in self.jobs]
            if job.get("state") == "DONE":
                if job["synthetic"]:
                    self.latest_synthetic = summary
                else:
                    self.latest_real = summary
            self.active_id = None

    def _run(self):
        try:
            import requests
            self.http = requests.Session()
        except Exception as error:
            with self.lock:
                self.connection, self.error = "ERROR", f"Avvio worker AI: {error}"
            return
        try:
            while not self.stopping.is_set():
                if self.detector is None:
                    try:
                        detector, model = create_detector()
                        self.detector = detector
                        with self.lock:
                            self.model, self.connection, self.error = model, "READY", None
                        print(f"AI_MODEL id={MODEL_ID} project_id={PROJECT_ID} "
                              f"frequency_hz={RATE_HZ} input_features_count={SAMPLE_COUNT*3} units=g", flush=True)
                    except Exception as error:
                        with self.lock:
                            self.connection = "ERROR"
                            self.error = f"Inizializzazione AI: {type(error).__name__}: {error}"
                        if self.stopping.wait(5):
                            break
                        continue
                try:
                    path, job = self.queue.get(timeout=0.2)
                except Empty:
                    continue
                with self.lock:
                    self.active_id = job["id"]
                try:
                    self._process(path, job)
                    with self.lock:
                        self.error = None
                except Exception as error:
                    job.update(state="ERROR", decision=None, error=f"{type(error).__name__}: {error}")
                    with self.lock:
                        self.error = job["error"]
                self._finish(job)
                self.queue.task_done()
        finally:
            self.http.close()
