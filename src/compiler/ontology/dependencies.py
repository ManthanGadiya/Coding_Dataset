"""Dependency graph — DAG of engineering entity dependencies.

Source: compiler/01_ontology/19_dependency_graph.toon
"""

from dataclasses import dataclass, field

import networkx as nx


@dataclass
class DependencyGraph:
    graph: nx.DiGraph = field(default_factory=nx.DiGraph)

    def add_dependency(self, dependent: str, dependency: str, weight: float = 1.0, metadata: dict | None = None):
        self.graph.add_edge(dependency, dependent, weight=weight, metadata=metadata or {})

    def dependencies_of(self, node: str) -> list[str]:
        return list(self.graph.predecessors(node))

    def dependents_of(self, node: str) -> list[str]:
        return list(self.graph.successors(node))

    def is_acyclic(self) -> bool:
        return nx.is_directed_acyclic_graph(self.graph)

    def topological_order(self) -> list[str]:
        if not self.is_acyclic():
            raise ValueError("DAG contains cycles")
        return list(nx.topological_sort(self.graph))

    def to_dict(self) -> dict:
        return {
            "nodes": list(self.graph.nodes()),
            "edges": [{"from": u, "to": v, "weight": d.get("weight", 1.0)}
                      for u, v, d in self.graph.edges(data=True)],
            "acyclic": self.is_acyclic(),
        }
