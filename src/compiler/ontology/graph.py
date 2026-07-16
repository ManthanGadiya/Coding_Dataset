"""Knowledge Graph — directed property graph of engineering knowledge.

Source: compiler/01_ontology/08_relationships.toon
"""

from dataclasses import dataclass, field

import networkx as nx


@dataclass
class KnowledgeGraph:
    graph: nx.MultiDiGraph = field(default_factory=nx.MultiDiGraph)

    def add_node(self, node_id: str, node_type: str = "entity", **attrs):
        attrs.setdefault("node_type", node_type)
        self.graph.add_node(node_id, **attrs)

    def add_relationship(self, source: str, target: str, rel_type: str, **props):
        self.graph.add_edge(source, target, key=rel_type, type=rel_type, **props)

    def get_relationships(self, source: str, rel_type: str | None = None) -> list[dict]:
        return [
            {"source": u, "target": v, "type": k, **d}
            for u, v, k, d in self.graph.edges(source, data=True, keys=True)
            if rel_type is None or k == rel_type
        ]

    def neighbors(self, node_id: str) -> list[str]:
        return list(set(self.graph.predecessors(node_id)) | set(self.graph.successors(node_id)))

    @property
    def node_count(self) -> int:
        return self.graph.number_of_nodes()

    @property
    def edge_count(self) -> int:
        return self.graph.number_of_edges()

    def to_dict(self) -> dict:
        nodes = [{"id": n, **d} for n, d in self.graph.nodes(data=True)]
        edges = [{"source": u, "target": v, "type": k, **d}
                 for u, v, k, d in self.graph.edges(data=True, keys=True)]
        return {"nodes": nodes, "edges": edges}
