from pathlib import Path
import subprocess,json
from PIL import Image,ImageDraw,ImageFont,ImageOps
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'video_output'
FF=ROOT/'solarecho-promo/node_modules/@remotion/compositor-win32-x64-msvc/ffmpeg.exe'
FP=FF.with_name('ffprobe.exe')
MEDIA=ROOT/'materiale_per_video'
AN=OUT/'analisi';AN.mkdir(parents=True,exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',20)
report=[];photos=[]
for num,path in enumerate(sorted(MEDIA.rglob('*'))):
 if not path.is_file():continue
 if path.suffix.lower() in ['.jpg','.jpeg','.png','.webp']:
  im=ImageOps.exif_transpose(Image.open(path));photos.append((path,im.copy()))
  report.append({'file':str(path.relative_to(ROOT)),'type':'photo','width':im.width,'height':im.height,'bytes':path.stat().st_size})
  continue
 p=subprocess.run([str(FP),'-v','error','-show_streams','-show_format','-of','json',str(path)],capture_output=True,text=True)
 if p.returncode:continue
 data=json.loads(p.stdout);(AN/f'probe-{num}.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
 videos=[s for s in data.get('streams',[]) if s['codec_type']=='video']
 if not videos:continue
 v=videos[0];duration=float(data.get('format',{}).get('duration',0));times=list(range(0,int(duration),4)) if duration>12 else [round(t,2) for t in np.linspace(.1,max(.2,duration-.2),8)]
 frames=AN/f'filmato-{num}';frames.mkdir(exist_ok=True)
 sheet=Image.new('RGB',(2000,((len(times)+3)//4)*290),'#081820');d=ImageDraw.Draw(sheet)
 for i,t in enumerate(times):
  dest=frames/f'{t:06.2f}s.jpg'
  subprocess.run([str(FF),'-v','error','-y','-ss',str(t),'-i',str(path),'-frames:v','1','-vf','scale=480:-2',str(dest)],check=True)
  im=Image.open(dest);im.thumbnail((480,236));x=(i%4)*500+10;y=(i//4)*290+10
  sheet.paste(im,(x,y));d.text((x,y+247),f'{t:05.1f} s',font=font,fill='white')
 sheet.save(AN/f'contact-sheet-{num}.jpg',quality=95)
 report.append({'file':str(path.relative_to(ROOT)),'type':'video','duration_s':duration,'width':v['width'],'height':v['height'],'fps':v['avg_frame_rate'],'codec':v['codec_name'],'audio':[s['codec_name'] for s in data['streams'] if s['codec_type']=='audio'],'bytes':path.stat().st_size,'sampled_frames_s':times,'contact_sheet':f'contact-sheet-{num}.jpg'})
if photos:
 sheet=Image.new('RGB',(2000,((len(photos)+2)//3)*550),'#081820');d=ImageDraw.Draw(sheet)
 for i,(path,im) in enumerate(photos):
  im.thumbnail((640,475));x=(i%3)*665+15;y=(i//3)*550+15;sheet.paste(im,(x,y));d.text((x,y+485),path.name,font=font,fill='white')
 sheet.save(AN/'photos.jpg',quality=95)
(AN/'inventario.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
