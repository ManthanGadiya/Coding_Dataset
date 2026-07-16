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

## v0.3 — Production Dataset (Done)

100K EKRs at Q4+ quality, 73 knowledge atoms from real-world sources via Firecrawl ingestion.

| Component | Status |
|-----------|--------|
| 100K EKR production dataset | Done |
| Real-world knowledge ingestion | Done |
| Knowledge-enriched generation (73 atoms, 15 domains) | Done |
| 70+ tests passing | Done |

## v0.4 — Scale & Release (Done)

- **1,000,000 EKR dataset** generated in JSONL + TOON formats
- **114 knowledge atoms** across 15 domains (was 73)
- **Benchmark suite**: quality distribution, domain coverage, throughput, atom diversity
- **Variable reasoning chain length**: true Q2-Q4 distribution (14.4% / 74.0% / 11.6%)
- **SourceAcquirer**: three-tier fallback (Firecrawl → HTTP → ingest file)

| Component | Status |
|-----------|--------|
| 1M EKR production dataset | Done |
| Benchmark suite | Done |
| Knowledge base expansion (114 atoms) | Done |
| Quality discrimination (Q2-Q4 distribution) | Done |
| Public dataset release | Done |
| Model training pipeline | Done (scaffold) |

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
| M7 | Pilot dataset released | Done |
| M8 | Public v1.0 release | Future |

---

# Future (v1.0+)

- Fine-tune models on TOON dataset
- Multi-language dataset (Python, Go, Rust, TypeScript)
- Interactive dataset browser/explorer
- Web UI for dataset curation
- Community contribution pipeline

---

## v0.3 — Production Dataset (Done)

v0.3.0: 100K EKRs at Q4+ quality, 73 knowledge atoms from real sources, Firecrawl ingestion pipeline.

| Component | Status |
|-----------|--------|
| 100K EKR production dataset | Done |
| Real-world knowledge ingestion (73 atoms) | Done |
| Knowledge-enriched generation | Done |
| 70+ tests passing | Done |
| v0.3.0 tagged | Done |

---

# Principles

- Build foundations before features
- Correctness over speed
- Quality over quantity
- Extensibility over shortcuts
- Every subsystem independently testable
- Every release reproducible
