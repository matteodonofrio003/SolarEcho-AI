from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'video_output'
records=json.loads((OUT/'narrazione.json').read_text(encoding='utf-8'))
scenes=[('00:00–00:18','Il problema','problema','Fotografia al sole → prova controllata all’aperto in replay 0,5× → push-in video del pannello. Titoli cinematografici con richiamo a grandine, vento e urti. Nessuna grandinata simulata presentata come reale.'),('00:18–00:38','La soluzione','soluzione','Reveal SolarEcho AI; fotografia frontale; orbit video; dettaglio elettronica e callout UNO Q. Piezo: trigger. IMU: vibrazioni XYZ. Diagramma essenziale del percorso.'),('00:38–00:47','Demo: impatto','impatto','Ripresa principale: sorgente 6,30–9,80 s a velocità normale; replay da 7,15 s a metà velocità. Nessuna diagnosi di danno associata al contatto.'),('00:47–00:57','Demo: acquisizione','acquisizione','Dashboard da 19,30 a 21,90 s, poi fermoimmagine autentico al secondo 22. Grafico originale XYZ, unità g e tempo dal trigger in ms. Filmato fisico e registrazione sono inserti montati: non si dichiara una sincronizzazione temporale tra le due sorgenti.'),('00:57–01:09','Demo: analisi AI','analisi','Dettaglio dello score reale 0,6035 dal fotogramma a 24 s. Soglia configurata 0,3000; nessuna probabilità di danno. Poi laptop nella ripresa principale e schema Impatto → Vibrazione → Analisi AI → Segnalazione.'),('01:09–01:20','Demo: risultato e limiti','risultato','Avviso originale “Ispezione consigliata” dal fotogramma a 44 s, affiancato alla ripresa del LED. Inserto test sintetico: video 29–30 s, poi fermoimmagine a 29 s; indicazione persistente di test software, non prova di danno fisico.'),('01:20–01:42','Valore economico','economia','Confronto animato tra calendario e priorità; schema illustrativo senza conteggi o percentuali. Chiusura: meno controlli inutili, interventi più mirati, costi potenzialmente ridotti. Benefici da validare.'),('01:42–01:52','Innovazione','innovazione','Montage sensori, elettronica, prototipo con laptop. Analisi locale e firma vibrazionale. Prossimo passo esplicito: validazione del modello su alterazioni fisiche.'),('01:52–01:58','Finale','finale','Prototipo reale, nome e slogan richiesto. Indicazione “Prototipo sperimentale”. Risoluzione musicale originale e dissolvenza al nero.')]
byname={r['name']:r for r in records}
script='# SolarEcho AI — sceneggiatura definitiva\n\nDurata: **118 secondi**, 3.540 fotogrammi a 30 fps. Formato 16:9, Full HD.\n\nVoce italiana neurale Diego; sottotitoli sincronizzati alle parole e inclusi nel video. Musica originale composta proceduralmente per questo montaggio.\n\n'
for time,title,name,visual in scenes:
 r=byname[name]
 script+=f'## {time} — {title}\n\n**Voce:** {r["text"]}\n\n**Immagini e regia:** {visual}\n\n**Audio:** ingresso voce a {r["start"]:.1f} s; durata {r["duration"]:.2f} s. Musica sotto il parlato.\n\n'
