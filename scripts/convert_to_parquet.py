"""Convert native .toon dataset to Parquet for Hugging Face release."""
import json
import sys
from pathlib import Path

try:
    import pyarrow as pa
    import pyarrow.parquet as pq
except ImportError:
    print("pyarrow not installed. Run: pip install pyarrow")
    sys.exit(1)

SRC = Path("release/v0.4/dataset_1m.toon")
DST = Path("release/v0.4/dataset_1m.parquet")
BATCH = 10_000


def parse_value(v):
    v = v.strip()
    if v.startswith('"') and v.endswith('"'):
        return v[1:-1]
    if v.lower() in ("true", "yes"):
        return True
    if v.lower() in ("false", "no"):
        return False
    if v.lower() in ("null", "none", "~"):
        return None
    try:
        return int(v)
    except ValueError:
        pass
    try:
        return float(v)
    except ValueError:
        pass
    return v


def parse_block(text):
    lines = text.splitlines()
    root = {}
    stack = [(root, -1)]

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(line) - len(line.lstrip(" "))

        # Pop to correct parent (strictly greater indent means child)
        while len(stack) > 1 and stack[-1][1] > indent:
            stack.pop()

        parent = stack[-1][0]

        # List item (-) inside a list
        if stripped == "-" and isinstance(parent, list):
            item = {}
            parent.append(item)
            stack.append((item, indent + 2))
            continue

        # Simple list item (- value)
        if stripped.startswith("- ") and isinstance(parent, list):
            parent.append(parse_value(stripped[2:]))
            continue

        # key: value or just key:
        if ": " in stripped:
            idx = stripped.index(": ")
            key = stripped[:idx].strip()
            val = stripped[idx + 2:].strip()
            if val:
                parent[key] = parse_value(val)
            else:
                # Empty value — peek next line to determine list vs dict
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    next_indent = len(next_line) - len(next_line.lstrip(" "))
                    ns = next_line.strip()
                    if next_indent > indent and (ns == "-" or ns.startswith("- ")):
                        parent[key] = []
                        stack.append((parent[key], next_indent))
                    elif next_indent > indent:
                        parent[key] = {}
                        stack.append((parent[key], next_indent))
                    else:
                        parent[key] = {}
                else:
                    parent[key] = {}
        elif stripped.endswith(":"):
            key = stripped[:-1].strip()
            # Same empty value logic
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                next_indent = len(next_line) - len(next_line.lstrip(" "))
                ns = next_line.strip()
                if next_indent > indent and (ns == "-" or ns.startswith("- ")):
                    parent[key] = []
                    stack.append((parent[key], next_indent))
                elif next_indent > indent:
                    parent[key] = {}
                    stack.append((parent[key], next_indent))
                else:
                    parent[key] = {}
            else:
                parent[key] = {}

    return root


def stream_records(path):
    with open(path, "r", encoding="utf-8") as f:
        buf = []
        for line in f:
            if line.startswith("record_"):
                if buf:
                    yield _flatten(parse_block("".join(buf)))
                buf = []
            elif line.strip().startswith("#"):
                continue
            elif line.strip() != "":
                buf.append(line)
        if buf:
            yield _flatten(parse_block("".join(buf)))


def _flatten(r):
    d = {
        "id": r.get("id", ""),
        "name": r.get("name", ""),
        "type": r.get("type", ""),
        "domain": r.get("domain", ""),
        "difficulty": r.get("difficulty", 0),
        "quality_score": r.get("_quality", r.get("quality_score", 0)),
        "confidence": r.get("confidence", 0),
        "episode_type": r.get("_episode_type", ""),
        "throughput_step": r.get("_throughput_step", 0),
        "reasoning": json.dumps(r.get("reasoning", [])),
        "decisions": json.dumps(r.get("decisions", [])),
        "tradeoffs": json.dumps(r.get("tradeoffs", [])),
        "evidence": json.dumps(r.get("evidence", [])),
        "knowledge_atoms": json.dumps(r.get("knowledge_atoms", [])),
        "tags": json.dumps(r.get("tags", [])),
        "properties": json.dumps(r.get("properties", {})),
    }
    meta = r.get("metadata", {}) or {}
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
    lifecycle = r.get("lifecycle", {}) or {}
    if isinstance(lifecycle, dict):
        d["lifecycle_stage"] = lifecycle.get("stage", "")
    d["reasoning_count"] = len(r.get("reasoning", []) or [])
    d["decision_count"] = len(r.get("decisions", []) or [])
    d["evidence_count"] = len(r.get("evidence", []) or [])
    d["atom_count"] = len(r.get("knowledge_atoms", []) or [])
    return d


def main():
    print(f"Parsing {SRC}...")
    batches, batch, count = [], [], 0

    for flat in stream_records(SRC):
        batch.append(flat)
        count += 1
        if len(batch) >= BATCH:
            batches.append(pa.Table.from_pylist(batch))
            if count % 100000 == 0:
                print(f"  Parsed {count} records...")
            batch = []
    if batch:
        batches.append(pa.Table.from_pylist(batch))

    print(f"Total records: {count}")
    print(f"Merging {len(batches)} batches...")
    table = pa.concat_tables(batches)
    print(f"Writing {DST}...")
    pq.write_table(table, DST)
    size = DST.stat().st_size
    print(f"Done. {DST} — {size/1024/1024:.2f} MB")

    row = table.to_pydict()
    s = row["reasoning"][0]
    rc = row["reasoning_count"][0]
    print(f"\nValidation:")
    print(f"  Sample reasoning: {str(s)[:150]}...")
    print(f"  Sample reasoning_count: {rc}")
    non_empty_r = sum(1 for r in row["reasoning"] if r and r != "[]")
    non_empty_d = sum(1 for r in row["decisions"] if r and r != "[]")
    avg_quality = sum(row["quality_score"]) / count
    print(f"  Records with reasoning: {non_empty_r}/{count}")
    print(f"  Records with decisions: {non_empty_d}/{count}")
    print(f"  Avg quality_score: {avg_quality:.2f}")


if __name__ == "__main__":
    main()
