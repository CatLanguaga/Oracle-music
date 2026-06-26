"""Oracle gameplay endpoints.

Flow:
    POST /oracle/session            → JWT + first question
    POST /oracle/answer             → next question or guess
    POST /oracle/give-up            → guess regardless
    POST /oracle/confirm            → close session (audit row)
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status

from backend.api import auth
from backend.api.deps import get_matrix, get_qmap, get_store
from backend.api.schemas import (
    AnswerIn,
    ConfirmIn,
    ConfirmOut,
    GuessOut,
    QuestionOut,
    SessionCreateOut,
    TrackOut,
    TurnOut,
)
from backend.core import oracle_engine as oe
from backend.core.attribute_matrix import AttributeMatrix
from backend.core.question_selector import select_attribute
from backend.core.session_manager import SessionStore
from sqlalchemy import update

from backend.db.base import SessionLocal
from backend.db.models import GameSession, SessionResult

log = logging.getLogger("nyota.api.oracle")
router = APIRouter(prefix="/oracle", tags=["oracle"])


# ------------------------------------------------------------------ helpers

def _track_out(am: AttributeMatrix, row: int) -> TrackOut:
    t = am.tracks[row]
    return TrackOut(
        track_id=t.track_id,
        title=t.title,
        artist=t.artist,
        album=t.album,
        album_art_url=t.album_art_url,
        release_year=t.release_year,
    )


def _next_question(
    state: oe.OracleState, qmap: dict[int, str]
) -> QuestionOut | None:
    attr_idx = select_attribute(state, qmap)
    if attr_idx is None:
        return None
    return QuestionOut(
        attr_idx=attr_idx,
        attribute_key=state.am.attr_keys[attr_idx],
        text=qmap[attr_idx],
        question_number=state.n_questions + 1,
        candidates=oe.n_candidates(state),
    )


def _guess(state: oe.OracleState) -> GuessOut:
    row, prob = oe.top_candidate(state)
    return GuessOut(
        track=_track_out(state.am, row),
        prob=prob,
        questions_asked=state.n_questions,
        top_k=[(_track_out(state.am, r), p) for r, p in oe.top_k(state, 5)],
    )


# ------------------------------------------------------------------ routes

@router.post("/session", response_model=SessionCreateOut)
async def create_session(
    am: AttributeMatrix = Depends(get_matrix),
    qmap: dict[int, str] = Depends(get_qmap),
    store: SessionStore = Depends(get_store),
) -> SessionCreateOut:
    state = oe.init_state(am)
    sid = auth.new_session_id()
    await store.save(sid, state)

    async with SessionLocal() as db:
        db.add(GameSession(id=sid))
        await db.commit()

    q = _next_question(state, qmap)
    if q is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="no questions available",
        )
    log.info("session.create sid=%s tracks=%d", sid, am.n_tracks)
    return SessionCreateOut(
        token=auth.issue_token(sid),
        session_id=sid,
        n_tracks=am.n_tracks,
        n_attrs=am.n_attrs,
        question=q,
    )


@router.post("/answer", response_model=TurnOut)
async def answer(
    body: AnswerIn,
    sid: str = Depends(auth.session_id_from_header),
    am: AttributeMatrix = Depends(get_matrix),
    qmap: dict[int, str] = Depends(get_qmap),
    store: SessionStore = Depends(get_store),
) -> TurnOut:
    state = await store.load(sid, am)
    if state is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="session not found"
        )
    if not (0 <= body.attr_idx < am.n_attrs):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="bad attr_idx"
        )
    if body.attr_idx in state.asked_attrs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="attr already asked"
        )

    oe.update(state, body.attr_idx, body.answer)
    await store.save(sid, state)
    log.info(
        "session.answer sid=%s q=%d attr=%s ans=%.2f cands=%d",
        sid,
        state.n_questions,
        am.attr_keys[body.attr_idx],
        body.answer,
        oe.n_candidates(state),
    )

    if oe.should_guess(state):
        return TurnOut(state="guess", guess=_guess(state))

    q = _next_question(state, qmap)
    if q is None:
        return TurnOut(state="guess", guess=_guess(state))
    return TurnOut(state="question", question=q)


@router.post("/give-up", response_model=GuessOut)
async def give_up(
    sid: str = Depends(auth.session_id_from_header),
    am: AttributeMatrix = Depends(get_matrix),
    store: SessionStore = Depends(get_store),
) -> GuessOut:
    state = await store.load(sid, am)
    if state is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="session not found"
        )
    log.info("session.give_up sid=%s q=%d", sid, state.n_questions)
    return _guess(state)


@router.post("/confirm", response_model=ConfirmOut)
async def confirm(
    body: ConfirmIn,
    sid: str = Depends(auth.session_id_from_header),
    am: AttributeMatrix = Depends(get_matrix),
    store: SessionStore = Depends(get_store),
) -> ConfirmOut:
    state = await store.load(sid, am)
    if state is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="session not found"
        )

    guessed_row, _ = oe.top_candidate(state)
    guessed_id = am.tracks[guessed_row].track_id
    result = SessionResult.correct if body.correct else SessionResult.wrong

    async with SessionLocal() as db:
        await db.execute(
            update(GameSession)
            .where(GameSession.id == sid)
            .values(
                ended_at=datetime.now(timezone.utc),
                questions_count=state.n_questions,
                result=result,
                guessed_track_id=guessed_id,
                actual_track_id=body.actual_track_id,
            )
        )
        await db.commit()
    await store.delete(sid)
    log.info(
        "session.confirm sid=%s result=%s q=%d guess=%s actual=%s",
        sid,
        result.value,
        state.n_questions,
        guessed_id,
        body.actual_track_id,
    )
    return ConfirmOut(result=result.value)
