# Componenti e documentazione hardware

L'inventario iniziale proveniva da `Materiale di elettronica da reperire -
Materiale.pdf`, consultato durante la selezione ma non incluso nella repository.
Questa pagina distingue i componenti del prototipo dalle alternative scartate.
La sigla del pezzo fisico resta il controllo finale prima dei collegamenti.

## Componenti del prototipo

| Componente | Documenti e ruolo |
| --- | --- |
| Arduino UNO Q 4 GB | [Datasheet](hardware/datasheets/ABX00162-ABX00173-it-datasheet.pdf), [pinout](hardware/datasheets/ABX00162-full-pinout.pdf), [manuale ufficiale](https://docs.arduino.cc/tutorials/uno-q/user-manual/). STM32 per acquisizione e Linux per analisi locale; GPIO e Qwiic a 3,3 V. Alimentazione demo USB-C. |
| Modulino Movement ABX00101 | [Datasheet](hardware/datasheets/ABX00101-Modulino-Movement-datasheet.pdf), [schema](hardware/datasheets/ABX00101-Modulino-Movement-schematics.pdf), [Arduino](https://docs.arduino.cc/hardware/modulino-movement/). Sensore XYZ, Qwiic su `Wire1`. |
| Piezo passivo analogico a due fili | Trigger su A0 attraverso condizionamento e protezioni. Il modello esatto non e identificato: non attribuirgli il datasheet del Grove. Una resistenza da 1 MOhm in parallelo non protegge da sola l'ADC. |
| INA219 con shunt R100 | [Datasheet TI](hardware/datasheets/INA219-datasheet.pdf), [fonte originale](https://www.ti.com/lit/ds/symlink/ina219.pdf). Confermato dal team: SDA/SCL su `Wire`, shunt 0,1 ohm, fra pannello e charger. Annotare modello e limiti del breakout e dello shunt. |
| LED rosso | D7 con resistenza in serie; [cablaggio e logica di allerta](DASHBOARD.md#allerte-e-led). Replica anche sul rosso del LED RGB 3 integrato. |

Collegamenti, diagnostica e formati: [Acquisizione e sensori](ACQUISIZIONE_E_SENSORI.md).
Schema, distinta e progetto editabile: [indice hardware](hardware/README.md).

## Pannello, batteria e caricatore

Il team ha collegato pannello, charger e batteria per la prova elettrica.
Questo sottosistema non dimostra l'autonomia energetica della UNO Q, alimentata
via USB-C nella demo. Prima di alimentarla diversamente verificare tensioni,
correnti, conversione e protezioni con il modello esatto di ogni componente.

| Componente | Documentazione | Limiti delle informazioni disponibili |
| --- | --- | --- |
| Mini Solar Panel R1123 | Nessun datasheet del produttore verificato. Una [inserzione che cita R1123](https://www.desertcart.in/products/657216814-runcci-yun-4pcs-6v-100ma-90-60mm-polycrystalline-micro-mini) era presente nella ricerca iniziale. | Le indicazioni commerciali di 6 V, 100 mA e circa 90 x 60 mm non sono specifiche confermate del pezzo del team. Verificare etichette, dimensioni e misure reali. |
| LiPo PLIB1000-2MM | [Scheda commerciale salvata](hardware/datasheets/PLIB1000-2MM-battery-product.html), [fonte](https://www.open-electronics.org/product/lithium-polymer-battery-3-7v-1000ma-2mm-pitch/). | La pagina indica 3,7 V, 1000 mAh e connettore passo 2 mm; non documenta tutti i limiti di carica/scarica. Verificare polarita e caratteristiche del pezzo. |
| Solar charger Waveshare | [Panoramica salvata](hardware/datasheets/Waveshare-Solar-Power-Manager-family.html), [wiki ufficiale](https://www.waveshare.com/wiki/Solar_Power_Manager). | La pagina descrive una famiglia di varianti; modello e revisione della scheda fisica restano da identificare. Un simbolo CAD non ne certifica l'identita. |

## Alternative valutate e non usate

Le copie locali di questi documenti sono state rimosse per mantenere il focus
sull'hardware effettivo. Restano i riferimenti ufficiali:

| Componente | Fonte | Motivo della distinzione |
| --- | --- | --- |
| Grove Piezo Vibration Sensor | [Seeed Wiki](https://wiki.seeedstudio.com/Grove-Piezo_Vibration_Sensor/) | Modulo con uscita HIGH/LOW; non e il piezo analogico passivo collegato ad A0. La FAQ e l'esempio analogico della guida richiedono attenzione alla natura dell'uscita. |
| Elemento LDT0-028K | [Datasheet collegato da Seeed](https://files.seeedstudio.com/wiki/Grove-Piezo_Vibration_Sensor/res/Piezo_Vibration_Sensor.pdf) | Riguarda l'elemento interno al Grove, non ne descrive l'uscita completa e non identifica il piezo attuale. |
| Grove OLED SSD1315 | [Seeed Wiki](https://wiki.seeedstudio.com/Grove-OLED-Display-0.96-SSD1315/) | Non utilizzato dal firmware corrente; visualizzazione tramite dashboard e LED. |
| Grove ACS70331 | [Seeed Wiki](https://wiki.seeedstudio.com/Grove-2.5A-DC-Current-Sensor-ACS70331/) | Alternativa analogica dell'inventario; per corrente e potenza e stato usato INA219. |

## Provenienza dei riferimenti conservati

- UNO Q: [Arduino](https://docs.arduino.cc/hardware/uno-q/).
- Movement: [datasheet originale](https://docs.arduino.cc/resources/datasheets/ABX00101-datasheet.pdf)
  e [schema originale](https://docs.arduino.cc/resources/schematics/ABX00101-schematics.pdf).
- INA219: [Texas Instruments](https://www.ti.com/lit/ds/symlink/ina219.pdf).
- Batteria e charger: fonti riportate nella tabella dedicata.
- Chip IMU LSM6DSOX: [datasheet ST online](https://www.st.com/resource/en/datasheet/lsm6dsox.pdf);
  la copia locale non era stata scaricata. Il datasheet Arduino del modulo e conservato.
