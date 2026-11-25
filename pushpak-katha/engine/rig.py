"""Action rig: keyframed bodies with planted feet, weight, weapon trails and hit-stop.

A pose is a dict over BASE. Angles are degrees, 0 = hanging down, 90 = forward, 180 = up. h = hip height, hx = hip ahead of the feet,
f1/f2 = feet (forward, lift) relative to x, x = world place, j = height of a jump, rot = whole body roll."""
import math, random
import numpy as np, skia
from math import sin, cos, pi, radians as rad
from lab import W, H, col, mix, fill, line, vgrad, glow, poly, smooth, oval

INK = (38, 18, 30)
BASE = dict(x=0., h=282., hx=0., lean=4., head=0., a1u=20., a1f=50., a2u=-12., a2f=14., gr=80., f1x=48., f1y=0., f2x=-52., f2y=0., rot=0., j=0., sq=0.)
def P(**k): return dict(BASE, **k)
POSE = dict(
    stand=P(), guard=P(h=258, lean=9, a1u=38, a1f=112, a2u=25, a2f=105, gr=70, f1x=84, f2x=-96),
    run=P(h=262, lean=24, a1u=-20, a1f=40, a2u=40, a2f=110, f1x=120, f2x=-130, gr=110),
    wind=P(h=238, hx=-46, lean=-16, head=8, a1u=200, a1f=232, gr=34, a2u=66, a2f=98, f1x=70, f2x=-120),
    strike=P(h=232, hx=54, lean=30, head=-12, a1u=84, a1f=78, gr=16, a2u=-40, a2f=-10, f1x=150, f2x=-128),
    follow=P(h=236, hx=58, lean=38, head=-14, a1u=34, a1f=10, gr=0, a2u=-50, a2f=-20, f1x=150, f2x=-126),
    block=P(h=246, hx=-30, lean=-8, a1u=112, a1f=160, gr=-70, a2u=100, a2f=140, f1x=80, f2x=-116),
    duck=P(h=150, hx=10, lean=52, head=-24, a1u=-30, a1f=30, gr=60, a2u=30, a2f=100, f1x=126, f2x=-120),
    punchw=P(h=200, hx=-20, lean=14, a1u=-30, a1f=40, gr=60, a2u=-60, a2f=30, f1x=110, f2x=-110),
    punch=P(h=268, hx=60, lean=14, head=10, a1u=-40, a1f=10, gr=60, a2u=120, a2f=135, f1x=130, f2x=-110),
    hit=P(h=254, hx=-60, lean=-34, head=-26, a1u=-50, a1f=-20, gr=60, a2u=112, a2f=130, f1x=66, f2x=-120),
    stagger=P(h=240, hx=-20, lean=20, head=20, a1u=10, a1f=30, gr=60, a2u=0, a2f=30, f1x=100, f2x=-110),
    roar=P(h=252, lean=-10, head=-16, a1u=-70, a1f=-110, gr=60, a2u=-60, a2f=-100, f1x=110, f2x=-110),
    crouch=P(h=176, hx=-6, lean=34, a1u=-60, a1f=-30, gr=70, a2u=-50, a2f=-20, f1x=90, f2x=-90),
    leap=P(h=270, lean=10, a1u=205, a1f=220, gr=40, a2u=70, a2f=100, f1x=60, f1y=110, f2x=-70, f2y=40, j=250),
    tuck=P(h=220, lean=40, a1u=40, a1f=120, gr=90, a2u=40, a2f=120, f1x=40, f1y=130, f2x=10, f2y=120, j=330),
    land=P(h=170, hx=30, lean=34, head=-10, a1u=70, a1f=40, gr=20, a2u=-60, a2f=-30, f1x=140, f2x=-130),
    down=P(h=64, lean=0, rot=-86, head=-10, a1u=60, a1f=80, gr=70, a2u=-30, a2f=10, f1x=50, f1y=10, f2x=30, f2y=0),
    hero=P(h=280, lean=-4, head=-4, a1u=52, a1f=98, gr=80, a2u=-40, a2f=60, f1x=86, f2x=-90),
    namaste=P(lean=10, head=14, a1u=42, a1f=140, a2u=38, a2f=138, f1x=24, f2x=-26), talk=P(a1u=50, a1f=120), point=P(a1u=82, a1f=92, lean=8),
    kneel=P(h=150, lean=14, head=20, a1u=30, a1f=80, a2u=30, a2f=80, f1x=110, f2x=-150), swim=P(h=230, lean=0, rot=62, a1u=150, a1f=170, a2u=60, a2f=90, f1x=0, f1y=-40, f2x=-60, f2y=10),
    fly=P(h=290, rot=66, lean=8, head=-46, a1u=176, a1f=180, gr=90, a2u=-20, a2f=-30, f1x=6, f1y=-8, f2x=-46, f2y=34))
