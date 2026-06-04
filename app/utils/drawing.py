from __future__ import annotations

import math
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.strip().lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def font(size: int, preferred: str | None = None, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = []
    if preferred:
        candidates.append(preferred)
    if bold:
        candidates.extend(["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "DejaVuSans-Bold.ttf"])
    candidates.extend(["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "DejaVuSans.ttf"])
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def wrap_text(text: str, draw: ImageDraw.ImageDraw, fnt: ImageFont.ImageFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        test = " ".join([*current, word])
        if draw.textbbox((0, 0), test, font=fnt)[2] <= max_width or not current:
            current.append(word)
        else:
            lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines


def draw_multiline_center(draw: ImageDraw.ImageDraw, text: str, box: tuple[int, int, int, int], fnt: ImageFont.ImageFont, fill: str, spacing: int = 12) -> None:
    x1, y1, x2, y2 = box
    lines = wrap_text(text, draw, fnt, x2 - x1)
    heights = [draw.textbbox((0, 0), line, font=fnt)[3] for line in lines]
    total = sum(heights) + spacing * max(0, len(lines) - 1)
    y = y1 + ((y2 - y1) - total) // 2
    for line, height in zip(lines, heights):
        w = draw.textbbox((0, 0), line, font=fnt)[2]
        draw.text((x1 + ((x2 - x1) - w) // 2, y), line, font=fnt, fill=fill)
        y += height + spacing


def rounded_panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], fill: str | tuple[int, int, int, int], outline: str | None = None, radius: int = 28, width: int = 3) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def fit_cover(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    src = image.convert("RGB")
    sw, sh = src.size
    tw, th = size
    scale = max(tw / sw, th / sh)
    resized = src.resize((math.ceil(sw * scale), math.ceil(sh * scale)), Image.Resampling.LANCZOS)
    left = (resized.width - tw) // 2
    top = (resized.height - th) // 2
    return resized.crop((left, top, left + tw, top + th))


def add_vignette(image: Image.Image, strength: float = 0.65) -> Image.Image:
    width, height = image.size
    mask = Image.new("L", (width, height), 0)
    pixels = mask.load()
    cx, cy = width / 2, height / 2
    max_dist = math.hypot(cx, cy)
    for y in range(height):
        for x in range(width):
            dist = math.hypot(x - cx, y - cy) / max_dist
            pixels[x, y] = int(255 * min(1, dist * strength))
    dark = Image.new("RGB", image.size, (0, 0, 0))
    return Image.composite(dark, image, mask.filter(ImageFilter.GaussianBlur(30)))
