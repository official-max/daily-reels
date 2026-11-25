"""Shared engine for the 2D samples: voices + word timings, captions, progress bar, sound, encoding. Drawing is Skia."""
import os, sys, math, json, asyncio, subprocess, random, wave
import numpy as np, skia
from PIL import Image, ImageDraw, ImageFont
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); OUT = os.path.join(ROOT, "out"); os.makedirs(OUT, exist_ok=True)
import audio as au
import imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe(); W, H, FPS, SR = 1080, 1920, 30, 44100
BLACK, BOLD = os.path.join(ROOT, "fonts", "Poppins-Black.ttf"), os.path.join(ROOT, "fonts", "Poppins-Bold.ttf")
M, S = "hi-IN-MadhurNeural", "hi-IN-SwaraNeural"

# ---------------- drawing helpers
def col(c, a=1.0): return skia.Color(int(c[0]), int(c[1]), int(c[2]), int(255 * max(0, min(1, a))))
def mix(a, b, u): return tuple(x + (y - x) * u for x, y in zip(a, b))
def fill(c, a=1.0, blur=0):
    p = skia.Paint(Color=col(c, a), AntiAlias=True)
    if blur: p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    return p
def line(c, w, a=1.0): return skia.Paint(Color=col(c, a), AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=w, StrokeCap=skia.Paint.kRound_Cap, StrokeJoin=skia.Paint.kRound_Join)
def vgrad(c, stops, y0=0, y1=H):
    p = skia.Paint(Shader=skia.GradientShader.MakeLinear([skia.Point(0, y0), skia.Point(0, y1)], [col(s[1]) for s in stops], [s[0] for s in stops]))
    c.drawRect(skia.Rect.MakeLTRB(0, y0, W, y1), p)
def glow(c, x, y, r, rgb, a=1.0):
    p = skia.Paint(Shader=skia.GradientShader.MakeRadial(skia.Point(x, y), r, [col(rgb, a), col(rgb, 0)])); c.drawCircle(x, y, r, p)
def poly(pts, close=True):
    p = skia.Path(); p.moveTo(*pts[0]); [p.lineTo(*q) for q in pts[1:]]
    if close: p.close()
    return p
def smooth(pts, close=True):
    """Closed (or open) smooth curve through the midpoints of pts."""
    p = skia.Path(); n = len(pts); mid = lambda a, b: ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    if close:
        p.moveTo(*mid(pts[-1], pts[0]))
        for i in range(n): p.quadTo(*pts[i], *mid(pts[i], pts[(i + 1) % n]))
        p.close()
    else:
        p.moveTo(*pts[0])
        for i in range(1, n - 1): p.quadTo(*pts[i], *(mid(pts[i], pts[i + 1]) if i < n - 2 else pts[-1]))
    return p
def oval(x, y, rx, ry=None):
    ry = rx if ry is None else ry; p = skia.Path(); p.addOval(skia.Rect.MakeLTRB(x - rx, y - ry, x + rx, y + ry)); return p
INK = (48, 30, 40)
def cel(c, path, rgb, shade=.2, ink=INK, w=7, off=(-12, -12)):
    """Flat cartoon shape: shadow side, lit side, dark outline."""
    c.save(); c.clipPath(path, True); c.drawPaint(fill(mix(rgb, (60, 20, 90), shade))); c.translate(*off); c.drawPath(path, fill(rgb)); c.restore()
    if w: c.drawPath(path, line(ink, w))
def limb(c, pts, w, rgb, ink=INK):
    p = smooth(pts, False); c.drawPath(p, line(ink, w + 13)); c.drawPath(p, line(rgb, w))

# ---------------- voice
async def _speak(lines, d):
    import edge_tts
    for i, ln in enumerate(lines):
        js = f"{d}/{i}.json"; key = [ln["hi"], ln["v"]]
        if os.path.exists(js) and json.load(open(js, encoding="utf-8"))["key"] == [ln["hi"], list(ln["v"])]: continue
        for k in range(4):
            try:
                data, ws = b"", []
                async for x in edge_tts.Communicate(ln["hi"], ln["v"][0], rate=ln["v"][1], pitch=ln["v"][2], boundary="WordBoundary").stream():
                    if x["type"] == "audio": data += x["data"]
                    else: ws.append((x["offset"] / 1e7, (x["offset"] + x["duration"]) / 1e7))
                break
            except Exception:
                if k == 3: raise
                await asyncio.sleep(6)
        open(f"{d}/{i}.mp3", "wb").write(data); json.dump(dict(key=key, words=ws), open(js, "w", encoding="utf-8"))

