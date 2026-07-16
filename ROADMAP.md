# TOON Dataset Compiler Roadmap

> **Development roadmap for v0.2.0-dev.**

---

# Version History

## v0.1 — Foundation (Done)

Goal: Design complete compiler architecture.
Deliverables: Repository structure, documentation, architecture, all specs.

## v0.2 — Implementation (Done)

All 11 modules implemented. 70 tests. 100K EKR pilot at Q4+ quality.

| Component | Status |
|-----------|--------|
| All 11 compiler modules | Done |
| 70 passing tests | Done |
| Spec-driven generation (12 types, domain concepts) | Done |
| 10-dimensional quality scoring | Done |
| 100K EKR pilot at Q4+ avg (4.03) | Done |

## v0.3 — Production Dataset (Next)

- Generate 1M+ EKR dataset
- Build real-world sources (Firecrawl)
- Benchmark suite
- Public dataset release

---

# Milestones

| M | Description | Status |
|---|-------------|--------|
| M1 | Compiler architecture complete | Done |
| M2 | Ontology implemented | Done |
| M3 | World simulation | Done |
| M4 | Generation pipeline | Done |
| M5 | Validation pipeline | Done |
| M6 | Optimization pipeline | Done |
| M7 | Pilot dataset released | Pending |
| M8 | Public v1.0 release | Future |

---

# Principles

- Build foundations before features
- Correctness over speed
- Quality over quantity
- Extensibility over shortcuts
- Every subsystem independently testable
- Every release reproducible
