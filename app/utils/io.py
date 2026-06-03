from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from app.models.question import Question


def load_question(path: Path) -> Question:
    return Question.from_dict(json.loads(path.read_text(encoding="utf-8")))


def discover_questions(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if not path.exists():
        raise FileNotFoundError(path)
    return sorted(p for p in path.glob("*.json") if p.is_file())


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
