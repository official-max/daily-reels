"""Pushpak Katha: logo (800x800) and YouTube banner (2560x1440, everything important inside the middle 1546x423)."""
import os, random, sys
import skia
from math import sin, cos, pi
from PIL import Image
from lab import col, mix, fill, line, glow, poly, smooth, oval, BLACK, BOLD
from lab import ROOT
OUT = os.path.join(ROOT, "brand"); os.makedirs(OUT, exist_ok=True)
GOLD, DK, LT, RED, INK = (246, 182, 52), (168, 92, 22), (255, 236, 160), (206, 44, 52), (44, 14, 40)

def grad(c, path, a, b, y0, y1, ow=8):
    c.drawPath(path, skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeLinear([skia.Point(0, y0), skia.Point(0, y1)], [col(a), col(b)]))); ow and c.drawPath(path, line(INK, ow))
def viman(c, x, y, s):
    """The flying palace with swan prows, about 620 wide; (x, y) is the middle of the deck."""
    c.save(); c.translate(x, y); c.scale(s, s)
    # wings
    for d in (-1, 1):
        for k in range(4): a, up = 1 - k * .13, 150 - k * 58; grad(c, smooth([(d * 150, 60 + k * 14), (d * 250 * a, -20 - up * .5), (d * 430 * a, -up - 40), (d * 450 * a, -up), (d * 370 * a, 10 - up * .2), (d * 240, 100 + k * 10)]), mix(LT, (255, 255, 255), .4 - k * .1), mix(GOLD, RED, k * .2), -190, 110, 7)
    # hull
    grad(c, smooth([(-240, 30), (-200, 110), (-90, 168), (0, 180), (90, 168), (200, 110), (240, 30), (0, 60)]), GOLD, DK, 20, 180, 9); c.drawPath(smooth([(-214, 72), (0, 112), (214, 72)], False), line(RED, 22)); c.drawPath(smooth([(-214, 72), (0, 112), (214, 72)], False), line(INK, 3)); [c.drawCircle(-160 + k * 64, 84 + (2.5 - abs(2.5 - k)) * 8, 10, fill(LT)) for k in range(6)]
    for d in (-1, 1):      # swans: long S neck, small head bowed outwards, crown of gold
        grad(c, smooth([(d * 150, 96), (d * 236, 60), (d * 282, 10), (d * 290, -50), (d * 262, -110), (d * 244, -170), (d * 262, -222), (d * 306, -238), (d * 340, -214), (d * 344, -184), (d * 318, -178), (d * 300, -196), (d * 290, -176), (d * 306, -120), (d * 340, -50), (d * 330, 40), (d * 270, 110), (d * 190, 134)]), (255, 255, 252), (255, 222, 200), -240, 130, 8)
        bk = smooth([(d * 330, -212), (d * 366, -196), (d * 382, -160), (d * 352, -172), (d * 328, -182)]); c.drawPath(bk, fill((255, 150, 40))); c.drawPath(bk, line(INK, 6)); c.drawCircle(d * 312, -210, 8, fill(INK)); cr = poly([(d * 270, -232), (d * 262, -276), (d * 286, -254), (d * 302, -284), (d * 314, -250), (d * 334, -262), (d * 326, -232), (d * 298, -240)]); c.drawPath(cr, fill(GOLD)); c.drawPath(cr, line(INK, 5)); nk = smooth([(d * 262, -24), (d * 296, -8), (d * 334, -22)], False); c.drawPath(nk, line(INK, 22)); c.drawPath(nk, line(GOLD, 13))
    # palace
    def tower(tx, w, h, base):
        grad(c, poly([(tx - w, base), (tx - w, base - h * .5), (tx + w, base - h * .5), (tx + w, base)]), LT, GOLD, base - h * .5, base, 7); grad(c, smooth([(tx - w * .9, base - h * .46), (tx - w * .8, base - h * .5), (tx - w * .6, base - h * .75), (tx, base - h), (tx + w * .6, base - h * .75), (tx + w * .8, base - h * .5), (tx + w * .9, base - h * .46)]), (255, 120, 70), RED, base - h, base - h * .5, 7); c.drawRect(skia.Rect.MakeLTRB(tx - w * 1.1, base - h * .54, tx + w * 1.1, base - h * .47), fill(DK)); c.drawRect(skia.Rect.MakeLTRB(tx - w * 1.1, base - h * .54, tx + w * 1.1, base - h * .47), line(INK, 5)); c.drawCircle(tx, base - h * 1.0, w * .16, fill(LT)); c.drawCircle(tx, base - h, w * .16, line(INK, 5))
        d = smooth([(tx - w * .42, base), (tx - w * .42, base - h * .22), (tx, base - h * .38), (tx + w * .42, base - h * .22), (tx + w * .42, base)]); c.drawPath(d, fill((90, 24, 60))); glow(c, tx, base - h * .1, w * .6, (255, 220, 120), .9); c.drawPath(d, line(INK, 5))
    tower(-140, 52, 210, 44); tower(140, 52, 210, 44); tower(0, 88, 350, 56)
    c.drawLine(0, -300, 0, -372, line(INK, 8)); f = smooth([(2, -372), (60, -384), (104, -352), (60, -346), (2, -326)]); c.drawPath(f, fill((255, 140, 40))); c.drawPath(f, line(INK, 6)); c.restore()
