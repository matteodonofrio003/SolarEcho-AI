# SolarEcho AI

Prototipo per monitorare variazioni della risposta meccanica di un pannello
fotovoltaico dopo impatti controllati. Un'anomalia richiede ispezione: non prova
la presenza di microfratture.

Stato attuale: acquisizione automatica su trigger piezo analogico A0, con buffer
IMU di 200 ms precedenti e 2 s successivi. Un CSV e un JSON per evento, controllo
della qualita e riarmo dopo il salvataggio. Le precedenti letture IMU/piezo sono
state provate dal team, insieme alla cattura e all'esportazione per Edge Impulse.
Integrato il modello personalizzato `ei-model-1136239-1` per l'inferenza locale
sugli eventi: nuova integrazione pronta per la verifica del team.

Dashboard locale implementata con il brick Web UI di App Lab: misure elettriche,
anteprima IMU/piezo, contatori, grafico delle acquisizioni e download CSV/JSON.
La dashboard iniziale e stata provata dal team. Aggiunto lo storico elettrico
automatico in `data/power/`: CSV per sessione, consultazione delle ultime 600
letture e download completo, anche dopo un riavvio. Lo storico e stato
provato dal team. Accessibile sulla stessa rete a
`http://<IP-della-UNO-Q>:7000`. Aggiunti score, storico AI e confronto con una
copia sintetica esplicitamente identificata nella dashboard.

La dashboard e ora organizzata in quattro tab: Panoramica, Vibrazioni e AI,
Energia e costi, Segnalazioni. Stato e allerta restano visibili; impostazioni,
diagnostica e archivi sono richiudibili. Questa riorganizzazione grafica e pronta
per la verifica del team: [uso e procedura](docs/DASHBOARD.md).

Aggiunto il confronto elettrico controllato: riferimento su 10 letture,
integrazione dell'energia sui soli intervalli coperti e scenario domestico
ipotetico con produzione/tariffe configurabili. Report JSON e parametri salvati
localmente. Questa nuova parte e pronta per la verifica del team.

Aggiunta la richiesta di ispezione con LED rosso su D7 e sul LED RGB 3
integrato: calo persistente dopo un numero configurabile di impatti, allerta
confermata dalla dashboard e stato salvato localmente. L'AI puo attivare il LED
dopo il salvataggio della soglia usata in Edge Impulse. Il test artificiale usa
il motivo `AI_TEST`, distinto da una misura reale. Da verificare sul banco.

Aggiunta la segnalazione manuale via brick Telegram Bot: destinatario configurabile
dalla dashboard, anteprima dei dati e storico locale degli invii con report JSON.
Il token si configura solo sulla scheda dopo il deploy. L'integrazione Telegram
e stata provata dal team; l'aggiunta dei dati AI e da verificare.

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
- [Modello AI: avvio, soglia e prova dalla dashboard](docs/AI_INTEGRAZIONE.md)
- [Generazione e limiti dei test sintetici](docs/TEST_SINTETICO.md)
- [Lettura seriale di tensione, corrente e potenza con INA219](docs/INA219_SERIALE.md)
- [Deploy dal repository a App Lab](docs/DEPLOY.md): eseguire `.\deploy.ps1` e riaprire la App sull'UNO Q.
- [Dashboard: avvio passo per passo e prima verifica](docs/DASHBOARD.md).
- [Demo elettrica e calcolo dello scenario economico](docs/DEMO_ECONOMICA.md).
- [LED rosso: collegamento, soglie e prova di ispezione](docs/LED_ISPEZIONE.md).
- [Telegram: configurazione e invio dalla dashboard](docs/TELEGRAM.md).
- [Stampa seriale X/Y/Z e piezo analogico su A0: protezioni e lettura](docs/SERIALE_PIEZO.md).
