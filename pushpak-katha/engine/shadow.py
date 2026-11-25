"""Sample 3: Baatuni Kachhua (Panchatantra), shadow-theatre silhouette cartoon."""
from lab import *
from lab import main as run
sin, cos, pi = math.sin, math.cos, math.pi
def clamp(x, a=0., b=1.): return max(a, min(b, x))
def ease(u): u = clamp(u); return u * u * (3 - 2 * u)
K = (14, 8, 22)
SKY = dict(dawn=((44, 36, 92), (210, 96, 120), (255, 190, 120)), dry=((150, 40, 20), (236, 110, 30), (255, 206, 90)), sunset=((52, 22, 84), (216, 70, 86), (255, 176, 84)),
           dusk=((20, 18, 60), (110, 50, 120), (250, 130, 100)), night=((6, 10, 34), (20, 34, 84), (60, 80, 140)))

def sky(c, k, T, sun=(540, 800, 190), suncol=(255, 236, 180), stars=0):
    a, b, d = SKY[k]; vgrad(c, [(0, a), (.5, b), (.8, d), (1, d)]); r = random.Random(2)
    for i in range(stars): c.drawCircle(r.random() * W, r.random() * 1300, r.uniform(1.5, 4), fill((255, 255, 255), .5 + .5 * sin(T * 2 + i)))
    glow(c, sun[0], sun[1], sun[2] * 3.4, suncol, .6); c.drawCircle(*sun, fill(suncol))

def hills(c, T, layers, scroll=0.):
    for k, (base, amp, cc, sp) in enumerate(layers):
        pts = [(x, base + amp * sin((x + scroll * sp) * .004 + k * 1.7) + amp * .45 * sin((x + scroll * sp) * .0097 + k * 3) + amp * .15 * sin((x + scroll * sp) * .031)) for x in range(-20, W + 40, 12)]
        c.drawPath(poly([(-20, H)] + pts + [(W + 40, H)]), fill(cc))

def motes(c, T, rgb=(255, 220, 150), up=True):
    r = random.Random(8)
    for i in range(46):
        x0, ph, sp, s = r.random() * W, r.random(), r.uniform(.03, .08), r.uniform(2, 5); u = (ph + T * sp) % 1; c.drawCircle(x0 + 30 * sin(T + i), H * (1 - u if up else u), s, fill(rgb, .8 * sin(pi * u), 1.5))

def s_turtle(c, x, y, s, T, d=1, open_=0., rot=0., hang=False, eye=True):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s * d, s); p = fill(K)
    c.drawPath(smooth([(-150, 0), (-165, -70), (-90, -150), (20, -155), (110, -95), (135, 0), (0, 22)]), p)
    sw = sin(T * (9 if hang else 2)) * (14 if hang else 4)
    for lx in (-96, 76): c.drawPath(smooth([(lx - 26, -6), (lx + 26, -6), (lx + 22 + sw, 62), (lx - 18 + sw, 62)]), p)
    c.drawPath(smooth([(-140, -18), (-200, 6 + sw), (-140, 8)]), p)
    nx, ny = (150, -100) if hang else (170, -60 + sin(T * 1.7) * 6)
    q = line(K, 46); c.drawPath(smooth([(100, -30), (135, -30), (nx, ny)], False), q)
    c.save(); c.translate(nx, ny); c.rotate(-60 if hang else 0); c.drawPath(oval(14, -6, 50, 40), p)
    if open_ > .05: c.drawPath(poly([(30, 4), (84, -6 - 22 * open_), (84, 14 + 26 * open_)]), fill((255, 196, 110)))
    if eye: c.drawCircle(24, -16, 9, fill((255, 240, 200))); c.drawCircle(27, -15, 4, fill(K))
    c.restore()
    for hx, hy in ((-70, -70), (10, -85), (70, -50)): c.drawPath(poly([(hx + 30 * cos(i * pi / 3), hy + 24 * sin(i * pi / 3)) for i in range(6)]), line((255, 190, 120), 4, .28))
    c.restore()

