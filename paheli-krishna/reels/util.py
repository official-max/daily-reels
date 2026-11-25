"""Small shared helpers: easing, curves, a 2x-scale drawing pen, blinking, ffmpeg."""

from PIL import ImageDraw
from .config import SS as S


def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))

def lerp(a, b, t): return a + (b - a) * t

def ease_io(t): t = clamp(t); return t * t * (3 - 2 * t)

def ease_out(t): t = clamp(t); return 1 - (1 - t) ** 3

def ease_back(t):
    t = clamp(t); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2

def darker(c, f=0.72): return tuple(int(v * f) for v in c[:3])

def cubic(p0, p1, p2, p3, n=24):
    out = []
    for i in range(n + 1):
        t = i / n; m = 1 - t
        out.append((m**3*p0[0] + 3*m*m*t*p1[0] + 3*m*t*t*p2[0] + t**3*p3[0],
                    m**3*p0[1] + 3*m*m*t*p1[1] + 3*m*t*t*p2[1] + t**3*p3[1]))
    return out

class Pen:
    def __init__(self, img): self.d = ImageDraw.Draw(img, "RGBA")
    def ell(self, cx, cy, rx, ry=None, fill=None, outline=None, w=0):
        ry = rx if ry is None else ry
        if rx <= 0.2 or ry <= 0.2: return
        self.d.ellipse([(cx-rx)*S, (cy-ry)*S, (cx+rx)*S, (cy+ry)*S], fill=fill, outline=outline, width=max(1, int(round(w*S))) if outline else 0)
    def poly(self, pts, fill=None, outline=None, w=0):
        self.d.polygon([(x*S, y*S) for x, y in pts], fill=fill, outline=outline, width=max(1, int(round(w*S))) if outline else 1)
    def line(self, pts, fill, w, caps=True):
        self.d.line([(x*S, y*S) for x, y in pts], fill=fill, width=max(1, int(round(w*S))), joint="curve")
        if caps and w >= 3:
            for x, y in (pts[0], pts[-1]): self.ell(x, y, w/2, fill=fill)
    def arc(self, cx, cy, rx, ry, a0, a1, fill, w):
        self.d.arc([(cx-rx)*S, (cy-ry)*S, (cx+rx)*S, (cy+ry)*S], a0, a1, fill=fill, width=max(1, int(round(w*S))))
    def chord(self, cx, cy, rx, ry, a0, a1, fill):
        self.d.chord([(cx-rx)*S, (cy-ry)*S, (cx+rx)*S, (cy+ry)*S], a0, a1, fill=fill)
    def rect(self, x0, y0, x1, y1, fill):
        self.d.rectangle([x0*S, y0*S, x1*S, y1*S], fill=fill)

def blink(t):
    ph = t % 3.3
    return max(0.08, abs(ph - 0.07) / 0.07) if ph < 0.14 else 1.0

def ffmpeg_exe():
    import imageio_ffmpeg; return imageio_ffmpeg.get_ffmpeg_exe()
