"""Ramayan bhaag 2 (Uttar kaand, sarg 2): Pulastya's curse, Trinabindu's daughter, the birth of Vishravas.
Script: scripts/002.md. Characters from cast/ramayan.json via the factory. 60 fps.
    python engine/bhaag002.py preview   -> out/preview_bhaag002.jpg
    python engine/bhaag002.py           -> out/sample_bhaag002.mp4
"""
import lab, rig
from rig import *
from lab import main as run, SR, M, S, au
from hanuman import cam, live, stand, embers, aura, vig, sky, stars, ground, clouds, thump, boom, GY, tree, seated
import factory as fa
from bhaag001 import petals, p_sabha, shadow_of
lab.FPS = 60; rig.SOFT = True
ss = lambda u: (lambda v: v * v * (3 - 2 * v))(max(0., min(1., u)))

# ---------------- cast: main people from the design file; the girls of the forest are one-time extras
CASTF = fa.load()
GIRL = lambda n, hair, crown, tilak, cl, eg, jw, wp, sk: dict(name=n, kind="human", sex="f", age="young", skin=sk, hair=hair, crown=crown, tilak=tilak, eyes="kind", top="blouse", lower="saree", cloth=cl, edge=eg, jewel=jw, weapon=wp, size=.86)
GIRLS = [GIRL("Kanya1", "braid", "none", "dot", [236, 110, 170], [255, 230, 150], [120, 60, 200], "lotus", "fair"),
         GIRL("Kanya2", "long", "tiara", "bindi", [250, 190, 40], [200, 60, 60], [40, 150, 200], "none", "wheat"),
         GIRL("Kanya3", "braid", "tiara", "dot", [130, 70, 200], [240, 236, 220], [250, 200, 70], "lotus", "brown")]
PUTRI = dict(name="Putri", kind="human", sex="f", age="young", skin="wheat", hair="long", hair_rgb=[40, 24, 30], crown="none", tilak="dot", eyes="calm", top="blouse", lower="saree", cloth=[30, 150, 150], edge=[240, 236, 220], jewel=[250, 200, 70], weapon="none", size=.9)
for sp in CASTF + GIRLS + [PUTRI]: rig.CAST[sp["name"].lower().replace(" ", "")] = fa.make(sp)

# ---------------- places, painted once
def p_meru(c):
    r = random.Random(21); sky(c, (250, 140, 120), (255, 228, 170)); glow(c, 540, 640, 700, (255, 250, 220), .8)
    mountains(c, r, 1120, 360, (200, 120, 120), (255, 236, 230))
    shape(c, poly([(-180, 1340), (160, 820), (330, 640), (440, 470), (540, 300), (650, 470), (760, 620), (930, 830), (1260, 1340)]), (244, 184, 70), 7)
    c.drawPath(poly([(540, 300), (650, 470), (760, 620), (930, 830), (1260, 1340), (640, 1340)]), fill((200, 130, 50), .45))
    c.drawPath(poly([(440, 470), (540, 300), (650, 470), (600, 450), (560, 500), (500, 450)]), fill((255, 250, 240)))
    for i in range(10): c.drawLine(200 + i * 80, 1320, 520 + i * 10, 420 + i * 30, line((255, 230, 140), 3, .35))
    for i in range(7): x = r.uniform(-200, W + 200); [c.drawCircle(x + q * 90, 1180 - abs(q) * 20, 120, fill((255, 240, 236), .85)) for q in range(-2, 3)]
    ground(c, (150, 104, 80), (255, 220, 170), r)
    shape(c, smooth([(300, 1340), (330, 1300), (540, 1285), (750, 1300), (780, 1340)]), (170, 130, 110), 5)
