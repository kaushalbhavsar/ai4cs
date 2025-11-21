import json
from pathlib import Path
from typing import Iterable, List


def load_schema(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_topics(path: Path) -> List[str]:
    if not path.exists():
        return []

    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def ensure_directories(directories: Iterable[Path]) -> None:
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
