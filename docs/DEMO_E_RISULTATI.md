# Demo e risultati

Aggiornamento documentale: **17 ottobre 2026**. Questa pagina riassume le
evidenze già raccolte; non introduce nuove prove o misure.

## Cosa dimostra il prototipo

SolarEcho AI acquisisce la risposta vibrazionale di un pannello a piccoli
impatti controllati. Il piezo avvia la cattura, il Modulino Movement misura
l'accelerazione XYZ e Arduino UNO Q salva gli eventi ed esegue l'analisi locale.
La dashboard affianca i segnali alle misure elettriche e permette una
segnalazione manuale al tecnico tramite Telegram.

| Evidenza disponibile | Cosa permette di mostrare |
| --- | --- |
| Riprese della pallina e del prototipo | Impatto fisico controllato sul pannello |
| CSV e JSON delle acquisizioni | Campioni temporali, frequenza effettiva e qualità della cattura |
| Registrazione della dashboard | Grafico XYZ, misure elettriche, score e soglia visualizzati |
| Ripresa del LED e del messaggio sul telefono | Risposta visibile e comunicazione dei dati al destinatario |
| Test sintetico dichiarato | Inferenza su una firma alterata via software e relativo percorso di allerta |

Le riprese del pannello e la registrazione dello schermo sono inserti montati:
non dimostrano la sincronizzazione fra uno specifico lancio e lo score mostrato.
L'invio Telegram è manuale e richiede Internet; l'inferenza è locale e può
funzionare offline dopo l'installazione di modello e dipendenze.

## Sequenza raccontata nel video

1. **Impatto:** la pallina colpisce il pannello; il piezo fornisce il trigger.
2. **Acquisizione:** si conserva la risposta XYZ prima e dopo l'evento.
3. **Analisi locale:** il modello restituisce uno score, confrontato con la
   soglia configurata. Uno score oltre soglia può richiedere un'ispezione.
4. **Test sintetico:** una copia del segnale viene alterata esplicitamente via
   software. La dicitura di test resta visibile e il grezzo viene conservato.
5. **Segnalazione:** dashboard e LED mostrano l'allerta; l'utente può inviare
   i dati del pannello al destinatario Telegram.

Video corrente: [guida e materiali del montaggio di 90 secondi](../presentation/docs/SHOWCASE.md).
Schema già disponibile: [schema elettrico](hardware/design/SolarEcho-AI-schematic_schem.jpg)
e [vista breadboard](hardware/design/SolarEcho-AI-schematic_bb.jpg).

## Numeri disponibili e loro significato

### Acquisizioni conservate

| Lotto | Dati documentati | Interpretazione |
| --- | --- | --- |
| Demo, sessione dell'11 ottobre | 31 eventi di origine: 28 validi, 3 esclusi; suddivisione in 18 training, 5 calibrazione e 5 test | Preparazione e qualità del dataset; non è una misura dell'accuratezza AI |
| Prove storiche del 10 ottobre | 28 acquisizioni iniziali, 22 mantenute: 8 normali, 8 con massa, 6 dopo ripristino | Sono disponibili segnali fisici in tre condizioni; la separazione da parte del modello non è dimostrata dal controllo dei file |
| Prove storiche mantenute | Frequenza media circa 104,12–104,25 Hz; massimo intervallo fra campioni circa 11,40 ms | Regolarità temporale del lotto esaminato; non è la banda utile del sensore |

Fonti: [report originale dello split demo](../datasets/manifests/archive/demo_split_report.json),
[verifica storica delle tre condizioni](archive/tests/VERIFICA_TEST_20261010.md)
e [indice dei dataset](../datasets/README.md). Gli eventi esclusi restano
archiviati e non sono stati nascosti nel conteggio iniziale delle acquisizioni.

### Esempi visualizzati nella registrazione

| Origine mostrata | Score | Soglia mostrata | Lettura corretta |
| --- | ---: | ---: | --- |
| Acquisizione reale | 0,6035 | 0,3000 | L'esempio supera già la soglia; non dimostra che il modello riconosca correttamente gli impatti normali |
| Firma alterata artificialmente | circa 82,1386 | 0,3000 | Il test software supera la soglia; non rappresenta un danno fisico misurato |

Questi valori provengono dagli inserti della registrazione, documentati nel
[manifest dei materiali](../presentation/public/social-v2/provenance.json).
Sono esempi visualizzati, non medie, probabilità o un confronto sperimentale
appaiato fra pannello integro e pannello danneggiato. Il significato dello score
e della soglia è descritto nella [scheda del modello](MODEL_CARD.md).

## Cosa resta da validare

- Riconoscimento di modifiche meccaniche reali, con impatti ripetibili e
  successivo ripristino, su prove nuove rispetto a training e calibrazione.
- Tasso di rilevamento degli impatti, falsi trigger e tempo non monitorato
  durante il trasferimento, usando un conteggio indipendente dei lanci.
- Falsi allarmi e anomalie mancate con modello e soglia fissati prima del test.
- Tempo medio di inferenza su un lotto definito: il codice registra la durata,
  ma qui non è disponibile una misura aggregata da riportare.
- Vantaggio rispetto a una soglia convenzionale e benefici economici sul campo.

Non si dichiara una percentuale di accuratezza sui danni. Un calo di potenza
ottenuto oscurando il pannello dimostra una variazione di illuminazione:
non dimostra che gli impatti ne siano la causa. Le proiezioni economiche
restano uno [scenario ipotetico](DEMO_ECONOMICA.md).

## Versione dimostrata e repository corrente

Il video documenta la versione utilizzata dal team nella demo. Il successivo
refactoring di logger e preprocessing e il riordino della repository hanno
ricevuto controlli statici; i test aggiornati e la prova sulla UNO Q non sono
stati eseguiti dall'assistente. Non si attribuiscono alla nuova revisione
prove hardware effettuate sulla versione precedente.
