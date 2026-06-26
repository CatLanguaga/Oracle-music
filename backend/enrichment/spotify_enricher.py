"""Spotify client + metadata import.

Provides:
- get_client(): cached Spotipy client using Client Credentials flow.
- fetch_playlist_tracks(playlist_id): list of normalized track dicts.
- fetch_track(track_id): single normalized track dict.

Note: Spotify Audio Features endpoint is deprecated for new apps
(Nov 2024). We intentionally do NOT use it. Sonic attributes come
from Last.fm tags + Gemini, not Spotify.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Any

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from backend.config import get_settings
from backend.enrichment import cache


@lru_cache(maxsize=1)
def get_client() -> spotipy.Spotify:
    s = get_settings()
    auth = SpotifyClientCredentials(
        client_id=s.spotify_client_id,
        client_secret=s.spotify_client_secret,
    )
    return spotipy.Spotify(auth_manager=auth, requests_timeout=15, retries=3)


def _normalize_track(raw: dict[str, Any]) -> dict[str, Any] | None:
    """Strip a Spotify track object down to what we persist."""
    if raw is None or raw.get("id") is None:
        return None
    album = raw.get("album") or {}
    images = album.get("images") or []
    release_date = album.get("release_date") or ""
    release_year: int | None = None
    if release_date[:4].isdigit():
        release_year = int(release_date[:4])
    artists = raw.get("artists") or []
    return {
        "id": raw["id"],
        "title": raw.get("name") or "",
        "artist": ", ".join(a.get("name", "") for a in artists),
        "artist_ids": [a.get("id") for a in artists if a.get("id")],
        "album": album.get("name"),
        "album_art_url": images[0]["url"] if images else None,
        "spotify_popularity": raw.get("popularity"),
        "duration_ms": raw.get("duration_ms"),
        "release_year": release_year,
        "has_featuring": len(artists) > 1,
    }


def fetch_track(track_id: str) -> dict[str, Any] | None:
    raw = cache.cached_call(
        "spotify", f"track:{track_id}", lambda: get_client().track(track_id)
    )
    return _normalize_track(raw)


def fetch_playlist_tracks(playlist_id: str, limit: int | None = None) -> list[dict[str, Any]]:
    """Paginate through a playlist and return normalized track dicts."""
    out: list[dict[str, Any]] = []
    offset = 0
    page_size = 100
    sp = get_client()
    while True:
        cache_key = f"playlist:{playlist_id}:offset={offset}"
        page = cache.cached_call(
            "spotify",
            cache_key,
            lambda: sp.playlist_items(
                playlist_id,
                limit=page_size,
                offset=offset,
                fields="items.track(id,name,popularity,duration_ms,artists(id,name),"
                "album(name,release_date,images)),next",
                additional_types=("track",),
            ),
        )
        items = page.get("items") or []
        for it in items:
            n = _normalize_track(it.get("track") or {})
            if n:
                out.append(n)
                if limit and len(out) >= limit:
                    return out
        if not page.get("next"):
            break
        offset += page_size
    return out


def fetch_artist(artist_id: str) -> dict[str, Any] | None:
    return cache.cached_call(
        "spotify", f"artist:{artist_id}", lambda: get_client().artist(artist_id)
    )


def search_artist(query: str) -> dict[str, Any] | None:
    """Return the top-matching artist for a search query."""
    res = cache.cached_call(
        "spotify",
        f"search_artist:{query.lower()}",
        lambda: get_client().search(q=query, type="artist", limit=1),
    )
    items = ((res or {}).get("artists") or {}).get("items") or []
    return items[0] if items else None


def fetch_artist_top_tracks(
    artist_id: str, market: str = "US"
) -> list[dict[str, Any]]:
    """Top tracks endpoint — Client Credentials accessible.

    Returns normalized track dicts. Spotify returns up to 10.
    """
    raw = cache.cached_call(
        "spotify",
        f"artist_top:{artist_id}:{market}",
        lambda: get_client().artist_top_tracks(artist_id, country=market),
    )
    out: list[dict[str, Any]] = []
    for t in (raw or {}).get("tracks", []) or []:
        n = _normalize_track(t)
        if n:
            out.append(n)
    return out