script+='## Correttezza tecnica\n\nIl piezo rileva il trigger dell’impatto; l’IMU acquisisce le vibrazioni XYZ. La forma d’onda non è attribuita al piezo. L’AI locale integrata su UNO Q confronta la firma con il riferimento; lo score non è una percentuale di danno. L’allerta è sperimentale e propone un controllo. Il test sintetico è distinto dalla prova fisica e dalla validazione su danni. Nessun risparmio, precisione o risultato di danno viene inventato. Lo slogan finale esprime il concept e resta accompagnato dal contesto sperimentale.\n'
(OUT/'sceneggiatura.md').write_text(script,encoding='utf-8')
story='# SolarEcho AI — storyboard definitivo\n\nLe transizioni principali sono dissolvenze di 15 fotogrammi; gli inserti della demo usano tagli netti. Fotografie con zoom controllato; titoli animati in opacità e posizione. Colori: blu notte, ciano, bianco, accenti solari.\n\n| Tempo | Sequenza e sorgenti | Testi / effetti |\n|---|---|---|\n'
rows=[('0–4,5','IMG20261011143930.jpg, pannello al sole','Un impatto. Un istante. / zoom lento'),('4,5–9','VID20261011145827.mp4 da 1,45 s, replay 0,5×','Grandine · Vento · Urti / Prova controllata'),('9–18','VID20261011143706.mp4, push-in 0,57×','Quando serve controllare?'),('18–23','IMG20261011143543.jpg','Reveal SolarEcho AI'),('23–29','VID20261011143749.mp4 da 0,3 s','Piezo: impatto / IMU: vibrazioni XYZ'),('29–38','IMG20261011143612.jpg','UNO Q / Edge AI / callout e diagramma'),('38–41,5','VID20261011150931.mp4 da 6,30 s','La prova è reale / audio sorgente attenuato'),('41,5–47','Stesso video da 7,15 s a 0,5×','Urto rilevato. Danno da verificare. / replay dichiarato'),('47–57','Registrazione dashboard da 19,30 s; poi fotogramma 22 s','Forma d’onda reale, nessuna ricostruzione numerica'),('57–60,5','Fotogramma dashboard 24 s, ritaglio carta ultimo score reale','0,6035 / soglia 0,3000 / nessuna probabilità'),('60,5–69','VID20261011150931.mp4 da 24,20 s','Schema animato del flusso di elaborazione'),('69–74','Fotogramma dashboard 44 s + video principale da 19,10 s a 0,2×','Ispezione consigliata / LED reale / nessun danno certo'),('74–80','Dashboard 29–30 s + fermoimmagine a 29 s','TEST SINTETICO, etichetta persistente'),('80–94','Grafica animata, fondo pannello reale','Calendario vs priorità / schema illustrativo'),('94–102','Confronto conclusivo e obiettivi','Meno controlli inutili / costi potenzialmente ridotti'),('102–105,5','IMG20261011143550.jpg','Sensori accessibili'),('105,5–109','IMG20261011143612.jpg','Firma vibrazionale + Edge AI'),('109–112','VID20261011145659.mp4 da 5,50 s','Validazione sul campo: prossimo passo'),('112–118','IMG20261011143543.jpg','SolarEcho AI / slogan / prototipo sperimentale / fade out')]
for a,b,c in rows:story+=f'| {a} s | {b} | {c} |\n'
story+='\n## Trattamento e integrità delle sorgenti\n\nI filmati telefonici sono realmente verticali, con metadati di rotazione −90°. Sono convertiti in H.264 720×1280 a 60 fps per il montaggio, mantenendo proporzioni e contenuto. Il master è 1920×1080, 30 fps. Leggera correzione cromatica uniforme. Nessuna interpolazione di impatti, danni aggiunti o modifica dei risultati. I fermoimmagine provengono dalla registrazione originale e sono dichiarati. La linea grafica collega analisi locale ed elettronica reale; la scheda UNO Q e visibile nella fotografia posteriore. Gli altri componenti sono spiegati per funzione, senza etichette su elementi di identificazione incerta.\n\nI quadrati nella comparazione economica sono elementi grafici illustrativi e non rappresentano un numero di pannelli, visite o un risparmio misurato. Nessuna notifica Telegram automatica è attribuita al modello.\n'
(OUT/'storyboard.md').write_text(story,encoding='utf-8')
inventory=json.loads((OUT/'analisi/inventario.json').read_text(encoding='utf-8'))
analysis='# Analisi dei materiali\n\n17 file analizzati: 6 fotografie e 11 video, inclusa la registrazione della dashboard. Metadati completi in `analisi/inventario.json` e `probe-*.json`; contatti visivi estratti con FFmpeg in `analisi/contact-sheet-*.jpg`, `photos.jpg` e `impatti/`.\n\n| File | Formato / durata | Contenuto e scelta |\n|---|---|---|\n'
selection={'IMG20261011143543.jpg':'Selezionata: frontale per reveal/finale','IMG20261011143550.jpg':'Selezionata: sensore laterale e pannello','IMG20261011143558.jpg':'Esclusa: frontale simile, angolo meno utile','IMG20261011143612.jpg':'Selezionata: elettronica, UNO Q e cablaggi','IMG20261011143914.jpg':'Esclusa: pannello più piccolo rispetto all’altro scatto al sole','IMG20261011143930.jpg':'Selezionata: apertura e sfondo economico','Registrazione 2026-10-11 151111.mp4':'Selezionata: grafico XYZ, score reale, avviso e test sintetico','VID20261011143651.mp4':'Riserva: simile al push-in selezionato','VID20261011143706.mp4':'Selezionata: avvicinamento al pannello','VID20261011143749.mp4':'Selezionata: orbita e integrazione fisica','VID20261011143801.mp4':'Esclusa: pan ripetitivo','VID20261011145644.mp4':'Esclusa: composizione meno chiara e persona in primo piano','VID20261011145659.mp4':'Selezionata: laboratorio all’aperto e laptop','VID20261011145827.mp4':'Selezionata: seconda prova d’impatto all’aperto, apertura','VID20261011150931.mp4':'Selezionata: demo principale, lancio, laptop e LED','VID20261011151038.mp4':'Esclusa: inserto Telegram troppo breve','VID20261011151045.mp4':'Riserva analizzata: LED e telefono; non attribuita all’AI una notifica automatica'}
for item in inventory:
 name=Path(item['file']).name
 if item['type']=='photo':spec=f"JPEG {item['width']}×{item['height']}"
 else:spec=f"{item['codec']} {item['width']}×{item['height']}, {item['duration_s']:.3f} s, {item['fps']} fps, AAC"
 analysis+=f'| {name} | {spec} | {selection.get(name,"Analizzato")} |\n'
