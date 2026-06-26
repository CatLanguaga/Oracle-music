"""Attributes derivable from Spotify metadata alone — no API call needed."""
from __future__ import annotations

from datetime import date


def attrs_from_metadata(track: dict) -> dict[str, float]:
    """Compute era + duration + featuring attributes."""
    out: dict[str, float] = {}
    year = track.get("release_year")
    if year:
        if year < 2000:
            out["released_before_2000"] = 1.0
        if 1970 <= year <= 1979:
            out["released_in_70s"] = 1.0
        if 1980 <= year <= 1989:
            out["released_in_80s"] = 1.0
        if 1990 <= year <= 1999:
            out["released_in_90s"] = 1.0
        if year >= 2010:
            out["released_after_2010"] = 1.0
        if year >= date.today().year - 3:
            out["released_recent_3y"] = 1.0

    dur = track.get("duration_ms")
    if dur:
        if dur > 5 * 60 * 1000:
            out["is_longer_than_5min"] = 1.0
        if dur < 3 * 60 * 1000:
            out["is_shorter_than_3min"] = 1.0

    if track.get("has_featuring"):
        out["has_featuring"] = 1.0

    return out
