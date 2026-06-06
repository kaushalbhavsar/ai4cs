from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class CurriculumConfig:
    topics_file: Path = field(default_factory=lambda: Path("topics.txt"))
    schema_file: Path = field(default_factory=lambda: Path("curriculum.schema.json"))
    output_base: Path = field(default_factory=lambda: Path("output"))
    model: str = "gpt-4o-mini"


settings = CurriculumConfig()
