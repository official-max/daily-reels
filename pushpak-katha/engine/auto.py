"""One Pushpak Katha video: next bhaag -> (Claude writes script + scene code, if not there yet) -> render -> upload -> bookmark.

    python engine/auto.py --date 2026-11-29 --slot 09:00 --publish 09:00   # one slot
    python engine/auto.py --bhaag 2 --no-upload                            # local test of one part
Claude runs headless with the subscription token (CLAUDE_CODE_OAUTH_TOKEN) and sees no YouTube secrets.
"""
import os, sys, json, glob, shutil, argparse, subprocess, datetime as dt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); ENG = os.path.join(ROOT, "engine"); OUT = os.path.join(ROOT, "out")
PLAN = os.path.join(ROOT, "plan", "ramayan.json"); HIST = os.path.join(ROOT, "state", "history.json"); IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
MODELS = ["claude-opus-5-5", "claude-sonnet-5-5"]
MAX_SECONDS = 170


def load(p, d):
    try: return json.load(open(p, encoding="utf-8"))
    except (OSError, ValueError): return d
def save(p, d): os.makedirs(os.path.dirname(p), exist_ok=True); json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
def log(m): print(m, flush=True)
def warn(t, m): print(f"::warning title={t}::{m}" if os.environ.get("GITHUB_ACTIONS") else f"WARNING {t}: {m}", flush=True)


def next_part(plan):
    return next((p for p in plan if not p.get("video_id")), None)


def files(n):
    k = f"{n:03d}"; return dict(py=os.path.join(ENG, f"bhaag{k}.py"), md=os.path.join(ROOT, "scripts", f"{k}.md"),
                                meta=os.path.join(ROOT, "scripts", f"{k}.json"), mp4=os.path.join(OUT, f"sample_bhaag{k}.mp4"))


def claude_env():
    """Only what the CLI needs: no YouTube secrets."""
    keep = ("PATH", "HOME", "USERPROFILE", "APPDATA", "LOCALAPPDATA", "TEMP", "TMP", "SYSTEMROOT", "LANG", "PYTHONUTF8", "CI", "GITHUB_ACTIONS")
    env = {k: v for k, v in os.environ.items() if k in keep}
    tok = "".join(os.environ.get("CLAUDE_CODE_OAUTH_TOKEN", "").split())
    if tok: env["CLAUDE_CODE_OAUTH_TOKEN"] = tok
    env["PYTHONUTF8"] = "1"; return env


def write_with_claude(part, plan):
    exe = shutil.which("claude")
    if not exe: raise RuntimeError("Claude Code CLI not found (npm install -g @anthropic-ai/claude-code)")
    i = plan.index(part); prev = plan[i - 1] if i else None; nxt = plan[i + 1] if i + 1 < len(plan) else None
    n = part["bhaag"]; f = files(n)
    prompt = (open(os.path.join(ROOT, "AGENT.md"), encoding="utf-8").read() + "\n\n---\n\n"
              f"Make bhaag {n} now. NNN = {n:03d}.\nThis part: {json.dumps(part, ensure_ascii=False)}\n"
              f"Previous part: {json.dumps(prev, ensure_ascii=False)}\nNext part: {json.dumps(nxt, ensure_ascii=False)}\n"
              f"Python: run scripts with `{sys.executable}` from the folder {ROOT}.\n"
              f"When you are done, the files {os.path.relpath(f['md'], ROOT)}, {os.path.relpath(f['meta'], ROOT)} and "
              f"{os.path.relpath(f['py'], ROOT)} must exist and the preview must look right.")
    err = []
    for model in MODELS:
        cmd = [exe, "-p", "--model", model, "--output-format", "json", "--max-turns", "120",
               "--allowedTools", "Read", "Write", "Edit", "Glob", "Grep", "Bash", "WebFetch", "WebSearch"]
        log(f"claude ({model}) is making bhaag {n} ...")
        try:
            r = subprocess.run(cmd, input=prompt, capture_output=True, text=True, encoding="utf-8", timeout=5400, cwd=ROOT, env=claude_env())
        except subprocess.TimeoutExpired:
            err.append(f"{model}: timeout"); continue
        try: out = json.loads(r.stdout)
        except ValueError: out = {"is_error": True, "result": (r.stderr or r.stdout)[-600:]}
        log(f"claude done: exit {r.returncode}, turns {out.get('num_turns')}, cost {out.get('total_cost_usd')}")
        if os.path.exists(os.path.join(OUT, "STOP.txt")): return "stop"
        if r.returncode == 0 and not out.get("is_error") and all(os.path.exists(f[k]) for k in ("py", "md", "meta")): return "ok"
        err.append(f"{model}: exit {r.returncode} {str(out.get('result'))[-400:]}")
    raise RuntimeError(" | ".join(err)[-1500:])


