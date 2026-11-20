"""Original cheerful score + SFX for 'Misi Penjelajah Cilik'. Pure numpy synthesis, synced to timeline.json."""
import json, wave, numpy as np

SR = 44100
TL = json.load(open('timeline.json'))
TOTAL = TL['total'] + 0.3
N = int(TOTAL * SR)
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(7)

def secs(name):
    return [(s['s'], s['e']) for s in TL['tl'] if s['k'] == name]
def scene_at(t):
    for s in TL['tl']:
        if s['s'] <= t < s['e']:
            return s
    return TL['tl'][-1]

def add(sig, t, pan=0.0, gain=1.0):
    i = int(t * SR)
    if i >= N or i + len(sig) <= 0: return
    j = min(N, i + len(sig)); s = sig[:j - i] * gain
    L[i:j] += s * np.sqrt(0.5 * (1 - pan)) * 1.414
    R[i:j] += s * np.sqrt(0.5 * (1 + pan)) * 1.414

def hz(n):  # midi -> Hz
    return 440.0 * 2 ** ((n - 69) / 12)
NOTE = {'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}
def m(s):  # 'E5' -> midi
    return 12 * (int(s[-1]) + 1) + NOTE[s[0]] + (1 if '#' in s else 0)

def env_ad(n, a, d):
    t = np.arange(n) / SR
    e = np.exp(-t * d)
    k = max(1, int(a * SR)); e[:k] *= np.linspace(0, 1, k)
    return e

def lowpass(x, k):
    if k <= 1: return x
    w = np.hanning(k); w /= w.sum()
    return np.convolve(x, w, mode='same')

# ---------------- instruments ----------------
def pluck(f, dur=1.4, bright=1.0):
    n = int(dur * SR); t = np.arange(n) / SR; out = np.zeros(n)
    for k in range(1, 11):
        if f * k > 12000: break
        out += (1 / k ** (1.35 / bright)) * np.sin(2 * np.pi * f * k * t + k) * np.exp(-t * (2.6 + 1.7 * k))
    out *= env_ad(n, 0.003, 0.0)
    return out * 0.35

def glock(f, dur=1.8):
    n = int(dur * SR); t = np.arange(n) / SR
    s = (np.sin(2*np.pi*f*t) * np.exp(-t*2.2) + 0.32*np.sin(2*np.pi*f*2.756*t) * np.exp(-t*7)
         + 0.12*np.sin(2*np.pi*f*5.404*t) * np.exp(-t*13))
    s *= env_ad(n, 0.002, 0)
    return s * 0.28

def bass(f, dur=0.9):
    n = int(dur * SR); t = np.arange(n) / SR
    s = np.sin(2*np.pi*f*t) + 0.35*np.sin(4*np.pi*f*t) + 0.1*np.sin(6*np.pi*f*t)
    return np.tanh(1.4 * s * env_ad(n, 0.006, 3.2)) * 0.42

def pad(freqs, dur, att=0.6, rel=0.8, gain=0.06):
    n = int(dur * SR); t = np.arange(n) / SR; s = np.zeros(n)
    for f in freqs:
        for det in (-0.12, 0.0, 0.13):
            ph = rng.random()
            s += 2 * ((t * f * 2 ** (det / 12) + ph) % 1) - 1
    s = lowpass(s, 48)
    e = np.ones(n); a = int(att * SR); r = int(rel * SR)
    e[:a] = np.linspace(0, 1, a); e[-r:] *= np.linspace(1, 0, r)
    return s * e * gain / max(1, len(freqs))

def kick(g=1.0):
    n = int(0.35 * SR); t = np.arange(n) / SR
    f = 50 + 95 * np.exp(-t * 28)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9) * 0.55 * g

def noise(n): return rng.standard_normal(n)
def band(x, lo, hi):  # crude band via moving averages
    return lowpass(x, lo) - lowpass(x, hi)

