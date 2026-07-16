"""Tests for TOON parser."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from compiler.serialization.toon_parser import ToonParser, ToonCompiler


SAMPLE_TOON = """
# Test spec
spec:
  id: test_spec
  version: 1.0.0
  status: stable

priority:
  P0: Critical
  P1: High
  P2: Medium

difficulty:
  D0: 0
  D1: 1
  D2: 2

examples:
  - item1
  - item2
  - item3

nested:
  key1: val1
  key2:
    subkey: subval
"""


class TestToonParser:
    def test_parse_basic(self):
        parser = ToonParser()
        result = parser.parse(SAMPLE_TOON)
        assert result.success
        assert result.data["spec"]["id"] == "test_spec"
        assert result.data["spec"]["version"] == "1.0.0"

    def test_parse_lists(self):
        parser = ToonParser()
        result = parser.parse(SAMPLE_TOON)
        assert result.data["examples"] == ["item1", "item2", "item3"]

    def test_parse_nested(self):
        parser = ToonParser()
        result = parser.parse(SAMPLE_TOON)
        assert result.data["nested"]["key1"] == "val1"
        assert result.data["nested"]["key2"]["subkey"] == "subval"

    def test_parse_numbers(self):
        parser = ToonParser()
        result = parser.parse(SAMPLE_TOON)
        assert result.data["difficulty"]["D0"] == 0
        assert result.data["difficulty"]["D1"] == 1

    def test_parse_int_literals(self):
        parser = ToonParser()
        result = parser.parse("count: 42\nscore: 3.14\nactive: true\n")
        assert result.data["count"] == 42
        assert result.data["score"] == 3.14
        assert result.data["active"] is True

    def test_parse_empty(self):
        parser = ToonParser()
        result = parser.parse("")
        assert result.success
        assert result.data == {}

    def test_parse_comments_only(self):
        parser = ToonParser()
        result = parser.parse("# just a comment\n# another\n")
        assert result.success


class TestToonCompiler:
    def test_compile_spec_file(self):
        compiler = ToonCompiler()
        spec_path = Path("compiler/00_core/07_global_constants.toon")
        assert spec_path.exists()
        data = compiler.compile_spec(spec_path)
        assert "priority" in data
        assert data["priority"]["P0"] == "Critical"

    def test_compile_constants_spec(self):
        compiler = ToonCompiler()
        spec_path = Path("compiler/00_core/07_global_constants.toon")
        data = compiler.compile_spec(spec_path)
        assert "priority" in data
        assert "difficulty" in data
        assert data["priority"]["P0"] == "Critical"

    def test_compile_pipeline_spec(self):
        compiler = ToonCompiler()
        spec_path = Path("compiler/00_core/03_pipeline.toon")
        data = compiler.compile_spec(spec_path)
        assert "stages" in data
        assert "Stage_00" in data["stages"]
        assert data["stages"]["Stage_00"]["name"] == "Initialization"

    def test_compile_all_specs(self):
        compiler = ToonCompiler()
        spec_dir = Path("compiler")
        count = 0
        errors = []
        for toon_file in spec_dir.rglob("*.toon"):
            try:
                data = compiler.compile_spec(toon_file)
                assert data
                count += 1
            except Exception as e:
                errors.append(f"{toon_file.name}: {e}")
        assert not errors, f"Parse errors: {errors}"
        assert count == 151

    def test_parse_real_priority(self):
        parser = ToonParser()
        spec_path = Path("compiler/00_core/07_global_constants.toon")
        result = parser.parse_file(spec_path)
        assert result.success
        assert result.data["priority"]["P0"] == "Critical"

    def test_parse_real_pipeline_stages(self):
        parser = ToonParser()
        spec_path = Path("compiler/00_core/03_pipeline.toon")
        result = parser.parse_file(spec_path)
        assert result.success
        assert "Stage_00" in result.data.get("stages", {})
