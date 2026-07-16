"""Universal Entity Model.

Source: compiler/01_ontology/17_entity_model.toon
"""

from dataclasses import dataclass, field

from compiler.core.metadata import Metadata
from compiler.core.lifecycle import LifecycleState, LifecycleStage


@dataclass
class Entity:
    metadata: Metadata
    lifecycle: LifecycleState = field(default_factory=LifecycleState)
    properties: dict = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)

    @property
    def id(self) -> str:
        return self.metadata.id

    @property
    def name(self) -> str:
        return self.metadata.object_name

    def transition(self, stage: LifecycleStage) -> "Entity":
        self.lifecycle.transition(stage)
        return self

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.metadata.object_type,
            "metadata": self.metadata.to_dict(),
            "lifecycle": self.lifecycle.to_dict(),
            "properties": self.properties,
            "tags": self.tags,
        }
