from __future__ import annotations

import json
from pathlib import Path

from app.animations import FadeIn, SlideRight, Typewriter, ZoomIn
from app.models.question import Question
from app.models.theme import Theme
from app.pipeline import GenerationOptions, QuizVideoGenerator
from app.renderers.video import VideoRenderer
from app.services.image_generation import ImageGenerationService
from app.services.thumbnail import ThumbnailGenerator


def sample_question() -> Question:
    return Question.from_dict(
        {
            "id": 42,
            "category": "Phishing",
            "difficulty": "Easy",
            "question": "Which clue best indicates this email is phishing?",
            "options": ["Urgent password request", "Company logo", "Normal signature", "Short subject"],
            "correct_answer": "A",
            "explanation": "Urgent credential requests are a common phishing signal.",
        }
    )


def test_question_validation_and_properties() -> None:
    question = sample_question()
    assert question.correct_index == 0
    assert question.correct_option == "Urgent password request"
    assert question.output_dir(Path("output")) == Path("output/42")


def test_animation_primitives_progress() -> None:
    assert FadeIn(duration=10).opacity(10) == 255
    assert SlideRight(duration=10, distance=100).offset(0) == (-100, 0)
    assert SlideRight(duration=10, distance=100).offset(10) == (0, 0)
    assert Typewriter(duration=10).visible_text(5, "abcdef") in {"abc", "abcd", "abcde"}
    assert ZoomIn(duration=10, start_scale=1.0, end_scale=2.0).scale(10) == 2.0


def test_image_and_thumbnail_generation_without_openai_key(tmp_path, monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    question = sample_question()
    theme = Theme()
    scenario = ImageGenerationService(tmp_path / "cache", theme=theme).generate(question, tmp_path / "scenario.png")
    thumb = ThumbnailGenerator(theme).generate(question, scenario, tmp_path / "thumbnail.png")
    assert scenario.exists()
    assert thumb.exists()


def test_timeline_duration() -> None:
    question = sample_question()
    renderer = VideoRenderer(theme=Theme(), fps=30)
    # Scenario image is supplied by the deterministic fallback generator.
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        path = ImageGenerationService(Path(td) / "cache").generate(question, Path(td) / "scenario.png")
        timeline = renderer.build_timeline(question, path)
    assert timeline.duration_frames == 19 * 30


def test_audio_only_pipeline_outputs_expected_files(tmp_path, monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    question = sample_question()
    generator = QuizVideoGenerator(output_root=tmp_path / "output", cache_root=tmp_path / "cache", theme=Theme())
    out = generator.generate(question, GenerationOptions(audio_only=True))
    assert (out / "scenario.png").exists()
    assert (out / "narration.mp3").exists()
    assert (out / "render.log").read_text() == "Generated audio only.\n"
