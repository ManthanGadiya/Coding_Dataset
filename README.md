# TOON Dataset Compiler

> **Building the world's most comprehensive engineering dataset for training autonomous coding models.**

---

## What is TOON?

TOON is a domain-specific knowledge representation and dataset compiler for autonomous software engineering systems. It converts raw engineering knowledge into structured, interconnected knowledge graphs — capturing code, architecture, design decisions, bugs, reviews, incidents, team interactions, and engineering reasoning.

Unlike traditional datasets that flatten engineering into text sequences, TOON preserves engineering as structured knowledge.

---

## Current Status

Version: `0.2.0-dev` | Stage: **Compiler Implementation Complete**

| Component | Status |
|-----------|--------|
| 151 .toon spec files | Done |
| 11-layer pipeline | Done |
| 70 passing tests | Done |
| World generator | Done |
| Dataset builder | Done |
| TOON parser | Done |
| Pilot dataset | Pending |

---

## Quick Start

```bash
git clone <repo>
cd Dataset
PYTHONPATH=src python main.py
```

Generate a pilot dataset:

```bash
PYTHONPATH=src python -c "
from compiler.generation.dataset import DatasetBuilder
b = DatasetBuilder()
r = b.build(num_worlds=2, episodes_per_world=3, num_ekrs=5)
print(r.report())
"
```

---

## Repository Structure

```
src/compiler/          # Python compiler implementation (11 modules)
  core/                #   Config, constants, pipeline, identifiers, lifecycle
  ontology/            #   EKR, knowledge graph, domain taxonomy, entities
  cognition/           #   Reasoning primitives, graphs, decision records
  curriculum/          #   Curriculum graph, difficulty distribution
  world/               #   Company/team/engineer/repo/incident models + generator
  generation/          #   Episode generator + dataset builder
  repair/              #   Failure classification + auto-repair
  quality/             #   Multi-dimensional quality scoring
  validation/          #   9-domain validation engine
  optimization/        #   Deduplication + token optimization
  serialization/       #   JSONL/TOON exporters, TOON parser, manifests
compiler/              # 151 .toon spec files (source of truth)
tests/                 # 70 passing tests (pytest)
schemas/               # 7 JSON schema files
docs/                  # Module documentation
main.py                # Entry point
```

---

## Architecture

11-layer pipeline:

```
Core → Ontology → Cognition → Curriculum → World → Generation
  → Repair → Quality → Validation → Optimization → Serialization
```

Each layer has a single responsibility. Every generated artifact is traceable, validated, and scored.

---

## Design Philosophy

Engineering is not just programming. TOON models engineering as:

- Knowledge graphs (not text sequences)
- Reasoning chains (not final answers)
- Evolving worlds (not isolated examples)
- Trade-offs and decisions (not single solutions)
- Context and constraints (not abstract problems)

---

## Documentation

- `ARCHITECTURE.md` — Complete architectural blueprint
- `ROADMAP.md` — Development roadmap and milestones
- `docs/` — Per-module documentation
- `compiler/` — Spec files (source of truth)
- `schemas/` — JSON schema definitions

---

## License

See LICENSE.