def goose(c, x, y, s, T, d=1, fly=True, ph=0., head=0.):
    c.save(); c.translate(x, y); c.scale(s * d, s); p = fill(K); f = sin(T * 7 + ph)
    if fly:
        c.translate(0, -f * 14); w = skia.Path(); tip = -200 * f
        for dx, k in ((-18, .85), (10, 1)):
            c.drawPath(smooth([(-50 + dx, -8), (-70 + dx, tip * .6 * k - 20), (-150 + dx, tip * k - 8), (-190 + dx, tip * k + 24), (-80 + dx, tip * .35 * k + 20), (40 + dx, 6)]), p)
        c.drawPath(smooth([(-150, -6), (-90, -36), (40, -34), (110, -8), (40, 34), (-80, 30), (-200, 12)]), p)
        c.drawPath(smooth([(80, -10), (150, -30), (214, -52 + head)], False), line(K, 26)); c.drawPath(oval(226, -56 + head, 28, 20), p)
        c.drawPath(poly([(244, -66 + head), (292, -52 + head), (244, -46 + head)]), fill((230, 120, 40))); c.drawCircle(232, -62 + head, 4, fill((255, 240, 200)))
    else:
        for lx in (-14, 22): c.drawLine(lx, 0, lx + 4, 80, line(K, 8)); c.drawLine(lx + 4, 80, lx + 28, 82, line(K, 8))
        c.drawPath(smooth([(-130, -50), (-60, -78), (60, -70), (96, -20), (40, 26), (-60, 20)]), p); n = sin(T * 2 + ph) * 8
        c.drawPath(smooth([(64, -36), (110, -90), (84, -160), (112, -206 + n)], False), line(K, 28)); c.drawPath(oval(122, -212 + n, 30, 22), p)
        c.drawPath(poly([(142, -224 + n), (194, -208 + n), (142, -200 + n)]), fill((230, 120, 40))); c.drawCircle(128, -218 + n, 5, fill((255, 240, 200)))
    c.restore()

def reeds(c, T, n, y, seed, hh=260):
    r = random.Random(seed)
    for i in range(n):
        x = r.random() * W; h = r.uniform(.5, 1) * hh; sw = sin(T * 1.3 + x) * 16; c.drawPath(smooth([(x, y), (x + sw * .3, y - h * .6), (x + sw, y - h)], False), line(K, 7))
        if i % 3 == 0: c.drawPath(oval(x + sw, y - h - 26, 9, 34), fill(K))
def btree(c, x, y, s, T, leaf=True):
    def br(x0, y0, a, l, w, n):
        x1, y1 = x0 + cos(a) * l, y0 + sin(a) * l; c.drawLine(x0, y0, x1, y1, line(K, w))
        if n:
            for da in (-.5, .12, .55): br(x1, y1, a + da + sin(T * .8 + n) * .015, l * .72, w * .62, n - 1)
        elif leaf: c.drawCircle(x1, y1, 34 * s, fill(K, .95))
    br(x, y, -pi / 2, 210 * s, 44 * s, 4)
def zoom(c, z, x=540, y=960): c.translate(540, 960); c.scale(z, z); c.translate(-x, -y)
def carry(c, x, y, s, T, gap=300):
    """Two geese holding a stick with their feet."""
    b = sin(T * 7) * 8 * s; c.drawLine(x - (gap + 50) * s, y + b, x + (gap + 50) * s, y + b, line(K, 14 * s))
    for gx, ph in ((-gap, 0), (gap, .6)):
        for k in (-16, 10): c.drawLine(x + (gx + k) * s, y - 60 * s, x + (gx + k + 6) * s, y + b, line(K, 8 * s))
        goose(c, x + gx * s, y - 84 * s, .85 * s, T, 1, ph=ph)
    return b

def trio(c, x, y, s, T, open_=0.):
    """Two geese carrying the stick, the turtle hanging in the middle."""
    b = carry(c, x, y, s, T)
    s_turtle(c, x - 95 * s, y + 84 * s + b, .66 * s, T, 1, open_, sin(T * 3) * 4, hang=True)

def s_lake(c, t, D, tk, T):
    zoom(c, 1 + .07 * ease(t / D)); sky(c, "dawn", T, (700, 860, 150)); hills(c, T, [(1050, 70, (120, 60, 110), 0), (1130, 50, (70, 36, 84), 0)])
    vgrad(c, [(0, (255, 176, 120)), (1, (70, 40, 96))], 1180, H); r = random.Random(4)
    for i in range(34):
        y = 1190 + r.random() * 560; w = r.uniform(30, 180); x = 700 + r.uniform(-260, 260) + 20 * sin(T * 1.5 + i); c.drawRoundRect(skia.Rect.MakeLTRB(x - w, y, x + w, y + 7), 4, 4, fill((255, 226, 170), .5))
    c.drawPath(smooth([(60, 1420), (200, 1300), (460, 1290), (600, 1400), (560, 1470), (80, 1470)]), fill(K)); s_turtle(c, 320, 1260, 1.0, T, 1, .5 + .5 * sin(T * 11) if tk.get("N", 0) > 0 else 0)
    goose(c, 790, 1330, 1.0, T, -1, fly=False); goose(c, 950, 1370, .85, T, -1, fly=False, ph=1.2); reeds(c, T, 26, 1900, 5, 420); motes(c, T)
