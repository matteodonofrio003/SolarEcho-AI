# SolarEcho AI — Ascolta l'energia

Progetto Remotion 4.0.534 con due montaggi in italiano: il promo storico di
**45 secondi** e il video hackathon di **118 secondi**.
Master: **1920 × 1080, 30 fps, H.264, MP4, YUV420p, BT.709**, audio AAC stereo.

## Video hackathon — 118 secondi

Composizione `SolarEcho-Hackathon`, 3.540 fotogrammi, sorgenti in `src/hackathon/`
e asset in `public/hackathon/`. Dalla cartella di questo progetto:

```powershell
npm run preview:hackathon
npm run render:hackathon
```

Le consegne sono `../video_output/SolarEcho_AI_anteprima.mp4` e
`../video_output/SolarEcho_AI_finale.mp4`. La [guida hackathon](../video_output/README.md)
descrive rigenerazione, narrazione, sottotitoli e verifiche.

Il montaggio mostra l'integrazione AI locale sperimentale; lo stato corrente
dell'app è descritto in [Integrazione AI](../docs/AI_INTEGRAZIONE.md).

## File del promo storico — 45 secondi

- `out/SolarEcho-AI-promo-1080p.mp4`: video finale.
- `out/SolarEcho-AI-anteprima-720p.mp4`: anteprima completa 1280 × 720 con audio.
- `out/poster.png`: copertina.
- `out/storyboard.jpg`: riepilogo delle sei scene.
- `out/verification.json`: verifica tecnica con FFprobe.

## Anteprima e rendering

Da questa cartella:

```powershell
npm ci
npm run dev
npm run preview
npm run render
npm run lint
```

Studio: http://localhost:3000/SolarEcho-Promo (oppure l'URL stampato dal server).
Le sei scene sono registrate anche separatamente nella cartella `Scene` di Studio.
L'anteprima usa scala `0.6666666666666666` per ottenere dimensioni intere.
Il video contiene 1.350 fotogrammi.

## Regia

| Tempo | Scena | Contenuto |
| --- | --- | --- |
| 00–08 s | Apertura | Ogni pannello ha una voce; pannello, sole e anelli animati |
| 07–16 s | Acquisizione | Firma vibrazionale reale, tre assi e finestra di 2,2 s |
| 15–23 s | Hardware | UNO Q, IMU, piezo, INA219 e involucro CAD |
| 22–31 s | Dashboard | Misure, risposta all'impatto, archivio CSV/JSON |
| 30–38 s | Ricerca AI | Anomaly explorer; modello in sviluppo |
| 37–45 s | Chiusura | Ascolta l'energia; esplora il prototipo |

Sovrapposizioni di 1 secondo con dissolvenze e tendine. Animazioni, titoli,
sfocatura di ingresso, particelle e movimenti deterministici, guidati dai frame.
Verde acqua e ambra su fondo scuro; palette derivata dalla dashboard originale.
Tutti gli asset sono locali.

## Materiali del progetto

- `../README.md`, `../docs/SRS.md`, `../docs/COMPONENTI.md`: funzioni e stato del prototipo.
- `../app/assets/index.html` e `style.css`: identità e funzioni della dashboard.
  La dashboard nel video è una ricostruzione grafica, non una registrazione della scheda.
  I valori elettrici restano non disponibili; i 230 campioni sono reali.
- `../datasets/raw/normal_test/20261010_171420_45cdb44c_event_0001.csv`: traccia IMU.
  Agli assi è sottratta la mediana pretrigger; il CSV originale è intatto.
- `../Solar_Housing.stl`: rendering delle 29.804 facce dell'involucro originale.
- `../risultato_training1.png`: ritaglio del grafico nella scena ricerca AI.
  Anche `test.png` è stato esaminato; le metriche non sono usate come promessa di prestazioni.
- Font Bahnschrift e Segoe UI dell'installazione locale Windows.

I testi del promo storico conservano lo stato al momento della sua creazione:
**prototipo sperimentale, AI non attiva, modello in sviluppo**. Questa descrizione
non rappresenta lo stato corrente dell'app. Il video non presenta i grafici come
diagnosi di danni.

## Musica originale

`public/solarecho-original-score.wav`: composizione elettronica procedurale
originale di 45 s, 120 BPM, stereo 48 kHz, senza campioni musicali esterni.
Pad, arpeggi, basso, percussioni, transizioni sonore e firma finale.
Riproduzione al volume 0,85. WAV: −16,38 LUFS, true peak −0,98 dBTP;
il volume di composizione riduce il livello nel video.

Rigenerazione asset: `python tools/prepare_assets.py` (NumPy, Pillow, Matplotlib).
Sorgenti React in `src/`; audio e immagini in `public/`.
