"""Populate the knowledge store with real-world engineering atoms."""

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from compiler.ingestion.atoms import KnowledgeStore, PREBUILT_ATOMS


def main():
    store = KnowledgeStore(path=Path("ingestion/atoms"))
    store.save(PREBUILT_ATOMS)

    # Reload and verify
    store2 = KnowledgeStore(path=Path("ingestion/atoms"))
    print(f"Knowledge store populated: {store2.count()} atoms across domains:")
    from collections import Counter
    domains = Counter(a.domain for a in PREBUILT_ATOMS)
    for d, c in sorted(domains.items()):
        print(f"  {d}: {c} atoms")


if __name__ == "__main__":
    main()
