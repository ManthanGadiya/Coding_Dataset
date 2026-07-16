# TOON Dataset Compiler

> **Building the world's most comprehensive engineering dataset for training autonomous coding models.**
# TOON Dataset Compiler

> **Building the world's most comprehensive engineering dataset for training autonomous coding models.**

---

## Vision

Modern coding models are primarily trained on source code and natural language. While they generate code effectively, they often struggle with the deeper aspects of software engineering:

- Architectural reasoning
- Long-term planning
- Debugging methodology
- Trade-off analysis
- Production incident handling
- Decision making under constraints
- Large-scale repository evolution
- Engineering communication

The TOON Dataset Compiler aims to bridge this gap by creating a structured engineering knowledge representation rather than another collection of code snippets.

Instead of teaching models *what code looks like*, TOON teaches models *how engineers think*.

---

# What is TOON?

TOON is a domain-specific knowledge representation and dataset compiler designed for autonomous software engineering systems.

It converts raw engineering knowledge into structured, interconnected knowledge graphs that capture:

- Code
- Architecture
- Design decisions
- Bugs
- Reviews
- Documentation
- Production incidents
- Team interactions
- Engineering reasoning
- Long-term project evolution

Every generated example is represented as structured knowledge rather than isolated text.

---

# Goals

The project has six primary objectives.

## 1. Engineering Intelligence

Teach models engineering principles instead of memorizing syntax.

---

## 2. Structured Knowledge

Represent software engineering as interconnected knowledge graphs.

---

## 3. Autonomous Reasoning

Capture planning, reflection, debugging, hypothesis formation, and decision making.

---

## 4. Dataset Quality

Generate datasets that prioritize quality, consistency, diversity, and traceability over raw scale.

---

## 5. Extensibility

Provide a modular compiler architecture where every component can evolve independently.

---

## 6. Research Platform

Enable experimentation in:

- reasoning
- planning
- curriculum learning
- world simulation
- engineering cognition
- autonomous software development

---

# Core Principles

The compiler is built around several foundational principles.

- Knowledge before tokens
- Reasoning before answers
- Graphs before sequences
- Engineering before code
- Quality before quantity
- Deterministic generation
- Continuous validation
- Explainable decisions

---

# Compiler Pipeline

```
Raw Sources
      │
      ▼
Knowledge Extraction
      │
      ▼
Ontology Mapping
      │
      ▼
Reasoning Enrichment
      │
      ▼
Episode Generation
      │
      ▼
Validation
      │
      ▼
Repair
      │
      ▼
Optimization
      │
      ▼
Serialization
      │
      ▼
Release
```

---

# Repository Structure

```
compiler/
schemas/
templates/
golden/
ingestion/
tools/
workspace/
build/
release/
benchmarks/
docs/
experiments/
```

---

# Intended Applications

The generated datasets are designed for:

- Coding language models
- Autonomous coding agents
- Software engineering agents
- AI research
- Curriculum learning
- Knowledge graph research
- Tool-using agents
- Long-horizon planning systems

---

# Design Philosophy

Unlike traditional datasets, TOON does not treat software engineering as isolated programming tasks.

Instead, engineering is modeled as an evolving system consisting of:

- people
- repositories
- architecture
- requirements
- constraints
- failures
- discussions
- deployments
- production environments
- business decisions

Every artifact exists within a larger engineering context.

---

# Long-Term Vision

The long-term objective is to create a reusable engineering knowledge infrastructure capable of generating high-quality datasets for future generations of autonomous software engineering models.

Rather than maintaining static datasets, TOON aims to function as a continuously evolving dataset compiler capable of incorporating new knowledge, validating existing information, and generating increasingly realistic engineering scenarios.

---

# Current Status

Current Version:

```
v0.1 (Foundation)
```

Development Stage:

```
Architecture & Compiler Design
```

---

# License

See LICENSE for licensing information.

---

# Documentation

Additional documentation can be found in:

- docs/
- compiler/
- schemas/

---

# Contributing

Contributions are welcome after the core compiler architecture reaches stability.

Please see `CONTRIBUTING.md`.

---

# Citation

Coming soon.
---

## What is TOON?

TOON is a domain-specific knowledge representation and dataset compiler for autonomous software engineering systems. It converts raw engineering knowledge into structured, interconnected knowledge graphs — capturing code, architecture, design decisions, bugs, reviews, incidents, team interactions, and engineering reasoning.

Unlike traditional datasets that flatten engineering into text sequences, TOON preserves engineering as structured knowledge.

---

## Current Status

Version: `0.3.0` | Stage: **Production Dataset Generated**

| Component | Status |
|-----------|--------|
| 151 .toon spec files | Done |
| 11-layer pipeline | Done |
| 70+ passing tests | Done |
| World generator | Done |
| Dataset builder | Done |
| TOON parser | Done |
| Real-world knowledge ingestion | Done (73 atoms, 15 domains) |
| Production dataset | Done (100K Q4+) |

---

## Quick Start

```bash
git clone <repo>
cd Dataset
PYTHONPATH=src python main.py
```

Generate a production dataset (100K+ EKRs):

```bash
PYTHONPATH=src python scripts/generate_production.py
```

---

## Repository Structure

```
src/compiler/          # Python compiler implementation (12 modules)
  core/                #   Config, constants, pipeline, identifiers, lifecycle
  ontology/            #   EKR, knowledge graph, domain taxonomy, entities
  cognition/           #   Reasoning primitives, graphs, decision records
  curriculum/          #   Curriculum graph, difficulty distribution
  world/               #   Company/team/engineer/repo/incident models + generator
  generation/          #   Episode generator + dataset builder
  ingestion/           #   Real-world knowledge atoms, source acquisition
  repair/              #   Failure classification + auto-repair
  quality/             #   Multi-dimensional quality scoring
  validation/          #   9-domain validation engine
  optimization/        #   Deduplication + token optimization
  serialization/       #   JSONL/TOON exporters, TOON parser, manifests
compiler/              # 151 .toon spec files (source of truth)
tests/                 # 70+ passing tests (pytest)
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