import os
from flask import Flask, request, jsonify, render_template
import openai

from .pdf_processor import PdfVectorIndex

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PDF_DIR = os.getenv("PDF_DIR", "pdfs")

app = Flask(__name__)
vector_index = PdfVectorIndex(OPENAI_API_KEY)
vector_index.build_index(PDF_DIR)


def generate_answer(question: str) -> str:
    contexts = vector_index.query(question)
    prompt = "Answer the question using the context below.\n\n" + "\n\n".join(contexts) + f"\n\nQuestion: {question}\nAnswer:"
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return response.choices[0].message.content.strip()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "")
    if not question:
        return jsonify({"error": "Question is required"}), 400
    answer = generate_answer(question)
    return jsonify({"answer": answer})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
