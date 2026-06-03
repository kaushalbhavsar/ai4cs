from __future__ import annotations

import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from app.models.question import Question
from app.models.theme import Theme
from app.scenes import CountdownScene, ExplanationScene, IntroScene, OptionsScene, QuestionScene, RenderContext, RevealScene, Scene
from app.utils.io import write_json


class Timeline:
    def __init__(self, scenes: list[Scene]) -> None:
        self.scenes = scenes
        self.duration_frames = sum(scene.duration_frames for scene in scenes)

    def render_frame(self, frame_number: int):
        offset = 0
        for scene in self.scenes:
            if frame_number < offset + scene.duration_frames:
                return scene.render(frame_number - offset)
            offset += scene.duration_frames
        return self.scenes[-1].render(self.scenes[-1].duration_frames - 1)


class VideoRenderer:
    def __init__(self, theme: Theme | None = None, fps: int = 30, resolution: str = "landscape") -> None:
        self.theme = theme or Theme()
        self.fps = fps
        if resolution == "shorts":
            self.width, self.height = 1080, 1920
        else:
            self.width, self.height = 1920, 1080

    def build_timeline(self, question: Question, scenario_path: Path) -> Timeline:
        context = RenderContext(width=self.width, height=self.height, fps=self.fps, theme=self.theme)
        return Timeline([
            IntroScene(question, context, scenario_path),
            QuestionScene(question, context),
            OptionsScene(question, context),
            CountdownScene(question, context),
            RevealScene(question, context),
            ExplanationScene(question, context),
        ])

    def render(self, question: Question, scenario_path: Path, narration_path: Path, output_path: Path, force: bool = False) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if output_path.exists() and not force:
            return output_path
        if shutil.which("ffmpeg") is None:
            raise RuntimeError("ffmpeg is required to render MP4 videos")
        timeline = self.build_timeline(question, scenario_path)
        with tempfile.TemporaryDirectory(prefix=f"quiz_{question.id}_frames_") as frame_dir:
            frame_root = Path(frame_dir)
            for frame in range(timeline.duration_frames):
                timeline.render_frame(frame).save(frame_root / f"frame_{frame:06d}.png", optimize=False)
            cmd = [
                "ffmpeg",
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                "-framerate",
                str(self.fps),
                "-i",
                str(frame_root / "frame_%06d.png"),
                "-i",
                str(narration_path),
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                "-shortest",
                str(output_path),
            ]
            subprocess.run(cmd, check=True)
        return output_path

    def write_metadata(self, question: Question, output_dir: Path, voice: str, duration_seconds: int = 19) -> Path:
        metadata = {
            "question_id": question.id,
            "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "voice": voice,
            "duration_seconds": duration_seconds,
            "video_file": "video.mp4",
            "thumbnail_file": "thumbnail.png",
            "narration_file": "narration.mp3",
            "scenario_file": "scenario.png",
        }
        path = output_dir / "metadata.json"
        write_json(path, metadata)
        return path