def pose(n, **k): return dict(POSE[n], **k)

E = dict(io=lambda u: u * u * (3 - 2 * u), out=lambda u: 1 - (1 - u) ** 3, inn=lambda u: u * u * u, lin=lambda u: u, back=lambda u: 1 + 2.7 * (u - 1) ** 3 + 1.7 * (u - 1) ** 2, hit=lambda u: u ** 2.2)
def anim(keys, t):
    """keys: [(time, pose, ease into it)]. Feet travel in the world one after the other, so a planted foot stays where it is."""
    i = 0
    while i + 1 < len(keys) and keys[i + 1][0] <= t: i += 1
    if i + 1 >= len(keys): return dict(keys[-1][1])
    (t0, a, _), (t1, b, e) = keys[i][:3], keys[i + 1][:3]; u = max(0., min(1., (t - t0) / max(1e-6, t1 - t0))); v = E[e](u); o = {k: a[k] + (b[k] - a[k]) * v for k in BASE}
    air = max(a["j"], b["j"]) > 30; d = keys[i + 1][3] if len(keys[i + 1]) > 3 else 1
    if air and a["j"] != b["j"]: w = E["out"](u) if b["j"] > a["j"] else E["inn"](u) ** .7; o["j"] = a["j"] + (b["j"] - a["j"]) * w
    for n, lag in (("f1", (0., .75)), ("f2", (.25, 1.))):
        if air: continue
        wa, wb = a["x"] + FD(keys) * a[n + "x"], b["x"] + FD(keys) * b[n + "x"]; q = E["io"](max(0., min(1., (u - lag[0]) / (lag[1] - lag[0])))); o[n + "x"] = (wa + (wb - wa) * q - o["x"]) * FD(keys); o[n + "y"] += sin(pi * q) * min(52., abs(wb - wa) * .28)
    return o
class Keys(list):
    """Keyframes of one fighter: d is the way they face, s their scale."""
    def __init__(self, d, s, ks): super().__init__(ks); self.d, self.s = d, s
def FD(k): return getattr(k, "d", 1) * getattr(k, "s", 1.)

def rotp(p, c, a): s, q = sin(rad(a)), cos(rad(a)); return (c[0] + (p[0] - c[0]) * q - (p[1] - c[1]) * s, c[1] + (p[0] - c[0]) * s + (p[1] - c[1]) * q)
def end(p, a, l): return (p[0] + sin(rad(a)) * l, p[1] + cos(rad(a)) * l)
def solve(v, bulk=1.):
    """Joint places, feet line at y = 0, facing +x."""
    h = v["h"] + v["j"]; hip = (v["hx"], -h); neck = end(hip, 180 - v["lean"], 218); sh = end(hip, 180 - v["lean"], 190); J = dict(hip=hip, neck=neck, sh=sh)
    for n in ("a1", "a2"): off = 34 * bulk if n == "a1" else -30 * bulk; s0 = (sh[0] + off * .55, sh[1] + 6); e = end(s0, v[n + "u"], 112); J[n] = (s0, e, end(e, v[n + "f"], 106))
    for n, o in (("f1", 24), ("f2", -24)):
        hp = (hip[0] + o * bulk, hip[1] + 8); f = (v[n + "x"], -v[n + "y"] - v["j"] - 16); dx, dy = f[0] - hp[0], f[1] - hp[1]; D = math.hypot(dx, dy) or 1; l = max(133., D / 2 + .5); b = math.sqrt(max(0., l * l - D * D / 4)); k = ((hp[0] + f[0]) / 2 + b * dy / D, (hp[1] + f[1]) / 2 - b * dx / D); J[n] = (hp, k, f)
    J["tip"] = end(J["a1"][2], v["a1f"] + v["gr"], 250); J["rot"] = v["rot"]
    if v["rot"]: J = {k: (rotp(q, hip, v["rot"]) if k in ("neck", "sh", "tip") else tuple(rotp(z, hip, v["rot"]) for z in q) if k in ("a1", "a2", "f1", "f2") else q) for k, q in J.items()}
    return J
def world(p, v, y, s, d): return (v["x"] + p[0] * s * d, y + p[1] * s)

# ---------------- pieces
def shape(c, path, rgb, w=6, sh=.26, off=(-9, -10)):
    c.save(); c.clipPath(path, True); c.drawPaint(fill(mix(rgb, (50, 10, 70), sh))); c.translate(*off); c.drawPath(path, fill(rgb)); c.restore(); c.drawPath(path, line(INK, w))
