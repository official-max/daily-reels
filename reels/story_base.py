"""
Krishna-Arjun Samvaad - 3 part cartoon reel series.
Pillow (2x supersampled drawing) + numpy (tanpura/bansuri/SFX) + edge-tts (Hindi voices) + ffmpeg.

    python make_story.py preview 1     # contact sheet of part 1 in build/
    python make_story.py 1             # render part 1 -> part1.mp4
    python make_story.py all           # render all parts
"""
import os, sys, math, random, asyncio, subprocess, json, wave, hashlib
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from multiprocessing import Pool

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(HERE, "out")
W, H, FPS, S = 1080, 1920, 30, 2
SR = 44100
GAP, XF = 0.3, 0.35
GY = 1500          # ground line in forest scenes
HZ = 1150          # horizon for walk / farm
FONT_CAP = os.path.join(HERE, "fonts", "Poppins-Black.ttf")
FONT_B = os.path.join(HERE, "fonts", "Poppins-Bold.ttf")

VOICES = {   # speaker: (voice, rate, pitch)
    "N": ("hi-IN-SwaraNeural", "-4%", "+0Hz"),
    "K": ("hi-IN-MadhurNeural", "-10%", "-4Hz"),
    "A": ("hi-IN-MadhurNeural", "+0%", "+6Hz"),
    "P": ("hi-IN-MadhurNeural", "-12%", "-10Hz"),
    "R": ("hi-IN-MadhurNeural", "-8%", "-14Hz"),
    "C": ("hi-IN-MadhurNeural", "+4%", "+3Hz"),
}
TAGS = {"K": ("Shri Krishna", (45, 100, 205)), "A": ("Arjun", (165, 40, 55)), "P": ("Garib vyakti", (125, 88, 52)),
        "R": ("Raja", (176, 28, 44)), "C": ("Chatur", (205, 110, 30))}

# ================================================================ helpers
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def lerp(a, b, t): return a + (b - a) * t
def ease_io(t): t = clamp(t); return t * t * (3 - 2 * t)
def ease_out(t): t = clamp(t); return 1 - (1 - t) ** 3
def ease_back(t):
    t = clamp(t); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2
def lerpc(c1, c2, t): return tuple(int(lerp(a, b, t)) for a, b in zip(c1, c2))
def darker(c, f=0.72): return tuple(int(v * f) for v in c[:3])
def cubic(p0, p1, p2, p3, n=24):
    out = []
    for i in range(n + 1):
        t = i / n; m = 1 - t
        out.append((m**3*p0[0] + 3*m*m*t*p1[0] + 3*m*t*t*p2[0] + t**3*p3[0],
                    m**3*p0[1] + 3*m*m*t*p1[1] + 3*m*t*t*p2[1] + t**3*p3[1]))
    return out


class Pen:
    def __init__(self, img): self.d = ImageDraw.Draw(img, "RGBA")
    def ell(self, cx, cy, rx, ry=None, fill=None, outline=None, w=0):
        ry = rx if ry is None else ry
        if rx <= 0.2 or ry <= 0.2: return
        self.d.ellipse([(cx-rx)*S, (cy-ry)*S, (cx+rx)*S, (cy+ry)*S], fill=fill, outline=outline, width=max(1, int(round(w*S))) if outline else 0)
    def poly(self, pts, fill=None, outline=None, w=0):
        self.d.polygon([(x*S, y*S) for x, y in pts], fill=fill, outline=outline, width=max(1, int(round(w*S))) if outline else 1)
    def line(self, pts, fill, w, caps=True):
        self.d.line([(x*S, y*S) for x, y in pts], fill=fill, width=max(1, int(round(w*S))), joint="curve")
        if caps and w >= 3:
            for x, y in (pts[0], pts[-1]): self.ell(x, y, w/2, fill=fill)
    def arc(self, cx, cy, rx, ry, a0, a1, fill, w):
        self.d.arc([(cx-rx)*S, (cy-ry)*S, (cx+rx)*S, (cy+ry)*S], a0, a1, fill=fill, width=max(1, int(round(w*S))))
    def chord(self, cx, cy, rx, ry, a0, a1, fill):
        self.d.chord([(cx-rx)*S, (cy-ry)*S, (cx+rx)*S, (cy+ry)*S], a0, a1, fill=fill)
    def rect(self, x0, y0, x1, y1, fill):
        self.d.rectangle([x0*S, y0*S, x1*S, y1*S], fill=fill)


def blink(t):
    ph = t % 3.3
    return max(0.08, abs(ph - 0.07) / 0.07) if ph < 0.14 else 1.0

def vane(p, bx, by, ux, uy, L, wid, col, start=0.2):
    nx, ny = -uy, ux; top, bot = [], []
    for i in range(21):
        u = start + (1 - start) * i / 20; w = wid * math.sin(math.pi * i / 20) ** 0.7
        cx, cy = bx + ux*L*u, by + uy*L*u
        top.append((cx + nx*w, cy + ny*w)); bot.append((cx - nx*w, cy - ny*w))
    p.poly(top + bot[::-1], fill=col)

def draw_feather(p, bx, by, ang, L):
    a = math.radians(ang); ux, uy = math.sin(a), -math.cos(a)
    p.line([(bx, by), (bx + ux*L, by + uy*L)], fill=(225, 215, 170), w=L*0.025)
    vane(p, bx, by, ux, uy, L, L*0.17, (36, 132, 82))
    vane(p, bx, by, ux, uy, L*0.96, L*0.11, (78, 176, 98), start=0.35)
    ex, ey = bx + ux*L*0.8, by + uy*L*0.8
    for r, col in ((0.12, (228, 186, 60)), (0.095, (30, 150, 150)), (0.065, (35, 72, 175)), (0.035, (15, 25, 70))):
        p.ell(ex, ey, L*r, L*r*1.15, fill=col)

# ================================================================ characters
INK = (50, 30, 25)
CHARS = {
    "K": dict(skin=(92, 142, 224), skin_d=(52, 92, 168), hair=(22, 18, 36), dhoti=(250, 200, 45), dhoti_b=(220, 60, 75),
              sash=(235, 80, 115), crown="krishna", tilak="K", mala=True, halo=True, lash=True),
    "A": dict(skin=(236, 190, 150), skin_d=(190, 140, 105), hair=(32, 24, 22), dhoti=(246, 240, 226), dhoti_b=(200, 55, 60),
              top=(155, 38, 52), top_d=(105, 24, 34), belt=(240, 190, 60), crown="arjun", tilak="A", bow=True),
    "P": dict(skin=(196, 146, 104), skin_d=(148, 104, 72), hair=(80, 76, 76), dhoti=(128, 104, 82), dhoti_b=(96, 76, 58),
              top=(184, 172, 146), top_d=(130, 120, 100), patches=True),
    "F": dict(skin=(205, 150, 100), skin_d=(158, 108, 72), hair=(30, 25, 25), dhoti=(240, 236, 222), dhoti_b=(210, 120, 50),
              top=(250, 250, 245), top_d=(196, 196, 190), turban=(245, 130, 40), moustache=True),
}
BLINK_OFF = dict(K=0.0, A=1.3, P=2.2, F=0.7, R=0.5, C=1.8, G=2.9)


