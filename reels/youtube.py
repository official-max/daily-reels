"""YouTube Data API v3 helpers (OAuth refresh-token auth, resumable upload)."""
import os, datetime as dt
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.readonly"]


def client():
    cid, secret, token = (os.environ.get(k) for k in ("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN"))
    if not (cid and secret and token):
        return None
    creds = Credentials(None, refresh_token=token, client_id=cid, client_secret=secret,
                        token_uri="https://oauth2.googleapis.com/token", scopes=SCOPES)
    return build("youtube", "v3", credentials=creds, cache_discovery=False)


def upload(yt, path, title, description, tags, publish_at_utc=None):
    """Upload a Short. If publish_at_utc is in the future, it is scheduled (private until then)."""
    status = {"selfDeclaredMadeForKids": False}
    now = dt.datetime.now(dt.timezone.utc)
    if publish_at_utc and publish_at_utc > now + dt.timedelta(minutes=10):
        status.update(privacyStatus="private", publishAt=publish_at_utc.strftime("%Y-%m-%dT%H:%M:%S.000Z"))
    else:
        status.update(privacyStatus="public")
    body = {"snippet": {"title": title[:100], "description": description[:4900], "tags": tags[:15],
                        "categoryId": "22", "defaultLanguage": "hi", "defaultAudioLanguage": "hi"},
            "status": status}
    req = yt.videos().insert(part="snippet,status", body=body,
                             media_body=MediaFileUpload(path, mimetype="video/mp4", chunksize=8 * 1024 * 1024, resumable=True))
    resp = None
    while resp is None:
        _, resp = req.next_chunk()
    return resp["id"], status
