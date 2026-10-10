# Documentazione dei componenti SolarEcho AI

Fonte dell'inventario: [Materiale di elettronica da reperire - Materiale.pdf](../Materiale%20di%20elettronica%20da%20reperire%20-%20Materiale.pdf). I nomi e i link del PDF identificano i componenti selezionati; la sigla stampata sui pezzi fisici resta il controllo finale prima dei collegamenti.

## Acquisizione e visualizzazione

| Componente | Documenti locali | Fonte originale | Nota per il progetto |
| --- | --- | --- | --- |
| Arduino UNO Q 4 GB | [Datasheet italiano](ABX00162-ABX00173-it-datasheet.pdf), [pinout completo](ABX00162-full-pinout.pdf), [manuale](UM.md) | [Arduino UNO Q](https://docs.arduino.cc/hardware/uno-q/) | STM32 per acquisizione; Linux per elaborazione. GPIO STM32 e Qwiic a 3,3 V. Alimentazione demo USB-C 5 V / 3 A. |
| Arduino Modulino Movement, ABX00101 | [Datasheet](ABX00101-Modulino-Movement-datasheet.pdf), [schema elettrico](ABX00101-Modulino-Movement-schematics.pdf) | [Arduino Modulino Movement](https://docs.arduino.cc/hardware/modulino-movement/) | IMU LSM6DSOXTR, collegamento Qwiic al bus `Wire1` dell'UNO Q. Sensore principale per X/Y/Z. |
| Grove Piezo Vibration Sensor, SKU 101020031 | [Guida PDF](Grove-Piezo-Vibration-Sensor-wiki.pdf), [guida Markdown](Grove-Piezo-Vibration-Sensor-wiki.md), [schema elettrico](Grove-Piezo-Vibration-Sensor-schematic.pdf), [datasheet elemento piezo LDT0-028K](LDT0-028K-piezo-film-datasheet.pdf) | [Seeed Wiki](https://wiki.seeedstudio.com/Grove-Piezo_Vibration_Sensor/) | La guida Seeed specifica un'uscita HIGH/LOW regolata dal potenziometro. Usare come trigger; non trattare il valore letto sull'uscita come forma d'onda analogica. Alimentare e verificare l'uscita nel dominio 3,3 V prima di collegarla allo STM32. |
| Grove OLED 0,96\" SSD1315, SKU 104020208 | [Guida Markdown](Grove-OLED-SSD1315-wiki.md), [datasheet modulo display](Grove-OLED-SSD1315-module-datasheet.pdf), [schemi Seeed](Grove-OLED-SSD1315-schematics.zip) | [Seeed Wiki](https://wiki.seeedstudio.com/Grove-OLED-Display-0.96-SSD1315/) | Display I2C 128 x 64 compatibile con alimentazione 3,3 V. Il connettore Grove richiede cablaggio o adattatore appropriato; verificare indirizzo I2C prima del firmware. |

La [guida Seeed del piezo](Grove-Piezo-Vibration-Sensor-wiki.md) contiene anche un esempio che usa un ingresso analogico, ma la FAQ dello stesso produttore specifica che l'uscita del modulo e digitale LOW/HIGH. Il datasheet LDT0-028K descrive il **solo elemento piezoelettrico interno**: non descrive l'uscita elettrica del modulo Grove completo.

## Alimentazione e pannello

| Componente | Documenti locali | Fonte originale | Stato |
| --- | --- | --- | --- |
| Batteria LiPo PLIB1000-2MM | [Scheda commerciale salvata](PLIB1000-2MM-battery-product.html) | [Open Electronics](https://www.open-electronics.org/product/lithium-polymer-battery-3-7v-1000ma-2mm-pitch/) | La scheda indica 3,7 V, 1000 mAh e connettore passo 2 mm. Verificare fisicamente la polarita del connettore prima del caricatore. Non e un datasheet con limiti di carica/scarica. |
| Solar charger Waveshare | [Panoramica della famiglia](Waveshare-Solar-Power-Manager-family.html) | [Waveshare Wiki](https://www.waveshare.com/wiki/Solar_Power_Manager) | L'inventario non riporta modello o revisione. La pagina confronta varianti con uscite diverse: nessuna puo essere attribuita con certezza alla scheda disponibile. Serve foto della serigrafia fronte/retro o SKU. |
| Mini Solar Panel R1123 | Nessun datasheet del produttore verificato | L'inventario non contiene un link. Una [inserzione che cita R1123](https://www.desertcart.in/products/657216814-runcci-yun-4pcs-6v-100ma-90-60mm-polycrystalline-micro-mini) indica un pannello circa 90 x 60 mm, 6 V e 100 mA, ma non costituisce una specifica verificata del pezzo disponibile. | Misurare tensione a vuoto, corrente in luce controllata e dimensioni; leggere etichette o confezione. Non usarlo per alimentare direttamente l'UNO Q. |

Il caricatore Waveshare e il pannello R1123 restano fuori dal circuito di alimentazione dell'MVP fino all'identificazione dei modelli e alla verifica di tensioni, correnti, connettori e protezioni.

## Provenienza dei file scaricati

| File | URL di download |
| --- | --- |
| `ABX00101-Modulino-Movement-datasheet.pdf` | https://docs.arduino.cc/resources/datasheets/ABX00101-datasheet.pdf |
| `ABX00101-Modulino-Movement-schematics.pdf` | https://docs.arduino.cc/resources/schematics/ABX00101-schematics.pdf |
| `Grove-Piezo-Vibration-Sensor-wiki.pdf` | https://files.seeedstudio.com/wiki/Grove-Piezo_Vibration_Sensor/res/Grove-Piezo_Vibration_Sensor_wiki.pdf |
| `Grove-Piezo-Vibration-Sensor-wiki.md` | https://raw.githubusercontent.com/Seeed-Studio/wiki-documents/docusaurus-version/sites/en/docs/Sensor/Grove/Grove_Sensors/Motion/Grove-Piezo_Vibration_Sensor.md |
| `Grove-Piezo-Vibration-Sensor-schematic.pdf` | https://files.seeedstudio.com/wiki/Grove-Piezo_Vibration_Sensor/res/Gvove-Piezo_Vibration_Sensor.pdf |
| `LDT0-028K-piezo-film-datasheet.pdf` | https://files.seeedstudio.com/wiki/Grove-Piezo_Vibration_Sensor/res/Piezo_Vibration_Sensor.pdf |
| `Grove-OLED-SSD1315-wiki.md` | https://raw.githubusercontent.com/Seeed-Studio/wiki-documents/docusaurus-version/sites/en/docs/Sensor/LCD_Displays/Grove_Series/Grove-OLED-Display-0.96-SSD1315.md |
| `Grove-OLED-SSD1315-module-datasheet.pdf` | https://files.seeedstudio.com/wiki/Grove-OLED-Display-0.96-SSD1315-/res/OEL%20Display%20Module.pdf |
| `Grove-OLED-SSD1315-schematics.zip` | https://files.seeedstudio.com/wiki/Grove-OLED-Display-0.96-SSD1315-/res/Grove%20-%20OLED%20Display%200.96%20%28SSD1315%29_v1.0.zip |
| `PLIB1000-2MM-battery-product.html` | https://www.open-electronics.org/product/lithium-polymer-battery-3-7v-1000ma-2mm-pitch/ |
| `Waveshare-Solar-Power-Manager-family.html` | https://www.waveshare.com/wiki/Solar_Power_Manager |

Non e stato scaricato il datasheet ST del chip LSM6DSOX: il server ST non ha risposto nei tentativi di download. Il datasheet del modulo Arduino e presente; [datasheet ST online](https://www.st.com/resource/en/datasheet/lsm6dsox.pdf).
