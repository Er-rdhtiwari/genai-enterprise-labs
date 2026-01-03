# Capstone POC (15 days): **LLM Research Engineer Workbench**

A production-like system to **run GenAI experiments** end-to-end:

**Core features**

* RAG service (FastAPI) with **dataset-backed evaluation harness**
* Prompt/version registry + experiment tracking
* Automated eval metrics + human feedback loop
* Observability (logs/metrics/traces)
* Deployment: **EKS + Helm + Jenkins + Route53/ACM + Secrets Manager**

**LLM Providers**

* OpenAI + Anthropic via a **single provider abstraction**
* (Optional later) add OSS model (vLLM / TGI) if time permits

**Datasets**

* Hugging Face datasets for QA/RAG evaluation (e.g., NaturalQuestions subset, HotpotQA, SQuAD-like, or any HF dataset you choose)

---

# 15-Day Plan (2h Interview + 2h Build + 1h Deploy)

## Week 1 — LLM + RAG foundation (build something working fast)

**Day 1 — Architecture + Repo + Baseline**

* **Interview (2h):** LLM systems overview, RAG vs fine-tune, latency/cost tradeoffs, failure modes
* **Build (2h):** Monorepo skeleton (backend + eval runner), settings, logging, health endpoints
* **Deploy (1h):** Local Docker Compose (API + Qdrant + Postgres + Redis)
* **Output:** Running `/health`, `/version`, basic CI checks locally

**Day 2 — Provider Abstraction (OpenAI/Anthropic) + Prompting**

* **Interview:** prompt patterns (few-shot, ReAct), guardrails, structured outputs
* **Build:** `LLMClient` interface + OpenAI/Anthropic adapters + retries/timeouts
* **Deploy:** secrets via `.env` + compose; smoke test script
* **Output:** `/generate` endpoint + traceable request IDs

**Day 3 — Embeddings + Vector DB (Qdrant)**

* **Interview:** embeddings, similarity, chunking impacts, ANN basics
* **Build:** embedding service + Qdrant collections + upsert/query
* **Deploy:** Qdrant in compose; basic monitoring endpoint
* **Output:** `/embed`, `/search` endpoints

**Day 4 — Ingestion Pipeline + Chunking**

* **Interview:** chunking strategies, metadata, dedupe, doc lifecycle
* **Build:** ingestion job (PDF/TXT/MD), chunker, metadata store in Postgres
* **Deploy:** background worker (Celery/RQ) OR simple internal job runner
* **Output:** `/ingest` + “doc status” endpoints

**Day 5 — RAG v1 (Retrieve → Augment → Generate)**

* **Interview:** hallucinations, citation strategy, context windows
* **Build:** `/rag/query` with citations + prompt templates
* **Deploy:** config for prompt versions; readiness/liveness probes
* **Output:** RAG responses + citations and latency stats

**Day 6 — Evaluation Harness v1 (HF dataset)**

* **Interview:** offline vs online eval, metrics pitfalls, baselines
* **Build:** eval runner that loads a HF dataset → runs RAG → stores results
* **Deploy:** make eval runnable as a k8s Job later; for now CLI
* **Output:** metrics report JSON + simple leaderboard

**Day 7 — Feedback Loop + Prompt Registry**

* **Interview:** human-in-loop, RLHF basics, preference data, prompt iteration
* **Build:** prompt registry (versioned prompts), feedback endpoints (thumbs up/down + comment)
* **Deploy:** Postgres migrations; seed scripts
* **Output:** prompt versions + feedback stored per run

---

## Week 2 — Research-grade evaluation + production engineering

**Day 8 — Advanced RAG (reranking / hybrid retrieval)**

* **Interview:** sparse vs dense, reranking, multi-query retrieval
* **Build:** optional BM25 (or hybrid) + reranker (cross-encoder or LLM rerank)
* **Deploy:** feature flags; fallback strategy
* **Output:** compare RAG v1 vs RAG v2 in eval

**Day 9 — Robustness: caching, rate limits, cost controls**

* **Interview:** scaling LLM services, caching layers, throttling, cost budgeting
* **Build:** Redis caching (embeddings + retrieval), rate limit middleware, cost estimator
* **Deploy:** config maps; define SLO targets
* **Output:** predictable latency + reduced token spend

**Day 10 — Security & Compliance**

* **Interview:** secrets, IAM, PII redaction, audit logging
* **Build:** auth (API key/JWT), audit logs, PII scrubber option
* **Deploy:** External Secrets pattern (later EKS), local secret hygiene now
* **Output:** secured endpoints + audit trail

