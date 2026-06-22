"""Verifica conexión a Postgres y Redis. Corre tras `docker compose up -d`."""
import asyncio
import os
import sys

import asyncpg
import redis.asyncio as redis
from dotenv import load_dotenv

load_dotenv()


async def check_postgres() -> bool:
    url = os.environ["DATABASE_URL"].replace("postgresql+asyncpg://", "postgresql://")
    try:
        conn = await asyncpg.connect(url)
        version = await conn.fetchval("SELECT version()")
        await conn.close()
        print(f"[ok] postgres: {version.split(',')[0]}")
        return True
    except Exception as e:
        print(f"[fail] postgres: {e}")
        return False


async def check_redis() -> bool:
    try:
        client = redis.from_url(os.environ["REDIS_URL"])
        pong = await client.ping()
        await client.aclose()
        print(f"[ok] redis: ping={pong}")
        return True
    except Exception as e:
        print(f"[fail] redis: {e}")
        return False


async def main() -> int:
    results = await asyncio.gather(check_postgres(), check_redis())
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
