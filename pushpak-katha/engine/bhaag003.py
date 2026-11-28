"""Ramayan bhaag 3 (Uttar kaand, sarg 3): Vaishravan (Kuber), his tapasya, Brahma's boon, the Pushpak, and Lanka.
Script: scripts/003.md. Characters from cast/ramayan.json via the factory. 60 fps.
    python engine/bhaag003.py preview   -> out/preview_bhaag003.jpg
    python engine/bhaag003.py           -> out/sample_bhaag003.mp4
"""
import lab, rig
from rig import *
from lab import main as run, SR, M, S, au
from hanuman import cam, live, stand, embers, aura, vig, sky, stars, ground, clouds, thump, boom, GY, tree, seated
import factory as fa
from bhaag001 import petals, shadow_of
lab.FPS = 60; rig.SOFT = True
ss = lambda u: (lambda v: v * v * (3 - 2 * v))(max(0., min(1., u)))

# ---------------- cast: main people from the design file; Vishrava's wife and the fleeing rakshas are one-time extras
CASTF = fa.load()
PATNI = dict(name="Patni", kind="human", sex="f", age="young", skin="fair", hair="braid", hair_rgb=[30, 20, 24], crown="none", tilak="bindi", eyes="kind", top="blouse", lower="saree", cloth=[240, 150, 40], edge=[200, 40, 60], jewel=[40, 150, 200], weapon="none", size=.88)
RAK = [fa.auto("rakshas", k, CASTF, f"Rakshas {k}") for k in (3, 5, 8)]
for sp in CASTF + [PATNI] + RAK: rig.CAST[sp["name"].lower().replace(" ", "")] = fa.make(sp)

# ---------------- places, painted once
def city(c, r, cx=540, top=600, w=330):
    """Golden Lanka on the three peaks of Trikut: towers, gold walls, emerald arches."""
    for i, (dx, h) in enumerate(((-300, 150), (-230, 230), (-150, 300), (-70, 260), (0, 380), (70, 270), (150, 320), (230, 220), (300, 160))):
        x = cx + dx * w / 300; y0 = top + 210 - h
        c.drawRect(skia.Rect.MakeLTRB(x - 30, y0, x + 30, top + 240), fill((250, 196, 60))); c.drawRect(skia.Rect.MakeLTRB(x + 10, y0, x + 30, top + 240), fill((220, 150, 40)))
        c.drawPath(smooth([(x - 38, y0 + 4), (x - 20, y0 - 50), (x, y0 - 90), (x + 20, y0 - 50), (x + 38, y0 + 4)]), fill((255, 220, 90))); c.drawCircle(x, y0 - 96, 8, fill((255, 250, 220)))
        for k in range(int(h / 80)): c.drawPath(smooth([(x - 12, y0 + 70 + k * 70), (x - 12, y0 + 46 + k * 70), (x, y0 + 36 + k * 70), (x + 12, y0 + 46 + k * 70), (x + 12, y0 + 70 + k * 70)]), fill((40, 170, 110)))
    c.drawRect(skia.Rect.MakeLTRB(cx - w - 40, top + 200, cx + w + 40, top + 270), fill((240, 180, 50))); [c.drawRect(skia.Rect.MakeXYWH(cx - w - 40 + i * 44, top + 182, 26, 22), fill((240, 180, 50))) for i in range(int((2 * w + 80) / 44) + 1)]
    for dx in (-200, 0, 200): c.drawPath(smooth([(cx + dx - 40, top + 270), (cx + dx - 40, top + 230), (cx + dx, top + 206), (cx + dx + 40, top + 230), (cx + dx + 40, top + 270)]), fill((30, 140, 90)))
def p_trikut(c):
    r = random.Random(81); sky(c, (70, 120, 210), (255, 214, 150), 1150); glow(c, 540, 700, 700, (255, 240, 190), .7)
    for i in range(6): x, y = r.uniform(-200, W + 200), r.uniform(150, 500); [c.drawCircle(x + q * 70, y - abs(q) * 14, 70, fill((255, 246, 236), .7)) for q in range(-2, 3)]
    shape(c, poly([(-200, 1180), (120, 960), (250, 780), (330, 860), (420, 760), (540, 640), (660, 760), (750, 850), (830, 780), (960, 960), (1280, 1180)]), (120, 110, 100), 6)
    c.drawPath(poly([(540, 640), (660, 760), (750, 850), (830, 780), (960, 960), (1280, 1180), (700, 1180)]), fill((70, 60, 70), .35))
    for x in (250, 830): c.drawPath(poly([(x - 40, 820), (x, 780), (x + 40, 820), (x, 840)]), fill((160, 200, 120)))
    city(c, r, 540, 460, 300)
    c.drawRect(skia.Rect.MakeLTRB(-240, 1170, W + 240, H + 240), fill((30, 110, 160)))
    for y in range(1190, 1400, 20): x = r.uniform(-200, 900); c.drawLine(x, y, x + r.uniform(200, 500), y, line((200, 240, 255), 4, .45))
    c.drawPath(smooth([(-240, 1360), (200, 1320), (600, 1340), (1000, 1310), (1320, 1350), (1320, H + 240), (-240, H + 240)]), fill((236, 200, 140)))
    c.drawRect(skia.Rect.MakeLTRB(-240, 1500, W + 240, H + 240), fill((214, 176, 120)))
