# Daily Reels 🎬

Roz ek naya Hindi cartoon Short **apne aap** banta hai aur YouTube par **shaam 7 baje (IST)** publish hota hai.

- **Ek din devotional** (Shri Krishna ki kahani/seekh), **ek din motivational** (aam aadmi ki kahani)
- Trending topics (Google News + YouTube India) se inspiration, Claude script likhta hai
- Premium 2.5D cartoon animation, Hindi voiceover, captions, music — sab code se
- GitHub Actions par chalta hai — laptop on rakhne ki zaroorat nahi

## Kaise chalta hai

```
4:00 PM IST  GitHub Actions start
   → trending topics → Claude (claude-opus-5-5) se script (JSON)
   → voice (edge-tts) → animation render → reel.mp4
   → YouTube upload, 7:00 PM IST par publish scheduled
   → state/history.json update (repeat se bachne ke liye)
```

Agar Claude fail ho jaye to `samples/` folder ki koi script use hoti hai, taaki us din ki video na chhoote.

## One-time setup

### 1. Claude (script likhne ke liye) — do mein se ek

**A) Claude Pro/Max subscription se (recommended, koi alag bill nahi)**
1. Apne laptop ke terminal mein:
   ```
   npm install -g @anthropic-ai/claude-code
   claude setup-token
   ```
2. Browser mein Claude account se login → Allow. Terminal mein ek lamba token print hoga (1 saal valid).
3. GitHub repo → **Settings → Secrets and variables → Actions → New repository secret**
   - Name: `CLAUDE_CODE_OAUTH_TOKEN`, Value: wo token
   Usage aapke subscription ki limit mein ginta hai.

**B) Claude API key se (pay-as-you-go)**
1. https://platform.claude.com → billing add → **API Keys → Create Key**.
2. Secret: `ANTHROPIC_API_KEY`. (Agar ye set hai to isi ko priority milti hai.)

### 2. YouTube upload permission
1. https://console.cloud.google.com par naya project banaiye (jaise `daily-reels`).
2. **APIs & Services → Library → "YouTube Data API v3" → Enable**.
3. **OAuth consent screen** (Google Auth Platform):
   - User type: **External**, app name `daily-reels`, apna email.
   - Scopes add kijiye: `youtube.upload`, `youtube.readonly`.
   - **Audience → Publish app → In production** kar dijiye.
     (Testing mode mein token 7 din mein expire ho jata hai aur upload ruk jayega.)
4. **Credentials → Create credentials → OAuth client ID → Desktop app**. JSON download kijiye (`client_secret.json`).
5. Apne laptop par (is repo folder mein):
   ```
   pip install google-auth-oauthlib
   python scripts/get_youtube_token.py C:\path\to\client_secret.json
   ```
   Browser khulega → channel wale Google account se login → *"Google hasn't verified this app"* aaye to **Advanced → Go to daily-reels** → Allow.
6. Terminal mein jo 3 values aayengi, unhe GitHub Secrets mein daaliye:
   `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`

> ⚠️ `client_secret.json` aur ye values kabhi repo mein commit mat kijiye, chat mein mat bhejiye.

### 3. Pehla test run
GitHub repo → **Actions → Daily Reel → Run workflow**
- Pehli baar `upload = false` rakhiye → run khatam hone par neeche **Artifacts** se video download karke dekhiye.
- Sab theek ho to `upload = true` se chalaiye.

## ⚠️ YouTube ki zaroori shart (audit)
Google ke naye API projects se upload hui videos **Private** reh jaati hain jab tak project ka
[API audit](https://support.google.com/youtube/contact/yt_api_form) approve na ho.
Tab tak: YouTube Studio mein video ko roz **Public** kar dijiye (1 click), aur audit form bhar dijiye.

## Local par chalana
```
pip install -r requirements.txt
python -m reels.pipeline --script samples/motivational_01.json --no-upload           # video banao
python -m reels.pipeline --script samples/devotional_01.json --no-upload --preview    # sirf preview image
```
Output `out/` folder mein aata hai.

## Kya badal sakte hain
| Kya | Kahan |
|---|---|
| Post ka time | `.github/workflows/daily.yml` (cron) aur `--post-time` |
| Script ka style / rules | `reels/writer.py` → `SYSTEM` prompt |
| Voices | `reels/story_base.py` → `VOICES` |
| Backup scripts | `samples/*.json` |
| Apni kahaniyan, style notes, reference videos | `references/` (dekhiye `references/README.md`) |