def cap(a, b, w0, w1):
    dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy) or 1; nx, ny = -dy / L, dx / L; m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2); mw = (w0 + w1) / 2 * 1.1
    q = skia.Path(); q.moveTo(a[0] + nx * w0, a[1] + ny * w0); q.quadTo(m[0] + nx * mw, m[1] + ny * mw, b[0] + nx * w1, b[1] + ny * w1); q.lineTo(b[0] - nx * w1, b[1] - ny * w1); q.quadTo(m[0] - nx * mw, m[1] - ny * mw, a[0] - nx * w0, a[1] - ny * w0); q.close()
    return skia.Op(skia.Op(q, oval(*a, w0), skia.kUnion_PathOp), oval(*b, w1), skia.kUnion_PathOp)
def limb2(a, b, e, w): return skia.Op(cap(a, b, w[0], w[1]), cap(b, e, w[1], w[2]), skia.kUnion_PathOp)

def gada(c, a, b, gold=(246, 186, 60)):
    c.drawPath(cap(a, b, 9, 11), line(INK, 10)); c.drawPath(cap(a, b, 9, 11), fill(gold)); dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy) or 1; u = (dx / L, dy / L)
    shape(c, oval(b[0], b[1], 52), gold, 7); [c.drawCircle(b[0] + cos(k * pi / 3 + .4) * 32, b[1] + sin(k * pi / 3 + .4) * 32, 8, fill((200, 60, 40))) for k in range(6)]; shape(c, oval(b[0] + u[0] * 60, b[1] + u[1] * 60, 17), gold, 5)
def khadga(c, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy) or 1; u, n = (dx / L, dy / L), (-dy / L, dx / L); pt = lambda q, w: (a[0] + u[0] * q + n[0] * w, a[1] + u[1] * q + n[1] * w)
    shape(c, smooth([pt(10, -10), pt(140, -22), pt(230, -44), pt(275, -20), pt(240, 18), pt(120, 14), pt(10, 12)]), (196, 206, 218)); shape(c, poly([pt(-4, -36), pt(16, -36), pt(16, 36), pt(-4, 36)]), (200, 150, 50), 5); c.drawLine(*pt(0, 0), *pt(-44, 0), line(INK, 20)); c.drawLine(*pt(0, 0), *pt(-44, 0), line((120, 60, 40), 11))
def trail(c, pts, rgb, w=60):
    """Smear behind a fast weapon. pts: newest first, (tip, grip)."""
    for i in range(len(pts) - 1):
        (a, g), (b, k) = pts[i], pts[i + 1]; f = 1 - i / (len(pts) - 1)
        if math.hypot(a[0] - b[0], a[1] - b[1]) < 7: continue
        ia, ib = (a[0] + (g[0] - a[0]) * .5, a[1] + (g[1] - a[1]) * .5), (b[0] + (k[0] - b[0]) * .5, b[1] + (k[1] - b[1]) * .5); c.drawPath(poly([a, b, ib, ia]), fill(rgb, .62 * f * f))
def tailpath(p, w0=15, w1=7):
    """Tapered tail along points, outlined."""
    q = smooth(p, False); c = q; return c
def draw_tail(c, pts, rgb, w=26):
    q = smooth(pts, False); c.drawPath(q, line(INK, w + 12)); c.drawPath(q, line(rgb, w)); c.drawPath(q, line(mix(rgb, (255, 240, 200), .35), w * .25)); x, y = pts[-1]; shape(c, smooth([(x - 26, y - 22), (x + 20, y - 34), (x + 34, y + 6), (x + 6, y + 30), (x - 28, y + 20)]), mix(rgb, (120, 40, 10), .35), 6)

# ---------------- heads, neck at (0, 0), looking right
def eye(c, x, y, rx, ry, look=.25, lid=0., iris=(50, 24, 20), brow=0., w=9, bc=INK):
    q = oval(x, y, rx, ry); c.save(); c.clipPath(q, True); c.drawPaint(fill((255, 252, 244))); c.drawCircle(x + rx * look, y + 2, ry * .64, fill(iris)); c.drawCircle(x + rx * look + 5, y - 5, ry * .2, fill((255, 255, 255)))
    if lid > 0: c.drawRect(skia.Rect.MakeLTRB(x - rx, y - ry, x + rx, y - ry + 2 * ry * lid), fill((190, 96, 50)))
    c.restore(); c.drawPath(q, line(INK, 5)); c.drawPath(smooth([(x - rx * 1.2, y - ry - 12 - brow * 10), (x, y - ry - 24), (x + rx * 1.2, y - ry - 12 + brow * 14)], False), line(bc, w))
