# Acquisizione e sensori

Guida unica per Modulino Movement, piezo analogico e INA219. Per ogni impatto
il firmware conserva **200 ms prima del trigger e 2 s dopo**, poi trasferisce
i campioni a Python per salvataggio e analisi locale. Per dati e limiti dell'AI
vedere la [scheda del modello](MODEL_CARD.md).

## Collegamenti

Alimentare UNO Q da USB-C e spegnere la scheda prima di modificare i collegamenti.
Usare il [pinout UNO Q](hardware/datasheets/ABX00162-full-pinout.pdf), lo
[schema elettrico](hardware/design/SolarEcho-AI-schematic_schem.jpg) e la
[vista breadboard](hardware/design/SolarEcho-AI-schematic_bb.jpg).

| Componente | Collegamento e ruolo |
| --- | --- |
| Modulino Movement | Qwiic, bus `Wire1` a 3,3 V; misura accelerazione X/Y/Z in `g` |
| Piezo passivo a due fili | Uscita del circuito di condizionamento su A0, riferimento GND; trigger e diagnostica |
| INA219 | Bus `Wire`, SDA/D20 e SCL/D21; tensione e corrente sul ramo misurato |

Fissare il Modulino sempre nello stesso punto e orientamento, solidale al
pannello o alla struttura. Non colpire direttamente il sensore. Per una prova
con la sola IMU, lasciare il piezo scollegato e tenere A0 a GND; la cattura
automatica richiede il trigger. L'OLED non fa parte del firmware corrente.

## Piezo analogico e protezione

La resistenza da **1 MΩ in parallelo** scarica il piezo, ma non limita da sola
i picchi. L'ingresso deve restare fra **0 e 3,3 V**: il circuito esterno deve
limitare la corrente e proteggere da tensioni positive e negative, usando
componenti identificati e dimensionati per l'ADC. Il software non protegge il pin.
Verificare il segnale condizionato con un oscilloscopio, se disponibile;
un multimetro può non mostrare i picchi brevi.

Il firmware assume un segnale riferito a GND e prossimo a zero a riposo.
Il piezo passivo non va alimentato come un modulo VCC/GND/OUT. Un bias a
1,65 V richiederebbe soglie e trattamento del segnale differenti. Questa
configurazione non registra fedelmente entrambe le semionde del piezo.
Il modulo Grove digitale valutato inizialmente non viene utilizzato.

### Lettura e contatore

- ADC a 14 bit, valori 0–16383, riferimento predefinito 3,3 V.
- Polling con obiettivo di 1000 µs fra letture, senza temporizzazione hardware:
  I2C e scheduling possono aumentare gli intervalli e far perdere impulsi brevi.
- Soglie diagnostiche ON=512 e OFF=256, circa 103 e 52 mV nominali:
  **da calibrare sul montaggio**, distinte dalla soglia di anomalia AI.
- Un attraversamento ON incrementa `RAW`; un nuovo fronte richiede prima
  il ritorno sotto OFF. Lockout di 800 ms fra eventi accettati in `EVENTS`;
  attraversamenti durante il lockout incrementano `SUPPRESSED`.
- Un ulteriore evento accettato durante la cattura incrementa il contatore
  e rende la finestra inutilizzabile per la baseline, senza crearne una seconda.
- Polling sospeso durante trasferimento e attesa dell'ACK: attendere **READY**.

Un valore zero non distingue il riposo da un sensore scollegato. Un ADC
saturo segnala una possibile uscita fuori scala e richiede verifica hardware.

### Monitor seriale LIVE

Stampa a 5 Hz, sospesa durante cattura e trasferimento. Esempio di formato,
**non risultato sperimentale**:

```text
LIVE AX=0.0100 AY=-0.0200 AZ=0.9900 g | ADC=12 PEAK=780 ACTIVE=0 RAW=3 EVENTS=1 SUPPRESSED=2
```

`ADC` è l'ultima lettura; `PEAK` il massimo dall'ultima stampa; `ACTIVE` lo
stato con isteresi. `RAW` conta attraversamenti software, non fronti catturati
da interrupt. I contatori ripartono al riavvio del firmware.

## INA219 e misura elettrica

Configurazione confermata dal team: INA219 sui pin SDA/SCL, shunt **R100 = 0,1 Ω**,
inserito **fra pannello e charger**. Annotare modello del breakout, corrente
ammissibile dello shunt e modello esatto del caricatore.

