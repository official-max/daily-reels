"""Backgrounds and animated shots.  Each shot function takes (t, shot) and returns (image at 2x, camera dict).

    forest:  walk (Krishna & Arjun walking), meet (banyan clearing with the ordinary man), divine (Krishna in golden light)
    darbar:  royal court with the Raja, two guards and the clever man (paheli format)
"""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from .config import W, H, SS
from .util import clamp, lerp, ease_io, ease_out, darker, Pen
from .canvas import SC, sprite, E, POLY, LINE
from .characters import char, shadow
from .themes import THEME

GY = 1500   # ground line of the forest clearing


def gradient(stops, h, w):
    ys = np.linspace(0, 1, h); arr = np.zeros((h, 3), np.float32)
    for (a, ca), (b, cb) in zip(stops, stops[1:]):
        k = (ys >= a) & (ys <= b); f = ((ys[k] - a) / (b - a))[:, None]
        arr[k] = np.array(ca) * (1 - f) + np.array(cb) * f
    return np.repeat(arr[:, None, :], w, axis=1)

def tree_blob(cv, x, y, s, cols):
    m = cv.mask
    cv.part(m(lambda d: [E(cv, d, x + dx*s, y + dy*s, r*s) for dx, dy, r in ((0, 0, 120), (-95, 35, 95), (95, 35, 95), (-55, -75, 95), (60, -80, 90), (0, 70, 100))]), cols[1], sh=0.5, hl=0.35, rim=0.5, cast=0)
    cv.part(m(lambda d: [E(cv, d, x + dx*s, y + dy*s, r*s) for dx, dy, r in ((-50, -70, 50), (40, -60, 42), (-90, 10, 38))]), cols[2], sh=0.3, hl=0.4, rim=0.6, cast=0.2)

def screen(img, col, mask):
    b = np.asarray(img, np.float32); a = np.array(col, np.float32); mk = np.asarray(mask, np.float32)[..., None] / 255
    return Image.fromarray(np.clip(255 - (255 - b) * (255 - a * mk) / 255, 0, 255).astype(np.uint8), "RGB")

def god_rays(size, sx, sy, angs, val=60):
    lay = Image.new("L", size, 0); d = ImageDraw.Draw(lay)
    for k, a0 in enumerate(angs):
        a = math.radians(a0); da = math.radians(2.2); L = 2600 * SS
        d.polygon([(sx*SS, sy*SS), (sx*SS + math.cos(a - da)*L, sy*SS + math.sin(a - da)*L), (sx*SS + math.cos(a + da)*L, sy*SS + math.sin(a + da)*L)], fill=val)
    return lay.filter(ImageFilter.GaussianBlur(26 * SS))

