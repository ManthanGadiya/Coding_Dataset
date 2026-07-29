"""Tests for the benchmark module."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import random
import pytest
from compiler.generation.engine import EpisodeType
from compiler.benchmark.engine import BenchmarkSuite, BenchmarkReport


class TestBenchmarkReport:
    def test_empty_report(self):
        report = BenchmarkReport()
        d = report.to_dict()
        assert d["total_ekrs"] == 0
        assert d["unique_operations"] == 0

    def test_summary_output(self):
        report = BenchmarkReport(
            quality_distribution={2: 100, 3: 700, 4: 200},
            domain_coverage={"Databases": 500, "Networking": 500},
            episode_type_coverage={"bug_fix": 400, "code_review": 600},
            avg_reasoning_steps=5.2,
            avg_decisions=0.4,
            avg_evidence=2.1,
            avg_atom_refs=1.8,
            throughput_ekrs_per_sec=2894,
            atom_ref_rate=0.35,
            unique_operations=12,
            total_ekrs=1000,
        )
        s = report.summary()
        assert "Total EKRs:" in s
        assert "2894" in s
        assert "Q2" in s

    def test_summary_with_errors(self):
        report = BenchmarkReport(errors=["EKR 0: timeout", "EKR 1: empty"])
        s = report.summary()
        assert "Errors" in s


class TestBenchmarkSuite:
    def test_run_small(self):
        suite = BenchmarkSuite()
        report = suite.run(num_ekrs=5, seed=42)
        assert report.total_ekrs == 5
        assert sum(report.quality_distribution.values()) == 5
        assert len(report.errors) == 0
        assert report.throughput_ekrs_per_sec > 0

    def test_run_with_types_filter(self):
        suite = BenchmarkSuite()
        types = [EpisodeType.BUG_FIX, EpisodeType.CODE_REVIEW]
        report = suite.run(num_ekrs=10, types=types, seed=1)
        for et in report.episode_type_coverage:
            assert et in {"bug_fix", "code_review"}
        assert report.total_ekrs == 10

    def test_run_with_domains_filter(self):
        suite = BenchmarkSuite()
        report = suite.run(num_ekrs=10, domains=["Databases"], seed=1)
        for d in report.domain_coverage:
            assert d == "Databases"

    def test_run_consistency(self):
        suite = BenchmarkSuite()
        r1 = suite.run(num_ekrs=10, seed=0)
        r2 = suite.run(num_ekrs=10, seed=0)
        assert abs(r1.avg_reasoning_steps - r2.avg_reasoning_steps) < 1.5
        assert abs(r1.avg_atom_refs - r2.avg_atom_refs) < 1.0

    def test_run_quality_distribution(self):
        suite = BenchmarkSuite()
        report = suite.run(num_ekrs=50, seed=123)
        q_vals = report.quality_distribution
        total = sum(q_vals.values())
        assert total == 50
        for q in q_vals:
            assert q >= 2 and q <= 4

    def test_report_to_dict_roundtrip(self):
        suite = BenchmarkSuite()
        report = suite.run(num_ekrs=5, seed=99)
        d = report.to_dict()
        assert isinstance(d["quality_distribution"], dict)
        assert isinstance(d["throughput_ekrs_per_sec"], float)
        assert isinstance(d["total_ekrs"], int)