def p_van(c):
    r = random.Random(31); sky(c, (110, 196, 232), (232, 250, 222)); glow(c, 760, 500, 500, (255, 255, 230), .6)
    mountains(c, r, 1060, 440, (150, 176, 206), (250, 252, 255)); mountains(c, r, 1210, 220, (106, 160, 136), None)
    for x, h, g in ((330, 430, (70, 140, 90)), (760, 470, (80, 150, 86))): tree(c, x, 1300, h, r, g)
    for x, h in ((-60, 700), (1120, 760)): tree(c, x, 1340, h, r, (50, 126, 70))
    for x, y in ((-100, 640), (20, 580), (60, 700), (1030, 600), (1160, 560), (1200, 680), (300, 860), (800, 820)): c.drawCircle(x, y, 18, fill(r.choice([(255, 140, 40), (240, 60, 60), (255, 200, 40)])))
    ground(c, (110, 150, 80), (220, 240, 160), r, grass=(70, 130, 60))
    for _ in range(46):
        x, y = r.uniform(-200, W + 200), r.uniform(1350, 1900); g = r.choice([(255, 255, 255), (255, 200, 60), (250, 120, 170)])
        for k in range(5): a = k * 2 * pi / 5; c.drawCircle(x + cos(a) * 10, y + sin(a) * 6, 8, fill(g))
        c.drawCircle(x, y, 5, fill((250, 180, 40)))
def p_ashram2(c):
    r = random.Random(41); sky(c, (250, 190, 140), (255, 238, 204)); glow(c, 540, 900, 600, (255, 240, 200), .6)
    mountains(c, r, 1100, 380, (214, 150, 130), (255, 240, 230))
    for x, k in ((140, 1.0), (930, .9)):
        c.drawRect(skia.Rect.MakeLTRB(x - 150 * k, 1340 - 260 * k, x + 150 * k, 1340), fill((176, 120, 76))); [c.drawLine(x - 150 * k, y, x + 150 * k, y, line((130, 84, 50), 4)) for y in np.arange(1340 - 250 * k, 1340, 30 * k)]
        shape(c, poly([(x - 210 * k, 1340 - 250 * k), (x, 1340 - 480 * k), (x + 210 * k, 1340 - 250 * k)]), (210, 166, 80), 6); c.drawRect(skia.Rect.MakeLTRB(x - 40 * k, 1340 - 170 * k, x + 40 * k, 1340), fill((70, 40, 34)))
    for x in (330, 760): c.drawLine(x, 1340, x + 10, 900, line((110, 150, 70), 14)); [c.drawPath(smooth([(x + 10, 900 + q * 40), (x + 10 + d * 150, 860 + q * 50), (x + 10 + d * 200, 940 + q * 50)], False), line((90, 170, 70), 22)) for q in (0, 1) for d in (-1, 1)]
    shape(c, poly([(470, 1310), (490, 1260), (590, 1260), (610, 1310)]), (190, 110, 70), 5)
    for x in range(-200, W + 240, 90): c.drawLine(x, 1330, x, 1270, line((140, 96, 60), 8))
    c.drawLine(-200, 1290, W + 200, 1290, line((140, 96, 60), 6))
    ground(c, (196, 156, 104), (255, 236, 190), r, grass=(140, 150, 70))
def p_dhyan(c):
    r = random.Random(51); vgrad(c, [(0, (16, 8, 44)), (.6, (50, 20, 80)), (1, (90, 40, 90))], -240, H + 240); stars(c, r, 160, H)
    for k in range(6): c.drawCircle(540, 900, 160 + k * 110, line((200, 170, 255), 3, .18))
    c.drawRect(skia.Rect.MakeLTRB(-240, 1340, W + 240, H + 240), fill((40, 20, 60))); c.drawOval(skia.Rect.MakeLTRB(160, 1350, 920, 1500), fill((90, 60, 140), .6))
def p_prakash(c):
    vgrad(c, [(0, (255, 214, 150)), (1, (250, 150, 90))], -240, H + 240)
    for i in range(24): a = i * pi / 12; c.drawPath(poly([(540, 900), (540 + cos(a) * 2200, 900 + sin(a) * 2200), (540 + cos(a + .12) * 2200, 900 + sin(a + .12) * 2200)]), fill((255, 250, 220), .25))
    r = random.Random(61)
    for i in range(30): x, y, k = r.uniform(-240, W + 240), r.uniform(1300, 2000), r.uniform(.8, 1.5); [c.drawCircle(x + q * 80 * k, y - (2 - abs(q)) * 26 * k, 110 * k, fill((255, 246, 236), .9)) for q in range(-2, 3)]
