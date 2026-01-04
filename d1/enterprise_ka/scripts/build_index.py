import asyncio
from app.core.config import settings
from app.llm.openai_chat import OpenAIEmbedder
from app.rag.retriever import Retriever

async def main():
    embedder = OpenAIEmbedder(settings.openai_api_key, settings.openai_embed_model, settings.openai_base_url)
    retriever = Retriever(settings.docs_dir, settings.index_path, embedder, settings.chunk_max_chars, settings.chunk_overlap_chars)
    await retriever.warmup()
    print("Index ready:", settings.index_path)

if __name__ == "__main__":
    asyncio.run(main())
