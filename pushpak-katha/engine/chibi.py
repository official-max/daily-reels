"""Little round characters in a painted, deep, softly lit world. -> series/chibi_krishna.png, chibi_ganesh.png, preview_chibi.jpg"""
import random, math, sys
import skia
from math import sin, cos, pi
from PIL import Image
from lab import ROOT, W, H, col, mix, fill, line, vgrad, glow, poly, smooth, oval

def blurp(rgb, a, b): return fill(rgb, a, b)
def form(c, path, rgb, sh=None, lt=None, w=4, s=26, rim=None, off=(-.09, -.11)):
    """Airbrushed form: soft shade on the lower right, soft light on the upper left, thin coloured edge."""
    b = path.getBounds(); ww, hh = b.width(), b.height(); sh = sh or mix(rgb, (70, 20, 90), .36); lt = lt or mix(rgb, (255, 246, 220), .42); k = max(6, min(s, min(ww, hh) * .16))
    c.save(); c.clipPath(path, True); c.drawPaint(fill(rgb))
    inv = skia.Path(); inv.addRect(skia.Rect.MakeLTRB(b.left() - 300, b.top() - 300, b.right() + 300, b.bottom() + 300)); hole = skia.Path(path); hole.offset(ww * off[0] * .8, hh * off[1] * .8); d = skia.Op(inv, hole, skia.kDifference_PathOp); c.drawPath(d, blurp(sh, .85, k))
    hole = skia.Path(path); hole.offset(-ww * off[0] * .55, -hh * off[1] * .55); d = skia.Op(inv, hole, skia.kDifference_PathOp); c.drawPath(d, blurp(lt, .55, k * .8))
    if rim: hole = skia.Path(path); hole.offset(-7, 5); d = skia.Op(inv, hole, skia.kDifference_PathOp); c.drawPath(d, blurp(rim, .95, 3))
    c.restore(); c.drawPath(path, line(mix(sh, (30, 8, 40), .55), w))
def soften(c, sigma, draw):
    p = skia.Paint(ImageFilter=skia.ImageFilters.Blur(sigma, sigma)); c.saveLayer(None, p); draw(); c.restore()
def grass(c, r, y0, y1, n, cols, k0=.5, k1=1.6, x0=-20, x1=W + 20):
    for i in range(n):
        u = i / n; y = y0 + (y1 - y0) * u; k = k0 + (k1 - k0) * u; x = r.uniform(x0, x1); g = r.choice(cols); h = r.uniform(20, 46) * k; l = r.uniform(-16, 16) * k; c.drawPath(smooth([(x - 4 * k, y), (x + l * .4 - 2 * k, y - h * .6), (x + l, y - h), (x + l * .5 + 2 * k, y - h * .55), (x + 4 * k, y)]), fill(mix(g, (255, 250, 160), max(0, r.uniform(-.2, .25)))))
def flowers(c, r, y0, y1, n, cols):
    for i in range(n):
        u = i / n; y = y0 + (y1 - y0) * u; k = .5 + u; x = r.uniform(0, W); q = r.choice(cols); c.drawLine(x, y, x + 3, y - 34 * k, line((60, 120, 50), 4 * k)); y -= 36 * k
        for a in range(6): c.drawCircle(x + cos(a * pi / 3) * 9 * k, y + sin(a * pi / 3) * 8 * k, 7.5 * k, fill(mix(q, (60, 0, 60), .08 * (a % 3))))
        c.drawCircle(x, y, 6 * k, fill((255, 214, 80)))
def leaves(c, r, x, y, rx, ry, n, cols, size=34):
    for i in range(n):
        u = i / n; a, q = r.uniform(0, 2 * pi), r.uniform(0, 1) ** .5; lx, ly = x + cos(a) * rx * q, y + sin(a) * ry * q; k = size * r.uniform(.6, 1.2); lit = max(0, min(1, .5 - (lx - x) / rx * .35 - (ly - y) / ry * .5 + r.uniform(-.2, .2))); g = mix(cols[0], cols[1], lit); c.save(); c.translate(lx, ly); c.rotate(r.uniform(0, 360)); c.drawPath(smooth([(-k, 0), (0, -k * .45), (k, 0), (0, k * .45)]), fill(g)); c.restore()
def trunk(c, x, y, w, h, rgb, bend=0):
    form(c, smooth([(x - w * 1.9, y + 20), (x - w * .9, y - h * .12), (x - w * .75 + bend, y - h * .6), (x - w * .9 + bend, y - h), (x + w * .9 + bend, y - h), (x + w * .7 + bend, y - h * .6), (x + w, y - h * .12), (x + w * 2.1, y + 20), (x, y + 40)]), rgb, w=3); r = random.Random(int(x))
    for _ in range(12): yy = y - r.uniform(.05, .95) * h; xx = x + r.uniform(-.5, .5) * w + bend * (y - yy) / h; c.drawPath(smooth([(xx, yy), (xx + r.uniform(-8, 8), yy - 40), (xx + r.uniform(-8, 8), yy - 90)], False), line(mix(rgb, (20, 0, 20), .35), 4, .6))
