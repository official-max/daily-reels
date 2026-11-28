"""Ramayan bhaag 1 (Uttar kaand, sarg 1): the rishis come to Ram's court; why was Meghnad greater than Ravan?
Script: scripts/001.md. Characters from cast/ramayan.json via the factory. 60 fps.
    python engine/bhaag001.py preview   -> out/preview_bhaag001.jpg
    python engine/bhaag001.py           -> out/sample_bhaag001.mp4
"""
import lab, rig
from rig import *
from lab import main as run, SR, M, S, au
from hanuman import cam, live, stand, embers, aura, vig, sky, stars, ground, clouds, thump, boom, GY
import factory as fa
lab.FPS = 60; rig.SOFT = True
ss = lambda u: (lambda v: v * v * (3 - 2 * v))(max(0., min(1., u)))

# ---------------- cast: the main people from the design file, the rest made by the factory
CASTF = fa.load(); BY = {s["name"]: s for s in CASTF}
INDRA = dict(name="Indra", kind="human", age="adult", build="strong", skin=[246, 214, 170], hair="crown", beard="moustache", crown="tall", tilak="dot", eyes="calm", top="kavach", lower="dhoti", cloth=[60, 120, 220], edge=[255, 210, 70], jewel=[40, 200, 220], weapon="vajra")
def vajra(c, a, b):
    u, n = fa._ax(a, b); P = lambda q, w: (a[0] + u[0] * q + n[0] * w, a[1] + u[1] * q + n[1] * w); glow(c, *P(60, 0), 160, (180, 230, 255), .6)
    for d in (-1, 1): shape(c, poly([P(0, 0), P(d * 60 + 30, -30), P(d * 150 + 30, -8), P(d * 110 + 30, 0), P(d * 150 + 30, 8), P(d * 60 + 30, 30)]), (255, 210, 60), 5)
    shape(c, oval(*P(30, 0), 22), (255, 220, 90), 5)
fa.WEAPONS["vajra"] = vajra
EXTRA = [fa.auto("sainik", 7, CASTF, "Dwarpal")] + [fa.auto("rishi", k, CASTF, f"Rishi {k}") for k in (2, 3, 4)]
for sp in CASTF + [INDRA] + EXTRA: rig.CAST[sp["name"].lower().replace(" ", "")] = fa.make(sp)

def shadow_of(c, draw, rgb=(30, 6, 24), a=.95, rim=(255, 120, 50)):
    """A giant dark shape with a glowing edge."""
    c.saveLayer(None, skia.Paint(ImageFilter=skia.ImageFilters.Blur(18, 18), ColorFilter=skia.ColorFilters.Blend(col(rim, 1), skia.BlendMode.kSrcIn))); draw(); c.restore()
    c.saveLayer(None, skia.Paint(ColorFilter=skia.ColorFilters.Blend(col(rgb, a), skia.BlendMode.kSrcATop))); draw(); c.restore()

# ---------------- places, painted once
def pillar(c, x, y0, y1, w, rgb, gold):
    shape(c, poly([(x - w, y1), (x - w, y0), (x + w, y0), (x + w, y1)]), rgb, 5)
    for y in (y0 + 30, y1 - 50): shape(c, poly([(x - w * 1.35, y + 30), (x - w * 1.35, y), (x + w * 1.35, y), (x + w * 1.35, y + 30)]), gold, 4)
    for k in range(3): c.drawLine(x - w * .5 + k * w * .5, y0 + 70, x - w * .5 + k * w * .5, y1 - 60, line(mix(rgb, (60, 20, 30), .25), 4))
def arch(c, x, y, w, h, rgb):
    c.drawPath(smooth([(x - w, y), (x - w, y - h * .6), (x - w * .5, y - h * .92), (x, y - h), (x + w * .5, y - h * .92), (x + w, y - h * .6), (x + w, y)], False), line(rgb, 26))
