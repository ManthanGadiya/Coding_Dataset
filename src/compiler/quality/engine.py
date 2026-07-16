"""Quality engine — multi-dimensional scoring.

Source: compiler/07_quality/
"""

from dataclasses import dataclass, field

from compiler.core.constants import Quality


@dataclass
class QualityScore:
    overall: Quality
    dimensions: dict[str, float] = field(default_factory=dict)
    details: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "overall": int(self.overall),
            "dimensions": self.dimensions,
            "details": self.details,
        }


class QualityEngine:
    DIMENSIONS = [
        "knowledge_density", "reasoning_depth", "engineering_quality",
        "diversity", "realism", "novelty", "educational_value",
        "completeness", "consistency", "coherence",
    ]

    def score(self, ekr_dict: dict) -> QualityScore:
        dims = {}
        scores = []

        for dim in self.DIMENSIONS:
            s = self._score_dimension(dim, ekr_dict)
            dims[dim] = s
            scores.append(s)

        avg = sum(scores) / len(scores) if scores else 0.0
        if avg >= 4.5:
            overall = Quality.Q5
        elif avg >= 3.5:
            overall = Quality.Q4
        elif avg >= 2.5:
            overall = Quality.Q3
        elif avg >= 1.5:
            overall = Quality.Q2
        elif avg >= 0.5:
            overall = Quality.Q1
        else:
            overall = Quality.Q0

        return QualityScore(overall=overall, dimensions=dims)

    def _score_dimension(self, dim: str, ekr_dict: dict) -> float:
        reasoning = ekr_dict.get("reasoning", [])
        decisions = ekr_dict.get("decisions", [])
        evidence = ekr_dict.get("evidence", [])
        tradeoffs = ekr_dict.get("tradeoffs", [])
        atoms = ekr_dict.get("knowledge_atoms", [])
        difficulty = ekr_dict.get("difficulty", 1)
        domain = ekr_dict.get("domain", "")

        if dim == "reasoning_depth":
            ops = set(s.get("operation", "") for s in reasoning)
            base = min(5.0, len(reasoning))
            bonus = 0.5 if len(ops) >= 5 else 0
            return min(5.0, base + bonus)

        if dim == "engineering_quality":
            base = min(5.0, len(decisions) * 1.2)
            if any(d.get("alternatives") for d in decisions):
                base = min(5.0, base + 0.5)
            return base

        if dim == "knowledge_density":
            return min(5.0, len(atoms) * 1.2 + len(evidence) * 0.3)

        if dim == "completeness":
            score = 2.0
            if ekr_dict.get("metadata"):
                score += 1.0
            if reasoning:
                score += 0.5
            if decisions:
                score += 0.5
            if evidence:
                score += 0.5
            if atoms:
                score += 0.5
            return min(5.0, score)

        if dim == "diversity":
            ops = set(s.get("operation", "") for s in reasoning)
            return min(5.0, len(ops) * 0.6 + 1.0)

        if dim == "realism":
            if evidence:
                return min(5.0, len(evidence) * 0.8 + 2.0)
            return 2.0

        if dim == "novelty":
            if difficulty >= 3:
                return min(5.0, difficulty * 0.8 + 1.0)
            return 2.0

        if dim == "educational_value":
            return min(5.0, len(reasoning) * 0.4 + len(decisions) * 0.5 + 1.0)

        if dim == "consistency":
            meta = ekr_dict.get("metadata", {})
            if meta.get("domain") and domain and meta["domain"] == domain:
                return 4.5
            return 3.0

        if dim == "coherence":
            if reasoning and decisions:
                return 4.0
            return 2.5

        return 3.0
