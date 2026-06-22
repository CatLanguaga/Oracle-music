"""Modelos de datos del Oráculo.

Diagrama:
  tracks ── track_attributes ── attributes ── questions
                ▲                                 ▲
                │                                 │
          attribute_votes                     sessions
                                                  │
                                          suggested_tracks
"""
from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base


def _uuid_str() -> str:
    return str(uuid.uuid4())


# ------------------------------------------------------------------ enums

class AttributeSource(str, enum.Enum):
    spotify = "spotify"
    lastfm = "lastfm"
    claude = "claude"
    crowd = "crowd"
    manual = "manual"


class SessionResult(str, enum.Enum):
    correct = "correct"
    wrong = "wrong"
    gave_up = "gave_up"
    abandoned = "abandoned"


class SuggestionStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


# ------------------------------------------------------------------ tracks

class Track(Base):
    __tablename__ = "tracks"

    id: Mapped[str] = mapped_column(String, primary_key=True)  # spotify_track_id
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    artist: Mapped[str] = mapped_column(String(500), nullable=False)
    album: Mapped[str | None] = mapped_column(String(500))
    album_art_url: Mapped[str | None] = mapped_column(String(1000))
    spotify_popularity: Mapped[int | None] = mapped_column(Integer)
    duration_ms: Mapped[int | None] = mapped_column(Integer)
    release_year: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    attributes: Mapped[list[TrackAttribute]] = relationship(
        back_populates="track", cascade="all, delete-orphan"
    )


# ------------------------------------------------------------------ attributes

class Attribute(Base):
    """Catálogo canónico de atributos (e.g. is_rock, is_fast_tempo)."""

    __tablename__ = "attributes"

    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class TrackAttribute(Base):
    """Vector sparse: P(atributo | track), 0.0–1.0."""

    __tablename__ = "track_attributes"

    track_id: Mapped[str] = mapped_column(
        ForeignKey("tracks.id", ondelete="CASCADE"), primary_key=True
    )
    attribute_key: Mapped[str] = mapped_column(
        ForeignKey("attributes.key", ondelete="CASCADE"), primary_key=True
    )
    value: Mapped[float] = mapped_column(Float, nullable=False)
    source: Mapped[AttributeSource] = mapped_column(
        Enum(AttributeSource), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    track: Mapped[Track] = relationship(back_populates="attributes")


# ------------------------------------------------------------------ questions

class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    attribute_key: Mapped[str] = mapped_column(
        ForeignKey("attributes.key", ondelete="CASCADE"), nullable=False, index=True
    )
    text_es: Mapped[str] = mapped_column(String(500), nullable=False)
    text_en: Mapped[str | None] = mapped_column(String(500))
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # Telemetría — fase 10
    ask_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    yes_rate: Mapped[float | None] = mapped_column(Float)

    __table_args__ = (
        UniqueConstraint("attribute_key", "text_es", name="uq_question_attr_text"),
    )


# ------------------------------------------------------------------ sessions

class GameSession(Base):
    """Audit de partidas. Estado live vive en Redis, NO aquí."""

    __tablename__ = "game_sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid_str)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    questions_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    result: Mapped[SessionResult | None] = mapped_column(Enum(SessionResult))
    guessed_track_id: Mapped[str | None] = mapped_column(
        ForeignKey("tracks.id", ondelete="SET NULL")
    )
    actual_track_id: Mapped[str | None] = mapped_column(
        ForeignKey("tracks.id", ondelete="SET NULL")
    )


# ------------------------------------------------------------------ suggestions

class SuggestedTrack(Base):
    __tablename__ = "suggested_tracks"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid_str)
    session_id: Mapped[str | None] = mapped_column(
        ForeignKey("game_sessions.id", ondelete="SET NULL")
    )
    title_raw: Mapped[str] = mapped_column(String(500), nullable=False)
    artist_raw: Mapped[str] = mapped_column(String(500), nullable=False)
    spotify_track_id: Mapped[str | None] = mapped_column(String)
    status: Mapped[SuggestionStatus] = mapped_column(
        Enum(SuggestionStatus), default=SuggestionStatus.pending, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


# ------------------------------------------------------------------ votes

class AttributeVote(Base):
    """Crowdsourcing: voto de usuario sobre P(atributo | track)."""

    __tablename__ = "attribute_votes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    track_id: Mapped[str] = mapped_column(
        ForeignKey("tracks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    attribute_key: Mapped[str] = mapped_column(
        ForeignKey("attributes.key", ondelete="CASCADE"), nullable=False, index=True
    )
    value: Mapped[float] = mapped_column(Float, nullable=False)  # 0.0, 0.5, 1.0
    session_id: Mapped[str | None] = mapped_column(
        ForeignKey("game_sessions.id", ondelete="SET NULL")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