**Day 11 — Observability (Logs/Metrics/Tracing)**

* **Interview:** what to log for GenAI, tracing spans, golden signals
* **Build:** OpenTelemetry tracing + Prometheus metrics + structured logs
* **Deploy:** docker compose add Prometheus/Grafana (optional)
* **Output:** dashboard-ready metrics and traces

**Day 12 — CI Quality Gates + Tests**

* **Interview:** testing AI systems, contract tests, eval-as-test
* **Build:** unit tests + integration tests; “eval threshold gate” in CI
* **Deploy:** Github Actions or Jenkins local pipeline (even before EKS)
* **Output:** CI pipeline that fails if quality drops

---

## Week 3 — Kubernetes + Helm + Jenkins + DNS (the “real industry” part)

**Day 13 — Kubernetes Packaging (Helm chart)**

* **Interview:** k8s primitives, rolling updates, config strategies
* **Build:** Helm chart for API + worker + jobs; values for dev/prod
* **Deploy:** minikube/kind deploy via helm (fast feedback)
* **Output:** `helm upgrade --install` works locally

**Day 14 — AWS EKS Deploy + ECR + Secrets Manager**

* **Interview:** IRSA, ALB ingress, ACM, Route53 mapping
* **Build:** Terraform for EKS + ECR + IAM + ALB controller + external secrets
* **Deploy:** EKS live deploy; dev URL `workbench-dev.rdhcloudlab.com`
* **Output:** public HTTPS endpoint working

**Day 15 — Jenkins CI/CD + Promotion to Prod**

* **Interview:** release strategies (blue/green, canary), rollbacks, incident story
* **Build:** Jenkins pipeline: build → test → scan → push → helm deploy → smoke tests → promote
* **Deploy:** prod URL `workbench.rdhcloudlab.com`; implement “promote to prod” stage
* **Output:** real pipeline + dev→prod promotion story for interviews

---

# 7-Day Interview-Focused Revision Plan (1 week after Day 15)

**R1 — LLM & Prompting mastery**

* 30 Q/A drills: tokens, context window, prompt patterns, failure modes
* 2 system-design prompts: “LLM gateway service”, “multi-provider abstraction”

**R2 — RAG deep revision**

* chunking, retrieval, reranking, citations, hallucination mitigation
* whiteboard: RAG architecture + scaling + caching

**R3 — Evaluation & Research mindset**

* offline eval, metric selection, baselines, ablations, regression testing
* prepare: “How I proved improvement” narrative (STAR format)

**R4 — MLOps & Deployment**

* CI/CD design, model/prompt versioning, rollback, monitoring
* prepare: “promotion to prod pipeline story”

**R5 — Security + Reliability**

* secrets, IAM, PII, audit logs, rate limit, incident response
* mock: threat model for LLM API

**R6 — Behavioral + IBM-style impact stories**

* 6 stories: leadership, conflict, design tradeoff, outage fix, mentoring, delivery

**R7 — Full mocks**

* 1 mock system design (60 min)
* 1 mock coding (45 min)
* 1 mock research/eval deep dive (45 min)
* finalize cheat sheets + portfolio README

---

# ✅ Now the 3 Prompts you asked (copy-paste ready)

## 1) Daily Notes Prompt (Senior AI Engineer + Research + DevOps Coach)

Paste this every day, replace placeholders.

```text
You are my Senior AI Engineer + AI Research Engineer + Cloud/DevOps Architect coach.

DAY: {DAY_NUMBER}/15
TODAY’S TOPIC: {PASTE_TODAY_TOPIC}

My constraints:
- I have 2 hours for interview prep learning, 2 hours for building the POC, 1 hour for deployment.
- I want production-grade reasoning + interview readiness.
- Use crisp explanations but senior depth. Use simple examples when needed.
- Assume AWS + OpenAI + Anthropic are available.
- Use Hugging Face dataset examples wherever possible.

Deliver in 2 phases:

PHASE A — High-Level Map (no deep dive yet)
1) Break TODAY’S TOPIC into 7–10 parts/modules.
2) For each part provide:
   - What it is (1–2 lines)
   - Why it matters in enterprise GenAI / IBM Research-style work
   - What I must say in interviews (talking points)
   - Common failure modes / pitfalls
3) End PHASE A by asking me: “Which part number should we deep dive first?”

PHASE B — Deep Dive (ONLY for the part(s) I select)
For each selected part:
1) Explain like senior engineer: architecture + tradeoffs + best practices
2) Give 8–12 interview Q&A (with crisp, correct answers)
3) Add “Red flags I must avoid saying” (common mistakes)
4) Provide a small runnable example or pseudo-code
5) End with: “What I should implement today in the POC to reinforce this”
Wait for my part selection before doing Phase B.
```

