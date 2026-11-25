# Setting up daily-reels for a new YouTube channel

> All paths below are inside the folder `paheli-krishna/` (run commands from there). The workflow is `.github/workflows/daily.yml` in the repo root.

Instructions for an AI coding assistant (for example Claude Code) helping a person run this project for their own channel.
The person may write in Hinglish; reply in their language and keep steps short.

## What this project does
A GitHub Actions workflow is set to run every hour (GitHub often runs it hours late). Each run fills every free slot
(12:00, 16:00, 19:00 IST) of the next 24 hours, at most 3 videos. For each one it:
1. Asks Claude (via the Claude Code CLI) to write a multi-part series: a royal-court riddle ("paheli", 2 parts) or a Shri Krishna story (2-3 parts).
2. Renders a 1080x1920 cartoon Short in Python (Pillow + numpy + edge-tts voices + ffmpeg).
3. Uploads it to YouTube, scheduled for the slot.
4. Commits `state/` (history, active series, last error) back to the repo.

Read `README.md` for the code map. Key files: `reels/schedule.py` (slots), `reels/pipeline.py` (daily run),
`reels/writer.py` (Claude prompt), `.github/workflows/daily.yml`.

## Ground rules
- Never put tokens, keys or `client_secret*.json` in the repo, in commits, or in chat. They go only into GitHub repository secrets.
- Do not ask the person to paste a secret to you. Tell them where to paste it themselves.
- The Claude token may belong to the person or to a family member who has chosen to let this channel use their
  Claude subscription. Whoever owns it creates it on their own computer and pastes it into the secret themselves.

## Steps

### 1. Get the code
The person forks the source repo on GitHub into their own account (**Fork → Create fork**), then opens the fork's
**Actions** tab and clicks **"I understand my workflows, go ahead and enable them"** (scheduled workflows are off in forks until then).
Clone the fork if you need to edit files locally.

### 2. Reset the previous owner's state
In the fork, so the new channel starts fresh and does not repeat the original channel's videos:
- `state/history.json` → `[]`
- `state/series.json` → `{"active": null, "last_kind": null}`
- delete `state/last_error.txt` if it exists
- delete every story file under `references/stories/*/` except `.gitkeep` (those stories were already used by the other channel)
- optional: rewrite `references/style.md` with this channel's own style so the two channels do not look alike
Commit and push.

### 3. Claude token (secret `CLAUDE_CODE_OAUTH_TOKEN`)
This needs a Claude Pro or Max subscription: the person's own, or the family member's who is sharing theirs
(that owner runs these commands on their computer; one subscription's usage then covers both channels, roughly
one or two Claude calls per channel per day):
```
npm install -g @anthropic-ai/claude-code
claude setup-token
```
They log in in the browser; a long token is printed. In the fork: **Settings → Secrets and variables → Actions →
New repository secret**, name `CLAUDE_CODE_OAUTH_TOKEN`. The token must be one line; the code strips stray line breaks anyway.
(Alternative: a pay-as-you-go API key as secret `ANTHROPIC_API_KEY`.)

### 4. YouTube upload permission (secrets `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`)
Use a separate Google Cloud project for this channel, so its upload quota and API audit are its own:
1. https://console.cloud.google.com → new project → **APIs & Services → Library → YouTube Data API v3 → Enable**.
2. **Google Auth Platform**: Get started → External → app name, support email, contact email.
   **Data Access**: add scopes `.../auth/youtube.upload` and `.../auth/youtube.readonly`.
   **Branding**: home page and privacy policy links are required before publishing. A small GitHub Pages site works
   (a public repo with `index.html` and `privacy.html`; add the `<user>.github.io` domain under Authorised domains).
   **Audience → Publish app → In production** (in Testing mode refresh tokens expire after 7 days).
3. **Clients → Create client → Desktop app** (leave "AI-powered agent" unticked) → **Download JSON**. Keep it outside the repo.
4. In the repo folder on their computer:
   ```
   python -m pip install --user google-auth-oauthlib
   python scripts/get_youtube_token.py "<full path to the downloaded client_secret json file>"
   ```
   The browser opens: choose the Google account that owns the channel. On "Google hasn't verified this app" click
   **Advanced → Go to <app> (unsafe) → Continue** (it is their own app).
5. Add the three printed values as repository secrets `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`.

Uploads from a new API project stay **private** until the project passes YouTube's API audit
(https://support.google.com/youtube/contact/yt_api_form). Until then the person makes each video public in YouTube Studio.

### 5. Test
**Actions → Daily Reel → Run workflow**, `upload = false`. When it finishes, download the `reel-N` artifact and watch it.
Check that `state/last_error.txt` was not created (if it exists, it says why Claude failed). Then run once with `upload = true`.
After that nothing is needed: the hourly schedule fills the three daily slots.

## Troubleshooting
| Symptom | Where to look / fix |
|---|---|
| Same sample story every time | `state/last_error.txt`. `invalid_credential_header` = bad `CLAUDE_CODE_OAUTH_TOKEN` |
| Run fails at "Make the reel" with YouTube errors | the three `YT_*` secrets; app must be "In production" |
| `quotaExceeded` from YouTube | the Google project's daily quota (about 6 uploads); use one project per channel |
| A run took 10 seconds and made nothing | normal: the next 24 hours are already scheduled |
| Change posting times | `SLOTS` in `reels/schedule.py` |
