"""Spec-driven generation engine — produces realistic EKRs from .toon specs.

Reads domain concepts, incident types, feature requests, and engineering
thinking from compiled .toon specs to drive episode generation.
"""

import random
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from compiler.core.constants import Difficulty, Quality, Confidence, Severity, Priority
from compiler.ontology.ekr import EngineeringKnowledgeRecord
from compiler.ingestion.atoms import KnowledgeStore


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


DOMAIN_CONCEPTS: dict[str, list[str]] = {
    "Foundations": ["Mathematics", "Logic", "Set Theory", "Probability", "Computation Theory"],
    "Programming": ["Type Systems", "Memory Models", "Modules", "Packages", "Runtime"],
    "Algorithms": ["Searching", "Sorting", "Dynamic Programming", "Graph Algorithms"],
    "Data_Structures": ["Arrays", "Trees", "Hash Tables", "Graphs", "Tries"],
    "Systems": ["Processes", "Threads", "Scheduling", "Memory", "IPC"],
    "Compilers": ["Parsing", "AST", "IR", "Optimization", "Code Generation"],
    "Networking": ["TCP/IP", "HTTP", "DNS", "Load Balancing", "gRPC"],
    "Databases": ["Transactions", "Indexing", "Replication", "Sharding", "Consistency"],
    "Distributed_Systems": ["Consensus", "Leader Election", "CAP", "Fault Tolerance"],
    "Security": ["Authentication", "Authorization", "Cryptography", "Threat Modeling"],
    "Software_Architecture": ["Design Patterns", "Principles", "Technical Debt"],
    "Testing": ["Unit Testing", "Integration Testing", "Property Testing", "Fuzz Testing"],
    "DevOps": ["CI/CD", "Containers", "Kubernetes", "Monitoring"],
    "Performance": ["Profiling", "Benchmarking", "Parallelism", "Concurrency"],
    "Cloud": ["Compute", "Storage", "Serverless", "IAM"],
    "AI_Engineering": ["Machine Learning", "LLMs", "RAG", "Fine Tuning"],
    "Human_Factors": ["Collaboration", "Mentoring", "Communication", "Planning"],
    "Production_Engineering": ["Incidents", "Reliability", "Observability"],
}

INCIDENT_SCENARIOS: dict[str, list[dict]] = {
    "bug_fix": [
        {"problem": "Null pointer dereference in payment gateway", "cause": "Missing null check on upstream response", "fix": "Add defensive null check with structured error response"},
        {"problem": "Race condition in order processing", "cause": "Shared mutable state without synchronization", "fix": "Replace shared state with actor-based isolation"},
        {"problem": "Memory leak in cache layer", "cause": "Evicted entries not garbage collected", "fix": "Use weak references and configurable TTL eviction"},
        {"problem": "Data corruption in CSV export", "cause": "Unicode encoding mismatch between systems", "fix": "Normalize to UTF-8 with BOM at serialization boundary"},
        {"problem": "Incorrect aggregation in analytics pipeline", "cause": "Double-counting due to retry logic", "fix": "Make aggregation idempotent with dedup keys"},
    ],
    "incident_response": [
        {"problem": "Database connection pool exhausted", "cause": "Slow queries holding connections under load spike", "fix": "Add connection timeout, increase pool, optimize slow query"},
        {"problem": "Certificate expiry causes outage", "cause": "No monitoring on certificate expiration dates", "fix": "Add cert expiry monitoring with 30-day alert window"},
        {"problem": "DNS resolution failure cascades to all services", "cause": "Stale DNS cache with no fallback resolver", "fix": "Implement multi-resolver fallback chain"},
        {"problem": "Kubernetes node failure takes down critical pods", "cause": "No pod anti-affinity and single AZ deployment", "fix": "Add pod anti-affinity, spread across AZs"},
        {"problem": "Rate limiter blocks legitimate traffic", "cause": "Hash-based rate limiting creates hot shards", "fix": "Switch to sliding window with consistent hashing"},
    ],
    "performance_optimization": [
        {"problem": "Slow page load (8s P95)", "cause": "N+1 queries in API response composition", "fix": "Batch-load with DataLoader pattern"},
        {"problem": "High memory usage in data pipeline", "cause": "Loading entire dataset into memory before processing", "fix": "Stream-process with bounded buffer"},
        {"problem": "API latency spikes under concurrent load", "cause": "Thundering herd on cache expiry", "fix": "Add probabilistic early recompute with jitter"},
        {"problem": "Slow search queries (>500ms)", "cause": "Full table scan without covering index", "fix": "Add composite covering index for search columns"},
    ],
}