def bg_forest(walk=False):
    T = THEME; cv = SC((0, 0, W, H), SS); m = cv.mask; rr = random.Random(4)
    cv.rgb[:] = gradient(list(zip((0, 0.3, 0.5, 0.62, 1), T["sky"] + T["sky"][-1:])), cv.h, cv.w); cv.a[:] = 1
    sun = T["sun_xy"]
    if T["stars"]:
        for _ in range(90):
            x, y, r_ = rr.uniform(0, W), rr.uniform(0, 900), rr.uniform(1.5, 4)
            cv.flat(m(lambda d: E(cv, d, x, y, r_)), (235, 242, 255), alpha=0.9)
    cv.soft(m(lambda d: E(cv, d, *sun, 260)), T["sun"][0], 0.55, 90)
    cv.soft(m(lambda d: E(cv, d, *sun, 80)), T["sun"][1], 1.0, 12)
    hz = 1150 if walk else 1060
    hills = [(x, hz - 10 + 40*math.sin(x*0.006 + 1) + 16*math.sin(x*0.02)) for x in range(-20, 1110, 10)]
    cv.flat(m(lambda d: POLY(cv, d, hills + [(1110, 1500), (-20, 1500)])), T["hills"])
    for x in range(-40, 1130, 46):
        r_ = rr.uniform(40, 70) * (0.6 if walk else 1); y_ = hz + 60 - rr.uniform(0, 40) - (40 if walk else 0)
        cv.flat(m(lambda d, x=x, r_=r_, y_=y_: E(cv, d, x, y_, r_)), T["far"])
    if not walk:
        for x, y, s in ((60, 880, 1.15), (290, 950, 0.85)):
            cv.part(m(lambda d, x=x, y=y, s=s: POLY(cv, d, [(x - 16*s, y), (x + 16*s, y), (x + 22*s, 1230), (x - 22*s, 1230)])), (96, 70, 52), sh=0.5, rim=0.6, cast=0)
            tree_blob(cv, x, y - 40*s, s, T["leaf"])
        cv.part(m(lambda d: POLY(cv, d, [(800, 1520), (1000, 1520), (950, 1150), (970, 760), (870, 720), (850, 1150)])), (112, 80, 56), sh=0.55, hl=0.25, rim=0.8)
        for x in range(640, 1080, 30):
            cv.flat(m(lambda d, x=x: d.line([cv.P(x, 760 + (x % 3)*20), cv.P(x + 5, 1160 + (x % 5)*40)], fill=255, width=int(4*SS))), (120, 90, 64), alpha=0.8)
        for x, y, s in ((880, 500, 1.6), (650, 640, 1.0), (1070, 600, 1.1), (760, 360, 1.0), (1000, 380, 1.0)):
            tree_blob(cv, x, y, s, T["leaf"])
    gtop = 1160 if walk else 1200
    cv.rgb[int(gtop*SS):] = gradient([(0, T["ground"][0]), (1, T["ground"][1])], cv.h - int(gtop*SS), cv.w)
    path = [(515, gtop), (565, gtop), (1050, H), (30, H)] if walk else [(470, gtop), (610, gtop), (1000, H), (90, H)]
    cv.flat(m(lambda d: POLY(cv, d, path)), T["path"], alpha=0.9)
    cv.soft(m(lambda d: POLY(cv, d, [(0, gtop - 10), (W, gtop - 10), (W, gtop + 90), (0, gtop + 90)])), T["haze"], 0.35, 30)
    img = cv.image().convert("RGB").filter(ImageFilter.GaussianBlur(4 * SS))
    img = screen(img, T["haze"], god_rays(img.size, *sun, [(105 if sun[0] > 540 else 20) + k*9 + random.Random(k).uniform(-3, 3) for k in range(9)], T["rays"]))
    return img

def fg_grass(y0, y1, n, seed):
    cv = SC((0, 0, W, H), SS); m = cv.mask; rr = random.Random(seed)
    def blades(d):
        for _ in range(n):
            x = rr.uniform(-20, 1100); y = rr.uniform(y0, y1); h_ = rr.uniform(20, 60) * (0.6 + 0.6*(y - y0) / max(1, y1 - y0)); lean = rr.uniform(-12, 12)
            POLY(cv, d, [(x - 4, y), (x + lean, y - h_), (x + 4, y)])
    cv.part(m(blades), tuple(int(c * 0.8) for c in THEME["ground"][0]), sh=0.3, hl=0.35, rim=0.8, cast=0)
    for _ in range(7):
        x, y = rr.uniform(40, 1040), rr.uniform(y0 + 20, y1); c_ = rr.choice([(255, 120, 170), (255, 230, 90), (255, 255, 255)])
        cv.part(m(lambda d, x=x, y=y: [E(cv, d, x + math.cos(a)*10, y + math.sin(a)*10, 8) for a in np.linspace(0, 2*math.pi, 6)[:-1]]), c_, sh=0.3, rim=0.6)
        cv.part(m(lambda d, x=x, y=y: E(cv, d, x, y, 5)), (255, 200, 60), gloss=0.5)
    img = cv.image(); bb = img.getbbox(); return (img.crop(bb), -bb[0], -bb[1])

def tree_cols(i):
    """Leaf colours of the theme, a little lighter or darker per tree."""
    k = (1.0, 0.9, 1.1)[i]
    return tuple(tuple(min(255, int(c * k)) for c in col) for col in THEME["leaf"])

def tree_sprite(i):
    def fn(cv):
        m = cv.mask
        cv.part(m(lambda d: POLY(cv, d, [(-34, 0), (34, 0), (22, -330), (-22, -330)])), (105, 75, 50), sh=0.5, hl=0.25, rim=0.7)
        tree_blob(cv, 0, -420, 1.25, tree_cols(i))
    img, ox, oy = sprite(("tree", tree_cols(i)), (-300, -640, 300, 10), 1.6 * SS, fn)
    return img, ox, oy

CACHE = {}

def asset(name, fn):
    if name not in CACHE: CACHE[name] = fn()
    return CACHE[name]

TALK = {}

def talk(w): return TALK.get(w, 0.0)

_r = random.Random(9)

WALK_TREES = [((1 if i % 2 else -1) * _r.uniform(330, 640), i * 0.5, i % 3) for i in range(14)]

