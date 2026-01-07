## Day 14 — LLM Fundamentals + Multimodal + Prompt Engineering (Production Focus)

### The mental model (why this matters)

In production, almost every LLM failure maps to one of these:

1. **Representation issues** (tokenization, truncation, long-context “lost in middle”)
2. **Behavior shaping** (training stage + alignment vs raw capability)
3. **Sampling instability** (temperature/top-p causing unpredictability)
4. **Prompt/guardrail drift** (small prompt change → big behavior change)
5. **Evaluation gaps** (you can’t improve what you can’t measure)

---

## 1) LLM fundamentals

### 1.1 Tokenization (BPE, SentencePiece) — why first

**Why it matters:** LLMs don’t “see words”; they see **tokens**. Cost, latency, context limits, truncation, and even weird behaviors (e.g., spelling mistakes, strange splits) come from tokenization.

**Core idea:** Convert text → integers (token IDs) using a learned vocabulary.

#### BPE (Byte Pair Encoding) — concept

* Starts with small units (often bytes/characters).
* Repeatedly merges the most frequent adjacent pairs into new “subword” tokens.
* Good trade-off: handles unknown words by splitting into subwords.

#### SentencePiece — concept

* Similar idea but trains directly on raw text (often **byte-level**) and supports **Unigram LM** tokenization too.
* Often more robust across languages because it doesn’t rely on whitespace rules.

**Production impacts**

* **Costs scale with tokens**, not characters.
* Some languages tokenize into *more tokens* (cost ↑, context consumed faster).
* Guardrails like “respond in <100 words” are less reliable than “<N tokens”.

**ASCII**

```
Text:  "deployment-ready"
Tokens: ["deploy", "ment", "-", "ready"]   (illustrative)
IDs:    [  8123,   443,  17,   9021  ]
```

---

### 1.2 Training pipeline — what each stage *optimizes for*

**Why it matters:** Interviewers want you to connect *model behavior* to *how it was trained*. Also, the “right” mitigation depends on whether you need **capability** or **alignment**.

#### Pre-training

* Learns general language/statistics by predicting next token on massive corpora.
* **Gives capability** (knowledge patterns, reasoning-ish, style imitation).
* **Risks:** hallucination, bias, unsafe content patterns (it learned the internet).

#### Fine-tuning (task/domain)

* Training on labeled examples for a specific task/domain.
* **Gives specialization** (tone, format, domain vocabulary).
* **Risk:** overfitting, catastrophic forgetting, narrow behavior.

#### Instruction tuning

* Fine-tuning on “follow instructions” datasets (multi-task).
* **Gives helpfulness + instruction adherence**.

#### RLHF vs DPO (high-level)

* **RLHF:** Train a reward model from human preferences, then optimize the policy to maximize reward.
* **DPO:** Directly optimize preference comparisons without an explicit RL loop (often simpler, stable).
* **Why it matters:** These stages aim at **alignment**, not raw intelligence. They can reduce toxicity but may also increase refusals or “over-cautiousness”.

**ASCII**

```
Pre-train (capability) -> Instr-tune (follow tasks) -> RLHF/DPO (aligned style/safety)
```

---

### 1.3 Inference controls (sampling parameters) — why they matter

**Why it matters:** In production, most “random weird outputs” come from sampling settings, not the prompt.

* **temperature**: randomness scale

  * 0.0–0.3 for deterministic/enterprise workflows
  * 0.7+ for creative
* **top-p (nucleus sampling)**: sample from smallest set of tokens whose cumulative prob ≥ p

  * common: 0.8–0.95
* **top-k**: only consider top K tokens

  * common: 20–100 (less common now vs top-p)
* **repetition penalty**: discourages repeating tokens/phrases

  * useful for rambling/repeated loops; too high can harm coherence
* **max tokens**: hard cap on output length

  * protects cost/latency; also prevents runaways

**Trade-offs**

* Lower temperature/top-p → **stability** but can reduce diversity and sometimes correctness on ambiguous tasks.
* Higher randomness → can improve exploration but **hurts reliability** and regression stability.

---

### 1.4 Context window (truncation + long-context limits)

**Why it matters:** “Just stuff more context” is the #1 naive production mistake.

* **Truncation**: when prompt + history + docs exceed context, you drop something.
* **Long-context limitations**

  * Attention cost often grows superlinearly with length (more tokens → more compute → latency/cost).
  * Models can miss info in the middle (“lost in the middle”).
  * Retrieval quality matters more than raw window size.

**Production pattern**

* Prefer **RAG + summarization + memory discipline** over dumping full docs.
* Use **chunking + reranking** and keep “must-follow rules” short and early (system message).

---

## 2) Model families + context window + cost/latency trade-offs

### 2.1 Model families (overview)

**Why it matters:** In interviews, you’ll be asked why you chose a model (not just “because it works”).

