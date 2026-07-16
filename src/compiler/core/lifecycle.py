"""Object lifecycle management.

Source: compiler/00_core/06_dataset_lifecycle.toon
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone

from .constants import LifecycleStage


@dataclass
class LifecycleState:
    current_stage: LifecycleStage = LifecycleStage.DISCOVERY
    history: list[dict] = field(default_factory=list)
    error: str | None = None

    def transition(self, stage: LifecycleStage) -> "LifecycleState":
        now = datetime.now(timezone.utc).isoformat()
        self.history.append({"from": self.current_stage.value, "to": stage.value, "ts": now})
        self.current_stage = stage
        return self

    def fail(self, error: str) -> "LifecycleState":
        self.error = error
        return self

    @property
    def has_error(self) -> bool:
        return self.error is not None

    @property
    def is_terminal(self) -> bool:
        return self.current_stage in (LifecycleStage.RELEASE, LifecycleStage.EVOLUTION)

    def to_dict(self) -> dict:
        return {"stage": self.current_stage.value, "history": self.history, "error": self.error}
