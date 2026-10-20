# Dashboard SolarEcho sulla UNO Q

Consultazione: [navigazione](#navigazione-a-tab), [storico elettrico](#storico-elettrico-automatico), [allerte e LED](#allerte-e-led).

## Navigazione a tab

La pagina e organizzata in quattro tab:

| Tab | Contenuto |
| --- | --- |
| Panoramica | Tensione, corrente, potenza, impatti, ultimo risultato AI, LED e ultima acquisizione |
| Vibrazioni e AI | Selezione evento, forma d'onda XYZ, inferenza, confronto sintetico, diagnostica e archivi |
| Energia e costi | Riferimento, confronto con oscuramento, scenario economico e storico elettrico |
| Segnalazioni | Dettaglio e reset dell'allerta, anteprima Telegram, invio e storico |

La barra con connessione, READY/BUSY, eta della telemetria e allerta resta
visibile durante lo scorrimento. Un'allerta aggiunge un indicatore al tab
Segnalazioni; il pulsante **Apri segnalazione** porta al dettaglio.

Impostazioni AI, soglie elettriche del LED, destinatario Telegram e parametri
economici sono in pannelli richiudibili. Aprili per modificare e salvare i
valori. Se manca la soglia AI o la configurazione Telegram, il relativo pannello
si apre inizialmente per facilitare il setup. Reset allerta e invio Telegram
restano accessibili fuori dalle impostazioni.

La Panoramica mostra il risultato AI dell'ultima analisi conclusa, con origine,
evento e data. **TEST SINTETICO** resta dichiarato anche qui e nell'allerta:
non indica una modifica fisica misurata. I risultati archiviati non sono uno
stato aggiornato in tempo reale del pannello. In assenza di connessione i valori
live vengono rimossi e gli altri sono indicati come ultimi dati ricevuti.

Cambiare tab non interrompe acquisizione, inferenza, salvataggio o richieste
gia in corso. Le selezioni degli eventi e i valori scritti nei moduli restano
in memoria fino alla ricarica della pagina. I grafici si ridisegnano quando
diventano visibili. Il tab selezionato e indicato nell'URL, ad esempio
`#vibrazioni`, e viene ripristinato ricaricando quell'indirizzo.

Su telefono la barra dei tab scorre orizzontalmente. Da tastiera usa Tab per
raggiungere la navigazione, frecce sinistra/destra per cambiare tab e Home/End
per il primo/ultimo. Si possono usare anche i collegamenti della Panoramica.

### Aggiornamento e verifica della nuova interfaccia

1. Dal repository esegui `.\deploy.ps1` senza `-Start`.
2. Riapri SolarEcho-AI in App Lab, riconfigura il token del brick Telegram
   dopo il deploy e verifica il modello personalizzato selezionato.
3. Premi Run, poi ricarica la dashboard con **Ctrl+F5**.
4. Controlla i quattro tab e apri i pannelli delle impostazioni. I valori
   devono essere quelli salvati sulla scheda.
5. Effettua un impatto aspettando READY. Cambia tab mentre viene salvato:
   contatore, evento e risultato AI devono aggiornarsi anche in Panoramica.
6. Apri Vibrazioni e AI e verifica i grafici; seleziona un evento, cambia tab
   e torna: selezione e dati devono restare disponibili.
7. Esegui un test sintetico e verifica la dicitura nella Panoramica e, se
   scatta l'allerta, nella barra sempre visibile. Leggi il dettaglio in
   Segnalazioni e usa il reset.
8. Verifica Energia e costi, download e anteprima Telegram; l'invio resta
   manuale. Prova anche dal telefono e con le frecce della tastiera.

Questa modifica riguarda gli asset HTML/CSS/JavaScript. Non aggiunge dipendenze
frontend. L'assistente ha effettuato una revisione statica senza eseguire app,
test o deploy; la verifica della nuova interfaccia e affidata al team.

## Cosa mostra

- Tensione del pannello su VIN+ dell'INA219, corrente in mA e potenza in **mW**.
- Storico elettrico persistente in CSV sulla UNO Q, selezione della sessione,
  grafico di potenza/tensione/corrente e download completo. Il grafico mostra
  le ultime 600 letture della sessione scelta e si ricarica dai file salvati.
- Anteprima accelerazione X/Y/Z in g e piezo A0, circa una volta al secondo.
- Contatore impatti, fronti piezo e fronti soppressi dal lockout.
- Stato dell'acquisizione, problemi IMU/INA219 e dati non aggiornati.
- Forma d'onda di ciascun evento salvato, con i timestamp reali.
- Ultimi 100 eventi presenti sulla scheda, download CSV originale e JSON.

Il modello AI personalizzato analizza gli eventi: vedere
[avvio, soglia e test sintetico](AI_INTEGRAZIONE.md). Gli esiti NORMAL/ANOMALY
descrivono la singola finestra rispetto alla baseline, non un danno certo.
"Cattura completa" descrive la qualita dell'acquisizione, non lo stato meccanico
del pannello e non la sua idoneita automatica per il training.

Disponibile anche il confronto elettrico con riferimento, calcolo energetico
e scenario economico ipotetico: vedere [la procedura della demo](DEMO_ECONOMICA.md).
Questa estensione deve essere provata dal team.

## Primo avvio: passo per passo

1. Collega UNO Q al PC con USB-C e apri Arduino App Lab.
2. Configura la connessione Wi-Fi della scheda in App Lab. Collega il PC alla
   stessa rete; va bene anche un hotspot che permetta ai dispositivi di comunicare.
3. Ferma SolarEcho-AI. Salva e chiudi eventuali modifiche aperte nell'editor
   di App Lab prima di trasferire i sorgenti del repository.
4. Apri PowerShell nella cartella `SolarEcho-AI` ed esegui:

   ```powershell
   .\deploy.ps1
   ```

   Lo script ora trasferisce anche `python/dashboard.py`, `python/power_history.py`,
   `python/electrical_demo.py`, `python/vibration_ai.py` e `assets/`.
   I CSV gia presenti sulla scheda vengono conservati.

5. Torna alla lista delle App e riapri **SolarEcho-AI** in App Lab.
   Il file `app.yaml` del repository contiene gia:

   ```yaml
   ports:
     - 7000
   bricks:
     - arduino:web_ui
     - arduino:telegram_bot
     - arduino:vibration_anomaly_detection:
         model: ei-model-1136239-1
   ```

   Non serve aggiungere nuovamente il brick a mano. Se nell'editor vedi ancora
   `bricks: []`, ricarica la App e verifica che il deploy sia terminato.

6. Reinserisci il token Telegram nel brick dopo il deploy e verifica che il
   modello AI sia gia scaricato. Premi **Run**. Attendi la compilazione e l'avvio di Python. Al primo avvio
   il runtime potrebbe dover scaricare le dipendenze del brick: prepara questa
   fase con Internet disponibile prima della demo offline.
7. Cerca nei log Python l'indirizzo mostrato dal brick Web UI come **Network URL**.
   Se manca, recupera l'IP della UNO Q dalle informazioni della scheda/rete
   in App Lab, oppure dal terminale Linux della scheda con:

   ```sh
   hostname -I
   ```

   Usa l'IP dell'interfaccia sulla stessa rete del PC, non un IP interno Docker.
8. Apri sul browser del PC:

   ```text
   http://<IP-della-UNO-Q>:7000
   ```

   Esempio: `http://192.168.1.42:7000` se quello e davvero l'IP della tua scheda.
   Dopo una modifica ai sorgenti, ripeti deploy e Run; non occorre un push GitHub.

## Prima verifica sul banco

1. Senza toccare il pannello, controlla che la pagina mostri **UNO Q connessa**.
   L'INA219 dovrebbe fornire letture circa una volta al secondo quando il firmware
   non sta acquisendo o trasferendo un impatto.
2. Punta una luce sul pannello e confronta i numeri con le righe `POWER` della
   seriale. La pagina usa **mW**, la seriale usa **W**: `0.00120 W = 1.200 mW`.
   Con una luce debole non dedurre da questi valori che la batteria stia caricando.
3. Attendi **READY** prima di far cadere la pallina. Il piezo deve essere tornato
   sotto soglia e il buffer pretrigger deve essere pronto.
4. Dopo l'impatto, la telemetria live si ferma durante la cattura di 2 s e il
   trasferimento. La dashboard mostra **TELEMETRIA SOSPESA** quando l'anteprima
   non e piu recente, poi **SALVATAGGIO** quando riceve l'inizio del trasferimento.
   La pausa non viene interpretata come prova certa di un nuovo impatto.
5. Attendi il prossimo **READY**. Il nuovo evento compare nell'elenco e, se
   **Segui ultimo evento** e selezionato, nel grafico. Il contatore live si
   aggiorna alla ripresa della telemetria.
6. Controlla numero di campioni, frequenza media e qualita. I gate sui CSV
   esistenti restano attivi: un evento incompleto o con altri eventi nella
   finestra viene mostrato come **Da escludere** e conservato per diagnosi.
7. Premi **Scarica CSV** e **Metadati JSON**. Salva entrambi nella stessa cartella
   sul PC, ad esempio `datasets/raw/normal/`; verifica la cartella Download del
   browser. Il download CSV e grezzo: per Edge Impulse passa ancora attraverso
   [la procedura di esportazione](EDGE_IMPULSE_EXPORT.md).
8. Ripeti 3 impatti separati, attendendo READY ogni volta. Verifica che seriale,
   contatore, eventi e file scaricati corrispondano.

La checkbox **Sottrai media pretrigger** sottrae per ciascun asse la media dei
campioni precedenti al trigger, solo per visualizzare meglio le oscillazioni.
Disattivala per vedere l'accelerazione grezza, inclusa la gravita. Nessun filtro
o ricampionamento viene applicato ai CSV scaricati dalla dashboard.

## Architettura

```text
STM32: IMU + piezo + INA219
  ├── IDLE: solarecho_live (~1 Hz, un JSON compatto)
  └── impatto: buffer RAM → solarecho_begin/sample/end → CSV + JSON
                         ↓ Bridge
Linux: main.py → Dashboard → Web UI brick :7000
                              ↓ HTTP sulla rete locale
                      Browser: HTML + CSS + JavaScript + canvas
```

Le richieste del browser leggono una copia della telemetria su Linux e i file
salvati. Non chiamano Bridge e non interrogano direttamente i sensori. I callback
live conservano l'ultima anteprima e accodano nuove misure elettriche valide,
senza scrivere su disco nel callback Bridge. Il loop Python scrive lo storico
in batch piccoli, con flush e fsync. L'acquisizione conserva timestamp e
controllo degli intervalli originali. Non sono state aggiunte RPC al firmware
per registrare lo storico: viene usata la telemetria gia disponibile.

Durante CAPTURING, SENDING e WAIT_ACK il firmware non aggiunge messaggi live.
Le RPC di telemetria in IDLE possono comunque introdurre latenza nel pretrigger:
va verificata sui primi CSV reali con la dashboard abilitata. Se compare
"interruzione nel campionamento IMU", confrontare `max_imu_gap_us` e i log prima
di raccogliere un nuovo dataset.

Non servono librerie frontend o font scaricati da Internet. Dopo l'installazione
delle dipendenze della App, dashboard e acquisizione funzionano sulla rete locale
anche senza Internet. L'accesso pubblico da fuori rete resta da configurare.

### API di consultazione

| Endpoint GET | Contenuto |
| --- | --- |
| `/api/status` | Stato, sessione, eta della telemetria, anteprima, AI, allerta e servizi |
| `/api/events` | Ultimi 100 eventi con CSV e JSON, qualita e totale archivio |
| `/api/events/<nome>` | Timestamp in ms, accelerazione dei tre assi e metadati |
| `/api/download/<nome>/csv` | CSV grezzo originale |
| `/api/download/<nome>/json` | Metadati originali |
| `/api/power` | Ultime 100 sessioni elettriche disponibili e totale |
| `/api/power/<nome>?limit=600` | Ultime letture della sessione, massimo 3000 via API |
| `/api/power/<nome>/download` | CSV elettrico completo fino all'inizio del download |

Sono scaricabili i file evento riconosciuti in `data/raw/` e gli storici
elettrici riconosciuti in `data/power/`. Non sono presenti
comandi web per cancellare dati, modificare il firmware o avviare training.
I controlli POST del confronto elettrico e dei parametri economici sono descritti
in [DEMO_ECONOMICA.md](DEMO_ECONOMICA.md). Non comandano il firmware.
Questa prima versione non include login: e pensata per la rete locale della demo.

## Se qualcosa non va

| Sintomo | Cosa controllare |
| --- | --- |
| `No module named arduino.app_bricks.web_ui` | YAML trasferito, brick Web UI visibile, dipendenze installate dal runtime |
| `No module named dashboard` | `python/dashboard.py` deve essere presente dopo il nuovo deploy |
| `No module named power_history` | `python/power_history.py` deve essere presente dopo il nuovo deploy |
| Pagina non raggiungibile | Run attivo, indirizzo corretto, porta 7000, stessa rete, nessun isolamento client Wi-Fi |
| Pagina visibile ma sempre AVVIO | Firmware aggiornato e log Python/Bridge; devono essere trasferiti sia sketch sia Python |
| Potenza non disponibile | Stato INA219 e log `POWER SENSOR ERROR`; un impatto sospende normalmente le letture |
| Piezo sempre sopra soglia | Controllare circuito e offset A0: il firmware aspetta il rilascio prima del riarmo |
| Evento presente ma non valido | Leggere il JSON; non cambiare le soglie di qualita solo per farlo apparire valido |
| Storico sospeso / errore di salvataggio | Controllare spazio su disco e permessi di `data/power/`, poi riavviare la App |

## Storico elettrico automatico

Appena arriva una nuova misura valida, Python la registra in:

```text
data/power/power_<session_id>.csv
```

Esempio di percorso sulla scheda:
`/home/arduino/ArduinoApps/solarecho-ai/data/power/`.
Ogni avvio della App crea una nuova sessione; il file viene creato alla prima
lettura valida. Non si sovrascrivono file precedenti. Il salvataggio funziona
anche con browser chiuso e senza Internet; i dati restano dopo Stop/Run o riavvio
e non vengono toccati dal deploy. Questa funzione non recupera le letture
elettriche dei test precedenti alla sua installazione.

### Uso dalla pagina

1. Esegui il nuovo deploy e Run, poi ricarica la dashboard.
2. Nel tab **Energia e costi**, sezione **Storico elettrico**, controlla che il numero di letture salvate
   della sessione corrente aumenti. La registrazione e automatica.
3. Seleziona **Potenza**, **Tensione** o **Corrente** per cambiare il grafico.
4. Lascia **Segui sessione corrente** selezionato per vedere la sessione attuale.
   Per consultare una prova precedente, scegli la sessione nel menu: il follow
   si disattiva. Il grafico si aggiorna circa ogni 3 secondi.
5. Premi **Scarica storico CSV** per copiare l'intera sessione sul PC. Il grafico
   mostra solo le ultime 600 righe; il download non ha questo limite. Se il file
   sta crescendo, il download contiene i dati scritti all'inizio della richiesta.

### Formato CSV

| Colonna | Significato |
| --- | --- |
| `session_id` | Identificatore della sessione Python |
| `received_at_utc` | Ora UTC di ricezione della telemetria su Linux, con offset `+00:00` |
| `elapsed_s` | Secondi dalla partenza del logger, misurati con orologio monotono Python |
| `measurement_timestamp_ms` | Timestamp della misura INA219, `millis()` del microcontrollore |
| `telemetry_timestamp_ms` | Timestamp della telemetria, `millis()` del microcontrollore |
| `measurement_age_ms` | Eta della misura quando e stata inviata la telemetria, con gestione rollover |
| `v_in_v`, `v_out_v` | Tensioni su VIN+ e VIN- in V |
| `shunt_mv` | Tensione dello shunt in mV |
| `current_ma` | Corrente in mA, con il segno originale |
| `power_in_w` | Potenza su VIN+ in W, con il segno originale |

L'ora UTC dipende dall'orologio Linux della scheda; non e un timestamp hardware
dell'istante di conversione. Il grafico usa `elapsed_s`, quindi non cambia
se l'orologio civile viene corretto. Mostra il tempo di ricezione delle letture.

Si registrano soltanto nuove misure valide presenti nella telemetria, con eta
massima di 3 secondi, scartando duplicati del timestamp INA219. Il ritmo e circa
1 Hz, senza garantire di conservare ogni conversione stampata sulla seriale:
il firmware invia nella telemetria l'ultima misura disponibile. Durante impatti,
trasferimenti o errori INA219 non vengono aggiunte letture inventate e il grafico
non collega intervalli superiori a 2,5 s. Non viene calcolata energia cumulativa
attraverso queste pause.

Il logger usa una coda massima di 256 misure. Se si riempie, il contatore di
letture non registrate compare nella pagina. Un errore disco sospende lo storico
e mostra un messaggio; per ripartire occorre correggere il problema e riavviare
la App. Gli impatti non sono fermati da un errore del logger elettrico, ma un
disco pieno puo naturalmente impedire anche il salvataggio dei loro CSV.
Il contatore "salvate" include i batch confermati con fsync. Dopo un errore I/O,
un batch puo essere presente solo in parte: controllare il CSV della sessione.
Uno stop improvviso puo perdere le misure ancora in coda, non ancora scritte.

### Verifica da eseguire

1. Lascia Run attivo 30 secondi e verifica che le righe salvate aumentino.
2. Chiudi il browser per 20 secondi. Riaprilo: le letture del periodo devono
   essere presenti nello storico, anche se non osservate live.
3. Cambia illuminazione e controlla le colonne tensione/corrente/potenza nel CSV.
4. Esegui un impatto e verifica che il grafico lasci la pausa senza valori
   interpolati e che l'acquisizione dell'impatto rimanga completa.
5. Fai Stop/Run. Scegli la sessione precedente: grafico e download devono restare
   disponibili; la nuova sessione deve avere un file distinto.

## Stato della verifica

La dashboard iniziale e stata provata dal team e dichiarata funzionante.
Lo storico elettrico e stato preparato nel repository senza eseguire test,
deploy o Run. Verifica del salvataggio persistente e della consultazione delle
sessioni precedenti affidata al team, secondo la procedura sopra.

## Documentazione ufficiale utilizzata

- [Web UI: API, asset locali, avvio e porta predefinita](https://github.com/arduino/app-bricks-py/blob/main/src/arduino/app_bricks/web_ui/README.md).
- [Esempio Arduino con brick Web UI nel manifest](https://github.com/arduino/app-bricks-examples/blob/main/inspirational/platform_unoq/color-your-leds/app.yaml).
- [Specifica App Lab: cartelle, dati persistenti, porte e bricks](https://github.com/arduino/arduino-app-cli/blob/main/docs/app-specification.md).

## Allerte e LED

### Regola implementata

Il LED si accende quando si verifica **una delle due condizioni**:

1. Dopo un riferimento elettrico valido, il contatore piezo registra almeno
   **3 nuovi impatti** e **5 nuove letture consecutive** dell'INA219 indicano
   una potenza inferiore di almeno **20%** rispetto al riferimento.
2. Il modello locale personalizzato restituisce uno score maggiore o uguale alla soglia salvata
   per una cattura confrontabile. Questa condizione non richiede 3 impatti.

Numero di impatti, percentuale e letture consecutive sono modificabili nella
dashboard. **3 / 20% / 5 sono valori iniziali per la demo, non soglie validate**.
Il conteggio usa gli eventi accettati dal firmware, dopo isteresi e lockout:
verificare che corrispondano ai colpi realmente effettuati.

L'integrazione AI e pronta per la prova: [procedura e soglia](AI_INTEGRAZIONE.md).
Senza soglia salvata, o con LED AI disabilitato, non vengono generate allerte AI.
Il test artificiale puo accendere il LED, ma dashboard, archivio e Telegram
riportano **AI_TEST / TEST SINTETICO**, non un'alterazione fisica misurata.

L'allerta significa **"Ispezione consigliata"**. Ombra, variazioni della luce,
carico o comportamento del charger possono cambiare la potenza. La sequenza
impatti + calo non dimostra che gli impatti abbiano danneggiato il pannello.

### Collegamento del LED esterno

Per un comune LED rosso a due terminali, a scheda disalimentata:

```text
UNO Q D7 ── resistenza 1 kohm ── anodo LED rosso
                                     catodo ── UNO Q GND
```

- Anodo: normalmente il terminale lungo.
- Catodo: normalmente il terminale corto e il lato piatto del contenitore;
  se i terminali sono stati tagliati, verificare la polarita del componente.
- La resistenza e **in serie**, non in parallelo.
- D7 e un'uscita a 3,3 V: non collegare il LED al 5 V.
- Per un LED con caduta diretta di circa 2 V, la corrente e circa
  `(3,3 - 2) / 1000 = 1,3 mA`; il valore effettivo dipende dal LED.
- Questo schema riguarda un LED indicatore semplice; moduli e LED di potenza
  richiedono la verifica della loro documentazione.

D7 corrisponde a PB2 sull'header digitale secondo il
[manuale ufficiale Arduino](https://docs.arduino.cc/resources/datasheets/ABX00162-ABX00173-datasheet.pdf)
e il [riferimento al manuale Arduino](https://docs.arduino.cc/tutorials/uno-q/user-manual/). Il dimensionamento a bassa corrente e coerente
con le caratteristiche GPIO del
[datasheet STM32U585, sezione caratteristiche di uscita](https://www.st.com/resource/en/datasheet/stm32u585ai.pdf).

Lo sketch replica la segnalazione sul **segmento rosso del LED RGB integrato
numero 3**, `LED3_R`, attivo LOW. Puoi quindi fare la prima prova senza LED
esterno. Gli altri segmenti di quel LED sono spenti. Il controllo del LED
integrato e documentato nel [manuale Arduino](https://docs.arduino.cc/tutorials/uno-q/user-manual/).

### Prova passo per passo

1. Collega il LED come sopra, oppure usa quello integrato.
2. Dal repository esegui `./deploy.ps1`, poi apri SolarEcho-AI in App Lab e premi
   **Run**. Ricarica la dashboard per caricare anche il nuovo JavaScript.
3. Illumina stabilmente il pannello. Tieni invariati luce, posizione e carico.
4. Premi **Acquisisci riferimento** e aspetta le 10 letture valide. Servono
   potenza sufficiente e stabilita, come nella [demo elettrica](DEMO_ECONOMICA.md).
5. Controlla la sezione **Segnalazione di ispezione**: LED spento, impatti dal
   riferimento pari a zero. Se una precedente allerta e stata ripristinata,
   leggine il motivo e premi **Conferma / reset allerta** prima della nuova prova.
6. Fai cadere la pallina 3 volte, aspettando **READY** prima di ogni colpo.
   Controlla che il contatore aumenti correttamente. I soli colpi non devono
   accendere il LED se la potenza resta normale.
7. Per questa demo, copri una parte del pannello senza spostare la sorgente
   luminosa. Mantieni un calo di almeno 20%: dopo 5 letture consecutive valide
   compare **Ispezione consigliata** e si accendono entrambi i LED rossi.
8. Scopri il pannello: la potenza dovrebbe recuperare, ma l'allerta resta
   accesa finche premi **Conferma / reset allerta**.
9. Premi reset con potenza tornata normale: la richiesta di spegnimento viene
   inviata al firmware. La dashboard conferma lo stato sulla telemetria
   successiva. Se il calo persiste, l'allerta puo riattivarsi dopo altre 5 letture.

Il confronto economico puo essere avviato in parallelo per misurare il deficit;
il LED non richiede che sia attivo. La percentuale ipotetica del calcolatore
economico non viene usata per accendere il LED.

Le letture elettriche sono sospese durante cattura e trasferimento dei CSV.
Una pausa di oltre 2,5 s azzera la serie di letture consecutive: riparte con
nuove misure. Cinque letture richiedono circa cinque secondi di monitoraggio
senza pause, piu la latenza della telemetria e del comando LED.

### Stato, reset e salvataggio

- Il cambio fisico delle uscite avviene solo nello stato firmware `IDLE`.
  La richiesta Bridge memorizza un intero atomico, senza accessi ai GPIO,
  stampe o chiamate RPC nel callback. Vedere
  [Arduino RouterBridge](https://github.com/arduino-libraries/Arduino_RouterBridge).
- La dashboard distingue allerta software, stato GPIO confermato e aggiornamento
  in corso. La conferma GPIO non misura elettricamente l'accensione del LED.
- Nessun dato mancante o errore INA219 e interpretato come potenza zero.
  Le misure inverse interrompono la serie; restano nei CSV grezzi.
- Soglie e allerta corrente, con motivo, timestamp e valori rilevati, sono
  salvati in `data/analysis/inspection_alert.json`. Il reset conferma e rimuove
  l'allerta corrente da questo file; non e un archivio di tutte le allerte.
- Un'allerta salvata viene ripristinata dopo Run quando riprende la comunicazione
  con il firmware. Alla partenza dello sketch le uscite sono inizialmente spente.
- Il riferimento elettrico e i conteggi relativi non vengono ripristinati dopo
  Run. Raccogli un nuovo riferimento prima di una nuova sequenza di prova.
- Un reset del contatore/tempo MCU invalida il riferimento per il LED; acquisiscine
  uno nuovo. Un riferimento nuovo o un cambio di soglie non cancella un'allerta.
- Se il salvataggio dell'allerta fallisce, resta attiva in RAM con un errore
  visibile; il ripristino al successivo Run non e garantito. Un reset fallito
  non spegne l'allerta. Lo storico elettrico fallito sospende le nuove valutazioni.

API aggiunte: `POST /api/inspection/settings` con i tre parametri
`min_impacts`, `drop_pct`, `consecutive_samples`; `POST /api/inspection/reset`.
Lo stato si trova nel campo `inspection` di `GET /api/status`.

### Collegamento al modello AI

Nel loop di elaborazione, dopo un'inferenza reale e la verifica di qualita:

```python
inspection.on_ai_result(float(score), float(calibrated_threshold), event_name,
                        comparable=capture_complete)
```

`calibrated_threshold` deve provenire dalla validazione del modello; non usare
la soglia di calo elettrico. Uno score non finito o una cattura non confrontabile
non genera una richiesta di ispezione. Uno score normale non cancella un'allerta
precedente. La chiamata va eseguita nel processamento Python, non nel callback
di acquisizione. Il worker `vibration_ai.py` esegue questa chiamata.
`/api/ai/synthetic` genera una copia alterata e inferisce sul runner reale;
non accetta una classificazione o uno score da inserire a mano.

### Verifiche affidate al team

La tabella seguente descrive le verifiche da eseguire sul banco; non riporta nuovi risultati:

| Prova | Comportamento atteso |
| --- | --- |
| Nessun riferimento | Nessuna nuova allerta elettrica |
| Calo prima di 3 impatti | LED spento |
| 3 impatti con potenza normale | LED spento |
| Calo breve, meno di 5 letture | LED spento |
| 3 impatti + calo persistente | LED acceso e motivo elettrico |
| Ripristino della luce | Allerta ancora accesa |
| Reset con luce normale | LED spento alla ripresa del monitoraggio |
| Reset con calo persistente | Nuova allerta dopo 5 letture |
| INA219 non disponibile | Nessun calo ricavato dal dato mancante |
| Run dopo allerta salvata | Allerta ripristinata, nuovo riferimento necessario |

Controllare anche la qualita dei CSV IMU dopo l'aggiunta del comando Bridge
LED. I test in `tests/test_inspection_alert.py` usano esclusivamente valori
sintetici, senza hardware e senza risultati sperimentali. Se vuoi eseguirli:

```powershell
python -m unittest discover -s tests -p test_inspection_alert.py
```