def s_dry(c, t, D, tk, T):
    zoom(c, 1 + .08 * ease(t / D)); sky(c, "dry", T, (540, 640, 240), (255, 246, 200)); hills(c, T, [(1120, 50, (170, 60, 24), 0)]); vgrad(c, [(0, (150, 60, 26)), (1, (60, 20, 18))], 1200, H)
    r = random.Random(6)
    for i in range(26):
        x, y = r.random() * W, 1230 + r.random() * 640; pts = [(x, y)]
        for k in range(4): x += r.uniform(-80, 80); y += r.uniform(-16, 40); pts.append((x, y))
        c.drawPath(poly(pts, False), line((40, 12, 14), 6, .8))
    btree(c, 930, 1330, .9, T, leaf=False); s_turtle(c, 300, 1390, .95, T, 1); goose(c, 690, 1330, 1.0, T, -1, fly=False); goose(c, 860, 1360, .85, T, -1, fly=False, ph=1); motes(c, T, (255, 200, 110))
def s_stick(c, t, D, tk, T):
    zoom(c, 1.12 + .08 * ease(t / D), 540, 1050); c.clear(col(K)); sky(c, "dry", T, (540, 820, 320), (255, 240, 190)); c.drawRect(skia.Rect.MakeLTRB(-100, 1360, W + 100, H), fill(K))
    goose(c, 200, 1290, 1.15, T, 1, fly=False); goose(c, 890, 1290, 1.15, T, -1, fly=False, ph=1.1); y = 1035 + sin(T * 2) * 8; c.drawLine(250, y, 850, y, line(K, 20)); s_turtle(c, 520, 1290, .8, T, 1); motes(c, T)
def clouds(c, T, sc, a=.35, rgb=(255, 210, 170)):
    for i in range(6):
        x = (i * 330 - sc) % 1980 - 400; y = 420 + (i * 271) % 900
        for dx, dy, r in ((-110, 20, 60), (0, 0, 90), (120, 16, 66)): c.drawOval(skia.Rect.MakeLTRB(x + dx - r * 1.5, y + dy - r * .6, x + dx + r * 1.5, y + dy + r * .6), fill(rgb, a, 18))
def s_fly(c, t, D, tk, T):
    zoom(c, 1 + .05 * ease(t / D)); sky(c, "sunset", T, (700, 900, 230), (255, 230, 170)); clouds(c, T, T * 60); hills(c, T, [(1290, 130, (150, 50, 96), .2), (1440, 110, (90, 28, 78), .45), (1620, 90, (40, 14, 48), 1)], T * 260)
    trio(c, 530, 900 + 40 * sin(T * 1.1), 1.0, T); motes(c, T, (255, 220, 170))
def person(c, x, y, s, T, k):
    a = -1.0 - .25 * sin(T * 5 + k); p = fill(K); c.drawCircle(x, y - 190 * s, 34 * s, p); c.drawPath(smooth([(x - 46 * s, y - 150 * s), (x + 46 * s, y - 150 * s), (x + 60 * s, y), (x - 60 * s, y)]), p)
    c.drawLine(x + 24 * s, y - 130 * s, x + 24 * s + cos(a) * 130 * s, y - 130 * s + sin(a) * 130 * s, line(K, 22 * s)); c.drawLine(x - 26 * s, y - 130 * s, x - 60 * s, y - 60 * s, line(K, 22 * s))
def s_village(c, t, D, tk, T):
    zoom(c, 1 + .05 * ease(t / D)); sky(c, "dusk", T, (300, 980, 170), (255, 214, 150), 30); hills(c, T, [(1120, 60, (120, 56, 120), 0), (1230, 30, (92, 40, 100), 0)])
    for x, w, h in ((60, 210, 190), (330, 170, 150), (760, 190, 170), (1000, 220, 210)):
        c.drawRect(skia.Rect.MakeLTRB(x - w / 2, 1330 - h, x + w / 2, 1400), fill((58, 26, 74))); c.drawPath(poly([(x - w * .66, 1330 - h), (x, 1330 - h - 120), (x + w * .66, 1330 - h)]), fill((44, 18, 58))); c.drawRect(skia.Rect.MakeLTRB(x - 22, 1240, x + 22, 1290), fill((255, 190, 90)))
    c.drawRect(skia.Rect.MakeLTRB(-50, 1380, W + 50, H + 80), fill((92, 40, 84))); c.drawRect(skia.Rect.MakeLTRB(-50, 1430, W + 50, H + 80), fill(K))
    for i, (x, s) in enumerate(((150, .9), (300, 1.05), (470, .8), (640, 1.0), (820, .9))): person(c, x, 1440 - abs(sin(T * 6 + i)) * 14, s, T, i)
    trio(c, 250 + 330 * t / D, 640 + 24 * sin(T * 1.3), .8, T)
