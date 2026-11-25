"""Sample 2: Khargosh aur Kachhua, outlined 2D cartoon (all characters drawn here)."""
from lab import *
from lab import main as run
sin, cos, pi = math.sin, math.cos, math.pi
def clamp(x, a=0., b=1.): return max(a, min(b, x))
def ease(u): u = clamp(u); return u * u * (3 - 2 * u)

def eye(c, x, y, r, look=(0, 0), t=0, mood="n", off=0):
    ph = (t + off) % 3.1; open_ = .1 if ph < .12 and mood != "shock" else 1
    if mood == "sleep" or mood == "happy":
        p = skia.Path(); p.moveTo(x - r, y); p.quadTo(x, y + (r if mood == "sleep" else -r * 1.2), x + r, y); c.drawPath(p, line(INK, 8)); return
    ry = r * 1.25 * open_ * (1.15 if mood == "shock" else 1)
    c.save(); o = oval(x, y, r, ry); c.drawPath(o, fill((255, 255, 255))); c.clipPath(o, True)
    pr = r * (.42 if mood == "shock" else .62); px, py = x + look[0] * r * .35, y + look[1] * r * .4
    c.drawPath(oval(px, py, pr, pr * 1.15), fill((40, 24, 36))); c.drawCircle(px - pr * .3, py - pr * .45, pr * .34, fill((255, 255, 255)))
    if mood == "smug": c.drawRect(skia.Rect.MakeLTRB(x - r - 5, y - ry - 5, x + r + 5, y - ry * .15), fill((150, 112, 100) if off == 9 else (214, 196, 214)))
    c.restore(); c.drawPath(o, line(INK, 6))
    if mood == "smug": c.drawLine(x - r, y - ry * .15, x + r, y - ry * .15, line(INK, 7))

def mouth(c, x, y, w, talk, mood):
    if talk > .08 or mood in ("laugh", "shock"):
        h = w * (.3 + .6 * max(talk, .5 if mood == "laugh" else .3)); p = skia.Path(); p.moveTo(x - w, y); p.quadTo(x, y - w * .2, x + w, y); p.quadTo(x + w * .8, y + h * 1.5, x, y + h * 1.5); p.quadTo(x - w * .8, y + h * 1.5, x - w, y); p.close()
        c.drawPath(p, fill((120, 24, 40))); c.save(); c.clipPath(p, True); c.drawPath(oval(x, y + h * 1.5, w * .6, h * .6), fill((240, 110, 120))); c.restore(); c.drawPath(p, line(INK, 6))
    else:
        p = skia.Path(); s = -1 if mood == "sad" else 1; p.moveTo(x - w * .8, y); p.quadTo(x, y + w * .8 * s, x + w * .8, y); c.drawPath(p, line(INK, 7))

