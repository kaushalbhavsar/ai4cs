from pathlib import Path
from typing import Iterable

from openai import OpenAI

from curriculum_tool.config import settings
from curriculum_tool.generation import generate_curriculum_json
from curriculum_tool.io_utils import (
    ensure_directories,
    load_schema,
    load_topics,
    write_json,
    write_text,
)
from curriculum_tool.renderers import (
    pick_first_module,
    render_code_notes,
    render_handout,
    render_slides_outline,
    render_youtube_script,
)
from curriculum_tool.text_utils import slugify
from curriculum_tool.validation import validate_curriculum


def ensure_required_files(paths: Iterable[Path]) -> bool:
    missing = [path for path in paths if not path.exists()]
    for path in missing:
        print(f"Required file not found: {path}")
    return not missing


def process_topic(topic: str, schema: dict, client: OpenAI) -> None:
    slug = slugify(topic)
    topic_dir = settings.output_base / slug

    print(f"\n=== TOPIC: {topic} ({slug}) ===")

    curriculum_json = generate_curriculum_json(topic, settings.model, client)

    try:
        validate_curriculum(curriculum_json, schema)
        print("Schema validation: OK")
    except ValueError as error:
        print("Schema validation FAILED:")
        print(error)
        return

    topic_dir.mkdir(parents=True, exist_ok=True)
    json_path = topic_dir / f"{slug}-curriculum.json"
    write_json(json_path, curriculum_json)

    script_dir = topic_dir / "script"
    slides_dir = topic_dir / "slides"
    handouts_dir = topic_dir / "handouts"
    code_dir = topic_dir / "code"
    ensure_directories([script_dir, slides_dir, handouts_dir, code_dir])

    data = pick_first_module(curriculum_json)

    youtube_text = render_youtube_script(data)
    slides_text = render_slides_outline(data)
    handout_text = render_handout(data)
    code_notes_text = render_code_notes(data)

    write_text(script_dir / f"{slug}-youtube.txt", youtube_text)
    write_text(slides_dir / f"{slug}-slides-outline.md", slides_text)
    write_text(handouts_dir / f"{slug}-handout.md", handout_text)
    write_text(code_dir / f"{slug}-code-notes.md", code_notes_text)

    print(f"Generated files under: {topic_dir}")


def run() -> None:
    topics_path = settings.topics_file
    schema_path = settings.schema_file

    if not ensure_required_files([topics_path, schema_path]):
        return

    schema = load_schema(schema_path)
    settings.output_base.mkdir(parents=True, exist_ok=True)

    topics = load_topics(topics_path)
    if not topics:
        print("No topics found to process.")
        return

    client = OpenAI()

    for topic in topics:
        process_topic(topic, schema, client)


if __name__ == "__main__":
    run()
