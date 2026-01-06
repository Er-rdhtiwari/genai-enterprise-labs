import json
import os
from dataclasses import dataclass

import numpy as np

from app.rag.chunking import Chunk, chunk_text


@dataclass
class IndexedChunk:
    doc_id: str
    chunk_id: str
    text: str
    vector: list[float]

def load_docs_from_dir(docs_dir: str) -> dict[str, str]:
    docs: dict[str, str] = {}
    for name in os.listdir(docs_dir):
        if not name.endswith(".txt"):
            continue
        path = os.path.join(docs_dir, name)
        doc_id = name.replace(".txt", "")
        with open(path, encoding="utf-8") as f:
            docs[doc_id] = f.read()
    return docs

def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    denom = (np.linalg.norm(a) * np.linalg.norm(b)) + 1e-12
    return float(np.dot(a, b) / denom)

def save_index(index_path: str, items: list[IndexedChunk]) -> None:
    os.makedirs(os.path.dirname(index_path), exist_ok=True)
    payload = [item.__dict__ for item in items]
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(payload, f)

def load_index(index_path: str) -> list[IndexedChunk]:
    with open(index_path, encoding="utf-8") as f:
        payload = json.load(f)
    return [IndexedChunk(**x) for x in payload]

def build_chunks(docs_dir: str, max_chars: int, overlap: int) -> list[Chunk]:
    docs = load_docs_from_dir(docs_dir)
    all_chunks: list[Chunk] = []
    for doc_id, text in docs.items():
        all_chunks.extend(chunk_text(doc_id, text, max_chars=max_chars, overlap=overlap))
    return all_chunks
