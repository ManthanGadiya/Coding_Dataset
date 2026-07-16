# Changelog

SemVer: MAJOR.MINOR.PATCH

---

# [0.2.0-dev] — 2026-07-16

## Added

### Compiler Implementation (11 modules, 36 files)
- **Core**: Config, constants (Priority, Severity, Risk, Confidence, Quality, Complexity, Difficulty, CapabilityLevel), pipeline (17 stages), lifecycle, identifiers, versioning, metadata
- **Ontology**: EngineeringKnowledgeRecord (EKR), KnowledgeGraph (NetworkX MultiDiGraph), 18 domains with dependencies, entities, knowledge atoms, dependency graph
- **Cognition**: 20 reasoning primitives, ReasoningGraph, DecisionRecord, Hypothesis
- **Curriculum**: CurriculumGraph, sample type weights, difficulty distribution (D0-D6)
- **World**: EngineeringWorld, Company, Team (15 types), Engineer (7 levels), Repository (5 scales), Incident, FeatureRequest — seeded deterministic generator
- **Generation**: 12 EpisodeTypes, EpisodeGenerator with reasoning injection, DatasetBuilder (full orchestration pipeline)
- **Repair**: 16 FailureCategories, RepairEngine with auto-classify and auto-repair
- **Quality**: 10-dimension QualityEngine, QualityScore
- **Validation**: 9-domain ValidationEngine, ValidationReport
- **Optimization**: DeduplicationEngine, OptimizationEngine (dedup + token truncation)
- **Serialization**: JSONL export, TOON format export, DatasetManifest, TOONParser (parses all 151 .toon specs)

### Testing
- 70 pytest tests across all modules (core, ontology, modules, integration, TOON parser)

### Documentation
- Filled all 10 docs/*.md stubs with real content
- Updated README, ARCHITECTURE, ROADMAP, CHANGELOG
- Added IMPLEMENTATION_NOTES.md, API.md

## Changed
- Architecture docs updated to reflect actual implementation
- Roadmap updated with current progress

## Removed
- `compile_constants` method from ToonCompiler (replaced by direct dict access)

# [0.1.0] — Foundation

Initial project architecture. Repository structure, documentation, 151 .toon spec files, compiler architecture design.
