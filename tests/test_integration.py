"""Integration tests for the full compiler pipeline."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from compiler.core.config import CompilerConfig
from compiler.core.pipeline import CompilerPipeline
from compiler.ontology.ekr import EngineeringKnowledgeRecord
from compiler.ontology.graph import KnowledgeGraph
from compiler.generation.engine import EpisodeGenerator, EpisodeType
from compiler.repair.engine import RepairEngine
from compiler.quality.engine import QualityEngine
from compiler.validation.engine import ValidationEngine
from compiler.optimization.engine import OptimizationEngine
from compiler.serialization.engine import SerializationEngine


def test_end_to_end_pipeline():
    cfg = CompilerConfig.default()
    pipe = CompilerPipeline(cfg)
    pr = pipe.run()
    assert pr.success
    assert pr.status == "passed"
    assert len(pr.stages) == 17


def test_generate_validate_quality_loop():
    gen = EpisodeGenerator()
    ve = ValidationEngine()
    qe = QualityEngine()

    for ep_type in list(EpisodeType)[:3]:
        result = gen.generate({"domain": "Systems"}, ep_type, "Systems")
        assert result.success
        ekr = result.ekr

        vr = ve.validate(ekr.to_dict())
        assert vr.all_passed

        qs = qe.score(ekr.to_dict())
        assert int(qs.overall) >= 2


def test_full_lifecycle():
    gen = EpisodeGenerator()
    re = RepairEngine()
    qe = QualityEngine()
    ve = ValidationEngine()
    oe = OptimizationEngine()
    se = SerializationEngine()

    result = gen.generate({"domain": "Databases"}, EpisodeType.PERFORMANCE_OPTIMIZATION, "Databases")
    ekr = result.ekr
    ekr.add_decision("Add index", "Slow queries", ["denormalize", "cache"], "added composite index")

    repaired = re.repair(ekr.to_dict())
    assert repaired.success

    score = qe.score(ekr.to_dict())
    assert int(score.overall) >= 2

    validated = ve.validate(ekr.to_dict())
    assert validated.all_passed

    opt = oe.optimize([ekr.to_dict(), ekr.to_dict()])
    assert opt.optimized_size == 1

    sr = se.to_jsonl([ekr.to_dict()])
    assert sr.record_count == 1


def test_knowledge_graph_integration():
    kg = KnowledgeGraph()
    ekr = EngineeringKnowledgeRecord.create("graph_test", "Networking")
    kg.add_node(ekr.id, "ekr")
    kg.add_node("KA-DNS-001", "knowledge_atom")
    kg.add_relationship(ekr.id, "KA-DNS-001", "references")
    assert kg.node_count == 2
    assert kg.edge_count == 1
    rels = kg.get_relationships(ekr.id)
    assert len(rels) == 1
    assert rels[0]["type"] == "references"