def s_face(c, t, D, tk, T):
    zoom(c, 1.9 + .5 * ease(t / D), 500, 1030); sky(c, "sunset", T, (560, 1000, 260), (255, 226, 160)); clouds(c, T, T * 90); trio(c, 540, 940, 1.0, T, clamp((t - D * .72) / (D * .2)))
def s_fall(c, t, D, tk, T):
    u = clamp(t / D); zoom(c, 1); sky(c, "dusk", T, (540, 700, 210), (255, 214, 160), 40); hills(c, T, [(1560 - 60 * u, 70, (60, 26, 80), .2), (1700 - 90 * u, 50, K, .5)])
    b = 520 - 300 * u; carry(c, 540, b + 40, .9, T)
    y = 640 + 1050 * u * u
    for i in range(6): c.drawLine(440 + i * 45, y - 360 - (i * 37) % 120, 440 + i * 45, y - 200, line((255, 230, 200), 5, .5 * u))
    s_turtle(c, 550, y, .75, T, 1, 1, u * 380)
def s_moon(c, t, D, tk, T):
    zoom(c, 1 + .08 * ease(t / D)); sky(c, "night", T, (540, 740, 260), (240, 240, 220), 110); clouds(c, T, T * 30, .25, (120, 140, 200)); hills(c, T, [(1380, 80, (22, 30, 74), .1), (1520, 60, (12, 14, 40), .3), (1660, 40, K, .6)], T * 60)
    x = 140 + 420 * t / D; carry(c, x + 120, 840, .72, T, 280); reeds(c, T, 30, 1920, 9, 260); motes(c, T, (200, 220, 255))

N, G, P = (M, "-4%", "-6Hz"), (S, "+2%", "+0Hz"), (S, "+8%", "+14Hz")
def L(shot, who, v, hi, ro, **k): return dict(shot=shot, who=who, v=v, hi=hi, ro=ro, **k)
LINES = [
 L("lake", "N", N, "एक झील में रहता था एक कछुआ, जो कभी चुप नहीं रहता था।", "Ek jheel mein rehta tha ek *kachhua,* jo kabhi *chup* *nahi* rehta tha."),
 L("dry", "N", N, "एक साल झील सूख गई। तब उसके दो हंस दोस्त बोले,", "Ek saal jheel *sookh* gayi. Tab uske do *hans* dost bole,", pad=.15),
 L("stick", "G", G, "इस लकड़ी को मुँह से पकड़ लो, हम तुम्हें उड़ा ले चलेंगे। पर याद रहे, मुँह मत खोलना!", "Is *lakdi* ko munh se pakad lo, hum tumhein *uda* le chalenge. Par yaad rahe, *munh* *mat* *kholna!*"),
 L("fly", "N", N, "और वो उड़ चले। पहाड़ों के ऊपर, बादलों के पार।", "Aur woh *udd* chale. *Pahaadon* ke upar, *baadalon* ke paar.", pad=.6),
 L("village", "P", P, "अरे देखो देखो! उड़ता हुआ कछुआ! हा हा हा!", "Arre dekho dekho! *Udta* hua *kachhua!* Ha ha ha!"),
 L("face", "N", N, "कछुए से रहा नहीं गया। जवाब देने के लिए, उसने मुँह खोला...", "Kachhue se *raha* nahi gaya. Jawab dene ke liye, usne *munh* *khola...*", pad=.35),
 L("fall", "N", N, "और बस... वहीं सब ख़त्म।", "Aur bas... wahin sab *khatam.*", pre=.9, pad=.5),
 L("moon", "N", N, "कभी कभी, चुप रहना ही, सबसे बड़ी समझदारी है।", "Kabhi kabhi, *chup* rehna hi, sabse badi *samajhdaari* hai.", pad=1.3),
]
SH = {k[2:]: v for k, v in list(globals().items()) if k.startswith("s_") and k != "s_turtle"}
def music(n, tl): return au.tanpura(n, .89) * .5 + au.bansuri(n, 12, .89) * .6
def fxs(fx, tl):
    for l in tl["lines"]:
        if l["start"] > 0: au.add(fx, l["start"] - .35, au.band(au.noise(.8), 300, 2500) * np.hanning(int(.8 * SR)), .1)
        if l["shot"] in ("fly", "village", "moon"):
            t = l["start"]
            while t < l["end"]: au.add(fx, t, au.band(au.noise(.25), 150, 900) * np.hanning(int(.25 * SR)), .12); t += .9
        if l["shot"] == "fall": au.add(fx, l["start"], au.sweep(1200, 160, l["end"] - l["start"], 1.0), .25); au.add(fx, l["end"] - .25, au.sweep(70, 40, 1.0, 4), .9)
        if l["shot"] == "moon": au.add(fx, l["start"], au.bell(440), .3)

if __name__ == "__main__": run("shadow", LINES, SH, ("PANCHATANTRA", "BAATUNI KACHHUA"), music, fxs)
