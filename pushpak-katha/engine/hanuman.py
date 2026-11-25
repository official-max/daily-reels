"""Sample 6: Hanuman ji aur Kalnemi. Action rig, keyframed fight, 60 fps."""
import lab
from rig import *
from lab import main as run, SR, M, S, au
lab.FPS = 60
_env = au.lip_env
def _lip(x): e = np.array(_env(x)); n = len(e) * 2; e = np.interp(np.arange(n) / 2, range(len(e)), e); k = np.hanning(9); return list(np.convolve(e, k / k.sum(), "same"))
au.lip_env = _lip
GY = 1400
ss = lambda u: (lambda v: v * v * (3 - 2 * v))(max(0., min(1., u)))

# ---------------- places (painted once each)
def sky(c, top, bot, gy=GY): c.save(); c.translate(-320, -320); c.scale(1.7, 1.0); vgrad(c, [(0, top), (1, bot)], 0, gy + 700); c.restore()
def stars(c, r, n=120, y=900): [c.drawCircle(r.uniform(-150, W + 150), r.uniform(-150, y), r.uniform(1, 4), fill((255, 248, 220), r.uniform(.4, 1))) for _ in range(n)]
def moon(c, x, y, R=110): glow(c, x, y, R * 4.2, (200, 220, 255), .5); c.drawCircle(x, y, R, fill((250, 246, 226))); [c.drawCircle(x + a * R, y + b * R, q * R, fill((226, 220, 204))) for a, b, q in ((-.3, -.2, .22), (.35, .25, .16), (.1, -.45, .12), (-.15, .42, .18))]
def ground(c, rgb, lt, r, gy=GY - 70, grass=None):
    c.drawRect(skia.Rect.MakeLTRB(-320, gy, W + 320, H + 340), fill(rgb)); c.drawRect(skia.Rect.MakeLTRB(-320, gy, W + 320, gy + 8), fill(lt, .6))
    for _ in range(70):
        x, y = r.uniform(-150, W + 150), r.uniform(gy + 20, H + 100); k = .4 + (y - gy) / 420
        if grass and r.random() < .6: [c.drawLine(x + q * 7 * k, y, x + q * 18 * k, y - 34 * k, line(mix(grass, (0, 0, 0), r.uniform(0, .3)), 6 * k)) for q in (-1, 0, 1)]
        else: c.drawOval(skia.Rect.MakeXYWH(x, y, 54 * k, 16 * k), fill(mix(rgb, (0, 0, 0) if r.random() < .6 else lt, .25)))
def tree(c, x, y, h, r, lf, tr=(64, 44, 44)):
    c.drawPath(smooth([(x - 34, y + 10), (x - 16, y - h * .5), (x - 14, y - h), (x + 14, y - h), (x + 18, y - h * .5), (x + 40, y + 10)]), fill(tr)); [c.drawCircle(x + cos(q) * 110, y - h + sin(q) * 70, r.uniform(70, 110), fill(mix(lf, (0, 0, 20), .25 - .05 * q))) for q in range(6)]; [c.drawCircle(x + cos(q) * 100 - 14, y - h + sin(q) * 64 - 22, 50, fill(mix(lf, (255, 255, 200), .12))) for q in range(6)]
def p_camp(c):
    r = random.Random(3); sky(c, (18, 18, 52), (120, 60, 90)); stars(c, r); moon(c, 850, 380, 80); mountains(c, r, 1260, 300, (54, 40, 80), None)
    for x, k in ((-40, 1.1), (300, .8), (790, .9), (1100, 1.1)): c.drawPath(poly([(x - 170 * k, 1340), (x, 1340 - 330 * k), (x + 170 * k, 1340)]), fill((130, 60, 60))); c.drawPath(poly([(x, 1340 - 330 * k), (x + 170 * k, 1340), (x + 40 * k, 1340)]), fill((92, 40, 56))); c.drawLine(x, 1340 - 330 * k, x, 1340 - 430 * k, line((40, 24, 40), 8)); c.drawPath(poly([(x, 1340 - 430 * k), (x + 90 * k, 1340 - 400 * k), (x, 1340 - 370 * k)]), fill((250, 150, 40)))
    ground(c, (70, 48, 66), (200, 130, 110), r)
    for x in (60, 1010): c.drawLine(x, 1500, x, 1230, line((50, 30, 34), 18)); glow(c, x, 1190, 300, (255, 160, 60), .7); c.drawPath(smooth([(x - 34, 1230), (x - 30, 1180), (x, 1110), (x + 30, 1180), (x + 34, 1230)]), fill((255, 150, 40))); c.drawPath(smooth([(x - 16, 1230), (x, 1160), (x + 16, 1230)]), fill((255, 240, 150)))
def p_fly(c): r = random.Random(8); sky(c, (10, 20, 64), (70, 110, 180), H); stars(c, r, 160, 1300); moon(c, 760, 520, 200); mountains(c, r, 1720, 480, (60, 90, 150), (220, 234, 255)); mountains(c, r, 1900, 420, (34, 54, 104), (170, 196, 236))
def p_palace(c):
    r = random.Random(2); sky(c, (40, 6, 20), (170, 40, 30));
    for x in range(-100, W + 200, 270): c.drawRect(skia.Rect.MakeLTRB(x, 200, x + 80, 1340), fill((70, 18, 30))); c.drawRect(skia.Rect.MakeLTRB(x, 200, x + 24, 1340), fill((110, 34, 36))); c.drawRect(skia.Rect.MakeLTRB(x - 26, 1270, x + 106, 1340), fill((130, 60, 40))); c.drawRect(skia.Rect.MakeLTRB(x - 26, 190, x + 106, 260), fill((130, 60, 40)))
    ground(c, (60, 20, 34), (240, 120, 60), r); glow(c, 540, 900, 700, (255, 90, 30), .5)
