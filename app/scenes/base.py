from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from PIL import Image

from app.models.question import Question
from app.models.theme import Theme


@dataclass
class RenderContext:
    width: int = 1920
    height: int = 1080
    fps: int = 30
    theme: Theme = Theme()


class Scene(ABC):
    duration_frames: int

    def __init__(self, question: Question, context: RenderContext) -> None:
        self.question = question
        self.context = context

    @abstractmethod
    def render(self, frame_number: int) -> Image.Image:
        pass
