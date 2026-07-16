# Examples

## Generate a Complete Dataset

```python
from compiler.generation.dataset import DatasetBuilder

builder = DatasetBuilder(seed=42)
result = builder.build(num_worlds=3, episodes_per_world=4, num_ekrs=10)
print(result.report())
```

Expected output:
```
Dataset Build Report
  Worlds:      3
  Episodes:    12
  EKRs:        30
  Validated:   30
  Quality:     30
  Optimized:   30
  Serialized:  [pilot_dataset.jsonl, pilot_dataset.toon]
  Errors:      0
  Duration:    ~150ms
```

## Parse a Spec File

```python
from compiler.serialization.toon_parser import ToonParser
from pathlib import Path

p = ToonParser()
for spec in Path("compiler").rglob("*.toon"):
    result = p.parse_file(spec)
    assert result.success, f"Failed to parse {spec}"
```

## Create a World

```python
from compiler.world.generator import WorldGenerator

gen = WorldGenerator(seed=42)
world = gen.generate_world(domain="Distributed_Systems")
print(f"World: {world.name}")
print(f"Companies: {len(world.companies)}")
company = world.companies[0]
print(f"  {company.name}: {len(company.teams)} teams, {len(company.repositories)} repos")
```

## Score Quality

```python
from compiler.quality.engine import QualityEngine

qe = QualityEngine()
score = qe.score({"reasoning": [{"op": "Observe"}], "decisions": [], "knowledge_atoms": ["ka1"]})
print(f"Overall: {score.overall}")  # Q2
print(f"Dimensions: {score.dimensions}")
```
