# Verifica acquisizioni di test del 10 ottobre 2026

Cartella analizzata: `datasets/raw/modified_test`. Conteneva 24 coppie CSV/JSON.
Sono state rimosse 11 coppie; rimangono 13 catture complete. Gli scarti sono
recuperabili da `datasets/rejected/modified_test_rejected_20261010.zip`.

## Metodo

Verificati i criteri di `tools/export_edge_impulse.py`: cattura e trasporto
completi, nessun overflow/timeout/evento aggiuntivo, conteggi e identita coerenti,
indici consecutivi, timestamp crescenti, accelerazioni finite e copertura della
griglia di esportazione a 100 Hz. Non sono stati eseguiti firmware, deployment
o test hardware.

Le registrazioni hanno 229-230 campioni e frequenza media circa 104,16-104,25 Hz.
Il massimo intervallo fra campioni e circa 11,03 ms; non sono emersi buchi di
campionamento superiori al limite di 30 ms dell'esportatore.

Per esaminare l'allineamento si e calcolata la norma della differenza dei tre
assi rispetto alla mediana del pretrigger. Sono state confrontate anche le
porzioni -200/-100 ms, -100/0 ms e successive al trigger. L'ampiezza diversa
dalla baseline non e stata usata come criterio di esclusione: potrebbe essere
proprio l'effetto della modifica meccanica.

## Acquisizioni rimosse

| Nome base CSV/JSON | Motivo |
| --- | --- |
| 20261010_165054_8a9bef27_event_0001 | Forte vibrazione gia presente dall'inizio della finestra: manca il riposo precedente all'impatto |
| 20261010_165054_8a9bef27_event_0005 | capture_complete=false, evento piezo aggiuntivo |
| 20261010_165054_8a9bef27_event_0006 | capture_complete=false, evento piezo aggiuntivo |
| 20261010_165054_8a9bef27_event_0007 | capture_complete=false, eventi piezo aggiuntivi |
| 20261010_165054_8a9bef27_event_0008 | capture_complete=false, eventi piezo aggiuntivi |
| 20261010_165359_ea967bbf_event_0003 | capture_complete=false, evento piezo aggiuntivo |
| 20261010_165359_ea967bbf_event_0004 | capture_complete=false, evento piezo aggiuntivo |
| 20261010_165359_ea967bbf_event_0008 | Nessuna risposta d'impatto presso il trigger; picco della vibrazione a circa +632 ms, non confrontabile con gli impatti allineati della baseline |
| 20261010_165359_ea967bbf_event_0009 | capture_complete=false, evento piezo aggiuntivo |
| 20261010_165359_ea967bbf_event_0010 | capture_complete=false, evento piezo aggiuntivo |
| 20261010_165359_ea967bbf_event_0013 | capture_complete=false, evento piezo aggiuntivo |

## Acquisizioni mantenute

- Sessione `20261010_165054_8a9bef27`: eventi 0002, 0003, 0004.
- Sessione `20261010_165359_ea967bbf`: eventi 0001, 0002, 0005, 0006, 0007,
  0011, 0012, 0014, 0015, 0016.

Due acquisizioni richiedono una conferma dell'operatore:

- `20261010_165054_8a9bef27_event_0002`: picco dinamico posttrigger circa
  0,024 g, RMS nei primi 500 ms circa 0,005 g.
- `20261010_165359_ea967bbf_event_0005`: picco dinamico posttrigger circa
  0,021 g, RMS nei primi 500 ms circa 0,008 g.

La risposta debole non dimostra un falso trigger: confermare se e stata
effettuata una caduta e quale condizione fisica era presente. L'evento 0012
della seconda sessione mostra inoltre oscillazione residua nel pretrigger;
controllare se il pannello era fermo prima della caduta.

In alcune catture il segnale inizia poche decine di millisecondi prima del
trigger piezo, ma resta contenuto nella finestra esportata (-150/+1950 ms).
Questo e un limite dell'allineamento da verificare nella valutazione.

## Condizioni fisiche ancora da associare

CSV e JSON non indicano se la massa era presente. Tutti i file sono mescolati
nella cartella `modified_test`: non e possibile assegnare correttamente
normal, modified e restored dal solo segnale. Chiedere all'operatore gli
intervalli di eventi per ciascuna sessione, includendo gli ID rimossi nel
conteggio originale. Non esportare l'intera cartella con etichetta modified.

I conteggi sopra misurano la qualita delle acquisizioni. Non sono metriche di
accuratezza del modello o prova della rilevabilita della massa aggiunta.
