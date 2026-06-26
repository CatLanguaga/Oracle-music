"""Persist OracleState in Redis.

Live state in Redis (TTL = settings.session_ttl_minutes). The AttributeMatrix
is shared/process-wide and rehydrated from app.state on each request.

Wire format (msgpack would be smaller, but json keeps debugging trivial):
    {
        "probs_b64": base64(float32 ndarray bytes),
        "n": int,
        "asked": [int, ...],
        "log":   [[int, float], ...]
    }
"""
from __future__ import annotations

import base64
import json
from dataclasses import dataclass

import numpy as np
import redis.asyncio as redis

from backend.config import get_settings
from backend.core.attribute_matrix import AttributeMatrix
from backend.core.oracle_engine import OracleState

KEY_PREFIX = "nyota:session:"


def _key(session_id: str) -> str:
    return f"{KEY_PREFIX}{session_id}"


def _encode(state: OracleState) -> bytes:
    payload = {
        "n": int(state.probs.size),
        "probs_b64": base64.b64encode(
            state.probs.astype(np.float32).tobytes()
        ).decode("ascii"),
        "asked": sorted(state.asked_attrs),
        "log": [[int(i), float(a)] for i, a in state.answers_log],
    }
    return json.dumps(payload).encode("utf-8")


def _decode(raw: bytes, am: AttributeMatrix) -> OracleState:
    payload = json.loads(raw.decode("utf-8"))
    n = int(payload["n"])
    if n != am.n_tracks:
        raise ValueError(
            f"session built against {n} tracks, current matrix has {am.n_tracks}"
        )
    probs = np.frombuffer(
        base64.b64decode(payload["probs_b64"]), dtype=np.float32
    ).astype(np.float64).copy()
    return OracleState(
        am=am,
        probs=probs,
        asked_attrs=set(int(x) for x in payload["asked"]),
        answers_log=[(int(i), float(a)) for i, a in payload["log"]],
    )


@dataclass
class SessionStore:
    client: redis.Redis

    async def save(self, session_id: str, state: OracleState) -> None:
        ttl = get_settings().session_ttl_minutes * 60
        await self.client.set(_key(session_id), _encode(state), ex=ttl)

    async def load(
        self, session_id: str, am: AttributeMatrix
    ) -> OracleState | None:
        raw = await self.client.get(_key(session_id))
        if raw is None:
            return None
        return _decode(raw, am)

    async def delete(self, session_id: str) -> None:
        await self.client.delete(_key(session_id))
