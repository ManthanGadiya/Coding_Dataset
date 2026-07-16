"""Optimization engine — deduplication, compression, balancing.

Source: compiler/09_optimization/
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class OptimizationResult:
    original_size: int
    optimized_size: int
    strategies_applied: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)

    @property
    def compression_ratio(self) -> float:
        if self.original_size == 0:
            return 1.0
        return self.optimized_size / self.original_size

    def to_dict(self) -> dict:
        return {
            "original_size": self.original_size,
            "optimized_size": self.optimized_size,
            "compression_ratio": self.compression_ratio,
            "strategies_applied": self.strategies_applied,
            "details": self.details,
        }


class DeduplicationEngine:
    def deduplicate(self, records: list[dict]) -> tuple[list[dict], int]:
        seen_ids = set()
        unique = []
        removed = 0
        for r in records:
            rid = r.get("id", r.get("metadata", {}).get("id", ""))
            if rid in seen_ids:
                removed += 1
                continue
            seen_ids.add(rid)
            unique.append(r)
        return unique, removed


class OptimizationEngine:
    def __init__(self):
        self.dedup = DeduplicationEngine()

    def optimize(self, records: list[dict]) -> OptimizationResult:
        original = len(records)
        strategies = []
        unique, removed = self.dedup.deduplicate(records)
        if removed:
            strategies.append("deduplication")
        unique, token_removed = self._optimize_tokens(unique)
        if token_removed:
            strategies.append("token_optimization")
        return OptimizationResult(
            original_size=original,
            optimized_size=len(unique),
            strategies_applied=strategies,
            details={"removed_duplicates": removed},
        )

    def _optimize_tokens(self, records: list[dict]) -> tuple[list[dict], int]:
        removed = 0
        for r in records:
            reasoning = r.get("reasoning", [])
            if len(reasoning) > 10:
                r["reasoning"] = reasoning[:10]
                removed += 1
        return records, removed
