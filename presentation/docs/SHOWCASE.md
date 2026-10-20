# SolarEcho AI — nuovo montaggio, solo musica e testi

Composizione Remotion **SolarEcho-Showcase-108**: 108 secondi, 1920 x 1080,
30 fps. Nessuna voce narrante e audio delle riprese disattivato.
Il precedente `SolarEcho_AI_finale.mp4` resta il video consegnato originale.

## Esplorazione dei componenti — v4 esportata

La scena hardware passa da 370 a 910 fotogrammi (circa 30 secondi).
I nove elementi si separano da un gruppo centrale, si ingrandiscono per funzione
e tornano alla vista d'insieme: pannello FV, supporto 3D, UNO Q, piezo analogico,
Modulino Movement, INA219, solar charger, batteria LiPo e LED con resistenza.
La traccia grafica delle vibrazioni e i collegamenti sono animazioni illustrative,
non nuove misure sperimentali né un cablaggio da riprodurre.

Il charger è rappresentato genericamente: la sua revisione non è confermata.
La scena ricorda che la UNO Q nella demo è alimentata via USB-C. OLED e Grove
piezo digitale non sono rappresentati perché non fanno parte del prototipo attuale.

Asset trasparente generato con ImageGen, geometrie semplificate e animazione
dei singoli elementi in Remotion. [Prompt e provenienza](../public/exploded/components-atlas-v4.provenance.json).
La musica originale a 120 BPM è estesa a 108 secondi e salvata separatamente in
`public/exploded/score-hardware-v4.wav`. Nessuna voce.

La v4 è esportata: [SolarEcho_AI_showcase_componenti_v4.mp4](../../video_output/SolarEcho_AI_showcase_componenti_v4.mp4).
MP4 H.264, 1920 x 1080, 30 fps, 108 secondi, audio AAC stereo a 48 kHz.
Dimensione: 37.368.790 byte (circa 37,4 MB). Decodifica integrale completata
senza errori e sei fotogrammi finali controllati a 20, 28, 39, 43, 92 e 105 secondi.
[Rapporto tecnico e SHA-256](showcase/verifica_export_componenti_v4.json).
Gli MP4 v2 e v3 restano conservati.

## Precedente scena hardware con esploso — v3 esportata

La versione v3 includeva, fra 16 e 28 secondi, una foto reale seguita da
un esploso illustrativo generato dalle fotografie del team con ImageGen.
Testi e richiami ai componenti sono animati in Remotion. I tre gruppi mostrano
pannello, supporto ed elettronica; una riga descrive piezo, Modulino, INA219 e LED.

