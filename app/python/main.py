"""Cattura per impatto: pretrigger IMU, CSV e controllo della qualita' locale."""
from arduino.app_utils import App, Bridge
from dashboard import Dashboard
from power_history import PowerHistory
from electrical_demo import ElectricalDemo
from inspection_alert import InspectionAlert
from telegram_notifications import TelegramNotifications
from vibration_ai import VibrationAI
from event_logger import EventLogger

from datetime import datetime
from pathlib import Path
import time
from uuid import uuid4


# App Lab conserva i dati persistenti nella cartella data/ della App.
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
armed = False
next_arm_at = time.monotonic() + 1.0
session_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:8]}"
power_history = PowerHistory(OUTPUT_DIR.parent / "power", session_id)
electrical_demo = ElectricalDemo(OUTPUT_DIR.parent / "analysis", power_history)
inspection = InspectionAlert(OUTPUT_DIR.parent / "analysis")
notifications = TelegramNotifications(OUTPUT_DIR.parent / "notifications")
vibration_ai = VibrationAI(OUTPUT_DIR.parent / "ai", inspection)
dashboard = Dashboard(OUTPUT_DIR, session_id, power_history, electrical_demo, inspection, notifications, vibration_ai)
next_led_sync_at = 0.0


def capture_saved(path):
    dashboard.saved(path)
    try:
        vibration_ai.submit(path)
    except RuntimeError as error:
        print(f"AI: evento non accodato ({error}); CSV conservato.")


logger = EventLogger(OUTPUT_DIR, session_id,
                     lambda capture_id: Bridge.call("solarecho_ack", capture_id),
                     on_saved=capture_saved, on_error=dashboard.fail)


def on_ready(previous_capture_id):
    dashboard.set_phase("READY")
    logger.on_ready(previous_capture_id)


def on_begin(capture_id, count, pre_count, pre_us, post_us, trigger_adc, event_count):
    dashboard.set_phase("TRANSFER")
    logger.on_begin(capture_id, count, pre_count, pre_us, post_us, trigger_adc, event_count)


def on_sample(capture_id, index, timestamp_us, ax_g, ay_g, az_g,
              piezo_state, piezo_threshold_crossings, piezo_event_count,
              piezo_adc, piezo_peak_adc, piezo_timestamp_us, piezo_max_gap_us):
    logger.on_sample(capture_id, index, timestamp_us, ax_g, ay_g, az_g,
                     piezo_state, piezo_threshold_crossings, piezo_event_count,
                     piezo_adc, piezo_peak_adc, piezo_timestamp_us, piezo_max_gap_us)


def on_end(capture_id, count, overflow, additional_events):
    logger.on_end(capture_id, count, overflow, additional_events)


Bridge.provide("solarecho_begin", on_begin)
Bridge.provide("solarecho_sample", on_sample)
Bridge.provide("solarecho_end", on_end)
Bridge.provide("solarecho_ready", on_ready)
Bridge.provide("solarecho_live", dashboard.telemetry)
print("Acquisizione automatica: attendere READY prima di ogni impatto.")
print("Dashboard Web UI: http://<IP-della-UNO-Q>:7000")
print(f"Storico elettrico automatico: {power_history.path}")


def loop():
    global armed, next_arm_at, next_led_sync_at
    notifications.start()  # Thread avviato dopo App.run; inizializzazione rete fuori dal main.
    vibration_ai.start()

    if not armed and not logger.halted and time.monotonic() >= next_arm_at:
        next_arm_at = time.monotonic() + 1.0
        try:
            result = Bridge.call("solarecho_arm")
            if result == 1:
                armed = True
            elif result == -1:
                logger.halted = True
                dashboard.fail("Modulino non inizializzato. Controllare Qwiic e riavviare.")
                print("SENSOR ERROR: Modulino non inizializzato. Controllare Qwiic e riavviare.")
        except Exception as error:
            print(f"Attesa firmware Bridge: {error}")

    logger.process()

    for row in power_history.flush():
        electrical_demo.observe_row(row)
        inspection.observe_row(row, electrical_demo.status())
    electrical_demo.tick()
    if armed and not logger.halted and logger.pending is None and time.monotonic() >= next_led_sync_at:
        desired_led = dashboard.led_request()
        if desired_led is not None:
            next_led_sync_at = time.monotonic() + 2.0
            try:
                result = Bridge.call("solarecho_inspection_led", desired_led, timeout=1.0)
                if result != 1:
                    print("LED: richiesta rifiutata; controllare firmware e telemetria.")
            except Exception as error:
                print(f"LED: sincronizzazione non riuscita; nuovo tentativo alla ripresa: {error}")
    time.sleep(0.05)


try:
    App.run(user_loop=loop)
finally:
    vibration_ai.stop()
    notifications.stop()
