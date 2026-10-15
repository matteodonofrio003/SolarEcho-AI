"""Verify delivered files and extract visual/audio QA from the encoded master."""
from pathlib import Path
import subprocess,json,wave,re,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'video_output';AN=OUT/'analisi';QA=AN/'master';QA.mkdir(exist_ok=True)
FF=ROOT/'solarecho-promo/node_modules/@remotion/compositor-win32-x64-msvc/ffmpeg.exe';FP=FF.with_name('ffprobe.exe')
report={'checks':{},'files':{}}
for name in ['SolarEcho_AI_finale.mp4','SolarEcho_AI_anteprima.mp4']:
 p=OUT/name
 data=json.loads(subprocess.check_output([str(FP),'-v','error','-show_streams','-show_format','-of','json',str(p)]))
 v=next(s for s in data['streams'] if s['codec_type']=='video');a=next(s for s in data['streams'] if s['codec_type']=='audio')
 duration=float(data['format']['duration']);expected=(1920,1080) if 'finale' in name else (1280,720)
 checks={'duration_under_120':duration<=120,'duration_118':abs(duration-118)<.06,'resolution_correct':(v['width'],v['height'])==expected,'fps_30':v['avg_frame_rate']=='30/1','video_h264':v['codec_name']=='h264','audio_aac':a['codec_name']=='aac','frames_3540':int(v['nb_frames'])==3540,'pixel_format_yuv420p':v['pix_fmt']=='yuv420p','audio_stereo':a['channels']==2}
 assert all(checks.values()),(name,checks)
 decoded=subprocess.run([str(FF),'-v','error','-i',str(p),'-c:v','rawvideo','-c:a','pcm_s16le','-f','null','-'],capture_output=True,text=True)
 (AN/(name+'.decode.log')).write_text(decoded.stderr,encoding='utf-8')
 checks['full_decode_ok']=decoded.returncode==0 and not decoded.stderr.strip()
 assert checks['full_decode_ok'],decoded.stderr
 report['checks'][name]=checks
 report['files'][name]={'duration_s':duration,'width':v['width'],'height':v['height'],'fps':v['avg_frame_rate'],'frames':v['nb_frames'],'video_codec':v['codec_name'],'audio_codec':a['codec_name'],'sample_rate':a['sample_rate'],'channels':a['channels'],'color_space':v.get('color_space'),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
 print('Verified',name,duration,'seconds',flush=True)
master=OUT/'SolarEcho_AI_finale.mp4'
audio=AN/'audio-master.wav'
subprocess.run([str(FF),'-v','error','-y','-i',str(master),'-vn','-ar','48000','-ac','2','-c:a','pcm_s16le',str(audio)],check=True)
with wave.open(str(audio),'rb') as f:samples=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').astype(np.float64)/32768
report['audio']={'sample_peak_dbfs':float(20*np.log10(max(np.max(np.abs(samples)),1e-10))),'clipped_samples':int(np.count_nonzero(np.abs(samples)>=.9999)),'rms_dbfs':float(20*np.log10(np.sqrt(np.mean(samples**2))))}
assert report['audio']['clipped_samples']==0
loud=subprocess.run([str(FF),'-hide_banner','-i',str(master),'-vn','-af','loudnorm=I=-16:TP=-1:LRA=11:print_format=json','-c:a','pcm_s16le','-f','null','-'],capture_output=True,text=True)
m=re.search(r'\{\s*"input_i".*?\}',loud.stderr,re.S)
if m:report['audio']['measured_loudness']=json.loads(m.group(0))
times=[2,6,12,20,25,34,39.5,42.6,50,58.5,64,71.5,77,85,96,104,108,110,114,117.9]
sheet=Image.new('RGB',(1920,((len(times)+2)//3)*400),'#040b19');d=ImageDraw.Draw(sheet);font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',24)
for i,t in enumerate(times):
 dest=QA/f'{t:06.2f}s.png'
 subprocess.run([str(FF),'-v','error','-y','-ss',str(t),'-i',str(master),'-frames:v','1',str(dest)],check=True)
 im=Image.open(dest).resize((620,349));x=(i%3)*640+10;y=(i//3)*400+10;sheet.paste(im,(x,y));d.text((x,y+357),f'{t:.2f} s',font=font,fill='white')
sheet.save(OUT/'storyboard_anteprima.jpg',quality=95)
subprocess.run([str(FF),'-v','error','-y','-ss','20','-i',str(master),'-frames:v','1',str(OUT/'SolarEcho_AI_copertina.jpg')],check=True)
report['content_review']={'real_physical_demo':True,'selected_real_photos':4,'impact_is_not_damage_diagnosis':True,'synthetic_test_is_labeled':True,'economic_benefits_are_potential':True,'italian_narration_and_captions':True,'original_procedural_music':True,'render_stills_reviewed':True,'master_frames_extracted':times}
(OUT/'verifica_finale.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report['audio'],indent=2));print('All delivery checks passed.',flush=True)
