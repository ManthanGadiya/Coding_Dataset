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
        self._atoms.clear()
        for a in atoms:
            self._atoms.setdefault(a.domain, []).append(a)

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
    # === Distributed_Systems (8 atoms) ===
    KnowledgeAtom("Distributed_Systems", "CAP theorem",
        "A distributed system can only provide two of three properties simultaneously: consistency, availability, and partition tolerance.",
        "https://dev.to/fahimulhaq/complete-guide-to-system-design-oc7", "article"),
    KnowledgeAtom("Distributed_Systems", "PACELC theorem",
        "When there is no partition, a distributed system can trade off between latency and consistency.",
        "https://dev.to/fahimulhaq/complete-guide-to-system-design-oc7", "article"),
    KnowledgeAtom("Distributed_Systems", "sharding",
        "Sharding distributes data across multiple database instances, with each shard containing a unique subset of data.",
        "https://dev.to/fahimulhaq/complete-guide-to-system-design-oc7", "article"),
    KnowledgeAtom("Distributed_Systems", "consensus",
        "Consensus algorithms like Raft and Paxos allow distributed nodes to agree on values despite failures, ensuring consistency across a cluster.",
        "https://github.com/Sairyss/system-design-patterns", "pattern"),
    KnowledgeAtom("Distributed_Systems", "gossip protocol",
        "Gossip protocols enable decentralized information dissemination where each node periodically exchanges state with random peers, scaling to thousands of nodes.",
        "https://github.com/Sairyss/system-design-patterns", "pattern"),
    KnowledgeAtom("Distributed_Systems", "consistent hashing",
        "Consistent hashing maps keys to nodes using a hash ring, minimizing remapping when nodes are added or removed — critical for distributed caches.",
        "https://github.com/Sairyss/system-design-patterns", "pattern"),
    KnowledgeAtom("Distributed_Systems", "vector clocks",
        "Vector clocks capture causal relationships between events in distributed systems, enabling detection of concurrent updates.",
        "https://github.com/Sairyss/system-design-patterns", "pattern"),
    KnowledgeAtom("Distributed_Systems", "CRDT",
        "Conflict-free Replicated Data Types (CRDTs) allow concurrent updates across replicas that converge automatically without consensus.",
        "https://github.com/Sairyss/system-design-patterns", "pattern"),

    # === Software_Architecture (12 atoms) ===
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
    KnowledgeAtom("Software_Architecture", "Architecture Decision Record",
        "An Architecture Decision Record (ADR) captures a single architectural decision along with its context, trade-offs, and consequences.",
        "https://adr.github.io/", "pattern"),
    KnowledgeAtom("Software_Architecture", "CQRS",
        "Command Query Responsibility Segregation (CQRS) separates read and write models, enabling independent scaling and optimization.",
        "https://github.com/Sairyss/system-design-patterns", "pattern"),
    KnowledgeAtom("Software_Architecture", "SAGA pattern",
        "The Saga pattern manages distributed transactions by breaking them into a series of local transactions with compensating rollback steps.",
        "https://github.com/Sairyss/system-design-patterns", "pattern"),
    KnowledgeAtom("Software_Architecture", "outbox pattern",
        "The Outbox pattern ensures reliable message delivery by writing events to a database table as part of the same transaction as the state change.",
        "https://github.com/Sairyss/system-design-patterns", "pattern"),
    KnowledgeAtom("Software_Architecture", "strangler fig pattern",
        "The Strangler Fig pattern incrementally replaces legacy systems by gradually routing functionality to new services until the old system can be decommissioned.",
        "https://martinfowler.com/bliki/StranglerFigApplication.html", "pattern"),
    KnowledgeAtom("Software_Architecture", "bulkhead pattern",
        "The Bulkhead pattern isolates system components into pools so failure in one pool does not cascade, ensuring partial availability during outages.",
        "https://github.com/Sairyss/system-design-patterns", "pattern"),

    # === Production_Engineering (10 atoms) ===
    KnowledgeAtom("Production_Engineering", "incident response",
        "Modern postmortem software captures timeline data during the incident and uses it to draft postmortems automatically, saving 60-90 minutes per incident.",
        "https://incident.io/blog/best-incident-postmortem-software-2026-guide", "postmortem"),
    KnowledgeAtom("Production_Engineering", "postmortem",
        "Postmortems should be blameless and focus on process and technology, not people. Assume everyone acted with good intent given available information.",
        "https://sre.google/sre-book/service-best-practices/", "postmortem"),
    KnowledgeAtom("Production_Engineering", "MTTR",
        "Mean Time To Resolution (MTTR) is the average time to fully resolve a failure, including detection, diagnosis, repair, and ensuring recurrence prevention.",
        "https://incident.io/blog/best-incident-postmortem-software-2026-guide", "postmortem"),
    KnowledgeAtom("Production_Engineering", "blameless culture",
        "Blameless postmortem culture focuses on identifying contributing causes without indicting individuals, emphasizing system-level issues rather than personal mistakes.",
        "https://incident.io/blog/best-incident-postmortem-software-2026-guide", "postmortem"),
    KnowledgeAtom("Production_Engineering", "error budgets",
        "Error budgets balance reliability and innovation. A budget is 1 minus the service SLO; when exhausted, all feature changes freeze until budget recovers.",
        "https://sre.google/sre-book/service-best-practices/", "sre"),
    KnowledgeAtom("Production_Engineering", "SLO",
        "Service Level Objectives (SLOs) should be measured in terms that matter to end users, such as client-side latency rather than server-side metrics.",
        "https://sre.google/sre-book/service-best-practices/", "sre"),
    KnowledgeAtom("Production_Engineering", "progressive rollouts",
        "Nonemergency rollouts must proceed in stages — apply changes to small traffic fractions, monitor, and roll back first before diagnosing if issues arise.",
        "https://sre.google/sre-book/service-best-practices/", "sre"),
    KnowledgeAtom("Production_Engineering", "capacity planning",
        "Provision N+2 capacity to handle simultaneous planned and unplanned outages without degrading user experience.",
        "https://sre.google/sre-book/service-best-practices/", "sre"),
    KnowledgeAtom("Production_Engineering", "monitoring",
        "Monitoring has three output types: pages (act now), tickets (act within days), and logging (analysis later). Alerts in email are effectively /dev/null.",
        "https://sre.google/sre-book/service-best-practices/", "sre"),
    KnowledgeAtom("Production_Engineering", "graceful degradation",
        "Services should produce reasonable but suboptimal results when overloaded, such as searching a smaller index or disabling non-critical features.",
        "https://sre.google/sre-book/service-best-practices/", "sre"),
    KnowledgeAtom("Production_Engineering", "fail sanely",
        "Sanitize and validate configuration inputs. Respond to bad input by continuing with previous state and alerting, not by applying corrupt data.",
        "https://sre.google/sre-book/service-best-practices/", "sre"),

    # === Databases (6 atoms) ===
    KnowledgeAtom("Databases", "replication",
        "Replication works alongside redundancy by keeping duplicate components synchronized, commonly using a primary-replica model.",
        "https://dev.to/fahimulhaq/complete-guide-to-system-design-oc7", "article"),
    KnowledgeAtom("Databases", "partitioning",
        "Data partitioning divides data within a single database instance based on logical rules such as date ranges or user IDs to reduce query load.",
        "https://dev.to/fahimulhaq/complete-guide-to-system-design-oc7", "article"),
    KnowledgeAtom("Databases", "indexing",
        "Database indexing creates a data structure that enables fast data lookup without scanning the entire table. B-Tree indexes work for most cases.",
        "https://github.com/Sairyss/system-design-patterns", "pattern"),
    KnowledgeAtom("Databases", "denormalization",
        "Denormalization improves read performance by adding redundant copies of data, sacrificing write performance to reduce join complexity.",
        "https://github.com/Sairyss/system-design-patterns", "pattern"),
    KnowledgeAtom("Databases", "materialized views",
        "Materialized views pre-compute and store query results for fast retrieval. Data may be stale as refresh happens periodically.",
        "https://github.com/Sairyss/system-design-patterns", "pattern"),
    KnowledgeAtom("Databases", "connection pooling",
        "Connection pooling reuses database connections across requests, avoiding the overhead of establishing a new TCP connection for each operation.",
        "https://github.com/Sairyss/system-design-patterns", "pattern"),

    # === Performance (4 atoms) ===
    KnowledgeAtom("Performance", "caching",
        "Caching reduces latency by storing frequently accessed data closer to users, while load balancing distributes traffic to optimize resource use.",
        "https://dev.to/fahimulhaq/complete-guide-to-system-design-oc7", "article"),
    KnowledgeAtom("Performance", "autoscaling",
        "Autoscaling dynamically adjusts computational resources based on load, adding capacity during peaks and releasing resources during lulls.",
        "https://github.com/Sairyss/system-design-patterns", "pattern"),
    KnowledgeAtom("Performance", "load balancing",
        "Load balancing distributes traffic across servers using algorithms like round-robin, least-connections, or consistent hashing for optimal resource use.",
        "https://github.com/Sairyss/system-design-patterns", "pattern"),
    KnowledgeAtom("Performance", "CDN",
        "Content Delivery Networks (CDNs) cache content at edge servers close to users, reducing latency and offloading origin servers.",
        "https://dev.to/fahimulhaq/complete-guide-to-system-design-oc7", "article"),

    # === Security (3 atoms) ===
    KnowledgeAtom("Security", "authentication",
        "Authentication verifies a user's identity. Best practices include implementing multi-factor authentication (MFA) to reduce the risk of unauthorized access.",
        "https://dev.to/fahimulhaq/complete-guide-to-system-design-oc7", "article"),
    KnowledgeAtom("Security", "defense in depth",
        "Modern security strategies rely on defense in depth, layering protections at multiple levels: network, application, and data.",
        "https://dev.to/fahimulhaq/complete-guide-to-system-design-oc7", "article"),
    KnowledgeAtom("Security", "zero trust",
        "Zero Trust architecture assumes no implicit trust based on network location; every request must be authenticated, authorized, and encrypted.",
        "https://sre.google/sre-book/service-best-practices/", "sre"),

    # === Networking (4 atoms) ===
    KnowledgeAtom("Networking", "API Gateway",
        "An API Gateway acts as a reverse proxy that routes requests, handles load balancing, rate limiting, authentication, and aggregates responses from multiple services.",
        "https://github.com/Sairyss/system-design-patterns", "pattern"),
    KnowledgeAtom("Networking", "circuit breaker",
        "The Circuit Breaker pattern prevents cascading failures by detecting when a downstream service is failing and routing around it until it recovers.",
        "https://github.com/Sairyss/system-design-patterns", "pattern"),
    KnowledgeAtom("Networking", "retry with backoff",
        "Clients making RPCs must implement exponential backoff with jitter for retries to prevent retry storms that amplify failure rates.",
        "https://sre.google/sre-book/service-best-practices/", "sre"),
    KnowledgeAtom("Networking", "graceful load shedding",
        "When load exceeds capacity, use well-behaved queuing, dynamic timeouts, and tarpitting to shed load gracefully rather than failing entirely.",
        "https://sre.google/sre-book/service-best-practices/", "sre"),

    # === DevOps (4 atoms) ===
    KnowledgeAtom("DevOps", "CI/CD",
        "Continuous Integration and Continuous Deployment automates building, testing, and deploying code changes, reducing manual error and speeding delivery.",
        "https://sre.google/sre-book/release-engineering/", "sre"),
    KnowledgeAtom("DevOps", "release engineering",
        "Release engineering manages the process of building and deploying software, including versioning, artifact management, and progressive rollout strategies.",
        "https://sre.google/sre-book/release-engineering/", "sre"),
    KnowledgeAtom("DevOps", "immutable infrastructure",
        "Immutable infrastructure replaces servers instead of modifying them in-place, ensuring consistent and reproducible deployments.",
        "https://sre.google/sre-book/service-best-practices/", "sre"),
    KnowledgeAtom("DevOps", "chaos engineering",
        "Chaos engineering proactively tests system resilience by injecting failures in production-like environments to uncover weaknesses before they cause real outages.",
        "https://github.com/Sairyss/system-design-patterns", "pattern"),

    # === Testing (4 atoms) ===
    KnowledgeAtom("Testing", "testing for reliability",
        "Testing for reliability includes unit tests, integration tests, load tests, and disaster recovery drills to validate system behavior under adverse conditions.",
        "https://sre.google/sre-book/testing-reliability/", "sre"),
    KnowledgeAtom("Testing", "load testing",
        "Load testing validates systems under expected and peak traffic, establishing the resource-to-capacity ratio that drives provisioning decisions.",
        "https://sre.google/sre-book/service-best-practices/", "sre"),
    KnowledgeAtom("Testing", "canary deployment",
        "Canary deployments route a small percentage of traffic to a new version before full rollout, detecting regressions with minimal user impact.",
        "https://sre.google/sre-book/service-best-practices/", "sre"),
    KnowledgeAtom("Testing", "disaster role playing",
        "Practice handling hypothetical outages through disaster role-playing to keep incident response skills sharp and improve documentation.",
        "https://sre.google/sre-book/service-best-practices/", "sre"),

    # === Cloud (3 atoms) ===
    KnowledgeAtom("Cloud", "serverless",
        "Serverless computing abstracts infrastructure management — cloud providers dynamically allocate resources based on usage, scaling automatically.",
        "https://dev.to/fahimulhaq/complete-guide-to-system-design-oc7", "article"),
    KnowledgeAtom("Cloud", "multi-AZ deployment",
        "Multi-Availability Zone deployment spreads services across physically isolated data centers, ensuring continued operation during regional failures.",
        "https://sre.google/sre-book/service-best-practices/", "sre"),
    KnowledgeAtom("Cloud", "N+2 capacity",
        "Provision N+2 capacity means peak traffic can be handled by N instances while the largest 2 instances are unavailable simultaneously.",
        "https://sre.google/sre-book/service-best-practices/", "sre"),

    # === Systems (3 atoms) ===
    KnowledgeAtom("Systems", "asynchronous processing",
        "Asynchronous processing uses message queues or event streams to decouple components, improving scalability and resilience.",
        "https://github.com/Sairyss/system-design-patterns", "pattern"),
    KnowledgeAtom("Systems", "event sourcing",
        "Event sourcing stores all state changes as a sequence of events, enabling full audit trails, temporal queries, and replay for recovery.",
        "https://github.com/Sairyss/system-design-patterns", "pattern"),
    KnowledgeAtom("Systems", "actor model",
        "The Actor model isolates state within lightweight actors that communicate via messages, eliminating shared-state concurrency bugs.",
        "https://github.com/Sairyss/system-design-patterns", "pattern"),

    # === AI_Engineering (4 atoms) ===
    KnowledgeAtom("AI_Engineering", "RAG",
        "Retrieval-Augmented Generation (RAG) combines LLMs with external knowledge retrieval, grounding model outputs in verifiable source documents.",
        "https://dev.to/fahimulhaq/complete-guide-to-system-design-oc7", "article"),
    KnowledgeAtom("AI_Engineering", "LLM inference",
        "Large Language Model inference introduces new cost and latency constraints — model inference costs can dwarf compute costs in AI-native architectures.",
        "https://dev.to/fahimulhaq/complete-guide-to-system-design-oc7", "article"),
    KnowledgeAtom("AI_Engineering", "prompt caching",
        "Prompt caching reduces LLM inference costs by reusing cached processing results for repeated prompt prefixes across requests.",
        "https://dev.to/fahimulhaq/complete-guide-to-system-design-oc7", "article"),
    KnowledgeAtom("AI_Engineering", "AI observability",
        "AI systems require specialized observability: tracking embeddings drift, hallucination rates, token usage, and model response quality over time.",
        "https://dev.to/fahimulhaq/complete-guide-to-system-design-oc7", "article"),

    # === Human_Factors (3 atoms) ===
    KnowledgeAtom("Human_Factors", "SRE team model",
        "SRE teams should spend no more than 50% of time on operational work. At least 8 people per on-call rotation prevents fatigue.",
        "https://sre.google/sre-book/service-best-practices/", "sre"),
    KnowledgeAtom("Human_Factors", "blameless culture",
        "Blameless postmortems focus on fixing the system, not the people. We can't fix people — but we can improve system design to prevent entire failure classes.",
        "https://sre.google/sre-book/service-best-practices/", "sre"),
    KnowledgeAtom("Human_Factors", "production meetings",
        "Regular production meetings between SRE and development teams align on operational health, incident trends, and reliability improvements.",
        "https://sre.google/sre-book/service-best-practices/", "sre"),

    # === Foundations (2 atoms) ===
    KnowledgeAtom("Foundations", "engineering thinking",
        "System Design is the process of understanding a system's requirements and creating infrastructure to satisfy them under constraints.",
        "https://dev.to/fahimulhaq/complete-guide-to-system-design-oc7", "article"),
    KnowledgeAtom("Foundations", "trade-off thinking",
        "Engineering is about trade-offs: consistency vs availability, latency vs throughput, build vs buy, speed vs quality. There are no free lunches.",
        "https://dev.to/fahimulhaq/complete-guide-to-system-design-oc7", "article"),

    # === Algorithms (2 atoms) ===
    KnowledgeAtom("Algorithms", "exponential backoff",
        "Exponential backoff with jitter is essential for retry logic in distributed systems, preventing retry storms that amplify failure rates.",
        "https://sre.google/sre-book/service-best-practices/", "sre"),
    KnowledgeAtom("Algorithms", "consistent hashing",
        "Consistent hashing maps keys to positions on a hash ring, with each node responsible for a range. Adding or removing nodes affects only immediate neighbors.",
        "https://github.com/Sairyss/system-design-patterns", "pattern"),

    # === Software_Architecture additions from microservices article (15 atoms) ===
    KnowledgeAtom("Software_Architecture", "microservices definition",
        "Microservice architecture builds applications as suites of independently deployable services, each running in its own process and communicating via lightweight HTTP APIs.",
        "https://martinfowler.com/articles/microservices.html", "pattern"),
    KnowledgeAtom("Software_Architecture", "smart endpoints dumb pipes",
        "Microservices favor smart endpoints and dumb pipes using simple RESTish protocols and lightweight messaging, avoiding complex ESB middleware for communication.",
        "https://martinfowler.com/articles/microservices.html", "pattern"),
    KnowledgeAtom("Software_Architecture", "decentralized governance",
        "Microservices decentralize governance so each service can choose the best technology stack for its requirements, enabled by service boundary enforcement.",
        "https://martinfowler.com/articles/microservices.html", "pattern"),
    KnowledgeAtom("Software_Architecture", "polyglot persistence",
        "Microservices prefer decentralized data management where each service owns its own database using polyglot persistence — different databases for different service needs.",
        "https://martinfowler.com/articles/microservices.html", "pattern"),
    KnowledgeAtom("Software_Architecture", "design for failure",
        "Microservice architectures must design for failure: any service call can fail, so clients implement graceful degradation with circuit breakers, timeouts, and bulkheads.",
        "https://martinfowler.com/articles/microservices.html", "pattern"),
    KnowledgeAtom("Software_Architecture", "bounded context",
        "Bounded Context from Domain-Driven Design provides natural service boundaries by dividing complex domains into separate contexts with explicit relationships between them.",
        "https://martinfowler.com/articles/microservices.html", "pattern"),
    KnowledgeAtom("Software_Architecture", "tolerant reader",
        "Tolerant Reader pattern allows services to tolerate changes in suppliers by ignoring unknown fields in responses, enabling independent evolution of service contracts.",
        "https://martinfowler.com/articles/microservices.html", "pattern"),
    KnowledgeAtom("Software_Architecture", "consumer-driven contracts",
        "Consumer-Driven Contracts enable services to evolve independently by defining expected behavior from the consumer perspective with automated contract validation in CI/CD.",
        "https://martinfowler.com/articles/microservices.html", "pattern"),
    KnowledgeAtom("Software_Architecture", "products not projects",
        "Microservice teams own their products over the full lifetime using 'you build, you run it' model, bringing developers into daily contact with production behavior.",
        "https://martinfowler.com/articles/microservices.html", "pattern"),
    KnowledgeAtom("Software_Architecture", "Conway's Law",
        "Conway's Law states organizations design systems whose structure mirrors their communication structure, motivating team alignment with service boundaries.",
        "https://martinfowler.com/articles/microservices.html", "pattern"),
    KnowledgeAtom("Software_Architecture", "evolutionary design",
        "Evolutionary design in microservices enables incremental migration by adding new features as services alongside existing systems, allowing gradual replacement of monolithic components.",
        "https://martinfowler.com/articles/microservices.html", "pattern"),
    KnowledgeAtom("Software_Architecture", "two pizza team",
        "The Two Pizza Team rule limits service teams to a size that can be fed by two pizzas, ensuring teams remain small enough for effective communication and ownership.",
        "https://martinfowler.com/articles/microservices.html", "pattern"),
    KnowledgeAtom("Software_Architecture", "continuous delivery",
        "Continuous Delivery is essential for microservices: automated testing, deployment pipelines, and infrastructure automation enable frequent, reliable deployments across many services.",
        "https://martinfowler.com/articles/microservices.html", "pattern"),
    KnowledgeAtom("Software_Architecture", "semantic monitoring",
        "Microservice architectures require semantic monitoring of both technical metrics (requests per second) and business metrics (orders per minute) to detect emergent behavior issues.",
        "https://martinfowler.com/articles/microservices.html", "pattern"),
    KnowledgeAtom("Software_Architecture", "service decomposition",
        "Good microservice decomposition keeps things that change together in the same service; repeatedly changing two services together signals they should be merged.",
        "https://martinfowler.com/articles/microservices.html", "pattern"),

    # === Production_Engineering additions (5 atoms from incident.io) ===
    KnowledgeAtom("Production_Engineering", "on-call rotations",
        "Effective on-call rotations require at least 8 engineers per rotation to prevent burnout, with clear escalation paths and automated runbooks for common incidents.",
        "https://incident.io/blog/best-incident-postmortem-software-2026-guide", "postmortem"),
    KnowledgeAtom("Production_Engineering", "incident severity levels",
        "Incidents should be classified by severity based on customer impact: SEV1 (complete outage), SEV2 (degraded service), SEV3 (minor issue) with different response SLAs per level.",
        "https://incident.io/blog/best-incident-postmortem-software-2026-guide", "postmortem"),
    KnowledgeAtom("Production_Engineering", "declaration-to-resolution pipeline",
        "Modern incident management follows a pipeline: detect, declare, triage, diagnose, mitigate, resolve, document, and prevent — each stage has specific tooling and automation.",
        "https://incident.io/blog/best-incident-postmortem-software-2026-guide", "postmortem"),
    KnowledgeAtom("Production_Engineering", "runbook automation",
        "Runbooks should be version-controlled, tested, and automated where possible. Common incident types should have documented runbooks that reduce MTTR by providing step-by-step guidance.",
        "https://incident.io/blog/best-incident-postmortem-software-2026-guide", "postmortem"),
    KnowledgeAtom("Production_Engineering", "incident commander role",
        "The Incident Commander role coordinates response without fixing — they track timeline, assign tasks, communicate status, and ensure the team follows the incident response process.",
        "https://incident.io/blog/best-incident-postmortem-software-2026-guide", "postmortem"),

    # === Cloud additions (8 atoms from AWS WA) ===
    KnowledgeAtom("Cloud", "well-architected framework",
        "AWS Well-Architected Framework provides six pillars: operational excellence, security, reliability, performance efficiency, cost optimization, and sustainability.",
        "https://aws.amazon.com/architecture/well-architected/", "article"),
    KnowledgeAtom("Cloud", "operational excellence pillar",
        "Operational excellence focuses on running and monitoring systems, automating changes, responding to events, and continually improving processes and procedures.",
        "https://aws.amazon.com/architecture/well-architected/", "article"),
    KnowledgeAtom("Cloud", "reliability pillar",
        "The reliability pillar ensures workloads perform intended functions and recover quickly from failure through distributed system design, recovery planning, and adaptation to change.",
        "https://aws.amazon.com/architecture/well-architected/", "article"),
    KnowledgeAtom("Cloud", "cell-based architecture",
        "Cell-based architecture increases resilience by applying fault isolation at the application level, limiting blast radius of failures to individual cells.",
        "https://docs.aws.amazon.com/wellarchitected/latest/reducing-scope-of-impact-with-cell-based-architecture/", "article"),
    KnowledgeAtom("Cloud", "disaster recovery",
        "Disaster Recovery planning requires defined RPO and RTO objectives, tested recovery procedures, and multi-region failover capability for critical workloads.",
        "https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/", "article"),
    KnowledgeAtom("Cloud", "cost optimization",
        "Cloud cost optimization requires understanding spending patterns, selecting right-sized resources, using reserved capacity, and implementing auto-scaling to match demand.",
        "https://aws.amazon.com/architecture/well-architected/", "article"),
    KnowledgeAtom("Cloud", "shared responsibility model",
        "Cloud security follows a shared responsibility model: AWS secures the cloud infrastructure, customers are responsible for security IN the cloud including data, configs, and access.",
        "https://aws.amazon.com/architecture/well-architected/", "article"),
    KnowledgeAtom("Cloud", "auto-scaling",
        "Auto-scaling dynamically adjusts compute resources based on load, adding capacity during traffic peaks and releasing resources during lulls to optimize cost and performance.",
        "https://aws.amazon.com/architecture/well-architected/", "article"),

    # === AI_Engineering additions (5 atoms) ===
    KnowledgeAtom("AI_Engineering", "fine-tuning",
        "Fine-tuning adapts a pre-trained LLM to a specific domain by training on curated datasets, improving output quality for specialized tasks at the cost of additional compute.",
        "https://dev.to/fahimulhaq/complete-guide-to-system-design-oc7", "article"),
    KnowledgeAtom("AI_Engineering", "embeddings",
        "Embeddings convert text into dense vector representations that capture semantic meaning, enabling similarity search, clustering, and retrieval for RAG pipelines.",
        "https://dev.to/fahimulhaq/complete-guide-to-system-design-oc7", "article"),
    KnowledgeAtom("AI_Engineering", "LLM evaluation",
        "LLM evaluation requires automated metrics (BLEU, ROUGE, accuracy) combined with human evaluation for subjective quality, hallucination rate, and factual consistency measurement.",
        "https://dev.to/fahimulhaq/complete-guide-to-system-design-oc7", "article"),
    KnowledgeAtom("AI_Engineering", "vector databases",
        "Vector databases store and index embeddings for efficient similarity search, using approximate nearest neighbor (ANN) algorithms for sub-millisecond retrieval at billion-scale.",
        "https://dev.to/fahimulhaq/complete-guide-to-system-design-oc7", "article"),
    KnowledgeAtom("AI_Engineering", "agentic AI",
        "Agentic AI systems autonomously reason, plan, and execute multi-step tasks using tools and external knowledge, requiring careful observability for safety and correctness.",
        "https://aws.amazon.com/what-is/agentic-ai/", "article"),

    # === Networking additions (3 atoms) ===
    KnowledgeAtom("Networking", "REST API design",
        "REST APIs use HTTP methods (GET, POST, PUT, DELETE) as verbs on resource URIs, with stateless interactions, cacheable responses, and layered system architecture.",
        "https://martinfowler.com/articles/microservices.html", "pattern"),
    KnowledgeAtom("Networking", "gRPC",
        "gRPC uses Protocol Buffers for typed service contracts with HTTP/2 transport, enabling bidirectional streaming, flow control, and low-latency inter-service communication.",
        "https://martinfowler.com/articles/microservices.html", "pattern"),
    KnowledgeAtom("Networking", "message queuing",
        "Message queues decouple producers from consumers with asynchronous communication, enabling buffering during load spikes, guaranteed delivery, and work distribution across workers.",
        "https://martinfowler.com/articles/microservices.html", "pattern"),

    # === Databases additions (3 atoms) ===
    KnowledgeAtom("Databases", "polyglot persistence",
        "Polyglot persistence uses different database technologies for different service needs: document stores for flexible schemas, relational for ACID transactions, time-series for metrics.",
        "https://martinfowler.com/articles/microservices.html", "pattern"),
    KnowledgeAtom("Databases", "distributed transactions",
        "Distributed transactions across services are notoriously difficult to implement; microservice architectures prefer eventual consistency with compensating operations instead.",
        "https://martinfowler.com/articles/microservices.html", "pattern"),
    KnowledgeAtom("Databases", "read replicas",
        "Read replicas offload query traffic from the primary database by maintaining synchronized copies, improving read throughput and reducing latency for reporting workloads.",
        "https://dev.to/fahimulhaq/complete-guide-to-system-design-oc7", "article"),

    # === Security additions (2 atoms) ===
    KnowledgeAtom("Security", "OWASP Top 10",
        "The OWASP Top 10 lists critical web application security risks including injection, broken authentication, sensitive data exposure, XXE, and broken access control.",
        "https://dev.to/fahimulhaq/complete-guide-to-system-design-oc7", "article"),
    KnowledgeAtom("Security", "encryption at rest and transit",
        "Data must be encrypted both at rest (using AES-256 for storage) and in transit (using TLS 1.3 for network communication) to protect against unauthorized access.",
        "https://aws.amazon.com/architecture/well-architected/", "article"),
]
