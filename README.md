# SolarEcho AI

Prototipo per monitorare variazioni della risposta meccanica di un pannello
fotovoltaico dopo impatti controllati. Un'anomalia richiede ispezione: non prova
la presenza di microfratture.

Stato attuale: acquisizione automatica su trigger piezo analogico A0, con buffer
IMU di 200 ms precedenti e 2 s successivi. Un CSV e un JSON per evento, controllo
della qualita e riarmo dopo il salvataggio. Le precedenti letture IMU/piezo sono
state provate dal team; la cattura automatica va verificata sul banco.
Elaborazione dei segnali e modello AI da implementare.

Disponibile l'esportazione locale dei CSV per Edge Impulse: ricampionamento
a 100 Hz, etichette esplicite e report degli eventi esclusi. Il convertitore
e i relativi test devono essere eseguiti e verificati dal team.

Il firmware include il monitor elettrico INA219 sui pin SDA/SCL (`Wire`),
con shunt R100: stampa tensione, corrente e potenza sul Serial Monitor.
Compilazione e verifica fisica di questa integrazione sono affidate al team.

- [Specifica dei requisiti](docs/SRS.md)
- [Componenti e documentazione](docs/COMPONENTI.md)
- [Procedura della prima acquisizione](docs/PRIMA_ACQUISIZIONE.md)
- [Esportazione CSV per Edge Impulse](docs/EDGE_IMPULSE_EXPORT.md)
- [Lettura seriale di tensione, corrente e potenza con INA219](docs/INA219_SERIALE.md)
- [Deploy dal repository a App Lab](docs/DEPLOY.md): eseguire `.\deploy.ps1` e riaprire la App sull'UNO Q.
- [Stampa seriale X/Y/Z e piezo analogico su A0: protezioni e lettura](docs/SERIALE_PIEZO.md).
