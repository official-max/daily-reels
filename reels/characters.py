"""Cartoon characters built from cached, shaded sprite layers.

Speakers/characters:  K Shri Krishna, A Arjun, P ordinary man,  R Raja, C Chatur (clever man), G guard.
char() draws one character for one frame: body layers + arms in a pose + head + blinking eyes + lip-synced mouth.
"""
import math
import numpy as np
from .config import SS, BLINK_OFF
from .util import clamp, lerp, darker, cubic, blink
from .canvas import sprite, put, E, POLY, LINE, ARC, CHORD, ribbon


GOLD = (242, 188, 64); RED = (210, 40, 60)

GOLD = (242, 188, 64); RED = (210, 40, 60)

C = {
    "K": dict(skin=(88, 136, 222), skin_d=(55, 92, 175), hair=(28, 22, 44), dhoti=(252, 196, 40), pleat=(255, 214, 80), border=RED),
    "A": dict(skin=(238, 192, 152), skin_d=(190, 140, 106), hair=(34, 24, 22), dhoti=(246, 240, 226), pleat=(255, 251, 242), border=(196, 52, 58), top=(150, 36, 50)),
    "P": dict(skin=(186, 136, 98), skin_d=(140, 98, 68), hair=(108, 104, 104), dhoti=(128, 104, 82), pleat=(142, 118, 94), border=(98, 78, 60), top=(196, 186, 160)),
    "R": dict(skin=(232, 186, 142), skin_d=(186, 136, 98), hair=(30, 22, 22), dhoti=(186, 30, 46), pleat=(206, 48, 62), border=GOLD, top=(196, 34, 50), legs=(186, 30, 46), feet=(200, 150, 50)),
    "C": dict(skin=(206, 152, 110), skin_d=(160, 112, 78), hair=(28, 22, 22), dhoti=(244, 234, 210), pleat=(252, 246, 230), border=(226, 120, 40), top=(246, 238, 216), legs=(244, 236, 218), feet=(120, 74, 44)),
    "G": dict(skin=(196, 142, 100), skin_d=(150, 104, 72), hair=(28, 22, 22), dhoti=(140, 30, 40), pleat=(160, 40, 50), border=(110, 20, 30), top=(176, 184, 196), legs=(140, 30, 40), feet=(80, 54, 36)),
}

def L_back(cv, who, uy):
    c = C[who]; m = cv.mask
    if who == "K":
        cv.soft(m(lambda d: E(cv, d, 0, -440 + uy, 210)), (255, 230, 160), 0.6, 40)
        path = cubic((40, -320 + uy), (150, -330 + uy), (140, -190 + uy), (200, -140 + uy), 30)
        cv.part(m(lambda d: POLY(cv, d, ribbon(path, 28, 52))), (248, 140, 60), sh=0.5, rim=0.7)
    if who in ("K", "A"):
        bot = -280 if who == "K" else -318
        cv.part(m(lambda d: POLY(cv, d, [(-80, -440 + uy), (80, -440 + uy), (98, -360 + uy), (96, bot - 12 + uy), (70, bot + uy), (-70, bot + uy), (-96, bot - 12 + uy), (-98, -360 + uy)])), c["hair"], sh=0.3, hl=0.15, rim=0.5)
    if who == "A":
        cv.part(m(lambda d: POLY(cv, d, ribbon([(-36, -300 + uy), (-100, -440 + uy)], 34, 40))), (120, 76, 40), sh=0.45, rim=0.6)
        for k in range(3):
            x0 = -84 - k*12 + 6
            cv.part(m(lambda d, x0=x0: LINE(cv, d, [(x0 + 10, -420 + uy), (x0, -478 + uy)], 4)), (170, 130, 80), sh=0.2, cast=0)
            cv.part(m(lambda d, x0=x0: POLY(cv, d, [(x0 - 8, -470 + uy), (x0 + 8, -470 + uy), (x0, -500 + uy)])), (225, 60, 60), sh=0.3, cast=0)
        bow = cubic((100, -392 + uy), (196, -320 + uy), (160, -170 + uy), (66, -116 + uy), 30)
        cv.part(m(lambda d: POLY(cv, d, ribbon(bow, 14, 14))), (130, 78, 36), sh=0.45, hl=0.35, gloss=0.2, rim=0.7)
        cv.flat(m(lambda d: LINE(cv, d, [(100, -392 + uy), (66, -116 + uy)], 2, caps=False)), (240, 230, 205))
        for pt in ((100, -392), (66, -116)): cv.part(m(lambda d, pt=pt: E(cv, d, pt[0], pt[1] + uy, 9)), GOLD, gloss=0.6)
    if who == "R":
        cv.part(m(lambda d: POLY(cv, d, [(-70, -336 + uy), (70, -336 + uy), (132, -40), (-132, -40)])), (140, 18, 34), sh=0.5, hl=0.2, rim=0.6)
        cv.part(m(lambda d: LINE(cv, d, [(-132, -44), (132, -44)], 10)), GOLD, sh=0.3, gloss=0.4, cast=0)
    if who == "G":
        cv.part(m(lambda d: LINE(cv, d, [(112, -660), (112, 10)], 12)), (120, 82, 50), sh=0.45, hl=0.3, rim=0.6)
        cv.part(m(lambda d: POLY(cv, d, [(112, -715), (134, -650), (112, -628), (90, -650)])), (215, 222, 232), sh=0.3, hl=0.5, gloss=0.6, rim=0.8)