STONES = [(_r.uniform(-140, 140), _r.uniform(0, 1)) for _ in range(14)]

LEAVES = [(_r.uniform(380, 1100), _r.uniform(0, 900), _r.uniform(0, 6.28)) for _ in range(8)]

DUST = [(_r.uniform(0, W), _r.uniform(0, 1), _r.uniform(0.03, 0.08), _r.uniform(2, 5)) for _ in range(40)]

def dust(p, t, y0=250, y1=1700):
    for i, (x0, ph, sp, r) in enumerate(DUST):
        u = (ph + t*sp) % 1; y = y1 - u*(y1 - y0); x = x0 + 20*math.sin(t*0.7 + i)
        p.ell(x, y, r + 3, fill=(255, 236, 170, int(40*math.sin(math.pi*u))))
        p.ell(x, y, r*0.6, fill=(255, 245, 200, int(200*math.sin(math.pi*u))))


def build_divine():
    yy, xx = np.mgrid[0:H*SS, 0:W*SS].astype(np.float32)
    d = np.sqrt((xx - 540*SS)**2 + ((yy - 1150*SS) * 0.85)**2) / (1150*SS)
    stops = list(zip((0, 0.3, 0.65, 1.0), THEME["divine"]))
    out = np.zeros((H*SS, W*SS, 3), np.float32)
    for (a, ca), (b, cb) in zip(stops, stops[1:]):
        m = (d >= a) & (d < b); f = ((d[m] - a) / (b - a))[:, None]
        out[m] = np.array(ca) * (1 - f) + np.array(cb) * f
    out[d >= 1.0] = stops[-1][1]
    img = Image.fromarray(out.astype(np.uint8), "RGB"); p = Pen(img)
    for r in (330, 450, 570, 700): p.ell(540, 1150, r, outline=(255, 235, 180, 45), w=3)
    for k in range(24):
        a = k * math.pi / 12
        p.ell(540 + math.cos(a)*450, 1150 + math.sin(a)*450, 10, fill=(255, 235, 180, 70))
    return img


_r2 = random.Random(31)
SPARKS = [(_r2.uniform(80, 1000), _r2.uniform(0, 1), _r2.uniform(0.08, 0.2)) for _ in range(40)]
PETALS = [(_r2.uniform(0, 1080), _r2.uniform(0, 1), _r2.uniform(0, 6.28)) for _ in range(12)]


def shot_walk(t, s):
    img = asset("walk", lambda: bg_forest(walk=True)).copy(); p = Pen(img)
    fog = np.array(THEME["fog"], np.float32); hz = 1160
    items = sorted([(((z0 - t*0.55) % 7.0) + 0.7, X, i) for X, z0, i in WALK_TREES], reverse=True)
    for z, X, i in items:
        k = 1 / z; spr, ox, oy = tree_sprite(i); f = clamp((z - 0.7) / 6) * 0.75
        sc = k / 1.6; w_, h_ = max(1, int(spr.width * sc)), max(1, int(spr.height * sc))
        im = spr.resize((w_, h_), Image.BILINEAR)
        if f > 0.05:
            a = np.asarray(im, np.float32); a[..., :3] = a[..., :3] * (1 - f) + fog * f; im = Image.fromarray(a.astype(np.uint8), "RGBA")
        sx, by = 540 + X*k, hz + 420*k
        img.paste(im, (int(sx*SS - ox*sc), int(by*SS - oy*sc)), im)
    for X, u0 in STONES:
        u = (u0 + t*0.13) % 1; z = lerp(7.5, 0.6, u); k = 1 / z
        p.ell(540 + X*k, hz + 420*k, 10*k, 5*k, fill=(185, 160, 120))
    if s.get("who") == "P":
        shadow(img, 540, 1690, 95)
        char(img, p, "P", 540, 1690, 1.5, t, mood=s.get("pmood", "neutral"), look=(0, 0.2), walking=True)
    else:
        for x in (380, 700): shadow(img, x, 1690, 95)
        char(img, p, "K", 380, 1690, 1.45, t, mood="smile", look=(0.5, 0), walking=True)
        char(img, p, "A", 700, 1690, 1.45, t + 0.25, mood="smile", look=(-0.5, 0), walking=True)
    dust(p, t)
    e = ease_io(t / s["dur"])
    return img, dict(zoom=lerp(1.0, 1.06, e), cx=540, cy=1000)

