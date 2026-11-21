"""
Premium 2.5D cut-out version of the Krishna-Arjun series.
Characters are built from shaded sprite layers (rendered once, cached on disk),
then animated per frame.  Script, voices, music and captions come from make_story.py.

    python premium_story.py preview 1
    python premium_story.py 1
"""
import os, sys, math, random, json, hashlib, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from multiprocessing import Pool
from . import story_base as ms

HERE = ms.HERE; BUILD = ms.BUILD
W, H, FPS, SS = 1080, 1920, 30, 2
SPR = os.path.join(os.environ.get("LOCALAPPDATA", BUILD), "reel_sprites"); os.makedirs(SPR, exist_ok=True)
GY = 1500
LIGHT = (-0.55, -0.83); RIM = (0.92, -0.38); RIM_COL = (255, 214, 150)
clamp, lerp, ease_io, ease_out = ms.clamp, ms.lerp, ms.ease_io, ms.ease_out
def pulse(t, t0, d): return max(0.0, 1 - (t - t0) / d) if t >= t0 else 0.0

# ================================================================ shading canvas
def blur(a, r):
    if r < 0.5: return a
    im = Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8), "L").filter(ImageFilter.GaussianBlur(r))
    return np.asarray(im, np.float32) / 255
def shift(a, dy, dx): return np.roll(a, (int(round(dy)), int(round(dx))), axis=(0, 1))

class SC:
    """float RGBA canvas; coordinates in 'units', s = pixels per unit"""
    def __init__(self, bbox, s):
        self.ox, self.oy = bbox[0], bbox[1]; self.s = s
        self.w, self.h = max(2, int((bbox[2] - bbox[0]) * s)), max(2, int((bbox[3] - bbox[1]) * s))
        self.rgb = np.zeros((self.h, self.w, 3), np.float32); self.a = np.zeros((self.h, self.w), np.float32)
    def P(self, x, y): return ((x - self.ox) * self.s, (y - self.oy) * self.s)
    def mask(self, fn):
        m = Image.new("L", (self.w, self.h), 0); fn(ImageDraw.Draw(m)); return m
    def part(self, m, base=None, sh=0.42, hl=0.28, rim=0.55, cast=0.28, grad=None, gloss=0.0, alpha=1.0):
        bb = m.getbbox()
        if not bb: return
        size = max(bb[2] - bb[0], bb[3] - bb[1]); d = clamp(size * 0.2, 3, 70)
        pad = int(d * 2.2 + 10)
        x0, y0, x1, y1 = max(0, bb[0] - pad), max(0, bb[1] - pad), min(self.w, bb[2] + pad), min(self.h, bb[3] + pad)
        mm = np.asarray(m.crop((x0, y0, x1, y1)), np.float32) / 255
        lx, ly = LIGHT; rgb = self.rgb[y0:y1, x0:x1]; al = self.a[y0:y1, x0:x1]
        if cast > 0:
            cd = d * 0.55; s_ = blur(shift(mm, -ly*cd, -lx*cd), cd * 0.6); rgb *= (1 - cast * s_ * al)[..., None]
        dark = mm * (1 - blur(shift(mm, ly*d, lx*d), d * 0.7))
        hi = mm * (1 - blur(shift(mm, -ly*d, -lx*d), d * 0.7))
        rd = max(2, d * 0.32); rimt = mm * (1 - blur(shift(mm, -RIM[1]*rd, -RIM[0]*rd), rd * 0.6))
        if grad:
            gy = np.clip((np.arange(y0, y1) - bb[1]) / max(1, bb[3] - bb[1]), 0, 1)[:, None, None]
            col = np.array(grad[0], np.float32) * (1 - gy) + np.array(grad[1], np.float32) * gy
            col = np.broadcast_to(col, (y1 - y0, x1 - x0, 3)).copy()
        else:
            col = np.ones((y1 - y0, x1 - x0, 3), np.float32) * np.array(base, np.float32)
        col = col * (1 - sh * dark[..., None]); col = col + (255 - col) * hl * hi[..., None]
        col = col + np.array(RIM_COL, np.float32) * rim * rimt[..., None]
        if gloss: col = col + 255 * gloss * (blur(hi, d * 0.3) ** 2)[..., None]
        a = mm * alpha; col = np.clip(col, 0, 255)
        rgb[:] = rgb * (1 - a[..., None]) + col * a[..., None]; al[:] = al + a * (1 - al)
    def flat(self, m, col, alpha=1.0): self.part(m, col, sh=0, hl=0, rim=0, cast=0, alpha=alpha)
    def soft(self, m, col, alpha, r_units):
        mm = blur(np.asarray(m, np.float32) / 255, r_units * self.s) * alpha
        self.rgb[:] = self.rgb * (1 - mm[..., None]) + np.array(col, np.float32) * mm[..., None]
        self.a[:] = self.a + mm * (1 - self.a)
    def image(self):
        return Image.fromarray(np.dstack([np.clip(self.rgb, 0, 255), np.clip(self.a * 255, 0, 255)]).astype(np.uint8), "RGBA")

# shape helpers: all take (cv, d) and unit coordinates
def E(cv, d, cx, cy, rx, ry=None):
    ry = rx if ry is None else ry; d.ellipse([*cv.P(cx - rx, cy - ry), *cv.P(cx + rx, cy + ry)], fill=255)
def POLY(cv, d, pts): d.polygon([cv.P(x, y) for x, y in pts], fill=255)
def LINE(cv, d, pts, w, caps=True):
    d.line([cv.P(x, y) for x, y in pts], fill=255, width=max(1, int(w * cv.s)), joint="curve")
    if caps:
        for x, y in (pts[0], pts[-1]): E(cv, d, x, y, w / 2)
def ARC(cv, d, cx, cy, rx, ry, a0, a1, w):
    d.arc([*cv.P(cx - rx, cy - ry), *cv.P(cx + rx, cy + ry)], a0, a1, fill=255, width=max(1, int(w * cv.s)))
def CHORD(cv, d, cx, cy, rx, ry, a0, a1):
    d.chord([*cv.P(cx - rx, cy - ry), *cv.P(cx + rx, cy + ry)], a0, a1, fill=255)
cubic = ms.cubic
def ribbon(path, w0, w1):
    L, R = [], []
    for i, (x, y) in enumerate(path):
        j, k = min(i + 1, len(path) - 1), max(i - 1, 0)
        dx, dy = path[j][0] - path[k][0], path[j][1] - path[k][1]; n = math.hypot(dx, dy) or 1
        nx, ny = -dy / n, dx / n; w = lerp(w0, w1, i / (len(path) - 1)) / 2
        L.append((x + nx*w, y + ny*w)); R.append((x - nx*w, y - ny*w))
    return L + R[::-1]

# ================================================================ sprite cache
MEM = {}
def sprite(key, bbox, s, fn):
    k = hashlib.md5(repr(key).encode()).hexdigest()
    if k in MEM: return MEM[k]
    path = os.path.join(SPR, k + ".png"); meta = os.path.join(SPR, k + ".json")
    if os.path.exists(meta) and os.path.exists(path):
        try:
            img = Image.open(path); img.load(); ox, oy = json.load(open(meta)); MEM[k] = (img, ox, oy); return MEM[k]
        except Exception: pass
    cv = SC(bbox, s); fn(cv); img = cv.image(); bb = img.getbbox()
    if not bb: img, bb = Image.new("RGBA", (1, 1)), (0, 0, 1, 1)
    else: img = img.crop(bb)
    ox, oy = -bbox[0] * s - bb[0], -bbox[1] * s - bb[1]
    pid = os.getpid()
    try:
        img.save(path + f".{pid}.png", compress_level=1); os.replace(path + f".{pid}.png", path)
        with open(meta + f".{pid}", "w") as f: json.dump([ox, oy], f)
        os.replace(meta + f".{pid}", meta)
    except OSError:
        for tmp in (path + f".{pid}.png", meta + f".{pid}"):
            try: os.remove(tmp)
            except OSError: pass
    MEM[k] = (img, ox, oy); return MEM[k]

def put(frame, spr, X, Y):
    img, ox, oy = spr
    frame.paste(img, (int(round(X * SS - ox)), int(round(Y * SS - oy))), img)

# ================================================================ characters
GOLD = (242, 188, 64); RED = (210, 40, 60)
C = {
    "K": dict(skin=(88, 136, 222), skin_d=(55, 92, 175), hair=(28, 22, 44), dhoti=(252, 196, 40), pleat=(255, 214, 80), border=RED),
    "A": dict(skin=(238, 192, 152), skin_d=(190, 140, 106), hair=(34, 24, 22), dhoti=(246, 240, 226), pleat=(255, 251, 242), border=(196, 52, 58), top=(150, 36, 50)),
    "P": dict(skin=(186, 136, 98), skin_d=(140, 98, 68), hair=(108, 104, 104), dhoti=(128, 104, 82), pleat=(142, 118, 94), border=(98, 78, 60), top=(196, 186, 160)),
}

