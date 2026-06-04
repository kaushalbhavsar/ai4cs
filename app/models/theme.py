from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class Theme:
    background: str = "#0D1B2A"
    primary: str = "#3A86FF"
    accent: str = "#FFBE0B"
    success: str = "#2ECC71"
    danger: str = "#FF5C5C"
    text: str = "#F8FAFC"
    muted: str = "#9FB3C8"
    font: str = "DejaVuSans"
    logo: str | None = None
    brand: str = "InfoSecQuiz.com"

    @classmethod
    def from_mapping(cls, mapping: dict[str, Any]) -> "Theme":
        data = mapping.get("theme", mapping)
        allowed = {field for field in cls.__dataclass_fields__}
        return cls(**{key: value for key, value in data.items() if key in allowed})

    @classmethod
    def from_file(cls, path: Path) -> "Theme":
        if not path.exists():
            return cls()
        if path.suffix.lower() in {".yaml", ".yml"}:
            return cls.from_mapping(yaml.safe_load(path.read_text()) or {})
        import json

        return cls.from_mapping(json.loads(path.read_text()))
