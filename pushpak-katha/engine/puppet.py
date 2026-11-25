"""Puppet-style (kathputli) generator: every seed gives a new cast, clothes, place, time of day, craft and framing.
    python puppet.py            # writes preview_puppet.jpg, a sheet of different looks
One story keeps one seed, so its people stay the same from shot to shot; the next story gets new ones."""
import random, math
import numpy as np, skia
from math import sin, cos, pi
from lab import W, H, col, mix, fill, line, vgrad, glow, poly, smooth, oval

SKIN = [(236,188,140),(214,158,110),(188,126,82),(158,100,64),(128,80,54)]
SETS = [dict(a=(178,34,42),b=(240,180,60),c=(34,110,84)), dict(a=(28,84,140),b=(246,196,90),c=(196,60,50)), dict(a=(112,44,120),b=(250,170,70),c=(40,130,130)),
        dict(a=(20,120,110),b=(250,214,130),c=(206,70,80)), dict(a=(214,96,30),b=(255,226,150),c=(64,60,130)), dict(a=(60,104,50),b=(240,200,110),c=(160,50,60)),
        dict(a=(190,60,110),b=(252,208,120),c=(44,90,120)), dict(a=(70,60,80),b=(224,190,130),c=(170,60,44))]
# sky top, sky bottom, far, near, ground, light
TIMES = dict(night=((16,20,58),(62,56,120),(44,46,96),(28,28,66),(38,32,60),(255,214,130)), dusk=((92,36,72),(244,142,78),(132,60,84),(78,38,66),(92,50,60),(255,206,120)),
             day=((86,176,206),(250,236,196),(150,190,160),(96,146,110),(196,160,104),(255,250,220)), dawn=((110,104,168),(255,204,176),(176,132,158),(120,92,130),(150,110,112),(255,232,190)),
             storm=((34,44,52),(112,124,120),(64,78,80),(40,52,56),(58,60,56),(210,230,230)), gold=((188,120,40),(255,222,140),(204,140,70),(150,88,44),(140,84,46),(255,246,200)))
PLACES = ["palace","ghat","battle","desert","forest","village"]
CRAFTS = ["kathputli","leather","paper","miniature"]
ROLES = dict(raja=("crown","turban"), sage=("jata","bald"), rani=("veil","hairlong"), yoddha=("helmet","crown"), kisan=("pagdi","turban"), bala=("braid","veil"), dev=("mukut",))

def person(r, role, craft, pal=None):
    """All that makes one person look like nobody else."""
    f = role in ("rani", "bala")
    return dict(role=role, f=f, craft=craft, pal=pal or r.choice(SETS), skin=(78,140,196) if role == "dev" else r.choice(SKIN), nose=r.uniform(14,40), nosey=r.uniform(-4,16),
        jaw=r.uniform(70,96), chin=r.uniform(-8,16), brow=r.uniform(-6,10), eye=r.uniform(20,32), head=r.uniform(.9,1.12), wide=r.uniform(.8,1.2) * (.86 if f else 1), tall=r.uniform(.9,1.1),
        hat=r.choice(ROLES[role]), hatk=r.uniform(.8,1.35), feather=r.randrange(3), tilak=r.randrange(4), must=0 if f or role == "dev" else r.choice([1,2,3,0] if role != "sage" else [0]),
        beard=0 if f or role == "dev" else (r.choice([2,3]) if role == "sage" else r.choice([0,0,1])), pat=r.randrange(5), pat2=r.randrange(5), top=r.randrange(3), bottom="skirt" if f else r.choice(["dhoti","robe","pyjama"]),
        neck=r.randrange(3), ear=r.randrange(3), prop=r.choice({"raja":["sword",None],"sage":["staff","mala"],"yoddha":["bow","sword","spear"],"kisan":["staff","sickle"],"dev":["flute"]}.get(role,["lamp","pot",None])))

def ink(p): return dict(kathputli=(40,22,26), leather=(24,10,8), paper=None, miniature=(84,40,24))[p["craft"]]
def put(c, path, rgb, p, w=6):
    """One cut-out piece, in the story's craft."""
    k = p["craft"]
    if k == "paper":
        c.save(); c.translate(7, 9); c.drawPath(path, fill((0,0,0), .35, 7)); c.restore(); c.drawPath(path, fill(rgb)); c.save(); c.clipPath(path, True); c.translate(0,3); c.drawPath(path, line(mix(rgb,(255,255,255),.45), 5)); c.restore(); return
    if k == "leather": rgb = mix(rgb, (190,80,20), .28)
    c.drawPath(path, fill(rgb)); c.save(); c.clipPath(path, True)
    c.drawPath(path, line(mix(rgb, (20,0,30), .3) if k != "miniature" else mix(rgb,(255,220,150),.4), 26 if k != "miniature" else 14)); c.restore()
    c.drawPath(path, line(ink(p), w))
