"""Curriculum engine — sampling, difficulty progression, balancing.

Source: compiler/03_curriculum/
"""

from dataclasses import dataclass, field
from enum import Enum

from compiler.core.constants import Difficulty
from compiler.ontology.domain import DomainName


class SampleType(Enum):
    KNOWLEDGE_ATOM = "knowledge_atom"
    ENGINEERING_EPISODE = "engineering_episode"
    CODE_EXAMPLE = "code_example"
    BUG_REPORT = "bug_report"
    CODE_REVIEW = "code_review"
    ARCHITECTURE_DECISION = "architecture_decision"
    PRODUCTION_INCIDENT = "production_incident"
    ENGINEERING_STORY = "engineering_story"
    LESSON = "lesson"
    TUTORIAL = "tutorial"
    DIALOG = "dialog"


SAMPLE_WEIGHTS: dict[SampleType, float] = {
    SampleType.KNOWLEDGE_ATOM: 0.10,
    SampleType.ENGINEERING_EPISODE: 0.20,
    SampleType.CODE_EXAMPLE: 0.10,
    SampleType.BUG_REPORT: 0.10,
    SampleType.CODE_REVIEW: 0.10,
    SampleType.ARCHITECTURE_DECISION: 0.10,
    SampleType.PRODUCTION_INCIDENT: 0.05,
    SampleType.ENGINEERING_STORY: 0.10,
    SampleType.LESSON: 0.05,
    SampleType.TUTORIAL: 0.05,
    SampleType.DIALOG: 0.05,
}

DOMAIN_WEIGHTS: dict[str, float] = {
    "Foundations": 0.05, "Programming": 0.10, "Algorithms": 0.08,
    "Data_Structures": 0.08, "Systems": 0.05, "Compilers": 0.03,
    "Networking": 0.04, "Databases": 0.05, "Distributed_Systems": 0.08,
    "Security": 0.05, "Software_Architecture": 0.08, "Testing": 0.05,
    "DevOps": 0.04, "Performance": 0.05, "Cloud": 0.04,
    "AI_Engineering": 0.08, "Human_Factors": 0.03, "Production_Engineering": 0.02,
}

DIFFICULTY_DISTRIBUTION: dict[Difficulty, float] = {
    Difficulty.D0: 0.05, Difficulty.D1: 0.15, Difficulty.D2: 0.25,
    Difficulty.D3: 0.25, Difficulty.D4: 0.15, Difficulty.D5: 0.10,
    Difficulty.D6: 0.05,
}


@dataclass
class CurriculumNode:
    id: str
    name: str
    domain: str
    difficulty: Difficulty
    prerequisites: list[str] = field(default_factory=list)
    sample_types: list[SampleType] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id, "name": self.name, "domain": self.domain,
            "difficulty": int(self.difficulty), "prerequisites": self.prerequisites,
        }


@dataclass
class CurriculumGraph:
    nodes: dict[str, CurriculumNode] = field(default_factory=dict)
    edges: list[tuple[str, str]] = field(default_factory=list)

    def add_node(self, node: CurriculumNode):
        self.nodes[node.id] = node

    def add_edge(self, from_id: str, to_id: str):
        self.edges.append((from_id, to_id))

    def prerequisites_of(self, node_id: str) -> list[CurriculumNode]:
        return [self.nodes[nid] for fid, nid in self.edges if nid == node_id and fid in self.nodes]

    def to_dict(self) -> dict:
        return {
            "nodes": {k: v.to_dict() for k, v in self.nodes.items()},
            "edges": [{"from": f, "to": t} for f, t in self.edges],
        }
