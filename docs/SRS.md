# SolarEcho AI - Software Requirements Specification

**Versione:** 0.1  
**Stato:** Bozza per MVP hackTurin 2026  
**Data:** 10 ottobre 2026

## 1. Scopo

SolarEcho AI e un prototipo embedded per il monitoraggio della risposta vibrazionale di un piccolo pannello fotovoltaico. Dopo impatti controllati, il sistema acquisisce l'accelerazione del pannello, confronta la risposta con una baseline locale e segnala una **possibile alterazione meccanica** che richiede ispezione.

Il sistema non rileva ne certifica microfratture, danni strutturali o perdita di efficienza elettrica del pannello.

## 2. Utenti e scenario d'uso

L'utente previsto e un gestore di impianti fotovoltaici o un tecnico di manutenzione. Durante la demo, una pallina leggera viene lasciata cadere da altezza e punto definiti su una superficie protettiva solidale al pannello. Il sistema registra l'evento, ne analizza la firma vibrazionale e ne mostra l'esito.

Due condizioni devono essere confrontabili:

1. configurazione meccanica normale, usata per acquisire la baseline;
2. configurazione con modifica reversibile del supporto, per esempio massa aggiuntiva o fissaggio allentato in modo controllato.

## 3. Ambito dell'MVP

### 3.1 Incluso

- acquisizione locale dell'accelerazione X, Y e Z;
- rilevamento dell'impatto tramite piezo, accelerometro o entrambi;
- raccolta di finestre temporali attorno all'impatto;
- salvataggio locale di campioni, metadati, caratteristiche e risultati;
- addestramento e inferenza offline di un rilevatore di anomalie;
- visualizzazione di stato, contatore e score sull'OLED, quando il display e disponibile;
- dashboard locale opzionale sul computer o sul lato Linux dell'UNO Q;
- confronto quantitativo con una soglia convenzionale basata sulle caratteristiche estratte;
- esportazione di dati sperimentali per GitHub e Devpost.

### 3.2 Escluso

- diagnosi certa di danni interni, microfratture o degrado elettrico;
- inferenza cloud;
- attuatori o servomotori;
- generazione automatica degli impatti;
- autonomia energetica garantita tramite il piccolo pannello solare;
- dati sintetici dichiarati come risultati sperimentali.

## 4. Architettura

```text
Pannello + struttura + pallina
          |
          v
Modulino Movement ----> STM32U585 su UNO Q ----> Bridge/RPC ----> Python su Debian
accelerazione X/Y/Z          |                                      |
                              |                                      +--> preprocessing e feature extraction
Piezo 1, Piezo 2 ------------+                                      +--> modello anomaly detection
trigger o diagnostica                                                +--> CSV, modello, dashboard
                                                                     |
                                                                     v
                                                              OLED / stato demo
```

Lo STM32 gestisce la lettura deterministica dei sensori e la cattura delle finestre. Il processore Linux dell'UNO Q gestisce persistenza, elaborazione dei segnali, addestramento, inferenza e visualizzazione locale.

## 5. Vincoli hardware verificati

| Elemento | Requisito di integrazione |
| --- | --- |
| Arduino UNO Q | MCU STM32U585 per I/O real time e MPU QRB2210 con Debian per Python e modello locale. |
| Modulino Movement | Collegamento al Qwiic dell'UNO Q su `Wire1`, I2C4, 3,3 V. Indirizzo predefinito previsto `0x6A`. |
| I/O UNO Q | GPIO e ADC dello STM32 operano a 3,3 V. Nessun segnale esterno superiore a 3,3 V deve raggiungere un ingresso analogico. |
| ADC | A0-A5 disponibili; risoluzione configurabile fino a 14 bit, riferimento predefinito 3,3 V. |
| Piezo Sensor | Il link nell'inventario identifica il Grove Piezo Vibration Sensor Seeed, con uscita digitale HIGH/LOW. Usarlo come trigger dopo verifica del modulo fisico e dei livelli a 3,3 V. Non usarlo come sorgente di forma d'onda analogica. |
| OLED Grove 0,96 | Il link nell'inventario identifica la variante SSD1315. Verificare la serigrafia e l'indirizzo I2C del pezzo fisico. Il connettore Grove non coincide meccanicamente con Qwiic. |
| Alimentazione MVP | UNO Q alimentato tramite USB-C 5 V / 3 A. L'eventuale alimentazione solare e un sottosistema separato fino a verifica del caricatore Waveshare e del pannello R1123. |