def p_ashram3(c):
    r = random.Random(91); sky(c, (150, 214, 220), (240, 250, 230)); glow(c, 300, 700, 500, (255, 255, 230), .7)
    mountains(c, r, 1080, 300, (150, 190, 200), (255, 255, 255)); mountains(c, r, 1180, 160, (110, 170, 140), None)
    c.drawRect(skia.Rect.MakeLTRB(-240, 1150, W + 240, 1240), fill((80, 160, 200)))
    for y in range(1160, 1240, 16): x = r.uniform(-200, 1000); c.drawLine(x, y, x + r.uniform(100, 300), y, line((230, 250, 255), 3, .6))
    for x in (120, 380, 700): c.drawCircle(x, 1200, 18, fill((250, 150, 180))); c.drawOval(skia.Rect.MakeLTRB(x - 40, 1206, x + 40, 1222), fill((60, 140, 80)))
    tree(c, -40, 1330, 760, r, (60, 140, 80))
    x = 1000; c.drawRect(skia.Rect.MakeLTRB(x - 140, 1060, x + 140, 1330), fill((200, 150, 100))); [c.drawLine(x - 140, y, x + 140, y, line((150, 100, 60), 4)) for y in range(1070, 1330, 28)]
    shape(c, smooth([(x - 200, 1080), (x - 120, 950), (x, 900), (x + 120, 950), (x + 200, 1080)]), (190, 170, 90), 6); c.drawRect(skia.Rect.MakeLTRB(x - 44, 1180, x + 44, 1330), fill((80, 50, 40)))
    ground(c, (130, 170, 100), (220, 240, 180), r, grass=(80, 140, 70))
    for _ in range(30):
        x, y = r.uniform(-200, W + 200), r.uniform(1380, 1900); g = r.choice([(255, 255, 255), (255, 210, 80)])
        for k in range(5): a = k * 2 * pi / 5; c.drawCircle(x + cos(a) * 9, y + sin(a) * 5, 7, fill(g))
def p_tapvan(c):
    """Forest without sky: the sky (day and night) is painted live behind it."""
    c.clear(skia.Color(0, 0, 0, 0)); r = random.Random(101)
    for i in range(12): x = -200 + i * 130 + r.uniform(-30, 30); h = r.uniform(300, 520); c.drawPath(smooth([(x - 90, 1300), (x - 70, 1300 - h), (x, 1300 - h - 90), (x + 70, 1300 - h), (x + 90, 1300)]), fill((40, 90, 70)))
    for x, w in ((-60, 110), (1140, 120), (180, 60), (900, 66)):
        c.drawRect(skia.Rect.MakeLTRB(x - w / 2, -240, x + w / 2, 1360), fill((80, 54, 44))); c.drawLine(x - w / 4, -240, x - w / 4, 1360, line((60, 40, 34), 6))
    for x, y, R in ((-120, 60, 420), (1200, 40, 440), (200, -60, 300), (880, -80, 320), (540, -200, 260)):
        for q in range(7): a = q * 2 * pi / 7; c.drawCircle(x + cos(a) * R * .5, y + sin(a) * R * .4, R * .5, fill(mix((40, 110, 60), (70, 140, 70), q / 7)))
    for x in (60, 300, 760, 1020): c.drawPath(smooth([(x, 0), (x + 20, 300), (x - 10, 560)], False), line((60, 130, 70), 6))
    c.drawRect(skia.Rect.MakeLTRB(-240, 1290, W + 240, H + 240), fill((70, 100, 60)))
    c.drawPath(smooth([(-240, 1300), (300, 1280), (800, 1300), (1320, 1280), (1320, 1360), (-240, 1360)]), fill((90, 130, 70)))
    for _ in range(80): x, y = r.uniform(-200, W + 200), r.uniform(1320, 1900); c.drawLine(x, y, x + r.uniform(-12, 12), y - r.uniform(20, 46), line((110, 160, 80), 5))
def p_lok(c):
    r = random.Random(111); vgrad(c, [(0, (14, 10, 50)), (.5, (60, 30, 110)), (1, (120, 50, 120))], -240, H + 240); stars(c, r, 220, H)
    for x, y, R, g in ((260, 500, 500, (120, 80, 220)), (840, 1300, 600, (220, 80, 160)), (600, 800, 400, (80, 140, 240))): glow(c, x, y, R, g, .35)
    for k in range(3): c.drawCircle(540, 900, 380 + k * 18, line((255, 230, 170), 3, .35 - k * .1))
    for a in range(4): q = a * pi / 2; c.drawLine(540 + cos(q) * 300, 900 + sin(q) * 300, 540 + cos(q) * 470, 900 + sin(q) * 470, line((255, 230, 170), 4, .4))
    c.drawOval(skia.Rect.MakeLTRB(200, 1360, 880, 1480), fill((255, 230, 170), .18))