def p_sagar(c):
    r = random.Random(71); sky(c, (40, 30, 96), (250, 140, 90), 1150); stars(c, r, 60, 500); glow(c, 760, 900, 600, (255, 200, 100), .6)
    shape(c, smooth([(420, 1160), (560, 900), (700, 820), (860, 860), (1000, 980), (1140, 1160)]), (90, 60, 90), 5)
    for x, h in ((600, 230), (660, 330), (720, 420), (780, 360), (840, 280), (900, 210)):
        c.drawRect(skia.Rect.MakeLTRB(x - 24, 900 - h + 120, x + 24, 1010), fill((250, 196, 60))); c.drawPath(poly([(x - 30, 900 - h + 124), (x, 900 - h + 40), (x + 30, 900 - h + 124)]), fill((255, 220, 90)))
        for k in range(3): c.drawRect(skia.Rect.MakeXYWH(x - 8, 900 - h + 150 + k * 60, 16, 26), fill((255, 250, 210)))
    c.drawRect(skia.Rect.MakeLTRB(-240, 1150, W + 240, H + 240), fill((30, 40, 100)))
    for y in range(1170, 1340, 18): c.drawLine(r.uniform(-200, 500), y, r.uniform(600, 1300), y, line((255, 180, 110), 3, .35))
    ground(c, (200, 160, 120), (255, 230, 190), r, GY - 60)

# ---------------- moving bits
def runner(c, who, x, t, s, d, y=GY + 20, w=9.):
    f = lambda q: (lambda u: dict(POSE["run"], x=x - d * q * 380, f1x=100 * sin(u * w), f2x=-100 * sin(u * w), f1y=max(0., 46 * cos(u * w)), f2y=max(0., -46 * cos(u * w)), a1u=-10 + 50 * sin(u * w), a2u=40 - 50 * sin(u * w), j=8 * abs(sin(u * w))))(t - q)
    body(c, rig.CAST[who], f(0), y, s, d, t, 0, "sad", past=f, weapon=False)
def dancer(c, who, x, T, s, d, i, y=GY + 20):
    f = lambda q: (lambda u: dict(POSE["stand"], x=x + 26 * sin(u * 1.6 + i), lean=6 * sin(u * 2.4 + i), head=10 * sin(u * 2.4 + i + 1), a1u=130 + 50 * sin(u * 3 + i), a1f=170 + 40 * sin(u * 3 + i + .8), a2u=90 + 50 * sin(u * 3 + i + 2), a2f=140 + 40 * sin(u * 3 + i + 2.6), f1x=50 + 26 * sin(u * 2.4 + i), f2x=-50 + 26 * sin(u * 2.4 + i), f1y=max(0., 30 * sin(u * 4.8 + i)), j=10 * abs(sin(u * 2.4 + i))))(T - q)
    body(c, rig.CAST[who], f(0), y, s, d, T, 0, "n", past=f, weapon=True)
def rings(c, x, y, t, rgb, n=3, R=900, v=700, w=16):
    for k in range(n): r = (t * v + k * R / n) % R; c.drawCircle(x, y, r + 10, line(rgb, w * (1 - r / R) + 1, .8 * (1 - r / R)))
def notes(c, T, n=12, seed=3, x0=380, x1=1040):
    r = random.Random(seed)
    for i in range(n):
        x = r.uniform(x0, x1) + sin(T * 2 + i) * 20; v = r.uniform(60, 120); u = ((T * v + r.uniform(0, 600)) % 700) / 700; y = 1060 - u * 700; a = .9 * (1 - u); g = r.choice([(255, 255, 255), (255, 220, 120), (255, 150, 200)])
        c.drawCircle(x, y, 14, fill(g, a)); c.drawLine(x + 12, y, x + 12, y - 60, line(g, 5, a)); c.drawLine(x + 12, y - 60, x + 36, y - 44, line(g, 5, a))
def waves(c, x, y, t, d=-1, rgb=(255, 236, 160)):
    for k in range(4):
        r = (t * 160 + k * 70) % 280 + 30; a = .8 * (1 - r / 310); o = skia.Rect.MakeLTRB(x - r, y - r, x + r, y + r)
        c.drawArc(o, 150 if d < 0 else -30, 60, False, line(rgb, 7, a))
