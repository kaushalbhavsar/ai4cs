from __future__ import annotations

import math
from dataclasses import dataclass


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def ease_out_cubic(t: float) -> float:
    t = clamp(t)
    return 1 - pow(1 - t, 3)


def ease_in_out(t: float) -> float:
    t = clamp(t)
    return 0.5 - 0.5 * math.cos(math.pi * t)


@dataclass(frozen=True)
class Animation:
    start: int = 0
    duration: int = 1

    def progress(self, frame: int) -> float:
        return clamp((frame - self.start) / max(1, self.duration))


class FadeIn(Animation):
    def opacity(self, frame: int) -> int:
        return round(255 * ease_out_cubic(self.progress(frame)))


class FadeOut(Animation):
    def opacity(self, frame: int) -> int:
        return round(255 * (1 - ease_out_cubic(self.progress(frame))))


@dataclass(frozen=True)
class Slide(Animation):
    distance: int = 120

    def offset(self, frame: int) -> tuple[int, int]:
        raise NotImplementedError


class SlideLeft(Slide):
    def offset(self, frame: int) -> tuple[int, int]:
        return (round(self.distance * (1 - ease_out_cubic(self.progress(frame)))), 0)


class SlideRight(Slide):
    def offset(self, frame: int) -> tuple[int, int]:
        return (-round(self.distance * (1 - ease_out_cubic(self.progress(frame)))), 0)


class SlideUp(Slide):
    def offset(self, frame: int) -> tuple[int, int]:
        return (0, round(self.distance * (1 - ease_out_cubic(self.progress(frame)))))


class SlideDown(Slide):
    def offset(self, frame: int) -> tuple[int, int]:
        return (0, -round(self.distance * (1 - ease_out_cubic(self.progress(frame)))))


@dataclass(frozen=True)
class ZoomIn(Animation):
    start_scale: float = 1.0
    end_scale: float = 1.12

    def scale(self, frame: int) -> float:
        return self.start_scale + (self.end_scale - self.start_scale) * ease_in_out(self.progress(frame))


@dataclass(frozen=True)
class ZoomOut(Animation):
    start_scale: float = 1.12
    end_scale: float = 1.0

    def scale(self, frame: int) -> float:
        return self.start_scale + (self.end_scale - self.start_scale) * ease_in_out(self.progress(frame))


@dataclass(frozen=True)
class Pulse(Animation):
    amplitude: float = 0.06
    cycles: float = 2.0

    def scale(self, frame: int) -> float:
        return 1 + self.amplitude * math.sin(2 * math.pi * self.cycles * self.progress(frame))


class Typewriter(Animation):
    def visible_text(self, frame: int, text: str) -> str:
        length = round(len(text) * ease_out_cubic(self.progress(frame)))
        return text[:length]


@dataclass(frozen=True)
class Scale(Animation):
    start_scale: float = 0.85
    end_scale: float = 1.0

    def scale(self, frame: int) -> float:
        return self.start_scale + (self.end_scale - self.start_scale) * ease_out_cubic(self.progress(frame))


@dataclass(frozen=True)
class Rotate(Animation):
    start_degrees: float = 0
    end_degrees: float = 360

    def degrees(self, frame: int) -> float:
        return self.start_degrees + (self.end_degrees - self.start_degrees) * self.progress(frame)
