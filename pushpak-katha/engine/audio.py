"""Sound helpers: lip envelope, synthesized instruments and effects (numpy only)."""
import math, random
import numpy as np
SR, FPS = 44100, 30

def lip_env(x):
    hop = SR // FPS; n = len(x) // hop + 1
    r = np.array([np.sqrt(np.mean(x[i*hop:(i + 1)*hop] ** 2)) if i*hop < len(x) - 1 else 0 for i in range(n)])
    ref = np.percentile(r[r > 0], 90) if np.any(r > 0) else 1
    e = np.clip((r / ref - 0.15) / 0.85, 0, 1) ** 0.8
    return [round(float(v), 3) for v in e]

RNG = np.random.default_rng(21)

def tarr(d): return np.arange(int(d * SR)) / SR

def noise(d): return RNG.standard_normal(int(d * SR))

def band(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X[(f < lo) | (f > hi)] = 0
    y = np.fft.irfft(X, len(x)); return y / (np.max(np.abs(y)) + 1e-9)

def add(buf, t0, sig, g=1.0):
    i = int(t0 * SR)
    if i < 0: sig = sig[-i:]; i = 0
    j = min(len(buf), i + len(sig))
    if j > i: buf[i:j] += sig[:j - i] * g

def reverb(x):
    ir_t = tarr(1.4); ir = noise(1.4) * np.exp(-ir_t / 0.32); ir[:int(0.02*SR)] = 0; ir /= np.sqrt(np.sum(ir**2))
    n = len(x) + len(ir); y = np.fft.irfft(np.fft.rfft(x, n) * np.fft.rfft(ir, n), n)
    return np.concatenate([x, np.zeros(len(ir))]) + 0.2 * y / (np.max(np.abs(y)) + 1e-9) * np.max(np.abs(x))

def tanpura(n, pitch=1.0):
    out = np.zeros(n); cache = {}
    for f in (110.0, 146.83, 73.42):
        t = tarr(3.4); s = np.zeros_like(t)
        for h in range(1, 15):
            s += (1 / h) * (1 + 0.5*np.sin(2*np.pi*0.6*t*h/3 + h)) * np.sin(2*np.pi*f*pitch*h*t*(1 + 0.0006*h))
        cache[f] = s * np.exp(-t / 1.5) * np.minimum(1, t / 0.01)
    seq = [110.0, 146.83, 146.83, 73.42]; t0 = 0.3; i = 0
    while t0 < n / SR: add(out, t0, cache[seq[i % 4]]); t0 += 0.78; i += 1
    return out / (np.max(np.abs(out)) + 1e-9)

SCALE = [293.66, 329.63, 369.99, 440, 493.88, 587.33, 659.26, 739.99, 880]

def bansuri(n, seed, pitch=1.0):
    rng = random.Random(seed); out = np.zeros(n); t0 = 1.2; idx = 5
    while t0 < n / SR - 1.5:
        d = rng.choice([0.45, 0.45, 0.9, 0.9, 1.35, 1.8, 2.7])
        idx = max(0, min(8, idx + rng.choice([-2, -1, -1, 0, 1, 1, 2]))); f = SCALE[idx] * pitch
        L = d + 0.25; tt = tarr(L)
        vib = 1 + 0.006*np.sin(2*np.pi*5.2*tt)*np.clip((tt - 0.25) / 0.3, 0, 1)
        ph = 2*np.pi*np.cumsum(f*vib) / SR
        tone = np.sin(ph) + 0.12*np.sin(2*ph) + 0.04*np.sin(3*ph) + 0.05*band(noise(L), f*0.9, f*2.5)
        add(out, t0, tone * np.minimum(1, tt / 0.07) * np.clip((L - tt) / 0.25, 0, 1))
        t0 += d
        if rng.random() < 0.18: t0 += rng.choice([0.9, 1.8])
    return out / (np.max(np.abs(out)) + 1e-9)

def pad(freqs, d):
    t = tarr(d + 1.5); s = np.zeros_like(t)
    for f in freqs:
        for det in (1.0, 1.004, 0.996): s += np.sin(2*np.pi*f*det*t) * 0.5 + 0.15*np.sin(4*np.pi*f*det*t)
    return s / (len(freqs) * 3) * np.minimum(1, t / 1.0) * np.clip((d + 1.5 - t) / 1.5, 0, 1)

def bell(f0=520, d=4.0):
    t = tarr(d); s = np.zeros_like(t)
    for r, a, dc in ((1, 1, 2.5), (2.0, 0.6, 2.0), (2.76, 0.5, 1.6), (3.9, 0.3, 1.2), (5.4, 0.2, 0.9), (6.8, 0.1, 0.7)):
        s += a * np.sin(2*np.pi*f0*r*t) * np.exp(-t / dc)
    return s * np.minimum(1, t / 0.003) / 2.7

def sweep(f0, f1, d, decay):
    t = tarr(d); f = np.linspace(f0, f1, len(t))
    return np.sin(2*np.pi*np.cumsum(f) / SR) * np.exp(-t*decay) * np.minimum(1, t / 0.003)

def chirp(d=0.12):
    t = tarr(d); f = 3300 + 1300*np.sin(2*np.pi*28*t) + 2000*t/d
    return np.sin(2*np.pi*np.cumsum(f) / SR) * np.hanning(len(t))

SUSPENSE = [[110, 164.81, 220, 261.63], [98, 146.83, 196, 233.08], [87.31, 130.81, 174.61, 207.65], [82.41, 123.47, 164.81, 207.65]]
