from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance

from app.animations import FadeIn, Pulse, SlideRight, SlideUp, Typewriter, ZoomIn
from app.scenes.base import RenderContext, Scene
from app.utils.drawing import add_vignette, draw_multiline_center, fit_cover, font, hex_to_rgb, rounded_panel, wrap_text


def _background(ctx: RenderContext) -> Image.Image:
    return Image.new("RGB", (ctx.width, ctx.height), hex_to_rgb(ctx.theme.background))


def _brand(draw: ImageDraw.ImageDraw, ctx: RenderContext) -> None:
    draw.text((70, ctx.height - 92), ctx.theme.brand, fill=ctx.theme.muted, font=font(34, ctx.theme.font, bold=True))


def _header(draw: ImageDraw.ImageDraw, ctx: RenderContext, title: str, badge: str) -> None:
    draw.text((70, 52), title, fill=ctx.theme.accent, font=font(38, ctx.theme.font, bold=True))
    w = draw.textbbox((0, 0), badge, font=font(30, ctx.theme.font, bold=True))[2]
    rounded_panel(draw, (ctx.width - w - 150, 48, ctx.width - 70, 100), ctx.theme.primary, radius=22)
    draw.text((ctx.width - w - 110, 60), badge, fill=ctx.theme.text, font=font(30, ctx.theme.font, bold=True))


class IntroScene(Scene):
    def __init__(self, question, context: RenderContext, scenario_path: Path):
        super().__init__(question, context)
        self.duration_frames = 3 * context.fps
        self.scenario = Image.open(scenario_path).convert("RGB")
        self.zoom = ZoomIn(duration=self.duration_frames, end_scale=1.10)
        self.fade = FadeIn(duration=context.fps)

    def render(self, frame_number: int) -> Image.Image:
        ctx = self.context
        scale = self.zoom.scale(frame_number)
        base = fit_cover(self.scenario, (round(ctx.width * scale), round(ctx.height * scale)))
        pan = round(40 * (frame_number / max(1, self.duration_frames - 1)))
        left = (base.width - ctx.width) // 2 + pan
        top = (base.height - ctx.height) // 2
        image = base.crop((left, top, left + ctx.width, top + ctx.height))
        image = add_vignette(image, 0.75)
        overlay = Image.new("RGB", image.size, (0, 0, 0))
        image = Image.blend(overlay, image, self.fade.opacity(frame_number) / 255)
        draw = ImageDraw.Draw(image)
        _header(draw, ctx, self.question.category, self.question.difficulty)
        draw_multiline_center(draw, "Cybersecurity Scenario", (180, 720, ctx.width - 180, 900), font(72, ctx.theme.font, True), ctx.theme.text)
        _brand(draw, ctx)
        return image


class QuestionScene(Scene):
    def __init__(self, question, context: RenderContext):
        super().__init__(question, context)
        self.duration_frames = 2 * context.fps
        self.typewriter = Typewriter(duration=self.duration_frames - 8)
        self.fade = FadeIn(duration=12)

    def render(self, frame_number: int) -> Image.Image:
        ctx = self.context
        image = _background(ctx)
        draw = ImageDraw.Draw(image)
        _header(draw, ctx, self.question.category, self.question.difficulty)
        rounded_panel(draw, (170, 255, ctx.width - 170, 790), (14, 34, 54), outline=ctx.theme.primary, radius=42, width=5)
        text = self.typewriter.visible_text(frame_number, self.question.question)
        layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
        ldraw = ImageDraw.Draw(layer)
        draw_multiline_center(ldraw, text, (250, 320, ctx.width - 250, 700), font(76, ctx.theme.font, True), ctx.theme.text)
        layer.putalpha(self.fade.opacity(frame_number))
        image = Image.alpha_composite(image.convert("RGBA"), layer).convert("RGB")
        draw = ImageDraw.Draw(image)
        _brand(draw, ctx)
        return image


class OptionsScene(Scene):
    def __init__(self, question, context: RenderContext):
        super().__init__(question, context)
        self.duration_frames = 2 * context.fps

    def render(self, frame_number: int) -> Image.Image:
        ctx = self.context
        image = _background(ctx).convert("RGBA")
        draw = ImageDraw.Draw(image)
        _header(draw, ctx, "Choose the best answer", self.question.difficulty)
        for index, option in enumerate(self.question.options):
            y = 210 + index * 170
            start = index * 8
            slide = SlideRight(start=start, duration=20, distance=260)
            fade = FadeIn(start=start, duration=18)
            dx, dy = slide.offset(frame_number)
            layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
            ldraw = ImageDraw.Draw(layer)
            rounded_panel(ldraw, (210 + dx, y + dy, ctx.width - 210 + dx, y + 118 + dy), (18, 42, 66, 235), outline=ctx.theme.primary, radius=30, width=3)
            ldraw.text((260 + dx, y + 32 + dy), f"{chr(65 + index)}.", fill=ctx.theme.accent, font=font(44, ctx.theme.font, True))
            for line_i, line in enumerate(wrap_text(option, ldraw, font(42, ctx.theme.font, True), ctx.width - 620)):
                ldraw.text((350 + dx, y + 28 + dy + line_i * 44), line, fill=ctx.theme.text, font=font(42, ctx.theme.font, True))
            layer.putalpha(fade.opacity(frame_number))
            image = Image.alpha_composite(image, layer)
        _brand(ImageDraw.Draw(image), ctx)
        return image.convert("RGB")


