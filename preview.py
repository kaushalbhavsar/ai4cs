from __future__ import annotations

from pathlib import Path

from flask import Flask, abort, send_file

app = Flask(__name__)
OUTPUT_ROOT = Path("output")


@app.get("/")
def index() -> str:
    items = sorted(p for p in OUTPUT_ROOT.glob("*/thumbnail.png"))
    cards = "".join(
        f'<article><a href="/{path.parent.name}/video"><img src="/{path.parent.name}/thumbnail"/></a><h2>Question {path.parent.name}</h2></article>'
        for path in items
    )
    return f"""
    <!doctype html><title>Quiz Video Preview</title>
    <style>body{{background:#0D1B2A;color:white;font-family:sans-serif;padding:32px}}main{{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:24px}}img{{width:100%;border-radius:16px}}</style>
    <h1>InfoSecQuiz Video Preview</h1><main>{cards}</main>
    """


@app.get("/<question_id>/thumbnail")
def thumbnail(question_id: str):
    path = OUTPUT_ROOT / question_id / "thumbnail.png"
    if not path.exists():
        abort(404)
    return send_file(path)


@app.get("/<question_id>/video")
def video(question_id: str):
    path = OUTPUT_ROOT / question_id / "video.mp4"
    if not path.exists():
        abort(404)
    return send_file(path)


if __name__ == "__main__":
    app.run(debug=True)
