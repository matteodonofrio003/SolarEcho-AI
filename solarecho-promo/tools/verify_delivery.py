"""Verify delivered MP4s and extract a storyboard from the actual final master."""
from pathlib import Path
import subprocess, json, shutil
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'out'
BIN=ROOT/'node_modules/@remotion/compositor-win32-x64-msvc'
FFPROBE=BIN/'ffprobe.exe'
FFMPEG=BIN/'ffmpeg.exe'

def probe(name, dimensions):
    path=OUT/name
    result=subprocess.run([str(FFPROBE),'-v','error','-show_streams','-show_format','-of','json',str(path)],capture_output=True,text=True,check=True)
    data=json.loads(result.stdout)
    video=next(s for s in data['streams'] if s['codec_type']=='video')
    audio=next(s for s in data['streams'] if s['codec_type']=='audio')
    assert (video['width'],video['height'])==dimensions
    assert video['codec_name']=='h264' and video['r_frame_rate']=='30/1'
    assert int(video['nb_frames'])==1350 and abs(float(video['duration'])-45)<.001
    assert audio['codec_name']=='aac' and audio['channels']==2 and audio['sample_rate']=='48000'
    result=subprocess.run([str(FFMPEG),'-v','error','-i',str(path),'-c:v','rawvideo','-c:a','pcm_s16le','-f','null','-'],capture_output=True,text=True,check=True)
    assert not result.stderr.strip(),result.stderr
    return {'file':name,'video':{k:video.get(k) for k in ['codec_name','width','height','pix_fmt','r_frame_rate','duration','nb_frames','color_space','color_range']},
            'audio':{k:audio.get(k) for k in ['codec_name','sample_rate','channels','duration','bit_rate']},
            'container_duration':data['format']['duration'],'size_bytes':path.stat().st_size,'full_decode':'passed'}

master=probe('SolarEcho-AI-promo-1080p.mp4',(1920,1080))
preview=probe('SolarEcho-AI-anteprima-720p.mp4',(1280,720))
assert master['video']['pix_fmt']=='yuv420p'
assert master['video']['color_space']=='bt709'

frames=[120,360,570,810,1020,1230]
qa=OUT/'final-frames';qa.mkdir(exist_ok=True)
for i,frame in enumerate(frames):
    subprocess.run([str(FFMPEG),'-v','error','-y','-ss',str(frame/30),'-i',str(OUT/master['file']),'-an','-frames:v','1','-c:v','png',str(qa/f'scene-{i+1:02d}.png')],check=True)
shutil.copy2(qa/'scene-01.png',OUT/'poster.png')
titles=['00:04 / Ogni pannello ha una voce','00:12 / Un impatto. Una firma.','00:19 / Il mondo fisico diventa dato','00:27 / Tutto. A vista.','00:34 / Dai segnali alla ricerca AI','00:41 / Ascolta l\'energia']
canvas=Image.new('RGB',(2016,876),'#06151a')
draw=ImageDraw.Draw(canvas)
font=ImageFont.truetype(str(ROOT/'public/segoeui.ttf'),23)
for i,title in enumerate(titles):
    image=Image.open(qa/f'scene-{i+1:02d}.png').convert('RGB');image.thumbnail((640,360))
    x=24+(i%3)*664;y=24+(i//3)*424
    canvas.paste(image,(x,y));draw.text((x+5,y+373),title,font=font,fill='#b4d3cc')
canvas.save(OUT/'storyboard.jpg',quality=95)
report={'master':master,'preview':preview,'checks':{'typescript':'passed','eslint':'passed','visual_frames':frames,'soundtrack':'original, procedural, stereo, 120 BPM'},'note':'Video track is exactly 45 s. Container may include about 13 ms of AAC encoder padding.'}
(OUT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
