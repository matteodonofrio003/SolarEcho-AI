"""Invii Telegram manuali: coda locale, rete nel worker, nessuna RPC ai sensori."""
import copy
from datetime import datetime, timezone
import importlib
import json
import logging
import math
import os
from pathlib import Path
from queue import Empty, Queue
import re
from threading import Event, RLock, Thread
import time


REQUEST_ID = re.compile(r"[0-9a-f]{32}")
RETRYABLE = {"FAILED", "UNCONFIRMED"}


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def number(value, digits=3):
    return f"{value:.{digits}f}" if isinstance(value, (int, float)) and math.isfinite(value) else "n/d"


def format_message(panel_id, snapshot, request_id="ANTEPRIMA"):
    """Testo semplice senza markup, dai soli dati raccolti localmente."""
    inspection = snapshot.get("inspection", {})
    alert = inspection.get("alert") or {}
    evidence = alert.get("evidence", {})
    reason = {"ELECTRICAL_DECLINE": "Calo elettrico persistente dopo impatti",
              "AI_ANOMALY": "Anomalia vibrazionale AI"}.get(alert.get("reason"), "Segnalazione manuale")
    power = snapshot.get("power", {})
    imu = snapshot.get("imu", {})
    lines = ["SolarEcho AI - Segnalazione pannello", f"ID: {request_id}",
             f"Pannello: {panel_id}", f"Dati raccolti: {snapshot.get('at_utc', 'n/d')}",
             f"Sessione: {snapshot.get('session_id', 'n/d')}",
             f"Stato monitoraggio: {snapshot.get('phase', 'n/d')}", f"Motivo: {reason}",
             f"Eta telemetria: {number(snapshot.get('telemetry_age_s'), 1)} s",
             f"Impatti totali: {number(snapshot.get('impacts'), 0)}",
             f"Impatti dal riferimento: {number(inspection.get('impacts_since_reference'), 0)}"]
    if power.get("valid"):
        lines += [f"Tensione: {number(power.get('voltage_v'))} V",
                  f"Corrente: {number(power.get('current_ma'), 2)} mA",
                  f"Potenza: {number(power.get('power_mw'))} mW",
                  f"Eta misura elettrica: {number(power.get('age_s'), 1)} s"]
    else:
        lines.append("Misure elettriche: non disponibili o non aggiornate")
    if imu.get("valid"):
        lines.append(f"Accelerazione X/Y/Z: {number(imu.get('ax_g'), 4)} / "
                     f"{number(imu.get('ay_g'), 4)} / {number(imu.get('az_g'), 4)} g (include gravita)")
    else:
        lines.append("Accelerazione: non disponibile o non aggiornata")
    economics = snapshot.get("economics", {})
    lines += [f"Potenza di riferimento: {number(economics.get('reference_mw'))} mW",
              f"Calo elettrico recente: {number(economics.get('live_reduction_pct'), 1)} %",
              "AI: " + ("inferenza disponibile" if inspection.get("ai_enabled") else "non attiva")]
    if alert:
        lines.append(f"Allerta registrata: {alert.get('at_utc', 'n/d')}")
    if alert.get("reason") == "ELECTRICAL_DECLINE":
        lines.append(f"Calo alla segnalazione: {number(evidence.get('drop_pct'), 1)} %")
    if alert.get("reason") == "AI_ANOMALY":
        lines.append(f"Score AI dell'allerta: {number(evidence.get('score'), 5)}; "
                     f"soglia: {number(evidence.get('threshold'), 5)}")
    if snapshot.get("last_event"):
        lines.append(f"Ultima acquisizione: {snapshot['last_event']}")
    scenario = economics.get("scenario")
    if scenario:
        lines.append(f"Scenario economico IPOTETICO: {number(scenario.get('total_eur'), 2)} EUR "
                     f"su {economics.get('scenario_days')} giorni, "
                     f"riduzione ipotizzata {number(scenario.get('reduction_pct'), 1)} %")
    if snapshot.get("error"):
        lines.append(f"Errore monitoraggio: {snapshot['error']}")
    lines += ["Ispezione consigliata se sono presenti anomalie. Nessuna diagnosi di danno certo.",
              "Ombra, luce e carico possono modificare la produzione."]
    return "\n".join(lines)


