import csv
import json
import os
from datetime import datetime
from difflib import SequenceMatcher
from typing import List, Dict

from flask import Flask, request, jsonify, render_template

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
FAQ_PATH = os.path.join(DATA_DIR, 'faqs.json')
LEADS_PATH = os.path.join(DATA_DIR, 'leads.csv')
CHECKLIST_PATH = os.path.join(DATA_DIR, 'checklists.json')
APPOINT_PATH = os.path.join(DATA_DIR, 'appointments.csv')

app = Flask(__name__)


def load_faqs() -> List[Dict[str, str]]:
    with open(FAQ_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


FAQS = load_faqs()


def find_best_faq(question: str) -> str:
    question = question.lower()
    best_score = 0
    best_answer = ''
    for item in FAQS:
        q = item['question'].lower()
        score = SequenceMatcher(None, question, q).ratio()
        if score > best_score:
            best_score = score
            best_answer = item['answer']
    return best_answer if best_score > 0.6 else ''


def append_csv(path: str, row: List[str]):
    file_exists = os.path.exists(path)
    with open(path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            # headers handled externally
            pass
        writer.writerow(row)


def load_checklists() -> Dict[str, List[str]]:
    with open(CHECKLIST_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


CHECKLISTS = load_checklists()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    q = data.get('question', '')
    if not q:
        return jsonify({'error': 'Question is required'}), 400
    answer = find_best_faq(q)
    if not answer:
        answer = "I'm sorry, I don't have that information right now."
    return jsonify({'answer': answer})


@app.route('/lead', methods=['POST'])
def capture_lead():
    data = request.get_json()
    name = data.get('name', '').strip()
    phone = data.get('phone', '').strip()
    email = data.get('email', '').strip()
    country = data.get('country', '').strip()
    if not all([name, phone, email, country]):
        return jsonify({'error': 'All fields are required'}), 400
    append_csv(LEADS_PATH, [name, phone, email, country, datetime.utcnow().isoformat()])
    return jsonify({'status': 'saved'})


@app.route('/checklist', methods=['POST'])
def checklist():
    data = request.get_json()
    country = data.get('country', '').strip()
    visa_type = data.get('visa_type', '').strip()
    applicant = data.get('applicant', '').strip()
    key = f"{country}-{visa_type}".lower()
    items = CHECKLISTS.get(key, [])
    if not items:
        return jsonify({'error': 'Checklist not found'}), 404
    return jsonify({'checklist': items})


@app.route('/appointment', methods=['POST'])
def appointment():
    data = request.get_json()
    name = data.get('name', '').strip()
    phone = data.get('phone', '').strip()
    email = data.get('email', '').strip()
    time = data.get('time', '').strip()
    if not all([name, phone, email, time]):
        return jsonify({'error': 'All fields are required'}), 400
    append_csv(APPOINT_PATH, [name, phone, email, time])
    return jsonify({'status': 'booked'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
