"""Smoke test: single track + artist top-tracks (Client Credentials safe)."""
from __future__ import annotations

from backend.enrichment.spotify_enricher import (
    fetch_artist_top_tracks,
    fetch_track,
    search_artist,
)


def main() -> None:
    t = fetch_track("7tFiyTwD0nx5a1eklYtX2J")
    print(f"[track] {t['title']} - {t['artist']} | year={t['release_year']} pop={t['spotify_popularity']}")

    art = search_artist("Daft Punk")
    print(f"[artist] {art['name']} id={art['id']}")
    tops = fetch_artist_top_tracks(art["id"], market="US")
    print(f"[top {len(tops)}]")
    for tr in tops[:5]:
        print(f"  - {tr['title']} | pop={tr['spotify_popularity']} year={tr['release_year']}")


if __name__ == "__main__":
    main()