def baby(c, x, y, k, T):
    c.save(); c.translate(x, y); c.scale(k, k); glow(c, 0, 0, 260, (255, 250, 220), .9)
    for i in range(8): a = i * pi / 4 + .2; shape(c, smooth([(0, 40), (cos(a) * 60 - 20, 40 + sin(a) * 30), (cos(a) * 150, 40 + sin(a) * 50 - 30), (cos(a) * 60 + 20, 40 + sin(a) * 30)]), (250, 150, 180), 3)
    shape(c, oval(0, 0, 110, 70), (255, 246, 226), 5); shape(c, oval(-60, -20, 46), rig.CAST["vishrava"]["skin"], 5)
    for e in (-74, -46): c.drawPath(smooth([(e - 6, -26), (e, -22), (e + 6, -26)], False), line(rig.INK, 3))
    c.drawPath(smooth([(-20, -50), (60, -40), (100, 20)], False), line((240, 200, 70), 8)); c.restore()

# ---------------- shots: c, t (time in shot), D (shot length), tk (talk per speaker), T (time in video)
def s_hook(c, t, D, tk, T):
    sx, sy = punchcam(t, [(.3, 1.2)]); c.translate(sx, sy); cam(c, 1.2 - .14 * ss(t / D), 540, 1120); bg(c, "van", p_van)
    c.drawPaint(fill((120, 20, 30), .28)); rings(c, 560, 1030, t, (255, 150, 60))
    for i, (who, x0, d) in enumerate((("kanya1", 230, -1), ("kanya2", 860, 1), ("kanya3", 110, -1))): runner(c, who, x0 + d * 460 * ss(t / (D * .8)) * (1 + i * .3), T + i, .74, d, GY + 30 + i * 10)
    seated(c, "pulastya", 540, 1440, 1.0, 1, T, 0, "angry")
    embers(c, T, 50); vig(c)
def s_katha(c, t, D, tk, T):
    u = ss(t / D); cam(c, 1.1 - .08 * u, 540, 1060 + 30 * u); bg(c, "sabha", p_sabha)
    stand(c, "agastya", "talk", 320, T, .8, 1, GY + 10, talk=tk.get("A", 0), weapon=False, a1u=60 + 25 * sin(T * 2.4), a1f=100 + 20 * sin(T * 3))
    stand(c, "ram", "stand", 800, T, .94, -1, GY + 30, weapon=False, head=8 + 6 * sin(T * 1.2)); petals(c, T, 20, 4); vig(c)
def s_meru(c, t, D, tk, T):
    u = ss(t / D); cam(c, 1.0 + .12 * u, 540, 760 + 360 * u); bg(c, "meru", p_meru); aura(c, 540, 1080, T, 380 * ss(t / 1.5) + 20, (255, 236, 150))
    stand(c, "pulastya", "hero", 540, T, .95, 1, GY - 40, weapon=True, shadow=False); clouds(c, T, 60, 5, 4, (255, 246, 240), .6, 1300, 1700); vig(c)
def s_naach(c, t, D, tk, T):
    cam(c, 1.05, 560 + 30 * ss(t / D), 1080); bg(c, "van", p_van, -20 * t)
    seated(c, "pulastya", 195, 1450, .72, 1, T, 0, "angry" if t > D * .6 else "n")
    for i, (who, x) in enumerate((("kanya1", 480), ("kanya2", 730), ("kanya3", 980))): dancer(c, who, x, T, .7, -1, i * 1.7, GY + 30 - i * 6)
    notes(c, T); petals(c, T, 18, 6); vig(c)
def s_shraap(c, t, D, tk, T):
    sx, sy = punchcam(t, [(D * .55, 1.0)]); c.translate(sx, sy); cam(c, 1.5 + .12 * ss(t / D), 560, 1150); bg(c, "van", p_van, 60)
    c.drawPaint(fill((140, 30, 20), .3 * ss(t / 1.0))); aura(c, 560, 1100, T, 520, (255, 110, 50)); rings(c, 580, 1040, t, (255, 170, 80), 3, 700, 500, 10)
    seated(c, "pulastya", 540, 1440, 1.0, 1, T, tk.get("P", 0), "angry"); embers(c, T, 40); vig(c)
def s_bhaag(c, t, D, tk, T):
    cam(c, 1.0, 540, 1080); bg(c, "van", p_van, -40 - 30 * t); h = D * .45
    if t < h:
        for i, (who, x0) in enumerate((("kanya2", 420), ("kanya1", 600), ("kanya3", 760))): runner(c, who, x0 + 700 * ss((t - i * .15) / h), T + i, .8, 1, GY + 30 - i * 8)
    else:
        q = t - h; x = 260 + 160 * ss(q / (D - h)); look = 30 * sin(q * 2.2)
        stand(c, "putri", "stand", x, T, .88, 1 if sin(q * 2.2) > -.3 else -1, GY + 30, weapon=False, head=look, a1u=70 + 20 * sin(q * 3), a1f=120)
    petals(c, T, 14, 9); vig(c)