def build(name, lines):
    """lines: dict(hi, ro, v=(voice, rate, pitch), who, shot, pad). Returns the timeline and voices."""
    d = os.path.join(OUT, "tmp_" + name); os.makedirs(d, exist_ok=True); asyncio.run(_speak(lines, d)); t = .25; out, voices = [], []
    for i, ln in enumerate(lines):
        raw = subprocess.run([FF, "-v", "quiet", "-i", f"{d}/{i}.mp3", "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True, check=True).stdout
        x = np.frombuffer(raw, np.float32).astype(float); tm = json.load(open(f"{d}/{i}.json", encoding="utf-8"))["words"]; end = tm[-1][1]; x = x[:int((end + .25) * SR)]
        toks = ln["ro"].split(); n = len(tm)
        if n != len(toks):
            print("words differ", i, n, len(toks)); st = [w[0] for w in tm] + [end]
            tm = [(float(np.interp(q / len(toks) * n, range(n + 1), st)), float(np.interp((q + 1) / len(toks) * n, range(n + 1), st))) for q in range(len(toks))]
        env = au.lip_env(x); pre = ln.get("pre", 0); t += pre
        out.append(dict(ln, start=t - pre if i else 0.0, voice=t, vend=t + end, words=[(t + a, t + b, w) for (a, b), w in zip(tm, toks)], env=env))
        voices.append((t, x)); t += end + ln.get("pad", .3)
        out[-1]["end"] = t
    return dict(lines=out, total=t, name=name), voices

# ---------------- captions and frame
def captions(fr, tl, T, y0=1455, hlc=(255, 214, 60)):
    for ln in tl["lines"]:
        ws = ln["words"]
        if not (ws[0][0] - .05 <= T <= ws[-1][1] + .2): continue
        gs, cur = [], []
        for w in ws:
            cur.append(w)
            if len(cur) == 4 or (w[2].strip("*")[-1] in ",.?!" and len(cur) > 1) or sum(len(x[2]) for x in cur) > 18: gs.append(cur); cur = []
        if cur: gs.append(cur)
        g = [g for g in gs if g[0][0] - .05 <= T or g is gs[0]][-1]; pop = min(1, max(0, T - g[0][0] + .05) / .12)
        size = int(84 * (.8 + .2 * pop)); f = ImageFont.truetype(BLACK, size); d = ImageDraw.Draw(fr, "RGBA"); rows, cw, sp = [[]], 0, f.getlength(" ")
        for a, b, w in g:
            s = w.replace("*", "").strip(",."); ww = f.getlength(s)
            if rows[-1] and cw + ww > 900: rows.append([]); cw = 0
            rows[-1].append((a, s, ww, "*" in w)); cw += ww + sp
        y = y0; now = [w[0] for w in g if w[0] <= T + .02]
        for r in rows:
            x = (W - sum(q[2] for q in r) - sp * (len(r) - 1)) / 2
            for a, s, ww, hl in r:
                on = now and a == now[-1]
                if on: d.rounded_rectangle([x - 14, y - 2, x + ww + 14, y + size * 1.28], 20, fill=hlc if hl else (225, 35, 55))
                d.text((x, y), s, font=f, fill=(20, 14, 30) if on and hl else hlc if hl else (255, 255, 255), stroke_width=0 if on and hl else 8, stroke_fill=(20, 14, 26)); x += ww + sp
            y += size * 1.35

def frame(T):
    tl = TL; lines = tl["lines"]; i = next((k for k, l in enumerate(lines) if T < l["end"]), len(lines) - 1); ln = lines[i]
    talk = 0.0
    if ln["voice"] <= T < ln["vend"]:
        k = int((T - ln["voice"]) * FPS); talk = ln["env"][k] if k < len(ln["env"]) else 0
    def shot(l, TT):
        s = skia.Surface(W, H); c = s.getCanvas(); c.clear(skia.ColorBLACK)
        SHOTS[l["shot"]](c, TT - l["start"], l["end"] - l["start"], {l["who"]: talk if l is ln else 0}, TT)
        return Image.fromarray(s.toarray(colorType=skia.kRGBA_8888_ColorType)).convert("RGB")
    fr = shot(ln, T); k = T - ln["start"]
    if i and k < .22 and lines[i - 1]["shot"] != ln["shot"]:
        fr = Image.blend(shot(lines[i - 1], T), fr, k / .22)
    d = ImageDraw.Draw(fr, "RGBA")
    d.rounded_rectangle([60, 110, W - 60, 120], 5, fill=(255, 255, 255, 70)); d.rounded_rectangle([60, 110, 60 + max(10, (W - 120) * T / tl["total"]), 120], 5, fill=(255, 205, 30, 255))
    if T < 2.5:
        a = min(1, T / .15) * min(1, (2.5 - T) / .3); o = Image.new("RGBA", (W, 400), (0, 0, 0, 0)); od = ImageDraw.Draw(o); f = ImageFont.truetype(BLACK, 92 if len(TITLE[1]) < 12 else 74)
        od.text((W / 2, 10), TITLE[0], font=ImageFont.truetype(BLACK, 72), fill=(255, 255, 255), anchor="ma", stroke_width=8, stroke_fill=(20, 14, 26))
        w = f.getlength(TITLE[1]) / 2 + 45; od.rounded_rectangle([W / 2 - w, 120, W / 2 + w, 270], 30, fill=(225, 35, 55)); od.text((W / 2, 122), TITLE[1], font=f, fill=(255, 255, 255), anchor="ma")
        o.putalpha(o.getchannel("A").point(lambda v: int(v * a))); fr.paste(o, (0, 230), o)
    captions(fr, tl, T)
    e0 = tl["lines"][-1]["vend"] + .3
    if T > e0 and tl["total"] - e0 > 1.2:                      # end card
        al = int(255 * min(1, (T - e0) / .25)); d = ImageDraw.Draw(fr, "RGBA"); d.text((W / 2, 1330), "Aisi aur kahaniyon ke liye", font=ImageFont.truetype(BOLD, 56), fill=(255, 255, 255, al), anchor="ma", stroke_width=7, stroke_fill=(20, 14, 26, al))
        d.rounded_rectangle([260, 1430, 820, 1560], 65, fill=(225, 35, 55, al), outline=(255, 255, 255, al), width=6); d.text((W / 2, 1446), "SUBSCRIBE", font=ImageFont.truetype(BLACK, 70), fill=(255, 255, 255, al), anchor="ma")
    if T > tl["total"] - .3: fr = Image.blend(fr, Image.new("RGB", (W, H)), min(1, (T - tl["total"] + .3) / .3))
    return fr

def sound(tl, voices, path, music, fxs):
    n = int((tl["total"] + .3) * SR); voice, fx = np.zeros(n), np.zeros(n); bed = music(n, tl)
    for t0, x in voices: au.add(voice, t0, x / (np.sqrt(np.mean(x[np.abs(x) > .01] ** 2)) + 1e-9) * .13)
    fxs(fx, tl); a = np.abs(voice); w = int(.25 * SR); cs = np.cumsum(np.r_[0, a]); env = np.zeros(n); env[w // 2:w // 2 + n - w + 1] = (cs[w:] - cs[:-w]) / w
    bed *= (1 - .5 * np.clip(env / .05, 0, 1)) * np.clip((tl["total"] - np.arange(n) / SR) / .8, 0, 1)
    m = voice + bed * .16 + fx * .5; m /= max(1, np.abs(m).max() / .97)
    with wave.open(path, "wb") as f: f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR); f.writeframes(np.repeat((m * 32767).astype(np.int16)[:, None], 2, 1).tobytes())

def init(tl, shots, title):
    global TL, SHOTS, TITLE
    TL, SHOTS, TITLE = tl, shots, title
def raw(fi): return frame(fi / FPS).tobytes()

def main(name, lines, shots, title, music, fxs):
    tl, voices = build(name, lines); init(tl, shots, title); print(name, round(tl["total"], 1), "s")
    if "preview" in sys.argv:
        sh = Image.new("RGB", (240 * 8, 427 * 4))
        for i in range(32): sh.paste(frame(tl["total"] * (i + .5) / 32).resize((240, 427)), ((i % 8) * 240, (i // 8) * 427))
        sh.save(os.path.join(OUT, f"preview_{name}.jpg"), quality=88); return
    wav = os.path.join(OUT, f"tmp_{name}", "mix.wav"); sound(tl, voices, wav, music, fxs)
    p = subprocess.Popen([FF, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium",
                          "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", os.path.join(OUT, f"sample_{name}.mp4")], stdin=subprocess.PIPE)
    with Pool(min(8, os.cpu_count()), initializer=init, initargs=(tl, shots, title)) as pool:
        for b in pool.imap(raw, range(int(tl["total"] * FPS)), chunksize=6): p.stdin.write(b)
    p.stdin.close(); sys.exit(p.wait())
