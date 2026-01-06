import importlib
from dataclasses import dataclass

import pytest
from fastapi.testclient import TestClient

# FastAPI app wires global singletons on import.
# To keep tests isolated and offline, we reload modules after setting env
# and replace the retriever/LLM with lightweight stubs.

@dataclass
class FakeChunk:
    doc_id: str
    chunk_id: str
    text: str


class DummyRetriever:
    async def warmup(self):
        return None

    async def search(self, query: str, top_k: int):
        return [(FakeChunk(doc_id="doc", chunk_id="doc::c0", text="fake context"), 0.95)]


class DummyLLM:
    def __init__(self):
        self.calls = []

    async def generate(self, system: str, user: str) -> str:
        self.calls.append({"system": system, "user": user})
        return "stubbed answer"


@pytest.fixture()
def test_client(monkeypatch, tmp_path):
    # Ensure deterministic env for settings on import
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")
    monkeypatch.setenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
    monkeypatch.setenv("DOCS_DIR", str(tmp_path))
    monkeypatch.setenv("INDEX_PATH", str(tmp_path / "index.json"))
    monkeypatch.setenv("PROMPT_TEMPLATE", "grounded_concise")
    monkeypatch.setenv("MIN_RELEVANCE_SCORE", "0.1")

    # Reload settings + app to pick up env overrides
    import app.core.config as config
    importlib.reload(config)
    import app.main as main
    importlib.reload(main)

    # Replace network-bound components with stubs
    main.retriever = DummyRetriever()
    main.llm_client = DummyLLM()

    with TestClient(main.app) as client:
        yield client


def test_health_ok(test_client):
    resp = test_client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}


def test_ask_returns_stubbed_answer_with_prompt_trace(test_client):
    payload = {"question": "What is the escalation policy?", "debug_prompt": True}
    resp = test_client.post("/v1/ask", json=payload)
    assert resp.status_code == 200
    body = resp.json()

    assert body["answer"] == "stubbed answer"
    assert body["citations"][0]["doc_id"] == "doc"
    assert body["prompt"]["template"] == "grounded_concise"
    assert body["prompt"]["system_prompt"]  # returned because debug_prompt=true
    assert body["prompt"]["user_prompt"]
    assert body["guardrails"] == []
