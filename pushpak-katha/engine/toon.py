"""Cartoon library: one rig for all upright animals (lion, elephant, monkey, fox, rabbit) + jungle scenery."""
from race import *          # drawing helpers, tree, clouds, confetti, zzz ...

KIND = dict(
    lion=dict(fur=(244, 186, 84), belly=(255, 228, 170), wide=1.12, tail=(150, 78, 34)),
    elephant=dict(fur=(150, 166, 196), belly=(196, 206, 226), wide=1.35, tail=(120, 136, 170)),
    monkey=dict(fur=(150, 96, 60), belly=(244, 204, 160), wide=.86, tail=(150, 96, 60)),
    fox=dict(fur=(238, 124, 52), belly=(255, 238, 220), wide=.88, tail=(238, 124, 52)),
    rabbit=dict(fur=(214, 196, 214), belly=(250, 244, 250), wide=.95, tail=(250, 244, 250)))
HIP = 1.0

def brows(c, xs, y, w, mood):
    for i, x in enumerate(xs):
        k = -1 if i == 0 else 1
        a, b = dict(angry=(-18, 16), worried=(14, -14), sad=(14, -14), shock=(-22, -22), smug=(-6, 8), laugh=(-12, -12)).get(mood, (0, 0))
        if mood in ("angry", "worried", "sad", "shock", "smug"):      # outer end a, inner end b
            c.drawLine(x + k * w, y + a, x - k * w, y + b, line(INK, 11))

def arm(c, x, y, pose, side, t, w, rgb, talk=0):
    """side -1 = left (behind), 1 = right."""
    k = side; sw = sin(t * 2.2 + side) * 6; tk = talk * 22
    P = dict(rest=[(x, y), (x + k * 44, y + 60), (x + k * 34 + sw, y + 122)], hips=[(x, y), (x + k * 84, y + 46), (x + k * 26, y + 96)],
             point=[(x, y), (x + 70, y + 6 - tk), (x + 168, y - 34 - tk)], up=[(x, y), (x + k * 66, y - 54), (x + k * 62 + sw * 2, y - 150)],
             cheer=[(x, y), (x + k * 70, y - 50), (x + k * 74, y - 140 + sin(t * 11 + side) * 26)], beg=[(x, y), (x + k * 34, y + 52), (x + k * 2 + 22, y + 6 + sw)],
             talk=[(x, y), (x + k * 74, y + 30), (x + k * 104, y - 26 - tk * 1.6)], fear=[(x, y), (x + k * 40, y + 20), (x - k * 6, y - 62 + sin(t * 30) * 3)],
             think=[(x, y), (x + k * 40, y + 56), (x + 10, y - 30)])[pose]
    limb(c, P, w, rgb); c.drawCircle(*P[-1], w * .62, fill(INK)); c.drawCircle(*P[-1], w * .62 - 6, fill(rgb))

