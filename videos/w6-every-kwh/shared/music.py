# Original bass-heavy lo-fi trap bed, synthesised from scratch (no samples, no copyright issues).
# Usage: python3 music.py <out.wav> <duration_s> <cues.json>
# cues.json: {"lift": t, "break": [t0, t1], "riser": [t0, t1], "drop": t}  (seconds, final timeline)
import sys, json
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt, fftconvolve

out, DUR, cues = sys.argv[1], float(sys.argv[2]), json.load(open(sys.argv[3]))
SR = 48000; BPM = 88; BEAT = 60 / BPM; BAR = 4 * BEAT; S16 = BEAT / 4
N = int(DUR * SR) + SR
rng = np.random.default_rng(7)
L = np.zeros(N); R = np.zeros(N)

def lp(x, f, o=2): return sosfilt(butter(o, f, 'low', fs=SR, output='sos'), x)
def hp(x, f, o=2): return sosfilt(butter(o, f, 'high', fs=SR, output='sos'), x)
def bp(x, lo, hi): return sosfilt(butter(2, [lo, hi], 'band', fs=SR, output='sos'), x)
def add(buf, t, x, g=1.0):
    s = int(t * SR)
    if s >= N or s < 0: return
    e = min(N, s + len(x)); buf[s:e] += g * x[:e - s]
def addst(t, x, g=1.0, pan=0.0):
    add(L, t, x, g * (1 - max(0, pan))); add(R, t, x, g * (1 + min(0, pan)))

# --- instruments ---
def kick():
    n = int(.45 * SR); t = np.arange(n) / SR
    f = 48 + 110 * np.exp(-t * 32)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)
    x += .35 * rng.standard_normal(n) * np.exp(-t * 300)  # click
    return np.tanh(1.6 * x)
def b808(freq, dur, glide_from=None):
    n = int(dur * SR); t = np.arange(n) / SR
    f = np.full(n, freq)
    if glide_from: f = freq + (glide_from - freq) * np.exp(-t * 18)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR)
    env = np.minimum(1, t / .005) * np.exp(-t * 1.1)
    env[-int(.03 * SR):] *= np.linspace(1, 0, int(.03 * SR))
    # saturation adds 2nd/3rd harmonics so the bass is heard on earphones and phone speakers
    return np.tanh(2.2 * x * env) * .9
def clap():
    n = int(.35 * SR); t = np.arange(n) / SR
    nz = bp(rng.standard_normal(n), 900, 5000)
    env = sum(np.exp(-np.maximum(0, t - d) * 60) * (t >= d) for d in (0, .011, .022)) / 3 + .6 * np.exp(-t * 18)
    body = .4 * np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30)
    return (nz * env + body) * .8
def hat(open_=False):
    n = int((.18 if open_ else .045) * SR); t = np.arange(n) / SR
    return hp(rng.standard_normal(n), 7000, 4) * np.exp(-t * (18 if open_ else 110))