def s_ved(c, t, D, tk, T):
    cam(c, 1.06 + .1 * ss(t / D), 560, 1090); bg(c, "van", p_van, 40)
    waves(c, 760, 1060, T); seated(c, "pulastya", 820, 1450, .86, -1, T, .5 + .5 * sin(T * 9), "n")
    x = 120 + 260 * ss(t / (D * .8)); stand(c, "putri", "stand" if t < D * .8 else "namaste", x, T, .88, 1, GY + 30, weapon=False, head=6)
    glow(c, 640, 1040, 300, (255, 240, 180), .3); vig(c)
def s_hairan(c, t, D, tk, T):
    cam(c, 1.45 + .1 * ss(t / D), 540, 1080); bg(c, "van", p_van, -80); k = .5 + .5 * sin(T * 5)
    aura(c, 540, 1060, T, 420 + 40 * k, (200, 230, 255)); glow(c, 540, 1100, 300, (255, 255, 255), .25 + .2 * k)
    stand(c, "putri", "stand", 540, T, .95, 1, GY + 20, talk=tk.get("D", 0), mood="sad", weapon=False, a1u=60, a1f=150, a2u=50, a2f=150, head=-8 + 10 * sin(T * 1.5)); embers(c, T, 30, (220, 240, 255)); vig(c)
def s_pita(c, t, D, tk, T):
    cam(c, 1.1 - .06 * ss(t / D), 540, 1080); bg(c, "ashram", p_ashram2, 30 - 20 * t)
    fire = .5 + .3 * sin(T * 11) * sin(T * 7); glow(c, 540, 1230, 140, (255, 150, 50), fire); c.drawPath(smooth([(510, 1262), (525, 1210 - 20 * fire), (540, 1180 - 30 * fire), (556, 1214), (570, 1262)]), fill((255, 170, 50)))
    stand(c, "putri", "namaste", 310, T, .88, 1, GY + 30, weapon=False, head=22, mood="sad")
    stand(c, "trinabindu", "talk", 780, T, .95, -1, GY + 20, talk=tk.get("T", 0), weapon=False, a1u=60 + 20 * sin(T * 2), a1f=110); vig(c)
def s_dhyan(c, t, D, tk, T):
    u = ss(t / D); cam(c, 1.05 + .2 * u, 540, 1100 - 60 * u); bg(c, "dhyan", p_dhyan)
    for k in range(3):
        c.save(); c.translate(540, 1000); c.rotate(T * (12 + k * 8) * (-1) ** k); R = 260 + k * 130
        for i in range(12): a = i * pi / 6; c.drawCircle(cos(a) * R, sin(a) * R, 10 + k * 3, fill((255, 220, 150), .6 * u + .2))
        c.restore()
    aura(c, 540, 1060, T, 300 + 200 * u, (190, 160, 255)); seated(c, "trinabindu", 540, 1440, .95, 1, T, 0, "n")
    glow(c, 572, 1036, 60 + 40 * u, (255, 240, 200), .5 + .4 * u); vig(c)
def s_daan(c, t, D, tk, T):
    cam(c, 1.0 + .06 * ss(t / D), 540, 1080); bg(c, "van", p_van, 10)
    stand(c, "putri", "namaste", 160, T, .84, 1, GY + 30, weapon=False, head=18)
    stand(c, "trinabindu", "namaste" if t > D * .6 else "talk", 440, T, .9, 1, GY + 24, talk=tk.get("T", 0), weapon=False)
    stand(c, "pulastya", "stand", 900, T, .92, -1, GY + 20, weapon=False, head=6 * sin(T * 1.3)); petals(c, T, 12, 3); vig(c)
