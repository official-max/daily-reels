"""
One video:  next part of the active series -> render -> YouTube upload -> save state.

A series has 2-3 parts and each run posts the next part. When a series ends, the next one is the other format
(paheli <-> devotional). The active series lives in state/series.json, so all parts of a story stay consistent.

    python -m reels.pipeline                                            # daily run (needs the secrets in env)
    python -m reels.pipeline --no-upload                                # test: render today's part, upload nothing
    python -m reels.pipeline --script samples/paheli_01.json --part 2 --preview
"""
import os, sys, json, glob, argparse, random, traceback, datetime as dt
from .config import ROOT, OUT, STATE, FORMATS, KINDS
from . import timeline, render, themes, writer, youtube

HISTORY = os.path.join(STATE, "history.json")        # every uploaded video
SERIES = os.path.join(STATE, "series.json")          # {"active": series + "next" part index, "last_kind": ...}
LAST_ERROR = os.path.join(STATE, "last_error.txt")   # why Claude failed last time (committed with the state)
LAST_CRASH = os.path.join(STATE, "last_crash.txt")   # why the last run stopped; removed after the next good upload
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))


def log(*a): print(*a, flush=True)


def load(path, default):
    try: return json.load(open(path, encoding="utf-8"))
    except (OSError, ValueError): return default


def save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def as_series(d):
    """A file is either a series {parts:[...]} or a single reel; always return a series."""
    return d if d.get("parts") else dict(series_title=d.get("yt_title", "")[:30], type=d.get("type", "devotional"), parts=[d])


def sample_series(kind, history):
    """Backup when Claude fails: a sample series of this kind, preferring one not posted yet."""
    pool = [as_series(load(p, {})) for p in sorted(glob.glob(os.path.join(ROOT, "samples", "*.json")))]
    pool = [s for s in pool if s.get("type") == kind] or [s for s in pool if s.get("type") in KINDS]
    used = {h.get("series") for h in history}
    return random.choice([s for s in pool if s.get("series_title") not in used] or pool)


def warn(title, msg):
    if os.environ.get("GITHUB_ACTIONS"):   # shown on the run's summary page
        msg = msg[:900].replace("%", "%25").replace("\r", "").replace("\n", "%0A")
        print(f"::warning title={title}::{msg}", flush=True)


def next_theme(kind, history):
    """The look after the one used by the last series of this kind (round and round)."""
    last = [h.get("theme", 0) for h in history if h.get("type") == kind]
    return (last[-1] + 1) % len(themes.THEMES[kind]) if last else 0


def new_series(kind, today, history, yt):
    trends = writer.trending(yt)
    log(f"writing a new {kind} series ({len(trends)} trending titles)")
    try:
        series = writer.write_series(kind, today.strftime("%d %B %Y, %A"), trends, [h.get("title", "") for h in history],
                                     [h["story"] for h in history if h.get("story")])
        if series.get("_story"): log("based on owner story:", series["_story"])
        if os.path.exists(LAST_ERROR): os.remove(LAST_ERROR)
    except Exception as e:
        log("Claude failed, using a sample series:", repr(e))
        warn("Claude script failed, sample used", repr(e))
        open(LAST_ERROR, "w", encoding="utf-8").write(f"{dt.datetime.now(IST):%Y-%m-%d %H:%M} IST\n{e}\n")
        series = sample_series(kind, history)
    return dict(series, next=0, theme=next_theme(kind, history))


