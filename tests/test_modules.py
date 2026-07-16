"""Tests for cognition, curriculum, world, generation, repair, quality, validation, optimization, serialization."""

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
            "reasoning": [{"op": "a"}, {"op": "b"}, {"op": "c"}],
            "decisions": [{"d": "a"}],
            "knowledge_atoms": ["KA-1", "KA-2"],
            "metadata": {"domain": "GEN"},
        }
        score = engine.score(ekr_dict)
        assert int(score.overall) >= 2


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
