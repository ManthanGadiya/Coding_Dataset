# Quality Module

> **v0.2.0-dev**

Multi-dimensional quality scoring. 1 file in `src/compiler/quality/`.

## Scoring Dimensions

10 dimensions, each scored 0-5:

| Dimension | Description |
|-----------|-------------|
| knowledge_density | Number of knowledge atoms |
| reasoning_depth | Length of reasoning chain |
| engineering_quality | Number of decisions |
| diversity | Variety of concepts |
| realism | How realistic the scenario is |
| novelty | How novel the approach is |
| educational_value | Teaching value |
| completeness | Has metadata + reasoning |
| consistency | Internal consistency |
| coherence | Logical flow |

## Overall Score

Average of all dimensions, mapped to Quality enum (Q0-Q5).

## Quality Gating

Records below `CompilerConfig.minimum_quality` (default Q2) are discarded.

```python
from compiler.quality.engine import QualityEngine

qe = QualityEngine()
score = qe.score(ekr_dict)
print(score.overall, score.dimensions)
```