def draw_char(p, who, x, fy, sc, t, pose="stand", mood="smile", talk=0.0, look=(0, 0), walking=False, sit=False, glow=1.0):
    c = CHARS[who]; sk, skd = c["skin"], c["skin_d"]
    def Q(dx, dy): return (x + dx*sc, fy + dy*sc)
    def E(dx, dy, rx, ry=None, fill=None, outline=None, w=0):
        ry = rx if ry is None else ry; px, py = Q(dx, dy)
        p.ell(px, py, rx*sc, ry*sc, fill=fill, outline=outline, w=w*sc)
    def PL(pts, fill, outline=None, w=0): p.poly([Q(a, b) for a, b in pts], fill=fill, outline=outline, w=w*sc)
    def LN(pts, w, col): p.line([Q(a, b) for a, b in pts], fill=col, w=w*sc)
    def AR(dx, dy, rx, ry, a0, a1, col, w):
        px, py = Q(dx, dy); p.arc(px, py, rx*sc, ry*sc, a0, a1, col, w*sc)

    ph = t * 6.5
    bob = -abs(math.sin(ph)) * 7 if walking else 0
    sob = math.sin(t * 16) * 2.5 if (mood == "sad" and talk < 0.05) else 0
    uy = (118 if sit else 0) + bob + sob
    hy = -382 + uy
    def A(pt): return (pt[0], pt[1] + uy)

    if c.get("halo"):
        for k in range(9):
            E(0, hy - 20, 178 - k*15, fill=(255, 226, 140, int(7 + k*3 * glow)))
    if who in ("K", "A"):
        PL([(-68, hy - 20), (68, hy - 20), (80, hy + 84), (-80, hy + 84)], fill=c["hair"])
    if c.get("bow"):
        bp = cubic((92, -352 + uy), (168, -290 + uy), (132, -170 + uy), (60, -118 + uy))
        p.line([Q(a, b) for a, b in bp], fill=(120, 72, 35), w=9*sc)
        LN([(92, -352 + uy), (60, -118 + uy)], 2, (235, 225, 200))
        for k in range(3):
            LN([(-40 - k*10, -290 + uy), (-70 - k*12, -385 + uy)], 5, (140, 95, 50))
            E(-70 - k*12, -392 + uy, 7, 12, fill=(220, 60, 60))
    # ---- legs / dhoti
    if sit:
        E(0, -40, 106, 40, fill=c["dhoti"], outline=darker(c["dhoti"]), w=3)
        E(-68, -20, 27, 12, fill=sk, outline=skd, w=2); E(68, -20, 27, 12, fill=sk, outline=skd, w=2)
    else:
        sw = math.sin(ph) * 16 if walking else 0
        for side, s_ in ((-1, sw), (1, -sw)):
            LN([(side*22, -150), (side*24 + s_, -16)], 26, sk)
            E(side*27 + s_, -9, 25, 11, fill=sk, outline=skd, w=2)
            if who == "K": E(side*24 + s_, -27, 14, 5, fill=(255, 210, 70))
        sway = math.sin(ph) * 6 if walking else 0
        PL([(-60, -170 + bob), (60, -170 + bob), (76 + sway, -54), (-76 + sway, -54)], fill=c["dhoti"], outline=darker(c["dhoti"]), w=2)
        PL([(-76 + sway, -54), (76 + sway, -54), (74 + sway, -68), (-74 + sway, -68)], fill=c["dhoti_b"])
        LN([(0, -160 + bob), (sway*0.6, -62)], 3, darker(c["dhoti"]))
    # ---- torso
    tc = c.get("top") or sk; td = c.get("top_d") or skd
    PL([(-58, -304 + uy), (58, -304 + uy), (50, -162 + uy), (-50, -162 + uy)], fill=tc, outline=td, w=2)
    E(-54, -292 + uy, 21, fill=tc); E(54, -292 + uy, 21, fill=tc)
    if who == "K":
        PL([(-60, -298 + uy), (-36, -304 + uy), (54, -178 + uy), (32, -170 + uy)], fill=c["sash"])
        PL([(-52, -190 + uy), (52, -190 + uy), (52, -162 + uy), (-52, -162 + uy)], fill=(250, 200, 45), outline=(210, 150, 20), w=2)
        LN([(-46, -222 + uy), (44, -150 + uy)], 9, (150, 95, 45))
        for k in range(4): E(-24 + k*15, -204 + uy + k*12, 2.2, fill=(60, 35, 20))
    if c.get("belt"):
        PL([(-52, -190 + uy), (52, -190 + uy), (52, -168 + uy), (-52, -168 + uy)], fill=c["belt"], outline=(180, 130, 30), w=2)
        E(0, -179 + uy, 9, fill=(200, 40, 50))
    if c.get("patches"):
        E(-26, -236 + uy, 14, 11, fill=(118, 94, 68)); E(28, -200 + uy, 11, 9, fill=(172, 142, 108))
        LN([(14, -282 + uy), (22, -262 + uy), (16, -250 + uy)], 2, td)
    if who in ("K", "A"):
        for i in range(9):
            u = i / 8; E(lerp(-34, 34, u), -296 + uy + 26*math.sin(math.pi*u), 5, fill=(255, 238, 195) if who == "K" else (240, 190, 60))
    if c.get("mala"):
        cols = [(255, 246, 246), (255, 110, 150), (255, 200, 60)]
        for i in range(19):
            u = i / 18; E(lerp(-44, 44, u), -300 + uy + 122*math.sin(math.pi*u), 7, fill=cols[i % 3])
    # ---- arms
    swing = math.sin(ph) * 14 if walking else 0
    g = math.sin(t * 3.3) * 10 * min(1, talk * 4)
    L_el, L_h = (-76, -228), (-70 + swing, -168)
    R_el, R_h = (76, -228), (70 - swing, -168)
    if pose == "talk": L_el, L_h = (-90, -232), (-44 + g*0.4, -262 + g)
    elif pose == "bless": L_el, L_h = (-104, -262), (-96 + g*0.3, -346 + g*0.4)
    elif pose == "namaste": L_el, R_el, L_h, R_h = (-74, -226), (74, -226), (-8, -262), (8, -262)
    elif pose == "wipe": L_el, L_h = (-84, -252), (-30, -372)
    elif pose == "sow":
        a = t * 4.0; L_el, L_h = (-92, -250), (-118 + 26*math.cos(a), -292 + 24*math.sin(a)); R_h = (64, -196)
    elif pose == "hip": L_el, R_el, L_h, R_h = (-100, -222), (100, -222), (-50, -176), (50, -176)
    arm_col = tc if who in ("P", "F") else sk
    for shd, el, hd in (((-56, -290), L_el, L_h), ((56, -290), R_el, R_h)):
        LN([A(shd), A(el), A(hd)], 22, arm_col)
        if who == "A": E(*A(((shd[0] + el[0]) / 2, (shd[1] + el[1]) / 2)), 13, 8, fill=(240, 190, 60))
        if who == "K": E(*A(((el[0]*2 + hd[0]) / 3, (el[1]*2 + hd[1]) / 3)), 12, 6, fill=(255, 210, 70))
        E(*A(hd), 12, fill=sk, outline=skd, w=2)
    if pose == "bless":
        hx, hy2 = A(L_h); E(hx, hy2 - 6, 17, 22, fill=sk, outline=skd, w=2)
        E(hx, hy2 - 4, 4, fill=(220, 50, 60))
    if pose == "namaste": PL([A((-15, -244)), A((15, -244)), A((0, -304))], fill=sk, outline=skd, w=2)
    if pose == "sow": E(*A((74, -198)), 26, 30, fill=(205, 172, 112), outline=(150, 118, 70), w=2)
    # ---- head
    PL([(-15, -322 + uy), (15, -322 + uy), (15, -294 + uy), (-15, -294 + uy)], fill=sk)
    for side in (-1, 1):
        E(side*70, hy + 6, 14, 18, fill=sk, outline=skd, w=2)
        if who == "K": E(side*73, hy + 33, 8, 11, fill=(255, 205, 60), outline=(200, 140, 30), w=1)
    E(0, hy, 72, 75, fill=sk, outline=skd, w=2.5)
    hx_, hy_ = Q(0, hy)
    p.chord(hx_, hy_, 77*sc, 77*sc, 205, 335, c["hair"])
    if who == "P":
        for dx, dy, rr in ((-40, -66, 22), (-10, -76, 24), (22, -74, 22), (48, -60, 18), (-58, -44, 14)):
            E(dx, hy + dy, rr, fill=c["hair"])
        p.chord(hx_, hy_ + 2*sc, 70*sc, 72*sc, 20, 160, (95, 72, 58, 110))
    bl = blink(t + BLINK_OFF[who]); ey = hy + 8
    for side in (-1, 1):
        ex = side * 27
        if mood == "happy" and talk < 0.05:
            AR(ex, ey + 4, 13, 10, 200, 340, INK, 4.5)
        else:
            E(ex, ey, 14, 17*bl, fill=(255, 255, 255), outline=INK, w=2)
            if bl > 0.3:
                E(ex + look[0]*5, ey + 2 + look[1]*5, 9, 10*bl, fill=(45, 28, 20))
                E(ex + look[0]*5 - 3, ey - 2 + look[1]*5, 3, fill=(255, 255, 255))
            if c.get("lash"): LN([(ex + side*12, ey - 12), (ex + side*19, ey - 18)], 3, INK)
        by_ = ey - 26
        if mood == "sad": LN([(side*42, by_ + 4), (side*14, by_ - 6)], 4, INK)
        elif mood == "curious" and side == 1: LN([(14, by_ - 4), (40, by_ - 12)], 4, INK)
        else: AR(ex, by_ + 6, 14, 6, 200, 340, INK, 4)
    if c.get("tilak") == "K":
        LN([(-8, hy - 34), (-6, hy - 16), (0, hy - 12), (6, hy - 16), (8, hy - 34)], 3, (255, 240, 190))
        LN([(0, hy - 32), (0, hy - 18)], 3, (220, 40, 50))
    elif c.get("tilak") == "A":
        LN([(0, hy - 32), (0, hy - 16)], 4, (210, 40, 45))
    AR(0, hy + 28, 6, 4, 20, 160, skd, 3)
    E(-46, hy + 30, 12, 7, fill=(255, 120, 140, 70)); E(46, hy + 30, 12, 7, fill=(255, 120, 140, 70))
    my = hy + 46
    if c.get("moustache"):
        E(-13, my - 9, 15, 5, fill=c["hair"]); E(13, my - 9, 15, 5, fill=c["hair"])
    if talk > 0.04:
        o = clamp(talk)
        E(0, my, 12 + 3*o, 3 + 12*o, fill=(115, 35, 40), outline=INK, w=2)
        if o > 0.3: E(0, my + 7*o, 7, 4*o, fill=(230, 115, 125))
    elif mood == "happy":
        px2, py2 = Q(0, my - 8); p.chord(px2, py2, 18*sc, 15*sc, 0, 180, (110, 35, 40))
    elif mood == "sad":
        AR(0, my + 8, 14, 9, 205, 335, INK, 4)
    elif mood == "neutral":
        LN([(-10, my), (10, my)], 4, INK)
    else:
        AR(0, my - 8, 16, 10, 25, 155, INK, 4)
    if mood == "sad":
        q = (t % 1.3) / 1.3
        for side in (-1, 1): E(side*30, ey + 14 + q*48, 4.5, 6.5, fill=(120, 190, 255, int(240*(1 - q))))
    # ---- headwear
    if c.get("crown") == "krishna":
        bx, by2 = Q(10, hy - 100)
        draw_feather(p, bx, by2, 14 + 3*math.sin(t*1.7), 165*sc)
        PL([(-46, hy - 52), (-30, hy - 98), (0, hy - 124), (30, hy - 98), (46, hy - 52)], fill=(245, 195, 55), outline=(190, 135, 25), w=2)
        PL([(-62, hy - 56), (62, hy - 56), (58, hy - 34), (-58, hy - 34)], fill=(250, 205, 70), outline=(190, 135, 25), w=2)
        E(0, hy - 80, 10, fill=(220, 40, 60), outline=(150, 20, 30), w=1)
        for dx in (-34, 34): E(dx, hy - 45, 5, fill=(40, 170, 100))
        for k in range(7): E(-48 + k*16, hy - 45 + (6 if k % 2 else 0), 2.6, fill=(255, 250, 230))
    elif c.get("crown") == "arjun":
        for dx, hh in ((-34, 30), (0, 44), (34, 30)):
            PL([(dx - 15, hy - 50), (dx, hy - 50 - hh), (dx + 15, hy - 50)], fill=(240, 190, 60), outline=(180, 130, 30), w=2)
        PL([(-60, hy - 56), (60, hy - 56), (56, hy - 34), (-56, hy - 34)], fill=(240, 190, 60), outline=(180, 130, 30), w=2)
        E(0, hy - 45, 7, fill=(210, 40, 50))
    if c.get("turban"):
        E(0, hy - 52, 82, 42, fill=c["turban"], outline=darker(c["turban"]), w=2)
        for k in range(3): AR(0, hy - 48 + k*10, 70 - k*6, 26, 200, 340, darker(c["turban"]), 3)

