"""One sample picture for each of the seven weekday series, each in its own art style. -> series/*.png and preview_series.jpg"""
import os, sys, random, math
import skia
from math import sin, cos, pi
from PIL import Image
from lab import W, H, col, mix, fill, line, vgrad, glow, poly, smooth, oval, BLACK, BOLD
import puppet as pp
from lab import ROOT
OUT = os.path.join(ROOT, "art"); os.makedirs(OUT, exist_ok=True)

def rim(c, path, rgb, lt, dk, off=(-14, -10), ow=0, ink=(20, 14, 30)):
    """Painted form: base, dark side, lit edge."""
    c.save(); c.clipPath(path, True); c.drawPaint(fill(dk)); c.translate(*off); c.drawPath(path, fill(rgb)); c.translate(off[0] * 1.2, off[1] * 1.2); c.restore()
    c.save(); c.clipPath(path, True); c.drawPath(path, line(lt, 12, .75)); c.restore()
    if ow: c.drawPath(path, line(ink, ow))
def flat(c, path, rgb, ow=9, ink=(52, 26, 30), sh=.16, off=(-16, -14)):
    c.save(); c.clipPath(path, True); c.drawPaint(fill(mix(rgb, (120, 20, 60), sh * 2))); c.translate(*off); c.drawPath(path, fill(rgb)); c.restore(); c.drawPath(path, line(ink, ow))
def paper(c, path, rgb, d=12, edge=True):
    c.save(); c.translate(d * .6, d); c.drawPath(path, fill((20, 4, 10), .45, d * .9)); c.restore(); c.drawPath(path, fill(rgb))
    if edge: c.save(); c.clipPath(path, True); c.translate(2, 4); c.drawPath(path, line(mix(rgb, (255, 255, 255), .4), 6, .8)); c.restore()
def label(c, day, name, rgb, y=96):
    f, g = skia.Font(skia.Typeface.MakeFromFile(BLACK), 74), skia.Font(skia.Typeface.MakeFromFile(BOLD), 42); w = f.measureText(name) / 2 + 60
    c.drawRoundRect(skia.Rect.MakeLTRB(W / 2 - w, y, W / 2 + w, y + 190), 40, 40, fill((10, 6, 20), .55)); c.drawString(day, W / 2 - g.measureText(day) / 2, y + 62, g, fill((255, 255, 255))); c.drawString(name, W / 2 - f.measureText(name) / 2, y + 148, f, fill(rgb))
def vig(c, a=.6): c.drawPaint(skia.Paint(Shader=skia.GradientShader.MakeRadial(skia.Point(W / 2, H * .5), 1250, [col((0, 0, 0), 0), col((0, 0, 10), a)], [.5, 1])))
def mirror(pts, cx=540): return pts + [(2 * cx - x, y) for x, y in reversed(pts)]

