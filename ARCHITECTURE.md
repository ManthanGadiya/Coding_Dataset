# TOON Dataset Compiler Architecture

> **Complete architectural blueprint for v0.2.0-dev.**

---

# Introduction

Modular engineering knowledge compilation system. Transforms knowledge into structured training datasets for coding models.

Design: modular, extensible, reproducible, explainable, deterministic.

---

# Layered Architecture

| # | Module | Files | Responsibility | Status |
|---|--------|-------|----------------|--------|
| 00 | Core | 7 | Config, constants, pipeline, lifecycle, IDs, versioning, metadata | Done |
| 01 | Ontology | 6 | EKR, knowledge graph (MultiDiGraph), 18 domains, entities, atoms, dependencies | Done |
| 02 | Cognition | 1 | 20 reasoning primitives, reasoning graphs, decision records | Done |
| 03 | Curriculum | 1 | Curriculum graph, difficulty distribution D0-D6 | Done |
| 04 | World | 2 | Company/team/engineer/repo/incident models + seeded generator | Done |
| 05 | Generation | 2 | 12 episode types, episode generator, dataset builder pipeline | Done |
| 06 | Repair | 1 | 16 failure categories, auto-repair | Done |
| 07 | Quality | 1 | 10-dimensional scoring | Done |
| 08 | Validation | 1 | 9-domain validation | Done |
| 09 | Optimization | 1 | Deduplication + token optimization | Done |
| 10 | Serialization | 2 | JSONL/TOON exporters, TOON parser, manifests | Done |

**36 Python files | 70 tests | 151 .toon specs**

---

# Key Modules

## Engineering Knowledge Record (EKR)
`src/compiler/ontology/ekr.py` — Canonical knowledge object. Fields: id, metadata, domain, difficulty, quality, confidence, reasoning, decisions, tradeoffs, evidence, atoms, relationships.

## Knowledge Graph
`src/compiler/ontology/graph.py` — NetworkX MultiDiGraph wrapper. Typed relationships, neighbor traversal, graph validation.

## Reasoning
`src/compiler/cognition/engine.py` — 20 primitives: Observe, Identify, Classify, Compare, Relate, Infer, Predict, Hypothesize, Validate, Measure, Diagnose, Explain, Generalize, Specialize, Optimize, Decide, Reflect, Transfer, Synthesize, Decompose.

## World Simulation
`src/compiler/world/models.py` — EngineeringWorld → Company → Team → Engineer + Repository + Incident + FeatureRequest. Seeded deterministic generation across 10 domains.

## Dataset Builder
`src/compiler/generation/dataset.py` — Orchestrates: generate worlds → episodes → validate → repair → score → optimize → serialize.

## TOON Parser
`src/compiler/serialization/toon_parser.py` — Parses all 151 .toon spec files. Indentation-based syntax.

## Validation
`src/compiler/validation/engine.py` — 9 domains: schema, graph, reasoning, fact, execution, security, consistency, dataset, final.

## Quality
`src/compiler/quality/engine.py` — 10 dimensions: knowledge_density, reasoning_depth, engineering_quality, diversity, realism, novelty, educational_value, completeness, consistency, coherence.

## Repair
`src/compiler/repair/engine.py` — 16 failure categories: structural, semantic, knowledge, reasoning, engineering, graph, curriculum, diversity, confidence, quality, token, consistency, completeness, accuracy, validation, security.

---

# Data Flow

```
.toon specs → TOON Parser → Config
  → WorldGenerator → EngineeringWorld
  → EpisodeGenerator → EKR
  → ValidationEngine → passes/fails
  → RepairEngine → auto-fixes
  → QualityEngine → score (0-5)
  → OptimizationEngine → dedup + truncate
  → Serialization → JSONL + TOON + manifest
```

---

# Design Goals

| Goal | Implementation |
|------|---------------|
| Deterministic | Seeded RNG, fixed order |
| Modular | 11 independent modules |
| Extensible | Add domains/episodes via enums |
| Explainable | Traceable reasoning chains |
| Graph Native | NetworkX MultiDiGraph |
| Reproducible | Same seed → same output |
| Quality Gated | Minimum threshold for release |

---

# Principles

1. Single Responsibility
2. Graph First
3. Deterministic
4. Explainable
5. Continuous Validation
6. Quality Gated