def todays_part(a, state, history, today, yt):
    """-> (series, part index, from_state)."""
    if a.script:
        series = as_series(load(a.script, {}))
        return series, max(0, min(a.part, len(series["parts"])) - 1), False
    series = state.get("active")
    if a.type in KINDS and series and series.get("type") != a.type:
        series = None                                           # a different format was asked for
    if not series or series.get("next", 0) >= len(series.get("parts", [])):
        last = state.get("last_kind")
        if a.type in KINDS: kind = a.type
        elif last in KINDS: kind = KINDS[(KINDS.index(last) + 1) % len(KINDS)]      # take turns
        else: kind = KINDS[0]
        series = new_series(kind, today, history, yt)
        state["active"] = series
        save(SERIES, state)          # saved on test runs too, so the next real run posts this same Part 1
    return series, series["next"], True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--type", default="auto", help="auto / " + " / ".join(KINDS) + " (forces a new series of that format)")
    ap.add_argument("--script", help="render a local script/series JSON instead of the series state")
    ap.add_argument("--part", type=int, default=1, help="with --script: which part")
    ap.add_argument("--no-upload", action="store_true")
    ap.add_argument("--preview", action="store_true", help="only render a contact sheet")
    ap.add_argument("--post-time", default="now", help="publish time IST, HH:MM, or 'now' (see reels/schedule.py)")
    ap.add_argument("--slot", default="extra", help="which daily slot this video fills (recorded in the history)")
    ap.add_argument("--theme", type=int, help="look number (reels/themes.py); default: the series' own")
    ap.add_argument("--date", help="publish date IST, YYYY-MM-DD (default today)")
    a = ap.parse_args()

    os.makedirs(OUT, exist_ok=True)
    today = dt.date.fromisoformat(a.date) if a.date else dt.datetime.now(IST).date()      # the day it is published
    history = load(HISTORY, [])
    state = load(SERIES, {"active": None, "last_kind": None})
    yt = None if a.no_upload else youtube.client()

    series, idx, from_state = todays_part(a, state, history, today, yt)
    kind, n = series.get("type", KINDS[0]), len(series["parts"])
    part = series["parts"][idx]
    badge = (part.get("label") or FORMATS[kind]["label"]).upper()
    script = timeline.clean_script(dict(part, type=kind, theme=a.theme if a.theme is not None else series.get("theme", 0),
                                       label=f"{badge} · PART {idx + 1}/{n}" if n > 1 else badge))
    save(os.path.join(OUT, "script.json"), dict(part, type=kind))
    log(f"{series.get('series_title')!r} part {idx + 1}/{n} ({kind}): {script['yt_title']!r}, {len(script['shots'])} shots")

    tl, voices = timeline.build_timeline(script, os.path.join(OUT, "voice"))
    log(f"timeline {tl['total']:.1f}s, {len(tl['phrases'])} lines")
    if a.preview:
        render.preview(tl, os.path.join(OUT, "preview.jpg")); log("preview ->", os.path.join(OUT, "preview.jpg")); return
    mp4 = render.render(tl, voices, os.path.join(OUT, "reel.mp4"), log=log)
    log("rendered ->", mp4)

    if a.no_upload:
        log("test run: nothing uploaded, this part stays queued"); return
    if yt is None: sys.exit("YouTube secrets missing (YT_CLIENT_ID / YT_CLIENT_SECRET / YT_REFRESH_TOKEN)")
    publish = None                                   # None = public right away
    if a.post_time != "now":
        hh, mm = map(int, a.post_time.split(":"))
        publish = dt.datetime(today.year, today.month, today.day, hh, mm, tzinfo=IST).astimezone(dt.timezone.utc)
    vid, status = youtube.upload(yt, mp4, script["yt_title"], script["yt_description"], script.get("tags", []), publish)
    log(f"uploaded https://youtube.com/shorts/{vid} ({status})")

    entry = dict(date=str(today), slot=a.slot, type=kind, series=series.get("series_title"), part=f"{idx + 1}/{n}", theme=script["theme"],
                 title=script["yt_title"], seconds=round(tl["total"], 1), video_id=vid)
    if series.get("_story"): entry["story"] = series["_story"]
    save(HISTORY, (history + [entry])[-200:])
    if from_state:
        series["next"] = idx + 1
        if series["next"] >= n: state.update(active=None, last_kind=kind)    # series finished
        else: state["active"] = series
        save(SERIES, state)
    if os.path.exists(LAST_CRASH): os.remove(LAST_CRASH)


def run():
    """main(), but the reason of a crash is kept in state/ and on the run's summary page."""
    try:
        main()
    except Exception as e:
        if os.environ.get("GITHUB_ACTIONS"):
            where = "".join(traceback.format_tb(e.__traceback__)[-4:])
            with open(LAST_CRASH, "w", encoding="utf-8") as f:
                f.write(f"{dt.datetime.now(IST):%Y-%m-%d %H:%M} IST
{where}{type(e).__name__}: {str(e)[:600]}
")
            warn("Run stopped", f"{type(e).__name__}: {e}")
        raise


if __name__ == "__main__":
    run()