def p_ashram(c):
    r = random.Random(12); sky(c, (24, 60, 92), (170, 206, 190)); stars(c, r, 40, 500); moon(c, 250, 360, 90); mountains(c, r, 1200, 520, (96, 130, 160), (236, 244, 250)); mountains(c, r, 1290, 260, (60, 100, 110), None);
    c.drawRect(skia.Rect.MakeLTRB(-320, 1215, W + 320, 1330), fill((70, 150, 180))); [c.drawLine(r.uniform(-100, 600), y, r.uniform(600, 1200), y, line((220, 245, 250), 3, .4)) for y in range(1228, 1325, 16)]
    tree(c, 60, 1340, 620, r, (50, 120, 70)); tree(c, 1040, 1340, 720, r, (60, 130, 66)); c.drawRect(skia.Rect.MakeLTRB(700, 1090, 960, 1350), fill((150, 104, 66))); [c.drawLine(700, y, 960, y, line((110, 70, 44), 4)) for y in range(1110, 1350, 30)]; c.drawPath(poly([(640, 1120), (830, 900), (1020, 1120)]), fill((176, 130, 66))); [c.drawLine(830 + q * 20, 910 + abs(q) * 8, 830 + q * 42, 1118, line((130, 90, 44), 5)) for q in range(-4, 5)]; c.drawRect(skia.Rect.MakeLTRB(790, 1170, 870, 1350), fill((56, 34, 34)))
    ground(c, (92, 110, 70), (220, 230, 150), r, grass=(60, 120, 60))
def p_water(c):
    r = random.Random(5); sky(c, (60, 170, 190), (6, 40, 80), H); [c.drawPath(poly([(x, -200), (x + 90, -200), (x + 330, H), (x + 60, H)]), fill((220, 255, 250), .09)) for x in range(-300, 1100, 190)]
    c.drawPath(smooth([(-250, 1900), (-100, 1640), (200, 1700), (520, 1600), (800, 1690), (1200, 1610), (1500, 1700), (1500, 2300), (-400, 2300), (-400, 1800)]), fill((20, 60, 70))); [c.drawPath(smooth([(x - 14, 1760), (x + 30, 1560), (x - 24, 1400), (x + 20, 1250), (x + 34, 1400), (x + 6, 1560), (x + 20, 1760)]), fill((30, 110, 80))) for x in (40, 150, 900, 1020)]
def p_arena(c):
    r = random.Random(21); sky(c, (30, 14, 50), (214, 90, 60)); glow(c, 540, 1050, 800, (255, 170, 80), .55); c.drawCircle(540, 980, 190, fill((255, 190, 100), .9)); mountains(c, r, 1240, 560, (104, 50, 84), (240, 170, 150)); mountains(c, r, 1320, 280, (66, 30, 62), None)
    for x, h in ((-30, 640), (1110, 700)): c.drawPath(smooth([(x - 60, 1360), (x - 30, 1360 - h * .5), (x - 10, 1360 - h), (x + 16, 1360 - h * .5), (x + 60, 1360)]), fill((36, 18, 40))); [c.drawLine(x, 1360 - h * (.5 + q * .12), x + (q % 2 * 2 - 1) * 190, 1360 - h * (.7 + q * .12), line((36, 18, 40), 16 - q * 3)) for q in range(4)]
    ground(c, (110, 66, 66), (255, 180, 120), r)
def p_peak(c):
    r = random.Random(30); sky(c, (14, 16, 60), (90, 90, 160)); stars(c, r, 150); moon(c, 820, 400, 120); mountains(c, r, 1280, 520, (64, 70, 130), (220, 228, 255)); ground(c, (54, 66, 90), (190, 210, 255), r, grass=(60, 130, 120))
    for _ in range(40): x, y = r.uniform(-100, W + 100), r.uniform(1340, 1850); g = r.choice([(120, 255, 190), (255, 220, 120), (150, 210, 255), (255, 150, 220)]); glow(c, x, y - 20, 60, g, .8); [c.drawPath(smooth([(x, y), (x + q * 16, y - 26), (x + q * 8, y - 50)]), fill(g)) for q in (-1, 0, 1)]
def p_dawn(c):
    r = random.Random(44); sky(c, (90, 120, 190), (255, 206, 150)); glow(c, 540, 1180, 900, (255, 240, 180), .8); c.drawCircle(540, 1180, 170, fill((255, 244, 200))); mountains(c, r, 1300, 260, (190, 130, 140), None)
    for x, k in ((40, 1.0), (1050, 1.0)): c.drawPath(poly([(x - 170 * k, 1340), (x, 1340 - 330 * k), (x + 170 * k, 1340)]), fill((214, 96, 70))); c.drawPath(poly([(x, 1340 - 330 * k), (x + 170 * k, 1340), (x + 40 * k, 1340)]), fill((176, 70, 64)))
    ground(c, (190, 140, 100), (255, 240, 200), r, grass=(120, 150, 70))
def clouds(c, t, v=300, n=9, seed=1, rgb=(230, 240, 255), a=.5, y0=200, y1=1800):
    r = random.Random(seed)
    for i in range(n):
        x, y, k = r.uniform(0, 1700), r.uniform(y0, y1), r.uniform(.6, 1.5); x = (x - t * v * k) % 1800 - 400
        for q in range(5): c.drawOval(skia.Rect.MakeXYWH(x + q * 70 * k, y - (2 - abs(2 - q)) * 24 * k, 150 * k, 80 * k), fill(rgb, a))
def speed(c, t, n=16, seed=3):
    r = random.Random(seed)
    for i in range(n): y, l, k = r.uniform(150, 1800), r.uniform(120, 380), r.uniform(1800, 3200); x = (r.uniform(0, 2000) - t * k) % 2000 - 400; c.drawLine(x, y, x + l, y, line((255, 255, 255), 4, .45))
def embers(c, t, n=40, rgb=(255, 170, 70)):
    r = random.Random(6)
    for i in range(n): x, y, v = r.uniform(0, W), r.uniform(0, H), r.uniform(60, 190); c.drawCircle(x + sin(t * 1.6 + i) * 34, (y - t * v) % H, r.uniform(2, 6), fill(rgb, .75))
def aura(c, x, y, t, r=420, rgb=(255, 200, 90)):
    glow(c, x, y, r, rgb, .55)
    for i in range(16): a = i * pi / 8 + t * .25; c.drawPath(poly([(x + cos(a - .05) * r * .5, y + sin(a - .05) * r * .5), (x + cos(a) * r * (1.05 + .08 * sin(t * 2 + i)), y + sin(a) * r * 1.05), (x + cos(a + .05) * r * .5, y + sin(a + .05) * r * .5)]), fill(rgb, .22))
