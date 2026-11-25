"""
One-time helper: run this on YOUR computer to let the bot upload to your YouTube channel.

    python scripts/get_youtube_token.py path/to/client_secret.json

A browser window opens -> log in with the Google account that owns the channel -> Allow.
The script prints three values. Put them in GitHub -> Settings -> Secrets and variables -> Actions:
    YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN
Never commit client_secret.json or these values to the repo.
"""
import sys, json
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.readonly"]

if len(sys.argv) != 2:
    sys.exit(__doc__)
flow = InstalledAppFlow.from_client_secrets_file(sys.argv[1], SCOPES)
creds = flow.run_local_server(port=0, prompt="consent", access_type="offline")
info = json.load(open(sys.argv[1]))
app = info.get("installed") or info.get("web")
print("\nAdd these as GitHub Actions secrets:\n")
print("YT_CLIENT_ID     =", app["client_id"])
print("YT_CLIENT_SECRET =", app["client_secret"])
print("YT_REFRESH_TOKEN =", creds.refresh_token)
