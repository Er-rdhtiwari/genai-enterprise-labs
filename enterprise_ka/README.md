
# Enterprise Knowledge Assistant (Minimal RAG PoC)

A minimal, production-minded **Enterprise Knowledge Assistant** built with **FastAPI** that answers questions using **internal documents** (dummy `.txt` files first) by applying **RAG (Retrieval-Augmented Generation)**:

1) **Retrieve** relevant internal document chunks (Top-K)  
2) **Ground** the LLM on that context (answer only from evidence)  
3) Return an answer with **citations**, **request tracing**, and **operational logs**

This PoC is designed to be **interview-ready (IBM-style)**: clear architecture, explicit trade-offs, observability, and failure-aware defaults.

---

## What this PoC demonstrates

- **RAG workflow** (index docs → retrieve top-k → answer using context)
- **Provider abstraction**: OpenAI or Anthropic for generation (OpenAI embeddings used for retrieval in this PoC)
- **Prompt safety + templates**:
  - system/user prompt separation with selectable templates (`grounded_concise`, `grounded_reasoned`)
  - rule-based guardrails for unsafe/off-topic queries (pre-LLM)
  - prompt trace/debugging so you can compare how template changes affect outputs
- **Enterprise guardrails (minimal)**:
  - “Answer only from provided internal context”
  - “If evidence missing, say you don’t know”
  - basic prompt-injection resistance by treating docs as untrusted text
- **Operational basics**:
  - request correlation (`x-request-id`)
  - structured logging and error handling
- **Developer productivity**:
  - **Makefile** = consistent commands for run/test/lint/build
  - **pyproject.toml** = one place to configure lint/format/typecheck/test tools

---

## High-level architecture

```text
Client
  |
  v
FastAPI /v1/ask
  |
  +--> Guardrails (unsafe/off-topic pre-checks; no LLM call if blocked)
  |
  +--> Retriever (top-k chunk search)
  |        |
  |        +--> Load/Build embeddings index (startup)
  |
  +--> Prompt Template Builder (system + user separation; selectable templates)
  |
  +--> LLM Provider (OpenAI or Anthropic)
  |
  v
Answer + citations + prompt trace + latency + x-request-id
````

---

## Repository structure

```text
enterprise_ka/
  app/
    main.py
    schemas.py
    core/
      config.py
      logging.py
      middleware.py
    llm/
      base.py
      openai_chat.py
      anthropic_messages.py
    rag/
      chunking.py
      index.py
      prompts.py
      retriever.py
  data/
    docs/
      security_policy.txt
      oncall_runbook.txt
  scripts/
    build_index.py
  requirements.txt
  .env.example
  README.md
  Dockerfile
  Makefile
  pyproject.toml