def p_aakash(c):
    r = random.Random(121); sky(c, (60, 140, 230), (220, 240, 255), 1500); glow(c, 860, 360, 420, (255, 250, 220), .8)
    for i in range(14): x, y, k = r.uniform(-200, W + 200), r.uniform(300, 1300), r.uniform(.6, 1.4); [c.drawCircle(x + q * 70 * k, y - abs(q) * 16 * k, 80 * k, fill((255, 255, 255), .75)) for q in range(-2, 3)]
    shape(c, smooth([(-240, 1360), (-100, 1300), (200, 1270), (500, 1300), (800, 1340), (1320, 1300), (1320, H + 240), (-240, H + 240)]), (110, 170, 90), 6)
    for _ in range(60): x, y = r.uniform(-200, W + 200), r.uniform(1340, 1900); c.drawLine(x, y, x + r.uniform(-10, 10), y - 30, line((80, 140, 70), 5))
def p_raat(c):
    r = random.Random(131); vgrad(c, [(0, (6, 6, 22)), (.55, (20, 24, 60)), (1, (10, 30, 50))], -240, H + 240); stars(c, r, 90, 900)
    glow(c, 540, 1100, 700, (120, 40, 80), .5)
    c.drawRect(skia.Rect.MakeLTRB(-240, 1100, W + 240, H + 240), fill((10, 30, 50)))
    for y in range(1120, 1900, 26): x = r.uniform(-200, 900); c.drawLine(x, y, x + r.uniform(150, 400), y, line((80, 120, 170), 3, .35))

# ---------------- things
def pushpak(c, x, y, k, T, rider=None, tilt=0.):
    """The flying vimana: gold hull with swan prows, a red inner wall, a shikhara, flags; the rider sits inside."""
    c.save(); c.translate(x, y + 10 * sin(T * 2)); c.rotate(tilt + 1.5 * sin(T * 1.3)); c.scale(k, k)
    glow(c, 0, -260, 640, (255, 230, 150), .55)
    for i in range(9): a = i - 4; c.drawCircle(a * 80 + 16 * sin(T * 2 + i), 150 - (4 - abs(a)) * 10, 76 - abs(a) * 4, fill((255, 255, 255), .85))
    shape(c, poly([(-250, -400), (250, -400), (250, 0), (-250, 0)]), (190, 50, 60), 5)
    for q in range(-4, 5): c.drawLine(q * 56, -390, q * 56, -10, line((240, 170, 60), 3, .5))
    for yy in (-300, -180): c.drawLine(-246, yy, 246, yy, line((240, 170, 60), 3, .5))
    if rider: rider(c)
    for px in (-262, 262): shape(c, poly([(px - 16, 0), (px - 16, -400), (px + 16, -400), (px + 16, 0)]), (255, 204, 70), 4)
    c.drawPath(smooth([(-246, -400), (-246, -330), (-160, -385), (0, -400), (160, -385), (246, -330), (246, -400)]), fill((255, 214, 90)))
    shape(c, poly([(-310, -400), (310, -400), (280, -452), (-280, -452)]), (250, 190, 50), 5)
    for d in (-1, 1):
        shape(c, smooth([(d * 300, -452), (d * 290, -500), (d * 250, -530), (d * 210, -500), (d * 200, -452)]), (255, 214, 80), 4)
        c.drawLine(d * 250, -530, d * 250, -620, line((150, 100, 40), 6)); fl = 14 * sin(T * 6 + d)
        c.drawPath(poly([(d * 250, -620), (d * 250 + d * 90, -600 + fl), (d * 250, -575)]), fill((230, 50, 60)))
    sh = smooth([(-170, -452), (-150, -560), (-80, -650), (0, -690), (80, -650), (150, -560), (170, -452)]); shape(c, sh, (255, 210, 70), 5)
    c.save(); c.clipPath(sh, True); [c.drawLine(-200, yy, 200, yy, line((220, 150, 40), 5)) for yy in range(-640, -452, 40)]; c.restore()
    c.drawCircle(0, -712, 24, fill((255, 230, 120))); c.drawCircle(0, -712, 24, line(INK, 4)); c.drawPath(poly([(-8, -734), (0, -770), (8, -734)]), fill((255, 230, 120)))
    shape(c, poly([(-300, -96), (300, -96), (300, 0), (-300, 0)]), (240, 180, 50), 5)
    for q in range(-5, 6): c.drawCircle(q * 52, -48, 12, fill((40, 180, 110) if q % 2 else (220, 40, 60)))
    for d in (-1, 1):
        q = smooth([(d * 300, -10), (d * 380, -40), (d * 400, -140), (d * 370, -190), (d * 340, -160), (d * 360, -100), (d * 330, -60), (d * 290, -60)]); shape(c, q, (255, 240, 220), 5)
        c.drawPath(poly([(d * 370, -190), (d * 420, -182), (d * 374, -170)]), fill((250, 160, 40)))
    shape(c, smooth([(-330, 0), (330, 0), (290, 70), (170, 120), (0, 136), (-170, 120), (-290, 70)]), (240, 170, 40), 6)
    c.drawPath(smooth([(-300, 40), (0, 80), (300, 40)], False), line((255, 230, 140), 8))
    c.restore()
def kuber_in(T, s=.62):
    return lambda c: seated(c, "kuber", 0, -20, s, 1, T, 0, "n")