def L_back(cv, who, uy):
    c = C[who]; m = cv.mask
    if who == "K":
        cv.soft(m(lambda d: E(cv, d, 0, -440 + uy, 210)), (255, 230, 160), 0.6, 40)
        path = cubic((40, -320 + uy), (150, -330 + uy), (140, -190 + uy), (200, -140 + uy), 30)
        cv.part(m(lambda d: POLY(cv, d, ribbon(path, 28, 52))), (248, 140, 60), sh=0.5, rim=0.7)
    if who in ("K", "A"):
        bot = -280 if who == "K" else -318
        cv.part(m(lambda d: POLY(cv, d, [(-80, -440 + uy), (80, -440 + uy), (98, -360 + uy), (96, bot - 12 + uy), (70, bot + uy), (-70, bot + uy), (-96, bot - 12 + uy), (-98, -360 + uy)])), c["hair"], sh=0.3, hl=0.15, rim=0.5)
    if who == "A":
        cv.part(m(lambda d: POLY(cv, d, ribbon([(-36, -300 + uy), (-100, -440 + uy)], 34, 40))), (120, 76, 40), sh=0.45, rim=0.6)
        for k in range(3):
            x0 = -84 - k*12 + 6
            cv.part(m(lambda d, x0=x0: LINE(cv, d, [(x0 + 10, -420 + uy), (x0, -478 + uy)], 4)), (170, 130, 80), sh=0.2, cast=0)
            cv.part(m(lambda d, x0=x0: POLY(cv, d, [(x0 - 8, -470 + uy), (x0 + 8, -470 + uy), (x0, -500 + uy)])), (225, 60, 60), sh=0.3, cast=0)
        bow = cubic((100, -392 + uy), (196, -320 + uy), (160, -170 + uy), (66, -116 + uy), 30)
        cv.part(m(lambda d: POLY(cv, d, ribbon(bow, 14, 14))), (130, 78, 36), sh=0.45, hl=0.35, gloss=0.2, rim=0.7)
        cv.flat(m(lambda d: LINE(cv, d, [(100, -392 + uy), (66, -116 + uy)], 2, caps=False)), (240, 230, 205))
        for pt in ((100, -392), (66, -116)): cv.part(m(lambda d, pt=pt: E(cv, d, pt[0], pt[1] + uy, 9)), GOLD, gloss=0.6)

def L_lower(cv, who, ph, sit):
    c = C[who]; m = cv.mask
    if sit:
        cv.part(m(lambda d: E(cv, d, 0, -42, 114, 42)), c["dhoti"], sh=0.45, hl=0.25)
        for s in (-1, 1): cv.part(m(lambda d, s=s: E(cv, d, s*74, -20, 30, 13)), c["skin"], sh=0.35)
        return
    sw = math.sin(ph) * 16 if ph is not None else 0
    sway = math.sin(ph) * 6 if ph is not None else 0
    for s, s_ in ((-1, sw), (1, -sw)):
        cv.part(m(lambda d, s=s, s_=s_: LINE(cv, d, [(s*24, -170), (s*27 + s_, -24)], 30)), c["skin"], sh=0.45)
        cv.part(m(lambda d, s=s, s_=s_: E(cv, d, s*31 + s_, -12, 30, 13)), c["skin"], sh=0.35)
        if who == "K": cv.part(m(lambda d, s=s, s_=s_: E(cv, d, s*27 + s_, -34, 17, 6)), GOLD, sh=0.3, hl=0.5, gloss=0.5, rim=0.8)
    hem = [(-66, -206), (66, -206), (80, -130), (90 + sway, -64), (60 + sway, -52), (30 + sway, -58), (0 + sway, -54), (-30 + sway, -58), (-60 + sway, -52), (-90 + sway, -64), (-80, -130)]
    cv.part(m(lambda d: POLY(cv, d, hem)), c["dhoti"], sh=0.45, hl=0.3)
    cv.part(m(lambda d: POLY(cv, d, [(-16, -200), (16, -200), (24 + sway, -58), (-24 + sway, -58)])), c["pleat"], sh=0.35, cast=0.2)
    for x0 in (-40, 40): cv.flat(m(lambda d, x0=x0: LINE(cv, d, [(x0*0.6, -190), (x0 + sway, -70)], 3)), ms.darker(c["dhoti"], 0.8), alpha=0.7)
    band = [(-90 + sway, -64), (-60 + sway, -52), (0 + sway, -56), (60 + sway, -52), (90 + sway, -64), (88 + sway, -80), (0 + sway, -74), (-88 + sway, -80)]
    cv.part(m(lambda d: POLY(cv, d, band)), c["border"], sh=0.3, hl=0.3)
    if who != "P":
        cv.part(m(lambda d: POLY(cv, d, [(-88 + sway, -78), (0 + sway, -72), (88 + sway, -78), (87 + sway, -85), (0 + sway, -79), (-87 + sway, -85)])), GOLD, sh=0, hl=0.3, gloss=0.4, cast=0)

def L_upper(cv, who, uy):
    c = C[who]; m = cv.mask; Y = lambda pts: [(x, y + uy) for x, y in pts]
    top = c.get("top", c["skin"])
    if who == "P":
        cv.part(m(lambda d: (POLY(cv, d, Y([(-62, -334), (62, -334), (68, -150), (44, -162), (22, -146), (0, -160), (-22, -146), (-44, -162), (-68, -150)])),
                             E(cv, d, -58, -320 + uy, 27), E(cv, d, 58, -320 + uy, 27))), top, sh=0.45, hl=0.25)
        cv.part(m(lambda d: E(cv, d, -28, -262 + uy, 16, 12)), (160, 140, 110), sh=0.35, cast=0.2)
        cv.part(m(lambda d: E(cv, d, 30, -196 + uy, 13, 10)), (176, 160, 128), sh=0.35, cast=0.2)
        cv.part(m(lambda d: LINE(cv, d, Y([(-62, -218), (0, -212), (62, -218)]), 7)), (120, 92, 60), sh=0.3)
        cv.flat(m(lambda d: LINE(cv, d, Y([(18, -300), (26, -280), (18, -266)]), 2.5)), (140, 130, 110))
    else:
        cv.part(m(lambda d: (POLY(cv, d, Y([(-62, -334), (62, -334), (56, -200), (-56, -200)])), E(cv, d, -58, -320 + uy, 26), E(cv, d, 58, -320 + uy, 26))),
                top, sh=0.5, hl=0.3)
    cv.soft(m(lambda d: E(cv, d, 0, -336 + uy, 36, 12)), (20, 20, 40), 0.35, 4)
    if who == "K":
        cv.part(m(lambda d: POLY(cv, d, Y([(-60, -222), (60, -222), (62, -198), (-62, -198)]))), GOLD, sh=0.35, hl=0.4, gloss=0.5)
        for i, x in enumerate((-36, 0, 36)):
            cv.part(m(lambda d, x=x: E(cv, d, x, -210 + uy, 7, 8)), (RED, (40, 170, 110), RED)[i], sh=0.3, gloss=0.8, cast=0.15)
        cv.part(m(lambda d: POLY(cv, d, Y([(-64, -326), (-38, -336), (60, -214), (36, -204)]))), (236, 70, 110), sh=0.45, hl=0.3)
        cv.part(m(lambda d: LINE(cv, d, Y([(-54, -238), (52, -162)]), 14)), (196, 136, 64), sh=0.45, hl=0.4, gloss=0.3, cast=0.4)
        for u in (0.1, 0.9):
            cv.part(m(lambda d, u=u: E(cv, d, lerp(-54, 52, u), lerp(-238, -162, u) + uy, 8, 8)), GOLD, gloss=0.6, cast=0)
        for r_, col in ((26, GOLD), (40, (255, 240, 205))):
            for i in range(13):
                u = i / 12
                cv.part(m(lambda d, u=u, r_=r_: E(cv, d, lerp(-38, 38, u), -330 + r_*math.sin(math.pi*u) + uy, 5)), col, sh=0.35, hl=0.4, gloss=0.6, cast=0.15)
        fl = [(255, 248, 245), (240, 60, 100), (255, 196, 50)]
        for i in range(23):
            u = i / 22
            cv.part(m(lambda d, u=u: E(cv, d, lerp(-50, 50, u), -330 + 175*math.sin(math.pi*u) + uy, 9)), fl[i % 3], sh=0.4, hl=0.3, cast=0.25)
    if who == "A":
        cv.part(m(lambda d: LINE(cv, d, Y([(-42, -332), (0, -300), (42, -332)]), 7)), GOLD, sh=0.3, hl=0.4, gloss=0.5)
        cv.part(m(lambda d: E(cv, d, 0, -266 + uy, 20)), GOLD, sh=0.4, hl=0.4, gloss=0.6)
        cv.part(m(lambda d: E(cv, d, 0, -266 + uy, 9)), RED, gloss=0.9, cast=0.2)
        cv.part(m(lambda d: POLY(cv, d, Y([(-60, -224), (60, -224), (62, -198), (-62, -198)]))), GOLD, sh=0.35, hl=0.4, gloss=0.5)
        cv.part(m(lambda d: E(cv, d, 0, -211 + uy, 9)), RED, gloss=0.9, cast=0.1)
        for i in range(5):
            x = -48 + i * 24
            cv.part(m(lambda d, x=x: POLY(cv, d, Y([(x - 10, -198), (x + 10, -198), (x + 8, -168), (x - 8, -168)]))), (GOLD if i % 2 else (150, 36, 50)), sh=0.35, cast=0.3)
        for i in range(11):
            u = i / 10
            cv.part(m(lambda d, u=u: E(cv, d, lerp(-30, 30, u), -330 + 18*math.sin(math.pi*u) + uy, 4.5)), GOLD, gloss=0.6, cast=0.1)

