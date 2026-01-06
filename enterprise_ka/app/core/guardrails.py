import re
from dataclasses import dataclass


@dataclass(frozen=True)
class GuardrailFinding:
    category: str
    action: str
    detail: str

@dataclass
class GuardrailDecision:
    blocked: bool
    findings: list[GuardrailFinding]
    message: str | None = None

class Guardrails:
    """
    Lightweight, rule-based guardrails to deflect obviously unsafe or irrelevant queries
    before they reach the LLM. This is intentionally simple (no network calls) to keep
    the PoC self-contained.
    """
    def __init__(self, min_relevance_score: float = 0.22):
        self.min_relevance_score = min_relevance_score
        self.denylist_patterns = [
            ("prompt_injection", re.compile(r"ignore (all )?previous instructions|reset the rules", re.I)),
            ("credential_exfiltration", re.compile(r"(password|api key|secret key|token|credential)", re.I)),
            ("destructive_ops", re.compile(r"(drop (table|database)|rm -rf|format c:|shutdown)", re.I)),
        ]
        self.off_topic_keywords = [
            "movie", "recipe", "song", "weather", "politics", "sports", "celebrity", "stock price"
        ]

    def pre_screen(self, question: str) -> GuardrailDecision:
        q = question.lower()
        findings: list[GuardrailFinding] = []

        for category, pattern in self.denylist_patterns:
            if pattern.search(q):
                findings.append(
                    GuardrailFinding(
                        category=category,
                        action="block",
                        detail="Rejected due to unsafe or system-override intent.",
                    )
                )
                return GuardrailDecision(
                    blocked=True,
                    findings=findings,
                    message="This assistant only answers enterprise documentation questions; this request was blocked by safety rules.",
                )

        for keyword in self.off_topic_keywords:
            if keyword in q:
                findings.append(
                    GuardrailFinding(
                        category="off_topic",
                        action="warn",
                        detail=f"Question appears unrelated to enterprise docs (keyword: {keyword}).",
                    )
                )
                break

        return GuardrailDecision(blocked=False, findings=findings)

    def relevance_guard(self, top_score: float) -> GuardrailFinding | None:
        if top_score < self.min_relevance_score:
            return GuardrailFinding(
                category="low_relevance",
                action="warn",
                detail=f"Top match score {top_score:.2f} is below threshold {self.min_relevance_score}.",
            )
        return None
