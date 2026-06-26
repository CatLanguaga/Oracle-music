"""Entrypoint FastAPI.

Lifespan preloads the (large, immutable) AttributeMatrix and question map
once, then shares them via app.state to all requests. Reloading per-request
would dominate latency.
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.api.oracle import router as oracle_router
from backend.api.suggest import router as suggest_router
from backend.cache import get_redis
from backend.config import get_settings
from backend.core.attribute_matrix import load_matrix
from backend.core.question_selector import load_question_map
from backend.core.session_manager import SessionStore


settings = get_settings()
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
log = logging.getLogger("nyota.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("startup: loading matrix")
    am = await load_matrix(min_attrs=10)
    log.info("startup: matrix %d tracks x %d attrs", am.n_tracks, am.n_attrs)
    qmap = await load_question_map(am.attr_keys)
    log.info("startup: %d questions", len(qmap))

    app.state.matrix = am
    app.state.qmap = qmap
    app.state.session_store = SessionStore(client=get_redis())
    try:
        yield
    finally:
        log.info("shutdown")


app = FastAPI(title="Nyota — Oráculo Musical", version="0.1.0", lifespan=lifespan)
app.include_router(oracle_router)
app.include_router(suggest_router)


@app.get("/health")
async def health() -> dict:
    return {
        "status": "ok",
        "env": settings.app_env,
        "db": settings.database_url.split("://")[0],
        "cache": "fakeredis" if settings.use_fakeredis else "redis",
        "tracks": getattr(app.state, "matrix", None) and app.state.matrix.n_tracks,
        "questions": getattr(app.state, "qmap", None) and len(app.state.qmap),
    }