def pattern(c, path, n, rgb, box):
    c.save(); c.clipPath(path, True); x0,y0,x1,y1 = box
    for iy, y in enumerate(np.arange(y0, y1, 38)):
        if n == 1: c.drawLine(x0,y,x1,y,line(rgb,5)); continue
        if n == 2: c.drawPath(poly([(x, y + (14 if i % 2 else 0)) for i, x in enumerate(np.arange(x0,x1+20,18))], False), line(rgb,4)); continue
        for x in np.arange(x0 + (19 if iy % 2 else 0), x1, 38):
            if n == 0: c.drawCircle(x,y,6,fill(rgb))
            elif n == 3: c.drawPath(poly([(x,y-10),(x+8,y),(x,y+10),(x-8,y)]), fill(rgb))
            else: c.drawPath(smooth([(x,y-13),(x+9,y+2),(x,y+10),(x-9,y+2)]), fill(rgb)); c.drawLine(x,y+8,x,y+16,line(rgb,3))
    c.restore()
def joint(c, x, y, p):
    if p["craft"] in ("kathputli","leather"): c.drawCircle(x,y,9,fill(p["pal"]["b"])); c.drawCircle(x,y,9,line(ink(p),4)); c.drawCircle(x,y,2.5,fill(ink(p)))

def seg(c, p, a, b, w0, w1, rgb):
    dx, dy = b[0]-a[0], b[1]-a[1]; L = math.hypot(dx,dy) or 1; nx, ny = -dy/L, dx/L
    q = skia.Path(); q.addPoly([skia.Point(a[0]+nx*w0,a[1]+ny*w0),skia.Point(b[0]+nx*w1,b[1]+ny*w1),skia.Point(b[0]-nx*w1,b[1]-ny*w1),skia.Point(a[0]-nx*w0,a[1]-ny*w0)], True)
    u = skia.Op(skia.Op(q, oval(*a,w0), skia.kUnion_PathOp), oval(*b,w1), skia.kUnion_PathOp); put(c, u, rgb, p)
def arm(c, p, x, y, a1, a2, rgb, hold=None):
    e = (x+sin(a1)*120, y+cos(a1)*120); h = (e[0]+sin(a2)*112, e[1]+cos(a2)*112)
    if hold: prop(c, p, hold, *h)
    seg(c, p, e, h, 21, 16, p["skin"]); seg(c, p, (x,y), e, 30, 24, rgb); joint(c, x, y, p); joint(c, *e, p)
    put(c, smooth([(h[0]-18,h[1]-16),(h[0]+18,h[1]-20),(h[0]+34,h[1]+2),(h[0]+12,h[1]+22),(h[0]-20,h[1]+14)]), p["skin"], p)
    for k in (-8, 0): c.drawLine(h[0]-sin(a2)*(18-k)-cos(a2)*17, h[1]-cos(a2)*(18-k)+sin(a2)*17, h[0]-sin(a2)*(18-k)+cos(a2)*17, h[1]-cos(a2)*(18-k)-sin(a2)*17, line(p["pal"]["b"],6))
def prop(c, p, k, x, y):
    g, wood, steel = p["pal"]["b"], (120,76,44), (206,214,220)
    if k == "sword": put(c, smooth([(x-6,y),(x+20,y-120),(x+80,y-250),(x+62,y-120),(x+16,y+4)]), steel, p); put(c, poly([(x-34,y-8),(x+40,y-14),(x+40,y+4),(x-34,y+10)]), g, p)
    elif k in ("staff","spear"):
        put(c, poly([(x-9,y-330),(x+9,y-330),(x+9,y+420),(x-9,y+420)]), wood, p)
        if k == "spear": put(c, poly([(x,y-440),(x+30,y-350),(x,y-320),(x-30,y-350)]), steel, p)
        else: put(c, oval(x,y-340,24), g, p)
    elif k == "bow":
        q = skia.Path(); q.moveTo(x-30,y-270); q.quadTo(x+110,y-130,x+10,y); q.quadTo(x+110,y+130,x-30,y+270); c.drawPath(q,line(ink(p) or (60,30,20),24)); c.drawPath(q,line(g,14)); c.drawLine(x-30,y-270,x-30,y+270,line((250,240,210),3))
    elif k == "lamp": glow(c,x+20,y-50,150,(255,200,90),.8); put(c, smooth([(x-40,y-24),(x+80,y-24),(x+46,y+18),(x-10,y+18)]), g, p); c.drawPath(smooth([(x+20,y-88),(x+38,y-40),(x+20,y-22),(x+2,y-40)]),fill((255,150,30))); c.drawPath(smooth([(x+20,y-64),(x+28,y-38),(x+20,y-26),(x+12,y-38)]),fill((255,240,150)))
    elif k == "pot": put(c, smooth([(x-30,y-110),(x+60,y-110),(x+44,y-84),(x+96,y-30),(x+50,y+24),(x-20,y+24),(x-66,y-30),(x-14,y-84)]), p["pal"]["c"], p)
    elif k == "sickle": c.drawPath(smooth([(x,y),(x+10,y-60),(x+80,y-110),(x+120,y-50)],False),line(ink(p) or (60,30,20),22)); c.drawPath(smooth([(x,y),(x+10,y-60),(x+80,y-110),(x+120,y-50)],False),line(steel,13))
    elif k == "mala": [c.drawCircle(x+sin(i/16*2*pi)*36,y+46+cos(i/16*2*pi)*52,9,fill((130,60,40))) for i in range(16)]
    elif k == "flute": c.drawLine(x-70,y+10,x+150,y-40,line(ink(p) or (60,30,20),24)); c.drawLine(x-70,y+10,x+150,y-40,line((226,180,90),15))

