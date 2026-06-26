"""Enrich tracks that lack attributes: Last.fm + LLM + deterministic.

Usage:
    python -m backend.scripts.enrich_batch [--limit N] [--min-attrs 20] [--concurrency 8]

Idempotent: skips tracks already at/above `--min-attrs` attributes.
Concurrent: processes multiple tracks in parallel via asyncio + thread pool
for blocking HTTP calls (lastfm + pollinations).
"""
from __future__ import annotations

import argparse
import asyncio
import sys
import traceback

# Windows cp1252 console crashes on non-ASCII track titles. Force utf-8.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # noqa: BLE001
    pass

from sqlalchemy import delete, func, select

from backend.db.base import SessionLocal
from backend.db.models import AttributeSource, Track, TrackAttribute
from backend.enrichment import (
    deterministic,
    lastfm_enricher,
    pollinations_enricher as llm_enricher,
)

# LLM outputs persisted under existing `claude` enum (kept for migration
# compatibility — represents "LLM-generated" source).
LLM_SOURCE = AttributeSource.claude


async def _attr_count(db, track_id: str) -> int:
    r = await db.execute(
        select(func.count(TrackAttribute.attribute_key)).where(
            TrackAttribute.track_id == track_id
        )
    )
    return r.scalar_one()


async def _replace_attrs(
    db, track_id: str, source: AttributeSource, attrs: dict[str, float]
) -> None:
    """Replace attrs from same source; skip keys already held by higher-priority source.

    Priority: spotify (deterministic) > lastfm (tag mapping) > LLM.
    First writer wins per (track_id, attribute_key).
    """
    if not attrs:
        return
    await db.execute(
        delete(TrackAttribute).where(
            TrackAttribute.track_id == track_id,
            TrackAttribute.source == source,
        )
    )
    await db.flush()
    existing_keys = {
        k for (k,) in (
            await db.execute(
                select(TrackAttribute.attribute_key).where(
                    TrackAttribute.track_id == track_id
                )
            )
        ).all()
    }
    for key, value in attrs.items():
        if key in existing_keys:
            continue
        db.add(
            TrackAttribute(
                track_id=track_id,
                attribute_key=key,
                value=value,
                source=source,
            )
        )


def _fetch_lastfm(primary_artist: str, title: str) -> dict:
    """Sync wrapper for thread pool."""
    try:
        return lastfm_enricher.enrich_track(primary_artist, title)
    except Exception as e:  # noqa: BLE001
        print(f"    lastfm error ({title[:30]}): {e}")
        return {"info": {}, "tags": [], "attributes": {}, "listeners": 0}


def _fetch_llm(title, artist, year, album, tags, listeners) -> dict:
    """Sync wrapper for thread pool."""
    try:
        return llm_enricher.estimate_attributes(
            title=title, artist=artist, year=year, album=album,
            tags=tags, listeners=listeners,
        )
    except Exception as e:  # noqa: BLE001
        print(f"    llm error ({title[:30]}): {e}")
        return {}


async def _enrich_one(track: Track, sem: asyncio.Semaphore, min_attrs: int) -> tuple[str, int, bool]:
    """Enrich one track in own session. Uses semaphore for I/O concurrency.

    Returns (title, final_attr_count, ok).
    """
    async with sem:
        try:
            primary_artist = track.artist.split(",")[0].strip()

            # 1. Deterministic from metadata (in-process, fast)
            det = deterministic.attrs_from_metadata(
                {
                    "release_year": track.release_year,
                    "duration_ms": track.duration_ms,
                    "has_featuring": "," in track.artist,
                }
            )

            # 2. Last.fm tags (blocking HTTP → thread)
            lf = await asyncio.to_thread(_fetch_lastfm, primary_artist, track.title)

            # 3. Pre-check: if det+lastfm already ≥ min_attrs, skip LLM call.
            #    Estimate union of keys (priority: det > lastfm).
            pre_keys = set(det.keys()) | set(lf["attributes"].keys())
            skip_llm = len(pre_keys) >= min_attrs

            llm_attrs: dict[str, float] = {}
            if not skip_llm:
                llm_attrs = await asyncio.to_thread(
                    _fetch_llm,
                    track.title, track.artist, track.release_year, track.album,
                    lf["tags"], lf["listeners"],
                )

            # Write to DB in own session (serialize per track, not per global)
            async with SessionLocal() as db:
                await _replace_attrs(db, track.id, AttributeSource.spotify, det)
                await _replace_attrs(db, track.id, AttributeSource.lastfm, lf["attributes"])
                if llm_attrs:
                    await _replace_attrs(db, track.id, LLM_SOURCE, llm_attrs)
                await db.commit()
                n = await _attr_count(db, track.id)
            tag = "SKIP-LLM" if skip_llm else "+LLM"
            return (f"{track.title[:40]:40s} - {track.artist[:25]:25s} attrs={n} [{tag}]", n, True)
        except Exception:  # noqa: BLE001
            traceback.print_exc()
            return (f"FAIL {track.title}", 0, False)


async def main(limit: int | None, min_attrs: int, concurrency: int) -> None:
    async with SessionLocal() as db:
        sub = (
            select(
                Track.id,
                func.count(TrackAttribute.attribute_key).label("nattrs"),
            )
            .outerjoin(TrackAttribute, TrackAttribute.track_id == Track.id)
            .group_by(Track.id)
            .subquery()
        )
        q = (
            select(Track)
            .join(sub, sub.c.id == Track.id)
            .where(sub.c.nattrs < min_attrs)
            .order_by(Track.spotify_popularity.desc().nullslast())
        )
        if limit:
            q = q.limit(limit)
        tracks = (await db.execute(q)).scalars().all()
        print(f"[enrich] {len(tracks)} tracks need enrichment (min_attrs={min_attrs}, concurrency={concurrency})")

    sem = asyncio.Semaphore(concurrency)
    done = 0
    total = len(tracks)

    async def _wrap(t):
        nonlocal done
        msg, _n, _ok = await _enrich_one(t, sem, min_attrs)
        done += 1
        print(f"  [{done}/{total}] {msg}")

    await asyncio.gather(*(_wrap(t) for t in tracks))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--min-attrs", type=int, default=20)
    p.add_argument("--concurrency", type=int, default=8)
    args = p.parse_args()
    asyncio.run(main(args.limit, args.min_attrs, args.concurrency))
