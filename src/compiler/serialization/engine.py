"""Serialization engine — TOON format, JSONL, Parquet export, manifests.

Source: compiler/10_serialization/
"""

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import pyarrow as pa
    import pyarrow.parquet as pq
    HAS_PARQUET = True
except ImportError:
    HAS_PARQUET = False


TOON_TYPES = [
    "string", "integer", "float", "boolean", "timestamp",
    "identifier", "reference", "enum", "list", "map", "structure", "any",
]


@dataclass
class SerializationResult:
    format: str
    path: Path
    record_count: int
    success: bool = True
    error: str | None = None

    def to_dict(self) -> dict:
        return {
            "format": self.format, "path": str(self.path),
            "record_count": self.record_count, "success": self.success,
        }


@dataclass
class DatasetManifest:
    name: str
    version: str
    record_count: int
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    compiler_version: str = "1.0.0"
    schema_version: str = "1.0.0"
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "name": self.name, "version": self.version,
            "record_count": self.record_count, "created_at": self.created_at,
            "compiler_version": self.compiler_version, "schema_version": self.schema_version,
            "metadata": self.metadata,
        }

    def save(self, path: Path):
        path.write_text(json.dumps(self.to_dict(), indent=2))


class SerializationEngine:
    def __init__(self, output_dir: Path = Path("build")):
        self.output_dir = output_dir

    def to_jsonl(self, records: list[dict], filename: str = "dataset.jsonl") -> SerializationResult:
        path = self.output_dir / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            for r in records:
                f.write(json.dumps(r) + "\n")
        return SerializationResult(format="jsonl", path=path, record_count=len(records))

    def to_toon(self, records: list[dict], filename: str = "dataset.toon") -> SerializationResult:
        path = self.output_dir / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        lines = ["# TOON Dataset", f"# Generated: {datetime.now(timezone.utc).isoformat()}", ""]
        for i, r in enumerate(records):
            lines.append(f"record_{i}:")
            for k, v in r.items():
                if isinstance(v, dict):
                    lines.append(f"  {k}:")
                    for sk, sv in v.items():
                        lines.append(f"    {sk}: {json.dumps(sv)}")
                elif isinstance(v, list):
                    lines.append(f"  {k}:")
                    for item in v:
                        if isinstance(item, dict):
                            lines.append(f"    -")
                            for sk, sv in item.items():
                                lines.append(f"      {sk}: {json.dumps(sv)}")
                        else:
                            lines.append(f"    - {json.dumps(item)}")
                else:
                    lines.append(f"  {k}: {json.dumps(v)}")
            lines.append("")
        path.write_text("\n".join(lines))
        return SerializationResult(format="toon", path=path, record_count=len(records))

    def _flatten_record(self, r: dict) -> dict:
        d = {
            "id": r.get("id", ""),
            "name": r.get("name", ""),
            "type": r.get("type", ""),
            "domain": r.get("domain", ""),
            "difficulty": r.get("difficulty", 0),
            "quality_score": r.get("quality_score", 0),
            "confidence": r.get("confidence", 0),
            "reasoning": json.dumps(r.get("reasoning", [])),
            "decisions": json.dumps(r.get("decisions", [])),
            "tradeoffs": json.dumps(r.get("tradeoffs", [])),
            "evidence": json.dumps(r.get("evidence", [])),
            "knowledge_atoms": json.dumps(r.get("knowledge_atoms", [])),
            "tags": json.dumps(r.get("tags", [])),
            "properties": json.dumps(r.get("properties", {})),
        }
        meta = r.get("metadata", {})
        if isinstance(meta, dict):
            d.update({
                "metadata_id": meta.get("id", ""),
                "metadata_object_type": meta.get("object_type", ""),
                "metadata_object_name": meta.get("object_name", ""),
                "metadata_version": meta.get("version", ""),
                "metadata_lifecycle_stage": meta.get("lifecycle_stage", ""),
                "metadata_created_at": meta.get("created_at", ""),
                "metadata_updated_at": meta.get("updated_at", ""),
            })
        lifecycle = r.get("lifecycle", {})
        if isinstance(lifecycle, dict):
            d["lifecycle_stage"] = lifecycle.get("stage", "")
        d["reasoning_count"] = len(r.get("reasoning", []))
        d["decision_count"] = len(r.get("decisions", []))
        d["evidence_count"] = len(r.get("evidence", []))
        d["atom_count"] = len(r.get("knowledge_atoms", []))
        return d

    def to_parquet(self, records: list[dict], filename: str = "dataset.parquet") -> SerializationResult:
        if not HAS_PARQUET:
            return SerializationResult(format="parquet", path=Path(filename), record_count=0, success=False, error="pyarrow not installed")
        path = self.output_dir / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        flat = [self._flatten_record(r) for r in records]
        table = pa.Table.from_pylist(flat)
        pq.write_table(table, path)
        return SerializationResult(format="parquet", path=path, record_count=len(records))

    def make_manifest(self, name: str, version: str, records: list[dict]) -> DatasetManifest:
        return DatasetManifest(name=name, version=version, record_count=len(records))
