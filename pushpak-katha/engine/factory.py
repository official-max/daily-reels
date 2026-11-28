"""Kirdaar factory: a character is a short design (a dict of choices), the factory turns it into a rig character.

    spec -> make(spec) -> dict for rig.body() (head, clothes, weapon, size)
    auto(kind, seed, cast) -> a new minor character that does not look like anyone in the cast
    python engine/factory.py   -> out/cast_sheet.jpg (all of cast/ramayan.json + 4 automatic extras)

Design fields (all optional): kind human|rakshas|vanar, sex m|f, age young|adult|old, build thin|normal|strong|huge, size (height),
skin, hair, hair_rgb, beard none|stubble|short|long|moustache|curled, crown none|tall|low|tiara|rakshas|helmet|vanar|turban,
tilak none|u|tripund|dot|bindi, eyes calm|kind|fierce|sleepy|wise, top bare|uttariya|kavach|robe|blouse|bark, lower dhoti|long|saree|bark,
cloth, edge, jewel, weapon none|bow|gada|khadga|trishul|danda|kamandal|lotus, heads (Ravan: 10), fangs, tusks, fur (vanar).
"""
import os, sys, json, random, math
import skia
from math import sin, cos, pi
from lab import ROOT, col, mix, fill, line, glow, poly, smooth, oval
import rig
from rig import shape, INK, blink

T = lambda q: tuple(q) if q is not None else None
SKIN = dict(shyam=(92, 150, 212), fair=(240, 196, 156), wheat=(222, 166, 118), brown=(170, 112, 74), dark=(118, 78, 60),
            ash=(150, 150, 140), green=(104, 128, 96), maroon=(140, 70, 70), vanar=(238, 128, 66))
GOLD = (255, 200, 46)


def _c(v, d):
    if v is None: return d
    return SKIN.get(v, d) if isinstance(v, str) else tuple(v)


# ---------------- head parts, neck at (0, 0), face looking right
def face_path(sp, m):
    k, sex, age = sp.get("kind", "human"), sp.get("sex", "m"), sp.get("age", "adult")
    jw = {"rakshas": 1.14, "human": 1.0}.get(k, 1.0) * (.9 if sex == "f" else 1) * (1.06 if sp.get("build") in ("strong", "huge") else 1)
    ch = -6 if sex == "f" else 0
    pts = [(-58, -30), (-66, -100), (-44, -150), (14, -164), (66, -148), (74, -104), (72 * jw, -50), (46 * jw, -6 + m + ch), (6, 4 + m + ch), (-36 * jw, -8)]
    return smooth(pts)


def back_hair(c, sp, hr):
    s = sp.get("hair", "long")
    if s in ("long", "crown"): shape(c, smooth([(-40, -170), (-88, -110), (-92, 10), (-78, 76), (-30, 60), (-10, -60)]), hr)
    elif s == "braid":
        shape(c, smooth([(-40, -170), (-96, -110), (-96, -20), (-60, 20), (-20, -60)]), hr)
        for i in range(7): y = 10 + i * 40; shape(c, oval(-74 + sin(i) * 4, y, 22 - i * 1.6, 26), hr, 4)
        for i in range(5): c.drawCircle(-92 + i * 6, -80 + i * 14, 9, fill((255, 250, 250)))
    elif s == "jata":
        shape(c, smooth([(-40, -170), (-96, -100), (-100, 40), (-70, 110), (-20, 80), (-10, -60)]), hr)
        for i in range(4): c.drawPath(smooth([(-60 - i * 8, -120), (-80 - i * 6, -20), (-70 - i * 4, 90)], False), line(mix(hr, INK, .3), 4))
    elif s == "wild":
        shape(c, poly([(-10, -190), (-60, -220), (-70, -180), (-130, -190), (-110, -140), (-170, -110), (-120, -80), (-160, -20), (-110, -10), (-120, 50), (-60, 20), (-20, -40)]), hr)