# ================================================================ backgrounds
FOREST_DAY = dict(sky=[(110, 185, 240), (175, 220, 248), (235, 240, 225)], far=(150, 195, 170), tfar=(95, 160, 115),
                  tmid=(60, 140, 75), thi=(95, 175, 95), trunk=(110, 78, 52), g0=(140, 195, 95), g1=(80, 150, 65), path=(225, 200, 150))
FOREST_SUNSET = dict(sky=[(45, 30, 85), (200, 85, 100), (255, 170, 90)], far=(130, 64, 92), tfar=(88, 44, 74),
                     tmid=(58, 32, 58), thi=(78, 42, 68), trunk=(52, 30, 46), g0=(130, 76, 74), g1=(72, 42, 56), path=(190, 126, 100))

def sky_img(stops, h=None):
    h = h or H * S
    ys = np.linspace(0, 1, h); n = len(stops) - 1; arr = np.zeros((h, 3))
    for i in range(n):
        a, b = i / n, (i + 1) / n
        m = (ys >= a) & (ys <= b); f = ((ys[m] - a) / (b - a))[:, None]
        arr[m] = np.array(stops[i]) * (1 - f) + np.array(stops[i + 1]) * f
    return Image.fromarray(np.repeat(arr[:, None, :], W * S, axis=1).astype(np.uint8), "RGB")

def ground_bands(p, y0, c0, c1, n=30):
    for i in range(n):
        a, b = lerp(y0, H, i / n), lerp(y0, H, (i + 1) / n)
        p.rect(0, a, W, b + 1, lerpc(c0, c1, i / n))

def canopy(p, x, y, s, col, hi):
    for dx, dy, r in ((0, 0, 120), (-90, 30, 90), (90, 30, 90), (-50, -70, 90), (55, -75, 85)):
        p.ell(x + dx*s, y + dy*s, r*s, fill=col)
    for dx, dy, r in ((-40, -60, 45), (45, -40, 38)):
        p.ell(x + dx*s, y + dy*s, r*s, fill=hi)

def build_forest(pal, banyan=False, sunset=False):
    img = sky_img(pal["sky"]); p = Pen(img); rr = random.Random(5)
    if sunset:
        for k in range(8): p.ell(540, 1090, 190 + k*60, fill=(255, 190, 110, 16))
        p.ell(540, 1090, 175, fill=(255, 180, 95))
    else:
        for k in range(6): p.ell(190, 470, 90 + k*40, fill=(255, 250, 215, 20))
        p.ell(190, 470, 72, fill=(255, 248, 210))
    far = [(x, 1070 + 40*math.sin(x*0.007 + 1) + 18*math.sin(x*0.02)) for x in range(-20, 1110, 10)]
    p.poly(far + [(1110, 1300), (-20, 1300)], fill=pal["far"])
    for x in range(-40, 1130, 50):
        r = rr.uniform(45, 80); p.ell(x, 1135 - rr.uniform(0, 40), r, fill=pal["tfar"])
    mids = (60, 250, 430) if banyan else (60, 250, 830, 1010)
    for x in mids:
        p.rect(x - 15, 900, x + 15, 1210, pal["trunk"])
        canopy(p, x, 870, 1.05, pal["tmid"], pal["thi"])
    ground_bands(p, 1180, pal["g0"], pal["g1"])
    p.poly([(470, 1180), (610, 1180), (1000, H), (80, H)], fill=pal["path"])
    for _ in range(70):
        x, y = rr.uniform(0, 1080), rr.uniform(1200, 1900)
        p.poly([(x - 6, y), (x, y - rr.uniform(14, 26)), (x + 6, y)], fill=lerpc(pal["g1"], (255, 255, 255), 0.12))
    for _ in range(18):
        x, y = rr.uniform(0, 1080), rr.uniform(1250, 1880)
        p.ell(x, y, 7, fill=rr.choice([(255, 120, 160), (255, 220, 80), (255, 255, 255), (190, 130, 255)]))
    if banyan:
        p.poly([(840, GY + 24), (1000, GY + 24), (965, 1200), (985, 800), (905, 760), (885, 1200)], fill=(110, 78, 52), outline=(70, 48, 30), w=4)
        for (a, b) in (((930, 860), (690, 640)), ((960, 820), (1120, 620)), ((920, 900), (760, 760))):
            p.line([a, b], fill=(100, 70, 46), w=34)
        for x in range(640, 1080, 34):
            p.line([(x, 780 + (x % 3) * 20), (x + 4, 1060 + (x % 5) * 40)], fill=(120, 88, 60, 200), w=4)
        for dx, dy, r, col in ((860, 560, 260, (46, 120, 56)), (640, 660, 170, (46, 120, 56)), (1080, 640, 190, (46, 120, 56)),
                               (760, 470, 170, (66, 150, 70)), (980, 470, 170, (66, 150, 70)), (860, 680, 170, (66, 150, 70)),
                               (700, 560, 120, (66, 150, 70)), (800, 420, 70, (110, 190, 100)), (950, 400, 60, (110, 190, 100)),
                               (690, 600, 55, (110, 190, 100)), (1040, 560, 55, (110, 190, 100))):
            p.ell(dx, dy, r, r*0.85, fill=col)
    for x in (30, 1050):
        canopy(p, x, 1830, 1.2, darker(pal["g1"], 0.8), pal["g1"])
    return img