def clouds(c, r, w, y0, y1, n, rgb, a):
    c.saveLayer(None, skia.Paint(Alphaf=a))
    for _ in range(n):
        x, y, k = r.uniform(-100, w), r.uniform(y0, y1), r.uniform(.6, 1.3)
        for q in range(5): c.drawOval(skia.Rect.MakeXYWH(x + q * 66 * k, y - (2 - abs(2 - q)) * 24 * k, 160 * k, 84 * k), fill(rgb))
    c.restore()
def sky(c, w, h, r):
    c.drawPaint(skia.Paint(Shader=skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, h)], [col((24, 10, 58)), col((96, 28, 104)), col((232, 92, 70)), col((255, 176, 80))], [0, .42, .8, 1])))
    for _ in range(int(w * h / 9000)): c.drawCircle(r.uniform(0, w), r.uniform(0, h * .55), r.uniform(1, 3.4), fill((255, 244, 214), r.uniform(.3, 1)))
def disc(c, x, y, R):
    glow(c, x, y, R * 1.9, (255, 214, 130), .75); c.drawCircle(x, y, R, skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeLinear([skia.Point(0, y - R), skia.Point(0, y + R)], [col((255, 250, 214)), col((255, 206, 110))])))
    for k in range(48): a = k * pi / 24; l = 1.13 if k % 2 else 1.2; c.drawLine(x + cos(a) * R * 1.05, y + sin(a) * R * 1.05, x + cos(a) * R * l, y + sin(a) * R * l, line((255, 226, 150), R * .014, .8))
def save(s, n): Image.fromarray(s.toarray(colorType=skia.kRGBA_8888_ColorType)).convert("RGB").save(f"{OUT}/{n}.png")

r = random.Random(4); s = skia.Surface(800, 800); c = s.getCanvas(); sky(c, 800, 800, r); disc(c, 400, 380, 252); clouds(c, r, 700, 640, 760, 5, (255, 214, 190), .55); viman(c, 400, 450, .8); clouds(c, r, 700, 730, 800, 5, (255, 240, 225), .85); save(s, "logo")
m = Image.open(f"{OUT}/logo.png"); p = Image.new("RGB", (800, 260), (255, 255, 255)); x = 20
for k in (200, 98, 48): q = m.resize((k, k), Image.LANCZOS); from PIL import ImageDraw; ms = Image.new("L", (k, k), 0); ImageDraw.Draw(ms).ellipse([0, 0, k, k], fill=255); p.paste(q, (x, 30), ms); x += k + 30
r = random.Random(9); s = skia.Surface(2560, 1440); c = s.getCanvas(); sky(c, 2560, 1440, r); disc(c, 1790, 715, 230)
for y, rgb in ((1060, (120, 40, 100)), (1180, (84, 24, 84))): c.drawPath(poly([(0, 1440), (0, y)] + [(x, y - 70 * abs(sin(x / 190 + y))) for x in range(0, 2561, 40)] + [(2560, 1440)]), fill(rgb))
clouds(c, r, 2560, 900, 1010, 12, (255, 190, 170), .4); viman(c, 1790, 738, .56); clouds(c, r, 2560, 980, 1400, 16, (255, 220, 200), .28)
f = lambda z, b=BLACK: skia.Font(skia.Typeface.MakeFromFile(b), z)
def text(t, x, y, z, rgb, b=BLACK, edge=10): (edge and c.drawString(t, x, y, f(z, b), skia.Paint(Color=col(INK), AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=edge, StrokeJoin=skia.Paint.kRound_Join))); c.drawString(t, x, y, f(z, b), fill(rgb))
text("PUSHPAK", 545, 690, 160, (255, 244, 220), edge=20); text("KATHA", 545, 830, 160, (255, 200, 70), edge=20); text("Roz ek nayi katha: Ramayan, shuru se", 550, 898, 43, (255, 255, 255), BOLD, 9); save(s, "banner")
b = Image.open(f"{OUT}/banner.png"); ImageDraw.Draw(b).rectangle([507, 508, 2053, 931], outline=(0, 255, 0), width=4); o = Image.new("RGB", (1280, 1010), (255, 255, 255)); o.paste(b.resize((1280, 720)), (0, 0)); o.paste(p, (0, 735)); o.save(f"{OUT}/preview.jpg", quality=92)