def vig(c):
    if "vig" not in _BG: s = skia.Surface(W, H); s.getCanvas().drawPaint(skia.Paint(Shader=skia.GradientShader.MakeRadial(skia.Point(W / 2, H * .46), 1250, [col((0, 0, 0), 0), col((0, 0, 20), .62)], [.5, 1]))); _BG["vig"] = s.makeImageSnapshot()
    c.save(); c.resetMatrix(); c.drawImage(_BG["vig"], 0, 0); c.restore()
from rig import _BG
def cam(c, z, x=540, y=1000): c.translate(540, 960); c.scale(z, z); c.translate(-x, -y)
def live(v, t, a=1.): return dict(v, h=v["h"] + sin(t * 2.6) * 4 * a, lean=v["lean"] + sin(t * 2.6 - .6) * 1.2 * a, a1u=v["a1u"] + sin(t * 2.2) * 3 * a, a1f=v["a1f"] + sin(t * 2.2 - .7) * 5 * a, a2u=v["a2u"] + sin(t * 2.0 + 1) * 3 * a, a2f=v["a2f"] + sin(t * 2 + .4) * 4 * a, head=v["head"] + sin(t * 1.9) * 2 * a)
def stand(c, who, n, x, t, s=1., d=1, y=GY, **k):
    kw = {q: k.pop(q) for q in list(k) if q in ("talk", "mood", "weapon", "shadow")}; f = lambda q: live(pose(n, x=x, **k), t - q); return body(c, who, f(0), y, s, d, t, past=f, **kw)
def fly(c, t, x, y, s=1., carry=None, d=1):
    f = lambda q: (lambda u: dict(POSE["fly"], x=x + sin(u * 1.1) * 26, j=sin(u * 1.7) * 26, rot=66 + sin(u * 1.7 + 1) * 4, f1y=-8 + sin(u * 5) * 10, f2y=34 + sin(u * 5 + 2) * 12, a2u=-20 + sin(u * 3) * 6))(t - q); v = f(0)
    v_ = v
    if carry:
        v_ = dict(v, a2u=236., a2f=246.); J = solve(v_, 1.12)
        h = world(J["a2"][2], v_, y, s, d); carry(c, h[0], h[1])
    old = f; body(c, "hanuman", v_, y, s, d, t, past=lambda q: dict(old(q), x=v_["x"] - 320 * q), weapon=not carry, shadow=False)
def mountain(c, x, y, k=1.):
    c.save(); c.translate(x, y); c.scale(k, k); glow(c, 0, -260, 640, (150, 255, 200), .45)
    shape(c, smooth([(-330, -40), (-260, -190), (-190, -260), (-120, -440), (-30, -390), (40, -540), (130, -380), (200, -330), (270, -180), (350, -50), (230, 0), (120, 40), (0, 20), (-130, 50), (-240, 10)]), (96, 110, 120), 8); c.drawPath(poly([(-150, -370), (-118, -430), (-60, -395), (-96, -340), (-120, -360)]), fill((240, 248, 255))); c.drawPath(poly([(0, -470), (40, -530), (92, -440), (60, -410), (40, -440), (16, -420)]), fill((240, 248, 255)))
    r = random.Random(4)
    for _ in range(30): a, b = r.uniform(-260, 280), r.uniform(-240, -40); g = r.choice([(120, 255, 170), (255, 220, 120), (255, 150, 220)]); c.drawCircle(a, b, r.uniform(8, 18), fill(g)); c.drawPath(poly([(a - 20, b + 34), (a, b), (a + 20, b + 34)]), fill((40, 120, 80)))
    c.restore()
def seated(c, who, x, y, s, d, t, talk=0., mood="n", v=None):
    """Cross-legged person."""
    p = CAST[who]; c.save(); c.translate(x, y); c.scale(s * d, s); c.drawOval(skia.Rect.MakeLTRB(-230, -30, 230, 40), fill((0, 0, 0), .4, 14)); shape(c, smooth([(-220, 10), (-190, -80), (-60, -140), (60, -140), (190, -80), (220, 10), (0, 30)]), p["cloth"]); c.drawPath(smooth([(-180, -40), (0, 0), (180, -40)], False), line(mix(p["cloth"], INK, .4), 6)); shape(c, smooth([(-70, -60), (-90, -220), (-60, -300), (0, -320), (60, -300), (90, -220), (70, -60)]), p["skin"]); c.drawPath(smooth([(-60, -290), (0, -180), (60, -80)], False), line(INK, 30)); c.drawPath(smooth([(-60, -290), (0, -180), (60, -80)], False), line(p["edge"], 20))
    b = sin(t * 2) * 5; shape(c, limb2((-80, -270), (-120, -160), (-90, -80 + b * .3), (28, 22, 17)), mix(p["skin"], INK, .2)); c.save(); c.translate(0, -306 + b * .5); c.rotate(sin(t * 1.8) * 2); HEADS[p["head"]](c, t, talk, mood, p); c.restore()
    u = ss(talk * 3) * 10; shape(c, limb2((84, -270), (140, -170), (200, -230 - b - u), (30, 24, 18)), p["skin"]); shape(c, oval(204, -242 - b - u, 24), p["skin"], 5); c.restore()