def L_lower(cv, who, ph, sit):
    c = C[who]; m = cv.mask
    if sit:
        cv.part(m(lambda d: E(cv, d, 0, -42, 114, 42)), c["dhoti"], sh=0.45, hl=0.25)
        for s in (-1, 1): cv.part(m(lambda d, s=s: E(cv, d, s*74, -20, 30, 13)), c["skin"], sh=0.35)
        return
    sw = math.sin(ph) * 16 if ph is not None else 0
    sway = math.sin(ph) * 6 if ph is not None else 0
    for s, s_ in ((-1, sw), (1, -sw)):
        cv.part(m(lambda d, s=s, s_=s_: LINE(cv, d, [(s*24, -170), (s*27 + s_, -24)], 30)), c.get("legs", c["skin"]), sh=0.45)
        cv.part(m(lambda d, s=s, s_=s_: E(cv, d, s*31 + s_, -12, 30, 13)), c.get("feet", c["skin"]), sh=0.35)
        if who == "K": cv.part(m(lambda d, s=s, s_=s_: E(cv, d, s*27 + s_, -34, 17, 6)), GOLD, sh=0.3, hl=0.5, gloss=0.5, rim=0.8)
    hem = [(-66, -206), (66, -206), (80, -130), (90 + sway, -64), (60 + sway, -52), (30 + sway, -58), (0 + sway, -54), (-30 + sway, -58), (-60 + sway, -52), (-90 + sway, -64), (-80, -130)]
    cv.part(m(lambda d: POLY(cv, d, hem)), c["dhoti"], sh=0.45, hl=0.3)
    cv.part(m(lambda d: POLY(cv, d, [(-16, -200), (16, -200), (24 + sway, -58), (-24 + sway, -58)])), c["pleat"], sh=0.35, cast=0.2)
    for x0 in (-40, 40): cv.flat(m(lambda d, x0=x0: LINE(cv, d, [(x0*0.6, -190), (x0 + sway, -70)], 3)), darker(c["dhoti"], 0.8), alpha=0.7)
    band = [(-90 + sway, -64), (-60 + sway, -52), (0 + sway, -56), (60 + sway, -52), (90 + sway, -64), (88 + sway, -80), (0 + sway, -74), (-88 + sway, -80)]
    cv.part(m(lambda d: POLY(cv, d, band)), c["border"], sh=0.3, hl=0.3)
    if who in ("K", "A", "R"):
        cv.part(m(lambda d: POLY(cv, d, [(-88 + sway, -78), (0 + sway, -72), (88 + sway, -78), (87 + sway, -85), (0 + sway, -79), (-87 + sway, -85)])), GOLD, sh=0, hl=0.3, gloss=0.4, cast=0)

