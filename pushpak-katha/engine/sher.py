"""Sample 4: Sher aur Chatur Khargosh (Panchatantra)."""
from toon import *
from lab import main as run
for _k in [k for k in globals() if k.startswith("s_")]: del globals()[_k]     # drop the race shots

def s_roar(c, t, D, tk, T):
    r = ease((t - D * .55) / .2) * (1 - ease((t - D * .9) / .2)); shake(c, T, 7 * r); cam(c, 1.1 + .2 * r, 540, 1050); scene(c, "jungle", T, dense=True); cave(c, 560, 1380, 1.0)
    beast(c, "lion", 560, GY, 1.2, T, mood="roar" if r > .4 else "angry", pose="cheer" if r > .4 else "hips")
    for i in range(3):
        if r > .4: u = (T * 2 + i / 3) % 1; c.drawCircle(580, 1010, 120 + 320 * u, line((255, 255, 255), 10, .7 * (1 - u)))
def s_plead(c, t, D, tk, T):
    cam(c, 1.02 + .05 * ease(t / D), 560, 1020); scene(c, "jungle", T, dense=True); cave(c, 1000, 1360, .8); beast(c, "monkey", 110, GY - 70, .78, T + 1, mood="worried", pose="fear"); beast(c, "fox", 520, GY - 80, .78, T + 2, mood="worried", pose="beg")
    beast(c, "elephant", 310, GY, 1.0, T, tk.get("E", 0), "worried", pose="talk"); beast(c, "lion", 860, GY, 1.12, T, mood="smug", d=-1, pose="hips")
def s_plan(c, t, D, tk, T):
    cam(c, 1.3 + .1 * ease(t / D), 520, 1130); scene(c, "day", T, 400); beast(c, "rabbit", 500, GY, 1.1, T, mood="worried" if t < D * .55 else "smug", pose="fear" if t < D * .55 else "think")
    if t > D * .6:
        u = ease((t - D * .6) / .25); x, y = 730, 880 - 14 * sin(T * 5); stars_burst(c, x, y, 130 * u, T * .6, rgb=(255, 244, 170)); cel(c, oval(x, y - 8, 50 * u, 56 * u), (255, 214, 60), w=6); cel(c, poly([(x - 22 * u, y + 44 * u), (x + 22 * u, y + 44 * u), (x + 18 * u, y + 74 * u), (x - 18 * u, y + 74 * u)]), (170, 170, 180), w=5)
def s_late(c, t, D, tk, T): shake(c, T, 3 * tk.get("L", 0)); cam(c, 1.5 + .06 * ease(t / D), 600, 1090); scene(c, "jungle", T, dense=True); cave(c, 700, 1370, 1.0); beast(c, "lion", 610, GY, 1.15, T, tk.get("L", 0), "angry", d=-1, pose="point")
def s_lie(c, t, D, tk, T): cam(c, 1.25 + .06 * ease(t / D), 500, 1120); scene(c, "jungle", T, 300, dense=True); beast(c, "lion", 850, GY, 1.1, T, mood="shock" if t > D * .5 else "angry", d=-1, pose="hips"); beast(c, "rabbit", 340, GY, .92, T, tk.get("R", 0), "worried", pose="talk")
def s_what(c, t, D, tk, T):
    cam(c, 1.75 + .12 * ease(t / D), 560, 1040); shake(c, T, 6 * tk.get("L", 0)); c.drawColor(col((200, 40, 40)))
    for i in range(18):
        a = i * pi / 9 + T * .25; c.drawPath(poly([(560, 1040), (560 + 2200 * cos(a), 1040 + 2200 * sin(a)), (560 + 2200 * cos(a + .17), 1040 + 2200 * sin(a + .17))]), fill((255, 150, 40)))
    beast(c, "lion", 560, GY, 1.15, T, tk.get("L", 0), "angry", pose="cheer")
