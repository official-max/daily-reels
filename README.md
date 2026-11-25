# Daily Reels 🎬

Is repo mein **2 YouTube channel** hain, dono apne folder mein alag:

| Folder | Channel | Kya | Haalat |
|---|---|---|---|
| [paheli-krishna/](paheli-krishna) | [Paheli aur Krishna katha](https://www.youtube.com/@JatinOfficial-t9y) | Roz 3 Shorts, apne aap | Chal raha hai |
| [pushpak-katha/](pushpak-katha) | [Pushpak Katha](https://www.youtube.com/@PushpakKatha) | Poori Valmiki Ramayan, 732 bhaag | Taiyari |

| Saajhi cheezein | Kaam |
|---|---|
| [Live page](https://official-max.github.io/daily-reels/) (`docs/`) | Dono channel ka plan; repo se seedha data padhta hai |
| [PLAN.md](PLAN.md) | Wahi plan GitHub ke andar, `tools/plan_page.py` banata hai |
| `.github/workflows/daily.yml` | paheli-krishna channel ko roz chalata hai |

**Ramayan ke baad** Pushpak Katha par isi kram mein: Shiv Mahagatha, Ganesh Leela, Krishna Leela, Bhakton ki Gatha, Mahabharat, Paheli/Rahasya/What If. Kram `pushpak-katha/plan/channel.json` ke `baad` mein hai.

---

# paheli-krishna channel

Neeche ke saare path `paheli-krishna/` ke andar ke hain, commands bhi wahin se chalao (`cd paheli-krishna`).

Roz **3 Hindi cartoon Shorts** apne aap bante hain aur YouTube par **12 PM, 4 PM aur 7 PM (IST)** publish hote hain.
GitHub Actions par chalta hai, laptop on rakhne ki zaroorat nahi.

📅 **Kaun si video kab aayegi:** [live page](https://official-max.github.io/daily-reels/) ya [PLAN.md](PLAN.md) (dono apne aap update hote hain)

- **Series mein kahaniyan**, roz ek part:
  - **Paheli** (raja ka darbar): Part 1 mein sawaal + "jawab comment karo", Part 2 mein jawab. 2 parts.
  - **Krishna katha**: 2-3 parts.
  - Ek series khatam hote hi agli dusre format ki (paheli → Krishna → paheli ...).
- Claude pehle web par asli katha / lok paheli dhoondhta hai, phir poori series ek saath likhta hai.
- 2.5D cartoon animation, Hindi awaaz, captions, music: sab code se banta hai, koi paid service nahi.

## Roz kya hota hai

```
GitHub jab bhi chale: agle 24 ghante mein koi khaali slot (12 PM / 4 PM / 7 PM) hai ya aaj ka chhoot gaya?  ── haan ──►
  ├─ state/series.json mein chal rahi series ka agla part?  ── nahi ──► Claude se nayi series (sab parts)
  ├─ awaaz (edge-tts) → animation → reel.mp4
  ├─ YouTube upload, slot ke time par schedule (ek run mein 3 videos tak)
  └─ state/ commit (history, series, aur fail hua ho to last_error.txt)
```
Claude fail ho jaye to `samples/` ki series use hoti hai, taaki us din ki video na chhoote.

## Code ka naksha (`reels/`)

| File | Kaam |
|---|---|
| `config.py` | **Saari settings**: video size, voices, caption names, aur dono formats ke rules |
| `pipeline.py` | Roz ka run: aaj ka part chuno → render → upload → state save |
| `writer.py` | Claude ko prompt + JSON schema; poori series likhwata hai |
| `timeline.py` | Script ko render-ready banata hai: camera, mood, awaaz, timing |
| `render.py` | Har frame jodta hai (shot + overlays) aur ffmpeg se mp4 banata hai |
| `themes.py` | Har nayi series ka alag look: rang, kapde, UI, transition, music (6 + 6 themes) |
| `scenes.py` | Backgrounds aur shots: jungle (walk, meet, divine), darbar |
| `characters.py` | Characters: Krishna, Arjun, aam aadmi, Raja, Chatur, sipahi |
| `canvas.py` | 2.5D shading wala drawing canvas + sprite cache |
| `overlays.py` | Captions, title card, end card, hook bar, sticker, icon cards |
| `audio.py` | Awaaz, lip-sync, music (tanpura, bansuri, suspense), sound effects |
| `youtube.py` | YouTube upload |
| `util.py` | Chhote helpers (easing, curves, drawing pen) |

Script ka format (Claude jo JSON likhta hai) `writer.py` mein `SCHEMA` hai. Example: `samples/paheli_01.json`.

## One-time setup

### 1. Claude (kahani likhne ke liye)
**A) Claude Pro/Max subscription se (recommended)**
1. Laptop terminal mein: `npm install -g @anthropic-ai/claude-code` phir `claude setup-token`
2. Browser mein login → Allow → terminal mein token aayega (1 saal valid).
3. GitHub repo → **Settings → Secrets and variables → Actions → New repository secret**:
   `CLAUDE_CODE_OAUTH_TOKEN` = wo token

**B) Claude API key se (pay-as-you-go):** secret `ANTHROPIC_API_KEY`. Ye set ho to isi ko priority milti hai.

### 2. YouTube upload permission
1. https://console.cloud.google.com par project banaiye, **YouTube Data API v3** enable kijiye.
2. **Google Auth Platform**: External app, scopes `youtube.upload` + `youtube.readonly`,
   Branding mein home page / privacy policy links, phir **Audience → Publish app → In production**.
   (Testing mode mein token 7 din mein expire ho jata hai.)
3. **Clients → Create client → Desktop app** → JSON download (repo ke bahar rakhiye).
4. `pip install google-auth-oauthlib` phir `python scripts/get_youtube_token.py "<json ka path>"`
5. Jo 3 values aayengi unhe GitHub Secrets mein daaliye: `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`

> ⚠️ Keys aur `client_secret.json` kabhi commit mat kijiye, chat mein mat bhejiye.

### 3. Test
GitHub → **Actions → Daily Reel → Run workflow**: pehle `upload = false` (video Artifacts mein milegi), phir `true`.

**YouTube audit:** naye API projects ki videos **Private** rehti hain jab tak
[API audit](https://support.google.com/youtube/contact/yt_api_form) approve na ho. Tab tak Studio mein Public kar dijiye.

## Apni kahaniyan aur style
`references/` dekhiye: `stories/paheli/` ya `stories/devotional/` mein `.txt` file daaliye, wo pehle use hogi.
`style.md` mein likhe notes Claude har baar padhta hai.

## Laptop par chalana
```
pip install -r requirements.txt
python -m reels.pipeline --script samples/paheli_01.json --part 1 --no-upload   # video: out/reel.mp4
python -m reels.pipeline --script samples/paheli_01.json --part 2 --preview     # sirf preview image
```

## Kuch badalna ho to
| Kya | Kahan |
|---|---|
| Post ke time (slots) | `reels/schedule.py` → `SLOTS` |
| Kahani ka style / rules | `writer.py` → `FORMAT_TEXT`, `RULES` |
| Rang / look (themes) | `themes.py` |
| Voices, caption names | `config.py` |
| Naya format (jaise Ramayan) | `config.FORMATS` + scene `scenes.py` mein + characters `characters.py` mein + `writer.FORMAT_TEXT` |
| Claude kyun fail hua | `state/last_error.txt` |
| Run kyun ruka | `state/last_crash.txt` |
