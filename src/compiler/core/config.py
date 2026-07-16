"""Compiler configuration.

Source: compiler/00_core/10_compiler_config.toon
"""

from dataclasses import dataclass, field
from pathlib import Path

from .constants import ExecutionMode, ExecutionStrategy, Quality


@dataclass
class PassConfig:
    enabled: bool = True
    mandatory: bool = False


@dataclass
class CompilerConfig:
    name: str = "TOON Dataset Compiler"
    codename: str = "CAMera"
    version: str = "1.0.0"
    execution_mode: ExecutionMode = ExecutionMode.DEVELOPMENT
    execution_strategy: ExecutionStrategy = ExecutionStrategy.INCREMENTAL
    seed: int = 42
    passes: dict = field(default_factory=lambda: {
        "ingestion": PassConfig(), "parsing": PassConfig(), "ontology": PassConfig(),
        "cognition": PassConfig(), "curriculum": PassConfig(), "world": PassConfig(),
        "generation": PassConfig(), "repair": PassConfig(), "quality": PassConfig(),
        "validation": PassConfig(mandatory=True), "optimization": PassConfig(),
        "serialization": PassConfig(mandatory=True),
    })
    workspace: Path = Path("workspace")
    output: Path = Path("build")
    fail_fast: bool = True
    minimum_quality: Quality = Quality.Q2
    release_quality: Quality = Quality.Q4

    @classmethod
    def default(cls) -> "CompilerConfig":
        return cls()

    @classmethod
    def load(cls, path: Path) -> "CompilerConfig":
        import json
        with open(path) as f:
            data = json.load(f)
        cfg = cls.default()
        for k, v in data.items():
            if hasattr(cfg, k):
                setattr(cfg, k, v)
        return cfg
