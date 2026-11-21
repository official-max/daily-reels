"""
Daily reel pipeline:  series (Claude) -> today's part -> render -> YouTube upload -> state.

Each series has 2-3 parts and one part is posted per day. When a series ends, the next one is the other kind
(paheli <-> devotional). The active series is kept in state/series.json, so every part of a story stays consistent.

    python -m reels.pipeline                                    # full daily run (needs secrets in env)
    python -m reels.pipeline --no-upload                        # test run: renders today's part, uploads nothing
    python -m reels.pipeline --script samples/paheli_01.json --part 2 --preview
"""
import os, sys, json, glob, argparse, random, datetime as dt
from . import story_base as ms, media, engine, writer, youtube

ROOT = ms.HERE
OUT = os.path.join(ROOT, "out")
HISTORY = os.path.join(ROOT, "state", "history.json")
SERIES = os.path.join(ROOT, "state", "series.json")
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))


def log(*a): print(*a, flush=True)


def load_json(path, default):
    try: return json.load(open(path, encoding="utf-8"))
    except Exception: return default


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def as_series(d):
    """A sample/script file is either a series {parts:[...]} or a single reel; return a series."""
    if d.get("parts"): return d
    return dict(series_title=d.get("yt_title", "")[:30], type=d.get("type", "devotional"), parts=[d])


def fallback_series(kind, history):
    used = {h.get("series") for h in history}
    pool = [as_series(json.load(open(p, encoding="utf-8"))) for p in sorted(glob.glob(os.path.join(ROOT, "samples", "*.json")))]
    pool = [s for s in pool if s.get("type") == kind] or [s for s in pool if s.get("type") in writer.KINDS]
    fresh = [s for s in pool if s.get("series_title") not in used]
    return random.choice(fresh or pool)


def warn(title, msg):
    if os.environ.get("GITHUB_ACTIONS"):  # shows up on the run's summary page
        msg = msg[:900].replace("%", "%25").replace("\r", "").replace("\n", "%0A")
        print(f"::warning title={title}::{msg}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--type", default="auto", help="auto / paheli / devotional (forces a new series of that kind)")
    ap.add_argument("--script", help="use a local script/series JSON instead of the series state")
    ap.add_argument("--part", type=int, default=1, help="with --script: which part to render")
    ap.add_argument("--no-upload", action="store_true")
    ap.add_argument("--preview", action="store_true", help="only render a contact sheet")
    ap.add_argument("--post-time", default="19:00", help="publish time IST, HH:MM")
    a = ap.parse_args()

    os.makedirs(OUT, exist_ok=True)
    today = dt.datetime.now(IST).date()
    history = load_json(HISTORY, [])
    state = load_json(SERIES, {"active": None, "last_kind": None})
    yt = None if a.no_upload else youtube.client()

    if a.script:
        series = as_series(json.load(open(a.script, encoding="utf-8")))
        idx = max(0, min(a.part, len(series["parts"])) - 1); from_state = False
    else:
        series = state.get("active")
        if a.type in writer.KINDS and series and series.get("type") != a.type:
            series = None
        if not series or series.get("next", 0) >= len(series.get("parts", [])):
            last = state.get("last_kind")
            kind = a.type if a.type in writer.KINDS else ("devotional" if last == "paheli" else "paheli")
            trends = writer.trending(yt)
            log(f"new {kind} series ({len(trends)} trending titles collected)")
            try:
                series = writer.write_series(kind, today.strftime("%d %B %Y, %A"), trends, [h.get("title", "") for h in history],
                                             [h["story"] for h in history if h.get("story")])
                if series.get("_story"): log("story from references:", series["_story"])
            except Exception as e:
                log("Claude series failed, using a sample instead:", repr(e))
                warn("Claude script failed, sample used", repr(e))
                series = fallback_series(kind, history)
            series = dict(series, next=0)
            state["active"] = series
            save_json(SERIES, state)   # kept even on test runs, so the real run posts this same Part 1
        idx = series["next"]; from_state = True

    kind = series.get("type", "paheli"); n = len(series["parts"]); part = series["parts"][idx]
    lab = (part.get("label") or ("PAHELI" if kind == "paheli" else "KAHANI")).upper()
    raw = dict(part, type=kind, label=f"{lab} · PART {idx + 1}/{n}" if n > 1 else lab)
    script = media.normalize(raw)
    json.dump(raw, open(os.path.join(OUT, "script.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    log(f"series={series.get('series_title')!r} part {idx + 1}/{n} type={kind} title={script['yt_title']!r} shots={len(script['shots'])}")

    tl, voices = media.build_timeline(script, os.path.join(OUT, "voice"))
    log(f"timeline {tl['total']:.1f}s, {len(tl['phrases'])} lines")
    if a.preview:
        engine.preview(tl, os.path.join(OUT, "preview.jpg")); log("preview ->", os.path.join(OUT, "preview.jpg")); return
    mp4 = engine.render(tl, voices, os.path.join(OUT, "reel.mp4"), log=log)
    log("rendered ->", mp4)

    if a.no_upload:
        log("test run (no upload): this part stays queued for the next real run")
        return
    if yt is None: sys.exit("YouTube secrets missing (YT_CLIENT_ID / YT_CLIENT_SECRET / YT_REFRESH_TOKEN)")
    hh, mm = map(int, a.post_time.split(":"))
    publish = dt.datetime(today.year, today.month, today.day, hh, mm, tzinfo=IST).astimezone(dt.timezone.utc)
    vid, status = youtube.upload(yt, mp4, script["yt_title"], script["yt_description"], script.get("tags", []), publish)
    log(f"uploaded https://youtube.com/shorts/{vid}  status={status}")

    entry = dict(date=str(today), type=kind, series=series.get("series_title"), part=f"{idx + 1}/{n}",
                 title=script["yt_title"], seconds=round(tl["total"], 1), video_id=vid)
    if series.get("_story"): entry["story"] = series["_story"]
    history.append(entry); save_json(HISTORY, history[-200:])
    if from_state:
        series["next"] = idx + 1
        if series["next"] >= n:
            state["active"], state["last_kind"] = None, kind
        else:
            state["active"] = series
        save_json(SERIES, state)


if __name__ == "__main__":
    main()