def shot_meet(t, s):
    img = asset("meet", lambda: bg_forest()).copy(); p = Pen(img)
    for x0, y0, ph in LEAVES:
        y = (y0 + t*80) % 1000 + 520; x = x0 + 40*math.sin(t*1.3 + ph)
        p.ell(x, y, 10, 5, fill=THEME["petal"] + (220,))
    kx = s.get("kx", 220); ax = 460; kwalk = False
    if "kwalk" in s:
        k0, k1 = s["kwalk"]; u = clamp((t - 0.3) / 2.8); kx = lerp(k0, k1, ease_io(u)); kwalk = 0 < u < 1
    if "kwalk" in s or "kx" in s: ax = 200
    arrive = s.get("arrive") and t < 2.6
    off = lerp(-440, 0, ease_out(t / 2.6)) if s.get("arrive") else 0
    pm = s.get("pmood", "sad"); pmood = {"listen": "neutral", "happy": "happy"}.get(pm, pm)
    pt = talk("P")
    ppose = "wipe" if (pmood == "sad" and pt < 0.05 and (t % 5) < 1.8) else "stand"
    plook = (-1, 0) if (talk("K") > 0 or talk("A") > 0 or pm == "listen") else (0, 0.5)
    shadow(img, 800, GY - 4, 130); shadow(img, ax + off, GY, 85); shadow(img, kx + off, GY, 85)
    char(img, p, "P", 800, GY, 1.3, t, pose=ppose, mood=pmood, talk=pt, look=plook, sit=True)
    ap = s.get("apose") or ("talk" if talk("A") > 0.05 else "stand")
    kp = s.get("kpose") or ("talk" if talk("K") > 0.05 else "stand")
    drawK = lambda: char(img, p, "K", kx + off, GY, 1.3, t, pose=kp, mood="smile", talk=talk("K"), look=(s.get("klook", 0.5), 0), walking=arrive or kwalk)
    drawA = lambda: char(img, p, "A", ax + off, GY, 1.3, t + 0.3, pose=ap, mood="curious" if pm == "sad" else "smile", talk=talk("A"), look=(s.get("alook", 0), 0), walking=arrive)
    if kx < ax: drawK(); drawA()
    else: drawA(); drawK()
    g, ox, oy = asset("meet_fg", lambda: fg_grass(1480, 1560, 160, 5)); img.paste(g, (int(ox), int(oy)), g)
    dust(p, t)
    nm = s.get("cam", "wide"); e = ease_io(t / s["dur"])
    z, cx, cy = dict(wide=(1.0, 540, 1000), a=(1.75, ax, GY - 470), k=(1.75, kx, GY - 470), p=(1.8, 800, GY - 380),
                     ka=(1.4, (kx + ax) / 2, GY - 440), kp=(1.45, (kx + 800) / 2, GY - 440))[nm]
    return img, dict(zoom=z * lerp(1.0, 1.06, e), cx=cx, cy=cy)

def shot_divine(t, s):
    img = asset("divine", build_divine).copy(); p = Pen(img); gl = s.get("glow", 1.0)
    for k in range(16):
        a = t*0.12 + k*math.pi/8; da = 0.06
        p.poly([(540, 1150), (540 + math.cos(a - da)*1600, 1150 + math.sin(a - da)*1600), (540 + math.cos(a + da)*1600, 1150 + math.sin(a + da)*1600)], fill=(255, 240, 200, int(22*gl)))
    for i, (x0, ph, sp) in enumerate(SPARKS):
        u = (t*sp + ph) % 1; y = 1900 - u*1750; x = x0 + 25*math.sin(t + i)
        p.ell(x, y, 3.5 + (i % 3), fill=(255, 248, 210, int(220*math.sin(math.pi*u))))
    for i, (x0, ph, r0) in enumerate(PETALS):
        u = (t*0.09 + ph) % 1; p.ell(x0 + 60*math.sin(t*0.8 + r0), -40 + u*2000, 13, 7, fill=(255, 140, 170, 210))
    char(img, p, "K", 540, 2100, 2.2, t, pose="bless", mood="smile", talk=talk("K"), look=(0, 0.2))
    e = ease_io(t / s["dur"])
    return img, dict(zoom=lerp(1.0, 1.07, e), cx=540, cy=1080)