def clap(g=1.0):
    n = int(0.22 * SR); x = band(noise(n), 4, 30); t = np.arange(n) / SR
    e = np.exp(-t * 22)
    for d in (0.0, 0.011, 0.022):
        k = int(d * SR); e[k:k + int(0.004 * SR)] += 0.8
    return x * e * 0.32 * g

def shaker(g=1.0):
    n = int(0.07 * SR); x = noise(n) - lowpass(noise(n), 6); t = np.arange(n) / SR
    return x * np.exp(-t * 60) * env_ad(n, 0.01, 0) * 0.06 * g

def whoosh(dur=0.7, g=1.0, rise=False):
    n = int(dur * SR); x = noise(n); t = np.linspace(0, 1, n)
    e = np.sin(np.pi * t) ** 2 if not rise else t ** 2.2 * (1 - np.clip((t - 0.92) / 0.08, 0, 1))
    return (0.6 * lowpass(x, 14) + 0.4 * lowpass(x, 5)) * e * 0.22 * g

def pop(g=1.0):
    n = int(0.12 * SR); t = np.arange(n) / SR
    f = 380 + 700 * np.exp(-t * 40)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 30) * 0.3 * g

def click():
    n = int(0.03 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 2200 * t) * 0.5 + noise(n) * 0.3) * np.exp(-t * 180) * 0.4

def horn():
    out = np.zeros(int(0.5 * SR))
    for k, (f, st) in enumerate(((523, 0.0), (659, 0.2))):
        n = int(0.16 * SR); t = np.arange(n) / SR
        s = sum(np.sin(2 * np.pi * f * h * t) / h for h in (1, 3, 5)) * env_ad(n, 0.01, 6)
        i = int(st * SR); out[i:i + n] += s * 0.12
    return out

def brass(freqs, dur, g=0.12):
    n = int(dur * SR); t = np.arange(n) / SR; s = np.zeros(n)
    for f in freqs:
        s += 2 * ((t * f) % 1) - 1 + 2 * ((t * f * 1.004) % 1) - 1
    s = lowpass(s, 10)
    e = np.minimum(1, t / 0.02) * np.exp(-t * 1.2)
    return s * e * g / len(freqs)

# ---------------- score ----------------
BEAT = 0.5; BAR = 2.0; EIGHTH = 0.25
CH = {'C': ['C', 'E', 'G'], 'G': ['G', 'B', 'D'], 'Am': ['A', 'C', 'E'], 'F': ['F', 'A', 'C']}
UKE = {'C': ['G4', 'C4', 'E4', 'C5'], 'G': ['G4', 'D4', 'G4', 'B4'], 'Am': ['A4', 'C4', 'E4', 'A4'], 'F': ['A4', 'C4', 'F4', 'A4']}
ROOT = {'C': 'C2', 'G': 'G2', 'Am': 'A2', 'F': 'F2'}
FIFTH = {'C': 'G2', 'G': 'D3', 'Am': 'E2', 'F': 'C3'}
PROG = ['C', 'G', 'Am', 'F']
MEL = [
    ['E5', None, 'G5', None, 'A5', 'G5', 'E5', None], ['D5', None, 'G5', None, 'B4', None, 'D5', None],
    ['C5', None, 'E5', None, 'A5', None, 'G5', 'E5'], ['F5', None, 'A5', None, 'G5', None, 'E5', None],
    ['G5', None, 'C6', None, 'A5', 'G5', 'E5', 'G5'], ['D6', None, 'B5', None, 'G5', None, 'D5', None],
    ['E5', None, 'A5', None, 'C6', None, 'A5', 'G5'], ['A5', None, 'G5', None, 'F5', 'E5', 'D5', 'C5'],
]
STRUM = [(0, 1.0, 1), (2, .75, 1), (3, .55, -1), (5, .55, -1), (6, .75, 1), (7, .5, -1)]

def mode_at(t):
    s = scene_at(t)
    k = s['k']
    if k == 'intro': return 'intro'
    if k == 'map':
        if s['s'] > 115: return 'night'
        if s['s'] > 100: return 'calm'
        return 'main'
    if k == 'level':
        if 'Masjid' in s['title']: return 'calm'
        if '249' in s['title']: return 'boss'
        return 'main'
    if k == 'done': return 'main'
    return 'outro'