def keys(freqs, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    x = np.zeros(n)
    for f in freqs:
        x += np.sin(2 * np.pi * f * t + 1.2 * np.sin(2 * np.pi * f * t) * np.exp(-t * 3)) * (1 / (1 + f / 900))
    env = np.minimum(1, t / .01) * np.exp(-t * 1.6) * (1 + .12 * np.sin(2 * np.pi * 4.5 * t))
    return lp(x * env, 2600) / len(freqs)
def pluck(f, dur=.5):
    n = int(dur * SR); t = np.arange(n) / SR
    x = np.sign(np.sin(2 * np.pi * f * t)) * .5 + np.sin(2 * np.pi * 2 * f * t) * .3
    return lp(x * np.exp(-t * 7), 3200)

mid = lambda m: 440 * 2 ** ((m - 69) / 12)
# A minor: Am9 - Fmaj7 - Cmaj7 - G6   (bass roots A1, F1, C2, G1)
PROG = [([57, 60, 64, 67, 71], 33), ([53, 57, 60, 64], 29), ([48, 55, 59, 64], 36), ([55, 59, 62, 64], 31)]
HOOK = [76, 74, 72, 69]   # 4-note motif, one per bar, on beat 1 "and"

brk0, brk1 = cues['break']; rs0, rs1 = cues['riser']; drop = cues['drop']; lift = cues['lift']
def in_break(t): return brk0 <= t < brk1 or rs0 <= t < drop
kenv = np.zeros(N)  # kick envelope used to pump the keys (sidechain feel)

nbars = int(DUR / BAR) + 2
for b in range(nbars):
    t0 = b * BAR
    chord, root = PROG[b % 4]
    rootf = mid(root)
    intro = b == 0
    # keys: chord stab on 1, re-hit on beat 3 "and"
    for off, g in ((0, .55), (2.5 * BEAT, .35)):
        tt = t0 + off
        if tt < DUR - .5: addst(tt, keys([mid(m) for m in chord], BAR * .9), 1.8 * g * (.6 if in_break(tt) else 1), pan=-.15)
    if not intro and not in_break(t0) and b % 2 == 1:
        addst(t0 + BEAT * .5, pluck(mid(HOOK[(b // 2) % 4])), .4, pan=.3)
    for st in range(16):
        tt = t0 + st * S16 + (S16 * .12 if st % 2 else 0)  # swing
        if tt >= DUR - .3: continue
        brk = in_break(tt)
        busy = tt >= lift
        # kick: 1, "a" of 2, 3-and
        if not intro and not brk and st in (0, 7, 10):
            addst(tt, kick(), .95); add(kenv, tt, np.exp(-np.arange(int(.3 * SR)) / SR * 14))
        # 808: follows the kick, slides into the next chord on the last 16th
        if not brk and st in (0, 7, 10) and tt >= 0:
            d = 3 * S16 if st == 7 else (6 * S16 if st == 10 else 7 * S16)
            glide = rootf * 1.5 if (busy and st == 10) else None
            addst(tt, b808(rootf, d, glide), 1.0 if not intro else .8)
        if brk and st == 0 and brk0 <= tt < brk1:
            addst(tt, b808(rootf, BAR * .95), .55)  # long held bass under the KEY POINT card
        if not intro and not brk and st in (4, 12):
            addst(tt, clap(), .8)
        # hats: 8ths, 16ths after the lift, ticking quarters during the countdown
        if rs0 <= tt < drop:
            if st % 4 == 0: addst(tt, hat(), .5, pan=.25)
        elif not brk and (st % 2 == 0 or busy) and not intro:
            vel = .30 if st % 4 == 0 else .18
            addst(tt, hat(st == 14 and b % 2 == 1), 1.7 * vel, pan=.25)

# sidechain pump on everything except kick/808 is approximated by ducking the stereo bed slightly
pump = 1 - .35 * np.clip(kenv, 0, 1)
# riser (filtered noise sweep) into the answer drop, plus impacts at 0 s and at the drop
n = int((rs1 - rs0) * SR); tt = np.arange(n) / SR
riser = rng.standard_normal(n); out_r = np.zeros(n); seg = int(.05 * SR)
for i in range(0, n, seg):
    fc = 300 + 7000 * (i / n) ** 2
    out_r[i:i + seg] = bp(riser[max(0, i - seg):i + seg], fc * .7, min(fc * 1.4, 20000))[-len(out_r[i:i + seg]):]
out_r *= (tt / tt[-1]) ** 2 * .35
addst(rs0, out_r, 1.0)
for t in (0.0, drop):
    addst(t, kick(), 1.1); addst(t, b808(mid(33), 1.6, glide_from=mid(45)), 1.0)
    rv = rng.standard_normal(int(1.2 * SR)) * np.exp(-np.arange(int(1.2 * SR)) / SR * 4)
    addst(t, lp(rv, 3000) * .25, 1.0)

L *= pump; R *= pump
# short room reverb on the bed for width
ir = rng.standard_normal(int(.6 * SR)) * np.exp(-np.arange(int(.6 * SR)) / SR * 9) * .06
L = L + lp(fftconvolve(L, ir)[:N], 5000); R = R + lp(fftconvolve(R, ir[::-1])[:N], 5000)
st = np.stack([L, R], 1)[:int(DUR * SR)]
# fade in/out
fi = int(.02 * SR); fo = int(2.5 * SR)
st[:fi] *= np.linspace(0, 1, fi)[:, None]; st[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 1.5
st = np.tanh(st / np.abs(st).max() * 1.3) * .85
sf.write(out, st.astype('float32'), SR)
print('music', out, round(len(st) / SR, 2), 's')