def beast(c, kind, x, y, s, t, talk=0., mood="n", d=1, pose="rest", walk=False, run=False, sit=False):
    K_ = KIND[kind]; fur, belly, wd = K_["fur"], K_["belly"], K_["wide"]; dark = mix(fur, (70, 30, 90), .22)
    c.save(); c.translate(x, y); c.scale(s * d, s); c.drawOval(skia.Rect.MakeLTRB(-130 * wd, -14, 130 * wd, 18), fill((20, 40, 20), .25))
    ph = t * (14 if run else 7); amp = 90 if run else 48 if walk else 0; a = sin(ph) * amp
    bob = -abs(sin(ph)) * (34 if run else 12) if amp else sin(t * 2.3) * 4
    sq = 1 + .035 * talk + (.03 * sin(t * 20) if mood == "laugh" else 0) + (.02 * sin(t * 2.3)); c.translate(0, bob)
    if mood == "fear" or mood == "worried": c.translate(sin(t * 34) * 2.5, 0)
    if run: c.rotate(13)
    # tail
    tw = sin(t * 3) * 24
    if kind == "rabbit": cel(c, oval(-100, -110, 34), belly)
    elif kind == "fox":
        cel(c, smooth([(-60, -110), (-170, -90), (-236, -190 + tw), (-190, -290 + tw), (-140, -200 + tw), (-70, -160)]), fur); cel(c, smooth([(-214, -220 + tw), (-236, -250 + tw), (-190, -296 + tw), (-172, -236 + tw)]), belly, w=5)
    elif kind == "monkey": limb(c, [(-60, -100), (-170, -80), (-200, -190 + tw), (-140, -250 + tw), (-120, -200 + tw)], 20, fur)
    else:
        limb(c, [(-80, -110), (-160, -110), (-190, -200 + tw)], 16 if kind == "lion" else 13, fur); cel(c, oval(-192, -214 + tw, 28 if kind == "lion" else 15, 34 if kind == "lion" else 18), K_["tail"])
    bw, lw = 98 * wd, 46 * (1.25 if kind == "elephant" else 1)
    limb(c, [(-30 * wd, -110), (-32 * wd - a * .5, -60), (-36 * wd - a, -16 - max(0, a) * .4)], lw, dark); cel(c, oval(-24 * wd - a, -14 - max(0, a) * .4, 48 * wd, 22), dark)
    ax, ay = 62 * wd, -262
    if pose in ("fear", "beg", "cheer", "up", "rest", "hips", "think", "talk", "point"):
        back = dict(point="hips", think="hips", talk="rest", up="rest").get(pose, pose); back = "rest" if run else back
        arm(c, -ax, ay, back, -1, t, 34, dark)
    c.save(); c.translate(0, -60); c.scale(2 - sq, sq); c.translate(0, 60)
    cel(c, smooth([(-.62 * bw, -300), (.62 * bw, -300), (1.04 * bw, -170), (.9 * bw, -70), (0, -44), (-.9 * bw, -70), (-1.06 * bw, -170)]), fur)
    c.drawPath(oval(16, -152, 58 * wd, 84), fill(belly)); c.restore()
    limb(c, [(34 * wd, -110), (36 * wd + a * .5, -60), (44 * wd + a, -16 - max(0, -a) * .4)], lw, fur); cel(c, oval(58 * wd + a, -14 - max(0, -a) * .4, 52 * wd, 23), fur)
    # head
    c.save(); c.translate(6, -372); c.rotate(sin(t * 2.1) * 2.2 + (-7 if mood == "laugh" else 0) + (6 if mood in ("sad", "worried") else 0)); c.scale(1.02 - .02 * talk, 1 + .03 * talk)
    ex, ey, er, my, mw = (-30, 56), -24, 34, 56, 36
    if kind == "lion":
        n = 15; R = [(1 + .06 * sin(t * 3 + i)) * (192 if i % 2 else 160) for i in range(n * 2)]
        cel(c, smooth([(R[i] * cos(i * pi / n), 6 + R[i] * sin(i * pi / n)) for i in range(n * 2)]), (158, 82, 36), .25, off=(-14, -16))
        for k in (-1, 1): cel(c, oval(k * 92, -96, 36), fur); c.drawPath(oval(k * 92, -92, 18), fill((214, 130, 90)))
        cel(c, smooth([(-112, -60), (0, -122), (112, -60), (116, 40), (60, 104), (-60, 104), (-116, 40)]), fur); c.drawPath(oval(16, 58, 72, 50), fill(belly))
        cel(c, smooth([(-18, 10), (48, 10), (16, 46)]), (96, 44, 40), w=4)
        if mood == "angry":
            for k in (-1, 1): pass
    elif kind == "elephant":
        fl = sin(t * 2.6) * 10
        for k in (-1, 1):
            cel(c, smooth([(k * 80, -110), (k * 200, -130 + fl), (k * 246, -20 + fl), (k * 196, 96 + fl), (k * 90, 70)]), fur, .25); c.drawPath(smooth([(k * 110, -70), (k * 180, -84 + fl), (k * 206, -10 + fl), (k * 170, 60 + fl), (k * 110, 40)]), fill((226, 170, 186)))
        cel(c, smooth([(-112, -70), (0, -140), (112, -70), (116, 40), (60, 96), (-60, 96), (-116, 40)]), fur)
        my, mw = 88, 24
    elif kind == "monkey":
        for k in (-1, 1): cel(c, oval(k * 116, -8, 42), fur); c.drawPath(oval(k * 116, -8, 24), fill(belly))
        cel(c, smooth([(-110, -70), (0, -136), (110, -70), (112, 30), (60, 98), (-60, 98), (-112, 30)]), fur)
        c.drawPath(smooth([(-92, -40), (-40, -84), (12, -50), (66, -84), (104, -40), (84, 50), (14, 96), (-60, 60)]), fill(belly)); er = 30
        for k in (2, 26): c.drawPath(oval(k, 26, 5, 7), fill(INK))
        cel(c, smooth([(-20, -118), (-34, -170), (4, -146), (24, -178), (34, -118)]), fur, w=6)
    elif kind == "fox":
        for k in (-1, 1): cel(c, smooth([(k * 30, -86), (k * 88, -210), (k * 122, -60)]), fur); c.drawPath(smooth([(k * 58, -94), (k * 88, -166), (k * 104, -78)]), fill((90, 40, 40)))
        cel(c, smooth([(-118, -50), (0, -124), (118, -50), (130, 34), (40, 106), (-40, 106), (-130, 34)]), fur)
        c.save(); c.clipPath(smooth([(-118, -50), (0, -124), (118, -50), (130, 34), (40, 106), (-40, 106), (-130, 34)]), True); c.drawPath(oval(-84, 80, 92, 74), fill(belly)); c.drawPath(oval(104, 80, 84, 74), fill(belly)); c.restore()
        c.drawPath(oval(14, 22, 20, 15), fill(INK)); my = 52
    else:
        sw = sin(t * 3) * 10 + (-60 if run else 0) + (46 if mood in ("sad", "worried") else 0)
        for exx, _ in ((-46, 1), (36, .6)):
            cel(c, smooth([(exx - 34, -70), (exx - 42 + sw * .5, -220), (exx + sw, -300), (exx + 40 + sw * .5, -210), (exx + 34, -70)]), fur)
            c.drawPath(smooth([(exx - 14, -90), (exx - 20 + sw * .5, -200), (exx + sw * .9, -262), (exx + 20 + sw * .5, -195), (exx + 14, -90)]), fill((255, 160, 178)))
        cel(c, smooth([(-118, -70), (0, -138), (118, -70), (128, 30), (70, 100), (-70, 100), (-126, 30)]), fur); c.drawPath(oval(24, 48, 78, 46), fill(belly))
        c.drawPath(smooth([(4, 12), (34, 12), (20, 34)]), fill((255, 120, 150))); my = 50
    c.drawPath(oval(-76, 34, 24, 15), fill((255, 110, 120), .45)); c.drawPath(oval(100, 34, 18, 14), fill((255, 110, 120), .45))
    em = dict(laugh="happy" if int(t * 2) % 2 else "n", worried="shock" if talk > .3 else "n", angry="n").get(mood, mood)
    for i, xx in enumerate(ex): eye(c, xx, ey, er, (.5, .1 if mood != "sad" else .6), t, em, hash(kind) % 7 * .3 if False else len(kind) * .37)
    brows(c, ex, ey - er - 20, 30, mood)
    if kind == "elephant":
        u = (-60 * talk) + sin(t * 2) * 10 + (-120 if mood == "happy" else 0); mouth(c, 46, my, mw, talk, mood)
        pth = [(8, 4), (14, 90), (30, 170 + u * .3), (96, 190 + u)]; limb(c, pth, 52, fur)
        for q in range(3): c.drawLine(-12 + q * 3, 70 + q * 32, 34 + q * 4, 66 + q * 32, line(dark, 6))
        for tx in (-36, 62): cel(c, smooth([(tx - 12, 70), (tx + 14, 70), (tx + 22, 128), (tx + 6, 124)]), (255, 250, 232), w=5)
    else:
        mouth(c, 16 if kind != "rabbit" else 24, my, mw * (1.35 if kind == "lion" and (talk > .3 or mood == "roar") else 1), max(talk, 1 if mood == "roar" else 0), mood)
        if kind == "lion" and (talk > .15 or mood == "roar"):
            for k in (-16, 48): c.drawPath(poly([(k - 8, my), (k + 8, my), (k, my + 26)]), fill((255, 255, 255)))
        if kind == "rabbit" and (talk > .08 or mood in ("laugh", "shock")):
            rc = skia.Rect.MakeLTRB(13, my - 2, 36, my + 18); c.drawRect(rc, fill((255, 255, 255))); c.drawRect(rc, line(INK, 4))
    c.restore()
    if mood in ("worried", "shock"):
        for i in range(3):
            u = (t * 1.3 + i / 3) % 1; c.drawPath(oval(-130 - 34 * u, -470 + i * 46 - 30 * u, 8, 13), fill((120, 200, 255), 1 - u))
    if pose in ("rest", "hips", "cheer", "point", "talk", "beg", "up", "fear", "think"): arm(c, ax, ay, pose if not run else "rest", 1, t, 34, fur, talk)
    c.restore()