# ---------------- 1 Shiv: cold painted light, front view, symmetrical
def shiv(c):
    r = random.Random(1); vgrad(c, [(0, (6, 12, 40)), (.55, (30, 84, 140)), (1, (150, 200, 226))], 0, 1500); [c.drawCircle(r.uniform(0, W), r.uniform(0, 1000), r.uniform(1, 4), fill((230, 245, 255), r.uniform(.3, 1))) for _ in range(150)]
    c.drawPath(poly([(0, 1300), (120, 1000), (250, 1120), (540, 420), (820, 1100), (960, 960), (1080, 1280), (1080, H), (0, H)]), fill((60, 110, 160))); c.drawPath(poly([(540, 420), (820, 1100), (960, 960), (1080, 1280), (1080, 1500), (620, 1400), (570, 900), (590, 700)]), fill((34, 72, 124))); c.drawPath(poly([(540, 420), (640, 660), (590, 640), (560, 720), (510, 640), (440, 690)]), fill((240, 250, 255)))
    glow(c, 540, 820, 620, (130, 210, 255), .75); c.drawCircle(540, 790, 330, line((220, 245, 255), 5, .6)); c.drawCircle(540, 790, 372, line((220, 245, 255), 2, .5))
    for i in range(48): a = i * pi / 24; c.drawLine(540 + cos(a) * 385, 790 + sin(a) * 385, 540 + cos(a) * (420 + 30 * (i % 2)), 790 + sin(a) * (420 + 30 * (i % 2)), line((200, 235, 255), 4, .45))
    c.drawPath(smooth([(-40, 1640), (200, 1560), (540, 1530), (880, 1560), (1120, 1640), (1120, 2000), (-40, 2000)]), fill((226, 240, 250))); c.drawPath(smooth([(-40, 1780), (300, 1690), (800, 1740), (1120, 1700), (1120, 2000), (-40, 2000)]), fill((170, 206, 232)))
    sk, dk, lt, ink = (120, 170, 206), (44, 78, 128), (224, 246, 255), (14, 24, 52)
    # trishul and damru
    c.drawLine(880, 640, 880, 1640, line(ink, 24)); c.drawLine(880, 640, 880, 1640, line((190, 206, 216), 14)); c.drawLine(874, 640, 874, 1640, line((255, 255, 255), 3, .8))
    for p in (smooth([(866, 660), (872, 520), (880, 430), (888, 520), (894, 660)]), smooth([(880, 660), (800, 640), (790, 540), (806, 470), (824, 560), (870, 610)]), smooth([(880, 660), (960, 640), (970, 540), (954, 470), (936, 560), (890, 610)])): rim(c, p, (214, 226, 234), (255, 255, 255), (90, 110, 140), (-6, -4), 6, ink)
    c.drawPath(poly([(838, 800), (922, 800), (892, 850), (922, 900), (838, 900), (868, 850)]), fill((150, 60, 40))); c.drawPath(poly([(838, 800), (922, 800), (892, 850), (922, 900), (838, 900), (868, 850)]), line(ink, 7)); c.drawLine(860, 850, 900, 850, line((240, 200, 90), 9))
    # hair falling behind
    rim(c, smooth(mirror([(540, 470), (430, 520), (390, 700), (350, 900), (330, 1090), (390, 1110), (430, 980)])), (50, 40, 60), (120, 150, 200), (18, 14, 34), ow=7, ink=ink)
    # tiger skin seat, legs
    rim(c, smooth([(150, 1600), (200, 1520), (540, 1490), (880, 1520), (930, 1600), (800, 1670), (540, 1690), (280, 1670)]), (222, 150, 62), (255, 220, 150), (140, 70, 30), ow=8, ink=ink); [c.drawPath(smooth([(220 + i * 70, 1600 + (i % 2) * 30), (240 + i * 70, 1640), (230 + i * 70, 1670)], False), line((60, 30, 20), 14)) for i in range(10)]
    rim(c, smooth([(170, 1560), (200, 1450), (380, 1380), (540, 1420), (700, 1380), (880, 1450), (910, 1560), (760, 1600), (540, 1560), (320, 1600)]), sk, lt, dk, ow=8, ink=ink); rim(c, smooth([(380, 1400), (540, 1350), (700, 1400), (760, 1480), (540, 1530), (320, 1480)]), (226, 156, 66), (255, 220, 150), (140, 70, 30), ow=7, ink=ink); [c.drawPath(smooth([(400 + i * 60, 1410 + (i % 2) * 20), (416 + i * 60, 1450), (404 + i * 60, 1490)], False), line((60, 30, 20), 12)) for i in range(6)]
    for s in (-1, 1): c.drawPath(smooth([(540 + s * 60, 1540), (540 + s * 170, 1510), (540 + s * 250, 1540), (540 + s * 180, 1586)]), fill(mix(sk, lt, .2))); c.drawPath(smooth([(540 + s * 60, 1540), (540 + s * 170, 1510), (540 + s * 250, 1540), (540 + s * 180, 1586)]), line(ink, 6))
    # torso and arms
    rim(c, smooth(mirror([(540, 990), (450, 1000), (300, 1060), (290, 1150), (350, 1260), (390, 1420), (540, 1430)])), sk, lt, dk, ow=8, ink=ink)
    for s in (-1, 1):
        q = [(540 + s * x, y) for x, y in ((190, 1050), (250, 1060), (292, 1180), (300, 1300), (330, 1420), (270, 1470), (220, 1330), (196, 1200))]; rim(c, smooth(q), sk, lt, dk, ow=8, ink=ink); c.drawPath(smooth([(540 + s * 285, 1150), (540 + s * 240, 1170), (540 + s * 196, 1150)], False), line((120, 70, 40), 20)); c.drawCircle(540 + s * 300, 1465, 34, fill(sk)); c.drawCircle(540 + s * 300, 1465, 34, line(ink, 7))
        for k in range(3): c.drawLine(540 + s * 205, 1216 + k * 18, 540 + s * 296, 1206 + k * 18, line((236, 240, 240), 7, .85))
    c.drawPath(smooth([(430, 1130), (500, 1160), (538, 1130)], False), line(dk, 7)); c.drawPath(smooth([(650, 1130), (580, 1160), (542, 1130)], False), line(dk, 7)); [c.drawPath(smooth([(480, 1230 + k * 50), (540, 1244 + k * 50), (600, 1230 + k * 50)], False), line(dk, 5)) for k in range(3)]; [c.drawLine(440, 1080 + k * 20, 640, 1080 + k * 20, line((236, 240, 240), 8, .8)) for k in range(3)]
    for i in range(23): a = pi * i / 22; c.drawCircle(540 - cos(a) * 150, 1010 + sin(a) * 250, 17, fill((116, 62, 40))); c.drawCircle(536 - cos(a) * 150, 1005 + sin(a) * 250, 6, fill((200, 140, 100)))
    # neck, blue throat, snake
    rim(c, poly([(480, 900), (600, 900), (616, 1030), (464, 1030)]), (60, 104, 176), lt, dk, ow=7, ink=ink); sp = smooth([(420, 1010), (480, 1050), (600, 1050), (660, 990), (600, 960), (470, 980), (430, 930), (400, 860)], False); c.drawPath(sp, line(ink, 44)); c.drawPath(sp, line((70, 120, 84), 32)); c.drawPath(sp, line((150, 200, 130), 8)); rim(c, smooth([(366, 860), (350, 800), (392, 760), (436, 800), (424, 860)]), (70, 120, 84), (190, 230, 150), (30, 60, 50), ow=7, ink=ink); [c.drawCircle(x, 806, 7, fill((255, 220, 60))) for x in (380, 408)]; c.drawPath(poly([(390, 770), (384, 740), (394, 752), (402, 738), (398, 770)], False), line((220, 40, 50), 5))
    # face
    for s in (-1, 1): rim(c, oval(540 + s * 128, 800, 24, 44), sk, lt, dk, ow=6, ink=ink); c.drawCircle(540 + s * 134, 862, 24, line(ink, 13)); c.drawCircle(540 + s * 134, 862, 24, line((236, 236, 226), 7))
    rim(c, smooth(mirror([(540, 600), (450, 616), (410, 700), (416, 820), (452, 900), (500, 950), (540, 956)])), sk, lt, dk, off=(-10, -8), ow=8, ink=ink)
    for k in range(3): c.drawPath(smooth([(440, 672 + k * 22), (540, 664 + k * 22), (640, 672 + k * 22)], False), line((244, 246, 246), 9))
    e = smooth([(540, 640), (558, 690), (540, 738), (522, 690)]); glow(c, 540, 690, 90, (255, 190, 80), .9); c.drawPath(e, fill((255, 246, 220))); c.drawCircle(540, 690, 13, fill((220, 70, 20))); c.drawPath(e, line(ink, 5))
    for s in (-1, 1): c.drawPath(smooth([(540 + s * 26, 778), (540 + s * 66, 752), (540 + s * 108, 770)], False), line(ink, 11)); c.drawPath(smooth([(540 + s * 30, 808), (540 + s * 66, 826), (540 + s * 104, 802)], False), line(ink, 8)); [c.drawLine(540 + s * (50 + k * 18), 822 - k * 3, 540 + s * (54 + k * 20), 836 - k * 4, line(ink, 4)) for k in range(3)]
    c.drawPath(smooth([(532, 790), (520, 852), (540, 868), (560, 852)], False), line(dk, 7)); c.drawPath(smooth([(500, 902), (522, 894), (540, 900), (558, 894), (580, 902), (540, 922)]), fill((110, 50, 80))); c.drawPath(smooth([(498, 902), (540, 910), (582, 902)], False), line(ink, 4))
    # jata, moon, ganga
    rim(c, smooth(mirror([(540, 560), (470, 556), (400, 640), (392, 720), (430, 690), (480, 640), (540, 630)])), (64, 50, 66), (150, 170, 210), (22, 16, 36), ow=7, ink=ink); rim(c, smooth([(440, 580), (420, 500), (470, 420), (540, 390), (610, 420), (660, 500), (640, 580), (540, 610)]), (64, 50, 66), (150, 170, 210), (22, 16, 36), ow=7, ink=ink); [c.drawPath(smooth([(440 + k * 34, 580), (470 + k * 20, 480), (540, 410)], False), line((24, 18, 38), 5)) for k in range(7)]; c.drawPath(smooth([(440, 566), (540, 596), (640, 566)], False), line((120, 70, 40), 20))
    m = skia.Op(oval(632, 470, 54), oval(654, 454, 48), skia.kDifference_PathOp); glow(c, 632, 470, 130, (255, 250, 220), .8); c.drawPath(m, fill((255, 250, 226)))
    g = smooth([(520, 400), (470, 330), (380, 350), (330, 480), (320, 700), (300, 960)], False); c.drawPath(g, line((190, 235, 255), 26, .6)); c.drawPath(g, line((255, 255, 255), 10, .9))
    for _ in range(90): x, y = r.uniform(0, W), r.uniform(0, H); c.drawCircle(x, y, r.uniform(2, 8), fill((255, 255, 255), r.uniform(.3, .9)))
    vig(c); label(c, "SOMVAAR", "SHIV MAHAGATHA", (160, 225, 255))

# ---------------- 2 Ramayan: cinematic, warm, strong silhouettes with light; ten heads in the sky
def ravan_head(c, x, y, s, main=False):
    c.save(); c.translate(x, y); c.scale(s, s); sk, dk, ink = (132, 62, 48), (60, 18, 32), (28, 6, 16)
    flat2 = lambda p, rgb, ow=7: rim(c, p, rgb, (255, 170, 90), mix(rgb, dk, .6), (-8, -10), ow, ink)
    flat2(smooth([(-120, -60), (-140, 60), (-110, 130), (110, 130), (140, 60), (120, -60)]), (24, 12, 22)); flat2(smooth([(-96, -80), (-104, 20), (-80, 96), (-40, 140), (0, 150), (40, 140), (80, 96), (104, 20), (96, -80), (0, -110)]), sk)
    for q in (-1, 1): c.drawPath(smooth([(q * 14, -26), (q * 50, -52), (q * 94, -40)], False), line(ink, 17)); c.drawPath(smooth([(q * 18, -6), (q * 46, -22), (q * 78, -6), (q * 46, 8)]), fill((255, 236, 190))); c.drawCircle(q * 44, -6, 11, fill((190, 20, 20))); c.drawCircle(q * 44, -6, 5, fill(ink)); c.drawCircle(q * 112, 50, 18, line((246, 190, 70), 9)); c.drawPath(smooth([(q * 4, 62), (q * 40, 50), (q * 84, 66), (q * 110, 30)], False), line(ink, 18))
    c.drawPath(smooth([(-12, -10), (-26, 40), (0, 52), (26, 40), (12, -10)], False), line(dk, 7)); q = smooth([(-44, 78), (0, 70), (44, 78), (20, 104), (-20, 104)]); c.drawPath(q, fill((70, 6, 16))); [c.drawPath(poly([(a - 8, 78), (a + 8, 78), (a, 100)]), fill((255, 250, 230))) for a in (-26, 26)]; c.drawPath(smooth([(0, -84), (8, -50), (0, -38), (-8, -50)]), fill((255, 80, 30)))
    flat2(poly([(-118, -70), (-130, -190), (-84, -140), (-52, -230), (-20, -160), (0, -270), (20, -160), (52, -230), (84, -140), (130, -190), (118, -70)]), (222, 150, 44)); c.drawRect(skia.Rect.MakeLTRB(-118, -96, 118, -62), fill((150, 20, 34))); [c.drawCircle(a, -79, 9, fill((255, 220, 110))) for a in range(-100, 101, 40)]; c.drawCircle(0, -150, 17, fill((220, 30, 50))); c.restore()
