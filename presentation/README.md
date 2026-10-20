# SolarEcho AI - Presentation

Progetto Remotion del video corrente: **108 secondi, 1920 x 1080, 30 fps**,
MP4 H.264 con musica originale e testi, senza voce narrante.

La sorgente corrente include circa 30 secondi di esplorazione hardware con nove
componenti illustrativi animati separatamente. La v4 e esportata in MP4;
gli MP4 v2 e v3 esportati in precedenza sono conservati.

## Struttura

- `src/showcase/`: gli otto capitoli e la timeline del montaggio corrente.
- `public/footage/`: due clip e quattro foto usate nel montaggio; le risorse
  sono rimaste identiche durante il riordino.
- `public/social-v2/`: musica, ritagli autentici della dashboard e inserto Telegram.
- `public/exploded/`: illustrazione del prototipo e manifest con prompt e provenienza.
- `materials/originals/`: foto e video originali del team.
- `tools/prepare_social_v2.py`: preparazione delle risorse e della musica.
- `tools/qa-showcase.cjs`: controllo opzionale dei fotogrammi.
- `docs/SHOWCASE.md`: contenuto, provenienza e limiti del video.

Gli MP4 esportati sono in `../video_output/`, esclusi da Git.
Le composizioni storiche da 45 e 118 secondi, le vecchie voci e gli strumenti
specifici sono stati rimossi. Gli MP4 gia consegnati e la documentazione
storica di provenienza sono stati conservati.

## Anteprima e modifica

Dalla cartella `presentation`, con Node.js e npm disponibili:

```powershell
npm ci
npm run dev
```

Aprire l'indirizzo stampato dal terminale e selezionare `SolarEcho-Showcase-108`.
Con la porta predefinita: <http://localhost:3000/SolarEcho-Showcase-108>.
Le scene sono disponibili anche nella cartella Studio `Showcase-Scene`.

## Esportazione

Solo quando si vuole rigenerare il file:

```powershell
npm run render
```

Il comando, disponibile anche come `npm run render:showcase`, scrive
`../video_output/SolarEcho_AI_showcase_componenti_v4.mp4` e sostituisce l'eventuale file
esistente. `npm run preview` esporta una copia a 720p in
`../video_output/SolarEcho_AI_showcase_componenti_v4_anteprima.mp4`.
La v4 e esportata e verificata; la precedente v3 e conservata.

## Risorse e provenienza

- [Guida al montaggio](docs/SHOWCASE.md)
- [Verifica dell'MP4 v4 con tutti i componenti](docs/showcase/verifica_export_componenti_v4.json)
- [Verifica dell'MP4 v3 con esploso](docs/showcase/verifica_export_esploso_v3.json)
- [Verifica del precedente MP4 v2](docs/showcase/verifica_export.json)
- [Originali del team](materials/README.md)
- [Origine delle clip e foto condivise](public/footage/provenance.json)
- [Documentazione del video precedente](docs/archive/hackathon/README.md)

Le risorse usate dal renderer sono incluse. Per rigenerare i ritagli e la
musica, dalla radice della repository usare Python con NumPy e Pillow:

```powershell
python presentation/tools/prepare_social_v2.py
```

Lo script usa FFmpeg incluso nell'installazione Remotion. Non ricostruisce
la clip `public/footage/demo.mp4` o le foto convertite, che sono conservate
nel repository. `public/footage/dashboard.mp4` e la copia canonica della
registrazione schermo originale.

Per controllare facoltativamente le sorgenti: `npm run lint`.
`npm run qa:showcase` produce fotogrammi di verifica senza esportare un MP4.
