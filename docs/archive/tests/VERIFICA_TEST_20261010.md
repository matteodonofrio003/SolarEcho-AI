# Verifica delle tre condizioni di test

Analisi dei CSV/JSON reali presenti nelle cartelle `datasets/raw/normal_test`,
`modified_test` e `restored_test` il 10 ottobre 2026.
Le condizioni sono quelle assegnate dall'operatore nelle cartelle; non sono
state dedotte dall'ampiezza o dallo score. Questa verifica non esegue il modello.

| Condizione | Acquisizioni iniziali | Rimosse | Mantenute |
| --- | ---: | ---: | ---: |
| Normale | 9 | 1 | 8 |
| Massa aggiunta | 11 | 3 | 8 |
| Ripristino | 8 | 2 | 6 |
| Totale | 28 | 6 | 22 |

## Controlli

Verificati i criteri dell'esportatore: completezza di cattura e trasporto,
assenza di overflow/timeout/eventi aggiuntivi, conteggi coerenti, identita
CSV/JSON, timestamp crescenti, indici consecutivi, valori finiti, pretrigger,
intervallo fra campioni e copertura della griglia a 100 Hz.
Le 22 catture mantenute superano anche la verifica della griglia di
ricampionamento (-150/+1950 ms, 210 campioni). Non sono duplicati dei campioni
in `datasets/raw/normal` o delle altre cartelle di test.

Le registrazioni hanno 229-230 campioni, frequenza media circa 104,12-104,25 Hz
e massimo intervallo fra campioni circa 11,40 ms. Nelle catture mantenute la
risposta dinamica e distinguibile dal rumore precedente all'impatto.
L'ampiezza e variabile: la verifica non dimostra ancora la separazione delle
condizioni da parte del modello.

Alcuni eventi iniziano fino a circa 80 ms prima del trigger piezo. Rimangono
coperti dalla finestra esportata; l'allineamento presenta comunque variabilita.
Diversi trigger piezo raggiungono 16383: l'ADC piezo e saturo. Non si e usata
questa ampiezza per classificare la condizione o invalidare l'IMU.

## Scarti recuperabili

Le coppie seguenti sono state archiviate in
`datasets/rejected/test_labeled_rejected_20261010.zip` prima della rimozione.

| Cartella | Nome base CSV/JSON | Motivo |
| --- | --- | --- |
| normal_test | 20261010_171420_45cdb44c_event_0008 | Cattura marcata incompleta, eventi piezo aggiuntivi |
| modified_test | 20261010_171823_c5ff0f78_event_0003 | Risposta inizia circa 159 ms prima del trigger: l'inizio cade prima della finestra esportata; trigger tardivo, non confrontabile come impatto allineato |
| modified_test | 20261010_171823_c5ff0f78_event_0008 | Cattura marcata incompleta, eventi piezo aggiuntivi |
| modified_test | 20261010_171823_c5ff0f78_event_0010 | Cattura marcata incompleta, eventi piezo aggiuntivi |
| restored_test | 20261010_172537_573d8b4e_event_0004 | Cattura marcata incompleta, eventi piezo aggiuntivi |
| restored_test | 20261010_172537_573d8b4e_event_0008 | Cattura marcata incompleta, eventi piezo aggiuntivi |

Gli eventi aggiuntivi possono derivare da rimbalzi o altri urti: i file da soli
non permettono di stabilire la causa. Questi scarti documentano una limitazione
dell'acquisizione e non devono essere nascosti nel conteggio delle prove fisiche.

## Esportazione e upload

I comandi seguenti riproducono la finestra storica da 210 campioni descritta
in questa verifica, per questo specificano `--end-ms 1950`. Dal 17 ottobre il
valore predefinito del convertitore e +1850 ms (200 campioni), coerente con
il modello corrente: vedere [Export Edge Impulse](../../EDGE_IMPULSE_EXPORT.md).

L'operatore esegue dalla radice del repository:

```powershell
python tools/export_edge_impulse.py --input datasets/raw/normal_test --output datasets/edge_impulse/normal_test_v1 --label normal --split test --end-ms 1950
python tools/export_edge_impulse.py --input datasets/raw/modified_test --output datasets/edge_impulse/modified_test_v1 --label modified --condition modified --split test --end-ms 1950
python tools/export_edge_impulse.py --input datasets/raw/restored_test --output datasets/edge_impulse/restored_test_v1 --label normal --condition restored --split test --end-ms 1950
```

Conteggi attesi: 8, 8, 6 esportati, nessuna esclusione. L'output deve essere una
cartella nuova. Caricare soltanto i CSV delle sottocartelle `test`, in tre lotti
distinti e nella categoria Testing.

Per le metriche automatiche di anomaly detection nello Studio assegnare
manualmente le etichette di upload, senza ricavarle dal prefisso dei file:

- normale: `no anomaly`;
- massa aggiunta: `anomaly`;
- ripristino: `no anomaly`.

La condizione ripristino rimane documentata nel report di esportazione anche
se condivide l'etichetta del normale. I report permettono di risalire dal nome
hash del CSV esportato all'evento originale.

Aprire Model testing e premere Classify all / Test all, poi aprire i singoli
risultati per osservare lo score. Il confronto atteso e uno score piu alto con
la massa e un ritorno verso i normali dopo il ripristino, da verificare.
Usare inizialmente la soglia corrente come provvisoria. Se questi dati vengono
usati per scegliere soglia o caratteristiche, diventano dati di calibrazione:
la valutazione finale richiede nuove prove con modello e soglia fissati.

Riferimento: [Model testing Edge Impulse](https://docs.edgeimpulse.com/studio/projects/model-testing).
Lo Studio richiede esattamente `anomaly` e `no anomaly` per le metriche
automatiche dell'anomaly detection; i nomi normal/modified dell'esportatore
restano etichette locali.
