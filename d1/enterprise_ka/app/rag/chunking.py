from dataclasses import dataclass

@dataclass(frozen=True)
class Chunk:
    doc_id: str
    chunk_id: str
    text: str

def chunk_text(doc_id: str, text: str, max_chars: int, overlap: int) -> list[Chunk]:
    # Simple sliding-window chunker (good enough for PoC)
    cleaned = " ".join(text.split())
    chunks: list[Chunk] = []
    start = 0
    idx = 0

    while start < len(cleaned):
        end = min(start + max_chars, len(cleaned))
        chunk = cleaned[start:end]
        chunks.append(Chunk(doc_id=doc_id, chunk_id=f"{doc_id}::c{idx}", text=chunk))
        idx += 1
        if end == len(cleaned):
            break
        start = max(0, end - overlap)

    return chunks