| INA219 | UNO Q |
| --- | --- |
| VCC | 3V3, se il breakout supporta alimentazione diretta a 3,3 V |
| GND | Negativo comune del circuito di misura |
| SDA | SDA / D20 |
| SCL | SCL / D21 |

I pull-up I2C devono portare SDA/SCL a 3,3 V. Non usare A4/A5 come sostituti
dei pin SDA/SCL. VCC alimenta il chip, non è il morsetto della tensione misurata.
L'indirizzo configurato è `0x40`: A0/A1 **del chip INA219** a GND; per un altro
indirizzo modificare `kIna219Address` nello sketch. Il Modulino resta su `Wire1`.

```text
Pannello + ---- VIN+ [INA219, shunt R100] VIN- ---- ingresso solare + charger
Pannello - ------------------------------------ ingresso solare - charger
                      GND INA219 e UNO Q sul negativo comune
```

VIN+ e VIN- sono due punti sul ramo positivo, non i poli positivo e negativo
del pannello. Confrontare il cablaggio con la documentazione del charger.
Se si sposta il sensore fra charger e batteria, i valori descrivono quel ramo.
Il verso VIN+ → VIN- determina la corrente positiva; il segno viene conservato
anche nella potenza. Piccole letture vicino allo zero risentono dell'offset:
non dimostrano da sole corrente inversa. Non azzerare una corrente reale di carica.

### Monitor seriale POWER

Attendere il messaggio iniziale `INA219: Wire/SDA/SCL ... R_SHUNT=0.100`
e le righe `POWER`, indicativamente a 1 Hz fuori dalla cattura.

| Campo | Significato |
| --- | --- |
| `t_ms` | Tempo firmware alla lettura dei registri |
| `V_IN` / `V_OUT` | Tensioni VIN+ / VIN- rispetto a GND, in V |
| `SHUNT` | Caduta VIN+ meno VIN-, in mV |
| `I` | Corrente nel ramo, in mA: `I_A = Vshunt_V / Rshunt_ohm` |
| `P_IN` / `P_OUT` | `V_IN * I_A` / `V_OUT * I_A`, in W |