def build_walkbg():
    pal = FOREST_DAY; img = sky_img(pal["sky"]); p = Pen(img)
    for k in range(6): p.ell(270, 560, 90 + k*40, fill=(255, 250, 215, 20))
    p.ell(270, 560, 70, fill=(255, 248, 210))
    far = [(x, HZ - 60 + 30*math.sin(x*0.008) + 14*math.sin(x*0.021)) for x in range(-20, 1110, 10)]
    p.poly(far + [(1110, HZ + 10), (-20, HZ + 10)], fill=pal["far"])
    for x in range(-30, 1120, 36): p.ell(x, HZ - 8, 22 + (x * 7) % 14, fill=pal["tfar"])
    ground_bands(p, HZ, pal["g0"], pal["g1"])
    p.poly([(515, HZ), (565, HZ), (1050, H), (30, H)], fill=pal["path"])
    return img

def build_divine():
    yy, xx = np.mgrid[0:H*S, 0:W*S].astype(np.float32)
    d = np.sqrt((xx - 540*S)**2 + ((yy - 1150*S) * 0.85)**2) / (1150*S)
    stops = [(0, (255, 242, 195)), (0.3, (252, 190, 100)), (0.65, (196, 84, 96)), (1.0, (64, 28, 84))]
    out = np.zeros((H*S, W*S, 3), np.float32)
    for (a, ca), (b, cb) in zip(stops, stops[1:]):
        m = (d >= a) & (d < b); f = ((d[m] - a) / (b - a))[:, None]
        out[m] = np.array(ca) * (1 - f) + np.array(cb) * f
    out[d >= 1.0] = stops[-1][1]
    img = Image.fromarray(out.astype(np.uint8), "RGB"); p = Pen(img)
    for r in (330, 450, 570, 700): p.ell(540, 1150, r, outline=(255, 235, 180, 45), w=3)
    for k in range(24):
        a = k * math.pi / 12
        p.ell(540 + math.cos(a)*450, 1150 + math.sin(a)*450, 10, fill=(255, 235, 180, 70))
    return img

def build_farm_fg():
    fg = Image.new("RGBA", (W*S, H*S), (0, 0, 0, 0)); p = Pen(fg)
    far = [(x, HZ - 50 + 30*math.sin(x*0.007 + 2)) for x in range(-20, 1110, 10)]
    p.poly(far + [(1110, HZ + 20), (-20, HZ + 20)], fill=(150, 190, 130))
    for hx in (180, 300):
        p.rect(hx - 40, HZ - 70, hx + 40, HZ, (200, 160, 110))
        p.poly([(hx - 55, HZ - 68), (hx, HZ - 115), (hx + 55, HZ - 68)], fill=(170, 120, 60))
        p.rect(hx - 10, HZ - 40, hx + 10, HZ, (100, 70, 45))
    ground_bands(p, HZ, (165, 120, 75), (120, 80, 48))
    for r in range(8):
        y = lerp(1190, 1880, (r / 7) ** 1.3)
        p.rect(0, y - 6 - r, W, y + 4 + r, (100, 66, 40, 120))
    a = np.array(fg); a[(HZ - 2)*S:, :, 3] = 255
    return Image.fromarray(a, "RGBA")

def build_sun_fg():
    fg = Image.new("RGBA", (W*S, H*S), (0, 0, 0, 0)); p = Pen(fg)
    h1 = [(x, 1360 + 50*math.sin(x*0.006 + 0.5)) for x in range(-20, 1110, 10)]
    h2 = [(x, 1470 + 40*math.sin(x*0.009 + 2)) for x in range(-20, 1110, 10)]
    p.poly(h1 + [(1110, H), (-20, H)], fill=(110, 170, 100))
    p.poly(h2 + [(1110, H), (-20, H)], fill=(80, 145, 75))
    ground_bands(p, 1620, (90, 155, 80), (60, 120, 55))
    for x in range(-20, 1100, 120): canopy(p, x, 1560 + (x % 3)*20, 0.45, (50, 110, 55), (80, 150, 75))
    return fg

CACHE = {}
def asset(name):
    key = "bg:" + name
    if key not in CACHE:
        bgs = [k for k in CACHE if isinstance(k, str) and k.startswith("bg:")]
        if len(bgs) >= 5:
            for k in bgs[:2]: del CACHE[k]
        b = dict(walk=build_walkbg, meet=lambda: build_forest(FOREST_DAY, banyan=True),
                 seekh=lambda: build_forest(FOREST_SUNSET, sunset=True), divine=build_divine,
                 farm_day=lambda: sky_img([(110, 185, 240), (180, 222, 248), (240, 240, 220)]),
                 farm_gold=lambda: sky_img([(250, 150, 80), (255, 200, 120), (255, 232, 170)]),
                 farm_fg=build_farm_fg, sun_dark=lambda: sky_img([(58, 64, 80), (92, 98, 112), (128, 132, 142)]),
                 sun_bright=lambda: sky_img([(70, 155, 240), (145, 205, 250), (235, 242, 250)]), sun_fg=build_sun_fg)[name]
        CACHE[key] = b()
    return CACHE[key]

# ================================================================ shots
_r = random.Random(9)
WALK_TREES = [((1 if i % 2 else -1) * _r.uniform(330, 650), i * 0.5, _r.choice([(60, 140, 75), (70, 150, 80), (50, 125, 70)])) for i in range(14)]
STONES = [(_r.uniform(-140, 140), _r.uniform(0, 1)) for _ in range(14)]
LEAVES = [(_r.uniform(400, 1100), _r.uniform(0, 900), _r.uniform(0, 6.28)) for _ in range(8)]
SPARKS = [(_r.uniform(80, 1000), _r.uniform(0, 1), _r.uniform(0.08, 0.2)) for _ in range(40)]
PETALS = [(_r.uniform(0, 1080), _r.uniform(0, 1), _r.uniform(0, 6.28)) for _ in range(12)]
CUR = dict(talk={})
def talk(who): return CUR["talk"].get(who, 0.0)

def shot_walk(t, s):
    img = asset("walk").copy(); p = Pen(img); fogc = (175, 210, 215)
    trees = []
    for X, z0, col in WALK_TREES:
        z = ((z0 - t * 0.55) % 7.0) + 0.7; trees.append((z, X, col))
    for z, X, col in sorted(trees, reverse=True):
        k = 1 / z; sx = 540 + X*k; by = HZ + 420*k; f = clamp((z - 0.7) / 6) * 0.8
        tr = lerpc((105, 75, 50), fogc, f); th, tw = 330*k, 34*k
        p.poly([(sx - tw, by), (sx + tw, by), (sx + tw*0.6, by - th), (sx - tw*0.6, by - th)], fill=tr)
        canopy(p, sx, by - th - 60*k, 1.25*k, lerpc(col, fogc, f), lerpc((100, 180, 95), fogc, f))
    for X, u0 in STONES:
        u = (u0 + t * 0.13) % 1; z = lerp(7.5, 0.6, u); k = 1 / z
        p.ell(540 + X*k, HZ + 420*k, 10*k, 5*k, fill=(185, 160, 120))
    draw_char(p, "K", 380, 1690, 1.45, t, mood="smile", look=(0.5, 0), walking=True)
    draw_char(p, "A", 700, 1690, 1.45, t + 0.25, mood="smile", look=(-0.6, 0), walking=True)
    e = ease_io(t / s["dur"])
    return img, dict(zoom=lerp(1.0, 1.06, e), cx=540, cy=1000)

