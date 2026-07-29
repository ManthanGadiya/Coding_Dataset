"""ASCII bar chart of quality distribution from a benchmark report or parquet."""
import sys; sys.path.insert(0, "src")
import json, argparse
from pathlib import Path
from collections import Counter

def chart(data: dict[int, int], title: str = "Quality Distribution", width: int = 40):
    total = sum(data.values())
    print(f"\n{title}")
    print(f"{'─' * (width + 20)}")
    for q in sorted(data):
        count = data[q]
        pct = count / max(1, total)
        bar_len = max(1, int(pct * width))
        bar = "█" * bar_len
        print(f"  Q{q}: {bar:>{width}} {count:>6} ({100*pct:5.1f}%)")

def from_benchmark(path: str, width: int = 40):
    report = json.loads(Path(path).read_text())
    chart({int(k): v for k, v in report.get("quality_distribution", {}).items()},
          title=f"Quality — {Path(path).stem}", width=width)

def from_parquet(path: str, width: int = 40, max_records: int = 100000):
    from datasets import load_dataset
    ds = load_dataset("parquet", data_files=path, split="train")
    if max_records and max_records < len(ds):
        ds = ds.select(range(max_records))
    c = Counter()
    for r in ds:
        c[int(r["quality_score"])] += 1
    chart(dict(sorted(c.items())), title=f"Quality — {Path(path).stem}", width=width)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", help="Benchmark report JSON")
    parser.add_argument("--parquet", help="Parquet file")
    parser.add_argument("--width", type=int, default=40)
    parser.add_argument("--max", type=int, default=100000)
    args = parser.parse_args()

    if args.report:
        from_benchmark(args.report, args.width)
    elif args.parquet:
        from_parquet(args.parquet, args.width, args.max)
    else:
        # Show all benchmark reports
        reports_dir = Path("benchmarks/reports")
        if reports_dir.exists():
            for f in sorted(reports_dir.glob("*.json")):
                from_benchmark(str(f), args.width)

if __name__ == "__main__":
    main()