def front_hair(c, sp, hr):
    s = sp.get("hair", "long")
    if s == "bald": c.drawPath(smooth([(-40, -150), (-70, -150), (-80, -110)], False), line(hr, 16)); return
    if s == "tuft": shape(c, smooth([(-20, -158), (-30, -186), (-60, -200), (-40, -170)]), hr, 4); return
    if s == "wild":
        shape(c, poly([(-66, -96), (-60, -170), (-20, -200), (0, -176), (30, -214), (44, -168), (80, -180), (76, -132), (40, -146), (0, -136), (-30, -110)]), hr); return
    if s == "short": shape(c, smooth([(-64, -100), (-62, -160), (10, -184), (70, -160), (74, -134), (30, -146), (-20, -132), (-40, -100)]), hr); return
    shape(c, smooth([(-66, -90), (-62, -164), (10, -190), (72, -160), (74, -130), (20, -150), (-30, -124)]), hr)
    if s == "jata": shape(c, smooth([(-40, -176), (-40, -236), (0, -270), (40, -236), (34, -176)]), hr); c.drawLine(-36, -190, 32, -190, line(mix(hr, (200, 160, 120), .6), 9)); [c.drawPath(smooth([(-30 + i * 16, -240), (-24 + i * 14, -200)], False), line(mix(hr, INK, .3), 4)) for i in range(4)]


def eyes(c, sp, t, mood, sk):
    e, sex, k = sp.get("eyes", "calm"), sp.get("sex", "m"), sp.get("kind", "human")
    l = max(blink(t), {"calm": .1, "kind": 0, "sleepy": .58, "wise": .28}.get(e, 0))
    iris = (200, 40, 30) if k == "rakshas" and e == "fierce" else (60, 30, 24)
    b = 1 if e == "fierce" or mood == "angry" else -1 if mood == "sad" else 0
    for x, r in ((12, 18), (54, 15)):
        ry = 15 if e != "fierce" else 12
        q = smooth([(x - r, -90), (x - r * .4, -90 - ry * 1.3), (x + r * .6, -91 - ry * 1.1), (x + r * 1.1, -92), (x + r * .3, -90 + ry * .9), (x - r * .5, -88 + ry * .7)])
        c.save(); c.clipPath(q, True); c.drawPaint(fill((255, 252, 246))); c.drawCircle(x + 5, -93, 11.5, fill(mix(iris, (20, 10, 10), .5))); c.drawCircle(x + 5, -91, 8, fill(iris)); c.drawCircle(x + 5, -93, 5, fill((14, 6, 8))); c.drawCircle(x + 9, -98, 3.6, fill((255, 255, 255))); c.drawCircle(x + 1, -88, 1.8, fill((255, 255, 255)))
        if l > 0: c.drawRect(skia.Rect.MakeLTRB(x - r - 4, -112, x + r + 6, -112 + 24 * l + 4), fill(sk))
        c.restore()
        top = smooth([(x - r * 1.1, -89), (x - r * .4, -90 - ry * 1.35 + 24 * l), (x + r * 1.2, -93 + 2 * l)], False); c.drawPath(top, line((50, 24, 20), 4.5 if sex == "m" else 7))
        if sex == "f": c.drawPath(smooth([(x + r * 1.1, -93), (x + r * 1.6, -99)], False), line(INK, 5))
        bw = 9 if sp.get("age") != "old" else 10; bc = _c(sp.get("brow"), _c(sp.get("hair_rgb"), (30, 20, 30)))
        if e == "fierce" or b == 1: c.drawPath(smooth([(x - 16, -126), (x, -120), (x + 18, -112)], False), line(bc, bw))
        elif b == -1: c.drawPath(smooth([(x - 16, -114), (x, -124), (x + 16, -122)], False), line(bc, bw - 3))
        else: c.drawPath(smooth([(x - 16, -118), (x, -127), (x + 18, -122)], False), line(bc, bw - (5 if sex == "f" else 3)))
    if sp.get("age") == "old":
        for i in range(3): c.drawPath(smooth([(-6 + i * 4, -140 + i * 8), (30, -144 + i * 8), (66, -138 + i * 8)], False), line(mix(sk, INK, .35), 3))
        c.drawPath(smooth([(70, -82), (76, -74), (70, -66)], False), line(mix(sk, INK, .35), 3))