def rays(c, x, y, n=9, a=.13, L=1900, rgb=(255, 244, 190), lo=.35, hi=1.35):
    def d():
        r = random.Random(3)
        for i in range(n): q = lo + (hi - lo) * i / n + r.uniform(-.03, .03); w = r.uniform(.02, .06); c.drawPath(poly([(x, y), (x + cos(q) * L, y + sin(q) * L), (x + cos(q + w) * L, y + sin(q + w) * L)]), fill(rgb, a))
    soften(c, 14, d)
def motes(c, r, n=60, rgb=(255, 246, 190)):
    for _ in range(n): x, y, k = r.uniform(0, W), r.uniform(200, H), r.uniform(2, 6); glow(c, x, y, k * 4, rgb, .5); c.drawCircle(x, y, k * .6, fill((255, 255, 240), .9))
def bokeh(c, r, rgb, where):
    def d():
        for x, y, k in where:
            for _ in range(9): c.save(); c.translate(x + r.uniform(-k, k), y + r.uniform(-k, k)); c.rotate(r.uniform(0, 360)); c.drawPath(smooth([(-k, 0), (0, -k * .4), (k, 0), (0, k * .4)]), fill(mix(rgb, (0, 20, 20), r.uniform(0, .4)), .95)); c.restore()
    soften(c, 16, d)

def eye(c, x, y, w, h, iris=(96, 52, 30), look=(0, 0), s=1, lash_n=0):
    q = smooth([(x - w, y + h * .1), (x - w * .6, y - h * .8), (x + w * .1, y - h), (x + w * .8, y - h * .6), (x + w, y + h * .2), (x + w * .5, y + h * .9), (x - w * .5, y + h * .9)]); c.drawPath(q, fill((255, 253, 248))); c.save(); c.clipPath(q, True); c.drawRect(skia.Rect.MakeLTRB(x - w * 1.5, y - h * 1.2, x + w * 1.5, y - h * .45), blurp((90, 60, 120), .35, 9)); ix, iy = x + look[0], y + look[1]; e = skia.Rect.MakeLTRB(ix - w * .74, iy - h * .82, ix + w * .74, iy + h * .86)
    c.drawOval(e, skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeLinear([skia.Point(0, iy - h * .8), skia.Point(0, iy + h * .85)], [col(mix(iris, (10, 0, 10), .75)), col(iris), col(mix(iris, (255, 190, 110), .65))], [0, .5, 1]))); c.drawOval(e, line(mix(iris, (10, 0, 10), .8), 4)); c.drawOval(skia.Rect.MakeLTRB(ix - w * .36, iy - h * .4, ix + w * .36, iy + h * .42), fill((16, 6, 14))); c.drawOval(skia.Rect.MakeLTRB(ix - w * .56, iy - h * .66, ix - w * .04, iy - h * .06), fill((255, 255, 255))); c.drawCircle(ix + w * .34, iy + h * .42, w * .14, fill((255, 255, 255), .9)); c.drawCircle(ix + w * .1, iy + h * .64, w * .08, fill((255, 240, 200), .8)); c.restore()
    lash = smooth([(x - w * 1.12, y + h * .04), (x - w * .72, y - h * .84), (x + w * .1, y - h * 1.06), (x + w * .86, y - h * .66), (x + w * 1.1, y + h * .1)], False); c.drawPath(lash, line((34, 14, 26), max(6, w * .26))); o = x + s * w; [c.drawPath(smooth([(o - s * k * 9, y - h * (.1 + k * .26)), (o + s * (14 - k * 2), y - h * (.28 + k * .28)), (o + s * (24 - k * 4), y - h * (.46 + k * .3))], False), line((34, 14, 26), 8 - k)) for k in range(lash_n)]; c.drawPath(smooth([(x - w * .5, y + h * .97), (x, y + h * 1.03), (x + w * .5, y + h * .97)], False), line((90, 40, 50), 4, .6))
def blush(c, x, y, rx, ry, rgb=(255, 92, 110), a=.5): c.drawOval(skia.Rect.MakeLTRB(x - rx, y - ry, x + rx, y + ry), blurp(rgb, a, 14)); [c.drawLine(x - 16 + k * 16, y + 7, x - 10 + k * 16, y - 7, line((255, 255, 255), 3, .35)) for k in range(3)]
def face(c, sk, iris, brow, mouth="smile", look=(5, 2), sp=94, ey=0, ew=43, eh=56, lash_n=0):
    for s in (-1, 1): eye(c, s * sp, ey, ew, eh, iris, look, s, lash_n); c.drawPath(smooth([(s * (sp - 44), ey - 86), (s * sp, ey - 102), (s * (sp + 42), ey - 84)], False), line(brow, 11)); blush(c, s * (sp + 34), ey + 84, 46, 28)
    c.drawOval(skia.Rect.MakeLTRB(-13, ey + 48, 13, ey + 60), blurp(mix(sk, (120, 20, 60), .5), .7, 3)); c.drawOval(skia.Rect.MakeLTRB(-8, ey + 36, 5, ey + 46), blurp((255, 255, 255), .6, 3))
    if mouth == "open": q = smooth([(-42, ey + 86), (0, ey + 96), (42, ey + 86), (24, ey + 130), (-24, ey + 130)]); c.drawPath(q, fill((150, 30, 56))); c.save(); c.clipPath(q, True); c.drawOval(skia.Rect.MakeLTRB(-22, ey + 110, 24, ey + 150), fill((255, 120, 130))); c.drawRect(skia.Rect.MakeLTRB(-22, ey + 80, 22, ey + 97), fill((255, 255, 255))); c.restore(); c.drawPath(q, line((90, 16, 40), 5))
    else: c.drawPath(smooth([(-30, ey + 92), (0, ey + 106), (30, ey + 92)], False), line((150, 36, 60), 8)); [c.drawCircle(s * 33, ey + 91, 4, fill((150, 36, 60))) for s in (-1, 1)]; c.drawPath(smooth([(-9, ey + 116), (0, ey + 119), (9, ey + 116)], False), line((255, 190, 190), 5, .7))