def baby(c, x, y, k, T):
    c.save(); c.translate(x, y); c.scale(k, k); glow(c, 0, 0, 240, (255, 250, 220), .9)
    shape(c, oval(0, 0, 110, 66), (255, 246, 226), 5); shape(c, oval(-60, -20, 46), rig.CAST["kuber"]["skin"], 5)
    for e in (-74, -46): c.drawPath(smooth([(e - 6, -26), (e, -22), (e + 6, -26)], False), line(rig.INK, 3))
    c.drawPath(smooth([(-20, -50), (60, -40), (100, 20)], False), line((150, 60, 170), 8)); c.restore()
def cradle(c, x, y, T):
    a = 4 * sin(T * 2.2); c.save(); c.translate(x, y); c.drawLine(-150, 0, -110, -230, line((130, 80, 40), 12)); c.drawLine(150, 0, 110, -230, line((130, 80, 40), 12)); c.drawLine(-120, -226, 120, -226, line((130, 80, 40), 12))
    c.translate(0, -226); c.rotate(a)
    for d in (-1, 1): c.drawLine(d * 100, 0, d * 110, 150, line((200, 160, 100), 4))
    baby(c, 0, 130, .9, T); shape(c, smooth([(-150, 130), (150, 130), (120, 190), (-120, 190)]), (196, 120, 60), 5); c.restore()
def vedi(c, x, y, T):
    f = .5 + .3 * sin(T * 11) * sin(T * 7); glow(c, x, y - 40, 150, (255, 150, 50), f)
    shape(c, poly([(x - 90, y), (x - 70, y - 50), (x + 70, y - 50), (x + 90, y)]), (190, 110, 70), 5)
    for dx, h in ((-30, 70), (0, 100), (30, 64)): c.drawPath(smooth([(x + dx - 24, y - 50), (x + dx - 10, y - 50 - h * .6 - 18 * f), (x + dx, y - 50 - h - 24 * f), (x + dx + 12, y - 50 - h * .5), (x + dx + 24, y - 50)]), fill((255, 170, 50)))
def lotus_seat(c, x, y, k, T):
    c.save(); c.translate(x, y); c.scale(k, k); glow(c, 0, -20, 300, (255, 200, 220), .6)
    for row, (n, R, g) in enumerate(((9, 200, (230, 110, 160)), (7, 150, (250, 150, 190)), (5, 100, (255, 200, 220)))):
        for i in range(n): a = pi + (i + .5) * pi / n; px, py = cos(a) * R, sin(a) * R * .35 - row * 10; shape(c, smooth([(px * .4, 20), (px - 26, py), (px, py - 50), (px + 26, py)]), g, 4)
    shape(c, oval(0, 26, 210, 34), (60, 150, 90), 5); c.restore()
def daysky(c, T, mode="cycle"):
    """Live sky behind the forest. cycle: days and nights rush by. dawn/gold: still bright."""
    if mode == "cycle":
        ph = (T * .7) % 1; f = .5 + .5 * cos(2 * pi * ph)
    else: ph, f = .12, 1.
    top = mix((10, 12, 46), (90, 170, 240) if mode != "gold" else (250, 170, 90), f); bot = mix((40, 30, 80), (230, 246, 255) if mode != "gold" else (255, 236, 180), f)
    vgrad(c, [(0, top), (1, bot)], -240, 1400)
    if f < .7: r = random.Random(4); [c.drawCircle(r.uniform(-100, W + 100), r.uniform(-100, 900), r.uniform(2, 4), fill((255, 250, 230), (.7 - f) * 1.2)) for _ in range(80)]
    if mode == "cycle":
        for o, rgb, R in ((0., (255, 230, 120), 70), (.5, (240, 240, 230), 56)):
            u = ((ph - o) % 1) / .5
            if u <= 1: x, y = -100 + 1280 * u, 900 - 620 * sin(pi * u); glow(c, x, y, R * 3, rgb, .6); c.drawCircle(x, y, R, fill(rgb))
    return f
def icon(c, x, y, kind, a, T):
    """Water drop, wind, or an empty bowl, floating beside the rishi."""
    c.save(); c.translate(x, y + 10 * sin(T * 2)); glow(c, 0, 0, 130, (255, 255, 255), .35 * a)
    if kind == 0: c.drawPath(smooth([(0, -70), (40, 0), (30, 40), (0, 54), (-30, 40), (-40, 0)]), fill((120, 200, 255), a)); c.drawCircle(-12, 10, 10, fill((255, 255, 255), a))
    elif kind == 1:
        for i in range(3): c.drawPath(smooth([(-70, -40 + i * 40), (0, -50 + i * 40), (50, -40 + i * 40), (60, -70 + i * 40), (36, -76 + i * 40)], False), line((230, 245, 255), 9, a))
    else: c.drawPath(smooth([(-70, -10), (70, -10), (50, 40), (-50, 40)]), fill((180, 120, 70), a)); c.drawPath(smooth([(-70, -10), (70, -10)], False), line(INK, 5, a))
    c.restore()
