"""Writes PLAN.md: what was posted, what comes next, and the plan of the new mythology channel.
Standard library only. The workflow runs it after every video; a failure here must never stop a video.

    python -m reels.plan_page
"""
import os, json, datetime as dt
from reels.schedule import SLOTS, IST, slot_time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KIND = {"paheli": "Paheli", "devotional": "Krishna katha"}
DAYS = ["Som", "Mangal", "Budh", "Guru", "Shukr", "Shani", "Ravi"]


def load(*p, default=None):
    try: return json.load(open(os.path.join(ROOT, *p), encoding="utf-8"))
    except (OSError, ValueError): return default


def cell(s): return str(s).replace("|", "/").replace("\n", " ")
def link(v): return f"[dekho](https://youtube.com/shorts/{v})" if v else "-"
def when(d, s): x = dt.date.fromisoformat(d); return f"{DAYS[x.weekday()]} {x:%d-%m-%Y}, {s}"


def daily(now):
    hist = [h for h in load("state", "history.json", default=[]) if h.get("date") and h.get("slot") in SLOTS]
    hist.sort(key=lambda h: (h["date"], h["slot"])); state = load("state", "series.json", default={}) or {}
    out = ["## 1. Daily Reels (chal raha hai, apne aap)", "", "Roz 3 video: **12:00, 16:00, 19:00** (IST).", ""]
    done = {(h["date"], h["slot"]): h for h in hist}
    out += ["### Aane wali", "", "| Kab | Haalat | Video |", "|---|---|---|"]
    ahead = [(str(now.date() + dt.timedelta(days=i)), s) for i in range(3) for s in SLOTS]
    for d, s in [x for x in ahead if slot_time(dt.date.fromisoformat(x[0]), x[1]) > now][:6]:
        h = done.get((d, s)); out.append(f"| {when(d, s)} | {'Taiyar, YouTube par schedule' if h else 'Abhi banni baaki'} | {cell(h['title']) if h else '-'} |")
    act = state.get("active")
    if act: out += ["", f"Chal rahi series: **{cell(act.get('series_title') or act.get('series') or act.get('title') or act.get('name') or '')}**, agla part: **{act.get('next', 0) + 1}**"]
    else: out += ["", f"Agli run nayi series shuru karegi: **{KIND['paheli' if state.get('last_kind') == 'devotional' else 'devotional']}**"]
    out += ["", "### Pichhli 12", "", "| Kab | Type | Series | Part | Video |", "|---|---|---|---|---|"]
    past = [h for h in hist if slot_time(dt.date.fromisoformat(h["date"]), h["slot"]) <= now]
    out += [f"| {when(h['date'], h['slot'])} | {KIND.get(h.get('type'), h.get('type'))} | {cell(h.get('series', '-'))} | {h.get('part', '-')} | {link(h.get('video_id'))} |" for h in reversed(past[-12:])]
    return out


def channel(now):
    ch = load("plan", "channel.json")
    if not ch: return []
    start = dt.date.fromisoformat(ch["start"]) if ch.get("start") else None
    out = ["", "## 2. Naya Mythology channel (taiyari chal rahi hai)", "", f"Shuru hone ki tareekh: **{start:%d-%m-%Y}**" if start else "Shuru hone ki tareekh: **abhi tay nahi**. Tay hote hi neeche tareekhein apne aap bhar jayengi.", "",
           "| Din | Series | Granth | Agla bhaag |", "|---|---|---|---|"]
    detail = []
    for s in ch["series"]:
        parts = load("plan", s["file"], default=[]) if s.get("file") else []; todo = [p for p in parts if not p.get("video_id")]
        nxt = f"Bhaag {todo[0]['bhaag']}: {todo[0]['naam']}" if todo else "List poori" if parts else "List banni baaki"
        out.append(f"| {s['din']} | {s['naam']} | {s['granth']} | {cell(nxt)} |")
        if not parts: continue
        d = None
        if start: d = max(start, now.date()); d += dt.timedelta(days=(s["day"] - d.weekday()) % 7)
        detail += ["", f"### {s['naam']}: saare {len(parts)} bhaag"]; khand = None
        for p in parts:
            if p.get("khand", "") != khand:
                if khand is not None: detail += ["", "</details>"]
                khand = p.get("khand", ""); n = [q for q in parts if q.get("khand", "") == khand]
                detail += ["", f"<details{' open' if todo and todo[0] in n else ''}><summary><b>{cell(khand or s['naam'])}</b> (bhaag {n[0]['bhaag']}-{n[-1]['bhaag']})</summary>", "", "| Bhaag | Kahani | Kaand, sarg | Kab | Haalat |", "|---|---|---|---|---|"]
            if p.get("video_id"): k, st = p.get("date") or "-", "Aa gayi " + link(p["video_id"]) + (f"<br>Kahan ruke: {cell(p['ruke'])}" if p.get("ruke") else "")
            else:
                k = f"{d:%d-%m-%Y}" if d else "tay nahi"; st = "**Agla**" if p is todo[0] else "Baaki"
                if d: d += dt.timedelta(days=7)
            out_src = f"[{p['kaand']} {p['sarg']}]({p['link']})"; detail.append(f"| {p['bhaag']} | {cell(p['naam'])} | {out_src} | {k} | {st} |")
        detail += ["", "</details>"]
    return out + detail + ["", "*Kram granth ki adhyay-soochi se liya hai. Har adhyay poora padhkar hi uski script banegi.*"]


def main():
    now = dt.datetime.now(IST)
    txt = ["# Video plan", "", "Ye page har nayi video banne ke baad apne aap update hota hai.", ""] + daily(now) + channel(now) + ["", f"Aakhri update: {now:%d-%m-%Y %H:%M} IST"]
    open(os.path.join(ROOT, "PLAN.md"), "w", encoding="utf-8", newline="\n").write("\n".join(txt) + "\n")


if __name__ == "__main__":
    main()
