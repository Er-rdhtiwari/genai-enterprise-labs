"use client";

import { useMemo, useState } from "react";

type Citation = {
  doc_id: string;
  chunk_id: string;
  score: number;
};

type GuardrailEvent = {
  category: string;
  action: string;
  detail: string;
};

type PromptTrace = {
  template: string;
  version: string;
  description: string;
  system_prompt?: string;
  user_prompt?: string;
};

type AskResponse = {
  request_id: string;
  answer: string;
  citations: Citation[];
  latency_ms: number;
  prompt?: PromptTrace;
  guardrails: GuardrailEvent[];
};

const defaultApiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function Home() {
  const [apiUrl, setApiUrl] = useState(defaultApiUrl);
  const [question, setQuestion] = useState("What is the SEV1 escalation procedure?");
  const [promptTemplate, setPromptTemplate] = useState("grounded_concise");
  const [debugPrompt, setDebugPrompt] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AskResponse | null>(null);

  const hasGuardrails = useMemo(() => (result?.guardrails?.length || 0) > 0, [result]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setResult(null);
    setLoading(true);

    try {
      const response = await fetch(`${apiUrl.replace(/\/$/, "")}/v1/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question,
          prompt_template: promptTemplate,
          debug_prompt: debugPrompt,
        }),
      });

      if (!response.ok) {
        const msg = await response.text();
        throw new Error(msg || `Request failed with ${response.status}`);
      }

      const data: AskResponse = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unexpected error");
    } finally {
      setLoading(false);
    }
  }

  const quickQuestions = [
    "What is the SEV1 escalation procedure?",
    "What should we avoid logging according to policy?",
    "When is RCA required after an incident?",
  ];

  return (
    <div className="stack">
      <div className="callout">
        <span>⚡</span>
        <div>
          <div className="tagline">
            <span className="pill">Prompt-safe</span>
            <span className="pill">RAG-backed</span>
            <span className="pill">Audit-friendly</span>
          </div>
          <div className="muted">
            Ask internal questions, swap prompt templates, and inspect guardrails without leaving the browser.
          </div>
        </div>
      </div>

      <div className="panel">
        <form className="stack" onSubmit={handleSubmit}>
          <div className="grid">
            <div className="stack">
              <div className="field">
                <label>Backend URL</label>
                <input
                  className="input"
                  value={apiUrl}
                  onChange={(e) => setApiUrl(e.target.value)}
                  placeholder="http://localhost:8000"
                  required
                />
                <span className="muted">FastAPI base URL (no trailing slash).</span>
              </div>
              <div className="field">
                <label>Question</label>
                <textarea
                  className="textarea"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  minLength={3}
                  maxLength={4000}
                  required
                />
                <div className="row">
                  {quickQuestions.map((q) => (
                    <button
                      key={q}
                      className="pill"
                      type="button"
                      onClick={() => setQuestion(q)}
                      style={{ border: "none", cursor: "pointer" }}
                    >
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            </div>
            <div className="stack">
              <div className="field">
                <label>Prompt template</label>
                <select
                  className="select"
                  value={promptTemplate}
                  onChange={(e) => setPromptTemplate(e.target.value)}
                >
                  <option value="grounded_concise">grounded_concise</option>
                  <option value="grounded_reasoned">grounded_reasoned</option>
                </select>
                <span className="muted">
                  Compare tone/structure; enable debug to see rendered system + user prompts.
                </span>
              </div>
              <div className="field">
                <label className="toggle">
                  <input
                    type="checkbox"
                    checked={debugPrompt}
                    onChange={(e) => setDebugPrompt(e.target.checked)}
                  />
                  Return rendered prompts (debug)
                </label>
              </div>
              <button className="button" type="submit" disabled={loading}>
                {loading ? "Asking..." : "Ask assistant"}
              </button>
              {error ? <div className="error">{error}</div> : null}
            </div>
          </div>
        </form>
      </div>

      {result ? (
        <div className="grid">
          <div className="panel stack">
            <div className="result-title">
              <div>
                <div className="muted">Answer</div>
                <div className="badge">Latency: {result.latency_ms} ms</div>
              </div>
              <div className="pill">Request ID: {result.request_id || "n/a"}</div>
            </div>
            <div className="response-block">{result.answer}</div>
            <div className="divider" />
            <div>
              <div className="muted">Citations</div>
              {result.citations?.length ? (
                <ul className="list">
                  {result.citations.map((c) => (
                    <li key={c.chunk_id} className="muted">
                      [{c.doc_id}::{c.chunk_id}] — score {c.score.toFixed(3)}
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="muted">None returned</div>
              )}
            </div>
          </div>

          <div className="panel stack">
            <div className="result-title">
              <div className="muted">Prompt trace</div>
              <div className="badge">{result.prompt?.template || "n/a"}</div>
            </div>
            <div className="row">
              <span className="pill">Version: {result.prompt?.version || "-"}</span>
              {result.prompt?.description ? <span className="pill">{result.prompt.description}</span> : null}
              <span className="pill">Debug: {debugPrompt ? "on" : "off"}</span>
            </div>
            {debugPrompt ? (
              <>
                <div className="field">
                  <label>System prompt</label>
                  <pre className="response-block muted">{result.prompt?.system_prompt || "n/a"}</pre>
                </div>
                <div className="field">
                  <label>User prompt</label>
                  <pre className="response-block muted">{result.prompt?.user_prompt || "n/a"}</pre>
                </div>
              </>
            ) : (
              <div className="muted">Enable debug to view rendered prompts.</div>
            )}
            <div className="divider" />
            <div className="field">
              <label>Guardrails</label>
              {hasGuardrails ? (
                <ul className="list">
                  {result.guardrails.map((g, idx) => (
                    <li key={`${g.category}-${idx}`} className="muted">
                      <span className="pill">{g.action.toUpperCase()}</span> {g.category}: {g.detail}
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="muted">None triggered.</div>
              )}
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