def head(c, p, talk, mood, t):
    """Side face looking right; the neck is at (0, 0)."""
    P, sk, g = p["pal"], p["skin"], p["pal"]["b"]; hair = (238,232,220) if p["role"] == "sage" else (30,22,30)
    c.save(); c.scale(p["head"], p["head"]); n, ny, j, ch = p["nose"], p["nosey"], p["jaw"], p["chin"]
    if p["hat"] in ("hairlong","braid"): put(c, smooth([(-70,-210),(-112,-130),(-110,0),(-124,160),(-80,170),(-50,40),(-40,-90)]), hair, p)
    if p["role"] in ("sage","dev"): put(c, smooth([(-60,-190),(-104,-110),(-96,30),(-40,40),(-30,-90)]), hair, p)
    put(c, poly([(-34,-40),(32,-40),(44,36),(-46,36)]), mix(sk,(60,20,40),.18), p)
    mo = talk * 16
    face = smooth([(-92,-120),(-72,-196),(0,-222),(62,-200),(80+p["brow"],-150),(76,-128),(86+n*.6,-104+ny),(88+n,-88+ny),(76,-74+ny),(84,-58),(88,-50),(76,-44),(84,-32+mo),(70,-20+mo),(62+ch,4+mo),(24,16+mo*.8),(-j+30,-20),(-84,-60)])
    put(c, face, sk, p)
    mouth = smooth([(88,-50),(52,-46),(40,-42+(-6 if mood=="happy" else 6)),(54,-38+mo*.9),(86,-40+mo)]); c.drawPath(mouth, fill((110,20,30))); c.drawLine(84,-50,44,-44+(-9 if mood=="happy" else 8 if mood in("sad","angry") else 0),line(mix(sk,(120,10,20),.65),6))
    e = p["eye"]; ex, ey = 36, -124
    bk = abs((t % 3.1) - .12)/.12; op = min(1, bk)**.7; blink = op < .25; e *= max(.18, op)
    c.drawPath(smooth([(ex-e*1.25,ey+2),(ex,ey-e*.72),(ex+e*1.2,ey-2),(ex,ey+e*.6)]), fill((255,252,240) if not blink else sk)); c.drawPath(smooth([(ex-e*1.5,ey+4),(ex,ey-e*.75),(ex+e*1.3,ey-2)],False), line((30,16,24),7))
    if not blink: c.drawCircle(ex+6,ey-2,e*.46,fill((30,16,24))); c.drawCircle(ex+10,ey-7,e*.15,fill((255,255,255)))
    by = dict(angry=(-16,14),sad=(8,-12)).get(mood,(-2,-4)); c.drawPath(smooth([(ex-40,ey-32+by[0]),(ex-4,ey-46),(ex+38,ey-34+by[1])],False),line(hair,11 if not p["f"] else 7))
    if p["f"]: c.drawCircle(70,-158,9,fill((210,20,40))); c.drawCircle(86+n*.5,-84+ny,14,line(g,4))
    elif p["tilak"] == 1: c.drawLine(62,-190,74,-142,line((214,40,30),10))
    elif p["tilak"] == 2: [c.drawLine(34,-192+k*13,76,-186+k*13,line((246,240,220),6)) for k in range(3)]
    elif p["tilak"] == 3: c.drawCircle(70,-160,10,fill((240,170,30)))
    m, b = p["must"], p["beard"]
    if b: put(c, smooth([(76,-34+mo),(74,10+mo),([0,50,36,64][b],[0,44,120,220][b]),(-10,[0,30,90,150][b]),(-46,-10),(-74,-84),(-50,-90),(-20,-34),(40,-24+mo)]), hair, p)
    if m: c.drawPath(smooth([(90,-66),(60,-58),(34,-56),(14,-66)] if m == 1 else [(90,-62),(60,-52),(24,-38),(6,-10)] if m == 2 else [(88,-66),(64,-58),(40,-62),(24,-80),(34,-98)],False),line(hair,17 if m != 2 else 13))
    k, h = p["hatk"], p["hat"]
    if h in ("turban","pagdi","crown","helmet"): put(c, smooth([(-100,-170),(-104,-90),(-90,-26),(-58,-40),(-36,-90),(-16,-130),(10,-176)]), hair, p)
    ear = oval(-28,-104,17,24); 
    if h not in ("veil","helmet"): put(c, ear, sk, p)
    if h in ("turban","pagdi"):
        hh = 110*k; put(c, smooth([(-118,-150),(-112,-200-hh*.6),(-20,-232-hh),(80,-200-hh*.6),(100,-160),(0,-184)]), P["a"], p)
        for i in range(4): c.drawPath(smooth([(-108+i*8,-160-i*24),(-10,-196-i*hh*.24),(96-i*8,-172-i*26)],False),line(mix(P["a"],g,.6),8))
        if h == "pagdi": put(c, smooth([(-108,-170),(-150,-90),(-140,40),(-104,50),(-100,-80)]), P["a"], p)
        else: put(c, oval(66,-204,20,26), P["c"], p)
    elif h in ("crown","mukut"):
        hh = (130 if h == "crown" else 170)*k
        pts = [(-104,-160),(-108,-204),(-96,-190-hh*.7),(-52,-200-hh*.35),(-4,-206-hh),(40,-200-hh*.35),(82,-190-hh*.7),(94,-160)] if h == "crown" else [(-104,-160),(-100,-210),(-60,-230-hh*.5),(-4,-230-hh),(50,-230-hh*.5),(88,-206),(94,-160)]
        put(c, poly(pts), g, p); put(c, poly([(-110,-196),(98,-196),(94,-152),(-104,-152)]), P["a"], p); [c.drawCircle(-84+i*34,-174,9,fill([g,P["c"]][i%2])) for i in range(6)]
        if h == "mukut": [c.drawLine(-70+i*12,-214-i*hh*.18,60-i*9,-214-i*hh*.18,line(P["a"],5)) for i in range(5)]
    elif h == "helmet": put(c, smooth([(-112,-60),(-120,-160),(-70,-250),(0,-270),(76,-236),(92,-160),(40,-170),(-40,-160),(-60,-70)]), (170,176,184), p); put(c, poly([(-12,-258),(0,-268-90*k),(12,-258)]), g, p); c.drawPath(smooth([(-112,-150),(0,-186),(92,-160)],False),line(g,11))
    elif h == "veil": put(c, smooth([(86,-196),(30,-250),(-70,-240),(-130,-150),(-136,20),(-160,220),(-90,230),(-56,40),(-44,-60),(10,-170),(80,-176)]), P["a"], p); c.drawPath(smooth([(84,-186),(6,-182),(-46,-70),(-58,40),(-90,226)],False),line(g,10)); c.drawCircle(72,-190,14,fill(g))
    elif h == "jata": put(c, smooth([(-100,-120),(-104,-200),(0,-240),(70,-212),(78,-176),(0,-190),(-60,-150)]), hair, p); put(c, smooth([(-56,-220),(-60,-290*k**.3),(0,-330*k**.3),(34,-270),(26,-220)]), hair, p); c.drawLine(-50,-228,28,-228,line((190,90,40),14))
    elif h == "bald": put(c, smooth([(-96,-110),(-104,-170),(-60,-180),(-50,-110)]), hair, p)
    else:
        put(c, smooth([(-104,-90),(-112,-190),(-20,-250),(70,-216),(84,-178),(20,-186),(-40,-140),(-60,-80)]), hair, p)
        c.drawPath(smooth([(80,-186),(20,-200),(-40,-160)],False),line(g,6))
        if h == "braid": [c.drawCircle(-116,-20+i*40,9,fill(g)) for i in range(5)]
    if p["feather"] and h in ("turban","crown","mukut"):
        q = smooth([(40,-220),(40,-330),(92,-400),(118,-340),(70,-250)]) if p["feather"] == 1 or p["role"]=="dev" else smooth([(30,-220),(-10,-320),(20,-420),(60,-340)]); put(c, q, (30,140,110), p)
        x, y = (88,-346) if p["feather"] == 1 or p["role"]=="dev" else (22,-344); c.drawCircle(x,y,22,fill((240,190,60))); c.drawCircle(x,y,13,fill((30,60,160)))
    if p["ear"]: c.drawCircle(-28,-76,[0,13,20][p["ear"]],line(g,7))
    c.restore()