GOLD = (255, 198, 66)
def beads(c, pts, r, cols):
    for i, (x, y) in enumerate(pts): form(c, oval(x, y, r), cols[i % len(cols)], w=3)
def arc(x, y, rx, ry, a0, a1, n): return [(x + cos(a0 + (a1 - a0) * i / (n - 1)) * rx, y + sin(a0 + (a1 - a0) * i / (n - 1)) * ry) for i in range(n)]
def feather(c, x, y, s, rot):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s); c.drawLine(0, 0, 0, -120, line((120, 150, 60), 8)); r = random.Random(2)
    for i in range(150):
        a = r.uniform(0, 2 * pi); ux, uy = cos(a) * 66, sin(a) * 84; k = r.uniform(.85, 1.12); c.drawPath(smooth([(ux * .3, -140 + uy * .3 + 20), (ux * .8, -146 + uy * .75), (ux * k, -156 + uy * k)], False), line(r.choice([(24, 110, 80), (44, 150, 90), (110, 180, 70), (20, 100, 110)]), 6))
    for a, b, q in ((50, 62, (214, 170, 60)), (40, 50, (40, 150, 130)), (28, 36, (40, 110, 210)), (16, 20, (24, 24, 90))): form(c, oval(0, -150, a, b), q, w=2, s=10)
    c.restore()
def hairs(c, pts, rgb, w=4, n=5):
    for k in range(n): c.drawPath(smooth([(x + k * 9 - n * 4, y + k * 3) for x, y in pts], False), line(mix(rgb, (150, 130, 200), .35), w, .55))