def blink(t): k = abs((t % 2.9) - .1) / .1; return max(0., 1 - k)
def h_hanuman(c, t, talk, mood, p):
    sk, fur, g = (238, 128, 66), (190, 78, 34), (250, 196, 66)
    shape(c, smooth([(-70, 6), (-98, -70), (-86, -150), (-10, -186), (66, -160), (84, -90), (60, 0), (0, 24)]), fur); shape(c, oval(-62, -84, 25, 30), sk, 5); c.drawCircle(-62, -50, 11, fill(g)); c.drawCircle(-62, -50, 11, line(INK, 4))
    shape(c, smooth([(-40, -20), (-46, -90), (-34, -140), (20, -150), (74, -138), (82, -90), (74, -40), (30, 0)]), sk, 5)
    m = talk * 22 + (12 if mood == "roar" else 0); shape(c, smooth([(-16, -30), (-6, -64), (40, -72), (92, -66), (112, -42), (100, -10 + m * .5), (50, 10 + m), (0, 0 + m * .4)]), (255, 190, 130), 5); c.drawPath(smooth([(70, -72), (100, -74), (104, -58), (84, -54)]), fill((120, 40, 30)))
    if m > 3 or mood == "roar": q = smooth([(16, -24), (60, -30), (96, -28), (86, -8 + m * .5), (48, 0 + m * .8), (20, -10 + m * .3)]); c.drawPath(q, fill((120, 20, 30))); c.save(); c.clipPath(q, True); c.drawRect(skia.Rect.MakeLTRB(10, -34, 110, -22), fill((255, 255, 255))); c.restore(); c.drawPath(q, line(INK, 4))
    else: c.drawPath(smooth([(18, -26), (56, -14 if mood != "angry" else -30), (98, -28)], False), line(INK, 5))
    b = dict(angry=1, roar=1, sad=-1).get(mood, 0); l = blink(t); eye(c, 8, -100, 19, 22, lid=l, brow=b); eye(c, 58, -100, 17, 21, lid=l, brow=b)
    c.drawPath(smooth([(26, -142), (34, -112), (42, -142)], False), line((214, 30, 40), 7)); c.drawLine(33, -140, 33, -118, line((255, 230, 120), 5))
    shape(c, poly([(-78, -146), (-70, -196), (-44, -174), (-18, -236), (8, -190), (34, -250), (54, -188), (82, -206), (88, -146)]), g); shape(c, poly([(-84, -164), (92, -162), (88, -134), (-80, -136)]), (220, 60, 40), 5); [c.drawCircle(-56 + i * 30, -149, 7, fill([(255, 240, 160), (40, 150, 160)][i % 2])) for i in range(5)]; c.drawCircle(32, -206, 11, fill((220, 40, 60)))
def h_demon(c, t, talk, mood, p):
    sk = p["skin"]; hair = (34, 22, 34)
    shape(c, smooth([(20, -190), (-60, -210), (-120, -150), (-96, -110), (-136, -60), (-92, -30), (-110, 30), (-40, 10), (20, -60)]), hair);
    for q in (-40, 50): shape(c, smooth([(q - 18, -158), (q - 30, -220), (q - 4, -262), (q + 12, -210), (q + 18, -158)]), (232, 216, 176), 6)
    m = talk * 26 + (20 if mood in ("roar", "shock") else 0); shape(c, smooth([(-62, -20), (-74, -100), (-46, -164), (20, -176), (78, -156), (88, -100), (94, -50), (78, 10 + m * .7), (20, 22 + m), (-34, 8 + m * .4)]), sk); shape(c, smooth([(-76, -110), (-128, -140), (-100, -84), (-66, -72)]), sk, 5); c.drawCircle(-90, -70, 13, line((240, 190, 60), 7))
    shape(c, smooth([(60, -96), (108, -70), (104, -50), (62, -52)]), mix(sk, (200, 60, 60), .25), 5); c.drawCircle(96, -54, 10, line((240, 190, 60), 5))
    q = smooth([(-8, -24), (40, -36), (86, -30), (80, -4 + m * .7), (40, 4 + m), (2, -8 + m * .5)]); c.drawPath(q, fill((110, 14, 26))); c.drawPath(q, line(INK, 5))
    for x, d in ((14, -1), (70, -1)): c.drawPath(poly([(x - 9, -14 + m * .5), (x + 9, -16 + m * .5), (x, -44)]), fill((255, 250, 230))); c.drawPath(poly([(x - 9, -14 + m * .5), (x + 9, -16 + m * .5), (x, -44)]), line(INK, 3))
    c.drawPath(smooth([(92, -46), (40, -58), (0, -40), (-30, 4), (-50, -20)], False), line(hair, 18))
    b = -1 if mood == "shock" else 1; eye(c, 0, -104, 20, 18 + (6 if mood == "shock" else 0), iris=(200, 30, 20), brow=b, w=15); eye(c, 56, -106, 18, 17 + (6 if mood == "shock" else 0), iris=(200, 30, 20), brow=b, w=15); c.drawPath(smooth([(24, -164), (30, -128), (36, -164)]), fill((220, 30, 40)))
