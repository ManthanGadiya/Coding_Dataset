"""Pipeline orchestration.

Source: compiler/00_core/03_pipeline.toon
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Protocol

from .config import CompilerConfig, PassConfig
from .constants import PipelineStage


class PipelinePass(Protocol):
    name: str
    def execute(self, ctx: dict) -> dict: ...


@dataclass
class StageResult:
    stage: PipelineStage
    success: bool
    duration_ms: float
    output: dict = field(default_factory=dict)
    error: str | None = None


@dataclass
class PipelineResult:
    status: str
    success: bool
    stages: list[StageResult] = field(default_factory=list)
    started_at: str = ""
    finished_at: str = ""
    errors: list[str] = field(default_factory=list)


class CompilerPipeline:
    def __init__(self, config: CompilerConfig):
        self.config = config
        self.ctx: dict = {}
        self._stages: list[tuple[PipelineStage, PassConfig]] = self._build_stages()

    def _build_stages(self) -> list[tuple[PipelineStage, PassConfig]]:
        m = {
            PipelineStage.INITIALIZATION: "ingestion",
            PipelineStage.KNOWLEDGE_ACQUISITION: "ingestion",
            PipelineStage.KNOWLEDGE_PARSING: "parsing",
            PipelineStage.ONTOLOGY_MAPPING: "ontology",
            PipelineStage.KNOWLEDGE_GRAPH_CONSTRUCTION: "ontology",
            PipelineStage.COGNITION_ENRICHMENT: "cognition",
            PipelineStage.CURRICULUM_PLANNING: "curriculum",
            PipelineStage.WORLD_GENERATION: "world",
            PipelineStage.EPISODE_GENERATION: "generation",
            PipelineStage.EKR_GENERATION: "generation",
            PipelineStage.ARTIFACT_GENERATION: "generation",
            PipelineStage.REPAIR: "repair",
            PipelineStage.QUALITY_ANALYSIS: "quality",
            PipelineStage.VALIDATION: "validation",
            PipelineStage.OPTIMIZATION: "optimization",
            PipelineStage.SERIALIZATION: "serialization",
            PipelineStage.RELEASE: "serialization",
        }
        return [(s, self.config.passes.get(k, PassConfig())) for s, k in m.items()]

    def run(self) -> PipelineResult:
        started = datetime.now(timezone.utc).isoformat()
        self.ctx["config"] = self.config
        self.ctx["started_at"] = started
        results: list[StageResult] = []
        errors: list[str] = []
        ok = True

        for stage, cfg in self._stages:
            if not cfg.enabled and not cfg.mandatory:
                continue
            r = self._exec(stage)
            results.append(r)
            if not r.success:
                ok = False
                errors.append(r.error or f"{stage.value} failed")
                if self.config.fail_fast:
                    break

        finished = datetime.now(timezone.utc).isoformat()
        return PipelineResult(
            status="passed" if ok else "failed", success=ok,
            stages=results, started_at=started, finished_at=finished, errors=errors,
        )

    def _exec(self, stage: PipelineStage) -> StageResult:
        import time
        t0 = time.perf_counter()
        try:
            out = {"stage": stage.value, "status": "ok"}
            elapsed = (time.perf_counter() - t0) * 1000
            return StageResult(stage, True, elapsed, out)
        except Exception as e:
            elapsed = (time.perf_counter() - t0) * 1000
            return StageResult(stage, False, elapsed, error=str(e))
