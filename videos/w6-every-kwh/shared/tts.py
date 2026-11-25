# Generate voice-over clips with Kokoro (offline). Usage: python3 tts.py <lines.json> <outdir> <model_dir> [voice] [speed]
# lines.json: [{"id":..,"t":start_seconds,"end":caption_end,"lang":"en-us"|"ms","text":..} ...]
# Text may contain {ms:...} spans: those words are phonemised as Malay inside an English sentence (e.g. names).
import json, re, sys, os
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

lines_path, out, mdir = sys.argv[1:4]
voice = sys.argv[4] if len(sys.argv) > 4 else 'am_michael'
speed = float(sys.argv[5]) if len(sys.argv) > 5 else 1.0
k = Kokoro(os.path.join(mdir, 'kokoro-v1.0.onnx'), os.path.join(mdir, 'voices-v1.0.bin'))
os.makedirs(out, exist_ok=True)
report = []
for ln in json.load(open(lines_path)):
    lang = ln.get('lang', 'en-us')
    parts = re.split(r'(\{ms:[^}]*\})', ln['text'])
    ph = ''
    for p in parts:
        if not p: continue
        if p.startswith('{ms:'):
            ph += ' ' + k.tokenizer.phonemize(p[4:-1], 'ms') + ' '
        else:
            ph += k.tokenizer.phonemize(p, lang)
    audio, sr = k.create(ph.strip(), voice=voice, speed=ln.get('speed', speed), is_phonemes=True)
    sf.write(os.path.join(out, f"{ln['id']}.wav"), audio, sr)
    d = len(audio) / sr
    slot = ln['end'] - ln['t']
    report.append((ln['id'], ln['t'], round(d, 2), round(slot, 2), 'OVER' if d > slot + 0.3 else ''))
for r in report: print(*r, sep='\t')
