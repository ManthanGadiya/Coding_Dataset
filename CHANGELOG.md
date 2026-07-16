# Changelog

SemVer: MAJOR.MINOR.PATCH

---

# [0.3.1] — 2026-07-16

## Changed

### Quality Engine Overhaul
- **Content-aware scoring**: 10 dimensions rewritten to evaluate actual content substance, not just structural counts
- **Real discrimination**: True Q3/Q4 distribution (84% Q3, 16% Q4) based on episode type richness
- **Substance analysis**: Reasoning steps scored by domain terminology density, concrete details, and explanation quality
- **Engineering quality**: Rewards decisions with alternatives and detailed outcomes; base penalty for non-decision types removed
- **SourceAcquirer**: Three-tier acquisition (Firecrawl SDK → HTTP fallback → ingest file), fixes falsy `[]` bug in `acquire_all`

## Added

### Ingestion Tests (13 new tests, 83 total)
- KnowledgeStore: save/get, search, random sampling, empty domain handling
- AtomProcessor: atom creation, short-sentence skipping
- Prebuilt atoms: content validation, domain coverage (≥10 domains)
- SourceAcquirer: cache hit/miss, HTTP fallback, ingest file fallback, empty source list

# [0.3.0] — 2026-07-16

## Added

### Real-World Knowledge Ingestion (Phase 5)
- **KnowledgeAtoms**: 73 structured engineering knowledge atoms across 15 domains (Distributed_Systems, Software_Architecture, Production_Engineering, Databases, Networking, DevOps, Security, Performance, Testing, Cloud, Systems, AI_Engineering, Human_Factors, Foundations, Algorithms)
- **KnowledgeStore**: Persistent on-disk store with domain-indexed retrieval, random sampling, and search
- **SourceAcquirer**: Firecrawl-based web scraper for real engineering content (SRE book, design patterns catalog, incident postmortem guides, ADR standards, system design handbook)
- **AtomProcessor**: Extracts structured atoms from scraped markdown content using technical keyword matching

### Production Dataset
- 100,000 EKRs generated at Q4+ (97.2% Q4, 2.8% Q5)
- 199,644 knowledge atom references across 15 domains
- 7-step average reasoning chains, 1.3 decisions, 2.5 evidence items per EKR
- All 18 domains covered, all 12 episode types evenly distributed
- 0 errors, 0 duplicates, 100% validation pass

### Generation Engine Enhancements
- Knowledge atom enrichment: 40% of reasoning steps include real-world engineering references
- EpisodeGenerator wired to KnowledgeStore for domain-aware atom sampling
- DatasetBuilder accepts external KnowledgeStore for reproducible builds

## Changed
- README updated to v0.3.0: new ingestion module, production dataset status
- Atom reference probability increased from 30% to 40% for richer enrichment

## Documentation
- ROADMAP.md: v0.3 milestone marked complete
- ingestion/ module: __init__.py, atoms.py, source.py with full docstrings

# [0.2.0] — 2026-07-16

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
- EpisodeGenerator: template-based → spec-driven (12 episode types, domain concepts, incident scenarios)
- QualityEngine: flat scoring → 10-dimensional content-aware scoring
- DatasetBuilder: cycling episode types for even distribution

## Improved
- Avg quality from Q3 (3.0) to Q4+ (4.03) at 100K scale
- Reasoning chains: 7-step spec-driven (was 2-step template)
- Evidence: 2.5 items per EKR (was 1)
- Decisions: 1.25 per EKR (was 1)

## Removed
- `compile_constants` method from ToonCompiler (replaced by direct dict access)
- Redundant reasoning injection in DatasetBuilder

# [0.1.0] — Foundation

Initial project architecture. Repository structure, documentation, 151 .toon spec files, compiler architecture design.
