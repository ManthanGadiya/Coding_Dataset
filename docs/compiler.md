# Compiler Overview

> **v0.2.0-dev**

11-layer pipeline for transforming engineering knowledge into structured datasets.

## Pipeline

```
Core → Ontology → Cognition → Curriculum → World → Generation
  → Repair → Quality → Validation → Optimization → Serialization
```

## Entry Point

```python
PYTHONPATH=src python main.py
```

Programmatic:

```python
from compiler.generation.dataset import DatasetBuilder
b = DatasetBuilder()
result = b.build(num_worlds=2, episodes_per_world=3)
print(result.report())
```

## Configuration

`CompilerConfig` in `src/compiler/core/config.py`:
- seed (int): RNG seed for reproducibility
- execution_mode: DEVELOPMENT / TESTING / PRODUCTION / BENCHMARK / RESEARCH
- passes: per-stage PassConfig (enabled, mandatory)
- minimum_quality: Quality threshold for record acceptance
- workspace/output: Paths

## Source of Truth

151 `.toon` spec files in `compiler/` define all types, constants, and domain knowledge. Parsed by `ToonParser` at compile time.