def puppet(c, p, x, y, s, t, d=1, talk=0., mood="n", arms=(.35,.9), strings=False, walk=0., pace=0.):
    """Feet at (x, y). arms = (front upper, front lower) angles from straight down."""
    P, sk, g = p["pal"], p["skin"], p["pal"]["b"]; sw = sin(t*2.1 + x)*.03; c.save(); c.translate(x,y); c.scale(s*d,s); c.drawOval(skia.Rect.MakeLTRB(-190,-26,220,34),fill((0,0,0),.38,14)); A = 64*max(walk,.01); om = pi*pace/s/(2*A) if pace else 5.2; ph = t*om; c.rotate(sw*57*.6 + 3.5*min(1,walk)); walk and c.translate(0,7*walk*cos(2*ph)+6)
    k, w = p["tall"], p["wide"]; hip, sh = -350*k, -650*k; a0, a1 = arms
    if strings and p["craft"] == "kathputli": [c.drawLine(q, sh-120, q*.7, -2600, line((250,236,200),2.5,.45)) for q in (-60*w,30,110*w)]
    for q in (-1,1):
        u = ((ph+(q>0)*pi)/(2*pi)) % 1
        if u < .5: st, up = 1-4*u, 0.
        else: v = (u-.5)*2; st, up = -1+2*v*v*(3-2*v), sin(v*pi)**2
        fx, fy = q*(46*w)*(1-.5*min(1,walk))+st*A*(walk>0), -up*44*walk*(walk>0)
        hx, hy, ax, ay = q*34*w, hip+20, fx, -30+fy; dx, dy = ax-hx, ay-hy; dd = math.hypot(dx,dy); l = max(168*k, dd/2+.5); b = math.sqrt(max(0, l*l-dd*dd/4))*min(1,walk)
        kx, ky = (hx+ax)/2+b*dy/dd, (hy+ay)/2-b*dx/dd
        if p["bottom"] != "skirt": lc = P["c"] if p["bottom"]=="pyjama" else sk; seg(c,p,(hx,hy),(kx,ky),34*w,26,lc); seg(c,p,(kx,ky),(ax,ay),26,20,lc); joint(c,kx,ky,p)
        put(c, smooth([(fx-30,-34+fy),(fx+20,-36+fy),(fx+84,-10+fy),(fx+64,4+fy),(fx-30,4+fy)]), P["a"] if p["role"] in("raja","yoddha") else sk, p)
    arm(c,p,-62*w,sh+34,-.25+sin(t*1.7)*.08-sin(ph)*.45*walk,.15+sin(t*1.7-.5)*.1-sin(ph-.5)*.5*walk, mix([P["a"],sk,P["c"]][p["top"]],(20,0,30),.25))
    if p["top"] == 0 and p["role"] in ("raja","dev","yoddha"): put(c, smooth([(-60*w,sh),(-150*w,hip),(-190*w,-60),(-60,-70),(30*w,sh+60)]), P["c"], p)
    body = smooth([(-92*w,sh+10),(-30,sh-22),(40,sh-22),(96*w,sh+16),(86*w,sh+150),(70*w,hip+30),(-70*w,hip+30),(-84*w,sh+150)])
    bc = P["a"] if p["top"] == 0 else sk if p["top"] == 1 and not p["f"] else P["c"]; put(c, body, bc, p)
    if bc != sk: pattern(c, body, p["pat"], mix(bc,g,.75), (-120*w,sh-20,120*w,hip+40))
    ln = {"skirt":-24,"dhoti":-150*k,"robe":-40,"pyjama":-230*k}[p["bottom"]]; fl = {"skirt":150,"dhoti":88,"robe":104,"pyjama":110}[p["bottom"]]*w; lc = P["c"] if bc == P["a"] else P["a"]
    if p["role"] == "dev": lc = (244,190,50)
    sway = sin(t*2+1)*8 - 20*min(1,walk) + sin(ph*2-1)*8*walk; sk_ = poly([(-68*w,hip-10),(68*w,hip-10),(fl+sway,ln),(fl*.5+sway,ln+16),(sway,ln),(-fl*.5+sway,ln+16),(-fl+sway,ln)]); put(c, sk_, lc, p); pattern(c, sk_, p["pat2"], mix(lc,g,.7), (-180*w,hip+20,180*w,ln-40))
    c.save(); c.clipPath(sk_,True); c.drawLine(-260,ln-18,260,ln-18,line(g,20)); c.drawLine(-260,ln-40,260,ln-40,line(P["a"] if lc!=P["a"] else P["c"],7)); c.restore()
    put(c, poly([(-76*w,hip-26),(76*w,hip-26),(74*w,hip+14),(-74*w,hip+14)]), g, p); put(c, oval(10,hip-6,20), P["a"], p)
    if p["top"]: put(c, poly([(-70*w,sh-10),(-26*w,sh-16),(80*w,hip-10),(40*w,hip-10)]), P["a"], p)
    c.save(); c.translate(6,sh-16); c.rotate(sin(t*2.4)*2 - 1 + sin(2*ph-.6)*1.5*walk); head(c,p,talk,mood,t); c.restore()
    for i in range(p["neck"]+1):
        q = smooth([(-56*w,sh),(10,sh+80+i*34),(66*w,sh+2)],False); c.drawPath(q,line(ink(p) or (60,30,20),13)); c.drawPath(q,line([g,(250,244,230),P["c"]][i],8))
    arm(c,p,70*w,sh+40,a0+sin(t*2.6)*.05,a1+sin(t*2.2-.6)*.09,bc,p["prop"])
    c.restore()

