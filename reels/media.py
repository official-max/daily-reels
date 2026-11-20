"""Turn a validated script dict into a render timeline (voices, lip-sync, shot timing)."""
import os, json, hashlib, asyncio
from . import story_base as ms

DEVOTIONAL_SCENES = ("walk", "meet", "divine")
MOTIVATIONAL_SCENES = ("road", "night", "rain", "sunrise", "mountain")


def normalize(script):
    """Clamp an LLM-written script to what the renderer can draw. Returns a new dict."""
    kind = script.get("type", "motivational")
    allowed = DEVOTIONAL_SCENES if kind == "devotional" else MOTIVATIONAL_SCENES
    shots, first_meet = [], True
    for raw in script["shots"]:
        scene = raw.get("scene") if raw.get("scene") in allowed else allowed[1 if kind == "devotional" else 0]
        mood = raw.get("mood", "neutral")
        lines = []
        for ln in raw.get("lines", []):
            spk = ln.get("speaker", "N"); hi = (ln.get("hindi") or "").strip(); cap = (ln.get("caption") or "").strip()
            if not hi or not cap: continue
            if kind == "motivational" and spk not in ("N", "P"): spk = "N"
            if scene == "walk": spk = "N"
            if scene == "divine" and spk not in ("K", "N"): spk = "N"
            if cap.count("*") % 2: cap = cap.replace("*", "")
            lines.append((spk, hi, cap))
        if not lines: continue
        sh = dict(phrases=lines)
        pmood = {"sad": "sad", "happy": "happy"}.get(mood, "neutral")
        if scene == "road": sh.update(kind="walk", who="P", pmood=pmood)
        elif scene == "meet":
            spk = [l[0] for l in lines]
            top = max(set(spk), key=spk.count)
            cam = {"A": "a", "P": "p", "K": "k"}.get(top, "wide" if first_meet else "ka")
            sh.update(kind="meet", cam=cam, pmood=pmood if pmood != "neutral" else "listen", arrive=first_meet and cam == "wide",
                      alook=1 if top == "A" else -1, klook=1)
            first_meet = False
        else:
            sh.update(kind=scene, pmood=pmood)
        shots.append(sh)
    if not shots: raise ValueError("script has no usable shots")
    shots[0]["lead"] = 1.6
    shots[-1]["tail"] = 3.6
    return dict(script, type=kind, shots=shots)


def build_timeline(script, voice_dir):
    os.makedirs(voice_dir, exist_ok=True)
    items = []
    for s in script["shots"]:
        for spk, hi, _ in s["phrases"]:
            key = hashlib.md5(json.dumps([spk, hi, ms.VOICES[spk]], ensure_ascii=False).encode()).hexdigest()[:12]
            items.append((os.path.join(voice_dir, f"{spk}_{key}.mp3"), hi, spk))
    asyncio.run(ms.tts_all(items))
    voices = [ms.decode(p) for p, _, _ in items]
    t, k, phrases, shots = 0.0, 0, [], []
    for s in script["shots"]:
        st = t; t += s.get("lead", 0.35)
        for j, (spk, hi, ro) in enumerate(s["phrases"]):
            if j: t += ms.GAP
            d = len(voices[k]) / ms.SR
            phrases.append(dict(start=t, end=t + d, text=ro, spk=spk, idx=k, env=ms.lip_env(voices[k]),
                                tag=script.get("p_name") if spk == "P" else None)); t += d; k += 1
        ne = t - st; t += s.get("tail", 0.45)
        sd = {kk: vv for kk, vv in s.items() if kk != "phrases"}
        sd.update(start=st, end=t, dur=t - st, narr_end=ne); shots.append(sd)
    tl = dict(shots=shots, phrases=phrases, total=t, type=script["type"], nxt=None,
              label=script["label"], title1=script["title_line1"], title2=script["title_line2"], title_sub=script["title_sub"],
              end_text=script["end_text"], end_sub=script["end_sub"])
    return tl, voices