# ---------------- scenery
PAL = dict(day=dict(sky=((70, 176, 240), (190, 232, 250), (255, 246, 214)), sun=(255, 226, 90), far=((150, 205, 190), (126, 198, 140), (104, 184, 100)), leaf=((86, 170, 74), (120, 184, 70), (66, 152, 96)), grass=((140, 206, 92), (70, 148, 66)), path=(238, 206, 150), tint=None),
           jungle=dict(sky=((32, 120, 120), (120, 200, 150), (240, 246, 190)), sun=(255, 246, 180), far=((110, 190, 150), (70, 160, 116), (44, 130, 92)), leaf=((34, 120, 74), (60, 146, 70), (24, 104, 88)), grass=((96, 176, 82), (34, 104, 62)), path=(206, 170, 112), tint=None),
           sunset=dict(sky=((110, 60, 150), (250, 130, 110), (255, 214, 130)), sun=(255, 232, 150), far=((206, 120, 130), (160, 92, 120), (120, 80, 100)), leaf=((170, 110, 50), (190, 140, 50), (130, 100, 60)), grass=((190, 160, 80), (110, 90, 60)), path=(240, 190, 130), tint=None))

def scene(c, pal, t, scroll=0, gy=1290, trees=4, dense=False):
    P = PAL[pal]; c.drawColor(col(P["sky"][0])); vgrad(c, [(0, P["sky"][0]), (.55, P["sky"][1]), (1, P["sky"][2])], -400, gy)
    glow(c, 820, 420, 420, P["sun"], .9); c.drawCircle(820, 420, 96, fill(P["sun"]))
    if not dense:
        for i in range(5):
            x = (i * 330 - scroll * .08 + t * 8) % 1650 - 250; y = 330 + (i * 137) % 330
            for a, b, r in ((-70, 10, 46), (0, -16, 66), (74, 8, 50)): c.drawCircle(x + a, y + b, r, fill((255, 255, 255), .85))
            c.drawRoundRect(skia.Rect.MakeLTRB(x - 116, y + 6, x + 124, y + 58), 26, 26, fill((255, 255, 255), .85))
    for k, (sp, base, amp) in enumerate(((.15, 1000, 90), (.3, 1100, 70), (.5, 1190, 50))):
        c.drawPath(poly([(-200, gy + 20)] + [(x, base + amp * sin((x + scroll * sp) * .0046 + k * 2) + amp * .4 * sin((x + scroll * sp) * .011 + k)) for x in range(-200, W + 220, 20)] + [(W + 220, gy + 20)]), fill(P["far"][k]))
        if dense:
            for i in range(9):
                x = (i * 170 + k * 60 - scroll * sp) % 1530 - 220; h = 420 - k * 60; c.drawRect(skia.Rect.MakeLTRB(x - 14, base - h, x + 14, gy), fill(mix(P["far"][k], (30, 50, 50), .35)))
                c.drawOval(skia.Rect.MakeLTRB(x - 130, base - h - 130, x + 130, base - h + 60), fill(mix(P["far"][k], P["leaf"][k], .4)))
    if dense:
        for i in range(5):
            x0 = 500 + i * 120; c.drawPath(poly([(x0, -100), (x0 + 60, -100), (x0 - 360 + 30 * sin(t + i), gy), (x0 - 520, gy)]), fill((255, 250, 190), .07))
    for i in range(trees):
        x = (i * 2240 / trees + 300 - scroll * .62) % 2240 - 500; tree(c, x, gy + 10, .66, t, P["leaf"][i % 3])
    vgrad_ = skia.Paint(Shader=skia.GradientShader.MakeLinear([skia.Point(0, gy), skia.Point(0, H)], [col(P["grass"][0]), col(P["grass"][1])])); c.drawRect(skia.Rect.MakeLTRB(-400, gy, W + 400, H + 600), vgrad_)
    c.drawRect(skia.Rect.MakeLTRB(-400, gy + 60, W + 400, gy + 260), fill(P["path"])); c.drawRect(skia.Rect.MakeLTRB(-400, gy + 60, W + 400, gy + 74), fill(mix(P["path"], (90, 50, 30), .25)))
    for i in range(16):
        x = (i * 131 - scroll) % 2096 - 400; y = gy + 110 + (i * 53) % 120; c.drawOval(skia.Rect.MakeLTRB(x, y, x + 44, y + 14), fill(mix(P["path"], (90, 50, 30), .25)))
    for i in range(16):
        x = (i * 157 - scroll * 1.05) % 2198 - 400; y = gy + 330 + (i * 97) % 300; g = mix(P["grass"][1], (10, 40, 20), .25)
        for b in (-16, 0, 16): c.drawPath(poly([(x + b - 8, y), (x + b * 1.7 + 4 * sin(t * 2 + i), y - 48), (x + b + 8, y)]), fill(g))
        if i % 3 == 0:
            for q in range(5): c.drawCircle(x + 60 + 15 * cos(q * 1.257), y - 20 + 15 * sin(q * 1.257), 11, fill(((255, 120, 160), (255, 255, 255), (255, 214, 80))[i % 9 // 3]))
            c.drawCircle(x + 60, y - 20, 8, fill((255, 200, 40)))

def cave(c, x, y, s):
    c.save(); c.translate(x, y); c.scale(s, s); cel(c, smooth([(-420, 40), (-400, -260), (-220, -520), (60, -580), (300, -440), (420, -180), (430, 40)]), (150, 136, 140), .3, off=(-30, -30))
    c.drawPath(smooth([(-220, 30), (-230, -180), (-80, -360), (120, -350), (240, -160), (230, 30)]), fill((46, 34, 48)))
    for a, b, r in ((-300, -200, 34), (260, -330, 28), (-120, -450, 24), (340, -90, 30)): c.drawPath(oval(a, b, r, r * .7), fill((120, 106, 116)))
    c.restore()

def well(c, x, y, s, front=False):
    c.save(); c.translate(x, y); c.scale(s, s)
    if not front:
        for k in (-1, 1): cel(c, poly([(k * 200 - 16, 0), (k * 200 + 16, 0), (k * 200 + 16, -520), (k * 200 - 16, -520)]), (150, 98, 62))
        cel(c, poly([(-270, -500), (0, -640), (270, -500)]), (206, 92, 70)); c.drawOval(skia.Rect.MakeLTRB(-210, -220, 210, -120), fill((40, 60, 90))); c.drawOval(skia.Rect.MakeLTRB(-210, -220, 210, -120), line(INK, 8))
    else:
        p = skia.Path(); p.moveTo(-220, -170); p.quadTo(0, -60, 220, -170); p.lineTo(206, 20); p.quadTo(0, 90, -206, 20); p.close(); cel(c, p, (168, 160, 166), .25, off=(-30, -10)); c.save(); c.clipPath(p, True)
        for r in range(4):
            for q in range(-4, 5): c.drawRoundRect(skia.Rect.MakeLTRB(q * 92 + (r % 2) * 46 - 42, -150 + r * 58 + 14, q * 92 + (r % 2) * 46 + 42, -150 + r * 58 + 62), 12, 12, line((110, 100, 110), 5))
        c.restore()
    c.restore()
def stars_burst(c, x, y, r, t, n=12, rgb=(255, 240, 120)):
    c.drawPath(poly([(x + (r if i % 2 else r * .62) * cos(i * pi / n + t), y + (r if i % 2 else r * .62) * sin(i * pi / n + t)) for i in range(n * 2)]), fill(rgb))
def shake(c, t, a): c.translate(sin(t * 61) * a, cos(t * 53) * a)
