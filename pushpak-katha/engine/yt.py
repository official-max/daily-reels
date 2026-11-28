"""YouTube upload for Pushpak Katha (its own refresh token; same Google project as Kanha Ki Paheli)."""
import os, datetime as dt
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.readonly"]


def client():
    cid, secret, token = (os.environ.get(k, "").strip() for k in ("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN_PUSHPAK"))
    if not (cid and secret and token): return None
    creds = Credentials(None, refresh_token="".join(token.split()), client_id=cid, client_secret=secret,
                        token_uri="https://oauth2.googleapis.com/token", scopes=SCOPES)
    return build("youtube", "v3", credentials=creds, cache_discovery=False)


def channel_title(yt):
    r = yt.channels().list(part="snippet", mine=True).execute(); return r["items"][0]["snippet"]["title"] if r.get("items") else "?"


def upload(yt, path, title, description, tags, publish_at_utc=None):
    """Upload a Short; scheduled (private until then) when the time is in the future."""
    status = {"selfDeclaredMadeForKids": False, "containsSyntheticMedia": False}
    if publish_at_utc and publish_at_utc > dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=10):
        status.update(privacyStatus="private", publishAt=publish_at_utc.strftime("%Y-%m-%dT%H:%M:%S.000Z"))
    else:
        status.update(privacyStatus="public")
    body = {"snippet": {"title": title[:100], "description": description[:4900], "tags": tags[:15], "categoryId": "1",
                        "defaultLanguage": "hi", "defaultAudioLanguage": "hi"}, "status": status}
    req = yt.videos().insert(part="snippet,status", body=body,
                             media_body=MediaFileUpload(path, mimetype="video/mp4", chunksize=8 * 1024 * 1024, resumable=True))
    resp = None
    while resp is None: _, resp = req.next_chunk()
    return resp["id"], status