## 6. Requisiti funzionali

| ID | Requisito | Criterio di accettazione |
| --- | --- | --- |
| FR-01 | Il firmware deve inizializzare il Modulino Movement e dichiarare `SENSOR ERROR` se non risponde. | All'avvio viene registrato il risultato dell'inizializzazione; in caso di errore non viene eseguita inferenza. |
| FR-02 | Il firmware deve campionare X, Y e Z con timestamp monotono. | Ogni campione valido contiene `timestamp_us`, `ax_g`, `ay_g`, `az_g`. |
| FR-03 | Il sistema deve misurare e salvare la frequenza effettiva di campionamento. | Ogni sessione contiene frequenza media, minima e massima derivata dai timestamp. |
| FR-04 | Il sistema deve identificare un impatto. | Il trigger puo provenire dal Grove Piezo Vibration Sensor digitale o da una soglia sul modulo dell'accelerazione. La sorgente deve essere salvata. |
| FR-05 | Un singolo impatto non deve essere conteggiato piu volte per rimbalzi e oscillazioni residue. | Dopo un evento e applicato un tempo di lockout configurabile; gli eventuali trigger durante il lockout sono registrati come soppressi. |
| FR-06 | Per ogni impatto accettato il sistema deve salvare una finestra di campioni. | Ogni evento contiene un tratto pre-trigger e un tratto post-trigger configurabili. |
| FR-07 | Il sistema deve consentire la raccolta esplicita di una baseline normale. | Gli eventi della baseline sono etichettati `normal` e associati a una configurazione meccanica nota. |
| FR-08 | Il sistema deve addestrare un modello solo se esiste un numero minimo configurabile di eventi normali validi. | Se il numero e insufficiente, lo stato e `BASELINE INSUFFICIENT`. |
| FR-09 | Il sistema deve salvare e ricaricare modello, scaler, soglia e versione delle caratteristiche. | Dopo il riavvio, un modello compatibile e utilizzabile senza nuovo addestramento. |
| FR-10 | Il sistema deve assegnare a ogni evento confrontabile uno score numerico e uno stato `NORMAL` o `ANOMALY`. | Lo stato `ANOMALY` appare solo quando lo score supera la soglia calibrata. |
| FR-11 | L'avviso deve descrivere una possibile alterazione meccanica e richiesta di ispezione. | Nessuna UI, log o documentazione usa formulazioni che affermano un danno certo. |
| FR-12 | Il sistema deve mostrare almeno contatore impatti, stato e score sul canale di visualizzazione disponibile. | OLED se configurato; log e dashboard locale come fallback. |
| FR-13 | Il sistema deve salvare gli eventi e gli esiti in formato CSV. | I file CSV sono leggibili senza servizi cloud e non contengono credenziali. |

## 7. Requisiti non funzionali

| ID | Requisito |
| --- | --- |
| NFR-01 | Inferenza, dati e modello devono funzionare senza connessione Internet. |
| NFR-02 | Il codice deve separare acquisizione, elaborazione, AI, monitoraggio e visualizzazione. |
| NFR-03 | I parametri sperimentali devono essere configurabili e tracciati insieme ai dati. |
| NFR-04 | Il sistema deve degradare in modo esplicito: errore sensore, baseline insufficiente, errore modello e campione non confrontabile. |
| NFR-05 | I risultati pubblicati devono provenire da prove fisiche reali; i test sintetici devono essere indicati come tali. |
| NFR-06 | Il modello e i dati non devono includere password, token o credenziali. |

## 8. Acquisizione ed eventi

### 8.1 Configurazione iniziale proposta

