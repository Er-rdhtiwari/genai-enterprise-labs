import logging
import time
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException, Request

from app.core.config import settings
from app.core.guardrails import GuardrailFinding, Guardrails
from app.core.logging import configure_logging
from app.core.middleware import RequestIdMiddleware
from app.llm.anthropic_messages import AnthropicMessagesClient
from app.llm.openai_chat import OpenAIChatClient, OpenAIEmbedder
from app.rag.prompts import build_prompts
from app.rag.retriever import Retriever
from app.schemas import AskRequest, AskResponse, Citation, GuardrailEvent, PromptTrace

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

@asynccontextmanager
async def lifespan(app: FastAPI):
    # PoC: build/load index at startup for predictable first-request latency.
    await retriever.warmup()
    yield

app = FastAPI(title="Enterprise Knowledge Assistant", version="0.1.0", lifespan=lifespan)
app.add_middleware(RequestIdMiddleware)
guardrails = Guardrails(min_relevance_score=settings.min_relevance_score)

def _serialize_guardrails(findings: list[GuardrailFinding]) -> list[GuardrailEvent]:
    return [GuardrailEvent(category=f.category, action=f.action, detail=f.detail) for f in findings]

@app.get("/healthz")
async def healthz():
    return {"ok": True}

@app.post("/v1/ask", response_model=AskResponse)
async def ask(req: AskRequest, request: Request):
    start = time.time()
    rid = getattr(request.state, "request_id", "")
    guardrail_findings: list[GuardrailFinding] = []

    try:
        precheck = guardrails.pre_screen(req.question)
        guardrail_findings.extend(precheck.findings)
        if precheck.blocked:
            latency_ms = int((time.time() - start) * 1000)
            serialized_guardrails = _serialize_guardrails(guardrail_findings)
            log.warning(
                "ask_blocked",
                extra={
                    "provider": settings.llm_provider,
                    "latency_ms": latency_ms,
                    "findings": [f.model_dump() for f in serialized_guardrails],
                },
            )
            return AskResponse(
                request_id=rid,
                answer=precheck.message or "Request blocked by safety policy.",
                citations=[],
                latency_ms=latency_ms,
                guardrails=serialized_guardrails,
            )

        top_k = req.top_k or settings.top_k
        results = await retriever.search(req.question, top_k=top_k)

        if not results:
            latency_ms = int((time.time() - start) * 1000)
            serialized_guardrails = _serialize_guardrails(guardrail_findings)
            return AskResponse(
                request_id=rid,
                answer="No documents available to answer this question.",
                citations=[],
                latency_ms=latency_ms,
                guardrails=serialized_guardrails,
            )

        context_blocks = []
        citations = []
        for item, score in results:
            context_blocks.append({"doc_id": item.doc_id, "chunk_id": item.chunk_id, "text": item.text})
            citations.append(Citation(doc_id=item.doc_id, chunk_id=item.chunk_id, score=score))

        top_score = citations[0].score if citations else 0.0
        relevance = guardrails.relevance_guard(top_score)
        if relevance:
            guardrail_findings.append(relevance)
            latency_ms = int((time.time() - start) * 1000)
            serialized_guardrails = _serialize_guardrails(guardrail_findings)
            log.info(
                "ask_low_relevance",
                extra={
                    "provider": settings.llm_provider,
                    "top_k": top_k,
                    "latency_ms": latency_ms,
                    "top_score": top_score,
                    "guardrails": [f.model_dump() for f in serialized_guardrails],
                },
            )
            return AskResponse(
                request_id=rid,
                answer="The question looks unrelated to the enterprise knowledge base. Please ask about policies, incidents, or runbooks.",
                citations=[],
                latency_ms=latency_ms,
                guardrails=serialized_guardrails,
            )

        safety_notes = [f.detail for f in guardrail_findings if f.action == "warn"]
        system_prompt, user_prompt, template = build_prompts(
            req.question,
            context_blocks,
            template_name=req.prompt_template or settings.prompt_template,
            safety_notes=safety_notes,
        )
        prompt_trace = PromptTrace(
            template=template.name,
            version=template.version,
            description=template.description,
        )
        if req.debug_prompt:
            prompt_trace.system_prompt = system_prompt
            prompt_trace.user_prompt = user_prompt

        answer = await llm_client.generate(system=system_prompt, user=user_prompt)

        latency_ms = int((time.time() - start) * 1000)
        serialized_guardrails = _serialize_guardrails(guardrail_findings)
        log.info(
            "ask_ok",
            extra={
                "provider": settings.llm_provider,
                "top_k": top_k,
                "latency_ms": latency_ms,
                "citations": [c.model_dump() for c in citations],
                "prompt_template": template.name,
                "guardrails": [f.model_dump() for f in serialized_guardrails],
            },
        )

        return AskResponse(
            request_id=rid,  # populated by middleware response header; keep body minimal
            answer=answer,
            citations=citations,
            latency_ms=latency_ms,
            prompt=prompt_trace,
            guardrails=serialized_guardrails,
        )

    except httpx.HTTPStatusError as e:
        log.exception("upstream_http_error")
        raise HTTPException(status_code=502, detail=f"Upstream error: {e.response.status_code}") from e
    except Exception as e:
        log.exception("ask_failed")
        raise HTTPException(status_code=500, detail=str(e)) from e
