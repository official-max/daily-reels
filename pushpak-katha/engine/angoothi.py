"""Sample 5 (puppets): Raja ki Angoothi, the old folk tale of "this too shall pass"."""
import random, sys
import numpy as np, skia
from math import sin, cos, pi
from puppet import *
import lab
from lab import main as run, W, H, SR, M, S, BLACK, au

lab.FPS = 60
_env = au.lip_env
def _lip(x):
    """Lip movement at 60 fps, without the frame-to-frame rattle."""
    e = np.array(_env(x)); n = len(e) * 2; e = np.interp(np.arange(n) / 2, range(len(e)), e); k = np.hanning(9); return list(np.convolve(e, k / k.sum(), "same"))
au.lip_env = _lip

CR = "kathputli"; ss = lambda u: (lambda v: v * v * (3 - 2 * v))(max(0., min(1., u)))
PAL = dict(a=(150, 30, 62), b=(246, 190, 70), c=(24, 104, 112))
def who(seed, role, pal, **k): return dict(person(random.Random(seed), role, CR, pal), **k)
KING = who(5, "raja", PAL, hat="crown", hatk=1.0, feather=1, must=3, beard=1, top=0, bottom="dhoti", prop=None, skin=(204, 142, 92), nose=26, jaw=84, wide=1.1, head=1.05, tilak=1, ear=1)
POOR = dict(KING, hat="none", feather=0, neck=0, top=1, prop=None)
QUEEN = who(8, "rani", dict(a=(206, 70, 120), b=(252, 208, 110), c=(60, 60, 130)), hat="veil", prop="lamp")
SAGE = who(3, "sage", dict(a=(214, 110, 40), b=(250, 210, 120), c=(236, 226, 200)), hat="jata", beard=3, prop="staff", top=1, bottom="dhoti", tilak=2)
ENEMY = who(11, "yoddha", dict(a=(50, 46, 66), b=(196, 160, 90), c=(120, 24, 34)), hat="helmet", must=3, beard=1, prop="sword", top=0)
SOLD = [who(20 + i, "yoddha", SETS[i], prop=["spear", "sword", "bow"][i], hat="helmet") for i in range(3)]
VILL = [who(31, "kisan", SETS[3], prop=None), who(37, "bala", SETS[6], prop=None)]

def stage(c, t, D, kind, time, seed, draw, z=(1., 1.06), at=(540, 1000), sh=0, curtain=0.):
    """One set: place, people, then the picture surface and the theatre curtain on top, which the camera does not move."""
    k = z[0] + (z[1] - z[0]) * ss(t / D); c.save(); c.translate(sin(t * 9) * sh, cos(t * 7) * sh); c.translate(*at); c.scale(k, k); c.translate(-at[0], -at[1])
    place(c, random.Random(seed), kind, time, PAL, t); front(c, random.Random(seed), kind, time, PAL); draw(); c.restore()
    surface(c, CR, PAL, random.Random(4))
    if curtain > 0:
        for s in (0, 1):
            w = 560 * curtain
            for i in range(8): x = i * w / 8; c.drawRect(skia.Rect.MakeXYWH(x if not s else W - x - w / 8, 0, w / 8 + 2, H), fill(mix(PAL["a"], (0, 0, 0), .12 + .3 * (i % 2))))
            c.drawRect(skia.Rect.MakeXYWH(w - 12 if not s else W - w, 0, 12, H), fill(PAL["b"]))
def petals(c, t, n=40):
    r = random.Random(9)
    for i in range(n):
        x, y, v = r.uniform(120, 960), r.uniform(0, H), r.uniform(120, 260); yy = (y + t * v) % H; c.save(); c.translate(x + sin(t * 2 + i) * 40, yy); c.rotate(t * 90 + i * 40); c.drawOval(skia.Rect.MakeXYWH(-12, -6, 24, 12), fill([(255, 190, 60), (230, 60, 90), (255, 240, 220)][i % 3])); c.restore()
def rain(c, t, n=90):
    r = random.Random(2)
    for i in range(n): x, y = r.uniform(0, W + 200), (r.uniform(0, H) + t * 1700) % H; c.drawLine(x, y, x - 22, y + 74, line((200, 220, 240), 3, .4))