| Parametro | Valore iniziale | Nota |
| --- | --- | --- |
| Sensore primario | Modulino Movement | La risposta dinamica e letta su X/Y/Z. |
| Frequenza nominale | Da confermare durante il test | La libreria standard deve essere verificata sperimentalmente sul firmware effettivo. |
| Pre-trigger | 100 ms | Conservato nel buffer circolare. |
| Post-trigger | 1.000 ms | Deve includere il decadimento osservabile. |
| Lockout | 800 ms iniziali | Da calibrare sui rimbalzi reali. |
| Intervallo tra prove | >= 2 s | Evita sovrapposizione della risposta residua. |
| Posizione sensore | Fissata e documentata | Non puo cambiare tra baseline e prova. |
| Impatto | Pallina, altezza e punto fissi | Ogni modifica deve essere registrata nei metadati. |

I valori sono parametri iniziali, non risultati sperimentali. Saranno confermati o modificati dopo la prima acquisizione reale.

### 8.2 Formato dei dati grezzi

Ogni riga di campione deve usare un CSV con questa struttura:

```text
session_id,event_id,sample_index,timestamp_us,ax_g,ay_g,az_g,trigger_source,trigger_state
```

Ogni evento deve avere un file metadati o una riga in un indice eventi:

```text
session_id,event_id,event_timestamp_us,label,mechanical_configuration,ball_mass_g,drop_height_cm,impact_position,sensor_position,sample_rate_hz,trigger_source,validity_reason
```

Etichette consentite: `normal`, `modified`, `unknown`, `invalid`. L'etichetta `modified` descrive la configurazione meccanica della prova, non un danno certo del pannello.

## 9. Preprocessing e caratteristiche

Per una finestra di accelerazione `a_x`, `a_y`, `a_z`, il sistema deve calcolare anche il modulo:

```text
a_mag = sqrt(ax^2 + ay^2 + az^2)
```

Il preprocessing minimo e:

1. verificare campioni mancanti, timestamp non monotoni e saturazione;
2. rimuovere l'offset usando il tratto pre-trigger;
3. eventualmente sottrarre la gravita tramite offset locale, senza usare la posizione assoluta come segnale di anomalia;
4. normalizzare la durata della finestra solo quando il campionamento effettivo lo richiede;
5. estrarre le caratteristiche sotto elencate.

| Caratteristica | Uso | Stato MVP |
| --- | --- | --- |
| Picco di `a_mag` | Verifica comparabilita dell'intensita dell'impatto e segnala saturazione. | Inclusa |
| RMS per asse e modulo | Misura l'ampiezza complessiva della risposta. | Inclusa |
| Energia, somma di `a_mag^2` | Riassume la risposta nel tempo. | Inclusa |
| Durata sopra soglia relativa al rumore | Stima quanto persiste la vibrazione. | Inclusa se robusta |
| Tempo di decadimento | Puo cambiare con massa o vincoli diversi. | Inclusa se stimabile |
| Rapporto RMS tra assi | Cattura la direzione relativa della risposta. | Inclusa |
| Frequenza dominante e energia di banda | Informazione utile solo entro la banda realmente campionabile. | Esplorativa, poi inclusa se ripetibile |

La FFT non e un requisito della prima inferenza. Non devono essere interpretate frequenze oltre il limite di Nyquist della frequenza effettiva misurata, ne frequenze attenuate dal filtro configurato nell'IMU.

## 10. Modello di anomaly detection

### 10.1 Modello MVP

Il modello predefinito e **Isolation Forest** su un vettore di caratteristiche normalizzato. Il modello viene eseguito localmente in Python sul lato Linux dell'UNO Q.

Motivazione:

- richiede solo esempi normali per il training;
- e compatto, riproducibile e ispezionabile;
- e appropriato per poche decine di eventi e poche caratteristiche;
- evita una rete neurale sovradimensionata per il dataset iniziale.

Un autoencoder leggero resta un'alternativa di studio solo se saranno raccolti abbastanza eventi normali ripetibili e l'Isolation Forest non separera le prove modificate.

