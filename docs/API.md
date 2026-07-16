# API Reference

> **v0.2.0-dev**

## Core

### CompilerConfig
`src/compiler/core/config.py`
- `CompilerConfig.default()` — Create default config
- `CompilerConfig.load(path)` — Load from JSON
- Fields: name, codename, version, execution_mode, execution_strategy, seed, passes, workspace, output, fail_fast, minimum_quality, release_quality

### Constants
`src/compiler/core/constants.py`
- Enums: Priority (P0-P4), Severity (S0-S4), Risk (R0-R4), Confidence (C0-C4), Quality (Q0-Q5), Complexity (X0-X4), Difficulty (D0-D6), CapabilityLevel (L0-L6), ExecutionMode, ExecutionStrategy, LifecycleStage, PipelineStage

### Pipeline
`src/compiler/core/pipeline.py`
- `CompilerPipeline(config)` — Pipeline orchestrator with 17 stages
- `pipeline.run()` — Returns PipelineResult

## Ontology

### EngineeringKnowledgeRecord
`src/compiler/ontology/ekr.py`
- `EKR.create(name, domain)` — Factory method
- `ekr.add_reasoning(op, content, confidence)` — Add reasoning step
- `ekr.add_decision(decision, context, alternatives, outcome)` — Add decision
- `ekr.to_dict()` — Serialize to dict

### KnowledgeGraph
`src/compiler/ontology/graph.py`
- `kg.add_node(id, type, **attrs)` — Add node
- `kg.add_relationship(source, target, type, **props)` — Add edge
- `kg.get_relationships(source, type)` — Query edges
- `kg.neighbors(id)` — Get connected nodes

## Cognition

### ReasoningGraph
`src/compiler/cognition/engine.py`
- `rg.add(operation, content, confidence)` — Add step
- `rg.to_dict()` — Serialize

## World

### WorldGenerator
`src/compiler/world/generator.py`
- `WorldGenerator(seed)` — Seeded generator
- `gen.generate_world(name, domain)` — Returns EngineeringWorld
- `gen.generate_company(domain)` — Returns Company with teams/repos
- `gen.generate_incident()` — Returns Incident

## Generation

### DatasetBuilder
`src/compiler/generation/dataset.py`
- `DatasetBuilder(config)` — Full pipeline orchestrator
- `builder.build(num_worlds, episodes_per_world, num_ekrs)` — Returns DatasetBuildResult
- `result.report()` — Formatted summary string

### EpisodeGenerator
`src/compiler/generation/engine.py`
- `gen.generate(context, episode_type, domain)` — Returns GenerationResult with EKR

## Serialization

### ToonParser
`src/compiler/serialization/toon_parser.py`
- `parser.parse(text)` — Parse TOON string → ParseResult
- `parser.parse_file(path)` — Parse .toon file → ParseResult

### SerializationEngine
`src/compiler/serialization/engine.py`
- `se.to_jsonl(records, filename)` → SerializationResult
- `se.to_toon(records, filename)` → SerializationResult
- `se.make_manifest(name, version, records)` → DatasetManifest

## Validation/Quality/Repair/Optimization

- `ValidationEngine.validate(ekr_dict)` → ValidationReport
- `QualityEngine.score(ekr_dict)` → QualityScore
- `RepairEngine.repair(ekr_dict)` → RepairResult
- `OptimizationEngine.optimize(records)` → OptimizationResult