ORIGIN = 6.2
end_music = TL['total']
bar = 0
t0 = ORIGIN
while t0 < end_music - 0.5:
    md = mode_at(t0 + 0.05)
    ch = PROG[bar % 4]
    mel = MEL[bar % 8]
    soft = md in ('calm', 'night', 'outro')
    # pad always
    add(pad([hz(m(n + '3')) for n in CH[ch]], BAR + 0.6, att=0.4 if not soft else 0.8, gain=0.05 if not soft else 0.075), t0, 0, 1)
    # ukulele
    if md in ('main', 'boss'):
        for pos, vel, d in STRUM:
            notes = UKE[ch] if d > 0 else UKE[ch][::-1]
            for k, nn in enumerate(notes):
                add(pluck(hz(m(nn)), 1.1), t0 + pos * EIGHTH + k * 0.012, -0.35, 0.55 * vel)
    elif md in ('calm', 'outro'):
        for pos in range(8):  # gentle fingerpicking
            nn = UKE[ch][[1, 2, 3, 2, 0, 2, 3, 2][pos]]
            add(pluck(hz(m(nn)), 1.3, 0.8), t0 + pos * EIGHTH, -0.3, 0.42)
    # bass
    if md in ('main', 'boss'):
        add(bass(hz(m(ROOT[ch]))), t0, 0, 1)
        add(bass(hz(m(ROOT[ch]))), t0 + 4 * EIGHTH, 0, .8)
        add(bass(hz(m(FIFTH[ch])), 0.4), t0 + 7 * EIGHTH, 0, .6)
    elif md in ('calm', 'outro'):
        add(bass(hz(m(ROOT[ch])), 1.6), t0, 0, .55)
    # drums
    if md in ('main', 'boss'):
        for b in (0, 2): add(kick(), t0 + b * BEAT)
        for b in (1, 3): add(clap(), t0 + b * BEAT, 0.1)
        for e in range(8): add(shaker(1.2 if e % 2 else 0.7), t0 + e * EIGHTH, 0.4)
        if md == 'boss':
            for e in range(16): add(shaker(0.8), t0 + e * EIGHTH / 2, -0.4)
            add(clap(.6), t0 + 3.5 * BEAT, -0.1)
    # melody (glock), octave up
    if md in ('main', 'boss', 'calm', 'outro', 'night'):
        step = 1 if md in ('main', 'boss') else 2
        for pos in range(0, 8, step):
            nn = mel[pos]
            if nn is None: continue
            f = hz(m(nn) + 12)
            add(glock(f, 1.6), t0 + pos * EIGHTH, 0.3, 0.75 if not soft else 0.55)
            if md == 'boss': add(pluck(hz(m(nn)), 0.6, 1.3), t0 + pos * EIGHTH, 0.2, 0.35)
    t0 += BAR; bar += 1

# intro (0..6.2): sparkle arps over C pad
add(pad([hz(m('C3')), hz(m('G3')), hz(m('E4'))], 6.4, att=1.5, rel=1.0, gain=0.09), 0.0)
for i, nn in enumerate(['C6', 'E6', 'G6', 'C7', 'G6', 'E6', 'G6', 'C7', 'E7']):
    add(glock(hz(m(nn)), 2.0), 0.6 + i * 0.32, 0.4 * np.sin(i), 0.35)
add(bass(hz(m('C2')), 2.5), 4.0, 0, .6)

# ending chord + fade
fin = TL['total'] - 3.2
add(pad([hz(m('C3')), hz(m('E3')), hz(m('G3')), hz(m('C4'))], 3.4, att=0.2, rel=2.0, gain=0.09), fin)
for i, nn in enumerate(['C5', 'E5', 'G5', 'C6']):
    add(glock(hz(m(nn) + 12), 3.0), fin + i * 0.09, 0.2, 0.6)