class SafeTelegramLog(logging.Handler):
    """Trasmette solo categorie note, mai URL, token o traceback della libreria."""
    def __init__(self, notice):
        super().__init__(logging.ERROR)
        self.notice = notice

    def emit(self, record):
        try:
            exception_name = record.exc_info[0].__name__.lower() if record.exc_info else ""
            message = exception_name + " " + record.getMessage().lower()
            if "webhook" in message:
                category = "Il bot ha un webhook attivo: la ricezione tramite polling non e disponibile."
            elif "conflict" in message or "terminated by other getupdates" in message:
                category = "Un altro processo usa lo stesso bot (Conflict). Ferma le altre App o istanze del bot, poi Riconnetti."
            elif "unauthorized" in message or "invalidtoken" in message or "invalid token" in message:
                category = "Token rifiutato da Telegram: controlla il token del brick e riavvia la App."
            else:
                category = "Errore nella ricezione Telegram. Controlla Internet sulla scheda e premi Riconnetti."
            self.notice("error", category)
        except Exception:
            pass  # Non lasciare che logging gestisca/mostri il record originale.


def create_bot(notice=None):
    """Chiamato SOLO dal worker dopo l'avvio di App.run, mai dai callback Bridge."""
    from arduino.app_utils import App
    from arduino.app_bricks.telegram_bot import TelegramBot

    if not callable(getattr(App, "unregister", None)):
        raise RuntimeError("Versione App Utils non compatibile")
    notice = notice or (lambda kind, value: None)
    # Evita i log HTTP con URL contenenti il token. Espone solo categorie note.
    for name in ("httpx", "httpcore", "telegram", "TelegramBot"):
        log = logging.getLogger(name)
        log.handlers = [logging.NullHandler()]
        log.propagate = False
    logging.getLogger("telegram").handlers = [SafeTelegramLog(notice)]
    # App Utils crea un Logger autonomo: getLogger() non recupera questo oggetto.
    module = importlib.import_module("arduino.app_bricks.telegram_bot.telegram_bot")
    module.logger.handlers = [SafeTelegramLog(notice)]
    module.logger.propagate = False
    bot = TelegramBot(message_timeout=8, max_retries=1, auto_set_commands=False)
    App.unregister(bot)  # Gestione manuale: start()/stop() possono attendere la rete.

    def show_chat_id(sender, message):
        # Questo comando non espone dati del pannello e non associa automaticamente utenti.
        notice("command", sender.chat_id)
        try:
            replied = sender.reply(f"SolarEcho AI\nIl tuo Chat ID: {sender.chat_id}\n"
                                   "Inseriscilo nella dashboard per ricevere le segnalazioni. "
                                   "Usa la chat privata con questo bot.")
        except Exception:
            replied = False
        notice("reply", bool(replied))

    bot.add_command("start", show_chat_id, "Mostra il Chat ID per la configurazione")
    return bot


