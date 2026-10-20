# Scheda del modello AI

Aggiornamento: **17 ottobre 2026**. Stato: modello integrato in un prototipo
sperimentale; validazione sulle alterazioni meccaniche reali da completare.

## Scopo e identità

| Campo | Valore documentato |
| --- | --- |
| Progetto | SolarEcho AI, monitoraggio vibrazionale di un pannello fotovoltaico |
| Destinatari | Gestori di impianti e tecnici di manutenzione |
| Modello configurato | `ei-model-1136239-1` |
| Progetto Edge Impulse | `1136239` |
| Integrazione | Brick Arduino App Lab `arduino:vibration_anomaly_detection` |
| Esecuzione | Runner locale sul lato Linux della UNO Q; acquisizione sullo STM32 |
| Uscita utilizzata | Score numerico di anomalia restituito dal runner |
| Uso previsto | Segnalare uno scostamento da approfondire con un'ispezione |

Il modello non certifica danni, microfratture, sicurezza del pannello o perdita
di produzione. Una risposta normale non esclude un danno.

L'identificativo è fissato nel [manifest dell'app](../app/app.yaml) e nel
[worker AI](../app/python/vibration_ai.py). Il codice verifica progetto,
frequenza, numero di valori e assi del runner; non ottiene un hash verificabile
del modello installato. La versione effettiva va quindi controllata anche in
App Lab.

## Dati predisposti per il modello corrente

Il lotto demo contiene impatti indicati dal team come normali, della stessa
sessione di acquisizione. Sono stati preparati questi gruppi di eventi interi:

| Gruppo | Eventi | Cartella grezzi | Export |
| --- | ---: | --- | --- |
| Training | 18 | `datasets/raw/demo_normal_training/` | `demo_training_v1` |
| Calibrazione | 5 | `datasets/raw/demo_normal_calibration/` | `demo_calibration_v1` |
| Test normale | 5 | `datasets/raw/demo_normal_test/` | `demo_test_v1` |

I gruppi seguono l'ordine temporale: primi 18, successivi 5, ultimi 5.
Non condividono eventi. Tre eventi esclusi rimangono archiviati; gli hash e le
assegnazioni sono nel [report dello split](../datasets/manifests/archive/demo_split_report.json).
Gli [export disponibili](../datasets/README.md) non dimostrano da soli quali
campioni siano stati effettivamente inclusi in una specifica esecuzione di training.

Sono disponibili anche raccolte precedenti e test con massa/ripristino,
documentati separatamente. I loro export storici da 210 campioni non sono
intercambiabili con l'input corrente da 200 campioni.

Il repository non contiene uno snapshot completo della configurazione
dell'impulso, degli iperparametri e del rapporto di training della versione
installata. Non permette quindi di ricostruire integralmente l'addestramento
o confermare qui l'architettura interna del modello. L'app Python prepara i
segnali e interroga il runner; non addestra un Autoencoder locale.

## Contratto dell'input

| Proprietà | Valore |
| --- | --- |
| Sensore principale | Accelerometro XYZ del Modulino Movement |
| Ruolo del piezo | Trigger e diagnostica; non è l'ingresso vibrazionale del modello |
| Unità | Accelerazione in `g`, con offset e gravità conservati |
| Frequenza AI | 100 Hz |
| Finestra | `[-150, +1850)` ms rispetto al trigger, estremo finale escluso |
| Dimensione | 200 campioni XYZ = 600 valori |
| Ordine | `X0, Y0, Z0, X1, Y1, Z1, …` |
| Ultimo campione | +1840 ms dal trigger |
| Timestamp nel CSV Edge Impulse | Da 0 a 1990 ms; trigger a 150 ms |

Il firmware registra circa 200 ms prima e 2 s dopo il trigger. La finestra AI
è ricavata dai timestamp acquisiti tramite interpolazione lineare, senza
estrapolazione. Export e inferenza condividono
[signal_processing.py](../app/python/signal_processing.py) e usano 10 cifre
significative per i valori degli assi. Il preprocessing esterno al modello
non sottrae l'offset e non normalizza l'ampiezza.