```

---

## Purpose of each file

### Root level

* **`requirements.txt`**

  * Runtime dependencies (FastAPI, httpx, numpy, retries, etc.)

* **`.env.example`**

  * Environment variable template (provider selection, API keys, models, RAG settings)

* **`Dockerfile`**

  * Container build for consistent local / CI execution

* **`Makefile`**

  * Standard developer/CI commands: `make run`, `make test`, `make lint`, `make docker-build`, etc.

* **`pyproject.toml`**

  * Central configuration for tooling:

    * lint/format (`ruff`)
    * type checking (`mypy`)
    * tests (`pytest`)
  * Keeps settings consistent across team + CI

* **`README.md`**

  * Project usage + architecture + ops/testing notes

---

### `app/` (application code)

* **`app/main.py`**

  * FastAPI entrypoint
  * wires: config → logging → middleware → retriever → LLM client
  * endpoints:

    * `GET /healthz`
    * `POST /v1/ask`
  * builds/loads index on startup for predictable first-request latency

* **`app/schemas.py`**

  * Pydantic request/response schemas (validation + clean API contracts)

---

### `app/core/` (platform basics)

* **`app/core/config.py`**

  * Central config via `pydantic-settings`
  * reads env vars, provides typed settings

* **`app/core/logging.py`**

  * logging setup for consistent stdout logs (dev + containers)

* **`app/core/middleware.py`**

  * request id middleware:

    * uses incoming `x-request-id` or generates one
    * injects it into response headers for tracing

* **`app/core/guardrails.py`**

  * lightweight, rule-based guardrails to deflect unsafe or irrelevant questions before the LLM:

    * blocks prompt-injection/system-override patterns and credential exfil attempts
    * warns on obviously off-topic queries (movies, sports, etc.)
    * low-relevance thresholding (when retrieval has weak matches)

---

### `app/llm/` (LLM providers)

* **`app/llm/base.py`**

  * interfaces:

    * `LLMClient.generate()`
    * `Embedder.embed()`
  * keeps app logic provider-agnostic

* **`app/llm/openai_chat.py`**

  * OpenAI Chat Completions client (HTTP via `httpx`)
  * OpenAI Embeddings client
  * retries with exponential backoff (`tenacity`)

* **`app/llm/anthropic_messages.py`**

  * Anthropic Messages client (HTTP via `httpx`)
  * used for generation in this PoC
  * retrieval still uses OpenAI embeddings for simplicity

> In production you typically standardize embeddings (self-host or single vendor)
> for governance, cost control, and reducing operational complexity.

---

### `app/rag/` (retrieval system)

* **`app/rag/chunking.py`**

  * simple chunking with overlap (practical for PoC)

* **`app/rag/index.py`**

  * loads docs from `data/docs`
  * cosine similarity utilities
  * index persistence to JSON

* **`app/rag/retriever.py`**

  * builds/loads index on startup
  * embeds query and returns top-k chunks by cosine similarity

* **`app/rag/prompts.py`**

  * prompt templates + system/user separation:

    * templates: `grounded_concise` (default) and `grounded_reasoned`
    * render system + user prompts with context + safety notes
    * can return prompt trace for debugging to compare variants
  * formats context chunks with IDs for citations

---

### `data/docs/` (dummy internal docs)

* **`security_policy.txt`**, **`oncall_runbook.txt`**

  * sample “internal” sources to test retrieval + grounded responses

---

### `scripts/`

* **`scripts/build_index.py`**

  * optional manual index build step (useful for CI or first-time warmup)

---

## Day 2: Prompt safety & template experimentation

- **Guardrails-first flow**: a rule-based pre-screen blocks obvious prompt-injection/credential exfiltration and warns on off-topic asks (movies, sports, etc.). Low-relevance checks (cosine score < `MIN_RELEVANCE_SCORE`) short-circuit responses instead of letting the LLM hallucinate.
- **Prompt templates (system + user separation)**: select `grounded_concise` (default) or `grounded_reasoned` via `prompt_template` in the request; both keep grounding rules but differ in tone and rationale depth.
- **Prompt trace & debugging**: set `debug_prompt=true` to get the rendered system/user prompts back (`prompt` field) so you can see how template changes impact outputs.

Example request with prompt variant + debug:

```bash
curl -s http://localhost:8000/v1/ask \
  -H "Content-Type: application/json" \
  -d '{
        "question":"What is the SEV1 escalation procedure?",
        "prompt_template":"grounded_reasoned",
        "debug_prompt":true
      }'