def mouth(c, sp, talk, mood, sk):
    m = talk * 16; k = sp.get("kind", "human")
    if m > 1: q = smooth([(26, -36), (48, -40), (64, -38), (48, -30 + m)]); c.drawPath(q, fill((150, 30, 50))); c.drawPath(q, line((110, 24, 40), 3))
    else:
        down = mood in ("sad",) or sp.get("eyes") == "fierce"; c.drawPath(smooth([(28, -36), (46, -42 if down else -30), (64, -38)], False), line((150, 40, 56), 5))
    if sp.get("fangs") or k == "rakshas":
        for x in (30, 58): c.drawPath(poly([(x - 5, -36), (x + 5, -36), (x, -22 - m * .3)]), fill((255, 250, 232))); c.drawPath(poly([(x - 5, -36), (x + 5, -36), (x, -22 - m * .3)]), line(INK, 2))
    if sp.get("tusks"):
        for x in (26, 64): q = smooth([(x - 7, -30), (x + 7, -30), (x + 4, -66), (x - 2, -80)]); c.drawPath(q, fill((250, 244, 220))); c.drawPath(q, line(INK, 3))


def beard(c, sp, m, hr):
    b = sp.get("beard", "none")
    if b in ("long", "short"):
        L = 150 if b == "long" else 50; shape(c, smooth([(-46, -60), (-20, -44), (20, -34), (72, -46), (84, -20 + m), (62, L * .55 + m), (24, L + m), (-14, L * .55), (-50, 0)]), hr, 5)
        [c.drawPath(smooth([(10 + i * 14, -20 + m), (14 + i * 12, L * .5 + m)], False), line(mix(hr, INK, .22), 3)) for i in range(4)]
    if b == "stubble": c.drawPath(smooth([(-40, -40), (10, 0), (60, -10)], False), line(mix(hr, (200, 160, 140), .5), 14, .5))
    if b in ("moustache", "curled", "long", "short"):
        w = 8 if b != "curled" else 11; q = smooth([(32, -50), (12, -46), (-4, -54), (-8, -66)] if b == "curled" else [(36, -50), (18, -44), (6, -48)], False)
        c.drawPath(smooth([(36, -54), (56, -52), (80, -48)], False), line(hr, w + 2)); c.drawPath(q, line(hr, w))
        if b == "curled": c.drawPath(smooth([(78, -50), (96, -54), (98, -70), (88, -72)], False), line(hr, w))


def tilak(c, sp):
    t = sp.get("tilak", "none")
    if t == "u": c.drawPath(smooth([(24, -150), (30, -118), (36, -150)], False), line((255, 240, 200), 7)); c.drawLine(30, -150, 30, -122, line((220, 30, 40), 5))
    elif t == "tripund": [c.drawLine(4, -144 + i * 8, 56, -146 + i * 8, line((250, 248, 240), 4)) for i in range(3)]; c.drawCircle(32, -138, 5, fill((220, 30, 40)))
    elif t == "dot": c.drawCircle(32, -128, 6, fill((220, 30, 40)))
    elif t == "bindi": c.drawCircle(34, -124, 7, fill((210, 20, 50))); c.drawCircle(34, -124, 2.5, fill((255, 230, 150)))


