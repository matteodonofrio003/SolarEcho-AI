# SolarEcho AI

Prototipo per monitorare variazioni della risposta meccanica di un pannello
fotovoltaico dopo impatti controllati. Un'anomalia richiede ispezione: non prova
la presenza di microfratture.

Stato attuale: prima acquisizione dell'accelerometro Modulino Movement su
Arduino UNO Q eseguita dal team. Deploy USB dal repository verificato sulla
scheda; elaborazione dei segnali e modello AI da implementare.

- [Specifica dei requisiti](docs/SRS.md)
- [Componenti e documentazione](docs/COMPONENTI.md)
- [Procedura della prima acquisizione](docs/PRIMA_ACQUISIZIONE.md)
- [Deploy dal repository a App Lab](docs/DEPLOY.md): eseguire `.\deploy.ps1` e riaprire la App sull'UNO Q.
- [Stampa seriale X/Y/Z e piezo analogico su A0: protezioni e lettura](docs/SERIALE_PIEZO.md).