def ring(c, x, y, s, t, openk=0.):
    c.save(); c.translate(x, y); c.scale(s, s); glow(c, 0, -40, 420, (255, 220, 130), .55 + .15 * sin(t * 4))
    for i in range(14): a = i * pi / 7 + t * .4; c.drawLine(cos(a) * 190, -40 + sin(a) * 190, cos(a) * (260 + 24 * sin(t * 5 + i)), -40 + sin(a) * (260 + 24 * sin(t * 5 + i)), line((255, 230, 150), 7, .7))
    q = oval(0, 40, 110); c.drawPath(q, line((60, 30, 16), 50)); c.drawPath(q, line((246, 190, 70), 36)); c.drawPath(q, line((255, 236, 160), 8))
    c.drawPath(poly([(-70, -60), (70, -60), (52, -110), (-52, -110)]), fill((246, 190, 70))); c.drawPath(poly([(-70, -60), (70, -60), (52, -110), (-52, -110)]), line((60, 30, 16), 8))
    c.save(); c.translate(52, -108); c.rotate(100 * openk); c.translate(-52, 108); g = poly([(-56, -108), (56, -108), (34, -170), (-34, -170)]); c.drawPath(g, fill((214, 30, 60))); c.drawPath(poly([(-20, -108), (0, -170), (20, -108)]), fill((255, 110, 130))); c.drawPath(g, line((60, 30, 16), 8)); c.restore()
    c.restore()
def hand(c, x, y, s, skin):
    c.save(); c.translate(x, y); c.scale(s, s); p = KING
    put(c, poly([(-900, 120), (-300, 40), (-300, 220), (-900, 380)]), PAL["c"], p, 8); put(c, poly([(-330, 24), (-270, 20), (-266, 236), (-326, 244)]), PAL["b"], p, 8)
    put(c, smooth([(-290, 50), (-120, 10), (60, 30), (230, 40), (250, 90), (120, 110), (240, 130), (230, 176), (80, 172), (-60, 220), (-290, 220)]), skin, p, 8); put(c, smooth([(-170, 40), (-80, -50), (-20, -60), (-10, -10), (-70, 50)]), skin, p, 8); c.restore()
def scroll(c, t, D, warm):
    u = ss(t / .5); c.save(); c.translate(540, 860); c.scale(.9, .9); c.rotate(sin(t * 1.5) * 1.5); glow(c, 0, 0, 760, warm, .6); w = 60 + 340 * u
    c.drawRect(skia.Rect.MakeLTRB(-w, -230, w, 230), fill((247, 230, 186))); c.drawRect(skia.Rect.MakeLTRB(-w, -230, w, 230), line((120, 70, 30), 8)); c.drawRect(skia.Rect.MakeLTRB(-w + 24, -206, w - 24, 206), line((200, 150, 80), 4))
    for x in (-w, w): c.drawRoundRect(skia.Rect.MakeLTRB(x - 28, -270, x + 28, 270), 20, 20, fill((132, 64, 34))); c.drawCircle(x, -280, 26, fill(PAL["b"])); c.drawCircle(x, 280, 26, fill(PAL["b"]))
    f = skia.Font(skia.Typeface.MakeFromFile(BLACK), 92); c.save(); c.clipRect(skia.Rect.MakeLTRB(-w + 30, -200, w - 30, 200))
    for i, s in enumerate(("Yeh samay", "bhi beet", "jayega")):
        if u > .4: c.drawString(s, -f.measureText(s) / 2, -78 + i * 114, f, fill((120, 24, 40), ss((t - .3 - i * .25) / .3)))
    c.restore(); c.restore()