ARM_POSES = {}
def arm_geom(pose, g, ph):
    swing = math.sin(ph) * 14 if ph is not None else 0
    L = [(-58, -318), (-82, -250), (-76 + swing, -180)]; R = [(58, -318), (82, -250), (76 - swing, -180)]
    if pose == "talk": L = [(-58, -318), (-98, -254), (-50 + g*0.4, -284 + g)]
    elif pose == "bless": L = [(-58, -318), (-112, -284), (-102 + g*0.3, -372 + g*0.4)]
    elif pose == "namaste": L = [(-58, -318), (-80, -246), (-9, -286)]; R = [(58, -318), (80, -246), (9, -286)]
    elif pose == "wipe": L = [(-58, -318), (-92, -272), (-34, -398)]
    elif pose == "victory": L = [(-58, -318), (-104, -404), (-92, -500)]; R = [(58, -318), (104, -404), (92, -500)]
    return L, R

def L_arms(cv, who, uy, pose, g, ph):
    c = C[who]; m = cv.mask; sk = c["skin"]
    L, R = arm_geom(pose, g, ph)
    Y = lambda pts: [(x, y + uy) for x, y in pts]
    for arm in (R, L):
        a = Y(arm)
        if who == "P":
            cv.part(m(lambda d, a=a: LINE(cv, d, a[:2], 31)), c["top"], sh=0.45, cast=0.3)
            cv.part(m(lambda d, a=a: LINE(cv, d, a[1:], 24)), sk, sh=0.45, cast=0.3)
        else:
            cv.part(m(lambda d, a=a: LINE(cv, d, a, 26)), sk, sh=0.45, cast=0.35)
            mid = ((a[0][0] + a[1][0]) / 2, (a[0][1] + a[1][1]) / 2)
            cv.part(m(lambda d, mid=mid: E(cv, d, mid[0], mid[1], 16, 9)), GOLD, sh=0.3, hl=0.4, gloss=0.6)
            if who == "A":
                fa = (lerp(a[1][0], a[2][0], 0.35), lerp(a[1][1], a[2][1], 0.35)), (lerp(a[1][0], a[2][0], 0.85), lerp(a[1][1], a[2][1], 0.85))
                cv.part(m(lambda d, fa=fa: LINE(cv, d, list(fa), 30)), (120, 72, 40), sh=0.45, hl=0.3, cast=0.2)
            else:
                b = (lerp(a[1][0], a[2][0], 0.85), lerp(a[1][1], a[2][1], 0.85))
                cv.part(m(lambda d, b=b: E(cv, d, b[0], b[1], 15, 8)), GOLD, gloss=0.6, cast=0.2)
        hx, hy = a[2]
        if pose == "bless" and arm is L:
            cv.part(m(lambda d: (E(cv, d, hx, hy - 8, 19, 24), [E(cv, d, hx - 12 + f*8, hy - 30, 5, 9) for f in range(4)])), sk, sh=0.35, hl=0.3, cast=0.3)
            if who == "K": cv.flat(m(lambda d: E(cv, d, hx, hy - 6, 4)), (225, 40, 60))
        else:
            cv.part(m(lambda d, hx=hx, hy=hy: E(cv, d, hx, hy, 16, 15)), sk, sh=0.4, hl=0.3, cast=0.3)
    if pose == "namaste":
        cv.part(m(lambda d: POLY(cv, d, Y([(-17, -266), (17, -266), (0, -330)]))), sk, sh=0.4, hl=0.3, cast=0.3)