def ramayan(c):
    r = random.Random(4); vgrad(c, [(0, (34, 6, 24)), (.4, (150, 30, 30)), (.72, (250, 140, 50)), (1, (255, 220, 130))], 0, 1500); glow(c, 540, 1240, 760, (255, 230, 140), .9); c.drawCircle(540, 1260, 220, fill((255, 246, 200)))
    for i in range(9): x, y = r.uniform(-100, 1000), r.uniform(300, 1000); [c.drawOval(skia.Rect.MakeXYWH(x + q * 80, y - (2 - abs(2 - q)) * 24, 190, 90), fill((70, 10, 30), .35)) for q in range(5)]
    glow(c, 540, 700, 620, (255, 60, 20), .45)
    for i in (4, 3, 2, 1): [ravan_head(c, 540 + q * (70 + i * 96), 690 + i * i * 7, .98 - i * .13) for q in (-1, 1)]
    ravan_head(c, 540, 660, .62) if False else None; ravan_head(c, 540, 720, 1.25)
    c.drawPaint(fill((255, 90, 30), .10))
    for k, (y, rgb) in enumerate(((1330, (120, 40, 50)), (1430, (80, 22, 44)))): c.drawPath(poly([(0, H), (0, y)] + [(x, y - 60 * abs(sin(x / 130 + k))) for x in range(0, W + 1, 30)] + [(W, H)]), fill(rgb))
    c.drawPath(smooth([(-60, 1640), (200, 1560), (620, 1610), (1140, 1540), (1200, 2000), (-60, 2000)]), fill((42, 12, 32)))
    for x, s in ((40, 1), (1040, -1)):
        c.drawPath(smooth([(x - 60, 1700), (x - 30, 1200), (x - 20 * s, 600), (x + 30 * s, 600), (x + 40, 1200), (x + 70, 1700)]), fill((26, 8, 24))); [c.drawOval(skia.Rect.MakeXYWH(x - 190 + r.uniform(-60, 60), 400 + r.uniform(0, 300), 300, 130), fill((30, 10, 26))) for _ in range(7)]
    # Ram, side view, drawing the bow up at Ravan
    sk, lt, dk, ink = (70, 132, 180), (255, 220, 150), (24, 50, 96), (20, 10, 30); R = lambda p, rgb, o=(-12, -6): rim(c, p, rgb, lt, mix(rgb, (20, 6, 40), .6), o, 8, ink)
    c.save(); c.translate(400, 1640); c.scale(.98, .98)
    R(smooth([(-150, -440), (-230, -300), (-300, -120), (-250, -110), (-180, -220), (-60, -380)]), (220, 90, 30)); R(smooth([(-60, -330), (-150, -180), (-190, 10), (-120, 20), (-70, -140), (10, -290)]), sk); R(smooth([(-200, -6), (-130, -10), (-70, 26), (-200, 30)]), sk); R(smooth([(0, -320), (100, -230), (110, -120), (90, 20), (150, 24), (170, -130), (150, -270), (70, -350)]), sk); R(smooth([(80, 0), (150, 0), (220, 34), (80, 36)]), sk)
    R(smooth([(-80, -400), (70, -400), (170, -260), (150, -180), (30, -250), (-90, -140), (-160, -190)]), (244, 176, 40)); [c.drawPath(smooth([(-50 + k * 30, -380), (-70 + k * 50, -300), (-110 + k * 80, -210)], False), line((170, 100, 20), 5)) for k in range(4)]
    R(smooth([(-80, -390), (-110, -520), (-100, -640), (-10, -690), (90, -640), (80, -520), (70, -390)]), sk); R(smooth([(-86, -420), (76, -420), (74, -372), (-84, -372)]), (200, 50, 40)); R(poly([(-110, -650), (-70, -670), (80, -440), (40, -420)]), (244, 176, 40))
    R(poly([(-200, -760), (-150, -790), (-60, -560), (-110, -540)]), (120, 60, 40)); [c.drawLine(-180 + k * 16, -780, -210 + k * 22, -860, line((255, 230, 180), 7)) for k in range(4)]
    c.save(); c.rotate(-24, 0, -640)
    bw = skia.Path(); bw.moveTo(250, -960); bw.cubicTo(420, -860, 340, -700, 350, -640); bw.cubicTo(340, -580, 420, -420, 250, -320); c.drawPath(bw, line(ink, 34)); c.drawPath(bw, line((246, 190, 70), 22)); c.drawPath(poly([(250, -960), (-96, -640), (250, -320)], False), line((255, 250, 230), 4)); c.drawLine(-110, -640, 470, -640, line(ink, 14)); c.drawLine(-110, -640, 470, -640, line((255, 236, 180), 8)); glow(c, 500, -640, 150, (255, 250, 190), 1); c.drawPath(poly([(530, -640), (456, -668), (474, -640), (456, -612)]), fill((255, 255, 240)))
    R(smooth([(40, -670), (180, -668), (330, -668), (376, -640), (330, -612), (180, -604), (40, -596)]), sk); R(smooth([(-20, -670), (-130, -700), (-230, -690), (-220, -650), (-120, -620), (-70, -616), (-110, -650), (-20, -610)]), sk); [R(poly([(x, -678), (x + 24, -678), (x + 24, -594), (x, -594)]), (246, 190, 70)) for x in (90, 290)]
    c.restore()
    c.save(); c.translate(10, -690); c.rotate(-14); R(poly([(-34, -40), (34, -40), (40, 30), (-40, 30)]), mix(sk, dk, .4)); R(smooth([(-70, -220), (-130, -120), (-120, 40), (-150, 150), (-90, 130), (-60, 0), (-20, -60)]), (28, 18, 30)); R(smooth([(-70, -40), (-84, -130), (-50, -200), (20, -214), (74, -190), (84, -150), (80, -130), (104, -104), (82, -88), (90, -66), (78, -50), (74, -24), (30, 0), (-30, -14)]), sk, (-8, -6)); c.drawPath(smooth([(20, -140), (46, -156), (78, -146)], False), line(ink, 9)); c.drawPath(smooth([(30, -122), (54, -134), (76, -122), (52, -114)]), fill((255, 250, 235))); c.drawCircle(60, -123, 8, fill(ink)); c.drawPath(smooth([(86, -62), (60, -56), (52, -60)], False), line((110, 20, 50), 6)); c.drawPath(smooth([(56, -196), (66, -170), (60, -150)], False), line((255, 210, 60), 8)); R(oval(-22, -110, 16, 26), sk); c.drawCircle(-22, -74, 13, line((246, 190, 70), 7)); R(smooth([(-84, -150), (-70, -230), (20, -250), (84, -196), (20, -206), (-30, -170)]), (28, 18, 30)); R(smooth([(-70, -220), (-60, -310), (-10, -340), (40, -300), (30, -230)]), (28, 18, 30)); c.drawPath(smooth([(-72, -232), (-10, -250), (34, -236)], False), line((246, 190, 70), 13)); c.restore(); c.restore()
    for _ in range(70): c.drawCircle(r.uniform(0, W), r.uniform(300, H), r.uniform(2, 7), fill((255, 190, 80), r.uniform(.3, .9)))
    vig(c, .7); label(c, "MANGALVAAR", "RAMAYAN", (255, 200, 90))