Mini follow-up (use this after Phase A):

```text
Deep dive Part #{N}. Also give me a 10-minute revision cheat sheet at the end.
```

---

## 2) Industry-Grade POC Prompt (Build incrementally, real repo, real quality)

Use this daily after notes (for the 2h build slot).

```text
You are my Staff-level Engineer pair programmer.

POC NAME: LLM Research Engineer Workbench
DAY: {DAY_NUMBER}/15
TODAY BUILD GOAL: {PASTE_TODAY_BUILD_GOAL}

Tech constraints (mandatory):
- Backend: FastAPI (Python 3.11), Pydantic settings, structured logging
- Vector DB: Qdrant (local via Docker; later cloud ok)
- Metadata store: Postgres
- Cache/rate limit: Redis
- LLM Providers: OpenAI + Anthropic via a single abstraction interface
- Dataset/Eval: Hugging Face datasets integrated in eval runner
- Repo quality: clean architecture, tests, README, .env.example
- Include cost & safety controls (timeouts, retries, max tokens)

What to output (must be production-like):
1) Target architecture diagram (ASCII ok) for TODAY BUILD GOAL.
2) Exact repo folder tree (backend/ eval/ infra/ helm/ etc).
3) Code files with full content (copy-paste ready).
4) Config files: pyproject/requirements, .env.example, docker-compose.yml updates.
5) Tests:
   - unit tests for core logic
   - 1 integration test (API + Qdrant/Postgres if relevant)
6) A “Run locally” section with commands.
7) A “Definition of Done” checklist (10 bullets).

Rules:
- Do not give vague guidance—give real files and commands.
- Prefer simple but correct production patterns.
- If a choice exists, pick one and explain the tradeoff briefly.
```

---

## 3) Industry-Grade Deployment Prompt (K8s + Helm + Jenkins + AWS + DNS)

Use this for the daily 1h deploy slot (and especially Days 13–15).

```text
Act as my Cloud/DevOps Architect and release engineer.

SYSTEM: LLM Research Engineer Workbench
TARGET: Kubernetes + Helm + Jenkins + AWS (EKS), with real DNS + TLS

Context:
- Domain: {YOUR_DOMAIN} (e.g., rdhcloudlab.com)
- Dev URL: workbench-dev.{YOUR_DOMAIN}
- Prod URL: workbench.{YOUR_DOMAIN}
- I want dev→prod promotion with rollback.

Deliverables (must be copy-paste ready):
A) Kubernetes + Helm
1) Helm chart structure:
   - API Deployment/Service
   - Worker Deployment (if used)
   - Job/CronJob for evaluation runner
   - Ingress (ALB Ingress Controller)
   - HPA (optional), PDB (optional)
   - ConfigMaps + Secrets or ExternalSecrets
2) values-dev.yaml and values-prod.yaml
3) Health checks, resource requests/limits, env vars

B) AWS (Terraform)
1) Terraform modules or minimal setup for:
   - EKS cluster + node group
   - ECR repo
   - IAM roles (IRSA) for service accounts
   - ACM certificate for dev/prod subdomains
   - Route53 records
   - AWS Load Balancer Controller installation
   - External Secrets operator + SecretStore using AWS Secrets Manager
2) Cost guardrails (node size suggestion + teardown commands)

C) Jenkins Pipeline
1) Jenkinsfile with stages:
   - Lint + unit tests
   - Build Docker image
   - Security scan (basic)
   - Push to ECR
   - Helm deploy to DEV
   - Smoke tests (curl endpoints)
   - Manual approval gate
   - Promote to PROD (same artifact)
   - Rollback strategy + how to execute rollback
2) Tagging strategy: git sha + semantic tags
3) “Promotion to Prod” explanation as an interview story

D) Runbook
- Exact commands to deploy dev/prod
- How to debug: kubectl, logs, events, ingress, DNS, cert issues
- How to destroy everything safely to control cost

Rules:
- Make choices for me (don’t ask questions).
- Use best practices (IRSA, ExternalSecrets, health probes, atomic helm deploy).
- Keep it minimal but real.
```

---


### Why above prompt-set is better than “normal plans”

