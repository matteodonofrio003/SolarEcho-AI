# LED rosso: richiesta di ispezione

## Regola implementata

Il LED si accende quando si verifica **una delle due condizioni**:

1. Dopo un riferimento elettrico valido, il contatore piezo registra almeno
   **3 nuovi impatti** e **5 nuove letture consecutive** dell'INA219 indicano
   una potenza inferiore di almeno **20%** rispetto al riferimento.
2. Un futuro modello locale restituisce uno score oltre la sua soglia calibrata
   per una cattura confrontabile. Questa condizione non richiede 3 impatti.

Numero di impatti, percentuale e letture consecutive sono modificabili nella
dashboard. **3 / 20% / 5 sono valori iniziali per la demo, non soglie validate**.
Il conteggio usa gli eventi accettati dal firmware, dopo isteresi e lockout:
verificare che corrispondano ai colpi realmente effettuati.

L'AI resta sospesa: la seconda condizione dispone del collegamento software,
ma non viene generata alcuna inferenza finche non integriamo un modello reale.

L'allerta significa **"Ispezione consigliata"**. Ombra, variazioni della luce,
carico o comportamento del charger possono cambiare la potenza. La sequenza
impatti + calo non dimostra che gli impatti abbiano danneggiato il pannello.

## Collegamento del LED esterno

Per un comune LED rosso a due terminali, a scheda disalimentata:

```text
UNO Q D3 ── resistenza 1 kohm ── anodo LED rosso
                                     catodo ── UNO Q GND
```

- Anodo: normalmente il terminale lungo.
- Catodo: normalmente il terminale corto e il lato piatto del contenitore;
  se i terminali sono stati tagliati, verificare la polarita del componente.
- La resistenza e **in serie**, non in parallelo.
- D3 e un'uscita a 3,3 V: non collegare il LED al 5 V.
- Per un LED con caduta diretta di circa 2 V, la corrente e circa
  `(3,3 - 2) / 1000 = 1,3 mA`; il valore effettivo dipende dal LED.
- Questo schema riguarda un LED indicatore semplice; moduli e LED di potenza
  richiedono la verifica della loro documentazione.

D3 corrisponde a PB0 sull'header digitale secondo il
[manuale ufficiale Arduino](https://docs.arduino.cc/resources/datasheets/ABX00162-ABX00173-datasheet.pdf)
e il [manuale locale](UM.md). Il dimensionamento a bassa corrente e coerente
con le caratteristiche GPIO del
[datasheet STM32U585, sezione caratteristiche di uscita](https://www.st.com/resource/en/datasheet/stm32u585ai.pdf).

Lo sketch replica la segnalazione sul **segmento rosso del LED RGB integrato
numero 3**, `LED3_R`, attivo LOW. Puoi quindi fare la prima prova senza LED
esterno. Gli altri segmenti di quel LED sono spenti. Il controllo del LED
integrato e documentato nel [manuale Arduino](UM.md).

## Prova passo per passo

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

## Stato, reset e salvataggio

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

## Collegamento futuro al modello AI

Nel loop di elaborazione, dopo un'inferenza reale e la verifica di qualita:

```python
inspection.on_ai_result(float(score), float(calibrated_threshold), event_name,
                        comparable=capture_complete)
```

`calibrated_threshold` deve provenire dalla validazione del modello; non usare
la soglia di calo elettrico. Uno score non finito o una cattura non confrontabile
non genera una richiesta di ispezione. Uno score normale non cancella un'allerta
precedente. La chiamata va eseguita nel processamento Python, non nel callback
di acquisizione. Non e esposta una API per simulare una classificazione AI.

## Verifiche affidate al team

Codice e test non sono stati eseguiti in questa modifica. Verificare sul banco:

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