def L_upper(cv, who, uy):
    c = C[who]; m = cv.mask; Y = lambda pts: [(x, y + uy) for x, y in pts]
    top = c.get("top", c["skin"])
    if who == "P":
        cv.part(m(lambda d: (POLY(cv, d, Y([(-62, -334), (62, -334), (68, -150), (44, -162), (22, -146), (0, -160), (-22, -146), (-44, -162), (-68, -150)])),
                             E(cv, d, -58, -320 + uy, 27), E(cv, d, 58, -320 + uy, 27))), top, sh=0.45, hl=0.25)
        cv.part(m(lambda d: E(cv, d, -28, -262 + uy, 16, 12)), (160, 140, 110), sh=0.35, cast=0.2)
        cv.part(m(lambda d: E(cv, d, 30, -196 + uy, 13, 10)), (176, 160, 128), sh=0.35, cast=0.2)
        cv.part(m(lambda d: LINE(cv, d, Y([(-62, -218), (0, -212), (62, -218)]), 7)), (120, 92, 60), sh=0.3)
        cv.flat(m(lambda d: LINE(cv, d, Y([(18, -300), (26, -280), (18, -266)]), 2.5)), (140, 130, 110))
    else:
        cv.part(m(lambda d: (POLY(cv, d, Y([(-62, -334), (62, -334), (56, -200), (-56, -200)])), E(cv, d, -58, -320 + uy, 26), E(cv, d, 58, -320 + uy, 26))),
                top, sh=0.5, hl=0.3)
    cv.soft(m(lambda d: E(cv, d, 0, -336 + uy, 36, 12)), (20, 20, 40), 0.35, 4)
    if who == "R":
        cv.part(m(lambda d: LINE(cv, d, Y([(0, -330), (0, -205)]), 6)), GOLD, sh=0.2, cast=0)
        for r_, col in ((30, GOLD), (46, (255, 236, 190))):
            for i in range(13):
                u = i / 12
                cv.part(m(lambda d, u=u, r_=r_: E(cv, d, lerp(-40, 40, u), -330 + r_*math.sin(math.pi*u) + uy, 5)), col, sh=0.3, hl=0.4, gloss=0.6, cast=0.15)
        cv.part(m(lambda d: E(cv, d, 0, -276 + uy, 15)), GOLD, sh=0.3, gloss=0.7)
        cv.part(m(lambda d: E(cv, d, 0, -276 + uy, 7)), (40, 170, 110), gloss=0.9, cast=0)
        cv.part(m(lambda d: POLY(cv, d, Y([(-58, -222), (58, -222), (60, -200), (-60, -200)]))), GOLD, sh=0.35, hl=0.4, gloss=0.5)
    if who == "C":
        cv.part(m(lambda d: POLY(cv, d, Y([(-64, -330), (-36, -338), (60, -212), (34, -202)]))), (232, 118, 40), sh=0.45, hl=0.3)
    if who == "G":
        cv.part(m(lambda d: E(cv, d, 0, -270 + uy, 30, 34)), (210, 216, 226), sh=0.4, hl=0.5, gloss=0.5)
        cv.part(m(lambda d: E(cv, d, 0, -270 + uy, 13)), GOLD, gloss=0.7, cast=0.1)
        cv.part(m(lambda d: POLY(cv, d, Y([(-58, -222), (58, -222), (60, -202), (-60, -202)]))), (110, 70, 40), sh=0.35, hl=0.2)
    if who == "K":
        cv.part(m(lambda d: POLY(cv, d, Y([(-60, -222), (60, -222), (62, -198), (-62, -198)]))), GOLD, sh=0.35, hl=0.4, gloss=0.5)
        for i, x in enumerate((-36, 0, 36)):
            cv.part(m(lambda d, x=x: E(cv, d, x, -210 + uy, 7, 8)), (RED, (40, 170, 110), RED)[i], sh=0.3, gloss=0.8, cast=0.15)
        cv.part(m(lambda d: POLY(cv, d, Y([(-64, -326), (-38, -336), (60, -214), (36, -204)]))), (236, 70, 110), sh=0.45, hl=0.3)
        cv.part(m(lambda d: LINE(cv, d, Y([(-54, -238), (52, -162)]), 14)), (196, 136, 64), sh=0.45, hl=0.4, gloss=0.3, cast=0.4)
        for u in (0.1, 0.9):
            cv.part(m(lambda d, u=u: E(cv, d, lerp(-54, 52, u), lerp(-238, -162, u) + uy, 8, 8)), GOLD, gloss=0.6, cast=0)
        for r_, col in ((26, GOLD), (40, (255, 240, 205))):
            for i in range(13):
                u = i / 12
                cv.part(m(lambda d, u=u, r_=r_: E(cv, d, lerp(-38, 38, u), -330 + r_*math.sin(math.pi*u) + uy, 5)), col, sh=0.35, hl=0.4, gloss=0.6, cast=0.15)
        fl = [(255, 248, 245), (240, 60, 100), (255, 196, 50)]
        for i in range(23):
            u = i / 22
            cv.part(m(lambda d, u=u: E(cv, d, lerp(-50, 50, u), -330 + 175*math.sin(math.pi*u) + uy, 9)), fl[i % 3], sh=0.4, hl=0.3, cast=0.25)
    if who == "A":
        cv.part(m(lambda d: LINE(cv, d, Y([(-42, -332), (0, -300), (42, -332)]), 7)), GOLD, sh=0.3, hl=0.4, gloss=0.5)
        cv.part(m(lambda d: E(cv, d, 0, -266 + uy, 20)), GOLD, sh=0.4, hl=0.4, gloss=0.6)
        cv.part(m(lambda d: E(cv, d, 0, -266 + uy, 9)), RED, gloss=0.9, cast=0.2)
        cv.part(m(lambda d: POLY(cv, d, Y([(-60, -224), (60, -224), (62, -198), (-62, -198)]))), GOLD, sh=0.35, hl=0.4, gloss=0.5)
        cv.part(m(lambda d: E(cv, d, 0, -211 + uy, 9)), RED, gloss=0.9, cast=0.1)
        for i in range(5):
            x = -48 + i * 24
            cv.part(m(lambda d, x=x: POLY(cv, d, Y([(x - 10, -198), (x + 10, -198), (x + 8, -168), (x - 8, -168)]))), (GOLD if i % 2 else (150, 36, 50)), sh=0.35, cast=0.3)
        for i in range(11):
            u = i / 10
            cv.part(m(lambda d, u=u: E(cv, d, lerp(-30, 30, u), -330 + 18*math.sin(math.pi*u) + uy, 4.5)), GOLD, gloss=0.6, cast=0.1)