# ---------------- people (origin at the feet, about 760 high)
def kanha(c, t=0.):
    sk, hr = (98, 150, 222), (34, 22, 46); R = (255, 226, 150)
    form(c, smooth([(-200, -560), (-250, -470), (-240, -360), (-190, -300), (-150, -380), (150, -380), (196, -300), (246, -370), (250, -480), (200, -560)]), hr, rim=R)
    form(c, smooth([(60, -330), (130, -250), (180, -120), (150, -90), (90, -160), (40, -260)]), (236, 70, 70), rim=R)
    # crossed legs
    form(c, smooth([(-60, -130), (-70, -60), (-58, -10), (0, -4), (6, -40), (0, -130)]), sk); form(c, smooth([(-66, -20), (-84, 6), (-30, 14), (10, 4), (-4, -20)]), sk); form(c, smooth([(40, -140), (60, -90), (20, -40), (-70, -14), (-110, -20), (-100, -50), (-30, -90), (-10, -140)]), sk); form(c, smooth([(-88, -54), (-140, -40), (-150, -10), (-110, -2), (-84, -14)]), sk); beads(c, arc(-40, -40, 34, 14, .2, 2.6, 5), 8, [GOLD])
    d = smooth([(-92, -230), (-120, -150), (-96, -96), (-40, -110), (0, -84), (50, -108), (106, -90), (122, -150), (92, -230)]); form(c, d, (255, 190, 44)); c.save(); c.clipPath(d, True); [c.drawPath(smooth([(-60 + k * 28, -226), (-70 + k * 34, -160), (-84 + k * 42, -90)], False), line((214, 130, 20), 5, .7)) for k in range(5)]; c.drawPath(smooth([(-124, -108), (-40, -118), (0, -96), (50, -118), (126, -104)], False), line((214, 50, 60), 13)); c.restore()
    form(c, smooth([(-84, -216), (-96, -290), (-70, -360), (70, -360), (96, -290), (84, -216)]), sk); form(c, smooth([(-92, -238), (0, -222), (92, -238), (96, -196), (0, -176), (-96, -196)]), (236, 70, 70), w=3); beads(c, [(-60 + k * 30, -206 + (2 - abs(2 - k)) * 5) for k in range(5)], 9, [GOLD, (70, 200, 180)]); form(c, smooth([(-20, -190), (14, -186), (34, -110), (6, -96), (-10, -120)]), (236, 70, 70), w=3)
    beads(c, arc(0, -356, 66, 100, .25, 2.9, 13), 13, [(255, 250, 240), (255, 160, 50), (255, 250, 240), (240, 80, 110)]); beads(c, arc(0, -364, 50, 46, .2, 2.95, 9), 8, [GOLD])
    # arms and flute
    form(c, smooth([(-66, -346), (-126, -320), (-150, -262), (-96, -248), (-30, -292), (-40, -320), (-90, -296), (-60, -320)]), sk); form(c, smooth([(66, -346), (140, -318), (176, -270), (150, -240), (60, -286), (70, -314), (128, -284), (90, -312)]), sk)
    c.save(); c.translate(0, -318); c.rotate(-9); form(c, poly([(-76, -11), (330, -11), (330, 11), (-76, 11)]), (226, 172, 84), w=4); [c.drawOval(skia.Rect.MakeLTRB(60 + k * 40, -7, 72 + k * 40, 5), fill((90, 46, 24))) for k in range(6)]; [c.drawLine(q, -12, q, 12, line((214, 50, 60), 9)) for q in (30, 310)]; form(c, smooth([(300, 8), (330, 70), (318, 110), (296, 70)]), (255, 150, 60), w=3); form(c, oval(26, 8, 34, 28), sk); form(c, oval(150, 10, 34, 28), sk); [c.drawLine(q, 0, q, 18, line(mix(sk, (30, 20, 90), .6), 4)) for q in (14, 30, 138, 154)]; c.restore()
    for x, y in ((-132, -300), (150, -296)): c.drawOval(skia.Rect.MakeLTRB(x - 24, y - 10, x + 24, y + 12), line(GOLD, 11))
    # head
    c.save(); c.translate(0, -540); c.rotate(-4)
    for s in (-1, 1): form(c, oval(s * 196, 24, 34, 46), sk); form(c, oval(s * 202, 78, 17), GOLD, w=3); form(c, oval(s * 202, 104, 10), (236, 70, 90), w=3)
    form(c, smooth([(-196, -30), (-170, -130), (0, -190), (170, -130), (196, -30), (180, 100), (104, 168), (0, 184), (-104, 168), (-180, 100)]), sk, lt=(190, 222, 255), s=34, rim=R)
    face(c, sk, (112, 56, 26), (34, 22, 46), "smile", (6, 4), ey=18)
    c.drawPath(smooth([(-18, -112), (-12, -54), (0, -44), (12, -54), (18, -112)], False), line((255, 236, 190), 9)); c.drawOval(skia.Rect.MakeLTRB(-6, -84, 6, -52), fill((224, 50, 60)))
    form(c, smooth([(-212, 40), (-226, -80), (-170, -190), (-40, -226), (90, -216), (190, -150), (222, -50), (210, 50), (184, -10), (150, -60), (120, -20), (84, -90), (40, -54), (-10, -100), (-50, -56), (-100, -96), (-130, -30), (-176, -40)]), hr, lt=(110, 96, 170), rim=R)
    for x, y, k in ((-214, 30, 34), (-226, 84, 28), (214, 36, 34), (226, 92, 28), (-208, 132, 22), (212, 138, 22)): form(c, oval(x, y, k), hr, lt=(110, 96, 170)); c.drawArc(skia.Rect.MakeLTRB(x - k * .5, y - k * .5, x + k * .5, y + k * .5), 180, 230, False, line((110, 96, 170), 4, .7))
    hairs(c, [(-150, -150), (-100, -120), (-70, -90)], hr); hairs(c, [(110, -170), (60, -130), (30, -90)], hr)
    form(c, smooth([(-70, -200), (-84, -270), (-30, -320), (50, -316), (90, -262), (74, -204)]), hr, lt=(110, 96, 170), rim=R); feather(c, 54, -230, .95, 24)
    q = smooth([(-176, -140), (-80, -196), (0, -206), (80, -196), (176, -140)], False); c.drawPath(q, line((170, 100, 20), 34)); c.drawPath(q, line(GOLD, 26)); c.drawPath(smooth([(-172, -148), (0, -212), (172, -148)], False), line((255, 244, 190), 5)); beads(c, [(-135 + k * 45, -164 - (9 - (3 - k) ** 2) * 3.6) for k in range(7)], 10, [(236, 60, 90), (70, 200, 190)]); beads(c, [(-120 + k * 40, -134 - (9 - (3 - k) ** 2) * 3.4) for k in range(7)], 6, [(255, 252, 244)]); c.restore()
def calf(c):
    fur = (255, 244, 230); R = (255, 232, 170)
    c.drawPath(smooth([(130, -210), (190, -180), (200, -80), (180, -40)], False), line((190, 150, 130), 16)); form(c, oval(182, -34, 18, 30), (120, 80, 70))
    for x in (-60, 10, 70, 112): form(c, smooth([(x - 24, -120), (x - 20, -10), (x + 22, -10), (x + 26, -120)]), fur); form(c, smooth([(x - 24, -24), (x - 24, 4), (x + 26, 4), (x + 26, -24)]), (120, 84, 80), w=3)
    form(c, smooth([(-110, -190), (-60, -260), (70, -262), (150, -210), (150, -110), (60, -80), (-80, -90)]), fur, rim=R); form(c, smooth([(30, -250), (90, -240), (100, -180), (50, -170)]), (214, 150, 110), w=0)
    for s in (-1, 1): form(c, smooth([(-140 + s * 90, -380), (-140 + s * 170, -410), (-140 + s * 176, -350), (-140 + s * 100, -330)]), (250, 220, 206)); form(c, smooth([(-140 + s * 50, -430), (-140 + s * 66, -470), (-140 + s * 78, -420)]), (230, 206, 160))
    form(c, smooth([(-250, -370), (-220, -440), (-140, -456), (-60, -440), (-30, -370), (-50, -270), (-90, -220), (-190, -220), (-230, -270)]), fur, rim=R); form(c, smooth([(-170, -450), (-110, -450), (-120, -370), (-140, -350), (-160, -370)]), (214, 150, 110), w=0); form(c, smooth([(-212, -256), (-140, -284), (-68, -256), (-76, -206), (-140, -186), (-204, -206)]), (255, 186, 180)); [c.drawOval(skia.Rect.MakeLTRB(-140 + s * 30 - 8, -250, -140 + s * 30 + 8, -234), fill((150, 70, 80))) for s in (-1, 1)]; c.drawPath(smooth([(-160, -212), (-140, -204), (-120, -212)], False), line((150, 70, 80), 5))
    for s in (-1, 1): eye(c, -140 + s * 58, -336, 24, 32, (80, 44, 30), (-3, 2), s); blush(c, -140 + s * 84, -284, 22, 14, a=.35)
    c.drawPath(smooth([(-150, -190), (-90, -170), (-40, -210)], False), line((214, 50, 60), 15)); form(c, oval(-96, -156, 24, 26), GOLD); c.drawCircle(-96, -140, 6, fill((130, 70, 20)))
