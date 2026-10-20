"""Prepare genuine footage and an original instrumental score for the new edit.

No voiceover, stock music, model inference, or generated experimental results.
The previously delivered edit and the source recordings are never overwritten.
"""
from pathlib import Path
import json
import subprocess
import wave

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
PUBLIC = ROOT / "presentation/public/social-v2"
FF = ROOT / "presentation/node_modules/@remotion/compositor-win32-x64-msvc/ffmpeg.exe"


def footage():
    PUBLIC.mkdir(parents=True, exist_ok=True)
    phone = PUBLIC / "telegram.mp4"
    if not phone.exists():
        subprocess.run([
            str(FF), "-v", "error", "-n", "-i",
            str(ROOT / "presentation/materials/originals/VID20261011151045.mp4"),
            "-vf", "scale=720:1280", "-r", "30", "-an", "-c:v", "libx264",
            "-preset", "fast", "-crf", "19", "-pix_fmt", "yuv420p",
            "-movflags", "+faststart", str(phone),
        ], check=True)
    # These are original screen captures, not recreated dashboard values.
    original = ROOT / "presentation/public/footage/dashboard.mp4"
    for name, stamp in (("acquisition", "22"), ("inference", "24"),
                        ("synthetic", "29"), ("alert", "44"), ("telegram", "76")):
        path = PUBLIC / f"screen-{name}.png"
        if not path.exists():
            subprocess.run([str(FF), "-v", "error", "-n", "-ss", stamp,
                            "-i", str(original), "-frames:v", "1", str(path)], check=True)
    phone_still = PUBLIC / "phone-original.png"
    if not phone_still.exists():
        subprocess.run([str(FF), "-v", "error", "-n", "-ss", "6", "-i", str(phone),
                        "-frames:v", "1", str(phone_still)], check=True)
    Image.open(phone_still).crop((340, 500, 700, 1220)).save(PUBLIC / "phone-detail.png")
    # Tight, readable crops of the authentic recording; values stay unchanged.
    crops = {
        "waveform": ("acquisition", (160, 340, 1680, 815)),
        "real-score": ("inference", (188, 790, 537, 910)),
        "synthetic-plot": ("synthetic", (160, 380, 1680, 893)),
        "alert": ("alert", (160, 385, 1680, 610)),
    }
    for name, (source, box) in crops.items():
        Image.open(PUBLIC / f"screen-{source}.png").crop(box).save(PUBLIC / f"crop-{name}.png")
    provenance = {
        "voiceover": False,
        "music": "Original procedural instrumental, 120 BPM; no third-party samples",
        "physical_demo": "VID20261011150931.mp4, source contact about 7.58 s",
        "phone": "VID20261011151045.mp4",
        "dashboard": original.name,
        "screenshots_at_seconds": {"acquisition": 22, "inference": 24,
                                    "synthetic": 29, "alert": 44, "telegram": 76},
        "crops_xyxy": {name: list(box) for name, (_, box) in crops.items()},
        "phone_detail": {"source": "telegram.mp4", "at_seconds": 6,
                         "crop_xyxy": [340, 500, 700, 1220]},
        "notes": [
            "Edited inserts do not establish synchronization between recordings.",
            "Real score 0.6035 exceeds configured threshold 0.3000; no proof of physical damage.",
            "Synthetic score 82.1386 is a software stress test, not physical validation.",
            "Telegram is a manual report, not an automatic dispatch.",
        ],
    }
    (PUBLIC / "provenance.json").write_text(json.dumps(provenance, indent=2, ensure_ascii=False), encoding="utf-8")