ARM_POSES = {}

def arm_geom(pose, g, ph):
    swing = math.sin(ph) * 14 if ph is not None else 0
    L = [(-58, -318), (-82, -250), (-76 + swing, -180)]; R = [(58, -318), (82, -250), (76 - swing, -180)]
    if pose == "talk": L = [(-58, -318), (-98, -254), (-50 + g*0.4, -284 + g)]
    elif pose == "bless": L = [(-58, -318), (-112, -284), (-102 + g*0.3, -372 + g*0.4)]
    elif pose == "namaste": L = [(-58, -318), (-80, -246), (-9, -286)]; R = [(58, -318), (80, -246), (9, -286)]
    elif pose == "wipe": L = [(-58, -318), (-92, -272), (-34, -398)]
    elif pose == "point": R = [(58, -318), (124, -298), (192, -326)]
    elif pose == "think": L = [(-58, -318), (-74, -238), (-16, -322)]
    elif pose == "victory": L = [(-58, -318), (-104, -404), (-92, -500)]; R = [(58, -318), (104, -404), (92, -500)]
    return L, R

def L_arms(cv, who, uy, pose, g, ph):
    c = C[who]; m = cv.mask; sk = c["skin"]
    L, R = arm_geom(pose, g, ph)
    Y = lambda pts: [(x, y + uy) for x, y in pts]
    for arm in (R, L):
        a = Y(arm)
        if who in ("R", "C", "G"):
            cv.part(m(lambda d, a=a: LINE(cv, d, a, 28)), c["top"], sh=0.45, cast=0.3)
            if who == "R":
                b = (lerp(a[1][0], a[2][0], 0.85), lerp(a[1][1], a[2][1], 0.85))
                cv.part(m(lambda d, b=b: E(cv, d, b[0], b[1], 16, 9)), GOLD, gloss=0.6, cast=0.2)
        elif who == "P":
            cv.part(m(lambda d, a=a: LINE(cv, d, a[:2], 31)), c["top"], sh=0.45, cast=0.3)
            cv.part(m(lambda d, a=a: LINE(cv, d, a[1:], 24)), sk, sh=0.45, cast=0.3)
        else:
            cv.part(m(lambda d, a=a: LINE(cv, d, a, 26)), sk, sh=0.45, cast=0.35)
            mid = ((a[0][0] + a[1][0]) / 2, (a[0][1] + a[1][1]) / 2)
            cv.part(m(lambda d, mid=mid: E(cv, d, mid[0], mid[1], 16, 9)), GOLD, sh=0.3, hl=0.4, gloss=0.6)
            if who == "A":
                fa = (lerp(a[1][0], a[2][0], 0.35), lerp(a[1][1], a[2][1], 0.35)), (lerp(a[1][0], a[2][0], 0.85), lerp(a[1][1], a[2][1], 0.85))
                cv.part(m(lambda d, fa=fa: LINE(cv, d, list(fa), 30)), (120, 72, 40), sh=0.45, hl=0.3, cast=0.2)
            else:
                b = (lerp(a[1][0], a[2][0], 0.85), lerp(a[1][1], a[2][1], 0.85))
                cv.part(m(lambda d, b=b: E(cv, d, b[0], b[1], 15, 8)), GOLD, gloss=0.6, cast=0.2)
        hx, hy = a[2]
        if pose == "bless" and arm is L:
            cv.part(m(lambda d: (E(cv, d, hx, hy - 8, 19, 24), [E(cv, d, hx - 12 + f*8, hy - 30, 5, 9) for f in range(4)])), sk, sh=0.35, hl=0.3, cast=0.3)
            if who == "K": cv.flat(m(lambda d: E(cv, d, hx, hy - 6, 4)), (225, 40, 60))
        else:
            cv.part(m(lambda d, hx=hx, hy=hy: E(cv, d, hx, hy, 16, 15)), sk, sh=0.4, hl=0.3, cast=0.3)
    if pose == "namaste":
        cv.part(m(lambda d: POLY(cv, d, Y([(-17, -266), (17, -266), (0, -330)]))), sk, sh=0.4, hl=0.3, cast=0.3)

