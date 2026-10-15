"""Build original score and visual assets from the SolarEcho repository."""
from pathlib import Path
import csv, json, shutil, struct, wave
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
PUBLIC = ROOT / 'public'
PUBLIC.mkdir(exist_ok=True)

def signals():
    f = REPO / 'datasets/raw/normal_test/20261010_171420_45cdb44c_event_0001.csv'
    rows = list(csv.DictReader(f.open()))
    pre = [r for r in rows if float(r['timestamp_us']) < 0]
    axes = []
    for field in ['ax_g', 'ay_g', 'az_g']:
        baseline = np.median([float(r[field]) for r in pre])
        axes.append([round(float(r[field])-baseline, 6) for r in rows])
    data = {'source': str(f.relative_to(REPO)).replace('\\', '/'),
            'timeMs': [round(float(r['timestamp_us']) / 1000, 3) for r in rows],
            'axes': axes, 'samples': len(rows)}
    (ROOT / 'src/data').mkdir(exist_ok=True)
    (ROOT / 'src/data/signal.json').write_text(json.dumps(data), encoding='utf-8')
    im = Image.open(REPO / 'risultato_training1.png')
    im.crop((12, 235, 728, 746)).save(PUBLIC / 'training-plot.png')
    shutil.copy2('C:/Windows/Fonts/bahnschrift.ttf', PUBLIC / 'bahnschrift.ttf')
    for name in ['segoeui.ttf', 'segoeuib.ttf']:
        shutil.copy2(Path('C:/Windows/Fonts') / name, PUBLIC / name)
    print(f'Signal: {len(rows)} real samples, dynamic peak {max(abs(v) for a in axes for v in a):.4f} g')

def housing():
    raw = (REPO / 'Solar_Housing.stl').read_bytes()
    count = struct.unpack_from('<I', raw, 80)[0]
    records = np.frombuffer(raw, dtype=np.dtype([('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')]), count=count, offset=84)
    verts = records['v'].astype(float)
    lo, hi = verts.min(axis=(0,1)), verts.max(axis=(0,1))
    verts -= (lo+hi)/2
    norm = np.cross(verts[:,1]-verts[:,0], verts[:,2]-verts[:,0])
    norm /= np.maximum(np.linalg.norm(norm,axis=1)[:,None], 1e-9)
    light = np.array([-.4, -.5, .9]); light /= np.linalg.norm(light)
    diffuse = np.abs(norm@light)
    colors = np.array([.71,.88,.85])[None,:]*(.48+.52*diffuse[:,None])
    fig = plt.figure(figsize=(12,10), dpi=150)
    ax = fig.add_subplot(111, projection='3d', computed_zorder=False)
    coll = Poly3DCollection(verts, facecolors=colors, edgecolors='none', linewidths=0, zorder=1)
    ax.add_collection3d(coll)
    span = hi-lo
    ax.set_xlim(-span[0]*.55, span[0]*.55); ax.set_ylim(-span[1]*.55, span[1]*.55); ax.set_zlim(-span[2]*.55, span[2]*.55)
    ax.set_box_aspect(span); ax.view_init(elev=28,azim=-54); ax.set_proj_type('ortho'); ax.set_axis_off()
    fig.patch.set_alpha(0); ax.patch.set_alpha(0)
    fig.subplots_adjust(left=0,right=1,top=1,bottom=0)
    dest = PUBLIC/'housing.png'
    fig.savefig(dest, transparent=True, pad_inches=0)
    plt.close(fig)
    im = Image.open(dest); box=im.getbbox(); im.crop(box).save(dest)
    print(f'Housing: {count} triangles, original dimensions {span.tolist()}')