def rabbit(c, x, y, s, t, talk=0., mood="smug", d=1, run=False, lie=False):
    fur, belly, pink = (214, 196, 214), (250, 244, 250), (255, 160, 178)
    c.save(); c.translate(x, y); c.scale(s * d, s)
    if lie: c.translate(0, -40); c.rotate(-62)
    ph = t * 15; bob = -abs(sin(ph)) * 36 if run else sin(t * 2.4) * 4
    if mood == "laugh": bob += sin(t * 22) * 6
    c.drawOval(skia.Rect.MakeLTRB(-120, -14, 120, 18), fill((20, 40, 20), 0 if lie else .25)); c.translate(0, bob)
    if run: c.rotate(16)
    a = sin(ph) * 95 if run else 0
    limb(c, [(-30, -130), (-30 - a * .6, -70), (-40 - a, -14 - (max(0, a) * .5))], 46, mix(fur, (80, 40, 100), .2))
    cel(c, oval(-92, -120, 34), belly)
    arm = sin(ph) * 80 if run else 0
    limb(c, [(-20, -260), (-60 - arm * .5, -210), (-40 - arm, -160)], 34, mix(fur, (80, 40, 100), .2))
    cel(c, smooth([(-75, -300), (70, -300), (105, -120), (40, -55), (-60, -55), (-112, -130)]), fur)
    c.drawPath(oval(28, -160, 54, 82), fill(belly))
    limb(c, [(36, -120), (36 + a * .6, -70), (46 + a, -14 - max(0, -a) * .5)], 48, fur); cel(c, oval(62 + a, -16 - max(0, -a) * .5, 54, 24), belly)
    if run: limb(c, [(40, -260), (80 + arm * .5, -220), (70 + arm, -170)], 34, fur)
    elif mood in ("smug", "laugh") and not lie: limb(c, [(50, -260), (130, -225), (150 + talk * 20, -290 - talk * 26)], 34, fur)
    else: limb(c, [(50, -260), (88, -215), (70, -160)], 34, fur)
    c.translate(10, -370); c.rotate(sin(t * 2.2) * 2.5 + (-8 if mood == "laugh" else 0))
    sw = sin(t * 3) * 10 + (-60 if run else 0) + (25 if mood == "sad" else 0) + (-14 if mood == "shock" else 0)
    for ex, k in ((-46, 1), (30, .6)):
        e = smooth([(ex - 34, -70), (ex - 42 + sw * .5, -220), (ex + sw, -300), (ex + 40 + sw * .5, -210), (ex + 34, -70)]); cel(c, e, fur)
        c.drawPath(smooth([(ex - 14, -90), (ex - 20 + sw * .5, -200), (ex + sw * .9, -262), (ex + 20 + sw * .5, -195), (ex + 14, -90)]), fill(pink))
    cel(c, smooth([(-118, -70), (0, -138), (118, -70), (128, 30), (70, 100), (-70, 100), (-126, 30)]), fur)
    c.drawPath(oval(30, 46, 78, 48), fill(belly)); c.drawPath(oval(-70, 30, 26, 18), fill(pink, .6)); c.drawPath(oval(108, 26, 18, 16), fill(pink, .6))
    eye(c, -22, -28, 36, (.6, .1), t, mood, 0); eye(c, 68, -28, 34, (.6, .1), t, mood, 0)
    c.drawPath(smooth([(18, 12), (48, 12), (34, 36)]), fill(pink)); c.drawPath(smooth([(18, 12), (48, 12), (34, 36)]), line(INK, 5))
    mouth(c, 34, 48, 34, talk, mood)
    if not (talk > .08 or mood in ("laugh", "shock")): pass
    else: c.drawRect(skia.Rect.MakeLTRB(22, 46, 46, 66), fill((255, 255, 255))); c.drawRect(skia.Rect.MakeLTRB(22, 46, 46, 66), line(INK, 4))
    c.restore()

def turtle(c, x, y, s, t, talk=0., mood="n", d=1, walk=False):
    skin, shell, rimc = (150, 205, 90), (46, 150, 120), (236, 196, 110); dark = mix(skin, (40, 60, 90), .25)
    c.save(); c.translate(x, y); c.scale(s * d, s); c.drawOval(skia.Rect.MakeLTRB(-210, -16, 210, 18), fill((20, 40, 20), .25))
    ph = t * 4.2; bob = sin(ph * 2) * 5 if walk else sin(t * 2) * 3; k = 34 if walk else 0
    for lx, q, cc in ((-96, pi, dark), (104, 0, dark), (-128, 0, skin), (74, pi, skin)):
        a = sin(ph + q) * k; up = max(0, cos(ph + q)) * k * .7; limb(c, [(lx, -90), (lx + a * .5, -50), (lx + a, -22 - up)], 56, cc)
    c.translate(0, bob); cel(c, smooth([(-190, -90), (-250, -70), (-190, -110)]), skin)
    n = 26 * sin(t * 1.6); limb(c, [(120, -110), (190, -150), (222, -232 + n * .2)], 66, skin)
    cel(c, smooth([(-215, -70), (-215, -180), (-110, -300), (20, -310), (150, -220), (185, -70)]), shell, .28)
    c.save(); c.clipPath(smooth([(-215, -70), (-215, -180), (-110, -300), (20, -310), (150, -220), (185, -70)]), True)
    for hx, hy, r in ((-110, -150, 48), (0, -200, 56), (96, -140, 44), (-40, -105, 40)):
        hp = poly([(hx + r * cos(q * pi / 3), hy + r * .85 * sin(q * pi / 3)) for q in range(6)]); c.drawPath(hp, fill((84, 186, 140))); c.drawPath(hp, line((30, 110, 92), 7))
    c.restore(); cel(c, smooth([(-225, -100), (185, -100), (205, -62), (0, -52), (-235, -62)]), rimc)
    c.translate(232, -262 + n * .2); c.rotate(sin(t * 1.8) * 3)
    cel(c, smooth([(-88, -60), (0, -108), (92, -56), (112, 30), (40, 84), (-70, 74), (-100, 10)]), skin)
    c.drawPath(oval(-44, 34, 22, 15), fill((255, 150, 120), .5))
    eye(c, -8, -26, 32, (.5, .05), t, mood, 1.2); eye(c, 62, -28, 30, (.5, .05), t, mood, 1.2)
    mouth(c, 44, 30, 32, talk, mood); c.restore()

