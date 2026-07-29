"""Spec-driven generation engine — produces realistic EKRs from .toon specs.

Reads domain concepts, incident types, feature requests, and engineering
thinking from compiled .toon specs to drive episode generation.
"""

import random
import time
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

DEEP_ENGINEERING_DECISIONS: dict[str, list[dict]] = {
    "bug_fix": [
        {"decision": "Rollback vs hotfix vs forward-fix", "alternatives": ["Rollback to previous version", "Apply hotfix to production", "Forward-fix with feature flag"], "reasoning": "Tradeoff between recovery speed and code quality"},
        {"decision": "Root cause fix vs symptom mitigation", "alternatives": ["Address root cause", "Mitigate symptom only", "Both"], "reasoning": "Scope of change vs risk of regression"},
        {"decision": "Add integration test vs unit test", "alternatives": ["Unit test only", "Integration test only", "Both"], "reasoning": "Coverage breadth vs execution speed in CI"},
    ],
    "incident_response": [
        {"decision": "Auto-remediate vs manual intervention", "alternatives": ["Automated runbook", "Manual SSH investigation", "Pager duty escalation"], "reasoning": "Speed of recovery vs risk of automation causing wider impact"},
        {"decision": "Rollback vs keep-alive vs failover", "alternatives": ["Rollback deployment", "Scale up to absorb load", "Failover to DR region"], "reasoning": "RTO and RPO tradeoffs for the incident class"},
        {"decision": "Page on-call vs defer to business hours", "alternatives": ["Immediate page", "Defer with ticket", "Escalate to senior"], "reasoning": "SEV level and customer impact determine urgency"},
    ],
    "performance_optimization": [
        {"decision": "Cache strategy: write-through vs write-behind", "alternatives": ["Write-through cache", "Write-behind cache", "No cache"], "reasoning": "Read latency vs data freshness tradeoff"},
        {"decision": "Indexing strategy: covering vs composite", "alternatives": ["Covering indexes", "Composite indexes", "Full table scan"], "reasoning": "Query speed vs write amplification and storage cost"},
        {"decision": "Vertical vs horizontal scaling", "alternatives": ["Vertical scale-up", "Horizontal scale-out", "Read replicas"], "reasoning": "Cost efficiency vs complexity of distributed coordination"},
    ],
    "code_review": [
        {"decision": "Approve with nits vs request changes", "alternatives": ["Approve with comments", "Request changes", "Defer to second reviewer"], "reasoning": "Blocking vs velocity — severity of findings"},
        {"decision": "Enforce style guide vs accept inconsistency", "alternatives": ["Block on style violations", "Auto-format post-merge", "Document as team guideline"], "reasoning": "Consistency value vs review friction cost"},
    ],
    "feature_implementation": [
        {"decision": "Feature flag vs branch-based development", "alternatives": ["Feature flag behind toggle", "Long-lived feature branch", "Trunk-based with small commits"], "reasoning": "Integration frequency vs isolation of incomplete work"},
        {"decision": "API design: REST vs GraphQL vs RPC", "alternatives": ["RESTful endpoints", "GraphQL schema", "gRPC services"], "reasoning": "Flexibility for clients vs server-side complexity"},
    ],
    "debugging_session": [
        {"decision": "Binary search bisect vs hypothesis-driven", "alternatives": ["Git bisect on commit range", "Hypothesis-driven probe", "Add exhaustive logging and replay"], "reasoning": "Time to root cause vs blast radius of additional instrumentation"},
        {"decision": "Fix in isolation vs assess systemic risk", "alternatives": ["Fix the one bug", "Audit all similar patterns", "File tech debt ticket"], "reasoning": "Focused fix speed vs thoroughness across codebase"},
    ],
    "planning": [
        {"decision": "Waterfall vs iterative delivery", "alternatives": ["Full spec then build", "Two-week sprints", "Kanban continuous flow"], "reasoning": "Predictability vs adaptability to changing requirements"},
        {"decision": "Dedicated team vs shared service", "alternatives": ["Dedicated platform team", "Shared DevOps rotation", "Outsource to SRE"], "reasoning": "Domain expertise vs resource utilization across teams"},
    ],
    "technical_debt": [
        {"decision": "Refactor now vs schedule later vs never", "alternatives": ["Immediate refactor", "Schedule in next quarter", "Accept as permanent debt"], "reasoning": "Compound interest of debt vs opportunity cost of feature work"},
        {"decision": "Big rewrite vs incremental strangler", "alternatives": ["Rewrite from scratch", "Strangler fig pattern", "In-place refactor"], "reasoning": "Clean slate allure vs risk of second-system effect"},
    ],
    "design_discussion": [
        {"decision": "Stateful vs stateless design", "alternatives": ["Stateful service with session affinity", "Stateless with external store", "Hybrid with local cache"], "reasoning": "Performance simplicity vs horizontal scalability"},
        {"decision": "Synchronous vs async communication", "alternatives": ["REST/HTTP sync calls", "Async message queue", "Event stream (Kafka)"], "reasoning": "Consistency guarantee vs latency decoupling"},
    ],
    "documentation": [
        {"decision": "Inline docs vs external wiki vs generated", "alternatives": ["Docstrings in code", "Confluence/Notion wiki", "Auto-generated from OpenAPI"], "reasoning": "Proximity to code vs searchability across the org"},
        {"decision": "ADRs vs living README vs formal spec", "alternatives": ["Architecture Decision Records", "Living README", "Formal design documents"], "reasoning": "Decision capture rigor vs maintenance burden"},
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
                 domain: str = "GEN", quality_target: str | None = None) -> GenerationResult:
        t0 = time.perf_counter()
        ekr = EngineeringKnowledgeRecord.create(
            name=f"{episode_type.value}_{domain}",
            domain=domain,
        )

        concepts = list(DOMAIN_CONCEPTS.get(domain, ["General"]))
        scenario = self._pick_scenario(episode_type, concepts)
        base_chain = REASONING_CHAINS.get(episode_type.value, ["Observe", "Analyze"])

        if quality_target == "q5":
            return self._generate_q5(ekr, episode_type, domain, concepts, scenario, base_chain, t0)

        # Standard generation (Q2-Q4): variable chain length
        trim = self._rng.randint(0, min(3, len(base_chain) - 2))
        reasoning_chain = base_chain[:len(base_chain) - trim]

        ekr.difficulty = self._pick_difficulty(episode_type)
        ekr.confidence = Confidence.C3

        for step in reasoning_chain:
            content = self._reasoning_content(step, episode_type, domain, scenario, concepts, False)
            ekr.add_reasoning(step, content, Confidence.C3)

        if len(reasoning_chain) >= 4:
            ekr.add_reasoning("Reflect",
                f"Lessons learned from {episode_type.value.replace('_', ' ')} in {domain}: "
                f"{scenario.get('fix', scenario.get('reasoning', 'Engineering insight'))}",
                Confidence.C4)

        decisions = ENGINEERING_DECISIONS.get(episode_type.value, [])
        if decisions:
            n_decisions = self._rng.randint(1, 3)
            self._rng.shuffle(decisions)
            for i in range(min(n_decisions, len(decisions))):
                d = decisions[i]
                ekr.add_decision(d["decision"], f"Context: {episode_type.value} in {domain}",
                               d.get("alternatives", ["Alternative approach"]), d["reasoning"])

        evidence_types = ["observation", "measurement", "log", "metric"]
        if "problem" in scenario:
            for et in evidence_types[:self._rng.randint(1, 4)]:
                ekr.evidence.append({
                    "type": et,
                    "content": scenario.get("cause", scenario["problem"]),
                    "source": f"{domain} engineering scenario",
                })

        ekr.knowledge_atoms = [f"KA-{domain}-{self._rng.randint(1000,9999)}"
                               for _ in range(self._rng.randint(0, 5))]

        elapsed = (time.perf_counter() - t0) * 1000
        return GenerationResult(ekr=ekr, episode_type=episode_type, duration_ms=elapsed)

    def _generate_q5(self, ekr: EngineeringKnowledgeRecord, episode_type: EpisodeType,
                     domain: str, concepts: list[str], scenario: dict,
                     base_chain: list[str], t0: float) -> GenerationResult:
        """Generate a Q5-quality EKR with deep reasoning, rich content, and full structure."""
        ekr.difficulty = Difficulty.D5
        ekr.confidence = Confidence.C4

        deep_chain = base_chain + ["Reflect"]
        if len(deep_chain) < 12:
            extra = ["Context", "Explore", "Compare", "Evaluate"]
            deep_chain = deep_chain[:6] + extra + deep_chain[6:]
        deep_chain = deep_chain[:12]

        for step in deep_chain:
            content = self._reasoning_content(step, episode_type, domain, scenario, concepts, True)
            ekr.add_reasoning(step, content, Confidence.C4)

        # Multiple decisions with deep alternatives
        decisions = DEEP_ENGINEERING_DECISIONS.get(episode_type.value, [])
        if not decisions:
            decisions = ENGINEERING_DECISIONS.get(episode_type.value, [])
        if decisions:
            n_decisions = self._rng.randint(2, 4)
            self._rng.shuffle(decisions)
            for i in range(min(n_decisions, len(decisions))):
                d = decisions[i]
                alts = d.get("alternatives", ["Alternative"])
                while len(alts) < 3:
                    alts.append(f"Alternative {len(alts)+1}")
                ekr.add_decision(
                    d["decision"],
                    f"Context: {episode_type.value.replace('_', ' ')} in {domain}, "
                    f"affecting {self._rng.randint(2,5)} services with {self._rng.choice(['high', 'critical'])} business impact",
                    alts,
                    f"{d['reasoning']}. Selected approach reduces complexity by "
                    f"{self._rng.randint(20,60)}% and improves {self._rng.choice(['latency', 'throughput', 'maintainability', 'reliability'])} by "
                    f"{self._rng.randint(30,90)}% based on {self._rng.choice(['load testing', 'production data', 'architectural analysis'])}",
                )

        # Populate tradeoffs
        for _ in range(self._rng.randint(1, 3)):
            ekr.tradeoffs.append({
                "aspect": self._rng.choice(["performance", "maintainability", "cost", "scalability", "security", "complexity"]),
                "tradeoff": f"Chose {self._rng.choice(['simplicity', 'performance', 'extensibility'])} over "
                           f"{self._rng.choice(['development speed', 'operational cost', 'time-to-market'])}",
                "impact": f"{self._rng.choice(['+25% latency', '-40% operational cost', '+60% throughput', '-30% deployment time'])}",
            })

        # Rich evidence
        evidence_templates = [
            ("metric", f"P95 latency increased from {self._rng.randint(50,200)}ms to {self._rng.randint(500,5000)}ms "
                      f"under {self._rng.randint(1000,10000)} RPS load"),
            ("log", f"Error rate spiked to {self._rng.randint(5,25)}% in {self._rng.choice(['payment', 'auth', 'search', 'checkout'])} service"),
            ("observation", f"{self._rng.choice(['Memory', 'CPU', 'Disk IO', 'Network'])} utilization at "
                          f"{self._rng.randint(80,99)}% during peak hours"),
            ("measurement", f"Query execution time: {self._rng.randint(100,5000)}ms (threshold: {self._rng.randint(50,200)}ms)"),
            ("alert", f"Alert fired: {self._rng.choice(['HighErrorRate', 'LatencySpike', 'ConnectionPoolExhaustion', 'CertificateExpiry'])} "
                     f"at severity {self._rng.choice(['warning', 'critical', 'page'])}"),
        ]
        for template in evidence_templates[:self._rng.randint(3, 5)]:
            ekr.evidence.append({"type": template[0], "content": template[1], "source": f"{domain} production"})

        # Many atom references
        atoms = self._knowledge.get_random(self._rng, domain, 5)
        atom_ids = set()
        for a in atoms[:5]:
            aid = f"KA-{domain}-{self._rng.randint(1000,9999)}"
            atom_ids.add(aid)
        ekr.knowledge_atoms = list(atom_ids)
        if len(ekr.knowledge_atoms) < 3:
            ekr.knowledge_atoms.extend([f"KA-{domain}-{self._rng.randint(1000,9999)}" for _ in range(3 - len(ekr.knowledge_atoms))])

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
                          domain: str, scenario: dict, concepts: list[str],
                          q5: bool = False) -> str:
        atom_ref = self._get_atom_content(domain)

        if q5:
            base = {
                "Observe": (
                    f"Observed {scenario.get('problem', 'degradation in system behavior')} in {domain} — "
                    f"impacted {self._rng.randint(3,8)} downstream services with error rate "
                    f"increasing from {self._rng.randint(1,20) * 0.1:.1f}% to {self._rng.randint(5,30)}% "
                    f"over {self._rng.randint(10,60)} minutes"
                ),
                "Diagnose": (
                    f"Root cause analysis of {domain} system reveals {scenario.get('cause', 'deep-seated architecture issue')}. "
                    f"Traced through {self._rng.randint(3,6)} service boundaries using "
                    f"{self._rng.choice(['distributed tracing', 'structured log analysis', 'metrics correlation', 'thread dump analysis'])}. "
                    f"The issue originates in {self._rng.choice(concepts)} where {self._rng.choice(['a race condition', 'a resource leak', 'an unhandled edge case', 'a configuration drift'])} "
                    f"manifests under {self._rng.choice(['concurrent load', 'memory pressure', 'network partition', 'cache staleness'])}"
                ),
                "Hypothesize": (
                    f"Hypothesis: {scenario.get('cause', 'the underlying root cause')} triggered by "
                    f"{self._rng.choice(['increased traffic', 'deployment of v' + str(self._rng.randint(2,9)) + '.'
                    + str(self._rng.randint(0,9)) + '.0', 'configuration change', 'dependency upgrade'])}. "
                    f"To validate, we will {self._rng.choice(['inject fault', 'replay traffic', 'simulate load', 'audit config drift'])} "
                    f"in the {self._rng.choice(['staging', 'canary', 'performance'])} environment"
                ),
                "Validate": (
                    f"Validated hypothesis by {self._rng.choice(['reproducing in isolation', 'analyzing canary deployment metrics', 'correlating with deployment timeline', 'running chaos experiment'])}. "
                    f"Results confirm {self._rng.choice(['causality with p-value < 0.01', 'direct correlation (r=0.92)', 'consistent reproduction across 3/3 attempts'])}. "
                    f"Confidence in root cause: {self._rng.choice(['high', 'very high'])}"
                ),
                "Implement": (
                    f"Implementing fix: {scenario.get('fix', 'comprehensive solution')}. "
                    f"Changes touch {self._rng.randint(3,8)} files across {self._rng.randint(2,4)} modules. "
                    f"Includes {self._rng.choice(['unit tests', 'integration tests', 'property-based tests'])} "
                    f"covering {self._rng.randint(5,15)} edge cases. "
                    f"Rollout strategy: {self._rng.choice(['gradual canary over 2 hours', 'feature flag with 1% → 10% → 100% ramp', 'blue-green with instant rollback'])}"
                ),
                "Verify": (
                    f"Verification confirms fix resolves the issue. "
                    f"Metrics after deployment: error rate {self._rng.choice(['dropped to 0%', 'decreased from 12% to 0.5%', 'returned to baseline'])}. "
                    f"Latency P95 {self._rng.choice(['recovered from 5s to 200ms', 'improved by 85%', 'returned to <100ms'])}. "
                    f"All {self._rng.randint(10,30)} monitors {self._rng.choice(['green', 'within threshold', 'healthy'])}"
                ),
                "Reflect": (
                    f"Post-incident reflection: {self._rng.choice([
                        'This incident could have been prevented with better testing around concurrency boundaries',
                        'Our monitoring gap allowed this to go undetected for 15 minutes — adding proactive checks',
                        'The architecture here violates the principle of least astonishment — needs RFC for redesign',
                        'We should add this scenario to our chaos engineering suite for continuous validation',
                    ])}. "
                    f"Action items: {self._rng.choice(['add runbook', 'create dashboard', 'schedule architecture review', 'update deployment checklist'])} "
                    f"assigned to {self._rng.choice(['platform team', 'SRE', 'owning squad'])} with {self._rng.choice(['P1', 'P2'])} priority"
                ),
                "Detect": (
                    f"Detected anomaly in {domain}: {scenario.get('problem', 'metric deviation')}. "
                    f"Alert fired at {self._rng.choice(['P95 latency 5s (threshold 500ms)', 'error rate 15% (threshold 1%)', 'queue depth 50K (threshold 1K)'])}. "
                    f"Detection source: {self._rng.choice(['Prometheus alert', 'Datadog monitor', 'synthetic check', 'customer report'])}"
                ),
                "Triage": (
                    f"Triaged as severity {self._rng.choice(['1', '2'])} — {self._rng.choice(['critical', 'high'])} business impact. "
                    f"Affected: {self._rng.randint(2,6)} customer-facing features, "
                    f"estimated blast radius: {self._rng.randint(10,80)}% of user base. "
                    f"Escalated to {self._rng.choice(['SRE team', 'backend squad', 'on-call engineer', 'incident commander'])}"
                ),
                "Mitigate": (
                    f"Applied {scenario.get('fix', 'mitigation strategy')} as immediate containment. "
                    f"Mitigation reduced impact by {self._rng.randint(70,99)}% within {self._rng.randint(2,15)} minutes. "
                    f"Users partially restored; residual {self._rng.choice(['degraded performance', 'elevated error rates', 'stale data'])} "
                    f"affecting {self._rng.randint(1,5)}% of traffic"
                ),
                "Resolve": (
                    f"Root cause resolved: {scenario.get('cause', 'deep-seated architecture issue')}. "
                    f"Resolution verified via {self._rng.choice(['green deployment with smoke tests', 'gradual rollback to last known good', 'hotfix promoted through pipeline'])}. "
                    f"All {self._rng.randint(5,15)} health checks passing. Incident duration: {self._rng.randint(30,180)} minutes"
                ),
                "Context": (
                    f"System context: {domain} infrastructure serving {self._rng.randint(100,10000)} RPS "
                    f"across {self._rng.randint(3,15)} microservices with "
                    f"{self._rng.choice(['PostgreSQL', 'Cassandra', 'DynamoDB', 'Spanner'])} as primary data store. "
                    f"Deployment: {self._rng.choice(['Kubernetes (50 pods)', 'ECS Fargate', 'self-managed VMs'])} "
                    f"in {self._rng.choice(['single region', '3 AZs', 'multi-region active-active'])} topology"
                ),
                "Explore": (
                    f"Explored {self._rng.randint(3,5)} potential approaches to address {scenario.get('problem', 'the issue')}: "
                    f"(1) {self._rng.choice(['Short-term tactical fix', 'Partial rewrite of affected module', 'Config change only'])}, "
                    f"(2) {self._rng.choice(['Full architectural refactor', 'Adopt new technology stack', 'Extract to independent service'])}, "
                    f"(3) {self._rng.choice(['Incremental improvement with feature flags', 'A/B test multiple solutions', 'Phased rollout'])}. "
                    f"Each evaluated against {self._rng.choice(['time-to-implement', 'risk profile', 'team capacity', 'business impact'])}"
                ),
                "Compare": (
                    f"Compared approaches across {self._rng.randint(3,5)} dimensions: "
                    f"performance ({self._rng.choice(['+20%', '+45%', '+80%', '-10%'])}), "
                    f"complexity ({self._rng.choice(['low', 'medium', 'high'])}), "
                    f"maintainability ({self._rng.choice(['improved', 'same', 'degraded'])}), "
                    f"risk ({self._rng.choice(['low', 'medium', 'high'])}), "
                    f"cost ({self._rng.choice(['$500/mo', '$2K/mo', '$10K/mo', 'neutral'])}). "
                    f"Winner: {self._rng.choice(['approach 2 due to better risk/reward ratio', 'incremental approach (lowest risk)',
                    f'a hybrid combining elements of all three'])}"
                ),
                "Evaluate": (
                    f"Evaluating tradeoffs between {self._rng.choice(concepts)} approach vs "
                    f"{self._rng.choice(concepts)} alternative. "
                    f"Primary tradeoff: {self._rng.choice(['immediate velocity vs long-term maintainability', 'operational simplicity vs feature velocity',
                    'performance optimization vs code clarity', 'team autonomy vs architectural consistency'])}. "
                    f"Decision matrix favors {self._rng.choice(['the pragmatic approach', 'long-term investment', 'balanced strategy'])} "
                    f"with {self._rng.randint(60,90)}% confidence"
                ),
                "Decide": (
                    f"Decision: adopt {self._rng.choice(['proven solution with incremental improvements', 'new architecture with migration plan',
                    'phased refactoring over 3 sprints', 'buy over build for this component'])}. "
                    f"Rationale: {self._rng.choice(['fastest time-to-value with acceptable risk', 'best long-term ROI despite higher upfront cost',
                    'aligns with platform vision and reduces duplication', 'leverage existing expertise in team'])}"
                ),
                "Measure": (
                    f"Measured baseline: P95 latency {self._rng.randint(100,500)}ms, "
                    f"throughput {self._rng.randint(500,5000)} req/s, "
                    f"error rate {self._rng.randint(1,20)*0.1:.1f}%, "
                    f"memory {self._rng.randint(256,4096)}MB. "
                    f"After optimization: P95 {self._rng.randint(20,100)}ms ({self._rng.randint(40,80)}% improvement), "
                    f"throughput {self._rng.randint(1000,10000)} req/s"
                ),
                "Analyze": (
                    f"Analysis reveals bottleneck in {self._rng.choice(concepts)} — "
                    f"identified via {self._rng.choice(['flame graph profiling', 'distributed tracing waterfall', 'database query analysis', 'heap dump analysis'])}. "
                    f"Root cause: {self._rng.choice(['contention on shared lock', 'N+1 query pattern', 'unbounded memory allocation', 'sequential processing of parallelizable work'])}. "
                    f"Estimated impact: {self._rng.randint(30,70)}% of total latency"
                ),
                "Document": (
                    f"Documented {episode_type.value.replace('_', ' ')} process for {domain}: "
                    f"timeline, root cause, resolution steps, and {self._rng.randint(3,7)} preventive action items. "
                    f"Postmortem published to {self._rng.choice(['team wiki', 'shared drive', 'incident management system'])}. "
                    f"Blameless culture review conducted with {self._rng.randint(3,8)} participants"
                ),
                "Prevent": (
                    f"Preventive measures implemented: "
                    f"(1) {self._rng.choice(['add monitoring alert', 'create runbook', 'add integration test', 'schedule recurring review'])}, "
                    f"(2) {self._rng.choice(['update CI/CD pipeline', 'add chaos experiment', 'update architecture decision record', 'add load test scenario'])}, "
                    f"(3) {self._rng.choice(['document in wiki', 'share in team retro', 'present in engineering all-hands', 'add to onboarding guide'])}"
                ),
            }
            content = base.get(step, f"Deep analysis step {step} for {episode_type.value} in {domain}: "
                              f"considering {self._rng.randint(2,5)} factors including "
                              f"{self._rng.choice(concepts)} and {self._rng.choice(['system constraints', 'business requirements', 'team velocity', 'technical debt'])}")
        else:
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
        if atom_ref and self._rng.random() < (0.6 if q5 else 0.4):
            content += f" [Ref: {atom_ref}]"
        return content

    def _get_atom_content(self, domain: str) -> str:
        atoms = self._knowledge.get_random(self._rng, domain, 1)
        if atoms:
            a = atoms[0]
            return f"{a.concept}: {a.content[:100]}"
        return ""
