import os
from flask import Flask, request, jsonify, render_template, session
import openai

from .pdf_processor import PdfVectorIndex

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PDF_DIR = os.getenv("PDF_DIR", "pdfs")
INDEX_PATH = os.getenv("INDEX_PATH", "index.faiss")
CHUNKS_PATH = os.getenv("CHUNKS_PATH", "chunks.json")

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "please-change-me")
vector_index = PdfVectorIndex(OPENAI_API_KEY, INDEX_PATH, CHUNKS_PATH)
vector_index.build_index(PDF_DIR)

def generate_answer(question: str) -> str:
    contexts = vector_index.query(question)
    prompt = (
        "Answer the user's question using only the following information. "
        "If the answer isn't present, reply that you do not have that information "
        "without referencing the word 'context'. "
        "When mentioning the organization, refer to it as 'we' instead of using its name.\n\n"
    ) + "\n\n".join(contexts) + f"\n\nQuestion: {question}\nAnswer:"
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return response.choices[0].message.content.strip()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/widget")
def widget():
    """Return minimal chat UI for embedding."""
    return render_template("widget.html")


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "")
    if not question:
        return jsonify({"error": "Question is required"}), 400
    count = session.get("question_count", 0)
    if count >= 7:
        return jsonify({"error": "Question limit reached"}), 429
    session["question_count"] = count + 1
    answer = generate_answer(question)
    remaining = 7 - session["question_count"]
    return jsonify({"answer": answer, "remaining": remaining})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
