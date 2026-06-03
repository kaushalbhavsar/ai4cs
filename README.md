# Automated Cybersecurity Quiz Video Generator

This repository now includes a Python pipeline for generating narrated cybersecurity quiz videos for **InfoSecQuiz.com** from structured JSON input. It reads quiz data, creates or caches AI scenario images, creates or caches AI narration, renders animated scene timelines, creates thumbnails, and supports unattended batch processing.

## Features

- JSON question loading and validation
- Reusable scene system: intro, question, options, countdown, reveal, and explanation
- Animation primitives: `FadeIn`, `FadeOut`, `SlideLeft`, `SlideRight`, `SlideUp`, `SlideDown`, `ZoomIn`, `ZoomOut`, `Pulse`, `Typewriter`, `Scale`, and `Rotate`
- OpenAI Images API integration with deterministic placeholder fallback when no API key is configured
- OpenAI TTS integration with generated silent fallback audio when no API key is configured
- FFmpeg MP4 rendering at 1920x1080 or 1080x1920 Shorts format
- YouTube-ready thumbnail generation
- Resume support by skipping completed renders unless `--force` is supplied
- Batch generation with optional parallel workers
- Minimal Flask preview UI

## Project Structure

```text
app/
  animations/      Reusable animation primitives
  models/          Question and theme models
  renderers/       Timeline and FFmpeg video renderer
  scenes/          Scene objects that render Pillow frames
  services/        OpenAI image, OpenAI narration, thumbnail services
  utils/           JSON and drawing helpers
config/            Theme configuration
questions/         Input JSON questions
output/            Generated per-question assets and video packages
cache/             Cached images, narration, and metadata
tests/             Unit tests
generate.py        Main CLI
preview.py         Flask preview UI
```

## Requirements

- Python 3.12+
- FFmpeg on `PATH` for MP4 rendering and MP3 fallback generation
- Optional `OPENAI_API_KEY` for AI image and narration generation

Install dependencies:

```bash
pip install -r requirements.txt
```

## Input Format

```json
{
  "id": 1001,
  "category": "Insider Threat",
  "difficulty": "Medium",
  "question": "What is the employee most likely doing?",
  "options": [
    "Stealing confidential data",
    "Working overtime legitimately",
    "Running a system backup",
    "Reporting a security incident"
  ],
  "correct_answer": "A",
  "explanation": "Accessing HR records outside business hours may indicate unauthorized activity."
}
```

## Usage

Generate one complete video package:

```bash
python generate.py questions/1001.json
```

Generate every JSON file in a directory:

```bash
python generate.py questions/
```

Generate thumbnails only:

```bash
python generate.py --thumbnail questions/1001.json
```

Generate audio only:

```bash
python generate.py --audio questions/1001.json
```

Force regeneration of cached assets and completed renders:

```bash
python generate.py --force questions/1001.json
```

Batch process with four workers:

```bash
python generate.py --workers 4 questions/
```

Render Shorts format:

```bash
python generate.py --resolution shorts questions/1001.json
```

## Output

Each question writes to `output/<question_id>/`:

```text
output/1001/
  video.mp4
  thumbnail.png
  narration.mp3
  scenario.png
  metadata.json
  render.log
```

## Preview UI

```bash
python preview.py
```

Open `http://localhost:5000` to browse generated thumbnails and videos.

## OpenAI Configuration

Set your key before generation to use the OpenAI Images and TTS providers:

```bash
export OPENAI_API_KEY=your_key
```

Without a key, the system remains runnable for development and CI by producing deterministic scenario placeholders and silent narration files.