def human(c, t, talk, mood, sk, hair, beard=None, long=True, lash=False, lid=0.):
    if long: shape(c, smooth([(-40, -170), (-88, -110), (-90, 10), (-76, 70), (-30, 60), (-10, -60)]), hair)
    m = talk * 16; shape(c, smooth([(-58, -30), (-66, -100), (-44, -150), (14, -164), (66, -148), (76, -100), (72, -44), (44, 0 + m), (6, 6 + m), (-34, -6)]), sk)
    if beard: shape(c, smooth([(-46, -60), (-20, -44), (20, -34), (70, -46), (84, -20 + m), (62, 90 + m), (24, 160 + m), (-14, 90), (-50, 0)]), beard, 5)
    c.drawPath(smooth([(60, -96), (80, -66), (62, -60)], False), line(mix(sk, (90, 20, 30), .5), 6)); q = smooth([(22, -36), (46, -38), (64, -36), (46, -26 + m)]); c.drawPath(q, fill((150, 30, 50)));
    if not m: c.drawPath(smooth([(22, -34), (44, -28 if mood != "sad" else -40), (66, -36)], False), line((130, 26, 44), 5))
    l = max(lid, blink(t)); b = dict(sad=-1, angry=1).get(mood, 0)
    for x, r in ((10, 16), (52, 14)):
        q = oval(x, -92, r, 13); c.save(); c.clipPath(q, True); c.drawPaint(fill((255, 252, 246))); c.drawCircle(x + 4, -92, 9, fill((40, 20, 24))); c.drawCircle(x + 7, -95, 3, fill((255, 255, 255))); (l > 0) and c.drawRect(skia.Rect.MakeLTRB(x - r, -106, x + r, -106 + 26 * l), fill(sk)); c.restore(); c.drawPath(smooth([(x - r * 1.2, -92), (x, -107), (x + r * 1.3, -92)], False) if l < .6 else smooth([(x - r * 1.2, -88), (x, -80), (x + r * 1.2, -88)], False), line(INK, 6)); c.drawPath(smooth([(x - 18, -118 - b * 6), (x, -126), (x + 18, -118 + b * 7)], False), line(beard or hair, 7))
    shape(c, oval(-44, -82, 14, 20), sk, 4)
def h_muni(c, t, talk, mood, p):
    human(c, t, talk, mood, p["skin"], (226, 220, 208), (238, 234, 224)); shape(c, smooth([(-70, -96), (-64, -160), (10, -190), (74, -160), (72, -130), (10, -150), (-40, -130)]), (226, 220, 208)); shape(c, smooth([(-34, -176), (-30, -236), (10, -262), (44, -226), (36, -176)]), (226, 220, 208)); c.drawLine(-26, -184, 34, -184, line((190, 90, 40), 15)); [c.drawLine(6, -142 + k * 10, 62, -140 + k * 10, line((250, 240, 220), 5)) for k in range(2)]
def h_prince(c, t, talk, mood, p):
    human(c, t, talk, mood, p["skin"], (30, 20, 34), lid=p.get("lid", 0)); g = (250, 200, 70); shape(c, smooth([(-64, -110), (-60, -164), (10, -186), (72, -160), (74, -130), (20, -150), (-30, -130)]), (30, 20, 34)); shape(c, poly([(-66, -134), (74, -138), (72, -164), (50, -180), (30, -230), (6, -182), (-22, -210), (-40, -172), (-66, -164)]), g, 6); c.drawCircle(22, -158, 9, fill((220, 40, 60))); c.drawLine(38, -140, 38, -112, line((250, 210, 60), 6)); c.drawCircle(-44, -54, 9, fill(g))
def h_apsara(c, t, talk, mood, p):
    human(c, t, talk, mood, p["skin"], (40, 20, 40)); shape(c, smooth([(-66, -90), (-60, -164), (10, -190), (70, -160), (72, -128), (20, -154), (-30, -120)]), (40, 20, 40)); g = (255, 214, 100); c.drawPath(smooth([(72, -140), (10, -166), (-56, -130)], False), line(g, 9)); c.drawCircle(50, -138, 9, fill((220, 30, 60))); c.drawCircle(-44, -54, 14, line(g, 6)); [c.drawCircle(-70 + sin(i) * 12, -150 + i * 34, 13, fill((255, 240, 250))) for i in range(6)]
