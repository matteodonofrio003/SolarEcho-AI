"""Storico elettrico persistente. Il callback Bridge accoda, il loop Python scrive."""
import csv
from datetime import datetime, timezone
import io
import math
import os
from pathlib import Path
from queue import Empty, Full, Queue
import re
from threading import Lock
import time


POWER_NAME = re.compile(r"power_\d{8}_\d{6}_[0-9a-f]{8}")
COLUMNS = ("session_id", "received_at_utc", "elapsed_s", "measurement_timestamp_ms",
           "telemetry_timestamp_ms", "measurement_age_ms", "v_in_v", "v_out_v",
           "shunt_mv", "current_ma", "power_in_w")


class PowerHistory:
    def __init__(self, directory, session_id):
        self.directory = Path(directory)
        self.session_id = session_id
        self.name = f"power_{session_id}"
        self.path = self.directory / f"{self.name}.csv"
        self.started_at = time.monotonic()
        self.queue = Queue(maxsize=256)
        self.lock = Lock()
        self.io_lock = Lock()
        self.last_stamp = None
        self.created = False
        self.written = 0
        self.dropped = 0
        self.error = None

    def enqueue(self, data):
        """Nessun accesso disco nel thread Bridge; evita letture ripetute o obsolete."""
        if data["power_ok"] != 1 or data["power_error"] != 1:
            return
        stamp = int(data["power_t_ms"])
        age_ms = (int(data["t_ms"]) - stamp) % (2 ** 32)
        if age_ms > 3000:
            return
        with self.lock:
            if stamp == self.last_stamp:
                return
            self.last_stamp = stamp
            if self.error:
                self.dropped += 1
                return
            row = (self.session_id, datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
                   round(time.monotonic() - self.started_at, 6), stamp, int(data["t_ms"]), age_ms,
                   data["v_in"], data["v_out"], data["shunt_mv"],
                   data["current_ma"], data["power_w"])
            try:
                self.queue.put_nowait(row)
            except Full:
                self.dropped += 1

    def flush(self):
        """Scrive batch piccoli. Un errore ferma lo storico, non la cattura degli impatti."""
        with self.lock:
            if self.error:
                return []
        rows = []
        try:
            for _ in range(32):
                rows.append(self.queue.get_nowait())
        except Empty:
            pass
        if not rows:
            return []
        try:
            with self.io_lock:
                self.directory.mkdir(parents=True, exist_ok=True)
                # 'x' al primo batch: non sovrascrive mai una sessione esistente.
                with self.path.open("a" if self.created else "x", newline="", encoding="utf-8") as stream:
                    writer = csv.writer(stream)
                    if not self.created:
                        writer.writerow(COLUMNS)
                    writer.writerows(rows)
                    stream.flush()
                    os.fsync(stream.fileno())
                self.created = True
            with self.lock:
                self.written += len(rows)
            return rows
        except OSError as error:
            with self.lock:
                self.error = f"{type(error).__name__}: {error}"
                self.dropped += len(rows)
                # Non ritentare append ambigui: un batch puo essere stato scritto in parte.
                while True:
                    try:
                        self.queue.get_nowait()
                        self.dropped += 1
                    except Empty:
                        break
            print(f"POWER HISTORY ERROR: {self.error}. Storico sospeso; controllare spazio/permessi e riavviare.")
            return []

    def status(self):
        with self.lock:
            return {"name": self.name, "written": self.written, "queued": self.queue.qsize(),
                    "dropped": self.dropped, "error": self.error}

    def path_for(self, name):
        if not POWER_NAME.fullmatch(name):
            raise ValueError("Nome storico non valido")
        root = self.directory.resolve()
        path = root / f"{name}.csv"
        if path.resolve().parent != root or not path.is_file():
            raise FileNotFoundError("Storico non trovato")
        return path

    def sessions(self):
        if not self.directory.exists():
            return {"sessions": [], "total": 0, "limit": 100}
        paths = sorted((p for p in self.directory.glob("*.csv")
                        if POWER_NAME.fullmatch(p.stem) and not p.is_symlink()),
                       key=lambda p: p.stat().st_mtime, reverse=True)
        result = []
        for path in paths[:100]:
            stat = path.stat()
            result.append({"name": path.stem, "bytes": stat.st_size,
                           "active": path.stem == self.name,
                           "updated_at_utc": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat()})
        return {"sessions": result, "total": len(paths), "limit": 100}

    def read_session(self, name, limit=600):
        """Legge soltanto la coda del file; il download conserva tutte le righe."""
        if not 1 <= limit <= 3000:
            raise ValueError("Limite campioni: 1..3000")
        path = self.path_for(name)
        with self.io_lock, path.open("rb") as stream:
            header = stream.readline(1024).decode("utf-8")
            if tuple(next(csv.reader([header]), ())) != COLUMNS:
                raise ValueError("Intestazione storico non valida")
            header_end = stream.tell()
            position = stream.seek(0, os.SEEK_END)
            chunks = []
            newline_count = 0
            while position > header_end and newline_count <= limit:
                start = max(header_end, position - 4096)
                stream.seek(start)
                chunk = stream.read(position - start)
                chunks.append(chunk)
                newline_count += chunk.count(b"\n")
                position = start
                if sum(len(part) for part in chunks) > 2_000_000:
                    raise ValueError("Righe storico troppo grandi")
            tail = b"".join(reversed(chunks))
        # Non interpretare la prima riga troncata o l'ultima riga incompleta.
        if position > header_end:
            tail = tail.partition(b"\n")[2]
        tail = tail[:tail.rfind(b"\n") + 1]
        rows = tail.decode("utf-8").splitlines()[-limit:]
        samples = []
        for row in csv.DictReader(io.StringIO(header + "\n".join(rows)), fieldnames=None):
            values = [float(row[key]) for key in ("elapsed_s", "v_in_v", "current_ma", "power_in_w")]
            if not all(math.isfinite(value) for value in values):
                raise ValueError("Valori storico non validi")
            samples.append([*values[:3], values[3] * 1000, row["received_at_utc"]])
        return {"name": name, "samples": samples, "limit": limit,
                "columns": ["elapsed_s", "v_in_v", "current_ma", "power_in_mw", "received_at_utc"]}

    def snapshot_size(self, name):
        with self.io_lock:
            path = self.path_for(name)
            return path, path.stat().st_size

    @staticmethod
    def download_chunks(path, size):
        """Si ferma alla dimensione iniziale anche mentre il CSV attivo cresce."""
        with path.open("rb") as stream:
            remaining = size
            while remaining:
                chunk = stream.read(min(65536, remaining))
                if not chunk:
                    break
                remaining -= len(chunk)
                yield chunk