def crown(c, sp):
    cr, g = sp.get("crown", "none"), _c(sp.get("edge_gold"), GOLD); j = _c(sp.get("jewel"), (220, 40, 60))
    if cr == "tall":
        shape(c, poly([(-64, -134), (74, -138), (70, -176), (52, -196), (40, -250), (20, -290), (0, -250), (-18, -200), (-50, -186), (-66, -166)]), g, 6)
        for y in (-150, -186): c.drawLine(-60, y, 70, y - 4, line(mix(g, INK, .4), 4))
        c.drawCircle(18, -214, 12, fill(j)); c.drawCircle(20, -164, 8, fill(j)); [c.drawCircle(-40 + i * 24, -146, 5, fill((255, 250, 220))) for i in range(5)]
    elif cr == "low":
        shape(c, poly([(-66, -134), (74, -138), (72, -164), (50, -176), (30, -214), (8, -178), (-22, -196), (-40, -168), (-66, -162)]), g, 6); c.drawCircle(28, -162, 9, fill(j))
    elif cr == "rakshas":
        dk = mix(g, (90, 30, 40), .08); pts = [(-70, -132), (80, -138)]
        for i in range(7): x = 76 - i * 24; pts.append((x, -176 - (40 if i % 2 else 0) - (30 if i == 3 else 0)))
        pts.append((-72, -168)); shape(c, poly(pts), dk, 6); [c.drawCircle(-50 + i * 30, -152, 7, fill(j)) for i in range(5)]
    elif cr == "helmet":
        shape(c, smooth([(-70, -110), (-66, -170), (10, -200), (76, -166), (78, -128), (10, -146)]), g, 6); shape(c, poly([(-10, -196), (0, -250), (16, -196)]), j, 4); c.drawLine(-66, -128, 78, -130, line(mix(g, INK, .4), 8))
    elif cr == "tiara":
        c.drawPath(smooth([(74, -142), (10, -170), (-56, -136)], False), line(g, 8)); c.drawLine(34, -160, 34, -138, line(g, 4)); c.drawCircle(34, -134, 8, fill(j)); c.drawCircle(-46, -56, 13, line(g, 6))
    elif cr == "vanar":
        shape(c, poly([(-78, -146), (-70, -196), (-44, -174), (-18, -236), (8, -190), (34, -250), (54, -188), (82, -206), (88, -146)]), g); shape(c, poly([(-84, -164), (92, -162), (88, -134), (-80, -136)]), j, 5)
    elif cr == "turban":
        shape(c, smooth([(-70, -110), (-74, -170), (0, -206), (76, -176), (78, -128), (0, -146)]), _c(sp.get("turban_rgb"), (240, 240, 230)), 6); c.drawCircle(30, -170, 9, fill(j))


def ears(c, sp, sk):
    k = sp.get("kind", "human")
    if k == "rakshas": shape(c, smooth([(-40, -102), (-96, -132), (-74, -88), (-50, -60)]), sk, 4)
    else: shape(c, oval(-44, -82, 14, 20), sk, 4)
    if sp.get("crown") not in ("tiara",): c.drawCircle(-46, -52, 10, fill(_c(sp.get("edge_gold"), GOLD)))


def vanar_head(c, t, talk, mood, sp, p):
    sk, fur = p["skin"], _c(sp.get("fur"), (190, 78, 34)); muz = mix(sk, (255, 240, 210), .4)
    shape(c, smooth([(-70, 6), (-98, -70), (-86, -150), (-10, -186), (66, -160), (84, -90), (60, 0), (0, 24)]), fur); shape(c, oval(-62, -84, 25, 30), sk, 5)
    shape(c, smooth([(-40, -20), (-46, -90), (-34, -140), (20, -150), (74, -138), (82, -90), (74, -40), (30, 0)]), sk, 5)
    m = talk * 22; shape(c, smooth([(-16, -30), (-6, -64), (40, -72), (92, -66), (112, -42), (100, -10 + m * .5), (50, 10 + m), (0, m * .4)]), muz, 5); c.drawPath(smooth([(70, -72), (100, -74), (104, -58), (84, -54)]), fill((120, 40, 30)))
    c.drawPath(smooth([(18, -26), (56, -14 if mood != "angry" else -30), (98, -28)], False), line(INK, 5))
    l = blink(t)
    for x, r in ((8, 19), (58, 17)): rig.eye(c, x, -100, r, 21, lid=max(l, .15 if sp.get("eyes") == "calm" else 0), brow=1 if sp.get("eyes") == "fierce" else 0)
    tilak(c, sp); crown(c, sp)