HEADS = dict(hanuman=h_hanuman, demon=h_demon, muni=h_muni, prince=h_prince, apsara=h_apsara)
CAST = dict(
    hanuman=dict(head="hanuman", skin=(238, 128, 66), cloth=(214, 40, 44), edge=(250, 200, 70), bulk=1.12, weapon=gada, tail=True, hs=1.04),
    demon=dict(head="demon", skin=(96, 122, 96), cloth=(60, 34, 70), edge=(214, 150, 50), bulk=1.34, weapon=khadga, hs=1.0),
    muni=dict(head="muni", skin=(212, 160, 112), cloth=(232, 120, 40), edge=(250, 210, 120), bulk=.9, hs=.95),
    ram=dict(head="prince", skin=(96, 158, 214), cloth=(250, 190, 50), edge=(220, 60, 50), bulk=.98, hs=.98), laksh=dict(head="prince", skin=(236, 190, 146), cloth=(240, 130, 50), edge=(250, 220, 120), bulk=.96, hs=.98),
    apsara=dict(head="apsara", skin=(244, 200, 168), cloth=(220, 70, 140), edge=(255, 220, 120), bulk=.74, hs=.92, skirt=True))

def body(c, who, v, y, s=1., d=1, t=0., talk=0., mood="n", past=None, weapon=True, tail=None, shadow=True):
    """Draw one person in pose v with the ground at y. past(k) gives the pose k seconds ago, for tail, cloth and weapon trail."""
    p = CAST[who] if isinstance(who, str) else who; B = p["bulk"]; J = solve(v, B); sk, cl, eg = p["skin"], p["cloth"], p["edge"]; old = past(.09) if past else v; far = mix(sk, (50, 10, 70), .28)
    vx = (v["x"] - old["x"]) * d / s; vy = v["j"] - old["j"]
    if shadow: k = 1 / (1 + v["j"] / 260); c.drawOval(skia.Rect.MakeLTRB(v["x"] - 190 * s * k, y - 22 * s * k, v["x"] + 190 * s * k, y + 26 * s * k), fill((0, 0, 0), .42 * k, 14))
    if weapon and p.get("weapon") and past:
        ps = []
        for i in range(9): q = past(i * .011); jj = solve(q, B); ps.append((world(jj["tip"], q, y, s, d), world(jj["a1"][2], q, y, s, d)))
        trail(c, ps, (255, 236, 170) if who == "hanuman" else (200, 190, 255))
    c.save(); c.translate(v["x"], y); c.scale(s * d, s); R = v["rot"]; hip = J["hip"]
    def local(pts): return [rotp((hip[0] + a, hip[1] + b), hip, R) for a, b in pts]
    if p.get("tail") and tail is None:
        w = sin(t * 2.2) * 22; g = max(-120, min(120, -vx * 1.1)); u = max(-90, min(90, -vy * .5)); draw_tail(c, local([(-30, 10), (-90 + g * .2, 30 - u * .2), (-160 + g * .5, -30 + w * .4 - u * .4), (-180 + g * .7, -150 + w - u * .7), (-120 + g * .9 + w, -250 - u), (-60 + g + w, -290 - u), (-30 + g + w * 1.4, -240 - u)]), mix(sk, (190, 78, 34), .5))
    s2, e2, h2 = J["a2"]; shape(c, limb2(s2, e2, h2, (33 * B, 25 * B, 19 * B)), far); shape(c, oval(h2[0], h2[1], 25 * B), far, 5); c.drawPath(cap(end(h2, 0, 0), e2, 4, 4), fill(far, 0))
    hp, k, f = J["f2"]; shape(c, limb2(hp, k, f, (46 * B, 33 * B, 22 * B)), far); foot(c, k, f, far, R, B, eg)
    # hanging cloth behind, lagging
    for q, r in ((-1, cl),): shape(c, smooth(local([(-40, -20), (-70 - vx * .25, 60), (-64 - vx * .6, 150 + vy * .2), (-20 - vx * .5, 150 + vy * .2), (0, 0)])), mix(r, (40, 0, 60), .3))
    hp, k, f = J["f1"]; shape(c, limb2(hp, k, f, (48 * B, 35 * B, 23 * B)), sk); foot(c, k, f, sk, R, B, eg)
    nk, hi = J["neck"], hip; L = R + v["lean"]
    def tor(pts): return [rotp((hi[0] + a * B, hi[1] + b), hi, L) for a, b in pts]
    shape(c, smooth(tor([(-58, 10), (-56, -60), (-88, -150), (-70, -206), (0, -224), (66, -208), (92, -156), (64, -70), (58, 10)])), sk, 6, off=(-12, -8))
    if B > 1: c.drawPath(smooth(tor([(-30, -128), (10, -116), (62, -134)]), False), line(mix(sk, INK, .4), 5)); c.drawPath(smooth(tor([(14, -190), (18, -150), (12, -116)]), False), line(mix(sk, INK, .4), 5)); [c.drawPath(smooth(tor([(-14, -92 + i * 30), (16, -86 + i * 30), (40, -94 + i * 30)]), False), line(mix(sk, INK, .3), 4)) for i in range(2)]
    if p.get("skirt"): shape(c, smooth(tor([(-62, -60), (-80, -206), (0, -216), (70, -206), (62, -60)])), cl)
    c.drawPath(smooth(tor([(-60, -196), (-10, -110), (54, -20)]), False), line(INK, 30)); c.drawPath(smooth(tor([(-60, -196), (-10, -110), (54, -20)]), False), line(eg, 20))
    # dhoti over the thighs
    k1, k2 = J["f1"][1], J["f2"][1]; mx = lambda a, b, u: (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u); W0 = tor([(-64, -24), (64, -24)]); u = .78 if not p.get("skirt") and who != "muni" else 1.0
    a, b = mx(J["f1"][0], k1, u), mx(J["f2"][0], k2, u)
    if u == 1.0: a, b = (J["f1"][2][0] + 44, J["f1"][2][1] - 22), (J["f2"][2][0] - 40, J["f2"][2][1] - 22)
    dh = poly([W0[0], W0[1], (max(a[0], b[0]) + 52 * B, a[1] if a[0] > b[0] else b[1]), (a[0] if a[0] > b[0] else b[0], (a[1] if a[0] > b[0] else b[1]) + 34), ((a[0] + b[0]) / 2, min(a[1], b[1]) - (10 if u < 1 else -20)), (a[0] if a[0] < b[0] else b[0], (a[1] if a[0] < b[0] else b[1]) + 34), (min(a[0], b[0]) - 52 * B, a[1] if a[0] < b[0] else b[1])]); pe = skia.Paint(Color=col(cl), AntiAlias=True, PathEffect=skia.CornerPathEffect.Make(34)); c.drawPath(dh, skia.Paint(Color=col(INK), AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=12, PathEffect=skia.CornerPathEffect.Make(34))); c.drawPath(dh, pe)
    c.save(); c.clipPath(dh, True)
    for q in range(4): m0 = mx(W0[0], W0[1], .2 + q * .2); m1 = mx(b, a, .05 + q * .3); c.drawLine(*m0, *m1, line(mix(cl, INK, .35), 5))
    for z, o in ((a, 1), (b, 1)): c.drawCircle(z[0], z[1] + 46, 46, line(eg, 13))
    c.restore()
    shape(c, smooth(tor([(-70, -36), (0, -44), (70, -36), (70, 2), (0, 10), (-70, 2)])), eg, 5); bl = tor([(0, -18)])[0]; shape(c, oval(bl[0], bl[1], 17), (200, 40, 50), 4)
    ss = tor([(30, 0)])[0]; shape(c, smooth([ss, (ss[0] + 40, ss[1] + 20), (ss[0] + 30 - vx * .4, ss[1] + 120 + vy * .2), (ss[0] - vx * .5, ss[1] + 130 + vy * .2)]), eg, 5)
    # head
    c.save(); c.translate(*nk); c.rotate(R + v["lean"] * .5 + v["head"] * -1 if False else R + v["lean"] * .5 + v["head"]); c.scale(p["hs"], p["hs"]); shape(c, poly([(-26, -30), (26, -30), (32, 20), (-32, 20)]), far, 5); HEADS[p["head"]](c, t, talk, mood, p); c.restore()
    for i, (rgb, w) in enumerate(((eg, 9), ((250, 240, 220), 7))): q = smooth(tor([(-56, -204), (10, -150 + i * 26), (60, -204)]), False); c.drawPath(q, line(INK, w + 6)); c.drawPath(q, line(rgb, w))
    s1, e1, h1 = J["a1"]
    if weapon and p.get("weapon"): back = end(h1, 0, 0); tp = J["tip"]; st = (h1[0] - (tp[0] - h1[0]) * .22, h1[1] - (tp[1] - h1[1]) * .22); p["weapon"](c, st if p["weapon"] is gada else h1, tp)
    shape(c, limb2(s1, e1, h1, (38 * B, 28 * B, 20 * B)), sk); shape(c, oval(h1[0], h1[1], 27 * B), sk, 5)
    for a_, b_, u_, w_ in ((s1, e1, .62, 33), (e1, h1, .72, 25)):
        m = mx(a_, b_, u_); dx, dy = b_[0] - a_[0], b_[1] - a_[1]; L_ = math.hypot(dx, dy) or 1; n = (-dy / L_ * w_ * B, dx / L_ * w_ * B); c.drawLine(m[0] - n[0], m[1] - n[1], m[0] + n[0], m[1] + n[1], line(INK, 19)); c.drawLine(m[0] - n[0], m[1] - n[1], m[0] + n[0], m[1] + n[1], line(eg, 11))
    c.restore(); return J
