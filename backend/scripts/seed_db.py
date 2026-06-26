"""Carga atributos y preguntas canónicas en la DB. Idempotente.

`questions.md` es la fuente de verdad. Filas no presentes en él se marcan
`enabled=False` (no se borran para preservar histórico).
"""
import asyncio

from sqlalchemy import select, update

from backend.db.base import SessionLocal
from backend.db.models import Attribute, Question
from backend.seeds.attributes import ATTRIBUTES
from backend.seeds.questions import QUESTIONS


async def seed() -> None:
    async with SessionLocal() as db:
        # ---- attributes ----
        existing_attrs = {
            k for (k,) in (await db.execute(select(Attribute.key))).all()
        }
        new_attrs = 0
        for key, category, description in ATTRIBUTES:
            if key in existing_attrs:
                continue
            db.add(Attribute(key=key, category=category, description=description))
            new_attrs += 1

        # ---- questions ----
        active_pairs = {(a, t) for a, t, _ in QUESTIONS}
        existing_qs: dict[tuple[str, str], tuple[int, bool]] = {
            (a, t): (qid, enabled)
            for (qid, a, t, enabled) in (
                await db.execute(
                    select(Question.id, Question.attribute_key, Question.text_es, Question.enabled)
                )
            ).all()
        }

        new_qs = 0
        for attribute_key, text_es, category in QUESTIONS:
            if (attribute_key, text_es) in existing_qs:
                continue
            db.add(
                Question(
                    attribute_key=attribute_key,
                    text_es=text_es,
                    category=category,
                    enabled=True,
                )
            )
            new_qs += 1

        # Reactivar filas que vuelven a estar activas
        reactivated = 0
        for (a, t), (qid, enabled) in existing_qs.items():
            if (a, t) in active_pairs and not enabled:
                await db.execute(
                    update(Question).where(Question.id == qid).values(enabled=True)
                )
                reactivated += 1

        # Deshabilitar filas que ya no están en el md
        disabled = 0
        for (a, t), (qid, enabled) in existing_qs.items():
            if (a, t) not in active_pairs and enabled:
                await db.execute(
                    update(Question).where(Question.id == qid).values(enabled=False)
                )
                disabled += 1

        await db.commit()
        print(f"[seed] attributes: +{new_attrs} (total {len(ATTRIBUTES)})")
        print(
            f"[seed] questions:  +{new_qs} new · "
            f"+{reactivated} reactivated · -{disabled} disabled "
            f"(active in md: {len(QUESTIONS)})"
        )


if __name__ == "__main__":
    asyncio.run(seed())
