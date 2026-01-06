# 7-Day Plan (Day-wise prompts you can paste into ChatGPT)

## Day 1 — LLM Foundations (Enterprise + Interview-ready mental model)

```text
You are my interview mentor for two roles:
(1) Senior Data Scientist – Tech Lead (GenAI CoE)
(2) Data Scientist – Graph RAG & LLM Fine-Tuning

Create interview-ready notes (enterprise focused, no infra) on:
TOPIC: LLM Fundamentals & Enterprise Tradeoffs

Cover these subtopics explicitly:
1) What is an LLM (enterprise view) vs classic ML vs NLP pipelines
2) Transformer at high level (attention conceptually), tokens, embeddings, context window
3) Inference vs training vs fine-tuning (conceptual differences + when to use what)
4) Model choice strategy: open-source (LLaMA/Mistral/Gemma/Falcon) vs hosted APIs
5) Key trade-offs: latency, cost, quality, hallucination, context limits, privacy
6) Prompt vs RAG vs Fine-tuning: decision framework (when each is best)
7) Enterprise constraints: governance, auditability, data sensitivity (finance examples)

Deliverables:
- Simple ASCII diagrams for: Transformer flow, inference flow, RAG vs fine-tune decision
- A “5–7 line story” that links tokens → embeddings → attention → output quality
- 15 interview questions WITH strong answers (mix of tech + leadership)
- Common pitfalls and how to explain them in interviews (no infra terms)
```

---

## Day 2 — Prompt Engineering + Prompt Safety + Prompt Lifecycle (Tech Lead must)

```text
Act as a Senior GenAI Tech Lead interviewer coach.

TOPIC: Prompt Engineering for Enterprise Assistants (system + user separation)

Cover subtopics explicitly:
1) System vs developer vs user prompts: responsibilities + examples
2) Prompt templates: variables, formatting, constraints, tone, style control
3) Few-shot prompting and instruction design (what works, what fails)
4) Guardrails in prompts: refusal rules, scope control, relevance control
5) Prompt injection & jailbreaks: common patterns, defenses (prompt-level + app-level concepts)
6) Handling unsafe/irrelevant queries: classification approach (policy-based), safe completion patterns
7) Prompt versioning & change management: how to prove “prompt change improved output”
8) Measuring prompt quality: accuracy, groundedness, helpfulness, safety, consistency

Deliverables:
- Template library: 5 reusable prompt templates (QA, summarization, text-to-SQL, extraction, classification)
- A “prompt A/B testing” plan with evaluation criteria and examples
- A short LLD: pseudo-code for prompt assembly (system + user + context + rules)
- 12 interview questions + best answers (including prompt injection scenario)
- A mini-case: finance domain assistant and how prompts prevent hallucinated financial advice
```

---

## Day 3 — RAG Core (Retrieval, Chunking, Grounding, Evaluation)

```text
Act as an interview mentor for RAG-heavy enterprise roles.

TOPIC: Retrieval-Augmented Generation (RAG) end-to-end (no infra)

Cover subtopics explicitly:
1) Why RAG in enterprises (vs fine-tune): freshness, governance, audit, cost
2) Document ingestion concepts: cleaning, dedup, sectioning, metadata strategy
3) Chunking strategies: fixed, recursive, semantic; chunk size trade-offs
4) Embeddings: what they represent; choosing embedding models; dimension trade-offs
5) Retrieval types: vector search, keyword search, hybrid; filters + metadata
6) Reranking + query rewriting + multi-query retrieval (why and when)
7) Context building: context compression, citation mapping, “answer only from sources”
8) Hallucination reduction patterns specific to RAG
9) RAG evaluation: offline vs online; golden datasets; metrics:
   - retrieval precision/recall@k
   - groundedness / faithfulness
   - answer relevance
   - context relevance
   Mention tools conceptually: LangSmith / TruLens style evaluation, and hallucination metrics

Deliverables:
- HLD for an “Enterprise Knowledge Assistant” RAG system (components + data flow)
- LLD pseudo-code for a basic RAG pipeline (ingest → index → retrieve → generate → cite)
- A checklist: “Top 15 RAG failure modes” + fixes
- 15 interview questions with strong answers (include debugging a bad RAG output)
```

