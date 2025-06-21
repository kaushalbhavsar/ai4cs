import os
import json
from typing import List, Tuple

import openai
import numpy as np
from PyPDF2 import PdfReader
import faiss


def load_pdf_text(pdf_path: str) -> str:
    """Extract text from a single PDF file."""
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


def split_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Split text into overlapping chunks."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


class PdfVectorIndex:
    def __init__(self, openai_api_key: str, index_path: str, chunks_path: str):
        openai.api_key = openai_api_key
        self.index_path = index_path
        self.chunks_path = chunks_path
        self.index = None
        self.text_chunks: List[str] = []

    def load_index(self) -> bool:
        """Load index and text chunks from disk if available."""
        if os.path.exists(self.index_path) and os.path.exists(self.chunks_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.chunks_path, "r", encoding="utf-8") as f:
                self.text_chunks = json.load(f)
            return True
        return False

    def save_index(self) -> None:
        """Persist index and text chunks to disk."""
        if self.index is not None:
            faiss.write_index(self.index, self.index_path)
            with open(self.chunks_path, "w", encoding="utf-8") as f:
                json.dump(self.text_chunks, f)

    def build_index(self, pdf_dir: str):
        """Load PDFs from a directory and build or load FAISS index."""
        if self.load_index():
            return

        pdf_paths = [
            os.path.join(pdf_dir, f)
            for f in os.listdir(pdf_dir)
            if f.lower().endswith(".pdf")
        ]
        self.add_pdfs(pdf_paths, save=False)
        self.save_index()

    def add_pdfs(self, pdf_paths: List[str], save: bool = True) -> None:
        """Add PDF files to the index."""
        new_chunks = []
        for path in pdf_paths:
            if not os.path.exists(path):
                continue
            text = load_pdf_text(path)
            chunks = split_text(text)
            new_chunks.extend(chunks)
        if not new_chunks:
            return
        embeddings = self._embed_texts(new_chunks)
        if self.index is None:
            dim = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)
        self.text_chunks.extend(new_chunks)
        if save:
            self.save_index()

    def _embed_texts(self, texts: List[str]) -> np.ndarray:
        embeddings = []
        for text in texts:
            resp = openai.embeddings.create(input=[text], model="text-embedding-ada-002")
            embeddings.append(np.array(resp.data[0].embedding, dtype=np.float32))
        return np.vstack(embeddings)

    def query(self, question: str, top_k: int = 3) -> List[str]:
        q_resp = openai.embeddings.create(input=[question], model="text-embedding-ada-002")
        q_emb = np.array(q_resp.data[0].embedding, dtype=np.float32).reshape(1, -1)
        distances, indices = self.index.search(q_emb, top_k)
        return [self.text_chunks[i] for i in indices[0]]