def L_head(cv, who, uy):
    c = C[who]; m = cv.mask; sk, skd = c["skin"], c["skin_d"]; hy = -410 + uy
    cv.part(m(lambda d: POLY(cv, d, [(-18, hy + 50), (18, hy + 50), (18, hy + 84), (-18, hy + 84)])), skd, sh=0.3, hl=0.1, rim=0.3)
    for s in (-1, 1): cv.part(m(lambda d, s=s: E(cv, d, s*80, hy + 6, 16, 21)), sk, sh=0.45)
    cv.part(m(lambda d: E(cv, d, 0, hy, 82, 86)), sk, sh=0.42, hl=0.32, rim=0.65, cast=0.3)
    for s in (-1, 1):
        if who == "K":
            cv.part(m(lambda d, s=s: E(cv, d, s*82, hy + 42, 10, 17)), GOLD, sh=0.3, hl=0.5, gloss=0.7, cast=0.3)
            cv.part(m(lambda d, s=s: E(cv, d, s*82, hy + 60, 6)), RED, gloss=0.8, cast=0)
        elif who == "A":
            cv.part(m(lambda d, s=s: E(cv, d, s*82, hy + 30, 8)), GOLD, gloss=0.7, cast=0.2)
        if who != "P":
            cv.soft(m(lambda d, s=s: E(cv, d, s*50, hy + 36, 15, 9)), (255, 120, 160), 0.33, 5)
    cv.flat(m(lambda d: ARC(cv, d, 0, hy + 34, 6, 5, 20, 160, 3)), skd, alpha=0.8)
    if who == "P":
        cv.soft(m(lambda d: CHORD(cv, d, 0, hy + 4, 78, 80, 20, 160)), (70, 60, 55), 0.35, 3)
        for k in range(2): cv.flat(m(lambda d, k=k: ARC(cv, d, 0, hy - 40 + k*10, 30, 8, 200, 340, 2)), skd, alpha=0.6)
        def hp(d):
            CHORD(cv, d, 0, hy, 86, 88, 205, 335)
            for dx, dy, r in ((-60, -50, 24), (-30, -72, 26), (0, -80, 26), (30, -74, 24), (60, -54, 22), (-78, -20, 16), (78, -22, 16)):
                E(cv, d, dx, hy + dy, r)
        cv.part(m(hp), c["hair"], sh=0.35, hl=0.25, rim=0.6, cast=0.4)
        return
    def hair_front(d):
        CHORD(cv, d, 0, hy - 5, 86, 85, 200, 340)
        n = 9 if who == "K" else 7
        for i in range(n):
            x = lerp(-72, 72, i / (n - 1)); E(cv, d, x, hy - 42 + 14 * (x / 72) ** 2, 17 if who == "K" else 20, 15)
        if who == "K":
            for s in (-1, 1):
                for j in range(6): E(cv, d, s*(78 + j*2.4), hy - 20 + j*24, 18 - j*0.8, 16)
        else:
            for s in (-1, 1): POLY(cv, d, [(s*70, hy - 40), (s*92, hy - 10), (s*96, hy + 70), (s*78, hy + 40)])
    cv.part(m(hair_front), c["hair"], sh=0.35, hl=0.22, rim=0.7, cast=0.4)
    if who == "K":
        cv.flat(m(lambda d: LINE(cv, d, [(-9, hy - 42), (-7, hy - 20), (0, hy - 15), (7, hy - 20), (9, hy - 42)], 3.5)), (255, 242, 200))
        cv.flat(m(lambda d: LINE(cv, d, [(0, hy - 40), (0, hy - 22)], 3.5)), (225, 30, 50))
        a = math.radians(12); ux, uy_ = math.sin(a), -math.cos(a)
        bx, by = 10, hy - 118; L = 230
        vp = [(bx + ux*L*u, by + uy_*L*u) for u in np.linspace(0.18, 1.0, 30)]
        Lp, Rp = [], []
        for i, (x, y) in enumerate(vp):
            w_ = 46 * math.sin(math.pi * i / 29) ** 0.6; Lp.append((x - uy_*w_, y + ux*w_)); Rp.append((x + uy_*w_, y - ux*w_))
        cv.part(m(lambda d: POLY(cv, d, Lp + Rp[::-1])), grad=((60, 200, 150), (20, 110, 70)), sh=0.35, hl=0.35, rim=0.8, cast=0.25)
        def barbs(d):
            for j in range(40):
                u = 0.22 + 0.76 * j / 39; w_ = 46 * math.sin(math.pi * (u - 0.18) / 0.82) ** 0.6
                cx_, cy_ = bx + ux*L*u, by + uy_*L*u
                for sg in (-1, 1):
                    d.line([cv.P(cx_, cy_), cv.P(cx_ - uy_*w_*sg + ux*w_*0.4, cy_ + ux*w_*sg + uy_*w_*0.4)], fill=255, width=max(1, int(1.2*cv.s)))
        cv.flat(m(barbs), (190, 240, 170), alpha=0.45)
        cv.flat(m(lambda d: LINE(cv, d, [(bx, by), (bx + ux*L, by + uy_*L)], 2.5)), (235, 225, 175))
        ex_, ey_ = bx + ux*L*0.78, by + uy_*L*0.78
        for r_, col, g_ in ((30, (236, 190, 60), 0.4), (23, (24, 160, 160), 0.3), (16, (30, 70, 190), 0.7), (8, (12, 20, 66), 0.2)):
            cv.part(m(lambda d, r_=r_: E(cv, d, ex_, ey_, r_, r_*1.2)), col, sh=0.3, hl=0.3, gloss=g_, rim=0.4, cast=0.1)
        for s in (-1, 1):
            cv.part(m(lambda d, s=s: POLY(cv, d, cubic((s*40, hy - 60), (s*58, hy - 110), (s*84, hy - 104), (s*80, hy - 60), 16))), GOLD, sh=0.4, hl=0.4, gloss=0.4, rim=0.8)
        cv.part(m(lambda d: POLY(cv, d, cubic((-46, hy - 60), (-48, hy - 118), (48, hy - 118), (46, hy - 60), 24))), GOLD, sh=0.45, hl=0.45, gloss=0.5, rim=0.8)
        cv.part(m(lambda d: POLY(cv, d, cubic((-26, hy - 68), (-28, hy - 102), (28, hy - 102), (26, hy - 68), 20))), (255, 214, 110), sh=0.3, hl=0.4, gloss=0.4, cast=0.2)
        cv.part(m(lambda d: E(cv, d, 0, hy - 122, 9)), GOLD, gloss=0.7, cast=0.1)
        cv.part(m(lambda d: POLY(cv, d, [(-76, hy - 66), (76, hy - 66), (72, hy - 38), (-72, hy - 38)])), (250, 200, 80), sh=0.4, hl=0.45, gloss=0.6, rim=0.8)
        cv.part(m(lambda d: E(cv, d, 0, hy - 86, 11, 14)), RED, sh=0.35, hl=0.4, gloss=1.0)
        for x in (-46, -23, 23, 46):
            cv.part(m(lambda d, x=x: E(cv, d, x, hy - 52, 6)), (40, 175, 110) if abs(x) > 30 else (60, 120, 230), gloss=0.9, cast=0.1)
        for i in range(11):
            cv.part(m(lambda d, i=i: E(cv, d, lerp(-66, 66, i / 10), hy - 34 + 6*math.sin(i), 3.2)), (255, 250, 236), sh=0.2, gloss=0.6, cast=0.1)
    else:  # Arjun
        cv.flat(m(lambda d: LINE(cv, d, [(0, hy - 40), (0, hy - 18)], 5)), (215, 40, 45))
        for x, hh in ((-40, 34), (0, 52), (40, 34)):
            cv.part(m(lambda d, x=x, hh=hh: POLY(cv, d, cubic((x - 20, hy - 62), (x - 16, hy - 62 - hh), (x + 16, hy - 62 - hh), (x + 20, hy - 62), 14) + [(x, hy - 62 - hh - 14)])), GOLD, sh=0.45, hl=0.45, gloss=0.5, rim=0.8)
            cv.part(m(lambda d, x=x, hh=hh: E(cv, d, x, hy - 70 - hh*0.45, 7 if x else 10)), RED if not x else (40, 175, 110), gloss=0.9, cast=0.15)
        cv.part(m(lambda d: POLY(cv, d, [(-78, hy - 66), (78, hy - 66), (74, hy - 40), (-74, hy - 40)])), (245, 196, 72), sh=0.4, hl=0.45, gloss=0.6, rim=0.8)
        for i in range(9):
            cv.part(m(lambda d, i=i: E(cv, d, lerp(-60, 60, i / 8), hy - 53, 3.5)), RED if i % 2 else (255, 250, 236), gloss=0.6, cast=0.1)

def L_eyes(cv, who, uy, brow, bl, lx, ly, closed):
    m = cv.mask; ey = -400 + uy; ink = (25, 15, 25)
    brc = C[who]["hair"] if who == "P" else (30, 20, 35)
    for s in (-1, 1):
        ex = s * 32
        if closed:
            cv.flat(m(lambda d, ex=ex: ARC(cv, d, ex, ey + 8, 16, 12, 200, 340, 5)), ink)
        elif bl < 0.3:
            cv.flat(m(lambda d, ex=ex: ARC(cv, d, ex, ey - 2, 17, 10, 20, 160, 4.5)), ink)
        else:
            cv.part(m(lambda d, ex=ex: E(cv, d, ex, ey, 18, 22 * bl)), (252, 252, 255), sh=0.25, hl=0, rim=0, cast=0.2)
            ix, iy = ex + lx*6 + s, ey + 3 + ly*5
            cv.part(m(lambda d, ix=ix, iy=iy: E(cv, d, ix, iy, 13, 16 * bl)), grad=((25, 15, 20), (130, 80, 50)) if who != "A" else ((20, 15, 15), (110, 70, 45)), sh=0.15, hl=0, rim=0, cast=0)
            cv.flat(m(lambda d, ix=ix, iy=iy: E(cv, d, ix, iy + 1, 6, 7 * bl)), (10, 6, 8))
            cv.flat(m(lambda d, ix=ix, iy=iy: E(cv, d, ix - 4, iy - 7, 5, 5.5 * bl)), (255, 255, 255))
            cv.flat(m(lambda d, ix=ix, iy=iy: E(cv, d, ix + 5, iy + 5, 2.2)), (255, 255, 255), alpha=0.9)
            cv.flat(m(lambda d, ex=ex: ARC(cv, d, ex, ey - 1, 19, 22 * bl, 200, 340, 5)), ink)
            if who == "P":
                cv.part(m(lambda d, ex=ex: CHORD(cv, d, ex, ey, 19, 22 * bl, 190, 350)), C["P"]["skin"], sh=0.3, hl=0.1, rim=0, cast=0)
                cv.flat(m(lambda d, ex=ex: ARC(cv, d, ex, ey + 18, 16, 8, 20, 160, 2)), C["P"]["skin_d"], alpha=0.7)
            else:
                cv.flat(m(lambda d, ex=ex, s=s: LINE(cv, d, [(ex + s*16, ey - 14), (ex + s*26, ey - 22)], 3.5)), ink)
                if who == "K": cv.flat(m(lambda d, ex=ex, s=s: LINE(cv, d, [(ex + s*18, ey - 6), (ex + s*27, ey - 10)], 3)), ink)
        by = ey - 30
        if brow == "sad": cv.flat(m(lambda d, s=s: LINE(cv, d, [(s*48, by + 6), (s*16, by - 6)], 5)), brc)
        elif brow == "curious" and s == 1: cv.flat(m(lambda d: LINE(cv, d, [(16, by - 4), (48, by - 14)], 5)), brc)
        else: cv.flat(m(lambda d, ex=ex: ARC(cv, d, ex, by + 8, 18, 9, 205, 335, 4.5)), brc)

def L_mouth(cv, who, uy, mood, o):
    m = cv.mask; my = -362 + uy; ink = (60, 25, 30)
    if o > 0:
        cv.part(m(lambda d: E(cv, d, 0, my, 13 + 4*o, 4 + 13*o)), (110, 30, 42), sh=0.3, hl=0, rim=0, cast=0)
        if o > 0.4: cv.flat(m(lambda d: CHORD(cv, d, 0, my - 2, 12 + 3*o, 3 + 10*o, 200, 340)), (250, 250, 250))
        cv.flat(m(lambda d: E(cv, d, 0, my + 8*o, 8, 4.5*o)), (235, 110, 125))
    elif mood == "happy":
        cv.part(m(lambda d: CHORD(cv, d, 0, my - 10, 22, 18, 0, 180)), (110, 30, 42), sh=0.2, hl=0, rim=0, cast=0)
        cv.flat(m(lambda d: E(cv, d, 0, my + 3, 9, 4)), (235, 110, 125))
    elif mood == "sad": cv.flat(m(lambda d: ARC(cv, d, 0, my + 10, 15, 9, 205, 335, 4.5)), ink)
    elif mood == "neutral": cv.flat(m(lambda d: LINE(cv, d, [(-10, my), (10, my)], 4)), ink)
    else: cv.flat(m(lambda d: ARC(cv, d, 0, my - 9, 17, 11, 25, 155, 4.5)), ink)

