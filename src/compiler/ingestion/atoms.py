"""Knowledge atoms — structured engineering knowledge extracted from real sources."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import json
import re


@dataclass
class KnowledgeAtom:
    domain: str
    concept: str
    content: str
    source_url: str
    source_type: str
    tags: list[str] = field(default_factory=list)
    quality: float = 1.0


class KnowledgeStore:
    """Stores and retrieves knowledge atoms for use in generation."""

    def __init__(self, path: Path = Path("ingestion/atoms")):
        self.path = path
        self.path.mkdir(parents=True, exist_ok=True)
        self._atoms: dict[str, list[KnowledgeAtom]] = {}
        self._load()

    def _load(self):
        for f in self.path.glob("*.json"):
            data = json.loads(f.read_text())
            for d in data:
                atom = KnowledgeAtom(**d)
                self._atoms.setdefault(atom.domain, []).append(atom)

    def save(self, atoms: list[KnowledgeAtom]):
        by_domain: dict[str, list[dict]] = {}
        for a in atoms:
            by_domain.setdefault(a.domain, []).append({
                "domain": a.domain, "concept": a.concept,
                "content": a.content, "source_url": a.source_url,
                "source_type": a.source_type, "tags": a.tags,
                "quality": a.quality,
            })
        for domain, data in by_domain.items():
            path = self.path / f"{domain.lower().replace(' ', '_')}.json"
            path.write_text(json.dumps(data, indent=2))

    def get(self, domain: str, concept: str | None = None) -> list[KnowledgeAtom]:
        atoms = self._atoms.get(domain, [])
        if concept:
            atoms = [a for a in atoms if concept.lower() in a.concept.lower()]
        return atoms

    def get_random(self, rng, domain: str, n: int = 1) -> list[KnowledgeAtom]:
        atoms = self._atoms.get(domain, [])
        if not atoms:
            return []
        return [atoms[rng.randint(0, len(atoms)-1)] for _ in range(min(n, len(atoms)))]

    def search(self, query: str) -> list[KnowledgeAtom]:
        results = []
        for atoms in self._atoms.values():
            for a in atoms:
                if query.lower() in a.content.lower() or query.lower() in a.concept.lower():
                    results.append(a)
        return results

    def count(self) -> int:
        return sum(len(v) for v in self._atoms.values())


class AtomProcessor:
    """Processes scraped markdown content into knowledge atoms."""

    def process(self, content: str, source_url: str, domain: str, source_type: str,
                concepts: list[str]) -> list[KnowledgeAtom]:
        atoms = []
        sentences = re.split(r'(?<=[.!?])\s+', content)
        tech_keywords = [
            "system", "design", "pattern", "architecture", "cache", "database",
            "load balanc", "replicat", "shard", "partition", "consistency",
            "availability", "latency", "throughput", "scalab", "fault", "redundan",
            "microservice", "monolith", "event", "queue", "async", "API",
            "incident", "postmortem", "reliability", "MTTR", "SRE", "monitor",
            "alert", "rollback", "failover", "timeout", "circuit break",
            "container", "Kubernetes", "deploy", "CI/CD", "observability",
            "tracing", "metric", "log", "auth", "encrypt", "token",
        ]

        seen = set()
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 30 or len(sentence) > 500:
                continue
            if any(kw in sentence.lower() for kw in tech_keywords):
                norm = sentence.lower().strip()
                if norm not in seen:
                    seen.add(norm)
                    for concept in concepts:
                        if concept.lower() in sentence.lower():
                            atoms.append(KnowledgeAtom(
                                domain=domain, concept=concept,
                                content=sentence, source_url=source_url,
                                source_type=source_type,
                                quality=1.0 if source_type in ("pattern", "postmortem") else 0.8,
                            ))
                            break
        return atoms


PREBUILT_ATOMS: list[KnowledgeAtom] = [
    KnowledgeAtom("Distributed_Systems", "CAP theorem",
        "A distributed system can only provide two of three properties simultaneously: consistency, availability, and partition tolerance.",
        "https://dev.to/fahimulhaq/complete-guide-to-system-design-oc7", "article"),
    KnowledgeAtom("Distributed_Systems", "PACELC theorem",
        "When there is no partition, a distributed system can trade off between latency and consistency.",
        "https://dev.to/fahimulhaq/complete-guide-to-system-design-oc7", "article"),
    KnowledgeAtom("Distributed_Systems", "sharding",
        "Sharding distributes data across multiple database instances, with each shard containing a unique subset of data.",
        "https://dev.to/fahimulhaq/complete-guide-to-system-design-oc7", "article"),
    KnowledgeAtom("Software_Architecture", "Design Patterns",
        "Design patterns are typical solutions to common problems in software design. Each pattern is like a blueprint that you can customize.",
        "https://refactoring.guru/design-patterns/catalog", "pattern"),
    KnowledgeAtom("Software_Architecture", "Creational Patterns",
        "Creational patterns provide various object creation mechanisms, which increase flexibility and reuse of existing code.",
        "https://refactoring.guru/design-patterns/catalog", "pattern"),
    KnowledgeAtom("Software_Architecture", "Structural Patterns",
        "Structural patterns explain how to assemble objects and classes into larger structures while keeping these structures flexible and efficient.",
        "https://refactoring.guru/design-patterns/catalog", "pattern"),
    KnowledgeAtom("Software_Architecture", "Behavioral Patterns",
        "Behavioral patterns are concerned with algorithms and the assignment of responsibilities between objects.",
        "https://refactoring.guru/design-patterns/catalog", "pattern"),
    KnowledgeAtom("Software_Architecture", "microservices",
        "Microservices architecture breaks a system into loosely coupled, independently deployable services, each responsible for a specific business function.",
        "https://dev.to/fahimulhaq/complete-guide-to-system-design-oc7", "article"),
    KnowledgeAtom("Software_Architecture", "event-driven architecture",
        "Event-driven architecture relies on the production, detection, and consumption of events to drive interactions between decoupled components.",
        "https://dev.to/fahimulhaq/complete-guide-to-system-design-oc7", "article"),
    KnowledgeAtom("Software_Architecture", "caching",
        "Caching stores frequently accessed data in a temporary high-speed storage area, reducing the need to recompute or re-fetch from slower sources.",
        "https://dev.to/fahimulhaq/complete-guide-to-system-design-oc7", "article"),
    KnowledgeAtom("Production_Engineering", "incident response",
        "Modern postmortem software captures timeline data during the incident and uses it to draft postmortems automatically, saving 60-90 minutes per incident.",
        "https://incident.io/blog/best-incident-postmortem-software-2026-guide", "postmortem"),
    KnowledgeAtom("Production_Engineering", "postmortem",
        "Incident postmortem software facilitates retrospective analysis after system outages or degraded performance, supporting the learning phase of incident management.",
        "https://incident.io/blog/best-incident-postmortem-software-2026-guide", "postmortem"),
    KnowledgeAtom("Production_Engineering", "MTTR",
        "Mean Time To Resolution (MTTR) is the average time to fully resolve a failure, including detection, diagnosis, repair, and ensuring recurrence prevention.",
        "https://incident.io/blog/best-incident-postmortem-software-2026-guide", "postmortem"),
    KnowledgeAtom("Production_Engineering", "blameless culture",
        "Blameless postmortem culture focuses on identifying contributing causes without indicting individuals, emphasizing system-level issues rather than personal mistakes.",
        "https://incident.io/blog/best-incident-postmortem-software-2026-guide", "postmortem"),
    KnowledgeAtom("Production_Engineering", "reliability",
        "Reliability measures how consistently a system runs without failure, while availability reflects how often it's accessible when needed.",
        "https://dev.to/fahimulhaq/complete-guide-to-system-design-oc7", "article"),
    KnowledgeAtom("Databases", "replication",
        "Replication works alongside redundancy by keeping duplicate components synchronized, commonly using a primary-replica model.",
        "https://dev.to/fahimulhaq/complete-guide-to-system-design-oc7", "article"),
    KnowledgeAtom("Databases", "partitioning",
        "Data partitioning divides data within a single database instance based on logical rules such as date ranges or user IDs to reduce query load.",
        "https://dev.to/fahimulhaq/complete-guide-to-system-design-oc7", "article"),
    KnowledgeAtom("Performance", "caching",
        "Caching reduces latency by storing frequently accessed data closer to users, while load balancing distributes traffic to optimize resource use.",
        "https://dev.to/fahimulhaq/complete-guide-to-system-design-oc7", "article"),
    KnowledgeAtom("Security", "authentication",
        "Authentication verifies a user's identity. Best practices include implementing multi-factor authentication (MFA) to reduce the risk of unauthorized access.",
        "https://dev.to/fahimulhaq/complete-guide-to-system-design-oc7", "article"),
    KnowledgeAtom("Security", "defense in depth",
        "Modern security strategies rely on defense in depth, layering protections at multiple levels: network, application, and data.",
        "https://dev.to/fahimulhaq/complete-guide-to-system-design-oc7", "article"),
]