Il driver usa tensione bus e shunt, non i registri interni corrente/potenza
o tensioni nominali. Avvia una conversione singola con media di 16 campioni
per canale, controllata senza `delay`. Una conversione in corso all'impatto
viene scartata; letture e stampa riprendono dopo il ciclo CSV.
I valori elettrici hanno uno [storico separato](DASHBOARD.md#storico-elettrico-automatico).

Errori I2C, configurazione o timeout producono `POWER SENSOR ERROR` e un nuovo
tentativo dopo 5 s. Misure fuori range non vengono pubblicate come valide.
Il chip ha limite di 26 V: il FSR ADC di 32 V non autorizza l'applicazione di
32 V. Corrente e dissipazione ammissibili dipendono anche da breakout e shunt.

## Prima acquisizione

1. Completare e verificare cablaggio e protezioni. Mantenere ripetibili
   fissaggio, sensori, pallina, altezza e punto di caduta.
2. Seguire [Deploy](DEPLOY.md), riaprire l'app e configurare i brick prima di
   **Run**. Non mescolare sketch e Python appartenenti a revisioni differenti.
3. Attendere **READY** in console o Serial Monitor; effettuare un solo impatto.
4. Attendere `BUSY`, `CSV:`, `cattura completa: True` e il successivo **READY**.
   La durata completa del ciclo va misurata sul banco; il trasferimento
   interrompe il monitoraggio degli impatti.
5. Copiare **CSV e JSON insieme** da `data/raw/` della app sulla UNO Q.
   Annotare condizione, altezza, punto, fissaggio e posizione del sensore.
6. Controllare il grafico e i metadati prima di usare l'evento come baseline.
   Per modello e soglia seguire [Integrazione AI](AI_INTEGRAZIONE.md).

Python conferma il salvataggio al firmware prima del riarmo. Un errore di
scrittura sospende le nuove catture; un trasferimento fermo per 10 s produce
file diagnostici incompleti. Il firmware sospende le catture se non riceve
conferma entro 15 s. Correggere il problema e riavviare l'app.

## Formato e controllo dei CSV

Un record per campione nuovo dell'IMU; nome `<sessione>_event_0001.csv` e JSON
dello stesso nome:

```text
session_id,event_id,sample_index,timestamp_us,ax_g,ay_g,az_g,trigger_source,trigger_state,piezo_threshold_crossings,piezo_event_count,piezo_adc,piezo_peak_adc,piezo_timestamp_us,piezo_max_gap_us,capture_complete
```

- `timestamp_us`: tempo firmato dell'accelerazione rispetto al trigger,
  negativo prima dell'evento. Lo zero è l'attraversamento della soglia piezo,
  che può avvenire dopo il primo contatto meccanico.
- `ax_g`, `ay_g`, `az_g`: accelerazioni in `g` secondo la libreria Arduino.
- `piezo_timestamp_us`: tempo dell'ultima lettura ADC rispetto allo stesso trigger;
  `piezo_adc` non è necessariamente simultaneo all'IMU.
- `piezo_peak_adc`: massimo dall'ultimo record IMU o dall'inizio della cattura.
- `piezo_max_gap_us`: massimo intervallo fra letture ADC nello stesso periodo;
  zero se non sono ancora disponibili due letture.
- `trigger_source=piezo_analog`; `trigger_state` è lo stato con isteresi.
- Il JSON contiene conteggi, copertura, frequenza effettiva, overflow, timeout,
  eventi aggiuntivi e motivi di esclusione. `transport_complete` riguarda la
  consegna; `capture_complete` include anche i controlli di qualità.

Il CSV non è una forma d'onda piezo a 1 kHz: non contiene tutte le letture
ADC. La firma vibrazionale principale è l'accelerazione del Modulino.
Il gate iniziale di 30 ms sugli intervalli IMU non è una soglia di anomalia.
Non usare per training le catture incomplete.

## Verifiche e stato

- Osservare almeno 30 s a riposo: contatori stabili e rumore piezo sotto soglia.
- Confrontare cadute fisiche, `EVENTS` e CSV salvati; controllare rimbalzi,
  saturazione e `piezo_max_gap_us`.
- Attendersi circa 229–230 campioni in 2,2 s alla frequenza nominale di 104 Hz,
  verificando sempre timestamp, frequenza reale, intervalli e copertura.
  `available()`, I2C e scheduling determinano il campionamento effettivo.
- Confrontare picco e decadimento con il rumore pretrigger. Se non si distinguono,
  migliorare l'acquisizione prima di addestrare il modello.
- Per INA219 confrontare la tensione con un multimetro sullo stesso punto;
  variare l'illuminazione mantenendo fissi carico e cablaggio. Una batteria
  carica o un charger che non assorbe possono mantenere bassa la corrente.

Log storici del team mostravano picchi piezo a riposo fino a circa 121 ADC
e impulsi circa 3879–9768 ADC, con `EVENTS` arrivato a 6. Non forniscono un
conteggio indipendente dei lanci o una verifica delle protezioni. Le evidenze
successive sono riassunte in [Demo e risultati](DEMO_E_RISULTATI.md).

Il refactoring corrente del logger è stato controllato staticamente; esecuzione
dei test aggiornati e prova sulla scheda restano al team. Comando software,
con soli dati sintetici e senza hardware:

```powershell
python -B -m unittest discover -s tests -p "test_event_logger.py" -v
```

I test coprono eventi consecutivi, timestamp, campioni mancanti, ulteriori
impatti, duplicati, timeout, salvataggio e ACK. Il profilo delle librerie è in
`app/sketch/sketch.yaml`. Per una compilazione senza upload sulla scheda:

```sh
arduino-cli compile --fqbn arduino:zephyr:unoq --profile default /percorso/dello/sketch
```

## Fonti tecniche

- [Manuale ufficiale UNO Q](https://docs.arduino.cc/tutorials/uno-q/user-manual/).
- [Datasheet UNO Q](hardware/datasheets/ABX00162-ABX00173-it-datasheet.pdf).
- [Filesystem delle app](https://docs.arduino.cc/tutorials/uno-q/debian-guide/).
- [API Arduino_Modulino](https://github.com/arduino-libraries/Arduino_Modulino/blob/main/docs/api.md).
- [ModulinoMovement](https://github.com/arduino-libraries/Arduino_Modulino/blob/main/src/Modulino.h).
- [Bridge Python](https://github.com/arduino/app-bricks-py/blob/main/src/arduino/app_utils/bridge.py).
- [Protezione di un ingresso piezo, discussione TI](https://e2e.ti.com/support/amplifiers-group/amplifiers/f/amplifiers-forum/552302/connect-a-piezoelectric-sensor-to-tlv2772-opamp).
- [Datasheet INA219](hardware/datasheets/INA219-datasheet.pdf), sezioni 8.5 e 8.6.
- [Wire del core Zephyr](https://github.com/arduino/ArduinoCore-zephyr/blob/main/libraries/Wire/Wire.h).