# ---------------- 3 Ganesh: round, bright children's cartoon
def ganesh(c):
    r = random.Random(7); vgrad(c, [(0, (120, 214, 240)), (1, (255, 244, 200))], 0, 1400); c.drawCircle(860, 480, 110, fill((255, 226, 90))); [c.drawPath(poly([(860 + cos(a - .1) * 140, 480 + sin(a - .1) * 140), (860 + cos(a) * 190, 480 + sin(a) * 190), (860 + cos(a + .1) * 140, 480 + sin(a + .1) * 140)]), fill((255, 226, 90))) for a in [i * pi / 6 for i in range(12)]]
    for x, y in ((180, 460), (640, 380)): [c.drawCircle(x + q * 56, y - (20 if q % 2 else 0), 56, fill((255, 255, 255))) for q in range(4)]
    c.drawPath(smooth([(-100, 1400), (200, 1180), (520, 1320), (820, 1150), (1180, 1380), (1180, 2000), (-100, 2000)]), fill((130, 206, 110))); c.drawPath(smooth([(-100, 1640), (300, 1500), (700, 1560), (1180, 1480), (1180, 2000), (-100, 2000)]), fill((92, 176, 92)))
    for _ in range(30): x, y = r.uniform(0, W), r.uniform(1560, H); q = r.choice([(255, 110, 140), (255, 220, 70), (255, 255, 255)]); [c.drawCircle(x + cos(k * 1.257) * 14, y + sin(k * 1.257) * 14, 11, fill(q)) for k in range(5)]; c.drawCircle(x, y, 8, fill((255, 180, 40)))
    sk, pk, gold, red = (250, 176, 150), (255, 140, 150), (255, 200, 60), (230, 60, 60); c.drawOval(skia.Rect.MakeLTRB(180, 1590, 900, 1700), fill((30, 80, 50), .4, 10))
    for s in (-1, 1): flat(c, smooth([(540 + s * 40, 1480), (540 + s * 230, 1460), (540 + s * 300, 1560), (540 + s * 240, 1650), (540 + s * 60, 1640)]), (250, 190, 50)); flat(c, smooth([(540 + s * 170, 1600), (540 + s * 260, 1580), (540 + s * 330, 1630), (540 + s * 250, 1680), (540 + s * 160, 1670)]), sk); [c.drawCircle(540 + s * (290 + k * 12), 1652 - k * 16, 7, fill((255, 240, 230))) for k in range(3)]
    flat(c, oval(540, 1390, 290, 250), sk, off=(-20, -18)); c.drawCircle(540, 1450, 12, fill((200, 110, 100))); flat(c, smooth([(270, 1500), (540, 1570), (810, 1500), (800, 1580), (540, 1650), (280, 1580)]), (250, 190, 50)); c.drawPath(smooth([(330, 1230), (500, 1400), (620, 1600)], False), line((255, 255, 255), 12)); flat(c, smooth([(330, 1190), (540, 1290), (750, 1190), (760, 1230), (540, 1350), (320, 1230)]), gold); [c.drawCircle(400 + k * 70, 1244 + (40 - abs(2 - k) * 22), 15, fill([red, (60, 160, 200)][k % 2])) for k in range(5)]
    # arms: modak up, blessing
    flat(c, smooth([(300, 1220), (200, 1260), (120, 1180), (130, 1080), (200, 1070), (220, 1150), (330, 1170)]), sk); flat(c, smooth([(120, 1100), (100, 1010), (150, 960), (220, 1000), (226, 1090)]), sk); flat(c, smooth([(780, 1220), (890, 1280), (960, 1190), (940, 1100), (870, 1100), (850, 1170), (750, 1170)]), sk); flat(c, smooth([(860, 1120), (960, 1130), (980, 1060), (930, 1010), (860, 1040)]), sk)
    flat(c, smooth([(820, 1030), (850, 960), (920, 890), (980, 970), (1010, 1030), (920, 1060)]), (255, 236, 190)); [c.drawPath(smooth([(920, 896), (850 + k * 46, 980), (850 + k * 46, 1040)], False), line((220, 180, 120), 6)) for k in range(4)]
    c.drawCircle(160, 1030, 24, line((220, 60, 60), 8))
    # ears, head, trunk
    for s in (-1, 1): flat(c, smooth([(540 + s * 180, 760), (540 + s * 340, 660), (540 + s * 450, 760), (540 + s * 430, 930), (540 + s * 320, 1030), (540 + s * 200, 980)]), sk); c.drawPath(smooth([(540 + s * 220, 800), (540 + s * 330, 730), (540 + s * 400, 800), (540 + s * 370, 920), (540 + s * 260, 960)]), fill(pk)); c.drawCircle(540 + s * 330, 1010, 26, line(gold, 12))
    flat(c, smooth([(330, 860), (350, 700), (450, 620), (540, 606), (630, 620), (730, 700), (750, 860), (720, 1010), (620, 1100), (460, 1100), (360, 1010)]), sk, off=(-18, -16))
    flat(c, smooth([(440, 1010), (410, 1080), (440, 1130), (490, 1090)]), (255, 252, 240)); flat(c, smooth([(630, 1010), (690, 1050), (680, 1090), (610, 1080)]), (255, 252, 240)); q = smooth([(400, 1030), (460, 1110), (560, 1130), (640, 1100), (680, 1030), (600, 1070), (480, 1070)]); c.drawPath(q, fill((190, 60, 70)))
    flat(c, smooth([(456, 900), (446, 1020), (470, 1140), (560, 1230), (690, 1230), (740, 1150), (700, 1090), (650, 1120), (660, 1160), (600, 1150), (580, 1060), (630, 900), (540, 850)]), sk, off=(-14, -10)); [c.drawPath(smooth([(470 + k * 6, 960 + k * 56), (530 + k * 6, 976 + k * 52), (600 - k * 4, 956 + k * 50)], False), line((220, 130, 120), 7)) for k in range(4)]
    for s in (-1, 1): c.drawCircle(540 + s * 112, 840, 54, fill((255, 255, 255))); c.drawCircle(540 + s * 112, 840, 54, line((52, 26, 30), 7)); c.drawCircle(540 + s * 112 + 20, 846, 35, fill((60, 34, 30))); c.drawCircle(540 + s * 112 + 32, 832, 13, fill((255, 255, 255))); c.drawCircle(540 + s * 112 + 8, 860, 6, fill((255, 255, 255))); c.drawPath(smooth([(540 + s * 70, 764), (540 + s * 115, 742), (540 + s * 160, 766)], False), line((90, 50, 50), 13)); c.drawOval(skia.Rect.MakeLTRB(540 + s * 170 - 46, 920, 540 + s * 170 + 46, 974), fill((255, 110, 120), .55))
    for k in range(3): c.drawPath(smooth([(470, 700 + k * 26), (540, 692 + k * 26), (610, 700 + k * 26)], False), line((255, 255, 255), 10))
    c.drawPath(smooth([(540, 700), (554, 740), (540, 770), (526, 740)]), fill(red))
    flat(c, poly([(380, 670), (400, 520), (460, 580), (540, 430), (620, 580), (680, 520), (700, 670), (540, 630)]), gold); flat(c, smooth([(366, 690), (540, 626), (714, 690), (708, 640), (540, 580), (372, 640)]), red); [c.drawCircle(420 + k * 60, 642 - (30 - abs(2 - k) * 16), 14, fill([gold, (255, 255, 255)][k % 2])) for k in range(5)]; c.drawCircle(540, 520, 24, fill(red)); c.drawCircle(540, 430, 18, fill(red))
    # mouse stealing a modak
    g = (170, 160, 176); flat(c, smooth([(770, 1740), (790, 1630), (880, 1600), (960, 1650), (980, 1750), (870, 1780)]), g); [flat(c, oval(x, 1570, 42), g) or c.drawCircle(x, 1572, 24, fill(pk)) for x in (820, 930)]; flat(c, smooth([(800, 1650), (810, 1590), (880, 1570), (940, 1600), (950, 1650), (870, 1690)]), g); [c.drawCircle(x, 1626, 13, fill((40, 26, 30))) or c.drawCircle(x + 4, 1622, 4, fill((255, 255, 255))) for x in (846, 902)]; c.drawCircle(872, 1656, 11, fill((255, 110, 130))); c.drawPath(smooth([(970, 1750), (1040, 1760), (1050, 1690), (1020, 1660)], False), line((52, 26, 30), 14)); flat(c, smooth([(820, 1740), (850, 1690), (872, 1664), (900, 1690), (930, 1740)]), (255, 236, 190), 7)
    label(c, "BUDHVAAR", "GANESH LEELA", (255, 214, 80))

