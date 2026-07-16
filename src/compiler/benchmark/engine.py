"""Benchmark suite — measures quality, diversity, coverage, and throughput."""

from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from compiler.generation.engine import EpisodeGenerator, EpisodeType
from compiler.quality.engine import QualityEngine


@dataclass
class BenchmarkReport:
    quality_distribution: dict[int, int] = field(default_factory=dict)
    domain_coverage: dict[str, int] = field(default_factory=dict)
    episode_type_coverage: dict[str, int] = field(default_factory=dict)
    avg_reasoning_steps: float = 0.0
    avg_decisions: float = 0.0
    avg_evidence: float = 0.0
    avg_atom_refs: float = 0.0
    throughput_ekrs_per_sec: float = 0.0
    atom_ref_rate: float = 0.0
    unique_operations: int = 0
    total_ekrs: int = 0
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "quality_distribution": self.quality_distribution,
            "domain_coverage": self.domain_coverage,
            "episode_type_coverage": self.episode_type_coverage,
            "avg_reasoning_steps": round(self.avg_reasoning_steps, 2),
            "avg_decisions": round(self.avg_decisions, 2),
            "avg_evidence": round(self.avg_evidence, 2),
            "avg_atom_refs": round(self.avg_atom_refs, 2),
            "throughput_ekrs_per_sec": round(self.throughput_ekrs_per_sec, 1),
            "atom_ref_rate": round(self.atom_ref_rate, 3),
            "unique_operations": self.unique_operations,
            "total_ekrs": self.total_ekrs,
        }

    def summary(self) -> str:
        lines = [
            "=" * 50,
            "  Benchmark Report",
            "=" * 50,
            f"  Total EKRs:       {self.total_ekrs}",
            f"  Throughput:       {self.throughput_ekrs_per_sec:.0f} EKRs/sec",
            "",
            "  Quality Distribution:",
        ]
        for q in sorted(self.quality_distribution):
            pct = 100 * self.quality_distribution[q] / max(1, self.total_ekrs)
            lines.append(f"    Q{q}: {self.quality_distribution[q]:>6} ({pct:5.1f}%)")
        lines += [
            "",
            f"  Avg reasoning steps: {self.avg_reasoning_steps:.1f}",
            f"  Avg decisions:       {self.avg_decisions:.1f}",
            f"  Avg evidence items:  {self.avg_evidence:.1f}",
            f"  Avg atom refs:       {self.avg_atom_refs:.1f}",
            f"  Atom ref rate:       {self.atom_ref_rate:.1%}",
            f"  Unique operations:   {self.unique_operations}",
            "",
            "  Domain Coverage:",
        ]
        for domain, count in sorted(self.domain_coverage.items(), key=lambda x: -x[1]):
            lines.append(f"    {domain:30s}: {count}")
        lines += [
            "",
            "  Episode Type Coverage:",
        ]
        for et, count in sorted(self.episode_type_coverage.items(), key=lambda x: -x[1]):
            lines.append(f"    {et:30s}: {count}")
        if self.errors:
            lines += ["", "  Errors:"]
            for e in self.errors[:5]:
                lines.append(f"    - {e}")
        lines.append("=" * 50)
        return "\n".join(lines)


