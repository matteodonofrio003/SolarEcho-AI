# Esportazione degli impatti per Edge Impulse

Lo script `tools/export_edge_impulse.py` prepara file locali. Non richiede
Arduino App Lab, pacchetti Python esterni, account o credenziali e non effettua upload.
Eseguirlo sul computer con Python 3.9 o successivo, dalla radice del repository.
Non serve fare deploy o modificare il firmware.

## 1. Copiare e separare gli originali

L'acquisizione salva CSV e JSON nella cartella `data/raw` della App sull'UNO Q.
Copiare **entrambi i file di ogni evento**, mantenendo gli stessi nomi.
Su Windows, per la connessione ADB gia usata dal progetto:

```powershell
New-Item -ItemType Directory -Force datasets/raw
$adb = "$env:LOCALAPPDATA\Arduino15\packages\arduino\tools\adb\32.0.0\adb.exe"
& $adb pull /home/arduino/ArduinoApps/solarecho-ai/data/raw datasets/raw
```

Se il percorso della App o di ADB e diverso, usare quello indicato dal deploy
e dalla console `CSV:`. Il pull puo creare una sottocartella `raw`: controllare
dove sono i file copiati. Copiarli senza alterarne il contenuto in cartelle
separate, ad esempio:

```text
datasets/raw/normal_training/       CSV + JSON normali per addestramento
datasets/raw/normal_calibration/    altri eventi normali per scegliere la soglia
datasets/raw/normal_test/           altri eventi normali per valutazione finale
datasets/raw/modified_test/         eventi con modifica meccanica reversibile
datasets/raw/restored_test/         eventi dopo il ripristino
```

La classe si assegna dalla condizione fisica annotata durante la prova, mai dal
picco o dallo score. Separare eventi interi prima dell'export; non dividere le
righe di un impatto tra gruppi. Preferire sessioni distinte per il test.
Non mettere lo stesso `(session_id, event_id)` in gruppi diversi: il convertitore
rileva duplicati nel singolo lotto, non confronta lotti separati.

## 2. Eseguire l'esportazione

Ogni comando richiede una cartella output **nuova**, senza sovrascrivere dati:

```powershell
python tools/export_edge_impulse.py --input datasets/raw/normal_training --output datasets/edge_impulse/normal_training_v1 --label normal --split training --notes "Annotare pallina, altezza, punto di caduta e fissaggio"
python tools/export_edge_impulse.py --input datasets/raw/normal_calibration --output datasets/edge_impulse/normal_calibration_v1 --label normal --split calibration
python tools/export_edge_impulse.py --input datasets/raw/normal_test --output datasets/edge_impulse/normal_test_v1 --label normal --split test
python tools/export_edge_impulse.py --input datasets/raw/modified_test --output datasets/edge_impulse/modified_test_v1 --label modified --split test
python tools/export_edge_impulse.py --input datasets/raw/restored_test --output datasets/edge_impulse/restored_test_v1 --label normal --condition restored --split test
```

Il ripristino ha classe `normal`, mentre il report conserva la condizione
`restored`. Le prove `modified` e `restored` vengono accettate solo nel test,
per mantenere l'addestramento della baseline sulle condizioni normali iniziali.
Questa regola riguarda il nostro percorso anomaly detection, non un classificatore.

## 3. Formato e trasformazioni

Ogni evento valido produce `<label>.<sha256-del-grezzo>.csv` nella sottocartella
del gruppo scelto, con le sole colonne:

```text
timestamp,accX,accY,accZ
```

- `timestamp`: millisecondi da zero, passo uniforme di 10 ms a 100 Hz.
- `accX/accY/accZ`: accelerazioni in **g**, ordine X/Y/Z.
- Finestra predefinita: da **-150 ms a +1850 ms esclusi**, relativa al trigger piezo.
- **200 campioni XYZ / 600 valori**, coerenti con il modello corrente: timestamp
  esportati da 0 a 1990 ms; il trigger cade a 150 ms. L'ultimo campione grezzo
  ricampionato corrisponde quindi a +1840 ms dal trigger.

Configurazione, controlli dei CSV/JSON e interpolazione sono condivisi con
l'inferenza nel modulo `app/python/signal_processing.py`. Export e inferenza
usano anche la stessa precisione numerica di 10 cifre significative sugli assi.
Nella dashboard il tempo rimane relativo al trigger; cambia solo l'origine
temporale, non i valori XYZ forniti al modello.