def s_walk(c, t, D, tk, T): cam(c, 1.08, 540, 1010); scene(c, "sunset", T, t * 320); beast(c, "lion", 320, GY, 1.05, T, mood="angry", walk=True); beast(c, "rabbit", 720, GY, .85, T, mood="smug", run=True)
def s_well(c, t, D, tk, T): cam(c, 1.1 + .05 * ease(t / D), 560, 1060); scene(c, "sunset", T, 900, trees=3); well(c, 770, GY, .95); well(c, 770, GY, .95, True); beast(c, "lion", 140, GY + 10, 1.0, T, mood="angry", pose="hips"); beast(c, "rabbit", 430, GY + 40, .85, T, tk.get("R", 0), "smug", pose="point")
def s_inside(c, t, D, tk, T):
    """Looking down into the well: the lion's reflection in the water."""
    roar = T % 1000 and t > D * .0 and tk is not None and s_inside.roar
    c.drawColor(col((58, 48, 62)))
    for r in range(7):
        R = 900 - r * 62; n = 18
        for q in range(n):
            a0, a1 = (q + (r % 2) * .5) * 2 * pi / n, (q + .9 + (r % 2) * .5) * 2 * pi / n; f = 1 - r * .1
            p = [(540 + (R + 100) * cos(a0), 900 + (R + 100) * sin(a0)), (540 + (R + 100) * cos(a1), 900 + (R + 100) * sin(a1)), (540 + (R + 45) * cos(a1), 900 + (R + 45) * sin(a1)), (540 + (R + 45) * cos(a0), 900 + (R + 45) * sin(a0))]
            c.drawPath(poly(p), fill((150 * f, 138 * f, 150 * f))); c.drawPath(poly(p), line((50, 40, 54), 6))
    w = oval(540, 900, 490); c.drawPath(w, fill((40, 120, 170))); c.save(); c.clipPath(w, True); glow(c, 540, 820, 480, (150, 220, 250), .8)
    c.save(); wob = 1 + .02 * sin(T * 4); c.translate(540, 0); c.scale(wob, 1); c.translate(-540, 0); beast(c, "lion", 540, 1560, 1.5 * (1 + .08 * ease(t / D)), T, tk.get("L", 0), "roar" if s_inside.roar(t, D) else "angry", d=-1, pose="rest"); c.restore()
    c.drawPaint(fill((40, 130, 190), .32))
    for i in range(5): u = (T * .4 + i / 5) % 1; c.drawOval(skia.Rect.MakeLTRB(540 - 480 * u, 900 - 480 * u, 540 + 480 * u, 900 + 480 * u), line((255, 255, 255), 6, .5 * (1 - u)))
    c.restore(); c.drawPath(w, line(INK, 16))
s_inside.roar = lambda t, D: False
def s_echo(c, t, D, tk, T):
    shake(c, T, 8 if t > D * .45 else 0); s_inside.roar = lambda t, D: t > D * .45; s_inside(c, t, D, tk, T); s_inside.roar = lambda t, D: False
def s_jump(c, t, D, tk, T):
    u = clamp((t - .5) / .9); shake(c, T, 10 * (1 if 1.35 < t < 1.75 else 0)); cam(c, 1.06, 560, 960); scene(c, "sunset", T, 900, trees=3); well(c, 620, GY, 1.1)
    if u < 1:
        x, y = 160 + 460 * u, GY - 30 - 1150 * u * (1 - u) - 100 * u; c.save()
        c.save(); c.translate(x, y - 180); c.rotate(170 * u); c.translate(-x, -y + 180); beast(c, "lion", x, y, 1.0 - .25 * u, T, mood="roar", pose="cheer"); c.restore(); c.restore()
    well(c, 620, GY, 1.1, True)
    if t > 1.35:
        v = t - 1.35; r = random.Random(1)
        for i in range(46):
            a = -pi / 2 + r.uniform(-.9, .9); sp = r.uniform(500, 1350); px, py = 620 + cos(a) * sp * v, GY - 190 + sin(a) * sp * v + 1300 * v * v; c.drawPath(oval(px, py, r.uniform(9, 24)), fill((120, 206, 250)));
    beast(c, "rabbit", 930, GY + 40, .8, T, mood="laugh" if t > 1.5 else "smug", d=-1, pose="cheer" if t > 1.5 else "rest")
def s_party(c, t, D, tk, T):
    cam(c, 1.04 + .04 * ease(t / D), 540, 1010); scene(c, "day", T, 200); h = lambda p: -abs(sin(T * 5 + p)) * 46
    beast(c, "elephant", 240, GY - 50 + h(0), .95, T, mood="happy", pose="cheer"); beast(c, "fox", 840, GY - 50 + h(1), .85, T, mood="happy", d=-1, pose="cheer"); beast(c, "monkey", 990, GY + h(2), .8, T, mood="laugh", d=-1, pose="cheer"); beast(c, "rabbit", 550, GY + 20 + h(.5), 1.0, T, mood="laugh", pose="cheer"); confetti(c, T)
def s_moral(c, t, D, tk, T): cam(c, 1.4 + .06 * ease(t / D), 540, 1120); scene(c, "day", T, 200); beast(c, "rabbit", 540, GY, 1.1, T, mood="happy", pose="point"); confetti(c, T)

