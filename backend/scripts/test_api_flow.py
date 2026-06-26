"""End-to-end smoke test of the Oracle HTTP API.

Picks N random target tracks, simulates a player by answering each question
from the target's attribute vector, then verifies the guess.

Run:
    python -m backend.scripts.test_api_flow [--n 10]
"""
from __future__ import annotations

import argparse
import asyncio
import random
import sys

import httpx

from backend.core.attribute_matrix import load_matrix
from backend.main import app

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # noqa: BLE001
    pass


def _vec_to_answer(p: float) -> float:
    """Quantize a ground-truth probability into a 5-button answer."""
    if p >= 0.85:
        return 1.0
    if p >= 0.6:
        return 0.75
    if p > 0.4:
        return 0.5
    if p > 0.15:
        return 0.25
    return 0.0


async def _play(client: httpx.AsyncClient, target_row: int, am) -> tuple[bool, int, str, str]:
    target = am.tracks[target_row]
    r = await client.post("/oracle/session")
    r.raise_for_status()
    s = r.json()
    headers = {"Authorization": f"Bearer {s['token']}"}

    q = s["question"]
    while True:
        attr_idx = q["attr_idx"]
        ans = _vec_to_answer(float(am.matrix[target_row, attr_idx]))
        r = await client.post(
            "/oracle/answer",
            json={"attr_idx": attr_idx, "answer": ans},
            headers=headers,
        )
        r.raise_for_status()
        turn = r.json()
        if turn["state"] == "guess":
            g = turn["guess"]
            ok = g["track"]["track_id"] == target.track_id
            await client.post(
                "/oracle/confirm",
                json={"correct": ok, "actual_track_id": target.track_id},
                headers=headers,
            )
            return ok, g["questions_asked"], target.title, g["track"]["title"]
        q = turn["question"]


async def main(n: int) -> None:
    am = await load_matrix(min_attrs=10)
    print(f"[load] {am.n_tracks} tracks")
    targets = random.sample(range(am.n_tracks), k=min(n, am.n_tracks))

    transport = httpx.ASGITransport(app=app)
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            wins, qs = 0, []
            for row in targets:
                ok, n_q, want, got = await _play(client, row, am)
                wins += int(ok)
                qs.append(n_q)
                mark = "OK " if ok else "MISS"
                print(f"  [{mark}] {n_q:2d}q   want='{want[:35]}'   got='{got[:35]}'")

    avg = sum(qs) / len(qs) if qs else 0
    print(f"\nWins {wins}/{len(targets)}   avg questions {avg:.1f}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, default=10)
    args = p.parse_args()
    asyncio.run(main(args.n))
