"""Disk JSON cache for external API responses.

Goal: avoid paying API quota twice during development. Each namespace
(spotify, lastfm, gemini) gets its own subfolder. Keys are hashed to
keep filenames short and filesystem-safe.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

CACHE_ROOT = Path(__file__).resolve().parent.parent.parent / ".cache" / "enrichment"


def _path(namespace: str, key: str) -> Path:
    h = hashlib.sha1(key.encode("utf-8")).hexdigest()
    folder = CACHE_ROOT / namespace
    folder.mkdir(parents=True, exist_ok=True)
    return folder / f"{h}.json"


def get(namespace: str, key: str) -> Any | None:
    p = _path(namespace, key)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def put(namespace: str, key: str, value: Any) -> None:
    p = _path(namespace, key)
    p.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


def cached_call(namespace: str, key: str, fn):
    """Sync helper: return cached value or call fn() and cache it.

    Skips caching empty results (empty dict/list) so transient API failures
    don't poison the cache with permanent empties.
    """
    hit = get(namespace, key)
    if hit is not None:
        return hit
    value = fn()
    if value:
        put(namespace, key, value)
    return value
