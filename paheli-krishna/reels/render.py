"""Frame composition and video encoding.

frame = shot image (scenes.py) -> camera crop -> colour grade -> transition into the next shot
        -> overlays (hook bar, sticker, icon cards, pill, captions, title card, end card) -> fade out
"""
import os, math, subprocess
import numpy as np
from PIL import Image
from multiprocessing import Pool
from .config import W, H, FPS, SS, XF
from .util import clamp, lerp, ease_io, ease_back, ffmpeg_exe
from .canvas import blur
from . import overlays as ov, scenes, themes
from .scenes import SHOTS, TALK
from .audio import build_audio

TL = None          # the timeline being rendered (set per process by start())
TITLE_END = 2.6    # the title card is visible until this time (s)


def start(tl):
    """Make `tl` the current timeline and forget overlays cached for a previous one."""
    global TL
    TL = tl
    themes.use(tl["type"], tl.get("theme", 0))
    scenes.CACHE.clear()
    for k in [k for k in ov.CACHE if isinstance(k, tuple) or k in ("title", "end", "hook", "pill")]:
        del ov.CACHE[k]


def cached(key, make):
    if key not in ov.CACHE: ov.CACHE[key] = make()
    return ov.CACHE[key]


# ---------------------------------------------------------------- picture
def grade(fr):
    """Soft bloom on highlights, a little contrast and warmth, vignette."""
    a = np.asarray(fr, np.float32)
    hl = blur(np.clip((a.mean(axis=2) - 200) / 55, 0, 1), 24)
    a = 255 - (255 - a) * (1 - 0.32 * hl[..., None])
    a = 255 * (0.5 + (a / 255 - 0.5) * 1.07); a *= np.array(themes.THEME["tint"], np.float32)
    if "vig" not in ov.CACHE:
        yy, xx = np.mgrid[0:H, 0:W]; dd = np.sqrt(((xx - W/2) / (W*0.7))**2 + ((yy - H/2) / (H*0.7))**2)
        ov.CACHE["vig"] = (1 - 0.35 * np.clip(dd - 0.55, 0, 1))[..., None].astype(np.float32)
    a *= ov.CACHE["vig"]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB")


def render_shot(si, t):
    """One shot at local time t, cropped to its camera and graded."""
    s = TL["shots"][si]
    img, cam = SHOTS[s["kind"]](max(0.0, t), s)
    z = cam["zoom"]; vw, vh = W / z, H / z
    x0 = clamp(cam["cx"] - vw / 2, 0, W - vw); y0 = clamp(cam["cy"] - vh / 2, 0, H - vh)
    fr = img.resize((W, H), Image.BILINEAR, box=(x0*SS, y0*SS, (x0 + vw)*SS, (y0 + vh)*SS), reducing_gap=2.0)
    return grade(fr)


# ---------------------------------------------------------------- overlays
def active_lines(T):
    return [(k, ph) for k, ph in enumerate(TL["phrases"]) if ph["start"] - 0.05 <= T <= ph["end"] + 0.3]


def caption(k, ph):
    return cached(("cap", k), lambda: ov.make_caption(ph["text"], ph["spk"], ph.get("tag")))


def draw_sticker(frame, T, si, s, ts):
    """Tilted paper card for the first 2.6 s of a shot, placed below the current caption."""
    if not s.get("sticker") or s.get("cards") or T < TITLE_END + 0.1 or ts >= 2.6:
        return
    img = cached(("stk", s["sticker"]), lambda: ov.make_sticker(s["sticker"]))
    cap_bottom = max([230 + caption(k, ph).height - 30 for k, ph in active_lines(T)] or [0])
    a = max(0.0, ts - 0.15)
    ov.overlay(frame, img, W / 2 + (130 if si % 2 else -130), max(690, cap_bottom + img.height / 2 + 10),
               lerp(0.4, 1.0, ease_back(a / 0.3)), clamp(a / 0.08) * clamp((2.6 - ts) / 0.25))


def draw_cards(frame, s, ts):
    """One or two icon cards (paheli stakes), lower down in close-ups so faces stay visible."""
    cards = (s.get("cards") or [])[:2]
    if not cards or ts <= 0.3:
        return
    xs = [W / 2] if len(cards) == 1 else [W / 2 - 175, W / 2 + 175]
    y = 1020 if s.get("cam") == "wide" else 1400
    if s.get("cam") == "both":                     # over the carpet, away from Chatur
        xs = [x + (190 if themes.THEME["flip"] else -190) for x in xs] if len(cards) == 1 else xs
    for j, cd in enumerate(cards):
        img = cached(("card", cd["icon"], cd["label"]), lambda: ov.make_card(cd["icon"], cd["label"]))
        a = max(0.0, ts - 0.3 - j*0.25)
        ov.overlay(frame, img, xs[j], y, lerp(0.3, 1.0, ease_back(a / 0.3)), clamp(a / 0.08) * clamp((s["dur"] - ts) / 0.3))