def lamp(c, x, y):
    c.drawLine(x, 0, x, y - 40, line((150, 100, 40), 5)); glow(c, x, y, 120, (255, 200, 100), .55); shape(c, smooth([(x - 34, y - 40), (x + 34, y - 40), (x + 20, y + 10), (x - 20, y + 10)]), (240, 180, 60), 4); c.drawPath(smooth([(x - 8, y - 40), (x, y - 70), (x + 8, y - 40)]), fill((255, 230, 120)))
def throne(c, x=540):
    G, RD = (250, 196, 60), (196, 36, 52)
    c.drawLine(x, 470, x, 640, line((150, 100, 40), 8)); shape(c, smooth([(x - 170, 640), (x - 120, 560), (x, 520), (x + 120, 560), (x + 170, 640)]), (255, 250, 240), 6)
    for i in range(9): c.drawCircle(x - 160 + i * 40, 650, 11, fill(G))
    shape(c, poly([(x - 150, 1100), (x - 150, 830), (x - 120, 760), (x - 60, 720), (x, 660), (x + 60, 720), (x + 120, 760), (x + 150, 830), (x + 150, 1100)]), G, 7)
    shape(c, poly([(x - 110, 1090), (x - 110, 850), (x - 70, 790), (x, 740), (x + 70, 790), (x + 110, 850), (x + 110, 1090)]), RD, 5)
    for k in range(3): c.drawCircle(x, 800 + k * 60, 12, fill(G))
    for d in (-1, 1): shape(c, oval(x + d * 165, 1000, 32, 60), G, 5); shape(c, oval(x + d * 165, 930, 26), G, 5)
    shape(c, poly([(x - 200, 1200), (x - 200, 1100), (x + 200, 1100), (x + 200, 1200)]), (230, 170, 60), 6); shape(c, poly([(x - 150, 1110), (x - 150, 1060), (x + 150, 1060), (x + 150, 1110)]), RD, 5)
    for k in range(3): shape(c, poly([(x - 230 - k * 30, 1220 + k * 20), (x - 230 - k * 30, 1200 + k * 20), (x + 230 + k * 30, 1200 + k * 20), (x + 230 + k * 30, 1220 + k * 20)]), (240, 226, 200), 4)
def petals(c, T, n=40, seed=2):
    r = random.Random(seed)
    for i in range(n):
        x0, v, ph = r.uniform(-100, W + 100), r.uniform(90, 170), r.uniform(0, 9); y = (r.uniform(0, H) + T * v) % (H + 200) - 100; x = x0 + sin(T * 1.3 + ph) * 40
        c.save(); c.translate(x, y); c.rotate((T * 90 + ph * 40) % 360); c.drawOval(skia.Rect.MakeLTRB(-11, -6, 11, 6), fill(r.choice([(255, 150, 30), (255, 200, 40), (230, 40, 70)]), .9)); c.restore()
def p_sabha(c):
    r = random.Random(1); vgrad(c, [(0, (120, 40, 40)), (.5, (220, 140, 80)), (1, (250, 200, 140))], -320, H + 320)
    for x in range(-200, W + 300, 280): arch(c, x + 140, 1100, 110, 520, (250, 210, 120))
    glow(c, 540, 820, 700, (255, 240, 200), .6)
    throne(c)
    for x in (-40, 210, 870, 1120): pillar(c, x, 360, 1320, 46, (240, 220, 190), (250, 196, 60))
    c.drawRect(skia.Rect.MakeLTRB(-320, 1260, W + 320, H + 320), fill((150, 60, 50))); c.drawPath(poly([(380, 1260), (700, 1260), (1150, H + 320), (-70, H + 320)]), fill((200, 40, 50)))
    for y in (1300, 1420, 1580, 1780): c.drawLine(-320, y, W + 320, y, line((120, 44, 40), 3, .5))
    for i in range(14): x = -60 + i * 90; c.drawPath(smooth([(x, 300), (x + 45, 360), (x + 90, 300)], False), line((255, 150, 40), 18)); c.drawCircle(x + 45, 372, 10, fill((220, 40, 60)))
    for x in (160, 920): lamp(c, x, 560)
