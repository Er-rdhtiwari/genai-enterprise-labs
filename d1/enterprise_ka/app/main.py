import time
import logging
from fastapi import FastAPI, HTTPException, Request
from app.core.config import settings
from app.core.logging import configure_logging
from app.core.middleware import RequestIdMiddleware
from app.schemas import AskRequest, AskResponse, Citation
from app.rag.retriever import Retriever
from app.rag.prompts import SYSTEM_PROMPT, build_user_prompt
from app.llm.openai_chat import OpenAIChatClient, OpenAIEmbedder
from app.llm.anthropic_messages import AnthropicMessagesClient

configure_logging(settings.log_level)
log = logging.getLogger("app")

def build_llm_and_embedder():
    if settings.llm_provider == "openai":
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is missing")
        llm = OpenAIChatClient(settings.openai_api_key, settings.openai_model, settings.openai_base_url)
        embedder = OpenAIEmbedder(settings.openai_api_key, settings.openai_embed_model, settings.openai_base_url)
        return llm, embedder

    if settings.llm_provider == "anthropic":
        if not settings.anthropic_api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is missing")
        llm = AnthropicMessagesClient(settings.anthropic_api_key, settings.anthropic_model, settings.anthropic_base_url)

        # For PoC simplicity: still use OpenAI embeddings even if Anthropic is the generator.
        # In enterprise, you'd standardize embeddings vendor or self-host embeddings.
        if not settings.openai_api_key:
            raise RuntimeError("For embeddings, OPENAI_API_KEY is required in this PoC.")
        embedder = OpenAIEmbedder(settings.openai_api_key, settings.openai_embed_model, settings.openai_base_url)
        return llm, embedder

    raise RuntimeError(f"Unsupported LLM_PROVIDER={settings.llm_provider}")

llm_client, embedder = build_llm_and_embedder()
retriever = Retriever(
    docs_dir=settings.docs_dir,
    index_path=settings.index_path,
    embedder=embedder,
    max_chars=settings.chunk_max_chars,
    overlap=settings.chunk_overlap_chars,
)

app = FastAPI(title="Enterprise Knowledge Assistant", version="0.1.0")
app.add_middleware(RequestIdMiddleware)

@app.get("/healthz")
async def healthz():
    return {"ok": True}

@app.on_event("startup")
async def startup():
    # PoC: build/load index at startup for predictable first-request latency.
    await retriever.warmup()

@app.post("/v1/ask", response_model=AskResponse)
async def ask(req: AskRequest, request: Request):
    start = time.time()
    rid = getattr(request.state, "request_id", "")
    request_id = getattr(getattr(req, "__dict__", None), "request_id", None)

    try:
        top_k = req.top_k or settings.top_k
        results = await retriever.search(req.question, top_k=top_k)

        context_blocks = []
        citations = []
        for item, score in results:
            context_blocks.append({"doc_id": item.doc_id, "chunk_id": item.chunk_id, "text": item.text})
            citations.append(Citation(doc_id=item.doc_id, chunk_id=item.chunk_id, score=score))

        user_prompt = build_user_prompt(req.question, context_blocks)
        answer = await llm_client.generate(system=SYSTEM_PROMPT, user=user_prompt)

        latency_ms = int((time.time() - start) * 1000)
        log.info(
            "ask_ok",
            extra={
                "provider": settings.llm_provider,
                "top_k": top_k,
                "latency_ms": latency_ms,
                "citations": [c.dict() for c in citations],
            },
        )

        return AskResponse(
            request_id=rid,  # populated by middleware response header; keep body minimal
            answer=answer,
            citations=citations,
            latency_ms=latency_ms,
        )

    except httpx.HTTPStatusError as e:
        log.exception("upstream_http_error")
        raise HTTPException(status_code=502, detail=f"Upstream error: {e.response.status_code}")
    except Exception as e:
        log.exception("ask_failed")
        raise HTTPException(status_code=500, detail=str(e))
