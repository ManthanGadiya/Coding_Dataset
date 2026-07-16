"""Tests for all modules: cognition, curriculum, world, generation, repair, quality, validation, optimization, serialization, ingestion."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from compiler.core.constants import Confidence, Quality, Difficulty
from compiler.ontology.ekr import EngineeringKnowledgeRecord


class TestCognition:
    def test_reasoning_graph(self):
        from compiler.cognition.engine import ReasoningGraph
        rg = ReasoningGraph()
        rg.add("Observe", "seeing", Confidence.C4)
        rg.add("Infer", "concluding", Confidence.C2)
        assert len(rg.steps) == 2

    def test_decision_record(self):
        from compiler.cognition.engine import DecisionRecord
        dr = DecisionRecord("use_redis", "need cache", ["memcached"], "low_latency", "deployed")
        assert dr.decision == "use_redis"
        d = dr.to_dict()
        assert d["outcome"] == "deployed"


class TestCurriculum:
    def test_curriculum_graph(self):
        from compiler.curriculum.engine import CurriculumGraph, CurriculumNode
        from compiler.core.constants import Difficulty
        cg = CurriculumGraph()
        n1 = CurriculumNode("n1", "Arrays", "Data_Structures", Difficulty.D1)
        n2 = CurriculumNode("n2", "Hash Tables", "Data_Structures", Difficulty.D2, prerequisites=["n1"])
        cg.add_node(n1)
        cg.add_node(n2)
        assert len(cg.nodes) == 2


class TestWorld:
    def test_engineer(self):
        from compiler.world.models import Engineer, EngineerLevel
        e = Engineer("Alice", EngineerLevel.SENIOR, "backend", ["Python", "Go"], 8)
        assert e.name == "Alice"
        assert e.level == EngineerLevel.SENIOR

    def test_company(self):
        from compiler.world.models import Company, Repository, RepoScale
        r = Repository("my-repo", "python", "A test repo", RepoScale.SMALL)
        c = Company("Acme", "technology", 500, [r])
        assert c.name == "Acme"
        assert c.size == 500
        assert len(c.repositories) == 1

    def test_engineering_world(self):
        from compiler.world.models import EngineeringWorld, Incident
        from compiler.core.constants import Severity
        w = EngineeringWorld("test-world")
        w.incidents.append(Incident("outage", Severity.S1, "detected", "DB overload"))
        assert w.name == "test-world"
        assert len(w.incidents) == 1


class TestGeneration:
    def test_generator(self):
        from compiler.generation.engine import EpisodeGenerator, EpisodeType
        gen = EpisodeGenerator()
        result = gen.generate({"domain": "Systems"}, EpisodeType.DEBUGGING_SESSION, "Systems")
        assert result.success
        assert result.ekr.domain == "Systems"
        assert result.duration_ms > 0


class TestRepair:
    def test_repair_empty(self):
        from compiler.repair.engine import RepairEngine
        engine = RepairEngine()
        ekr_dict = {"reasoning": [], "knowledge_atoms": [], "decisions": []}
        result = engine.repair(ekr_dict)
        assert result.success
        assert len(result.actions) > 0

    def test_repair_complete(self):
        from compiler.repair.engine import RepairEngine
        engine = RepairEngine()
        ekr_dict = {
            "reasoning": [{"operation": "Observe"}],
            "knowledge_atoms": ["KA-001"],
            "decisions": [{"decision": "use_x"}],
        }
        result = engine.repair(ekr_dict)
        assert result.success


class TestQuality:
    def test_scoring(self):
        from compiler.quality.engine import QualityEngine
        engine = QualityEngine()
        ekr_dict = {
            "reasoning": [
                {"operation": "Observe", "content": "Detected increased database query latency across the cluster"},
                {"operation": "Analyze", "content": "Examined slow query log and identified missing index on orders table"},
                {"operation": "Implement", "content": "Created composite index on (customer_id, order_date) to optimize range queries"},
            ],
            "decisions": [
                {"outcome": "chose B-tree index over hash index due to range query requirements", "alternatives": ["hash index", "full table scan"]},
            ],
            "knowledge_atoms": ["KA-001", "KA-042"],
            "evidence": [
                {"type": "metric", "content": "Query latency dropped from 2.5s to 40ms after index deployment"}
            ],
            "metadata": {"domain": "Databases"},
            "domain": "Databases",
            "difficulty": 3,
            "lifecycle": "proposed",
            "name": "Database query optimization",
        }
        score = engine.score(ekr_dict)
        assert int(score.overall) >= 3
        assert score.dimensions.get("coherence", 0) > 0
        assert score.dimensions.get("knowledge_density", 0) > 0


class TestValidation:
    def test_valid_record(self):
        from compiler.validation.engine import ValidationEngine
        engine = ValidationEngine()
        ekr_dict = {
            "id": "EKR-GEN-123",
            "domain": "GEN",
            "metadata": {"id": "EKR-GEN-123", "domain": "GEN"},
            "reasoning": [{"op": "a"}, {"op": "b"}],
        }
        report = engine.validate(ekr_dict)
        assert report.all_passed

    def test_invalid_record(self):
        from compiler.validation.engine import ValidationEngine
        engine = ValidationEngine()
        report = engine.validate({})
        assert not report.all_passed


class TestOptimization:
    def test_dedup(self):
        from compiler.optimization.engine import OptimizationEngine
        engine = OptimizationEngine()
        records = [
            {"id": "a", "data": "test", "reasoning": [{"i": 1}]},
            {"id": "a", "data": "test", "reasoning": [{"i": 1}]},
            {"id": "b", "data": "other", "reasoning": [{"i": 1}, {"i": 2}]},
        ]
        result = engine.optimize(records)
        assert result.optimized_size == 2
        assert result.details["removed_duplicates"] == 1


class TestSerialization:
    def test_jsonl(self, tmp_path):
        from compiler.serialization.engine import SerializationEngine
        engine = SerializationEngine(tmp_path)
        records = [{"id": "1", "name": "test"}, {"id": "2", "name": "test2"}]
        result = engine.to_jsonl(records, "test.jsonl")
        assert result.success
        assert result.record_count == 2
        assert result.path.exists()

    def test_toon(self, tmp_path):
        from compiler.serialization.engine import SerializationEngine
        engine = SerializationEngine(tmp_path)
        records = [{"id": "1", "name": "test", "meta": {"key": "val"}}]
        result = engine.to_toon(records, "test.toon")
        assert result.success
        assert result.path.exists()

    def test_manifest(self):
        from compiler.serialization.engine import SerializationEngine
        engine = SerializationEngine()
        manifest = engine.make_manifest("test", "1.0.0", [{"id": "1"}])
        assert manifest.name == "test"
        assert manifest.record_count == 1


class TestIngestion:
    def test_knowledge_store_init(self, tmp_path):
        from compiler.ingestion.atoms import KnowledgeStore
        store = KnowledgeStore(path=tmp_path)
        assert store.count() == 0

    def test_knowledge_store_save_and_get(self, tmp_path):
        from compiler.ingestion.atoms import KnowledgeStore, KnowledgeAtom
        store = KnowledgeStore(path=tmp_path)
        atoms = [
            KnowledgeAtom("Databases", "indexing", "B-tree indexes speed lookups.", "https://example.com", "article"),
            KnowledgeAtom("Databases", "sharding", "Horizontal sharding splits data.", "https://example.com", "article"),
            KnowledgeAtom("Networking", "DNS", "DNS resolves domain names.", "https://example.com", "article"),
        ]
        store.save(atoms)
        assert store.count() == 3
        db_atoms = store.get("Databases")
        assert len(db_atoms) == 2
        net_atoms = store.get("Networking")
        assert len(net_atoms) == 1
        found = store.get("Databases", concept="index")
        assert len(found) == 1

    def test_knowledge_store_search(self, tmp_path):
        from compiler.ingestion.atoms import KnowledgeStore, KnowledgeAtom
        store = KnowledgeStore(path=tmp_path)
        store.save([
            KnowledgeAtom("Databases", "indexing", "B-tree indexes are fast.", "https://ex.com", "article"),
            KnowledgeAtom("Databases", "caching", "Redis cache improves latency.", "https://ex.com", "article"),
        ])
        results = store.search("cache")
        assert len(results) == 1
        assert results[0].concept == "caching"

    def test_knowledge_store_get_random(self, tmp_path):
        import random
        from compiler.ingestion.atoms import KnowledgeStore, KnowledgeAtom
        store = KnowledgeStore(path=tmp_path)
        store.save([
            KnowledgeAtom("Databases", "a", "content a", "https://ex.com", "article"),
            KnowledgeAtom("Databases", "b", "content b", "https://ex.com", "article"),
            KnowledgeAtom("Databases", "c", "content c", "https://ex.com", "article"),
        ])
        rng = random.Random(42)
        chosen = store.get_random(rng, "Databases", n=2)
        assert len(chosen) == 2
        assert all(a.domain == "Databases" for a in chosen)

    def test_knowledge_store_get_random_empty_domain(self, tmp_path):
        import random
        from compiler.ingestion.atoms import KnowledgeStore
        store = KnowledgeStore(path=tmp_path)
        rng = random.Random(0)
        assert store.get_random(rng, "Nonexistent", n=3) == []

    def test_atom_processor_creates_atoms(self, tmp_path):
        from compiler.ingestion.atoms import AtomProcessor
        processor = AtomProcessor()
        content = (
            "Distributed systems use caching to reduce latency. "
            "Database sharding improves write throughput. "
            "Load balancing distributes traffic across servers. "
            "Microservices architecture enables independent deployment."
        )
        atoms = processor.process(content, "https://ex.com", "Distributed_Systems", "article",
                                   concepts=["caching", "sharding"])
        assert len(atoms) >= 2
        concepts_found = {a.concept for a in atoms}
        assert "caching" in concepts_found or "sharding" in concepts_found

    def test_atom_processor_skips_short_sentences(self, tmp_path):
        from compiler.ingestion.atoms import AtomProcessor
        processor = AtomProcessor()
        content = "Short."
        atoms = processor.process(content, "https://ex.com", "DevOps", "article", ["CI/CD"])
        assert len(atoms) == 0

    def test_prebuilt_atoms_have_content(self):
        from compiler.ingestion.atoms import PREBUILT_ATOMS
        assert len(PREBUILT_ATOMS) >= 70
        for atom in PREBUILT_ATOMS:
            assert len(atom.content) > 10
            assert atom.source_url
            assert atom.domain

    def test_prebuilt_atoms_domain_coverage(self):
        from compiler.ingestion.atoms import PREBUILT_ATOMS
        domains = set(a.domain for a in PREBUILT_ATOMS)
        assert len(domains) >= 10
        for required in ("Distributed_Systems", "Software_Architecture", "Production_Engineering",
                          "Databases", "Networking", "Performance"):
            assert required in domains, f"Missing domain: {required}"

    def test_source_acquirer_cache_hit(self, tmp_path):
        import json
        from compiler.ingestion.source import SourceAcquirer
        acquirer = SourceAcquirer(cache_dir=tmp_path / "cache")
        source_def = {"url": "https://example.com/test", "domain": "Databases", "type": "article", "concepts": ["sql"]}
        import hashlib
        cache_key = hashlib.md5(source_def["url"].encode()).hexdigest()
        cache_file = tmp_path / "cache" / f"{cache_key}.json"
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        cache_file.write_text(json.dumps({
            "url": "https://example.com/test", "title": "Test",
            "content": "Cached article about SQL databases",
            "domain": "Databases", "source_type": "article",
            "concepts": ["sql"],
        }))
        ks = acquirer.acquire(source_def)
        assert ks is not None
        assert "SQL" in ks.content

    def test_source_acquirer_fallback_http(self, tmp_path):
        from compiler.ingestion.source import SourceAcquirer
        acquirer = SourceAcquirer(cache_dir=tmp_path / "cache", ingest_dir=tmp_path / "ingest")
        source_def = {"url": "https://httpbin.org/html", "domain": "Networking", "type": "article", "concepts": ["HTTP"]}
        ks = acquirer.acquire(source_def)
        if ks is None:
            pytest.skip("httpbin.org not reachable")
        assert ks is not None
        assert ks.domain == "Networking"

    def test_source_acquirer_ingest_file_fallback(self, tmp_path):
        from compiler.ingestion.source import SourceAcquirer
        ingest_dir = tmp_path / "ingest"
        ingest_dir.mkdir()
        (ingest_dir / "example_com.txt").write_text("Fallback content about networks", encoding="utf-8")
        acquirer = SourceAcquirer(cache_dir=tmp_path / "cache", ingest_dir=ingest_dir)
        source_def = {"url": "https://example.com/networks", "domain": "Networking", "type": "article", "concepts": ["networks"]}
        ks = acquirer.acquire(source_def)
        assert ks is not None
        assert "Fallback" in ks.content

    def test_source_acquirer_acquire_all_empty(self, tmp_path):
        from compiler.ingestion.source import SourceAcquirer
        acquirer = SourceAcquirer(cache_dir=tmp_path / "cache")
        kss = acquirer.acquire_all([])
        assert kss == []
        kss = acquirer.acquire_all([{
            "url": "https://nonexistent.test/article",
            "domain": "Testing", "type": "article", "concepts": ["test"],
        }])
        assert len(kss) == 0