# ---------------- 4 Krishna: soft storybook, big-headed toddler, no outlines
def soft(c, path, rgb, d=.22): c.save(); c.clipPath(path, True); c.drawPaint(fill(rgb)); b = path.getBounds(); p = skia.Paint(Shader=skia.GradientShader.MakeLinear([skia.Point(b.left(), b.top()), skia.Point(b.right(), b.bottom())], [col(mix(rgb, (255, 255, 255), .28)), col(rgb), col(mix(rgb, (60, 10, 90), d))], [0, .45, 1])); c.drawPaint(p); c.restore()
def krishna(c):
    r = random.Random(9); vgrad(c, [(0, (255, 190, 160)), (.6, (255, 226, 180)), (1, (250, 200, 150))], 0, 1500); c.drawRect(skia.Rect.MakeLTRB(0, 0, W, 1480), fill((236, 170, 120), .5)); soft(c, poly([(0, 0), (W, 0), (W, 150), (0, 210)]), (150, 90, 60)); [soft(c, poly([(x, 0), (x + 60, 0), (x + 60, 1500), (x, 1500)]), (166, 104, 70)) for x in (20, 1000)]
    w = skia.Path(); w.moveTo(620, 1150); w.lineTo(620, 640); w.quadTo(770, 440, 920, 640); w.lineTo(920, 1150); w.close(); c.save(); c.clipPath(w, True); vgrad(c, [(0, (120, 200, 240)), (1, (200, 240, 210))], 440, 1150); c.drawPath(smooth([(560, 1050), (720, 940), (980, 1020), (980, 1200), (560, 1200)]), fill((120, 190, 110)))
    soft(c, smooth([(700, 1150), (690, 1000), (740, 930), (830, 930), (880, 1000), (870, 1150)]), (250, 246, 240)); [soft(c, smooth([(770 + s * 60, 950), (770 + s * 130, 930), (770 + s * 120, 980), (770 + s * 60, 990)]), (230, 180, 160)) for s in (-1, 1)]; [c.drawCircle(785 + s * 40, 1010, 12, fill((40, 26, 30))) for s in (-1, 1)]; soft(c, oval(785, 1090, 60, 42), (250, 190, 180)); [c.drawCircle(785 + s * 22, 1086, 8, fill((160, 80, 90))) for s in (-1, 1)]; [c.drawPath(smooth([(785 + s * 50, 930), (785 + s * 80, 870), (785 + s * 60, 840)], False), line((200, 170, 130), 18)) for s in (-1, 1)]; c.restore(); c.drawPath(w, line((150, 90, 60), 22))
    soft(c, poly([(0, 1480), (W, 1440), (W, H), (0, H)]), (206, 140, 96)); [c.drawOval(skia.Rect.MakeXYWH(r.uniform(0, W), r.uniform(1500, H), 70, 18), fill((170, 106, 70), .35)) for _ in range(30)]
    # hanging, broken pot
    c.drawLine(300, 0, 300, 420, line((140, 90, 50), 10)); [c.drawLine(300, 400, 300 + q * 120, 560, line((140, 90, 50), 8)) for q in (-1, 1)]; pot = smooth([(180, 560), (420, 560), (400, 600), (470, 700), (420, 800), (300, 830), (180, 800), (130, 700), (200, 600)]); soft(c, pot, (206, 100, 60)); [c.drawPath(smooth([(140, 680 + k * 40), (300, 712 + k * 40), (460, 680 + k * 40)], False), line((255, 226, 160), 7)) for k in range(2)]; cr = smooth([(330, 830), (350, 740), (390, 770), (440, 730), (460, 780), (400, 830)]); c.drawPath(cr, fill((90, 40, 30))); mk = smooth([(340, 800), (390, 780), (420, 800), (424, 900), (410, 1010), (390, 1040), (376, 980), (360, 900)]); soft(c, mk, (255, 250, 232), .1)
    # Kanha
    sk = (112, 160, 226); c.drawOval(skia.Rect.MakeLTRB(250, 1660, 850, 1770), fill((90, 40, 30), .4, 14))
    soft(c, smooth([(290, 1700), (310, 1590), (440, 1540), (600, 1560), (600, 1680), (440, 1740)]), sk); soft(c, smooth([(820, 1700), (800, 1580), (660, 1540), (520, 1560), (520, 1680), (660, 1740)]), sk); [soft(c, oval(x, 1704, 66, 46), sk) for x in (300, 810)]; [c.drawPath(smooth([(x - 60, 1660), (x, 1640), (x + 60, 1660)], False), line((255, 204, 70), 16)) for x in (320, 790)]
    soft(c, smooth([(400, 1640), (390, 1440), (440, 1300), (550, 1270), (660, 1300), (710, 1440), (700, 1640), (550, 1690)]), sk); soft(c, smooth([(370, 1580), (550, 1520), (730, 1580), (740, 1680), (550, 1730), (360, 1680)]), (255, 190, 40)); c.drawPath(smooth([(370, 1580), (550, 1530), (730, 1580)], False), line((220, 60, 60), 18)); c.drawCircle(550, 1488, 9, fill((70, 100, 170)))
    c.drawPath(smooth([(430, 1300), (550, 1420), (670, 1300)], False), line((255, 250, 240), 13)); c.drawPath(smooth([(420, 1310), (550, 1470), (680, 1310)], False), line((255, 204, 70), 9))
    soft(c, smooth([(430, 1340), (340, 1400), (300, 1480), (360, 1530), (430, 1480), (470, 1420)]), sk); pt2 = smooth([(250, 1530), (430, 1530), (420, 1560), (470, 1630), (430, 1710), (340, 1730), (250, 1710), (210, 1630), (260, 1560)]); soft(c, pt2, (214, 110, 64)); soft(c, smooth([(256, 1536), (290, 1490), (340, 1476), (400, 1494), (426, 1536), (340, 1556)]), (255, 250, 232), .1); c.drawPath(smooth([(224, 1620), (340, 1646), (456, 1620)], False), line((255, 226, 160), 7)); soft(c, oval(392, 1512, 36, 30), sk)
    soft(c, smooth([(660, 1340), (770, 1360), (820, 1280), (760, 1200), (700, 1210), (720, 1270), (640, 1290)]), sk); soft(c, oval(730, 1200, 42, 38), sk); soft(c, smooth([(690, 1190), (700, 1150), (750, 1150), (760, 1190), (726, 1210)]), (255, 250, 232), .1)
    soft(c, smooth([(270, 930), (300, 750), (430, 650), (560, 630), (700, 660), (810, 760), (830, 930), (800, 1060), (760, 1110), (330, 1110), (290, 1060)]), (44, 28, 52)); [soft(c, oval(540 + cos(a) * 280, 930 + sin(a) * 270, 64), (44, 28, 52)) for a in [pi * k / 8 for k in range(8, 17)]]
    [soft(c, oval(x, 1040, 44, 58), sk) for x in (320, 780)]; [c.drawCircle(x, 1104, 18, fill((255, 204, 70))) for x in (316, 784)]
    soft(c, smooth([(330, 960), (350, 840), (440, 780), (550, 770), (660, 780), (750, 840), (770, 960), (760, 1120), (680, 1240), (550, 1280), (420, 1240), (340, 1120)]), sk, .16)
    [soft(c, smooth([(540 + a, 800), (500 + a, 770), (470 + a, 820), (500 + a, 880), (540 + a, 850)]), (44, 28, 52)) for a in (-90, -10, 90, 150)]
    for s, look in ((-1, 16), (1, 16)):
        x = 550 + s * 104; c.drawOval(skia.Rect.MakeLTRB(x - 62, 950, x + 62, 1090), fill((255, 255, 255))); c.drawOval(skia.Rect.MakeLTRB(x - 40 + look, 972, x + 44 + look, 1086), fill((70, 40, 40))); c.drawOval(skia.Rect.MakeLTRB(x - 20 + look, 1000, x + 26 + look, 1070), fill((20, 10, 20))); c.drawCircle(x + 18 + look, 1000, 18, fill((255, 255, 255))); c.drawCircle(x - 8 + look, 1060, 8, fill((255, 255, 255))); c.drawPath(smooth([(x - 66, 1000), (x - 30, 946), (x + 30, 942), (x + 70, 984)], False), line((40, 20, 40), 13)); c.drawPath(smooth([(x - 50, 900 + (10 if s < 0 else -14)), (x, 880), (x + 50, 904 - (10 if s > 0 else 0))], False), line((44, 28, 52), 13)); c.drawOval(skia.Rect.MakeLTRB(x + s * 40 - 50, 1110, x + s * 40 + 50, 1170), fill((255, 130, 160), .55))
    c.drawPath(smooth([(536, 1098), (550, 1112), (566, 1098)], False), line((70, 100, 180), 9)); q = smooth([(470, 1150), (550, 1170), (640, 1144), (600, 1216), (530, 1220)]); c.drawPath(q, fill((170, 40, 70))); c.save(); c.clipPath(q, True); c.drawOval(skia.Rect.MakeLTRB(510, 1190, 610, 1250), fill((255, 120, 130))); c.drawRect(skia.Rect.MakeLTRB(530, 1150, 580, 1176), fill((255, 255, 255))); c.restore()
    for x, y, k in ((440, 1190, 34), (650, 1200, 30), (480, 1232, 24), (600, 1244, 28)): c.drawOval(skia.Rect.MakeLTRB(x - k, y - k * .7, x + k, y + k * .7), fill((255, 250, 232)))
    c.drawPath(smooth([(532, 860), (540, 930), (550, 940), (560, 930), (568, 860)], False), line((255, 220, 90), 10)); c.drawCircle(550, 920, 9, fill((220, 50, 60)))
    c.drawPath(smooth([(320, 840), (440, 740), (560, 716), (680, 744), (780, 840)], False), line((255, 204, 70), 34)); [c.drawCircle(400 + k * 60, 782 - (46 - abs(2.5 - k) * 18), 12, fill([(220, 50, 70), (60, 170, 150)][k % 2])) for k in range(6)]
    fe = smooth([(620, 720), (640, 560), (720, 470), (790, 520), (770, 620), (690, 720)]); soft(c, fe, (40, 150, 110)); [c.drawOval(skia.Rect.MakeLTRB(724 - a, 560 - b, 724 + a, 560 + b), fill(q)) for a, b, q in ((46, 54, (230, 190, 70)), (34, 40, (40, 120, 190)), (18, 22, (30, 30, 90)))]
    label(c, "GURUVAAR", "KRISHNA LEELA", (255, 224, 110))

