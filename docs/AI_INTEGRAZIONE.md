# Modello locale e test sintetico nella dashboard

Per identità, dataset, contratto dell'input e limiti vedere la
[scheda del modello](MODEL_CARD.md); per le evidenze già disponibili vedere
[Demo e risultati](DEMO_E_RISULTATI.md). Questa guida descrive la procedura operativa.

## Stato

Implementazione pronta per la prova del team; questa integrazione non e stata
eseguita, compilata o trasferita dall'assistente. Il modello personalizzato e
`ei-model-1136239-1`, progetto Edge Impulse 1136239. Non usare il modello generico
per giudicare la firma normale del pannello. La validazione su alterazioni
meccaniche reali resta da completare.

Export e inferenza usano il modulo comune `app/python/signal_processing.py`:
100 Hz, 200 campioni XYZ, finestra [-150, +1850) ms e assi in g. I controlli
di qualita, l'interpolazione e la precisione dei valori sono gli stessi.
Il convertitore usa ora questa finestra anche senza `--end-ms 1850`.

## Avvio passo per passo

1. Ferma l'altra App di prova delle vibrazioni. Dal repository esegui:

   ```powershell
   .\deploy.ps1
   ```

2. Torna alla lista delle App e riapri **SolarEcho-AI** in App Lab.
3. Verifica nel brick **Vibration Anomaly Detection** che sia selezionato il
   modello personalizzato `ei-model-1136239-1`, gia scaricato in AI Models.
   La selezione e gia nel manifest del repository. Se manca il modello,
   scaricalo prima di Run; non sostituirlo con quello predefinito.
4. Reinserisci il token nel campo segreto del brick Telegram Bot: il deploy
   sostituisce il manifest con quello senza credenziali. Non scriverlo nella repo.
5. Premi **Run**. Aspetta READY dell'acquisizione e **MODELLO PRONTO** nella
   dashboard. Nei log deve comparire:

   ```text
   AI_MODEL id=ei-model-1136239-1 project_id=1136239 frequency_hz=100 input_features_count=600 units=g
   ```

6. Apri `http://<IP-UNO-Q>:7000` e ricarica con **Ctrl+F5** per aggiornare gli asset.
7. In Edge Impulse apri **Model testing**, quindi le impostazioni delle soglie
   vicino a **Classify all / Test all**. Leggi il valore del blocco Anomaly
   detection in **Confidence thresholds**. Riporta lo stesso valore nel campo
   **Soglia usata in Edge Impulse** e premi **Salva soglia AI**.
8. Lascia selezionata **Attiva il LED D7 oltre soglia** per la dimostrazione.
   Senza soglia salvata, l'inferenza calcola lo score ma mostra
   **SOGLIA DA IMPOSTARE** e non genera allerte AI.

La soglia non e una probabilita o percentuale: lo score K-means puo essere
negativo. Non scegliamo un valore per ottenere una specifica risposta sui
sintetici. Le impostazioni dello Studio e della dashboard non si sincronizzano:
se cambi la soglia nello Studio, aggiornala e salvala anche nella dashboard.

## Prova reale

1. Mantieni montaggio, sensori, pallina, altezza e punto di impatto come nel
   training. Non spostare il Modulino.
2. Effettua 3 impatti normali, aspettando READY prima di ciascuno. Aspetta anche
   che l'inferenza precedente finisca per associare chiaramente evento e score.
3. Ogni CSV appena salvato entra nella coda AI. Lo storico mostra origine
   **REALE**, score, soglia ed esito. Apri **Mostra risultato** per il grafico.
4. Seleziona un evento nell'elenco delle acquisizioni per analizzarlo nuovamente
   con **Analizza evento selezionato**. Il pulsante non crea un nuovo impatto.
5. Un'anomalia reale sopra soglia puo accendere il LED e chiedere un'ispezione.
   Non certifica un danno o una microfrattura.

