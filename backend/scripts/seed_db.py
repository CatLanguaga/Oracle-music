"""Carga atributos y preguntas canónicas en la DB. Idempotente."""
import asyncio

from sqlalchemy import select

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
        existing_qs = {
            (a, t)
            for (a, t) in (
                await db.execute(select(Question.attribute_key, Question.text_es))
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
                )
            )
            new_qs += 1

        await db.commit()
        print(f"[seed] attributes: +{new_attrs} (total {len(ATTRIBUTES)})")
        print(f"[seed] questions:  +{new_qs} (total {len(QUESTIONS)})")


if __name__ == "__main__":
    asyncio.run(seed())