def foot(c, k, f, rgb, R, B, eg):
    pts = [(-26, -14), (4, -22), (54, 2), (66, 16), (-24, 18)]; shape(c, smooth([rotp((f[0] + a * B, f[1] + b), f, R) for a, b in pts]), rgb, 5); c.drawCircle(f[0], f[1] - 16, 3, fill(eg, 0))

# ---------------- effects
def burst(c, x, y, t, r=170, rgb=(255, 240, 150)):
    """Impact star: t seconds since the hit."""
    if not 0 <= t < .4: return
    u = t / .4; k = 1 - (1 - u) ** 3; rr = random.Random(int(x)); a = 1 - u
    c.drawCircle(x, y, r * 1.5 * k, line((255, 255, 255), 16 * (1 - u) + 1, a))
    pts = []
    for i in range(20): q = i * pi / 10 + .2; m = r * (1.0 if i % 2 else .42) * (.5 + .6 * k) * (1 - u * .5); pts.append((x + cos(q) * m, y + sin(q) * m))
    c.drawPath(poly(pts), fill(rgb, a)); c.drawPath(poly([((px - x) * .6 + x, (py - y) * .6 + y) for px, py in pts]), fill((255, 255, 255), a))
    for i in range(14): q = rr.uniform(0, 2 * pi); m = r * (.4 + 2.2 * k) * rr.uniform(.6, 1); c.drawLine(x + cos(q) * m * .8, y + sin(q) * m * .8, x + cos(q) * m, y + sin(q) * m, line((255, 200, 70), 8 * a + 1, a))
