# Ontology Module

Defines the engineering knowledge universe. 6 files in `src/compiler/ontology/`.

## Domain Taxonomy

18 engineering domains with prerequisite dependencies:

```
Foundations → Programming → Algorithms → Data_Structures
           → Systems → Compilers, Networking, Databases
           → Distributed_Systems → Security, DevOps, Cloud
           → Production_Engineering
           → Software_Architecture, AI_Engineering
           → Testing, Performance
Human_Factors (standalone)
```

## Engineering Knowledge Record (EKR)

Canonical knowledge object. Every artifact becomes an EKR.

Fields: id, metadata, domain, difficulty (D0-D6), quality_score (Q0-Q5), confidence (C0-C4), reasoning chain, decisions, tradeoffs, evidence, knowledge_atoms, parent/child IDs.

## Knowledge Graph

NetworkX `MultiDiGraph` wrapper. Methods: add_node, add_relationship, get_relationships, neighbors. Used for graph-based validation and traversal.

## Key Files

| File | Purpose |
|------|---------|
| domain.py | DomainName enum, dependency graph |
| ekr.py | EngineeringKnowledgeRecord dataclass |
| entity.py | Base Entity class |
| graph.py | KnowledgeGraph (MultiDiGraph) |
| knowledge_atom.py | KnowledgeAtom model |
| dependencies.py | Dependency graph (DAG) |
