"""Daily script writer: gathers today's trends and asks Claude for a reel script (strict JSON)."""
import os, json, shutil, subprocess, tempfile, urllib.request, xml.etree.ElementTree as ET

MODEL = "claude-opus-5-5"

SCENES = ["walk", "meet", "divine", "road", "night", "rain", "sunrise", "mountain"]
LINE = {"type": "object", "additionalProperties": False, "required": ["speaker", "hindi", "caption"],
        "properties": {"speaker": {"type": "string", "enum": ["N", "K", "A", "P"]},
                       "hindi": {"type": "string"}, "caption": {"type": "string"}}}
SHOT = {"type": "object", "additionalProperties": False, "required": ["scene", "mood", "lines"],
        "properties": {"scene": {"type": "string", "enum": SCENES},
                       "mood": {"type": "string", "enum": ["sad", "neutral", "happy"]},
                       "lines": {"type": "array", "items": LINE}}}
STR_FIELDS = ["topic", "p_name", "label", "title_line1", "title_line2", "title_sub", "end_text", "end_sub", "yt_title", "yt_description"]
SCHEMA = {"type": "object", "additionalProperties": False,
          "required": STR_FIELDS + ["tags", "shots"],
          "properties": {**{k: {"type": "string"} for k in STR_FIELDS},
                         "tags": {"type": "array", "items": {"type": "string"}},
                         "shots": {"type": "array", "items": SHOT}}}

SYSTEM = """You write scripts for a Hindi YouTube Shorts channel of short animated (cartoon) reels, 40-55 seconds long.
The video engine can only draw the characters and scenes listed below, so every shot must use them exactly.

FORMAT "devotional" - a short story or teaching of Shri Krishna.
  Speakers: N = female narrator, K = Shri Krishna, A = Arjun, P = an ordinary man (a devotee, villager, worker or student; always the same simple man in a plain kurta).
  Scenes:
    walk   - Krishna and Arjun walking on a forest path (narrator lines only)
    meet   - forest clearing under a banyan tree: Krishna and Arjun standing, P sitting under the tree (any speaker)
    divine - Krishna alone in golden divine light, blessing (K or N lines)
  Keep stories respectful and true to the spirit of the Gita and Bhagavata tradition. Paraphrase teachings; do not invent verse numbers or quote scripture you are unsure of.

FORMAT "motivational" - an inspiring mini story about P, the ordinary man.
  Speakers: N = narrator, P = the man himself (use P sparingly, short lines).
  Scenes: road (P walking a forest path), night (P sitting alone under a tree at night), rain (P sitting in a storm, struggling),
          sunrise (P standing as the sun rises, hopeful), mountain (P on a mountain top, arms raised in victory).
  Arc: struggle -> turning point -> victory -> one clear lesson.

Writing rules:
- 4 to 7 shots; 1 to 3 lines per shot; 85-120 spoken Hindi words in total. Each line at most 18 words.
- The first line is a strong hook. The last line is a short, punchy takeaway.
- "hindi": natural spoken Hindi in Devanagari, written for text-to-speech: commas and "..." for pauses, numbers as words, no emojis, no English words unless common in Hindi speech.
- "caption": the same line in Roman Hinglish. Wrap 1-3 key words in *asterisks* (always in pairs) to highlight them.
- "mood" describes how the shot feels; for scenes with P it also sets his expression.
- Trending topics are given only as optional inspiration. Use one only if a festival, occasion or positive theme fits the format naturally.
  Never mention news events, politics, accidents, disasters, crimes, real people, celebrities or brands, and never state facts about current events.
- Do not repeat or closely imitate any recent title listed.
- p_name: what to call P in his caption tag, in Roman (max 14 characters), e.g. "Raju", "Ek Kisaan", "Garib Bhakt".
- label: 2-3 word uppercase badge, e.g. "AAJ KI KAHANI" or "LIFE LESSON".
- title_line1 / title_line2: two short Roman lines for the opening title card (max 16 characters each).
- title_sub: one short Roman subtitle (max 28 characters).
- end_text: closing words in uppercase Roman (max 14 characters), e.g. "RADHE RADHE" or "HAAR MAT MAANO".
- end_sub: short Roman line (max 26 characters).
- yt_title: catchy Hinglish YouTube title, max 80 characters, ending with " #shorts".
- yt_description: 2-4 short Hinglish lines followed by 5-8 relevant hashtags.
- tags: 8-12 short search tags (Hinglish or English)."""