def gate_arc(w, top, x=540, y0=940, y1=1340):
    return [(x - w, y1), (x - w, y0)] + [(x - cos(a) * w, y0 - sin(a) * (y0 - top)) for a in np.linspace(0, pi, 15)[1:-1]] + [(x + w, y0), (x + w, y1)]
def p_dwar(c):
    r = random.Random(3); sky(c, (110, 170, 230), (255, 214, 170)); glow(c, 540, 820, 700, (255, 240, 200), .7)
    for i, (x, h) in enumerate(((-60, 720), (1140, 760), (180, 520), (900, 540))): shape(c, poly([(x - 90, 1330), (x - 90, 1330 - h), (x - 50, 1330 - h - 120), (x, 1330 - h - 220), (x + 50, 1330 - h - 120), (x + 90, 1330 - h), (x + 90, 1330)]), (246, 226, 196) if i < 2 else (236, 210, 176), 6)
    shape(c, poly([(260, 1340), (260, 640), (820, 640), (820, 1340)]), (240, 214, 170), 7); shape(c, poly(gate_arc(210, 700)), (120, 60, 40), 7)
    shape(c, poly(gate_arc(180, 740)), (250, 196, 70), 6); c.drawLine(540, 742, 540, 1340, line((150, 90, 30), 8))
    for d in (-1, 1): [c.drawRect(skia.Rect.MakeXYWH(540 + d * 95 - 55, 980 + k * 120, 110, 90), line((200, 140, 40), 5)) for k in range(3)]
    for x in (450, 630): [c.drawCircle(x, y, 9, fill((150, 90, 30))) for y in range(920, 1320, 70)]
    for i in range(12): x = 270 + i * 50; c.drawPath(smooth([(x, 650), (x + 25, 690), (x + 50, 650)], False), line((90, 170, 60), 14))
    for x in (290, 790): c.drawLine(x, 640, x, 470, line((120, 80, 40), 7)); c.drawPath(poly([(x, 470), (x + 110, 500), (x, 530)]), fill((255, 130, 30)))
    ground(c, (226, 196, 150), (255, 240, 210), r, GY - 70)
    for k in range(4): c.drawRect(skia.Rect.MakeLTRB(300 - k * 40, 1330 + k * 22, 780 + k * 40, 1352 + k * 22), fill(mix((236, 216, 180), (160, 120, 90), k * .15)))
def p_lanka(c):
    r = random.Random(5); sky(c, (20, 4, 16), (200, 50, 30)); glow(c, 540, 1180, 800, (255, 110, 40), .6)
    for x, h in ((-20, 760), (150, 520), (330, 880), (560, 640), (760, 940), (960, 600), (1110, 780)):
        c.drawPath(poly([(x - 80, 1330), (x - 80, 1330 - h), (x - 40, 1330 - h - 90), (x, 1330 - h - 230), (x + 40, 1330 - h - 90), (x + 80, 1330 - h), (x + 80, 1330)]), fill((50, 10, 24)))
        for k in range(5): c.drawRect(skia.Rect.MakeXYWH(x - 20, 1330 - h + 60 + k * 110, 40, 50), fill((255, 170, 60), .8))
    ground(c, (60, 18, 28), (230, 90, 50), r)
def p_yuddh(c):
    r = random.Random(9); sky(c, (60, 20, 20), (240, 130, 60)); glow(c, 540, 1100, 900, (255, 170, 80), .6)
    for i in range(9): x, y = r.uniform(-100, W + 100), r.uniform(900, 1300); [c.drawCircle(x + q * 60, y - abs(q) * 20, 110, fill((120, 70, 60), .35)) for q in range(-2, 3)]
    for i in range(14): x = r.uniform(-100, W + 100); c.drawLine(x, 1330, x + r.uniform(-80, 80), 1330 - r.uniform(150, 330), line((60, 30, 30), 8)); c.drawPath(poly([(x - 30, 1330 - 330), (x + 30, 1330 - 330), (x, 1330 - 420)]), fill((60, 30, 30)))
    ground(c, (120, 70, 50), (250, 170, 100), r)
