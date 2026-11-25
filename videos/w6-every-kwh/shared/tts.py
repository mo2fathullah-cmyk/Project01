# Generate voice-over clips with Kokoro (offline).
# Usage: python3 tts.py <lines.json> <outdir> <model_dir> [voice] [speed] [accent: my|none]
# lines.json: [{"id":..,"t":start_seconds,"end":caption_end,"lang":"en-gb"|"ms","text":..} ...]
# Text may contain {ms:...} spans: those words are phonemised as Malay inside an English sentence (e.g. names).
#
# accent "my" = Malaysian English: English is phonemised (en-gb) and then reshaped with common
# Malay-English features, so one Malay speaker voices both the English and the BM lines.
import json, re, sys, os
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

# order matters: multi-character patterns first
MY_RULES = [
    ('eɪ', 'e'), ('əʊ', 'o'), ('oʊ', 'o'), ('ɪə', 'iə'), ('eə', 'ɛ'),   # flatter diphthongs: "day" /de/, "go" /go/
    ('ð', 'd'), ('θ', 't'),                                            # "the" -> "de", "three" -> "tree"
    ('ɹ', 'r'), ('ɾ', 'r'),                                            # Malay r
    ('ɜː', 'ə'), ('ɜ', 'ə'), ('ʌ', 'a'), ('ɐ', 'ə'),                  # "work" /wək/, "but" /bat/
    ('ɒ', 'ɔ'), ('ɔː', 'ɔ'), ('ɑː', 'a'), ('ɑ', 'a'),
    ('iː', 'i'), ('ɪ', 'i'), ('uː', 'u'), ('ʊ', 'u'), ('æ', 'ɛ'),      # tense/lax merge, pure vowels
    ('ː', ''), ('ˌ', ''),                                              # no vowel length, flatter (syllable-timed) stress
]

def malaysian(ph):
    for a, b in MY_RULES:
        ph = ph.replace(a, b)
    return ph

def phonemes(k, text, lang='en-gb', accent='my'):
    ph = ''
    for p in re.split(r'(\{ms:[^}]*\})', text):
        if not p:
            continue
        if p.startswith('{ms:'):
            ph += ' ' + k.tokenizer.phonemize(p[4:-1], 'ms') + ' '
        elif lang == 'ms':
            ph += k.tokenizer.phonemize(p, 'ms')
        else:
            e = k.tokenizer.phonemize(p, lang)
            ph += malaysian(e) if accent == 'my' else e
    return re.sub(r'\s+', ' ', ph).strip()

def load(mdir):
    return Kokoro(os.path.join(mdir, 'kokoro-v1.0.onnx'), os.path.join(mdir, 'voices-v1.0.bin'))

if __name__ == '__main__':
    lines_path, out, mdir = sys.argv[1:4]
    voice = sys.argv[4] if len(sys.argv) > 4 else 'am_michael'
    speed = float(sys.argv[5]) if len(sys.argv) > 5 else 1.0
    accent = sys.argv[6] if len(sys.argv) > 6 else 'my'
    k = load(mdir)
    os.makedirs(out, exist_ok=True)
    for ln in json.load(open(lines_path)):
        ph = phonemes(k, ln['text'], ln.get('lang', 'en-gb'), accent)
        audio, sr = k.create(ph, voice=voice, speed=ln.get('speed', speed), is_phonemes=True)
        sf.write(os.path.join(out, f"{ln['id']}.wav"), audio, sr)
        d = len(audio) / sr
        slot = ln['end'] - ln['t']
        print(ln['id'], ln['t'], round(d, 2), round(slot, 2), 'OVER' if d > slot + 0.3 else '', sep='\t')
