"""TOON Dataset Compiler — main entry point.

Usage: python main.py [config.json]
       PYTHONPATH=src python main.py
"""

import sys
from pathlib import Path

# Ensure src/ is on the path
_src = Path(__file__).parent / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from compiler.core.config import CompilerConfig
from compiler.core.pipeline import CompilerPipeline


def main() -> int:
    config_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    config = CompilerConfig.load(config_path) if config_path else CompilerConfig.default()
    pipeline = CompilerPipeline(config)
    result = pipeline.run()
    print(f"Compiler: {result.status}")
    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(main())