N, Lv, R, E = (M, "+5%", "-4Hz"), (M, "+0%", "-26Hz"), (S, "+10%", "+26Hz"), (M, "-6%", "-14Hz")
def L(shot, who, v, hi, ro, **k): return dict(shot=shot, who=who, v=v, hi=hi, ro=ro, **k)
LINES = [
 L("roar", "N", N, "एक जंगल में था एक शेर, जो रोज़ कई जानवर मार देता था।", "Ek jungle mein tha ek *sher,* jo roz kai *jaanwar* maar deta tha.", pad=.5),
 L("plead", "E", E, "महाराज, हम रोज़ एक जानवर खुद भेज देंगे। बस शिकार बंद कर दीजिए।", "Maharaj, hum roz *ek* *jaanwar* khud bhej denge. Bas *shikaar* band kar dijiye."),
 L("plan", "N", N, "एक दिन बारी आई नन्हे खरगोश की। पर उसने एक चाल सोची।", "Ek din baari aayi nanhe *khargosh* ki. Par usne ek *chaal* sochi.", pad=.5),
 L("late", "L", Lv, "इतनी देर क्यों लगाई?", "Itni *der* kyun *lagayi?*"),
 L("lie", "R", R, "महाराज, रास्ते में दूसरा शेर मिला! बोला, जंगल का राजा मैं हूँ!", "Maharaj, raaste mein *doosra* *sher* mila! Bola, jungle ka *raja* main hoon!"),
 L("what", "L", Lv, "क्या? दिखाओ मुझे, कहाँ है वो!", "Kya? *Dikhao* mujhe, *kahan* hai woh!"),
 L("walk", "N", N, "खरगोश उसे एक कुएँ के पास ले गया।", "Khargosh use ek *kuen* ke paas le gaya."),
 L("well", "R", R, "वो इसी के अंदर छुपा है!", "Woh isi ke *andar* *chhupa* hai!"),
 L("inside", "N", N, "शेर ने झाँका, तो अपनी ही परछाई दिखी।", "Sher ne jhaanka, toh apni hi *parchhai* dikhi."),
 L("echo", "N", N, "उसने दहाड़ लगाई, तो अंदर से भी दहाड़ आई!", "Usne *dahaad* lagayi, toh andar se bhi *dahaad* aayi!", pad=.6),
 L("jump", "N", N, "गुस्से में शेर, कुएँ में कूद गया!", "Gusse mein sher, *kuen* mein *kood* gaya!", pad=.8),
 L("party", "N", N, "और पूरा जंगल आज़ाद हो गया!", "Aur poora jungle *azaad* ho gaya!", pad=.4),
 L("moral", "N", N, "याद रखो, बुद्धि ताक़त से बड़ी होती है।", "Yaad rakho, *buddhi* taaqat se *badi* hoti hai.", pad=2.2),
]
SH = {k[2:]: v for k, v in list(globals().items()) if k.startswith("s_")}
def growl(d=1.1):
    t = au.tarr(d); f = 95 + 35 * np.sin(2 * pi * 1.1 * t) - 25 * t; x = np.sign(np.sin(2 * pi * np.cumsum(f) / SR)) * .5 + au.noise(d) * .35
    return au.band(x * (1 + .5 * np.sin(2 * pi * 27 * t)), 60, 1400) * np.hanning(len(t)) ** .6
def mus(n, tl):
    b = music(n, dict(total=tl["total"])); drum = np.zeros(n); t = .1; i = 0
    while t < tl["total"]:
        q = au.tarr(.3); au.add(drum, t, np.sin(2 * pi * np.cumsum(70 + 60 * np.exp(-q * 30)) / SR) * np.exp(-q * 14), .8 if i % 4 in (0, 3) else .25); t += .25; i += 1
    return b * .8 + drum * .6
def fx(f, tl):
    for l in tl["lines"]:
        s = l["start"]; D = l["end"] - s
        if s > 0: au.add(f, s - .3, au.band(au.noise(.6), 400, 4000) * np.hanning(int(.6 * SR)), .12)
        if l["shot"] == "roar": au.add(f, s + D * .55, growl(), .5)
        if l["shot"] == "echo": au.add(f, s + D * .45, growl(1.3), .55); au.add(f, s + D * .45 + .5, growl(1.2), .25)
        if l["shot"] == "what": au.add(f, s, au.sweep(90, 50, 1.0, 4), .8)
        if l["shot"] == "plan": au.add(f, s + D * .6, au.bell(1040, 1.5), .4)
        if l["shot"] == "jump": au.add(f, s + .5, au.sweep(400, 1100, .8, 2), .18); au.add(f, s + 1.35, au.band(au.noise(1.0), 300, 5000) * np.exp(-au.tarr(1.0) * 4), .8)
        if l["shot"] == "party":
            for j, q in enumerate((523, 659, 784, 1047, 1318)): au.add(f, s + .1 + j * .11, au.sweep(q, q, .9, 4), .3)
if __name__ == "__main__": run("sher", LINES, SH, ("SHER AUR", "CHATUR KHARGOSH"), mus, fx)