# ---------------- 5 Bhakt: Shabari, Indian miniature
def bhakt(c):
    r = random.Random(3); PAL = dict(a=(150, 34, 40), b=(236, 180, 80), c=(30, 92, 84)); vgrad(c, [(0, (236, 196, 120)), (1, (250, 230, 180))], 0, 1400); c.drawPath(smooth([(-60, 1200), (200, 1060), (560, 1140), (860, 1040), (1160, 1160), (1160, 2000), (-60, 2000)]), fill((150, 176, 110))); c.drawPath(smooth([(-60, 1420), (300, 1330), (760, 1370), (1160, 1320), (1160, 2000), (-60, 2000)]), fill((176, 190, 120)))
    for x, y, h in ((150, 1330, 760), (940, 1340, 880), (560, 1180, 420)):
        c.drawPath(smooth([(x - 26, y), (x - 10, y - h * .5), (x - 8, y - h), (x + 8, y - h), (x + 16, y - h * .5), (x + 30, y)]), fill((104, 62, 44)))
        for k in range(46):
            a, q = r.uniform(0, 2 * pi), r.uniform(0, 1) ** .5; lx, ly = x + cos(a) * q * 190, y - h + sin(a) * q * 150; g = r.choice([(50, 100, 60), (70, 126, 70), (40, 84, 56)]); c.save(); c.translate(lx, ly); c.rotate(math.degrees(a)); p = smooth([(-34, 0), (0, -17), (34, 0), (0, 17)]); c.drawPath(p, fill(g)); c.drawPath(p, line((30, 56, 40), 3)); c.drawLine(-26, 0, 26, 0, line((150, 180, 100), 2)); c.restore()
        [c.drawCircle(x + r.uniform(-160, 160), y - h + r.uniform(-120, 130), 11, fill((200, 60, 40))) for _ in range(12)]
    hut = poly([(590, 1340), (590, 1060), (860, 1060), (860, 1340)]); c.drawPath(hut, fill((206, 160, 110))); c.drawPath(hut, line((90, 46, 30), 5)); rf = poly([(540, 1090), (725, 880), (910, 1090)]); c.drawPath(rf, fill((190, 150, 70))); [c.drawLine(725, 886, 550 + k * 44, 1088, line((130, 94, 40), 4)) for k in range(9)]; c.drawPath(rf, line((90, 46, 30), 5)); c.drawRect(skia.Rect.MakeLTRB(680, 1150, 770, 1340), fill((90, 46, 36))); [c.drawPath(poly([(600 + k * 40, 1120), (618 + k * 40, 1100), (636 + k * 40, 1120)]), fill((250, 240, 220))) for k in range(6)]
    for _ in range(60): x, y = r.uniform(80, 1000), r.uniform(1400, 1800); [c.drawLine(x, y, x + q * 9, y - 26, line((90, 130, 70), 4)) for q in (-1, 0, 1)]; (r.random() < .4) and c.drawCircle(x, y - 30, 8, fill(r.choice([(214, 70, 80), (250, 240, 220), (236, 180, 60)])))
    base = random.Random(6); ram = dict(pp.person(base, "kisan", "miniature", dict(a=(214, 110, 40), b=(240, 190, 80), c=(214, 110, 40))), skin=(104, 150, 190), hat="jata", beard=0, must=0, bottom="dhoti", top=1, prop=None, wide=.95, tilak=3, nose=26, eye=28, ear=1, jaw=80)
    shab = dict(pp.person(base, "bala", "miniature", dict(a=(238, 226, 200), b=(200, 150, 90), c=(206, 190, 160))), skin=(150, 100, 70), hat="veil", prop=None, nose=20, jaw=74, wide=.95, tall=.86, neck=0, ear=0, eye=22, top=2, pat=1)
    pp.puppet(c, ram, 330, 1640, 1.16, 1.0, 1, 0, "happy", (.7, 1.75)); glow(c, 330, 720, 260, (255, 240, 160), .7); pp.puppet(c, ram, 330, 1640, 1.16, 1.0, 1, 0, "happy", (.7, 1.75)); pp.puppet(c, shab, 770, 1640, 1.1, 1.3, -1, 0, "happy", (.9, 1.5))
    [c.drawLine(706 + k * 9, 968 + k * 22, 734 + k * 3, 960 + k * 22, line((110, 66, 46), 4)) for k in range(0)]
    b = smooth([(480, 1190), (640, 1190), (620, 1270), (500, 1270)]); [c.drawCircle(500 + k * 24, 1180 - (k % 2) * 16, 17, fill((190, 60, 40))) or c.drawCircle(496 + k * 24, 1174 - (k % 2) * 16, 5, fill((255, 190, 150))) for k in range(6)]; c.drawPath(b, fill((190, 140, 70))); [c.drawLine(490 + k * 22, 1200, 506 + k * 18, 1266, line((120, 80, 36), 4)) for k in range(7)]; c.drawPath(b, line((90, 46, 30), 5))
    pp.surface(c, "miniature", PAL, random.Random(1)); label(c, "SHUKRAVAAR", "BHAKTON KI GATHA", (255, 214, 120), 130)

