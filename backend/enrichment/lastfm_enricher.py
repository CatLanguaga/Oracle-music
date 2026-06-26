"""Last.fm client + tag-to-attribute mapping.

Last.fm gives:
- track.getInfo: listeners, playcount, summary, top tags (with weight 0-100).
- track.getTopTags: more tag detail.

We map tags → attribute keys with a hand-tuned dictionary. Tag
weights become attribute values in [0, 1].
"""
from __future__ import annotations

from typing import Any

import httpx

from backend.config import get_settings
from backend.enrichment import cache

BASE_URL = "https://ws.audioscrobbler.com/2.0/"

# Tag → list[attribute_key] mapping. Lowercase substring match.
# When a tag matches, its (weight/100) is OR-merged into the attribute value.
TAG_TO_ATTRS: dict[str, list[str]] = {
    # genres
    "rock": ["is_rock"],
    "classic rock": ["is_rock"],
    "hard rock": ["is_rock"],
    "alternative rock": ["is_rock", "is_indie_alt"],
    "indie rock": ["is_rock", "is_indie_alt"],
    "indie": ["is_indie_alt"],
    "alternative": ["is_indie_alt"],
    "pop": ["is_pop"],
    "synthpop": ["is_pop", "is_synth_driven"],
    "electropop": ["is_pop", "is_electronic"],
    "electronic": ["is_electronic"],
    "electronica": ["is_electronic"],
    "edm": ["is_electronic", "is_danceable"],
    "house": ["is_electronic", "is_danceable"],
    "techno": ["is_electronic", "is_danceable"],
    "dance": ["is_electronic", "is_danceable"],
    "hip-hop": ["is_hiphop_rap"],
    "hip hop": ["is_hiphop_rap"],
    "rap": ["is_hiphop_rap"],
    "trap": ["is_hiphop_rap"],
    "jazz": ["is_jazz_blues"],
    "blues": ["is_jazz_blues"],
    "classical": ["is_classical", "has_strings"],
    "orchestral": ["is_classical", "has_strings"],
    "reggaeton": ["is_latin", "lyrics_in_spanish", "is_danceable"],
    "salsa": ["is_latin", "lyrics_in_spanish", "is_danceable"],
    "bachata": ["is_latin", "lyrics_in_spanish"],
    "cumbia": ["is_latin", "lyrics_in_spanish"],
    "latin": ["is_latin"],
    "latino": ["is_latin"],
    "metal": ["is_metal", "has_electric_guitar", "is_energetic"],
    "heavy metal": ["is_metal", "has_electric_guitar"],
    "rnb": ["is_rnb_soul"],
    "r&b": ["is_rnb_soul"],
    "soul": ["is_rnb_soul"],
    "country": ["is_country_folk"],
    "folk": ["is_country_folk", "is_acoustic"],
    "punk": ["is_punk", "is_rebellious"],
    "post-punk": ["is_punk"],
    "reggae": ["is_reggae"],
    # moods
    "sad": ["is_sad_mood"],
    "melancholic": ["is_sad_mood"],
    "happy": ["is_happy_mood"],
    "love": ["is_romantic"],
    "love song": ["is_romantic"],
    "heartbreak": ["is_about_heartbreak", "is_sad_mood"],
    "party": ["is_party", "is_danceable"],
    "chill": ["is_chill"],
    "chillout": ["is_chill"],
    "relax": ["is_chill"],
    # energy / texture
    "instrumental": ["is_instrumental"],
    "acoustic": ["is_acoustic"],
    "ballad": ["is_ballad"],
    "guitar": ["has_electric_guitar"],
    "piano": ["has_piano"],
    "synth": ["is_synth_driven"],
    # era hints
    "80s": ["released_in_80s", "released_before_2000"],
    "90s": ["released_in_90s", "released_before_2000"],
    "70s": ["released_in_70s", "released_before_2000"],
    "oldies": ["released_before_2000"],
    # lyrics language hints
    "spanish": ["lyrics_in_spanish"],
    "english": ["lyrics_in_english"],
}


def _client() -> httpx.Client:
    return httpx.Client(timeout=15.0)


def _get(method: str, params: dict[str, Any]) -> dict[str, Any] | None:
    s = get_settings()
    q = {
        "method": method,
        "api_key": s.lastfm_api_key,
        "format": "json",
        **params,
    }
    cache_key = method + ":" + ":".join(f"{k}={v}" for k, v in sorted(params.items()))

    def _call() -> dict[str, Any]:
        with _client() as c:
            r = c.get(BASE_URL, params=q)
            r.raise_for_status()
            return r.json()

    return cache.cached_call("lastfm", cache_key, _call)


def get_track_info(artist: str, track: str) -> dict[str, Any] | None:
    data = _get("track.getInfo", {"artist": artist, "track": track, "autocorrect": "1"})
    return (data or {}).get("track")


def get_top_tags(artist: str, track: str) -> list[tuple[str, int]]:
    """Return [(tag_name, weight 0-100)]."""
    data = _get(
        "track.getTopTags", {"artist": artist, "track": track, "autocorrect": "1"}
    )
    tags = ((data or {}).get("toptags") or {}).get("tag") or []
    out: list[tuple[str, int]] = []
    for t in tags:
        name = (t.get("name") or "").strip().lower()
        try:
            w = int(t.get("count") or 0)
        except (TypeError, ValueError):
            w = 0
        if name:
            out.append((name, w))
    return out


def tags_to_attributes(tags: list[tuple[str, int]]) -> dict[str, float]:
    """Apply TAG_TO_ATTRS mapping. Highest weight wins per attribute."""
    out: dict[str, float] = {}
    for name, weight in tags:
        val = max(0.0, min(1.0, weight / 100.0))
        for tag_key, attrs in TAG_TO_ATTRS.items():
            if tag_key in name:
                for a in attrs:
                    if val > out.get(a, 0.0):
                        out[a] = val
    return out


def enrich_track(artist: str, title: str) -> dict[str, Any]:
    """Return {info, tags, attributes} for a (artist, title)."""
    info = get_track_info(artist, title) or {}
    tags = get_top_tags(artist, title)
    attrs = tags_to_attributes(tags)
    # Fame signal: listeners count → is_very_famous
    try:
        listeners = int(info.get("listeners") or 0)
    except (TypeError, ValueError):
        listeners = 0
    if listeners >= 1_000_000:
        attrs["is_very_famous"] = max(attrs.get("is_very_famous", 0.0), 1.0)
    elif listeners >= 250_000:
        attrs["is_very_famous"] = max(attrs.get("is_very_famous", 0.0), 0.7)
    elif listeners >= 50_000:
        attrs["is_very_famous"] = max(attrs.get("is_very_famous", 0.0), 0.4)
    return {"info": info, "tags": tags, "attributes": attrs, "listeners": listeners}