def arch_view(cv, arch, view, cx):
    """What is seen through an arch of the court: night sky, garden or sunset."""
    m = cv.mask; full = np.asarray(m(lambda d: POLY(cv, d, arch)))
    inside = lambda fn: Image.fromarray(np.minimum(full, np.asarray(m(fn))))
    sky = dict(night=((10, 14, 50), (60, 80, 150)), garden=((90, 170, 235), (225, 240, 240)), sunset=((90, 40, 120), (255, 170, 90)))[view]
    cv.part(m(lambda d: POLY(cv, d, arch)), grad=sky, sh=0.35, hl=0, rim=0, cast=0)
    rr = random.Random(cx)
    if view == "night":
        cv.flat(inside(lambda d: [E(cv, d, cx + rr.uniform(-140, 140), rr.uniform(400, 900), rr.uniform(2, 4)) for _ in range(26)]), (240, 244, 255))
        if cx == 900: cv.flat(inside(lambda d: E(cv, d, 880, 700, 46)), (250, 248, 225))
    if view == "sunset" and cx != 540:
        cv.flat(inside(lambda d: E(cv, d, cx, 860, 70)), (255, 226, 150))
    col = dict(night=(16, 24, 56), garden=(74, 150, 74), sunset=(90, 36, 80))[view]
    cv.flat(inside(lambda d: [E(cv, d, cx + dx, 1080, 110, 120 + (dx % 3)*16) for dx in (-150, -70, 20, 90, 160)]), col)


def bg_darbar():
    T = THEME; cv = SC((0, 0, W, H), SS); m = cv.mask; gold = T["gold"]; lite = tuple(min(255, c + 16) for c in gold)
    cv.rgb[:] = gradient([(0, T["wall"][0]), (0.42, T["wall"][1]), (0.62, T["wall"][2]), (1, T["wall"][2])], cv.h, cv.w); cv.a[:] = 1
    for cx_ in (180, 540, 900):
        w_ = 210 if cx_ == 540 else 150
        arch = [(cx_ - w_, 1150), (cx_ - w_, 560)] + [(cx_ + math.cos(a)*w_, 560 - math.sin(a)*w_*1.2) for a in np.linspace(math.pi, 0, 24)] + [(cx_ + w_, 1150)]
        cv.part(m(lambda d, arch=arch: POLY(cv, d, arch)), T["arch"], sh=0.5, hl=0.15, rim=0.3, cast=0)
        if T["view"]: arch_view(cv, arch, T["view"], cx_)
        cv.flat(m(lambda d, arch=arch: d.line([cv.P(x, y) for x, y in arch], fill=255, width=int(10*SS))), gold)
    for x in (40, 360, 720, 1040):
        cv.part(m(lambda d, x=x: POLY(cv, d, [(x - 34, 1250), (x - 34, 300), (x + 34, 300), (x + 34, 1250)])), gold, sh=0.5, hl=0.45, gloss=0.3, rim=0.8)
        for y in (290, 1220): cv.part(m(lambda d, x=x, y=y: POLY(cv, d, [(x - 50, y), (x + 50, y), (x + 50, y + 34), (x - 50, y + 34)])), lite, sh=0.4, hl=0.5, gloss=0.4)
    for x in (200, 880):
        cv.part(m(lambda d, x=x: POLY(cv, d, [(x - 46, 330), (x + 46, 330), (x + 46, 640), (x, 600), (x - 46, 640)])), T["banner"], sh=0.4, hl=0.3, rim=0.5)
        cv.part(m(lambda d, x=x: E(cv, d, x, 450, 22)), lite, gloss=0.5)
    if T["fan"]:                                        # peacock fan of feathers behind the throne
        for k in range(13):
            a = math.pi * (0.02 + 0.96 * k / 12); x, y = 540 - math.cos(a)*300, 760 - math.sin(a)*330
            cv.part(m(lambda d: LINE(cv, d, [(540, 760), (x, y)], 34)), darker(T["fan"], 0.7), sh=0.4, rim=0.5, cast=0.2)
            cv.part(m(lambda d: E(cv, d, x, y, 50)), T["fan"], sh=0.4, hl=0.4, rim=0.6, cast=0.3)
            cv.part(m(lambda d: E(cv, d, x, y, 24)), gold, gloss=0.6, cast=0)
            cv.part(m(lambda d: E(cv, d, x, y, 12)), T["gem"], gloss=0.9, cast=0)
    cv.part(m(lambda d: [E(cv, d, 540, 760, 200, 230), POLY(cv, d, [(340, 760), (740, 760), (740, 1230), (340, 1230)])]), gold, sh=0.5, hl=0.45, gloss=0.4, rim=0.8)
    cv.part(m(lambda d: [E(cv, d, 540, 780, 150, 180), POLY(cv, d, [(390, 780), (690, 780), (690, 1150), (390, 1150)])]), T["throne"], sh=0.45, hl=0.3)
    cv.part(m(lambda d: E(cv, d, 540, 600, 26)), T["gem"], gloss=0.9)
    fy = 1250
    cv.rgb[int(fy*SS):] = gradient([(0, T["floor"][0]), (1, T["floor"][1])], cv.h - int(fy*SS), cv.w)
    line = darker(T["floor"][0], 0.82); rows = (fy, 1300, 1380, 1490, 1640, 1840, 2080)
    if T["tiles"] == "checker":
        fx = lambda k, y: 540 + k*(40 + 220*(y - fy) / (H - fy))
        for j, (y0, y1) in enumerate(zip(rows, rows[1:])):
            cv.flat(m(lambda d: [POLY(cv, d, [(fx(k, y0), y0), (fx(k + 1, y0), y0), (fx(k + 1, y1), y1), (fx(k, y1), y1)])
                                 for k in range(-14, 14) if (k + j) % 2]), line, alpha=0.7)
    for k in range(-8, 9):
        cv.flat(m(lambda d, k=k: d.line([cv.P(540 + k*40, fy), cv.P(540 + k*260, H)], fill=255, width=int(3*SS))), line, alpha=0.6)
    for y in rows[1:-1]:
        cv.flat(m(lambda d, y=y: d.line([cv.P(0, y), cv.P(W, y)], fill=255, width=int(3*SS))), line, alpha=0.5)
    cv.part(m(lambda d: POLY(cv, d, [(440, fy - 20), (640, fy - 20), (900, H), (180, H)])), T["carpet"], sh=0.2, hl=0.15, cast=0)
    for sg in (-1, 1):
        cv.flat(m(lambda d, sg=sg: d.line([cv.P(540 + sg*92, fy - 20), cv.P(540 + sg*344, H)], fill=255, width=int(12*SS))), gold)
    cv.soft(m(lambda d: E(cv, d, 540, 760, 360)), (255, 220, 150), 0.18, 120)
    return cv.image().convert("RGB").filter(ImageFilter.GaussianBlur(3 * SS))