def s_open(c, t, D, tk, T): stage(c, t, D, "palace", "dusk", 7, lambda: (puppet(c, QUEEN, 800, 1540, 1.08, T, -1, 0, "n", (.5, 1.6)), puppet(c, KING, 350, 1560, 1.24, T, 1, 0, "sad", (.2, 2.2))), (1.0, 1.1), curtain=1 - ss((t - .2) / 1.1))
def s_ask(c, t, D, tk, T): stage(c, t, D, "ghat", "gold", 12, lambda: (puppet(c, SAGE, 790, 1560, 1.18, T, -1, 0, "n", (.3, 1.2)), puppet(c, KING, 320, 1560, 1.2, T, 1, tk.get("K", 0), "sad", (1.0 + .1 * sin(T * 4), 2.0))), (1.0, 1.1), (540, 1050))
def s_give(c, t, D, tk, T): stage(c, t, D, "ghat", "gold", 12, lambda: (puppet(c, dict(SAGE, prop=None), 640, 2030, 1.75, T, -1, tk.get("S", 0), "n", (.7, 2.0 + .15 * sin(T * 3))), ring(c, 205, 1000 + 10 * sin(T * 3), .55, T)), (1.0, 1.08), (500, 950))
def s_war(c, t, D, tk, T):
    def d():
        for i, p in enumerate(SOLD): puppet(c, p, 120 + i * 150 + 30 * sin(T * 2.4 + i), 1410, .72, T + i, 1, 0, "angry", (1.4 + .5 * sin(T * 3.6 + i), 2.2), False, walk=.5)
        for i in range(3): puppet(c, dict(ENEMY, prop=["spear", "sword", "sword"][i]), 700 + i * 140 - 30 * sin(T * 2.6 + i), 1430, .74, T + i, -1, 0, "angry", (1.4 + .5 * sin(T * 3.8 + i), 2.4), False, walk=.5)
        puppet(c, dict(KING, prop="sword"), 310 - 40 * ss(t / D), 1640, 1.2, T, 1, 0, "angry" if t < D * .5 else "sad", (1.3 + .5 * sin(T * 4), 2.2 + .3 * sin(T * 4 - .6)), walk=.35); puppet(c, ENEMY, 840 - 90 * ss(t / D), 1640, 1.25, T, -1, 0, "angry", (1.5 + .7 * sin(T * 4 + 2), 2.6 + .3 * sin(T * 4 + 1.4)), walk=.35)
        h = max(0, sin(T * 4 + 1)) ** 8; x, y = 570, 1020
        for i in range(10): a = i * pi / 5; c.drawLine(x + cos(a) * 30, y + sin(a) * 30, x + cos(a) * 110, y + sin(a) * 110, line((255, 240, 160), 9, h))
    stage(c, t, D, "battle", "dusk", 21, d, (1.05, 1.15), sh=1.2)
def s_flee(c, t, D, tk, T): v = 1500 / D; stage(c, t, D, "forest", "storm", 33, lambda: (puppet(c, POOR, -190 + v * t, 1580, 1.05, t, 1, 0, "sad", (.9 + .5 * sin(t * pi * v / 1.05 / 220), 1.9 + .4 * sin(t * pi * v / 1.05 / 220 - .5)), walk=1.7, pace=v), rain(c, T)), (1.08, 1.12), (540, 1100))
def s_lost(c, t, D, tk, T): stage(c, t, D, "forest", "storm", 34, lambda: (puppet(c, POOR, 470, 2120, 1.8, T, 1, tk.get("K", 0), "sad", (.6, 2.7 + .06 * sin(T * 3))), rain(c, T)), (1.0, 1.12), (560, 900))
def s_opening(c, t, D, tk, T): stage(c, t, D, "forest", "night", 35, lambda: (glow(c, 560, 900, 800, (255, 210, 120), .35), ring(c, 560, 860, 1.25, T, ss((t - D * .4) / .5)), hand(c, 500, 1000, 1.15, KING["skin"])), (1.0, 1.15), (560, 900))
def s_note(c, t, D, tk, T): stage(c, t, D, "forest", "night", 35, lambda: scroll(c, t, D, (255, 214, 130)), (1.0, 1.08), (540, 860))
def s_hope(c, t, D, tk, T):
    def d():
        for i, p in enumerate(SOLD + VILL): puppet(c, p, -260 + i * 150 + 260 * t / D, 1400, .76, T + i * .3, 1, 0, "happy", (2.2 + .3 * sin(T * 3 + i), 2.8), False, walk=1, pace=260 / D)
        puppet(c, dict(KING, prop="sword"), 340 + 300 * t / D, 1620, 1.28, T, 1, 0, "happy", (2.3 + .12 * sin(T * 3), 2.8 + .1 * sin(T * 3 - .6)), walk=1, pace=300 / D)
    stage(c, t, D, "desert", "dawn", 41, d, (1.0, 1.08))
