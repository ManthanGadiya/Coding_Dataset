"""World generator — creates engineering worlds from specs."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from compiler.core.identifiers import make_id
from compiler.core.constants import Difficulty, Severity, Priority
from compiler.world.models import (
    EngineeringWorld, Company, Team, TeamType,
    Engineer, EngineerLevel, Repository, RepoScale,
    Incident, FeatureRequest,
)
from compiler.serialization.toon_parser import ToonParser, ToonCompiler


DOMAINS = [
    "Web Development", "Distributed Systems", "Databases",
    "Cloud Infrastructure", "Machine Learning", "Security",
    "Mobile Development", "Developer Tools", "API Design",
    "Real-time Systems",
]


COMPANY_NAMES = [
    "NebulaSoft", "QuantumByte", "AetherStack", "PulseWare",
    "VertexCore", "DriftLabs", "CipherDyne", "FluxSystems",
]


TECH_STACKS: dict[str, list[str]] = {
    "Web Development": ["Python", "TypeScript", "React", "Go", "PostgreSQL"],
    "Distributed Systems": ["Go", "Rust", "Kafka", "Cassandra", "Kubernetes"],
    "Databases": ["C++", "Rust", "PostgreSQL", "Redis", "MongoDB"],
    "Cloud Infrastructure": ["Go", "Python", "AWS", "Terraform", "Kubernetes"],
    "Machine Learning": ["Python", "PyTorch", "CUDA", "Ray", "MLflow"],
    "Security": ["Rust", "Go", "Python", "OpenSSL", "Enclave"],
    "Mobile Development": ["Kotlin", "Swift", "Flutter", "Firebase"],
    "Developer Tools": ["TypeScript", "Rust", "Go", "Docker"],
    "API Design": ["Go", "TypeScript", "GraphQL", "gRPC", "Redis"],
    "Real-time Systems": ["C++", "Rust", "RTOS", "DDS", "ZeroMQ"],
}


ENGINEER_NAMES = [
    "Alice Chen", "Bob Martinez", "Carol Singh", "David Kim",
    "Eva Johansson", "Frank Okafor", "Grace Liu", "Henry Park",
    "Iris Nakamura", "James Wilson", "Katherine Lee", "Liam O'Brien",
    "Maya Patel", "Noah Schmidt", "Olivia Torres", "Peter Jackson",
]


class WorldGenerator:
    def __init__(self, seed: int = 42):
        self.seed = seed
        self._rng_state = seed

    def _rand(self, max_val: int) -> int:
        self._rng_state = (self._rng_state * 1103515245 + 12345) & 0x7FFFFFFF
        return self._rng_state % max_val

    def _pick(self, items: list) -> Any:
        return items[self._rand(len(items))]

    def _pick_n(self, items: list, n: int) -> list:
        pool = list(items)
        result = []
        for _ in range(min(n, len(pool))):
            idx = self._rand(len(pool))
            result.append(pool.pop(idx))
        return result

    def _engineer_level(self) -> EngineerLevel:
        levels = list(EngineerLevel)
        weights = [5, 10, 25, 30, 15, 10, 5]
        total = sum(weights)
        r = self._rand(total)
        cumulative = 0
        for i, w in enumerate(weights):
            cumulative += w
            if r < cumulative:
                return levels[i]
        return EngineerLevel.MID

    def generate_engineer(self) -> Engineer:
        name = self._pick(ENGINEER_NAMES)
        level = self._engineer_level()
        years_map = {
            EngineerLevel.INTERN: 0, EngineerLevel.JUNIOR: 1,
            EngineerLevel.MID: 4, EngineerLevel.SENIOR: 7,
            EngineerLevel.STAFF: 11, EngineerLevel.PRINCIPAL: 15,
            EngineerLevel.DISTINGUISHED: 20,
        }
        return Engineer(
            id=make_id("EN"),
            name=name, level=level, role=level.value,
            skills=self._pick_n(["Python", "Go", "Rust", "TypeScript", "Kubernetes",
                                "PostgreSQL", "AWS", "Docker", "GraphQL", "Kafka"], self._rand(5) + 2),
            experience_years=years_map[level],
        )

    def generate_team(self, team_type: TeamType = TeamType.BACKEND, size: int = 4) -> Team:
        return Team(
            id=make_id("TM"),
            name=f"{team_type.value}-team-{self._rand(100)}",
            team_type=team_type,
            members=[self.generate_engineer() for _ in range(size)],
        )

    def generate_repository(self, domain: str = "Web Development") -> Repository:
        scales = [RepoScale.TINY, RepoScale.SMALL, RepoScale.MEDIUM, RepoScale.LARGE]
        return Repository(
            id=make_id("RP"),
            name=f"service-{self._pick(['api', 'web', 'core', 'data', 'auth', 'worker'])}",
            language=self._pick(TECH_STACKS.get(domain, ["Python"])),
            description=f"{domain} service",
            scale=self._pick(scales),
        )

    def generate_company(self, domain: str = "Web Development") -> Company:
        c = Company(
            id=make_id("CO"),
            name=self._pick(COMPANY_NAMES),
            industry=domain,
            size=10 ** self._rand(3) * (self._rand(9) + 1),
        )
        num_teams = self._rand(3) + 2
        team_types = list(TeamType)
        for _ in range(num_teams):
            c.teams.append(self.generate_team(self._pick(team_types), self._rand(4) + 3))
        num_repos = self._rand(4) + 2
        for _ in range(num_repos):
            c.repositories.append(self.generate_repository(domain))
        return c

    def generate_incident(self, severity: Severity | None = None) -> Incident:
        return Incident(
            id=make_id("IN"),
            title=self._pick([
                "Database connection pool exhausted",
                "Memory leak in cache layer",
                "API timeout under load",
                "Data corruption in replication",
                "Certificate expiry causes outage",
                "Race condition in payment processing",
                "DNS resolution failure",
                "Deadlock in transaction manager",
            ]),
            severity=severity or self._pick(list(Severity)),
            status=self._pick(["detected", "analyzing", "mitigated", "resolved"]),
            description="Auto-generated incident for training",
        )

    def generate_world(self, name: str | None = None,
                       domain: str | None = None) -> EngineeringWorld:
        d = domain or self._pick(DOMAINS)
        w = EngineeringWorld(
            id=make_id("EW"),
            name=name or f"{d.replace(' ', '_')}_World",
        )
        num_companies = self._rand(2) + 1
        for _ in range(num_companies):
            w.companies.append(self.generate_company(d))
        num_incidents = self._rand(3)
        for _ in range(num_incidents):
            w.incidents.append(self.generate_incident())
        num_features = self._rand(4)
        for _ in range(num_features):
            w.features.append(FeatureRequest(
                id=make_id("FR"),
                title=self._pick([
                    "Add caching layer", "Implement rate limiting",
                    "Upgrade database", "Add monitoring dashboard",
                    "Implement circuit breaker", "Add audit logging",
                ]),
                priority=self._pick(list(Priority)),
                status=self._pick(["submitted", "approved", "in_progress"]),
            ))
        return w
