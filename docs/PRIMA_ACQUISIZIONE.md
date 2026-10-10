# Prima acquisizione reale

Obiettivo: ogni impatto rilevato dal piezo genera una finestra di accelerazione X/Y/Z, con **200 ms prima del trigger e 2 s dopo**. Il firmware conta gli eventi con isteresi e lockout; la classificazione delle anomalie sara aggiunta dopo la verifica dei segnali reali.

## Collegamenti

1. Alimentare l'UNO Q da USB-C secondo il manuale Arduino.
2. Collegare il Modulino Movement direttamente al connettore Qwiic dell'UNO Q. Il firmware usa `Wire1`, cioe il bus Qwiic I2C4 a 3,3 V.
3. Fissare il Modulino sempre nello stesso punto e orientamento sulla struttura solidale al pannello. Non collocare la pallina sopra il sensore.
4. Il firmware attuale legge il piezo analogico su A0: completare le protezioni secondo la [procedura seriale/piezo](SERIALE_PIEZO.md) prima del collegamento. Se si prova soltanto l'IMU, tenere A0 a GND e lasciare il piezo scollegato. OLED, caricatore e batteria restano scollegati.

## Esecuzione

1. Collegare l'UNO Q e completare il setup di Arduino App Lab.
2. Dal repository eseguire `.\deploy.ps1` secondo la [procedura di deploy](DEPLOY.md). Riaprire **SolarEcho-AI** in App Lab; sorgenti e configurazione delle librerie vengono trasferiti insieme.
3. Avviare la App e attendere **READY** nella console Python o nel Serial Monitor. Far cadere **una** pallina leggera da altezza e punto ripetibili. Non serve riavviare la App fra impatti.
4. Il firmware raccoglie 2 s di risposta, poi mostra BUSY e trasferisce i dati. Attendere `CSV:` e `cattura completa: True`, quindi il nuovo **READY** prima della caduta successiva. Un ciclo dura indicativamente 3-4 s, da verificare sul banco. Durante il trasferimento gli impatti non vengono monitorati.
5. Per ogni evento vengono salvati un CSV e un JSON in `data/raw` **della App sull'UNO Q**. Copiare entrambi nel repository per analisi; annotare condizione normale/modificata/ripristinata, altezza, punto, fissaggio e posizione del sensore.
6. Osservare anche almeno 30 s di riposo: il contatore deve restare stabile. Questa versione non avvia una finestra senza trigger; il tratto prima del trigger costituisce una prima misura del rumore.

Il CSV ha lo schema grezzo della SRS, esteso con diagnostica piezo e `capture_complete`: vedere il formato nella [procedura seriale/piezo](SERIALE_PIEZO.md). `event_id` identifica una cattura, `trigger_source=piezo_analog`. `timestamp_us` e firmato e relativo al trigger: negativo prima dell'impatto, positivo dopo. Il timestamp zero identifica il superamento della soglia piezo, che puo essere successivo al primo contatto meccanico. X/Y/Z sono in `g` secondo la libreria Arduino.

Il nome e `<sessione>_event_0001.csv`, con un JSON dello stesso nome. Nel JSON si trovano frequenza effettiva, durata prevista, campioni ricevuti, overflow ed eventuali motivi di esclusione. `transport_complete` verifica la consegna; `capture_complete` controlla anche copertura temporale, intervalli IMU non superiori al limite diagnostico di 30 ms e assenza di ulteriori eventi accettati nella stessa finestra. Questo limite iniziale e una regola di qualita del dataset, non una soglia di anomalia del pannello.

Python conferma il salvataggio al firmware prima del riarmo. Un errore di scrittura o l'assenza della conferma per 15 s sospende le nuove catture: correggere il problema e riavviare la App. Un trasferimento fermo per 10 s produce file diagnostici incompleti. Non usare per addestramento i file con `capture_complete=False`.

## Cosa verificare subito

- Circa 229 campioni in 2,2 s a 104 Hz nominali, con timestamp crescenti e valori negativi prima del trigger.
- Frequenza effettiva, intervalli min/max e assenza di buchi o campioni mancanti.
- Picco e successivo decadimento visibili vicino alla caduta, confrontati con la prova senza impatto.
- Nessuna saturazione apparente agli urti controllati.

Il valore nominale di 104 Hz della configurazione standard dell'IMU **non garantisce** 104 campioni/s nel CSV: `available()`, lettura I2C e scheduling determinano la frequenza reale. Se la firma non si distingue dal rumore o i campioni sono troppo radi, va modificata l'acquisizione prima di addestrare un modello.

La trasmissione Bridge inizia **dopo** la cattura. Il buffer circolare precedente al trigger evita di iniziare il segnale soltanto dopo il rilevamento. Le soglie piezo restano ON=512, OFF=256, con lockout=800 ms: da validare sul montaggio definitivo. Un secondo evento accettato durante i 2 s viene contato e rende la finestra inutilizzabile per la baseline.

Le versioni precedenti sono state eseguite sull'UNO Q del team; il team ha fornito log reali del piezo con separazione fra rumore e impulsi. La nuova versione e stata compilata per `arduino:zephyr:unoq` con core 1.0.0, Modulino 0.9.0 e RouterBridge 0.4.3: 116828 byte di programma e 64220 byte di RAM dello sketch. I sette test del logger sono passati. La cattura automatica richiede ancora una prova fisica con un CSV completo per impatto. I test del logger usano esclusivamente dati sintetici e non misurano prestazioni sperimentali del progetto.

## Verifica software ripetibile

```powershell
python -m unittest discover -s tests -p "test_event_logger.py" -v
```

I test verificano eventi consecutivi, tempo prima/dopo il trigger, campioni mancanti, timestamp errati, impatti aggiuntivi, messaggi duplicati, timeout ed errori di scrittura.

Il profilo `app/sketch/sketch.yaml` include esplicitamente `Arduino_RouterBridge 0.4.3`, oltre alle librerie gia usate. Sull'UNO Q si puo compilare senza upload:

```sh
arduino-cli compile --fqbn arduino:zephyr:unoq --profile default /percorso/dello/sketch
```

## Fonti tecniche

- [Manuale UNO Q](UM.md), sezioni Bridge e Qwiic.
- [Guida Arduino al filesystem delle App](https://docs.arduino.cc/tutorials/uno-q/debian-guide/).
- [API ufficiale Arduino_Modulino](https://github.com/arduino-libraries/Arduino_Modulino/blob/main/docs/api.md).
- [Implementazione ufficiale ModulinoMovement](https://github.com/arduino-libraries/Arduino_Modulino/blob/main/src/Modulino.h).
- [Implementazione ufficiale Bridge Python](https://github.com/arduino/app-bricks-py/blob/main/src/arduino/app_utils/bridge.py).
