"""Reproducible preparation: real assets, Italian voice, timed captions, original music."""
from pathlib import Path
import asyncio,sys,json,re,shutil,subprocess,wave,concurrent.futures
import numpy as np
from PIL import Image,ImageOps
ROOT=Path(__file__).resolve().parents[2]
PUB=ROOT/'solarecho-promo/public/hackathon';PUB.mkdir(parents=True,exist_ok=True)
SRC=ROOT/'solarecho-promo/src/hackathon';SRC.mkdir(parents=True,exist_ok=True)
FF=ROOT/'solarecho-promo/node_modules/@remotion/compositor-win32-x64-msvc/ffmpeg.exe'
FP=FF.with_name('ffprobe.exe')
BLOCKS=[
 ('problema',.8,16.6,'Un impatto può durare un istante. Le sue conseguenze possono durare anni. Grandine, vento e urti mettono alla prova i pannelli. Un’alterazione non sempre si vede subito. Capire quando controllare protegge produzione e risorse.'),
 ('soluzione',18.8,18.7,'Solar Echo AI ascolta la firma vibrazionale del pannello. Il piezo rileva l’impatto. Il sensore di movimento misura le vibrazioni sui tre assi. Arduino UNO Q raccoglie i dati e li analizza sul dispositivo. È Edge AI: intelligenza artificiale locale.'),
 ('impatto',38.8,7.8,'La pallina colpisce il pannello. Il sistema rileva l’urto: da solo, non dimostra un danno.'),
 ('acquisizione',47.5,8.8,'I sensori misurano la risposta. La dashboard mostra le vibrazioni sui tre assi: una traccia registrata, insieme ai dati dell’evento.'),
 ('analisi',57.5,10.8,'Il modello confronta il segnale con il riferimento. Lo score misura lo scostamento dalla firma normale: non è una percentuale di danno.'),
 ('risultato',69.4,10,'Oltre soglia, l’ispezione è consigliata. Dashboard e LED mostrano la segnalazione. Il test sintetico non dimostra danni fisici.'),
 ('economia',80.8,20.2,'Per chi gestisce un impianto, la domanda è: dove intervenire prima? Ai controlli programmati, Solar Echo AI affianca segnali per dare priorità alle ispezioni. L’obiettivo: meno controlli inutili, interventi più mirati e costi potenzialmente ridotti. Benefici da validare sul campo.'),
 ('innovazione',102.5,8.7,'Firma vibrazionale e AI locale. Manutenzione intelligente. Prossimo passo: validazione su alterazioni fisiche.'),
 ('finale',112.6,4.9,'Solar Echo AI. Il pannello che riconosce i propri danni.'),
]

def probe(p):
 return json.loads(subprocess.check_output([str(FP),'-v','error','-show_format','-of','json',str(p)]))

def assets():
 clips={'beauty':'VID20261011143706.mp4','orbit':'VID20261011143749.mp4','outdoor':'VID20261011145659.mp4','impact-outdoor':'VID20261011145827.mp4','demo':'VID20261011150931.mp4'}
 def convert(item):
  dest,name=item;p=PUB/f'{dest}.mp4'
  if p.exists() and p.stat().st_size>1000:return
  subprocess.run([str(FF),'-v','error','-y','-i',str(ROOT/'materiale_per_video'/name),'-vf','scale=720:1280:flags=lanczos','-r','60','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart',str(p)],check=True)
  print('Transcoded',name,flush=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(convert,clips.items()))
 for dest,name in {'panel':'IMG20261011143543.jpg','sensor':'IMG20261011143550.jpg','electronics':'IMG20261011143612.jpg','sunlight':'IMG20261011143930.jpg'}.items():
  im=ImageOps.exif_transpose(Image.open(ROOT/'materiale_per_video'/name));im.thumbnail((2200,2200));im.save(PUB/f'{dest}.jpg',quality=95)
 shutil.copy2(ROOT/'materiale_per_video/Registrazione 2026-10-11 151111.mp4',PUB/'dashboard.mp4')
 for dest,t in {'dash-acquisition':22,'dash-ai':24,'dash-alert':44,'dash-synthetic':29}.items():
  subprocess.run([str(FF),'-v','error','-y','-ss',str(t),'-i',str(PUB/'dashboard.mp4'),'-frames:v','1',str(PUB/f'{dest}.png')],check=True)
 md=(ROOT/'video_output/analisi/basic-captions-reference.md').read_text(encoding='utf-8')
 code=re.search(r'```tsx[^\n]*\n(.*?)\n```',md,re.S).group(1)
 (SRC/'basic-captions.tsx').write_text(code+'\n',encoding='utf-8')
 (PUB/'asset-origins.json').write_text(json.dumps({'clips':clips,'dashboard':'Registrazione 2026-10-11 151111.mp4','photos':{'panel':'IMG20261011143543.jpg','sensor':'IMG20261011143550.jpg','electronics':'IMG20261011143612.jpg','sunlight':'IMG20261011143930.jpg'},'processing':'EXIF rotation preserved; portrait proportions retained; mild contrast/saturation correction; no result changes'},indent=2),encoding='utf-8')

