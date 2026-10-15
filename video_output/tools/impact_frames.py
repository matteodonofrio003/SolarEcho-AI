from pathlib import Path
import subprocess
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[2]
FF=ROOT/'solarecho-promo/node_modules/@remotion/compositor-win32-x64-msvc/ffmpeg.exe'
OUT=ROOT/'video_output/analisi/impatti';OUT.mkdir(exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',23)
for name,start,end,step in [('VID20261011150931.mp4',5,11,.25),('VID20261011145827.mp4',0,2,.125)]:
 times=[start+i*step for i in range(round((end-start)/step))]
 sheet=Image.new('RGB',(1800,((len(times)+5)//6)*520),'#07111f');d=ImageDraw.Draw(sheet)
 for i,t in enumerate(times):
  p=OUT/f'{name}-{t:.3f}.jpg'
  subprocess.run([str(FF),'-v','error','-y','-ss',str(t),'-i',str(ROOT/'materiale_per_video'/name),'-frames:v','1','-vf','scale=270:-2',str(p)],check=True)
  im=Image.open(p);sheet.paste(im,((i%6)*300+15,(i//6)*520));d.text(((i%6)*300+15,(i//6)*520+480),f'{t:.3f}s',font=font,fill='white')
 sheet.save(OUT/f'{name}.jpg',quality=93)
print('Dense impact sheets complete')