class TelegramNotifications:
    def __init__(self, directory, bot_factory=create_bot):
        self.directory = Path(directory)
        self.lock = RLock()
        self.queue = Queue(maxsize=1)
        self.stopping = Event()
        self.worker = None
        self.bot_factory = bot_factory
        self.bot = None  # Usato soltanto dal worker.
        self.token_present = bool(os.getenv("TELEGRAM_BOT_TOKEN", "").strip())
        self.connection = "STARTING" if self.token_present else "DISABLED"
        self.error = None if self.token_present else "Configura TELEGRAM_BOT_TOKEN nel brick e riavvia la App."
        self.io_error = None
        self.bot_username = None
        self.last_command = None
        self.settings = {"panel_id": "SolarEcho-01", "chat_id": None}
        self.jobs = {}
        self.active_id = None
        self.last_accepted_at = 0.0
        try:
            config = self.directory / "settings.json"
            if config.exists():
                self.settings = self._validate_settings(json.loads(config.read_text(encoding="utf-8")))
            paths = sorted(self.directory.glob("notification_*.json"),
                           key=lambda p: p.stat().st_mtime)[-100:]
            for path in paths:
                job_id = path.stem.removeprefix("notification_")
                if not REQUEST_ID.fullmatch(job_id) or path.is_symlink() or path.stat().st_size > 64000:
                    continue
                job = json.loads(path.read_text(encoding="utf-8"))
                if not isinstance(job, dict) or job.get("id") != job_id:
                    continue
                if (job.get("state") not in {"QUEUED", "SENDING", "SENT", "FAILED", "UNCONFIRMED"}
                        or not isinstance(job.get("text"), str) or len(job["text"]) > 4000
                        or not isinstance(job.get("snapshot"), dict)
                        or type(job.get("attempts")) is not int or job["attempts"] < 0):
                    continue
                self._validate_settings({"panel_id": job.get("panel_id"), "chat_id": job.get("chat_id")})
                if job.get("state") in ("QUEUED", "SENDING"):
                    job.update(state="UNCONFIRMED", error="App riavviata: esito precedente non confermato. Verifica Telegram prima di riprovare.")
                    self._save_job(job)
                self.jobs[job_id] = job
        except (OSError, ValueError, TypeError, KeyError) as error:
            self.io_error = f"Archivio Telegram non caricato ({type(error).__name__})."

    @staticmethod
    def _validate_settings(settings):
        if not isinstance(settings, dict) or set(settings) != {"panel_id", "chat_id"}:
            raise ValueError("Servono identificativo del pannello e Chat ID")
        panel = settings["panel_id"]
        if not isinstance(panel, str) or not 1 <= len(panel.strip()) <= 64 or not panel.isprintable():
            raise ValueError("Identificativo pannello non valido (1-64 caratteri)")
        chat = settings["chat_id"]
        if isinstance(chat, str) and re.fullmatch(r"[1-9][0-9]{0,15}", chat.strip()):
            chat = int(chat.strip())
        if isinstance(chat, bool) or not isinstance(chat, int) or not 0 < chat < 2 ** 52:
            raise ValueError("Inserisci il Chat ID positivo della chat privata con il bot")
        return {"panel_id": panel.strip(), "chat_id": chat}

    def _write(self, path, value):
        self.directory.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(".tmp")
        with temporary.open("w", encoding="utf-8") as stream:
            json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)

    def _save_job(self, job):
        self._write(self.directory / f"notification_{job['id']}.json", job)

    def update_settings(self, settings):
        values = self._validate_settings(settings)
        with self.lock:
            if self.active_id:
                raise RuntimeError("Attendi l'esito dell'invio prima di cambiare il destinatario")
            self._write(self.directory / "settings.json", values)
            self.settings = values
            self.io_error = None
            return self.status()

    def start(self):
        """Invocare dal primo user_loop: nessuna inizializzazione di rete nel main."""
        with self.lock:
            if self.worker is not None or not self.token_present:
                return
            self.worker = Thread(target=self._run, name="SolarEchoTelegram", daemon=True)
            self.worker.start()

    def stop(self):
        self.stopping.set()  # Il worker chiude il bot; nessuna attesa di rete nel main.

    def reconnect(self):
        with self.lock:
            if not self.token_present:
                raise RuntimeError("Configura il token nel brick e riavvia la App")
            if self.active_id or self.connection in ("CONNECTING", "STARTING"):
                raise RuntimeError("Connessione o invio gia in corso")
            self.connection, self.error = "CONNECTING", None
            self.queue.put_nowait(("connect", None))
            return self.status()

    def preview(self, snapshot):
        with self.lock:
            return {"text": format_message(self.settings["panel_id"], snapshot)}

    def submit(self, request_id, snapshot):
        if not isinstance(request_id, str) or not REQUEST_ID.fullmatch(request_id):
            raise ValueError("Identificativo richiesta non valido")
        with self.lock:
            if request_id in self.jobs:
                return self.status()  # Stesso clic/ritentativo HTTP: nessun secondo invio.
            path = self.directory / f"notification_{request_id}.json"
            if path.exists():
                raise RuntimeError("Richiesta gia archiviata: consulta lo storico locale")
            self._check_ready()
            if time.monotonic() - self.last_accepted_at < 3:
                raise RuntimeError("Attendi tre secondi prima di una nuova segnalazione")
            job = {"id": request_id, "at_utc": utc_now(), "state": "QUEUED", "error": None,
                   "attempts": 0, "panel_id": self.settings["panel_id"],
                   "chat_id": self.settings["chat_id"], "snapshot": copy.deepcopy(snapshot)}
            job["text"] = format_message(job["panel_id"], job["snapshot"], request_id)
            if len(job["text"]) > 4000:
                raise ValueError("Segnalazione troppo lunga")
            self._save_job(job)  # Se fallisce non parte alcun invio.
            self.jobs[request_id] = job
            self.active_id = request_id
            self.last_accepted_at = time.monotonic()
            self.queue.put_nowait(("send", request_id))
            return self.status()

    def _check_ready(self):
        if not self.settings["chat_id"]:
            raise RuntimeError("Salva prima il Chat ID del destinatario")
        if self.connection != "READY":
            raise RuntimeError("Telegram non connesso: controlla token/rete e premi Riconnetti")
        if self.active_id:
            raise RuntimeError("Una segnalazione e gia in corso")

    def retry(self, request_id):
        with self.lock:
            self._check_ready()
            job = self.jobs.get(request_id)
            if not job or job.get("state") not in RETRYABLE:
                raise ValueError("Segnalazione non ripetibile")
            if job["chat_id"] != self.settings["chat_id"]:
                raise RuntimeError("Il destinatario e cambiato: crea una nuova segnalazione")
            updated = dict(job, state="QUEUED", error=None)
            self._save_job(updated)
            self.jobs[request_id] = updated
            self.active_id = request_id
            self.queue.put_nowait(("send", request_id))
            return self.status()

    def _close_bot(self):
        if self.bot is not None:
            try:
                self.bot.stop()
            except Exception:
                pass  # Non pubblicare eccezioni della libreria che potrebbero includere il token.
            self.bot = None

    def _notice(self, kind, value):
        with self.lock:
            if kind == "command":
                self.last_command = {"at_utc": utc_now(), "chat_id": value, "reply_ok": None}
                print(f"TELEGRAM: /start ricevuto; Chat ID: {value}")
            elif kind == "reply" and self.last_command:
                self.last_command["reply_ok"] = value
                print("TELEGRAM: risposta /start " + ("inviata." if value else "non confermata; Chat ID disponibile nella dashboard."))
            elif kind == "error":
                self.connection, self.error = "ERROR", value
                print(f"TELEGRAM: {value}")

    def _connect(self):
        self._close_bot()
        with self.lock:
            self.connection, self.error = "CONNECTING", None
            self.bot_username = None
        stage = "creazione brick"
        try:
            self.bot = create_bot(self._notice) if self.bot_factory is create_bot else self.bot_factory()
            stage = "avvio bot"
            self.bot.start()
            api_bot = getattr(getattr(self.bot, "application", None), "bot", None)
            username = getattr(api_bot, "username", None)
            with self.lock:
                self.bot_username = username if isinstance(username, str) and re.fullmatch(r"[A-Za-z0-9_]{5,32}", username) else None
                if not self.error:
                    self.connection = "READY"
                print("TELEGRAM: bot avviato" + (f" @{self.bot_username}" if self.bot_username else "") + "; invia /start nella sua chat privata.")
        except Exception as error:
            self._close_bot()
            with self.lock:
                self.connection = "ERROR"
                self.error = self.error or f"Errore durante {stage} ({type(error).__name__}): controlla token, rete e brick; poi Riconnetti."
                print(f"TELEGRAM: {self.error}")

    def _send(self, job_id):
        with self.lock:
            job = self.jobs[job_id]
            job.update(state="SENDING", attempts=job["attempts"] + 1,
                       attempted_at_utc=utc_now(), error=None)
            try:
                self._save_job(job)
            except OSError:
                job.update(state="FAILED", error="Archivio non scrivibile: invio non eseguito.")
                self.io_error = job["error"]
                self.active_id = None
                return
        try:
            sent = self.bot is not None and self.bot.send_message(job["chat_id"], job["text"])
        except Exception:
            sent = False
        with self.lock:
            job.update(state="SENT" if sent else "UNCONFIRMED", finished_at_utc=utc_now(),
                       error=None if sent else "Esito non confermato. Verifica la chat prima di riprovare: un duplicato e possibile.")
            try:
                self._save_job(job)
                self.io_error = None
            except OSError:
                self.io_error = "Esito presente in RAM ma non salvato; verifica Telegram prima di riavviare."
            self.active_id = None
            if not sent:
                self.connection, self.error = "ERROR", job["error"]

    def _run(self):
        try:
            self._connect()
            while not self.stopping.is_set():
                try:
                    kind, job_id = self.queue.get(timeout=0.2)
                except Empty:
                    continue
                if self.stopping.is_set():
                    break
                try:
                    if kind == "connect":
                        self._connect()
                    else:
                        self._send(job_id)
                except Exception:
                    # Mantiene disponibile Riconnetti anche dopo un errore inatteso.
                    with self.lock:
                        self.connection = "ERROR"
                        self.error = "Errore Telegram: verifica la chat prima di riconnettere e riprovare."
                        if self.active_id in self.jobs:
                            job = self.jobs[self.active_id]
                            job.update(state="UNCONFIRMED", error=self.error)
                            try:
                                self._save_job(job)
                            except Exception:
                                self.io_error = "Esito non salvato; controlla la chat."
                        self.active_id = None
        finally:
            self._close_bot()

    def status(self):
        with self.lock:
            summaries = [{key: job.get(key) for key in ("id", "at_utc", "state", "error", "attempts", "panel_id", "chat_id")}
                         for job in list(self.jobs.values())[-10:]][::-1]
            return {"connection": self.connection, "error": self.error, "io_error": self.io_error,
                    "bot_username": self.bot_username, "last_command": copy.deepcopy(self.last_command),
                    "settings": dict(self.settings), "token_present": self.token_present,
                    "busy": self.active_id is not None, "jobs": summaries,
                    "cooldown_s": max(0, 3 - (time.monotonic() - self.last_accepted_at))}

    def report(self, request_id):
        with self.lock:
            if not isinstance(request_id, str) or not REQUEST_ID.fullmatch(request_id) or request_id not in self.jobs:
                raise ValueError("Segnalazione non trovata")
            return copy.deepcopy(self.jobs[request_id])
