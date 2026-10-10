"""Confronto elettrico controllato e scenario economico esplicitamente ipotetico."""
from collections import deque
import copy
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import statistics
from threading import RLock
import time
from uuid import uuid4


REFERENCE_SAMPLES = 10
REFERENCE_TIMEOUT_S = 25
MAX_GAP_S = 2.5
MIN_REFERENCE_W = 0.0001  # Gate diagnostico iniziale (0,1 mW), non accuratezza del sensore.
MAX_REFERENCE_CV = 0.20
DEFAULT_SETTINGS = {
    "daily_kwh": 12.0, "days": 30, "self_consumption_pct": 50.0,
    "buy_eur_kwh": 0.30, "sell_eur_kwh": 0.08,
    "reduction_mode": "measured", "assumed_reduction_pct": 20.0,
}


class ElectricalDemo:
    def __init__(self, directory, power_history):
        self.directory = Path(directory)
        self.history = power_history
        self.lock = RLock()
        self.settings = dict(DEFAULT_SETTINGS)
        self.settings_error = None
        self.phase = "NO_REFERENCE"
        self.message = "Illumina il pannello e acquisisci un riferimento elettrico."
        self.baseline = None
        self.reference_rows = []
        self.reference_start = None
        self.latest = None
        self.recent = deque(maxlen=5)
        self.comparison = None
        self.previous = None
        self.last_report = None
        self.io_error = None
        try:
            path = self.directory / "economics_settings.json"
            if path.exists():
                with path.open(encoding="utf-8") as stream:
                    self.settings = self._validate_settings(json.load(stream))
        except (OSError, ValueError, TypeError) as error:
            self.settings_error = f"Configurazione non caricata: {error}. Sono attivi valori dimostrativi."

    def _now(self):
        return time.monotonic() - self.history.started_at

    @staticmethod
    def _utc():
        return datetime.now(timezone.utc).isoformat(timespec="milliseconds")

    def _write_json(self, filename, data):
        """Sostituzione atomica: un riavvio non lascia un JSON scritto a meta'."""
        self.directory.mkdir(parents=True, exist_ok=True)
        destination = self.directory / filename
        temporary = destination.with_suffix(".tmp")
        with temporary.open("w", encoding="utf-8") as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)

    @staticmethod
    def _validate_settings(settings):
        if not isinstance(settings, dict) or set(settings) != set(DEFAULT_SETTINGS):
            raise ValueError("Parametri economici incompleti o sconosciuti")
        ranges = {"daily_kwh": (0.001, 100000), "days": (1, 3650),
                  "self_consumption_pct": (0, 100), "buy_eur_kwh": (0, 10),
                  "sell_eur_kwh": (0, 10), "assumed_reduction_pct": (0, 100)}
        result = {}
        for key, (minimum, maximum) in ranges.items():
            value = settings[key]
            if (isinstance(value, bool) or not isinstance(value, (int, float))
                    or not math.isfinite(value) or not minimum <= value <= maximum):
                raise ValueError(f"Valore non valido: {key}")
            if key == "days" and int(value) != value:
                raise ValueError("La durata deve essere un numero intero di giorni")
            result[key] = int(value) if key == "days" else float(value)
        if settings["reduction_mode"] not in ("measured", "manual"):
            raise ValueError("Modalita riduzione non valida")
        result["reduction_mode"] = settings["reduction_mode"]
        return result

    def update_settings(self, settings):
        values = self._validate_settings(settings)
        with self.lock:
            self._write_json("economics_settings.json", values)
            self.settings = values
            self.settings_error = None
            return self.status()

    def _current(self):
        if self.latest is None or self._now() - self.latest[2] > 3:
            return None
        if self.latest[10] < 0:
            return None
        rows = [r for r in self.recent if self._now() - r[2] <= 6 and r[10] >= 0]
        return statistics.mean(r[10] for r in rows) if rows else None

    def start_reference(self):
        with self.lock:
            if self.phase == "COLLECTING" or (self.comparison and self.comparison["running"]):
                raise RuntimeError("Termina il confronto prima di acquisire un nuovo riferimento")
            self.phase = "COLLECTING"
            self.reference_start = self._now()
            self.reference_rows = []
            self.baseline = None
            self.comparison = None
            self.previous = None
            self.last_report = None
            self.message = "Mantieni luce, posizione e carico invariati; servono 10 nuove letture consecutive."
            self.io_error = None
            return self.status()

    def tick(self):
        with self.lock:
            if self.phase == "COLLECTING" and self._now() - self.reference_start > REFERENCE_TIMEOUT_S:
                self.phase = "REFERENCE_ERROR"
                self.message = "Riferimento incompleto: attendi letture regolari e ripeti senza impatti."

    def observe_row(self, row):
        """Usa solo righe confermate dal logger; nessun calcolo economico nel callback Bridge."""
        with self.lock:
            if self.latest is not None:
                gap = (row[3] - self.latest[3]) % (2 ** 32) / 1000
                if gap <= 0 or gap > MAX_GAP_S:
                    self.recent.clear()
            self.latest = row
            self.recent.append(row)
            if self.phase == "COLLECTING" and row[2] >= self.reference_start:
                self._collect_reference(row)
            if self.comparison and self.comparison["running"] and row[2] >= self.comparison["start_elapsed_s"]:
                self._integrate(row)
                # Checkpoint per diagnosi; lo stato non viene ripristinato automaticamente dopo Run.
                if self.comparison["samples"] % 5 == 0:
                    try:
                        self._write_json(f"{self.comparison['id']}.json", self._report())
                    except OSError as error:
                        self.io_error = f"Report non salvato: {error}"

    def _collect_reference(self, row):
        if row[10] < 0:
            self.phase = "REFERENCE_ERROR"
            self.message = "Corrente/potenza inversa: controlla verso della misura e luce prima del riferimento."
            return
        if self.reference_rows:
            gap = (row[3] - self.reference_rows[-1][3]) % (2 ** 32) / 1000
            if gap <= 0 or gap > MAX_GAP_S:
                self.reference_rows = []
        self.reference_rows.append(row)
        if len(self.reference_rows) < REFERENCE_SAMPLES:
            return
        powers = [r[10] for r in self.reference_rows]
        mean_w = statistics.mean(powers)
        std_w = statistics.stdev(powers)
        if mean_w <= MIN_REFERENCE_W or std_w / mean_w > MAX_REFERENCE_CV:
            self.phase = "REFERENCE_ERROR"
            self.message = "Potenza troppo bassa o instabile. Aumenta/stabilizza la luce e ripeti il riferimento."
            return
        baseline = {
            "id": f"reference_{self.history.session_id}_{uuid4().hex[:8]}",
            "mean_w": mean_w, "std_w": std_w, "cv": std_w / mean_w,
            "sample_count": len(powers), "captured_at_utc": self._utc(),
            "power_csv": self.history.path.name,
            "samples": [{"received_at_utc": r[1], "elapsed_s": r[2],
                         "measurement_timestamp_ms": r[3], "power_w": r[10]}
                        for r in self.reference_rows],
        }
        try:
            self._write_json(f"{baseline['id']}.json", baseline)
        except OSError as error:
            self.phase = "REFERENCE_ERROR"
            self.io_error = f"Riferimento non salvato: {error}"
            return
        self.baseline = baseline
        self.phase = "REFERENCE_READY"
        self.message = "Riferimento pronto. Avvia il confronto prima di oscurare il pannello."
        self.io_error = None

    def start_comparison(self):
        with self.lock:
            if self.phase != "REFERENCE_READY" or self.baseline is None or self._current() is None:
                raise RuntimeError("Acquisisci un riferimento valido e attendi una misura elettrica recente")
            if self.comparison and self.comparison["running"]:
                raise RuntimeError("Confronto gia in corso")
            comparison = {
                "id": f"demo_{self.history.session_id}_{uuid4().hex[:8]}", "running": True,
                "started_at_utc": self._utc(), "start_elapsed_s": self._now(),
                "ended_at_utc": None, "end_elapsed_s": None,
                "samples": 0, "covered_s": 0.0, "measured_wh": 0.0,
                "reference_wh": 0.0, "excluded_intervals": 0,
                "reverse_power_samples": 0,
            }
            # Verifica prima la persistenza; il nuovo confronto e attivo solo dopo il salvataggio.
            self._write_json(f"{comparison['id']}.json", {"comparison": comparison,
                             "baseline": self.baseline, "settings": self.settings,
                             "power_csv": self.history.path.name})
            self.comparison = comparison
            self.previous = None
            self.last_report = None
            self.io_error = None
            self.message = "Confronto attivo. L'oscuramento simula una riduzione di produzione."
            return self.status()

    def _integrate(self, row):
        trial = self.comparison
        trial["samples"] += 1
        # Flussi inversi conservati nel CSV grezzo, esclusi dalla stima della produzione.
        if row[10] < 0:
            trial["reverse_power_samples"] += 1
            trial["excluded_intervals"] += 1
            self.previous = None
            return
        if self.previous is not None:
            dt = (row[3] - self.previous[3]) % (2 ** 32) / 1000
            if 0 < dt <= MAX_GAP_S:
                trial["covered_s"] += dt
                trial["measured_wh"] += (self.previous[10] + row[10]) * 0.5 * dt / 3600
                trial["reference_wh"] += self.baseline["mean_w"] * dt / 3600
            else:
                trial["excluded_intervals"] += 1
        self.previous = row

    def finish_comparison(self):
        with self.lock:
            if not self.comparison or not self.comparison["running"]:
                raise RuntimeError("Nessun confronto attivo")
            self.comparison["running"] = False
            self.comparison["ended_at_utc"] = self._utc()
            self.comparison["end_elapsed_s"] = self._now()
            self.message = "Confronto terminato. Puoi scaricare il report o avviare una nuova prova."
            report = self._report()
            self.last_report = report
            try:
                self._write_json(f"{self.comparison['id']}.json", report)
            except OSError as error:
                self.io_error = f"Report finale non salvato: {error}"
                return self.status()  # Il report resta scaricabile dalla RAM fino a Stop/Run.
            self.io_error = None
            return self.status()

    def _scenario(self, measured_reduction_pct):
        s = self.settings
        reduction = s["assumed_reduction_pct"] if s["reduction_mode"] == "manual" else measured_reduction_pct
        if reduction is None:
            return None
        reduction = min(100.0, max(0.0, reduction))
        lost_kwh = s["daily_kwh"] * s["days"] * reduction / 100
        share = s["self_consumption_pct"] / 100
        return {"reduction_pct": reduction, "lost_kwh": lost_kwh,
                "self_consumption_cost_eur": lost_kwh * share * s["buy_eur_kwh"],
                "export_revenue_lost_eur": lost_kwh * (1 - share) * s["sell_eur_kwh"],
                "total_eur": lost_kwh * (share * s["buy_eur_kwh"] + (1 - share) * s["sell_eur_kwh"]),
                "hypothetical": True}

    def _report(self):
        trial = copy.deepcopy(self.comparison)
        baseline = copy.deepcopy(self.baseline)
        deficit = max(0.0, trial["reference_wh"] - trial["measured_wh"])
        period_reduction = (100 * (trial["reference_wh"] - trial["measured_wh"])
                            / trial["reference_wh"]) if trial["reference_wh"] > 0 else None
        end = trial["end_elapsed_s"] if not trial["running"] else self._now()
        trial["wall_duration_s"] = max(0.0, end - trial["start_elapsed_s"])
        share = self.settings["self_consumption_pct"] / 100
        unit_value = share * self.settings["buy_eur_kwh"] + (1 - share) * self.settings["sell_eur_kwh"]
        return {"schema_version": 1, "saved_at_utc": self._utc(), "power_csv": self.history.path.name,
                "baseline": baseline, "comparison": trial, "settings": dict(self.settings),
                "net_deficit_wh": deficit, "period_reduction_pct": period_reduction,
                "net_deficit_value_eur": deficit / 1000 * unit_value if trial["covered_s"] > 0 else None,
                "scenario": self._scenario(period_reduction),
                "assumptions": ["Confronto elettrico controllato con riferimento di potenza costante",
                                "Illuminazione, posizione e carico devono restare comparabili",
                                "Intervalli oltre 2,5 s e potenza negativa esclusi dall'integrazione",
                                "Scenario domestico ipotetico; percentuale applicata per ipotesi",
                                "Tariffe inserite dall'utente, senza quote fisse o costi di riparazione",
                                "Nessuna attribuzione causale a impatti, grandine o danni strutturali"]}

    def report(self):
        with self.lock:
            if self.last_report is None:
                raise RuntimeError("Termina un confronto e salva il report prima del download")
            return copy.deepcopy(self.last_report)

    def status(self):
        with self.lock:
            current = self._current()
            baseline_w = self.baseline["mean_w"] if self.baseline else None
            reduction = (100 * (1 - current / baseline_w)) if current is not None and baseline_w else None
            comparison = copy.deepcopy(self.comparison)
            if comparison:
                end = comparison["end_elapsed_s"] if not comparison["running"] else self._now()
                comparison["wall_duration_s"] = max(0.0, end - comparison["start_elapsed_s"])
                comparison["net_deficit_wh"] = max(0.0, comparison["reference_wh"] - comparison["measured_wh"])
                comparison["period_reduction_pct"] = (100 * (1 - comparison["measured_wh"] / comparison["reference_wh"])) if comparison["reference_wh"] > 0 else None
                share = self.settings["self_consumption_pct"] / 100
                unit_value = share * self.settings["buy_eur_kwh"] + (1 - share) * self.settings["sell_eur_kwh"]
                comparison["deficit_value_eur"] = comparison["net_deficit_wh"] / 1000 * unit_value if comparison["covered_s"] > 0 else None
            health = "OK" if current is not None else "NO_RECENT_POWER"
            if self.latest and self._now() - self.latest[2] <= 3 and self.latest[10] < 0:
                health = "REVERSE_POWER"
            # Scenario misurato: riduzione energetica sul periodo del confronto, non un picco live.
            period_reduction = comparison["period_reduction_pct"] if comparison else None
            return {"phase": self.phase, "message": self.message, "health": health,
                    "reference_progress": len(self.reference_rows), "reference_target": REFERENCE_SAMPLES,
                    "reference_w": baseline_w, "current_w": current,
                    "reference_id": self.baseline["id"] if self.baseline else None,
                    "live_reduction_pct": reduction, "comparison": comparison,
                    "scenario": self._scenario(period_reduction), "settings": dict(self.settings),
                    "settings_error": self.settings_error, "io_error": self.io_error,
                    "report_available": self.last_report is not None}