def s_vivah(c, t, D, tk, T):
    cam(c, 1.08 - .06 * ss(t / D), 540, 1080); bg(c, "van", p_van, -30)
    xt = 160 - 420 * ss((t - D * .35) / (D * .6)); stand(c, "trinabindu", "stand", xt, T, .82, -1, GY + 14, weapon=False) if xt > -200 else None
    stand(c, "putri", "namaste", 380, T, .88, 1, GY + 30, weapon=False, head=12)
    stand(c, "pulastya", "stand", 780, T, .94, -1, GY + 20, weapon=False, a1u=110 * ss((t - .4) / .8) + 30, a1f=150, head=8); petals(c, T, 60, 12); aura(c, 570, 1000, T, 340, (255, 230, 170)); vig(c)
def s_vardan(c, t, D, tk, T):
    cam(c, 1.28 + .08 * ss(t / D), 560, 1060); bg(c, "van", p_van, 80); u = ss((t - .6) / (D * .7))
    glow(c, 540, 720, 60 + 200 * u, (255, 236, 160), .9); c.drawCircle(540, 720, 10 + 40 * u, fill((255, 252, 230), .9))
    stand(c, "putri", "namaste", 330, T, .9, 1, GY + 30, weapon=False, head=10)
    stand(c, "pulastya", "talk", 770, T, .95, -1, GY + 20, talk=tk.get("P", 0), weapon=False, a1u=140 + 10 * sin(T * 2), a1f=160); embers(c, T, 30, (255, 230, 150)); vig(c)
def s_janm(c, t, D, tk, T):
    h = D * .45; bg(c, "prakash", p_prakash, 0, -10 * t)
    if t < h:
        cam(c, 1.3 - .2 * ss(t / h), 540, 1000); aura(c, 540, 1000, T, 500, (255, 250, 220)); baby(c, 540, 1040 + 10 * sin(T * 2), 1.6, T)
    else:
        q = t - h; u = ss(q / 1.0); cam(c, 1.0 + .06 * ss(q / (D - h)), 540, 1080)
        c.drawPaint(fill((60, 20, 30), .35 * u)); c.save(); c.translate(0, 200 * (1 - u)); shadow_of(c, lambda: stand(c, "ravan", "guard", 560, T, 1.55 + .2 * u, 1, GY + 80, weapon=True), a=.9); c.restore()
        stand(c, "vishrava", "stand", 540, T, 1.0, 1, GY + 30, weapon=True, a1u=60, a1f=120); c.drawPaint(fill((255, 250, 230), 1 - ss(q / .35)))
    embers(c, T, 40, (255, 230, 160)); vig(c)
def s_end(c, t, D, tk, T):
    cam(c, 1.0 + .2 * ss(t / D), 640, 1060 - 40 * ss(t / D)); bg(c, "sagar", p_sagar); glow(c, 760, 900, 260 + 30 * sin(T * 3), (255, 220, 120), .5)
    stand(c, "vishrava", "point", 250, T, .9, 1, GY + 20, weapon=True, head=-8); embers(c, T, 30, (255, 210, 120)); vig(c)
    c.drawPaint(fill((10, 4, 20), .45 * ss((t - 3.2) / .5)))

