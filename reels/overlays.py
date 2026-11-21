"""Text and graphic overlays: captions, title card, end card, hook bar, sticker, icon cards, pill."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from .config import W, FONT_CAP, FONT_B, TAGS

CACHE = {}   # fonts + rendered overlays (cleared per reel by render.start())


def fonts():
    if "f_cap" not in CACHE:
        CACHE["f_cap"] = ImageFont.truetype(FONT_CAP, 74)
        CACHE["f_b"] = ImageFont.truetype(FONT_B, 46)
        CACHE["f_tag"] = ImageFont.truetype(FONT_B, 40)
        CACHE["f_big"] = ImageFont.truetype(FONT_CAP, 100)
        CACHE["f_btn"] = ImageFont.truetype(FONT_CAP, 60)
    return CACHE

def parse_tokens(text):
    toks, cur, hl, state = [], "", False, False
    for ch in text:
        if ch == "*": state = not state; continue
        if ch == " ":
            if cur: toks.append((cur, hl)); cur = ""
            continue
        if not cur: hl = state
        cur += ch
    if cur: toks.append((cur, hl))
    return toks

def ctext(d, cx, y, txt, font, fill, stroke=6, sfill=(18, 14, 24)):
    tw = font.getlength(txt); d.text((cx - tw / 2, y), txt, font=font, fill=fill, stroke_width=stroke, stroke_fill=sfill)

def make_caption(text, spk, tag=None):
    f = fonts(); font = f["f_cap"]; sp = font.getlength(" ")
    lines, cur, cw = [], [], 0
    for w, hl in parse_tokens(text):
        ww = font.getlength(w)
        if cur and cw + sp + ww > 950: lines.append(cur); cur, cw = [], 0
        cw = ww if not cur else cw + sp + ww; cur.append((w, hl, ww))
    lines.append(cur)
    lh = int(font.size * 1.22); top = 78 if spk in TAGS else 18
    img = Image.new("RGBA", (W, top + lh * len(lines) + 40), (0, 0, 0, 0)); shd = img.copy()
    d, ds = ImageDraw.Draw(img), ImageDraw.Draw(shd)
    if spk in TAGS:
        name, col = TAGS[spk]; name = tag or name; tf = f["f_tag"]; tw = tf.getlength(name)
        d.rounded_rectangle([W/2 - tw/2 - 26, 6, W/2 + tw/2 + 26, 64], radius=29, fill=col + (235,), outline=(255, 255, 255), width=3)
        d.text((W/2 - tw/2, 9), name, font=tf, fill=(255, 255, 255))
    for li, line in enumerate(lines):
        lw = sum(x[2] for x in line) + sp * (len(line) - 1); x = (W - lw) / 2; y = top + li * lh
        for w, hl, ww in line:
            ds.text((x + 4, y + 8), w, font=font, fill=(0, 0, 0, 160), stroke_width=9, stroke_fill=(0, 0, 0, 160))
            d.text((x, y), w, font=font, fill=(255, 212, 0) if hl else (255, 255, 255), stroke_width=7, stroke_fill=(18, 16, 22))
            x += ww + sp
    shd = shd.filter(ImageFilter.GaussianBlur(7)); shd.alpha_composite(img)
    return shd

def fit(text, font, maxw):
    size = font.size
    while size > 30 and ImageFont.truetype(font.path, size).getlength(text) > maxw: size -= 4
    return ImageFont.truetype(font.path, size)

def make_title(label, l1, l2, sub):
    f = fonts(); img = Image.new("RGBA", (W, 470), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    d.rounded_rectangle([90, 40, W - 90, 450], radius=46, fill=(25, 12, 40, 165), outline=(245, 195, 60), width=5)
    tw = f["f_b"].getlength(label)
    d.rounded_rectangle([W/2 - tw/2 - 30, 70, W/2 + tw/2 + 30, 136], radius=33, fill=(245, 195, 60))
    d.text((W/2 - tw/2, 72), label, font=f["f_b"], fill=(60, 20, 30))
    ctext(d, W/2, 150, l1, fit(l1, f["f_big"], 860), (255, 214, 70), 7)
    ctext(d, W/2, 262, l2, fit(l2, f["f_big"], 860), (255, 255, 255), 7)
    ctext(d, W/2, 380, sub, fit(sub, f["f_b"], 820), (255, 225, 190), 4)
    return img

def make_end(end_text, end_sub):
    f = fonts(); img = Image.new("RGBA", (W, 520), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    d.rounded_rectangle([110, 20, W - 110, 500], radius=46, fill=(20, 10, 35, 150))
    ctext(d, W/2, 40, end_text, fit(end_text, f["f_big"], 780), (255, 214, 70), 8)
    ctext(d, W/2, 180, end_sub, fit(end_sub, f["f_b"], 760), (255, 255, 255), 4)
    bw, bh, by = 560, 120, 330; bx = (W - bw) / 2
    d.rounded_rectangle([bx + 6, by + 10, bx + bw + 6, by + bh + 10], radius=60, fill=(0, 0, 0, 110))
    d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=60, fill=(240, 40, 80), outline=(255, 255, 255), width=6)
    ctext(d, W/2, by + 18, "SUBSCRIBE", f["f_btn"], (255, 255, 255), 0)
    return img

def make_hook(text):
    """White bar pinned to the top for the whole reel; *word* is shown in red."""
    font = fit(text.replace("*", ""), ImageFont.truetype(FONT_CAP, 56), 880)
    toks = parse_tokens(text); sp = font.getlength(" ")
    tw = sum(font.getlength(w) for w, _ in toks) + sp * (len(toks) - 1)
    bw = tw + 80; img = Image.new("RGBA", (W, 150), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    d.rounded_rectangle([(W - bw) / 2 + 5, 24, (W + bw) / 2 + 5, 134], radius=22, fill=(0, 0, 0, 90))
    d.rounded_rectangle([(W - bw) / 2, 16, (W + bw) / 2, 126], radius=22, fill=(255, 255, 255), outline=(25, 20, 30), width=4)
    x = (W - tw) / 2; y = 71 - font.size * 0.62
    for w, hl in toks:
        d.text((x, y), w, font=font, fill=(214, 30, 50) if hl else (25, 20, 30)); x += font.getlength(w) + sp
    return img

def make_sticker(text):
    """Tilted paper card that pops in at the start of a shot."""
    font = fit(text, ImageFont.truetype(FONT_CAP, 54), 560); tw = font.getlength(text)
    bw, bh = int(tw + 90), int(font.size * 1.75)
    img = Image.new("RGBA", (bw + 40, bh + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    d.rectangle([28, 30, bw + 28, bh + 30], fill=(0, 0, 0, 100))
    d.rectangle([16, 16, bw + 16, bh + 16], fill=(255, 246, 214), outline=(40, 30, 30), width=5)
    d.rectangle([bw / 2 - 40, 6, bw / 2 + 72, 30], fill=(250, 210, 90, 220))
    d.text((16 + (bw - tw) / 2, 16 + (bh - font.size * 1.25) / 2), text, font=font, fill=(200, 30, 45))
    return img.filter(ImageFilter.SMOOTH).rotate(-4, resample=Image.BICUBIC, expand=True)

def _icon(d, icon, cx, cy, r):
    """Simple bold icons drawn into a 2x-scale card."""
    ink, gold, red, green = (40, 26, 20), (240, 184, 60), (215, 40, 50), (40, 170, 90)
    w = max(4, int(r * 0.14))
    if icon == "gallows":
        d.line([(cx - r*0.6, cy + r), (cx + r*0.2, cy + r)], fill=ink, width=w)
        d.line([(cx - r*0.4, cy + r), (cx - r*0.4, cy - r)], fill=ink, width=w)
        d.line([(cx - r*0.4, cy - r), (cx + r*0.5, cy - r)], fill=ink, width=w)
        d.line([(cx + r*0.4, cy - r), (cx + r*0.4, cy - r*0.35)], fill=ink, width=max(3, w // 2))
        d.ellipse([cx + r*0.22, cy - r*0.4, cx + r*0.58, cy + r*0.05], outline=ink, width=max(3, w // 2))
    elif icon == "sword":
        d.polygon([(cx - r*0.75, cy + r*0.75), (cx + r*0.6, cy - r*0.6), (cx + r*0.85, cy - r*0.85), (cx + r*0.75, cy - r*0.45), (cx - r*0.6, cy + r*0.9)], fill=(200, 208, 220), outline=ink)
        d.line([(cx - r*0.85, cy + r*0.45), (cx - r*0.45, cy + r*0.95)], fill=gold, width=w)
        d.line([(cx - r*0.75, cy + r*0.75), (cx - r*0.95, cy + r*0.95)], fill=(120, 70, 40), width=w)
    elif icon == "question":
        f = ImageFont.truetype(FONT_CAP, int(r * 2.1)); tw = f.getlength("?")
        d.text((cx - tw / 2, cy - r * 1.45), "?", font=f, fill=gold, stroke_width=max(3, w // 2), stroke_fill=ink)
    elif icon == "tick":
        d.line([(cx - r*0.7, cy), (cx - r*0.2, cy + r*0.55), (cx + r*0.75, cy - r*0.6)], fill=green, width=int(w*1.6), joint="curve")
    elif icon == "cross":
        for a, b in (((-0.65, -0.65), (0.65, 0.65)), ((0.65, -0.65), (-0.65, 0.65))):
            d.line([(cx + a[0]*r, cy + a[1]*r), (cx + b[0]*r, cy + b[1]*r)], fill=red, width=int(w*1.6))
    elif icon == "coin":
        for k, (dx, dy) in enumerate(((-0.35, 0.3), (0.3, 0.35), (0, -0.2))):
            x, y = cx + dx*r, cy + dy*r
            d.ellipse([x - r*0.5, y - r*0.5, x + r*0.5, y + r*0.5], fill=gold, outline=(170, 110, 20), width=max(3, w // 2))
            d.ellipse([x - r*0.3, y - r*0.3, x + r*0.3, y + r*0.3], outline=(200, 140, 30), width=max(2, w // 3))
    elif icon == "door":
        d.rectangle([cx - r*0.55, cy - r*0.4, cx + r*0.55, cy + r], fill=(150, 90, 50), outline=ink, width=max(3, w // 2))
        d.pieslice([cx - r*0.55, cy - r*0.95, cx + r*0.55, cy + r*0.15], 180, 360, fill=(150, 90, 50), outline=ink, width=max(3, w // 2))
        d.ellipse([cx + r*0.25, cy + r*0.3, cx + r*0.4, cy + r*0.45], fill=gold)
    elif icon == "lamp":
        d.ellipse([cx - r*0.15, cy - r*0.95, cx + r*0.15, cy - r*0.2], fill=(255, 190, 60))
        d.ellipse([cx - r*0.07, cy - r*0.6, cx + r*0.07, cy - r*0.3], fill=(255, 245, 210))
        d.chord([cx - r*0.8, cy - r*0.5, cx + r*0.8, cy + r*0.7], 0, 180, fill=(190, 100, 50), outline=ink, width=max(3, w // 2))
    elif icon == "crown":
        d.polygon([(cx - r*0.8, cy + r*0.5), (cx - r*0.8, cy - r*0.4), (cx - r*0.4, cy), (cx, cy - r*0.7), (cx + r*0.4, cy), (cx + r*0.8, cy - r*0.4), (cx + r*0.8, cy + r*0.5)], fill=gold, outline=ink)
        d.ellipse([cx - r*0.12, cy + r*0.05, cx + r*0.12, cy + r*0.29], fill=red)
    elif icon == "clock":
        d.ellipse([cx - r*0.8, cy - r*0.8, cx + r*0.8, cy + r*0.8], fill=(255, 250, 235), outline=ink, width=w)
        d.line([(cx, cy), (cx, cy - r*0.55)], fill=ink, width=w); d.line([(cx, cy), (cx + r*0.4, cy + r*0.15)], fill=ink, width=w)

def make_card(icon, label):
    """Square card with an icon and a short caption under it (shown over a shot)."""
    k = 2; cw, ch = 300 * k, 330 * k
    img = Image.new("RGBA", (cw + 30*k, ch + 30*k), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    d.rounded_rectangle([18*k, 22*k, cw + 18*k, ch + 22*k], radius=34*k, fill=(0, 0, 0, 110))
    d.rounded_rectangle([8*k, 8*k, cw + 8*k, ch + 8*k], radius=34*k, fill=(250, 236, 205), outline=(226, 168, 66), width=8*k)
    _icon(d, icon, 8*k + cw / 2, 8*k + 125*k, 82*k)
    if label:
        f = fit(label, ImageFont.truetype(FONT_CAP, 40*k), 250*k); tw = f.getlength(label)
        d.text((8*k + (cw - tw) / 2, 8*k + 250*k), label, font=f, fill=(150, 24, 36))
    return img.resize((img.width // k, img.height // k), Image.LANCZOS)

def make_pill(text):
    font = ImageFont.truetype(FONT_B, 46); tw = font.getlength(text)
    img = Image.new("RGBA", (int(tw + 80), 96), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 8, tw + 80, 88], radius=40, fill=(15, 12, 20, 215), outline=(255, 255, 255, 230), width=3)
    d.text((40, 48 - font.size * 0.66), text, font=font, fill=(255, 255, 255))
    return img

def overlay(frame, im, cx, cy, scale, alpha):
    if alpha <= 0.01: return
    if abs(scale - 1) > 0.01:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BILINEAR)
    if alpha < 0.99:
        im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    frame.paste(im, (int(cx - im.width / 2), int(cy - im.height / 2)), im)
