# SolarEcho AI — video hackathon

- `SolarEcho_AI_finale.mp4`: master Full HD 1920×1080, 30 fps, H.264, AAC, 118 secondi.
- `SolarEcho_AI_anteprima.mp4`: anteprima 1280×720 dello stesso montaggio finale.
- `sceneggiatura.md`, `storyboard.md`, `analisi_materiali.md`: narrazione, scelte e sorgenti.
- `sottotitoli_it.srt`: sottotitoli esterni; presenti anche nel video.
- `narrazione.json`: testo, tempi, durata e allineamento delle parole.
- `verifica_finale.json`: metadati FFprobe e controlli del file consegnato.

## Modificare il montaggio

Sorgente riutilizzabile: `../solarecho-promo/src/hackathon/`. Ogni scena ha un componente separato; `Hackathon.tsx` definisce timeline e composizioni. La composizione `SolarEcho-Hackathon` ha 3.540 fotogrammi. Il precedente promo di 45 secondi resta disponibile come composizione separata.

In PowerShell, dalla cartella del progetto:

```powershell
cd solarecho-promo
npm ci
npm run dev
npm run render:hackathon
npm run preview:hackathon
```

Studio: `http://localhost:3000/SolarEcho-Hackathon`. Il server deve essere avviato con `npm run dev`.

Le clip sono in `public/hackathon/`. Gli originali in `../materiale_per_video/` restano intatti. `asset-origins.json` identifica le sorgenti. Per cambiare tagli e testi, aprire i componenti delle scene. Per cambiare voce, modificare `video_output/tools/prepare_hackathon.py`, rigenerare e poi renderizzare.

## Rigenerare risorse

Python 3.11+, NumPy e Pillow. FFmpeg/FFprobe inclusi nell’installazione Remotion. Dalla radice:

```powershell
python -m venv .venv-video
./.venv-video/Scripts/Activate.ps1
python -m pip install -r video_output/tools/requirements.txt
python video_output/tools/analyze_materials.py
python video_output/tools/prepare_hackathon.py assets
python video_output/tools/prepare_hackathon.py voice
python video_output/tools/prepare_hackathon.py music
python video_output/tools/write_documentation.py
```

La rigenerazione della voce richiede rete; i WAV pronti sono già inclusi, perciò il rendering non richiede il servizio TTS. Voce italiana `it-IT-DiegoNeural`, sintesi tramite [edge-tts](https://github.com/rany2/edge-tts). Normalizzazione e piccole correzioni di tempo senza cambio d’intonazione; allineamento delle parole ridimensionato con lo stesso fattore. `Narration.tsx` conserva nodi voce/sottotitoli distinti ed editabili. `basic-captions.tsx` è copiato senza modifiche dal componente ufficiale Remotion.

## Musica e integrità

Musica originale generata proceduralmente: pad armonici, arpeggi, percussioni e transizioni sintetizzate dal codice, senza brani o campioni musicali esterni. Il volume lascia spazio al parlato. Un breve tratto della demo conserva l’audio originale attenuato; i replay sono muti. Font locali Windows già inclusi.

L’urto non è presentato come danno certo. Piezo e IMU hanno ruoli distinti. Score e soglia provengono dalla dashboard originale. Il test sintetico è dichiarato e non prova alterazioni fisiche. Il confronto economico è qualitativo: benefici potenziali da validare, senza percentuali di risparmio, costi o ROI inventati. Nessuna sincronizzazione fra registrazione schermata e ripresa fisica viene dichiarata.

## Verifica

`tools/verify_final.py` controlla codec, dimensioni, frame rate, durata, fotogrammi e audio, esegue la decodifica completa ed estrae immagini dal master finale. I risultati sono salvati in `verifica_finale.json`; i log e i fotogrammi di controllo restano in `analisi/`.
