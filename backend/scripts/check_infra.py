"""Smoke test de DB + cache. Soporta dev (sqlite + fakeredis) y prod (postgres + redis)."""
import asyncio
import sys

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

from backend.config import get_settings


async def check_db() -> bool:
    s = get_settings()
    try:
        engine = create_async_engine(s.database_url)
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            assert result.scalar() == 1
        await engine.dispose()
        print(f"[ok] db: {s.database_url}")
        return True
    except Exception as e:
        print(f"[fail] db: {e}")
        return False


async def check_cache() -> bool:
    s = get_settings()
    try:
        if s.use_fakeredis:
            import fakeredis.aioredis as fakeredis_aio

            client = fakeredis_aio.FakeRedis()
        else:
            import redis.asyncio as redis

            client = redis.from_url(s.redis_url)
        await client.set("__nyota_smoke__", "ok", ex=5)
        val = await client.get("__nyota_smoke__")
        await client.aclose()
        assert val == b"ok"
        print(f"[ok] cache: {s.redis_url}")
        return True
    except Exception as e:
        print(f"[fail] cache: {e}")
        return False


async def main() -> int:
    results = await asyncio.gather(check_db(), check_cache())
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