La finestra e leggermente piu corta del grezzo (-200 ms / +2 s), per evitare
di inventare i campioni alle estremita. I margini sono una scelta di export,
non una misura del tempo di decadimento. La griglia deve comunque essere
interamente coperta dai campioni reali: nessuna estrapolazione.

Il convertitore usa interpolazione lineare sui timestamp originali. Non sottrae
gravita/offset e non normalizza l'ampiezza. Non applica un filtro antialias:
il ricampionamento non rende osservabili frequenze mancanti e non garantisce
la fedelta della FFT vicino a Nyquist. Valutare banda e filtri prima del DSP.
Il report registra tutte queste scelte. L'eventuale preprocessing aggiuntivo
va definito e applicato nello stesso modo a training e inferenza.

`--rate-hz`, `--start-ms` e `--end-ms` sono configurabili, ma devono restare
uguali per tutto il dataset e per il modello. La durata moltiplicata per la
frequenza deve dare un numero intero di campioni. Una frequenza di export
superiore alla minima fra media e mediana della frequenza acquisita viene
rifiutata (tolleranza 1%): aumentarla non recupera informazioni mancanti.

I lotti storici da 210 campioni non vengono modificati. Per riprodurre la loro
finestra usare esplicitamente `--end-ms 1950`; questi CSV hanno una durata diversa
dall'input corrente a 200 campioni e non vanno sostituiti ai suoi dati di training.

## 4. Controllare il report

`export_report.json` resta fuori dalla cartella dei CSV da caricare e contiene
classi, condizioni, gruppo, note sperimentali, frequenza e finestra di export,
hash degli originali, frequenza misurata, numero di campioni e motivi di esclusione.

Lo script ricontrolla CSV e JSON: cattura/trasporto completi, assenza di
overflow/timeout/impatti aggiuntivi, conteggi e identita coerenti, indici consecutivi,
timestamp crescenti, valori finiti, pretrigger e copertura temporale sufficienti,
intervalli IMU non superiori a 30 ms. Un JSON mancante causa esclusione.
Questi controlli non provano che l'impatto sia ripetibile, la firma utile o il
sensore non saturato: serve ancora la verifica dei segnali reali.

Codici di uscita: `0` tutti esportati; `1` almeno un evento escluso (report da
controllare); `2` errore di comando, percorso o scrittura. Non sono risultati
di accuratezza del modello. Nessun dato sintetico viene generato dal convertitore.

## 5. Importare in Edge Impulse

1. Nel progetto aprire **Data acquisition**, quindi **Upload data**.
2. Caricare solo i CSV dentro la sottocartella `training` del lotto normale,
   scegliendo la destinazione **Training**.
3. Usare l'etichetta dal prefisso del nome file, oppure specificarla esplicitamente.
4. Verificare nel grafico tre assi, 100 Hz, un evento per file e classe `normal`.
5. Caricare i CSV dei lotti `test` nella destinazione **Testing**, con le classi
   `normal` o `modified` corrispondenti. Non usare una divisione casuale che
   riporti le prove modificate nel training.
6. Conservare `calibration` separato dal training e dalla valutazione finale.
   Edge Impulse distingue Training/Testing: la nostra cartella calibration non
   viene riconosciuta automaticamente come terzo gruppo. Per il primo MVP usare
   quei CSV per calibrare lo score localmente dopo il deployment.

Il modello personalizzato dovra aspettarsi **g**, gli stessi tre assi, **100 Hz**
e la stessa finestra. Il modello ventilatore predefinito non e la nostra baseline.
L'import e l'addestramento Edge Impulse richiedono rete; il deployment dovra
poi consentire l'inferenza offline sulla UNO Q.

## Verifiche software affidate al team

Sono inclusi test con dati esclusivamente sintetici, non eseguiti durante
questa implementazione e non utilizzabili come risultati sperimentali:

```powershell
python -m unittest discover -s tests -p "test_edge_impulse_export.py" -v
```

Il primo controllo su hardware resta l'export di una coppia CSV/JSON reale e
la visualizzazione del relativo segnale in Edge Impulse.

## Riferimenti

- [Formato CSV ufficiale Edge Impulse](https://docs.edgeimpulse.com/tools/specifications/data-acquisition/csv): timestamp in ms, intervalli costanti, un file per evento, prefisso etichetta.
- [Deployment su Arduino App Lab](https://docs.edgeimpulse.com/hardware/deployments/run-arduino-app-lab).
- [Procedura acquisizione e formato grezzo](ACQUISIZIONE_E_SENSORI.md#prima-acquisizione).