def make_head(sp):
    def h(c, t, talk, mood, p):
        if sp.get("kind") == "vanar": return vanar_head(c, t, talk, mood, sp, p)
        sk = p["skin"]; hr = _c(sp.get("hair_rgb"), (30, 20, 34)); m = talk * 16
        back_hair(c, sp, hr); ears(c, sp, sk); shape(c, face_path(sp, m), sk)
        c.drawPath(smooth([(60, -96), (82 if sp.get("kind") == "rakshas" else 78, -64), (60, -58)], False), line(mix(sk, (90, 20, 30), .5), 6))
        if sp.get("sex") == "f": c.drawOval(skia.Rect.MakeLTRB(50, -76, 82, -56), fill((255, 110, 120), .3, 6))
        eyes(c, sp, t, mood, sk); mouth(c, sp, talk, mood, sk); beard(c, sp, m, hr); front_hair(c, sp, hr); tilak(c, sp); crown(c, sp)
        if sp.get("sex") == "f": c.drawCircle(70, -66, 4, fill(_c(sp.get("edge_gold"), GOLD)))
    return h


def many_heads(fn, n):
    """Ravan: the main head in front, the others in a fan behind it."""
    if n <= 1: return fn
    def h(c, t, talk, mood, p):
        side = [(-1) ** i * (i // 2 + 1) for i in range(n - 1)]
        for k in sorted(side, key=lambda q: -abs(q)):
            c.save(); c.translate(k * 62, -30 - abs(k) * 15); c.rotate(k * 3); c.scale(.7, .7); c.saveLayer(None, skia.Paint(ColorFilter=skia.ColorFilters.Blend(col((40, 10, 40), .1), skia.BlendMode.kSrcATop))); fn(c, t + abs(k) * .7, 0, mood, p); c.restore(); c.restore()
        fn(c, t, talk, mood, p)
    return h


# ---------------- clothes and things in hand
def top_fn(kind, cl, eg):
    def kavach(c, tor, p):
        q = smooth(tor([(-62, -40), (-80, -150), (-66, -206), (0, -218), (66, -206), (86, -150), (62, -40)])); shape(c, q, mix(eg, (120, 120, 140), .35), 6); c.save(); c.clipPath(q, True)
        for i in range(5): c.drawPath(smooth(tor([(-80, -60 - i * 30), (0, -50 - i * 30), (90, -60 - i * 30)]), False), line(mix(eg, INK, .4), 5))
        c.restore(); cc = tor([(14, -160)])[0]; shape(c, oval(cc[0], cc[1], 26), eg, 5); c.drawCircle(cc[0], cc[1], 10, fill(p["jewel"]))
    def robe(c, tor, p):
        shape(c, smooth(tor([(-62, -20), (-86, -150), (-70, -210), (-10, -222), (30, -150), (66, -60), (60, -10)])), cl); c.drawPath(smooth(tor([(-60, -212), (10, -120), (62, -30)]), False), line(eg, 10))
    def uttariya(c, tor, p):
        for w, r in ((40, INK), (30, cl)): c.drawPath(smooth(tor([(-72, -200), (-20, -150), (40, -180), (80, -196)]), False), line(r, w))
        c.drawPath(smooth(tor([(-72, -200), (-20, -154), (40, -184), (80, -196)]), False), line(eg, 6))
    def blouse(c, tor, p):
        shape(c, smooth(tor([(-60, -40), (-90, -150), (-70, -206), (0, -214), (70, -206), (70, -40)])), cl); c.drawPath(smooth(tor([(-66, -206), (0, -110), (64, -40)]), False), line(INK, 42)); c.drawPath(smooth(tor([(-66, -206), (0, -110), (64, -40)]), False), line(mix(cl, (255, 255, 255), .12), 32)); c.drawPath(smooth(tor([(-66, -190), (4, -100), (64, -28)]), False), line(eg, 8))
    def bark(c, tor, p):
        shape(c, smooth(tor([(-62, -20), (-86, -150), (-70, -210), (-10, -222), (30, -150), (66, -60), (60, -10)])), (150, 110, 70)); [c.drawPath(smooth(tor([(-60 + i * 22, -200 + i * 10), (-30 + i * 22, -40)]), False), line((110, 76, 50), 4)) for i in range(5)]
    return dict(kavach=kavach, robe=robe, uttariya=uttariya, blouse=blouse, bark=bark).get(kind)


def _ax(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy) or 1; return (dx / L, dy / L), (-dy / L, dx / L)
def bow(c, a, b, rgb=(150, 80, 40)):
    u, n = _ax(a, b); P = lambda q, w: (a[0] + u[0] * q + n[0] * w, a[1] + u[1] * q + n[1] * w)
    c.drawLine(*P(-210, -40), *P(230, -40), line((250, 240, 220), 3)); q = smooth([P(-210, -40), P(-110, 20), P(0, 34), P(120, 20), P(230, -40)], False); c.drawPath(q, line(INK, 22)); c.drawPath(q, line(rgb, 13)); c.drawPath(q, line(GOLD, 3))
def trishul(c, a, b):
    u, n = _ax(a, b); P = lambda q, w: (a[0] + u[0] * q + n[0] * w, a[1] + u[1] * q + n[1] * w)
    c.drawLine(*P(-120, 0), *P(230, 0), line(INK, 16)); c.drawLine(*P(-120, 0), *P(230, 0), line((200, 170, 120), 9))
    for w in (-36, 0, 36): q = smooth([P(220, 0), P(250, w * .9), P(300 + (16 if not w else 0), w)], False); c.drawPath(q, line(INK, 14)); c.drawPath(q, line((210, 216, 226), 8))
def danda(c, a, b):
    u, n = _ax(a, b); P = lambda q, w: (a[0] + u[0] * q + n[0] * w, a[1] + u[1] * q + n[1] * w); c.drawLine(*P(-150, 0), *P(220, 0), line(INK, 16)); c.drawLine(*P(-150, 0), *P(220, 0), line((150, 100, 60), 9))
def kamandal(c, a, b):
    x, y = a; shape(c, smooth([(x - 34, y + 30), (x - 40, y + 80), (x, y + 104), (x + 40, y + 80), (x + 34, y + 30)]), (170, 110, 60), 5); c.drawPath(smooth([(x - 30, y + 30), (x, y - 10), (x + 30, y + 30)], False), line(INK, 7))
def lotus(c, a, b):
    x, y = a[0] + 6, a[1] - 34
    for k in range(5): q = (k - 2) * .45; shape(c, smooth([(x, y + 30), (x + sin(q) * 36 - 12, y - cos(q) * 30), (x + sin(q) * 50, y - cos(q) * 56), (x + sin(q) * 36 + 12, y - cos(q) * 30)]), (250, 150, 180), 3)
WEAPONS = dict(bow=bow, gada=rig.gada, khadga=rig.khadga, trishul=trishul, danda=danda, kamandal=kamandal, lotus=lotus)

BULK = dict(thin=.86, normal=.98, strong=1.12, huge=1.34)


def make(sp):
    """Design -> character dict for rig.body()."""
    k, sex = sp.get("kind", "human"), sp.get("sex", "m")
    sk = _c(sp.get("skin"), SKIN["vanar"] if k == "vanar" else SKIN["wheat"]); cl = _c(sp.get("cloth"), (240, 140, 50)); eg = _c(sp.get("edge"), GOLD)
    p = dict(skin=sk, cloth=cl, edge=eg, jewel=_c(sp.get("jewel"), (220, 40, 60)), bulk=BULK.get(sp.get("build", "normal"), .98) * (.78 if sex == "f" else 1),
             hs=.98 * (.94 if sex == "f" else 1), tail=k == "vanar", skirt=sp.get("lower") == "saree", long=sp.get("lower") in ("long", "saree", "bark"),
             weapon=WEAPONS.get(sp.get("weapon")), size=sp.get("size", 1.0), spec=sp, name=sp.get("name", "?"))
    p["head_fn"] = many_heads(make_head(sp), sp.get("heads", 1)); p["head"] = "_f_" + p["name"]; rig.HEADS[p["head"]] = p["head_fn"]
    tp = sp.get("top", "bare"); p["top"] = top_fn(tp, cl, eg); p["sash"] = tp in ("bare", "uttariya")
    if sp.get("lower") == "bark": p["cloth"] = (150, 110, 70)
    if sex == "f": p["necklace"] = ((eg, 7), (p["jewel"], 5))
    return p


# ---------------- similarity and automatic extras
FIELDS = ["kind", "sex", "age", "build", "hair", "beard", "crown", "tilak", "eyes", "top", "lower", "weapon"]
def distance(a, b):
    d = sum(a.get(f) != b.get(f) for f in FIELDS)
    for f in ("skin", "cloth", "edge"):
        x, y = _c(a.get(f), (0, 0, 0)), _c(b.get(f), (0, 0, 0)); d += min(1.5, math.dist(x, y) / 120)
    return d
POOL = dict(
    rishi=dict(kind=["human"], age=["old", "adult"], build=["thin", "normal"], hair=["jata", "tuft"], beard=["long", "short"], crown=["none"], tilak=["tripund", "u", "dot"], eyes=["wise", "kind", "calm"], top=["robe", "bark", "uttariya"], lower=["long", "bark"], weapon=["kamandal", "danda", "none"], skin=["wheat", "brown", "fair"], hair_rgb=[(236, 232, 222), (200, 196, 190), (60, 44, 40)], cloth=[(232, 120, 40), (240, 200, 60), (226, 90, 40), (240, 236, 220)]),
    sainik=dict(kind=["human"], age=["young", "adult"], build=["normal", "strong"], hair=["short", "long"], beard=["moustache", "stubble", "none"], crown=["helmet", "turban"], tilak=["dot", "none", "u"], eyes=["calm", "fierce"], top=["kavach", "uttariya"], lower=["dhoti"], weapon=["khadga", "bow", "danda"], skin=["wheat", "brown", "fair"], cloth=[(200, 60, 50), (60, 110, 180), (230, 170, 50), (90, 140, 80)]),
    rakshas=dict(kind=["rakshas"], age=["adult"], build=["strong", "huge"], hair=["wild", "long"], beard=["curled", "moustache", "short"], crown=["rakshas", "helmet", "none"], tilak=["tripund", "none"], eyes=["fierce"], top=["kavach", "bare"], lower=["dhoti"], weapon=["khadga", "trishul", "gada"], skin=["dark", "green", "maroon", "ash"], cloth=[(60, 34, 70), (120, 30, 40), (40, 60, 50)], tusks=[True, False]),
    vanar=dict(kind=["vanar"], age=["young", "adult"], build=["normal", "strong"], crown=["none", "vanar"], tilak=["u", "none"], eyes=["calm", "fierce", "kind"], top=["bare"], lower=["dhoti"], weapon=["gada", "danda", "none"], skin=[(238, 150, 90), (220, 170, 110), (200, 120, 80)], fur=[(150, 90, 50), (120, 90, 70), (190, 120, 60), (100, 70, 60)], cloth=[(200, 60, 50), (60, 130, 120), (230, 160, 50)]))
def auto(kind, seed, cast, name=None, need=5.0):
    """New minor character of a kind, at least `need` away from everyone in the cast (it keeps trying other seeds)."""
    for tr in range(60):
        r = random.Random(f"{kind}-{seed}-{tr}"); sp = {k: r.choice(v) for k, v in POOL[kind].items()}; sp["name"] = name or f"{kind} {seed}"; sp["edge"] = r.choice([GOLD, (240, 230, 210), (200, 200, 210)])
        if all(distance(sp, o) >= need for o in cast): return sp
    return sp


def load(path=os.path.join(ROOT, "cast", "ramayan.json")): return json.load(open(path, encoding="utf-8"))


# ---------------- test sheet
def figure(p, ps, s, t=1.3):
    """The character alone, cut to its own size (feet at the bottom edge)."""
    G = 2400; sf = skia.Surface(G, G); q = sf.getCanvas(); v = rig.pose(ps, x=G / 2); rig.body(q, p, v, G * .8, s, 1, t, weapon=True)
    im = sf.makeImageSnapshot(); a = im.toarray()[:, :, 3]; ys, xs = (a > 8).nonzero(); top, left, right = ys.min(), xs.min(), xs.max(); bot = int(G * .8 + 30 * s)
    return im.makeSubset(skia.IRect.MakeLTRB(int(left) - 4, int(top) - 4, int(right) + 4, bot))
def card(c, x0, y0, w, h, blue=False):
    bg = (232, 240, 250) if blue else (255, 246, 228); c.drawRect(skia.Rect.MakeXYWH(x0, y0, w, h), fill((236, 200, 140)))
    c.drawRect(skia.Rect.MakeXYWH(x0 + 12, y0 + 12, w - 24, h - 24), skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeRadial(skia.Point(x0 + w / 2, y0 + h * .42), h * .7, [col((255, 255, 250)), col(bg), col(mix(bg, (214, 160, 90), .35))], [0, .55, 1])))
    for q, a in ((28, 4), (40, 2)): c.drawRect(skia.Rect.MakeXYWH(x0 + q, y0 + q, w - 2 * q, h - 2 * q), line((210, 150, 60), a))
    for cx, cy, sx, sy in ((x0 + 28, y0 + 28, 1, 1), (x0 + w - 28, y0 + 28, -1, 1), (x0 + 28, y0 + h - 28, 1, -1), (x0 + w - 28, y0 + h - 28, -1, -1)):
        q = smooth([(cx, cy), (cx + sx * 70, cy + sy * 6), (cx + sx * 40, cy + sy * 20), (cx + sx * 20, cy + sy * 40), (cx + sx * 6, cy + sy * 70)]); c.drawPath(q, fill((226, 170, 70))); c.drawPath(q, line((170, 110, 40), 3)); c.drawCircle(cx + sx * 22, cy + sy * 22, 7, fill((200, 60, 50)))


if __name__ == "__main__":
    from PIL import Image
    cast = load(); extra = [auto(k, 1, cast, n) for k, n in (("rishi", "Rishi (auto)"), ("sainik", "Sainik (auto)"), ("rakshas", "Rakshas (auto)"), ("vanar", "Vanar (auto)"))]
    rig.SOFT = "flat" not in sys.argv
    people = cast + extra; CW, CH, cols = 700, 1000, 4; rows = (len(people) + cols - 1) // cols
    s = skia.Surface(CW * cols, CH * rows); c = s.getCanvas()
    c.drawPaint(skia.Paint(Shader=skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, CH * rows)], [col((250, 236, 210)), col((236, 210, 180))])))
    font = skia.Font(skia.Typeface.MakeFromFile(os.path.join(ROOT, "fonts", "Poppins-Bold.ttf")), 40)
    for i, sp in enumerate(people):
        x0, y0 = (i % cols) * CW, (i // cols) * CH; c.save(); c.clipRect(skia.Rect.MakeXYWH(x0, y0, CW, CH))
        card(c, x0, y0, CW, CH, i >= len(cast))
        p = make(sp); fig = figure(p, sp.get("pose", "stand"), .9 * p["size"]); bw, bh = CW - 110, CH - 190; k = min(1., bw / fig.width(), bh / fig.height())
        c.drawImageRect(fig, skia.Rect.MakeXYWH(x0 + (CW - fig.width() * k) / 2, y0 + CH - 110 - fig.height() * k, fig.width() * k, fig.height() * k), skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear))
        w = font.measureText(sp["name"]); rb = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x0 + (CW - w) / 2 - 50, y0 + CH - 92, w + 100, 70), 35, 35); c.drawRRect(rb, fill((255, 246, 222))); c.drawRRect(rb, line((200, 140, 50), 5)); c.drawString(sp["name"], x0 + (CW - w) / 2, y0 + CH - 42, font, fill((60, 30, 40))); c.restore()
    out = os.path.join(ROOT, "out", "cast_sheet.jpg"); Image.fromarray(s.toarray(colorType=skia.kRGBA_8888_ColorType)).convert("RGB").save(out, quality=90); print(out)
