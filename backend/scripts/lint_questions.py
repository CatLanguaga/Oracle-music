"""Lint del catálogo de preguntas (`backend/seeds/questions.md`).

Reglas:
- Sin duplicados (attribute_key, text).
- Texto termina en '?'.
- Toda key existe en `seeds.attributes.ATTRIBUTES`.
- Advertencias de ambigüedad para status='active': ' o ', '/', 'uno de'.

Exit code 1 si hay errores, 0 si sólo warnings o todo OK.
"""
from __future__ import annotations

import sys
from collections import Counter

from backend.seeds.attributes import ATTRIBUTES
from backend.seeds.questions import QUESTIONS

AMBIGUOUS_TOKENS = (" o ", "/", "uno de ", "alguno de ")


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    attr_keys = {k for k, *_ in ATTRIBUTES}

    # Duplicados (key,text)
    pair_counts = Counter((k, t) for k, t, _ in QUESTIONS)
    for (k, t), n in pair_counts.items():
        if n > 1:
            errors.append(f"duplicate (key={k!r}, text={t!r}) x{n}")

    for key, text, category in QUESTIONS:
        if key not in attr_keys:
            errors.append(f"key {key!r} not in ATTRIBUTES (category={category})")
        if not text.rstrip().endswith("?"):
            errors.append(f"text not ending in '?': {key} → {text!r}")
        for tok in AMBIGUOUS_TOKENS:
            if tok in text.lower():
                warnings.append(
                    f"ambiguous token {tok!r} in {key}: {text!r}"
                )

    for line in warnings:
        print(f"WARN  {line}")
    for line in errors:
        print(f"ERROR {line}")
    print(
        f"\nsummary: {len(QUESTIONS)} questions · "
        f"{len(errors)} errors · {len(warnings)} warnings"
    )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
