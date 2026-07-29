"""Export parquet to Hugging Face dataset format with dataset_info."""
import json, argparse
from pathlib import Path

HF_README_TEMPLATE = """---
dataset_info:
  description: "TOON Engineering Knowledge Records — 1M EKRs across 15 domains"
  size: {size}
  features:
    - name: id
      dtype: string
    - name: domain
      dtype: string
    - name: episode_type
      dtype: string
    - name: difficulty
      dtype: int32
    - name: quality_score
      dtype: int32
    - name: reasoning
      dtype: string
    - name: decisions
      dtype: string
    - name: evidence
      dtype: string
    - name: knowledge_atoms
      dtype: string
    - name: tradeoffs
      dtype: string
    - name: reasoning_count
      dtype: int32
    - name: decision_count
      dtype: int32
    - name: evidence_count
      dtype: int32
    - name: atom_count
      dtype: int32
  configs:
    - config_name: default
      data_files:
        - split: train
          path: dataset_1m.parquet
"""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--parquet", default="release/v0.4/dataset_1m.parquet")
    parser.add_argument("--output", default="release/v0.4/README.md")
    parser.add_argument("--manifest", default="release/v0.4/manifest.json")
    args = parser.parse_args()

    size = Path(args.parquet).stat().st_size
    readme = HF_README_TEMPLATE.format(size=size)
    Path(args.output).write_text(readme)
    print(f"Written {args.output} ({len(readme)} bytes)")

    if Path(args.manifest).exists():
        manifest = json.loads(Path(args.manifest).read_text())
        print(f"Manifest: {manifest.get('version', '?')}, "
              f"{manifest.get('total_ekrs', '?')} EKRs")

if __name__ == "__main__":
    main()