Vengono controllati completezza CSV/JSON, identità e conteggi, indici,
timestamp crescenti, valori finiti, copertura e assenza di ulteriori eventi.
Sono richiesti intervalli IMU non superiori a 30 ms e frequenza acquisita
sufficiente per la griglia, con tolleranza dell'1% nel confronto fra frequenze.
Gli input non idonei vengono esclusi dall'inferenza con esito `SKIPPED`.

L'interpolazione non è un filtro antialias. La frequenza di input di 100 Hz
non certifica una banda utile del sensore fino a 50 Hz. Il grafico può usare
una sottrazione dell'offset per leggibilità: questo non modifica l'input AI.

## Score, soglia e risposta

- Il runner restituisce uno score che può anche essere negativo: non è una
  percentuale di danno o una probabilità.
- La decisione implementata è `score >= soglia → ANOMALY`; altrimenti `NORMAL`.
- La soglia è configurabile e salvata localmente, associata al modello.
  Senza soglia lo stato è `UNCALIBRATED`: lo score non genera un'allerta AI.
- La demo registrata mostra **0,3000**. Questo valore non è presentato come
  soglia ottimale o validata per impianti reali. L'app non lo imposta come
  valore predefinito e non lo sincronizza automaticamente con Edge Impulse.
- Soglia e abilitazione allerta vengono registrate quando la richiesta entra
  in coda; un successivo cambio non riclassifica gli esiti precedenti.
- Se abilitata, l'allerta può accendere il LED D7 e rimane memorizzata fino al
  reset. Telegram parte soltanto da una richiesta manuale della dashboard.

Per una soglia utilizzabile occorre un lotto di calibrazione rappresentativo;
la valutazione finale richiede eventi nuovi, con soglia e modello già fissati.

## Valutazione ed esempi sintetici

La [pagina Demo e risultati](DEMO_E_RISULTATI.md) distingue le evidenze fisiche
dagli esempi di inferenza. Non è disponibile qui una valutazione aggregata
indipendente della sensibilità alle alterazioni meccaniche o dei falsi allarmi.
L'esempio reale mostrato nel video supera già la soglia: non prova una corretta
separazione fra impatti normali e anomali.

Il test sintetico della dashboard aggiunge, dopo il trigger, una perturbazione
persistente di ampiezza 0,35 g per asse, frequenze X/Y/Z 8/17/29 Hz e rampa di
50 ms. Il profilo `stress_sustained` è stato introdotto dopo le perturbazioni
moderate, che non erano sempre riconosciute: è un caso dimostrativo deliberato,
non una valutazione indipendente né un modello fisico del danno.

I sintetici rimangono distinti dai dati reali, non sono impatti aggiuntivi e
non devono entrare nel training normale. Il relativo motivo di allerta è
`AI_TEST`; quello per una cattura reale è `AI_ANOMALY`. Il CSV originale resta
intatto. Parametri e limiti sono nella [guida ai test sintetici](AI_INTEGRAZIONE.md#test-sintetici-offline).

## Limiti e tracciabilità

- Dataset piccolo, sessione unica per il lotto demo, senza prova di
  generalizzazione ad altri pannelli, montaggi o condizioni ambientali.
- Forza e posizione dell'impatto, fissaggio e orientamento del sensore possono
  cambiare lo score. Saturazione e banda limitata possono nascondere informazioni.
- Durante il trasferimento del buffer il firmware non monitora nuovi impatti.
- L'inferenza è serializzata in un worker; la coda RAM ha capacità 4. Un evento
  non accodato conserva il CSV per una successiva analisi manuale.
- I risultati delle inferenze completate conservano origine reale/sintetica, evento e hash del CSV,
  modello configurato, finestra, score, soglia, decisione ed eventuali errori.
- `inference_ms` misura la chiamata al runner HTTP locale, non solo il calcolo
  del modello. Non comprende l'intero tempo dal lancio all'allerta.
- Il refactoring successivo alla demo è stato controllato staticamente;
  test aggiornati e verifica sulla scheda restano da eseguire dal team.

Per avvio, percorsi dei report e gestione degli errori:
[Integrazione AI](AI_INTEGRAZIONE.md).
