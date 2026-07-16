"""Dataset builder — orchestrates full generation pipeline.

Generates worlds → episodes → EKRs → validate → repair → score → optimize → serialize.
"""

from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

from compiler.core.config import CompilerConfig
from compiler.core.constants import Difficulty, Quality, Confidence
from compiler.core.identifiers import make_id
from compiler.core.pipeline import PipelineResult, StageResult, PipelineStage

from compiler.ontology.ekr import EngineeringKnowledgeRecord
from compiler.ontology.graph import KnowledgeGraph
from compiler.ontology.domain import DomainName

from compiler.cognition.engine import ReasoningGraph, ReasoningStep

from compiler.world.generator import WorldGenerator
from compiler.world.models import EngineeringWorld

from compiler.generation.engine import EpisodeGenerator, EpisodeType

from compiler.repair.engine import RepairEngine
from compiler.quality.engine import QualityEngine
from compiler.validation.engine import ValidationEngine
from compiler.optimization.engine import OptimizationEngine
from compiler.serialization.engine import SerializationEngine


@dataclass
class DatasetBuildResult:
    total_worlds: int = 0
    total_episodes: int = 0
    total_ekrs: int = 0
    validated: int = 0
    passed_quality: int = 0
    optimized: int = 0
    serialized_to: list[str] = field(default_factory=list)
    manifest: dict = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    duration_ms: float = 0.0

    def report(self) -> str:
        lines = [
            f"Dataset Build Report",
            f"  Worlds:      {self.total_worlds}",
            f"  Episodes:    {self.total_episodes}",
            f"  EKRs:        {self.total_ekrs}",
            f"  Validated:   {self.validated}",
            f"  Quality:     {self.passed_quality}",
            f"  Optimized:   {self.optimized}",
            f"  Serialized:  {self.serialized_to}",
            f"  Errors:      {len(self.errors)}",
            f"  Duration:    {self.duration_ms:.0f}ms",
        ]
        if self.errors:
            lines.append(f"  Error list:")
            for e in self.errors[:5]:
                lines.append(f"    - {e}")
        return "\n".join(lines)


REASONING_TEMPLATES: dict[str, list[str]] = {
    "bug_fix": [
        "Observe the failing test output",
        "Identify the root cause of the regression",
        "Hypothesize about the incorrect assumption",
        "Validate the fix with unit tests",
        "Reflect on how to prevent similar bugs",
    ],
    "incident_response": [
        "Observe elevated error rates in monitoring",
        "Diagnose the failing service component",
        "Identify the root cause from logs",
        "Implement the mitigation strategy",
        "Document the incident for postmortem",
    ],
    "performance_optimization": [
        "Measure current latency distribution",
        "Identify the bottleneck component",
        "Design optimization approach",
        "Implement the optimization",
        "Benchmark and verify improvement",
    ],
    "architecture_decision": [
        "Analyze the current system limitations",
        "Research alternative architectures",
        "Evaluate trade-offs between options",
        "Select the optimal approach",
        "Document the decision rationale",
    ],
}


class DatasetBuilder:
    def __init__(self, config: CompilerConfig | None = None):
        self.config = config or CompilerConfig.default()
        self.world_gen = WorldGenerator(seed=self.config.seed)
        self.ep_gen = EpisodeGenerator()
        self.repair = RepairEngine()
        self.quality = QualityEngine()
        self.validation = ValidationEngine()
        self.optimization = OptimizationEngine()
        self.serialization = SerializationEngine(output_dir=self.config.output)
        self.graph = KnowledgeGraph()

    def build(self, num_worlds: int = 2, episodes_per_world: int = 3,
              num_ekrs: int = 5) -> DatasetBuildResult:
        import time
        t0 = time.perf_counter()
        result = DatasetBuildResult()
        all_records: list[dict] = []

        domains = list(DomainName)
        episode_types = list(EpisodeType)

        for w_idx in range(num_worlds):
            domain = domains[w_idx % len(domains)]
            world = self.world_gen.generate_world(domain=domain.value)
            result.total_worlds += 1

            for _ in range(episodes_per_world):
                ep_type = episode_types[self.world_gen._rand(len(episode_types))]
                gen_result = self.ep_gen.generate(
                    {"world": world.to_dict(), "domain": domain.value},
                    ep_type, domain.value,
                )
                ekr = gen_result.ekr
                result.total_episodes += 1

                # Inject realistic reasoning
                self._inject_reasoning(ekr, ep_type.value, domain.value)

                # Add decisions
                self._inject_decisions(ekr, ep_type.value)

                # Link knowledge atoms
                ekr.knowledge_atoms = [make_id("KA") for _ in range(self.world_gen._rand(3) + 1)]

                record = ekr.to_dict()

                # Validate
                vr = self.validation.validate(record)
                if vr.all_passed:
                    result.validated += 1

                # Repair if needed
                rr = self.repair.repair(record)
                if rr.success:
                    record["_repaired"] = True

                # Score quality
                qs = self.quality.score(record)
                record["_quality"] = int(qs.overall)
                if int(qs.overall) >= 2:
                    result.passed_quality += 1

                # Skip low quality records
                if int(qs.overall) >= self.config.minimum_quality:
                    all_records.append(record)
                    self.graph.add_node(ekr.id, "ekr", domain=domain.value)
                    result.total_ekrs += 1

        # Optimize
        opt_result = self.optimization.optimize(all_records)
        result.optimized = opt_result.optimized_size
        final_records = all_records[:opt_result.optimized_size]

        # Serialize
        jl = self.serialization.to_jsonl(final_records, "pilot_dataset.jsonl")
        tn = self.serialization.to_toon(final_records, "pilot_dataset.toon")
        result.serialized_to = [jl.path.name, tn.path.name]

        manifest = self.serialization.make_manifest(
            "toon-pilot", "0.1.0", final_records,
        )
        manifest_path = self.config.output / "manifest.json"
        manifest.save(manifest_path)
        result.manifest = manifest.to_dict()

        result.duration_ms = (time.perf_counter() - t0) * 1000
        return result

    def _inject_reasoning(self, ekr: EngineeringKnowledgeRecord, ep_type: str, domain: str):
        templates = REASONING_TEMPLATES.get(ep_type, [
            "Observe the current state",
            "Analyze the situation",
            "Formulate a plan",
        ])
        for step in templates:
            ekr.add_reasoning(
                step.split(" ")[0],
                f"{step} in {domain} context",
                Confidence.C3,
            )
        ekr.add_reasoning("Reflect", f"Lessons learned from {ep_type} in {domain}", Confidence.C4)

    def _inject_decisions(self, ekr: EngineeringKnowledgeRecord, ep_type: str):
        decisions = {
            "bug_fix": ("Apply minimal fix", ["Rewrite module", "Add workaround"], "Fixed with regression test"),
            "incident_response": ("Implement circuit breaker", ["Scale horizontally", "Add caching"], "Circuit breaker deployed"),
            "performance_optimization": ("Add connection pooling", ["Increase threads", "Use async IO"], "Pool size optimized"),
            "architecture_decision": ("Adopt event-driven architecture", ["Monolith", "Microservices"], "Event-driven selected"),
        }
        decision, alternatives, outcome = decisions.get(ep_type, (
            "Use proven solution", ["Custom solution", "Third-party tool"], "Proven solution adopted"
        ))
        ekr.add_decision(decision, f"Context: {ep_type}", alternatives, outcome)
