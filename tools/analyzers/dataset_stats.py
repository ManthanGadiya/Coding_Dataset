"""Analyze dataset statistics from the production parquet file."""
import sys; sys.path.insert(0, "src")
import json, argparse
from pathlib import Path
from collections import Counter
from datasets import load_dataset

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--parquet", default="release/v0.4/dataset_1m.parquet")
    parser.add_argument("--max", type=int, default=100000, help="Max records to analyze")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    ds = load_dataset("parquet", data_files=args.parquet, split="train")
    if args.max and args.max < len(ds):
        ds = ds.select(range(args.max))
    print(f"Analyzing {len(ds)} records")

    quality = Counter()
    domains = Counter()
    types = Counter()
    difficulties = Counter()
    reasoning_lens = []
    decision_lens = []
    evidence_lens = []
    atom_lens = []

    for r in ds:
        quality[int(r["quality_score"])] += 1
        domains[r["domain"]] += 1
        types[r["episode_type"]] += 1
        difficulties[int(r["difficulty"])] += 1

        reasoning_lens.append(r["reasoning_count"])
        decision_lens.append(r["decision_count"])
        evidence_lens.append(r["evidence_count"])
        atom_lens.append(r["atom_count"])

    stats = {
        "total": len(ds),
        "quality_distribution": {str(k): v for k, v in sorted(quality.items())},
        "domain_coverage": dict(domains.most_common()),
        "episode_type_coverage": dict(types.most_common()),
        "difficulty_distribution": {str(k): v for k, v in sorted(difficulties.items())},
        "avg_reasoning_steps": sum(reasoning_lens) / len(reasoning_lens),
        "avg_decisions": sum(decision_lens) / len(decision_lens),
        "avg_evidence": sum(evidence_lens) / len(evidence_lens),
        "avg_atom_refs": sum(atom_lens) / len(atom_lens),
    }

    if args.json:
        print(json.dumps(stats, indent=2))
    else:
        print(f"\nQuality Distribution:")
        for q, c in sorted(quality.items()):
            print(f"  Q{q}: {c:>6} ({100*c/len(ds):.1f}%)")
        print(f"\nDifficulty Distribution:")
        for d, c in sorted(difficulties.items()):
            print(f"  D{d}: {c:>6} ({100*c/len(ds):.1f}%)")
        print(f"\nAvg reasoning steps: {stats['avg_reasoning_steps']:.1f}")
        print(f"Avg decisions:       {stats['avg_decisions']:.1f}")
        print(f"Avg evidence items:  {stats['avg_evidence']:.1f}")
        print(f"Avg atom refs:       {stats['avg_atom_refs']:.1f}")
        print(f"\nTop 5 domains:")
        for d, c in domains.most_common(5):
            print(f"  {d}: {c}")
        print(f"\nTop 5 episode types:")
        for t, c in types.most_common(5):
            print(f"  {t}: {c}")

if __name__ == "__main__":
    main()
