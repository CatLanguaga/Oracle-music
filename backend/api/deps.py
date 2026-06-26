"""FastAPI dependencies wired against app.state."""
from __future__ import annotations

from fastapi import Request

from backend.core.attribute_matrix import AttributeMatrix
from backend.core.session_manager import SessionStore


def get_matrix(request: Request) -> AttributeMatrix:
    return request.app.state.matrix


def get_qmap(request: Request) -> dict[int, str]:
    return request.app.state.qmap


def get_store(request: Request) -> SessionStore:
    return request.app.state.session_store
