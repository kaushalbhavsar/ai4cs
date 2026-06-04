from __future__ import annotations

import os
import subprocess
import wave
from datetime import datetime, timezone
from pathlib import Path

from app.models.question import Question
from app.utils.io import write_json


class NarrationService:
    def __init__(self, cache_dir: Path = Path("cache/audio"), model: str = "gpt-4o-mini-tts", voice: str = "alloy") -> None:
        self.cache_dir = cache_dir
        self.model = model
        self.voice = voice
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def script(self, question: Question) -> str:
        return (
            f"{question.question}\n\n"
            "Take a moment to choose the best answer.\n\n"
            f"The correct answer is {question.correct_answer}: {question.correct_option}.\n\n"
            f"{question.explanation}"
        )

    def generate(self, question: Question, output_path: Path, force: bool = False) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cached = self.cache_dir / f"{question.cache_key}_{self.voice}.mp3"
        if cached.exists() and not force:
            output_path.write_bytes(cached.read_bytes())
            return output_path
        if os.getenv("OPENAI_API_KEY"):
            try:
                self._generate_openai(question, cached)
            except Exception:
                self._generate_silence(cached, seconds=19)
        else:
            self._generate_silence(cached, seconds=19)
        output_path.write_bytes(cached.read_bytes())
        return output_path

    def _generate_openai(self, question: Question, path: Path) -> None:
        from openai import OpenAI

        client = OpenAI()
        with client.audio.speech.with_streaming_response.create(
            model=self.model,
            voice=self.voice,
            input=self.script(question),
            response_format="mp3",
        ) as response:
            response.stream_to_file(path)
        write_json(path.with_suffix(".json"), {"question_id": question.id, "model": self.model, "voice": self.voice, "script": self.script(question), "generated_at": datetime.now(timezone.utc).isoformat()})

    def _generate_silence(self, path: Path, seconds: int) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        wav_path = path.with_suffix(".wav")
        sample_rate = 44100
        with wave.open(str(wav_path), "w") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            wav.writeframes(b"\x00\x00" * sample_rate * seconds)
        try:
            subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(wav_path), str(path)], check=True)
            wav_path.unlink(missing_ok=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            wav_path.replace(path)
        write_json(path.with_suffix(".json"), {"fallback": True, "voice": self.voice, "duration_seconds": seconds, "generated_at": datetime.now(timezone.utc).isoformat()})
