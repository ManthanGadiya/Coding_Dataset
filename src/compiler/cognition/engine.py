"""Cognition engine — reasoning primitives execution.

Source: compiler/02_cognition/
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone

from compiler.core.constants import Confidence


REASONING_PRIMITIVES = [
    "Observe", "Identify", "Classify", "Compare", "Relate",
    "Infer", "Predict", "Hypothesize", "Validate", "Measure",
    "Diagnose", "Explain", "Generalize", "Specialize", "Optimize",
    "Decide", "Reflect", "Transfer", "Synthesize", "Decompose",
]


@dataclass
class ReasoningStep:
    operation: str
    content: str
    confidence: Confidence = Confidence.C2
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    dependencies: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "operation": self.operation,
            "content": self.content,
            "confidence": int(self.confidence),
            "timestamp": self.timestamp,
        }


@dataclass
class ReasoningGraph:
    steps: list[ReasoningStep] = field(default_factory=list)

    def add(self, operation: str, content: str, confidence: Confidence = Confidence.C2) -> ReasoningStep:
        step = ReasoningStep(operation=operation, content=content, confidence=confidence)
        self.steps.append(step)
        return step

    def to_dict(self) -> list[dict]:
        return [s.to_dict() for s in self.steps]


@dataclass
class DecisionRecord:
    decision: str
    context: str
    alternatives: list[str]
    evidence: list[str]
    outcome: str
    confidence: Confidence = Confidence.C2
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {
            "decision": self.decision, "context": self.context,
            "alternatives": self.alternatives, "evidence": self.evidence,
            "outcome": self.outcome, "confidence": int(self.confidence),
            "timestamp": self.timestamp,
        }


@dataclass
class Hypothesis:
    statement: str
    evidence_for: list[str] = field(default_factory=list)
    evidence_against: list[str] = field(default_factory=list)
    confidence: Confidence = Confidence.C1
    status: str = "proposed"  # proposed, testing, confirmed, rejected

    def to_dict(self) -> dict:
        return {
            "statement": self.statement,
            "evidence_for": self.evidence_for,
            "evidence_against": self.evidence_against,
            "confidence": int(self.confidence),
            "status": self.status,
        }
