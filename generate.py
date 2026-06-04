from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from tqdm import tqdm

from app.models.theme import Theme
from app.pipeline import GenerationOptions, QuizVideoGenerator
from app.utils.io import discover_questions, load_question


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate narrated cybersecurity quiz videos from JSON input.")
    parser.add_argument("input", type=Path, help="Question JSON file or directory containing JSON questions")
    parser.add_argument("--thumbnail", action="store_true", help="Generate thumbnail.png only")
    parser.add_argument("--audio", action="store_true", help="Generate narration.mp3 only")
    parser.add_argument("--force", action="store_true", help="Regenerate cached assets and completed renders")
    parser.add_argument("--workers", type=int, default=1, help="Parallel worker count for directory batch generation")
    parser.add_argument("--theme", type=Path, default=Path("config/theme.yaml"), help="Theme YAML/JSON file")
    parser.add_argument("--output", type=Path, default=Path("output"), help="Output root directory")
    parser.add_argument("--cache", type=Path, default=Path("cache"), help="Cache root directory")
    parser.add_argument("--voice", default="alloy", help="OpenAI TTS voice")
    parser.add_argument("--resolution", choices=["landscape", "shorts"], default="landscape", help="Video format: 1920x1080 or 1080x1920")
    return parser.parse_args()


def _generate_one(path: Path, args: argparse.Namespace) -> str:
    theme = Theme.from_file(args.theme)
    question = load_question(path)
    generator = QuizVideoGenerator(args.output, args.cache, theme)
    options = GenerationOptions(
        thumbnail_only=args.thumbnail,
        audio_only=args.audio,
        force=args.force,
        resolution=args.resolution,
        voice=args.voice,
    )
    out = generator.generate(question, options)
    return str(out)


def main() -> None:
    args = parse_args()
    question_paths = discover_questions(args.input)
    if args.workers > 1 and len(question_paths) > 1:
        with ProcessPoolExecutor(max_workers=args.workers) as executor:
            futures = [executor.submit(_generate_one, path, args) for path in question_paths]
            for future in tqdm(as_completed(futures), total=len(futures), desc="Generating"):
                print(future.result())
    else:
        for path in tqdm(question_paths, desc="Generating"):
            print(_generate_one(path, args))


if __name__ == "__main__":
    main()
