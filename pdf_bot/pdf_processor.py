import os
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
    def __init__(self, openai_api_key: str):
        openai.api_key = openai_api_key
        self.index = None
        self.text_chunks: List[str] = []

    def build_index(self, pdf_dir: str):
        """Load PDFs from a directory and build FAISS index."""
        all_chunks = []
        for fname in os.listdir(pdf_dir):
            if fname.lower().endswith(".pdf"):
                text = load_pdf_text(os.path.join(pdf_dir, fname))
                chunks = split_text(text)
                all_chunks.extend(chunks)
        self.text_chunks = all_chunks
        embeddings = self._embed_texts(all_chunks)
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)

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
