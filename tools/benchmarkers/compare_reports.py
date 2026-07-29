"""Compare two benchmark reports side-by-side."""
import json, argparse
from pathlib import Path

def load(path):
    return json.loads(Path(path).read_text())

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("report_a", help="First benchmark report JSON")
    parser.add_argument("report_b", help="Second benchmark report JSON")
    args = parser.parse_args()

    a = load(args.report_a)
    b = load(args.report_b)

    print(f"{'Metric':35s} {'Report A':>15s} {'Report B':>15s} {'Δ':>10s}")
    print("-" * 75)

    keys = ["total_ekrs", "throughput_ekrs_per_sec", "avg_reasoning_steps",
            "avg_decisions", "avg_evidence", "avg_atom_refs", "unique_operations"]
    for k in keys:
        va = a.get(k, 0)
        vb = b.get(k, 0)
        diff = vb - va
        print(f"{k:35s} {va:>15.2f} {vb:>15.2f} {diff:>+10.2f}")

    print(f"\nQuality Distribution:")
    for q in sorted(set(list(a.get("quality_distribution", {}).keys()) +
                         list(b.get("quality_distribution", {}).keys()))):
        va = a.get("quality_distribution", {}).get(q, 0)
        vb = b.get("quality_distribution", {}).get(q, 0)
        diff = vb - va
        print(f"  Q{q:35s} {va:>15} {vb:>15} {diff:>+10}")

    print(f"\nAtom ref rate:")
    va = a.get("atom_ref_rate", 0)
    vb = b.get("atom_ref_rate", 0)
    print(f"{'':35s} {va:>15.3f} {vb:>15.3f} {vb-va:>+10.3f}")

if __name__ == "__main__":
    main()
