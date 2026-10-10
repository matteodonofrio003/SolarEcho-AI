# Demo elettrica e scenario economico

## Scopo

La dashboard confronta la produzione del minipannello con un riferimento
acquisito prima dell'oscuramento. Calcola energia misurata, energia attesa
mantenendo quel riferimento costante e scostamento sul tempo effettivamente
coperto dalle misure. Un calcolatore separato illustra uno scenario domestico
ipotetico con parametri inseriti dall'utente.

L'oscuramento simula una riduzione di produzione. Non dimostra che la pallina
abbia danneggiato il pannello o causato una perdita elettrica. Il confronto
meccanico/AI e il confronto elettrico hanno risultati separati.

## Installazione

1. Ferma SolarEcho in App Lab.
2. Dalla cartella del repository esegui `./deploy.ps1` in PowerShell.
3. Riapri SolarEcho-AI e premi Run.
4. Ricarica `http://<IP-della-UNO-Q>:7000` nel browser.

Il deploy trasferisce anche `python/electrical_demo.py`. Il firmware non richiede
nuove RPC: si usano le misure elettriche gia registrate dal logger.

## Prova passo per passo

### A. Prepara una luce stabile

1. Fissa il pannello e la sorgente luminosa; evita di tenere il telefono in mano.
2. Mantieni lo stesso solar charger, batteria e collegamenti durante la prova.
   Variazioni di carico o dello stato di carica possono cambiare la misura.
3. Attendi che corrente e potenza siano stabili e positive nello storico.
4. Gli impatti della prima parte della demo possono essere eseguiti qui, sempre
   aspettando READY. Evita impatti durante l'acquisizione del riferimento elettrico.

### B. Acquisisci il riferimento

1. Premi **1. Acquisisci riferimento**.
2. Lascia il pannello scoperto e fermo per circa 10-15 secondi.
3. La dashboard raccoglie 10 nuove misure consecutive e mostra il progresso.
4. Attendi **Riferimento pronto**. Se la potenza e troppo bassa o instabile,
   stabilizza la luce e ripeti. Un intervallo oltre 2,5 s ricomincia la raccolta;
   dopo 25 s senza completarla il riferimento e rifiutato.

Il riferimento e la media della potenza delle 10 misure. I gate iniziali sono
media maggiore di 0,1 mW e deviazione standard/media non superiore al 20%.
Sono parametri diagnostici del prototipo, non una specifica di accuratezza
dell'INA219. Devono essere verificati con le condizioni reali della demo.

### C. Imposta lo scenario

Nella sezione **Scenario domestico ipotetico** inserisci:

- produzione abituale dell'impianto in kWh/giorno, ricavata da dati reali se disponibili;
- durata ipotizzata in giorni;
- quota dell'energia mancante che sarebbe stata destinata all'autoconsumo;
- costo variabile di acquisto in euro/kWh, esclusi i costi fissi;
- valore dell'energia ceduta in euro/kWh, secondo il contratto applicabile.

I valori iniziali `12 kWh/giorno`, `30 giorni`, `50%`, `0,30 €/kWh` e
`0,08 €/kWh` sono **esempi dimostrativi**, non tariffe correnti del mercato.
Sostituiscili prima di presentare lo scenario come riferito a un utente specifico.
Premi **Salva parametri**: vengono conservati sulla UNO Q per i successivi Run.
Le modifiche al modulo non cambiano il risultato fino al salvataggio.

Per applicare la riduzione del test scegli **Dal periodo del confronto**.
In alternativa puoi selezionare **Percentuale ipotizzata manualmente** e inserire
una percentuale: questo scenario e utilizzabile anche senza confronto fisico.

### D. Esegui il confronto

1. Premi **2. Avvia confronto** con il pannello ancora scoperto.
2. Attendi un paio di letture per vedere i valori di energia.
3. Copri reversibilmente una parte del pannello senza muovere la luce o i sensori.
4. Osserva la potenza e la riduzione live, calcolata sulla media di fino a 5
   misure recenti. La media impiega qualche secondo ad assestarsi.
5. Lascia la copertura per 10-20 secondi. La riduzione **sul periodo** confronta
   l'energia di tutto il test, quindi puo differire da quella live.
6. Premi **3. Termina e salva** quando vuoi fissare il risultato della prova oscurata.
7. Premi **Scarica report JSON**. Scarica anche lo storico CSV corrispondente
   dalla sezione Storico elettrico: il report indica il nome del file sorgente.
8. Togli la copertura e mostra il recupero della potenza live. Per misurare
   separatamente il ripristino, premi nuovamente **2. Avvia confronto** con lo
   stesso riferimento e poi termina la seconda prova.

Se togli la copertura prima di terminare la prima prova, il recupero entra nel
calcolo medio dell'intero periodo. Non e un errore, ma va spiegato nella demo.

### E. Ripeti

Per ricominciare con una nuova illuminazione premi **Acquisisci riferimento**.
Questo azzera il confronto visualizzato; i precedenti file restano sulla scheda.
Dopo Stop/Run e sempre richiesto un nuovo riferimento: le condizioni di luce
e carico di un'altra sessione non sono considerate automaticamente confrontabili.

## Calcoli

Per due nuove misure valide consecutive, con intervallo `dt` tra timestamp
INA219 maggiore di zero e non superiore a 2,5 s:

```text
energia_misurata_Wh += (P_precedente_W + P_attuale_W) / 2 × dt_s / 3600
energia_riferimento_Wh += P_riferimento_W × dt_s / 3600
deficit_netto_Wh = max(0, energia_riferimento_Wh − energia_misurata_Wh)
riduzione_periodo_% = 100 × (1 − energia_misurata_Wh / energia_riferimento_Wh)
```

