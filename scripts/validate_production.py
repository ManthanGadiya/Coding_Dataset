"""Validate production dataset quality and knowledge enrichment."""
import sys; sys.path.insert(0, "src")
import json
from collections import Counter

with open("build/pilot_dataset.jsonl") as f:
    lines = f.readlines()

total = len(lines)
ekrs = [json.loads(l) for l in lines]

# Atom references
atom_domains = set()
total_atom_refs = 0
for rec in ekrs:
    steps = rec.get("reasoning", [])
    for s in steps:
        if "[Ref:" in s.get("content", ""):
            total_atom_refs += 1
            atom_domains.add(rec.get("domain", "?"))

# Quality distribution
quality_dist = Counter()
for rec in ekrs:
    quality_dist[rec.get("_quality", 0)] += 1

# Domain coverage
domain_dist = Counter()
for rec in ekrs:
    domain_dist[rec.get("domain", "?")] += 1

# Episode type coverage (from name field)
type_dist = Counter()
for rec in ekrs:
    t = rec.get("name", "?").split("_")[0]
    type_dist[t] += 1

# Evidence and decisions
total_evidence = sum(len(rec.get("evidence", [])) for rec in ekrs)
total_decisions = sum(len(rec.get("decisions", [])) for rec in ekrs)
total_reasoning = sum(len(rec.get("reasoning", [])) for rec in ekrs)

print(f"=== Production Dataset Validation ===")
print(f"Total EKRs: {total}")
print(f"Atom refs: {total_atom_refs} across {len(atom_domains)} domains")
print(f"Avg reasoning steps: {total_reasoning/total:.1f}")
print(f"Avg decisions: {total_decisions/total:.1f}")
print(f"Avg evidence items: {total_evidence/total:.1f}")
print()
print(f"Quality distribution:")
for q in sorted(quality_dist):
    pct = quality_dist[q] / total * 100
    print(f"  Q{q}: {quality_dist[q]:>6} ({pct:>5.1f}%)")
print()
print(f"Top domains:\n  " + "\n  ".join(f"{d}: {c}" for d, c in domain_dist.most_common(5)))
print(f"\nTop episode types:\n  " + "\n  ".join(f"{t}: {c}" for t, c in type_dist.most_common(8)))
