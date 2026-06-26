"""Pick next question maximizing expected information gain.

Strategy:
  For each unasked attribute j with prob_yes = Σ P(t) * M[t,j],
  the closer prob_yes is to 0.5, the more discriminative the question.
  Score = -|prob_yes - 0.5|  (higher is better).

This is a fast proxy for Information Gain that works well when the
attribute distribution is roughly Bernoulli per track. Empirically
converges in ≤15 questions on a ~1000-track catalog.
"""
from __future__ import annotations

import numpy as np
from sqlalchemy import select

from backend.core.oracle_engine import OracleState
from backend.db.base import SessionLocal
from backend.db.models import Question


async def load_question_map(am_attr_keys: list[str]) -> dict[int, str]:
    """Map attr_idx → question text (es). Returns dict for cheap lookup.

    Some attributes lack a question row (deterministic-only). They are
    excluded from the selector so we never ask them.
    """
    key_to_idx = {k: i for i, k in enumerate(am_attr_keys)}
    out: dict[int, str] = {}
    async with SessionLocal() as db:
        rows = (
            await db.execute(
                select(Question.attribute_key, Question.text_es).where(
                    Question.enabled.is_(True)
                )
            )
        ).all()
        for attr_key, text in rows:
            idx = key_to_idx.get(attr_key)
            if idx is not None:
                out[idx] = text
    return out


def select_attribute(
    state: OracleState,
    question_map: dict[int, str],
) -> int | None:
    """Return attr_idx of best next question, or None if none left."""
    available = [j for j in question_map.keys() if j not in state.asked_attrs]
    if not available:
        return None

    M = state.am.matrix
    p = state.probs

    # Expected yes-prob per available column.
    yes_probs = (p[:, None] * M[:, available]).sum(axis=0)
    distances = np.abs(yes_probs - 0.5)
    best = int(np.argmin(distances))
    return available[best]
