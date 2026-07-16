"""TOON Parser — parses .toon spec files into Python objects.

Syntax: indentation-based, key-value, list notation '- '
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator


@dataclass
class ParseResult:
    data: dict
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return len(self.errors) == 0


class ToonParser:
    """Iterative line-based TOON parser."""

    def parse(self, text: str) -> ParseResult:
        errors: list[str] = []
        warnings: list[str] = []
        raw_lines = text.split("\n")
        lines = []
        for i, raw in enumerate(raw_lines):
            stripped = raw.strip()
            if not stripped or stripped.startswith("#"):
                continue
            indent = len(raw) - len(raw.lstrip(" "))
            lines.append((indent, stripped, i + 1))

        data = self._build(lines, 0, len(lines), -1, errors, warnings)
        return ParseResult(data=data, errors=errors, warnings=warnings)

    def _build(self, lines: list[tuple[int, str, int]],
               start: int, end: int, parent_indent: int,
               errors: list, warnings: list) -> dict:
        result: dict = {}
        i = start
        pending_key: str | None = None

        while i < end:
            indent, content, line_no = lines[i]

            if indent <= parent_indent:
                break

            if content.startswith("- "):
                if pending_key:
                    lst = self._collect_list(lines, i, end, indent, errors, warnings)
                    result[pending_key] = lst
                    i += len(lst) + 1  # +1 because we also consumed the list items
                    pending_key = None
                    continue
                else:
                    warnings.append(f"Line {line_no}: list item outside list context: {content!r}")
                    i += 1
                    continue

            if ": " in content:
                key, _, val = content.partition(": ")
                key = key.strip()
                val = val.strip()
            elif content.endswith(":"):
                key = content[:-1].strip()
                val = ""
            else:
                warnings.append(f"Line {line_no}: unparseable: {content!r}")
                i += 1
                continue
            pending_key = key

            if val:
                result[key] = self._parse_value(val)
                i += 1
            else:
                # Peek ahead to determine child type
                if i + 1 < end:
                    n_indent, n_content, _ = lines[i + 1]
                    if n_indent > indent and n_content.startswith("- "):
                        lst = self._collect_list(lines, i + 1, end, n_indent, errors, warnings)
                        result[key] = lst
                        i += len(lst) + 1
                        pending_key = None
                        continue
                    elif n_indent > indent:
                        sub = self._build(lines, i + 1, end, indent, errors, warnings)
                        result[key] = sub
                        # Advance past consumed lines
                        j = i + 1
                        while j < end:
                            ci, _, _ = lines[j]
                            if ci <= indent:
                                break
                            j += 1
                        i = j
                        continue

                result[key] = {}
                i += 1

        return result

    def _collect_list(self, lines: list[tuple[int, str, int]],
                      start: int, end: int, base_indent: int,
                      errors: list, warnings: list) -> list:
        result: list = []
        i = start
        while i < end:
            indent, content, line_no = lines[i]
            if indent < base_indent:
                break
            if content.startswith("- "):
                item = self._parse_value(content[2:].strip())
                result.append(item)
            else:
                warnings.append(f"Line {line_no}: expected list item, got: {content!r}")
                break
            i += 1
        return result

    def _parse_value(self, val: str) -> Any:
        if val.startswith('"') and val.endswith('"'):
            inner = val[1:-1]
            if inner.startswith('"') and inner.endswith('"'):
                inner = inner[1:-1]
            return inner
        if val.lower() in ("true", "yes"):
            return True
        if val.lower() in ("false", "no"):
            return False
        if val.lower() in ("null", "none", "~"):
            return None
        try:
            return int(val)
        except ValueError:
            pass
        try:
            return float(val)
        except ValueError:
            pass
        return val

    def parse_file(self, path: Path) -> ParseResult:
        return self.parse(path.read_text(encoding="utf-8"))


class ToonCompiler:
    def __init__(self):
        self.parser = ToonParser()

    def compile_spec(self, path: Path) -> dict:
        result = self.parser.parse_file(path)
        if not result.success:
            raise ValueError(f"Parse error in {path}: {result.errors}")
        return result.data
