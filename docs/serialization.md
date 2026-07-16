# Serialization Module

> **v0.2.0-dev**

Converts internal EKRs to output formats. 2 files in `src/compiler/serialization/`.

## TOON Parser

Parses `.toon` spec files into Python dicts. Indentation-based syntax:

```toon
key: value
nested:
  subkey: "string value"
  list_key:
    - item1
    - item2
```

```python
from compiler.serialization.toon_parser import ToonParser

p = ToonParser()
result = p.parse_file("compiler/00_core/07_global_constants.toon")
print(result.data["P0"])  # "Critical"
```

## JSONL Export

One JSON object per line. Standard ML training format.

## TOON Export

Human-readable indented format. Preserves structure for debugging.

## Dataset Manifest

JSON metadata file: name, version, record_count, created_at, compiler_version, schema_version.

## Usage

```python
from compiler.serialization.engine import SerializationEngine

se = SerializationEngine(output_dir=Path("build"))
jl = se.to_jsonl(records, "dataset.jsonl")
tn = se.to_toon(records, "dataset.toon")
manifest = se.make_manifest("pilot", "0.1.0", records)
manifest.save(Path("build/manifest.json"))
```
