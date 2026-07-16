"""Tests for core module."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from compiler.core.constants import (
    Priority, Severity, Risk, Confidence, Quality, Complexity, Difficulty,
    LifecycleStage, PipelineStage, MINIMUM_QUALITY, RELEASE_QUALITY,
)
from compiler.core.metadata import Metadata
from compiler.core.identifiers import make_id, parse_id
from compiler.core.versioning import Version, ComponentVersion
from compiler.core.lifecycle import LifecycleState, LifecycleStage as LS
from compiler.core.config import CompilerConfig, PassConfig
from compiler.core.pipeline import CompilerPipeline, PipelineResult


class TestConstants:
    def test_priority_values(self):
        assert Priority.P0.value == 0
        assert Priority.P4.value == 4

    def test_difficulty_range(self):
        assert Difficulty.D0.value == 0
        assert Difficulty.D6.value == 6

    def test_quality_range(self):
        assert Quality.Q0.value == 0
        assert Quality.Q5.value == 5

    def test_global_limits(self):
        assert MINIMUM_QUALITY == Quality.Q2
        assert RELEASE_QUALITY == Quality.Q4


class TestMetadata:
    def test_create(self):
        m = Metadata.create("test_type", "test_object", "DOM")
        assert m.object_type == "test_type"
        assert m.object_name == "test_object"
        assert m.domain == "DOM"
        assert m.id.startswith("TES-DOM-")

    def test_to_dict(self):
        m = Metadata.create("ekr", "my_ekr", "NET")
        d = m.to_dict()
        assert d["id"] == m.id
        assert d["object_type"] == "ekr"
        assert d["domain"] == "NET"


class TestIdentifiers:
    def test_make_id(self):
        uid = make_id("TEST", "DOM")
        parts = uid.split("-")
        assert len(parts) == 3
        assert parts[0] == "TEST"
        assert parts[1] == "DOM"

    def test_parse_id(self):
        uid = make_id("EKR", "GEN")
        p = parse_id(uid)
        assert p["prefix"] == "EKR"
        assert p["domain"] == "GEN"


class TestVersioning:
    def test_parse(self):
        v = Version.parse("1.2.3")
        assert v.major == 1
        assert v.minor == 2
        assert v.patch == 3

    def test_bump_major(self):
        v = Version(1, 2, 3).bump_major()
        assert str(v) == "2.0.0"

    def test_bump_minor(self):
        v = Version(1, 2, 3).bump_minor()
        assert str(v) == "1.3.0"

    def test_bump_patch(self):
        v = Version(1, 2, 3).bump_patch()
        assert str(v) == "1.2.4"


class TestLifecycle:
    def test_transition(self):
        ls = LifecycleState()
        assert ls.current_stage == LS.DISCOVERY
        ls.transition(LS.ACQUISITION)
        assert ls.current_stage == LS.ACQUISITION
        assert len(ls.history) == 1

    def test_terminal(self):
        ls = LifecycleState(LS.RELEASE)
        assert ls.is_terminal

    def test_fail(self):
        ls = LifecycleState()
        ls.fail("error")
        assert ls.has_error


class TestConfig:
    def test_default(self):
        cfg = CompilerConfig.default()
        assert cfg.name == "TOON Dataset Compiler"
        assert cfg.seed == 42
        assert cfg.fail_fast is True

    def test_passes_have_mandatory(self):
        cfg = CompilerConfig.default()
        assert cfg.passes["validation"].mandatory is True
        assert cfg.passes["serialization"].mandatory is True


class TestPipeline:
    def test_run_default(self):
        cfg = CompilerConfig.default()
        p = CompilerPipeline(cfg)
        r = p.run()
        assert r.success
        assert r.status == "passed"
        assert len(r.stages) > 0

    def test_pipeline_result(self):
        r = PipelineResult(status="passed", success=True, stages=[])
        assert r.success
        assert r.status == "passed"
