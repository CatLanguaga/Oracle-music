"""Gemini-based semantic attribute enrichment.

Given track metadata + Last.fm tags, ask Gemini to estimate the
remaining subjective attributes (mood, energy, lyrics topic, etc.)
as a JSON dict of {attribute_key: float in [0,1]}.

Strict prompt: only return keys from ALLOWED_KEYS. Reject malformed.
"""
from __future__ import annotations

import json
import time
from typing import Any

from google import genai
from google.genai import types
from google.genai import errors as genai_errors

from backend.config import get_settings
from backend.enrichment import cache
from backend.seeds.attributes import ATTRIBUTES

ALLOWED_KEYS: set[str] = {key for key, _, _ in ATTRIBUTES}

# Attributes Gemini should NOT guess — already covered deterministically
# by Spotify metadata or Last.fm tag mapping.
DETERMINISTIC_KEYS = {
    "released_before_2000",
    "released_in_90s",
    "released_in_80s",
    "released_in_70s",
    "released_after_2010",
    "released_recent_3y",
    "is_longer_than_5min",
    "is_shorter_than_3min",
    "has_featuring",
}
LLM_KEYS: list[str] = sorted(ALLOWED_KEYS - DETERMINISTIC_KEYS)


_PROMPT = """Eres un experto musical. Te doy una canción y sus tags. Devuelve un JSON
con probabilidades (0.0 a 1.0) de que cada atributo aplique a la canción.

Reglas:
- SOLO usa las claves listadas abajo. No inventes claves.
- 0.0 = definitivamente no. 1.0 = definitivamente sí. 0.5 = no estoy seguro.
- Devuelve SOLO el objeto JSON, sin texto extra, sin markdown.

Claves permitidas:
{keys}

Canción:
Título: {title}
Artista: {artist}
Año: {year}
Álbum: {album}
Tags Last.fm (top): {tags}
Listeners Last.fm: {listeners}
"""


def _client():
    s = get_settings()
    return genai.Client(api_key=s.gemini_api_key)


def _parse_json(text: str) -> dict[str, float]:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
        text = text.strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return {}
    if not isinstance(data, dict):
        return {}
    out: dict[str, float] = {}
    for k, v in data.items():
        if k not in ALLOWED_KEYS:
            continue
        try:
            f = float(v)
        except (TypeError, ValueError):
            continue
        out[k] = max(0.0, min(1.0, f))
    return out


def estimate_attributes(
    title: str,
    artist: str,
    year: int | None,
    album: str | None,
    tags: list[tuple[str, int]],
    listeners: int = 0,
) -> dict[str, float]:
    """Ask Gemini for subjective attributes. Cached by (title, artist)."""
    cache_key = f"attrs:{artist.lower()}|{title.lower()}"
    s = get_settings()

    def _call() -> dict[str, float]:
        prompt = _PROMPT.format(
            keys=", ".join(LLM_KEYS),
            title=title,
            artist=artist,
            year=year or "desconocido",
            album=album or "desconocido",
            tags=", ".join(f"{t}({w})" for t, w in tags[:15]) or "ninguno",
            listeners=listeners,
        )
        cfg = types.GenerateContentConfig(
            temperature=0.2,
            response_mime_type="application/json",
        )
        client = _client()
        models_to_try = [s.gemini_model, "gemini-2.5-flash-lite"]
        last_exc: Exception | None = None
        for model in models_to_try:
            for attempt in range(3):
                try:
                    resp = client.models.generate_content(
                        model=model, contents=prompt, config=cfg
                    )
                    return _parse_json(resp.text or "")
                except genai_errors.APIError as e:
                    last_exc = e
                    status = getattr(e, "code", None) or getattr(e, "status_code", None)
                    if status in (429, 500, 502, 503, 504):
                        time.sleep(2 ** attempt)
                        continue
                    raise
        raise last_exc if last_exc else RuntimeError("gemini exhausted retries")

    return cache.cached_call("gemini", cache_key, _call)