BB = dict(back=(-280, -720, 330, 40), lower=(-140, -240, 140, 20), upper=(-150, -420, 150, 0), arms=(-210, -520, 230, 0),
          head=(-160, -800, 220, -180), eyes=(-75, -470, 75, -200), mouth=(-45, -400, 45, -200))

def blinkq(t, who):
    b = ms.blink(t + ms.BLINK_OFF[who])
    return 1.0 if b > 0.75 else (0.5 if b > 0.3 else 0.1)

def char(frame, pen, who, X, Y, sc, t, pose="stand", mood="smile", talk=0.0, look=(0, 0), walking=False, sit=False):
    s = sc * SS
    q = int(((t * 6.5) % (2*math.pi)) / (2*math.pi) * 8) % 8 if walking else None
    ph = q * 2*math.pi / 8 if walking else None
    bob = -abs(math.sin(ph)) * 7 if walking else 0
    sob = math.sin(t * 16) * 2.5 if (mood == "sad" and talk < 0.05) else 0
    dy = (bob + sob) * sc; uy = 118 if sit else 0
    put(frame, sprite(("back", who, uy, sc), BB["back"], s, lambda cv: L_back(cv, who, uy)), X, Y + dy)
    put(frame, sprite(("lower", who, q, sit, sc), BB["lower"], s, lambda cv: L_lower(cv, who, ph, sit)), X, Y)
    put(frame, sprite(("upper", who, uy, sc), BB["upper"], s, lambda cv: L_upper(cv, who, uy)), X, Y + dy)
    g = 0.0
    if pose in ("talk", "bless"): g = round(math.sin(t * 3.3) * min(1, talk * 4) * 2) / 2 * 10
    aq = q if (walking and pose == "stand") else None
    arms = lambda: put(frame, sprite(("arms", who, uy, sc, pose, g, aq), BB["arms"], s, lambda cv: L_arms(cv, who, uy, pose, g, ph if aq is not None else None)), X, Y + dy)
    if pose != "wipe": arms()
    put(frame, sprite(("head", who, uy, sc), BB["head"], s, lambda cv: L_head(cv, who, uy)), X, Y + dy)
    closed = mood == "happy" and talk < 0.05
    brow = mood if mood in ("sad", "curious") else "n"
    bl = blinkq(t, who); lx = round(look[0] * 2) / 2; ly = round(look[1] * 2) / 2
    put(frame, sprite(("eyes", who, uy, sc, brow, bl, lx, ly, closed), BB["eyes"], s, lambda cv: L_eyes(cv, who, uy, brow, bl, lx, ly, closed)), X, Y + dy)
    o = round(clamp(talk) * 4) / 4 if talk > 0.06 else 0
    put(frame, sprite(("mouth", who, uy, sc, mood if not o else "t", o), BB["mouth"], s, lambda cv: L_mouth(cv, who, uy, mood, o)), X, Y + dy)
    if pose == "wipe": arms()
    if mood == "sad":
        qq = (t % 1.3) / 1.3
        for sd in (-1, 1):
            pen.ell(X + sd*34*sc, Y + dy + (-400 + uy + 16 + qq*52)*sc, 5*sc, 7*sc, fill=(130, 195, 255, int(230*(1 - qq))))

def shadow(frame, X, Y, rx):
    spr = sprite(("shadow", int(rx)), (-rx*1.6, -rx*0.6, rx*1.6, rx*0.6), SS, lambda cv: cv.soft(cv.mask(lambda d: E(cv, d, 0, 0, rx, rx*0.17)), (30, 35, 20), 0.55, rx*0.12))
    put(frame, spr, X, Y)

# ================================================================ backgrounds
def gradient(stops, h, w):
    ys = np.linspace(0, 1, h); arr = np.zeros((h, 3), np.float32)
    for (a, ca), (b, cb) in zip(stops, stops[1:]):
        k = (ys >= a) & (ys <= b); f = ((ys[k] - a) / (b - a))[:, None]
        arr[k] = np.array(ca) * (1 - f) + np.array(cb) * f
    return np.repeat(arr[:, None, :], w, axis=1)

def tree_blob(cv, x, y, s, cols):
    m = cv.mask
    cv.part(m(lambda d: [E(cv, d, x + dx*s, y + dy*s, r*s) for dx, dy, r in ((0, 0, 120), (-95, 35, 95), (95, 35, 95), (-55, -75, 95), (60, -80, 90), (0, 70, 100))]), cols[1], sh=0.5, hl=0.35, rim=0.5, cast=0)
    cv.part(m(lambda d: [E(cv, d, x + dx*s, y + dy*s, r*s) for dx, dy, r in ((-50, -70, 50), (40, -60, 42), (-90, 10, 38))]), cols[2], sh=0.3, hl=0.4, rim=0.6, cast=0.2)

def screen(img, col, mask):
    b = np.asarray(img, np.float32); a = np.array(col, np.float32); mk = np.asarray(mask, np.float32)[..., None] / 255
    return Image.fromarray(np.clip(255 - (255 - b) * (255 - a * mk) / 255, 0, 255).astype(np.uint8), "RGB")

def god_rays(size, sx, sy, angs, val=60):
    lay = Image.new("L", size, 0); d = ImageDraw.Draw(lay)
    for k, a0 in enumerate(angs):
        a = math.radians(a0); da = math.radians(2.2); L = 2600 * SS
        d.polygon([(sx*SS, sy*SS), (sx*SS + math.cos(a - da)*L, sy*SS + math.sin(a - da)*L), (sx*SS + math.cos(a + da)*L, sy*SS + math.sin(a + da)*L)], fill=val)
    return lay.filter(ImageFilter.GaussianBlur(26 * SS))

def bg_forest(walk=False):
    cv = SC((0, 0, W, H), SS); m = cv.mask; rr = random.Random(4)
    cv.rgb[:] = gradient([(0, (92, 140, 205)), (0.3, (200, 190, 200)), (0.5, (255, 214, 168)), (0.62, (255, 222, 175)), (1, (255, 222, 175))], cv.h, cv.w); cv.a[:] = 1
    sun = (860, 560)
    cv.soft(m(lambda d: E(cv, d, *sun, 260)), (255, 236, 190), 0.55, 90)
    cv.soft(m(lambda d: E(cv, d, *sun, 80)), (255, 250, 230), 1.0, 12)
    hz = 1150 if walk else 1060
    hills = [(x, hz - 10 + 40*math.sin(x*0.006 + 1) + 16*math.sin(x*0.02)) for x in range(-20, 1110, 10)]
    cv.flat(m(lambda d: POLY(cv, d, hills + [(1110, 1500), (-20, 1500)])), (206, 170, 170))
    for x in range(-40, 1130, 46):
        r_ = rr.uniform(40, 70) * (0.6 if walk else 1); y_ = hz + 60 - rr.uniform(0, 40) - (40 if walk else 0)
        cv.flat(m(lambda d, x=x, r_=r_, y_=y_: E(cv, d, x, y_, r_)), (150, 150, 130))
    if not walk:
        for x, y, s in ((60, 880, 1.15), (290, 950, 0.85)):
            cv.part(m(lambda d, x=x, y=y, s=s: POLY(cv, d, [(x - 16*s, y), (x + 16*s, y), (x + 22*s, 1230), (x - 22*s, 1230)])), (96, 70, 52), sh=0.5, rim=0.6, cast=0)
            tree_blob(cv, x, y - 40*s, s, ((40, 90, 50), (72, 130, 64), (130, 175, 80)))
        cv.part(m(lambda d: POLY(cv, d, [(800, 1520), (1000, 1520), (950, 1150), (970, 760), (870, 720), (850, 1150)])), (112, 80, 56), sh=0.55, hl=0.25, rim=0.8)
        for x in range(640, 1080, 30):
            cv.flat(m(lambda d, x=x: d.line([cv.P(x, 760 + (x % 3)*20), cv.P(x + 5, 1160 + (x % 5)*40)], fill=255, width=int(4*SS))), (120, 90, 64), alpha=0.8)
        for x, y, s in ((880, 500, 1.6), (650, 640, 1.0), (1070, 600, 1.1), (760, 360, 1.0), (1000, 380, 1.0)):
            tree_blob(cv, x, y, s, ((42, 96, 52), (70, 138, 66), (140, 185, 84)))
    gtop = 1160 if walk else 1200
    cv.rgb[int(gtop*SS):] = gradient([(0, (170, 190, 100)), (1, (66, 110, 46))], cv.h - int(gtop*SS), cv.w)
    path = [(515, gtop), (565, gtop), (1050, H), (30, H)] if walk else [(470, gtop), (610, gtop), (1000, H), (90, H)]
    cv.flat(m(lambda d: POLY(cv, d, path)), (228, 196, 146), alpha=0.9)
    cv.soft(m(lambda d: POLY(cv, d, [(0, gtop - 10), (W, gtop - 10), (W, gtop + 90), (0, gtop + 90)])), (255, 225, 170), 0.35, 30)
    img = cv.image().convert("RGB").filter(ImageFilter.GaussianBlur(4 * SS))
    img = screen(img, (255, 230, 170), god_rays(img.size, *sun, [105 + k*9 + random.Random(k).uniform(-3, 3) for k in range(9)]))
    return img