def draw_overlays(frame, T, si, s, end_at):
    ts = T - s["start"]
    draw_sticker(frame, T, si, s, ts)
    draw_cards(frame, s, ts)
    pill_end = min(9.0, end_at - 0.5)
    if 2.8 < T < pill_end:
        ov.overlay(frame, cached("pill", lambda: ov.make_pill("Last tak zaroor dekhna")), W / 2, 1640, 1.0,
                   clamp((T - 2.8) / 0.3) * clamp((pill_end - T) / 0.3))
    if TL.get("hook"):
        ov.overlay(frame, cached("hook", lambda: ov.make_hook(TL["hook"])), W / 2, 95, 1.0, clamp((T - 0.1) / 0.25))
    for k, ph in active_lines(T):
        img = caption(k, ph); a = T - ph["start"] + 0.05
        ov.overlay(frame, img, W / 2, 330 + img.height / 2 - 100, lerp(0.6, 1.0, ease_back(a / 0.25)),
                   clamp(a / 0.1) * clamp((ph["end"] + 0.3 - T) / 0.2))
    if T < TITLE_END:
        img = cached("title", lambda: ov.make_title(TL["label"], TL["title1"], TL["title2"], TL["title_sub"]))
        ov.overlay(frame, img, W / 2, 860, lerp(0.7, 1.0, ease_back((T - 0.1) / 0.4)), clamp((T - 0.1) / 0.2) * clamp((TITLE_END - T) / 0.35))
    if T >= end_at:
        a = T - end_at
        ov.overlay(frame, cached("end", lambda: ov.make_end(TL["end_text"], TL["end_sub"])), W / 2, 460,
                   lerp(0.5, 1.0, ease_back(a / 0.35)) * (1 + 0.025*math.sin(a*6)*clamp(a - 0.4)), clamp(a / 0.15))


# ---------------------------------------------------------------- frame
def transition(a, b, u):
    """Frame between shot a and shot b, u = 0..1, in the theme's style."""
    cut = themes.THEME["cut"]
    if cut == "slide":
        x = int(W * ease_io(u)); out = Image.new("RGB", (W, H))
        out.paste(a, (-x, 0)); out.paste(b, (W - x, 0))
        return out
    if cut == "zoom":                              # push into the old shot while the new one fades in
        k = 1 + 0.5 * u * u; w, h = W / k, H / k
        a = a.resize((W, H), Image.BILINEAR, box=((W - w) / 2, (H - h) / 2, (W + w) / 2, (H + h) / 2))
    return Image.blend(a, b, ease_io(u))


def render_frame(fi):
    T = fi / FPS; shots = TL["shots"]
    TALK.clear()                                   # mouth openness per speaker for this frame
    for ph in TL["phrases"]:
        if ph["start"] <= T < ph["end"]:
            i = int((T - ph["start"]) * FPS)
            if i < len(ph["env"]): TALK[ph["spk"]] = ph["env"][i]
    si = next((i for i, s in enumerate(shots) if T < s["end"]), len(shots) - 1); s = shots[si]
    frame = render_shot(si, T - s["start"])
    if si + 1 < len(shots) and T > s["end"] - XF:   # transition into the next shot
        frame = transition(frame, render_shot(si + 1, T - shots[si + 1]["start"]), clamp((T - (s["end"] - XF)) / XF))
    last = shots[-1]
    draw_overlays(frame, T, si, s, end_at=last["start"] + last["narr_end"] + 0.4)
    if T > TL["total"] - 0.4:                      # fade to black
        frame = Image.blend(frame, Image.new("RGB", (W, H), (0, 0, 0)), clamp((T - (TL["total"] - 0.4)) / 0.4))
    return frame


def _frame_bytes(fi): return render_frame(fi).tobytes()


def render(tl, voices, out_mp4, workers=None, log=print):
    """Render a timeline to an mp4 (video + mixed audio)."""
    start(tl)
    log("warming sprite cache...")      # build character sprites once, before the worker processes start
    for sh in tl["shots"]:
        for f in (0.05, 0.4, 0.8): render_frame(int((sh["start"] + sh["dur"]*f) * FPS))
    wav = out_mp4[:-4] + ".wav"; build_audio(tl, voices, wav, seed=len(tl["phrases"]) * 7)
    nf = int(tl["total"] * FPS)
    cmd = [ffmpeg_exe(), "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out_mp4]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = workers or max(1, min(12, os.cpu_count() or 2))
    with Pool(n, initializer=start, initargs=(tl,)) as pool:
        for i, b in enumerate(pool.imap(_frame_bytes, range(nf), chunksize=4)):
            proc.stdin.write(b)
            if i % 300 == 0: log(f"  frame {i}/{nf}")
    proc.stdin.close()
    if proc.wait() != 0: raise RuntimeError("ffmpeg failed")
    return out_mp4


def preview(tl, path):
    """Contact sheet: two frames per shot."""
    start(tl); frames = []
    for sh in tl["shots"]:
        for f in (0.3, 0.8): frames.append(render_frame(int((sh["start"] + sh["dur"]*f) * FPS)).resize((270, 480)))
    cols = 6; rows = (len(frames) + cols - 1) // cols
    sheet = Image.new("RGB", (270*cols, 480*rows))
    for i, fr in enumerate(frames): sheet.paste(fr, ((i % cols)*270, (i // cols)*480))
    sheet.save(path, quality=85)