def L_head(cv, who, uy):
    c = C[who]; m = cv.mask; sk, skd = c["skin"], c["skin_d"]; hy = -410 + uy
    cv.part(m(lambda d: POLY(cv, d, [(-18, hy + 50), (18, hy + 50), (18, hy + 84), (-18, hy + 84)])), skd, sh=0.3, hl=0.1, rim=0.3)
    for s in (-1, 1): cv.part(m(lambda d, s=s: E(cv, d, s*80, hy + 6, 16, 21)), sk, sh=0.45)
    cv.part(m(lambda d: E(cv, d, 0, hy, 82, 86)), sk, sh=0.42, hl=0.32, rim=0.65, cast=0.3)
    for s in (-1, 1):
        if who == "K":
            cv.part(m(lambda d, s=s: E(cv, d, s*82, hy + 42, 10, 17)), GOLD, sh=0.3, hl=0.5, gloss=0.7, cast=0.3)
            cv.part(m(lambda d, s=s: E(cv, d, s*82, hy + 60, 6)), RED, gloss=0.8, cast=0)
        elif who == "A":
            cv.part(m(lambda d, s=s: E(cv, d, s*82, hy + 30, 8)), GOLD, gloss=0.7, cast=0.2)
        if who != "P":
            cv.soft(m(lambda d, s=s: E(cv, d, s*50, hy + 36, 15, 9)), (255, 120, 160), 0.33, 5)
    cv.flat(m(lambda d: ARC(cv, d, 0, hy + 34, 6, 5, 20, 160, 3)), skd, alpha=0.8)
    if who == "P":
        cv.soft(m(lambda d: CHORD(cv, d, 0, hy + 4, 78, 80, 20, 160)), (70, 60, 55), 0.35, 3)
        for k in range(2): cv.flat(m(lambda d, k=k: ARC(cv, d, 0, hy - 40 + k*10, 30, 8, 200, 340, 2)), skd, alpha=0.6)
        def hp(d):
            CHORD(cv, d, 0, hy, 86, 88, 205, 335)
            for dx, dy, r in ((-60, -50, 24), (-30, -72, 26), (0, -80, 26), (30, -74, 24), (60, -54, 22), (-78, -20, 16), (78, -22, 16)):
                E(cv, d, dx, hy + dy, r)
        cv.part(m(hp), c["hair"], sh=0.35, hl=0.25, rim=0.6, cast=0.4)
        return
    if who in ("R", "C", "G"):
        def hp(d):
            CHORD(cv, d, 0, hy - 4, 86, 86, 200, 340)
            for s in (-1, 1): POLY(cv, d, [(s*72, hy - 44), (s*90, hy - 12), (s*88, hy + 14), (s*76, hy - 4)])
        cv.part(m(hp), c["hair"], sh=0.35, hl=0.22, rim=0.7, cast=0.4)
        if who == "C":
            cv.flat(m(lambda d: E(cv, d, 0, hy - 30, 6)), (215, 40, 50))
        if who == "R":
            for s in (-1, 1):
                must = cubic((s*4, hy + 36), (s*40, hy + 26), (s*66, hy + 48), (s*84, hy + 16), 16)
                cv.part(m(lambda d, must=must: POLY(cv, d, ribbon(must, 22, 6))), (28, 20, 20), sh=0.3, hl=0.2, rim=0.5, cast=0.3)
            cv.part(m(lambda d: POLY(cv, d, [(-80, hy - 60), (80, hy - 60), (76, hy - 34), (-76, hy - 34)])), GOLD, sh=0.4, hl=0.45, gloss=0.6, rim=0.8)
            for x, hh in ((-60, 40), (-30, 56), (0, 76), (30, 56), (60, 40)):
                cv.part(m(lambda d, x=x, hh=hh: POLY(cv, d, [(x - 16, hy - 60), (x, hy - 60 - hh), (x + 16, hy - 60)])), GOLD, sh=0.45, hl=0.45, gloss=0.5, rim=0.8)
                cv.part(m(lambda d, x=x, hh=hh: E(cv, d, x, hy - 60 - hh + 8, 6)), (255, 245, 220), gloss=0.8, cast=0.1)
            cv.part(m(lambda d: E(cv, d, 0, hy - 47, 10, 9)), RED, gloss=1.0, cast=0.1)
            for x in (-44, 44): cv.part(m(lambda d, x=x: E(cv, d, x, hy - 47, 6)), (40, 170, 110), gloss=0.9, cast=0.1)
        if who == "G":
            cv.part(m(lambda d: CHORD(cv, d, 0, hy - 2, 92, 96, 190, 350)), (196, 204, 216), sh=0.4, hl=0.5, gloss=0.6, rim=0.8)
            cv.part(m(lambda d: POLY(cv, d, [(-8, hy - 30), (8, hy - 30), (6, hy + 30), (-6, hy + 30)])), (176, 184, 196), sh=0.3, hl=0.4, gloss=0.4)
            cv.part(m(lambda d: POLY(cv, d, [(-10, hy - 92), (10, hy - 92), (0, hy - 130)])), GOLD, gloss=0.6)
        return
    def hair_front(d):
        CHORD(cv, d, 0, hy - 5, 86, 85, 200, 340)
        n = 9 if who == "K" else 7
        for i in range(n):
            x = lerp(-72, 72, i / (n - 1)); E(cv, d, x, hy - 42 + 14 * (x / 72) ** 2, 17 if who == "K" else 20, 15)
        if who == "K":
            for s in (-1, 1):
                for j in range(6): E(cv, d, s*(78 + j*2.4), hy - 20 + j*24, 18 - j*0.8, 16)
        else:
            for s in (-1, 1): POLY(cv, d, [(s*70, hy - 40), (s*92, hy - 10), (s*96, hy + 70), (s*78, hy + 40)])
    cv.part(m(hair_front), c["hair"], sh=0.35, hl=0.22, rim=0.7, cast=0.4)
    if who == "K":
        cv.flat(m(lambda d: LINE(cv, d, [(-9, hy - 42), (-7, hy - 20), (0, hy - 15), (7, hy - 20), (9, hy - 42)], 3.5)), (255, 242, 200))
        cv.flat(m(lambda d: LINE(cv, d, [(0, hy - 40), (0, hy - 22)], 3.5)), (225, 30, 50))
        a = math.radians(12); ux, uy_ = math.sin(a), -math.cos(a)
        bx, by = 10, hy - 118; L = 230
        vp = [(bx + ux*L*u, by + uy_*L*u) for u in np.linspace(0.18, 1.0, 30)]
        Lp, Rp = [], []
        for i, (x, y) in enumerate(vp):
            w_ = 46 * math.sin(math.pi * i / 29) ** 0.6; Lp.append((x - uy_*w_, y + ux*w_)); Rp.append((x + uy_*w_, y - ux*w_))
        cv.part(m(lambda d: POLY(cv, d, Lp + Rp[::-1])), grad=((60, 200, 150), (20, 110, 70)), sh=0.35, hl=0.35, rim=0.8, cast=0.25)
        def barbs(d):
            for j in range(40):
                u = 0.22 + 0.76 * j / 39; w_ = 46 * math.sin(math.pi * (u - 0.18) / 0.82) ** 0.6
                cx_, cy_ = bx + ux*L*u, by + uy_*L*u
                for sg in (-1, 1):
                    d.line([cv.P(cx_, cy_), cv.P(cx_ - uy_*w_*sg + ux*w_*0.4, cy_ + ux*w_*sg + uy_*w_*0.4)], fill=255, width=max(1, int(1.2*cv.s)))
        cv.flat(m(barbs), (190, 240, 170), alpha=0.45)
        cv.flat(m(lambda d: LINE(cv, d, [(bx, by), (bx + ux*L, by + uy_*L)], 2.5)), (235, 225, 175))
        ex_, ey_ = bx + ux*L*0.78, by + uy_*L*0.78
        for r_, col, g_ in ((30, (236, 190, 60), 0.4), (23, (24, 160, 160), 0.3), (16, (30, 70, 190), 0.7), (8, (12, 20, 66), 0.2)):
            cv.part(m(lambda d, r_=r_: E(cv, d, ex_, ey_, r_, r_*1.2)), col, sh=0.3, hl=0.3, gloss=g_, rim=0.4, cast=0.1)
        for s in (-1, 1):
            cv.part(m(lambda d, s=s: POLY(cv, d, cubic((s*40, hy - 60), (s*58, hy - 110), (s*84, hy - 104), (s*80, hy - 60), 16))), GOLD, sh=0.4, hl=0.4, gloss=0.4, rim=0.8)
        cv.part(m(lambda d: POLY(cv, d, cubic((-46, hy - 60), (-48, hy - 118), (48, hy - 118), (46, hy - 60), 24))), GOLD, sh=0.45, hl=0.45, gloss=0.5, rim=0.8)
        cv.part(m(lambda d: POLY(cv, d, cubic((-26, hy - 68), (-28, hy - 102), (28, hy - 102), (26, hy - 68), 20))), (255, 214, 110), sh=0.3, hl=0.4, gloss=0.4, cast=0.2)
        cv.part(m(lambda d: E(cv, d, 0, hy - 122, 9)), GOLD, gloss=0.7, cast=0.1)
        cv.part(m(lambda d: POLY(cv, d, [(-76, hy - 66), (76, hy - 66), (72, hy - 38), (-72, hy - 38)])), (250, 200, 80), sh=0.4, hl=0.45, gloss=0.6, rim=0.8)
        cv.part(m(lambda d: E(cv, d, 0, hy - 86, 11, 14)), RED, sh=0.35, hl=0.4, gloss=1.0)
        for x in (-46, -23, 23, 46):
            cv.part(m(lambda d, x=x: E(cv, d, x, hy - 52, 6)), (40, 175, 110) if abs(x) > 30 else (60, 120, 230), gloss=0.9, cast=0.1)
        for i in range(11):
            cv.part(m(lambda d, i=i: E(cv, d, lerp(-66, 66, i / 10), hy - 34 + 6*math.sin(i), 3.2)), (255, 250, 236), sh=0.2, gloss=0.6, cast=0.1)
    else:  # Arjun
        cv.flat(m(lambda d: LINE(cv, d, [(0, hy - 40), (0, hy - 18)], 5)), (215, 40, 45))
        for x, hh in ((-40, 34), (0, 52), (40, 34)):
            cv.part(m(lambda d, x=x, hh=hh: POLY(cv, d, cubic((x - 20, hy - 62), (x - 16, hy - 62 - hh), (x + 16, hy - 62 - hh), (x + 20, hy - 62), 14) + [(x, hy - 62 - hh - 14)])), GOLD, sh=0.45, hl=0.45, gloss=0.5, rim=0.8)
            cv.part(m(lambda d, x=x, hh=hh: E(cv, d, x, hy - 70 - hh*0.45, 7 if x else 10)), RED if not x else (40, 175, 110), gloss=0.9, cast=0.15)
        cv.part(m(lambda d: POLY(cv, d, [(-78, hy - 66), (78, hy - 66), (74, hy - 40), (-74, hy - 40)])), (245, 196, 72), sh=0.4, hl=0.45, gloss=0.6, rim=0.8)
        for i in range(9):
            cv.part(m(lambda d, i=i: E(cv, d, lerp(-60, 60, i / 8), hy - 53, 3.5)), RED if i % 2 else (255, 250, 236), gloss=0.6, cast=0.1)

