from pathlib import Path
import subprocess,json
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'video_output/analisi/impatti'
FF=ROOT/'solarecho-promo/node_modules/@remotion/compositor-win32-x64-msvc/ffmpeg.exe';FP=FF.with_name('ffprobe.exe')
src=ROOT/'materiale_per_video/VID20261011150931.mp4'
data=json.loads(subprocess.check_output([str(FP),'-v','error','-select_streams','v:0','-read_intervals','7%8','-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','json',str(src)]))
times=[float(f['best_effort_timestamp_time']) for f in data['frames'] if 7.55<=float(f['best_effort_timestamp_time'])<=7.9]
sheet=Image.new('RGB',(2000,((len(times)+4)//5)*430),'#06111f');d=ImageDraw.Draw(sheet);font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',24)
for i,t in enumerate(times):
 p=OUT/f'precise-{t:.6f}.png'
 # A tiny negative epsilon selects the intended decoded frame at its real PTS.
 subprocess.run([str(FF),'-v','error','-y','-ss',str(t-.00001),'-i',str(src),'-frames:v','1','-vf','scale=540:-2',str(p)],check=True)
 im=Image.open(p).crop((0,410,540,935)).resize((390,380));x=(i%5)*400;y=(i//5)*430;sheet.paste(im,(x,y));d.text((x+7,y+387),f'{t:.6f} s',font=font,fill='white')
sheet.save(OUT/'contatto-preciso.jpg',quality=97)
(OUT/'contatto-pts.json').write_text(json.dumps(times,indent=2),encoding='utf-8')
print('Original frame PTS:',times)