def fg_grass(y0, y1, n, seed):
    cv = SC((0, 0, W, H), SS); m = cv.mask; rr = random.Random(seed)
    def blades(d):
        for _ in range(n):
            x = rr.uniform(-20, 1100); y = rr.uniform(y0, y1); h_ = rr.uniform(20, 60) * (0.6 + 0.6*(y - y0) / max(1, y1 - y0)); lean = rr.uniform(-12, 12)
            POLY(cv, d, [(x - 4, y), (x + lean, y - h_), (x + 4, y)])
    cv.part(m(blades), (96, 156, 62), sh=0.3, hl=0.35, rim=0.8, cast=0)
    for _ in range(7):
        x, y = rr.uniform(40, 1040), rr.uniform(y0 + 20, y1); c_ = rr.choice([(255, 120, 170), (255, 230, 90), (255, 255, 255)])
        cv.part(m(lambda d, x=x, y=y: [E(cv, d, x + math.cos(a)*10, y + math.sin(a)*10, 8) for a in np.linspace(0, 2*math.pi, 6)[:-1]]), c_, sh=0.3, rim=0.6)
        cv.part(m(lambda d, x=x, y=y: E(cv, d, x, y, 5)), (255, 200, 60), gloss=0.5)
    img = cv.image(); bb = img.getbbox(); return (img.crop(bb), -bb[0], -bb[1])

TREE_COLS = [((40, 90, 50), (66, 134, 66), (130, 180, 84)), ((36, 84, 54), (58, 124, 70), (118, 170, 90)), ((46, 98, 46), (80, 142, 60), (150, 190, 80))]
def tree_sprite(i):
    def fn(cv):
        m = cv.mask
        cv.part(m(lambda d: POLY(cv, d, [(-34, 0), (34, 0), (22, -330), (-22, -330)])), (105, 75, 50), sh=0.5, hl=0.25, rim=0.7)
        tree_blob(cv, 0, -420, 1.25, TREE_COLS[i])
    img, ox, oy = sprite(("tree", i), (-300, -640, 300, 10), 1.6 * SS, fn)
    return img, ox, oy

CACHE = {}
def asset(name, fn):
    if name not in CACHE: CACHE[name] = fn()
    return CACHE[name]

# ================================================================ shots (part 1 set)
TALK = {}
def talk(w): return TALK.get(w, 0.0)
_r = random.Random(9)
WALK_TREES = [((1 if i % 2 else -1) * _r.uniform(330, 640), i * 0.5, i % 3) for i in range(14)]
STONES = [(_r.uniform(-140, 140), _r.uniform(0, 1)) for _ in range(14)]
LEAVES = [(_r.uniform(380, 1100), _r.uniform(0, 900), _r.uniform(0, 6.28)) for _ in range(8)]
DUST = [(_r.uniform(0, W), _r.uniform(0, 1), _r.uniform(0.03, 0.08), _r.uniform(2, 5)) for _ in range(40)]

def dust(p, t, y0=250, y1=1700):
    for i, (x0, ph, sp, r) in enumerate(DUST):
        u = (ph + t*sp) % 1; y = y1 - u*(y1 - y0); x = x0 + 20*math.sin(t*0.7 + i)
        p.ell(x, y, r + 3, fill=(255, 236, 170, int(40*math.sin(math.pi*u))))
        p.ell(x, y, r*0.6, fill=(255, 245, 200, int(200*math.sin(math.pi*u))))

def shot_walk(t, s):
    img = asset("walk", lambda: bg_forest(walk=True)).copy(); p = ms.Pen(img)
    fog = np.array((235, 215, 190), np.float32); hz = 1160
    items = sorted([(((z0 - t*0.55) % 7.0) + 0.7, X, i) for X, z0, i in WALK_TREES], reverse=True)
    for z, X, i in items:
        k = 1 / z; spr, ox, oy = tree_sprite(i); f = clamp((z - 0.7) / 6) * 0.75
        sc = k / 1.6; w_, h_ = max(1, int(spr.width * sc)), max(1, int(spr.height * sc))
        im = spr.resize((w_, h_), Image.BILINEAR)
        if f > 0.05:
            a = np.asarray(im, np.float32); a[..., :3] = a[..., :3] * (1 - f) + fog * f; im = Image.fromarray(a.astype(np.uint8), "RGBA")
        sx, by = 540 + X*k, hz + 420*k
        img.paste(im, (int(sx*SS - ox*sc), int(by*SS - oy*sc)), im)
    for X, u0 in STONES:
        u = (u0 + t*0.13) % 1; z = lerp(7.5, 0.6, u); k = 1 / z
        p.ell(540 + X*k, hz + 420*k, 10*k, 5*k, fill=(185, 160, 120))
    if s.get("who") == "P":
        shadow(img, 540, 1690, 95)
        char(img, p, "P", 540, 1690, 1.5, t, mood=s.get("pmood", "neutral"), look=(0, 0.2), walking=True)
    else:
        for x in (380, 700): shadow(img, x, 1690, 95)
        char(img, p, "K", 380, 1690, 1.45, t, mood="smile", look=(0.5, 0), walking=True)
        char(img, p, "A", 700, 1690, 1.45, t + 0.25, mood="smile", look=(-0.5, 0), walking=True)
    dust(p, t)
    e = ease_io(t / s["dur"])
    return img, dict(zoom=lerp(1.0, 1.06, e), cx=540, cy=1000)

def shot_meet(t, s):
    img = asset("meet", lambda: bg_forest()).copy(); p = ms.Pen(img)
    for x0, y0, ph in LEAVES:
        y = (y0 + t*80) % 1000 + 520; x = x0 + 40*math.sin(t*1.3 + ph)
        p.ell(x, y, 10, 5, fill=(150, 200, 90, 220))
    kx = s.get("kx", 220); ax = 460; kwalk = False
    if "kwalk" in s:
        k0, k1 = s["kwalk"]; u = clamp((t - 0.3) / 2.8); kx = lerp(k0, k1, ease_io(u)); kwalk = 0 < u < 1
    if "kwalk" in s or "kx" in s: ax = 200
    arrive = s.get("arrive") and t < 2.6
    off = lerp(-440, 0, ease_out(t / 2.6)) if s.get("arrive") else 0
    pm = s.get("pmood", "sad"); pmood = {"listen": "neutral", "happy": "happy"}.get(pm, pm)
    pt = talk("P")
    ppose = "wipe" if (pmood == "sad" and pt < 0.05 and (t % 5) < 1.8) else "stand"
    plook = (-1, 0) if (talk("K") > 0 or talk("A") > 0 or pm == "listen") else (0, 0.5)
    shadow(img, 800, GY - 4, 130); shadow(img, ax + off, GY, 85); shadow(img, kx + off, GY, 85)
    char(img, p, "P", 800, GY, 1.3, t, pose=ppose, mood=pmood, talk=pt, look=plook, sit=True)
    ap = s.get("apose") or ("talk" if talk("A") > 0.05 else "stand")
    kp = s.get("kpose") or ("talk" if talk("K") > 0.05 else "stand")
    drawK = lambda: char(img, p, "K", kx + off, GY, 1.3, t, pose=kp, mood="smile", talk=talk("K"), look=(s.get("klook", 0.5), 0), walking=arrive or kwalk)
    drawA = lambda: char(img, p, "A", ax + off, GY, 1.3, t + 0.3, pose=ap, mood="curious" if pm == "sad" else "smile", talk=talk("A"), look=(s.get("alook", 0), 0), walking=arrive)
    if kx < ax: drawK(); drawA()
    else: drawA(); drawK()
    g, ox, oy = asset("meet_fg", lambda: fg_grass(1480, 1560, 160, 5)); img.paste(g, (int(ox), int(oy)), g)
    dust(p, t)
    nm = s.get("cam", "wide"); e = ease_io(t / s["dur"])
    z, cx, cy = dict(wide=(1.0, 540, 1000), a=(1.75, ax, GY - 470), k=(1.75, kx, GY - 470), p=(1.8, 800, GY - 380),
                     ka=(1.4, (kx + ax) / 2, GY - 440), kp=(1.45, (kx + 800) / 2, GY - 440))[nm]
    return img, dict(zoom=z * lerp(1.0, 1.06, e), cx=cx, cy=cy)

