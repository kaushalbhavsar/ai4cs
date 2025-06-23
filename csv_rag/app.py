import os
from flask import Flask, request, jsonify, render_template, session
import openai

from .csv_processor import CsvVectorIndex, row_to_text

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CSV_PATH = os.getenv("CSV_PATH", "data.csv")
INDEX_PATH = os.getenv("CSV_INDEX_PATH", "csv_index.faiss")
ROWS_PATH = os.getenv("CSV_ROWS_PATH", "rows.json")

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change-me")
vector_index = CsvVectorIndex(OPENAI_API_KEY, INDEX_PATH, ROWS_PATH)
vector_index.build_index(CSV_PATH)


def generate_answer(question: str) -> str:
    rows = vector_index.query(question)
    contexts = [row_to_text(r) for r in rows]
    prompt = (
        "Answer the user's question using only the following information about ve" \
        "hicles. If the answer isn't present, reply that you do not have that in" \
        "formation without referencing the word 'context'.\n\n"
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


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "").strip()
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
