"""Dataset builder — orchestrates full generation pipeline.

Generates worlds → episodes → EKRs → validate → repair → score → optimize → serialize.
"""

from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

from compiler.core.config import CompilerConfig
from compiler.core.constants import Quality
from compiler.ontology.graph import KnowledgeGraph
from compiler.ontology.domain import DomainName

from compiler.world.generator import WorldGenerator
from compiler.world.models import EngineeringWorld

from compiler.generation.engine import EpisodeGenerator, EpisodeType
from compiler.ingestion.atoms import KnowledgeStore

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





class DatasetBuilder:
    def __init__(self, config: CompilerConfig | None = None,
                 knowledge_store: KnowledgeStore | None = None,
                 knowledge_atoms_path: Path = Path("ingestion/atoms")):
        self.config = config or CompilerConfig.default()
        self.knowledge = knowledge_store or KnowledgeStore(path=knowledge_atoms_path)
        self.world_gen = WorldGenerator(seed=self.config.seed)
        self.ep_gen = EpisodeGenerator(knowledge_store=self.knowledge)
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
        ep_idx = 0

        for w_idx in range(num_worlds):
            domain = domains[w_idx % len(domains)]
            world = self.world_gen.generate_world(domain=domain.value)
            result.total_worlds += 1

            for _ in range(episodes_per_world):
                ep_type = episode_types[ep_idx % len(episode_types)]
                ep_idx += 1
                gen_result = self.ep_gen.generate(
                    {"world": world.to_dict(), "domain": domain.value},
                    ep_type, domain.value,
                )
                ekr = gen_result.ekr
                result.total_episodes += 1

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