def shot_divine(t, s):
    img = asset("divine", ms.build_divine).copy(); p = ms.Pen(img); gl = s.get("glow", 1.0)
    for k in range(16):
        a = t*0.12 + k*math.pi/8; da = 0.06
        p.poly([(540, 1150), (540 + math.cos(a - da)*1600, 1150 + math.sin(a - da)*1600), (540 + math.cos(a + da)*1600, 1150 + math.sin(a + da)*1600)], fill=(255, 240, 200, int(22*gl)))
    for i, (x0, ph, sp) in enumerate(ms.SPARKS):
        u = (t*sp + ph) % 1; y = 1900 - u*1750; x = x0 + 25*math.sin(t + i)
        p.ell(x, y, 3.5 + (i % 3), fill=(255, 248, 210, int(220*math.sin(math.pi*u))))
    for i, (x0, ph, r0) in enumerate(ms.PETALS):
        u = (t*0.09 + ph) % 1; p.ell(x0 + 60*math.sin(t*0.8 + r0), -40 + u*2000, 13, 7, fill=(255, 140, 170, 210))
    char(img, p, "K", 540, 2100, 2.2, t, pose="bless", mood="smile", talk=talk("K"), look=(0, 0.2))
    e = ease_io(t / s["dur"])
    return img, dict(zoom=lerp(1.0, 1.07, e), cx=540, cy=1080)

def tinted(src, mul, add):
    a = np.asarray(src, np.float32); lum = a.mean(axis=2, keepdims=True)
    a = (a * 0.35 + lum * 0.65) * np.array(mul, np.float32) + np.array(add, np.float32)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB")

def bg_night():
    img = tinted(asset("meet", lambda: bg_forest()), (0.32, 0.4, 0.78), (6, 10, 30)); p = ms.Pen(img); rr = random.Random(2)
    for _ in range(140):
        x, y = rr.uniform(0, W), rr.uniform(0, 900); r = rr.uniform(1.2, 3.2)
        p.ell(x, y, r, fill=(255, 255, 235, int(rr.uniform(120, 255))))
    for k in range(6): p.ell(230, 430, 80 + k*36, fill=(190, 205, 255, 12))
    p.ell(230, 430, 70, fill=(248, 244, 220))
    return img

def bg_rain():
    return tinted(asset("meet", lambda: bg_forest()), (0.6, 0.66, 0.78), (18, 20, 28))

FIREFLY = [(_r.uniform(80, 1000), _r.uniform(1050, 1450), _r.uniform(0, 6.28)) for _ in range(12)]
RAIN = [(_r.uniform(-100, 1300), _r.uniform(0, 2000), _r.uniform(1900, 2600)) for _ in range(170)]

def sit_p(img, p, t, s, mood):
    shadow(img, 800, GY - 4, 130)
    char(img, p, "P", 800, GY, 1.3, t, mood=mood, talk=talk("P"), look=(0, 0.5) if mood == "sad" else (-0.3, 0), sit=True)

def shot_night(t, s):
    img = asset("night", bg_night).copy(); p = ms.Pen(img)
    for x0, y0, ph in FIREFLY:
        x = x0 + 30*math.sin(t*0.7 + ph); y = y0 + 20*math.sin(t*1.1 + ph*2); a = 0.5 + 0.5*math.sin(t*3 + ph)
        p.ell(x, y, 18, fill=(210, 255, 120, int(45*a))); p.ell(x, y, 4.5, fill=(240, 255, 170, int(255*a)))
    sit_p(img, p, t, s, s.get("pmood", "sad"))
    e = ease_io(t / s["dur"])
    return img, dict(zoom=lerp(1.25, 1.4, e), cx=720, cy=GY - 360)

def shot_rain(t, s):
    img = asset("rain", bg_rain).copy(); p = ms.Pen(img)
    sit_p(img, p, t, s, s.get("pmood", "sad"))
    for x0, y0, sp in RAIN:
        y = (y0 + t*sp) % 2100 - 150; x = x0 - (y + 150)*0.17
        p.line([(x, y), (x - 8, y + 44)], fill=(200, 215, 240, 150), w=3, caps=False)
    tl = s["dur"] * 0.4; fl = max(pulse(t, tl, 0.18), 0.7*pulse(t, tl + 0.25, 0.14))
    e = ease_io(t / s["dur"])
    return img, dict(zoom=lerp(1.2, 1.32, e), cx=720, cy=GY - 360, flash=fl*0.6)

def bg_sunrise():
    sky = Image.fromarray(gradient([(0, (40, 60, 130)), (0.35, (200, 120, 140)), (0.55, (255, 190, 130)), (1, (255, 205, 150))], H*SS, W*SS).astype(np.uint8), "RGB")
    cv = SC((0, 0, W, H), SS); m = cv.mask
    for base, amp, col, ph in ((1080, 60, (150, 110, 150), 0.3), (1160, 50, (110, 90, 130), 1.9), (1250, 40, (80, 120, 80), 3.1)):
        pts = [(x, base + amp*math.sin(x*0.006 + ph) + amp*0.4*math.sin(x*0.017)) for x in range(-20, 1110, 10)]
        cv.part(m(lambda d, pts=pts: POLY(cv, d, pts + [(1110, H), (-20, H)])), col, sh=0.35, hl=0.25, rim=0.9, cast=0)
    cv.rgb[int(1400*SS):] = gradient([(0, (110, 150, 80)), (1, (60, 100, 45))], cv.h - int(1400*SS), cv.w)
    cv.a[int(1400*SS):] = 1
    cv.flat(m(lambda d: POLY(cv, d, [(500, 1400), (580, 1400), (900, H), (180, H)])), (215, 180, 135), alpha=0.85)
    fg = cv.image().filter(ImageFilter.GaussianBlur(1.5*SS))
    return sky, fg

def shot_sunrise(t, s):
    sky, fg = asset("sunrise", bg_sunrise); img = sky.copy(); p = ms.Pen(img); e = ease_io(t / s["dur"])
    sy = lerp(1180, 930, e)
    for k in range(8): p.ell(540, sy, 140 + k*55, fill=(255, 220, 160, 16))
    for k in range(14):
        a = t*0.06 + k*math.pi/7; da = 0.05
        p.poly([(540, sy), (540 + math.cos(a - da)*1700, sy + math.sin(a - da)*1700), (540 + math.cos(a + da)*1700, sy + math.sin(a + da)*1700)], fill=(255, 235, 190, 26))
    p.ell(540, sy, 120, fill=(255, 225, 150)); p.ell(540, sy, 100, fill=(255, 242, 190))
    img.paste(fg, (0, 0), fg)
    shadow(img, 540, 1660, 95)
    mood = s.get("pmood", "happy")
    char(img, p, "P", 540, 1660, 1.5, t, pose="victory" if mood == "happy" and t > 1.2 else "stand", mood=mood, talk=talk("P"), look=(0, -0.3))
    dust(p, t, 600, 1600)
    return img, dict(zoom=lerp(1.12, 1.0, e), cx=540, cy=1080)

def bg_mountain():
    cv = SC((0, 0, W, H), SS); m = cv.mask
    cv.rgb[:] = gradient([(0, (60, 110, 200)), (0.45, (170, 190, 220)), (0.6, (255, 205, 160)), (1, (255, 215, 170))], cv.h, cv.w); cv.a[:] = 1
    cv.soft(m(lambda d: E(cv, d, 820, 700, 220)), (255, 236, 190), 0.6, 80)
    for pk, col in (([(-40, 1250), (180, 820), (330, 1000), (470, 760), (640, 1050), (820, 800), (1120, 1200)], (170, 160, 190)),
                    ([(-40, 1400), (120, 1100), (300, 1250), (920, 1050), (1120, 1300)], (120, 120, 150))):
        cv.part(m(lambda d, pk=pk: POLY(cv, d, pk + [(1120, H), (-40, H)])), col, sh=0.4, hl=0.35, rim=0.9, cast=0)
    for x, y, r in ((60, 1520, 160), (300, 1580, 140), (800, 1560, 170), (1040, 1520, 150)):
        cv.part(m(lambda d, x=x, y=y, r=r: [E(cv, d, x + dx*r, y + dy*r, rr*r) for dx, dy, rr in ((0, 0, 1), (-0.8, 0.2, 0.7), (0.8, 0.2, 0.7))]), (250, 245, 245), sh=0.25, hl=0.3, rim=0.6, cast=0)
    cv.part(m(lambda d: POLY(cv, d, [(330, H), (420, 1700), (470, 1640), (610, 1630), (660, 1690), (760, H)])), (105, 95, 100), sh=0.5, hl=0.35, rim=0.9)
    img = cv.image().convert("RGB")
    return screen(img, (255, 230, 170), god_rays(img.size, 820, 700, [110 + k*10 for k in range(8)], 50))

