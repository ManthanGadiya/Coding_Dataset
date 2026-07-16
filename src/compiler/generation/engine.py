"""Generation engine orchestrator.

Source: compiler/05_generation/
"""

from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone

from compiler.core.constants import Difficulty, Quality, Confidence
from compiler.ontology.ekr import EngineeringKnowledgeRecord


class EpisodeType(Enum):
    BUG_FIX = "bug_fix"
    FEATURE_IMPLEMENTATION = "feature_implementation"
    CODE_REVIEW = "code_review"
    ARCHITECTURE_DECISION = "architecture_decision"
    INCIDENT_RESPONSE = "incident_response"
    REFACTORING = "refactoring"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    DESIGN_DISCUSSION = "design_discussion"
    DEBUGGING_SESSION = "debugging_session"
    PLANNING = "planning"
    DOCUMENTATION = "documentation"
    TECHNICAL_DEBT = "technical_debt"


@dataclass
class GenerationResult:
    ekr: EngineeringKnowledgeRecord
    episode_type: EpisodeType
    duration_ms: float
    success: bool = True
    error: str | None = None

    def to_dict(self) -> dict:
        return {
            "ekr": self.ekr.to_dict(),
            "episode_type": self.episode_type.value,
            "success": self.success,
            "error": self.error,
        }


@dataclass
class EpisodeGenerator:
    def generate(self, context: dict, episode_type: EpisodeType,
                 domain: str = "GEN") -> GenerationResult:
        import time
        t0 = time.perf_counter()
        ekr = EngineeringKnowledgeRecord.create(
            name=f"{episode_type.value}_{domain}",
            domain=domain,
        )
        ekr.difficulty = Difficulty.D2
        ekr.add_reasoning("Observe", f"Generating {episode_type.value} episode in {domain}")
        ekr.add_reasoning("Design", f"Designing solution for {episode_type.value}")
        elapsed = (time.perf_counter() - t0) * 1000
        return GenerationResult(ekr=ekr, episode_type=episode_type, duration_ms=elapsed)
