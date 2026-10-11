# SolarEcho AI — sceneggiatura hackathon

**Durata pianificata: 118 secondi / 3.540 fotogrammi a 30 fps.**
**Stato: bozza pronta per l'integrazione delle riprese fisiche attese.**

Le durate comprendono le transizioni. Nessun risultato visivo viene inventato.
Le inquadrature fisiche saranno selezionate dopo l'analisi dei nuovi file.
La registrazione disponibile documenta acquisizione, AI e segnalazione.

## 00:00–00:18 — Il problema

**Voce prevista**

«Un impatto può durare un istante. Le sue conseguenze possono durare anni.
Grandine, vento e urti mettono alla prova i pannelli fotovoltaici.
Un'alterazione non sempre si vede subito. Capire quando controllare significa
proteggere produzione, tempo e risorse.»

**Testi essenziali**

- Un istante.
- Conseguenze nel tempo.
- E se il pannello potesse avvisarci?

**Immagini**: apertura su pannello reale; dettaglio e impatto controllato,
se presenti nei nuovi materiali. Richiami a grandine e vento con grafica
esplicativa, senza spacciare la prova con pallina per evento meteorologico.

**Regia**: primo suono breve, nero iniziale, titolo con ingresso preciso,
alternanza di inquadrature ampie e dettagli. La parola «danno» non compare
come risultato attribuito a un urto osservato.

## 00:18–00:38 — La soluzione

**Voce prevista**

«SolarEcho AI ascolta la firma vibrazionale del pannello. Il piezo rileva
l'impatto. Il sensore di movimento misura le vibrazioni sui tre assi.
Arduino UNO Q raccoglie i dati e li analizza sul dispositivo:
è Edge AI, intelligenza artificiale locale.»

**Testi**: SOLARECHO AI / Piezo: trigger / IMU: vibrazioni / UNO Q: analisi locale.

**Immagini**: prototipo reale e fotografie dei componenti; callout soltanto
su componenti identificabili. Schema essenziale sensori → UNO Q → dashboard.
INA219 può essere mostrato come monitor elettrico, separato dal rilevamento
delle anomalie vibrazionali.

**Regia**: reveal del nome, dettagli hardware, linee sottili e tre etichette
animate in successione. Esplicitare il contributo dell'IMU evita di attribuire
al solo piezo la forma d'onda XYZ.

## 00:38–00:80 — Funzionamento e demo autentica

### 00:38–00:47 — Impatto

**Voce**: «Durante un impatto controllato, il sistema registra la risposta
del pannello. Rilevare l'urto è il primo passo: non significa aver rilevato un danno.»

**Immagini**: lancio reale, contatto e reazione. Eventuale replay a metà
velocità chiaramente identificato; suono dell'urto solo se disponibile o
effetto discreto usato come sound design, senza alterare la dimostrazione.

### 00:47–00:57 — Acquisizione

**Voce**: «La dashboard mostra l'acquisizione: le vibrazioni diventano
una traccia misurabile, salvata insieme ai dati dell'evento.»

**Immagini**: registrazione dashboard circa 18–23 s, grafico XYZ.
Una traccia CSV della repository può spiegare il segnale, con etichetta
«Acquisizione dal dataset» se non è identificabile come lo stesso impatto filmato.

### 00:57–00:69 — Analisi locale

**Voce**: «Il modello confronta il segnale con il comportamento di riferimento.
Lo score indica quanto la risposta si discosta dalla baseline.
Non è una percentuale di danno.»

**Immagini**: dashboard circa 23–26 s e schema animato del percorso reale.
Mostrare i valori originali, senza trasformare lo score in probabilità.

### 00:69–00:80 — Segnalazione e limiti della prova

**Voce**: «Oltre soglia, viene consigliata un'ispezione. La demo mostra anche
una firma alterata artificialmente: è un test software, distinto dalla
validazione dei danni fisici.»

**Immagini**: dashboard circa 43–47 s, «Ispezione consigliata», LED rosso acceso
come stato nell'interfaccia. Ripresa del LED fisico solo se realmente disponibile.
Breve inserto del test a circa 27–33 s con dicitura grande e persistente
«TEST SINTETICO — firma alterata artificialmente».

**Regia**: la catena «Impatto → Vibrazione → Analisi AI → Segnalazione»
si completa. Non attribuire la segnalazione della registrazione a una nuova
ripresa se manca una corrispondenza verificabile fra gli eventi.

## 00:80–01:42 — Valore economico

**Voce prevista**

«Per chi gestisce un impianto, la domanda è: dove intervenire prima?
Ai controlli programmati, SolarEcho AI affianca segnali utili per dare
priorità alle ispezioni. L'obiettivo è ridurre i controlli superflui,
indirizzare gli interventi e limitare i costi evitabili.»

**Confronto animato**

| Controlli programmati | Manutenzione supportata da SolarEcho AI |
| --- | --- |
| Visite secondo calendario | Eventi e variazioni osservabili |
| Tempo dedicato ai controlli | Priorità alle situazioni sospette |
| Risorse per ispezioni diffuse | Interventi potenzialmente più mirati |

**Messaggio**: «Meno controlli inutili. Interventi più mirati.
Costi potenzialmente ridotti.»

Benefici prospettici, senza percentuali, tariffe, ROI o risparmi misurati.
Non si afferma che il prototipo sostituisca le ispezioni o abbia già ridotto i costi.
La sezione economica della dashboard può comparire come strumento di scenario,
con dicitura «Scenario ipotetico», se utile al montaggio finale.

## 01:42–01:52 — Innovazione

**Voce prevista**

«Sensori accessibili, firma vibrazionale e analisi locale.
Un prototipo concreto verso una manutenzione più intelligente.
La validazione su alterazioni fisiche resta il prossimo passo.»

**Immagini**: montage reale di pannello, componenti, acquisizione e segnalazione.
Tre parole forti: FIRMA VIBRAZIONALE / EDGE AI / ISPEZIONI MIRATE.

## 01:52–01:58 — Finale

**Voce prevista**

«SolarEcho AI. Il pannello che riconosce i propri danni.»

**Immagini**: ripresa finale reale del prototipo, nome e slogan approvato.
Contesto già spiegato: segnalazione di possibili anomalie, nessuna diagnosi certa.
Breve indicazione «Prototipo sperimentale»; musica risolta e dissolvenza.

## Audio e sottotitoli

La voce italiana viene generata solo dopo aver fissato il montaggio e verificato
la qualità del servizio disponibile. È presente una voce italiana locale
Windows (Microsoft Elsa Desktop); non sono configurate chiavi TTS esterne.
Se non si ottiene un parlato adeguato, la versione completa userà titoli,
testi brevi e musica originale, come autorizzato.
Se viene aggiunto il parlato: musica abbassata e sottotitoli italiani sincronizzati.

## Verifiche necessarie sui nuovi materiali

- Identificare visivamente pannello, UNO Q, piezo, IMU e altri componenti mostrati.
- Localizzare il contatto reale della pallina fotogramma per fotogramma.
- Stabilire se i risultati della dashboard corrispondono alla ripresa fisica.
- Mostrare un eventuale LED soltanto nel contesto e nell'origine corretti.
- Conservare il carattere sintetico degli esperimenti software.