# ---------------- places
def temple(c, x, y, w, h, rgb, n=5):
    c.drawPath(smooth([(x-w,y+40),(x-w*.9,y-h*.3),(x-w*.4,y-h*.8),(x,y-h*1.1),(x+w*.4,y-h*.8),(x+w*.9,y-h*.3),(x+w,y+40)]),fill(rgb)); [c.drawLine(x-w*(1-i/n)*.9,y-h*i/n*.9,x+w*(1-i/n)*.9,y-h*i/n*.9,line(mix(rgb,(255,255,255),.14),4)) for i in range(1,n)]
    c.drawLine(x,y-h*.95,x,y-h*1.3,line(rgb,6)); c.drawPath(poly([(x,y-h*1.3),(x+46,y-h*1.22),(x,y-h*1.14)]),fill((230,90,50)))
def arch(x, y0, y1, w, cusps=7):
    q = skia.Path(); q.moveTo(x-w,y1); q.lineTo(x-w,y0+w*.75)
    pt = lambda u: (x-w*cos(u*pi), y0+w*.75-sin(u*pi)*w*.75)
    for i in range(cusps): a, b = pt(i/cusps), pt((i+1)/cusps); m = ((a[0]+b[0])/2,(a[1]+b[1])/2); q.quadTo(m[0]+(m[0]-x)*.28,m[1]+(m[1]-y0-w*.75)*.28,*b)
    q.lineTo(x+w,y1); q.close(); return q
    p = [(x-w,y1)]; [p.append((x-w*cos(i/(cusps*8)*pi)*(1-.07*abs(sin(i/8*pi))), y0+w*.9-sin(i/(cusps*8)*pi)**.8*w*1.1*(1-.07*abs(sin(i/8*pi))))) for i in range(cusps*8+1)]; p.append((x+w,y1)); return poly(p)
