# TOON Dataset Compiler Roadmap

> **Development roadmap for v0.2.0-dev.**

---

# Version History

## v0.1 — Foundation (Done)

Goal: Design complete compiler architecture.
Deliverables: Repository structure, documentation, architecture, all specs.

## v0.2 — Implementation (90% Done)

| Component | Status |
|-----------|--------|
| Core (config, constants, pipeline) | Done |
| Ontology (EKR, graph, 18 domains) | Done |
| Cognition (20 reasoning primitives) | Done |
| Curriculum (difficulty D0-D6) | Done |
| World (seeded generator, models) | Done |
| Generation (12 episode types, dataset builder) | Done |
| Repair (16 failure categories) | Done |
| Quality (10 scoring dimensions) | Done |
| Validation (9 domains) | Done |
| Optimization (dedup + tokens) | Done |
| Serialization (JSONL, TOON, parser, manifests) | Done |
| Pilot dataset generation | Pending |
| Full spec-driven generation | In Progress |

## v0.3 — Production Dataset (Next)

- Generate 100K+ EKR pilot
- Spec-driven full generation
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