def p_megh(c):
    r = random.Random(11); sky(c, (8, 10, 30), (60, 50, 90), H)
    for i in range(26): x, y, k = r.uniform(-200, W + 200), r.uniform(100, 1700), r.uniform(.8, 1.8); [c.drawCircle(x + q * 80 * k, y - (2 - abs(q)) * 30 * k, 120 * k, fill(mix((40, 40, 70), (110, 100, 150), r.random()), .8)) for q in range(-2, 3)]
def p_swarg(c):
    r = random.Random(13); sky(c, (250, 190, 210), (255, 240, 200), H); glow(c, 540, 700, 800, (255, 255, 230), .9)
    for x in (120, 960): pillar(c, x, 300, 1250, 40, (255, 250, 240), (255, 210, 90))
    for i in range(30): x, y, k = r.uniform(-200, W + 200), r.uniform(1150, 1900), r.uniform(.8, 1.6); [c.drawCircle(x + q * 80 * k, y - (2 - abs(q)) * 26 * k, 110 * k, fill((255, 250, 252), .9)) for q in range(-2, 3)]
def p_dark(c): vgrad(c, [(0, (10, 6, 20)), (1, (40, 16, 50))], -320, H + 320)

def bolt(c, t, seed, x0, y0, y1, a=1.):
    r = random.Random(seed); p = [(x0, y0)]; x = x0
    for y in np.linspace(y0, y1, 9)[1:]: x += r.uniform(-90, 90); p.append((x, y))
    q = poly(p, False); c.drawPath(q, line((200, 220, 255), 26, .4 * a)); c.drawPath(q, line((255, 255, 255), 8, a))

# ---------------- shots: c, t (time in shot), D (shot length), tk (talk per speaker), T (time in video)
def s_hook(c, t, D, tk, T):
    cam(c, 1.06 - .06 * ss(t / D), 540, 1080); bg(c, "lanka", p_lanka); u = ss((t - .3) / (D * .7))
    c.save(); c.translate(0, 120 * (1 - u)); shadow_of(c, lambda: stand(c, "meghnad", "hero", 560, T, 1.9 + .3 * u, -1, GY + 60, weapon=True), a=.92); c.restore()
    glow(c, 540, 1100, 500, (255, 90, 40), .35); stand(c, "ravan", "guard", 480, T, 1.05, 1, GY + 40, mood="angry"); embers(c, T, 50); vig(c)
def s_sabha(c, t, D, tk, T):
    u = ss(t / D); cam(c, 1.22 - .2 * u, 540, 980 + 110 * u); bg(c, "sabha", p_sabha)
    stand(c, "sita", "namaste", 175, T, .84, 1, GY + 10, weapon=False); stand(c, "lakshman", "stand", 905, T, .88, -1, GY + 10, weapon=False)
    stand(c, "ram", "hero", 520, T, .94, 1, GY + 30, weapon=False, a1u=40, a1f=60, head=8 * sin(T * 1.1)); petals(c, T, 30); vig(c)
def s_rishi(c, t, D, tk, T):
    cam(c, 1.0, 540, 1090); bg(c, "dwar", p_dwar, 40 - t * 20)
    for i, (who, x0, s) in enumerate((("rishi4", 1290, .84), ("rishi3", 1010, .86), ("agastya", 730, .78), ("rishi2", 1570, .86))):
        x = x0 - 420 * ss(t / D); f = lambda q, x=x, i=i: live(pose("stand", x=x - 30 * sin((T - q) * 3 + i), f1x=40 + 30 * sin((T - q) * 6 + i), f2x=-40 - 30 * sin((T - q) * 6 + i)), T - q, .5)
        body(c, rig.CAST[who], f(0), GY + 20 + i * 8, s, -1, T, 0, "n", past=f)
    glow(c, 540, 400, 500, (255, 250, 220), .3); vig(c)