def ganu(c):
    sk, pk = (255, 190, 170), (255, 138, 150); R = (255, 236, 180)
    for s in (-1, 1): form(c, smooth([(s * 14, -110), (s * 18, -20), (s * 30, 6), (s * 96, 4), (s * 104, -40), (s * 96, -120)]), sk); [form(c, oval(s * 60 + (k - 1) * 18, 0, 9, 8), (255, 240, 226), w=2) for k in range(3)]; c.drawPath(smooth([(s * 20, -34), (s * 60, -24), (s * 104, -40)], False), line(GOLD, 13))
    form(c, smooth([(-130, -190), (-150, -120), (-110, -70), (0, -88), (110, -70), (150, -120), (130, -190)]), (250, 100, 60)); c.drawPath(smooth([(-124, -84), (0, -100), (124, -84)], False), line(GOLD, 12)); [c.drawPath(smooth([(-70 + k * 46, -170), (-80 + k * 54, -110)], False), line((200, 60, 30), 5, .6)) for k in range(4)]
    form(c, smooth([(-120, -160), (-150, -240), (-110, -340), (0, -370), (110, -340), (150, -240), (120, -160), (0, -130)]), sk, s=34); c.drawOval(skia.Rect.MakeLTRB(-8, -210, 8, -196), fill((214, 110, 110))); form(c, smooth([(-126, -184), (0, -160), (126, -184), (130, -146), (0, -120), (-130, -146)]), GOLD, w=3); c.drawPath(smooth([(-90, -330), (0, -240), (80, -150)], False), line((255, 252, 244), 8)); beads(c, arc(0, -350, 92, 66, .3, 2.85, 9), 14, [(255, 150, 50), (255, 224, 90)])
    form(c, smooth([(-100, -320), (-180, -300), (-210, -220), (-160, -196), (-130, -250), (-80, -260)]), sk); form(c, oval(-184, -206, 34, 32), sk); form(c, smooth([(100, -300), (200, -270), (270, -330), (250, -372), (190, -330), (90, -340)]), sk); form(c, oval(272, -360, 34, 32), sk); c.save(); c.translate(58, 84); form(c, smooth([(168, -470), (186, -530), (214, -566), (244, -530), (262, -470), (214, -456)]), (255, 238, 200)); [c.drawPath(smooth([(214, -560), (214 + (k - 1.5) * 20, -510), (214 + (k - 1.5) * 24, -466)], False), line((226, 180, 120), 4)) for k in range(4)]; c.restore()
    for x, y in ((-196, -236), (246, -336)): c.drawOval(skia.Rect.MakeLTRB(x - 32, y - 12, x + 32, y + 14), line(GOLD, 11))
    c.save(); c.translate(0, -520); c.rotate(5)
    for s in (-1, 1): form(c, smooth([(s * 140, -90), (s * 250, -140), (s * 330, -70), (s * 330, 60), (s * 250, 130), (s * 150, 90)]), sk, rim=R); form(c, smooth([(s * 176, -60), (s * 250, -90), (s * 290, -40), (s * 284, 46), (s * 226, 86), (s * 176, 50)]), pk, w=0); form(c, oval(s * 250, 130, 16), GOLD, w=3)
    form(c, smooth([(-180, 0), (-176, -120), (-90, -200), (0, -212), (90, -200), (176, -120), (180, 0), (140, 110), (60, 150), (-60, 150), (-140, 110)]), sk, lt=(255, 236, 220), s=36, rim=R)
    form(c, smooth([(-84, 104), (-112, 130), (-100, 170), (-66, 140)]), (255, 252, 240), w=3); form(c, smooth([(84, 104), (106, 120), (98, 140), (70, 130)]), (255, 252, 240), w=3); q = smooth([(40, 112), (78, 116), (104, 96), (96, 138), (56, 150)]); c.drawPath(q, fill((170, 40, 60))); c.drawPath(q, line((100, 20, 40), 4))
    form(c, smooth([(-46, 40), (-54, 120), (-44, 200), (4, 250), (80, 256), (116, 214), (92, 178), (64, 200), (30, 190), (34, 120), (46, 40), (0, 10)]), sk, lt=(255, 230, 214)); [c.drawPath(smooth([(-42 + k * 3, 84 + k * 34), (-6 + k * 3, 94 + k * 32), (30 + k, 82 + k * 32)], False), line((226, 128, 124), 5, .8)) for k in range(4)]
    for s in (-1, 1): eye(c, s * 94, 4, 38, 48, (70, 44, 34), (6, 4), s); c.drawPath(smooth([(s * 56, -70), (s * 96, -86), (s * 136, -68)], False), line((120, 60, 60), 9)); blush(c, s * 136, 76, 38, 24)
    [c.drawPath(smooth([(-54, -128 + k * 20), (0, -134 + k * 20), (54, -128 + k * 20)], False), line((255, 252, 244), 8)) for k in range(3)]; c.drawOval(skia.Rect.MakeLTRB(-9, -132, 9, -72), fill((226, 46, 54)))
    form(c, smooth([(-150, -130), (-120, -190), (-110, -280), (-50, -240), (0, -340), (50, -240), (110, -280), (120, -190), (150, -130), (0, -190)]), GOLD, rim=R); form(c, smooth([(-160, -124), (0, -188), (160, -124), (154, -160), (0, -226), (-154, -160)]), (226, 56, 70), w=3); beads(c, [(-110 + k * 44, -152 - (6.25 - (2.5 - k) ** 2) * 7) for k in range(6)], 10, [GOLD, (255, 255, 255)]); form(c, oval(0, -256, 18, 22), (226, 56, 90), w=3); form(c, oval(0, -346, 14), (226, 56, 90), w=3); c.restore()
