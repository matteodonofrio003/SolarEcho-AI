# Documentazione hardware

## Riferimenti essenziali

- [Manuale ufficiale UNO Q](https://docs.arduino.cc/tutorials/uno-q/user-manual/)
- [Datasheet UNO Q](datasheets/ABX00162-ABX00173-it-datasheet.pdf)
- [Pinout UNO Q](datasheets/ABX00162-full-pinout.pdf)
- [Modulino Movement](datasheets/ABX00101-Modulino-Movement-datasheet.pdf)
- [Schema Modulino Movement](datasheets/ABX00101-Modulino-Movement-schematics.pdf)
- [INA219](datasheets/INA219-datasheet.pdf)

Le pagine salvate della batteria e della famiglia charger restano in
`datasheets/`. Identificazione e limiti: [Componenti](../COMPONENTI.md).

## Progettazione del prototipo

- [Schema elettrico](design/SolarEcho-AI-schematic_schem.jpg)
- [Vista breadboard](design/SolarEcho-AI-schematic_bb.jpg)
- [Progetto Fritzing](design/SolarEcho-AI-schematic.fzz)
- [Distinta elettronica](design/SolarEcho-AI-eBOM.xlsx)
- [Involucro STL](../../Solar_Housing.stl)

Il progetto `.fzz` incorpora le cinque parti personalizzate e le rispettive
risorse grafiche: i pacchetti `.fzpz` separati sono stati rimossi dopo il
confronto dei contenuti tramite SHA-256. Il simbolo UNO R4 incorporato e una
risorsa di disegno storica: per i collegamenti UNO Q usare il suo pinout e la
[guida acquisizione](../ACQUISIZIONE_E_SENSORI.md).
