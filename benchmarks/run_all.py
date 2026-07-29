"""Run all benchmark suites and save reports to benchmarks/reports/."""
import sys; sys.path.insert(0, "src")
import json, time
from pathlib import Path
from collections import Counter

from compiler.benchmark.engine import BenchmarkSuite, BenchmarkReport
from compiler.generation.engine import EpisodeType

REPORTS_DIR = Path("benchmarks/reports")
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

DOMAINS = [
    "Systems", "Databases", "Networking", "DevOps", "Security",
    "Performance", "Testing", "Cloud", "Distributed_Systems",
    "Software_Architecture", "AI_Engineering", "Production_Engineering",
    "Human_Factors", "Foundations", "Algorithms",
]

def run_suite(name: str, num_ekrs: int, domains: list[str] | None = None,
              types: list[EpisodeType] | None = None,
              quality_target: str | None = None):
    suite = BenchmarkSuite()
    r = suite.run(num_ekrs=num_ekrs, domains=domains or DOMAINS, types=types)
    return r

def save(report: BenchmarkReport, name: str):
    path = REPORTS_DIR / f"{name}.json"
    path.write_text(json.dumps(report.to_dict(), indent=2))
    print(f"  Saved {path}")


def run_agent():
    """Agent benchmark: full mix, measure throughput + quality distribution."""
    print("\n[agent] 5000 EKRs, all domains/types")
    r = run_suite("agent", 5000)
    save(r, "agent")
    print(r.summary())


def run_coding():
    """Coding benchmark: bug_fix, code_review, refactoring, debugging, feature_impl."""
    print("\n[coding] 5000 EKRs, coding types")
    r = run_suite("coding", 5000, types=[
        EpisodeType.BUG_FIX, EpisodeType.CODE_REVIEW, EpisodeType.REFACTORING,
        EpisodeType.DEBUGGING_SESSION, EpisodeType.FEATURE_IMPLEMENTATION,
    ])
    save(r, "coding")
    print(r.summary())


def run_reasoning():
    """Reasoning depth benchmark: measure avg steps/decisions/evidence per type."""
    print("\n[reasoning] 10000 EKRs, all types, detailed depth analysis")
    suite = BenchmarkSuite()
    r = suite.run(10000)
    # Add reasoning depth breakdown
    save(r, "reasoning")
    print(r.summary())


def run_debugging():
    """Debugging benchmark: bug_fix, debugging_session, incident_response."""
    print("\n[debugging] 5000 EKRs, debugging types")
    r = run_suite("debugging", 5000, types=[
        EpisodeType.BUG_FIX, EpisodeType.DEBUGGING_SESSION, EpisodeType.INCIDENT_RESPONSE,
    ])
    save(r, "debugging")
    print(r.summary())


def run_production():
    """Production benchmark: 100K EKRs, validate throughput at scale."""
    print("\n[production] 100000 EKRs — throughput at scale")
    suite = BenchmarkSuite()
    r = suite.run(100000)
    save(r, "production")
    print(r.summary())


def run_architecture():
    """Architecture benchmark: architecture_decision, design_discussion, documentation."""
    print("\n[architecture] 5000 EKRs, architecture types")
    r = run_suite("architecture", 5000, types=[
        EpisodeType.ARCHITECTURE_DECISION, EpisodeType.DESIGN_DISCUSSION,
        EpisodeType.DOCUMENTATION, EpisodeType.PLANNING,
    ])
    save(r, "architecture")
    print(r.summary())


suites = {
    "agent": run_agent,
    "coding": run_coding,
    "reasoning": run_reasoning,
    "debugging": run_debugging,
    "production": run_production,
    "architecture": run_architecture,
}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", choices=list(suites) + ["all"], default="all")
    args = parser.parse_args()

    t0 = time.perf_counter()
    if args.suite == "all":
        for name, fn in suites.items():
            fn()
    else:
        suites[args.suite]()

    elapsed = time.perf_counter() - t0
    print(f"\nTotal: {elapsed:.1f}s")
