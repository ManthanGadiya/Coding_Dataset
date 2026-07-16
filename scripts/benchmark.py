"""Benchmark runner — measures quality, diversity, coverage, and throughput."""
import sys; sys.path.insert(0, "src")
import time
from pathlib import Path
from compiler.generation.dataset import DatasetBuilder
from compiler.ingestion.atoms import KnowledgeStore, PREBUILT_ATOMS
from compiler.benchmark.engine import BenchmarkSuite
from compiler.core.config import CompilerConfig
from compiler.core.constants import Quality

def main():
    t0 = time.perf_counter()

    store = KnowledgeStore(path=Path("ingestion/atoms"))
    store.save(PREBUILT_ATOMS)
    print(f"Knowledge store: {store.count()} atoms")

    suite = BenchmarkSuite(knowledge_store=store)

    quick = suite.run(num_ekrs=1000)
    print(quick.summary())

    print("\nRunning full validation...")
    config = CompilerConfig.default()
    config.minimum_quality = Quality.Q3
    builder = DatasetBuilder(config=config, knowledge_store=store)
    build_result = builder.build(num_worlds=5, episodes_per_world=10, num_ekrs=50)
    print(build_result.report())

    elapsed = time.perf_counter() - t0
    print(f"\nTotal benchmark time: {elapsed:.1f}s")

if __name__ == "__main__":
    main()
