"""JWT session token.

Token payload: {"sid": str, "iat": int, "exp": int}. The session_id is the
authoritative key; signing prevents clients from forging or peeking at
another player's session.
"""
from __future__ import annotations

import time
import uuid

from fastapi import Header, HTTPException, status
from jose import JWTError, jwt

from backend.config import get_settings


def new_session_id() -> str:
    return str(uuid.uuid4())


def issue_token(session_id: str) -> str:
    settings = get_settings()
    now = int(time.time())
    payload = {
        "sid": session_id,
        "iat": now,
        "exp": now + settings.session_ttl_minutes * 60,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> str:
    settings = get_settings()
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"invalid token: {e}",
        ) from e
    sid = payload.get("sid")
    if not isinstance(sid, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="malformed token"
        )
    return sid


async def session_id_from_header(
    authorization: str = Header(..., alias="Authorization"),
) -> str:
    """FastAPI dep: extract session_id from `Authorization: Bearer <jwt>`."""
    if not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing Bearer token",
        )
    return decode_token(authorization.split(" ", 1)[1].strip())