def parvati(c):
    """Seated mother, facing left a little."""
    sk, sari, hr = (246, 200, 160), (46, 160, 120), (36, 20, 34); R = (255, 236, 180)
    form(c, smooth([(-300, 10), (-260, -90), (-120, -170), (120, -170), (270, -90), (310, 10), (0, 40)]), sari, rim=R); [c.drawPath(smooth([(-60 + k * 40, -150), (-110 + k * 60, -70), (-180 + k * 90, 14)], False), line((24, 110, 90), 6, .7)) for k in range(5)]; c.drawPath(smooth([(-296, -6), (-120, 14), (0, 20), (140, 14), (304, -6)], False), line(GOLD, 20)); c.drawPath(smooth([(-290, -30), (0, -2), (296, -30)], False), line((214, 50, 70), 7))
    form(c, smooth([(110, -560), (200, -420), (240, -240), (190, -110), (130, -220), (100, -420)]), hr, rim=R)
    form(c, smooth([(-100, -130), (-110, -260), (-90, -350), (90, -350), (116, -260), (110, -130)]), sk); form(c, smooth([(-104, -250), (-108, -330), (-60, -366), (60, -366), (108, -330), (106, -250), (0, -232)]), (226, 60, 90)); c.drawPath(smooth([(-104, -250), (0, -234), (106, -250)], False), line(GOLD, 11)); form(c, smooth([(50, -370), (112, -340), (60, -220), (-60, -130), (-120, -150), (-20, -250)]), sari); c.drawPath(smooth([(112, -336), (60, -214), (-56, -124)], False), line(GOLD, 10))
    beads(c, arc(0, -366, 62, 60, .2, 2.95, 9), 9, [GOLD, (226, 60, 90)])
    form(c, smooth([(-94, -340), (-170, -290), (-260, -260), (-262, -216), (-170, -222), (-76, -270)]), sk); form(c, oval(-276, -240, 34, 28), sk); form(c, smooth([(100, -340), (160, -280), (130, -190), (20, -150), (10, -190), (90, -230), (80, -290)]), sk); form(c, oval(4, -168, 32, 28), sk)
    for x, y in ((-226, -240), (46, -176)): [c.drawOval(skia.Rect.MakeLTRB(x - 9 + k * 14, y - 26, x + 5 + k * 14, y + 26), line([GOLD, (226, 60, 70)][k % 2], 6)) for k in range(3)]
    # plate of laddoos in the lap
    form(c, smooth([(-190, -170), (0, -186), (120, -170), (90, -130), (-30, -116), (-150, -130)]), (230, 190, 110)); [form(c, oval(x, y, 33), (255, 184, 50)) for x, y in ((-120, -190), (-60, -196), (0, -198), (56, -190), (-90, -236), (-30, -242), (26, -236), (-32, -284))]
    c.save(); c.translate(0, -530); c.rotate(-7)
    form(c, smooth([(-196, 20), (-200, -110), (-110, -210), (20, -226), (150, -190), (208, -90), (204, 60), (150, 130), (-150, 110)]), hr, lt=(110, 90, 150), rim=R)
    for s in (-1, 1): form(c, oval(s * 180, 30, 26, 38), sk); form(c, oval(s * 184, 78, 22, 24), GOLD, w=3); form(c, oval(s * 184, 112, 10), (226, 60, 90), w=3)
    form(c, smooth([(-178, -20), (-150, -120), (0, -160), (150, -120), (178, -20), (160, 96), (90, 156), (0, 172), (-90, 156), (-160, 96)]), sk, lt=(255, 236, 206), s=34); face(c, sk, (90, 50, 30), hr, "smile", (-9, 8), ey=20, sp=88, ew=39, eh=50, lash_n=3)
    form(c, smooth([(-188, 30), (-196, -90), (-110, -190), (0, -206), (0, -140), (-70, -110), (-130, -50), (-160, 10)]), hr, lt=(110, 90, 150)); form(c, smooth([(188, 30), (196, -90), (110, -190), (0, -206), (0, -140), (70, -110), (130, -50), (160, 10)]), hr, lt=(110, 90, 150)); c.drawLine(0, -204, 0, -146, line((226, 40, 50), 9)); c.drawCircle(0, -96, 13, fill((226, 40, 50))); c.drawPath(smooth([(0, -150), (-6, -126), (0, -112)], False), line(GOLD, 6)); form(c, oval(0, -122, 10, 13), (226, 60, 90), w=2); c.drawCircle(-16, 70, 9, line(GOLD, 4)); form(c, smooth([(-150, -150), (-96, -200), (-80, -270), (-30, -230), (0, -300), (30, -230), (80, -270), (96, -200), (150, -150), (0, -206)]), GOLD, rim=R); beads(c, [(-84 + k * 42, -196 - (4 - (2 - k) ** 2) * 5) for k in range(5)], 10, [(226, 60, 90), (70, 190, 160)])
    form(c, smooth([(60, -226), (170, -196), (226, -80), (236, 120), (262, 330), (190, 350), (186, 130), (186, -60), (130, -160)]), (80, 196, 150), rim=R); c.drawPath(smooth([(130, -160), (186, -60), (186, 130), (190, 346)], False), line(GOLD, 10)); c.restore()
