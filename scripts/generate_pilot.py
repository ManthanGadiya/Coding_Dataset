"""Generate the v0.2 pilot dataset — 100+ spec-driven EKRs."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path("src")))

from compiler.generation.dataset import DatasetBuilder
from compiler.core.config import CompilerConfig
from compiler.core.constants import Quality

config = CompilerConfig.default()
config.seed = 42
config.minimum_quality = Quality.Q2

builder = DatasetBuilder(config)
result = builder.build(
    num_worlds=10,
    episodes_per_world=4,
    num_ekrs=15,
)

print(result.report())
print(f"\nOutput files generated in: {builder.serialization.output_dir}")
