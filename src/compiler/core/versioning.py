"""Semantic versioning.

Source: compiler/00_core/09_versioning.toon
"""

import re
from dataclasses import dataclass

_VERSION_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


@dataclass(frozen=True)
class Version:
    major: int
    minor: int
    patch: int

    def __str__(self):
        return f"{self.major}.{self.minor}.{self.patch}"

    @classmethod
    def parse(cls, s: str) -> "Version":
        m = _VERSION_RE.match(s.strip())
        if not m:
            raise ValueError(f"Invalid version: {s!r}")
        return cls(int(m.group(1)), int(m.group(2)), int(m.group(3)))

    @classmethod
    def default(cls) -> "Version":
        return cls(1, 0, 0)

    def bump_major(self) -> "Version":
        return Version(self.major + 1, 0, 0)

    def bump_minor(self) -> "Version":
        return Version(self.major, self.minor + 1, 0)

    def bump_patch(self) -> "Version":
        return Version(self.major, self.minor, self.patch + 1)


@dataclass
class ComponentVersion:
    component: str
    version: Version
    compiler_version: Version
    ontology_version: Version
    schema_version: Version
    release_version: str | None = None

    def to_dict(self) -> dict:
        return {
            "component": self.component,
            "version": str(self.version),
            "compiler_version": str(self.compiler_version),
            "ontology_version": str(self.ontology_version),
            "schema_version": str(self.schema_version),
        }