def s_jashn(c, t, D, tk, T):
    def d():
        for i, p in enumerate(VILL + [SOLD[0], QUEEN]): puppet(c, dict(p, prop=None), [190, 400, 690, 880][i], 1420 - (.5 - .5 * cos(T * 6 + i)) * 30, .78, T + i, 1 if i < 2 else -1, 0, "happy", (2.4 + .4 * sin(T * 3 + i), 2.9 + .15 * sin(T * 3 + i - .6)), False)
        puppet(c, KING, 520, 1640 - (.5 - .5 * cos(T * 5)) * 20, 1.25, T, 1, 0, "happy", (2.0 + .3 * sin(T * 2.5), 2.7 + .12 * sin(T * 2.5 - .6))); petals(c, T)
    stage(c, t, D, "palace", "gold", 52, d, (1.0, 1.08))
def s_proud(c, t, D, tk, T): stage(c, t, D, "palace", "gold", 52, lambda: (glow(c, 520, 800, 700, (255, 210, 90), .6), puppet(c, KING, 450, 2080, 1.75, T, 1, tk.get("K", 0), "happy", (1.5 + .1 * sin(T * 2.5), 2.7 + .12 * sin(T * 2.5 - .6))), petals(c, T, 24)), (1.0, 1.15), (540, 900))
def s_again(c, t, D, tk, T): stage(c, t, D, "palace", "dusk", 7, lambda: (puppet(c, KING, 290, 1560, 1.2, T, 1, 0, "n" if t < D * .6 else "sad", (.3, 1.3)), puppet(c, dict(SAGE, prop="mala"), 810, 1560, 1.2, T, -1, tk.get("S", 0), "n", (1.0, 1.8 + .1 * sin(T * 3)))), (1.05, 1.15), (560, 1050))
def s_note2(c, t, D, tk, T): stage(c, t, D, "palace", "dusk", 7, lambda: scroll(c, t, D, (255, 170, 120)), (1.0, 1.08), (540, 860))
def s_moral(c, t, D, tk, T):
    u = ss((t - D + 4.2) / 1.0); a = lambda x, y: x + (y - x) * u
    stage(c, t, D, "ghat", "night", 60, lambda: (puppet(c, dict(SAGE, prop=None), 810, 1540, 1.1, T, -1, 0, "happy", (a(.5, .55), a(1.4, 2.5))), puppet(c, KING, 300, 1560, 1.16, T, 1, 0, "happy", (a(.9, .55), a(2.0, 2.5))), petals(c, T, int(40 * u))), (1.1, 1.0), (540, 1000), curtain=ss((t - D + 2.6) / 1.5))

N, K, R = (M, "+4%", "-2Hz"), (M, "+6%", "+10Hz"), (M, "-8%", "-22Hz")
def L(shot, w, v, hi, ro, **k): return dict(shot=shot, who=w, v=v, hi=hi, ro=ro, **k)
LINES = [
 L("open", "N", N, "एक राजा के पास सब कुछ था, पर मन में चैन नहीं।", "Ek *raja* ke paas sab kuch tha, par mann mein *chain* nahi.", pad=.4),
 L("ask", "K", K, "ऋषिवर, ऐसा मंत्र दीजिए, जो हर हाल में काम आए।", "Rishivar, aisa *mantra* dijiye, jo *har* *haal* mein kaam aaye."),
 L("give", "S", R, "वो इस अँगूठी में है। पर तभी खोलना, जब कोई रास्ता न बचे।", "Woh is *angoothi* mein hai. Par tabhi kholna, jab koi *raasta* na bache.", pad=.4),
 L("war", "N", N, "फिर दुश्मन ने हमला किया, और राजा सब कुछ हार गया।", "Phir dushman ne *hamla* kiya, aur raja sab kuch *haar* gaya."),
 L("flee", "N", N, "जान बचाकर, वो अकेला जंगल में भागा।", "Jaan bachakar, woh *akela* jungle mein *bhaaga.*"),
 L("lost", "K", (M, "-10%", "+6Hz"), "अब तो सब खत्म हो गया।", "Ab toh sab *khatam* ho gaya.", pad=.5),
 L("opening", "N", N, "तभी उसे अँगूठी याद आई। उसने उसे खोला।", "Tabhi use *angoothi* yaad aayi. Usne use *khola.*", pad=.4),
 L("note", "S", R, "यह समय भी बीत जाएगा।", "Yeh *samay* bhi *beet* jayega.", pad=.9),
 L("hope", "N", N, "हिम्मत लौट आई। उसने फिर सेना जोड़ी, और राज्य वापस जीत लिया।", "*Himmat* laut aayi. Usne phir sena jodi, aur rajya wapas *jeet* liya."),
 L("jashn", "N", N, "जीत का जश्न हुआ, और राजा में घमंड आ गया।", "Jeet ka *jashn* hua, aur raja mein *ghamand* aa gaya."),
 L("proud", "K", K, "अब मुझे कोई नहीं हरा सकता!", "Ab mujhe *koi* nahi *hara* sakta!"),
 L("again", "S", R, "महाराज, अँगूठी फिर से पढ़िए।", "Maharaj, angoothi *phir* se padhiye.", pad=.4),
 L("note2", "S", R, "यह समय भी बीत जाएगा।", "Yeh *samay* bhi *beet* jayega.", pad=.8),
 L("moral", "N", N, "दुख हो या सुख, याद रखना, कुछ भी हमेशा नहीं रहता।", "*Dukh* ho ya *sukh,* yaad rakhna, kuch bhi *hamesha* nahi rehta.", pad=4.6),
]
SH = {k[2:]: v for k, v in list(globals().items()) if k.startswith("s_")}

