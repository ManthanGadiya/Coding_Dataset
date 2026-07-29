"""Production dataset generation — 1M+ knowledge-enriched EKRs with Q2-Q4 distribution."""
import sys; sys.path.insert(0, "src")
import time
import json
from pathlib import Path
from collections import Counter
from compiler.core.config import CompilerConfig
from compiler.core.constants import Quality
from compiler.benchmark.engine import BenchmarkSuite
from compiler.ingestion.atoms import KnowledgeStore, PREBUILT_ATOMS
from compiler.generation.engine import EpisodeGenerator, EpisodeType
from compiler.quality.engine import QualityEngine
import random

def main():
    t0 = time.perf_counter()
    target = 1_000_000

    store = KnowledgeStore(path=Path("ingestion/atoms"))
    store.save(PREBUILT_ATOMS)
    print(f"Knowledge store: {store.count()} atoms")
    print(f"Generating {target:,} EKRs...")

    gen = EpisodeGenerator(knowledge_store=store)
    quality = QualityEngine()
    rng = random.Random(42)
    types = list(EpisodeType)
    all_domains = [
        "Systems", "Databases", "Architecture", "Networking", "DevOps",
        "Security", "Performance", "Testing", "Cloud", "Distributed_Systems",
        "Software_Architecture", "AI_Engineering", "Production_Engineering",
        "Human_Factors", "Foundations", "Algorithms",
    ]

    quality_counter: Counter[int] = Counter()
    total_refs = 0
    all_records: list[dict] = []
    checkpoint_dir = Path("build/v0.4")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_interval = 100_000

    q5_ratio = 0.10  # 10% Q5

    gen_t0 = time.perf_counter()
    for i in range(target):
        d = rng.choice(all_domains)
        et = rng.choice(types)
        diff = rng.choice([1, 2, 3, 4, 5])
        is_q5 = rng.random() < q5_ratio
        quality_target = "q5" if is_q5 else None
        result = gen.generate({"domain": d, "difficulty": diff}, et, d, quality_target=quality_target)
        ekr = result.to_dict()["ekr"]
        score = quality.score(ekr)
        q = int(score.overall)
        quality_counter[q] += 1
        ekr["_quality"] = q
        ekr["_episode_type"] = et.value
        ekr["_throughput_step"] = i
        total_refs += sum(1 for s in ekr.get("reasoning", []) if "[Ref:" in s.get("content", ""))
        if q >= 2:  # Only keep Q2+
            all_records.append(ekr)

        if (i + 1) % checkpoint_interval == 0:
            elapsed = time.perf_counter() - gen_t0
            rate = (i + 1) / max(0.001, elapsed)
            ckpt_path = checkpoint_dir / f"checkpoint_{i+1}.jsonl"
            with open(ckpt_path, "w") as f:
                for rec in all_records[-checkpoint_interval:]:
                    f.write(json.dumps(rec) + "\n")
            q_dist = ", ".join(f"Q{q}:{quality_counter[q]}" for q in sorted(quality_counter))
            print(f"  {i+1:>7,}/{target:,} — {rate:>.0f} EKRs/s — {q_dist}")

    gen_elapsed = time.perf_counter() - gen_t0

    out_path = checkpoint_dir / "dataset_1m.jsonl"
    with open(out_path, "w") as f:
        for rec in all_records:
            f.write(json.dumps(rec) + "\n")

    total = time.perf_counter() - t0
    final_count = len(all_records)
    print(f"\n{'='*50}")
    print(f"  v0.4 Production Dataset Complete")
    print(f"{'='*50}")
    print(f"  Target:          {target:,} EKRs")
    print(f"  Output:          {final_count:,} EKRs (Q2+ filtered)")
    print(f"  Duration:        {gen_elapsed:.0f}s ({gen_elapsed/60:.1f}m)")
    print(f"  Throughput:      {target/gen_elapsed:>.0f} EKRs/s")
    print(f"  Output file:     {out_path}")
    print(f"  Knowledge atoms: {store.count()}")
    for q in sorted(quality_counter):
        pct = 100 * quality_counter[q] / target
        out_pct = 100 * sum(c for qq, c in quality_counter.items() if qq >= 2 and qq == q) / max(1, final_count)
        print(f"  Q{q}: {quality_counter[q]:>7,} ({pct:5.1f}%) — filtered: {out_pct:.1f}% of output")
    print(f"  Atom ref rate:   {total_refs/target:.1%}")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()