ENGINEERING_DECISIONS: dict[str, list[dict]] = {
    "architecture_decision": [
        {"decision": "Adopt event-driven architecture", "alternatives": ["Monolith", "Microservices"], "reasoning": "Better decoupling and scalability for domain events"},
        {"decision": "Use PostgreSQL over MongoDB", "alternatives": ["MongoDB", "Cassandra"], "reasoning": "Strong consistency needs and complex joins required"},
        {"decision": "Adopt gRPC for inter-service communication", "alternatives": ["REST", "GraphQL", "Message Queue"], "reasoning": "Low latency and typed contracts needed"},
        {"decision": "Implement CQRS pattern", "alternatives": ["CRUD", "Event Sourcing"], "reasoning": "Read/write workloads have different scaling needs"},
    ],
    "refactoring": [
        {"decision": "Extract monolith into bounded contexts", "alternatives": ["Rewrite", "Strangler fig"], "reasoning": "Incremental migration reduces risk"},
        {"decision": "Replace custom ORM with SQLAlchemy", "alternatives": ["Raw SQL", "Django ORM"], "reasoning": "Better maintainability and query optimization"},
        {"decision": "Introduce repository pattern", "alternatives": ["Active Record", "Data Mapper"], "reasoning": "Testability via abstraction over data access"},
    ],
}


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


REASONING_CHAINS: dict[str, list[str]] = {
    "bug_fix": ["Observe", "Diagnose", "Hypothesize", "Validate", "Implement", "Verify", "Reflect"],
    "incident_response": ["Detect", "Triage", "Diagnose", "Mitigate", "Resolve", "Document", "Prevent"],
    "performance_optimization": ["Measure", "Analyze", "Design", "Implement", "Benchmark", "Deploy", "Monitor"],
    "architecture_decision": ["Research", "Analyze", "Evaluate", "Decide", "Document", "Review", "Implement"],
    "code_review": ["Review", "Analyze", "Identify", "Comment", "Approve", "Reflect"],
    "feature_implementation": ["Plan", "Design", "Implement", "Test", "Review", "Deploy"],
    "refactoring": ["Analyze", "Design", "Migrate", "Test", "Verify", "Cleanup"],
    "design_discussion": ["Context", "Explore", "Compare", "Propose", "Decide", "Document"],
    "debugging_session": ["Reproduce", "Isolate", "Analyze", "Fix", "Verify"],
    "planning": ["Assess", "Prioritize", "Estimate", "Sequence", "Assign"],
    "documentation": ["Audit", "Outline", "Write", "Review", "Publish"],
    "technical_debt": ["Identify", "Quantify", "Prioritize", "Address", "Verify"],
}


