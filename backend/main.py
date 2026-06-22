"""Entrypoint FastAPI. Por ahora solo healthcheck."""
from fastapi import FastAPI

from backend.config import get_settings

settings = get_settings()
app = FastAPI(title="Nyota — Oráculo Musical", version="0.0.1")


@app.get("/health")
async def health() -> dict:
    return {
        "status": "ok",
        "env": settings.app_env,
        "db": settings.database_url.split("://")[0],
        "cache": "fakeredis" if settings.use_fakeredis else "redis",
    }