class CountdownScene(Scene):
    def __init__(self, question, context: RenderContext):
        super().__init__(question, context)
        self.duration_frames = 5 * context.fps

    def render(self, frame_number: int) -> Image.Image:
        ctx = self.context
        image = _background(ctx)
        draw = ImageDraw.Draw(image)
        _header(draw, ctx, "Time to think", self.question.difficulty)
        progress = frame_number / max(1, self.duration_frames - 1)
        remaining = max(0, math.ceil(5 * (1 - progress)))
        cx, cy, r = ctx.width // 2, ctx.height // 2, 220
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(38, 68, 98), width=28)
        draw.arc((cx - r, cy - r, cx + r, cy + r), -90, -90 + 360 * progress, fill=ctx.theme.accent, width=28)
        text = str(remaining)
        fnt = font(170, ctx.theme.font, True)
        bbox = draw.textbbox((0, 0), text, font=fnt)
        draw.text((cx - (bbox[2] - bbox[0]) / 2, cy - (bbox[3] - bbox[1]) / 2 - 25), text, fill=ctx.theme.text, font=fnt)
        draw_multiline_center(draw, self.question.question, (250, 790, ctx.width - 250, 940), font(44, ctx.theme.font, True), ctx.theme.muted)
        _brand(draw, ctx)
        return image


class RevealScene(OptionsScene):
    def __init__(self, question, context: RenderContext):
        super().__init__(question, context)
        self.duration_frames = 2 * context.fps
        self.pulse = Pulse(duration=self.duration_frames)

    def render(self, frame_number: int) -> Image.Image:
        ctx = self.context
        image = _background(ctx)
        draw = ImageDraw.Draw(image)
        _header(draw, ctx, "Correct answer", self.question.difficulty)
        for index, option in enumerate(self.question.options):
            y = 210 + index * 170
            is_correct = index == self.question.correct_index
            color = ctx.theme.success if is_correct else "#1A2D44"
            text_color = ctx.theme.text if is_correct else ctx.theme.muted
            inset = round(10 * self.pulse.scale(frame_number)) if is_correct else 0
            rounded_panel(draw, (210 - inset, y - inset, ctx.width - 210 + inset, y + 118 + inset), color, outline=ctx.theme.accent if is_correct else ctx.theme.primary, radius=30, width=5 if is_correct else 2)
            draw.text((260, y + 32), f"{chr(65 + index)}.", fill=ctx.theme.accent if not is_correct else "#062B14", font=font(44, ctx.theme.font, True))
            for line_i, line in enumerate(wrap_text(option, draw, font(42, ctx.theme.font, True), ctx.width - 620)):
                draw.text((350, y + 28 + line_i * 44), line, fill=text_color if not is_correct else "#062B14", font=font(42, ctx.theme.font, True))
        _brand(draw, ctx)
        return image


class ExplanationScene(Scene):
    def __init__(self, question, context: RenderContext):
        super().__init__(question, context)
        self.duration_frames = 5 * context.fps
        self.fade = FadeIn(duration=30)
        self.slide = SlideUp(duration=30, distance=100)

    def render(self, frame_number: int) -> Image.Image:
        ctx = self.context
        image = _background(ctx).convert("RGBA")
        draw = ImageDraw.Draw(image)
        _header(draw, ctx, "Why this matters", self.question.difficulty)
        layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
        ldraw = ImageDraw.Draw(layer)
        dx, dy = self.slide.offset(frame_number)
        rounded_panel(ldraw, (170 + dx, 210 + dy, ctx.width - 170 + dx, 840 + dy), (14, 34, 54, 245), outline=ctx.theme.accent, radius=42, width=4)
        ldraw.text((245 + dx, 290 + dy), f"Answer {self.question.correct_answer}: {self.question.correct_option}", fill=ctx.theme.success, font=font(54, ctx.theme.font, True))
        draw_multiline_center(ldraw, self.question.explanation, (245 + dx, 395 + dy, ctx.width - 245 + dx, 760 + dy), font(52, ctx.theme.font, False), ctx.theme.text)
        layer.putalpha(self.fade.opacity(frame_number))
        image = Image.alpha_composite(image, layer)
        _brand(ImageDraw.Draw(image), ctx)
        return image.convert("RGB")