def place(c, r, kind, time, pal, t, gy=1330):
    top, bot, far, near, gr, lt = TIMES[time]; vgrad(c,[(0,top),(1,bot)],0,gy+40); r = random.Random(r.random())
    if time in ("night","storm"):
        for _ in range(60 if time=="night" else 0): x,y,q=r.uniform(0,W),r.uniform(0,900),r.uniform(1,4); c.drawCircle(x,y,q*(1+.3*sin(t*3+x)),fill((255,246,210),.8))
    mx, my = r.uniform(220,860), r.uniform(330,620); glow(c,mx,my,360,lt,.55); (time!="storm") and c.drawCircle(mx,my,r.uniform(60,120),fill(lt,.95))
    if time == "storm": c.drawPath(poly([(mx,my),(mx-50,my+200),(mx+10,my+190),(mx-60,my+470),(mx+70,my+150),(mx+14,my+160)]),fill((240,255,255),.9))
    for i in range(r.randint(2,5)):
        x,y=(r.uniform(0,W)+t*8)%1300-100,r.uniform(160,640); [c.drawOval(skia.Rect.MakeXYWH(x+q*60-120,y-abs(2-q)*-12,150,50),fill(mix(top,(255,255,255),.25),.55)) for q in range(5)]
    hills = lambda y,a,rgb,f: c.drawPath(poly([(0,H)]+[(x,y+sin(x/f+mx)*a+sin(x/f*2.3)*a*.4) for x in range(0,W+20,20)]+[(W,H)]),fill(rgb))
    hills(gy-230,60,far,210)
    if kind in ("palace","ghat"):
        for _ in range(r.randint(4,7)): temple(c,r.uniform(0,W),gy-90,r.uniform(60,130),r.uniform(220,480),mix(far,near,r.random()))
    if kind == "desert": hills(gy-120,90,mix(far,gr,.5),300); hills(gy-40,50,near,160)
    if kind in ("forest","village"):
        for _ in range(9 if kind=="forest" else 4):
            x=r.uniform(-40,W+40); th=r.uniform(360,900 if kind=="forest" else 560); lf=mix(near,(40,110,60),.45); c.drawPath(poly([(x-22,gy),(x-12,gy-th),(x+12,gy-th),(x+24,gy)]),fill(mix(near,(70,40,30),.5)))
            [c.drawCircle(x+sin(q*1.3)*95,gy-th+cos(q*1.3)*70,r.uniform(70,120),fill(mix(lf,(0,0,0),q*.05))) for q in range(6)]
            [c.drawCircle(x+r.uniform(-120,120),gy-th+r.uniform(-100,100),10,fill(pal["b"])) for _ in range(6)]
    if kind == "village":
        for x in (r.uniform(60,260),r.uniform(800,1000)):
            h=r.uniform(230,330); c.drawRect(skia.Rect.MakeLTRB(x-150,gy-h,x+150,gy+20),fill((196,140,96))); c.drawPath(poly([(x-200,gy-h+20),(x,gy-h-190),(x+200,gy-h+20)]),fill((164,116,56))); c.drawRect(skia.Rect.MakeLTRB(x-44,gy-160,x+44,gy+20),fill((70,40,36)))
            [c.drawPath(poly([(x-140+q*40,gy-h+60),(x-125+q*40,gy-h+36),(x-110+q*40,gy-h+60)]),fill((250,240,220))) for q in range(7)]
    if kind == "battle":
        for i in range(16): x=r.uniform(0,W); hh=r.uniform(160,420); c.drawLine(x,gy,x+r.uniform(-40,40),gy-hh,line(mix(near,(0,0,0),.4),7)); (i%2==0) and c.drawPath(poly([(x,gy-hh),(x+110+sin(t*4+i)*12,gy-hh+34),(x,gy-hh+80)]),fill(mix(pal["a"],near,.35)))
    c.drawRect(skia.Rect.MakeLTRB(0,gy,W,H),fill(gr)); c.drawRect(skia.Rect.MakeLTRB(0,gy,W,gy+10),fill(mix(gr,lt,.35)))
    if kind == "ghat":
        c.drawRect(skia.Rect.MakeLTRB(0,gy-110,W,gy+60),fill(mix((30,80,130),top,.4))); [c.drawLine(r.uniform(0,600),y,r.uniform(600,W),y+sin(t*2+y)*4,line(lt,3,.25)) for y in range(gy-95,gy+50,26)]; [c.drawRect(skia.Rect.MakeLTRB(0,gy+50+q*120,W,gy+66+q*120),fill(mix(gr,lt,.3))) or c.drawRect(skia.Rect.MakeLTRB(0,gy+66+q*120,W,gy+96+q*120),fill(mix(gr,(0,0,0),.3))) for q in range(6)]
        [(glow(c,x,gy-80+r.uniform(0,110),50,(255,190,80),.7)) for x in range(100,1050,190)]
    if kind == "palace":
        c.save(); hole = arch(W/2,420,gy,430); fr = skia.Path(); fr.addRect(skia.Rect.MakeLTRB(0,0,W,gy)); wall = skia.Op(fr,hole,skia.kDifference_PathOp); wc=mix(pal["a"],top,.35); c.drawPath(wall,fill(wc)); pattern(c,wall,r.randrange(5),mix(wc,pal["b"],.4),(0,60,W,gy)); c.drawPath(hole,line(pal["b"],16)); c.drawPath(hole,line(pal["c"],5)); c.restore()
        for y in range(gy+40,H,90): c.drawLine(0,y,W,y,line(mix(gr,lt,.25),3)); 
        for q in range(-6,7): c.drawLine(W/2+q*80,gy,W/2+q*260,H,line(mix(gr,lt,.25),3))