def shot_meet(t, s):
    img = asset("meet").copy(); p = Pen(img)
    for x0, y0, ph in LEAVES:
        y = (y0 + t * 80) % 1000 + 520; x = x0 + 40*math.sin(t*1.3 + ph)
        p.ell(x, y, 9, 5, fill=(150, 200, 90, 220))
    kx = s.get("kx", 230); ax = 450; kwalk = False
    if "kwalk" in s:
        k0, k1 = s["kwalk"]; u = clamp((t - 0.3) / 2.8); kx = lerp(k0, k1, ease_io(u)); kwalk = 0 < u < 1
    if "kwalk" in s or "kx" in s: ax = 200
    arrive = s.get("arrive") and t < 2.6
    off = lerp(-430, 0, ease_out(t / 2.6)) if s.get("arrive") else 0
    pm = s.get("pmood", "sad")
    pmood = {"listen": "neutral", "happy": "happy"}.get(pm, pm)
    ptalk = talk("P")
    ppose = "wipe" if (pmood == "sad" and ptalk < 0.05 and (t % 5) < 1.8) else "stand"
    plook = (-0.8, 0) if (talk("K") > 0 or talk("A") > 0 or pm == "listen") else (0, 0.4)
    draw_char(p, "P", 800, GY, 1.3, t, pose=ppose, mood=pmood, talk=ptalk, look=plook, sit=True)
    ap = s.get("apose") or ("talk" if talk("A") > 0.05 else "stand")
    draw_char(p, "A", ax + off, GY, 1.3, t + 0.3, pose=ap, mood="smile" if pm != "sad" else "curious",
              talk=talk("A"), look=(s.get("alook", 0), 0), walking=arrive)
    kp = s.get("kpose") or ("talk" if talk("K") > 0.05 else "stand")
    draw_char(p, "K", kx + off, GY, 1.3, t, pose=kp, mood="smile", talk=talk("K"),
              look=(s.get("klook", 0.6 if kwalk else 0.4), 0), walking=arrive or kwalk)
    nm = s.get("cam", "wide"); e = ease_io(t / s["dur"])
    z, cx, cy = dict(wide=(1.0, 540, 1000), a=(1.75, ax, GY - 440), k=(1.75, kx, GY - 440), p=(1.8, 800, GY - 330),
                     ka=(1.4, (kx + ax) / 2, GY - 400), kp=(1.45, (kx + 800) / 2, GY - 400))[nm]
    return img, dict(zoom=z * lerp(1.0, 1.06, e), cx=cx, cy=cy)

def shot_divine(t, s):
    img = asset("divine").copy(); p = Pen(img); gl = s.get("glow", 1.0)
    rot = t * 0.12
    for k in range(16):
        a = rot + k * math.pi / 8; da = 0.06
        p.poly([(540, 1150), (540 + math.cos(a - da)*1600, 1150 + math.sin(a - da)*1600),
                (540 + math.cos(a + da)*1600, 1150 + math.sin(a + da)*1600)], fill=(255, 240, 200, int(22*gl)))
    for i, (x0, ph, sp) in enumerate(SPARKS):
        u = (t * sp + ph) % 1; y = 1900 - u * 1750; x = x0 + 25*math.sin(t + i)
        p.ell(x, y, 3.5 + (i % 3), fill=(255, 248, 210, int(220 * math.sin(math.pi*u))))
    for i, (x0, ph, rot0) in enumerate(PETALS):
        u = (t * 0.09 + ph) % 1; y = -40 + u * 2000; x = x0 + 60*math.sin(t*0.8 + rot0)
        p.ell(x, y, 13, 7, fill=(255, 140, 170, 210))
    draw_char(p, "K", 540, 2080, 2.3, t, pose="bless", mood="smile", talk=talk("K"), look=(0, 0.1), glow=gl)
    e = ease_io(t / s["dur"])
    return img, dict(zoom=lerp(1.0, 1.07, e), cx=540, cy=1080)

def crop_rows(p, g, t, before=None):
    for r in range(8):
        u = r / 7; y = lerp(1190, 1880, u ** 1.3); s_ = lerp(0.4, 1.25, u); sp = 70 * s_
        if before and y > before[0]: before[1](); before = None
        x = -sp / 2 + (r % 2) * sp / 2
        gold = clamp((g - 0.65) / 0.35)
        col = lerpc((90, 172, 60), (222, 182, 70), gold)
        while x < W + sp:
            h_ = 130 * s_ * g
            if h_ > 2:
                for j, ang in enumerate((-12, 0, 12)):
                    a = math.radians(ang + 3*math.sin(t*2 + x*0.01))
                    tx, ty = x + math.sin(a)*h_, y - math.cos(a)*h_
                    p.line([(x, y), (tx, ty)], fill=col, w=max(1.5, 4*s_), caps=False)
                    if g > 0.5: p.ell(tx, ty - 6*s_, 6*s_, 15*s_*clamp((g - 0.5) * 3), fill=lerpc((150, 200, 90), (240, 196, 80), gold))
            x += sp
    if before: before[1]()

SEED_THROWS = None
def shot_farm(t, s):
    mode = s.get("mode", "sow"); dur = s["dur"]
    if mode == "sow":
        img = asset("farm_day").copy(); p = Pen(img)
        p.ell(260, 520, 70, fill=(255, 248, 210))
    else:
        k = ease_io(t / dur); img = Image.blend(asset("farm_day"), asset("farm_gold"), k); p = Pen(img)
        a = lerp(math.pi * 0.95, math.pi * 0.1, k)
        sx, sy = 540 + math.cos(a) * 440, 1100 - math.sin(a) * 620
        for j in range(5): p.ell(sx, sy, 80 + j*35, fill=(255, 240, 180, 22))
        p.ell(sx, sy, 70, fill=(255, 236, 160))
    fg = asset("farm_fg"); img.paste(fg, (0, 0), fg)
    if mode == "sow":
        fx = lerp(220, 820, t / dur)
        crop_rows(p, 0.0, t)
        for i in range(int(t / 0.5) + 1):
            t0 = i * 0.5
            hx = lerp(220, 820, t0 / dur) - 118*1.25; hy = 1600 - 300*1.25
            for j in range(3):
                vx, vy = -60 - j*50, -120 + j*40; dt = t - t0
                if dt < 0: continue
                land = 0.9 + j*0.1; dd = min(dt, land)
                x, y = hx + vx*dd, hy + vy*dd + 600*dd*dd
                p.ell(x, y, 5, 4, fill=(120, 80, 40))
        draw_char(p, "F", fx, 1600, 1.25, t, pose="sow", mood="smile", look=(-0.5, 0.3), walking=True)
        return img, dict(zoom=lerp(1.08, 1.0, ease_io(t / dur)), cx=540, cy=1050)
    g = ease_io((t - 0.2) / (dur - 0.7))
    crop_rows(p, g, t, before=(1640, lambda: draw_char(p, "F", 880, 1640, 1.15, t, pose="hip", mood="happy")))
    return img, dict(zoom=1.04, cx=540, cy=1000)