### 10.2 Addestramento e soglia

1. Raccogliere almeno il numero minimo configurato di impatti normali validi; valore iniziale consigliato: 20.
2. Separare gli eventi normali in training e calibrazione, senza usare gli stessi score per scegliere e valutare la soglia.
3. Addestrare lo scaler sulle sole caratteristiche di training.
4. Addestrare Isolation Forest sulle caratteristiche standardizzate.
5. Calibrare la soglia sugli score del gruppo normale di calibrazione, documentando il percentile scelto e il motivo.
6. Salvare modello, scaler, elenco e ordine delle feature, soglia, versione software, parametri di acquisizione e statistiche della baseline.

La soglia non deve essere arbitraria. Una previsione `ANOMALY` indica una risposta non coerente con la baseline acquisita nelle condizioni dichiarate.

### 10.3 Eventi non confrontabili

Un evento deve essere marcato `NOT COMPARABLE`, senza inferenza o con inferenza esclusa dalle metriche, quando almeno una condizione e vera:

- picco molto diverso dall'intervallo della baseline, a indicare un impatto non equivalente;
- finestra incompleta, timestamp irregolari o campioni mancanti;
- sensore non inizializzato o valori non finiti;
- accelerazione saturata;
- configurazione del pannello, del sensore o della pallina diversa da quella della baseline.

## 11. Stati del sistema e UI

| Stato | Significato | Messaggio minimo |
| --- | --- | --- |
| `STARTING` | Inizializzazione in corso. | `SolarEcho AI` |
| `READY` | Sensori validi; nessun modello caricato. | `READY - acquire baseline` |
| `BASELINE INSUFFICIENT` | Dati normali insufficienti per il training. | `Collect normal impacts` |
| `NORMAL` | Ultima risposta coerente con baseline. | `NORMAL / score: ...` |
| `ANOMALY` | Risposta diversa dalla baseline oltre soglia. | `POSSIBLE MECHANICAL CHANGE / Inspect panel` |
| `NOT COMPARABLE` | Impatto o dati non validi per confronto. | `Repeat controlled impact` |
| `SENSOR ERROR` | Uno o piu sensori non disponibili. | `SENSOR ERROR` |
| `MODEL ERROR` | Modello assente, incompatibile o non caricabile. | `MODEL ERROR` |

L'OLED deve evitare messaggi tecnici estesi: stato, numero impatti, score e invito all'ispezione sono prioritari. Il log conserva i dettagli diagnostici.

## 12. Struttura software prevista

```text
SolarEcho-AI/
├── firmware/
│   └── acquisition_sensors/
│       └── acquisition_sensors.ino
├── edge/
│   ├── acquisition/
│   ├── processing/
│   ├── ai/
│   ├── monitoring/
│   └── visualization/
├── datasets/
│   ├── raw/
│   ├── processed/
│   └── README.md
├── models/
├── tests/
├── docs/
│   └── SRS.md
├── requirements.txt
└── README.md
```

La struttura puo essere adattata al formato progetto imposto da Arduino App Lab, mantenendo le responsabilita separate.

## 13. Metriche e validazione

Le metriche devono essere calcolate su prove fisiche registrate e identificabili.

| Metrica | Definizione |
| --- | --- |
| Impatti effettuati | Numero di rilasci manuali registrati nel protocollo. |
| Impatti rilevati | Numero di eventi validi rilevati dal sistema. |
| Tasso di rilevamento | `impatti rilevati / impatti effettuati`. |
| Falsi impatti | Eventi rilevati senza un impatto pianificato. |
| Score normale medio e dispersione | Distribuzione degli score delle prove normali di test. |
| Score configurazione modificata | Distribuzione degli score delle prove con modifica reversibile. |
| Rilevamento anomalie simulate | `prove modified segnalate / prove modified confrontabili`. |
| Falsi allarmi | `prove normal segnalate / prove normal confrontabili`. |
| Tempo inferenza | Tempo dal completamento della finestra alla disponibilita dell'esito. |
| Baseline convenzionale | Stesse metriche ottenute con soglia su RMS o energia. |