LAMPS = [(130, 1180), (950, 1180)]

def shot_darbar(t, s):
    img = asset("darbar", bg_darbar).copy(); p = Pen(img)
    for i, (x, y) in enumerate(LAMPS):
        fl = 0.8 + 0.2*math.sin(t*9 + i*2) + 0.1*math.sin(t*23 + i)
        for k in range(5): p.ell(x, y - 30, 30 + k*22, fill=(255, 190, 90, int(16*fl)))
        p.ell(x, y, 34, 12, fill=(160, 90, 40)); p.ell(x, y - 26, 9*fl, 20*fl, fill=(255, 210, 110)); p.ell(x, y - 22, 4, 9, fill=(255, 250, 220))
    rt, ct = talk("R"), talk("C")
    rm, cm = s.get("rmood", "neutral"), s.get("cmood", "neutral")
    rpose = ("point" if rm == "angry" else "talk") if rt > 0.05 else ("think" if rm == "shock" else "stand")
    cpose = "talk" if ct > 0.05 else ("think" if cm == "neutral" and (t % 6) < 3 else "stand")
    for x, ph in ((190, 0), (900, 0.7)):
        shadow(img, x, 1340, 70)
        char(img, p, "G", x, 1340, 1.0, t + ph, mood="neutral", look=(0.3 if x < 540 else -0.3, 0))
    shadow(img, 540, 1272, 80)
    char(img, p, "R", 540, 1272, 1.05, t, pose=rpose, mood=rm, talk=rt, look=(-0.5 if THEME["flip"] else 0.5, 0.4))
    side = -1 if THEME["flip"] else 1; chx = 540 + 220*side     # Chatur stands right or left of the carpet
    shadow(img, chx, 1760, 110)
    char(img, p, "C", chx, 1760, 1.3, t + 0.4, pose=cpose, mood=cm, talk=ct, look=(-0.5*side, -0.5))
    dust(p, t)
    nm = s.get("cam", "wide"); e = ease_io(t / s["dur"])
    z, cx, cy = dict(wide=(1.0, 540, 1000), raja=(1.75, 540, 860), chatur=(1.7, chx, 1230), both=(1.25, 540 + 110*side, 1130))[nm]
    return img, dict(zoom=z * lerp(1.0, 1.05, e), cx=cx, cy=cy)


SHOTS = dict(walk=shot_walk, meet=shot_meet, divine=shot_divine, darbar=shot_darbar)
