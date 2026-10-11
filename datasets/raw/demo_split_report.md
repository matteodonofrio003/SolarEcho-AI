# Divisione delle acquisizioni demo

Origine: `datasets/raw/demo`. Originali conservati. Condizione normale secondo le indicazioni dell operatore.

| Gruppo | Eventi | Cartella |
| --- | --- | --- |
| Training | 0001-0018 (18) | `demo_normal_training` |
| Calibrazione | 0019-0023 (5) | `demo_normal_calibration` |
| Test | 0024-0028 (5) | `demo_normal_test` |

Divisione cronologica per evento intero, senza duplicati fra gruppi. Tutti gli eventi sono della stessa sessione: il test rimane preliminare.

## Qualita dei dati

28 eventi completi, 229-230 campioni grezzi. Frequenza media per evento: 104.100-104.205 Hz.
Massimo intervallo IMU: 11093 us. Tutti coprono la griglia richiesta a 100 Hz.
RMS dinamico posttrigger: 0.0250-0.0688 g. Picco dinamico: 0.171-0.569 g.

Per queste statistiche si sottrae, per asse, la media pretrigger e si calcola il modulo del vettore dinamico. I CSV originali e quelli copiati non sono modificati.

Evento 0001: RMS pretrigger maggiore degli altri. Conservato; questo solo dato non dimostra una cattura inutilizzabile. Le ampiezze degli impatti variano e vanno considerate durante la calibrazione.

## Esclusi dalla divisione

| Evento | Motivo |
| --- | --- | --- |
| 0029 | JSON composto interamente da byte NUL |
| 0030 | CSV e JSON vuoti |
| 0031 | CSV e JSON vuoti |

Nessun file eliminato. Ricopiare dalla scheda le coppie 0029-0031 prima di concludere che siano perse: anche i file sulla scheda potrebbero essere corrotti.

## Export da eseguire sul computer

Finestra comune: -150 ms / +1850 ms esclusi, 100 Hz, 200 campioni, unita g. Le cartelle output seguenti devono essere nuove.

```powershell
python tools/export_edge_impulse.py --input datasets/raw/demo_normal_training --output datasets/edge_impulse/demo_training_v1 --label normal --split training --rate-hz 100 --start-ms -150 --end-ms 1850
python tools/export_edge_impulse.py --input datasets/raw/demo_normal_calibration --output datasets/edge_impulse/demo_calibration_v1 --label normal --split calibration --rate-hz 100 --start-ms -150 --end-ms 1850
python tools/export_edge_impulse.py --input datasets/raw/demo_normal_test --output datasets/edge_impulse/demo_test_v1 --label normal --split test --rate-hz 100 --start-ms -150 --end-ms 1850
```

Training e test vanno caricati nei rispettivi gruppi Edge Impulse. Calibrazione rimane separata per scegliere la soglia localmente.

I controlli effettuati riguardano esclusivamente questi dati reali e l integrita delle copie. Nessun test del progetto, addestramento, inferenza o deploy eseguito.
