"""
Daily reel pipeline:  trends -> Claude script -> render -> YouTube upload -> history.

    python -m reels.pipeline                          # full daily run (needs secrets in env)
    python -m reels.pipeline --script samples/motivational.json --no-upload
    python -m reels.pipeline --script samples/devotional.json --preview
"""
import os, sys, json, glob, argparse, random, datetime as dt
from . import story_base as ms, media, engine, writer, youtube

ROOT = ms.HERE
OUT = os.path.join(ROOT, "out")
HISTORY = os.path.join(ROOT, "state", "history.json")
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))


def log(*a): print(*a, flush=True)


def load_history():
    try: return json.load(open(HISTORY, encoding="utf-8"))
    except Exception: return []


def save_history(h):
    os.makedirs(os.path.dirname(HISTORY), exist_ok=True)
    json.dump(h[-200:], open(HISTORY, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def pick_kind(today, arg):
    if arg in ("devotional", "motivational"): return arg
    return "devotional" if today.toordinal() % 2 == 0 else "motivational"


def fallback_script(kind, history):
    used = {h.get("title") for h in history}
    pool = [json.load(open(p, encoding="utf-8")) for p in sorted(glob.glob(os.path.join(ROOT, "samples", "*.json")))]
    pool = [s for s in pool if s.get("type") == kind] or pool
    fresh = [s for s in pool if s.get("yt_title") not in used]
    return random.choice(fresh or pool)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--type", default="auto")
    ap.add_argument("--script", help="use a local script JSON instead of calling Claude")
    ap.add_argument("--no-upload", action="store_true")
    ap.add_argument("--preview", action="store_true", help="only render a contact sheet")
    ap.add_argument("--post-time", default="19:00", help="publish time IST, HH:MM")
    a = ap.parse_args()

    os.makedirs(OUT, exist_ok=True)
    now = dt.datetime.now(IST); today = now.date()
    history = load_history()
    yt = None if a.no_upload else youtube.client()

    if a.script:
        raw = json.load(open(a.script, encoding="utf-8")); kind = raw.get("type", "motivational")
    else:
        kind = pick_kind(today, a.type)
        trends = writer.trending(yt)
        log(f"{len(trends)} trending titles collected")
        try:
            raw = writer.write_script(kind, today.strftime("%d %B %Y, %A"), trends, [h.get("title", "") for h in history])
        except Exception as e:
            log("Claude script failed, using a sample script instead:", repr(e))
            raw = fallback_script(kind, history)
    raw["type"] = raw.get("type", kind)
    script = media.normalize(raw)
    json.dump(raw, open(os.path.join(OUT, "script.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    log(f"type={script['type']} title={script['yt_title']!r} shots={len(script['shots'])}")

    tl, voices = media.build_timeline(script, os.path.join(OUT, "voice"))
    log(f"timeline {tl['total']:.1f}s, {len(tl['phrases'])} lines")
    if a.preview:
        engine.preview(tl, os.path.join(OUT, "preview.jpg")); log("preview ->", os.path.join(OUT, "preview.jpg")); return
    mp4 = engine.render(tl, voices, os.path.join(OUT, "reel.mp4"), log=log)
    log("rendered ->", mp4)

    entry = dict(date=str(today), type=script["type"], title=script["yt_title"], seconds=round(tl["total"], 1))
    if not a.no_upload:
        if yt is None: sys.exit("YouTube secrets missing (YT_CLIENT_ID / YT_CLIENT_SECRET / YT_REFRESH_TOKEN)")
        hh, mm = map(int, a.post_time.split(":"))
        publish = dt.datetime(today.year, today.month, today.day, hh, mm, tzinfo=IST).astimezone(dt.timezone.utc)
        vid, status = youtube.upload(yt, mp4, script["yt_title"], script["yt_description"], script.get("tags", []), publish)
        log(f"uploaded https://youtube.com/shorts/{vid}  status={status}")
        entry.update(video_id=vid)
    history.append(entry); save_history(history)


if __name__ == "__main__":
    main()
