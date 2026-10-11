# Deploy dal repository a Arduino App Lab

Il codice sorgente si modifica nel repository sul PC. [deploy.ps1](../deploy.ps1) trasferisce la cartella `app/` nell'App `solarecho-ai` sull'UNO Q. Dopo il trasferimento riaprire la App in App Lab per ricaricare l'editor e premere **Run**: lo sketch viene compilato e caricato sullo STM32, Python viene avviato su Linux.

## USB: comando abituale

1. Collegare UNO Q via USB-C dati e completare il setup di App Lab.
2. Salvare le modifiche nel repository. Chiudere le schede dell'editor App Lab con modifiche non salvate: i file locali verranno trasferiti sulla scheda.
3. In PowerShell, dalla cartella del repository, eseguire:

   ```powershell
   .\deploy.ps1
   ```

4. In App Lab tornare alla lista delle App e riaprire **SolarEcho-AI**. Riconfigurare il token nel brick Telegram Bot dopo il deploy (vedere [Telegram](TELEGRAM.md)), poi premere **Run** quando si vuole eseguire il codice aggiornato.

Se Windows blocca lo script per l'execution policy, eseguirlo con una policy limitata al solo processo:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\deploy.ps1
```

Lo script trova ADB dal PATH, da un processo ADB aperto da App Lab oppure dall'installazione Arduino15. Con piu dispositivi USB collegati bisogna indicare il seriale:

```powershell
.\deploy.ps1 -Serial 4238628897
```

Per un eseguibile ADB in un'altra posizione:

```powershell
.\deploy.ps1 -AdbPath 'C:\percorso\adb.exe'
```

## Anteprima e avvio da terminale

```powershell
# Controlla collegamento e destinazione senza trasferire file.
.\deploy.ps1 -WhatIf

# Trasferisce, compila e avvia; equivale al successivo Run in App Lab.
.\deploy.ps1 -Start
```

`-Start` richiede che eventuali altre App siano ferme. La versione attuale attende READY e avvia una cattura a ogni impatto piezo: 200 ms precedenti e 2 s successivi. Preparare il cablaggio protetto prima di eseguirla e attendere il successivo READY fra impatti.

## Wi-Fi: alternativa tramite SSH

Dopo la configurazione di rete dell'UNO Q, PC e scheda devono essere raggiungibili sulla stessa rete. Usare il nome o l'IP effettivo della scheda:

```powershell
.\deploy.ps1 -SshHost arduino@solarecho-unoq.local
```

SSH/SCP possono chiedere la password nel terminale e, al primo accesso, la conferma dell'impronta del dispositivo. Lo script non salva credenziali. Un'autenticazione con chiave SSH gia configurata evita le richieste di password durante i trasferimenti.

## File e dati

| Repository | Destinazione sull'UNO Q |
| --- | --- |
| `app/app.yaml` | `/home/arduino/ArduinoApps/solarecho-ai/app.yaml` |
| `app/sketch/sketch.yaml` | `/home/arduino/ArduinoApps/solarecho-ai/sketch/sketch.yaml` |
| `app/sketch/sketch.ino` | `/home/arduino/ArduinoApps/solarecho-ai/sketch/sketch.ino` |
| `app/sketch/ina219_monitor.h` | `/home/arduino/ArduinoApps/solarecho-ai/sketch/ina219_monitor.h` |
| `app/python/main.py` | `/home/arduino/ArduinoApps/solarecho-ai/python/main.py` |
| `app/python/dashboard.py` | `/home/arduino/ArduinoApps/solarecho-ai/python/dashboard.py` |
| `app/python/power_history.py` | `/home/arduino/ArduinoApps/solarecho-ai/python/power_history.py` |
| `app/python/electrical_demo.py` | `/home/arduino/ArduinoApps/solarecho-ai/python/electrical_demo.py` |
| `app/python/inspection_alert.py` | `/home/arduino/ArduinoApps/solarecho-ai/python/inspection_alert.py` |
| `app/python/telegram_notifications.py` | `/home/arduino/ArduinoApps/solarecho-ai/python/telegram_notifications.py` |
| `app/python/vibration_ai.py` | `/home/arduino/ArduinoApps/solarecho-ai/python/vibration_ai.py` |
| `app/assets/index.html` | `/home/arduino/ArduinoApps/solarecho-ai/assets/index.html` |
| `app/assets/style.css` | `/home/arduino/ArduinoApps/solarecho-ai/assets/style.css` |
| `app/assets/dashboard.js` | `/home/arduino/ArduinoApps/solarecho-ai/assets/dashboard.js` |

Il deploy ferma SolarEcho se e attiva, salva i file precedenti dell'elenco in `.deploy-backups/<data_id>/` della stessa App e verifica il checksum SHA256 di ogni file trasferito prima di sostituirlo. Se un passaggio fallisce, l'App non viene riavviata; correggere l'errore e ripetere il deploy. I CSV nella cartella `data/` vengono conservati.

Le variabili dei brick configurate in App Lab possono contenere segreti nel
manifest sulla scheda. Il deploy sostituisce `app.yaml` con il manifest senza
segreti del repository: reinserire `TELEGRAM_BOT_TOKEN` nel brick dopo ogni deploy.
Per questa configurazione usare `.\deploy.ps1` senza `-Start`, impostare il token,
poi premere Run. Non copiare il manifest o i backup della scheda nel repository.

La sincronizzazione avviene quando si esegue il comando. Dopo una modifica in questo repository il file non cambia automaticamente sulla scheda. Per evitare conflitti, usare il repository per modificare il codice e App Lab per eseguirlo e leggere i log. Eventuali nuove sorgenti richiedono l'aggiornamento dell'elenco `$files` nello script.

`sketch.yaml` riproduce le versioni delle librerie della App con cui il team ha gia acquisito i dati. La versione del core resta gestita dall'installazione App Lab dell'UNO Q.

Il manifest abilita i brick `arduino:web_ui`, `arduino:telegram_bot`,
`arduino:vibration_anomaly_detection` e la porta 7000. Prima di Run, il modello
personalizzato `ei-model-1136239-1` deve essere gia scaricato in App Lab.
Vedere [avvio e soglia AI](AI_INTEGRAZIONE.md). Dopo Run,
aprire `http://<IP-della-UNO-Q>:7000` sulla stessa rete: vedere
[la procedura dashboard](DASHBOARD.md). Anche gli asset web richiedono deploy
e riavvio per essere aggiornati sulla scheda.

## Verifica effettuata

Il 10 ottobre 2026 sono stati verificati sintassi PowerShell, anteprima `-WhatIf` e deploy USB sull'UNO Q del team. I quattro file trasferiti hanno superato il confronto SHA256 e il CLI ha riconosciuto SolarEcho-AI senza errori di configurazione. L'App e rimasta ferma, pronta per Run. Il percorso SSH e l'opzione `-Start` non sono stati eseguiti in questa verifica.

## Riferimenti

- [Specifica ufficiale delle App Arduino](https://github.com/arduino/arduino-app-cli/blob/main/docs/app-specification.md).
- [File delle App e Arduino App CLI](https://docs.arduino.cc/tutorials/uno-q/debian-guide/).
- [Trasferimento delle sorgenti via ADB o SCP](https://docs.arduino.cc/tutorials/uno-q/ai-coding-agents/).