La dicitura **ESPLOSO ILLUSTRATIVO DA FOTO · GEOMETRIE SEMPLIFICATE** resta visibile.
Le geometrie dei componenti sono approssimate: non è un disegno CAD né una foto
di smontaggio. Il file STL disponibile non è stato importato nel generatore.
Un modulo ottico estraneo al prototipo presente nella prima generazione è stato
rimosso prima dell'inserimento. Prompt, riferimenti e hash sono nel
[manifest dell'illustrazione](../public/exploded/provenance.json).

Durata della v3: **90 secondi, nessuna voce**, musica originale a 120 BPM.
La v3 è esportata: [SolarEcho_AI_showcase_esploso_v3.mp4](../../video_output/SolarEcho_AI_showcase_esploso_v3.mp4).
MP4 H.264, Full HD, 30 fps, 90 secondi, audio AAC stereo a 48 kHz;
30.395.801 byte (circa 30,4 MB). L'MP4 v2 precedente è conservato e il suo hash è invariato.

Decodifica integrale completata senza errori. Controllati i fotogrammi del file
esportato a 24,5, 74 e 87 secondi: etichette leggibili e nessuna sovrapposizione.
[Rapporto tecnico e SHA-256](showcase/verifica_export_esploso_v3.json).

## Anteprima

Dalla cartella `presentation`:

```powershell
npm run dev
```

Aprire l'indirizzo stampato dal terminale e selezionare **SolarEcho-Showcase-108**.
Se Studio usa la porta 3000: <http://localhost:3000/SolarEcho-Showcase-108>.
Premere Play e attivare l'audio del player per ascoltare la base musicale.
I capitoli sono anche disponibili singolarmente nella cartella **Showcase-Scene**.

## Versione precedente già esportata — v2

Versione approvata: [SolarEcho_AI_showcase_v2.mp4](../../video_output/SolarEcho_AI_showcase_v2.mp4).
MP4 H.264, Full HD, 30 fps, 90 secondi, audio AAC stereo a 48 kHz.
Dimensione: 33.155.460 byte (circa 33,2 MB). Solo musica e testi, nessuna voce.

Esportazione completata e decodifica integrale verificata senza errori.
Controllati anche tre fotogrammi estratti dal file finale, a 35, 74 e 87 secondi.
Dettagli tecnici e SHA-256: [verifica_export.json](showcase/verifica_export.json).

Per esportare la versione corrente con esploso dalla cartella `presentation`:

```powershell
npm run render:showcase
```

Il nuovo output è `video_output/SolarEcho_AI_showcase_componenti_v4.mp4`.
Il comando non sovrascrive gli MP4 v2 e v3.

## Sequenza

| Tempo | Contenuto |
| --- | --- |
| 0–6 s | Lancio della pallina, subito visibile |
| 6–16 s | Monitoraggio e destinatari del progetto |
| 16–46 s | Foto reale, nove componenti animati e dettagli per funzione |
| 46–60 s | Acquisizione autentica, poi fermoimmagine leggibile |
| 60–71 s | Score reale registrato 0,6035, soglia 0,3000 e limiti |
| 71–83 s | Test sintetico dichiarato: originale e firma alterata |
| 83–96 s | LED e segnalazione manuale Telegram sul telefono |
| 96–108 s | Nome del progetto, utilita e prossimo passo sperimentale |

Transizioni di 10 fotogrammi sovrapposte: la durata finale e 3.240 fotogrammi.

## Audio

Musica strumentale originale, sintetizzata dal codice a **120 BPM**:
arpeggi, pad, basso e percussioni. Non usa voci, campioni o brani di terzi.
Il ritmo accompagna i cambi scena; gli ultimi secondi chiudono con dissolvenza.
File corrente: `presentation/public/exploded/score-hardware-v4.wav`.
La traccia originale di 90 secondi resta in `public/social-v2/score.wav`.

## Provenienza e limiti

- Riprese e fotografie del team in `presentation/materials/originals/`.
- Esploso generato da foto, dichiarato illustrativo; geometrie semplificate.
- Dashboard originale: nessun numero o andamento viene ridisegnato o falsificato.
- Le riprese fisiche e lo schermo sono inserti montati: non si afferma una
  sincronizzazione tra lancio e specifica traccia mostrata.
- Lo score reale supera gia la soglia in questa prova: e mostrato come esempio
  del percorso di allerta, non come prova di riconoscimento di danni fisici.
- Il test sintetico e esplicitamente separato e non valida modifiche meccaniche.
- Il messaggio Telegram viene inviato manualmente dalla dashboard.
- Nessun risparmio economico o percentuale di accuratezza viene inventato.
- Finale: **Ascoltare il pannello. Guidare la manutenzione.** Prossimo passo:
  validazione su modifiche meccaniche reali.

Manifest: `presentation/public/social-v2/provenance.json`.
Scene e timeline: `presentation/src/showcase/`.

## Rigenerazione delle risorse

Dalla radice, con Python, NumPy e Pillow gia installati:

```powershell
python presentation/tools/prepare_social_v2.py
```

Il comando usa FFmpeg incluso nel progetto Remotion, prepara i ritagli dello
schermo e compone la musica. Non modifica gli originali o il montaggio precedente.

Per rigenerare soltanto la musica della v4, senza toccare le risorse precedenti:

```powershell
python presentation/tools/prepare_social_v2.py --music-only --duration 108 --hardware-end 46 --music-file ../exploded/score-hardware-v4.wav
```

## Controlli

`npm run qa:showcase` verifica che la composizione si carichi e produce quattordici
fotogrammi in `video_output/showcase_componenti_v4/qa/`, senza esportare il video. La verifica visiva riguarda
composizione, leggibilita e contenuti. Ascoltare l'anteprima per valutare il
gusto musicale; la valutazione del timbro e soggettiva.