def front(c, r, kind, time, pal, gy=1330):
    gr, lt = TIMES[time][4:]
    if kind in ("palace","ghat"):
        for k in range(3): c.drawOval(skia.Rect.MakeLTRB(540-420+k*110,1560-70+k*18,540+420-k*110,1560+70-k*18),line(mix(gr,pal["b"],.6),5))
        for i in range(24): c.drawCircle(540+cos(i/24*2*pi)*420,1560+sin(i/24*2*pi)*70,9,fill([pal["a"],pal["b"]][i%2]))
        return
    for _ in range(46):
        x, y = r.uniform(0,W), r.uniform(gy+30,H); k = .5+(y-gy)/500
        if kind in ("forest","village") :
            [c.drawLine(x+q*9*k,y,x+q*20*k,y-34*k,line(mix(gr,(60,140,70),.5),6*k)) for q in (-1,0,1)]
            if r.random() < .35: c.drawCircle(x,y-40*k,9*k,fill(r.choice([pal["a"],pal["b"],(250,240,230)])))
        elif kind == "battle" and r.random() < .4: c.drawLine(x,y,x+50*k,y-120*k,line((60,36,30),6*k)); c.drawPath(poly([(x+50*k,y-120*k),(x+38*k,y-86*k),(x+66*k,y-92*k)]),fill(pal["a"]))
        else: c.drawOval(skia.Rect.MakeXYWH(x,y,50*k,16*k),fill(mix(gr,[lt,(0,0,0)][r.random()<.6],.25)))