def shot_sun(t, s):
    dur = s["dur"]; k = ease_io((t - 0.8) / (dur * 0.55))
    img = Image.blend(asset("sun_dark"), asset("sun_bright"), k); p = Pen(img)
    sx, sy = 540, 860
    for j in range(8): p.ell(sx, sy, 130 + j*55, fill=(255, 240, 180, int(10 + 16*k)))
    rot = t * 0.08
    for j in range(14):
        a = rot + j * math.pi / 7; da = 0.05
        p.poly([(sx, sy), (sx + math.cos(a - da)*1700, sy + math.sin(a - da)*1700), (sx + math.cos(a + da)*1700, sy + math.sin(a + da)*1700)],
               fill=(255, 245, 200, int(45 * k)))
    p.ell(sx, sy, 115, fill=(255, 232, 120)); p.ell(sx, sy, 95, fill=(255, 245, 170))
    col = lerpc((88, 92, 106), (240, 242, 248), k); shd = lerpc((66, 70, 84), (210, 220, 236), k)
    cloud_parts = ((-150, 20, 120), (-60, -50, 150), (60, -40, 140), (160, 30, 120), (0, 60, 150), (-230, 70, 90), (240, 70, 90))
    for cx0, dirn in ((lerp(400, -160, k), -1), (lerp(680, 1240, k), 1)):
        for dx, dy, r in cloud_parts: p.ell(cx0 + dx*0.9, sy + dy + 20, r, r*0.8, fill=shd)
        for dx, dy, r in cloud_parts: p.ell(cx0 + dx*0.9, sy + dy, r, r*0.8, fill=col)
    for cx0, cy0 in ((lerp(200, -200, k), 420), (lerp(880, 1300, k), 520)):
        for dx, dy, r in cloud_parts: p.ell(cx0 + dx*0.5, cy0 + dy*0.5, r*0.5, r*0.4, fill=col)
    fg = asset("sun_fg"); img.paste(fg, (0, 0), fg)
    return img, dict(zoom=lerp(1.1, 1.0, ease_io(t / dur)), cx=540, cy=960)

def shot_seekh(t, s):
    img = asset("seekh").copy(); p = Pen(img)
    for i, (x0, ph, sp) in enumerate(SPARKS[:25]):
        u = (t * sp + ph) % 1; y = 1700 - u * 1300
        p.ell(x0 + 20*math.sin(t + i), y, 3, fill=(255, 230, 150, int(200 * math.sin(math.pi*u))))
    draw_char(p, "A", 240, 1580, 1.2, t + 0.3, pose="namaste", mood="smile", look=(0.6, 0))
    draw_char(p, "P", 840, 1580, 1.2, t + 0.7, pose="namaste", mood="happy", look=(-0.6, 0))
    draw_char(p, "K", 540, 1600, 1.3, t, pose="bless", mood="smile", look=(0, 0.1), glow=1.3)
    return img, dict(zoom=lerp(1.18, 1.32, ease_io(t / s["dur"])), cx=540, cy=1200)

SHOT_FN = dict(walk=shot_walk, meet=shot_meet, divine=shot_divine, farm=shot_farm, sun=shot_sun, seekh=shot_seekh)

# ================================================================ overlays
def fonts():
    if "f_cap" not in CACHE:
        CACHE["f_cap"] = ImageFont.truetype(FONT_CAP, 74)
        CACHE["f_b"] = ImageFont.truetype(FONT_B, 46)
        CACHE["f_tag"] = ImageFont.truetype(FONT_B, 40)
        CACHE["f_big"] = ImageFont.truetype(FONT_CAP, 100)
        CACHE["f_btn"] = ImageFont.truetype(FONT_CAP, 60)
        yy, xx = np.mgrid[0:H, 0:W]
        d = np.sqrt(((xx - W/2) / (W*0.62))**2 + ((yy - H/2) / (H*0.62))**2)
        v = np.zeros((H, W, 4), np.uint8); v[..., 3] = (np.clip((d - 0.62) / 0.55, 0, 1) ** 1.6 * 150).astype(np.uint8)
        CACHE["vig"] = Image.fromarray(v, "RGBA")
    return CACHE

def parse_tokens(text):
    toks, cur, hl, state = [], "", False, False
    for ch in text:
        if ch == "*": state = not state; continue
        if ch == " ":
            if cur: toks.append((cur, hl)); cur = ""
            continue
        if not cur: hl = state
        cur += ch
    if cur: toks.append((cur, hl))
    return toks

def ctext(d, cx, y, txt, font, fill, stroke=6, sfill=(18, 14, 24)):
    tw = font.getlength(txt); d.text((cx - tw / 2, y), txt, font=font, fill=fill, stroke_width=stroke, stroke_fill=sfill)

def make_caption(text, spk, tag=None):
    f = fonts(); font = f["f_cap"]; sp = font.getlength(" ")
    lines, cur, cw = [], [], 0
    for w, hl in parse_tokens(text):
        ww = font.getlength(w)
        if cur and cw + sp + ww > 950: lines.append(cur); cur, cw = [], 0
        cw = ww if not cur else cw + sp + ww; cur.append((w, hl, ww))
    lines.append(cur)
    lh = int(font.size * 1.22); top = 78 if spk in TAGS else 18
    img = Image.new("RGBA", (W, top + lh * len(lines) + 40), (0, 0, 0, 0)); shd = img.copy()
    d, ds = ImageDraw.Draw(img), ImageDraw.Draw(shd)
    if spk in TAGS:
        name, col = TAGS[spk]; name = tag or name; tf = f["f_tag"]; tw = tf.getlength(name)
        d.rounded_rectangle([W/2 - tw/2 - 26, 6, W/2 + tw/2 + 26, 64], radius=29, fill=col + (235,), outline=(255, 255, 255), width=3)
        d.text((W/2 - tw/2, 9), name, font=tf, fill=(255, 255, 255))
    for li, line in enumerate(lines):
        lw = sum(x[2] for x in line) + sp * (len(line) - 1); x = (W - lw) / 2; y = top + li * lh
        for w, hl, ww in line:
            ds.text((x + 4, y + 8), w, font=font, fill=(0, 0, 0, 160), stroke_width=9, stroke_fill=(0, 0, 0, 160))
            d.text((x, y), w, font=font, fill=(255, 212, 0) if hl else (255, 255, 255), stroke_width=7, stroke_fill=(18, 16, 22))
            x += ww + sp
    shd = shd.filter(ImageFilter.GaussianBlur(7)); shd.alpha_composite(img)
    return shd

def fit(text, font, maxw):
    size = font.size
    while size > 30 and ImageFont.truetype(font.path, size).getlength(text) > maxw: size -= 4
    return ImageFont.truetype(font.path, size)

