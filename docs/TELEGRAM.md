# Segnalazione manuale via Telegram

La dashboard invia una fotografia dei dati del pannello al bot, che rappresenta
l'operatore nella demo. Non serve una risposta dell'operatore. L'invio parte solo
quando premi **Invia segnalazione**; un'allerta o il LED non inviano messaggi da soli.

## Prima configurazione, passo per passo

1. Se non l'hai ancora fatto, rigenera con BotFather il token che hai condiviso
   in chat: usa `/revoke` e seleziona il bot. Conserva il nuovo token solo nelle
   impostazioni del brick sulla scheda.
2. Dal repository sul PC esegui il normale deploy:

   ```powershell
   .\deploy.ps1
   ```

3. Torna alla lista delle App in App Lab e riapri **SolarEcho-AI**. Il manifest
   include già **Web UI** e **Telegram Bot**.
4. Nelle impostazioni del brick **Telegram Bot** inserisci il nuovo token nel
   campo `TELEGRAM_BOT_TOKEN` e salva. Fallo **dopo il deploy**: lo script
   sostituisce `app.yaml` e le variabili impostate sulla scheda vanno riconfigurate.
   Non copiare il manifest della scheda con il token nel repository.
5. Collega UNO Q a una rete con accesso a Internet e premi **Run**. Apri la
   dashboard abituale `http://<IP-della-UNO-Q>:7000` e attendi lo stato Telegram
   **PRONTO PER INVIO**. Il PC deve poter raggiungere la scheda sulla rete locale.
6. Dal telefono apri la **chat privata** con il bot e invia `/start`, anche se
   avevi già premuto Avvia prima di aggiornare il codice. Il bot risponde con
   **Il tuo Chat ID: ...**.
7. Nella sezione **Segnalazione via Telegram** della dashboard inserisci:
   - **Identificativo pannello**: per esempio `SolarEcho-01`;
   - **Chat ID destinatario**: il numero positivo ricevuto dal bot, senza altro testo.

   Il Chat ID è diverso dal token. Premi **Salva destinatario**.
8. Con i sensori attivi, premi **Anteprima dati** per vedere il messaggio.
9. Premi **Invia segnalazione** una volta. Puoi farlo anche senza un'allerta:
   sarà una segnalazione manuale. Lo storico mostra l'esito; verifica sul telefono
   che sia arrivato il messaggio e che i valori corrispondano al pannello.

L'anteprima e l'invio acquisiscono i valori in momenti diversi: durante l'invio
vengono usati i dati disponibili in quel momento. Non vengono trasmesse le forme
d'onda CSV né allegati. L'inferenza e l'acquisizione restano locali; Telegram richiede
Internet. Non serve esporre la dashboard su Internet né aprire porte del router.

## Contenuto del messaggio

- Identificativo pannello, richiesta, sessione e istante UTC della fotografia.
- Stato monitoraggio ed età della telemetria.
- Impatti totali e dal riferimento, quando la telemetria è recente.
- Tensione, corrente e potenza recenti, con unità di misura.
- Accelerazione X/Y/Z, che include la gravità.
- Riferimento elettrico e calo recente, se disponibili.
- Motivo e valori dell'allerta registrata, se presente.
- Stato dell'AI: attualmente **non attiva**. Lo score appare solo per un'allerta
  AI reale passata al sistema, quando il modello sarà integrato.
- Scenario economico, se disponibile, esplicitamente **IPOTETICO**.
- Richiamo all'ispezione, senza diagnosi certa di danni o microfratture.

Durante una cattura o senza telemetria recente, le misure sono indicate come
non aggiornate o `n/d`. Un'allerta già registrata conserva i propri valori storici.
Il calo elettrico non dimostra che un impatto abbia danneggiato il pannello:
luce, ombra e carico possono influenzare la produzione.

## Esiti e problemi

| Esito | Cosa significa / cosa fare |
| --- | --- |
| In attesa | Richiesta salvata sulla scheda e accodata. |
| Invio in corso | Il servizio sta chiamando Telegram. |
| Inviato | Telegram ha accettato il messaggio; non prova che una persona l'abbia letto. |
| Invio non eseguito | Salvataggio fallito prima della chiamata: controlla spazio e permessi. |
| Esito non confermato | Telegram potrebbe aver ricevuto il messaggio: controlla la chat prima di riprovare. |

