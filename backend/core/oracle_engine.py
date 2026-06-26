"""Bayesian Oracle: maintain P(track | answers so far) and pick next question.

Pipeline per turn:
  1. select_question() → attr_idx (best discriminator given current beliefs)
  2. user answers in {YES=1.0, PROBABLY=0.75, IDK=0.5, PROBABLY_NOT=0.25, NO=0.0}
  3. update(attr_idx, answer) → multiplies track probs by likelihood, normalizes
  4. should_guess() → bool ; if True, top_candidate() returns guess

Math:
  likelihood(t | answer a, attr j) = a * M[t,j] + (1-a) * (1-M[t,j])
  This is symmetric and graceful for fractional answers.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from backend.core.attribute_matrix import AttributeMatrix


# Answer levels — must align with frontend buttons.
ANSWER_YES = 1.0
ANSWER_PROBABLY = 0.75
ANSWER_IDK = 0.5
ANSWER_PROBABLY_NOT = 0.25
ANSWER_NO = 0.0

# Engine tunables
# Pruning combines two rules:
#   1. Relative to uniform (early): drop tracks 100x less likely than uniform.
#   2. Relative to top (after few rounds): drop tracks <0.1% of max prob.
# Likelihood sharpening (beta>1) collapses distribution faster — soft LLM
# attrs (~0.3-0.7) become discriminative; without it engine maxes at 25 Q.
PRUNE_VS_UNIFORM = 0.01
PRUNE_VS_TOP = 1e-3
LIKELIHOOD_BETA = 2.0
GUESS_PROB_THRESHOLD = 0.5
GUESS_DOMINANCE = 0.25       # also guess if top - second > 0.25
GUESS_CANDIDATE_THRESHOLD = 5
MAX_QUESTIONS = 25
EPSILON = 1e-6


@dataclass
class OracleState:
    am: AttributeMatrix
    probs: np.ndarray              # (N_tracks,) posterior over tracks
    asked_attrs: set[int] = field(default_factory=set)
    answers_log: list[tuple[int, float]] = field(default_factory=list)  # (attr_idx, answer)

    @property
    def n_questions(self) -> int:
        return len(self.answers_log)


def init_state(am: AttributeMatrix) -> OracleState:
    n = am.n_tracks
    probs = np.full(n, 1.0 / n, dtype=np.float64)
    return OracleState(am=am, probs=probs)


def update(state: OracleState, attr_idx: int, answer: float) -> None:
    """Apply Bayesian update; normalize; prune below MIN_PROB_PRUNE."""
    a = float(np.clip(answer, 0.0, 1.0))
    col = state.am.matrix[:, attr_idx].astype(np.float64)
    likelihood = a * col + (1.0 - a) * (1.0 - col)
    likelihood = np.clip(likelihood, EPSILON, 1.0)
    # Sharpen — pushes likelihoods away from 0.5 so soft LLM attrs still
    # discriminate. Equivalent to weighting each answer as `beta` answers.
    if LIKELIHOOD_BETA != 1.0:
        likelihood = np.power(likelihood, LIKELIHOOD_BETA)

    state.probs *= likelihood
    total = state.probs.sum()
    if total <= 0:
        # Degenerate — reset uniform to avoid NaN spiral.
        state.probs = np.full_like(state.probs, 1.0 / state.probs.size)
    else:
        state.probs /= total

    # Prune: combine uniform-relative + top-relative thresholds.
    uniform_thr = PRUNE_VS_UNIFORM / state.probs.size
    top_thr = PRUNE_VS_TOP * state.probs.max()
    threshold = max(uniform_thr, top_thr)
    state.probs[state.probs < threshold] = 0.0
    s = state.probs.sum()
    if s > 0:
        state.probs /= s

    state.asked_attrs.add(attr_idx)
    state.answers_log.append((attr_idx, a))


def top_candidate(state: OracleState) -> tuple[int, float]:
    """Return (track_row, prob) of most likely track."""
    idx = int(state.probs.argmax())
    return idx, float(state.probs[idx])


def top_k(state: OracleState, k: int = 5) -> list[tuple[int, float]]:
    idxs = np.argsort(state.probs)[::-1][:k]
    return [(int(i), float(state.probs[i])) for i in idxs]


def n_candidates(state: OracleState) -> int:
    """Tracks with non-zero prob."""
    return int((state.probs > 0).sum())


def should_guess(state: OracleState) -> bool:
    top = top_k(state, 2)
    p1 = top[0][1] if top else 0.0
    p2 = top[1][1] if len(top) > 1 else 0.0
    if p1 >= GUESS_PROB_THRESHOLD:
        return True
    # Top clearly dominates runner-up — likely duplicates/remasters share
    # rest of mass.
    if p1 - p2 >= GUESS_DOMINANCE and state.n_questions >= 8:
        return True
    if n_candidates(state) <= GUESS_CANDIDATE_THRESHOLD:
        return True
    if state.n_questions >= MAX_QUESTIONS:
        return True
    return False