class BenchmarkSuite:
    def __init__(self, knowledge_store=None):
        self.generator = EpisodeGenerator(knowledge_store=knowledge_store)
        self.quality = QualityEngine()

    def run(self, num_ekrs: int = 1000, domains: list[str] | None = None,
            seed: int = 42) -> BenchmarkReport:
        import random
        import time
        rng = random.Random(seed)
        report = BenchmarkReport(total_ekrs=num_ekrs)
        types = list(EpisodeType)

        all_domains = domains or [
            "Systems", "Databases", "Architecture", "Networking", "DevOps",
            "Security", "Performance", "Testing", "Cloud", "Distributed_Systems",
            "Software_Architecture", "AI_Engineering", "Production_Engineering",
            "Human_Factors", "Foundations", "Algorithms",
        ]

        quality_counter: Counter[int] = Counter()
        domain_counter: Counter[str] = Counter()
        type_counter: Counter[str] = Counter()
        total_reasoning = 0
        total_decisions = 0
        total_evidence = 0
        total_atom_refs = 0
        total_ref_steps = 0
        all_operations: set[str] = set()

        t0 = time.perf_counter()
        for i in range(num_ekrs):
            try:
                d = rng.choice(all_domains)
                et = rng.choice(types)
                diff = rng.choice([1, 2, 3, 4, 5])
                result = self.generator.generate(
                    {"domain": d, "difficulty": diff}, et, d
                )
                ekr_dict = result.to_dict()["ekr"]
                reasoning = ekr_dict.get("reasoning", [])
                decisions = ekr_dict.get("decisions", [])
                evidence = ekr_dict.get("evidence", [])
                atoms = ekr_dict.get("knowledge_atoms", [])

                score = self.quality.score(ekr_dict)
                quality_counter[int(score.overall)] += 1
                domain_counter[d] += 1
                type_counter[et.value] += 1
                total_reasoning += len(reasoning)

                refs = sum(1 for s in reasoning if "[Ref:" in s.get("content", ""))
                total_atom_refs += len(atoms)
                total_ref_steps += refs

                total_decisions += len(decisions)
                total_evidence += len(evidence)

                for s in reasoning:
                    all_operations.add(s.get("operation", ""))

            except Exception as e:
                report.errors.append(f"EKR {i}: {e}")

        elapsed = time.perf_counter() - t0

        report.quality_distribution = dict(sorted(quality_counter.items()))
        report.domain_coverage = dict(domain_counter)
        report.episode_type_coverage = dict(type_counter)
        report.avg_reasoning_steps = total_reasoning / max(1, num_ekrs)
        report.avg_decisions = total_decisions / max(1, num_ekrs)
        report.avg_evidence = total_evidence / max(1, num_ekrs)
        report.avg_atom_refs = total_atom_refs / max(1, num_ekrs)
        report.atom_ref_rate = total_ref_steps / max(1, total_reasoning)
        report.unique_operations = len(all_operations)
        report.throughput_ekrs_per_sec = num_ekrs / max(0.001, elapsed)

        return report

    def run_at_scale(self, target_size: int = 1_000_000, domains: list[str] | None = None,
                     seed: int = 42, checkpoint_interval: int = 100_000) -> BenchmarkReport:
        import random
        import time
        import json
        from pathlib import Path

        rng = random.Random(seed)
        report = BenchmarkReport(total_ekrs=0)
        types = list(EpisodeType)
        all_domains = domains or [
            "Systems", "Databases", "Architecture", "Networking", "DevOps",
            "Security", "Performance", "Testing", "Cloud", "Distributed_Systems",
            "Software_Architecture", "AI_Engineering", "Production_Engineering",
            "Human_Factors", "Foundations", "Algorithms",
        ]

        quality_counter: Counter[int] = Counter()
        domain_counter: Counter[str] = Counter()
        type_counter: Counter[str] = Counter()
        total_reasoning = 0
        total_decisions = 0
        total_evidence = 0
        total_atom_refs = 0
        total_ref_steps = 0
        all_operations: set[str] = set()
        all_records: list[dict] = []

        checkpoint_dir = Path("build/checkpoints")
        checkpoint_dir.mkdir(parents=True, exist_ok=True)

        t0 = time.perf_counter()
        last_checkpoint = 0

        for i in range(target_size):
            try:
                d = rng.choice(all_domains)
                et = rng.choice(types)
                diff = rng.choice([1, 2, 3, 4, 5])
                result = self.generator.generate(
                    {"domain": d, "difficulty": diff}, et, d
                )
                ekr_dict = result.to_dict()["ekr"]
                reasoning = ekr_dict.get("reasoning", [])
                decisions = ekr_dict.get("decisions", [])
                evidence = ekr_dict.get("evidence", [])
                atoms = ekr_dict.get("knowledge_atoms", [])

                score = self.quality.score(ekr_dict)
                quality_counter[int(score.overall)] += 1
                domain_counter[d] += 1
                type_counter[et.value] += 1
                total_reasoning += len(reasoning)
                refs = sum(1 for s in reasoning if "[Ref:" in s.get("content", ""))
                total_atom_refs += len(atoms)
                total_ref_steps += refs
                total_decisions += len(decisions)
                total_evidence += len(evidence)
                for s in reasoning:
                    all_operations.add(s.get("operation", ""))
                all_records.append(ekr_dict)

                if (i + 1) % checkpoint_interval == 0:
                    ckpt = checkpoint_dir / f"checkpoint_{i+1}.jsonl"
                    with open(ckpt, "w") as f:
                        for rec in all_records[-checkpoint_interval:]:
                            f.write(json.dumps(rec) + "\n")
                    elapsed = time.perf_counter() - t0
                    rate = (i + 1) / max(0.001, elapsed)
                    print(f"  Checkpoint {i+1}/{target_size} — {rate:.0f} EKRs/sec")

            except Exception as e:
                report.errors.append(f"EKR {i}: {e}")

        elapsed = time.perf_counter() - t0

        report.total_ekrs = target_size
        report.quality_distribution = dict(sorted(quality_counter.items()))
        report.domain_coverage = dict(domain_counter)
        report.episode_type_coverage = dict(type_counter)
        report.avg_reasoning_steps = total_reasoning / max(1, target_size)
        report.avg_decisions = total_decisions / max(1, target_size)
        report.avg_evidence = total_evidence / max(1, target_size)
        report.avg_atom_refs = total_atom_refs / max(1, target_size)
        report.atom_ref_rate = total_ref_steps / max(1, total_reasoning)
        report.unique_operations = len(all_operations)
        report.throughput_ekrs_per_sec = target_size / max(0.001, elapsed)

        return report, all_records