Non e garantito che tutti i nuovi impatti normali siano riconosciuti: montaggio,
forza, rumore e variabilita non rappresentata dal training possono cambiare lo
score. Conservare anche falsi allarmi e mancati rilevamenti.

## Prova sintetica, dichiarata come tale

1. Seleziona una cattura normale valida nell'elenco degli eventi. Puoi
   disabilitare **Segui ultimo evento** per mantenerla selezionata.
2. Se il LED e gia acceso, leggi il motivo e premi **Conferma / reset allerta**.
   Un'allerta gia presente resta memorizzata fino al reset.
3. Premi **Esegui TEST SINTETICO** e aspetta il completamento. Non servono altri
   lanci durante questa prova.
4. Il sistema inferisce la copia alterata e il suo originale sullo stesso
   runner. Il dettaglio mostra i due score e il grafico sovrapposto; la dicitura
   **TEST SINTETICO — firma alterata artificialmente** resta visibile.
5. Se la copia supera la soglia e il LED AI e abilitato, l'allerta ha motivo
   **AI_TEST**. Il contatore degli impatti fisici non cambia. Il superamento
   della soglia non e garantito e lo score non viene forzato.
6. Scarica il risultato JSON. L'anteprima e l'invio manuale Telegram includono
   l'origine sintetica. Per inviare, premi il pulsante Telegram gia esistente;
   il test AI non invia automaticamente messaggi.
7. Premi reset dopo la prova. Uno score normale successivo non spegne da solo
   un'allerta memorizzata.