def dust(c, x, y, t, n=12, w=240, rgb=(200, 176, 150), seed=1):
    if not 0 <= t < .9: return
    u = t / .9; k = 1 - (1 - u) ** 3; r = random.Random(seed)
    for i in range(n): q = r.uniform(-1, 1); c.drawCircle(x + q * w * k, y - 10 - r.uniform(0, 90) * k, r.uniform(22, 50) * (.5 + .7 * k), fill(mix(rgb, (90, 70, 80), r.uniform(0, .3)), .7 * (1 - u)))
def cracks(c, x, y, t, r=300):
    if t < 0: return
    k = min(1, t / .12); rr = random.Random(5)
    for i in range(9):
        a = pi * i / 8; px, py = x, y; p = [(px, py)]
        for j in range(4): px += cos(a) * r * k / 4 + rr.uniform(-16, 16); py += (sin(a) * .26 * r * k / 4 + rr.uniform(-5, 5)); p.append((px, py))
        c.drawPath(poly(p, False), line((30, 16, 26), 8 - i % 3 * 2, .85))
def punchcam(t, events, amp=16, dur=.35):
    """Smoothly decaying shake after the hits."""
    x = y = 0.
    for e, k in events:
        u = t - e
        if 0 <= u < dur: f = (1 - u / dur) ** 2 * amp * k; x += sin(u * 62) * f; y += cos(u * 51) * f
    return x, y
def hitstop(t, events, hold=.075):
    """Freeze for a moment on every hit: real time -> action time."""
    for e, k in sorted(events):
        if t <= e: break
        t -= min(hold * k, t - e)
    return t
_BG = {}
def bg(c, key, draw, dx=0., dy=0., m=240):
    """A still painting, drawn once per process, a bit wider than the picture so it can pan."""
    if key not in _BG:
        s = skia.Surface(W + 2 * m, H + 2 * m); q = s.getCanvas(); q.translate(m, m); draw(q); _BG[key] = s.makeImageSnapshot()
    c.drawImage(_BG[key], -m + max(-m, min(m, dx)), -m + max(-m, min(m, dy)))
def ridge(r, y, a, n=9, x0=-320, x1=W + 320): return [(x0 + (x1 - x0) * i / n, y - (a if i % 2 else a * .25) * r.uniform(.55, 1)) for i in range(n + 1)]
def mountains(c, r, y, a, rgb, snow, n=9, bot=H + 340):
    p = ridge(r, y, a, n); c.drawPath(poly([(-320, bot)] + p + [(W + 320, bot)]), fill(rgb))
    for i in range(1, len(p) - 1):
        (lx, ly), (x, yy), (rx, ry) = p[i - 1], p[i], p[i + 1]
        if yy < ly and yy < ry:
            q = lambda A, u: (x + (A[0] - x) * u, yy + (A[1] - yy) * u); c.drawPath(poly([(x, yy), q((rx, ry), 1), (x + 10, max(ly, ry) + 120)]), fill(mix(rgb, (20, 10, 50), .28)))
            if snow: c.drawPath(poly([q((lx, ly), .42), (x, yy), q((rx, ry), .42), (x + (rx - x) * .2, yy + a * .16), (x + 6, yy + a * .36), (x + (lx - x) * .18, yy + a * .18)]), fill(snow))
