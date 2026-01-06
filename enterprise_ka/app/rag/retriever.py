import logging
import os

import numpy as np

from app.llm.base import Embedder
from app.rag.index import IndexedChunk, build_chunks, cosine_sim, load_index, save_index

log = logging.getLogger("rag")

class Retriever:
    def __init__(self, docs_dir: str, index_path: str, embedder: Embedder, max_chars: int, overlap: int):
        self.docs_dir = docs_dir
        self.index_path = index_path
        self.embedder = embedder
        self.max_chars = max_chars
        self.overlap = overlap
        self._index: list[IndexedChunk] | None = None

    async def warmup(self) -> None:
        if self._index is not None:
            return
        if os.path.exists(self.index_path):
            self._index = load_index(self.index_path)
            log.info("Loaded index", extra={"chunks": len(self._index)})
            return

        # PoC choice: build on startup for small doc sets.
        chunks = build_chunks(self.docs_dir, max_chars=self.max_chars, overlap=self.overlap)
        vectors = await self.embedder.embed([c.text for c in chunks])

        self._index = [
            IndexedChunk(doc_id=c.doc_id, chunk_id=c.chunk_id, text=c.text, vector=v)
            for c, v in zip(chunks, vectors, strict=True)
        ]
        save_index(self.index_path, self._index)
        log.info("Built & saved index", extra={"chunks": len(self._index)})

    async def search(self, query: str, top_k: int) -> list[tuple[IndexedChunk, float]]:
        await self.warmup()
        assert self._index is not None

        q_vec = (await self.embedder.embed([query]))[0]
        q = np.array(q_vec, dtype=np.float32)

        scored: list[tuple[IndexedChunk, float]] = []
        for item in self._index:
            v = np.array(item.vector, dtype=np.float32)
            scored.append((item, cosine_sim(q, v)))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]