---

## Day 4 — Graph RAG + Knowledge Graphs (Role #2 core)

```text
You are a Graph RAG specialist and interview coach.

TOPIC: Graph RAG & Knowledge Graphs for enterprise retrieval + reasoning

Cover subtopics explicitly:
1) What is Graph RAG vs Vector RAG: when graph helps (relationships, multi-hop queries, reasoning)
2) Knowledge graph basics:
   - entities, relations, triples
   - ontology/schema design
   - property graph vs RDF (conceptual)
3) Building a KG from documents:
   - entity extraction, relation extraction
   - disambiguation, canonical IDs
   - confidence scoring and human review concepts
4) Graph databases & concepts (high-level):
   - Neo4j-style nodes/edges/properties
   - Cypher query concepts (example queries)
5) Combining graph + vectors:
   - entity-linked chunking
   - vector retrieval → map to entities → expand neighbors
   - graph traversal constraints (depth, time, confidence)
6) Graph embeddings & GNN idea (high-level): what they add, when not needed
7) Evaluation for Graph RAG:
   - correctness of entity linking
   - multi-hop answer accuracy
   - evidence traceability (“why this answer”)
8) Finance examples: KYC, regulatory policies, product knowledge, incident root cause linking

Deliverables:
- HLD diagram for Graph RAG system (vector + KG hybrid)
- LLD: step-by-step algorithm for query → retrieve → graph expand → answer
- 8 sample Cypher-like queries (simple, conceptual)
- 12 interview Qs + strong answers (include “why graph instead of more context chunks?”)
```

---

## Day 5 — Fine-tuning (LoRA/QLoRA/DeepSpeed conceptually) + Alignment (DPO/RLHF)

```text
Act as a Senior Data Scientist (LLM fine-tuning) interview mentor.

TOPIC: LLM Fine-tuning & Alignment (no infra)

Cover subtopics explicitly:
1) When to fine-tune vs RAG vs prompt: decision framework + examples
2) Fine-tuning types:
   - SFT (supervised fine-tuning)
   - PEFT: LoRA, QLoRA (what changes, why cheaper)
3) Training data strategy:
   - instruction datasets, domain data, synthetic data
   - labeling guidelines, quality filters, leakage prevention
4) Alignment methods (high-level):
   - RLHF conceptually
   - DPO conceptually (why used, what it optimizes)
5) Evaluation for fine-tunes:
   - task metrics, regression tests, safety checks
   - overfitting signs, catastrophic forgetting
6) Risks:
   - bias amplification
   - memorization of sensitive data
   - degraded general performance
7) Practical interview scenarios:
   - “Model is great on dev set but fails in real queries”
   - “Fine-tune improved accuracy but increased hallucinations—why?”

Deliverables:
- Comparison table: SFT vs LoRA vs QLoRA vs RLHF vs DPO (purpose, pros/cons, risks)
- LLD pseudo-code: training/evaluation loop concept + dataset splits
- A “fine-tune readiness checklist” (data, eval, rollback plan conceptually)
- 15 interview questions + strong answers
```

---

## Day 6 — Responsible AI (Hallucinations, Safety, Bias, Prompt Injection defenses)

```text
You are mentoring me for enterprise GenAI roles in financial services.

TOPIC: Responsible AI & Model Risk Management for GenAI systems

Cover subtopics explicitly:
1) Hallucinations:
   - types (fabrication, wrong attribution, outdated info)
   - why they happen (model behavior + retrieval issues)
   - mitigation patterns (RAG grounding, refusal, confidence cues, citations)
2) Prompt injection & data exfiltration:
   - attack patterns (override, instruction smuggling, tool abuse)
   - defenses (input sanitization concepts, policy checks, constrained answering)
3) Bias & toxicity:
   - where it enters (data, prompts, fine-tune)
   - detection strategies + mitigation
4) Privacy & sensitive data:
   - PII handling principles
   - “don’t memorize / don’t reveal” patterns
5) Governance for enterprise:
   - auditability (“why answer came”)
   - human-in-the-loop review concepts
   - model change management (prompt & fine-tune)
6) Evaluation safety gates:
   - red teaming approach
   - regression suite concept for safety + quality

Deliverables:
- A “Risk Register” table for GenAI assistant (risk, impact, detection, mitigation)
- 10 scenario-based interview questions + strong answers (finance-style)
- A short HLD add-on: where safety checks sit in the system flow
```

