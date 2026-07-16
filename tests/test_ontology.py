"""Tests for ontology module."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from compiler.ontology.entity import Entity
from compiler.ontology.knowledge_atom import KnowledgeAtom, AtomType
from compiler.ontology.ekr import EngineeringKnowledgeRecord
from compiler.ontology.domain import Domain, DomainName, DOMAIN_DEPS
from compiler.ontology.graph import KnowledgeGraph
from compiler.ontology.dependencies import DependencyGraph
from compiler.core.metadata import Metadata
from compiler.core.constants import LifecycleStage


class TestEntity:
    def test_create(self):
        m = Metadata.create("entity", "test")
        e = Entity(metadata=m)
        assert e.id == m.id
        assert e.name == "test"

    def test_transition(self):
        m = Metadata.create("entity", "test")
        e = Entity(metadata=m)
        e.transition(LifecycleStage.ACQUISITION)
        assert e.lifecycle.current_stage == LifecycleStage.ACQUISITION

    def test_to_dict(self):
        m = Metadata.create("entity", "test")
        e = Entity(metadata=m, tags=["tag1"])
        d = e.to_dict()
        assert d["id"] == m.id
        assert "tag1" in d["tags"]


class TestKnowledgeAtom:
    def test_create_concept(self):
        ka = KnowledgeAtom.create("Mutex", AtomType.CONCEPT, "Systems", "Mutual exclusion")
        assert ka.atom_type == AtomType.CONCEPT
        assert ka.name == "Mutex"
        assert ka.id.startswith("KA-")

    def test_atom_types(self):
        for t in AtomType:
            ka = KnowledgeAtom.create(f"Test_{t.value}", t)
            assert ka.atom_type == t


class TestEKR:
    def test_create(self):
        ekr = EngineeringKnowledgeRecord.create("test_ekr", "Databases")
        assert ekr.name == "test_ekr"
        assert ekr.domain == "Databases"
        assert ekr.id.startswith("EKR-")

    def test_add_reasoning(self):
        ekr = EngineeringKnowledgeRecord.create("r_test")
        ekr.add_reasoning("Observe", "watching")
        assert len(ekr.reasoning) == 1
        assert ekr.reasoning[0]["operation"] == "Observe"

    def test_add_decision(self):
        ekr = EngineeringKnowledgeRecord.create("d_test")
        ekr.add_decision("Use X", "need X", ["Y", "Z"], "picked X")
        assert len(ekr.decisions) == 1

    def test_to_dict(self):
        ekr = EngineeringKnowledgeRecord.create("dict_test")
        d = ekr.to_dict()
        assert d["id"] == ekr.id
        assert d["domain"] == "GEN"


class TestDomain:
    def test_domain_names(self):
        assert len(list(DomainName)) >= 18

    def test_domain_dependencies(self):
        deps = DOMAIN_DEPS[DomainName.PROGRAMMING]
        assert DomainName.FOUNDATIONS in deps

    def test_all_domains(self):
        domains = Domain.all()
        assert len(domains) == len(list(DomainName))


class TestKnowledgeGraph:
    def test_add_nodes(self):
        kg = KnowledgeGraph()
        kg.add_node("A", "ekr")
        kg.add_node("B", "ka")
        assert kg.node_count == 2

    def test_add_relationship(self):
        kg = KnowledgeGraph()
        kg.add_node("A")
        kg.add_node("B")
        kg.add_relationship("A", "B", "references")
        assert kg.edge_count == 1

    def test_neighbors(self):
        kg = KnowledgeGraph()
        kg.add_node("A")
        kg.add_node("B")
        kg.add_relationship("A", "B", "depends_on")
        assert "B" in kg.neighbors("A")


class TestDependencyGraph:
    def test_dag(self):
        dg = DependencyGraph()
        dg.add_dependency("B", "A")
        dg.add_dependency("C", "B")
        assert dg.is_acyclic()

    def test_cycle_detection(self):
        dg = DependencyGraph()
        dg.graph.add_edge("A", "B")
        dg.graph.add_edge("B", "C")
        dg.graph.add_edge("C", "A")
        assert not dg.is_acyclic()

    def test_topological_order(self):
        dg = DependencyGraph()
        dg.add_dependency("B", "A")
        dg.add_dependency("C", "B")
        order = dg.topological_order()
        assert order.index("A") < order.index("C")