def music():
    sr=48000; duration=45; n=sr*duration
    out=np.zeros((n,2),dtype=np.float64); rng=np.random.default_rng(23)
    def hz(m): return 440*2**((m-69)/12)
    def add(sound,start,gain=1,pan=0):
        off=round(start*sr)
        if off>=n: return
        sound=sound[:min(len(sound), n-off)]*gain
        out[off:off+len(sound),0]+=sound*np.sqrt((1-pan)/2)
        out[off:off+len(sound),1]+=sound*np.sqrt((1+pan)/2)
    chords=[[52,55,59,66],[48,52,55,62],[43,50,55,59],[50,54,57,64]]
    # Wide, slowly blooming harmonic bed. No third-party music samples.
    for k,start in enumerate(np.arange(0,44,4)):
        t=np.arange(int(sr*5.6))/sr
        env=np.minimum(t/1.2,1)*np.minimum(np.maximum((5.6-t)/1.6,0),1)
        for j,m in enumerate(chords[k%4]):
            s=np.sin(2*np.pi*hz(m)*t)+.32*np.sin(2*np.pi*hz(m)*1.003*t)+.13*np.sin(2*np.pi*hz(m)*2*t)
            s*=env*(.92+.08*np.sin(2*np.pi*.18*t+j))
            add(s,start,.040,(-1 if j%2 else 1)*.55)
    arp=[0,2,1,3,2,1,3,2]
    for k,start in enumerate(np.arange(2,41,.25)):
        chord=chords[int(start//4)%4]; m=chord[arp[k%8]]+12
        t=np.arange(int(sr*1.4))/sr
        env=(1-np.exp(-t*140))*np.exp(-t*5)
        s=(np.sin(2*np.pi*hz(m)*t)+.3*np.sin(2*np.pi*hz(m)*2*t)+.08*np.sin(2*np.pi*hz(m)*3*t))*env
        gain=.075 if start>=7 else .038
        add(s,start,gain,.35*np.sin(k*1.2)); add(s,start+.375,gain*.26,-.35*np.sin(k*1.2)); add(s,start+.75,gain*.12)
    for k,start in enumerate(np.arange(7,39,.5)):
        root=chords[int(start//4)%4][0]-12
        t=np.arange(int(sr*.48))/sr
        s=(np.sin(2*np.pi*hz(root)*t)+.2*np.sin(2*np.pi*hz(root)*2*t))*(1-np.exp(-t*100))*np.exp(-t*5)
        add(s,start,.20)
        t=np.arange(int(sr*.4))/sr
        phase=2*np.pi*(46*t+(125-46)*.025*(1-np.exp(-t/.025)))
        kick=np.sin(phase)*np.exp(-t*15)
        add(kick,start,.32)
        if k%2:
            t=np.arange(int(sr*.19))/sr; noise=rng.normal(size=len(t)); noise-=np.roll(noise,1)*.65
            add(noise*np.exp(-t*30),start,.044)
    for k,start in enumerate(np.arange(7,39,.25)):
        t=np.arange(int(sr*.08))/sr; noise=rng.normal(size=len(t)); noise-=np.roll(noise,1)*.9
        add(noise*np.exp(-t*80),start,.022 if k%2 else .014, .5 if k%2 else -.5)
    # Transition swells and a three-note signature on the closing reveal.
    for cut in [7,15,22,30,37]:
        t=np.arange(int(sr*1.25))/sr
        noise=rng.normal(size=len(t)); soft=np.convolve(noise,np.ones(11)/11,mode='same')
        env=np.sin(np.pi*np.clip(t/1.25,0,1))**2
        add(soft*env,cut-.7,.085,-.25)
        t=np.arange(int(sr*2.2))/sr
        add(np.sin(2*np.pi*hz(76)*t)*np.exp(-t*3),cut,.035,.4)
    for start,m in [(38,76),(38.5,79),(39,83)]:
        t=np.arange(sr*4)/sr
        add((np.sin(2*np.pi*hz(m)*t)+.2*np.sin(2*np.pi*hz(m)*2*t))*np.exp(-t*1.5)*(1-np.exp(-t*120)),start,.16)
    out=np.tanh(out*1.15)
    t=np.arange(n)/sr; fade=np.minimum(t/1.6,1)*np.minimum(np.maximum((45-t)/2,0),1)
    out*=fade[:,None]
    out*=.89/max(abs(out.min()),out.max())
    with wave.open(str(PUBLIC/'solarecho-original-score.wav'),'wb') as f:
        f.setnchannels(2); f.setsampwidth(2); f.setframerate(sr)
        f.writeframes((out*32767).astype('<i2').tobytes())
    print(f'Original score: {duration}s, 120 BPM, stereo {sr}Hz, peak {np.max(np.abs(out)):.3f}')

if __name__=='__main__':
    signals(); housing(); music()
