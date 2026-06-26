"""Request/response models for the Oracle API."""
from __future__ import annotations

from pydantic import BaseModel, Field


class TrackOut(BaseModel):
    track_id: str
    title: str
    artist: str
    album: str | None = None
    album_art_url: str | None = None
    release_year: int | None = None


class QuestionOut(BaseModel):
    attr_idx: int
    attribute_key: str
    text: str
    question_number: int
    candidates: int


class GuessOut(BaseModel):
    track: TrackOut
    prob: float
    questions_asked: int
    top_k: list[tuple[TrackOut, float]]


class SessionCreateOut(BaseModel):
    token: str
    session_id: str
    n_tracks: int
    n_attrs: int
    question: QuestionOut


class TurnOut(BaseModel):
    """Either another question or a guess."""

    state: str = Field(..., description="'question' | 'guess'")
    question: QuestionOut | None = None
    guess: GuessOut | None = None


class AnswerIn(BaseModel):
    attr_idx: int
    answer: float = Field(..., ge=0.0, le=1.0)


class ConfirmIn(BaseModel):
    correct: bool
    actual_track_id: str | None = None


class ConfirmOut(BaseModel):
    result: str  # "correct" | "wrong" | "gave_up"


class SuggestIn(BaseModel):
    title: str
    artist: str
    spotify_track_id: str | None = None


class SuggestOut(BaseModel):
    suggestion_id: str
    status: str
