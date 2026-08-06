"""
config.py
v4.0 - central configuration (Google Drive backend)

Changelog:
- v4.0: switched storage backend Yandex.Disk -> Google Drive (drive.file
        scope, non-sensitive, app published "In Production" so no 100-user
        cap and no 7-day refresh-token expiry).
- v3.0: Yandex.Disk backend (accessible from BY/CIS).
"""
import os


class Config:
    BOT_TOKEN = os.environ["BOT_TOKEN"]

    # One Google Cloud OAuth "Web application" client, shared by all users.
    # Each user authorizes their OWN Google Drive via the consent screen.
    GOOGLE_CLIENT_ID = os.environ["GOOGLE_CLIENT_ID"]
    GOOGLE_CLIENT_SECRET = os.environ["GOOGLE_CLIENT_SECRET"]
    # Must exactly match a redirect URI registered in Google Cloud Console, e.g.
    # https://your-app.onrender.com/oauth/callback
    OAUTH_REDIRECT_URI = os.environ["OAUTH_REDIRECT_URI"]

    SUPABASE_URL = os.environ["SUPABASE_URL"]
    SUPABASE_KEY = os.environ["SUPABASE_KEY"]

    PORT = int(os.environ.get("PORT", "10000"))

    # drive.file: app can only see/edit files IT created or that the user
    # explicitly opened with it — not the whole Drive.
    GOOGLE_SCOPE = "https://www.googleapis.com/auth/drive.file"

    TEMP_DIR = "/tmp/cleandrive_bot"


config = Config()
