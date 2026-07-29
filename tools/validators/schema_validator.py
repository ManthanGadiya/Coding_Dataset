"""Validate EKR records against expected schema."""
import sys; sys.path.insert(0, "src")
import json, argparse
from pathlib import Path

REQUIRED_FIELDS = ["id", "name", "domain", "difficulty", "quality_score",
                   "episode_type", "reasoning", "decisions", "evidence"]

OPTIONAL_FIELDS = ["tradeoffs", "knowledge_atoms", "tags", "properties",
                   "metadata_id", "metadata_version", "lifecycle_stage"]

def validate_record(r: dict, idx: int) -> list[str]:
    errors = []
    for f in REQUIRED_FIELDS:
        if f not in r:
            errors.append(f"[{idx}] Missing required field: {f}")
    for f in ["difficulty", "quality_score"]:
        if f in r and not isinstance(r[f], (int, float)):
            errors.append(f"[{idx}] {f} should be numeric, got {type(r[f]).__name__}")
    return errors

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="JSONL or JSON file to validate")
    parser.add_argument("--max", type=int, default=1000, help="Max records to check")
    args = parser.parse_args()

    path = Path(args.input)
    if not path.exists():
        print(f"File not found: {args.input}")
        return

    text = path.read_text(encoding="utf-8")
    records = []
    if args.input.endswith(".jsonl"):
        records = [json.loads(line) for line in text.splitlines() if line.strip()]
    else:
        data = json.loads(text)
        records = data if isinstance(data, list) else [data]

    records = records[:args.max]
    all_errors = []
    for i, r in enumerate(records):
        all_errors.extend(validate_record(r, i))

    print(f"Validated {len(records)} records")
    if all_errors:
        print(f"Errors: {len(all_errors)}")
        for e in all_errors[:20]:
            print(f"  {e}")
        if len(all_errors) > 20:
            print(f"  ... and {len(all_errors) - 20} more")
    else:
        print("All records valid ✓")

if __name__ == "__main__":
    main()