def orb(c, x, y, rgb, kind, T, k=1.):
    glow(c, x, y, 170 * k, rgb, .7); c.drawCircle(x, y, 62 * k, fill(mix(rgb, (255, 255, 255), .4))); c.drawCircle(x, y, 62 * k, line((255, 250, 230), 5))
    if kind == "vajra": c.drawPath(poly([(x + 8, y - 42), (x - 22, y + 6), (x, y + 6), (x - 10, y + 44), (x + 24, y - 8), (x + 2, y - 8)]), fill((250, 170, 30)))
    elif kind == "jal": [c.drawArc(skia.Rect.MakeLTRB(x - 40 + i * 30 - 20, y - 20, x - 40 + i * 30 + 20, y + 20), 0, 180, False, line((30, 80, 180), 7)) for i in range(3)]
    elif kind == "danda": c.drawLine(x - 30, y + 40, x + 30, y - 40, line((60, 30, 60), 10)); c.drawCircle(x + 32, y - 42, 13, fill((60, 30, 60)))
    else: c.drawCircle(x, y, 26, fill((40, 200, 120))); c.drawCircle(x, y, 12, fill((255, 240, 160)))
def runner(c, who, x, t, s, d, y=GY + 20, w=9.):
    f = lambda q: (lambda u: dict(POSE["run"], x=x - d * q * 380, f1x=100 * sin(u * w), f2x=-100 * sin(u * w), f1y=max(0., 46 * cos(u * w)), f2y=max(0., -46 * cos(u * w)), a1u=-10 + 50 * sin(u * w), a2u=40 - 50 * sin(u * w), j=8 * abs(sin(u * w))))(t - q)
    body(c, rig.CAST[who], f(0), y, s, d, t, 0, "n", past=f, weapon=False)
def sparkle(c, T, n=14, seed=5, x0=200, x1=880, y0=380, y1=760):
    r = random.Random(seed)
    for i in range(n):
        x, y, ph = r.uniform(x0, x1), r.uniform(y0, y1), r.uniform(0, 6); a = max(0., sin(T * 3 + ph)); L = 26 * a
        c.drawLine(x - L, y, x + L, y, line((255, 255, 230), 4, a)); c.drawLine(x, y - L, x, y + L, line((255, 255, 230), 4, a))

# ---------------- shots: c, t (time in shot), D (shot length), tk (talk per speaker), T (time in video)
def s_hook(c, t, D, tk, T):
    sx, sy = punchcam(t, [(D * .5, 1.1)]); c.translate(sx, sy); u = ss(t / D); cam(c, 1.0 + .1 * u, 540, 820 + 40 * u); bg(c, "trikut", p_trikut)
    sparkle(c, T, 18); h = D * .5; a = 1 - ss((t - h) / .4)
    c.drawPaint(fill((110, 20, 40), .35 * a))
    if a > 0:
        c.save(); c.clipRect(skia.Rect.MakeLTRB(-600, -600, W + 600, 740)); c.saveLayerAlpha(None, int(235 * a)); c.translate(0, 150 * (1 - ss(t / (h * .8))))
        shadow_of(c, lambda: stand(c, "ravan", "roar" if t > h * .45 else "guard", 430, T, 1.6, 1, 1260, weapon=True), a=.92); c.restore(); c.restore()
        city(c, random.Random(81), 540, 460, 300); sparkle(c, T, 18)
    if t > h:
        b = ss((t - h) / .5); c.saveLayerAlpha(None, int(255 * b)); aura(c, 540, 1000, T, 520, (255, 220, 120))
        shadow_of(c, lambda: stand(c, "kuber", "hero", 540, T, 1.0, 1, GY + 40, weapon=True), rgb=(255, 214, 110), a=.95, rim=(255, 255, 230)); c.restore()
    embers(c, T, 40, (255, 210, 120)); vig(c)
def s_vivah(c, t, D, tk, T):
    u = ss(t / D); cam(c, 1.12 - .08 * u, 540, 1080); bg(c, "ashram", p_ashram3, 30 - 30 * u)
    vedi(c, 540, 1320, T)
    stand(c, "vishrava", "namaste" if t > D * .5 else "stand", 290, T, .9, 1, GY + 20, weapon=False, head=8)
    stand(c, "patni", "namaste", 790, T, .9, -1, GY + 30, weapon=False, head=12); petals(c, T, 40, 13); vig(c)
def s_naam(c, t, D, tk, T):
    u = ss(t / D); cam(c, 1.06 + .1 * u, 540, 1060); bg(c, "ashram", p_ashram3, -60)
    for i in range(7): a = -pi / 2 + (i - 3) * .12; c.drawPath(poly([(470, -100), (470 + cos(a - .03) * 1500, -100 - sin(a - .03) * -1500), (470 + cos(a + .03) * 1500, -100 - sin(a + .03) * -1500)]), fill((255, 250, 220), .18))
    stand(c, "patni", "namaste", 170, T, .84, 1, GY + 30, weapon=False, head=16)
    cradle(c, 470, 1360, T)
    stand(c, "pulastya", "talk", 820, T, .94, -1, GY + 20, talk=tk.get("P", 0), weapon=False, a1u=120 + 15 * sin(T * 2), a1f=150, head=10); petals(c, T, 16, 4); vig(c)