def croc(c, x, y, s, t, mouth=20., rot=0., d=1, ko=False):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s * d, s); g, b = (76, 128, 72), (190, 206, 130); w = [sin(t * 4 - i * .6) * (10 + i * 8) * (0 if ko else 1) for i in range(5)]
    for q in (-150, 120): shape(c, limb2((q, 60), (q - 30, 120 + w[0]), (q + 14, 160), (34, 24, 18)), mix(g, INK, .3))
    shape(c, smooth([(180, -60), (60, -96), (-120, -86), (-280, -60 + w[1]), (-440, -20 + w[2]), (-600, 10 + w[3] * 1.4), (-440, 40 + w[2]), (-280, 60 + w[1]), (-100, 96), (80, 96), (190, 60)]), g, 8); c.drawPath(smooth([(170, 60), (0, 92), (-200, 70 + w[1] * .6), (-100, 90), (80, 96)]), fill(b)); [c.drawPath(poly([(q - 26, -78 + abs(q) * .06), (q, -124 + abs(q) * .08), (q + 26, -78 + abs(q) * .06)]), fill(mix(g, INK, .3))) for q in range(-260, 130, 56)]
    c.save(); c.translate(170, 20); c.rotate(mouth * .7); shape(c, smooth([(-40, 0), (120, 6), (300, 14), (310, 44), (120, 56), (-40, 50)]), b, 7); [c.drawPath(poly([(60 + i * 40, 14), (76 + i * 40, -18), (92 + i * 40, 14)]), fill((255, 255, 250))) for i in range(6)]; c.restore()
    c.save(); c.translate(170, 0); c.rotate(-mouth); shape(c, smooth([(-60, -70), (40, -84), (150, -44), (300, -40), (326, -10), (300, 14), (100, 14), (-50, 30)]), g, 7); [c.drawPath(poly([(70 + i * 40, 8), (86 + i * 40, 38), (102 + i * 40, 8)]), fill((255, 255, 250))) for i in range(6)]; c.drawCircle(300, -30, 8, fill(INK)); shape(c, oval(30, -84, 34), g, 6)
    if ko: [c.drawLine(30 + a, -84 - a, 30 - a, -84 + a, line(INK, 8)) for a in (18,)]; c.drawLine(12, -102, 48, -66, line(INK, 8))
    else: c.drawCircle(34, -86, 20, fill((255, 230, 90))); c.drawOval(skia.Rect.MakeLTRB(32, -104, 42, -68), fill(INK))
    c.restore(); c.restore()
def bubbles(c, t, n=40):
    r = random.Random(9)
    for i in range(n): x, y, v, k = r.uniform(0, W), r.uniform(0, H), r.uniform(120, 320), r.uniform(5, 22); yy = (y - t * v) % H; xx = x + sin(t * 2 + i) * 20; c.drawCircle(xx, yy, k, line((230, 255, 255), 3, .7)); c.drawCircle(xx - k * .3, yy - k * .3, k * .2, fill((255, 255, 255), .8))

# ---------------- shots
def lying(c, t): c.save(); c.drawPath(smooth([(170, 1470), (190, 1400), (820, 1400), (850, 1470)]), fill((120, 60, 40))); c.restore(); v = live(pose("down", x=520, rot=-90, h=58, a1u=10, a1f=10, a2u=0, a2f=5, f1x=20, f2x=0, f1y=0, f2y=-10), t, .25); body(c, dict(CAST["laksh"], lid=1), dict(v, h=70), 1420, .92, 1, t, weapon=False, mood="sad")
def s_camp(c, t, D, tk, T): cam(c, 1.0 + .08 * ss(t / D), 540, 1000); bg(c, "camp", p_camp); stand(c, "ram", "kneel", 230, T, 1.0, 1, 1390, mood="sad"); lying(c, T); stand(c, "hanuman", "stand", 850, T, 1.12, -1, 1400, weapon=False, mood="sad", a1u=30, a1f=100, head=12); glow(c, 540, 1100, 500, (255, 150, 60), .12); vig(c)
def s_vow(c, t, D, tk, T): cam(c, 1.45 + .08 * ss(t / D), 560, 1060); bg(c, "camp", p_camp, -60); u = ss((t - D * .5) / .4); f = lambda q: live({k: POSE["namaste"][k] + (POSE["hero"][k] - POSE["namaste"][k]) * ss((t - q - D * .55) / .45) for k in BASE} | dict(x=540), T - q); aura(c, 560, 960, T, 420 * (.6 + .4 * u)); body(c, "hanuman", f(0), GY + 10, 1.15, 1, T, tk.get("H", 0), "n", past=f, weapon=False); vig(c)
def s_fly(c, t, D, tk, T): bg(c, "fly", p_fly, 60 - t * 40); clouds(c, T, 500, 7, 2, a=.25); speed(c, T); fly(c, T, 470 + 60 * ss(t / D), 1290, 1.35); clouds(c, T, 1300, 4, 7, a=.4, y0=1300); vig(c)
def s_send(c, t, D, tk, T):
    cam(c, 1.05 + .12 * ss(t / D), 540, 1010); bg(c, "pal", p_palace); u = ss((t - D * .55) / .5)
    stand(c, "demon", "hero", 540, T, 1.2, 1, GY, weapon=False, mood="angry", a1f=40 + 60 * u); embers(c, T)
    k = max(0, 1 - abs(t - D * .62) / .5)
    for i in range(18): a = i * 2.4 + T * 1.5; r = 130 + (i * 37 % 260); c.drawCircle(540 + cos(a) * r, 1100 + sin(a) * r * 1.2, 60 + 50 * k, fill((70, 200, 120), .10 + .25 * k))
    vig(c)
def s_muni(c, t, D, tk, T):
    cam(c, 1.15 + .1 * ss(t / D), 560, 1080); bg(c, "ash", p_ashram, -30 * ss(t / D)); k = max(0, 1 - t / .9); c.save(); seated(c, "muni", 520, 1420, 1.1, -1, T); c.restore()
    if k > 0: [c.drawCircle(520 + cos(i * 2.4) * (60 + i * 16) * (1.5 - k), 1200 + sin(i * 2.4) * (60 + i * 16) * (1.5 - k), 90 * k, fill((150, 240, 180), .7 * k)) for i in range(18)]
    sh = .5 + .5 * sin(T * 2); c.drawPath(smooth([(430, 1440), (330, 1500), (390, 1620), (520, 1660), (640, 1610), (700, 1500), (600, 1440)]), fill((20, 0, 30), .35)); [c.drawPath(poly([(440 + q * 150 - 24, 1640), (440 + q * 150 + 10, 1730), (440 + q * 150 + 40, 1630)]), fill((20, 0, 30), .35)) for q in (0, 1)]; vig(c)