def shot_mountain(t, s):
    img = asset("mountain", bg_mountain).copy(); p = ms.Pen(img); e = ease_io(t / s["dur"])
    shadow(img, 540, 1640, 90)
    mood = s.get("pmood", "happy")
    char(img, p, "P", 540, 1640, 1.35, t, pose="victory" if mood == "happy" else "stand", mood=mood, talk=talk("P"), look=(0, -0.3))
    dust(p, t, 300, 1500)
    return img, dict(zoom=lerp(1.35, 1.0, e), cx=540, cy=lerp(1300, 1000, e))

SHOTS = dict(walk=shot_walk, meet=shot_meet, divine=shot_divine, night=shot_night, rain=shot_rain, sunrise=shot_sunrise, mountain=shot_mountain)

# ================================================================ frame
TL = None
def worker_init(tl):
    global TL; TL = tl

def post(fr):
    a = np.asarray(fr, np.float32)
    lum = a.mean(axis=2); hl = np.clip((lum - 200) / 55, 0, 1)
    bl = blur(hl, 24)
    a = 255 - (255 - a) * (1 - 0.32 * bl[..., None])
    a = 255 * (0.5 + (a / 255 - 0.5) * 1.07); a *= np.array([1.03, 1.0, 0.95], np.float32)
    if "vig" not in CACHE:
        yy, xx = np.mgrid[0:H, 0:W]; dd = np.sqrt(((xx - W/2) / (W*0.7))**2 + ((yy - H/2) / (H*0.7))**2)
        CACHE["vig"] = (1 - 0.35 * np.clip(dd - 0.55, 0, 1))[..., None].astype(np.float32)
    a *= CACHE["vig"]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB")

def render_shot(si, t):
    s = TL["shots"][si]; t = max(0.0, t)
    img, cam = SHOTS[s["kind"]](t, s)
    z = cam["zoom"]; vw, vh = W / z, H / z
    x0 = clamp(cam["cx"] - vw / 2, 0, W - vw); y0 = clamp(cam["cy"] - vh / 2, 0, H - vh)
    fr = img.resize((W, H), Image.BILINEAR, box=(x0*SS, y0*SS, (x0 + vw)*SS, (y0 + vh)*SS), reducing_gap=2.0)
    fr = post(fr)
    if cam.get("flash", 0) > 0.01: fr = Image.blend(fr, Image.new("RGB", (W, H), (235, 240, 255)), cam["flash"])
    return fr

def render_frame(fi):
    T = fi / FPS; shots = TL["shots"]
    TALK.clear()
    for ph in TL["phrases"]:
        if ph["start"] <= T < ph["end"]:
            i = int((T - ph["start"]) * FPS)
            if i < len(ph["env"]): TALK[ph["spk"]] = ph["env"][i]
    si = next((i for i, s in enumerate(shots) if T < s["end"]), len(shots) - 1); s = shots[si]
    frame = render_shot(si, T - s["start"])
    if si + 1 < len(shots) and T > s["end"] - ms.XF:
        frame = Image.blend(frame, render_shot(si + 1, T - shots[si + 1]["start"]), ease_io((T - (s["end"] - ms.XF)) / ms.XF))
    C_ = ms.CACHE
    last = shots[-1]; te = last["start"] + last["narr_end"] + 0.4
    # sticker card at the start of each shot (after the title card is gone)
    st = s.get("sticker"); ts = T - s["start"]
    if st and T > 2.7 and ts < 2.6:
        key = ("stk", si)
        if key not in C_: C_[key] = ms.make_sticker(st)
        a = max(0.0, ts - 0.15); cap_bottom = 0
        for k, ph in enumerate(TL["phrases"]):
            if ph["start"] - 0.05 <= T <= ph["end"] + 0.3:
                ck = ("cap", k)
                if ck not in C_: C_[ck] = ms.make_caption(ph["text"], ph["spk"], ph.get("tag"))
                cap_bottom = max(cap_bottom, 230 + C_[ck].height - 30)
        sy = max(690, cap_bottom + C_[key].height / 2 + 10)
        ms.overlay(frame, C_[key], W / 2 + (130 if si % 2 else -130), sy, lerp(0.4, 1.0, ms.ease_back(a / 0.3)), clamp(a / 0.08) * clamp((2.6 - ts) / 0.25))
    # "watch till the end" pill near the bottom
    if 2.8 < T < min(9.0, te - 0.5):
        if "pill" not in C_: C_["pill"] = ms.make_pill("Last tak zaroor dekhna")
        ms.overlay(frame, C_["pill"], W / 2, 1640, 1.0, clamp((T - 2.8) / 0.3) * clamp((min(9.0, te - 0.5) - T) / 0.3))
    # hook bar pinned to the top for the whole reel
    if TL.get("hook"):
        if "hook" not in C_: C_["hook"] = ms.make_hook(TL["hook"])
        ms.overlay(frame, C_["hook"], W / 2, 95, 1.0, clamp((T - 0.1) / 0.25))
    for k, ph in enumerate(TL["phrases"]):
        if ph["start"] - 0.05 <= T <= ph["end"] + 0.3:
            key = ("cap", k)
            if key not in C_: C_[key] = ms.make_caption(ph["text"], ph["spk"], ph.get("tag"))
            a = T - ph["start"] + 0.05
            ms.overlay(frame, C_[key], W / 2, 330 + C_[key].height / 2 - 100, lerp(0.6, 1.0, ms.ease_back(a / 0.25)), clamp(a / 0.1) * clamp((ph["end"] + 0.3 - T) / 0.2))
    if T < 2.6:
        if "title" not in C_: C_["title"] = ms.make_title(TL["label"], TL["title1"], TL["title2"], TL["title_sub"])
        ms.overlay(frame, C_["title"], W / 2, 860, lerp(0.7, 1.0, ms.ease_back((T - 0.1) / 0.4)), clamp((T - 0.1) / 0.2) * clamp((2.6 - T) / 0.35))
    if T >= te:
        if "end" not in C_: C_["end"] = ms.make_end(TL["end_text"], TL["end_sub"])
        a = T - te
        ms.overlay(frame, C_["end"], W / 2, 460, lerp(0.5, 1.0, ms.ease_back(a / 0.35)) * (1 + 0.025*math.sin(a*6)*clamp(a - 0.4)), clamp(a / 0.15))
    if T > TL["total"] - 0.4:
        frame = Image.blend(frame, Image.new("RGB", (W, H), (0, 0, 0)), clamp((T - (TL["total"] - 0.4)) / 0.4))
    return frame

def render_bytes(fi): return render_frame(fi).tobytes()

def render(tl, voices, out_mp4, workers=None, log=print):
    """Render a timeline to an mp4 (video + mixed audio)."""
    worker_init(tl)
    log("warming sprite cache...")
    for sh_ in tl["shots"]:
        for f in (0.05, 0.4, 0.8): render_frame(int((sh_["start"] + sh_["dur"]*f) * FPS))
    wav = out_mp4[:-4] + ".wav"; ms.build_audio(tl, voices, wav, seed=len(tl["phrases"]) * 7)
    nf = int(tl["total"] * FPS)
    cmd = [ms.ffmpeg_exe(), "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", wav,
           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out_mp4]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = workers or max(1, min(12, (os.cpu_count() or 2)))
    with Pool(n, initializer=worker_init, initargs=(tl,)) as pool:
        for i, b in enumerate(pool.imap(render_bytes, range(nf), chunksize=4)):
            proc.stdin.write(b)
            if i % 300 == 0: log(f"  frame {i}/{nf}")
    proc.stdin.close()
    if proc.wait() != 0: raise RuntimeError("ffmpeg failed")
    return out_mp4

def preview(tl, path):
    worker_init(tl); frames = []
    for sh_ in tl["shots"]:
        for f in (0.3, 0.8): frames.append(render_frame(int((sh_["start"] + sh_["dur"]*f) * FPS)).resize((270, 480)))
    cols = 6; rows = (len(frames) + cols - 1) // cols
    sheet = Image.new("RGB", (270*cols, 480*rows))
    for i, fr in enumerate(frames): sheet.paste(fr, ((i % cols)*270, (i // cols)*480))
    sheet.save(path, quality=85)