def s_tap(c, t, D, tk, T):
    u = ss(t / D); cam(c, 1.0 + .25 * u, 540, 1080 - 40 * u); f = daysky(c, T); bg(c, "tapvan", p_tapvan)
    c.drawPaint(fill((10, 10, 40), .5 * (1 - f)))
    aura(c, 540, 1080, T, 300 + 260 * u, (255, 236, 160)); seated(c, "kuber", 540, 1440, 1.0, 1, T, 0, "n")
    for k in range(3):
        a0 = .45 + k * .17; a = ss((t / D - a0) / .06) * (1 - ss((t / D - a0 - .15) / .05)) if k < 2 else ss((t / D - a0) / .06)
        if a > 0: icon(c, 860, 820, k, a, T)
    petals(c, T, 14, 21); vig(c)
def s_brahma(c, t, D, tk, T):
    u = ss(t / D); cam(c, 1.0, 540, 1000 - 40 * u); daysky(c, T, "gold"); bg(c, "tapvan", p_tapvan); c.drawPaint(fill((255, 230, 160), .25 + .15 * u))
    for i in range(18): a = i * pi / 9 + T * .2; c.drawPath(poly([(640, 700), (640 + cos(a) * 1600, 700 + sin(a) * 1600), (640 + cos(a + .08) * 1600, 700 + sin(a + .08) * 1600)]), fill((255, 250, 220), .2 * ss(t / .8)))
    for i in range(6): a = i * pi / 3 + T * .5; glow(c, 640 + cos(a) * 330, 760 + sin(a) * 200, 70, (255, 250, 220), .8); c.drawCircle(640 + cos(a) * 330, 760 + sin(a) * 200, 16, fill((255, 255, 240)))
    v = ss((t - .2) / (D * .6)); yb = 760 + 440 * v
    seated(c, "kuber", 220, 1450, .8, 1, T, 0, "n")
    stand(c, "brahma", "stand", 680, T, .82, -1, yb, weapon=True, a1u=110, a1f=150, shadow=False); lotus_seat(c, 680, yb + 10, .9, T)
    embers(c, T, 40, (255, 240, 190)); vig(c)
def s_var(c, t, D, tk, T):
    cam(c, 1.1 + .06 * ss(t / D), 560, 1080); daysky(c, T, "gold"); bg(c, "tapvan", p_tapvan, -40); aura(c, 740, 1000, T, 480, (255, 230, 170))
    stand(c, "kuber", "namaste", 290, T, .9, 1, GY + 20, weapon=False, head=12)
    stand(c, "brahma", "talk", 770, T, .86, -1, GY - 10, talk=tk.get("B", 0), weapon=True, a1u=120 + 20 * sin(T * 2), a1f=150, shadow=False); lotus_seat(c, 770, GY, .8, T)
    petals(c, T, 20, 7); vig(c)
def s_maang(c, t, D, tk, T):
    cam(c, 1.5 + .1 * ss(t / D), 460, 1080); daysky(c, T, "dawn"); bg(c, "tapvan", p_tapvan, 60); aura(c, 460, 1060, T, 380, (255, 240, 200))
    stand(c, "kuber", "namaste", 460, T, .95, 1, GY + 20, talk=tk.get("K", 0), weapon=False, head=6 + 4 * sin(T * 1.5)); embers(c, T, 24, (255, 240, 200)); vig(c)
def s_lokpal(c, t, D, tk, T):
    u = ss(t / D); cam(c, 1.1 - .1 * u, 540, 960); bg(c, "lok", p_lok)
    sx, sy = punchcam(t, [(.15, .8)]); c.translate(sx, sy)
    for i, (g, kd) in enumerate((((255, 220, 90), "vajra"), ((90, 170, 255), "jal"), ((200, 120, 200), "danda"))):
        a = -pi / 2 + i * pi * 2 / 3 + T * .5; R = 420; orb(c, 540 + cos(a) * R, 900 + sin(a) * R * .9, g, kd, T, ss((t - .3 - i * .5) / .4))
    k = ss((t - 2.0) / .8); glow(c, 540, 1000, 300 + 200 * k, (100, 230, 160), .5 * k)
    stand(c, "kuber", "hero", 540, T, .9, 1, GY + 10, weapon=True)
    if k > 0: orb(c, 540, 560 - 20 * sin(T * 2), (60, 220, 140), "dhan", T, k)
    embers(c, T, 40, (220, 230, 255)); vig(c)
def s_pushpak(c, t, D, tk, T):
    sx, sy = punchcam(t, [(D * .55, .9)], 10); c.translate(sx, sy); cam(c, 1.0 + .06 * ss(t / D), 540, 1000); bg(c, "aakash", p_aakash, -30 * t)
    clouds(c, T, 400, 5, 3, (255, 255, 255), .5, 300, 1200); v = ss(t / (D * .6))
    for i in range(14): a = i * pi / 7 + T * .4; c.drawPath(poly([(640, 760), (640 + cos(a) * 1500, 760 + sin(a) * 1500), (640 + cos(a + .07) * 1500, 760 + sin(a + .07) * 1500)]), fill((255, 250, 210), .2 * v))
    pushpak(c, 640, -300 + 1250 * v, .78, T, tilt=-10 * (1 - v))
    stand(c, "kuber", "namaste" if v > .9 else "point", 230, T, .82, 1, GY + 30, weapon=False, head=-24); embers(c, T, 30, (255, 236, 160)); vig(c)