def render(n):
    f = files(n)
    if os.path.exists(f["mp4"]): os.remove(f["mp4"])
    r = subprocess.run([sys.executable, f["py"]], cwd=ROOT, env=dict(os.environ, PYTHONUTF8="1"), capture_output=True, text=True, encoding="utf-8", timeout=7200)
    log(r.stdout[-800:])
    if r.returncode != 0 or not os.path.exists(f["mp4"]): raise RuntimeError(f"render failed: {r.stderr[-1200:]}")
    import imageio_ffmpeg
    info = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-i", f["mp4"]], capture_output=True, text=True).stderr
    hh, mm, ss = info.split("Duration: ")[1].split(",")[0].split(":"); sec = int(hh) * 3600 + int(mm) * 60 + float(ss)
    if not 20 < sec <= MAX_SECONDS: raise RuntimeError(f"video is {sec:.1f} s (allowed up to {MAX_SECONDS})")
    return f["mp4"], round(sec, 1)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--date"); ap.add_argument("--slot"); ap.add_argument("--publish")
    ap.add_argument("--bhaag", type=int); ap.add_argument("--no-upload", action="store_true"); a = ap.parse_args()
    plan = load(PLAN, []); hist = load(HIST, [])
    part = next((p for p in plan if p["bhaag"] == a.bhaag), None) if a.bhaag else next_part(plan)
    if not part: log("Ramayan list is finished"); return
    n = part["bhaag"]; f = files(n)
    if os.path.exists(os.path.join(OUT, "STOP.txt")): os.remove(os.path.join(OUT, "STOP.txt"))
    if not (os.path.exists(f["py"]) and os.path.exists(f["meta"])):
        if write_with_claude(part, plan) == "stop":
            warn("Pushpak: user decision needed", f"Bhaag {n} ({part['naam']}): " + open(os.path.join(OUT, "STOP.txt"), encoding="utf-8").read()[:500]); sys.exit(3)
    mp4, sec = render(n); meta = load(f["meta"], {}); log(f"bhaag {n}: {sec} s, {meta.get('yt_title')!r}")
    if a.no_upload: log(f"test run, not uploaded: {mp4}"); return
    import yt as Y
    yt = Y.client()
    if not yt: raise RuntimeError("YouTube secrets missing (YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN_PUSHPAK)")
    ch = Y.channel_title(yt)
    if "pushpak" not in ch.lower(): raise RuntimeError(f"the token belongs to the channel {ch!r}, not Pushpak Katha: not uploading")
    when = None
    if a.publish and a.publish != "now":
        hh, mm = map(int, a.publish.split(":")); d = dt.date.fromisoformat(a.date)
        when = dt.datetime(d.year, d.month, d.day, hh, mm, tzinfo=IST).astimezone(dt.timezone.utc)
    vid, status = Y.upload(yt, mp4, meta["yt_title"], meta.get("yt_description", ""), meta.get("tags", []), when)
    log(f"uploaded https://youtube.com/shorts/{vid} ({status.get('publishAt', 'public now')})")
    hist.append(dict(date=a.date, slot=a.slot, bhaag=n, title=meta["yt_title"], seconds=sec, video_id=vid)); save(HIST, hist)
    part.update(video_id=vid, date=a.date, kya_aaya=meta.get("kya_aaya", ""), baaki=meta.get("baaki", ""))
    if meta.get("ruke"): part["ruke"] = meta["ruke"]
    open(PLAN, "w", encoding="utf-8").write("[\n" + ",\n".join(json.dumps(p, ensure_ascii=False) for p in plan) + "\n]\n")   # one part per line, like before


if __name__ == "__main__":
    try: main()
    except Exception as e:
        warn("Pushpak video failed", str(e)[:900]); os.makedirs(os.path.join(ROOT, "state"), exist_ok=True)
        open(os.path.join(ROOT, "state", "last_error.txt"), "w", encoding="utf-8").write(f"{dt.datetime.now(IST):%Y-%m-%d %H:%M} IST\n{e}\n"); sys.exit(1)
