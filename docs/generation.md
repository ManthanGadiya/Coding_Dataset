# Generation Module

Transforms worlds into Engineering Knowledge Records. 2 files in `src/compiler/generation/`.

## Episode Types

12 episode types:
- bug_fix
- feature_implementation
- code_review
- architecture_decision
- incident_response
- refactoring
- performance_optimization
- design_discussion
- debugging_session
- planning
- documentation
- technical_debt

## Dataset Builder

Orchestrates the full pipeline:

```
WorldGenerator → EpisodeGenerator → Validation → Repair
  → Quality → Optimization → Serialization
```

```python
from compiler.generation.dataset import DatasetBuilder

b = DatasetBuilder(seed=42)
result = b.build(
    num_worlds=2,
    episodes_per_world=3,
    num_ekrs=5,
)
print(result.report())
```

## Reasoning Templates

Each episode type has pre-defined reasoning templates:
- bug_fix: Observe → Identify → Hypothesize → Validate → Reflect
- incident_response: Observe → Diagnose → Identify → Implement → Document
- performance: Measure → Identify → Design → Implement → Benchmark
- architecture: Analyze → Research → Evaluate → Select → Document
