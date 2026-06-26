"""Import seed-artist top tracks into the `tracks` table.

Usage:
    python -m backend.scripts.import_artists [--limit N] [--market US]

Idempotent: existing track ids are skipped. Designed to be re-run safely.
"""
from __future__ import annotations

import argparse
import asyncio

from backend.db.base import SessionLocal
from backend.db.models import Track
from backend.enrichment.spotify_enricher import (
    fetch_artist_top_tracks,
    search_artist,
)
from backend.seeds.artists import SEED_ARTISTS


async def _upsert_track(db, track: dict) -> bool:
    """Insert track if missing. Return True if newly inserted."""
    existing = await db.get(Track, track["id"])
    if existing:
        return False
    db.add(
        Track(
            id=track["id"],
            title=track["title"],
            artist=track["artist"],
            album=track["album"],
            album_art_url=track["album_art_url"],
            spotify_popularity=track["spotify_popularity"],
            duration_ms=track["duration_ms"],
            release_year=track["release_year"],
        )
    )
    return True


async def main(limit_artists: int | None, market: str) -> None:
    artists = SEED_ARTISTS[:limit_artists] if limit_artists else SEED_ARTISTS
    print(f"[import] {len(artists)} artists, market={market}")
    total_new = 0
    total_seen = 0
    async with SessionLocal() as db:
        for i, name in enumerate(artists, 1):
            art = search_artist(name)
            if not art:
                print(f"  [{i}/{len(artists)}] {name!r:30s} NOT FOUND")
                continue
            tops = fetch_artist_top_tracks(art["id"], market=market)
            new_here = 0
            for tr in tops:
                total_seen += 1
                if await _upsert_track(db, tr):
                    new_here += 1
                    total_new += 1
            await db.commit()
            print(f"  [{i}/{len(artists)}] {name:30s} +{new_here}/{len(tops)} (id={art['id']})")
    print(f"[import] done: {total_new} new tracks ({total_seen} seen)")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--limit", type=int, default=None, help="limit number of artists")
    p.add_argument("--market", type=str, default="US")
    args = p.parse_args()
    asyncio.run(main(args.limit, args.market))
