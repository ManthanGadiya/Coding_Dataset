"""Validate pilot dataset — quality, consistency, diversity, schema checks."""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path("src")))

from compiler.validation.engine import ValidationEngine
from compiler.quality.engine import QualityEngine


def load_records(path="build/pilot_dataset.jsonl"):
    with open(path) as f:
        return [json.loads(l) for l in f]


def report(records):
    ve = ValidationEngine()
    qe = QualityEngine()

    domains = {}
    ep_types = {}
    diffs = {}
    reasoning_lens = []
    quality_scores = []
    decisions_count = 0
    evidence_count = 0
    atoms_total = 0

    schema_pass = 0
    schema_fail = 0

    seen_ids = set()
    duplicates = 0

    for r in records:
        d = r.get("domain", "?")
        domains[d] = domains.get(d, 0) + 1

        name = r.get("name", "")
        ep_type = name.split("_")[0] if "_" in name else name
        ep_types[ep_type] = ep_types.get(ep_type, 0) + 1

        diff = r.get("difficulty", -1)
        diffs[diff] = diffs.get(diff, 0) + 1

        reasoning_lens.append(len(r.get("reasoning", [])))
        quality_scores.append(r.get("_quality", 0))
        decisions_count += len(r.get("decisions", []))
        evidence_count += len(r.get("evidence", []))
        atoms_total += len(r.get("knowledge_atoms", []))

        rid = r.get("id", "")
        if rid in seen_ids:
            duplicates += 1
        seen_ids.add(rid)

        # Schema validation
        if not r.get("metadata") or not r.get("id"):
            schema_fail += 1
        else:
            schema_pass += 1

    total = len(records)
    print(f"{'='*60}")
    print(f"  PILOT DATASET VALIDATION REPORT")
    print(f"{'='*60}")
    print(f"  Total records:    {total}")
    print(f"  Duplicates:       {duplicates}")
    print(f"  Schema pass:      {schema_pass}/{total}")
    print(f"  Schema fail:      {schema_fail}")
    print()

    print(f"  Domains ({len(domains)}):")
    for d, c in sorted(domains.items(), key=lambda x: -x[1]):
        print(f"    {d:30s} {c:3d} ({c/total*100:5.1f}%)")

    print()
    print(f"  Episode types ({len(ep_types)}):")
    for t, c in sorted(ep_types.items(), key=lambda x: -x[1]):
        print(f"    {t:30s} {c:3d} ({c/total*100:5.1f}%)")

    print()
    print(f"  Difficulty distribution:")
    for d in sorted(diffs):
        c = diffs[d]
        bar = "#" * (c * 40 // max(diffs.values()))
        print(f"    D{d}: {c:3d} {bar}")

    print()
    avg_rl = sum(reasoning_lens) / total
    avg_q = sum(quality_scores) / total
    print(f"  Avg reasoning steps: {avg_rl:.1f}")
    print(f"  Avg quality score:   {avg_q:.2f}")
    print(f"  Total decisions:     {decisions_count}")
    print(f"  Total evidence:      {evidence_count}")
    print(f"  Avg knowledge atoms: {atoms_total/total:.1f}")
    print()

    # Quality distribution
    q_dist = {}
    for q in quality_scores:
        q_dist[q] = q_dist.get(q, 0) + 1
    print(f"  Quality distribution:")
    for q in sorted(q_dist):
        c = q_dist[q]
        bar = "#" * (c * 40 // max(q_dist.values()))
        print(f"    Q{q}: {c:3d} {bar}")

    print()
    print(f"  Consistency check:")
    meta_domain_mismatch = 0
    for r in records:
        meta = r.get("metadata", {})
        if meta.get("domain") and r.get("domain") and meta["domain"] != r["domain"]:
            meta_domain_mismatch += 1
    print(f"    Domain mismatches:      {meta_domain_mismatch}")
    print(f"    Records with decisions: {sum(1 for r in records if r.get('decisions'))}/{total}")
    print(f"    Records with evidence:  {sum(1 for r in records if r.get('evidence'))}/{total}")
    print(f"    Records with atoms:     {sum(1 for r in records if r.get('knowledge_atoms'))}/{total}")
    print(f"    Records with reasoning: {sum(1 for r in records if r.get('reasoning'))}/{total}")
    print(f"{'='*60}")

    return {
        "total": total,
        "duplicates": duplicates,
        "domains": len(domains),
        "ep_types": len(ep_types),
        "avg_reasoning": avg_rl,
        "avg_quality": avg_q,
        "decisions": decisions_count,
        "evidence": evidence_count,
        "avg_atoms": atoms_total / total,
    }


if __name__ == "__main__":
    records = load_records()
    stats = report(records)
    # Save report
    report_path = Path("build/validation_report.json")
    report_path.write_text(json.dumps(stats, indent=2))
    print(f"\nReport saved to {report_path}")