Se compare **TOKEN DA CONFIGURARE**, imposta il token nel brick e riavvia la App.
Se compare **NON DISPONIBILE**, verifica token e Internet, poi premi **Riconnetti**.
Il primo collegamento può richiedere alcuni secondi; l'acquisizione continua
indipendentemente dal servizio Telegram.

### Se /start non risponde

La dashboard mostra **Bot collegato: @nome**: apri quella chat tramite il link,
così usi il bot associato al token effettivo della App. Invia un nuovo `/start`
dopo che il bot è avviato.

Sotto il destinatario trovi **Ultimo /start**, **Chat ID** ed esito della risposta.
Se il comando è ricevuto ma la risposta non è confermata, puoi copiare quel Chat
ID nella configurazione. Nessun destinatario viene associato automaticamente.
Se resta **Nessun /start ricevuto**, consulta il messaggio di errore Telegram e
le righe `TELEGRAM:` nei log Python di App Lab.

Un errore **Conflict** indica che un altro processo sta ricevendo gli aggiornamenti
con lo stesso token: ferma le altre App/istanze del bot, poi premi **Riconnetti**.
Con un errore di token, correggi il token nel brick e riavvia. Con un errore di
rete, verifica Internet sulla scheda. Non condividere token né URL contenenti token
quando copi i log.

Un timeout o un riavvio durante l'invio può lasciare un esito incerto. Il sistema
non reinvia automaticamente: prima verifica la chat, poi riconnetti e usa
**Ripeti (possibile duplicato)** se necessario. Ripeti usa lo stesso ID, testo e
destinatario originali; per trasmettere nuovi valori usa **Invia segnalazione**.
Se hai cambiato destinatario, crea una nuova segnalazione.

## Archivio e implementazione

I dati sono salvati nella cartella `data/notifications/` della App:

- `settings.json`: identificativo pannello e Chat ID, senza token;
- `notification_<id>.json`: fotografia dei dati, testo, tentativi ed esito.

Il pulsante **JSON** nello storico scarica il report. Al riavvio vengono caricati
gli ultimi 100 report; la dashboard mostra le ultime 10 richieste. I file più vecchi
restano su disco. Il deploy conserva `data/` ma sostituisce `app.yaml`: riconfigura
il token dopo ogni deploy. Anche i backup del manifest sulla scheda possono
contenere segreti; non pubblicarli su GitHub.

`telegram_notifications.py` usa il brick in un worker dedicato. Avvio del bot e
invio non bloccano il ciclo di acquisizione e non effettuano RPC ai sensori.
La richiesta viene salvata prima dell'invio. Lo stesso ID ricevuto più volte
non produce un secondo invio automatico. L'API Telegram non garantisce la
deduplicazione dopo un timeout: per questo i tentativi incerti sono manuali.
Una versione incompatibile di App Utils o del brick viene mostrata come errore
Telegram senza interrompere il monitoraggio. La configurazione prevista è una
chat privata, non gruppi o canali.

## Verifica affidata al team

Questa integrazione non è stata eseguita né provata sulla scheda dall'assistente.
Prima della demo verifica:

1. `/start` risponde con il Chat ID dopo l'avvio della nuova App.
2. Senza destinatario salvato, il pulsante di invio rimane disabilitato.
3. Una segnalazione normale arriva con unità, contatori e AI non attiva corretti.
4. Con un'allerta elettrica, il messaggio include il motivo e i valori dell'allerta.
5. Togliendo Internet alla scheda, il monitoraggio locale continua; lo storico
   segnala l'invio non confermato. Verifica la chat prima di ripetere.
6. Riavviando la App, destinatario e storico restano disponibili, senza reinvio
   automatico delle richieste precedenti.

I test software in `tests/test_telegram_notifications.py` usano un bot fittizio,
senza rete o dati sperimentali. Sono stati preparati, **non eseguiti**:

```powershell
python -m unittest discover -s tests -p test_telegram_notifications.py
```

## Documentazione verificata

- [Implementazione ufficiale del brick Telegram Bot](https://github.com/arduino/app-bricks-py/blob/main/src/arduino/app_bricks/telegram_bot/telegram_bot.py).
- [Variabile segreta del brick](https://github.com/arduino/app-bricks-py/blob/main/src/arduino/app_bricks/telegram_bot/brick_config.yaml).
- [Manifest delle App e variabili dei brick](https://github.com/arduino/arduino-app-cli/blob/main/docs/app-specification.md).
- [Bot Telegram: avvio delle conversazioni](https://core.telegram.org/bots).