La dashboard usa il profilo `stress_sustained` descritto nei
[test sintetici offline](#test-sintetici-offline). Il CSV originale rimane
intatto. La prova dimostra il percorso software di inferenza e allerta,
non il rilevamento di danni fisici.

## Contratto dei dati e architettura

- MCU: acquisizione IMU/piezo e buffer -200 ms / +2 s; nessuna modifica al firmware.
- Linux: dopo il salvataggio CSV, accoda il percorso senza inferenza nel callback
  Bridge. Il worker AI e separato; la conferma al firmware non attende il modello.
- Controlli: cattura completa, nessun evento aggiuntivo, indici e conteggi
  coerenti, timestamp crescenti, valori finiti, copertura pre/posttrigger,
  intervallo IMU massimo 30 ms e frequenza sufficiente.
- Input: interpolazione lineare a **100 Hz**, **200 campioni XYZ**, **600 valori**,
  in **g**, griglia **[-150, +1850) ms** dal trigger. Nessuna estrapolazione.
  Come l'export del training: nessun offset o normalizzazione aggiuntiva
  prima dell'input. La precisione decimale riproduce quella dell'export.
- Limite: l'interpolazione non e un filtro antialias e non recupera frequenze
  non misurate dal sensore. Non si dichiarano misure affidabili oltre banda.
- Grafico: modulo XYZ dopo sottrazione della media pretrigger, solo per
  visualizzazione; il modello riceve gli assi originali in g.
- All'avvio verifichiamo progetto, frequenza, numero di valori e assi. Il
  manifest fissa la versione; il runner non espone qui un identificatore
  verificabile della versione del modello.
- Score ottenuto dal runner locale del brick; confronto `score >= soglia`.
  Niente inferenza cloud. Telegram richiede Internet, l'inferenza no, una volta
  scaricati modello e dipendenze necessari.
- Coda RAM limitata a 4 richieste, inferenze serializzate e timeout HTTP.
  Coda piena: il CSV resta salvato e puo essere rianalizzato manualmente.
  Una richiesta in coda interrotta da Stop/Run non viene recuperata automaticamente.
- Soglia e abilitazione LED sono fotografate quando la richiesta viene accodata;
  modificarle non ricalcola gli esiti precedenti.
- Ogni risultato conserva nome e hash SHA256 del CSV di origine, dati
  ricampionati, trasformazione eventuale, score, soglia, tempi ed errori.
  Il tempo esposto include la chiamata HTTP locale, non e solo tempo CPU del modello.
- La dashboard mostra gli ultimi 20 risultati; JSON e CSV restano su disco.
  Gli ultimi score possono riferirsi a eventi diversi: il confronto sulla
  stessa cattura e esplicitamente nel dettaglio del test sintetico.

## File salvati sulla scheda

```text
data/ai/settings.json           # soglia e LED associati al modello
data/ai/inferences.csv          # storico compatto, incluse esclusioni/errori
data/ai/result_<id>.json        # report con forme d'onda e provenienza
data/analysis/inspection_alert.json  # allerta memorizzata, inclusi AI_TEST/AI_ANOMALY
data/raw/<evento>.csv + .json   # acquisizione originale
```

API: `POST /api/ai/settings`, `POST /api/ai/analyze`, `POST /api/ai/synthetic`,
`GET /api/ai/result/{id}`; stato nel campo `ai` di `GET /api/status`.
Le due API di analisi accettano `{"event":"<nome senza estensione>"}`. L'API
sintetica genera la perturbazione descritta; non accetta score arbitrari.

## Se qualcosa non funziona

| Esito | Cosa controllare |
| --- | --- |
| Modello non pronto | Modello scaricato, brick selezionato, log runner in App Lab |
| Modello inatteso | Progetto 1136239, modello 1136239-1, 100 Hz, 600 valori XYZ |
| SKIPPED | Motivo nella riga dello storico; ripetere l'acquisizione dopo READY |
| ERROR / timeout | Log runner; CSV conservato, rianalizzare quando disponibile |
| SOGLIA DA IMPOSTARE | Inserire e salvare il valore letto in Edge Impulse |
| Score oltre soglia ma LED spento | LED AI abilitato nella richiesta, telemetria e firmware D7 |
| LED gia acceso prima del test | Allerta memorizzata: leggere il motivo, poi reset |
| Grafico o pulsanti mancanti | Deploy degli asset, riaprire App e Ctrl+F5 |
| Errore archivio AI | Spazio/permessi; i risultati non sono garantiti persistenti |

## Test sintetici offline

Il generatore produce perturbazioni software di acquisizioni reali del gruppo
test. Non addestra modelli, non esegue inferenza e non dimostra il rilevamento di
danni fisici. Gli originali vengono conservati.

### Generazione

Dalla radice del repository, con Python 3.9 o successivo:

```powershell
python tools/generate_synthetic_impacts.py --input datasets/edge_impulse/demo_test_v1 --output datasets/edge_impulse/demo_synthetic_v1
```

L'output deve essere nuovo: lo script rifiuta sovrascritture. Il lotto di input
deve essere un export SolarEcho di test normale, in g, con il suo report.

### Trasformazioni

Ogni impatto genera tre copie, con parametri fissati prima dell'inferenza:

| Variante | Operazione dopo il trigger |
| --- | --- |
| `attenuated` | Moltiplica per 0,5 lo scostamento dalla media pretrigger, per asse |
| `amplified` | Moltiplica per 2 lo scostamento dalla media pretrigger, per asse |
| `added_oscillation` | Aggiunge su Z una sinusoide a 12 Hz con ampiezza iniziale 0,08 g e decadimento esponenziale di 0,45 s |

Il pretrigger rimane invariato. La media pretrigger rappresenta l'offset iniziale,
comprendente la gravita: non viene moltiplicata. Timestamp, frequenza, durata,
ordine degli assi e unita rimangono quelli dell'export di origine.

La trasformazione oscillatoria e `0.08 * exp(-t/0.45) * sin(2*pi*12*t)`, con
`t` in secondi dal trigger. Non simula una frequenza propria misurata del pannello.
La moltiplicazione modifica anche il rumore e l'eventuale deriva dopo il trigger:
e una perturbazione del segnale, non un modello fisico del danno.

#### Profilo stress per la demo software

```powershell
python tools/generate_synthetic_impacts.py --input datasets/edge_impulse/demo_test_v1 --output datasets/edge_impulse/demo_synthetic_stress_v1 --profile stress
```

Produce una copia per evento, aggiungendo oscillazioni persistenti dopo il
trigger: ampiezza 0,35 g su ciascun asse, frequenze X/Y/Z di 8/17/29 Hz e rampa
iniziale di 50 ms. La formula per asse e
`a_originale + min(1, t/0.05) * 0.35 * sin(2*pi*f*t)`, con `t` in secondi.

Questo profilo e stato aggiunto dopo i risultati delle perturbazioni moderate.
E un nuovo caso dimostrativo deliberatamente distante dalla baseline, non una
prova indipendente di efficacia su alterazioni fisiche. I parametri sono fissati
prima della sua inferenza. Conservare anche i risultati precedenti e riportare
gli eventuali mancati rilevamenti. Il superamento della soglia non e garantito.

Caricare i cinque CSV in `demo_synthetic_stress_v1/test` nel gruppo Testing, con
etichetta `anomaly`. I nomi includono `synthetic_stress_sustained`. Confrontare i
singoli score con quelli dei cinque originali `no anomaly`; non confondere le
metriche aggregate con quelle dei precedenti quindici test sintetici.

I CSV hanno colonne `timestamp,accX,accY,accZ` e prefisso
`anomaly.synthetic_<variante>`. `synthetic_report.json` conserva parametri, hash,
evento di origine e statistiche del segnale originale e alterato. Queste
statistiche sono misure dei file, non score di inferenza AI.

### Uso su Edge Impulse

1. Mantieni il modello addestrato e la soglia attuale.
2. Apri Data acquisition, Upload data.
3. Carica soltanto i CSV in `demo_synthetic_v1/test` nella destinazione Testing.
4. Assegna esplicitamente l'etichetta `anomaly`.
5. Conserva i cinque originali in Testing con etichetta `no anomaly`.
6. Esegui nuovamente Model testing. Apri i risultati per leggere gli score.
7. Confronta ogni variante con il suo originale e riporta anche le trasformazioni
   non riconosciute. Il report permette di risalire alla coppia di origine.

Non spostare le copie nel Training e non modificare la soglia per ottenere un
risultato desiderato su questi test. Se si usano queste copie per scegliere
nuovi parametri, diventano dati di sviluppo: per una valutazione successiva
servono altri eventi separati.

Con cinque originali e tre varianti si ottengono quindici copie sintetiche,
correlate fra loro. Non sono quindici impatti fisici aggiuntivi. Una metrica
aggregata su originali e copie descrive esclusivamente questo insieme di prova.

### Presentazione

Usare la dicitura **TEST SINTETICO - firma alterata artificialmente** nel grafico,
nella dashboard e negli eventuali messaggi. Questa dicitura deve accompagnare
anche un'eventuale accensione del LED nella modalita demo.

Il pulsante di test nella dashboard usa ora lo stesso profilo stress:
[avvio e procedura](AI_INTEGRAZIONE.md). Il generatore resta uno strumento offline
separato. La validazione su alterazioni meccaniche reali
richiede impatti fisici con modifica reversibile e successivo ripristino.

## Riferimenti ufficiali

- [Test e soglie Edge Impulse](https://docs.edgeimpulse.com/studio/projects/model-testing).
- [Deployment su Arduino App Lab](https://docs.edgeimpulse.com/hardware/deployments/run-arduino-app-lab).
- [Brick Vibration Anomaly Detection](https://github.com/arduino/app-bricks-py/blob/main/src/arduino/app_bricks/vibration_anomaly_detection/__init__.py).
- [Facade del runner: API info e features](https://github.com/arduino/app-bricks-py/blob/main/src/arduino/app_internal/core/ei.py).
