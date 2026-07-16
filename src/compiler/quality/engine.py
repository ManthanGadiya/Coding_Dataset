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
        if dim == "reasoning_depth":
            return min(5.0, len(ekr_dict.get("reasoning", [])) * 1.0)
        if dim == "engineering_quality":
            return min(5.0, len(ekr_dict.get("decisions", [])) * 1.5)
        if dim == "knowledge_density":
            return min(5.0, len(ekr_dict.get("knowledge_atoms", [])) * 1.5 + 1.0)
        if dim == "completeness":
            return 4.0 if ekr_dict.get("metadata") and ekr_dict.get("reasoning") else 2.0
        return 3.0
