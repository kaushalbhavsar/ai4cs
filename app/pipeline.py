from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.models.question import Question
from app.models.theme import Theme
from app.renderers.video import VideoRenderer
from app.services import ImageGenerationService, NarrationService, ThumbnailGenerator


@dataclass
class GenerationOptions:
    thumbnail_only: bool = False
    audio_only: bool = False
    force: bool = False
    skip_completed: bool = True
    resolution: str = "landscape"
    voice: str = "alloy"


class QuizVideoGenerator:
    def __init__(self, output_root: Path = Path("output"), cache_root: Path = Path("cache"), theme: Theme | None = None) -> None:
        self.output_root = output_root
        self.cache_root = cache_root
        self.theme = theme or Theme()

    def generate(self, question: Question, options: GenerationOptions) -> Path:
        output_dir = question.output_dir(self.output_root)
        output_dir.mkdir(parents=True, exist_ok=True)
        log_path = output_dir / "render.log"
        video_path = output_dir / "video.mp4"
        if options.skip_completed and not options.force and not options.thumbnail_only and not options.audio_only and video_path.exists() and (output_dir / "metadata.json").exists():
            log_path.write_text("Skipped completed render.\n", encoding="utf-8")
            return output_dir

        image_service = ImageGenerationService(self.cache_root / "images", theme=self.theme)
        narration_service = NarrationService(self.cache_root / "audio", voice=options.voice)
        thumbnailer = ThumbnailGenerator(self.theme)
        scenario_path = image_service.generate(question, output_dir / "scenario.png", force=options.force)

        if options.thumbnail_only:
            thumbnailer.generate(question, scenario_path, output_dir / "thumbnail.png")
            log_path.write_text("Generated thumbnail only.\n", encoding="utf-8")
            return output_dir

        narration_path = narration_service.generate(question, output_dir / "narration.mp3", force=options.force)
        if options.audio_only:
            log_path.write_text("Generated audio only.\n", encoding="utf-8")
            return output_dir

        thumbnailer.generate(question, scenario_path, output_dir / "thumbnail.png")
        renderer = VideoRenderer(theme=self.theme, resolution=options.resolution)
        renderer.render(question, scenario_path, narration_path, video_path, force=options.force)
        renderer.write_metadata(question, output_dir, options.voice)
        log_path.write_text("Generated complete video package.\n", encoding="utf-8")
        return output_dir
