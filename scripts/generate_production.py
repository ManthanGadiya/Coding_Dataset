"""Production dataset generation — 100K+ knowledge-enriched EKRs at Q4+."""
import sys; sys.path.insert(0, "src")
import time
from pathlib import Path
from compiler.core.config import CompilerConfig
from compiler.core.constants import Quality
from compiler.generation.dataset import DatasetBuilder
from compiler.ingestion.atoms import KnowledgeStore, PREBUILT_ATOMS

def main():
    t0 = time.perf_counter()

    # Pre-populate knowledge store with real-world atoms
    store = KnowledgeStore(path=Path("ingestion/atoms"))
    store.save(PREBUILT_ATOMS)
    print(f"Knowledge store: {store.count()} atoms")

    # Production config: high quality threshold
    config = CompilerConfig.default()
    config.seed = 42
    config.minimum_quality = Quality.Q3

    builder = DatasetBuilder(config=config, knowledge_store=store)
    result = builder.build(
        num_worlds=2000,
        episodes_per_world=50,
    )

    elapsed = time.perf_counter() - t0
    print(f"\n=== Production Generation Complete ===")
    print(f"Duration: {elapsed:.0f}s ({elapsed/60:.1f}m)")
    print(f"Rate: {result.total_ekrs/elapsed:.0f} EKRs/s")
    print(result.report())

if __name__ == "__main__":
    main()