# ---------------- world
def tree(c, x, y, s, t, hue=(86, 170, 74)):
    c.save(); c.translate(x, y); c.scale(s, s); cel(c, smooth([(-40, 10), (-24, -160), (-46, -330), (50, -330), (26, -160), (46, 10)]), (150, 98, 62))
    sw = sin(t * 1.2 + x) * 6; cel(c, smooth([(-190 + sw, -300), (-230 + sw, -430), (-130 + sw, -560), (20 + sw, -610), (170 + sw, -540), (240 + sw, -410), (180 + sw, -300), (0, -270)]), hue, .25, off=(-24, -28))
    for a, b, r in ((-80, -470, 46), (40, -520, 60), (110, -400, 36)): c.drawPath(oval(a + sw, b, r, r * .7), fill(mix(hue, (255, 255, 180), .3), .8))
    c.restore()

def world(c, scroll, t, gy=1290):
    c.drawColor(col((70, 176, 240))); vgrad(c, [(0, (70, 176, 240)), (.55, (190, 232, 250)), (1, (255, 246, 214))], 0, gy)
    glow(c, 860, 360, 340, (255, 240, 170), .9); c.drawCircle(860, 360, 92, fill((255, 226, 90)))
    for i in range(5):
        x = (i * 330 - scroll * .08 + t * 8) % 1650 - 250; y = 300 + (i * 137) % 330; c.save(); c.translate(x, y)
        for a, b, r in ((-70, 10, 46), (0, -16, 66), (74, 8, 50)): c.drawCircle(a, b, r, fill((255, 255, 255), .92))
        c.drawRoundRect(skia.Rect.MakeLTRB(-116, 6, 124, 58), 26, 26, fill((255, 255, 255), .92)); c.restore()
    for k, (sp, base, amp, cc) in enumerate(((.15, 1010, 90, (150, 205, 190)), (.3, 1110, 70, (126, 198, 140)), (.5, 1190, 50, (104, 184, 100)))):
        c.drawPath(poly([(-10, gy + 20)] + [(x, base + amp * sin((x + scroll * sp) * .0046 + k * 2) + amp * .4 * sin((x + scroll * sp) * .011 + k)) for x in range(-10, W + 30, 20)] + [(W + 30, gy + 20)]), fill(cc))
    for i in range(4):
        x = (i * 560 + 300 - scroll * .62) % 2240 - 500; tree(c, x, gy + 10, .62, t, ((86, 170, 74), (120, 184, 70), (66, 152, 96), (104, 176, 64))[i])
    vgrad(c, [(0, (140, 206, 92)), (1, (70, 148, 66))], gy, H + 500)
    c.drawPath(poly([(0, gy + 60), (W, gy + 60), (W, gy + 250), (0, gy + 250)]), fill((238, 206, 150))); c.drawRect(skia.Rect.MakeLTRB(0, gy + 60, W, gy + 74), fill((206, 166, 108)))
    for i in range(16):
        x = (i * 131 - scroll) % 2096 - 300; c.drawOval(skia.Rect.MakeLTRB(x, gy + 120 + (i * 53) % 100, x + 44, gy + 134 + (i * 53) % 100), fill((206, 166, 108)))
    for i in range(14):
        x = (i * 157 - scroll * 1.05) % 2198 - 300; y = gy + 330 + (i * 97) % 260
        for b in (-16, 0, 16): c.drawPath(poly([(x + b - 8, y), (x + b * 1.7, y - 46), (x + b + 8, y)]), fill((54, 126, 54)))
        if i % 3 == 0:
            for q in range(5): c.drawCircle(x + 60 + 15 * cos(q * 1.257), y - 20 + 15 * sin(q * 1.257), 11, fill(((255, 120, 160), (255, 255, 255), (255, 214, 80))[i % 9 // 3]))
            c.drawCircle(x + 60, y - 20, 8, fill((255, 200, 40)))

def cam(c, z, x, y):
    c.translate(W / 2, 800 + 60 / z); c.scale(z, z); c.translate(-x, -y)

GY = 1470
def s_intro(c, t, D, tk, T): cam(c, 1.08 + .06 * ease(t / D), 540, 1000); world(c, 0, T); rabbit(c, 330, GY, 1.15, T, mood="smug"); turtle(c, 790, GY, .85, T, d=-1)
def s_laugh(c, t, D, tk, T): cam(c, 1.45 + .05 * ease(t / D), 430, 1140); world(c, 0, T); turtle(c, 860, GY, .85, T, mood="n", d=-1); rabbit(c, 370, GY, 1.15, T, tk.get("R", 0), "laugh")
def s_dare(c, t, D, tk, T): cam(c, 1.5 + .06 * ease(t / D), 690, 1220); world(c, 0, T); rabbit(c, 250, GY, 1.15, T, mood="smug"); turtle(c, 790, GY, .95, T, tk.get("T", 0), "n", d=-1)
def s_run(c, t, D, tk, T):
    cam(c, 1.05, 540 + sin(T * 40) * 2, 1000); sc = t * 1500; world(c, sc, T); rx = 200 + 420 * ease(t / D * 1.2)
    for i in range(14):
        y = 560 + i * 74; x = W - ((T * 2600 + i * 313) % 1700); c.drawLine(x, y, x + 260, y, line((255, 255, 255), 6, .55))
    for i in range(7):
        u = (T * 2.2 + i / 7) % 1; c.drawCircle(rx - 110 - u * 330, GY - 20 - u * 60, 20 + u * 46, fill((244, 226, 190), .75 * (1 - u)))
    turtle(c, 160 - t * 420, GY, .8, T, walk=True); rabbit(c, rx, GY, 1.1, T, mood="laugh", run=True)
def zzz(c, x, y, T):
    f = skia.Font(skia.Typeface.MakeFromFile(BLACK), 80)
    for i in range(3):
        u = (T * .45 + i / 3) % 1; f.setSize(50 + 60 * u); c.drawString("Z", x + u * 130 + 20 * sin(u * 6), y - u * 260, f, fill((255, 255, 255), 1 - u)); c.drawString("Z", x + u * 130 + 20 * sin(u * 6), y - u * 260, f, line((70, 60, 130), 4, 1 - u))
def s_nap(c, t, D, tk, T): cam(c, 1.25 + .06 * ease(t / D), 600, 1100); world(c, 900, T); tree(c, 800, GY - 40, 1.35, T); rabbit(c, 560, GY - 30, 1.05, T, tk.get("R", 0), "smug")
def s_pass(c, t, D, tk, T):
    cam(c, 1.08, 540, 1010); world(c, 900, T); tree(c, 800, GY - 60, 1.3, T); rabbit(c, 860, GY - 40, .85, T, mood="sleep", lie=True); zzz(c, 640, GY - 250, T); turtle(c, -160 + 1050 * (t / D), GY + 70, .9, T, mood="happy", walk=True)
def s_wake(c, t, D, tk, T): cam(c, 1.6 + .25 * ease(t / .3), 560 + sin(T * 45) * 5 * clamp(1 - t), 1080); world(c, 900, T); tree(c, 820, GY - 40, 1.3, T); rabbit(c, 540, GY - 20, 1.05, T, tk.get("R", 0), "shock")
def confetti(c, T):
    r = random.Random(3)
    for i in range(110):
        x0, sp, ph = r.random() * W, r.uniform(260, 520), r.random(); y = (T * sp + ph * 2000) % 2000 - 60; c.save(); c.translate(x0 + 40 * sin(T * 2 + i), y); c.rotate(T * 200 + i * 40)
        c.drawRect(skia.Rect.MakeLTRB(-11, -6, 11, 6), fill(((255, 80, 100), (255, 210, 60), (90, 200, 255), (130, 220, 110), (220, 130, 255))[i % 5])); c.restore()
def s_win(c, t, D, tk, T):
    cam(c, 1.08, 540, 1020); world(c, 1800, T)
    for x in (330, 900): cel(c, poly([(x - 16, GY + 20), (x + 16, GY + 20), (x + 16, 760), (x - 16, 760)]), (230, 70, 80))
    cel(c, poly([(310, 700), (920, 700), (920, 840), (310, 840)]), (255, 255, 255), .08)
    for i in range(15):
        for j in range(2):
            if (i + j) % 2: c.drawRect(skia.Rect.MakeLTRB(316 + i * 40, 704 + j * 66, 356 + i * 40, 770 + j * 66), fill(INK))
    tx = 130 + 480 * ease(t / (D * .55)); turtle(c, tx, GY, .9, T, mood="happy", walk=tx < 600)
    for sg in (-1, 1):
        u = clamp((tx - 380) / 200); c.drawPath(smooth([(615 + sg * 285, GY - 170), (615 + sg * 140, GY - 170 + 60 * u), (615 + sg * 285 * u, GY - 170 + 150 * u)], False), line((230, 40, 60), 14))
    confetti(c, T)
def s_moral(c, t, D, tk, T): cam(c, 1.2 + .05 * ease(t / D), 560, 1120); world(c, 1800, T); rabbit(c, 320, GY, 1.0, T, mood="sad"); turtle(c, 770, GY, .9, T, mood="happy", d=-1); confetti(c, T)

N, R, Tt = (M, "+4%", "-4Hz"), (M, "+14%", "+22Hz"), (M, "-8%", "-16Hz")
def L(shot, who, v, hi, ro, **k): return dict(shot=shot, who=who, v=v, hi=hi, ro=ro, **k)
LINES = [
 L("intro", "N", N, "खरगोश को अपनी रफ़्तार पर बड़ा घमंड था।", "Khargosh ko apni *raftaar* par bada *ghamand* tha."),
 L("laugh", "R", R, "अरे कछुए! तू तो चलते चलते सो जाता होगा! हा हा हा!", "Arre *kachhue!* Tu toh chalte chalte *so* jaata hoga! Ha ha ha!"),
 L("dare", "T", Tt, "अच्छा? तो हो जाए एक रेस?", "Achha? Toh ho jaye ek *race?*", pad=.5),
 L("run", "N", N, "रेस शुरू हुई, और खरगोश हवा की तरह भागा!", "Race shuru hui, aur khargosh *hawa* ki tarah *bhaaga!*"),
 L("nap", "R", R, "कछुआ तो बहुत पीछे है। थोड़ी झपकी ले लेता हूँ।", "Kachhua toh bahut *peeche* hai. Thodi *jhapki* le leta hoon."),
 L("pass", "N", N, "पर कछुआ रुका नहीं। धीरे धीरे, बस चलता रहा।", "Par kachhua *ruka* *nahi.* Dheere dheere, bas *chalta* raha.", pad=.7),
 L("wake", "R", R, "अरे! वो कहाँ गया?", "Arre! Woh *kahan* gaya?"),
 L("win", "N", N, "और रेस जीत गया, कछुआ!", "Aur race *jeet* gaya, *kachhua!*", pre=.4, pad=.9),
 L("moral", "N", N, "याद रखो, जीत रफ़्तार से नहीं, लगन से मिलती है।", "Yaad rakho, *jeet* raftaar se nahi, *lagan* se milti hai.", pad=1.2),
]
SH = {k[2:]: v for k, v in list(globals().items()) if k.startswith("s_")}

def music(n, tl):
    """Light plucked tune with a bouncy bass and soft claps."""
    b = np.zeros(n); t, i = .1, 0; step = .25; mel = [0, 4, 7, 12, 7, 4, 9, 7, 5, 9, 12, 9, 7, 4, 2, 4, 0, 7, 4, 12, 16, 12, 9, 7, 5, 4, 2, 7, 4, 2, 0, -1]; bass = [0, 0, 5, 7]
    while t < tl["total"]:
        m = mel[i % 32]
        if m >= 0: au.add(b, t, au.sweep(523.25 * 2 ** (m / 12), 523.25 * 2 ** (m / 12), .5, 8), .38)
        if i % 4 == 0: au.add(b, t, au.sweep(130.8 * 2 ** (bass[i // 8 % 4] / 12), 130.8 * 2 ** (bass[i // 8 % 4] / 12), .45, 6), .7)
        if i % 4 == 2: au.add(b, t, au.band(au.noise(.08), 1500, 6000) * np.exp(-au.tarr(.08) * 50), .22)
        t += step; i += 1
    return b
def fxs(fx, tl):
    for l in tl["lines"]:
        if l["start"] > 0: au.add(fx, l["start"] - .1, au.sweep(300, 900, .25, 8), .14)
        if l["shot"] == "run":
            t = l["start"]
            while t < l["end"]: au.add(fx, t, au.band(au.noise(.07), 80, 600) * np.exp(-au.tarr(.07) * 45), .25); t += .21
            au.add(fx, l["start"], au.band(au.noise(1.2), 400, 5000) * np.hanning(int(1.2 * SR)), .22)
        if l["shot"] == "wake": au.add(fx, l["start"], au.sweep(500, 1500, .4, 5), .35)
        if l["shot"] == "win":
            for j, f in enumerate((523, 659, 784, 1047, 1318)): au.add(fx, l["start"] + .5 + j * .11, au.sweep(f, f, .9, 4), .3)
            au.add(fx, l["start"] + .6, au.band(au.noise(2.2), 800, 6000) * np.hanning(int(2.2 * SR)) * (.6 + .4 * np.sin(2 * pi * 13 * au.tarr(2.2))), .16)

if __name__ == "__main__": run("race", LINES, SH, ("KHARGOSH AUR", "KACHHUA"), music, fxs)
