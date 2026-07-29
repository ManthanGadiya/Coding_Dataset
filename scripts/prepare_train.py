"""Prepare EKR Parquet → formatted JSONL for LLM fine-tuning."""
import sys; sys.path.insert(0, "src")
import json, random
from pathlib import Path

def parse_field(v):
    if isinstance(v, str):
        try:
            return json.loads(v)
        except (json.JSONDecodeError, TypeError):
            return []
    return v if isinstance(v, list) else []

def format_ekr(ekr: dict) -> str:
    domain = ekr.get("domain", "GEN")
    ep_type = ekr.get("episode_type", ekr.get("_episode_type", "unknown"))
    reasoning = parse_field(ekr.get("reasoning", []))
    decisions = parse_field(ekr.get("decisions", []))

    steps = "\n".join(
        f"  [{s.get('operation', 'Step')}] {s.get('content', '')}"
        for s in reasoning
    )
    dec_text = ""
    if decisions:
        dec_text = "\nDecisions:\n" + "\n".join(
            f"  - {d.get('decision', d.get('outcome', ''))}"
            for d in decisions
        )
    return (
        f"<|domain|> {domain}\n"
        f"<|episode|> {ep_type}\n"
        f"<|reasoning|>\n{steps}"
        f"{dec_text}"
    )

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--parquet", default="release/v0.4/dataset_1m.parquet")
    parser.add_argument("--output", default="build/v0.4/data")
    parser.add_argument("--samples", type=int, default=100_000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    from datasets import load_dataset
    ds = load_dataset("parquet", data_files=args.parquet, split="train")
    print(f"Loaded {len(ds)} records from {args.parquet}")

    total = len(ds)
    rng = random.Random(args.seed)
    indices = list(range(total))
    rng.shuffle(indices)
    indices = indices[:args.samples]

    formatted = []
    for idx in indices:
        formatted.append({"text": format_ekr(ds[idx])})
    split = int(len(formatted) * 0.95)
    train, val = formatted[:split], formatted[split:]

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "train.jsonl", "w") as f:
        for r in train:
            f.write(json.dumps(r) + "\n")
    with open(out / "val.jsonl", "w") as f:
        for r in val:
            f.write(json.dumps(r) + "\n")
    print(f"Train: {len(train)}, Val: {len(val)}")
    print(f"Output: {out}")

if __name__ == "__main__":
    main()