# ---------------- SFX from cues ----------------
for c in TL['cues']:
    t, k = c['t'], c['type']
    if k == 'shimmer':
        for i, nn in enumerate(['G6', 'C7', 'E7', 'G7']): add(glock(hz(m(nn)), 2.4), t + i * 0.07, 0.5 - i * 0.3, 0.3)
    elif k == 'ding':
        add(glock(hz(m('C7')), 3.0), t, 0, 0.9); add(glock(hz(m('G7')), 2.5), t + 0.02, 0.2, 0.5)
    elif k == 'whoosh': add(whoosh(0.7), t - 0.35, 0, 1.2)
    elif k == 'pop': add(pop(), t, 0, 1)
    elif k == 'click': add(click(), t)
    elif k == 'horn': add(horn(), t, -0.2, 1)
    elif k.startswith('engine'):
        d = float(k.split('_')[1]); n = int(d * SR); tt = np.arange(n) / SR
        rum = lowpass(noise(n), 60) * 3 + 0.4 * np.sin(2 * np.pi * 55 * tt) * (1 + 0.3 * np.sin(2 * np.pi * 9 * tt))
        e = np.minimum(1, tt / 0.4) * np.minimum(1, (d - tt) / 0.4)
        add(rum * e * 0.12, t, -0.1)
        add(whoosh(0.8, 0.9), t + d - 0.6, 0.3)
    elif k in ('stamp', 'boss'):
        add(whoosh(0.5, 1.2), t - 0.3)
        add(kick(1.6 if k == 'boss' else 1.1), t)
        for i, nn in enumerate(['C6', 'E6', 'G6']): add(glock(hz(m(nn)), 1.6), t + 0.02 * i, 0, 0.45)
        if k == 'boss':
            add(brass([hz(m('C4')), hz(m('G4')), hz(m('C5'))], 0.9, 0.16), t)
            add(whoosh(1.2, 1.0, rise=True), t - 1.2)
    elif k == 'badge':
        for i, nn in enumerate(['C6', 'E6', 'G6', 'C7', 'E7']): add(glock(hz(m(nn)), 1.6), t + i * 0.06, -0.3 + 0.15 * i, 0.55)
        add(pop(1.2), t)
    elif k == 'fanfare':
        for st, d in ((0.0, 0.16), (0.2, 0.16), (0.4, 0.9)):
            add(brass([hz(m('C4')), hz(m('E4')), hz(m('G4')), hz(m('C5'))], d + 0.3, 0.2), t + st)
        add(kick(1.4), t + 0.4); add(clap(1.2), t + 0.4)

# ---------------- mix bus: reverb, master ----------------
def reverb(x, decay=0.38, length=1.6, seed=1):
    n = int(length * SR); r = np.random.default_rng(seed).standard_normal(n)
    ir = r * np.exp(-np.arange(n) / SR / decay); ir = lowpass(ir, 6); ir /= np.sqrt((ir ** 2).sum())
    size = 1 << int(np.ceil(np.log2(len(x) + n)))
    y = np.fft.irfft(np.fft.rfft(x, size) * np.fft.rfft(ir, size), size)[:len(x)]
    return y
wetL = reverb(L, seed=1); wetR = reverb(R, seed=2)
L2 = L + 0.18 * wetL; R2 = R + 0.18 * wetR
# fade in/out
fade = np.ones(N); fo = int(1.6 * SR); end_i = int(TL['total'] * SR)
fade[end_i - fo:end_i] = np.linspace(1, 0, fo) ** 1.5; fade[end_i:] = 0
fi = int(0.3 * SR); fade[:fi] *= np.linspace(0, 1, fi)
L2 *= fade; R2 *= fade
# gentle glue compression (soft clip)
peak = max(np.abs(L2).max(), np.abs(R2).max())
L2 = np.tanh(1.2 * L2 / peak) / np.tanh(1.2); R2 = np.tanh(1.2 * R2 / peak) / np.tanh(1.2)
st = np.stack([L2, R2], 1) * 0.89
with wave.open('music.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st * 32767).astype('<i2').tobytes())
print('music.wav', round(N / SR, 2), 's')
