"""Copie sintetiche dei CSV di test SolarEcho: non modifica gli originali.

Solo libreria standard. Non esegue inferenza, non addestra e non effettua upload.
Le trasformazioni sono prove software, non modelli fisici di danni al pannello.
"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics


AXES = ("accX", "accY", "accZ")
TRANSFORMS = (
    {"name": "attenuated", "kind": "scale", "factor": 0.5},
    {"name": "amplified", "kind": "scale", "factor": 2.0},
    {"name": "added_oscillation", "kind": "ringing", "axis": "accZ",
     "amplitude_g": 0.08, "frequency_hz": 12.0, "decay_time_s": 0.45},
)
PROFILES = {
    "moderate": TRANSFORMS,
    "stress": (
        {"name": "stress_sustained", "kind": "sustained",
         "amplitude_g": 0.35, "frequencies_hz": [8.0, 17.0, 29.0],
         "ramp_time_s": 0.05},
    ),
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path):
    with path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != ["timestamp", *AXES]:
            raise ValueError(f"Colonne non supportate: {path.name}")
        rows = list(reader)
    if len(rows) < 2:
        raise ValueError(f"Campioni insufficienti: {path.name}")
    values = []
    for row in rows:
        if None in row or any(v is None for v in row.values()):
            raise ValueError(f"Riga incompleta: {path.name}")
        numeric = tuple(float(row[key]) for key in ("timestamp", *AXES))
        if not all(math.isfinite(v) for v in numeric):
            raise ValueError(f"NaN o infinito: {path.name}")
        values.append(numeric)
    return values


def diagnostics(rows, offset, trigger_ms):
    post = [row for row in rows if row[0] >= trigger_ms]
    dynamic_squared = [sum((row[k+1]-offset[k])**2 for k in range(3)) for row in post]
    return {
        "posttrigger_dynamic_rms_g": math.sqrt(statistics.mean(dynamic_squared)),
        "posttrigger_dynamic_peak_g": math.sqrt(max(dynamic_squared)),
        "max_abs_axis_g": max(abs(v) for row in rows for v in row[1:]),
    }


def transform(rows, trigger_ms, offset, settings):
    result = []
    for stamp, *axes in rows:
        if stamp >= trigger_ms:
            if settings["kind"] == "scale":
                axes = [offset[k] + settings["factor"] * (axes[k]-offset[k])
                        for k in range(3)]
            elif settings["kind"] == "ringing":
                elapsed = (stamp-trigger_ms)/1000
                oscillation = (settings["amplitude_g"]
                               * math.exp(-elapsed/settings["decay_time_s"])
                               * math.sin(2*math.pi*settings["frequency_hz"]*elapsed))
                axes[AXES.index(settings["axis"])] += oscillation
            elif settings["kind"] == "sustained":
                elapsed = (stamp-trigger_ms)/1000
                ramp = min(1.0, elapsed/settings["ramp_time_s"])
                for k, frequency in enumerate(settings["frequencies_hz"]):
                    axes[k] += (ramp * settings["amplitude_g"]
                                * math.sin(2*math.pi*frequency*elapsed))
            else:
                raise ValueError("Trasformazione sconosciuta")
        result.append((stamp, *axes))
    return result


def generate(source, output, profile="moderate"):
    if profile not in PROFILES:
        raise ValueError("Profilo sconosciuto")
    transformations = PROFILES[profile]
    source, output = Path(source).resolve(), Path(output).resolve()
    if output == source or source in output.parents:
        raise ValueError("Scegli un output fuori dalla cartella di input")
    if output.exists():
        raise ValueError("Output gia esistente: usa un nuovo nome, senza sovrascrivere")
    report_path = source / "export_report.json"
    report = json.loads(report_path.read_text(encoding="utf-8-sig"))
    if (report.get("split") != "test" or report.get("condition") != "normal"
            or report.get("label") != "normal" or report.get("units") != "g"):
        raise ValueError("Input richiesto: lotto di test normale esportato in g")
    rate = report["rate_hz"]
    duration = report["window_duration_ms"]
    trigger = report["trigger_at_export_ms"]
    if any(isinstance(v, bool) or not isinstance(v, (int, float))
           or not math.isfinite(v) or v <= 0 for v in (rate, duration, trigger)):
        raise ValueError("Frequenza, durata o trigger non validi")
    frequencies = [frequency for settings in transformations
                   for frequency in [settings.get("frequency_hz", 0),
                                     *settings.get("frequencies_hz", [])]]
    if max(frequencies) >= rate/2:
        raise ValueError("Oscillazione sintetica oltre il limite della griglia")
    expected_count = round(duration*rate/1000)
    if not math.isclose(expected_count, duration*rate/1000):
        raise ValueError("Durata e frequenza non danno un numero intero di campioni")
    events = [event for event in report["events"] if event["status"] == "exported"]
    actual_files = {path.resolve() for path in (source / "test").glob("*.csv")}
    sources, generated, seen_ids, seen_hashes = [], [], set(), set()
    # Valida e prepara l'intero lotto prima di creare l'output.
    for event in events:
        path = (source / event["output_csv"].replace("\\", "/")).resolve()
        path.relative_to(source / "test")
        identity = (event["session_id"], event["event_id"])
        checksum = digest(path)
        if identity in seen_ids or checksum in seen_hashes:
            raise ValueError("Evento duplicato nell'input")
        seen_ids.add(identity)
        seen_hashes.add(checksum)
        rows = read_csv(path)
        if len(rows) != expected_count:
            raise ValueError(f"Numero campioni errato: {path.name}")
        if any(not math.isclose(row[0], i*1000/rate, abs_tol=1e-6)
               for i, row in enumerate(rows)):
            raise ValueError(f"Timestamp non uniformi o non da zero: {path.name}")
        pre = [row for row in rows if row[0] < trigger]
        if len(pre) < 3 or not any(row[0] >= trigger for row in rows):
            raise ValueError("Pretrigger o posttrigger insufficienti")
        offset = [statistics.mean(row[k+1] for row in pre) for k in range(3)]
        source_record = {
            "source_csv": str(path), "source_csv_sha256": checksum,
            "raw_source_sha256": event["source_csv_sha256"],
            "session_id": identity[0], "event_id": identity[1],
            "pretrigger_mean_g": offset, **diagnostics(rows, offset, trigger),
        }
        sources.append(source_record)
        for settings in transformations:
            altered = transform(rows, trigger, offset, settings)
            if not all(math.isfinite(v) for row in altered for v in row):
                raise ValueError("Trasformazione non finita")
            filename = (f"anomaly.synthetic_{settings['name']}."
                        f"{event['source_csv_sha256']}.csv")
            generated.append((filename, altered, {
                "synthetic": True, "expected_test_label": "anomaly",
                "source_event_id": identity[1], "source_session_id": identity[0],
                "source_export_sha256": checksum,
                "transform": dict(settings), "output_csv": "test/" + filename,
                **diagnostics(altered, offset, trigger),
            }))
    if not events or actual_files != {Path(r["source_csv"]) for r in sources}:
        raise ValueError("CSV presenti diversi dagli eventi del report o lotto vuoto")
    if report["exported"] != len(sources):
        raise ValueError("Conteggio nel report incoerente")
    upload_dir = output / "test"
    upload_dir.mkdir(parents=True)
    for filename, altered, record in generated:
        destination = upload_dir / filename
        with destination.open("x", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(("timestamp", *AXES))
            for row in altered:
                writer.writerow(tuple(format(v, ".12g") for v in row))
        saved = read_csv(destination)
        if len(saved) != expected_count or any(
            not math.isclose(a, b, rel_tol=1e-10, abs_tol=1e-10)
            for expected, actual in zip(altered, saved) for a,b in zip(expected, actual)
        ):
            raise ValueError(f"Verifica del CSV scritto fallita: {filename}")
        record["output_sha256"] = digest(destination)
    if any(digest(Path(record["source_csv"])) != record["source_csv_sha256"]
           for record in sources):
        raise ValueError("Un originale e cambiato durante la generazione")
    manifest = {
        "format_version": 1, "synthetic": True, "split": "test", "profile": profile,
        "purpose": "Perturbazioni software di segnali di test reali; non validazione di danni fisici",
        "source_export_report": str(report_path), "source_report_sha256": digest(report_path),
        "rate_hz": rate, "window_duration_ms": duration, "samples_per_file": expected_count,
        "trigger_at_export_ms": trigger, "units": "g", "axes": list(AXES),
        "source_events": len(sources), "generated_files": len(generated),
        "pretrigger_preserved": True, "sources_unchanged": True,
        "transform_scope": "Solo campioni dal trigger in poi; offset medio pretrigger conservato",
        "warning": "Varianti dello stesso evento sono correlate. Non contarle come impatti fisici indipendenti. La label anomaly e un'aspettativa del test, non un risultato del modello.",
        "sources": sources, "generated": [record for _,_,record in generated],
    }
    (output / "synthetic_report.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False, allow_nan=False)+"\n", encoding="utf-8")
    description = (
        "- attenuated: componente dinamica moltiplicata per 0,5.\n"
        "- amplified: componente dinamica moltiplicata per 2.\n"
        "- added_oscillation: somma su accZ di una sinusoide a 12 Hz, ampiezza iniziale 0,08 g, decadimento esponenziale di 0,45 s.\n"
        if profile == "moderate" else
        "- stress_sustained: somma di oscillazioni persistenti di ampiezza 0,35 g su X/Y/Z, rispettivamente a 8/17/29 Hz; rampa iniziale di 50 ms.\n"
    )
    (output / "README.md").write_text(
        "# TEST SINTETICO\n\n"
        f"{len(generated)} CSV derivati da {len(sources)} impatti normali reali di test.\n\n"
        f"Profilo: {profile}.\n\n"
        "Trasformazioni fisse, applicate solo dopo il trigger:\n\n"
        + description + "\n"
        "Queste trasformazioni non sono modelli fisici validati del pannello.\n"
        "Originali, timestamp, unita e pretrigger sono conservati.\n\n"
        "Caricare SOLO i CSV in test/ nella destinazione Testing di Edge Impulse, con etichetta anomaly.\n"
        "Non caricarli nel Training. Mantenere fissi modello e soglia durante il confronto.\n"
        "Confrontare gli score di ogni variante con il suo originale; riportare anche i mancati rilevamenti.\n"
        "Le varianti sono correlate e non sono nuove prove sperimentali.\n"
        "Nessun risultato AI viene generato da questo script.\n", encoding="utf-8")
    print(f"Originali: {len(sources)}; copie sintetiche: {len(generated)}")
    print(f"Formato: {rate:g} Hz, {expected_count} campioni, {duration:g} ms, g")
    print(f"CSV da caricare in Testing, label anomaly: {upload_dir}")
    print("Integrita verificata: timestamp/formato validi; originali invariati.")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Lotto export normale di test, con export_report.json")
    parser.add_argument("--output", type=Path, required=True, help="Nuova cartella di output")
    parser.add_argument("--profile", choices=tuple(PROFILES), default="moderate",
                        help="moderate: tre perturbazioni; stress: oscillazioni persistenti sui tre assi")
    args = parser.parse_args()
    try:
        generate(args.input, args.output, args.profile)
    except (OSError, ValueError, TypeError, KeyError, csv.Error) as error:
        parser.exit(2, f"ERRORE: {error}\n")


if __name__ == "__main__":
    main()