* **GPT family**: strong general capability, tool use ecosystem, often top-tier reasoning; may be higher cost.
* **LLaMA family**: widely used open-weight ecosystem; good for on-prem/self-host; strong community tooling.
* **Mistral family**: efficient, strong performance per parameter; popular for latency-sensitive setups.
* **Gemma family**: lightweight open models; often good for constrained environments.
* **Phi family**: small models for cost/edge; good for narrow tasks, less robust for broad reasoning.

(Exact strengths vary by specific model release; in production you benchmark on your data.)

### 2.2 Context vs cost/latency (what actually drives your bill)

**Why it matters:** Token economics is a first-class architectural constraint.

Key drivers:

* **Input tokens** (prompt + retrieved context + chat history)
* **Output tokens** (generated answer; often more expensive in time and money)
* **Context length** increases compute and can reduce throughput.
* **Concurrency + tail latency**: p95/p99 dominates user experience.

**Rough cost/latency considerations (practical)**

* Minimize **retrieved text**: better retrieval beats bigger prompts.
* Use **streaming** for perceived latency.
* Add **response caps** (max tokens) + structured formats to control verbosity.
* Cache:

  * **Prompt caching** (system + stable instructions)
  * **Embedding caching** (for repeated docs)
  * **RAG result caching** (for repeated queries)
* Consider **small model first** (router): cheap classify → decide whether to call big model.

**ASCII (simple routing)**

```
User -> small model: classify/route
         |-> simple -> answer
         |-> complex -> big model (+RAG) -> answer
```

---

## 3) Multimodal LLMs + diffusion + limitations/risks

### 3.1 Multimodal LLMs (text+image input/output)

**Why it matters:** Multimodal adds new failure modes: visual hallucinations, privacy leakage, and weak grounding.

Common architecture pattern:

* **Vision encoder** (turn image into embeddings/tokens)
* These feed into the **LLM** alongside text tokens
* Output can be text, or text that controls a generator, or direct multimodal output depending on the model

**ASCII**

```
Image -> Vision Encoder -> visual tokens ----\
                                             +--> LLM -> text (or tool calls)
Text  -----------------> text tokens --------/
```

**Production risks**

* **Overconfidence about images** (“hallucinated objects”).
* **Sensitive data** in images (IDs, faces, documents).
* Need strict policy: what images allowed, what must be redacted, logging constraints.

---

### 3.2 Diffusion models (denoising intuition)

**Why it matters:** If your system generates images, diffusion is the dominant modern approach; you need to explain why it behaves differently than LLMs.

**Core idea:** Start from noise → repeatedly “denoise” guided by text conditioning.

**ASCII**

```
noise -> denoise step1 -> step2 -> ... -> stepN -> image
          (guided by text embedding)
```

**Text-to-image pipeline (high-level)**

1. Text prompt → text encoder embeddings
2. Noise latent → diffusion denoising loop (U-Net style backbone often)
3. Decode latent → image (often via VAE decoder)

---

### 3.3 VAEs, GANs vs diffusion vs LLMs (high-level compare)

* **LLMs**: discrete token generation (text/code), autoregressive next-token prediction.
* **GANs**: generator vs discriminator game; can be sharp but tricky to train, mode collapse risk.
* **VAEs**: learn latent distribution; stable training, sometimes blurrier outputs.
* **Diffusion**: iterative refinement; strong quality/diversity, slower due to many steps (though optimizations exist).

**Interview-friendly summary:**
GANs = fast generator but unstable training; VAEs = stable but can be blurry; Diffusion = best quality, slower; LLMs = best for language reasoning + tool orchestration.

---

### 3.4 Limitations & risks (must know)

* **Hallucinations**: confident but wrong outputs; worsens with long prompts, weak grounding.
* **Bias/toxicity**: inherited from data; mitigated by alignment + moderation + eval.
* **Copyright/IP**: generated content may resemble training data; manage via policy, filters, provenance tooling.
* **Safety**: prompt injection, jailbreaks, data exfiltration, disallowed outputs.

---

### 3.5 Evaluation (BLEU/ROUGE, LLM-as-judge, human rubrics)

**Why it matters:** You need a measurement strategy that matches the task.

* **BLEU/ROUGE**: OK for *overlap-based* tasks (summaries, translation) but weak for open-ended helpfulness.
* **LLM-as-judge**: scalable scoring, but can be biased/inconsistent; use:

  * fixed rubric
  * pairwise comparisons
  * calibration against human labels
* **Human rubrics**: gold standard for nuance/safety, expensive; use for high-stakes slices and periodic audits.

**Production pattern:** automated evals daily + human eval on sampled critical flows.

---

## 4) Prompt engineering patterns + guardrails + testing/regression

### 4.1 Message roles: system vs user vs assistant vs tool

**Why it matters:** Most enterprise reliability comes from **clear instruction hierarchy**.

* **System**: non-negotiable policies, style, safety rules
* **User**: request
* **Assistant**: model output (also includes previous turns; can be attacked via injection)
* **Tool**: outputs from tools (should be treated as untrusted unless verified)

**ASCII hierarchy**

```
SYSTEM (policy + guardrails)
  USER (task)
    TOOL outputs (facts to use, verify)
      ASSISTANT (final response)
```

