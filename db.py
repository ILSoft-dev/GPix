"""
db.py
v4.1 - per-user Google OAuth token storage + persistent upload settings, in Supabase

Table (create once, SQL in README):
    disk_users(telegram_id bigint primary key,
               access_token text,
               refresh_token text,
               clean_metadata boolean default true,
               anonymize_names boolean default false,
               created_at timestamptz default now())

Changelog:
- v4.1: added clean_metadata / anonymize_names settings, previously asked
        per-upload via buttons — now a standing preference toggled via
        /settings, so the upload flow itself is just files -> folder name
        -> link.
"""
from supabase import create_client

from config import config

_supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)

DEFAULT_SETTINGS = {"clean_metadata": True, "anonymize_names": False}


def save_tokens(telegram_id: int, access_token: str, refresh_token: str) -> None:
    _supabase.table("disk_users").upsert({
        "telegram_id": telegram_id,
        "access_token": access_token,
        "refresh_token": refresh_token,
    }).execute()


def get_tokens(telegram_id: int) -> dict | None:
    resp = (
        _supabase.table("disk_users")
        .select("access_token, refresh_token")
        .eq("telegram_id", telegram_id)
        .limit(1)
        .execute()
    )
    if resp.data:
        return resp.data[0]
    return None


def delete_user(telegram_id: int) -> None:
    _supabase.table("disk_users").delete().eq("telegram_id", telegram_id).execute()


def get_settings(telegram_id: int) -> dict:
    """Returns {clean_metadata, anonymize_names}, falling back to defaults
    for users created before these columns existed (NULL) or with no row."""
    resp = (
        _supabase.table("disk_users")
        .select("clean_metadata, anonymize_names")
        .eq("telegram_id", telegram_id)
        .limit(1)
        .execute()
    )
    if not resp.data:
        return dict(DEFAULT_SETTINGS)
    row = resp.data[0]
    return {
        key: (row.get(key) if row.get(key) is not None else default)
        for key, default in DEFAULT_SETTINGS.items()
    }


def set_setting(telegram_id: int, field: str, value: bool) -> None:
    if field not in DEFAULT_SETTINGS:
        raise ValueError(f"Unknown setting: {field}")
    _supabase.table("disk_users").update({field: value}).eq(
        "telegram_id", telegram_id
    ).execute()