def _surface(c, craft, pal, r):
    """What the whole picture is made of."""
    if craft == "kathputli":
        for s in (0,1):
            for i in range(3): x=s*(W-26)+(-1 if s else 1)*i*24; c.drawRect(skia.Rect.MakeXYWH(x,0,28,H),fill(mix(pal["a"],(0,0,0),.15+.3*(i%2))))
        for i in range(10): c.drawPath(smooth([(i*120-70,-30),(i*120-60,150),(i*120,210),(i*120+60,150),(i*120+70,-30)]),fill(mix(pal["a"],(0,0,0),.2*(i%2)))); c.drawCircle(i*120,205,10,fill(pal["b"]))
    if craft == "miniature":
        for k,(rgb,w) in enumerate([(pal["c"],76),(pal["b"],14),(pal["a"],8)]): o=[0,44,62][k]; c.drawRect(skia.Rect.MakeLTRB(o,o,W-o,H-o),skia.Paint(Color=col(rgb),Style=skia.Paint.kStroke_Style,StrokeWidth=w if k else 90))
        for y in range(30,H,70): [c.drawCircle(x,y,8,fill(pal["b"])) for x in (20,W-20)]
        for x in range(60,W-40,70): [c.drawCircle(x,y,8,fill(pal["b"])) for y in (20,H-20)]
    sh = dict(kathputli=.10,leather=.16,paper=.13,miniature=.12)[craft]; n = None
    if n: c.drawPaint(skia.Paint(Shader=n,Alphaf=sh*2,BlendMode=skia.BlendMode.kSoftLight))
    if craft == "leather": c.drawPaint(skia.Paint(Color=col((255,150,50),.16),BlendMode=skia.BlendMode.kMultiply))
    c.drawPaint(skia.Paint(Shader=skia.GradientShader.MakeRadial(skia.Point(W/2,H*.46),1250,[col((0,0,0),0),col((0,0,0),.6)],[.5,1])))

_CACHE = {}
def surface(c, craft, pal, r):
    k = (craft, tuple(pal["a"]))
    if k not in _CACHE:
        s1, s2 = skia.Surface(W, H), skia.Surface(W, H); _surface(s1.getCanvas(), craft, pal, r); sh = dict(kathputli=.10,leather=.16,paper=.13,miniature=.12)[craft]
        s2.getCanvas().drawPaint(skia.Paint(Shader=skia.PerlinNoiseShader.MakeFractalNoise(.75,.75,3,7), Alphaf=sh*2)); _CACHE[k] = s1.makeImageSnapshot(), s2.makeImageSnapshot()
    a, b = _CACHE[k]; c.drawImage(b, 0, 0, skia.SamplingOptions(), skia.Paint(BlendMode=skia.BlendMode.kSoftLight)); c.drawImage(a, 0, 0)

def look(seed, used=()):
    """The whole look of one video. `used`: (craft, place, time) of the last videos, not to be repeated."""
    r = random.Random(seed)
    while True:
        k = (r.choice(CRAFTS), r.choice(PLACES), r.choice(list(TIMES)))
        if all(sum(a == b for a, b in zip(k, u)) == 0 for u in used[-2:]) and all(k != u for u in used): break
    roles = r.sample(list(ROLES), 2); pals = r.sample(SETS, 2)
    return dict(key=k, pal=pals[0], cast=[person(r, q, k[0], pals[i]) for i, q in enumerate(roles)], seed=seed, layout=r.choice(["two","close","low","solo"]))
def still(L, t=1.0):
    s = skia.Surface(W,H); c = s.getCanvas(); craft, pl, tm = L["key"]; r = random.Random(L["seed"]); a, b = L["cast"]; lay = L["layout"]
    place(c, r, pl, tm, L["pal"], t); front(c, r, pl, tm, L["pal"]); A = r.choice([(.3,.9),(.5,1.7),(1.2,2.3),(1.6,1.5),(.1,1.9),(2.0,2.8),(.9,2.6)]); B = r.choice([(.2,.6),(.9,2.2),(1.5,1.6),(.1,1.6)]); m, n = r.choice(["happy","angry","sad","n"]), r.choice(["happy","angry","sad","n"])
    if lay == "two": puppet(c,a,300,1560,1.22,t,1,.5,m,A); puppet(c,b,800,1560,1.22,t,-1,0,n,B)
    elif lay == "close": puppet(c,a,470,2060,1.75,t,1,.7,m,A)
    elif lay == "low": puppet(c,b,830,1440,.85,t,-1,0,n,B); puppet(c,a,320,1720,1.4,t,1,.5,m,A)
    else: glow(c,540,1000,620,TIMES[tm][5],.4); puppet(c,a,500,1620,1.4,t,1,.3,m,A)
    surface(c, craft, L["pal"], r); return s.makeImageSnapshot()
if __name__ == "__main__":
    from PIL import Image
    o = Image.new("RGB",(4*480,2*853)); used = []
    for i in range(8):
        L = look(101+i, used); used.append(L["key"]); print(i+1, L["key"], [p["role"] for p in L["cast"]], L["layout"])
        o.paste(Image.fromarray(still(L).toarray(colorType=skia.kRGBA_8888_ColorType)).convert("RGB").resize((480,853)), (i%4*480, i//4*853))
    o.save(__import__("os").path.join(__import__("lab").OUT, "preview_puppet.jpg"), quality=90)
