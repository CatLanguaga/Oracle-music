"""Simulación: para cada track conocido, responde como el modelo lo describe
y verifica que el Oráculo converge en ≤ MAX_QUESTIONS preguntas.

Cada respuesta simulada se discretiza desde M[track, attr]:
    >=0.75 → ANSWER_YES
    >=0.55 → ANSWER_PROBABLY
    >=0.45 → ANSWER_IDK
    >=0.25 → ANSWER_PROBABLY_NOT
    else   → ANSWER_NO
"""
from __future__ import annotations

import asyncio

from backend.core import oracle_engine as oe
from backend.core.attribute_matrix import load_matrix
from backend.core.question_selector import load_question_map, select_attribute


KNOWN_HITS = [
    ("Bohemian Rhapsody", "Queen"),
    ("Despacito", "Luis Fonsi"),
    ("Smells Like Teen Spirit", "Nirvana"),
    ("Bad Guy", "Billie Eilish"),
    ("Hotel California", "Eagles"),
    ("Shape of You", "Ed Sheeran"),
    ("Thriller", "Michael Jackson"),
    ("Wonderwall", "Oasis"),
    ("Rolling in the Deep", "Adele"),
    ("Lose Yourself", "Eminem"),
]


def _discretize(p: float) -> float:
    if p >= 0.75:
        return oe.ANSWER_YES
    if p >= 0.55:
        return oe.ANSWER_PROBABLY
    if p >= 0.45:
        return oe.ANSWER_IDK
    if p >= 0.25:
        return oe.ANSWER_PROBABLY_NOT
    return oe.ANSWER_NO


def _find_row(am, title_sub: str, artist_sub: str) -> int | None:
    title_l = title_sub.lower()
    artist_l = artist_sub.lower()
    for i, t in enumerate(am.tracks):
        if title_l in t.title.lower() and artist_l in t.artist.lower():
            return i
    return None


async def main() -> None:
    am = await load_matrix(min_attrs=10)
    qmap = await load_question_map(am.attr_keys)
    print(f"[load] {am.n_tracks} tracks, {len(qmap)} questions\n")

    results = []
    for title, artist in KNOWN_HITS:
        row = _find_row(am, title, artist)
        if row is None:
            print(f"  SKIP not in catalog: {title} - {artist}")
            results.append((title, None, None, False))
            continue

        true_vec = am.matrix[row]
        state = oe.init_state(am)
        while not oe.should_guess(state):
            attr_idx = select_attribute(state, qmap)
            if attr_idx is None:
                break
            ans = _discretize(float(true_vec[attr_idx]))
            oe.update(state, attr_idx, ans)

        guess_row, guess_prob = oe.top_candidate(state)
        ok = guess_row == row
        g = am.tracks[guess_row]
        marker = "OK" if ok else "MISS"
        print(f"  [{marker}] target={title[:30]:30s} - {artist[:20]:20s}")
        print(f"         guess={g.title[:30]:30s} - {g.artist[:20]:20s} q={state.n_questions} p={guess_prob:.2%}")
        results.append((title, state.n_questions, g.title, ok))

    in_catalog = [r for r in results if r[1] is not None]
    n_ok = sum(1 for r in in_catalog if r[3])
    avg_q = sum(r[1] for r in in_catalog) / max(1, len(in_catalog))
    print(f"\n[summary] {n_ok}/{len(in_catalog)} aciertos, avg preguntas={avg_q:.1f}")


if __name__ == "__main__":
    asyncio.run(main())