def L_eyes(cv, who, uy, brow, bl, lx, ly, closed):
    m = cv.mask; ey = -400 + uy; ink = (25, 15, 25)
    brc = C[who]["hair"] if who == "P" else (30, 20, 35)
    for s in (-1, 1):
        ex = s * 32
        if closed:
            cv.flat(m(lambda d, ex=ex: ARC(cv, d, ex, ey + 8, 16, 12, 200, 340, 5)), ink)
        elif bl < 0.3:
            cv.flat(m(lambda d, ex=ex: ARC(cv, d, ex, ey - 2, 17, 10, 20, 160, 4.5)), ink)
        else:
            cv.part(m(lambda d, ex=ex: E(cv, d, ex, ey, 18, 22 * bl)), (252, 252, 255), sh=0.25, hl=0, rim=0, cast=0.2)
            ix, iy = ex + lx*6 + s, ey + 3 + ly*5
            cv.part(m(lambda d, ix=ix, iy=iy: E(cv, d, ix, iy, 13, 16 * bl)), grad=((25, 15, 20), (130, 80, 50)) if who != "A" else ((20, 15, 15), (110, 70, 45)), sh=0.15, hl=0, rim=0, cast=0)
            cv.flat(m(lambda d, ix=ix, iy=iy: E(cv, d, ix, iy + 1, 6, 7 * bl)), (10, 6, 8))
            cv.flat(m(lambda d, ix=ix, iy=iy: E(cv, d, ix - 4, iy - 7, 5, 5.5 * bl)), (255, 255, 255))
            cv.flat(m(lambda d, ix=ix, iy=iy: E(cv, d, ix + 5, iy + 5, 2.2)), (255, 255, 255), alpha=0.9)
            cv.flat(m(lambda d, ex=ex: ARC(cv, d, ex, ey - 1, 19, 22 * bl, 200, 340, 5)), ink)
            if who == "P":
                cv.part(m(lambda d, ex=ex: CHORD(cv, d, ex, ey, 19, 22 * bl, 190, 350)), C["P"]["skin"], sh=0.3, hl=0.1, rim=0, cast=0)
                cv.flat(m(lambda d, ex=ex: ARC(cv, d, ex, ey + 18, 16, 8, 20, 160, 2)), C["P"]["skin_d"], alpha=0.7)
            else:
                cv.flat(m(lambda d, ex=ex, s=s: LINE(cv, d, [(ex + s*16, ey - 14), (ex + s*26, ey - 22)], 3.5)), ink)
                if who == "K": cv.flat(m(lambda d, ex=ex, s=s: LINE(cv, d, [(ex + s*18, ey - 6), (ex + s*27, ey - 10)], 3)), ink)
        by = ey - 30
        if brow == "sad": cv.flat(m(lambda d, s=s: LINE(cv, d, [(s*48, by + 6), (s*16, by - 6)], 5)), brc)
        elif brow == "angry": cv.flat(m(lambda d, s=s: LINE(cv, d, [(s*50, by - 12), (s*14, by + 6)], 6)), brc)
        elif brow == "curious" and s == 1: cv.flat(m(lambda d: LINE(cv, d, [(16, by - 4), (48, by - 14)], 5)), brc)
        else: cv.flat(m(lambda d, ex=ex: ARC(cv, d, ex, by + 8, 18, 9, 205, 335, 4.5)), brc)