def music(duration=90, filename="score.wav", hardware_end=28):
    """Warm plucks, bass, acoustic-style drum synthesis: all sounds synthesized here."""
    PUBLIC.mkdir(parents=True, exist_ok=True)
    sr = 48000
    out = np.zeros((sr * duration, 2), dtype=np.float32)
    rng = np.random.default_rng(20261017)

    def hz(note):
        return 440 * 2 ** ((note - 69) / 12)

    def add(signal, at, gain=1.0, pan=0.0):
        start = round(at * sr)
        if not 0 <= start < len(out):
            return
        signal = signal[:len(out)-start] * gain
        out[start:start+len(signal), 0] += signal * np.sqrt((1-pan)/2)
        out[start:start+len(signal), 1] += signal * np.sqrt((1+pan)/2)

    chords = [(50, 57, 60, 64), (46, 53, 57, 60), (53, 57, 60, 67), (48, 55, 60, 64)]
    for i, at in enumerate(np.arange(0, duration - 2, 4.0)):
        t = np.arange(round(4.8 * sr)) / sr
        envelope = np.minimum(t/.18, 1) * np.minimum(np.maximum((4.8-t)/1.2, 0), 1)
        for j, note in enumerate(chords[i % 4]):
            signal = (np.sin(2*np.pi*hz(note)*t) + .22*np.sin(2*np.pi*hz(note)*1.004*t))
            add(signal*envelope, at, .052, (j-1.5)*.35)

    motif = (0, 2, 1, 3, 2, 0, 3, 1)
    for i, at in enumerate(np.arange(.5, duration - 3, .25)):
        chord = chords[int(at // 4) % 4]
        note = chord[motif[i % len(motif)]] + 12
        t = np.arange(round(.85*sr)) / sr
        signal = (np.sin(2*np.pi*hz(note)*t) + .25*np.sin(2*np.pi*hz(note)*2*t))
        signal *= (1-np.exp(-t*190))*np.exp(-t*7)
        gain = .105 if 6 <= at < duration - 12 else .065
        add(signal, at, gain, .45*np.sin(i*.7))
        add(signal, at+.375, gain*.21, -.45*np.sin(i*.7))

    for i, at in enumerate(np.arange(0, duration - 2.5, .5)):
        section = .65 if 16 <= at < hardware_end or at >= duration - 12 else 1.0
        t = np.arange(round(.38*sr)) / sr
        phase = 2*np.pi*(47*t + 90*.024*(1-np.exp(-t/.024)))
        kick = np.sin(phase)*np.exp(-t*19)*(1-np.exp(-t*900))
        add(kick, at, .48*section)
        chord = chords[int(at // 4) % 4]
        bass_note = chord[0]-12 + (12 if i % 8 == 7 else 0)
        bass = (np.sin(2*np.pi*hz(bass_note)*t) + .13*np.sin(2*np.pi*hz(bass_note)*2*t))
        bass *= (1-np.exp(-t*140))*np.exp(-t*8)
        add(bass, at+.015, .20*section)
        if i % 2:
            t = np.arange(round(.19*sr))/sr
            noise = rng.normal(size=len(t))
            noise = noise - .82*np.roll(noise, 1)
            clap = noise*np.exp(-t*30) * (1-np.exp(-t*700))
            add(clap, at, .052*section, -.08)
            add(np.sin(2*np.pi*185*t)*np.exp(-t*27), at, .075*section)
        for subdivision in (0, .25):
            t = np.arange(round(.075*sr))/sr
            noise = rng.normal(size=len(t))
            noise -= np.roll(noise, 1)
            add(noise*np.exp(-t*85), at+subdivision,
                .012 if subdivision == 0 else .020, .28 if i % 2 else -.28)

    for at in (6, 16, hardware_end, hardware_end + 14, hardware_end + 25, hardware_end + 37, hardware_end + 50):
        t = np.arange(round(.55*sr))/sr
        noise = rng.normal(size=len(t))
        air = np.convolve(noise, np.ones(9)/9, mode="same")
        add(air*np.sin(np.pi*t/.55)**2, at-.3, .075, .15)
        add(np.sin(2*np.pi*hz(86)*t)*np.exp(-t*14), at, .06, -.2)

    for note, at in ((74, duration - 4), (77, duration - 3.5), (81, duration - 3)):
        t = np.arange(3*sr)/sr
        add(np.sin(2*np.pi*hz(note)*t)*np.exp(-t*1.6)*(1-np.exp(-t*150)), at, .14)
    t = np.arange(len(out))/sr
    out = np.tanh(out*1.08)
    out *= np.minimum(t/.06, 1)[:, None] * np.minimum(np.maximum((duration-t)/2.0, 0), 1)[:, None]
    out *= .78 / max(float(np.max(np.abs(out))), 1e-8)
    destination = PUBLIC / filename
    destination.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(destination), "wb") as stream:
        stream.setnchannels(2)
        stream.setsampwidth(2)
        stream.setframerate(sr)
        stream.writeframes((out*32767).astype("<i2").tobytes())
    print(f"Musica originale: {duration} secondi, 120 BPM, stereo 48 kHz. Nessuna voce. {destination}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--music-only", action="store_true")
    parser.add_argument("--duration", type=int, default=90)
    parser.add_argument("--hardware-end", type=int, default=28)
    parser.add_argument("--music-file", default="score.wav")
    args = parser.parse_args()
    if not 60 <= args.duration <= 120 or not 16 < args.hardware_end < args.duration - 12:
        parser.error("Duration must be 60..120s; hardware end must precede closing.")
    if not args.music_only:
        footage()
    music(args.duration, args.music_file, args.hardware_end)