def mouse(c):
    g = (188, 176, 196); c.drawPath(smooth([(70, -30), (130, -20), (150, -70), (120, -100)], False), line((214, 150, 160), 10)); form(c, smooth([(-70, 0), (-76, -80), (0, -120), (76, -80), (70, 0)]), g); [form(c, oval(s * 64, -190, 42), g) or form(c, oval(s * 64, -186, 26), (255, 160, 176), w=0) for s in (-1, 1)]; form(c, smooth([(-80, -130), (-60, -180), (0, -196), (60, -180), (80, -130), (40, -84), (-40, -84)]), g)
    for s in (-1, 1): eye(c, s * 34, -140, 15, 20, (60, 34, 40), (3, 2), s)
    c.drawCircle(0, -106, 9, fill((255, 110, 130))); form(c, oval(0, -50, 30), (255, 184, 50)); [form(c, oval(s * 34, -52, 17, 14), g) for s in (-1, 1)]
def at(c, x, y, s, fn, sh=190, d=1):
    c.drawOval(skia.Rect.MakeLTRB(x - sh * s, y - 26 * s, x + sh * s * 1.25, y + 34 * s), blurp((16, 24, 50), .5, 16)); c.save(); c.translate(x, y); c.scale(s * d, s); fn(c); c.restore()

def krishna(c):
    r = random.Random(5); vgrad(c, [(0, (255, 196, 120)), (.35, (255, 224, 160)), (.7, (255, 240, 206))], 0, 1250); glow(c, 250, 420, 620, (255, 252, 220), 1)
    def far():
        for i, (y, rgb) in enumerate(((820, (206, 190, 150)), (900, (160, 180, 130)))): c.drawPath(smooth([(-200, y + 60), (120, y - 90), (420, y + 20), (760, y - 110), (1280, y + 40), (1280, 1400), (-200, 1400)]), fill(rgb))
        for _ in range(26): x, y, k = r.uniform(-60, W + 60), r.uniform(820, 960), r.uniform(50, 120); c.drawCircle(x, y, k, fill(r.choice([(120, 160, 100), (140, 176, 110), (100, 146, 110)]), .9))
    soften(c, 18, far)
    def river():
        c.drawPath(smooth([(-200, 1010), (300, 985), (700, 1000), (1300, 975), (1300, 1250), (-200, 1250)]), skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeLinear([skia.Point(0, 980), skia.Point(0, 1250)], [col((255, 226, 160)), col((110, 176, 190)), col((60, 120, 150))]))); [c.drawLine(x, y, x + r.uniform(40, 200), y, line((255, 250, 220), 4, .6)) for x, y in [(r.uniform(-60, W), r.uniform(1000, 1220)) for _ in range(60)]]
    soften(c, 4, river)
    def mid():
        for x, w, h in ((930, 46, 1200), (80, 34, 1050)): trunk(c, x, 1260, w, h, (120, 84, 70))
        leaves(c, r, 960, 130, 420, 330, 520, [(50, 96, 60), (190, 206, 90)], 40); leaves(c, r, 40, 120, 340, 260, 360, [(60, 110, 70), (214, 220, 110)], 36)
    soften(c, 5, mid)
    for _ in range(26):
        x, y = r.choice([(960, 160), (60, 140)]); x += r.uniform(-260, 230); y += r.uniform(-120, 200); c.drawCircle(x, y, 20, blurp((255, 180, 60), .95, 3)); [c.drawCircle(x + cos(a) * 20, y + sin(a) * 20, 3, fill((255, 244, 200))) for a in [k * pi / 6 for k in range(12)]]
    c.drawPath(smooth([(-200, 1270), (240, 1200), (640, 1250), (1300, 1190), (1300, 2100), (-200, 2100)]), skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeLinear([skia.Point(0, 1200), skia.Point(0, H)], [col((190, 206, 90)), col((96, 160, 70)), col((30, 80, 60))]))); grass(c, r, 1230, 1640, 1500, [(120, 176, 70), (150, 196, 80), (90, 150, 66)]); flowers(c, r, 1300, 1600, 16, [(255, 255, 250), (255, 150, 180), (255, 120, 100)]); rays(c, 180, 250)
    at(c, 860, 1500, .92, calf, 170); at(c, 390, 1650, 1.2, kanha, 130); grass(c, r, 1650, 1930, 900, [(70, 130, 60), (50, 106, 60), (100, 156, 66)], 1.1, 2.4); flowers(c, r, 1720, 1900, 9, [(255, 255, 250), (255, 140, 170), (255, 200, 80)]); motes(c, r); bokeh(c, r, (40, 90, 60), [(40, 1880, 110), (1050, 1860, 130), (1060, 60, 120), (30, 40, 110)])
    c.drawPaint(skia.Paint(Shader=skia.GradientShader.MakeRadial(skia.Point(W / 2, 1000), 1250, [col((0, 0, 0), 0), col((30, 0, 40), .5)], [.55, 1])))