async def voice():
 import edge_tts
 records=[];srt=[];count=1
 for name,start,slot,text in BLOCKS:
  mp3=PUB/f'voice-{name}.mp3';bounds=PUB/f'voice-{name}-words.json'
  textfile=PUB/f'voice-{name}.txt'
  if not mp3.exists() or not bounds.exists() or not textfile.exists() or textfile.read_text(encoding='utf-8')!=text:
   for attempt in range(8):
    words=[]
    try:
     com=edge_tts.Communicate(text,voice='it-IT-DiegoNeural',rate='+4%',boundary='WordBoundary')
     with mp3.open('wb') as f:
      async for msg in com.stream():
       if msg['type']=='audio':f.write(msg['data'])
       elif msg['type']=='WordBoundary':words.append({'text':msg['text'],'offset':msg['offset']/10000,'duration':msg['duration']/10000})
     if words:break
    except Exception as e:
     print('TTS retry',name,attempt+1,type(e).__name__,flush=True)
     await asyncio.sleep(5)
   if not words:raise RuntimeError('No TTS words for '+name)
   bounds.write_text(json.dumps(words,ensure_ascii=False),encoding='utf-8');textfile.write_text(text,encoding='utf-8')
  words=json.loads(bounds.read_text(encoding='utf-8'));dur=float(probe(mp3)['format']['duration'])
  factor=max(1,dur/slot)
  # Small tempo adjustment, without pitch change, when needed to fit the fixed edit.
  subprocess.run([str(FF),'-v','error','-y','-i',str(mp3),'-af',f'atempo={factor:.8f},loudnorm=I=-17:TP=-2:LRA=8','-ar','48000','-ac','1',str(PUB/f'voice-{name}.wav')],check=True)
  caps=[];pointer=0
  for i,w in enumerate(words):
   match=re.search(re.escape(w['text'])+r'([.,:;!?]*)',text[pointer:],re.I)
   shown=w['text']
   if match:shown=match.group(0);pointer+=match.end()
   cap={'text':(' ' if i else '')+shown,'startMs':round(w['offset']/factor,2),'endMs':round((w['offset']+w['duration'])/factor,2),'timestampMs':None,'confidence':None}
   if shown.endswith(('.', '!', '?')):cap['pageBreakAfter']=True
   caps.append(cap)
  records.append({'name':name,'start':start,'slot':slot,'text':text,'duration':dur/factor,'tempoFactor':factor,'captions':caps})
  print('Voice',name,round(dur/factor,2),'seconds; tempo',round(factor,3),flush=True)
 (ROOT/'video_output/narrazione.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
 # Each authored narration block has its own editable node; captions stay inline.
 js="import {AbsoluteFill, Sequence, staticFile} from 'remotion';\nimport {Audio} from '@remotion/media';\nimport {BasicCaptions} from './basic-captions';\nexport const Narration = () => <AbsoluteFill>\n"
 for r in records:
  js+=f'''<Sequence name="Voce / {r["name"]}" from={{{round(r["start"]*30)}}} durationInFrames={{{round(r["slot"]*30)}}} premountFor={{30}}>\n<Audio src={{staticFile("hackathon/voice-{r["name"]}.wav")}} volume={{.94}}/>\n<BasicCaptions width={{1900}} combineTokensWithinMilliseconds={{2200}} style={{{{position:"absolute",left:200,bottom:65,transform:"scale(.8)",transformOrigin:"bottom left"}}}} captions={{{json.dumps(r['captions'],ensure_ascii=False)}}}/>\n</Sequence>\n'''
 js+='</AbsoluteFill>;\n';(SRC/'Narration.tsx').write_text(js,encoding='utf-8')
 def stamp(ms):
  s,milli=divmod(round(ms),1000);mins,s=divmod(s,60);h,mins=divmod(mins,60);return f'{h:02}:{mins:02}:{s:02},{milli:03}'
 for r in records:
  caps=r['captions']
  for i in range(0,len(caps),7):
   group=caps[i:i+7];srt.append(f'{count}\n{stamp(r["start"]*1000+group[0]["startMs"])} --> {stamp(r["start"]*1000+group[-1]["endMs"])}\n'+''.join(c['text'] for c in group).strip()+'\n');count+=1
 (ROOT/'video_output/sottotitoli_it.srt').write_text('\n'.join(srt),encoding='utf-8')

def music():
 sr=48000;dur=118;n=sr*dur;out=np.zeros((n,2),dtype=np.float32);rng=np.random.default_rng(1136239)
 def hz(m):return 440*2**((m-69)/12)
 def add(s,t,gain=1,pan=0):
  off=round(t*sr)
  if off<0 or off>=n:return
  s=s[:n-off]*gain;out[off:off+len(s),0]+=s*np.sqrt((1-pan)/2);out[off:off+len(s),1]+=s*np.sqrt((1+pan)/2)
 chords=[[52,55,59,66],[48,52,55,62],[43,50,55,59],[50,54,57,64]]
 for k,start in enumerate(np.arange(0,116,4)):
  t=np.arange(round(sr*5.7))/sr;env=np.minimum(t/1.1,1)*np.minimum(np.maximum((5.7-t)/1.6,0),1)
  for j,m in enumerate(chords[k%4]):
   s=(np.sin(2*np.pi*hz(m)*t)+.3*np.sin(2*np.pi*hz(m)*1.003*t)+.1*np.sin(2*np.pi*hz(m)*2*t))*env
   add(s,start,.041,(-1 if j%2 else 1)*.6)
 arp=[0,2,1,3,2,1,3,2]
 for k,start in enumerate(np.arange(3,113,.25)):
  m=chords[int(start//4)%4][arp[k%8]]+12;t=np.arange(round(sr*1.3))/sr
  env=(1-np.exp(-t*100))*np.exp(-t*4.8)
  s=(np.sin(2*np.pi*hz(m)*t)+.25*np.sin(2*np.pi*hz(m)*2*t))*env
  g=.04 if start<18 or 80<=start<102 else .075
  add(s,start,g,.4*np.sin(k));add(s,start+.375,g*.23,-.4*np.sin(k))
 for k,start in enumerate(np.arange(18,112,.5)):
  if 80<=start<91:continue
  t=np.arange(round(sr*.45))/sr;root=chords[int(start//4)%4][0]-12
  add(np.sin(2*np.pi*hz(root)*t)*(1-np.exp(-t*120))*np.exp(-t*5),start,.17)
  phase=2*np.pi*(46*t+79*.025*(1-np.exp(-t/.025)))
  add(np.sin(phase)*np.exp(-t*15),start,.29)
  if k%2:
   t=np.arange(round(sr*.14))/sr;noise=rng.normal(size=len(t));noise-=.7*np.roll(noise,1);add(noise*np.exp(-t*36),start,.025)
 for cut in [18,38,47,57,69,80,102,112]:
  t=np.arange(round(sr*1.1))/sr;noise=rng.normal(size=len(t));soft=np.convolve(noise,np.ones(13)/13,mode='same');add(soft*np.sin(np.pi*t/1.1)**2,cut-.55,.085)
 for start,m in [(112,76),(112.5,79),(113,83)]:
  t=np.arange(sr*4)/sr;add(np.sin(2*np.pi*hz(m)*t)*np.exp(-t*1.1)*(1-np.exp(-t*120)),start,.15)
 t=np.arange(n)/sr;out=np.tanh(out);out*=np.minimum(t/1.3,1)[:,None]*np.minimum(np.maximum((118-t)/2.4,0),1)[:,None]
 out*=.85/np.max(np.abs(out))
 with wave.open(str(PUB/'original-score.wav'),'wb') as f:f.setnchannels(2);f.setsampwidth(2);f.setframerate(sr);f.writeframes((out*32767).astype('<i2').tobytes())
 print('Original procedural score: 118s stereo48k',flush=True)

if __name__=='__main__':
 mode=sys.argv[1] if len(sys.argv)>1 else 'all'
 if mode in ['all','assets']:assets()
 if mode in ['all','voice']:asyncio.run(voice())
 if mode in ['all','music']:music()
