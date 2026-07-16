"""Knowledge Atom — minimal semantic unit.

Source: compiler/01_ontology/09_knowledge_atoms.toon
"""

from dataclasses import dataclass, field
from enum import Enum

from compiler.core.metadata import Metadata
from compiler.core.constants import Difficulty
from compiler.ontology.entity import Entity


class AtomType(Enum):
    CONCEPT = "Concept"
    PRINCIPLE = "Principle"
    MECHANISM = "Mechanism"
    FAILURE = "Failure"
    LESSON = "Lesson"


@dataclass
class KnowledgeAtom(Entity):
    atom_type: AtomType = AtomType.CONCEPT
    definition: str = ""
    domain: str = "GEN"
    difficulty: Difficulty = Difficulty.D1
    relationships: list[dict] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)

    @classmethod
    def create(cls, name: str, atom_type: AtomType, domain: str = "GEN",
               definition: str = "") -> "KnowledgeAtom":
        meta = Metadata.create(
            object_type=f"knowledge_atom.{atom_type.value}",
            object_name=name, domain=domain, prefix="KA",
        )
        return cls(metadata=meta, atom_type=atom_type, definition=definition, domain=domain)

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({
            "atom_type": self.atom_type.value, "definition": self.definition,
            "domain": self.domain, "difficulty": int(self.difficulty),
        })
        return d
