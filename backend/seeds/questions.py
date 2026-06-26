"""Loader de preguntas. Fuente verdad: ``questions.md``.

Mantiene contrato anterior: ``QUESTIONS: list[tuple[key, text, category]]``.
Sólo emite filas con ``status in {'active', 'rephrasing'}``.
"""
from pathlib import Path
import re

_MD_PATH = Path(__file__).parent / "questions.md"
_ACTIVE_STATUSES = {"active", "rephrasing"}


def _split_row(line: str) -> list[str]:
    body = line.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|"):
        body = body[:-1]
    # Permitir pipes escapados \|
    cells = re.split(r"(?<!\\)\|", body)
    return [c.replace(r"\|", "|").strip() for c in cells]


def _is_separator(cells: list[str]) -> bool:
    return all(c == "" or set(c) <= {"-", ":"} for c in cells)


def _parse() -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    current_cat: str | None = None
    for line in _MD_PATH.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^##\s+([\w\-]+)\s*$", line)
        if m:
            current_cat = m.group(1).strip()
            continue
        if not current_cat or not line.lstrip().startswith("|"):
            continue
        cells = _split_row(line)
        if len(cells) < 3:
            continue
        if cells[0] == "key" or _is_separator(cells):
            continue
        key, text, status = cells[0], cells[1], cells[2]
        if not key or status not in _ACTIVE_STATUSES:
            continue
        rows.append((key, text, current_cat))
    return rows


QUESTIONS: list[tuple[str, str, str]] = _parse()