def s_bath(c, t, D, tk, T): cam(c, 1.1 + .06 * ss(t / D), 520, 1030); bg(c, "ash", p_ashram); seated(c, "muni", 790, 1430, 1.05, -1, T, tk.get("K", 0)); stand(c, "hanuman", "namaste", 300, T, 1.08, 1, GY, weapon=False); vig(c)
def bite_v(t, T): return dict(POSE["swim"], x=380 + sin(T * 1.3) * 14, j=520 + sin(T * 1.8) * 20, rot=-14 + sin(T * 2) * 5, a1u=105 + sin(T * 2.4) * 16, a1f=140 + sin(T * 2.4 - .7) * 20, a2u=60 + sin(T * 2.1) * 14, a2f=100 + sin(T * 2.1 - .6) * 16, f1x=90, f1y=-10, f2x=-50, f2y=40)
def s_bite(c, t, D, tk, T):
    cam(c, 1.08 + .08 * ss(t / D), 540, 1000); bg(c, "wat", p_water); u = E["hit"](max(0, min(1, (t - .3) / (D * .45)))); e = D * .45 + .3; f = lambda q: bite_v(t - q, T - q); sx, sy = punchcam(t, [(e, .8)]); c.translate(sx, sy)
    body(c, "hanuman", f(0), 1700, 1.15, 1, T, 0, "n" if t < e else "angry", past=f, weapon=False, shadow=False); m = 34 * (1 - ss((t - e + .12) / .12)) + 5 + sin(T * 3) * 2; croc(c, 1500 - 560 * u, 1250 + sin(T * 2) * 10, 1.0, T, m, -8, -1); burst(c, 560, 1180, t - e, 130); bubbles(c, T); vig(c)
def s_beat(c, t, D, tk, T):
    cam(c, 1.1, 540, 1000); bg(c, "wat", p_water); e = .85; sx, sy = punchcam(t, [(e, 1.4)]); c.translate(sx, sy); tt = hitstop(t, [(e, 1.4)])
    ks = Keys(1, 1.15, [(0, dict(bite_v(0, T), a2u=-30.), "io"), (.55, dict(pose("punchw"), x=380, j=520, rot=-22, f1y=20, f2y=60), "io"), (.85, dict(pose("punch"), x=450, j=520, rot=16, a1u=-60, a2u=84, a2f=90, f1y=30, f2y=70), "hit"), (1.5, dict(pose("punch"), x=465, j=520, rot=10, a2u=70, a2f=82, f1y=20, f2y=60), "out"), (3, dict(POSE["hero"], x=460, j=540, rot=0), "io")]); f = lambda q: anim(ks, tt - q)
    k = max(0, tt - e); kk = 1 - math.exp(-k * 2.2); gone = ss((tt - e - 1.1) / .7)
    if gone < 1: c.save(); croc(c, 830 + 240 * kk, 1150 + 120 * kk, 1.0 * (1 - .4 * gone), T, 8 + 24 * kk, 150 * kk, -1, ko=k > 0); c.restore()
    body(c, "hanuman", f(0), 1700, 1.15, 1, T, 0, "angry" if tt < 1.6 else "n", past=f, weapon=False, shadow=False); burst(c, 720, 1130, t - e, 210)
    if gone > 0: glow(c, 860, 1250, 600 * gone, (255, 250, 210), .95 * gone)
    bubbles(c, T); vig(c)
def s_apsara(c, t, D, tk, T): cam(c, 1.12 + .06 * ss(t / D), 540, 1040); bg(c, "ash", p_ashram, 40); aura(c, 740, 900, T, 480, (255, 220, 240)); f = lambda q: live(pose("talk", x=740, j=150 + sin((T - q) * 1.6) * 14, f1x=16, f2x=-16, f1y=-20), T - q); body(c, "apsara", f(0), GY, 1.1, -1, T, tk.get("A", 0), "n", past=f); stand(c, "hanuman", "stand", 300, T, 1.08, 1, GY, weapon=False, mood="angry" if t > D * .6 else "n"); embers(c, T, 30, (255, 240, 200)); vig(c)
def s_daksh(c, t, D, tk, T): cam(c, 1.15 + .12 * ss(t / D), 480, 1010); bg(c, "ash", p_ashram); seated(c, "muni", 810, 1430, 1.0, -1, T, 0, "sad" if t > D * .6 else "n"); stand(c, "hanuman", "hero", 320, T, 1.2, 1, GY, talk=tk.get("H", 0), mood="angry", a2u=70, a2f=100); vig(c)
def s_reveal(c, t, D, tk, T):
    u = E["back"](max(0, min(1, (t - .35) / .55))); sx, sy = punchcam(t, [(.4, 1.2)], dur=.6); c.translate(sx, sy); cam(c, 1.2 + .1 * ss(t / D), 560, 1010); bg(c, "are", p_arena); aura(c, 560, 1000, T, 520, (120, 255, 120)); embers(c, T, 50, (140, 255, 140))
    if t < .4: seated(c, "muni", 560, 1430, 1.1, -1, T)
    if u > 0: f = lambda q: live(pose("roar", x=560, h=252 * max(.2, u)), T - q, 1.6); body(c, "demon", f(0), GY, 1.2 * max(.3, u), -1, T, tk.get("K", 0), "roar", past=f)
    k = max(0, 1 - abs(t - .4) / .5); [c.drawCircle(560 + cos(i * 2.4) * (40 + i * 22) * (1.4 - k), 1080 + sin(i * 2.4) * (40 + i * 22) * (1.4 - k), 110 * k, fill((130, 240, 150), .8 * k)) for i in range(18)]; vig(c)

