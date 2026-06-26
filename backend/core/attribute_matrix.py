"""Load tracks + attributes from DB → dense numpy matrix.

Matrix layout:
    M[i, j] = P(attribute_j | track_i), values in [0, 1].
Missing attrs default to 0.5 (no signal). Order is stable:
    track_ids[i] ↔ row i
    attr_keys[j] ↔ col j
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sqlalchemy import func, select

from backend.db.base import SessionLocal
from backend.db.models import Track, TrackAttribute
from backend.seeds.attributes import ATTRIBUTES


@dataclass
class TrackMeta:
    track_id: str
    title: str
    artist: str
    album: str | None
    album_art_url: str | None
    release_year: int | None


@dataclass
class AttributeMatrix:
    matrix: np.ndarray  # (N_tracks, N_attrs) float32
    track_ids: list[str]
    attr_keys: list[str]
    tracks: list[TrackMeta]

    @property
    def n_tracks(self) -> int:
        return len(self.track_ids)

    @property
    def n_attrs(self) -> int:
        return len(self.attr_keys)

    def attr_index(self, key: str) -> int:
        return self.attr_keys.index(key)

    def track_index(self, track_id: str) -> int:
        return self.track_ids.index(track_id)


async def load_matrix(min_attrs: int = 10) -> AttributeMatrix:
    """Build matrix of tracks with at least `min_attrs` attributes."""
    attr_keys = [k for k, _, _ in ATTRIBUTES]
    attr_idx = {k: i for i, k in enumerate(attr_keys)}

    async with SessionLocal() as db:
        sub = (
            select(
                Track.id,
                func.count(TrackAttribute.attribute_key).label("n"),
            )
            .outerjoin(TrackAttribute, TrackAttribute.track_id == Track.id)
            .group_by(Track.id)
            .subquery()
        )
        q = (
            select(Track)
            .join(sub, sub.c.id == Track.id)
            .where(sub.c.n >= min_attrs)
            .order_by(Track.spotify_popularity.desc().nullslast())
        )
        tracks = (await db.execute(q)).scalars().all()

        track_ids = [t.id for t in tracks]
        track_meta = [
            TrackMeta(
                track_id=t.id,
                title=t.title,
                artist=t.artist,
                album=t.album,
                album_art_url=t.album_art_url,
                release_year=t.release_year,
            )
            for t in tracks
        ]

        # Pre-fill with 0.5 (neutral prior for missing attrs)
        M = np.full((len(tracks), len(attr_keys)), 0.5, dtype=np.float32)
        track_id_to_row = {tid: i for i, tid in enumerate(track_ids)}

        rows = (
            await db.execute(
                select(
                    TrackAttribute.track_id,
                    TrackAttribute.attribute_key,
                    TrackAttribute.value,
                ).where(TrackAttribute.track_id.in_(track_ids))
            )
        ).all()
        for tid, key, value in rows:
            r = track_id_to_row.get(tid)
            c = attr_idx.get(key)
            if r is None or c is None:
                continue
            M[r, c] = value

    return AttributeMatrix(
        matrix=M,
        track_ids=track_ids,
        attr_keys=attr_keys,
        tracks=track_meta,
    )