def pluck(f, d=.9):
    q = au.tarr(d); return sum(np.sin(2 * pi * f * h * q + .3 * np.sin(2 * pi * 5 * q)) * np.exp(-q * (3 + h * 1.6)) / h for h in (1, 2, 3, 4, 5))
def mus(n, tl):
    """Tanpura drone, sarangi-like plucked raga line and a dholak."""
    b = np.zeros(n); q = np.arange(n) / SR
    for f, a in ((110, .3), (165, .2), (220, .15)): b += a * np.sin(2 * pi * f * q) * (1 + .4 * np.sin(2 * pi * .5 * q + f))
    sc = [220, 247.5, 277.2, 330, 366.7, 440, 495]; r = random.Random(6); i = 3; t = .2; k = 0
    while t < tl["total"]:
        if k % 8 != 7: i = max(0, min(6, i + r.choice([-1, -1, 1, 1, 2, -2]))); au.add(b, t, pluck(sc[i]), .34)
        if k % 2 == 0 or k % 8 in (3, 7): h = au.tarr(.3); au.add(b, t, np.sin(2 * pi * np.cumsum(75 + 60 * np.exp(-h * 30)) / SR) * np.exp(-h * 13), .7 if k % 4 == 0 else .35)
        if k % 2: h = au.tarr(.1); au.add(b, t, np.sin(2 * pi * 420 * h) * np.exp(-h * 45), .3)
        t += .3; k += 1
    return b
def fx(f, tl):
    for l in tl["lines"]:
        s, D = l["start"], l["end"] - l["start"]
        if s > 0: au.add(f, s - .2, au.band(au.noise(.5), 400, 4000) * np.hanning(int(.5 * SR)), .1)
        if l["shot"] in ("flee", "lost"): x = au.band(au.noise(D), 800, 6000); au.add(f, s, x * np.hanning(len(x)) ** .2, .12)
        if l["shot"] == "flee": x = au.band(au.noise(1.6), 40, 300); au.add(f, s + .2, x * np.exp(-au.tarr(1.6) * 2), .9)
        if l["shot"] == "war":
            for j in range(int(D / .9)): x = au.tarr(.5); au.add(f, s + .3 + j * .9, (np.sin(2 * pi * 2300 * x) + np.sin(2 * pi * 3470 * x)) * np.exp(-x * 14), .2)
        if l["shot"] in ("give", "opening"): au.add(f, s + D * .4, au.bell(1040, 1.6), .35)
        if l["shot"] in ("note", "note2"): au.add(f, s + .05, au.bell(520, 2.2), .5)
        if l["shot"] == "jashn":
            for j, w in enumerate((440, 554, 660, 880)): au.add(f, s + .1 + j * .12, au.sweep(w, w, .9, 4), .25)
if __name__ == "__main__": run("angoothi", LINES, SH, ("RAJA KI", "ANGOOTHI"), mus, fx)