def L_mouth(cv, who, uy, mood, o):
    m = cv.mask; my = -362 + uy; ink = (60, 25, 30)
    if o > 0:
        cv.part(m(lambda d: E(cv, d, 0, my, 13 + 4*o, 4 + 13*o)), (110, 30, 42), sh=0.3, hl=0, rim=0, cast=0)
        if o > 0.4: cv.flat(m(lambda d: CHORD(cv, d, 0, my - 2, 12 + 3*o, 3 + 10*o, 200, 340)), (250, 250, 250))
        cv.flat(m(lambda d: E(cv, d, 0, my + 8*o, 8, 4.5*o)), (235, 110, 125))
    elif mood == "happy":
        cv.part(m(lambda d: CHORD(cv, d, 0, my - 10, 22, 18, 0, 180)), (110, 30, 42), sh=0.2, hl=0, rim=0, cast=0)
        cv.flat(m(lambda d: E(cv, d, 0, my + 3, 9, 4)), (235, 110, 125))
    elif mood in ("sad", "angry"): cv.flat(m(lambda d: ARC(cv, d, 0, my + 10, 15, 9, 205, 335, 4.5)), ink)
    elif mood == "shock":
        cv.part(m(lambda d: E(cv, d, 0, my + 4, 12, 16)), (110, 30, 42), sh=0.3, hl=0, rim=0, cast=0)
        cv.flat(m(lambda d: E(cv, d, 0, my + 12, 7, 5)), (235, 110, 125))
    elif mood == "neutral": cv.flat(m(lambda d: LINE(cv, d, [(-10, my), (10, my)], 4)), ink)
    else: cv.flat(m(lambda d: ARC(cv, d, 0, my - 9, 17, 11, 25, 155, 4.5)), ink)

