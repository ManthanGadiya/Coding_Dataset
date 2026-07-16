"""Canonical metadata for every compiler object.

Source: compiler/00_core/08_metadata_spec.toon
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone

from .constants import LifecycleStage
from .identifiers import make_id


@dataclass
class Metadata:
    id: str
    object_type: str
    object_name: str
    short_name: str | None = None
    domain: str = "GEN"
    version: str = "1.0.0"
    lifecycle_stage: LifecycleStage = LifecycleStage.DISCOVERY
    compiler_version: str = "1.0.0"
    ontology_version: str = "1.0.0"
    schema_version: str = "1.0.0"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    provenance: list[str] = field(default_factory=list)
    parent_id: str | None = None

    @classmethod
    def create(cls, object_type: str, object_name: str, domain: str = "GEN",
               prefix: str | None = None) -> "Metadata":
        pfx = prefix or object_type[:3].upper()
        return cls(
            id=make_id(pfx, domain),
            object_type=object_type,
            object_name=object_name,
            domain=domain,
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "object_type": self.object_type,
            "object_name": self.object_name,
            "domain": self.domain,
            "version": self.version,
            "lifecycle_stage": self.lifecycle_stage.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "provenance": self.provenance,
        }
