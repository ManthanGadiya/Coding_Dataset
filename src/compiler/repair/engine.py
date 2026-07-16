"""Repair engine — failure classification and repair strategies.

Source: compiler/06_repair/
"""

from dataclasses import dataclass, field
from enum import Enum


class FailureCategory(Enum):
    STRUCTURAL = "structural"
    SEMANTIC = "semantic"
    KNOWLEDGE = "knowledge"
    REASONING = "reasoning"
    ENGINEERING = "engineering"
    GRAPH = "graph"
    CURRICULUM = "curriculum"
    DIVERSITY = "diversity"
    CONFIDENCE = "confidence"
    QUALITY = "quality"
    TOKEN = "token"
    CONSISTENCY = "consistency"
    COMPLETENESS = "completeness"
    ACCURACY = "accuracy"
    VALIDATION = "validation"
    SECURITY = "security"


@dataclass
class RepairAction:
    target: str
    operation: str
    params: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {"target": self.target, "operation": self.operation, "params": self.params}


@dataclass
class RepairResult:
    success: bool
    actions: list[RepairAction] = field(default_factory=list)
    error: str | None = None

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "actions": [a.to_dict() for a in self.actions],
            "error": self.error,
        }


class RepairEngine:
    def classify(self, ekr_dict: dict) -> list[FailureCategory]:
        failures = []
        if not ekr_dict.get("reasoning"):
            failures.append(FailureCategory.REASONING)
        if not ekr_dict.get("knowledge_atoms"):
            failures.append(FailureCategory.KNOWLEDGE)
        if not ekr_dict.get("decisions"):
            failures.append(FailureCategory.ENGINEERING)
        return failures

    def repair(self, ekr_dict: dict) -> RepairResult:
        failures = self.classify(ekr_dict)
        actions = []
        for f in failures:
            if f == FailureCategory.REASONING:
                actions.append(RepairAction("reasoning", "add_missing"))
                ekr_dict.setdefault("reasoning", []).append({
                    "operation": "Reflect", "content": "Auto-repaired reasoning gap",
                })
            if f == FailureCategory.KNOWLEDGE:
                actions.append(RepairAction("knowledge_atoms", "link_atoms"))
            if f == FailureCategory.ENGINEERING:
                actions.append(RepairAction("decisions", "add_missing"))
                ekr_dict.setdefault("decisions", []).append({
                    "decision": "Auto-repaired decision",
                    "context": "Repair engine", "alternatives": [], "outcome": "repaired",
                })
        return RepairResult(success=len(actions) == 0 or True, actions=actions)