---

### 4.2 Few-shot examples

**Why it matters:** Examples reduce ambiguity and stabilize format. They’re often better than long prose rules.

Use when:

* output format matters
* edge cases repeat
  Avoid when:
* examples are too specific → model overfits style/content

---

### 4.3 Chain-of-thought (when and when not)

**Why it matters:** Asking for detailed reasoning can improve accuracy, but in production you often don’t want to expose it.

* **Use internally** (or ask for “brief rationale”) for complex reasoning/debug.
* **Don’t require** verbose reasoning in user-visible outputs for:

  * security (leaking policies or tool prompts)
  * compliance (sensitive details)
  * user experience (noise)

**Pattern:** “Think step-by-step internally. Output only final answer + short justification.”

---

### 4.4 ReAct style (reason + act)

**Why it matters:** Best pattern for tool-using agents: decide, call tool, verify, answer.

Minimal production-safe approach:

1. Identify what you need (facts, calculations, retrieval)
2. Call tool(s)
3. Validate tool output (sanity checks)
4. Respond

---

### 4.5 Output format control (JSON, tables)

**Why it matters:** Downstream systems break on free-form text.

Best practice:

* Provide a **JSON schema** (keys, types, constraints)
* Require **valid JSON only**
* Validate server-side; retry with repair prompt if invalid

Pitfall: “Return JSON” without schema → model drifts.

---

### 4.6 Guardrails via prompting (citations, refusal style, “I don’t know”)

**Why it matters:** Guardrails reduce harm and improve trust, but **prompt-only** guardrails are not sufficient.

Prompt-level guardrails:

* Require citations when using retrieved sources
* Define refusal style: “I can’t help with X, but I can help with Y”
* Explicitly allow “I don’t know” and ask clarifying questions
* For RAG: “If not in context, say you don’t know”

Production caveat:

* Use **defense in depth**: policy prompts + moderation + allowlists + output validation.

---

### 4.7 Prompt testing: test cases + regression suites

**Why it matters:** Prompt changes are code changes. Treat prompts like versioned artifacts.

**What to test**

* Happy paths
* Known adversarial prompts (injection, jailbreak)
* Boundary cases (long inputs, empty docs)
* Safety compliance
* JSON validity

**Regression strategy**

* Snapshot expected outputs (or score via rubric)
* Run daily/CI
* Track p50/p95 latency, token usage, refusal rates

**ASCII**

```
prompts/ v12 -> CI eval suite -> metrics diff -> approve/rollback
```

---

### 4.8 Anti-patterns (what breaks production)

* **Vague prompts** (“do the needful”, “explain everything”) → inconsistent output
* **Overlong prompts** (huge policy + examples + docs) → costs ↑, attention dilution
* **Brittle hacks** (prompt injection “magic strings”) → easily bypassed
* **No evals** → you’re flying blind
* **No schema validation** → silent downstream failures

---

## Interview Q&A (concise, strong answers)

1. **Why does tokenization matter in production?**
   Because cost, latency, and context usage scale with tokens; tokenization also affects truncation behavior and multilingual costs.

2. **Pre-training vs instruction tuning vs RLHF/DPO—what’s the difference?**
   Pre-training builds general capability; instruction tuning teaches task-following; RLHF/DPO aligns outputs with human preferences/safety style.

3. **What do temperature and top-p control?**
   They control randomness in token selection. Lower values increase determinism and regression stability; higher values increase diversity but reduce reliability.

4. **Why is “bigger context window” not a full solution?**
   Long context increases cost/latency and models still miss mid-context info. Retrieval quality + summarization + memory discipline usually outperform context stuffing.

5. **How would you reduce LLM cost without losing quality?**
   Reduce input tokens via better retrieval/reranking, cap outputs, cache stable prompts/results, use routing (small model first), and stream responses.

6. **Describe a typical multimodal LLM architecture.**
   A vision encoder converts images to embeddings/tokens that are fed into an LLM along with text tokens; the LLM generates text/tool calls (or multimodal outputs depending on model).

7. **Diffusion vs GAN vs VAE—what’s the key difference?**
   GANs are adversarial and can be unstable; VAEs optimize likelihood with stable training but can blur; diffusion iteratively denoises for high quality but can be slower.

8. **What’s wrong with BLEU/ROUGE for chat assistants?**
   They measure token overlap, not correctness/helpfulness. For assistants you need rubric-based scoring, human evaluation, and/or calibrated LLM-as-judge.

9. **How do you prevent prompt regressions?**
   Version prompts, run a fixed eval suite in CI, validate JSON outputs, track metrics (quality + refusal + latency + tokens), and rollback on regressions.

10. **Prompt-only guardrails are enough?**
    No. Use defense-in-depth: system policies + moderation + tool allowlists + output schema validation + monitoring and red-teaming.

If you want, I can also give you a **mini “production prompt template pack”** (system prompt + tool prompt + JSON schema wrapper + eval checklist) that you can reuse across projects.
