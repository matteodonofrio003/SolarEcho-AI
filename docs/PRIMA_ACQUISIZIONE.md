# Prima acquisizione reale

Obiettivo: salvare una finestra di accelerazione X/Y/Z che contenga l'impatto della pallina. Questa fase **non** classifica anomalie e non conta automaticamente gli impatti.

## Collegamenti

1. Alimentare l'UNO Q da USB-C secondo il manuale Arduino.
2. Collegare il Modulino Movement direttamente al connettore Qwiic dell'UNO Q. Il firmware usa `Wire1`, cioe il bus Qwiic I2C4 a 3,3 V.
3. Fissare il Modulino sempre nello stesso punto e orientamento sulla struttura solidale al pannello. Non collocare la pallina sopra il sensore.
4. Il firmware attuale legge il piezo analogico su A0: completare le protezioni secondo la [procedura seriale/piezo](SERIALE_PIEZO.md) prima del collegamento. Se si prova soltanto l'IMU, tenere A0 a GND e lasciare il piezo scollegato. OLED, caricatore e batteria restano scollegati.

## Esecuzione

1. Collegare l'UNO Q e completare il setup di Arduino App Lab.
2. Dal repository eseguire `.\deploy.ps1` secondo la [procedura di deploy](DEPLOY.md). Riaprire **SolarEcho-AI** in App Lab; sorgenti e configurazione delle librerie vengono trasferiti insieme.
3. Avviare la App. Dopo 5 s parte una cattura di 6 s: far cadere **una** pallina leggera da altezza e punto ripetibili durante quella finestra.
4. Attendere la stampa `CSV:` e `cattura completa: True` nel log Python. Il file e nella directory persistente `data/raw` **della App sull'UNO Q**; copiarlo nel repository locale per analisi e confronto.
5. Ripetere almeno una prova a pannello fermo senza impatto e una con impatto. Conservare i file originali, annotando altezza, punto, fissaggio e posizione del sensore.

Il CSV ha lo schema grezzo della SRS, esteso con contatore, attraversamenti di soglia, ultima lettura ADC, picco e timestamp del piezo: vedere il formato aggiornato nella [procedura seriale/piezo](SERIALE_PIEZO.md). `trigger_state` contiene lo stato del rilevatore analogico con isteresi. `event_id=0` e `trigger_source=manual_window` indicano che si tratta di una finestra comandata, non di un evento identificato automaticamente. `timestamp_us` e il tempo relativo all'inizio della cattura misurato dallo STM32. X/Y/Z sono in `g` secondo la libreria Arduino.

## Cosa verificare subito

- Almeno alcune centinaia di campioni in 6 s e timestamp crescenti.
- Frequenza effettiva, intervalli min/max e assenza di buchi o campioni mancanti.
- Picco e successivo decadimento visibili vicino alla caduta, confrontati con la prova senza impatto.
- Nessuna saturazione apparente agli urti controllati.

Il valore nominale di 104 Hz della configurazione standard dell'IMU **non garantisce** 104 campioni/s nel CSV: `available()`, lettura I2C e scheduling determinano la frequenza reale. Se la firma non si distingue dal rumore o i campioni sono troppo radi, va modificata l'acquisizione prima di addestrare un modello.

La trasmissione Bridge inizia **dopo** la cattura. Il firmware invia un campione per notifica RPC e il logger verifica il numero, gli indici e i timestamp ricevuti. Una cattura incompleta viene comunque salvata per diagnosi, ma non deve entrare nella baseline.

Il team ha confermato compilazione ed esecuzione di questi sorgenti sull'UNO Q fisico. Il deploy USB e stato verificato sulla stessa scheda. La qualita della firma vibrazionale e la separazione tra condizioni meccaniche richiedono ancora l'analisi dei CSV reali.

## Fonti tecniche

- [Manuale UNO Q](UM.md), sezioni Bridge e Qwiic.
- [Guida Arduino al filesystem delle App](https://docs.arduino.cc/tutorials/uno-q/debian-guide/).
- [API ufficiale Arduino_Modulino](https://github.com/arduino-libraries/Arduino_Modulino/blob/main/docs/api.md).
- [Implementazione ufficiale ModulinoMovement](https://github.com/arduino-libraries/Arduino_Modulino/blob/main/src/Modulino.h).
- [Implementazione ufficiale Bridge Python](https://github.com/arduino/app-bricks-py/blob/main/src/arduino/app_utils/bridge.py).