BB = dict(back=(-280, -720, 330, 40), lower=(-140, -240, 140, 20), upper=(-150, -420, 150, 0), arms=(-210, -520, 230, 0),
          head=(-160, -800, 220, -180), eyes=(-75, -470, 75, -200), mouth=(-45, -400, 45, -200))

def blinkq(t, who):
    b = blink(t + BLINK_OFF[who])
    return 1.0 if b > 0.75 else (0.5 if b > 0.3 else 0.1)

def char(frame, pen, who, X, Y, sc, t, pose="stand", mood="smile", talk=0.0, look=(0, 0), walking=False, sit=False):
    s = sc * SS
    q = int(((t * 6.5) % (2*math.pi)) / (2*math.pi) * 8) % 8 if walking else None
    ph = q * 2*math.pi / 8 if walking else None
    bob = -abs(math.sin(ph)) * 7 if walking else 0
    sob = math.sin(t * 16) * 2.5 if (mood == "sad" and talk < 0.05) else 0
    dy = (bob + sob) * sc; uy = 118 if sit else 0
    put(frame, sprite(("back", who, uy, sc), BB["back"], s, lambda cv: L_back(cv, who, uy)), X, Y + dy)
    put(frame, sprite(("lower", who, q, sit, sc), BB["lower"], s, lambda cv: L_lower(cv, who, ph, sit)), X, Y)
    put(frame, sprite(("upper", who, uy, sc), BB["upper"], s, lambda cv: L_upper(cv, who, uy)), X, Y + dy)
    g = 0.0
    if pose in ("talk", "bless"): g = round(math.sin(t * 3.3) * min(1, talk * 4) * 2) / 2 * 10
    aq = q if (walking and pose == "stand") else None
    arms = lambda: put(frame, sprite(("arms", who, uy, sc, pose, g, aq), BB["arms"], s, lambda cv: L_arms(cv, who, uy, pose, g, ph if aq is not None else None)), X, Y + dy)
    if pose != "wipe": arms()
    put(frame, sprite(("head", who, uy, sc), BB["head"], s, lambda cv: L_head(cv, who, uy)), X, Y + dy)
    closed = mood == "happy" and talk < 0.05
    brow = mood if mood in ("sad", "curious", "angry") else ("curious" if mood == "shock" else "n")
    bl = blinkq(t, who); lx = round(look[0] * 2) / 2; ly = round(look[1] * 2) / 2
    put(frame, sprite(("eyes", who, uy, sc, brow, bl, lx, ly, closed), BB["eyes"], s, lambda cv: L_eyes(cv, who, uy, brow, bl, lx, ly, closed)), X, Y + dy)
    o = round(clamp(talk) * 4) / 4 if talk > 0.06 else 0
    put(frame, sprite(("mouth", who, uy, sc, mood if not o else "t", o), BB["mouth"], s, lambda cv: L_mouth(cv, who, uy, mood, o)), X, Y + dy)
    if pose == "wipe": arms()
    if mood == "sad":
        qq = (t % 1.3) / 1.3
        for sd in (-1, 1):
            pen.ell(X + sd*34*sc, Y + dy + (-400 + uy + 16 + qq*52)*sc, 5*sc, 7*sc, fill=(130, 195, 255, int(230*(1 - qq))))

def shadow(frame, X, Y, rx):
    spr = sprite(("shadow", int(rx)), (-rx*1.6, -rx*0.6, rx*1.6, rx*0.6), SS, lambda cv: cv.soft(cv.mask(lambda d: E(cv, d, 0, 0, rx, rx*0.17)), (30, 35, 20), 0.55, rx*0.12))
    put(frame, spr, X, Y)
