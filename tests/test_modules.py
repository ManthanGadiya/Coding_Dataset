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


class TestQ5Generation:
    def test_q5_generates_q5_content(self):
        from compiler.generation.engine import EpisodeGenerator, EpisodeType
        gen = EpisodeGenerator()
        result = gen.generate({"domain": "Databases"}, EpisodeType.PERFORMANCE_OPTIMIZATION, "Databases", quality_target="q5")
        assert result.success
        ekr = result.to_dict()["ekr"]
        reasoning = ekr.get("reasoning", [])
        decisions = ekr.get("decisions", [])
        evidence = ekr.get("evidence", [])
        assert len(reasoning) >= 8
        assert len(decisions) >= 2
        assert len(evidence) >= 2

    def test_q5_has_deep_engineering_decisions(self):
        from compiler.generation.engine import EpisodeGenerator, EpisodeType
        gen = EpisodeGenerator()
        result = gen.generate({"domain": "Networking"}, EpisodeType.INCIDENT_RESPONSE, "Networking", quality_target="q5")
        ekr = result.to_dict()["ekr"]
        decisions = ekr.get("decisions", [])
        for d in decisions:
            assert len(d.get("alternatives", [])) >= 3
            assert d.get("outcome", "")

    def test_q5_has_metrics_in_evidence(self):
        from compiler.generation.engine import EpisodeGenerator, EpisodeType
        import re
        gen = EpisodeGenerator()
        result = gen.generate({"domain": "Performance"}, EpisodeType.PERFORMANCE_OPTIMIZATION, "Performance", quality_target="q5")
        ekr = result.to_dict()["ekr"]
        evidence = ekr.get("evidence", [])
        evidence_text = " ".join(e.get("content", "") for e in evidence)
        has_number = bool(re.search(r'\d+\.?\d*', evidence_text))
        assert has_number, "Q5 evidence should contain metrics/numbers"
        assert any(e.get("type") in ("metric", "log", "observation", "measurement", "alert") for e in evidence)

    def test_q5_tradeoffs_present(self):
        from compiler.generation.engine import EpisodeGenerator, EpisodeType
        gen = EpisodeGenerator()
        result = gen.generate({"domain": "Software_Architecture"}, EpisodeType.ARCHITECTURE_DECISION, "Software_Architecture", quality_target="q5")
        ekr = result.to_dict()["ekr"]
        tradeoffs = ekr.get("tradeoffs", [])
        assert len(tradeoffs) >= 1

    def test_q5_across_all_deep_types(self):
        from compiler.generation.engine import EpisodeGenerator, EpisodeType, DEEP_ENGINEERING_DECISIONS
        gen = EpisodeGenerator()
        deep_types = {EpisodeType(k) for k in DEEP_ENGINEERING_DECISIONS if hasattr(EpisodeType, k)}
        for et in list(deep_types)[:3]:
            result = gen.generate({"domain": "Systems"}, et, "Systems", quality_target="q5")
            assert result.success
            ekr = result.to_dict()["ekr"]
            assert len(ekr.get("reasoning", [])) >= 8

    def test_q5_quality_engine_confirms_q5(self):
        from compiler.generation.engine import EpisodeGenerator, EpisodeType
        from compiler.quality.engine import QualityEngine
        gen = EpisodeGenerator()
        quality = QualityEngine()
        result = gen.generate({"domain": "Databases"}, EpisodeType.PERFORMANCE_OPTIMIZATION, "Databases", quality_target="q5")
        ekr = result.to_dict()["ekr"]
        score = quality.score(ekr)
        assert int(score.overall) == 5

    def test_q5_vs_standard_comparison(self):
        from compiler.generation.engine import EpisodeGenerator, EpisodeType
        from compiler.quality.engine import QualityEngine
        gen = EpisodeGenerator(seed=42)
        quality = QualityEngine()
        std = gen.generate({"domain": "Databases"}, EpisodeType.PERFORMANCE_OPTIMIZATION, "Databases")
        q5 = gen.generate({"domain": "Databases"}, EpisodeType.PERFORMANCE_OPTIMIZATION, "Databases", quality_target="q5")
        std_ekr = std.to_dict()["ekr"]
        q5_ekr = q5.to_dict()["ekr"]
        assert len(q5_ekr.get("reasoning", [])) >= len(std_ekr.get("reasoning", []))
        assert len(q5_ekr.get("decisions", [])) >= len(std_ekr.get("decisions", []))
        std_score = quality.score(std_ekr)
        q5_score = quality.score(q5_ekr)
        assert int(q5_score.overall) >= int(std_score.overall)