def ganesh(c):
    r = random.Random(8); vgrad(c, [(0, (120, 170, 236)), (.5, (214, 226, 250)), (1, (255, 236, 220))], 0, 1250); glow(c, 820, 380, 600, (255, 250, 226), .95)
    def far():
        for p, rgb, sn in (([(-200, 1150), (60, 760), (200, 880), (470, 460), (700, 800), (820, 700), (1280, 1150)], (140, 160, 206), (250, 252, 255)), ([(-200, 1200), (150, 960), (380, 1060), (700, 900), (980, 1040), (1280, 960), (1280, 1300)], (120, 150, 176), None)):
            c.drawPath(poly(p), fill(rgb))
            if sn: c.drawPath(poly([(470, 460), (590, 640), (530, 620), (490, 700), (430, 610), (350, 640)]), fill(sn)); c.drawPath(poly([(470, 460), (700, 800), (820, 700), (1000, 900), (560, 900)]), fill((90, 110, 170), .35))
        for x, y in ((120, 500), (900, 620), (640, 360)): [c.drawOval(skia.Rect.MakeXYWH(x + q * 60, y - (2 - abs(2 - q)) * 18, 170, 74), fill((255, 255, 255), .8)) for q in range(4)]
    soften(c, 12, far)
    def mid():
        for x, h in ((-10, 560), (110, 400), (960, 460), (1080, 620)):
            for k in range(5): y = 1240 - h * k / 5.5; w = (1 - k / 6) * 150; c.drawPath(smooth([(x, y - 190), (x + w * .6, y - 60), (x + w, y), (x, y + 24), (x - w, y), (x - w * .6, y - 60)]), fill(mix((40, 110, 100), (150, 200, 170), k / 8)))
    soften(c, 6, mid)
    c.drawPath(smooth([(-200, 1240), (300, 1190), (760, 1220), (1300, 1180), (1300, 2100), (-200, 2100)]), skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeLinear([skia.Point(0, 1190), skia.Point(0, H)], [col((170, 214, 130)), col((90, 170, 100)), col((30, 90, 90))]))); grass(c, r, 1215, 1640, 1500, [(110, 180, 96), (140, 200, 110), (80, 156, 90)]); flowers(c, r, 1260, 1600, 22, [(255, 255, 255), (200, 160, 255), (255, 150, 190)]); rays(c, 860, 180, rgb=(255, 252, 226), lo=1.5, hi=2.6, a=.15)
    at(c, 735, 1560, 1.0, parvati, 280); at(c, 300, 1690, .9, ganu, 150); grass(c, r, 1700, 1930, 800, [(60, 140, 90), (44, 116, 84), (96, 170, 96)], 1.1, 2.4); at(c, 610, 1800, .9, mouse, 80); flowers(c, r, 1800, 1910, 8, [(255, 255, 255), (214, 170, 255), (255, 170, 190)]); motes(c, r, 60, (255, 255, 230)); bokeh(c, r, (40, 110, 100), [(30, 1890, 110), (1060, 1870, 120)]); bokeh(c, r, (230, 130, 180), [(40, 40, 90), (1050, 60, 90)])
    c.drawPaint(skia.Paint(Shader=skia.GradientShader.MakeRadial(skia.Point(W / 2, 1000), 1250, [col((0, 0, 0), 0), col((10, 10, 60), .42)], [.55, 1])))
import os
OUT = os.path.join(ROOT, "art")
if __name__ == "__main__":
    o = Image.new("RGB", (1440, 1280))
    for i, (n, fn) in enumerate((("krishna", krishna), ("ganesh", ganesh))): s = skia.Surface(W, H); fn(s.getCanvas()); im = Image.fromarray(s.toarray(colorType=skia.kRGBA_8888_ColorType)).convert("RGB"); im.save(f"{OUT}/chibi_{n}.png"); o.paste(im.resize((720, 1280), Image.LANCZOS), (i * 720, 0))
    o.save(f"{OUT}/preview_chibi.jpg", quality=93)
