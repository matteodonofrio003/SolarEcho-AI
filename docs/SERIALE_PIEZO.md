# Stampa seriale Modulino e piezo analogico

La versione nel repository usa un **piezo a due fili su A0**, attraverso un circuito di protezione. Il Grove digitale su D2 non viene piu letto. Sketch e Python vanno aggiornati insieme: il formato RPC e CSV e cambiato.

## Prima del collegamento

La resistenza da **1 Mohm in parallelo ai due fili** scarica il piezo. Non garantisce che i picchi rientrino nel range dell'ADC. Il piezo puo generare tensioni positive e negative: **non collegare il solo piezo con questa resistenza direttamente ad A0**.

L'UNO Q richiede un segnale analogico tra **0 e 3,3 V**. Serve un circuito esterno che limiti la corrente e protegga l'ingresso da entrambe le polarita, dimensionato in base al piezo e ai diodi realmente disponibili. Identificare le sigle dei diodi prima di definire il circuito. Un multimetro puo non mostrare i picchi brevi: verificare il segnale condizionato con un oscilloscopio, se disponibile.

Il firmware diagnostico assume un segnale **riferito a GND, prossimo a zero a riposo**, con la parte negativa gestita dal circuito di protezione. Non alimentare il piezo passivo come un modulo VCC/GND/OUT. L'uscita del condizionamento va ad A0 e il suo riferimento a GND. Una polarizzazione a 1,65 V richiedera soglie e preprocessing differenti. Questa versione non acquisisce fedelmente entrambe le semionde e non usa il piezo per una FFT.

Spegnere la scheda prima di modificare i collegamenti. Il Modulino resta sul Qwiic, `Wire1`.

## Lettura e contatore

- ADC a 14 bit: valori da 0 a 16383, riferimento predefinito 3,3 V.
- Polling con obiettivo di un campione ogni 1000 us. Non e un'acquisizione hardware temporizzata; I2C e altre operazioni possono allungare gli intervalli e far perdere impulsi brevi.
- Soglia diagnostica ON = 512 e OFF = 256, circa 103 e 52 mV nominali. Sono valori iniziali **da calibrare sui dati reali**, non soglie di anomalia AI.
- Un attraversamento della soglia ON incrementa RAW; per riarmare il rilevatore il valore deve tornare sotto OFF.
- Lockout di 800 ms fra eventi accettati; ulteriori attraversamenti incrementano SUPPRESSED.
- Il polling analogico viene sospeso durante il trasferimento dei campioni via Bridge. Gli impatti in questa fase possono essere persi.

L'ingresso a zero non distingue un sensore scollegato da un sensore a riposo. Un ADC saturo puo indicare un segnale fuori scala, ma il software non puo proteggere il pin.

## Stampa seriale

La console del firmware/Serial Monitor di App Lab mostra X/Y/Z in g e il piezo a 5 Hz. La stampa e sospesa durante cattura e trasferimento.

Esempio di formato, **non risultato sperimentale**:

```text
LIVE AX=0.0100 AY=-0.0200 AZ=0.9900 g | ADC=12 PEAK=780 ACTIVE=0 RAW=3 EVENTS=1 SUPPRESSED=2
```

`ADC` e l'ultima lettura; `PEAK` e il massimo osservato dall'ultima stampa. RAW conta attraversamenti di soglia software, non fronti catturati da interrupt. I contatori ripartono al riavvio del firmware.

## CSV

La cattura manuale dura 6 secondi e salva un record per campione nuovo dell'IMU:

```text
session_id,event_id,sample_index,timestamp_us,ax_g,ay_g,az_g,trigger_source,trigger_state,piezo_threshold_crossings,piezo_event_count,piezo_adc,piezo_peak_adc,piezo_timestamp_us,piezo_max_gap_us
```

- `timestamp_us`: timestamp dell'accelerazione relativo all'inizio della finestra.
- `piezo_timestamp_us`: timestamp dell'ultima lettura ADC, relativo allo stesso inizio.
- `piezo_adc`: ultima lettura ADC; non necessariamente simultanea all'IMU.
- `piezo_peak_adc`: massimo ADC osservato dall'ultimo record IMU (o dall'inizio della cattura).
- `piezo_max_gap_us`: massimo intervallo fra letture ADC nello stesso periodo; zero se non ci sono ancora due letture.
- `trigger_state`: stato del rilevatore con isteresi; la sorgente della finestra resta `manual_window`.

Il CSV **non contiene tutti i campioni del polling ADC** e non e una forma d'onda piezo a 1 kHz. La forma d'onda principale resta l'accelerazione del Modulino. Per una forma d'onda piezo completa servira una cattura dedicata con tempi verificati.

## Verifica sul banco

1. Completare e verificare le protezioni hardware prima di caricare questa versione.
2. Eseguire `deploy.ps1`, riaprire l'App e premere Run.
3. A riposo misurare rumore ADC e picchi: i contatori devono restare stabili.
4. Fare piccoli impatti controllati distanziati di almeno 2 s; confrontare cadute fisiche ed EVENTS.
5. Calibrare ON/OFF sopra il rumore; verificare rimbalzi e lockout. Controllare `piezo_max_gap_us` e saturazione nei CSV.

Non sono ancora disponibili risultati sperimentali del piezo analogico. Le precedenti prove di compilazione/acquisizione con la versione digitale non validano questa versione.

## Fonti

- [Datasheet ufficiale UNO Q: limiti degli ingressi analogici](https://docs.arduino.cc/resources/datasheets/ABX00162-ABX00173-datasheet.pdf).
- [Manuale UNO Q: ADC, risoluzione e riferimento](https://docs.arduino.cc/tutorials/uno-q/user-manual/).
- [TI: protezione di un ingresso collegato a un piezo](https://e2e.ti.com/support/amplifiers-group/amplifiers/f/amplifiers-forum/552302/connect-a-piezoelectric-sensor-to-tlv2772-opamp). La discussione riguarda un amplificatore: i componenti devono essere dimensionati per l'ADC dell'UNO Q.