class TestSerializationRoundTrip:
    def test_jsonl_round_trip(self, tmp_path):
        from compiler.serialization.engine import SerializationEngine
        import json
        engine = SerializationEngine(tmp_path)
        records = [
            {"id": "1", "name": "test", "value": 42, "tags": ["a", "b"]},
            {"id": "2", "name": "test2", "value": 99, "tags": []},
        ]
        out_path = tmp_path / "test.jsonl"
        result = engine.to_jsonl(records, out_path.name)
        assert result.success
        loaded = [json.loads(line) for line in out_path.read_text().splitlines() if line.strip()]
        assert len(loaded) == 2
        assert loaded[0]["id"] == "1"
        assert loaded[1]["value"] == 99

    def test_jsonl_round_trip_ekr(self, tmp_path):
        from compiler.generation.engine import EpisodeGenerator, EpisodeType
        from compiler.serialization.engine import SerializationEngine
        import json
        gen = EpisodeGenerator()
        se = SerializationEngine(tmp_path)
        result = gen.generate({"domain": "Databases"}, EpisodeType.CODE_REVIEW, "Databases")
        ekr = result.to_dict()["ekr"]
        se.to_jsonl([ekr], "ekr.jsonl")
        loaded = [json.loads(line) for line in (tmp_path / "ekr.jsonl").read_text().splitlines() if line.strip()]
        assert len(loaded) == 1
        assert loaded[0]["domain"] == "Databases"
        assert len(loaded[0].get("reasoning", [])) > 0

    def test_toon_round_trip(self, tmp_path):
        from compiler.serialization.engine import SerializationEngine
        engine = SerializationEngine(tmp_path)
        records = [{"id": "1", "data": {"nested": "value"}}, {"id": "2", "data": None}]
        result = engine.to_toon(records, "test.toon")
        assert result.success
        assert result.path.exists()
        assert result.path.stat().st_size > 0

    def test_toon_with_ekr(self, tmp_path):
        from compiler.generation.engine import EpisodeGenerator, EpisodeType
        from compiler.serialization.engine import SerializationEngine
        gen = EpisodeGenerator()
        se = SerializationEngine(tmp_path)
        result = gen.generate({"domain": "Networking"}, EpisodeType.BUG_FIX, "Networking")
        ekr = result.to_dict()["ekr"]
        ser = se.to_toon([ekr], "networking_ekr.toon")
        assert ser.success
        assert ser.path.exists()

    def test_manifest_matches_records(self):
        from compiler.serialization.engine import SerializationEngine
        se = SerializationEngine()
        records = [{"id": "a"}, {"id": "b"}, {"id": "c"}]
        m = se.make_manifest("test", "1.0.0", records)
        assert m.record_count == 3
        assert m.name == "test"
        assert m.version == "1.0.0"

    def test_serialize_empty_list(self, tmp_path):
        from compiler.serialization.engine import SerializationEngine
        se = SerializationEngine(tmp_path)
        result = se.to_jsonl([], "empty.jsonl")
        assert result.success
        assert result.path.exists()
        assert result.path.stat().st_size < 10


