"""Script (what Claude writes) -> timeline (what the renderer needs).

clean_script(): keeps only scenes/speakers the engine can draw for the format and picks a camera for every shot.
build_timeline(): makes the voices, measures them and lays out start/end times for every line and shot.
"""
import os, json, hashlib, asyncio
from .config import FORMATS, VOICES, MOODS, ICONS, GAP, SR
from .audio import tts_all, decode, lip_env


def _squash(text, n):
    return " ".join((text or "").replace("*", "").split())[:n]


def _main_speaker(lines):
    spk = [l[0] for l in lines]
    return max(set(spk), key=spk.count)


def clean_script(script):
    """Clamp a script to what the renderer can draw. Returns a new dict with render-ready shots."""
    kind = script["type"]; fmt = FORMATS[kind]
    shots = []
    for raw in script["shots"]:
        scene = raw.get("scene") if raw.get("scene") in fmt["scenes"] else fmt["default_scene"]
        mood = raw.get("mood") if raw.get("mood") in MOODS else "neutral"
        lines = []
        for ln in raw.get("lines", []):
            spk = ln.get("speaker") if ln.get("speaker") in fmt["speakers"] else "N"
            if scene == "walk": spk = "N"                                  # walking shot: narrator only
            if scene == "divine" and spk not in ("K", "N"): spk = "N"
            hi, cap = (ln.get("hindi") or "").strip(), (ln.get("caption") or "").strip()
            if cap.count("*") % 2: cap = cap.replace("*", "")
            if hi and cap: lines.append((spk, hi, cap))
        if not lines:
            continue
        sh = dict(kind=scene, phrases=lines, sticker=_squash(raw.get("sticker"), 26).upper())
        top = _main_speaker(lines)
        if scene == "darbar":
            n_before = sum(1 for x in shots if x["kind"] == "darbar")
            # the person the shot is about gets the mood; a stunned court makes the clever man smile
            rmood, cmood = ("neutral", mood) if top == "C" else (mood, "happy" if mood == "shock" else "neutral")
            sh.update(cam={"R": "raja", "C": "chatur"}.get(top, "wide" if n_before % 2 == 0 else "both"), rmood=rmood, cmood=cmood,
                      cards=[dict(icon=c["icon"] if c.get("icon") in ICONS else "question", label=_squash(c.get("label"), 16))
                             for c in (raw.get("cards") or [])[:2] if isinstance(c, dict)])
        elif scene == "meet":
            first = not any(x["kind"] == "meet" for x in shots)
            cam = {"A": "a", "P": "p", "K": "k"}.get(top, "wide" if first else "ka")
            pm = {"sad": "sad", "happy": "happy"}.get(mood, "listen")
            sh.update(cam=cam, pmood=pm, arrive=first and cam == "wide", alook=1 if top == "A" else -1, klook=1)
        shots.append(sh)
    if not shots:
        raise ValueError("script has no usable shots")
    shots[0]["lead"] = 1.6     # room for the title card
    shots[-1]["tail"] = 3.6    # room for the end card
    return dict(script, shots=shots)


def build_timeline(script, voice_dir):
    """Returns (timeline, voices). Voices are cached as mp3 files keyed by speaker + text."""
    os.makedirs(voice_dir, exist_ok=True)
    items = []
    for s in script["shots"]:
        for spk, hi, _ in s["phrases"]:
            key = hashlib.md5(json.dumps([spk, hi, VOICES[spk]], ensure_ascii=False).encode()).hexdigest()[:12]
            items.append((os.path.join(voice_dir, f"{spk}_{key}.mp3"), hi, spk))
    asyncio.run(tts_all(items))
    voices = [decode(p) for p, _, _ in items]

    named = FORMATS[script["type"]]["named"]
    t, k, phrases, shots = 0.0, 0, [], []
    for s in script["shots"]:
        st = t; t += s.get("lead", 0.35)
        for j, (spk, hi, ro) in enumerate(s["phrases"]):
            if j: t += GAP
            d = len(voices[k]) / SR
            phrases.append(dict(start=t, end=t + d, text=ro, spk=spk, idx=k, env=lip_env(voices[k]),
                                tag=script.get("p_name") if spk == named else None))
            t += d; k += 1
        narr_end = t - st; t += s.get("tail", 0.45)
        shots.append({**{kk: vv for kk, vv in s.items() if kk != "phrases"}, "start": st, "end": t, "dur": t - st, "narr_end": narr_end})
    tl = dict(shots=shots, phrases=phrases, total=t, type=script["type"], label=script["label"],
              title1=script["title_line1"], title2=script["title_line2"], title_sub=script["title_sub"],
              end_text=script["end_text"], end_sub=script["end_sub"], hook=(script.get("hook") or "").strip()[:40])
    return tl, voices
