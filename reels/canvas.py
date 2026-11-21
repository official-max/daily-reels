"""Shaded drawing canvas used for characters and painted backgrounds.

Shapes are drawn as masks; SC.part() turns a mask into a lit 2.5D shape (shadow side, highlight, rim light,
cast shadow, gloss). Character layers are rendered once and cached on disk by sprite().
"""
import os, math, json, hashlib
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from .config import SS, SPRITE_DIR
from .util import clamp, lerp

LIGHT = (-0.55, -0.83); RIM = (0.92, -0.38); RIM_COL = (255, 214, 150)
SPR = SPRITE_DIR


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

def ribbon(path, w0, w1):
    L, R = [], []
    for i, (x, y) in enumerate(path):
        j, k = min(i + 1, len(path) - 1), max(i - 1, 0)
        dx, dy = path[j][0] - path[k][0], path[j][1] - path[k][1]; n = math.hypot(dx, dy) or 1
        nx, ny = -dy / n, dx / n; w = lerp(w0, w1, i / (len(path) - 1)) / 2
        L.append((x + nx*w, y + ny*w)); R.append((x - nx*w, y - ny*w))
    return L + R[::-1]

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
