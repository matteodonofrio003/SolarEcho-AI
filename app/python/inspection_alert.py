"""Richiesta di ispezione: calo elettrico dopo impatti oppure anomalia AI valida."""
from collections import OrderedDict
import copy
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
from threading import RLock


DEFAULT_SETTINGS = {"min_impacts": 3, "drop_pct": 20.0, "consecutive_samples": 5}


class InspectionAlert:
    def __init__(self, directory):
        self.path = Path(directory) / "inspection_alert.json"
        self.lock = RLock()
        self.settings = dict(DEFAULT_SETTINGS)
        self.alert = None
        self.io_error = None
        self.ai_enabled = False
        self.reference_id = None
        self.blocked_reference_id = None
        self.reference_events = None
        self.events = None
        self.last_uptime = None
        self.streak = 0
        self.previous_stamp = None
        self.last_drop = None
        self.contexts = OrderedDict()
        try:
            if self.path.exists():
                saved = json.loads(self.path.read_text(encoding="utf-8"))
                settings = self._validate(saved["settings"])
                alert = saved.get("alert")
                if alert is not None and (not isinstance(alert, dict)
                        or alert.get("reason") not in ("ELECTRICAL_DECLINE", "AI_ANOMALY")
                        or not isinstance(alert.get("at_utc"), str)
                        or not isinstance(alert.get("evidence"), dict)):
                    raise ValueError("Allerta salvata non valida")
                self.settings, self.alert = settings, alert
        except (OSError, ValueError, KeyError, TypeError) as error:
            self.io_error = f"Stato LED non caricato: {error}"

    @staticmethod
    def _validate(settings):
        if not isinstance(settings, dict) or set(settings) != set(DEFAULT_SETTINGS):
            raise ValueError("Servono numero impatti, percentuale di calo e letture consecutive")
        result = {}
        for key, limits in {"min_impacts": (1, 1000), "drop_pct": (1, 100),
                            "consecutive_samples": (2, 120)}.items():
            value = settings[key]
            if (isinstance(value, bool) or not isinstance(value, (float, int))
                    or not math.isfinite(value) or not limits[0] <= value <= limits[1]
                    or (key != "drop_pct" and int(value) != value)):
                raise ValueError(f"Valore non valido: {key}")
            result[key] = float(value) if key == "drop_pct" else int(value)
        return result

    def _save(self, settings, alert):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".tmp")
        with temporary.open("w", encoding="utf-8") as stream:
            json.dump({"settings": settings, "alert": alert}, stream,
                      ensure_ascii=False, indent=2, allow_nan=False)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, self.path)

    def update_settings(self, settings):
        values = self._validate(settings)
        with self.lock:
            self._save(values, self.alert)
            self.settings = values
            self.streak = 0
            self.previous_stamp = None
            self.io_error = None
            return self.status()

    def reset(self):
        """Il reset conferma l'allerta; se la condizione persiste potra riaccendersi."""
        with self.lock:
            self._save(self.settings, None)  # Non spegnere se il reset non e persistibile.
            self.alert = None
            self.streak = 0
            self.previous_stamp = None
            self.io_error = None
            return self.status()

    def _latch(self, reason, evidence):
        if self.alert is not None:
            return  # Conserva il motivo originale fino alla conferma dell'operatore.
        self.alert = {"reason": reason,
                      "at_utc": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
                      "evidence": evidence}
        try:
            self._save(self.settings, self.alert)
            self.io_error = None
        except OSError as error:
            # Segnalazione attiva in RAM anche se lo storico non puo essere scritto.
            self.io_error = f"Allerta attiva ma non salvata: {error}"

    def telemetry(self, data):
        """Callback senza disco/RPC; associa ogni misura al suo contatore di impatti."""
        with self.lock:
            events = int(data["events"])
            uptime = int(data["t_ms"])
            reboot = (self.events is not None and events < self.events) or (
                self.last_uptime is not None
                and (uptime - self.last_uptime) % (2 ** 32) > 2 ** 31)
            if reboot:
                self.blocked_reference_id = self.reference_id
                self.reference_events = None
                self.contexts.clear()
            if events != self.events or not data["power_ok"]:
                self.streak = 0
                self.previous_stamp = None
            self.events, self.last_uptime = events, uptime
            stamp = int(data["power_t_ms"])
            if data["power_ok"] and data["power_error"] == 1 and stamp not in self.contexts:
                self.contexts[stamp] = events
            while len(self.contexts) > 256:
                self.contexts.popitem(last=False)

    def observe_row(self, row, reference):
        """Solo misure effettivamente salvate. Le pause azzerano la consecutivita."""
        with self.lock:
            stamp, power_w = int(row[3]), row[10]
            events = self.contexts.pop(stamp, None)
            reference_id = reference.get("reference_id")
            if reference_id != self.reference_id:
                self.reference_id = reference_id
                self.reference_events = events if reference_id else None
                self.streak = 0
                self.previous_stamp = None
                self.last_drop = None
                return  # La misura che completa il riferimento non e una prova nuova.
            baseline = reference.get("reference_w")
            if (not reference_id or reference_id == self.blocked_reference_id
                    or self.reference_events is None or events is None
                    or events - self.reference_events < self.settings["min_impacts"]
                    or not baseline or power_w < 0
                    or (self.last_uptime - stamp) % (2 ** 32) > 3000):
                self.streak = 0
                self.previous_stamp = None
                self.last_drop = None
                return
            gap = None if self.previous_stamp is None else (stamp - self.previous_stamp) % (2 ** 32) / 1000
            if gap is not None and not 0 < gap <= 2.5:
                self.streak = 0
            self.previous_stamp = stamp
            self.last_drop = 100 * (1 - power_w / baseline)
            cutoff_w = baseline * (1 - self.settings["drop_pct"] / 100)
            self.streak = self.streak + 1 if power_w <= cutoff_w else 0
            if self.streak >= self.settings["consecutive_samples"]:
                self._latch("ELECTRICAL_DECLINE", {
                    "reference_id": reference_id, "reference_w": baseline,
                    "power_w": power_w, "drop_pct": self.last_drop,
                    "impacts_since_reference": events - self.reference_events,
                    "consecutive_samples": self.streak, "settings": dict(self.settings),
                    "power_session_id": row[0], "measurement_timestamp_ms": stamp,
                })

    def on_ai_result(self, score, threshold, event_name, *, comparable):
        """Hook per un'inferenza reale futura; non addestra e non simula un modello."""
        if not isinstance(comparable, bool) or not isinstance(event_name, str):
            raise ValueError("Indicare evento e confrontabilita della cattura")
        if any(isinstance(v, bool) or not isinstance(v, (int, float))
               or not math.isfinite(v) or v < 0 for v in (score, threshold)):
            raise ValueError("Score e soglia AI devono essere numerici, finiti e non negativi")
        with self.lock:
            self.ai_enabled = True
            if comparable and score > threshold:
                self._latch("AI_ANOMALY", {"event": event_name, "score": score,
                                          "threshold": threshold})

    def desired_led(self):
        with self.lock:
            return int(self.alert is not None)

    def status(self):
        with self.lock:
            count = None if self.reference_events is None else max(0, (self.events or 0) - self.reference_events)
            available = bool(self.reference_id and self.reference_events is not None
                             and self.reference_id != self.blocked_reference_id)
            return {"active": self.alert is not None, "alert": copy.deepcopy(self.alert),
                    "settings": dict(self.settings), "impacts_since_reference": count,
                    "reference_available": available, "consecutive_low_samples": self.streak,
                    "last_drop_pct": self.last_drop, "ai_enabled": self.ai_enabled,
                    "io_error": self.io_error}
