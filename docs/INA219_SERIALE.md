# Verifica elettrica del pannello con INA219

Configurazione confermata dal team: **INA219 sui pin SDA/SCL della UNO Q**,
resistenza shunt marcata **R100**, quindi 0,1 ohm. Il punto di inserzione del
sensore nel circuito e il modello esatto del charger restano da annotare.

## Collegamenti di comunicazione

| Modulo INA219 | UNO Q |
| --- | --- |
| VCC | 3V3, se il breakout supporta alimentazione diretta a 3,3 V |
| GND | GND comune del circuito di misura |
| SDA | SDA / D20 |
| SCL | SCL / D21 |

Il codice usa `Wire`; il Modulino continua a usare `Wire1` sul Qwiic. Non
confondere SDA/SCL con A4/A5. I pull-up del modulo devono portare SDA/SCL a
3,3 V. VCC alimenta il sensore: non e il morsetto della tensione da misurare.
La scheda UNO Q continua a essere alimentata da USB-C.

L'indirizzo configurato e `0x40`, corrispondente ad A0/A1 **del chip INA219**
collegati a GND. Se i ponticelli del modulo impostano un indirizzo diverso,
modificare `kIna219Address` in `app/sketch/sketch.ino`.

## Punto di misura

Per misurare il pannello, lo shunt va in serie sul ramo positivo:

```text
Pannello + ---- INA219 VIN+ [shunt R100] VIN- ---- ingresso solare + charger
Pannello - ------------------------------------ ingresso solare - charger
                      GND INA219 e GND UNO Q riferiti al negativo comune
```

Confrontare questo schema con quello del charger effettivamente disponibile.
VIN+ e VIN- sono i due lati dello shunt sul positivo, non il positivo e
negativo del pannello da collegare direttamente ai due morsetti.

Se il sensore e fra charger e batteria, i valori descrivono quel ramo:
non chiamarli potenza del pannello. Il verso da VIN+ a VIN- determina corrente
positiva; il segno viene conservato anche nella potenza. Piccoli valori vicino
a zero risentono dell'offset e non dimostrano da soli una corrente inversa.

## Eseguire la nuova versione

1. Dalla radice del repository eseguire `./deploy.ps1`. L'elenco trasferisce
   anche il nuovo `app/sketch/ina219_monitor.h`.
2. Riaprire SolarEcho-AI in App Lab e premere **Run**.
3. Aprire il **Serial Monitor**, come per le letture LIVE del piezo/Modulino.
4. Verificare il messaggio iniziale `INA219: Wire/SDA/SCL ... R_SHUNT=0.100`.
5. Attendere le righe `POWER`, indicativamente una al secondo.

La riga contiene:

| Campo | Significato |
| --- | --- |
| `t_ms` | Tempo firmware alla lettura dei registri |
| `V_IN` | Tensione VIN+ rispetto a GND, in V |
| `V_OUT` | Tensione VIN- rispetto a GND, in V |
| `SHUNT` | Caduta VIN+ meno VIN-, in mV |
| `I` | Corrente nel ramo, in mA |
| `P_IN` | `V_IN * I_A`, potenza lato VIN+ in W |
| `P_OUT` | `V_OUT * I_A`, potenza lato VIN- in W |

Il driver legge tensione bus e shunt, poi calcola corrente con `I_A =
Vshunt_V / Rshunt_ohm`. Le potenze sono calcolate da queste misure, non dalla
tensione nominale del pannello. Non usa i registri corrente/potenza interni:
non serve una libreria esterna con calibrazione fissa.

Il sensore acquisisce una conversione singola con media di 16 campioni per
canale. Il loop attende il completamento senza `delay`; lettura e stampa
vengono sospese durante cattura, trasferimento e attesa del salvataggio degli
impatti. Una conversione in corso all'impatto viene scartata.
Non vengono aggiunti questi dati ai CSV vibrazionali in questa versione.

## Controlli sul banco

- Con luce sul pannello confrontare `V_IN` con il multimetro sullo stesso punto.
- Ombreggiare e scoprire il pannello mantenendo gli altri collegamenti fissi.
  La corrente puo restare bassa se la batteria e carica o il charger non assorbe.
- Se non passa corrente, verificare l'offset vicino a zero senza azzerare
  automaticamente una corrente reale di carica all'avvio.
- Ripetere un impatto: le righe POWER devono riprendere dopo il ciclo CSV.

Un errore I2C, di configurazione o timeout produce `POWER SENSOR ERROR` e un
nuovo tentativo dopo 5 s. Una misura fuori range viene segnalata senza valori
di corrente/potenza. Il controllo software non protegge elettricamente gli
ingressi: il chip ha limite di 26 V e il range di corrente dipende anche dal
breakout e dalla potenza ammissibile dello shunt. Il FSR ADC impostato a 32 V
non autorizza l'applicazione di 32 V.

## Stato delle verifiche

Codice e deploy aggiornati; compilazione, esecuzione e prove fisiche sono
affidate al team, non eseguite durante questa implementazione. Non sono
disponibili risultati sperimentali di corrente o potenza.

## Fonti

- [Datasheet TI INA219](https://www.ti.com/lit/ds/symlink/ina219.pdf), sezioni 8.5 e 8.6; [copia locale](INA219-datasheet.pdf).
- [Manuale UNO Q](UM.md), sezione I2C: mapping Wire/Wire1 e logica a 3,3 V.
- [API Wire del core Arduino Zephyr](https://github.com/arduino/ArduinoCore-zephyr/blob/main/libraries/Wire/Wire.h).
