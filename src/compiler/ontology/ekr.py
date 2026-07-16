"""Engineering Knowledge Record — canonical knowledge object.

Source: compiler/01_ontology/07_engineering_knowledge_record.toon
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone

from compiler.core.metadata import Metadata
from compiler.core.constants import Quality, Confidence, Difficulty
from compiler.ontology.entity import Entity


@dataclass
class EngineeringKnowledgeRecord(Entity):
    domain: str = "GEN"
    difficulty: Difficulty = Difficulty.D1
    quality_score: Quality = Quality.Q2
    confidence: Confidence = Confidence.C2
    reasoning: list[dict] = field(default_factory=list)
    decisions: list[dict] = field(default_factory=list)
    tradeoffs: list[dict] = field(default_factory=list)
    evidence: list[dict] = field(default_factory=list)
    knowledge_atoms: list[str] = field(default_factory=list)
    parent_id: str | None = None
    child_ids: list[str] = field(default_factory=list)
    related_ekr_ids: list[str] = field(default_factory=list)

    @classmethod
    def create(cls, name: str, domain: str = "GEN") -> "EngineeringKnowledgeRecord":
        meta = Metadata.create("engineering_knowledge_record", name, domain, "EKR")
        return cls(metadata=meta, domain=domain)

    def add_reasoning(self, operation: str, content: str, confidence: Confidence = Confidence.C2):
        self.reasoning.append({
            "operation": operation, "content": content,
            "confidence": int(confidence),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def add_decision(self, decision: str, context: str, alternatives: list[str], outcome: str):
        self.decisions.append({
            "decision": decision, "context": context,
            "alternatives": alternatives, "outcome": outcome,
        })

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({
            "domain": self.domain, "difficulty": int(self.difficulty),
            "quality_score": int(self.quality_score), "confidence": int(self.confidence),
            "reasoning": self.reasoning, "decisions": self.decisions,
            "tradeoffs": self.tradeoffs, "evidence": self.evidence,
            "knowledge_atoms": self.knowledge_atoms,
            "parent_id": self.parent_id, "child_ids": self.child_ids,
        })
        return d
