# Cognition Module

Models engineering reasoning. 1 file in `src/compiler/cognition/`.

## Reasoning Primitives

20 atomic operations:

```
Observe, Identify, Classify, Compare, Relate,
Infer, Predict, Hypothesize, Validate, Measure,
Diagnose, Explain, Generalize, Specialize, Optimize,
Decide, Reflect, Transfer, Synthesize, Decompose
```

## Reasoning Graph

Chain of `ReasoningStep` objects, each with: operation, content, confidence (C0-C4), timestamp, dependencies.

## Decision Record

Structured decisions with: decision, context, alternatives, evidence, outcome, confidence.

## Hypothesis

Testable statements with: evidence_for, evidence_against, confidence, status (proposed/testing/confirmed/rejected).

## Usage

```python
from compiler.cognition.engine import ReasoningGraph, DecisionRecord

g = ReasoningGraph()
g.add("Observe", "Error rate increased 10x")
g.add("Hypothesize", "Cache layer failure")
g.add("Validate", "Confirmed cache eviction bug")
```
