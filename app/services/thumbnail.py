from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from app.models.question import Question
from app.models.theme import Theme
from app.utils.drawing import draw_multiline_center, fit_cover, font, hex_to_rgb, rounded_panel


class ThumbnailGenerator:
    def __init__(self, theme: Theme | None = None, size: tuple[int, int] = (1280, 720)) -> None:
        self.theme = theme or Theme()
        self.size = size

    def generate(self, question: Question, scenario_path: Path, output_path: Path) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        bg = fit_cover(Image.open(scenario_path), self.size).filter(ImageFilter.GaussianBlur(2))
        overlay = Image.new("RGBA", self.size, (4, 14, 26, 120))
        image = Image.alpha_composite(bg.convert("RGBA"), overlay)
        draw = ImageDraw.Draw(image)
        rounded_panel(draw, (50, 48, 375, 118), self.theme.accent, radius=24)
        draw.text((80, 65), self.theme.brand, fill="#0D1B2A", font=font(30, self.theme.font, True))
        badge_w = 230
        rounded_panel(draw, (self.size[0] - badge_w - 50, 48, self.size[0] - 50, 118), self.theme.primary, radius=24)
        draw_multiline_center(draw, question.difficulty.upper(), (self.size[0] - badge_w - 40, 45, self.size[0] - 60, 120), font(30, self.theme.font, True), self.theme.text)
        rounded_panel(draw, (70, 175, self.size[0] - 70, 620), (10, 28, 48, 225), outline=self.theme.accent, radius=36, width=4)
        draw_multiline_center(draw, question.question, (120, 215, self.size[0] - 120, 540), font(58, self.theme.font, True), self.theme.text)
        draw.text((120, 555), question.category, fill=self.theme.accent, font=font(34, self.theme.font, True))
        image.convert("RGB").save(output_path)
        return output_path