# ---------------- 6 Mahabharat: layered paper-cut
def horse(c, x, y, s, rgb, k=0.):
    c.save(); c.translate(x, y); c.scale(s, s); q = mix(rgb, (120, 60, 50), .18)
    for a, l in (((-150, -120), [(-150, -130), (-230, -60), (-260, 40), (-220, 50), (-180, -20), (-100, -90)]), (0, [(120, -110), (230, -90), (300, -10), (270, 20), (210, -40), (90, -60)])): paper(c, smooth(l), q, 8)
    paper(c, smooth([(-230, -230), (-320, -240), (-390, -130), (-340, -160), (-240, -180)]), (70, 40, 44), 8); paper(c, smooth([(-240, -200), (-180, -290), (0, -270), (130, -310), (210, -430), (280, -520), (350, -500), (400, -440), (420, -400), (380, -380), (320, -410), (280, -330), (240, -180), (160, -90), (0, -70), (-160, -90)]), rgb)
    paper(c, smooth([(250, -530), (190, -480), (120, -400), (60, -320), (130, -330), (220, -400), (290, -480)]), (70, 40, 44), 6); paper(c, poly([(290, -520), (300, -580), (326, -512)]), rgb, 5); c.drawCircle(340, -452, 9, fill((40, 16, 24))); c.drawPath(smooth([(300, -480), (330, -420), (390, -404)], False), line((200, 50, 50), 9)); c.drawPath(smooth([(230, -400), (270, -320), (250, -220)], False), line((230, 170, 60), 14))
    for l in ([(-110, -120), (-120, -30), (-200, 60), (-160, 80), (-70, 0), (-40, -110)], [(160, -140), (290, -150), (350, -60), (320, -40), (260, -90), (140, -80)]): paper(c, smooth(l), rgb, 8)
    paper(c, smooth([(-120, -270), (40, -268), (60, -140), (-110, -130)]), (190, 40, 50), 6); c.drawPath(smooth([(-112, -150), (60, -156)], False), line((240, 190, 80), 9)); c.restore()
def mahabharat(c):
    r = random.Random(2); c.drawColor(col((240, 180, 96)))
    for i, (R, rgb) in enumerate(((900, (236, 160, 80)), (700, (240, 138, 66)), (520, (244, 176, 80)), (350, (252, 214, 120)))): paper(c, oval(540, 720, R), rgb, 16)
    for i, (y, rgb) in enumerate(((1060, (206, 104, 70)), (1180, (176, 74, 62)), (1300, (146, 50, 56)))):
        for k in range(26): x = r.uniform(-20, W + 20); h = r.uniform(120, 330); c.drawLine(x, y + 40, x + r.uniform(-30, 30), y - h, line(mix(rgb, (60, 10, 30), .35), 7)); (k % 3 == 0) and paper(c, poly([(x, y - h), (x + 80, y - h + 24), (x, y - h + 56)]), mix(rgb, (255, 220, 120), .25), 5, False)
        paper(c, smooth([(-80, y + 40), (100, y - 30), (330, y + 20), (560, y - 40), (800, y + 14), (1160, y - 30), (1160, 2100), (-80, 2100)]), rgb, 14)
    # chariot
    paper(c, poly([(150, 560), (170, 560), (190, 1200), (166, 1200)]), (110, 50, 40), 8); paper(c, smooth([(160, 500), (330, 470), (440, 540), (330, 560), (400, 640), (250, 640), (166, 660)]), (214, 60, 50)); c.save(); c.translate(250, 566); c.drawCircle(0, 0, 34, fill((250, 190, 70))); [c.drawLine(cos(a) * 42, sin(a) * 42, cos(a) * 58, sin(a) * 58, line((250, 190, 70), 8)) for a in [k * pi / 4 for k in range(8)]]; c.restore()
    paper(c, smooth([(40, 840), (260, 720), (480, 840), (440, 870), (260, 800), (80, 870)]), (190, 44, 54)); [paper(c, poly([(x, 850), (x + 18, 850), (x + 18, 1260), (x, 1260)]), (230, 170, 60), 6) for x in (70, 440)]
    horse(c, 800, 1500, .92, (236, 220, 200));
    # Arjun
    def man(x, y, s, skin, cloth, hair, crown, up):
        c.save(); c.translate(x, y); c.scale(s, s); paper(c, smooth([(-90, 0), (-110, -170), (-80, -330), (0, -360), (90, -330), (110, -170), (90, 0)]), cloth); paper(c, smooth([(-70, -190), (-84, -320), (0, -352), (84, -320), (70, -190), (0, -170)]), skin, 6); paper(c, poly([(-70, -330), (-30, -344), (84, -180), (40, -166)]), (240, 190, 70), 5); up()
        paper(c, smooth([(-70, -400), (-90, -500), (-50, -580), (30, -590), (80, -540), (84, -500), (110, -470), (84, -452), (80, -410), (30, -372), (-40, -376)]), skin, 8); paper(c, smooth([(-80, -380), (-110, -500), (-60, -600), (40, -600), (76, -556), (0, -540), (-30, -480), (-40, -390)]), hair, 6); c.drawPath(smooth([(30, -500), (54, -512), (80, -500), (54, -490)]), fill((255, 250, 235))); c.drawCircle(60, -500, 8, fill((30, 10, 20))); c.drawPath(smooth([(24, -526), (52, -538), (84, -524)], False), line((40, 16, 24), 8)); c.drawPath(smooth([(92, -432), (66, -424), (54, -430)], False), line((140, 40, 50), 6)); paper(c, oval(-14, -474, 16, 24), skin, 4); crown(); c.restore()
    def bow():
        q = skia.Path(); q.moveTo(170, -640); q.cubicTo(330, -540, 250, -400, 260, -330); q.cubicTo(250, -260, 330, -120, 170, -20); c.save(); c.translate(6, 10); c.drawPath(q, line((20, 4, 10), 22, .4)); c.restore(); c.drawPath(q, line((250, 200, 80), 22)); c.drawPath(poly([(170, -640), (-30, -330), (170, -20)], False), line((255, 250, 230), 4)); c.drawLine(-40, -330, 360, -330, line((255, 240, 200), 8)); c.drawPath(poly([(400, -330), (346, -350), (346, -310)]), fill((255, 250, 235))); paper(c, smooth([(40, -356), (160, -350), (270, -350), (276, -312), (160, -300), (40, -290)]), (206, 150, 110), 6); paper(c, smooth([(-60, -330), (-160, -300), (-120, -250), (-40, -310), (-24, -340)]), (206, 150, 110), 6)
    def crA(): paper(c, poly([(-84, -570), (-90, -670), (-40, -620), (0, -720), (40, -630), (90, -680), (86, -560), (0, -580)]), (246, 196, 70), 6); c.drawCircle(0, -630, 13, fill((200, 40, 60)))
    man(230, 1300, .98, (206, 150, 110), (60, 110, 130), (46, 24, 30), crA, bow)
    paper(c, smooth([(30, 1230), (520, 1230), (640, 1200), (620, 1330), (480, 1420), (90, 1420)]), (206, 140, 50)); [c.drawCircle(120 + k * 74, 1320, 22, fill([(190, 40, 50), (40, 110, 110)][k % 2])) for k in range(6)]
    def rein(): [c.drawPath(smooth([(150, -200 + k * 16), (320, -170), (520, -230 + k * 20)], False), line((90, 40, 36), 7)) for k in (0, 1)]; paper(c, smooth([(50, -310), (130, -250), (190, -190), (160, -150), (90, -200), (30, -250)]), (70, 120, 180), 6)
    def crK(): paper(c, poly([(-84, -560), (-76, -650), (0, -700), (76, -640), (84, -556), (0, -580)]), (246, 196, 70), 6); paper(c, smooth([(20, -680), (30, -770), (84, -820), (120, -760), (80, -690)]), (30, 130, 100), 5); c.drawCircle(80, -764, 22, fill((240, 190, 70))); c.drawCircle(80, -764, 12, fill((30, 60, 150)))
    man(520, 1300, .72, (70, 120, 180), (250, 190, 50), (30, 18, 34), crK, rein)
    paper(c, smooth([(440, 1260), (640, 1230), (640, 1330), (480, 1390), (420, 1380)]), (206, 140, 50), 8)
    for x, R in ((220, 190),):
        paper(c, oval(x, 1520, R), (120, 54, 40), 14); paper(c, oval(x, 1520, R - 34), (226, 160, 60), 6); c.drawCircle(x, 1520, R - 60, fill((140, 50, 54))); [c.drawLine(x, 1520, x + cos(a) * (R - 40), 1520 + sin(a) * (R - 40), line((240, 190, 80), 16)) for a in [k * pi / 5 for k in range(10)]]; paper(c, oval(x, 1520, 44), (240, 190, 80), 6)
    horse(c, 690, 1610, 1.0, (255, 246, 230)); paper(c, smooth([(-80, 1740), (200, 1690), (520, 1730), (860, 1680), (1160, 1720), (1160, 2100), (-80, 2100)]), (96, 26, 44), 16); [paper(c, oval(r.uniform(0, 700), 1700 + r.uniform(-20, 40), r.uniform(26, 60)), (200, 130, 90), 5) for _ in range(12)]
    vig(c, .35); label(c, "SHANIVAAR", "MAHABHARAT", (255, 206, 100))