def s_dwar(c, t, D, tk, T):
    cam(c, 1.12 + .08 * ss(t / D), 560, 1080); bg(c, "dwar", p_dwar); stand(c, "dwarpal", "namaste" if t > D * .7 else "stand", 250, T, .98, 1, GY + 10, mood="n", weapon=t <= D * .7, head=14 * ss((t - D * .7) / .3))
    stand(c, "agastya", "talk", 800, T, .86, -1, GY + 10, talk=tk.get("A", 0), weapon=True); vig(c)
def s_swagat(c, t, D, tk, T):
    cam(c, 1.02, 540, 1090); bg(c, "sabha", p_sabha); SIT = P(h=150, hx=-30, lean=-4, a1u=30, a1f=70, a2u=20, a2f=60, f1x=80, f2x=50, f1y=0)
    mixp = lambda a, b, w: {k: a[k] + (b[k] - a[k]) * w for k in BASE}
    v = lambda q: live(dict(mixp(SIT, POSE["stand"], ss((t - q - .6) / 1.0)) if t - q < 1.9 else mixp(POSE["stand"], POSE["namaste"], ss((t - q - 1.9) / .7)), x=470 - 160 * ss((t - q - 1.2) / 1.2)), T - q)
    body(c, rig.CAST["ram"], v(0), GY + 30, .94, 1, T, 0, "n", past=v, weapon=False)
    for i, (who, x, s) in enumerate((("rishi3", 1000, .84), ("agastya", 760, .78))): xx = x + 200 * (1 - ss(t / 1.6)); stand(c, who, "namaste" if t > D * .55 else "stand", xx, T, s, -1, GY + 20, weapon=False)
    aura(c, 320, 1000, T, 300 * ss((t - 1.9) / .7) + 10, (255, 230, 160)); vig(c)
def s_prashansa(c, t, D, tk, T):
    cam(c, 1.06 - .06 * ss(t / D), 540, 1090); bg(c, "sabha", p_sabha); stand(c, "ram", "namaste", 300, T, .94, 1, GY + 30, weapon=False)
    for i, (who, x, s) in enumerate((("rishi2", 1060, .8), ("rishi4", 850, .78), ("agastya", 630, .76))): stand(c, who, "hero", x, T + i, s, -1, GY + 20 - i * 6, weapon=False, a1u=150 + 10 * sin(T * 2 + i), a1f=170, a2u=20, a2f=40)
    aura(c, 300, 1000, T, 360, (255, 220, 140)); petals(c, T, 60, 5); vig(c)
def s_yuddh(c, t, D, tk, T):
    sx, sy = sin(T * 31) * 4, cos(T * 27) * 4; c.translate(sx, sy); cam(c, 1.0 + .05 * ss(t / D), 540, 1080); bg(c, "yuddh", p_yuddh, -t * 30)
    kk = Keys(-1, 1.25, [(0, pose("guard", x=860), "io"), (.6, pose("roar", x=820), "io"), (1.4, pose("run", x=760), "io"), (2.2, pose("roar", x=760), "io"), (9, pose("roar", x=760), "io")]); f = lambda q: live(anim(kk, t - q), T - q)
    rk = Keys(1, .95, [(0, pose("guard", x=230), "io"), (.8, pose("wind", x=250), "io"), (1.1, pose("strike", x=300), "hit"), (1.4, pose("follow", x=302), "out"), (2.2, pose("guard", x=290), "io"), (9, pose("guard", x=290), "io")]); g = lambda q: anim(rk, t - q)
    body(c, rig.CAST["kumbhkaran"], f(0), GY + 20, 1.25, -1, T, 0, "roar", past=f); body(c, rig.CAST["ravan"], g(0), GY + 30, .95, 1, T, 0, "angry", past=g); burst(c, 520, 980, t - 1.1, 140); embers(c, T, 60); vig(c)