HS, KS = .9, .94
HK = Keys(1, HS, [(0, pose("guard", x=190), "io"), (.45, pose("run", x=270), "io"), (.85, pose("wind", x=310), "io"), (1.12, pose("strike", x=365), "hit"), (1.3, pose("follow", x=367), "out"), (1.65, pose("guard", x=350), "io"), (1.92, pose("duck", x=370), "out"), (2.2, pose("punchw", x=430), "io"), (2.42, pose("punch", x=525), "hit"), (2.65, pose("punch", x=535, hx=70, lean=10), "out"), (3.1, pose("guard", x=450), "io"), (3.55, pose("crouch", x=400), "io"), (3.82, pose("hit", x=235, h=266, j=70, f1y=40, f2y=20), "out"), (4.06, pose("crouch", x=215), "inn"), (4.4, pose("crouch", x=215, h=160), "io"), (4.72, pose("tuck", x=280, rot=40), "out"), (5.0, pose("tuck", x=380, j=380, rot=300), "lin"), (5.12, pose("leap", x=425, j=300, rot=372, lean=-10), "lin"), (5.3, pose("land", x=455, rot=360), "hit"), (5.7, pose("land", x=457, rot=360, h=186), "out"), (6.3, pose("hero", x=430, rot=360), "io"), (9, pose("hero", x=430, rot=360), "io")])
KK = Keys(-1, KS, [(0, pose("guard", x=890), "io"), (.5, pose("run", x=820), "io"), (.95, pose("block", x=790), "io"), (1.12, pose("block", x=792, lean=-12), "hit"), (1.3, pose("block", x=835, hx=-50, lean=-20), "out"), (1.55, pose("wind", x=820), "io"), (1.95, pose("strike", x=740, a1u=108, a1f=100), "hit"), (2.15, pose("follow", x=738), "out"), (2.42, pose("stagger", x=745), "io"), (2.5, pose("hit", x=785, lean=-40), "out"), (2.95, pose("stagger", x=880), "io"), (3.3, pose("crouch", x=880), "io"), (3.6, pose("leap", x=690, j=300), "out"), (3.84, pose("land", x=545), "inn"), (4.2, pose("land", x=545, h=160), "out"), (4.7, pose("guard", x=620), "io"), (5.1, pose("block", x=690, head=-30), "io"), (5.3, pose("stagger", x=725, h=170, lean=60), "hit"), (5.42, pose("hit", x=790, j=110, rot=-30, f1y=60, f2y=40), "out"), (5.75, pose("down", x=810), "inn"), (9, pose("down", x=810), "io")])
EV = [(1.12, 1.), (2.44, 1.3), (3.84, 1.2), (5.3, 2.2)]
def s_fight(c, t, D, tk, T):
    a = hitstop(t, EV); rt = lambda e: e + sum(.075 * k for q, k in EV if q < e); ev = [(rt(e), k) for e, k in EV]; sx, sy = punchcam(t, ev); f, g = (lambda q: anim(HK, a - q)), (lambda q: anim(KK, a - q))
    h, k = f(0), g(0); mid = lambda u: (anim(HK, u)["x"] + anim(KK, u)["x"]) / 2; cx = sum(mid(a - .1 * i) for i in range(6)) / 6; z = 1.06 + sum(.10 * kk * max(0, 1 - abs(t - e - .05) / .3) ** 2 for e, kk in ev); c.translate(sx, sy); cam(c, z, 540 + (cx - 540) * .5, 1010); bg(c, "are", p_arena, (540 - cx) * .25); embers(c, T, 50)
    for e, (x, w) in ((3.84, (290, 300)), (5.3, (720, 360))): cracks(c, x, GY + 14, a - e, w)
    body(c, "demon", k, GY, KS, -1, T, 0, "shock" if a > 5.05 or 2.4 < a < 2.9 else "roar" if 3.3 < a < 3.9 else "angry", past=g); body(c, "hanuman", h, GY + 20, HS, 1, T, 0, "roar" if 1 < a < 1.3 or 4.9 < a < 5.6 else "angry", past=f)
    for (e, kk), (x, y, r) in zip(ev, ((640, 1010, 140), (690, 960, 190), (290, 1400, 200), (730, 1080, 300))): burst(c, x, y, t - e, r)
    for e, x, w in ((3.84, 290, 320), (5.3, 720, 380), (5.75, 900, 260), (4.06, 160, 160)): dust(c, x, GY + 10, t - rt(e), 16, w, seed=int(x))
    for e, kk in ev:
        if 0 <= t - e < .07 and kk > 1: c.restore() if False else None; c.drawPaint(fill((255, 255, 255), .28))
    vig(c)
def s_tail(c, t, D, tk, T):
    """The tail goes round him, one swing over the head, and down."""
    w, sw, hit = .75, 1.1, 2.05; ev = [(hit, 2.4)]; a = hitstop(t, ev); sx, sy = punchcam(t, ev, 20, .5); c.translate(sx, sy); cam(c, 1.0 + .1 * max(0, 1 - abs(t - hit - .05) / .35) ** 2, 540, 1000); bg(c, "are", p_arena, 20); embers(c, T, 50); hx, hy = 400, GY - 300
    cracks(c, 830, GY + 20, a - hit, 380)
    ks = Keys(1, 1.0, [(0, pose("guard", x=400), "io"), (.6, pose("crouch", x=400), "io"), (1.1, pose("hero", x=400, lean=-16, a1u=160, a1f=170, a2u=150, a2f=170), "out"), (1.75, pose("wind", x=400, lean=-26), "io"), (hit, pose("strike", x=410), "hit"), (2.5, pose("follow", x=410), "out"), (3.2, pose("hero", x=400), "io"), (9, pose("hero", x=400), "io")]); f = lambda q: anim(ks, a - q); v = f(0)
    def kp(u):
        if u < sw: q = ss((u - .3) / .45); return 800 + 26 * q, GY - 260 - 504 * q * q, -20 * q
        q = min(1, (u - sw) / (hit - sw)); q = E["inn"](q) * .55 + q * .45; an = -60 + 330 * 0 + (-60 - 240 * 0) * 0; th = rad(-25 - 310 * q); R = 360; x, y = 500 + cos(th) * R, GY - 620 + sin(th) * R * .95
        g = ss((q - .82) / .18); return x + (830 - x) * g, y + (GY - 60 - y) * g, -20 - 430 * q
    x, y, ro = kp(a); dk = lambda q: pose("hit", x=kp(a - q)[0], h=254, j=0, hx=0, rot=kp(a - q)[2], a1u=100 + sin(a * 9) * 30, a1f=130, a2u=-80, a2f=-100 + sin(a * 8) * 20, f1x=60, f1y=30, f2x=-80, f2y=0)
    if a > hit: v2 = pose("down", x=830); body(c, "demon", v2, GY + 10, .88, -1, T, 0, "shock", weapon=False)
    else: body(c, "demon", dk(0), y + 254 * .88, .88, -1, T, 0, "shock", weapon=False, shadow=False)
    u = ss((a - .1) / .5); bx, by = 370, hy + 10; tx, ty = (x, y - 70) if a < hit else (800, GY - 110)
    k = min(u, 1); rel = ss((a - hit - .25) / .5); ex, ey = bx - 150 + (tx - bx + 150) * k, by - 200 + (ty - by + 200) * k
    mx, my = (bx + ex) / 2 - 40 - (ey - by) * .22, (by + ey) / 2 + 60 + (ex - bx) * .16; pts = [(bx, by), (bx - 90, by + 10), (mx - 60, my + 20), (mx + 60, my - 10)]
    if k > .97 and rel < .5:
        for i in range(17): q = i / 16 * 4 * pi; pts.append((ex + cos(q + 2.6) * 128, ey + sin(q + 2.6) * 34 + i * 4 - 30))
    else: pts += [(ex - 60, ey + 30), (ex + 10, ey), (ex + 30, ey - 50)]
    if rel > 0: rst = [(bx, by), (bx - 90, by + 20), (bx - 170, by - 60), (bx - 180, by - 190), (bx - 120, by - 270), (bx - 60, by - 300), (bx - 30, by - 250)]; pts = [(bx + (p_[0] - bx) * (1 - rel), by + (p_[1] - by) * (1 - rel)) for p_ in pts] if rel < .5 else [(bx + (p_[0] - bx) * rel, by + (p_[1] - by) * rel) for p_ in rst]
    body(c, "hanuman", v, GY + 20, 1.0, 1, T, 0, "roar" if a > 1.7 and a < 2.6 else "angry", past=f, tail=False); draw_tail(c, pts, (214, 104, 50), 28)
    burst(c, 830, GY - 70, t - hit, 330); dust(c, 830, GY + 10, t - hit, 22, 420)
    if 0 <= t - hit < .07: c.drawPaint(fill((255, 255, 255), .3))
    vig(c)
