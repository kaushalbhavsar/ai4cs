import os
import csv
import json
from typing import List, Dict

import openai
import numpy as np
import faiss


def row_to_text(row: Dict[str, str]) -> str:
    """Convert a CSV row dict to a plain text representation."""
    parts = [f"{k}: {v}" for k, v in row.items()]
    return " | ".join(parts)


class CsvVectorIndex:
    def __init__(self, openai_api_key: str, index_path: str, rows_path: str):
        openai.api_key = openai_api_key
        self.index_path = index_path
        self.rows_path = rows_path
        self.index = None
        self.row_texts: List[str] = []
        self.rows: List[Dict[str, str]] = []

    def load_index(self) -> bool:
        if os.path.exists(self.index_path) and os.path.exists(self.rows_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.rows_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.row_texts = data["texts"]
                self.rows = data["rows"]
            return True
        return False

    def save_index(self) -> None:
        if self.index is not None:
            faiss.write_index(self.index, self.index_path)
            with open(self.rows_path, "w", encoding="utf-8") as f:
                json.dump({"texts": self.row_texts, "rows": self.rows}, f)

    def build_index(self, csv_path: str) -> None:
        if self.load_index():
            return
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        self.add_rows(rows, save=False)
        self.save_index()

    def add_rows(self, rows: List[Dict[str, str]], save: bool = True) -> None:
        if not rows:
            return
        texts = [row_to_text(r) for r in rows]
        embeddings = self._embed_texts(texts)
        if self.index is None:
            dim = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)
        self.row_texts.extend(texts)
        self.rows.extend(rows)
        if save:
            self.save_index()

    def _embed_texts(self, texts: List[str]) -> np.ndarray:
        embeddings = []
        for text in texts:
            resp = openai.embeddings.create(input=[text], model="text-embedding-ada-002")
            embeddings.append(np.array(resp.data[0].embedding, dtype=np.float32))
        return np.vstack(embeddings)

    def query(self, question: str, top_k: int = 3) -> List[Dict[str, str]]:
        q_resp = openai.embeddings.create(input=[question], model="text-embedding-ada-002")
        q_emb = np.array(q_resp.data[0].embedding, dtype=np.float32).reshape(1, -1)
        distances, indices = self.index.search(q_emb, top_k)
        return [self.rows[i] for i in indices[0]]