analysis+='\n## Qualità e momenti scelti\n\nFotografie nitide, luce naturale; scatto posteriore indispensabile per mostrare UNO Q. Video telefonici verticali, ripresa a mano e alcune riflessioni sul pannello; preservata la geometria, scelti segmenti brevi e leggibili. Lo schermo del laptop in esterno è meno leggibile: affiancato a ritagli della registrazione originale. Il master non ingrandisce artificialmente il testo del laptop come se fosse un’interfaccia nuova.\n\nIl contatto della pallina è visibile attorno al fotogramma originale con PTS 7,579867 s (risoluzione temporale circa 0,0167 s); il rilascio è precedente. La griglia `impatti/contatto-preciso.jpg` e `contatto-pts.json` documentano la verifica sui fotogrammi originali. La selezione 6,3–9,8 s mostra preparazione, contatto e reazione; il replay 7,15–9,9 s a metà velocità non modifica la traiettoria. La seconda prova all’aperto contiene un contatto intorno a 1,9 s. Le griglie dense estratte consentono di verificare entrambe.\n\nLa dashboard documenta uno score reale 0,6035 e una soglia 0,3000. Mostra anche uno score sintetico circa 82,1386, mantenuto nella sua sezione e con etichetta esplicita. Si tratta di firma alterata artificialmente. Nessuno dei due valori è interpretato come diagnosi o probabilità di danno. Il LED acceso è osservabile nel video principale.\n\n## Fonti tecniche nel progetto\n\n`README.md`, `AI_INTEGRAZIONE.md`, `TEST_SINTETICO.md`, `DEMO_ECONOMICA.md` e il codice del progetto hanno guidato la distinzione piezo/IMU, analisi locale e limiti sperimentali. I filmati e i dati sono dell’utente; nessuna ripresa artificiale aggiunta.\n'
(OUT/'analisi_materiali.md').write_text(analysis,encoding='utf-8')
readme='''# SolarEcho AI — video hackathon

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
'''
(OUT/'README.md').write_text(readme,encoding='utf-8')
pkg=ROOT/'solarecho-promo/package.json';data=json.loads(pkg.read_text(encoding='utf-8'))
data['scripts']['render:hackathon']='remotion render src/index.ts SolarEcho-Hackathon ../video_output/SolarEcho_AI_finale.mp4 --codec=h264 --crf=18 --audio-bitrate=256k --pixel-format=yuv420p --color-space=bt709 --concurrency=3'
data['scripts']['preview:hackathon']='remotion render src/index.ts SolarEcho-Hackathon ../video_output/SolarEcho_AI_anteprima.mp4 --codec=h264 --scale=0.6666666666666666 --crf=25 --audio-bitrate=192k --pixel-format=yuv420p --color-space=bt709 --concurrency=3'
pkg.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Documentation and reusable render scripts updated.')