def s_megh(c, t, D, tk, T):
    cam(c, 1.05 + .08 * ss(t / D), 540, 960); bg(c, "megh", p_megh, 0, -t * 20)
    for e in (.4, 1.6, 2.6):
        if 0 <= t - e < .18: c.drawPaint(fill((200, 210, 255), .25 * (1 - (t - e) / .18))); bolt(c, t, int(e * 10), 200 + e * 220, -100, 1200, 1 - (t - e) / .18)
    v = lambda q: live(dict(pose("guard", x=600), j=300 + sin((T - q) * 1.4) * 24), T - q); aura(c, 540, 900, T, 420, (140, 120, 255)); body(c, rig.CAST["meghnad"], v(0), GY, 1.2, -1, T, 0, "angry", past=v, shadow=False)
    clouds(c, T, 60, 6, 3, (70, 70, 110), .7, 1500, 1900); vig(c)
def s_ramq(c, t, D, tk, T):
    cam(c, 1.7 + .1 * ss(t / D), 540, 820); bg(c, "sabha", p_sabha); stand(c, "ram", "talk", 540, T, 1.0, 1, GY + 30, talk=tk.get("R", 0), weapon=False, head=6); vig(c)
def s_chhaya(c, t, D, tk, T):
    cam(c, 1.0, 540, 1080); bg(c, "lanka", p_lanka, 30); u = ss(t / (D * .8))
    shadow_of(c, lambda: stand(c, "meghnad", "hero", 700, T, 1.3 + .9 * u, -1, GY + 40), a=.85)
    stand(c, "ravan", "stand", 230, T, .9, 1, GY + 40, mood="n"); stand(c, "meghnad", "hero", 830, T, .9, -1, GY + 40); embers(c, T, 40); vig(c)
def s_indra(c, t, D, tk, T):
    e = 1.1; sx, sy = punchcam(t, [(e, 1.4)]); c.translate(sx, sy); cam(c, 1.02, 540, 1060); bg(c, "swarg", p_swarg)
    ks = Keys(-1, 1.05, [(0, pose("hero", x=700), "io"), (e - .05, pose("guard", x=700), "io"), (e + .15, pose("hit", x=780, j=40), "hit"), (e + .8, pose("kneel", x=820), "out"), (9, pose("kneel", x=820), "io")]); f = lambda q: anim(ks, t - q)
    body(c, rig.CAST["indra"], f(0), GY - 60, 1.05, -1, T, 0, "sad" if t > e else "n", past=f, shadow=False)
    if t < e:
        k = ss(t / e) ** 1.5; x = -150 + 830 * k; y = 900 + 60 * k; glow(c, x, y, 150, (255, 200, 90), .8); c.drawLine(x - 420, y - 30, x, y, line((255, 190, 70), 34, .35)); c.drawLine(x - 300, y - 20, x, y, line((255, 230, 140), 16, .8))
        c.drawLine(x - 90, y - 6, x + 10, y, line((90, 50, 20), 9)); c.drawPath(poly([(x + 10, y - 16), (x + 50, y + 3), (x + 8, y + 16)]), fill((230, 236, 255))); c.drawPath(poly([(x - 90, y - 6), (x - 120, y - 26), (x - 104, y - 4), (x - 120, y + 14)]), fill((220, 50, 60)))
    burst(c, 700, 980, t - e, 220); clouds(c, T, 40, 5, 9, (255, 255, 255), .6, 1500, 1900); vig(c)
def s_katha(c, t, D, tk, T):
    cam(c, 1.1 + .15 * ss(t / D), 540, 1040 - 80 * ss(t / D)); bg(c, "dark", p_dark); r = random.Random(4)
    for i in range(40): a = i * .5 + T * .4; rr = 120 + i * 14; c.drawCircle(540 + cos(a) * rr, 640 + sin(a) * rr * .5 - i * 6, 60 + i * 2, fill((150, 110, 200), .05))
    aura(c, 540, 700, T, 380, (200, 160, 255)); stand(c, "agastya", "talk", 540, T, .9, 1, GY, talk=tk.get("A", 0), weapon=True); vig(c)
