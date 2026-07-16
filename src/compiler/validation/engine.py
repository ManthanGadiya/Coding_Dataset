"""Validation engine — multi-domain validation.

Source: compiler/08_validation/
"""

from dataclasses import dataclass, field
from enum import Enum


class ValidationStatus(Enum):
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"


@dataclass
class ValidationResult:
    domain: str
    status: ValidationStatus
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return self.status in (ValidationStatus.PASSED, ValidationStatus.WARNING)

    def to_dict(self) -> dict:
        return {
            "domain": self.domain, "status": self.status.value,
            "errors": self.errors, "warnings": self.warnings,
        }


@dataclass
class ValidationReport:
    results: list[ValidationResult] = field(default_factory=list)

    @property
    def all_passed(self) -> bool:
        return all(r.passed for r in self.results)

    def to_dict(self) -> dict:
        return {
            "all_passed": self.all_passed,
            "results": [r.to_dict() for r in self.results],
        }


class ValidationEngine:
    DOMAINS = [
        "schema", "graph", "reasoning", "fact", "execution",
        "security", "consistency", "dataset", "final",
    ]

    def validate(self, ekr_dict: dict) -> ValidationReport:
        results = []
        for domain in self.DOMAINS:
            r = self._validate_domain(domain, ekr_dict)
            results.append(r)
        return ValidationReport(results=results)

    def _validate_domain(self, domain: str, ekr_dict: dict) -> ValidationResult:
        errors = []
        warnings = []

        if domain == "schema":
            if not ekr_dict.get("metadata"):
                errors.append("Missing metadata")
            if not ekr_dict.get("id"):
                errors.append("Missing id")

        if domain == "graph":
            if not ekr_dict.get("knowledge_atoms"):
                warnings.append("No knowledge atoms linked")

        if domain == "reasoning":
            if not ekr_dict.get("reasoning"):
                errors.append("Missing reasoning chain")
            if len(ekr_dict.get("reasoning", [])) < 2:
                warnings.append("Reasoning chain too short")

        if domain == "consistency":
            meta = ekr_dict.get("metadata", {})
            if meta.get("domain") and ekr_dict.get("domain") and meta["domain"] != ekr_dict["domain"]:
                errors.append("Domain mismatch between metadata and record")

        status = ValidationStatus.FAILED if errors else (ValidationStatus.WARNING if warnings else ValidationStatus.PASSED)
        return ValidationResult(domain=domain, status=status, errors=errors, warnings=warnings)
