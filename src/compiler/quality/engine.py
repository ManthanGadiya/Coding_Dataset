"""Quality engine — multi-dimensional content-aware scoring.

Source: compiler/07_quality/
Produces a true Q0-Q5 distribution by scoring actual content substance.
"""

import re
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


REASONING_OPS = [
    "Observe", "Diagnose", "Hypothesize", "Validate", "Implement",
    "Verify", "Reflect", "Detect", "Triage", "Mitigate", "Resolve",
    "Document", "Prevent", "Measure", "Analyze", "Design", "Benchmark",
    "Deploy", "Research", "Evaluate", "Decide", "Review", "Plan",
    "Assess", "Prioritize", "Identify", "Reproduce", "Isolate",
    "Context", "Explore", "Compare", "Propose",
]


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

    # ── helpers ──────────────────────────────────────────────────

    @staticmethod
    def _has_substance(text: str) -> float:
        tokens = text.split()
        domain_terms = [
            "cluster", "database", "cache", "network", "api", "service",
            "deploy", "config", "metric", "alert", "incident", "query",
            "index", "shard", "replica", "latency", "throughput", "timeout",
            "failover", "backup", "pipeline", "queue", "stream", "batch",
            "monitor", "container", "orchestrator", "partition", "replication",
        ]
        if len(tokens) < 5:
            return 0.0
        content_len = min(1.0, len(tokens) / 15)
        domain_hits = sum(1 for t in domain_terms if t in text.lower())
        domain_bonus = min(0.5, domain_hits * 0.1)
        return min(1.5, content_len + domain_bonus)

    @staticmethod
    def _avg_substance(items: list[dict], key: str = "content") -> float:
        if not items:
            return 0.0
        scores = [QualityEngine._has_substance(i.get(key, "")) for i in items]
        return sum(scores) / len(scores)

    @staticmethod
    def _concrete_detail_ratio(text: str) -> float:
        numbers = len(re.findall(r'\d+', text))
        tech = len(re.findall(r'\b[A-Z][A-Za-z0-9+/]{2,}\b', text))
        return min(1.0, (numbers + tech * 0.5) / 10)

    # ── dimension scorers ────────────────────────────────────────

    def _score_knowledge_density(self, ekr: dict) -> float:
        reasoning = ekr.get("reasoning", [])
        decisions = ekr.get("decisions", [])
        evidence = ekr.get("evidence", [])
        atoms = ekr.get("knowledge_atoms", [])

        reasoning_substance = self._avg_substance(reasoning)
        atom_bonus = min(2.0, len(atoms) * 0.5)
        ev_bonus = min(1.0, len(evidence) * 0.3)
        decision_bonus = min(1.5, len(decisions) * 0.5)
        tradeoff_bonus = min(0.5, len(ekr.get("tradeoffs", [])) * 0.3)
        ref_bonus = 0
        for s in reasoning:
            if "[Ref:" in s.get("content", ""):
                ref_bonus = min(1.0, ref_bonus + 0.3)

        base = reasoning_substance + atom_bonus + ev_bonus + decision_bonus + tradeoff_bonus + ref_bonus
        return min(5.0, max(0.0, base))

    def _score_reasoning_depth(self, ekr: dict) -> float:
        reasoning = ekr.get("reasoning", [])
        if not reasoning:
            return 0.0
        ops = [s.get("operation", "") for s in reasoning]
        unique_ops = set(ops)
        chain_len = len(reasoning)
        substance = self._avg_substance(reasoning)

        base = min(3.0, chain_len * 0.4)
        variety_bonus = min(1.0, len(unique_ops) * 0.15)
        depth_bonus = substance * 1.0
        return min(5.0, base + variety_bonus + depth_bonus)

    def _score_engineering_quality(self, ekr: dict) -> float:
        decisions = ekr.get("decisions", [])
        evidence = ekr.get("evidence", [])
        tradeoffs = ekr.get("tradeoffs", [])
        reasoning = ekr.get("reasoning", [])

        base = 0.5
        if not decisions:
            return base  # no decisions = minimal engineering quality

        alt_count = sum(1 for d in decisions if d.get("alternatives"))
        reasoning_scores = [len(d.get("outcome", d.get("reasoning", ""))) for d in decisions]
        avg_len = sum(reasoning_scores) / len(reasoning_scores) if reasoning_scores else 0

        dec_score = min(2.5, len(decisions) * 0.8 + alt_count * 0.3 + avg_len / 80)
        ev_base = min(0.5, len(evidence) * 0.15)
        tradeoff_bonus = min(0.5, len(tradeoffs) * 0.2)
        depth_bonus = min(0.5, len(reasoning) * 0.08)

        return min(5.0, base + dec_score + ev_base + tradeoff_bonus + depth_bonus)

    def _score_diversity(self, ekr: dict) -> float:
        reasoning = ekr.get("reasoning", [])
        ops = set(s.get("operation", "") for s in reasoning)
        evidence_types = set(e.get("type", "") for e in ekr.get("evidence", []))

        op_div = min(2.5, len(ops) * 0.3)
        ev_div = min(1.0, len(evidence_types) * 0.3)
        has_decisions = 0.5 if ekr.get("decisions") else 0
        has_tradeoffs = 0.5 if ekr.get("tradeoffs") else 0
        domain_bonus = 0.5 if ekr.get("domain") else 0
        return min(5.0, op_div + ev_div + has_decisions + has_tradeoffs + domain_bonus)

    def _score_realism(self, ekr: dict) -> float:
        reasoning = ekr.get("reasoning", [])
        evidence = ekr.get("evidence", [])
        all_text = " ".join(s.get("content", "") for s in reasoning)
        all_text += " ".join(e.get("content", "") for e in evidence)

        detail = self._concrete_detail_ratio(all_text)
        ev_count = min(1.5, len(evidence) * 0.5)
        subst = min(1.5, self._avg_substance(reasoning) * 0.8)
        ev_types = len(set(e.get("type", "") for e in evidence))
        ev_variety = min(0.5, ev_types * 0.15)
        return min(5.0, detail + ev_count + subst + ev_variety + 0.5)

    def _score_novelty(self, ekr: dict) -> float:
        difficulty = ekr.get("difficulty", 1)
        reasoning = ekr.get("reasoning", [])
        ops = set(s.get("operation", "") for s in reasoning)
        tradeoffs = ekr.get("tradeoffs", [])

        diff_bonus = min(2.0, difficulty * 0.5)
        if difficulty >= 5:
            diff_bonus = min(2.5, diff_bonus + 0.5)
        op_bonus = min(1.5, len(ops) * 0.15)
        subst = min(1.5, self._avg_substance(reasoning))
        tradeoff_bonus = min(0.5, len(tradeoffs) * 0.25)
        return min(5.0, diff_bonus + op_bonus + subst + tradeoff_bonus)

    def _score_educational_value(self, ekr: dict) -> float:
        reasoning = ekr.get("reasoning", [])
        decisions = ekr.get("decisions", [])
        tradeoffs = ekr.get("tradeoffs", [])
        all_text = " ".join(s.get("content", "") for s in reasoning)
        all_text += " ".join(d.get("outcome", d.get("reasoning", "")) for d in decisions)

        subst = self._has_substance(all_text)
        step_count = min(1.0, len(reasoning) * 0.15)
        decision_count = min(1.0, len(decisions) * 0.4)
        tradeoff_bonus = min(0.5, len(tradeoffs) * 0.25)

        explainers = ["because", "therefore", "since", "leads to", "causes", "requires"]
        explanation_score = sum(1 for e in explainers if e in all_text.lower()) * 0.3
        explanation_bonus = min(1.5, explanation_score)
        return min(5.0, max(0.5, subst + step_count + decision_count + tradeoff_bonus + explanation_bonus))

    def _score_completeness(self, ekr: dict) -> float:
        score = 0.5
        if ekr.get("metadata"):
            score += 0.5
        if ekr.get("reasoning"):
            score += 0.8
        if ekr.get("decisions"):
            score += 0.8
        if ekr.get("evidence"):
            score += 0.6
        if ekr.get("knowledge_atoms"):
            score += 0.6
        if ekr.get("lifecycle"):
            score += 0.4
        if ekr.get("difficulty", 0) > 0:
            score += 0.3
        if ekr.get("tradeoffs"):
            score += 0.4
        if ekr.get("domain", "") in ("", "GEN"):
            score -= 0.5
        return min(5.0, max(0.0, score))

    def _score_consistency(self, ekr: dict) -> float:
        meta = ekr.get("metadata", {})
        domain = ekr.get("domain", "")
        name = ekr.get("name", "")
        reasoning = ekr.get("reasoning", [])

        score = 2.0
        if meta.get("domain") and domain and meta["domain"] == domain:
            score += 1.0
        if domain.lower() in name.lower():
            score += 0.5
        ops = {s.get("operation", "") for s in reasoning}
        if len(ops) >= 5:
            score += 0.8
        elif len(ops) >= 3:
            score += 0.4
        has_ref = any("[Ref:" in s.get("content", "") for s in reasoning)
        if has_ref:
            score += 0.5
        return min(5.0, score)

    def _score_coherence(self, ekr: dict) -> float:
        reasoning = ekr.get("reasoning", [])
        if not reasoning:
            return 0.0

        ops = [s.get("operation", "") for s in reasoning]
        all_content = " ".join(s.get("content", "") for s in reasoning)
        subst = self._has_substance(all_content)

        flow = len([o for o in ops if o in REASONING_OPS]) / max(1, len(ops))
        chain_len = len(reasoning)
        if chain_len >= 10:
            chain_bonus = 2.0
        elif chain_len >= 7:
            chain_bonus = 1.5
        else:
            chain_bonus = min(1.5, chain_len * 0.2)
        return min(5.0, max(0.5, flow * 2.0 + chain_bonus + subst * 0.5))

    def _score_dimension(self, dim: str, ekr_dict: dict) -> float:
        dispatch = {
            "knowledge_density": self._score_knowledge_density,
            "reasoning_depth": self._score_reasoning_depth,
            "engineering_quality": self._score_engineering_quality,
            "diversity": self._score_diversity,
            "realism": self._score_realism,
            "novelty": self._score_novelty,
            "educational_value": self._score_educational_value,
            "completeness": self._score_completeness,
            "consistency": self._score_consistency,
            "coherence": self._score_coherence,
        }
        scorer = dispatch.get(dim)
        if scorer is None:
            return 3.0
        return scorer(ekr_dict)