* **Single capstone, compounding learning**: instead of 15 disconnected mini-projects, you build **one IBM-69961 relevant system** that gets more production-grade daily (exactly what interviewers want: *depth + story*).
* **Research + engineering together**: IBM Research roles want you to **improve quality with evidence**. This plan forces **evaluation harness + baselines + regressions**, not just “a chatbot that works.”
* **Interview readiness is built-in**: each day you generate **talking points + pitfalls + Q&A**, then immediately implement the concept. That creates strong recall.
* **Production story end-to-end**: Kubernetes + Helm + Jenkins + DNS + Secrets are not “extra”; they become your **release narrative** (dev→prod promotion + rollback), which is a big differentiator.
* **Reusable daily prompts**: you don’t need to think “what should I study today?”—you paste the same prompts and only change the placeholders.

---

## How to follow it daily (super clear routine)

Think of your day as **3 blocks**: Learn (2h) + Build (2h) + Deploy (1h).

### Every day you do this exact sequence:

## Block 1 — 2 hours (Interview prep notes)

1. **Paste Prompt #1 (Daily Notes Prompt)**

   * Set `DAY` and `TODAY’S TOPIC` from the plan.
2. You will receive **PHASE A (High-Level Map)**: 7–10 parts.
3. **Pick 1–2 parts only** (don’t try all).
4. Paste:
   `Deep dive Part #X (and Part #Y if time). Also give me a 10-minute revision cheat sheet.`
5. Output you save in your notes:

   * key concepts + tradeoffs
   * 8–12 Q&A
   * pitfalls/red flags
   * small pseudo-code

✅ Done for Block 1.

---

## Block 2 — 2 hours (Build the POC increment)

1. Take the last section from notes: **“What I should implement today in the POC”**
2. Paste Prompt #2 (POC Build Prompt) with:

   * `DAY`
   * `TODAY BUILD GOAL` (1 crisp goal)
3. It will generate:

   * repo tree
   * code files
   * tests
   * run commands
   * definition of done checklist
4. You implement it locally and run:

   * unit tests
   * one integration test (if included)
   * smoke test

✅ Done for Block 2.

---

## Block 3 — 1 hour (Deploy / DevOps)

There are two modes depending on the day:

### Mode A (Days 1–12): “Local deploy”

* Use Docker Compose, health checks, env, secrets hygiene.
* Paste Prompt #3 but specify:
  **“Today I want local deployment (docker-compose) + basic CI steps.”**

### Mode B (Days 13–15): “Kubernetes/AWS deploy”

* Paste Prompt #3 as-is.
* Output will give Helm/Terraform/Jenkins steps.
* You deploy to:

  * `workbench-dev.yourdomain`
  * then promote to prod

✅ Done for Block 3.

---

# What you should prepare before Day 1 (one-time setup)

Do this once so daily flow is smooth:

* Create repo: `llm-workbench/`
* Install: Python 3.11 + poetry/pip-tools
* Docker Desktop running
* Decide one dataset: HuggingFace QA dataset (any)
* Create API keys:

  * OpenAI
  * Anthropic
* AWS baseline:

  * IAM user/role access
  * Route53 zone already exists (you said you have domain)

---

## Daily “Checklist” you follow (copy-paste)

```text
Daily execution checklist (repeat every day):
1) Notes (2h)
   - Paste Prompt #1 with today’s topic
   - Pick Part # -> Deep dive
   - Save cheat sheet + Q&A

2) Build (2h)
   - Paste Prompt #2 with today build goal
   - Implement files + run tests
   - Confirm Definition of Done

3) Deploy (1h)
   - Days 1–12: docker-compose + smoke test
   - Days 13–15: Helm + EKS + DNS
   - End with: curl /health and /rag/query
```

---

## Example of how Day 1 looks (so you’re not confused)

### Step 1 (Notes prompt)

* Day: 1/15
* Topic: “Architecture of LLM Workbench + RAG vs Fine-tune + baseline service skeleton”

You pick Part #2 (example: “RAG vs Fine-tune decision”) for deep dive.

### Step 2 (Build prompt)

* Build goal: “Create FastAPI skeleton + docker-compose (postgres/qdrant/redis) + /health + logging”

### Step 3 (Deploy prompt)

* Ask for docker-compose deploy + smoke test commands

---

## Common mistakes to avoid (this is where people fail)

* Trying to deep dive all parts in one day → you’ll burn out. Pick **1–2 parts max**.
* Starting AWS/EKS too early → wait until you have working local service + tests.
* No evaluation harness → IBM Research will expect you to explain *how you proved improvement*.
* No release story → you must be able to say: **“I promoted dev→prod with rollback.”**

---
