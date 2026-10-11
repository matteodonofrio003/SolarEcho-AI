"""Dashboard e controlli del confronto elettrico; nessuna API interroga il microcontrollore."""
import copy
import csv
import json
import math
from pathlib import Path
import re
from threading import Lock
import time

from arduino.app_bricks.web_ui import WebUI
from fastapi import HTTPException
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
from telegram_notifications import utc_now


EVENT_NAME = re.compile(r"\d{8}_\d{6}_[0-9a-f]{8}_event_\d+")


class Dashboard:
    def __init__(self, output_dir, session_id, power_history, electrical_demo, inspection, notifications, vibration_ai):
        self.output_dir = Path(output_dir)
        self.lock = Lock()
        self.live = None
        self.received_at = None
        self.phase = "STARTING"
        self.error = None
        self.last_event = None
        self.session_id = session_id
        self.power_history = power_history
        self.electrical_demo = electrical_demo
        self.inspection = inspection
        self.notifications = notifications
        self.vibration_ai = vibration_ai
        self.web = WebUI(assets_dir_path=str(Path(__file__).resolve().parent.parent / "assets"),
                         cors_origins="")
        self.web.expose_api("GET", "/api/status", self.status)
        self.web.expose_api("GET", "/api/events", self.events)
        self.web.expose_api("GET", "/api/events/{name}", self.event)
        self.web.expose_api("GET", "/api/download/{name}/{extension}", self.download)
        self.web.expose_api("GET", "/api/power", self.power_sessions)
        self.web.expose_api("GET", "/api/power/{name}", self.power_session)
        self.web.expose_api("GET", "/api/power/{name}/download", self.power_download)
        self.web.expose_api("POST", "/api/economics/reference", self.economic_reference)
        self.web.expose_api("POST", "/api/economics/start", self.economic_start)
        self.web.expose_api("POST", "/api/economics/stop", self.economic_stop)
        self.web.expose_api("POST", "/api/economics/settings", self.economic_settings)
        self.web.expose_api("GET", "/api/economics/report", self.economic_report)
        self.web.expose_api("POST", "/api/inspection/reset", self.inspection_reset)
        self.web.expose_api("POST", "/api/inspection/settings", self.inspection_settings)
        self.web.expose_api("GET", "/api/telegram/preview", self.telegram_preview)
        self.web.expose_api("POST", "/api/telegram/settings", self.telegram_settings)
        self.web.expose_api("POST", "/api/telegram/send", self.telegram_send)
        self.web.expose_api("POST", "/api/telegram/reconnect", self.telegram_reconnect)
        self.web.expose_api("POST", "/api/telegram/retry/{request_id}", self.telegram_retry)
        self.web.expose_api("GET", "/api/telegram/report/{request_id}", self.telegram_report)
        self.web.expose_api("POST", "/api/ai/settings", self.ai_settings)
        self.web.expose_api("POST", "/api/ai/analyze", self.ai_analyze)
        self.web.expose_api("POST", "/api/ai/synthetic", self.ai_synthetic)
        self.web.expose_api("GET", "/api/ai/result/{result_id}", self.ai_result)

    def telemetry(self, payload):
        """Callback Bridge corto; mantiene soltanto l'ultima anteprima."""
        try:
            data = json.loads(payload)
            required = ("t_ms", "ready", "imu_ok", "ack_error", "ax", "ay", "az",
                        "adc", "peak", "active", "raw", "events", "suppressed",
                        "power_ok", "power_error", "power_t_ms", "v_in", "v_out",
                        "shunt_mv", "current_ma", "power_w")
            if not isinstance(data, dict) or any(
                not isinstance(data.get(key), (int, float)) or not math.isfinite(data[key])
                for key in required
            ):
                return
        except (TypeError, ValueError):
            return
        with self.lock:
            self.live = data
            self.received_at = time.monotonic()
            self.phase = "READY" if data["ready"] else "WAIT"
        self.inspection.telemetry(data)
        self.power_history.enqueue(data)

    def led_request(self):
        """Lo user_loop invia solo differenze rispetto all'ultima telemetria recente."""
        with self.lock:
            if (not self.live or self.received_at is None or self.phase == "TRANSFER"
                    or self.error or time.monotonic() - self.received_at > 1.8):
                return None
            requested = self.live.get("led_requested")
        desired = self.inspection.desired_led()
        return desired if requested in (0, 1) and requested != desired else None

    def set_phase(self, phase):
        with self.lock:
            self.phase = phase

    def fail(self, message):
        with self.lock:
            self.error = message
            self.phase = "SENSOR_ERROR"

    def saved(self, path):
        with self.lock:
            self.last_event = path.stem

    def status(self):
        with self.lock:
            age = None if self.received_at is None else time.monotonic() - self.received_at
            data = copy.deepcopy(self.live)
            phase, error = self.phase, self.error
            last_event = self.last_event
        if error or (data and data["ack_error"]):
            phase = "SENSOR_ERROR"
            error = error or "Firmware senza conferma del CSV: riavviare la App."
        elif phase != "TRANSFER" and data:
            if age > 8:
                phase = "NO_TELEMETRY"
            elif age > 1.8:
                # Non deduciamo un impatto dall'assenza di telemetria.
                phase = "PAUSED"
            elif not data["imu_ok"]:
                phase = "SENSOR_ERROR"
                error = "Modulino Movement senza dati recenti."
        inspection = self.inspection.status()
        ai = self.vibration_ai.status()
        return {"session_id": self.session_id, "phase": phase, "error": error,
                "telemetry_age_s": age, "live": data, "last_event": last_event,
                "ai_enabled": ai["ready"], "inspection": inspection,
                "ai": ai,
                "power_history": self.power_history.status(),
                "telegram": self.notifications.status(),
                "economics": self.electrical_demo.status()}

    def panel_snapshot(self):
        """Foto dei valori disponibili, senza interrogare MCU, rete o forme d'onda."""
        data = self.status()
        live, age = data["live"], data["telemetry_age_s"]
        fresh = bool(live and age is not None and age < 1.8 and data["phase"] != "TRANSFER")
        power_age = ((live["t_ms"] - live["power_t_ms"]) % (2 ** 32) / 1000 + age) if live and age is not None else None
        power_valid = bool(fresh and live["power_ok"] == 1 and live["power_error"] == 1 and power_age < 3)
        imu_valid = bool(fresh and live["imu_ok"])
        economics = data["economics"]
        reference = economics["reference_w"]
        inspection = copy.deepcopy(data["inspection"])
        if not fresh:
            inspection["impacts_since_reference"] = None
        return {"at_utc": utc_now(), "session_id": data["session_id"], "phase": data["phase"],
                "error": data["error"], "last_event": data["last_event"],
                "telemetry_age_s": age, "impacts": live["events"] if fresh else None,
                "inspection": inspection,
                "ai": {"model": data["ai"]["model"], "ready": data["ai"]["ready"],
                       "latest_real": data["ai"]["latest_real"],
                       "latest_synthetic": data["ai"]["latest_synthetic"]},
                "power": {"valid": power_valid, "age_s": power_age,
                          "voltage_v": live["v_in"] if power_valid else None,
                          "current_ma": live["current_ma"] if power_valid else None,
                          "power_mw": live["power_w"] * 1000 if power_valid else None},
                "imu": {"valid": imu_valid,
                        "ax_g": live["ax"] if imu_valid else None,
                        "ay_g": live["ay"] if imu_valid else None,
                        "az_g": live["az"] if imu_valid else None},
                "economics": {"reference_mw": reference * 1000 if reference is not None else None,
                              "live_reduction_pct": economics["live_reduction_pct"] if power_valid else None,
                              "scenario": economics["scenario"],
                              "scenario_days": economics["settings"]["days"]}}

    def telegram_preview(self):
        return self.notifications.preview(self.panel_snapshot())

    def telegram_settings(self, settings: dict):
        return self._economic_call(self.notifications.update_settings, settings)

    def telegram_send(self, request: dict):
        return self._economic_call(self.notifications.submit, request.get("request_id"), self.panel_snapshot())

    def telegram_reconnect(self):
        return self._economic_call(self.notifications.reconnect)

    def telegram_retry(self, request_id: str):
        return self._economic_call(self.notifications.retry, request_id)

    def telegram_report(self, request_id: str):
        report = self._economic_call(self.notifications.report, request_id)
        return JSONResponse(report, headers={"Content-Disposition": f'attachment; filename="notification_{report["id"]}.json"',
                                             "Cache-Control": "no-store"})

    @staticmethod
    def _economic_call(action, *args, **kwargs):
        try:
            return action(*args, **kwargs)
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
        except RuntimeError as error:
            raise HTTPException(status_code=409, detail=str(error)) from error
        except OSError as error:
            raise HTTPException(status_code=503, detail="Salvataggio non riuscito: controllare spazio e permessi") from error

    def economic_reference(self):
        return self._economic_call(self.electrical_demo.start_reference)

    def ai_settings(self, settings: dict):
        return self._economic_call(self.vibration_ai.update_settings, settings)

    def ai_analyze(self, request: dict):
        return self._economic_call(self.vibration_ai.submit, self._path(request.get("event", ""), "csv"))

    def ai_synthetic(self, request: dict):
        return self._economic_call(self.vibration_ai.submit, self._path(request.get("event", ""), "csv"),
                                   synthetic=True)

    def ai_result(self, result_id: str):
        try:
            result = self.vibration_ai.result(result_id)
            return JSONResponse(result, headers={"Cache-Control": "no-store",
                "Content-Disposition": f'attachment; filename="ai_{result_id}.json"'})
        except (OSError, ValueError, KeyError, TypeError) as error:
            raise self._history_error(error) from error

    def economic_start(self):
        return self._economic_call(self.electrical_demo.start_comparison)

    def economic_stop(self):
        return self._economic_call(self.electrical_demo.finish_comparison)

    def economic_settings(self, settings: dict):
        return self._economic_call(self.electrical_demo.update_settings, settings)

    def inspection_reset(self):
        return self._economic_call(self.inspection.reset)

    def inspection_settings(self, settings: dict):
        return self._economic_call(self.inspection.update_settings, settings)

    def economic_report(self):
        report = self._economic_call(self.electrical_demo.report)
        name = report["comparison"]["id"]
        return JSONResponse(report, headers={"Content-Disposition": f'attachment; filename="{name}.json"',
                                             "Cache-Control": "no-store"})

    @staticmethod
    def _history_error(error):
        if isinstance(error, FileNotFoundError):
            return HTTPException(status_code=404, detail="Storico non trovato")
        if isinstance(error, (ValueError, KeyError, TypeError, csv.Error)):
            return HTTPException(status_code=422, detail="Storico non valido o limite non ammesso")
        return HTTPException(status_code=503, detail="Archivio elettrico non leggibile")

    def power_sessions(self):
        try:
            return self.power_history.sessions()
        except OSError as error:
            raise self._history_error(error) from error

    def power_session(self, name: str, limit: int = 600):
        try:
            return self.power_history.read_session(name, limit)
        except (OSError, ValueError, KeyError, TypeError, csv.Error) as error:
            raise self._history_error(error) from error

    def power_download(self, name: str):
        try:
            path, size = self.power_history.snapshot_size(name)
        except (OSError, ValueError) as error:
            raise self._history_error(error) from error
        return StreamingResponse(self.power_history.download_chunks(path, size), media_type="text/csv",
                                 headers={"Content-Disposition": f'attachment; filename="{path.name}"',
                                          "Content-Length": str(size), "Cache-Control": "no-store"})

    def _path(self, name, extension):
        if not isinstance(name, str) or not EVENT_NAME.fullmatch(name) or extension not in ("csv", "json"):
            raise HTTPException(status_code=400, detail="Nome evento non valido")
        root = self.output_dir.resolve()
        path = root / f"{name}.{extension}"
        # Impedisce anche la lettura di symlink diretti fuori da data/raw.
        if path.resolve().parent != root or not path.is_file():
            raise HTTPException(status_code=404, detail="Evento non trovato")
        return path

    def _metadata(self, name):
        path = self._path(name, "json")
        if path.stat().st_size > 64_000:
            raise HTTPException(status_code=422, detail="Metadati troppo grandi")
        try:
            with path.open(encoding="utf-8") as stream:
                data = json.load(stream)
            if not isinstance(data, dict):
                raise ValueError("Metadati non validi")
            return data
        except (OSError, ValueError) as error:
            raise HTTPException(status_code=422, detail="Metadati non leggibili") from error

    def events(self):
        """Ultimi 100 eventi con CSV e JSON; include quelli marcati inutilizzabili."""
        if not self.output_dir.exists():
            return {"events": [], "total": 0, "limit": 100}
        try:
            paths = sorted(
                (p for p in self.output_dir.glob("*.csv") if EVENT_NAME.fullmatch(p.stem)
                 and p.with_suffix(".json").is_file()),
                key=lambda p: p.stat().st_mtime, reverse=True,
            )
            result = []
            for path in paths[:100]:
                try:
                    meta = self._metadata(path.stem)
                    result.append({"name": path.stem, "complete": meta.get("capture_complete") is True,
                                   "samples": meta.get("received_samples"),
                                   "rate_hz": meta.get("mean_sample_rate_hz"),
                                   "reasons": meta.get("unusable_reasons", [])})
                except HTTPException:
                    result.append({"name": path.stem, "complete": False,
                                   "samples": None, "rate_hz": None,
                                   "reasons": ["Metadati non leggibili"]})
            return {"events": result, "total": len(paths), "limit": 100}
        except OSError as error:
            raise HTTPException(status_code=503, detail="Archivio non leggibile") from error

    def event(self, name: str):
        meta = self._metadata(name)
        path = self._path(name, "csv")
        if path.stat().st_size > 4_000_000:
            raise HTTPException(status_code=422, detail="CSV troppo grande")
        try:
            with path.open(newline="", encoding="utf-8") as stream:
                samples = []
                for row in csv.DictReader(stream):
                    values = [float(row[key]) for key in ("timestamp_us", "ax_g", "ay_g", "az_g")]
                    if not all(math.isfinite(v) for v in values) or len(samples) >= 512:
                        raise ValueError("Campioni non validi")
                    samples.append([values[0] / 1000, *values[1:]])
            return {"name": name, "metadata": meta, "samples": samples}
        except (OSError, ValueError, KeyError, TypeError) as error:
            raise HTTPException(status_code=422, detail="CSV non leggibile") from error

    def download(self, name: str, extension: str):
        path = self._path(name, extension)
        return FileResponse(path, filename=path.name,
                            media_type="text/csv" if extension == "csv" else "application/json",
                            headers={"Cache-Control": "no-store"})
