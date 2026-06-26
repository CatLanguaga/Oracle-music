"""Pollinations-based semantic attribute enrichment.

Drop-in replacement for gemini_enricher. Uses the OpenAI-compatible
endpoint at https://text.pollinations.ai/openai with a seed API key.

Same interface as gemini_enricher: estimate_attributes(...) -> dict.
"""
from __future__ import annotations

import json
import time

import httpx

from backend.config import get_settings
from backend.enrichment import cache
from backend.seeds.attributes import ATTRIBUTES

ALLOWED_KEYS: set[str] = {key for key, _, _ in ATTRIBUTES}

DETERMINISTIC_KEYS = {
    "released_before_2000", "released_in_90s", "released_in_80s",
    "released_in_70s", "released_after_2010", "released_recent_3y",
    "is_longer_than_5min", "is_shorter_than_3min", "has_featuring",
}
LLM_KEYS: list[str] = sorted(ALLOWED_KEYS - DETERMINISTIC_KEYS)

ENDPOINT = "https://text.pollinations.ai/openai"

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


def _parse_json(text: str) -> dict[str, float]:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
        text = text.strip()
    # Some models wrap output with prose; isolate first {...} block.
    if not text.startswith("{"):
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            text = text[start : end + 1]
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
    """Ask Pollinations for subjective attributes. Cached by (title, artist)."""
    s = get_settings()
    cache_key = f"attrs:{s.pollinations_model}:{artist.lower()}|{title.lower()}"

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
        payload = {
            "model": s.pollinations_model,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
            "max_tokens": 16000,
            "reasoning_effort": "low",
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {s.pollinations_api_key}",
        }
        last_exc: Exception | None = None
        for attempt in range(4):
            try:
                with httpx.Client(timeout=120.0) as c:
                    r = c.post(ENDPOINT, json=payload, headers=headers)
                if r.status_code in (429, 500, 502, 503, 504):
                    time.sleep(2 ** attempt)
                    continue
                r.raise_for_status()
                data = r.json()
                choices = data.get("choices") or []
                if not choices:
                    last_exc = RuntimeError(f"empty choices: {data}")
                    time.sleep(2 ** attempt)
                    continue
                msg = choices[0].get("message") or {}
                content = msg.get("content")
                if not content:
                    # Sometimes content is empty when finish_reason='length' or
                    # the model emits reasoning only. Retry with explicit instruction.
                    last_exc = RuntimeError(
                        f"empty content, finish={choices[0].get('finish_reason')}"
                    )
                    time.sleep(2 ** attempt)
                    continue
                parsed = _parse_json(content)
                if len(parsed) < 10 and attempt < 3:
                    last_exc = RuntimeError(f"parsed too small: {len(parsed)} keys")
                    time.sleep(2 ** attempt)
                    continue
                return parsed
            except (httpx.HTTPError, ValueError) as e:
                last_exc = e
                time.sleep(2 ** attempt)
        if last_exc:
            raise last_exc
        return {}

    return cache.cached_call("pollinations", cache_key, _call)
