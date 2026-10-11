# Analisi materiali — stato iniziale

Analisi della cartella `materiale_per_video` l'11 ottobre 2026.

## Inventario

Un file: `Registrazione 2026-10-11 151111.mp4`.

- Durata: **83,200 s**.
- Video: **1828 × 924**, 30 fps costanti, H.264, YUV420p.
- Audio: AAC stereo, 48 kHz, circa 192 kbit/s.
- Dimensione: 74.902.426 byte.
- Contenuto: screen recording dell'interfaccia SolarEcho AI.
- Qualità: testo nitido nella registrazione originale, leggero scroll e cursore;
  rapporto d'aspetto diverso da 16:9, da preservare con cornice e ritagli controllati.

Sono stati estratti con FFmpeg 21 fotogrammi ogni 4 secondi e sette
fotogrammi a risoluzione originale. Inventario e dati FFprobe in `analisi/`.

## Evidenze osservabili

- Stato UNO Q connessa e READY.
- Misure di tensione, corrente e potenza nell'interfaccia.
- Evoluzione del contatore da 8 a 9 e nuova acquisizione.
- Grafico XYZ di risposta all'impatto.
- Modello pronto; score reale 0,6035 con soglia 0,3000.
- Inferenza separata su firma alterata, etichettata TEST SINTETICO.
- Ispezione consigliata e stato LED rosso acceso nella dashboard.
- Interfaccia di segnalazione Telegram.

Queste evidenze documentano acquisizione, analisi e segnalazione software.
Non mostrano fisicamente la pallina, il pannello o il LED; non dimostrano
un danno meccanico. Lo score non è una probabilità di danno.

## Verifica tecnica dal codice

Il manifest usa il modello locale `ei-model-1136239-1`.
`app/python/vibration_ai.py` ricampiona XYZ a 100 Hz, usa 200 campioni
(600 valori), controlla la qualità dell'acquisizione e confronta lo score
con una soglia salvata. L'inferenza è locale tramite il brick Arduino;
la validazione su alterazioni meccaniche reali resta da completare.

Il piezo è usato come trigger; il sensore IMU misura la risposta XYZ.
INA219 misura grandezze elettriche, che non sono prova di danno da impatto.
Il test sintetico aggiunge oscillazioni software e resta distinto da eventi reali.

## Materiali mancanti e decisione

Non sono presenti fotografie o riprese fisiche nella cartella iniziale.
L'utente ha chiesto esplicitamente di **attendere**, perché aggiungerà
le riprese fisiche. Il montaggio e il rendering hackathon restano in attesa;
sceneggiatura e storyboard sono stati preparati come bozza.

Il precedente promo da 45 secondi resta separato e intatto.