Per ciascuna sessione devono essere registrati operatore, data, configurazione meccanica, altezza, punto di impatto, massa della pallina, posizione del sensore e parametri software.

## 14. Protocollo demo

### Scenario A - Pannello normale

1. Fissare pannello e Modulino nella configurazione di baseline.
2. Verificare lo stato `READY` o il modello caricato.
3. Rilasciare la pallina dal riferimento meccanico stabilito.
4. Mostrare incremento del contatore, finestra acquisita e stato `NORMAL` se l'evento e confrontabile.

### Scenario B - Modifica meccanica reversibile

1. Applicare una modifica documentata, per esempio una piccola massa al telaio oppure un fissaggio lievemente allentato.
2. Ripetere lo stesso impatto.
3. Mostrare score e stato. Il risultato e valido come dimostrazione solo se le prove reali indicano una separazione ripetibile.

### Scenario C - Ripristino

1. Ripristinare la configurazione iniziale.
2. Ripetere l'impatto controllato.
3. Registrare se score e stato tornano nella distribuzione della baseline.

## 15. Rischi e mitigazioni

| Rischio | Effetto | Mitigazione |
| --- | --- | --- |
| Frequenza utile insufficiente | Le risonanze rilevanti non vengono osservate. | Misurare frequenza reale; concentrarsi su ampiezza, energia, durata e decadimento osservabili; testare la modifica meccanica prima di impegnare la demo. |
| Variabilita della caduta | Score dominato dalla forza dell'impatto. | Guida meccanica, pallina e altezza fisse; controllo di comparabilita tramite picco; ripetizioni. |
| Sensore fissato in modo non ripetibile | Cambia la risposta senza modifica del pannello. | Fissaggio documentato, posizione marcata, nessuna rimozione tra baseline e prova. |
| Rimbalzi | Piu conteggi per un solo impatto. | Lockout configurabile e analisi degli intervalli tra trigger. |
| Piezo fisico diverso dal modello indicato nell'inventario o uscita non a 3,3 V | Rischio elettrico o interpretazione errata. | Verificare serigrafia e livello di uscita; usare il Grove Piezo digitale solo come trigger. |
| Pochi dati | Modello instabile. | Stato esplicito baseline insufficiente; aumentare le prove; preferire modello a feature semplici. |
| Alimentazione solare insufficiente | Riavvii o instabilita. | USB-C per la demo; sottosistema solare separato e verificato successivamente. |

## 16. Criteri di completamento MVP

L'MVP e pronto per una demo quando tutte le condizioni seguenti sono soddisfatte:

1. il Modulino acquisisce e salva una forma d'onda reale X/Y/Z per un impatto;
2. il sistema conta un singolo impatto una sola volta nel protocollo controllato;
3. esistono baseline, modello e soglia salvati localmente oppure viene mostrato correttamente `BASELINE INSUFFICIENT`;
4. un evento confrontabile produce score e stato senza Internet;
5. il sistema distingue chiaramente `ANOMALY` da una dichiarazione di danno certo;
6. la UI o il log visualizza contatore, stato e score;
7. i risultati numerici della demo provengono dalle sessioni salvate;
8. il test con modifica meccanica viene dichiarato riuscito solo se le misure sperimentali lo supportano.

## 17. Riferimenti

- [Manuale ufficiale UNO Q](https://docs.arduino.cc/tutorials/uno-q/user-manual/) - Riferimento al manuale ufficiale Arduino UNO Q e risorse locali.
- `docs/hardware/datasheets/ABX00162-ABX00173-it-datasheet.pdf` - Datasheet locale Arduino UNO Q.
- `docs/hardware/datasheets/ABX00162-full-pinout.pdf` - Pinout locale Arduino UNO Q.
- [Indice dei componenti e della documentazione scaricata](COMPONENTI.md), inclusi Modulino Movement e Grove Piezo Vibration Sensor identificato dal link dell'inventario.
- [Procedura della prima acquisizione](ACQUISIZIONE_E_SENSORI.md#prima-acquisizione).