N, AG, PU, TB, PT = (S, "+2%", "+0Hz"), (M, "-8%", "-14Hz"), (M, "-4%", "-16Hz"), (M, "+4%", "-12Hz"), (S, "+6%", "+25Hz")
def L(shot, w, v, hi, ro, **k): return dict(shot=shot, who=w, v=v, hi=hi, ro=ro, **k)
LINES = [
 L("hook", "N", N, "एक ऋषि का श्राप... और यहीं से शुरू हुआ रावण का वंश!", "Ek rishi ka *shraap...* aur yahin se shuru hua *Ravan* ka vansh!", pad=.8),
 L("katha", "A", AG, "राम, पहले रावण के जन्म और वंश की कथा सुनो।", "Ram, pehle Ravan ke *janm* aur *vansh* ki katha suno.", pad=.5),
 L("meru", "N", N, "सतयुग में थे, प्रजापति के पुत्र, महर्षि पुलस्त्य।", "Satyug mein the, Prajapati ke putra, *Maharishi Pulastya.*", pad=.5),
 L("naach", "N", N, "मेरु पर्वत पर वे तप करते, पर कन्याएँ वहाँ आकर गातीं, नाचतीं...", "Meru parvat par woh *tap* karte, par kanyayein wahan aakar gaatin, *naachtin...*", pad=.4),
 L("shraap", "P", PU, "जो कन्या मेरी दृष्टि में आएगी, वह गर्भवती हो जाएगी!", "Jo kanya meri *drishti* mein aayegi, woh *garbhvati* ho jayegi!", pad=.7),
 L("bhaag", "N", N, "डर कर सब भाग गईं... पर तृणबिंदु की बेटी ने ये श्राप सुना ही नहीं।", "Darr kar sab *bhaag* gayin... par Trinabindu ki beti ne ye shraap *suna hi nahin.*", pad=.4),
 L("ved", "N", N, "वेद-पाठ की आवाज़ सुनकर, वो ऋषि के सामने आ गई।", "*Ved-paath* ki awaaz sunkar, woh rishi ke *saamne* aa gayi.", pad=.4),
 L("hairan", "D", PT, "अरे! ये मुझे क्या हो गया?", "Arre! Ye mujhe *kya* ho gaya?", pad=.6),
 L("pita", "T", TB, "बेटी, ये तुम्हारी कैसी दशा है?", "Beti, ye tumhari *kaisi* dasha hai?", pad=.4),
 L("dhyan", "N", N, "तृणबिंदु ने ध्यान लगाया, और श्राप का सच जान लिया।", "Trinabindu ne *dhyan* lagaya, aur shraap ka *sach* jaan liya.", pad=.4),
 L("daan", "T", TB, "हे महर्षि, मेरी इस बेटी को स्वीकार कीजिए। ये सदा आपकी सेवा करेगी।", "He Maharishi, meri is beti ko *sweekar* kijiye. Ye sada aapki *seva* karegi.", pad=.4),
 L("vivah", "N", N, "ऋषि ने कहा, ठीक है। उसके गुणों से वे बहुत प्रसन्न हुए।", "Rishi ne kaha, 'Theek hai.' Uske *gunon* se woh bahut *prasann* hue.", pad=.4),
 L("vardan", "P", PU, "तुमने मेरा वेद-पाठ सुना था, इसलिए हमारा पुत्र विश्रवा कहलाएगा।", "Tumne mera ved-paath *suna* tha, isliye hamara putra *Vishrava* kahlayega.", pad=.5),
 L("janm", "N", N, "और जन्मे तपस्वी विश्रवा... यही आगे बने, रावण के पिता!", "Aur janme tapasvi *Vishrava...* yahi aage bane, *Ravan* ke pita!", pad=.9),
 L("end", "N", N, "अगले भाग में: कुबेर को लंका कैसे मिली?", "Agle bhaag mein: *Kuber* ko *Lanka* kaise mili?", pad=3.6),
]
SH = {k[2:]: v for k, v in list(globals().items()) if k.startswith("s_")}
HEAT = dict(hook=3, katha=1, meru=1, naach=1, shraap=3, bhaag=2, ved=0, hairan=1, pita=0, dhyan=1, daan=0, vivah=1, vardan=1, janm=2, end=1)

def mus(n, tl):
    b = np.zeros(n); q = np.arange(n) / SR
    for f, a in ((98, .3), (147, .2), (196, .14)): b += a * np.sin(2 * pi * f * q + .4 * np.sin(2 * pi * .25 * q)) * (1 + .3 * np.sin(2 * pi * .35 * q + f))
    sc = [392, 440, 523, 587, 659, 784]; r = random.Random(8)
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
        if n == "hook": au.add(f, s + .3, boom(1.6), .8)
        if n == "shraap": au.add(f, s + D * .55, boom(1.3), .9)
        if n in ("katha", "vivah", "end"): au.add(f, s + .1, au.bell(660, 2.5), .35)
        if n == "bhaag": wh(s + .2, .35, .7)
        if n == "ved": au.add(f, s + .2, au.bell(440, 3), .3)
        if n == "hairan": au.add(f, s + .1, au.sweep(300, 900, 1.0, 3), .25)
        if n == "dhyan": au.add(f, s + .2, au.bell(220, 3.5), .5)
        if n == "vardan": au.add(f, s + .6, au.sweep(200, 800, 1.6, 3), .25)
        if n == "janm": au.add(f, s + .1, au.bell(880, 2.5), .4); au.add(f, s + D * .45, boom(1.2), .7)
if __name__ == "__main__": run("bhaag002", LINES, SH, ("RAMAYAN  |  BHAAG 2", "VISHRAVA KA JANM"), mus, fx)
