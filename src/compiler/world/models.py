"""World simulation models.

Source: compiler/04_world/
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

from compiler.core.metadata import Metadata
from compiler.core.constants import Difficulty, Severity, Priority
from compiler.ontology.entity import Entity


class TeamType(Enum):
    PLATFORM = "platform"
    INFRASTRUCTURE = "infrastructure"
    BACKEND = "backend"
    FRONTEND = "frontend"
    FULLSTACK = "fullstack"
    DATA = "data"
    ML = "machine_learning"
    SECURITY = "security"
    QA = "quality_assurance"
    DEVOPS = "devops"
    SRE = "site_reliability"
    MOBILE = "mobile"
    PRODUCT = "product"
    RESEARCH = "research"
    ARCHITECTURE = "architecture"


class EngineerLevel(Enum):
    INTERN = "intern"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    STAFF = "staff"
    PRINCIPAL = "principal"
    DISTINGUISHED = "distinguished"


@dataclass
class Engineer:
    name: str
    level: EngineerLevel
    role: str
    skills: list[str] = field(default_factory=list)
    experience_years: int = 0
    id: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id, "name": self.name,
            "level": self.level.value, "role": self.role,
            "skills": self.skills, "experience_years": self.experience_years,
        }


@dataclass
class Team:
    name: str
    team_type: TeamType
    members: list[Engineer] = field(default_factory=list)
    id: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id, "name": self.name,
            "type": self.team_type.value,
            "members": [m.to_dict() for m in self.members],
        }


class RepoScale(Enum):
    TINY = "tiny"       # 10 files
    SMALL = "small"     # 100 files
    MEDIUM = "medium"   # 1K files
    LARGE = "large"     # 10K files
    MONOLITH = "monolith"  # 100K+ files


@dataclass
class Repository:
    name: str
    language: str = "python"
    description: str = ""
    scale: RepoScale = RepoScale.MEDIUM
    teams: list[str] = field(default_factory=list)
    id: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id, "name": self.name, "language": self.language,
            "description": self.description, "scale": self.scale.value,
            "teams": self.teams,
        }


@dataclass
class Company:
    name: str
    industry: str = "technology"
    size: int = 100
    repositories: list[Repository] = field(default_factory=list)
    teams: list[Team] = field(default_factory=list)
    id: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id, "name": self.name, "industry": self.industry,
            "size": self.size,
            "repositories": [r.to_dict() for r in self.repositories],
            "teams": [t.to_dict() for t in self.teams],
        }


@dataclass
class Incident:
    title: str
    severity: Severity = Severity.S2
    status: str = "detected"
    description: str = ""
    root_cause: str = ""
    resolution: str = ""
    id: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {
            "id": self.id, "title": self.title, "severity": int(self.severity),
            "status": self.status, "description": self.description,
            "root_cause": self.root_cause, "resolution": self.resolution,
            "timestamp": self.timestamp,
        }


@dataclass
class FeatureRequest:
    title: str
    description: str = ""
    priority: Priority = Priority.P2
    status: str = "submitted"
    requester: str = ""
    id: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id, "title": self.title, "description": self.description,
            "priority": int(self.priority), "status": self.status,
            "requester": self.requester,
        }


@dataclass
class EngineeringWorld:
    name: str
    companies: list[Company] = field(default_factory=list)
    incidents: list[Incident] = field(default_factory=list)
    features: list[FeatureRequest] = field(default_factory=list)
    timeline: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    id: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id, "name": self.name,
            "companies": [c.to_dict() for c in self.companies],
            "incidents": [i.to_dict() for i in self.incidents],
            "features": [f.to_dict() for f in self.features],
            "timeline": self.timeline,
        }