class EpisodeGenerator:
    def __init__(self, seed: int = 42, knowledge_store: KnowledgeStore | None = None):
        self.seed = seed
        self._rng = random.Random(seed)
        self._knowledge = knowledge_store or KnowledgeStore()

    def generate(self, context: dict, episode_type: EpisodeType,
                 domain: str = "GEN") -> GenerationResult:
        import time
        t0 = time.perf_counter()
        ekr = EngineeringKnowledgeRecord.create(
            name=f"{episode_type.value}_{domain}",
            domain=domain,
        )

        concepts = list(DOMAIN_CONCEPTS.get(domain, ["General"]))
        atoms = self._knowledge.get_random(self._rng, domain, 2)
        scenario = self._pick_scenario(episode_type, concepts)
        reasoning_chain = REASONING_CHAINS.get(episode_type.value, ["Observe", "Analyze"])

        ekr.difficulty = self._pick_difficulty(episode_type)
        ekr.confidence = Confidence.C3

        for step in reasoning_chain:
            content = self._reasoning_content(step, episode_type, domain, scenario, concepts)
            ekr.add_reasoning(step, content, Confidence.C3)

        ekr.add_reasoning("Reflect",
            f"Lessons learned from {episode_type.value.replace('_', ' ')} in {domain}: "
            f"{scenario.get('fix', scenario.get('reasoning', 'Engineering insight'))}",
            Confidence.C4)

        decisions = ENGINEERING_DECISIONS.get(episode_type.value, [])
        if decisions:
            n_decisions = self._rng.randint(2, 3)
            self._rng.shuffle(decisions)
            for i in range(min(n_decisions, len(decisions))):
                d = decisions[i]
                ekr.add_decision(d["decision"], f"Context: {episode_type.value} in {domain}",
                               d.get("alternatives", ["Alternative approach"]), d["reasoning"])

        evidence_types = ["observation", "measurement", "log", "metric"]
        if "problem" in scenario:
            for et in evidence_types[:self._rng.randint(2, 3)]:
                ekr.evidence.append({
                    "type": et,
                    "content": scenario.get("cause", scenario["problem"]),
                    "source": f"{domain} engineering scenario",
                })

        ekr.knowledge_atoms = [f"KA-{domain}-{self._rng.randint(1000,9999)}"
                               for _ in range(self._rng.randint(2, 4))]

        elapsed = (time.perf_counter() - t0) * 1000
        return GenerationResult(ekr=ekr, episode_type=episode_type, duration_ms=elapsed)

    def _pick_scenario(self, episode_type: EpisodeType, concepts: list[str]) -> dict:
        scenarios = INCIDENT_SCENARIOS.get(episode_type.value, [])
        if scenarios:
            s = dict(self._rng.choice(scenarios))
        else:
            s = {"problem": f"Engineering challenge in {self._rng.choice(concepts)}",
                 "fix": "Standard engineering solution applied"}
        return s

    def _pick_difficulty(self, episode_type: EpisodeType) -> Difficulty:
        mapping = {
            EpisodeType.DOCUMENTATION: Difficulty.D1,
            EpisodeType.CODE_REVIEW: Difficulty.D2,
            EpisodeType.BUG_FIX: Difficulty.D2,
            EpisodeType.REFACTORING: Difficulty.D2,
            EpisodeType.FEATURE_IMPLEMENTATION: Difficulty.D3,
            EpisodeType.PLANNING: Difficulty.D3,
            EpisodeType.DEBUGGING_SESSION: Difficulty.D3,
            EpisodeType.PERFORMANCE_OPTIMIZATION: Difficulty.D3,
            EpisodeType.DESIGN_DISCUSSION: Difficulty.D3,
            EpisodeType.TECHNICAL_DEBT: Difficulty.D3,
            EpisodeType.ARCHITECTURE_DECISION: Difficulty.D4,
            EpisodeType.INCIDENT_RESPONSE: Difficulty.D4,
        }
        return mapping.get(episode_type, Difficulty.D2)

    def _reasoning_content(self, step: str, episode_type: EpisodeType,
                          domain: str, scenario: dict, concepts: list[str]) -> str:
        atom_ref = self._get_atom_content(domain)
        base = {
            "Observe": f"In {domain}, observed {scenario.get('problem', 'unexpected behavior')}",
            "Diagnose": f"Analysis of {domain} system suggests {scenario.get('cause', 'root cause in system interaction')}",
            "Hypothesize": f"Hypothesis: {scenario.get('cause', 'underlying issue in component boundary')}",
            "Validate": f"Validated hypothesis through {self._rng.choice(['log analysis', 'reproduction', 'metrics review', 'code inspection'])}",
            "Implement": f"Implementing: {scenario.get('fix', 'targeted fix')}",
            "Verify": f"Verified fix resolves issue in {domain} context",
            "Reflect": f"Lesson: {self._rng.choice(['add monitoring', 'defensive coding', 'earlier validation', 'document assumptions'])}",
            "Detect": f"Detected anomaly in {domain} — {scenario.get('problem', 'metric deviation')}",
            "Triage": f"Triaged as {self._rng.choice(['sev2', 'sev3'])} — impacts {self._rng.choice(concepts)}",
            "Mitigate": f"Applied {scenario.get('fix', 'mitigation strategy')}",
            "Resolve": f"Root cause: {scenario.get('cause', 'system interaction issue')}",
            "Document": f"Documenting {episode_type.value} process for {domain}",
            "Prevent": f"Preventive measure: {self._rng.choice(['add alert', 'update runbook', 'add test', 'review docs'])}",
            "Measure": f"Measured {self._rng.choice(['latency', 'throughput', 'memory', 'CPU'])}, baseline {self._rng.randint(100,5000)}ms",
            "Analyze": f"Analysis reveals bottleneck in {self._rng.choice(concepts)} component",
            "Design": f"Designing solution using {self._rng.choice(['caching', 'batching', 'pooling', 'indexing', 'partitioning'])}",
            "Benchmark": f"Benchmark shows {self._rng.randint(20,80)}% improvement over baseline",
            "Deploy": f"Deploying to {self._rng.choice(['staging', 'canary', 'production'])} with monitoring",
            "Research": f"Researching approaches for {scenario.get('problem', domain + ' challenge')}",
            "Evaluate": f"Evaluating tradeoffs between {self._rng.sample(concepts, min(2, len(concepts)))}",
            "Decide": f"Decision: adopt {self._rng.choice(['proven solution', 'new architecture', 'incremental refactor'])}",
            "Review": f"Reviewing code changes in {domain} — {self._rng.randint(1,5)} files changed",
            "Plan": f"Planning {episode_type.value} for {domain} with {self._rng.randint(2,5)} sprints",
            "Assess": f"Assessment: current state of {self._rng.choice(concepts)} needs improvement",
            "Prioritize": f"Priority: {self._rng.choice(['P1', 'P2'])} — business impact assessment complete",
            "Identify": f"Identified {self._rng.choice(['technical debt', 'code smell', 'anti-pattern'])} in {self._rng.choice(concepts)}",
            "Reproduce": f"Reproduced issue consistently in {self._rng.choice(['dev', 'staging'])} environment",
            "Isolate": f"Isolated to {self._rng.choice(['module boundary', 'dependency version', 'config parameter'])}",
            "Context": f"Context: {domain} system with {self._rng.randint(2,10)} services",
            "Explore": f"Explored {self._rng.randint(2,4)} potential approaches for {episode_type.value}",
            "Compare": f"Comparing approaches: {self._rng.choice(['performance', 'maintainability', 'cost'])} analysis",
            "Propose": f"Proposed solution addresses {scenario.get('problem', 'core engineering need')}",
        }
        content = base.get(step, f"Engineering step {step} for {episode_type.value} in {domain}")
        if atom_ref and self._rng.random() < 0.4:
            content += f" [Ref: {atom_ref}]"
        return content

    def _get_atom_content(self, domain: str) -> str:
        atoms = self._knowledge.get_random(self._rng, domain, 1)
        if atoms:
            a = atoms[0]
            return f"{a.concept}: {a.content[:100]}"
        return ""