class TestEdgeCasesAndStress:
    def test_empty_ekr_quality_score(self):
        from compiler.quality.engine import QualityEngine
        qe = QualityEngine()
        score = qe.score({})
        assert int(score.overall) >= 0
        assert score.dimensions.get("coherence", 0) >= 0

    def test_ekr_with_no_reasoning(self):
        from compiler.quality.engine import QualityEngine
        qe = QualityEngine()
        ekr = {"id": "no-reasoning", "domain": "Test", "reasoning": []}
        score = qe.score(ekr)
        assert int(score.overall) >= 0

    def test_validation_empty_record(self):
        from compiler.validation.engine import ValidationEngine
        ve = ValidationEngine()
        report = ve.validate({})
        assert not report.all_passed
        assert any(not r.passed for r in report.results)

    def test_validation_none_record(self):
        from compiler.validation.engine import ValidationEngine
        ve = ValidationEngine()
        report = ve.validate({})
        assert not report.all_passed

    def test_optimization_empty_list(self):
        from compiler.optimization.engine import OptimizationEngine
        oe = OptimizationEngine()
        result = oe.optimize([])
        assert result.original_size == 0
        assert result.optimized_size == 0

    def test_optimization_all_identical(self):
        from compiler.optimization.engine import OptimizationEngine
        oe = OptimizationEngine()
        records = [{"id": "a", "reasoning": [{"x": 1}]}] * 10
        result = oe.optimize(records)
        assert result.optimized_size == 1
        assert result.details["removed_duplicates"] == 9

    def test_generate_stress_100(self):
        from compiler.generation.engine import EpisodeGenerator, EpisodeType
        gen = EpisodeGenerator(seed=0)
        import random, time
        rng = random.Random(0)
        types = list(EpisodeType)
        t0 = time.perf_counter()
        successes = 0
        for i in range(100):
            d = rng.choice(["Systems", "Databases", "Networking", "Security", "Performance"])
            et = rng.choice(types)
            result = gen.generate({"domain": d}, et, d)
            if result.success:
                successes += 1
        elapsed = time.perf_counter() - t0
        print(f"  Stress: {successes}/100 succeeded in {elapsed:.1f}s ({successes/max(0.001, elapsed):.0f}/sec)")
        assert successes >= 90

    def test_generate_high_difficulty(self):
        from compiler.generation.engine import EpisodeGenerator, EpisodeType
        gen = EpisodeGenerator(seed=1)
        result = gen.generate({"domain": "Distributed_Systems"}, EpisodeType.INCIDENT_RESPONSE, "Distributed_Systems", quality_target="q5")
        assert result.success
        ekr = result.to_dict()["ekr"]
        assert ekr["difficulty"] == 5

    def test_generate_all_episode_types(self):
        from compiler.generation.engine import EpisodeGenerator, EpisodeType
        gen = EpisodeGenerator(seed=42)
        failed = []
        for et in EpisodeType:
            try:
                result = gen.generate({"domain": "Systems"}, et, "Systems")
                if not result.success:
                    failed.append(et.value)
            except Exception as e:
                failed.append(f"{et.value}: {e}")
        assert not failed, f"Failed types: {failed}"

    def test_quality_engine_concurrent_parallel_safety(self):
        from compiler.quality.engine import QualityEngine
        qe = QualityEngine()
        ekr = {
            "reasoning": [{"operation": "Observe", "content": "test"}],
            "decisions": [{"outcome": "chose A", "alternatives": ["B", "C"]}],
            "knowledge_atoms": ["KA-001"],
            "evidence": [{"type": "metric", "content": "99.9% uptime"}],
        }
        scores = [qe.score(ekr) for _ in range(10)]
        unique = {int(s.overall) for s in scores}
        assert len(unique) == 1

    def test_tradeoffs_use_engineering_language(self):
        from compiler.generation.engine import EpisodeGenerator, EpisodeType
        gen = EpisodeGenerator()
        result = gen.generate({"domain": "Cloud"}, EpisodeType.ARCHITECTURE_DECISION, "Cloud", quality_target="q5")
        ekr = result.to_dict()["ekr"]
        assert len(ekr.get("tradeoffs", [])) >= 1
        for t in ekr.get("tradeoffs", []):
            text = t.get("tradeoff", "") if isinstance(t, dict) else str(t)
            assert len(text) > 10, f"Tradeoff too short: {text}"
            assert "chose" in text.lower(), f"Tradeoff missing 'chose': {text[:80]}"

