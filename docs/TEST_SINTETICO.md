# Test sintetico della firma vibrazionale

Il generatore produce perturbazioni software di acquisizioni reali del gruppo
test. Non addestra modelli, non esegue inferenza e non dimostra il rilevamento di
danni fisici. Gli originali vengono conservati.

## Generazione

Dalla radice del repository, con Python 3.9 o successivo:

```powershell
python tools/generate_synthetic_impacts.py --input datasets/edge_impulse/demo_test_v1 --output datasets/edge_impulse/demo_synthetic_v1
```

L'output deve essere nuovo: lo script rifiuta sovrascritture. Il lotto di input
deve essere un export SolarEcho di test normale, in g, con il suo report.

## Trasformazioni

Ogni impatto genera tre copie, con parametri fissati prima dell'inferenza:

| Variante | Operazione dopo il trigger |
| --- | --- |
| `attenuated` | Moltiplica per 0,5 lo scostamento dalla media pretrigger, per asse |
| `amplified` | Moltiplica per 2 lo scostamento dalla media pretrigger, per asse |
| `added_oscillation` | Aggiunge su Z una sinusoide a 12 Hz con ampiezza iniziale 0,08 g e decadimento esponenziale di 0,45 s |

Il pretrigger rimane invariato. La media pretrigger rappresenta l'offset iniziale,
comprendente la gravita: non viene moltiplicata. Timestamp, frequenza, durata,
ordine degli assi e unita rimangono quelli dell'export di origine.

La trasformazione oscillatoria e `0.08 * exp(-t/0.45) * sin(2*pi*12*t)`, con
`t` in secondi dal trigger. Non simula una frequenza propria misurata del pannello.
La moltiplicazione modifica anche il rumore e l'eventuale deriva dopo il trigger:
e una perturbazione del segnale, non un modello fisico del danno.

### Profilo stress per la demo software

```powershell
python tools/generate_synthetic_impacts.py --input datasets/edge_impulse/demo_test_v1 --output datasets/edge_impulse/demo_synthetic_stress_v1 --profile stress
```

Produce una copia per evento, aggiungendo oscillazioni persistenti dopo il
trigger: ampiezza 0,35 g su ciascun asse, frequenze X/Y/Z di 8/17/29 Hz e rampa
iniziale di 50 ms. La formula per asse e
`a_originale + min(1, t/0.05) * 0.35 * sin(2*pi*f*t)`, con `t` in secondi.

Questo profilo e stato aggiunto dopo i risultati delle perturbazioni moderate.
E un nuovo caso dimostrativo deliberatamente distante dalla baseline, non una
prova indipendente di efficacia su alterazioni fisiche. I parametri sono fissati
prima della sua inferenza. Conservare anche i risultati precedenti e riportare
gli eventuali mancati rilevamenti. Il superamento della soglia non e garantito.

Caricare i cinque CSV in `demo_synthetic_stress_v1/test` nel gruppo Testing, con
etichetta `anomaly`. I nomi includono `synthetic_stress_sustained`. Confrontare i
singoli score con quelli dei cinque originali `no anomaly`; non confondere le
metriche aggregate con quelle dei precedenti quindici test sintetici.

I CSV hanno colonne `timestamp,accX,accY,accZ` e prefisso
`anomaly.synthetic_<variante>`. `synthetic_report.json` conserva parametri, hash,
evento di origine e statistiche del segnale originale e alterato. Queste
statistiche sono misure dei file, non score di inferenza AI.

## Uso su Edge Impulse

1. Mantieni il modello addestrato e la soglia attuale.
2. Apri Data acquisition, Upload data.
3. Carica soltanto i CSV in `demo_synthetic_v1/test` nella destinazione Testing.
4. Assegna esplicitamente l'etichetta `anomaly`.
5. Conserva i cinque originali in Testing con etichetta `no anomaly`.
6. Esegui nuovamente Model testing. Apri i risultati per leggere gli score.
7. Confronta ogni variante con il suo originale e riporta anche le trasformazioni
   non riconosciute. Il report permette di risalire alla coppia di origine.

Non spostare le copie nel Training e non modificare la soglia per ottenere un
risultato desiderato su questi test. Se si usano queste copie per scegliere
nuovi parametri, diventano dati di sviluppo: per una valutazione successiva
servono altri eventi separati.

Con cinque originali e tre varianti si ottengono quindici copie sintetiche,
correlate fra loro. Non sono quindici impatti fisici aggiuntivi. Una metrica
aggregata su originali e copie descrive esclusivamente questo insieme di prova.

## Presentazione

Usare la dicitura **TEST SINTETICO - firma alterata artificialmente** nel grafico,
nella dashboard e negli eventuali messaggi. Questa dicitura deve accompagnare
anche un'eventuale accensione del LED nella modalita demo.

Il pulsante di test nella dashboard usa ora lo stesso profilo stress:
[avvio e procedura](AI_INTEGRAZIONE.md). Il generatore resta uno strumento offline
separato. La validazione su alterazioni meccaniche reali
richiede impatti fisici con modifica reversibile e successivo ripristino.