def s_lift(c, t, D, tk, T):
    u = ss((t - D * .35) / (D * .5)); sx, sy = (sin(t * 37) * 5 * (u > 0) * (1 - u), cos(t * 31) * 5 * (u > 0) * (1 - u)); c.translate(sx, sy); cam(c, 1.05 - .08 * u, 540, 960 - 60 * u); bg(c, "peak", p_peak); f = lambda q: (lambda w: {k: POSE["crouch"][k] + (P(a1u=165., a1f=178., a2u=172., a2f=182., lean=0., f1x=80., f2x=-84., head=-12.)[k] - POSE["crouch"][k]) * w for k in BASE} | dict(x=540, a1u=120 + 45 * w, a1f=165 + 13 * w, a2u=130 + 42 * w, a2f=170 + 12 * w))(ss((t - q - D * .35) / (D * .5))); v = f(0); J = solve(v, 1.12); h = world(J["a1"][2], v, GY + 20, 1.15, 1); aura(c, 540, 900, T, 620 * u + 10, (255, 220, 120)); mountain(c, 560, h[1] - 10, 1.15); body(c, "hanuman", v, GY + 20, 1.15, 1, T, 0, "angry" if u < .9 else "n", past=f, weapon=False)
    r = random.Random(2)
    for i in range(14): q = (t * 1.1 + r.random()) % 1; (u > 0) and c.drawCircle(540 + r.uniform(-330, 330), h[1] + 20 + q * 700, r.uniform(6, 18) * (1 - q), fill((110, 110, 120)))
    vig(c)
def s_carry(c, t, D, tk, T): bg(c, "fly", p_fly, 60 - t * 40); clouds(c, T, 500, 7, 2, a=.25); speed(c, T); fly(c, T, 520, 1560, 1.1, lambda c, x, y: mountain(c, x + 10, y - 10, .95)); clouds(c, T, 1300, 4, 7, a=.4, y0=1450); vig(c)
def s_saved(c, t, D, tk, T): cam(c, 1.02 + .06 * ss(t / D), 540, 1000); bg(c, "dawn", p_dawn); aura(c, 540, 1000, T, 600, (255, 240, 180)); stand(c, "laksh", "namaste", 850, T, .98, -1, GY); stand(c, "ram", "stand", 560, T, 1.0, -1, GY - 14, a1u=70, a1f=100); stand(c, "hanuman", "namaste", 210, T, 1.0, 1, GY, weapon=False); embers(c, T, 30, (255, 230, 150)); vig(c)
def s_end(c, t, D, tk, T): cam(c, 1.3 - .1 * ss(t / D), 540, 1010); bg(c, "dawn", p_dawn); aura(c, 540, 900, T, 700, (255, 220, 120)); f = lambda q: live({k: POSE["hero"][k] + (POSE["namaste"][k] - POSE["hero"][k]) * ss((t - q - D + 5) / .8) for k in BASE} | dict(x=520), T - q); body(c, "hanuman", f(0), GY, 1.2, 1, T, 0, "n", past=f, weapon=t < D - 5 and True); embers(c, T, 50, (255, 200, 90)); vig(c)

N, HV, KV, R, A = (M, "+6%", "-2Hz"), (M, "+4%", "-12Hz"), (M, "-8%", "+6Hz"), (M, "-4%", "-30Hz"), (S, "+4%", "+8Hz")
def L(shot, w, v, hi, ro, **k): return dict(shot=shot, who=w, v=v, hi=hi, ro=ro, **k)
LINES = [
 L("camp", "N", N, "लक्ष्मण जी मूर्छित थे। रात भर में संजीवनी लानी थी।", "Lakshman ji *moorchhit* the. Raat bhar mein *sanjeevani* laani thi."),
 L("vow", "H", HV, "प्रभु, मैं अभी लाता हूँ!", "*Prabhu,* main *abhi* laata hoon!", pad=.5),
 L("fly", "N", N, "हनुमान जी हवा की गति से उड़ चले।", "Hanuman ji *hawa* ki gati se *ud* chale."),
 L("send", "N", N, "पर रावण ने भेजा, मायावी राक्षस कालनेमि।", "Par Ravan ne bheja, mayavi rakshas *Kalnemi.*", pad=.5),
 L("muni", "N", N, "वो साधु बनकर रास्ते में बैठ गया।", "Woh *sadhu* bankar raaste mein *baith* gaya."),
 L("bath", "K", KV, "थक गए होगे वत्स। पहले सरोवर में स्नान कर लो।", "Thak gaye hoge vats. Pehle *sarovar* mein *snaan* kar lo."),
 L("bite", "N", N, "पानी में उतरते ही, एक मगरमच्छ ने पैर पकड़ लिया!", "Paani mein utarte hi, ek *magarmachh* ne *pair* pakad liya!"),
 L("beat", "N", N, "एक ही वार में, वो अप्सरा बन गई!", "Ek hi *vaar* mein, woh *apsara* ban gayi!", pad=.9),
 L("apsara", "A", A, "सावधान! वो साधु नहीं, राक्षस है!", "*Saavdhaan!* Woh sadhu nahi, *rakshas* hai!"),
 L("daksh", "H", HV, "मुनिवर, पहले गुरु दक्षिणा तो ले लीजिए!", "Munivar, pehle *guru* *dakshina* toh le lijiye!"),
 L("reveal", "K", R, "हा हा हा! तू यहाँ से नहीं जाएगा!", "Ha ha ha! Tu *yahan* se nahi *jayega!*", pre=.6, pad=.5),
 L("fight", "N", N, "और छिड़ गया, महायुद्ध!", "Aur chhid gaya, *mahayuddh!*", pad=5.3),
 L("tail", "N", N, "फिर पूँछ में लपेटकर, धरती पर पटक दिया!", "Phir *poonchh* mein lapetkar, dharti par *patak* diya!", pad=.9),
 L("lift", "N", N, "बूटी पहचान में न आई, तो पूरा पर्वत ही उठा लिया!", "Booti pehchaan mein na aayi, toh poora *parvat* hi *utha* liya!", pad=.4),
 L("carry", "N", N, "और समय रहते, लंका लौट आए।", "Aur *samay* rehte, *Lanka* laut aaye."),
 L("saved", "N", N, "लक्ष्मण जी के प्राण बच गए।", "Lakshman ji ke *praan* bach gaye.", pad=.4),
 L("end", "N", N, "सच्ची भक्ति के आगे, कोई माया नहीं टिकती। जय श्री राम!", "Sachchi *bhakti* ke aage, koi *maya* nahi tikti. *Jai* *Shri* *Ram!*", pad=3.6),
]
SH = {k[2:]: v for k, v in list(globals().items()) if k.startswith("s_")}