def s_raaz(c, t, D, tk, T):
    bg(c, "dark", p_dark); u = ss((t - .5) / 1.2); glow(c, 540, 860, 600 * u + 10, (255, 160, 60), .5)
    for x in (400, 680):
        q = smooth([(x - 110, 860), (x, 860 - 70 * u - 2), (x + 110, 860), (x, 860 + 50 * u + 2)]); c.drawPath(q, fill((255, 240, 210))); c.save(); c.clipPath(q, True); c.drawCircle(x, 860, 46, fill((200, 90, 30))); c.drawCircle(x, 860, 22, fill((10, 4, 6))); c.drawCircle(x + 14, 846, 9, fill((255, 255, 255))); c.restore(); c.drawPath(q, line((40, 20, 20), 8))
    embers(c, T, 30, (255, 200, 120)); vig(c)
def s_end(c, t, D, tk, T):
    cam(c, 1.0 + .18 * ss(t / D), 470, 1090 - 60 * ss(t / D)); bg(c, "sabha", p_sabha); stand(c, "agastya", "talk", 290, T, .8, 1, GY + 10, weapon=False, a1u=60 + 25 * sin(T * 2.4), a1f=100 + 20 * sin(T * 3)); stand(c, "ram", "namaste", 800, T, .94, -1, GY + 30, weapon=False); petals(c, T, 25, 8); vig(c)
    c.drawPaint(fill((10, 4, 20), .45 * ss((t - 3.2) / .5)))

N, AG, RM = (S, "+2%", "+0Hz"), (M, "-8%", "-14Hz"), (M, "+0%", "+4Hz")
def L(shot, w, v, hi, ro, **k): return dict(shot=shot, who=w, v=v, hi=hi, ro=ro, **k)
LINES = [
 L("hook", "N", N, "रावण से भी ज़्यादा शक्तिशाली... कौन था?", "Ravan se bhi *zyada* shaktishali... *kaun* tha?", pad=1.0),
 L("sabha", "N", N, "रावण का अंत हो चुका था। श्री राम अयोध्या के राजा थे।", "Ravan ka *ant* ho chuka tha. Shri Ram *Ayodhya* ke raja the.", pad=.6),
 L("rishi", "N", N, "एक दिन, चारों दिशाओं से महान ऋषि अयोध्या आए।", "Ek din, chaaron *dishaon* se mahan *rishi* Ayodhya aaye.", pad=.6),
 L("dwar", "A", AG, "द्वारपाल, राम को हमारे आने की सूचना दो।", "*Dwarpal,* Ram ko hamare aane ki *soochna* do."),
 L("swagat", "N", N, "राम जी उठे, और सबका आदर से स्वागत किया।", "Ram ji *uthe,* aur sabka aadar se *swagat* kiya.", pad=.8),
 L("prashansa", "N", N, "ऋषियों ने राम जी की विजय की प्रशंसा की।", "Rishiyon ne Ram ji ki *vijay* ki *prashansa* ki.", pad=.4),
 L("yuddh", "A", AG, "राम, तुमने रावण को हराया, कुंभकर्ण को भी।", "Ram, tumne *Ravan* ko haraya, *Kumbhkaran* ko bhi."),
 L("megh", "A", AG, "पर मेघनाद का अंत सुनकर, हम चकित रह गए!", "Par *Meghnad* ka ant sunkar, hum *chakit* reh gaye!", pad=.8),
 L("ramq", "R", RM, "मेघनाद? उसमें ऐसा क्या था?", "*Meghnad?* Usmein aisa *kya* tha?"),
 L("chhaya", "R", RM, "वो अपने पिता रावण से भी बढ़कर कैसे था?", "Woh apne pita *Ravan* se bhi *badhkar* kaise tha?"),
 L("indra", "R", RM, "उसने इंद्र तक को कैसे हरा दिया?", "Usne *Indra* tak ko kaise *hara* diya?", pad=1.0),
 L("katha", "A", AG, "ये जानने के लिए, पहले रावण के वंश की कथा सुनो।", "Ye jaanne ke liye, pehle Ravan ke *vansh* ki *katha* suno.", pad=.6),
 L("raaz", "N", N, "और फिर खुला, वो राज़...", "Aur phir khula, woh *raaz...*", pad=.8),
 L("end", "N", N, "अगले भाग में: रावण का वंश, एक महान ऋषि से कैसे शुरू हुआ?", "Agle bhaag mein: Ravan ka *vansh,* ek mahan *rishi* se kaise shuru hua?", pad=3.6),
]
SH = {k[2:]: v for k, v in list(globals().items()) if k.startswith("s_")}
HEAT = dict(prashansa=1, hook=2, sabha=0, rishi=0, dwar=0, swagat=1, yuddh=3, megh=2, ramq=0, chhaya=1, indra=3, katha=1, raaz=1, end=1)

