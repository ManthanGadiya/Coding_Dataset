"""Generate sample EKRs with specific parameters — useful for quick prototyping."""
import sys; sys.path.insert(0, "src")
import argparse, json
from compiler.generation.engine import EpisodeGenerator, EpisodeType
from compiler.quality.engine import QualityEngine

DOMAINS = [
    "Networking", "Cloud", "Databases", "Security", "Distributed_Systems",
    "Software_Architecture", "Performance", "DevOps", "Testing", "Systems",
    "AI_Engineering", "Production_Engineering",
]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=5)
    parser.add_argument("--domain", choices=DOMAINS + ["random"], default="random")
    parser.add_argument("--type", choices=[e.value for e in EpisodeType] + ["random"], default="random")
    parser.add_argument("--quality", choices=["q2", "q3", "q4", "q5", "random"], default="random")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    gen = EpisodeGenerator(seed=args.seed)
    quality = QualityEngine()
    types = list(EpisodeType)
    import random; rng = random.Random(args.seed)

    for i in range(args.count):
        d = args.domain if args.domain != "random" else rng.choice(DOMAINS)
        et_name = args.type if args.type != "random" else rng.choice(types).value
        et = next(t for t in types if t.value == et_name)
        qt = None
        if args.quality == "q5":
            qt = "q5"
        elif args.quality != "random":
            qt = args.quality

        result = gen.generate({"domain": d}, et, d, quality_target=qt)
        ekr = result.to_dict()["ekr"]
        score = quality.score(ekr)

        if args.json:
            print(json.dumps({"ekr": ekr, "score": score.to_dict(), "episode_type": et_name}, indent=2))
        else:
            print(f"\n--- EKR {i+1}: {et_name} / {d} / Q{int(score.overall)} ---")
            print(f"  Steps: {len(ekr.get('reasoning', []))}")
            print(f"  Decisions: {len(ekr.get('decisions', []))}")
            print(f"  Evidence: {len(ekr.get('evidence', []))}")
            print(f"  Tradeoffs: {len(ekr.get('tradeoffs', []))}")
            print(f"  Atoms: {len(ekr.get('knowledge_atoms', []))}")
            print(f"  Score: {score.to_dict()}")

if __name__ == "__main__":
    main()