def thump(f0=62, d=.5, k=9): q = au.tarr(d); return np.sin(2 * pi * np.cumsum(f0 + 90 * np.exp(-q * 34)) / SR) * np.exp(-q * k)
def boom(d=1.1): q = au.tarr(d); return thump(44, d, 4) + au.band(au.noise(d), 40, 900) * np.exp(-q * 6) * .7
def clang(d=.8): q = au.tarr(d); return sum(np.sin(2 * pi * f * q) * np.exp(-q * (6 + i * 2)) / (i + 1) for i, f in enumerate((1240, 2030, 3170, 4420)))
def mus(n, tl):
    """Drone and dhol; the fight and the lift get the full war beat, the sad and quiet shots only the drone."""
    b = np.zeros(n); q = np.arange(n) / SR
    for f, a in ((98, .32), (147, .22), (196, .16)): b += a * np.sin(2 * pi * f * q + .4 * np.sin(2 * pi * .3 * q)) * (1 + .3 * np.sin(2 * pi * .4 * q + f))
    heat = dict(camp=0, vow=1, fly=2, send=1, muni=0, bath=0, bite=2, beat=2, apsara=0, daksh=1, reveal=1, fight=3, tail=3, lift=2, carry=2, saved=1, end=1); sc = [392, 440, 523, 587, 659, 784]; r = random.Random(4)
    for l in tl["lines"]:
        h = heat[l["shot"]]; t = l["start"]; k = 0; st = .15 if h == 3 else .18
        while t < l["end"] - .05:
            if h >= 1 and k % 8 in ((0, 3, 6) if h < 3 else (0, 2, 3, 5, 6)): au.add(b, t, thump(), .9 if k % 8 == 0 else .6)
            if h >= 2 and k % 2: x = au.tarr(.09); au.add(b, t, np.sin(2 * pi * 360 * x) * np.exp(-x * 50), .35)
            if h >= 2 and k % 16 == 12: au.add(b, t, au.band(au.noise(.3), 2000, 8000) * np.exp(-au.tarr(.3) * 12), .2)
            if k % (4 if h else 6) == 0: f = r.choice(sc) / (2 if h == 3 else 1); x = au.tarr(.9); au.add(b, t, (np.sin(2 * pi * f * x + .5 * np.sin(2 * pi * 5 * x)) + .3 * np.sin(4 * pi * f * x)) * np.minimum(1, x / .06) * np.exp(-x * 3), .22)
            t += st; k += 1
    return b
def fx(f, tl):
    wh = lambda t, g=.3, d=.35: au.add(f, t, au.band(au.noise(d), 500, 5000) * np.hanning(int(d * SR)), g)
    for l in tl["lines"]:
        s, D, n = l["start"], l["end"] - l["start"], l["shot"]; s > 0 and wh(s - .2, .1, .5)
        if n == "vow": au.add(f, s + D * .55, au.bell(520, 2), .4)
        if n in ("fly", "carry"): x = au.band(au.noise(D), 200, 1600); au.add(f, s, x * np.hanning(len(x)) ** .3, .18)
        if n in ("muni", "reveal"): au.add(f, s + .1, au.sweep(200, 900, .8, 3), .25); wh(s + .1, .3, .8)
        if n == "reveal": au.add(f, s + .4, boom(), .6)
        if n == "bite": au.add(f, s + D * .45 + .3, boom(.6), .7)
        if n == "beat": au.add(f, s + .85, boom(), 1.0); au.add(f, s + 2.0, au.bell(780, 2), .4)
        if n == "apsara": au.add(f, s, au.bell(1040, 2), .3)
        if n == "fight":
            rt = lambda e: s + e + sum(.075 * k for q, k in EV if q < e)
            for e in (1.0, 1.82, 2.34, 3.7, 4.8, 5.18): wh(rt(e), .4, .28)
            au.add(f, rt(1.12), clang(), .5); au.add(f, rt(2.44), boom(.6), .9); au.add(f, rt(3.84), boom(), .9); au.add(f, rt(3.84), clang(.5), .25); au.add(f, rt(5.3), boom(1.4), 1.3); au.add(f, rt(5.75), boom(.6), .6)
        if n == "tail": wh(s + .2, .3, .5); wh(s + 1.2, .4, .5); wh(s + 1.6, .5, .5); au.add(f, s + 2.05, boom(1.5), 1.4)
        if n == "lift": x = au.band(au.noise(D * .5), 30, 220); au.add(f, s + D * .35, x * np.hanning(len(x)) ** .5, .7); au.add(f, s + D * .85, au.bell(520, 2.5), .5)
        if n in ("saved", "end"): au.add(f, s + .1, au.bell(660, 2.5), .4)
if __name__ == "__main__": run("hanuman", LINES, SH, ("HANUMAN JI AUR", "KALNEMI"), mus, fx)