def make_title(label, l1, l2, sub):
    f = fonts(); img = Image.new("RGBA", (W, 470), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    d.rounded_rectangle([90, 40, W - 90, 450], radius=46, fill=(25, 12, 40, 165), outline=(245, 195, 60), width=5)
    tw = f["f_b"].getlength(label)
    d.rounded_rectangle([W/2 - tw/2 - 30, 70, W/2 + tw/2 + 30, 136], radius=33, fill=(245, 195, 60))
    d.text((W/2 - tw/2, 72), label, font=f["f_b"], fill=(60, 20, 30))
    ctext(d, W/2, 150, l1, fit(l1, f["f_big"], 860), (255, 214, 70), 7)
    ctext(d, W/2, 262, l2, fit(l2, f["f_big"], 860), (255, 255, 255), 7)
    ctext(d, W/2, 380, sub, fit(sub, f["f_b"], 820), (255, 225, 190), 4)
    return img

def make_end(end_text, end_sub):
    f = fonts(); img = Image.new("RGBA", (W, 520), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    d.rounded_rectangle([110, 20, W - 110, 500], radius=46, fill=(20, 10, 35, 150))
    ctext(d, W/2, 40, end_text, fit(end_text, f["f_big"], 780), (255, 214, 70), 8)
    ctext(d, W/2, 180, end_sub, fit(end_sub, f["f_b"], 760), (255, 255, 255), 4)
    bw, bh, by = 560, 120, 330; bx = (W - bw) / 2
    d.rounded_rectangle([bx + 6, by + 10, bx + bw + 6, by + bh + 10], radius=60, fill=(0, 0, 0, 110))
    d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=60, fill=(240, 40, 80), outline=(255, 255, 255), width=6)
    ctext(d, W/2, by + 18, "SUBSCRIBE", f["f_btn"], (255, 255, 255), 0)
    return img

def make_hook(text):
    """White bar pinned to the top for the whole reel; *word* is shown in red."""
    font = fit(text.replace("*", ""), ImageFont.truetype(FONT_CAP, 56), 880)
    toks = parse_tokens(text); sp = font.getlength(" ")
    tw = sum(font.getlength(w) for w, _ in toks) + sp * (len(toks) - 1)
    bw = tw + 80; img = Image.new("RGBA", (W, 150), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    d.rounded_rectangle([(W - bw) / 2 + 5, 24, (W + bw) / 2 + 5, 134], radius=22, fill=(0, 0, 0, 90))
    d.rounded_rectangle([(W - bw) / 2, 16, (W + bw) / 2, 126], radius=22, fill=(255, 255, 255), outline=(25, 20, 30), width=4)
    x = (W - tw) / 2; y = 71 - font.size * 0.62
    for w, hl in toks:
        d.text((x, y), w, font=font, fill=(214, 30, 50) if hl else (25, 20, 30)); x += font.getlength(w) + sp
    return img

def make_sticker(text):
    """Tilted paper card that pops in at the start of a shot."""
    font = fit(text, ImageFont.truetype(FONT_CAP, 54), 560); tw = font.getlength(text)
    bw, bh = int(tw + 90), int(font.size * 1.75)
    img = Image.new("RGBA", (bw + 40, bh + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    d.rectangle([28, 30, bw + 28, bh + 30], fill=(0, 0, 0, 100))
    d.rectangle([16, 16, bw + 16, bh + 16], fill=(255, 246, 214), outline=(40, 30, 30), width=5)
    d.rectangle([bw / 2 - 40, 6, bw / 2 + 72, 30], fill=(250, 210, 90, 220))
    d.text((16 + (bw - tw) / 2, 16 + (bh - font.size * 1.25) / 2), text, font=font, fill=(200, 30, 45))
    return img.filter(ImageFilter.SMOOTH).rotate(-4, resample=Image.BICUBIC, expand=True)

def _icon(d, icon, cx, cy, r):
    """Simple bold icons drawn into a 2x-scale card."""
    ink, gold, red, green = (40, 26, 20), (240, 184, 60), (215, 40, 50), (40, 170, 90)
    w = max(4, int(r * 0.14))
    if icon == "gallows":
        d.line([(cx - r*0.6, cy + r), (cx + r*0.2, cy + r)], fill=ink, width=w)
        d.line([(cx - r*0.4, cy + r), (cx - r*0.4, cy - r)], fill=ink, width=w)
        d.line([(cx - r*0.4, cy - r), (cx + r*0.5, cy - r)], fill=ink, width=w)
        d.line([(cx + r*0.4, cy - r), (cx + r*0.4, cy - r*0.35)], fill=ink, width=max(3, w // 2))
        d.ellipse([cx + r*0.22, cy - r*0.4, cx + r*0.58, cy + r*0.05], outline=ink, width=max(3, w // 2))
    elif icon == "sword":
        d.polygon([(cx - r*0.75, cy + r*0.75), (cx + r*0.6, cy - r*0.6), (cx + r*0.85, cy - r*0.85), (cx + r*0.75, cy - r*0.45), (cx - r*0.6, cy + r*0.9)], fill=(200, 208, 220), outline=ink)
        d.line([(cx - r*0.85, cy + r*0.45), (cx - r*0.45, cy + r*0.95)], fill=gold, width=w)
        d.line([(cx - r*0.75, cy + r*0.75), (cx - r*0.95, cy + r*0.95)], fill=(120, 70, 40), width=w)
    elif icon == "question":
        f = ImageFont.truetype(FONT_CAP, int(r * 2.1)); tw = f.getlength("?")
        d.text((cx - tw / 2, cy - r * 1.45), "?", font=f, fill=gold, stroke_width=max(3, w // 2), stroke_fill=ink)
    elif icon == "tick":
        d.line([(cx - r*0.7, cy), (cx - r*0.2, cy + r*0.55), (cx + r*0.75, cy - r*0.6)], fill=green, width=int(w*1.6), joint="curve")
    elif icon == "cross":
        for a, b in (((-0.65, -0.65), (0.65, 0.65)), ((0.65, -0.65), (-0.65, 0.65))):
            d.line([(cx + a[0]*r, cy + a[1]*r), (cx + b[0]*r, cy + b[1]*r)], fill=red, width=int(w*1.6))
    elif icon == "coin":
        for k, (dx, dy) in enumerate(((-0.35, 0.3), (0.3, 0.35), (0, -0.2))):
            x, y = cx + dx*r, cy + dy*r
            d.ellipse([x - r*0.5, y - r*0.5, x + r*0.5, y + r*0.5], fill=gold, outline=(170, 110, 20), width=max(3, w // 2))
            d.ellipse([x - r*0.3, y - r*0.3, x + r*0.3, y + r*0.3], outline=(200, 140, 30), width=max(2, w // 3))
    elif icon == "door":
        d.rectangle([cx - r*0.55, cy - r*0.4, cx + r*0.55, cy + r], fill=(150, 90, 50), outline=ink, width=max(3, w // 2))
        d.pieslice([cx - r*0.55, cy - r*0.95, cx + r*0.55, cy + r*0.15], 180, 360, fill=(150, 90, 50), outline=ink, width=max(3, w // 2))
        d.ellipse([cx + r*0.25, cy + r*0.3, cx + r*0.4, cy + r*0.45], fill=gold)
    elif icon == "lamp":
        d.ellipse([cx - r*0.15, cy - r*0.95, cx + r*0.15, cy - r*0.2], fill=(255, 190, 60))
        d.ellipse([cx - r*0.07, cy - r*0.6, cx + r*0.07, cy - r*0.3], fill=(255, 245, 210))
        d.chord([cx - r*0.8, cy - r*0.5, cx + r*0.8, cy + r*0.7], 0, 180, fill=(190, 100, 50), outline=ink, width=max(3, w // 2))
    elif icon == "crown":
        d.polygon([(cx - r*0.8, cy + r*0.5), (cx - r*0.8, cy - r*0.4), (cx - r*0.4, cy), (cx, cy - r*0.7), (cx + r*0.4, cy), (cx + r*0.8, cy - r*0.4), (cx + r*0.8, cy + r*0.5)], fill=gold, outline=ink)
        d.ellipse([cx - r*0.12, cy + r*0.05, cx + r*0.12, cy + r*0.29], fill=red)
    elif icon == "clock":
        d.ellipse([cx - r*0.8, cy - r*0.8, cx + r*0.8, cy + r*0.8], fill=(255, 250, 235), outline=ink, width=w)
        d.line([(cx, cy), (cx, cy - r*0.55)], fill=ink, width=w); d.line([(cx, cy), (cx + r*0.4, cy + r*0.15)], fill=ink, width=w)

def make_card(icon, label):
    """Square card with an icon and a short caption under it (shown over a shot)."""
    k = 2; cw, ch = 300 * k, 330 * k
    img = Image.new("RGBA", (cw + 30*k, ch + 30*k), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    d.rounded_rectangle([18*k, 22*k, cw + 18*k, ch + 22*k], radius=34*k, fill=(0, 0, 0, 110))
    d.rounded_rectangle([8*k, 8*k, cw + 8*k, ch + 8*k], radius=34*k, fill=(250, 236, 205), outline=(226, 168, 66), width=8*k)
    _icon(d, icon, 8*k + cw / 2, 8*k + 125*k, 82*k)
    if label:
        f = fit(label, ImageFont.truetype(FONT_CAP, 40*k), 250*k); tw = f.getlength(label)
        d.text((8*k + (cw - tw) / 2, 8*k + 250*k), label, font=f, fill=(150, 24, 36))
    return img.resize((img.width // k, img.height // k), Image.LANCZOS)

def make_pill(text):
    font = ImageFont.truetype(FONT_B, 46); tw = font.getlength(text)
    img = Image.new("RGBA", (int(tw + 80), 96), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 8, tw + 80, 88], radius=40, fill=(15, 12, 20, 215), outline=(255, 255, 255, 230), width=3)
    d.text((40, 48 - font.size * 0.66), text, font=font, fill=(255, 255, 255))
    return img

def overlay(frame, im, cx, cy, scale, alpha):
    if alpha <= 0.01: return
    if abs(scale - 1) > 0.01:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BILINEAR)
    if alpha < 0.99:
        im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    frame.paste(im, (int(cx - im.width / 2), int(cy - im.height / 2)), im)

# ================================================================ frame render
TL = None
def worker_init(tl):
    global TL; TL = tl

def render_shot(si, t):
    s = TL["shots"][si]; t = max(0.0, t)
    img, cam = SHOT_FN[s["kind"]](t, s)
    z = cam["zoom"]; vw, vh = W / z, H / z
    x0 = clamp(cam["cx"] - vw / 2, 0, W - vw); y0 = clamp(cam["cy"] - vh / 2, 0, H - vh)
    fr = img.resize((W, H), Image.BILINEAR, box=(x0*S, y0*S, (x0 + vw)*S, (y0 + vh)*S), reducing_gap=2.0)
    v = fonts()["vig"]; fr.paste(v, (0, 0), v)
    return fr

def render_frame(fi):
    T = fi / FPS; shots = TL["shots"]
    CUR["talk"] = {}
    for ph in TL["phrases"]:
        if ph["start"] <= T < ph["end"]:
            i = int((T - ph["start"]) * FPS)
            if i < len(ph["env"]): CUR["talk"][ph["spk"]] = ph["env"][i]
    si = next((i for i, s in enumerate(shots) if T < s["end"]), len(shots) - 1); s = shots[si]
    frame = render_shot(si, T - s["start"])
    if si + 1 < len(shots) and T > s["end"] - XF:
        frame = Image.blend(frame, render_shot(si + 1, T - shots[si + 1]["start"]), ease_io((T - (s["end"] - XF)) / XF))
    for k, ph in enumerate(TL["phrases"]):
        if ph["start"] - 0.05 <= T <= ph["end"] + 0.3:
            key = ("cap", k)
            if key not in CACHE: CACHE[key] = make_caption(ph["text"], ph["spk"])
            a = T - ph["start"] + 0.05
            overlay(frame, CACHE[key], W / 2, 330 + CACHE[key].height / 2 - 100, lerp(0.6, 1.0, ease_back(a / 0.25)),
                    clamp(a / 0.1) * clamp((ph["end"] + 0.3 - T) / 0.2))
    if T < 2.6:
        if "title" not in CACHE: CACHE["title"] = make_title(TL["label"])
        overlay(frame, CACHE["title"], W / 2, 860, lerp(0.7, 1.0, ease_back((T - 0.1) / 0.4)), clamp((T - 0.1) / 0.2) * clamp((2.6 - T) / 0.35))
    last = shots[-1]; te = last["start"] + last["narr_end"] + 0.4
    if T >= te:
        if "end" not in CACHE: CACHE["end"] = make_end(TL["nxt"])
        a = T - te
        overlay(frame, CACHE["end"], W / 2, 720 if TL["nxt"] else 460, lerp(0.5, 1.0, ease_back(a / 0.35)) * (1 + 0.025*math.sin(a*6)*clamp(a - 0.4)), clamp(a / 0.15))
    if T > TL["total"] - 0.4:
        frame = Image.blend(frame, Image.new("RGB", (W, H), (0, 0, 0)), clamp((T - (TL["total"] - 0.4)) / 0.4))
    return frame

def render_bytes(fi): return render_frame(fi).tobytes()

# ================================================================ audio
def ffmpeg_exe():
    import imageio_ffmpeg; return imageio_ffmpeg.get_ffmpeg_exe()

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

def build_audio(tl, voices, path, seed):
    total = tl["total"]; n = int((total + 0.6) * SR)
    voice, bed, sfx = np.zeros(n), np.zeros(n), np.zeros(n)
    for ph in tl["phrases"]:
        x = voices[ph["idx"]]
        if ph["spk"] == "K": x = reverb(x)
        add(voice, ph["start"], x)
    if tl.get("type") == "paheli":   # slow minor pads: suspense
        prog = [[110, 164.81, 220, 261.63], [98, 146.83, 196, 233.08], [87.31, 130.81, 174.61, 207.65], [82.41, 123.47, 164.81, 207.65]]
        t0, i = 0.0, 0
        while t0 < total:
            add(bed, t0, pad(prog[i % 4], 4.0), 0.8); t0 += 4.0; i += 1
        bed += tanpura(n) * 0.3
    elif tl.get("type") == "motivational":
        prog = [[110, 220, 261.63, 329.63], [87.31, 174.61, 220, 261.63], [130.81, 261.63, 329.63, 392], [98, 196, 246.94, 293.66]]
        t0, i = 0.0, 0
        while t0 < total:
            add(bed, t0, pad(prog[i % 4], 4.0), 0.9); t0 += 4.0; i += 1
        bed += bansuri(n, seed) * 0.25
    else:
        bed += tanpura(n) * 0.55 + bansuri(n, seed) * 0.5
    rng = random.Random(seed)
    for si, s in enumerate(tl["shots"]):
        st, d, kd = s["start"], s["dur"], s["kind"]
        if si: add(sfx, st - 0.4, band(noise(0.8), 300, 3000) * np.hanning(int(0.8*SR)), 0.08)
        if kd in ("divine", "sun", "sunrise", "mountain"):
            add(bed, st, pad([146.83, 220, 293.66, 369.99], d), 0.7)
            for j, f in enumerate([587.33, 659.26, 739.99, 880, 987.77, 1174.66]):
                add(sfx, st + 0.1 + j*0.06, sweep(f, f, 1.2, 3.5), 0.06)
        if kd in ("walk", "meet", "farm", "seekh", "sunrise", "mountain"):
            tb = 0.6
            while tb < d:
                add(sfx, st + tb, chirp(), 0.045); add(sfx, st + tb + 0.17, chirp(), 0.04); tb += rng.uniform(1.4, 3.2)
            add(sfx, st, band(noise(d), 200, 900) * np.minimum(1, tarr(d) / 0.5), 0.02)
        walking = kd == "walk" or (kd == "meet" and (s.get("arrive") or "kwalk" in s))
        if walking or (kd == "farm" and s.get("mode") == "sow"):
            tw = 0.1; end = d if kd in ("walk", "farm") else 2.8
            while tw < end:
                tq = tarr(0.09); add(sfx, st + tw, band(noise(0.09), 60, 500) * np.exp(-tq*40), 0.07); tw += math.pi / 6.5
        if kd == "darbar":   # deep drum hit on every cut
            tq = tarr(1.2); add(sfx, st + 0.05, np.sin(2*np.pi*58*tq) * np.exp(-tq*4.5) * np.minimum(1, tq / 0.004), 0.35)
        if kd == "rain":
            r = band(noise(d + 0.6), 400, 6500) * np.minimum(1, tarr(d + 0.6) / 0.5) * np.clip((d + 0.6 - tarr(d + 0.6)) / 0.6, 0, 1)
            add(sfx, st, r, 0.14)
            tq = tarr(3.0); add(sfx, st + d*0.4 + 0.1, band(noise(3.0), 20, 220) * np.minimum(1, tq/0.08) * np.exp(-tq/0.9), 0.6)
        if kd == "night":
            tb = 0.3
            while tb < d:
                for q in range(3):
                    tq = tarr(0.035); add(sfx, st + tb + q*0.06, np.sin(2*np.pi*4300*tq) * np.hanning(len(tq)), 0.04)
                tb += 0.8
        if kd == "sun":
            k_at = st + 0.8 + d*0.55
            add(sfx, st + 0.8, sweep(200, 600, d*0.55, 0) * np.sin(np.pi*tarr(d*0.55)/(d*0.55)), 0.03)
            add(sfx, k_at - 0.2, bell(880, 3.0), 0.12)
        if kd == "farm" and s.get("mode") == "grow":
            add(sfx, st + d - 1.0, bell(1046, 2.5), 0.1)
    add(sfx, 0.12, bell(520), 0.4)
    last = tl["shots"][-1]; te = last["start"] + last["narr_end"] + 0.4
    add(sfx, te, bell(700, 3.0), 0.3)
    if tl.get("type") != "motivational":
        add(sfx, tl["phrases"][-1]["start"], bell(520), 0.35)
    # duck bed under voice
    a = np.abs(voice); k = int(0.25 * SR); cs = np.cumsum(np.concatenate([[0], a]))
    env = np.zeros(n); env[k//2: k//2 + n - k + 1] = (cs[k:] - cs[:-k]) / k
    bed *= 1 - 0.55 * np.clip(env / 0.05, 0, 1)
    bed *= np.clip((total - np.arange(n) / SR) / 1.8, 0, 1) * np.minimum(1, np.arange(n) / SR / 0.8)
    mix = voice * 1.0 + bed * 0.13 + sfx * 0.6
    mix /= max(1.0, np.max(np.abs(mix)) / 0.97)
    pcm = (np.clip(mix, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes(np.repeat(pcm[:, None], 2, axis=1).tobytes())