def s_ghar(c, t, D, tk, T):
    cam(c, 1.04 + .06 * ss(t / D), 540, 1060); bg(c, "ashram", p_ashram3, 40 - 20 * t); pushpak(c, 560, 640, .56, T)
    stand(c, "kuber", "talk", 250, T, .9, 1, GY + 20, talk=tk.get("K", 0), weapon=False, a1u=60 + 25 * sin(T * 2.4), a1f=100, head=-4)
    stand(c, "vishrava", "stand", 820, T, .92, -1, GY + 20, weapon=False, head=6 * sin(T * 1.3)); petals(c, T, 10, 3); vig(c)
def s_trikut(c, t, D, tk, T):
    u = ss(t / D); cam(c, 1.0 + .3 * u, 540, 1250 - 600 * u); bg(c, "trikut", p_trikut); sparkle(c, T, 26, 9)
    glow(c, 540, 600, 300 + 40 * sin(T * 3), (255, 230, 140), .35); clouds(c, T, 120, 4, 9, (255, 250, 240), .45, 400, 900); vig(c)
def s_chhod(c, t, D, tk, T):
    h = D * .5
    if t < h:
        cam(c, 1.05, 540, 1000); bg(c, "trikut", p_trikut, 40); c.drawPaint(fill((40, 20, 70), .45))
        for i, who in enumerate(("rakshas3", "rakshas5", "rakshas8")):
            x = 220 + i * 230 + 420 * ss((t - i * .15) / h); c.save(); shadow_of(c, lambda: runner(c, who, x, T + i, .72, 1, GY + 30 - i * 10), a=.95, rim=(255, 120, 80)); c.restore()
        glow(c, 540, 300, 300, (200, 220, 255), .5)
    else:
        q = t - h; cam(c, 1.08 - .05 * ss(q / (D - h)), 540, 1080); bg(c, "ashram", p_ashram3, -20)
        stand(c, "kuber", "namaste", 300, T, .9, 1, GY + 20, weapon=False, head=14)
        stand(c, "vishrava", "talk", 780, T, .92, -1, GY + 20, talk=tk.get("V", 0), weapon=False, a1u=130 + 10 * sin(T * 2), a1f=160, head=8); petals(c, T, 30, 17)
        c.drawPaint(fill((255, 250, 230), 1 - ss(q / .3)))
    vig(c)
def s_raja(c, t, D, tk, T):
    h = D * .5
    if t < h:
        u = ss(t / h); cam(c, 1.15, 540, 900); bg(c, "trikut", p_trikut, 60 - 120 * u); sparkle(c, T, 20, 3)
        pushpak(c, -200 + 1000 * u, 600 + 80 * sin(u * pi), .62, T, kuber_in(T), tilt=6)
        petals(c, T, 30, 31)
    else:
        q = t - h; u = ss(q / (D - h)); cam(c, 1.02 + .06 * u, 540, 1060); bg(c, "ashram", p_ashram3, 20)
        pushpak(c, 560, 380 + 420 * ss(q / 1.2), .6, T, kuber_in(T))
        stand(c, "vishrava", "namaste", 180, T, .84, 1, GY + 20, weapon=False, head=-16)
        stand(c, "patni", "namaste", 900, T, .82, -1, GY + 30, weapon=False, head=-16); petals(c, T, 40, 33)
        c.drawPaint(fill((255, 250, 230), 1 - ss(q / .3)))
    vig(c)
def s_end(c, t, D, tk, T):
    u = ss(t / D); cam(c, 1.0 + .15 * u, 540, 1040); bg(c, "raat", p_raat)
    for i, (who, x, s) in enumerate((("rakshas5", 280, .9), ("rakshas3", 800, .95), ("rakshas8", 540, 1.15))):
        rise = ss((t - i * .4) / 1.6); c.save(); c.translate(0, 700 * (1 - rise)); shadow_of(c, lambda: stand(c, who, "roar" if i == 2 else "guard", x, T, s, 1 if x < 540 else -1, GY + 60, weapon=True), a=.95, rim=(200, 60, 120)); c.restore()
    embers(c, T, 30, (200, 120, 255)); vig(c)
    c.drawPaint(fill((10, 4, 20), .45 * ss((t - 3.2) / .5)))