# ---------------- 7 Paheli: glowing silhouette and clue cards
def paheli(c):
    r = random.Random(5); vgrad(c, [(0, (28, 10, 70)), (.5, (90, 30, 140)), (1, (20, 8, 50))], 0, H)
    for i in range(24): a = i * pi / 12; c.drawPath(poly([(540, 860), (540 + cos(a) * 1600, 860 + sin(a) * 1600), (540 + cos(a + .13) * 1600, 860 + sin(a + .13) * 1600)]), fill((255, 120, 220), .10))
    glow(c, 540, 860, 620, (255, 200, 110), .95); c.drawCircle(540, 860, 360, fill((255, 226, 150))); c.drawCircle(540, 860, 390, line((255, 226, 150), 6, .7)); B = (34, 10, 60)
    S = lambda p: c.drawPath(p, fill(B)); S(smooth([(330, 1290), (350, 1130), (440, 1060), (540, 1040), (640, 1060), (730, 1130), (760, 1290)])); S(poly([(500, 940), (580, 940), (590, 1070), (490, 1070)])); S(smooth([(440, 830), (450, 720), (540, 670), (620, 700), (644, 780), (672, 830), (646, 850), (644, 890), (600, 950), (520, 966), (460, 920)])); S(smooth([(440, 800), (420, 720), (460, 640), (540, 620), (620, 650), (630, 720), (540, 700), (480, 760)])); S(smooth([(500, 650), (480, 570), (540, 520), (600, 570), (580, 650)])); c.drawLine(490, 636, 592, 636, line((255, 190, 80), 10)); c.drawPath(smooth([(440, 860), (426, 900), (446, 920)], False), line((255, 200, 90), 7))
    # veena and khartal
    c.drawLine(250, 1230, 800, 640, line(B, 26)); S(oval(290, 1190, 96)); S(oval(770, 680, 70)); [c.drawLine(300 + k * 7, 1200 + k * 5, 776 + k * 5, 664 + k * 6, line((255, 200, 110), 3)) for k in range(3)]; S(smooth([(430, 1110), (340, 1080), (380, 1010), (470, 1070)])); S(smooth([(650, 1110), (790, 1060), (830, 930), (870, 900), (880, 960), (820, 1100), (700, 1200)])); [c.drawOval(skia.Rect.MakeLTRB(836 + k * 10, 868 + k * 34, 930 + k * 10, 894 + k * 34), fill(B)) for k in (0, 1)]
    f = lambda s, b=BLACK: skia.Font(skia.Typeface.MakeFromFile(b), s); T = lambda s, y, z, rgb, b=BLACK, x=540: c.drawString(s, x - f(z, b).measureText(s) / 2, y, f(z, b), fill(rgb))
    c.drawCircle(880, 520, 92, fill((230, 40, 90))); T("?", 572, 150, (255, 255, 255), x=880); T("PEHCHANO KAUN?", 1400, 104, (255, 214, 80))
    for i, (n, s) in enumerate((("1", "Haath mein veena"), ("2", "Teeno lok mein ghoomte hain"), ("3", "Mukh par ek hi naam..."))):
        y = 1450 + i * 120; c.drawRoundRect(skia.Rect.MakeLTRB(110, y, 970, y + 98), 49, 49, fill((255, 255, 255), .14)); c.drawRoundRect(skia.Rect.MakeLTRB(110, y, 970, y + 98), 49, 49, line((255, 214, 120), 4, .8)); c.drawCircle(160, y + 49, 38, fill((255, 190, 60))); T(n, y + 67, 52, (50, 10, 60), x=160); g = f(46, BOLD); c.drawString(s, 226, y + 65, g, fill((255, 255, 255)))
    c.drawCircle(160, 400, 80, fill((255, 255, 255), .14)); c.drawArc(skia.Rect.MakeLTRB(80, 320, 240, 480), -90, 250, False, line((90, 240, 160), 14)); T("5", 428, 84, (255, 255, 255), x=160)
    for _ in range(80): c.drawCircle(r.uniform(0, W), r.uniform(0, H), r.uniform(1, 5), fill((255, 230, 160), r.uniform(.3, 1)))
    vig(c, .5); label(c, "RAVIVAAR", "PAHELI AUR RAHASYA", (255, 160, 220))

ALL = dict(somvaar_shiv=shiv, mangalvaar_ramayan=ramayan, budhvaar_ganesh=ganesh, guruvaar_krishna=krishna, shukravaar_bhakt=bhakt, shanivaar_mahabharat=mahabharat, ravivaar_paheli=paheli)
if __name__ == "__main__":
    sh = Image.new("RGB", (4 * 480, 2 * 853), (20, 14, 30))
    for i, (n, fn) in enumerate(ALL.items()):
        s = skia.Surface(W, H); fn(s.getCanvas()); im = Image.fromarray(s.toarray(colorType=skia.kRGBA_8888_ColorType)).convert("RGB"); im.save(f"{OUT}/{i + 1}_{n}.png"); sh.paste(im.resize((480, 853)), (i % 4 * 480 + (240 if i > 3 else 0), i // 4 * 853))
    sh.save(f"{OUT}/preview.jpg", quality=92)
