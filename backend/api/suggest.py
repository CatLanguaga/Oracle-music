"""Suggest a track when the oracle fails. Persists pending row only;
enrichment + approval happen async in Fase 8.
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends

from backend.api import auth
from backend.api.schemas import SuggestIn, SuggestOut
from backend.db.base import SessionLocal
from backend.db.models import SuggestedTrack, SuggestionStatus

log = logging.getLogger("nyota.api.suggest")
router = APIRouter(prefix="/oracle", tags=["oracle"])


@router.post("/suggest", response_model=SuggestOut)
async def suggest(
    body: SuggestIn,
    sid: str = Depends(auth.session_id_from_header),
) -> SuggestOut:
    row = SuggestedTrack(
        session_id=sid,
        title_raw=body.title.strip(),
        artist_raw=body.artist.strip(),
        spotify_track_id=body.spotify_track_id,
        status=SuggestionStatus.pending,
    )
    async with SessionLocal() as db:
        db.add(row)
        await db.commit()
        await db.refresh(row)
    log.info("suggest sid=%s id=%s '%s' - '%s'", sid, row.id, body.title, body.artist)
    return SuggestOut(suggestion_id=row.id, status=row.status.value)