N, PU, BR, KU, VI = (S, "+2%", "+0Hz"), (M, "-4%", "-16Hz"), (M, "-12%", "-12Hz"), (M, "+2%", "+8Hz"), (M, "-2%", "-6Hz")
def L(shot, w, v, hi, ro, **k): return dict(shot=shot, who=w, v=v, hi=hi, ro=ro, **k)
LINES = [
 L("hook", "N", N, "सोने की लंका... पहले रावण की नहीं थी! तो किसकी थी?", "Sone ki *Lanka...* pehle Ravan ki nahin thi! Toh *kiski* thi?", pad=.7),
 L("vivah", "N", N, "विश्रवा भी पिता की तरह तपस्वी बने, और भरद्वाज मुनि की बेटी से विवाह किया।", "Vishrava bhi pita ki tarah *tapasvi* bane, aur Bharadwaj muni ki beti se *vivah* kiya.", pad=.4),
 L("naam", "P", PU, "ये अपने पिता जैसा है, इसलिए इसका नाम होगा वैश्रवण! ये धन का रक्षक बनेगा।", "Ye apne pita jaisa hai, isliye iska naam hoga *Vaishravan!* Ye *dhan* ka rakshak banega.", pad=.5),
 L("tap", "N", N, "वैश्रवण ने वन में हज़ार वर्ष तप किया... कभी सिर्फ़ जल, कभी सिर्फ़ हवा, कभी कुछ नहीं!", "Vaishravan ne van mein *hazaar varsh* tap kiya... kabhi sirf jal, kabhi sirf hawa, kabhi *kuchh nahin!*", pad=.5),
 L("brahma", "N", N, "तब देवताओं के साथ, स्वयं ब्रह्मा जी प्रकट हुए।", "Tab devtaon ke saath, swayam *Brahma ji* prakat hue.", pad=.6),
 L("var", "B", BR, "पुत्र, मैं तुम्हारे तप से बहुत प्रसन्न हूँ। वर माँगो!", "Putra, main tumhare tap se bahut *prasann* hoon. *Var* maango!", pad=.4),
 L("maang", "K", KU, "भगवन, मैं संसार का रक्षक बनना चाहता हूँ।", "Bhagwan, main sansaar ka *rakshak* banna chahta hoon.", pad=.4),
 L("lokpal", "B", BR, "तथास्तु! इंद्र, वरुण और यम के साथ, तुम चौथे लोकपाल बनोगे।", "*Tathastu!* Indra, Varun aur Yam ke saath, tum chauthe *lokpal* banoge.", pad=.5),
 L("pushpak", "N", N, "और उपहार में मिला, सूरज जैसा चमकता, पुष्पक विमान!", "Aur upahaar mein mila, suraj jaisa chamakta, *Pushpak vimaan!*", pad=.7),
 L("ghar", "K", KU, "पिताजी, वर तो मिल गया, पर मेरा कोई घर नहीं। मैं कहाँ रहूँ?", "Pitaji, var toh mil gaya, par mera koi *ghar* nahin. Main *kahan* rahoon?", pad=.4),
 L("trikut", "V", VI, "दक्षिण सागर के तट पर त्रिकूट पर्वत है। वहाँ विश्वकर्मा की बनाई लंका है।", "Dakshin saagar ke tat par *Trikut* parvat hai. Wahan Vishwakarma ki banayi *Lanka* hai.", pad=.4),
 L("chhod", "V", VI, "राक्षस विष्णु के डर से उसे छोड़ गए। वहाँ जाओ, सुख से रहो!", "Rakshas *Vishnu* ke darr se use chhod gaye. Wahan jaao, *sukh* se raho!", pad=.5),
 L("raja", "N", N, "वैश्रवण, यानी कुबेर, लंका के राजा बने, और पुष्पक में बैठ कर माता-पिता से मिलने आते।", "Vaishravan, yaani *Kuber,* Lanka ke *raja* bane, aur Pushpak mein baith kar maata-pita se milne aate.", pad=.8),
 L("end", "N", N, "अगले भाग में: राक्षस कैसे बने?", "Agle bhaag mein: *Rakshas* kaise bane?", pad=3.6),
]
SH = {k[2:]: v for k, v in list(globals().items()) if k.startswith("s_")}
HEAT = dict(hook=3, vivah=0, naam=1, tap=2, brahma=2, var=1, maang=0, lokpal=3, pushpak=2, ghar=0, trikut=1, chhod=2, raja=1, end=2)

def mus(n, tl):
    b = np.zeros(n); q = np.arange(n) / SR
    for f, a in ((110, .3), (165, .2), (220, .14)): b += a * np.sin(2 * pi * f * q + .4 * np.sin(2 * pi * .25 * q)) * (1 + .3 * np.sin(2 * pi * .35 * q + f))
    sc = [440, 494, 554, 659, 740, 880]; r = random.Random(9)
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
        if n == "hook": au.add(f, s + .2, boom(1.6), .8); au.add(f, s + D * .5, au.bell(880, 2.5), .45)
        if n in ("vivah", "naam", "raja"): au.add(f, s + .1, au.bell(660, 2.5), .35)
        if n == "tap": au.add(f, s + .2, au.bell(220, 3.5), .5); au.add(f, s + D * .5, au.sweep(200, 600, 2.0, 3), .2)
        if n == "brahma": au.add(f, s + .1, au.sweep(300, 1200, 1.8, 3), .3); au.add(f, s + .3, au.bell(880, 3), .4)
        if n == "lokpal": au.add(f, s + .15, boom(1.3), .85); au.add(f, s + 2.0, au.bell(990, 2.5), .4)
        if n == "pushpak": wh(s + .2, .4, 1.2); au.add(f, s + D * .55, boom(1.2), .6)
        if n == "trikut": au.add(f, s + .2, au.bell(740, 3), .3)
        if n == "chhod": wh(s + .2, .35, .7); au.add(f, s + D * .5, au.bell(660, 2.5), .35)
        if n == "end": au.add(f, s + .2, boom(1.4), .7)
if __name__ == "__main__": run("bhaag003", LINES, SH, ("RAMAYAN  |  BHAAG 3", "KUBER KI LANKA"), mus, fx)
