"""REPL para probar el Oracle desde consola.

Usage:
    python -m backend.scripts.play_console [--min-attrs 10]

Inputs durante el juego:
    1 = Sí
    2 = Probablemente sí
    3 = No sé
    4 = Probablemente no
    5 = No
    q = rendirse
"""
from __future__ import annotations

import argparse
import asyncio
import sys

from backend.core import oracle_engine as oe
from backend.core.attribute_matrix import load_matrix
from backend.core.question_selector import load_question_map, select_attribute

# Windows console encoding
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # noqa: BLE001
    pass


ANSWER_MAP = {
    "1": oe.ANSWER_YES,
    "2": oe.ANSWER_PROBABLY,
    "3": oe.ANSWER_IDK,
    "4": oe.ANSWER_PROBABLY_NOT,
    "5": oe.ANSWER_NO,
}


def _print_topk(state: oe.OracleState, k: int = 5) -> None:
    print("  top candidates:")
    for row, prob in oe.top_k(state, k):
        t = state.am.tracks[row]
        print(f"    {prob:6.2%}  {t.title[:45]:45s} - {t.artist[:30]:30s} ({t.release_year})")


async def main(min_attrs: int) -> None:
    print(f"[load] matriz min_attrs={min_attrs}")
    am = await load_matrix(min_attrs=min_attrs)
    print(f"[load] {am.n_tracks} tracks x {am.n_attrs} attrs")
    qmap = await load_question_map(am.attr_keys)
    print(f"[load] {len(qmap)} preguntas disponibles\n")

    print("Piensa una canción del catálogo. Responde:")
    print("  1=Sí  2=Probablemente  3=No sé  4=Probablemente no  5=No  q=rendirse\n")

    state = oe.init_state(am)

    while not oe.should_guess(state):
        attr_idx = select_attribute(state, qmap)
        if attr_idx is None:
            print("[stop] sin preguntas restantes")
            break
        q_text = qmap[attr_idx]
        print(f"[Q{state.n_questions + 1}] {q_text}  (candidatos={oe.n_candidates(state)})")
        ans = input("> ").strip().lower()
        if ans == "q":
            print("Rendido.")
            break
        if ans not in ANSWER_MAP:
            print("respuesta inválida, usa 1-5 o q")
            continue
        oe.update(state, attr_idx, ANSWER_MAP[ans])

    row, prob = oe.top_candidate(state)
    t = am.tracks[row]
    print(f"\n[GUESS] tras {state.n_questions} preguntas (prob={prob:.2%}):")
    print(f"  → {t.title} — {t.artist} ({t.release_year})")
    _print_topk(state, 5)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--min-attrs", type=int, default=10)
    args = p.parse_args()
    asyncio.run(main(args.min_attrs))