def trending(youtube=None, limit=15):
    """Best-effort list of trending titles in India (Google News + YouTube). Never raises."""
    out = []
    try:
        req = urllib.request.Request("https://news.google.com/rss?hl=hi&gl=IN&ceid=IN:hi", headers={"User-Agent": "Mozilla/5.0 (daily-reels)"})
        root = ET.fromstring(urllib.request.urlopen(req, timeout=20).read())
        out += [i.findtext("title") for i in root.iter("item")][:limit]
    except Exception as e:
        print("news trends unavailable:", e)
    if youtube is not None:
        try:
            res = youtube.videos().list(part="snippet", chart="mostPopular", regionCode="IN", maxResults=limit).execute()
            out += [it["snippet"]["title"] for it in res.get("items", [])]
        except Exception as e:
            print("youtube trends unavailable:", e)
    return [t for t in out if t]


def write_script(kind, date_str, trends, recent_titles):
    """Uses the Claude API if ANTHROPIC_API_KEY is set, otherwise the Claude Code CLI
    (subscription auth via CLAUDE_CODE_OAUTH_TOKEN from `claude setup-token`)."""
    user = (f"Today is {date_str} (India). Write today's reel in the \"{kind}\" format.\n\n"
            f"Trending in India today (optional inspiration only):\n- " + "\n- ".join(trends[:25] or ["(none)"]) +
            "\n\nRecent titles to avoid repeating:\n- " + "\n- ".join(recent_titles[-30:] or ["(none)"]))
    data = _via_api(user) if os.environ.get("ANTHROPIC_API_KEY") else _via_claude_code(user)
    data["type"] = kind
    return data


def _via_claude_code(user):
    exe = shutil.which("claude")
    if not exe:
        raise RuntimeError("Claude Code CLI not found (npm install -g @anthropic-ai/claude-code)")
    if not os.environ.get("CLAUDE_CODE_OAUTH_TOKEN"):
        raise RuntimeError("Neither ANTHROPIC_API_KEY nor CLAUDE_CODE_OAUTH_TOKEN is set")
    prompt = SYSTEM + "\n\n---\n\n" + user + "\n\nReply only with the JSON object for today's reel."
    # Prompt goes through stdin (a multi-line argument gets cut at the first newline on Windows).
    # No tools, and run outside the repo, so the model only writes the script.
    cmd = [exe, "-p", "--model", MODEL, "--output-format", "json", "--tools", "",
           "--json-schema", json.dumps(SCHEMA), "--max-turns", "3"]
    r = subprocess.run(cmd, input=prompt, capture_output=True, text=True, encoding="utf-8",
                       timeout=900, cwd=tempfile.gettempdir())
    if r.returncode != 0:
        raise RuntimeError(f"claude CLI failed ({r.returncode}): {(r.stderr or r.stdout)[-1500:]}")
    out = json.loads(r.stdout)
    if out.get("is_error"):
        raise RuntimeError(f"claude CLI error: {str(out.get('result'))[:1500]}")
    data = out.get("structured_output")
    if data is None:
        data = json.loads(out.get("result") or "")
    if isinstance(data, str):
        data = json.loads(data)
    return data


def _via_api(user):
    import anthropic
    client = anthropic.Anthropic()
    resp = client.beta.messages.create(
        model=MODEL,
        max_tokens=16000,
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        system=SYSTEM,
        messages=[{"role": "user", "content": user}],
        output_config={"effort": "medium", "format": {"type": "json_schema", "schema": SCHEMA}},
    )
    if resp.stop_reason == "refusal":
        raise RuntimeError(f"script request refused: {getattr(resp, 'stop_details', None)}")
    if resp.stop_reason == "max_tokens":
        raise RuntimeError("script output was cut off (max_tokens)")
    text = next(b.text for b in resp.content if b.type == "text")
    return json.loads(text)
