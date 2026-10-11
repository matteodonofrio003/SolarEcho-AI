# Analisi dei materiali

17 file analizzati: 6 fotografie e 11 video, inclusa la registrazione della dashboard. Metadati completi in `analisi/inventario.json` e `probe-*.json`; contatti visivi estratti con FFmpeg in `analisi/contact-sheet-*.jpg`, `photos.jpg` e `impatti/`.

| File | Formato / durata | Contenuto e scelta |
|---|---|---|
| IMG20261011143543.jpg | JPEG 3000×3000 | Selezionata: frontale per reveal/finale |
| IMG20261011143550.jpg | JPEG 3000×3000 | Selezionata: sensore laterale e pannello |
| IMG20261011143558.jpg | JPEG 3000×3000 | Esclusa: frontale simile, angolo meno utile |
| IMG20261011143612.jpg | JPEG 3000×3000 | Selezionata: elettronica, UNO Q e cablaggi |
| IMG20261011143914.jpg | JPEG 3000×3000 | Esclusa: pannello più piccolo rispetto all’altro scatto al sole |
| IMG20261011143930.jpg | JPEG 3000×3000 | Selezionata: apertura e sfondo economico |
| Registrazione 2026-10-11 151111.mp4 | h264 1828×924, 83.200 s, 30/1 fps, AAC | Selezionata: grafico XYZ, score reale, avviso e test sintetico |
| VID20261011143651.mp4 | hevc 1920×1080, 6.405 s, 6822000/113561 fps, AAC | Riserva: simile al push-in selezionato |
| VID20261011143706.mp4 | hevc 1920×1080, 5.617 s, 14895000/247927 fps, AAC | Selezionata: avvicinamento al pannello |
| VID20261011143749.mp4 | hevc 1920×1080, 7.217 s, 38430000/640163 fps, AAC | Selezionata: orbita e integrazione fisica |
| VID20261011143801.mp4 | hevc 1920×1080, 5.944 s, 1735000/29089 fps, AAC | Esclusa: pan ripetitivo |
| VID20261011145644.mp4 | hevc 1920×1080, 6.362 s, 90000/1499 fps, AAC | Esclusa: composizione meno chiara e persona in primo piano |
| VID20261011145659.mp4 | hevc 1920×1080, 12.511 s, 66060000/1110721 fps, AAC | Selezionata: laboratorio all’aperto e laptop |
| VID20261011145827.mp4 | hevc 1920×1080, 12.377 s, 4128750/68953 fps, AAC | Selezionata: seconda prova d’impatto all’aperto, apertura |
| VID20261011150931.mp4 | hevc 1920×1080, 47.765 s, 255960000/4288061 fps, AAC | Selezionata: demo principale, lancio, laptop e LED |
| VID20261011151038.mp4 | hevc 1920×1080, 3.343 s, 3712500/72703 fps, AAC | Esclusa: inserto Telegram troppo breve |
| VID20261011151045.mp4 | hevc 1920×1080, 10.224 s, 46980000/907147 fps, AAC | Riserva analizzata: LED e telefono; non attribuita all’AI una notifica automatica |

## Qualità e momenti scelti

Fotografie nitide, luce naturale; scatto posteriore indispensabile per mostrare UNO Q. Video telefonici verticali, ripresa a mano e alcune riflessioni sul pannello; preservata la geometria, scelti segmenti brevi e leggibili. Lo schermo del laptop in esterno è meno leggibile: affiancato a ritagli della registrazione originale. Il master non ingrandisce artificialmente il testo del laptop come se fosse un’interfaccia nuova.

Il contatto della pallina è visibile attorno al fotogramma originale con PTS 7,579867 s (risoluzione temporale circa 0,0167 s); il rilascio è precedente. La griglia `impatti/contatto-preciso.jpg` e `contatto-pts.json` documentano la verifica sui fotogrammi originali. La selezione 6,3–9,8 s mostra preparazione, contatto e reazione; il replay 7,15–9,9 s a metà velocità non modifica la traiettoria. La seconda prova all’aperto contiene un contatto intorno a 1,9 s. Le griglie dense estratte consentono di verificare entrambe.

La dashboard documenta uno score reale 0,6035 e una soglia 0,3000. Mostra anche uno score sintetico circa 82,1386, mantenuto nella sua sezione e con etichetta esplicita. Si tratta di firma alterata artificialmente. Nessuno dei due valori è interpretato come diagnosi o probabilità di danno. Il LED acceso è osservabile nel video principale.

## Fonti tecniche nel progetto

`README.md`, `AI_INTEGRAZIONE.md`, `TEST_SINTETICO.md`, `DEMO_ECONOMICA.md` e il codice del progetto hanno guidato la distinzione piezo/IMU, analisi locale e limiti sperimentali. I filmati e i dati sono dell’utente; nessuna ripresa artificiale aggiunta.