```

Handling off-topic/unsafe queries:
- If the question matches block rules (prompt injection / credentials / destructive ops) → returns a guarded message, no LLM call.
- If retrieval relevance is too low → returns a gentle “ask about policies/incidents/runbooks” response with `guardrails` noting the low score.

Responses now include extra traceability fields:
- `guardrails`: list of safety findings (block/warn/info) that influenced routing.
- `prompt`: which template/version was used; with `debug_prompt=true` the rendered system/user prompts are echoed for side-by-side comparison.

Available templates (extend in `app/rag/prompts.py`):
- `grounded_concise` → fast, citation-first answers with safety notes injected.
- `grounded_reasoned` → adds a short rationale and gap call-outs to illustrate prompt impact.

## Setup

### 1) Create virtual environment + install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Configure environment

```bash
cp .env.example .env
# edit .env and set:
# - LLM_PROVIDER=openai OR anthropic
# - OPENAI_API_KEY (required for embeddings in this PoC)
# - ANTHROPIC_API_KEY (required only if LLM_PROVIDER=anthropic)
# - PROMPT_TEMPLATE (grounded_concise or grounded_reasoned)
# - MIN_RELEVANCE_SCORE (low-signal cutoff for off-topic handling)
# - CORS_ORIGINS (comma-separated, e.g. http://localhost:3000 for the Next.js UI)
```

### 3) Run the service

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## Efficient usage: Makefile (recommended workflow)

> Makefile is your “single command surface” for dev + CI.

### See available commands

```bash
make help
```

### One-time setup (recommended)

```bash
make venv
make install
make install-dev
```

### Run locally (dev)

```bash
make run
```

### Build or refresh the index (calls embeddings API)

```bash
make build-index
```

### Quality checks before commit

```bash
make fmt
make lint
make type
make test
```

### One command to run everything (CI-style)

```bash
make check
```

### Docker build/run

```bash
make docker-build
make docker-run
```

**Why this is efficient**

* You don’t memorize long commands.
* CI can run `make check` reliably.
* Everyone uses the same entry points → fewer “works on my machine” issues.

---

## Efficient usage: pyproject.toml (tooling configuration)

`pyproject.toml` is not something you “run”. It **configures** tools you run.

### Example: ruff uses pyproject.toml automatically

```bash
python -m ruff check .
python -m ruff format .
```

### mypy uses pyproject.toml automatically

```bash
python -m mypy app
```

### pytest uses pyproject.toml automatically

```bash
python -m pytest
```

**Why this is efficient**

* Central config for tooling (no scattered `.flake8`, `setup.cfg`, etc.)
* Tools behave the same locally and in CI

---

## Testing (manual)

### Health check

```bash
curl -s http://localhost:8000/healthz
```

Expected:

```json
{"ok": true}
```

### Ask a question (check citations + request id header)

```bash
curl -i -s http://localhost:8000/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"What is the policy for logging PII?"}'
```

What to verify:

* Answer grounded in docs
* Citations like `[security_policy::security_policy::c0]` (chunk id format may vary)
* Response includes `x-request-id` header

### Test “I don’t know” behavior

```bash
curl -s http://localhost:8000/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"What is our maternity leave policy?"}'
```

Expected:

* “I don’t know based on the provided documents.”

### Verify retrieval relevance

```bash
curl -s http://localhost:8000/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"How quickly should we escalate SEV1 to the Incident Commander?"}'
```

Expected:

* mentions “within 10 minutes”
* cites `oncall_runbook` chunks

---

## Docker

Build:

```bash
docker build -t enterprise-ka:0.1 .
```

Run:

```bash
docker run --rm -p 8000:8000 \
  -e LLM_PROVIDER=openai \
  -e OPENAI_API_KEY=your_key_here \
  enterprise-ka:0.1
```

---

## Observability notes (what to look for)

* Logs should include:

  * provider used (`openai` / `anthropic`)
  * latency
  * citations (chunk IDs + similarity scores)
* `x-request-id` header lets you trace a request across logs.

---

## Security notes (PoC vs production)

PoC demonstrates the correct direction:

* Never expose raw internal corpus to clients
* Treat retrieved docs as untrusted (prompt injection resistance)
* Avoid logging sensitive content
* Secrets only via env vars (in K8s: Secrets / External Secrets)

Production upgrades:

* AuthN/AuthZ (OIDC/JWT), per-tenant isolation
* doc-level ACL filtering at retrieval time
* rate limiting, caching, circuit breakers
* evaluation harness (retrieval quality, groundedness, regression tests)
* replace JSON index with a real vector DB (FAISS/Qdrant/Pinecone/pgvector)

---

## Known limitations (intentional for PoC)

* In-memory cosine similarity search (OK for small docs)
* OpenAI embeddings required even when Anthropic generation is used
* No automated test suite yet (easy next step: add `tests/` + mocks)

---

## Quick demo questions

* “What should we avoid logging according to policy?”
* “What is the SEV1 escalation procedure?”
* “When should RCA be written after an incident?”
* “Do we log full Aadhaar numbers?”

---


## Add new documents + re-test (quick)

### 1) Add a new doc
Put a new `.txt` file in `data/docs/` (only `.txt` is indexed):

```bash
cat > data/docs/new_policy.txt <<'EOF'
Title: New Policy (Internal)
- Example rule: Do not log passwords or full Aadhaar numbers.
EOF
````

### 2) Rebuild the index (required)

The retriever uses `data/index.json`. After adding docs, rebuild:

```bash
make build-index
# OR
python scripts/build_index.py
```

(Alternative: delete index and restart)

```bash
rm -f data/index.json
# restart uvicorn
```

### 3) Ask a question to verify

```bash
curl -i -s http://localhost:8000/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"What does the new policy say about logging?"}'
```

✅ Success checklist:

* HTTP **200**
* Answer includes info from the new doc
* Citations include `new_policy` (doc_id) / chunk id

### Troubleshooting (fast)

* Ensure doc is `.txt` and placed under `data/docs/`
* Confirm `.env` points to the correct folder:

  ```bash
  echo $DOCS_DIR
  ```
* If it still says “I don’t know”, rebuild the index again and retry with a more direct question.

---
