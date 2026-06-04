from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Question:
    id: int
    category: str
    difficulty: str
    question: str
    options: list[str]
    correct_answer: str
    explanation: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Question":
        required = ["id", "category", "difficulty", "question", "options", "correct_answer", "explanation"]
        missing = [key for key in required if key not in data]
        if missing:
            raise ValueError(f"Missing required question fields: {', '.join(missing)}")
        options = list(data["options"])
        if len(options) != 4:
            raise ValueError("Question must contain exactly four options")
        answer = str(data["correct_answer"]).strip().upper()
        if answer not in {"A", "B", "C", "D"}:
            raise ValueError("correct_answer must be one of A, B, C, or D")
        return cls(
            id=int(data["id"]),
            category=str(data["category"]),
            difficulty=str(data["difficulty"]),
            question=str(data["question"]),
            options=options,
            correct_answer=answer,
            explanation=str(data["explanation"]),
        )

    @property
    def correct_index(self) -> int:
        return ord(self.correct_answer) - ord("A")

    @property
    def correct_option(self) -> str:
        return self.options[self.correct_index]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "category": self.category,
            "difficulty": self.difficulty,
            "question": self.question,
            "options": self.options,
            "correct_answer": self.correct_answer,
            "explanation": self.explanation,
        }

    @property
    def cache_key(self) -> str:
        return str(self.id)

    def output_dir(self, root: Path) -> Path:
        return root / str(self.id)