def mus(n, tl):
    b = np.zeros(n); q = np.arange(n) / SR
    for f, a in ((110, .3), (165, .2), (220, .14)): b += a * np.sin(2 * pi * f * q + .4 * np.sin(2 * pi * .25 * q)) * (1 + .3 * np.sin(2 * pi * .35 * q + f))
    sc = [440, 494, 554, 659, 740, 880]; r = random.Random(7)
    for l in tl["lines"]:
        h = HEAT[l["shot"]]; t = l["start"]; k = 0; st = .16 if h == 3 else .2
        while t < l["end"] - .05:
            if h >= 1 and k % 8 in ((0, 4) if h < 3 else (0, 2, 3, 5, 6)): au.add(b, t, thump(), .8 if k % 8 == 0 else .55)
            if h >= 2 and k % 2: x = au.tarr(.09); au.add(b, t, np.sin(2 * pi * 380 * x) * np.exp(-x * 50), .3)
            if k % (4 if h else 6) == 0: f = r.choice(sc) / (2 if h == 3 else 1); x = au.tarr(1.0); au.add(b, t, (np.sin(2 * pi * f * x + .5 * np.sin(2 * pi * 5 * x)) + .3 * np.sin(4 * pi * f * x)) * np.minimum(1, x / .06) * np.exp(-x * 2.6), .2)
            t += st; k += 1
    return b
def fx(f, tl):
    wh = lambda t, g=.3, d=.35: au.add(f, t, au.band(au.noise(d), 500, 5000) * np.hanning(int(d * SR)), g)
    for l in tl["lines"]:
        s, D, n = l["start"], l["end"] - l["start"], l["shot"]; s > 0 and wh(s - .2, .1, .5)
        if n == "hook": au.add(f, s + .3, boom(1.6), .7)
        if n == "yuddh": au.add(f, s + 1.1, boom(.8), .7)
        if n in ("sabha", "swagat", "prashansa", "end"): au.add(f, s + .1, au.bell(660, 2.5), .35)
        if n == "yuddh": au.add(f, s + .2, boom(), .6)
        if n == "megh": [au.add(f, s + e, boom(1.2), .8) for e in (.4, 1.6, 2.6)]
        if n == "indra": wh(s + .2, .4, .9); au.add(f, s + 1.1, boom(1.3), 1.1)
        if n == "katha": au.add(f, s + .1, au.sweep(200, 700, 1.2, 3), .25)
        if n == "raaz": au.add(f, s + .5, au.bell(330, 3), .5)
if __name__ == "__main__": run("bhaag001", LINES, SH, ("RAMAYAN  |  BHAAG 1", "MEGHNAD KA RAAZ"), mus, fx)