Le pause non sono riempite. Una potenza negativa resta nel CSV grezzo ma e
esclusa da questo calcolo di produzione: non viene trasformata in una perdita
maggiore del 100%. Un rollover di `millis()` viene gestito con sottrazione modulo
2^32; un salto/reset del microcontrollore interrompe l'intervallo confrontabile.

Il riferimento costante e adatto a un breve test controllato. Con sole variabile,
temperatura o carico diversi non e una baseline di rendimento normalizzata e
non permette di attribuire un deficit a un guasto. La potenza misurata fra
pannello e charger e potenza DC in quel circuito, non energia AC domestica.

Il valore ipotetico del deficit del minipannello applica le tariffe e la quota
di autoconsumo inserite anche a quella piccola energia. Non e una bolletta
misurata: per la sua piccola entita puo apparire in notazione scientifica.

### Scenario domestico

```text
energia_mancante_kWh = produzione_giornaliera_kWh × giorni × riduzione_% / 100
costo_autoconsumo_perso = energia_mancante_kWh × quota_autoconsumo × prezzo_acquisto
ricavo_vendita_perso = energia_mancante_kWh × (1 − quota_autoconsumo) × prezzo_vendita
impatto_totale_euro = costo_autoconsumo_perso + ricavo_vendita_perso
```

La percentuale dal confronto viene limitata a 0..100% per lo scenario. Un aumento
di produzione rispetto al riferimento resta visibile con riduzione negativa,
mentre lo scenario non mostra una perdita economica negativa.

Si ipotizzano produzione giornaliera, percentuale di riduzione, ripartizione
dell'energia mancante e tariffe costanti nel periodo. Applicare la percentuale
del minipannello a un impianto domestico e un'ipotesi illustrativa, non una
previsione validata. Costi di riparazione, incentivi, assicurazioni, fiscalita
specifica e profili tariffari orari non sono modellati.

## Persistenza e report

```text
data/analysis/
  economics_settings.json
  reference_<session_id>_<id>.json
  demo_<session_id>_<id>.json
```

- Il riferimento salva media, dispersione, campioni e nome del CSV sorgente.
- Il confronto salva un checkpoint ogni 5 nuove misure e un report finale
  alla pressione di **Termina e salva**.
- Il report contiene energia misurata/attesa, tempo coperto, intervalli esclusi,
  flussi inversi, riferimento, parametri e scenario ipotetico.
- Con browser chiuso, riferimento in raccolta e confronto attivo continuano
  sul lato Linux finche la App resta in Run.
- Un checkpoint con `running: true` e una prova interrotta senza report finale.
  Non viene ripresa automaticamente dopo un riavvio.
- I file salvati rimangono sulla scheda. Il pulsante della dashboard scarica
  l'ultimo report terminato della sessione corrente; i report precedenti sono
  recuperabili dalla cartella `data/analysis/` via ADB/SSH.
- Il report finale conserva i parametri presenti al termine della prova. Se
  successivamente cambi le tariffe, lo scenario nella dashboard si ricalcola,
  ma il report gia terminato conserva le ipotesi originali.
- Un errore di scrittura compare nella dashboard. Se fallisce il salvataggio
  finale, il report resta scaricabile dalla RAM fino a Stop/Run.

## API

| Metodo | Endpoint | Azione |
| --- | --- | --- |
| GET | `/api/status` | Include stato del confronto e risultati in `economics` |
| POST | `/api/economics/reference` | Raccoglie un nuovo riferimento |
| POST | `/api/economics/start` | Avvia un confronto |
| POST | `/api/economics/stop` | Termina e salva il confronto |
| POST | `/api/economics/settings` | Valida e salva il JSON dei parametri |
| GET | `/api/economics/report` | Scarica l'ultimo report terminato |

Questi controlli riguardano l'analisi su Linux e non comandano sensori, attuatori
o firmware. Sono pensati per la rete locale della demo.

## Verifica affidata al team

Il codice non e stato eseguito o distribuito dall'assistente. Verifica:

1. Riferimento stabile accettato; riferimento con luce in movimento rifiutato.
2. Potenza e percentuale che diminuiscono/aumentano coerentemente con la copertura.
3. Energia ferma durante le pause, con ripresa senza integrare attraverso il buco.
4. Report coerente con CSV e parametri salvati.
5. Nuovo riferimento richiesto dopo Run, con tariffe ancora salvate.

I test software in `tests/test_electrical_demo.py` usano esclusivamente segnali
**sintetici**, non risultati sperimentali. Se vuoi eseguirli sul PC:

```powershell
python -m unittest discover -s tests -p test_electrical_demo.py
```

## Riferimenti per scegliere i prezzi

- [ARERA: quota consumi e quote fisse in bolletta](https://www.arera.it/en/bolletta/bolletta-dellelettricita/lo-scontrino-dellenergia).
- [GSE: prezzi di valorizzazione del Ritiro Dedicato](https://assistenza.clienti.gse.it/csm/it/prezzi-gse-per-il-corrispettivo-di-ritiro-dedicato?id=faq&sys_id=1269efc2dbbc0050d6647cde3b96194a).
- [ARERA: riferimento Maggior Tutela ottobre-dicembre 2026](https://www.arera.it/comunicati-stampa/dettaglio/elettricita-maggior-tutela-373-nel-iv-trimestre-2026-per-i-clienti-vulnerabili): prezzo complessivo di riferimento 0,4343 €/kWh per il cliente tipo vulnerabile; non e il prezzo variabile di ogni contratto e non viene usato automaticamente dal calcolatore.
