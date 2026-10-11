"""Test SINTETICI con bot fittizio: nessuna rete, token reale o prova sul pannello."""
from pathlib import Path
import logging
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app" / "python"))
from telegram_notifications import SafeTelegramLog, TelegramNotifications, format_message


class FakeBot:
    def __init__(self, accepted=True):
        self.accepted = accepted
        self.calls = []

    def send_message(self, chat_id, text):
        self.calls.append((chat_id, text))
        return self.accepted


class TelegramNotificationTests(unittest.TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        environment = patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": ""})
        environment.start()
        self.addCleanup(environment.stop)
        self.bot = FakeBot()
        self.service = TelegramNotifications(self.directory.name)
        self.service.update_settings({"panel_id": "SYNTHETIC-PANEL", "chat_id": "123456"})
        # Non avviamo thread: il gateway e la sua chiamata vengono controllati dal test.
        self.service.connection = "READY"
        self.service.bot = self.bot
        self.service.last_accepted_at = -10
        self.request_id = "a" * 32
        self.snapshot = {"at_utc": "2026-10-10T10:00:00+00:00", "session_id": "synthetic",
                         "phase": "READY", "impacts": 7, "telemetry_age_s": 0.5,
                         "power": {"valid": True, "voltage_v": 1.0,
                                   "current_ma": 2.0, "power_mw": 2.0, "age_s": 0.5},
                         "inspection": {"ai_enabled": False}, "imu": {"valid": False}}

    def take_and_send(self):
        kind, job_id = self.service.queue.get_nowait()
        self.assertEqual(kind, "send")
        self.service._send(job_id)

    def test_duplicate_http_request_sends_only_once_and_report_survives_restart(self):
        self.service.submit(self.request_id, self.snapshot)
        self.snapshot["impacts"] = 99
        self.service.submit(self.request_id, self.snapshot)
        self.assertEqual(self.service.queue.qsize(), 1)
        self.assertEqual(self.bot.calls, [])
        self.take_and_send()
        self.assertEqual(len(self.bot.calls), 1)
        self.assertIn("Impatti totali: 7", self.bot.calls[0][1])
        restored = TelegramNotifications(self.directory.name)
        self.assertEqual(restored.report(self.request_id)["state"], "SENT")
        self.assertTrue(restored.queue.empty())

    def test_uncertain_delivery_requires_explicit_retry_and_preserves_payload(self):
        self.bot.accepted = False
        self.service.submit(self.request_id, self.snapshot)
        self.take_and_send()
        original = self.bot.calls[0]
        self.assertEqual(self.service.report(self.request_id)["state"], "UNCONFIRMED")
        self.assertTrue(self.service.queue.empty())
        with self.assertRaises(RuntimeError):
            self.service.retry(self.request_id)  # Prima va riconnesso il bot.
        self.service.connection = "READY"
        self.bot.accepted = True
        self.service.retry(self.request_id)
        self.take_and_send()
        self.assertEqual(self.bot.calls[1], original)
        self.assertEqual(self.service.report(self.request_id)["attempts"], 2)

    def test_restart_never_automatically_sends_pending_request(self):
        self.service.submit(self.request_id, self.snapshot)
        restored = TelegramNotifications(self.directory.name)
        self.assertEqual(restored.report(self.request_id)["state"], "UNCONFIRMED")
        self.assertTrue(restored.queue.empty())
        self.assertEqual(self.bot.calls, [])

    def test_disk_failure_prevents_enqueue_and_network_call(self):
        with patch.object(self.service, "_save_job", side_effect=OSError("synthetic disk failure")):
            with self.assertRaises(OSError):
                self.service.submit(self.request_id, self.snapshot)
        self.assertTrue(self.service.queue.empty())
        self.assertEqual(self.bot.calls, [])
        self.assertFalse(self.service.status()["busy"])

    def test_unavailable_measurements_are_not_presented_as_real_zeros(self):
        message = format_message("SYNTHETIC-PANEL", {
            "phase": "PAUSED", "power": {"valid": False}, "imu": {"valid": False},
            "inspection": {"ai_enabled": False}})
        self.assertIn("Impatti totali: n/d", message)
        self.assertIn("Misure elettriche: non disponibili", message)
        self.assertIn("AI: non attiva", message)
        self.assertNotIn("Potenza: 0", message)

    def test_private_chat_id_validation_rejects_groups_and_booleans(self):
        for chat in (-123, True, "bot-token", 0):
            with self.subTest(chat=chat), self.assertRaises(ValueError):
                self.service.update_settings({"panel_id": "SYNTHETIC-PANEL", "chat_id": chat})

    def test_start_receipt_exposes_chat_id_without_changing_recipient(self):
        self.service._notice("command", 789012)
        self.service._notice("reply", False)
        state = self.service.status()
        self.assertEqual(state["last_command"]["chat_id"], 789012)
        self.assertFalse(state["last_command"]["reply_ok"])
        self.assertEqual(state["settings"]["chat_id"], 123456)

    def test_conflict_diagnostic_never_exposes_original_log_or_secret(self):
        events = []
        handler = SafeTelegramLog(lambda kind, value: events.append((kind, value)))
        record = logging.LogRecord("telegram", logging.ERROR, "synthetic", 1,
                                   "Conflict: other getUpdates at /botSYNTHETIC_SECRET/", (), None)
        handler.emit(record)
        self.assertEqual(events[0][0], "error")
        self.assertIn("Conflict", events[0][1])
        self.assertNotIn("SYNTHETIC_SECRET", events[0][1])

    def test_polling_error_disables_send_until_reconnected(self):
        self.service._notice("error", "Errore sintetico nella ricezione")
        self.assertEqual(self.service.status()["connection"], "ERROR")
        with self.assertRaises(RuntimeError):
            self.service.submit(self.request_id, self.snapshot)
        self.assertEqual(self.bot.calls, [])


if __name__ == "__main__":
    unittest.main()
