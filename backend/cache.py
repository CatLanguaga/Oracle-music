"""Async cache client. Real Redis in prod, fakeredis in dev."""
from __future__ import annotations

from functools import lru_cache

import fakeredis.aioredis
import redis.asyncio as redis

from backend.config import get_settings


@lru_cache
def get_redis() -> redis.Redis:
    settings = get_settings()
    if settings.use_fakeredis:
        return fakeredis.aioredis.FakeRedis(decode_responses=False)
    return redis.from_url(settings.redis_url, decode_responses=False)
