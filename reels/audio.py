"""Voices (edge-tts), lip-sync envelopes, synthesized music (tanpura, bansuri, pads) and sound effects, mixed to WAV."""
import os, math, random, subprocess, wave
import numpy as np
from .config import SR, FPS, VOICES
from .util import ffmpeg_exe


async def tts_all(items):
    import edge_tts
    for path, text, spk in items:
        if not os.path.exists(path):
            v, rate, pitch = VOICES[spk]
            await edge_tts.Communicate(text, v, rate=rate, pitch=pitch).save(path)

def decode(path):
    raw = subprocess.run([ffmpeg_exe(), "-v", "quiet", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).astype(np.float64)
    idx = np.where(np.abs(x) > 0.02)[0]
    if len(idx): x = x[max(0, idx[0] - 800): idx[-1] + 2500]
    act = np.abs(x) > 0.01
    rms = np.sqrt(np.mean(x[act] ** 2)) if act.any() else 1
    return x * (0.12 / rms)

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

def tanpura(n):
    out = np.zeros(n); cache = {}
    for f in (110.0, 146.83, 73.42):
        t = tarr(3.4); s = np.zeros_like(t)
        for h in range(1, 15):
            s += (1 / h) * (1 + 0.5*np.sin(2*np.pi*0.6*t*h/3 + h)) * np.sin(2*np.pi*f*h*t*(1 + 0.0006*h))
        cache[f] = s * np.exp(-t / 1.5) * np.minimum(1, t / 0.01)
    seq = [110.0, 146.83, 146.83, 73.42]; t0 = 0.3; i = 0
    while t0 < n / SR: add(out, t0, cache[seq[i % 4]]); t0 += 0.78; i += 1
    return out / (np.max(np.abs(out)) + 1e-9)

SCALE = [293.66, 329.63, 369.99, 440, 493.88, 587.33, 659.26, 739.99, 880]

def bansuri(n, seed):
    rng = random.Random(seed); out = np.zeros(n); t0 = 1.2; idx = 5
    while t0 < n / SR - 1.5:
        d = rng.choice([0.45, 0.45, 0.9, 0.9, 1.35, 1.8, 2.7])
        idx = max(0, min(8, idx + rng.choice([-2, -1, -1, 0, 1, 1, 2]))); f = SCALE[idx]
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


def music_bed(kind, n, total, seed):
    """Background music for the whole reel: suspense pads (paheli) or tanpura + bansuri (devotional)."""
    bed = np.zeros(n)
    if kind == "paheli":
        t0 = 0.0
        for i in range(int(total // 4) + 1):
            add(bed, t0, pad(SUSPENSE[i % 4], 4.0), 0.8); t0 += 4.0
        return bed + tanpura(n) * 0.3
    return bed + tanpura(n) * 0.55 + bansuri(n, seed) * 0.5


def shot_sfx(sfx, bed, s, first, rng):
    """Sound effects for one shot: a whoosh on every cut plus scene ambience."""
    st, d, kd = s["start"], s["dur"], s["kind"]
    if not first:
        add(sfx, st - 0.4, band(noise(0.8), 300, 3000) * np.hanning(int(0.8 * SR)), 0.08)
    if kd == "darbar":                                   # deep drum hit
        tq = tarr(1.2); add(sfx, st + 0.05, np.sin(2*np.pi*58*tq) * np.exp(-tq*4.5) * np.minimum(1, tq / 0.004), 0.35)
    if kd == "divine":                                   # warm chord + sparkle
        add(bed, st, pad([146.83, 220, 293.66, 369.99], d), 0.7)
        for j, f in enumerate([587.33, 659.26, 739.99, 880, 987.77, 1174.66]):
            add(sfx, st + 0.1 + j*0.06, sweep(f, f, 1.2, 3.5), 0.06)
    if kd in ("walk", "meet"):                           # birds + soft wind
        tb = 0.6
        while tb < d:
            add(sfx, st + tb, chirp(), 0.045); add(sfx, st + tb + 0.17, chirp(), 0.04); tb += rng.uniform(1.4, 3.2)
        add(sfx, st, band(noise(d), 200, 900) * np.minimum(1, tarr(d) / 0.5), 0.02)
    if kd == "walk" or (kd == "meet" and s.get("arrive")):   # footsteps
        tw, end = 0.1, (d if kd == "walk" else 2.8)
        while tw < end:
            tq = tarr(0.09); add(sfx, st + tw, band(noise(0.09), 60, 500) * np.exp(-tq*40), 0.07); tw += math.pi / 6.5


def build_audio(tl, voices, path, seed):
    """Mix voices, music and effects for a timeline and write a stereo WAV."""
    total = tl["total"]; n = int((total + 0.6) * SR)
    voice, sfx = np.zeros(n), np.zeros(n)
    for ph in tl["phrases"]:
        x = voices[ph["idx"]]
        add(voice, ph["start"], reverb(x) if ph["spk"] == "K" else x)
    bed = music_bed(tl.get("type"), n, total, seed)
    rng = random.Random(seed)
    for si, s in enumerate(tl["shots"]):
        shot_sfx(sfx, bed, s, si == 0, rng)
    last = tl["shots"][-1]
    add(sfx, 0.12, bell(520), 0.4)                                   # opening bell
    add(sfx, tl["phrases"][-1]["start"], bell(520), 0.35)            # last line
    add(sfx, last["start"] + last["narr_end"] + 0.4, bell(700, 3.0), 0.3)   # end card

    # duck the music under the voice, fade in/out, normalise
    a = np.abs(voice); k = int(0.25 * SR); cs = np.cumsum(np.concatenate([[0], a]))
    env = np.zeros(n); env[k//2: k//2 + n - k + 1] = (cs[k:] - cs[:-k]) / k
    bed *= 1 - 0.55 * np.clip(env / 0.05, 0, 1)
    bed *= np.clip((total - np.arange(n) / SR) / 1.8, 0, 1) * np.minimum(1, np.arange(n) / SR / 0.8)
    mix = voice + bed * 0.13 + sfx * 0.6
    mix /= max(1.0, np.max(np.abs(mix)) / 0.97)
    pcm = (np.clip(mix, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR)
        wf.writeframes(np.repeat(pcm[:, None], 2, axis=1).tobytes())