---

## Day 7 — System Design (HLD + LLD) for BOTH roles (RAG + Graph RAG + Fine-tune)

```text
Act as a Staff-level System Design interviewer for GenAI / Data Scientist roles.

TOPIC: System Design (HLD + LLD) for:
A) Enterprise Knowledge Assistant (Vector RAG)
B) Graph RAG Assistant (Vector + Knowledge Graph)
C) Fine-tuned domain assistant (where fine-tune is used, and how evaluated)

Constraints:
- No infra details (no Kubernetes/Docker/Terraform). Focus on architecture, interfaces, data flow, trade-offs.

Cover explicitly for each design:
1) Requirements:
   - functional (QA, summarization, extraction, text-to-SQL)
   - non-functional (accuracy, latency targets conceptually, privacy, auditability)
2) HLD:
   - components (ingestion, indexing, retrieval, reasoning/generation, eval)
   - data flow diagrams + boundaries
3) Retrieval design:
   - chunk/metadata strategy
   - hybrid retrieval + reranking strategy
4) Graph RAG specifics:
   - entity linking layer
   - traversal strategy and stopping rules
5) LLD:
   - API contracts (request/response fields)
   - core modules/classes responsibilities
   - error handling and fallback behaviors
6) Evaluation strategy:
   - offline golden set + online feedback loop concept
   - what metrics you track and why
7) Trade-offs:
   - RAG vs Graph RAG vs Fine-tune
   - quality vs cost vs governance

Deliverables:
- 3 separate HLD diagrams (ASCII)
- LLD: module breakdown + pseudo-code for the “answer pipeline”
- “Top 20 system design interview questions” + strong answers
- A 2-minute “whiteboard pitch” script for each design
```

---

# 2-Day Revision Plan (only revision, interview simulation)

## Revision Day 1 — Consolidation + Cheat Sheets + Q/A bank

```text
You are my interview revision coach for GenAI roles.

Create a revision pack covering:
1) One-page cheat sheets for:
   - LLM fundamentals
   - Prompt engineering + prompt injection defenses
   - RAG pipeline + failure modes
   - Graph RAG + when to use
   - Fine-tuning (LoRA/QLoRA/DPO/RLHF) + decision framework
   - Responsible AI risk register

2) A “Top 50 interview questions” bank with crisp best answers:
   - 25 technical (RAG/Graph/Fine-tune/Eval/Safety)
   - 15 system design (HLD/LLD tradeoffs)
   - 10 leadership/tech-lead (decision making, stakeholder mgmt, mentoring)

3) 3 quick mock case studies:
   - RAG output is wrong → debug path
   - Graph RAG is slow/wrong multi-hop → debug path
   - Fine-tune improved one task but regressed others → debug path

Keep answers structured: Situation → Reasoning → Decision → Outcome.
```

## Revision Day 2 — Full mock interview loop (System Design + Deep Dives)

```text
Run a complete mock interview simulation for these two roles.

Structure:
1) 5-minute intro: summarize my profile (assume I’m 8+ years Python dev moving into GenAI)
2) 45-minute system design:
   - choose between RAG assistant or Graph RAG assistant
   - ask me questions step-by-step like an interviewer
   - after each answer, give feedback and the “ideal answer”
3) 30-minute deep dive:
   - prompt injection scenario
   - evaluation design (offline + online)
   - fine-tuning decision and risks
4) 15-minute leadership round:
   - conflict with stakeholders
   - setting success metrics
   - managing model risk

Deliverables:
- My “final best answers” for each section
- My weak points + what to revise in 30 minutes before the real interview
```

---
