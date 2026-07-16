# Getting Started

> **v0.2.0-dev**

## Prerequisites

- Python 3.10+
- pip install networkx

## Clone & Setup

```bash
git clone <repo>
cd Dataset
```

## Run Tests

```bash
$env:PYTHONPATH = "src"
pytest tests/ -q
# 70 passed
```

## Generate a Dataset

```bash
python -c "
from compiler.generation.dataset import DatasetBuilder
b = DatasetBuilder()
r = b.build(num_worlds=2, episodes_per_world=3, num_ekrs=5)
print(r.report())
"
```

## Parse Spec Files

```python
from compiler.serialization.toon_parser import ToonParser
p = ToonParser()
result = p.parse_file("compiler/00_core/07_global_constants.toon")
print(result.data)
```

## Project Layout

```
src/compiler/     # Implementation
compiler/         # .toon spec files (source of truth)
tests/            # 70 pytest tests
schemas/          # JSON schemas
main.py           # Entry point
docs/             # Documentation
```
