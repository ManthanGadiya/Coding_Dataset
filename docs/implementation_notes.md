# Implementation Notes

## Architecture Decisions

### ADR-001: Relative Imports Within `src/compiler/`
All internal imports use relative paths (e.g., `from ..core.config import CompilerConfig`). This keeps the package self-contained.

### ADR-002: Seeded Deterministic Generation
WorldGenerator uses a linear congruential generator (LCG) with seed 42. Same seed → same output every time. No randomness from external sources.

### ADR-003: TOON Spec Files as Source of Truth
`.toon` spec files in `compiler/` define all types, constants, and domain knowledge. Never modify specs. Implementation reads them via ToonParser.

### ADR-004: DatasetBuilder Orchestrates Full Pipeline
Rather than exposing individual stages, `DatasetBuilder.build()` runs the complete pipeline: generate → validate → repair → score → optimize → serialize.

### ADR-005: NetworkX MultiDiGraph for Knowledge Graphs
MultiDiGraph allows multiple edges between same nodes with different relationship types. Used for all graph operations.

## Known Limitations

1. Generation engine creates basic EKRs with template reasoning (not full spec-driven)
2. No Parquet or Avro serialization yet
3. No distributed generation
4. Pilot dataset not yet generated
5. Some spec fields are parsed but not used by generators

## Testing Strategy

- 70 tests across 5 test files
- Tests run in ~0.3s
- Tests cover: core constants, config, pipeline, identifiers, ontology models, knowledge graph, EKR, domain taxonomy, cognition, curriculum, world models, generation, repair, quality, validation, optimization, serialization, TOON parser, integration
- All tests use deterministic data (no random seeding)
