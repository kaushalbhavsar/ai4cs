from __future__ import annotations

import base64
import os
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from app.models.question import Question
from app.models.theme import Theme
from app.utils.drawing import draw_multiline_center, font, hex_to_rgb
from app.utils.io import write_json


class ImageGenerationService:
    def __init__(self, cache_dir: Path = Path("cache/images"), model: str = "gpt-image-1", size: str = "1536x1024", theme: Theme | None = None) -> None:
        self.cache_dir = cache_dir
        self.model = model
        self.size = size
        self.theme = theme or Theme()
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, question: Question, output_path: Path, force: bool = False) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cached = self.cache_dir / f"{question.cache_key}.png"
        if cached.exists() and not force:
            output_path.write_bytes(cached.read_bytes())
            return output_path
        if os.getenv("OPENAI_API_KEY"):
            try:
                self._generate_openai(question, cached)
            except Exception as exc:  # keep batch renders unattended when API is unavailable
                self._generate_placeholder(question, cached, f"OpenAI image fallback: {exc}")
        else:
            self._generate_placeholder(question, cached, "OPENAI_API_KEY not set; generated deterministic placeholder")
        output_path.write_bytes(cached.read_bytes())
        return output_path

    def _prompt(self, question: Question) -> str:
        return (
            "Create a cinematic, realistic cybersecurity training scenario image. "
            "No readable text, no logos, no gore. "
            f"Category: {question.category}. Difficulty: {question.difficulty}. "
            f"Quiz question: {question.question}. Correct scenario cue: {question.correct_option}. "
            "Composition should leave subtle negative space for quiz overlays, blue security operations center color palette."
        )

    def _generate_openai(self, question: Question, path: Path) -> None:
        from openai import OpenAI

        client = OpenAI()
        result = client.images.generate(model=self.model, prompt=self._prompt(question), size=self.size)
        data = result.data[0]
        if getattr(data, "b64_json", None):
            path.write_bytes(base64.b64decode(data.b64_json))
        elif getattr(data, "url", None):
            import requests

            response = requests.get(data.url, timeout=60)
            response.raise_for_status()
            path.write_bytes(response.content)
        else:
            raise RuntimeError("OpenAI image response did not include image data")
        write_json(path.with_suffix(".json"), {"question_id": question.id, "model": self.model, "prompt": self._prompt(question), "generated_at": datetime.now(timezone.utc).isoformat()})

    def _generate_placeholder(self, question: Question, path: Path, reason: str) -> None:
        width, height = 1536, 1024
        bg = Image.new("RGB", (width, height), hex_to_rgb(self.theme.background))
        draw = ImageDraw.Draw(bg)
        for i in range(0, width, 24):
            color = (18, 49 + (i % 80), 82)
            draw.line((i, 0, i - 420, height), fill=color, width=2)
        draw.rounded_rectangle((130, 150, width - 130, height - 150), radius=48, fill=(12, 29, 46), outline=hex_to_rgb(self.theme.primary), width=8)
        draw.text((190, 210), "Cybersecurity Scenario", fill=hex_to_rgb(self.theme.accent), font=font(70, self.theme.font, True))
        draw_multiline_center(draw, question.category, (190, 330, width - 190, 470), font(82, self.theme.font, True), self.theme.text)
        draw_multiline_center(draw, question.question, (220, 540, width - 220, 780), font(50, self.theme.font, False), self.theme.muted)
        draw.text((190, 815), f"Difficulty: {question.difficulty}", fill=hex_to_rgb(self.theme.primary), font=font(42, self.theme.font, True))
        bg = bg.filter(ImageFilter.UnsharpMask(radius=2, percent=110))
        path.parent.mkdir(parents=True, exist_ok=True)
        bg.save(path)
        write_json(path.with_suffix(".json"), {"question_id": question.id, "fallback": True, "reason": reason, "generated_at": datetime.now(timezone.utc).isoformat()})
